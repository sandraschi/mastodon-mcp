"""Thin Mastodon REST client — always respects dry_run."""

from __future__ import annotations

import logging
import mimetypes
from pathlib import Path
from typing import Any

import httpx

from mastodon_mcp.config import get_settings

log = logging.getLogger(__name__)


def _headers(json_body: bool = True) -> dict[str, str]:
    cfg = get_settings()
    h = {"Authorization": f"Bearer {cfg.access_token}"}
    if json_body:
        h["Content-Type"] = "application/json"
    return h


def _configured() -> dict[str, Any] | None:
    cfg = get_settings()
    if not cfg.instance or not cfg.access_token:
        return {
            "success": False,
            "error": "MASTODON_INSTANCE and MASTODON_ACCESS_TOKEN required",
            "dry_run": False,
        }
    return None


async def create_status(
    status_text: str,
    *,
    visibility: str = "public",
    spoiler_text: str | None = None,
    in_reply_to_id: str | None = None,
    media_ids: list[str] | None = None,
    dry_run: bool | None = None,
) -> dict[str, Any]:
    cfg = get_settings()
    use_dry = cfg.dry_run if dry_run is None else dry_run
    # Dry-run must short-circuit before credential checks (local/CI without tokens).
    if use_dry:
        log.info("DRY RUN status: %s", status_text[:120])
        return {
            "success": True,
            "dry_run": True,
            "message": "dry_run — not posted",
            "status_text": status_text,
            "visibility": visibility,
            "in_reply_to_id": in_reply_to_id,
            "media_ids": media_ids or [],
            "id": "dry-run",
        }
    err = _configured()
    if err:
        return err

    url = f"{cfg.instance}/api/v1/statuses"
    body: dict[str, Any] = {"status": status_text, "visibility": visibility}
    if spoiler_text:
        body["spoiler_text"] = spoiler_text
    if in_reply_to_id:
        body["in_reply_to_id"] = in_reply_to_id
    if media_ids:
        body["media_ids"] = media_ids
    try:
        async with httpx.AsyncClient(timeout=30.0) as http:
            resp = await http.post(url, headers=_headers(), json=body)
            if resp.status_code >= 400:
                return {
                    "success": False,
                    "error": f"Mastodon HTTP {resp.status_code}",
                    "detail": resp.text[:300],
                }
            data = resp.json()
            return {"success": True, "dry_run": False, "id": data.get("id"), "data": data}
    except httpx.HTTPError as exc:
        log.exception("create_status failed")
        return {"success": False, "error": str(exc)}


async def reply_status(
    in_reply_to_id: str,
    status_text: str,
    *,
    visibility: str = "public",
    dry_run: bool | None = None,
) -> dict[str, Any]:
    if not in_reply_to_id:
        return {"success": False, "error": "in_reply_to_id (status_id) required"}
    return await create_status(
        status_text,
        visibility=visibility,
        in_reply_to_id=in_reply_to_id,
        dry_run=dry_run,
    )


async def boost_status(
    status_id: str,
    *,
    dry_run: bool | None = None,
) -> dict[str, Any]:
    if not status_id:
        return {"success": False, "error": "status_id required"}
    cfg = get_settings()
    use_dry = cfg.dry_run if dry_run is None else dry_run
    if use_dry:
        return {
            "success": True,
            "dry_run": True,
            "message": "dry_run — boost not sent",
            "status_id": status_id,
            "id": "dry-run-boost",
        }
    err = _configured()
    if err:
        return err
    url = f"{cfg.instance}/api/v1/statuses/{status_id}/reblog"
    try:
        async with httpx.AsyncClient(timeout=30.0) as http:
            resp = await http.post(url, headers=_headers())
            if resp.status_code >= 400:
                return {
                    "success": False,
                    "error": f"Mastodon HTTP {resp.status_code}",
                    "detail": resp.text[:300],
                }
            data = resp.json()
            return {"success": True, "dry_run": False, "id": data.get("id"), "data": data}
    except httpx.HTTPError as exc:
        return {"success": False, "error": str(exc)}


async def upload_media(
    path: str,
    *,
    description: str = "",
    dry_run: bool | None = None,
) -> dict[str, Any]:
    if not path:
        return {"success": False, "error": "media path required"}
    file_path = Path(path)
    if not file_path.is_file():
        return {"success": False, "error": f"file not found: {path}"}
    cfg = get_settings()
    use_dry = cfg.dry_run if dry_run is None else dry_run
    if use_dry:
        return {
            "success": True,
            "dry_run": True,
            "message": "dry_run — media not uploaded",
            "path": str(file_path),
            "id": "dry-run-media",
            "description": description,
        }
    err = _configured()
    if err:
        return err
    mime, _ = mimetypes.guess_type(str(file_path))
    mime = mime or "application/octet-stream"
    url = f"{cfg.instance}/api/v2/media"
    try:
        async with httpx.AsyncClient(timeout=120.0) as http:
            with file_path.open("rb") as fh:
                files = {"file": (file_path.name, fh, mime)}
                data = {}
                if description:
                    data["description"] = description
                resp = await http.post(
                    url,
                    headers=_headers(json_body=False),
                    files=files,
                    data=data or None,
                )
            if resp.status_code >= 400:
                return {
                    "success": False,
                    "error": f"Mastodon HTTP {resp.status_code}",
                    "detail": resp.text[:300],
                }
            body = resp.json()
            return {
                "success": True,
                "dry_run": False,
                "id": body.get("id"),
                "url": body.get("url") or body.get("preview_url"),
                "data": body,
            }
    except OSError as exc:
        return {"success": False, "error": str(exc)}
    except httpx.HTTPError as exc:
        return {"success": False, "error": str(exc)}


async def get_notifications(limit: int = 20) -> dict[str, Any]:
    """Fetch notification inbox from the instance (or empty dry stub)."""
    cfg = get_settings()
    if cfg.dry_run and (not cfg.instance or not cfg.access_token):
        return {
            "success": True,
            "dry_run": True,
            "notifications": [],
            "message": "dry_run — notifications inbox empty without credentials",
        }
    if not cfg.instance or not cfg.access_token:
        return {"success": False, "error": "not configured"}
    url = f"{cfg.instance}/api/v1/notifications?limit={limit}"
    try:
        async with httpx.AsyncClient(timeout=30.0) as http:
            resp = await http.get(url, headers=_headers())
            if resp.status_code >= 400:
                return {"success": False, "error": f"HTTP {resp.status_code}"}
            return {"success": True, "notifications": resp.json()}
    except httpx.HTTPError as exc:
        return {"success": False, "error": str(exc)}


async def get_timeline(timeline: str = "home", limit: int = 20) -> dict[str, Any]:
    cfg = get_settings()
    if not cfg.instance or not cfg.access_token:
        return {"success": False, "error": "not configured"}
    path = {
        "home": "/api/v1/timelines/home",
        "local": "/api/v1/timelines/public?local=true",
        "public": "/api/v1/timelines/public",
    }.get(timeline, "/api/v1/timelines/home")
    url = f"{cfg.instance}{path}"
    if "?" not in path:
        url = f"{url}?limit={limit}"
    else:
        url = f"{url}&limit={limit}"
    try:
        async with httpx.AsyncClient(timeout=30.0) as http:
            resp = await http.get(url, headers=_headers())
            if resp.status_code >= 400:
                return {"success": False, "error": f"HTTP {resp.status_code}"}
            return {"success": True, "statuses": resp.json()}
    except httpx.HTTPError as exc:
        return {"success": False, "error": str(exc)}


async def push_subscription_get() -> dict[str, Any]:
    """GET /api/v1/push/subscription — Web Push subscription if configured on instance."""
    cfg = get_settings()
    if cfg.dry_run and (not cfg.instance or not cfg.access_token):
        return {
            "success": True,
            "dry_run": True,
            "subscription": None,
            "message": "dry_run — no push subscription without credentials",
        }
    err = _configured()
    if err:
        return err
    url = f"{cfg.instance}/api/v1/push/subscription"
    try:
        async with httpx.AsyncClient(timeout=30.0) as http:
            resp = await http.get(url, headers=_headers())
            if resp.status_code == 404:
                return {"success": True, "subscription": None}
            if resp.status_code >= 400:
                return {
                    "success": False,
                    "error": f"HTTP {resp.status_code}",
                    "detail": resp.text[:200],
                }
            return {"success": True, "subscription": resp.json()}
    except httpx.HTTPError as exc:
        return {"success": False, "error": str(exc)}

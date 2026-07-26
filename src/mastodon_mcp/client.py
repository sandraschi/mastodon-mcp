"""Thin Mastodon REST client — always respects dry_run."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from mastodon_mcp.config import get_settings

log = logging.getLogger(__name__)


def _headers() -> dict[str, str]:
    cfg = get_settings()
    return {
        "Authorization": f"Bearer {cfg.access_token}",
        "Content-Type": "application/json",
    }


async def create_status(
    status_text: str,
    *,
    visibility: str = "public",
    spoiler_text: str | None = None,
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
            "id": "dry-run",
        }
    if not cfg.instance or not cfg.access_token:
        return {
            "success": False,
            "error": "MASTODON_INSTANCE and MASTODON_ACCESS_TOKEN required",
            "dry_run": False,
        }

    url = f"{cfg.instance}/api/v1/statuses"
    body: dict[str, Any] = {"status": status_text, "visibility": visibility}
    if spoiler_text:
        body["spoiler_text"] = spoiler_text
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=_headers(), json=body)
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
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=_headers())
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
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=_headers())
            if resp.status_code >= 400:
                return {"success": False, "error": f"HTTP {resp.status_code}"}
            return {"success": True, "statuses": resp.json()}
    except httpx.HTTPError as exc:
        return {"success": False, "error": str(exc)}

"""mastodon_social portmanteau tool."""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import Field

from mastodon_mcp import client, outbox
from mastodon_mcp.config import get_settings


async def mastodon_social(
    operation: Annotated[
        str,
        Field(
            description=(
                "post|reply|boost|upload_media|timeline|notifications|"
                "outbox_list|outbox_enqueue|outbox_approve|outbox_publish|outbox_reject|accounts_list"
            )
        ),
    ],
    status_text: str = "",
    outbox_id: int = 0,
    timeline: str = "home",
    visibility: str = "public",
    payload: dict[str, Any] | None = None,
    reason: str = "",
    dry_run: bool | None = None,
) -> dict[str, Any]:
    """Unified Mastodon / outbox operations. Fleet drafts must go through outbox approve → publish."""
    op = operation.strip().lower()
    cfg = get_settings()

    if op == "outbox_list":
        return {"success": True, "items": outbox.list_items()}

    if op == "outbox_enqueue":
        if not payload:
            payload = {
                "status_text": status_text,
                "visibility": visibility,
                "source": "mastodon_social",
            }
        return outbox.enqueue(payload)

    if op == "outbox_approve":
        if not outbox_id:
            return {"success": False, "error": "outbox_id required"}
        return outbox.approve(outbox_id)

    if op == "outbox_reject":
        if not outbox_id:
            return {"success": False, "error": "outbox_id required"}
        return outbox.reject(outbox_id, reason)

    if op == "outbox_publish":
        if not outbox_id:
            return {"success": False, "error": "outbox_id required"}
        row = outbox.get_item(outbox_id)
        if not row:
            return {"success": False, "error": "not found"}
        if row["status"] != "approved":
            return {"success": False, "error": "must be approved before publish"}
        result = await client.create_status(
            row["status_text"],
            visibility=row.get("visibility") or "public",
            dry_run=dry_run,
        )
        if result.get("success") and not result.get("dry_run"):
            outbox.mark_published(outbox_id, str(result.get("id", "")))
        elif result.get("success") and result.get("dry_run"):
            result["message"] = (
                "dry_run publish OK — set MASTODON_DRY_RUN=0 to post for real after approve"
            )
        return result

    if op == "post":
        if cfg.require_outbox_approval and not outbox_id:
            return {
                "success": False,
                "error": (
                    "direct post blocked — enqueue to outbox, approve, then outbox_publish "
                    "(or set MASTODON_REQUIRE_OUTBOX_APPROVAL=0 for interactive compose)"
                ),
            }
        if outbox_id:
            return await mastodon_social(
                operation="outbox_publish", outbox_id=outbox_id, dry_run=dry_run
            )
        return await client.create_status(status_text, visibility=visibility, dry_run=dry_run)

    if op == "timeline":
        return await client.get_timeline(timeline)

    if op == "notifications":
        return await client.get_notifications()

    if op in ("reply", "boost", "upload_media"):
        return {
            "success": False,
            "error": f"{op} stubbed in v0.1 — use outbox + post path first",
            "planned": True,
        }

    if op == "accounts_list":
        return {
            "success": True,
            "accounts": [
                {
                    "instance": cfg.instance or "(unset)",
                    "configured": bool(cfg.access_token),
                    "dry_run": cfg.dry_run,
                }
            ],
        }

    return {
        "success": False,
        "error": f"unknown operation {operation!r}",
        "operations": [
            "post",
            "reply",
            "boost",
            "upload_media",
            "timeline",
            "notifications",
            "outbox_list",
            "outbox_enqueue",
            "outbox_approve",
            "outbox_publish",
            "outbox_reject",
            "accounts_list",
        ],
    }

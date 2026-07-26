"""mastodon_social portmanteau tool — full ops, no planned stubs."""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import Field

from mastodon_mcp import client, outbox, webhooks
from mastodon_mcp.config import get_settings

OPS = [
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
    "webhook_list",
    "webhook_receive",
    "push_subscription_get",
]


async def mastodon_social(
    operation: Annotated[
        str,
        Field(description="|".join(OPS)),
    ],
    status_text: str = "",
    outbox_id: int = 0,
    timeline: str = "home",
    visibility: str = "public",
    payload: dict[str, Any] | None = None,
    reason: str = "",
    dry_run: bool | None = None,
    status_id: str = "",
    in_reply_to_id: str = "",
    media_path: str = "",
    media_description: str = "",
    media_ids: list[str] | None = None,
    event_type: str = "generic",
    source: str = "agent",
) -> dict[str, Any]:
    """Unified Mastodon / outbox / webhook operations. Fleet drafts: outbox approve → publish."""
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
        return await client.create_status(
            status_text,
            visibility=visibility,
            media_ids=media_ids,
            dry_run=dry_run,
        )

    if op == "reply":
        sid = in_reply_to_id or status_id
        return await client.reply_status(sid, status_text, visibility=visibility, dry_run=dry_run)

    if op == "boost":
        sid = status_id or in_reply_to_id
        return await client.boost_status(sid, dry_run=dry_run)

    if op == "upload_media":
        return await client.upload_media(media_path, description=media_description, dry_run=dry_run)

    if op == "timeline":
        return await client.get_timeline(timeline)

    if op == "notifications":
        return await client.get_notifications()

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

    if op == "webhook_list":
        return webhooks.list_events()

    if op == "webhook_receive":
        if not payload:
            return {"success": False, "error": "payload required"}
        return webhooks.enqueue_event(source or "agent", event_type, payload)

    if op == "push_subscription_get":
        return await client.push_subscription_get()

    return {
        "success": False,
        "error": f"unknown operation {operation!r}",
        "operations": OPS,
    }

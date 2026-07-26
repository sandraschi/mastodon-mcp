"""Portmanteau mastodon_social operation tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from mastodon_mcp.portmanteau import mastodon_social


@pytest.mark.asyncio
async def test_outbox_portmanteau_lifecycle(isolated_data):
    enq = await mastodon_social(
        operation="outbox_enqueue",
        payload={
            "repo_id": "kicad-mcp",
            "status_text": "KiCad headless export via MCP.",
            "source": "fleet-public-relations-mcp",
        },
    )
    assert enq["success"] is True
    oid = enq["id"]

    listed = await mastodon_social(operation="outbox_list")
    assert listed["success"] is True
    assert any(i["id"] == oid for i in listed["items"])

    assert (await mastodon_social(operation="outbox_publish", outbox_id=oid))["success"] is False

    appr = await mastodon_social(operation="outbox_approve", outbox_id=oid)
    assert appr["success"] is True

    pub = await mastodon_social(operation="outbox_publish", outbox_id=oid, dry_run=True)
    assert pub["success"] is True
    assert pub["dry_run"] is True


@pytest.mark.asyncio
async def test_direct_post_blocked_without_outbox(isolated_data):
    r = await mastodon_social(operation="post", status_text="hello fediverse")
    assert r["success"] is False
    assert "outbox" in r["error"].lower()


@pytest.mark.asyncio
async def test_notifications_and_accounts(isolated_data):
    n = await mastodon_social(operation="notifications")
    assert n["success"] is True
    assert n["notifications"] == []

    a = await mastodon_social(operation="accounts_list")
    assert a["success"] is True
    assert len(a["accounts"]) == 1


@pytest.mark.asyncio
async def test_reply_boost_media_dry_run(isolated_data, tmp_path: Path):
    reply = await mastodon_social(
        operation="reply",
        in_reply_to_id="123",
        status_text="thanks",
        dry_run=True,
    )
    assert reply["success"] is True
    assert reply["dry_run"] is True
    assert reply.get("in_reply_to_id") == "123"

    boost = await mastodon_social(operation="boost", status_id="456", dry_run=True)
    assert boost["success"] is True
    assert boost["dry_run"] is True

    media_file = tmp_path / "pic.png"
    media_file.write_bytes(b"\x89PNG\r\n\x1a\n")
    up = await mastodon_social(
        operation="upload_media",
        media_path=str(media_file),
        media_description="test",
        dry_run=True,
    )
    assert up["success"] is True
    assert up["id"] == "dry-run-media"


@pytest.mark.asyncio
async def test_webhook_ops(isolated_data):
    recv = await mastodon_social(
        operation="webhook_receive",
        source="fleet-pr",
        event_type="draft.queued",
        payload={"repo_id": "mixx-dj-mcp"},
    )
    assert recv["success"] is True
    listed = await mastodon_social(operation="webhook_list")
    assert listed["count"] >= 1
    push = await mastodon_social(operation="push_subscription_get")
    assert push["success"] is True


@pytest.mark.asyncio
async def test_unknown_op(isolated_data):
    bad = await mastodon_social(operation="dance")
    assert bad["success"] is False
    assert "operations" in bad

"""Portmanteau mastodon_social operation tests."""

from __future__ import annotations

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
async def test_unknown_and_stub_ops(isolated_data):
    stub = await mastodon_social(operation="boost")
    assert stub.get("planned") is True
    bad = await mastodon_social(operation="dance")
    assert bad["success"] is False
    assert "operations" in bad

"""Mastodon client dry-run / credential gates."""

from __future__ import annotations

import pytest

from mastodon_mcp import client


@pytest.mark.asyncio
async def test_create_status_dry_run_without_token(isolated_data):
    r = await client.create_status("useful pointer post", dry_run=True)
    assert r["success"] is True
    assert r["dry_run"] is True
    assert r["id"] == "dry-run"


@pytest.mark.asyncio
async def test_create_status_live_requires_creds(isolated_data, monkeypatch):
    monkeypatch.setenv("MASTODON_DRY_RUN", "0")
    from mastodon_mcp import config

    config.get_settings.cache_clear()
    r = await client.create_status("should fail", dry_run=False)
    assert r["success"] is False
    assert "required" in r["error"].lower()
    config.get_settings.cache_clear()


@pytest.mark.asyncio
async def test_notifications_dry_empty(isolated_data):
    r = await client.get_notifications()
    assert r["success"] is True
    assert r["notifications"] == []

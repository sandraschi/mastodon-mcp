"""Shared fixtures — isolated SQLite data dir per test session/function."""

from __future__ import annotations

import pytest


@pytest.fixture()
def isolated_data(tmp_path, monkeypatch):
    monkeypatch.setenv("MASTODON_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("MASTODON_DRY_RUN", "1")
    monkeypatch.setenv("MASTODON_REQUIRE_OUTBOX_APPROVAL", "1")
    monkeypatch.delenv("MASTODON_INSTANCE", raising=False)
    monkeypatch.delenv("MASTODON_ACCESS_TOKEN", raising=False)

    from mastodon_mcp import config, outbox

    config.get_settings.cache_clear()
    outbox._DB = None
    yield tmp_path
    outbox._DB = None
    config.get_settings.cache_clear()


@pytest.fixture()
def client(isolated_data):
    from fastapi.testclient import TestClient

    from mastodon_mcp.server import app

    with TestClient(app) as c:
        yield c

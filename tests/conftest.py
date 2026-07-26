"""Shared fixtures — declared doubles only (see docs/DEVELOPMENT.md § Declared doubles).

isolated_data: temp SQLite dir, MASTODON_DRY_RUN=1, no instance token.
Live Mastodon calls are not mocked with MagicMock; dry_run short-circuits in client.py.
"""

from __future__ import annotations

import pytest


@pytest.fixture()
def isolated_data(tmp_path, monkeypatch):
    """Declared double: isolated data dir + dry_run; tokens removed (no live API)."""
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
    """FastAPI TestClient over real app ASGI (not a fake API layer)."""
    from fastapi.testclient import TestClient

    from mastodon_mcp.server import app

    with TestClient(app) as c:
        yield c

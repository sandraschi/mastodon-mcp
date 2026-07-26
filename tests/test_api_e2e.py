"""API e2e — fleet-PR handoff shape into outbox (HTTP), approve, dry-run publish."""

from __future__ import annotations


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["dry_run"] is True
    assert body["server"] == "mastodon-mcp"


def test_fleet_pr_inbound_outbox_e2e(client):
    """Simulate fleet-public-relations-mcp POST /api/v1/outbox payload."""
    payload = {
        "schema_version": 1,
        "source": "fleet-public-relations-mcp",
        "repo_id": "mixx-dj-mcp",
        "campaign": "dogfood-mixxx",
        "status_text": (
            "AI-native DJ control — forked Mixxx for video decks. "
            "https://github.com/sandraschi/mixx-dj-mcp"
        ),
        "visibility": "public",
        "idempotency_key": "mixx-dj-mcp:mastodon:test",
        "media_paths": [],
        "cw_sensitive": False,
    }
    enq = client.post("/api/v1/outbox", json=payload)
    assert enq.status_code == 200
    data = enq.json()
    assert data["success"] is True
    oid = data["id"]

    listed = client.get("/api/v1/outbox")
    assert listed.status_code == 200
    assert listed.json()["count"] >= 1
    assert any(i["id"] == oid for i in listed.json()["items"])

    # publish before approve must fail
    early = client.post(f"/api/v1/outbox/{oid}/publish")
    assert early.status_code == 200
    assert early.json().get("success") is False

    appr = client.post(f"/api/v1/outbox/{oid}/approve")
    assert appr.status_code == 200
    assert appr.json()["status"] == "approved"

    pub = client.post(f"/api/v1/outbox/{oid}/publish")
    assert pub.status_code == 200
    body = pub.json()
    assert body["success"] is True
    assert body["dry_run"] is True
    assert "not posted" in body.get("message", "").lower() or body.get("id") == "dry-run"


def test_outbox_reject_api(client):
    enq = client.post(
        "/api/v1/outbox",
        json={"status_text": "game-changer 10x", "repo_id": "x", "source": "test"},
    )
    oid = enq.json()["id"]
    rej = client.post(f"/api/v1/outbox/{oid}/reject", params={"reason": "hype"})
    assert rej.status_code == 200
    assert rej.json()["status"] == "rejected"
    items = client.get("/api/v1/outbox", params={"status": "rejected"}).json()["items"]
    assert any(i["id"] == oid for i in items)


def test_notifications_inbox_dry(client):
    r = client.get("/api/v1/notifications")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body.get("dry_run") is True
    assert body["notifications"] == []


def test_timeline_unconfigured(client):
    r = client.get("/api/v1/timeline", params={"kind": "home"})
    assert r.status_code == 200
    # no credentials → not configured
    assert r.json().get("success") is False

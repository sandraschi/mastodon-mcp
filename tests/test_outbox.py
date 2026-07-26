"""Outbox store unit tests — fleet-PR inbound queue lifecycle."""

from mastodon_mcp.outbox import (
    approve,
    enqueue,
    get_item,
    list_items,
    mark_published,
    reject,
)


def test_version():
    from mastodon_mcp import __version__

    assert __version__ == "0.1.0"


def test_enqueue_pending(isolated_data):
    q = enqueue(
        {
            "repo_id": "mixx-dj-mcp",
            "status_text": "Headless Mixxx control via MCP.",
            "campaign": "dogfood",
            "source": "fleet-public-relations-mcp",
            "idempotency_key": "mixx:1",
        }
    )
    assert q["success"] is True
    assert q["outbox_id"] == q["id"]
    row = get_item(q["id"])
    assert row is not None
    assert row["status"] == "pending"
    assert row["repo_id"] == "mixx-dj-mcp"
    assert "Mixxx" in row["status_text"]


def test_approve_reject_publish_states(isolated_data):
    oid = enqueue({"status_text": "pointer post", "repo_id": "blender-mcp"})["id"]
    assert approve(99999)["success"] is False
    assert approve(oid)["success"] is True
    assert get_item(oid)["status"] == "approved"
    # double-approve from approved should fail
    assert approve(oid)["success"] is False
    mark_published(oid, "status-123")
    assert get_item(oid)["status"] == "published"
    assert get_item(oid)["published_status_id"] == "status-123"


def test_reject_from_pending(isolated_data):
    oid = enqueue({"status_text": "nope", "repo_id": "x"})["id"]
    assert reject(oid, "tone fail")["success"] is True
    row = get_item(oid)
    assert row["status"] == "rejected"
    assert row["reject_reason"] == "tone fail"
    # can re-approve after reject
    assert approve(oid)["success"] is True


def test_list_filter_by_status(isolated_data):
    a = enqueue({"status_text": "a", "repo_id": "r1"})["id"]
    b = enqueue({"status_text": "b", "repo_id": "r2"})["id"]
    approve(a)
    pending = list_items("pending")
    approved = list_items("approved")
    assert all(i["status"] == "pending" for i in pending)
    assert any(i["id"] == b for i in pending)
    assert any(i["id"] == a for i in approved)
    assert len(list_items()) >= 2

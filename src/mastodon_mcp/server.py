"""mastodon-mcp FastMCP + FastAPI server — ports 10754 (HTTP/MCP)."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP
from fastmcp.server.providers.skills import SkillsDirectoryProvider
from pydantic import BaseModel, Field

from mastodon_mcp import outbox
from mastodon_mcp._version import __version__
from mastodon_mcp.config import get_settings
from mastodon_mcp.portmanteau import mastodon_social

log = logging.getLogger(__name__)
cfg = get_settings()

mcp = FastMCP(
    name=cfg.server_name,
    version=__version__,
    instructions=(
        "Mastodon / Fediverse bridge. Fleet-PR drafts land in outbox; "
        "human must approve before publish. Dry-run default."
    ),
)

_skills_root = Path(__file__).parent / "skills"
if _skills_root.is_dir():
    mcp.add_provider(SkillsDirectoryProvider(roots=[_skills_root]))


@mcp.prompt()
async def mastodon_outbox_prompt() -> str:
    """How to queue and publish fleet promotion drafts safely."""
    return (
        "Use mastodon_social_tool outbox_enqueue for fleet-PR payloads.\n"
        "Never publish without human outbox_approve.\n"
        "Respect MASTODON_DRY_RUN=1 unless explicitly told to go live.\n"
        "Tone: FLEET_PROMOTION.md — useful pointer, no hype, no 'written by AI'."
    )


@mcp.tool()
async def mastodon_social_tool(
    operation: str,
    status_text: str = "",
    outbox_id: int = 0,
    timeline: str = "home",
    visibility: str = "public",
    reason: str = "",
    dry_run: bool | None = None,
    payload: dict[str, Any] | None = None,
) -> dict:
    """Portmanteau: post/timeline/outbox_* — fleet drafts use outbox_enqueue → approve → publish."""
    return await mastodon_social(
        operation=operation,
        status_text=status_text,
        outbox_id=outbox_id,
        timeline=timeline,
        visibility=visibility,
        reason=reason,
        dry_run=dry_run,
        payload=payload,
    )


@mcp.tool()
async def mastodon_help() -> dict:
    """Help for mastodon-mcp."""
    return {
        "server": cfg.server_name,
        "version": __version__,
        "ports": {"backend": cfg.backend_port, "frontend": 10755},
        "dry_run": cfg.dry_run,
        "tools": ["mastodon_social_tool", "mastodon_help", "mastodon_shutdown"],
        "outbox_flow": "outbox_enqueue → outbox_approve → outbox_publish",
    }


@mcp.tool()
async def mastodon_shutdown() -> dict:
    """Signal graceful shutdown (process exit left to host)."""
    return {"success": True, "message": "Shutdown signal acknowledged"}


@mcp.tool(app=True)
async def show_outbox_card() -> dict:
    """Rich Prefab card summarizing pending outbox drafts."""
    try:
        from prefab_ui.app import PrefabApp
        from prefab_ui.components import Badge, Card, CardContent, Heading, Muted, Text
    except ImportError:
        items = outbox.list_items()
        pending = sum(1 for i in items if i.get("status") == "pending")
        return {
            "success": True,
            "prefab": False,
            "pending": pending,
            "total": len(items),
            "message": "prefab-ui not installed — raw summary",
        }

    items = outbox.list_items()
    pending = [i for i in items if i.get("status") == "pending"]
    app = PrefabApp(title="Mastodon Outbox")
    with app:
        Heading("Outbox", level=2)
        Text(f"{len(pending)} pending · {len(items)} total")
        Muted("Dry-run default — approve then publish")
        for row in pending[:8]:
            with Card(), CardContent():
                Badge(row.get("repo_id") or "manual", color="violet")
                Text((row.get("status_text") or "")[:160])
    return app.output()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    os.makedirs(cfg.data_dir, exist_ok=True)
    outbox._db()  # init schema
    log.info("mastodon-mcp starting port=%s dry_run=%s", cfg.backend_port, cfg.dry_run)
    yield


app = FastAPI(title="mastodon-mcp", version=__version__, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:10755", "http://localhost:10755"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
@app.get("/api/v1/health")
async def health():
    return {
        "status": "ok",
        "server": cfg.server_name,
        "version": __version__,
        "dry_run": cfg.dry_run,
        "instance_configured": bool(cfg.instance and cfg.access_token),
    }


class OutboxBody(BaseModel):
    status_text: str = ""
    repo_id: str = ""
    campaign: str = ""
    visibility: str = "public"
    schema_version: int = 1
    source: str = "fleet-public-relations-mcp"
    idempotency_key: str = ""
    spoiler_text: str | None = None
    media_paths: list[str] = Field(default_factory=list)
    cw_sensitive: bool = False
    created_at: str = ""

    model_config = {"extra": "allow"}


@app.post("/api/v1/outbox")
async def api_outbox_enqueue(body: OutboxBody):
    return outbox.enqueue(body.model_dump())


@app.get("/api/v1/outbox")
async def api_outbox_list(status: str = ""):
    items = outbox.list_items(status)
    return {"items": items, "count": len(items)}


@app.post("/api/v1/outbox/{item_id}/approve")
async def api_outbox_approve(item_id: int):
    return outbox.approve(item_id)


@app.post("/api/v1/outbox/{item_id}/reject")
async def api_outbox_reject(item_id: int, reason: str = ""):
    return outbox.reject(item_id, reason)


@app.post("/api/v1/outbox/{item_id}/publish")
async def api_outbox_publish(item_id: int):
    return await mastodon_social(operation="outbox_publish", outbox_id=item_id)


@app.get("/api/v1/notifications")
async def api_notifications():
    return await mastodon_social(operation="notifications")


@app.get("/api/v1/timeline")
async def api_timeline(kind: str = "home"):
    return await mastodon_social(operation="timeline", timeline=kind)


_mcp_asgi = mcp.http_app(path="/")
app.mount("/mcp", _mcp_asgi)


def main() -> None:
    logging.basicConfig(level=getattr(logging, cfg.log_level.upper(), logging.INFO))
    port = int(os.getenv("PORT", cfg.backend_port))
    uvicorn.run(
        "mastodon_mcp.server:app",
        host="127.0.0.1",
        port=port,
        log_level=cfg.log_level.lower(),
    )


if __name__ == "__main__":
    main()

"""mastodon-mcp FastMCP + FastAPI server — ports 10754 (HTTP/MCP)."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP
from fastmcp.server.providers.skills import SkillsDirectoryProvider
from pydantic import BaseModel, Field

from mastodon_mcp import outbox, webhooks
from mastodon_mcp._version import __version__
from mastodon_mcp.config import get_settings
from mastodon_mcp.portmanteau import OPS, mastodon_social

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
        "ports": {"backend": cfg.backend_port, "frontend": 10755},
    }


@app.get("/api/dashboard")
async def api_dashboard():
    items = outbox.list_items()
    by_status: dict[str, int] = {}
    for row in items:
        st = str(row.get("status") or "unknown")
        by_status[st] = by_status.get(st, 0) + 1
    return {
        "success": True,
        "pending": by_status.get("pending", 0),
        "approved": by_status.get("approved", 0),
        "published": by_status.get("published", 0),
        "rejected": by_status.get("rejected", 0),
        "total": len(items),
        "dry_run": cfg.dry_run,
        "instance_configured": bool(cfg.instance and cfg.access_token),
        "recent": items[:8],
    }


@app.get("/api/skills")
async def api_skills():
    root = Path(__file__).parent / "skills"
    skills = []
    if root.is_dir():
        for d in sorted(root.iterdir()):
            skill_md = d / "SKILL.md"
            if d.is_dir() and skill_md.is_file():
                skills.append(
                    {
                        "name": d.name,
                        "content": skill_md.read_text(encoding="utf-8"),
                    }
                )
    return {"skills": skills, "count": len(skills)}


@app.get("/api/tools")
async def api_tools():
    return {
        "tools": [
            {
                "name": "mastodon_social_tool",
                "kind": "portmanteau",
                "operations": OPS,
                "description": "Unified Mastodon / outbox / webhook operations",
            },
            {"name": "mastodon_help", "kind": "solo", "description": "Help and ports"},
            {"name": "mastodon_shutdown", "kind": "solo", "description": "Graceful shutdown ack"},
            {"name": "show_outbox_card", "kind": "prefab", "description": "Prefab outbox summary"},
        ]
    }


@app.get("/api/llm/providers")
async def api_llm_providers():
    import httpx

    providers = []
    for name, port, path in (
        ("Ollama", 11434, "/api/tags"),
        ("LM Studio", 1234, "/v1/models"),
        ("vLLM", 8000, "/v1/models"),
    ):
        detected = False
        models: list[str] = []
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                r = await client.get(f"http://127.0.0.1:{port}{path}")
                if r.status_code < 400:
                    detected = True
                    body = r.json()
                    if name == "Ollama":
                        models = [m.get("name", "") for m in body.get("models", [])]
                    else:
                        models = [m.get("id", "") for m in body.get("data", [])]
        except Exception:
            pass
        providers.append(
            {"name": name, "port": port, "detected": detected, "models": [m for m in models if m]}
        )
    return {"providers": providers}


class ChatBody(BaseModel):
    messages: list[dict[str, str]] = Field(default_factory=list)
    model: str = "qwen3:14b"
    provider_port: int = 11434


@app.post("/api/llm/chat")
async def api_llm_chat(body: ChatBody):
    """Proxy chat to local Ollama-compatible API (Compose assist / Chat page)."""
    import httpx

    url = f"http://127.0.0.1:{body.provider_port}/api/chat"
    # OpenAI-compatible path for LM Studio / vLLM
    openai_url = f"http://127.0.0.1:{body.provider_port}/v1/chat/completions"
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            if body.provider_port == 11434:
                r = await client.post(
                    url,
                    json={"model": body.model, "messages": body.messages, "stream": False},
                )
                if r.status_code >= 400:
                    return {"success": False, "error": r.text[:300]}
                data = r.json()
                return {
                    "success": True,
                    "content": data.get("message", {}).get("content", ""),
                }
            r = await client.post(
                openai_url,
                json={"model": body.model, "messages": body.messages},
            )
            if r.status_code >= 400:
                return {"success": False, "error": r.text[:300]}
            data = r.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {"success": True, "content": content}
    except httpx.HTTPError as exc:
        return {"success": False, "error": str(exc)}


class ComposeAssistBody(BaseModel):
    draft: str = ""
    repo_id: str = ""
    goal: str = "Tighten for FLEET_PROMOTION: concrete, no hype, name MCP/Cursor if relevant."


@app.post("/api/compose/assist")
async def api_compose_assist(body: ComposeAssistBody):
    """AI-assisted compose — returns suggested status text (local LLM)."""
    skill = ""
    skill_path = Path(__file__).parent / "skills" / "mastodon-outbox" / "SKILL.md"
    if skill_path.is_file():
        skill = skill_path.read_text(encoding="utf-8")[:4000]
    messages = [
        {
            "role": "system",
            "content": (
                f"{skill}\n\n---\nYou rewrite Mastodon drafts for sandraschi fleet promotion. "
                "Follow FLEET_PROMOTION: useful pointer, no game-changer/10x/revolution, "
                "no 'written by AI'. Return ONLY the improved status text."
            ),
        },
        {
            "role": "user",
            "content": (
                f"repo_id={body.repo_id or 'manual'}\ngoal={body.goal}\n\nDraft:\n{body.draft}"
            ),
        },
    ]
    result = await api_llm_chat(ChatBody(messages=messages, model="qwen3:14b", provider_port=11434))
    if not result.get("success"):
        return result
    return {"success": True, "suggested": (result.get("content") or "").strip()}


_LOG_RING: list[dict[str, Any]] = []


@app.get("/api/logs")
async def api_logs(limit: int = 100):
    return {"entries": _LOG_RING[-limit:], "count": len(_LOG_RING)}


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


class WebhookInboundBody(BaseModel):
    source: str = "external"
    event_type: str = "generic"
    payload: dict[str, Any] = Field(default_factory=dict)

    model_config = {"extra": "allow"}


@app.post("/api/v1/webhooks/inbound")
async def api_webhook_inbound(
    body: WebhookInboundBody,
    x_mastodon_webhook_secret: str | None = Header(default=None),
):
    """Fleet inbound webhook — set MASTODON_WEBHOOK_SECRET; header X-Mastodon-Webhook-Secret."""
    if not webhooks.verify_secret(x_mastodon_webhook_secret):
        return {"success": False, "error": "invalid or missing webhook secret"}
    payload = (
        body.payload
        if body.payload
        else body.model_dump(exclude={"source", "event_type", "payload"})
    )
    return webhooks.enqueue_event(body.source, body.event_type, payload)


@app.get("/api/v1/webhooks")
async def api_webhook_list(limit: int = 50):
    return webhooks.list_events(limit)


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

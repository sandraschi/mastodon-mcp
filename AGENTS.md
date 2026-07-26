# mastodon-mcp — Agent Guide

Fleet MCP server (Comms / Fediverse). Private until `.nopublish` lifted.

## Overview

FastMCP 3.4+ Mastodon bridge — human-approved outbox for `fleet-public-relations-mcp` drafts. Ports **10754** / **10755**. Pattern sibling of discord-mcp.

## Standards

- FastMCP 3.4.4+ portmanteau + skills + prompt + Prefab card
- Dual transport: HTTP `/mcp` + REST; dry-run default
- MCPB: `just mcpb-pack` · Tauri scaffold: `src-tauri/` (icons + PyInstaller before native)
- **No** GitHub Actions while private
- Tone: FLEET_PROMOTION.md

## Key files

| Path | Role |
|------|------|
| `src/mastodon_mcp/server.py` | FastAPI + FastMCP |
| `src/mastodon_mcp/portmanteau.py` | mastodon_social ops |
| `src/mastodon_mcp/outbox.py` | SQLite outbox |
| `webapp/` | Dark UI + Playwright e2e |
| `INSTALL.md` / `llms.txt` / `llms-full.txt` | Install + LLM manifests |
| `manifest.json` / `glama.json` | MCPB + discovery metadata |

## Quick ref

```powershell
.\start.ps1
uv run pytest tests/ -q
cd webapp; npm run test:e2e
just mcpb-pack
```

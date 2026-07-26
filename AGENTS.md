# mastodon-mcp — Agent Guide

Fleet MCP server (Comms / Fediverse lane). Scaffold only until v0.1 implementation.

## Overview

Mastodon (ActivityPub) bridge with human-approved outbox for `fleet-public-relations-mcp` drafts. Ports **10754** / **10755**. Modeled on `discord-mcp` (10756/10757).

## Standards

- FastMCP 3.x portmanteau: `mastodon_social(operation=…)`
- Responses: `{success, message, …}`
- Dual transport: stdio + HTTP `/mcp`
- Dry-run default; never auto-post
- Private repo until Sandra says otherwise (`.nopublish`)

## Key files

| Path | Role |
|------|------|
| `README.md` | User-facing overview |
| `PRD.md` | Requirements + payload contract |
| `.env.example` | Instance + token + dry_run |
| `src/` | Not yet — implement after approved plan |

## Do not

- Call Mastodon API from `fleet-public-relations-mcp` inline — handoff to this outbox only
- Use `glama-status-mcp` for grades — use `scraper-mcp` (10998)
- Post Bluesky here

## Quick ref (when implemented)

```powershell
.\start.ps1
just test
just lint
```

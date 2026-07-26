# mastodon-mcp — Product Requirements Document

**Status:** SCAFFOLD (v0.1.0 not implemented)
**Owner:** Sandra Schieder (sandraschi)
**Ports:** 10754 (backend), 10755 (dashboard)
**Category:** Comms / Fediverse
**Template:** discord-mcp (10756/10757)

## Overview

FastMCP bridge to Mastodon (ActivityPub). Primary fleet job: hold a **human-approved outbox** for promotion drafts produced by `fleet-public-relations-mcp`, then publish to one or more Mastodon instances.

## Problem

Discovery/promotion for 137+ public MCP repos is manual and inconsistent. Agents can draft release notes and social posts, but posting directly from a PR/automation server risks AI-spam and irreversible fediverse noise. A dedicated comms MCP with an outbox gate keeps drafting separate from publishing.

## Non-goals

- Bluesky / AT Protocol (later, separate repo)
- Auto-posting from CI or scraper-mcp
- Scraping Glama / grades (that is scraper-mcp)
- Hosting a Mastodon instance

## Success metrics

| Metric | Target |
|--------|--------|
| Accidental public posts | Zero while `MASTODON_DRY_RUN=1` |
| Fleet-PR → outbox handoff | HTTP enqueue returns id; webapp shows draft |
| Approve → publish | Single explicit action; audit row in SQLite |
| Tone | Rejected drafts if FLEET_PROMOTION banned phrases slip through (lint at fleet-PR; optional re-check here) |

## Requirements

### Functional — v0.1.0

- **REQ-001:** `mastodon_social` portmanteau (post, reply, boost, upload_media, timeline, notifications, outbox_*)
- **REQ-002:** Dual transport: stdio + streamable HTTP `/mcp`
- **REQ-003:** REST health `/api/health`, outbox CRUD `/api/v1/outbox/*`, compose proxy
- **REQ-004:** SQLite outbox store (`pending` → `approved` → `published` | `rejected`)
- **REQ-005:** `outbox_enqueue` accepts fleet-PR `mastodon_payload.json`
- **REQ-006:** Dry-run default; publish no-ops unless env allows
- **REQ-007:** Dark webapp: Compose, Timelines, Outbox, Accounts, Settings
- **REQ-008:** `start.ps1` + justfile (fleet conventions)
- **REQ-009:** Ports registered in WEBAPP_PORTS.md

### Functional — later

- **REQ-101:** Multi-account / multi-instance profiles
- **REQ-102:** Media upload from local path for release screenshots
- **REQ-103:** Prefab outbox card for Cursor
- **REQ-104:** Optional aiwatcher `ingest_fleet_event` on successful publish

### Non-functional

| Area | Requirement |
|------|-------------|
| Security | Bind 127.0.0.1; tokens only in `.env` |
| Safety | Human approve before fleet drafts publish |
| Tone | Align with FLEET_PROMOTION.md |
| Portability | Windows primary |

## Payload contract (`mastodon_payload.json`)

```json
{
  "schema_version": 1,
  "source": "fleet-public-relations-mcp",
  "repo_id": "mixx-dj-mcp",
  "campaign": "dogfood-mixxx-2026-07",
  "status_text": "…",
  "visibility": "public",
  "spoiler_text": null,
  "media_paths": [],
  "cw_sensitive": false,
  "idempotency_key": "mixx-dj-mcp:release:0.x.y:mastodon",
  "created_at": "2026-07-26T12:00:00Z"
}
```

## Integration

| Peer | Direction | Mechanism |
|------|-----------|-----------|
| fleet-public-relations-mcp | inbound | `POST http://127.0.0.1:10754/api/v1/outbox` |
| scraper-mcp | none | grades gate stays in fleet-PR |
| git-github-mcp | none (optional later) | releases stay optional from fleet-PR |
| aiwatcher-mcp | outbound optional | `ingest_fleet_event` after publish |

## Dogfood campaign (first use)

- **Hero:** mixx-dj-mcp + mixxxxx
- **Hook (draft seed):** "AI-native DJ control — forked Mixxx for video decks. Claude fades in Daft Punk on the next beat."
- **Gate:** scraper grades + README hook lint + human approve in Outbox UI before any live post

## Implementation plan

1. Scaffold (this) — README, PRD, AGENTS, .env.example
2. Skeleton — pyproject, server, portmanteau stub, outbox SQLite, start.ps1, empty webapp shell
3. Mastodon REST client (statuses + media) behind dry_run
4. Outbox UI + fleet-PR `queue_fediverse` client
5. Dogfood dry-run campaign for mixx-dj-mcp

## Out of scope for v0.1

- Gateway streaming / notifications push
- Federation peer discovery beyond one instance token
- Public GitHub release of this repo (stays private until said otherwise)

## References

- [README.md](README.md)
- discord-mcp PRD / portmanteau pattern
- `mcp-central-docs/standards/FLEET_PROMOTION.md`
- Mastodon API: https://docs.joinmastodon.org/api/

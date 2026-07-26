# mastodon-mcp

<p align="center">
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.4%2B-7c5cfc?style=flat-square" alt="FastMCP"></a>
</p>

Fediverse (Mastodon / ActivityPub) bridge for the sandraschi fleet — compose, timelines, and a **human-approved outbox** for promotion drafts from `fleet-public-relations-mcp`.

**v0.1.0** · Private · Ports **10754** / **10755** · Pattern sibling of [discord-mcp](https://github.com/sandraschi/discord-mcp) (10756/10757)

> FastMCP 3.4+ · outbox REST · dark webapp · pytest + Playwright e2e · MCPB · Tauri/NSIS scaffold · dry-run default. Reply/boost/media still stubs.

> Mastodon = ActivityPub microblogging. **Not** Bluesky (AT Protocol — separate later).

---

## Principle

Agents draft. Humans approve. Nothing posts without an explicit outbox approve → publish step.

Tone for fleet drafts must follow [`FLEET_PROMOTION.md`](../mcp-central-docs/standards/FLEET_PROMOTION.md): useful pointer, not AI grifter.

---

## Architecture (fleet)

```
scraper-mcp (10998)          grades / readiness
        │
fleet-public-relations-mcp   draft release notes + mastodon_payload.json
        │  queue_fediverse (HTTP handoff — no inline Mastodon API in fleet-PR)
        ▼
mastodon-mcp outbox          pending → human approve → publish
        │
Mastodon instance API        statuses, media, boosts, replies
```

---

## Ports

| Service | Port | URL |
|---------|------|-----|
| Backend (REST + MCP `/mcp`) | **10754** | http://127.0.0.1:10754 |
| Web dashboard | **10755** | http://127.0.0.1:10755 |

Register in `mcp-central-docs/operations/WEBAPP_PORTS.md` when implementing (10754/10755 free as of 2026-07-26; adjacent to discord-mcp).

---

## MCP tools (planned)

### `mastodon_social` portmanteau

| Operation | Role |
|-----------|------|
| `post` | Create status (blocked unless dry_run=false **and** outbox-approved path, or explicit interactive compose) |
| `reply` | Reply to a status |
| `boost` | Reblog |
| `upload_media` | Attach media, return media_id |
| `timeline` | Home / local / public / hashtag |
| `notifications` | List notifications |
| `outbox_list` | Pending / approved / published / rejected drafts |
| `outbox_enqueue` | Accept payload from fleet-PR (`mastodon_payload.json` shape) |
| `outbox_approve` | Human (or webapp) marks draft ready |
| `outbox_publish` | POST to instance; default dry_run unless `MASTODON_DRY_RUN=0` |
| `outbox_reject` | Discard with reason |
| `accounts_list` | Multi-instance account profiles |

Also: `mastodon_help`, `mastodon_shutdown`, optional Prefab status card.

---

## Webapp (dark, discord-mcp layout)

| Page | Purpose |
|------|---------|
| **Compose** | Manual status + media; still respects dry_run |
| **Timelines** | Home / local / public |
| **Outbox** | Fleet-PR drafts — review, edit, approve, publish |
| **Accounts** | Multi-instance tokens (local SQLite, never commit) |
| **Settings** | Instance URL, dry_run toggle display, health |

---

## Quick start (when implemented)

```powershell
cd D:\Dev\repos\mastodon-mcp
Copy-Item .env.example .env
# Edit MASTODON_INSTANCE + MASTODON_ACCESS_TOKEN
.\start.ps1
```

Dashboard: http://127.0.0.1:10755 · MCP: http://127.0.0.1:10754/mcp

---

## Env (see `.env.example`)

| Variable | Default | Notes |
|----------|---------|-------|
| `MASTODON_INSTANCE` | — | e.g. `https://mastodon.social` |
| `MASTODON_ACCESS_TOKEN` | — | App token with write:statuses |
| `MASTODON_DRY_RUN` | `1` | Default on — publish logs only |
| `MASTODON_BACKEND_PORT` | `10754` | |
| `MASTODON_REQUIRE_OUTBOX_APPROVAL` | `1` | Agent `post` without outbox id rejected |

---

## Safety

- Bind `127.0.0.1` only
- Dry-run default
- Outbox approve required for fleet-PR payloads
- No auto-post from fleet-PR or scraper-mcp
- Rate-limit client-side; respect `429` / `Retry-After`

---

## Tests

```powershell
uv run pytest tests/ -q          # unit + API e2e (TestClient)
cd webapp; npm run test:e2e      # Playwright: health, outbox handoff, notifications inbox, Compose UI
```

Coverage includes fleet-PR inbound payload → outbox → approve → dry-run publish, and notifications inbox (empty under dry-run without tokens).

---

## Packaging / native

| Artifact | Command |
|----------|---------|
| MCPB | `just mcpb-pack` → `dist/mastodon-mcp-v0.1.0.mcpb` |
| Tauri/NSIS | scaffold in `src-tauri/` — icons + `mastodon-mcp-backend.spec` before `just build-native` |
| CI | **None** while private (`.nopublish`) |

See [INSTALL.md](INSTALL.md) · [PRD.md](PRD.md) · [llms-full.txt](llms-full.txt).

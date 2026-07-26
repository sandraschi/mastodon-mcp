# mastodon-mcp

<p align="center">
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.4%2B-7c5cfc?style=flat-square" alt="FastMCP"></a>
</p>

Fediverse (Mastodon / ActivityPub) bridge for the sandraschi fleet — compose, timelines, and a **human-approved outbox** for promotion drafts from `fleet-public-relations-mcp`.

**v0.1.1** · Private · Ports **10754** / **10755** · Sibling of [discord-mcp](https://github.com/sandraschi/discord-mcp)

> FastMCP 3.4+ · full portmanteau (reply/boost/media/webhooks) · SOTA webapp · dry-run default · Windows CI workflow + local `just ci`

> Mastodon = ActivityPub. **Not** Bluesky.

---

## Principle

Agents draft. Humans approve. Nothing posts without outbox approve → publish.

Tone: [`FLEET_PROMOTION.md`](../mcp-central-docs/standards/FLEET_PROMOTION.md).

---

## Features

- Human-approved outbox + fleet-PR REST handoff
- Full `mastodon_social` ops: post, reply, boost, media, timelines, notifications, webhooks
- Dark SOTA webapp: Dashboard, Inbox, Outbox, Compose (AI assist), Chat, Skills, Tools, Settings, Help
- Dry-run default; inbound webhooks with shared secret
- Ruff + Biome + pytest gate; Windows-only CI workflow

---

## Quick start

```powershell
cd D:\Dev\repos\mastodon-mcp
Copy-Item .env.example .env
# Edit MASTODON_INSTANCE + MASTODON_ACCESS_TOKEN
.\start.bat
```

Dashboard: http://127.0.0.1:10755 · MCP: http://127.0.0.1:10754/mcp

---

## Documentation

| Doc | Contents |
|-----|----------|
| [INSTALL.md](INSTALL.md) | Install paths |
| [docs/ONBOARDING.md](docs/ONBOARDING.md) | First-timer: account, money/CC, pitfalls, sanity check |
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | Env vars |
| [docs/TOOLS.md](docs/TOOLS.md) | MCP + REST reference |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Lint, `just ci`, packaging |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Symptom → fix |

---

## Ports

| Service | Port |
|---------|------|
| Backend | **10754** |
| Webapp | **10755** |

---

## MCP tools

Portmanteau **`mastodon_social`** — all operations implemented (see [docs/TOOLS.md](docs/TOOLS.md)). Also `mastodon_help`, `mastodon_shutdown`, `show_outbox_card`.

---

## Quality

```powershell
just ci
```

Private repos: GitHub Actions stay disabled at account level (billing). Workflow file is still required; run `just ci` locally.

---

## License

MIT (see LICENSE if present)

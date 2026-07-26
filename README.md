# mastodon-mcp

<p align="center">
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.4%2B-7c5cfc?style=flat-square" alt="FastMCP"></a>
  <a href="https://github.com/sandraschi/mastodon-mcp/actions"><img src="https://img.shields.io/github/actions/workflow/status/sandraschi/mastodon-mcp/ci.yml?branch=master&style=flat-square" alt="CI"></a>
  <a href="https://joinmastodon.org/"><img src="https://img.shields.io/badge/Fediverse-ActivityPub-6364FF?style=flat-square" alt="ActivityPub"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-yellow?style=flat-square" alt="MIT"></a>
</p>

Fediverse **Mastodon client** (ActivityPub) — full webapp + MCP agent automation, including a **human-approved outbox** for promotion drafts from `fleet-public-relations-mcp`.

**v0.1.1** · Ports **10754** / **10755** · Sibling of [discord-mcp](https://github.com/sandraschi/discord-mcp) · AT Proto sibling [bluesky-mcp](https://github.com/sandraschi/bluesky-mcp)

> FastMCP 3.4+ · full portmanteau (reply/boost/media/webhooks) · SOTA webapp · dry-run default · Windows CI + local `just ci`

> Mastodon = ActivityPub. **Not** Bluesky. Primer: [docs/FEDIVERSE.md](docs/FEDIVERSE.md).

---

## Principle

Agents draft and assist. Humans approve fleet promotion posts. Interactive client use still respects dry-run until you go live.

Tone: [`FLEET_PROMOTION.md`](../mcp-central-docs/standards/FLEET_PROMOTION.md).

---

## Features

- Full Mastodon web client: Inbox, Timelines, Compose (AI assist), Chat, Accounts, Skills, Tools, Settings, Help
- Agent automation via `mastodon_social` portmanteau + Prefab cards
- Human-approved outbox + fleet-PR REST handoff (safety gate — not the only job)
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

# Installing mastodon-mcp

Private fleet Fediverse bridge — human-approved outbox for `fleet-public-relations-mcp` drafts.

> **First time?** Complete [docs/ONBOARDING.md](docs/ONBOARDING.md) before expecting live Mastodon calls (account, token, money/CC honesty, pitfalls).

## Prerequisites

| Tool | Purpose | Install (Windows) |
|------|---------|-------------------|
| Git | Clone | `winget install Git.Git` |
| uv | Python deps | `winget install astral-sh.uv` |
| Node.js | Webapp | `winget install OpenJS.NodeJS` |
| just | Recipes (optional) | `winget install Casey.Just` |

Mastodon access token: instance → Preferences → Development → New application (`read` + `write:statuses` + `write:media`).

---

## Option A — MCPB (local pack)

```powershell
cd D:\Dev\repos\mastodon-mcp
just mcpb-pack
# Install dist\mastodon-mcp-v0.1.0.mcpb via Claude Desktop → MCP Servers → Install from file
```

Keep `MASTODON_DRY_RUN=1` until you intend to post.

---

## Option B — Fastest from source

```powershell
cd D:\Dev\repos\mastodon-mcp
Copy-Item .env.example .env
# Edit .env — MASTODON_INSTANCE + MASTODON_ACCESS_TOKEN
.\start.ps1
```

Dashboard **http://127.0.0.1:10755** · API/MCP **http://127.0.0.1:10754** (`/mcp`).

---

## Option C — Manual

```powershell
uv sync --extra dev
Set-Location webapp
npm install
Set-Location ..
Copy-Item .env.example .env
.\start.ps1
```

**Stdio only** (no webapp):

```powershell
uv run python -m mastodon_mcp
# or FastMCP stdio host config pointing at the same module
```

---

## Cursor / Claude Desktop (HTTP)

```json
{
  "mcpServers": {
    "mastodon-mcp": {
      "url": "http://127.0.0.1:10754/mcp"
    }
  }
}
```

---

## Verify

```powershell
Invoke-WebRequest http://127.0.0.1:10754/api/health -UseBasicParsing
uv run pytest tests/ -q
```

---

## Safety

- Default `MASTODON_DRY_RUN=1` — no public posts
- Outbox approve required before publish
- No GitHub Actions while private (`.nopublish`)

See [README.md](README.md) and [PRD.md](PRD.md).

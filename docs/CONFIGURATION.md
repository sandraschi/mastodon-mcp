# Configuration — mastodon-mcp

Copy `.env.example` to `.env` and edit.

| Variable | Default | Purpose |
|----------|---------|---------|
| `MASTODON_INSTANCE` | — | Base URL, e.g. `https://mastodon.social` |
| `MASTODON_ACCESS_TOKEN` | — | App token (`read`, `write:statuses`, `write:media`, `push` optional) |
| `MASTODON_DRY_RUN` | `1` | `1` = simulate writes; `0` = live |
| `MASTODON_REQUIRE_OUTBOX_APPROVAL` | `1` | Block direct `post` without outbox |
| `MASTODON_BACKEND_PORT` | `10754` | FastAPI + MCP |
| `MASTODON_DATA_DIR` | `%LOCALAPPDATA%\mastodon-mcp` | SQLite outbox + webhooks |
| `MASTODON_WEBHOOK_SECRET` | — | Shared secret for `POST /api/v1/webhooks/inbound` |
| `MASTODON_LOG_LEVEL` | `INFO` | Logging |
| `PORT` | (backend port) | Override bind port (Tauri / packagers) |

Frontend Vite port is **10755** (fixed in `webapp/vite.config.ts` / `start.ps1`).

Claude Desktop / Cursor `env` block should pass the same keys when using stdio or HTTP MCP.

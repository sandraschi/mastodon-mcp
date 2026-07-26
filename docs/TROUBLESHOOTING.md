# Troubleshooting — mastodon-mcp

| Symptom | Fix |
|---------|-----|
| Publish succeeds but nothing on instance | Expected when `MASTODON_DRY_RUN=1`. Set `0` and restart only for live posts. |
| Direct `post` rejected | Outbox required. Enqueue → approve → `outbox_publish`, or set `MASTODON_REQUIRE_OUTBOX_APPROVAL=0`. |
| Timelines / inbox empty errors | Set `MASTODON_INSTANCE` + `MASTODON_ACCESS_TOKEN`. |
| Webhook inbound rejected | Set `MASTODON_WEBHOOK_SECRET` and send header `X-Mastodon-Webhook-Secret`. Without secret, only accepted while dry_run is on. |
| Chat / AI assist fails | Start Ollama on `:11434` (or LM Studio `:1234`). Check Settings provider probe. |
| Port in use | `start.ps1` clears 10754/10755; kill leftover node/python if needed. |
| Biome / ruff red | `just ci` — fix before commit. |
| Private repo CI badge failing | Actions disabled on private by fleet policy; use local `just ci`. |

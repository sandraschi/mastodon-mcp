# Onboarding — mastodon-mcp

## What this is for

**mastodon-mcp** is a Fediverse (Mastodon / ActivityPub) bridge for the sandraschi fleet. Agents and `fleet-public-relations-mcp` enqueue promotion drafts into a **human-approved outbox**. You review, approve, then publish.

It is **not** an auto-poster, **not** Bluesky (AT Protocol), and **not** a growth-hacking bot. Default mode is dry-run so nothing hits the public timeline until you say so.

## Cost and accounts (money / CC)

| Question | Answer |
|----------|--------|
| Do I need an account? | **Yes** — an account on a Mastodon-compatible instance |
| Free tier? | **Usually yes** on public instances (mastodon.social, fosstodon.org, etc.). Some instances are invite-only. |
| Credit card required? | **No** for typical public instances. Self-hosting or paid hosts may bill separately — that is between you and the host, not this repo. |
| Ongoing cost? | Free on most community instances; optional paid hosting if you run your own |
| Who bills? | Your instance host (if anyone) — not sandraschi / not this MCP |

## Prerequisites outside this repo

- A Mastodon (or compatible) **account** you control
- Ability to open **Preferences → Development → New application** on that instance
- Token scopes: at least `read`, `write:statuses`, `write:media` (add `push` if you use push subscription later)
- Optional: `MASTODON_WEBHOOK_SECRET` if other fleet tools will POST to `/api/v1/webhooks/inbound`

Install tooling (uv, Node, git) is covered in [INSTALL.md](../INSTALL.md) — not repeated here.

## First-timer setup steps

1. Create or log into your Mastodon account in a browser.
2. Open **Preferences → Development → New application**.
3. Name it e.g. `mastodon-mcp`, enable scopes above, submit, copy the **access token**.
4. Copy the instance base URL (no trailing slash), e.g. `https://mastodon.social`.
5. In the repo:
   ```powershell
   cd D:\Dev\repos\mastodon-mcp
   Copy-Item .env.example .env
   ```
6. Edit `.env`:
   - `MASTODON_INSTANCE=https://your.instance`
   - `MASTODON_ACCESS_TOKEN=...`
   - Keep `MASTODON_DRY_RUN=1` until you intentionally go live
7. Start: `.\start.bat` → dashboard http://127.0.0.1:10755
8. Open **Settings** — confirm “Instance configured” / health shows configured.
9. Enqueue a test draft on **Compose** or **Outbox**, approve, publish — expect `dry_run: true` until you set `MASTODON_DRY_RUN=0`.

## Pitfalls

- **Dry-run default** — publish “succeeds” but does not toot. This is intentional. Flip `MASTODON_DRY_RUN=0` only when you mean it, then restart the backend.
- **Direct `post` blocked** — fleet path is outbox → approve → publish (`MASTODON_REQUIRE_OUTBOX_APPROVAL=1`).
- **Wrong scopes** — media upload / write fails with HTTP 403 if the app lacks `write:media` / `write:statuses`.
- **Token in git** — never commit `.env`. Rotate the token if it leaks.
- **Tone** — fleet drafts follow `FLEET_PROMOTION.md` (no hype, no “written by AI” theater).
- **Invite-only instances** — signup may wait on a human moderator; plan ahead.
- **Not Bluesky** — different protocol; do not paste AT Protocol handles into Mastodon fields.

## Sanity check

| Check | Expected |
|-------|----------|
| `GET http://127.0.0.1:10754/api/health` | `"instance_configured": true` when token + instance set |
| Settings page | Shows instance configured; LLM probe is separate (optional) |
| Outbox publish with dry_run | `"success": true`, `"dry_run": true`, message about not posted |
| Inbox without token | Empty list + dry message — not fabricated notifications |

## Declared doubles

See [DEVELOPMENT.md](DEVELOPMENT.md) § Declared doubles. Without finishing this onboarding, the server still runs: dry-run writes, empty notifications API, local outbox SQLite.

### Mock-until-onboarded (webapp)

Until `instance_configured` is true, the dashboard shows a **big red** “Complete onboarding” button under the hero, plus **MOCK**-badged sample KPIs / outbox rows and inbox messages from **Joe Mocky** and **Sandra Mockinger**. Those UI samples are declared in `webapp/src/lib/mockOnboarding.ts` and disappear automatically after you set instance + token — they are not live Fediverse data.

# Fediverse — what this is

## What is the fediverse?

The **fediverse** is a network of independent social servers that talk to each other with **ActivityPub**. You pick an instance (a home server), get an account there, and can follow / reply / boost people on *other* instances — similar to email across different providers.

| Term | Meaning |
|------|---------|
| **Fediverse** | The whole ActivityPub social network (Mastodon, Pixelfed, PeerTube, …) |
| **Mastodon** | The most common *microblogging* software on that network — short posts (“toots”), timelines, boosts, replies |
| **Instance** | One Mastodon (or compatible) server, e.g. `mastodon.social`, or a self-hosted host |
| **ActivityPub** | The open protocol those servers use to federate |

This repo is **not** Bluesky. Bluesky uses **AT Proto** — see sibling `bluesky-mcp` if you need that.

## What is mastodon-mcp?

**mastodon-mcp** is a full-featured **Mastodon client + MCP server** for agents and humans:

1. **Webapp client** — Inbox, timelines, compose, accounts, settings (ports **10754** / **10755**)
2. **Agent automation** — FastMCP tools (`mastodon_social` portmanteau), Chat, Compose AI assist, Skills, Prefab cards
3. **Fleet safety gate** — Human-approved **outbox** for promotion drafts from `fleet-public-relations-mcp` (one capability among many — not the whole product)

Dry-run is the default. Live posts need instance URL + access token, and outbox approve → publish when the approval gate is on.

## How it fits the fleet

```text
scraper-mcp → fleet-public-relations-mcp (drafts)
                    ↓
              mastodon-mcp outbox  →  human approve  →  Mastodon API
                    ↕
         webapp + MCP agents (read timelines, reply, boost, …)
```

## Learn more

- [ONBOARDING.md](ONBOARDING.md) — account, token, money/CC
- [TOOLS.md](TOOLS.md) — MCP + REST surface
- [CONFIGURATION.md](CONFIGURATION.md) — env vars
- Help page → **Fediverse** tab in the webapp

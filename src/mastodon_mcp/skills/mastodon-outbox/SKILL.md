# Mastodon Outbox Skill

## Role

Hold promotion drafts from `fleet-public-relations-mcp` until a human approves, then publish to Mastodon (dry-run by default).

## Flow

1. Fleet-PR: `pr_draft` → `pr_approve_draft` → `pr_queue_fediverse`
2. This server: outbox `pending`
3. Human: Outbox UI or `outbox_approve`
4. `outbox_publish` — posts only if `MASTODON_DRY_RUN=0`

## Tools

- `mastodon_social_tool(operation=…)` — outbox_* / timeline / notifications / accounts_list
- `mastodon_help` — ports and flow summary

## Safety

Never auto-publish. Never bypass outbox for fleet drafts.

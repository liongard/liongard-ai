---
name: liongard-setup
description: Install and configure the Liongard MCP server in Claude Code using Bearer Access Token auth.
argument-hint: "[instance] [scope]"
---

# Liongard MCP setup

You are guiding the user through installing the Liongard MCP server into
Claude Code. Do exactly the following — do not skip or combine steps.

Bearer Access Token auth is the supported setup path. OAuth is experimental and
client-dependent; do not offer it as the default.

## Step 1 — gather input

Ask the user, one at a time (or all at once if that's more natural):

1. **Liongard instance hostname.** Accept either `acme` or
   `acme.app.liongard.com`. If they give just the subdomain, append
   `.app.liongard.com`. Reject anything that includes a scheme or path —
   only the hostname is valid. Store as `INSTANCE`.
2. **Token.** Ask for the combined Access Token from **AI Preferences -> Access
   Tokens**. It must be `<accessKeyId>:<accessKeySecret>` and start with
   `lg_mcp_`. Treat it as secret — do not echo it back in full. Store as
   `TOKEN`.
3. **Scope.** Offer `user` (default, recommended; applies to all their
   projects) or `local` (this project only) or `project` (shared via
   `.mcp.json`, commit without the token). Store as `SCOPE`. Default: `user`.

## Step 2 — register the server

Construct the URL: `https://${INSTANCE}/api/mcp`.

Preview the exact command you're about to run and ask the user to confirm.
Redact the token in the preview (show `Bearer lg_mcp_<id>:***`).

Run **exactly one** of these via the shell:

```bash
claude mcp add --scope ${SCOPE:-user} --transport http liongard \
  "https://${INSTANCE}/api/mcp" \
  --header "Authorization: Bearer ${TOKEN}"
```

If the server already exists, ask the user whether to remove and re-add, or
update in place. `claude mcp remove liongard` deletes an existing entry.

## Step 3 — verify

Run:

```bash
claude mcp list
claude mcp get liongard
```

Confirm the output shows:

- `liongard` is present.
- Transport is `http`.
- URL matches `https://${INSTANCE}/api/mcp`.

## Step 4 — smoke test

Ask the user if they're ready to smoke-test. If yes, call the Liongard MCP
via `tools/call` for a small, safe query:

- Call `liongard_environment` with `{ operation: "COUNT" }` to get the total
  count of environments the token can see.
- If that succeeds, call `liongard_environment` with
  `{ operation: "LIST", pageSize: 5 }` and show the first 5 environment
  names.

If the call fails, route the user to `/liongard-doctor`.

## Step 5 — next steps

Tell the user:

- They can start asking Liongard questions in this chat.
- Useful starting prompts:
  - "What alerts are open in `<environment name>`?"
  - "Show me MFA coverage across all environments."
  - "Investigate alert `<id>`."
- Examples live in `examples/prompts.md`.
- If they want a structured workflow, they can load a Liongard skill —
  `liongard-investigate-alert`, `liongard-environment-health`,
  `liongard-compliance-audit`.

## Guardrails

- Never print the full token back to the user.
- Never log the token to a file.
- If the user provides a malformed token (no colon, no `lg_mcp_` prefix),
  stop and ask them to recreate in the Liongard UI.
- If `claude mcp add` returns a non-zero exit code, show the error and stop.

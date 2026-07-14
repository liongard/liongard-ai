---
name: liongard-setup-api-key
description: Install the Liongard MCP server using Bearer Access Token auth (non-interactive path).
argument-hint: "<instance> <token> [scope]"
---

# Liongard MCP setup — API key

Non-interactive variant of `/liongard-setup` that assumes the user already has
an Access Token from **AI Preferences -> Access Tokens**.

## Arguments

`$ARGUMENTS` should contain, in order:

1. `INSTANCE` — instance hostname, either `acme` or `acme.app.liongard.com`.
2. `TOKEN` — combined token in the form `<accessKeyId>:<accessKeySecret>`.
3. `SCOPE` *(optional, default `user`)* — one of `user`, `local`, `project`.

If any required argument is missing, fall back to `/liongard-setup` and
gather them interactively.

## Validation

Before running anything:

- `INSTANCE` must not contain `://` or `/`. If only a subdomain is given,
  append `.app.liongard.com`.
- `TOKEN` must match `lg_mcp_<something>:<something>`. If it doesn't,
  stop and ask the user to recreate in Liongard → AI Preferences → Access Tokens.
- `SCOPE` must be one of `user`, `local`, `project`.

## Register

Preview the command with a redacted token (`Bearer lg_mcp_<id>:***`) and
run:

```bash
claude mcp add --scope ${SCOPE:-user} --transport http liongard \
  "https://${INSTANCE}/api/mcp" \
  --header "Authorization: Bearer ${TOKEN}"
```

If the server already exists, remove it first:

```bash
claude mcp remove liongard
```

## Verify

```bash
claude mcp list
claude mcp get liongard
```

## Smoke test

Call `liongard_environment` with `{ operation: "COUNT" }` via `tools/call`.
On success, tell the user they're good to go. On failure, route to
`/liongard-doctor`.

## Guardrails

- Never print the full token back to the user.
- Never write the token to a file that isn't the Claude Code config.

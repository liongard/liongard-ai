---
name: liongard-setup-oauth
description: Experimental OAuth setup for Liongard MCP; use Bearer Access Token setup unless explicitly testing OAuth.
argument-hint: "<instance> [scope]"
---

# Liongard MCP setup — OAuth

OAuth is experimental and client-dependent. Do not use this command for normal
customer setup. Prefer `/liongard-setup` with a Bearer Access Token.

Before continuing, tell the user this path is only for testing OAuth behavior
in their exact Claude Code version and ask for explicit confirmation.

## Arguments

`$ARGUMENTS` should contain, in order:

1. `INSTANCE` — instance hostname, either `acme` or `acme.app.liongard.com`.
2. `SCOPE` *(optional, default `user`)* — one of `user`, `local`, `project`.

If `INSTANCE` is missing, fall back to `/liongard-setup`.

## Validation

- `INSTANCE` must not contain `://` or `/`. If only a subdomain is given,
  append `.app.liongard.com`.
- `SCOPE` must be one of `user`, `local`, `project`.

## Register

```bash
claude mcp add --scope ${SCOPE:-user} --transport http liongard \
  "https://${INSTANCE}/api/mcp"
```

If the server already exists, `claude mcp remove liongard` first.

## Complete OAuth

Tell the user to:

1. Run `/mcp` in this Claude Code session.
2. Select `liongard`.
3. Choose **Authenticate** and complete the browser login (MFA included).

Wait for the user to confirm auth succeeded before continuing.

## Verify

```bash
claude mcp list
claude mcp get liongard
```

## Smoke test

Call `liongard_environment` with `{ operation: "COUNT" }` via `tools/call`.
On success, tell the user they're good to go. On failure, route to
`/liongard-doctor`.

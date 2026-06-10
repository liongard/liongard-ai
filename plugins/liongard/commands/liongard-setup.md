---
name: liongard-setup
description: Configure the hosted Liongard MCP server in Claude Code using Bearer Access Token auth.
argument-hint: "[instance] [scope]"
---

# Liongard MCP Setup

Guide the user through Claude Code setup. Use Bearer Access Token auth as the
default and supported path.

## Inputs

`$ARGUMENTS` may include:

- `INSTANCE` — `acme` or `acme.app.liongard.com`.
- `SCOPE` — `user`, `local`, or `project` (default `user`).

If missing, ask for them. Ask for the MCP token separately and never echo it.
The token is `<accessKeyId>:<accessKeySecret>` from **AI Preferences -> Access
Tokens**.

## Steps

1. Normalize `INSTANCE` to `<instance>.app.liongard.com`.
2. Validate the token contains a colon and starts with `lg_mcp_`.
3. Preview the command with the token redacted.
4. If `liongard` already exists, ask before removing it.
5. Run:

   ```bash
   claude mcp add --scope ${SCOPE:-user} --transport http liongard \
     "https://${INSTANCE}/api/mcp" \
     --header "Authorization: Bearer ${TOKEN}"
   ```

6. Run:

   ```bash
   claude mcp list
   claude mcp get liongard
   ```

7. Ask the user to verify with: `List my Liongard environments.`

## Guardrails

- Do not offer OAuth as the normal path. It is experimental and client-dependent.
- Do not print, log, or persist the token anywhere except the Claude MCP config.
- If setup fails, route the user to `/liongard-doctor`.

---
name: liongard-setup-api-key
description: Non-interactive Claude Code setup for Liongard MCP Bearer Access Token auth.
argument-hint: "<instance> <token> [scope]"
---

# Liongard MCP Setup — Bearer Token

Use this when the user already has an Access Token from **AI Preferences ->
Access Tokens**.

## Arguments

1. `INSTANCE` — `acme` or `acme.app.liongard.com`.
2. `TOKEN` — `<accessKeyId>:<accessKeySecret>`.
3. `SCOPE` — optional; `user`, `local`, or `project`; default `user`.

If required arguments are missing, fall back to `/liongard-setup`.

## Register

Redact the token in any preview, then run:

```bash
claude mcp add --scope ${SCOPE:-user} --transport http liongard \
  "https://${INSTANCE}/api/mcp" \
  --header "Authorization: Bearer ${TOKEN}"
```

If the server exists, ask before running:

```bash
claude mcp remove liongard
```

## Verify

```bash
claude mcp list
claude mcp get liongard
```

Then ask the user to try: `List my Liongard environments.`

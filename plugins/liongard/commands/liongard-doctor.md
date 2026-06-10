---
name: liongard-doctor
description: Diagnose Liongard MCP registration, network, auth, and tool-call issues.
---

# Liongard MCP Doctor

Walk through checks in order. Stop at the first hard failure and give the most
likely fix.

## Checks

1. **Registration**

   ```bash
   claude mcp list
   ```

   If `liongard` is missing, tell the user to run `/liongard-setup`.

2. **Config**

   ```bash
   claude mcp get liongard
   ```

   Verify `http`, `https://<instance>.app.liongard.com/api/mcp`, and an
   Authorization header. Redact secrets.

3. **Reachability**

   Send a JSON-RPC `ping` to the configured URL. Interpret `401` as reachable
   but unauthenticated.

4. **Auth**

   On `401`, tell the user to recreate the credential in **AI Preferences ->
   Access Tokens** and re-run `/liongard-setup`.

5. **Safe tool call**

   Call `liongard_environment` with `{ "operation": "COUNT" }`.

## Error Hints

- `-32002` — reconnect or restart the MCP server in the client.
- `401` — bad, expired, revoked, or malformed token.
- `403` — tenant access or token scope issue.
- Empty environment list — likely token scope.

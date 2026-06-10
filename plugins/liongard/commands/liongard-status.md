---
name: liongard-status
description: Show the current Liongard MCP registration and run a safe connectivity check.
---

# Liongard MCP Status

Report concise status for the `liongard` MCP server.

## Checks

1. Run:

   ```bash
   claude mcp list
   claude mcp get liongard
   ```

2. Confirm:

   - `liongard` is registered.
   - Transport is `http`.
   - URL ends with `/api/mcp`.
   - Authorization header exists; never print the token.

3. If connected, call `liongard_environment` with `{ "operation": "COUNT" }`.

## Output

Use plain labels:

- `OK` — connected, with visible environment count.
- `WARN` — registered but not initialized.
- `FAIL` — auth, network, or registration problem.

If unhealthy, recommend `/liongard-doctor`.

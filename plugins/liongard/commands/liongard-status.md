---
name: liongard-status
description: Show the current Liongard MCP server registration and a quick connectivity check.
---

# Liongard MCP status

Give the user a concise status report.

## Step 1 — registration

Run:

```bash
claude mcp list
claude mcp get liongard
```

Extract and show:

- Whether `liongard` is registered.
- Scope (`user`, `local`, or `project`).
- Transport (should be `http`).
- URL.
- Whether an `Authorization` header is configured (yes / no — do not print the token).

## Step 2 — connectivity check

If `liongard` is registered, attempt a safe MCP call via `tools/call`:

- Call `liongard_environment` with `{ operation: "COUNT" }`.

Report one of:

- `CONNECTED` with the returned environment count.
- `AUTH_FAILED` if the response is `401`. Suggest `/liongard-setup` again.
- `NOT_INITIALIZED` on JSON-RPC `-32002`. Suggest waiting a few seconds and
  retrying, or restarting Claude Code.
- `UNREACHABLE` on network-level failures. Suggest checking VPN / proxy and
  the instance hostname.

## Step 3 — summary

Print a one-line summary with plain labels:

- `OK`: Liongard MCP is connected (`<n>` environments visible).
- `WARN`: Liongard MCP is registered but auth or initialization failed.
- `FAIL`: Liongard MCP is not registered.

If anything is not healthy, offer to run `/liongard-doctor`.

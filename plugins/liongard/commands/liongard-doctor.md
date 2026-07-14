---
name: liongard-doctor
description: Diagnose Liongard MCP connectivity and auth issues in Claude Code.
---

# Liongard MCP doctor

Walk through a set of checks and report anything unhealthy. At each failing
check, give the user the most-likely fix and stop before blasting through
the rest.

## Check 1 — registration

Run:

```bash
claude mcp list
```

- If `liongard` is not in the list → tell the user to run `/liongard-setup`
  and stop.
- Otherwise continue.

## Check 2 — configuration

Run:

```bash
claude mcp get liongard
```

Verify:

- `type` / transport is `http`.
- `url` matches `https://<something>/api/mcp` exactly (no trailing slash,
  no extra path).
- For API-key auth, there's an `Authorization: Bearer lg_mcp_...:...` header
  (don't print the secret).

If any of those are wrong, offer to run `/liongard-setup` to re-register.

## Check 3 — DNS + TCP reachability

Extract the hostname from the URL and run:

```bash
getent hosts <hostname> || nslookup <hostname>
```

and

```bash
curl -sS -o /dev/null -w "%{http_code}\n" "https://<hostname>/api/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json,text/event-stream" \
  -X POST --data '{"jsonrpc":"2.0","id":1,"method":"ping"}'
```

Interpret:

- HTTP `401` — server is reachable but rejecting auth. Go to Check 4.
- HTTP `400` / `406` — the endpoint is wrong or the client isn't sending
  required headers. Verify the URL matches `/api/mcp`.
- HTTP `200` — everything looks healthy.
- Curl failure / DNS failure — suggest VPN / proxy / firewall.

## Check 4 — auth

If Check 3 returned `401`, the token is wrong, revoked, or expired. Tell
the user to:

1. Open Liongard → AI Preferences → Access Tokens.
2. Revoke and recreate the MCP Access Token.
3. Re-run `/liongard-setup` (or `/liongard-setup-api-key <instance> <token>`).

## Check 5 — live MCP call

Call `liongard_environment` with `{ operation: "COUNT" }` via `tools/call`.

- On success, report `Liongard MCP is healthy — <n> environments visible`.
- On error, show the JSON-RPC error and suggest next action:
  - `-32002 Server not initialized` — wait a few seconds and retry, or
    restart Claude Code.
  - `403 Forbidden` on a specific tool — tenant or token scope does not allow
    that capability; ask the user's Liongard admin to confirm access.
  - `401 Unauthorized` — token is bad, go back to Check 4.

## Check 6 — clock skew (only if auth keeps failing)

If auth keeps failing despite a fresh token, check the user's machine clock:

```bash
date -u
```

If it's more than ~5 minutes off, auth tokens can appear expired. Tell the
user to fix NTP / system time.

## Final summary

Give a short report:

- `Registered`: yes / no
- `Configuration`: OK / WARN (`<issue>`) / FAIL (`<issue>`)
- `Reachable`: OK / FAIL
- `Auth`: OK / FAIL
- `Tools`: OK (<n> environments) / FAIL (`<json-rpc error>`)

Then, if anything failed, name the single most likely fix in one sentence.

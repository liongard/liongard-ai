# Troubleshooting

If something isn't working, start here.

For a guided experience inside Claude Code, run:

```text
/liongard-doctor
```

---

## Connectivity

### "MCP server failed to start" / "Connection refused"

- Verify your instance hostname. In a browser, open
  `https://<your-instance>.app.liongard.com/` and confirm you can log in.
- The MCP endpoint is exactly `https://<your-instance>.app.liongard.com/api/mcp`
  (no trailing slash, no extra path).
- If you're on a corporate VPN or behind a proxy, make sure that host is
  reachable.

### `tools/list` returns nothing, or `tools/list` is empty

- Verify the configured URL is exactly `https://<your-instance>.app.liongard.com/api/mcp`.
- Some clients opt into **compact mode** during `initialize`. In compact mode
  `tools/list` returns only `liongard_navigate`; `tools/call` still works for
  every tool by canonical name. Call `liongard_navigate` to discover the
  catalog.

---

## Authentication

### `401 Unauthorized` on every request

- The token is wrong, revoked, or expired. Create a new token (Settings →
  AI Preferences → Access Tokens) and re-register the server.
- Double-check the `Authorization` header has the word `Bearer ` in front of
  the token (case-sensitive).
- The token must include both halves: `<accessKeyId>:<accessKeySecret>` — no
  space, no missing colon. User Access Token IDs usually start with `lg_mcp_`.

### `403 Forbidden` on a specific tool

- Your tenant or credential may not have access to that MCP capability.
- Your token's environment scope may not include the environment the tool is
  targeting. Re-create the token with a broader scope or pass an
  `environmentId` within scope.

### OAuth flow fails or times out

OAuth is experimental and client-dependent. Use a Bearer Access Token unless
you are explicitly testing OAuth support in a known-compatible client.

---

## Tool behavior

### "Server not initialized" / JSON-RPC `-32002`

This means the MCP client hasn't finished its `initialize` handshake yet.

- In Cursor, open **Settings → MCP** and reconnect the server.
- In Claude Code, run `/mcp` and wait for the server to come online, then
  retry your question.
- If the error persists, restart the client.

### Pagination looks stuck at one page

- Most `liongard_*` tools return a `Pagination` block with `HasMoreRows`,
  `TotalPages`, `CurrentPage`. If `HasMoreRows` is true, the agent should
  keep paging — ask it to "load all pages" or "give me an exact count".
- Aggregation queries (`aggregate: true, group_by: [...]` on `liongard_asset`)
  page internally; a single call returns exact totals.

### "No results" but you know the data exists

- Check the token's environment scope — scoped tokens can't see other
  environments.
- Keyword search defaults to `filter` mode; try `searchMode: "keyword"` on
  `liongard_environment` / `liongard_launchpoint` to allow fuzzy name match.
- Inventory `LIST` calls need at least one of `query` or `environmentId`; a
  bare `{operation: "LIST"}` returns nothing.

### `liongard_query` gives a generic "unable to retrieve the dataprint details" answer

- This is the agent's fallback message when no approach produced text. Ask it
  to retry, or rephrase with a specific system or environment name to narrow
  scope.

### Agent questions return no agent data

- Use `liongard_agents`, not `liongard_launchpoint`, for installed agent
  inventory and status questions.
- For customer-owned/on-prem agents, prefer `managed: false` unless you need a
  specific `type` filter.

---

## Client-specific

### Claude Code

- Run `/doctor` for a general config check.
- Run `/liongard-doctor` (shipped in this repo) for Liongard-specific checks.
- `claude mcp list` shows every registered server and whether it's connected.
- `claude mcp get liongard` shows the current config for the Liongard server.
- `claude mcp remove liongard` deletes the registration so you can re-add.

### Claude Desktop

- Config lives in `claude_desktop_config.json` (platform-specific path; see
  [`clients/claude-desktop.md`](clients/claude-desktop.md)).
- After editing, fully quit and relaunch Claude Desktop.
- If Claude Desktop shows no Liongard tools, check the app's log files for
  MCP errors.

### Cursor

- Config lives in `~/.cursor/mcp.json` (user scope) or `.cursor/mcp.json`
  (project scope).
- Cursor caches MCP state; use **Settings → MCP** to force a reconnect.
- MCP tool calls return `-32002` until the server has finished startup; reconnect
  the MCP server, then retry.

### VS Code / Copilot

- Make sure your Copilot version supports MCP.
- Config lives in your VS Code settings JSON under `"chat.mcp.servers"` or
  the dedicated MCP settings panel — see
  [`clients/vscode.md`](clients/vscode.md).

---

## When all else fails

Collect:

- Your client name and version.
- The exact MCP endpoint URL you configured (you can share it — it's public).
- A recent error message, scrubbed of token values.
- Output of `/liongard-status` (Claude Code) or `claude mcp get liongard`.

Then reach out to your Liongard CSM or open an issue in this repo.

# Harness Support Matrix

Stable baseline for every harness:

- Endpoint: `https://<instance>.app.liongard.com/api/mcp`
- Transport: streamable HTTP MCP
- Auth: `Authorization: Bearer <accessKeyId>:<accessKeySecret>`

Statuses:

- `verified` — tested with a real install and `liongard_environment COUNT`.
- `config provided` — config shape documented, but version-specific behavior can vary.
- `experimental` — supported by protocol/server behavior, but client UX varies.
- `unsupported` — not a good fit today.

## Matrix

| Harness | Status | Setup |
| --- | --- | --- |
| Claude Code | verified | Plugin or `claude mcp add`. |
| Claude Desktop | config provided | `claude_desktop_config.json`. |
| Cursor | config provided | `~/.cursor/mcp.json` or project `.cursor/mcp.json`. |
| VS Code / GitHub Copilot | config provided | `.vscode/mcp.json` or user-level `mcp.json` (`servers` key); requires `chat.mcp.enabled`. |
| Codex CLI | config provided | Use generic HTTP MCP server config if supported by installed version. |
| Gemini CLI | config provided | Use generic HTTP MCP server config if supported by installed version. |
| Continue | config provided | Use generic MCP server config in Continue config. |
| OpenCode | config provided | Use generic HTTP MCP server config if supported by installed version. |
| Windsurf | config provided | Use MCP settings UI/config if available in installed version. |
| Copilot Studio | experimental | Stateless authenticated `POST /api/mcp`; no skills/prompts UX guaranteed. |
| Custom MCP client | verified by protocol | Use `initialize`, `tools/list`, `tools/call`, Bearer auth. |

## Claude Code

Plugin path:

```text
/plugin marketplace add liongard/liongard-ai
/plugin install liongard
/liongard-setup
```

Manual path:

```bash
claude mcp add --scope user --transport http liongard \
  "https://<instance>.app.liongard.com/api/mcp" \
  --header "Authorization: Bearer <accessKeyId>:<accessKeySecret>"
```

## Claude Desktop

Generate:

```bash
node scripts/liongard-mcp-config.js --client claude-desktop --print
```

Config shape:

```json
{
  "mcpServers": {
    "liongard": {
      "type": "http",
      "url": "https://<instance>.app.liongard.com/api/mcp",
      "headers": {
        "Authorization": "Bearer <accessKeyId>:<accessKeySecret>"
      }
    }
  }
}
```

Fully quit and relaunch Claude Desktop after editing.

## Cursor

Generate:

```bash
node scripts/liongard-mcp-config.js --client cursor --print
```

User config lives at `~/.cursor/mcp.json`; project config lives at
`.cursor/mcp.json`.

Skills can be copied or symlinked from `plugins/liongard/skills` into
`.cursor/skills` if your Cursor version supports local skills.

## VS Code / GitHub Copilot

Generate:

```bash
node scripts/liongard-mcp-config.js --client vscode --print
```

Common shape (goes in `.vscode/mcp.json` in your workspace, or the user-level
`mcp.json` opened via **MCP: Open User Configuration** — not `settings.json`):

```json
{
  "servers": {
    "liongard": {
      "type": "http",
      "url": "https://<instance>.app.liongard.com/api/mcp",
      "headers": {
        "Authorization": "Bearer <accessKeyId>:<accessKeySecret>"
      }
    }
  }
}
```

VS Code uses the `servers` key (not `mcpServers`) and requires
`"chat.mcp.enabled": true` in settings. See
[`clients/vscode.md`](clients/vscode.md) for the full walkthrough.

## Codex, Gemini, Continue, OpenCode, Windsurf

Use the generic config generator first:

```bash
node scripts/liongard-mcp-config.js --client generic --print
```

Then adapt the generated server object to your harness. The required values are
the same:

```json
{
  "name": "liongard",
  "type": "http",
  "url": "https://<instance>.app.liongard.com/api/mcp",
  "headers": {
    "Authorization": "Bearer <accessKeyId>:<accessKeySecret>"
  }
}
```

Do not assume Claude Code skills load in these harnesses. Use the Markdown
files in `plugins/liongard/skills` as prompt/workflow guidance when needed.

## Copilot Studio / Stateless Clients

Liongard supports authenticated stateless `POST /api/mcp` for JSON-RPC methods
such as `tools/list` and `tools/call`.

Minimum `tools/list` request:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

Send it as an HTTP `POST` with:

```http
Content-Type: application/json
Accept: application/json,text/event-stream
Authorization: Bearer <accessKeyId>:<accessKeySecret>
```

This path is for advanced gateway builders. Prompt catalogs and skill loading
depend on the client.

## Custom Client Smoke Flow

1. `initialize` with protocol version `2025-11-25`.
2. Store `Mcp-Session-Id` from the response.
3. Call `tools/list`.
4. Call:

   ```json
   {
     "name": "liongard_environment",
     "arguments": {
       "operation": "COUNT"
     }
   }
   ```

5. Treat any `401`, `403`, or `-32002` response as setup failure.

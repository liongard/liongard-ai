# VS Code / GitHub Copilot

VS Code (with GitHub Copilot Chat) supports MCP servers natively. Servers are
configured in a dedicated `mcp.json` file — **not** in `settings.json`.

## Prerequisites

- A recent VS Code with **GitHub Copilot Chat** installed and signed in.
- MCP enabled in settings: `"chat.mcp.enabled": true` (Settings → search
  "chat mcp"). Without this, VS Code silently ignores your `mcp.json`.
- Your Liongard instance hostname, for example `acme.app.liongard.com`.
- A Liongard Access Token from **AI Preferences -> Access Tokens**.

---

## Option 1 — user-level `mcp.json`

Open the command palette (`Cmd/Ctrl+Shift+P`) and pick
**MCP: Open User Configuration**. Add:

```json
{
  "servers": {
    "liongard": {
      "type": "http",
      "url": "https://<your-instance>.app.liongard.com/api/mcp",
      "headers": {
        "Authorization": "Bearer <accessKeyId>:<accessKeySecret>"
      }
    }
  }
}
```

> VS Code uses the `servers` key, not `mcpServers` — configs copied from
> Claude Desktop or Cursor will be silently ignored.

Generate this config (with your real host and token filled in) via:

```bash
node scripts/liongard-mcp-config.js --client vscode --print
```

Or write it directly to your user-level `mcp.json`:

```bash
node scripts/liongard-mcp-config.js --client vscode --write
```

Save and reload the window (`Cmd/Ctrl+Shift+P` → **Developer: Reload Window**).

---

## Option 2 — workspace `.vscode/mcp.json`

Drop the same block into `.vscode/mcp.json` in your project to share the
server definition with your team. Use an environment variable for the token so
you don't commit secrets:

```json
{
  "servers": {
    "liongard": {
      "type": "http",
      "url": "https://<your-instance>.app.liongard.com/api/mcp",
      "headers": {
        "Authorization": "Bearer ${env:LIONGARD_MCP_TOKEN}"
      }
    }
  }
}
```

Each contributor exports `LIONGARD_MCP_TOKEN` (`<accessKeyId>:<accessKeySecret>`)
in their own shell. If you keep a real token in `.vscode/mcp.json` instead,
add that file to `.gitignore`.

---

## Verifying the install

Open Copilot Chat (agent mode) and ask:

```text
Using the Liongard MCP, list my environments.
```

If Copilot says it doesn't have the Liongard tools available, reload the
window and check the MCP servers list (`Cmd/Ctrl+Shift+P` →
**MCP: List Servers**) to confirm the server is connected.

---

## Skills

VS Code Copilot doesn't read Anthropic-format skill files. You have two
options:

1. Keep this repo cloned alongside your project and open the relevant
   [`../plugins/liongard/skills/*/SKILL.md`](../../plugins/liongard/skills) file when you need
   the workflow. Paste the relevant steps into Copilot Chat.
2. Rewrite the skill as a VS Code Copilot **prompt file** and save it to
   `.github/prompts/` (or the prompt-file location your version recommends).

---

## Troubleshooting

- **The server never appears.** Confirm `"chat.mcp.enabled": true` is set —
  this is the most common cause of MCP configs being silently ignored.
- **Copilot says the MCP server isn't available.** Reload the VS Code window
  and open the Copilot output channel to see MCP errors.
- **Auth fails.** Verify the `Authorization` header exactly matches
  `Bearer <accessKeyId>:<accessKeySecret>` (no extra whitespace, no missing
  colon).
- **Proxy / VPN.** If your VS Code is behind a corporate proxy, make sure
  `https://<your-instance>.app.liongard.com/api/mcp` is reachable from the
  Copilot process (not just your browser).

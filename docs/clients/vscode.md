# VS Code / GitHub Copilot

Recent versions of VS Code (with GitHub Copilot Chat) support MCP servers.
The exact UI is still evolving, so this guide sticks to the stable JSON
config path.

## Prerequisites

- VS Code with **GitHub Copilot Chat** installed and signed in.
- A Copilot subscription that includes MCP (check your VS Code Copilot
  settings — look for an **MCP servers** panel).
- Your Liongard instance hostname, for example `acme.app.liongard.com`.
- A Liongard Access Token from **AI Preferences -> Access Tokens**.

---

## Option 1 — user `settings.json`

Open the command palette (`Cmd/Ctrl+Shift+P`) and pick
**Preferences: Open User Settings (JSON)**. Add:

```json
{
  "chat.mcp.servers": {
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

Save and reload the window (`Cmd/Ctrl+Shift+P` → **Developer: Reload Window**).

> The exact settings key may shift as Copilot's MCP support matures. If the
> key above isn't recognized in your version, check VS Code's MCP settings
> panel for a direct editor.

---

## Option 2 — workspace `.vscode/settings.json`

Drop the same block into your project's `.vscode/settings.json` to share the
server with your team. Use an environment variable for the token so you don't
commit secrets:

```json
{
  "chat.mcp.servers": {
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

Each contributor exports `LIONGARD_MCP_TOKEN` in their own shell. Generate a
snippet with:

```bash
node scripts/liongard-mcp-config.js --client vscode --print
```

---

## Verifying the install

Open Copilot Chat and ask:

```text
Using the Liongard MCP, list my environments.
```

If Copilot says it doesn't have the Liongard tools available, reload the
window and check the MCP panel in VS Code settings to confirm the server is
connected.

---

## Skills

VS Code Copilot doesn't read Anthropic-format skill files. You have two
options:

1. Keep this repo cloned alongside your project and open the relevant
   [`../.claude/skills/*/SKILL.md`](../../.claude/skills) file when you need
   the workflow. Paste the relevant steps into Copilot Chat.
2. Rewrite the skill as a VS Code Copilot **prompt file** (if your version
   supports it) and save to `.github/prompts/` or the Copilot-recommended
   path for prompts.

---

## Troubleshooting

- **Copilot says the MCP server isn't available.** Reload the VS Code window
  and open the Copilot output channel to see MCP errors.
- **Auth fails.** Verify the `Authorization` header exactly matches
  `Bearer <accessKeyId>:<accessKeySecret>` (no extra whitespace, no missing
  colon).
- **Proxy / VPN.** If your VS Code is behind a corporate proxy, make sure
  `https://<your-instance>.app.liongard.com/api/mcp` is reachable from the
  Copilot process (not just your browser).

# Claude Desktop

[Claude Desktop](https://claude.ai/download) is Anthropic's desktop chat app.
It supports MCP via a JSON config file.

## Prerequisites

- Claude Desktop installed and signed in.
- Your Liongard instance hostname, for example `acme.app.liongard.com`.
- A Liongard Access Token from **AI Preferences -> Access Tokens**.

---

## Quick install

Run the helper script from this repo — it appends the Liongard entry to your
existing `claude_desktop_config.json`:

```bash
node scripts/liongard-mcp-config.js --client claude-desktop --print
./scripts/install-claude-desktop.sh
```

The script will prompt for your instance URL and token, then write the
config after creating a backup. Fully quit and relaunch Claude Desktop.

---

## Manual install

Locate your config file:

| OS | Path |
| --- | --- |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

Create the file if it doesn't exist. Add a `liongard` entry under
`mcpServers`:

```json
{
  "mcpServers": {
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

Fully quit and relaunch Claude Desktop. In a new chat, type `/` — you should
see Liongard prompts available as `/mcp__liongard__<prompt-name>`.

---

## Verifying the install

In a new chat:

1. Type `/` and look for `mcp__liongard__*` prompts — if they show up, the
   server connected successfully.
2. Ask:

   ```text
   List my Liongard environments.
   ```

---

## Skills

Claude Desktop reads skill files from the **workspace** you open. To use the
skills shipped in this repo, open this repo folder as your workspace (or copy
`.claude/skills/` into your own workspace). See [`../skills.md`](../skills.md).

---

## Troubleshooting

- **No MCP tools show up.** Fully quit Claude Desktop (from the menu bar — not
  just close the window) and relaunch. Check the app's logs:
  - macOS: `~/Library/Logs/Claude/mcp*.log`
  - Windows: `%APPDATA%\Claude\logs\mcp*.log`
- **`401 Unauthorized` in logs.** The token is wrong or expired. Recreate it in
  Liongard → AI Preferences → Access Tokens and update the config.
- **Config file not loaded.** Verify JSON is valid
  (`python -m json.tool < claude_desktop_config.json`) and the file path
  matches your OS.

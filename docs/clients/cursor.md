# Cursor

[Cursor](https://cursor.com) is an AI-first code editor with first-class MCP
support.

## Prerequisites

- Cursor installed (any recent version with MCP support).
- Your Liongard instance hostname, for example `acme.app.liongard.com`.
- A Liongard Access Token from **AI Preferences -> Access Tokens**.

---

## Quick install

Run the helper script, or print the config first:

```bash
node scripts/liongard-mcp-config.js --client cursor --print
./scripts/install-cursor.sh
```

The script will prompt for your instance URL and token, then write the
Liongard entry into `~/.cursor/mcp.json` after creating a backup. Open
Cursor's **Settings → MCP** panel and confirm the server shows as connected.

---

## Manual install — user scope (recommended)

User-scope MCP config lives at `~/.cursor/mcp.json`. Create the file if it
doesn't exist:

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

Restart Cursor (or reconnect the server in **Settings → MCP**).

---

## Manual install — project scope

Drop a `.cursor/mcp.json` file at the root of your project:

```json
{
  "mcpServers": {
    "liongard": {
      "type": "http",
      "url": "https://<your-instance>.app.liongard.com/api/mcp",
      "headers": {
        "Authorization": "Bearer ${LIONGARD_MCP_TOKEN}"
      }
    }
  }
}
```

Commit this file if you want the entire team to pick up the Liongard server
automatically. **Do not commit the actual token**; every contributor should
export `LIONGARD_MCP_TOKEN` in their own shell.

---

## Verifying the install

1. Open **Settings → MCP**. The `liongard` entry should show as connected.
2. In a new Cursor chat, type:

   ```text
   List my Liongard environments.
   ```

---

## Skills (optional)

This repo ships Anthropic-format skill files under [`.claude/skills/`](../../.claude/skills).
Cursor uses a slightly different convention (`.cursor/skills/`). To use the
Liongard skills in Cursor, copy the directories:

```bash
mkdir -p ~/.cursor/skills
cp -R .claude/skills/liongard-* ~/.cursor/skills/
```

Or symlink for easy updates:

```bash
mkdir -p ~/.cursor/skills
for skill in .claude/skills/liongard-*; do
  ln -sfn "$(pwd)/$skill" "$HOME/.cursor/skills/$(basename "$skill")"
done
```

---

## Troubleshooting

- **`-32002 Server not initialized`** — Cursor's MCP client returns this
  until the server finishes startup. Open **Settings → MCP**, reconnect the
  server, then retry.
- **Server stays red in Settings → MCP.** Check the server logs there.
  Common causes: wrong URL, wrong token format, network/proxy blocking the
  host.
- **Tools show up but every call errors.** Your token's environment scope
  may not include the environment you're asking about. Recreate the token
  with a broader scope, or be explicit about `environmentId` in your prompts.

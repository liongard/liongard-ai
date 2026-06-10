# Claude Code

[Claude Code](https://claude.com/product/claude-code) is the primary supported
path for this repo. Use Bearer Access Token auth unless you have separately
verified OAuth with your Claude Code version.

## Prerequisites

- Claude Code installed. One-liner:

  ```bash
  curl -fsSL https://claude.ai/install.sh | sh
  ```

- A Liongard user with **Manage AI** permission so you can create an Access Token.
- Your Liongard instance hostname, for example `acme.app.liongard.com`.

---

## Option 1 — install the plugin (recommended)

```text
/plugin marketplace add liongard/liongard-ai
/plugin install liongard
```

Restart Claude Code if prompted, then run:

```text
/liongard-setup
```

## Option 2 — run from a clone

1. Clone this repo and `cd` into it:

   ```bash
   git clone https://github.com/liongard/liongard-ai.git
   cd liongard-ai
   ```

2. Start Claude Code from the repo root:

   ```bash
   claude
   ```

3. Run:

   ```text
   /liongard-setup
   ```

   Claude will ask you a few questions and register the server for you. When
   it's done, run `/liongard-status` to confirm.

---

## Option 3 — add the server manually

Create an Access Token in **AI Preferences -> Access Tokens**. Configure the
combined token as `<accessKeyId>:<accessKeySecret>`:

```bash
claude mcp add --transport http liongard \
  "https://<your-instance>.app.liongard.com/api/mcp" \
  --header "Authorization: Bearer <accessKeyId>:<accessKeySecret>"
```

OAuth is experimental/client-dependent. Do not use it as the default customer
setup path.

---

## Scopes

Claude Code supports three MCP scopes:

| Scope | Flag | Where it lives | Who sees it |
| --- | --- | --- | --- |
| Local (default) | `--scope local` | `~/.claude.json` under the project path | Only you, this project only |
| Project | `--scope project` | `.mcp.json` at the project root | Everyone on the team (commit to git) |
| User | `--scope user` | `~/.claude.json` | Only you, all your projects |

Pick **user** for personal laptops that connect to a single Liongard tenant:

```bash
claude mcp add --scope user --transport http liongard \
  "https://<your-instance>.app.liongard.com/api/mcp" \
  --header "Authorization: Bearer <accessKeyId>:<accessKeySecret>"
```

Pick **project** for a shared repo where every contributor should see the
same Liongard MCP. Commit `.mcp.json`, but **do not** commit the token —
use a placeholder and have each contributor run `/liongard-setup` locally.

---

## Verifying the install

```bash
claude mcp list
claude mcp get liongard
```

In-session:

```text
/mcp
/liongard-status
```

Then ask a sanity-check question:

```text
List my Liongard environments.
```

---

## Removing

```bash
claude mcp remove liongard
```

Or, if you used project scope, edit `.mcp.json` and delete the `liongard`
entry.

---

## `.mcp.json` example (project scope)

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

Using `${LIONGARD_MCP_TOKEN}` lets each contributor export their own token
without the secret ending up in git.

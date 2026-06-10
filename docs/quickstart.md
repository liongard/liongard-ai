# Quickstart

This is the short path for connecting any MCP-capable agent to Liongard.

## 1. Get Your Instance Hostname

Use the hostname you log into:

```text
acme.app.liongard.com
```

The MCP endpoint is:

```text
https://acme.app.liongard.com/api/mcp
```

If a guide asks for only the instance name, use `acme`.

## 2. Create A Liongard Access Token

1. Open Liongard.
2. Go to **AI Preferences -> Access Tokens**.
3. Create a credential with a label such as `claude-code-laptop`.
4. Choose an expiration and environment scope.
5. Copy the generated `accessKeyId` and `accessKeySecret`.
6. Configure clients with:

   ```text
   Authorization: Bearer <accessKeyId>:<accessKeySecret>
   ```

The secret is shown once. Revoke and recreate it if you lose it.

## 3. Configure Your Agent

For Claude Code:

```bash
claude mcp add --scope user --transport http liongard \
  "https://acme.app.liongard.com/api/mcp" \
  --header "Authorization: Bearer <accessKeyId>:<accessKeySecret>"
```

For JSON-config clients:

```bash
node scripts/liongard-mcp-config.js --client cursor --print
node scripts/liongard-mcp-config.js --client claude-desktop --print
node scripts/liongard-mcp-config.js --client vscode --print
node scripts/liongard-mcp-config.js --client generic --print
```

Client guides:

- [Claude Code](clients/claude-code.md)
- [Claude Desktop](clients/claude-desktop.md)
- [Cursor](clients/cursor.md)
- [VS Code / GitHub Copilot](clients/vscode.md)
- [Harness matrix](harnesses.md)

## 4. Verify

Ask:

```text
List my Liongard environments.
```

Or run the smoke test:

```bash
node scripts/liongard-mcp-smoke-test.js \
  --instance acme.app.liongard.com \
  --token "$LIONGARD_MCP_TOKEN"
```

## 5. Try Useful Prompts

```text
What alerts are open in <environment name>?
Show me MFA coverage across all environments.
Which agents are offline?
What systems failed their last inspection?
Investigate alert <alert id>.
```

More examples: [`../examples/prompts.md`](../examples/prompts.md).

## OAuth Note

OAuth discovery endpoints exist for compatibility, but Bearer Access Tokens are
the supported setup path. Treat OAuth as experimental unless your exact client
version has been verified.

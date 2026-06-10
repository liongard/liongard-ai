# Authentication

Bearer token auth is the stable path for all supported harnesses.

```http
Authorization: Bearer <accessKeyId>:<accessKeySecret>
```

The MCP server never sees your Liongard UI password. Credentials are scoped and
can be revoked from the Liongard UI.

## Create An Access Token

1. Log in to Liongard as a user with **Manage AI** permission.
2. Open **AI Preferences -> Access Tokens**.
3. Click **Create Credential**.
4. Choose a label, expiration, and optional environment or environment-group
   scope.
5. Copy both values shown once:
   - `accessKeyId`, usually shaped like `lg_mcp_<id>`.
   - `accessKeySecret`.
6. Combine them with a colon when configuring MCP:

   ```text
   <accessKeyId>:<accessKeySecret>
   ```

Treat the combined token like a password.

## Configure A Client

### Claude Code

```bash
claude mcp add --scope user --transport http liongard \
  "https://<instance>.app.liongard.com/api/mcp" \
  --header "Authorization: Bearer <accessKeyId>:<accessKeySecret>"
```

### JSON Config Clients

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

Use `node scripts/liongard-mcp-config.js --client <client>` to generate the
right shape for Cursor, Claude Desktop, VS Code, and generic clients.

## Token Scopes

Access Tokens can be scoped to all visible environments or an explicit list of
environments and environment groups. The MCP server enforces scope on every
tool and prompt call.

Use narrow scopes for automation tied to one customer. Use broader scopes only
for workflows that genuinely need tenant-wide visibility.

## OAuth Status

Liongard exposes minimal discovery endpoints for client compatibility, but
Bearer Access Tokens are the supported setup path today. OAuth behavior varies
by MCP client and should be treated as experimental until it has been verified
with your exact harness version.

Do not document or depend on OAuth as the default path for customers.

## What The Server Sees

Successful auth populates server-side context including:

- `serviceProviderID`
- `accessKeyID`
- `userID`
- `tokenType`
- `environmentIds` when scoped
- `correlationID`

If a token is revoked or expires mid-session, the next request returns `401`.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `401 Unauthorized` | Bad, expired, revoked, or malformed token | Recreate the Access Token and reconfigure the client. |
| `403 Forbidden` | The tenant, credential, or token scope cannot access that capability | Ask an admin to confirm access and token scope. |
| `-32002 Server not initialized` | Client has not completed MCP initialization | Reconnect/restart the MCP server in the client. |
| No expected environment data | Token scope is too narrow | Recreate with the right environment or group scope. |

More tips: [`troubleshooting.md`](troubleshooting.md).

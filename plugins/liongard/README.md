# Liongard Claude Code Plugin

Connect Claude Code to the hosted Liongard MCP server and load Liongard-specific
skills for common MSP workflows.

## Install

```text
/plugin marketplace add liongard/liongard-ai
/plugin install liongard
```

Then run:

```text
/liongard-setup
```

## Configure

1. In Liongard, open **AI Preferences -> Access Tokens**.
2. Create a credential.
3. Copy `accessKeyId` and `accessKeySecret`.
4. Use the combined token as:

   ```text
   <accessKeyId>:<accessKeySecret>
   ```

The MCP URL is:

```text
https://<instance>.app.liongard.com/api/mcp
```

## Commands

- `/liongard-setup` — guided Claude Code setup using Bearer Access Token auth.
- `/liongard-setup-api-key` — non-interactive Bearer setup path.
- `/liongard-status` — registration and safe environment-count check.
- `/liongard-doctor` — step-by-step troubleshooting.

OAuth setup is intentionally not the default path. Use Bearer Access Tokens
unless your exact client version has been verified with OAuth.

## Skills

- `liongard-mcp` — baseline tool and prompt usage.
- `liongard-first-five-minutes` — first-run checklist for a newly connected tenant.
- `liongard-investigate-alert` — alert triage workflow.
- `liongard-environment-health` — daily customer health check.
- `liongard-compliance-audit` — cyber-risk/compliance coverage review.

## Verify

Ask:

```text
List my Liongard environments.
```

For a deeper check, run `/liongard-doctor`.

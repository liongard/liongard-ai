# Capability Status

This page is the user-facing snapshot of the current Liongard MCP surface. The
live tenant remains the source of truth: call `tools/list` and `prompts/list`
after connecting.

## Supported Today

| Capability | Status | Notes |
| --- | --- | --- |
| Streamable HTTP MCP | Supported | `POST /api/mcp`, `GET /api/mcp`, `DELETE /api/mcp`. |
| Bearer Access Token auth | Supported | `Authorization: Bearer <accessKeyId>:<accessKeySecret>`. |
| Stateful sessions | Supported | Standard `initialize` plus `Mcp-Session-Id`. |
| Stateless authenticated POST | Supported | Useful for Copilot Studio-style clients. |
| Native `liongard_*` tools | Supported | See [`tools-reference.md`](tools-reference.md). |
| Prompt catalog | Supported | Canonical kebab-case prompt names only. |
| Tenant external MCP tools | Supported when configured | External tools can appear in `tools/list`. |
| Compact tools mode | Supported | Client opt-in via `experimental.liongard.compactTools`. |
| `responseFormat: "toon"` | Tool-dependent | Available only where the live schema advertises it. |

## Experimental / Client-Dependent

| Capability | Status | Notes |
| --- | --- | --- |
| OAuth login | Experimental | Discovery endpoints exist, but Bearer auth is the supported setup path. |
| Skills outside Claude/Cursor | Client-dependent | Treat skills as guidance files unless the harness loads them natively. |
| VS Code/Copilot MCP settings | Client-dependent | Config keys can change between Copilot releases. |

## Not A Data Source

| Capability | Status | Notes |
| --- | --- | --- |
| `resources/list` | Placeholder | Returns an empty list today. Use tools and prompts for Liongard data. |
| Legacy prompt names | Unsupported | Use kebab-case names such as `investigate-alert`. |
| Legacy standalone systems tool | Unsupported | Use `liongard_launchpoint` for systems. |

## Release Checklist

Before publishing docs or plugin changes:

1. Connect to a current Liongard test tenant.
2. Compare this page with live `tools/list` and `prompts/list` responses.
3. Run `node scripts/validate-repo.js`.
4. Run `node scripts/liongard-mcp-smoke-test.js` against a test tenant.

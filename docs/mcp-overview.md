# Liongard MCP Overview

The **Liongard MCP** is hosted by your Liongard tenant. It gives MCP-compatible
AI assistants structured, scoped access to Liongard data: environments, agents,
alerts, systems, inventory, metrics, detections, timelines, reports, and
grounded natural-language query.

## Endpoints

Use your normal Liongard hostname:

```text
https://<instance>.app.liongard.com/api/mcp
```

Current surfaces:

- `POST /api/mcp` — primary MCP JSON-RPC endpoint using streamable HTTP.
- `GET /api/mcp` — SSE notifications and resumable event replay.
- `DELETE /api/mcp` — session termination.

Compatibility discovery routes exist at the instance root and under `/api/mcp`
for clients that probe OAuth/OIDC metadata. They are intentionally minimal; use
Bearer token auth as the stable setup path unless your client has been verified
with Liongard OAuth.

## Transport

Liongard implements streamable HTTP MCP. JSON-RPC responses return on the
requesting `POST`; SSE is reserved for `GET`. Stateful clients should call
`initialize`, store the returned `Mcp-Session-Id`, and send it on later
requests.

Authenticated stateless clients can send `tools/list` or `tools/call` directly
to `POST /api/mcp` without a prior session. The server creates a short-lived
already-initialized session from the Bearer token. `GET` and `DELETE` still
require an existing session.

## Authentication

Send:

```http
Authorization: Bearer <accessKeyId>:<accessKeySecret>
```

For user setup, create the credential in **AI Preferences -> Access Tokens** and
combine the two values with a colon. Agent and vendor tokens also exist for
internal and partner flows, but most human users should use user Access Tokens.

See [`authentication.md`](authentication.md).

## Native Tool Surface

`/api/mcp` lists native Liongard tools and may merge tenant-configured external
MCP tools. Native tools currently include:

- `liongard_environment`
- `liongard_agents`
- `liongard_alert`
- `liongard_detection`
- `liongard_launchpoint`
- `liongard_asset`
- `liongard_metric`
- `liongard_cyber_risk_dashboard`
- `liongard_timeline`
- `liongard_report`
- `liongard_query`
- `liongard_navigate`

Most native tools are read-only and support paginated `LIST`/`GET` style
operations. Tools that expose `responseFormat` support `json` and `toon`; use
`toon` only when the client benefits from compact output.

Full reference: [`tools-reference.md`](tools-reference.md).

## Compact Mode

Gateways that want a tiny `tools/list` response can opt in during `initialize`:

```json
{
  "capabilities": {
    "experimental": {
      "liongard": {
        "compactTools": true
      }
    }
  }
}
```

In compact mode, `tools/list` returns only `liongard_navigate`. Direct
`tools/call` dispatch to the native tool names still works.

## Prompt Catalog

`prompts/list` exposes reusable tenant-scoped prompts. Canonical names are
kebab-case only; legacy names such as `investigate_alert`, `system-overview`,
and `change-report` are not supported.

See [`prompts-reference.md`](prompts-reference.md).

## Resources And Other Methods

Core MCP methods are wired for initialization, tools, prompts, ping, logging,
roots, and resource subscribe/unsubscribe. `resources/list` currently returns
an empty list; do not rely on MCP resources for Liongard data access. Use tools
and prompts instead.

## Scoping And Access

Every call is scoped by the token. The server checks:

1. The credential belongs to a valid service provider.
2. Requested environments are visible to the credential.
3. The tenant and credential are allowed to use the requested MCP capability.

Scoped tokens cannot access data outside their allow-list.

## Billing And Quotas

Credit behavior is activity-based:

- Chat turns and `liongard_query` calls are billable AI requests.
- Direct tool calls such as `liongard_environment LIST` are telemetry and rate
  limited, but not directly billed as credits.

See your Liongard admin console for current entitlement and quota details.

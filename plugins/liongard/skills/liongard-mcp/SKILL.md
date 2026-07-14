---
name: liongard-mcp
description: Use the Liongard MCP server to answer questions about MSP environments, alerts, detections, systems, launchpoints, assets, metrics, cyber-risk posture, and change history. Load whenever the user mentions Liongard, their customers/environments, actionable alerts, launchpoints, inspectors, dataprints, MFA/EDR/encryption coverage, compliance, or cyber risk.
---

# Liongard MCP — baseline usage

This skill teaches you how to use the Liongard MCP server effectively. The
stable setup path is Bearer Access Token auth against
`https://<instance>.app.liongard.com/api/mcp`.

## When to load

Load this skill when the user:

- Mentions "Liongard" or a known Liongard concept (environment, launchpoint,
  inspector, dataprint, actionable alert, cyber-risk dashboard, MFA / EDR /
  encryption / firewall / TLS coverage).
- Asks about their managed customers (MSPs refer to customers as
  "environments" in Liongard).
- Asks about failing inspections, recent changes, or security posture
  across their tenant.

If the user's question has nothing to do with Liongard, don't use this skill.

## Core tools

All tool names start with `liongard_`. The catalog:

| Tool | Purpose |
| --- | --- |
| `liongard_environment` | List / get environments (customers). |
| `liongard_agents` | List / get / count installed Liongard agents. |
| `liongard_alert` | Query actionable alerts. |
| `liongard_detection` | Query change detections. |
| `liongard_launchpoint` | Unified launchpoint + system view. |
| `liongard_device` / `liongard_identity` / `liongard_domain` | Reconciled device / identity / domain inventory (LIST + GET + COUNT). |
| `liongard_metric` | Evaluate metric values. |
| `liongard_cyber_risk_dashboard` | MFA / EDR / encryption / firewall / TLS/SSL coverage rollups. |
| `liongard_timeline` | Dataprint history per system. |
| `liongard_report` | Generate reports. |
| `liongard_query` | High-level grounded Q&A across tools. |
| `liongard_navigate` | Tool catalog navigator (mostly for gateway clients). |

## Prompt catalog

If the user's question maps cleanly to one of these prompts, **prefer the
prompt over re-implementing it by hand**:

- `investigate-alert alertId=<id>`
- `analyze-environment environmentId=<id>`
- `analyze-system systemId=<id>`
- `security-posture environmentId=<id>`
- `compliance-check [environmentId=<id>]`
- `capacity-planning [environmentId=<id>]`
- `health-check [environmentId=<id>]`
- `failing-inspections [environmentId=<id>]`
- `recent-changes [environmentId=<id>, days=<n>]`
- `onboard-environment environmentId=<id>`
- `compare-environments environmentId1=<id> environmentId2=<id>`
- `metric-analysis environmentId=<id>|systemId=<id>`
- `metric-time-series systemId=<id> startDate=<...> endDate=<...> metricId|jmesPathQuery=<...>`
- `alert-trends environmentId=<id>|systemId=<id> [days=<n>]`
- `troubleshoot issue=<free text> [environmentId, systemId]`

## Workflow rules

### 1. Resolve names to IDs first

If the user mentions an environment, system, or alert by name or label,
call `liongard_environment` / `liongard_launchpoint` / `liongard_alert`
with a `searchMode: "keyword"` filter to resolve the name to an ID. Do
this **before** any detail query — it keeps everything scope-consistent
and avoids cross-environment drift.

### 2. Honor pagination

Most list tools return a `Pagination` block with `HasMoreRows`,
`TotalPages`, `CurrentPage`. Rules:

- If the user asked for an **exact count** ("how many", "total"), keep
  paging until exhausted, or use `COUNT` on `liongard_device` / `liongard_identity` /
  `liongard_domain` (with `includeStatusCounts: true`) when available.
- If the user asked for a **list** without a count, show up to ~25 items
  and tell them if more are available.
- Never extrapolate a sample page to a total. If you only see page 1, say
  "showing X of Y" — never invent a rounded total.

### 3. Prefer aggregation when appropriate

For MFA/EDR/identity counts, use `liongard_identity` / `liongard_device` `COUNT`:

```json
{
  "operation": "COUNT",
  "environmentId": 1234,
  "mfaStatus": "NO",
  "enabled": true,
  "includeStatusCounts": true
}
```

This avoids paging through thousands of rows for a bucket count.

### 4. Use the right tool for each job

| If the user asks… | Use |
| --- | --- |
| "What alerts are open?" | `liongard_alert LIST` filtered by `Status = "Open"` |
| "Which agents are offline/suspended?" | `liongard_agents COUNT` then `LIST` for examples |
| "What changed recently?" | `liongard_detection LIST` or the `recent-changes` prompt |
| "Overview of system X" | `liongard_launchpoint GET_OVERVIEW` by `systemId` |
| "What kinds of systems are here?" | `liongard_launchpoint LIST_TYPES` |
| "Is MFA on everywhere?" | `liongard_cyber_risk_dashboard` or `compliance-check` prompt |
| "Show history for this system" | `liongard_timeline LIST` (use `systemDetailID` to fetch dataprints) |

### 5. Scope respectfully

- Never invent an `environmentId` that the user didn't mention or that a
  previous tool call didn't return.
- If the token is scoped to a subset of environments, accept that a tool
  call may return fewer results — don't retry with broader scope.
- When the user's question is broad ("across all environments"), prefer
  prompts and tools that aggregate tenant-wide (`compliance-check`,
  `liongard_cyber_risk_dashboard`) over fanning out per-environment.

### 6. Keep output tight

Lead with the direct answer. Supporting evidence (counts, top offenders,
quotes from detection bodies) goes below. For long lists, use tables with
the most useful columns only.

## Failure handling

- **`401 Unauthorized`** — tell the user their MCP token may be revoked /
  expired and suggest `/liongard-setup` in Claude Code.
- **`403 Forbidden`** on a specific tool — tenant is missing a feature
  flag; escalate.
- **`-32002 Server not initialized`** — MCP server is still starting; wait
  a few seconds and retry.
- **Tool returned no results but you expect some** — recheck token scope
  and try with `searchMode: "keyword"` for fuzzy matches.
- **`liongard_query` returned the generic "unable to retrieve dataprint
  details" answer** — rephrase with specific system / environment, or fall
  back to manual tool orchestration.

## Don't

- Don't make up tool names that don't exist. The tools above are the
  complete native surface.
- Don't retry a failed call with a larger `pageSize` hoping for better
  luck — address the root cause.
- Don't expose raw tool output verbatim when a summarized answer is more
  useful. Tool output is there to ground your answer, not be the answer.
- Don't leak tokens into tool arguments or logs.

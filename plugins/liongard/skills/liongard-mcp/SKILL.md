---
name: liongard-mcp
description: Use when a user asks about Liongard environments, agents, alerts, inspections, launchpoints, systems, inventory, metrics, cyber-risk posture, detections, reports, or dataprint history.
---

# Liongard MCP

Use the hosted Liongard MCP server. The stable endpoint is
`https://<instance>.app.liongard.com/api/mcp`; Bearer Access Token auth is the
supported setup path.

## Native Tools

| Tool | Use for |
| --- | --- |
| `liongard_environment` | Environment/customer lookup and counts. |
| `liongard_agents` | Installed agent inventory, platform, status, and ownership. |
| `liongard_alert` | Actionable alerts and alert counts. |
| `liongard_detection` | Change detections and recent drift. |
| `liongard_launchpoint` | Launchpoints and systems; use `LIST_TYPES` for system types. |
| `liongard_asset` | Identity and device inventory, including MFA/EDR/device attributes. |
| `liongard_metric` | Metric metadata and metric evaluation. |
| `liongard_cyber_risk_dashboard` | Broad cyber-risk posture and pillar coverage. |
| `liongard_timeline` | Per-system inspection history. |
| `liongard_report` | Saved and system reports. |
| `liongard_query` | Natural-language, multi-step, grounded Q&A. |
| `liongard_navigate` | Compact discovery for gateways. |

## Prompt Catalog

Prefer server prompts when they match the task:

- `investigate-alert`
- `analyze-environment`
- `analyze-system`
- `security-posture`
- `compliance-check`
- `capacity-planning`
- `health-check`
- `failing-inspections`
- `recent-changes`
- `compare-environments`
- `metric-analysis`
- `metric-time-series`
- `alert-trends`
- `troubleshoot`
- `onboard-environment`

Prompt names are kebab-case only.

## Rules

1. Resolve environment names to IDs first with `liongard_environment`.
2. Use `liongard_launchpoint` for systems; there is no standalone systems tool.
3. Use `liongard_agents` for installed agent questions.
4. Use `liongard_asset` for identity/device attribute questions.
5. Honor pagination. For exact totals, keep paging or use `COUNT`/aggregation.
6. Never extrapolate page 1 into a total. Say “showing X of Y” when partial.
7. Respect token scope. Do not retry with broader scope.
8. Keep answers concise and grounded in tool output.

## Common Failures

- `401` — token is bad, expired, or revoked.
- `403` — tenant access or token scope issue.
- `-32002` — client has not initialized the MCP server yet.
- Generic `liongard_query` fallback — retry with a specific environment/system or orchestrate direct tools.

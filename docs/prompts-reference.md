# Prompts reference

The Liongard MCP exposes a curated catalog of tenant-scoped **prompts** over
MCP `prompts/list`. Each prompt renders a single user-role text message that
an agent can run — the prompt loads the right Liongard data for you and hands
the model a clean instruction block.

Prompt names are **canonical kebab-case**. Legacy snake_case / camelCase names
are not supported; calling `investigate_alert` or `system_overview` will
return `Prompt not found`.

---

## Catalog

| Prompt | Purpose | Required args | Optional args |
| --- | --- | --- | --- |
| `analyze-environment` | Environment health, alerts, and recommendations | `environmentId` | — |
| `security-posture` | Security alerts + detections for an environment | `environmentId` | — |
| `metric-analysis` | Metric trend analysis | one of `environmentId` or `systemId` | the other |
| `investigate-alert` | Step-by-step alert investigation with fan-out | `alertId` | — |
| `analyze-system` | Deep system health analysis (status + alerts + metrics) | `systemId` | — |
| `troubleshoot` | Guided troubleshooting workflow for a described issue | `issue` | `environmentId`, `systemId` |
| `onboard-environment` | Environment onboarding checklist and next steps | `environmentId` | — |
| `compare-environments` | Side-by-side comparison of two environments | `environmentId1`, `environmentId2` | — |
| `alert-trends` | Current open-alert load | one of `environmentId` or `systemId` | the other, `days` |
| `compliance-check` | Cyber-risk coverage (MFA, EDR, encryption, firewall, TLS/SSL) | — | `environmentId` |
| `capacity-planning` | Resource usage grounded in evaluated metric values | — | `environmentId` |
| `metric-time-series` | Temporal metric analysis across a date range | `systemId`, `startDate`, `endDate`, one of `metricId` or `jmesPathQuery` | the other |
| `health-check` | Operator-facing health check (visibility, status, open alerts) | — | `environmentId` |
| `recent-changes` | Current change-detection snapshot | — | `environmentId`, `days` |
| `failing-inspections` | Launchpoint failure triage summary | — | `environmentId` |

---

## Calling a prompt

Most MCP clients surface prompts as slash commands. For example, in Claude
Code:

```text
/mcp__liongard__investigate-alert alertId=12345
/mcp__liongard__analyze-environment environmentId=678
/mcp__liongard__compliance-check
```

Under the hood, this calls `prompts/get` with the given arguments.

---

## Behavior notes

### Snapshot vs. time-windowed data

Some prompts take a `days` argument as **interpretive context** only; the
underlying data is the **current snapshot** of the tenant, not a pre-filtered
time window.

- `alert-trends`, `recent-changes` — `days` tells the model the time frame
  the user cares about, but the loaded alert/detection rows are the current
  open set, not a rolling window.

The rendered prompt makes this explicit so the model can correlate using
`createdOn` / `createdAt` fields on each row.

### Truncation envelope

Prompts that load paginated data (alerts, detections, launchpoints, metrics)
cap each list call at a fixed page size and surface a `Showing X of Y` line in
the rendered message. If you see "Showing 200 of 547", the model is seeing
the first 200 rows — ask a scoped follow-up if you need more.

### Partial failures

If a non-critical scoped data call fails (for example, an alert list fails
while the environment fetch succeeds), env/alert prompts log the failure as a
"Some sections failed to load" note and continue, rather than aborting. This
keeps prompts useful even when one part of the tenant is temporarily noisy.

### Scoping

Every prompt reconciles the caller's accessible environments from credentials
before loading data. A token scoped to one environment can't coax data from
another environment by passing a foreign `environmentId`.

---

## Writing your own "prompt-like" skill

Prompts are defined server-side. If you want a reusable workflow the server
doesn't ship, write a Skill in this repo instead — see [`skills.md`](skills.md).
A skill is essentially client-side: it teaches the agent a recipe that uses
the existing tools, without requiring a server change.

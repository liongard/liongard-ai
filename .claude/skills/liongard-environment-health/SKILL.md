---
name: liongard-environment-health
description: Daily health check for a Liongard environment. Use when the user asks to review an environment, get a status report, do a morning check, or see what needs attention. Pulls open-alert load, failing inspections, recent changes, and cyber-risk posture into a concise brief.
---

# Liongard — Environment health check

Use this skill when the user says something like:

- "Give me a morning health check on <environment>."
- "What needs attention in the <customer> environment?"
- "Review <environment> for me."
- "What's going on with <customer> today?"

## Prefer the built-in prompt

If the user wants a deep dive on one environment and you have its ID, call
the `analyze-environment` prompt first:

```text
prompts/get name=analyze-environment arguments={"environmentId": <id>}
```

You can also combine with `security-posture` or `health-check` for more
coverage. Fall back to manual orchestration only when the user wants a
specific slice.

## Manual workflow

### Step 1 — resolve the environment

If the user gave a name, resolve it via `liongard_environment LIST` with
`searchMode: "keyword"`. Confirm the ID you're using in your answer.

### Step 2 — open alerts

Call `liongard_alert LIST` with:

- `environmentId = <resolved id>`
- `Status = "Open"`
- `pageSize = 50`, sorted by `Severity` desc, then `CreatedOn` desc.

Capture:

- Total open count.
- Count per severity.
- Top 5 alerts by severity / age.

### Step 3 — failing inspections

Call `liongard_launchpoint LIST` with:

- `environmentId = <resolved id>`
- Filter or sort by status to isolate failing launchpoints.

Alternatively, call the `failing-inspections` prompt with the
`environmentId` for a canned summary.

Capture:

- Number of launchpoints in a failing state.
- Top 5 failing ones (system name + type + last error if available).

### Step 4 — recent changes

Call `liongard_detection LIST` with:

- `environmentId = <resolved id>`
- Last 24 hours (or whatever window the user implied).

Capture:

- Total detections in window.
- Top 5 notable detections (title / affected system).

### Step 5 — cyber-risk posture

Call `liongard_cyber_risk_dashboard` for the five pillars (MFA, EDR,
encryption, firewall, TLS/SSL) scoped to this environment. Capture
coverage percentages.

Alternatively, call the `compliance-check` prompt with the environment ID.

### Step 6 — synthesize

Produce a report with these sections, in this order:

1. **Environment** — name, ID, number of systems.
2. **Open alerts** — total + severity breakdown + top 5 table.
3. **Failing inspections** — count + top 5 table.
4. **Recent changes (24h)** — count + top 5 list.
5. **Cyber-risk posture** — per-pillar percentage.
6. **Top 3 things that need attention** — distilled from the above, with
   the reason and the suggested next action for each.

## Rules

- Honor the user's time window if they specified one ("last week", "since
  Monday"). Otherwise default to 24 hours for detections and "current
  snapshot" for alerts.
- Be explicit about pagination: if the alert or detection count is
  truncated, say so ("showing top 5 of 47 open alerts").
- Never invent a severity or status that wasn't in the tool output.
- If a step fails, surface it as "unavailable" in the corresponding
  section and continue with the rest — don't block the whole report on
  one failure.
- The final **Top 3 things that need attention** should be concrete and
  ranked; avoid vague advice like "review alerts".

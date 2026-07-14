---
name: liongard-investigate-alert
description: Investigate a Liongard actionable alert end-to-end. Use when the user asks to triage, investigate, diagnose, or explain a specific alert (usually identified by alert ID or a short description). Pulls related launchpoint, recent detections on the same system, and other open alerts, then proposes remediation.
---

# Liongard — Investigate alert

Use this skill when the user says something like:

- "Investigate alert 12345."
- "What's going on with this alert?"
- "Triage the MFA alert that fired this morning."
- "Why did we get this alert?"

If the user gives an alert **ID**, use it directly. Otherwise, resolve the
alert first from the context they gave (system name, time, keyword).

## Prefer the built-in prompt

The Liongard MCP ships an `investigate-alert` prompt that already does
most of this fan-out. **If the user gave an alert ID, call that prompt
first** and build on its output rather than duplicating work:

```text
prompts/get name=investigate-alert arguments={"alertId": <id>}
```

Only fall back to manual orchestration if the prompt is unavailable or
returns `Prompt not found`.

## Manual workflow (fallback)

### Step 1 — resolve the alert

Call `liongard_alert GET` with the ID. Capture:

- `AlertID`
- `EnvironmentID`
- `SystemID`
- `LaunchpointID`
- `Severity`
- `Status`
- `CreatedOn`
- `Title` / `Body` (or equivalent fields)

If the user gave no ID:

- Ask `liongard_alert LIST` filtered by their hint (system name,
  keyword, `Status = "Open"`, recent time window).
- Show up to 5 candidates and ask them to confirm.

### Step 2 — launchpoint / system context

Call `liongard_launchpoint GET_OVERVIEW` for the system the alert fired on.
Capture the system's type, category, current status, and last inspection
result.

### Step 3 — recent detections on the same system

Call `liongard_detection LIST` filtered by `SystemID` and the last 14 days.
Summarize the most relevant change(s) close to the alert's `CreatedOn`.

### Step 4 — other open alerts on the same system / environment

Call `liongard_alert LIST` filtered by `SystemID` **and** by
`EnvironmentID` with `Status = "Open"`. Identify whether this alert is a
one-off or part of a cluster.

### Step 5 — recent inspection history (optional)

For deeper questions, call `liongard_timeline LIST` for the system and
inspect the last few inspections. Use `systemDetailID` from the timeline
row to fetch a specific dataprint if needed.

### Step 6 — synthesize

Produce a short report with these sections:

1. **Summary** — one sentence: what fired, on what system, at what time,
   severity.
2. **Context** — system name, type, environment, and whether anything
   obvious changed just before the alert.
3. **Related** — other open alerts on the same system / environment, or
   "no related alerts".
4. **Likely cause** — your best reading of what caused the alert, grounded
   in the detection / timeline evidence. Do **not** invent.
5. **Recommended next action** — one or two concrete steps the user can
   take (for example "remediate in the upstream system, then re-run the
   inspector") or "contact Liongard support" when the root cause is
   unclear.

## Rules

- Use exact IDs and timestamps from tool responses. Do not round or fudge.
- Every claim in **Likely cause** must be supported by data from steps 1–5.
  If you don't have evidence, say so explicitly.
- Keep the report compact; this is a triage brief, not a full incident
  report.
- If any step fails (for example the detection call returns no data), move
  on and mark that section as "not available" rather than blocking.

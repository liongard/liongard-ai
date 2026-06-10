---
name: liongard-investigate-alert
description: Use when the user asks to triage, investigate, diagnose, or explain a Liongard actionable alert.
---

# Liongard Investigate Alert

Prefer the built-in prompt when the alert ID is known:

```text
prompts/get name=investigate-alert arguments={"alertId": <id>}
```

If the prompt is unavailable or the user did not provide an ID, orchestrate
direct tools.

## Manual Workflow

1. Resolve the alert with `liongard_alert GET`, or list candidates with
   `liongard_alert LIST` filtered by the user's hint.
2. Capture alert ID, environment ID, system ID, launchpoint ID, severity, status,
   created time, title, and body.
3. Use `liongard_launchpoint GET_OVERVIEW` for system context.
4. Use `liongard_detection LIST` for recent detections on the same system.
5. Use `liongard_alert LIST` for related open alerts on the same system or
   environment.
6. Use `liongard_timeline LIST` only when deeper inspection history is needed.

## Output

Return:

1. Summary.
2. Context.
3. Related alerts or detections.
4. Likely cause, only if supported by evidence.
5. Recommended next action.

If evidence is missing, say so directly.

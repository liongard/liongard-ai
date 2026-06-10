---
name: liongard-environment-health
description: Use when the user asks for a daily health check, customer review, morning check, or attention list for a Liongard environment.
---

# Liongard Environment Health

Prefer `analyze-environment` when the environment ID is known:

```text
prompts/get name=analyze-environment arguments={"environmentId": <id>}
```

For tenant-wide operator checks, use `health-check`.

## Manual Workflow

1. Resolve the environment with `liongard_environment LIST` and
   `searchMode: "keyword"`.
2. Count and list open alerts with `liongard_alert`.
3. Check failing inspections with `liongard_launchpoint LIST` or the
   `failing-inspections` prompt.
4. Check recent changes with `liongard_detection LIST` or `recent-changes`.
5. Check security posture with `liongard_cyber_risk_dashboard` or
   `compliance-check`.
6. Include agent posture with `liongard_agents` when the user asks about
   collectors, offline agents, suspended agents, or coverage.

## Output

Return a concise report:

- Environment name and ID.
- Open alert count and top issues.
- Failing inspections.
- Recent changes.
- Cyber-risk posture.
- Top 3 recommended actions.

Mark partial/truncated data clearly.

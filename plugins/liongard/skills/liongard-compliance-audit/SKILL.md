---
name: liongard-compliance-audit
description: Use when the user asks about Liongard cyber-risk coverage, audit readiness, MFA, EDR, encryption, firewall, TLS/SSL, or security posture.
---

# Liongard Compliance Audit

Prefer the built-in prompt:

```text
prompts/get name=compliance-check arguments={"environmentId": <id>}
prompts/get name=compliance-check arguments={}
```

The prompt uses real cyber-risk coverage. Do not invent a synthetic compliance
score.

## Manual Workflow

1. Determine scope: one environment or all visible environments.
2. Resolve environment names with `liongard_environment`.
3. Pull broad posture with `liongard_cyber_risk_dashboard`.
4. For identity/device drilldowns, use `liongard_asset`.
5. For system-specific TLS/domain/configuration evidence, use
   `liongard_launchpoint`.
6. For recent drift, add `liongard_detection`.

## Output

Include:

- Scope.
- Per-pillar posture for MFA, EDR, encryption, firewall, TLS/SSL.
- Most urgent gap.
- Representative non-compliant entities when available.
- Next remediation steps.

If a pillar is not measured, say `not measured` instead of showing `0%`.

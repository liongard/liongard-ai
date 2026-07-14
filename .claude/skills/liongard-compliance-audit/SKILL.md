---
name: liongard-compliance-audit
description: Compliance audit across Liongard cyber-risk pillars (MFA, EDR, encryption, firewall, TLS/SSL) for one environment or the whole tenant. Use when the user asks about compliance status, security posture coverage, audit readiness, or per-pillar coverage.
---

# Liongard — Compliance audit

Use this skill when the user says something like:

- "Run a compliance audit on <environment>."
- "How is our MFA coverage?"
- "Are we ready for an audit?"
- "Show me EDR / encryption / firewall / TLS coverage."
- "What's our overall cyber-risk posture?"

## Prefer the built-in prompt

The Liongard MCP ships a `compliance-check` prompt that uses real
cyber-risk coverage data — not a synthetic score. Call it first:

```text
prompts/get name=compliance-check arguments={"environmentId": <id>}   # scope to one env
prompts/get name=compliance-check arguments={}                         # tenant-wide
```

If the user wants environment-by-environment deltas, also call
`compare-environments` for the two environments they care about.

## Manual workflow (fallback)

### Step 1 — scope

Identify:

- Whether the user wants a **single environment** or the **whole tenant**.
- Whether they want a specific pillar (MFA / EDR / encryption / firewall /
  TLS/SSL) or all five.

If they gave an environment name, resolve via `liongard_environment LIST`.

### Step 2 — pull coverage

Call `liongard_cyber_risk_dashboard` for each requested pillar. Capture:

- Total applicable assets / systems.
- Compliant count.
- Non-compliant count.
- Coverage percentage.

### Step 3 — drill into non-compliant population

For the pillar(s) with the lowest coverage, list representative
non-compliant entities:

- **MFA** — `liongard_identity COUNT` with `mfaStatus: "NO"`, `enabled: true`,
  `includeStatusCounts: true`. Then a focused `liongard_identity LIST` of
  `mfaStatus = "NO"` identities limited to ~20 rows.
- **EDR / encryption / firewall** — `liongard_device LIST` with
  the right filter (for example `edr` is null).
- **TLS/SSL** — pull the relevant systems via `liongard_launchpoint LIST`
  filtered by `systemCategory` and then check dataprint signals.

Keep each list to ≤20 entries and mark if more exist.

### Step 4 — synthesize

Produce a report with:

1. **Scope** — environment(s) audited, pillars covered.
2. **Posture summary** — one line per pillar:
   `MFA: 87% (112/129 identities)` etc.
3. **Lowest-coverage pillar** — the pillar most urgently in need of
   attention, with the top 5–10 non-compliant entities and the
   recommended remediation step.
4. **Other gaps** — one line per remaining pillar with any notable gap.
5. **Overall readiness** — a short, sober judgement (not a made-up score).
   Examples: "Ready for standard SOC 2 review pending MFA closeout on 17
   accounts" or "Audit blockers exist — see MFA and EDR sections".

## Rules

- Use real coverage numbers from the dashboard. Do not invent a
  composite "compliance score" — there is no such number in Liongard.
- Never show identity or device names that a scoped token can't actually
  see. Trust the tool response.
- Keep any exported list compact (≤20 rows). If more exist, say so
  ("showing 20 of 47").
- If coverage for a pillar is unavailable (for example, no identity
  inspector is installed in that environment), mark it as "not measured"
  instead of showing 0%.

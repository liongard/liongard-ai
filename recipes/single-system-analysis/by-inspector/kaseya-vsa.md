---
name: single-system-kaseya-vsa
description: >
  Use this skill when the user wants a single-system analysis of a
  Kaseya VSA tenant — agent coverage, patch posture, AV posture,
  software inventory, monitor / agent-procedure audit, alarm posture,
  technician usage, license utilization. Trigger phrases: "Kaseya VSA
  review", "VSA posture for <customer>", "Kaseya agent coverage",
  "Kaseya patch posture", "Kaseya alarm audit".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, technical-alignment-manager, vcio-account-manager, accounting-finance]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  - metrics:kaseya-vsa-inspector:agents-offline-count
  - metrics:kaseya-vsa-inspector:agents-online-count
  - metrics:kaseya-vsa-inspector:agents-total-count
  - metrics:kaseya-vsa-inspector:alarms-critical-count
  - metrics:kaseya-vsa-inspector:alarms-open-count
  - metrics:kaseya-vsa-inspector:endpoint-security-coverage-count
  - metrics:kaseya-vsa-inspector:licensing-seat-total
  - metrics:kaseya-vsa-inspector:licensing-seat-used
  - metrics:kaseya-vsa-inspector:licensing-utilization-pct
  - metrics:kaseya-vsa-inspector:monitor-sets-assigned-count
  - metrics:kaseya-vsa-inspector:monitor-sets-disabled-count
  - metrics:kaseya-vsa-inspector:patches-critical-pending-count
  - metrics:kaseya-vsa-inspector:patches-pending-count
  - metrics:kaseya-vsa-inspector:users-mfa-enabled-count
  - metrics:kaseya-vsa-inspector:users-total-count
---

# Single-System Analysis — Kaseya VSA

> **Inspector:** `kaseya-vsa-inspector` (ID 48). Apps & Services
> category. **One system per Kaseya VSA tenant.** Distinct from
> Kaseya BMS (PSA) — confirm scope when user says "Kaseya".
>
> **References:** `reference/inspector-aliases.md` (Kaseya, VSA,
> Kaseya VSA).

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-kaseya-vsa-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  agent_coverage: "Agent Coverage"
  patch_posture: "Patch Posture"
  antivirus_posture: "AV Posture"
  agent_procedures: "Agent Procedures / Monitor Sets"
  alarm_posture: "Alarm Activity"
  software_inventory: "Software Inventory"
  technician_usage: "Technician / VSA-User Posture"
  licensing: "License Utilization"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  agent_coverage_pct_min: 95
  agent_lastSeen_days_max: 7
  patch_age_days_max: 30
  critical_patches_pending_max: 0
  unresolved_alarms_max: 0
  antivirus_coverage_pct_min: 95
  monitor_sets_disabled_max: 0
  vsa_user_mfa_required: true            # Kaseya VSA has well-publicized MFA history; MFA on every VSA user
  license_utilization_warn_pct: 90
  license_expiration_warn_days: 60

reporting_period: { default: "current_state" }

qa:
  retry_on_null: true
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: false
  manual_verification_section_required: true
```

---

## When to use

- "Kaseya VSA posture review for <customer>"
- "VSA agent coverage check"
- "Kaseya VSA patch posture"
- "Kaseya VSA alarm audit"
- "Kaseya VSA-user MFA audit" (post-2021 incident hardening)

Cadence: monthly per customer; quarterly in PBR.

Personas:
- **NOC** (primary)
- **TAM** (monitor / agent-procedure drift)
- **vCIO / Account Manager** (renewal)
- **Accounting / Finance** (seat utilization)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the Kaseya VSA tenant) | Yes | `liongard_system LIST query="kaseya-vsa"` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="kaseya-vsa"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Agent coverage + device inventory

```
liongard_device LIST environmentId=<ENV_ID>
                     fields=["hostname","operatingSystem","class","inspectors","lastSeen"]
                     filter="inspectors contains 'kaseya-vsa-inspector'"

liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative:
#   "kaseya-vsa.agents.totalCount"
#   "kaseya-vsa.agents.onlineCount"
#   "kaseya-vsa.agents.offlineCount"
#   "kaseya-vsa.agents.byOs"
#   "kaseya-vsa.agents.byMachineGroup"
#   "kaseya-vsa.agents.lastCheckinDays"
```

### Step 4 — Patch posture

```
#   "kaseya-vsa.patches.pendingCount"
#   "kaseya-vsa.patches.criticalPendingCount"
#   "kaseya-vsa.patches.scanLastRun"
#   "kaseya-vsa.patches.installLastRun"
#   "kaseya-vsa.patches.byPolicy"
```

### Step 5 — Antivirus + Endpoint Security posture

```
#   "kaseya-vsa.endpointSecurity.coverageCount"
#   "kaseya-vsa.endpointSecurity.byVendor"     (Kaseya AV / third-party / none)
#   "kaseya-vsa.endpointSecurity.activeThreats"
```

### Step 6 — Agent procedures / Monitor sets

```
#   "kaseya-vsa.agentProcedures.scheduledCount"
#   "kaseya-vsa.agentProcedures.failedLast30Days"
#   "kaseya-vsa.monitorSets.assignedCount"
#   "kaseya-vsa.monitorSets.disabledCount"
```

### Step 7 — Alarm posture

```
#   "kaseya-vsa.alarms.openCount"
#   "kaseya-vsa.alarms.criticalCount"
#   "kaseya-vsa.alarms.byAge"
#   "kaseya-vsa.alarms.byMonitorSet"
```

### Step 8 — VSA-user posture (MFA / privileges)

```
#   "kaseya-vsa.users.totalCount"
#   "kaseya-vsa.users.mfaEnabledCount"
#   "kaseya-vsa.users.byRole"                  (Master / Admin / User / etc.)
#   "kaseya-vsa.users.disabledCount"
```

> **MFA on every VSA user is non-negotiable.** Kaseya VSA's 2021
> supply-chain incident drove a hardening push; flag any VSA user
> without MFA as Critical.

### Step 9 — Licensing

```
#   "kaseya-vsa.licensing.seatTotal"
#   "kaseya-vsa.licensing.seatUsed"
#   "kaseya-vsa.licensing.utilizationPct"
#   "kaseya-vsa.licensing.renewalDate"
```

### Step 10 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on:
1. Retry persistent nulls.
2. Stale inspector flag.
3. Cross-tool divergence (VSA agent count vs. reconciled inventory).
4. Proposed-metric gaps.
5. **MFA verification** — VSA-user MFA gaps elevated to Critical per
   post-incident hardening guidance.

### Step 11 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ⚠️ | Kaseya VSA is an RMM, not an EDR — RMM-equivalent endpoint questions covered above. Matrix doesn't yet include an RMM row; extend after first customer engagement. |
| CIS Controls (v8.1) | ✅ | Maps to CIS 1.1 (asset inventory), 2.1 (software inventory), 7.3 / 7.4 (patch currency / deployment), 10.1 / 10.6 (AV coverage), 6.3 / 6.4 (VSA-user MFA — elevated per post-2021-incident hardening), 8.2 (audit logs). |
| Cyber-insurance domain files | ✅ | Aligns with `domains/endpoint.md` (patch + AV), `domains/auth.md` Q14–Q17 (admin MFA — VSA-user MFA is the high-value-target subset), `domains/governance.md`. |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this when VSA is deployed; surfaces agent coverage %, critical patches pending, monitor-set coverage %, VSA-user MFA %, license utilization. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| Agent coverage below SLA | "Deploy Kaseya agent to <N> uncovered devices." |
| Agent offline > SLA | "<N> agents offline > <N> days. Triage." |
| Critical patches pending | "Apply <N> critical patches." |
| AV coverage below SLA | "Confirm AV deployment on <N> devices." |
| Disabled monitor set | "<N> monitor sets disabled. Re-enable per MSP standard." |
| Agent-procedure failure trend | "<N> agent procedures failed in last 30 days. Review and remediate." |
| **VSA user without MFA** | "URGENT: Enforce MFA on <N> VSA users immediately. Required post-2021 incident." |
| Excessive Master role | "Reduce Master-role count from <N> to operational minimum." |
| License utilization > warn | "Plan renewal expansion." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Per-agent procedure execution detail | partial | Kaseya VSA Console |
| Remote-control / Live Connect session audit | partial | Kaseya VSA Console |
| PSA / BMS integration health | partial | Kaseya BMS Console |
| Historical incident-response audit | external | SIEM |

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST + liongard_system LIST | per inspector | array | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3 | liongard_device LIST + liongard_metric VALUE | envId=<ENV_ID> [filter / metric names/JMESPath queries] | varies | ok per metric |
| 10 | QA pass (with MFA verification) | per `reference/qa-retry-pattern.md` | varies | ok |
| 11 | render | per `output.format` | <artifact path> | ok |
```

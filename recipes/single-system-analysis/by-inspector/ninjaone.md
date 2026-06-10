---
name: single-system-ninjaone
description: >
  Use this skill when the user wants a single-system analysis of a
  NinjaOne RMM tenant — agent coverage, patch posture, antivirus
  posture (NinjaOne Protect / third-party AV detection), software
  inventory, alert posture, technician usage, license utilization.
  Trigger phrases: "NinjaOne review", "Ninja RMM report", "NinjaRMM
  posture for <customer>" (legacy name), "Ninja agent coverage",
  "Ninja patch posture", "NinjaOne alert audit", "Ninja license
  utilization".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, technical-alignment-manager, vcio-account-manager, accounting-finance]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  - metrics:ninjaone:alerts-critical-count
  - metrics:ninjaone:alerts-open-count
  - metrics:ninjaone:devices-online-count
  - metrics:ninjaone:devices-total-count
  - metrics:ninjaone:licensing-utilization-pct
  - metrics:ninjaone:patches-critical-pending-count
  - metrics:ninjaone:patches-pending-count
  - metrics:ninjaone:users-mfa-enabled-count
  - metrics:ninjaone:users-technician-count
---

# Single-System Analysis — NinjaOne

> **Inspector:** `ninjaone-inspector` (ID 72). Apps & Services
> category. **One system per NinjaOne tenant.** Renamed from
> NinjaRMM in 2022 — both names accepted.
>
> **References:** `reference/inspector-aliases.md` (Ninja, NinjaOne,
> NinjaRMM). Pairs with `reference/asset-fields.md` for the
> reconciled device inventory; cross-reference with EDR / OS
> inspectors via the `inspectors[]` array on devices.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-ninjaone-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  agent_coverage: "Agent Coverage"
  patch_posture: "Patch Posture"
  antivirus_posture: "Antivirus / Protect Posture"
  software_inventory: "Software Inventory"
  alert_posture: "Alert Activity"
  technician_usage: "Technician Usage"
  licensing: "License Utilization"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  agent_coverage_pct_min: 95             # of expected device count
  agent_lastSeen_days_max: 7              # offline agents flag
  patch_age_days_max: 30
  critical_patches_pending_max: 0
  unresolved_alerts_max: 0
  antivirus_coverage_pct_min: 95
  license_utilization_warn_pct: 90       # > 90% utilization = warn for renewal
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

- "NinjaOne posture for <customer>"
- "Ninja agent coverage check"
- "Ninja patch posture review"
- "Ninja license utilization"
- "NinjaRMM report" (legacy)

Cadence: monthly per customer; quarterly in PBR; ad-hoc post-incident.

Personas:
- **NOC** (primary — daily operational health)
- **TAM** (policy / patch-cadence drift)
- **vCIO / Account Manager** (renewal narrative)
- **Accounting / Finance** (seat utilization)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the NinjaOne tenant) | Yes | `liongard_system LIST query="ninjaone"` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="ninjaone"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Agent coverage

```
liongard_device LIST environmentId=<ENV_ID>
                     fields=["hostname","operatingSystem","class","role","inspectors","lastSeen"]
                     filter="inspectors contains 'ninjaone-inspector'"

liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative:
#   "ninjaone.devices.totalCount"
#   "ninjaone.devices.onlineCount"
#   "ninjaone.devices.offlineCount"
#   "ninjaone.devices.lastSeenDays"
#   "ninjaone.devices.byOS"
#   "ninjaone.devices.byOrganization"
#   "ninjaone.devices.byLocation"
#   "ninjaone.devices.bySite"
```

Cross-reference with reconciled `liongard_device` inventory — devices
in environment but not in NinjaOne = agent-coverage gap.

### Step 4 — Patch posture

```
#   "ninjaone.patches.pendingCount"
#   "ninjaone.patches.criticalPendingCount"
#   "ninjaone.patches.installedLast30Days"
#   "ninjaone.patches.byOldestPending"      (oldest pending patch days)
#   "ninjaone.patches.byDevice"             (per-device pending count)
#   "ninjaone.patches.failedCount"          (failed install attempts)
```

### Step 5 — Antivirus posture

```
#   "ninjaone.protect.coverageCount"        (NinjaOne Protect)
#   "ninjaone.protect.threatsActiveCount"
#   "ninjaone.thirdPartyAv.detected"        (third-party AV detected per device)
```

### Step 6 — Software inventory

```
#   "ninjaone.software.totalUniqueCount"
#   "ninjaone.software.unauthorizedCount"   (if customer has unauthorized-list)
#   "ninjaone.software.byCategory"
```

### Step 7 — Alert posture

```
#   "ninjaone.alerts.openCount"
#   "ninjaone.alerts.criticalCount"
#   "ninjaone.alerts.byPriority"
#   "ninjaone.alerts.byAge"                 (open alert age in hours)
#   "ninjaone.alerts.byPolicyName"
```

### Step 8 — Technician usage + license utilization

```
#   "ninjaone.users.technicianCount"
#   "ninjaone.users.mfaEnabledCount"        (technicians)
#   "ninjaone.licensing.deviceSeatTotal"
#   "ninjaone.licensing.deviceSeatUsed"
#   "ninjaone.licensing.utilizationPct"
#   "ninjaone.licensing.renewalDate"
```

### Step 9 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on:
1. Retry persistent nulls.
2. Stale inspector flag.
3. Cross-tool divergence (NinjaOne device count vs. reconciled `liongard_device` count filtered to NinjaOne).
4. Proposed-metric gaps.
5. Single-source visibility — devices only in NinjaOne with no EDR / OS inspector cross-confirmation.

### Step 10 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ⚠️ | NinjaOne is an RMM, not an EDR — the six standard endpoint questions translate to "total devices managed / online last 30d / offline 60d+ / not covered / server vs workstation split / open alerts" and are covered above. The matrix does not currently include an RMM row; recommend extending it after first customer engagement uses this recipe. |
| CIS Controls (v8.1) | ✅ | Maps to CIS 1.1 (asset inventory — devices in RMM), 2.1 (software inventory), 7.3 / 7.4 (patch currency, patch deployment), 10.1 / 10.6 (AV / anti-malware coverage), 8.2 / 8.10 (audit logs from RMM). See `recipes/compliance/cyber-insurance/domains/endpoint.md`. |
| Cyber-insurance domain files | ✅ | Aligns with `domains/endpoint.md` patch-currency questions (Q8–Q11, Q10-sub) and AV coverage (Q1, Q12); `domains/governance.md` for technician-MFA audit. |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this when NinjaOne is the customer's RMM; surfaces agent coverage %, critical patches pending, open alerts, license utilization % as highlights. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| Agent coverage below SLA | "Deploy NinjaOne agent to <N> uncovered devices." |
| Agent offline > SLA days | "<N> agents offline for > <N> days. Triage — credential / network / decommission." |
| Critical patches pending | "Apply <N> critical patches. Oldest pending: <N> days." |
| High patch-failure count | "Investigate patch-install failures on <N> devices. Re-attempt or escalate." |
| Antivirus coverage below SLA | "Enable Protect (or confirm third-party AV) on <N> devices." |
| Unresolved alerts | "<N> open NinjaOne alerts; <N> critical. Triage backlog." |
| Technician without MFA | "Enforce MFA on <N> technician accounts." |
| License utilization > warn | "License utilization at <N>%. Plan renewal expansion before next billing cycle." |
| License renewal < warn-days | "License renewal in <N> days. Confirm seat count + initiate renewal." |
| Unauthorized software detected | "<N> instances of <software> detected. Confirm policy; remove if unauthorized." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Script-execution audit log | partial | NinjaOne Console |
| Per-device performance trend | partial | NinjaOne Console |
| Remote-control session history | partial | NinjaOne Console |
| Ticket / PSA integration health | partial | NinjaOne ↔ PSA console |

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST + liongard_system LIST | per inspector | array | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3 | liongard_device LIST + liongard_metric VALUE | envId=<ENV_ID> [filter / metric names/JMESPath queries] | varies | ok per metric |
| 9 | QA pass | per `reference/qa-retry-pattern.md` | varies | ok |
| 10 | render | per `output.format` | <artifact path> | ok |
```

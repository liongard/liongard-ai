---
name: single-system-datto-rmm
description: >
  Use this skill when the user wants a single-system analysis of a
  Datto RMM tenant — agent / device coverage, patch posture, antivirus
  posture (Datto AV / third-party), software inventory, monitor /
  alert posture, technician usage, license utilization. Trigger
  phrases: "Datto RMM review", "Datto RMM posture for <customer>",
  "Centrastage report" (legacy), "Autotask Endpoint Management" (legacy),
  "Datto RMM agent coverage", "Datto RMM patch posture".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, technical-alignment-manager, vcio-account-manager, accounting-finance]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  - metrics:datto-rmm:devices-pending-patches-count
  - metrics:datto-rmm:devices-snmp-enabled-count
---

# Single-System Analysis — Datto RMM

> **Inspector:** `datto-rmm-inspector` (ID 73). Apps & Services
> category. **One system per Datto RMM account.** Formerly Centrastage
> and Autotask Endpoint Management; legacy names accepted.
>
> **References:** `reference/inspector-aliases.md` (Datto RMM,
> Centrastage, AEM). Pairs with `reference/asset-fields.md` for the
> reconciled device inventory.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-datto-rmm-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  agent_coverage: "Agent Coverage"
  patch_posture: "Patch Posture"
  antivirus_posture: "AV Posture"
  monitor_audit: "Monitor / Component Audit"
  alert_posture: "Alert Activity"
  software_inventory: "Software Inventory"
  technician_usage: "Technician Usage"
  licensing: "License Utilization"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  agent_coverage_pct_min: 95
  agent_lastSeen_days_max: 7
  patch_age_days_max: 30
  critical_patches_pending_max: 0
  unresolved_alerts_max: 0
  antivirus_coverage_pct_min: 95
  monitors_disabled_max: 0               # any disabled standard monitor = finding
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

- "Datto RMM posture for <customer>"
- "Datto RMM agent coverage check"
- "Datto RMM patch posture review"
- "Centrastage report" (legacy)
- "Datto RMM monitor audit"

Cadence: monthly per customer; quarterly in PBR.

Personas:
- **NOC** (primary — operational health)
- **TAM** (monitor / patch standard drift)
- **vCIO / Account Manager** (renewal)
- **Accounting / Finance** (seat utilization)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the Datto RMM account) | Yes | `liongard_system LIST query="datto-rmm"` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="datto-rmm"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Agent coverage + device inventory

```
liongard_device LIST environmentId=<ENV_ID>
                     fields=["hostname","operatingSystem","class","role","inspectors","lastSeen"]
                     filter="inspectors contains 'datto-rmm-inspector'"

liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative:
#   "datto-rmm.devices.totalCount"
#   "datto-rmm.devices.onlineCount"
#   "datto-rmm.devices.offlineCount"
#   "datto-rmm.devices.byOs"
#   "datto-rmm.devices.bySite"
#   "datto-rmm.devices.lastSeenDays"
```

### Step 4 — Patch posture

```
#   "datto-rmm.patches.pendingCount"
#   "datto-rmm.patches.criticalPendingCount"
#   "datto-rmm.patches.byPolicy"          (per patch policy)
#   "datto-rmm.patches.deferredCount"
```

### Step 5 — Antivirus posture

```
#   "datto-rmm.av.coverageCount"
#   "datto-rmm.av.byVendor"               (Datto-AV / third-party / none)
#   "datto-rmm.av.threatsActiveCount"
```

### Step 6 — Monitor / component audit

```
#   "datto-rmm.monitors.standardCount"
#   "datto-rmm.monitors.customCount"
#   "datto-rmm.monitors.disabledCount"
#   "datto-rmm.components.runningCount"
#   "datto-rmm.components.failedLast30Days"
```

> **Why this matters:** Datto RMM's value is the monitor library.
> Drift from MSP-standard monitor coverage is the most-common TAM
> finding.

### Step 7 — Alert posture

```
#   "datto-rmm.alerts.openCount"
#   "datto-rmm.alerts.priorityCount"     (per priority level)
#   "datto-rmm.alerts.byAge"
#   "datto-rmm.alerts.byMonitorName"
```

### Step 8 — Software inventory + licensing

```
#   "datto-rmm.software.uniqueCount"
#   "datto-rmm.licensing.deviceSeatTotal"
#   "datto-rmm.licensing.deviceSeatUsed"
#   "datto-rmm.licensing.utilizationPct"
#   "datto-rmm.licensing.renewalDate"
```

### Step 9 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on:
1. Retry persistent nulls.
2. Stale inspector flag.
3. Cross-tool divergence (Datto RMM device count vs. reconciled inventory).
4. Proposed-metric gaps.
5. Single-source-visibility check.

### Step 10 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ⚠️ | Datto RMM is an RMM, not an EDR — RMM-equivalent endpoint questions (total devices / online 30d / offline 60d+ / not covered / server vs workstation / open alerts) are covered above. Matrix doesn't yet include an RMM row; extend after first customer engagement. |
| CIS Controls (v8.1) | ✅ | Maps to CIS 1.1 (asset inventory), 2.1 (software inventory), 7.3 / 7.4 (patch currency / deployment), 10.1 / 10.6 (AV coverage), 8.2 (audit logs). |
| Cyber-insurance domain files | ✅ | Aligns with `domains/endpoint.md` (patch + AV) and `domains/governance.md` (technician-MFA audit). |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this when Datto RMM is deployed; surfaces agent coverage %, critical patches pending, monitor-set coverage %, license utilization. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| Agent coverage below SLA | "Deploy Datto RMM agent to <N> uncovered devices." |
| Agent offline > SLA | "<N> agents offline > <N> days. Triage." |
| Critical patches pending | "Apply <N> critical patches." |
| Patches deferred excessively | "<N> patches deferred — review patch policy for over-deferral." |
| AV coverage below SLA | "Confirm AV deployment on <N> devices." |
| Disabled standard monitor | "<N> standard monitors disabled. Re-enable per MSP baseline." |
| Component failure trend | "<N> components failed in last 30 days. Review and remediate." |
| Open alerts unresolved | "<N> open alerts; <N> high priority. Triage backlog." |
| License utilization > warn | "Plan renewal expansion before next billing cycle." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Per-component script content | external | Datto RMM Console |
| Remote-control session history | partial | Datto RMM Console |
| Per-device performance trend | partial | Datto RMM Console |
| PSA / Autotask integration health | partial | Datto RMM ↔ Autotask |

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

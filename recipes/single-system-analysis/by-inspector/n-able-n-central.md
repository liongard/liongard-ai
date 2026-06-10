---
name: single-system-n-able-n-central
description: >
  Use this skill when the user wants a single-system analysis of an
  N-able N-central tenant — agent coverage, patch posture, AV posture
  (N-able EDR / third-party), monitor / service posture, alert
  activity, technician usage, license utilization. Trigger phrases:
  "N-central review", "N-able N-central posture for <customer>",
  "SolarWinds N-central report" (legacy), "N-central agent coverage",
  "N-central patch posture".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, technical-alignment-manager, vcio-account-manager, accounting-finance]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  - metrics:n-able-n-central:count-of-devices-added-last-30-days
  - metrics:n-able-n-central:count-of-devices-failed-state
  - metrics:n-able-n-central:count-of-devices-stale-state
  - metrics:n-able-n-central:count-of-devices-warning-state
  - metrics:n-able-n-central:count-of-esxi-servers
  - metrics:n-able-n-central:count-of-failed-jobs
  - metrics:n-able-n-central:count-of-printers
  - metrics:n-able-n-central:count-of-storage-devices
  - metrics:n-able-n-central:count-of-switch-router-devices
  - metrics:n-able-n-central:count-of-windows-laptops
  - metrics:n-able-n-central:count-of-windows-servers
  - metrics:n-able-n-central:count-of-workstations
  - metrics:n-able-n-central:device-details-powerbi
  - metrics:n-able-n-central:device-info-with-last-user
  - metrics:n-able-n-central:device-list-powerbi
  - metrics:n-able-n-central:list-of-devices-added-last-30-days
  - metrics:n-able-n-central:list-of-devices-failed-state
  - metrics:n-able-n-central:list-of-devices-stale-state
  - metrics:n-able-n-central:list-of-devices-warning-state
  - metrics:n-able-n-central:list-of-esxi-servers
  - metrics:n-able-n-central:list-of-failed-jobs
  - metrics:n-able-n-central:list-of-printers
  - metrics:n-able-n-central:list-of-storage-devices
  - metrics:n-able-n-central:list-of-switch-router-devices
  - metrics:n-able-n-central:list-of-windows-laptops
  - metrics:n-able-n-central:list-of-windows-servers
  - metrics:n-able-n-central:list-of-workstations
---

# Single-System Analysis — N-able N-central

> **Inspector:** `n-able-n-central-inspector` (ID 71). Apps & Services
> category. **One system per N-central tenant.** Formerly SolarWinds
> N-central; legacy name accepted.
>
> **References:** `reference/inspector-aliases.md` (N-central, NC,
> SolarWinds N-central).

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-n-central-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  agent_coverage: "Agent Coverage"
  patch_posture: "Patch Posture"
  antivirus_posture: "AV / EDR Posture"
  monitor_audit: "Monitor / Service Audit"
  alert_posture: "Alert Activity"
  technician_usage: "Technician / User Posture"
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
  service_monitors_disabled_max: 0
  user_mfa_required: true
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

- "N-central posture for <customer>"
- "N-central agent coverage check"
- "N-central patch posture"
- "SolarWinds N-central report" (legacy)

Cadence: monthly per customer; quarterly in PBR.

Personas: NOC (primary), TAM, vCIO/AM, Accounting/Finance.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID | Yes | `liongard_system LIST query="n-central"` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="n-central"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Agent coverage + device inventory

```
liongard_device LIST environmentId=<ENV_ID>
                     fields=["hostname","operatingSystem","class","inspectors","lastSeen"]
                     filter="inspectors contains 'n-able-n-central-inspector'"

liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative:
#   "n-central.devices.totalCount"
#   "n-central.devices.onlineCount"
#   "n-central.devices.offlineCount"
#   "n-central.devices.byOs"
#   "n-central.devices.byCustomer"        (multi-tenant grouping)
#   "n-central.devices.byServiceOrg"
```

### Step 4 — Patch posture

```
#   "n-central.patches.pendingCount"
#   "n-central.patches.criticalPendingCount"
#   "n-central.patches.byPolicy"
#   "n-central.patches.complianceScore"
```

### Step 5 — AV / EDR posture

```
#   "n-central.av.coverageCount"
#   "n-central.av.byVendor"
#   "n-central.av.activeThreats"
#   "n-central.edr.coverageCount"         (N-able EDR if deployed)
```

### Step 6 — Monitor / Service audit

```
#   "n-central.services.monitoredCount"
#   "n-central.services.failedCount"
#   "n-central.services.disabledCount"
#   "n-central.monitors.standardCount"
#   "n-central.monitors.customCount"
```

### Step 7 — Alert posture

```
#   "n-central.alerts.openCount"
#   "n-central.alerts.byPriority"
#   "n-central.alerts.byAge"
```

### Step 8 — User + license posture

```
#   "n-central.users.totalCount"
#   "n-central.users.mfaEnabledCount"
#   "n-central.users.byRole"
#   "n-central.licensing.seatTotal"
#   "n-central.licensing.seatUsed"
#   "n-central.licensing.utilizationPct"
#   "n-central.licensing.renewalDate"
```

### Step 9 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on retry, freshness, cross-tool divergence, proposed-metric
gaps, single-source visibility.

### Step 10 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ⚠️ | N-central is an RMM — RMM-equivalent endpoint questions covered above. Matrix doesn't yet include an RMM row; extend after first customer engagement. |
| CIS Controls (v8.1) | ✅ | Maps to CIS 1.1, 2.1, 7.3 / 7.4 (patch), 10.1 / 10.6 (AV), 8.2 (audit logs). |
| Cyber-insurance domain files | ✅ | Aligns with `domains/endpoint.md` and `domains/governance.md`. |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this when N-central is the customer's RMM. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| Agent coverage below SLA | "Deploy N-central agent to <N> uncovered devices." |
| Agent offline > SLA | "<N> agents offline > <N> days. Triage." |
| Critical patches pending | "Apply <N> critical patches." |
| AV coverage below SLA | "Confirm AV / EDR deployment on <N> devices." |
| Disabled service monitor | "<N> service monitors disabled. Re-enable per MSP standard." |
| Open alerts unresolved | "<N> open alerts; <N> high priority. Triage." |
| User without MFA | "Enforce MFA on <N> N-central users." |
| License utilization > warn | "Plan renewal expansion." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Automation policy detail | partial | N-central Console |
| Remote-control session audit | partial | N-central Console |
| PSA integration health | partial | N-central ↔ PSA |
| Backup-integration (Cove / Backup Manager) | partial | N-central Console + backup-vendor recipes |

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

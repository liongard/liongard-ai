---
name: single-system-connectwise-automate
description: >
  Use this skill when the user wants a single-system analysis of a
  ConnectWise Automate tenant — agent coverage, patch posture, AV
  posture, monitor / internal-monitor audit, ticket-script integration,
  technician usage, license utilization. Trigger phrases: "ConnectWise
  Automate review", "CWA posture for <customer>", "LabTech report"
  (legacy), "Automate agent coverage", "Automate patch posture",
  "Automate alerts".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, technical-alignment-manager, vcio-account-manager, accounting-finance]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  # Reconciled 2026-05-29: pruned dangling refs not present in the live dataprint (see internal/proposed-metrics-backlog.md).
  - metrics:connectwise-automate:computers-total-count
---

# Single-System Analysis — ConnectWise Automate

> **Inspector:** `connectwise-automate-inspector` (ID 36). Apps &
> Services category. **One system per ConnectWise Automate server.**
> Formerly LabTech; legacy name accepted.
>
> **References:** `reference/inspector-aliases.md` (CW Automate, CWA,
> Automate, LabTech).

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-cw-automate-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  agent_coverage: "Agent Coverage"
  patch_posture: "Patch Posture"
  antivirus_posture: "AV Posture"
  monitor_audit: "Internal Monitor / Group Audit"
  alert_posture: "Alert / Ticket Activity"
  scripts: "Script Posture"
  technician_usage: "Technician Posture"
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
  internal_monitors_disabled_max: 0
  technician_mfa_required: true
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

- "Automate posture for <customer>"
- "CWA agent coverage"
- "Automate patch posture"
- "LabTech report" (legacy)

Cadence: monthly per customer; quarterly in PBR.

Personas: NOC (primary), TAM, vCIO/AM, Accounting/Finance.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID | Yes | `liongard_system LIST query="connectwise-automate"` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="connectwise-automate"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Agent coverage + device inventory

```
liongard_device LIST environmentId=<ENV_ID>
                     fields=["hostname","operatingSystem","class","inspectors","lastSeen"]
                     filter="inspectors contains 'connectwise-automate-inspector'"

liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative:
#   "cw-automate.computers.totalCount"
#   "cw-automate.computers.onlineCount"
#   "cw-automate.computers.offlineCount"
#   "cw-automate.computers.byOs"
#   "cw-automate.computers.byLocation"
#   "cw-automate.computers.byClient"
#   "cw-automate.computers.heartbeatLastDays"
```

### Step 4 — Patch posture

```
#   "cw-automate.patches.pendingCount"
#   "cw-automate.patches.criticalPendingCount"
#   "cw-automate.patches.byPolicyName"
#   "cw-automate.patches.failedLast30Days"
```

### Step 5 — AV posture

```
#   "cw-automate.av.coverageCount"
#   "cw-automate.av.byVendor"
#   "cw-automate.av.activeThreats"
```

### Step 6 — Internal monitor / group audit

```
#   "cw-automate.monitors.standardCount"
#   "cw-automate.monitors.customCount"
#   "cw-automate.monitors.disabledCount"
#   "cw-automate.groups.computerGroupCount"
#   "cw-automate.groups.locationGroupCount"
```

> **Why this matters:** Automate's value is in the monitor + group
> structure. Drift here = drift in actual coverage and is the most-
> common TAM finding.

### Step 7 — Alert / ticket posture

```
#   "cw-automate.alerts.openCount"
#   "cw-automate.alerts.byPriority"
#   "cw-automate.alerts.byAge"
#   "cw-automate.tickets.openCount"           (CW Manage integration)
```

### Step 8 — Script posture

```
#   "cw-automate.scripts.scheduledCount"
#   "cw-automate.scripts.runningCount"
#   "cw-automate.scripts.failedLast30Days"
#   "cw-automate.scripts.byCategory"
```

### Step 9 — Technician + licensing

```
#   "cw-automate.users.technicianCount"
#   "cw-automate.users.mfaEnabledCount"
#   "cw-automate.licensing.agentSeatTotal"
#   "cw-automate.licensing.agentSeatUsed"
#   "cw-automate.licensing.utilizationPct"
#   "cw-automate.licensing.renewalDate"
```

### Step 10 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on retry, freshness, cross-tool divergence, proposed-metric
gaps, single-source visibility.

### Step 11 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ⚠️ | Automate is an RMM — RMM-equivalent endpoint questions covered above. Matrix doesn't yet include an RMM row; extend after first customer engagement. |
| CIS Controls (v8.1) | ✅ | Maps to CIS 1.1, 2.1, 7.3 / 7.4 (patch), 10.1 / 10.6 (AV), 8.2 (audit logs from internal monitors). |
| Cyber-insurance domain files | ✅ | Aligns with `domains/endpoint.md` and `domains/governance.md`. |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this when Automate is the customer's RMM; surfaces agent coverage %, patch posture, internal-monitor coverage %, technician-MFA %, license utilization. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| Agent coverage below SLA | "Deploy Automate agent to <N> uncovered devices." |
| Agent offline > SLA | "<N> agents offline > <N> days. Triage." |
| Critical patches pending | "Apply <N> critical patches." |
| Patch-install failure trend | "Review patch install failures on <N> devices." |
| AV coverage below SLA | "Confirm AV deployment on <N> devices." |
| Disabled standard monitor | "<N> internal monitors disabled. Re-enable per MSP standard." |
| Script failure trend | "<N> scripts failed in last 30 days. Review and remediate." |
| Open alerts unresolved | "<N> open alerts; <N> high priority. Triage." |
| Technician without MFA | "Enforce MFA on <N> Automate users." |
| License utilization > warn | "Plan renewal expansion." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Script content / logic detail | partial | Automate Console |
| Remote-control session audit | partial | Automate Console |
| CW Manage integration health | partial | CW Manage Console |
| Plugins / Solution Center detail | partial | Automate Console |

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST + liongard_system LIST | per inspector | array | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3 | liongard_device LIST + liongard_metric VALUE | envId=<ENV_ID> [filter / metric names/JMESPath queries] | varies | ok per metric |
| 10 | QA pass | per `reference/qa-retry-pattern.md` | varies | ok |
| 11 | render | per `output.format` | <artifact path> | ok |
```

---
name: single-system-syncro
description: >
  Use this skill when the user wants a single-system analysis of a
  Syncro tenant — ticket volume + aging, SLA compliance, technician
  utilization, time-tracking + billing, RMM agent coverage (Syncro
  bundles RMM + PSA), contract / recurring-invoice audit. Trigger
  phrases: "Syncro review", "Syncro posture for <customer>", "RepairShopr
  report" (legacy), "Syncro ticket aging", "Syncro agent coverage",
  "Syncro recurring invoice audit".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [vcio-account-manager, accounting-finance, noc, technical-alignment-manager]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  # Reconciled 2026-05-29 vs live dataprint (live production environment, inspected 2026-05-29).
  # This dataprint exposes Companies/Users/Contracts/Products only — no devices,
  # tickets, invoices, patches, SLA, or per-user MFA. Those refs were pruned to
  # internal/proposed-metrics-backlog.md.
  - metrics:syncro-inspector:companies-total-count
  - metrics:syncro-inspector:companies-active-count
  - metrics:syncro-inspector:users-total-count
  - metrics:syncro-inspector:users-admin-count
  - metrics:syncro-inspector:contracts-total-count
  - metrics:syncro-inspector:products-count
---

# Single-System Analysis — Syncro

> **Inspector:** `syncro-inspector` (ID 86). Apps & Services category.
> **One system per Syncro tenant.** Hybrid PSA + RMM in a single
> platform — most common at small / mid-market MSPs. Formerly
> RepairShopr; legacy name accepted.
>
> **References:** `reference/inspector-aliases.md` (Syncro, RepairShopr).

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-syncro-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  ticket_volume: "Ticket Volume & Trend"
  ticket_aging: "Ticket Aging"
  sla_compliance: "SLA Compliance"
  agent_coverage: "RMM Agent Coverage"        # Syncro includes RMM
  technician_utilization: "Technician Utilization"
  time_billing: "Time Entry & Billing"
  recurring_invoices: "Recurring Invoice Audit"
  customer_profile: "Per-Customer Ticket Profile"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  ticket_age_warn_days: 7
  ticket_age_critical_days: 30
  sla_compliance_pct_min: 95
  agent_coverage_pct_min: 95
  agent_lastSeen_days_max: 7
  technician_billable_utilization_target_pct: 70
  time_entry_lag_days_max: 2
  recurring_invoice_warn_days: 60

reporting_period:
  default: "last_quarter"

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

- "Syncro posture review"
- "Syncro ticket aging"
- "Syncro RMM agent coverage"
- "Syncro recurring invoice audit"
- "RepairShopr report" (legacy)

Cadence: monthly per MSP; quarterly for PBR.

Personas: vCIO/AM (primary), Accounting/Finance (primary — recurring
invoices), NOC (operational + RMM-agent), TAM.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the Syncro tenant) | Yes | `liongard_system LIST query="syncro"` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="syncro"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Ticket + SLA + utilization + time-tracking (PSA side)

```
liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative:
#   "syncro.tickets.{openCount, openByPriority, openByCustomer, openByTech, agingByBracket}"
#   "syncro.tickets.{closedLast30Days, avgTimeToClose}"
#   "syncro.sla.{responseCompliancePct, resolutionCompliancePct, breachedCount}"
#   "syncro.users.{totalCount, byRole, billableUtilizationPct, mfaEnabledCount}"
#   "syncro.timeEntries.{totalCount, byEntryLagDays, notInvoicedCount}"
```

### Step 4 — RMM agent coverage (RMM side)

```
liongard_device LIST environmentId=<ENV_ID>
                     fields=["hostname","operatingSystem","class","inspectors","lastSeen"]
                     filter="inspectors contains 'syncro-inspector'"

#   "syncro.devices.totalCount"
#   "syncro.devices.onlineCount / offlineCount"
#   "syncro.devices.byOs"
#   "syncro.devices.byCustomer"
#   "syncro.patches.pendingCount / criticalPendingCount"
#   "syncro.av.coverageCount / byVendor"
```

Cross-reference with reconciled `liongard_device` inventory.

### Step 5 — Recurring invoice audit

```
#   "syncro.invoices.recurringCount"
#   "syncro.invoices.recurringByCustomer"
#   "syncro.invoices.expiringWithinWarnDays"
#   "syncro.invoices.unbilledThisCycle"
#   "syncro.invoices.totalRecurringRevenuePerMonth"
```

### Step 6 — Per-customer ticket profile

```
#   "syncro.tickets.byCustomerLast90Days"
#   "syncro.tickets.topCustomersByVolume"
```

### Step 7 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on retry, freshness, agent-coverage divergence (Syncro RMM vs.
reconciled device inventory), recurring-invoice expiration check,
proposed-metric gaps.

### Step 8 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ⚠️ | Syncro RMM side touches the six standard endpoint questions (total / online / offline / not covered / OS split / open tickets). Matrix doesn't yet include a Syncro row; extend after first customer engagement. |
| CIS Controls (v8.1) | ✅ | Maps to CIS 1.1 (asset inventory — RMM side), 7.3 / 7.4 (patch), 10.1 (AV), 6.4 (Syncro user MFA), 8.2 (audit logs). |
| Cyber-insurance domain files | ⚠️ | RMM side aligns with `domains/endpoint.md` (patch + AV). PSA side not typically required for cyber-insurance evidence. |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this when Syncro is the customer's PSA+RMM; surfaces per-customer ticket profile, RMM agent coverage, recurring-invoice expirations. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| High aged-ticket count | "<N> tickets aged > <N> days." |
| Agent coverage below SLA | "Deploy Syncro agent to <N> uncovered devices." |
| Critical patches pending | "Apply <N> critical patches via Syncro." |
| Recurring invoice expiring | "<N> recurring invoices expire within <N> days. Renew or terminate." |
| Top customer volume divergence | "Customer <C> volume up <N>%. AM conversation." |
| Syncro user without MFA | "Enforce MFA on <N> Syncro users." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Ticket / repair note content | not in dataprint | Syncro Console |
| Per-customer NPS | external | `recipes/external-data/client-surveys-nps.md` |
| Inventory / parts module detail | partial | Syncro Console |
| Estimate / quote pipeline | partial | Syncro Console |

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST + liongard_system LIST | per inspector | array | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3-6 | liongard_metric VALUE + liongard_device LIST | envId=<ENV_ID> sysId=<SYS_ID> | varies | ok per metric |
| 7 | QA pass | per `reference/qa-retry-pattern.md` | varies | ok |
| 8 | render | per `output.format` | <artifact path> | ok |
```

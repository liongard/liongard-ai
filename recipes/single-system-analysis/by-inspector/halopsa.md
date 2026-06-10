---
name: single-system-halopsa
description: >
  Use this skill when the user wants a single-system analysis of a
  HaloPSA tenant — ticket volume + aging, SLA compliance, agent
  utilization, time-tracking + billing, contract audit, per-customer
  ticket profile. Trigger phrases: "HaloPSA review", "Halo posture for
  <customer>", "HaloPSA ticket aging", "HaloPSA SLA compliance",
  "Halo agent utilization", "HaloPSA contract audit".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric"
personas: [vcio-account-manager, accounting-finance, noc, technical-alignment-manager]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  # Reconciled 2026-05-29 vs live dataprint (live production environment, inspected 2026-05-29).
  # Tickets[] key exists but was empty on the test system, and no SLA-compliance/billable
  # fields are present — tickets-*, sla-*, agents-billable-utilization-pct, contracts-expiring
  # pruned to internal/proposed-metrics-backlog.md (tickets-* are SCHEMA_CONFIRMED candidates).
  - metrics:halopsa-inspector:agents-total-count
  - metrics:halopsa-inspector:agents-active-count
  - metrics:halopsa-inspector:customers-total-count
  - metrics:halopsa-inspector:customers-active-count
  - metrics:halopsa-inspector:sites-total-count
  - metrics:halopsa-inspector:sites-active-count
  - metrics:halopsa-inspector:teams-total-count
  - metrics:halopsa-inspector:contracts-total-count
  - metrics:halopsa-inspector:contracts-active-count
  - metrics:halopsa-inspector:system-version
---

# Single-System Analysis — HaloPSA

> **Inspector:** `halopsa-inspector` (ID 94). Apps & Services
> category. **One system per HaloPSA tenant.** Modern PSA platform —
> popular alternative to ConnectWise / Autotask.
>
> **References:** `reference/inspector-aliases.md` (Halo, HaloPSA).

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-halopsa-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  ticket_volume: "Ticket Volume & Trend"
  ticket_aging: "Ticket Aging"
  sla_compliance: "SLA Compliance"
  agent_utilization: "Agent Utilization"
  time_billing: "Time Entry & Billing"
  contracts: "Contract Audit"
  customer_profile: "Per-Customer Ticket Profile"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  ticket_age_warn_days: 7
  ticket_age_critical_days: 30
  sla_compliance_pct_min: 95
  agent_billable_utilization_target_pct: 70
  time_entry_lag_days_max: 2
  contract_expiration_warn_days: 60

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

- "HaloPSA posture review"
- "Halo ticket aging"
- "Halo SLA compliance"
- "Halo agent utilization"
- "Halo contract audit"
- "Per-customer ticket profile from Halo"

Cadence: monthly per MSP; quarterly for PBR.

Personas: vCIO/AM (primary), Accounting/Finance (primary), NOC, TAM.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the HaloPSA tenant) | Yes | `liongard_system LIST query="halopsa"` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="halopsa"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Tickets

```
liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative:
#   "halopsa.tickets.openCount"
#   "halopsa.tickets.openByPriority"
#   "halopsa.tickets.openByTeam"
#   "halopsa.tickets.openByClient"          (per customer)
#   "halopsa.tickets.openByAgent"
#   "halopsa.tickets.agingByBracket"
#   "halopsa.tickets.closedLast30Days"
#   "halopsa.tickets.avgTimeToClose"
```

### Step 4 — SLA compliance

```
#   "halopsa.sla.responseCompliancePct"
#   "halopsa.sla.resolutionCompliancePct"
#   "halopsa.sla.breachedCount"
#   "halopsa.sla.byTeam"
#   "halopsa.sla.byPriority"
```

### Step 5 — Agent utilization

```
#   "halopsa.agents.totalCount"
#   "halopsa.agents.activeCount"
#   "halopsa.agents.byTeam"
#   "halopsa.agents.billableUtilizationPct"
#   "halopsa.agents.timeEntriesLast30Days"
```

### Step 6 — Time + billing

```
#   "halopsa.timeEntries.totalCount"
#   "halopsa.timeEntries.byEntryLagDays"
#   "halopsa.timeEntries.unbillableCount"
#   "halopsa.timeEntries.notInvoicedCount"
```

### Step 7 — Contract audit

```
#   "halopsa.contracts.activeCount"
#   "halopsa.contracts.byType"
#   "halopsa.contracts.expiringWithinWarnDays"
```

### Step 8 — Per-customer ticket profile

```
#   "halopsa.tickets.byClientLast90Days"
#   "halopsa.tickets.topClientsByVolume"
#   "halopsa.tickets.reopenedByClient"
#   "halopsa.tickets.avgCloseTimeByClient"
```

### Step 9 — QA pass (per `reference/qa-retry-pattern.md`)

Same operational privacy stance as other PSA recipes.

### Step 10 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | PSA operational tooling. |
| CIS Controls (v8.1) | ⚠️ | Indirect: CIS 8.2 (PSA audit logs), 6.4 (Halo user MFA). |
| Cyber-insurance domain files | n/a | PSA operational data. |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this when Halo is the PSA; surfaces per-customer ticket profile, SLA compliance, contract expiration. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| High aged-ticket count | "<N> tickets aged > <N> days. Triage; reassign / escalate." |
| SLA compliance below threshold | "Response/resolution SLA breach. Review by team / priority." |
| Agent utilization below target | "Agent <X> at <N>%. Confirm time-entry flow." |
| Time-entry lag high | "<N> entries > <N> days late." |
| Contract expiring < warn | "<N> contracts expire within <N> days." |
| Reopen rate high per client | "Client <C> at <N>% reopen rate. Root-cause triage." |
| Top client volume divergence | "Client <C> volume up <N>%. AM conversation." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Ticket content / resolution notes | not in dataprint | HaloPSA Console |
| Per-ticket profitability | partial | HaloPSA Console + accounting |
| Per-client NPS | external | `recipes/external-data/client-surveys-nps.md` |
| Halo ITSM / CMDB modules | partial | HaloPSA Console |

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST + liongard_system LIST | per inspector | array | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3-8 | liongard_metric VALUE | envId=<ENV_ID> sysId=<SYS_ID> metric=<id> | varies | ok per metric |
| 9 | QA pass | per `reference/qa-retry-pattern.md` | varies | ok |
| 10 | render | per `output.format` | <artifact path> | ok |
```

---
name: single-system-kaseya-bms
description: >
  Use this skill when the user wants a single-system analysis of a
  Kaseya BMS (PSA) tenant — ticket volume + aging, SLA compliance,
  technician utilization, time-tracking + billing, contract audit,
  per-customer ticket profile. Trigger phrases: "Kaseya BMS review",
  "BMS posture for <customer>", "Kaseya BMS ticket aging", "BMS SLA
  compliance", "BMS contract audit".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric"
personas: [vcio-account-manager, accounting-finance, noc, technical-alignment-manager]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  # Reconciled 2026-05-29 vs live dataprint (live production environment, inspected 2026-05-28).
  # This dataprint exposes Users/Roles/Contracts/Accounts/Services only — no tickets,
  # SLA-compliance, billable-utilization, or per-user MFA. Those refs were pruned to
  # internal/proposed-metrics-backlog.md. (Users are the technicians/employees.)
  - metrics:kaseya-bms-inspector:users-total-count
  - metrics:kaseya-bms-inspector:users-active-count
  - metrics:kaseya-bms-inspector:accounts-total-count
  - metrics:kaseya-bms-inspector:accounts-active-count
  - metrics:kaseya-bms-inspector:contracts-total-count
  - metrics:kaseya-bms-inspector:roles-total-count
---

# Single-System Analysis — Kaseya BMS

> **Inspector:** `kaseya-bms-inspector` (ID 83). Apps & Services
> category. **One system per Kaseya BMS tenant.** Kaseya's PSA —
> distinct from Kaseya VSA (RMM); confirm scope when user says "Kaseya".
>
> **References:** `reference/inspector-aliases.md` (BMS, Kaseya BMS).
> Pairs with `kaseya-vsa.md` for the Kaseya-stack integration story.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-kaseya-bms-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  ticket_volume: "Ticket Volume & Trend"
  ticket_aging: "Ticket Aging"
  sla_compliance: "SLA Compliance"
  technician_utilization: "Technician Utilization"
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
  technician_billable_utilization_target_pct: 70
  time_entry_lag_days_max: 2
  contract_expiration_warn_days: 60
  bms_user_mfa_required: true              # Kaseya post-2021 incident hardening — every BMS user MFA

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

- "Kaseya BMS review"
- "BMS ticket aging"
- "BMS SLA compliance"
- "BMS contract audit"
- "Per-customer ticket profile from BMS"

Cadence: monthly per MSP; quarterly for PBR.

Personas: vCIO/AM (primary), Accounting/Finance (primary), NOC, TAM.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the BMS tenant) | Yes | `liongard_system LIST query="kaseya-bms"` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="kaseya-bms"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Tickets + SLA + utilization + time + contracts + per-customer

```
liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Same metric family as CW Manage / Autotask / Halo — namespace under "kaseya-bms.":
#   "kaseya-bms.tickets.openCount"
#   "kaseya-bms.tickets.openByPriority / Queue / Account / Technician"
#   "kaseya-bms.tickets.agingByBracket"
#   "kaseya-bms.tickets.closedLast30Days"
#   "kaseya-bms.tickets.avgTimeToClose"
#   "kaseya-bms.sla.{response,resolution}CompliancePct"
#   "kaseya-bms.sla.breachedCount"
#   "kaseya-bms.technicians.{totalCount, activeCount, byRole, billableUtilizationPct}"
#   "kaseya-bms.timeEntries.{totalCount, byEntryLagDays, notInvoicedCount}"
#   "kaseya-bms.contracts.{activeCount, byType, expiringWithinWarnDays}"
#   "kaseya-bms.tickets.byAccountLast90Days"
#   "kaseya-bms.tickets.topAccountsByVolume"
#   "kaseya-bms.users.{totalCount, mfaEnabledCount, byRole}"
```

### Step 4 — BMS-user MFA audit

```
#   "kaseya-bms.users.mfaCoveragePct"
#   "kaseya-bms.users.mfaDisabledList"
```

> **MFA on every BMS user is non-negotiable** per post-2021 Kaseya
> incident hardening. Flag any BMS-user without MFA as Critical.

### Step 5 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on retry, freshness, BMS-user MFA verification, proposed-metric gaps.

### Step 6 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | PSA operational tooling. |
| CIS Controls (v8.1) | ⚠️ | Indirect: CIS 8.2 (PSA audit logs), 6.4 (BMS-user MFA — elevated per Kaseya post-2021 guidance). |
| Cyber-insurance domain files | n/a | PSA operational data. |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this when BMS is the PSA. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| High aged-ticket count | "<N> tickets aged > <N> days." |
| SLA compliance below threshold | "Review breached tickets by queue / priority." |
| Technician utilization below target | "Confirm time-entry flow for <X>." |
| Contract expiring < warn | "<N> contracts expire within <N> days." |
| **BMS user without MFA** | "URGENT: Enforce MFA on <N> BMS users. Required post-2021 incident." |
| Top account volume divergence | "Account <A> volume up <N>%. AM conversation." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Ticket content / resolution notes | not in dataprint | BMS Console |
| Per-ticket profitability | partial | BMS Console + accounting |
| Per-client NPS | external | `recipes/external-data/client-surveys-nps.md` |
| VSA integration health | partial | VSA Console + per-VSA recipe |

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST + liongard_system LIST | per inspector | array | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3-4 | liongard_metric VALUE | envId=<ENV_ID> sysId=<SYS_ID> metric=<id> | varies | ok per metric |
| 5 | QA pass (with BMS-user MFA verification) | per `reference/qa-retry-pattern.md` | varies | ok |
| 6 | render | per `output.format` | <artifact path> | ok |
```

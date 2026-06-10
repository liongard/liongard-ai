---
name: single-system-connectwise-manage
description: >
  Use this skill when the user wants a single-system analysis of a
  ConnectWise Manage (PSA) tenant — ticket volume + aging, SLA
  compliance, technician utilization, time-tracking accuracy, contract
  / agreement audit, customer ticket profile. Trigger phrases:
  "ConnectWise Manage review", "CW Manage posture for <customer>",
  "ticket aging in CW Manage", "PSA SLA compliance", "technician
  utilization in CW Manage", "CW Manage agreement audit".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric"
personas: [vcio-account-manager, accounting-finance, noc, technical-alignment-manager]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  - metrics:connectwise-manage-inspector:agreements-active-count
  - metrics:connectwise-manage-inspector:agreements-expiring-count
  - metrics:connectwise-manage-inspector:agreements-without-member-count
  - metrics:connectwise-manage-inspector:members-billable-utilization-pct
  - metrics:connectwise-manage-inspector:members-total-count
  - metrics:connectwise-manage-inspector:sla-breached-count
  - metrics:connectwise-manage-inspector:sla-resolution-compliance-pct
  - metrics:connectwise-manage-inspector:sla-response-compliance-pct
  - metrics:connectwise-manage-inspector:tickets-aging-by-bracket
  - metrics:connectwise-manage-inspector:tickets-avg-time-to-close
  - metrics:connectwise-manage-inspector:tickets-open-by-priority
  - metrics:connectwise-manage-inspector:tickets-open-count
  - metrics:connectwise-manage-inspector:time-entries-total-count
---

# Single-System Analysis — ConnectWise Manage

> **Inspector:** `connectwise-manage-inspector` (ID 9). Apps & Services
> category. **One system per ConnectWise Manage tenant.** PSA platform —
> the system of record for tickets, time entries, agreements, and
> billing.
>
> **References:** `reference/inspector-aliases.md` (CW Manage, CWM,
> Manage). Pairs with `recipes/single-system-analysis/by-inspector/connectwise-automate.md`
> for the RMM ↔ PSA integration story.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-cw-manage-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  ticket_volume: "Ticket Volume & Trend"
  ticket_aging: "Ticket Aging"
  sla_compliance: "SLA Compliance"
  technician_utilization: "Technician Utilization"
  time_tracking: "Time-Tracking Accuracy"
  agreements: "Agreement Audit"
  customer_profile: "Per-Customer Ticket Profile"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  ticket_age_warn_days: 7                # tickets open > N days = aging finding
  ticket_age_critical_days: 30
  sla_compliance_pct_min: 95
  technician_utilization_target_pct: 70  # billable utilization target
  time_entry_lag_days_max: 2             # time entries should be entered within N days
  agreement_expiration_warn_days: 60
  agreement_without_member_max: 0        # agreements without technicians assigned

reporting_period:
  default: "last_quarter"                # ticket / time data is time-series — quarterly default

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

- "CW Manage posture for <customer>" (internal MSP-operations review)
- "Ticket aging — what's slipping?"
- "SLA compliance for <customer>"
- "Technician utilization for the period"
- "CW Manage agreement audit — renewals + assignments"
- "Per-customer ticket profile for <customer>"

Cadence: monthly per MSP (internal operational review); quarterly in
the customer-facing PBR (per-customer ticket profile only — internal
operational metrics stay internal).

Personas:
- **vCIO / Account Manager** (primary — per-customer ticket profile
  in PBR, agreement-renewal cadence)
- **Accounting / Finance** (primary — time-tracking accuracy,
  agreement billing, contract expiration)
- **NOC** (operational — ticket aging, SLA breach triage)
- **TAM** (technician utilization, time-entry compliance with MSP
  standards)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the CW Manage tenant) | Yes | `liongard_system LIST query="connectwise-manage"` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="connectwise-manage"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Ticket volume + aging

```
liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative:
#   "cw-manage.tickets.openCount"
#   "cw-manage.tickets.openByPriority"        (priority distribution)
#   "cw-manage.tickets.openByBoard"           (per service board)
#   "cw-manage.tickets.openByCompany"         (per customer)
#   "cw-manage.tickets.openByOwner"           (per technician)
#   "cw-manage.tickets.agingByBracket"        ([0-1d, 1-7d, 7-30d, 30+d])
#   "cw-manage.tickets.closedLast30Days"
#   "cw-manage.tickets.reopenedLast30Days"
#   "cw-manage.tickets.avgTimeToClose"
```

### Step 4 — SLA compliance

```
#   "cw-manage.sla.responseCompliancePct"
#   "cw-manage.sla.resolutionCompliancePct"
#   "cw-manage.sla.breachedCount"
#   "cw-manage.sla.byBoard"                  (compliance per service board)
#   "cw-manage.sla.byPriority"
```

### Step 5 — Technician utilization

```
#   "cw-manage.members.totalCount"
#   "cw-manage.members.activeCount"
#   "cw-manage.members.byRole"
#   "cw-manage.members.billableUtilizationPct"   (per member)
#   "cw-manage.members.timeEntriesLast30Days"
#   "cw-manage.members.assignedTicketsByMember"
```

### Step 6 — Time-tracking accuracy

```
#   "cw-manage.timeEntries.totalCount"
#   "cw-manage.timeEntries.byEntryLagDays"   (when entered vs work date)
#   "cw-manage.timeEntries.missingTimesheet"
#   "cw-manage.timeEntries.notInvoiced"
#   "cw-manage.timeEntries.zeroDurationCount"
```

### Step 7 — Agreement audit

```
#   "cw-manage.agreements.activeCount"
#   "cw-manage.agreements.byType"
#   "cw-manage.agreements.expiringWithinWarnDays"
#   "cw-manage.agreements.withoutAssignedMember"
#   "cw-manage.agreements.expiredCount"
#   "cw-manage.agreements.totalContractedHoursPerMonth"
```

### Step 8 — Per-customer ticket profile (for PBR)

```
#   "cw-manage.tickets.byCompanyLast90Days"
#   "cw-manage.tickets.topCompaniesByVolume"
#   "cw-manage.tickets.reopenedByCompany"
#   "cw-manage.tickets.avgCloseTimeByCompany"
```

Surface for each top customer: ticket volume trend, reopen rate, average
close time, agreement coverage status.

### Step 9 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on retry, freshness, proposed-metric gaps. Privacy: per-technician
utilization is sensitive — keep `audience.tone: "executive"` outputs
aggregated; per-technician detail stays internal.

### Step 10 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | PSA is operational tooling, not endpoint coverage; the six standard endpoint questions don't apply. |
| CIS Controls (v8.1) | ⚠️ | Indirect mapping to CIS 8.2 (audit logs of PSA technician actions), 6.4 (CW Manage user MFA). PSA isn't a primary CIS-control source. |
| Cyber-insurance domain files | n/a | PSA operational data not typically required for cyber-insurance evidence. |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this when CW Manage is the customer's PSA; surfaces per-customer ticket profile, SLA compliance, agreement expiration for the AM's renewal conversation. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| High aged-ticket count | "<N> tickets aged > <N> days. Triage backlog; reassign or escalate." |
| SLA compliance below threshold | "Response SLA at <N>%, resolution SLA at <N>%. Review breached tickets by board / priority." |
| Technician utilization below target | "Member <X> at <N>% billable utilization — confirm time entries are flowing correctly." |
| Time-entry lag high | "<N> time entries entered > <N> days late. Reinforce daily-entry policy." |
| Agreement expiring < warn | "<N> agreements expire within <N> days. Initiate renewal conversations." |
| Agreement without assigned member | "<N> agreements lack technician assignment. Assign per agreement type." |
| Reopen rate high (per customer) | "Customer <C> has <N>% reopen rate. Triage common root cause; potential standard-build issue." |
| Top customer volume divergence | "Customer <C> ticket volume up <N>% over prior quarter. Surface in AM conversation." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Ticket content / resolution notes | not in dataprint | CW Manage Console |
| Per-ticket profitability (effort vs. agreement coverage) | partial | CW Manage Console + accounting |
| Per-customer satisfaction / NPS | external | NPS / survey tool — see `recipes/external-data/client-surveys-nps.md` |
| Quote / opportunity pipeline | partial | CW Manage Sell module |
| Procurement / project hours | partial | CW Manage project module |

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

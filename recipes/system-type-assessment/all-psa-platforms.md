---
name: system-type-all-psa-platforms
description: >
  Use this skill when the user wants a unified PSA-platform assessment
  across all PSA tenants in an environment — ConnectWise Manage,
  Autotask, HaloPSA, Kaseya BMS, Syncro. Trigger phrases: "PSA posture
  for <customer>", "all PSA platforms", "PSA sprawl audit", "PSA
  consolidation candidate", "ticket aging across PSAs", "PSA contract
  expiration rollup", "MSP operational health".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric"
personas: [vcio-account-manager, accounting-finance, noc, technical-alignment-manager]
output_formats: [pptx, word, xlsx, markdown]
primitives:
  - metrics:autotask-inspector:accounts-active-count
  - metrics:autotask-inspector:accounts-inactive-count
  - metrics:autotask-inspector:accounts-total-count
  - metrics:autotask-inspector:contacts-active-count
  - metrics:autotask-inspector:contacts-primary-count
  - metrics:autotask-inspector:contacts-total-count
  - metrics:autotask-inspector:unique-composite-key
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
  - metrics:halopsa-inspector:agents-active-count
  - metrics:halopsa-inspector:agents-total-count
  - metrics:halopsa-inspector:contracts-active-count
  - metrics:kaseya-bms-inspector:users-total-count
  - metrics:syncro-inspector:users-total-count
---

# System-Type Assessment — All PSA Platforms

> Unified PSA posture across every PSA inspector deployed at the MSP.
> Most healthy MSPs run **one PSA**; this rollup surfaces sprawl
> (a common acquisition / migration artifact) and produces the
> consolidated ticket / SLA / utilization / contract view.
>
> **Note:** This rollup is **MSP-internal operational**, not customer-
> facing. The per-PSA singles already produce per-customer profiles
> for the QBR. This rollup tells the MSP its own operational health.
>
> **PSA inspectors covered:**
>
> | Inspector | Recipe |
> |---|---|
> | ConnectWise Manage | `recipes/single-system-analysis/by-inspector/connectwise-manage.md` |
> | Autotask | `recipes/single-system-analysis/by-inspector/autotask.md` |
> | HaloPSA | `recipes/single-system-analysis/by-inspector/halopsa.md` |
> | Kaseya BMS | `recipes/single-system-analysis/by-inspector/kaseya-bms.md` |
> | Syncro (PSA + RMM hybrid) | `recipes/single-system-analysis/by-inspector/syncro.md` |
>
> **References:** `reference/qa-retry-pattern.md`;
> `reference/inspector-aliases.md`. Pairs with
> `recipes/system-type-assessment/all-rmm-platforms.md` for the
> complete operational tooling story.

---

## Customize for your MSP

```yaml
output:
  format: pptx
  filename: "<msp>-psa-posture-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  cover: "PSA Posture Assessment"
  executive_summary: "Executive Summary"
  psa_inventory: "PSA Platforms in Use"
  ticket_rollup: "Ticket Volume + Aging (Reconciled)"
  sla_rollup: "SLA Compliance"
  utilization_rollup: "Technician / Resource Utilization"
  time_billing_rollup: "Time & Billing Hygiene"
  contracts_rollup: "Contract Expiration Calendar"
  consolidation_opportunity: "PSA Consolidation Opportunity"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Manual Verification"
  appendix: "Appendix — Per-PSA Detail"
  verification_log: "Verification Log"

audience: { tone: "balanced" }

slas:
  ticket_age_warn_days: 7
  ticket_age_critical_days: 30
  sla_compliance_pct_min: 95
  technician_billable_utilization_target_pct: 70
  time_entry_lag_days_max: 2
  contract_expiration_warn_days: 60
  psa_consolidation_target: 1            # MSP standard: exactly one PSA
                                         # > 1 = consolidation candidate

reporting_period:
  default: "last_quarter"

stack:
  auto_discover: true
  inspectors_in_scope: []
  inspectors_to_skip: []

qa:
  retry_on_null: true
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: false
  surface_single_source_visibility: true
  manual_verification_section_required: true
```

---

## When to use

- "PSA posture for the MSP" (internal operational review)
- "All PSA ticket aging — what's slipping?"
- "PSA consolidation candidate analysis"
- "Contract expiration calendar across PSAs"
- "Time-entry hygiene across PSA platforms"

Cadence: monthly per MSP (internal); ad-hoc during migration /
consolidation projects.

Personas:
- **vCIO / Account Manager** (consolidation business case;
  contract-renewal cadence)
- **Accounting / Finance** (primary — time/billing hygiene,
  contract expiration calendar, recurring-invoice audit)
- **NOC** (operational — aged-ticket rollup, SLA breach triage)
- **TAM** (technician utilization, time-entry policy compliance)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes (typically the MSP's own operational environment) | `liongard_environment LIST` |

---

## Workflow

### Step 1 — Scope + PSA discovery

```
liongard_environment LIST searchMode=keyword query="<MSP-or-customer>"

# Discover deployed PSAs
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="connectwise-manage"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="autotask"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="halopsa"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="kaseya-bms"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="syncro"
```

Per-PSA deployment table. If more than
`slas.psa_consolidation_target` (default 1) PSAs deployed,
surface as a **consolidation candidate**.

### Step 2 — Inspector freshness across all PSAs

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Per-PSA chained findings

For each deployed PSA, chain the per-vendor single. Extract:
- Open ticket count + aging bracket
- SLA compliance %
- Technician utilization
- Contract expiration calendar

### Step 4 — Reconciled ticket rollup

Aggregate across PSAs:
- Total open tickets (reconciled — should align across PSAs in a
  consolidation scenario)
- Aged-ticket count by bracket (0-1d, 1-7d, 7-30d, 30+d)
- Average time-to-close (weighted across PSAs)
- Per-customer ticket volume (when same customer spans 2+ PSAs —
  migration leftover)

### Step 5 — SLA rollup

Per-PSA + reconciled SLA compliance:
- Response SLA % per PSA + reconciled
- Resolution SLA % per PSA + reconciled
- Breached ticket count

### Step 6 — Utilization rollup

Per-PSA + total:
- Active technician count
- Average billable utilization %
- Flag technicians appearing in multiple PSAs (license overlap)

### Step 7 — Time + billing hygiene

Per-PSA + total:
- Time entries entered > `slas.time_entry_lag_days_max` late
- Time entries missing timesheet / not approved
- Time entries not invoiced

### Step 8 — Contract / agreement / recurring-invoice expiration calendar

Per-PSA + consolidated:
- Active contracts / agreements / recurring invoices
- Expiring within `slas.contract_expiration_warn_days`
- Without assigned member / technician
- Total contracted hours / recurring revenue per month

> **The consolidated contract calendar is the rollup's most-
> differentiated section.** MSPs with multiple PSAs often have
> contracts in each (migration leftover). The consolidated calendar
> exposes upcoming renewals across the whole portfolio.

### Step 9 — PSA-user MFA audit

```
For each PSA: users.totalCount + users.mfaEnabledCount
Aggregate to: total PSA users, MFA coverage %, list of MFA-less users
```

> Same elevated MFA stance as RMM rollup — PSA accounts are high-value
> targets (Kaseya 2021 incident).

### Step 10 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on:
1. Retry persistent nulls per PSA.
2. Stale-inspector flags propagate per PSA.
3. **Cross-PSA ticket overlap** (same customer in 2+ PSAs) = expected
   during migration; surface as a sprawl finding.
4. **PSA-user MFA verification** elevated.
5. **Privacy** — per-technician utilization is sensitive; keep
   executive output aggregated.

### Step 11 — Render

Recommended slide / page order for pptx:

| # | Slide | Content |
|---|---|---|
| 1 | Cover | MSP, period |
| 2 | Executive Summary | Headline + consolidation candidate flag |
| 3 | PSA Platforms in Use | Per-PSA deployment table |
| 4 | Ticket Volume + Aging (Reconciled) | Aggregated view |
| 5 | SLA Compliance | Per-PSA + reconciled |
| 6 | Technician Utilization | Aggregated |
| 7 | Time & Billing Hygiene | Late entries, unbilled, etc. |
| 8 | Contract Expiration Calendar | The Step 8 consolidated view |
| 9 | PSA-user MFA Audit | The Step 9 finding |
| 10 | Consolidation Opportunity | Recommended target + migration plan |
| 11 | Recommendations | Prioritized actions |
| 12 | Data Gaps | Step 10 manual-verification appendix |

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | PSA operational tooling; endpoint-question matrix doesn't apply. Syncro's RMM side is covered by the RMM rollup. |
| CIS Controls (v8.1) | ⚠️ | Indirect: CIS 8.2 (PSA audit logs across platforms), 6.4 (PSA-user MFA — elevated). |
| Cyber-insurance domain files | n/a | PSA operational data. |
| QBR / quarterly-business-review | n/a | This rollup is MSP-internal; the per-PSA singles produce the QBR per-customer profiles. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| Multiple PSAs deployed | "MSP uses <N> PSA platforms. Consolidation candidate — recommended target is <MSP standard>." |
| Reconciled aged-ticket count high | "<N> tickets aged > <N> days across all PSAs. Triage." |
| Reconciled SLA below threshold | "Reconciled SLA at <N>%. Review breached tickets by board / priority." |
| Customer in 2+ PSAs | "Customer <C> exists in <N> PSAs. Consolidate to a single source of record." |
| Reconciled utilization below target | "Average technician utilization <N>%. Review time-entry flow." |
| Contracts expiring across PSAs | "<N> contracts expire within <N> days across portfolio." |
| Time-entry lag high | "<N> entries > <N> days late across PSAs." |
| **PSA user without MFA** | "URGENT: Enforce MFA on <N> PSA users across <PSAs>. High-value target." |
| Overlapping technician licenses | "Same technician licensed in <N> PSAs. Consolidate." |

---

## Data gaps & coverage notes

Inherits per-PSA data gaps. Rollup-specific:

| Field | Status | Source if missing |
|---|---|---|
| Cross-PSA workflow / automation parity | external | Per-PSA consoles |
| Migration-effort estimation | external | MSP engineering capacity planning |
| PSA ↔ RMM integration health (per pair) | partial | Per-tool consoles |
| Profitability per customer (cross-PSA join) | external | MSP accounting |

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST + liongard_system LIST | per-PSA queries | array<system> | ok per PSA |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3 | (chain per-PSA singles) | per single-system recipe | per-recipe findings | ok per PSA |
| 4-9 | (per-area rollups — derived) | per slas | aggregations | ok |
| 10 | QA pass | per `reference/qa-retry-pattern.md` | varies | ok |
| 11 | render | per `output.format` | <artifact path> | ok |
```

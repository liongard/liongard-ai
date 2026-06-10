---
name: single-system-autotask
description: >
  Use this skill when the user wants a single-system analysis of an
  Autotask PSA tenant. The Dev MCP dataprint currently supports
  tenant-level company/account and contact inventory; ticket volume,
  SLA, resource utilization, time-entry, billing, contract, and project
  analysis must be marked as manual gaps unless those collections appear
  in the tenant dataprint. Trigger phrases: "Autotask review",
  "AT posture for <customer>", "Autotask company inventory",
  "Autotask contact inventory", "Datto Autotask PBR".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_launchpoint, liongard_metric, liongard_timeline"
personas: [vcio-account-manager, accounting-finance, noc, technical-alignment-manager]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  - metrics:autotask-inspector:accounts-active-count
  - metrics:autotask-inspector:accounts-inactive-count
  - metrics:autotask-inspector:accounts-total-count
  - metrics:autotask-inspector:contacts-active-count
  - metrics:autotask-inspector:contacts-primary-count
  - metrics:autotask-inspector:contacts-total-count
  - metrics:autotask-inspector:unique-composite-key
---

# Single-System Analysis — Autotask

> **Inspector:** `autotask-inspector` (ID 45). Apps & Services
> category. **One system per Autotask tenant.** Datto-owned PSA —
> closely integrated with Datto RMM and Datto BCDR.
>
> **References:** `reference/inspector-aliases.md` (AT, Autotask).
> Pairs with `datto-rmm.md` and `datto-bcdr.md` for the Datto-stack
> integration story.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-autotask-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  ticket_volume: "Ticket Volume & Trend"
  ticket_aging: "Ticket Aging"
  sla_compliance: "SLA Compliance"
  resource_utilization: "Resource Utilization"
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
  resource_billable_utilization_target_pct: 70
  time_entry_lag_days_max: 2
  contract_expiration_warn_days: 60
  contract_without_resource_max: 0

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

- "Autotask posture review"
- "Autotask ticket aging"
- "Autotask SLA compliance"
- "Autotask resource utilization for the period"
- "Autotask contract audit — renewals + assignments"
- "Per-customer ticket profile from Autotask"

Cadence: monthly per MSP; quarterly for PBR customer-profile section.

Personas:
- **vCIO / Account Manager** (primary — per-customer profile, contract renewals)
- **Accounting / Finance** (primary — time + billing accuracy, contract expirations)
- **NOC** (operational — ticket aging, SLA breach triage)
- **TAM** (resource utilization, time-entry policy compliance)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the Autotask tenant) | Yes | `liongard_launchpoint LIST environmentIds=[<ENV_ID>] inspectorId=45` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_launchpoint LIST environmentIds=[<ENV_ID>] inspectorId=45
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

Check the launchpoint `status`, `daysSinceLastInspection`, and timeline
before interpreting any metric. The Dev MCP sample included one empty
dataprint for a `Setup Issue` launchpoint and one populated parent
dataprint for a `Platform Failure` launchpoint.

### Step 3 — Validate dataprint shape

```
liongard_metric EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID> jmesPathQuery="keys(@)"
```

Validated parent-dataprint keys in the Dev MCP sample:

```
["Accounts", "Contacts", "Discovered", "UniqueCompositeKey"]
```

No child Autotask dataprints were observed in the Dev MCP sample. Treat
all validated paths below as parent-dataprint paths.

### Step 4 — Company / account inventory

Use direct JMESPath evaluation or the global catalog metric by name.

```
liongard_metric EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID> jmesPathQuery="length(Accounts)"
liongard_metric EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID> jmesPathQuery="length(Accounts[?Active == `true`])"
liongard_metric EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID> jmesPathQuery="length(Accounts[?Active == `false`])"
```

Validated account fields include:

```
Accounts[].id
Accounts[].AccountName
Accounts[].AccountType
Accounts[].Active
Accounts[].OwnerResourceID
Accounts[].ClientPortalActive
Accounts[].LastActivityDate
Accounts[].LastTrackedModifiedDateTime
Accounts[].UserDefinedFields
```

Metric catalog notes:
- Global catalog metric **"Autotask: Company Count"** (`length(Accounts)`) may return no historical rows in some environments; fall back to direct `jmesPathQuery="length(Accounts)"` if the catalog metric returns empty.
- Do not use [metric 100034 not in global catalog] (query is `NA`).

### Step 5 — Contact inventory

```
liongard_metric EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID> jmesPathQuery="length(Contacts)"
liongard_metric EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID> jmesPathQuery="length(Contacts[?Active == `1`])"
liongard_metric EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID> jmesPathQuery="length(Contacts[?PrimaryContact == `true`])"
```

Validated contact fields include:

```
Contacts[].id
Contacts[].AccountID
Contacts[].Active
Contacts[].PrimaryContact
Contacts[].CreateDate
Contacts[].LastActivityDate
Contacts[].LastModifiedDate
Contacts[].UserDefinedFields
```

Do not print or export contact names, email addresses, phone numbers, or
street addresses unless the user explicitly requests a contact export and
confirms the audience. For normal reviews, aggregate counts are enough.

### Step 6 — Tenant identity

```
liongard_metric EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID> jmesPathQuery="UniqueCompositeKey"
```

Use this only to confirm that the dataprint belongs to the expected
Autotask tenant. Avoid including the full value in client-facing output.

### Step 7 — Manual operational gaps

The following analysis areas are not backed by validated Dev MCP
dataprint paths for inspector `45` unless the tenant exposes additional
collections. Do not invent metrics for these sections.

| Area | Invalid / absent collection in Dev MCP sample | Required source |
|---|---|---|
| Ticket volume, queues, priorities, aging, reopen rate | `Tickets` | Autotask Console / export |
| SLA response and resolution compliance | `Tickets`, SLA rollup collections | Autotask Console / reports |
| Resource utilization and billable targets | `Resources`, `TimeEntries` | Autotask Console / finance report |
| Time-entry lag, approval, invoicing | `TimeEntries` | Autotask Console / finance report |
| Contract counts, expiration, assigned resources | `Contracts` | Autotask Console / contract report |
| Project module detail | `Projects` | Autotask Console / project report |
| Configuration items | `ConfigurationItems` | Autotask Console or integrated asset source |

If one of these collections appears in a future dataprint, first validate
the exact JMESPath with `liongard_metric EVALUATE` against that system,
then add the path and evidence note to this recipe.

### Step 8 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on retry, freshness, launchpoint status, and proposed-metric gaps.
Per-contact detail stays internal.

### Step 9 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | PSA operational tooling — endpoint-question matrix doesn't apply. |
| CIS Controls (v8.1) | ⚠️ | Indirect: CIS 8.2 (PSA audit logs), 6.4 (Autotask user MFA). |
| Cyber-insurance domain files | n/a | PSA operational data not typically required for cyber-insurance evidence. |
| QBR / quarterly-business-review | ✅ | QBR Step 8 can chain this when Autotask is the customer's PSA; MCP-backed output is company/contact inventory and coverage gaps unless additional tenant collections are validated. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| Empty or stale Autotask dataprint | "Autotask launchpoint is not producing current data. Fix inspection status before using PSA metrics in reporting." |
| Company/account inventory available | "Autotask contains <N> active companies/accounts. Use this as the MCP-backed tenant inventory baseline." |
| Inactive company/account count above zero | "Autotask contains <N> inactive companies/accounts. Confirm whether inactive records should be excluded from reporting and billing workflows." |
| Primary contact coverage | "Autotask contains <N> primary contacts. Validate primary-contact coverage in the Autotask console before client communication workflows rely on it." |
| Operational PSA metrics requested | "Ticket, SLA, resource, time-entry, contract, and project metrics are not present in the validated Liongard Autotask dataprint. Attach Autotask console reports for those sections." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Company/account count | validated parent dataprint | `length(Accounts)` or [metric 66404 not in global catalog] |
| Active company/account count | validated parent dataprint | ``length(Accounts[?Active == `true`])`` |
| Contact count | validated parent dataprint | `length(Contacts)` |
| Primary contact count | validated parent dataprint | ``length(Contacts[?PrimaryContact == `true`])`` |
| Tenant identity | validated parent dataprint | `UniqueCompositeKey` |
| Ticket content / resolution notes | not in Dev MCP dataprint | Autotask Console |
| Ticket volume / aging / reopen rate | not in Dev MCP dataprint | Autotask Console / export |
| SLA compliance | not in Dev MCP dataprint | Autotask Console / reports |
| Resource utilization | not in Dev MCP dataprint | Autotask Console / finance report |
| Time entry / billing accuracy | not in Dev MCP dataprint | Autotask Console + accounting |
| Contract audit | not in Dev MCP dataprint | Autotask Console / contract report |
| Per-customer NPS / satisfaction | external | `recipes/external-data/client-surveys-nps.md` |
| Project module deep detail | not in Dev MCP dataprint | Autotask Console |
| Procurement / quotes | not in Dev MCP dataprint | Autotask Console |

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST + liongard_launchpoint LIST | `inspectorId=45` | array | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3 | liongard_metric EVALUATE | `jmesPathQuery="keys(@)"` | `["Accounts","Contacts","Discovered","UniqueCompositeKey"]` | validated parent dataprint |
| 4 | liongard_metric EVALUATE | `jmesPathQuery="length(Accounts)"` | number | VALIDATED — use direct JMESPath or metricName="Autotask: Company Count" |
| 5 | liongard_metric EVALUATE | `jmesPathQuery="length(Contacts)"` | number | validated parent dataprint |
| 6 | liongard_metric EVALUATE | `jmesPathQuery="UniqueCompositeKey"` | string | validated parent dataprint |
| 7 | manual gap check | `Tickets`, `Resources`, `TimeEntries`, `Contracts`, `Projects`, `ConfigurationItems` | absent/null in Dev MCP sample | manual source required |
| 8 | QA pass | per `reference/qa-retry-pattern.md` | varies | ok |
| 9 | render | per `output.format` | <artifact path> | ok |
```

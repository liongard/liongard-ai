---
name: single-system-connectwise-asio
description: >
  Use this recipe when the user wants a single-system analysis of a
  ConnectWise Asio RMM account — managed company inventory, site and device
  counts, child-system discovery, and activity-status audit. Trigger phrases:
  "ConnectWise Asio report for <customer>", "ConnectWise RMM review",
  "Asio company inventory", "ConnectWise Asio device coverage", "CW Asio
  posture for <MSP>", "ConnectWise Asio managed-company audit". One system
  per ConnectWise Asio MSP account (parent); child systems are auto-discovered
  per managed company.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_launchpoint, liongard_metric, liongard_timeline"
inspector_id: 103
inspector_name: "ConnectWise Asio"
category: RMM
personas: [noc, technical-alignment-manager, vcio-account-manager, accounting-finance]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  - metrics:connectwise-asio-inspector:active-company-count
  - metrics:connectwise-asio-inspector:company-count
  - metrics:connectwise-asio-inspector:company-roster
  - metrics:connectwise-asio-inspector:discovered-child-count
  - metrics:connectwise-asio-inspector:discovered-children
  - metrics:connectwise-asio-inspector:zero-device-companies
---

# Single-System Analysis — ConnectWise Asio

> **Inspector:** `connectwise-asio-inspector` (ID 103). Apps & Services
> category. **Parent/child pattern.** The parent system represents the MSP's
> ConnectWise Asio account and holds the full company roster. Each managed
> company generates a corresponding **child** launchpoint (auto-discovered via
> the `Discovered[]` array). ConnectWise Asio is the unified platform launched
> by ConnectWise ca. 2022, consolidating RMM, PSA, and security tooling.
> **Credentialed** — requires an active ConnectWise Asio account.
>
> **References:** `reference/inspector-aliases.md` (ConnectWise Asio,
> ConnectWise RMM). Pairs with `connectwise-manage.md` (PSA) and
> `connectwise-automate.md` (legacy Automate RMM) for full ConnectWise stack
> coverage. Use `all-rmm-platforms.md` rollup when multiple RMMs coexist.

---

## When to use

- "ConnectWise Asio company inventory for \<MSP\>"
- "ConnectWise Asio device coverage audit"
- "ConnectWise Asio child system discovery"
- "Which companies are active in ConnectWise Asio?"
- "ConnectWise RMM managed-company report"
- Onboarding baseline (parent-company roster); quarterly account review;
  RMM-sprawl / consolidation analysis

Cadence: monthly for account-roster changes; quarterly in PBR; ad-hoc
during MSP toolstack migrations (ConnectWise Automate → Asio).

Personas:
- **NOC** (primary — company and device count baseline)
- **TAM / Technical Alignment Manager** (child-system discovery, company
  ownership type classification, site/device count drift)
- **vCIO / Account Manager** (renewal, company roster accuracy vs PSA)
- **Accounting / Finance** (seat / company count vs contract)

---

## Customize for your MSP

```yaml
output:
  format: markdown                          # markdown | word | pptx | xlsx
  filename: "<msp>-cw-asio-<date>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary:    "Executive Summary"
  company_roster:       "Managed Company Roster"
  child_discovery:      "Child System Discovery"
  device_coverage:      "Device Coverage Summary"
  activity_status:      "Company Activity Status"
  recommendations:      "Recommended Actions"
  data_gaps:            "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"                          # technical | balanced | executive

slas:
  inactive_company_flag: true              # flag companies where activityStatus.activeFlag != true
  min_devices_per_company: 1               # flag companies with DevicesCount == 0
  child_discovery_expected: true           # each company should have a child launchpoint

qa:
  retry_on_null: true
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  surface_proposed_metrics: false
  manual_verification_section_required: true
```

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System / launchpoint ID (CW Asio parent) | Yes | `liongard_launchpoint LIST inspectorId=103` |
| Optional: specific company name | No | User prompt — narrows output scope |

---

## Workflow

### Step 1 — Resolve environment + parent system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_launchpoint LIST environmentId=<ENV_ID> inspectorId=103
```

ConnectWise Asio uses a parent/child pattern. The result from
`LIST inspectorId=103` will include:
- The **parent** system (one per MSP Asio account) — contains
  `Companies[]` and `Discovered[]`
- One or more **child** systems (one per managed company) — contain
  per-company device and site detail

Run this recipe against the **parent** system to get the company roster
and child-discovery map. Run child-specific analysis by following the
child launchpoints returned in `Discovered[]`.

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

The CW Asio parent inspector syncs the company roster and discovers
child systems. A stale parent means newly added companies may not yet
have child launchpoints. Flag parent inspector last-seen >
`slas.flag_inspector_lastseen_threshold_days` days.

### Step 3 — Company roster

Use `liongard_metric GENERATE_AND_EVALUATE` for each path below.
All paths are **VALIDATED** against System A (dev environment)
(inspected 2026-05-21).

```
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  jmesPath="<path>"

# ── VALIDATED ────────────────────────────────────────────────────────

# Total managed company count
#   length(Companies)
#     → integer (e.g. 2)

# Full company roster with identity and classification
#   Companies[].{id: id,
#                name: name,
#                friendlyName: friendlyName,
#                activityStatus: activityStatus.name,
#                ownershipType: ownershipType.name,
#                sitesCount: SitesCount,
#                devicesCount: DevicesCount}
#
#   id                — string (UUID); ConnectWise Asio company identifier
#   name              — string; short company identifier (may be a code)
#   friendlyName      — string; display name (e.g. "Test 1")
#   activityStatus    — dereferenced string; confirmed values:
#                         "Active Customer"
#                         (other statuses possible per CW Asio configuration)
#   activityStatus.activeFlag (raw field) — boolean; true = active
#   ownershipType     — dereferenced string; confirmed values:
#                         "Small Business"
#                         "Public Company"
#   SitesCount        — integer; number of sites for this company
#   DevicesCount      — integer; number of devices managed for this company

# Count of active companies
#   length(Companies[?activityStatus.activeFlag == `true`])
#     → integer
#   NOTE: activityStatus is an OBJECT in the raw dataprint —
#   use activityStatus.activeFlag for boolean filter.

# Companies with zero devices (coverage gap flag)
#   Companies[?DevicesCount == `0`].{name: name, friendlyName: friendlyName}
#     → array of companies with no managed devices
```

**Company roster analysis:**

| Signal | Threshold | Severity |
|---|---|---|
| Company with `activityStatus.activeFlag != true` | Any | Warning — verify if intentional (churned client?) |
| Company with `DevicesCount == 0` | Any | Warning — no devices under management; onboarding incomplete or recently churned |
| Company count unexpectedly low vs PSA | Compare to ConnectWise Manage | Warning — company may have been removed without PSA sync |

### Step 4 — Child system discovery

```
# ── VALIDATED ────────────────────────────────────────────────────────

# Child systems auto-discovered by this parent
#   Discovered[].{EnvironmentSearch: EnvironmentSearch,
#                 Alias: Alias,
#                 Inspector: Inspector}
#
#   EnvironmentSearch — string; the environment search key (maps to company
#                       name / identifier in Liongard)
#   Alias             — string; child launchpoint display name
#                       (e.g. "ConnectWise Asio - <company_name>")
#   Inspector         — string; always "connectwise-asio-inspector"
#                       (confirms child inspector type)

# Count of discovered child systems
#   length(Discovered)
#     → integer (should equal length(Companies) when all are healthy)
```

**Child-discovery reconciliation:**

1. Count companies in `Companies[]` and children in `Discovered[]`.
2. If `length(Discovered) < length(Companies)` → some companies have no
   child launchpoint yet (parent inspector may be stale, or company was
   just added). Flag as a data gap.
3. For each child in `Discovered[]`, run `liongard_launchpoint LIST`
   scoped to the child environment to retrieve per-company device data.

### Step 5 — Device coverage summary

From the `Companies[]` query in Step 3, aggregate device counts:

```python
# Derived from VALIDATED Companies[].DevicesCount
total_devices    = sum(Companies[].DevicesCount)
zero_device_cos  = Companies[?DevicesCount == `0`]
top_companies    = sort_by(Companies, DevicesCount) | reverse[:5]
```

Report:
- Total managed device count across all companies
- Companies with zero devices (flag)
- Top 5 companies by device count (capacity context)

### Step 6 — Site coverage summary

```python
# Derived from VALIDATED Companies[].SitesCount
total_sites      = sum(Companies[].SitesCount)
zero_site_cos    = Companies[?SitesCount == `0`]
```

Companies with `SitesCount == 0` should be flagged — they either have
no sites configured or the sync is incomplete.

### Step 7 — QA pass

1. Retry any null results per `reference/qa-retry-pattern.md`.
2. Reconcile `length(Companies)` vs `length(Discovered)` — discrepancies
   indicate pending child-launchpoint creation (normal for freshly onboarded
   companies; unusual if persistent).
3. Cross-reference total `DevicesCount` against reconciled inventory from
   `liongard_asset LIST environmentId=<ENV_ID>` if available.
4. Flag any company where `activityStatus.activeFlag != true` for
   human review — CW Asio may retain churned companies in the system.

### Step 8 — Render

Recommended report structure:

| # | Section | Key Content |
|---|---|---|
| 1 | Executive Summary | Company count, total devices, active vs inactive flag |
| 2 | Managed Company Roster | Table: friendlyName, ownershipType, activityStatus, sitesCount, devicesCount |
| 3 | Child System Discovery | Map of Companies → Discovered children; gap analysis |
| 4 | Device Coverage Summary | Total devices, zero-device companies, top-5 by device count |
| 5 | Site Coverage Summary | Total sites, zero-site companies |
| 6 | Recommended Actions | Prioritised findings |
| 7 | Data Gaps | Manual-verification appendix |

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | Steps 3–4 answer managed-company roster and child-system discovery questions; Step 5 answers device-coverage baseline. |
| CIS Controls (v8.1) | ✅ | CIS 1.1/1.2 (Steps 5–6 — asset inventory via device and site counts per company), 2.1 (software inventory — available at child-system level), 6.3/6.4 (RMM-user MFA — see data gaps; verify in CW Asio console). |
| Cyber-insurance domain files | ✅ | `domains/endpoint.md` — device coverage counts; `domains/governance.md` — company-roster accuracy as vendor-management evidence. |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this for total managed-device count, company-roster accuracy vs PSA, and RMM-coverage gaps. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| Company with `DevicesCount == 0` | "Company \<friendlyName\> has zero devices under management in CW Asio. Confirm onboarding is complete or mark as excluded from device-count SLA." |
| Company count mismatch vs PSA | "CW Asio shows \<N\> companies; ConnectWise Manage shows \<M\>. Reconcile — churned customers may need removal from Asio." |
| `length(Discovered) < length(Companies)` | "\<N\> companies lack a child launchpoint. Re-run parent inspector to trigger child discovery for newly added companies." |
| Inactive company flag | "Company \<friendlyName\> has activityStatus = \<status\> (not Active Customer). Verify if intentional; remove from Asio if churned." |
| Stale parent inspector | "CW Asio parent inspector last seen \<N\> days ago. Newly added companies and site/device-count changes may not be reflected." |
| Multiple RMMs present | "Customer has CW Asio alongside another RMM platform. Consolidation candidate — surface in QBR with migration timeline." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Per-device detail (hostname, OS, patch, AV) | At child-system level | Run recipe against each child launchpoint (`Discovered[].EnvironmentSearch`) |
| RMM technician / user list | Not in parent dataprint | ConnectWise Asio console → user management |
| License seat utilization | Not in parent dataprint | ConnectWise Asio console → subscription / billing |
| Agent version per device | At child-system level | Child launchpoint dataprint |
| Alert / ticket activity | Not in parent dataprint | ConnectWise Asio console or ConnectWise Manage (PSA) |
| Patch posture | At child-system level | Child launchpoint dataprint |

---

## Verification log

| Step | Tool | Validated Path | Result Shape | Validation Status |
|---|---|---|---|---|
| 3 | liongard_metric GENERATE_AND_EVALUATE | `length(Companies)` | integer → 2 | VALIDATED (System A, dev environment, 2026-05-21) |
| 3 | liongard_metric EVALUATE | `Companies[].{id, name, friendlyName, activityStatus: activityStatus.name, ownershipType: ownershipType.name, sitesCount: SitesCount, devicesCount: DevicesCount}` | array; `activityStatus.name: "Active Customer"`, `ownershipType.name: "Small Business"\|"Public Company"`, `SitesCount`: int, `DevicesCount`: int | VALIDATED |
| 4 | liongard_metric EVALUATE | `Discovered[].{EnvironmentSearch, Alias, Inspector}` | array of 2; `Inspector: "connectwise-asio-inspector"` | VALIDATED |
| 5 | — | `sum(Companies[].DevicesCount)` | derived from VALIDATED Companies[] | DERIVED |
| 6 | — | `sum(Companies[].SitesCount)` | derived from VALIDATED Companies[] | DERIVED |

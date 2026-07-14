---
name: environment-quarterly-lookback
description: >
  Use this skill when the user wants a Periodic Business Review (PBR /
  QBR / Quarterly Business Review) or environment lookback for a
  customer — a time-bounded narrative report of what changed, what
  alerted, and what the current state is over the last 90 days, last
  quarter, last year, or since a specific date. Trigger phrases:
  "PBR for the customer", "QBR for a customer", "quarterly business
  review", "environment lookback", "what changed in the last 90 days",
  "what has happened since a specific date", "quarterly report",
  "year-end review". Auto-discovers the customer's deployed inspector
  stack and chains the appropriate per-system and system-type recipes.
  Produces a narrative report (PowerPoint executive deck + Word written
  report by default) that integrates change-detection, alerts, inspection
  timeline, cyber-risk-dashboard KPIs, and current-state inventory.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_timeline, liongard_cyber_risk_dashboard, liongard_device, liongard_identity, liongard_domain, liongard_detection, liongard_alert, liongard_metric"
personas: [vcio-account-manager, executive, noc, soc, technical-alignment-manager, accounting-finance]
output_formats: [pptx, word, markdown, xlsx]
primitives: []
composes:
  - recipe:single-system:single-system-active-directory
  - recipe:single-system:single-system-knowbe4
  - recipe:single-system:single-system-microsoft-365
  - recipe:system-type:system-type-all-backups
  - recipe:system-type:system-type-all-domains
  - recipe:system-type:system-type-all-edrs
  - recipe:system-type:system-type-all-external-attack-surface
  - recipe:system-type:system-type-all-firewalls
  - recipe:system-type:system-type-all-hypervisors
  - recipe:system-type:system-type-all-servers
---

# Environment Quarterly Lookback — Master Recipe (PBR / QBR)

> **The canonical Periodic Business Review.** A time-bounded narrative
> report that answers: *"What material changes, alerts, inventory have
> happened over the last 90 days / 3 months / since X date?"* — and
> couples that with a current-state snapshot, recommended actions,
> and an executive-friendly summary.
>
> **Customer-stack-adaptive.** The recipe doesn't assume what's
> deployed. It calls `liongard_system LIST` to discover the inspector
> stack in the environment, then chains the appropriate per-system or
> per-system-type recipes for what it finds.
>
> **References:** `reference/cross-cutting-signals.md` (the 10-step
> cross-cutting workflow, MCP tool table, time-window math),
> `reference/asset-fields.md` (the reconciled-asset-inventory tools),
> `reference/qa-retry-pattern.md` (the QA pass), `reference/inspector-aliases.md`
> (translating user shorthand to inspector slugs),
> `reference/personas-recipe-matrix.md` (which audience consumes which
> section).


---

## Customize for your MSP

```yaml
output:
  format: pptx                          # pptx | word | markdown | xlsx
                                         # Default: executive deck. Use word for the
                                         # written report; xlsx for the data appendix;
                                         # markdown for working drafts.
  filename: "<customer>-PBR-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  cover: "Quarterly Business Review"
  executive_summary: "Executive Summary"
  headline_kpis: "Headline KPIs"
  material_changes: "What Changed This Quarter"
  alerts: "Alert Activity"
  current_state: "Current State"
  per_class_sections: "Per-System Highlights"        # auto-generated per deployed inspector class
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Manual Verification"
  appendix: "Appendix — Methodology"
  verification_log: "Verification Log"               # technical readers only

audience:
  tone: "executive"                      # technical | balanced | executive
                                         # Default executive — PBR audience is customer
                                         # leadership. Override to balanced for the
                                         # internal vCIO-prep version.
  reading_level: "executive"

reporting_period:
  default: "last_quarter"                # last_30_days | last_90_days | last_quarter
                                         # | last_year | since_date | custom
  fiscal_year_start_month: 1             # 1 = Jan; override for customer's fiscal year
  since_date: ""                         # ISO date — only used when default == "since_date"
  custom_start: ""                       # ISO date — only used when default == "custom"
  custom_end: ""                         # ISO date — only used when default == "custom"

stack:
  # Auto-discover by default. Manual overrides for scoping.
  auto_discover: true
  inspectors_in_scope: []                # explicit list overrides auto-discovery
  inspectors_to_skip: []                 # exclusions from auto-discovery

per_class_recipe_overrides:
  # Map an inspector slug or system-type rollup to a custom recipe
  # path. Defaults to library recipes when not overridden.
  # cisco-meraki-inspector: "<msp-local>/meraki-custom.md"

slas:
  # Used for flagging / status icons in the headline KPI dashboard.
  inspector_lastseen_days_max: 7
  mfa_coverage_pct_min: 95
  edr_coverage_pct_min: 95
  unprotected_servers_max: 0
  patch_age_days_max: 30
  license_expiration_warn_days: 60
  alert_resolution_target_hours: 24
  detections_per_window_warn_threshold: 50    # high detection count = environment instability

narrative:
  # Tone settings for the recipe's narrative sections
  lead_with_outcomes: true               # "most users are protected" not "94/100 users have MFA"
  surface_no_op_categories: true         # "Network: no material changes this quarter" reads as reassurance
  group_recommendations_by_priority: true
  include_year_over_year_comparison: false    # set true for annual-review variant

verification:
  log_queries: true
  redact_values: true

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

- "PBR for the customer" (Periodic Business Review)
- "QBR for <customer>" (Quarterly Business Review)
- "What changed in the last 90 days for <customer>"
- "Quarterly report for <customer>"
- "Year-end review for <customer>"
- "Environment lookback since <date>"
- "Has anything material changed since the last review?"

Cadence: quarterly (most common); annual for year-end review; on-demand
for incident retrospectives.

Personas:
- **vCIO / Account Manager** (primary author + presenter)
- **Executive** (the customer's leadership — the consumer of the deck)
- **NOC / SOC / TAM** (read for operational + security context)
- **Accounting / Finance** (cares about license-renewal section)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` → match by name |
| Reporting period | No (default from customization block) | User prompt |
| Customer name | No | Used for filename + report header |
| Optional: focus areas | No | User prompt — e.g., "focus on backup posture this quarter" |

---

## Workflow — the cross-cutting 10-step pattern

This recipe is the **canonical implementation** of the cross-cutting
pattern documented in `reference/cross-cutting-signals.md`. Other
cross-cutting recipes (onboarding, roadmap, sales, CMMC) inherit the
same shape with purpose-specific variations.

### Step 1 — Scope discovery

```
liongard_environment LIST searchMode=keyword query="<customer-name>"
# Confirm environmentId. If multi-environment customer, repeat per
# environment; final report aggregates.
```

### Step 2 — Define the time window

Compute `window_start` and `window_end` from `customization.reporting_period`:

| `default` | `window_start` | `window_end` |
|---|---|---|
| `last_30_days` | today − 30d | today |
| `last_90_days` | today − 90d | today |
| `last_quarter` | start of previous fiscal quarter | end of previous fiscal quarter |
| `last_year` | start of previous fiscal year | end of previous fiscal year |
| `since_date` | `customization.since_date` | today |
| `custom` | `customization.custom_start` | `customization.custom_end` |

Fiscal quarter / year math uses `customization.fiscal_year_start_month`
(default 1 = January).

Surface the window in the report header so consumers know the scope of
"the quarter" being reviewed.

### Step 3 — Inspection timeline + freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
                       startDate=<window_start> endDate=<window_end>
```

Identify:
- Inspectors that ran during the window — confirm data freshness
- Inspectors that didn't run — **stale-data flag** for every assertion
  about those inspectors
- Inspector reconnects / disconnects in window — narrate as
  operational changes

> **The timeline check matters more for PBR than any other recipe.**
> An executive deck built on stale data is worse than no deck. If
> coverage degraded during the window, lead with that finding.

### Step 4 — Headline KPIs (category counts) for the executive dashboard

```
liongard_cyber_risk_dashboard <metric>  environmentId=<ENV_ID>
```

The KPI dashboard slide pulls from the pre-aggregated dashboard
metrics. Typical KPIs:

| KPI | Metric (representative) | Compliant when |
|---|---|---|
| M365 users | `m365TotalUsers` | (informational) |
| AD users | `activeDirectoryTotalUsers` | (informational) |
| Workstations | `workstationTotalCount` | (informational) |
| Servers (Win + Linux + macOS) | `winServerTotalCount`, `macOSTotalCount`, plus Linux totals | (informational) |
| MFA coverage % | (dashboard metric) | ≥ `slas.mfa_coverage_pct_min` |
| EDR coverage % | (dashboard metric) | ≥ `slas.edr_coverage_pct_min` |
| Domain count | `domainAndWebsiteSecurityTotalDomains` | (informational) |
| Detections in window | computed from Step 6 | < `slas.detections_per_window_warn_threshold` |
| Alerts in window | computed from Step 7 | (narrative) |
| Inspectors current | computed from Step 3 | 100% expected |

### Step 5 — Current-state inventory snapshot

> **Reconciled asset inventory is the primary source for current-state
> counts** — dedup'd across every inspector that observed the entity.
> Per-inspector deep-dives happen in Step 8 for configuration detail.
> See `reference/asset-fields.md` § Deduplication keys (email /
> hostname-serial-MAC / domain name).

```
# Devices — reconciled across OS + EDR + RMM + AD + hypervisor
liongard_device COUNT environmentId=<ENV_ID>
liongard_device COUNT environmentId=<ENV_ID> physical=false
liongard_device LIST environmentId=<ENV_ID>
                     fields=["hostname","operatingSystem","manufacturer","serialNumber","class","role","warrantyExpiration","winElevenReady","inspectors"]

# Identities — reconciled across M365 + AD + JumpCloud + OneLogin + Duo
liongard_identity COUNT environmentId=<ENV_ID>
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true
liongard_identity COUNT environmentId=<ENV_ID> privileged=true

# Domains — reconciled across Internet Domain + M365 + Google Workspace
liongard_domain COUNT environmentId=<ENV_ID>
liongard_domain LIST environmentId=<ENV_ID>
                     maxDaysTillExpiration=<slas.license_expiration_warn_days>
                     fields=["domainName","registrar","daysTillExpiration","dmarcHealth","inspectors"]
```

Produces the current-state snapshot for the report. The
`inspectors[]` array on each record is the cross-coverage signal —
e.g., a device only in `active-directory-inspector` (no EDR / RMM) is
a coverage gap to surface in the PBR's "What changed" section.

### Step 6 — Material changes in window (the PBR's primary content)

```
liongard_detection LIST environmentId=<ENV_ID>
                        startDate=<window_start> endDate=<window_end>
```

Group detections by:
- **Severity** (critical / high / medium / low / informational)
- **System / inspector class** — where did the change occur?
- **Detection type** — config change, drift from baseline, new asset
  appeared, account state change, firewall-rule modification, etc.

For each significant category, write a 1–3-sentence narrative bullet.
Example output structure:

```
## What Changed This Quarter

### Critical / High-severity (<N> events)
- 2026-04-12 — Active Directory password policy weakened (`MinPasswordLength`
  reduced from 14 to 8). MSP recommendation: revert via GPO and notify
  customer security lead.
- 2026-04-28 — SonicWall firewall rule added permitting any-source-to-LAN
  on TCP/3389 (RDP). Recommendation: remove or restrict to admin VLAN.

### Notable but lower priority (<N> events)
- ...

### No-op categories (helpful to call out)
- Network device firmware: no changes detected. Customer remained on
  the validated firmware baseline this quarter.
```

### Step 7 — Alerts in window

```
liongard_alert LIST environmentId=<ENV_ID>
                    startDate=<window_start> endDate=<window_end>
```

Group by:
- **Severity**
- **Triage outcome** (resolved, in-progress, dismissed, escalated)
- **Mean time to resolve** if exposed
- **Recurring patterns** — same condition firing repeatedly = remediation
  candidate

### Step 8 — Auto-discover deployed inspector stack + chain sub-recipes

```
liongard_system LIST environmentId=<ENV_ID>
```

Group systems by inspector slug. For each inspector class deployed
(per `customization.stack.auto_discover` / `inspectors_in_scope` /
`inspectors_to_skip`):

| Customer has… | Recipe to chain |
|---|---|
| Windows Servers + Workstations | `recipes/system-type-assessment/all-servers.md` + `all-endpoints.md` + `all-windows-patching.md` |
| Any EDR (multiple vendors common) | `recipes/system-type-assessment/all-edrs.md` |
| Firewalls (one or multiple vendors) | `recipes/system-type-assessment/all-firewalls.md` |
| Backups (any vendor) | `recipes/system-type-assessment/all-backups.md` |
| Hypervisors | `recipes/system-type-assessment/all-hypervisors.md` |
| M365 tenant | `recipes/single-system-analysis/by-inspector/microsoft-365.md` |
| AD | `recipes/single-system-analysis/by-inspector/active-directory.md` |
| KnowBe4 | `recipes/single-system-analysis/by-inspector/knowbe4.md` |
| Domains (any) | `recipes/system-type-assessment/all-domains.md` |
| External-facing IPs + customer-facing TLS hosts + breach exposure | `recipes/system-type-assessment/all-external-attack-surface.md` (the outside-in PBR section) |
| One-off vendors not covered by a rollup | The corresponding per-vendor single-system recipe |

For each chained recipe, run with the PBR recipe's `customization`
inherited (especially `audience.tone: "executive"` and the time window).
Extract the **highlights** from each chained run — not the full output —
and roll into the "Per-System Highlights" section.

> **Don't paste each chained recipe's full output into the PBR.** The
> PBR is a summary; the per-recipe runs produce supporting detail
> that lives in the appendix or as separate working documents.

### Step 9 — QA pass (per `reference/qa-retry-pattern.md`)

This recipe's QA pass especially focuses on:

1. **Retry persistent nulls** on the cyber-risk-dashboard metrics — they
   can be transient if a dashboard refresh job is mid-run.
2. **Flag stale inspectors** from Step 3. Stale inspectors mean
   downstream assertions are out of date — every per-class section in
   Step 8 that uses a stale inspector gets a 🔍 REVIEW flag.
3. **Cross-tool divergence checks** —
   - `cyber-risk-dashboard m365TotalUsers` vs.
     `liongard_identity COUNT environmentId=<ENV_ID>` filtered to M365
   - `cyber-risk-dashboard workstationTotalCount` vs.
     `liongard_device COUNT operatingSystem="Windows" category="compute"` minus servers
   - Per-EDR per-inspector counts vs. asset-inventory device counts (the
     `all-edrs.md` rollup covers this internally; surface its conclusion
     in the PBR's data-gaps section)
4. **Proposed-metric gaps** for any inspector the PBR chained where the
   inspector's recipe carries data gap notes.
5. **Single-source visibility** — call out devices / identities only
   reported by one inspector class (no security-tool cross-confirmation).

### Step 10 — Render the time-bounded narrative

The PBR output is **narrative**, not a data dump. Recommended slide / page order:

| # | Section | Content |
|---|---|---|
| 1 | Cover | Customer, period (e.g. "Q1 2026 PBR"), MSP name + logo, date |
| 2 | Executive Summary | 3–5 outcome-language bullets. Lead with the headline story (positive or risk). |
| 3 | Headline KPIs | 4–6 KPI tiles from Step 4. Status icons + trend arrows where comparison data exists. |
| 4 | What Changed | The Step 6 detections narrative — critical first, then notable, then no-op reassurance. |
| 5 | Alert Activity | Step 7 — resolved vs. outstanding, recurring patterns, mean time to resolve. |
| 6 | Current State | Step 5 snapshot — inventory composition charts, lifecycle risks, coverage gaps. |
| 7…N | Per-System Highlights | One slide / section per deployed inspector class (Step 8 highlights). |
| N+1 | Recommended Actions | Prioritized list. Each action with owner, target date, business outcome. |
| N+2 | Data Gaps & Manual Verification | The Step 9 manual-verification appendix. |
| Last | Appendix | Methodology, full inspector list, verification log, customer-stack inventory. |

### Tone-driven adaptations

When `audience.tone == "executive"` (PBR default):
- Drop JMESPath / metric details from the body — appendix only
- Replace numeric counts with risk language where the count is small
  ("a handful of users lack MFA" instead of "7 of 124 users")
- Section headings use customer-business language, not vendor names
  ("Email Security" instead of "Microsoft 365 Conditional Access
  Policy Compliance")

When `audience.tone == "balanced"` (the internal vCIO-prep version):
- Keep the section structure but include the supporting counts +
  vendor names so the AM can answer technical-buyer questions
- Per-class sections include the relevant single-system recipe's
  highlights + a link to run the full single-system recipe for deep
  dive

When `audience.tone == "technical"`:
- All counts, vendor names, JMESPath references included
- Suitable for engineering-led customer reviews

---

## QA & Manual Verification

The Step 9 detail above is the recipe-specific QA pass. The canonical
pattern (retry-on-null, stale-flag thresholds, cross-tool divergence,
proposed-metric gap surfacing) lives in
`reference/qa-retry-pattern.md`. Every customer's PBR run produces a
**Manual Verification Needed** appendix in the deliverable per that
pattern — even if empty (in which case the appendix explicitly says
"✅ All evidence verified — no manual checks needed").

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | QBR Step 3 cross-references the onboarding baseline from day zero. Every QA coverage question resurfaces as a "did it improve?" signal — MFA %, EDR coverage, patch age, backup success rate, open-port count. Without a complete onboarding record the trend analysis has no origin point. |
| CIS Controls (v8.1) | ✅ | Drives trend and delta reporting across the full CIS control set via the per-inspector chain. Focal controls per quarter: CIS 4.1 (config drift), 5.2/5.3 (stale + privileged-account churn), 6.3 (MFA coverage trend), 8.2 (audit-log coverage delta), 10.1 (backup success rate trend), 12.2 (firewall change delta). Control-level depth lives in the per-inspector and system-type recipes chained by Steps 5–8. |
| Cyber-insurance domain files | ✅ | QBR Step 7 chains the full cyber-insurance domain file set to produce the renewal evidence section. This recipe is the canonical runtime for generating renewal-ready documentation — when run at renewal cadence the QBR IS the annual evidence pack for carriers. |
| QBR / quarterly-business-review | n/a | This recipe IS the QBR. |

---

## Insights & recommendations — generation patterns

For each headline-KPI breach, each material change in window, and each
unresolved alert, the recipe produces a 1-line recommended action:

| Pattern | Recommendation template |
|---|---|
| MFA coverage below SLA | "Enroll <N> remaining users in MFA via <method>." |
| EDR coverage gap | "Install EDR on <N> servers / endpoints; investigate inspectors-array gap for <N> AD-only devices." |
| Critical patches pending | "Apply <N> critical patches within <SLA> days. Top exposed systems: <list>." |
| Licenses expiring < SLA | "Initiate renewal for <list> within <N> days." |
| Out-of-warranty hardware | "<N> devices out of warranty — refresh plan needed for <quarter>." |
| Win10 EOL approaching | "<N> Win10 devices on incompatible hardware — refresh roadmap required." |
| Stale inspectors | "<N> inspectors haven't reported in <N> days — confirm agent / API access." |
| Recurring alerts | "<count> alerts of pattern <X> fired this quarter — recommend remediation: <suggestion>." |
| Customer-stack drift | "Customer added <vendor> this quarter without standardization review — confirm policy alignment." |

Group recommendations by **priority** (Critical / High / Medium / Low)
when `narrative.group_recommendations_by_priority == true` (default).

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Stale inspectors in window | flagged from Step 3 | Trigger re-inspection; confirm agent / API access |
| Proposed-metric gaps in chained per-class recipes | flagged per-recipe | File a metric request with Liongard via the `liongard-metrics` skill |
| Vendor portal-only data (traffic / threat analytics) | external | The relevant vendor console |
| Restore-test history | not in dataprint | MSP runbook |
| HA-pair config drift across vendors | not in dataprint | Manual UI compare |
| Per-tenant licensing $ amounts | not in dataprint | MSP PSA / accounting system |

---

## Output format

`pptx` (default — executive deck) is the canonical deliverable.
Supplement with:

- **Word** written report — same content, prose format, for the
  customer's records
- **Excel** data appendix — the supporting tables (detections list,
  alerts list, asset inventory, recommendation tracker)
- **Markdown** working draft — useful for the AM to edit before
  generating the customer-facing pptx

See `templates/output-block-pptx.md` and `templates/output-block-word.md`
for layout conventions.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | query=<customer> | array<environment> | ok |
| 2 | (compute window) | per customization | { start, end } | ok |
| 3 | liongard_timeline LIST | envId=<ENV_ID> startDate=<window_start> endDate=<window_end> | array<timeline-entry> | ok |
| 4 | liongard_cyber_risk_dashboard | per-metric | <integer> | ok per metric |
| 5 | liongard_device / identity / domain LIST + COUNT | envId=<ENV_ID> [filters] | varies | ok |
| 6 | liongard_detection LIST | envId=<ENV_ID> startDate endDate | array<detection> | ok |
| 7 | liongard_alert LIST | envId=<ENV_ID> startDate endDate | array<alert> | ok |
| 8 | liongard_system LIST + chained sub-recipes | envId=<ENV_ID> | array<system> + per-recipe outputs | ok per class |
| 9 | QA pass | per `reference/qa-retry-pattern.md` | varies | ok |
| 10 | render | per `output.format` | <artifact path> | ok |
```

---

## Annual review variant

For year-end review (`reporting_period.default: "last_year"`):

- Set `narrative.include_year_over_year_comparison: true` — the
  recipe computes year-over-year deltas on the headline KPIs
- Section 4 ("What Changed") groups by quarter for the full year
- Section 5 ("Alert Activity") includes the annual alert-volume trend
- Section 6 ("Current State") adds a "Year-over-year" composition
  comparison

The recipe structure stays the same; the window definition + the
optional year-over-year comparison are the only knobs that change.

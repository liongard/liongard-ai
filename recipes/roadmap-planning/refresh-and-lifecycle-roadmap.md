---
name: refresh-and-lifecycle-roadmap
description: >
  Use this skill when the user wants a forward-looking refresh, lifecycle,
  end-of-life, end-of-support, warranty-expiration, or renewal roadmap for
  a customer. Forward-looking variant of the cross-cutting recipe pattern
  — answers "what hardware, software, OS, license, certificate, or domain
  is going to need money, attention, or replacement in the next 12 / 24 /
  36 months". Trigger phrases: "refresh roadmap", "lifecycle roadmap",
  "hardware refresh plan", "warranty roadmap", "renewal calendar",
  "license expiration roadmap", "Win10 EOL plan", "EOL inventory",
  "what's expiring this year for a customer", "budget planning for next
  fiscal year for a customer", "capital plan", "what needs replacement".
  Auto-discovers deployed inspectors and pulls every lifecycle signal —
  hardware warranty, OS end-of-life, firmware support, license expiration,
  certificate expiration, domain expiration — into one forward-rolling
  calendar with budget-quarter grouping. Produces an Excel renewal /
  refresh calendar plus a Word narrative budget-planning document.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_timeline, liongard_cyber_risk_dashboard, liongard_device, liongard_identity, liongard_domain, liongard_metric. liongard_detection and liongard_alert are optional context for the narrative."
personas: [vcio-account-manager, executive, accounting-finance, technical-alignment-manager, sales, noc]
output_formats: [xlsx, word, markdown, pptx]
primitives: []
composes:
  - recipe:qbr:environment-quarterly-lookback
  - recipe:system-type:system-type-all-external-attack-surface
---

# Refresh & Lifecycle Roadmap — Master Recipe

> **The canonical forward-looking lifecycle planning recipe.** Where the
> PBR is *time-bounded backward* and onboarding is *point-in-time*, this
> recipe is *time-bounded forward*. It answers: *"What's going to need
> money, attention, or replacement in the next 12 / 24 / 36 months — and
> in which budget quarter does each item land?"*
>
> **The recipe is the canonical driver of the budget conversation.** vCIO
> / AM uses it to scope renewal proposals; Accounting / Finance uses it to
> build the customer's IT capital plan; Executive consumes the rolled-up
> view as part of strategic planning.
>
> **Customer-stack-adaptive.** Calls `liongard_system LIST` to discover
> deployed inspectors, then chains the lifecycle-relevant sections of the
> appropriate per-system or per-system-type recipes. Aggregates results
> into a single forward calendar.
>
> **References:** `reference/cross-cutting-signals.md` (the cross-cutting
> workflow + MCP tool table; this recipe substitutes forward windows for
> the PBR's backward windows), `reference/asset-fields.md` (lifecycle
> fields on devices + domains), `reference/qa-retry-pattern.md`,
> `reference/inspector-aliases.md`,
> `reference/personas-recipe-matrix.md`.


---

## Customize for your MSP

```yaml
output:
  format: xlsx                           # xlsx | word | markdown | pptx
                                         # Default: renewal/refresh calendar workbook.
                                         # Use word for the budget-planning narrative;
                                         # pptx for the executive capital-plan deck;
                                         # markdown for working drafts.
  filename: "<customer>-Refresh-Roadmap-<horizon>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  cover: "Refresh & Lifecycle Roadmap"
  executive_summary: "Executive Summary"
  budget_summary: "Budget Summary by Quarter"
  hardware_refresh: "Hardware Refresh"
  os_end_of_life: "Operating System End-of-Life"
  firmware_support: "Firmware & Vendor Support"
  license_renewal: "License & Subscription Renewals"
  certificate_expiration: "Certificates & Encryption"
  domain_renewal: "Domain Renewals"
  vendor_consolidation: "Vendor Consolidation Opportunities"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Manual Verification"
  appendix: "Appendix — Methodology"
  verification_log: "Verification Log"

audience:
  tone: "balanced"                       # technical | balanced | executive
                                         # Default balanced — primary readers are vCIO/AM
                                         # planning renewals + Acct/Fin building the budget.
                                         # Override to executive for the capital-plan deck;
                                         # technical for engineering capacity planning.
  reading_level: "business-and-technical"

planning_horizon:
  forward_months: 24                     # 12 | 24 | 36 — how far forward the roadmap looks
  fiscal_year_start_month: 1             # 1 = Jan; override for customer's fiscal year
  group_by: "quarter"                    # month | quarter | half-year | year
  show_quarters_with_no_action: true     # surfaces "Q3 2027 — no scheduled actions" reassurance
  include_past_due: true                 # include items already past their EOL / expiration date
                                         # — flagged as overdue; never silently hidden

refresh_standard:
  # The MSP's documented refresh standards. Each per-class section grades
  # observed assets against these thresholds to determine "in-window".

  hardware:
    workstation_refresh_age_years: 5
    laptop_refresh_age_years: 4
    server_refresh_age_years: 7
    network_device_refresh_age_years: 7
    out_of_warranty_action: "refresh"    # refresh | extend-warranty | accept-risk
    win11_eligibility_required: true     # flag Win10 devices on Win11-incompatible hardware

  operating_systems:
    # OS EOL anchor dates the recipe uses. Update as MS / vendor announces.
    windows_10_eol: "2025-10-14"
    windows_11_eol: "2031-10-14"
    windows_server_2012_r2_eol: "2023-10-10"     # already past — flag any survivor
    windows_server_2016_eol: "2027-01-12"
    windows_server_2019_eol: "2029-01-09"
    windows_server_2022_eol: "2031-10-14"
    macos_supported_versions_min: 3              # n, n-1, n-2 by default
    rhel_supported_versions: ["8", "9"]          # MSP-supported RHEL versions
    ubuntu_lts_supported_versions: ["20.04", "22.04", "24.04"]

  licenses:
    firewall_license_renewal_warn_days: 60
    edr_license_renewal_warn_days: 60
    backup_license_renewal_warn_days: 60
    m365_renewal_warn_days: 90                   # M365 tenant renewals get more notice
    rmm_psa_renewal_warn_days: 90

  certificates:
    ssl_renewal_warn_days: 45
    s_mime_renewal_warn_days: 60
    code_signing_renewal_warn_days: 90

  domains:
    domain_renewal_warn_days: 60
    registrar_lock_required: true                # flag any unlocked + auto-renew-off domain

  firmware:
    firewall_firmware_age_days_max: 180          # vendor-supported firmware track
    switch_firmware_age_days_max: 365
    hypervisor_patch_currency_days_max: 90

stack:
  auto_discover: true
  inspectors_in_scope: []
  inspectors_to_skip: []

per_class_recipe_overrides:
  # cisco-meraki-inspector: "<msp-local>/meraki-roadmap-custom.md"

vendor_replacement_preferences:
  # INHERITS from config/msp-config.yaml `preferred_stack` block
  # (workstation_oem, laptop_oem, server_oem, firewall, switch,
  # ssl_certificate_authority). Override per-deliverable ONLY when a
  # specific customer engagement requires a different replacement
  # vendor than the MSP's standard. To override, uncomment + set values:
  #
  # workstation: "<your-standard-workstation-vendor>"
  # laptop: "<your-standard-laptop-vendor>"
  # server: "<your-standard-server-vendor>"
  # firewall: "<your-standard-firewall-slug>"
  # switch: "<your-standard-switch-slug>"
  # ssl_certificate_authority: "<your-standard-ca>"

cost_estimates:
  # INHERITS from config/msp-config.yaml `cost_estimates` block.
  # Override per-deliverable ONLY when a specific customer engagement
  # uses different cost figures (e.g., customer has a negotiated
  # discount). When the config-level block is empty (default), the
  # budget-summary section outputs counts only — no dollar column.
  # To override, uncomment + set values:
  #
  # workstation_replacement_avg: 0
  # laptop_replacement_avg: 0
  # server_replacement_avg: 0
  # firewall_replacement_avg: 0
  # m365_seat_avg_monthly: 0
  # edr_seat_avg_annual: 0

narrative:
  lead_with_outcomes: true               # "10 workstations need refresh in Q3" not "rawDeviceList[N]"
  group_by_phase: true                   # group output by fiscal quarter
  include_no_action_quarters: true       # confidence-building "no actions in Q4 2026"
  include_vendor_consolidation: true     # call out multi-vendor sprawl as a consolidation opportunity
  separate_capex_opex: false             # set true for the Acct/Fin variant

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

- "Refresh roadmap for <customer>"
- "Lifecycle roadmap for <customer>"
- "Hardware refresh plan for the next fiscal year"
- "Warranty roadmap"
- "Renewal calendar for <customer>"
- "License expiration roadmap"
- "Win10 EOL plan for the customer"
- "What's expiring this year for <customer>"
- "Budget planning for next fiscal year for <customer>"
- "Capital plan for <customer>'s IT spend"
- "What needs replacement at <customer>"

Cadence: annual for fiscal-year capital planning; quarterly for
in-flight renewal calendar updates; ad-hoc when a vendor announces a
new EOL date.

Personas:
- **vCIO / Account Manager** (primary — owns the customer budget
  conversation and renewal proposals)
- **Accounting / Finance** (primary — builds the customer's IT
  capital + opex plan from the calendar)
- **Executive** (consumes the rolled-up view in strategic planning)
- **TAM** (reads the hardware / firmware / OS sections to align with
  the standards baseline)
- **Sales** (uses for upsell conversations during renewal cycles)
- **NOC** (reads firmware / EOL sections to plan maintenance windows)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` → match by name |
| Customer name | No | Used for filename + report header |
| Planning horizon override | No | User prompt — e.g., "show me 36 months ahead" |
| Optional: budget-cycle dates | No | Customer's fiscal year — if provided, recipe groups around customer's fiscal boundaries instead of calendar quarters |
| Optional: focus areas | No | User prompt — e.g., "focus on hardware refresh only this year" |

---

## Workflow — forward-looking variant of the cross-cutting pattern

This recipe is the **forward-looking variant** of the cross-cutting
pattern documented in `reference/cross-cutting-signals.md`. Where the
PBR (`recipes/environment-quarterly-lookback/quarterly-business-review.md`)
uses backward windows on detections / alerts / timeline, this recipe
substitutes **forward windows on every lifecycle field on every asset
class**.

### Step 1 — Scope discovery

```
liongard_environment LIST searchMode=keyword query="<customer-name>"
# Confirm environmentId. If multi-environment customer, aggregate per
# environment with a per-environment column in the calendar.
```

### Step 2 — Inspector freshness (so the roadmap isn't built on stale data)

```
liongard_timeline LIST environmentId=<ENV_ID>
```

Latest inspection events per system. Stale inspectors (older than
`qa.flag_inspector_lastseen_threshold_days`) get a 🔍 REVIEW flag,
and any lifecycle item derived from a stale inspector inherits the
flag in the calendar.

> **The roadmap is only as accurate as the latest inspection.** A
> firewall license expiring "next month" is only credible if the
> firewall inspector ran this week. Stale-data flags carry forward to
> every downstream lifecycle assertion.

### Step 3 — Headline KPIs from the cyber-risk dashboard

```
liongard_cyber_risk_dashboard <metric>  environmentId=<ENV_ID>
```

For the roadmap, the KPI dashboard is **forward-leaning**:

| KPI | Source | Roadmap meaning |
|---|---|---|
| Hardware out of warranty count | computed in Step 4 | Refresh demand today |
| Hardware within 12 months of warranty expiry | computed in Step 4 | Refresh demand next 12 months |
| Win10 devices count | computed in Step 4 (filter `operatingSystem`) | Win10 EOL exposure |
| Win10 on Win11-incompatible hardware count | computed in Step 4 (`winElevenReady=false`) | Hardware-driven refresh demand |
| Firewall licenses expiring within warn window | `all-firewalls` chained output | Renewal cycle work |
| Backup licenses expiring within warn window | `all-backups` chained output | Renewal cycle work |
| EDR licenses expiring within warn window | `all-edrs` chained output | Renewal cycle work |
| Domains expiring within warn window | Step 4 domain inventory | Renewal cycle work |
| SSL certificates expiring within warn window | per-system chained output | Renewal cycle work |
| Total roadmap line items in horizon | computed across calendar | Workload signal |

### Step 4 — Lifecycle inventory snapshot

> **Reconciled asset inventory is the primary source for lifecycle
> data** — every hardware refresh / OS EOL / domain renewal flag comes
> from the dedup'd inventory. `liongard_device` joins OS + EDR + RMM
> + AD observations on hostname / serial / MAC, so warranty +
> Win11-readiness fields reconcile to one row per real machine. See
> `reference/asset-fields.md` § Deduplication keys.

```
liongard_device LIST environmentId=<ENV_ID>
                     fields=["hostname","operatingSystem","manufacturer","model","serialNumber","class","warrantyExpiration","winElevenReady","installDate","inspectors","lastSeen"]
                     sort="warrantyExpiration"

liongard_device COUNT environmentId=<ENV_ID> operatingSystem="Windows 10"
liongard_device COUNT environmentId=<ENV_ID> operatingSystem="Windows 10" winElevenReady=false

liongard_domain LIST environmentId=<ENV_ID>
                     fields=["domainName","registrar","daysTillExpiration","registrarLock","dmarcHealth","inspectors"]
                     sort="daysTillExpiration"
                     maxDaysTillExpiration=<planning_horizon.forward_months * 30>
```

These produce the master device + domain inventory the calendar is built
from. Identity inventory is consulted only for M365 seat counts driving
license-renewal math; per-user lifecycle isn't a roadmap concern.

### Step 5 — Auto-discover deployed inspector stack + chain sub-recipes

```
liongard_system LIST environmentId=<ENV_ID>
```

Group systems by inspector slug. For each inspector class deployed
(per `customization.stack`), chain the matching system-type or
single-system recipe **with focus on lifecycle sections only**:

| Customer has… | Chained recipe | Lifecycle sections of interest |
|---|---|---|
| Windows Servers + Workstations | `all-servers.md` + `all-endpoints.md` + per-OS singles | Hardware refresh, OS EOL, patch currency, Win11 readiness |
| EDR | `all-edrs.md` + per-vendor singles | License expiration, agent version EOL |
| Firewalls | `all-firewalls.md` + per-vendor singles | Firmware support, license expiration, HA-pair lifecycle |
| Backups | `all-backups.md` + per-vendor singles | License expiration, software version EOL |
| Hypervisors | `all-hypervisors.md` | Host hardware refresh, hypervisor patch currency, vendor-support track |
| M365 tenant | `microsoft-365.md` | License SKU renewals, seat utilization, tenant lifecycle |
| KnowBe4 | `knowbe4.md` | License expiration, seat utilization |
| Domains (any) | `all-domains.md` | Domain registration expiration, SSL cert expiration where exposed |
| Identity providers (AD / Duo / JumpCloud / OneLogin) | corresponding single | License + SKU expirations |
| External attack surface (domain registrations + TLS certs) | `recipes/system-type-assessment/all-external-attack-surface.md` (or singles: `internet-domain-dns.md`, `tls-ssl.md`) | Domain registration renewal, SSL/TLS certificate expiration |
| One-off vendors | corresponding single | Whatever lifecycle field that vendor exposes |

For each chained recipe, inherit:
- `customization.refresh_standard` (the MSP's standards baseline)
- `customization.planning_horizon` (the forward window)
- `audience.tone` (so chained outputs use the right vernacular)

Extract **only the lifecycle-relevant findings** from each chained run —
not the full output — and aggregate into the calendar.

### Step 6 — Forward-rolling calendar build

For each lifecycle line item from Steps 3–5, place into the calendar:

```
For each item:
  due_date    = the EOL / warranty / expiration / renewal date
  category    = hardware | os | firmware | license | certificate | domain
  asset_count = count of assets affected (1 for licenses, N for hardware refresh)
  priority    = Critical (overdue or < 30d) | High (< 90d) | Medium (within horizon) | Low (beyond horizon)
  bucket      = floor((due_date - today_quarter_start) / 90 days)   # for group_by quarter
  recommendation = lookup from the recommendation template table below
```

Sort and group by `planning_horizon.group_by` (default quarter).

Within each bucket, sort by:
1. Category (hardware → OS → firmware → license → certificate → domain)
2. Priority descending
3. Asset count descending

The output is a **forward-rolling table** with one row per lifecycle
item, plus optional cost-estimate column when
`customization.cost_estimates.*` is populated.

### Step 7 — Budget summary by quarter

Aggregate Step 6 by bucket and category. Output for each bucket:

| Bucket | Category | Item count | Asset count | Estimated $ (if configured) |
|---|---|---|---|---|
| Q3 2026 | Hardware refresh | 3 | 24 | $36,000 |
| Q3 2026 | OS EOL migration | 1 | 12 | $0 (labor only) |
| Q3 2026 | Firewall license renewal | 2 | 2 firewalls | $4,800 |
| ... | ... | ... | ... | ... |

When `cost_estimates` block is empty (default), the column is omitted
and the recipe outputs **counts only**. MSPs who want budget figures
populate the block at the customization level; the recipe does not
ship dollar values.

### Step 8 — Vendor consolidation opportunities

If `narrative.include_vendor_consolidation == true` (default), surface:

- **Multi-vendor sprawl per category** — e.g., "Customer has 3 EDR
  vendors. Consolidation could simplify procurement and reduce licensing
  spend." (Pulls from the `all-edrs.md` and `all-backups.md` vendor
  rollups.)
- **Within-vendor SKU sprawl** — e.g., "M365 tenant has 7 SKU types
  active; review for rightsizing." (Pulls from the `microsoft-365.md`
  recipe's licensing section.)
- **Refresh-driven vendor changes** — when hardware refresh is in
  window and a different MSP-standard vendor is configured in
  `vendor_replacement_preferences`, surface the swap as a
  consolidation opportunity.

### Step 9 — QA pass (per `reference/qa-retry-pattern.md`)

This recipe's QA pass especially focuses on:

1. **Retry persistent nulls** on the cyber-risk-dashboard metrics.
2. **Flag stale inspectors** from Step 2. Stale inspectors → lifecycle
   data may be out of date → every roadmap item from that inspector
   inherits the flag.
3. **Sanity-check warranty / EOL dates** — flag items with `warrantyExpiration`
   in the far past (likely data quality issue) or > 10 years in the future
   (likely incorrect data entry).
4. **Cross-tool divergence** —
   - Device counts from `liongard_device` vs.
     `cyber-risk-dashboard workstationTotalCount` / `winServerTotalCount`
   - EDR / backup license counts per-vendor recipe vs. their per-vendor
     dashboard metric
5. **Proposed-metric gaps** for any inspector the recipe chained where
   the inspector's recipe carries data gap notes — especially
   for the warranty / serial-number / install-date fields, which several
   vendor inspectors expose only via data gaps.
6. **Single-source visibility** — a license expiration reported by only
   one inspector class without an asset-inventory cross-reference is
   flagged for manual confirmation.

### Step 10 — Render the roadmap deliverables

The roadmap output is **two deliverables by default**:

#### A. Renewal/refresh calendar workbook (xlsx — primary)

Recommended sheet order:

| # | Sheet | Content |
|---|---|---|
| 1 | Cover | Customer, horizon (e.g. "Next 24 months — through Q2 2028"), MSP name + logo, generation date |
| 2 | Executive Summary | 5–7 outcome bullets. Headline numbers (total items, biggest quarter). |
| 3 | Budget Summary | The Step 7 quarter-by-category aggregation. With or without dollars. |
| 4 | Calendar | The full Step 6 forward-rolling table. Filterable by category / quarter / priority. |
| 5 | Hardware Refresh | Filtered view: hardware-only roadmap rows. |
| 6 | OS End-of-Life | Filtered view: OS-only roadmap rows. With migration target column (Win10 → Win11). |
| 7 | Firmware & Support | Filtered view: firmware roadmap rows. |
| 8 | License Renewals | Filtered view: license / subscription rows. |
| 9 | Certificates | Filtered view: cert expiration rows. |
| 10 | Domain Renewals | Filtered view: domain registration rows. |
| 11 | Vendor Consolidation | The Step 8 narrative. |
| 12 | Data Gaps | The Step 9 manual-verification appendix. |
| 13 | Methodology | One paragraph + a link to this recipe in the prompt library. |
| 14 | Verification Log | The Step 10 verification table below. |

#### B. Budget-planning narrative (word — secondary)

Prose version of sheets 2, 3, and 11 with per-category narrative
sections derived from the calendar. Target audience is the customer's
CFO / IT director sitting down to plan next year's budget.

#### C. Executive capital-plan deck (pptx — optional)

Set `output.format: "pptx"` and `audience.tone: "executive"` for the
capital-plan presentation. Same content, slide format, heavy on
budget-quarter summary + outcome language.

### Tone-driven adaptations

When `audience.tone == "balanced"` (default):
- Keep all standard references + counts + vendor names
- Per-category sections include the JMESPath / metric reference

When `audience.tone == "executive"` (capital-plan deck):
- Drop JMESPath / metric details from the body — appendix only
- Replace asset lists with counts ("12 workstations need refresh in Q3")
- Section headings use business language ("Workstation Refresh" not
  "winElevenReady == false count")
- Lead with the budget summary; the detail tables move to appendix

When `audience.tone == "technical"`:
- All counts, vendor names, JMESPath references, model numbers, serials
- Suitable for engineering capacity planning

---

## QA & Manual Verification

The Step 9 detail above is the recipe-specific QA pass. The canonical
pattern (retry-on-null, stale-flag thresholds, cross-tool divergence,
proposed-metric gap surfacing) lives in
`reference/qa-retry-pattern.md`. Every roadmap run produces a
**Manual Verification Needed** appendix per that pattern.

Manual checks specific to roadmap planning:

- Hardware lease / lease-end dates — not in any Liongard dataprint;
  pulled from customer asset tracker or finance system
- Vendor-specific contractual renewal calendars — partial only via
  inspector
- Per-tenant licensing $ amounts — pulled from MSP PSA / accounting
- Special-purpose appliances (printers, phones, IoT) — partial only
  via inspector
- Migration project capacity (the MSP's engineering hours to execute
  the roadmap) — external

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | Roadmap planning draws directly from the onboarding inventory: hardware age (servers, workstations, firewalls), OS version, firmware version, and end-of-support flags are the primary inputs for refresh prioritization. Without a complete onboarding record, the roadmap has no inventory foundation. |
| CIS Controls (v8.1) | ✅ | Maps to CIS 1.1/1.2 (hardware + software inventory — identifies EOL assets), 2.1/2.2 (authorized software + unsupported OS — flags replacement candidates), 4.1 (configuration management — firmware and OS versions drive currency findings), 7.3 (automated patch management — identifies assets not yet EOL but approaching risk), 12.1 (network infrastructure lifecycle — firewall and switch age). Roadmap planning is the operational output of CIS 1–2 inventory hygiene. |
| Cyber-insurance domain files | ✅ | Aligns with `domains/endpoint.md` (EOL OS + unpatched software = uncoverable risk event — carriers often exclude incidents on EOL assets), `domains/network.md` (EOL firewall firmware), `domains/governance.md` (vendor support + warranty expiry as a documentation gap). The refresh roadmap directly reduces cyber-insurance exclusion surface. |
| QBR / quarterly-business-review | ✅ | Roadmap is a standard QBR deliverable. QBR Step 9 chains this recipe to produce the upcoming-refresh and budget-planning section. Budget figures from this recipe feed the vCIO narrative at the QBR. |

---

## Insights & recommendations — generation patterns

| Pattern | Recommendation template | Default priority |
|---|---|---|
| Hardware out of warranty | "<N> <class>s out of warranty — refresh recommended within <bucket>. Quote available on request." | High (overdue) → Medium (within horizon) |
| Hardware within 12 months of warranty | "<N> <class>s within 12 months of warranty expiry — plan refresh by <quarter>." | Medium |
| Win10 device on Win11-eligible hardware | "<N> Win10 devices Win11-ready — schedule in-place upgrades by <Win10 EOL date>." | High (within 6 months of EOL) → Medium |
| Win10 device on Win11-incompatible hardware | "<N> Win10 devices NOT Win11-ready — refresh required by <Win10 EOL date>." | Critical (within 6 months of EOL) → High |
| Server OS approaching EOL | "<N> <OS> servers within <N> months of EOL — migration plan needed by <date>." | High (within 6 months) → Medium |
| Server OS past EOL | "<N> <OS> servers PAST EOL <date> — security exposure, immediate refresh / migrate." | Critical |
| Firmware out of support | "<N> firewalls / switches on EOL firmware — upgrade by <date>." | High |
| Firewall license expiring | "Renew <vendor> license on <N> firewalls by <date>." | Critical (< 30d) → High (< 90d) |
| EDR license expiring | "Renew <vendor> EDR for <N> seats by <date>." | Critical (< 30d) → High (< 90d) |
| Backup license expiring | "Renew <vendor> backup license for <N> protected systems by <date>." | Critical (< 30d) → High (< 90d) |
| M365 SKU renewal | "<N> seats of <SKU> renew on <date>. Confirm seat utilization before renewal commit." | Medium |
| SSL cert expiring | "Renew <N> SSL certificates by <date>. Top exposures: <list>." | Critical (< 14d) → High (< 45d) |
| Domain expiring | "Renew <N> domains by <date>. Top: <list>." | Critical (< 30d) → High (< 60d) |
| Domain without registrar lock | "Enable registrar lock on <N> domains. No renewal needed; security hardening only." | Medium |
| Multi-vendor sprawl (EDR / backup) | "<N> competing <category> products — consolidation plan available." | Low (informational) — vCIO decides priority |
| Hypervisor cluster aging | "<N> hosts in <cluster> approaching <refresh threshold> — capacity + refresh plan needed by <quarter>." | High (within 6 months) → Medium |

Group recommendations by **bucket / quarter** when
`narrative.group_by_phase == true` (default).

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Hardware install date / serial | partial — depends on inspector | RMM / customer asset tracker |
| Hardware lease end | not in dataprint | Customer finance system |
| Warranty expiration | partial — model-derived where vendor exposes; sometimes manual | Vendor support portal (Dell / HPE / Lenovo / Apple) |
| OS EOL anchor dates | from `refresh_standard.operating_systems` (MSP-customized) | Vendor announcements — update customization block annually |
| Firmware EOL track per vendor | varies per vendor inspector | Vendor EOL bulletins |
| License $ amounts | not in dataprint | MSP PSA / accounting |
| SSL cert inventory | partial — per-inspector exposure | External cert-scanning tool |
| Code-signing cert inventory | not in dataprint | Customer development team |
| Per-tenant negotiated discounts | not in dataprint | MSP procurement / vendor portal |
| Migration project hours | external | MSP engineering capacity planning |

---

## Output format

`xlsx` (default — calendar workbook) is the canonical primary
deliverable. Supplement with:

- **Word** budget-planning narrative — for the CFO / IT director
- **PowerPoint** capital-plan deck — for the executive presentation
  (set `audience.tone: "executive"`)
- **Markdown** working draft — useful for the AM to edit before
  generating the customer-facing xlsx

See `templates/output-block-xlsx.md`, `templates/output-block-word.md`,
and `templates/output-block-pptx.md` for layout conventions.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | query=<customer> | array<environment> | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3 | liongard_cyber_risk_dashboard | per-metric | <integer> | ok per metric |
| 4 | liongard_device / domain LIST | envId=<ENV_ID> [filters incl. forward-window for domain] | varies | ok |
| 5 | liongard_system LIST + chained sub-recipes | envId=<ENV_ID> | array<system> + per-recipe lifecycle excerpts | ok per class |
| 6 | (calendar build) | per planning_horizon + refresh_standard | array<roadmap-row> | ok |
| 7 | (budget summary) | per group_by | aggregation table | ok |
| 8 | (vendor consolidation) | per narrative.include_vendor_consolidation | array<finding> | ok |
| 9 | QA pass | per `reference/qa-retry-pattern.md` | varies | ok |
| 10 | render | per `output.format` | <artifact path> | ok |
```

---

## Relationship to other cross-cutting recipes

- **PBR (`environment-quarterly-lookback/quarterly-business-review.md`)** —
  *Backward-looking.* The roadmap is the natural follow-on to a PBR
  conversation. PBR says "here's what happened"; roadmap says "here's
  what's next".
- **Onboarding (`onboarding-assessment/new-customer-onboarding.md`)** —
  *Point-in-time.* The onboarding intake includes a roadmap section
  scoped to the first 12 months; this recipe is the standalone
  full-horizon version. After 90 days of onboarding, the customer
  transitions to this recipe for ongoing annual capital planning.
- **Cyber-insurance readiness (`compliance/cyber-insurance/cyber-insurance-readiness.md`)** —
  *Compliance evidence.* When a cyber-insurance question asks about
  patching / refresh cadence / firmware currency, the roadmap is the
  evidentiary backup. Link the roadmap into the cyber-insurance
  appendix when applicable.

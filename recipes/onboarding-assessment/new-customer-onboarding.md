---
name: new-customer-onboarding
description: >
  Use this skill when the user wants to onboard a new customer to the MSP,
  perform an intake / first-90-days assessment, run a Technical Alignment
  intake, or build a remediation plan to bring a new customer to the MSP's
  documentation + security standard. Point-in-time (current-state) variant
  of the cross-cutting recipe pattern — discovers the customer's full
  inspector stack and grades each system class against the MSP's onboarding
  baseline. Trigger phrases: "onboarding assessment for a customer",
  "intake for a new customer", "TAM onboarding", "first-90-days plan",
  "technical alignment intake", "what does this new customer need fixed",
  "bring this customer to standard", "gap analysis for a new customer".
  Auto-discovers deployed inspectors and chains the appropriate per-system
  and system-type recipes against the onboarding standard. Produces an
  Excel intake workbook (per-class scorecard + remediation tracker) and a
  Word narrative gap analysis (TAM's first conversation document).
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_timeline, liongard_cyber_risk_dashboard, liongard_device, liongard_identity, liongard_domain, liongard_metric. liongard_detection and liongard_alert are optional — used only if customer was inspected before formal handoff."
personas: [technical-alignment-manager, vcio-account-manager, sales, noc, soc]
output_formats: [xlsx, word, markdown, pptx]
primitives: []
composes:
  - recipe:qbr:environment-quarterly-lookback
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

# New Customer Onboarding Assessment — Master Recipe

> **The canonical onboarding intake.** A *point-in-time* current-state
> assessment that answers: *"What is in this customer's environment today,
> what aligns to our standard, what needs to be fixed, and in what order?"*
> Coupled to a remediation tracker that drives the first 30 / 60 / 90 days
> of the engagement.
>
> **Differs from the PBR cross-cutting recipe.** The PBR is *time-bounded*
> ("what changed in the last 90 days"). Onboarding is *point-in-time*
> ("what is the current state, period"). The PBR cares about detections,
> alerts, and the inspection timeline within a window. Onboarding cares
> about the current inventory, the configuration baseline of each system
> class, and how it stacks up against the MSP's documented standard.
>
> **Customer-stack-adaptive.** Calls `liongard_system LIST` to discover
> the inspector stack the new customer has deployed, then chains the
> appropriate per-system or per-system-type recipes for what it finds —
> and **flags inspector gaps** (the MSP's standard stack vs. what this
> customer actually has).
>
> **References:** `reference/cross-cutting-signals.md` (the cross-cutting
> workflow + MCP tool table; this recipe drops the time-window steps),
> `reference/asset-fields.md` (the reconciled-asset-inventory tools),
> `reference/qa-retry-pattern.md` (the QA pass), `reference/inspector-aliases.md`
> (translating user shorthand to inspector slugs),
> `reference/personas-recipe-matrix.md` (which audience consumes which
> section).


---

## Customize for your MSP

```yaml
output:
  format: xlsx                           # xlsx | word | markdown | pptx
                                         # Default: intake workbook. Use word for the
                                         # narrative gap analysis; pptx for the sales-handoff
                                         # or executive intro deck; markdown for working drafts.
  filename: "<customer>-Onboarding-Intake-<date>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  cover: "Onboarding Assessment"
  executive_summary: "Executive Summary"
  inventory_snapshot: "Inventory Snapshot"
  inspector_coverage: "Inspector Coverage"
  headline_kpis: "Headline KPIs"
  per_class_sections: "Per-System Findings"          # auto-generated per deployed inspector class
  gap_analysis: "Gap Analysis vs. Standard"
  remediation_plan: "30 / 60 / 90 Day Plan"
  data_gaps: "Data Gaps & Manual Verification"
  appendix: "Appendix — Methodology"
  verification_log: "Verification Log"               # technical readers only

audience:
  tone: "balanced"                       # technical | balanced | executive
                                         # Default balanced — TAM is the primary author
                                         # and the first internal handoff conversation.
                                         # Override to executive for the customer-facing
                                         # kickoff deck; technical for the engineering
                                         # remediation working document.
  reading_level: "technical-buyer"

onboarding_standard:
  # The MSP's documented onboarding baseline. Recipe grades the customer
  # against these defaults; per-class sections call out misalignment.

  expected_inspectors:
    # The MSP's standard stack — recipe flags any of these NOT present
    # in the customer environment so the TAM can scope inspector deployment.
    # INHERITS from config/msp-config.yaml `preferred_stack` block by
    # default. Override per-engagement ONLY when a specific customer
    # has been onboarded with a non-standard stack and you want the
    # gap-analysis section scoped to their stack rather than the MSP
    # standard. To override, uncomment + set explicit slug lists:
    #
    # identity: ["microsoft-365", "active-directory"]                 # one is acceptable; both is standard
    # edr: ["<your-standard-edr-slug>"]                               # e.g. "sentinelone", "huntress", "sophos-central"
    # backup: ["<your-standard-backup-slug>"]                         # e.g. "datto-bcdr", "cove-data-protection"
    # firewall: ["<your-standard-firewall-slug>"]                     # e.g. "fortinet-fortigate", "sonicwall"
    # awareness_training: ["knowbe4"]
    # dns_filtering: ["cisco-umbrella"]
    # rmm: []                                                          # add when RMM inspectors ship
    # psa: []
    # optional: ["axcient-x360-recover", "acronis-cyber-protect-cloud"]

  identity_baseline:
    mfa_coverage_pct_min: 95
    privileged_mfa_required: true                                    # 100% MFA on privileged accounts is non-negotiable
    stale_account_max_days: 90                                       # accounts not logged in past N days = candidate for disable
    shared_account_max: 0                                            # generic / shared logins flagged
    service_account_naming_pattern: "svc-*"                          # used to grep stale + un-named service accounts

  endpoint_baseline:
    edr_coverage_pct_min: 95
    unprotected_servers_max: 0
    bitlocker_required_on: ["laptop"]                                # asset classes that must show disk encryption
    patch_age_days_max: 30
    win10_eol_policy: "refresh-or-extend-by-2025-10"
    supported_os_only: true                                          # flag any device on EOL OS

  network_baseline:
    firewall_firmware_age_days_max: 180
    firewall_high_availability_required: false                       # set true if HA is the standard for this MSP
    license_expiration_warn_days: 60
    open_rdp_to_internet_allowed: false                              # never allowed — flag any matching rule
    default_deny_outbound: false                                     # set true if MSP standard is default-deny egress

  backup_baseline:
    server_coverage_pct_min: 100                                     # every server must have a backup job
    successful_backup_recency_days_max: 7                            # last successful backup ≤ N days old
    offsite_replication_required: true
    encryption_in_flight_required: true
    encryption_at_rest_required: true

  domain_baseline:
    dmarc_health_required: "pass"                                    # pass | quarantine | reject — choose MSP standard
    registrar_lock_required: true
    expiration_warn_days: 60
    spf_pass_required: true
    dkim_pass_required: true

stack:
  # Auto-discover by default. Manual overrides for scoping.
  auto_discover: true
  inspectors_in_scope: []                # explicit list overrides auto-discovery
  inspectors_to_skip: []                 # exclusions from auto-discovery
  freshness_grace_period_days: 14        # new customers — give recently-deployed inspectors time to settle
                                         # before flagging as stale. Override to 7 once past first 30 days.

per_class_recipe_overrides:
  # Map an inspector slug or system-type rollup to a custom recipe
  # path. Defaults to library recipes when not overridden.
  # cisco-meraki-inspector: "<msp-local>/meraki-onboarding-custom.md"

narrative:
  lead_with_outcomes: true               # "customer is missing EDR on 4 servers" not "edrCoverageCount=96"
  surface_no_op_categories: true         # "Backups: meets standard, no remediation needed" reads as confidence-building
  group_remediation_by_phase: true       # 30 / 60 / 90 grouping
  include_inspector_gap_section: true    # flag MSP-standard inspectors not yet deployed
  include_quick_wins_section: true       # easy first-30-day wins build customer trust

remediation_phases:
  # Days from onboarding start. Used to group findings in the plan.
  immediate: 7                           # safety / critical gaps — must close in first week
  thirty_day: 30
  sixty_day: 60
  ninety_day: 90

verification:
  log_queries: true
  redact_values: true

qa:
  retry_on_null: true
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 14    # see stack.freshness_grace_period_days
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: false
  surface_single_source_visibility: true
  manual_verification_section_required: true
```

---

## When to use

- "Onboarding assessment for <customer>"
- "Intake for the new customer we just signed"
- "TAM onboarding for <customer>"
- "First-90-days plan for <customer>"
- "Technical Alignment intake"
- "What does this new customer need fixed?"
- "Bring <customer> to our standard"
- "Gap analysis for the customer we're onboarding"
- "We just deployed inspectors at <customer> — give me the punch list"

Cadence: once per new customer (formal onboarding), with optional re-runs
at 30 / 60 / 90 days to confirm remediation progress. After the 90-day
mark, the customer transitions to PBR cadence
(`recipes/environment-quarterly-lookback/quarterly-business-review.md`).

Personas:
- **Technical Alignment Manager** (primary author + owner of remediation)
- **vCIO / Account Manager** (consumes for engagement scoping + budget
  conversations)
- **Sales** (in some MSP shops, runs the discovery-mode variant during
  late-stage sales — see `recipes/sales-assessment/`; onboarding is the
  same recipe but with `audience.tone: "executive"` and `output.format:
  "pptx"`)
- **NOC / SOC** (read for operational + security context once standing
  up monitoring)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` → match by name |
| Customer name | No | Used for filename + report header |
| Optional: focus areas | No | User prompt — e.g., "focus on identity posture this intake" |
| Optional: handoff-from-sales notes | No | Free-text from the AE / vCIO who closed the deal — pasted into Executive Summary as context |

> **Why not a time window?** Onboarding is point-in-time. The customer
> may have data preceding handoff, but the recipe treats the inspection
> data as a current-state photograph and grades it against the standard.
> Time-bounded narrative belongs in the quarterly review (PBR), not the
> intake.

---

## Workflow — point-in-time variant of the cross-cutting pattern

This recipe is the **point-in-time variant** of the cross-cutting pattern
documented in `reference/cross-cutting-signals.md`. The PBR
(`recipes/environment-quarterly-lookback/quarterly-business-review.md`) is
the time-bounded canonical implementation; this recipe drops the
detections-in-window / alerts-in-window / timeline-in-window steps and
adds a gap-analysis-vs-standard step.

### Phase 0 — External Attack Surface (zero-credential first pass)

> **Run this before any credentialed step.** When a new customer is
> handed off, the MSP often has the domain names and public IPs before
> credentials have been collected. The external-attack-surface rollup
> produces real findings on day 0 — quick wins for the first-week
> remediation list, and a baseline the TAM returns to throughout the
> 30 / 60 / 90 plan.

```
# Chain the external-attack-surface rollup
include recipes/system-type-assessment/all-external-attack-surface.md
  with scope_inputs.mode = "credentialed" (or "discovery" if env not built yet)
       scope_inputs.domains = <customer domains>
       audience.tone = "balanced"
       narrative.redact_individual_users = true
```

Outputs from this phase feed Step 6 (Gap analysis) directly:
- Mail-trust gaps → identity / network baseline rows
- TLS gaps → endpoint / network baseline rows
- IP reputation findings → network baseline rows
- Dark-web credential exposures → identity baseline rows (with
  cross-reference to the identity inventory once credentialed access
  is in place)

The Phase 0 quick wins (registrar lock, HSTS, expired-cert renewals,
DMARC at `p=none rua=...`) become the literal first-week deliverable
the TAM owns before deeper credentialed work begins.

### Step 1 — Scope discovery

```
liongard_environment LIST searchMode=keyword query="<customer-name>"
# Confirm environmentId. If multi-environment customer (e.g., parent +
# subsidiaries), repeat per environment; final intake aggregates with a
# per-environment breakdown.
```

### Step 2 — Inspector freshness + inspector-gap check

```
liongard_timeline LIST environmentId=<ENV_ID>
# Latest inspection events per system. No window — we want most-recent state.
```

Two passes from the timeline data:

1. **Freshness pass** — Identify inspectors that haven't run since
   `freshness_grace_period_days` ago. New customers get a longer grace
   period than tenured ones because inspector deployment is still
   stabilizing. Stale inspectors get a 🔍 REVIEW flag and a
   "confirm-credentials" remediation item.
2. **Inspector-gap pass** — Diff the deployed inspector slugs against
   `onboarding_standard.expected_inspectors`. For each expected
   inspector not deployed, add a "deploy inspector" item to the
   remediation plan, scoped to `remediation_phases.thirty_day` by
   default.

> **The inspector-gap section is the recipe's most differentiated content.**
> A new customer arriving with an incomplete inspector stack is the norm.
> The TAM needs the gap surfaced up front so deployment-scope and
> credentials-collection work starts day 1.

### Step 3 — Headline KPIs from the cyber-risk dashboard

```
liongard_cyber_risk_dashboard <metric>  environmentId=<ENV_ID>
```

| KPI | Metric (representative) | Compliant when |
|---|---|---|
| M365 users | `m365TotalUsers` | (informational) |
| AD users | `activeDirectoryTotalUsers` | (informational) |
| Workstations | `workstationTotalCount` | (informational) |
| Servers (Win + Linux + macOS) | `winServerTotalCount`, plus macOS / Linux totals | (informational) |
| MFA coverage % | (dashboard metric) | ≥ `onboarding_standard.identity_baseline.mfa_coverage_pct_min` |
| Privileged MFA coverage % | (dashboard metric) | 100% required |
| EDR coverage % | (dashboard metric) | ≥ `onboarding_standard.endpoint_baseline.edr_coverage_pct_min` |
| Servers without backup coverage | computed in Step 5 join | = 0 required |
| Domain count | `domainAndWebsiteSecurityTotalDomains` | (informational) |
| Inspectors deployed vs. expected | computed in Step 2 | 100% of standard stack expected |

Surface the KPI tiles at the top of the intake workbook's
"Inspector Coverage" sheet — these are the **scoreboard** the TAM
returns to throughout the engagement.

### Step 4 — Current-state inventory snapshot — **the recipe's foundation**

> **The reconciled asset inventory is the primary source for this
> recipe**, not a cross-check. Per-inspector `liongard_metric` calls in
> later steps are for inspector-specific configuration detail; the
> three reconciled tools below are the authoritative "who / what /
> where" answer for the new customer's environment.
>
> Each tool deduplicates across inspectors using a primary key
> (see `reference/asset-fields.md` § Deduplication keys):
>
> | Tool | Dedup key | Result |
> |---|---|---|
> | `liongard_identity` | email address | One identity per unique user, with `inspectors[]` listing every IdP / MFA layer / app where they appear |
> | `liongard_device` | hostname / serial / MAC | One device per real machine, with `inspectors[]` listing every OS / EDR / RMM / AD inspector observing it |
> | `liongard_domain` | domain name | One record per domain, with `inspectors[]` listing every place the domain is referenced |

```
# Devices — reconciled across OS inspectors + EDR + RMM + AD + hypervisor
liongard_device COUNT environmentId=<ENV_ID>
liongard_device COUNT environmentId=<ENV_ID> physical=false
liongard_device LIST environmentId=<ENV_ID>
                     fields=["hostname","operatingSystem","manufacturer","model","serialNumber","macAddress","class","role","warrantyExpiration","winElevenReady","inspectors","lastSeen"]

# Identities — reconciled across M365 + AD + JumpCloud + OneLogin + Duo + per-app
liongard_identity COUNT environmentId=<ENV_ID>
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true
liongard_identity COUNT environmentId=<ENV_ID> privileged=true
liongard_identity LIST environmentId=<ENV_ID>
                       fields=["displayName","username","email","accountType","privileged","mfaStatus","lastLogin","enabled","emailLicenses","inspectors"]

# Domains — reconciled across Internet Domain + M365 accepted-domains + Google Workspace verified-domains + per-tenant references
liongard_domain COUNT environmentId=<ENV_ID>
liongard_domain LIST environmentId=<ENV_ID>
                     fields=["domainName","registrar","daysTillExpiration","registrarLock","dmarcHealth","spfHealth","dkimHealth","inspectors"]
```

Produces the intake workbook's three master inventory sheets
(Devices / Identities / Domains). These power every downstream gap check.

> **Always include the `inspectors[]` field on each LIST call.** The
> array is the TAM's first signal: a device with only one inspector
> in the array (e.g., only `active-directory-inspector`) is a coverage
> gap — that device is in AD but not in any EDR or RMM. Cross-check
> against the per-class chained recipes in Step 5 to confirm.

### Step 5 — Auto-discover deployed inspector stack + chain sub-recipes

```
liongard_system LIST environmentId=<ENV_ID>
```

Group systems by inspector slug. For each inspector class deployed
(per `customization.stack.auto_discover` / `inspectors_in_scope` /
`inspectors_to_skip`), chain the matching system-type or single-system
recipe with `audience.tone: "balanced"` and time-window steps SKIPPED:

| Customer has… | Recipe to chain |
|---|---|
| Windows Servers + Workstations | `recipes/system-type-assessment/all-servers.md` + `all-endpoints.md` + `all-windows-patching.md` |
| Any EDR (multiple vendors common at handoff) | `recipes/system-type-assessment/all-edrs.md` |
| Firewalls (one or multiple vendors) | `recipes/system-type-assessment/all-firewalls.md` |
| Backups (any vendor) | `recipes/system-type-assessment/all-backups.md` |
| Hypervisors | `recipes/system-type-assessment/all-hypervisors.md` |
| M365 tenant | `recipes/single-system-analysis/by-inspector/microsoft-365.md` |
| AD | `recipes/single-system-analysis/by-inspector/active-directory.md` |
| KnowBe4 | `recipes/single-system-analysis/by-inspector/knowbe4.md` |
| Domains (any) | `recipes/system-type-assessment/all-domains.md` |
| External-facing IPs + customer-facing TLS hosts + breach exposure | `recipes/system-type-assessment/all-external-attack-surface.md` (already chained in Phase 0; re-reference findings here) |
| One-off vendors not covered by a rollup | The corresponding per-vendor single-system recipe |

For each chained recipe, run with the onboarding recipe's `customization`
inherited (the **standard baseline** is the most important inherited
input). Extract the **findings + recommendations** from each chained run
— not the full output — and roll into the "Per-System Findings" section.

> **At handoff a customer commonly has multiple competing EDRs / backups
> from prior MSPs.** The `all-edrs.md` and `all-backups.md` rollups
> surface the vendor sprawl + orphaned-license findings that drive
> consolidation decisions in the first 60 days. Don't skip them.

### Step 6 — Gap analysis vs. standard

For each baseline section in `customization.onboarding_standard`, run the
corresponding check and build a finding row:

| Baseline category | Check | Source |
|---|---|---|
| Identity — MFA coverage | Compare dashboard MFA % to baseline minimum | Step 3 KPI |
| Identity — privileged MFA | Find any privileged account without MFA | `liongard_identity LIST privileged=true mfaStatus="NO"` |
| Identity — stale accounts | Enabled accounts with `lastLogin` > `stale_account_max_days` ago | Step 4 identity inventory |
| Identity — shared accounts | Generic naming patterns (e.g., "shared", "team", "front-desk") | Step 4 identity inventory (regex over `username`) |
| Endpoint — EDR coverage | Compare dashboard EDR % to baseline minimum | Step 3 KPI |
| Endpoint — unprotected servers | Servers in `liongard_device` not present in any EDR inspector's coverage | `all-servers.md` chained output |
| Endpoint — disk encryption | Laptops without disk encryption flag | Per-OS recipe (Step 5) |
| Endpoint — patch currency | Devices with patch age > baseline | `all-windows-patching.md` chained output |
| Endpoint — supported OS | Devices on EOL OS (Win 7 / Win 8 / Win Server 2008 / Win Server 2012) | Step 4 device inventory |
| Network — firmware currency | Firewalls with firmware age > baseline | `all-firewalls.md` chained output |
| Network — license expiration | Firewall licenses expiring within warn window | `all-firewalls.md` chained output |
| Network — open RDP to internet | Firewall rules permitting any-source to TCP/3389 | `all-firewalls.md` chained output |
| Backup — server coverage | Servers in `liongard_device` not joined to a backup job | `all-backups.md` chained output |
| Backup — recency | Backup jobs with last successful run > baseline | `all-backups.md` chained output |
| Backup — offsite replication | Jobs without offsite replication enabled | `all-backups.md` chained output |
| Domain — DMARC health | Domains failing baseline DMARC posture | Step 4 domain inventory |
| Domain — registrar lock | Domains without registrar lock | Step 4 domain inventory |
| Domain — expiration | Domains expiring within warn window | Step 4 domain inventory |

Every failed check produces a finding row with:
- **Finding text** (1–2 sentences)
- **Severity** (Critical / High / Medium / Low) — derived from baseline category
- **Affected asset list** (capped at 10 in the narrative; full list in the workbook)
- **Recommendation** (1-line action template)
- **Effort estimate** (S / M / L) — TAM fills in during workbook review
- **Phase** (Immediate / 30-day / 60-day / 90-day) — defaults by severity, TAM can override

### Step 7 — Quick-wins enumeration

If `narrative.include_quick_wins_section == true` (default), pull the
findings tagged Low or Medium severity with effort = S, plus the
inspector-gap items with credentials-on-hand, into a **first-week
quick-wins** list. These build customer trust by showing fast progress
before the harder remediation work begins.

Examples of quick-wins:
- Enable registrar lock on the customer's domains
- Disable a handful of stale accounts after MSP-customer confirmation
- Apply a backlog of pending non-critical patches during the first
  maintenance window
- Deploy KnowBe4 phishing simulation campaign (if KnowBe4 already exists
  but no campaigns are active)

### Step 8 — QA pass (per `reference/qa-retry-pattern.md`)

This recipe's QA pass especially focuses on:

1. **Retry persistent nulls** on the cyber-risk-dashboard metrics — they
   can be transient if a dashboard refresh job is mid-run.
2. **Flag stale inspectors** from Step 2, with the longer
   `freshness_grace_period_days` accounted for. Stale inspectors mean
   the gap analysis is reading from incomplete data — every gap check
   that depends on a stale inspector gets a "data may be incomplete"
   note in the finding row.
3. **Cross-tool divergence checks** —
   - `cyber-risk-dashboard m365TotalUsers` vs.
     `liongard_identity COUNT environmentId=<ENV_ID>` filtered to M365
   - `cyber-risk-dashboard workstationTotalCount` vs.
     `liongard_device COUNT operatingSystem="Windows" category="compute"` minus servers
   - Per-EDR per-inspector counts vs. asset-inventory device counts
4. **Proposed-metric gaps** for any inspector the recipe chained where
   the inspector's recipe carries data gap notes.
5. **Single-source visibility** — call out devices / identities only
   reported by one inspector class. At onboarding this is a common
   finding (e.g., devices only in AD because EDR isn't deployed yet) and
   the recipe should narrate it as "deploy EDR to confirm" rather than
   "data quality issue".

### Step 9 — Render the intake deliverables

The onboarding output is **two deliverables by default**:

#### A. Intake workbook (xlsx — primary)

Recommended sheet order:

| # | Sheet | Content |
|---|---|---|
| 1 | Cover | Customer, date, MSP TAM owner, environment IDs in scope, MSP name + logo |
| 2 | Executive Summary | 5–8 outcome bullets + handoff-from-sales notes pasted here for context |
| 3 | Inspector Coverage | Deployed-vs-expected table (Step 2). Status icons per inspector. Owner / target-date columns for the missing ones. |
| 4 | Headline KPIs | Step 3 KPI tiles. Compliance status vs. baseline. |
| 5 | Devices | Full device inventory from Step 4. Filterable columns. |
| 6 | Identities | Full identity inventory from Step 4. Privileged / stale / shared flags. |
| 7 | Domains | Full domain inventory from Step 4. DMARC / lock / expiration columns. |
| 8 | Per-System Findings | One section per chained recipe (Step 5). Findings + recommendations. |
| 9 | Gap Analysis | The Step 6 finding rows — the master remediation tracker. |
| 10 | Quick Wins | Step 7 (if enabled). The first-week punch list. |
| 11 | 30 / 60 / 90 Plan | Phase-grouped view of Gap Analysis findings. Owners + target dates filled by the TAM. |
| 12 | Data Gaps | The Step 8 manual-verification appendix. |
| 13 | Methodology | One paragraph + a link to this recipe in the prompt library. |
| 14 | Verification Log | The Step 9 verification table below (technical readers). |

#### B. Narrative gap analysis (word — secondary)

A prose version of sheets 2, 3, 4, 9, and 11 for the TAM's first
conversation with the customer's IT leadership. Same content, narrative
format. Sheet 11 becomes "Recommended 30 / 60 / 90 Day Plan" with each
phase as a section.

#### C. Sales-handoff or executive intro deck (pptx — optional)

Set `output.format: "pptx"` and `audience.tone: "executive"` for the
customer-facing kickoff deck. Same content as the Word doc, slide format,
heavy on outcome language.

### Tone-driven adaptations

When `audience.tone == "balanced"` (default):
- Keep all baseline references + counts + vendor names
- Per-class findings include the specific JMESPath / metric reference
  for the technical reader

When `audience.tone == "executive"` (customer kickoff deck):
- Drop JMESPath / metric details from the body — appendix only
- Replace numeric counts with risk language where the count is small
- Section headings use customer-business language, not vendor names
- Lead with the "how we'll bring you to standard" story, not the "what's
  broken today" story

When `audience.tone == "technical"`:
- All counts, vendor names, JMESPath references included
- Suitable for engineering-led remediation working sessions

---

## QA & Manual Verification

The Step 8 detail above is the recipe-specific QA pass. The canonical
pattern (retry-on-null, stale-flag thresholds, cross-tool divergence,
proposed-metric gap surfacing) lives in
`reference/qa-retry-pattern.md`. Every onboarding intake produces a
**Manual Verification Needed** appendix in the deliverable per that
pattern — even if empty (in which case the appendix explicitly says
"✅ All evidence verified — no manual checks needed").

Manual checks specific to onboarding (frequent at handoff):

- Customer-provided documentation review (network diagrams, runbooks,
  vendor contacts, license keys) — not in any Liongard dataprint
- Physical access controls / facility security — not in any Liongard
  dataprint
- Out-of-band management posture (iLO / iDRAC / IPMI) — partial only
- Vendor portal-only data (firewall traffic analytics, EDR threat
  intel, backup restore-test history) — confirm via vendor consoles

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | This recipe IS the onboarding intake driver. Every question in the QA coverage matrix is answered by Steps 3–10 of this workflow. The output is the primary population event for `onboarding-qa-coverage.md`. |
| CIS Controls (v8.1) | ✅ | Breadth coverage across the full control set at intake depth: CIS 1.1/1.2 (hardware + software inventory), 4.1 (configuration baseline), 5.1/5.2 (account inventory + privileged-account audit), 6.3 (MFA coverage baseline), 8.2 (audit-log status), 10.1 (backup coverage), 12.2 (firewall / boundary protection), 14.1/14.6 (email auth — SPF/DKIM/DMARC baseline). Full per-control depth is handled by the per-inspector and system-type recipes chained from this one. |
| Cyber-insurance domain files | ✅ | Onboarding data is the canonical first-run evidence source for all 7 domain files: `domains/auth.md` (MFA + privileged-account baseline), `domains/endpoint.md` (EDR + patch baseline), `domains/backup.md` (backup coverage + encryption), `domains/network.md` (firewall posture + open-port baseline), `domains/governance.md` (documentation + policy baseline). Gaps found here become the MSP's initial remediation roadmap. |
| QBR / quarterly-business-review | ✅ | Onboarding output is the QBR's day-zero baseline. QBR Step 3 explicitly chains from this recipe to measure quarter-over-quarter delta. Without a complete onboarding run, the QBR trend analysis has no origin point. |

---

## Insights & recommendations — generation patterns

| Pattern | Recommendation template | Default phase |
|---|---|---|
| MFA coverage below baseline | "Enroll <N> remaining users in MFA via <method>." | Immediate (privileged) / 30-day (general) |
| Privileged account without MFA | "Enable MFA on <N> privileged accounts immediately. Confirm with customer security lead before enforcement." | Immediate |
| EDR coverage gap | "Install EDR on <N> servers / endpoints; investigate inspectors-array gap for <N> AD-only devices." | 30-day |
| Unprotected server | "<N> servers have no EDR — deploy <standard EDR> after confirming customer change window." | Immediate (production) / 30-day (others) |
| Unsupported OS | "<N> devices on EOL OS — refresh roadmap required; quote within first 60 days." | 60-day plan, 90-day execution |
| Win10 EOL approaching | "<N> Win10 devices on incompatible hardware — refresh roadmap required." | 60-day plan |
| Critical patches pending | "Apply <N> critical patches within <SLA> days. Top exposed systems: <list>." | Immediate |
| Firewall firmware out of date | "<N> firewalls have firmware older than <baseline> days — schedule upgrade." | 30-day |
| Firewall license expiring | "Initiate renewal for <list> within <N> days." | Immediate if < 30d, otherwise 60-day |
| Open RDP to internet | "Remove or restrict any-source RDP rules on <N> firewalls. Confirm legitimate access via VPN." | Immediate |
| Servers without backup | "<N> servers lack any backup coverage — deploy <standard backup> after capacity review." | Immediate (production) / 30-day (others) |
| Stale backup jobs | "<N> backup jobs haven't succeeded in <N> days — triage and remediate." | Immediate |
| DMARC not at standard | "<N> domains missing DMARC <baseline> — coordinate with email-marketing stakeholders before enforcement." | 60-day |
| Domain registrar lock missing | "Enable registrar lock on <N> domains." | Immediate (quick win) |
| Inspector gap — missing from standard stack | "Deploy <inspector slug> inspector — coordinate credentials with customer." | 30-day |
| Stale accounts | "Confirm with customer whether <N> stale accounts can be disabled. Schedule disable + delete-after-30-day flow." | 30-day |
| Shared accounts | "<N> shared / generic accounts identified. Convert to per-user named accounts before enforcement of access controls." | 60-day |
| Vendor sprawl (multiple EDRs / backups) | "<N> competing <category> products in environment — consolidation plan needed." | 90-day plan |

Group recommendations by **phase** when
`narrative.group_remediation_by_phase == true` (default).

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Inspector freshness | flagged from Step 2 | Trigger re-inspection; confirm agent / API access; coordinate credentials with customer |
| Expected-but-missing inspector | flagged from Step 2 | Customer onboarding checklist — credentials + access |
| Proposed-metric gaps in chained per-class recipes | flagged per-recipe | The relevant Jira metric-request ticket under ROAR-27030 |
| Vendor portal-only data (traffic / threat analytics) | external | The relevant vendor console |
| Restore-test history | not in dataprint | MSP runbook + customer vendor portal |
| HA-pair config drift across vendors | not in dataprint | Manual UI compare |
| Per-tenant licensing $ amounts | not in dataprint | MSP PSA / accounting system |
| Customer-provided documentation (diagrams, runbooks, contacts) | external | Customer SharePoint / handoff packet |
| Physical / facility security posture | external | Customer site walk-through |
| Out-of-band management posture | partial / external | Vendor consoles + customer documentation |

---

## Output format

`xlsx` (default — intake workbook) is the canonical primary deliverable.
Supplement with:

- **Word** narrative gap analysis — for the TAM's first conversation
  with customer IT leadership
- **PowerPoint** kickoff deck — for the executive intro meeting
  (set `audience.tone: "executive"`)
- **Markdown** working draft — useful for the TAM to edit before
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
| 4 | liongard_device / identity / domain LIST + COUNT | envId=<ENV_ID> [filters] | varies | ok |
| 5 | liongard_system LIST + chained sub-recipes | envId=<ENV_ID> | array<system> + per-recipe outputs | ok per class |
| 6 | (gap analysis — derived from Steps 2–5) | per onboarding_standard | array<finding> | ok |
| 7 | (quick wins — derived from Step 6) | per narrative.include_quick_wins_section | array<finding subset> | ok |
| 8 | QA pass | per `reference/qa-retry-pattern.md` | varies | ok |
| 9 | render | per `output.format` | <artifact path> | ok |
```

---

## Transitioning out of onboarding

After the 90-day intake cadence, the customer transitions to the PBR
recurring cadence:

- **Primary recurring recipe:**
  `recipes/environment-quarterly-lookback/quarterly-business-review.md`
- **Per-class drift checks at quarterly cadence:**
  Same system-type and single-system recipes chained here, but with the
  PBR's time-bounded variant (detections / alerts / timeline-in-window
  signals included)
- **Standards re-grading:**
  Run this onboarding recipe again at the 1-year anniversary to confirm
  the customer has stayed at standard. Findings from the re-run become
  the next cycle's remediation backlog.

The `onboarding_standard` block defined here is the **same baseline** the
PBR's per-class chained recipes grade against — keep it aligned. When the
MSP updates its onboarding standard, update this customization block, and
the PBR + per-class recipes automatically inherit the new baseline on
their next run.

---
name: <kebab-case-skill-name>
description: >
  Use this skill when <trigger phrases — what the user says or asks for>. Produces
  <artifact name> using live Liongard data via <tools used: liongard_metric, liongard_device,
  liongard_identity, liongard_environment, etc.>. Best for <persona(s)> at <cadence>.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_launchpoint, liongard_metric, liongard_device, liongard_identity"
personas: []                # optional — e.g. [vcio-account-manager, noc, soc]
output_formats: [markdown]  # default; add: html, word, pptx, xlsx as supported
---

# <Recipe Name>

> **Quick reference.** This recipe pulls live data from Liongard and produces a
> <single-system | system-type | domain | environment | compliance> artifact. Edit the
> **Customize for your MSP** block below before first use; the rest of the file is the
> agent's playbook.

---

## Customize for your MSP

Edit these knobs before first use. Re-edit when your standards change. The agent reads
this block and adapts every downstream output.

```yaml
output:
  format: markdown            # markdown | html | word | pptx | xlsx
                              # Set here to skip the pre-flight format question (see recipes/AGENTS.md § 3).
  audience_type: internal     # internal | external
                              # internal: verification log included; health timestamp optional.
                              # external: verification log OMITTED; health section MUST show
                              #   "Data as of: YYYY-MM-DD" timestamp per inspector.
                              # Set here to skip the pre-flight audience question.
  filename: "<artifact>-<customer>-<period>.md"
  # brand: inherits from config/msp-config.yaml — override per-recipe only
  #   when a deliverable needs a different brand (e.g., co-branded white-label).

sections:
  # Rename headings to match your report templates. Set to null to suppress a section.
  executive_summary: "Executive Summary"
  data_overview: "<System Type> Overview"
  health_metrics: "Health & Compliance"
  detail_table: "Detail Table"
  insights: "Key Insights"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"
  appendix: "Appendix — Methodology"

audience:
  tone: "balanced"           # technical | balanced | executive
  reading_level: "manager"   # engineer | manager | executive

slas:
  # Override these to match your standards. The agent will compare evaluated values
  # against these thresholds when computing health/compliance status.
  patch_age_days_max: 30
  mfa_coverage_pct_min: 95
  edr_coverage_pct_min: 95
  agent_uptodate_pct_min: 95
  license_expiration_warn_days: 30
  inspector_lastseen_days_max: 7

inspectors_in_scope:
  # List the inspectors you actually deploy. The agent will gracefully skip any
  # inspector listed in the recipe but absent from this list.
  - <inspector-slug>
  - <inspector-slug>

naming:
  client_term: "Client"      # how you refer to customers (Client | Tenant | Customer)
  environment_term: "Environment"
  site_term: "Site"

reporting_period:
  default: "last_quarter"    # last_quarter | last_30_days | last_year | custom
  fiscal_year_start_month: 1

qa:
  # See reference/qa-retry-pattern.md for the full QA + manual-verification spec.
  # The QA pass runs after data collection and before output is rendered.
  retry_on_null: true
  retry_on_empty_array: false
  retry_attempts: 2                              # extra attempts after the first
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: true
  surface_single_source_visibility: true
  manual_verification_section_required: true    # appendix mandatory in deliverable
```

---

## When to use

Trigger phrases that should map to this recipe:
- "<trigger phrase 1>"
- "<trigger phrase 2>"
- "<trigger phrase 3>"

Cadence: <on-demand | weekly | monthly | quarterly | annual>.
Persona fit: <persona(s)>.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` → match by name |
| System ID | <Yes/No> | `liongard_system LIST searchMode=keyword query="<inspector-keyword>"` |
| Reporting period | No (default from customization block) | User prompt |
| Customer / tenant name | No | Used for filename + report header |

---

## Liongard data sources

> **Asset Inventory First, Metric Cross-Check.** When the question can be answered
> from the cross-inspector asset record (identity-level or device-level attribute
> like MFA, account activity, AV/EDR, OS, privileged), the agent **must** filter the
> asset inventory first. Per-inspector metrics are run as a cross-check or for fields
> the asset doesn't expose. When the two disagree, the asset value wins and the
> divergence is surfaced as a data-quality flag.

### Inspector(s) covered

| Inspector | Slug | ID | Target System Type | Notes |
|---|---|---|---|---|
| <Display Name> | `<inspector-slug>` | <id> | <target-type> | <parent/child? per-site? rate-limited?> |

### Locating the right system

```
liongard_system LIST searchMode=keyword query="<keyword>" environmentId=<ENV_ID>
```

<Add per-inspector notes — parent vs. child systems, how to identify the correct child,
which dataprint key holds the tenant name.>

### Primary evidence — reconciled asset inventory

Three dedicated tools provide the cross-inspector reconciled asset inventory.
**Use these directly with structured filters and the `COUNT` operation —
prefer them to `liongard_metric` for any attribute Liongard reconciles across
inspectors.**

| Tool | Use for | Dedup key |
|---|---|---|
| `liongard_device` | Devices: hostname, IP/MAC, OS, serial, manufacturer, model, AV/EDR, warranty, EOL, virtualization, inspectors[] | hostname / serial number / MAC address (any of three) |
| `liongard_identity` | Identities: email, MFA status / method, privileged, enabled, account activity, department, membership, license SKUs, billable, support status, inspectors[] | email address |
| `liongard_domain` | Domains: registrar, expiration, days till expiration, DMARC health, email/website detection, IPv4/IPv6, ASN, managed flag, inspectors[] | domain name |

> **Each tool returns one record per real-world entity**, joined across every
> inspector that observed it. The `inspectors[]` array on each record lists
> the joined inspectors and is the most useful coverage signal —
> a device with only one inspector in the array (e.g., `active-directory-inspector`
> alone) is a coverage gap to flag. See
> [`reference/asset-fields.md`](../reference/asset-fields.md) § Deduplication
> keys for details.

> **Note:** the legacy `liongard_asset` tool has been removed from the catalog —
> do not use it in recipes. The three tools above are the supported path.

> **Use `liongard_cyber_risk_dashboard` for category counts** (M365 users,
> Windows workstations, Windows servers, macOS, AD users, etc.). Use the
> dedicated tools' `COUNT` operation for attribute-based counts (e.g.,
> "identities with mfaStatus = NO in env X").

> **For cross-cutting / time-bounded recipes** (PBR, onboarding,
> roadmap, sales discovery, compliance), see
> `reference/cross-cutting-signals.md` for the broader MCP toolset
> (`liongard_detection`, `liongard_alert`, `liongard_timeline`,
> `liongard_cyber_risk_dashboard`, `liongard_events`, `liongard_query`,
> `liongard_report`). Per-system recipes do not need these tools; they
> are the spine of cross-cutting recipes that produce time-bounded
> narrative reports like "what changed in the last 90 days?".

#### Operations available on every tool

| Operation | Purpose |
|---|---|
| `LIST` | Filtered listing with pagination. All filter parameters listed in the tool description (camelCase). |
| `GET` | Single record by UUID. |
| `COUNT` | Returns count(s) without pagination overhead. **For `liongard_identity`, returns a `StatusCounts[]` breakdown by InventoryState + MfaStatus** — surface this when present. |

#### Common patterns — server-side filters (preferred) vs. JMESPath fallback

Most filtering should happen via tool parameters. JMESPath/client-side filtering
is the fallback when a needed condition isn't a parameter.

**Identity:**

```
# Server-side: count identities without MFA in an environment
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true

# Server-side: privileged users without MFA
liongard_identity LIST environmentId=<ENV_ID> privileged=true mfaStatus="NO"

# Server-side: stale-but-enabled accounts (filter accountActivity client-side)
liongard_identity LIST environmentId=<ENV_ID> enabled=true accountActivity="Stale"

# Server-side + projection: just emails of users with E3 license
liongard_identity LIST environmentId=<ENV_ID> fields=["email","emailLicenses"]

# Field combinations not as direct parameters → still fetch + JMESPath
# e.g. "Identities with EmailLicenses contains 'E3' AND Department == 'Finance'"
```

**Device:**

```
# Server-side: lookup by hostname
liongard_device LIST hostname="<hostname>" environmentId=<ENV_ID>

# Server-side: by serial / MAC / IP
liongard_device LIST serialNumber="<serial>"
liongard_device LIST macAddress="<mac>"
liongard_device LIST ipAddress="<ip>"

# Server-side: hardware inventory by manufacturer
liongard_device LIST manufacturer="Lenovo" environmentId=<ENV_ID>

# Server-side: by OS family + virtualization
liongard_device LIST operatingSystem="Windows Server" physical=true environmentId=<ENV_ID>

# Server-side: managed-device count
liongard_device COUNT managedDevice=true environmentId=<ENV_ID>

# JMESPath fallback for compound filters
# e.g. "EDR == null AND inspectors contains 'windows-workstation-inspector'"
# → LIST then filter client-side
```

**Domain:**

```
# Server-side: domains expiring within 30 days
liongard_domain LIST maxDaysTillExpiration=30 environmentId=<ENV_ID>

# Server-side: DMARC health audit
liongard_domain LIST dmarcHealth="not-valid" environmentId=<ENV_ID>
liongard_domain LIST dmarcHealth="not-found" environmentId=<ENV_ID>

# Server-side: by registrar
liongard_domain LIST registrar="GoDaddy" environmentId=<ENV_ID>

# Server-side: domains with email but no website (or vice versa)
liongard_domain LIST emailDetected=true websiteDetected=false environmentId=<ENV_ID>
```

> **Field reference.** See `reference/asset-fields.md` for the complete field
> map per tool — every queryable field, value shapes, source inspectors, and
> ready-to-use patterns (hardware inventory, license distribution, refresh
> roadmap, identity↔device joins, virtualization topology, network exposure,
> domain expiration roadmap, DMARC posture).
>
> Recipes do **not** redefine the field list — link to the centralized
> reference.

> **Coverage gap rule.** A device with only `active-directory-inspector` in
> `inspectors[]` is *not locally inspected*; `antivirus`/`edr` will be null
> because Liongard cannot confirm them, not because the products are absent.
> Surface this as a 🔍 REVIEW (coverage gap) — distinct from a ❌ NON-COMPLIANT
> (locally inspected, EDR genuinely missing).

### Cross-check evidence — per-metric evaluation (`liongard_metric EVALUATE`)

For questions that need an inspector-unique field the asset doesn't expose
(e.g., AD password policy, Conditional Access policy names, firewall rule counts,
NSG exposed ports), or as a quantitative cross-check on the asset answer, evaluate
the listed metrics:

```
liongard_metric EVALUATE metricId=<METRIC_ID> systemId=<SYS_ID> environmentId=<ENV_ID>
```

| # | Question / Section | Metric ID | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|---|---|
| 1 | <what this answers> | `<id>` | <inspector> | <name> | `<jmespath>` | <threshold> |

**When metric and asset disagree:** the asset value is authoritative; the recipe
records the divergence in the data-gaps section and recommends inspector hygiene
(recent re-run, sync confirmation, missing inspector deployment).

> **Scrub note:** Never paste concrete evaluated values into the recipe. Use shape
> annotations only: `<integer>`, `<bool>`, `<ISO timestamp>`, `<set<string>>`, etc.

---

## Output formats

The agent picks the format from the customization block (`output.format`). Each format
has a default layout below; the MSP can override section names via `sections.*` in the
customization block.

### Markdown (default)
Sections in order: Executive Summary → Data Overview → Health Metrics → Detail Table →
Insights → Recommendations → Data Gaps → Appendix. Use tables for tabular data, fenced
code blocks for query references, and a "Verification Log" appendix.

<!-- INSPECTOR HEALTH SECTION — conditional field -->
<!-- IF audience_type == external: each inspector row MUST include a "Data as of:"     -->
<!--   timestamp derived from latestInspectionDate. Format: YYYY-MM-DD HH:MM UTC.      -->
<!--   Example row: | SentinelOne | ✅ Active | Data as of: 2026-05-28 14:32 UTC |     -->
<!-- IF audience_type == internal: timestamp is optional; status column is sufficient. -->
<!-- See recipes/AGENTS.md § 4 and § 5 for HTML-specific timestamp rendering guidance.          -->

### Word (.docx)
See `templates/output-block-word.md`. Uses heading styles (Heading 1 / 2 / 3),
auto-generated TOC, page numbers, MSP letterhead from `output.brand`. One-page Executive
Summary first; detail tables follow.

### PowerPoint (.pptx)
See `templates/output-block-pptx.md`. Cover slide → KPI dashboard slide → one slide per
section heading → recommendations slide → appendix slide. Charts where the data shape
supports it (donut for coverage %, bar for counts, line for trends from time-series).

### Excel (.xlsx)
One sheet per logical section: KPIs, Detail, Insights, Gaps. Conditional formatting on
Status column (✅/⚠️/❌). Suitable for compliance evidence packs.

---

## Cross-cutting recipe pattern (OMIT for single-system recipes)

> **Use this section only for cross-cutting recipes** — environment
> quarterly lookback, onboarding assessment, roadmap planning, sales
> assessment, compliance / cyber-insurance / CMMC / HIPAA. Per-system
> single recipes do not need this section.

Cross-cutting recipes produce time-bounded narrative reports. The
deliverable shape MSPs ask for:

> *"What material changes, alerts, inventory have happened over the
> last 90 days / 3 months since X date?"*

The pattern has **10 standard steps** documented in
`reference/cross-cutting-signals.md`. Recipes follow it inline:

### Step 1 — Scope discovery

```
liongard_environment LIST → confirm environmentId
```

### Step 2 — Define time window from customization block

```yaml
reporting_period:
  default: "last_quarter"   # last_30_days | last_90_days | last_quarter | last_year | since_date | custom
  fiscal_year_start_month: 1
  since_date: ""
  custom_start: ""
  custom_end: ""
```

Compute `window_start` and `window_end`.

### Step 3 — Inspection timeline + freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
                       startDate=<window_start>
                       endDate=<window_end>
```

Surface inspector freshness; flag inspectors that didn't run in window.

### Step 4 — Headline KPIs (category counts)

```
liongard_cyber_risk_dashboard <metric>  environmentId=<ENV_ID>
```

Use for the executive KPI dashboard slide.

### Step 5 — Current-state inventory snapshot

```
liongard_device LIST environmentId=<ENV_ID>
liongard_identity LIST environmentId=<ENV_ID>
liongard_domain LIST environmentId=<ENV_ID>
```

Prefer COUNT operations for attribute-based counts.

### Step 6 — Material changes in window

```
liongard_detection LIST environmentId=<ENV_ID>
                        startDate=<window_start> endDate=<window_end>
```

Group by severity, system, detection type. **Primary narrative content
for PBR / quarterly-lookback recipes.**

### Step 7 — Alerts in window

```
liongard_alert LIST environmentId=<ENV_ID>
                    startDate=<window_start> endDate=<window_end>
```

Group by severity, triage outcome, recurring patterns.

### Step 8 — Auto-discover deployed inspectors + chain sub-recipes

```
liongard_system LIST environmentId=<ENV_ID>
```

Group systems by inspector slug. For each class:
- One system → run `recipes/single-system-analysis/by-inspector/<slug>.md`
- Multiple → run `recipes/system-type-assessment/all-<category>.md`
  if one exists, else iterate

This is the **customer-stack-adaptive** layer — recipe doesn't
hard-code a stack, it discovers what's deployed.

### Step 9 — QA pass (per `reference/qa-retry-pattern.md`)

Stale-inspector flags from Step 3 land in the manual-verification
appendix. Cross-tool divergence between cyber-risk-dashboard
aggregates and the reconciled asset inventory counts gets flagged.

### Step 10 — Render time-bounded narrative

Narrative output (analyst-style), not data dump. Default format depends
on recipe purpose:
- PBR / quarterly: PowerPoint executive deck + Word written report
- Onboarding: Excel intake workbook + Word narrative
- Roadmap: Excel forecast + Word memo
- Sales: PowerPoint pitch deck
- Compliance: Excel evidence workbook

### Customer-stack adaptation block (add to the recipe's customization YAML)

```yaml
stack:
  auto_discover: true                 # discover deployed inspectors via liongard_system LIST
  inspectors_in_scope: []             # explicit list overrides auto-discovery
  inspectors_to_skip: []              # exclusions

per_class_recipe_overrides:
  # cisco-meraki-inspector: "<msp-local-path>/meraki-custom.md"
```

---

## QA & Manual Verification

Before rendering output, run the QA pass per `reference/qa-retry-pattern.md`:

1. **Retry persistent nulls.** For every metric / asset / domain / identity
   call that returned `null` (or status that indicates failure), re-run up
   to `qa.retry_attempts` times with `qa.retry_delay_seconds` between
   attempts. Cache the final result. Persistent nulls go to the manual-
   verification list.

2. **Flag stale inspectors.** For every system used by this recipe, check
   `lastSeen`. If older than `qa.flag_inspector_lastseen_threshold_days`,
   surface as a stale-data flag.

3. **Cross-tool divergence check.** If the recipe answers any question via
   two paths (e.g., `liongard_identity COUNT mfaStatus="NO"` vs. an
   inspector-specific metric), compare the values. If divergent by more
   than `qa.flag_count_divergence_threshold_pct`, surface both with the
   asset value as authoritative.

4. **List this recipe's known proposed-metric gaps.** Recipes that depend
   on metrics not yet in the library should list them explicitly:

   ```yaml
   proposed_metric_gaps:
     - field: <field name>
       fallback: <what we did instead>
       remediation: "Confirm in <vendor> console; tracking <CORE-XXXX>"
   ```

5. **Single-source visibility flags.** Surface devices / identities seen by
   only one inspector when this recipe needs cross-inspector data
   (e.g., AV/EDR coverage on a device with only `active-directory-inspector`).

6. **Render the "Manual Verification Needed" appendix** in the deliverable
   (mandatory when `qa.manual_verification_section_required == true`).
   Format per `reference/qa-retry-pattern.md`. If QA produced zero items,
   say so explicitly: "✅ All evidence verified — no manual checks needed."

## Coverage cross-check (REQUIRED — recipe-author fills before shipping)

Every new recipe runs the four-source coverage check (per
`CONTRIBUTING.md` § 8) and documents the result here. Format:

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` (partner QA matrix) | ✅ / ⚠️ / ❌ / n/a | Which of the six standard questions are addressed; gaps flagged with cross-check path |
| CIS Controls (v8.1) mapping | ✅ / ⚠️ / ❌ / n/a | Mapped controls (e.g., 5.1, 5.3, 5.4); only required for SOC / TAM / compliance recipes |
| Cyber-insurance domain files | ✅ / ⚠️ / ❌ / n/a | Which domain file (`auth`, `endpoint`, `backup`, `network`, `governance`, `regulatory`, `vendor`) the recipe aligns with; gaps flagged |
| QBR / quarterly-business-review | ✅ / ⚠️ / ❌ / n/a | Highlights the QBR's Step 8 can consume from this recipe |

If the check surfaces a gap that requires a new Liongard metric, file a
metric request with Liongard via the `liongard-metrics` skill and reference
the response here.

> **Why this matters:** Recipes that skip the cross-check ship with
> predictable blind spots — questions the MSP's audience expects an
> answer to, but the recipe never asks. The four sources are the
> project's accumulated wisdom about what those questions are.

---

## Insights & recommendations — generation patterns

After fetching data, the agent computes these insights (subject to SLA thresholds in the
customization block):

| Insight | Trigger | Recommended action template |
|---|---|---|
| <e.g., MFA coverage below SLA> | `mfa_coverage_pct < slas.mfa_coverage_pct_min` | "Enroll <N> remaining users in MFA via <inspector>." |
| <e.g., agents out of date> | `outOfDate > 0` | "Push agent update to <N> endpoints; investigate offline ones." |
| <e.g., license expiring soon> | `daysUntilExpiration < slas.license_expiration_warn_days` | "Initiate renewal with <vendor> for <N> seats." |

---

## Data gaps & coverage notes

Always include a Data Gaps section in the output. Populate it from:
- Inspectors listed in the recipe but missing from the customer's environment.
- Metrics that returned `null` (system not inspected or inspector not yet configured).
- Devices/identities present in one inspector but missing from the asset inventory.
- `lastSeen` older than `slas.inspector_lastseen_days_max` (stale inspector).

A gap is **not** a non-compliance — it's a visibility limitation. Mark with `🔍 REVIEW`
status and recommend a remediation step (e.g., "Connect the X inspector to confirm Y").

---

## Verification log (agent appends, MSP reviews)

<!-- CONDITIONAL: INCLUDE IF audience_type == internal | OMIT IF audience_type == external -->
<!-- For external-facing output (HTML or MD), omit this section entirely.               -->
<!-- See recipes/AGENTS.md § 4 — render rules.                                                   -->

Every run, the agent appends a log of every query it ran and the **shape** of the result
(no concrete values). This makes the report auditable without leaking customer data into
the library.

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | — | array<environment> | ok |
| 2 | liongard_system LIST | query=<keyword> envId=<ENV_ID> | array<system> | ok |
| 3 | liongard_metric EVALUATE | metricId=<id> sysId=<SYS_ID> envId=<ENV_ID> | <integer> | ok |
| 4 | liongard_identity COUNT | envId=<ENV_ID> mfaStatus="NO" enabled=true includeStatusCounts=true | {Count, statusCounts[]} | ok |
```

---

## Notes for authors

- **Strip evaluated examples** — see scrub policy in `CONTRIBUTING.md`.
- **Metric references** must resolve to a defined primitive in
  `primitives/metrics/<inspector>.yaml` (the registry source of truth; `Liongard-Metrics.xlsx`
  is retired). Every `@id` in the frontmatter `primitives:` list must exist there — Gate 7
  fails on dangling references. If you need a metric that doesn't exist yet, validate it live
  with `liongard_metric` and add it to the matching `primitives/metrics/<inspector>.yaml`
  file, or flag it in the Data Gaps section of your recipe as a future-build opportunity.
- **Inspector slugs / IDs** must match `reference/inspector-name-system-id-mapping.xlsx`.
- **Frontmatter `description`** controls auto-trigger. Lead with "Use this skill when…"
  and include the most-likely user phrasings.

# Cross-Cutting MCP Signals — Reference

Per-system recipes pull data from one inspector via `liongard_metric` +
the reconciled asset inventory (`liongard_device` / `liongard_identity` /
`liongard_domain`). **Cross-cutting recipes** — Periodic Business Reviews,
onboarding assessments, roadmap planning, sales assessments, compliance
evidence — need **broader environment-level signals** that aren't tied to
a single inspector.

This file is the canonical reference for those broader signals. Recipes
that produce time-bounded narrative reports ("what changed in the last
90 days?", "what's the state of the customer right now?") link here.

> **Pairs with:** `reference/asset-fields.md` (the reconciled-asset
> inventory tools for current-state snapshots), `reference/qa-retry-pattern.md`
> (the QA pass every recipe runs before rendering output).

## The deliverable shape

The MSP's customer-facing question is almost always:

> *"What material changes, alerts, inventory have happened over the
> last 90 days / 3 months since X date?"*

That sentence implies four things every cross-cutting recipe must answer:

1. **Time-bounded** — the window is part of the request (last 30 days,
   last quarter, last year, since a specific date, custom range)
2. **Material changes** — what actually changed in that window?
3. **Alerts** — what triggered MSP-monitored alerts in that window?
4. **Inventory state** — what does the environment look like *now*, as
   the baseline for the next window?

Plus an executive overlay: **rolled-up KPIs** suitable for the
customer's leadership.

## The MCP tools

| Tool | What it answers | Time-window aware? |
|---|---|---|
| `liongard_environment` | Tenant identity + metadata | n/a — scope-setter |
| `liongard_timeline` | When was each inspector last run? How fresh is the data? Has inspection coverage degraded? | Yes — query a window for inspection events |
| `liongard_cyber_risk_dashboard` | Pre-aggregated category counts: M365 user totals, AD user totals, workstation / server / macOS counts, MFA / EDR / patch dashboards | Mostly current-state; some metrics support comparison |
| `liongard_device` / `liongard_identity` / `liongard_domain` | Current-state reconciled inventory by asset type | Current-state |
| `liongard_detection` | **Change-detection events** — what materially changed on a system in the window | Yes — the core "what changed?" signal |
| `liongard_alert` | Alerts triggered in the window — which detections crossed an MSP-configured alert threshold | Yes |
| `liongard_events` | Lower-level event log (less curated than detections / alerts) | Yes |
| `liongard_query` | Ad-hoc query engine for cases the other tools don't cover | Optional |
| `liongard_report` | Pre-built report compositional units | n/a |
| `liongard_metric` (EVALUATE / EVALUATE_TIME_SERIES) | Per-inspector dataprint evaluation; time-series for trend charts | Yes via EVALUATE_TIME_SERIES |
| `liongard_navigate` / `liongard_launchpoint` | Navigation + launchpoint config helpers | n/a |

## Zero-credential discovery category (external attack surface)

A subset of inspectors run **without any customer credential** — they
pull from public-internet probes (WHOIS, DNS, TLS handshake, IP
reputation, breach corpus). These power the "Phase 0" sections of
discovery / onboarding / PBR recipes:

| Inspector | What it answers | Per-system recipe |
|---|---|---|
| `internet-domain-dns-inspector` | Registration, WHOIS, DNS, mail trust (SPF / DKIM / DMARC), NS health, expiration | `recipes/single-system-analysis/by-inspector/internet-domain-dns.md` |
| `tls-ssl-inspector` | Cert validity, protocol versions, cipher strength, known vulnerabilities, HSTS | `recipes/single-system-analysis/by-inspector/tls-ssl.md` |
| `network-ip-inspector` | Public IP reputation, blocklist / RBL status, exposed services, hosting / ASN | `recipes/single-system-analysis/by-inspector/network-ip-address.md` |
| `dark-web-inspector` | Breach-corpus matches per domain (joined with identity inventory when available) | `recipes/single-system-analysis/by-inspector/dark-web-monitoring.md` |

Rollup: `recipes/system-type-assessment/all-external-attack-surface.md`
— the flagship pre-sales recipe; combines all four for the complete
outside-in view.

Cross-cutting recipes (PBR, onboarding, sales-discovery, cyber-insurance,
CMMC, roadmap) chain this rollup as their zero-credential phase.

## Cross-cutting recipe workflow

Every cross-cutting recipe follows this 10-step pattern. Some steps are
optional depending on the recipe's purpose (onboarding is mostly
current-state; PBR is mostly window-bounded; roadmap is forward-looking).

### Step 1 — Scope discovery

```
liongard_environment LIST (or GET by name) → confirm environmentId
```

If multi-environment in scope, repeat per environment.

### Step 2 — Define time window

From the recipe's customization block:

```yaml
reporting_period:
  default: "last_quarter"   # last_30_days | last_90_days | last_quarter | last_year | since_date | custom
  fiscal_year_start_month: 1
  since_date: ""            # ISO date — only when default == "since_date" or "custom"
  custom_start: ""
  custom_end: ""
```

Compute `window_start` and `window_end` from the user's input.

### Step 3 — Inspection timeline + freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
                       startDate=<window_start>
                       endDate=<window_end>
```

Surface:
- **Inspectors that ran during the window** — confirm data freshness for
  every system the report cites
- **Inspectors that didn't run** — stale-data flag (every assertion
  about that inspector should be marked accordingly)
- **Inspector reconnects / disconnects in window** — operational change
  worth narrating

### Step 4 — Headline KPIs (category counts)

```
liongard_cyber_risk_dashboard <metric_name> environmentId=<ENV_ID>
```

Pre-aggregated counts that drive the executive KPI dashboard slide:

| Metric (representative) | What it answers |
|---|---|
| `m365TotalUsers` | M365 user count |
| `activeDirectoryTotalUsers` | AD user count |
| `workstationTotalCount` | Windows workstation count |
| `winServerTotalCount` | Windows Server count |
| `macOSTotalCount` | macOS device count |
| MFA / EDR / patch coverage dashboards | Headline coverage %s |
| `domainAndWebsiteSecurityTotalDomains` | Domain count |

Use the cyber-risk-dashboard tool's discovery / list helpers to enumerate
the available metrics in the current Liongard version — the metric set
expands over time.

### Step 5 — Current-state inventory snapshot

```
liongard_device LIST environmentId=<ENV_ID>
liongard_identity LIST environmentId=<ENV_ID>
liongard_domain LIST environmentId=<ENV_ID>
```

Use `COUNT` operations for attribute-based counts where pagination isn't
needed (per `reference/asset-fields.md`).

### Step 6 — Material changes in window

```
liongard_detection LIST environmentId=<ENV_ID>
                        startDate=<window_start>
                        endDate=<window_end>
```

Group detections by:
- **Severity** (if exposed) — critical / high / medium / low
- **System / inspector** — where did the change occur?
- **Detection type** — config change, drift from baseline, new asset
  appeared, etc.

For PBR / quarterly-lookback recipes, this is the **primary narrative
content** — "12 material changes occurred this quarter; here they are
in priority order."

### Step 7 — Alerts in window

```
liongard_alert LIST environmentId=<ENV_ID>
                    startDate=<window_start>
                    endDate=<window_end>
```

Alerts are the subset of detections that crossed an MSP-configured
threshold and notified the team. Group by:
- **Severity**
- **Triage outcome** — resolved, in-progress, dismissed, escalated
- **Mean time to resolve** if exposed
- **Recurring alerts** — same condition firing repeatedly = remediation
  candidate

For SOC-driven recipes, this is the primary content; for PBR it's
secondary to the detections list.

### Step 8 — Auto-discover deployed inspectors + chain per-system / per-system-type recipes

```
liongard_system LIST environmentId=<ENV_ID>
```

Group by inspector slug to identify which inspector classes the
customer has connected. For each class, decide:

- **One system of this inspector class** → run the per-system recipe
  at `recipes/single-system-analysis/by-inspector/<slug>.md`
- **Multiple systems of the same class** (e.g. multiple Windows
  Workstations, multiple firewalls) → run the system-type rollup at
  `recipes/system-type-assessment/all-<category>.md` if one exists,
  otherwise iterate per-system

This is the **customer-stack-adaptive** part — the recipe doesn't
hard-code a stack; it discovers what's deployed and runs the right
sub-recipes.

### Step 9 — QA pass

Per `reference/qa-retry-pattern.md`. Cross-cutting recipes especially
benefit from:

- **Stale-inspector flags** for any inspector that didn't run in the
  window (the timeline check at Step 3 produced this list)
- **Cross-tool divergence checks** between `cyber-risk-dashboard`
  aggregates and the reconciled asset inventory counts
- **Proposed-metric gaps** for any inspector class where the
  cross-cutting recipe wanted a metric that's still on the
  metric-request backlog

### Step 10 — Render the time-bounded narrative

Cross-cutting recipes default to a **narrative** output format — a
report that reads like an analyst wrote it, not a data dump. Typical
shape:

```
Executive Summary (2 paragraphs, outcome-led)
Headline KPIs (4–6 tiles: coverage %, asset counts, alert counts, key risks)

What changed in the window (the detections narrative)
  - Critical changes
  - Notable but lower-priority changes
  - No-op categories (helpful to call out)

What we alerted on
  - Resolved
  - Outstanding
  - Recurring patterns

Current-state inventory snapshot
  - Composition by class / OS / vendor
  - Lifecycle risks (Win10 EOL, expiring licenses, out-of-warranty)
  - Coverage gaps (EDR, backup, MFA, etc.)

Per-inspector deep-dives (auto-generated for deployed inspectors)
  - One section per inspector class with key findings

Recommended actions (prioritized)
Data gaps and manual verification needed
Appendix — methodology + verification log
```

Output format defaults vary by recipe purpose:
- PBR / quarterly: PowerPoint executive deck + Word written report
- Onboarding: Excel intake workbook + Word narrative
- Roadmap: Excel forecast + Word memo
- Sales: PowerPoint pitch deck
- Compliance (CMMC, etc.): Excel evidence workbook

## Customer-stack adaptation

The cross-cutting recipe's customization block should expose:

```yaml
stack:
  # Auto-discover from liongard_system LIST by default. Manual override
  # available for cases where the MSP wants to scope intentionally
  # (e.g., "skip this customer's third-party-managed firewalls").
  auto_discover: true
  inspectors_in_scope: []        # explicit list overrides auto-discovery
  inspectors_to_skip: []         # exclusions from auto-discovery

per_class_recipe_overrides:
  # Map an inspector slug (or system-type-rollup name) to a custom
  # per-MSP recipe path. Defaults to the library recipes when not
  # overridden.
  # cisco-meraki-inspector: "<msp-local-path>/meraki-custom.md"
```

When MSPs run the recipe against a real customer, the customization
block is the single point of stack adaptation — the recipe doesn't need
forking.

## Patterns for common time windows

| Window | window_start | window_end |
|---|---|---|
| `last_30_days` | today − 30 days | today |
| `last_90_days` | today − 90 days | today |
| `last_quarter` | start of previous fiscal quarter | end of previous fiscal quarter |
| `last_year` | start of previous fiscal year | end of previous fiscal year |
| `since_date` | `<customization.since_date>` | today |
| `custom` | `<customization.custom_start>` | `<customization.custom_end>` |

Fiscal quarter / year math uses `customization.fiscal_year_start_month`
(default 1 = January; 7 = July fiscal start, etc.).

## Tool description reminders

The Liongard MCP servers expose multiple instances of each tool
(multiple MCP instances). Always confirm the inspector schemas
via the active MCP tool description (the tool's `description` field
documents the exact filter parameter shapes and operation semantics)
before writing a recipe section that depends on a specific field.

The reconciled asset-inventory tools (`liongard_device` /
`liongard_identity` / `liongard_domain`) are documented in
`reference/asset-fields.md`; the broader cross-cutting signals here
(`liongard_detection` / `_alert` / `_timeline` / `_cyber_risk_dashboard`
etc.) are documented in this file.

## Maintenance

When new cross-cutting MCP tools land or existing ones gain new
operations / filter parameters:

1. Update the tool table at the top of this file.
2. Add the new pattern to the workflow steps below if it changes
   recipe authoring (e.g., a new "behavior-change" tool would slot in
   between Steps 6 and 7).
3. Update `templates/recipe-skeleton.md`'s cross-cutting signals
   section to surface the new pattern.
4. Update each existing cross-cutting recipe to incorporate the new
   signal if it's broadly applicable.

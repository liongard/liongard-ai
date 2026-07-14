---
name: system-type-all-edrs
description: >
  Use this skill when the user wants a unified EDR posture across every EDR
  deployed in an environment — fleet view of agent counts, coverage gaps,
  active threats, and per-vendor health. Trigger phrases: "EDR fleet review",
  "all-EDR coverage report", "unified EDR posture for <CUSTOMER>", "compare
  EDR coverage across vendors". Iterates each deployed EDR (SentinelOne,
  Huntress, Sophos Central, Webroot, Bitdefender, CrowdStrike, ESET, SonicWall
  Capture Client) and rolls up to one fleet-level report.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [vcio-account-manager, soc, technical-alignment-manager]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  - metrics:bitdefender-gravityzone:endpoint-detail
  - metrics:bitdefender-gravityzone:online-endpoints
  - metrics:bitdefender-gravityzone:total-endpoints
  - metrics:crowdstrike:high-risk-users-list
  - metrics:crowdstrike:inactive-users-count-30d
  - metrics:crowdstrike:no-rtr-count
  - metrics:crowdstrike:reduced-functionality-mode-count
  - metrics:crowdstrike:stale-hosts-count-30d
  - metrics:crowdstrike:stale-hosts-count-7d
  - metrics:crowdstrike:stale-hosts-list-30d
  - metrics:crowdstrike:users-without-mfa-count
  - metrics:eset-inspector:count-licenses-in-error
  - metrics:eset-inspector:count-licenses-in-warning
  - metrics:eset-inspector:count-licenses-suspended
  - metrics:eset-inspector:count-of-active-users
  - metrics:eset-inspector:count-of-privileged-users
  - metrics:eset-inspector:count-trial-licenses-expiring-30d
  - metrics:eset-inspector:count-users-waiting-activation
  - metrics:eset-inspector:license-usage-summary
  - metrics:eset-inspector:list-licenses-in-error
  - metrics:eset-inspector:list-licenses-in-warning
  - metrics:eset-inspector:list-licenses-suspended
  - metrics:eset-inspector:list-of-active-users
  - metrics:eset-inspector:list-of-privileged-users
  - metrics:eset-inspector:list-trial-licenses-expiring-30d
  - metrics:eset-inspector:list-users-waiting-activation
  - metrics:huntress:active-incidents-count
  - metrics:huntress:agents-total-count
  - metrics:huntress:unresponsive-agents-count-21d
  - metrics:huntress:unresponsive-agents-count-30d
  - metrics:huntress:unresponsive-agents-count-60d
  - metrics:huntress:unresponsive-agents-list-21d
  - metrics:huntress:unresponsive-agents-list-30d
  - metrics:huntress:unresponsive-agents-list-60d
  - metrics:sentinelone:active-licenses
  - metrics:sentinelone:agents-decommissioned
  - metrics:sentinelone:agents-infected
  - metrics:sentinelone:agents-online
  - metrics:sentinelone:agents-out-of-date-count
  - metrics:sentinelone:agents-total
  - metrics:sentinelone:agents-up-to-date
  - metrics:sentinelone:console-users-with-api-tokens-list
  - metrics:sentinelone:console-users-without-mfa-list
  - metrics:sentinelone:days-until-license-expiry
  - metrics:sentinelone:infected-agents-list
  - metrics:sentinelone:threats-malicious-unresolved
  - metrics:sentinelone:threats-resolved
  - metrics:sentinelone:threats-total
  - metrics:sentinelone:threats-unresolved
  - metrics:sentinelone:total-licenses
  - metrics:sonicwall-capture-client-inspector:active-endpoints-list
  - metrics:sonicwall-capture-client-inspector:count-active-endpoints
  - metrics:sonicwall-capture-client-inspector:count-infected-endpoints
  - metrics:sonicwall-capture-client-inspector:count-offline-endpoints
  - metrics:sonicwall-capture-client-inspector:count-total-endpoints
  - metrics:sonicwall-capture-client-inspector:infected-endpoints-list
  - metrics:sonicwall-capture-client-inspector:offline-endpoints-list
  - metrics:sonicwall-capture-client-inspector:total-endpoints-list
  - metrics:sonicwall-capture-client-inspector:users
  - metrics:sophos-central:device-encryption-installed-count
  - metrics:sophos-central:device-encryption-not-installed-count
  - metrics:sophos-central:device-encryption-not-installed-list
  - metrics:sophos-central:endpoint-protection-installed-count
  - metrics:sophos-central:endpoint-protection-not-installed-count
  - metrics:sophos-central:endpoint-protection-not-installed-list
  - metrics:sophos-central:endpoints-total-count
  - metrics:sophos-central:intercept-x-installed-count
  - metrics:sophos-central:intercept-x-not-installed-count
  - metrics:sophos-central:intercept-x-not-installed-list
  - metrics:sophos-central:mtr-installed-count
  - metrics:sophos-central:service-health-not-good-count
  - metrics:sophos-central:service-health-not-good-list
  - metrics:sophos-central:tamper-protection-disabled-count
  - metrics:sophos-central:tamper-protection-disabled-list
  - metrics:sophos-central:threat-health-not-good-count
  - metrics:sophos-central:threat-health-not-good-list
  - metrics:webroot:active-endpoint-count
  - metrics:webroot:devices-not-checked-in-30-days-count
  - metrics:webroot:endpoint-detail
  - metrics:webroot:infected-device-count
---

# System-Type Assessment — All EDRs

> Iterates every EDR inspector deployed in the environment and produces a unified
> fleet-level report covering the **six standard onboarding-QA questions**:
> total / active 30d / inactive 60d+ / not protected / servers split / alerts.
>
> **Decision table:** `reference/onboarding-qa-coverage.md` — partner-validated
> matrix of which EDR exposes which question directly vs. requires asset-inventory
> fallback.
>
> **Per-vendor recipes** (linked deep dive when needed):
> `recipes/single-system-analysis/by-inspector/{sentinelone,huntress,sophos-central,webroot,bitdefender-gravityzone,crowdstrike,eset-licensing,sonicwall-capture-client}.md`

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-edr-fleet-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  fleet_kpis: "Fleet KPI Dashboard"
  per_vendor: "Per-Vendor Posture"
  coverage_gap: "Coverage Gap Analysis"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  edr_coverage_pct_min: 95
  unresolved_threats_max: 0

inspectors_in_scope:
  # Set to which EDRs you actually deploy. Empty = use all that exist in env.
  - sentinelone-inspector
  - huntress-inspector
  - sophos-central-inspector
  # - bitdefender-gravityzone-inspector
  # - crowdstrike-inspector
  # - webroot-inspector
  # - eset-licensing-inspector
  # - sonicwall-capture-client-inspector

reporting_period: { default: "current_state" }
```

---

## When to use

- "How does our EDR fleet look across <customer>?"
- "Compare SentinelOne vs Sophos coverage in <env>"
- Quarterly EDR posture review at MSP fleet level
- Pre-renewal audit — which EDRs are deployed, what's the coverage % of each, are any redundant

Personas: vCIO/AM (executive summary), SOC (threat posture), TAM (deep dive).

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Reporting period | No | Default per customization |

This recipe iterates the EDR inspectors internally — no per-inspector system ID
required.

---

## Workflow

### Step 1 — Pull asset inventory (the denominator)

```
liongard_device LIST environmentId=<ENV_ID> pageSize=200
compute_devices = Devices where category == "compute"
total_compute = length(compute_devices)
```

This is the **fleet denominator** for coverage % calculations.

### Step 2 — Discover deployed EDR inspectors

```
liongard_system LIST environmentId=<ENV_ID>
```

Filter for systems whose inspector slug is in the EDR list:

```
edr_systems = [s for s in systems if s.inspector.slug in [
  'sentinelone-inspector',
  'huntress-inspector',
  'sophos-central-inspector',
  'bitdefender-gravityzone-inspector',
  'crowdstrike-inspector',
  'webroot-inspector',
  'eset-licensing-inspector',
  'sonicwall-capture-client-inspector'
]]
```

If `inspectors_in_scope` is set in the customization block, narrow to that list.

### Step 3 — For each EDR, answer the six standard questions

Use the per-EDR recipe's onboarding-QA section as the playbook. The
coverage matrix tells you which questions the EDR can answer directly and
which require asset-inventory fallback.

```
for each edr in edr_systems:
  if edr is parent system: skip; navigate to children
  for each child / per-tenant system:
    Q1 total = <metric per EDR's recipe>
    Q2 active_30d = <metric per EDR's recipe>
    Q3 inactive_60d = <metric per EDR's recipe>
    Q4 not_protected = (compute_devices - devices_seen_by_edr)
                       split into "ad_only" (not locally inspected) vs
                       "edr_specifically_missing" (locally inspected, no EDR)
    Q5 servers = <metric per EDR's recipe; fall back to asset filter if not exposed>
    Q6 alerts = <metric per EDR's recipe>
```

### Step 4 — Roll up to fleet KPIs

| Fleet KPI | Computation |
|---|---|
| Fleet EDR coverage % | `length(union of devices_seen_by_each_edr) / total_compute * 100` |
| Devices with no EDR at all | `total_compute - length(union)` |
| Devices with multiple EDRs (overlap audit) | `compute_devices where count(EDRs reporting it) > 1` |
| Total active threats across fleet | `sum(per_vendor_alerts)` |
| Per-vendor active count | one row per EDR |

### Step 5 — Coverage gap drill-down

```
# Devices with no EDR
no_edr = compute_devices where Inspectors does not contain any of [<EDR slugs>]

# Devices with EDR but no OS inspector (locally uninspected — visibility gap)
edr_but_not_os = compute_devices where Inspectors contains <any EDR>
                 AND Inspectors does not contain any local-OS inspector

# Devices with two or more EDRs (license waste / conflict)
multi_edr = compute_devices where length(Inspectors intersect EDR list) > 1
```

---

## Per-vendor coverage decision table

(See `reference/onboarding-qa-coverage.md` for the canonical matrix.)

| Inspector | Total | Active 30d | Inactive 60d+ | Not protected | Servers split | Alerts |
|---|---|---|---|---|---|---|
| SentinelOne | ✅ | ✅ | ✅ | 🔍 | ✅ | ✅ |
| Huntress | ✅ | ✅ | ✅ | 🔍 | ❌ asset fallback | ⚠️ cumulative only |
| Sophos Central | ✅ | ✅ | ✅ | ✅ direct | ✅ | ✅ |
| Bitdefender | ✅ | ✅ online | ✅ offline | 🔍 | ⚠️ VM-count only | ✅ infected |
| CrowdStrike | ✅ | ✅ | ✅ | 🔍 | ✅ | ✅ |
| Webroot | ✅ | ✅ | ✅ | ✅ deactivated | ❌ asset fallback | ✅ |
| ESET Licensing | ✅ seats | ❌ | ❌ | 🔍 | ❌ | ❌ |
| SonicWall Capture Client | ✅ | ✅ | ⚠️ | 🔍 | ❌ asset fallback | ✅ |

For ❌ and 🔍 cells, use asset-inventory fallback (`AccountType` for server split;
`Inspectors[]` set difference for not-protected).

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Fleet coverage gap | fleet coverage % < SLA | "<N> compute devices have no EDR — extend deployment." |
| Multi-EDR overlap | devices with 2+ EDRs > 0 | "<N> devices run multiple EDRs — license waste; consolidate." |
| Redundant EDR vendors | two vendors covering similar device classes | "Reduce EDR sprawl — pick one for workstations + one for servers." |
| Vendor with no posture data | ESET-only environment | "Layer a posture-capable EDR alongside ESET." |
| High alerts on one vendor | per-vendor alerts > 0 | "<vendor> has <N> active threats — triage in vendor console." |
| Stale per-vendor inspector | inspector lastSeen > 7 days | "<vendor> inspector hasn't reported in <N> days — confirm." |

---

## Data gaps & coverage notes

When per-vendor data isn't available (the ❌ cells), use the asset-inventory
fallback. Document explicitly what required fallback so the deliverable is
auditable:

```
ESET active 30d: ❌ inspector exposure — not reported
Huntress server split: 🔍 fell back to asset.AccountType filter
Webroot server split: 🔍 fell back to asset.AccountType filter
```

---

## Output format

Markdown / Word / PowerPoint / Excel per `output.format`. **xlsx** for
fleet-evidence packs (one row per device); PowerPoint for executive overview.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_device LIST | envId=<ENV_ID> | array<device> | ok |
| 3 | liongard_system LIST | envId=<ENV_ID> | array<system> | ok |
| 4 | per EDR system: liongard_metric EVALUATE | jmesPath sysId=<SYS_ID> envId=<ENV_ID> | varies | ok |
```

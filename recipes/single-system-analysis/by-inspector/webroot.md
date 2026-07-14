---
name: single-system-webroot
description: >
  Use this skill when the user wants a single-system analysis of a Webroot
  SecureAnywhere site — Periodic Business Review (PBR), endpoint deployment
  review, infection counts, deactivated-endpoint audit. Trigger phrases:
  "Webroot PBR", "WSA report", "SecureAnywhere review", "pull Webroot data
  for <CUSTOMER>". Produces an artifact in the format set in the
  customization block.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, soc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, pptx]
primitives:
  - metrics:webroot:active-endpoint-count
  - metrics:webroot:devices-not-checked-in-30-days-count
  - metrics:webroot:endpoint-detail
  - metrics:webroot:infected-device-count
---

# Single-System Analysis — Webroot SecureAnywhere

> **Inspector:** `webroot-inspector` (ID 15). Apps & Services category.
> EDR / AV (Webroot SecureAnywhere GSM).
>
> **References:** `reference/inspector-aliases.md` (Webroot, WSA,
> SecureAnywhere). `reference/onboarding-qa-coverage.md` for the per-EDR
> coverage matrix.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-webroot-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  endpoints: "Endpoint Coverage"
  threats: "Infections"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  active_pct_min: 95
  infected_max: 0
  stale_endpoint_days_max: 30

reporting_period: { default: "last_quarter" }
```

---

## When to use

- "Pull Webroot / WSA / SecureAnywhere data for <customer>"
- "How many endpoints are infected on Webroot?"
- "Any deactivated endpoints?"

Personas: NOC, SOC, vCIO/AM, TAM.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Webroot system ID | Yes | `liongard_system LIST query="webroot"` |

---

## Locating the right system

```
liongard_system LIST searchMode=keyword query="webroot" environmentId=<ENV_ID>
```

Webroot is organized by **site**. `SiteInfo.SiteName` returns the site display
name (a `<string>`).

---

## Liongard data sources

### Per-vendor data — system fields

| Key | Description |
|---|---|
| `Endpoints` | Array of enrolled endpoints: hostname, lastSeen, deactivated, infected |
| `SiteInfo` | Tenant / site metadata: name, billable seats, license expiration |

### Cross-inspector cross-check — asset inventory

```
liongard_device LIST environmentId=<ENV_ID> pageSize=200
```

```
# Devices Webroot reports on
items[?inspectors[?name=='webroot-inspector']]

# Coverage gap
items[?!inspectors[?name=='webroot-inspector'] && category == 'compute']

# Devices with Webroot in AV set
items[?contains(antivirus, 'Webroot')]
```

---

## Onboarding QA — endpoint posture

Per partner-validated matrix at `reference/onboarding-qa-coverage.md`:

| Question | JMESPath / approach | Coverage |
|---|---|---|
| Total endpoints managed | metricName=`Webroot: Active Endpoint Count` "Active Endpoint Count" | ✅ |
| Active in last 30 days | filter `Endpoints[?lastSeen > '<today − 30d>']` (proposed) | ✅ |
| Inactive 2+ months | metricName=`Webroot: Devices Not Checked in Within 30 Days Count` | ✅ — partner audit confirms |
| Not protected (Webroot-specific) | "Deactivated Endpoints Count" — not in current dataprint | ✅ — direct, rare among EDRs |
| Servers managed | **Not directly available.** Webroot doesn't split server vs. workstation. Asset cross-check via `AccountType` | 🔍 asset cross-check |
| Infected endpoints | metricName=`Webroot: Infected Device Count` "Infected Device Count" | ✅ |

> **Limitation flagged by partner audit.** Webroot does not distinguish servers
> from workstations — fall back to filtering the asset inventory by
> `AccountType` for the split.

---

## Metrics and queries

### Headline

| Metric | JMESPath / metric detail | Result shape |
|---|---|---|
| Active endpoints | `Endpoints[?Deactivated == \`false\`] | length(@)` | `<integer>` |
| Stale endpoints (30+ days) | metricName=`Webroot: Devices Not Checked in Within 30 Days Count` | `<integer>` |
| Infected endpoints | | `<integer>` |
| Deactivated endpoints | not in current dataprint | `<integer>` |
| Site name | `SiteInfo.SiteName` — VALIDATED | `<string>` |

### Endpoint detail

```jmespath
Endpoints[*].{
  hostname: HostName,
  lastSeen: LastSeen,
  deactivated: Deactivated,
  infected: Infected,
  os: OperatingSystem
}
```

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Stale endpoints | not-checked-in-30d > 0 | "<N> endpoints offline >30d — investigate or decommission." |
| Infected endpoints | infected > 0 | "<N> endpoints infected — clean and verify." |
| Deactivated count | deactivated > 0 | "<N> endpoints deactivated — confirm intentional or re-enroll." |
| Coverage gap | asset cross-check | "<N> compute devices not on Webroot — extend deployment." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Server vs. workstation split | not exposed | Asset-inventory `AccountType` filter |
| Threat lifecycle / detection detail | partial | Webroot console |
| Per-policy enforcement | partial | Webroot console |

---

## Output format

Markdown / Word / PowerPoint per `output.format`.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_system LIST | query="webroot" envId=<ENV_ID> | array<system> | ok |
| 3 | liongard_metric EVALUATE | metricName or jmesPathQuery sysId=<SYS_ID> envId=<ENV_ID> | <integer>, <array> | ok |
| 4 | liongard_device LIST | envId=<ENV_ID> | array<device> | ok |
```

---
name: single-system-bitdefender-gravityzone
description: >
  Use this skill when the user wants a single-system analysis of a Bitdefender
  GravityZone tenant — Periodic Business Review (PBR), endpoint deployment review,
  threat posture, license utilization. Trigger phrases: "Bitdefender PBR",
  "GravityZone report", "BD report", "BDGZ analysis", "pull Bitdefender data for
  <CUSTOMER>". Produces an artifact in the format set in the customization block.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, soc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, pptx]
primitives:
  - metrics:bitdefender-gravityzone:endpoint-detail
  - metrics:bitdefender-gravityzone:online-endpoints
  - metrics:bitdefender-gravityzone:total-endpoints
---

# Single-System Analysis — Bitdefender GravityZone

> **Inspector:** `bitdefender-gravityzone-inspector` (ID 57). Apps & Services
> category. EDR / AV.
>
> **References:** `reference/inspector-aliases.md` (BD, BDGZ, GravityZone, GZ).
> `reference/asset-fields.md` for asset cross-checks.
> `reference/onboarding-qa-coverage.md` for the per-EDR coverage matrix.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-bitdefender-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  endpoints: "Endpoint Coverage"
  threats: "Threat Posture"
  licensing: "License Utilization"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  online_pct_min: 95
  infected_max: 0
  license_expiration_warn_days: 30

reporting_period: { default: "last_quarter" }
```

---

## When to use

- "Pull the Bitdefender / BDGZ / GravityZone data for <customer>"
- "How many endpoints are infected on the BD console?"
- Monthly health check, quarterly PBR.

Personas: NOC (agent health), SOC (threats), vCIO/AM (executive summary), TAM.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Bitdefender system ID | Yes | `liongard_system LIST query="bitdefender"` |
| Reporting period | No | Default per customization |

---

## Locating the right system

```
liongard_system LIST searchMode=keyword query="bitdefender" environmentId=<ENV_ID>
```

Bitdefender GravityZone is typically a single per-tenant system. Identify by the
company-name field on the dataprint.

---

## Liongard data sources

> **Asset Inventory First, Metric Cross-Check.** Bitdefender is the source of
> truth for *console-side* state (endpoint enrollment, infection, online).
> The asset inventory is the source of truth for *coverage* — which compute
> devices have BD in their `Inspectors[]` array.

### Per-vendor data — system fields

| Key | Description |
|---|---|
| `Endpoints` | Array of all enrolled endpoints with `details.stateName`, agent metadata |
| `Companies` / `Account` | Tenant / company metadata |
| `Policies` | Policy configurations |
| `Tasks` | Scan / push-task history |

### Cross-inspector cross-check — asset inventory

```
liongard_device LIST environmentId=<ENV_ID> pageSize=200
```

```
# Devices BD reports on
items[?inspectors[?name=='bitdefender-gravityzone-inspector']]

# Coverage gap
# (requires liongard_device LIST result — client-side filter)
items[?!inspectors[?name=='bitdefender-gravityzone-inspector'] && category == 'compute']

# Devices with BD in their AV/EDR sets
items[?contains(antivirus, 'Bitdefender') || contains(edr, 'Bitdefender')]
```

---

## Onboarding QA — endpoint posture

Coverage per `reference/onboarding-qa-coverage.md`:

| Question | JMESPath / approach | Coverage |
|---|---|---|
| Total endpoints managed | `length(Endpoints)` | ✅ |
| Active in last 30 days | `length(Endpoints[?details.stateName == 'online'])` | ✅ via online state |
| Inactive 2+ months | `length(Endpoints[?details.stateName != 'online'])` (offline count — not in current dataprint or compute client-side) | ✅ |
| Not protected (coverage gap) | `liongard_device LIST` + client filter: `items[?!inspectors[?name=='bitdefender-gravityzone-inspector'] && category == 'compute']` | 🔍 asset cross-check |
| Servers managed | `length(Endpoints[?details.machineType == \`2\`])` (integer: 1=workstation, 2=server) or VM count from the asset inventory | ⚠️ partial — VM count yes, server-vs-workstation requires client-side filter |
| High alerts / threats | `length(Endpoints[?details.malware != null])` | ✅ |

> **Field gotcha — `machineType` is an integer, not a string:** `details.machineType == 'server'` never matches. The field returns an integer: `1` = workstation, `2` = server. Always use backtick-quoted integers in JMESPath: `details.machineType == \`2\``. Validated on live system (2026-05-28).
>
> **Limitation flagged by partner audit.** Bitdefender doesn't combine
> server-type with activity in one query — for "servers active in last 30 days",
> filter `Endpoints[]` client-side.

---

## Metrics and queries

### Headline

| Metric | JMESPath | Result shape |
|---|---|---|
| Total endpoints | `length(Endpoints)` | `<integer>` |
| Online endpoints | `length(Endpoints[?details.stateName == 'online'])` | `<integer>` |
| Managed endpoints | | `<integer>` |
| Virtual machines | | `<integer>` |
| Infected systems | | `<integer>` |

### Endpoint detail

```jmespath
Endpoints[*].{
  name: name,
  state: details.stateName,
  os: details.operatingSystem,
  machineType: details.machineType,
  policy: assignedPolicyName,
  lastSeen: details.lastSeen,
  malware: details.malware
}
```

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Offline endpoints | online% < `slas.online_pct_min` | "<N> endpoints offline >24h — investigate connectivity / agent health." |
| Infected | infected > `slas.infected_max` | "<N> endpoints flagged as infected — investigate and clean." |
| Coverage gap | asset.compute − `length(Endpoints)` > 0 | "<N> compute devices in inventory not in Bitdefender — extend deployment." |
| License expiry | days_until_expiry < SLA | "Renew Bitdefender subscription within <N> days." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Server vs. workstation activity split | partial — `machineType` is integer: 1=workstation, 2=server | Filter `Endpoints[?details.machineType == \`2\`]` client-side |
| Per-policy threat distribution | partial | Bitdefender console for full breakdown |
| Threat lifecycle (resolved/open/pending) | partial | Bitdefender console |

---

## Output format

Markdown / Word / PowerPoint per `output.format`. See `templates/output-block-*.md`.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_system LIST | query="bitdefender" envId=<ENV_ID> | array<system> | ok |
| 3 | liongard_metric EVALUATE | metricName or jmesPathQuery sysId=<SYS_ID> envId=<ENV_ID> | <integer>, <array> | ok |
| 4 | liongard_device LIST | envId=<ENV_ID> | array<device> | ok |
```

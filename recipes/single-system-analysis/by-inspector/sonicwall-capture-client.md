---
name: single-system-sonicwall-capture-client
description: >
  Use this skill when the user wants a single-system analysis of SonicWall
  Capture Client — endpoint deployment review, infection counts, license
  utilization. Trigger phrases: "Capture Client report", "SCC PBR", "SonicWall
  EDR review", "pull Capture Client data for <CUSTOMER>". Produces an artifact
  in the format set in the customization block.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, soc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, pptx]
primitives:
  - metrics:sonicwall-capture-client-inspector:active-endpoints-list
  - metrics:sonicwall-capture-client-inspector:count-active-endpoints
  - metrics:sonicwall-capture-client-inspector:count-infected-endpoints
  - metrics:sonicwall-capture-client-inspector:count-offline-endpoints
  - metrics:sonicwall-capture-client-inspector:count-total-endpoints
  - metrics:sonicwall-capture-client-inspector:infected-endpoints-list
  - metrics:sonicwall-capture-client-inspector:offline-endpoints-list
  - metrics:sonicwall-capture-client-inspector:total-endpoints-list
  - metrics:sonicwall-capture-client-inspector:users
---

# Single-System Analysis — SonicWall Capture Client

> **Inspector:** `sonicwall-capture-client-inspector` (ID 95). Apps & Services
> category. EDR (SentinelOne-based, distributed by SonicWall as their EDR
> offering).
>
> **References:** `reference/inspector-aliases.md` (SCC, Capture Client,
> SonicWall EDR). `reference/onboarding-qa-coverage.md` for the per-EDR coverage
> matrix.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-sonicwall-capture-client-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  endpoints: "Endpoint Coverage"
  threats: "Threats & Infections"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  active_pct_min: 95
  infected_max: 0

reporting_period: { default: "last_quarter" }
```

---

## When to use

- "Pull SCC / Capture Client / SonicWall EDR data for <customer>"
- "Any infected endpoints on Capture Client?"
- Quarterly endpoint posture review.

Personas: NOC, SOC, vCIO/AM, TAM.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Capture Client system ID | Yes | `liongard_system LIST query="sonicwall-capture"` |

---

## Locating the right system

```
liongard_system LIST searchMode=keyword query="sonicwall-capture-client" environmentId=<ENV_ID>
```

If multiple SonicWall systems are present, distinguish Capture Client (EDR) from
SonicWall firewall (`sonicwall-inspector` ID 7) — different inspectors.

---

## Liongard data sources

### Per-vendor data — system fields

Capture Client surfaces SentinelOne-based agent data:

| Key | Description |
|---|---|
| `Endpoints` | Array of all enrolled endpoints with state, version, threat count |
| `Account` | Tenant / company metadata |
| `Policies` | Policy configurations |

### Cross-inspector cross-check — asset inventory

```
liongard_device LIST environmentId=<ENV_ID> pageSize=200
```

```
# Devices Capture Client reports on
Devices[?Inspectors contains "sonicwall-capture-client-inspector"]

# Coverage gap
Devices where category == "compute" AND Inspectors does not contain "sonicwall-capture-client-inspector"
```

---

## Onboarding QA — endpoint posture

Per partner-validated matrix at `reference/onboarding-qa-coverage.md`:

| Question | JMESPath / approach | Coverage |
|---|---|---|
| Total endpoints managed | `length(Endpoints)` | ✅ |
| Active in last 30 days | `length(Endpoints[?status == 'active'])` | ✅ |
| Inactive 2+ months | filter client-side by lastActiveDate | ⚠️ partial |
| Not protected (coverage gap) | Asset cross-check | 🔍 |
| Servers managed | `length(Endpoints[?machineType == 'server'])` | ⚠️ partial — not exposed by partner audit; client-side filter |
| Infected endpoints | `length(Endpoints[?infected])` | ✅ |

---

## Metrics and queries

### Headline

| Metric | JMESPath | Result shape |
|---|---|---|
| Total endpoints | `length(Endpoints)` | `<integer>` |
| Active endpoints | | `<integer>` |
| Infected endpoints | | `<integer>` |

### Endpoint detail

```jmespath
Endpoints[*].{
  name: name,
  status: status,
  os: os,
  agentVersion: agentVersion,
  lastActive: lastActiveDate,
  infected: infected,
  threatCount: threatCount
}
```

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Inactive endpoints | active% < SLA | "<N> endpoints inactive — investigate." |
| Infected endpoints | infected > 0 | "<N> endpoints infected — triage and clean." |
| Coverage gap | asset cross-check shows compute devices without SCC | "<N> devices not enrolled — extend deployment." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Server vs. workstation split | partial | Client-side filter on `machineType` |
| Inactive 2+ months specifically | partial | Client-side filter on lastActiveDate |
| Per-policy coverage | partial | SonicWall console |

---

## Output format

Markdown / Word / PowerPoint per `output.format`.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_system LIST | query="sonicwall-capture-client" envId=<ENV_ID> | array<system> | ok |
| 3 | liongard_metric EVALUATE | metricName or jmesPathQuery sysId=<SYS_ID> envId=<ENV_ID> | <integer>, <array> | ok |
| 4 | liongard_device LIST | envId=<ENV_ID> | array<device> | ok |
```

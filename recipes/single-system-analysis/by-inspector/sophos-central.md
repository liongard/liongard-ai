---
name: single-system-sophos-central
description: >
  Use this skill when the user wants a single-system analysis of a Sophos
  Central tenant — Periodic Business Review (PBR), endpoint deployment review,
  threat health audit, server vs. workstation breakdown. Trigger phrases:
  "Sophos PBR", "Sophos Central report", "Intercept X review", "pull Sophos
  data for <CUSTOMER>". Produces an artifact in the format set in the
  customization block.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, soc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, pptx]
primitives:
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
---

# Single-System Analysis — Sophos Central

> **Inspector:** `sophos-central-inspector` (ID 65). Apps & Services category.
> EDR / endpoint protection.
>
> **Naming gotcha.** "Sophos" can mean three different inspectors — Central
> (this one, EDR), Sophos Firewall XG/XGS, or Sophos SG (legacy). Confirm with
> the user before assuming. See `reference/inspector-aliases.md`.
>
> **References:** `reference/onboarding-qa-coverage.md` — Sophos Central has
> the strongest server-vs-workstation split among the EDRs.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-sophos-central-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  endpoints: "Endpoint Coverage"
  servers: "Server Coverage"
  threats: "Threat Health"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  endpoint_protection_pct_min: 95
  threat_health_pct_min: 95
  server_protection_pct_min: 100   # often stricter than workstations

reporting_period: { default: "last_quarter" }
```

---

## When to use

- "Pull Sophos Central / Intercept X data for <customer>"
- "How many endpoints are unprotected on Sophos?"
- "Any threat-health alerts on the Sophos console?"

Personas: NOC, SOC, vCIO/AM, TAM.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Sophos Central system ID | Yes | `liongard_system LIST query="sophos-central"` |

---

## Locating the right system

```
liongard_system LIST searchMode=keyword query="sophos-central" environmentId=<ENV_ID>
```

> Be explicit with `sophos-central` (not bare `sophos`) to disambiguate from
> Sophos Firewall.

---

## Liongard data sources

### Per-vendor data — system fields

| Key | Description |
|---|---|
| `Endpoints` | Array of enrolled endpoints with `assignedProducts`, threat health, OS type, lastSeenAt |
| `Servers` | Array of server-class endpoints (separate enumeration) |
| `Account` | Tenant metadata |
| `Policies` | Policy configurations |

### Cross-inspector cross-check — asset inventory

```
liongard_device LIST environmentId=<ENV_ID> pageSize=200
```

```
# Devices Sophos sees
Devices[?Inspectors contains "sophos-central-inspector"]

# Coverage gap
Devices where category == "compute" AND Inspectors does not contain "sophos-central-inspector"

# Devices reporting Sophos AV/EDR
Devices where antivirus contains "Sophos" OR edr contains "Sophos" OR edr contains "Intercept"
```

---

## Onboarding QA — endpoint posture

Sophos Central has the **most complete coverage** of the EDR onboarding-QA
fields per `reference/onboarding-qa-coverage.md`:

| Question | JMESPath / approach | Coverage |
|---|---|---|
| Total endpoints managed | `length(Endpoints)` (not in current dataprint) | ✅ |
| Active in last 30 days | `length(Endpoints[?lastSeenAt > '<today − 30d>'])` (proposed) | ✅ |
| Inactive 2+ months | "Endpoints Not Seen In Last 30 Days Count" (existing metric) | ✅ |
| Not protected (Sophos-specific) | "Endpoints with Endpoint Protection Not Installed" (existing metric) | ✅ direct — rare among EDRs |
| Servers managed | `length(Servers)` or filter — partner mapping has ✅ | ✅ |
| Servers — active 30d | `length(Servers[?lastSeenAt > '<today − 30d>'])` (proposed) | ✅ |
| Servers — inactive 2+ months | proposed | ✅ |
| Servers — not protected | proposed | ✅ |
| Threat health | "Endpoints with Threat Health Not In Good State" (existing) | ✅ |

> Sophos Central is the **canonical example** of full onboarding-QA coverage —
> when comparing to other EDRs in a fleet rollup, it provides the cleanest data.

---

## Metrics and queries

### Headline

| Metric | JMESPath / metric detail | Result shape |
|---|---|---|
| Total managed endpoints | `length(Endpoints)` (proposed) | `<integer>` |
| Endpoints with protection installed | metricName=`Sophos Central: Endpoints with Endpoint Protection Installed Count` | `<integer>` |
| Endpoints not seen 30d | existing metric | `<integer>` |
| Endpoints not protected | existing metric | `<integer>` |
| Servers managed | `length(Servers)` (proposed) | `<integer>` |
| Servers without protection | not in current dataprint | `<integer>` |
| Threat health not good | existing metric | `<integer>` |

### Endpoint detail

```jmespath
Endpoints[*].{
  hostname: hostname,
  os: os.name,
  type: type,
  protectionInstalled: contains(assignedProducts[].code, 'endpointProtection'),
  threatHealth: health.threats.status,
  servicesHealth: health.services.status,
  lastSeen: lastSeenAt
}
```

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Endpoints without protection | unprotected count > 0 | "<N> endpoints without Sophos protection — install agent." |
| Servers without protection | server unprotected > 0 | "<N> servers without protection — critical, install today." |
| Threat health degraded | threat-health-not-good > 0 | "<N> endpoints in bad threat health — investigate." |
| Stale endpoints | not-seen-30d > 0 | "<N> endpoints offline >30d — confirm decommissioned or reconnect." |
| Coverage gap (asset cross-check) | compute devices not in Sophos | "<N> compute devices not enrolled — extend deployment." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Several "active 30d / inactive 60d" counts | data gaps | Client-side filter against `Endpoints[]` |
| Per-policy threat distribution | partial | Sophos Central console for full breakdown |
| MTR (Managed Threat Response) detection lifecycle | not in dataprint | Sophos console |

---

## Output format

Markdown / Word / PowerPoint per `output.format`.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_system LIST | query="sophos-central" envId=<ENV_ID> | array<system> | ok |
| 3 | liongard_metric EVALUATE | metricName or jmesPathQuery sysId=<SYS_ID> envId=<ENV_ID> | <integer>, <array> | ok |
| 4 | liongard_device LIST | envId=<ENV_ID> | array<device> | ok |
```

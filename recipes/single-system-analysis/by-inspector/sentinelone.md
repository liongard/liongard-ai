---
name: single-system-sentinelone
description: >
  Use this skill when the user wants a single-system analysis of a SentinelOne
  tenant — Periodic Business Review (PBR / QBR), monthly health check, threat
  posture review, or license utilization audit. Trigger phrases: "S1 PBR",
  "SentinelOne report", "pull the S1 data for <CUSTOMER>", "single system review of
  SentinelOne", "review the S1 tenant for <CUSTOMER>". Produces an artifact in the
  format set in the customization block (Word, PowerPoint, Markdown, or Excel).
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, soc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, pptx]
primitives:
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
---

# Single-System Analysis — SentinelOne

> **Inspector:** `sentinelone-inspector` (ID 70). Cloud category. EDR.
> **Parent/child:** Yes. Parent = sparse discovery stub; **child = the per-tenant
> system that holds Agents, Threats, Policies, and exclusions.** Always target the
> child for reporting.
>
> **References:** `reference/inspector-aliases.md` for SentinelOne aliases (S1,
> Singularity). `reference/asset-fields.md` for cross-checks against the asset
> inventory.

---

## Customize for your MSP

```yaml
output:
  format: markdown            # markdown | word | pptx | xlsx
  filename: "<customer>-sentinelone-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  threats: "Threat Posture"
  agents: "Agent Health"
  licenses: "License Utilization"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"            # technical | balanced | executive

slas:
  agent_uptodate_pct_min: 95
  unresolved_threats_max: 0
  license_expiration_warn_days: 30
  agent_offline_days_max: 7

reporting_period:
  default: "last_quarter"
  fiscal_year_start_month: 1
```

---

## When to use

Trigger phrases / scenarios:
- "Pull the SentinelOne / S1 data for <customer>" (PBR or QBR)
- "Single-system review of SentinelOne"
- "S1 monthly health check"
- "Are there any unresolved threats in <customer>'s S1?"
- "What's the license headroom on the S1 tenant?"

Cadence: monthly health check, quarterly PBR, on-demand for incidents.
Personas: NOC (agent health), SOC (threats), vCIO/AM (executive summary), TAM (deep-dive).

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` → match by name |
| Child SentinelOne system ID | Yes | `liongard_system LIST query="sentinelone"` → confirm child via `SystemInfo.accountName` |
| Reporting period | No (default per customization) | User or fiscal calendar |

---

## Locating the right system

```
liongard_system LIST searchMode=keyword query="sentinelone" environmentId=<ENV_ID>
```

Multiple systems will return for parent + child. Distinguish by dataprint shape:

| Shape | What it is | Action |
|---|---|---|
| Sparse keys: `Name`, `Tenants`, `Discovered` | **Parent** discovery stub | Skip for reporting |
| Has `Agents[]`, `Threats[]`, `ThreatsSummary`, `AgentsSummary`, `SystemInfo` | **Child** tenant | Use this |

`SystemInfo.accountName` returns the tenant/site display name (a `<string>`).

---

## Liongard data sources

> **Asset Inventory First, Metric Cross-Check.** SentinelOne is the per-vendor
> source of truth for *agent health, policy state, and threat detail*. The
> cross-inspector asset inventory is the source of truth for *coverage* — which
> compute devices Liongard knows exist and which of them have SentinelOne in their
> `inspectors[]` array. Use both.

### Per-vendor data — the SentinelOne child dataprint

Top-level keys on a SentinelOne child system:

| Key | Description |
|---|---|
| `SystemInfo` | Tenant metadata: `accountName`, `accountId`, license counts, health, expiration |
| `Agents` | Array of all endpoint agents with full detail (hostname, OS, status, version) |
| `AgentsSummary` | Rollup counts: `total`, `online`, `infected`, `upToDate`, `outOfDate`, `decommissioned` |
| `Threats` | Array of threat objects with indicators, mitigation status, agent context |
| `ThreatsSummary` | Rollup: `total`, `resolved`, `inProgress`, `notResolved`, `maliciousNotResolved`, `suspiciousNotResolved` |
| `Users` | Console user accounts |
| `Groups` | Agent groups |
| `Policies` | Policy configurations |
| `Exclusions` / `ExclusionsPath` / `ExclusionsHash` / `ExclusionsFile` | Exclusion rules — granular audit |
| `Firewall` | Firewall rules |
| `ApplicationCVEs` | Known CVEs on managed endpoints (can be very large — use `length()` not full pull) |
| `Sysinfo` | SentinelOne **console/platform** version: `build`, `release`, `version`, `latestAgentVersion` |
| `Devices` | Discovered network devices (Ranger) |
| `GroupPolicyInformation` | Policy inheritance + group policy details |

> **Naming gotcha.** `Sysinfo` (lowercase 'i') is distinct from `SystemInfo` (capital
> 'I'). `Sysinfo` holds the S1 console release version (e.g., `<console-version>`).
> `SystemInfo` holds the tenant/site metadata.

### Cross-inspector cross-check — asset inventory

```
liongard_device LIST environmentId=<ENV_ID> pageSize=200
```

For SentinelOne specifically:

```
# Devices SentinelOne reports on
items[?inspectors[?name=='sentinelone-inspector']]

# Devices Liongard knows but SentinelOne doesn't see (coverage gap)
# (requires liongard_device LIST result — client-side filter)
items[?!inspectors[?name=='sentinelone-inspector'] && category == 'compute']

# Devices reporting EDR via S1
items[?contains(edr, 'SentinelOne') || contains(edr, 'Sentinel')]
```

The asset-inventory device count for `category == "compute"` is the authoritative
denominator. SentinelOne's `AgentsSummary.total` is the numerator. Coverage gap =
denominator − numerator.

---

## Metrics and queries

### Threat posture (headline KPIs)

| Metric | JMESPath | Result shape |
|---|---|---|
| Total detections | `ThreatsSummary.total` | `<integer>` |
| Resolved threats | `ThreatsSummary.resolved` | `<integer>` |
| Unresolved threats | `ThreatsSummary.notResolved` | `<integer>` |
| In-progress threats | `ThreatsSummary.inProgress` | `<integer>` |
| Malicious unresolved | `ThreatsSummary.maliciousNotResolved` | `<integer>` |
| Suspicious unresolved | `ThreatsSummary.suspiciousNotResolved` | `<integer>` |

### Agent health (headline KPIs)

| Metric | JMESPath | Result shape |
|---|---|---|
| Total agents | `AgentsSummary.total` | `<integer>` |
| Online | `AgentsSummary.online` | `<integer>` |
| Infected | `AgentsSummary.infected` | `<integer>` |
| Up-to-date | `AgentsSummary.upToDate` | `<integer>` |
| Out-of-date | `AgentsSummary.outOfDate` | `<integer>` |
| Decommissioned | `AgentsSummary.decommissioned` | `<integer>` |

### License utilization

| Metric | JMESPath | Result shape |
|---|---|---|
| Total licenses | `SystemInfo.totalLicenses` | `<integer>` |
| Active licenses | `SystemInfo.activeLicenses` | `<integer>` |
| Days until expiration | `SystemInfo.daysUntilExpiration` | `<integer>` |
| Health status | `SystemInfo.healthStatus` | `<bool>` |
| SKU | `SystemInfo.sku` | `<string>` |
| Tenant name | `SystemInfo.accountName` | `<string>` |

### Console version

| Metric | JMESPath | Result shape |
|---|---|---|
| Console release | `Sysinfo.release` | `<string>` |
| Latest agent version (advertised) | `Sysinfo.latestAgentVersion` | `<string>` |
| Console build | `Sysinfo.build` | `<string>` |

### Threat detail table

```jmespath
Threats[*].{
  threatName: threatInfo.threatName,
  classification: threatInfo.classification,
  confidenceLevel: threatInfo.confidenceLevel,
  analystVerdict: threatInfo.analystVerdictDescription,
  incidentStatus: threatInfo.incidentStatusDescription,
  mitigationStatus: threatInfo.mitigationStatusDescription,
  endpoint: agentRealtimeInfo.agentComputerName,
  identifiedAt: threatInfo.identifiedAt,
  filePath: threatInfo.filePath
}
```

### Infected vs healthy split (donut chart)

```jmespath
{
  healthy: length(Agents[?infected == `false`]),
  infected: length(Agents[?infected == `true`])
}
```

### Verdict breakdown

```jmespath
{
  truePositive: length(Threats[?threatInfo.analystVerdict == 'true_positive']),
  falsePositive: length(Threats[?threatInfo.analystVerdict == 'false_positive']),
  suspicious: length(Threats[?threatInfo.analystVerdict == 'suspicious']),
  undefined: length(Threats[?threatInfo.analystVerdict == 'undefined'])
}
```

### Onboarding QA — endpoint posture (six standard questions)

Partner-validated coverage matrix at `reference/onboarding-qa-coverage.md`.
SentinelOne answers all six directly except "Not protected", which requires the
asset-inventory cross-check.

| Question | JMESPath / approach | Coverage |
|---|---|---|
| Total endpoints managed | `AgentsSummary.total` | ✅ |
| Active in last 30 days | `length(Agents[?lastActiveDate > '<today − 30d>'])` | ✅ |
| Inactive 2+ months | `length(Agents[?lastActiveDate < '<today − 60d>'])` | ✅ |
| Not protected (coverage gap) | `liongard_device LIST` + client filter: `items[?!inspectors[?name=='sentinelone-inspector'] && category == 'compute']` | 🔍 asset cross-check |
| Servers managed | `length(Agents[?machineType == 'server'])` | ✅ |
| High alerts / threats | `ThreatsSummary.notResolved` + `Threats[]` lifecycle | ✅ |

> **Limitation flagged by partner audit.** SentinelOne does not combine
> `machineType=server` with `lastActiveDate` in a single query — to count
> "servers active in the last 30 days" or "servers inactive 2+ months",
> filter `Agents[]` client-side: `Agents[?machineType == 'server' && lastActiveDate > <threshold>]`.

### Time-series trend (PBR "protected over time" chart)

```
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID>
  environmentId=<ENV_ID>
  startDate=<ISO timestamp>
  endDate=<ISO timestamp>
  jmesPathQuery="ThreatsSummary"
```

Returns one result per inspection timeline entry — chart trends over the period.

---

## Insights & recommendations — generation patterns

| Insight | Trigger | Recommended action template |
|---|---|---|
| Unresolved threat present | `ThreatsSummary.notResolved > slas.unresolved_threats_max` | "Triage and resolve <N> unresolved threats in S1 console." |
| Infected endpoints | `AgentsSummary.infected > 0` | "Investigate infection on <N> endpoints; isolate and remediate." |
| Out-of-date agents | `AgentsSummary.outOfDate > 0` AND coverage % < SLA | "Push agent update to <N> endpoints; investigate offline agents." |
| Coverage gap (devices without S1) | asset.compute_count − `AgentsSummary.total` > 0 | "<N> compute devices in inventory have no SentinelOne agent — confirm scope or deploy." |
| License headroom low | `activeLicenses / totalLicenses > 0.95` | "Provision <N> additional seats before next assignment." |
| Expiration imminent | `daysUntilExpiration < slas.license_expiration_warn_days` | "Initiate renewal with vendor for <N> seats." |
| Threat resolution rate | `resolved / total < target` | "Review SOC triage capacity; <pct>% of threats remain unresolved at period end." |

---

## Data gaps & coverage notes

Always include this section. Populate from:
- Devices in `liongard_device` where `category == "compute"` and `Inspectors` does
  not contain `sentinelone-inspector` → ungoverned by S1.
- `Agents[]` entries where `lastActiveDate` is older than `slas.agent_offline_days_max`.
- `ApplicationCVEs` length is very large (8000+); a `length()` query is sufficient
  for the report — pulling the full array wastes context.

---

## Output format

The agent picks the format from `output.format`:

- **Markdown** (default) — sections in order: Executive Summary → Threat Posture →
  Agent Health → License Utilization → Recommended Actions → Data Gaps. Use tables.
- **Word** — see `templates/output-block-word.md`. Heading 1 per section, KPI table
  in Executive Summary, threat detail as a wide table.
- **PowerPoint** — see `templates/output-block-pptx.md`. Cover → KPI dashboard →
  Threats donut + verdict bar → Agents donut → Licenses gauge → Recommendations.

---

## Notes for the agent

- **Always target the child system.** The parent is a discovery stub.
- **`Threats[]` is the lifecycle source** — includes `mitigationStatus[]` actions
  (quarantine, kill, etc.) per threat.
- **Per-agent detail is in `Agents[]`** — `computerName`, `osName`, `agentVersion`,
  `networkInterfaces[].inet[]` for IP.
- **`ApplicationCVEs` is enormous** — never pull the full array; use `length()`
  or filter to specific CVE IDs.
- **`ExclusionsPath` / `ExclusionsHash` / `ExclusionsFile`** are granular —
  useful for exclusion-audit recipes (separate use case).
- **Two reporting variants are common**: quarterly (Q4) and rolling 30-day. Same
  queries, different `startDate` / `endDate`.

---

## Verification log (agent appends, MSP reviews)

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_system LIST | query="sentinelone" envId=<ENV_ID> | array<system> | ok |
| 3 | liongard_metric EVALUATE | metricName=<METRIC_NAME> sysId=<SYS_ID> envId=<ENV_ID> | <integer> or <object> | ok |
| 4 | liongard_device LIST | envId=<ENV_ID> | array<device> | ok |
```

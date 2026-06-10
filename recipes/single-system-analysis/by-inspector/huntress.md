---
name: single-system-huntress
description: >
  Use this skill when the user wants a single-system analysis of a Huntress
  customer organization — Periodic Business Review (PBR / QBR), monthly health
  check, agent deployment audit, or incident trend review. Trigger phrases:
  "Huntress PBR", "Huntress report", "pull Huntress data for <CUSTOMER>",
  "single system review of Huntress". Produces an artifact in the format set in
  the customization block (Word, PowerPoint, Markdown, Excel).
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_asset"
personas: [noc, soc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, pptx]
primitives:
  # Reconciled 2026-05-29: pruned dangling refs not present in the live dataprint (see internal/proposed-metrics-backlog.md).
  - metrics:huntress:active-incidents-count
  - metrics:huntress:agents-total-count
  - metrics:huntress:unresponsive-agents-count-21d
  - metrics:huntress:unresponsive-agents-count-30d
  - metrics:huntress:unresponsive-agents-count-60d
  - metrics:huntress:unresponsive-agents-list-21d
  - metrics:huntress:unresponsive-agents-list-30d
  - metrics:huntress:unresponsive-agents-list-60d
---

# Single-System Analysis — Huntress

> **Inspector:** `huntress-inspector` (ID 97). Apps & Services category. EDR / MDR
> with SOC.
> **Parent/child:** Yes. **Parent** holds an `Organizations[]` rollup with
> `agents_count` and `incident_reports_count` per customer org. **Child** is the
> per-customer system that holds `Agents[]`. Use the **child** for per-customer
> reports; use the **parent** for MSP-level rollup across all customers.
>
> **References:** `reference/inspector-aliases.md` (Huntress, Huntress Labs).
> `reference/asset-fields.md` for cross-checks.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-huntress-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  agents: "Agent Deployment & Health"
  incidents: "Incident Activity"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"

slas:
  agent_offline_days_max: 7        # flag agents that haven't checked in for N days
  agent_stale_days_max: 30         # critical staleness threshold
  edr_coverage_pct_min: 95         # vs. asset-inventory compute device count

reporting_period:
  default: "last_quarter"
```

---

## When to use

- "Pull the Huntress data for <customer>" (PBR)
- "Huntress monthly health check"
- "How many Huntress agents are offline?"
- "What's our Huntress agent coverage vs. our managed device count?"

Cadence: monthly health check, quarterly PBR.
Personas: NOC (agent health), SOC (incidents), vCIO/AM, TAM.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Child Huntress system ID | Yes for per-customer report | `liongard_system LIST query="huntress"` → confirm child via `Organization.name` |
| Reporting period | No (default per customization) | User or fiscal calendar |

---

## Locating the right system

```
liongard_system LIST searchMode=keyword query="huntress" environmentId=<ENV_ID>
```

| Shape | What it is | Use for |
|---|---|---|
| Has `Organizations[]` (plural) with `agents_count`, `incident_reports_count` | **Parent** — MSP-level rollup | Cross-customer summary |
| Has `Organization` (singular) and `Agents[]` | **Child** — single customer | Per-customer PBR (this recipe's primary target) |

`Organization.name` returns the customer org name (a `<string>`).

---

## Liongard data sources

> **Asset Inventory First, Metric Cross-Check.** Huntress is the source of truth
> for *agent deployment, EDR detection, and incident lifecycle*. The cross-inspector
> asset inventory gives you the *denominator* — total compute devices Liongard
> knows exist — to compute coverage gaps.

### Per-vendor data — child system fields

| Key | Description |
|---|---|
| `Organization` | Single org: `name`, `agents_count`, `incident_reports_count`, `microsoft_365_users_count` |
| `Agents` | Array of all Huntress agents for this customer |

#### Agent fields

| Field | Description |
|---|---|
| `hostname` | Agent hostname |
| `ipv4_address` | Internal IP |
| `external_ip` | External / public IP |
| `mac_addresses` | MAC address array |
| `platform` | OS platform (`windows`, `linux`, `mac`) |
| `os` | Full OS name |
| `version` | Huntress agent version |
| `edr_version` | EDR component version |
| `serial_number` | Hardware serial |
| `last_survey_at` | Last survey/scan timestamp |
| `last_callback_at` | Last agent check-in timestamp |
| `DaysSinceLastCheckin` | Computed days since last check-in |
| `tags` | Agent tag array |
| `created_at` | Agent install date |

### Cross-inspector cross-check — asset inventory

```
liongard_asset LIST environmentId=<ENV_ID> assetType=Device detail=full pageSize=200
```

```
# Devices Huntress reports on
items[?contains(Inspectors, 'huntress-inspector')]

# Coverage gap — compute devices without Huntress
# (requires liongard_asset LIST result — client-side filter)
items[?!contains(Inspectors, 'huntress-inspector') && category == 'compute']

# Devices with Huntress reporting EDR
items[?contains(EDR, 'Huntress')]
```

Coverage % = `length(Agents) / count(asset compute devices)`.

---

## Metrics and queries

### Headline KPIs

| Metric | JMESPath | Result shape |
|---|---|---|
| Total agents (rollup field) | `Organization.agents_count` | `<integer>` |
| Total agents (from array) | `length(Agents)` | `<integer>` |
| Cumulative incident reports | `Organization.incident_reports_count` | `<integer>` |

### Agent health

| Metric | JMESPath | Result shape |
|---|---|---|
| Unresponsive (>SLA days) | `length(Agents[?DaysSinceLastCheckin > <slas.agent_offline_days_max>])` | `<integer>` |
| Stale (>critical days) | `length(Agents[?DaysSinceLastCheckin > <slas.agent_stale_days_max>])` | `<integer>` |
| Agents by platform | `length(Agents[?platform == 'windows'])` etc. | `<integer>` |

### Agent inventory table

```jmespath
Agents[*].{
  hostname: hostname,
  platform: platform,
  os: os,
  ip: ipv4_address,
  externalIp: external_ip,
  agentVersion: version,
  edrVersion: edr_version,
  lastCheckin: last_callback_at,
  daysSinceCheckin: DaysSinceLastCheckin,
  serial: serial_number,
  tags: tags
}
```

### Onboarding QA — endpoint posture (six standard questions)

Partner-validated coverage matrix at `reference/onboarding-qa-coverage.md`.
Huntress has limited per-endpoint metadata — several questions are not directly
answerable.

| Question | JMESPath / approach | Coverage |
|---|---|---|
| Total endpoints managed | `length(Agents)` or `Organization.agents_count` | ✅ |
| Active in last 30 days | `length(Agents[?DaysSinceLastCheckin <= \`30\`])` | ✅ |
| Inactive 2+ months | `length(Agents[?DaysSinceLastCheckin > \`60\`])` (metricName=`Huntress: Unresponsive agents count (60 days)`) | ✅ |
| Not protected (coverage gap) | `liongard_asset LIST` + client filter: `items[?!contains(Inspectors, 'huntress-inspector') && category == 'compute']` | 🔍 asset cross-check |
| Servers managed (vs. workstations) | **Not directly available from Huntress dataprint.** `liongard_asset LIST` + client filter: `items[?contains(Inspectors, 'huntress-inspector') && AccountType == 'server']` | 🔍 asset cross-check |
| High alerts / threats | `Organization.incident_reports_count` (cumulative — NOT split into active/resolved) | ⚠️ partial — supplement from Huntress portal for active/resolved breakdown |

> **Two limitations flagged by partner audit.** Huntress does not expose:
> 1. Server vs. workstation breakdown — fall back to asset-inventory filtering.
> 2. Active vs. resolved incident split — only the cumulative count.
> Both must be supplemented from the Huntress portal when needed.

### Time-series trends

```
# Deployment growth
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="length(Agents)"

# Cumulative incident trend
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="Organization.incident_reports_count"
```

---

## Insights & recommendations

| Insight | Trigger | Recommended action template |
|---|---|---|
| Stale agents | `length(Agents[?DaysSinceLastCheckin > <stale_days>]) > 0` | "Investigate <N> agents that haven't checked in in <N> days." |
| Coverage gap | asset.compute − `length(Agents)` > 0 | "<N> compute devices in inventory have no Huntress agent — confirm scope or deploy." |
| Increasing incident rate | period-over-period delta on `incident_reports_count` | "Incident volume up <pct>% vs. prior period — review SOC posture." |
| Platform skew | unexpected platform mix | "All agents are Windows but inventory shows <N> Macs without Huntress — extend coverage." |
| EDR version drift | distinct `edr_version` values | "Standardize EDR version across <N> agents to <latest>." |

---

## Data gaps vs. typical PBR slide

The Liongard Huntress dataprint covers deployment and aggregate counts. The Huntress
**portal** has additional detail not in the dataprint:

| Data point | In Liongard? | Alternative |
|---|---|---|
| Active vs. resolved incident split | No | Supplement from Huntress portal |
| EDR signals investigated | No | Supplement from Huntress portal |
| Incidents by severity | No | Supplement from Huntress portal |
| Surveys-per-day chart | Partial | Use `last_survey_at` time-series as proxy |
| Windows Defender Firewall disabled hosts | No | Use `windows-server-inspector` / `windows-workstation-inspector` `Firewall` data |
| Agent total + offline | Yes | This recipe |
| Cumulative incident count | Yes | This recipe (no breakdown) |

Surface these gaps in the **Data Gaps** section of the output so the reader knows
what required portal supplementation.

---

## Output format

Markdown / Word / PowerPoint per `output.format`. See `templates/output-block-*.md`.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_system LIST | query="huntress" envId=<ENV_ID> | array<system> | ok |
| 3 | liongard_metric EVALUATE | metricName or jmesPathQuery sysId=<SYS_ID> envId=<ENV_ID> | <integer> or <array> | ok |
| 4 | liongard_asset LIST | envId=<ENV_ID> assetType=Device detail=full | array<device> | ok |
```

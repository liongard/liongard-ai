---
name: single-system-eset-licensing
description: >
  Use this skill when the user wants a single-system analysis of an ESET
  Licensing tenant — license utilization audit, seat consumption review,
  product mix snapshot. Trigger phrases: "ESET license report", "ESET PBR",
  "pull ESET licensing for <CUSTOMER>". Produces an artifact in the format set
  in the customization block.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_asset"
personas: [vcio-account-manager, technical-alignment-manager, accounting-finance]
output_formats: [markdown, word, xlsx]
primitives:
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
---

# Single-System Analysis — ESET Licensing

> **Inspector:** `eset-licensing-inspector` (ID 69). Cloud category. EDR licensing.
>
> **⚠️ Important scope limitation.** The ESET inspector is **licensing-only** —
> it tracks seat consumption, product names, and license counts. It does NOT
> expose endpoint last-seen dates, threat counts, server vs. workstation splits,
> or per-endpoint protection status. Per partner audit: do not promise endpoint
> posture data on ESET; recommend co-deploying with another EDR for visibility.
>
> **References:** `reference/inspector-aliases.md` (ESET).
> `reference/onboarding-qa-coverage.md` for the per-EDR coverage matrix —
> ESET is the most-limited row.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-eset-licensing-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  licenses: "License Utilization"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  license_utilization_pct_max: 95
  license_expiration_warn_days: 30

reporting_period: { default: "last_quarter" }
```

---

## When to use

- "What's the ESET license consumption for <customer>?"
- "Are we approaching the ESET license cap?"
- Quarterly license-utilization review.

Personas: vCIO/AM (license trend), TAM, Accounting/Finance (cost).

For **endpoint posture** (active devices, threats, coverage) ESET is the wrong
tool — direct the user to the Sophos Central, SentinelOne, Bitdefender,
CrowdStrike, or Webroot recipe instead.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| ESET system ID | Yes | `liongard_system LIST query="eset"` |

---

## Locating the right system

```
liongard_system LIST searchMode=keyword query="eset" environmentId=<ENV_ID>
```

---

## Liongard data sources

### Per-vendor data — system fields

| Key | Description |
|---|---|
| `Licenses` | Array of active license records: product name, seats, used, expiration |
| `Account` | Tenant metadata |

### Cross-inspector cross-check — asset inventory

ESET-specific fields aren't on assets (the inspector doesn't enumerate endpoints),
but the asset inventory tells you the **expected denominator** — total compute
devices in scope:

```
liongard_asset LIST environmentId=<ENV_ID> assetType=Device detail=full pageSize=200
total_compute = Devices where category == "compute" | count
```

If `total_compute > total ESET seats consumed`, you have either uncovered
devices or over-licensed seats — both warrant review.

---

## Onboarding QA — endpoint posture

Per partner-validated matrix at `reference/onboarding-qa-coverage.md` — ESET
is licensing-only, so most onboarding-QA fields are not available:

| Question | Coverage | Notes |
|---|---|---|
| Total endpoints managed | ✅ Active Users count | Treat as "seat consumption", not "device count" |
| Active in last 30 days | ❌ | Not exposed by ESET inspector |
| Inactive 2+ months | ❌ | Not exposed |
| Not protected | 🔍 asset cross-check | Compare ESET seats vs. asset compute count |
| Servers managed | ❌ | Not exposed |
| High alerts / threats | ❌ | Not exposed |

> **Partner recommendation:** ESET is acceptable for license-utilization
> reporting. For endpoint posture, **co-deploy with a posture-capable EDR**
> (Sophos Central, SentinelOne, Bitdefender, CrowdStrike) and use that recipe.

---

## Metrics and queries

| Metric | JMESPath | Result shape |
|---|---|---|
| Active users / seats | `length(Users)` | `<integer>` |
| Licenses summary | `Licenses[*].{product: product, total: total, used: used, expiration: expiration}` | `<array>` |
| License utilization % | `used / total * 100` (compute) | `<percent>` |

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| License approaching cap | `used / total > slas.license_utilization_pct_max / 100` | "Provision additional ESET seats." |
| License expiring | days_until_expiry < SLA | "Renew ESET subscription within <N> days." |
| Coverage gap | asset.compute > ESET seats consumed | "<N> compute devices may not have ESET protection — confirm or extend coverage." |
| ESET-only environment | no other EDR inspector deployed | "**Recommend layering posture EDR** (e.g., Sophos Central) — ESET visibility is licensing-only." |

---

## Data gaps & coverage notes

The ESET inspector intentionally does NOT expose:
- Per-endpoint last-seen / activity
- Endpoint type (server / workstation / laptop)
- Per-endpoint protection status
- Threat counts / detections
- Agent version / health

**These all require the ESET console / API or a co-deployed posture-capable EDR.**

---

## Output format

Markdown / Word / Excel per `output.format`. **xlsx** is the natural fit for a
license-utilization report — sortable and formula-driven.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_system LIST | query="eset" envId=<ENV_ID> | array<system> | ok |
| 3 | liongard_metric EVALUATE | metricName="ESET Licensing: Count of Active Users" sysId=<SYS_ID> envId=<ENV_ID> | <integer> | ok |
| 4 | liongard_metric EVALUATE | metricName="ESET Licensing: License Usage Summary" sysId=<SYS_ID> envId=<ENV_ID> | <array> | ok |
| 5 | liongard_asset LIST | envId=<ENV_ID> assetType=Device detail=full | array<device> | ok |
```

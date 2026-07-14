---
name: single-system-crowdstrike
description: >
  Use this skill when the user wants a single-system analysis of a CrowdStrike
  Falcon tenant — Periodic Business Review (PBR), endpoint deployment review,
  detection / threat trend, sensor health. Trigger phrases: "CrowdStrike PBR",
  "Falcon report", "CS report", "CSF report", "pull CrowdStrike data for
  <CUSTOMER>". Produces an artifact in the format set in the customization block.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, soc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, pptx]
primitives:
  # Reconciled 2026-05-29 vs live dataprint (live production environment, inspected 2026-05-18).
  # This dataprint exposes device/org roster + DevicesDetails[] (incl. device_policies with
  # prevention/firewall/sensor_update keys), but NO detections, alerts, or ZTA scores. Those,
  # plus the device_policies-derived posture metrics (disabled-prevention/firewall, missing-policy),
  # were pruned to internal/proposed-metrics-backlog.md (the policy ones are derivable from
  # DevicesDetails[].device_policies — validate the exact logic before re-adding).
  - metrics:crowdstrike:stale-hosts-count-30d
  - metrics:crowdstrike:stale-hosts-count-7d
  - metrics:crowdstrike:stale-hosts-list-30d
  - metrics:crowdstrike:reduced-functionality-mode-count
  - metrics:crowdstrike:no-rtr-count
  - metrics:crowdstrike:high-risk-users-list
  - metrics:crowdstrike:users-without-mfa-count
  - metrics:crowdstrike:inactive-users-count-30d
---

# Single-System Analysis — CrowdStrike Falcon

> **Inspector:** `crowdstrike-inspector` (ID 102). **Beta** category. EDR.
>
> **References:** `reference/inspector-aliases.md` (CS, CSF, Falcon).
> `reference/onboarding-qa-coverage.md` for the per-EDR coverage matrix.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-crowdstrike-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  sensor_health: "Sensor Health"
  detections: "Active Detections"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  active_sensor_pct_min: 95
  unresolved_detections_max: 0

reporting_period: { default: "last_quarter" }
```

---

## When to use

- "Pull CrowdStrike / Falcon / CS data for <customer>"
- "What's the sensor health?"
- "Any active detections?"

Personas: NOC, SOC, vCIO/AM, TAM.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| CrowdStrike system ID | Yes | `liongard_system LIST query="crowdstrike"` |

---

## Locating the right system

```
liongard_system LIST searchMode=keyword query="crowdstrike" environmentId=<ENV_ID>
```

CrowdStrike CID = customer ID. Identify the right system by CID name on the
dataprint.

---

## Liongard data sources

### Per-vendor data — system fields

> **⚠️ Schema note — validated 2026-05-28 against live Completed system (inspector ID 102).**
> The enrolled-host array is `DevicesDetails`, NOT `Devices`. `Detections` is not in the dataprint — see Data Gaps section.

| Key | Description |
|---|---|
| `DevicesDetails` | Array of enrolled hosts: `hostname`, `status`, `product_type_desc`, `platform_name`, `last_seen`, `reduced_functionality_mode`, `rtr_state`, `device_policies` |
| `Users` | Array of console users: `uuid`, `status`, `first_name`, `last_name`, `last_login_at`, `factors`, `Roles`, `DaysSinceLastLogin`, `MFAMethod`, `RoleNames` |
| `UsersOverview` | Pre-aggregated user counts: `TotalUsers`, `UsersWithCustomerScope`, `UsersWithMFA`, `InactiveUsers`, `UsersWithMultipleRoles` — use these for headline KPIs |
| `CustomerDetails` | Tenant records: `child_cid`, `name`, `status`, `domains` |
| `DeviceIDs` / `UserIDs` / `CIDs` | ID arrays (cross-reference only) |

### Cross-inspector cross-check — asset inventory

```
liongard_device LIST environmentId=<ENV_ID> pageSize=200
```

```
# Devices CrowdStrike reports on
items[?inspectors[?name=='crowdstrike-inspector']]

# Coverage gap — compute devices without CrowdStrike
items[?!inspectors[?name=='crowdstrike-inspector'] && category == 'compute']

# Devices with CrowdStrike in EDR set
items[?contains(edr, 'CrowdStrike') || contains(edr, 'Falcon')]
```

---

## Onboarding QA — endpoint posture

Per partner-validated matrix at `reference/onboarding-qa-coverage.md` —
CrowdStrike has the strongest coverage among the EDRs:

| Question | JMESPath / approach | Coverage |
|---|---|---|
| Total endpoints managed | `length(DevicesDetails)` | ✅ |
| Active in last 30 days | `length(DevicesDetails[?status == 'normal'])` | ✅ |
| Inactive / non-normal | `length(DevicesDetails[?status != 'normal'])` | ✅ |
| Not protected (coverage gap) | Asset cross-check | 🔍 |
| Servers managed | `length(DevicesDetails[?product_type_desc == 'Server'])` | ✅ |
| High alerts / threats | Not in dataprint — see Data Gaps | ❌ |

---

## Metrics and queries

### Headline

| Metric | JMESPath | Result shape |
|---|---|---|
| Total enrolled devices | `length(DevicesDetails)` | `<integer>` |
| Active sensor count | `length(DevicesDetails[?status == 'normal'])` | `<integer>` |
| Non-normal sensor status | `length(DevicesDetails[?status != 'normal'])` | `<integer>` |
| Total servers | `length(DevicesDetails[?product_type_desc == 'Server'])` | `<integer>` |
| Servers — active sensor | `length(DevicesDetails[?product_type_desc == 'Server' && status == 'normal'])` | `<integer>` |
| Total users | `UsersOverview.TotalUsers` | `<integer>` |
| Users with MFA | `UsersOverview.UsersWithMFA` | `<integer>` |
| Inactive users | `UsersOverview.InactiveUsers` | `<integer>` |

> **Field gotcha — `DevicesDetails` not `Devices`:** The enrolled-host array is `DevicesDetails`. `Devices` returns null. Validated on live system (2026-05-28).
>
> **`Detections` not in dataprint:** CrowdStrike detection/alert data is not exposed by the inspector. See Data Gaps section. Use the Falcon console or `liongard_detection` for change-based alert data.

### Device detail

```jmespath
DevicesDetails[*].{
  hostname: hostname,
  status: status,
  productType: product_type_desc,
  platform: platform_name,
  lastSeen: last_seen,
  rfm: reduced_functionality_mode,
  rtr: rtr_state,
  policyId: device_policies.prevention.policy_id,
  policyApplied: device_policies.prevention.applied
}
```

### Prevention policy compliance

```jmespath
DevicesDetails[*].{hostname: hostname, policyId: device_policies.prevention.policy_id, applied: device_policies.prevention.applied}
```

Compliant when `device_policies.prevention.applied == true` on every host.

> **Field gotcha — policy name vs. ID:** `device_policies.prevention.policy_id` returns a UUID (e.g., `"fcc937cf6c264db88258df62fac39d35"`), not a friendly name. `prevention_policy_name` and `prevention_policy_status` do not exist in the dataprint. Cross-reference UUID in the Falcon console to get the human-readable policy name.

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Sensor not normal | `length(DevicesDetails[?status != 'normal']) > 0` | "<N> sensors not in normal state — investigate connectivity / version drift." |
| Prevention policy not applied | `DevicesDetails[?device_policies.prevention.applied != \`true\`]` count > 0 | "<N> hosts have prevention policy not applied — verify in Falcon console." |
| Inactive console users | `UsersOverview.InactiveUsers > 0` | "<N> inactive Falcon console users — review and remove stale access." |
| Users without MFA | `UsersOverview.TotalUsers − UsersOverview.UsersWithMFA > 0` | "<N> console users have no MFA — enforce MFA on all Falcon accounts." |
| Coverage gap | asset cross-check | "<N> compute devices not enrolled in Falcon." |
| Detections (data gap) | — | CrowdStrike detections are not in the Liongard dataprint. Pull active detections directly from the Falcon console. |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Total enrolled devices | ✅ use `length(DevicesDetails)` — VALIDATED | Falcon console |
| Sensor status breakdown | ✅ filter `DevicesDetails[?status == 'normal']` — VALIDATED | Falcon console |
| Server breakdown | ✅ filter `DevicesDetails[?product_type_desc == 'Server']` — VALIDATED | Falcon console |
| **Detections / alerts** | **❌ not in dataprint** — `Detections` key does not exist | Falcon console (mandatory supplement) |
| Threat severity breakdown | ❌ not in dataprint | Falcon console |
| Prevention policy name | ⚠️ UUID only (`device_policies.prevention.policy_id`) — no friendly name exposed | Falcon console for policy name lookup |

---

## Output format

Markdown / Word / PowerPoint per `output.format`.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_system LIST | query="crowdstrike" envId=<ENV_ID> | array<system> | ok |
| 3 | liongard_metric EVALUATE | jmesPath sysId=<SYS_ID> envId=<ENV_ID> | <integer>, <array> | ok |
| 4 | liongard_device LIST | envId=<ENV_ID> | array<device> | ok |
```

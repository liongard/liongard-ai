---
name: single-system-cisco-umbrella
description: >
  Use this skill when the user wants a single-system analysis of a Cisco Umbrella
  sub-organization — DNS-security deployment review, Periodic Business Review (PBR),
  roaming-client coverage audit, or virtual-appliance health check. Trigger phrases:
  "Umbrella PBR", "Cisco Umbrella report", "pull Umbrella data for <CUSTOMER>",
  "DNS security review", "OpenDNS report" (legacy name). Produces an artifact in
  the format set in the customization block.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_asset"
personas: [noc, soc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, pptx]
primitives:
  # Reconciled 2026-05-29: pruned dangling refs not present in the live dataprint (see internal/proposed-metrics-backlog.md).
  - metrics:cisco-umbrella-inspector:console-user-count
  - metrics:cisco-umbrella-inspector:destination-list-count
  - metrics:cisco-umbrella-inspector:encrypted-roaming-client-count
  - metrics:cisco-umbrella-inspector:internal-network-count
  - metrics:cisco-umbrella-inspector:network-count
  - metrics:cisco-umbrella-inspector:roaming-client-count
  - metrics:cisco-umbrella-inspector:roaming-client-inventory
  - metrics:cisco-umbrella-inspector:site-count
  - metrics:cisco-umbrella-inspector:stale-roaming-client-count
  - metrics:cisco-umbrella-inspector:virtual-appliance-count
  - metrics:cisco-umbrella-inspector:virtual-appliance-inventory
---

# Single-System Analysis — Cisco Umbrella

> **Inspector:** `cisco-umbrella-inspector` (ID 32). Cloud category. DNS Security.
> **Parent/child:** Yes. Parent = sparse stub. **Child** = the per-customer
> sub-organization with `roamingComputers`, `virtualAppliances`, `networks`,
> `internalNetworks`, `sites`, `destinationLists`, `users`, `Policies`,
> `NetworkDevices`. Always target the **child**.
>
> **Important scope note.** The Liongard Umbrella dataprint captures **configuration
> and deployment** — roaming clients, VAs, networks, sites, policies. It does NOT
> capture **traffic/blocking statistics** (request volumes, security blocks).
> Traffic data must come from the Umbrella portal/API.
>
> **References:** `reference/inspector-aliases.md` (Umbrella, OpenDNS legacy).
> `reference/asset-fields.md` for cross-checks.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-umbrella-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  deployment: "Deployment Posture"
  client_health: "Roaming Client Health"
  va_health: "Virtual Appliance Health"
  configuration: "Policies & Destination Lists"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"

slas:
  roaming_client_stale_days_max: 30   # daysSinceLastSync_r threshold
  va_health_required: "ok"             # any other state = flag

reporting_period:
  default: "last_quarter"
```

---

## When to use

- "Pull the Umbrella / DNS security data for <customer>" (PBR)
- "Roaming client coverage check"
- "Are any VAs unhealthy or upgradable?"
- "Confirm Umbrella is actively deployed for <customer>"

Cadence: monthly health check, quarterly PBR.
Personas: NOC, SOC, vCIO/AM, TAM.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Child Umbrella system ID | Yes | `liongard_system LIST query="umbrella"` → confirm via `SystemInfo.Name` |
| Reporting period | No | User or fiscal calendar |

---

## Locating the right system

```
liongard_system LIST searchMode=keyword query="umbrella" environmentId=<ENV_ID>
```

| Shape | What it is | Action |
|---|---|---|
| Sparse: `Name`, `Primary`, `Discovered`, `Description`, `UniqueCompositeKey` | **Parent** stub | Skip |
| Has `roamingComputers`, `virtualAppliances`, `networks`, `sites`, `destinationLists` | **Child** sub-organization | Use this |

`SystemInfo.Name` returns the sub-org display name (a `<string>`).

---

## Liongard data sources

> **Asset Inventory First, Metric Cross-Check.** The Umbrella per-system data is
> the source of truth for *Umbrella-specific configuration*. The asset inventory
> tells you which compute devices exist in the environment — coverage gap analysis
> is `compute device count − roaming client count`.

### Per-vendor data — child system fields

| Key | Description |
|---|---|
| `SystemInfo` | Sub-org metadata: `Name` |
| `roamingComputers` | Array of Umbrella roaming clients deployed to endpoints |
| `virtualAppliances` | Array of on-prem DNS forwarders |
| `networks` | Array of registered external networks |
| `internalNetworks` | Array of internal network ranges |
| `sites` | Array of sites/locations |
| `destinationLists` | Array of custom allow/block destination lists |
| `users` | Array of Umbrella console users |
| `roles` | Console role definitions |
| `Policies` | Array of DNS policy configurations (`name`, `priority`, `isDefault`) |
| `NetworkDevices` | Array of discovered network devices |

#### Roaming computer fields

| Field | Description |
|---|---|
| `name` | Device hostname |
| `type` | Client type (`roaming`) |
| `status` | Encryption status (`Encrypted`, etc.) |
| `version` | Umbrella client version |
| `deviceId` | Unique device identifier |
| `lastSync` | Last sync timestamp |
| `lastSyncStatus` | Last sync status |
| `osVersionName` | OS name |
| `daysSinceLastSync_r` | Computed days since last sync |

#### Virtual appliance fields

| Field | Description |
|---|---|
| `name` | VA hostname |
| `type` | Appliance type |
| `state` | Current state |
| `health` | Health status |
| `siteId` | Associated site |
| `isUpgradable` | Whether upgrade is available |

#### Network fields

| Field | Description |
|---|---|
| `name` | Network name |
| `status` | Registration status |
| `ipAddress` | External IP |
| `isDynamic` | Dynamic IP flag |
| `isVerified` | Verification status |

### Cross-inspector cross-check — asset inventory

```
liongard_asset LIST environmentId=<ENV_ID> assetType=Device detail=full pageSize=200
```

```
# Devices Umbrella sees (have a roaming client)
Devices[?Inspectors contains "cisco-umbrella-inspector"]

# Coverage gap — compute devices without roaming client
Devices where category == "compute" AND Inspectors does not contain "cisco-umbrella-inspector"
```

---

## Metrics and queries

### Deployment summary (configuration posture)

| Metric | JMESPath | Result shape |
|---|---|---|
| Roaming clients deployed | `length(roamingComputers)` | `<integer>` |
| Virtual appliances | `length(virtualAppliances)` | `<integer>` |
| Registered networks | `length(networks)` | `<integer>` |
| Internal networks | `length(internalNetworks)` | `<integer>` |
| Sites configured | `length(sites)` | `<integer>` |
| Destination lists | `length(destinationLists)` | `<integer>` |
| Console users | `length(users)` | `<integer>` |
| DNS policies | `length(Policies)` | `<integer>` |

### Roaming client health

| Metric | JMESPath | Result shape |
|---|---|---|
| Stale clients (>SLA days) | `length(roamingComputers[?daysSinceLastSync_r > <slas.roaming_client_stale_days_max>])` | `<integer>` |
| Encrypted clients | `length(roamingComputers[?status == 'Encrypted'])` | `<integer>` |
| Client version distribution | `roamingComputers[*].version` | `<array<string>>` |

### Virtual appliance health

```jmespath
virtualAppliances[*].{
  name: name,
  state: state,
  health: health,
  isUpgradable: isUpgradable,
  site: siteId
}
```

### Roaming client inventory

```jmespath
roamingComputers[*].{
  name: name,
  os: osVersionName,
  version: version,
  status: status,
  lastSync: lastSync,
  daysSinceSync: daysSinceLastSync_r
}
```

### Time-series — deployment growth

```
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="length(roamingComputers)"
```

---

## Insights & recommendations

| Insight | Trigger | Recommended action template |
|---|---|---|
| Coverage gap | asset.compute − `length(roamingComputers)` > 0 | "<N> compute devices have no Umbrella client — extend deployment." |
| Stale roaming clients | `length(roamingComputers[?daysSinceLastSync_r > <stale_days>]) > 0` | "<N> clients haven't synced in <stale_days> days — investigate." |
| Unhealthy VA | any VA where `health != "ok"` | "VA <name> in state <state>; restart or replace." |
| Upgradable VA | any VA where `isUpgradable == true` | "<N> VAs have upgrades available; schedule maintenance window." |
| Unverified networks | any `networks[?isVerified == false]` | "<N> registered networks unverified — confirm DNS-redirect config." |
| Unencrypted clients | `length(roamingComputers[?status != 'Encrypted']) > 0` | "<N> roaming clients without encrypted DNS — review policy." |

---

## Data gaps vs. typical PBR slide

The Liongard Umbrella inspector covers configuration/deployment, NOT traffic/blocking.

| PBR data point | In Liongard? | Alternative |
|---|---|---|
| Total DNS requests | No | Umbrella dashboard/API |
| Total blocks | No | Umbrella dashboard/API |
| Security blocks | No | Umbrella dashboard/API |
| DNS vs Web breakdown | No | Umbrella dashboard/API |
| Requests/blocks over time chart | No | Umbrella dashboard/API |
| Roaming client count | Yes | This recipe |
| VA health | Yes | This recipe |
| Network registration status | Yes | This recipe |

Surface gaps in the **Data Gaps** section so the reader knows what required portal
supplementation.

### What Liongard CAN provide for the slide
- Confirmation that Umbrella is actively deployed (clients exist and syncing)
- Virtual appliance health status
- Network registration and verification status
- Configuration drift detection over time (destination lists changed, networks added)

---

## Output format

Markdown / Word / PowerPoint per `output.format`. See `templates/output-block-*.md`.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_system LIST | query="umbrella" envId=<ENV_ID> | array<system> | ok |
| 3 | liongard_metric EVALUATE | jmesPath sysId=<SYS_ID> envId=<ENV_ID> | <integer> or <array> | ok |
| 4 | liongard_asset LIST | envId=<ENV_ID> assetType=Device detail=full | array<device> | ok |
```

---
name: single-system-auvik
description: >
  Use this skill when the user wants an Auvik Network Management assessment —
  tenant roster audit (parent), or per-tenant network topology, VLAN
  inventory, scan permission validation, and device/alert inventory (child).
  Trigger phrases: "Auvik tenant audit", "Auvik VLAN inventory",
  "Auvik network topology for <customer>", "which Auvik networks have scan
  disabled", "Auvik scan permission check", "multi-tenant Auvik view",
  "device discovery in Auvik", "Auvik alert inventory". Produces a network
  topology or tenant roster report using live Liongard data. Best for NOC,
  TAM, and vCIO/Account Manager.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_launchpoint, liongard_metric, liongard_timeline"
personas: [noc, technical-alignment-manager, vcio-account-manager]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  - metrics:auvik-inspector:child-alert-count
  - metrics:auvik-inspector:child-configuration-count
  - metrics:auvik-inspector:child-device-count
  - metrics:auvik-inspector:child-entity-audit-count
  - metrics:auvik-inspector:child-network-count
  - metrics:auvik-inspector:device-ip-summary
  - metrics:auvik-inspector:device-warranty-summary
  - metrics:auvik-inspector:expired-device-service-coverage-status-count
  - metrics:auvik-inspector:expired-device-service-coverage-status-list
  - metrics:auvik-inspector:expired-device-warranty-coverage-status-count
  - metrics:auvik-inspector:expired-device-warranty-coverage-status-list
  - metrics:auvik-inspector:known-interface-summary
  - metrics:auvik-inspector:network-summary
  - metrics:auvik-inspector:parent-tenant-count
  - metrics:auvik-inspector:parent-tenant-roster
  - metrics:auvik-inspector:scan-disabled-network-count
  - metrics:auvik-inspector:unknown-device-count
  - metrics:auvik-inspector:unknown-device-list
  - metrics:auvik-inspector:windows-7-workstation-count
  - metrics:auvik-inspector:windows-7-workstations-list
---

# Single-System Analysis — Auvik Network Management

> **Inspector:** `auvik-inspector` (ID 62). Network category.
> **Parent/Child inspector.** The **parent** system surfaces the Auvik
> tenant roster (one parent per Auvik MSP account). Each **child** system
> surfaces one Auvik tenant's network topology — VLANs, devices, interfaces,
> configurations, alerts, and the change audit trail. This recipe covers
> **both** the parent path and the child path.
>
> **Important:** Full value from the child path requires the Auvik inspector
> to be actively scanning. If `scanStatus == "notAllowed"` on all networks in
> a child system, Auvik has not been granted scan permission — device
> discovery is blocked until scan access is granted in the Auvik portal.
>
> **References:** `reference/inspector-aliases.md` (Auvik, Auvik Network
> Management, Auvik NMS). Pairs with `domains/network.md` for the network
> topology narrative; pairs with `domains/governance.md` for the network
> change audit via `EntityAudits`.


---

## Customize for your MSP

Edit these knobs before first use. Re-edit when your standards change. The
agent reads this block and adapts every downstream output.

```yaml
output:
  format: markdown
  filename: "<customer>-auvik-<date>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

inspector_mode: parent   # parent: tenant roster; child: per-tenant topology
                         # The agent auto-detects based on dataprint shape:
                         #   parent → Tenants[] array present
                         #   child  → SystemInfo.TenantName present

sections:
  executive_summary: "Executive Summary"
  # Parent sections
  tenant_inventory: "Tenant Inventory"
  # Child sections
  tenant_identity: "Tenant Identity"
  network_topology: "Network Topology"
  device_inventory: "Device Inventory"       # child-dataprint validated; requires scanning data
  alert_inventory: "Active Alerts"           # child-dataprint validated; requires scanning data
  change_audit: "Change Audit"               # child-dataprint validated; requires scanning data
  insights: "Key Insights"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"
  appendix: "Appendix — Methodology"

audience:
  tone: "balanced"           # technical | balanced | executive
  reading_level: "manager"   # engineer | manager | executive

slas:
  scan_disabled_networks_flagged: true   # any network with scanStatus = "notAllowed" triggers a flag
  stale_network_days: 30                 # network not modified in N days triggers a review flag
  inspector_lastseen_days_max: 7         # inherits from config/msp-config.yaml default

inspectors_in_scope:
  - auvik-inspector

naming:
  client_term: "Client"
  environment_term: "Environment"
  site_term: "Site"

qa:
  # See reference/qa-retry-pattern.md for the full QA + manual-verification spec.
  retry_on_null: true
  retry_on_empty_array: false      # empty arrays in Devices/Interfaces/Alerts may indicate
                                   # scan permission denied, not transient null — do not retry
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: false
  manual_verification_section_required: true
```

---

## When to use

- "Auvik tenant audit for <customer>"
- "Auvik VLAN inventory"
- "Auvik network topology for <customer>"
- "Which Auvik networks have scan disabled?"
- "Auvik scan permission check"
- "Multi-tenant Auvik view"
- "Device discovery in Auvik — what's been found?"
- "Auvik alert inventory"
- "Is Auvik scanning all VLANs?"
- On-demand when onboarding a new Auvik-managed customer

Cadence: monthly per tenant for topology review; on-demand during customer
onboarding, VLAN change events, or when Auvik alerts fire.

Personas:
- **NOC** (primary — scan permission validation, active alert triage,
  VLAN topology awareness)
- **TAM** (alignment — VLAN inventory currency, device discovery completeness,
  change audit review)
- **vCIO / Account Manager** (QBR — VLAN count, device count, alert delta
  as operational KPIs)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` → match by customer name |
| System ID (parent or child) | Yes — one per recipe run | `liongard_launchpoint LIST inspectorId=62 environmentIds=[<ENV_ID>]` |
| Inspector mode (parent or child) | Auto-detected | Agent checks for `Tenants[]` (parent) vs. `SystemInfo.TenantName` (child) in the dataprint |
| Optional: focus area | No | User prompt — e.g., "focus on networks with scan disabled" |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_launchpoint LIST inspectorId=62 environmentIds=[<ENV_ID>]
```


**Auto-detect inspector mode:**
- If `Tenants[]` is present in the dataprint → this is the **parent** system.
  Follow the Parent Path steps below.
- If `SystemInfo.TenantName` is present → this is a **child** system.
  Follow the Child Path steps below.

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

Check `lastSeen` for the Auvik system. If older than
`slas.inspector_lastseen_days_max` (default 7), flag as stale. Network
topology can change rapidly — stale data understates current VLAN or device
state.

---

### PARENT PATH — Tenant Inventory

Run Steps 3P when the system is the Auvik parent.

#### Step 3P — Tenant inventory

```
liongard_metric EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  jmesPathQuery="<path>"

# ── VALIDATED parent-dataprint fields (Dev MCP inspector 62) ─────────────

#   length(Tenants)
#     (integer — total Auvik tenants registered under this MSP account)

#   Tenants[].{type: type, id: id,
#               domainPrefix: attributes.domainPrefix,
#               tenantType: attributes.tenantType}
#
#   Field shapes:
#     type          — string, value is "tenant"
#     id            — string (numeric Auvik tenant ID)
#     domainPrefix  — string (Auvik subdomain; used to construct the Auvik
#                      portal URL for this tenant, e.g. "<prefix>.my.auvik.com")
#     tenantType    — string: "multiClient" (MSP management tenant) |
#                              "client" (per-customer tenant)

#   Tenants[?attributes.tenantType == `multiClient`]
#     (array — list of multi-client / MSP management tenants; VALIDATED)

#   Tenants[?attributes.tenantType == `client`]
#     (array — list of client tenants, one per managed customer; VALIDATED)
```

From the tenant list, produce:
- Total tenant count
- Count of `multiClient` vs. `client` tenants
- Per-tenant table: `domainPrefix`, `tenantType`, `id`

Flag any `multiClient` tenant that is unexpected — typically there should be
one (the MSP's own management tenant). Multiple `multiClient` tenants may
indicate a configuration issue or an inherited account structure.

---

### CHILD PATH — Per-Tenant Topology

Run Steps 3C–6C when the system is an Auvik child (one Auvik tenant).

#### Step 3C — Tenant identity

```
liongard_metric EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  jmesPathQuery="<path>"

# ── VALIDATED child-dataprint fields (Dev MCP inspector 62) ──────────────

#   SystemInfo.TenantName
#     (string — Auvik tenant display name)

#   SystemInfo.TenantID
#     (string — Auvik tenant ID; matches Tenants[].id in the parent system)
```

Confirm `TenantName` and `TenantID` match the intended customer tenant.

#### Step 4C — Network topology

```
liongard_metric EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  jmesPathQuery="<path>"

# ── VALIDATED child-dataprint fields (Dev MCP inspector 62) ──────────────

#   length(Networks)
#     (integer — number of networks/VLANs defined in this Auvik tenant)

#   Networks[].attributes.{networkType: networkType,
#                           networkName: networkName,
#                           description: description,
#                           scanStatus: scanStatus,
#                           lastModified: lastModified}
#
#   Field shapes:
#     networkType   — string (e.g. "vlan")
#     networkName   — string (VLAN display name)
#     description   — string (optional description field)
#     scanStatus    — string: "notAllowed" = scan disabled on this VLAN;
#                      other values indicate scan is permitted or pending
#     lastModified  — ISO timestamp string (last time this network record was
#                      modified in Auvik)
```

Flag any network where `scanStatus == "notAllowed"` per SLA
`scan_disabled_networks_flagged: true`. When all networks have
`scanStatus == "notAllowed"`, no device discovery is occurring — escalate
to grant scan permission in the Auvik portal.

Flag any network where `lastModified` is more than `slas.stale_network_days`
(default 30) days ago. A topology that has not changed in 30+ days may
be stale documentation or may indicate the tenant is inactive.

#### Step 5C — Confirm child-dataprint metric catalog

The published Auvik metric catalog for inspector `62` is built against
child dataprint collections such as `Devices`, `Interfaces`,
`Configurations`, `Alerts`, `DeviceWarranties`, and `Networks`. Confirm
that the selected system is a child dataprint before using these metric names:

```
liongard_metric LIST inspectorId=62 includeQuery=true
liongard_metric EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID> jmesPathQuery="keys(@)"
```

Expected child root keys include:

```
["Name", "Alerts", "Devices", "Networks", "Components", "Interfaces",
 "SystemInfo", "EntityNotes", "EntityAudits", "DeviceDetails",
 "Configurations", "NetworkDetails", "DeviceWarranties"]
```

Do not run the child metric names against the parent roster dataprint. Parent
dataprints contain `Tenants` but not `Devices`, `Alerts`, `Networks`, or
the other child topology arrays.

#### Step 6C — Device, interface, alert, and audit inventory

> **VALIDATED child dataprint paths.** The Dev MCP child sample populated
> these arrays: `Devices`, `Interfaces`, `Configurations`, `Alerts`,
> `EntityAudits`, `DeviceWarranties`, `DeviceDetails`, and `Components`.
> If the same paths are empty for a customer tenant, treat that as a
> tenant-specific data gap or scan-permission issue rather than a missing
> recipe path.

```
# VALIDATED child arrays — evaluate only on child systems

liongard_metric EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID> jmesPathQuery="length(Devices)"
liongard_metric EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID> jmesPathQuery="length(Interfaces)"
liongard_metric EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID> jmesPathQuery="length(Configurations)"
liongard_metric EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID> jmesPathQuery="length(Alerts)"
liongard_metric EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID> jmesPathQuery="length(EntityAudits)"
liongard_metric EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID> jmesPathQuery="length(DeviceWarranties)"
liongard_metric EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID> jmesPathQuery="length(DeviceDetails)"
liongard_metric EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID> jmesPathQuery="length(Components)"
```

Validated device fields include:

```
Devices[].attributes.deviceName
Devices[].attributes.deviceType
Devices[].attributes.vendorName
Devices[].attributes.makeModel
Devices[].attributes.ipAddresses
Devices[].attributes.onlineStatus
Devices[].attributes.lastSeenTime
Devices[].attributes.lastModified
Devices[].attributes.serialNumber
Devices[].attributes.firmwareVersion
Devices[].attributes.softwareVersion
```

Validated alert fields include:

```
Alerts[].attributes.name
Alerts[].attributes.status
Alerts[].attributes.severity
Alerts[].attributes.dismissed
Alerts[].attributes.detectedOn
Alerts[].attributes.dispatched
Alerts[].attributes.description
Alerts[].attributes.externalTicket
```

Validated configuration, warranty, interface, and audit fields include:

```
Configurations[].attributes.isRunning
Configurations[].attributes.backupTime
DeviceWarranties[].attributes.deviceName
DeviceWarranties[].attributes.serviceCoverageStatus
DeviceWarranties[].attributes.warrantyCoverageStatus
DeviceWarranties[].attributes.warrantyExpirationDate
Interfaces[].attributes.interfaceName
Interfaces[].attributes.interfaceType
Interfaces[].attributes.operationalStatus
Interfaces[].attributes.ipAddresses
EntityAudits[].attributes.category
EntityAudits[].attributes.action
EntityAudits[].attributes.status
EntityAudits[].attributes.dateStarted
EntityAudits[].attributes.lastActive
```

When data is present, produce:
- Device count and type breakdown (from `Devices`)
- Active alert count and severity distribution (from `Alerts`)
- Configuration count and most-recent capture date (from `Configurations`)
- Recent change events (from `EntityAudits`)

Published Auvik metric names validated against the child dataprint include:

| Metric name | Query focus |
|---|---|
| `Auvik: Expired Device Service Coverage Status List` / `Auvik: Expired Device Service Coverage Status Count` | expired device service coverage list/count from `DeviceWarranties` |
| `Auvik: Expired Device Warranty Coverage Status List` / `Auvik: Expired Device Warranty Coverage Status Count` | expired device warranty coverage list/count from `DeviceWarranties` |
| `Auvik: Unknown Device count` / `Auvik: Unknown Device List` | unknown device count/list from `Devices` |
| `Auvik: Windows 7 Workstations List` / `Auvik: Windows 7 Workstation Count` | Windows 7 workstation list/count from `Devices` |
| `Auvik: Known Interface Summary` | known interface summary from `Interfaces` |

Several catalog metrics are valid child-array concepts but returned no
historical rows in the sampled child system. Prefer direct `jmesPathQuery`
evaluation when a metric name evaluation returns an empty historical result despite the
underlying child collection being present.

### Step 7 — QA pass + render

Run the QA pass per `reference/qa-retry-pattern.md`. This recipe's QA pass
focuses on:

1. **Do not retry empty validated child arrays.** Empty `Devices`,
   `Interfaces`, `Alerts`, etc. on a child dataprint are most likely due to
   scan permission denied or tenant-specific collection gaps — retrying will
   not populate them. Document as a data gap instead.
2. **Retry transient nulls** on VALIDATED fields (`Tenants[]`,
   `SystemInfo.TenantName`, `Networks[].attributes`).
3. **Flag stale inspectors** (Step 2).
4. **Scan permission gate.** If any VALIDATED network has
   `scanStatus == "notAllowed"`, explicitly note that all child inventory
   arrays may be empty as a direct consequence.
5. **No cross-tool divergence** for this recipe — Auvik topology data is
   not in the reconciled `liongard_device` inventory. Record as a
   single-source-visibility note.

---

## QA & Manual Verification

Before rendering the report, run the QA pass per
`reference/qa-retry-pattern.md`:

1. **Retry persistent nulls.** For every VALIDATED metric call that returned
   null in Steps 3P or 3C–4C, re-run up to `qa.retry_attempts` times with
   `qa.retry_delay_seconds` between attempts.

2. **Do not retry empty validated child arrays.** Empty arrays for
   `Devices`, `Interfaces`, `Configurations`, `Alerts`, `EntityAudits`
   are expected when scan permission is denied. Flag as a data gap and
   provide the recommended remediation (grant scan permission in Auvik).

3. **Flag stale inspectors.** Compare `lastSeen` against
   `qa.flag_inspector_lastseen_threshold_days`. Add stale systems to the
   manual-verification list.

4. **Cross-tool divergence check.** Not applicable — Auvik topology data
   is not currently in the `liongard_device` reconciled inventory. Record
   this as a single-source-visibility note.

5. **Known metric gaps.** Parent tenant roster paths are direct JMESPath
   evaluations, not published metric names. Published Auvik child metric names are
   child-dataprint metrics. If sub-fields within `Devices`, `Alerts`, etc.
   are added in future, validate them from a live child system with active
   scanning and update the verification log.

6. **Render the Manual Verification appendix** in the deliverable
   (mandatory: `qa.manual_verification_section_required: true`).

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` (partner QA matrix) | ✅ | Covers network topology and device inventory questions; VLAN inventory, gateway documentation from the onboarding intake matrix. Device-level data requires a populated child dataprint. |
| CIS Controls v8.1 mapping | ✅ | CIS 1.1 — network asset inventory (`Devices`); CIS 1.2 — authorized software inventory (`Configurations`); CIS 4.1 — configuration baseline (`Configurations`); CIS 12.2 — network boundary defense (VLAN topology via `Networks[].attributes`); CIS 13.1 — intrusion detection capability (`Alerts`) |
| Cyber-insurance domain files | ✅ | `domains/network.md` — network topology documentation (VLANs, device inventory from `Devices`); `domains/governance.md` — network change audit (`EntityAudits`) |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this recipe for the network topology section; VLAN count, device count, and alert delta are child-dataprint operational KPIs. If scanning is disabled, the QBR section surfaces the scan permission gap as an open action item. |

---

## Insights & recommendations — generation patterns


| Pattern | Trigger | Recommendation template |
|---|---|---|
| Scan disabled on a VLAN | `scanStatus == "notAllowed"` on any network | "Auvik scan is disabled on VLAN <name>. Grant scan permission in the Auvik portal (Settings → Networks) to enable device discovery on this segment." |
| All networks scan-disabled | All `Networks[].attributes.scanStatus == "notAllowed"` | "Auvik has not been granted scan permission on any VLAN in tenant <TenantName>. Device discovery is fully blocked. This prevents population of Devices, Interfaces, Configurations, and Alerts. Grant scan access in Auvik to restore full topology visibility." |
| Stale network record | `lastModified` > `slas.stale_network_days` days ago | "Network <name> was last modified <date> — <N> days ago. Confirm the VLAN topology is still accurate and that Auvik is actively scanning this segment." |
| Unexpected multiClient tenant count | More than one `tenantType == "multiClient"` tenant | "More than one multi-client tenant found in this Auvik account. Typically there is one MSP management tenant. Confirm the additional multi-client tenant is intentional." |
| Tenant type unexpected | `tenantType` does not match expected value for context | "Tenant <domainPrefix> has type <tenantType>. For this environment, <expected-type> is expected. Confirm tenant configuration in the Auvik portal." |
| Active alerts present | `length(Alerts) > 0` on child dataprint | "Auvik reports <N> active alert(s) in tenant <TenantName>. Review and triage in the Auvik portal." |
| No configuration captures | `length(Configurations) == 0` on child dataprint | "No device configuration captures found for tenant <TenantName>. Confirm Auvik has been granted configuration backup permissions for managed devices." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Parent tenant roster | validated parent dataprint | `Tenants[]` |
| Child tenant identity | validated child dataprint | `SystemInfo.TenantName`, `SystemInfo.TenantID` |
| Networks / VLANs | validated child dataprint | `Networks[].attributes` |
| `Devices` — network device inventory | validated child dataprint | Grant scan permission in Auvik portal if empty |
| `DeviceWarranties` — warranty per device | validated child dataprint | Vendor / distributor records; Auvik portal device details |
| `DeviceDetails` — extended device attributes | validated child dataprint | Auvik portal |
| `Interfaces` — interface inventory | validated child dataprint | Auvik portal; SNMP/CDP/LLDP data from managed switches |
| `Components` — hardware components | validated child dataprint | Auvik portal |
| `Configurations` — device config captures | validated child dataprint | Auvik portal; confirm backup permission granted |
| `Alerts` — active Auvik alerts | validated child dataprint | Auvik portal alerting dashboard |
| `EntityAudits` — change audit trail | validated child dataprint | Auvik portal audit log |
| Published metric names for parent tenant roster | not present | Use direct `liongard_metric EVALUATE` JMESPath against `Tenants[]` |
| Published Auvik child metricNames: `Auvik: Network Summary` (620), `Auvik: Device IP Summary` (621), `Auvik: Device Warranty Summary` (623); offline/backup metrics 896-908: `Auvik: Devices with Configuration Backup Not Running List/Count`, `Auvik: Access Point Offline List/Count`, `Auvik: IPMI Device Offline List/Count`, `Auvik: Server Offline List/Count`, `Auvik: Switch Offline List/Count`, `Auvik: Hypervisor Offline List/Count`, `Auvik: Collector Offline List` | metric names confirmed in catalog; no historical rows in sampled child | Use `liongard_metric EVALUATE metricName=\`<name>\`` against an active child system; fall back to direct JMESPath |
| Auvik topology data in `liongard_device` | Not currently reconciled — Auvik-discovered devices do not appear in the cross-inspector device asset record | Single-source; no cross-check available |

> **Scan permission gate:** The root cause of most data gaps in this
> recipe is `scanStatus == "notAllowed"`. When this condition is present,
> the Auvik inspector cannot collect device topology data regardless of
> API connectivity. The fix is in the Auvik portal, not in Liongard.
> Surface this clearly in the Manual Verification appendix so the NOC or
> TAM can take the right remediation action.

---

## Output formats

The agent picks the format from `output.format` in the customization block.

| Format | Best for |
|---|---|
| `markdown` | Working draft (NOC triage, TAM alignment review, onboarding intake) |
| `word` | Customer-facing network topology letter |
| `pptx` | QBR network topology slide (VLAN count, device count, alert delta, scan permission status) |
| `xlsx` | Internal per-VLAN + per-device audit table when child inventory data is populated |

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | query=<customer> | array<environment> | ok |
| 1 | liongard_launchpoint LIST | `inspectorId=62 environmentIds=[<ENV_ID>]` | array<system> | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3P | liongard_metric EVALUATE | `jmesPathQuery="length(Tenants)"` | integer | VALIDATED parent dataprint |
| 3P | liongard_metric EVALUATE | `jmesPathQuery="Tenants[].{type: type, id: id, domainPrefix: attributes.domainPrefix, tenantType: attributes.tenantType}"` | array<tenant-object> | VALIDATED parent dataprint |
| 3P | liongard_metric EVALUATE | `jmesPathQuery="Tenants[?attributes.tenantType == \`multiClient\`]"` | filtered array | VALIDATED parent dataprint |
| 3P | liongard_metric EVALUATE | `jmesPathQuery="Tenants[?attributes.tenantType == \`client\`]"` | filtered array | VALIDATED parent dataprint |
| 3C | liongard_metric EVALUATE | `jmesPathQuery="SystemInfo.TenantName"` | string | VALIDATED child dataprint |
| 3C | liongard_metric EVALUATE | `jmesPathQuery="SystemInfo.TenantID"` | string | VALIDATED child dataprint |
| 4C | liongard_metric EVALUATE | `jmesPathQuery="length(Networks)"` | integer | VALIDATED child dataprint |
| 4C | liongard_metric EVALUATE | `jmesPathQuery="Networks[].attributes.{networkType: networkType, networkName: networkName, description: description, scanStatus: scanStatus, lastModified: lastModified}"` | array<network-attributes-object> | VALIDATED child dataprint |
| 5C | liongard_metric LIST | `inspectorId=62 includeQuery=true` | 29 metric catalog rows | ok; catalog metrics are child-dataprint metrics |
| 6C | liongard_metric EVALUATE | `jmesPathQuery="length(Devices)"` | integer | VALIDATED child dataprint |
| 6C | liongard_metric EVALUATE | `jmesPathQuery="length(Alerts)"` | integer | VALIDATED child dataprint |
| 6C | liongard_metric EVALUATE | `jmesPathQuery="length(Configurations)"` | integer | VALIDATED child dataprint |
| 6C | liongard_metric EVALUATE | `jmesPathQuery="length(EntityAudits)"` | integer | VALIDATED child dataprint |
| 6C | liongard_metric EVALUATE | `jmesPathQuery="length(DeviceWarranties)"` | integer | VALIDATED child dataprint |
| 6C | liongard_metric EVALUATE | metricName="Auvik: Expired Device Service Coverage Status List" envId=<ENV_ID> | array | VALIDATED |
| 6C | liongard_metric EVALUATE | metricName="Auvik: Expired Device Service Coverage Status Count" envId=<ENV_ID> | integer | VALIDATED |
| 6C | liongard_metric EVALUATE | metricName="Auvik: Expired Device Warranty Coverage Status List" envId=<ENV_ID> | array | VALIDATED |
| 6C | liongard_metric EVALUATE | metricName="Auvik: Expired Device Warranty Coverage Status Count" envId=<ENV_ID> | integer | VALIDATED |
| 6C | liongard_metric EVALUATE | metricName="Auvik: Unknown Device count" envId=<ENV_ID> | integer | VALIDATED |
| 6C | liongard_metric EVALUATE | metricName="Auvik: Unknown Device List" envId=<ENV_ID> | array | VALIDATED |
| 6C | liongard_metric EVALUATE | metricName="Auvik: Windows 7 Workstations List" envId=<ENV_ID> | array | VALIDATED |
| 6C | liongard_metric EVALUATE | metricName="Auvik: Windows 7 Workstation Count" envId=<ENV_ID> | integer | VALIDATED |
| 6C | liongard_metric EVALUATE | metricName="Auvik: Known Interface Summary" envId=<ENV_ID> | array | VALIDATED |
| 7 | QA pass | per reference/qa-retry-pattern.md | varies | ok |
| 7 | render | per output.format | <artifact path> | ok |
```

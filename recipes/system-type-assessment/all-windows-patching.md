---
name: system-type-windows-patching
description: >
  Use this skill when the user wants a cross-system patching summary for an
  environment — Windows patching compliance across all servers and workstations,
  per-class breakdown (server / laptop / workstation), top unpatched devices,
  Windows 11 readiness, or RMM-driven patch history. Trigger phrases: "patching
  summary for <CUSTOMER>", "Windows patch compliance report", "how patched is
  <CUSTOMER>", "top devices with pending patches", "Windows 11 readiness". This
  is a system-type recipe (not single-system) — it iterates across every Windows
  Server and Windows Workstation system in the environment, with optional RMM
  cross-check.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  - metrics:connectwise-automate:computers-total-count
  - metrics:datto-rmm:devices-pending-patches-count
  - metrics:datto-rmm:devices-snmp-enabled-count
  - metrics:kaseya-vsa-inspector:agents-offline-count
  - metrics:kaseya-vsa-inspector:agents-online-count
  - metrics:kaseya-vsa-inspector:agents-total-count
  - metrics:kaseya-vsa-inspector:alarms-critical-count
  - metrics:kaseya-vsa-inspector:alarms-open-count
  - metrics:kaseya-vsa-inspector:endpoint-security-coverage-count
  - metrics:kaseya-vsa-inspector:licensing-seat-total
  - metrics:kaseya-vsa-inspector:licensing-seat-used
  - metrics:kaseya-vsa-inspector:licensing-utilization-pct
  - metrics:kaseya-vsa-inspector:monitor-sets-assigned-count
  - metrics:kaseya-vsa-inspector:monitor-sets-disabled-count
  - metrics:kaseya-vsa-inspector:patches-critical-pending-count
  - metrics:kaseya-vsa-inspector:patches-pending-count
  - metrics:kaseya-vsa-inspector:users-mfa-enabled-count
  - metrics:kaseya-vsa-inspector:users-total-count
  - metrics:n-able-n-central:count-of-devices-added-last-30-days
  - metrics:n-able-n-central:count-of-devices-failed-state
  - metrics:n-able-n-central:count-of-devices-stale-state
  - metrics:n-able-n-central:count-of-devices-warning-state
  - metrics:n-able-n-central:count-of-esxi-servers
  - metrics:n-able-n-central:count-of-failed-jobs
  - metrics:n-able-n-central:count-of-printers
  - metrics:n-able-n-central:count-of-storage-devices
  - metrics:n-able-n-central:count-of-switch-router-devices
  - metrics:n-able-n-central:count-of-windows-laptops
  - metrics:n-able-n-central:count-of-windows-servers
  - metrics:n-able-n-central:count-of-workstations
  - metrics:n-able-n-central:device-details-powerbi
  - metrics:n-able-n-central:device-info-with-last-user
  - metrics:n-able-n-central:device-list-powerbi
  - metrics:n-able-n-central:list-of-devices-added-last-30-days
  - metrics:n-able-n-central:list-of-devices-failed-state
  - metrics:n-able-n-central:list-of-devices-stale-state
  - metrics:n-able-n-central:list-of-devices-warning-state
  - metrics:n-able-n-central:list-of-esxi-servers
  - metrics:n-able-n-central:list-of-failed-jobs
  - metrics:n-able-n-central:list-of-printers
  - metrics:n-able-n-central:list-of-storage-devices
  - metrics:n-able-n-central:list-of-switch-router-devices
  - metrics:n-able-n-central:list-of-windows-laptops
  - metrics:n-able-n-central:list-of-windows-servers
  - metrics:n-able-n-central:list-of-workstations
  - metrics:ninjaone:alerts-critical-count
  - metrics:ninjaone:alerts-open-count
  - metrics:ninjaone:devices-online-count
  - metrics:ninjaone:devices-total-count
  - metrics:ninjaone:licensing-utilization-pct
  - metrics:ninjaone:patches-critical-pending-count
  - metrics:ninjaone:patches-pending-count
  - metrics:ninjaone:users-mfa-enabled-count
  - metrics:ninjaone:users-technician-count
  - metrics:windows-server:all-drives-encrypted
  - metrics:windows-server:all-drives-encrypted-protected
  - metrics:windows-server:antivirus-list
  - metrics:windows-server:available-updates-count
  - metrics:windows-server:critical-updates-count
  - metrics:windows-server:days-since-last-reboot
  - metrics:windows-server:dns-filters-list
  - metrics:windows-server:domain-firewall-enabled
  - metrics:windows-server:drives-bitlocker-status
  - metrics:windows-server:edr-list
  - metrics:windows-server:failed-patches-count
  - metrics:windows-server:failed-patches-list
  - metrics:windows-server:file-share-count
  - metrics:windows-server:hostname
  - metrics:windows-server:installed-roles-list
  - metrics:windows-server:local-admin-list
  - metrics:windows-server:mandatory-updates-count
  - metrics:windows-server:os-name
  - metrics:windows-server:private-firewall-enabled
  - metrics:windows-server:public-firewall-enabled
  - metrics:windows-server:rdp-config
  - metrics:windows-server:warranty-active
  - metrics:windows-server:warranty-days-remaining
  - metrics:windows-workstation:all-drives-encrypted
  - metrics:windows-workstation:all-drives-encrypted-protected
  - metrics:windows-workstation:av-list
  - metrics:windows-workstation:defender-av-enabled
  - metrics:windows-workstation:defender-realtime-enabled
  - metrics:windows-workstation:defender-tamper-protected
  - metrics:windows-workstation:defender-threat-count
  - metrics:windows-workstation:dns-filters-list
  - metrics:windows-workstation:domain-firewall-enabled
  - metrics:windows-workstation:drives-bitlocker-status
  - metrics:windows-workstation:edr-list
  - metrics:windows-workstation:guest-account-disabled
  - metrics:windows-workstation:hostname
  - metrics:windows-workstation:local-users-list
  - metrics:windows-workstation:mandatory-updates-count
  - metrics:windows-workstation:mandatory-updates-list
  - metrics:windows-workstation:os-name
  - metrics:windows-workstation:private-firewall-enabled
  - metrics:windows-workstation:public-firewall-enabled
  - metrics:windows-workstation:rdp-enabled
  - metrics:windows-workstation:software-count
  - metrics:windows-workstation:total-memory-gb
  - metrics:windows-workstation:warranty-active
  - metrics:windows-workstation:warranty-days-remaining
  - metrics:windows-workstation:win11-compatible-detail
---

# System-Type Assessment — Windows Patching

> **Inspectors used:**
> - `windows-server-inspector` (ID 25) — per-server patching state
> - `windows-workstation-inspector` (ID 90) — per-workstation patching state
> - `connectwise-automate-inspector` (ID 36) **or** `ninjaone-inspector` (72) /
>   `n-able-n-central-inspector` (71) / `kaseya-vsa-inspector` (48) /
>   `datto-rmm-inspector` (73) — centralized RMM patch history (optional)
>
> **References:** `reference/inspector-aliases.md` for RMM aliases (LabTech →
> CW Automate, NinjaRMM → NinjaOne, etc.). `reference/asset-fields.md` for the
> `winElevenReady`, `Manufacturer`, `Model`, `Class`, `Role`, `Status` device
> fields used in this recipe.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-windows-patching-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  health_table: "Patching Health by Class"
  top_devices: "Top Devices with Pending Updates"
  win11_readiness: "Windows 11 Readiness"
  by_severity: "Pending Updates by Severity"
  rmm_history: "RMM Patch History"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"

slas:
  patch_age_days_max: 30
  critical_pending_max: 0
  patched_pct_min: 95
  win11_readiness_pct_min: 80     # by Win10 EOL — Oct 2025

inspectors_in_scope:               # which patching inspectors are deployed
  - windows-server-inspector
  - windows-workstation-inspector
  # - connectwise-automate-inspector
  # - ninjaone-inspector
  # - n-able-n-central-inspector
  # - kaseya-vsa-inspector
  # - datto-rmm-inspector

device_classes:
  # MSP-defined naming for the report. Maps internally to AccountType + Physical.
  laptop: "Laptop"
  desktop: "Workstation"
  server: "Server"
```

---

## When to use

- Quarterly patching summary section of a PBR
- Monthly patching compliance check
- "How patched is <customer>?"
- "Top 10 devices with pending updates"
- Windows 10 EOL planning — list devices that can't upgrade to Windows 11

Cadence: monthly health check, quarterly PBR.
Personas: NOC (operational tracking), vCIO/AM (executive summary, EOL roadmap),
TAM (deep dive, remediation planning).

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Reporting period | No | Default per customization |

This recipe does **not** take a single system ID — it iterates across every
Windows Server and Windows Workstation system in the environment.

---

## Two complementary data approaches

### Approach A — Per-endpoint (Windows Server + Workstation inspectors)

Per-device patching state. Best for **current posture** and per-device drilldown.

### Approach B — Centralized RMM (CW Automate / NinjaOne / Kaseya / N-central / Datto RMM)

Aggregate patch history and policy compliance. Best for **historical activity** and
policy context.

**Use both when both are deployed.** Approach A gives current state per device;
Approach B gives the trend and remediation activity. The asset inventory (next
section) reconciles.

---

## Liongard data sources

> **Asset Inventory First.** Before iterating per-device, pull the device asset
> inventory. It synthesizes `OperatingSystem`, `oSVersion`, `winElevenReady`,
> `Manufacturer`, `Model`, `Class`, `Role`, `Status`, and `LastSeen` across every
> inspector that sees the device — and lets you filter to scope before the
> per-device fetches.

### Cross-inspector primary — asset inventory

```
liongard_device LIST environmentId=<ENV_ID> pageSize=200
```

Filters useful for this recipe:

```
# In-scope Windows compute devices
windows_devices = Devices where OperatingSystem contains "Windows" AND category == "compute"

# By class
servers   = windows_devices where AccountType == "server"
laptops   = windows_devices where AccountType == "laptop"
desktops  = windows_devices where AccountType == "workstation"

# Win10 EOL risk
win10_eol_compatible    = windows_devices where OperatingSystem contains "Windows 10" AND winElevenReady == "Compatible"
win10_eol_incompatible  = windows_devices where OperatingSystem contains "Windows 10" AND winElevenReady == "Incompatible"

# Locally inspected vs AD-only (coverage gap)
locally_inspected = windows_devices where Inspectors contains "windows-workstation-inspector" OR Inspectors contains "windows-server-inspector"
ad_only           = windows_devices where Inspectors only contain "active-directory-inspector"

# Stale inspector (data quality flag)
stale = windows_devices where LastSeen < (today - 7 days)
```

### Per-vendor data — Windows Server / Workstation system fields

| Key | Description |
|---|---|
| `InstalledUpdates` | Array of installed Windows updates: `HotFixID`, `InstallDate`, `Description`, `InstalledBy`, `Status` |
| `AvailableUpdates` | Array of pending updates: `Title`, `MsrcSeverity` (Critical/Important/Moderate/Low/null), `IsInstalled`, `IsMandatory`, `Categories`, `KBArticleIDs`, `LastDeploymentChangeTime` |
| `WindowsUpdateConfig` | Update service configuration: notification level, auto-update, recommended updates |
| `SystemInfo` | Hostname (`CSName`), OS version, manufacturer, model |
| `OS` | OS details: `Caption`, `Version`, `BuildNumber` |
| `IsWindows11Compatible` | Win11 compatibility object: `Compatible` (bool), `Errors` (string) |
| `ComputerSystem` | Domain membership, manufacturer, model, MachineType |

### Per-vendor data — RMM inspectors (Approach B)

#### ConnectWise Automate (ID 36)

| Key | Description |
|---|---|
| `PatchHistory` | Array of patch installation records: `PatchHistoryTitle`, `ActionDate`, `ComputerId`, `ResultCode` (Succeeded/Failed/etc.), `OperationCodeName`, `PatchHistoryClient`, `DaysSinceActionDate_r` |
| `GroupPatchingPolicies` | Patching group policies: `GroupName`, `IsPatchingGroup`, `WindowsComputerCount`, `ApprovalPolicies`, `Priority` |
| `Clients` | Array of CW Automate client companies |

> Other RMMs (NinjaOne, N-central, Kaseya VSA, Datto RMM) expose similar concepts
> under different field names. The Liongard cyber-insurance domains/endpoint.md
> file documents the equivalent metrics. Patching-specific metrics by name:
> metricName=`NinjaRMM: Count of Devices not updated in the last 14 days` (1089),
> metricName=`NinjaRMM: Count of Devices with failed OS patches` (1095),
> metricName=`ConnectWise Automate: Computers Not Seen In Past 30 Days` (1502),
> metricName=`ConnectWise Automate: Days Since Server Last Patched` (1499),
> metricName=`SolarWinds N-central: Count of Devices in a Failed State` (1122),
> metricName=`SolarWinds N-central: Count of Devices in a Stale State` (1128),
> metricName=`datto-rmm-inspector: Devices with Pending Patches Count` (1069).

---

## Metrics and queries

### Per-endpoint patching metrics (Approach A — iterate per device)

| Metric | JMESPath | Result shape |
|---|---|---|
| Hostname | `SystemInfo.CSName` | `<string>` |
| Installed update count | `length(InstalledUpdates)` | `<integer>` |
| Pending update count | `length(AvailableUpdates)` | `<integer>` |
| Critical pending | `length(AvailableUpdates[?MsrcSeverity == 'Critical'])` | `<integer>` |
| Important pending | `length(AvailableUpdates[?MsrcSeverity == 'Important'])` | `<integer>` |
| Mandatory pending | `length(AvailableUpdates[?IsMandatory])` | `<integer>` |
| Mandatory titles | `AvailableUpdates[?IsMandatory].Title` | `<array<string>>` |
| OS version | `OS.Version` | `<string>` |
| Win11 compatible | `IsWindows11Compatible.Compatible` | `<bool>` |
| Update config (notification level) | `WindowsUpdateConfig.NotificationLevel` | `<string>` |
| % Patched per device | `installed / (installed + pending) * 100` (compute) | `<percent>` |

### Aggregate by class

For each class (server / laptop / desktop):

```
For each device in class:
  patched_pct = installed / (installed + pending) * 100
mean_patched_pct = mean(patched_pct values)
fully_patched_count = count where pending == 0
total_in_class = count
```

### RMM patch history (Approach B — single CW Automate / RMM call)

| Metric | JMESPath | Result shape |
|---|---|---|
| Total patch actions | `length(PatchHistory)` | `<integer>` |
| Successful | `length(PatchHistory[?ResultCode == 'Succeeded'])` | `<integer>` |
| Failed | `length(PatchHistory[?ResultCode == 'Failed'])` | `<integer>` |
| Recent (last 30d) | `length(PatchHistory[?DaysSinceActionDate_r <= \`30\`])` | `<integer>` |
| Managed clients | `length(Clients)` | `<integer>` |
| Active patching groups | `length(GroupPatchingPolicies[?IsPatchingGroup == \`true\`])` | `<integer>` |

### Time-series — patching trend

```
# Per-device pending updates trend
liongard_metric EVALUATE_TIME_SERIES
  systemId=<DEVICE_SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="length(AvailableUpdates)"

# RMM patch volume trend
liongard_metric EVALUATE_TIME_SERIES
  systemId=<RMM_SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="length(PatchHistory)"
```

---

## Insights & recommendations

| Insight | Trigger | Recommended action template |
|---|---|---|
| Overall patching compliance | mean across class < `slas.patched_pct_min` | "<class> patching at <pct>% — below <SLA>% target." |
| Critical patches pending | any device with `length(AvailableUpdates[?MsrcSeverity == 'Critical']) > slas.critical_pending_max` | "<N> devices have critical patches pending — apply within <SLA> days." |
| Top unpatched devices | rank by `length(AvailableUpdates) DESC` | "Top <N> devices by pending updates — schedule maintenance windows." |
| Windows 11 readiness | `length(devices where Win10 AND winElevenReady == "Compatible") / length(Win10 devices)` | "<pct>% of Win10 devices can upgrade to Win11; <N> require hardware refresh." |
| Hardware refresh roadmap | `winElevenReady == "Incompatible" AND OperatingSystem contains "Windows 10"` | "<N> devices require hardware replacement before Win10 EOL — plan refresh." |
| RMM patch failures | `length(PatchHistory[?ResultCode == 'Failed']) > 0` | "<N> patch failures in <period> — investigate failed installations." |
| Auto-update misconfiguration | `WindowsUpdateConfig.NotificationLevel != <expected>` | "<N> devices have non-standard Windows Update config — apply policy." |
| Stale device (no inspection) | `LastSeen < today - 7 days` | "<N> devices not inspected in 7+ days — confirm agent health." |

---

## Data gaps vs. typical PBR slide

The PBR "Patching Summary" slide is often vendor-specific (Tapestry 360,
ConnectSecure, etc.). Liongard reconstructs most fields:

| PBR field | In Liongard? | Source |
|---|---|---|
| % patched per device class | Yes | Per-endpoint aggregation |
| Critical/Security/Update Rollup counts | Yes | `AvailableUpdates[?MsrcSeverity == ...]` per device |
| Top unpatched devices | Yes | Rank by `length(AvailableUpdates)` |
| Patch installation history | Yes (when RMM connected) | RMM `PatchHistory` |
| Patches Approved Not Installed | Partial | RMM `GroupPatchingPolicies.ApprovalPolicies` vs. installed history |
| Third-party patches | Partial | RMM (CW Automate, etc.) — not Windows Update agent |
| Server/Laptop/Desktop counts | Yes | Asset inventory `AccountType` |
| Network device counts | No | Separate inspector (network category) |

---

## Output format

Markdown / Word / PowerPoint / Excel per `output.format`. **xlsx** is the natural
fit when the deliverable is a per-device patching status report (sortable,
filterable). PowerPoint works best for the executive overview with the
`% patched by class` chart and `top 10 unpatched` table.

---

## Sample workflow

```
1. liongard_environment LIST → match customer → ENV_ID
2. liongard_device LIST → cache the device inventory
3. List all Windows Server systems → SERVER_SYSTEM_IDS[]
4. List all Windows Workstation systems → WORKSTATION_SYSTEM_IDS[]
5. (Optional) Locate the RMM system (CW Automate / NinjaOne / N-central / Kaseya / Datto RMM) → RMM_SYSTEM_ID
6. For each endpoint system:
   - Evaluate length(InstalledUpdates), length(AvailableUpdates), critical pending
   - Pull SystemInfo.CSName, OS.Version, IsWindows11Compatible.Compatible
7. Aggregate by class using the asset inventory's AccountType field
8. Rank by pending update count → top-N table
9. (Optional) Evaluate RMM PatchHistory aggregates → patch activity volume + success rate
10. Run EVALUATE_TIME_SERIES on a representative device's pending count → trend
11. Compute insights against SLAs
12. Render output per output.format
```

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_device LIST | envId=<ENV_ID> | array<device> | ok |
| 3 | liongard_system LIST | inspector=windows-server envId=<ENV_ID> | array<system> | ok |
| 4 | liongard_system LIST | inspector=windows-workstation envId=<ENV_ID> | array<system> | ok |
| 5 | liongard_metric EVALUATE | jmesPath sysId=<DEVICE_SYS_ID> envId=<ENV_ID> | <integer>, <array> | ok per device |
| 6 | liongard_metric EVALUATE | jmesPath sysId=<RMM_SYS_ID> envId=<ENV_ID> | <integer>, <array> | ok |
```

---
name: single-system-windows-workstation
description: >
  Use this skill when the user wants a single-system analysis of a Windows
  workstation / laptop — onboarding QA, hardware inventory + lifecycle, patch
  posture, AV/firewall/BitLocker presence, RDP exposure, Win11 readiness.
  Trigger phrases: "Windows workstation review for <HOSTNAME>", "audit
  <LAPTOP>", "is this device Win11 ready", "BitLocker status on <HOSTNAME>".
  Produces an artifact in the format set in the customization block.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, technical-alignment-manager, vcio-account-manager]
output_formats: [markdown, word, xlsx]
primitives:
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

# Single-System Analysis — Windows Workstation

> **Inspector:** `windows-workstation-inspector` (ID 90). Endpoint category.
> One system per Windows workstation / laptop in the environment.
>
> **Scope.** This recipe covers **a single named workstation**. For
> environment-wide patching, use `recipes/system-type-assessment/all-windows-patching.md`.
> For all endpoints (server + workstation + macOS + Linux), use
> `recipes/system-type-assessment/all-endpoints.md`.
>
> **References:** `reference/inspector-aliases.md` (Workstation, WS).
> `reference/asset-fields.md` for the device asset record.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<hostname>-windows-workstation-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  identity: "Device Identity & Hardware"
  network: "Network Configuration"
  os_patching: "OS, Patching & Win11 Readiness"
  software: "Installed Software"
  security: "Security Posture"
  users: "Last User & Local Admins"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  patch_age_days_max: 30
  warranty_warn_days: 90
  inspector_lastseen_days_max: 7
  win10_eol_date: "2025-10-14"

reporting_period: { default: "current_state" }
```

---

## When to use

- New-customer onboarding — single-workstation intake
- "Is <HOSTNAME> Win11 ready?"
- Pre-decom checklist — last user, BitLocker key custody, decom date
- Insurance asset attestation on a specific high-value device

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Workstation system ID | Yes | `liongard_system LIST query="windows-workstation"` |
| Hostname (alternative) | If no system ID | Match by `SystemInfo.CSName` or asset `Hostname` |

---

## Locating the right system

```
liongard_system LIST searchMode=keyword query="windows-workstation" environmentId=<ENV_ID>
```

Many results — filter by hostname. The asset inventory provides the join key:

```
liongard_device LIST environmentId=<ENV_ID> pageSize=200
device = Data[?hostname == '<workstation-hostname>']
```

---

## Liongard data sources

> **Asset Inventory First, Metric Cross-Check.** Hardware (Manufacturer, Model,
> SerialNumber, warrantyExpiration), OS family, Win11 readiness, and
> `Inspectors[]` coverage come from the asset record. The Workstation inspector
> dataprint is the cross-check + source for software, patches, BitLocker,
> firewall profiles, RDP, local users.

### Per-vendor data — Workstation fields

| Key | Description |
|---|---|
| `SystemInfo` | `CSName`, OS, manufacturer, model, BIOS, machine type |
| `OS` | `Caption`, `Version`, `BuildNumber`, `RDPEnabled` |
| `ComputerSystem` | Domain, manufacturer, model |
| `IsWindows11Compatible` | Win11 compatibility (`Compatible` bool, `Errors` string) |
| `Software` | Installed software array |
| `InstalledUpdates` | KB articles + install dates |
| `AvailableUpdates` | Pending updates |
| `WindowsUpdateConfig` | Update service config |
| `NetConfig` | Network adapter array (IP, DNS) |
| `Firewall` | Domain/Private/Public profile state |
| `AVs` | Detected AV product names |
| `DefenderInfo` | Microsoft Defender state |
| `Drives` | Disk drives + BitLocker status |
| `Users` | Local users with admin flag |

### Cross-inspector cross-check — asset inventory

```
device = Data[?hostname == '<workstation-hostname>']
```

Asset gives:
- `Manufacturer`, `Model`, `SerialNumber`, `MACAddress`, `InternalIP`
- `warrantyExpiration` (SMBIOS / RMM)
- `winElevenReady` ("Compatible" / "Incompatible" / "Unknown")
- `LastLogin`, `LastLoginUser`
- `Inspectors[]` — coverage gap analysis

---

## Onboarding QA — Workstation intake fields

Mirror of the server recipe, scoped to workstation/laptop concerns:

| Question | Source | Coverage |
|---|---|---|
| Hostname | `SystemInfo.CSName` | ✅ |
| Site / location | RMM tag, asset `Location` | ⚠️ partial |
| Type (laptop / desktop / VM) | Asset `AccountType`, `Physical` | ✅ |
| Under warranty? | Asset `warrantyExpiration` | ⚠️ partial |
| Manufacturer / Model / Serial | Asset record | ✅ |
| IP / MAC / DNS | `NetConfig`, asset `MACAddress` / `InternalIP` | ✅ |
| Operating system | `OS.Caption` + `OS.Version` | ✅ |
| Connected to the domain? | `ComputerSystem.PartOfDomain` | ✅ |
| Reviewed installed programs | `Software[*]` | ✅ |
| Pending Windows updates | `length(AvailableUpdates)` | ✅ |
| Critical updates pending | `length(AvailableUpdates[?MsrcSeverity == 'Critical'])` | ✅ |
| RMM agent installed | `Software[*]` filter | ✅ |
| AV installed | `AVs[*].Name` | ✅ |
| Defender state | `DefenderInfo.Status.AntivirusEnabled` | ✅ |
| BitLocker on all drives | `Drives[?Type == 'Fixed' && BitlockerStatus != 'Fully Encrypted']` | ✅ |
| Win11 compatible | `IsWindows11Compatible.Compatible` (bool) | ✅ |
| Last login user | Asset `LastLoginUser` | ✅ |
| Local admins | `Users[?Admin && LocalAccount].Name` | ✅ |
| Firewall (3 profiles) | `Firewall.Domain` / `.Private` / `.Public` | ✅ |
| RDP enabled | `OS.RDPEnabled` | ✅ |

---

## Metrics and queries

### Identity / hardware

```jmespath
{
  hostname: SystemInfo.CSName,
  domain: ComputerSystem.Domain,
  manufacturer: SystemInfo.Manufacturer,
  model: SystemInfo.Model,
  serial: SystemInfo.SerialNumber,
  os: OS.Caption,
  osVersion: OS.Version,
  machineType: ComputerSystem.MachineType,
  win11Compatible: IsWindows11Compatible.Compatible,
  win11Errors: IsWindows11Compatible.Errors
}
```

### Network

```jmespath
NetConfig[*].{ adapter: Description, ip: IPAddress, dns: DNSServerSearchOrder }
```

### Patching

| Metric | JMESPath | Result shape |
|---|---|---|
| Available updates list | `AvailableUpdates[*].Title` | `<array<string>>` |
| Mandatory pending count | `length(AvailableUpdates[?IsMandatory])` | `<integer>` |
| Mandatory pending titles | `AvailableUpdates[?IsMandatory].Title` | `<array<string>>` |
| Installed software list | `Software[*]` | `<array>` |
| Installed software count | `length(Software)` | `<integer>` |

### BitLocker

| Metric | JMESPath | Result shape |
|---|---|---|
| All fixed drives encrypted? | `length(Drives[?Type == 'Fixed' && BitlockerStatus == 'Fully Encrypted']) == length(Drives[?Type == 'Fixed'])` | `<bool>` |
| BitLocker status summary | `Drives[*].{DriveName: DriveName, BitlockerStatus: BitlockerStatus}` | `<array>` |

### Firewall

| Profile | JMESPath | Compliant |
|---|---|---|
| Domain | `Firewall.Domain` | `true` |
| Private | `Firewall.Private` | `true` |
| Public | `Firewall.Public` | `true` |
| Summary | `Firewall` | all profiles `true` |

### RDP

| Metric | JMESPath | Compliant |
|---|---|---|
| RDP enabled? | `OS.RDPEnabled` | `false` for unmanaged workstations |

### AV

| Metric | JMESPath | Result |
|---|---|---|
| AV product names | `AVs[*].Name` | `<array<string>>` |
| Defender AV enabled | `DefenderInfo.Status.AntivirusEnabled` | `<bool>` |
| Any AV present? | `length(AVs) > '0'` | `<bool>` |

### Local users

```jmespath
Users[*].{ name: Name, admin: Admin, enabled: Enabled, sid: SID }
```
Default Administrator (SID ends `-500`) and Guest (`-501`) should generally be
disabled.

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Win11 incompatible | `winElevenReady == "Incompatible"` AND `OperatingSystem contains "Windows 10"` | "Hardware refresh required before Win10 EOL." |
| Win10 still in use | OS contains "Windows 10" AND today > Win10 EOL date | "Windows 10 is past EOL — upgrade or replace." |
| Critical patches pending | `length(AvailableUpdates[?MsrcSeverity == 'Critical']) > 0` | "<N> critical patches pending — apply." |
| BitLocker disabled | not all fixed drives encrypted | "Enable BitLocker on all fixed drives — escrow keys to AD/M365." |
| RDP enabled on workstation | `OS.RDPEnabled == true` | "RDP enabled — confirm intentional or disable." |
| Firewall profile off | any of Domain/Private/Public is `false` | "Re-enable firewall profile." |
| No AV detected | `length(AVs) == 0` | "No AV reported — confirm protection." |
| Default admin enabled | `Users[?contains(SID, '-500') && Enabled].Name` non-empty | "Disable or rename built-in Administrator." |
| Out-of-warranty | `warrantyExpiration < today` | "Out of warranty — schedule refresh." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Asset tag (MSP-internal) | ⚠️ partial | RMM custom field |
| Endpoint usage / activity | ⚠️ partial | RMM real-time monitoring |
| User profile size / disk usage | partial | RMM or local |
| EDR-specific posture | not in this recipe | Use the matching EDR recipe |

---

## Output format

Markdown / Word / Excel per `output.format`. **xlsx** for onboarding-QA tables.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_device LIST | envId=<ENV_ID> | array<device> | ok |
| 3 | liongard_system LIST | query="windows-workstation" envId=<ENV_ID> | array<system> | ok |
| 4 | liongard_metric EVALUATE | jmesPath sysId=<SYS_ID> envId=<ENV_ID> | varies | ok |
```

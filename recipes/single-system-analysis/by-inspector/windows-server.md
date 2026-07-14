---
name: single-system-windows-server
description: >
  Use this skill when the user wants a single-system analysis of a Windows
  Server — onboarding QA, hardware inventory + lifecycle, role/purpose audit,
  patch posture, local privileged user list, AV/firewall presence. Trigger
  phrases: "Windows server review for <HOSTNAME>", "single-server onboarding
  QA", "audit <SERVER>", "what roles are on this server". Produces an artifact
  in the format set in the customization block.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, technical-alignment-manager, vcio-account-manager]
output_formats: [markdown, word, xlsx]
primitives:
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
---

# Single-System Analysis — Windows Server

> **Inspector:** `windows-server-inspector` (ID 25). Endpoint category. One
> system per Windows Server installed in the environment.
>
> **Scope.** This recipe covers **a single named server**. For environment-wide
> patching across all servers + workstations, use
> `recipes/system-type-assessment/all-windows-patching.md`. For all servers
> compared across vendors, use
> `recipes/system-type-assessment/all-endpoints.md`.
>
> **References:** `reference/inspector-aliases.md` (Server, WinSrv).
> `reference/asset-fields.md` for the device asset record this server appears on.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<hostname>-windows-server-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  identity: "Server Identity & Hardware"
  network: "Network Configuration"
  os_patching: "OS & Patching"
  software: "Installed Software & Roles"
  security: "Security Posture"
  users: "Local Users"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  patch_age_days_max: 30
  warranty_warn_days: 90
  inspector_lastseen_days_max: 7

reporting_period: { default: "current_state" }
```

---

## When to use

- New-customer onboarding — produce a single-server intake summary
- "Audit the file server / DC / DB server"
- Pre-decom checklist — confirm role, dependencies, last-patched date
- Insurance evidence on a specific high-value server

Personas: NOC (operational state), TAM (deep dive), vCIO/AM (executive
summary).

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Server system ID | Yes | `liongard_system LIST query="windows-server"` |
| Hostname (alternative) | If no system ID | Match by `SystemInfo.CSName` |

---

## Locating the right system

```
liongard_system LIST searchMode=keyword query="windows-server" environmentId=<ENV_ID>
```

Many results when the customer has multiple servers. Filter by
`SystemInfo.CSName` (hostname) to pick the right one. The asset inventory
provides the same join key:

```
# Asset shows hostname AND inspectors[]
liongard_device LIST environmentId=<ENV_ID>
device = Data[?hostname == '<server-hostname>']
# device.inspectors[].name should contain "windows-server-inspector"
```

---

## Liongard data sources

> **Asset Inventory First, Metric Cross-Check.** For hardware lifecycle
> (manufacturer, model, serial, warranty), OS family, and `inspectors[]`
> coverage, the **asset inventory is primary**. The Windows Server inspector
> dataprint is the cross-check + the source for installed software, roles,
> patch state, and local privileged users.

### Per-vendor data — Windows Server fields

| Key | Description |
|---|---|
| `SystemInfo` | `CSName` (hostname), OS version, manufacturer, model, BIOS version, machine type |
| `OS` | `Caption`, `Version`, `BuildNumber`, `RDPEnabled` |
| `ComputerSystem` | Domain membership, manufacturer, model, machine type |
| `IsWindows11Compatible` | Win11 compatibility (less relevant for servers) |
| `Software` | Array of installed software with `DisplayName`, `DisplayVersion`, `Publisher`, `InstallDate` |
| `InstalledUpdates` | KB articles installed, install dates |
| `AvailableUpdates` | Pending updates with severity, mandatory flag |
| `WindowsUpdateConfig` | Update service config |
| `NetConfig` | Network adapter array with IP, DNS server list |
| `Firewall` | Domain/Private/Public profile state |
| `AntivirusSoftware` | Detected AV product names |
| `DefenderInfo` | Microsoft Defender state |
| `Users` | Local users with admin/local account flags |
| `Roles` | Installed Windows server roles (DC, File, IIS, DHCP, DNS, etc.) |

### Cross-inspector cross-check — asset inventory

```
liongard_device LIST environmentId=<ENV_ID> pageSize=200
device = Data[?hostname == '<server-hostname>']
```

The device asset provides:
- `Manufacturer`, `Model`, `SerialNumber` — hardware identity
- `warrantyExpiration` — when populated by SMBIOS or RMM
- `Class`, `Role`, `AccountType` — categorization
- `Physical` — physical vs. VM (false = VM; check `HostServer` for the host)
- `ClusterName`, `DataCenter` — virtualization topology
- `Inspectors[]` — confirms which inspectors see this device

---

## Onboarding QA — Windows Server intake fields

Partner-validated mapping (22 fields) — all map to existing metrics or asset
inventory:

| Question | Source | Coverage |
|---|---|---|
| Server name (hostname) | `SystemInfo.CSName` | ✅ |
| Site / location | Asset `Location`, RMM tag, or manual | ⚠️ partial — varies by RMM |
| Type (physical / VM / Hyper-V / VMware) | Asset `Physical`, `HostServer` | ✅ |
| Under warranty? | Asset `warrantyExpiration` (if populated) | ⚠️ partial |
| IP address | `NetConfig[*].IPAddress` or asset `InternalIP` | ✅ |
| DNS1 / DNS2 / DNS3 | `NetConfig[*].DNSServerSearchOrder` | ✅ |
| Operating system | `OS.Caption` + `OS.Version` | ✅ |
| Connected to the domain? | `ComputerSystem.PartOfDomain` or asset `domainRole` | ✅ |
| Reviewed installed programs | `Software[*]` | ✅ |
| Windows security updates past 2 months | `InstalledUpdates[?InstallDate > '<today − 60d>']` | ✅ |
| How many packages need updating | `length(AvailableUpdates)` | ✅ |
| Local admin / sudo users | `Users[?Admin && LocalAccount].Name` | ✅ |
| Server roles | `Roles[*]` | ✅ |
| Server roles to remove (cleanup) | `Roles[*]` review | ⚠️ judgment call |
| RMM / ConnectWise Automate installed | `Software[*]` filter for RMM agent | ✅ |
| Antivirus installed? | `AntivirusSoftware[*]` | ✅ |
| RAID health | not in dataprint | ❌ — RMM or hardware-vendor tooling |
| VMs audited (if Hyper-V host) | use `hyper-v-inspector` recipe | 🔄 pivot |
| Backup status | use `recipes/system-type-assessment/all-backups.md` | 🔄 pivot |

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
  machineType: ComputerSystem.MachineType
}
```

### Network

```jmespath
NetConfig[*].{
  adapter: Description,
  ip: IPAddress,
  dns: DNSServerSearchOrder,
  gateway: DefaultIPGateway
}
```

### Patching

| Metric | JMESPath | Result shape |
|---|---|---|
| Pending updates | `length(AvailableUpdates)` | `<integer>` |
| Mandatory pending | `length(AvailableUpdates[?IsMandatory])` | `<integer>` |
| Critical pending | `length(AvailableUpdates[?MsrcSeverity == 'Critical'])` | `<integer>` |
| Recently installed | `InstalledUpdates[?InstallDate > '<today − 30d>'].HotFixID` | `<array<string>>` |

### Local users

```jmespath
Users[*].{
  name: Name,
  admin: Admin,
  local: LocalAccount,
  enabled: Enabled,
  passwordExpires: PasswordExpires
}
```

### Software audit

```jmespath
Software[*].{
  name: DisplayName,
  version: DisplayVersion,
  publisher: Publisher,
  installDate: InstallDate
}
```

### Roles

```jmespath
Roles[*].DisplayName
```

### Security posture

| Metric | JMESPath | Result shape |
|---|---|---|
| Domain firewall enabled | `Firewall.Domain` | `<bool>` |
| Private firewall enabled | `Firewall.Private` | `<bool>` |
| Public firewall enabled | `Firewall.Public` | `<bool>` |

> **Field gotcha (VALIDATED 2026-05-28):** The firewall state is at top-level `Firewall`, not
> `Network.FirewallInfo`. The object is `{Domain: bool, Private: bool, Public: bool, DomainProfile: null,
> PrivateProfile: null, PublicProfile: null}`. Use `Firewall.Domain` directly — the boolean IS the
> enabled state. `DomainProfile`, `PrivateProfile`, and `PublicProfile` are null on typical systems
> (more detailed profile objects not present in the standard dataprint).

| Antivirus | `AntivirusSoftware[*].Name` | `<array<string>>` |
| RDP enabled | `OS.RDPEnabled` | `<bool>` |
| All drives encrypted | `length(Drives[?Type == 'Fixed' && BitlockerStatus == 'Fully Encrypted']) == length(Drives[?Type == 'Fixed'])` | `<bool>` |
| Local admin list | `Users[?Admin && LocalAccount].Name` | `<array<string>>` |

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Pending critical updates | `length(AvailableUpdates[?MsrcSeverity == 'Critical']) > 0` | "<N> critical patches pending — apply within <SLA> days." |
| Out-of-warranty | `warrantyExpiration < today` | "Warranty expired — refresh or renew support." |
| RDP enabled on server | `OS.RDPEnabled == true` | "RDP enabled — confirm scoped to admin VLAN with MFA." |
| Domain firewall off | `Firewall.Domain == false` | "Domain firewall disabled — re-enable." |
| Default admin account enabled | check via AD inspector + `Users[?CN=='Administrator']` | "Local Administrator enabled — disable or rename." |
| RMM agent missing | no RMM in `Software[*]` | "No RMM agent detected — confirm management coverage." |
| Antivirus missing | `AntivirusSoftware == []` | "No antivirus detected — confirm coverage." |
| Multiple roles consolidated | many roles on one host | "Server runs <N> roles — consider role separation for blast-radius reduction." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| RAID health | ❌ | RMM (NinjaOne, ConnectWise) or vendor tooling (iDRAC, iLO) |
| Site / location | ⚠️ partial | RMM tag; manual entry |
| Backup status | not in this recipe | `all-backups.md` cross-inspector recipe |
| VM-level patching of guests | not in this recipe | `hyper-v-inspector` or `vmware-esxi-inspector` recipes |
| Service availability uptime | not in dataprint | Monitoring tool (PRTG, Auvik, Domotz) |

---

## Output format

Markdown / Word / Excel per `output.format`. **xlsx** is the natural fit when
delivering an onboarding-QA workbook (one row per server, sortable columns).

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_device LIST | envId=<ENV_ID> | array<device> | ok |
| 3 | liongard_system LIST | query="windows-server" envId=<ENV_ID> | array<system> | ok |
| 4 | liongard_metric EVALUATE | jmesPath sysId=<SYS_ID> envId=<ENV_ID> | varies | ok |
| 4a | liongard_metric EVALUATE | jmesPathQuery="Network.FirewallInfo.Domain.Enabled" sysId=<SYS_ID> | null — WRONG PATH | BUG 2026-05-28: Path does not exist; correct path is Firewall.Domain |
| 4b | liongard_metric EVALUATE | jmesPathQuery="Firewall.Domain" sysId=<SYS_ID> | true (boolean) | VALIDATED 2026-05-28 — top-level Firewall object: {Domain: bool, Private: bool, Public: bool} |
| 4c | liongard_metric EVALUATE | jmesPathQuery="Firewall.Private" sysId=<SYS_ID> | true (boolean) | VALIDATED 2026-05-28 |
| 4d | liongard_metric EVALUATE | jmesPathQuery="Firewall.Public" sysId=<SYS_ID> | true (boolean) | VALIDATED 2026-05-28 |
```

---
name: system-type-all-servers
description: >
  Use this skill when the user wants a server-class assessment across an
  environment — Windows Servers + Linux servers (and server-class macOS where
  applicable). Scope is server-tier concerns: role inventory, role consolidation
  (blast-radius), patch cadence, local privileged accounts, server-specific
  firewall rules, RAID / storage health, AV/EDR products, hypervisor-host vs.
  guest distinction, hardware lifecycle, backup coverage. Trigger phrases:
  "server inventory for <CUSTOMER>", "all-servers report", "server-class
  assessment", "DC / file server / app server review", "what servers are at
  EOL", "are all servers backed up". Distinct from `all-endpoints.md` (which is
  the broad fleet view).
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_asset"
personas: [noc, technical-alignment-manager, vcio-account-manager, soc]
output_formats: [markdown, word, pptx, xlsx]
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

# System-Type Assessment — All Servers

> **Why this is separate from `all-endpoints.md`.** Servers are managed under
> different SLAs and security expectations than workstations. The same metric
> (RDP enabled, default admin, pending updates) has different implications on
> a server. This recipe is server-class only.
>
> **Inspectors used:** `windows-server-inspector` (25),
> `linux-inspector` (53), and `macos-inspector` (96) for the rare server-class
> Mac (mostly Mac mini / Mac Pro running services).
>
> **Pairs with:** `all-windows-patching.md` (Windows-specific patch posture),
> `all-edrs.md` (EDR fleet posture), `all-hypervisors.md` (hypervisor stack
> topology), `all-backups.md` (server backup coverage join — future).
>
> **References:** `reference/asset-fields.md` for the device asset record.
> `reference/inspector-aliases.md` for inspector lookups.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-server-assessment-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  inventory: "Server Inventory"
  by_role: "Servers by Role / Purpose"
  patching: "Patch Posture"
  privileged: "Local Privileged Accounts"
  security: "Server Security Posture"
  lifecycle: "Hardware Lifecycle & Warranty"
  virtualization: "Physical vs. Virtual Distribution"
  backup: "Backup Coverage Cross-Reference"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  # Servers commonly enforce stricter SLAs than workstations
  patch_age_days_max: 30                # critical patches
  important_patch_age_days_max: 30
  warranty_warn_days: 180               # longer lead time for server refresh
  inspector_lastseen_days_max: 1        # servers should be inspected daily
  edr_coverage_pct_min: 100             # zero tolerance on production servers
  rdp_allowed: false                    # default — override per role if jump host
  default_admin_enabled: false
  default_guest_enabled: false
  max_roles_per_server: 3               # blast-radius cap

inspectors_in_scope:
  - windows-server-inspector
  - linux-inspector
  # - macos-inspector                   # rare — uncomment if server-class Macs deployed

server_role_taxonomy:
  # Map common AD/role labels to your MSP's narrative categories
  domain_controller: ["DC", "Domain Controller", "AD DS"]
  file: ["File Server", "FS"]
  print: ["Print Server"]
  database: ["SQL Server", "MSSQL", "Postgres"]
  web: ["IIS", "Web Server", "Nginx", "Apache"]
  app: ["Application Server"]
  rdsh: ["Remote Desktop", "RDS", "RDSH"]
  backup: ["Backup Server"]
  hypervisor: ["Hyper-V Host", "ESXi Host"]
  monitoring: ["RMM Server", "Monitoring"]

reporting_period: { default: "current_state" }
```

---

## When to use

- Quarterly server-class review at the customer level
- Pre-decommission audit of a server cohort
- "Are all our servers patched / backed up / under warranty?"
- Role consolidation analysis ("we have 3 servers each running 6 roles —
  any blast-radius reduction opportunities?")
- Insurance evidence pack covering server-tier controls
- vCIO conversations on server refresh budget / EOL planning

Personas:
- **NOC** — operational state per server.
- **TAM** — deep dive, role rollup, recommendations.
- **vCIO/AM** — executive summary, refresh roadmap, risk narrative.
- **SOC** — privileged-account audit, RDP / SMB exposure, default-account
  state.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Reporting period | No | Default per customization |

Environment-scoped — no per-system input.

---

## Workflow

### Step 1 — Asset inventory primary (server-only filter)

```
liongard_asset LIST environmentId=<ENV_ID> assetType=Device detail=full pageSize=200
servers = Devices where AccountType == "server"
```

This is the **authoritative server roster**. Per-OS-inspector queries are the
cross-check + source for OS-specific evidence (roles, patches, local admins).

> **Server-class identification.** `AccountType == "server"` is the cleanest
> filter. Edge cases: a Windows Server running as a workstation (e.g., dev box)
> may be tagged differently — also include `OperatingSystem contains "Windows
> Server"`. For Linux, fall back to `OperatingSystem contains "Linux"` plus
> hostname-based heuristics if the customer uses a server-naming convention.

### Step 2 — Classify by OS

```
windows_servers  = servers where OperatingSystem contains "Windows Server"
linux_servers    = servers where OperatingSystem contains "Linux"
macos_servers    = servers where OperatingSystem contains "macOS"
unknown_servers  = servers where OS family unrecognized
```

### Step 3 — Per-server detail (iterate windows-server / linux / macos systems)

For each Windows Server system, evaluate the per-system queries from
`recipes/single-system-analysis/by-inspector/windows-server.md`. For Linux,
use `linux.md`. Stitch results into the cohort report.

Key per-server data points (from per-OS recipes):

**Windows Server — strong per-server data:**
- `SystemInfo.CSName` (hostname), `OS.Caption + OS.Version`
- Role list (`Roles[*].DisplayName`)
- Pending updates by severity (`AvailableUpdates`)
- Local privileged users (`Users[?Admin && LocalAccount]`)
- Firewall profiles (`Firewall.Domain` / `.Private` / `.Public`)
- RDP enabled (`OS.RDPEnabled`)
- Default admin (`Users[?contains(SID,'-500') && Enabled]`)
- BitLocker on fixed drives
- Antivirus product names

**Linux — partial per-server data:**
- Hostname (`SystemInfo.Hostname`)
- OS version (`SystemInfo.VERSION`)
- Sudo / privileged users (`Users[?Privileged]`)
- Several fields proposed; fall back to RMM cross-reference

### Step 4 — Roles & blast-radius rollup

```
# For each Windows Server, map Roles[] to taxonomy
for each ws in windows_servers:
  roles_present = ws.Roles[*].DisplayName mapped via server_role_taxonomy

# Counts by role
servers_by_role = group by role across windows_servers

# Servers with multi-role consolidation > slas.max_roles_per_server
high_consolidation = windows_servers where length(Roles) > slas.max_roles_per_server
```

### Step 5 — Cross-checks

```
# Backup coverage (join to all-backups.md when built)
unprotected = servers where no backup record exists for hostname

# EDR coverage (cross-check against all-edrs.md)
edr_gap = servers where no EDR inspector in Inspectors[]

# Hypervisor host vs. guest
hypervisor_hosts = servers where Inspectors contains
  ("vmware-esxi-inspector" OR "hyper-v-inspector")
vm_guests = servers where Physical == false AND HostServer != null
physical_only = servers where Physical == true
```

---

## Server posture — partner-validated mappings

22 onboarding-QA fields per Windows Server (existing metrics, see
`windows-server.md`). 22 per Linux (mostly not in the current dataprint — see Data Gaps).

| Server-class question | Source | Coverage |
|---|---|---|
| Hostname | windows-server `SystemInfo.CSName` / linux Hostname | ✅ |
| OS version | windows-server `OS.Caption` / linux metricName="Linux: Software Version" (`SystemInfo.VERSION`) | ✅ |
| Domain joined | `ComputerSystem.PartOfDomain` (Win) / proposed (Linux) | ⚠️ partial |
| Role / purpose | `Roles[*].DisplayName` (Win) / manual or naming convention (Linux) | ✅ Win, ❌ Linux |
| Local privileged users | `Users[?Admin && LocalAccount]` (Win) / `Users[?Privileged]` (Linux) | ✅ |
| Default admin enabled | `Users[?contains(SID,'-500')]` (Win) | ✅ Win |
| RDP enabled | `OS.RDPEnabled` (Win) | ✅ Win |
| Pending updates | `length(AvailableUpdates)` (Win) | ✅ Win, ❌ Linux |
| Critical updates pending | `length(AvailableUpdates[?MsrcSeverity == 'Critical'])` (Win) | ✅ Win, ❌ Linux |
| Antivirus | `AntivirusSoftware[*].Name` (Win) / proposed (Linux) | ✅ Win, ❌ Linux |
| Firewall enabled | per-profile (Win) | ✅ Win, ❌ Linux |
| Drives encrypted | BitLocker via verified Windows Server JMESPath: ``length(Drives[?Type == `Fixed` && BitlockerStatus == `Fully Encrypted`]) == length(Drives[?Type == `Fixed`])`` | ✅ Win, ❌ Linux (LUKS not in dataprint) |
| Hardware (manufacturer/model/serial) | Asset record + `SystemInfo` | ✅ |
| Warranty | Asset `warrantyExpiration` | ⚠️ partial |
| RAID health | not in dataprint | ❌ — RMM / iDRAC / iLO / vendor |
| Backup status | cross-inspector join | 🔄 see all-backups.md |

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Critical patches pending on production servers | any server with `length(AvailableUpdates[?MsrcSeverity == 'Critical']) > 0` | "<N> servers have critical patches pending — apply within <SLA> days." |
| Server-tier EDR gap | server in `edr_gap` | "<N> production servers have no EDR — install before next maintenance window." |
| RDP exposed on server | `OS.RDPEnabled == true` AND not jump host | "RDP enabled on <hostname> — confirm intentional or disable; if needed, restrict to admin VLAN + MFA." |
| Default admin enabled | `Users[?contains(SID,'-500') && Enabled]` non-empty | "Disable / rename built-in Administrator on <N> servers." |
| Role consolidation | `length(Roles) > slas.max_roles_per_server` | "<hostname> runs <N> roles — consider role separation for blast-radius reduction." |
| Out-of-warranty production server | `warrantyExpiration < today` AND server | "<N> production servers out of warranty — refresh schedule needed." |
| Stale inspector | `LastSeen > slas.inspector_lastseen_days_max` | "Server inspector hasn't reported in <N> days — confirm agent." |
| Backup gap | server in `unprotected` from all-backups join | "<N> servers have no detected backup — confirm or remediate." |
| BitLocker disabled on production server | `BitLocker not Fully Encrypted` | "<N> servers have unencrypted fixed drives — enable BitLocker; escrow keys." |
| Linux posture limited | proposed Linux metrics not yet in library | "Linux servers have limited posture data — file metric requests; supplement with RMM." |

---

## Lifecycle & refresh roadmap (forward-looking)

```
# Out of warranty already
out_of_warranty = servers where warrantyExpiration < today

# Warranty expiring within SLA
expiring = servers where today < warrantyExpiration < (today + slas.warranty_warn_days days)

# Win Server EOL by version
ws2012_r2 = servers where OperatingSystem contains "Windows Server 2012"  # extended support 2026 deadline
ws2016    = servers where OperatingSystem contains "Windows Server 2016"
# (Add Linux distros with EOL — RHEL 7, Ubuntu 18.04, etc.)
```

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Linux IP / domain / RMM coverage | ⚠️ not in dataprint metrics | Manual / RMM cross-reference |
| Linux antivirus / EDR detection | ⚠️ not in dataprint | RMM / EDR inspector cross-reference |
| RAID / storage health | ❌ | RMM (NinjaOne, ConnectWise), iDRAC, iLO, vendor mgmt |
| Service uptime / availability | ❌ | Monitoring tool (PRTG, Auvik, Domotz) |
| Server roles on Linux | ❌ | Manual / naming convention / RMM tag |
| Backup coverage detail | not in this recipe | Cross-link to `all-backups.md` |
| Hypervisor topology detail | partial | Cross-link to `all-hypervisors.md` |

---

## Output format

Markdown / Word / PowerPoint / Excel per `output.format`. **xlsx** is the
canonical server-inventory deliverable (one row per server with status columns
and conditional formatting). **pptx** for executive overview with role
distribution chart + EOL roadmap timeline.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_asset LIST | envId=<ENV_ID> assetType=Device detail=full | array<device> | ok |
| 3 | liongard_system LIST | inspector=windows-server envId=<ENV_ID> | array<system> | ok |
| 4 | liongard_system LIST | inspector=linux envId=<ENV_ID> | array<system> | ok |
| 5 | per server: liongard_metric EVALUATE | jmesPath sysId=<SYS_ID> envId=<ENV_ID> | varies | ok |
```

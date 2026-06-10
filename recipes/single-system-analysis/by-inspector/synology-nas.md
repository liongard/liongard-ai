---
name: single-system-synology-nas
description: >
  Use this skill when the user wants a single-system assessment of a Synology
  NAS appliance. Trigger phrases: "Synology NAS assessment for <customer>",
  "NAS storage health", "Synology disk health", "storage capacity report",
  "Synology user audit", "NAS share permissions", "Synology package status".
  Queries the synology-nas-inspector dataprint for system info, disk health,
  volume/pool status, share inventory, user accounts, network config, services,
  and installed packages.
compatibility: "Requires Liongard MCP: liongard_launchpoint, liongard_metric"
personas: [noc, technical-alignment-manager, vcio-account-manager]
output_formats: [markdown, word, xlsx]
primitives:
  - metrics:synology-nas:active-users-count
  - metrics:synology-nas:admin-users-count
  - metrics:synology-nas:admin-users-list
  - metrics:synology-nas:disks-normal-count
  - metrics:synology-nas:disks-ssd-count
  - metrics:synology-nas:drives-not-normal-count
  - metrics:synology-nas:drives-not-normal-list
  - metrics:synology-nas:firmware-version
  - metrics:synology-nas:iscsi-offline-count
  - metrics:synology-nas:iscsi-offline-list
  - metrics:synology-nas:model
  - metrics:synology-nas:risky-services-enabled
  - metrics:synology-nas:serial
  - metrics:synology-nas:services-disabled-count
  - metrics:synology-nas:services-enabled-count
  - metrics:synology-nas:services-total-count
  - metrics:synology-nas:shares-unencrypted-count
  - metrics:synology-nas:storage-pools-not-normal-count
  - metrics:synology-nas:storage-pools-not-normal-list
  - metrics:synology-nas:system-temperature-celsius
  - metrics:synology-nas:volumes-below-20pct-free-count
  - metrics:synology-nas:volumes-below-20pct-free-list
  - metrics:synology-nas:volumes-not-normal-count
  - metrics:synology-nas:volumes-not-normal-list
---

# Single-System Assessment — Synology NAS

> Per-appliance Synology NAS health and configuration posture. Covers hardware
> health (disks, temperature), storage capacity (volumes, pools, shares),
> user/group inventory, network configuration, enabled services, and installed
> packages.
>
> **Inspector:** `synology-nas-inspector`
> **Inspector ID:** 119
>
> **Pairs with:** `all-backups.md` (backup coverage per NAS),
> `all-endpoints.md` (NAS as a network storage node in the endpoint fleet),
> `all-network-monitoring.md` (SNMP/ping monitoring for the NAS).
>
> **Note:** The Synology NAS inspector may show "Agent Issue" status if the
> DSM API token expires or the NAS is offline. The dataprint retains the last
> successful inspection. Always check `LastSeen` in the verification log —
> hardware health data (temperature, disk status) may be stale.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-synology-nas-assessment-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  system_overview: "System Overview"
  disk_health: "Disk Health"
  storage_capacity: "Storage Capacity (Volumes & Pools)"
  shares: "Shared Folders"
  users: "User Accounts"
  network: "Network Configuration"
  services: "Enabled Services"
  packages: "Installed Packages"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 7
  disk_temp_warn_celsius: 50
  volume_space_used_pct_warn: 85
  firmware_age_days_warn: 180
  user_expired_warn: true
  services_to_flag_if_enabled:
    - "Telnet"
    - "NFS"        # flag if enabled without justification
    - "AFP"        # legacy Apple filing protocol — flag if no macOS clients

reporting_period: { default: "current_state" }
```

---

## When to use

- NAS health check during onboarding
- Quarterly storage capacity review
- "How full is the NAS / when do we need to expand?"
- Disk warranty/health audit before refresh
- Security review: unnecessary services enabled? Default admin account active?

Personas: NOC (disk/service health), TAM (capacity planning, user audit), vCIO/AM (refresh roadmap).

---

## Inputs

| Input | Required | Source |
|---|---|---|
| System ID | Yes | `liongard_launchpoint LIST inspectorId=119` |
| Environment ID | Yes | from launchpoint result |

---

## Workflow

### Step 1 — Locate the system

```
liongard_launchpoint LIST environmentId=<ENV_ID> inspectorId=119
```

Note the `systemId` and `environmentId`. Confirm `LastSeen` — if > 7 days, flag as stale and
note hardware data may not reflect current state. The inspector may show "Agent Issue"
status; the dataprint is still valid for last-known state analysis.

### Step 2 — System overview

```jmespath
SystemInfo.{
  model: model,
  firmware: firmware_ver,
  firmware_date: firmware_date,
  serial: serial,
  ram_mb: ram_size,
  cpu_vendor: cpu_vendor,
  cpu_series: cpu_series,
  cpu_cores: cpu_cores,
  temp_celsius: sys_temp,
  temp_warning: sys_tempwarn,
  uptime: up_time,
  ntp_enabled: enabled_ntp,
  ntp_server: ntp_server
}
```

**VALIDATED** — System A (inspected 2025-05-01):
- `model`: `"DS420+"` (string)
- `firmware_ver`: `"DSM 7.2.2-72806 Update 3"` (string)
- `firmware_date`: `"2025/01/20"` (YYYY/MM/DD string)
- `serial`: string
- `ram_size`: `2048` (MB, integer)
- `cpu_vendor`: `"INTEL"`, `cpu_series`: `"J4025"`, `cpu_cores`: `"2"` (string)
- `sys_temp`: `43` (°C, integer); `sys_tempwarn`: `false` (boolean)
- `up_time`: `"254:38:9"` (HH:MM:SS string)
- `enabled_ntp`: `true`; `ntp_server`: `"time.google.com"` (string)

### Step 3 — Disk health

```jmespath
Disks[].{
  id: id,
  name: name,
  model: model,
  diskType: diskType,
  portType: portType,
  isSsd: isSsd,
  drive_status: drive_status_key,
  overview_status: overview_status,
  firmware_status: firmware_status,
  remain_life_trustable: remain_life.trustable,
  remain_life_value: remain_life.value
}
```

**VALIDATED** — 4 disks on System A:
- `diskType`: `"SATA"` (string)
- `portType`: `"SATA"` (string)
- `isSsd`: `false` (boolean — `true` for SSDs)
- `drive_status_key`: `"normal"` | `"other"` (string)
- `overview_status`: `"normal"` (string)
- `firmware_status`: string (check for `"outdated"`)
- `remain_life`: **OBJECT** `{trustable: boolean, value: integer}` — NOT a scalar.
  - `remain_life.value`: `-1` for HDDs (not applicable); positive integer percent for SSDs
  - `remain_life.trustable`: `false` when value is unavailable
- **Flag:** `drive_status_key != "normal"` OR `overview_status != "normal"`
- **Flag (SSD only):** `remain_life.trustable == true AND remain_life.value < 20`

Count by status:
```jmespath
length(Disks[?drive_status_key == 'normal'])
length(Disks[?drive_status_key != 'normal'])
length(Disks[?isSsd == `true`])
```

### Step 4 — Storage capacity (volumes and pools)

**Volumes:**
```jmespath
Volumes[].{
  id: id,
  fs_type: fs_type,
  raidType: raidType,
  size_total_bytes: size.total,
  size_used_bytes: size.used,
  status: status,
  is_encrypted: is_encrypted,
  space_status: space_status.status,
  summary_status: space_status.summary_status,
  show_attention: space_status.show_attention
}
```

**VALIDATED** — volumes on System A:
- `fs_type`: `"btrfs"` (string)
- `raidType`: `"multiple"` for SHR configurations (string)
- `size.total` / `size.used`: byte integers (divide by `1099511627776` for TB)
- `is_encrypted`: `false` (boolean — **FLAG if false on volumes containing sensitive shares**)
- `space_status.status`: `"fs_normal"` (string)
- `space_status.show_attention`: `false` (boolean — **FLAG if true**)

**Storage Pools:**
```jmespath
StoragePools[].{
  id: id,
  raidType: raidType,
  status: status,
  capacity_used: capacity_used_r,
  capacity_total: capacity_total_r,
  disk_failures_tolerable: disk_failure_number
}
```

**VALIDATED**:
- `capacity_used_r`: `"10.886 TB"` (human-readable string)
- `capacity_total_r`: `"10.886 TB"` (human-readable string)
- `disk_failure_number`: `0` (integer — number of additional disk failures the pool can tolerate)
- **FLAG:** `disk_failure_number == 0` AND RAID type requires redundancy — pool cannot survive any disk failure

### Step 5 — Shared folders

```jmespath
Shares[].{
  name: name,
  path: path,
  freespace: freespace_r,
  totalspace: totalspace_r,
  encryption: encryption,
  hidden: hidden,
  recycle_bin: enable_recycle_bin
}
```

**VALIDATED** — shares on System A:
- `freespace_r`: `"8.056 TB"` (human-readable string)
- `totalspace_r`: `"10.45 TB"` (human-readable string)
- `encryption`: `0` (integer — `0` = not encrypted; flag unencrypted shares containing sensitive data)
- `hidden`: boolean
- `enable_recycle_bin`: `false` (boolean)

### Step 6 — User accounts

```jmespath
Users[].{
  name: name,
  email: email,
  expired: expired,
  groups: GroupMembershipStr_r
}
```

**VALIDATED** — users on System A:
- `expired`: `"normal"` | `"now"` (string — `"now"` = account is expired; **FLAG**)
- `GroupMembershipStr_r`: `"administrators | users"` (pipe-separated string)
- **Flag:** `expired == 'now'` → expired account (disable or remove)
- **Flag:** `name == 'admin'` → default admin account still active (rename recommended)
- Count admins: `length(Users[?contains(GroupMembershipStr_r, 'administrators')])`

### Step 7 — Network configuration

```jmespath
Network.{
  server_name: server_name,
  dns_primary: dns_primary,
  dns_secondary: dns_secondary,
  gateway: gateway,
  samba_enabled: enabled_samba,
  domain_joined: enabled_domain,
  workgroup: workgroup
}
```

**VALIDATED**:
- `server_name`: `"AXXNAS02"` (string)
- `enabled_samba`: `true` (boolean)
- `enabled_domain`: `false` (boolean — NAS joined to AD domain)
- `workgroup`: string (relevant when not domain-joined)

Per-interface detail:
```jmespath
Interfaces[].{
  name: ifname,
  ip: ip,
  mask: mask,
  speed_mbps: speed,
  status: status,
  type: type,
  dhcp: use_dhcp
}
```

**VALIDATED** — 3 interfaces on System A:
- `speed`: `1000` (Mbps integer; `-1` = disconnected/no link)
- `status`: `"connected"` | `"disconnected"` (string)
- `use_dhcp`: `true` | `false` (boolean — **FLAG DHCP on NAS**: static IP strongly recommended)

### Step 8 — Services

```jmespath
Services[?enable_status == 'enabled'].{
  display_name: display_name,
  service_id: service_id,
  status: enable_status
}
```

**VALIDATED** — `enable_status` is a **STRING** `"enabled"` | `"disabled"` (NOT a boolean).
- Correct filter: `enable_status == 'enabled'` (single quotes, string comparison)
- ❌ Do NOT use `enable_status == 'true'` — will return empty array

All services count:
```jmespath
length(Services)
length(Services[?enable_status == 'enabled'])
length(Services[?enable_status == 'disabled'])
```

Flag if any of the following appear in the enabled list:
- `display_name == 'Telnet'` — unencrypted remote access; **Critical**
- `display_name == 'NFS'` — flag if no Linux clients requiring NFS
- `display_name == 'AFP'` — legacy Apple Filing Protocol; flag if no macOS clients

### Step 9 — Installed packages

```jmespath
Packages[].{
  id: id,
  name: name,
  version: version,
  status: status,
  autoupdate: autoupdate_r,
  beta: beta_r
}
```

**VALIDATED** — 11 packages on System A:
- `status`: `"running"` | `"stopped"` | `"broken"` (string — **FLAG non-running**)
- `autoupdate_r`: `"false"` (**STRING** not boolean — `"true"` or `"false"`)
  - Filter: `autoupdate_r == 'false'` (single quotes)
  - **FLAG:** packages with `autoupdate_r == 'false'` — manual update required
- `beta_r`: `"false"` (**STRING**) — flag beta packages in production

Confirmed packages in test data: Active Insight, File Station, SMB Service, SAN Manager, Universal Search, others.

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Firmware outdated | `firmware_date` > 180 days old | "DSM firmware last updated <date> — check for updates." |
| Temperature warning | `sys_tempwarn == true` OR `sys_temp > 50°C` | "NAS temperature at <N>°C — check airflow and fan health." |
| Disk degraded | `drive_status_key != 'normal'` | "<N> disks in non-normal state — schedule replacement." |
| SSD life low | `remain_life.trustable == true AND remain_life.value < 20` | "SSD <name> at <N>% remaining life — plan replacement." |
| Pool at risk | `disk_failure_number == 0` | "Storage pool cannot tolerate additional disk failure — replace degraded disk immediately." |
| Volume high utilization | `size.used / size.total > 0.85` | "Volume at <N>% capacity — plan expansion." |
| Unencrypted volumes | `is_encrypted == false` | "Volume(s) not encrypted — enable DSM volume encryption for data at rest." |
| Expired user accounts | `expired == 'now'` | "<N> expired user accounts — disable or remove." |
| Default admin active | `name == 'admin'` in Users | "Default 'admin' account active — rename per Synology security hardening guidance." |
| NAS using DHCP | `use_dhcp == true` on active interface | "NAS IP assigned via DHCP — configure static IP for reliable network share access." |
| Telnet enabled | `display_name == 'Telnet'` in enabled services | "Telnet is enabled — disable immediately; use SSH instead." |
| Legacy AFP enabled | AFP in enabled services | "AFP (Apple Filing Protocol) is enabled — disable if no macOS clients require it." |
| Packages not auto-updating | `autoupdate_r == 'false'` | "<N> packages have auto-update disabled — schedule manual review." |
| Broken package | `status == 'broken'` | "Package <name> is in broken state — reinstall." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| S.M.A.R.T. disk attributes (raw) | ⚠️ partial | DSM Storage Manager → Disk Health |
| Backup job status (Hyper Backup) | ❌ | Separate Hyper Backup package or `all-backups.md` |
| SNMP configuration | ❌ | DSM Control Panel → Terminal & SNMP |
| Active user sessions | ❌ | DSM → Resource Monitor |
| Share-level permissions (ACL) | ❌ | DSM → Control Panel → Shared Folder → Edit |
| Remote access (QuickConnect / VPN) status | ❌ | DSM → QuickConnect |
| DSM audit log | ❌ | DSM → Log Center |

---

## Coverage cross-check

| Source | Status | Note |
|---|---|---|
| `reference/onboarding-qa-coverage.md` | ✅ | Steps 2–5 cover NAS hardware, storage capacity, and share inventory. User audit (Step 6) + service audit (Step 8) cover basic access hygiene. |
| CIS Controls (v8.1) | ✅ | CIS 1.1 (Steps 2, 5 — device + share inventory), 3.6/3.11 (Step 4 — volume encryption), 4.1/4.8 (Step 8 — disable unnecessary services including Telnet), 5.3 (Step 6 — disable inactive accounts), 7.3 (Step 9 — package/firmware update posture). |
| Cyber-insurance domain files | ✅ | Supports `domains/storage.md` (if present) for NAS device inventory, encryption posture, and access control evidence. |
| QBR / quarterly-business-review | ✅ | QBR storage section: capacity utilization trend (Step 4), disk health/lifecycle (Step 3), firmware currency (Step 2). |

---

## Output format

Markdown / Word for narrative assessment. **xlsx** for disk inventory and capacity tables
(one row per disk; one row per volume with used/total/pct).

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_launchpoint LIST | inspectorId=119 envId=<envId> | array<launchpoint> | ok — System A |
| 2 | liongard_metric EVALUATE | SystemInfo.{...} sysId=<sysId> envId=<envId> | object | VALIDATED |
| 3 | liongard_metric EVALUATE | Disks[].{...} sysId=<sysId> envId=<envId> | array(4) | VALIDATED |
| 3 | liongard_metric EVALUATE | remain_life object sysId=<sysId> envId=<envId> | {trustable: false, value: -1} | VALIDATED |
| 4 | liongard_metric EVALUATE | Volumes[].{...} sysId=<sysId> envId=<envId> | array | VALIDATED |
| 4 | liongard_metric EVALUATE | StoragePools[].{...} sysId=<sysId> envId=<envId> | array | VALIDATED |
| 5 | liongard_metric EVALUATE | Shares[].{...} sysId=<sysId> envId=<envId> | array | VALIDATED |
| 6 | liongard_metric EVALUATE | Users[].{...} sysId=<sysId> envId=<envId> | array | VALIDATED |
| 7 | liongard_metric EVALUATE | Network.{...} sysId=<sysId> envId=<envId> | object | VALIDATED |
| 7 | liongard_metric EVALUATE | Interfaces[].{...} sysId=<sysId> envId=<envId> | array(3) | VALIDATED |
| 8 | liongard_metric EVALUATE | Services[0] sysId=<sysId> envId=<envId> | {enable_status: "disabled"} | VALIDATED — STRING not boolean |
| 8 | liongard_metric EVALUATE | Services[?enable_status=='enabled'] sysId=<sysId> envId=<envId> | array | VALIDATED |
| 9 | liongard_metric EVALUATE | Packages[].{...} sysId=<sysId> envId=<envId> | array(11) | VALIDATED |
```

Last inspection: 2025-05-01 (Agent Issue status — dataprint is last-known state)

---
name: system-type-all-backups
description: >
  Use this skill when the user wants a unified backup-coverage assessment
  across an environment — which servers / endpoints / VMs are protected,
  which aren't, last-valid-backup date per protected asset, failed-backup
  trend, and backup-vendor distribution. Trigger phrases: "are all servers
  backed up", "backup coverage report", "what's our backup status",
  "all-backups review", "is the customer's backup working", "backup
  vendor inventory", "last valid backup per server", "find unprotected
  servers". Joins server-OS inspectors (Windows Server, Linux, macOS,
  ESXi, Hyper-V) against backup inspectors (Datto BCDR, Cove, Acronis,
  Axcient, Veeam VAC/VSPC, StorageCraft) by hostname / VM name to
  reconstruct the per-server backup state — there is no direct join
  field, so the recipe builds it.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, technical-alignment-manager, vcio-account-manager, soc]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  - metrics:acronis-cyber-protect-cloud:count-of-machines
  - metrics:acronis-cyber-protect-cloud:count-of-machines-not-backed-up-24h
  - metrics:acronis-cyber-protect-cloud:count-of-machines-with-backup-enabled
  - metrics:acronis-cyber-protect-cloud:list-of-machines-backed-up-30d
  - metrics:acronis-cyber-protect-cloud:list-of-machines-not-backed-up-24h
  - metrics:acronis-cyber-protect-cloud:list-of-machines-not-backed-up-30d
  - metrics:acronis-cyber-protect-cloud:list-of-machines-with-backup-enabled
  - metrics:acronis-cyber-protect-cloud:list-of-machines-without-backup-enabled
  - metrics:acronis-cyber-protect-cloud:local-storage-used-bytes
  - metrics:acronis-cyber-protect-cloud:machine-backup-summary
  - metrics:axcient-x360-recover:appliance-drive-usage-percent
  - metrics:axcient-x360-recover:appliance-health-status
  - metrics:axcient-x360-recover:appliance-health-status-reason
  - metrics:axcient-x360-recover:appliance-ip-address
  - metrics:axcient-x360-recover:appliance-last-tunnel-up
  - metrics:axcient-x360-recover:appliance-model
  - metrics:axcient-x360-recover:appliance-software-version
  - metrics:axcient-x360-recover:appliance-tunnel-info
  - metrics:axcient-x360-recover:appliance-tunnel-status
  - metrics:axcient-x360-recover:client-name
  - metrics:axcient-x360-recover:device-agent-version
  - metrics:axcient-x360-recover:device-ip-address
  - metrics:axcient-x360-recover:device-job-health-status
  - metrics:axcient-x360-recover:device-job-latest-restore-point
  - metrics:axcient-x360-recover:device-latest-cloud-restore-point
  - metrics:axcient-x360-recover:device-latest-local-restore-point
  - metrics:axcient-x360-recover:device-type
  - metrics:axcient-x360-recover:device-vault-latest-restore-point
  - metrics:axcient-x360-recover:job-health-status
  - metrics:axcient-x360-recover:organization-server-count
  - metrics:axcient-x360-recover:organization-workstation-count
  - metrics:axcient-x360-recover:unprotected-client-count
  - metrics:axcient-x360-recover:vault-connectivity-threshold
  - metrics:axcient-x360-recover:vault-days-since-latest-restore-point
  - metrics:axcient-x360-recover:vault-drive-storage-drive-size
  - metrics:axcient-x360-recover:vault-drive-storage-used-size
  - metrics:axcient-x360-recover:vault-health-status
  - metrics:axcient-x360-recover:vault-health-status-reason
  - metrics:axcient-x360-recover:vault-ip-address
  - metrics:axcient-x360-recover:vault-last-tunnel-up
  - metrics:axcient-x360-recover:vault-latest-restore-point
  - metrics:axcient-x360-recover:vault-software-version
  - metrics:axcient-x360-recover:vault-tunnel-status
  - metrics:cove-data-protection:count-backups-completed-with-errors
  - metrics:cove-data-protection:count-device-backup-overdue-24h
  - metrics:cove-data-protection:count-devices-not-synchronized
  - metrics:cove-data-protection:count-exchange-backup-overdue-24h
  - metrics:cove-data-protection:count-failed-backups
  - metrics:cove-data-protection:count-onedrive-backup-overdue-24h
  - metrics:cove-data-protection:count-protected-m365-users
  - metrics:cove-data-protection:count-sharepoint-backup-overdue-24h
  - metrics:cove-data-protection:count-users-with-2fa
  - metrics:cove-data-protection:count-users-without-2fa
  - metrics:cove-data-protection:list-backups-completed-with-errors
  - metrics:cove-data-protection:list-device-backup-overdue-24h
  - metrics:cove-data-protection:list-devices-not-synchronized
  - metrics:cove-data-protection:list-exchange-backup-overdue-24h
  - metrics:cove-data-protection:list-failed-backups
  - metrics:cove-data-protection:list-onedrive-backup-overdue-24h
  - metrics:cove-data-protection:list-protected-servers
  - metrics:cove-data-protection:list-protected-workstations
  - metrics:cove-data-protection:list-sharepoint-backup-overdue-24h
  - metrics:cove-data-protection:list-users-with-2fa
  - metrics:cove-data-protection:list-users-without-2fa
  - metrics:cove-data-protection:servers-no-backup-30d
  - metrics:cove-data-protection:total-count-of-users
  - metrics:datto-bcdr:agent-backups-without-screenshot-list
  - metrics:datto-bcdr:appliance-model
  - metrics:datto-bcdr:appliance-serial
  - metrics:datto-bcdr:assets-count
  - metrics:datto-bcdr:associated-device-list
  - metrics:datto-bcdr:backups-failed-recent-list
  - metrics:datto-bcdr:backups-older-than-30d-list
  - metrics:datto-bcdr:backups-overdue-24h-count
  - metrics:datto-bcdr:backups-overdue-24h-summary
  - metrics:datto-bcdr:days-until-service-expiry
  - metrics:datto-bcdr:days-until-warranty-expiry
  - metrics:datto-bcdr:local-storage-free-pct
  - metrics:storagecraft-spx-inspector:days-until-license-expiration
  - metrics:storagecraft-spx-inspector:last-backup-attempt-failed-count
  - metrics:storagecraft-spx-inspector:last-backup-attempt-failed-list
  - metrics:storagecraft-spx-inspector:last-successful-backup
  - metrics:storagecraft-spx-inspector:software-version
  - metrics:veeam-availability-console:backup-server-license-expiration-list
  - metrics:veeam-availability-console:license-expiration-date
  - metrics:veeam-availability-console:portal-administrator-list
  - metrics:veeam-availability-console:unhealthy-repositories-count
  - metrics:veeam-availability-console:unhealthy-repositories-list
  - metrics:veeam-vspc:agents-errors-warnings-count
  - metrics:veeam-vspc:agents-errors-warnings-list
  - metrics:veeam-vspc:agents-inaccessible-count-v5
  - metrics:veeam-vspc:agents-inaccessible-list-v5
  - metrics:veeam-vspc:agents-reboot-required-count
  - metrics:veeam-vspc:enabled-tenants-count
  - metrics:veeam-vspc:jobs-enabled-count
  - metrics:veeam-vspc:jobs-failed-or-warning-count-v5
  - metrics:veeam-vspc:jobs-failed-or-warning-list-v5
  - metrics:veeam-vspc:jobs-success-count-v5
  - metrics:veeam-vspc:proxies-disabled-count
  - metrics:veeam-vspc:proxies-disabled-list
  - metrics:veeam-vspc:proxies-out-of-date-count
  - metrics:veeam-vspc:proxies-out-of-date-list
  - metrics:veeam-vspc:server-version
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

# System-Type Assessment — All Backups (Cross-Inspector Coverage Join)

> **The hardest recipe in the library so far** — cross-inspector
> synthesis with no direct join field. Backup vendors report which
> *assets they protect*; OS / hypervisor inspectors report which
> *servers exist*. The customer wants the intersection: "is every server
> backed up, and when was its last valid backup?" The recipe reconstructs
> that by joining on hostname / VM name across multiple data shapes.
>
> **Inspectors covered:**
>
> Server-OS / hypervisor (the "should be backed up" denominator):
> - `windows-server-inspector` (ID 25)
> - `linux-inspector` (ID 53)
> - `macos-inspector` (ID 96) — server-class Macs are rare but possible
> - `vmware-esxi-inspector` (ID 59) — VM-level backup targets
> - `hyper-v-inspector` (ID 39) — VM-level backup targets
>
> Backup vendors (the "is backed up" numerator):
> - `datto-bcdr-inspector` (ID 38)
> - `cove-data-protection-inspector` (ID 76)
> - `acronis-cyber-protect-cloud-inspector` (ID 93)
> - `axcient-x360-recover-inspector` (ID 100, Beta)
> - `veeam-availability-console-inspector` (ID 35)
> - `veeam-service-provider-console-inspector` (ID 75)
> - `storagecraft-spx-inspector` (ID 46)
>
> **Pairs with:** `recipes/system-type-assessment/all-servers.md` (the
> server roster this recipe joins against);
> `recipes/single-system-analysis/by-inspector/{windows-server,linux,macos}.md`
> for per-server detail; `recipes/compliance/cyber-insurance/domains/backup.md`
> for cyber-insurance Q5 backup evidence.
>
> **References:** `reference/inspector-aliases.md` for vendor lookups
> (Cove was formerly SolarWinds Backup; Datto = SIRIS/ALTO/BCDR; Axcient
> x360 Recover used to be Replibit). `reference/asset-fields.md` for the
> `liongard_device` field map. `reference/qa-retry-pattern.md` for the
> QA pass.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-backup-coverage-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  fleet_kpis: "Backup Coverage KPIs"
  unprotected_servers: "Unprotected Servers (Critical)"
  per_server_status: "Per-Server Backup Status"
  per_vendor_breakdown: "Per-Vendor Distribution"
  failed_backups: "Failed Backups & Stale Protection"
  retention_compliance: "Retention & Frequency Compliance"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 1
  cloud_backup_max_age_hours: 24       # last successful cloud backup must be within 24h
  local_backup_max_age_hours: 24       # same for local backup
  unprotected_servers_max: 0           # zero tolerance — every server should be backed up
  retention_days_min: 30               # backup retention SLA
  failed_backup_consecutive_max: 1     # 2+ consecutive failures = escalation

inspectors_in_scope:
  # Server-OS / hypervisor (the denominator)
  servers:
    - windows-server-inspector
    - linux-inspector
    # - macos-inspector              # uncomment if server-class Macs are inspected
    - vmware-esxi-inspector
    - hyper-v-inspector

  # Backup vendors (the numerator) — set to what you actually deploy
  backups:
    - datto-bcdr-inspector
    - cove-data-protection-inspector
    # - acronis-cyber-protect-cloud-inspector
    # - axcient-x360-recover-inspector
    # - veeam-availability-console-inspector
    # - veeam-service-provider-console-inspector
    # - storagecraft-spx-inspector

# Customer-specific overrides
backup_strategy:
  expected_pattern: "3-2-1"           # 3 copies, 2 media, 1 offsite
  cloud_required_for: ["servers", "domain_controllers"]
  local_required_for: ["domain_controllers", "file_servers"]
  vms_require_image_level_backup: true

reporting_period: { default: "current_state" }

qa:
  retry_on_null: true
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 1
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: false
  manual_verification_section_required: true
```

---

## When to use

- "Are all the customer's servers backed up?"
- Quarterly backup-coverage review (vCIO + insurance evidence)
- Pre-incident drill — "what's the last-known-good restore point per server?"
- Cyber-insurance Q5 evidence pack (pairs with
  `cyber-insurance/domains/backup.md`)
- New-customer onboarding — "what's currently being backed up, and what
  needs to be added?"
- Vendor consolidation analysis — "we have 3 backup vendors; can we
  standardize?"

Personas:
- **NOC** — operational state (failures, stale backups).
- **TAM** — deep dive, per-server status, remediation planning.
- **vCIO/AM** — executive summary, vendor consolidation, insurance evidence.
- **SOC** — ransomware-recovery preparedness, retention compliance, air-gap
  posture.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Reporting period | No | Default per customization |

Environment-scoped — no per-system input. The recipe iterates per-vendor
internally.

---

## Liongard data sources

> **Asset Inventory First, Metric Cross-Check.** The cross-inspector
> device inventory is the **denominator** — every server / hypervisor
> host / VM the customer has. Per-backup-vendor system queries are the
> **numerator** — what each vendor is actively protecting. The recipe
> joins them by hostname / VM name.

| Source | Used for |
|---|---|
| `liongard_device LIST environmentId=<ENV_ID> category="compute"` | Server / VM roster (the denominator) |
| `liongard_system LIST environmentId=<ENV_ID>` | Discover deployed backup inspectors + server-OS inspectors |
| `liongard_metric EVALUATE` (per server-OS inspector) | Per-server hostname / domain / OS detail |
| `liongard_metric EVALUATE` (per backup vendor) | Per-vendor protected-asset list + last-backup state |
| Per-vendor single-system recipes under `recipes/single-system-analysis/by-inspector/` | Source of truth for each vendor's protected-asset shape |

---

## Workflow

### Step 1 — Build the server / VM denominator

Pull the device inventory and filter to server-class compute + VMs:

```
liongard_device LIST environmentId=<ENV_ID> category="compute"
                     fields=["hostname","operatingSystem","class","role","physical","hostServer","inspectors","internalIP"]

servers = devices where class == "server" OR role == "server"
                       OR operatingSystem contains "Windows Server"
                       OR operatingSystem contains "Linux"
                       OR (operatingSystem contains "macOS" AND class == "server")

vms = devices where physical == false                # VM guests
host_servers = devices where Inspectors contains "vmware-esxi-inspector"
                            OR Inspectors contains "hyper-v-inspector"
```

This is the master list of "things that should have backup coverage". A
production customer typically has 5–50 servers + hypervisor hosts and
10–500 VMs.

### Step 2 — Discover deployed backup inspectors

```
liongard_system LIST environmentId=<ENV_ID>
```

Filter for systems whose inspector slug is in `inspectors_in_scope.backups`.
Some backup vendors use a parent/child model (Datto BCDR, Acronis Cyber
Cloud, Veeam VAC, Axcient) — each child is a separate Liongard system,
typically one per protected device or per customer tenant. **Always
include both parent and child systems** in the iteration.

### Step 3 — For each backup vendor, enumerate protected assets

Each backup vendor exposes protected assets in a different field shape.
The recipe normalizes them into a common `(vendor, protected_hostname,
last_backup_at, status)` tuple set.

| Vendor | Inspector slug | Protected asset enumeration | Status field |
|---|---|---|---|
| **Datto BCDR** | `datto-bcdr-inspector` | Parent: `SystemInfo[*].clientCompanyName` + agents. Child: per-device backup history | Backup result status; last successful backup timestamp |
| **Cove Data Protection** | `cove-data-protection-inspector` | `Devices[*]` — per-device array with `Name`, `Type` (BackupManager / Office365), `BackupStatus`, `HoursSinceLastCompletedBackup` | `BackupStatus` ("Successful" / "Failed" / etc.); `HoursSinceLastCompletedBackup` |
| **Acronis Cyber Cloud** | `acronis-cyber-protect-cloud-inspector` | Parent: `ChildTenants[*]`. Child: `Resources[*]` — per-resource backup state | Resource backup-plan state + last-run-status |
| **Axcient x360 Recover** | `axcient-x360-recover-inspector` | `Clients[*].Devices[*]` — per-protected-device array | `Devices[*].jobs[*].health_status` (metricName=`Axcient: Device Job Health Status`) |
| **Veeam Availability Console** | `veeam-availability-console-inspector` | Child per-tenant: `Backups[*]` job array | Per-job status + last-run timestamp |
| **Veeam Service Provider Console** | `veeam-service-provider-console-inspector` | Similar to VAC but service-provider-scoped | Per-job status |
| **StorageCraft SPX** | `storagecraft-spx-inspector` | Single-server inspector — `SystemInfo.Hostname` is the protected device; the inspector itself represents one server's backup state | Job status array |

For each backup system, evaluate the appropriate JMESPath to extract
`(protected_hostname, last_backup_at, status)` and accumulate into a
master `protected_assets` array:

```
protected_assets = []

for cove_system in cove_systems:
  for device in Devices[?Type == "BackupManager"]:
    protected_assets.append({
      vendor: "Cove",
      hostname: device.Name,
      last_backup_hours_ago: device.HoursSinceLastCompletedBackup,
      status: device.BackupStatus
    })

for datto_system in datto_systems where is_child:
  # Datto child = per-appliance; protected hostnames in the agent array
  for agent in agents:
    protected_assets.append({
      vendor: "Datto BCDR",
      hostname: agent.machineName,
      last_backup_at: agent.lastBackupTime,
      status: agent.lastBackupStatus
    })

# ... and so on for each vendor
```

### Step 4 — Join servers against protected_assets

For each server / VM in the denominator, look up its protection state:

```
for server in servers + vms + host_servers:
  matches = protected_assets where hostname matches server.hostname
            (case-insensitive; strip domain suffix if needed)

  if length(matches) == 0:
    server.protection_status = "UNPROTECTED"
    server.last_backup = null
    server.vendor = null

  elif length(matches) == 1:
    server.protection_status = matches[0].status      # likely "Successful" or "Failed"
    server.last_backup = matches[0].last_backup_at or
                         (now - matches[0].last_backup_hours_ago hours)
    server.vendor = matches[0].vendor

  else:
    # Multiple vendors protect this server (e.g., local Cove + cloud Datto)
    server.protection_status = worst(matches)        # any failure dominates
    server.last_backup = most_recent(matches)
    server.vendor = list of vendors
```

### Step 5 — Fleet KPI rollup

| KPI | Computation |
|---|---|
| Total servers + hypervisor hosts | `length(servers) + length(host_servers)` |
| Total VMs | `length(vms)` |
| **Unprotected servers** | servers where `protection_status == "UNPROTECTED"` |
| **Unprotected VMs** | VMs where `protection_status == "UNPROTECTED"` |
| Servers with failed last backup | servers where `protection_status` indicates failure |
| Servers with stale backup (>SLA hours) | servers where `last_backup` > SLA hours ago |
| Servers protected by multiple vendors | servers where `vendor` is a list with > 1 entry |
| Backup vendor distribution | group_by `vendor`, count protected servers |
| Coverage % | (total - unprotected) / total * 100 |

### Step 6 — Per-vendor health rollup

For each backup vendor, summarize its own operational state:

| Vendor | Health KPI source |
|---|---|
| Cove | `length(Devices[?BackupStatus == "Failed"])` (metricName=`Cove Data Protection: Count of Failed Backups`) |
| Cove (24h check) | `Devices[?Type == "BackupManager" && HoursSinceLastCompletedBackup > 24]` (metricName=`Cove Data Protection: 24 Hours Since Last Completed Device Backup Count`) |
| Axcient | `Appliances[*].health_status` (metricName=`Axcient: Appliance Health Status`); `Devices[*].jobs[*].health_status` (metricName=`Axcient: Device Job Health Status`) |
| Datto BCDR | (proposed — see Data Gaps) |
| Acronis | (proposed — see Data Gaps) |
| Veeam VAC / VSPC | (proposed — see Data Gaps) |
| StorageCraft SPX | per-job result count |

---

## Hostname-join gotchas (the recipe's primary risk)

This is the section the author needs to read carefully — getting the
join wrong silently produces wrong coverage numbers.

### Match patterns

1. **Exact hostname match** (case-insensitive) — works ~80% of the time.
2. **FQDN vs. short name** — `liongard_device` typically reports short
   hostname (e.g. `DC01`). Backup vendors may report FQDN (`DC01.corp.local`)
   or vice versa. Strip the domain suffix before comparison.
3. **Alias mismatches** — some MSPs use backup-job names that don't match
   hostname (e.g. job named "Critical Servers" containing multiple
   servers). Treat the job name as a group; the underlying agent array
   has the real hostname.
4. **VM names from hypervisor vs. guest OS** — a VM's name in vCenter /
   Hyper-V Manager may differ from the OS-reported hostname. Both can
   show up in backup vendor data. Try both before declaring unprotected.
5. **Stale orphaned entries** — backup vendor may still report a protected
   device that no longer exists. Surface as a data-quality flag.

### Recommended join algorithm

```
def find_protection(server_hostname, protected_assets):
    server_short = server_hostname.split('.')[0].lower()
    server_fqdn = server_hostname.lower()

    matches = []
    for asset in protected_assets:
        asset_short = asset.hostname.split('.')[0].lower()
        asset_fqdn = asset.hostname.lower()
        if (server_short == asset_short or
            server_fqdn == asset_fqdn or
            server_short == asset_fqdn or
            server_fqdn == asset_short):
            matches.append(asset)

    # If still no matches, check VM name from hypervisor side
    # (server.hostServer / asset's hypervisor-reported VM name)
    if not matches and server.physical == false:
        for asset in protected_assets:
            if asset.vm_name and asset.vm_name.lower() == server_short:
                matches.append(asset)

    return matches
```

This handles the 95% case. The remaining 5% (custom job naming, multi-OS
machines with shared hostnames, post-migration orphans) becomes a
manual-verification item.

---

## QA & Manual Verification

Run the QA pass per `reference/qa-retry-pattern.md` before rendering output:

1. **Retry persistent nulls.** Backup vendors sometimes return partial
   data when their API is throttled — retry up to `qa.retry_attempts`
   times.

2. **Flag stale backup-vendor inspectors.** A stale backup inspector
   means the coverage view is out of date. Tighter
   `qa.flag_inspector_lastseen_threshold_days: 1` because backup state
   should be inspected daily.

3. **Hostname-join divergence checks (critical for this recipe):**

   - **Servers with zero matches**: candidate "unprotected" — but before
     declaring so, retry with FQDN-stripped + VM-name lookups. If still
     no match after the full join algorithm, escalate to
     manual-verification as a potential **rename-after-migration** or
     **custom-backup-job-naming** scenario.
   - **Servers with multi-vendor matches**: surface as "Protected by N
     vendors". This is sometimes intentional (cloud + local for DR) and
     sometimes accidental (orphaned old backup job alongside new one).
     Flag both for review.
   - **Backup-vendor entries with no matching server**: orphaned
     protection — server may have been decommissioned but backup wasn't
     turned off. Cost leak; surface in manual-verification.

4. **Proposed-metric gaps for this recipe** — surface in the
   manual-verification appendix:
   - **Datto BCDR**: Recent Datto Backup Failed flag, Backups Not
     Completed in Last 24 Hours count/list — currently all `NOT_FOUND`
     (see `cyber-insurance/domains/backup.md`)
   - **Acronis**: per-resource backup status enumeration
   - **Veeam VAC / VSPC**: per-job status normalization
   - **StorageCraft SPX**: per-job result count rollup
   - **Composite "is this server backed up?"** metric across all server-OS
     inspectors that joins to the backup vendor list — would eliminate
     this recipe's manual join logic

5. **Manual Verification appendix** — render in the deliverable. Typical
   items for this recipe:
   - Servers with no detected backup record (could be rename / custom
     job / true unprotected — verify in backup vendor console).
   - Orphaned backup-vendor entries (protected device that's been
     decommissioned).
   - Multi-vendor protected servers (confirm intentional or remove
     redundancy).
   - Backup-vendor inspector stale > 1 day (coverage view may be out of
     date).

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Unprotected servers | `length(unprotected_servers) > slas.unprotected_servers_max` | "**CRITICAL:** <N> servers have no detected backup — confirm in vendor console; if truly unprotected, onboard to backup immediately." |
| Unprotected VMs | `length(unprotected_vms) > 0` | "<N> VMs have no detected backup — confirm coverage at image-level vs. guest-OS level." |
| Backup failure spike | failed backups > prior period | "Backup failure rate up <pct>% — investigate vendor reachability, agent health, or capacity." |
| Stale backup | last successful backup > SLA hours ago | "<hostname> last successful backup was <N> hours ago — exceeds <SLA> SLA; investigate." |
| Multi-vendor protected | server has >1 backup vendor | "<hostname> protected by <vendors> — confirm intentional or consolidate." |
| Orphaned backup-vendor entry | protected device with no matching server | "<vendor> still protects <hostname>, but no matching server in inventory — likely decommissioned; remove the protection plan." |
| Hypervisor host without VM-level backup | ESXi/Hyper-V host with VMs but no image-level backup | "<host> has <N> VMs but no image-level backup — risk if host fails." |
| Domain controller without offsite | DC server without cloud-backup vendor protection | "<DC hostname> has no offsite backup — DCs warrant 3-2-1 (one offsite copy)." |
| Vendor sprawl | `length(distinct vendors) >= 3` | "Customer runs <N> backup vendors — consider consolidation; schedule vCIO conversation." |
| Stale backup-vendor inspector | inspector `lastSeen > 1 day` | "<vendor> inspector hasn't reported in <N> days — coverage view is stale; refresh." |

---

## Per-vendor coverage matrix

(Hand-maintained; consider centralizing in `reference/backup-coverage-matrix.md`
if it grows.)

| Vendor | Protected device enumeration | Last-backup field | Failed-backup detection | Health field |
|---|---|---|---|---|
| Cove Data Protection | ✅ `Devices[*]` direct | ✅ `HoursSinceLastCompletedBackup` | ✅ metricName=`Cove Data Protection: Count of Failed Backups` (failed count) | ✅ `BackupStatus` per device |
| Axcient x360 Recover | ✅ `Clients[*].Devices[*]` | ⚠️ `jobs[*].lastRunTime` (per-job, requires aggregation) | ⚠️ via `jobs[*].health_status` | ✅ metricName=`Axcient: Appliance Health Status` (appliance), `78656` (device job) |
| Datto BCDR | ⚠️ parent enumerates `SystemInfo[*].clientCompanyName`; child has agent array | ⚠️ not in dataprint | ⚠️ not in dataprint | ⚠️ not in dataprint |
| Acronis Cyber Cloud | ⚠️ parent enumerates `ChildTenants[*]`; child has `Resources[*]` | ⚠️ not in dataprint | ⚠️ not in dataprint | ⚠️ not in dataprint |
| Veeam VAC | ⚠️ per-tenant `Backups[*]` | ⚠️ not in dataprint | ⚠️ not in dataprint | ⚠️ not in dataprint |
| Veeam VSPC | ⚠️ similar to VAC | ⚠️ not in dataprint | ⚠️ not in dataprint | ⚠️ not in dataprint |
| StorageCraft SPX | ✅ single-server (`SystemInfo.Hostname` is the protected device) | ⚠️ per-job in dataprint | ⚠️ per-job in dataprint | ⚠️ aggregated count |

For ⚠️ cells the recipe falls back to client-side dataprint parsing and
flags in the manual-verification appendix. The Cove + Axcient rows are
the most-complete coverage today; the rest carry significant proposed-
metric backlog.

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Datto BCDR backup state | ⚠️ not in dataprint metrics flagged in cyber-insurance backup.md | Datto Portal / Datto Partner Portal |
| Acronis Cyber Cloud per-resource state | ⚠️ not in dataprint | Acronis Management Portal |
| Veeam VAC / VSPC per-job status normalization | ⚠️ not in dataprint | Veeam Console |
| StorageCraft SPX per-job rollup | ⚠️ not in dataprint | SPX dashboard |
| Hostname → backup join (composite metric) | ⚠️ none exists — recipe builds the join | The recipe IS the workaround |
| Per-server retention policy enforcement | ❌ not in any dataprint | Vendor portal manual review |
| Offsite / immutability flag (ransomware preparedness) | ❌ not in any dataprint | Vendor portal manual review |
| Restore test history | ❌ not in any dataprint | MSP runbook + vendor console |

> **The biggest data gap is the join itself.** Liongard's current schema
> doesn't expose a "this server is protected by vendor X, last good
> backup at Y" composite. Every recipe-author runs this same join
> logic. A future `liongard_backup_coverage` tool or composite metric
> per server-OS inspector would eliminate this recipe's most fragile
> section.

---

## Output format

Markdown / Word / PowerPoint / Excel per `output.format`. **xlsx** is
the canonical fit for the per-server status grid (one row per server
with columns: hostname, OS, last_backup, vendor, status, days_ago).
Sort by `protection_status` descending so unprotected servers are at the
top. **pptx** for the executive overview with the coverage % gauge,
unprotected-servers count, and per-vendor distribution donut.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_device LIST | envId=<ENV_ID> category=compute | array<device> | ok |
| 3 | liongard_system LIST | envId=<ENV_ID> | array<system> | ok |
| 4 | per server-OS inspector: liongard_metric EVALUATE | jmesPath sysId=<SYS_ID> envId=<ENV_ID> | per-server detail | ok per system |
| 5 | per backup vendor: liongard_metric EVALUATE | jmesPath sysId=<SYS_ID> envId=<ENV_ID> | per-vendor protected-asset list | ok per vendor |
| 6 | (in-recipe join) hostname-match algorithm | servers × protected_assets | annotated server list | ok |
| 7 | (QA pass) retry + divergence checks | per `reference/qa-retry-pattern.md` | varies | ok |
```

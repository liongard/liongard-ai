---
name: system-type-all-hypervisors
description: >
  Use this skill when the user wants a unified hypervisor stack assessment —
  VMware ESXi, VMware vCenter, and Hyper-V hosts together with their VM-to-host
  topology, datastore / storage health, capacity, license expiry, snapshot
  hygiene, HA / replication, and admin user audit. Trigger phrases: "hypervisor
  inventory", "VMware report", "Hyper-V report", "all-hypervisors review", "VM
  density per host", "datastore free space", "snapshot age audit". Pulls
  vmware-esxi-inspector, vmware-vcenter-inspector (Beta), and hyper-v-inspector
  plus asset-inventory cross-reference for VM-to-host mapping.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_asset"
personas: [noc, technical-alignment-manager, vcio-account-manager]
output_formats: [markdown, word, pptx, xlsx]
primitives: []
---

# System-Type Assessment — All Hypervisors

> **Hypervisor stack** = the layer that hosts your VMs. Different operational
> discipline from server OS — capacity, datastore health, VM density,
> snapshot hygiene, HA/replication, hardware compatibility. This recipe covers
> all three Liongard hypervisor inspectors at once.
>
> **Inspectors used:**
> - `vmware-esxi-inspector` (ID 59) — per-host data
> - `vmware-vcenter-inspector` (ID 58, **Beta**) — cluster / aggregation layer
> - `hyper-v-inspector` (ID 39) — Microsoft hypervisor host
>
> Plus the asset inventory for VM-to-host topology via `Physical`,
> `HostServer`, `ClusterName`, `DataCenter`.
>
> **Pairs with:** `all-servers.md` (the hypervisor *host* is also a server),
> `all-backups.md` (VM-level backup coverage — future), `all-windows-patching.md`
> (host OS patching for Hyper-V).
>
> **References:** `reference/asset-fields.md` (`HostServer`, `ClusterName`,
> `DataCenter`, `Physical`). `reference/inspector-aliases.md` for inspector
> lookups (ESXi vs. vCenter — distinct inspectors).

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-hypervisor-assessment-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  inventory: "Hypervisor Host Inventory"
  topology: "Cluster & Datacenter Topology"
  capacity: "VM Density & Capacity"
  storage: "Datastore / Storage Volume Health"
  vm_inventory: "Virtual Machine Inventory"
  ha_replication: "HA / Replication"
  snapshots: "Snapshot Hygiene"
  licensing: "Licensing & Expiration"
  admin_users: "Hypervisor Admin Users"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  datastore_free_pct_min: 20             # below this = warn
  datastore_free_pct_critical: 10        # below this = critical
  vm_density_max_per_host: 30            # VM count per host before recommend rebalance
  license_expiration_warn_days: 30
  inspector_lastseen_days_max: 1         # hypervisor hosts inspected daily
  snapshot_age_days_max: 7               # long-running snapshots = data integrity risk
  hyperv_replication_required_for: ["production"]   # tag to enforce per role

inspectors_in_scope:
  - vmware-esxi-inspector
  - vmware-vcenter-inspector
  - hyper-v-inspector

reporting_period: { default: "current_state" }
```

---

## When to use

- "Hypervisor inventory for <customer>"
- "How many VMs per ESXi host?"
- "Datastore free space across the cluster"
- "Any old snapshots we should consolidate?"
- "License expiration on the VMware stack"
- "Hyper-V replication health"
- vCIO conversations on virtualization-stack refresh
- Pre-migration audit before a hypervisor upgrade

Personas: NOC (operational state, capacity), TAM (deep dive,
recommendations), vCIO/AM (executive summary, refresh roadmap, capacity
planning).

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Reporting period | No | Default per customization |

Environment-scoped — no per-system input. The recipe iterates the deployed
hypervisor inspectors internally.

---

## Workflow

### Step 1 — Asset inventory primary (find VMs and hosts)

```
liongard_asset LIST environmentId=<ENV_ID> assetType=Device detail=full pageSize=200

# Hypervisor hosts (devices reported by ESXi or Hyper-V inspectors)
hypervisor_hosts = Devices where Inspectors contains
  ("vmware-esxi-inspector" OR "hyper-v-inspector" OR "vmware-vcenter-inspector")

# All VMs (from any inspector)
vms = Devices where Physical == false

# Physical hosts that aren't running a hypervisor inspector — probably bare-metal servers
bare_metal = Devices where Physical == true AND Inspectors does not contain ("vmware-esxi-inspector" OR "hyper-v-inspector")

# Cluster topology
by_cluster = vms | group_by ClusterName | count
by_datacenter = vms | group_by DataCenter | count
by_host = vms | group_by HostServer | count   # VM density per host
```

### Step 2 — Discover hypervisor systems

```
liongard_system LIST searchMode=keyword query="esxi" environmentId=<ENV_ID>
liongard_system LIST searchMode=keyword query="vcenter" environmentId=<ENV_ID>
liongard_system LIST searchMode=keyword query="hyper-v" environmentId=<ENV_ID>
```

For each, evaluate the per-host queries below.

### Step 3 — Per-host data evaluation

| Inspector | Available metrics |
|---|---|
| `vmware-esxi-inspector` | Management IP, VM list, Version, License Expiration, User list, Datastore free space (proposed), VIB count (proposed) |
| `vmware-vcenter-inspector` | Beta — cluster topology, alarms, HA state, vMotion / DRS state |
| `hyper-v-inspector` | Host OS Version, VM list, VM Count, Unhealthy storage, Replication Status |

### Step 4 — Capacity rollup

```
# VM density per host (from asset by_host)
high_density_hosts = by_host where count > slas.vm_density_max_per_host

# ESXi datastore free %
for each esxi_host:
  for each datastore:
    free_pct = free / total * 100
    if free_pct < slas.datastore_free_pct_critical: critical
    elif free_pct < slas.datastore_free_pct_min: warn

# Hyper-V volume health (metricName=`Hyper-V: Replication Enabled`)
unhealthy_hyperv_volumes = per Hyper-V host where unhealthy storage volume(s) > 0
```

### Step 5 — Snapshot hygiene (when available)

```
# VMware ESXi: snapshot data is in the dataprint per VM (snapshot list)
old_snapshots = ESXi VMs where any snapshot's age > slas.snapshot_age_days_max

# Hyper-V: checkpoint age (similar concept; may require client-side parsing)
```

> Snapshot age may be **not in current dataprint** territory in some Liongard versions —
> the partner audit didn't map it. If not directly exposed, parse the VM list
> object for `snapshot[*].createTime` client-side.

### Step 6 — HA / replication / availability

```
# Hyper-V replication (metricName=`Hyper-V: Replication Status`)
hyperv_replication = per Hyper-V host: replication status

# vCenter HA / DRS — Beta inspector; check vCenter cluster object
vcenter_ha = vCenter cluster.HA enabled and admission-control settings
```

---

## Hypervisor inventory — partner-mapped fields

| Hypervisor question | Source | Coverage |
|---|---|---|
| Host name / identifier | ESXi: hostname via asset / Hyper-V: metricName="Hyper-V: Host OS Version" | ⚠️ partial |
| Hardware model | Asset `Manufacturer + Model` | ✅ via asset |
| Management IP | metricName="VMware ESXi: Management IP Address" | ✅ |
| OS / hypervisor version | metricName="VMware ESXi: Version" / metricName="Hyper-V: Host OS Version" | ✅ |
| VM list | metricName="VMware ESXi: VM List" / metricName="Hyper-V: Virtual Machine List" | ✅ |
| VM count | ESXi: `jmesPathQuery="length(VMs)"` / metricName="Hyper-V: VM Count" | ✅ |
| Datastore free space | ⚠️ not in dataprint — manual via vCenter / esxcli | ⚠️ not available |
| Replication enabled | metricName="Hyper-V: Replication Enabled" | ✅ Hyper-V |
| Admin users | metricName="VMware ESXi: User List" | ✅ ESXi |
| License expiration | metricName="VMware ESXi: License Expiration Date" | ✅ ESXi |
| Replication status | metricName="Hyper-V: Replication Status" | ✅ Hyper-V |
| Snapshot age | not directly exposed — parse client-side | ⚠️ |
| Cluster / datacenter | Asset `ClusterName`, `DataCenter` | ✅ via asset |

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| High VM density | host with VM count > `slas.vm_density_max_per_host` | "<host> hosts <N> VMs — consider rebalance or capacity expansion." |
| Low datastore free | `free_pct < slas.datastore_free_pct_min` | "<datastore> at <pct>% free — provision storage before <forecast date>." |
| Critical datastore free | `free_pct < slas.datastore_free_pct_critical` | "**Critical**: <datastore> at <pct>% free — escalate now." |
| Unhealthy Hyper-V volume | `length(UnhealthyStorageVolumes) > 0` | "<N> Hyper-V volumes unhealthy — investigate and remediate." |
| Hyper-V replication broken | replication status not healthy on production VM | "Replication for <VM> reporting <state> — restore protection." |
| ESXi license expiring | `daysUntilExpiration < slas.license_expiration_warn_days` | "Renew ESXi license — expires in <N> days." |
| Old snapshots | snapshot age > `slas.snapshot_age_days_max` | "<N> VMs have snapshots older than <days> — consolidate." |
| Hypervisor admin user audit | unexpected entries in ESXi / vCenter user list | "Review hypervisor admin accounts — <N> entries warrant review." |
| Bare-metal physical server count | bare-metal count high relative to virt | "Consider virtualization for <N> bare-metal servers." |
| Stale hypervisor inspector | `LastSeen > slas.inspector_lastseen_days_max` | "Hypervisor inspector hasn't reported in <N> days — confirm." |
| vCenter inspector still Beta | vCenter inspector deployed | "vCenter inspector is Beta — supplement with vCenter UI for cluster aggregations not yet exposed." |

---

## Forward-looking lifecycle

```
# ESXi / vSphere version EOL planning
esxi_eol = ESXi hosts where Version is at extended support / unsupported
# (cross-reference VMware lifecycle policy externally; not in dataprint)

# Hyper-V host OS lifecycle
hyperv_eol = Hyper-V hosts where Host OS Version contains "Windows Server 2012"  # ESU 2026

# Hardware host EOL via asset.warrantyExpiration
host_warranty_expiring = hypervisor_hosts where warrantyExpiration < (today + 180 days)
```

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| ESXi datastore free space | ⚠️ not in dataprint | Manual via vCenter or `esxcli` |
| ESXi VIB / patch level detail | ⚠️ not in dataprint | `esxcli software vib list` |
| vCenter cluster aggregations | ⚠️ Beta inspector | vCenter UI |
| Snapshot age | ⚠️ partial — parse client-side | vCenter UI / PowerCLI |
| VMware HA / DRS / vMotion state | ⚠️ Beta vCenter inspector | vCenter UI |
| Hyper-V cluster (failover) state | not in dataprint | Failover Cluster Manager |
| Per-VM CPU/RAM utilization | not in dataprint | vCenter / SCVMM / monitoring |
| Backup coverage of VMs | cross-link | `all-backups.md` (future) |

---

## Output format

Markdown / Word / PowerPoint / Excel per `output.format`. **xlsx** for
host-and-VM inventory grids; **pptx** for executive overview with cluster
topology diagram and capacity charts.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_asset LIST | envId=<ENV_ID> assetType=Device detail=full | array<device> | ok |
| 3 | liongard_system LIST | query="esxi" envId=<ENV_ID> | array<system> | ok |
| 4 | liongard_system LIST | query="vcenter" envId=<ENV_ID> | array<system> | ok |
| 5 | liongard_system LIST | query="hyper-v" envId=<ENV_ID> | array<system> | ok |
| 6 | per host: liongard_metric EVALUATE | jmesPath sysId=<SYS_ID> envId=<ENV_ID> | varies | ok |
```

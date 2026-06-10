---
name: system-type-all-endpoints
description: >
  Use this skill when the user wants a unified endpoint inventory across every
  OS — Windows Server, Windows Workstation, macOS, Linux. Trigger phrases:
  "endpoint inventory for <CUSTOMER>", "all endpoints report", "fleet OS
  breakdown", "device inventory by class", "Windows 11 readiness across the
  fleet". Iterates the OS inspectors and the asset inventory to produce a
  unified endpoint posture across class (server/laptop/desktop), OS family,
  hardware vendor, virtualization, and security tooling.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, vcio-account-manager, technical-alignment-manager, accounting-finance]
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

# System-Type Assessment — All Endpoints

> Cross-OS endpoint **fleet** view. Combines `windows-server-inspector`,
> `windows-workstation-inspector`, `macos-inspector`, `linux-inspector` with
> the asset inventory to produce a unified inventory across class, OS family,
> hardware vendor, virtualization, and security tooling.
>
> **For server-class deep dive, use `all-servers.md` instead** — servers are
> managed under different SLAs and security expectations than workstations.
> This recipe gives the fleet view; `all-servers.md` zooms in on production
> servers with role inventory, blast-radius analysis, server-tier patch
> cadence, and lifecycle. Run both for a full picture: this recipe for
> composition + workstation posture; `all-servers.md` for server-tier
> assessment.
>
> **Pairs with:** `all-servers.md` (server-class deep dive),
> `all-hypervisors.md` (hypervisor stack: ESXi, vCenter, Hyper-V),
> `all-edrs.md` (EDR posture across all vendors), `all-windows-patching.md`
> (Windows patch compliance), `all-backups.md` (future — backup coverage
> per server), `addigy.md` (macOS MDM policy/enrollment coverage),
> `watchman-monitoring.md` (macOS device health, missing-machine audit,
> software expirations).
>
> **macOS-native management note:** For environments using Addigy or
> Watchman Monitoring, chain those singles after Step 4 to extend macOS
> coverage with policy enrollment, missing-machine status, software
> expirations, and 2FA posture — signals the `macos-inspector` alone does
> not surface.
>
> **References:** `reference/asset-fields.md` for the device asset field map.
> `reference/inspector-aliases.md` for OS inspector lookups.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-endpoint-inventory-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  fleet_kpis: "Fleet Composition"
  by_class: "Breakdown by Class (Server / Laptop / Desktop)"
  by_os: "Breakdown by OS Family"
  by_manufacturer: "Hardware Vendor Distribution"
  win11_readiness: "Windows 11 Readiness"
  security_tooling: "Security Tooling Coverage"
  lifecycle: "EOL & Warranty"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 7
  warranty_warn_days: 90
  win10_eol_date: "2025-10-14"
  edr_coverage_pct_min: 95

inspectors_in_scope:
  - windows-server-inspector
  - windows-workstation-inspector
  - macos-inspector
  - linux-inspector

reporting_period: { default: "current_state" }
```

---

## When to use

- Fleet inventory at onboarding
- Quarterly composition review (vendor refresh planning)
- "How many laptops vs. desktops do we manage?"
- "Win11 readiness across the fleet"
- "Where's our hardware coming from? Vendor consolidation candidate?"

Personas: NOC, vCIO/AM, TAM, Accounting/Finance (vendor / refresh budgeting).

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |

This recipe is environment-scoped — no per-system input needed.

---

## Workflow

### Step 1 — Device inventory is primary

```
liongard_device LIST environmentId=<ENV_ID> pageSize=200
  fields=["hostname","class","role","operatingSystem","osVersion","manufacturer","model",
          "serialNumber","physical","hostServer","status","antivirus","edr","inspectors",
          "warrantyExpiration","winElevenReady","lastSeen","internalIP","environmentId"]

all_devices = result
compute_devices = all_devices where category == "compute"
```

`liongard_device` returns the **reconciled, dedup'd device roster** — one record per
real-world asset, joined across every inspector that observed it (OS, EDR, RMM, AD,
hypervisor). This is the authoritative endpoint count. Per-OS-inspector metric calls
in later steps provide configuration-level detail (patch lists, firewall state, drive
encryption status) that the device record doesn't expose.

> **Cross-system intelligence on every device record:**
> - `status` (`active` / `inactive` / `idle` / `standby`) — synthesized across all
>   reporting inspectors; a device active in the RMM but showing offline in Windows OS
>   gets a reconciled status. Use this for dormancy / activity analysis rather than
>   per-inspector last-seen alone.
> - `edr` — set of confirmed EDR products from **any** reporting system. A device with
>   `edr != null` has confirmed EDR coverage regardless of which inspector surfaced it.
>   A device with `edr == null` AND `inspectors` containing a local OS inspector is a
>   genuine gap.
> - `antivirus` — same cross-system synthesis as `edr`.
> - `inspectors[]` — which Liongard inspectors have observed this device. The coverage
>   gap rule: local OS inspector present + `edr == null` = no EDR. Only AD/RMM present
>   = not locally inspected. See `reference/asset-fields.md` § Coverage gap rule.
> - `physical` (bool) — physical vs. VM, reconciled across OS + hypervisor inspectors.

### Step 2 — Classify the fleet

```
# Class breakdown  (field: class)
servers      = compute_devices where class == "server"
laptops      = compute_devices where class == "laptop"
desktops     = compute_devices where class == "workstation"
unknown      = compute_devices where class is null

# OS family  (field: operatingSystem — lowercase)
windows_server = compute_devices where operatingSystem contains "Windows Server"
windows_client = compute_devices where operatingSystem contains "Windows" AND not contains "Server"
macos          = compute_devices where operatingSystem contains "macOS"
linux          = compute_devices where operatingSystem contains "Linux"

# Physical vs. virtual  (field: physical — boolean)
physical = compute_devices where physical == true
virtual  = compute_devices where physical == false

# Device activity / dormancy  (field: status — cross-system synthesized)
active   = compute_devices where status == "active"
inactive = compute_devices where status == "inactive"
idle     = compute_devices where status == "idle"
# Inactive/idle devices that still appear managed may warrant offboarding review.
```

### Step 3 — Hardware vendor + model rollup

```
# Per manufacturer  (field: manufacturer)
by_manufacturer = compute_devices | group_by manufacturer | count

# Per model (often long-tail)  (field: model)
by_model = compute_devices | group_by model | count

# Models with low count (consolidation candidates)
consolidation_candidates = by_model where count < 5
```

### Step 4 — Windows 11 readiness

```
win10_devices = compute_devices where operatingSystem contains "Windows 10"
win10_compatible    = win10_devices where winElevenReady == "Compatible"
win10_incompatible  = win10_devices where winElevenReady == "Incompatible"
win10_unknown       = win10_devices where winElevenReady in ["Unknown", null]

readiness_pct = length(win10_compatible) / length(win10_devices) * 100
hardware_refresh_count = length(win10_incompatible)
```

### Step 5 — Security tooling coverage

> **Key point:** `antivirus` and `edr` on the device record are **cross-system
> synthesized** — they aggregate confirmed coverage from every inspector that observed
> the device (local OS inspector, RMM, EDR agent, etc.). A device with `edr != null`
> has confirmed EDR from at least one reporting system. This is a stronger signal than
> any single inspector's view. A genuine gap is: `edr == null` AND the device's
> `inspectors[]` includes a local OS inspector (confirming it was locally inspected,
> not just domain-known). See `reference/asset-fields.md` § Coverage gap rule.

```
# AV / EDR coverage  (fields: antivirus, edr — cross-system synthesized sets)
locally_inspected = compute_devices where inspectors contains
  ("windows-workstation-inspector" OR "windows-server-inspector" OR "macos-inspector")

confirmed_av  = locally_inspected where antivirus != null
confirmed_edr = locally_inspected where edr != null
gap_av        = locally_inspected where antivirus == null   # genuine gap — locally confirmed missing
gap_edr       = locally_inspected where edr == null         # genuine gap — locally confirmed missing

# Devices known only via AD (not locally inspected — visibility, not security gap)
ad_only = compute_devices where inspectors contains only ["active-directory-inspector"]
# → edr/antivirus will be null for these, but that's because they haven't been
#   locally inspected, not because EDR is absent. Deploy OS inspector to resolve.

# Inactive / stale devices to include in coverage gap context
inactive_no_edr = gap_edr where status in ["inactive", "idle"]
# Surface separately — these may be decommission candidates, not remediation targets.
```

### Step 6 — Lifecycle / warranty

```
# Out-of-warranty (already past expiration)
out_of_warranty = compute_devices where warrantyExpiration < today

# Warranty expiring within SLA
expiring_soon = compute_devices where today < warrantyExpiration < (today + slas.warranty_warn_days days)

# Warranty unknown (gap)
warranty_unknown = compute_devices where warrantyExpiration is null
```

### Step 7 — Per-OS-inspector cross-check

For each OS inspector deployed, run a count and verify the asset-inventory
totals match. Divergence is a data-quality flag.

```
for each OS inspector in inspectors_in_scope:
  inspector_systems_count = count(systems with this inspector)
  asset_count_for_os      = length(compute_devices where inspectors contains <inspector slug>)
  if inspector_systems_count != asset_count_for_os:
    flag as data quality issue
```

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Hardware refresh roadmap | win10_incompatible > 0 | "<N> Win10 devices need hardware replacement before <Win10 EOL>." |
| Vendor consolidation candidate | many low-count models | "<N> models with <5 devices each — opportunity to standardize." |
| EDR coverage gap | confirmed_edr / locally_inspected < SLA | "<N> locally-inspected devices have no EDR — install." |
| Visibility gap (AD-only) | ad_only > 0 | "<N> devices known only via AD — deploy OS inspector for posture data." |
| Out-of-warranty fleet | out_of_warranty / total > X% | "<pct>% of devices out of warranty — refresh schedule needed." |
| Warranty unknown | warranty_unknown > X | "<N> devices have no warranty data — populate via SMBIOS or RMM." |
| Linux gap | Linux inspectors deployed but (not in dataprint) metrics missing | "Linux posture limited — file metric requests for Linux: IP, Domain, RMM agent service status." |
| Inactive devices with no EDR | inactive_no_edr > 0 | "<N> inactive devices have no EDR — confirm decommission or remediate before reactivation." |
| Stale inspector | lastSeen > 7d on any system | "<N> inspectors haven't reported recently." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Linux IP / domain / RMM coverage | ⚠️ not in dataprint metrics | Manual SSH check or RMM cross-reference |
| Site / location per device | ⚠️ partial | RMM tag, MDM, manual |
| Asset tag (MSP-internal) | ⚠️ partial | RMM custom field |
| Decommission status | ⚠️ partial | RMM lifecycle tag |
| RAID / disk health | ❌ | RMM, vendor (iDRAC, iLO) |

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | Steps 2–4 answer all managed-endpoint inventory questions (class, OS, hardware vendor, virtualization). macOS MDM enrollment and missing-machine status require chaining `addigy.md` + `watchman-monitoring.md` (Step 4 extension). |
| CIS Controls (v8.1) | ✅ | CIS 1.1/1.2 (Steps 2–4 — full device inventory across all OS), 2.1/2.2 (Step 4 — OS version inventory, EOL exposure), 7.3/7.4 (Steps 4 + Windows-patching rollup — patch posture by OS), 10.1 (Step 5 — EDR/AV coverage gap analysis), 3.6/3.11 (Step 6 — lifecycle + warranty as hardware-refresh trigger). |
| Cyber-insurance domain files | ✅ | This rollup is the cross-OS evidence source for `domains/endpoint.md` device-count and OS-coverage questions. Pair with `all-edrs.md` for AV/EDR evidence and `all-windows-patching.md` for patch-posture evidence. |
| QBR / quarterly-business-review | ✅ | QBR Step 6 chains this for fleet composition (total devices, OS breakdown, hardware vendor), Win11 readiness, EDR coverage gap, and EOL/warranty summary. |

---

## Output format

Markdown / Word / PowerPoint / Excel per `output.format`. **xlsx** is the
canonical fleet-inventory deliverable (one row per device; sortable). Use
**pptx** for the executive overview (KPI dashboard slide + composition charts).

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_device LIST | envId=<ENV_ID> pageSize=200 fields=[...] | array<device> | ok |
| 3 | liongard_system LIST | envId=<ENV_ID> | array<system> | ok |
| 4 | per OS inspector: liongard_metric EVALUATE | jmesPath sysId=<SYS_ID> envId=<ENV_ID> | varies | ok |
```

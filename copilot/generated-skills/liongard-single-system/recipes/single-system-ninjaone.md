---
name: single-system-ninjaone
description: >
  Use this skill when the user wants a single-system analysis of a
  NinjaOne RMM tenant — agent coverage, device health, patch posture,
  antivirus and encryption posture, installed software and Windows
  services, hardware and activity, alert volume, technician MFA.
  Trigger phrases: "NinjaOne review", "Ninja RMM report", "NinjaRMM
  posture for <customer>" (legacy name), "Ninja agent coverage",
  "Ninja patch posture", "NinjaOne alert audit", "Ninja technician
  MFA", "Ninja license utilization".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_launchpoint, liongard_metric, liongard_device"
personas: [noc, technical-alignment-manager, vcio-account-manager, accounting-finance]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  - metrics:ninjaone:alerts-open-count
  - metrics:ninjaone:av-definitions-outdated-count
  - metrics:ninjaone:av-not-protected-count
  - metrics:ninjaone:devices-agent-count
  - metrics:ninjaone:devices-failed-os-patches-count
  - metrics:ninjaone:devices-failed-software-patches-count
  - metrics:ninjaone:devices-low-disk-count
  - metrics:ninjaone:devices-needs-attention-count
  - metrics:ninjaone:devices-not-updated-14d-count
  - metrics:ninjaone:devices-offline-count
  - metrics:ninjaone:devices-offline-list
  - metrics:ninjaone:devices-online-count
  - metrics:ninjaone:devices-pending-reboot-count
  - metrics:ninjaone:devices-server-count
  - metrics:ninjaone:devices-total-count
  - metrics:ninjaone:devices-unhealthy-count
  - metrics:ninjaone:devices-windows10-count
  - metrics:ninjaone:disks-not-ok-count
  - metrics:ninjaone:organizations-count
  - metrics:ninjaone:patches-critical-pending-count
  - metrics:ninjaone:patches-failed-count
  - metrics:ninjaone:patches-pending-count
  - metrics:ninjaone:services-auto-start-stopped-count
  - metrics:ninjaone:software-inventory-count
  - metrics:ninjaone:threats-active-count
  - metrics:ninjaone:users-mfa-enabled-count
  - metrics:ninjaone:users-privileged-count
  - metrics:ninjaone:users-technician-count
  - metrics:ninjaone:users-without-mfa-count
  - metrics:ninjaone:users-without-mfa-list
  - metrics:ninjaone:volumes-bitlocker-unprotected-count
---

# Single-System Analysis — NinjaOne

> **Inspector:** `ninjaone-inspector` (ID 72). Apps & Services
> category. Renamed from NinjaRMM in 2022 — both names accepted.
>
> **Parent/child: yes.** The **parent** system holds the tenant roster
> (organizations, groups, policies, roles, **technicians**). Each
> **child** system is one NinjaOne organization and holds the devices
> and all device telemetry. A full review reads **both**: the child for
> Steps 4–9 and the parent for Step 10.
>
> **References:** `reference/inspector-aliases.md` (Ninja, NinjaOne,
> NinjaRMM). Pairs with `reference/asset-fields.md` for the
> reconciled device inventory; cross-reference with EDR / OS
> inspectors via the `inspectors[]` array on devices. Rolls up into
> `recipes/system-type-assessment/all-rmm-platforms.md` and
> `recipes/system-type-assessment/all-windows-patching.md`.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-ninjaone-review-<period>.<ext>"
  # brand: inherits from `references/msp-config.yaml` — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  agent_coverage: "Agent Coverage & Device Health"
  patch_posture: "Patch Posture"
  antivirus_posture: "Antivirus, Threat & Encryption Posture"
  software_inventory: "Software & Services"
  hardware_activity: "Hardware & Activity"
  alert_posture: "Alert Activity"
  technician_usage: "Technician Access"
  licensing: "License Utilization (manual)"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  agent_coverage_pct_min: 95             # NinjaOne devices / asset-inventory compute devices
  agent_not_updated_days_max: 14          # matches the stored "not updated in 14 days" metric
  critical_patches_pending_max: 0
  failed_patches_max: 0
  unresolved_alerts_max: 0
  antivirus_coverage_pct_min: 95
  technician_mfa_pct_min: 100
  low_disk_free_pct_min: 20

reporting_period: { default: "current_state" }

qa:
  retry_on_null: true
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: false
  manual_verification_section_required: true
```

---

## When to use

- "NinjaOne posture for <customer>"
- "Ninja agent coverage check"
- "Ninja patch posture review"
- "Which technicians don't have MFA in NinjaOne?"
- "NinjaRMM report" (legacy)

Cadence: monthly per customer; quarterly in PBR; ad-hoc post-incident.

Personas:
- **NOC** (primary — device health, patching, offline agents)
- **TAM** (policy / patch-cadence drift, services, encryption)
- **vCIO / Account Manager** (renewal narrative, hardware refresh signals)
- **Accounting / Finance** (managed-device count for seat reconciliation)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Child system ID (the customer's NinjaOne organization) | Yes | `liongard_launchpoint LIST inspectorId=72` (Step 1) |
| Parent system ID (the NinjaOne tenant) | For Step 10 | The child launchpoint's `parentID` → that launchpoint's `system.id` |

---

## Liongard data sources

> **Asset inventory first, metric cross-check.** NinjaOne is the
> per-vendor source of truth for *device health, patching, AV state and
> technician access*. The reconciled asset inventory is the source of
> truth for *coverage* — which compute devices Liongard knows exist and
> which of them NinjaOne manages.

### Parent dataprint (tenant roster)

| Key | Description |
|---|---|
| `Organizations[]` | NinjaOne organizations: `id`, `name`, `nodeApprovalMode` |
| `Users[]` | Console users — `userType == 'TECHNICIAN'`, `enabled`, `administrator`, `mfaConfigured`, `invitationStatus` |
| `Groups[]` | Saved device groups with `deviceCount` (e.g., "Doesn't have AV protection on (any)") |
| `Policies[]` / `Roles[]` | Policy and role catalog (`nodeClass`) |
| `Discovered[]` | One row per organization that can become a child system (`Inspector: 'ninja-rmm-inspector'`) |

### Child dataprint (one organization)

Every child has: `Name`, `SystemInfo`, `Users`, `Devices`, `DiskSummary`,
`AntiVirusSummary` (the **lean** shape). Children collected with the
2026 telemetry also carry the **expanded** keys:

| Key | Description |
|---|---|
| `Devices[]` | Per device: `systemName`, `nodeClass`, `offline`, `os{}`, `system{}`, `volumes[]`, `LastContact_r`, `DaysSinceLastUpdated_r`, `DeviceHealth_r{}` |
| `Devices[].DeviceHealth_r` | Per-device rollup: `healthStatus`, `alertCount`, pending / failed OS + software patch counts, active / quarantined / blocked threat counts, vulnerability counts |
| `AntiVirusSummary[]` | `productName` (`'NONE'` = no AV), `productState`, `definitionStatus`, `DeviceName_r` |
| `DiskSummary[]` | Physical disks: `model`, `status`, `Size_r`, `smartCapable` |
| `SystemInfo` | Organization record: `name`, `locations[]`, `policies[]`, feature flags (`backup`, `psa`, `splashtop`, `trayicon`) |
| `PatchStatus[]` *(expanded)* | Outstanding patches: `name`, `kbNumber`, `severity`, `status`, `type`, `PatchKind_r` (`OS` / `SOFTWARE`), `DeviceName_r` |
| `OsPatchInstallHistory[]` *(expanded)* | Installed OS patches: `name`, `kbNumber`, `status`, `InstalledTime_r` — **very large** (tens of thousands of rows) |
| `SoftwarePatchInstallHistory[]` *(expanded)* | Third-party patch history (empty on the test systems) |
| `SoftwareInventory[]` *(expanded)* | Installed software, one row per title per device: `name`, `publisher`, `version`, `installDate`, `DeviceName_r` |
| `WindowsServices[]` *(expanded)* | `name`, `displayName`, `startType`, `state`, `userName`, `DeviceName_r` |
| `Volumes[]` *(expanded)* | Per volume incl. `bitLockerStatus.protectionStatus` |
| `ComputerSystem[]`, `Processors[]`, `OperatingSystems[]`, `NetworkInterfaces[]`, `RaidControllers[]`, `RaidDrives[]` *(expanded)* | Hardware detail per device |
| `UserSession[]` *(expanded)* | Last logged-on user per device: `userName`, `LogonTime_r` |
| `BackupUsage[]`, `PolicyOverrides[]` *(expanded)* | Present but empty on the test systems |

There is **no `Alerts[]`, `Licensing`, or activity-log key** on any
shape (see Data gaps).

---

## Workflow

### Step 1 — Resolve environment, child and parent

```
liongard_environment LIST searchMode=keyword query="<customer>"

liongard_launchpoint LIST inspectorId=72 environmentIds=[<ENV_ID>]
  fields=["id","friendlyName","status","parentID","system.id","environment.id","latestInspectionDate"]
```

- A row with a non-null `parentID` is a **child**. Its parent is the
  launchpoint whose `id` equals that `parentID` — run
  `liongard_launchpoint GET id=<parentID>` to get the parent's
  `system.id` and `environment.id` (the parent usually lives in the
  MSP's own environment, not the customer's).
- **Confirm by shape, not by name.** Launchpoint names are free text; a
  system named "child" can be a parent. Run Step 3 on each candidate.

### Step 2 — Inspector freshness

Use the `inspectionHealth` block on each launchpoint row from Step 1
(`assessment`, `latestInspectionDate`, `daysSinceLastInspection`). It is
the only source of inspection recency. Flag `overdue`, `faulted`,
`disabled` or `paused` in the QA pass. Never use device `lastSeen` as an
inspection date.

### Step 3 — Detect role and shape

```
liongard_metric EVALUATE systemId=<SYS_ID> environmentId=<ENV_ID> jmesPathQuery="keys(@)"
```

| Keys returned | Meaning | Action |
|---|---|---|
| `Organizations`, `Groups`, `Policies`, `Roles`, `Users`, `Discovered`, `Name` | **Parent** | Use for Step 10 only |
| `Name`, `Users`, `Devices`, `SystemInfo`, `DiskSummary`, `AntiVirusSummary` | **Lean child** | Run Steps 4–6, 8 (from `Devices[]`), 9; skip expanded-only primitives and record them as "not collected" |
| Lean keys + `PatchStatus`, `SoftwareInventory`, `WindowsServices`, `Volumes`, … | **Expanded child** | Run every step |

> **Field gotcha — absent keys fail the query.** `length(PatchStatus)`
> on a lean child raises `length() expected argument 1 to be type
> string,array,object but received type null`. That is "not collected on
> this shape", not a transient error and not zero. Do not retry it, and
> do not wrap it in ``PatchStatus || `[]` `` (that reports a false 0).

### Step 4 — Agent coverage and device health (child)

```
liongard_metric EVALUATE systemId=<CHILD_SYS_ID> environmentId=<ENV_ID> jmesPathQuery="<primitive jmesPath>"
```

| Primitive | Query | Status |
|---|---|---|
| `devices-agent-count` | `length(Devices[?deviceType == 'AgentDevice'])` | VALIDATED |
| `devices-total-count` | `length(Devices)` | VALIDATED |
| `devices-online-count` | ``length(Devices[?offline == `false`])`` | VALIDATED |
| `devices-offline-count` / `devices-offline-list` | ``Devices[?offline == `true`].{name: systemName, lastContact: LastContact_r, nodeClass: nodeClass}`` | VALIDATED |
| `devices-server-count` | `length(Devices[?contains(nodeClass, 'SERVER')])` | VALIDATED |
| `devices-not-updated-14d-count` (stored metric 1089) | ``Devices[?DaysSinceLastUpdated_r > `14`] \| length(@)`` | VALIDATED |
| `devices-unhealthy-count` (stored metric 1091) | ``Devices[?DeviceHealth_r.healthStatus == `UNHEALTHY`] \| length(@)`` | VALIDATED |
| `devices-needs-attention-count` (stored metric 1093) | ``Devices[?DeviceHealth_r.healthStatus == `NEEDS_ATTENTION`] \| length(@)`` | VALIDATED |
| `devices-pending-reboot-count` | ``length(Devices[?os.needsReboot == `true`])`` | VALIDATED |
| `devices-low-disk-count` (stored metric 1099) | ``Devices[?volumes[?PercentageFree_r < `20` && PercentageFree_r != `null`]] \| length(@)`` | VALIDATED |
| `disks-not-ok-count` (stored metric 1101) | ``DiskSummary[?status != `OK`] \| length(@)`` | VALIDATED |
| `devices-windows10-count` | `length(Devices[?contains(os.name \|\| '', 'Windows 10')])` | VALIDATED |

> **Field gotcha — VM records are counted twice.** When NinjaOne monitors
> an ESXi host, every VM appears as a `deviceType: 'VMGuest'` record, and
> again as an `AgentDevice` if it also runs the agent. `devices-total-count`
> therefore overstates the fleet (29 records for 24 unique hosts on one
> test system). Report `devices-agent-count` as "managed endpoints", and
> list `VMHost` / `VMGuest` records separately. `os.name` is null on those
> records, which is why the Windows 10 query needs the `|| ''` guard.

When a primitive has a stored metric ID, call `liongard_metric EVALUATE
metricId=<id>` first. If it returns no data rows (the metric is not
cached on this instance — observed on the test tenant), evaluate the
listed query instead.

#### Coverage gap — asset inventory vs NinjaOne

Pull the environment's reconciled inventory once (page until
`CountBasis.isCompletePopulation` is true):

```
liongard_device LIST environmentId=<ENV_ID> pageSize=200
  fields=["hostname","category","operatingSystem","inspectors","lastSeen"]
```

Then filter client-side:

```jmespath
# 0. Pre-check: is this child reconciled into the inventory at all?
length(items[?inspectors[?name == 'ninja-rmm-inspector' && systemID == `<CHILD_SYS_ID>`]])

# 1. Missing from NinjaOne: real compute devices with no NinjaOne source
items[?category == 'compute' && operatingSystem != null && !inspectors[?name == 'ninja-rmm-inspector']].{host: hostname, os: operatingSystem, seenBy: inspectors[].alias}

# 2. NinjaOne-only: devices no other source (directory, M365, EDR) knows about
items[?inspectors[?name == 'ninja-rmm-inspector'] && length(inspectors) == `1`].{host: hostname, os: operatingSystem}
```

| Output | Meaning | Recommendation row |
|---|---|---|
| Pre-check = 0 | The child's devices are not in the asset inventory. Coverage cannot be computed. | "NinjaOne devices for this organization are not reconciled into Liongard's asset inventory. Confirm the NinjaOne system is mapped to this environment." (Report it in the QA section; skip lists 1 and 2.) |
| List 1 | Devices Liongard sees (via AD, M365, EDR, network) that NinjaOne does not manage | "Deploy the NinjaOne agent to <N> devices, or confirm they are retired / out of scope." |
| List 2 | Devices only NinjaOne knows about: not in the directory, M365 or any EDR | "Confirm <N> NinjaOne-only devices are company assets; join them to the directory and confirm EDR coverage." |

Coverage % = `devices-agent-count` ÷ (`devices-agent-count` + count of
list 1). Compare it with `slas.agent_coverage_pct_min`.

> **Field gotcha — runtime inspector name.** On asset-inventory rows the
> NinjaOne source appears as `name: 'ninja-rmm-inspector'`, alias
> `'NinjaOne'` — **not** `ninjaone-inspector`. A filter on
> `ninjaone-inspector` matches nothing.
>
> **Field gotcha — directory objects without an OS.** AD service and SSO
> computer accounts (e.g. the Azure AD SSO account and gMSA objects) are
> `category: 'compute'` with `operatingSystem: null`. The
> `operatingSystem != null` filter keeps them out of list 1.
>
> **Field gotcha — other NinjaOne systems in the environment.** An
> environment can hold devices from more than one NinjaOne system. Use
> the `systemID` in the pre-check to confirm the rows belong to the child
> being reviewed.

Anonymized sample, from a test environment with 72 inventory devices
(71 compute):

| Result | Count | Composition |
|---|---:|---|
| Pre-check | 58 | Child is reconciled (matches `devices-agent-count`) |
| List 1 — missing from NinjaOne | 11 | 10 workstations/laptops known to AD + M365; 1 laptop known only to M365 (2 OS-less directory objects excluded) |
| List 2 — NinjaOne-only | 0 | Every NinjaOne device is also known to AD |
| Coverage | 84% | 58 ÷ 69 — below a 95% SLA |

> **Field gotcha — OS name strings differ by shape.** Lean children
> report `os.name` as `"Microsoft Windows 11 Pro"`; expanded children
> report `"Windows 11 Professional Edition"`. Use
> `contains(os.name, 'Windows 11')`, never equality. For Windows 10 EOL
> counting use `contains(os.name, 'Windows 10')`.

### Step 5 — Patch posture (child)

| Primitive | Query | Shape | Status |
|---|---|---|---|
| `patches-pending-count` | `sum(Devices[].[DeviceHealth_r.pendingOSPatchesCount, DeviceHealth_r.pendingSoftwarePatchesCount][])` | lean + expanded | VALIDATED |
| `patches-failed-count` | `sum(Devices[].[DeviceHealth_r.failedOSPatchesCount, DeviceHealth_r.failedSoftwarePatchesCount][])` | lean + expanded | VALIDATED |
| `devices-failed-os-patches-count` (stored 1095) | ``Devices[?DeviceHealth_r.failedOSPatchesCount > `0` && systemName].systemName \| length(@)`` | lean + expanded | VALIDATED |
| `devices-failed-software-patches-count` (stored 1097) | ``Devices[?DeviceHealth_r.failedSoftwarePatchesCount > `0` && systemName] \| length(@)`` | lean + expanded | VALIDATED |
| `patches-critical-pending-count` | `length(PatchStatus[?(severity == 'CRITICAL' \|\| severity == 'IMPORTANT') && status != 'REJECTED'])` | expanded | VALIDATED |

Supporting detail (expanded only, not registered):

```jmespath
# Outstanding important/critical patches, per device
PatchStatus[?(severity == 'CRITICAL' || severity == 'IMPORTANT') && status != 'REJECTED'].{device: DeviceName_r, kb: kbNumber, name: name, status: status, kind: PatchKind_r}

# OS patches installed since a date (substitute today − 30 days, ISO 8601)
length(OsPatchInstallHistory[?InstalledTime_r >= '<YYYY-MM-DD>'])
```

> **Field gotcha — PatchStatus severity.** Observed values: `IMPORTANT`,
> `MODERATE`, `OPTIONAL`, `NONE`, and `null` on most third-party
> (`PatchKind_r == 'SOFTWARE'`) rows — 271 of 390 rows on one test
> system. `CRITICAL` never appeared in test data but stays in the
> filter. Third-party patches therefore rarely show up in the
> critical/important count; report `PatchKind_r == 'SOFTWARE'` rows
> separately when they matter.
>
> **Field gotcha — PatchStatus status.** `APPROVED`, `DELAYED`, `MANUAL`
> (awaiting approval) and `REJECTED` (policy-excluded). Exclude
> `REJECTED` from "pending".
>
> **Large array.** `OsPatchInstallHistory` reached 23,300 rows on a
> 29-device organization. Only ever use `length()` or a filtered
> projection — never pull it whole.

### Step 6 — Antivirus, threat and encryption posture (child)

| Primitive | Query | Shape | Status |
|---|---|---|---|
| `av-not-protected-count` | `length(AntiVirusSummary[?productName == 'NONE' \|\| productState != 'ON'])` | lean + expanded | VALIDATED |
| `av-definitions-outdated-count` | `length(AntiVirusSummary[?productName != 'NONE' && definitionStatus != 'Up-to-Date'])` | lean + expanded | VALIDATED |
| `threats-active-count` | `sum(Devices[].DeviceHealth_r.activeThreatsCount)` | lean + expanded | VALIDATED |
| `volumes-bitlocker-unprotected-count` | `length(Volumes[?bitLockerStatus.protectionStatus == 'UNPROTECTED'])` | expanded | VALIDATED |

Supporting detail:

```jmespath
# AV product mix (third-party AV is reported here too, e.g. SentinelOne, Windows Defender)
AntiVirusSummary[].{device: DeviceName_r, product: productName, state: productState, defs: definitionStatus}
```

> **Field gotcha — devices with no AV row.** `AntiVirusSummary` had 22
> rows for 29 devices on one test system. Compare
> `length(AntiVirusSummary)` with `length(Devices)`; the difference is
> devices NinjaOne reports no AV state for (often hypervisor hosts and
> Linux). Flag them for manual review rather than counting them as
> protected.

### Step 7 — Software and services (expanded child only)

| Primitive | Query | Status |
|---|---|---|
| `software-inventory-count` | `length(SoftwareInventory)` | VALIDATED |
| `services-auto-start-stopped-count` | `length(WindowsServices[?(startType == 'AUTO_START' \|\| startType == 'AUTO_START_DELAYED') && state == 'STOPPED'])` | VALIDATED |

Supporting detail (substitute a title or publisher; never pull the full
array on large organizations):

```jmespath
SoftwareInventory[?contains(name, '<title>')].{device: DeviceName_r, name: name, version: version, installed: installDate}
WindowsServices[?(startType == 'AUTO_START' || startType == 'AUTO_START_DELAYED') && state == 'STOPPED'].{device: DeviceName_r, service: displayName}
```

> **Field gotcha — software rows are per device.** 2,542 rows covered 22
> devices on one test system. JMESPath has no distinct, so there is no
> unique-title count; group client-side if the report needs one.
>
> **Field gotcha — WindowsServices cap.** One test system returned
> exactly 1,000 rows, which suggests a collection cap. On large
> organizations treat service counts as a floor. Many delayed-start and
> trigger-start services stop normally; review names before calling a
> stopped service a failure.

### Step 8 — Hardware and activity (child)

```jmespath
# Lean and expanded: hardware from the device record
Devices[].{name: systemName, class: nodeClass, mfr: system.manufacturer, model: system.model, serial: system.serialNumber, vm: system.virtualMachine, chassis: system.chassisType, os: os.name}

# Activity: last contact and last-updated age
Devices[].{name: systemName, lastContact: LastContact_r, daysSinceUpdate: DaysSinceLastUpdated_r}

# Expanded only: last logged-on user per device
UserSession[].{device: DeviceName_r, user: userName, logon: LogonTime_r}
```

> **Field gotcha — epoch units differ.** `Devices[].lastContact` is
> epoch **seconds** (a float); `UserSession[].logonTime` is epoch
> **milliseconds**. Always use the `_r` ISO fields (`LastContact_r`,
> `LogonTime_r`) in reports.

Warranty and purchase dates are not in the NinjaOne dataprint — take
them from `liongard_device` (`warrantyExpiration`, `purchaseDate`) when a
hardware vendor inspector supplies them.

### Step 9 — Alert activity (child)

| Primitive | Query | Status |
|---|---|---|
| `alerts-open-count` | `sum(Devices[].DeviceHealth_r.alertCount)` | VALIDATED |

Per-device breakdown:

```jmespath
Devices[?DeviceHealth_r.alertCount > `0`].{name: systemName, alerts: DeviceHealth_r.alertCount, health: DeviceHealth_r.healthStatus}
```

Alert severity, age, and condition/policy name are **not** collected
(no `Alerts[]` array) — see Data gaps.

### Step 10 — Technician access and tenant roster (parent)

Run these against the **parent** system from Step 1.

> **Check the parent first.** A parent launchpoint with
> `inspectionHealth.assessment` of `faulted` (typically *Setup Issue* —
> expired API credentials) can return an empty dataprint: `keys(@)`
> returns `[]`. Then skip this step, report "technician access not
> available — parent inspection failing" in the Data gaps and QA
> sections, and recommend fixing the parent credentials. Child data is
> unaffected, because children are inspected separately.

| Primitive | Query | Status |
|---|---|---|
| `users-technician-count` | `length(Users[?userType == 'TECHNICIAN'])` | VALIDATED |
| `users-mfa-enabled-count` | ``length(Users[?userType == 'TECHNICIAN' && mfaConfigured == `true`])`` | VALIDATED |
| `users-without-mfa-count` (stored 1077) | ``Users[?enabled == `true` && mfaConfigured == `false`] \| length(@)`` | VALIDATED |
| `users-without-mfa-list` (stored 1076) | ``Users[?enabled == `true` && mfaConfigured == `false`].[firstName, lastName]`` | VALIDATED |
| `users-privileged-count` (stored 1079) | ``Users[?enabled == `true` && administrator == `true`] \| length(@)`` | VALIDATED |
| `organizations-count` | `length(Organizations)` | VALIDATED |

> **Field gotcha — child `Users[]` is not technicians.** Child
> dataprints have a `Users[]` array of `END_USER` contacts (or it is
> empty). Running the technician primitives on a child returns the wrong
> population. The pre-2026-10 version of `users-technician-count`
> (`length(Users)`) had this bug.
>
> **Field gotcha — expired invitations.** Accounts with
> `invitationStatus == 'EXPIRED'` are still `enabled == true` and show up
> as "without MFA". List them separately: they are cleanup candidates,
> not active technicians skipping MFA.

The parent's `Groups[]` also carries useful NinjaOne-computed counts
(tenant-wide, not per organization):

```jmespath
Groups[?starts_with(name, 'Doesn')].{group: name, devices: deviceCount}
```

### Step 11 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on:
1. **Retry persistent nulls** — but not the absent-key failure from
   Step 3; record that as "not collected on this shape".
2. **Stale inspector flag** — from `inspectionHealth`. A child can be
   overdue while its parent is current; flag each separately.
3. **Cross-tool divergence** — `devices-agent-count` vs the Step 4
   pre-check count (inventory rows with this child's `systemID`); and AV
   product per device vs the asset inventory `antivirus` / `edr` fields.
   Never compare against `devices-total-count`, which includes VM-guest records.
4. **Data gaps** — licensing, alert severity/age, oldest-pending-patch
   age (below).
5. **Single-source visibility** — devices whose only source in
   `inspectors[]` is `ninja-rmm-inspector` have no EDR / OS-inspector
   confirmation.

### Step 12 — Render

Sections in the order of the customization block. Executive Summary
KPIs: coverage %, offline + not-updated devices, critical/important
pending patches, failed patches, devices without active AV, open
alerts, technicians without MFA.

---

## Insights & recommendations

| Pattern | Trigger | Recommendation template |
|---|---|---|
| Agent coverage below SLA | coverage % < `slas.agent_coverage_pct_min` (Step 4 list 1) | "Deploy the NinjaOne agent to <N> devices Liongard sees but NinjaOne does not manage, or confirm they are retired." |
| NinjaOne-only devices | Step 4 list 2 non-empty | "<N> devices are known only to NinjaOne. Confirm they are company assets; join them to the directory and confirm EDR." |
| Inventory not reconciled | Step 4 pre-check = 0 | "This organization's NinjaOne devices are not in the Liongard asset inventory. Check the system-to-environment mapping." |
| Windows 10 still in use | `devices-windows10-count` > 0 | "<N> devices run Windows 10, which is past end of support. Plan upgrade or replacement." |
| Parent inspection failing | parent `inspectionHealth.assessment` = `faulted` | "Fix the NinjaOne parent credentials so technician access and MFA can be reviewed." |
| Stale agents | `devices-not-updated-14d-count` > 0 or `devices-offline-count` > 0 | "<N> devices have not checked in for 14+ days. Triage: reinstall agent, fix network, or retire the device." |
| Unhealthy devices | `devices-unhealthy-count` > 0 | "<N> devices are rated Unhealthy in NinjaOne. Review the device dashboard for the failing condition." |
| Critical/important patches pending | `patches-critical-pending-count` > `slas.critical_patches_pending_max` | "Approve and deploy <N> important/critical patches; <N> are DELAYED by policy." |
| Patch failures | `patches-failed-count` > `slas.failed_patches_max` | "Investigate patch-install failures on <N> devices. Re-attempt or escalate." |
| Reboot backlog | `devices-pending-reboot-count` > 0 | "<N> devices need a reboot to finish patching. Schedule a maintenance window." |
| AV gap | `av-not-protected-count` > 0, or AV rows < device rows | "Enable antivirus (NinjaOne-managed or third-party) on <N> devices; confirm <N> devices with no AV record." |
| Outdated AV definitions | `av-definitions-outdated-count` > 0 | "Force a definition update on <N> devices." |
| Unencrypted volumes | `volumes-bitlocker-unprotected-count` > 0 | "Enable BitLocker on <N> volumes (prioritize laptops and OS drives)." |
| Low disk | `devices-low-disk-count` > 0 | "<N> devices have a volume below 20% free. Clean up or expand storage." |
| Disk health | `disks-not-ok-count` > 0 | "Replace or investigate <N> physical disks not reporting OK." |
| Stopped automatic services | `services-auto-start-stopped-count` > 0 (after review) | "<N> automatic services are stopped, including <names>. Confirm intended state." |
| Unresolved alerts | `alerts-open-count` > `slas.unresolved_alerts_max` | "<N> open NinjaOne alerts across <N> devices. Triage the backlog." |
| Technician without MFA | `users-without-mfa-count` > 0 | "Enforce MFA on <N> technician accounts; remove <N> expired invitations." |
| Excess administrators | `users-privileged-count` close to `users-technician-count` | "<N> of <N> technicians are administrators. Apply least privilege with NinjaOne roles." |
| Unauthorized software | customer list match in `SoftwareInventory[]` | "<N> installs of <software> detected. Confirm policy; remove if unauthorized." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| License seat total / used / renewal date | **Not in dataprint** (no `Licensing` object on any shape, re-checked 2026-10-21) | NinjaOne console → Administration → Billing; reconcile seat count against `devices-total-count` |
| Alert severity, age, condition / policy name | **Not in dataprint** (no `Alerts[]`; only per-device `alertCount`) | NinjaOne console → Alerts |
| Oldest pending patch age | **Not derivable** — `PatchStatus[].Timestamp_r` is the last status time, not the release date | NinjaOne console → Patching |
| Unique software title count | Not derivable in JMESPath | Group `SoftwareInventory[]` client-side |
| Expanded telemetry (software, services, patch detail, BitLocker) on lean children | **Not collected** on the lean shape | Confirm the organization is being inspected with current inspector settings; NinjaOne console otherwise |
| Third-party patch severity | Mostly `null` | NinjaOne console → Software patching |
| Warranty / purchase dates | Not in dataprint | `liongard_device` (`warrantyExpiration`) from hardware vendor inspectors |
| Backup usage | `BackupUsage[]` empty on test systems | NinjaOne Backup console |
| Script-execution audit log, remote-control session history | Not in dataprint | NinjaOne console → Activities |
| Ticket / PSA integration health | Partial (`SystemInfo.psa.enabled` only) | NinjaOne ↔ PSA console |

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ⚠️ | NinjaOne is an RMM, not an EDR. The six standard endpoint questions map to: total devices managed (`devices-total-count`), active (`devices-online-count` − `devices-not-updated-14d-count`), inactive (`devices-offline-list`), not covered (asset-inventory cross-check), server vs workstation split (`devices-server-count`), open alerts (`alerts-open-count`). The matrix has no RMM row yet. |
| CIS Controls (v8.1) | ✅ | CIS 1.1 (asset inventory), 2.1 (software inventory), 3.6 (encryption on end-user devices), 5.4 (restrict admin privileges), 6.5 (MFA for administrative access), 7.3 / 7.4 (OS and application patching), 10.1 / 10.2 (anti-malware deployed and updated). See `recipes/compliance/cyber-insurance/domains/endpoint.md`. |
| Cyber-insurance domain files | ✅ | `domains/endpoint.md` patch currency (Q8–Q11) and AV coverage (Q1, Q12); `domains/governance.md` / `domains/auth.md` for technician MFA. |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this when NinjaOne is the customer's RMM: coverage %, critical/important patches pending, devices without AV, open alerts, technician MFA. License utilization is a manual item. |

---

## Output format

- **Markdown** (default) — sections in customization order, one KPI table per section.
- **Word** — see `templates/output-block-word.md`. KPI table in the Executive Summary; patch and AV detail as wide tables.
- **PowerPoint** — see `templates/output-block-pptx.md`. Cover → KPI dashboard → coverage donut → patch bar (pending / failed / important) → AV and encryption → technician MFA → recommendations.
- **Excel** — one sheet per detail query (offline devices, outstanding patches, AV per device, stopped services, technicians without MFA).

---

## Verification log

Validation run 2026-10-21 against a dev environment. Systems A–C are
children (A = lean shape, B and C = expanded shape); D, E and F are
parents (F's dataprint was empty). Results are recorded as shapes only.

| Path / Query | Systems | Result shape | Status |
|---|---|---|---|
| `liongard_launchpoint LIST inspectorId=72` | dev environment | array<launchpoint>; children carry non-null `parentID` | VALIDATED |
| `inspectionHealth` | A–F | object (`assessment`: on_schedule / overdue / faulted) | VALIDATED |
| `keys(@)` | D, E | array<string> — 7 roster keys | VALIDATED |
| `keys(@)` | F (parent, faulted) | empty array | SCHEMA_CONFIRMED (empty dataprint) |
| `keys(@)` | A / B / C | array<string> — 6 / 21 / 13 keys | VALIDATED |
| `length(Devices)` | A, B, C | integer | VALIDATED |
| `length(Devices[?deviceType == 'AgentDevice'])` | A, B, C | integer (< `length(Devices)` on C: VMHost / VMGuest records) | VALIDATED |
| ``Devices[?offline == `true`].{…}`` | A, B, C | array<object{name, lastContact, nodeClass}> | VALIDATED |
| `length(Devices[?contains(nodeClass, 'SERVER')])` | A, B, C | integer | VALIDATED |
| `length(Devices[?contains(os.name, 'Windows 10')])` | C | error: `contains()` received null (VMGuest `os.name`) | fixed with `\|\| ''` guard |
| `length(Devices[?contains(os.name \|\| '', 'Windows 10')])` | A, B, C | integer | VALIDATED |
| stored-metric queries 1089 / 1091 / 1093 / 1095 / 1097 / 1099 / 1101 | A, B, C | integer | VALIDATED |
| `liongard_metric EVALUATE metricId=<id>` | D | empty Data (metric not cached) | query fallback used |
| ``length(Devices[?os.needsReboot == `true`])`` | A, B, C | integer (`needsReboot` boolean) | VALIDATED |
| pending / failed patch sums (`DeviceHealth_r`) | A, B, C | integer | VALIDATED |
| critical/important non-rejected `PatchStatus` | B, C | integer | VALIDATED |
| `length(PatchStatus)` | A | error: `length()` received null (key absent) | SCHEMA_CONFIRMED (lean shape) |
| `PatchStatus[].severity` / `.status` | C | string or null / string | VALIDATED |
| `length(OsPatchInstallHistory[?InstalledTime_r >= '<date>'])` | C | integer | VALIDATED |
| `AntiVirusSummary[]` filters | A, B, C | integer; `productName` string ('NONE' = no AV) | VALIDATED |
| `sum(Devices[].DeviceHealth_r.activeThreatsCount)` | A, B, C | integer | VALIDATED |
| `Volumes[?bitLockerStatus.protectionStatus == 'UNPROTECTED']` | B, C | integer; absent on A | VALIDATED |
| `length(SoftwareInventory)` / `WindowsServices` filters | B, C | integer | VALIDATED |
| `ComputerSystem[]`, `UserSession[]` projections | B, C | array<object> | VALIDATED |
| `sum(Devices[].DeviceHealth_r.alertCount)` | A, B, C | integer | VALIDATED |
| `Users[].userType` | A / D, E | string — END_USER on children, TECHNICIAN on parents | VALIDATED |
| technician / MFA / admin / organization counts | D, E | integer | VALIDATED |
| `Alerts`, `Licensing`, `Activities` | B, D | null | Data gap (not in dataprint) |
| `liongard_device LIST` + Step 4 filters | A's environment | array<device>; pre-check, list 1 and list 2 all evaluated | VALIDATED |
| `inspectors[].name` on device rows | A's environment | string `ninja-rmm-inspector` | VALIDATED |
| End-to-end report run | C + F | rendered HTML; Step 10 skipped (empty parent) | ok |

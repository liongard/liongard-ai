---
name: single-system-nable-rmm
description: >
  Use this recipe when the user wants a single-system analysis of an N-able
  RMM account — site connectivity audit, server and workstation agent coverage,
  OS inventory, agent-version drift, online/offline status, patch posture, and
  agentless-device detection. Trigger phrases: "N-able RMM report for
  <customer>", "N-able site connectivity check", "N-able agent coverage for
  <site>", "N-able patch posture", "N-able RMM review", "N-sight RMM report".
  One system per N-able RMM account; Sites represent managed clients.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_launchpoint, liongard_metric, liongard_timeline"
inspector_id: 87
inspector_name: "N-able RMM"
category: RMM
personas: [noc, technical-alignment-manager, vcio-account-manager, accounting-finance]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  - metrics:nable-rmm:inactive-mobile-devices
  - metrics:nable-rmm:server-count
  - metrics:nable-rmm:server-list
  - metrics:nable-rmm:server-summary
  - metrics:nable-rmm:sites-count
  - metrics:nable-rmm:sites-list
  - metrics:nable-rmm:workstation-count
  - metrics:nable-rmm:workstation-summary
---

# Single-System Analysis — N-able RMM

> **Inspector:** `nable-rmm-inspector` (ID 87). Apps & Services category.
> **One system per N-able RMM account.** Each account contains one or more
> Sites (client sites), each with Servers and Workstations managed by the
> N-able agent. Also known as N-sight RMM (cloud-based SMB product); distinct
> from N-able N-central (enterprise). **Credentialed** — requires an active
> N-able RMM account API token.
>
> **References:** `reference/inspector-aliases.md` (N-able RMM, N-sight).
> Pairs with the `all-rmm-platforms.md` rollup for multi-RMM customer
> environments. Cross-reference endpoint findings with EDR/AV inspector
> recipes for full security posture.

---

## When to use

- "N-able RMM posture for \<customer\>"
- "N-able site connectivity audit"
- "N-able agent coverage check"
- "N-able patch posture review"
- "Which N-able sites are disconnected?"
- "N-able agent version drift"
- Monthly NOC health review; quarterly TAM alignment assessment;
  RMM consolidation analysis

Cadence: monthly for operational reviews; quarterly in PBR; ad-hoc for
site-connectivity outages or agent failures.

Personas:
- **NOC** (primary — agent online/offline triage, site connectivity alerts)
- **TAM / Technical Alignment Manager** (agent version drift, patch posture
  standard compliance, agentless device gap analysis)
- **vCIO / Account Manager** (renewal, coverage posture)
- **Accounting / Finance** (seat utilization, site count vs contract)

---

## Customize for your MSP

```yaml
output:
  format: markdown                          # markdown | word | pptx | xlsx
  filename: "<customer>-nable-rmm-<date>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary:    "Executive Summary"
  site_inventory:       "Site Inventory & Connectivity"
  server_coverage:      "Server Coverage"
  workstation_coverage: "Workstation Coverage"
  os_inventory:         "OS Inventory"
  agent_versions:       "Agent Version Drift"
  patch_posture:        "Patch Posture"
  agentless_devices:    "Agentless / Unmanaged Devices"
  recommendations:      "Recommended Actions"
  data_gaps:            "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"                          # technical | balanced | executive

slas:
  site_connectivity_alert: 0               # connection_ok == 0 → flag site
  agent_online_threshold: 1                # online == 1 = managed and online
  agent_lastSeen_days_max: 7               # workstations/servers last seen > 7 days
  agent_version_max_lag: 2                 # agent_version lag by > 2 minor versions
  patch_age_days_max: 30
  critical_patches_pending_max: 0
  antivirus_coverage_pct_min: 95

qa:
  retry_on_null: true
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  surface_proposed_metrics: false
  manual_verification_section_required: true
```

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System / launchpoint ID (N-able account) | Yes | `liongard_launchpoint LIST inspectorId=87` |
| Optional: specific site name | No | User prompt — narrows output scope |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_launchpoint LIST environmentId=<ENV_ID> inspectorId=87
```

**Note:** N-able RMM may use a parent/child inspector pattern in some
deployments ("N-Able RMM Demo - Parent" / "N-Able RMM Demo - Child").
If both a parent and one or more child launchpoints are present, run this
recipe against the child system that contains `Sites`, `Servers`, and
`Workstations` arrays. The parent is a tenant-roster system; all device
data lives in child systems.

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

N-able RMM data is near-real-time in the N-able console but the Liongard
inspector snapshot is point-in-time. A stale inspector means device
online/offline status may not reflect current reality. Flag any inspector
last-seen > `slas.flag_inspector_lastseen_threshold_days` days.

### Step 3 — Site inventory and connectivity

Use `liongard_metric GENERATE_AND_EVALUATE` for each path below.
All paths are **VALIDATED** against System A (dev environment)
(inspected 2025-05-06).

```
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  jmesPath="<path>"

# ── VALIDATED ────────────────────────────────────────────────────────

# Total site count
#   length(Sites)
#     → integer (e.g. 3)

# Site list with connectivity status
#   Sites[].{siteid: siteid,
#            name: name,
#            connection_ok: connection_ok}
#
#   siteid         — integer; N-able's internal site ID
#   name           — string; site / client name
#   connection_ok  — integer: 1 = site agent connected; 0 = disconnected
#     NOTE: An anonymised demo environment returns obfuscated names
#     (e.g. "anon_87809c95"). Production environments return real site names.

# Count of sites with connectivity issues
#   length(Sites[?connection_ok == `0`])
#     → integer; 0 = all sites healthy
```

**Site connectivity evaluation:**

| Signal | Threshold | Severity |
|---|---|---|
| `connection_ok == 0` | Any site | Critical — N-able cannot reach this site's gateway; device data frozen |
| Site count unexpectedly low | Compare to contract | Warning — verify no sites deleted |

### Step 4 — Server coverage

```
# ── VALIDATED ────────────────────────────────────────────────────────

# Server count
#   length(Servers)
#     → integer

# Server list with identity and status
#   Servers[].{guid: guid,
#              name: name,
#              ip: ip,
#              external_ip: external_ip,
#              os: os,
#              online: online,
#              agent_version: agent_version,
#              domain: domain,
#              last_boot_time: last_boot_time}
#
#   guid           — string; N-able agent GUID
#   name           — string; server hostname
#   ip             — string; internal IP address
#   external_ip    — string; external (WAN) IP
#   os             — string; e.g. "Microsoft Windows Server 2022 Standard"
#   online         — integer: 1 = online; 0 = offline
#   agent_version  — string; underscore-separated (e.g. "10_14_3");
#                    convert to "10.14.3" for display
#   domain         — string; Active Directory domain (e.g. "Jovani.local")
#   last_boot_time — Unix timestamp integer; convert to human-readable date

# Count of online servers
#   length(Servers[?online == `1`])
#     → integer

# Count of offline servers
#   length(Servers[?online == `0`])
#     → integer
```

**Server analysis:**

1. **Coverage** — record `length(Servers)` and confirm it matches
   contract-managed server count.
2. **Offline servers** — any server with `online == 0` is a finding.
   Correlate with `Sites[].connection_ok` to determine if site-level
   connectivity is the root cause.
3. **Agent version drift** — parse `agent_version` (underscore-separated)
   and compare across servers. Flag servers lagging by more than
   `slas.agent_version_max_lag` minor versions from the latest.
4. **Last boot time** — convert Unix timestamp to date. Servers not
   rebooted within the past 30 days may have pending patches requiring
   restart.
5. **OS inventory** — enumerate `os` values and group by OS family and
   version for EOL tracking.

### Step 5 — Workstation coverage

```
# ── VALIDATED ────────────────────────────────────────────────────────

# Workstation count
#   length(Workstations)
#     → integer

# Workstation list with identity and status
#   Workstations[].{guid: guid,
#                   name: name,
#                   ip: ip,
#                   external_ip: external_ip,
#                   os: os,
#                   online: online,
#                   agent_version: agent_version,
#                   domain: domain,
#                   last_boot_time: last_boot_time}
#
#   (fields identical to Servers[] — see Step 4 for field descriptions)
#   os             — e.g. "Microsoft Windows 10 Enterprise"

# Count of online workstations
#   length(Workstations[?online == `1`])

# Count of offline workstations
#   length(Workstations[?online == `0`])
```

Apply the same offline-flag, agent-version-drift, and OS-inventory
analyses as Step 4. Workstations typically have more agent-version lag
than servers; surface as a TAM finding if delta exceeds SLA.

### Step 6 — Agentless devices

```
# ── SCHEMA_CONFIRMED ─────────────────────────────────────────────────
# (array structure confirmed; no data on test system — empty array
#  expected when N-able agentless device scanning is not enabled)

#   length(AgentlessDevices)
#     → integer (0 when feature disabled or no devices detected)
```

If `AgentlessDevices` returns a non-zero count, these are devices visible
on the N-able-monitored network that lack an agent. Surface as a coverage
gap. Cross-reference against the Reconciled Device Inventory (liongard_asset)
to determine if they are unmanaged or out-of-scope devices.

### Step 7 — Mobile devices

```
# ── SCHEMA_CONFIRMED ─────────────────────────────────────────────────
# MobileDevices returns XML-formatted data when N-able MDM is enabled.
# Structure: MobileDevices.result.items[]
# Not data-validated on test system (no mobile devices enrolled).
# Treat as present-if-enrolled; skip if MobileDevices.result.items
# is null or empty.
```

### Step 8 — Patch posture

The N-able RMM Inspector captures patch data per device in
`Servers[].PatchList` and `Workstations[].PatchList`.

```
# ── SCHEMA_CONFIRMED ─────────────────────────────────────────────────
# (PatchList confirmed in schema; detailed sub-field structure
#  requires a populated test system — use liongard_metric
#  GENERATE_AND_EVALUATE against a customer system to confirm
#  PatchList field names before referencing in output)

# Suggested path:
#   Servers[].{name: name, patchCount: length(PatchList)}
#   Workstations[].{name: name, patchCount: length(PatchList)}
```

If patch detail is available, report:
- Count of patches pending per device
- Any device with `>= slas.critical_patches_pending_max` critical patches
- Total managed-device patch age (all pending > `slas.patch_age_days_max` days)

> If `PatchList` is null or empty on the customer system, note as a
> data gap. N-able patch data may require the N-able Patch Manager add-on
> to be enabled and the MSP-standard patch policy applied. Verify in the
> N-able console.

### Step 9 — QA pass

1. Retry any null results per `reference/qa-retry-pattern.md`.
2. **Site connectivity flags propagate** — if `connection_ok == 0`, all
   device data for that site may be stale. Note in every affected finding.
3. Verify `length(Sites) + length(Servers) + length(Workstations)` matches
   expected contract scope.
4. Note data gaps (PatchList sub-fields, MobileDevices)
   as manual-verification items.

### Step 10 — Render

Recommended report structure:

| # | Section | Key Content |
|---|---|---|
| 1 | Executive Summary | Site count, server count, workstation count, connectivity flags |
| 2 | Site Inventory | Table of sites with connectivity status |
| 3 | Server Coverage | Server list: online/offline, OS, agent version |
| 4 | Workstation Coverage | Workstation list: online/offline, OS, agent version |
| 5 | Agent Version Drift | Per-device version heatmap; flag lagging agents |
| 6 | Patch Posture | Per-device pending patches (if available) |
| 7 | Agentless Devices | List of devices without N-able agent (coverage gap) |
| 8 | Recommended Actions | Prioritised findings list |
| 9 | Data Gaps | Manual verification appendix |

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | Steps 3–5 answer asset-inventory and managed-endpoint coverage questions; Step 6 answers agentless-device (unmanaged endpoint) questions. |
| CIS Controls (v8.1) | ✅ | CIS 1.1/1.2 (Steps 3–5 — managed endpoint inventory), 7.3/7.4 (Step 8 — patch posture), 10.1 (Steps 4–5 — AV coverage gap via agentless), 2.1/2.2 (Step 7 — agentless/unmanaged assets). |
| Cyber-insurance domain files | ✅ | `domains/endpoint.md` — Steps 4–5 agent coverage + patch posture; `domains/governance.md` — agent version drift as maintenance-standard evidence. |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this for agent coverage %, offline-device count, patch posture, and agent-version-drift findings. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| Site `connection_ok == 0` | "N-able cannot reach site \<name\>. Device data is frozen as of \<last_seen\>. Investigate gateway / credential issue in N-able console." |
| Offline server | "Server \<name\> at site \<site\> is offline. Confirm hardware health and N-able agent service status." |
| Agent version drift | "Agent \<version\> on \<N\> devices is \<lag\> versions behind current (\<latest\>). Schedule agent update task." |
| Stale last-boot time | "Server \<name\> has not rebooted in \<N\> days — pending patches may require restart. Schedule maintenance window." |
| Agentless devices detected | "\<N\> unmanaged devices detected by N-able. Confirm if in-scope; deploy agent or mark as excluded." |
| PatchList unavailable | "Patch data not available from N-able inspector. Verify N-able Patch Manager add-on is enabled and patch policy is applied." |
| Multiple RMMs present | "Customer has N-able RMM alongside another RMM. Consolidation candidate — surface in QBR." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Patch detail per device (`PatchList` sub-fields) | SCHEMA_CONFIRMED | N-able console; requires Patch Manager add-on |
| Mobile device inventory (MDM) | SCHEMA_CONFIRMED | N-able console; requires MDM feature enabled |
| Antivirus status per device | not in dataprint | N-able console; cross-reference EDR inspector |
| Monitor / alert policy per device | Not in dataprint | N-able console |
| RMM user / technician list | Not in dataprint | N-able console → user audit |
| License seat utilization | Not in dataprint | N-able console → subscription dashboard |

---

## Verification log

| Step | Tool | Validated Path | Result Shape | Validation Status |
|---|---|---|---|---|
| 3 | liongard_metric EVALUATE | `length(Sites)` | integer → 3 | VALIDATED (System A, dev environment) |
| 3 | liongard_metric EVALUATE | `Sites[].{siteid, name, connection_ok}` | array; `connection_ok: 1` | VALIDATED |
| 4 | liongard_metric EVALUATE | `length(Servers)` | integer → 1 | VALIDATED |
| 4 | liongard_metric EVALUATE | `Servers[].{guid, name, ip, external_ip, os, online, agent_version, domain, last_boot_time}` | array; `online: 1`, `agent_version: "10_14_3"`, `last_boot_time`: Unix int | VALIDATED |
| 5 | liongard_metric EVALUATE | `length(Workstations)` | integer → 1 | VALIDATED |
| 5 | liongard_metric EVALUATE | `Workstations[].{guid, name, ip, external_ip, os, online, agent_version, domain, last_boot_time}` | array; `os: "Microsoft Windows 10 Enterprise"` | VALIDATED |
| 6 | liongard_launchpoint GET_OVERVIEW | `AgentlessDevices` | Array(0) in schema | SCHEMA_CONFIRMED |
| 7 | liongard_launchpoint GET_OVERVIEW | `MobileDevices` | XML structure in schema | SCHEMA_CONFIRMED |
| 8 | liongard_launchpoint GET_OVERVIEW | `Servers[].PatchList` / `Workstations[].PatchList` | schema key only | SCHEMA_CONFIRMED |

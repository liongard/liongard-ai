---
name: single-system-continuum-rmm
description: >
  Use this recipe when the user wants a single-system analysis of a legacy
  Continuum RMM account — device inventory, antivirus posture summary,
  patch-state summary, health-score review, warranty summary, and site
  statistics. Trigger phrases: "Continuum RMM report for <customer>",
  "Continuum RMM device inventory", "Continuum antivirus posture", "legacy
  Continuum RMM review", "Continuum RMM EOL migration assessment".
  IMPORTANT: Continuum RMM reached End of Life; ConnectWise migrated customers
  to ConnectWise Command / ConnectWise RMM. This recipe is for environments
  still running the Continuum inspector (inspector ID 60) with historical data.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_launchpoint, liongard_metric, liongard_timeline"
inspector_id: 60
inspector_name: "Continuum RMM"
category: RMM
personas: [noc, technical-alignment-manager, vcio-account-manager]
output_formats: [markdown, word, xlsx]
primitives:
  - metrics:continuum-rmm-inspector:antivirus-summary-desktops
  - metrics:continuum-rmm-inspector:antivirus-summary-servers
  - metrics:continuum-rmm-inspector:device-inventory
  - metrics:continuum-rmm-inspector:failed-or-stale-agents-count
  - metrics:continuum-rmm-inspector:failed-or-stale-agents-list
  - metrics:continuum-rmm-inspector:health-scores
  - metrics:continuum-rmm-inspector:patch-state-servers
  - metrics:continuum-rmm-inspector:summary-site
  - metrics:continuum-rmm-inspector:total-agents-count
  - metrics:continuum-rmm-inspector:total-snmp-devices-count
  - metrics:continuum-rmm-inspector:warranty-summary-servers
---

# Single-System Analysis — Continuum RMM (Legacy)

> **Inspector:** `continuum-rmm-inspector` (ID 60). Apps & Services category.
> **One system per Continuum RMM account.** Continuum RMM was acquired by
> ConnectWise in 2019 and subsequently End-of-Lifed (EOL) as ConnectWise
> migrated customers to ConnectWise Command / ConnectWise RMM. If this
> inspector exists in a Liongard environment, it reflects a **legacy or
> partially migrated** deployment. All inspection data is historical; the
> `online` field for managed devices is expected to be `null` on EOL systems.
>
> **Use case for this recipe:**
> 1. Historical device-inventory baseline prior to RMM migration
> 2. EOL migration assessment — what devices were in Continuum and do
>    they appear in the replacement RMM?
> 3. Legacy compliance evidence (patch state, AV posture, health scores
>    from the last successful inspection)
>
> **References:** `reference/inspector-aliases.md` (Continuum, ConnectWise
> Command). For the replacement platform, see
> `connectwise-asio.md` or `connectwise-automate.md`. Use
> `all-rmm-platforms.md` to identify whether a successor RMM is deployed.

---

## When to use

- "Continuum RMM historical inventory for \<customer\>"
- "Continuum EOL — what devices were managed?"
- "Continuum antivirus/patch posture (last known state)"
- "RMM migration baseline — compare Continuum devices to \<new RMM\>"
- "Continuum health score review"
- EOL migration planning; compliance evidence for past period;
  legacy-environment decommission support

Cadence: typically one-time (EOL migration) or ad-hoc (compliance evidence).
If the Continuum inspector is still active and returning data, treat as a
monthly review until migration is confirmed complete.

Personas:
- **NOC** (historical device inventory, offline-device triage)
- **TAM / Technical Alignment Manager** (EOL migration assessment;
  device-count reconciliation between Continuum and successor RMM)
- **vCIO / Account Manager** (migration completion confirmation;
  risk narrative for EOL platform)

---

## Customize for your MSP

```yaml
output:
  format: markdown                          # markdown | word | xlsx
  filename: "<customer>-continuum-rmm-legacy-<date>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary:    "Executive Summary"
  platform_status:      "Platform EOL Status"
  device_inventory:     "Device Inventory (Last Known State)"
  health_scores:        "Health Score Summary"
  site_statistics:      "Site Statistics"
  antivirus_posture:    "Antivirus Posture"
  patch_state:          "Patch State Summary"
  warranty_summary:     "Warranty Summary"
  migration_checklist:  "Migration Checklist (if applicable)"
  recommendations:      "Recommended Actions"
  data_gaps:            "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"                          # technical | balanced | executive

flags:
  eol_platform: true                        # always flag this as an EOL platform
  migration_check: true                     # check for successor RMM in same environment

qa:
  retry_on_null: true
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 30   # relaxed threshold — EOL expected to be stale
  surface_proposed_metrics: false
  manual_verification_section_required: true
```

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System / launchpoint ID (Continuum account) | Yes | `liongard_launchpoint LIST inspectorId=60` |
| Successor RMM system (if migrating) | Recommended | `liongard_launchpoint LIST inspectorId=<successor_id>` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_launchpoint LIST environmentId=<ENV_ID> inspectorId=60
```

**Expected:** The Continuum launchpoint will typically show status
`Inspector Failure` (EOL — API no longer reachable). The last successful
inspection timestamp indicates when live data was last captured.
All subsequent steps operate against that historical dataprint.

**Also check for a successor RMM:**

```
liongard_launchpoint LIST environmentId=<ENV_ID> inspectorId=103  # CW Asio
liongard_launchpoint LIST environmentId=<ENV_ID> inspectorId=73   # Datto RMM
liongard_launchpoint LIST environmentId=<ENV_ID> inspectorId=78   # NinjaOne
```

If a successor RMM is present, the primary deliverable is a migration
reconciliation (Continuum devices vs successor RMM devices).

### Step 2 — Inspector freshness / EOL acknowledgement

```
liongard_timeline LIST environmentId=<ENV_ID>
```

Note the last successful inspection date. Document prominently in the
report: "This data reflects the state of Continuum RMM as of
\<last_inspection_date\>. The Continuum platform has reached End of Life;
this represents historical data only."

If `Inspector Failure` status is confirmed, skip freshness SLA flags
(stale is expected) and proceed with historical data analysis.

### Step 3 — Device inventory (last known state)

Use `liongard_metric GENERATE_AND_EVALUATE` for each path below.
All paths are **VALIDATED** against System A (dev environment)
(last inspected 2025-02-11 — Inspector Failure status but dataprint
preserved).

```
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  jmesPath="<path>"

# ── VALIDATED ────────────────────────────────────────────────────────

# Total device count
#   length(Devices)
#     → integer (e.g. 3)

# Device list with identity and status
#   Devices[].{machineID: machineID,
#              machineName: machineName,
#              assetType: assetType,
#              companyName: companyName,
#              siteName: siteName,
#              operatingSystem: operatingSystem,
#              online: online,
#              lastSeenOnline: lastSeenOnline,
#              lastReboot: lastReboot}
#
#   machineID         — string; Continuum's internal machine identifier
#   machineName       — string; hostname as registered in Continuum
#   assetType         — string; role classification
#                       (e.g. "Primary Domain Controller", "")
#   companyName       — string; the client company this device belongs to
#   siteName          — string; the site this device belongs to
#   operatingSystem   — string; OS name (e.g.
#                       "Microsoft Windows Server 2019 Datacenter ()")
#                       or "" when not captured
#   online            — null on EOL systems (Continuum API no longer
#                       returning real-time status); may be boolean on
#                       live systems
#   lastSeenOnline    — ISO 8601 timestamp; last time device was reported
#                       online by Continuum (e.g. "2024-03-15T04:59:44Z")
#   lastReboot        — string; ISO 8601 or "" when not captured
```

**Device inventory notes:**

- `online: null` is expected on all EOL systems — Continuum is no longer
  reporting real-time device status.
- Use `lastSeenOnline` as a proxy for device activity history.
- `assetType` provides role classification for server vs workstation
  categorisation (though the structure also uses `Servers[]` /
  `Workstations[]` sub-collections in richer deployments).

**Also pull site statistics from the summary object:**

```
# ── VALIDATED ────────────────────────────────────────────────────────

# Summary site statistics
#   SummarySite
#     → object with fields:
#       AntivirusMachineCount  — integer; total devices with AV tracked
#       AntivirusMachineUpdated — integer; devices with AV up to date
#       DesktopCount           — integer; total desktops managed
#       FirewallCount          — integer; firewalls managed
#       MobileDeviceCount      — integer; mobile devices
#       PatchesInstalled       — integer; patches installed
#       PatchesUnderReview     — integer; patches pending review
#       ServerCount            — integer; total servers managed
#       ServiceTicketsClosed   — integer; closed tickets (if PSA linked)
#       ServiceTicketsOpened   — integer; opened tickets (if PSA linked)
#       SwitchCount            — integer; network switches
#       TemporaryFilesRemoved  — string (e.g. "0"); temp files cleaned
#       ThirdPartyPatchesInstalled — integer; third-party patches installed
#
#   Example result: ServerCount: 2, DesktopCount: 1,
#                   AntivirusMachineCount: 3, AntivirusMachineUpdated: 2
```

### Step 4 — Health score summary

```
# ── VALIDATED ────────────────────────────────────────────────────────

# Overall and per-category health scores (0–100; -1 = data unavailable)
#   SummaryScore.Scores
#     → object with fields:
#       Overall                  — integer (e.g. 37); composite health score
#       DesktopAntivirus         — integer | -1
#       DesktopDiskSpace         — integer | -1
#       DesktopPatch             — integer | -1
#       DesktopTempFile          — integer | -1
#       DesktopWarranty          — integer | -1
#       ServerAntivirus          — integer | -1 (e.g. 62)
#       ServerAvailability       — integer | -1 (e.g. 0 — all offline EOL)
#       ServerCpuUtilization     — integer | -1 (e.g. 100)
#       ServerDiskUtilization    — integer | -1 (e.g. 100)
#       ServerMemoryUtilization  — integer | -1 (e.g. 100)
#       ServerPatch              — integer | -1
#       ServerWarranty           — integer | -1
#
#   NOTE: -1 means no data available for that category (feature not
#   enabled, no devices, or metric not captured).
#   ServerAvailability: 0 is expected on EOL systems (all offline).
```

**Score interpretation:**

| Score | Meaning |
|---|---|
| 100 | Category fully compliant / healthy at last inspection |
| 1–99 | Partial compliance — some devices failing category check |
| 0 | Category at full failure (all devices failing — or platform offline) |
| -1 | No data for this category |

Present the `Overall` score as the headline number. Identify the lowest
non-(-1) category scores as priority remediation areas (or migration
evidence for the EOL case).

### Step 5 — Antivirus posture

```
# ── VALIDATED ────────────────────────────────────────────────────────

# Server AV summary
#   AntivirusSummaryServers.Updated         → integer (e.g. 2)
#   AntivirusSummaryServers.Outdated        → integer
#   AntivirusSummaryServers.NotInstalled    → integer
#
#   (combine into AV coverage percentage:
#    Updated / (Updated + Outdated + NotInstalled) * 100)

# Desktop AV summary
#   AntivirusSummaryDesktops.Updated        → integer
#   AntivirusSummaryDesktops.Outdated       → integer
#   AntivirusSummaryDesktops.NotInstalled   → integer
```

**AV coverage calculation:**

```
server_av_coverage_pct  = Updated / (Updated + Outdated + NotInstalled) * 100
desktop_av_coverage_pct = Updated / (Updated + Outdated + NotInstalled) * 100
```

Flag when either falls below 100% (EOL baseline — every device should have
had updated AV at last inspection). For migration assessments, note AV
coverage status as a comparison baseline against the successor RMM.

Antivirus version detail (vendor, version, status) is captured in
`AntivirusVersions.AntivirusVersionSummary[]` but may return null fields
on degraded systems:

```
# ── SCHEMA_CONFIRMED (fields present; may be null) ───────────────────
#   AntivirusVersions.AntivirusVersionSummary[].{antivirus: antivirus,
#                                                count: count,
#                                                status: status}
#   NOTE: In test system, all fields returned null — possible data
#   degradation on EOL system or feature not enabled.
```

### Step 6 — Patch state summary

```
# ── VALIDATED ────────────────────────────────────────────────────────

# Server patch state
#   PatchesStateServers.{Installed: Installed,
#                        Missing: Missing,
#                        Blacklisted: Blacklisted,
#                        MarkedForDeployment: MarkedForDeployment,
#                        Others: Others,
#                        UnderReview: UnderReview}
#     → integers per state
#     Example: Installed: 0, Missing: 0 (test system — no patch data)

# Desktop patch state
#   PatchesStateDesktops.{Installed: Installed,
#                         Missing: Missing,
#                         Blacklisted: Blacklisted,
#                         MarkedForDeployment: MarkedForDeployment,
#                         Others: Others,
#                         UnderReview: UnderReview}
#     → integers per state
```

**Patch state notes:**

- `Missing` is the primary risk field. Any non-zero `Missing` count at
  the EOL snapshot date indicates patch debt that carried into the migration.
- `Blacklisted` indicates patches deliberately excluded from deployment.
  Surface for TAM review — blacklisted patches should have documented
  justification.
- `MarkedForDeployment` = patches queued but not yet applied (test-system
  value: 0).
- On EOL systems, `Installed: 0, Missing: 0` typically indicates Continuum's
  patch data was not collected before EOL (not necessarily that all patches
  are installed).

### Step 7 — Warranty summary

```
# ── VALIDATED ────────────────────────────────────────────────────────

# Server warranty summary
#   WarrantySummaryServers.{Error: Error,
#                           Active: Active,
#                           DataUnavailable: DataUnavailable,
#                           Expired: Expired}
#     → integers (Error is null when no API errors)
#     Example: Active: 0, DataUnavailable: 2, Expired: 0
```

Desktop warranty summary also available at `WarrantySummaryDesktops`
(same structure). `DataUnavailable` is common on EOL systems where
warranty APIs are no longer polled. For migration assessments, note
which devices had expired warranties at EOL — these are refresh candidates.

### Step 8 — Migration reconciliation (if applicable)

When a successor RMM is deployed in the same environment:

1. Pull device count from the successor RMM.
2. Compare `length(Devices)` from Continuum vs successor RMM device count.
3. Surface any delta as a migration-completeness finding.
4. Cross-reference by device `machineName` where possible.

```
# Example reconciliation query against successor RMM
# (adjust path per the successor recipe):
liongard_metric EVALUATE systemId=<SUCCESSOR_SYS_ID>
  jmesPath="length(<DeviceArray>)"
```

Emit a migration-status table:

| System | Device Count | Source |
|---|---|---|
| Continuum RMM (historical) | `length(Devices)` | This recipe |
| \<Successor RMM\> (current) | \<count\> | Successor recipe |
| Delta | Δ | Unreconciled devices |

### Step 9 — QA pass

1. Retry any null results per `reference/qa-retry-pattern.md`.
2. **Inspector Failure is expected** — do not flag as an error; document
   the EOL status prominently.
3. Verify `SummarySite.ServerCount + SummarySite.DesktopCount` against
   `length(Devices)` for internal consistency.
4. Note all `-1` health scores as "data unavailable" rather than "score 0".

### Step 10 — Render

Recommended report structure:

| # | Section | Key Content |
|---|---|---|
| 1 | Executive Summary | EOL platform flag; last inspection date; device count; overall health score |
| 2 | Platform EOL Status | EOL explanation; migration status; successor RMM identified (if any) |
| 3 | Device Inventory | Table: machineName, assetType, companyName, siteName, OS, lastSeenOnline |
| 4 | Health Score Summary | Overall score + per-category scorecard (exclude -1 entries) |
| 5 | Site Statistics | SummarySite key counts |
| 6 | Antivirus Posture | Server + desktop AV coverage percentages |
| 7 | Patch State Summary | Server + desktop patch state breakdown |
| 8 | Warranty Summary | Server + desktop warranty status |
| 9 | Migration Checklist | Continuum vs successor device count reconciliation |
| 10 | Recommended Actions | Prioritised findings |
| 11 | Data Gaps | Manual-verification appendix |

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ⚠️ | This is a legacy EOL inspector. Onboarding questions are answered by the *successor* RMM recipe. Continuum data is useful as a historical baseline only; onboarding matrix should reference current-state RMM. |
| CIS Controls (v8.1) | ✅ | CIS 1.1/1.2 (Step 3 — device inventory at EOL snapshot), 10.1 (Steps 5 — AV coverage at last inspection), 7.3/7.4 (Step 6 — patch state at last inspection), 2.1 (OS inventory from `Devices[].operatingSystem`). |
| Cyber-insurance domain files | ⚠️ | `domains/endpoint.md` — AV/patch posture available as historical evidence only. Cyber-insurance applications should use successor-RMM data for current-state posture. Note if Continuum data is used as evidence: cite last-inspection date. |
| QBR / quarterly-business-review | ⚠️ | Continuum data should only appear in a QBR to document migration progress (EOL baseline vs current-state in successor RMM). Do not present Continuum scores as current-state posture. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| Continuum launchpoint still present, no successor RMM | "Continuum RMM has reached EOL and is no longer functional. No successor RMM was detected. Recommend immediate RMM platform selection and deployment." |
| Successor RMM device count < Continuum count | "\<Δ\> devices from Continuum have not migrated to \<successor\>. Complete agent deployment to \<list\> before decommissioning Continuum launchpoint." |
| AV coverage < 100% at EOL snapshot | "At last Continuum inspection (\<date\>), \<N\> devices had outdated or missing AV. Confirm these devices are now protected under \<successor RMM\>." |
| `SummaryScore.Overall` < 70 | "Continuum health score was \<score\>/100 at last inspection (\<date\>). Remediation items from that snapshot should be confirmed as resolved in \<successor\>." |
| `WarrantySummaryServers.Expired > 0` | "\<N\> servers had expired warranties at Continuum EOL. Flag as refresh candidates; include in hardware roadmap." |
| `PatchesStateServers.Missing > 0` | "\<N\> server patches were missing at last Continuum inspection. Confirm applied in \<successor\>; include in patch-debt remediation if not." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Real-time device online status | Not available (EOL) | Successor RMM; direct device connectivity check |
| Antivirus version detail (`AntivirusVersions`) | SCHEMA_CONFIRMED but null on test system | Continuum console (if still accessible) |
| Per-device patch list | SCHEMA_CONFIRMED in schema | Continuum console |
| Alert / ticket history | `Worksummary` — empty on test system | ConnectWise Manage / PSA |
| Backup continuity appliance data | `BackupContinuity247*` — empty on test system | Continuum / ConnectWise BCDR console |
| SNMP device inventory | `SnmpDevices` — empty on test system | Continuum console |
| Mobile device compliance | `MobiledevicesNoncompliant` — empty on test system | Continuum MDM console |

---

## Verification log

| Step | Tool | Validated Path | Result Shape | Validation Status |
|---|---|---|---|---|
| 3 | liongard_metric GENERATE_AND_EVALUATE | `length(Devices)` | integer → 3 | VALIDATED (System A, dev environment, last insp. 2025-02-11) |
| 3 | liongard_metric EVALUATE | `Devices[].{machineID, machineName, assetType, companyName, siteName, operatingSystem, online, lastSeenOnline, lastReboot}` | array; `online: null`, `assetType: "Primary Domain Controller"\|""`, `operatingSystem`: string | VALIDATED |
| 3 | liongard_metric EVALUATE | `SummarySite` | object; `ServerCount: 2`, `DesktopCount: 1`, `AntivirusMachineCount: 3`, `AntivirusMachineUpdated: 2` | VALIDATED |
| 4 | liongard_metric EVALUATE | `SummaryScore.Scores` | object; `Overall: 37`, `ServerAntivirus: 62`, `ServerAvailability: 0`, `ServerCpuUtilization: 100` | VALIDATED |
| 5 | liongard_metric GENERATE_AND_EVALUATE | `AntivirusSummaryServers.{Updated, Outdated, NotInstalled}` | object; `Updated: 2`, `Outdated: 0`, `NotInstalled: 0` | VALIDATED |
| 5 | liongard_metric GENERATE_AND_EVALUATE | `AntivirusSummaryDesktops.{Updated, Outdated, NotInstalled}` | object; all 0 (no desktop AV data) | VALIDATED |
| 5 | liongard_metric EVALUATE | `AntivirusVersions.AntivirusVersionSummary[].{antivirus, count, status}` | array; all fields null on test system | SCHEMA_CONFIRMED (degraded) |
| 6 | liongard_metric GENERATE_AND_EVALUATE | `PatchesStateServers.{Installed, Missing, Blacklisted, MarkedForDeployment, Others, UnderReview}` | object; all 0 on test system | VALIDATED |
| 6 | liongard_metric GENERATE_AND_EVALUATE | `PatchesStateDesktops.{Installed, Missing, ...}` | object; all 0 on test system | VALIDATED |
| 7 | liongard_metric EVALUATE | `WarrantySummaryServers` | object; `Active: 0`, `DataUnavailable: 2`, `Expired: 0`, `Error: null` | VALIDATED |

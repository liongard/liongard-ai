---
name: single-system-cove-data-protection
description: >
  Use this skill when the user wants a single-tenant analysis of a Cove
  Data Protection account — backup-coverage review, failed-backup audit,
  24-hour completion compliance, Exchange / OneDrive / file-server
  protection state, device-level backup status. Cove is N-able's cloud
  backup product (formerly SolarWinds Backup). Trigger phrases: "Cove
  PBR", "Cove backup review", "pull Cove data", "Cove failed backups",
  "N-able Cove report", "SolarWinds Backup review". Produces an artifact
  in the format set in the customization block.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, xlsx]
primitives:
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
---

# Single-System Analysis — Cove Data Protection

> **Inspector:** `cove-data-protection-inspector` (ID 76). Apps & Services
> category. Backup / DR. Cove is N-able's cloud-managed backup product
> (formerly SolarWinds Backup before the N-able rebrand).
>
> **References:** `reference/inspector-aliases.md` (Cove, N-able Cove,
> "SolarWinds Backup" legacy). `reference/asset-fields.md` for the
> device-inventory cross-check. `reference/qa-retry-pattern.md` for QA
> pass details. **Pairs with `recipes/system-type-assessment/all-backups.md`**
> for the cross-vendor coverage rollup.


---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-cove-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  device_coverage: "Device Backup Coverage"
  m365_coverage: "Microsoft 365 Backup Coverage"
  failed_backups: "Failed Backups"
  retention: "Retention & Storage"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 1
  failed_backups_max: 0
  cloud_backup_max_age_hours: 24
  device_hours_since_last_backup_max: 24
  exchange_hours_since_last_backup_max: 24
  onedrive_hours_since_last_backup_max: 24

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

- "Pull Cove data for the customer" (PBR)
- "Are any Cove backups failing?"
- "Cove 24-hour completion compliance check"
- "What M365 resources is Cove protecting?"
- Quarterly backup-coverage review

Personas: NOC (operational state), TAM (deep dive), vCIO/AM (executive
summary, license / cost).

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Cove system ID | Yes | `liongard_system LIST query="cove"` |
| Reporting period | No | Default per customization |

---

## Locating the right system

```
liongard_system LIST searchMode=keyword query="cove" environmentId=<ENV_ID>
```

`SystemInfo.Name` returns the tenant / partner-company name within Cove.


---

## Liongard data sources

> **Asset Inventory First, Metric Cross-Check.** The cross-inspector
> `liongard_device` is the **denominator** — every server / VM the
> customer has. Cove's `Devices[*]` array is the **numerator** — what
> Cove is actively protecting. The all-backups.md recipe joins them by
> hostname for the unprotected-servers analysis; this recipe focuses on
> Cove's own operational state.

### Per-vendor data — Cove dataprint top-level keys

| Key | Description |
|---|---|
| `SystemInfo` | Tenant identifier — Name (partner / company within Cove) |
| `Devices` | Array of every protected device — Type (BackupManager / Office365), Name, BackupStatus, per-service Hours-Since-Last-Backup fields |
| `Account` | Cove account metadata (license + seat counts) |

#### Field gotchas (inline notes — not TODO)

- **`Devices[*].Type` distinguishes the protection class.** Cove uses
  `BackupManager` for agent-based device backups (Windows / Linux / Mac
  servers, VMs) and `Office365` for cloud-to-cloud M365 backups
  (Exchange / OneDrive / SharePoint / Teams). The `HoursSince*` fields
  are Type-specific:
  - For `BackupManager` devices: `HoursSinceLastCompletedBackup`
  - For `Office365` devices: `HoursSinceExchangeLastCompletedBackup`,
    `HoursSinceOneDriveLastCompletedBackup`,
    `HoursSinceSharePointLastCompletedBackup` (proposed),
    `HoursSinceTeamsLastCompletedBackup` (proposed)
- **`BackupStatus` values include `Successful`, `Failed`, `InProgress`,
  `Idle`.** Filter on `Failed` for the headline failure count and
  `Idle` for orphaned protected devices that haven't run recently.

### Cross-inspector cross-check — device inventory

```
liongard_device LIST environmentId=<ENV_ID> class="server"
                     fields=["hostname","inspectors","operatingSystem"]
```

```
# Servers Cove sees
cove_protected = devices where inspectors contains "cove-data-protection-inspector"

# Servers Liongard knows about but Cove doesn't see → unprotected candidates
unprotected_candidates = devices where class == "server"
                                       AND inspectors does not contain "cove-data-protection-inspector"
```

For the full cross-vendor unprotected-servers analysis, run
`all-backups.md` — it joins Cove + every other backup vendor against the
device inventory.

---

## Metrics and queries

### Failed backups (headline)

| Metric | JMESPath | Compliant when |
|---|---|---|
| Failed backup count | `length(Devices[?BackupStatus == \`Failed\`])` | `0` |
| Devices >24h since successful backup | `length(Devices[?Type == \`BackupManager\` && HoursSinceLastCompletedBackup > \`24\`])` | `0` |

### Microsoft 365 protection

| Metric | JMESPath | Compliant when |
|---|---|---|
| Exchange >24h overdue count | `length(Devices[?Type == \`Office365\` && HoursSinceExchangeLastCompletedBackup > \`24\`])` | `0` |
| OneDrive >24h overdue count | `length(Devices[?Type == \`Office365\` && HoursSinceOneDriveLastCompletedBackup > \`24\`])` | `0` |
| SharePoint >24h overdue count | proposed | `0` |
| Teams >24h overdue count | proposed | `0` |

### Per-device detail (for the all-backups.md join)

```jmespath
Devices[*].{
  name: Name,
  type: Type,
  status: BackupStatus,
  hoursAgo: HoursSinceLastCompletedBackup,
  retention: RetentionDays
}
```

### Proposed metrics (not yet in Liongard library)

| Field | Workaround |
|---|---|
| Per-device backup detail composite | Client-side parse of `Devices[*]` |
| SharePoint / Teams protection state | Manual confirm in Cove dashboard (`backup.management`) |
| Per-device storage used | Manual confirm in Cove dashboard |

### Time-series — failure / coverage trend

```
# Failed-backup count trend
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="length(Devices[?BackupStatus == `Failed`])"

# Protected-device count trend (capacity / scope)
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="length(Devices)"
```

---

## QA & Manual Verification

Run the QA pass per `reference/qa-retry-pattern.md` before rendering output:

1. **Retry persistent nulls.** Cove API throttling can produce transient
   null Devices arrays — retry up to `qa.retry_attempts` times.

2. **Flag stale inspector data.** Cove is cloud-API-driven; staleness
   usually means API-key or scope problems.

3. **Cross-tool divergence:** the Cove `Devices[*]` enumeration should
   reconcile with the device inventory's "servers with Cove in their
   `inspectors[]` array". A divergence (Cove sees more devices than the
   asset inventory does, or vice versa) indicates either stale data or
   a naming mismatch.

4. **Proposed-metric gaps for this recipe** — surface in the
   manual-verification appendix:
   - Per-device backup detail composite metric
   - SharePoint / Teams protection state
   - Per-device storage used

5. **Manual Verification appendix** — render in the deliverable. Typical
   items for this recipe:
   - Devices in `Idle` status (protected but not running — orphaned?)
   - Cove-protected hostnames that don't match any server in the device
     inventory (orphaned protection on a decommissioned server — cost
     leak).
   - Customer reports M365 SharePoint / Teams should be protected, but
     the metric is proposed — manual confirm in Cove dashboard.

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Failed backups | `length(Devices[?BackupStatus == 'Failed']) > 0` | "<N> devices in Failed state — investigate agent connectivity / target availability." |
| Overdue device backups | `length(Devices[?Type == 'BackupManager' && HoursSinceLastCompletedBackup > 24]) > 0` | "<N> agent-based devices haven't completed a backup in 24h+ — escalate." |
| Overdue M365 backups | Exchange / OneDrive overdue counts > 0 | "<N> M365 resources overdue — confirm Cove M365 service status." |
| Cove-protected hostname unknown to device inventory | a Cove `Devices[*].Name` doesn't match any device record | "Cove protects <hostname> but no matching server in inventory — confirm intentional or remove the orphaned plan." |
| Idle protected device | `Devices[?BackupStatus == 'Idle']` > 0 | "<N> protected devices in `Idle` state — schedule may not be running; review." |
| Stale Cove inspector | `lastSeen > 1 day` | "Cove inspector hasn't reported in <N> days — confirm API access." |


---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Per-device storage utilization | ⚠️ not in dataprint | Cove dashboard |
| SharePoint / Teams protection state | ⚠️ not in dataprint | Cove dashboard |
| Restore test history | ❌ not in dataprint | MSP runbook |
| Per-device retention enforcement | ⚠️ partial (`RetentionDays` in proposed composite) | Cove dashboard |
| CloudCache / standby image status | ❌ not in dataprint | Cove dashboard |
| Bandwidth throttling / WAN-acceleration state | ❌ not in dataprint | Cove dashboard |


---

## Output format

Markdown / Word / Excel per `output.format`. **xlsx** is the canonical
fit for per-device backup status grids (sortable by status / hours-since).

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_system LIST | query="cove" envId=<ENV_ID> | array<system> | ok |
| 3 | liongard_metric EVALUATE | verified overdue/failed-backup JMESPaths against `Devices[]` sysId=<SYS_ID> envId=<ENV_ID> | <integer> | ok per path |
| 4 | liongard_metric EVALUATE | jmesPath Devices[*]... sysId=<SYS_ID> envId=<ENV_ID> | <array> | ok |
| 5 | liongard_device LIST | envId=<ENV_ID> class=server fields=[hostname,inspectors,operatingSystem] | array<device> | ok |
| 6 | (QA pass) retry persistent nulls + divergence checks | per `reference/qa-retry-pattern.md` | varies | ok |
```

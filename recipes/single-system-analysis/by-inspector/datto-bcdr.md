---
name: single-system-datto-bcdr
description: >
  Use this skill when the user wants a single-appliance analysis of a
  Datto BCDR (SIRIS or ALTO appliance) — protected-device coverage,
  last-valid-backup state per device, failed-backup detection, cloud
  sync status, screenshot-verification posture. Datto BCDR is
  appliance-based image-level backup with cloud replication. Trigger
  phrases: "Datto BCDR review", "SIRIS PBR", "ALTO appliance status",
  "pull Datto backup data", "Datto failed backups", "Datto cloud sync
  status". Produces an artifact in the format set in the customization
  block.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, xlsx]
primitives:
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
---

# Single-System Analysis — Datto BCDR

> **Inspector:** `datto-bcdr-inspector` (ID 38). Apps & Services
> category. Backup / DR. Datto BCDR family includes SIRIS (appliance)
> and ALTO (smaller appliance form factor).
>
> **Parent/child:** Yes. Parent enumerates customer companies across
> appliances; child is per-appliance with `Assets[*]` for that
> appliance's protected machines.
>
> **References:** `reference/inspector-aliases.md` (Datto BCDR, SIRIS,
> ALTO). **Pairs with `recipes/system-type-assessment/all-backups.md`**
> for the cross-vendor coverage rollup.
>
> **Data gap note.** Most Datto BCDR detail fields are not available as
> catalog metrics. The workflow uses direct JMESPath evaluation against
> the `Assets[]` array. Manual portal verification is required for
> cloud sync, appliance storage, and screenshot verification state.


---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-datto-bcdr-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  appliance_inventory: "Appliance / Customer Inventory"
  agent_coverage: "Per-Agent Backup Coverage"
  failed_backups: "Failed & Overdue Backups"
  cloud_sync: "Cloud Sync (3-2-1 Compliance)"
  screenshot_verification: "Screenshot Verification State"
  capacity: "Appliance Storage Utilization"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 1
  failed_backups_max: 0
  hours_since_last_backup_max: 24
  cloud_sync_required: true
  screenshot_verification_max_age_days: 7   # weekly verification expected

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

- "Pull Datto BCDR data for the customer" (PBR)
- "SIRIS / ALTO appliance status review"
- "Datto failed backups audit"
- "Datto cloud-sync compliance check (3-2-1)"
- "Datto screenshot-verification review"

Personas: NOC, vCIO/AM, TAM, SOC (ransomware preparedness via screenshot
verification).

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Datto BCDR child system ID | Yes | `liongard_system LIST query="datto"` |
| Reporting period | No | Default per customization |

---

## Locating the right system

```
liongard_system LIST searchMode=keyword query="datto" environmentId=<ENV_ID>
```

| Shape | What it is | Action |
|---|---|---|
| Has `SystemInfo[*]` (array) enumerating `clientCompanyName` + appliance metadata | **Parent** — partner-level rollup | Skip for per-customer reports |
| Has `SystemInfo` (object) with `clientCompanyName` (singular) + `Assets[*]` for that appliance | **Child** — per-appliance | Use this |

`SystemInfo.clientCompanyName` (singular, on the child) returns the
customer company name.

> **Disambiguate from Datto RMM.** That's a separate inspector
> (`datto-rmm-inspector` ID 73) for the RMM product, NOT the BCDR
> backup appliance.


---

## Liongard data sources

> **Asset Inventory First, Metric Cross-Check.** Datto BCDR's
> `Assets[*]` array is the per-vendor protected-device list. The
> cross-inspector `liongard_device` is the denominator. Most of Datto's
> backup-state fields are not in the current dataprint — surface the gaps in the
> Manual Verification appendix.

### Per-vendor data — Datto BCDR dataprint top-level keys

| Key | Description |
|---|---|
| `SystemInfo` | Parent: array enumerating clientCompanyName + appliance metadata. Child: singular object for one appliance + customer. |
| `Assets` | Per-protected-machine array on the child appliance — `name` is the hostname-join key |
| `Account` | Datto Partner Portal account metadata |

#### Field gotchas (inline notes — not TODO)

- **Parent vs. child distinction.** Parent has `SystemInfo[*]` (array)
  enumerating `clientCompanyName` + appliance metadata across all child
  appliances. Child has `SystemInfo` (object) with `clientCompanyName`
  (singular) + `Assets[*]` for that appliance's protected machines.
  Always target the child for per-customer reports.
- **`Assets[*].name` is the hostname-join key for
  `all-backups.md`.** May contain FQDN or short name depending on agent
  install configuration — apply the FQDN-stripping pattern documented
  in `all-backups.md`.
- **Field name correction (VALIDATED 2026-05-27).** The protected-machine
  array is `Assets[*]`, not `Agents[*]`. The hostname field is `name`, not
  `machineName`. Backup age is `HoursSinceLastSuccessfulBackup_r` (numeric,
  hours, `_r` suffix = raw value). Screenshot field is
  `lastScreenshotAttemptStatus`, not `lastScreenshotStatus`.
  `cloudSyncStatus` is not present in the dataprint — use portal review.
- **Screenshot verification is unique to Datto.** Other backup vendors
  don't expose anything equivalent. Highlight this in vCIO conversations
  when Datto is the chosen vendor — it shifts "we hope backups work" to
  "we have visual evidence they're recoverable, refreshed weekly".

### Cross-inspector cross-check — device inventory

```
liongard_device LIST environmentId=<ENV_ID> class="server"
                     fields=["hostname","inspectors","operatingSystem"]
```

```
# Servers Datto BCDR sees (protected by an Agent record)
datto_protected = devices where inspectors contains "datto-bcdr-inspector"

# Servers Liongard knows but Datto doesn't see → unprotected candidates
unprotected = devices where class == "server"
                            AND inspectors does not contain "datto-bcdr-inspector"
```

---

## Metrics and queries

### Per-agent detail (for the all-backups.md join)

```jmespath
Assets[*].{
  name: name,
  hoursSinceBackup: HoursSinceLastSuccessfulBackup_r,
  status: lastBackupStatus
}
```

> **Field notes (VALIDATED 2026-05-27):** Array is `Assets[*]` (not `Agents`).
> Hostname field is `name` (not `machineName`). Backup age is
> `HoursSinceLastSuccessfulBackup_r` (integer, unit = hours; `_r` = raw value
> from API). `protectedSizeGB` is not confirmed in dataprint — omit or mark
> PROPOSED. `lastBackupStatus` — confirm field presence on a live system before
> relying on it.

### Cloud sync (3-2-1 compliance)

> **Data gap (2026-05-27):** `cloudSyncStatus` and `lastOffsiteSnapshotTime` are
> NOT present in the Datto BCDR dataprint. Cloud sync state must be verified in
> the Datto Partner Portal. Surface in the Manual Verification appendix.

```jmespath
# No dataprint fields for cloud sync — use portal verification
# Reference the assets that are expected to be synced:
Assets[*].name
```

### Screenshot verification

```jmespath
Assets[*].{
  name: name,
  screenshotStatus: lastScreenshotAttemptStatus
}
```

> **Field note (VALIDATED 2026-05-28):** Field is `lastScreenshotAttemptStatus`
> and returns a **boolean** — `true` = screenshot succeeded, `false` = screenshot
> failed. It is NOT a string status. Filter for failures with:
> `Assets[?lastScreenshotAttemptStatus == \`false\`]`.
> `lastScreenshotTime` — presence not confirmed in dataprint; use portal for timestamp.

### Time-series — failure trend / agent count

```
# Overdue-backup count trend (machines with HoursSinceLastSuccessfulBackup_r > 24)
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="length(Assets[?HoursSinceLastSuccessfulBackup_r > `24`])"
```

---

## QA & Manual Verification

Run the QA pass per `reference/qa-retry-pattern.md` before rendering output:

1. **Retry persistent nulls.** Datto API throttling can produce
   transient null `Assets` arrays — retry up to `qa.retry_attempts`
   times.

2. **Flag stale inspector data.** Datto inspector lastSeen > 1 day =
   API key / partner-portal scope issue.

3. **Cross-tool divergence.** Datto-protected machines (via `Assets[*].
   name`) should reconcile with the device inventory's "servers
   with Datto in inspectors[]". Divergence = a Datto-protected machine
   that no other inspector sees — usually a server-OS inspector hasn't
   been deployed, OR an orphaned Datto agent on a decommissioned server.

4. **Missing catalog metrics** — several Datto BCDR fields have no catalog
   metric. The JMESPath queries in this recipe evaluate the raw `Assets[]`
   array directly. Surface any gaps in the manual-verification appendix.

5. **Manual Verification appendix** — render in the deliverable. Typical
   items for this recipe:
   - **Several Datto BCDR fields require portal review** — direct readers
     to the Datto Partner Portal for cloud sync, appliance storage, and
     screenshot verification confirmation.
   - Assets with `HoursSinceLastSuccessfulBackup_r > 24` (escalate).
   - Screenshot verification failed — `Assets[?lastScreenshotAttemptStatus == \`false\`]`
     non-empty (`lastScreenshotAttemptStatus` is a boolean: `true`=ok, `false`=failed).
   - Cloud sync not confirmed in dataprint — must verify via Datto
     Partner Portal (breaks the 3-2-1 promise if stalled).

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Overdue backups | `Assets[?HoursSinceLastSuccessfulBackup_r > \`24\`]` non-empty | "<N> machines have not successfully backed up in 24h+ — escalate." |
| Screenshot verification failed | `Assets[?lastScreenshotAttemptStatus == \`false\`]` non-empty | "<N> machines have failed screenshot-verification — review in Datto Partner Portal." |
| Cloud sync not verified | `cloudSyncStatus` absent from dataprint | "Cloud sync state requires portal verification — confirm 3-2-1 compliance in Datto Partner Portal." |
| Missing catalog metrics | JMESPath workarounds active; verify via Datto Partner Portal | "Datto BCDR detail metrics not yet in catalog — use JMESPath queries and portal confirmation." |
| Stale Datto inspector | `lastSeen > 1 day` | "Datto inspector hasn't reported in <N> days — confirm API key / partner-portal scope." |


---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Most Datto BCDR detail fields | ⚠️ no catalog metric — use direct JMESPath on `Assets[]` | Datto Partner Portal — manual review |
| Screenshot verification state | ⚠️ no catalog metric | Datto Partner Portal |
| Cloud sync / offsite replication | ⚠️ no catalog metric | Datto Partner Portal |
| Appliance storage utilization | ⚠️ no catalog metric | Datto Partner Portal |
| Datto SaaS Backup state (separate product) | ❌ not in this inspector | Use `microsoft-365` recipe + Datto SaaS portal |
| Restore test history | ❌ not in dataprint | MSP runbook |


---

## Output format

Markdown / Word / Excel per `output.format`.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_system LIST | query="datto" envId=<ENV_ID> | array<system> | ok |
| 3 | liongard_metric EVALUATE | jmesPath Assets[*].{name:name, hoursSinceBackup:HoursSinceLastSuccessfulBackup_r} sysId=<SYS_ID> envId=<ENV_ID> | array<object> | VALIDATED — array name confirmed Assets (not Agents); hostname field confirmed `name`; backup age field confirmed `HoursSinceLastSuccessfulBackup_r` |
| 4 | liongard_device LIST | envId=<ENV_ID> class=server fields=[...] | array<device> | ok |
| 5 | (QA pass) retry + divergence checks + proposed-metric surfacing | per `reference/qa-retry-pattern.md` | varies | ok |
```

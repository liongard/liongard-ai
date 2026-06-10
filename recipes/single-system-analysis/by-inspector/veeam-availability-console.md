---
name: single-system-veeam-availability-console
description: >
  Use this skill when the user wants a single-tenant analysis of a Veeam
  Availability Console — per-tenant backup job inventory, last-run
  status, repository capacity, agent inventory. VAC is Veeam's
  MSP-oriented orchestration product for managed-customer backups.
  Trigger phrases: "Veeam VAC review", "Veeam Availability Console
  PBR", "pull Veeam backup data", "Veeam tenant audit", "VAC backup
  job status".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, xlsx]
primitives:
  - metrics:veeam-availability-console:backup-server-license-expiration-list
  - metrics:veeam-availability-console:license-expiration-date
  - metrics:veeam-availability-console:portal-administrator-list
  - metrics:veeam-availability-console:unhealthy-repositories-count
  - metrics:veeam-availability-console:unhealthy-repositories-list
---

# Single-System Analysis — Veeam Availability Console (VAC)

> **Inspector:** `veeam-availability-console-inspector` (ID 35). Apps &
> Services category. Backup / DR. MSP-oriented orchestration.
>
> **Parent/child:** Yes. Parent (the VAC installation) holds account
> identity; each child represents one MSP-managed customer tenant —
> identified by `BackupRepositories[0].companyName`.
>
> **Naming gotcha — two Veeam inspectors exist.** Always confirm with
> the user which they mean:
> - `veeam-availability-console-inspector` (this one, ID 35) — VAC
> - `veeam-service-provider-console-inspector` (ID 75) — VSPC
>
> **References:** `reference/inspector-aliases.md` (Veeam VAC, VAC,
> "Veeam Availability Console"). **Pairs with
> `recipes/system-type-assessment/all-backups.md`** for cross-vendor
> coverage rollup.


---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-veeam-vac-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  job_inventory: "Per-Tenant Backup Job Inventory"
  failed_jobs: "Failed Jobs"
  repository_capacity: "Repository Capacity"
  protected_servers: "Per-Protected-Server Backup State"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 1
  failed_jobs_max: 0
  hours_since_last_successful_max: 24
  repository_capacity_warn_percent: 80

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

- "Pull Veeam VAC data for the customer" (PBR)
- "Veeam backup job status review"
- "Veeam repository capacity check"
- "Veeam failed-job audit"

Personas: NOC, vCIO/AM, TAM.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Veeam VAC child system ID | Yes | `liongard_system LIST query="veeam"` |
| Reporting period | No | Default per customization |

---

## Locating the right system

```
liongard_system LIST searchMode=keyword query="veeam" environmentId=<ENV_ID>
```

| Shape | What it is | Action |
|---|---|---|
| `LicenseSettings.productName == "Veeam Availability Console"` | **Parent** — VAC installation account-level view | Skip for per-customer reports |
| `BackupRepositories[0].companyName` returns one tenant | **Child** — per-customer | Use this |

> **Be explicit with `veeam-availability-console`** — bare `veeam` may
> return both VAC and VSPC systems. The Liongard inspector slug is
> the disambiguation key.


---

## Liongard data sources

### Per-vendor data — VAC dataprint top-level keys

| Key | Description |
|---|---|
| `LicenseSettings` | VAC product / license identifier (parent system) |
| `BackupRepositories` | Storage repositories — `BackupRepositories[0].companyName` identifies the tenant on the child |
| `Backups` | Per-job backup definitions; each `Backups[*].objects[*]` contains the protected hostnames |
| `Computers` | Per-protected-computer inventory with agent-state detail |

#### Field gotchas (inline notes — not TODO)

- **Parent vs. child distinction** — parent has
  `LicenseSettings.productName == "Veeam Availability Console"`; child
  has `BackupRepositories[0].companyName` for one tenant. Target the
  child for per-customer reports.
- **Disambiguate from VSPC.** Veeam Service Provider Console
  (`veeam-service-provider-console-inspector` ID 75) is a separate
  inspector with similar concepts but different shape. Confirm with
  user which product the customer runs.
- **`Backups[*].objects[*]` is the hostname-join source.** A job
  typically protects multiple servers — the `objects` array enumerates
  each. For the `all-backups.md` hostname join, flatten across all jobs
  and dedupe by hostname.

### Cross-inspector cross-check — device inventory

```
liongard_device LIST environmentId=<ENV_ID> class="server"
                     fields=["hostname","inspectors","operatingSystem"]
```

```
veeam_protected = devices where inspectors contains "veeam-availability-console-inspector"
unprotected = devices where class == "server"
                            AND inspectors does not contain "veeam-availability-console-inspector"
```

---

## Metrics and queries

### Proposed metrics (VAC — most fields)

| Field | Workaround |
|---|---|
| Per-tenant backup job inventory composite | Client-side parse of `Backups[*]` |
| Failed job count | Client-side `length(Backups[?lastResult == 'Failed'])` |
| Repository capacity status | Manual confirm in VAC console |
| Repository >80% utilized list | Manual confirm in VAC console |
| Per-server last backup (the all-backups.md join key) | Client-side parse of `Backups[*].objects[*]` |

### Per-job snapshot

```jmespath
Backups[*].{
  name: name,
  status: lastResult,
  lastRun: lastRunTime,
  nextRun: nextRunTime,
  scheduleType: scheduleType
}
```

### Per-protected-server (for the all-backups.md join)

```jmespath
Backups[*].objects[*].{
  hostname: name,
  lastBackup: lastRunTime,
  jobName: parent_job_name
}
```

### Repository capacity

```jmespath
BackupRepositories[*].{
  name: name,
  capacityGB: capacityGB,
  freeGB: freeGB,
  percentUsed: percentUsed
}
```

### Time-series — failure / capacity trend

```
# Failed-job count trend
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="length(Backups[?lastResult == `Failed`])"

# Repository capacity trend
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="BackupRepositories[*].percentUsed"
```

---

## QA & Manual Verification

Run the QA pass per `reference/qa-retry-pattern.md` before rendering output:

1. **Retry persistent nulls.** Retry up to `qa.retry_attempts` times.

2. **Flag stale inspector data.** VAC inspector lastSeen > 1 day = API
   / connectivity issue.

3. **Cross-tool divergence.** VAC `Backups[*].objects[*].name` (deduped)
   should reconcile with device-inventory servers having Veeam in
   `inspectors[]`. Divergence = job-name-vs-hostname mismatch or stale
   data.

4. **Proposed-metric gaps for this recipe** — surface in the
   manual-verification appendix (see workaround table above).

5. **Manual Verification appendix** — render in the deliverable. Typical
   items for this recipe:
   - Jobs in Failed state.
   - Repositories approaching capacity (`percentUsed > slas.repository_capacity_warn_percent`).
   - Objects in backup jobs that don't match any server in the device
     inventory (job-naming vs. hostname mismatch — common with
     image-level VM backups).

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Failed jobs | `length(Backups[?lastResult == 'Failed']) > 0` | "<N> jobs in Failed state — investigate the source / target / agent." |
| Repository >80% utilized | any `BackupRepositories[?percentUsed > 80]` | "Repository <name> at <pct>% — provision storage before exhaustion." |
| Job has no recent run | `Backups[?lastRunTime < (today - 24h)]` non-empty | "<N> jobs haven't completed in 24h+ — escalate." |
| Veeam-protected hostname unknown to device inventory | object name doesn't match | "Veeam protects <hostname> but no matching server in inventory — confirm intentional or remove orphaned job." |
| Stale VAC inspector | `lastSeen > 1 day` | "VAC inspector hasn't reported in <N> days — confirm API access." |


---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Most VAC detail fields | ⚠️ not in dataprint metrics | VAC console |
| Cloud Connect repository state | ❌ not in dataprint | VAC console |
| Immutability posture per repository | ❌ not in dataprint | VAC console |
| Restore test history | ❌ not in dataprint | MSP runbook |
| Per-VM (vs. per-job) last-backup detail | ⚠️ not in dataprint | Client-side dedupe via `Backups[*].objects[*]` |


---

## Output format

Markdown / Word / Excel per `output.format`.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_system LIST | query="veeam-availability-console" envId=<ENV_ID> | array<system> | ok |
| 3 | liongard_metric EVALUATE | jmesPath Backups[*]... sysId=<SYS_ID> envId=<ENV_ID> | <array> | ok |
| 4 | liongard_metric EVALUATE | jmesPath BackupRepositories[*]... sysId=<SYS_ID> envId=<ENV_ID> | <array> | ok |
| 5 | liongard_device LIST | envId=<ENV_ID> class=server fields=[...] | array<device> | ok |
| 6 | (QA pass) retry + divergence checks | per `reference/qa-retry-pattern.md` | varies | ok |
```

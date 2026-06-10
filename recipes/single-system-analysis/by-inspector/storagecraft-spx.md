---
name: single-system-storagecraft-spx
description: >
  Use this skill when the user wants a single-server analysis of a
  StorageCraft SPX installation — per-job backup status, retention
  policy, last-valid-backup time, license / product key audit. Unlike
  other backup inspectors, SPX inspects one protected server per
  Liongard system (not a multi-tenant console). Trigger phrases:
  "StorageCraft SPX review", "SPX backup audit", "pull SPX data",
  "ShadowProtect review". Produces an artifact in the format set in the
  customization block.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, xlsx]
primitives:
  # Reconciled 2026-05-29: pruned dangling refs not present in the live dataprint (see internal/proposed-metrics-backlog.md).
  - metrics:storagecraft-spx-inspector:days-until-license-expiration
  - metrics:storagecraft-spx-inspector:last-backup-attempt-failed-count
  - metrics:storagecraft-spx-inspector:last-backup-attempt-failed-list
  - metrics:storagecraft-spx-inspector:last-successful-backup
  - metrics:storagecraft-spx-inspector:software-version
---

# Single-System Analysis — StorageCraft SPX

> **Inspector:** `storagecraft-spx-inspector` (ID 46). Apps & Services
> category. Backup / DR. **Single-server inspector** — one protected
> server per Liongard system (no parent/child, no multi-tenant
> console).
>
> **References:** `reference/inspector-aliases.md` (SPX, StorageCraft,
> ShadowProtect). **Pairs with
> `recipes/system-type-assessment/all-backups.md`** for cross-vendor
> coverage rollup.


---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<hostname>-storagecraft-spx-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  identity: "SPX Identity & License"
  jobs: "Backup Jobs"
  failed_jobs: "Failed Jobs"
  retention: "Retention Compliance"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 1
  failed_jobs_max: 0
  hours_since_last_successful_max: 24

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

- "Pull SPX data for the server"
- "StorageCraft SPX backup audit"
- "Is the SPX job still running successfully?"
- Pre-decommission audit — confirm last valid backup before
  decommissioning a server

Personas: NOC, vCIO/AM, TAM.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| SPX system ID | Yes | `liongard_system LIST query="storagecraft"` |
| Hostname (alternative) | If no system ID | Match by `SystemInfo.Hostname` |
| Reporting period | No | Default per customization |

---

## Locating the right system

```
liongard_system LIST searchMode=keyword query="storagecraft" environmentId=<ENV_ID>
```

`SystemInfo.Hostname` is the protected server's hostname (one server
per SPX system in Liongard — if a customer has 10 SPX-protected servers,
10 SPX systems will appear).


---

## Liongard data sources

> **Asset Inventory First, Metric Cross-Check.** The SPX inspector
> reports one server's backup state. The cross-inspector
> `liongard_device` confirms the same hostname is also reported by a
> server-OS inspector (good data-quality check).

### Per-vendor data — SPX dataprint top-level keys

| Key | Description |
|---|---|
| `SystemInfo` | This SPX server's identity — `Hostname`, `ProductKey`, `SystemOS` |
| `System` | Same hostname identifier in lowercase path |
| `Jobs` | Backup job array for this server |
| `License` | SPX license / product key |

#### Field gotchas (inline notes — not TODO)

- **Single-server inspector.** Unlike Datto BCDR / Cove / Acronis /
  Axcient / Veeam VAC / Veeam VSPC, the StorageCraft SPX inspector
  represents ONE protected server per Liongard system. If the customer
  has 10 servers backed up via SPX, there will be 10 SPX systems in
  Liongard. The `all-backups.md` hostname join is one-to-one for SPX.
- **`SystemInfo.Hostname` is both the SPX-installation identifier AND
  the protected-server hostname.** The `all-backups.md` join key is
  straightforward — no parent/child traversal needed.

### Cross-inspector cross-check — device inventory

```
liongard_device LIST hostname=<this SPX hostname> environmentId=<ENV_ID>
                     fields=["hostname","inspectors","operatingSystem"]
```

```
# Confirm this server is also reported by a server-OS inspector
# (good data-quality check — SPX should be alongside Windows / Linux
# inspector)
device = devices where Hostname matches SPX's SystemInfo.Hostname
expected_inspectors = ["storagecraft-spx-inspector", "windows-server-inspector"]
                      # OR linux-inspector / macos-inspector
```

---

## Metrics and queries

### Proposed metrics (SPX — most fields)

| Field | Workaround |
|---|---|
| Per-job status composite | Client-side parse of `Jobs[*]` |
| Failed job count | Client-side `length(Jobs[?lastResult == 'Failed'])` |
| Hours since last successful backup | Client-side `max()` over `Jobs[*]` |
| Backup image retention compliance | Manual confirm in SPX console |

### Per-job snapshot

```jmespath
Jobs[*].{
  name: name,
  status: lastResult,
  lastRun: lastRunTime,
  nextRun: nextRunTime,
  retention: retentionDays
}
```

### Failed jobs

```jmespath
Jobs[?lastResult == `Failed`].{
  name: name,
  lastRun: lastRunTime,
  failureReason: lastErrorMessage
}
```

### Retention compliance

```jmespath
Jobs[*].{
  name: name,
  retentionDays: retentionDays,
  oldestImageAge: oldestImageDays
}
```

### Time-series — failure trend

```
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="length(Jobs[?lastResult == `Failed`])"
```

---

## QA & Manual Verification

Run the QA pass per `reference/qa-retry-pattern.md` before rendering output:

1. **Retry persistent nulls.** Retry up to `qa.retry_attempts` times.

2. **Flag stale inspector data.** SPX inspector lastSeen > 1 day = SPX
   service down or Liongard agent connectivity issue on the protected
   server.

3. **Cross-tool divergence.** Confirm the SPX `SystemInfo.Hostname` is
   also reported by a server-OS inspector via `liongard_device`. If
   only SPX sees this hostname, there's a data-quality issue (server-OS
   inspector should also be deployed).

4. **Proposed-metric gaps for this recipe** — surface in the
   manual-verification appendix.

5. **Manual Verification appendix** — render in the deliverable.
   Typical items:
   - Jobs in Failed state (escalate immediately — single-server SPX
     means a failure here = this server is unprotected).
   - Retention compliance (oldest image age vs. configured retention
     days).
   - License / product key validity (if `License` field is null or
     expired).

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Failed jobs | `length(Jobs[?lastResult == 'Failed']) > 0` | "**Critical:** <hostname> has failed SPX jobs — this server has no working backup." |
| Stale backup | max hours since last successful > 24 | "<hostname>'s last successful backup is <N> hours old — investigate." |
| Retention drift | `oldestImageDays > retentionDays * 1.1` | "<hostname>'s SPX retention is over configured policy — confirm intentional or clean up." |
| Cross-inspector data quality | SPX hostname not reported by a server-OS inspector | "<hostname> appears in SPX but no matching server-OS inspector — deploy Windows Server / Linux / macOS inspector for full posture." |
| License expired / invalid | `License` field is null or `License.status == 'Expired'` | "SPX license issue on <hostname> — renew before next backup window." |
| Stale SPX inspector | `lastSeen > 1 day` | "SPX inspector hasn't reported in <N> days — confirm SPX service + Liongard agent on the protected server." |


---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Per-job composite metric | ⚠️ not in dataprint | Client-side parse |
| Retention enforcement detail | ⚠️ partial — `retentionDays` available, `oldestImageDays` proposed | SPX console |
| ImageManager replication status | ❌ not in dataprint | ImageManager console (separate SPX product) |
| VirtualBoot test history | ❌ not in dataprint | SPX console + MSP runbook |
| Restore test history | ❌ not in dataprint | MSP runbook |


---

## Output format

Markdown / Word / Excel per `output.format`. Per-server SPX recipes are
typically aggregated in `all-backups.md` for a fleet view; this recipe
is the per-server deep dive.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_system LIST | query="storagecraft" envId=<ENV_ID> | array<system> | ok |
| 3 | liongard_metric EVALUATE | jmesPath Jobs[*]... sysId=<SYS_ID> envId=<ENV_ID> | <array> | ok |
| 4 | liongard_device LIST | hostname=<SPX server hostname> envId=<ENV_ID> | array<device> | ok |
| 5 | (QA pass) retry + divergence checks | per `reference/qa-retry-pattern.md` | varies | ok |
```

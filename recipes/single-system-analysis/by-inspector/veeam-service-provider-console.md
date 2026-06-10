---
name: single-system-veeam-service-provider-console
description: >
  Use this skill when the user wants a single-tenant analysis of a Veeam
  Service Provider Console — per-tenant backup job inventory, last-run
  status, agent + cloud-tenant inventory. VSPC is Veeam's
  service-provider orchestration product (successor / variant of VAC
  for the service-provider tier). Trigger phrases: "Veeam VSPC review",
  "Service Provider Console PBR", "pull Veeam VSPC data", "VSPC backup
  audit".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, xlsx]
primitives:
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
---

# Single-System Analysis — Veeam Service Provider Console (VSPC)

> **Inspector:** `veeam-service-provider-console-inspector` (ID 75).
> Apps & Services category. Virtual Server Backup. Service-provider
> orchestration (successor / variant of VAC).
>
> **Parent/child:** Yes. Each child represents one MSP-managed tenant.
>
> **Naming gotcha — two Veeam inspectors exist.** Always confirm with
> the user which they mean:
> - `veeam-availability-console-inspector` (ID 35) — VAC
> - `veeam-service-provider-console-inspector` (this one, ID 75) — VSPC
>
> **References:** `reference/inspector-aliases.md` (VSPC, "Veeam
> Service Provider Console"). **Pairs with
> `recipes/system-type-assessment/all-backups.md`** for cross-vendor
> coverage rollup.


---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-veeam-vspc-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  job_inventory: "Per-Tenant Backup Job Inventory"
  failed_jobs: "Failed Jobs"
  cloud_tenants: "Cloud Tenant Quota & Utilization"
  protected_agents: "Per-Agent Backup State"
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

- "Pull Veeam VSPC data for the customer" (PBR)
- "VSPC backup job status review"
- "VSPC cloud-tenant quota check"
- "VSPC failed-job audit"

Personas: NOC, vCIO/AM, TAM.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Veeam VSPC child system ID | Yes | `liongard_system LIST query="veeam-spc"` |
| Reporting period | No | Default per customization |

---

## Locating the right system

```
liongard_system LIST searchMode=keyword query="veeam-spc" environmentId=<ENV_ID>
```

`Tenant.name` returns the tenant identifier for the child VSPC system.

> **Be explicit with `veeam-spc` (or `veeam-service-provider-console`)** —
> bare `veeam` may return both VAC and VSPC systems. The Liongard
> inspector slug is the disambiguation key.


---

## Liongard data sources

### Per-vendor data — VSPC dataprint top-level keys

| Key | Description |
|---|---|
| `Tenant` | Tenant identifier (`Tenant.name`) for the child VSPC system |
| `BackupJobs` | Job inventory with last-run state |
| `CloudTenants` | Storage quota allocation per cloud tenant |
| `Agents` | Per-protected-machine inventory |

#### Field gotchas (inline notes — not TODO)

- **VAC vs. VSPC distinction.** Veeam has two separate inspectors —
  VAC (ID 35, target "Backup / DR") and VSPC (ID 75, target "Virtual
  Server Backup"). They cover similar concepts with different
  dataprint shapes. Confirm with user which product the customer
  actually runs.

### Cross-inspector cross-check — device inventory

```
liongard_device LIST environmentId=<ENV_ID> class="server"
                     fields=["hostname","inspectors","operatingSystem"]
```

```
vspc_protected = devices where inspectors contains "veeam-service-provider-console-inspector"
unprotected = devices where class == "server"
                            AND inspectors does not contain "veeam-service-provider-console-inspector"
```

---

## Metrics and queries

### Proposed metrics (VSPC — most fields)

| Field | Workaround |
|---|---|
| Per-tenant backup job inventory composite | Client-side parse of `BackupJobs[*]` |
| Failed job count | Client-side `length(BackupJobs[?lastResult == 'Failed'])` |
| Cloud tenant quota / utilization | Manual confirm in VSPC console |
| Per-agent backup state | Client-side parse of `Agents[*]` |

### Per-job snapshot

```jmespath
BackupJobs[*].{
  name: name,
  status: lastResult,
  lastRun: lastRunTime,
  scheduleType: scheduleType
}
```

### Cloud tenant inventory

```jmespath
CloudTenants[*].{
  name: name,
  quotaGB: quotaGB,
  usedGB: usedGB
}
```

### Per-agent (for the all-backups.md join)

```jmespath
Agents[*].{
  hostname: hostname,
  lastBackup: lastBackupTime,
  status: status
}
```

### Time-series — failure / quota trend

```
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="length(BackupJobs[?lastResult == `Failed`])"
```

---

## QA & Manual Verification

Run the QA pass per `reference/qa-retry-pattern.md` before rendering output:

1. **Retry persistent nulls.** Retry up to `qa.retry_attempts` times.

2. **Flag stale inspector data.** VSPC inspector lastSeen > 1 day =
   API access issue.

3. **Cross-tool divergence.** VSPC `Agents[*].hostname` should
   reconcile with device-inventory servers having VSPC in
   `inspectors[]`.

4. **Proposed-metric gaps for this recipe** — surface in the
   manual-verification appendix.

5. **Manual Verification appendix** — render in the deliverable.
   Typical items:
   - Jobs in Failed state.
   - Cloud tenants approaching quota.
   - Agents not present in device inventory (orphaned protection).

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Failed jobs | `length(BackupJobs[?lastResult == 'Failed']) > 0` | "<N> jobs in Failed state — investigate." |
| Cloud tenant near quota | any `CloudTenants[?usedGB / quotaGB > 0.8]` | "Cloud tenant <name> at <pct>% of quota — provision additional capacity." |
| Orphaned agent | VSPC `Agents[*].hostname` not in device inventory | "VSPC protects <hostname> but no matching server in inventory — confirm intentional." |
| Stale VSPC inspector | `lastSeen > 1 day` | "VSPC inspector hasn't reported in <N> days — confirm API access." |


---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Most VSPC detail fields | ⚠️ not in dataprint metrics | VSPC console |
| Cloud Connect repository state | ❌ not in dataprint | VSPC console |
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
| 2 | liongard_system LIST | query="veeam-spc" envId=<ENV_ID> | array<system> | ok |
| 3 | liongard_metric EVALUATE | jmesPath BackupJobs[*]... sysId=<SYS_ID> envId=<ENV_ID> | <array> | ok |
| 4 | liongard_device LIST | envId=<ENV_ID> class=server fields=[...] | array<device> | ok |
| 5 | (QA pass) retry + divergence checks | per `reference/qa-retry-pattern.md` | varies | ok |
```

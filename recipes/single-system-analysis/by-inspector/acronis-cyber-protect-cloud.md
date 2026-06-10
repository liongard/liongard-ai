---
name: single-system-acronis-cyber-protect-cloud
description: >
  Use this skill when the user wants a single-tenant analysis of an
  Acronis Cyber Protect Cloud account — per-resource backup state,
  backup plan compliance, last-run status per resource, child-tenant
  inventory. Acronis Cyber Protect Cloud combines backup, EDR, and
  DLP — this recipe covers the backup portion. Trigger phrases:
  "Acronis backup review", "Acronis Cyber Protect PBR", "pull Acronis
  backup data", "Acronis tenant audit", "Acronis Cyber Protect Cloud
  report".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_launchpoint, liongard_metric, liongard_device"
personas: [noc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, xlsx]
primitives:
  - metrics:acronis-cyber-protect-cloud:count-of-machines
  - metrics:acronis-cyber-protect-cloud:count-of-machines-not-backed-up-24h
  - metrics:acronis-cyber-protect-cloud:count-of-machines-with-backup-enabled
  - metrics:acronis-cyber-protect-cloud:list-of-machines-backed-up-30d
  - metrics:acronis-cyber-protect-cloud:list-of-machines-not-backed-up-24h
  - metrics:acronis-cyber-protect-cloud:list-of-machines-not-backed-up-30d
  - metrics:acronis-cyber-protect-cloud:list-of-machines-with-backup-enabled
  - metrics:acronis-cyber-protect-cloud:list-of-machines-without-backup-enabled
  - metrics:acronis-cyber-protect-cloud:local-storage-used-bytes
  - metrics:acronis-cyber-protect-cloud:machine-backup-summary
---

# Single-System Analysis — Acronis Cyber Protect Cloud

> **Inspector:** `acronis-cyber-protect-cloud-inspector` (ID 93). Cloud
> category. Backup / DR (with optional EDR + DLP modules).
>
> **Parent/child:** Yes. Parent has `ChildTenants[*]`; child has
> `Resources[*]` for one customer tenant.
>
> **References:** `reference/inspector-aliases.md` (Acronis, ACP,
> "Acronis Cyber Protect", "Acronis Cyber Cloud"). **Pairs with
> `recipes/system-type-assessment/all-backups.md`** for cross-vendor
> coverage rollup.


---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-acronis-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  tenant_inventory: "Child Tenant Inventory"
  resource_coverage: "Per-Resource Backup State"
  failed_backups: "Failed Backups"
  unplanned_resources: "Resources Without a Backup Plan"
  capacity: "Storage Utilization"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 1
  failed_backups_max: 0
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

- "Pull Acronis backup data for the customer" (PBR)
- "Acronis Cyber Protect tenant audit"
- "Any Acronis backups failing?"
- "Acronis resources without a backup plan"

Personas: NOC, vCIO/AM, TAM.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Acronis child system ID | Yes | `liongard_launchpoint LIST inspectorId=93` |
| Reporting period | No | Default per customization |

---

## Locating the right system

```
liongard_launchpoint LIST inspectorId=93 environmentIds=[<ENV_ID>]
```

| Shape | What it is | Action |
|---|---|---|
| Has `ChildTenants[*]` (customer tenants enumerated) | **Parent** — partner-level rollup | Skip for per-customer reports |
| Has `Resources[*]` for one tenant | **Child** — per-customer | Use this |

Both use `Account.name` as the identifier — disambiguate via the
dataprint shape (parent has `ChildTenants`, child has `Resources`).


---

## Liongard data sources

### Per-vendor data — Acronis dataprint top-level keys

| Key | Description |
|---|---|
| `Account` | Tenant identity — `Account.name` (partner or customer name within Acronis) |
| `ChildTenants` | Parent — array of customer tenants the partner manages |
| `Resources` | Child — array of protected resources (machines, M365 mailboxes, etc.) with backup state |
| `BackupPlans` | Plan definitions (schedule, retention, scope) |

#### Field gotchas (inline notes — not TODO)

- **Parent vs. child distinction** — see the "Locating the right system"
  table above.
- **`Resources[*].type` covers multiple protection classes** —
  machines (workstation/server), M365 user mailboxes, M365 SharePoint,
  Google Workspace, websites. The `all-backups.md` join only cares
  about machine-type resources; filter `Resources[?type contains
  'machine']`.

### Cross-inspector cross-check — device inventory

```
liongard_device LIST environmentId=<ENV_ID> class="server"
                     fields=["hostname","inspectors","operatingSystem"]
```

```
acronis_protected = devices where inspectors contains "acronis-cyber-protect-cloud-inspector"
unprotected = devices where class == "server"
                            AND inspectors does not contain "acronis-cyber-protect-cloud-inspector"
```

---

## Metrics and queries

### MCP-validated metrics and queries

The Acronis Cyber Cloud inspector has first-class metrics for machine
backup coverage and recency. Backup state is modeled on each resource's
`policies[]` array, not as top-level `lastRunStatus`, `lastRunTime`, or
`planName` fields.

| Field | Metric / source |
|---|---|
| Child tenant enumeration (parent) | Client-side parse of `ChildTenants[*].name` |
| Count of machines | metricName="Acronis Cyber Cloud: Count of Machines" |
| Count of machines with backup enabled | metricName="Acronis Cyber Cloud: Count of Machines with Backup Enabled" |
| List of machines with backup enabled | metricName="Acronis Cyber Cloud: List of Machines with Backup Enabled" |
| List of machines without backup enabled | metricName="Acronis Cyber Cloud: List of Machines without Backup Enabled" |
| Machine backup summary | metricName="Acronis Cyber Cloud: Machine Backup Summary" — policy `last_run`, `last_success_run`, and `next_run` |
| Count not successfully backed up in last 24 hours | metricName="Acronis Cyber Cloud: Count of Machines Not Successfully Backed Up In Last 24 Hours" |
| List not successfully backed up in last 24 hours | metricName="Acronis Cyber Cloud: List of Machines Not Successfully Backed Up In Last 24 Hours" |
| List successfully backed up in last 30 days | metricName="Acronis Cyber Cloud: List of Machines Successfully Backed Up In Last 30 days" |
| List not successfully backed up in last 30 days | metricName="Acronis Cyber Cloud: List of Machines NOT Successfully Backed Up In Last 30 days" |
| Local storage used | metricName="Acronis Cyber Cloud: Local Storage Used (Bytes)" |
| Backup plan inventory + retention | Manual confirm in Acronis Management Portal; `BackupPlans[*]` was not present in sampled MCP dataprints |

Validated JMESPath reference:

```jmespath
machine_count:
Resources[?type == `resource.machine`] | length(@)

backup_enabled_count:
Resources[?type == `resource.machine` && policies[?type == `policy.backup.machine`]] | length(@)

machines_without_backup_enabled:
Resources[?type == `resource.machine` && (!policies || !contains(policies[].type, `policy.backup.machine`))].name || `-`

local_storage_used:
Usages[].usages[?usage_name == `local_storage`].value
```

### Per-resource detail (for the all-backups.md join)

```jmespath
Resources[*].{
  name: name,
  type: type,
  backup_policy: policies[?type == `policy.backup.machine`].type | [0],
  last_run: policies[?type == `policy.backup.machine`].last_run | [0],
  last_success_run: policies[?type == `policy.backup.machine`].last_success_run | [0],
  next_run: policies[?type == `policy.backup.machine`].next_run | [0]
}
```

### Backup coverage and recency

```jmespath
{
  machine_count: length(Resources[?type == `resource.machine`]),
  backup_enabled_count: length(Resources[?type == `resource.machine` && policies[?type == `policy.backup.machine`]]),
  unprotected_machines: Resources[?type == `resource.machine` && (!policies || !contains(policies[].type, `policy.backup.machine`))].name,
  not_successfully_backed_up_24h: Resources[?type == `resource.machine` && policies[?type == `policy.backup.machine`] && policies[?type == `policy.backup.machine`].last_success_run && (time_since(policies[?type == `policy.backup.machine`].last_success_run | [0], 'hours') > `24`)].name
}
```

### Time-series — backup recency trend

```
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="Resources[?type == `resource.machine` && policies[?type == `policy.backup.machine`] && policies[?type == `policy.backup.machine`].last_success_run && (time_since(policies[?type == `policy.backup.machine`].last_success_run | [0], 'hours') > `24`)] | length(@)"
```

---

## QA & Manual Verification

Run the QA pass per `reference/qa-retry-pattern.md` before rendering output:

1. **Retry persistent nulls.** Retry up to `qa.retry_attempts` times.

2. **Flag stale inspector data.** Acronis API-driven; lastSeen > 1 day
   = API access issue.

3. **Cross-tool divergence.** Acronis `Resources[*].name` (filtered to
   machine-type) should reconcile with device-inventory servers with
   Acronis in `inspectors[]`. Divergence = naming mismatch or stale
   data.

4. **Manual-only gaps for this recipe** — surface in the
   manual-verification appendix (see table above).

5. **Manual Verification appendix** — render in the deliverable. Typical
   items for this recipe:
   - `BackupPlans[*]` was not present in MCP-validated dataprints —
     confirm plan schedule / retention in the Acronis Management Portal.
   - Machines without `policy.backup.machine` attached (coverage gap).
   - Machines not successfully backed up in the last 24 hours.
   - Storage utilization from metricName=`Acronis Cyber Cloud: Local Storage Used (Bytes)`; manually confirm if null or
     if the portal shows a different capacity figure.

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Stale backups | metricName=`Acronis Cyber Cloud: Count of Machines Not Successfully Backed Up In Last 24 Hours` > 0 | "<N> machines have not successfully backed up in the last 24 hours — investigate plan / agent / target." |
| Unprotected machines | metricName=`Acronis Cyber Cloud: List of Machines without Backup Enabled` not empty | "<N> machine resources are registered with Acronis but do not have machine backup enabled — assign a backup policy or remove the resource." |
| Acronis-protected hostname unknown to device inventory | a resource's `name` doesn't match any device record | "Acronis protects <hostname> but no matching server in inventory — confirm intentional or remove orphaned plan." |
| Stale Acronis inspector | `lastSeen > 1 day` | "Acronis inspector hasn't reported in <N> days — confirm API access." |


---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Backup policy coverage and recency | ✅ existing metrics metricName=`Acronis Cyber Cloud: Count of Machines`, metricName=`Acronis Cyber Cloud: List of Machines without Backup Enabled`, metricName=`Acronis Cyber Cloud: Machine Backup Summary`, metricName=`Acronis Cyber Cloud: List of Machines Not Successfully Backed Up In Last 24 Hours`, metricName=`Acronis Cyber Cloud: List of Machines Successfully Backed Up In Last 30 days`, metricName=`Acronis Cyber Cloud: List of Machines NOT Successfully Backed Up In Last 30 days` | Acronis Management Portal for dispute resolution |
| Local storage utilization | ✅ metricName=`Acronis Cyber Cloud: Local Storage Used (Bytes)` | Acronis Management Portal for dispute resolution |
| Backup plan inventory + retention | ⚠️ not present in sampled MCP dataprints | Acronis Management Portal |
| EDR / anti-malware module data | ❌ not in this recipe's scope | Acronis Management Portal — separate domain |
| DLP module data | ❌ not in this recipe's scope | Acronis Management Portal |
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
| 2 | liongard_launchpoint LIST | inspectorId=93 envId=<ENV_ID> | array<launchpoint/system> | ok |
| 3 | liongard_metric EVALUATE | metricName="Acronis Cyber Cloud: Count of Machines" sysId=<SYS_ID> envId=<ENV_ID> | integer | ok |
| 3 | liongard_metric EVALUATE | metricName="Acronis Cyber Cloud: Count of Machines with Backup Enabled" sysId=<SYS_ID> envId=<ENV_ID> | integer | ok |
| 3 | liongard_metric EVALUATE | metricName="Acronis Cyber Cloud: List of Machines with Backup Enabled" sysId=<SYS_ID> envId=<ENV_ID> | array | ok |
| 3 | liongard_metric EVALUATE | metricName="Acronis Cyber Cloud: List of Machines without Backup Enabled" sysId=<SYS_ID> envId=<ENV_ID> | array | ok |
| 3 | liongard_metric EVALUATE | metricName="Acronis Cyber Cloud: Machine Backup Summary" sysId=<SYS_ID> envId=<ENV_ID> | object | ok |
| 3 | liongard_metric EVALUATE | metricName="Acronis Cyber Cloud: Count of Machines Not Successfully Backed Up In Last 24 Hours" sysId=<SYS_ID> envId=<ENV_ID> | integer | ok |
| 3 | liongard_metric EVALUATE | metricName="Acronis Cyber Cloud: List of Machines Not Successfully Backed Up In Last 24 Hours" sysId=<SYS_ID> envId=<ENV_ID> | array | ok |
| 3 | liongard_metric EVALUATE | metricName="Acronis Cyber Cloud: List of Machines Successfully Backed Up In Last 30 days" sysId=<SYS_ID> envId=<ENV_ID> | array | ok |
| 3 | liongard_metric EVALUATE | metricName="Acronis Cyber Cloud: List of Machines NOT Successfully Backed Up In Last 30 days" sysId=<SYS_ID> envId=<ENV_ID> | array | ok |
| 4 | liongard_device LIST | envId=<ENV_ID> class=server fields=[...] | array<device> | ok |
| 5 | (QA pass) retry + divergence checks + manual-gap surfacing | per `reference/qa-retry-pattern.md` | varies | ok |
```

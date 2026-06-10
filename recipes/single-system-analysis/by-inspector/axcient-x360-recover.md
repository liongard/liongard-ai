---
name: single-system-axcient-x360-recover
description: >
  Use this skill when the user wants a single-tenant analysis of an
  Axcient x360 Recover account — appliance health, per-device backup job
  status, vault inventory, client coverage. Axcient is an appliance-based
  backup product (formerly Replibit before the x360 rebrand). Beta
  inspector — some fields may be sparse. Trigger phrases: "Axcient PBR",
  "x360 Recover review", "Axcient appliance health", "Axcient backup job
  status", "Replibit review". Produces an artifact in the format set in
  the customization block.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_launchpoint, liongard_metric, liongard_device"
personas: [noc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, xlsx]
primitives:
  - metrics:axcient-x360-recover:appliance-drive-usage-percent
  - metrics:axcient-x360-recover:appliance-health-status
  - metrics:axcient-x360-recover:appliance-health-status-reason
  - metrics:axcient-x360-recover:appliance-ip-address
  - metrics:axcient-x360-recover:appliance-last-tunnel-up
  - metrics:axcient-x360-recover:appliance-model
  - metrics:axcient-x360-recover:appliance-software-version
  - metrics:axcient-x360-recover:appliance-tunnel-info
  - metrics:axcient-x360-recover:appliance-tunnel-status
  - metrics:axcient-x360-recover:client-name
  - metrics:axcient-x360-recover:device-agent-version
  - metrics:axcient-x360-recover:device-ip-address
  - metrics:axcient-x360-recover:device-job-health-status
  - metrics:axcient-x360-recover:device-job-latest-restore-point
  - metrics:axcient-x360-recover:device-latest-cloud-restore-point
  - metrics:axcient-x360-recover:device-latest-local-restore-point
  - metrics:axcient-x360-recover:device-type
  - metrics:axcient-x360-recover:device-vault-latest-restore-point
  - metrics:axcient-x360-recover:job-health-status
  - metrics:axcient-x360-recover:organization-server-count
  - metrics:axcient-x360-recover:organization-workstation-count
  - metrics:axcient-x360-recover:unprotected-client-count
  - metrics:axcient-x360-recover:vault-connectivity-threshold
  - metrics:axcient-x360-recover:vault-days-since-latest-restore-point
  - metrics:axcient-x360-recover:vault-drive-storage-drive-size
  - metrics:axcient-x360-recover:vault-drive-storage-used-size
  - metrics:axcient-x360-recover:vault-health-status
  - metrics:axcient-x360-recover:vault-health-status-reason
  - metrics:axcient-x360-recover:vault-ip-address
  - metrics:axcient-x360-recover:vault-last-tunnel-up
  - metrics:axcient-x360-recover:vault-latest-restore-point
  - metrics:axcient-x360-recover:vault-software-version
  - metrics:axcient-x360-recover:vault-tunnel-status
---

# Single-System Analysis — Axcient x360 Recover

> **Inspector:** `axcient-x360-recover-inspector` (ID 100). **Beta**
> category. Backup / DR. Appliance-based image-level backup with cloud
> replication. Renamed from Replibit.
>
> **Parent/child:** Yes. Parent = the partner organization (enumerates
> `Clients[*]`). Child = the per-client view (holds `Devices[*]` and
> `Vaults[*]` for one customer).
>
> **References:** `reference/inspector-aliases.md` (Axcient, x360,
> "Replibit" legacy). `reference/asset-fields.md` for cross-checks.
> **Pairs with `recipes/system-type-assessment/all-backups.md`** for
> the cross-vendor coverage rollup.


---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-axcient-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  appliance_health: "Appliance / Vault Health"
  device_coverage: "Per-Device Backup Coverage"
  failed_jobs: "Failed Jobs"
  capacity: "Vault Capacity"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 1
  appliance_health_required: healthy
  device_job_health_required: healthy
  failed_jobs_max: 0

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

- "Pull Axcient data for the customer" (PBR)
- "Are any Axcient appliances unhealthy?"
- "x360 Recover backup job status review"
- "Axcient vault capacity check"

Personas: NOC, vCIO/AM, TAM.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Axcient system ID | Yes | `liongard_launchpoint LIST inspectorId=100` |
| Reporting period | No | Default per customization |

---

## Locating the right system

```
liongard_launchpoint LIST inspectorId=100 environmentIds=[<ENV_ID>]
```

| Shape | What it is | Action |
|---|---|---|
| Parent launchpoint (`parentID` null) and has `Clients[*]` rollup | **Parent** — MSP organization rollup | Use only for scoping / child discovery |
| Child launchpoint (`parentID` set) and has `Devices[*]` + `Vaults[*]` for one customer | **Child** — per-client | Use this for all backup-health metrics |

`Organization.name` returns the Axcient organization / MSP name (parent);
on the child, the customer's protected resources are in
`Devices[*].name`.

> MCP validation note: some Dev parent systems also expose `Devices[*]`
> and `Vaults[*]`. For a customer report, do **not** evaluate the
> operational backup metrics against the parent rollup. Select the
> child launchpoint for the customer and evaluate metrics against that
> child `systemId`.


---

## Liongard data sources

> **Asset Inventory First, Metric Cross-Check.** Axcient is a backup
> vendor — protected-device enumeration is the per-vendor data; the
> denominator (every server the customer has) is the cross-inspector
> device inventory.

### Per-vendor data — Axcient dataprint top-level keys

| Key | Description |
|---|---|
| `Organization` | Axcient organization / MSP-level identity |
| `Clients` | Parent — array of client / customer companies managed by this account |
| `Vaults` | Backup vault inventory (appliances providing storage) |
| `Appliances` | Health-reporting appliances — each with its own `health_status` |
| `Devices` | Per-protected-device array; each device has `jobs[*]` with status |

#### Field gotchas (inline notes — not TODO)

- **Parent/child model.** Axcient uses a parent (org) / child (per-client)
  model. Parent enumerates `Clients[*]`; child holds the per-customer
  backup detail. Confirm with the launchpoint relationship first
  (`parentID` set = child). Dev parent dataprints may also expose
  `Devices[*]` / `Vaults[*]`, so do not rely on those arrays alone to
  select the evidence system.
- **Beta status.** Inspector is flagged Beta in Liongard. Some fields
  are partial or unstable; surface this in the manual-verification
  appendix when reporting to a customer.

### Cross-inspector cross-check — device inventory

```
liongard_device LIST environmentId=<ENV_ID> class="server"
                     fields=["hostname","inspectors","operatingSystem"]
```

```
# Servers Axcient sees
axcient_protected = devices where inspectors contains "axcient-x360-recover-inspector"

# Unprotected candidates
unprotected = devices where class == "server"
                            AND inspectors does not contain "axcient-x360-recover-inspector"
```

---

## Metrics and queries

### Parent scoping only

Use these only to find the correct child/customer dataprint. Do not use
parent rollup values as evidence for a customer's appliance, vault, or
device backup health.

| Metric | JMESPath | Purpose |
|---|---|---|
| Client list | `Clients[].name` | inventory / scoping |
| Client count | `length(Clients)` | inventory / scoping |

### Child dataprint metrics

Evaluate the following against the selected child/customer `systemId`
only.

| Metric | JMESPath | Compliant when |
|---|---|---|
| Appliance health status | metricName="Axcient: Appliance Health Status" — `Appliances[].health_status` | every entry == `healthy` |
| Vault health status | metricName="Axcient: Vault Health Status" — `Vaults[].health_status` | every entry == `healthy` |
| Device job health status | metricName="Axcient: Device Job Health Status" — `Devices[].jobs[].health_status` | every entry == `healthy` |
| Job health status | metricName="Axcient: Job Health Status" — `Jobs[].health_status` | every entry == `healthy` |
| Vault used size | metricName="Axcient: Vault Drive Storage details - Used Size" — `Vaults[].storage_details.used_size` | capacity context |
| Appliance drive usage percent | metricName="Axcient: Appliance Drive Usage Percent" — `map(&percent_of(storage_details.used_size, storage_details.drive_size), Appliances)` | below MSP threshold when populated |

### Per-device backup detail (for the all-backups.md join)

Run this against the child/customer dataprint:

```jmespath
Devices[*].{
  name: name,
  latestRestorePoint: jobs[*].latest_rp,
  lastBackup: jobs[*].lastRunTime,
  status: jobs[*].health_status
}
```

### Additional MCP-validated detail

| Field | Metric / workaround |
|---|---|
| Per-device latest restore point | metricName="Axcient: Device Job Latest Restore Point" — `Devices[].jobs[].latest_rp` |
| Device latest local restore point | metricName="Axcient: Device Latest Local Restore Point" — `Devices[].latest_local_rp` |
| Device latest cloud restore point | metricName="Axcient: Device Latest Cloud Restore Point" — `Devices[].latest_cloud_rp` |
| Device vault latest restore point | metricName="Axcient: Device Vault Latest Restore Point" — `Devices[].vaults[].latest_vault_rp` |
| Vault latest restore point | metricName="Axcient: Vault Latest Restore Point" — `Vaults[].devices[].latest_vault_rp` |
| Vault used size | metricName="Axcient: Vault Drive Storage details - Used Size" — `Vaults[].storage_details.used_size` |
| Vault drive size | metricName="Axcient: Vault Drive Storage Details - Drive Size" — `Vaults[].storage_details.drive_size`; may be null in some dataprints |
| Appliance drive usage percent | metricName="Axcient: Appliance Drive Usage Percent" — depends on `storage_details.drive_size` being populated |
| Client count rollup | Parent scoping only — client-side `length(Clients)` |

### Time-series — health trend

```
liongard_metric EVALUATE_TIME_SERIES
  systemId=<CHILD_SYS_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="length(Appliances[?health_status != `healthy`])"

liongard_metric EVALUATE_TIME_SERIES
  systemId=<CHILD_SYS_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="length(Vaults[?health_status != `healthy`])"
```

---

## QA & Manual Verification

Run the QA pass per `reference/qa-retry-pattern.md` before rendering output:

1. **Retry persistent nulls.** Retry up to `qa.retry_attempts` times.

2. **Flag stale inspector data.** Axcient API-driven; lastSeen > 1 day =
   API access issue.

3. **Cross-tool divergence.** Confirm Axcient `Devices[*].name` reconciles
   with the device inventory's "servers with Axcient in inspectors[]".

4. **Manual / partial data gaps for this recipe** — surface in the
   manual-verification appendix:
   - Vault capacity utilization when `drive_size` is missing
   - Appliance drive usage percent when `Appliances[*]` is empty
   - Client count rollup when parent/child shape is ambiguous

5. **Manual Verification appendix** — render in the deliverable. Typical
   items for this recipe:
   - **Beta inspector status** — note for customer-facing reports that
     some fields may not be fully populated.
   - Appliance reporting non-healthy state (escalate immediately).
   - Vault capacity percent (manual confirm if `drive_size` is null).

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Unhealthy appliance | any entry in `Appliances[].health_status` != `healthy` | "**Critical:** <N> appliances reporting non-healthy state — investigate immediately." |
| Unhealthy vault | any entry in `Vaults[].health_status` != `healthy` | "**Critical:** <N> vaults reporting non-healthy state — investigate storage / connectivity immediately." |
| Failed device job | any entry in `Devices[].jobs[].health_status` != `healthy` | "<N> device jobs unhealthy — review per-device status." |
| Stale Axcient inspector | `lastSeen > 1 day` | "Axcient inspector hasn't reported in <N> days — confirm API access." |
| Beta inspector advisory | always (until inspector is GA) | "Note: Axcient inspector is currently Beta — some fields may be partial. Manual UI confirm recommended for the full picture." |


---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Per-device job health | ✅ metricName="Axcient: Device Job Health Status" | Axcient portal for dispute resolution |
| Per-device latest restore point | ✅ metricName="Axcient: Device Job Latest Restore Point"; composite can be parsed client-side | Axcient portal for dispute resolution |
| Vault health / used size | ✅ metricName="Axcient: Vault Health Status" + "Axcient: Vault Drive Storage details - Used Size" | Axcient portal for dispute resolution |
| Vault capacity utilization percent | ⚠️ partial — `drive_size` may be null; use metricName="Axcient: Appliance Drive Usage Percent" when storage details are populated | Axcient portal |
| Client count rollup | ⚠️ no count metric; client names metricName=`Axcient: Client Name`, count via `length(Clients)` | Client-side length |
| Replication lag (to cloud vault) | ❌ not in dataprint | Axcient portal |
| Recovery time objective (RTO) per device | ❌ not in dataprint | Axcient portal / manual test |
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
| 2 | liongard_launchpoint LIST | inspectorId=100 envId=<ENV_ID> | array<launchpoint/system> | identify child customer system |
| 3 | liongard_metric EVALUATE | metricName="Axcient: Appliance Health Status" sysId=<CHILD_SYS_ID> envId=<ENV_ID> | array | ok |
| 3 | liongard_metric EVALUATE | metricName="Axcient: Vault Health Status" sysId=<CHILD_SYS_ID> envId=<ENV_ID> | array | ok |
| 3 | liongard_metric EVALUATE | metricName="Axcient: Device Job Health Status" sysId=<CHILD_SYS_ID> envId=<ENV_ID> | array | ok |
| 3 | liongard_metric EVALUATE | metricName="Axcient: Job Health Status" sysId=<CHILD_SYS_ID> envId=<ENV_ID> | array | ok |
| 3 | liongard_metric EVALUATE | metricName="Axcient: Device Job Latest Restore Point" sysId=<CHILD_SYS_ID> envId=<ENV_ID> | array | ok |
| 3 | liongard_metric EVALUATE | metricName="Axcient: Vault Drive Storage details - Used Size" sysId=<CHILD_SYS_ID> envId=<ENV_ID> | array | ok |
| 4 | liongard_metric EVALUATE | jmesPath Devices[*]... sysId=<CHILD_SYS_ID> envId=<ENV_ID> | <array> | ok |
| 5 | liongard_device LIST | envId=<ENV_ID> class=server fields=[...] | array<device> | ok |
| 6 | (QA pass) retry + divergence checks | per `reference/qa-retry-pattern.md` | varies | ok |
```

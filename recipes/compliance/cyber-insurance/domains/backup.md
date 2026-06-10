---
name: cyber-insurance-backup
description: >
  Domain reference for the cyber-insurance-readiness master skill. Covers Backup & Business Continuity
  (Q5, Q5a, Q5b, Q46). Used as a sub-reference when answering cyber insurance underwriting
  questions in this control area.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_asset"
personas: [vcio-account-manager, soc, technical-alignment-manager]
primitives:
  - metrics:axcient-x360-recover:appliance-health-status
  - metrics:axcient-x360-recover:device-job-health-status
  - metrics:axcient-x360-recover:job-health-status
  - metrics:axcient-x360-recover:unprotected-client-count
  - metrics:axcient-x360-recover:vault-health-status
  - metrics:cove-data-protection:count-backups-completed-with-errors
  - metrics:cove-data-protection:count-device-backup-overdue-24h
  - metrics:cove-data-protection:count-exchange-backup-overdue-24h
  - metrics:cove-data-protection:count-failed-backups
  - metrics:cove-data-protection:count-onedrive-backup-overdue-24h
  - metrics:cove-data-protection:count-sharepoint-backup-overdue-24h
  - metrics:cove-data-protection:list-device-backup-overdue-24h
  - metrics:cove-data-protection:list-failed-backups
  - metrics:cove-data-protection:servers-no-backup-30d
  - metrics:datto-bcdr:agent-backups-without-screenshot-list
  - metrics:datto-bcdr:backups-failed-recent-list
  - metrics:datto-bcdr:backups-older-than-30d-list
  - metrics:datto-bcdr:backups-overdue-24h-count
  - metrics:datto-bcdr:backups-overdue-24h-summary
  - metrics:datto-bcdr:days-until-service-expiry
  - metrics:veeam-availability-console:unhealthy-repositories-count
  - metrics:veeam-availability-console:unhealthy-repositories-list
  - metrics:veeam-vspc:jobs-failed-or-warning-count-v5
  - metrics:veeam-vspc:jobs-failed-or-warning-list-v5
---


```yaml
customize:
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed
```
# Cyber Insurance — Domain: Backup & Business Continuity

> **Pairs with:** `recipes/compliance/cyber-insurance/cyber-insurance-readiness.md`. The master file
> documents the workflow, customization block, asset-inventory schema, and gap-summary
> output. This domain file documents the metric names and JMESPath queries for each
> question in this control area.

> **Asset Inventory First.** Before evaluating the per-metric tables below, the
> agent should pull `liongard_asset LIST detail=full` for the relevant assetType
> (Identity or Device) and answer the question from the asset record's
> cross-inspector synthesis (`mfaStatus`, `accountActivity`, `privileged`,
> `antivirus`, `edr`, `inspectors[]`, etc.). Per-inspector metrics in this file
> are the **cross-check** — they confirm the asset answer and provide
> inspector-unique fields the asset doesn't expose (e.g., AD password policy,
> Conditional Access policy names, firewall rule counts). When asset and metric
> disagree, the asset value wins and the divergence is recorded as a data-quality
> flag in the gap summary.


**Inspectors referenced:** Datto BCDR, Cove Data Protection, Axcient, Veeam

**Question coverage:** Q5, Q5a, Q5b, Q46

---

## Recording evidence

For every metric below:

1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_keyword>" environmentId=<ENV_ID>`
2. Evaluate the metric: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL.

The output format is whatever the master skill's customization block specifies
(`xlsx` evidence workbook, `word` summary report, or `markdown`). The agent maps the
recorded evidence into the chosen format's evidence + status fields.

---

## Q5 — Do you maintain backup processes?
**N/A**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ❌ `NOT_FOUND` | unknown | Datto BCDR: Recent Datto Backup Failed | `NOT_FOUND` | false |
| ❌ `NOT_FOUND` | unknown | Datto BCDR: Datto Backups Not Completed in the Last 24 Hours Count | `NOT_FOUND` | 0 |
| ❌ `NOT_FOUND` | unknown | Datto BCDR: Datto Backups Not Completed in the Last 24 Hours Summary | `NOT_FOUND` | empty |
| ✅ | Cove Data Protection | Cove Data Protection: Count of Failed Backups | `Devices[?BackupStatus==`Failed`] \| length(@)` | 0 |
| ✅ | Cove Data Protection | Cove Data Protection: 24 Hours Since Last Completed Device Backup Count | `Devices[?Type == `BackupManager` && HoursSinceLastComplet...` | 0 |
| ✅ | Cove Data Protection | Cove Data Protection: 24 Hours Since Last Completed Exchange Backup Count | `Devices[?Type == `Office365` && HoursSinceExchangeLastCom...` | 0 |
| ✅ | Cove Data Protection | Cove Data Protection: 24 Hours Since Last Completed OneDrive Backup Count | `Devices[?Type == `Office365` && HoursSinceOneDriveLastCom...` | 0 |
| ✅ | Axcient | Axcient: Appliance Health Status | `Appliances[].health_status` | healthy |
| ✅ | Axcient | Axcient: Device Job Health Status | `Devices[].jobs[].health_status` | healthy |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q5a — Are backup and recovery procedures automated?
**Source:** Travelers Q10l follow-on · Workbook sub-item of Q5

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record value → Assessment evidence column (row Q5a); set Status in status column

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Cove Data Protection | Cove: 24 Hours Since Last Completed Device Backup Count | `Devices[?Type==\`BackupManager\`&&HoursSinceLastCompleted>\`24\`]\|length(@)` | 0 — implies automated schedule running |
| ✅ | Cove Data Protection | Cove: 24 Hours Since Last Completed Exchange Backup Count | `Devices[?Type==\`Office365\`&&HoursSinceExchangeLastCompleted>\`24\`]\|length(@)` | 0 |
| ✅ | Axcient | Axcient: Appliance Health Status | `Appliances[].health_status` | healthy — automated jobs running |

**Interpretation:** A count of 0 for "24h since last backup" is strong evidence of an automated
schedule. If counts are non-zero, investigate whether manual runs or a schedule failure explains
the gap. Also confirm automation setting in the backup console (manual attestation).

---

## Q5b — Are backup and recovery procedures tested on an annual basis?
**Source:** Travelers Q10l follow-on · Workbook sub-item of Q5  
**Coverage:** `ℹ️ MANUAL`

> Liongard cannot verify that backup *restoration* has been tested — only that backup jobs are
> running. Backup testing requires a restore exercise with documented results.

**Evidence to collect:**
- Most recent restore test date
- Test type (file-level, full system, bare-metal, cloud failover)
- Test results and any identified recovery gaps
- Who conducted the test (internal IT, MSP, or third party)

---

## Q46 — Does the organization maintain a formal business continuity plan?
**N/A**

> ℹ️ **No Liongard metric available.** This question requires manual attestation.
> See the Manual Attestation sheet in the evidence record for guidance.

---

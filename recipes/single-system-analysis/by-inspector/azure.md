---
name: single-system-azure
description: >
  Use this skill when the user wants a single-subscription analysis
  of a Microsoft Azure subscription — RBAC posture, NSG / firewall
  rules, storage-account public-access audit, Key Vault inventory,
  Activity Log / Microsoft Defender for Cloud / Sentinel status,
  cost anomalies, resource inventory by region. Trigger phrases:
  "Azure review for <customer>", "Azure PBR", "Azure subscription
  audit", "RBAC audit on Azure", "Azure NSG review", "Defender for
  Cloud findings", "Azure storage public-access check".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device, liongard_identity"
personas: [soc, technical-alignment-manager, vcio-account-manager, accounting-finance, noc]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  - metrics:azure:enabled-subscriptions-count
  - metrics:azure:nsg-rdp-exposed-count
  - metrics:azure:nsg-rdp-exposed-list
  - metrics:azure:subnets-list
  - metrics:azure:virtual-machine-count
  - metrics:azure:virtual-machines-list
---

# Single-System Analysis — Microsoft Azure

> **Inspector:** `azure-inspector` (ID 11). Cloud category. **One
> system per Azure subscription.** Covers subscription resources, RBAC,
> NSGs, storage accounts, Key Vault, Defender for Cloud, Sentinel.
>
> **IMPORTANT — identity routing:** Entra ID / Azure AD identity data
> lives in the **`microsoft-365-inspector`**, NOT the `azure-inspector`.
> When a user says "Azure AD", route to the M365 recipe. This inspector
> covers Azure **subscription resources** (compute, storage, networking,
> security tooling) — NOT identity.
>
> **References:** `reference/inspector-aliases.md` (Azure, MS Azure;
> Azure AD → microsoft-365).

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-azure-<subscription-alias>-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  subscription_identity: "Subscription Identity & Billing"
  rbac: "RBAC Posture"
  networking: "Virtual Networks & NSGs"
  storage_accounts: "Storage Accounts (Public Access)"
  key_vault: "Key Vaults & Secrets"
  activity_log: "Activity Log & Audit"
  defender_sentinel: "Defender for Cloud & Sentinel"
  region_inventory: "Region & Resource Inventory"
  cost_anomalies: "Cost Anomalies & Reservation Coverage"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 7
  owner_count_max: 3                           # Owner-role count above N flagged
  classic_admin_allowed: false                 # legacy Service Admin / Co-Admin must not exist
  rbac_assignment_review_days_max: 180
  guest_user_review_days_max: 90               # external guests should be reviewed regularly
  privileged_pim_required: true                # Privileged Identity Management for privileged roles
  nsg_open_to_world_ports_critical: [22, 3389, 1433, 3306, 5432, 27017]
  nsg_default_deny_required: true
  storage_blob_public_access_allowed: false
  storage_https_only_required: true
  storage_min_tls_version: "TLS1_2"
  storage_default_encryption_required: true
  key_vault_soft_delete_required: true
  key_vault_purge_protection_required: true
  activity_log_retention_days_min: 90
  defender_for_cloud_enabled_required: true
  defender_for_cloud_plan_min: "Standard"      # Free | Standard
  sentinel_enabled_recommended: true           # WARN not FAIL — Sentinel is paid
  cost_anomaly_alert_required: false
  reservation_coverage_pct_min: 0              # MSP-customizable

reporting_period: { default: "current_state" }

qa:
  retry_on_null: true
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: false
  manual_verification_section_required: true
```

---

## When to use

- "Azure posture for <customer>"
- "Azure PBR / quarterly review"
- "RBAC audit on the Azure subscription"
- "Azure NSG review (any open RDP / SSH / DB ports?)"
- "Azure storage public-access check"
- "Defender for Cloud findings"
- "Azure compliance prep (cyber-insurance, CMMC, HIPAA)"

Cadence: monthly per subscription; quarterly in PBR; ad-hoc post-MS
security bulletin.

Personas:
- **SOC** (primary — RBAC, NSG, storage exposure, Defender findings)
- **TAM** (standards alignment, baseline compliance)
- **vCIO / Account Manager** (cost anomalies, renewal narrative)
- **Accounting / Finance** (reservation / savings-plan coverage)
- **NOC** (operational — resource health, regions in use)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the Azure subscription) | Yes — one per subscription | `liongard_system LIST query="azure"` |

> **One system per subscription.** Multi-subscription customers
> (Enterprise Agreement, Microsoft Customer Agreement with multiple
> subscriptions) have one system per subscription. Run per-subscription;
> aggregate via the future cloud-infrastructure rollup.

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="azure"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Subscription identity + billing

```
liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative:
#   "azure.subscription.id"
#   "azure.subscription.name"
#   "azure.subscription.tenantId"
#   "azure.subscription.offerType"            (EA / MCA / Pay-As-You-Go / etc.)
#   "azure.subscription.billingAccount"
#   "azure.subscription.spendingLimit"
#   "azure.subscription.spendCurrentMonthUSD"
#   "azure.subscription.spendPreviousMonthUSD"
#   "azure.subscription.spendTrendPct"
```

### Step 4 — RBAC posture

```
#   "azure.rbac.ownerCount"
#   "azure.rbac.ownerList"
#   "azure.rbac.contributorCount"
#   "azure.rbac.userAccessAdminCount"
#   "azure.rbac.byRoleDistribution"
#   "azure.rbac.guestUserCount"
#   "azure.rbac.guestUserStaleCount"          (no activity > N days)
#   "azure.rbac.classicAdminCount"            (Service Admin / Co-Admin — should be 0)
#   "azure.rbac.principalsByMfaStatus"        (cross-ref to Entra ID)
#   "azure.rbac.pim.eligibleAssignmentsCount"
#   "azure.rbac.pim.activeAssignmentsCount"
#   "azure.rbac.pim.justInTimeEnabled"
#   "azure.rbac.customRolesCount"
#   "azure.rbac.customRolesWithStarPermissionsCount"   (wildcard = critical)
```

### Step 5 — Networking + NSGs

```
#   "azure.vnet.totalCount"
#   "azure.vnet.byRegion"
#   "azure.vnet.peeringsCount"
#   "azure.nsg.totalCount"
#   "azure.nsg.openToWorldCount"               (Source = `*` / `Internet` / `0.0.0.0/0`)
#   "azure.nsg.openSshList"
#   "azure.nsg.openRdpList"
#   "azure.nsg.openDbList"
#   "azure.nsg.flowLogsEnabledCount"
#   "azure.firewall.deployedCount"
#   "azure.bastion.deployedCount"
#   "azure.frontDoor.deployedCount"
#   "azure.applicationGateway.wafEnabledCount"
#   "azure.publicIps.totalCount"
#   "azure.publicIps.unusedCount"
```

### Step 6 — Storage accounts

```
#   "azure.storage.accountsCount"
#   "azure.storage.accounts.publicBlobAccessEnabledCount"
#   "azure.storage.accounts.publicContainerCount"
#   "azure.storage.accounts.httpsOnlyDisabledCount"
#   "azure.storage.accounts.minTlsBelowStandardCount"
#   "azure.storage.accounts.encryptionDisabledCount"
#   "azure.storage.accounts.softDeleteDisabledCount"
#   "azure.storage.accounts.sharedKeyAccessEnabledCount"     (should prefer Entra ID auth)
#   "azure.storage.accounts.networkRulesAllowAllCount"        (firewall disabled)
```

### Step 7 — Key Vault + Secrets

```
#   "azure.keyVault.vaultsCount"
#   "azure.keyVault.softDeleteEnabledCount"
#   "azure.keyVault.purgeProtectionEnabledCount"
#   "azure.keyVault.publicAccessEnabledCount"   (must be 0)
#   "azure.keyVault.privateLinkEnabledCount"
#   "azure.keyVault.secretsExpiringSoonCount"
#   "azure.keyVault.keysWithoutRotationCount"
```

### Step 8 — Activity Log + audit

```
#   "azure.activityLog.diagnosticSettingExists"
#   "azure.activityLog.exportedToLogAnalytics"
#   "azure.activityLog.exportedToStorage"
#   "azure.activityLog.retentionDays"
#   "azure.diagnosticSettings.subscriptionLevel"
```

### Step 9 — Defender for Cloud + Sentinel

```
#   "azure.defenderForCloud.enabled"
#   "azure.defenderForCloud.planByService"     (Servers / Storage / SQL / etc. — Free vs Standard)
#   "azure.defenderForCloud.secureScorePct"
#   "azure.defenderForCloud.recommendationsHighCount"
#   "azure.defenderForCloud.alertsCriticalCount"
#   "azure.defenderForCloud.alertsHighCount"
#   "azure.defenderForCloud.regulatoryComplianceStandards"   (CIS / NIST / PCI / etc.)
#   "azure.sentinel.deployed"
#   "azure.sentinel.workspaceId"
#   "azure.sentinel.dataConnectorsCount"
#   "azure.sentinel.activeIncidentsCount"
```

### Step 10 — Resource inventory

```
liongard_device LIST environmentId=<ENV_ID>
                     fields=["hostname","operatingSystem","manufacturer","class","inspectors","lastSeen"]
                     filter="inspectors contains 'azure-inspector'"

#   "azure.compute.vmsCount"
#   "azure.compute.vmsByRegion"
#   "azure.compute.vmsByState"
#   "azure.compute.vmsPublicIpCount"
#   "azure.compute.vmsUnencryptedDiskCount"
#   "azure.compute.vmsBackupDisabledCount"
#   "azure.sql.serversCount"
#   "azure.sql.serversPublicAccessCount"
#   "azure.sql.serversAuditDisabledCount"
#   "azure.sql.serversTdeDisabledCount"
#   "azure.sql.serversAdvancedDataSecurityDisabledCount"
#   "azure.aks.clustersCount"
#   "azure.aks.clustersPublicApiEnabledCount"
#   "azure.functionApps.count"
#   "azure.appService.count"
#   "azure.appService.minTlsBelowStandardCount"
```

### Step 11 — Cost + reservations

```
#   "azure.billing.anomalyCount"
#   "azure.billing.byServiceTopSpend"
#   "azure.billing.byRegionDistribution"
#   "azure.reservations.coveragePct"
#   "azure.reservations.expiringWithinWarnDays"
#   "azure.savingsplans.coveragePct"
```

### Step 12 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on:
1. Retry persistent nulls.
2. Stale inspector flag.
3. **RBAC cross-reference** with M365 identity inventory (RBAC principals = Entra ID users / service principals).
4. **Region-coverage divergence** — confirm Defender for Cloud + Diagnostic Settings cover every region actually in use.
5. **Identity-vs-subscription routing** — verify the recipe isn't conflating Azure AD (M365 inspector) with subscription resources (this inspector).
6. Proposed-metric gaps.

### Step 13 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | Cloud infrastructure, not endpoint. |
| CIS Controls (v8.1) | ✅ | CIS 1.1 (cloud asset inventory), 3.3, 3.10 / 3.11 (encryption), 4.1, 5.4 (RBAC admin separation), 6.3 / 6.4 (RBAC MFA — via Entra ID conditional access), 8.2 / 8.5 / 8.11 (Activity Log + Diagnostic Settings), 12.2 (NSG boundary), 13.1 / 13.6 (Defender for Cloud, Sentinel), 14.6 (DLP — partial via Purview). |
| Cyber-insurance domain files | ✅ | Pairs with `domains/auth.md` (RBAC), `domains/network.md` (NSG), `domains/governance.md` (Activity Log audit retention), `domains/regulatory.md` (HIPAA / PCI / SOC2 — storage encryption, Key Vault, Defender compliance score). |
| QBR / quarterly-business-review | ✅ | Chained when Azure is deployed; surfaces RBAC owner count, NSG public exposure, Defender Secure Score, cost trend. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| Excessive Owner count | "<N> Owner-role assignments. Reduce to operational minimum; use Contributor + PIM eligible for elevated work." |
| Classic admin present | "URGENT: Service Admin / Co-Admin still present. Migrate to RBAC; remove classic admin." |
| PIM not used for privileged roles | "Enable Privileged Identity Management (PIM) for Owner / User Access Administrator / Global Admin. JIT activation per MSP standard." |
| Stale guest user | "<N> guest users inactive > <N> days. Remove or convert to member with explicit role." |
| Custom role with wildcard | "<N> custom roles use `*` permissions. Replace with granular built-in roles." |
| NSG open to world (high-risk port) | "URGENT: <N> NSG rules expose <port> to Internet. Restrict via Bastion / VPN / Azure Firewall." |
| NSG flow logs disabled | "<N> NSGs without flow logs. Enable for boundary-protection evidence." |
| Storage public blob access | "URGENT: <N> storage accounts allow public blob access. Disable at account level + container level." |
| Storage HTTPS-only off | "<N> storage accounts allow HTTP. Enable secure-transfer-required." |
| Storage TLS below 1.2 | "<N> storage accounts allow TLS < 1.2. Raise minimum to TLS 1.2." |
| Storage shared-key auth enabled | "<N> storage accounts allow shared-key auth. Disable; require Entra ID authentication." |
| Storage network rules allow all | "<N> storage accounts accept traffic from anywhere. Apply network ACLs + private endpoints." |
| Key Vault soft-delete disabled | "Enable soft-delete + purge protection on <N> Key Vaults. Required for compliance." |
| Key Vault public access | "<N> Key Vaults accept public access. Restrict via firewall + private endpoint." |
| Activity Log not exported | "Configure Activity Log Diagnostic Setting to export to Log Analytics + Storage. Retention ≥ <baseline> days." |
| Defender for Cloud disabled | "Enable Defender for Cloud at Standard tier per MSP baseline." |
| Defender Secure Score low | "Secure Score at <N>%. Triage top recommendations." |
| Defender critical alerts open | "<N> critical Defender alerts. Investigate immediately." |
| Sentinel not deployed | "Consider Sentinel for SIEM coverage. (Paid — confirm budget.)" |
| SQL public access | "<N> Azure SQL servers publicly accessible. Move to private endpoint." |
| SQL TDE disabled | "<N> SQL servers without Transparent Data Encryption. Enable." |
| AKS API public | "<N> AKS clusters with public API server. Restrict to authorized IP ranges." |
| VM unencrypted disk | "<N> VMs with unencrypted OS / data disks. Enable Azure Disk Encryption." |
| VM backup disabled | "<N> VMs without backup policy. Enable Recovery Services Vault backup." |
| Cost anomaly | "<N> cost anomalies (<$N>). Investigate." |
| Low reservation coverage | "Reservation coverage at <N>%. Review committed-use opportunities." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Per-resource cost detail | partial | Azure Cost Management |
| Azure Policy compliance state | partial | Azure Policy / Defender for Cloud |
| Purview data-classification findings | partial / external | Microsoft Purview |
| Per-Activity-Log event detail | partial | Log Analytics queries |
| Resource tagging compliance | partial | Azure Policy |
| Microsoft 365 / Entra ID cross-tenant detail | n/a | Use `microsoft-365.md` recipe |

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST + liongard_system LIST | per inspector | array | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3-11 | liongard_metric VALUE | envId=<ENV_ID> sysId=<SYS_ID> metric=<id> | varies | ok per metric |
| 10 | liongard_device LIST | envId=<ENV_ID> filter=inspectors contains azure | array<device> | ok |
| 12 | QA pass | per `reference/qa-retry-pattern.md` | varies | ok |
| 13 | render | per `output.format` | <artifact path> | ok |
```

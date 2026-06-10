---
name: single-system-aws
description: >
  Use this skill when the user wants a single-account analysis of an
  AWS account — IAM posture (users, roles, MFA, access keys), VPC /
  security-group configuration, S3 bucket public-access audit, KMS
  key inventory, CloudTrail / GuardDuty / Security Hub status, billing
  / cost anomalies, region-by-region resource inventory. Trigger
  phrases: "AWS review for <customer>", "AWS PBR", "AWS account
  audit", "pull AWS data for <customer>", "IAM audit on AWS", "S3
  public bucket check", "AWS security posture".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device, liongard_identity"
personas: [soc, technical-alignment-manager, vcio-account-manager, accounting-finance, noc]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  - metrics:aws:cloudtrails-enabled
  - metrics:aws:ec2-instances-with-status-alerts-count
  - metrics:aws:iam-users-count
  - metrics:aws:iam-users-mfa-enabled-count
  - metrics:aws:rds-backup-older-than-15d-count
  - metrics:aws:root-access-keys
  - metrics:aws:root-account-mfa-enabled
  - metrics:aws:running-ec2-instances-count
  - metrics:aws:s3-buckets-count
  - metrics:aws:s3-buckets-without-default-encryption-count
  - metrics:aws:s3-buckets-without-default-encryption-list
  - metrics:aws:s3-publicly-accessible-bucket-count
  - metrics:aws:security-groups-count
  - metrics:aws:strong-password-policy-enabled
  - metrics:aws:unencrypted-ebs-volumes-count
  - metrics:aws:unencrypted-ebs-volumes-list
  - metrics:aws:users-without-mfa-list
---

# Single-System Analysis — Amazon Web Services

> **Inspector:** `aws-inspector` (ID 1). Cloud category. **One system
> per AWS account.** Covers subscription resources, IAM, VPC / security
> groups, S3, KMS, CloudTrail, GuardDuty, Security Hub. **Distinct from
> per-IAM-user / per-IAM-role identity records** — those reconcile into
> `liongard_identity` via email / IAM principal.
>
> **Cross-account considerations:** Multi-account customers (Organizations,
> Control Tower, Landing Zone) have one Liongard system per account.
> Use this recipe per-account; the future `all-cloud-infrastructure.md`
> rollup will produce the cross-account view.
>
> **References:** `reference/inspector-aliases.md` (AWS, Amazon).
> `reference/asset-fields.md` for the reconciled identity / device
> inventory cross-check.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-aws-<account-alias>-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  account_identity: "Account Identity & Billing"
  iam: "IAM Posture (Users, Roles, MFA, Access Keys)"
  vpc_networking: "VPC & Security Group Configuration"
  s3_storage: "S3 Bucket Public-Access Audit"
  kms_secrets: "KMS Keys & Secrets Manager"
  cloudtrail_logging: "CloudTrail & Audit Logging"
  threat_detection: "GuardDuty, Security Hub, Inspector findings"
  region_inventory: "Region-by-Region Resource Inventory"
  cost_anomalies: "Cost Anomalies & Reserved-Instance Coverage"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 7
  iam_user_mfa_required: true                # every IAM user with console access = MFA
  root_account_mfa_required: true            # non-negotiable
  iam_user_access_key_age_days_max: 90       # rotate or remove keys older than N days
  iam_user_password_age_days_max: 90
  unused_iam_user_days_max: 90               # IAM user with no recent activity
  iam_role_assume_principal_review_days_max: 180
  s3_public_bucket_allowed: false            # any unintentional public bucket = critical
  s3_default_encryption_required: true
  ebs_default_encryption_required: true
  rds_encryption_required: true
  cloudtrail_enabled_required: true          # CloudTrail in every region
  cloudtrail_log_file_validation_required: true
  guardduty_enabled_required: true
  security_hub_enabled_required: true
  vpc_flow_logs_required: true
  default_security_group_open_allowed: false
  open_to_world_ports_critical: [22, 3389, 1433, 3306, 5432, 27017]  # SSH/RDP/DB
  reserved_instance_coverage_pct_min: 0      # MSP-customizable per customer
  cost_anomaly_alert_required: false         # set true if MSP standard

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

- "AWS posture for <customer>"
- "AWS PBR / quarterly review"
- "IAM audit — root MFA, key rotation, unused users"
- "S3 public bucket check"
- "VPC security group review"
- "AWS compliance prep (cyber-insurance, CMMC, HIPAA)"

Cadence: monthly per account; quarterly in PBR; ad-hoc for new
account-takeover indicators, AWS bulletin advisories, or compliance
prep.

Personas:
- **SOC** (primary — IAM, S3, security-group findings)
- **TAM** (standards alignment, baseline compliance)
- **vCIO / Account Manager** (cost anomalies for renewal conversations)
- **Accounting / Finance** (Reserved Instance coverage, cost-anomaly alerting)
- **NOC** (operational — instance health, regions in use)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the AWS account) | Yes — one per account | `liongard_system LIST query="aws"` |
| Optional: focus area | No | User prompt — e.g., "focus on IAM only" |

> **One system per account.** Customer with `Production`, `Staging`,
> `Sandbox` accounts has 3 systems under this inspector. Run per-
> account; aggregate via the future cloud-infrastructure rollup.

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="aws"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Account identity + billing

```
liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative:
#   "aws.account.id"
#   "aws.account.alias"
#   "aws.account.email"                     (root email — confirm correct ownership)
#   "aws.account.organizationStatus"        (standalone | member | management)
#   "aws.account.organizationId"
#   "aws.account.supportPlan"               (Basic / Developer / Business / Enterprise)
#   "aws.billing.currentMonthSpendUSD"
#   "aws.billing.previousMonthSpendUSD"
#   "aws.billing.spendTrendPct"
```

### Step 4 — IAM posture

```
#   "aws.iam.users.totalCount"
#   "aws.iam.users.mfaEnabledCount"
#   "aws.iam.users.mfaCoveragePct"
#   "aws.iam.users.passwordEnabledCount"     (console access)
#   "aws.iam.users.accessKeyEnabledCount"
#   "aws.iam.users.accessKeyOlderThanWarn"   (keys > slas.iam_user_access_key_age_days_max)
#   "aws.iam.users.passwordOlderThanWarn"
#   "aws.iam.users.inactiveCount"            (last activity > slas.unused_iam_user_days_max)
#   "aws.iam.users.adminAttachedCount"       (AdministratorAccess policy attached)
#   "aws.iam.root.accessKeyExists"           (must be false — critical)
#   "aws.iam.root.mfaEnabled"                (must be true — critical)
#   "aws.iam.root.lastUsedDate"
#   "aws.iam.roles.totalCount"
#   "aws.iam.roles.byType"                  (service / cross-account / SAML / etc.)
#   "aws.iam.roles.crossAccountList"
#   "aws.iam.roles.openToWorldList"          (`Principal: *` on AssumeRole = critical)
#   "aws.iam.passwordPolicy.minLength"
#   "aws.iam.passwordPolicy.requireSymbols"
#   "aws.iam.passwordPolicy.requireNumbers"
#   "aws.iam.passwordPolicy.requireUppercase"
#   "aws.iam.passwordPolicy.requireLowercase"
#   "aws.iam.passwordPolicy.maxPasswordAge"
#   "aws.iam.passwordPolicy.reusePrevention"
```

Cross-reference IAM users with the reconciled identity inventory —
where IAM users align with M365 / AD email addresses, that's a
federation candidate; standalone IAM users are a candidate for
SSO migration.

### Step 5 — VPC + security groups

```
#   "aws.vpc.totalCount"
#   "aws.vpc.byRegion"
#   "aws.vpc.flowLogsEnabledCount"
#   "aws.vpc.flowLogsDisabledCount"
#   "aws.securityGroups.totalCount"
#   "aws.securityGroups.unusedCount"         (not attached to any ENI)
#   "aws.securityGroups.openToWorldCount"    (0.0.0.0/0 ingress)
#   "aws.securityGroups.openSshList"         (SG with 22 open to 0.0.0.0/0)
#   "aws.securityGroups.openRdpList"
#   "aws.securityGroups.openDbList"          (1433/3306/5432/27017 open to world)
#   "aws.securityGroups.defaultModifiedList" (default SG with non-default rules)
#   "aws.nacl.openToWorldCount"
```

### Step 6 — S3 storage

```
#   "aws.s3.bucketsTotalCount"
#   "aws.s3.buckets.publicAccessCount"       (any public read / write)
#   "aws.s3.buckets.publicReadList"
#   "aws.s3.buckets.publicWriteList"
#   "aws.s3.buckets.encryptionEnabledCount"
#   "aws.s3.buckets.encryptionDisabledCount"
#   "aws.s3.buckets.versioningEnabledCount"
#   "aws.s3.buckets.mfaDeleteEnabledCount"
#   "aws.s3.buckets.bucketPolicyHasPublicCount"
#   "aws.s3.buckets.byStorageClassDistribution"
```

### Step 7 — KMS + Secrets Manager

```
#   "aws.kms.customerKeysCount"
#   "aws.kms.keysWithRotationEnabledCount"
#   "aws.kms.keysPendingDeletionCount"
#   "aws.secretsManager.secretsCount"
#   "aws.secretsManager.secretsWithRotationCount"
#   "aws.secretsManager.secretsNeverRotatedCount"
```

### Step 8 — CloudTrail + audit logging

```
#   "aws.cloudtrail.trailsCount"
#   "aws.cloudtrail.multiRegionTrailExists"
#   "aws.cloudtrail.logFileValidationEnabled"
#   "aws.cloudtrail.s3BucketEncryptedCount"
#   "aws.cloudtrail.cloudwatchLogsIntegrationEnabled"
#   "aws.cloudtrail.daysSinceLastLogDelivery"
```

### Step 9 — Threat detection

```
#   "aws.guardduty.enabled"
#   "aws.guardduty.regionsEnabledCount"
#   "aws.guardduty.activeFindingsCount"
#   "aws.guardduty.criticalFindingsCount"
#   "aws.guardduty.highFindingsCount"
#   "aws.securityHub.enabled"
#   "aws.securityHub.complianceScoreByStandard"   (CIS, AWS Foundational, PCI-DSS)
#   "aws.inspector.enabled"
#   "aws.inspector.criticalFindingsCount"
```

### Step 10 — Region / resource inventory

```
liongard_device LIST environmentId=<ENV_ID>
                     fields=["hostname","operatingSystem","manufacturer","class","inspectors","lastSeen"]
                     filter="inspectors contains 'aws-inspector'"

#   "aws.ec2.instancesCount"
#   "aws.ec2.instancesByRegion"
#   "aws.ec2.instancesByState"               (running / stopped / terminated)
#   "aws.ec2.publicIpsCount"
#   "aws.ec2.ebsVolumesUnencryptedCount"
#   "aws.ec2.snapshotsPublicCount"           (public AMI / EBS snapshots = critical)
#   "aws.rds.instancesCount"
#   "aws.rds.instancesPubliclyAccessibleCount"
#   "aws.rds.instancesUnencryptedCount"
#   "aws.rds.instancesBackupDisabledCount"
#   "aws.lambda.functionsCount"
#   "aws.lambda.functionsWithoutVpcCount"
```

### Step 11 — Cost anomalies + RI coverage

```
#   "aws.billing.anomalyCount"
#   "aws.billing.anomalyTotalImpactUSD"
#   "aws.billing.byServiceTopSpend"          (top 10 services by spend)
#   "aws.billing.byRegionDistribution"
#   "aws.ri.coveragePct"
#   "aws.ri.expiringWithinWarnDays"
#   "aws.savingsplans.coveragePct"
```

### Step 12 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on:
1. Retry persistent nulls.
2. Stale inspector flag.
3. **Region-coverage divergence** — confirm CloudTrail / GuardDuty cover every region the account actually uses (EC2 / RDS / S3 across regions vs. the security-tooling regions).
4. **IAM cross-check** with reconciled identity inventory.
5. **Federation candidate identification** — IAM users with email matching an M365 / AD user = SSO migration candidate.
6. Proposed-metric gaps.

### Step 13 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | Cloud infrastructure, not endpoint. |
| CIS Controls (v8.1) | ✅ | Maps to CIS 1.1 (cloud asset inventory), 3.3 (data access), 3.11 (encryption at rest — S3/EBS/RDS), 3.10 (encryption in transit — TLS/HTTPS-only buckets), 4.1 (centralized config — Organizations / SCPs), 5.1 / 5.4 (IAM inventory + admin separation), 6.3 / 6.4 (IAM MFA), 6.5 (root MFA), 8.2 / 8.5 / 8.11 (CloudTrail audit logging), 12.2 (boundary protection — security groups), 13.1 / 13.6 (GuardDuty IDS), 14.6 (DLP — partial via Macie). |
| Cyber-insurance domain files | ✅ | Aligns with `domains/auth.md` (IAM MFA + privileged audit), `domains/endpoint.md` (EC2 patching — partial via Inspector), `domains/network.md` (VPC + security groups extend the boundary-protection story), `domains/governance.md` (CloudTrail audit), `domains/regulatory.md` (HIPAA / PCI / SOC2 controls — S3 encryption, KMS, log retention). |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this when AWS is deployed; surfaces IAM MFA %, S3 public buckets, GuardDuty findings, cost anomalies. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| Root account has access key | "URGENT: Root account has access key. Delete immediately; root must not have programmatic credentials." |
| Root MFA disabled | "URGENT: Root MFA not enabled. Configure hardware MFA token on root immediately." |
| IAM user without MFA | "<N> IAM users with console access lack MFA. Enforce via IAM password policy + condition-key SCP." |
| IAM access key old | "<N> access keys > <N> days old. Rotate or delete." |
| Unused IAM user | "<N> IAM users inactive > <N> days. Confirm separation, disable / delete." |
| IAM user with AdministratorAccess | "<N> IAM users have AdministratorAccess attached. Switch to role-based assume + condition-key constraints." |
| IAM role open to world | "URGENT: <N> IAM roles allow `Principal: *` AssumeRole. Restrict to specific accounts / external IDs." |
| Weak IAM password policy | "Tighten IAM password policy: min length 14, complexity required, reuse history ≥ 24, max age ≤ 90 days." |
| S3 public bucket | "URGENT: <N> S3 buckets allow public read/write. Block public access at account + bucket level." |
| S3 bucket without encryption | "<N> S3 buckets without default encryption. Enable SSE-S3 or SSE-KMS." |
| S3 bucket without versioning | "<N> S3 buckets without versioning. Enable for accidental-deletion protection." |
| Open SSH/RDP/DB to 0.0.0.0/0 | "URGENT: <N> security groups allow <port> from 0.0.0.0/0. Restrict to bastion / VPN allowlist." |
| Default security group modified | "<N> default security groups have non-default rules. Restore defaults; create explicit SGs." |
| VPC flow logs disabled | "Enable VPC flow logs on <N> VPCs. Required for boundary-protection evidence." |
| CloudTrail not multi-region | "Enable multi-region CloudTrail. Required for full audit coverage." |
| CloudTrail log-file validation off | "Enable CloudTrail log-file validation for integrity assurance." |
| GuardDuty disabled / partial | "Enable GuardDuty across all regions. Currently active in <N>/<total>." |
| Security Hub disabled | "Enable Security Hub for continuous compliance scoring." |
| GuardDuty critical findings open | "<N> critical GuardDuty findings open. Triage immediately." |
| Public EBS snapshot / AMI | "URGENT: <N> public EBS snapshots / AMIs. Restrict to account-only access." |
| RDS publicly accessible | "<N> RDS instances publicly accessible. Move to private subnet or restrict via SG." |
| RDS unencrypted | "<N> RDS instances unencrypted at rest. Migrate to encrypted snapshot." |
| KMS key without rotation | "<N> customer KMS keys without automatic rotation. Enable annual rotation." |
| Cost anomaly | "<N> cost anomalies in current period (<$N> impact). Investigate." |
| Low RI / Savings Plan coverage | "Reserved Instance / Savings Plan coverage at <N>%. Review committed-use opportunities." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Per-service usage history | partial | AWS Cost Explorer / Athena Cost & Usage Reports |
| AWS Config rule compliance history | partial | AWS Config Console |
| Macie sensitive-data findings | partial / external | Macie Console |
| Per-CloudTrail-event detail | partial | CloudTrail / Athena |
| Cross-account role usage frequency | partial | CloudTrail |
| Resource tagging compliance | partial | AWS Config / Cost Categories |

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST + liongard_system LIST | per inspector | array | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3-11 | liongard_metric VALUE | envId=<ENV_ID> sysId=<SYS_ID> metric=<id> | varies | ok per metric |
| 10 | liongard_device LIST | envId=<ENV_ID> filter=inspectors contains aws | array<device> | ok |
| 12 | QA pass | per `reference/qa-retry-pattern.md` | varies | ok |
| 13 | render | per `output.format` | <artifact path> | ok |
```

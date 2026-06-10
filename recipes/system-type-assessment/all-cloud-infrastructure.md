---
name: all-cloud-infrastructure
description: >
  Use this skill when the user wants a cross-cloud infrastructure assessment
  spanning AWS accounts, Azure subscriptions, and Google Workspace tenants —
  multi-account IAM posture, encryption and logging status, public-access
  exposure, security tooling coverage (GuardDuty / Defender for Cloud /
  Workspace security settings), cost anomalies, and a unified cross-cloud
  recommendation set. Trigger phrases: "cloud infrastructure assessment for
  <customer>", "AWS + Azure review", "multi-cloud posture", "cloud security
  rollup", "cross-cloud IAM audit", "cloud environment review", "cloud PBR",
  "all cloud accounts review". Chains aws.md, azure.md, and google-workspace.md
  per discovered instance; produces a unified cloud posture report.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_launchpoint, liongard_metric, liongard_identity, liongard_device, liongard_cyber_risk_dashboard, liongard_detection, liongard_alert"
personas: [soc, technical-alignment-manager, vcio-account-manager, accounting-finance]
output_formats: [markdown, word, xlsx]
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
  - metrics:azure:enabled-subscriptions-count
  - metrics:azure:nsg-rdp-exposed-count
  - metrics:azure:nsg-rdp-exposed-list
  - metrics:azure:subnets-list
  - metrics:azure:virtual-machine-count
  - metrics:azure:virtual-machines-list
  - metrics:google-workspace:groups-open-membership-count
  - metrics:google-workspace:less-secure-app-access-enabled
  - metrics:google-workspace:licensing-utilization-pct
  - metrics:google-workspace:super-admin-count
  - metrics:google-workspace:super-admin-list
  - metrics:google-workspace:third-party-apps-unverified-count
  - metrics:google-workspace:twostep-coverage-pct
  - metrics:google-workspace:twostep-enforced-count
  - metrics:google-workspace:users-stale-count
  - metrics:google-workspace:users-total-count
---

# System-Type Assessment — All Cloud Infrastructure

> **Composite recipe.** Covers AWS (Inspector ID 1), Microsoft Azure (ID 11),
> and Google Workspace (ID 61). Chains the three per-cloud single-system
> recipes and produces a unified cross-cloud posture report. Run the
> per-cloud single-system recipes first for per-account detail; this rollup
> provides the executive-level cross-cloud summary.
>
> **Scope boundaries:**
> - **AWS** covers IAM, VPC/SGs, S3, KMS, CloudTrail, GuardDuty, Security Hub.
>   Multi-account environments (Organizations / Control Tower) have one
>   Liongard system per AWS account — this rollup aggregates across all.
> - **Azure** covers RBAC, NSGs, storage accounts, Key Vault, Defender for
>   Cloud, Sentinel. One system per Azure subscription. **Identity (Entra ID /
>   Azure AD) lives in the `microsoft-365-inspector` — NOT here.**
> - **Google Workspace** covers identity (users, 2SV, admins), OU/group
>   structure, third-party app access, and tenant-level security settings. GWS
>   is **both** a cloud identity platform and a SaaS productivity suite; this
>   rollup covers the security settings and identity posture. File storage
>   detail (Google Drive) lives in the separate `google-drive-inspector`.
>
> **Google Workspace identity cross-over:** GWS also feeds
> `recipes/system-type-assessment/all-identity-providers.md`. For a multi-IdP
> identity rollup (GWS + M365 + JumpCloud + Duo + etc.), use that recipe. This
> rollup focuses on GWS as *infrastructure* — security configuration, admin
> posture, third-party app exposure.
>
> **References:** `recipes/single-system-analysis/by-inspector/aws.md`,
> `recipes/single-system-analysis/by-inspector/azure.md`,
> `recipes/single-system-analysis/by-inspector/google-workspace.md`,
> `reference/cross-cutting-signals.md`, `reference/asset-fields.md`.

---

## Customize for your MSP

```yaml
output:
  format: markdown              # markdown | word | xlsx
  filename: "<customer>-cloud-infrastructure-review-<YYYY-MM-DD>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Cloud Infrastructure Executive Summary"
  scope_discovery: "Cloud Accounts in Scope"
  cross_cloud_iam: "Cross-Cloud IAM & Identity Summary"
  aws_summary: "Amazon Web Services"
  azure_summary: "Microsoft Azure"
  gws_summary: "Google Workspace"
  encryption_logging: "Encryption & Audit Logging"
  public_exposure: "Public Exposure & External Access"
  security_tooling: "Security Tooling Coverage"
  cost_anomalies: "Cost Anomalies & Optimization"
  change_summary: "Material Changes (Detection Window)"
  recommendations: "Cross-Cloud Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"              # technical | balanced | executive
  reading_level: "manager"

clouds_in_scope:
  aws: true
  azure: true
  google_workspace: true

slas:
  mfa_coverage_pct_min: 100     # cloud admin MFA; GWS 2SV + AWS root MFA + Azure PIM
  public_s3_buckets_max: 0      # zero tolerance for public S3 buckets
  public_storage_accounts_max: 0
  cloudtrail_enabled: true      # all AWS accounts should have CloudTrail
  activity_log_enabled: true    # all Azure subscriptions
  guarduty_enabled: true        # all AWS accounts
  defender_enabled: true        # all Azure subscriptions
  inspector_lastseen_days_max: 7
  owner_count_max: 3            # Azure Owner-role count above N flagged
  aws_root_mfa_required: true
  access_key_age_days_max: 90   # IAM access keys older than N days

naming:
  client_term: "Client"
  environment_term: "Environment"
  account_term: "Account"       # AWS account | Azure subscription | GWS tenant

qa:
  retry_on_null: true
  retry_on_empty_array: false
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: false
```

---

## When to use

- **Quarterly cloud review / PBR** — consolidated cross-cloud posture, IAM
  drift, logging gaps, and cost anomalies in a single deliverable.
- **Onboarding cloud assessment** — establish baseline security posture across
  all cloud accounts for a new customer.
- **Cyber-insurance evidence** — IAM/MFA posture, encryption at rest/in transit,
  audit logging, and security tooling coverage for cloud platforms.
- **Executive briefing** — "how secure is our cloud footprint?" with per-
  platform traffic-light status.

---

## Inputs

| Input | How to obtain |
|---|---|
| `environmentId` | `liongard_environment LIST` — customer's env ID |
| AWS system IDs | `liongard_launchpoint LIST inspectorId=1 environmentId=<ENV>` |
| Azure system IDs | `liongard_launchpoint LIST inspectorId=11 environmentId=<ENV>` |
| GWS system IDs | `liongard_launchpoint LIST inspectorId=61 environmentId=<ENV>` |

---

## Workflow

### Step 1 — Scope discovery: enumerate all cloud accounts

```
liongard_launchpoint LIST
  inspectorId=1
  environmentId=<ENV_ID>
  fields=["id", "system", "environment", "latestInspectionDate", "status"]
```

Repeat for Azure (inspectorId=11) and GWS (inspectorId=61).

Build a scope table:

| Platform | Account / Subscription / Tenant | System ID | Last Inspected | Status |
|---|---|---|---|---|
| AWS | `<account alias>` | `<id>` | `<date>` | `<status>` |
| Azure | `<subscription name>` | `<id>` | `<date>` | `<status>` |
| GWS | `<tenant domain>` | `<id>` | `<date>` | `<status>` |

Flag any account with status "Agent Issue" or inspection date older than
`slas.inspector_lastseen_days_max` days — data may be stale.

---

### Step 2 — Inspection timeline: confirm data freshness

```
liongard_timeline GET
  environmentId=<ENV_ID>
  inspectorIds=[1, 11, 61]
```

Confirm that the most recent inspection for each cloud platform is within the
acceptable window. Surface stale inspections in the manual-verification
appendix.

---

### Step 3 — Cross-cloud identity summary (reconciled)

```
liongard_identity COUNT
  environmentId=<ENV_ID>
```

This reconciled count deduplicates across AWS IAM, Entra ID (M365), and GWS
identities by email address. Use this as the authoritative user count for the
executive summary — do NOT sum per-inspector user counts.

For MFA/2FA coverage across all cloud identities:

```
liongard_identity COUNT
  environmentId=<ENV_ID>
  mfaStatus="NO"
  enabled=true
```

Flag if any enabled identities have `mfaStatus="NO"`.

---

### Step 4 — AWS: per-account security posture

For each AWS system ID discovered in Step 1, chain
`recipes/single-system-analysis/by-inspector/aws.md` or run the following
summary queries:

**IAM posture:**

```
liongard_metric EVALUATE
  jmesPathQuery="IAM.{rootMfaEnabled: RootMFAEnabled, usersWithoutMfa: UsersWithoutMFA,
    accessKeysOlderThan90: AccessKeysOlderThan90Days, userCount: UserCount}"
  systemId=<AWS_SYSTEM_ID> environmentId=<ENV_ID>
```

**CloudTrail enabled:**

```
liongard_metric EVALUATE
  jmesPathQuery="CloudTrail.{enabled: Enabled, multiRegion: MultiRegionEnabled}"
  systemId=<AWS_SYSTEM_ID> environmentId=<ENV_ID>
```

**GuardDuty enabled:**

```
liongard_metric EVALUATE
  jmesPathQuery="GuardDuty.Enabled"
  systemId=<AWS_SYSTEM_ID> environmentId=<ENV_ID>
```

**Public S3 buckets:**

```
liongard_metric EVALUATE
  jmesPathQuery="S3.Buckets[?PublicAccess == `true`].Name"
  systemId=<AWS_SYSTEM_ID> environmentId=<ENV_ID>
```

> **Note:** The exact JMESPath field names above reflect the expected AWS
> inspector schema structure. Confirm field names via `GET_OVERVIEW` on a
> live AWS system — the aws.md single-system recipe has validated paths.
> Label any path that differs from the single-system recipe as
> SCHEMA_CONFIRMED on the specific system tested.

For each AWS account, produce a traffic-light summary:

| Control | Status | Notes |
|---|---|---|
| Root MFA enabled | ✅/🔴 | |
| No IAM users without MFA | ✅/🔴 | N users without MFA |
| Access keys ≤ 90 days old | ✅/🟡 | N keys exceeding threshold |
| CloudTrail enabled (all regions) | ✅/🔴 | |
| GuardDuty enabled | ✅/🔴 | |
| Zero public S3 buckets | ✅/🔴 | N public buckets found |

---

### Step 5 — Azure: per-subscription security posture

For each Azure system ID, chain
`recipes/single-system-analysis/by-inspector/azure.md` or run summary queries:

**RBAC Owner count:**

```
liongard_metric EVALUATE
  jmesPathQuery="RBAC.RoleAssignments[?RoleName == 'Owner'] | length(@)"
  systemId=<AZURE_SYSTEM_ID> environmentId=<ENV_ID>
```

**Defender for Cloud enabled:**

```
liongard_metric EVALUATE
  jmesPathQuery="Defender.Enabled"
  systemId=<AZURE_SYSTEM_ID> environmentId=<ENV_ID>
```

**Activity Log enabled:**

```
liongard_metric EVALUATE
  jmesPathQuery="ActivityLog.Enabled"
  systemId=<AZURE_SYSTEM_ID> environmentId=<ENV_ID>
```

**Public storage accounts:**

```
liongard_metric EVALUATE
  jmesPathQuery="StorageAccounts[?PublicAccess == `true`].Name"
  systemId=<AZURE_SYSTEM_ID> environmentId=<ENV_ID>
```

> **Note:** Confirm field names via `GET_OVERVIEW` on a live Azure system.
> Azure AD / Entra ID identity data is in the `microsoft-365-inspector`, NOT
> in the Azure inspector — do not look for user MFA data here.

Per-subscription traffic light:

| Control | Status | Notes |
|---|---|---|
| Owner-role count ≤ `slas.owner_count_max` | ✅/🟡 | N Owner assignments |
| Defender for Cloud enabled | ✅/🔴 | |
| Activity Log enabled | ✅/🔴 | |
| Zero public storage accounts | ✅/🔴 | N public containers |
| Sentinel deployed | ✅/⚪ (informational) | |

---

### Step 6 — Google Workspace: security posture

For each GWS system ID, chain
`recipes/single-system-analysis/by-inspector/google-workspace.md` or run
summary queries:

**2-Step Verification (2SV) coverage:**

```
liongard_metric EVALUATE
  jmesPathQuery="Users[?isEnrolledIn2Sv == `false` && suspended == `false`].
    {name: name, email: primaryEmail}"
  systemId=<GWS_SYSTEM_ID> environmentId=<ENV_ID>
```

**Super admin count:**

```
liongard_metric EVALUATE
  jmesPathQuery="Users[?isAdmin == `true` && suspended == `false`] | length(@)"
  systemId=<GWS_SYSTEM_ID> environmentId=<ENV_ID>
```

**Third-party app count:**

```
liongard_metric EVALUATE
  jmesPathQuery="ThirdPartyApps | length(@)"
  systemId=<GWS_SYSTEM_ID> environmentId=<ENV_ID>
```

> **Note:** Confirm field names via `GET_OVERVIEW` on a live GWS system — the
> google-workspace.md single-system recipe has validated paths. Label
> SCHEMA_CONFIRMED on first use until validated against your environment.

GWS traffic light:

| Control | Status | Notes |
|---|---|---|
| 2SV enforced for all users | ✅/🔴 | N users without 2SV |
| Super admin count reasonable | ✅/🟡 | N super admins |
| Third-party app access reviewed | ✅/🟡 (informational) | N apps authorized |
| Domain verified | ✅/⚪ | |

---

### Step 7 — Material changes in the review window

```
liongard_detection LIST
  environmentId=<ENV_ID>
  inspectorIds=[1, 11, 61]
  startDate=<WINDOW_START>
  endDate=<WINDOW_END>
```

Review changes since the last assessment for:
- New IAM users or role assignments (AWS/Azure)
- New OAuth / third-party app authorizations (GWS)
- Security tooling toggled off (GuardDuty, Defender, 2SV enforcement)
- New public-access buckets or storage accounts
- New admin/owner assignments

---

### Step 8 — Cross-cloud alerts in the review window

```
liongard_alert LIST
  environmentId=<ENV_ID>
  inspectorIds=[1, 11, 61]
  startDate=<WINDOW_START>
```

Surface any cloud-inspector alerts as action items in the deliverable.

---

### Step 9 — QA pass & manual-verification appendix

Apply the QA retry pattern (`reference/qa-retry-pattern.md`):

- Retry null evaluations up to `qa.retry_attempts` times.
- Flag any cloud account with `latestInspectionDate` older than
  `qa.flag_inspector_lastseen_threshold_days` days.
- Compare reconciled `liongard_identity COUNT` to the sum of per-inspector
  user counts — flag divergence as a data-quality note (deduplication
  expected; the reconciled count should be lower).

Build the **Manual verification** appendix:

| Item | Reason | Action |
|---|---|---|
| Public S3 bucket or Azure container found | Automated data exposure risk | Review bucket policy; make private unless intentionally public CDN |
| Root MFA not enabled (AWS) | Highest-privilege account unprotected | Enable MFA on root account; store credentials in vault |
| CloudTrail / Activity Log disabled | Audit trail gap | Enable immediately in all regions/subscriptions |
| GuardDuty / Defender disabled | Threat detection gap | Enable and review initial findings |
| Owner count exceeds SLA | Excess privileged assignments | Review and remove unnecessary Owner-role assignments |
| Stale inspection (> `slas.inspector_lastseen_days_max` days) | Data may not reflect current state | Trigger manual inspection; confirm credentials are valid |

---

## Insights & recommendations

| Condition | Finding | Recommendation |
|---|---|---|
| Any enabled identity with `mfaStatus="NO"` | **MFA gap — [N] cloud identities without MFA** | Enforce MFA across all cloud platforms. Highest priority: admin/owner roles. |
| Public S3 bucket or storage account exists | **Public cloud storage — [N] buckets/containers** | Review immediately; apply Block Public Access (AWS) or disable public container access (Azure). |
| CloudTrail / Activity Log disabled on any account | **Audit logging gap** | Enable logging in all regions; logs are the primary evidence source for breach investigation and compliance. |
| GuardDuty / Defender not enabled | **Threat detection gap** | Enable and integrate with the MSP's SIEM or alert workflow. |
| AWS root MFA not enabled | **Critical — root account unprotected** | Enable MFA on AWS root account immediately; this is the single highest-value target in AWS. |
| IAM access keys older than `slas.access_key_age_days_max` days | **Stale access keys — [N] keys** | Rotate all keys exceeding threshold; implement key rotation policy. |
| GWS 2SV not enforced | **2SV gap — [N] users without 2SV** | Enforce 2SV in GWS Admin → Security → 2-Step Verification. |
| Azure Owner count > `slas.owner_count_max` | **Excess Owner assignments** | Review and reduce; apply PIM (Privileged Identity Management) for just-in-time access. |
| No security tooling across any cloud platform | **Security visibility gap** | Prioritize GuardDuty (AWS), Defender for Cloud (Azure), GWS Advanced Security. Consider MDR/SIEM integration. |
| Significant change-detection activity | **[N] cloud changes detected in [window]** | Review change log with customer; confirm all changes were authorized. |

---

## Data gaps

| Field | Gap type | Alternative |
|---|---|---|
| AWS account-level cost breakdown | not in current dataprint — billing scope varies by inspector version | AWS Cost Explorer or CUR report |
| Azure cost anomalies / reserved instance coverage | not in dataprint | Azure Cost Management |
| GWS license utilization per SKU | not in current dataprint — requires Workspace Admin Reports API scope | GWS Admin → Reports → Accounts |
| AWS Config compliance rules | not in dataprint | AWS Config console |
| Azure Policy compliance state | not in dataprint | Azure Policy compliance blade |
| GWS device management (BeyondCorp / MDM) | not in dataprint | GWS Admin → Devices |
| Multi-account AWS Organizations hierarchy | not in current dataprint — one system per account; org-level view not yet in inspector | AWS Organizations console |

---

## Coverage cross-check

| Source | Coverage notes |
|---|---|
| Partner QA matrix | Cloud infrastructure not in partner audit. This recipe covers the functional equivalents: user/admin counts, MFA state, public exposure, logging, and threat-detection tooling. |
| CIS Controls v8.1 | CIS 1.1 (asset inventory — accounts/subscriptions scoped), CIS 5 (account management — IAM/admin audit), CIS 6.3 (MFA), CIS 8 (audit logging — CloudTrail/Activity Log), CIS 13 (network monitoring — GuardDuty/Defender). |
| Cyber-insurance domain files | Feeds `domains/auth.md` (MFA for cloud admins), `domains/network.md` (public exposure, security groups/NSGs), `domains/governance.md` (access reviews, admin count). |
| QBR recipe | Chain this recipe in QBR Step 8 for "Cloud Infrastructure" section. Surface IAM drift, public-access findings, security tooling gaps, and cost anomalies as QBR highlights. |

---

## Output format

**Default: Markdown** — suitable for TAM review notes and ticket attachments.
**Word**: use for customer-facing quarterly cloud security report.
**Excel**: use for multi-account/multi-subscription fleet comparison — one
row per account with traffic-light status for each control domain.

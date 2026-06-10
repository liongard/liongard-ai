---
name: cyber-insurance-vendor
description: >
  Domain reference for the cyber-insurance-readiness master skill. Covers Vendor & Third-Party
  (VND-1 through VND-8). Used as a sub-reference when answering cyber insurance underwriting
  questions in this control area.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_asset"
personas: [vcio-account-manager, soc, technical-alignment-manager]
primitives:
  - metrics:active-directory:stale-users-count
  - metrics:aws:cloudtrails-enabled
  - metrics:aws:running-ec2-instances-count
  - metrics:aws:s3-buckets-count
  - metrics:axcient-x360-recover:appliance-health-status
  - metrics:azure:virtual-machine-count
  - metrics:microsoft-365:stale-licensed-users-count
---


```yaml
customize:
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed
```
# Cyber Insurance — Domain: Vendor & Third-Party

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


**Inspectors referenced:** Active Directory, Microsoft 365, AWS, Azure, Cove, Axcient

**Question coverage:** VND-1 through VND-8

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

## Coverage Summary

| Question | CIS | Liongard Signal | Coverage |
|---|---|---|---|
| VND-1 | CIS 15.1 | None | ℹ️ MANUAL |
| VND-2 | CIS 6.2 | AD stale computers, M365 stale users | ⚠️ PARTIAL |
| VND-3 | CIS 6.2 | M365 stale users, AD disabled users | ✅ LIONGARD (access state) |
| VND-4 | CIS 8.2 | AWS CloudTrail | ⚠️ PARTIAL |
| VND-5 | N/A | None | ℹ️ MANUAL |
| VND-6 | N/A | None | ℹ️ MANUAL |
| VND-7 | N/A | AWS EC2/S3, Azure VMs | ⚠️ PARTIAL |
| VND-8 | N/A | Cove/Axcient backup health | ⚠️ PARTIAL |

---

## VND-1 — Written Vendor Security Policies

**Form source:** Travelers Q17a  
**Coverage:** `ℹ️ MANUAL`

**Question:** Does the organization maintain written policies specifying appropriate vendor
information security controls?

**Evidence to collect:**
- Named policy document (e.g., "Vendor Management Policy", "Third-Party Risk Policy")
- Date of most recent review/approval
- Whether the policy defines minimum security requirements for vendors (e.g., MFA, encryption,
  incident notification SLA)
- Whether the policy is referenced in vendor contracts

**Note:** Many insurers accept a Vendor Risk Assessment questionnaire process as equivalent
to a written policy. If the org uses a standardized vendor risk questionnaire (e.g., CAIQ, SIG),
document the questionnaire name and how often it is administered.

---

## VND-2 — Periodic Review of Vendor Access Rights

**Form source:** Travelers Q17b  
**Coverage:** `⚠️ PARTIAL`

**Question:** Does the organization conduct periodic reviews of and updates to vendor access rights?

**Fetch protocol:**
1. Resolve system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. Evaluate: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record → Vendor & Third-Party sheet evidence column; set Status in status column

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | Active Directory | Active Directory: Stale Computer Accounts Count | `Computers[?Activity==\`Stale\`&&Enabled==\`true\`]\|length(@)` | 0 |
| ✅ | Active Directory | Active Directory: Stale Computer Accounts List | `Computers[?Enabled==\`true\`&&Activity==\`Stale\`].Name` | empty |
| ✅ | Microsoft 365 | Office 365: Stale or Disused User Accounts Count | `length(Users[?activeLast30Days==\`false\`&&accountEnabled==\`true\`])` | 0 |
| ✅ | Microsoft 365 | Office 365: Stale or Disused User Accounts List | `Users[?activeLast30Days==\`false\`&&accountEnabled==\`true\`].displayName` | empty |

**Manual component:** Liongard confirms 0 stale active accounts as evidence of hygiene, but a
formal vendor access review cadence (e.g., quarterly review by the IT manager) requires written
attestation. Document: review frequency, reviewer role, and most recent review date.

---

## VND-3 — Prompt Revocation of Vendor Access

**Form source:** Travelers Q17c  
**Coverage:** `✅ LIONGARD` (access state confirmed)

**Question:** Does the organization promptly revoke vendor access rights when access is no longer needed?

**Fetch protocol:**

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | Microsoft 365 | Office 365: Stale or Disused User Accounts List | `Users[?activeLast30Days==\`false\`&&accountEnabled==\`true\`].displayName` | empty |
| ✅ | Microsoft 365 | Office 365: Stale or Disused User Accounts Count | `length(Users[?activeLast30Days==\`false\`&&accountEnabled==\`true\`])` | 0 |
| ✅ | Active Directory | Active Directory: Stale User Accounts Count | `Users[?UserActivity==\`Stale\`&&DefaultSystemUser==\`false\`]\|length(@)` | 0 |
| ✅ | Active Directory | Active Directory: Disabled Users List | `Users[?UserStatus==\`Disabled\`].Name` | review — confirm ex-vendors present |
| ✅ | Microsoft 365 | M365: Users not signed in over 90 days | `Users[?signInActivity.daysSinceLastSignIn>\`90\`].displayName` | 0 |

**Interpretation:**
- 0 stale active accounts + disabled list showing timely disablement = strong evidence of prompt revocation
- Cross-reference disabled list timestamps if available (AD `whenChanged` attribute) to show revocation within SLA
- If the organization uses a ticketing system for vendor offboarding, attach a sample ticket as supplemental evidence

---

## VND-4 — Logging & Monitoring of Vendor Access

**Form source:** Travelers Q17d  
**Coverage:** `⚠️ PARTIAL`

**Question:** Does the organization log and monitor vendor access to its computer systems?

**Fetch protocol:**

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | AWS | Amazon Web Services: CloudTrails Enabled | `CloudTrailsActivated` | true — all regions |

**Manual component:** CloudTrail confirms AWS API-level logging. For broader vendor access monitoring:
- **On-premises:** Confirm Windows Event Log forwarding or SIEM integration captures vendor login events
- **SaaS vendors:** Confirm admin audit logs are enabled in each SaaS platform (M365 Unified Audit Log, etc.)
- **Privileged Access:** If using a PAM tool (CyberArk, BeyondTrust, etc.), document vendor sessions are recorded

**Supporting metrics for M365 admin access logging:**

| Evidence | Inspector | Metric Name | Compliant When |
|---|---|---|---|
| ✅ | Microsoft 365 | Azure AD: Conditional Access Policies List | CA policies active — confirms sign-in event logging is available |
| ✅ | AWS | CloudTrails Enabled | true — all API calls logged |

---

## VND-5 — Vendor Cyber Insurance Requirement

**Form source:** Travelers Q17e  
**Coverage:** `ℹ️ MANUAL`

**Question:** Does the organization require vendors to carry their own Professional Liability or
Cyber Liability insurance?

**Evidence to collect:**
- Standard contract clause or vendor onboarding checklist item requiring COI (Certificate of Insurance)
- Minimum coverage amounts specified (e.g., $1M cyber liability)
- Process for collecting and verifying COIs annually
- List of critical vendors and their confirmed coverage (if available)

---

## VND-6 — Hold Harmless / Indemnity Clauses

**Form source:** Travelers Q17f  
**Coverage:** `ℹ️ MANUAL`

**Question:** Do vendor contracts contain hold harmless / indemnity clauses that benefit the organization?

**Evidence to collect:**
- Standard contract template with indemnification language
- Legal counsel confirmation that clauses are enforceable
- Note any critical vendor contracts lacking these clauses (risk exceptions)

---

## VND-7 — Outsourced Services Inventory

**Form source:** Travelers Q18  
**Coverage:** `⚠️ PARTIAL`

**Question:** Which services are outsourced, and to which providers? (Data backup, data center
hosting, IT infrastructure, IT security, web hosting, payment processing, physical security,
software development, customer marketing, data processing)

**Liongard can confirm cloud asset presence (partial inventory):**

**Fetch protocol:**

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | AWS | Amazon Web Services: Running EC2 Instances Count | `SystemInfo.NumRunningEC2Instances` | document count |
| ✅ | AWS | Amazon Web Services: S3 Buckets Count | `SystemInfo.NumS3Buckets` | document count |
| ✅ | Azure | Azure: Virtual Machine Count | `VirtualMachines\|length(@)` | document count |
| ✅ | Google G Suite | Google G Suite: Active Users Count | `length(Users[?archived==\`false\`&&suspended==\`false\`])` | document count |

**Manual inventory template** (complete for each outsourced function):

| Function | Outsourced? | Provider Name | Criticality | Alt Solution? |
|---|---|---|---|---|
| Data backup | | | | |
| Data center / hosting | | | | |
| IT infrastructure | | | | |
| IT security / SOC | | | | |
| Web hosting | | | | |
| Payment processing | | | | |
| Physical security | | | | |
| Software development | | | | |
| Customer marketing | | | | |
| Data processing | | | | |

**If data center hosting or IT infrastructure is outsourced:** Document the likely impact to the
organization if those services become unavailable, and whether an alternative solution exists.

---

## VND-8 — Alternative Solutions for Provider Failure

**Form source:** Travelers Q18 follow-on  
**Coverage:** `⚠️ PARTIAL`

**Question:** Does the organization have an alternative solution in the event of a failure or outage
of a critical outsourced service provider?

**Fetch protocol:**

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | Cove Data Protection | Cove: Count of Failed Backups | `Devices[?BackupStatus==\`Failed\`]\|length(@)` | 0 |
| ✅ | Axcient | Axcient: Appliance Health Status | `Appliances[].health_status` | healthy |
| ✅ | Cove Data Protection | Cove: 24h Since Last Completed Device Backup | `Devices[?Type==\`BackupManager\`&&HoursSinceLastCompleted>\`24\`]\|length(@)` | 0 |

**Manual component:** Liongard backup health metrics confirm that recovery infrastructure is
operational. The alternative solution question also requires:
- Documented failover plan for each critical provider
- RTO (Recovery Time Objective) for each function
- Whether the alternative has been tested (cross-reference Q15 / Q5b in Assessment sheet)

---

## Interpretation Key

| Status | Meaning |
|---|---|
| ✅ LIONGARD | Metric confirms the control state — record value and mark compliant/non-compliant |
| ⚠️ PARTIAL | Liongard provides supporting evidence; written policy also required |
| ℹ️ MANUAL | No Liongard metric — collect written attestation, policy doc, or contract clause |

---

## Cross-References to Assessment Sheet

| Vendor Control | Related Assessment Questions |
|---|---|
| VND-2/3 (access review/revocation) | Q30 (termination process), Q31 (inactive accounts), Q29 (access approval) |
| VND-4 (vendor access logging) | Q42 (audit logging policy) |
| VND-7 (cloud assets) | Q19 (cloud assets maintained), Q20 (cloud credentials) |
| VND-8 (alt solutions) | Q5/Q5a/Q5b (backup), Q46 (BCP) |

---
name: cyber-insurance-auth
description: >
  Domain reference for the cyber-insurance-readiness master skill. Covers Authentication, MFA & Access Control
  (Q2–Q4, Q6–Q7 (incl. 6a–6f), Q14–Q17, Q30–Q31, Q38–Q39). Used as a sub-reference when answering cyber insurance underwriting
  questions in this control area.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_identity"
personas: [vcio-account-manager, soc, technical-alignment-manager]
primitives:
  - metrics:active-directory:guest-account-enabled
  - metrics:active-directory:lockout-threshold
  - metrics:active-directory:min-password-length
  - metrics:active-directory:password-complexity-enabled
  - metrics:active-directory:password-reversible-encryption
  - metrics:active-directory:privileged-users-count
  - metrics:active-directory:stale-users-count
  - metrics:cisco-meraki:privileged-user-count
  - metrics:cisco-meraki:privileged-user-list
  - metrics:cove-data-protection:count-users-without-2fa
  - metrics:cove-data-protection:list-users-without-2fa
  - metrics:crowdstrike:high-risk-users-list
  - metrics:crowdstrike:inactive-users-count-30d
  - metrics:crowdstrike:users-without-mfa-count
  - metrics:microsoft-365:admin-users-mfa-disabled-count
  - metrics:microsoft-365:conditional-access-policies-list
  - metrics:microsoft-365:privileged-users-count
  - metrics:microsoft-365:security-defaults-enabled
  - metrics:microsoft-365:users-not-mfa-registered-count
  - metrics:palo-alto-panos:device-admins
  - metrics:sentinelone:console-users-without-mfa-list
  - metrics:sonicwall:admin-username
  - metrics:sonicwall:http-management-enabled
  - metrics:sonicwall:local-users-count
  - metrics:sonicwall:min-password-length
  - metrics:sonicwall:otp-config-count
  - metrics:sonicwall:user-lockout-enabled
  - metrics:veeam-availability-console:portal-administrator-list
  - metrics:watchguard:account-lockout-disabled-count
  - metrics:windows-server:local-admin-list
  - metrics:windows-workstation:guest-account-disabled
---


```yaml
customize:
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed
```
# Cyber Insurance — Domain: Authentication, MFA & Access Control

> **Pairs with:** `recipes/compliance/cyber-insurance/cyber-insurance-readiness.md`. The master file
> documents the workflow, customization block, asset-inventory schema, and gap-summary
> output. This domain file documents the metric names and JMESPath queries for each
> question in this control area.

> **Asset Inventory First.** The master recipe (Step 2) pulls `liongard_identity LIST`
> and `liongard_device LIST` before this domain file runs. The reconciled identity
> record already synthesizes cross-system signals into a single authoritative answer
> for the MFA, dormancy, and privileged-account questions:
>
> - **`mfaStatus`** (`YES` / `NO` / `PARTIAL`) — confirmed from **any** connected
>   system. An identity shown as "MFA not registered" in M365 native MFA may still
>   have `mfaStatus = "YES"` because Duo is enrolled, Conditional Access enforces an
>   MFA claim, or another IdP confirmed it. **Do not conclude MFA is absent from a
>   single-inspector metric when `mfaStatus = "YES"` on the identity record.**
> - **`accountActivity`** (`Active` / `Stale` / `Dormant` / `Never Used`) —
>   cross-system synthesized staleness. Use for Q30/Q31 rather than computing from
>   per-IdP last-login fields individually.
> - **`privileged`** (bool) — elevated in any connected system.
>
> Per-inspector metrics in this file are the **cross-check and configuration detail
> layer** — they confirm the reconciled answer and surface inspector-unique fields
> (AD password policy, Conditional Access policy names, firewall rule counts) that
> don't roll up to the identity record. When the reconciled record and a per-IdP
> metric disagree, the reconciled record wins; record the divergence as a data-quality
> flag.


**Inspectors referenced:** Active Directory, Microsoft 365, Azure AD, Duo, NinjaRMM, WatchGuard, JumpCloud, AWS, OneLogin, GSuite

**Question coverage:** Q2–Q4, Q6–Q7 (incl. 6a–6f), Q14–Q17, Q30–Q31, Q38–Q39

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

## Q2 — Do you use any default or standard passwords or credentials?
**CIS 5.2**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Active Directory | Active Directory: Account Minimum Password Length | `AccountPolicy.MinPasswordLength` | ≥14 |
| ✅ | Active Directory | Active Directory: Account Password Complexity | `AccountPolicy.PasswordComplexity` | true |
| ✅ | Active Directory | Active Directory: Default Administrator Account Enabled | `Users[?CN==`Administrator`].Enabled \| [0] \| replace(to_...` | false |
| ✅ | Active Directory | Active Directory: Default Guest Account Enabled | `DefaultGuestAccountEnabled` | false |
| ✅ | Microsoft 365 | Office 365: Accounts with Weak Passwords Count | `length(Users[?passwordPolicies.contains(to_string(@),`Dis...` | 0 |
| ✅ | Microsoft 365 | Office 365: Accounts with Weak Passwords List | `Users[?passwordPolicies.contains(to_string(@),`DisableStr...` | empty |
| ✅ | AWS | Amazon Web Services: Strong Password Policy Enabled | `StrongPasswordPolicy` | true |
| ✅ | jumpcloud-inspector | JumpCloud: User Accounts with No Password Expiration Count | `Users[?password_never_expires == \`true\`] \| length(@)` | 0 |
| ✅ | jumpcloud-inspector | JumpCloud: Count of Locked User Accounts | `Users[?status == 'LOCKED'] \| length(@)` | 0 — lockout policy confirms password enforcement |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

**Dark-web cross-check (compromised credentials):**
Several carriers explicitly ask whether the applicant has changed all known-to-be-compromised
passwords (AIG Q14, At-Bay posture assessment, Beazley controls evaluation). Liongard's
metrics above confirm *policy* (complexity, expiry, default accounts) but cannot confirm
whether credentials were exposed in a breach. Run the dark-web monitoring recipe as a
supplemental check:

```
recipes/single-system-analysis/by-inspector/dark-web-monitoring.md
```

Any exposed credentials found there should be treated as ❌ NON-COMPLIANT for the
"compromised passwords changed" question until the affected accounts are rotated and
confirmed clean on a subsequent scan.

---

## Q3 — Do you use single-factor authentication for any remote access?
**CIS 6.4**

**Step 0 — Reconciled identity check (primary answer):**
```
# How many enabled identities have NO confirmed MFA from any system?
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" privileged=true
```
If `mfaStatus="NO"` count is 0 for all enabled identities: ✅ COMPLIANT.
If count > 0: identify those users and cross-check whether a Conditional Access
policy, Duo, or other enforcement mechanism is in place (Step 1 metrics below).
**A non-zero count here is the finding; the per-inspector metrics below explain why.**

**Step 1 — Per-inspector cross-check (RDP exposure + MFA enforcement configuration):**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Windows Server | Windows Server: Is RDP Enabled? | `to_array(`[{"isRdpEnabled": true, "translatedAnswer": "Tr...` | false |
| ✅ | Windows Workstation | Windows Workstation: Is RDP Enabled? | `OS.RDPEnabled` | false |
| ✅ | azure-inspector | Azure Inspector: Network Security Rules with Exposed Default RDP Port Count | `NetworkSecurityGroups[].properties.securityRules[?propert...` | 0 |
| ✅ | azure-inspector | Azure Inspector: Network Security Rules with Exposed Default RDP Port List | `NetworkSecurityGroups[].properties.securityRules[?propert...` | empty |
| ✅ | SonicWall | SonicWall: SSL-VPN RADIUS Authentication Enabled | `SslVpn.SslVpnServer.UseRadius` | true |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q4 — Do you use single-factor authentication for any administrative access?
**CIS 6.5**

**Step 0 — Reconciled identity check (primary answer):**
```
# Privileged identities with NO confirmed MFA from any system — this is the carrier's question
liongard_identity COUNT environmentId=<ENV_ID> privileged=true mfaStatus="NO"
liongard_identity LIST environmentId=<ENV_ID> privileged=true mfaStatus="NO"
  fields=["email","displayName","mfaStatus","mfaMethod","inspectors","enabled"]
```
If count = 0: ✅ COMPLIANT (all admins have MFA confirmed from at least one system).
If count > 0: ❌ NON-COMPLIANT. The list is the evidence for the carrier.
The `mfaMethod` and `inspectors[]` fields explain which systems confirmed (or failed
to confirm) MFA for each privileged user. A user confirmed only by Conditional Access
or Duo will show here as `mfaStatus="YES"` even if M365 native MFA shows "not registered."

**Step 1 — Per-inspector cross-check (admin MFA configuration detail):**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Microsoft 365 | Office 365: Admin Users with MFA Disabled Count | `subtract(length(Users[?Privileged == `Yes`]), length(User...` | 0 |
| ✅ | Microsoft 365 | Azure Active Directory: Security Defaults Enabled Status | `SystemInfo.Overview.securityDefaults.isEnabled` | enabled |
| ✅ | Microsoft 365 | Azure Active Directory: Conditional Access Policies List | `Policies.ConditionalAccess[?state == `enabled`].displayName` | review — MFA enforced |
| ✅ | Microsoft 365 | Count of Privileged Users with no detected conditional access authentication policy that enforces multifactor authentication | `Users[?accountEnabled && Privileged == 'Yes' && length(Co...` | 0 |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q6 — Do you use MFA for [check all that apply]?
**N/A**

**Step 0 — Reconciled identity check (headline coverage):**
```
# Overall MFA coverage across all users and all systems
liongard_identity COUNT environmentId=<ENV_ID> enabled=true                   # total enabled
liongard_identity COUNT environmentId=<ENV_ID> enabled=true mfaStatus="YES"   # confirmed MFA (any system)
liongard_identity COUNT environmentId=<ENV_ID> enabled=true mfaStatus="NO"    # no MFA from any system
liongard_identity COUNT environmentId=<ENV_ID> enabled=true mfaStatus="PARTIAL" # partial
```
MFA coverage % = mfaStatus="YES" / total enabled × 100.
This single number is the carrier's headline answer. It accounts for every enforcement
mechanism Liongard observes — Conditional Access policies, Duo, Security Defaults,
JumpCloud, OneLogin, Google Workspace 2FA — without requiring separate per-IdP adds.

**Step 1 — Per-inspector cross-check (enforcement mechanism detail):**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Duo Security | Duo Security: Users Not Enrolled in MFA Count | `length(Users[?is_enrolled == `false`])` | 0 |
| ✅ | Duo Security | Duo Security: Users Not Enrolled in MFA List | `Users[?is_enrolled == `false`].{username: username, realn...` | empty |
| ✅ | NinjaRMM | NinjaRMM: Count of Users without MFA | `Users[?enabled == `true` && mfaConfigured == `false`] \| ...` | 0 |
| ✅ | NinjaRMM | NinjaRMM: List of Users without MFA | `Users[?enabled == `true` && mfaConfigured == `false`].[fi...` | empty |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q7 — What MFA product/tools are being used?
**N/A**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Microsoft 365 | Azure Active Directory: Conditional Access Policies List | `Policies.ConditionalAccess[?state == `enabled`].displayName` | review — confirms MFA method |
| ✅ | Microsoft 365 | Azure Active Directory: Security Defaults Enabled Status | `SystemInfo.Overview.securityDefaults.isEnabled` | review |
| ✅ | Microsoft 365 | Legacy Per User MFA Enabled Users Count | `Users[?perUserMfaState == 'Enabled'] \| length(@)` | review |
| ✅ | Microsoft 365 | Legacy Per User MFA Enforced Users Count | `Users[?perUserMfaState == 'Enforced'] \| length(@)` | review |
| ✅ | Microsoft 365 | Count of Users with a detected conditional access policy that enforces Duo multifactor authentication | `Users[?accountEnabled && ConditionalAccessPolicies[?conta...` | review |
| ✅ | Microsoft 365 | Count of Users with a detected conditional access policy that enforces Microsoft multifactor authentication | `Users[?accountEnabled && ConditionalAccessPolicies[?isMFA...` | review |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q14 — Do you maintain dedicated admin accounts separate from regular users?
**CIS 5.4**

**Step 0 — Reconciled privileged-identity roster (primary answer):**
```
# Cross-system privileged count and roster — elevated in ANY connected system
liongard_identity COUNT environmentId=<ENV_ID> privileged=true
liongard_identity LIST environmentId=<ENV_ID> privileged=true
  fields=["email","displayName","type","mfaStatus","accountActivity","enabled",
          "membership","inspectors","lastLogin"]
```
This gives the carrier a cross-IdP privileged roster in a single call. The
`type` field identifies service accounts (`"service"`, `"application"`) vs.
interactive admin accounts. `inspectors[]` shows which systems confirmed the
privileged flag. Per-inspector metrics below provide additional detail (M365
role names, AD group membership, local admin lists on individual servers).

**Step 1 — Per-inspector cross-check:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Microsoft 365 | Office 365: Privileged Users Count | `Users[?Privileged == `Yes`] \| length(@)` | low count |
| ✅ | Microsoft 365 | Office 365: Privileged Users List | `Users[?Privileged==`Yes`] \| sort_by(@,&id)[].[displayNam...` | review for dedicated accounts |
| ✅ | Active Directory | Active Directory: Privileged Users Count | `SystemInfo.NumPrivilegedUsers` | low count |
| ✅ | Active Directory | Active Directory: Privileged Users List | `SystemInfo.PrivilegedUsersStr` | review |
| ✅ | Microsoft 365 | Office 365: Privileged Users with Overuse Count | `length(Users[?Privileged==`Yes` && Assigned_Products])` | 0 |
| ✅ | Microsoft 365 | Office 365: Privileged Users with Overuse List | `Users[?Privileged==`Yes` && Assigned_Products].displayNam...` | empty |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q15 — How many domain admin/privileged user accounts do you maintain?
**N/A**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Microsoft 365 | Office 365: Privileged Users Count | `Users[?Privileged == `Yes`] \| length(@)` | document count |
| ✅ | Active Directory | Active Directory: Privileged Users Count | `SystemInfo.NumPrivilegedUsers` | document count |
| ✅ | Microsoft 365 | Microsoft Teams: Count of Privileged Users | `Users[?Privileged_r ==`true` && accountEnabled == `true`]...` | document count |
| ✅ | Cisco Meraki | Cisco Meraki: Privileged User Count | `Users[?Privileged == `Yes`].name \| length(@)` | document count |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q16 — How many service accounts maintain admin privileges?
**N/A**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Active Directory | Active Directory: Privileged Users List | `SystemInfo.PrivilegedUsersStr` | review for service accounts |
| ✅ | Microsoft 365 | Office 365: Privileged Users List | `Users[?Privileged==`Yes`] \| sort_by(@,&id)[].[displayNam...` | review for service accounts |
| ✅ | Windows Server | Windows: Local Privileged User List | `Users[?Admin && LocalAccount].Name \| sort(@)` | review for service accounts |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q17 — Do you restrict local administrative access for all users?
**CIS 5.4**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Active Directory | Active Directory: Default Administrator Account Enabled | `Users[?CN==`Administrator`].Enabled \| [0] \| replace(to_...` | false |
| ✅ | Windows Server | Windows: Local Privileged User List | `Users[?Admin && LocalAccount].Name \| sort(@)` | IT accounts only |
| ✅ | Active Directory | Active Directory: Privileged Users Count | `SystemInfo.NumPrivilegedUsers` | low, role-appropriate |
| ✅ | Windows Workstation | Windows Workstation: Guest Account Disabled | `Users[?contains(SID, '-501')].Disabled` | true |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q30 — Do you maintain formal processes for revoking access upon termination?
**CIS 6.2**

**Step 0 — Reconciled identity dormancy check (primary answer):**
```
# Cross-system synthesized activity state — accounts active in any system count as Active
liongard_identity COUNT environmentId=<ENV_ID> enabled=true accountActivity="Stale"
liongard_identity COUNT environmentId=<ENV_ID> enabled=true accountActivity="Dormant"
liongard_identity COUNT environmentId=<ENV_ID> enabled=true accountActivity="Never Used"

# Full roster for carrier review
liongard_identity LIST environmentId=<ENV_ID> enabled=true accountActivity="Stale"
  fields=["email","displayName","accountActivity","lastLogin","lastSeen","privileged","inspectors"]
liongard_identity LIST environmentId=<ENV_ID> enabled=true accountActivity="Dormant"
  fields=["email","displayName","accountActivity","lastLogin","lastSeen","privileged","inspectors"]
```
`accountActivity` is synthesized across every connected system. A user active
in one IdP but dormant in another yields a reconciled activity state reflecting
the full picture — this is more reliable than per-IdP last-login alone, which only
reflects a single system's view. Stale + enabled + privileged users are the
highest-severity termination finding.

**Step 1 — Per-inspector cross-check:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Microsoft 365 | Office 365: Stale or Disused User Accounts Count | `length(Users[?activeLast30Days==`false` && accountEnabled...` | 0 |
| ✅ | Microsoft 365 | Office 365: Stale or Disused User Accounts List | `Users[?activeLast30Days==`false` && accountEnabled == `tr...` | empty |
| ✅ | Active Directory | Active Directory: Stale User Accounts Count | `Users[?UserActivity==`Stale` && DefaultSystemUser==`false...` | 0 |
| ✅ | Active Directory | Active Directory: Disabled Users List | `Users[?UserStatus==`Disabled`].Name` | review |
| ✅ | Microsoft 365 | Office 365: Privileged Users List | `Users[?Privileged==`Yes`] \| sort_by(@,&id)[].[displayNam...` | no ex-employees |
| ✅ | Active Directory | Active Directory: Privileged Users List | `SystemInfo.PrivilegedUsersStr` | no ex-employees |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q31 — Do you disable inactive accounts after no more than 45 days?
**CIS 5.3**

**Step 0 — Reconciled dormancy check (primary answer):**
```
# Accounts Liongard has synthesized as inactive across connected systems
liongard_identity COUNT environmentId=<ENV_ID> enabled=true accountActivity="Stale"
liongard_identity COUNT environmentId=<ENV_ID> enabled=true accountActivity="Dormant"
liongard_identity COUNT environmentId=<ENV_ID> enabled=true accountActivity="Never Used"
```
If all three counts = 0: ✅ COMPLIANT. The carrier wants assurance that
inactive accounts are being disabled; a zero result across all three categories
from the reconciled cross-system view is the strongest possible evidence.

**Step 1 — Per-inspector cross-check (45-day threshold detail):**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Active Directory | Active Directory: Stale User Accounts Count | `Users[?UserActivity==`Stale` && DefaultSystemUser==`false...` | 0 |
| ✅ | Active Directory | Active Directory: Stale Users List | `Users[?UserActivity==`Stale` && DefaultSystemUser==`false...` | empty |
| ✅ | Active Directory | Active Directory: Never Used User Accounts Count | `Users[?LastLogonDate == `null` && DefaultSystemUser == `f...` | 0 |
| ✅ | Active Directory | Active Directory: Never Used User Accounts Summary | `Users[?LastLogonDate==`null` && DefaultSystemUser == `fal...` | empty |
| ✅ | Microsoft 365 | Office 365: Stale or Disused User Accounts Count | `length(Users[?activeLast30Days==`false` && accountEnabled...` | 0 |
| ✅ | Microsoft 365 | Office 365: Stale or Disused User Accounts List | `Users[?activeLast30Days==`false` && accountEnabled == `tr...` | empty |
| ✅ | Microsoft 365 | Microsoft 365: Users that have not signed in in over 30 days | `Users[?signInActivity.daysSinceLastSignIn > `30`].display...` | low / documented |
| ✅ | Microsoft 365 | Microsoft 365: Users that have not signed in in over 90 days | `Users[?signInActivity.daysSinceLastSignIn > `90`].display...` | 0 |
| ✅ | gsuite-inspector | Google G Suite Inspector: Stale User Accounts Count | `Users[?suspended == `false` && archived == `false` && Day...` | 0 |
| ✅ | OneLogin | OneLogin: Never Logged In Users Count | `Users[?last_login==`null`] \| length(@)` | 0 |
| ✅ | jumpcloud-inspector | JumpCloud: User Accounts with No Password Expiration Count | `Users[?password_never_expires == \`true\`] \| length(@)` | 0 |
| ✅ | jumpcloud-inspector | JumpCloud: Locked User Accounts Count | `Users[?status == 'LOCKED'] \| length(@)` | review — locked accounts confirm enforcement |
| ✅ | jumpcloud-inspector | JumpCloud: Locked User Accounts List | `Users[?status == 'LOCKED'].[firstname, lastname, email]` | review for ex-employee accounts |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q38 — Do you disable all default accounts on enterprise assets?
**CIS 4.7**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Active Directory | Active Directory: Default Administrator Account Enabled | `Users[?CN==`Administrator`].Enabled \| [0] \| replace(to_...` | false |
| ✅ | Active Directory | Active Directory: Default Guest Account Enabled | `DefaultGuestAccountEnabled` | false |
| ✅ | Active Directory | Active Directory: Default Guest Account Enabled Count | `GuestMembers \| length(@)` | 0 |
| ✅ | Windows Workstation | Windows Workstation: Guest Account Disabled | `Users[?contains(SID, '-501')].Disabled` | true |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q39 — Do you require automatic session timeout/locking for all enterprise assets?
**CIS 4.1**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Active Directory | Active Directory: Account Lockout Duration | `AccountPolicy.AccountLockoutDuration` | >0 min |
| ✅ | Active Directory | Active Directory: Account Lockout Threshold | `AccountPolicy.lockoutThreshold` | ≤10 attempts |
| ✅ | Active Directory | Active Directory: Account Lockout Observation Window | `AccountPolicy.AccountLockoutObservationWindow` | ≥15 min |
| ✅ | Active Directory | Active Directory: Account Policy [Power BI] | `AccountPolicy.{CanonicalName: CanonicalName, Modified: Mo...` | review full policy |
| ✅ | WatchGuard | WatchGuard: Account Lockout Disabled Count | `SystemInfo.AccountLockoutSettings[?Status != 'Enabled'] \...` | 0 |
| ✅ | WatchGuard | WatchGuard: Account Lockout Not Enabled Status List | `SystemInfo.AccountLockoutSettings[?Status == 'Enabled'].[...` | empty |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q6a–Q6f — MFA by Access Vector (Workbook sub-items)
**Source:** Travelers CYB-14306 MFA Attestation · Added to Assessment sheet as Q6a–Q6f

> These sub-items extend Q6 ("Do you use MFA for [check all that apply]?") with the six specific
> access vectors that Travelers and most modern carriers assess individually. Answer each vector
> independently — a carrier may decline or surcharge if any single vector is unprotected.

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record value → Assessment evidence column (row Q6a–Q6f); set Status in status column

---

### Q6a — MFA for Email / Web-Based Email Access (All Users)
**CIS:** N/A | **Travelers:** MFA-1

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Microsoft 365 | Azure Active Directory: Security Defaults Enabled | `SystemInfo.Overview.securityDefaults.isEnabled` | enabled |
| ✅ | Microsoft 365 | Azure AD: Conditional Access Policies List | `Policies.ConditionalAccess[?state=='enabled'].displayName` | MFA policy present for all users |
| ✅ | Microsoft 365 | Count of Users with CA enforcing Microsoft MFA | `Users[?accountEnabled&&ConditionalAccessPolicies[?isMFAEnabled]]|length(@)` | = total enabled users |
| ✅ | Duo Security | Duo Security: Users Not Enrolled in MFA Count | `length(Users[?is_enrolled=='false'])` | 0 |
| ✅ | NinjaRMM | NinjaRMM: Count of Users without MFA | `Users[?enabled=='true'&&mfaConfigured=='false']|length(@)` | 0 |

---

### Q6b — MFA for Remote Network Access (Employees, Contractors, 3rd Parties)
**CIS:** 6.4 | **Travelers:** MFA-2 | **See also:** Q3

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Windows Server | Windows Server: Is RDP Enabled? | `isRdpEnabled` | false |
| ✅ | Windows Workstation | Windows Workstation: Is RDP Enabled? | `OS.RDPEnabled` | false |
| ✅ | Azure | Azure: NSG Exposed RDP Port Count | `NetworkSecurityGroups[...] | length(@)` | 0 |
| ✅ | SonicWall | SonicWall: SSL-VPN RADIUS Auth Enabled | `SslVpn.SslVpnServer.UseRadius` | true |

---

### Q6c — MFA for Admin Access to Directory Services (AD, LDAP, etc.)
**CIS:** 6.5 | **Travelers:** MFA-3a | **See also:** Q4

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Microsoft 365 | Office 365: Admin Users with MFA Disabled Count | `subtract(length(Users[?Privileged=='Yes']),length(Users[?Privileged=='Yes'&&MFAEnabled]))` | 0 |
| ✅ | Microsoft 365 | Azure AD: Security Defaults Enabled | `SystemInfo.Overview.securityDefaults.isEnabled` | enabled |
| ✅ | Microsoft 365 | Count of Privileged Users with no CA MFA policy | `Users[?accountEnabled&&Privileged=='Yes'&&length(ConditionalAccessPolicies)=='0']|length(@)` | 0 |
| ✅ | Active Directory | AD: Default Administrator Account Enabled | `Users[?CN=='Administrator'].Enabled|[0]` | false |

---

### Q6d — MFA for Admin Access to Network Backup Environments
**CIS:** N/A | **Travelers:** MFA-3b

> ⚠️ **Partial** — Liongard confirms backup system health. Backup console MFA (Cove/Axcient/Datto portal) requires vendor portal attestation.

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Cove Data Protection | Cove: Count of Failed Backups | `Devices[?BackupStatus=='Failed']|length(@)` | 0 |
| ✅ | Axcient | Axcient: Appliance Health Status | `Appliances[].health_status` | healthy |

**Manual component:** Confirm backup vendor portal enforces MFA for all admin logins.

---

### Q6e — MFA for Admin Access to Network Infrastructure (Firewalls, Routers, Switches)
**CIS:** N/A | **Travelers:** MFA-3c

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | WatchGuard | WatchGuard: Account Lockout Disabled Count | `SystemInfo.AccountLockoutSettings[?Status!='Enabled']|length(@)` | 0 |
| ✅ | SonicWall | SonicWall: SSL-VPN RADIUS Auth Enabled | `SslVpn.SslVpnServer.UseRadius` | true |
| ✅ | Cisco Meraki | Cisco Meraki: Privileged User Count | `Users[?Privileged=='Yes'].name|length(@)` | low / role-appropriate |

---

### Q6f — MFA for Admin Access to Endpoints and Servers
**CIS:** 6.5 | **Travelers:** MFA-3d

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Windows Server | Windows: Local Privileged User List | `Users[?Admin&&LocalAccount].Name|sort(@)` | IT accounts only |
| ✅ | Active Directory | AD: Default Administrator Account Enabled | `Users[?CN=='Administrator'].Enabled|[0]` | false |
| ✅ | Windows Workstation | Windows Workstation: Guest Account Disabled | `Users[?contains(SID,'-501')].Disabled` | true |

---

---

## Asset Inventory Approach — Identity MFA & Activity State

> **Use `liongard_asset` as the primary cross-inspector view for all identity questions.**
> It synthesizes data from AD, M365, Duo, NinjaRMM, and other inspectors into one record per
> person, with evaluated `accountActivity` and `mfaStatus` already computed. This is faster and
> more comprehensive than running individual metrics per inspector.

### Fetch Pattern

```
liongard_asset LIST environmentId=<ENV_ID> assetType=Identity detail=full pageSize=200
```

Paginate until all identities are retrieved (`Pagination.totalItems / 200` pages).
Filter the returned JSON client-side using the conditions below.

---

### MFA Coverage — Q3, Q4, Q6, Q6a–Q6f

**Field:** `mfaStatus`  
**Values confirmed in live data:** `"YES"` · `"NO"` · `"PARTIAL"` · `null`  
**Field:** `mfaMethod`  
**Values:** JSON array of policy/method names, e.g. `{"Liongard Resilient Policy - Enforce MFA"}`

```
# Users with NO MFA — primary risk list
records where mfaStatus == "NO"

# Privileged users with NO MFA — critical (answers Q4, Q6c)
records where privileged == true AND mfaStatus == "NO"

# Enabled accounts with only partial MFA — risk (answers Q6a, Q6b)
records where enabled == true AND mfaStatus == "PARTIAL"

# MFA method breakdown — answers Q7 (what MFA tools are in use)
group by mfaMethod value across all records

# Total MFA coverage rate
count(mfaStatus == "YES") / count(all enabled identities)
```

**Workbook mapping:**

| Asset filter | Workbook question | Status rule |
|---|---|---|
| `privileged==true AND mfaStatus=="NO"` > 0 | Q4, Q6c | ❌ NON-COMPLIANT |
| `mfaStatus=="NO"` count > 0 | Q6a, Q6b | ❌ or ⚠️ depending on scope |
| `mfaStatus=="YES"` = all enabled users | Q6a | ✅ COMPLIANT |
| `mfaMethod` values | Q7 | Record tool names in Actual Value |

---

### Identity Activity State — Q30, Q31

**Field:** `accountActivity`  
**Source:** Evaluated by Liongard from `LastLogonDate` (AD inspector), `signInActivity.lastSignInDateTime` (M365 inspector), and activity signals across all connected inspectors. Not a raw field from any single source — it is a synthesized, cross-inspector assessment.  
**Values confirmed in live data:** `"Active"` · `"Stale"` · `"Dormant"` · `"Never Used"` · `"No Activity Found"` · `null`

**Field:** `lastLogin`  
**Source:** Raw last sign-in timestamp. AD: `LastLogonDate` attribute (metric 773/774 via AD inspector). M365: `signInActivity.daysSinceLastSignIn` (metrics 2173/2174 via M365 inspector). Use this for the specific 45-day threshold.

**Field:** `lastSeen`  
**Source:** The most recent timestamp any Liongard inspector reported this identity. If `lastSeen > 45 days` and the account is `enabled == true`, the inspector may not be running — or the identity was deleted from the source system and Liongard is showing a stale record.

> ⚠️ **Offboarding is circumstantial, not a single field.**
> There is no single `terminated = true` flag. Evidence of proper termination converges from:
> 1. `accountActivity` = "Stale" / "Dormant" / "Never Used" (Liongard-evaluated)
> 2. `lastSeen` exceeding 45 days (inspector stopped reporting the identity)
> 3. Identity absent from current AD/M365 inspector results (hard deleted from source)
> 4. Identity present in AD disabled users list (metricName=`AD: Disabled Users List`) or M365 stale users (metrics metricName=`Office 365: Stale or Disused User Accounts List`, metricName=`Office 365: Stale or Disused User Accounts Count`)
> `inventoryState == "Archive"` is an MSP workflow action — it does NOT confirm formal offboarding.

```
# Stale/inactive identity patterns
# Never logged in (highest priority — enabled with no activity):
records where accountActivity == "Never Used" AND enabled == true

# Stale accounts still enabled:
records where accountActivity in ["Stale","Dormant"] AND enabled == true

# All inactive-state accounts (full termination review — Q30):
records where accountActivity != "Active" AND accountActivity != null AND enabled == true

# Raw 45-day threshold cross-check (Q31):
records where lastLogin < (today - 45 days) AND enabled == true

# Accounts never logged in at all (cross-check with metric 775 — AD never-used):
records where lastLogin == null AND enabled == true AND accountType not in ["application","service"]

# Possible inspector data quality issue (lastSeen stale but account shows active):
records where lastSeen < (today - 45 days) AND enabled == true
```

**Workbook mapping:**

| Asset filter | Source field | Workbook question | Status rule |
|---|---|---|---|
| `accountActivity in ["Never Used","Stale","Dormant"] AND enabled==true` > 0 | AD + M365 evaluated | Q31 | ❌ NON-COMPLIANT |
| All inactive-enabled = 0 | AD + M365 evaluated | Q31 | ✅ COMPLIANT |
| `accountActivity != "Active" AND enabled==true` list | AD + M365 evaluated | Q30 | Review — confirm ex-employees in list are disabled |
| `lastLogin < today-45days AND enabled==true` | AD `LastLogonDate`, M365 `signInActivity` | Q31 | ❌ if count > 0 |

---

### Additional Identity Fields — Source References

**`membership/InternalIP`**  
**Source:** AD inspector — `memberOf` attribute per user (group membership array). Answers Q14–Q17 without needing separate metric calls.
```
# All admin group members:   membership contains "Domain Admins" OR "Administrators"
# Enterprise admins:         membership contains "Enterprise Admins"
# Schema admins:             membership contains "Schema Admins"
# Custom privileged groups:  parse membership for any group with "admin" in name
```

**`department`**  
**Source:** AD inspector `department` attribute, M365 `department` property.  
**Use:** Q9f (role-based access) — group MFA coverage and privileged access by department to demonstrate access is scoped to job function.

**`accountType`**  
**Source:** Evaluated by Liongard from account properties (AD service accounts, M365 application objects).  
**Values:** `"service"`, `"application"`, `null` (regular user)  
**Use:** Q16 — filter `privileged == true AND accountType == "service"` to enumerate service accounts with administrative rights directly.

**`relatedEmails`**  
**Source:** M365 inspector — linked UPN or alias addresses for the identity.  
**Use:** Q30 — a terminated employee's primary account may be disabled but a linked alias or secondary account may remain active. Check `relatedEmails` against the stale/disabled list.

---

### Privileged Account Inventory — Q14, Q15, Q16, Q17

**Fields:** `privileged`, `enabled`, `accountType`, `membership/InternalIP`

```
# All privileged accounts
records where privileged == true

# Privileged accounts that are enabled
records where privileged == true AND enabled == true

# Service accounts with admin rights (accountType clue)
records where privileged == true AND accountType in ["service","application"]

# Privileged accounts with no MFA (highest priority)
records where privileged == true AND enabled == true AND mfaStatus == "NO"

# Inactive privileged accounts (should not exist)
records where privileged == true AND accountActivity != "Active"
```

---

### Default / Guest Accounts — Q38

```
# Look for default accounts by username
records where username in ["administrator","admin","guest","default"]

# Enabled default accounts — non-compliant
records where username == "administrator" AND enabled == true
records where username == "guest" AND enabled == true
```

---

### Evidence Recording

When using `liongard_asset` as the evidence source, record in the evidence record Notes column:

```
Source: liongard_asset LIST assetType=Identity · environmentId=<ENV_ID> · date=<YYYY-MM-DD>
Result: <count> identities with mfaStatus=="NO" / <total> enabled identities
```

This timestamp is important — insurance carriers may require evidence to be current
(typically within 30–90 days of policy renewal).

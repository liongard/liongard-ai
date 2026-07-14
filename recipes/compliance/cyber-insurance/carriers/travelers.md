---
name: cyber-insurance-travelers
description: >
  Use this skill when filling out the Travelers Casualty CyberRisk Renewal Application
  (form CYB-14202) or the Travelers MFA Attestation (form CYB-14306). Trigger phrases:
  "fill out Travelers cyber renewal", "Travelers CyberRisk application", "MFA
  attestation for Travelers", "answer Travelers underwriting questions". Carrier-specific
  variant of the cyber-insurance-readiness master skill, mapping each Travelers question
  to the corresponding Liongard metric-name, JMESPath, and asset-inventory evidence patterns.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device, liongard_identity"
personas: [vcio-account-manager, soc, technical-alignment-manager]
output_formats: [xlsx, word, markdown]
primitives: []
composes:
  - recipe:compliance:cyber-insurance-readiness
---


```yaml
customize:
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed
```
# Cyber Insurance — Carrier: Travelers CyberRisk

> **Pairs with:** `recipes/compliance/cyber-insurance/cyber-insurance-readiness.md`. The master file
> documents workflow, customization block, asset-inventory schema, and gap-summary
> output. This carrier file maps each Travelers form question to the corresponding
> Liongard metrics + asset-inventory evidence patterns.

**Forms covered:**
- Travelers CYB-14202 Ed. 01-19 — CyberRisk Renewal Application
- Travelers CYB-14306 Ed. 05-21 — MFA Attestation

**How to run this:**

1. Pull `liongard_identity LIST` and `liongard_device LIST` (the reconciled inventory).
   This is the **primary evidence source** — it reconciles MFA, account activity,
   privileged status, AV/EDR, OS, and `inspectors[]` coverage across every connected
   inspector into one record per asset.
2. For each question below, filter the cached asset records first; then run the
   listed `liongard_metric EVALUATE` calls as **cross-checks** and to capture
   inspector-unique configuration fields the asset doesn't expose (Conditional
   Access policies, password policy values, firewall rules, NSG ports).
3. When the asset answer and the per-metric counts disagree, the asset value wins
   and the divergence is recorded as a data-quality flag in the gap summary.
4. Recorded value + status are written into the deliverable format chosen in the
   master skill's customization block.

---


## COVERAGE SUMMARY

| Category | Count |
|---|---|
| Questions answerable with Liongard metric evidence | 10 of 22 trackable controls |
| Questions with additional reconciled-inventory (`liongard_identity` / `liongard_device`) evidence | 8 (MFA, AV/EDR, stale accounts, vendor access) |
| Questions requiring manual attestation | ~12 |
| Liongard evidence mappings referenced | 50+ |

### Liongard-Answerable Questions (with metric-name and JMESPath evidence)
Q6a/6b (encryption at rest/transit), Q10b (firewall), Q10c (AV), Q10d (patching),
Q10h (admin MFA), Q10i (remote access MFA), Q10j (email MFA), Q10k (VPN-only remote),
Q10l (backup), Q10p (password policy), Q10q (user termination), MFA-1, MFA-2, MFA-3a–3d

### Additional Asset Inventory Evidence (`liongard_identity` / `liongard_device`)
The following questions can be answered or corroborated using the Asset Inventory directly,
which synthesizes data across all connected inspectors into per-identity and per-device records.
See the **Asset Inventory Evidence** section at the bottom of this file for full fetch patterns.

| Travelers Question | Asset Field(s) | What it answers |
|---|---|---|
| Q10c — AV on all devices | `antivirus`, `edr`, `inspectors` | Which devices have confirmed AV/EDR; which are not locally inspected |
| Q10h — Admin MFA | `mfaStatus`, `privileged`, `membership/InternalIP` | Privileged users with `mfaStatus == "NO"` |
| Q10i — Remote access MFA | `mfaStatus`, `enabled` | All enabled users with no MFA |
| Q10j — Email MFA | `mfaStatus`, `mfaMethod` | Email-accessible accounts without MFA; method/policy in use |
| Q10q — User termination | `accountActivity`, `lastLogin`, `lastSeen`, `enabled` | Stale/never-used accounts still enabled |
| Q17b/c — Vendor access review/revocation | `accountActivity`, `lastSeen`, `enabled` | Stale enabled accounts as revocation hygiene signal |
| MFA-1 — Email MFA (all users) | `mfaStatus`, `mfaMethod` | Full MFA coverage rate across all identities |
| MFA-3a — Admin directory MFA | `privileged`, `mfaStatus`, `membership/InternalIP` | Admin group members without MFA |

### Manual / Policy-Only Questions
Q4 (data types), Q5 (record count), Q7 (HIPAA), Q8 (GDPR), Q9a–9e, Q10a (CISO),
Q10e (IDS), Q10f (IPS), Q10g (DLP), Q10m (pen test), Q10n (network assessments),
Q11 (payment card), Q12–13 (content/IP), Q14–16 (BCP/IR/recovery time), Q17–18 (vendor)

---

## SECTION: DATA INVENTORY

### Q4 — Data Types Collected / Processed / Stored
**Form:** Does the Applicant collect credit/debit card data, medical info, SSNs, employee/HR data?  
**Coverage:** `MANUAL` — Liongard does not inventory data classifications. Requires written attestation.  
**Related metric (evidence only):** M365 user list can support HR data scope awareness.

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | Microsoft 365 | Office 365: Privileged Users List | `Users[?Privileged==\`Yes\`] \| sort_by(@,&id)[].[displayName,userPrincipalName]` | review — scope of HR data access |

---

### Q5 — Volume of Individuals' Personal Information
**Form:** How many unique individuals' personal info does the org collect/store?  
**Coverage:** `MANUAL` — requires records count attestation from data systems.

---

### Q6 — Data Encryption Status
**Form:** Is data encrypted at rest, in transit, on mobile, on employee-owned devices, with third parties?  
**Coverage:** `LIONGARD (PARTIAL)` — can confirm at-rest encryption on managed endpoints. Mobile/BYOD/third-party require manual attestation.

**Fetch protocol:**
1. Resolve system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. Evaluate: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record → evidence record evidence value + status fields

**6a — Data at rest:**

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | Windows Workstation | Windows Workstation: Bitlocker Status Summary [VI] | `Drives[].{DriveName: DriveName, BitlockerStatus: BitlockerStatus}` | all Fixed drives = "Fully Encrypted" |
| ✅ | Windows Workstation | Windows Workstation: All Drives Encrypted | `length(Drives[?Type == 'Fixed' && BitlockerStatus == 'Fully Encrypted'])` | true |
| ✅ | Windows Server | Windows Server: All Drives Encrypted | `length(Drives[?Type == 'Fixed' && BitlockerStatus == 'Fully Encrypted'])` | true |
| ✅ | macOS | macOS: File Vault Encryption Status | `Overview.FileVaultEncryption` | enabled |

**6b — Data in transit:**

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | SonicWall | SonicWall: SSL-VPN RADIUS Authentication Enabled | `SslVpn.SslVpnServer.UseRadius` | true — confirms encrypted VPN tunnel |
| ✅ | Domain/DNS | Internet Domain/DNS: DMARC Exists on Domain | `DMARCExists` | true |

**6c/6d — Mobile / Employee-Owned:** `MANUAL` — Liongard does not inspect unmanaged/personal devices.

**6e — Third-party:** `MANUAL` — requires vendor review and contractual attestation.

---

### Q7 — HIPAA Compliance
**Coverage:** `MANUAL` — regulatory compliance status requires attestation. Liongard can surface user access and data configuration as supporting evidence but cannot assert HIPAA compliance.

---

### Q8 — GDPR Applicability
**Coverage:** `MANUAL` — regulatory applicability and compliance status require attestation.

---

## SECTION: PRIVACY CONTROLS (Q9)

### Q9e — Annual Privacy & Security Training for Employees
**Form:** Does the Applicant conduct annual privacy/security training?  
**Coverage:** `MANUAL` — no Liongard metric exists for training completion. Recommend KnowBe4 or similar platform documentation.

### Q9f — Restricted Access Based on Job Function
**Form:** Is access to sensitive data/systems restricted by job function?  
**Coverage:** `LIONGARD (PARTIAL)` — Liongard can surface privileged account lists and separation of duties evidence.

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | Microsoft 365 | Office 365: Privileged Users List | `Users[?Privileged==\`Yes\`] \| sort_by(@,&id)[].[displayName,userPrincipalName]` | role-appropriate only |
| ✅ | Active Directory | Active Directory: Privileged Users List | `SystemInfo.PrivilegedUsersStr` | role-appropriate only |
| ✅ | Microsoft 365 | Office 365: Privileged Users with Overuse Count | `length(Users[?Privileged==\`Yes\` && Assigned_Products])` | 0 |

**All other Q9 sub-items (9a–9d):** `MANUAL` — policy documents, privacy officer assignment, data classification procedures.

---

## SECTION: NETWORK SECURITY CONTROLS (Q10)

### Q10a — CISO / Security Responsibility Owner
**Coverage:** `MANUAL` — requires named individual attestation.

---

### Q10b — Active Firewall Technology
**Form:** Does the Applicant have up-to-date, active firewall technology?  
**Coverage:** `LIONGARD` ✅

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | Windows Workstation | Windows Workstation: Firewall Status Summary | `Firewall` | all profiles enabled |
| ✅ | Windows Workstation | Windows Workstation: Domain Firewall Enabled | `Firewall.Domain` | true |
| ✅ | Windows Workstation | Windows Workstation: Public Firewall Enabled | `Firewall.Public` | true |
| ✅ | Windows Workstation | Windows Workstation: Private Firewall Enabled | `Firewall.Private` | true |
| ✅ | macOS | macOS: Firewall Enabled Status | `(contains(Firewall.globalState, \`Enabled\`))` | true |
| ✅ | Windows Server | Windows Server: Domain Firewall Enabled | `Network.FirewallInfo.Domain.Enabled` | true |
| ✅ | SonicWall | SonicWall: Firewall Rule Count | `[Firewall.AccessRulesIPv4, Firewall.AccessRulesIPv6][]\|length(@)` | review — rules active |
| ✅ | Fortinet FortiGate | Fortinet FortiGate: Firewall Policy Summary | `FirewallPolicy[].join(\`, \`, [...])` | reviewed |
| ✅ | Ubiquiti UniFi | Ubiquiti UniFi: Hardware type and version | (server-side JMESPath) | review — firmware current on all UniFi devices |
| ✅ | Ubiquiti UniFi | UniFi: Devices List | (server-side JMESPath) | review — network device inventory confirmed |

---

### Q10c — Anti-Virus on All Computers / Networks / Mobile
**Form:** Does the Applicant have up-to-date, active anti-virus on all computers, networks, and mobile?  
**Coverage:** `LIONGARD` ✅

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | Windows Workstation | Windows Workstation: Is Antivirus on System? | `length(AVs) > '0'` | true |
| ✅ | Windows Workstation | Windows Workstation: Antivirus on System | `AVs[].Name` | non-empty |
| ✅ | Windows Workstation | Windows Workstation: Defender - Anti Virus Enabled | `DefenderInfo.Status.AntivirusEnabled` | true |
| ✅ | Windows Server | Windows Server: Antivirus on System | `AntivirusSoftware[].Name` | non-empty |
| ✅ | macOS | macOS: Antivirus On System | `SecurityProducts[].Name` | non-empty |
| ✅ | Sophos Central | Sophos Central: Endpoints with Endpoint Protection Installed Count | `Endpoints[?assignedProducts[?code==\`endpointProtection\`]] \| length(@)` | = total endpoints |
| ✅ | Webroot | Webroot: Active Endpoint Count | `Endpoints[?Deactivated==\`false\`]\|length(@)` | = total endpoints |
| ✅ | Bitdefender GravityZone | Bitdefender GravityZone: Online Endpoints Count | `Endpoints[?details.stateName==\`online\`]\|length(@)` | = total endpoints |
| ✅ `GENERATE` | CrowdStrike EDR | CrowdStrike EDR: Total Protected Devices Count | `length(Devices)` | = total managed device count |
| ✅ `GENERATE` | CrowdStrike EDR | CrowdStrike EDR: Active Detections Count | `length(Detections)` | 0 — any open detection = active threat |
| ✅ | Huntress | Huntress: Agents Count | (server-side JMESPath) | = total managed devices |
| ✅ | Huntress | Huntress: Open Incident Reports Count | (server-side JMESPath) | 0 — open incidents = active threat |
| ✅ | ESET Licensing | ESET Licensing: License Usage Summary | (server-side JMESPath) | review — used/total seats confirms coverage |
| ✅ | SonicWall Capture Client | Sonicwall Capture Client: Count of Active Endpoints | (server-side JMESPath) | = total device count |
| ✅ | SonicWall Capture Client | Sonicwall Capture Client: Count of Infected Endpoints | (server-side JMESPath) | 0 |
| ✅ | Kaseya VSA | Kaseya VSA: Agent Count | (server-side JMESPath) | review — RMM agent coverage |

---

### Q10d — Patch Management Process (+ Automated + Critical Patches Within 30 Days)
**Form:** Does the Applicant have a process to regularly download, test, and install patches? Is it automated? Are critical patches installed within 30 days?  
**Coverage:** `LIONGARD` ✅

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | Windows Workstation | Windows Workstation: Available Updates | `AvailableUpdates[].Title` | 0 pending |
| ✅ | Windows Workstation | Windows Workstation: Mandatory Updates Not Installed | `AvailableUpdates[?IsMandatory].Title` | 0 |
| ✅ | Windows Workstation | Windows Workstation: Mandatory Updates Not Installed Count | `AvailableUpdates[?IsMandatory]\|length(@)` | 0 |
| ✅ | Windows Server | Windows Server: Available Updates [VI] | `AvailableUpdates[]` | 0 |
| ✅ | NinjaRMM | NinjaRMM: Count of Devices not updated in the last 14 days | `Devices[?DaysSinceLastUpdated_r > \`14\`]\|length(@)` | 0 |
| ✅ | NinjaRMM | NinjaRMM: Count of Devices with failed OS patches | `Devices[?DeviceHealth_r.failedOSPatchesCount > \`0\`]\|length(@)` | 0 |
| ✅ | NinjaRMM | NinjaRMM: List of Devices not updated in the last 14 days | `Devices[?DaysSinceLastUpdated_r > \`14\`].systemName` | empty |
| ✅ | ConnectWise Automate | ConnectWise Automate: Computers Not Seen In Past 30 Days | (server-side JMESPath) | 0 — stale agents = devices not receiving patches |
| ✅ | ConnectWise Automate | ConnectWise Automate: Days Since Server Last Patched | (server-side JMESPath) | ≤ 30 days |
| ✅ | N-able N-central | SolarWinds N-central: Count of Devices in a Failed State | (server-side JMESPath) | 0 |
| ✅ | N-able N-central | SolarWinds N-central: Count of Devices in a Stale State | (server-side JMESPath) | 0 |
| ✅ | Datto RMM | datto-rmm-inspector: Devices with Pending Patches Count | (server-side JMESPath) | 0 |

---

### Q10e — Intrusion Detection System (IDS)
**Coverage:** `MANUAL` — Liongard does not inspect IDS/IPS platforms natively. Provide vendor attestation (e.g., SentinelOne alerts, Meraki Security events).

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | SentinelOne | SentinelOne: Systems With Active Threats List | `Agents[?infected==\`true\`].join(\` \`,[...])` | empty — no active threats |

---

### Q10f — Intrusion Prevention System (IPS)
**Coverage:** `MANUAL` — network hardware IPS capabilities require vendor attestation.

---

### Q10g — Data Loss Prevention (DLP)
**Coverage:** `MANUAL` — no Liongard DLP inspector. Requires policy and tooling attestation.

---

### Q10h — MFA for Administrative / Privileged Access
**Form:** Does the Applicant use MFA for administrative or privileged access?  
**Coverage:** `LIONGARD` ✅

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | Microsoft 365 | Office 365: Admin Users with MFA Disabled Count | `subtract(length(Users[?Privileged==\`Yes\`]), length(Users[?Privileged==\`Yes\`&&MFAEnabled]))` | 0 |
| ✅ | Microsoft 365 | Azure Active Directory: Security Defaults Enabled Status | `SystemInfo.Overview.securityDefaults.isEnabled` | enabled |
| ✅ | Microsoft 365 | Azure Active Directory: Conditional Access Policies List | `Policies.ConditionalAccess[?state==\`enabled\`].displayName` | MFA policy present |
| ✅ | Microsoft 365 | Count of Privileged Users with no CA MFA policy | `Users[?accountEnabled && Privileged=='Yes' && length(ConditionalAccessPolicies)==\`0\`]\|length(@)` | 0 |
| ✅ | Duo Security | Duo Security: Users Not Enrolled in MFA Count | `length(Users[?is_enrolled==\`false\`])` | 0 |
| ✅ | WatchGuard | WatchGuard: Account Lockout Disabled Count | `SystemInfo.AccountLockoutSettings[?Status!='Enabled']\|length(@)` | 0 |

---

### Q10i — MFA for Remote Access to Network / Sensitive Systems
**Form:** Does the Applicant use MFA for remote access to the network and systems containing private/sensitive data?  
**Coverage:** `LIONGARD` ✅

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | Windows Server | Windows Server: Is RDP Enabled? | `isRdpEnabled` | false |
| ✅ | Windows Workstation | Windows Workstation: Is RDP Enabled? | `OS.RDPEnabled` | false |
| ✅ | Azure | Azure: Network Security Rules with Exposed RDP Port Count | `NetworkSecurityGroups[].properties.securityRules[?...]\|length(@)` | 0 |
| ✅ | Azure | Azure: Network Security Rules with Exposed RDP Port List | `NetworkSecurityGroups[].properties.securityRules[?...]` | empty |
| ✅ | SonicWall | SonicWall: SSL-VPN RADIUS Authentication Enabled | `SslVpn.SslVpnServer.UseRadius` | true |

---

### Q10j — MFA for Remote Access to Email
**Form:** Does the Applicant use MFA for remote access to email?  
**Coverage:** `LIONGARD` ✅

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | Microsoft 365 | Azure Active Directory: Security Defaults Enabled Status | `SystemInfo.Overview.securityDefaults.isEnabled` | enabled |
| ✅ | Microsoft 365 | Azure Active Directory: Conditional Access Policies List | `Policies.ConditionalAccess[?state==\`enabled\`].displayName` | MFA policy active |
| ✅ | Microsoft 365 | Legacy Per User MFA Enabled Users Count | `Users[?perUserMfaState=='Enabled']\|length(@)` | review |
| ✅ | Microsoft 365 | Legacy Per User MFA Enforced Users Count | `Users[?perUserMfaState=='Enforced']\|length(@)` | review |
| ✅ | Microsoft 365 | Count of Users with CA policy enforcing Duo MFA | `Users[?accountEnabled && ConditionalAccessPolicies[?...]]\|length(@)` | review |
| ✅ | Microsoft 365 | Count of Users with CA policy enforcing Microsoft MFA | `Users[?accountEnabled && ConditionalAccessPolicies[?isMFAEnabled]]\|length(@)` | review |
| ✅ | Duo Security | Duo Security: Users Not Enrolled in MFA Count | `length(Users[?is_enrolled==\`false\`])` | 0 |

---

### Q10k — Remote Access Limited to VPN
**Form:** Is remote access to the Applicant's network limited to VPN?  
**Coverage:** `LIONGARD` ✅ (confirms RDP disabled + VPN configured)

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | Windows Server | Windows Server: Is RDP Enabled? | `isRdpEnabled` | false |
| ✅ | Windows Workstation | Windows Workstation: Is RDP Enabled? | `OS.RDPEnabled` | false |
| ✅ | Azure | Azure: Exposed RDP Port Count | `NetworkSecurityGroups[...]\|length(@)` | 0 |
| ✅ | SonicWall | SonicWall: SSL-VPN RADIUS Authentication Enabled | `SslVpn.SslVpnServer.UseRadius` | true |
| ✅ | SonicWall | SonicWall: Interface Summary | `Interfaces[].join(...)` | VPN zone configured |

---

### Q10l — Backup & Recovery (+ Automated + Annually Tested)
**Form:** Does the Applicant have backup and recovery procedures? Are they automated and tested annually?  
**Coverage:** `LIONGARD` ✅

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | Cove Data Protection | Cove: Count of Failed Backups | `Devices[?BackupStatus==\`Failed\`]\|length(@)` | 0 |
| ✅ | Cove Data Protection | Cove: 24 Hours Since Last Completed Device Backup Count | `Devices[?Type==\`BackupManager\`&&HoursSinceLastCompleted>\`24\`]\|length(@)` | 0 |
| ✅ | Cove Data Protection | Cove: 24 Hours Since Last Completed Exchange Backup Count | `Devices[?Type==\`Office365\`&&HoursSinceExchangeLastCompleted>\`24\`]\|length(@)` | 0 |
| ✅ | Cove Data Protection | Cove: 24 Hours Since Last Completed OneDrive Backup Count | `Devices[?Type==\`Office365\`&&HoursSinceOneDriveLastCompleted>\`24\`]\|length(@)` | 0 |
| ✅ | Axcient | Axcient: Appliance Health Status | `Appliances[].health_status` | healthy |
| ✅ | Axcient | Axcient: Device Job Health Status | `Devices[].jobs[].health_status` | healthy |

---

### Q10m — Annual Penetration Testing
**Coverage:** `MANUAL` — requires signed third-party pen test report. Liongard is not a pen testing tool.

---

### Q10n — Annual Network Security Assessments
**Coverage:** `MANUAL` (Liongard *is* the network security assessment platform — the evidence workbook itself is the deliverable).

---

### Q10o — Systematic Storage and Monitoring of Network/Security Logs
**Form:** Does the Applicant systematically store and monitor network/security logs?  
**Coverage:** `LIONGARD (PARTIAL)` — can confirm AWS CloudTrail; endpoint log presence requires RMM/SIEM attestation.

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | AWS | Amazon Web Services: CloudTrails Enabled | `CloudTrailsActivated` | true — all regions |

---

### Q10p — Password Complexity Requirements
**Form:** Does the Applicant enforce password complexity requirements?  
**Coverage:** `LIONGARD` ✅

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | Active Directory | Active Directory: Account Minimum Password Length | `AccountPolicy.MinPasswordLength` | ≥14 |
| ✅ | Active Directory | Active Directory: Account Password Complexity | `AccountPolicy.PasswordComplexity` | true |
| ✅ | Microsoft 365 | Office 365: Accounts with Weak Passwords Count | `length(Users[?passwordPolicies.contains(...)])` | 0 |
| ✅ | Microsoft 365 | Office 365: Accounts with Weak Passwords List | `Users[?passwordPolicies.contains(...)].displayName` | empty |
| ✅ | AWS | Amazon Web Services: Strong Password Policy Enabled | `StrongPasswordPolicy` | true |
| ✅ | JumpCloud | JumpCloud: User Accounts with No Password Expiration Count | `Users[?password_never_expires == \`true\`] \| length(@)` | 0 |

---

### Q10q — User Access Termination Procedures
**Form:** Are there procedures to terminate user access as part of the employee exit process?  
**Coverage:** `LIONGARD` ✅

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | Microsoft 365 | Office 365: Stale or Disused User Accounts Count | `length(Users[?activeLast30Days==\`false\`&&accountEnabled==\`true\`])` | 0 |
| ✅ | Microsoft 365 | Office 365: Stale or Disused User Accounts List | `Users[?activeLast30Days==\`false\`&&accountEnabled==\`true\`].displayName` | empty |
| ✅ | Active Directory | Active Directory: Stale User Accounts Count | `Users[?UserActivity==\`Stale\`&&DefaultSystemUser==\`false\`]\|length(@)` | 0 |
| ✅ | Active Directory | Active Directory: Disabled Users List | `Users[?UserStatus==\`Disabled\`].Name` | review — recent ex-employees disabled |
| ✅ | Microsoft 365 | Microsoft 365: Users not signed in over 90 days | `Users[?signInActivity.daysSinceLastSignIn>\`90\`].displayName` | 0 |

---

## SECTION: PAYMENT CARD CONTROLS (Q11)
**Coverage:** `MANUAL` — conditional on Q4a (credit/debit card data). Requires PCI-DSS attestation and QSA documentation.

---

## SECTION: CONTENT LIABILITY (Q12–13)
**Coverage:** `MANUAL` — IP policy management and content review procedures are not inspectable by Liongard.

---

## SECTION: BUSINESS CONTINUITY / DISASTER RECOVERY / INCIDENT RESPONSE (Q14–16)

### Q14 — DR/BCP Plan & Incident Response Plan
**Coverage:** `MANUAL` — plan documents require direct attestation. Liongard backup health metrics (Q10l) provide supporting evidence for Q14a.

### Q15 — Plans Tested Regularly
**Coverage:** `MANUAL` — testing records require attestation.

### Q16 — Recovery Time Objective (RTO)
**Coverage:** `MANUAL` — RTO is determined by DR testing, not Liongard inspection. Backup health metrics provide indirect signal.

---

## SECTION: VENDOR CONTROLS (Q17–18)

### Q17c — Prompt Revocation of Vendor Access
**Coverage:** `LIONGARD (PARTIAL)` — stale/disabled account metrics serve as evidence.

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | Microsoft 365 | Office 365: Stale or Disused User Accounts List | `Users[?activeLast30Days==\`false\`&&accountEnabled==\`true\`].displayName` | empty |
| ✅ | Active Directory | Active Directory: Disabled Users List | `Users[?UserStatus==\`Disabled\`].Name` | review |
| ✅ | Active Directory | Active Directory: Stale Computer Accounts Count | `Computers[?Activity==\`Stale\`&&Enabled==\`true\`]\|length(@)` | 0 |

### Q17a/b/d/e/f — Vendor Policy / Logging / Insurance / Contracts
**Coverage:** `MANUAL` — contractual and policy items.

### Q18 — Outsourced Services Inventory
**Coverage:** `MANUAL` — requires inventory of third-party providers with named vendors. Liongard can surface cloud asset counts as supporting context.

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | AWS | Amazon Web Services: Running EC2 Instances Count | `SystemInfo.NumRunningEC2Instances` | document |
| ✅ | AWS | Amazon Web Services: S3 Buckets Count | `SystemInfo.NumS3Buckets` | document |
| ✅ | Azure | Azure: Virtual Machine Count | `VirtualMachines\|length(@)` | document |

---

## SECTION: MFA ATTESTATION (CYB-14306)

### MFA-1 — MFA Required for All Employees Accessing Email via Web / Cloud
**Coverage:** `LIONGARD` ✅

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | Microsoft 365 | Azure AD: Security Defaults Enabled | `SystemInfo.Overview.securityDefaults.isEnabled` | enabled |
| ✅ | Microsoft 365 | Azure AD: Conditional Access Policies List | `Policies.ConditionalAccess[?state==\`enabled\`].displayName` | MFA policy active |
| ✅ | Microsoft 365 | Count of Users with CA enforcing Microsoft MFA | `Users[?accountEnabled&&ConditionalAccessPolicies[?isMFAEnabled]]\|length(@)` | = total enabled users |
| ✅ | Microsoft 365 | Count of Users with CA enforcing Duo MFA | `Users[?accountEnabled&&ConditionalAccessPolicies[?contains(name,\`Duo\`)]]\|length(@)` | review |
| ✅ | Duo Security | Duo: Users Not Enrolled in MFA Count | `length(Users[?is_enrolled==\`false\`])` | 0 |
| ✅ | Duo Security | Duo: Users Not Enrolled in MFA List | `Users[?is_enrolled==\`false\`].{username: username}` | empty |
| ✅ | NinjaRMM | NinjaRMM: Count of Users without MFA | `Users[?enabled==\`true\`&&mfaConfigured==\`false\`]\|length(@)` | 0 |
| ✅ | JumpCloud | JumpCloud: User Accounts with No Password Expiration Count | `Users[?password_never_expires == \`true\`] \| length(@)` | 0 — password policy enforcement signal |

---

### MFA-2 — MFA Required for All Remote Network Access (Employees, Contractors, Third Parties)
**Coverage:** `LIONGARD` ✅

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | Windows Server | Windows Server: Is RDP Enabled? | `isRdpEnabled` | false |
| ✅ | Windows Workstation | Windows Workstation: Is RDP Enabled? | `OS.RDPEnabled` | false |
| ✅ | Azure | Azure: Exposed RDP Port Count | `NetworkSecurityGroups[...]\|length(@)` | 0 |
| ✅ | Azure | Azure: Exposed RDP Port List | `NetworkSecurityGroups[...]` | empty |
| ✅ | SonicWall | SonicWall: SSL-VPN RADIUS Authentication Enabled | `SslVpn.SslVpnServer.UseRadius` | true |

---

### MFA-3a — MFA for Admin Access to Directory Services (AD, LDAP)
**Coverage:** `LIONGARD` ✅

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | Microsoft 365 | Office 365: Admin Users with MFA Disabled Count | `subtract(length(Users[?Privileged==\`Yes\`]),length(Users[?Privileged==\`Yes\`&&MFAEnabled]))` | 0 |
| ✅ | Microsoft 365 | Azure AD: Security Defaults Enabled | `SystemInfo.Overview.securityDefaults.isEnabled` | enabled |
| ✅ | Microsoft 365 | Azure AD: Conditional Access Policies List | `Policies.ConditionalAccess[?state==\`enabled\`].displayName` | MFA policy active |
| ✅ | Microsoft 365 | Count of Privileged Users with no CA MFA policy | `Users[?accountEnabled&&Privileged=='Yes'&&length(ConditionalAccessPolicies)==\`0\`]\|length(@)` | 0 |
| ✅ | Active Directory | AD: Default Administrator Account Enabled | `Users[?CN==\`Administrator\`].Enabled\|[0]` | false |

---

### MFA-3b — MFA for Admin Access to Network Backup Environments
**Coverage:** `LIONGARD (PARTIAL)` — can confirm backup system health and job status; MFA configuration on backup consoles requires vendor portal attestation.

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | Cove Data Protection | Cove: Count of Failed Backups | `Devices[?BackupStatus==\`Failed\`]\|length(@)` | 0 |
| ✅ | Axcient | Axcient: Appliance Health Status | `Appliances[].health_status` | healthy |

---

### MFA-3c — MFA for Admin Access to Network Infrastructure (Firewalls, Routers, Switches)
**Coverage:** `LIONGARD` ✅

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | WatchGuard | WatchGuard: Account Lockout Disabled Count | `SystemInfo.AccountLockoutSettings[?Status!='Enabled']\|length(@)` | 0 |
| ✅ | SonicWall | SonicWall: SSL-VPN RADIUS Authentication Enabled | `SslVpn.SslVpnServer.UseRadius` | true |
| ✅ | Cisco Meraki | Cisco Meraki: Privileged User Count | `Users[?Privileged==\`Yes\`].name\|length(@)` | low / appropriate |
| ✅ | Fortinet FortiGate | Fortinet FortiGate: Interface Summary | `Interfaces[].join(...)` | management interface segmented |
| ✅ | Ubiquiti UniFi | UniFi: Super Admin Users List | (server-side JMESPath) | review — admin accounts on UniFi network infrastructure |

---

### MFA-3d — MFA for Admin Access to Endpoints / Servers
**Coverage:** `LIONGARD` ✅

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | Windows Server | Windows: Local Privileged User List | `Users[?Admin&&LocalAccount].Name\|sort(@)` | IT accounts only — no shared/default |
| ✅ | Active Directory | AD: Default Administrator Account Enabled | `Users[?CN==\`Administrator\`].Enabled\|[0]` | false |
| ✅ | Active Directory | Active Directory: Privileged Users Count | `SystemInfo.NumPrivilegedUsers` | low / role-appropriate |
| ✅ | Windows Workstation | Windows Workstation: Guest Account Disabled | `Users[?contains(SID,'-501')].Disabled` | true |

---

## Asset Inventory Evidence (`liongard_identity` / `liongard_device`)

For Travelers questions about MFA coverage, AV/EDR deployment, and identity hygiene, the
Asset Inventory is the fastest cross-inspector evidence source. It synthesizes data from AD,
M365, Duo, NinjaRMM, Windows Workstation, and other inspectors into a single record per
person or device — no per-inspector metric calls needed.

```
liongard_identity LIST environmentId=<ENV_ID> pageSize=200   # identity evidence
liongard_device   LIST environmentId=<ENV_ID> pageSize=200   # device evidence
```

Paginate until all records are retrieved (`Pagination.totalItems / 200` pages).

---

### Identity Asset — Travelers-Relevant Fields

| Field | Source inspector(s) | Values | Travelers question |
|---|---|---|---|
| `mfaStatus` | M365 (CA policies), Duo, NinjaRMM | `"YES"` · `"NO"` · `"PARTIAL"` | Q10h, Q10i, Q10j, MFA-1 through MFA-3d |
| `mfaMethod` | M365 CA policy names | `{"Liongard Resilient Policy - Enforce MFA"}` | Q10j — which MFA product/method is in use |
| `privileged` | AD group membership, M365 admin roles | `true` / `false` | Q10h, MFA-3a — admin account identification |
| `enabled` | AD `Enabled` attribute, M365 `accountEnabled` | `true` / `false` | Q10q, Q17c — active account scope |
| `accountActivity` | Evaluated across AD `LastLogonDate` + M365 `signInActivity` | `"Active"` · `"Stale"` · `"Dormant"` · `"Never Used"` · `"No Activity Found"` | Q10q — stale account detection; Q17b/c — vendor access hygiene |
| `lastLogin` | AD `LastLogonDate`, M365 `signInActivity.lastSignInDateTime` | ISO timestamp or `null` | Q10q — 45-day inactivity threshold |
| `lastSeen` | All inspectors — most recent report date | ISO timestamp | Q10q, Q17c — inspector data freshness; `> 45 days` = possible orphaned account |
| `membership/InternalIP` | AD `memberOf` attribute | `{Domain Admins, Administrators, ...}` | MFA-3a — exact admin group membership per user |
| `accountType` | Liongard evaluation of account properties | `"service"` · `"application"` · `null` | MFA-3d — service accounts with admin rights |
| `department` | AD `department`, M365 `department` | `"HR"` · `"IT"` · `null` | Q9f — role-based access by job function |
| `relatedEmails` | M365 — linked UPN or alias addresses | secondary email string | Q10q — linked accounts that may remain active after primary disabled |

**Key identity patterns for Travelers questions:**

```
# Q10h / MFA-3a — admin accounts without MFA (HIGHEST PRIORITY)
filter: privileged == true AND mfaStatus == "NO" AND enabled == true

# Q10i / Q10j / MFA-1 — all enabled users without MFA
filter: mfaStatus == "NO" AND enabled == true

# MFA method/product inventory (answers Q10j and MFA-1 attestation)
group by: mfaMethod across all enabled identities

# Q10q — stale accounts still enabled (Travelers asks about termination procedures)
filter: accountActivity in ["Stale","Dormant","Never Used","No Activity Found"] AND enabled == true

# Q10q — accounts never logged in, still active
filter: lastLogin == null AND enabled == true AND accountType not in ["application","service"]

# MFA-3a — admin group members, enumerate for directory services MFA attestation
filter: privileged == true — then parse membership/InternalIP for specific admin group names

# MFA-3d — service accounts with admin rights
filter: privileged == true AND accountType == "service"

# Q17b/c — vendor access hygiene (stale enabled accounts as revocation signal)
filter: accountActivity != "Active" AND enabled == true AND lastSeen < (today - 45 days)
```

> ⚠️ **Offboarding is not a single field.** The `inventoryState: "Archive"` value is an MSP
> workflow action in Liongard — it does not confirm formal identity termination. Real termination
> evidence requires converging signals: `accountActivity` evaluated as stale, `lastSeen` exceeding
> 45 days, identity absent from current AD/M365 inspector results (hard deleted), or present in
> the AD disabled users list (metricName=`AD: Disabled Users List`) or M365 stale accounts list (metrics metricName=`Office 365: Stale or Disused User Accounts List`, metricName=`Office 365: Stale or Disused User Accounts Count`).

---

### Device Asset — Travelers-Relevant Fields

| Field | Source inspector(s) | Values | Travelers question |
|---|---|---|---|
| `antivirus` | `windows-workstation-inspector` (`AVs[].Name`), `windows-server-inspector` (`AntivirusSoftware[].Name`), `mac-inspector` (`SecurityProducts[].Name`) | Set string e.g. `"{CylancePROTECT,Windows Defender}"` or `null` | Q10c — AV on all computers/networks |
| `edr` | `windows-workstation-inspector`, `windows-server-inspector` — security product detection | Set string e.g. `"{CylancePROTECT}"` or `null` | Q10c — EDR presence |
| `inspectors` | Liongard — all inspectors reporting this device | JSON array | Q10c — coverage gap: AD-only device has no local inspection → `antivirus`/`edr` null |
| `operatingSystem` | `windows-workstation-inspector`, `windows-server-inspector`, `mac-inspector` | `"Microsoft Windows 10 Pro"` · `"Windows Server 2019"` | Q10d — OS family for patching context |
| `oSVersion` | `windows-workstation-inspector`, `windows-server-inspector` | `"10.0.19045"` · `"6.1 (7601)"` | Q10d — exact build; EOL determination |
| `winElevenReady` | `windows-workstation-inspector` (WMI hardware compatibility check) | `"Compatible"` · `"Incompatible"` · `"Unknown"` | Q10d — Windows 10 EOL (Oct 2025); `"Incompatible"` = hardware must be replaced |
| `warrantyExpiration` | `windows-workstation-inspector` (SMBIOS), RMM inspectors | ISO timestamp or `null` | Hardware lifecycle tracking signal |
| `physical` | `windows-workstation-inspector`, `windows-server-inspector` | `true` = physical · `false` = VM | Q18 — physical vs. hosted/cloud device split |
| `accountType` | Liongard evaluation | `"workstation"` · `"laptop"` · `"server"` | Q10c — AV/EDR coverage broken out by device class |
| `lastSeen` | All inspectors — most recent report date | ISO timestamp | Data quality — `> 45 days` = stale inspection; AV/EDR data may not be current |
| `location` | RMM inspectors (NinjaRMM, ConnectWise) | e.g. `"No Patch or AV"` · `null` | Q10c — RMM-sourced security posture tag is direct coverage gap evidence |

**Key device patterns for Travelers questions:**

```
# Q10c — AV/EDR coverage assessment
# Locally inspected, no EDR:
filter: edr == null AND inspectors contains "windows-workstation-inspector"

# Locally inspected, no AV:
filter: antivirus == null AND inspectors contains "windows-workstation-inspector"

# AD-only (not locally inspected — antivirus/edr will be null, status unknown):
filter: inspectors contains ONLY "active-directory-inspector"

# AV/EDR product inventory (answers Q10c — "what antimalware software is being used?"):
collect unique values of antivirus and edr across all compute devices

# Q10d / Windows 10 EOL risk (Oct 2025):
filter: operatingSystem contains "Windows 10" AND winElevenReady == "Incompatible"
→ these devices cannot be upgraded; require hardware replacement before EOL

# Coverage by device type (workstations vs. servers):
group by: accountType — report AV/EDR coverage rate per class
```

---

### Evidence Recording for evidence record

When using the reconciled inventory (`liongard_identity` / `liongard_device`) as an evidence source, record in the evidence record Notes column (column L):

```
Source: liongard_identity|liongard_device LIST · environmentId=<ENV_ID> · date=<YYYY-MM-DD>
Result: <finding, e.g. "3 of 47 enabled identities have mfaStatus==NO">
```

Include the assessment date — Travelers and most carriers require evidence to be current
(typically within 30–90 days of the policy effective date).

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | Travelers questionnaire answers draw directly from the onboarding inventory. Hardware, identity, backup, and network data from onboarding feeds the MFA Attestation (CYB-14306) and Network Security Controls (Q10) sections — the highest-weighted questions for Travelers underwriting. |
| CIS Controls (v8.1) | ✅ | Travelers questions map to: CIS 5–6 (Q3 MFA / auth controls), CIS 10–11 (Q4 backup coverage + immutability), CIS 1–4/7 (Q10 endpoint patching + EDR), CIS 12–14 (Q10 network / firewall controls), CIS 17–18 (Q15–16 incident response + BCP), CIS 15 (Q17–18 vendor controls + third-party access). |
| Cyber-insurance domain files | ✅ | Travelers sections map directly to Liongard domain files: `domains/auth.md` (MFA Q3 + CYB-14306), `domains/backup.md` (Q4 + Q14–16 DR), `domains/endpoint.md` (Q10 EDR + patching), `domains/network.md` (Q10 network controls), `domains/governance.md` (Q2 policies + documentation), `domains/regulatory.md` (Q9 privacy + PCI), `domains/vendor.md` (Q17–18 third-party vendor access). |
| QBR / quarterly-business-review | ✅ | Travelers renewal date drives QBR cadence. QBR Step 7 surfaces the Travelers evidence pack generated by this recipe; the QBR run closest to renewal is the canonical runtime for populating the carrier application. |

---

## INTERPRETATION KEY

| Status | Meaning |
|---|---|
| ✅ LIONGARD CONFIRMED | Metric returns value matching "Compliant When" |
| ⚠️ PARTIAL | Most compliant; exceptions exist — document in Notes |
| ❌ NON-COMPLIANT | Metric shows risk; flag for remediation |
| ℹ️ MANUAL | No Liongard metric — requires written attestation |
| 🔍 REVIEW | Null return — system may not be inspected; verify coverage |

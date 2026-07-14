---
name: cyber-insurance-network
description: >
  Domain reference for the cyber-insurance-readiness master skill. Covers Network & Cloud Infrastructure
  (Q19–Q21, Q35–Q36, Q41–Q43). Used as a sub-reference when answering cyber insurance underwriting
  questions in this control area.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device, liongard_identity"
personas: [vcio-account-manager, soc, technical-alignment-manager]
primitives:
  - metrics:sonicwall:any-to-any-allow-rules-count
  - metrics:sonicwall:geo-ip-block-all-enabled
  - metrics:sonicwall:wan-allow-rules-for-management-count
  - metrics:sonicwall:wan-to-lan-explicit-allow-any-list
  - metrics:sonicwall:zones-without-ips-count
  - metrics:sonicwall:zones-without-ips-list
---


```yaml
customize:
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed
```
# Cyber Insurance — Domain: Network & Cloud Infrastructure

> **Pairs with:** `recipes/compliance/cyber-insurance/cyber-insurance-readiness.md`. The master file
> documents the workflow, customization block, asset-inventory schema, and gap-summary
> output. This domain file documents the metric names and JMESPath queries for each
> question in this control area.

> **Asset Inventory First.** Before evaluating the per-metric tables below, the
> agent should pull the reconciled inventory — `liongard_identity` (identity) or
> `liongard_device` (device), using server-side filters or `COUNT` when only a
> coverage figure is needed — and answer the question from the asset record's
> cross-inspector synthesis (`mfaStatus`, `accountActivity`, `privileged`,
> `antivirus`, `edr`, `inspectors[]`, etc.). Per-inspector metrics in this file
> are the **cross-check** — they confirm the asset answer and provide
> inspector-unique fields the asset doesn't expose (e.g., AD password policy,
> Conditional Access policy names, firewall rule counts). When asset and metric
> disagree, the asset value wins and the divergence is recorded as a data-quality
> flag in the gap summary.


**Inspectors referenced:** SonicWall, Cisco Meraki, Fortinet, AWS, Azure, Cisco Umbrella, WatchGuard

**Question coverage:** Q19–Q21, Q35–Q36, Q41–Q43

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

## Q19 — Do you maintain cloud-based assets?
**N/A**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | AWS | Amazon Web Services: Running EC2 Instances Count | `SystemInfo.NumRunningEC2Instances` | document count |
| ✅ | AWS | Amazon Web Services: S3 Buckets Count | `SystemInfo.NumS3Buckets` | document count |
| ✅ | azure-inspector | Azure: Virtual Machine Count | `VirtualMachines \| length(@)` | document count |
| ✅ | gsuite-inspector | Google G Suite: Active Users Count | `length(Users[?archived == `false` && suspended == `false`...` | document count |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q20 — Are cloud assets protected with credentials separate from AD?
**N/A**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | AWS | Amazon Web Services: Root Account MFA Enabled | `SystemInfo.RootAccountMFAEnabled` | true |
| ✅ | AWS | Amazon Web Services: Root Access Keys | `RootAccessKeys` | 0 / none |
| ✅ | AWS | Amazon Web Services: Users without MFA Enabled List | `Users[?MFAEnabled==`false`].UserName \| join(`, `, @)` | empty |
| ✅ | AWS | Amazon Web Services: IAM Users Count | `SystemInfo.NumIAMUsers` | document |
| ✅ | AWS | Amazon Web Services: IAM Enabled | `IAMUsed` | true |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q21 — Do you maintain controls to prevent unauthorized assets?
**CIS 1.2**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Microsoft 365 | Azure Active Directory: Total Devices Not Enrolled Count | `Devices[?intuneRegistered_r==`false`] \| length(@)` | 0 |
| ✅ | Microsoft 365 | Azure Active Directory: Non-Compliant Device Count | `Devices[?isCompliant == `false` && accountEnabled == `tru...` | 0 |
| ✅ | Active Directory | Active Directory: Stale Computer Accounts Count | `Computers[?Activity==`Stale` && Enabled ==`true`] \| leng...` | 0 |
| ✅ | Active Directory | Active Directory: Stale Computer Accounts List | `Computers[?Enabled == `true` && Activity ==`Stale`].Name` | empty |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q35 — Do you maintain regularly updated secure configuration processes?
**CIS 4.1**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Windows Server | Windows Server: System Information Summary [VI] | `{MachineID: MachineID, BootDevice: SystemInfo.BootDevice,...` | documented |
| ✅ | Fortinet FortiGate | Fortinet FortiGate: Firewall Policy Summary | `FirewallPolicy[].join( `, `, [join(`: `, [`Name`, to_stri...` | reviewed |
| ✅ | SonicWall | SonicWall: Firewall Rule Count | `[Firewall. AccessRulesIPv4, Firewall. AccessRulesIPv6][] ...` | appropriate/minimal |
| ✅ | Cisco Meraki | Cisco Meraki: Device Firmware Summary | `Networks[].Devices[]. join( `, `, [join(`: `, [`Device Na...` | current firmware |
| ✅ | ubiquiti-unifi-inspector | Ubiquiti UniFi: Hardware type and version | (server-side JMESPath) | review — firmware version confirms current, supported firmware |
| ✅ | ubiquiti-unifi-inspector | UniFi: Devices List | (server-side JMESPath) | review — network device inventory baseline |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q36 — Do you use secure network protocols to manage enterprise assets?
**CIS 4.6**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | SonicWall | SonicWall: Interface Summary | `Interfaces[].join( `, `, [join(`: `, [`Name`, to_string(n...` | zones configured |
| ✅ | SonicWall | SonicWall: NAT Policy Count | `[Firewall.NatPolicies.Ipv4, Firewall.NatPolicies.Ipv6][] ...` | minimal/appropriate |
| ✅ | Windows Server | Windows Server: Is RDP Enabled? | `to_array(`[{"isRdpEnabled": true, "translatedAnswer": "Tr...` | false |
| ✅ | Cisco Meraki | Cisco Meraki: Network Device Summary | `Networks[].Devices[].join( `, `, [join(`: `, [`Network`, ...` | management VLAN only |
| ✅ | Fortinet FortiGate | Fortinet FortiGate: Interface Summary | `Interfaces[].join( `, `, [join(`: `, [`Name`, to_string(n...` | segmented |
| ✅ | ubiquiti-unifi-inspector | UniFi: Super Admin Users List | (server-side JMESPath) | review — admin accounts on network hardware; MFA-3c evidence |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q41 — Do you use DNS filtering to block malicious domains?
**CIS 9.2**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Windows Workstation | Windows Workstation: DNS Filters Installed | `Software[?contains(Name, `Zscaler`)\|\| contains(Name, `C...` | agent present |
| ✅ | Windows Server | Windows Server: DNS Filters Installed | `Software[?contains(Name, `Zscaler`)\|\| contains(Name, `C...` | agent present |
| ✅ | Webroot | Webroot: DNS Policies Summary | `DNSPPolicies` | active policy |
| ✅ | Domain/DNS | Internet Domain/DNS: DMARC Exists on Domain | `DMARCExists` | true |
| ✅ | Cisco Umbrella | Cisco Umbrella: List of Devices | `roamingComputers[?lastSyncStatus != `Uninstalled`].name` | all devices covered |
| ✅ | Cisco Umbrella | Cisco Umbrella: Unverified Networks List | `networks[?isVerified != `true`].name \| join(`, `, @)` | empty |
| ✅ | Cisco Umbrella | Cisco Umbrella: Active Users Without MFA Count | `users[?twoFactorEnable != `true` && status == `Active`] \...` | 0 |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q42 — Do you maintain a policy defining which audit logs are maintained?
**CIS 8.1**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | AWS | Amazon Web Services: CloudTrails Enabled | `CloudTrailsActivated` | true — all regions |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q43 — Do you maintain a vulnerability management process?
**CIS 7.1**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Acronis Cyber Cloud | Acronis Cyber Cloud: Count of Machines with Vulnerability Assessment Enabled | `Resources[?type == `resource.machine` && policies[?type =...` | = total devices |
| ✅ | Acronis Cyber Cloud | Acronis Cyber Cloud: List of Machines with Vulnerability Assessment Enabled | `Resources[?type == `resource.machine` && policies[?type =...` | full coverage |
| ✅ | NinjaRMM | NinjaRMM: Count of Devices in Unhealthy State | `Devices[?DeviceHealth_r.healthStatus == `UNHEALTHY`] \| l...` | 0 |
| ✅ | NinjaRMM | NinjaRMM: List of Devices in Unhealthy State | `Devices[?DeviceHealth_r.healthStatus == `UNHEALTHY`].syst...` | empty |
| ✅ | AWS | Amazon Web Services: EC2 Instances with Status Alerts Count | `InstanceStatuses[?Events] \| length(@)` | 0 |
| ✅ | SentinelOne | SentinelOne: Systems With Active Threats List | `Agents[?infected==`true`].join(` `,[`Site Name: `, siteNa...` | empty |
| ❌ `NOT_FOUND` | unknown | Datto RMM: Devices with Pending Patches Count | `NOT_FOUND` | 0 |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

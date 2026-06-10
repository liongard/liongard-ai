---
name: cyber-insurance-endpoint
description: >
  Domain reference for the cyber-insurance-readiness master skill. Covers Endpoint Protection, Patching & Encryption
  (Q1, Q8–Q12, Q10-sub, Q27, Q32–Q34, Q37, Q40). Used as a sub-reference when answering cyber insurance underwriting
  questions in this control area.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_asset"
personas: [vcio-account-manager, soc, technical-alignment-manager]
primitives:
  - metrics:cisco-meraki:days-until-license-expiry
  - metrics:cisco-meraki:open-ssid-count
  - metrics:cisco-meraki:open-ssid-list
  - metrics:cisco-meraki:weak-encryption-ssid-count
  - metrics:crowdstrike:reduced-functionality-mode-count
  - metrics:crowdstrike:stale-hosts-count-30d
  - metrics:huntress:active-incidents-count
  - metrics:huntress:unresponsive-agents-count-30d
  - metrics:huntress:unresponsive-agents-list-30d
  - metrics:sentinelone:agents-infected
  - metrics:sentinelone:agents-out-of-date-count
  - metrics:sentinelone:days-until-license-expiry
  - metrics:sentinelone:infected-agents-list
  - metrics:sentinelone:threats-malicious-unresolved
  - metrics:sentinelone:threats-unresolved
  - metrics:sonicwall:capture-atp-enabled
  - metrics:sonicwall:zones-without-gav-count
  - metrics:sophos-central:device-encryption-installed-count
  - metrics:sophos-central:device-encryption-not-installed-count
  - metrics:sophos-central:endpoint-protection-installed-count
  - metrics:sophos-central:endpoint-protection-not-installed-count
  - metrics:sophos-central:intercept-x-installed-count
  - metrics:sophos-central:intercept-x-not-installed-count
  - metrics:sophos-central:service-health-not-good-count
  - metrics:sophos-central:tamper-protection-disabled-count
  - metrics:sophos-central:tamper-protection-disabled-list
  - metrics:sophos-central:threat-health-not-good-count
  - metrics:sophos-central:threat-health-not-good-list
  - metrics:windows-server:all-drives-encrypted
  - metrics:windows-server:all-drives-encrypted-protected
  - metrics:windows-server:antivirus-list
  - metrics:windows-server:critical-updates-count
  - metrics:windows-server:days-since-last-reboot
  - metrics:windows-server:domain-firewall-enabled
  - metrics:windows-server:edr-list
  - metrics:windows-server:mandatory-updates-count
  - metrics:windows-server:public-firewall-enabled
  - metrics:windows-server:rdp-config
  - metrics:windows-workstation:all-drives-encrypted
  - metrics:windows-workstation:all-drives-encrypted-protected
  - metrics:windows-workstation:av-list
  - metrics:windows-workstation:defender-av-enabled
  - metrics:windows-workstation:defender-realtime-enabled
  - metrics:windows-workstation:defender-threat-count
  - metrics:windows-workstation:domain-firewall-enabled
  - metrics:windows-workstation:edr-list
  - metrics:windows-workstation:mandatory-updates-count
  - metrics:windows-workstation:public-firewall-enabled
  - metrics:windows-workstation:rdp-enabled
---


```yaml
customize:
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed
```
# Cyber Insurance — Domain: Endpoint Protection, Patching & Encryption

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


**Inspectors referenced:** Windows Workstation, Windows Server, macOS, Linux, AV/EDR (Sophos, SentinelOne, Webroot, Huntress, CrowdStrike, Bitdefender, ESET, SonicWall Capture Client), RMM (NinjaRMM, ConnectWise Automate, Datto RMM, Kaseya VSA, N-central)

**Question coverage:** Q1, Q8–Q12, Q10-sub, Q27, Q32–Q34, Q37, Q40

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

## Q1 — Do you use any end-of-life or unsupported software?
**CIS 2.2**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Active Directory | Active Directory: End of Life Workstations (Excludes Roar Group) | `Computers[?Type == `Workstation` && Activity != `Stale` &...` | 0 |
| ✅ | Active Directory | Active Directory: Workstations at or near End of OS Support Summary | `Computers[?Type==`Workstation` && Activity!=`Stale` && En...` | empty |
| ✅ | Windows Workstation | Windows Workstation: List of Installed Software [VI] | `Software[].{Name:Name,DisplayName:DisplayName,DisplayVers...` | review for EOL apps |
| ✅ | Windows Workstation | Windows Workstation: Available Updates | `AvailableUpdates[].Title` | 0 pending |
| ✅ | Windows Server | Windows Server: List of Installed Software [VI] | `Software[].{Name:Name,DisplayName:DisplayName,DisplayVers...` | review for EOL apps |
| ✅ | macOS | macOS: List of Applications | `Applications[].[Name, `,Version:` Version]` | review for EOL apps |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q8 — Do you maintain patching processes at least monthly?
**N/A**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ❌ `NOT_FOUND` | unknown | macOS: Available Updates Count [NEW - Proposed] | `NOT_FOUND` | 0 |
| ✅ | NinjaRMM | NinjaRMM: Count of Devices not updated in the last 14 days | `Devices[?DaysSinceLastUpdated_r > `14`] \| length(@)` | 0 |
| ✅ | NinjaRMM | NinjaRMM: Count of Devices with failed OS patches | `Devices[?DeviceHealth_r.failedOSPatchesCount > `0` && sys...` | 0 |
| ✅ | connectwise-automate-inspector | ConnectWise Automate: Computers Not Seen In Past 30 Days | (server-side JMESPath) | 0 — stale agents = devices not receiving patches |
| ✅ | connectwise-automate-inspector | ConnectWise Automate: Days Since Server Last Patched | (server-side JMESPath) | ≤ 30 days |
| ✅ | n-able-ncentral-inspector | SolarWinds N-central: Count of Devices in a Failed State | (server-side JMESPath) | 0 |
| ✅ | n-able-ncentral-inspector | SolarWinds N-central: Count of Devices in a Stale State | (server-side JMESPath) | 0 |
| ✅ | datto-rmm-inspector | datto-rmm-inspector: Devices with Pending Patches Count | Devices with Approved Patches Pending Installation | 0 |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q9 — What is your documented patch cadence?
**CIS 7.2**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Windows Workstation | Windows Workstation: Available Updates | `AvailableUpdates[].Title` | 0 |
| ✅ | Windows Workstation | Windows Workstation: Available Updates List [Power BI] | `{Hostname: NetConfig[0].DNSHostName,AvailableUpdate: Avai...` | empty |
| ✅ | NinjaRMM | NinjaRMM: List of Devices not updated in the last 14 days | `Devices[?DaysSinceLastUpdated_r > `14`].systemName` | empty |
| ✅ | NinjaRMM | NinjaRMM: Count of Devices not updated in the last 14 days | `Devices[?DaysSinceLastUpdated_r > `14`] \| length(@)` | 0 |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q10 — Do you ensure critical patches can be installed outside regular processes?
**N/A**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Windows Workstation | Windows Workstation: Mandatory Updates Not Installed | `AvailableUpdates[?IsMandatory].Title` | 0 |
| ✅ | Windows Workstation | Windows Workstation: Mandatory Updates Not Installed Count | `AvailableUpdates[?IsMandatory] \| length(@)` | 0 |
| ✅ | Windows Workstation | Windows Workstation: Available Updates | `AvailableUpdates[].Title` | 0 |
| ✅ | Windows Server | Windows Server: Available Updates [VI] | ` AvailableUpdates[]` | 0 |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q10-sub — Are critical patches installed within 30 days of release?
**CIS 7.4** | **Source:** Travelers Q10d follow-on · Workbook sub-item

> This sub-item directly answers the Travelers underwriting question "If yes [to patch process],
> are critical patches installed within 30 days of release?" Use the mandatory/failed-patch
> metrics as primary evidence. A count of 0 across all metrics = strong confirmation.

**Fetch protocol:** Same as Q10 above — use the same system resolution.

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Windows Workstation | Windows Workstation: Mandatory Updates Not Installed | `AvailableUpdates[?IsMandatory].Title` | empty — all mandatory updates applied |
| ✅ | Windows Workstation | Windows Workstation: Mandatory Updates Not Installed Count | `AvailableUpdates[?IsMandatory]\|length(@)` | 0 |
| ✅ | Windows Server | Windows Server: Available Updates [VI] | `AvailableUpdates[]` | empty |
| ✅ | NinjaRMM | NinjaRMM: Count of Devices with failed OS patches | `Devices[?DeviceHealth_r.failedOSPatchesCount>\`0\`]\|length(@)` | 0 |

**Note:** Liongard confirms *current pending patch state*, not patch *age*. If mandatory updates
are pending, cross-reference the update release date to determine if the 30-day SLA has been
breached. Record the oldest pending update date in the Notes column.

---

## Q11 — Do you have antimalware deployed on all enterprise assets?
**CIS 10.1**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Windows Workstation | Windows Workstation: Antivirus on System | `AVs[].Name` | true |
| ✅ | Windows Workstation | Windows Workstation: Defender - Anti Virus Enabled | `DefenderInfo.Status.AntivirusEnabled` | true |
| ✅ | Windows Workstation | Windows Workstation: Is Antivirus on System? | `length(AVs) > '0'` | yes |
| ✅ | Windows Server | Windows Server: Antivirus on System | `AntivirusSoftware[].Name` | true |
| ✅ | macOS | macOS: Antivirus On System | `SecurityProducts[].Name` | true |
| ✅ | Sophos Central | Sophos Central: Endpoints with Endpoint Protection Installed Count | `Endpoints[?assignedProducts[?code == `endpointProtection`...` | = total endpoints |
| ✅ | Webroot | Webroot: Active Endpoint Count | `Endpoints[?Deactivated == `false`]\| length(@)` | = total endpoints |
| ✅ `GENERATE` | crowdstrike-inspector | CrowdStrike EDR: Total Protected Devices Count | `length(Devices)` | = total managed device count |
| ✅ `GENERATE` | crowdstrike-inspector | CrowdStrike EDR: Active Detections Count | `length(Detections)` | 0 — any open detection = active threat |
| ✅ | huntress-inspector | Huntress: Agents Count | (server-side JMESPath) | = total managed devices |
| ✅ | huntress-inspector | Huntress: Open Incident Reports Count | (server-side JMESPath) | 0 — open incidents = active threat |
| ✅ | eset-inspector | ESET Licensing: License Usage Summary | (server-side JMESPath) | review — used/total seat count confirms coverage |
| ✅ | sonicwall-capture-client-inspector | Sonicwall Capture Client: Count of Active Endpoints | (server-side JMESPath) | = total device count |
| ✅ | sonicwall-capture-client-inspector | Sonicwall Capture Client: Count of Infected Endpoints | (server-side JMESPath) | 0 |
| ✅ | kaseya-vsa-inspector | Kaseya VSA: Agent Count | (server-side JMESPath) | review — confirms RMM agent coverage across managed devices |
| ✅ | kaseya-vsa-inspector | Kaseya VSA: Desktop/Laptop Count | (server-side JMESPath) | document count — total managed workstations/laptops |

| ✅ | Bitdefender GravityZone | Bitdefender GravityZone: Online Endpoints Count | `Endpoints[?details.stateName==`online`] \| length(@)` | = total endpoints |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q12 — What antimalware software is being used?
**CIS 10.1**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Windows Workstation | Windows Workstation: Antivirus on System | `AVs[].Name` | review — product name |
| ✅ | Windows Server | Windows Server: Antivirus on System | `AntivirusSoftware[].Name` | review — product name |
| ✅ | macOS | macOS: Antivirus On System | `SecurityProducts[].Name` | review — product name |
| ✅ | macOS | macOS: Endpoint Detection on System | `EDR[].Name` | review — product name |
| ✅ | Sophos Central | Sophos Central: Endpoints with Endpoint Protection Installed Count | `Endpoints[?assignedProducts[?code == `endpointProtection`...` | review |
| ✅ | SentinelOne | SentinelOne: Global Policy Summary | `GlobalPolicy` | review |
| ✅ | Webroot | Webroot: SiteInfo Summary | `SiteInfo` | review |
| ✅ `GENERATE` | crowdstrike-inspector | CrowdStrike EDR: Protected Hosts with Policy | `Hosts[].[hostname, prevention_policy_name, prevention_policy_status]` | review — policy = 'ENABLED' on all hosts |
| ✅ | huntress-inspector | Huntress: Agents List | (server-side JMESPath) | review — confirms agent deployment and host coverage |
| ✅ | eset-inspector | ESET Licensing: License Usage Summary | (server-side JMESPath) | review — product name and seat count |
| ✅ | sonicwall-capture-client-inspector | Sonicwall Capture Client: Total Endpoints | (server-side JMESPath) | review — confirms product and endpoint list |

| ✅ | Bitdefender GravityZone | Bitdefender GravityZone: Online Endpoints Count | `Endpoints[?details.stateName==`online`] \| length(@)` | review |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q27 — Describe your use of encryption for sensitive data.
**N/A**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ❌ `NOT_FOUND` | unknown | Windows Workstation: BitLocker Status | `NOT_FOUND` | enabled |
| ✅ | Windows Workstation | Windows Workstation: All Drives Encrypted | `length(Drives[?Type == 'Fixed' && BitlockerStatus == 'Ful...` | true |
| ✅ | Windows Workstation | Windows Workstation: Bitlocker Status Summary [VI] | `Drives[].{DriveName: DriveName, BitlockerStatus: Bitlocke...` | all encrypted |
| ❌ `NOT_FOUND` | unknown | Windows Server: BitLocker Status | `NOT_FOUND` | enabled |
| ✅ | Windows Server | Windows Server: All Drives Encrypted | `length(Drives[?Type == 'Fixed' && BitlockerStatus == 'Ful...` | true |
| ✅ | macOS | macOS: File Vault Encryption Status | `Overview.FileVaultEncryption` | enabled |
| ❌ `NOT_FOUND` | unknown | Amazon Web Services: Unencrypted EBS Volumes Count [NEW - Proposed] | `NOT_FOUND` | 0 |
| ❌ `NOT_FOUND` | unknown | Amazon Web Services: Unencrypted EBS Volumes List [NEW - Proposed] | `NOT_FOUND` | empty |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q32 — Do you maintain software older than one release from current?
**CIS 2.2**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Windows Workstation | Windows Workstation: List of Installed Software [VI] | `Software[].{Name:Name,DisplayName:DisplayName,DisplayVers...` | review versions |
| ✅ | Windows Server | Windows Server: List of Installed Software [VI] | `Software[].{Name:Name,DisplayName:DisplayName,DisplayVers...` | review versions |
| ✅ | macOS | macOS: List of Applications | `Applications[].[Name, `,Version:` Version]` | review versions |
| ✅ | Windows Workstation | Windows Workstation: Installed Software Count | `Software[] \| length(@)` | document |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q33 — Do you ensure only authorized software is installed?
**CIS 2.5**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Windows Workstation | Windows Workstation: List of Installed Software [VI] | `Software[].{Name:Name,DisplayName:DisplayName,DisplayVers...` | matches baseline |
| ✅ | Windows Workstation | Windows Workstation: Available Updates List [Power BI] | `{Hostname: NetConfig[0].DNSHostName,AvailableUpdate: Avai...` | empty |
| ✅ | macOS | macOS: List of Applications | `Applications[].[Name, `,Version:` Version]` | matches baseline |
| ✅ | macOS | macOS: List of Available Updates | `AvailableUpdates[].Title` | empty |
| ✅ | Linux | Linux: Software Version | `SystemInfo.VERSION` | current |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q34 — Do you scan for/alert on unauthorized software?
**N/A**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Windows Workstation | Windows Workstation: List of Installed Software [VI] | `Software[].{Name:Name,DisplayName:DisplayName,DisplayVers...` | audited |
| ✅ | Windows Workstation | Windows Workstation: Installed Software Count | `Software[] \| length(@)` | consistent over time |
| ✅ | Windows Server | Windows Server: List of Installed Software [VI] | `Software[].{Name:Name,DisplayName:DisplayName,DisplayVers...` | audited |
| ✅ | macOS | macOS: List of Applications | `Applications[].[Name, `,Version:` Version]` | audited |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q37 — Do you maintain a hardware or software firewall in front of all [assets]?
**N/A**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Windows Workstation | Windows Workstation: Domain Firewall Enabled | `Firewall.Domain` | true |
| ✅ | Windows Workstation | Windows Workstation: Firewall Status Summary | `Firewall` | all profiles on |
| ✅ | Windows Workstation | Windows Workstation: Private Firewall Enabled | `Firewall.Private` | true |
| ✅ | Windows Workstation | Windows Workstation: Public Firewall Enabled | `Firewall.Public` | true |
| ✅ | macOS | macOS: Firewall Enabled Status | `(contains(Firewall.globalState, `Enabled`))` | true |
| ✅ | Windows Server | Windows Server: Domain Firewall Enabled | `Network.FirewallInfo.Domain.Enabled` | true |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q40 — Do you disable autorun and autoplay for all removable media?
**CIS 10.3**

> ℹ️ **No Liongard metric available.** This question requires manual attestation.
> See the Manual Attestation sheet in the evidence record for guidance.

---

---

## Asset Inventory Approach — Device EDR & AV Coverage

> **Use `liongard_asset` as the cross-inspector coverage view for all endpoint security questions.**
> The asset inventory synthesizes `antivirus` and `edr` fields from locally-inspected devices
> (Windows Workstation, Windows Server, macOS inspectors) and exposes the `inspectors` array
> showing which security tools "see" each device. This is the authoritative gap-detection method.

### Fetch Pattern

```
liongard_asset LIST environmentId=<ENV_ID> assetType=Device detail=full pageSize=200
```

Paginate until all devices retrieved. Filter returned JSON client-side.

---

### AV / EDR Coverage — Q11, Q12 (Antimalware)

**Field:** `antivirus`  
**Source:** `windows-workstation-inspector` reads `AVs[].Name` from the local system (same data as metricName=`Windows Workstation: Antivirus on System`). `windows-server-inspector` reads `AntivirusSoftware[].Name` (metricName=`Windows Server: Antivirus on System`). `mac-inspector` reads `SecurityProducts[].Name` (metricName=`macOS: Antivirus On System`). Liongard aggregates these into a single set on the device asset.  
**Format:** PostgreSQL set string e.g. `"{CylancePROTECT,Windows Defender}"` or `null`

**Field:** `edr`  
**Source:** `windows-workstation-inspector` and `windows-server-inspector` detect EDR presence via installed software enumeration and security product APIs — the same inspection pass that populates the AV field. EDR products (SentinelOne, CrowdStrike, Cylance, Huntress, etc.) are classified separately from AV.  
**Format:** PostgreSQL set string e.g. `"{CylancePROTECT}"` or `null`

These fields are populated **only when a Windows Workstation or Windows Server inspector has
locally inspected the device**. If a device is visible only through AD (no local inspection),
both fields will be `null` — this is a coverage gap signal, not confirmation that AV/EDR is
absent. Use the `inspectors` array to distinguish "not installed" from "not yet locally inspected."

```
# Compute devices with confirmed AV
records where antivirus != null AND category == "compute"
→ parse set string for product name(s): strip "{" and "}" and split on ","

# Compute devices with confirmed EDR
records where edr != null AND category == "compute"

# Compute devices with NO confirmed AV (coverage gap or not inspected)
records where antivirus == null AND category == "compute"

# Compute devices with NO confirmed EDR (highest risk)
records where edr == null AND category == "compute"

# Distinguish "not installed" from "not inspected" — check inspectors array
records where edr == null AND category == "compute"
  → for each: parse inspectors JSON
    if inspectors contains only "active-directory-inspector" → device NOT locally inspected
    if inspectors contains "windows-workstation-inspector" OR "windows-server-inspector"
      → device IS locally inspected → edr == null means EDR genuinely not detected
```

**Workbook mapping:**

| Asset filter | Workbook question | Status rule |
|---|---|---|
| `edr != null` count = total compute devices | Q11 | ✅ COMPLIANT |
| `edr == null AND locally inspected` count > 0 | Q11 | ❌ NON-COMPLIANT |
| `edr == null AND not locally inspected` count > 0 | Q11 | 🔍 REVIEW — expand inspector coverage |
| `antivirus != null` — list unique product names | Q12 | Record in Actual Value |

---

### Inspector-Based Coverage Gap Detection — Q11, Q21

The `inspectors` JSON array on each device asset reveals which Liongard inspectors are
aware of the device. This is the most reliable way to detect ungoverned endpoints:

```json
// Well-covered device — locally inspected + security tool coverage
"inspectors": [
  {"Name": "windows-workstation-inspector"},
  {"Name": "sentinelone-inspector"},
  {"Name": "ninja-rmm-inspector"}
]

// AD-only device — exists in domain but not locally inspected
"inspectors": [
  {"Name": "active-directory-inspector"}
]
// → antivirus and edr will be null; cannot confirm security posture
```

**Coverage tiers to report:**

| Inspector presence | Coverage level | Action |
|---|---|---|
| WS/Server inspector + EDR inspector | Full | ✅ Count as covered |
| WS/Server inspector, antivirus/edr populated | Good | ✅ Count as covered |
| WS/Server inspector, antivirus/edr null | Gap | ❌ EDR not detected — remediate |
| AD inspector only | Unknown | 🔍 Deploy endpoint inspector |
| No inspector at all | Shadow IT | ❌ Unauthorized or ungoverned device |

---

### OS Version / EOL Assessment — Q1, Q32

**Fields:** `operatingSystem`, `oSVersion`, `eOLDate`

```
# All compute devices with OS info
records where category == "compute" AND operatingSystem != null

# Windows 10 devices (EOL October 2025)
records where operatingSystem contains "Windows 10"

# Group by OS for distribution report
group by operatingSystem

# Devices with explicit EOL date populated
records where eOLDate != null AND eOLDate < today
```

**Common oSVersion EOL markers (Windows):**
- `10.0 (10240)` → Windows 10 1507 — EOL
- `10.0 (14393)` → Windows 10 1607 LTSB — check LTSB/LTSC support dates
- `6.0 (*)` → Windows Vista — EOL
- `6.1 (*)` → Windows 7 — EOL
- `6.2 (*)` or `6.3 (*)` → Windows 8/8.1 — EOL

---

### Additional Device Fields — Source References

**`winElevenReady`**
Source: `windows-workstation-inspector` reads hardware compatibility via WMI.
Values: `"Compatible"`, `"Incompatible"`, `"Unknown"`
Use: Q1, Q32 — Win10 EOL October 2025. `Incompatible` devices cannot upgrade via software; hardware replacement required. Filter: `operatingSystem contains "Windows 10" AND winElevenReady == "Incompatible"`.

**`warrantyExpiration`**
Source: `windows-workstation-inspector` reads SMBIOS warranty data. Also populated by RMM inspectors (NinjaRMM, ConnectWise) if warranty tracking is enabled.
Use: Q1, asset lifecycle — active warranty dates signal the org tracks hardware lifecycle.

**`physical`**
Source: `windows-workstation-inspector`, `windows-server-inspector` — determined from hypervisor detection.
Values: `true` = physical hardware, `false` = VM
Use: Q18, VND-7 — separates physical on-premises devices from VMs for the outsourced services inventory.

**`accountType` (devices)**
Source: Evaluated by Liongard from OS role and inspector type.
Values: `"workstation"`, `"laptop"`, `"server"`, `null`
Use: Q11, Q18 — break AV/EDR coverage by device class. Carriers may ask about server-specific AV separately from workstations.

**`manufacturer` / `model`**
Source: `windows-workstation-inspector` reads SMBIOS manufacturer and model strings.
Use: Q18 — hardware identity for asset lifecycle tracking.

**`interfaces`**
Source: `windows-workstation-inspector` enumerates network adapters (MAC address, IP address array).
Use: Q21 — compare IP addresses against expected subnets. Devices with IPs outside managed ranges signal unauthorized or ungoverned endpoints.

**`lastLoginUser`**
Source: `windows-workstation-inspector` reads last interactive logon username from Windows.
Use: Q21, Q38 — for shared or kiosk devices, reveals who last accessed the machine. No login user + no `lastLogin` = likely orphaned device.

**`domainRole`**
Source: `active-directory-inspector` — computer object distinguished name path (e.g. `CN=Domain Computers,CN=Users,DC=corp,DC=local`).
Use: Q18, Q21 — OU path reveals device classification. Devices in unexpected OUs may be unauthorized or miscategorized.

**`location`**
Source: RMM inspectors (NinjaRMM, ConnectWise) — may carry policy labels or security posture strings set by the MSP.
Example observed: `"No Patch or AV"` — NinjaRMM-sourced tag indicating no patch policy or AV configured on device.
Use: Q11 — if location contains security posture labels, they are direct RMM-sourced coverage gap evidence.

**`firmware`**
Source: `windows-workstation-inspector` reads BIOS/UEFI version from SMBIOS. Network device inspectors (SonicWall, Meraki, Fortinet) populate this for network hardware.
Use: Q35, Q36 — firmware version for network devices confirms current, supported firmware. Key for secure configuration attestation.

**`inventoryState` (devices)**
Source: MSP workflow state — manually set in Liongard by the MSP team.
Values: `"Discovery"` (inspector detected it, MSP not yet reviewed), `"Inventory"` (MSP categorized), `"Archive"` (MSP moved to archive)
Use: Q21 — `inventoryState == "Discovery"` = detected but not formally reviewed. Closest asset-level signal to an unreviewed device, but reflects MSP workflow state, not a definitive authorization control.


---

### Evidence Recording

When using `liongard_asset` for endpoint evidence, record in the evidence record Notes column:

```
Source: liongard_asset LIST assetType=Device · environmentId=<ENV_ID> · date=<YYYY-MM-DD>
Result: <X> of <total> compute devices have confirmed EDR; <Y> have no local inspection
Products: <list antivirus/edr values observed>
```

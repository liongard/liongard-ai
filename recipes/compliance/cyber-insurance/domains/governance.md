---
name: cyber-insurance-governance
description: >
  Domain reference for the cyber-insurance-readiness master skill. Covers Governance, Training & Policy
  (Q13, Q18, Q22–Q26, Q28–Q29, Q44–Q50). Used as a sub-reference when answering cyber insurance underwriting
  questions in this control area.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_asset"
personas: [vcio-account-manager, soc, technical-alignment-manager]
primitives:
  - metrics:microsoft-365:privileged-users-count
  - metrics:microsoft-365:privileged-users-list
  - metrics:microsoft-365:sharepoint-sites-count
---


```yaml
customize:
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed
```
# Cyber Insurance — Domain: Governance, Training & Policy

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


**Inspectors referenced:** Active Directory, Microsoft 365, KnowBe4, Manual attestation

**Question coverage:** Q13, Q18, Q22–Q26, Q28–Q29, Q44–Q50

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

## Q13 — Do you maintain a security awareness program?
**N/A**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | KnowBe4 | KnowBe4: Users Count | `Users[] \| length(@)` | = total user count |
| ✅ | KnowBe4 | KnowBe4: Current Risk Score | `AccountInfo.current_risk_score` | below threshold |
| ✅ | KnowBe4 | KnowBe4: Average User Risk Score | `Users[].current_risk_score \| avg(@)` | trending down |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q18 — Do you maintain an asset inventory?
**CIS 1.1**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Active Directory | Active Directory: Computers List | `Computers[].Name` | complete inventory |
| ✅ | Active Directory | Active Directory: Count of Joined Computers | `length(Computers)` | document count |
| ✅ | Active Directory | Active Directory: Workstation Count | `Computers[?Type==`Workstation`] \| length(@)` | document count |
| ✅ | Active Directory | Active Directory: Server Count | `Computers[?Type==`Server`] \| length(@)` | document count |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q22 — Do you maintain a Data Handling Policy?
**N/A**

> ℹ️ **No Liongard metric available.** This question requires manual attestation.
> See the Manual Attestation sheet in the evidence record for guidance.

---

## Q23 — Does your organization know where ALL sensitive data is stored?
**CIS 3.2**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Microsoft 365 | Microsoft OneDrive: Total Drives Count | `OneDrives[] \| length(@)` | document |
| ✅ | Microsoft 365 | Microsoft OneDrive: Total Size of All Drives | `OneDrives[?quota.used!=null].quota.used \| sum(@) \| floo...` | document |
| ✅ | Microsoft 365 | Microsoft SharePoint: Total Sites Count | `sites[] \| length(@)` | document |
| ✅ | Microsoft 365 | Microsoft SharePoint: Total Lists Count | `lists[] \| length(@)` | document |
| ✅ | Microsoft 365 | Azure Active Directory: SharePoint Library User Access | `Groups.ActiveGroups[?groupType_r == 'Microsoft 365 group'...` | review |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q24 — What types of data do you collect/process/store?
**N/A**

> ℹ️ **No Liongard metric available.** This question requires manual attestation.
> See the Manual Attestation sheet in the evidence record for guidance.

---

## Q25 — How many sensitive data records do you maintain?
**N/A**

> ℹ️ **No Liongard metric available.** This question requires manual attestation.
> See the Manual Attestation sheet in the evidence record for guidance.

---

## Q26 — Where is sensitive data stored?
**N/A**

> ℹ️ **No Liongard metric available.** This question requires manual attestation.
> See the Manual Attestation sheet in the evidence record for guidance.

---

## Q28 — Do you limit who has access to sensitive data?
**CIS 3.3**

**Fetch protocol:**
1. Resolve the inspector system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. For each metric below: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record the evaluated value as evidence; set status to ✅ COMPLIANT / ⚠️ PARTIAL / ❌ NON-COMPLIANT / 🔍 REVIEW / ℹ️ MANUAL

| Evidence | Inspector | Metric Name | JMESPath Query | Compliant When |
|-----------|-----------|-------------|----------------|----------------|
| ✅ | Microsoft 365 | Azure Active Directory: SharePoint Library User Access | `Groups.ActiveGroups[?groupType_r == 'Microsoft 365 group'...` | restricted |
| ✅ | Microsoft 365 | Office 365: Privileged Users Count | `Users[?Privileged == `Yes`] \| length(@)` | low, least-privilege |
| ✅ | Microsoft 365 | Office 365: Privileged Users List | `Users[?Privileged==`Yes`] \| sort_by(@,&id)[].[displayNam...` | review |
| ✅ | Microsoft 365 | Microsoft SharePoint: Total Sites Count | `sites[] \| length(@)` | document |
| ✅ | Microsoft 365 | Microsoft OneDrive: List of Users | `Users[].displayName` | review — active employees only |

**Interpretation:**
- ✅ **Compliant** — all metrics return values matching 'Compliant When' column
- ⚠️ **Partial** — most compliant but exceptions exist; document in Notes column
- ❌ **Non-Compliant** — one or more metrics show risk; flag for remediation

---

## Q29 — Do you have a formal approval process for granting access?
**CIS 6.1**

> ℹ️ **No Liongard metric available.** This question requires manual attestation.
> See the Manual Attestation sheet in the evidence record for guidance.

---

## Q44 — Does the organization maintain a formal incident response plan?
**CIS 17.4**

> ℹ️ **No Liongard metric available.** This question requires manual attestation.
> See the Manual Attestation sheet in the evidence record for guidance.

---

## Q45 — Does the IR plan include [check all that apply]?
**N/A**

> ℹ️ **No Liongard metric available.** This question requires manual attestation.
> See the Manual Attestation sheet in the evidence record for guidance.

---

## Q47 — Do all funds transfer requests require out-of-band verification?
**N/A**

> ℹ️ **No Liongard metric available.** This question requires manual attestation.
> See the Manual Attestation sheet in the evidence record for guidance.

---

## Q48 — Does your org maintain ICS/SCADA/OT environments?
**N/A**

> ℹ️ **No Liongard metric available.** This question requires manual attestation.
> See the Manual Attestation sheet in the evidence record for guidance.

---

## Q49 — Is your OT environment logically/physically separated from IT?
**N/A**

> ℹ️ **No Liongard metric available.** This question requires manual attestation.
> See the Manual Attestation sheet in the evidence record for guidance.

---

## Q50 — Does remote access into OT require MFA?
**N/A**

> ℹ️ **No Liongard metric available.** This question requires manual attestation.
> See the Manual Attestation sheet in the evidence record for guidance.

---

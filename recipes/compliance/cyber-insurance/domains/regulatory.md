---
name: cyber-insurance-regulatory
description: >
  Domain reference for the cyber-insurance-readiness master skill. Covers Regulatory & Privacy
  (REG-1 through REG-8 (HIPAA, GDPR, PCI-DSS, privacy governance)). Used as a sub-reference when answering cyber insurance underwriting
  questions in this control area.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_asset"
personas: [vcio-account-manager, soc, technical-alignment-manager]
primitives:
  - metrics:active-directory:privileged-users-list
  - metrics:microsoft-365:privileged-users-list
---


```yaml
customize:
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed
```
# Cyber Insurance — Domain: Regulatory & Privacy

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


**Inspectors referenced:** Manual attestation primarily; KnowBe4 (REG-8 awareness)

**Question coverage:** REG-1 through REG-8 (HIPAA, GDPR, PCI-DSS, privacy governance)

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

| Question | Control | Liongard Signal | Primary Source |
|---|---|---|---|
| REG-1a/b | HIPAA applicability + compliance | None | Attestation only |
| REG-2a/b | GDPR applicability + compliance | None | Attestation only |
| REG-3a–f | PCI-DSS applicability + controls | None | Attestation / QSA |
| REG-4 | Chief Privacy Officer | None | Attestation only |
| REG-5 | Public privacy policy | None | Attestation only |
| REG-6 | Data classification procedures | ⚠️ Partial — access controls | AD/M365 privileged user lists |
| REG-7 | Data retention/destruction | None | Attestation only |
| REG-8 | Annual privacy/security training | ⚠️ Partial — KnowBe4 | See Q13 in Assessment sheet |

---

## REG-1 — HIPAA Compliance

**Form source:** Travelers Q7  
**Coverage:** `ℹ️ MANUAL`

Questions to answer:
- Is the organization a Healthcare Provider, Business Associate, or Covered Entity under HIPAA?
- If yes: Is the organization currently HIPAA compliant?

**Evidence to collect:**
- Applicability determination (legal counsel or compliance officer)
- Most recent HIPAA risk assessment (required under 45 CFR § 164.308)
- Business Associate Agreements (BAAs) with any vendors handling PHI
- Incident response policy covering PHI breach notification (45 CFR § 164.400)

**Note:** Liongard does not inspect PHI data stores or HIPAA-specific controls. However, the
Access Control, Audit Log, and Encryption evidence gathered elsewhere in this workbook
(Q27 encryption, Q42 audit logging, Q30 user termination) constitutes supporting evidence for
a HIPAA compliance program and should be cross-referenced in the attestation.

---

## REG-2 — GDPR Compliance

**Form source:** Travelers Q8  
**Coverage:** `ℹ️ MANUAL`

Questions to answer:
- Is the organization subject to GDPR? (Applies if org processes personal data of EU residents,
  regardless of where the org is located)
- If yes: Is the organization currently GDPR compliant?
- If not yet compliant: What steps are being taken toward compliance?

**Evidence to collect:**
- Legal determination of GDPR applicability
- Data Protection Officer (DPO) designation if required (Art. 37)
- Records of Processing Activities (ROPA) document (Art. 30)
- Data Subject Rights procedures (Art. 15–22)
- Data Processing Agreements (DPAs) with third-party processors

---

## REG-3 — PCI-DSS Compliance

**Form source:** Travelers Q11  
**Coverage:** `ℹ️ MANUAL`

Questions to answer:
- Does the organization collect, process, store, or accept payment card data?
- If yes:
  - Is the organization currently PCI-DSS compliant?
  - What is the organization's reporting level? (1 / 2 / 3 / 4)
  - Was the last PCI assessment conducted within the past 12 months?
  - Does the payment environment use End-to-End or Point-to-Point (E2E/P2P) encryption?
  - Is card data encrypted or tokenized when stored?
  - Do card-present transactions use EMV-capable devices?

**Reporting Levels (Visa/Mastercard):**

| Level | Annual Transactions |
|---|---|
| 1 | > 6 million |
| 2 | 1–6 million |
| 3 | 20,000–1 million (e-commerce) |
| 4 | < 20,000 (e-commerce) or < 1 million (all other) |

**Evidence to collect:**
- Attestation of Compliance (AOC) or Self-Assessment Questionnaire (SAQ)
- QSA name and assessment date (Level 1)
- E2E/P2PE solution vendor and validation certificate
- Tokenization provider documentation

---

## REG-4 — Chief Privacy Officer / Privacy Responsibility Owner

**Form source:** Travelers Q9a  
**Coverage:** `ℹ️ MANUAL`

**Question:** Does the organization have a Chief Privacy Officer or individual assigned responsibility
for monitoring changes in privacy statutes and regulations?

**Evidence to collect:** Named individual, title, date assigned. Note: this is distinct from the
CISO role (Q10a in the Assessment sheet). The CPO focuses on regulatory privacy requirements
while the CISO owns security program execution.

---

## REG-5 — Public Privacy Policy

**Form source:** Travelers Q9b  
**Coverage:** `ℹ️ MANUAL`

**Question:** Does the organization maintain a publicly available privacy policy that has been
reviewed by an attorney?

**Evidence to collect:**
- URL of published privacy policy
- Date of most recent attorney review
- Name of reviewing attorney or firm (optional)

---

## REG-6 — Sensitive Data Classification & Inventory Procedures

**Form source:** Travelers Q9c  
**Coverage:** `⚠️ PARTIAL`

**Question:** Does the organization maintain sensitive data classification and inventory procedures?

**Fetch protocol:**
1. Resolve system: `liongard_system LIST searchMode=keyword query="<inspector_type>" environmentId=<ENV_ID>`
2. Evaluate: `liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>`
3. Record → Regulatory & Privacy sheet evidence column; set Status in status column

| Evidence | Inspector | Metric Name | JMESPath | Compliant When |
|---|---|---|---|---|
| ✅ | Microsoft 365 | Office 365: Privileged Users List | `Users[?Privileged==\`Yes\`] \| sort_by(@,&id)[].[displayName]` | role-appropriate only |
| ✅ | Active Directory | Active Directory: Privileged Users List | `SystemInfo.PrivilegedUsersStr` | role-appropriate only |
| ✅ | Microsoft 365 | Office 365: Privileged Users with Overuse Count | `length(Users[?Privileged==\`Yes\`&&Assigned_Products])` | 0 |

**Interpretation:** Liongard confirms that access to sensitive systems is role-restricted (supporting
a classification program), but a written data classification schema with labeled tiers (e.g.,
Public / Internal / Confidential / Restricted) requires manual attestation. Cross-reference with
workbook Q28 (who has access to sensitive data) and Q29 (access approval process).

---

## REG-7 — Data Retention, Destruction, and Record Keeping

**Form source:** Travelers Q9d  
**Coverage:** `ℹ️ MANUAL`

**Question:** Does the organization maintain data retention, destruction, and record keeping procedures?

**Evidence to collect:**
- Written retention schedule (document type → retention period)
- Documented destruction method for each media type (digital, physical)
- Certificate of Destruction examples for hardware disposals
- Any automated retention enforcement (e.g., M365 retention policies) — note presence in attestation

---

## REG-8 — Annual Privacy & Security Training

**Form source:** Travelers Q9e  
**Coverage:** `⚠️ PARTIAL` — KnowBe4 provides metric-level evidence; see Q13 in Assessment sheet

**Question:** Does the organization conduct annual privacy and information security training for all employees?

**Fetch protocol:** Use existing Q13 metrics from the Assessment sheet.

| Evidence | Inspector | Metric Name | Compliant When |
|---|---|---|---|
| See Q13 | KnowBe4 | Training campaign completion metrics | ≥ 95% completion rate |

**Manual component:** Confirm that the training curriculum includes privacy-specific topics
(data handling, PII, breach reporting) not just general security awareness. If using a platform
other than KnowBe4 (e.g., Proofpoint, SANS, internal LMS), note the platform and attach a
completion report.

---

## Key Cross-References

| Regulatory Requirement | Supporting Workbook Questions |
|---|---|
| HIPAA Access Controls | Q14 (dedicated admin accounts), Q28 (data access limits), Q30 (termination) |
| HIPAA Audit Controls | Q42 (audit logging policy) |
| HIPAA Encryption | Q27 (encryption at rest and in transit) |
| HIPAA Incident Response | Q44 (IR plan) |
| GDPR Data Subject Rights | REG-7 (retention/destruction), Q24 (data types), Q26 (data location) |
| PCI-DSS Network Controls | Q37 (firewall), Q3 (remote access MFA), Q10b (active firewall) |
| PCI-DSS Patch Management | Q8–Q10 (patching cadence and criticality) |
| PCI-DSS Logging | Q42 (audit logging) |

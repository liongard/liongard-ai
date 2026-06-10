---
name: cyber-insurance-at-bay
description: >
  Use this recipe when filling out the At-Bay Cyber Insurance Application (AB-CYB-APP,
  Ed. 09/2023), the Cyber Insurance Renewal Application (AB-CYB-RAP), or the At-Bay
  Ransomware Supplemental Application (AB-CYB-RWS). Trigger phrases: "fill out At-Bay
  cyber application", "At-Bay renewal", "At-Bay ransomware supplemental", "answer At-Bay
  underwriting questions". Carrier-specific variant of the cyber-insurance-readiness
  master recipe, mapping each At-Bay question to Liongard evidence patterns.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_metric, liongard_identity, liongard_device, liongard_domain"
personas: [vcio-account-manager, technical-alignment-manager]
output_formats: [xlsx, word, markdown]
primitives: []
composes:
  - recipe:compliance:cyber-insurance-readiness
  - recipe:single-system:single-system-active-directory
  - recipe:single-system:single-system-knowbe4
  - recipe:single-system:single-system-network-ip-address
  - recipe:system-type:system-type-all-edrs
---


```yaml
customize:
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed
```
# Cyber Insurance — Carrier: At-Bay

> **Pairs with:** `recipes/compliance/cyber-insurance/cyber-insurance-readiness.md` (master workflow,
> customization block, asset-inventory schema) and the seven `domains/` files for full metric tables.

**Forms covered:**
- At-Bay Cyber Insurance Application (AB-CYB-APP-COV, Ed. 09/2023) — new business
- At-Bay Cyber Insurance Renewal Application (AB-CYB-RAP) — renewal
- At-Bay Ransomware Supplemental Application (AB-CYB-RWS, Ed. 09/2025) — supplemental for high-risk accounts

**Important At-Bay context:** At-Bay includes the **Stance Exposure Manager** and **Managed
Security** services with every policy. After binding, At-Bay scans the insured's public attack
surface and sends security advisories. The Ransomware Supplemental (AB-CYB-RWS) is triggered when
At-Bay's underwriting scan detects elevated ransomware risk signals (open RDP, legacy OS, weak MFA).
Run `all-external-attack-surface.md` proactively — it surfaces the same signals At-Bay's scan checks.

---

## How to run

1. Run the master recipe's Steps 1–3.
2. For renewal, confirm whether the Ransomware Supplemental is required (At-Bay may trigger it
   based on their own scan — check with the broker before the renewal date).
3. For each section below, pull the referenced domain evidence. Items marked `MANUAL` require
   written attestation.

---

## Coverage Summary — New Business Application (AB-CYB-APP)

| Section | Questions | Liongard Coverage |
|---|---|---|
| General Information (01) | Applicant info, revenue, e-commerce % | `MANUAL` |
| Sensitive data scope (03–04) | Record count, data types | `MANUAL` |
| Encryption & Governance (05–06) | DB/server encryption, written policies | `PARTIAL` — server-disk encryption confirmed; DB-level is manual |
| Regulatory (07–10) | HIPAA, PCI compliance levels | `MANUAL` |
| Financial Fraud (11–12) | Wire transfer controls, security training | `MANUAL` |
| Security Controls (13) | AV, DLP, IDS/IPS, MFA, pen test | `PARTIAL` — AV/EDR and MFA confirmed via Liongard; DLP/IDS/pen test are manual |
| MFA — Email (14) | Email MFA enforced on ALL access | `LIONGARD` |
| MFA — Remote Access (15) | VPN / remote network access MFA | `LIONGARD` |
| Email Security (16) | Inbound SEG / email filtering product | `PARTIAL` — email inspector confirms M365/Google; SEG vendor is manual |
| EDR (17) | EDR product(s) in use | `LIONGARD` — EDR inspector coverage rate |
| Backups (18–19, 21) | Backup procedures, offline backups, BCP | `PARTIAL` — frequency and isolation confirmed; BCP testing is manual |
| Media (22–23) | Licensed content, legal review | `MANUAL` |
| Loss History (24–25) | Prior incidents, known circumstances | `MANUAL` |

---

## Question Mapping — New Business (AB-CYB-APP)

### Sections 01–04 — General / Data Scope
**Coverage:** `MANUAL` for revenue, data type classification, and record counts.

**Partial evidence:** `liongard_identity COUNT environmentId=<ENV_ID>` provides employee identity
count as a lower bound for internal-records scope. PII/PHI/PCI data classification requires
client attestation.

---

### Section 05 — Database and Server Encryption
**Form:** Does Applicant encrypt data stored and processed on databases and servers?

**Coverage:** `PARTIAL`

**Domain reference:** `domains/endpoint.md` — "Encryption at Rest" section

**Evidence:**
- Windows Server BitLocker: metricName=`Windows Server: All Drives Encrypted`
- Linux disk encryption: per-system check via `liongard_metric EVALUATE` on Linux inspector
- Database-level encryption (TDE, column-level) is not exposed by Liongard — requires DBA attestation

**Answer guidance:** Answer Yes if full-disk encryption is confirmed on all servers AND database
encryption is attested. Note disk-level vs. database-level distinction in the gap summary.

---

### Section 06 — Written Security Policies
**Coverage:** `MANUAL` — governance documentation attestation.

---

### Sections 07–10 — Regulatory (HIPAA / PCI)
**Coverage:** `MANUAL`

**Supporting evidence:** M365 and Active Directory inspectors can surface user access scope
(who has access to what systems) as supporting evidence for HIPAA access controls — but
compliance attestation itself is manual.

---

### Sections 11–12 — Financial Fraud / Training
**Coverage:** `MANUAL`

**Note:** Security awareness training (Q12) — Liongard does not inspect training platforms
directly. If the MSP uses KnowBe4, run `recipes/single-system-analysis/by-inspector/knowbe4.md`
for training completion rate evidence.

---

### Section 13 — Security Controls Inventory
**Form:** Which security controls are in use? (Antivirus, DLP, IDS/IPS, MFA, pen tests)

**Coverage:** `PARTIAL`

| Control | Coverage | Evidence |
|---|---|---|
| Antivirus | `LIONGARD` | `liongard_device` → `inspectors[]` for AV/EDR coverage; per-EDR inspector metrics |
| DLP | `MANUAL` | Not inspected by Liongard |
| IDS/IPS | `MANUAL` | Firewall inspector may surface IPS service status — see `domains/network.md` |
| MFA | `LIONGARD` | `liongard_identity COUNT mfaStatus="NO"` |
| Pen tests | `MANUAL` | Process / policy attestation |

---

### Section 14 — Email MFA
**Form:** Does Applicant have MFA enforced on ALL email access?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/auth.md` — "Email MFA" section

```
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true
```

**Answer guidance:** Answer Yes only if count = 0. At-Bay treats email MFA as a hard underwriting
requirement — any gap may result in a subjectivity or premium loading.

---

### Section 15 — Remote Access MFA
**Form:** Does Applicant have MFA enforced on ALL remote access including VPN?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/auth.md` — "Remote Access MFA"; `domains/network.md` — "RDP / VPN"

**Evidence:**
- RDP disabled or MFA-gated: Windows Server/Workstation inspector metrics
- VPN authentication: SonicWall, Fortinet, Sophos firewall inspector metrics — see deployed firewall recipe
- External port 3389 exposure: `recipes/single-system-analysis/by-inspector/network-ip-address.md`

**Answer guidance:** Answer Yes only if ALL remote paths (VPN, RDP, RDWeb, RD Gateway) require
MFA. Open RDP without MFA is one of At-Bay's top ransomware risk triggers — surface it explicitly.

---

### Section 16 — Inbound Email Security / SEG
**Form:** Which Inbound Email Security (SEG) products does Applicant use?

**Coverage:** `PARTIAL`

**Evidence:**
- M365 Defender for Office 365 / Exchange Online Protection: M365 inspector confirms deployment
- Google Workspace spam/phishing filters: Google Workspace inspector
- Third-party SEG (Mimecast, Proofpoint, Barracuda): not directly inspected by Liongard —
  confirm vendor name from the client's M365/Exchange mail flow configuration

---

### Section 17 — EDR Product
**Form:** Which Endpoint Detection & Response (EDR) products does Applicant use?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/endpoint.md` — "EDR Coverage" section

**Evidence:** Run `recipes/system-type-assessment/all-edrs.md` to identify which EDR inspectors
are deployed and their coverage rates. Use `liongard_device LIST environmentId=<ENV_ID>` →
filter for devices where `inspectors[]` does NOT contain an EDR slug → unprotected device count.

**Answer guidance:** Report the EDR vendor(s) deployed, % coverage rate, and unprotected count.
At-Bay's forms list specific accepted EDR products — verify the deployed product is on the list.

---

### Sections 18–21 — Backups and BCP
**Form:** Backup procedures, offline storage, BCP tested in last year.

**Coverage:** `PARTIAL`

**Domain reference:** `domains/backup.md` — "Backup Frequency", "Backup Isolation", "BCP Testing"

**Evidence:**
- Backup job recency and frequency: backup vendor inspector dataprint (Datto BCDR, Acronis,
  Axcient, Cove, Veeam) — use the relevant single-system backup recipe
- Offline / air-gap / cloud isolation: backup inspector configuration fields confirm or manual
- BCP testing: `MANUAL` — requires documented test results

---

### Sections 22–25 — Media / Loss History
**Coverage:** `MANUAL` throughout.

---

## Coverage Summary — Renewal Application (AB-CYB-RAP)

The renewal form is shorter and focused on *changes since last policy*. Key Liongard-relevant
renewal questions:

| Renewal Question | Coverage | Evidence / Notes |
|---|---|---|
| Changes to MFA deployment | `LIONGARD` | Re-run `liongard_identity COUNT mfaStatus="NO"` — compare to prior year |
| Changes to EDR deployment | `LIONGARD` | Re-run `all-edrs.md` — note any new or removed EDR inspectors |
| VPN details (provider, MFA method) | `PARTIAL` | Firewall inspector confirms VPN type; MFA method is manual |
| MSP usage (managed or self-managed) | `PARTIAL` | RMM inspector presence confirms managed model |
| Backup immutability | `PARTIAL` | Backup inspector config fields; full immutability confirmation may be manual |
| EDR management model (MDR vs. self-managed) | `PARTIAL` | EDR inspector metadata; MDR/MSSP model is manual |
| Open RDP check | `LIONGARD` | External attack surface recipe — port 3389 exposure |

---

## Ransomware Supplemental (AB-CYB-RWS) — Key Sections

The Ransomware Supplemental asks deep technical questions. Liongard covers the strongest evidence:

| RWS Section | Key Questions | Coverage |
|---|---|---|
| IT Architecture | AD/Azure AD deployment, domain structure | `PARTIAL` — AD inspector confirms; Azure AD via M365 |
| Patch Management | Critical patch SLA, vulnerability scanning | `PARTIAL` — Windows patching metrics; scanner is manual |
| Privileged Access | PAM tool, separate admin accounts, local admin uniqueness | `PARTIAL` — AD privileged user metrics; PAM tool is manual |
| Network Security | Network segmentation, VLAN structure, firewall vendor | `PARTIAL` — firewall inspector; VLAN design is manual |
| Endpoint Deployment | EDR vendor, % deployed on servers and workstations | `LIONGARD` — EDR inspector coverage rates |
| Remote Access | VPN MFA, RDP exposure, IP whitelisting | `LIONGARD` — firewall + external attack surface |
| OT / ICS Environments | OT present, air-gap status | `MANUAL` — not inspected by Liongard |

**For the Ransomware Supplemental, run these recipes before the application:**
1. `recipes/system-type-assessment/all-edrs.md` — EDR coverage rates (servers + workstations)
2. `recipes/single-system-analysis/by-inspector/network-ip-address.md` — open RDP / external exposure
3. `recipes/single-system-analysis/by-inspector/active-directory.md` — AD privileged user and policy posture
4. `all-windows-patching.md` — patch cadence evidence

---

## Verification Log

| Item | Source | Notes |
|---|---|---|
| New business question set (AB-CYB-APP) | `internal/cyber-insurance-forms/at-bay/at-bay-cyber-insurance-new-business-application-2023.txt` | Full extraction |
| Renewal question set (AB-CYB-RAP) | `internal/cyber-insurance-forms/at-bay/at-bay-cyber-renewal-application-2025.txt` | Key renewal deltas |
| Ransomware Supplemental (AB-CYB-RWS) | `internal/cyber-insurance-forms/at-bay/at-bay-ransomware-supplemental-application-2025.txt` | Deep technical sections |
| Evidence mapping | `domains/auth.md`, `domains/endpoint.md`, `domains/backup.md`, `domains/network.md` | Metric source of truth |

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | At-Bay draws heavily on identity and endpoint inventory — the onboarding assessment populates MFA status, EDR deployment, and backup architecture directly. |
| CIS Controls (v8.1) | ✅ | At-Bay maps to: CIS 5–6 (§14–15 email + remote MFA), CIS 10 (§18–21 backup + RTO/RPO), CIS 7 (§16 patching cadence), CIS 13 (§17 EDR), CIS 12 (§22 network segmentation), CIS 17–18 (§23–24 IR + BCP). |
| Cyber-insurance domain files | ✅ | `domains/auth.md` (§14–15 MFA), `domains/endpoint.md` (§16–17 patching + EDR), `domains/backup.md` (§18–21 backup + recovery), `domains/network.md` (§22 segmentation + VPN), `domains/governance.md` (§23–25 IR + training + vendor). |
| QBR / quarterly-business-review | ✅ | At-Bay renewal supplements (AB-CYB-RWS ransomware supplemental) are best addressed at the QBR closest to renewal — run the four referenced single-system recipes before the renewal QBR to populate ransomware-specific evidence. |

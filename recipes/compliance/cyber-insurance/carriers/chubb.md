---
name: cyber-insurance-chubb
description: >
  Use this recipe when filling out the Chubb Cyber Enterprise Risk Management (ERM)
  Policy — Cyber and Privacy Insurance New Business Application (PF-48163, Ed. 08/17
  or current). Trigger phrases: "fill out Chubb cyber application", "Chubb Cyber ERM
  renewal", "Chubb cyber application", "answer Chubb underwriting questions".
  Carrier-specific variant of the cyber-insurance-readiness master recipe.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_metric, liongard_identity, liongard_device"
personas: [vcio-account-manager, technical-alignment-manager]
output_formats: [xlsx, word, markdown]
primitives: []
composes:
  - recipe:compliance:cyber-insurance-readiness
  - recipe:system-type:system-type-windows-patching
---


```yaml
customize:
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed
```
# Cyber Insurance — Carrier: Chubb

> **Pairs with:** `recipes/compliance/cyber-insurance/cyber-insurance-readiness.md` (master workflow)
> and the `domains/` files for full metric tables.

**Forms covered:**
- Chubb Cyber ERM — Cyber and Privacy Insurance New Business Application (PF-48163, Ed. 08/17)
- Chubb Cyber ERM — Small Business Application (PF-48163, Ed. 10/16)

**Important Chubb context:** The Chubb Cyber ERM form is a concise checklist (six security
controls + regulatory questions). It is not as granular as At-Bay or Corvus. The strongest
evidence Liongard can provide maps to controls 1, 2, 4, and 5. For larger accounts, Chubb
may supplement with a more detailed questionnaire or supplemental from the underwriter.

---

## Coverage Summary

| Section | Controls | Coverage |
|---|---|---|
| §4.1 — Antivirus and Firewalls | AV + firewall | `LIONGARD` |
| §4.2 — Encryption of Sensitive Data | Data encryption | `PARTIAL` |
| §4.3 — Encryption of Mobile Computing Devices | Mobile / laptop encryption | `LIONGARD` |
| §4.4 — Critical Software Patching | Patch management | `LIONGARD` |
| §4.5 — Critical Data Backup and Recovery | Backup procedures | `PARTIAL` |
| §4.6 — Formal Cyber Incident Response Plan | IR plan | `MANUAL` |
| PCI — Payment card compliance | PCI DSS | `MANUAL` |
| HIPAA — PHI compliance | HIPAA | `MANUAL` |
| California / CMIA | State privacy | `MANUAL` |
| Trademark review | IP/media | `MANUAL` |

---

## Question Mapping

### §4.1 — Antivirus and Firewalls

**Form:** Which IT security controls does the Applicant have in place?
— Antivirus and Firewalls (Windows 7 or higher qualifies)

**Coverage:** `LIONGARD`

| Sub-control | Domain reference | Evidence |
|---|---|---|
| Antivirus / endpoint protection | `domains/endpoint.md` | `liongard_device` → `inspectors[]`; `all-edrs.md` |
| Firewalls | `domains/network.md` | Firewall inspector presence; deployed firewall recipe |

**Note:** Chubb's form parenthetically notes "Windows 7 or higher qualifies" for the AV check,
meaning the OS-level Windows Security Center / Defender counts. However, a dedicated EDR provides
stronger evidence — lead with EDR coverage rate if available.

---

### §4.2 — Encryption of Sensitive Data

**Form:** Encryption of Sensitive Data?

**Coverage:** `PARTIAL`

**Domain reference:** `domains/endpoint.md` — "Encryption at Rest"

**Evidence:**
- Server and workstation full-disk encryption: metricNames `Windows Workstation: All Drives Encrypted`, `Windows Server: All Drives Encrypted`, `macOS: File Vault Encryption Status`
- Database-level encryption (TDE): not inspected — requires DBA attestation
- Cloud data encryption: M365 / cloud inspector (platform default) — partially confirmed

---

### §4.3 — Encryption of Mobile Computing Devices

**Form:** Encryption of Mobile Computing Devices?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/endpoint.md` — "Encryption at Rest"

**Evidence:**
- Windows laptops (BitLocker): metricNames `Windows Workstation: Bitlocker Status Summary [VI]`, `Windows Workstation: All Drives Encrypted`
- macOS laptops (FileVault): metricName `macOS: File Vault Encryption Status`
- Mobile devices (MDM-managed): not directly inspected by Liongard — confirm MDM encryption
  policy from admin if applicable

---

### §4.4 — Critical Software Patching Procedures

**Form:** Critical Software Patching Procedures?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/endpoint.md` — "Patch Management"

**Evidence:** `recipes/system-type-assessment/all-windows-patching.md`. For macOS/Linux,
run the respective single-system recipes.

---

### §4.5 — Critical Data Backup and Recovery Procedures

**Form:** Critical Data Backup and Recovery Procedures?

**Coverage:** `PARTIAL`

**Domain reference:** `domains/backup.md`

**Evidence:** Use the deployed backup vendor recipe to confirm backup procedures are in place
and jobs are running. Recovery procedures (tested restore) require manual attestation.

---

### §4.6 — Formal Cyber Incident Response Plan

**Coverage:** `MANUAL` — governance documentation attestation.

---

### Regulatory Questions

| Question | Coverage | Notes |
|---|---|---|
| PCI compliance (via assessment or self-attestation) | `MANUAL` | Payment card compliance attestation |
| HIPAA / HITECH compliance | `MANUAL` | Healthcare compliance attestation |
| California / CMIA exposure | `MANUAL` | Legal jurisdiction attestation |
| Trademark legal review | `MANUAL` | Legal / IP review attestation |

---

## Record Count (§1)

**Form:** Maximum number of unique individuals whose Protected Information could be compromised:
[<1,000 / 1,001–10,000 / 10,001–100,000 / 100,001–500,000 / 500,001–1M / >1M]

**Coverage:** `PARTIAL`

**Evidence:** `liongard_identity COUNT environmentId=<ENV_ID>` provides employee identity count.
Customer, partner, and third-party record volumes require client attestation.

---

## Verification Log

| Item | Source | Notes |
|---|---|---|
| PF-48163 Ed. 08/17 | `internal/cyber-insurance-forms/chubb/chubb-cyber-privacy-new-business-application-2017.txt` | Full extraction |
| Small business edition Ed. 10/16 | `internal/cyber-insurance-forms/chubb/chubb-cyber-erm-small-business-application-2016.txt` | Similar controls, adds Cyber Crime section |
| Evidence mapping | `domains/endpoint.md`, `domains/network.md`, `domains/backup.md` | Domain files are metric source of truth |

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | Chubb Cyber ERM security checklist maps efficiently to onboarding inventory — endpoint encryption, patching, and AV/firewall presence are all captured at onboarding. |
| CIS Controls (v8.1) | ✅ | Chubb maps to: CIS 13 (§4.1 AV + §4.1 firewall), CIS 6 (§4.2 admin privilege controls), CIS 3 (§4.3 mobile/laptop encryption), CIS 7 (§4.4 patching), CIS 5 (§4.5 remote access MFA), CIS 17 (§4.6 IR plan). |
| Cyber-insurance domain files | ✅ | `domains/auth.md` (§4.2 admin controls + §4.5 MFA), `domains/endpoint.md` (§4.1 AV + firewall + §4.3 encryption + §4.4 patching), `domains/governance.md` (§4.6 IR plan), `domains/network.md` (§4.1 firewall controls). |
| QBR / quarterly-business-review | ✅ | Chubb uses a compact 6-control checklist — the QBR closest to renewal should validate each control row with current Liongard evidence. §4.6 (IR plan) requires MANUAL attestation; confirm IR plan exists and is dated within 12 months. |

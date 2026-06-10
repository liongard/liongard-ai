---
name: cyber-insurance-hiscox
description: >
  Use this recipe when filling out the Hiscox PRO® Tech & Cyber Renewal Application
  (PLP_A0002) or a Hiscox CyberClear application form. Trigger phrases: "fill out
  Hiscox cyber application", "Hiscox PRO cyber renewal", "Hiscox CyberClear application",
  "answer Hiscox underwriting questions". Carrier-specific variant of the
  cyber-insurance-readiness master recipe.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_metric, liongard_identity, liongard_device"
personas: [vcio-account-manager, technical-alignment-manager]
output_formats: [xlsx, word, markdown]
primitives: []
composes:
  - recipe:compliance:cyber-insurance-readiness
  - recipe:single-system:single-system-internet-domain-dns
  - recipe:single-system:single-system-tls-ssl
---


```yaml
customize:
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed
```
# Cyber Insurance — Carrier: Hiscox

> **Pairs with:** `recipes/compliance/cyber-insurance/cyber-insurance-readiness.md` (master workflow)
> and the `domains/` files for full metric tables.

**Forms covered:**
- Hiscox PRO® Tech & Cyber Renewal Application (PLP_A0002) — combined Tech Professional
  Liability, Data Breach & Privacy Security Liability, and Cyber Enhancements

**Form availability note:** Hiscox's online broker portal forms (new business application PDFs)
require authentication and are not publicly accessible. The PLP_A0002 DOC file is the primary
reference available in this library. For current form versions, access the Hiscox broker portal
or request the latest form from the Hiscox PRO team.

**Hiscox product coverage (PLP_A0002 is a combined form):**
- Technology Professional Liability — 3rd party claims from technology services
- Data Breach & Privacy Security Liability — breach response costs + 3rd party privacy claims
- Cyber Enhancements: Hacker Damage, Cyber Business Interruption, Cyber Extortion

---

## Coverage Summary

The PLP_A0002 form is modular — applicants select coverages in Section 1 and complete only
the relevant sections. The table below covers the data breach / cyber sections most relevant
to MSP clients.

| Section | Topic | Coverage |
|---|---|---|
| §1 — Coverage selection + applicant details | General info, subsidiaries | `MANUAL` |
| §2 — Material supplier relationships | Vendor dependency | `PARTIAL` |
| §3 — Technology Professional Liability | Revenue allocation, contracts | `MANUAL` |
| Data Breach — Record scope | Data subject volume | `MANUAL` |
| Data Breach — Dual-factor authentication | MFA on sensitive systems | `LIONGARD` |
| Data Breach — Encryption | Encryption at rest and in transit | `LIONGARD` |
| Data Breach — Employee background checks | HR controls | `MANUAL` |
| Data Breach — Security awareness | Training | `PARTIAL` |
| Data Breach — PCI/HIPAA scope | Regulatory compliance | `MANUAL` |
| Cyber — Network security controls | AV, firewall, patch, backup | `PARTIAL` |
| Cyber — Incident response | IR plan existence | `MANUAL` |

---

## Question Mapping

### §2 — Material Supplier Relationships

**Form:** Identify any new material supplier relationships established in the last year upon
whom you depend to conduct professional or technology services.

**Coverage:** `PARTIAL`

**Domain reference:** `domains/vendor.md`

**Evidence:**
- Cloud infrastructure: AWS, Azure, Cloudflare inspectors in `liongard_launchpoint LIST`
- IT management / RMM: RMM inspector presence signals key vendor dependency
- Other suppliers: `MANUAL` — not inspected by Liongard

---

### Data Breach — Dual-Factor Authentication

**Form:** Is dual-factor authentication in place for access to sensitive data systems?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/auth.md` — "MFA" sections

```
# All enabled identities without MFA
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true

# Privileged identities without MFA (highest risk for sensitive system access)
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true privileged=true
```

---

### Data Breach — Encryption

**Form:** Is sensitive data encrypted at rest and in transit?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/endpoint.md` — "Encryption at Rest"; TLS recipe for in-transit

**At rest:**
- Windows BitLocker: metricNames `Windows Workstation: Bitlocker Status Summary [VI]`, `Windows Workstation: All Drives Encrypted` (workstation), `Windows Server: All Drives Encrypted` (server)
- macOS FileVault: metricName `macOS: File Vault Encryption Status`

**In transit:**
- TLS certificate health: `recipes/single-system-analysis/by-inspector/tls-ssl.md`
- DMARC / email encryption: `recipes/single-system-analysis/by-inspector/internet-domain-dns.md`
- VPN encryption: firewall inspector confirms encrypted VPN tunnel (e.g., SonicWall SSL-VPN metric)

---

### Data Breach — Employee Background Checks

**Coverage:** `MANUAL` — HR process attestation.

---

### Data Breach — Security Awareness Training

**Coverage:** `PARTIAL` — KnowBe4 inspector if deployed; otherwise `MANUAL`.

---

### Cyber Section — Network Security Controls

**Form:** AV, firewalls, patch management, backup/recovery procedures.

**Coverage:** `PARTIAL`

| Control | Coverage | Evidence |
|---|---|---|
| Antivirus | `LIONGARD` | `all-edrs.md`, `liongard_device` → `inspectors[]` |
| Firewalls | `LIONGARD` | Deployed firewall inspector; `domains/network.md` |
| Patch management | `LIONGARD` | `all-windows-patching.md`; `domains/endpoint.md` |
| Backup / recovery | `PARTIAL` | Backup vendor inspector; `domains/backup.md` |

---

### Cyber Section — Incident Response Plan

**Coverage:** `MANUAL` — governance documentation attestation.

---

### §3 — Technology Professional Liability (if applicable)

The Tech E&O section asks about:
- Revenue by technology service type (% breakdown)
- Largest contracts for ongoing/completed work in the last 3 years

**Coverage:** `MANUAL` throughout — financial and contractual records.

---

## Verification Log

| Item | Source | Notes |
|---|---|---|
| PLP_A0002 DOC file | `internal/cyber-insurance-forms/hiscox/PLP_A0002-HiscoxPRO-Tech-Cyber-Renewal-Application.DOC` | 437K DOC; broker portal PDFs require authentication |
| Evidence mapping | `domains/auth.md`, `domains/endpoint.md`, `domains/backup.md`, `domains/network.md`, `domains/vendor.md` | Domain files are metric source of truth |
| Form availability note | As of 2026-05-21, Hiscox broker portal PDFs are not publicly accessible. Use the DOC file above and request current forms from the Hiscox PRO team or broker portal. | |

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | Hiscox PRO Tech & Cyber Renewal maps to onboarding inventory — encryption, dual-factor auth, and patching posture are all captured at onboarding and surfaced at renewal. |
| CIS Controls (v8.1) | ✅ | Hiscox maps to: CIS 5–6 (dual-factor auth + MFA), CIS 3 (data-at-rest encryption), CIS 7 (patching), CIS 9 (email security), CIS 13 (AV/EDR), CIS 10 (backup), CIS 17 (IR plan), CIS 14 (security training). |
| Cyber-insurance domain files | ✅ | `domains/auth.md` (dual-factor auth + MFA), `domains/endpoint.md` (AV + encryption + patching), `domains/backup.md` (backup controls), `domains/governance.md` (IR + training), `domains/network.md` (email security + remote access). |
| QBR / quarterly-business-review | ✅ | Hiscox renewal form (PLP_A0002) is obtained via broker portal — request the current form at least 60 days before renewal. The QBR evidence pack generated by the domain files populates the majority of renewal questions. |

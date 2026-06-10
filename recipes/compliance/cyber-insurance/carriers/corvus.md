---
name: cyber-insurance-corvus
description: >
  Use this recipe when filling out the Corvus Smart Cyber Insurance® Application
  (Version 3.2, September 2024 / current edition). Trigger phrases: "fill out Corvus
  cyber application", "Corvus Smart Cyber renewal", "Corvus by Travelers application",
  "answer Corvus underwriting questions". Carrier-specific variant of the
  cyber-insurance-readiness master recipe. Note: Corvus is now operated by Travelers.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_metric, liongard_identity, liongard_device"
personas: [vcio-account-manager, technical-alignment-manager]
output_formats: [xlsx, word, markdown]
primitives: []
composes:
  - recipe:compliance:cyber-insurance-readiness
  - recipe:single-system:single-system-internet-domain-dns
  - recipe:single-system:single-system-network-ip-address
  - recipe:single-system:single-system-tls-ssl
  - recipe:system-type:system-type-all-edrs
  - recipe:system-type:system-type-all-external-attack-surface
---


```yaml
customize:
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed
```
# Cyber Insurance — Carrier: Corvus (by Travelers)

> **Pairs with:** `recipes/compliance/cyber-insurance/cyber-insurance-readiness.md` (master workflow)
> and the `domains/` files for full metric tables.

**Forms covered:**
- Corvus Smart Cyber Insurance® Application — Version 3.2, September 2024

**Important Corvus context:** Like Coalition, Corvus runs an automated scan of the applicant's
public internet footprint (their "Dynamic Loss Prevention" report) at quote time. After binding,
a full DLP report is generated and shared. Run `recipes/system-type-assessment/all-external-attack-surface.md`
before submitting the application — the TLS, DNS/email auth, and public-IP evidence maps directly
to Corvus's scan signals. Corvus also enrolls applicants in the **CrowBar** risk management platform.

---

## Coverage Summary

| Question | Topic | Coverage |
|---|---|---|
| Q7 — PII record count | Data scope | `MANUAL` |
| Q8 — Biometric data | Biometrics | `MANUAL` |
| Q9 — Email filtering / SEG | Email security | `PARTIAL` |
| Q10 — Backup solution, frequency, properties | Backup | `PARTIAL` |
| Q11a — MFA: ALL remote access | Remote MFA | `LIONGARD` |
| Q11b — MFA: Privileged / admin accounts | Privileged MFA | `LIONGARD` |
| Q11c — MFA: Email (webmail + all employees) | Email MFA | `LIONGARD` |
| Q11d — MFA: Critical applications | App MFA | `PARTIAL` |
| Q12 — Privileged Access Management | PAM controls | `PARTIAL` |
| Q13 — Endpoint security technology (EDR/XDR/MDR) | EDR coverage | `LIONGARD` |
| Q14 — Data protection controls | Encryption, segmentation, RBAC | `PARTIAL` |
| Q15 — BCP / DRP tested | Business continuity | `MANUAL` |
| Q16 — IDS / IPS | Network detection | `PARTIAL` |
| Q17 — Annual pen testing | Pen test | `MANUAL` |
| Q18 — Annual security training | Phishing training | `PARTIAL` |
| Q19 — Wire transfer verification | Financial fraud | `MANUAL` |
| Q20 — Licensed media | IP / content | `MANUAL` |
| Q21 — PCI compliance | Payment card | `MANUAL` |
| Q22–24 — Loss history | Prior incidents | `MANUAL` |

**DLP pre-score:** Run `all-external-attack-surface.md` before the application for TLS, DMARC,
and public-IP posture evidence.

---

## Question Mapping

### Q9 — Email Filtering / SEG

**Form:** Email filtering in place? Advanced email security including URL and attachment sandboxing?

**Coverage:** `PARTIAL`

**Evidence:**
- M365 Defender for Office 365 / EOP: M365 inspector confirms deployment and license SKU
- Google Workspace: Google Workspace inspector
- Third-party SEG (Mimecast, Proofpoint, Barracuda): not directly inspected — confirm from
  mail flow configuration or client attestation
- DMARC/SPF/DKIM: `recipes/single-system-analysis/by-inspector/internet-domain-dns.md`

---

### Q10 — Backup Solution, Frequency, and Properties

**Form:** Backup frequency (Continuous / Daily / Weekly / Monthly). Which properties apply?
(Backup servers not domain-joined / Cloud backups / Unique credentials / Multiple geographies /
Segmented / Immutable backups / Air-gapped / MFA for backup access)

**Coverage:** `PARTIAL`

**Domain reference:** `domains/backup.md`

**Evidence:**
- Backup frequency and last-run: backup vendor inspector (Datto BCDR, Acronis, Axcient, Cove, Veeam)
- Corvus asks specifically whether backup servers are **not domain-joined** — Active Directory
  inspector can confirm whether the backup server hostname is a member of the domain
- MFA for backup access: `liongard_identity COUNT privileged=true mfaStatus="NO"` (indirect signal)
- Immutability, air-gap, multiple geographies: backup vendor configuration — may be manual

**Note:** Corvus's backup property checklist is the most detailed of any carrier in this library.
Work through each property with the backup vendor admin. The backup vendor recipe surfaces what
Liongard knows; the rest requires configuration-level attestation.

---

### Q11a — MFA: ALL Remote Access

**Form:** MFA enforced to secure ALL remote access to your network?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/auth.md` — "Remote Access MFA"; `domains/network.md` — "RDP / VPN"

**Evidence:**
- VPN MFA: deployed firewall inspector metrics
- RDP exposure: `recipes/single-system-analysis/by-inspector/network-ip-address.md` — port 3389
- `liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true`

---

### Q11b — MFA: Privileged / Admin Accounts

**Form:** MFA enforced for internal use of privileged accounts (administrator, service accounts)?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/auth.md` — "Privileged Account MFA"

```
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true privileged=true
```

---

### Q11c — MFA: Email (Webmail + Non-Corporate Devices + All Employees)

**Form:** MFA enforced for email access via webmail portal, mailbox applications, and non-corporate
devices for ALL employees?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/auth.md` — "Email MFA"

```
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true
```

---

### Q11d — MFA: Critical Applications

**Form:** MFA enforced to secure access to all critical applications?

**Coverage:** `PARTIAL`

**Evidence:** Conditional Access policies (M365 / Azure AD): M365 inspector surfaces CA policy
names but not per-application coverage in detail. Full application-level MFA coverage requires
admin attestation of the CA policy scope.

---

### Q12 — Privileged Access Management

**Form:** How are privileged accounts secured? (Separate admin/non-admin accounts / Unique
local admin passwords / Password vault / Standard users without admin rights)

**Coverage:** `PARTIAL`

**Domain reference:** `domains/auth.md` — "Privileged Accounts" section

**Evidence:**
- Privileged account list: `liongard_identity LIST environmentId=<ENV_ID> privileged=true`
- Standard user local admin check: Windows inspector `LocalAdministrators` metric (per system)
- Password vault / PAM tool: `MANUAL` — not directly inspected by Liongard
- Separate admin accounts: AD inspector can surface dual accounts by naming convention — `PARTIAL`

---

### Q13 — Endpoint Security Technology

**Form:** Endpoint security in place? (MDR / Next-Gen AV / XDR / EDR — list product/vendor)

**Coverage:** `LIONGARD`

**Domain reference:** `domains/endpoint.md` — "EDR Coverage"

**Evidence:** `recipes/system-type-assessment/all-edrs.md` — returns deployed EDR/XDR/MDR
vendors, coverage rates, and product metadata. Corvus's form also asks for the specific
product/vendor name — pull from the inspector system metadata.

---

### Q14 — Data Protection Controls

**Form:** Controls to protect sensitive data? (Least privilege RBAC / MFA for sensitive systems /
Network segmentation / Logging & monitoring / Encryption at rest / Encryption in transit)

**Coverage:** `PARTIAL`

| Control | Coverage | Evidence |
|---|---|---|
| Least privilege RBAC | `PARTIAL` | AD privileged user list; manual attestation for RBAC policy |
| MFA for sensitive data access | `LIONGARD` | `liongard_identity COUNT mfaStatus="NO"` |
| Network segmentation | `PARTIAL` | Firewall VLAN/DMZ config — see deployed firewall recipe |
| Logging & monitoring | `MANUAL` | SIEM/logging platform attestation |
| Encryption at rest | `LIONGARD` | BitLocker via verified `Drives[]` JMESPath / FileVault via `metricName="macOS: File Vault Encryption Status"` |
| Encryption in transit | `PARTIAL` | TLS recipe; DMARC/SPF/DKIM recipe |

---

### Q15 — BCP / DRP Tested in Last 12 Months

**Coverage:** `MANUAL`

---

### Q16 — IDS / IPS

**Coverage:** `PARTIAL`

**Evidence:** Firewall inspectors for IPS service status (SonicWall IPS service, Fortinet IPS,
Sophos IPS). See `domains/network.md` — "IDS/IPS" section.

---

### Q17 — Annual Pen Testing

**Coverage:** `MANUAL`

---

### Q18 — Annual Security Training

**Coverage:** `PARTIAL` — KnowBe4 inspector if deployed; otherwise `MANUAL`.

---

### Q19–24 — Wire Transfer / Media / PCI / Loss History

**Coverage:** `MANUAL` throughout.

---

## DLP Pre-Score Evidence (Corvus Scan)

| Corvus scan signal | Liongard recipe |
|---|---|
| TLS certificate health | `recipes/single-system-analysis/by-inspector/tls-ssl.md` |
| DMARC / SPF / DKIM posture | `recipes/single-system-analysis/by-inspector/internet-domain-dns.md` |
| Open ports / public exposure | `recipes/single-system-analysis/by-inspector/network-ip-address.md` |
| Domain expiration | `liongard_domain LIST environmentId=<ENV_ID> maxDaysTillExpiration=30` |

---

## Verification Log

| Item | Source | Notes |
|---|---|---|
| Form Version 3.2 September 2024 | `internal/cyber-insurance-forms/corvus/corvus-smart-cyber-application-v3.2-2024.txt` | Full extraction |
| Evidence mapping | `domains/auth.md`, `domains/endpoint.md`, `domains/backup.md`, `domains/network.md` | Domain files are metric source of truth |
| Corvus DLP scan context | Corvus product documentation | Automated internet scanning is core to the Corvus model |

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | Corvus combines attestation with automated scanning — onboarding inventory populates the attestation questions; Step 0 internet footprint sweep pre-aligns with Corvus scan. |
| CIS Controls (v8.1) | ✅ | Corvus maps to: CIS 5–6 (Q11a–11d MFA matrix + Q12 PAM), CIS 13 (Q13 EDR), CIS 10 (Q16–17 backup + RTO), CIS 7 (Q14–15 patching), CIS 12 (Q18 network segmentation), CIS 9 (Q9–10 email security), CIS 17 (Q20 IR), CIS 14 (Q19 training). |
| Cyber-insurance domain files | ✅ | `domains/auth.md` (Q11a–11d + Q12 PAM), `domains/endpoint.md` (Q13–15 EDR + patching), `domains/backup.md` (Q16–17 backup + immutability), `domains/network.md` (Q18 segmentation), `domains/governance.md` (Q19–21 training + IR + BCP), `domains/vendor.md` (Q22 vendor controls). |
| QBR / quarterly-business-review | ✅ | Corvus (now Corvus by Travelers) automated scan runs at quote time — run Step 0 internet footprint sweep at least 30 days before renewal so TLS, DMARC, and open-port posture matches what Corvus will observe. |

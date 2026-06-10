---
name: cyber-insurance-hartford
description: >
  Use this recipe when filling out The Hartford CyberChoice Premier Application
  (CB 00 H027 02 0323) for lower-revenue accounts or the CyberChoice Underwriting
  Application (CB 00 H027 03 0824) for accounts with revenue of $10M or more.
  Trigger phrases: "fill out Hartford cyber application", "Hartford CyberChoice renewal",
  "Hartford cyber underwriting form", "answer Hartford underwriting questions".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_metric, liongard_identity, liongard_device"
personas: [vcio-account-manager, technical-alignment-manager]
output_formats: [xlsx, word, markdown]
primitives: []
composes:
  - recipe:compliance:cyber-insurance-readiness
  - recipe:single-system:single-system-network-ip-address
  - recipe:system-type:system-type-all-edrs
  - recipe:system-type:system-type-windows-patching
---


```yaml
customize:
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed
```
# Cyber Insurance — Carrier: The Hartford

> **Pairs with:** `recipes/compliance/cyber-insurance/cyber-insurance-readiness.md` (master workflow)
> and the `domains/` files for full metric tables.

**Forms covered:**
- CyberChoice Premier Application (CB 00 H027 02 0323) — lower-revenue accounts
- CyberChoice Underwriting Application (CB 00 H027 03 0824 / 2025 edition) — accounts with $10M+ revenue

**Form selection:** Use the Premier form for accounts under ~$10M revenue; use the Underwriting form
for $10M+ accounts. The Underwriting form has dedicated sections for cybersecurity team structure,
data inventory, EDR/MDR, SEG, and funds transfer controls.

---

## Coverage Summary — Premier Application (CB 00 H027 02 0323)

The Premier form is brief — it maps to Hartford's Sections 3–4:

| Question | Coverage | Notes |
|---|---|---|
| 4e — NPI record count | `MANUAL` | Data inventory attestation |
| 4f — Backups (regular + offline + isolated) | `PARTIAL` | Backup inspector confirms frequency; isolation is config/manual |
| 4g — System update / patch cadence | `LIONGARD` | Patching recipe |
| 4h — Firewalls, AV, authentication | `LIONGARD` | Firewall + EDR inspector coverage |
| 4i — Encryption on departing devices/laptops/mobile | `LIONGARD` | BitLocker / FileVault metrics |
| Media (4j–4l) | `MANUAL` | Content policy attestation |

---

## Coverage Summary — Underwriting Application (CB 00 H027 03 0824)

| Section | Key Questions | Coverage |
|---|---|---|
| 4 — Cybersecurity Function | Dedicated team, in-house vs. outsourced, CISO contact | `PARTIAL` — RMM inspector presence signals managed model; team size is manual |
| 6 — Data Inventory | NPI record count, encryption at rest/transit/mobile | `PARTIAL` — encryption confirmed by Liongard; record count is manual |
| 6 — Backups | Regular backups, offline isolation, recovery testing | `PARTIAL` |
| 6 — BCP/IR Plan | Plan in place and tested | `MANUAL` |
| 7 — MFA (remote access) | MFA required for ALL remote access | `LIONGARD` |
| 7 — MFA (email) | MFA required for email access | `LIONGARD` |
| 7 — Funds transfer controls | Dual authentication for wire transfers | `MANUAL` |
| 7 — Endpoint protection | AV on computers/networks/mobile, EDR/MDR product | `LIONGARD` |
| 7 — Email security | SEG, attachment scanning, link screening, external tagging | `PARTIAL` |
| 7 — Anti-phishing training | Training frequency | `PARTIAL` — KnowBe4 if deployed |
| 8 — Loss history | Prior cyber incidents | `MANUAL` |

---

## Question Mapping

### 4f / Underwriting §6 — Backups

**Form (Premier):** Does the Applicant back up mission-critical data regularly, routinely store recent backups off-line, and are backups well isolated from threats?

**Form (Underwriting):** Is critical data regularly backed up? Are backups stored offline / isolated? How often is recovery tested?

**Coverage:** `PARTIAL`

**Domain reference:** `domains/backup.md`

**Evidence:** Use the deployed backup vendor single-system recipe (Datto BCDR, Acronis, Axcient,
Cove, or Veeam) to confirm job frequency and last-run date. Offline isolation and recovery testing
are configuration/process attestations.

---

### 4g — System Security Updates / Patching

**Coverage:** `LIONGARD`

**Domain reference:** `domains/endpoint.md` — "Patch Management"

**Evidence:** `recipes/system-type-assessment/all-windows-patching.md`. For macOS and Linux,
run the respective single-system recipes.

**Answer guidance:** Map patch cadence to Hartford's tiers: "Immediately / Weekly / Monthly /
Yearly / Not at all". If the majority of endpoints patch monthly, select Monthly and note the
exceptions.

---

### 4h — Firewalls, AV, Passwords / Authentication

**Coverage:** `LIONGARD`

| Sub-control | Domain reference | Evidence |
|---|---|---|
| Firewalls | `domains/network.md` | Deployed firewall inspector (SonicWall, Fortinet, etc.) |
| Antivirus / AV | `domains/endpoint.md` | `liongard_device` → `inspectors[]` for AV/EDR coverage |
| Passwords / Authentication | `domains/auth.md` | `liongard_identity COUNT mfaStatus="NO"` |

---

### 4i — Encryption of Departing Devices

**Form:** Does the Applicant encrypt all electronic information that leaves its physical control
(laptops, mobile devices, storage) using strong encryption?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/endpoint.md` — "Encryption at Rest"

**Evidence:**
- Windows laptops: BitLocker metricNames `Windows Workstation: Bitlocker Status Summary [VI]`, `Windows Workstation: All Drives Encrypted`
- macOS: FileVault metricName `macOS: File Vault Encryption Status`
- Mobile devices: not directly inspected — confirm MDM status if applicable

---

### Underwriting §7 — MFA (Remote Access)

**Form:** Is MFA required for ALL remote access to the network (cloud-hosted, on-premises, VPN)?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/auth.md` — "Remote Access MFA"; `domains/network.md` — "RDP"

**Evidence:**
- VPN MFA: deployed firewall inspector metrics
- RDP exposure: `recipes/single-system-analysis/by-inspector/network-ip-address.md`
- Identity-level: `liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true`

---

### Underwriting §7 — MFA (Email)

**Coverage:** `LIONGARD`

**Domain reference:** `domains/auth.md` — "Email MFA"

```
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true
```

---

### Underwriting §7 — Endpoint Protection (AV / EDR / MDR)

**Form:** Antimalware/AV running on computers, networks, mobile? EDR/MDR product in place?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/endpoint.md` — "EDR Coverage"

**Evidence:** `recipes/system-type-assessment/all-edrs.md` → EDR vendor, deployment rate on
servers and workstations. Hartford specifically asks for the product name — pull from the EDR
inspector system metadata.

---

### Underwriting §7 — Email Security (SEG)

**Form:** SEG in place, attachment scanning, link screening, external sender tagging?

**Coverage:** `PARTIAL`

**Evidence:**
- M365 Defender for Office 365 / EOP: M365 inspector confirms deployment and configuration
- Google Workspace security features: Google Workspace inspector
- Third-party SEG (Mimecast, Proofpoint, etc.): not directly inspected — confirm from M365 mail
  flow rules or client attestation
- External email tagging: M365 Exchange transport rule — partially visible via M365 inspector

---

### Underwriting §7 — Funds Transfer Controls

**Coverage:** `MANUAL` — finance / process attestation.

---

## Verification Log

| Item | Source | Notes |
|---|---|---|
| Premier form question set | `internal/cyber-insurance-forms/hartford/hartford-cyberchoice-premier-application-2023.txt` | Extracted |
| Underwriting form question set | `internal/cyber-insurance-forms/hartford/hartford-cyberchoice-underwriting-application-2025.txt` | Extracted |
| Evidence mapping | `domains/auth.md`, `domains/endpoint.md`, `domains/backup.md`, `domains/network.md` | Domain files are metric source of truth |

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | Hartford CyberChoice draws on endpoint, identity, and backup inventory from onboarding. The Underwriting supplement (CB 00 H027 03 0824) requires specific product names — confirm AV, SEG, and EDR product names from inspector data at onboarding. |
| CIS Controls (v8.1) | ✅ | Hartford Premier maps to: CIS 5–6 (Q4h auth + Q7 MFA), CIS 13 (Q4h AV + Q4i EDR), CIS 10 (Q4f backup), CIS 7 (Q4g patching), CIS 3 (Q4i encryption). Underwriting §7 adds PAM and MFA attestation. |
| Cyber-insurance domain files | ✅ | `domains/auth.md` (Q4h auth + §7 MFA + PAM), `domains/endpoint.md` (Q4g patching + Q4h AV + Q4i EDR + encryption), `domains/backup.md` (Q4f backup controls), `domains/governance.md` (Q4j IR + Q4k training), `domains/network.md` (Q4d–4e network controls). |
| QBR / quarterly-business-review | ✅ | Hartford requires both Premier and Underwriting supplements — run this recipe at the QBR closest to renewal, then complete the manual sections with the client's IT contact who can confirm product names and incident history. |

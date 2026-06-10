---
name: cyber-insurance-aig
description: >
  Use this recipe when filling out the AIG CyberEdge Cyber Insurance Application
  (form 149053, Ed. 08/23) for applicants with annual revenues of $50M or less.
  Trigger phrases: "fill out AIG cyber application", "AIG CyberEdge renewal",
  "AIG cyber application", "answer AIG underwriting questions". Carrier-specific
  variant of the cyber-insurance-readiness master recipe.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_metric, liongard_identity, liongard_device"
personas: [vcio-account-manager, technical-alignment-manager, soc]
output_formats: [xlsx, word, markdown]
primitives: []
composes:
  - recipe:compliance:cyber-insurance-readiness
  - recipe:single-system:single-system-active-directory
  - recipe:single-system:single-system-dark-web-monitoring
  - recipe:single-system:single-system-network-ip-address
  - recipe:system-type:system-type-all-edrs
---


```yaml
customize:
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed
```
# Cyber Insurance — Carrier: AIG (CyberEdge)

> **Pairs with:** `recipes/compliance/cyber-insurance/cyber-insurance-readiness.md` (master workflow)
> and the `domains/` files for full metric tables.

**Forms covered:**
- AIG CyberEdge Cyber Insurance Application — 149053 (Ed. 08/23), for annual revenue ≤$50M

**Revenue tier note:** A different application (not covered here) is required for revenue >$50M.
AIG uses the Cygnvs platform to provision access — the named contact in Q6 will receive an invite.

**AIG trigger questions** (additional info required if any are Yes):
- PII + PCI + PHI combined >1M records
- Operations in: Adult Entertainment, Airlines, Aviation, Cannabis, Credit Bureau, Cryptocurrency,
  Data Business Risks, Financial Institutions, Hospitals/Healthcare, Law Firms, MSPs, MSSPs,
  Music/Movie/TV production, Payment Processors, Public Entities, Schools, Social Networking
- More than 300 employees
- Prior claim/incident in last 5 years exceeding $50K

**Note for MSPs:** AIG flags MSPs as a trigger industry. If the client is an MSP, be prepared
for a supplemental questionnaire. Liongard's own data can demonstrate the MSP's security maturity
to the underwriter.

---

## Coverage Summary

| Question | Topic | Coverage |
|---|---|---|
| Q1 — Industry vertical | Industry classification | `MANUAL` |
| Q2–4 — Revenue, foreign revenue, employees | Firmographics | `MANUAL` |
| Q5 — Record types and volumes | PII/PHI/PCI/biometric | `MANUAL` |
| Q6 — CISO / security contact | Security leadership | `MANUAL` |
| Q7–9 — Domains and IP addresses | Internet presence | `PARTIAL` |
| Q10 — Email from other domains | Email domains | `PARTIAL` |
| Q11 — Active Directory (ADDS) usage | AD deployment | `LIONGARD` |
| Q12 — Exchange / Exchange Online | Email platform | `LIONGARD` |
| Q13 — Unsupported software | EOL/EOS software | `PARTIAL` |
| Q14 — Default and compromised passwords changed | Password hygiene | `PARTIAL` |
| Q15a — MFA: ALL remote access | Remote MFA | `LIONGARD` |
| Q15b — MFA: ALL admin access | Admin MFA | `LIONGARD` |
| Q16 — Endpoint encryption (BitLocker/FileVault) | Disk encryption | `LIONGARD` |
| Q17 — IT asset inventory within last year | Asset inventory | `LIONGARD` |
| Q18 — IT management model (in-house vs. MSP) | IT structure | `PARTIAL` |
| Q19 — EDR tool | EDR deployment | `LIONGARD` |
| Q20 — DPO / CPO | Privacy leadership | `MANUAL` |
| Q21 — Security awareness training | Training | `PARTIAL` |
| Q22 — External email tagging | Email controls | `PARTIAL` |
| Q23 — Third-party service providers | Vendor taxonomy | `PARTIAL` |
| Warranty — Prior incidents (5 years) | Loss history | `MANUAL` |

---

## Question Mapping

### Q7–9 — Domains and IP Addresses

**Form:** Primary web domain; other web domains; IP addresses (including ISP-leased).

**Coverage:** `PARTIAL`

**Evidence:**
- `liongard_domain LIST environmentId=<ENV_ID>` → domain inventory with DNS/TLS posture
- Internet Domain / DNS inspector: confirmed domains and IP assignments
- `recipes/single-system-analysis/by-inspector/network-ip-address.md` — public IP inventory

---

### Q11 — Active Directory (ADDS) Usage

**Form:** Does the Applicant utilize Microsoft Active Directory Domain Services (on-prem or hosted)?

**Coverage:** `LIONGARD`

**Evidence:** Active Directory inspector presence in `liongard_launchpoint LIST` confirms ADDS
deployment. If present, run `recipes/single-system-analysis/by-inspector/active-directory.md`.

**Answer guidance:** Answer Yes if an Active Directory inspector is deployed. Note whether
it's on-premises or hybrid. AIG explicitly excludes Azure AD from this question (Azure AD
without on-prem ADDS = answer No).

---

### Q12 — Exchange / Exchange Online

**Form:** Does the Applicant utilize Microsoft Exchange (including hybrid)?

**Coverage:** `LIONGARD`

**Evidence:** M365 inspector or a dedicated Exchange inspector in `liongard_launchpoint LIST`
confirms Exchange Online deployment. On-premises Exchange may appear in Windows Server
services — check via Windows Server single-system recipe.

---

### Q13 — Unsupported Software

**Form:** Does the Applicant utilize any unsupported software (vendor no longer providing security fixes)?

**Coverage:** `PARTIAL`

**Domain reference:** `domains/endpoint.md` — "OS End of Life" section

**Evidence:**
- Windows OS EOL: Windows Server and Workstation inspector OS version metrics
- macOS support status: macOS inspector
- Third-party application EOL: not directly inspected — requires software inventory attestation

**Note:** Use string-based OS filters (not `OperatingSystemVersionNum < 6.2` which misses
Windows 10) per `learnings.md` — confirmed bug. Correct pattern:
`contains(OperatingSystem, 'Windows 7')`, `contains(OperatingSystem, 'Windows XP')`.

---

### Q14 — Default and Compromised Passwords Changed

**Form:** Has the Applicant changed all default passwords and any known-to-be-compromised passwords?

**Coverage:** `PARTIAL`

**Evidence:**
- AD domain default admin account status: Active Directory inspector
- Dark web credential exposure: `recipes/single-system-analysis/by-inspector/dark-web-monitoring.md`
  — surfaces known-compromised credentials from breach data
- Default vendor passwords on network devices: firewall inspector default credential checks

---

### Q15a — MFA: ALL Remote Access

**Form:** Do the Applicant and third-party vendors enforce MFA for ALL remote access to systems?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/auth.md` — "Remote Access MFA"; `domains/network.md` — "VPN / RDP"

```
# All enabled identities without MFA (includes vendor access accounts if in AD/M365)
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true

# Open RDP exposure (critical — AIG treats this as a hard underwriting signal)
# See: recipes/single-system-analysis/by-inspector/network-ip-address.md
```

---

### Q15b — MFA: ALL Admin Access

**Form:** Do the Applicant and third-party vendors enforce MFA for ALL admin access?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/auth.md` — "Privileged Account MFA"

```
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true privileged=true
```

---

### Q16 — Endpoint Encryption

**Form:** Does the Applicant encrypt data on end-user devices to safeguard against lost devices?
(BitLocker, FileVault, dm-crypt)

**Coverage:** `LIONGARD`

**Domain reference:** `domains/endpoint.md` — "Encryption at Rest"

| Platform | Evidence | Verified JMESPath |
|---|---|---|
| Windows Workstation — BitLocker | Direct `liongard_metric EVALUATE` against the Windows Workstation dataprint | ``length(Drives[?Type == `Fixed` && BitlockerStatus == `Fully Encrypted`]) == length(Drives[?Type == `Fixed`])``; summary: `Drives[].{DriveName: DriveName, Type: Type, BitlockerStatus: BitlockerStatus}` |
| Windows Server — BitLocker | Direct `liongard_metric EVALUATE` against the Windows Server dataprint | ``length(Drives[?Type == `Fixed` && BitlockerStatus == `Fully Encrypted`]) == length(Drives[?Type == `Fixed`])``; summary: `Drives[].{DriveName: DriveName, Type: Type, BitlockerStatus: BitlockerStatus}` |
| macOS — FileVault | `metricName="macOS: File Vault Encryption Status"` | `Overview.FileVaultEncryption` |
| Linux — dm-crypt / LUKS | Per-system `liongard_metric EVALUATE` | Check Linux inspector for disk encryption config |

---

### Q17 — IT Asset Inventory Within Last Year

**Form:** Has the Applicant conducted an inventory of all IT assets within the last year?

**Coverage:** `LIONGARD`

**Evidence:**
- `liongard_device LIST environmentId=<ENV_ID>` → full device inventory
- `liongard_identity LIST environmentId=<ENV_ID>` → full identity inventory
- `liongard_timeline environmentId=<ENV_ID>` → most recent inspection date per system

**Answer guidance:** If Liongard is actively deployed and inspections ran within the last year,
answer Yes — Liongard is the asset inventory. Note the most recent inspection date and any
systems with stale data.

---

### Q18 — IT Management Model

**Form:** How is IT managed — IT employees vs. outsourced MSP? (If outsourced: provider name)

**Coverage:** `PARTIAL`

**Evidence:** RMM inspector presence in `liongard_launchpoint LIST` signals an MSP-managed
environment (NinjaOne, Datto RMM, ConnectWise Automate, etc.). The MSP provider name is in
the RMM inspector system metadata.

---

### Q19 — EDR Tool

**Form:** Does Applicant utilize an EDR tool? If Yes: company, software, and specific SKUs.

**Coverage:** `LIONGARD`

**Domain reference:** `domains/endpoint.md` — "EDR Coverage"

**Evidence:** `recipes/system-type-assessment/all-edrs.md` — deployed EDR vendor, product name,
coverage rate, and inspector metadata. Pull specific SKU from the inspector system name or
configuration fields.

---

### Q21 — Security Awareness Training

**Coverage:** `PARTIAL` — KnowBe4 inspector if deployed; otherwise `MANUAL`.

---

### Q22 — External Email Tagging

**Form:** Does the Applicant "tag" or otherwise mark emails from outside the organization?

**Coverage:** `PARTIAL`

**Evidence:** M365 inspector — Exchange transport rule or Defender anti-spam policy may
confirm external tagging. If not visible: confirm from M365 admin attestation.

---

### Q23 — Third-Party Service Providers

**Form:** Third-party providers for: Hosting / Email / CRM / HR / E-Commerce & Payments /
Security / Industrial Control

**Coverage:** `PARTIAL`

**Evidence:**
- Cloud inspector presence (AWS, Azure, Cloudflare): confirms hosting providers
- M365 / Google Workspace: confirms email platform
- RMM inspector: confirms IT/security provider
- Security providers (EDR, SIEM): confirmed via EDR inspector
- Other vendors (CRM, HR, E-Commerce): `MANUAL` — not inspected by Liongard

---

## Verification Log

| Item | Source | Notes |
|---|---|---|
| Form 149053 Ed. 08/23 | `internal/cyber-insurance-forms/aig/aig-cyber-insurance-application-2023.txt` | Full extraction, ≤$50M revenue form |
| Broker guidance | `internal/cyber-insurance-forms/aig/aig-cyber-application-broker-guidance.txt` | SAR/ESR context, CyberMatics |
| Evidence mapping | `domains/auth.md`, `domains/endpoint.md`, `domains/network.md`, `domains/vendor.md` | Domain files are metric source of truth |
| EOL OS note | `learnings.md` — 2026-05-21 AD bug entry | Use string-based OS filter, not VersionNum |

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | AIG CyberEdge pulls significantly from onboarding inventory: AD/identity count, device count, EDR deployment, and backup architecture are all captured at onboarding intake. |
| CIS Controls (v8.1) | ✅ | AIG maps to: CIS 1–2 (Q17 asset inventory), CIS 5–6 (Q8–9 MFA + PAM), CIS 13 (Q19 EDR), CIS 10 (Q18 backup), CIS 7 (Q20 patching), CIS 9 (Q21–22 email security), CIS 3 (Q24 encryption), CIS 17 (Q27 IR), CIS 14 (Q28 training), CIS 15 (Q29–30 vendor). |
| Cyber-insurance domain files | ✅ | `domains/auth.md` (Q8–9 MFA + PAM), `domains/endpoint.md` (Q19–20 EDR + patching + encryption), `domains/backup.md` (Q18 backup + immutability), `domains/network.md` (Q23 network controls), `domains/governance.md` (Q27–30 IR + training + vendor), `domains/regulatory.md` (Q31–32 HIPAA/PCI). |
| QBR / quarterly-business-review | ✅ | AIG flags MSP clients as a higher-risk industry — prepare for more detailed underwriting questions at each renewal. AIG Q17 (asset inventory) is uniquely answerable via Liongard: the QBR should include a Liongard inventory attestation note per `cyber-insurance-readiness.md` Step 2. |

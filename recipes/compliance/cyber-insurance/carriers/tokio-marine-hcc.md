---
name: cyber-insurance-tokio-marine-hcc
description: >
  Use this recipe when filling out the Tokio Marine HCC NetGuard® Plus Cyber Liability
  Insurance Application (NGP-NBA, Ed. 10.2020 or current). Trigger phrases: "fill out
  Tokio Marine cyber application", "Tokio Marine HCC NetGuard renewal", "TMHCC cyber
  application", "answer Tokio Marine underwriting questions", "NetGuard Plus application".
  Carrier-specific variant of the cyber-insurance-readiness master recipe.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_metric, liongard_identity, liongard_device"
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
# Cyber Insurance — Carrier: Tokio Marine HCC (NetGuard® Plus)

> **Pairs with:** `recipes/compliance/cyber-insurance/cyber-insurance-readiness.md` (master workflow)
> and the `domains/` files for full metric tables.

**Forms covered:**
- Tokio Marine HCC NetGuard® Plus Cyber Liability Insurance Application — NGP-NBA (10.2020)

**Important TMHCC context:** The NetGuard® Plus form has an unusually detailed **Ransomware
Controls** section (§6) with specific questions about RDP, IP whitelisting, admin account
MFA, email filtering, and backup isolation. This maps closely to Liongard's evidence set.
Run `recipes/single-system-analysis/by-inspector/network-ip-address.md` and the Active Directory
recipe before submitting — they directly address §6.

---

## Coverage Summary

| Section | Key Questions | Coverage |
|---|---|---|
| §1 — General Information | Name, address, contact | `MANUAL` |
| §2 — Form of Business | Corp structure, employees, subsidiaries | `MANUAL` |
| §3 — Revenues | Annual revenue tiers | `MANUAL` |
| §4a — Record types and counts | PII/PHI/PCI/biometric | `MANUAL` |
| §5a — AV / firewall | Endpoint + network protection | `LIONGARD` |
| §5b — Cloud provider usage | Cloud deployment | `PARTIAL` |
| §5c — Cloud MFA | Cloud MFA (AWS/Azure/GCP) | `PARTIAL` |
| §5d — Data encryption | Encryption at rest + compensating controls | `LIONGARD` |
| §5e — PCI DSS compliance | Payment card | `MANUAL` |
| §6a — Remote access existence + MFA | VPN / remote MFA | `LIONGARD` |
| §6a(2) — IP whitelisting | Remote access controls | `PARTIAL` |
| §6b — RDP disabled or MFA-protected | RDP exposure | `LIONGARD` |
| §6c — Admin account MFA | Privileged account MFA | `LIONGARD` |
| §6d — Email account remote access MFA | Email MFA | `LIONGARD` |
| §6e — EDR / NGAV | Endpoint detection | `LIONGARD` |
| §6f — Email filtering beyond native | SEG / phishing filter | `PARTIAL` |
| §6g — Backup solution + properties | Backup controls | `PARTIAL` |
| §7a — Phishing / social engineering training | Security awareness | `PARTIAL` |
| §7b — Wire transfer controls | Financial fraud | `MANUAL` |
| §8 — Loss history | Prior incidents | `MANUAL` |

---

## Question Mapping

### §5a — Antivirus and Firewall

**Form:** Do you use anti-virus software and a firewall to protect your network?

**Coverage:** `LIONGARD`

| Sub-control | Domain reference | Evidence |
|---|---|---|
| Antivirus / endpoint protection | `domains/endpoint.md` | `liongard_device` → `inspectors[]` for AV/EDR; `all-edrs.md` |
| Firewall | `domains/network.md` | Firewall inspector presence; deployed firewall recipe |

---

### §5c — Cloud MFA (AWS / Azure / GCP)

**Form:** Do you use 2-factor authentication to secure all cloud provider services?

**Coverage:** `PARTIAL`

**Evidence:**
- Azure AD / Entra ID: M365 inspector surfaces MFA status for cloud identities
- AWS/GCP: not directly inspected unless AWS or Azure inspector is deployed
- `liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true` covers cloud
  identities that Liongard has indexed (M365, Google Workspace, etc.)

---

### §5d — Data Encryption at Rest + Compensating Controls

**Form:** Do you encrypt all sensitive and confidential information on your systems and networks?
If No, are these compensating controls in place: server segregation / role-based access control?

**Coverage:** `LIONGARD` (disk encryption); `PARTIAL` (compensating controls)

**Domain reference:** `domains/endpoint.md` — "Encryption at Rest"

| Platform | Evidence |
|---|---|
| Windows Workstation BitLocker | Direct `liongard_metric EVALUATE`: ``length(Drives[?Type == `Fixed` && BitlockerStatus == `Fully Encrypted`]) == length(Drives[?Type == `Fixed`])``; summary path `Drives[].{DriveName: DriveName, Type: Type, BitlockerStatus: BitlockerStatus}` |
| Windows Server BitLocker | Direct `liongard_metric EVALUATE`: ``length(Drives[?Type == `Fixed` && BitlockerStatus == `Fully Encrypted`]) == length(Drives[?Type == `Fixed`])``; summary path `Drives[].{DriveName: DriveName, Type: Type, BitlockerStatus: BitlockerStatus}` |
| macOS FileVault | `metricName="macOS: File Vault Encryption Status"`; JMESPath `Overview.FileVaultEncryption` |
| Server segmentation (compensating control) | Firewall inspector VLAN/DMZ config — `PARTIAL` |
| RBAC (compensating control) | AD privileged user list — `PARTIAL` |

---

### §6a — Remote Access Existence and MFA

**Form:** Do you allow remote access? If Yes: (1) Is ALL remote access MFA-protected?
(2) Is IP whitelisting in place?

**Coverage:**
- Remote access existence: `LIONGARD`
- MFA on all remote access: `LIONGARD`
- IP whitelisting: `PARTIAL`

**Domain reference:** `domains/auth.md` — "Remote Access MFA"; `domains/network.md` — "VPN"

**Evidence:**
- VPN MFA: deployed firewall inspector (SonicWall RADIUS [metric 200006 not in global catalog], Fortinet, Sophos)
- IP whitelisting: firewall inspector access policies — partially visible, manual confirmation

---

### §6b — RDP Disabled or MFA-Protected

**Form:** Have you disabled RDP and/or RDG on all endpoints and servers? If No, is RDP
protected by two-factor authentication?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/network.md` — "RDP Exposure"

**Evidence:**
- External RDP port exposure: `recipes/single-system-analysis/by-inspector/network-ip-address.md`
  — confirms whether port 3389 is open to the internet
- Windows Server RDP setting: Windows Server inspector firewall / services metrics
- Windows Workstation RDP: Windows Workstation inspector

**Answer guidance:** TMHCC's preference is "disabled". If RDP is enabled, MFA protection is
the acceptable alternative. Any internet-facing open RDP without MFA is a hard risk signal —
flag it explicitly.

---

### §6c — Domain / Network Administrator Account MFA

**Form:** Do you use 2-factor authentication to secure all domain or network administrator accounts?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/auth.md` — "Privileged Account MFA"

```
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true privileged=true
```

Also check Active Directory inspector for domain admin group membership:
`recipes/single-system-analysis/by-inspector/active-directory.md`

---

### §6d — Email Account Remote Access MFA

**Form:** Do you use 2-factor authentication to secure remote access to email accounts?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/auth.md` — "Email MFA"

```
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true
```

---

### §6e — EDR / NGAV

**Form:** Do you use EDR or Next-Generation Antivirus software to secure all endpoints?
If Yes: list provider.

**Coverage:** `LIONGARD`

**Domain reference:** `domains/endpoint.md` — "EDR Coverage"

**Evidence:** `recipes/system-type-assessment/all-edrs.md` — deployed EDR/NGAV vendor, product
name, and coverage rate (servers + workstations). Pull provider name from inspector metadata.

---

### §6f — Email Filtering Beyond Native Provider

**Form:** Do you use an email filtering solution to prevent phishing or ransomware attacks
in addition to any filtering provided by your email provider? If Yes: provider name.

**Coverage:** `PARTIAL`

**Evidence:**
- M365 Defender for Office 365 add-on: M365 inspector confirms whether this is licensed
  beyond the native EOP (Exchange Online Protection)
- Third-party SEG (Mimecast, Proofpoint, Barracuda, Ironscales): not directly inspected
- DMARC/SPF/DKIM email authentication: `domains/auth.md` and internet-domain recipe

---

### §6g — Backup Solution and Properties

**Form:** Backup solution for all critical data? Frequency (Daily / Weekly / Monthly).
Type (Local / Network drive / Tape / Off-site / Cloud). Provider name. Properties:
(a) Physically disconnected from network? (b) Segmented with 2FA access? Recovery time estimate.

**Coverage:** `PARTIAL`

**Domain reference:** `domains/backup.md`

**Evidence:**
- Backup vendor inspector (Datto BCDR, Acronis, Axcient, Cove, Veeam): confirms solution
  type, frequency, last-run date, and provider name
- Physical disconnection and 2FA access: backup configuration — may be manual
- Recovery time estimate: backup vendor SLA documentation — `MANUAL`

---

### §7a — Phishing / Social Engineering Training

**Form:** Do employees with financial / accounting responsibilities complete social engineering
training? Do other employees? Does training include phishing simulation?

**Coverage:** `PARTIAL`

**Evidence:** KnowBe4 inspector if deployed (`recipes/single-system-analysis/by-inspector/knowbe4.md`)
surfaces campaign completion rates and simulation results. Otherwise `MANUAL`.

---

### §7b / §8 — Wire Transfer Controls / Loss History

**Coverage:** `MANUAL` throughout.

---

## Verification Log

| Item | Source | Notes |
|---|---|---|
| NGP-NBA (10.2020) | `internal/cyber-insurance-forms/tokio-marine-hcc/netguard-plus-cyber-application-2020.txt` | Full extraction |
| Evidence mapping | `domains/auth.md`, `domains/endpoint.md`, `domains/backup.md`, `domains/network.md` | Domain files are metric source of truth |

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | TMHCC NetGuard Plus ransomware controls section (§6) maps directly to onboarding inventory — VPN MFA, RDP exposure, email MFA, and EDR are all captured at onboarding. |
| CIS Controls (v8.1) | ✅ | TMHCC maps to: CIS 5–6 (§3 MFA + §6a VPN MFA + §6c–6d admin/email MFA), CIS 13 (§6e EDR/NGAV), CIS 12 (§6b RDP disabled + network controls), CIS 10 (§4 backup), CIS 7 (§5 patching), CIS 17 (§7 IR), CIS 14 (§8 training). |
| Cyber-insurance domain files | ✅ | `domains/auth.md` (§3 + §6a/6c/6d MFA tiers), `domains/endpoint.md` (§5 patching + §6e EDR), `domains/backup.md` (§4 backup + immutability), `domains/network.md` (§6b RDP + VPN + network controls), `domains/governance.md` (§7–8 IR + training), `domains/vendor.md` (§9 vendor controls). |
| QBR / quarterly-business-review | ✅ | TMHCC NetGuard Plus is a straightforward form — the ransomware controls section (§6) is the underwriter focus. Run the QBR at renewal using this recipe to produce a clean §6 evidence pack; §6b (RDP disabled) Liongard mapping provides the strongest single-item differentiation. |

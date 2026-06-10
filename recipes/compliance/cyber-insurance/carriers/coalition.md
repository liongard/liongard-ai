---
name: cyber-insurance-coalition
description: >
  Use this recipe when filling out the Coalition Cyber and Technology E&O Policy
  Application (form SP 17 717 1120 or the current Active Cyber Policy equivalent).
  Trigger phrases: "fill out Coalition cyber application", "Coalition cyber renewal",
  "answer Coalition underwriting questions", "Coalition Active Cyber form".
  Carrier-specific variant of the cyber-insurance-readiness master recipe, mapping
  each Coalition question to the corresponding Liongard evidence patterns.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_metric, liongard_identity, liongard_device, liongard_domain"
personas: [vcio-account-manager, technical-alignment-manager]
output_formats: [xlsx, word, markdown]
primitives: []
composes:
  - recipe:compliance:cyber-insurance-readiness
  - recipe:single-system:single-system-dark-web-monitoring
  - recipe:single-system:single-system-internet-domain-dns
  - recipe:single-system:single-system-network-ip-address
  - recipe:single-system:single-system-tls-ssl
  - recipe:system-type:system-type-all-external-attack-surface
---


```yaml
customize:
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed
```
# Cyber Insurance — Carrier: Coalition

> **Pairs with:** `recipes/compliance/cyber-insurance/cyber-insurance-readiness.md` (master workflow,
> customization block, asset-inventory schema) and the seven `domains/` files for full metric tables.
> This file maps each Coalition question number to coverage status and the relevant domain reference.

**Forms covered:**
- Coalition Cyber and Technology E&O Policy Application — SP 17 717 1120 (2024 edition)
- Current "Active Cyber Policy" application (2025 Active Cyber Policy form, US non-admitted)

**Important Coalition context:** Coalition uses automated scanning of the applicant's public
internet footprint to pre-score the application. Before or after submitting the form, run
`recipes/system-type-assessment/all-external-attack-surface.md` — the TLS/SSL, internet domain/DNS,
and public-IP posture evidence it surfaces aligns directly with what Coalition's scan checks.

---

## How to run

1. Run the master recipe's Steps 1–3 (`liongard_environment` → asset inventory → inspection timeline).
2. For each section below, call out the coverage status and pull the referenced domain evidence.
3. Items marked `MANUAL` require written attestation from the client — Liongard cannot answer them.
4. Populate the deliverable format from the master recipe's customization block.

---

## Coverage Summary

| Category | Liongard Coverage |
|---|---|
| Q1 — Prior cyber incidents | `MANUAL` — loss history only |
| Q2 — Prior circumstances | `MANUAL` — attestation only |
| Q3 — Encryption on laptops/desktops/portable media | `LIONGARD` — BitLocker / FileVault metrics |
| Q4 — PCI / PII / PHI scope | `PARTIAL` — record-type classification is manual; asset inventory supports user/device scope |
| Q5 — Weekly offline or cloud backups | `PARTIAL` — backup recency from backup inspectors; isolation is manual |
| Q6a — Email MFA | `LIONGARD` — identity MFA status |
| Q6b — VPN / RDP / remote access MFA | `LIONGARD` — auth domain metrics + RDP exposure |
| Q6c — Network / cloud admin MFA | `LIONGARD` — privileged identity MFA status |
| Q7 — Wire transfer secondary verification | `MANUAL` — process / policy control |
| Q8 — Content complaints | `MANUAL` — legal / claims history |
| Q9 — IP / content removal procedures | `MANUAL` — policy attestation |
| Q10–11 — Concurrent E&O policy | `MANUAL` — insurance placement records |

**Internet-footprint pre-score (Coalition-unique):** Run `all-external-attack-surface.md` for
TLS certificate health, DMARC/SPF/DKIM posture, and public-IP exposure evidence — these
signals feed Coalition's automated underwriting scan directly.

---

## Question Mapping

### Q1 — Prior Cyber Incidents (Loss History)
**Form:** Within the last 3 years has Named Insured suffered any cyber incident resulting in
a claim in excess of $25,000?

**Coverage:** `MANUAL`

**Notes:** No Liongard data source covers insurance claims history. Requires client attestation
and, if Yes, a loss run from the prior carrier.

---

### Q2 — Known Circumstances
**Form:** Is Named Insured aware of any circumstances that could give rise to a claim?

**Coverage:** `MANUAL`

---

### Q3 — Encryption of Endpoints and Portable Media
**Form:** Does Named Insured implement encryption on laptop computers, desktop computers, and
other portable media devices?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/endpoint.md` — "Encryption at Rest" section

**Evidence:**
- `liongard_device LIST` filtered for compute devices → check `inspectors[]` for Windows/macOS/Linux
- BitLocker status: metricNames `Windows Workstation: Bitlocker Status Summary [VI]` (WS summary), `Windows Workstation: All Drives Encrypted` (WS all drives encrypted), `Windows Server: All Drives Encrypted` (server all drives)
- FileVault: metricName `macOS: File Vault Encryption Status` (macOS FileVault status)
- `liongard_device COUNT environmentId=<ID>` → denominator for coverage rate

**Answer guidance:** If ≥95% of managed endpoints show full-disk encryption, answer Yes. Surface
the exceptions list (unencrypted devices) as the gap to remediate before renewal.

---

### Q4 — PCI / PII / PHI Collection and Volume
**Form:** Does Named Insured collect, process, store, transmit, or have access to PCI, PII, or PHI
other than its own employees? If Yes: estimated volume of payment card transactions and PII/PHI records.

**Coverage:** `PARTIAL`

**Notes:** Liongard cannot classify data types or count PII records. The asset inventory DOES
provide supporting scope context:
- `liongard_identity COUNT environmentId=<ID>` → total identity count (employee scope)
- M365 user count via `liongard_metric` on the M365 inspector supports employee PII boundary
- HIPAA/PCI applicability and record volumes require client attestation

---

### Q5 — Weekly Offline / Cloud Backups
**Form:** Does Named Insured maintain at least weekly backups of all sensitive or critical data
offline or on a separate network?

**Coverage:** `PARTIAL`

**Domain reference:** `domains/backup.md` — "Backup Frequency" and "Backup Isolation" sections

**Evidence:**
- Backup vendor inspectors (Datto BCDR, Acronis, Axcient, Cove, Veeam): use
  `recipes/single-system-analysis/by-inspector/<backup-vendor>.md` for each deployed backup system
- Backup job recency and frequency are LIONGARD-answerable from the backup inspector dataprint
- Offline / air-gap isolation and cloud separation require manual attestation (backup config)

**Answer guidance:** If the backup inspector shows daily or continuous jobs running, answer Yes
for frequency. Note air-gap or cloud isolation status separately.

---

### Q6a — Email MFA
**Form:** For email — do you enforce Multi-Factor Authentication?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/auth.md` — "Email MFA" section

**Evidence:**
```
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true
```
Returns count of enabled identities without MFA. Divide by total enabled identities for coverage rate.

**Answer guidance:** Answer Yes if `mfaStatus="NO"` count = 0 (or near 0 with documented exceptions).
Include the coverage rate and exception list in the gap summary.

---

### Q6b — VPN / RDP / Remote Access MFA
**Form:** For VPN, RDP, RDWeb, RD Gateway, or other remote access — do you enforce MFA?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/auth.md` — "Remote Access MFA" section; `domains/network.md` — "RDP Exposure" section

**Evidence:**
- RDP disabled or MFA-protected: metric names/JMESPath queries from the Windows Server and Workstation inspectors
  (e.g., metricName=`Windows Workstation: Bitlocker Status Summary [VI]`, Windows Firewall RDP rule metrics)
- VPN MFA: SonicWall SSL-VPN RADIUS auth — `SslVpn.SslVpnServer.UseRadius` JMESPath [metric 200006 not in global catalog]; check each deployed VPN inspector
- External RDP exposure: `recipes/single-system-analysis/by-inspector/network-ip-address.md` — open port 3389 check

**Answer guidance:** Answer Yes only if ALL remote access paths (VPN, RDP, RDWeb) require MFA.
A single unprotected RDP exposure is a material gap — surface it explicitly.

---

### Q6c — Network / Cloud Admin MFA
**Form:** For network/cloud administration or other privileged user accounts — do you enforce MFA?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/auth.md` — "Privileged Account MFA" section

**Evidence:**
```
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true privileged=true
```

**Answer guidance:** Answer Yes if count = 0. If any privileged accounts lack MFA, this is a
high-severity finding — note names/count in the gap summary.

---

### Q7 — Wire Transfer Secondary Verification
**Form:** Does Named Insured require a secondary means of communication to validate funds
transfer authenticity before processing requests over $25,000?

**Coverage:** `MANUAL`

**Notes:** Financial fraud controls are a process/policy control. Liongard does not inspect
wire transfer approval workflows. Requires CFO or finance manager attestation.

---

### Q8 — Content Complaints History
**Form:** Within the last 3 years has Named Insured been subject to complaints concerning
content of its website, advertising, social media, or other publications?

**Coverage:** `MANUAL`

---

### Q9 — IP / Content Removal Procedures
**Form:** Does Named Insured enforce procedures to remove content that may infringe or
violate intellectual property or privacy rights?

**Coverage:** `MANUAL`

---

### Q10–11 — Concurrent E&O and Professional Liability Coverage
**Form:** Will Named Insured have an active Technology E&O / E&O or miscellaneous professional
liability policy concurrent with this policy?

**Coverage:** `MANUAL`

**Notes:** Insurance placement records — requires broker confirmation.

---

## Technology E&O Section (if applicable)

These questions apply only if Technology E&O coverage is requested:

| Question | Coverage | Notes |
|---|---|---|
| TEO-1 — Describe technology use | `MANUAL` | Business description |
| TEO-2 — Prior technology claims | `MANUAL` | Loss history |
| TEO-3 — MSP / high-risk industry flag | `PARTIAL` | If client is an MSP, Liongard's own inspector data can demonstrate maturity; flag to underwriter |
| TEO-4 — % of services under written contract | `MANUAL` | Legal / contract records |
| TEO-5 — Risk-mitigating clauses in agreements | `MANUAL` | Legal attestation |

---

## Internet Footprint Pre-Score Evidence

Coalition scans the applicant's public internet footprint before generating a quote. Pull this
evidence from Liongard before submitting the application to surface issues proactively:

| What Coalition scans | Liongard source |
|---|---|
| TLS certificate health (expired, weak cipher) | `recipes/single-system-analysis/by-inspector/tls-ssl.md` |
| DMARC / SPF / DKIM posture | `recipes/single-system-analysis/by-inspector/internet-domain-dns.md` |
| Open ports / public-IP exposure | `recipes/single-system-analysis/by-inspector/network-ip-address.md` |
| Domain expiration risk | `liongard_domain LIST environmentId=<ENV_ID> maxDaysTillExpiration=30` |
| Dark web credential exposure | `recipes/single-system-analysis/by-inspector/dark-web-monitoring.md` |

---

## Verification Log

| Item | Source | Notes |
|---|---|---|
| Form SP 17 717 1120 question set | `internal/cyber-insurance-forms/coalition/coalition-new-business-cyber-application.txt` | Full question text extracted |
| Evidence mapping | `domains/auth.md`, `domains/endpoint.md`, `domains/backup.md` | Domain files are the metric source of truth |
| Coalition scan context | Coalition product documentation | Automated internet scanning supplements this form |

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | Coalition questions map directly to onboarding inventory — identity count, device count, MFA status, and backup posture all collected at onboarding and refreshed each inspection cycle. |
| CIS Controls (v8.1) | ✅ | Coalition attestations map to: CIS 5–6 (Q6a–6c MFA tiers), CIS 1–2 (Q1 asset inventory), CIS 10 (Q7 backup coverage), CIS 7 (Q3–4 patching + EDR), CIS 12–13 (Q5 network segmentation), CIS 17 (Q10 IR/BCP), CIS 14 (Q8–9 email security + training). |
| Cyber-insurance domain files | ✅ | `domains/auth.md` (Q6a–6c MFA + PAM), `domains/endpoint.md` (Q3–5 EDR + patching), `domains/backup.md` (Q7 backup + immutability), `domains/network.md` (Q5 network controls), `domains/governance.md` (Q8–10 training + IR), `domains/vendor.md` (Q11 third-party). |
| QBR / quarterly-business-review | ✅ | Coalition renewal date aligns with QBR cadence. Pre-flight internet footprint sweep (Step 0 of `cyber-insurance-readiness.md`) should run at least 60 days before renewal so Coalition scan results match Liongard-observed posture. |

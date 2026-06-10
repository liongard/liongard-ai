---
name: cyber-insurance-application-universal
description: >
  Use this recipe to prepare a cyber insurance application for any carrier the MSP has
  not yet encountered, or as a pre-work pass before using a carrier-specific recipe.
  Produces draft Yes/No answers with supporting evidence for every question that appears
  across major carrier forms, organized into 15 universal control domains. Trigger phrases:
  "fill out a cyber insurance application", "new carrier application", "generic cyber
  insurance form", "universal cyber application", "prepare insurance answers", "cyber
  insurance application I haven't seen before", "answer underwriting questions for
  [carrier not in our library]". Distinct from cyber-insurance-readiness.md (evidence
  assessment) — this recipe produces draft application answers ready to hand to a broker.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_metric, liongard_identity, liongard_device, liongard_domain"
personas: [vcio-account-manager, technical-alignment-manager]
output_formats: [xlsx, word, markdown]
primitives: []
composes:
  - recipe:single-system:single-system-internet-domain-dns
  - recipe:single-system:single-system-knowbe4
  - recipe:single-system:single-system-network-ip-address
  - recipe:single-system:single-system-tls-ssl
  - recipe:system-type:system-type-all-edrs
  - recipe:system-type:system-type-all-external-attack-surface
  - recipe:system-type:system-type-windows-patching
---

# Cyber Insurance — Universal Application Assistant

> **Relationship to other recipes:**
> - `cyber-insurance-readiness.md` — evidence *assessment* organized by CIS Controls.
>   Use it to measure readiness and produce an evidence workbook.
> - **This recipe** — application *assistant* organized by carrier question domains.
>   Use it to produce draft answers ready to submit on any carrier form.
> - `carriers/<carrier>.md` — carrier-specific question number maps.
>   Use after this recipe when you know the specific carrier.

This recipe synthesizes the universal question set that appears across all major carrier
applications (Coalition, At-Bay, Cowbell, Hartford, Beazley, AIG, Corvus, Tokio Marine HCC,
Chubb, Hiscox, Travelers). Every question below appears on three or more carrier forms.
For each question, the recipe produces a draft answer, identifies the Liongard evidence
supporting it, and flags what still needs manual attestation.

**When to use this recipe:**
- The MSP is filling out a carrier form not in the `carriers/` library
- The MSP wants a complete draft application before a broker meeting
- The MSP wants to verify readiness across all common underwriting questions at once
- Pre-renewal prep: run this 60–90 days before renewal to surface gaps while there is
  time to remediate

---

## Customize for your MSP

```yaml
output:
  format: word              # word | xlsx | markdown
                             # word produces a broker-ready draft; xlsx produces
                             # an evidence workbook with draft answers per row
  filename: "<customer>-cyber-insurance-universal-application-<YYYY-MM-DD>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

draft_answer_style: "formal"    # formal | brief
                                 # formal = full sentence suitable for pasting into a form
                                 # brief = terse Yes/No + one-line rationale

thresholds:
  mfa_coverage_required_pct: 100   # carriers expect 100% on remote/admin
  edr_coverage_required_pct: 95
  patch_age_critical_days: 30
  backup_max_age_days: 7           # "weekly" is the most common carrier threshold
  account_inactive_days: 45
  evidence_currency_days: 90       # maximum age of inspection data to cite as current

carrier_form_on_hand: ""          # optional: note the specific carrier/form number
                                   # so the deliverable can include question-number
                                   # cross-references from the table in this recipe
```

---

## How to run

1. **Run Step 0** from `cyber-insurance-readiness.md` — internet footprint sweep first.
   This produces TLS, email authentication, open-port, and dark-web findings that feed
   directly into domains 3, 6, 7, and 8 below.

2. **Run Steps 1–2** from `cyber-insurance-readiness.md` — identify the environment and
   pull the asset inventory. Cache the identity and device arrays; the domains below
   filter that dataset.

3. **Work through the 15 domains** in order. For each question:
   - Pull the referenced evidence (asset filter or metric via the domain file)
   - Fill the draft answer template
   - Flag any `MANUAL` items for the client to attest

4. **Produce the deliverable** — a structured document with one section per domain,
   each containing: the question text, draft answer, evidence citations, and a
   manual-attestation checklist.

5. **If you know the carrier** — after completing this recipe, open the matching
   `carriers/<carrier>.md` file and map each draft answer to the carrier's specific
   question numbers. Most answers transfer directly; the carrier file flags any
   carrier-unique questions not covered here.

---

## Carrier Cross-Reference Table

The table below maps each universal domain to the corresponding question number on each
carrier's form. Use it to translate draft answers into specific carrier question responses.

| Universal Domain | Coalition | At-Bay | Cowbell | Hartford (U) | Beazley | AIG | Corvus | TMHCC | Chubb | Hiscox | Travelers |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1. MFA — Email | Q6a | §14 | R3/1.6 | §7 | Q6 | Q15a | Q11c | §6d | — | DB-DFA | Q10h |
| 2. MFA — Remote access | Q6b | §15 | R3/1.6 | §7 | Q5 | Q15a | Q11a | §6a | — | DB-DFA | Q10i |
| 3. MFA — Admin accounts | Q6c | §13 | R3/1.6 | §7 | — | Q15b | Q11b | §6c | — | DB-DFA | Q10j |
| 4. Endpoint AV/EDR | — | §13, 17 | 1.5b | §7 EP | Q9, Q14 | Q19 | Q13 | §5a, 6e | §4.1 | Cyber-net | Q10c |
| 5. Encryption — at rest | Q3 | §05 | 1.3 | §6 enc | Q2, §4.3 (C) | Q16 | Q14 enc | §5d | §4.2, 4.3 | DB-enc | Q6a |
| 6. Encryption — in transit | — | — | 1.3 | §6 enc | — | — | Q14 enc | §5d | §4.2 | DB-enc | Q6b |
| 7. Backup | Q5 | §18–21 | R2/1.5a | §6 bk | Q10, Q16 | — | Q10 | §6g | §4.5 | Cyber-net | Q10l |
| 8. Patch management | — | — | 1.5b | §7 patch | Q11 | — | — | — | §4.4 | Cyber-net | Q10d |
| 9. Email security (SEG/DMARC) | Q6a (partial) | §16 | — | §7 email | Q7, Q12 | Q22 | Q9 | §6f | — | — | — |
| 10. Security awareness training | — | §12 | 1.2/R4 | §7 train | Q8 | Q21 | Q18 | §7a | — | DB-trn | Q10e |
| 11. Incident response plan | — | §21 | R4/1.7 | §6 BCP | Q17 | — | Q15 | — | §4.6 | Cyber-IR | Q10n |
| 12. Data inventory (PII/PHI/PCI) | Q4 | §03–04 | — | §6 data | — | Q5 | Q7 | §4 | §1 rec | DB-data | Q4–Q5 |
| 13. Regulatory (HIPAA/PCI) | Q4 | §07–10 | — | — | — | Q5 PCI | Q21 | §5e | §4 PCI | DB-PCI | Q7–Q8 |
| 14. Wire transfer controls | Q7 | §11 | §3 opt | §7 funds | Q21 | — | Q19 | §7b | — | — | Q10g |
| 15. Prior incidents / loss history | Q1–Q2 | §24–25 | 2.1–2.4 | §8 | loss | warranty | Q22–24 | §8 | §3 loss | — | Q9 |

*(U) = Hartford CyberChoice Underwriting Application (CB 00 H027 03 0824)*
*(DB = Hiscox Data Breach section; Cyber = Hiscox Cyber Enhancements section)*

---

## Domain 1 — MFA: Email Access

**Universal question:** Do you enforce Multi-Factor Authentication (MFA) for ALL user access to email?

**Carrier framing variants:** "MFA for web-based email" (Beazley Q6) / "MFA enforced on ALL email access" (At-Bay §14) / "email MFA" (Hartford §7) / "MFA for access via webmail portal, Outlook, non-corporate devices, for all employees" (Corvus Q11c)

**Coverage:** `LIONGARD`

**Evidence:**
```
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true
```
→ Count of enabled identities without MFA (target: 0)
→ `liongard_identity COUNT environmentId=<ENV_ID> enabled=true` → total denominator

**Domain reference:** `domains/auth.md` — "Email MFA" section

**Draft answer template:**
> "Yes. MFA is enforced for all [N] enabled user accounts with email access via
> [M365 / Google Workspace / other]. As of [inspection date], [coverage %]% of
> enabled accounts have MFA enrolled ([N] of [total]). [If exceptions: N service
> accounts are excluded per documented exception; all human user accounts require MFA.]
> Evidence source: Liongard continuous identity inventory, most recent inspection
> [date]."

**If coverage < 100%:**
> "Partially. MFA is enforced for [N]% of email-accessible accounts ([N] of [total]).
> [N] accounts lack MFA enrollment: [list or count by type]. Remediation in progress;
> target completion date [date]."

---

## Domain 2 — MFA: Remote Access (VPN / RDP / RDWeb)

**Universal question:** Do you enforce MFA for ALL remote access to your network, including VPN, RDP, RD Gateway, and RDWeb?

**Carrier framing variants:** "MFA on ALL remote access" (Beazley Q5, AIG Q15a) / "VPN, RDP, RDWeb, RD Gateway, or other remote access" (Coalition Q6b) / "remote access to your network (cloud-hosted, on-premises, VPN)" (Hartford §7, Corvus Q11a)

**Coverage:** `LIONGARD`

**Evidence:**
- VPN MFA: deployed firewall inspector metric (see `domains/auth.md` → "Remote Access MFA")
- RDP exposure: `recipes/single-system-analysis/by-inspector/network-ip-address.md` → port 3389
- Identity level: `liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true`

**Domain reference:** `domains/auth.md` — "Remote Access MFA"; `domains/network.md` — "RDP"

**Draft answer template:**
> "Yes. MFA is required for all remote access paths: [VPN via <vendor> with RADIUS/MFA /
> RDP disabled on all externally facing endpoints / RDWeb protected by MFA].
> As of [date], no open RDP (port 3389) is exposed to the internet. All VPN connections
> require MFA authentication via [product]. Evidence: Liongard firewall and external
> attack surface inspection, [date]."

**If RDP is open:** Flag as ❌ before submitting — this is a hard underwriting signal
at At-Bay, TMHCC, AIG, and Coalition. Remediate before renewal.

---

## Domain 3 — MFA: Admin / Privileged Accounts

**Universal question:** Do you enforce MFA for all administrative and privileged user accounts?

**Carrier framing variants:** "MFA for network/cloud admin or privileged users" (Coalition Q6c) / "MFA for ALL administrative access" (AIG Q15b) / "MFA for admin accounts" (TMHCC §6c) / "MFA for privileged accounts (admin, service accounts)" (Corvus Q11b)

**Coverage:** `LIONGARD`

**Evidence:**
```
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true privileged=true
```
→ Target: 0

**Domain reference:** `domains/auth.md` — "Privileged Account MFA"

**Draft answer template:**
> "Yes. MFA is enforced for all [N] privileged/administrative accounts. As of
> [inspection date], 0 privileged accounts lack MFA enrollment. Administrative accounts
> are managed via [Active Directory / Azure AD / JumpCloud / other] with MFA enforced
> through [Conditional Access / Duo / other]. Evidence: Liongard identity inventory,
> [date]."

---

## Domain 4 — Endpoint Protection (AV / EDR / MDR)

**Universal question:** Do you have antivirus/antimalware and/or Endpoint Detection and Response (EDR) software deployed on all endpoints? If yes, identify the product and vendor.

**Carrier framing variants:** "AV and firewalls" (Chubb §4.1) / "EDR tool — company, software, SKUs" (AIG Q19) / "EDR or NGAV on all system endpoints" (TMHCC §6e) / "EDR/MDR product in place" (Hartford §7)

**Coverage:** `LIONGARD`

**Evidence:** `recipes/system-type-assessment/all-edrs.md`
- Deployed EDR vendor(s) and product names
- Coverage rate: servers and workstations separately
- Unprotected devices: `liongard_device LIST` → compute devices where `inspectors[]` lacks EDR slug

**Domain reference:** `domains/endpoint.md` — "EDR Coverage"

**Draft answer template:**
> "Yes. [EDR vendor / product name] (e.g., SentinelOne Singularity, CrowdStrike Falcon,
> Huntress) is deployed on [N] of [total] managed endpoints ([coverage %]% coverage).
> Server coverage: [N servers / coverage %]. Workstation coverage: [N workstations /
> coverage %]. [If MDR: endpoint monitoring is managed by [MDR vendor] 24/7.]
> Evidence: Liongard [EDR inspector] inspection, [date]."

---

## Domain 5 — Encryption at Rest (Laptops, Desktops, Servers)

**Universal question:** Is data on laptops, desktop computers, and servers encrypted using full-disk encryption (e.g., BitLocker, FileVault)?

**Carrier framing variants:** "Encryption on laptops, desktop computers, portable media" (Coalition Q3) / "encrypt data on end-user devices — BitLocker, FileVault, dm-crypt" (AIG Q16) / "Encryption of Mobile Computing Devices" (Chubb §4.3) / "encrypt all electronic information that leaves physical control" (Hartford §4i)

**Coverage:** `LIONGARD`

**Evidence:**
- Windows: metricName=`Windows Workstation: Bitlocker Status Summary [VI]` (WS BitLocker summary), metricName=`Windows Workstation: All Drives Encrypted` (WS all drives encrypted), metricName=`Windows Server: All Drives Encrypted` (server all drives)
- macOS: metricName=`macOS: File Vault Encryption Status` (FileVault status)
- Linux: per-system `liongard_metric EVALUATE` on Linux inspector

**Domain reference:** `domains/endpoint.md` — "Encryption at Rest"

**Draft answer template:**
> "Yes. Full-disk encryption is enabled on all managed endpoints. Windows devices use
> BitLocker ([N] of [total] Windows devices confirmed encrypted, [coverage %]% coverage).
> macOS devices use FileVault ([N] of [total] confirmed). [Linux: dm-crypt/LUKS
> confirmed on server-class Linux systems.] Evidence: Liongard endpoint inspection, [date]."

---

## Domain 6 — Encryption in Transit

**Universal question:** Is sensitive data encrypted in transit (VPN, TLS, email)?

**Carrier framing variants:** "Encrypt all electronic information that leaves physical control" (Hartford §4i) / "Encryption of Data in-transit" (Corvus Q14) / "Data in transit encrypted?" (Hartford §6 data inventory)

**Coverage:** `PARTIAL`

**Evidence:**
- TLS certificate health: `recipes/single-system-analysis/by-inspector/tls-ssl.md`
- DMARC/SPF/DKIM (email in transit): `recipes/single-system-analysis/by-inspector/internet-domain-dns.md`
- VPN encryption: deployed firewall inspector confirms encrypted tunnel type

**Draft answer template:**
> "Yes. Data in transit is protected via: (1) TLS [version] on all web services —
> certificates current, next expiry [date]; (2) DMARC [enforced/monitoring] /
> SPF [pass/fail] / DKIM [configured/missing] on domain [domain]; (3) all remote access
> via encrypted VPN ([vendor / protocol]). Evidence: Liongard external attack surface
> inspection, [date]."

---

## Domain 7 — Backup (Frequency, Isolation, Recovery)

**Universal question:** Do you maintain regular backups of critical data? Are backups stored offline or isolated from production systems? Have backups been tested?

**Carrier framing variants:** "Weekly backups offline or on separate network" (Coalition Q5) / "Backup frequency, offline, tested" (Hartford §6, Corvus Q10) / "Backup and restore procedures, offline backups" (At-Bay §18–21) / "Regular backups; offline/secure; regularly tested" (Beazley short form)

**Coverage:** `PARTIAL`

**Evidence:** Backup vendor inspector (Datto BCDR, Acronis, Axcient, Cove, Veeam):
- Job frequency and last-run timestamp: `LIONGARD`
- Offline / air-gap / cloud isolation: configuration field — `PARTIAL` or `MANUAL`
- Tested recovery: `MANUAL` — requires documented test results

**Domain reference:** `domains/backup.md`

**Draft answer template:**
> "Yes. Critical data is backed up [daily / continuously] using [backup vendor]. Backups
> are stored [offsite at [location] / in isolated cloud storage ([vendor]) / air-gapped].
> Most recent backup job: [date], status: [success]. Recovery testing: [date of last
> test, outcome]. Evidence: Liongard [backup inspector] inspection, [date]. Recovery
> testing confirmation: [client attestation / documented test record]."

---

## Domain 8 — Patch Management

**Universal question:** How frequently do you apply security updates and patches to critical systems? Do you actively patch internet-facing systems?

**Carrier framing variants:** "How often are system security updates/patches implemented?" (Hartford §4g) / "Actively manage and install critical patches across internet-facing systems" (Beazley Q11) / "Critical Software Patching Procedures" (Chubb §4.4)

**Coverage:** `LIONGARD`

**Evidence:** `recipes/system-type-assessment/all-windows-patching.md`
- Pending update age distribution across managed endpoints
- macOS: macOS inspector patch metrics
- Linux: Linux inspector security updates

**Domain reference:** `domains/endpoint.md` — "Patch Management"

**Draft answer template (monthly patch cadence):**
> "Critical security patches are applied within 30 days of release across all managed
> endpoints. As of [date]: [N] of [total] endpoints have no critical patches overdue
> ([coverage %]% current). Internet-facing systems are prioritized — [N] internet-facing
> servers have all critical patches applied as of [date]. Patch deployment is managed
> via [RMM vendor / WSUS / Intune]. Evidence: Liongard patching inspection, [date]."

---

## Domain 9 — Email Security (SEG, DMARC, External Tagging)

**Universal question:** Do you have email security controls in place — including filtering of malicious attachments/links, DMARC/SPF/DKIM, a Secure Email Gateway (SEG), and tagging of external sender emails?

**Carrier framing variants:** "SEG in place, attachment/link scanning, external tagging, anti-phishing" (Hartford §7) / "Inbound email security controls" (Beazley Q7) / "Email filtering / advanced SEG with sandboxing" (Corvus Q9) / "Email filtering solution beyond native provider" (TMHCC §6f)

**Coverage:** `PARTIAL`

**Evidence:**
- DMARC / SPF / DKIM: `recipes/single-system-analysis/by-inspector/internet-domain-dns.md` — `LIONGARD`
- M365 Defender for Office 365 / EOP: M365 inspector — `LIONGARD`
- Google Workspace filtering: Google Workspace inspector — `LIONGARD`
- Third-party SEG (Mimecast, Proofpoint, Barracuda): not inspected — `MANUAL`
- External email tagging: M365 transport rule — `PARTIAL`

**Domain reference:** `domains/auth.md` — "Email Authentication"

**Draft answer template:**
> "Yes. Email security controls include: (1) DMARC [policy: reject/quarantine/none] on
> [domain] with SPF [pass] and DKIM [configured]; (2) [M365 Defender for Office 365 /
> Google Workspace / SEG vendor] providing attachment scanning, link detonation, and
> anti-phishing protection; (3) external sender tagging enabled via [transport rule /
> SEG policy]. Evidence: Liongard DNS and M365 inspection, [date]. SEG vendor
> configuration: [client attestation]."

---

## Domain 10 — Security Awareness Training

**Universal question:** Do you provide cybersecurity awareness and anti-phishing training to all employees at least annually? Does training include phishing simulation?

**Carrier framing variants:** "Security training including phishing prevention" (At-Bay §12) / "Annual mandatory training" (Cowbell 1.2) / "Interactive social engineering training including simulation" (Beazley Q8) / "Annual security training with phishing simulation" (Corvus Q18)

**Coverage:** `PARTIAL`

**Evidence:**
- KnowBe4: `recipes/single-system-analysis/by-inspector/knowbe4.md` → campaign completion rate,
  simulation results — `LIONGARD` if deployed
- Other platforms: `MANUAL`

**Domain reference:** `domains/governance.md` — "Security Awareness"

**Draft answer template (KnowBe4 deployed):**
> "Yes. Annual cybersecurity awareness training including phishing simulation is conducted
> for all [N] employees via [KnowBe4 / platform]. Most recent training cycle: [date],
> completion rate: [%]. Phishing simulation campaigns run [frequency]; most recent
> click rate: [%]. Evidence: Liongard KnowBe4 inspection, [date]."

**Draft answer template (manual):**
> "Yes. Annual cybersecurity awareness and anti-phishing training is conducted for all
> employees. Most recent training cycle: [date], completion rate: [%]. [Phishing
> simulation: included / not currently included.] Evidence: HR/training records,
> [client attestation]."

---

## Domain 11 — Incident Response Plan

**Universal question:** Do you have a formal, tested Cyber Incident Response Plan (IRP) or Business Continuity / Disaster Recovery Plan?

**Carrier framing variants:** "Formal Cyber IRP" (Chubb §4.6) / "IR plan tested and in-effect" (Cowbell R4) / "BCP or DRP tested in last 12 months" (Corvus Q15) / "Cyber IRP or BCP in place; how often tested?" (Hartford §6)

**Coverage:** `MANUAL`

**Notes:** Liongard does not inspect governance documentation. Requires client attestation
of plan existence and most recent test date.

**Draft answer template:**
> "Yes. A formal Cyber Incident Response Plan is in place, approved by [CISO / senior
> leadership] on [date]. The plan covers: detection and analysis, containment, eradication
> and recovery, and post-incident review. Most recent tabletop exercise / test: [date],
> conducted by [internal team / IR retainer vendor]. Business Continuity Plan last
> reviewed: [date]."

---

## Domain 12 — Data Inventory (PII / PHI / PCI Record Types and Volumes)

**Universal question:** What types of sensitive data do you collect, process, store, or transmit? How many unique individuals' records? Does this include PII, PHI, or payment card data?

**Carrier framing variants:** "PII/PHI/PCI scope and volume" (AIG Q5, Coalition Q4) / "Record count tiers" (Corvus Q7, Hartford §6, Chubb §1) / "Data types collected" (At-Bay §04)

**Coverage:** `PARTIAL`

**Evidence:**
- Employee record scope: `liongard_identity COUNT environmentId=<ENV_ID>` → employee count
- Customer/patient/third-party records: `MANUAL` — data classification requires client attestation
- M365 user count (as proxy for email-accessible HR records): M365 inspector

**Draft answer template:**
> "[N] employees' records (HR, payroll, benefits data). Customer / third-party records:
> [client-attested count]. PII type: [SSN / addresses / dates of birth / financial
> account info — as applicable]. PHI: [Yes — [N] patient records / No]. Payment card
> data: [processed directly / fully outsourced to PCI-compliant processor / N/A].
> All sensitive records stored on [systems] with encryption at rest confirmed via
> Liongard inspection, [date]. Record volumes for customers/patients: [client attestation]."

---

## Domain 13 — Regulatory Compliance (HIPAA / PCI-DSS)

**Universal question:** Is your organization subject to and compliant with HIPAA? With PCI-DSS?

**Coverage:** `MANUAL` — compliance attestation is always manual; Liongard evidence supports
but cannot assert compliance.

**Notes:** Liongard can surface supporting evidence (access controls, encryption, user activity)
but the compliance declaration itself requires a HIPAA Privacy Officer or PCI QSA/SAQ attestation.

**Draft answer template (HIPAA):**
> "[Yes / No / N/A]. [If Yes: Organization confirmed compliance with HIPAA Privacy Rule
> and Security Rule. Most recent risk assessment: [date]. BAAs in place with all applicable
> vendors. PHI access controls confirmed via Liongard identity inspection: [N] users
> with PHI system access, all MFA-enrolled.]"

**Draft answer template (PCI):**
> "[Yes / No / N/A]. [If Yes: PCI-DSS compliance confirmed at Level [1/2/3/4] via
> [QSA assessment / SAQ]. Payment processing [fully outsourced to validated P2PE
> processor / handled in-house at Level X]. Most recent attestation: [date].]"

---

## Domain 14 — Financial Fraud / Wire Transfer Controls

**Universal question:** Do you require out-of-band secondary verification (phone call, separate channel) before executing fund transfers or processing account change requests from vendors?

**Carrier framing variants:** "Secondary means of communication to validate transfers over $25,000" (Coalition Q7) / "Dual authentication protocol for funds transfers" (Hartford §7) / "Out-of-band authentication for vendor account changes" (Beazley Q21) / "Wire transfer authorization with separation of authority" (TMHCC §7b)

**Coverage:** `MANUAL`

**Notes:** Financial fraud controls are a process / policy control. No Liongard inspector
covers wire transfer workflows. Requires CFO or finance manager attestation.

**Domain reference:** `domains/governance.md` — Q47 "Funds transfer out-of-band verification"

**Draft answer template:**
> "Yes. All fund transfer requests over $[threshold] require: (1) initiation by authorized
> personnel, (2) independent approval by a second authorized employee, and (3) verbal
> confirmation via a callback to a pre-registered phone number before execution.
> Account change requests from vendors are confirmed via a separate channel (phone call
> to the vendor's known number) before updating payment details. [Client attestation
> from CFO / finance manager, [date].]"

---

## Domain 15 — Prior Incidents and Loss History

**Universal question:** In the past [3–5] years, has your organization experienced any cyber incident, security breach, privacy violation, ransomware attack, or cyber-related claim? Are you aware of any circumstances that could give rise to a claim?

**Carrier framing variants:** "Cyber incident resulting in claim >$25K" (Coalition Q1) / "Prior claims in last 5 years exceeding $50K" (AIG warranty) / "Cyber incidents including attacks, extortion, breaches, system failures" (Hartford §8) / "Losses or claims in last 5 years" (Beazley short form)

**Coverage:** `MANUAL`

**Notes:** Claims and incident history are not inspectable. Requires client attestation
and, if Yes, a loss run from the prior carrier. This question directly affects coverage
terms — any answer of Yes should be reviewed by the broker before submission.

**Draft answer template (No prior incidents):**
> "No. The organization has not experienced any cyber incident, security breach, data
> privacy violation, ransomware attack, or system failure resulting in a loss or claim
> during the past [3/5] years. The organization is not aware of any circumstances,
> facts, or situations that could reasonably give rise to a claim under the proposed
> coverage."

**Draft answer template (Prior incident):**
> "Yes. [Brief factual description of incident: type, date, root cause.] Corrective
> actions taken: [list]. Total loss: $[amount]. Prior carrier claim: [filed / not filed].
> Loss run attached. Current controls implemented since incident: [summary]."

---

## Universal Manual-Attestation Checklist

These items appear on every major carrier form and have no Liongard evidence source.
Collect these from the client before the broker meeting:

| # | Item | Owner | Notes |
|---|---|---|---|
| A | CISO / designated security contact | IT leadership | Name, title, email — required on AIG, Beazley, Hartford, At-Bay |
| B | IT management model (in-house / outsourced MSP, provider name) | IT leadership | AIG Q18, Hartford §4 |
| C | Total revenue (most recent FY + current projection) | CFO | Required on all forms |
| D | Total employee count | HR | Required on all forms |
| E | PII / PHI / PCI record count (customers + third parties) | Legal / DPO | Most carriers ask for tier ranges |
| F | HIPAA compliance status and most recent risk assessment date | Compliance | HIPAA-subject orgs only |
| G | PCI-DSS compliance level and most recent attestation | Finance / IT | Payment-processing orgs only |
| H | Incident Response Plan — existence and most recent test date | IT / CISO | All carriers |
| I | BCP / DRP — existence and most recent test date | IT / CISO | Most carriers |
| J | Security awareness training completion rate and most recent date | HR / IT | All carriers |
| K | Wire transfer out-of-band verification process | CFO / Finance | Most carriers |
| L | Vendor account change verification process | Finance | Most carriers |
| M | Prior cyber incidents / claims (last 3–5 years) | Legal / broker | All carriers |
| N | Pending litigation or known circumstances | Legal | All carriers |
| O | Media / IP legal review process (published content) | Marketing / Legal | Most carriers (optional for many) |
| P | M&A activity in past 12 months | CFO | Hartford, Beazley, Coalition, Cowbell |

---

## Coverage Summary by Domain

| Domain | Liongard Coverage | Draft Answer Source |
|---|---|---|
| 1 — MFA: Email | `LIONGARD` | Asset inventory identity MFA count |
| 2 — MFA: Remote access | `LIONGARD` | Firewall inspector + external attack surface |
| 3 — MFA: Admin accounts | `LIONGARD` | Asset inventory privileged identity MFA count |
| 4 — Endpoint AV/EDR | `LIONGARD` | EDR inspector coverage rate + vendor name |
| 5 — Encryption at rest | `LIONGARD` | BitLocker/FileVault metrics |
| 6 — Encryption in transit | `PARTIAL` | TLS recipe + DMARC recipe; VPN config manual |
| 7 — Backup | `PARTIAL` | Backup inspector frequency; isolation/testing manual |
| 8 — Patch management | `LIONGARD` | Patching recipe |
| 9 — Email security | `PARTIAL` | DNS inspector (DMARC/SPF/DKIM); SEG vendor manual |
| 10 — Security training | `PARTIAL` | KnowBe4 if deployed; otherwise manual |
| 11 — IR plan | `MANUAL` | Client attestation |
| 12 — Data inventory | `PARTIAL` | Identity count for employee scope; customer records manual |
| 13 — Regulatory compliance | `MANUAL` | Client attestation + supporting Liongard evidence |
| 14 — Wire transfer controls | `MANUAL` | Finance process attestation |
| 15 — Prior incidents | `MANUAL` | Client attestation + loss run |

**Summary:** Of the 15 universal domains, **8 are fully or substantially answerable from
Liongard evidence** (domains 1–5, 8, and partial 6–7). The remaining 7 require manual
attestation but can be pre-populated with templates from this recipe.

---

## Output format

The recommended deliverable is a **Word document** structured as:

1. **Cover page** — client name, assessment date, carrier (if known), MSP name
2. **Executive Summary** — coverage score (Liongard-answerable domains), top 3 gaps, renewal readiness statement
3. **Domain sections 1–15** — one section per domain with: question text, draft answer, evidence citations
4. **Manual attestation checklist** — items A–P above, for client completion before broker submission
5. **Gap remediation plan** — any domains with `❌ NON-COMPLIANT` findings, prioritized by carrier impact

For an Excel deliverable: one row per question with columns for Draft Answer, Evidence Source,
Status (LIONGARD / PARTIAL / MANUAL), and Notes.

---

## Pairs with

- `cyber-insurance-readiness.md` — evidence assessment (run first if full CIS Controls coverage is needed)
- `carriers/` — carrier-specific question maps (use after this recipe when carrier is known)
- `recipes/system-type-assessment/all-external-attack-surface.md` — Step 0 pre-flight
- `recipes/system-type-assessment/all-edrs.md` — Domain 4 evidence
- `recipes/system-type-assessment/all-windows-patching.md` — Domain 8 evidence
- `recipes/single-system-analysis/by-inspector/knowbe4.md` — Domain 10 evidence (if deployed)
- `domains/auth.md`, `domains/endpoint.md`, `domains/backup.md`, `domains/network.md`,
  `domains/governance.md` — full metric tables for each domain

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | The onboarding assessment is the primary intake for all 15 universal domains — MFA deployment, EDR presence, backup architecture, patching cadence, and identity inventory are all captured at onboarding and used directly in application draft answers. |
| CIS Controls (v8.1) | ✅ | All 15 domains map to CIS Controls v8.1: CIS 5–6 (Domains 1–3 MFA tiers), CIS 13 (Domain 4 EDR), CIS 3 (Domain 5 encryption at rest), CIS 3/12 (Domain 6 encryption in transit), CIS 10 (Domain 7 backup), CIS 7 (Domain 8 patching), CIS 9 (Domain 9 email security), CIS 14 (Domain 10 training), CIS 17 (Domain 11 IR plan), CIS 1–2 (Domain 12 data inventory), CIS 3/18 (Domain 13 regulatory), CIS 6/5 (Domain 14 wire transfer controls), CIS 17 (Domain 15 prior incidents). |
| Cyber-insurance domain files | ✅ | This recipe is the aggregation layer above the 7 domain files. Evidence for each domain is sourced from: `domains/auth.md` (Domains 1–3), `domains/endpoint.md` (Domains 4–5, 8), `domains/network.md` (Domain 6), `domains/backup.md` (Domain 7), `domains/governance.md` (Domains 9–11, 14–15), `domains/regulatory.md` (Domain 13), `domains/vendor.md` (cross-cutting). |
| QBR / quarterly-business-review | ✅ | This recipe is designed to run once per renewal cycle, feeding draft answers into the carrier-specific form. The QBR closest to the earliest carrier renewal date is the canonical runtime. Use the carrier cross-reference table to translate domain answers to the specific question numbers on whichever form you are completing. |

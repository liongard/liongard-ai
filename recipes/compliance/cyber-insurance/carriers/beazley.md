---
name: cyber-insurance-beazley
description: >
  Use this recipe when filling out the Beazley Cyber Insurance Application — Below $250M Revenue
  (F00863 042023 ed.) or the Beazley Short-Form Questionnaire for accounts under $20M.
  Trigger phrases: "fill out Beazley cyber application", "Beazley BBR renewal",
  "Beazley cyber application below 250m", "answer Beazley underwriting questions".
  Carrier-specific variant of the cyber-insurance-readiness master recipe.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_metric, liongard_identity, liongard_device"
personas: [vcio-account-manager, technical-alignment-manager, soc]
output_formats: [xlsx, word, markdown]
primitives: []
composes:
  - recipe:compliance:cyber-insurance-readiness
  - recipe:single-system:single-system-knowbe4
  - recipe:single-system:single-system-network-ip-address
  - recipe:system-type:system-type-all-edrs
  - recipe:system-type:system-type-windows-patching
---


```yaml
customize:
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed
```
# Cyber Insurance — Carrier: Beazley

> **Pairs with:** `recipes/compliance/cyber-insurance/cyber-insurance-readiness.md` (master workflow)
> and the `domains/` files for full metric tables.

**Forms covered:**
- Beazley Cyber Insurance Application — Below $250M Revenue (F00863 042023 ed.)
- Beazley Cyber Insurance Questionnaire — Short Form (Sub-$20M revenue)

**Form selection:** Use the Short Form for accounts under $20M. The Below-$250M form adds
additional controls questions (Q12–17) for accounts with revenue over $35M. Accounts over
$250M require a separate application not covered here.

**Important Beazley context:** Beazley has a dedicated Breach Response team (BBR) and places
heavy emphasis on incident response plan, privileged access management, and EDR quality.
For accounts over $35M, Q12–17 add questions on advanced email security, macro policy,
PAM tooling, hardened configurations, and backup isolation.

---

## Coverage Summary

| Question | Topic | Coverage |
|---|---|---|
| Q3 — CISO / security contact | Designated security lead | `MANUAL` |
| Q5 — MFA for remote access | VPN / RDP / cloud | `LIONGARD` |
| Q6 — MFA for web email | Email MFA | `LIONGARD` |
| Q7 — Inbound email security controls | Email filtering | `PARTIAL` |
| Q8 — Phishing training frequency | Awareness training | `PARTIAL` — KnowBe4 if deployed |
| Q9 — AV / anti-malware on all devices | Endpoint protection | `LIONGARD` |
| Q10 — Backup frequency | Backup cadence | `PARTIAL` |
| Q11 — Critical patch management (internet-facing) | Patch management | `LIONGARD` |
| Q12 — Advanced email security (>$35M) | M365 Defender / SEG | `PARTIAL` |
| Q13 — Macro policy (>$35M) | Office macro controls | `PARTIAL` |
| Q14 — EDR / MDR product (>$35M) | EDR deployment | `LIONGARD` |
| Q15 — Hardened baseline config (>$35M) | Device hardening | `MANUAL` |
| Q16 — Cloud backup isolation (>$35M) | Sync vs. true backup | `PARTIAL` |
| Q17 — IR plan (>$35M) | Incident response | `MANUAL` |
| Q18–19 — Media controls | IP / content | `MANUAL` |
| Q20–21 — Financial fraud controls | Wire transfer / vendor changes | `MANUAL` |
| Q22 — M&A activity | Business changes | `MANUAL` |

---

## Question Mapping

### Q5 — MFA for Remote Access

**Form:** Require MFA for remote access to network (cloud-hosted and on-premises, including VPNs)?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/auth.md` — "Remote Access MFA"; `domains/network.md` — "VPN / RDP"

**Evidence:**
- VPN MFA: deployed firewall inspector metrics (SonicWall RADIUS, Fortinet, Sophos, etc.)
- RDP exposure: `recipes/single-system-analysis/by-inspector/network-ip-address.md` — port 3389
- Identity fallback: `liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true`

---

### Q6 — MFA for Web Email

**Form:** Require MFA for access to web-based email?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/auth.md` — "Email MFA"

```
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true
```

---

### Q7 — Inbound Email Security Controls

**Form:** Security controls for incoming email? (Attachment screening / Link screening / External tagging)

**Coverage:** `PARTIAL`

**Evidence:**
- M365 Defender for Office 365 / EOP: M365 inspector confirms deployment
- Google Workspace spam filtering: Google Workspace inspector
- External email tagging: M365 transport rule visibility (partial via M365 inspector)
- Third-party SEG (Mimecast, Barracuda, Proofpoint): not directly inspected — client attestation

---

### Q8 — Phishing Training Frequency

**Form:** How often is interactive social engineering / phishing training conducted?
(Never / Annually / ≥2× per year)

**Coverage:** `PARTIAL`

**Evidence:** If KnowBe4 is deployed, run `recipes/single-system-analysis/by-inspector/knowbe4.md`
for training completion rate and campaign frequency. Otherwise `MANUAL`.

---

### Q9 — Antivirus / Anti-Malware on All Devices

**Form:** Protect all company devices with anti-virus, anti-malware, and/or endpoint protection?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/endpoint.md` — "EDR / AV Coverage"

**Evidence:**
- `liongard_device LIST environmentId=<ENV_ID>` → filter for compute devices where `inspectors[]`
  does NOT contain an AV/EDR inspector slug → unprotected count
- Per-EDR coverage rate: `recipes/system-type-assessment/all-edrs.md`

---

### Q10 — Backup Frequency

**Form:** Regularly back up business-critical data? (No / At least monthly / At least weekly or daily)

**Coverage:** `PARTIAL`

**Domain reference:** `domains/backup.md` — "Backup Frequency"

**Evidence:** Use the relevant backup vendor single-system recipe for the client's deployed
backup platform (Datto BCDR, Acronis Cyber Protect Cloud, Axcient, Cove, Veeam).

**Answer guidance:** Beazley's best tier is "at least weekly or daily" — confirm from backup
job schedule and last-run timestamp.

---

### Q11 — Critical Patch Management (Internet-Facing Systems)

**Form:** Actively manage and install critical patches across internet-facing systems?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/endpoint.md` — "Patch Management"

**Evidence:**
- `recipes/system-type-assessment/all-windows-patching.md` — pending update counts and ages
- External-facing server patching: run the Windows Server recipe for internet-facing systems

---

### Q12 — Advanced Email Security (>$35M revenue)

**Form:** Use Microsoft 365 Defender add-on or equivalent advanced threat hunting product?

**Coverage:** `PARTIAL`

**Evidence:** M365 inspector — confirm whether Defender for Office 365 Plan 1 or Plan 2
(MDO) is licensed and active. License SKU visible via M365 inspector `EmailLicenses` field.

---

### Q13 — Macro Policy (>$35M revenue)

**Form:** Disable macros in Office / Google Workspace by default?

**Coverage:** `PARTIAL`

**Evidence:** M365 / Windows OS inspector group policy fields may surface macro policy — check
with `liongard_metric EVALUATE` on the M365 or Windows inspector for relevant policy settings.
If not available, `MANUAL` — confirm from GP/Intune policy or admin attestation.

---

### Q14 — EDR / MDR Product (>$35M revenue)

**Form:** EDR vendor and product name?

**Coverage:** `LIONGARD`

**Domain reference:** `domains/endpoint.md` — "EDR Coverage"

**Evidence:** `recipes/system-type-assessment/all-edrs.md` — returns EDR vendor(s), coverage
rate, and product details from the inspector system metadata.

---

### Q15 — Hardened Baseline Configuration (>$35M revenue)

**Form:** Use a hardened baseline configuration across all (or substantially all) devices?

**Coverage:** `MANUAL`

**Notes:** Hardening benchmarks (CIS, DISA STIG) are configuration standards not directly
inspected. Confirm via compliance scanning tool or admin attestation.

---

### Q16 — Cloud Backup Isolation (>$35M revenue)

**Form:** If relying on cloud backup, is it a "syncing service" (DropBox, OneDrive, etc.)?

**Coverage:** `PARTIAL`

**Evidence:** Backup inspector platform type (Datto, Acronis, Axcient, Veeam) indicates true
backup vs. sync. Cloud file storage inspector (Box, Dropbox, Google Drive) confirms whether
the client is relying on sync services as backup — flag if so.

---

### Q17 — Incident Response Plan (>$35M revenue)

**Form:** Incident response plan for network intrusions and malware incidents?

**Coverage:** `MANUAL` — policy documentation attestation.

---

### Q18–22 — Media / Funds Transfer / M&A

**Coverage:** `MANUAL` throughout.

---

## Verification Log

| Item | Source | Notes |
|---|---|---|
| Below-$250M form | `internal/cyber-insurance-forms/beazley/beazley-cyber-insurance-below-250m-2023.txt` | F00863 042023 ed. |
| Short sub-$20M form | `internal/cyber-insurance-forms/beazley/beazley-cyber-insurance-short-sub-20m.txt` | UK/ROW short form |
| Evidence mapping | `domains/auth.md`, `domains/endpoint.md`, `domains/backup.md`, `domains/network.md`, `domains/governance.md` | Domain files are metric source of truth |

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | Beazley baseline questions (Q4–Q6) are directly populated by onboarding inventory: EDR presence, MFA for remote/email, and backup posture. |
| CIS Controls (v8.1) | ✅ | Beazley maps to: CIS 5–6 (Q5–6 MFA), CIS 13 (Q4 AV/EDR), CIS 10 (Q7 backup), CIS 7 (Q8 patching), CIS 17 (Q14 IR plan). Revenue >$35M questions (Q12–17) add CIS 12, 15, 18. |
| Cyber-insurance domain files | ✅ | `domains/auth.md` (Q5–6 MFA + PAM), `domains/endpoint.md` (Q4 EDR + Q8 patching), `domains/backup.md` (Q7 backup + immutability), `domains/governance.md` (Q14 IR + Q10 training), `domains/network.md` (Q12–13 network controls — >$35M). |
| QBR / quarterly-business-review | ✅ | Beazley uses binary Yes/No attestation; the QBR closest to renewal is the canonical run time for this recipe. Revenue threshold check (>$35M) determines which extended questions apply — verify with client before running. |

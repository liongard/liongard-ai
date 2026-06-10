---
name: cyber-insurance-cowbell
description: >
  Use this recipe when filling out the Cowbell Cyber Risk Insurance Prime 250 Renewal
  Application (PRIME 250 075 06 21) or the Prime 250 New Business Application
  (PRIME 250 003 07 20). Trigger phrases: "fill out Cowbell cyber application",
  "Cowbell Prime 250 renewal", "Cowbell renewal form", "answer Cowbell underwriting
  questions". Carrier-specific variant of the cyber-insurance-readiness master recipe.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_metric, liongard_identity, liongard_device"
personas: [vcio-account-manager, technical-alignment-manager]
output_formats: [xlsx, word, markdown]
primitives: []
composes:
  - recipe:compliance:cyber-insurance-readiness
  - recipe:single-system:single-system-internet-domain-dns
  - recipe:single-system:single-system-knowbe4
  - recipe:single-system:single-system-tls-ssl
  - recipe:system-type:system-type-windows-patching
---


```yaml
customize:
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed
```
# Cyber Insurance — Carrier: Cowbell

> **Pairs with:** `recipes/compliance/cyber-insurance/cyber-insurance-readiness.md` (master workflow)
> and the `domains/` files for full metric tables.

**Forms covered:**
- Cowbell Cyber Risk Insurance Renewal Application — PRIME 250 075 06 21
- Cowbell Cyber Risk Insurance New Business Application — PRIME 250 003 07 20

**Important Cowbell context:** Cowbell uses continuous monitoring of the insured's cyber risk
posture (via the **Cowbell Factor** score) and may auto-rate renewals based on that score rather
than requiring a full application. The Prime 250 is Cowbell's SMB-focused product (typically
for organizations under $25M revenue). Renewal forms are short (5 questions); new business is
more detailed.

---

## How to run

1. Run the master recipe's Steps 1–3.
2. Determine whether this is a renewal (short form) or new business (longer form).
3. For renewal: the form asks only 5 questions — confirm whether any Yes answers are needed.
4. For new business: work through Sections 1–4 below.

---

## Coverage Summary — Renewal Application (PRIME 250 075 06 21)

| Question | Coverage | Evidence |
|---|---|---|
| R1 — Any changes from prior application | `LIONGARD-ASSISTED` | Compare current posture to last year's answers using Liongard data below |
| R2 — Backup frequency and properties | `PARTIAL` | Backup inspector: frequency confirmed; encryption/testing are configuration fields |
| R3 — MFA enforced on all users/contractors/partners | `LIONGARD` | `liongard_identity COUNT mfaStatus="NO"` |
| R4 — Incident response plan tested and in effect | `MANUAL` | Policy attestation |
| R5 — Business size / scope changes | `MANUAL` | Business records |

---

## Coverage Summary — New Business Application (PRIME 250 003 07 20)

| Section | Questions | Coverage |
|---|---|---|
| 1.1 — Information security responsibility | `MANUAL` — designated person attestation |
| 1.2 — Mandatory annual cybersecurity training | `PARTIAL` — KnowBe4 recipe if deployed; otherwise manual |
| 1.3 — Encryption of external communications | `PARTIAL` — DMARC/TLS from external attack surface |
| 1.4 — Encryption of sensitive data in cloud | `PARTIAL` — M365 / cloud inspector configuration |
| 1.5a — Backup frequency and properties | `PARTIAL` — backup inspector |
| 1.5b — Security patching cadence | `LIONGARD` — Windows patching recipe |
| 1.6 — MFA enforcement | `LIONGARD` — identity MFA coverage |
| 1.7 — Incident response plan | `MANUAL` |

---

## Question Mapping

### Renewal R2 — Backup Frequency and Properties

**Coverage:** `PARTIAL`

**Domain reference:** `domains/backup.md` — "Backup Frequency" and "Backup Properties" sections

**Evidence:**
- Use the relevant backup inspector single-system recipe (Datto BCDR, Acronis, Axcient, Cove, Veeam)
  to confirm job frequency and last-run date
- Cowbell asks specifically for: Encrypted / Tested / Separate (offline or cloud) — backup inspector
  configuration fields confirm encryption and isolation where available; test confirmation is manual

---

### Renewal R3 / New Business 1.6 — MFA

**Form (renewal):** Do you enforce MFA for all employees, contractors, and partners?
If Yes: Mission-Critical Systems / Email / Remote Access / Cloud Deployments

**Coverage:** `LIONGARD`

**Domain reference:** `domains/auth.md` — "Email MFA", "Remote Access MFA", "Privileged Account MFA"

**Evidence:**
```
# Total enabled identities without MFA
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true

# Privileged identities without MFA
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true privileged=true
```

**Answer guidance:** Answer Yes if count = 0 for all enabled users. Report coverage rate
(e.g., "MFA enforced on 98% of 150 enabled identities; 3 service accounts pending"). Cowbell
scores the MFA categories separately — confirm email, remote access, and cloud all have MFA.

---

### New Business 1.3 — Encryption of External Communications

**Form:** Does the organization encrypt all external communications containing sensitive information?

**Coverage:** `PARTIAL`

**Domain reference:** `domains/auth.md` — "Email Encryption" and `domains/endpoint.md` — "Encryption in Transit"

**Evidence:**
- DMARC / TLS enforcement: `recipes/single-system-analysis/by-inspector/internet-domain-dns.md`
- TLS certificate health: `recipes/single-system-analysis/by-inspector/tls-ssl.md`
- Email encryption (S/MIME, OME): M365 inspector configuration — manual confirmation

---

### New Business 1.4 — Cloud Data Encryption

**Form:** Does the organization encrypt sensitive information stored on the cloud?

**Coverage:** `PARTIAL`

**Evidence:**
- M365 data-at-rest encryption is a platform default — confirm M365 inspector is active
- Azure / AWS encryption-at-rest status: cloud inspector configuration fields (manual if cloud
  inspector not deployed)
- OneDrive / SharePoint encryption: M365 platform default; no per-file encryption metric available

---

### New Business 1.5b — Security Patching Cadence

**Form:** How often does the organization apply updates to critical IT systems? (Weekly / Monthly / Quarterly / Every 6 months / Never)

**Coverage:** `LIONGARD`

**Domain reference:** `domains/endpoint.md` — "Patch Management" section

**Evidence:** Run `recipes/system-type-assessment/all-windows-patching.md` for Windows patch
cadence. For macOS: macOS inspector patch metrics. For Linux: Linux inspector security updates.

**Answer guidance:** Translate patch data into Cowbell's frequency tiers. Monthly patches on
most endpoints → select "Monthly". Note any endpoints with patches >90 days overdue.

---

### New Business 1.2 — Security Awareness Training

**Form:** Does the organization hold mandatory cybersecurity training with all employees at least annually?

**Coverage:** `PARTIAL`

**Evidence:** If the client uses KnowBe4, run `recipes/single-system-analysis/by-inspector/knowbe4.md`
for training completion rate. Otherwise `MANUAL` — confirm with HR or IT manager.

---

### Sections 2–4 — Past Activities, Cyber Crime, System Failure Options

**Coverage:** `MANUAL` throughout

**Notes:**
- Past claims, litigation, and breach history: client attestation and loss runs
- Cyber Crime endorsement questions (vendor bank account verification, wire transfer authorization):
  finance process attestation
- System Failure Contingent BI questions (DMZ segregation, third-party security requirements):
  `PARTIAL` — firewall inspector may confirm DMZ configuration; third-party contract terms are manual

---

## Verification Log

| Item | Source | Notes |
|---|---|---|
| Renewal question set (PRIME 250 075 06 21) | `internal/cyber-insurance-forms/cowbell/cowbell-prime250-renewal-application.txt` | Extracted |
| New business question set (PRIME 250 003 07 20) | Same file | Included in the same PDF |
| Evidence mapping | `domains/auth.md`, `domains/endpoint.md`, `domains/backup.md` | Domain files are metric source of truth |

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | Cowbell Prime 250 draws on onboarding inventory for MFA status, patching cadence, and backup confirmation — all captured at onboarding intake. |
| CIS Controls (v8.1) | ✅ | Cowbell maps to: CIS 5–6 (R3/1.6 MFA), CIS 7 (1.5b patching cadence), CIS 10 (1.4 backup + immutability), CIS 13 (1.3 EDR/AV), CIS 17 (1.7 IR plan). |
| Cyber-insurance domain files | ✅ | `domains/auth.md` (R3/1.6 MFA), `domains/endpoint.md` (1.3 EDR + 1.5b patching), `domains/backup.md` (1.4 backup + immutability), `domains/governance.md` (1.7 IR plan + training). |
| QBR / quarterly-business-review | ✅ | Cowbell Prime 250 renewal form is only 5 questions — the most concise form in the library. Run this recipe at the QBR closest to renewal; all five renewal questions are answerable within 15 minutes using Liongard MCP data. |

---
name: hipaa-readiness
description: >
  Use this skill when the user wants a HIPAA Security Rule readiness
  assessment, Security Rule gap analysis, HIPAA technical-safeguard evidence
  pack, or pre-audit compliance workbook for a healthcare or covered-entity
  customer. Compliance variant of the cross-cutting recipe pattern — point-
  in-time evidence collection mapped to HIPAA Security Rule technical and
  administrative safeguards, with per-section breakouts. Trigger phrases:
  "HIPAA readiness", "HIPAA Security Rule assessment", "HIPAA gap analysis",
  "HIPAA technical safeguards audit", "HIPAA pre-audit", "HIPAA evidence pack",
  "what's our HIPAA posture", "ePHI security review", "covered entity security
  assessment", "business associate HIPAA assessment". Auto-discovers deployed
  inspectors, chains per-class recipes, and maps findings to the HIPAA Security
  Rule (45 CFR Part 164, Subpart C). Produces a Word readiness narrative and
  an Excel evidence workbook.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_launchpoint, liongard_timeline, liongard_cyber_risk_dashboard, liongard_identity, liongard_device, liongard_domain, liongard_metric, liongard_detection, liongard_alert"
personas: [soc, vcio-account-manager, technical-alignment-manager, executive]
output_formats: [word, xlsx, markdown]
primitives: []
composes:
  - recipe:single-system:single-system-knowbe4
  - recipe:single-system:single-system-tls-ssl
  - recipe:single-system:single-system-windows-server
  - recipe:single-system:single-system-windows-workstation
  - recipe:system-type:system-type-all-backups
  - recipe:system-type:system-type-all-edrs
  - recipe:system-type:system-type-all-firewalls
  - recipe:system-type:system-type-windows-patching
---

# HIPAA Readiness — Master Recipe

> **The canonical HIPAA Security Rule compliance evidence recipe.** Maps
> Liongard data to the HIPAA Security Rule (45 CFR Part 164, Subpart C)
> technical safeguards (§164.312) and selected administrative safeguards
> (§164.308) and physical safeguards (§164.310) where Liongard evidence is
> available.
>
> **Who this applies to:** Covered Entities (healthcare providers, health
> plans, healthcare clearinghouses) and Business Associates (vendors and
> MSPs that create, receive, maintain, or transmit ePHI on behalf of a
> covered entity). MSPs serving healthcare customers are typically Business
> Associates and must comply with the Security Rule independently.
>
> **Scope: technical and procedural controls evidenced by Liongard.** The
> HIPAA Security Rule has 18 Standards across Administrative, Physical, and
> Technical categories. Many standards are policy/procedural and require
> external documentation (risk assessment, workforce training, contingency
> plan, BAA register). This recipe surfaces the Liongard-evidenced subset and
> clearly marks policy-driven standards as "external documentation required."
>
> **2025 HIPAA Security Rule update (HHS proposed):** HHS published a Notice
> of Proposed Rulemaking (NPRM) in January 2025 to strengthen Security Rule
> requirements — including mandatory MFA, 72-hour backup restoration
> requirements, network segmentation, and annual compliance audits. Where
> finalized, these align with or strengthen the controls in this recipe. Verify
> final rule status and adjust thresholds if your customer's regulatory counsel
> confirms applicability.
>
> **Customer-stack-adaptive.** Calls `liongard_launchpoint LIST` to discover
> deployed inspectors, then chains the appropriate per-class recipes for
> identity, endpoint, network, backup, and domain evidence. Standards requiring
> data from uninspected systems are flagged as "deploy required inspector" gaps.
>
> **References:** `reference/cross-cutting-signals.md`,
> `reference/asset-fields.md`, `reference/qa-retry-pattern.md`,
> `reference/inspector-aliases.md`, `reference/personas-recipe-matrix.md`.

---

## Customize for your MSP

```yaml
output:
  format: word                          # word | xlsx | markdown
                                        # word for the readiness narrative;
                                        # xlsx for the evidence workbook (one sheet per
                                        # Security Rule section);
                                        # markdown for working drafts.
  filename: "<customer>-HIPAA-Security-Rule-Readiness-<YYYY-MM-DD>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  cover: "HIPAA Security Rule Readiness Assessment"
  executive_summary: "Executive Summary"
  entity_type: "Covered Entity / Business Associate Classification"
  scope_definition: "ePHI Systems & Scope"
  readiness_summary: "Readiness Summary by Safeguard Category"
  administrative: "Administrative Safeguards (§164.308)"
  physical: "Physical Safeguards (§164.310)"
  technical: "Technical Safeguards (§164.312)"
  gap_tracker: "Gap Remediation Tracker"
  policy_external: "Policy / External Documentation Required"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Manual Verification"
  appendix: "Appendix — Methodology"

audience:
  tone: "balanced"                      # technical | balanced | executive
  reading_level: "compliance-and-technical"

hipaa_scope:
  entity_type: "business-associate"     # covered-entity | business-associate | both
  phi_systems: []                       # list of inspector slugs or system IDs in ePHI scope
                                        # leave empty to assess all discovered systems

slas:
  mfa_coverage_pct_min: 100             # ePHI system access — MFA required for all users
  patch_age_days_max: 30                # §164.308(a)(5)(ii)(B) — patch management
  account_inactive_days_max: 90         # §164.308(a)(3)(ii)(B) — workforce clearance
  password_min_length: 8                # HIPAA does not specify length; 8+ is minimum best practice
  backup_rpo_days_max: 1                # §164.308(a)(7)(ii)(A) — data backup plan
  backup_test_days_max: 90              # §164.308(a)(7)(ii)(D) — testing and revision
  tls_min_version: "1.2"               # §164.312(e)(2)(ii) — encryption in transit
  inspector_lastseen_days_max: 7
  license_expiration_warn_days: 30

naming:
  client_term: "Client"
  environment_term: "Environment"
  phi_term: "ePHI"                      # ePHI | PHI | patient data

qa:
  retry_on_null: true
  retry_on_empty_array: false
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: false
```

---

## When to use

- **Annual HIPAA Security Rule risk assessment support** — technical evidence
  component of the required annual review.
- **Business Associate security assessment** — demonstrate to a covered-entity
  client that the MSP's controls meet Security Rule requirements.
- **Pre-OCR audit preparation** — gather technical evidence before an Office
  for Civil Rights audit or investigation.
- **Onboarding a new healthcare customer** — baseline HIPAA posture gap
  analysis before signing a Business Associate Agreement (BAA).
- **Cyber-insurance for healthcare** — many cyber-insurance carriers require
  HIPAA compliance evidence; this recipe pairs with the cyber-insurance
  readiness recipe.

---

## HIPAA Security Rule control mapping

### Administrative Safeguards (§164.308) — Liongard-evidenced subset

| Standard | Implementation Specification | Liongard Evidence Available | Status |
|---|---|---|---|
| §164.308(a)(1) — Security Management Process | Risk Analysis (R) | Partial — asset inventory and vulnerability posture as inputs to risk analysis | External documentation required |
| §164.308(a)(1) — Security Management Process | Sanction Policy (R) | None | External documentation required |
| §164.308(a)(1) — Security Management Process | Information System Activity Review (R) | `liongard_detection` change log; `liongard_alert` alerts | **Liongard-evidenced** |
| §164.308(a)(3) — Workforce Security | Workforce Clearance Procedure (A) | Inactive account identification | **Liongard-evidenced** |
| §164.308(a)(3) — Workforce Security | Termination Procedures (A) | Disabled accounts, stale credentials | **Liongard-evidenced** |
| §164.308(a)(4) — Access Management | Access Authorization (R) | Privileged identity list | **Liongard-evidenced** |
| §164.308(a)(4) — Access Management | Access Establishment / Modification (A) | Change detection on role assignments | **Liongard-evidenced** |
| §164.308(a)(5) — Security Awareness | Security Reminders (A) | KnowBe4 training completion (if deployed) | **Liongard-evidenced (if connected)** |
| §164.308(a)(5) — Security Awareness | Protection from Malicious Software (A) | EDR coverage via `all-edrs.md` | **Liongard-evidenced** |
| §164.308(a)(5) — Security Awareness | Log-In Monitoring (A) | `liongard_alert` + `liongard_detection` | **Liongard-evidenced** |
| §164.308(a)(5) — Security Awareness | Password Management (A) | AD/M365 password policy metrics | **Liongard-evidenced** |
| §164.308(a)(7) — Contingency Plan | Data Backup Plan (R) | Backup recency via backup inspector | **Liongard-evidenced** |
| §164.308(a)(7) — Contingency Plan | Disaster Recovery Plan (R) | Backup job success rate | Partial — policy documentation required |
| §164.308(a)(7) — Contingency Plan | Testing and Revision (A) | Backup test timestamps | **Liongard-evidenced (where inspectors expose)** |

*(R) = Required; (A) = Addressable — must implement or document equivalent alternative.*

---

### Physical Safeguards (§164.310) — Liongard-evidenced subset

| Standard | Implementation Specification | Liongard Evidence Available |
|---|---|---|
| §164.310(d)(1) — Device and Media Controls | Disposal (R) | Device inventory for decommission tracking | Partial |
| §164.310(d)(1) — Device and Media Controls | Media Re-use (R) | Device inventory | Partial |
| §164.310(d)(1) — Device and Media Controls | Accountability (A) | `liongard_device` serial/asset inventory | **Liongard-evidenced** |

Physical safeguards (facility access controls, workstation physical security)
require on-site verification or access control systems — outside Liongard scope.

---

### Technical Safeguards (§164.312) — primary Liongard evidence domain

| Standard | Implementation Specification | Liongard Evidence Available |
|---|---|---|
| §164.312(a)(1) — Access Control | Unique User Identification (R) | `liongard_identity` — unique users per system | **Liongard-evidenced** |
| §164.312(a)(1) — Access Control | Emergency Access Procedure (R) | None | External documentation required |
| §164.312(a)(1) — Access Control | Automatic Logoff (A) | Screen-lock policy (Windows / AD Group Policy) | **Liongard-evidenced (where metric available)** |
| §164.312(a)(1) — Access Control | Encryption/Decryption (A) | BitLocker (Windows), FileVault (macOS) | **Liongard-evidenced** |
| §164.312(b) — Audit Controls | Audit Controls (R) | `liongard_detection` change log + `liongard_alert` | **Liongard-evidenced** |
| §164.312(c)(1) — Integrity | ePHI Integrity Controls (R) | Backup integrity (backup inspector success state) | Partial |
| §164.312(c)(2) — Integrity | Transmission Integrity (A) | TLS/SSL certificate health (TLS inspector) | **Liongard-evidenced** |
| §164.312(d) — Person/Entity Authentication | Authentication (R) | MFA state (`liongard_identity`), AD policy, M365 MFA | **Liongard-evidenced** |
| §164.312(e)(1) — Transmission Security | Transmission Security (R) | TLS inspection, firewall rules | **Liongard-evidenced** |
| §164.312(e)(2) — Transmission Security | Encryption (A) | TLS certificate versions, firewall TLS inspection | **Liongard-evidenced** |

---

## Workflow

### Step 1 — Scope discovery & ePHI system identification

```
liongard_environment LIST
  environmentId=<ENV_ID>
```

```
liongard_launchpoint LIST
  environmentId=<ENV_ID>
  fields=["id", "system", "inspector", "latestInspectionDate", "status"]
```

Build a scope inventory. Identify which systems are in the ePHI boundary:
- All EHR / EMR integration systems (if connected via Liongard)
- Windows Server / Windows Workstation systems that access ePHI
- Identity systems (AD, M365, GWS, Duo, JumpCloud) that authenticate ePHI-
  system access
- Network systems (firewalls, VPN, switches) forming the ePHI network boundary
- Backup systems backing up ePHI servers
- Email systems (M365, GWS) if ePHI is transmitted via email

If `hipaa_scope.phi_systems` is populated in the customization block, filter
to only those systems. Otherwise, assess all discovered systems.

---

### Step 2 — Inspection timeline: confirm data freshness

```
liongard_timeline GET
  environmentId=<ENV_ID>
```

Confirm all in-scope systems have inspections within
`slas.inspector_lastseen_days_max` days. Flag stale inspectors in the
manual-verification appendix.

---

### Step 3 — Identity & access control evidence (§164.312(a)(1), §164.312(d))

**Total identity count (deduplicated):**

```
liongard_identity COUNT
  environmentId=<ENV_ID>
```

**Identities without MFA (§164.312(d) — Person/Entity Authentication):**

```
liongard_identity COUNT
  environmentId=<ENV_ID>
  mfaStatus="NO"
  enabled=true
```

Flag any enabled identities with `mfaStatus="NO"`. HIPAA does not explicitly
mandate MFA by name in the original rule text, but it is required to meet the
authentication standard (§164.312(d)) under current OCR guidance and the 2025
NPRM. MFA is also required by most cyber-insurance carriers serving healthcare.

**Privileged identities (access control — §164.308(a)(4)):**

```
liongard_identity LIST
  environmentId=<ENV_ID>
  privileged=true
  enabled=true
  fields=["email", "firstName", "lastName", "inspectors", "mfaStatus", "mfaMethod"]
```

Review the privileged identity list. Each privileged account that accesses
ePHI systems must have a documented access authorization (§164.308(a)(4)(i)).

**Inactive accounts (§164.308(a)(3) — Workforce clearance):**

```
liongard_identity LIST
  environmentId=<ENV_ID>
  inventoryState="INACTIVE"
  enabled=true
```

Any active account not used in more than `slas.account_inactive_days_max` days
is an access control risk. Disabled/terminated user accounts with residual
access are a common OCR finding.

---

### Step 4 — Endpoint encryption evidence (§164.312(a)(1)(ii)(d) — encryption/decryption)

Chain `recipes/single-system-analysis/by-inspector/windows-workstation.md`
and `recipes/single-system-analysis/by-inspector/windows-server.md` for
BitLocker encryption status:

```
liongard_metric EVALUATE
  jmesPathQuery="Disks[?Encrypted == `false`].{drive: DriveLetter, name: DeviceName}"
  systemId=<WINDOWS_SYSTEM_ID> environmentId=<ENV_ID>
```

For macOS: chain `macos.md` for FileVault status.

Flag all unencrypted drives on systems that store or access ePHI. Encryption
at rest is an addressable specification — if not implemented, document the
equivalent safeguard and rationale.

---

### Step 5 — Patch and malware protection evidence (§164.308(a)(5))

**Patch currency (§164.308(a)(5)(ii)(B)):**

Chain `recipes/system-type-assessment/all-windows-patching.md` for patch
age across Windows systems.

**EDR / AV coverage (§164.308(a)(5)(ii)(B)):**

Chain `recipes/system-type-assessment/all-edrs.md` for endpoint protection
coverage across all endpoint-class systems in the ePHI boundary.

Coverage below `slas.edr_coverage_pct_min` (inherited from cyber-insurance
recipe SLA) is a HIPAA risk. Document unprotected ePHI-system endpoints
in the gap tracker.

**Security awareness training (§164.308(a)(5)(i)):**

If KnowBe4 is deployed, chain
`recipes/single-system-analysis/by-inspector/knowbe4.md` for training
completion rates. Document any users with outstanding or overdue training.

---

### Step 6 — Backup and contingency plan evidence (§164.308(a)(7))

Chain `recipes/system-type-assessment/all-backups.md` for:
- Most recent successful backup per ePHI server
- Backup job failure rate
- Backup test recency

Flag any ePHI server with no successful backup in the last
`slas.backup_rpo_days_max` day(s) as a critical HIPAA gap.
The 2025 NPRM proposes a 72-hour restoration requirement for ePHI systems —
flag any backup that does not meet this RPO.

---

### Step 7 — Audit controls & change detection (§164.312(b))

```
liongard_detection LIST
  environmentId=<ENV_ID>
  startDate=<REVIEW_WINDOW_START>
  endDate=<REVIEW_WINDOW_END>
```

```
liongard_alert LIST
  environmentId=<ENV_ID>
  startDate=<REVIEW_WINDOW_START>
```

Surface material changes and active alerts as the audit-activity review
required by §164.312(b). A complete change log confirms the organization
has the capability to review activity — a key OCR audit question.

---

### Step 8 — Transmission security (§164.312(e))

Chain `recipes/single-system-analysis/by-inspector/tls-ssl.md` for:
- Certificate expiration dates (expired = transmission gap)
- TLS version (TLS 1.0 / 1.1 = insecure transmission)
- Self-signed certificates (no chain of trust)

Minimum TLS version for ePHI transmission is `slas.tls_min_version` (TLS 1.2;
TLS 1.3 preferred). Flag all certificates using deprecated versions.

Also check firewall TLS inspection settings for ePHI-boundary firewalls
(chain the appropriate firewall single-system recipe).

---

### Step 9 — Network segmentation (§164.312(a)(1))

Network segmentation is an addressable specification under Access Control.
Chain `recipes/system-type-assessment/all-firewalls.md` to confirm:
- ePHI network segments are firewalled from general corporate network
- Remote access to ePHI systems requires VPN or equivalent
- WAN-exposed management interfaces are not directly accessible

---

### Step 10 — QA pass & manual-verification appendix

Apply the QA retry pattern (`reference/qa-retry-pattern.md`).

Build the **Manual verification** appendix — items the MSP must confirm
by hand before presenting the assessment to the customer or regulatory body:

| Item | HIPAA Reference | Action |
|---|---|---|
| Risk analysis documentation | §164.308(a)(1)(ii)(A) — Required | Obtain and review the covered entity's written risk analysis |
| Business Associate Agreements | §164.308(b)(1) — Required | Confirm executed BAA with all ePHI-accessing vendors |
| Workforce training records | §164.308(a)(5)(i) — Required | Confirm all workforce members completed annual HIPAA training |
| Contingency plan documentation | §164.308(a)(7)(i) — Required | Review written disaster recovery and emergency mode plans |
| Emergency access procedure | §164.312(a)(2)(ii) — Required | Document procedure for ePHI access during system emergency |
| Physical access controls | §164.310(a)(1) — Required | Verify facility access logs and workstation physical security |
| Unencrypted drive found | §164.312(a)(2)(iv) Addressable | Confirm the unencrypted system does not store/access ePHI; if it does, encrypt or document equivalent safeguard |
| MFA not enabled on ePHI user | §164.312(d) Required | Remediate; document interim compensating control |

---

## Insights & recommendations

| Condition | Finding | Recommendation |
|---|---|---|
| Any enabled ePHI-system identity with `mfaStatus="NO"` | **Authentication gap — [N] users without MFA** | Enforce MFA on all accounts that access ePHI systems. Priority: admin + remote-access users. Aligns with §164.312(d) and OCR guidance. |
| Unencrypted drive on ePHI system | **Encryption gap — [N] unencrypted drives** | Enable BitLocker (Windows) or FileVault (macOS) on all ePHI-storing devices. §164.312(a)(2)(iv) addressable — document or implement. |
| Backup failure or RPO > `slas.backup_rpo_days_max` day | **Backup gap — [system] has no recent valid backup** | Restore from most recent backup; investigate failure; verify backup monitoring. §164.308(a)(7)(ii)(A) required. |
| EDR not covering all ePHI endpoints | **Malware protection gap — [N] endpoints uncovered** | Deploy EDR on all ePHI-class endpoints. §164.308(a)(5)(ii)(B) addressable. |
| TLS 1.0 or 1.1 certificate found | **Insecure transmission** | Upgrade TLS to 1.2 minimum on all ePHI-transmitting services. §164.312(e)(2)(ii). |
| Expired TLS certificate | **Certificate expired — [domain]** | Renew immediately; expired cert may disable ePHI transmission or generate browser warnings. |
| Inactive enabled accounts | **Access risk — [N] inactive accounts still enabled** | Disable or remove accounts inactive > `slas.account_inactive_days_max` days. §164.308(a)(3)(ii)(B). |
| No KnowBe4 or training data | **Training evidence gap** | Confirm security awareness training program; obtain completion records for OCR evidence. §164.308(a)(5) required. |
| No change-detection activity available | **Audit trail gap** | Ensure Liongard inspection cadence captures change events; supplement with SIEM/log management for continuous audit capability. §164.312(b) required. |

---

## Coverage cross-check

| Source | Coverage notes |
|---|---|
| Partner QA matrix | HIPAA not directly in partner audit. Controls mapped to the equivalent onboarding-QA fields: identity/MFA, EDR, patch, backup, TLS, privileged access. |
| CIS Controls v8.1 | HIPAA Security Rule aligns strongly with CIS Controls: CIS 3 (data protection — encryption), CIS 5 (account management — access control), CIS 6 (access control management — MFA), CIS 9 (email/browser — transmission), CIS 10 (malware — EDR), CIS 11 (data recovery — backup), CIS 16 (application software security — patch). |
| Cyber-insurance domain files | HIPAA evidence feeds and overlaps with `domains/auth.md` (MFA), `domains/endpoint.md` (EDR + encryption), `domains/backup.md` (contingency plan), `domains/network.md` (transmission security). Run cyber-insurance readiness alongside HIPAA for healthcare customers. |
| QBR recipe | Chain this recipe in QBR Step 8 for healthcare customers with "HIPAA Compliance Evidence" as a standing QBR section. Surface any new gaps or gap closures in the review period. |

---

## Policy / external documentation required

The following HIPAA Security Rule standards cannot be evidenced by Liongard
and require external documentation from the covered entity or business associate:

- **Written Risk Analysis** (§164.308(a)(1)(ii)(A)) — annual or when significant change occurs
- **Sanction Policy** (§164.308(a)(1)(ii)(C)) — workforce consequences for policy violations
- **Workforce Training Records** (§164.308(a)(5)(i)) — annual training completion records
- **Business Associate Agreements** (§164.308(b)(1)) — executed BAAs with all ePHI vendors
- **Contingency Plan — Disaster Recovery and Emergency Mode** (§164.308(a)(7)) — written plans
- **Facility Access Controls** (§164.310(a)(1)) — physical security policies and access logs
- **Workstation Physical Security** (§164.310(c)) — workstation placement and use policies
- **Emergency Access Procedure** (§164.312(a)(2)(ii)) — documented emergency access process
- **Breach Notification Policy** (§164.400–414) — Breach Notification Rule (separate from Security Rule)

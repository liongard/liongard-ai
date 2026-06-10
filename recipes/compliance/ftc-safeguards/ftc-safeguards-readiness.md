---
name: ftc-safeguards-readiness
description: >
  Use this skill when the user wants an FTC Safeguards Rule (16 CFR Part 314)
  readiness assessment, information security program gap analysis, GLBA
  Safeguards Rule compliance evidence, or a Written Information Security
  Program (WISP) technical evidence pack for a financial institution customer.
  Trigger phrases: "FTC Safeguards Rule assessment", "GLBA Safeguards
  compliance", "Safeguards Rule readiness", "16 CFR 314 evidence",
  "Written Information Security Program audit", "WISP evidence", "financial
  institution security assessment", "non-bank financial institution security",
  "mortgage company security review", "auto dealer security assessment",
  "tax preparer security posture", "accounting firm GLBA compliance",
  "Safeguards Rule gap analysis". Two output modes in one recipe: TAM/SOC
  technical checklist and vCIO executive summary. Maps to the 9 core program
  elements under §314.4.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_launchpoint, liongard_timeline, liongard_cyber_risk_dashboard, liongard_identity, liongard_device, liongard_domain, liongard_metric, liongard_detection, liongard_alert"
personas: [vcio-account-manager, technical-alignment-manager, soc, executive]
output_formats: [word, xlsx, markdown]
primitives: []
composes:
  - recipe:single-system:single-system-active-directory
  - recipe:system-type:system-type-windows-patching
---

# FTC Safeguards Rule Readiness — Master Recipe

> **The canonical FTC Safeguards Rule compliance evidence recipe.** Maps
> Liongard data to the nine core elements of a Written Information Security
> Program (WISP) required by the FTC Safeguards Rule (16 CFR Part 314,
> implemented under the Gramm-Leach-Bliley Act, 15 U.S.C. §6801 et seq.).
>
> **Who this applies to:** Financial institutions under FTC jurisdiction —
> companies engaged in financial activities that are not regulated by another
> federal agency (OCC, Federal Reserve, FDIC, NCUA, SEC, CFTC). Commonly
> includes: mortgage lenders and brokers, auto dealers that arrange financing,
> payday lenders, check cashers, finance companies, tax preparers, financial
> advisors and planners (non-SEC registered), collection agencies,
> accountants providing financial services, retailers that extend credit, and
> non-federally-insured credit unions. **When in doubt, confirm covered-entity
> status with the customer's legal counsel.**
>
> **MSP relevance — two angles:**
> (1) MSPs serving covered financial institutions must help those customers
>     comply; this recipe generates the technical evidence the customer needs
>     for their WISP.
> (2) MSPs themselves may be "service providers" subject to oversight under
>     §314.4(f) — the covered entity is required to oversee the security of
>     their service providers (including their MSP). This recipe also supports
>     MSP compliance when the MSP is acting as a service provider to a
>     covered financial institution.
>
> **Small company exemption (§314.1(b)):** Covered entities that maintain
> customer financial information for fewer than 5,000 consumers are exempt
> from: penetration testing, vulnerability scanning, audit trails, encryption,
> MFA, access controls based on need-to-know, security awareness training,
> incident response plan, and annual board reporting. The recipe notes
> which elements carry the small-company exemption. Set
> `safeguards_scope.small_company_exempt: true` in the customization block to
> suppress those elements from the output.
>
> **Two output modes:**
> - `audience.mode: "technical"` → TAM/SOC technical gap checklist with
>   per-control VALIDATED / GAP / not in dataprint status and exact JMESPath evidence.
> - `audience.mode: "executive"` → vCIO executive summary with traffic-light
>   status per program element, top-5 findings, and a remediation roadmap.
>
> **References:** `reference/cross-cutting-signals.md`,
> `reference/asset-fields.md`, `reference/qa-retry-pattern.md`,
> `reference/inspector-aliases.md`, `reference/personas-recipe-matrix.md`.
> FTC rule text: 16 CFR Part 314 (https://www.ecfr.gov/current/title-16/part-314).
> FTC Safeguards Rule guidance: https://www.ftc.gov/legal-library/browse/rules/safeguards-rule.

---

## Customize for your MSP

```yaml
output:
  format: word                          # word | xlsx | markdown
                                        # word for the readiness narrative or executive summary;
                                        # xlsx for the technical evidence workbook;
                                        # markdown for working drafts.
  filename: "<customer>-FTC-Safeguards-Readiness-<YYYY-MM-DD>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  cover: "FTC Safeguards Rule — Information Security Program Assessment"
  executive_summary: "Executive Summary"
  entity_classification: "Covered Entity Classification"
  wisp_summary: "Written Information Security Program Summary"
  element_01_qi: "Element 1 — Qualified Individual"
  element_02_risk: "Element 2 — Risk Assessment"
  element_03_safeguards: "Element 3 — Safeguards & Controls"
  element_04_testing: "Element 4 — Regular Testing & Monitoring"
  element_05_vendors: "Element 5 — Service Provider Oversight"
  element_06_data_minimization: "Element 6 — Data Minimization & Disposal"
  element_07_incident_response: "Element 7 — Incident Response Plan"
  element_08_board_report: "Element 8 — Qualified Individual Annual Report"
  gap_tracker: "Gap Remediation Tracker"
  external_documentation: "Program Documentation Required"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Manual Verification"
  appendix: "Appendix — Methodology"

audience:
  mode: "both"                          # technical | executive | both
                                        # technical = TAM/SOC gap checklist with evidence paths
                                        # executive = vCIO traffic-light summary + remediation roadmap
                                        # both = technical findings with executive summary section
  tone: "balanced"
  reading_level: "manager"

safeguards_scope:
  small_company_exempt: false           # true if customer processes < 5,000 consumers
                                        # exempts: pen testing, vuln scanning, audit trails,
                                        # encryption, MFA, access controls, training,
                                        # incident response plan, annual board report
  customer_info_types: []               # list of customer information types in scope
                                        # e.g. ["SSN", "credit card", "bank account",
                                        #        "tax records", "mortgage documents"]
  in_scope_systems: []                  # leave empty for all discovered systems;
                                        # or list inspector slugs limiting the assessment scope

slas:
  mfa_coverage_pct_min: 100             # §314.4(c)(4) — MFA for all customer-info system access
  patch_age_days_max: 30                # §314.4(c)(8) — vulnerability management
  access_key_age_days_max: 90           # §314.4(c)(6) — change management / key rotation
  account_inactive_days_max: 60         # §314.4(c)(1) — access control
  password_min_length: 12               # §314.4(c)(1) — access control best practice
  tls_min_version: "1.2"               # §314.4(c)(2) — encryption in transit
  inspector_lastseen_days_max: 7
  license_expiration_warn_days: 30
  pen_test_max_age_months: 12           # §314.4(c)(7) — annual penetration testing
                                        # (not required if small_company_exempt: true)
  vuln_scan_max_age_months: 3           # §314.4(c)(7) — quarterly vulnerability assessments
                                        # (not required if small_company_exempt: true)

naming:
  client_term: "Client"
  environment_term: "Environment"
  customer_info_term: "Customer Financial Information"

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

- **Annual WISP review** — technical evidence gathering for the covered entity's
  required annual information security program review.
- **New customer onboarding** — baseline Safeguards Rule posture assessment
  before formalizing an MSP engagement with a financial institution.
- **Service provider questionnaire response** — when a covered-entity client
  asks their MSP to demonstrate compliance with §314.4(f) service-provider
  requirements.
- **Regulatory examination preparation** — FTC or state regulator examination
  requires the covered entity to produce their WISP and demonstrate it is
  operational. This recipe produces the technical evidence appendix.
- **Cyber-insurance for financial institutions** — Safeguards Rule compliance
  is increasingly required or premium-discounted by carriers serving financial
  institutions. Run alongside the cyber-insurance readiness recipe.

---

## The 9 WISP Elements — control mapping

### Element 1 — Qualified Individual (§314.4(a))

**Requirement:** Designate a Qualified Individual (QI) responsible for
overseeing, implementing, and enforcing the information security program.
The QI may be in-house or a third-party service provider (the MSP).

**Liongard evidence:** None — personnel/role designation is a governance
and HR matter. The MSP may be the designated QI; if so, document that
designation.

**Status:** External documentation required. Confirm in the manual-
verification appendix: who is the designated QI, their title/role, and date
of designation.

**Small-company exemption:** Not exempt — all covered entities must designate a QI.

---

### Element 2 — Risk Assessment (§314.4(b))

**Requirement:** Conduct and document a risk assessment identifying
reasonably foreseeable threats to the security, confidentiality, and
integrity of customer information; likelihood and potential damage; and
sufficiency of existing safeguards.

**Liongard evidence:** Partial — Liongard provides technical inputs to the
risk assessment:

```
liongard_cyber_risk_dashboard GET
  environmentId=<ENV_ID>
```

The cyber risk dashboard provides pre-aggregated category scores (EDR
coverage, MFA coverage, patch currency, backup recency) that serve as
quantitative inputs to the risk assessment. Surfacing these numbers in the
customer's risk analysis satisfies the "sufficiency of existing safeguards"
component.

**Status:** External documentation required for the full risk analysis
document. Liongard data is a supporting input, not a substitute.

**Small-company exemption:** Not exempt — risk assessment is required of all
covered entities.

---

### Element 3 — Safeguards to Control Identified Risks (§314.4(c))

This is the primary technical-control element. The rule specifies eight
categories of safeguards. Each is assessed below.

#### §314.4(c)(1) — Access Controls

*Limit who can access customer information; control who is authorized.*

**Access control evidence:**

Reconciled identity inventory:

```
liongard_identity COUNT
  environmentId=<ENV_ID>
```

Users without MFA on customer-information systems (small-company
exemption applies):

```
liongard_identity COUNT
  environmentId=<ENV_ID>
  mfaStatus="NO"
  enabled=true
```

Privileged users with access to customer information systems:

```
liongard_identity LIST
  environmentId=<ENV_ID>
  privileged=true
  enabled=true
  fields=["email", "firstName", "lastName", "inspectors", "mfaStatus"]
```

Inactive enabled accounts (access should be revoked on departure / inactivity):

```
liongard_identity LIST
  environmentId=<ENV_ID>
  inventoryState="INACTIVE"
  enabled=true
```

AD password policy (minimum length, complexity, history):

Chain `recipes/single-system-analysis/by-inspector/active-directory.md`
Step 4 for password policy metrics.

Flag: inactive enabled accounts; privileged accounts without MFA; accounts
with no recorded authentication inspector.

#### §314.4(c)(2) — Encryption (small-company exemption applies)

*Encrypt customer information in transit and at rest.*

Encryption at rest — chain `windows-workstation.md` and `windows-server.md`
for BitLocker status on customer-information-storing devices. Chain
`macos.md` for FileVault status.

Encryption in transit — chain `tls-ssl.md` for TLS certificate versions and
expiration dates. Flag TLS versions below `slas.tls_min_version`.

#### §314.4(c)(3) — Secure Development Practices

*Adopt secure development practices for in-house developed applications.*

**Liongard evidence:** None — software development practices are outside
Liongard's inspection scope. Document the customer's secure development
policy or confirm it is not applicable (customer does not develop software).

#### §314.4(c)(4) — Multi-Factor Authentication (small-company exemption applies)

*Require MFA for anyone accessing customer information systems — including
remote access.*

This is the most commonly tested Safeguards Rule control post-2023. The rule
requires MFA unless the covered entity's QI approves a reasonably equivalent
alternative in writing.

```
liongard_identity COUNT
  environmentId=<ENV_ID>
  mfaStatus="NO"
  enabled=true
```

Also check remote-access MFA specifically — VPN and remote-desktop:
chain `all-firewalls.md` and `all-rmm-platforms.md` for VPN/RDP MFA
enforcement settings where available.

Flag: any enabled identity accessing customer-information systems without
MFA. Zero tolerance — the rule does not provide a grace period; the QI must
approve a written equivalent before the assessment date.

#### §314.4(c)(5) — Secure Disposal

*Dispose of customer information securely when no longer needed.*

**Liongard evidence:** Partial — `liongard_device` device inventory provides
the asset register needed to track decommissioned devices.

```
liongard_device LIST
  environmentId=<ENV_ID>
  inventoryState="INACTIVE"
  fields=["hostname", "serialNumber", "manufacturer", "model", "lastSeen", "inspectors"]
```

Devices with `inventoryState=INACTIVE` and no recent inspection may be
decommissioned — confirm data was securely wiped. Document wipe confirmation
in the manual-verification appendix.

#### §314.4(c)(6) — Change Management

*Implement policies and procedures for change management (adds, changes,
deletions to systems/applications/data).*

```
liongard_detection LIST
  environmentId=<ENV_ID>
  startDate=<REVIEW_WINDOW_START>
```

The Liongard change-detection log demonstrates that changes to in-scope
systems are captured and observable. Surface the change log as evidence of
change-awareness capability.

Flag: periods with no detection activity on in-scope systems may indicate
the inspector is not running or the change log is not being reviewed.

#### §314.4(c)(7) — Regular Testing & Monitoring (small-company exemption applies)

*Test and monitor the effectiveness of key controls, systems, and procedures.
Annually: penetration testing. Quarterly: vulnerability assessments. OR
continuous monitoring as an equivalent.*

**Liongard evidence (continuous monitoring component):**

```
liongard_timeline GET
  environmentId=<ENV_ID>
```

Liongard's inspection cadence (typically daily or weekly per system) provides
continuous visibility into configuration state — evidence of ongoing monitoring.

**Penetration testing and vulnerability scanning** are external services not
performed by Liongard. Confirm the customer has:
- Annual penetration test results (within `slas.pen_test_max_age_months` months)
- Quarterly vulnerability scan results (within `slas.vuln_scan_max_age_months` months)

Document in the manual-verification appendix.

#### §314.4(c)(8) — Vulnerability Management

*Monitor, evaluate, and address security vulnerabilities.*

Chain `recipes/system-type-assessment/all-windows-patching.md` for Windows
patch currency. Flag any systems with patches older than
`slas.patch_age_days_max` days.

Chain `all-edrs.md` for EDR coverage — EDR is the primary real-time
vulnerability response tool.

```
liongard_alert LIST
  environmentId=<ENV_ID>
  startDate=<REVIEW_WINDOW_START>
```

Active alerts are the vulnerability management signal — surface unresolved
alerts as open vulnerability management items.

---

### Element 4 — Regular Testing & Monitoring (§314.4(d))

Covered by §314.4(c)(7) above. The element-level requirement is to
*regularly test or monitor* the effectiveness of safeguards, key controls,
systems, and procedures. Liongard's continuous inspection cadence satisfies
the "monitoring" component; penetration testing and vulnerability scanning
are the "testing" components.

---

### Element 5 — Service Provider Oversight (§314.4(f))

**Requirement:** Select and retain service providers that maintain
appropriate safeguards; require service providers by contract to implement
appropriate safeguards.

**Liongard evidence:** Partial — list of connected inspectors provides a
roster of technology service providers with Liongard visibility.

```
liongard_launchpoint LIST
  environmentId=<ENV_ID>
  fields=["inspector", "system", "latestInspectionDate", "status"]
```

This inspector list is the starting point for the vendor inventory. Not all
vendors will have Liongard inspectors — supplement with the customer's
vendor register.

**Status:** External documentation required for executed service-provider
agreements with appropriate safeguards clauses. The vendor inventory from
Liongard is a supporting input.

---

### Element 6 — Data Minimization & Disposal (§314.4(e))

**Requirement:** Collect only necessary customer information and retain it
only as long as necessary; securely dispose of data no longer needed.

**Liongard evidence:**

Device inventory for decommission tracking (see §314.4(c)(5) above).

Inactive cloud storage that may hold customer data:
Chain `all-cloud-storage.md` for Box, Dropbox, and Google Drive — confirm
stale/archived shared drives do not retain customer financial information.

**Status:** External documentation required for the data retention and
disposal policy.

---

### Element 7 — Incident Response Plan (§314.4(h); small-company exemption applies)

**Requirement:** Establish a written incident response plan addressing:
goals, internal processes for responding to security events, roles/responsibilities,
external communications, remediation, documentation, and post-incident review.

Additionally: covered entities must notify the FTC within 30 days of
discovering a notification event involving 500+ consumers (§314.5 — effective
May 2024 breach notification amendment).

**Liongard evidence:** None — incident response plan is a written governance
document. Liongard's change-detection and alert system can be cited as the
*detection capability* that feeds incident response, but the plan itself
requires external documentation.

**Status:** External documentation required. Confirm existence of a written
IRP in the manual-verification appendix. For MSPs: confirm the MSP's own IRP
covers the customer's customer-information systems.

---

### Element 8 — Qualified Individual Annual Report (§314.4(i); small-company exemption applies)

**Requirement:** The QI must report to the board of directors (or senior
officer at companies without a board) at least annually on the information
security program — including risk assessment, program changes, compliance
test results, security events, and any management recommendations.

**Liongard evidence:** This recipe and its outputs serve as the technical
annex to the QI's annual report. The executive-summary output (`audience.mode:
"executive"`) is formatted for direct delivery to the board or senior officer.

---

## Workflow

### Step 1 — Scope discovery

```
liongard_environment LIST environmentId=<ENV_ID>
```

```
liongard_launchpoint LIST
  environmentId=<ENV_ID>
  fields=["id", "system", "inspector", "latestInspectionDate", "status"]
```

Build the in-scope system inventory. If `safeguards_scope.in_scope_systems`
is populated, filter accordingly.

---

### Step 2 — Inspection timeline

```
liongard_timeline GET environmentId=<ENV_ID>
```

Confirm inspection currency. Flag stale systems for the manual-verification
appendix.

---

### Step 3 — Access control & MFA evidence (§314.4(c)(1) and §314.4(c)(4))

Run the identity queries from Element 3 §(c)(1) and §(c)(4) above.

Also run the cyber risk dashboard for category-level MFA score:

```
liongard_cyber_risk_dashboard GET environmentId=<ENV_ID>
```

---

### Step 4 — Encryption evidence (§314.4(c)(2))

Chain endpoint encryption recipes (windows-workstation, windows-server,
macos) and TLS inspector for at-rest and in-transit encryption state.

---

### Step 5 — Patch & vulnerability management (§314.4(c)(8))

Chain `all-windows-patching.md` and `all-edrs.md`.

---

### Step 6 — Change detection & monitoring evidence (§314.4(c)(6), §314.4(c)(7))

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

---

### Step 7 — Vendor inventory (§314.4(f))

```
liongard_launchpoint LIST
  environmentId=<ENV_ID>
  fields=["inspector", "system", "latestInspectionDate"]
```

Surface the inspector list as the Liongard-visible portion of the vendor/
service-provider inventory.

---

### Step 8 — QA pass & manual-verification appendix

Apply the QA retry pattern (`reference/qa-retry-pattern.md`).

Build the **Manual verification** appendix:

| Item | Rule Reference | Action |
|---|---|---|
| QI designation document | §314.4(a) | Confirm named QI, role, and date |
| Written risk analysis | §314.4(b) | Obtain and review the WISP risk analysis document |
| MFA alternative approval | §314.4(c)(4) | If any user lacks MFA, confirm written QI approval of equivalent |
| Penetration test results | §314.4(c)(7) | Confirm annual pen test within `slas.pen_test_max_age_months` months |
| Vulnerability scan results | §314.4(c)(7) | Confirm quarterly scans within `slas.vuln_scan_max_age_months` months |
| Service provider contracts | §314.4(f) | Confirm executed agreements with safeguards clause |
| Data retention / disposal policy | §314.4(e) | Review written policy |
| Incident response plan | §314.4(h) | Confirm written IRP exists and is current |
| Annual board report | §314.4(i) | Confirm QI annual report was delivered; obtain prior year report |
| Breach notification capability | §314.5 | Confirm 30-day FTC notification process is documented |

---

## Output modes

### Technical output (TAM/SOC gap checklist)

When `audience.mode: "technical"`, produce a per-control table:

| Control | Rule Reference | Status | Evidence | Gap |
|---|---|---|---|---|
| MFA for all users | §314.4(c)(4) | 🔴 GAP / ✅ MET | `liongard_identity COUNT mfaStatus=NO` = N | N users need MFA |
| BitLocker on all devices | §314.4(c)(2) | ✅ MET / 🟡 PARTIAL | N of M devices encrypted | 2 workstations unencrypted |
| ... | ... | ... | ... | ... |

### Executive output (vCIO board-ready summary)

When `audience.mode: "executive"`, produce:

1. **Program status summary** — traffic-light per element (Green/Amber/Red)
2. **Top findings** — top 5 gaps in business-impact priority order
3. **Remediation roadmap** — prioritized action plan with estimated effort
   and projected compliance date
4. **Liongard monitoring statement** — one-paragraph description of ongoing
   monitoring capability as evidence of §314.4(c)(7) continuous monitoring

---

## Insights & recommendations

| Condition | Finding | Recommendation |
|---|---|---|
| Any enabled identity with `mfaStatus="NO"` | **Critical — MFA gap ([N] users)** | Enforce MFA on all accounts immediately. §314.4(c)(4) has no grace period; non-compliance is an active violation. |
| Unencrypted device storing customer information | **Encryption gap** | Enable BitLocker/FileVault. §314.4(c)(2). |
| Patch age > `slas.patch_age_days_max` days | **Vulnerability management gap** | Accelerate patch deployment. §314.4(c)(8). |
| No written IRP | **Incident response gap** | Create or obtain a written IRP. §314.4(h) required (not exempt for small companies in the original rule — check current rule text). |
| No penetration test within `slas.pen_test_max_age_months` months | **Testing gap** | Schedule annual penetration test. §314.4(c)(7) (exempt if small-company). |
| Inactive enabled accounts > threshold | **Access control gap — [N] stale accounts** | Disable accounts inactive > `slas.account_inactive_days_max` days. §314.4(c)(1). |
| No service-provider agreements with safeguards clauses | **Vendor management gap** | Update MSA/vendor agreements to include GLBA Safeguards clause. §314.4(f). |
| No QI designation document | **Program governance gap** | Formally designate a QI in writing. §314.4(a) — required of all covered entities including small companies. |
| No written risk analysis | **Risk assessment gap** | Conduct and document a risk analysis. §314.4(b) required. |

---

## Coverage cross-check

| Source | Coverage notes |
|---|---|
| Partner QA matrix | FTC Safeguards not in partner audit. Controls map to the same onboarding-QA fields as cyber-insurance: identity/MFA, EDR, patch, backup, TLS. |
| CIS Controls v8.1 | Safeguards Rule §314.4(c) maps closely to CIS Controls: CIS 5 (account management — §(c)(1)), CIS 6 (access control — MFA §(c)(4)), CIS 3 (data protection — encryption §(c)(2)), CIS 7 (continuous monitoring — §(c)(7)), CIS 10 (malware defense — §(c)(8)), CIS 16 (patch management — §(c)(8)). |
| Cyber-insurance domain files | Strong overlap — run cyber-insurance readiness alongside this recipe for financial institution customers. Feeds `domains/auth.md` (MFA), `domains/endpoint.md` (encryption + EDR), `domains/network.md` (transmission security), `domains/governance.md` (access control, vendor management). |
| QBR recipe | Chain this recipe in QBR Step 8 for financial institution customers. Surface WISP element status (with changes since last review) as a standing QBR compliance section. The executive output doubles as a QBR compliance slide. |

---

## Policy / external documentation required

The following Safeguards Rule elements cannot be evidenced by Liongard and
require external documentation from the covered entity:

- **Written WISP document** (§314.2) — the formal information security program document
- **Qualified Individual designation** (§314.4(a)) — written designation with role and date
- **Written risk analysis** (§314.4(b)) — documented risk assessment
- **Service provider agreements** (§314.4(f)) — contracts with safeguards clauses
- **Data retention and disposal policy** (§314.4(e)) — written policy
- **Incident response plan** (§314.4(h)) — written IRP (small-company exempt)
- **Annual QI report to board** (§314.4(i)) — written report delivered to board/senior officer (small-company exempt)
- **Penetration test results** (§314.4(c)(7)) — external assessment (small-company exempt)
- **Vulnerability scan results** (§314.4(c)(7)) — quarterly scans or continuous monitoring documentation (small-company exempt)
- **MFA alternative approval** (§314.4(c)(4)) — written QI approval if MFA is not implemented
- **Breach notification log** (§314.5) — FTC notification within 30 days of notification event (500+ consumers)

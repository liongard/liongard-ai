---
name: cmmc-readiness
description: >
  Use this skill when the user wants a CMMC (Cybersecurity Maturity Model
  Certification) readiness assessment, Level 1 or Level 2 evidence pack,
  NIST SP 800-171 gap analysis, or a DoD-contracting-prep compliance
  workbook for a customer. Compliance variant of the cross-cutting recipe
  pattern — point-in-time evidence collection mapped to CMMC practices,
  with per-domain breakouts. Trigger phrases: "CMMC readiness", "CMMC L1
  assessment", "CMMC L2 assessment", "NIST 800-171 gap analysis",
  "DoD contracting compliance evidence", "CMMC self-assessment",
  "CMMC pre-audit", "CMMC evidence pack", "what's our CMMC posture".
  Auto-discovers deployed inspectors, chains per-class recipes, and maps
  findings to CMMC Level 1 (17 practices) and Level 2 (110 practices /
  NIST 800-171 controls). Produces an Excel CMMC evidence workbook
  (control-by-control evidence + gap tracker) and a Word readiness
  narrative.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_timeline, liongard_cyber_risk_dashboard, liongard_device, liongard_identity, liongard_domain, liongard_metric. liongard_detection and liongard_alert add audit-trail evidence for AU-family controls when available."
personas: [soc, vcio-account-manager, technical-alignment-manager, executive, sales]
output_formats: [xlsx, word, markdown]
primitives: []
composes:
  - recipe:single-system:single-system-active-directory
  - recipe:single-system:single-system-windows-server
  - recipe:single-system:single-system-windows-workstation
  - recipe:system-type:system-type-all-backups
  - recipe:system-type:system-type-all-domains
  - recipe:system-type:system-type-all-edrs
  - recipe:system-type:system-type-all-endpoints
  - recipe:system-type:system-type-all-firewalls
  - recipe:system-type:system-type-all-identity-providers
  - recipe:system-type:system-type-all-network-infrastructure
  - recipe:system-type:system-type-windows-patching
---

# CMMC Readiness — Master Recipe

> **The canonical CMMC compliance evidence-pack recipe.** Maps Liongard
> data to CMMC Level 1 and Level 2 practices (and the underlying NIST
> SP 800-171 controls for Level 2). Produces evidence for the assessor,
> a gap tracker for the path-to-certification, and an executive
> readiness summary.
>
> **Scope: technical controls.** CMMC Level 2 has 110 practices across
> 14 domains. Many controls are policy / procedural / training-driven
> and live outside Liongard's data scope. This recipe surfaces the
> Liongard-evidenced subset (predominantly AC, AT, AU, CM, IA, MA, SI,
> SC) and clearly marks the policy-driven controls as "external
> evidence required" rather than failing to surface them.
>
> **Customer-stack-adaptive.** Calls `liongard_system LIST` to discover
> deployed inspectors, then chains the appropriate per-class recipes for
> identity, endpoint, network, backup, and domain evidence. Controls
> requiring data from inspectors the customer doesn't have deployed
> are flagged as "deploy required inspector" gaps.
>
> **Two-level architecture.** The recipe defaults to Level 2 (the more
> common scope for DoD primes and subcontractors). Setting
> `cmmc_level: 1` produces the simpler Level 1 evidence pack scoped to
> the 17 Level 1 practices and FCI handling. Set `cmmc_level: "L2-and-L1"`
> for a combined pack that explicitly distinguishes both levels.
>
> **References:** `reference/cross-cutting-signals.md` (the
> cross-cutting workflow + MCP tool table), `reference/asset-fields.md`
> (the reconciled-asset-inventory tools), `reference/qa-retry-pattern.md`,
> `reference/inspector-aliases.md`,
> `reference/personas-recipe-matrix.md`,
> `domains/` (per-CMMC-domain control mappings — see below).


---

## Customize for your MSP

```yaml
output:
  format: xlsx                           # xlsx | word | markdown
                                         # Default: evidence workbook (one sheet per CMMC domain).
                                         # Use word for the readiness narrative;
                                         # markdown for working drafts.
  filename: "<customer>-CMMC-Readiness-L<level>-<date>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  cover: "CMMC Readiness Assessment"
  executive_summary: "Executive Summary"
  scope_definition: "Scope & CUI / FCI Boundaries"
  readiness_summary: "Readiness Summary by Domain"
  per_domain_evidence: "Per-Domain Evidence"            # one block per CMMC domain
  per_practice_findings: "Per-Practice Findings"        # one row per practice
  gap_tracker: "Gap Remediation Tracker"
  policy_external_evidence: "Policy / External Evidence Required"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Manual Verification"
  appendix: "Appendix — Methodology"
  verification_log: "Verification Log"

audience:
  tone: "balanced"                       # technical | balanced | executive
                                         # Default balanced — primary readers are SOC + vCIO
                                         # owning the certification path. Override to executive
                                         # for the readiness summary slide deck; technical for
                                         # engineering remediation working documents.
  reading_level: "compliance-and-technical"

cmmc_scope:
  level: 2                               # 1 | 2 | "L2-and-L1"
  certification_type: "self-assessment"  # self-assessment | C3PAO-assessed | DIBCAC-assessed
                                         # — adjusts the narrative emphasis (self-assessments
                                         # are more flexible; C3PAO / DIBCAC require stricter
                                         # evidence documentation)
  cui_handling_systems: []               # explicit list of system names handling CUI; recipe
                                         # scopes findings to these systems when populated
  fci_handling_systems: []               # explicit list of system names handling FCI (Level 1)
  asset_categorization_required: true    # Level 2 expects asset categorization (CUI Assets,
                                         # Security Protection Assets, Contractor Risk Managed
                                         # Assets, Specialized Assets, Out-of-Scope Assets)
  in_scope_inspector_overrides: []       # explicit inspector list overrides auto-discovery for
                                         # scoping — useful when CUI lives in a sub-environment

baseline:
  # Practice-level pass / fail thresholds. Defaults reflect CMMC L2 / NIST 800-171.

  access_control:                        # AC family
    mfa_coverage_pct_min: 95             # AC.L2-3.5.3 — multi-factor for privileged + general
    privileged_mfa_required: true        # 100% on privileged
    session_timeout_max_minutes: 30      # AC.L2-3.1.11
    unsuccessful_logon_attempts_max: 5   # AC.L2-3.1.8
    least_privilege_enforced: true       # AC.L2-3.1.5
    shared_account_max: 0                # generic / shared accounts are AC violations

  audit_accountability:                  # AU family
    audit_log_retention_days_min: 90     # AU.L2-3.3.1
    audit_log_review_required: true      # AU.L2-3.3.5
    audit_log_protected: true            # AU.L2-3.3.8

  configuration_management:              # CM family
    baseline_config_documented: true     # CM.L2-3.4.1
    least_functionality_enforced: true   # CM.L2-3.4.7
    change_control_required: true        # CM.L2-3.4.3
    inventory_managed: true              # CM.L2-3.4.1 / 3.4.2

  identification_authentication:         # IA family
    password_complexity_required: true   # IA.L2-3.5.7
    password_min_length: 14
    password_reuse_prohibited_count: 24
    privileged_authenticator_management: true   # IA.L2-3.5.5

  system_communications:                 # SC family
    boundary_protection_required: true   # SC.L2-3.13.1
    network_segmentation_required: true  # SC.L2-3.13.5 (CUI flow control)
    encryption_in_transit_required: true # SC.L2-3.13.8
    encryption_at_rest_required: true    # SC.L2-3.13.16 / MP.L2-3.8.9
    open_rdp_to_internet_allowed: false  # SC.L2-3.13.1 — boundary protection violation

  system_information_integrity:          # SI family
    malicious_code_protection_required: true   # SI.L2-3.14.2 — EDR on every system
    edr_coverage_pct_min: 95
    unprotected_servers_max: 0
    patch_age_days_max: 30                     # SI.L2-3.14.1 — flaw remediation timeliness
    monitor_security_alerts_required: true     # SI.L2-3.14.3
    spam_protection_required: true             # SI.L2-3.14.2 (mail)

  awareness_training:                    # AT family — partially Liongard-evidenced via KnowBe4
    training_program_required: true      # AT.L2-3.2.1
    role_based_training_required: true   # AT.L2-3.2.2
    phishing_simulation_required: true   # AT.L2-3.2.3 (insider-threat awareness)

  media_protection:                      # MP family — partial via disk encryption signal
    encryption_at_rest_required: true    # MP.L2-3.8.9
    portable_media_controlled: true      # MP.L2-3.8.7 — external; flagged as policy evidence

  maintenance:                           # MA family — partial via lifecycle signals
    nonlocal_maintenance_controlled: true # MA.L2-3.7.5

  recovery:                              # RE family — partial via backup signals
    backup_program_required: true        # RE.L2-3.8.9 / RE.L2-3.13.13
    backup_recency_days_max: 7
    offsite_replication_required: true
    backup_encryption_required: true

  domain_baseline:                       # external-trust posture (supports SC family)
    dmarc_health_required: "pass"
    registrar_lock_required: true

stack:
  auto_discover: true
  inspectors_in_scope: []
  inspectors_to_skip: []
  freshness_grace_period_days: 7

per_class_recipe_overrides:
  # cisco-meraki-inspector: "<msp-local>/meraki-cmmc-custom.md"

assessor_documentation_level:
  # How much narrative + evidence detail the workbook produces.
  level: "self-assessment"               # self-assessment | C3PAO-prep | DIBCAC-prep
  include_screenshot_placeholders: true  # workbook adds placeholder rows for manual screenshot evidence
  include_policy_links: true             # each policy-driven control links to the customer's policy doc

verification:
  log_queries: true
  redact_values: true

qa:
  retry_on_null: true
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: false
  surface_single_source_visibility: true
  manual_verification_section_required: true
```

---

## When to use

- "CMMC readiness assessment for <customer>"
- "CMMC Level 1 self-assessment evidence"
- "CMMC Level 2 evidence pack"
- "NIST 800-171 gap analysis for <customer>"
- "DoD contracting compliance prep for <customer>"
- "CMMC pre-audit for <customer>"
- "What's our CMMC posture for <customer>"
- "CMMC C3PAO prep" (assessor-led variant)

Cadence: annual for self-assessments; pre-engagement when responding to
a CMMC-required contract; quarterly drift checks once certified.

Personas:
- **SOC** (primary — owns the technical control evidence + gap
  remediation)
- **vCIO / Account Manager** (primary — owns the certification path
  conversation with customer leadership)
- **TAM** (advisory — confirms findings align with the build standard)
- **Executive** (consumes the readiness summary)
- **Sales** (pre-engagement variant when responding to DoD-prime RFPs
  that require CMMC posture)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` → match by name |
| Customer name | No | Used for filename + report header |
| CMMC level | No (default from customization block) | User prompt or customization |
| Scope boundary (CUI / FCI system list) | Recommended | User-provided; recipe defaults to the full environment when not specified |
| Optional: certification type | No | self-assessment / C3PAO / DIBCAC — informs documentation depth |

---

## Workflow — compliance variant of the cross-cutting pattern

This recipe is the **compliance variant** of the cross-cutting pattern
documented in `reference/cross-cutting-signals.md`. Like the
cyber-insurance recipe, it is point-in-time evidence collection. Unlike
cyber-insurance, the framework is **prescriptive and hierarchical** —
each finding maps to a specific CMMC practice (e.g., AC.L2-3.1.1), and
the workbook is structured around the 14 CMMC domains.

### Step 1 — Scope discovery

```
liongard_environment LIST searchMode=keyword query="<customer-name>"
# Confirm environmentId. Multi-environment customers with CUI in a
# sub-environment should set cmmc_scope.in_scope_inspector_overrides
# to restrict findings to the in-scope environment.
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

Stale-inspector flags surface as evidence-currency notes. A CMMC
assessor wants evidence from the **last inspection** — stale data is
acceptable for some controls (e.g., point-in-time configuration), not
acceptable for others (e.g., audit-log review currency).

### Step 3 — Asset categorization (Level 2)

When `cmmc_scope.asset_categorization_required == true` (default for
Level 2), produce an asset-categorization table.

> **The reconciled asset inventory is the primary source.** CMMC
> categorization scope is "every real-world identity / device / domain
> in this customer's environment", and the dedup'd inventory is the
> authoritative list. The `inspectors[]` array on each record tells
> the assessor which Liongard inspectors observe that asset — critical
> for the SC.L2-3.12.4 / CA.L2-3.12.3 evidence chain. See
> `reference/asset-fields.md` § Deduplication keys.

```
liongard_device LIST environmentId=<ENV_ID> fields=["hostname","class","role","operatingSystem","serialNumber","macAddress","inspectors"]
liongard_identity LIST environmentId=<ENV_ID> fields=["username","email","accountType","privileged","inspectors"]
liongard_domain LIST environmentId=<ENV_ID> fields=["domainName","registrar","inspectors"]
```

Apply categorization:
- **CUI Assets** — systems explicitly in `cmmc_scope.cui_handling_systems`
- **Security Protection Assets** — domain controllers, firewalls, EDR
  management consoles, backup servers, identity providers
- **Contractor Risk Managed Assets** — managed but not CUI-touching
- **Specialized Assets** — IoT, OT, test systems (auto-flagged based on
  device class if available)
- **Out-of-Scope Assets** — explicitly excluded from CUI handling

The categorization table feeds every per-practice finding so the
assessor can verify scope decisions.

### Step 4 — Headline KPIs from the cyber-risk dashboard

```
liongard_cyber_risk_dashboard <metric>  environmentId=<ENV_ID>
```

CMMC-relevant KPIs:

| KPI | Source | Maps to |
|---|---|---|
| MFA coverage % | dashboard | AC.L2-3.5.3 |
| Privileged MFA coverage % | dashboard | AC.L2-3.5.3 (high-impact subset) |
| EDR coverage % | dashboard | SI.L2-3.14.2 |
| Unprotected servers count | computed | SI.L2-3.14.2 + AC.L2-3.1.20 |
| Patch currency | computed | SI.L2-3.14.1 |
| Backup coverage | computed (chained `all-backups.md`) | RE.L2-3.8.9 |
| DMARC posture | computed (Step 5 domain inventory) | SC family (mail-trust evidence) |
| Inspectors deployed for evidence | computed Step 2 | (foundational — without inspectors there's no evidence) |

### Step 5 — Current-state inventory snapshot

> Same reconciled-inventory pattern as Step 3, broadened beyond the
> categorization view to capture full lifecycle / security fields for
> evidence collection.

```
liongard_device COUNT environmentId=<ENV_ID>
liongard_device LIST environmentId=<ENV_ID>
                     fields=["hostname","operatingSystem","class","role","inspectors","lastSeen","manufacturer","model","serialNumber","macAddress"]

liongard_identity COUNT environmentId=<ENV_ID>
liongard_identity LIST environmentId=<ENV_ID>
                       fields=["displayName","username","email","accountType","privileged","mfaStatus","lastLogin","enabled","inspectors"]

liongard_domain LIST environmentId=<ENV_ID>
                     fields=["domainName","registrar","registrarLock","dmarcHealth","spfHealth","dkimHealth","inspectors"]
```

### Step 6 — Auto-discover deployed inspectors + chain sub-recipes

```
liongard_system LIST environmentId=<ENV_ID>
```

Chain the appropriate system-type and single-system recipes with
**CMMC framing** inherited:

| Customer has… | Chained recipe | CMMC domains served |
|---|---|---|
| Windows Servers + Workstations | `all-servers.md` + `all-endpoints.md` + per-OS singles | CM, SI, MA, MP |
| EDR | `all-edrs.md` + per-vendor | SI |
| Firewalls | `all-firewalls.md` + per-vendor | SC, CM |
| Backups | `all-backups.md` + per-vendor | RE, MP |
| Hypervisors | `all-hypervisors.md` | CM, SC, RE |
| M365 | `microsoft-365.md` | AC, IA, AU |
| AD | `active-directory.md` | AC, IA, AU |
| KnowBe4 | `knowbe4.md` | AT |
| Domains | `all-domains.md` | SC (mail / DNS trust) |
| External-facing IPs + TLS hosts + dark-web exposure | `all-external-attack-surface.md` | SC.L2-3.13.8 (encryption-in-transit), SC.L2-3.13.1 (boundary protection), IA family (credential exposure) |

Extract **per-domain CMMC findings** from each chained recipe. The
per-domain `domains/` subfiles (planned — see footer) provide the
canonical practice-to-Liongard-data mapping; chained recipes inherit
those mappings via the customization block.

### Step 7 — Per-practice finding build

For each CMMC practice in scope (17 for L1, 110 for L2, 127 combined),
build a finding row:

```
For each practice:
  practice_id      = e.g., "AC.L2-3.1.1"
  practice_text    = the practice description (from CMMC v2.13 reference)
  evidence_source  = which Liongard data point supports this practice
                     (NULL if external evidence required)
  evidence_summary = "94/100 users have MFA enabled (cyber-risk-dashboard
                     mfaCoverage). Confirms AC.L2-3.5.3 partially."
  status           = MET | NOT MET | PARTIAL | EXTERNAL EVIDENCE
                     REQUIRED | NOT APPLICABLE
  gap_description  = what's missing if status != MET (NULL otherwise)
  remediation      = the recommendation if status != MET
  priority         = Critical / High / Medium / Low based on scoring
                     methodology (NIST 800-171A risk levels)
```

CMMC v2.13 scoring methodology (relevant for self-assessment scoring):
- Level 1 (17 practices) — each practice is 1 point; total possible 17
- Level 2 (110 practices) — point values vary (1, 3, or 5 points per
  practice) per NIST 800-171A; total possible 110

If the user wants the **score** rather than the readiness summary, set
`output.format: "xlsx"` and the workbook surfaces score-rolled-up
totals per domain + overall.

### Step 8 — Quick wins enumeration

Identify practices flagged PARTIAL or NOT MET where remediation is
high-leverage / low-effort. Typical examples:
- Enable MFA on the handful of remaining users
- Configure DMARC enforcement on customer's domains
- Deploy EDR to the small number of unprotected servers
- Apply backlogged critical patches

These become the customer's first-30-days CMMC remediation track.

### Step 9 — Policy / external evidence required section

CMMC practices that **cannot be evidenced from Liongard** are surfaced
in a dedicated section so the customer knows what documentation they
need to provide:

| Practice family | External evidence typically required |
|---|---|
| AT — Awareness & Training | Training records, role-based curriculum, completion reports (KnowBe4 partial; HR system) |
| IR — Incident Response | IR plan, tabletop exercise records, IR team designation |
| MA — Maintenance | Maintenance logs, contractor agreements, non-local maintenance approvals |
| MP — Media Protection (physical) | Media-handling procedures, sanitization records |
| PE — Physical Protection | Facility access logs, badge audit, visitor logs |
| PS — Personnel Security | Background check records, separation procedures, HR sign-offs |
| RA — Risk Assessment | Risk register, risk-assessment cadence documentation |
| CA — Security Assessment | POAM, SSP, ongoing assessment cadence documentation |

When a practice falls in one of these families, the recipe outputs
status = EXTERNAL EVIDENCE REQUIRED and adds a row to the policy /
external evidence section with the typical documentation needed.

### Step 10 — QA pass (per `reference/qa-retry-pattern.md`)

This recipe's QA pass especially focuses on:

1. **Retry persistent nulls** on the cyber-risk-dashboard metrics.
2. **Flag stale inspectors** from Step 2. CMMC evidence currency matters
   — a stale inspector means the evidence is from before the assessor's
   point-in-time. Stale-inspector findings get a "re-inspect before
   submission" note.
3. **Cross-tool divergence** — for any practice evidenced by multiple
   Liongard sources, surface divergence in the verification log so the
   assessor can see the rigor.
4. **Proposed-metric gaps** for any inspector chained where the recipe
   carries data gap notes — these become evidence gaps the
   customer can't fix from Liongard data alone yet.
5. **Single-source visibility** — controls evidenced by only one
   inspector are flagged for assessor awareness. Two independent
   sources is the gold standard; one is acceptable; zero is the
   external-evidence pathway.
6. **Categorization integrity** — confirm every device + identity has
   been categorized (CUI Asset / Security Protection / etc.). Uncategorized
   assets are an evidence gap for the scope-definition control.

### Step 11 — Render the readiness deliverables

The CMMC output is **two deliverables by default**:

#### A. CMMC evidence workbook (xlsx — primary)

Recommended sheet order:

| # | Sheet | Content |
|---|---|---|
| 1 | Cover | Customer, scope (L1 / L2 / combined), assessment type (self / C3PAO / DIBCAC), generation date |
| 2 | Executive Summary | Readiness summary, headline scores, gap counts by priority |
| 3 | Scope Definition | Boundary definition + asset categorization table |
| 4 | Readiness Summary | Per-domain summary table — practice count by status (MET / NOT MET / PARTIAL / EXTERNAL / NA) |
| 5–18 | One sheet per CMMC domain | Per-practice findings, evidence summaries, gap descriptions |
| 19 | Per-Practice Findings | Master table — all practices in scope, sortable / filterable |
| 20 | Gap Tracker | Status != MET rows, with remediation columns + owner / target-date for the customer |
| 21 | Policy / External Evidence | The Step 9 external-evidence section |
| 22 | Asset Inventory | The Step 3 categorization snapshot |
| 23 | Data Gaps | The Step 10 manual-verification appendix |
| 24 | Methodology | One paragraph + link to this recipe in the prompt library |
| 25 | Verification Log | The Step 11 verification table below |

#### B. Readiness narrative (word — secondary)

Prose version of sheets 2, 3, 4, 20, and 21 for the customer's
leadership conversation about the path to certification.

### Tone-driven adaptations

When `audience.tone == "balanced"` (default):
- Per-practice findings include the JMESPath / metric reference for
  the SOC reader
- Practice IDs cited inline

When `audience.tone == "executive"` (readiness summary deck):
- Drop practice IDs from the body — appendix only
- Replace per-practice findings with per-domain status indicators
- Lead with the readiness summary

When `audience.tone == "technical"`:
- All counts, vendor names, JMESPath references, scoring math
- Suitable for SOC working sessions

---

## QA & Manual Verification

The Step 10 detail above is the recipe-specific QA pass. The canonical
pattern lives in `reference/qa-retry-pattern.md`. Every CMMC run produces
a **Manual Verification Needed** appendix per that pattern.

Manual checks specific to CMMC:

- **Policy documentation review** — every external-evidence-required
  practice needs the customer's policy + procedure documents.
- **Scope-boundary confirmation** — the customer's CUI / FCI handling
  scope must be confirmed before the workbook ships.
- **Asset categorization sign-off** — the auto-categorization in Step 3
  is a draft; the customer's CCM / ISSO must sign off on it.
- **Audit-log evidence sampling** — Liongard data confirms audit logging
  is enabled, but the assessor wants evidence of log review cadence
  (typically from the SIEM / log management vendor).
- **Physical security evidence** — PE-family controls are entirely
  external.
- **Personnel security evidence** — PS-family controls are entirely
  external.

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | CMMC evidence chains from the onboarding inventory. Hardware/software inventory, identity posture, backup status, and network controls collected at onboarding map to CMMC Level 1–2 practice families: AC (access control), IA (identification + authentication), MA (maintenance), SC (system + communications protection), SI (system + information integrity). |
| CIS Controls (v8.1) | ✅ | CMMC Level 1 aligns with CIS IG1 (basic cyber hygiene); CMMC Level 2 / NIST 800-171 maps broadly to CIS IG1–2. Key mappings: AC.1.001/AC.1.002 (CIS 6.1–6.2), IA.1.076/IA.1.077 (CIS 5.2/6.3), SC.1.175/SC.3.177 (CIS 12.2/3.11), SI.1.210–211 (CIS 7.1/7.3), MP.2.121/MA.2.111 (CIS 3.9/4.3), AU.2.041/AU.2.042 (CIS 8.2–8.5). CIS compliance significantly accelerates CMMC Level 2 scoping. |
| Cyber-insurance domain files | ✅ | CMMC controls align with cyber-insurance domains: `domains/auth.md` (AC/IA practices — access control + MFA), `domains/endpoint.md` (SI practices — patching + EDR), `domains/backup.md` (RE practices — data recovery), `domains/network.md` (SC practices — boundary protection + CUI boundary), `domains/governance.md` (CA practices — assessment + policy documentation). CMMC evidence typically doubles as cyber-insurance evidence. |
| QBR / quarterly-business-review | ✅ | CMMC compliance status surfaces in QBR for DoD-contractor customers. QBR Step 10 chains this recipe for the annual posture update, gap closure tracking, and SPRS score narrative. |

---

## Insights & recommendations — generation patterns

For each NOT MET / PARTIAL practice, the recipe produces a one-line
remediation:

| Practice family | Common gap | Recommendation template |
|---|---|---|
| AC.L2-3.5.3 | MFA below threshold | "Enroll remaining <N> users in MFA. Privileged accounts: immediate; general accounts: 30-day plan." |
| AC.L2-3.1.5 | Excessive privileged accounts | "Reduce privileged-account count from <N> to operational minimum (typically ≤ 5)." |
| AC.L2-3.1.8 | Account lockout threshold absent | "Configure account lockout after <baseline> unsuccessful attempts via GPO / cloud identity policy." |
| AC.L2-3.1.11 | Session timeout absent | "Configure session timeout ≤ <baseline> minutes via GPO / M365 conditional access." |
| AU.L2-3.3.1 | Audit logging incomplete | "Enable + retain audit logs for <baseline> days on <list of systems>." |
| AU.L2-3.3.5 | Audit log review cadence absent | "Implement weekly audit-log review with documented review cadence." |
| CM.L2-3.4.1 | Configuration baseline absent | "Document approved configuration baseline for <system class>; baseline-deviation monitoring via Liongard." |
| CM.L2-3.4.7 | Excessive functionality | "Audit installed software / running services on <list> against baseline; remove unauthorized." |
| IA.L2-3.5.7 | Password complexity below baseline | "Update password policy: min length <baseline>, reuse <baseline>, complexity required." |
| SC.L2-3.13.1 | Boundary protection gap (open RDP) | "Remove / restrict any-source RDP rules. Confirm legitimate access via VPN." |
| SC.L2-3.13.5 | CUI segmentation gap | "Implement network segmentation isolating CUI-handling systems." |
| SC.L2-3.13.8 | Encryption-in-transit gap | "Enable TLS on internal services handling CUI; document protocol/cipher baseline." |
| SC.L2-3.13.16 | Encryption-at-rest gap | "Enable BitLocker / FileVault / LUKS on <list of systems>." |
| SI.L2-3.14.1 | Patch currency below baseline | "Apply <N> outstanding critical patches; target patch-currency SLA of <baseline> days." |
| SI.L2-3.14.2 | EDR coverage gap | "Install EDR on <N> servers / endpoints; investigate AD-only-visibility gap for <N> devices." |
| RE.L2-3.8.9 | Backup coverage gap | "Add <N> servers to backup program; confirm offsite replication + encryption per baseline." |
| AT.L2-3.2.3 | Awareness training gap | "Deploy KnowBe4 monthly phishing simulation cadence + role-based training curriculum." |
| External-evidence-required | (any) | "Customer-provided <documentation type> required; see policy / external evidence sheet for details." |

Group recommendations by **CMMC domain** for the assessor view, then
re-sort by **priority** for the remediation tracker view.

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Audit-log review cadence | not in dataprint | SIEM / log-management tool + customer SOP |
| Encryption-in-transit configuration | partial (vendor-dependent) | Per-system vendor consoles |
| Encryption-at-rest deployment | partial (some inspectors expose; others external) | Per-OS console / MDM |
| Network segmentation topology | partial (firewall rule + VLAN visibility) | Network diagrams + manual review |
| Policy documentation | external | Customer documentation repository |
| Training records + completion | partial (KnowBe4 if deployed) | HR / LMS system |
| Physical security controls | external | Customer site walk-through |
| Personnel security records | external | HR system |
| Incident response plan + tabletop history | external | Customer IR documentation |
| POAM / SSP / continuous monitoring records | external | Customer compliance program |
| CUI handling procedures | external | Customer documentation |

---

## Output format

`xlsx` (default — evidence workbook) is the canonical primary deliverable.
Supplement with:

- **Word** readiness narrative — for the customer leadership
  conversation
- **Markdown** working draft — useful for the SOC analyst to edit
  before generating the customer-facing xlsx

See `templates/output-block-xlsx.md` and `templates/output-block-word.md`
for layout conventions.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | query=<customer> | array<environment> | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3 | liongard_device + identity LIST | envId=<ENV_ID> | inventory for categorization | ok |
| 4 | liongard_cyber_risk_dashboard | per-metric | <integer> | ok per metric |
| 5 | liongard_device / identity / domain LIST + COUNT | envId=<ENV_ID> [filters] | varies | ok |
| 6 | liongard_system LIST + chained sub-recipes (CMMC framing) | envId=<ENV_ID> | array<system> + per-recipe findings | ok per class |
| 7 | (per-practice build — derived) | per CMMC level + baseline | array<practice-row> | ok |
| 8 | (quick wins — derived) | per Step 7 status filter | array<finding subset> | ok |
| 9 | (policy / external evidence — derived) | per CMMC practice family | array<external-req> | ok |
| 10 | QA pass | per `reference/qa-retry-pattern.md` | varies | ok |
| 11 | render | per `output.format` | <artifact path> | ok |
```

---

## Domain subfiles (future)

The cyber-insurance recipe pattern uses per-domain subfiles
(`domains/auth.md`, `domains/endpoint.md`, etc.) to keep the master
recipe legible. The same architecture applies to CMMC; per-domain
files map specific CMMC practices to specific Liongard data sources.

Planned domain subfiles (not yet built):

| File | CMMC domain | Liongard data sources |
|---|---|---|
| `domains/access-control.md` | AC (22 practices L2) | identity / device inventory + MFA + privileged-account counts |
| `domains/audit-accountability.md` | AU (9 practices L2) | audit log evidence across inspectors |
| `domains/configuration-management.md` | CM (9 practices L2) | baseline-deviation, software inventory, firmware currency |
| `domains/identification-authentication.md` | IA (11 practices L2) | password policy, MFA, authenticator management |
| `domains/system-communications.md` | SC (16 practices L2) | firewall, segmentation, encryption-in-transit, mail trust |
| `domains/system-integrity.md` | SI (7 practices L2) | EDR, patching, monitoring, mail protection |
| `domains/awareness-training.md` | AT (3 practices L2) | KnowBe4 (partial); external otherwise |
| `domains/recovery.md` | RE (relevant subset) | backup-program evidence |
| `domains/media-protection.md` | MP (9 practices L2) | encryption-at-rest (partial); external otherwise |
| `domains/maintenance.md` | MA (6 practices L2) | partial; mostly external |
| `domains/policy-external.md` | IR / PE / PS / RA / CA | aggregator of external-evidence practices |

Until subfiles exist, the master recipe handles per-practice mapping
inline. Subfile architecture is a future optimization once the recipe
has had time to mature with real customer engagements.

---

## Relationship to other cross-cutting recipes

- **Cyber-insurance readiness (`compliance/cyber-insurance/cyber-insurance-readiness.md`)** —
  overlapping evidence categories (MFA, EDR, backup, patching). The
  recipes share the underlying chained per-class recipes; outputs
  differ in framing (cyber-insurance is questionnaire-driven; CMMC is
  control-driven).
- **Onboarding (`onboarding-assessment/new-customer-onboarding.md`)** —
  for new customers in DoD-adjacent industries, the onboarding intake
  can chain the CMMC readiness as a sub-section to surface the CMMC
  baseline at handoff.
- **PBR (`environment-quarterly-lookback/quarterly-business-review.md`)** —
  CMMC readiness becomes a recurring PBR section for certified
  customers; drift detection is the quarterly read.
- **Roadmap (`roadmap-planning/refresh-and-lifecycle-roadmap.md`)** —
  when a CMMC gap requires a hardware refresh or licensing change, the
  roadmap captures the planning + budget side.

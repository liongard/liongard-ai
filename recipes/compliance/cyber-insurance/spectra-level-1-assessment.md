---
name: spectra-level-1-assessment
description: >
  Use this recipe to prepare evidence for a Spectra Level 1 cyber insurance / MSP
  certification assessment. Trigger phrases: "Spectra Level 1 assessment",
  "Spectra certification evidence", "Spectra cyber controls", "fill out the Spectra
  questionnaire", "Spectra MSP evaluation", "Spectra Level 1 standards evidence".
  This recipe maps all 21 Spectra Level 1 standard IDs (C01a–C17 and MDR1–MDR4) to
  Liongard MCP evidence and manual attestation requirements. Produces an evidence
  pack in the format the MSP configures (Word, Excel, or Markdown). Unlike the
  universal carrier application recipe, this assessment targets the MSP's OWN
  internal security posture and service-delivery capabilities — not a specific
  end-customer environment.
compatibility: >
  Requires Liongard MCP: liongard_environment, liongard_identity, liongard_device,
  liongard_metric, liongard_launchpoint. Most governance controls (C01–C05, C12,
  C13 partial, C17) require manual attestation — Liongard evidence is strongest for
  MDR1, MDR3, C10, C11, C07, C06, and C14.
personas: [vcio-account-manager, soc, technical-alignment-manager]
output_formats: [xlsx, word, markdown]
primitives: []
composes:
  - recipe:single-system:single-system-dark-web-monitoring
  - recipe:single-system:single-system-internet-domain-dns
  - recipe:single-system:single-system-knowbe4
  - recipe:single-system:single-system-network-ip-address
  - recipe:single-system:single-system-tls-ssl
  - recipe:system-type:system-type-all-edrs
---

# Spectra Level 1 Assessment — MSP Evidence Pack

> **Scope note:** This recipe evaluates the **MSP's own** internal security posture and
> service-delivery capabilities against the Spectra Level 1 standard. Point Liongard at
> the MSP's own internal environment (not a customer's), or use the MSP's own Liongard
> instance if they manage themselves as a customer.
>
> For carrier applications on behalf of an end-customer, use
> `cyber-insurance-application-universal.md` or `cyber-insurance-readiness.md` instead.

---

## Customize for your MSP

```yaml
output:
  format: xlsx              # xlsx | word | markdown
  filename: "spectra-level-1-evidence-<YYYY-MM-DD>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  govern: "Governance & MSP Controls"
  identify: "Identify — Risk & Threat Intelligence"
  protect: "Protect — Technical & Operational Controls"
  detect: "Detect — Coverage & Log Management"
  respond_recover: "Respond & Recover"
  mdr: "Managed Protection & Detection (MDR)"
  contract: "Contract Management"
  gaps: "Gaps & Remediation Plan"
  manual_attestation: "Manual Attestation Checklist"

audience:
  tone: "balanced"           # technical | balanced | executive
  reading_level: "manager"

thresholds:
  mdr_endpoint_coverage_pct_min: 99   # MDR1: ≥99% of endpoints
  mdr_server_coverage_pct_min: 100    # MDR1: 100% of servers
  mdr_identity_coverage_pct_min: 100  # MDR1: 100% of user identities
  phishing_campaign_frequency_months: 3   # C07: quarterly minimum
  awareness_training_frequency_months: 12 # C07: annual minimum
  vuln_patch_critical_days: 7         # C06: high/critical patched within 7 days
  external_scan_frequency: "weekly"   # C06: weekly external scanning
  pentest_frequency_months: 12        # C06: annual pen test
  psaRetentionMonths: 6               # MDR4: 6-month minimum retention

evidence_currency_days: 90

qa:
  retry_on_null: true
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: true
```

---

## When to use

- **Spectra certification / renewal** — produce the evidence pack for the Spectra
  certifier's review.
- **Pre-assessment readiness check** — run 60–90 days before certification to surface
  gaps while there is time to remediate.
- **Ongoing compliance monitoring** — the Liongard-backed sections (MDR1, MDR3, C10,
  C11, C07) can be re-run quarterly as a standing posture check.

---

## Inputs

| Input | How to obtain |
|---|---|
| MSP internal environment ID | `liongard_environment LIST` — match the MSP's own managed environment |
| MSP-owned Liongard system IDs | `liongard_launchpoint LIST` per inspector type in the MSP's own environment |
| Spectra standard version | Confirm the version on file with the certifier (this recipe targets Level 1) |

---

## Workflow

### Step 0 — Pre-flight: Internet Footprint Sweep (supports C06, C11)

Before pulling internal evidence, run the external attack surface sweep against the
MSP's own domains and public-facing IP ranges. This step surfaces findings that Spectra
C06 (vulnerability scanning, open ports) and C11 (zero-trust / segmentation) reference
directly, and that a Spectra certifier could independently verify.

```
# MSP's own external posture:
recipes/single-system-analysis/by-inspector/tls-ssl.md
recipes/single-system-analysis/by-inspector/internet-domain-dns.md   # DMARC/SPF/DKIM
recipes/single-system-analysis/by-inspector/network-ip-address.md    # open ports
recipes/single-system-analysis/by-inspector/dark-web-monitoring.md   # credential exposure
```

| Finding | Spectra control |
|---|---|
| Open RDP (port 3389) to internet | C06, C09, C11 — hard failure |
| Missing DMARC/SPF/DKIM on MSP domain | C07 (email hygiene), C06 |
| Expired or near-expiry TLS cert | C06, C08 |
| Dark-web credential exposure | C11, C08 |

---

### Step 1 — Identify the MSP's own environment

```
liongard_environment LIST
```

Match the MSP's internal environment. Note `environmentId` — required for every
subsequent call.

---

### Step 2 — Pull the asset inventory (primary evidence source)

Pull the MSP's own internal identity and device inventory. These records are the
primary evidence for MDR1 (enrollment coverage), C10 (endpoint protection), and C11
(identity / MFA posture).

```
liongard_identity COUNT environmentId=<MSP_ENV_ID>
liongard_identity COUNT environmentId=<MSP_ENV_ID> mfaStatus="NO" enabled=true
liongard_identity COUNT environmentId=<MSP_ENV_ID> privileged=true
liongard_identity COUNT environmentId=<MSP_ENV_ID> privileged=true mfaStatus="NO" enabled=true

liongard_device LIST environmentId=<MSP_ENV_ID> detail=full pageSize=200
```

`detail=full` is required — without it, `edr`, `antivirus`, and `inspectors[]` are
not populated. Paginate until all records are retrieved.

> **Deduplication note:** `liongard_identity` deduplicates across all identity
> inspectors (AD, M365, JumpCloud, Duo, etc.) by email address. One record per
> real person. Do NOT sum per-inspector user counts — that double-counts.
> See `reference/asset-fields.md` for field reference and deduplication keys.

---

### Step 3 — Work through all 21 Spectra Level 1 controls

For each control, the recipe lists:
- **Coverage** — `LIONGARD` / `PARTIAL` / `MANUAL`
- **Evidence** — MCP call(s) or attestation requirement
- **Spectra requirement** — the verbatim standard text (abbreviated)
- **Draft answer template**

---

## Domain: IT Support & Incident Response

### C01a — SLAs in contract language

**Spectra requirement:** SLAs are captured in contract language with incident
prioritization and response times clearly defined.

**Coverage:** `MANUAL`

**Evidence:** MSP contract templates, SOW, SLA documentation. No Liongard inspector
covers contractual SLA definition.

**Draft answer:**
> "SLAs are defined in our standard MSA and SOW templates for all managed-service
> customers. Incident priority tiers (P1–P4) and corresponding response / resolution
> times are documented in Exhibit [X] of the MSA. Templates reviewed by legal counsel
> as of [date]. [Attach: SLA exhibit or MSA excerpt — redacted for confidentiality.]"

---

### C01b — Standardized Incident Response Procedures

**Spectra requirement:** Incident Response Procedures are standardized, documented,
and consistent across all managed-services customers.

**Coverage:** `MANUAL`

**Evidence:** Incident Response Plan document; PSA ticket workflow documentation.

**Pairs with:** C15 (detection and response capabilities — technical implementation)

**Draft answer:**
> "A standardized Incident Response Procedure is documented and applied consistently
> across all managed-service customers. The procedure covers: detection, triage,
> containment, eradication, recovery, and post-incident review. Most recent review
> date: [date]. [Attach: IRP document — excerpts or table of contents acceptable.]"

---

### C01c — Annual helpdesk training on IR procedures

**Spectra requirement:** All helpdesk personnel trained at least annually on helpdesk
processes and incident response procedures.

**Coverage:** `MANUAL`

**Evidence:** HR / LMS training completion records. If the MSP uses KnowBe4 for
security awareness training, partial evidence is available via Liongard.

**Draft answer:**
> "All helpdesk personnel complete annual training on helpdesk processes and incident
> response procedures. Most recent training cycle: [date], completion rate: [%].
> Training is delivered via [LMS / KnowBe4 / vendor platform]. Records available
> upon request."

---

### C01d — Vendor certifications for technical staff

**Spectra requirement:** Technical staff maintain current training/accreditation from
technology vendors proportional to their role.

**Coverage:** `MANUAL`

**Evidence:** Certification records (vendor-issued). No Liongard coverage.

**Draft answer:**
> "Technical staff maintain current vendor accreditations proportional to their role.
> Certifications held include: [list vendor names only, not employee names —
> e.g., Microsoft, Cisco, SentinelOne, Datto]. Renewal tracking is maintained in
> [HR system / spreadsheet]. Certifications reviewed annually as part of performance
> management."

---

## Domain: MSP Controls — Govern

### C02a — Third-party vendor due diligence

**Spectra requirement:** MSP undertakes due diligence for RFPs and vendor assessments
aligned with organizational security values.

**Coverage:** `MANUAL`

**Evidence:** Vendor assessment process documentation; vendor register.

**Draft answer:**
> "A vendor assessment process is in place for onboarding third-party vendors and
> software providers. Due diligence includes: [security questionnaire / SOC 2 review /
> ISO 27001 certification check / contractual security requirements]. Vendor risk
> review is repeated [annually / upon material contract change]. [Attach: vendor
> assessment framework or sample questionnaire — redacted.]"

---

### C02b — Software security management / patch testing

**Spectra requirement:** An appropriate strategy for software security management
(including patch testing and containerization) is established.

**Coverage:** `PARTIAL`

**Evidence:**
- Patch cadence evidence from endpoint inspectors (Windows / macOS / Linux):
  ```
  # Windows patching posture (MSP internal fleet)
  liongard_metric EVALUATE jmesPathQuery="<patch-age-path>" systemId=<MSP_WIN_SYS_ID> environmentId=<MSP_ENV_ID>
  ```
- Containerization / sandbox strategy: `MANUAL`
- Patch testing policy (ringed deployment, staging): `MANUAL`

**Draft answer:**
> "A software security management strategy is established covering: patch testing
> (staged/ringed deployment to low-risk systems before wide rollout), patch deployment
> SLAs ([critical: <7 days, high: <30 days]), and [containerization / sandboxing
> approach if applicable]. As of [date], [N]% of MSP-managed devices have no
> critical patches overdue per Liongard inspection. [Attach: patch management policy.]"

---

### C03a / C03b / C03c — AI security evaluation (MSP use of AI)

**Spectra requirement:** The MSP's use of AI security services has been formally
evaluated by management, documenting: (a) opportunities to improve security via AI,
(b) controls to manage AI-related risk (data leakage), and (c) clearly defined roles
and responsibilities in the MSA.

**Coverage:** `MANUAL`

**Evidence:** AI strategy / governance documentation; MSA AI clause.

**Draft answer:**
> "Management has formally evaluated our use of AI security services. The evaluation
> documents: (a) AI-enabled security opportunities deployed or under evaluation
> (including [list vendor/product names without proprietary details]); (b) controls
> to manage AI-related risk — including data-leakage controls, approved-tool lists,
> and training on acceptable use; (c) roles and responsibilities for AI deployment
> are defined in our standard MSA (Section [X]). The evaluation was last reviewed
> by management on [date]."

---

## Domain: MSP Controls — Identify

### C04 — Threat intelligence

**Spectra requirement:** The MSP incorporates appropriate sources of threat
intelligence on an ongoing basis and uses it to evaluate and improve their
security strategy.

**Coverage:** `MANUAL`

**Evidence:** Threat intelligence feed subscriptions; documented review process.
Dark-web monitoring exposure (if the MSP has Dark Web Monitoring deployed for its
own domains) is Liongard-observable.

**Liongard evidence (supplemental):**
```
# If dark-web monitoring is deployed for the MSP's own domain(s):
recipes/single-system-analysis/by-inspector/dark-web-monitoring.md
→ credential exposures for MSP staff email addresses
```

**Draft answer:**
> "The MSP subscribes to [threat intelligence sources — e.g., CISA advisories,
> MS-ISAC, vendor threat feeds, dark-web monitoring]. Threat intelligence is reviewed
> [weekly / at security standup] and findings inform [patch prioritization / security
> advisory communications to customers / tooling adjustments]. Dark-web credential
> monitoring for MSP staff is conducted via [platform]; most recent review: [date]."

---

### C05 — Customer authentication / change approval

**Spectra requirement:** A process is in place to validate user requests and seek
approval for changes commensurate to the risk profile.

**Coverage:** `MANUAL`

**Evidence:** Helpdesk authentication procedure; PSA change approval workflow.

**Draft answer:**
> "All customer requests received via [helpdesk / PSA / email] are validated using
> [authentication method — e.g., pre-set security phrase, callback to registered
> number, ticketing portal with SSO authentication] before action is taken.
> Change requests are escalated for customer approval based on risk tier
> (Tier 1: standard changes pre-approved; Tier 2: change requires written
> customer approval; Tier 3: change requires emergency change process).
> Process documented in [PSA workflow / runbook — attach excerpt]."

---

### C06 — Penetration testing & vulnerability scanning

**Spectra requirement:** Annual penetration test; quarterly internal vulnerability
scanning; weekly external vulnerability scanning (or continuous). High/Critical
vulnerabilities patched or mitigated within 7 days of discovery.

**Coverage:** `PARTIAL`

**Liongard evidence:**
```
# External attack surface scan — open ports, TLS, exposed services on MSP's own network:
recipes/single-system-analysis/by-inspector/network-ip-address.md
  → open ports per public IP (port 3389 RDP, 22 SSH, 445 SMB, 23 Telnet)
  → confirm no unintended internet-facing services

# Patch age on MSP endpoints to demonstrate <7-day critical patching:
liongard_metric EVALUATE jmesPathQuery="<windows-critical-patch-age-path>"
  systemId=<MSP_WIN_SYSTEM_ID> environmentId=<MSP_ENV_ID>
```

**Manual evidence required:**
- Annual pen test report (engagement letter / executive summary — redact sensitive findings)
- Quarterly internal vulnerability scan results
- Vulnerability remediation log demonstrating <7 days for high/critical

**Draft answer:**
> "An annual penetration test is conducted by [external firm]. Most recent engagement:
> [date], scope: [internal / external / both]. Findings: [count] High, [count]
> Critical — all remediated within 7 days per remediation log (attached).
> Quarterly internal vulnerability scanning is conducted via [scanner tool].
> External scanning is [weekly / continuous] via [scanner / external attack surface
> monitoring platform]. As of [date], no open RDP/SMB/Telnet ports are exposed on
> MSP internet-facing addresses per Liongard inspection."

---

## Domain: MSP Controls — Protect

### C07 — Phishing training & security awareness

**Spectra requirement:** Annual security awareness training and quarterly phishing
simulations at minimum.

**Coverage:** `PARTIAL`

**Liongard evidence (if KnowBe4 is deployed):**
```
# KnowBe4 training and phishing campaign results for MSP staff:
recipes/single-system-analysis/by-inspector/knowbe4.md
  → campaign completion rate (target: 100%)
  → phishing simulation click rate (target: declining trend)
  → last campaign date (confirm quarterly cadence)
```

**Manual evidence if KnowBe4 not deployed:** Training platform completion records.

**Draft answer (KnowBe4):**
> "Annual security awareness training and quarterly phishing simulation campaigns
> are conducted for all [N] MSP staff via [KnowBe4 / platform]. Most recent
> training cycle: [date], completion rate: [%]. Most recent phishing campaign:
> [date], click rate: [%]. Campaign history confirms quarterly cadence for
> past 12 months. Evidence: Liongard KnowBe4 inspection, [date]."

**Draft answer (manual):**
> "Annual security awareness training ([date], [%] completion) and quarterly
> phishing simulations ([dates of last 4 campaigns]) are conducted for all
> MSP staff via [platform]. Training records available upon request."

---

### C08a — Secure device build process

**Spectra requirement:** New assets are built securely following a predefined
process, including all required security solutions.

**Coverage:** `PARTIAL`

**Liongard evidence (newly provisioned devices):**
```
# Confirm EDR/AV is enrolled on devices with recent creation dates:
liongard_device LIST environmentId=<MSP_ENV_ID> detail=full
  → filter: accountCreated > (today - 30d) AND edr == null
  → any new devices missing EDR coverage = gap
```

**Manual evidence:** Device build checklist / golden image documentation.

**Draft answer:**
> "A standardized device build process is in place for all MSP-managed devices.
> New devices are built from a [golden image / baseline build] that includes:
> [EDR agent, AV, MDM enrollment, disk encryption, approved software set].
> Build checklist is signed off by [IT admin] before the device enters production.
> As of [date], all MSP devices with Liongard-visible recent provisioning dates
> have confirmed EDR enrollment."

---

### C08b — Restricted access to MSP tools and systems

**Spectra requirement:** Access to MSP tools and systems is restricted appropriately
(aligned with the BEC service section).

**Coverage:** `PARTIAL`

**Liongard evidence:**
```
# Privileged account MFA posture on MSP's own identities:
liongard_identity COUNT environmentId=<MSP_ENV_ID> privileged=true mfaStatus="NO" enabled=true
  → target: 0 (no privileged accounts without MFA)

# Stale or dormant privileged accounts:
liongard_identity LIST environmentId=<MSP_ENV_ID> privileged=true detail=full
  → filter: accountActivity in ["Stale", "Dormant", "Never Used"] AND enabled=true
  → target: 0 (no active stale privileged accounts)
```

**Manual evidence:** RMM/PSA access control policy; role-based access documentation;
access review date.

**Draft answer:**
> "Access to MSP tools and systems (RMM, PSA, billing, remote access) is restricted
> per a documented access control policy using role-based access (RBAC). As of
> [date], [0 / N] privileged accounts lack MFA. Most recent privileged access review:
> [date]. Service accounts are documented with owner assignment. [Attach: access
> control policy summary — no credential details.]"

---

### C09 — Secure remote access to customer environments

**Spectra requirement:** Tools and processes for remote access to client environments
are secure, standardized, documented, and consistent across all managed-services customers.

**Coverage:** `PARTIAL`

**Liongard evidence:**
```
# MSP's own external attack surface — confirm no legacy open RDP to internet:
recipes/single-system-analysis/by-inspector/network-ip-address.md
  → open port 3389 = ❌ (remote access must go through authenticated RMM, not raw RDP)

# Firewall inspector on MSP's own network — confirm VPN/MFA enforcement:
liongard_metric EVALUATE jmesPathQuery="<vpn-mfa-policy-path>"
  systemId=<MSP_FIREWALL_SYS_ID> environmentId=<MSP_ENV_ID>
```

**Manual evidence:** Remote access tool list (RMM name, version, MFA configuration);
remote access policy; screen-share / break-glass process documentation.

**Draft answer:**
> "Remote access to all client environments is performed exclusively via
> [RMM tool — e.g., NinjaRMM, ConnectWise Automate] with MFA enforced at login.
> Direct (raw) RDP to customer systems is prohibited by policy. No open RDP port
> (3389) is exposed on MSP-managed infrastructure per Liongard inspection as of
> [date]. Remote access policy is documented and consistent across all customers.
> [Attach: remote access policy excerpt — no customer-specific details.]"

---

### C10 — MSP devices enrolled in endpoint protection / MDM

**Spectra requirement:** All MSP devices (including mobile) enrolled in endpoint
protection; an appropriate MDM policy is in place for MSP internal devices.

**Coverage:** `PARTIAL`

**Liongard evidence:**
```
# EDR/AV coverage on MSP internal devices:
liongard_device LIST environmentId=<MSP_ENV_ID> detail=full pageSize=200
  → for each device where category == "compute" AND inspectors[] contains <local-inspector>:
    edr == null  → ❌ no EDR confirmed (genuine gap — locally inspected but no EDR)
    edr != null  → ✅ EDR enrolled

# Server coverage separately (Spectra MDR1 also requires 100% server coverage):
liongard_device LIST environmentId=<MSP_ENV_ID> operatingSystem="Windows Server" detail=full
  → all servers should have edr != null
```

**Manual evidence:** MDM solution name and enrollment scope; mobile device policy.

**Draft answer:**
> "All MSP workstations and servers are enrolled in [EDR product]. As of [date],
> EDR coverage is [N]% of MSP-managed devices (target: 100%). [N] devices lack
> confirmed EDR enrollment — investigation in progress.
> MDM is deployed for MSP-owned mobile devices via [MDM platform]. MDM policy
> requires: [device encryption, PIN/passcode, remote wipe capability, approved
> app list]. Evidence: Liongard device inspection, [date]."

---

## Domain: Systemic Risk Management — Protect

### C11 — IAM controls to prevent propagation across client environments

**Spectra requirement:** Zero trust network access policies, logical segmentation of
client environments, modern MFA enforced across any RMM tools deployed.

**Coverage:** `PARTIAL`

**Liongard evidence:**
```
# MFA enforcement across MSP identities (including RMM logins):
liongard_identity COUNT environmentId=<MSP_ENV_ID> mfaStatus="NO" enabled=true
  → target: 0 (100% MFA coverage on MSP staff)

liongard_identity COUNT environmentId=<MSP_ENV_ID> privileged=true mfaStatus="NO" enabled=true
  → target: 0 (absolute — no privileged account without MFA)

# RMM-specific MFA (if RMM inspector available for MSP's own RMM account):
liongard_metric EVALUATE jmesPathQuery="<rmm-mfa-users-without-mfa-path>"
  systemId=<MSP_RMM_SYS_ID> environmentId=<MSP_ENV_ID>
```

**Manual evidence:** Zero trust architecture documentation; network segmentation
diagram; RMM MFA enforcement configuration screenshot.

**Draft answer:**
> "MFA is enforced for all [N] MSP staff identities. As of [date], [0] MSP accounts
> lack MFA (0 privileged accounts without MFA). Remote access to client environments
> requires MFA via [RMM / ZTNA tool]. Client environments are logically segmented
> — each customer's Liongard environment is isolated and MSP staff access is scoped
> by role. Network segmentation: [VLAN / ZTNA / PSK isolation — describe approach].
> Evidence: Liongard identity inspection, [date]. [Attach: network segmentation
> diagram — no customer-specific details.]"

---

### C12a — Change management policy

**Spectra requirement:** A change management and patch rollout policy is in place
commensurate to the risk profile of the release and systems affected.

**Coverage:** `MANUAL`

**Draft answer:**
> "A change management policy is documented and applied to all changes to
> MSP-managed tooling and customer environments. Changes are classified by risk tier:
> [Standard: pre-approved, low risk / Major: requires review + customer notification /
> Emergency: expedited approval with post-change review]. The policy governs:
> approval workflow, rollback plan, communication requirements, and documentation.
> Most recent policy review: [date]. [Attach: change management policy excerpt.]"

---

### C12b — Testing / staged rollout

**Spectra requirement:** Testing including staggered rollout to low-risk environments
to minimize disruption.

**Coverage:** `MANUAL`

**Draft answer:**
> "All major and high-risk changes follow a staged rollout process: changes are
> first applied to [low-risk / internal test / smallest customer] environments,
> monitored for [N] hours, then promoted to remaining environments. For RMM /
> tooling updates, an internal test tenant is used for initial validation before
> customer deployment. [Attach: rollout procedure or example change record showing
> staged deployment — redact customer identifiers.]"

---

## Domain: MSP Coverage — Detect

### C13 — Oversight of client estate outside MSP scope

**Spectra requirement:** MSP has identified significant systems, control processes,
and user populations outside their scope and has addressed associated risks.

**Coverage:** `PARTIAL`

**Liongard evidence:**
```
# Assets discovered but not fully managed (Discovery-state assets flag scope gaps):
liongard_device LIST environmentId=<CUSTOMER_ENV_ID> inventoryState="Discovery" detail=full
  → devices visible to Liongard but not fully onboarded = out-of-scope systems to document

# Inspector coverage gaps per environment:
liongard_launchpoint LIST environmentId=<CUSTOMER_ENV_ID> pageSize=50
  → fields: ["id", "system", "latestInspectionDate", "status"]
  → systems with "Agent Issue" or stale inspectionDate = potential blind spots
```

**Manual evidence:** Scope-of-work documentation; out-of-scope system register;
customer sign-off on out-of-scope systems.

**Draft answer:**
> "For each managed customer, the MSP maintains a documented scope registry
> identifying systems, user populations, and processes outside the managed-services
> agreement. Out-of-scope systems are flagged to the customer in writing (SOW
> exclusion list) and risks associated with separately managed IT are communicated
> annually or on material change. Liongard Discovery-state assets are reviewed
> quarterly and either onboarded or documented as out-of-scope. Most recent review:
> [date]."

---

### C14 — Log management for endpoint customers

**Spectra requirement:** A solution is deployed to collect, normalize, and analyze
security logs and telemetry for visibility into security events.

**Coverage:** `PARTIAL`

**Liongard evidence:**
```
# Confirm SIEM / log aggregation tool is deployed (if inspector available):
liongard_launchpoint LIST inspectorId=<SIEM_INSPECTOR_ID> environmentId=<MSP_ENV_ID>
  → confirms SIEM inspector is connected and running

# EDR/MDR telemetry coverage via endpoint inspector (MDR3 cross-check):
liongard_device LIST environmentId=<MSP_ENV_ID> detail=full
  → devices with edr != null → actively reporting to MDR platform
```

**Manual evidence:** SIEM/MDR platform name; log source list; retention configuration
(note: MDR4 requires PSA retention ≥ 6 months; C14 requires log collection).

**Draft answer:**
> "A centralized log management and SIEM platform is deployed: [platform name].
> Security telemetry is collected from: [endpoint agents, firewall logs, identity
> provider logs, cloud workloads — list sources without customer details].
> Log retention: [N] months (meets or exceeds the 6-month MDR4 minimum).
> All MSP endpoint customers with EDR enrolled have security telemetry ingested
> into the centralized platform. Evidence: Liongard device inspection confirms
> EDR telemetry enrollment as of [date]."

---

## Domain: MSP Controls — Respond

### C15 — Incident response across MSP and client environment

**Spectra requirement:** Detection and response capabilities implemented to identify,
investigate, and respond to security incidents across managed customer environments.
Monitoring tools, documented procedures, and trained personnel are in place. Integrated
across MSP/MSSP platform and customer environments.

**Coverage:** `PARTIAL`

**Liongard evidence:**
```
# MDR/EDR deployment across customer endpoints (same as MDR1 evidence):
liongard_device LIST environmentId=<CUSTOMER_ENV_ID> detail=full pageSize=200
  → edr != null per device = actively reporting to detection platform

# Active alerts / detections visible in Liongard:
liongard_alert LIST environmentId=<CUSTOMER_ENV_ID> pageSize=50
  → recent alerts by type — demonstrates active monitoring
```

**Manual evidence:** SOC / MDR SLA documentation; escalation matrix; incident
response runbook (redacted); evidence of 24x7 coverage (shifts or SOC partner agreement).

**Draft answer:**
> "Detection and response capabilities are implemented via [MDR platform / SOC
> partner / internal SOC]. Coverage: [24x7 / business hours + on-call]. All
> [N] managed endpoints have EDR agents reporting to the centralized platform per
> Liongard inspection as of [date]. Documented incident response procedures cover
> detection, analysis, containment, eradication, and recovery. Security events are
> escalated per the documented escalation matrix. [Attach: IR runbook table of
> contents; SOC coverage agreement excerpt.]"

---

## Domain: Systemic Risk Management — Recover

### C16 — Reduce impact of catastrophic multi-customer incident

**Spectra requirement:** Sufficient layered controls to reduce impact of large-scale
incidents affecting multiple customers.

**Coverage:** `PARTIAL`

**Liongard evidence:**
```
# Backup coverage across customer environments — demonstrates recovery capability:
liongard_launchpoint LIST inspectorId=<BACKUP_INSPECTOR_ID> environmentId=<CUSTOMER_ENV_ID>
  → confirms backup inspector is running and last inspection is recent

# EDR coverage across environments — layered endpoint defense:
liongard_device LIST environmentId=<CUSTOMER_ENV_ID> detail=full
  → edr != null percentage = proportion of endpoints with active defense layer
```

**Manual evidence:** Business continuity plan; backup isolation documentation;
cross-tenant segmentation architecture (how an incident in one customer can't
propagate to others).

**Draft answer:**
> "Layered controls are in place to reduce the risk of a catastrophic cross-customer
> incident: (1) **Segmentation** — customer environments are logically isolated
> (separate Liongard environments, role-scoped access, no shared credentials);
> (2) **EDR/MDR** — endpoint detection deployed across [N]% of managed devices,
> with isolation capability (endpoint isolation and cloud workload isolation);
> (3) **Backup** — isolated backup infrastructure confirmed for all customers with
> backup inspectors active; (4) **Incident response** — documented cross-customer
> triage process. Evidence: Liongard environment and device inspection, [date]."

---

## Domain: Contract Management

### C17 — Standardized MSP contract templates

**Spectra requirement:** Standardized MSA and SOW templates reviewed by legal counsel.
Contracts include: liability cap, formalized SLAs, exclusions for consequential/
indirect damages, force majeure clause. Changes to standard wording require approval
and legal guidance.

**Coverage:** `MANUAL`

**Draft answer:**
> "MSP maintains standardized MSA and SOW templates reviewed and approved by legal
> counsel as of [date]. Standard contract language includes: (a) liability cap
> ([cap basis — e.g., fees paid in prior 12 months]); (b) formalized SLAs (see C01a);
> (c) exclusions for consequential, special, indirect damages, loss of profits, and
> liquidated damages; (d) force majeure provision. Material changes to standard
> wording require approval by [designated approver] and legal review when significant.
> [Attach: MSA section headings / table of contents — no confidential client-specific
> terms.]"

---

## Domain: Managed Protection & Detection (MDR)

### MDR1 — MDR coverage ≥99% endpoints, 100% servers, 100% identities; ITDR modules enabled

**Spectra requirement:**
- ≥99% of customer endpoints enrolled in MDR and actively reporting
- 100% of servers enrolled in MDR
- 100% of user identities (including privileged/admin) monitored for indicators of compromise
- Baseline ITDR modules enabled: Geographic Location, Impossible Travel, Credential Misuse,
  Shadow Admin, Mailbox Tampering
- MDR configured for endpoint/tenant/cloud isolation and recovery

**Coverage:** `LIONGARD` (for enrollment rates); `PARTIAL` (for ITDR module configuration)

**Liongard evidence:**
```
# Step 1 — Total device count and EDR enrollment:
liongard_device COUNT environmentId=<ENV_ID>
liongard_device LIST environmentId=<ENV_ID> detail=full pageSize=200
  → compute devices where inspectors[] contains <local-inspector> AND edr == null  → gaps
  → compute devices where category == "server" AND edr == null                     → server gaps (must be 0)

# Step 2 — Identity monitoring coverage:
liongard_identity COUNT environmentId=<ENV_ID>
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true  → cross-check

# Step 3 — MDR / ITDR platform configuration (if inspector available):
liongard_metric EVALUATE jmesPathQuery="<itdr-modules-enabled-path>"
  systemId=<MDR_SYSTEM_ID> environmentId=<ENV_ID>
```

**Coverage computation:**
```
endpoint_coverage_pct = (total_compute_devices - devices_without_edr_locally_inspected) / total_compute_devices * 100
server_coverage_pct   = (total_servers - servers_without_edr) / total_servers * 100
identity_coverage_pct = (total_identities - identities_without_mdr_monitoring) / total_identities * 100
```

**Thresholds (from customization block):**
- Endpoint: ≥ `mdr_endpoint_coverage_pct_min` (default 99%)
- Server: ≥ `mdr_server_coverage_pct_min` (default 100%)
- Identity: ≥ `mdr_identity_coverage_pct_min` (default 100%)

**ITDR modules (manual attestation required for specific module names):**

| Module | Liongard Coverage | Evidence Source |
|---|---|---|
| Geographic Location monitoring | PROPOSED | MDR platform console |
| Impossible Travel detection | PROPOSED | MDR platform console |
| Credential Misuse | PROPOSED | MDR platform console |
| Shadow Admin monitoring | PARTIAL — `liongard_identity LIST privileged=true` shows admin accounts | MDR platform confirms detection rule |
| Mailbox Tampering | PROPOSED | M365 inspector + MDR platform |

**Draft answer:**
> "MDR is deployed across all managed customer environments. As of [date]:
> - Endpoint coverage: [N]% ([N] of [total] compute endpoints with confirmed EDR enrollment;
>   target ≥99%)
> - Server coverage: [N]% ([N] of [total] servers with confirmed EDR enrollment; target 100%)
> - Identity monitoring: [N] identities monitored across [N] environments
> Baseline ITDR modules enabled in [MDR platform]: Geographic Location monitoring ✅,
> Impossible Travel ✅, Credential Misuse ✅, Shadow Admin monitoring ✅,
> Mailbox Tampering ✅ (confirm in MDR console — Liongard provides supporting
> identity and M365 data).
> MDR is configured to isolate endpoints, cloud tenants, and environments on detection.
> Evidence: Liongard device and identity inventory, [date]."

---

### MDR2 — Third-party evaluation of detection capabilities

**Spectra requirement:** Vendor has participated within the past 3 years in an
independent third-party evaluation against publicly documented adversary techniques
(e.g., MITRE ATT&CK evaluations). Results available for Spectra certifier review.

**Coverage:** `MANUAL`

**Evidence:** Third-party evaluation report or certification (vendor-issued or
independent — e.g., MITRE ATT&CK Evaluation, MSSP alert validation report).

**Draft answer:**
> "Our MDR platform vendor ([vendor name]) has participated in the following
> independent third-party evaluation(s) within the past 3 years: [evaluation name,
> year, public reference URL — e.g., MITRE ATT&CK Enterprise Evaluation, Round N,
> Year]. Evaluation results are publicly available at [URL] and available for
> Spectra certifier review on request. [If no public evaluation: description of
> most recent internal or third-party SOC validation exercise with dates.]"

---

### MDR3 — Continuous 24x7x365 security monitoring

**Spectra requirement:** MDR service provides continuous 24x7x365 monitoring for
all in-scope assets. Security telemetry from all in-scope assets ingested into a
centralized platform, monitored continuously. Threat intelligence integrated.

**Coverage:** `PARTIAL`

**Liongard evidence:**
```
# Active detections and alerts — confirms monitoring is generating output:
liongard_alert LIST environmentId=<ENV_ID> pageSize=50
  → recent alerts by type, severity, date — demonstrates active 24x7 telemetry

# MDR inspector deployment (if inspector available):
liongard_launchpoint LIST inspectorId=<MDR_INSPECTOR_ID> pageSize=10
  → latestInspectionDate, status → confirms MDR platform is connected and running
```

**Manual evidence:** SOC coverage agreement or SLA (24x7 confirmation); threat
intelligence feed integration documentation; centralized platform architecture diagram.

**Draft answer:**
> "The MDR service provides 24x7x365 security monitoring via [MDR platform / SOC partner].
> Security telemetry from all [N] in-scope endpoints, [N] identities, and [cloud workloads]
> is ingested into the centralized platform. Monitoring is continuous — no coverage gaps.
> Threat intelligence from [feed sources — e.g., MITRE ATT&CK, vendor TI feeds, MS-ISAC]
> is integrated and correlated against ingested telemetry. Alert activity from Liongard
> inspection as of [date] confirms active detection output. [Attach: SOC coverage SLA;
> TI integration documentation excerpt.]"

---

### MDR4 — PSA vendor record retention ≥ 6 months

**Spectra requirement:** MSP/MSSP's PSA vendor retains incident and ticket records
for a minimum of 6 months. Documented retention system configuration shows the
configured retention policies.

**Coverage:** `PARTIAL`

**Liongard evidence (if PSA inspector deployed):**
```
# PSA inspector (ConnectWise Manage, Autotask, HaloPSA, etc.):
liongard_launchpoint LIST inspectorId=<PSA_INSPECTOR_ID> environmentId=<MSP_ENV_ID>
  → confirms PSA inspector is active and recent

# Retention configuration (if exposed in dataprint):
liongard_metric EVALUATE jmesPathQuery="<retention-policy-path>"
  systemId=<PSA_SYSTEM_ID> environmentId=<MSP_ENV_ID>
```

**Manual evidence:** PSA retention policy configuration screenshot; vendor
documentation confirming default / configured retention period.

**Draft answer:**
> "Our PSA ([PSA vendor name]) is configured to retain incident and ticket records for
> [N] months (meets or exceeds the 6-month minimum). Retention is set at the [system /
> tenant] level. [Attach: PSA retention configuration screenshot — redact customer
> identifiers. Or: vendor documentation link confirming default retention ≥ 6 months.]"

---

## QA & Manual Verification

After completing all 21 controls, run the following QA checks before producing the
deliverable:

1. **Retry transient nulls** — any MCP call that returned `null` should be retried
   (up to `qa.retry_attempts` times) before marking as SCHEMA_CONFIRMED / PROPOSED.
2. **Flag stale inspectors** — any system where `latestInspectionDate` exceeds
   `qa.flag_inspector_lastseen_threshold_days` (default 7 days) must be flagged in
   the deliverable. Stale data degrades the evidence quality for MDR1 and MDR3
   specifically — Spectra certifiers will notice evidence currency.
3. **Flag count divergence** — if `liongard_identity COUNT` and a per-inspector
   user-count metric differ by more than `qa.flag_count_divergence_threshold_pct`
   (default 5%), surface both values and the divergence as a data-quality note.
4. **MDR1 calculation check** — confirm the endpoint coverage percentage formula
   (see MDR1 section above) is applied consistently across all customer environments
   in scope, not just the MSP's own environment.
5. **Manual items checklist** — every `MANUAL` control must have a named owner and
   a target completion date before submission.

---

## Manual Attestation Checklist

The following items have no Liongard evidence source and require signed attestation
from the named owner before the evidence pack can be submitted to Spectra:

| Control | Item | Owner | Target Date |
|---|---|---|---|
| C01a | SLA exhibit from MSA | Legal / Operations | |
| C01b | IRP document (current version) | IT / CISO | |
| C01c | Staff training completion records (most recent cycle) | HR / IT | |
| C01d | Vendor certification register | HR / IT | |
| C02a | Vendor assessment process documentation | Operations / Procurement | |
| C02b | Patch management policy | IT | |
| C03a/b/c | AI governance evaluation documentation | Management | |
| C04 | Threat intelligence subscription list + review process | IT / CISO | |
| C05 | Customer authentication procedure (helpdesk runbook) | Operations | |
| C06 | Most recent pen test executive summary | IT / CISO | |
| C06 | Quarterly vulnerability scan results | IT | |
| C06 | Vulnerability remediation log (<7 day high/critical) | IT | |
| C12a | Change management policy | IT | |
| C12b | Staged rollout procedure / example change record | IT | |
| C13 | Out-of-scope system register + customer sign-off | Account Management | |
| C15 | SOC / MDR coverage agreement | IT / CISO | |
| C15 | Escalation matrix | IT / CISO | |
| C16 | BCP / cross-tenant segmentation architecture | IT / CISO | |
| C17 | MSA / SOW template (table of contents) | Legal | |
| MDR2 | Third-party evaluation report reference | IT / CISO | |
| MDR3 | SOC 24x7 coverage SLA + TI integration docs | IT / CISO | |
| MDR4 | PSA retention configuration screenshot | IT | |

---

## Coverage Summary

| Control ID | Description | Liongard Coverage |
|---|---|---|
| C01a | SLAs in contracts | MANUAL |
| C01b | Standardized IR procedures | MANUAL |
| C01c | Helpdesk training | MANUAL |
| C01d | Vendor certifications | MANUAL |
| C02a | Vendor due diligence | MANUAL |
| C02b | Patch testing / software security | PARTIAL |
| C03a/b/c | AI use evaluation | MANUAL |
| C04 | Threat intelligence | PARTIAL (dark web) |
| C05 | Customer auth / change approval | MANUAL |
| C06 | Pen testing / vuln scanning | PARTIAL (open ports + patch age) |
| C07 | Phishing training | PARTIAL (KnowBe4 if deployed) |
| C08a | Secure device build | PARTIAL (new device EDR enrollment) |
| C08b | Restricted access to MSP tools | PARTIAL (identity MFA + stale accounts) |
| C09 | Secure remote access to customers | PARTIAL (open ports + MFA) |
| C10 | MSP device EDR + MDM | PARTIAL (device EDR coverage) |
| C11 | IAM / zero trust / RMM MFA | PARTIAL (identity MFA rates) |
| C12a | Change management policy | MANUAL |
| C12b | Staged rollout testing | MANUAL |
| C13 | Oversight of out-of-scope systems | PARTIAL (Discovery-state assets) |
| C14 | Log management / SIEM | PARTIAL (SIEM inspector + EDR telemetry) |
| C15 | Incident response capabilities | PARTIAL (EDR coverage + alerts) |
| C16 | Catastrophic incident recovery | PARTIAL (backup + EDR + segmentation) |
| C17 | Standardized contracts | MANUAL |
| MDR1 | MDR endpoint/server/identity coverage | **LIONGARD** |
| MDR2 | Third-party evaluation | MANUAL |
| MDR3 | 24x7 continuous monitoring | PARTIAL |
| MDR4 | PSA ticket retention ≥ 6 months | PARTIAL |

**Summary:** Of 27 standard IDs, **1 is fully answerable from Liongard** (MDR1);
**11 have partial Liongard evidence** that reduces but does not eliminate the manual
attestation burden; **15 require complete manual attestation**.

The highest Liongard leverage is in the MDR domain (MDR1, MDR3) and the technical
protect controls (C10, C11, C08a/b, C09).

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | MDR1 endpoint enrollment and EDR coverage metrics align with the onboarding EDR coverage section. The six standard endpoint questions (total managed, active 30d, inactive 60d+, not protected, server/workstation split, high alerts) are used in MDR1 evidence computation. |
| CIS Controls (v8.1) | ✅ | C10/MDR1 → CIS 4 (Secure Configuration), CIS 10 (Malware Defense); C11/C08b → CIS 5–6 (Account/Access Mgmt); C06 → CIS 7 (Vulnerability Management); C07 → CIS 14 (Security Awareness); C14/MDR3 → CIS 8 (Audit Log Management); C15 → CIS 17 (Incident Response); C16 → CIS 10–11 (Backup / Data Recovery). |
| Cyber-insurance domain files | ✅ | C11 MFA evidence → `domains/auth.md`; C10/MDR1 EDR evidence → `domains/endpoint.md`; C14/MDR3 logging → `domains/network.md` and `domains/governance.md`; C16 backup recovery → `domains/backup.md`. Spectra evidence for these shared controls is compatible with carrier evidence — run this recipe and the relevant domain files share the same Liongard calls. |
| QBR / quarterly-business-review | ✅ | MDR1 endpoint coverage percentage and MFA coverage (C11) are the two most recurring QBR headline metrics. A Spectra certification run produces updated evidence that the QBR Step 4 (posture summary) can directly consume. |

---

## Pairs with

- `cyber-insurance-readiness.md` — shares evidence for CIS-mapped controls (auth,
  endpoint, backup, network domains); run in parallel for carrier renewal
- `cyber-insurance-application-universal.md` — if the MSP is also helping a customer
  complete a carrier application simultaneously
- `recipes/system-type-assessment/all-edrs.md` — MDR1 endpoint enrollment coverage
  across all deployed EDR inspectors
- `recipes/single-system-analysis/by-inspector/knowbe4.md` — C07 phishing training evidence
- `recipes/single-system-analysis/by-inspector/internet-domain-dns.md` — C06 / C09 external posture
- `recipes/single-system-analysis/by-inspector/network-ip-address.md` — C06 / C09 open ports

---

## Output format

The recommended deliverable for a Spectra certifier submission is an **Excel workbook**:

- **Sheet 1 — Evidence Summary:** One row per standard ID, columns for:
  Standard ID | Domain | Requirement (abbreviated) | Coverage | Answer | Evidence Source | Evidence Date | Status
- **Sheet 2 — Manual Attestation Tracker:** Items from the checklist above with
  Owner, Due Date, Completion Date, and attachment reference
- **Sheet 3 — Liongard Verification Log:** Every MCP call made during evidence
  collection with system reference, query, result shape, and VALIDATED /
  SCHEMA_CONFIRMED status
- **Sheet 4 — Gap Remediation Plan:** Any control with status ❌ NON-COMPLIANT,
  with recommended action and target date

For a Word document variant, use one section per domain (Govern → Identify →
Protect → Detect → Respond/Recover → MDR → Contract) with each control as a
subsection containing question, answer, and evidence citations.

---

## Verification log

The agent appends every MCP call made during evidence collection.

| Path / Query | System Reference | Result Shape | Status |
|---|---|---|---|
| `liongard_identity COUNT mfaStatus="NO" enabled=true` | MSP internal environment | `{ Count: <int> }` | VALIDATED |
| `liongard_identity COUNT privileged=true mfaStatus="NO"` | MSP internal environment | `{ Count: <int> }` | VALIDATED |
| `liongard_device LIST detail=full` (compute devices, edr field) | MSP internal environment | Array of device records; edr field populated for locally-inspected devices | VALIDATED |
| KnowBe4 phishing campaign last date | Confirm with inspector | Array or null if not deployed | SCHEMA_CONFIRMED |
| Dark web monitoring domain exposure | Confirm with inspector | Credential exposure records | SCHEMA_CONFIRMED |
| PSA retention configuration | Confirm per PSA inspector | May be null if not in dataprint | PROPOSED |
| ITDR module configuration | Confirm per MDR inspector | Varies by MDR platform | PROPOSED |

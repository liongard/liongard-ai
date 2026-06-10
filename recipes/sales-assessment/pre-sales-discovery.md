---
name: pre-sales-discovery
description: >
  Use this skill when the user wants a pre-sales discovery assessment for
  a prospect — turning a Liongard read-only inspection (or trial-tenant
  installation) into a compelling MSP proposal. Discovery variant of the
  cross-cutting recipe pattern — point-in-time current-state assessment
  framed as risk + opportunity findings that a prospect's leadership will
  recognize as "you understand my environment". Trigger phrases: "pre-sales
  discovery for a prospect", "sales assessment for a prospect", "discovery
  call deck", "prospect MSA / RFP response", "MSP proposal for a prospect",
  "sales deck", "free assessment for a prospect", "sales pitch deck",
  "what's in the prospect environment", "discovery findings". Auto-discovers
  the prospect's deployed stack, chains per-class recipes with executive
  tone, then frames findings as risk-opportunity pairs scoped to the MSP's
  service offering. Produces an executive-friendly PowerPoint discovery
  deck plus a Word findings letter — same content the prospect's CFO and
  IT director can both read.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_timeline, liongard_cyber_risk_dashboard, liongard_device, liongard_identity, liongard_domain, liongard_metric. liongard_detection and liongard_alert are optional — relevant only if the prospect has been monitored long enough to produce signal."
personas: [sales, vcio-account-manager, executive, technical-alignment-manager]
output_formats: [pptx, word, markdown, xlsx]
primitives: []
composes:
  - recipe:domain:domain-assessment-external-attack-surface-deep-dive
  - recipe:onboarding:new-customer-onboarding
  - recipe:single-system:single-system-active-directory
  - recipe:single-system:single-system-knowbe4
  - recipe:single-system:single-system-microsoft-365
  - recipe:system-type:system-type-all-backups
  - recipe:system-type:system-type-all-domains
  - recipe:system-type:system-type-all-edrs
  - recipe:system-type:system-type-all-external-attack-surface
  - recipe:system-type:system-type-all-firewalls
  - recipe:system-type:system-type-all-hypervisors
  - recipe:system-type:system-type-all-servers
---

# Pre-Sales Discovery — Master Recipe

> **The canonical sales-discovery deliverable.** A point-in-time
> current-state assessment of a prospect's environment, framed as
> *risk-opportunity pairs* the MSP can address. The output is two things
> at once: a credibility document ("you really do understand my
> environment") and a proposal foundation ("here's what we'd do in the
> first 90 days").
>
> **Discovery-variant of the cross-cutting pattern.** Drops time-bounded
> sections (no detections / alerts / timeline-in-window content — a
> prospect under read-only assessment doesn't have a trustworthy
> historical window) and adds **risk-framing** to every per-class
> finding (every observation paired with a business consequence).
>
> **Differs from onboarding intake.** Onboarding's audience is the
> prospect *after* they've signed; the gap analysis is direct and
> prescriptive. Discovery's audience is the prospect *before* they've
> signed; findings are framed as risks the MSP would address, with
> care taken not to embarrass the prospect's current vendor or IT staff.
> Use executive tone by default.
>
> **Customer-stack-adaptive.** Calls `liongard_system LIST` to discover
> deployed inspectors; the recipe doesn't assume the prospect has the
> MSP's preferred stack. Findings reference what's deployed; the
> sales narrative recommends what would be deployed if engaged.
>
> **References:** `reference/cross-cutting-signals.md`,
> `reference/asset-fields.md`, `reference/qa-retry-pattern.md`,
> `reference/inspector-aliases.md`,
> `reference/personas-recipe-matrix.md`.


---

## Customize for your MSP

```yaml
output:
  format: pptx                           # pptx | word | markdown | xlsx
                                         # Default: executive discovery deck.
                                         # Use word for the findings letter;
                                         # xlsx for the supporting data appendix;
                                         # markdown for working drafts.
  filename: "<prospect>-Discovery-<date>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  cover: "Discovery Findings"
  about: "About <Your MSP Name>"
  scope: "What We Looked At"
  executive_summary: "Executive Summary"
  current_state: "What We Found"
  risk_opportunities: "Risks & Opportunities"
  service_alignment: "How We'd Help"
  proposal_summary: "Recommended Engagement"
  appendix: "Appendix — Methodology"
  verification_log: "Verification Log"

audience:
  tone: "executive"                      # technical | balanced | executive
                                         # Default executive — discovery's audience is
                                         # prospect leadership (owner / CFO / IT director).
                                         # Override to balanced for the IT-director-only
                                         # version; technical only for engineer-led calls.
  reading_level: "executive"

discovery_framing:
  lead_with_business_impact: true        # "downtime exposure" not "no backup configured"
  pair_finding_with_recommendation: true # every finding gets a one-line "we'd address this by..."
  preserve_current_vendor_dignity: true  # avoid language that disparages the prospect's
                                         # current IT staff or vendors
  surface_no_issue_categories: true      # "Identity is well-managed" reads as credibility
                                         # (not everything is broken — say so when true)
  redact_specific_asset_names: false     # default false — prospect IT director appreciates
                                         # seeing the actual hostnames. Set true if compliance
                                         # / NDA scope requires generic placeholders.
  include_competitive_context: false     # set true if the MSP wants a "compared to industry
                                         # baseline" slide

stack:
  auto_discover: true
  inspectors_in_scope: []
  inspectors_to_skip: []
  trial_install_mode: true               # tells the recipe to treat freshness gaps as
                                         # "still settling" rather than "stale credentials";
                                         # most prospects are mid-trial when this recipe runs

  # External attack surface depth — controls Phase 0
  use_domain_deep_dive: false            # true | false
                                         # false (default): chain the fleet-breadth rollup
                                         #   (recipes/system-type-assessment/all-external-attack-surface.md)
                                         #   Works best for prospects with 4+ monitored domains.
                                         # true: chain the domain-focused deep-dive
                                         #   (recipes/domain-assessment/external-attack-surface-deep-dive.md)
                                         #   Recommended for BEC-focused conversations, prospects
                                         #   with 1–3 primary domains, or when the discovery
                                         #   conversation centers on email fraud / phishing risk.
                                         #   Produces BEC-risk scoring, SaaS footprint map,
                                         #   DKIM selector audit, MX filter stack ID, and
                                         #   subdomain WAF/CDN fingerprinting.

per_class_recipe_overrides:
  # cisco-meraki-inspector: "<msp-local>/meraki-discovery-custom.md"

msp_service_offering:
  # The MSP's catalog. Used to map findings → "how we'd help" recommendations.
  # Each finding category maps to one or more service offerings.

  managed_it: true
  managed_security: true
  managed_backup: true
  managed_firewall: true
  managed_m365: true
  cyber_insurance_readiness: true
  vciso: false
  compliance_consulting: false           # CMMC, HIPAA, PCI — set true if MSP offers
  cloud_migration: false
  staff_augmentation: false

msp_preferred_stack:
  # INHERITS from config/msp-config.yaml `preferred_stack` block.
  # Override per-deliverable ONLY when a specific prospect engagement
  # needs a different recommended stack (e.g., the prospect's vertical
  # requires a different EDR than the MSP's standard). To override,
  # uncomment the relevant keys and set explicit values.
  #
  # edr: "<your-standard-edr-slug>"
  # backup: "<your-standard-backup-slug>"
  # firewall: "<your-standard-firewall-slug>"
  # awareness_training: "knowbe4"
  # dns_filtering: "cisco-umbrella"
  # identity_baseline_mfa_pct_min: 95
  # patch_cadence_days: 30

risk_framing:
  # Tone / wording overrides for the risk language. MSP can dial up or
  # down based on prospect industry (legal vs. retail vs. healthcare).
  use_dollar_impact_language: false      # set true if MSP has industry-vertical
                                         # downtime-cost benchmarks to cite
  use_compliance_language: false         # set true for healthcare / finance prospects
                                         # — surfaces HIPAA / PCI / SOC2 implications
  emphasize_business_continuity: true    # downtime / restore framing reads broadly

verification:
  log_queries: true
  redact_values: true                    # default true for discovery — sensitive prospect data

qa:
  retry_on_null: true
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 14   # discovery / trial-install mode
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: false              # don't expose "[PROPOSED]" labels to prospect
  surface_single_source_visibility: true
  manual_verification_section_required: true
```

---

## When to use

- "Pre-sales discovery for <prospect>"
- "Sales assessment for <prospect>"
- "Discovery call deck"
- "MSP proposal for <prospect>"
- "Free assessment for <prospect>"
- "Sales pitch deck"
- "Discovery findings for <prospect>"
- "What's in the prospect environment?"
- "Findings letter for the prospect after the discovery call"

Cadence: once per prospect (sometimes twice — discovery deck during
late-stage sales, refreshed findings letter at proposal time). After
prospect signs, transition to the onboarding intake
(`recipes/onboarding-assessment/new-customer-onboarding.md`) — the
onboarding recipe inherits findings from this discovery and elevates
them to the 30 / 60 / 90 remediation plan.

Personas:
- **Sales** (primary — owns the discovery conversation and proposal)
- **vCIO / Account Manager** (joins discovery calls; co-author of
  findings letter; in many MSPs, vCIO replaces sales for this recipe)
- **Executive** (the prospect's leadership — the consumer of the deck)
- **TAM** (advisory — confirms the findings are accurate before deck
  ships to prospect)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` → match by prospect name |
| Prospect name | No | Used for filename + report header |
| Decision-maker context | No | Free-text — who the deck is for (owner / CFO / IT director); informs tone |
| Optional: industry vertical | No | If specified, recipe pulls in vertical-specific compliance framing |
| Optional: incumbent provider context | No | Free-text — informs the "preserve_current_vendor_dignity" framing |

---

## Workflow — discovery variant of the cross-cutting pattern

This recipe is the **discovery variant** of the cross-cutting pattern
documented in `reference/cross-cutting-signals.md`. It is closest to the
onboarding-intake variant (point-in-time, gap-analysis-driven) but
diverges in:

- **Tone:** executive by default; risk-framing throughout
- **Trial-install mode:** stale-data thresholds are loosened because
  inspectors are typically mid-deployment
- **Sales framing:** every finding paired with a service-offering
  recommendation
- **Vendor dignity:** findings are described as risks the MSP would
  address, not as criticism of the prospect's current vendor

### Phase 0 — External Attack Surface (zero-credential)

> **Run this phase before any credentialed steps.** The four external-
> attack-surface inspectors (Internet Domain / TLS / Network IP /
> Dark Web) require **only public identifiers** from the prospect —
> a list of domain names, a few public IPs, and the customer-facing
> hostnames. No password, no agent install, no agreed inspection
> window. This is the lowest-friction discovery moment available
> and should always lead the engagement.

Choose the Phase 0 depth based on `stack.use_domain_deep_dive`:

#### Path A — Fleet-breadth rollup (default: `use_domain_deep_dive: false`)

Best for prospects with 4+ monitored domains, or when the discovery
conversation is centered on endpoint / backup / identity risk with
external posture as a supporting signal.

```
# Chain the external-attack-surface rollup
include recipes/system-type-assessment/all-external-attack-surface.md
  with scope_inputs.mode = "discovery" (or "credentialed" if trial env exists)
       scope_inputs.domains = <prospect domains>
       scope_inputs.ip_addresses = <prospect public IPs (optional)>
       audience.tone = "executive"
       narrative.preserve_current_vendor_dignity = true
       narrative.redact_individual_users = true
```

#### Path B — Domain deep-dive (`use_domain_deep_dive: true`)

Recommended for:
- Prospects where BEC / phishing / email fraud risk is the conversation anchor
- Prospects with 1–3 primary domains (deep-dive is per-domain; fleet rollup
  is more efficient for large fleets)
- Discovery conversations where the decision-maker recognizes email security
  as a top concern (financial services, healthcare, legal)
- Pre-engagement situations where a dark-web credential count alone needs
  a richer BEC-risk narrative to drive urgency

```
# Chain the domain deep-dive (per primary domain)
include recipes/domain-assessment/external-attack-surface-deep-dive.md
  with scope_inputs.mode = "discovery" (or "credentialed")
       scope_inputs.domain = <primary prospect domain>
       audience.tone = "executive"
       discovery_framing.preserve_current_vendor_dignity = true
       discovery_framing.redact_individual_users = true
       # The deep-dive produces a BEC risk score (Low/Medium/High/Critical)
       # and a combined risk story: spoofability + credential exposure +
       # SaaS attack surface + filter stack. Use the BEC risk score as the
       # discovery deck's headline finding for the domain slide.
```

For multi-domain prospects (2–3 primary domains) with `use_domain_deep_dive: true`,
run the deep-dive per domain and roll up the BEC risk scores to the highest-severity
tier for the deck. Individual domain results go to the IT-director appendix.

Capture the **combined risk story** from the selected path (e.g., "spoofable
+ breached", "BEC High — spoofable domain + unfiltered MX + 23 exposed credentials")
as the discovery deck's anchor finding. These cumulative findings are the recipe's
highest-credibility content because no incumbent provider has surfaced them.

> **Why Phase 0 changes the discovery sequence:** the rollup or deep-dive produces
> findings the prospect can verify themselves (DMARC records, public
> certs, IP reputation, dark-web counts), giving the MSP credibility
> *before* asking for credentialed access. By the time the prospect
> agrees to a credentialed trial, the MSP is no longer cold-pitching;
> they're addressing already-acknowledged risks.

### Step 1 — Scope discovery

```
liongard_environment LIST searchMode=keyword query="<prospect-name>"
# Confirm environmentId. Discovery is usually one environment per
# prospect; multi-environment prospects (parent + subsidiaries) require
# explicit per-environment scoping.
```

### Step 2 — Inspector freshness (trial-install mode)

```
liongard_timeline LIST environmentId=<ENV_ID>
```

In trial-install mode (`customization.stack.trial_install_mode: true`,
default), stale-inspector flags use the longer grace period from
`qa.flag_inspector_lastseen_threshold_days` (default 14 days).
Inspectors still settling produce a confidence flag but **do not** show
up as gaps in the deck — that would surface a deployment-side issue as
a prospect finding, which damages credibility.

### Step 3 — Headline KPIs from the cyber-risk dashboard

```
liongard_cyber_risk_dashboard <metric>  environmentId=<ENV_ID>
```

For the discovery deck, headline KPIs are framed as **business
indicators**:

| KPI | Metric | Business framing |
|---|---|---|
| User count | `m365TotalUsers` + `activeDirectoryTotalUsers` | "Environment scale" |
| Workstation + server count | `workstationTotalCount`, `winServerTotalCount`, macOS / Linux totals | "Infrastructure footprint" |
| MFA coverage | (dashboard metric) | "Identity protection level" |
| EDR coverage | (dashboard metric) | "Endpoint security level" |
| Servers without backup coverage | computed Step 5 cross-recipe join | "Business-continuity exposure" |
| Domain count + DMARC posture | `domainAndWebsiteSecurityTotalDomains` + Step 4 | "Email & domain trust signal" |

### Step 4 — Current-state inventory snapshot

> **Reconciled asset inventory is the primary source for prospect
> counts** — dedup'd across every inspector. Use `liongard_identity`
> (keyed on email), `liongard_device` (keyed on hostname / serial /
> MAC), and `liongard_domain` (keyed on domain name) directly. Per-
> inspector metrics are reserved for the credentialed deep-dive
> sections that follow. See `reference/asset-fields.md` § Deduplication
> keys.

```
liongard_device COUNT environmentId=<ENV_ID>
liongard_device LIST environmentId=<ENV_ID>
                     fields=["hostname","operatingSystem","manufacturer","serialNumber","class","role","warrantyExpiration","winElevenReady","inspectors","lastSeen"]

liongard_identity COUNT environmentId=<ENV_ID>
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true
liongard_identity COUNT environmentId=<ENV_ID> privileged=true

liongard_domain LIST environmentId=<ENV_ID>
                     fields=["domainName","registrar","daysTillExpiration","registrarLock","dmarcHealth","inspectors"]
```

In discovery mode, the inventory tables move to the **appendix**. The
deck body uses summary-level counts only ("approximately 50 users",
"a fleet of around 60 workstations") — exact figures stay in the
appendix for the IT-director audience.

### Step 5 — Auto-discover deployed stack + chain sub-recipes

```
liongard_system LIST environmentId=<ENV_ID>
```

Chain the appropriate system-type and single-system recipes with
`audience.tone: "executive"` inherited:

| Prospect has… | Chained recipe |
|---|---|
| Windows Servers + Workstations | `recipes/system-type-assessment/all-servers.md` + `all-endpoints.md` |
| Any EDR (or multiple — common at prospects) | `recipes/system-type-assessment/all-edrs.md` |
| Firewalls | `recipes/system-type-assessment/all-firewalls.md` |
| Backups (any vendor) | `recipes/system-type-assessment/all-backups.md` |
| Hypervisors | `recipes/system-type-assessment/all-hypervisors.md` |
| M365 tenant | `recipes/single-system-analysis/by-inspector/microsoft-365.md` |
| AD | `recipes/single-system-analysis/by-inspector/active-directory.md` |
| KnowBe4 | `recipes/single-system-analysis/by-inspector/knowbe4.md` |
| Domains | `recipes/system-type-assessment/all-domains.md` |
| External attack surface — fleet breadth (`use_domain_deep_dive: false`) | `recipes/system-type-assessment/all-external-attack-surface.md` (already chained in Phase 0) |
| External attack surface — BEC-focused deep-dive (`use_domain_deep_dive: true`) | `recipes/domain-assessment/external-attack-surface-deep-dive.md` (already chained in Phase 0; per primary domain) |

Inherit `audience.tone: "executive"` so chained outputs use the right
vernacular. Extract **the top 3 findings + recommendations** from each
chained run — not the full output — and consolidate.

> **The deck is a curated story, not a data dump.** Pick the findings
> that pair with the MSP's service offering and the prospect's
> decision-maker context. Discard the rest into the appendix.

### Step 6 — Risk-opportunity framing

For each finding from Step 5, re-frame as a **risk-opportunity pair**:

```
For each finding:
  observation     = the underlying fact (counts, configuration, status)
  business_impact = the consequence to the prospect's business
                    (downtime, compliance, data loss, productivity)
  recommendation  = how the MSP would address it
  service_match   = which service offering(s) this maps to
                    (from msp_service_offering customization)
  severity        = Critical / High / Medium / Low
  quick_win       = boolean — true if MSP can demonstrate value in
                    first 30 days
```

Discard findings where:
- The MSP doesn't offer a corresponding service
  (set `msp_service_offering.<offering>: false`)
- The finding is administrative noise (e.g., naming conventions)
- The risk language would embarrass the prospect's current vendor
  unnecessarily

### Step 7 — Service-alignment narrative

For each finding category, map to an MSP service offering and surface
in the "How We'd Help" section:

| Finding category | Service offering | Typical narrative beat |
|---|---|---|
| MFA / privileged access gaps | Managed IT + Managed Security | "We enforce MFA on day 1; privileged accounts get a hardened standard." |
| Unprotected endpoints / servers | Managed Security | "Our standard EDR covers your full fleet, with 24/7 SOC monitoring." |
| Backup coverage gaps | Managed Backup | "Every server lands in our 3-2-1 backup standard with offsite replication." |
| Firewall configuration drift | Managed Firewall | "We baseline your firewall to our hardened standard and monitor configuration changes." |
| Domain / email-trust gaps | Managed IT + Managed M365 | "We enforce DMARC, registrar lock, and SPF/DKIM as part of our standard." |
| Patching / lifecycle exposure | Managed IT | "Our monthly patch cadence keeps you within <SLA> days of release." |
| Phishing / awareness training gap | Managed Security | "We deploy KnowBe4 with a structured monthly campaign cadence." |
| Cyber-insurance gaps | Cyber-insurance readiness | "We complete your renewal questionnaire from Liongard data — no internal scramble." |
| Compliance gaps (HIPAA/PCI/CMMC) | Compliance consulting | "We map your environment to <framework> controls and own the evidence pack." |

When a service offering is `false` in `msp_service_offering`, the
recipe **omits** corresponding findings from the deck. This keeps the
narrative tight and avoids implying a service the MSP doesn't deliver.

### Step 8 — Quick wins enumeration

Pull the findings tagged `quick_win = true` into a dedicated "First 30
Days" slide. This is the proposal's anchor: tangible, fast progress the
prospect can see during the early engagement. Examples:

- Enable DMARC monitoring on domains
- Configure registrar lock
- Deploy EDR to unprotected servers
- Enforce MFA on privileged accounts
- Apply backlogged critical patches

### Step 9 — QA pass (per `reference/qa-retry-pattern.md`)

This recipe's QA pass especially focuses on:

1. **Retry persistent nulls** on the cyber-risk-dashboard metrics.
2. **Flag stale inspectors** with trial-install thresholds (Step 2).
   Stale-inspector findings stay in the verification log; they do **not**
   leak into the deck.
3. **Cross-tool divergence checks** — exact counts matter less for an
   executive deck, but the IT-director audience appreciates seeing the
   recipe was rigorous. Divergence notes belong in the verification log.
4. **Proposed-metric gaps** — discovery mode suppresses these from the
   prospect-facing output (`qa.surface_proposed_metrics: false`); they
   appear in the verification log only.
5. **Single-source visibility** — surface in the appendix as data-quality
   context, not as findings.
6. **NDA / scrub check** — confirm no specific user names, email
   addresses, or sensitive content has leaked through into the
   deck-body text. The customization block's `verification.redact_values`
   defaults to true for discovery.

### Step 10 — Render the discovery deliverables

The discovery output is **two deliverables by default**:

#### A. Executive discovery deck (pptx — primary)

Recommended slide order:

| # | Slide | Content |
|---|---|---|
| 1 | Cover | Prospect, MSP name + logo, "Discovery Findings", date |
| 2 | About | Brief MSP intro (omit if presenting live) |
| 3 | What We Looked At | Inspector inventory — "We reviewed X systems across Y categories." |
| 4 | Executive Summary | 3–5 outcome bullets. Lead with the headline story. |
| 5 | What We Found — Identity & Access | 2–3 findings, risk-framed |
| 6 | What We Found — Endpoints & Devices | 2–3 findings |
| 7 | What We Found — Network & Perimeter | 2–3 findings |
| 8 | What We Found — Backup & Continuity | 2–3 findings |
| 9 | What We Found — Domains & Email | 2–3 findings |
| 10 | Risks & Opportunities | Roll-up — categorized risk register |
| 11 | How We'd Help | Service-alignment narrative |
| 12 | First 30 Days | The Step 8 quick-wins slide |
| 13 | Recommended Engagement | Service offering + cadence + initial roadmap |
| 14 | Next Steps | CTAs — proposal, technical deep-dive, references |

Slides 5–9 are omitted for any category where the prospect has no
relevant inspector (e.g., no domains discovered → skip the domain
slide rather than adding a "we don't have visibility" beat that reads
as weakness).

#### B. Findings letter (word — secondary)

Same content in prose form, addressed to the prospect's decision-maker.
A typical sales motion sends the deck for the live conversation and
follows up with the findings letter as a leave-behind document the
decision-maker can share internally.

#### C. Data appendix (xlsx — optional)

Inventory tables (devices / identities / domains) for the IT-director
audience who wants to verify the findings against their CMDB.

### Tone-driven adaptations

When `audience.tone == "executive"` (default):
- Drop all JMESPath / metric details from the deck body
- Replace device-class language ("Windows Server 2019") with risk
  language ("aging server infrastructure")
- Section headings use business language

When `audience.tone == "balanced"` (the IT-director-only version):
- Keep counts + vendor names + the deeper finding context
- Include the inventory tables in the deck body, not appendix-only

When `audience.tone == "technical"`:
- All counts, vendor names, JMESPath references, model numbers
- Suitable for engineering-led discovery calls

---

## QA & Manual Verification

The Step 9 detail above is the recipe-specific QA pass. The canonical
pattern lives in `reference/qa-retry-pattern.md`. Every discovery run
produces a **Manual Verification Needed** appendix per that pattern —
internal-only for sales discovery (the prospect does NOT receive the
verification log).

Manual checks specific to discovery:

- Confirm the inspector-coverage scope matches what the prospect agreed
  to (don't surface findings from systems outside the agreed
  read-only scope)
- Confirm NDA compliance on the redact_values setting
- Sanity-check the findings narrative for any language that would
  embarrass the prospect's current vendor or staff — adjust before
  the deck ships
- Confirm the service-alignment narrative matches the actual MSP
  catalog at the time the deck is sent

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | Discovery Phases 0–2 map directly to the onboarding QA matrix. Gaps surfaced here become the onboarding intake scope when the prospect signs. The discovery deliverable is structured to minimize re-work at onboarding — same inspector chain, same finding categories, same recommended-action format. |
| CIS Controls (v8.1) | partial | Non-credentialed discovery covers only externally observable posture: CIS 9.4/9.5 (DMARC + email auth — observable via DNS), 12.2 (internet-exposed services — open ports, TLS posture), 13.1 (threat intel — IP reputation checks), 14.6 (dark-web credential exposure as a DLP proxy). Full CIS coverage across identity, endpoint, backup, and internal network requires credentialed onboarding post-sign. |
| Cyber-insurance domain files | partial | Discovery surfaces pre-sale indicators across domains: `domains/auth.md` (dark-web exposure hints at MFA gaps), `domains/network.md` (open ports + TLS posture), `domains/backup.md` (absence of backup vendor signals in DNS/TXT), `domains/governance.md` (documentation gaps inferred from public posture). All domains reach full coverage at credentialed onboarding post-sign. |
| QBR / quarterly-business-review | ✅ | Discovery output becomes the QBR day-zero baseline if the prospect converts. The discovery deliverable structure mirrors the QBR template to reduce conversion friction — the first QBR is a credentialed re-run of this recipe. |

---

## Insights & recommendations — generation patterns

Findings in discovery mode follow a **risk-opportunity-recommendation**
template: state the observation, frame the business impact, propose
the MSP's response. Severity language is softer than in the onboarding
recipe — discovery uses "exposure" / "opportunity" / "risk", not
"critical gap" / "must fix".

| Pattern | Discovery-tone narrative |
|---|---|
| MFA coverage below SLA | "Roughly <N>% of users currently rely on password-only access — a known attack vector that our MFA standard would address." |
| Privileged account without MFA | "Privileged accounts without MFA represent the highest-value target for ransomware actors — we'd remediate as part of week-one work." |
| EDR coverage gap | "<N> servers / endpoints lack modern threat detection. Our managed EDR includes 24/7 SOC monitoring across the full fleet." |
| Unprotected server | "<N> production servers lack endpoint protection. We'd deploy our standard EDR within the first 30 days." |
| Critical patches pending | "Patch currency is one of the strongest indicators of operational maturity. Our managed cadence keeps you within <SLA> days." |
| Firewall firmware out of date | "Aging firewall firmware exposes the perimeter to known vulnerabilities. Our managed firewall service maintains vendor-supported firmware." |
| Open RDP / risky firewall rules | "We observed firewall rules that may expose internal services to the public internet. Our hardened firewall baseline would address this." |
| Servers without backup | "<N> servers lack any backup coverage. Our managed backup service covers every production system with offsite replication." |
| DMARC not enforced | "Your email-sending domains are vulnerable to spoofing. We'd implement DMARC enforcement as part of our managed M365 service." |
| Domain registrar lock missing | "Without registrar lock, your domains could be hijacked. We enable registrar lock on every customer domain." |
| Win10 EOL exposure | "Windows 10 reaches end-of-support in October 2025. We'd build a refresh roadmap to align with your fiscal-year planning." |
| Vendor sprawl (multiple EDRs / backups) | "Multiple overlapping <category> products suggest opportunity for consolidation, simplification, and licensing savings." |
| Cyber-insurance question gaps | "Your environment can already answer <N>% of common cyber-insurance application questions — we'd own the evidence pack going forward." |

When `risk_framing.use_dollar_impact_language == true`, append rough
dollar-impact estimates from industry benchmarks (downtime cost / breach
cost) — but only when the MSP has vertical-specific data to cite. Never
fabricate dollar figures.

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Prospect-specific business KPIs | external | Discovery call notes |
| Headcount / revenue / industry vertical | external | CRM (HubSpot / Salesforce / etc.) |
| Vendor portal-only data | external | Vendor consoles (if granted access during trial) |
| Restore-test history | not in dataprint | Prospect's existing documentation |
| Physical / facility security | external | Discovery call notes |
| Compliance posture (HIPAA / PCI / CMMC) | partial via Liongard for some inspectors | Prospect's existing compliance documentation + dedicated CMMC/HIPAA recipes |
| Existing MSA / SOW with incumbent provider | external | Discovery call notes |

---

## Output format

`pptx` (default — discovery deck) is the canonical primary deliverable.
Supplement with:

- **Word** findings letter — the leave-behind document
- **Excel** data appendix — for the IT-director audience
- **Markdown** working draft — useful for the AE to edit before
  generating the prospect-facing pptx

See `templates/output-block-pptx.md`, `templates/output-block-word.md`,
and `templates/output-block-xlsx.md` for layout conventions.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 0a | all-external-attack-surface.md (if use_domain_deep_dive=false) | scope=discovery domains=<list> | combined risk story | ok |
| 0b | external-attack-surface-deep-dive.md (if use_domain_deep_dive=true) | scope=discovery domain=<primary> | BEC risk score + combined risk story | ok |
| 1 | liongard_environment LIST | query=<prospect> | array<environment> | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok (trial-install thresholds) |
| 3 | liongard_cyber_risk_dashboard | per-metric | <integer> | ok per metric |
| 4 | liongard_device / identity / domain LIST + COUNT | envId=<ENV_ID> [filters] | varies | ok |
| 5 | liongard_system LIST + chained sub-recipes (executive tone) | envId=<ENV_ID> | array<system> + per-recipe top-3 findings | ok per class |
| 6 | (risk-opportunity framing — derived) | per discovery_framing | array<finding> | ok |
| 7 | (service alignment — derived) | per msp_service_offering | mapping table | ok |
| 8 | (quick wins — derived from Step 6) | per discovery_framing | array<quick-win> | ok |
| 9 | QA pass | per `reference/qa-retry-pattern.md` (discovery suppressions) | varies | ok |
| 10 | render | per `output.format` | <artifact path> | ok |
```

---

## Transitioning from discovery to engagement

After the prospect signs, transition to the onboarding intake:

- **Onboarding recipe:**
  `recipes/onboarding-assessment/new-customer-onboarding.md`
- **Discovery findings carry forward:** The risk-opportunity pairs from
  the discovery deck become the seed for the onboarding 30 / 60 / 90 plan.
  Don't re-discover what's already been written into the proposal.
- **Tone shift:** From executive risk-framing (discovery) to balanced
  gap-vs-standard (onboarding). Same underlying findings; different
  language.
- **Re-baseline:** The onboarding recipe runs a fresh inventory snapshot
  to confirm nothing changed in the gap between discovery and signing —
  prospects sometimes adjust their environment when they know the MSP
  is watching.

## Relationship to other cross-cutting recipes

- **Onboarding (`onboarding-assessment/new-customer-onboarding.md`)** —
  same recipe shape, post-signing. Discovery → Onboarding is the
  canonical handoff.
- **Roadmap (`roadmap-planning/refresh-and-lifecycle-roadmap.md`)** —
  use the forward-looking roadmap as a discovery supplement when the
  prospect's conversation is budget-led ("what would IT cost us next
  fiscal year?"). The roadmap's calendar surfaces capex/opex visibility
  that complements the discovery deck.
- **Cyber-insurance readiness (`compliance/cyber-insurance/cyber-insurance-readiness.md`)** —
  when the prospect cares about cyber-insurance renewal, run the
  readiness recipe alongside discovery; pull the "evidence pack
  readiness %" figure into the discovery deck's service-alignment slide.
- **PBR (`environment-quarterly-lookback/quarterly-business-review.md`)** —
  not applicable for prospects (no historical window). Becomes the
  recurring deliverable after the customer signs and completes onboarding.

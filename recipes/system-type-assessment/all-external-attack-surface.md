---
name: system-type-all-external-attack-surface
description: >
  Use this skill when the user wants a whole-environment external
  attack surface posture assessment — the combined story across
  Internet Domain / DNS, TLS/SSL Certificates, Network IP Address,
  and Dark Web Monitoring inspectors. Trigger phrases: "external
  attack surface for <customer>", "external posture audit",
  "perimeter assessment", "outside-in view of <customer>", "what
  does a prospect look like from the internet", "pre-sales external
  audit", "encryption-in-transit posture across the environment",
  "external risk summary". Non-credentialed — produces a complete
  external-posture story from public data alone, making it the
  flagship pre-sales discovery recipe and a core compliance evidence
  source for the encryption-in-transit + identity-exposure questions.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_timeline, liongard_cyber_risk_dashboard, liongard_domain, liongard_identity, liongard_metric"
personas: [sales, vcio-account-manager, soc, technical-alignment-manager, executive]
output_formats: [pptx, word, xlsx, markdown]
primitives:
  - metrics:cloudflare-inspector:zones-active-count
  - metrics:cloudflare-inspector:zones-paused-count
  - metrics:cloudflare-inspector:zones-total-count
  - metrics:dark-web-inspector:breach-details
  - metrics:dark-web-inspector:total-breaches-count
  - metrics:dark-web-inspector:users-breach-list
  - metrics:dark-web-inspector:users-email-list
  - metrics:dark-web-inspector:users-with-data-breach-count
  - metrics:internet-domain-dns-inspector:days-till-expiration
  - metrics:internet-domain-dns-inspector:dkim-found
  - metrics:internet-domain-dns-inspector:dkim-records
  - metrics:internet-domain-dns-inspector:dmarc-agg-reports
  - metrics:internet-domain-dns-inspector:dmarc-exists
  - metrics:internet-domain-dns-inspector:dmarc-policy
  - metrics:internet-domain-dns-inspector:dmarc-record
  - metrics:internet-domain-dns-inspector:dns-a-records
  - metrics:internet-domain-dns-inspector:dns-mx-records
  - metrics:internet-domain-dns-inspector:dns-ns-records
  - metrics:internet-domain-dns-inspector:dns-txt-records
  - metrics:internet-domain-dns-inspector:dnssec
  - metrics:internet-domain-dns-inspector:domain-creation-date
  - metrics:internet-domain-dns-inspector:domain-expiration-date
  - metrics:internet-domain-dns-inspector:domain-name
  - metrics:internet-domain-dns-inspector:domain-status
  - metrics:internet-domain-dns-inspector:email-security-overview
  - metrics:internet-domain-dns-inspector:registrant-contact-email
  - metrics:internet-domain-dns-inspector:registrar
  - metrics:internet-domain-dns-inspector:spf-all-exists
  - metrics:internet-domain-dns-inspector:spf-exists
  - metrics:internet-domain-dns-inspector:spf-record
  - metrics:internet-domain-dns-inspector:spf-record-breakdown
  - metrics:internet-domain-dns-inspector:spoof-intel
  - metrics:internet-domain-dns-inspector:subdomains
  - metrics:internet-domain-dns-inspector:website-http-status-code
  - metrics:internet-domain-dns-inspector:website-https-status-code
  - metrics:internet-domain-dns-inspector:whois-server
  - metrics:network-ip-inspector:asn
  - metrics:network-ip-inspector:asn-info
  - metrics:network-ip-inspector:ip-address
  - metrics:network-ip-inspector:limited-output
  - metrics:network-ip-inspector:reverse-lookup
  - metrics:tls-ssl-inspector:aia-url
  - metrics:tls-ssl-inspector:alt-names
  - metrics:tls-ssl-inspector:cert-exists
  - metrics:tls-ssl-inspector:days-till-expiration
  - metrics:tls-ssl-inspector:expires-on
  - metrics:tls-ssl-inspector:extensions
  - metrics:tls-ssl-inspector:ocsp-url
  - metrics:tls-ssl-inspector:protocol-tls10
  - metrics:tls-ssl-inspector:protocol-tls11
  - metrics:tls-ssl-inspector:protocol-tls12
  - metrics:tls-ssl-inspector:protocol-tls13
  - metrics:tls-ssl-inspector:public-key-algorithm
  - metrics:tls-ssl-inspector:public-key-pin
  - metrics:tls-ssl-inspector:redirects
  - metrics:tls-ssl-inspector:redirects-to
  - metrics:tls-ssl-inspector:sha256-fingerprint
  - metrics:tls-ssl-inspector:ssl-match-names
  - metrics:tls-ssl-inspector:valid-from
---

# System-Type Assessment — All External Attack Surface

> **The canonical external-attack-surface rollup.** Combines four
> non-credentialed inspectors into one whole-perimeter view:
>
> | Inspector | What it answers |
> |---|---|
> | `internet-domain-dns-inspector` (ID 2) | Who owns the domains? Are mail-trust controls (DMARC/SPF/DKIM) in place? Is anything expiring? |
> | `tls-ssl-inspector` (ID 16) | Is data transported with strong, modern, valid encryption? When do certs expire? |
> | `network-ip-inspector` (ID 4) | What's the reputation of the public IPs? What's exposed? Are any IPs on blocklists? |
> | `dark-web-inspector` (ID 4) | Are users' credentials in known breach corpora? |
> | `cloudflare-inspector` (ID 82) — *credentialed* | What's the edge posture (SSL Mode, min-TLS, WAF, Zero Trust) for customer-facing properties fronted by Cloudflare? |
>
> **On Cloudflare:** Unlike the other four inspectors, Cloudflare is
> credentialed (requires API access to the customer's Cloudflare
> account). It's included in this rollup because the edge it fronts
> *is* part of the external attack surface — when Cloudflare proxies a
> customer-facing host, the public's view of TLS / WAF / DDoS
> protection comes from Cloudflare's configuration, not the origin.
> In discovery / pre-sales mode, the Cloudflare section is **omitted**
> unless the MSP already has trial access.
>
> **Zero credentials required.** Every inspector in this set runs on
> public-internet data. The combined recipe is the **flagship pre-sales
> discovery deliverable**: an MSP can produce a real outside-in audit
> of any prospect without asking for a single password.
>
> **References:** Per-inspector recipes in
> `recipes/single-system-analysis/by-inspector/internet-domain-dns.md`,
> `tls-ssl.md`, `network-ip-address.md`, `dark-web-monitoring.md`.
> Also `recipes/system-type-assessment/all-domains.md` (the
> reconciled-domain rollup that complements this recipe), and
> `recipes/sales-assessment/pre-sales-discovery.md` (which chains
> this rollup as its zero-credential discovery foundation).

---

## When this recipe is the right choice

| Scenario | This recipe vs. alternatives |
|---|---|
| Pre-sales discovery — no credentials yet | **This recipe.** Produces a complete outside-in story before any credentialed access. |
| Post-engagement quarterly external audit | **This recipe** for the rollup; combine with the per-inspector singles for any deep-dive section. |
| Cyber-insurance evidence — encryption-in-transit + identity-exposure questions | **This recipe.** Produces the consolidated evidence pack. |
| Domain inventory + DMARC posture only | `recipes/system-type-assessment/all-domains.md` (lighter weight; reconciled-tool only). |
| Single-host TLS check | `recipes/single-system-analysis/by-inspector/tls-ssl.md`. |
| Single-IP reputation triage | `recipes/single-system-analysis/by-inspector/network-ip-address.md`. |
| Identity-exposure deep dive | `recipes/single-system-analysis/by-inspector/dark-web-monitoring.md`. |

---

## Pre-Sales Discovery Value (the flagship motion)

This is the single highest-leverage recipe in the prompt library for
pre-sales. The motion:

1. **Prospect agrees to a Liongard trial OR provides only public
   identifiers** (domain names, public IPs, customer-facing hostnames).
2. **MSP runs this recipe** against a trial environment or a discovery-
   mode environment populated with the public identifiers.
3. **Findings emerge in minutes** — not days, not after a deployment
   project. Mail-trust gaps, expiring certs, blocklisted IPs, exposed
   credentials.
4. **MSP presents the deck.** The combination of findings (DMARC missing
   + TLS 1.0 still supported + IP on Spamhaus + 47 credentials in breach
   corpus) tells a complete external-posture story that no single
   inspector could.
5. **Quick wins are obvious.** Each finding has a 30-day remediation
   path. The proposal anchor writes itself.

> **Why this works:** Most prospects don't know any of these findings.
> Their incumbent provider hasn't surfaced them because the incumbent
> doesn't have outside-in visibility. The MSP that ships this recipe
> as a free assessment immediately differentiates on visibility — the
> hardest thing for a prospect to verify objectively in a competitive
> bake-off.

---

## Customize for your MSP

```yaml
output:
  format: pptx                           # pptx | word | xlsx | markdown
                                         # Default: executive discovery deck.
                                         # Switch to word for a leave-behind letter;
                                         # xlsx for the data appendix;
                                         # markdown for working drafts.
  filename: "<customer-or-prospect>-external-attack-surface-<date>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  cover: "External Attack Surface"
  executive_summary: "Executive Summary"
  scope: "What We Examined"
  domain_posture: "Domain & Mail Trust"
  encryption_posture: "Encryption in Transit"
  ip_posture: "Public IP Reputation & Exposure"
  identity_exposure: "Credential Exposure (Dark Web)"
  combined_findings: "Combined Risk Story"
  recommendations: "Recommended Actions"
  quick_wins: "First 30 Days — Quick Wins"
  data_gaps: "Data Gaps & Manual Verification"
  appendix: "Appendix — Methodology"
  verification_log: "Verification Log"

audience:
  tone: "executive"                      # technical | balanced | executive
                                         # Default executive for the discovery / pre-sales
                                         # motion. Switch to balanced for the IT-director
                                         # leave-behind document; technical for the SOC
                                         # remediation working document.
  reading_level: "executive"

scope_inputs:
  # Two modes — credentialed (everything inspected in Liongard) or
  # discovery (public identifiers provided by the user).
  mode: "credentialed"                   # credentialed | discovery | hybrid
  domains: []                            # ["customer.com", "customer.net"]
  ip_addresses: []                       # ["203.0.113.10", "203.0.113.11"]
  tls_hosts: []                          # ["www.customer.com:443", "mail.customer.com:993"]
  include_dark_web_for_domains: true     # run dark-web inspector on each domain

inspector_baselines:
  # Inherit the per-inspector baselines. The rollup recipe does NOT
  # override individual inspector slas; instead it composes them.
  domain_baseline_recipe: "recipes/single-system-analysis/by-inspector/internet-domain-dns.md"
  tls_baseline_recipe:    "recipes/single-system-analysis/by-inspector/tls-ssl.md"
  ip_baseline_recipe:     "recipes/single-system-analysis/by-inspector/network-ip-address.md"
  dark_web_baseline_recipe: "recipes/single-system-analysis/by-inspector/dark-web-monitoring.md"
  cloudflare_baseline_recipe: "recipes/single-system-analysis/by-inspector/cloudflare.md"
  # Cloudflare is credentialed — chained only when the customer has
  # Cloudflare in scope AND access has been granted. Discovery / pre-sales
  # mode omits this section by default.

include_cloudflare_when_present: true       # set false to suppress in pre-sales mode

narrative:
  lead_with_combined_story: true         # surface the "attackers have both halves" findings
                                         # before per-inspector detail. This is the recipe's
                                         # most-differentiated narrative.
  preserve_current_vendor_dignity: true  # same vendor-dignity stance as pre-sales-discovery
  redact_individual_users: true          # never name individual exposed users in deck
  surface_no_issue_categories: true      # "Mail trust is well-configured" reads as confidence
  quick_wins_required: true              # always produce the 30-day quick-wins list

reporting_period:
  default: "current_state"
  include_breach_recency_section: true   # dark-web "recent exposures" pulled into a sidebar

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

- "External attack surface for <customer>"
- "External posture audit for <customer>"
- "Perimeter assessment"
- "Outside-in view of <customer>"
- "What does the prospect look like from the internet?"
- "Pre-sales external audit"
- "Encryption-in-transit posture across <customer>"
- "External risk summary for the QBR"
- "Cyber-insurance external-posture evidence pack"

Cadence: per prospect (pre-sales); quarterly per customer (rollup as
part of the PBR); ad-hoc for incident response or vendor-disclosure
events (new TLS protocol break, major breach corpus update).

Personas:
- **Sales** (primary — discovery deck)
- **vCIO / Account Manager** (renewal narrative; QBR external section)
- **SOC** (incident — comprehensive outside-in view after a reported
  compromise)
- **TAM** (remediation — surfaces all four families' remediation
  items in one tracker)
- **Executive** (consumes the executive deck as the customer-facing
  external risk story)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes (credentialed mode) | `liongard_environment LIST` |
| Domain list | Yes (discovery / hybrid mode) | User-provided |
| IP list | Optional (discovery / hybrid mode) | User-provided |
| TLS host list | Optional (discovery / hybrid mode) | User-provided |
| Optional: focus area | No | User prompt |

---

## Workflow

### Step 1 — Scope discovery

```
liongard_environment LIST searchMode=keyword query="<customer-or-prospect>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="internet-domain"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="tls"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="cloudflare"   # credentialed — skip in pre-sales
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="network-ip"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="dark-web"
```

Enumerate the systems present from each inspector. In credentialed
mode, surface inspector-gap findings (e.g., "TLS inspector not deployed
— missing critical encryption-in-transit evidence").

### Step 2 — Inspector freshness across all four

```
liongard_timeline LIST environmentId=<ENV_ID>
```

Surface stale inspector findings for each of the four. The Dark Web
inspector freshness threshold is especially tight (≤ 7 days; new
exposures appear daily).

### Step 3 — Run the per-inspector recipes (chain)

For each in-scope domain / host / IP / dark-web system, run the
corresponding single-system recipe with the rollup's customization
inherited (especially `audience.tone` and `narrative.preserve_current_vendor_dignity`).

| Per-system recipe | Inputs |
|---|---|
| `internet-domain-dns.md` | one per domain |
| `tls-ssl.md` | one per TLS-monitored host |
| `network-ip-address.md` | one per monitored IP |
| `dark-web-monitoring.md` | one per dark-web-monitored domain |

Extract **the findings + recommendations** from each chained run, not
the full output. Aggregate into the four per-family sections.

### Step 4 — Combined risk-story synthesis

This is the recipe's most-differentiated output. For each domain,
combine findings across the four inspectors:

| Combined finding | Source signals |
|---|---|
| **Spoofable + breached** | Domain has no DMARC enforcement (Internet Domain inspector) AND has accounts in dark-web corpus AND has accounts without MFA → attackers have address validity + credentials. |
| **Eavesdroppable + reputable-target** | Public services support TLS 1.0/1.1 (TLS inspector) AND the host's IP is high-reputation (low chance of being firewalled by ISPs) → MITM-friendly target. |
| **Mail-blocked + spoofable** | Mail IP on Spamhaus (Network IP) AND domain has no DMARC (Internet Domain) → mail is bouncing AND spoofers can ride the legitimate-domain name. |
| **Exposed services + credential exposure** | Risky open ports (Network IP) AND credential exposure (Dark Web) → external attackers have the attack vector + working keys. |
| **Cert-imminent + DMARC-loose** | Cert expiring soon (TLS) AND DMARC at p=none (Internet Domain) → upcoming outage + ongoing spoofability. |

For each combined finding, surface a 1–3 sentence narrative bullet
explaining the *cumulative* risk — what makes the combination worse
than the individual findings.

> **The combined section drives the deck.** Per-inspector findings are
> the supporting detail; the combined story is what the executive
> remembers.

### Step 5 — Headline KPIs

| KPI | Source | Compliance framing |
|---|---|---|
| Domains audited | Step 1 count | (scope) |
| Domains with DMARC at enforcement | Internet Domain inspector | Mail-trust posture |
| TLS hosts on modern protocols only (TLS 1.2 / 1.3) | TLS inspector | Encryption-in-transit |
| Certs expiring within 60 days | TLS inspector | Renewal calendar |
| Public IPs on any major blocklist | Network IP inspector | Mail-deliverability |
| Critical exposures (CVE / risky port / etc.) on public IPs | Network IP inspector | Boundary protection |
| Total credentials in breach corpus | Dark Web inspector | Identity exposure |
| Privileged accounts in breach corpus | Dark Web inspector (joined with identity inventory) | Critical-account exposure |
| Recent exposures (last 90 days) | Dark Web inspector | Trend visibility |

### Step 6 — Quick wins enumeration

The rollup naturally surfaces high-leverage / low-effort wins across
all four families:

- Enable registrar lock on the customer's domains (Internet Domain)
- Enable HSTS on customer-facing web hosts (TLS)
- Submit blocklist-delisting requests on cleared IPs (Network IP)
- Force password resets on identified exposed accounts (Dark Web)
- Publish a baseline DMARC record at `p=none rua=...` to gain
  visibility (Internet Domain)
- Disable TLS 1.0/1.1 on web hosts (TLS)
- Configure PTR records on outbound-mail IPs (Network IP)
- Enroll exposed accounts in MFA (Dark Web ↔ identity inventory)

### Step 7 — QA pass (per `reference/qa-retry-pattern.md`)

This recipe's QA pass especially focuses on:

1. **Inherit per-inspector QA pass results** from Step 3.
2. **Surface inspector-gap findings prominently** — missing inspectors
   in credentialed mode = missing evidence categories.
3. **Confirm domain-to-IP-to-cert linkage** — when a domain's MX
   points at an IP also monitored by the Network IP inspector, and
   that IP exposes a TLS endpoint monitored by the TLS inspector,
   confirm the three findings tell a coherent story.
4. **Privacy validation** — confirm `narrative.redact_individual_users`
   has been applied before any deck output.
5. **Proposed-metric gaps** surface in the verification log.

### Step 8 — Render

Recommended slide / page order for pptx:

| # | Slide | Content |
|---|---|---|
| 1 | Cover | Prospect / customer name, "External Attack Surface Assessment", date |
| 2 | What We Examined | Inspector + system inventory (scope) |
| 3 | Executive Summary | 5–7 outcome bullets, leading with combined-risk story |
| 4 | Combined Risk Story | The Step 4 synthesis — 3–5 cumulative findings |
| 5 | Headline KPIs | Step 5 KPI tiles |
| 6 | Domain & Mail Trust | Top 3 Internet Domain findings |
| 7 | Encryption in Transit | Top 3 TLS findings |
| 8 | Public IP Reputation & Exposure | Top 3 Network IP findings |
| 9 | Credential Exposure (Dark Web) | Aggregate counts — never per-user |
| 10 | First 30 Days — Quick Wins | The Step 6 quick-wins list |
| 11 | Recommended Engagement | Service offerings mapped to findings |
| 12 | Next Steps | CTAs |
| Appendix | Per-inspector details, methodology, verification log | |

For Word / Excel formats, follow the same structure adapted for the
medium.

### Tone-driven adaptations

When `audience.tone == "executive"` (default):
- Drop JMESPath / metric details from body — appendix only
- Replace counts with risk language for small numbers
- Combined risk-story leads; per-inspector detail is supporting
- Never name individual exposed users (per
  `narrative.redact_individual_users`)

When `audience.tone == "balanced"` (IT-director leave-behind):
- Keep counts + per-inspector detail in the body
- Cite specific domains / hostnames / IPs (those are not sensitive)
- Still redact individual users from dark-web findings

When `audience.tone == "technical"` (SOC working session):
- All counts, all per-inspector detail, all JMESPath references
- IT-director-eyes-only sheet may include per-user dark-web detail
  (but plaintext passwords are always redacted)

---

## QA & Manual Verification

Per `reference/qa-retry-pattern.md`. Manual checks for this rollup
include all four per-inspector manual checks plus:

- **Combined-story sanity check** — confirm the "attackers have both
  halves" narratives describe real, accurate, current state before
  surfacing them. False positives undermine credibility.
- **Inspector-deployment scope** — confirm the prospect / customer
  has not asked the MSP to limit external scanning (some prospects
  prohibit any external probing in early discovery; the recipe
  should respect that scope).
- **Combined-finding double-counting** — a single underlying weakness
  shouldn't be counted multiple times in the headline KPIs.

---

## Insights & recommendations — generation patterns

The rollup surfaces patterns its individual inspectors can't surface
alone. Recommendations follow the per-inspector templates (see each
single-system recipe) plus combined-risk recommendations:

| Combined pattern | Recommendation template |
|---|---|
| Spoofable + breached | "URGENT: Domain <D> lacks DMARC enforcement AND <N> users are in breach corpora. Combined: trivial business-email-compromise vector. Recommend immediate DMARC enforcement + password reset + MFA on the affected accounts." |
| Eavesdroppable + reputable-target | "Host <H> supports deprecated TLS protocols on a high-reputation IP — high-value MITM target. Recommend disabling TLS 1.0/1.1 + enforcing HSTS." |
| Mail-blocked + spoofable | "Mail IP <I> is on <blocklist> AND domain <D> lacks DMARC enforcement. Customers receive less mail from you AND impersonators can ride your domain. Recommend dual-track remediation: delisting + DMARC enforcement." |
| Exposed services + credential exposure | "Public IP <I> exposes <service-port> AND <N> credentials are in breach corpora. Combined: external attackers have the attack vector and the keys. Recommend immediate service closure + password reset on exposed accounts." |
| Cert-imminent + DMARC-loose | "Customer-facing <host> cert expires in <N> days AND domain <D> lacks DMARC enforcement. Recommend cert renewal + DMARC enforcement in the same maintenance window." |

---

## Data gaps & coverage notes

Inherits per-inspector data gaps (see each single-system recipe). Rollup-
specific:

| Field | Status | Source if missing |
|---|---|---|
| Brand-protection look-alike domains | external | Brand-monitoring service |
| Internal IP exposure (RFC 1918) | not in scope | Internal scanning tool |
| Email-deliverability telemetry | external | Mail-flow vendor data (Microsoft / Google / Mimecast / etc.) |
| Active exploitation attempts | external | SIEM / EDR data |
| Customer-vendor contract obligations | external | MSA / SOW review |

---

## Output format

`pptx` is the canonical discovery deliverable; `word` is the
leave-behind letter; `xlsx` is the multi-finding data appendix;
`markdown` is the working draft. See `templates/output-block-pptx.md`,
`templates/output-block-word.md`, `templates/output-block-xlsx.md`.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | query=<customer> | array<environment> | ok |
| 1 | liongard_system LIST | envId=<ENV_ID> query=<per inspector> | array<system> | ok per inspector |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3 | (chain per-inspector singles) | per single-system recipe | per-recipe findings | ok per system |
| 4 | (combined risk-story synthesis — derived) | per narrative.lead_with_combined_story | array<combined-finding> | ok |
| 5 | (headline KPIs — derived) | per Step 4 + Step 3 aggregates | KPI tiles | ok |
| 6 | (quick wins — derived) | per narrative.quick_wins_required | array<quick-win> | ok |
| 7 | QA pass | per `reference/qa-retry-pattern.md` + per-inspector QA | varies | ok |
| 8 | render | per `output.format` | <artifact path> | ok |
```

---

## Relationship to other recipes

- **`pre-sales-discovery.md`** — the parent cross-cutting recipe;
  this rollup is its zero-credential foundation. When `pre-sales-
  discovery.md` runs in trial-install mode, this rollup is the
  highest-leverage chained section.
- **`environment-quarterly-lookback/quarterly-business-review.md`** —
  this rollup provides the external-posture section of the PBR.
- **`onboarding-assessment/new-customer-onboarding.md`** — chained
  from the onboarding intake as one of the very first sections (since
  it surfaces zero-credential gaps the TAM can remediate before
  credentialed work begins).
- **`compliance/cyber-insurance/cyber-insurance-readiness.md`** —
  provides direct evidence for the encryption-in-transit + identity-
  exposure + perimeter-protection question families.
- **`compliance/cmmc/cmmc-readiness.md`** — provides evidence for
  the SC (System & Communications Protection) and IA (Identification
  & Authentication) practice families.
- **`recipes/system-type-assessment/all-domains.md`** — lighter-
  weight rollup focused on just the reconciled domain view. Use
  `all-domains.md` when the user wants domain inventory only; use
  this recipe when the user wants the full external posture.

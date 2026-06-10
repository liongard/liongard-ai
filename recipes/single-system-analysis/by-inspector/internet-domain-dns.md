---
name: single-system-internet-domain-dns
description: >
  Use this skill when the user wants a single-domain deep-dive analysis
  of registration, WHOIS, DNS configuration, mail-trust posture (SPF /
  DKIM / DMARC), nameserver health, or domain-expiration risk. Trigger
  phrases: "domain review for <domain>", "DNS health check for <domain>",
  "WHOIS lookup for <domain>", "DMARC posture for <domain>", "is <domain>
  expiring soon", "registrar status for <domain>", "domain hijack risk
  for <domain>". Non-credentialed — pulls entirely from public DNS +
  WHOIS data, making it suitable for prospects, third-party assessments,
  and pre-sales discovery before any customer credential has been
  shared.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_domain"
personas: [sales, vcio-account-manager, soc, technical-alignment-manager]
output_formats: [markdown, word, pptx, xlsx]
primitives:
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
---

# Single-System Analysis — Internet Domain / DNS

> **Inspector:** `internet-domain-dns-inspector` (ID 2). Cloud category.
> External-attack-surface family. **One system per domain.** Pulls
> entirely from public WHOIS, DNS, and reverse-DNS data — **no
> customer credential required**.
>
> **References:** `reference/inspector-aliases.md` (Domain, DNS, WHOIS,
> MX). `reference/asset-fields.md` for the `liongard_domain` reconciled
> view (use that tool for cross-environment rollups; this recipe is
> the single-domain deep-dive).

---

## Pre-Sales Discovery Value

This inspector is **uniquely valuable for pre-sales** because it runs
without any credential from the prospect. Common sales motions:

- **External email-trust audit** — pull a prospect's domain into a
  Liongard trial environment, run this recipe, and surface DMARC /
  SPF / DKIM weaknesses as discovery findings. Most prospects don't
  know their mail-trust posture; the IT director recognizes the gap
  immediately.
- **Domain-expiration / hijack-risk surfacing** — registrar lock
  missing, auto-renew off, expiring < 90 days, contact info exposed.
  These are catastrophic-risk findings that resonate with executives.
- **Brand-protection narrative** — typo-squat domains, recently
  registered look-alikes (when the recipe surfaces them via NS
  patterns). Frames the MSP as proactive about brand integrity.

The recipe accepts either an `environmentId` (when the prospect has a
trial environment) **or** a list of domain names via the
`customization.discovery_input.domains[]` block (when even a trial isn't
in place). The latter mode runs `liongard_domain` against the MSP's
own discovery environment with the prospect's domain temporarily added.

> **Why this matters:** Most non-credentialed discovery tools (security
> scanners, OSINT platforms) generate noisy output that's hard to
> translate into a sales narrative. This recipe produces clean
> per-domain findings in MSP-customer vernacular.

> **Deep-dive variant:** For BEC / phishing / ransomware risk analysis
> that combines this inspector with TLS/SSL, Dark Web, and Network IP
> into a single BEC-risk-scored narrative, use
> `recipes/domain-assessment/external-attack-surface-deep-dive.md`.
> That recipe is the roll-up; this one is the single-inspector deep-dive.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer-or-prospect>-<domain>-domain-review-<date>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  registration: "Registration & Ownership"
  expiration: "Expiration & Renewal"
  nameservers: "Nameserver Configuration"
  mail_trust: "Mail Trust (SPF / DKIM / DMARC)"
  dns_records: "DNS Records"
  hosting_footprint: "Hosting Infrastructure"
  reverse_dns: "Reverse DNS / PTR"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"                       # technical | balanced | executive
                                         # Default balanced. Use executive for the
                                         # sales-handoff slide; technical for the
                                         # engineering remediation doc.

slas:
  # Registration / expiration — inherits from config/msp-config.yaml:
  #   slas.domain_expiration_warn_days    (default 60)
  #   slas.registrar_lock_required        (default true)
  expiration_critical_days: 14
  expiration_warn_days: 60               # override: inherits from msp-config slas.domain_expiration_warn_days
  registrar_lock_required: true
  auto_renew_required: true
  whois_privacy_required: true           # MSP standard: WHOIS contact info should be
                                         # behind privacy unless customer is legally
                                         # required to publish (e.g., gTLD vs ccTLD)
  # Email authentication — inherits from config/msp-config.yaml:
  #   slas.spf_required                  (default true)
  #   slas.spf_all_qualifier_required    (default "-all")
  #   slas.dkim_required                 (default true)
  #   slas.dkim_min_key_bits             (default 1024)
  #   slas.dmarc_policy_minimum          (default "quarantine")
  #   slas.dmarc_policy_target           (default "reject")
  #   slas.dmarc_rua_required            (default true)
  # Override per-recipe only if this customer has a different standard.
  dnssec_required: false                 # set true if MSP standard
  ns_provider_consolidation_required: false   # MSP standard: all NS at one provider

reporting_period:
  default: "current_state"               # always point-in-time for this inspector

discovery_input:
  # Non-credentialed pre-sales mode. When environmentId is not provided,
  # supply a list of domains here. Recipe runs against the MSP's own
  # discovery environment.
  mode: "credentialed"                   # credentialed | discovery
  domains: []                            # ["prospect.com", "prospect.co.uk"]

qa:
  retry_on_null: true
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: false
  manual_verification_section_required: true
```

---

## When to use

- "Domain review for <domain>"
- "DNS health check for <domain>"
- "WHOIS lookup for <domain>"
- "DMARC posture for <domain>"
- "Is <domain> expiring soon?"
- "Registrar status for <domain>"
- "Domain hijack risk for <domain>"
- "Pre-sales domain analysis for <prospect>"
- "Are we protecting <customer>'s domains correctly?" (single-domain
  deep-dive; for the whole environment use
  `recipes/system-type-assessment/all-domains.md`)

Cadence: annual per domain (most domains are stable); quarterly for
heavily-utilized customer domains; ad-hoc when a registrar change /
NS migration is being planned; on-demand during pre-sales.

Personas:
- **Sales** (primary in discovery mode — public-data findings power
  the proposal)
- **vCIO / Account Manager** (renewal calendar conversations,
  registrar consolidation, DMARC enforcement upsell)
- **SOC** (mail-spoofing / phishing investigation; brand-protection
  monitoring)
- **TAM** (DMARC / SPF / DKIM remediation work; ensuring customer is
  on MSP-standard registrar)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes (credentialed mode) | `liongard_environment LIST` |
| System ID (the specific domain system) | Yes — one per recipe run | `liongard_system LIST query="internet-domain"` |
| Domain name(s) | Yes (discovery mode) | User-provided; see `discovery_input.domains` |
| Optional: focus area | No | User prompt — e.g., "focus on mail trust only" |

> **System-per-domain.** The `internet-domain-dns-inspector` creates
> one Liongard system per domain. A customer with 5 domains has 5
> systems under this inspector. Run this recipe per-domain; use
> `recipes/system-type-assessment/all-domains.md` for the rollup.

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer-or-prospect>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="internet-domain"
# Pick the specific domain's system by name.
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

Confirm the domain's last inspection date. Domain data changes
infrequently (registrar / NS changes are rare events), but a stale
inspection means SPF / DKIM / DMARC drift could be unreported.

### Step 3 — Pull the reconciled domain view

```
liongard_domain LIST environmentId=<ENV_ID> domainName="<the-domain>"
                     fields=["domainName","registrar","daysTillExpiration","registrarLock","autoRenew","whoisPrivacy","dmarcHealth","spfHealth","dkimHealth","dnssec","nameservers","mxRecords","ipv4","ipv6","asn"]
```

The reconciled `liongard_domain` tool exposes the most-useful fields
without per-inspector navigation. Use this as the primary data source.

### Step 4 — Pull the raw inspector dataprint (validated JMESPath paths)

Use `liongard_metric GENERATE_AND_EVALUATE` with the JMESPath expressions below.
These paths are validated against the live Internet Domain/DNS inspector dataprint.

```
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  description="<plain English description of what you want>"

# Registration & expiration (all paths validated against live dataprint)
#   SystemInfo.DomainName                          (the monitored domain)
#   SystemInfo.Registrar                           (registrar name)
#   SystemInfo.DomainCreationDate                  (registration date)
#   SystemInfo.DomainExpirationDate                (expiration date)
#   SystemInfo.DomainStatus                        (WHOIS status flags, e.g.
#                                                   "clientTransferProhibited" = registrar lock on)
#   SystemInfo.WhoIsServer
#   SystemInfo.RegistrantContactEmail              (privacy check — should be masked)
#   SystemInfo.AdminContactEmail
#   SystemInfo.TechContactEmail
#   DaysTillExpiration                             (integer — primary expiry field)
#
#   NOTE: registrarLock and autoRenew are NOT separate fields.
#   Check SystemInfo.DomainStatus for lock status ("clientTransferProhibited").
#   autoRenew status is not available in the Internet Domain inspector dataprint.

# Website posture (validated)
#   Website.HTTP.statusCode                        (should be a redirect to HTTPS)
#   Website.HTTPS.statusCode
#   Website.HTTPS.SSLCertificate                   (cert summary from domain inspector perspective)

# Email authentication — granular health checks (all validated)
#   EmailSecurityOverview                          (quick pass/fail summary per protocol)
#                                                   sub-fields: SpfRecord, SpfRecordResult,
#                                                   DkimRecord, DkimRecordResult,
#                                                   DmarcRecord, DmarcRecordResult
#   SPFRecord                                      (raw SPF TXT record string)
#   SPFRecordBreakdown                             (human-readable parsed mechanism string)
#   SPFExists                                      (boolean)
#   SPFAllExists                                   (qualifier: "strong" = -all, "weak" = ~all, etc.)
#   DMARCRecord                                    (raw DMARC TXT record string)
#   DMARCPolicy                                    (string — value includes "p=" prefix,
#                                                   e.g. "p=reject" NOT just "reject")
#   DMARCExists                                    (boolean)
#   DMARCAggReports                                (boolean — rua= present)
#   DMARCForensicReports                           (boolean — ruf= present)
#   DKIMFound                                      (boolean — at least one selector found)
#   EmailSecurity.spfChecks[*]                     (10 checks; each has name + results array)
#   EmailSecurity.dkimChecks[*]                    (3 checks per selector)
#   EmailSecurity.dmarcChecks[*]                   (5 checks)
#   EmailSecurity.dkimRecords[*].{Selector, KeyType, PublicKeySize, Domain}
#                                                  (each DKIM selector = one authorized sending platform)
#   SpoofIntel                                     (object: spfExists, dmarcExists, spfAll,
#                                                   strongInclude, dmarcAgg, dmarcFor, dmarcPolicy)

# DNS records — validated field names (PascalCase, "DNS" prefix on record arrays)
#   DNSMXRecords[*].{Exchange, Preference, ASStr, ASInfoStr, AddressStr}
#                                                  (MX targets with ASN provider info)
#   DNSTXTRecords[*].data                          (raw TXT string per record — SaaS tokens here)
#   DNSTXTRecords[*]                               (full object includes parsed SPF fields)
#   DNSNSRecords[*].{data, ASStr, ASInfoStr}        (nameserver hostnames with ASN)
#   DNSARecords[*].{data, AddressStr, ASStr, ASInfoStr}
#                                                  (A records with ASN/cloud provider)
#   DNSCNAMERecords[*]                             (CNAME records — field shape varies)
#   DNSSEC                                         (array of DNSKEY objects; empty = not configured)

# Subdomains (validated — path accepted; may be empty if no subdomain data)
#   Subdomains[*].{target, hostname, subdomainHasSSL, ipaddress}
#                                                  (hostname reveals CDN/WAF via CNAME target)
```

> **Metric availability.** Enumerate what's available with
> `liongard_metric LIST environmentId=<ENV_ID> systemId=<SYS_ID>`.
> File a metric request via the `liongard-metrics` skill for any
> gap that blocks a baseline check.
> The JMESPath paths above are validated from live dataprints but
> customer-specific inspectors may omit fields with no data.

### Step 5 — Mail-trust evaluation

For each of SPF / DKIM / DMARC, evaluate against `slas` (inherits from msp-config):

| Signal | What to check |
|---|---|
| SPF | Record present + valid syntax + `spf_all_qualifier_required` (default `-all`; not `+all`) |
| SPF complexity | `include:` chain count ≤ 10 DNS lookups (RFC 7208 limit) |
| DKIM | `DKIMFound = true` + at least one key ≥ `dkim_min_key_bits` (default 1024; 2048 preferred) |
| DMARC | Record present + `DMARCPolicy` ≥ `dmarc_policy_minimum` (default `quarantine`) |
| DMARC reporting | `rua` aggregate-report URI present if `dmarc_rua_required = true` |
| Alignment | DKIM + SPF both align with the From: domain (strict or relaxed) |

Use `EmailSecurity.spfChecks[*]`, `EmailSecurity.dkimChecks[*]`, and
`EmailSecurity.dmarcChecks[*]` for per-check detail. Each check object has a `name`
field and a `results` array where each result has `{domain, name, result, description}`.
`result` values are `"Pass"`, `"Fail"`, or `"Caution"`.
`EmailSecurityOverview` gives the rolled-up pass/fail per protocol (`SpfRecordResult`,
`DkimRecordResult`, `DmarcRecordResult`).

> **`DMARCPolicy` value format:** The field returns the full tag-value string including
> the `p=` prefix (e.g., `"p=reject"` not `"reject"`). Compare accordingly:
> `p=none` < `p=quarantine` < `p=reject`.

### Step 5a — SaaS footprint discovery (TXT record mining)

Pull `TXT[*]` and parse each record for domain-verification tokens. These tokens reveal
third-party SaaS platforms the customer has connected to the domain — critical for
understanding the actual attack surface.

| TXT token pattern | Platform |
|---|---|
| `v=spf1 include:spf.protection.outlook.com` | Microsoft 365 / Exchange Online |
| `v=spf1 include:_spf.google.com` | Google Workspace |
| `MS=ms<digits>` | Microsoft domain verification |
| `google-site-verification=` | Google Search Console / Workspace |
| `atlassian-domain-verification=` | Atlassian (Jira/Confluence) |
| `docusign=` | DocuSign |
| `pardot<digits>.domainkey.salesforce.com` (CNAME) | Salesforce / Pardot email |
| `rippling-verify=` | Rippling (HR/payroll) |
| `stripe-verification=` | Stripe (payments) |
| `apple-domain-verification=` | Apple Business Manager |
| `facebook-domain-verification=` | Meta / Facebook Business |
| `zoom-domain-verification=` | Zoom |
| `_github-challenge-<org>` | GitHub organization ownership |
| `have-i-been-pwned-verification=` | HIBP monitoring |
| `adobe-sign-verification=` | Adobe Sign |
| `twilio-domain-verification=` | Twilio (communications) |
| `mandrill_verify=` | Mandrill (Mailchimp transactional) |
| `sendgrid.net` include in SPF | SendGrid |
| `amazonses.com` include in SPF | Amazon SES |

For each discovered SaaS platform, flag whether it is covered by the SPF `include:` chain.
An authorized email sender that is **not** covered by SPF creates a spoofing vector even
if DMARC is enforced — the "DKIM-only sender gap."

### Step 5b — DKIM selector audit (sender coverage cross-reference)

DKIM selectors name the sending platform that published that key. Map observed selectors
to their origin platform:

| Selector name pattern | Platform |
|---|---|
| `selector1`, `selector2` | Microsoft 365 (DKIM rotation pair) |
| `google` | Google Workspace |
| `k1` | Mailchimp / Mandrill |
| `s1`, `s2` | Generic; check CNAME target for confirmation |
| `sm_<hash>` | Salesforce Marketing Cloud |
| `api` | SendGrid |
| `pm` | Postmark |
| `mtarouter` | Mimecast relay |
| `dkim` (generic) | On-prem / custom MTA |

Cross-reference: every SaaS platform found in Step 5a that sends email **must** appear
in the DKIM selector list. A platform with domain-verification TXT but no corresponding
DKIM selector is either (a) not sending email from this domain (low risk) or (b) signing
with a selector not yet observed (gap — flag for manual verification).

### Step 5c — MX record filter stack identification

Pull `DNSMXRecords[*].Exchange` hostnames and map to the inbound email security stack:

| MX hostname pattern | Platform / Filter |
|---|---|
| `*.protection.outlook.com` | Microsoft 365 (EOP / Defender for Office) |
| `aspmx.l.google.com` / `alt*.aspmx.*` | Google Workspace |
| `*.mimecast.com` | Mimecast |
| `*.pphosted.com` | Proofpoint |
| `*.barracudanetworks.com` | Barracuda |
| `*.ppe-hosted.com` | Proofpoint Essentials |
| `*.spamh.com` | SpamHero |
| `*.hornetsecurity.com` | Hornetsecurity |
| `*.exclaimer.net` | Exclaimer (signature; not a filter) |
| `mail.<domain>` or internal hostname | On-prem mail server |

Flag if the MX provider does not match the preferred email platform from
`msp-config.yaml preferred_stack.identity_primary`. A mismatch often means the customer
has a third-party filter in front of M365 / Google that may not be managed by the MSP.

### Step 5d — Subdomain attack surface and WAF/CDN fingerprinting

Pull `Subdomains[*].{target, hostname, subdomainHasSSL, ipaddress}` and fingerprint each:

```
# For each subdomain CNAME target, determine the CDN/WAF/hosting provider:
Subdomains[*].hostname
```

| CNAME target pattern | Provider |
|---|---|
| `*.cloudfront.net` | AWS CloudFront CDN |
| `*.cdn.cloudflare.net` / `*.cloudflare.com` | Cloudflare (CDN + WAF) |
| `*.akamaiedge.net` / `*.akamai.net` | Akamai |
| `*.fastly.net` | Fastly CDN |
| `*.azurewebsites.net` / `*.azurefd.net` | Azure (App Service / Front Door) |
| `*.awsglobalaccelerator.com` / `*.elb.amazonaws.com` | AWS ELB / Global Accelerator |
| `*.netlify.app` | Netlify |
| `*.vercel.app` | Vercel |
| `*.github.io` | GitHub Pages |
| `*.squarespace.com` | Squarespace |
| `*.wixsite.com` / `*.wix.com` | Wix |
| `*.zendesk.com` | Zendesk (support portal) |
| `*.hubspot.com` / `*.hs-sites.com` | HubSpot (landing pages / CRM portal) |
| `*.salesforce.com` / `*.force.com` | Salesforce |
| `*.my.id.me` | ID.me |

For each subdomain flagged `subdomainHasSSL = false`, surface as a finding.
Subdomains pointing to third-party SaaS with no SSL are uncommon post-2024 but worth
confirming.

**Subdomain takeover risk:** Any subdomain CNAME pointing to a platform where the
underlying resource no longer exists (dangling CNAME) is a takeover vector. This requires
manual verification — Liongard confirms the CNAME target hostname but does not probe
whether the target resource is claimed.

### Step 6 — Expiration + ownership risk

| Signal | Risk |
|---|---|
| `daysTillExpiration` < 14 | Critical — domain could fall to opportunistic registrar |
| `daysTillExpiration` < 60 | High — proactive renewal needed |
| `registrarLock = false` | High — hijack risk |
| `autoRenew = false` | Medium — manual renewal dependency |
| `whoisPrivacy = false` | Low — contact info exposed (some TLDs require this; flag for review) |
| Registrar not on MSP standard | Low — consolidation opportunity |

### Step 7 — Nameserver + hosting posture

| Signal | Surface |
|---|---|
| NS provider | Note if not MSP-standard or split across providers |
| MX records | Confirm match the customer's email platform (M365 / Google Workspace / on-prem) |
| IP / ASN | Map to a hosting provider; flag if hosted at customer site (legacy on-prem mail / web) |
| Reverse DNS / PTR | Confirm PTR exists for mail-handling IPs (RBL / deliverability) |

### Step 8 — QA pass (per `reference/qa-retry-pattern.md`)

This recipe's QA pass especially focuses on:

1. **Retry persistent nulls** on DMARC / SPF / DKIM fields — DNS
   propagation can cause transient missing data on freshly-changed
   records.
2. **Flag stale inspectors** from Step 2.
3. **Cross-reference with M365 / Google Workspace** — if the customer
   has a tenant inspector, confirm the mail-trust posture observed
   here aligns with the tenant's accepted-domains config.
4. **SaaS coverage gaps** — every platform found in TXT tokens that
   sends email (Step 5a) must appear in both SPF and DKIM (Step 5b).
   Flag any where the coverage is incomplete.
5. **Dangling CNAME / subdomain takeover** — manually verify any
   subdomain CNAME pointing to a third-party platform (Step 5d) to
   confirm the underlying resource is still claimed.
6. **Proposed-metric gaps** surface in the verification log + file a
   metric request via `liongard-metrics`.
7. **Whois privacy provider identification** — some privacy providers
   are themselves notorious; surface the provider name when available.

### Step 9 — Render output

| Output mode | Best for |
|---|---|
| `markdown` | Working draft / IT-director audience |
| `word` | Customer-facing findings letter (single-domain) |
| `pptx` | Slide-per-domain for the pre-sales / QBR deck |
| `xlsx` | Cross-domain rollup (use the system-type recipe instead) |

---

## QA & Manual Verification

Per `reference/qa-retry-pattern.md`. Every run produces a **Manual
Verification Needed** appendix.

Manual checks specific to this recipe:

- **Authoritative DNS confirmation** — Liongard observes DNS from a
  public resolver; if the customer uses split-horizon DNS, confirm the
  external view aligns with what's intended.
- **DKIM key rotation history** — Liongard exposes the current
  selector(s); the rotation cadence is policy-driven and external.
- **Brand-protection look-alike domains** — typo-squat or recently-
  registered look-alikes are external to this inspector; pair with a
  domain-monitoring service for full coverage.
- **Sender reputation / RBL listings on mail IPs** — partial via the
  Network IP inspector; complement with mail-flow vendor data.

---

## Insights & recommendations — generation patterns

| Pattern | Recommendation template |
|---|---|
| Domain expiring < critical SLA | "Initiate renewal immediately for <domain> — expires in <N> days." |
| Domain expiring < warn SLA | "Schedule renewal for <domain> in next maintenance window." |
| Registrar lock missing | "Enable registrar lock on <domain>. No business impact; security hardening only." |
| Auto-renew off | "Enable auto-renewal on <domain> to eliminate manual renewal risk." |
| WHOIS privacy off | "Enable WHOIS privacy on <domain> to reduce social-engineering exposure (TLD permitting)." |
| SPF record missing | "Publish SPF record for <domain>: `v=spf1 include:<mail-provider> -all` (or `~all`)." |
| SPF too permissive | "Tighten SPF policy from `+all` / no qualifier to `-all` after confirming legitimate senders." |
| SPF DNS-lookup limit exceeded | "<domain>'s SPF chain exceeds 10 DNS lookups (RFC 7208 limit). Refactor via SPF flattening or DMARC-only enforcement." |
| DKIM missing | "Publish DKIM keys for <domain>'s sending services (M365 / Google / third-party senders)." |
| DKIM key too short | "Rotate DKIM keys on <domain> to ≥ 2048 bits." |
| DMARC missing | "Publish DMARC record for <domain>. Start at `p=none rua=...` to gather telemetry, then move to enforcement." |
| DMARC at `p=none` (monitoring) | "Move <domain> from monitoring to enforcement (`p=quarantine` or `p=reject`) after report review." |
| DMARC missing `rua` | "Add aggregate-report URI to <domain>'s DMARC record so visibility into authentication failures is gained." |
| NS provider sprawl | "Consolidate <domain>'s NS records at a single provider to reduce operational risk." |
| Reverse DNS missing on mail IPs | "Configure PTR record for <domain>'s outbound mail IPs to improve deliverability and RBL standing." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Authoritative DNS view | partial — Liongard sees public resolution | Authoritative DNS vendor portal |
| DKIM key strength + rotation history | partial — current selector observed | Sending-service vendor portal |
| RBL / blocklist status of mail IPs | partial — pair with Network IP inspector | Reputation services (Spamhaus, etc.) |
| Brand look-alike domains | external | Brand-monitoring service |
| Domain abuse history | external | Domain-abuse intel services |
| DNSSEC validation chain | partial — status observed; chain detail external | Authoritative DNS vendor |

---

## Output format

Default `markdown` for working drafts. Switch to `word` or `pptx` for
customer-facing deliverables. See `templates/output-block-word.md` and
`templates/output-block-pptx.md`.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | query=<customer> | array<environment> | ok |
| 1 | liongard_system LIST | envId=<ENV_ID> query="internet-domain" | array<system> | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3 | liongard_domain LIST | envId=<ENV_ID> domainName=<domain> [fields...] | array<domain-record> | ok |
| 4 | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath=<path> | varies | ok per path |
| 5 | (mail-trust evaluation — derived) | EmailSecurity[*], EmailSecurityOverview | findings | ok |
| 5a | (SaaS footprint — derived) | TXT[*] token parse | platform-coverage map | ok |
| 5b | (DKIM selector audit — derived) | EmailSecurity DKIM checks | selector-platform map | ok |
| 5c | (MX filter stack — derived) | DNSMXRecords[*].Exchange hostname map | filter-stack finding | ok |
| 5d | (subdomain WAF/CDN — derived) | Subdomains[*].hostname CNAME map | fingerprint table | ok |
| 6 | (expiration / ownership — derived) | per slas | findings | ok |
| 7 | (NS / hosting — derived) | per slas | findings | ok |
| 8 | QA pass | per `reference/qa-retry-pattern.md` | varies | ok |
| 9 | render | per `output.format` | <artifact path> | ok |
```

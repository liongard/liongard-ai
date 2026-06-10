---
name: domain-assessment-external-attack-surface-deep-dive
description: >
  Use this recipe when you need a forensic-depth external attack surface
  assessment for a single domain — covering BEC risk, phishing/spearphishing
  exposure, ransomware entry vectors, email authentication posture, SaaS
  footprint discovery, subdomain attack surface, WAF/CDN gaps, SSL
  vulnerabilities, credential exposure, and expiration risk. Trigger phrases:
  "deep-dive external assessment for <domain>", "BEC risk report for
  <customer>", "phishing risk assessment for <domain>", "full email security
  audit for <domain>", "SaaS footprint discovery for <prospect>",
  "pre-sales deep-dive for <prospect>", "what can an attacker see about
  <domain>". Non-credentialed — builds the complete attack-surface picture
  from public DNS, WHOIS, TLS handshake, and breach corpus data. Suitable for
  prospects, third-party assessments, and pre-sales discovery.
compatibility: >
  Requires Liongard MCP: liongard_environment, liongard_launchpoint,
  liongard_metric, liongard_domain. Optional enrichment: liongard_identity
  (for credential cross-reference). Inspector IDs: Internet Domain/DNS (2),
  TLS/SSL (16), Dark Web Monitoring (4), Network IP (18).
personas: [sales, soc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, pptx]
primitives:
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
related_recipes:
  - recipes/system-type-assessment/all-external-attack-surface.md   # fleet rollup — use this for breadth across many environments
  - recipes/single-system-analysis/by-inspector/internet-domain-dns.md
  - recipes/single-system-analysis/by-inspector/tls-ssl.md
  - recipes/single-system-analysis/by-inspector/dark-web-monitoring.md
  - recipes/single-system-analysis/by-inspector/network-ip-address.md
  - recipes/sales-assessment/pre-sales-discovery.md
---

# Domain Assessment — External Attack Surface Deep Dive

> **This is the forensic-depth single-domain recipe.** It goes far
> deeper than `all-external-attack-surface.md` (which is a breadth-first
> fleet rollup) by fully exploiting every signal the Internet Domain/DNS
> inspector surfaces: granular email-security checks, SaaS footprint
> discovery from TXT records, DKIM selector cross-referencing, subdomain
> enumeration with WAF/CDN fingerprinting, and MX-based email filter
> stack identification.
>
> **Inspectors consumed:**
>
> | Inspector | ID | What it answers |
> |---|---|---|
> | Internet Domain/DNS | 2 | Registration, WHOIS exposure, full DNS record set, email auth (SPF/DKIM/DMARC with 18 granular checks), subdomain enumeration, website status |
> | TLS/SSL | 16 | Certificate validity, protocol versions, cipher weakness, known vulns (HEARTBLEED/POODLE/etc.), HSTS, HTTP→HTTPS redirect |
> | Dark Web Monitoring | 4 | Credential exposure count, breach sources, plaintext password exposure, recency |
> | Network IP | 18 | Reverse DNS, ASN/hosting, reputation (blocklist status) for mail-sending IPs |
>
> **Zero credentials required.** Every signal comes from public internet
> data, making this the sharpest pre-sales discovery tool in the library.

---

## Why this recipe exists

The single-system recipes (`internet-domain-dns.md`, `tls-ssl.md`, etc.)
each tell one part of the story well. The fleet rollup
(`all-external-attack-surface.md`) tells the breadth story. Neither does
what this recipe does: take one domain and fully decompose its external
attack surface into the signals that matter specifically for **BEC,
phishing/spearphishing, and ransomware initial-access risk** — the three
threat scenarios MSPs are asked about most.

A well-run MSP can produce this for a prospect in under 30 minutes without
asking for a single password. When presented as a findings brief, it
typically surfaces 4–8 findings the prospect's incumbent has never shown
them.

---

## Customize for your MSP

```yaml
output:
  format: markdown                        # markdown | word | pptx
  filename: "<customer-or-prospect>-<domain>-eas-deep-dive-<date>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  threat_model: "Threat Model — What Attackers See"
  bec_risk: "BEC Risk Assessment"
  phishing_risk: "Phishing & Spearphishing Risk"
  email_auth: "Email Authentication Posture (SPF / DKIM / DMARC)"
  saas_footprint: "SaaS Footprint Discovery"
  email_filter_stack: "Email Filter & Security Stack"
  subdomain_surface: "Subdomain Attack Surface"
  waf_cdn_posture: "WAF / CDN Edge Posture"
  ssl_tls_posture: "SSL / TLS Certificate & Protocol Posture"
  credential_exposure: "Credential Exposure (Dark Web)"
  expiration_calendar: "Expiration Calendar"
  combined_risk_story: "Combined Risk — How the Findings Chain Together"
  recommendations: "Recommended Actions"
  quick_wins: "First 30 Days — Quick Wins"
  data_gaps: "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"                        # technical | balanced | executive
  # Use executive for the pre-sales deck cover + summary.
  # Use balanced for the IT-director leave-behind.
  # Use technical for the SOC working document.

slas:
  # Domain
  domain_expiration_critical_days: 14
  domain_expiration_warn_days: 60
  registrar_lock_required: true
  auto_renew_required: true
  whois_privacy_required: true
  dnssec_required: false

  # Email auth
  dmarc_policy_minimum: "quarantine"      # none | quarantine | reject
  dmarc_policy_target:  "reject"          # what MSP standard is — used in upgrade recommendation
  dmarc_rua_required: true                # aggregate reporting required
  dmarc_ruf_recommended: true             # forensic reporting recommended
  spf_required: true
  spf_all_qualifier_required: "~all"      # ~all minimum; -all preferred
  dkim_required: true
  dkim_min_key_bits: 2048
  dkim_selectors_all_in_spf: true         # every DKIM-authorized sender should also be in SPF

  # TLS
  tls_expiration_critical_days: 14
  tls_expiration_warn_days: 45
  min_tls_version: "TLSv1.2"
  prohibited_protocols: ["SSLv2", "SSLv3", "TLSv1.0", "TLSv1.1"]
  hsts_required: true
  http_to_https_redirect_required: true

  # Dark web
  credential_exposure_pct_max: 5          # % of identities in breach corpus = Critical
  privileged_account_exposed_max: 0
  recent_exposure_days: 90

privacy:
  redact_individual_users_in: ["pptx", "executive-tone-output", "word"]
  redact_passwords_in_output: true

reporting_period:
  default: "current_state"

discovery_input:
  # Non-credentialed pre-sales mode.
  mode: "credentialed"                    # credentialed | discovery
  domains: []                             # ["prospect.com", "prospect.co.uk"]
  tls_hosts: []                           # ["www.prospect.com:443", "mail.prospect.com:993"]

qa:
  retry_on_null: true
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  surface_proposed_metrics: false
  manual_verification_section_required: true
```

---

## When to use

- "Deep-dive external assessment for <domain>"
- "BEC risk report for <customer>"
- "Full email security audit for <domain>"
- "What SaaS services is <prospect> using?" (no credentials needed)
- "Pre-sales deep-dive for <prospect>"
- "What can an attacker learn about <domain> from the internet?"
- "Phishing risk assessment for <customer>"
- Post-incident: "What was the external exposure at the time of the BEC?"

**Use the fleet rollup instead** (`all-external-attack-surface.md`) when
you need breadth across many domains/environments in one pass. Use this
recipe when you need depth on a single domain.

Cadence: per prospect (pre-sales); annually per customer domain; ad-hoc
post-incident or when a major email-platform migration occurs.

Personas:
- **Sales** (primary — produces the discovery brief that wins the room)
- **SOC** (BEC/phishing triage; incident response evidence)
- **vCIO / AM** (DMARC enforcement roadmap; SaaS rationalization conversation)
- **TAM** (email-auth remediation; DKIM rotation; SPF gap closure)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes (credentialed mode) | `liongard_environment LIST` |
| Internet Domain/DNS system ID | Yes | `liongard_launchpoint LIST systemType="Internet Domain"` |
| TLS/SSL system ID(s) | Recommended | `liongard_launchpoint LIST systemType="TLS"` |
| Dark Web system ID | Recommended | `liongard_launchpoint LIST systemType="Dark Web"` |
| Network IP system ID(s) | Optional | `liongard_launchpoint LIST systemType="Network IP"` |
| Domain name(s) | Yes (discovery mode) | User-provided |
| TLS host(s) | Yes (discovery mode) | User-provided |

---

## Workflow

### Step 1 — Resolve environment and system IDs

```
liongard_environment LIST searchMode=keyword query="<customer-or-prospect>"

# For each inspector family:
liongard_launchpoint LIST systemType="Internet Domain" environmentIds=[<ENV_ID>]
liongard_launchpoint LIST systemType="TLS"             environmentIds=[<ENV_ID>]
liongard_launchpoint LIST systemType="Dark Web"        environmentIds=[<ENV_ID>]
liongard_launchpoint LIST systemType="Network IP"      environmentIds=[<ENV_ID>]
```

Note which inspector families are deployed vs. absent. Missing inspectors
become coverage-gap findings in the output.

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

Flag any inspector with `latestInspectionDate` older than
`qa.flag_inspector_lastseen_threshold_days` (7 days). Dark Web is the
most time-sensitive — breach corpus updates daily.

### Step 3 — Internet Domain/DNS dataprint (the core data source)

Pull the full email-security and DNS data using the validated JMESPath
structure from the Internet Domain/DNS inspector dataprint:

```
liongard_metric GENERATE_AND_EVALUATE
  systemId=<DOMAIN_SYS_ID>
  environmentId=<ENV_ID>
  description="Full email security posture: SPF record and breakdown,
               all DKIM selectors and check results, DMARC record and
               policy, MX records with ASN/provider, all TXT records,
               subdomain list with SSL status and resolved hostnames,
               WHOIS expiration and registrar lock status,
               website HTTP and HTTPS status codes"
```

**Validated dataprint paths (use these directly in JMESPath):**

```jmespath
# Email authentication — primary signals
SPFRecord                                  # raw SPF record string
SPFRecordBreakdown                         # parsed SPF with mechanism descriptions
SPFExists                                  # boolean
SPFAllExists                               # ~all / -all / +all / none
SPFStrongInclude                           # boolean — no +all or overly permissive includes
DMARCRecord                                # raw DMARC TXT string
DMARCPolicy                                # p=none|quarantine|reject
DMARCExists                                # boolean
DMARCAggReports                            # boolean — rua= present
DMARCForensicReports                       # boolean — ruf= present
DMARCOrg                                   # organizational domain
DKIMFound                                  # boolean — at least one selector found

# Granular email security checks (18 checks total across SPF/DKIM/DMARC)
EmailSecurity.spfChecks[*]                 # 10 checks: presence, syntax, lookup count,
                                           # duplicate lookups, void lookup limit,
                                           # post-all mechanisms, ptr modifier,
                                           # A/AAAA record limit, null lookups, recursion
EmailSecurity.dkimChecks[*]                # 3 checks per selector: presence, syntax, public key
EmailSecurity.dmarcChecks[*]               # 5 checks: presence, quarantine/reject policy,
                                           # syntax, external domain permission, record count
EmailSecurity.dkimRecords[*].{
  Selector: Selector,
  KeyType: KeyType,
  PublicKeySize: PublicKeySize,
  Domain: Domain
}                                          # each DKIM selector = one authorized sending platform

# EmailSecurityOverview — quick pass/fail per protocol
EmailSecurityOverview.{
  SpfRecord: SpfRecord,
  SpfRecordResult: SpfRecordResult,
  DkimRecord: DkimRecord,
  DkimRecordResult: DkimRecordResult,
  DmarcRecord: DmarcRecord,
  DmarcRecordResult: DmarcRecordResult
}

# SaaS footprint discovery — TXT records
DNSTXTRecords[*].{data: data, Name: Name}  # parse for vendor domain-verification tokens

# Email filter stack identification — MX records with ASN
DNSMXRecords[*].{
  Exchange: Exchange,
  Priority: Priority,
  ASInfoStr: ASInfoStr,
  AddressStr: AddressStr
}

# Subdomain attack surface
Subdomains[*].{
  target: target,
  hostname: hostname,         # reveals CDN/WAF provider in CNAME
  ssl_status: subdomainHasSSL,
  ip: ipaddress,
  response: response          # HTTP status code
}

# DNS record set — ASN data reveals cloud provider per IP
DNSARecords[*].{Name: Name, AddressStr: AddressStr, ASStr: ASStr, ASInfoStr: ASInfoStr}
DNSMXRecords[*].{Exchange: Exchange, ASStr: ASStr, ASInfoStr: ASInfoStr}
DNSNSRecords[*].{Address: Address, ASStr: ASStr, ASInfoStr: ASInfoStr}
DNSTXTRecords[*].data

# WHOIS registration and expiration
SystemInfo.DomainExpirationDate            # expiration date
SystemInfo.DomainStatus                    # clientTransferProhibited etc.
SystemInfo.Registrar
SystemInfo.WhoIsServer
DaysTillExpiration                         # integer
SystemInfo.RegistrantContactEmail          # privacy check — should be masked
SystemInfo.TechContactEmail
SystemInfo.AdminContactEmail
SystemInfo.ContactEmail

# Website status
Website.HTTP.statusCode                    # is HTTP live? redirects to HTTPS?
Website.HTTPS.statusCode                   # is HTTPS live?
Website.HTTPS.SSLCertificate               # cert seen from domain inspector perspective

# DNSSEC
DNSSEC                                     # array — empty = DNSSEC not configured
```

> **Note on DNSSEC:** `DNSSEC` is an array; empty array means not
> configured. This is the correct check — do not rely on a boolean field.

### Step 4 — SaaS footprint mapping (from TXT records)

Parse every `DNSTXTRecords[].data` entry for domain-verification tokens.
These reveal every SaaS vendor that has been granted domain-level
authorization. Build a SaaS inventory table:

**Known TXT record prefixes and their services:**

| TXT record prefix | Service | Risk relevance |
|---|---|---|
| `MS=ms...` | Microsoft (M365 / Azure AD domain verification) | Multiple records = possible shadow tenants |
| `google-site-verification=` | Google Workspace / Google Search Console | GWS sending capability |
| `apple-domain-verification=` | Apple Business Manager | Device management |
| `atlassian-domain-verification=` | Jira / Confluence / Atlassian Cloud | Internal collaboration platform |
| `pardot...=` | Salesforce Pardot | Marketing emails — common phishing vector |
| `hubspot-developer-verification=` | HubSpot | Marketing emails — common phishing vector |
| `mailchimp-domain-verification=` | Mailchimp | Marketing emails |
| `sendgrid-domain-verification=` | SendGrid / Twilio | Transactional email sender |
| `rippling-domain-verification=` | Rippling HR/Payroll | HR/payroll emails — high-value phishing target |
| `gusto-domain-verification=` | Gusto Payroll | Payroll emails — high-value phishing target |
| `workday-domain-verification=` | Workday HCM | HR/payroll emails |
| `docusign-domain-verification=` | DocuSign | e-Signature emails — impersonation risk |
| `zendesk-...` | Zendesk | Customer support ticketing |
| `salesforce-...` | Salesforce CRM | CRM/opportunity emails |
| `mixpanel-domain-verify=` | Mixpanel | Product analytics |
| `stripe-verification=` | Stripe | Payment processing — high-value phishing target |
| `krisp-domain-verification=` | Krisp | Meeting audio (lower risk) |
| `smartsheet-site-validation=` | Smartsheet | Project/workflow collaboration |
| `zoom-...` | Zoom | Video conferencing |
| `adobe-idp-site-verification` | Adobe / Acrobat Sign | e-Signature / document emails |
| `_amazonses=` | Amazon SES | Transactional email sender |
| `v=spf1 ...` | SPF record (extract include: chain) | Authorized mail-sending services |

Flag:
1. **High-value phishing targets** — payroll/HR/payments services whose
   domain-verification means the domain sends these email types. An
   attacker spoofing or compromising one of these services has maximum
   impact.
2. **Multiple `MS=ms...` records** — more than one Microsoft domain
   verification record can indicate multiple M365 tenants (shadow IT) or
   an incomplete tenant migration.
3. **Marketing senders (Pardot/HubSpot/Mailchimp/SendGrid)** — these
   services send high-volume email from the domain and are common
   targets for BEC and credential-theft campaigns.
4. **Services verified but NOT in SPF** — cross-reference TXT
   verification tokens against `SPFRecordBreakdown` include: chain. Any
   service with a domain-verification token but no SPF authorization is a
   DKIM-only sender — DMARC can pass on DKIM alignment alone, but this
   is a fragile configuration.

### Step 5 — DKIM selector audit (authorized-sender cross-reference)

For each DKIM selector found in `EmailSecurity.dkimRecords[*].Selector`:

1. Identify the sending platform by selector name pattern:

   | Selector pattern | Platform |
   |---|---|
   | `selector1`, `selector2` | Microsoft 365 (standard selectors) |
   | `google`, `google2` | Google Workspace |
   | `s1`, `s2`, `k1` | Various (check key domain for confirmation) |
   | `scph...` | SendGrid / Twilio |
   | `mxvault`, `mandrill`, `mailchimp` | Mailchimp / Mandrill |
   | `pm`, `pm2` | Postmark |
   | `smtp` | Custom SMTP relay |
   | `dkim` | Generic / self-hosted |
   | `zendesk...` | Zendesk |
   | `sfdc`, `pardot` | Salesforce / Pardot |
   | `hubspot...` | HubSpot |

2. Cross-reference against `SPFRecordBreakdown` — every platform with a
   DKIM selector should also have its mail IPs authorized in SPF. If a
   selector exists without a corresponding SPF include, flag as:
   **DKIM-only sender gap** — DMARC passes on DKIM alignment but SPF
   alignment fails for this sender. If the DKIM key is rotated/expired
   on the sending service without the selector being updated in DNS,
   mail will fail DMARC entirely.

3. Evaluate key strength: `EmailSecurity.dkimRecords[*].PublicKeySize`
   — minimum 2048 bits per `slas.dkim_min_key_bits`.

### Step 6 — Email filter stack identification (from MX records)

Parse `DNSMXRecords[*].Exchange` to identify the inbound email security stack:

| MX exchange pattern | Email platform / filter |
|---|---|
| `*.mail.protection.outlook.com` | Microsoft 365 / Exchange Online Protection |
| `*.google.com` / `aspmx.l.google.com` | Google Workspace |
| `*.mimecast.com` | Mimecast email security |
| `*.pphosted.com` | Proofpoint |
| `*.barracudanetworks.com` | Barracuda Email Security |
| `*.ess.cisco.com` / `*.iphmx.com` | Cisco Email Security (IronPort) |
| `*.spamexperts.com` | SpamExperts |
| `*.messagelabs.com` | Symantec Email Security.cloud |
| `*.mailhop.org` | DuoCircle |
| `*.hornetsecurity.com` | Hornet Security |
| `*.trendmicro.com` | Trend Micro Email Security |
| Raw IP or domain not matching above | On-premises or unknown mail server |

Use `DNSMXRecords[*].ASInfoStr` to confirm the hosting provider of the
MX destination IPs (AS8075 = Microsoft, AS15169 = Google, etc.).

Flag:
- **No dedicated email security gateway** — MX goes directly to M365
  without Proofpoint/Mimecast/Barracuda in front. EOP is decent but a
  third-party gateway adds defense-in-depth.
- **MX provider mismatch** — MX points at Google but SPF only authorizes
  M365 (or vice versa). Indicates a misconfigured or incomplete migration.
- **Multiple MX providers** — mail routing to two different platforms
  simultaneously. Often a migration artifact; creates SPF/DKIM confusion.
- **On-premises mail server** — public IP in MX, no known gateway prefix.
  Credential-bearing server on the internet; high-value attack target.

### Step 7 — Subdomain attack surface mapping

For each entry in `Subdomains[*]`:

1. **Identify WAF/CDN provider** from the `hostname` CNAME target:

   | CNAME target pattern | Provider |
   |---|---|
   | `*.cloudfront.net` | AWS CloudFront CDN (no WAF unless explicitly configured) |
   | `*.cdn.cloudflare.net` / Cloudflare IPs | Cloudflare CDN (WAF may be on, check plan) |
   | `*.akamaiedge.net` / `*.akamaized.net` | Akamai |
   | `*.fastly.net` | Fastly CDN |
   | `*.azureedge.net` | Azure CDN / Front Door |
   | `*.trafficmanager.net` | Azure Traffic Manager |
   | `*.azurewebsites.net` | Azure App Service (no CDN) |
   | `*.s3.amazonaws.com` | AWS S3 — static hosting (no WAF) |
   | `*.elb.amazonaws.com` / `*.compute.amazonaws.com` | AWS direct (no CDN) |
   | `*.googleapis.com` | Google Cloud |
   | CNAME = same as target (no redirect) | Direct hosting — no CDN/WAF |

2. **Flag by risk level:**

   | Signal | Severity | Meaning |
   |---|---|---|
   | `ssl_status = false` on any subdomain | High | Public subdomain with no HTTPS — eavesdropping risk |
   | `vpn.*` subdomain with no SSL | Critical | VPN endpoint potentially unauthenticated |
   | `admin.*`, `portal.*`, `login.*`, `sso.*` with no WAF | High | Credential-bearing surface exposed without WAF |
   | `mail.*`, `smtp.*`, `autodiscover.*` | Medium | Email infrastructure directly exposed |
   | `ftp.*`, `sftp.*` | High | Legacy file-transfer protocol exposed |
   | `dev.*`, `staging.*`, `test.*` with SSL | Medium | Non-production environment reachable |
   | `api.*` with no CNAME (direct IP) | Medium | API surface directly on IP, no CDN/WAF |
   | `_dmarc.*`, `_domainkey.*` | Informational | DNS-only subdomains — expected |
   | CNAME points to deprovisioned service (dangling CNAME) | Critical | Subdomain takeover risk |

3. **Check for dangling CNAMEs** — when `hostname` resolves to a
   third-party service pattern but the `response` (HTTP status) is 404
   or the IP is non-routable, the CNAME may be dangling. Dangling CNAMEs
   on services like GitHub Pages, Heroku, or AWS S3 are exploitable for
   subdomain takeover (an attacker claims the deprovisioned resource
   and inherits the subdomain).

### Step 8 — WAF/CDN edge posture summary

From the subdomain CNAME data (Step 7) and the TLS inspector (Step 9),
synthesize the WAF/CDN posture:

| Question | Source | Finding |
|---|---|---|
| Is the main web property CDN-fronted? | `www.*` CNAME hostname | CDN identified / direct IP |
| Is the CDN also a WAF? | CDN provider type | Cloudflare/Akamai/Fastly = WAF capability; CloudFront/Azure CDN = CDN only unless WAF explicitly configured |
| Are credentialed subdomains (admin, portal, login) protected? | Per subdomain CNAME | Flag unprotected |
| Is the WAF configuration credentialed? | Cloudflare inspector (if deployed) | Full WAF rule-set only visible with Cloudflare inspector |
| Are any subdomains bypassing the CDN? | Subdomains pointing to origin IPs | Origin IP exposure |

> **Cloudflare note:** The `www.*` subdomain CNAME resolving to
> `*.cdn.cloudflare.net` confirms Cloudflare is proxying, but the WAF
> rule-set, SSL Mode, minimum TLS version, and Bot Management config
> are only visible via the credentialed Cloudflare inspector. Surface
> this as a coverage note when Cloudflare is detected but the inspector
> is not deployed.

### Step 9 — TLS/SSL certificate and protocol posture

For each TLS/SSL system associated with this domain:

**JMESPath paths (validated against live TLS inspector dataprint):**

```jmespath
# Certificate basics
SystemInfo.{
  SSLCertExists: SSLCertExists,
  ValidFrom: ValidFrom,
  ExpiresOn: ExpiresOn,
  SubjectCommonName: SubjectCommonName,
  AltNames: AltNames,
  IssuerOrganizationName: IssuerOrganizationName,
  IssuerCommonName: IssuerCommonName,
  SSLMatchNames: SSLMatchNames,
  Redirects: Redirects,
  RedirectsTo: RedirectsTo,
  PublicKeyAlgorithm: PublicKeyAlgorithm,
  SignatureAlgorithm: SignatureAlgorithm
}

# Protocol version support
SystemInfo.Protocols.{tls1: tls1, tls1_1: tls1_1, tls1_2: tls1_2, tls1_3: tls1_3}

# Days to expiration
Intel.SSLCertDaysTillExpiration

# Certificate transparency + pinning
SystemInfo.{SHA256Fingerprint: SHA256Fingerprint, PublicKeyPin: PublicKeyPin}

# OCSP / AIA revocation
SystemInfo.{OCSPUrl: OCSPUrl, AIAUrl: AIAUrl}

# Extensions (key usage, EKU, CT, SANs)
Extensions[*].{name: name, oid: oid, critical: critical, value: value}
```

Evaluate against `slas.prohibited_protocols`, `slas.min_tls_version`,
and `slas.hsts_required`.

**HTTP → HTTPS redirect check:**
- `SystemInfo.Redirects = true` AND `SystemInfo.RedirectsTo` contains
  `https://` → compliant
- `SystemInfo.Redirects = false` with HTTPS available → flag: HTTP
  traffic not automatically upgraded

**Name mismatch check:**
- `SystemInfo.SSLMatchNames = false` → certificate does not cover the
  monitored hostname. Browsers will show a security warning.

### Step 10 — Credential exposure (Dark Web)

Pull from the Dark Web inspector using the validated dataprint structure:

```jmespath
# Aggregate counts
NumberOfUsersWithDataBreach               # integer — users matched in breach corpus
NumberOfTotalBreaches                     # integer — total breach events

# Per-user detail (for IT-director eyes-only output)
Users[*].{Email: Email, Breaches: Breaches}
```

**Cross-reference with identity inventory** (when credentialed):

```
liongard_identity LIST environmentId=<ENV_ID>
  fields=["username","accountType","privileged","mfaStatus","lastLogin","enabled"]
```

Join on email address. Exposed + active + no MFA = Critical. Flag each
combination per the dark-web-monitoring.md recipe.

**BEC amplification:** Cross-reference breach corpus emails against the
SaaS footprint from Step 4. An exposed credential for a user who also
has access to a payroll platform (Rippling, Gusto, Workday) identified
in the TXT record scan is a BEC pre-condition: attacker has the
credential + knows the target system.

### Step 11 — Network IP reputation (for mail-sending IPs)

For each IP in `DNSMXRecords[*].AddressStr` (the IPs resolving from
the MX exchange):

If Network IP inspectors are deployed for these IPs, pull:

```jmespath
SystemInfo.{
  Ip: Ip,
  ReverseLookup: ReverseLookup,
  AS: AS,
  ASInfo: ASInfo
}
```

Flag:
- **Blocklisted mail-sending IP** — if the IP ASN is known-bad or the
  reverse DNS doesn't match the claimed MX provider. Note: most M365
  and Google Workspace IPs rotate via the provider's shared pools and
  will not be individually inspected. Surface this section only when
  the customer uses a dedicated mail IP (on-premises relay, custom SMTP).

When Network IP inspectors are not deployed, note the coverage gap
and recommend deployment for the outbound mail relay IPs.

### Step 12 — BEC risk scoring

Synthesize the above signals into a BEC risk assessment. Three attack
paths matter most:

**Path 1 — Domain impersonation / spoofing**

The attacker sends email claiming to be `@<domain>` without owning the
domain. Gated by email authentication.

| Condition | Effect on risk |
|---|---|
| DMARC at `p=none` | Spoofed email **delivered to inbox** — critical path open |
| DMARC at `p=quarantine` | Spoofed email goes to spam — degraded but partial path |
| DMARC at `p=reject` | Spoofed email rejected — this path blocked |
| SPF missing | Spoofing via unauthenticated MTA is possible |
| DKIM missing | No cryptographic authentication — domain spoof undetectable by DKIM |

**Path 2 — Credential theft + account takeover**

The attacker obtains a user's credential (from breach corpus or
phishing) and authenticates to a service that uses this domain's SSO.

| Condition | Effect on risk |
|---|---|
| Credentials in breach corpus | Attacker already has candidate passwords |
| No MFA on exposed accounts | Credential → immediate access |
| Payroll/HR/finance SaaS in TXT footprint + no MFA | Direct financial-fraud path |
| Multiple MS= records (shadow tenant) | Attacker may target the less-monitored tenant |

**Path 3 — Phishing via lookalike / authorized sender abuse**

The attacker uses a legitimate authorized sender (e.g., Pardot, HubSpot)
or a typo-squat domain to deliver phishing.

| Condition | Effect on risk |
|---|---|
| Marketing email platforms (Pardot/HubSpot/Mailchimp) in TXT footprint | Platform-originated phishing has real DKIM; hard to detect |
| DKIM-only sender gaps (Step 5) | Mail from these services passes DMARC even with SPF failures |
| DocuSign / Adobe Sign in footprint | e-Signature phishing is highly effective |
| Dark web credential exposure | Targets the sender's service for supply-chain phishing |

**BEC Risk Score (composite):**

Produce a 5-point composite risk score with one-line rationale for each
contributing factor:

```
1. Domain spoofability     (DMARC policy level)
2. SPF posture             (record quality + DKIM-only sender gaps)
3. Credential exposure     (dark web count + MFA coverage)
4. SaaS attack surface     (high-value phishing-target services in footprint)
5. Email filter strength   (dedicated gateway vs. platform-native only)
```

Score each 1–5 (1 = best, 5 = worst). Average to a composite. Present
as: Low (1.0–2.0) / Medium (2.1–3.5) / High (3.6–4.5) / Critical (4.6–5.0).

### Step 13 — Phishing and ransomware initial-access risk

Beyond BEC, surface the findings that matter for phishing-to-ransomware
kill chains:

| Signal | Ransomware relevance |
|---|---|
| VPN/RDP subdomain with no SSL | Credential-stuffing / brute-force entry point |
| Admin/portal subdomains without WAF | Credential theft via web attack |
| `staging.*` / `dev.*` reachable from internet | Often has weaker auth; same credentials as prod |
| Dangling CNAME (subdomain takeover) | Attacker-controlled subdomain passes domain trust checks |
| TLS 1.0/1.1 on any subdomain | Weak encryption on potentially sensitive service |
| Payroll/HR SaaS in footprint | Wire-transfer fraud / payroll diversion |
| Exposed RDP / SMB in Network IP (if deployed) | Direct lateral-movement entry point |
| Credentials in breach corpus for known admin accounts | Domain admin exposure = ransomware pre-condition |

### Step 14 — Expiration calendar

Compile all time-sensitive expirations into a single calendar table:

| Item | Expiration date | Days remaining | Severity | Action |
|---|---|---|---|---|
| Domain registration | `DomainExpirationDate` | `DaysTillExpiration` | per slas | Renew / enable auto-renew |
| TLS certificate (each host) | `ExpiresOn` | `Intel.SSLCertDaysTillExpiration` | per slas | Renew + deploy |

### Step 15 — Combined risk story synthesis

This section is what makes the recipe a discovery tool rather than a
checklist. For the top 3–5 combined findings, write a 2–3 sentence
narrative in the form:

> **"[Attacker capability] because [finding A] combined with [finding B].
> This enables [specific attack scenario]. Risk: [impact]."**

Example patterns from live data:

| Combined finding | Narrative template |
|---|---|
| DMARC `p=quarantine` + Pardot in TXT footprint | "Spoofed emails from `@<domain>` land in spam — but email sent via the legitimately-authorized Pardot platform will pass DMARC, DKIM, and SPF. A phisher with access to the Pardot instance (or who has purchased a trial) can send fully-authenticated marketing emails from your domain at scale." |
| Rippling (payroll) in TXT + credentials in breach corpus | "<N> users' credentials are in breach corpora. Rippling HR/payroll is authorized to send email from this domain. An attacker with one of these credentials has a clear path to payroll diversion." |
| `vpn.*` subdomain with no SSL + dark web exposure | "The VPN endpoint at `vpn.<domain>` is reachable without TLS. Credential-stuffing attacks using the <N> exposed credentials from breach corpora can attempt authentication with no encryption in transit — the session is potentially observable." |
| Multiple `MS=` records + no MFA signal | "Two Microsoft domain-verification records suggest a possible shadow tenant or incomplete migration. If a secondary M365 tenant exists and is unmonitored, users may be logging in to unmanaged cloud resources with the same credentials that appear in breach corpora." |
| DKIM `google` selector + Google not in SPF | "Google Workspace is signing email from this domain (DKIM selector `google` is present) but Google IPs are not authorized in the SPF record. DMARC passes on DKIM alignment alone — but if this DKIM key is ever rotated or the sending service changes, DMARC enforcement will silently break." |

### Step 16 — QA pass (per `reference/qa-retry-pattern.md`)

This recipe's QA pass especially focuses on:

1. **Retry null email-security fields** — DMARC/SPF/DKIM propagation can
   cause transient nulls on freshly-changed records. Use `retry_attempts: 2`.
2. **Privacy validation before any output** — confirm
   `privacy.redact_individual_users_in` has been honored. Breach corpus
   per-account data never appears in pptx or executive-tone output.
3. **DKIM-only sender gap cross-check** — manually verify the selector-
   to-SPF cross-reference. Automation can misidentify selectors with
   generic names (`dkim`, `s1`, `smtp`).
4. **Dangling CNAME confirmation** — HTTP status 404 on a CNAME target
   does not always mean the CNAME is dangling (origin may have rate-
   limited). Verify externally before calling it takeover-vulnerable.
5. **Shadow-tenant interpretation** — multiple `MS=` records are
   suspicious but not conclusive. Flag for manual follow-up: ask the
   customer to enumerate their M365 tenants.
6. **Cloudflare WAF coverage gap note** — when Cloudflare CNAMEs are
   found but the Cloudflare inspector is not deployed, note this as a
   coverage gap with upgrade path.

### Step 17 — Render output

**For pre-sales (pptx, executive tone):**

Recommended slide order:
1. Cover — "[Customer/Prospect] External Attack Surface Assessment — [date]"
2. What We Examined — inspector inventory + domain scope
3. BEC Risk Score — the 5-factor composite with traffic-light summary
4. Combined Risk Story — top 3 combined findings (no per-user names)
5. Email Authentication Posture — SPF/DKIM/DMARC pass/fail tiles
6. SaaS Footprint — identified services table with risk callouts
7. Email Filter Stack — MX-derived filter chain identification
8. Subdomain Surface — table of subdomains with risk flags
9. Credential Exposure — aggregate counts only (no user names in deck)
10. Expiration Calendar — domain + cert timeline
11. Quick Wins — first 30 days
12. Recommended Engagement — MSP services mapped to findings
13. Next Steps — CTAs

**For IT-director leave-behind (word, balanced tone):**
Same structure, add per-finding technical detail and full JMESPath
query log in the appendix.

**For SOC working document (markdown, technical tone):**
Full technical detail, per-account breach table (IT-director-eyes-only),
all JMESPath references, proposed-metric gaps noted.

---

## Insights & recommendations — generation patterns

### Email authentication

| Pattern | Recommendation template |
|---|---|
| DMARC at `p=none` | "Upgrade DMARC from monitoring (`p=none`) to enforcement (`p=quarantine` then `p=reject`). Every day at `p=none` is a day spoofed email from `@<domain>` is delivered." |
| DMARC at `p=quarantine` | "Advance DMARC from `p=quarantine` to `p=reject` after reviewing the aggregate report. Current policy puts spoofed mail in spam — `p=reject` stops it entirely." |
| DMARC missing `rua` | "Add an aggregate-report URI (`rua=`) to the DMARC record. Without it, you cannot see what's failing authentication and you cannot safely move to enforcement." |
| DKIM-only sender (not in SPF) | "Add <service>'s sending IPs to the SPF record. Currently DMARC passes on DKIM alignment alone — if DKIM breaks for this service, DMARC fails silently." |
| SPF `+all` or missing `-all`/`~all` | "Tighten the SPF record: change `+all` to `-all` (or at minimum `~all`) after confirming all legitimate senders are included." |
| SPF lookup count > 10 | "SPF include chain exceeds the RFC 7208 DNS-lookup limit. Refactor using SPF record flattening or DNS-based SPF optimization service." |
| Multiple DKIM selectors from same platform | "Two DKIM selectors for the same platform may indicate a pending key rotation. Confirm which is active and retire the old selector after cutover." |

### SaaS footprint

| Pattern | Recommendation template |
|---|---|
| Payroll/HR service in footprint + DMARC < `p=reject` | "Rippling/Gusto/Workday is authorized to send email from `@<domain>`, and DMARC is not at `p=reject`. A phisher impersonating payroll communications will have a high delivery rate. Priority: move DMARC to enforcement AND enroll payroll-platform users in phishing-resistant MFA." |
| Marketing platform in footprint | "Pardot/HubSpot/Mailchimp is authorized to send from `@<domain>`. Ensure login to this platform is protected with MFA and monitored for unauthorized campaign creation." |
| Multiple `MS=` records | "Two Microsoft domain-verification records detected. Enumerate all M365 tenants claiming this domain and confirm none are unmanaged. Shadow tenants are a known compliance and security gap." |
| DocuSign/Adobe Sign in footprint | "e-Signature platforms authorized to send from `@<domain>`. Phishing via fake DocuSign/Adobe requests is highly effective. Confirm MFA is enforced on the e-signature platform account." |

### Subdomain surface

| Pattern | Recommendation template |
|---|---|
| Subdomain with no SSL | "Subdomain `<target>` is publicly reachable without HTTPS. Provision a certificate and enforce HTTPS-only access." |
| VPN subdomain with no SSL | "URGENT: VPN endpoint `<target>` is reachable without SSL. Credential-stuffing attacks against this endpoint have no encryption in transit. Provision a certificate immediately." |
| Admin/portal subdomain without WAF | "Login surface `<target>` is directly hosted without a WAF. Consider routing through Cloudflare or equivalent WAF/reverse-proxy before launch/promotion." |
| Dangling CNAME candidate | "`<subdomain>` CNAME points to a deprovisioned service. Verify whether this subdomain is still needed; if not, remove the DNS record to prevent subdomain takeover." |
| `dev.*`/`staging.*` reachable | "Non-production environment `<target>` is reachable from the internet. Confirm auth is segregated from production and restrict access to known IPs." |

### TLS/SSL

| Pattern | Recommendation template |
|---|---|
| Certificate expiring < warn SLA | "Certificate for `<host>` expires in <N> days. Order renewal and schedule deployment before expiration." |
| No HTTP → HTTPS redirect | "HTTP traffic to `<host>` is not automatically redirected to HTTPS. Enable a server-side 301 redirect and deploy HSTS." |
| TLS 1.0 / 1.1 supported | "Disable TLS 1.0 and 1.1 on `<host>`. Both are deprecated and fail modern compliance baselines." |
| Certificate name mismatch | "The certificate on `<host>` does not cover the monitored hostname. Replace with a cert that includes this hostname in the SAN list." |

---

## Data gaps & coverage notes

| Area | Gap | What fills it |
|---|---|---|
| DKIM key rotation history | Liongard sees current selectors only — rotation cadence is external | Sending-service vendor portal |
| SPF-authorized senders' IP reputation | SPF includes are resolved but reputation of those IPs is external | Network IP inspector on outbound relay IPs |
| WAF rule-set (Cloudflare) | CNAME confirms Cloudflare proxy; WAF config requires credentialed Cloudflare inspector | Deploy Cloudflare inspector |
| Brand look-alike / typo-squat domains | External to all four inspectors | Brand-protection service |
| Email volume / deliverability telemetry | Mail flow data is inside M365/GWS platform | Microsoft 365 inspector (message trace) |
| Sender reputation / RBL for shared provider IPs | M365 / GWS use shared IP pools that can't be individually inspected | Provider reputation dashboard |
| Internal DNS (split-horizon) | Liongard sees public resolution only | Internal scanning tool |
| Active exploitation attempts | SIEM / EDR event data | SIEM (out of scope for external-only recipe) |
| Personal-email breach exposure of employees | Breach corpus matches `@<domain>` only | Partner-provided tool covering personal email |

---

## Relationship to other recipes

- **`all-external-attack-surface.md`** — fleet breadth rollup; this
  recipe is the single-domain depth complement. Use the rollup when
  you need a cross-environment scorecard; use this recipe when one
  domain needs the full treatment.
- **`pre-sales-discovery.md`** — the cross-cutting sales recipe; this
  domain assessment is the zero-credential anchor section within it.
- **`internet-domain-dns.md`** — single-system recipe for the DNS
  inspector; this recipe goes deeper on every section.
- **`dark-web-monitoring.md`** — single-system recipe; referenced in
  Step 10 for the per-account cross-reference pattern.
- **`compliance/cyber-insurance/domains/auth.md`** — the cyber-insurance
  email-auth domain file; the BEC risk story here maps directly to the
  auth domain's questions.
- **`compliance/cyber-insurance/cyber-insurance-readiness.md`** — this
  recipe's SPF/DKIM/DMARC and credential-exposure findings answer the
  external-attack-surface evidence questions in the cyber-insurance
  application directly.

---

## QA & Manual Verification

Per `reference/qa-retry-pattern.md`. Manual checks specific to this recipe:

- **DKIM selector identity** — automated selector-to-platform mapping
  can be wrong for generic names. Confirm with the customer which
  platforms are active before filing a remediation ticket.
- **Shadow-tenant verification** — ask the customer to list their M365
  tenants if multiple `MS=` records are found. Never assume; false
  positives here are credibility-damaging.
- **Subdomain takeover verification** — confirm a dangling CNAME
  externally (multiple resolvers, `nslookup`) before presenting as a
  finding.
- **Breach-corpus freshness** — confirm the Dark Web inspector's last
  inspection date is within `qa.flag_inspector_lastseen_threshold_days`
  before citing exposure counts.
- **Privacy clearance** — confirm per-user breach data has been
  removed from any deck or Word output before delivery.

---

## Verification log

```
| Step | Tool | Args | Result shape | Status |
|------|------|------|--------------|--------|
| 1  | liongard_environment LIST | query=<customer> | array<environment> | ok |
| 1  | liongard_launchpoint LIST | systemType=Internet Domain envIds=[<ENV>] | array<launchpoint> | ok |
| 1  | liongard_launchpoint LIST | systemType=TLS envIds=[<ENV>] | array<launchpoint> | ok |
| 1  | liongard_launchpoint LIST | systemType=Dark Web envIds=[<ENV>] | array<launchpoint> | ok |
| 1  | liongard_launchpoint LIST | systemType=Network IP envIds=[<ENV>] | array<launchpoint> | ok |
| 2  | liongard_timeline LIST | envId=<ENV> | array<timeline-entry> | ok |
| 3  | liongard_metric GENERATE_AND_EVALUATE | sysId=<DOMAIN> envId=<ENV> | full DNS/email dataprint | ok |
| 4  | (SaaS footprint — derived from DNSTXTRecords) | — | saas-inventory table | ok |
| 5  | (DKIM selector audit — derived from EmailSecurity.dkimRecords) | — | selector-spf cross-ref | ok |
| 6  | (Email filter stack — derived from DNSMXRecords) | — | filter-stack table | ok |
| 7  | (Subdomain surface — derived from Subdomains[*]) | — | subdomain-risk table | ok |
| 8  | (WAF/CDN posture — derived from Subdomains[*].hostname) | — | waf-cdn summary | ok |
| 9  | liongard_metric GENERATE_AND_EVALUATE | sysId=<TLS> envId=<ENV> | cert + protocol data | ok |
| 10 | liongard_metric GENERATE_AND_EVALUATE | sysId=<DARKWEB> envId=<ENV> | breach counts | ok |
| 10 | liongard_identity LIST | envId=<ENV> [fields] | identity inventory | ok (if credentialed) |
| 11 | liongard_metric GENERATE_AND_EVALUATE | sysId=<NETIP> envId=<ENV> | IP + ASN + reverse DNS | ok (if deployed) |
| 12 | (BEC risk scoring — derived) | per threat-path signals | 5-factor composite score | ok |
| 13 | (Phishing/ransomware risk — derived) | per signal table | risk findings | ok |
| 14 | (Expiration calendar — derived) | DaysTillExpiration + Intel.SSLCertDaysTillExpiration | calendar table | ok |
| 15 | (Combined risk story — derived) | per narrative patterns | 3-5 combined findings | ok |
| 16 | QA pass | per reference/qa-retry-pattern.md + privacy check | varies | ok |
| 17 | render | per output.format | <artifact path> | ok |
```

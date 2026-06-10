---
name: single-system-tls-ssl
description: >
  Use this skill when the user wants a single-host TLS/SSL certificate
  analysis — certificate expiration risk, issuer trust, key strength,
  protocol versions supported (TLS 1.0 / 1.1 / 1.2 / 1.3), cipher
  weakness, chain validity, or encryption-in-transit compliance
  evidence. Trigger phrases: "TLS check for <host>", "SSL cert review",
  "is <host>'s cert expiring", "certificate inventory for <customer>",
  "encryption in transit evidence", "what protocols does <host>
  support", "weak cipher detection on <host>". Non-credentialed —
  pulls entirely from public TLS handshake data on the host's exposed
  endpoint, making it suitable for prospects and pre-sales discovery.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric"
personas: [sales, vcio-account-manager, soc, technical-alignment-manager]
output_formats: [markdown, word, pptx, xlsx]
primitives:
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

# Single-System Analysis — TLS/SSL Certificates

> **Inspector:** `tls-ssl-inspector` (ID 16). Cloud category.
> External-attack-surface family. **One system per monitored host**
> (typically the customer's public-facing web / mail / VPN endpoints).
> Pulls entirely from public TLS handshake data — **no customer
> credential required**.
>
> **References:** `reference/inspector-aliases.md` (TLS, SSL, Cert).
> Pairs with `internet-domain-dns.md` for the full external mail /
> web posture story.

---

## Pre-Sales Discovery Value

TLS/SSL findings are some of the most-credibility-building discovery
content available, for two reasons:

1. **Encryption-in-transit is a near-universal compliance question.**
   Cyber-insurance, CMMC, HIPAA, PCI-DSS, and SOC 2 all ask "is data
   transported encrypted, and with what strength?" The TLS inspector
   produces the literal evidence — protocol versions supported, cipher
   suites accepted, certificate validity — that compliance assessors
   want.
2. **Expiring certificates are catastrophic.** A cert expires →
   service outage. Surfacing a soon-to-expire cert before the prospect
   notices is the kind of finding that becomes the proposal anchor:
   "we monitor this 24/7 so this doesn't happen to you."

Like the Internet Domain inspector, this runs with no prospect
credential. Accepts a list of hostnames or URLs in
`customization.discovery_input.hosts[]` for the pre-sales /
trial-environment mode.

> **Sales narrative tip:** A prospect's customer-facing web property
> (the marketing site, their app, their customer portal) is where TLS
> findings have the most business impact. Lead with those hosts in the
> deck; treat internal-only endpoints as appendix material.

> **Deep-dive variant:** For a combined external attack surface
> narrative that rolls TLS/SSL posture together with domain email
> authentication, dark web credential exposure, and BEC risk scoring,
> use `recipes/domain-assessment/external-attack-surface-deep-dive.md`.
> That recipe is the roll-up; this one is the single-inspector deep-dive.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer-or-prospect>-<host>-tls-review-<date>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  certificate: "Certificate Details"
  expiration: "Expiration Risk"
  trust_chain: "Trust Chain"
  protocols: "Protocol Versions Supported"
  ciphers: "Cipher Suite Strength"
  key_strength: "Key Strength"
  vulnerabilities: "Known Vulnerabilities (HEARTBLEED / POODLE / ROBOT / etc.)"
  hsts: "HSTS & Security Headers"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"                       # technical | balanced | executive

slas:
  # TLS / SSL — inherits from config/msp-config.yaml:
  #   slas.ssl_cert_expiration_warn_days     (default 45)
  #   slas.ssl_cert_expiration_critical_days (default 14)
  #   slas.min_tls_version                   (default "TLSv1.2")
  #   slas.prohibited_tls_protocols          (default ["TLSv1.0","TLSv1.1","SSLv3"])
  #   slas.hsts_required                     (default true)
  #   slas.http_to_https_redirect_required   (default true)
  # Override per-recipe only if this customer has a different standard.
  expiration_critical_days: 14           # override: inherits from msp-config slas.ssl_cert_expiration_critical_days
  expiration_warn_days: 45               # override: inherits from msp-config slas.ssl_cert_expiration_warn_days
  min_key_size_rsa: 2048
  min_key_size_ec: 256
  prohibited_protocols: ["SSLv2", "SSLv3", "TLSv1.0", "TLSv1.1"]
  required_protocols: ["TLSv1.2", "TLSv1.3"]
  preferred_protocol: "TLSv1.3"
  prohibited_ciphers: ["NULL", "EXPORT", "RC4", "DES", "3DES", "MD5"]
  hsts_required: true                    # inherits from msp-config slas.hsts_required
  http_to_https_redirect_required: true  # inherits from msp-config slas.http_to_https_redirect_required
  certificate_transparency_required: true
  prohibited_issuers: []                 # add CAs the MSP refuses (e.g. expired roots)

reporting_period:
  default: "current_state"

discovery_input:
  # Non-credentialed pre-sales mode. When environmentId is not provided,
  # supply a list of hostnames/URLs here.
  mode: "credentialed"                   # credentialed | discovery
  hosts: []                              # ["www.prospect.com:443", "mail.prospect.com:993"]

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

- "TLS check for <host>"
- "SSL cert review for <customer>"
- "Is <host>'s cert expiring?"
- "Certificate inventory for <customer>"
- "Encryption-in-transit evidence for the cyber-insurance form"
- "What TLS protocols does <host> support?"
- "Weak cipher detection on <host>"
- "Pre-sales TLS analysis for <prospect>"

Cadence: monthly per critical customer-facing host (cert expiration);
quarterly for internal hosts; on-demand during pre-sales, audit prep,
or post-vulnerability-disclosure (e.g., new TLS protocol weakness
announced).

Personas:
- **Sales** (primary in discovery mode — public-data findings power
  the proposal; expiring certs become quick wins)
- **vCIO / Account Manager** (renewal calendar, compliance pre-renewal
  evidence)
- **SOC** (incident response — confirm encryption posture after a
  reported breach; compliance evidence ownership)
- **TAM** (remediation — drives the customer to MSP-standard
  cipher / protocol baseline)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes (credentialed mode) | `liongard_environment LIST` |
| System ID (the specific TLS-monitored host system) | Yes — one per recipe run | `liongard_system LIST query="tls"` |
| Hostname(s) | Yes (discovery mode) | User-provided; see `discovery_input.hosts` |
| Optional: focus area | No | User prompt — e.g., "focus on protocol compliance" |

> **System-per-host.** The `tls-ssl-inspector` creates one Liongard
> system per monitored TLS endpoint. A customer with multiple
> public-facing endpoints (web, mail, VPN) has multiple systems under
> this inspector.

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer-or-prospect>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="tls"
# Pick the specific host's system.
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

Confirm last inspection. Certs change rarely, but protocol /
cipher support can change after a vendor patch. Stale data should be
re-inspected before formal compliance evidence is generated.

### Step 3 — Pull the certificate and handshake details (validated JMESPath paths)

Use `liongard_metric GENERATE_AND_EVALUATE` with the JMESPath expressions below.
These paths are validated against the live TLS/SSL inspector dataprint.

```
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  jmesPath="<path>"

# Certificate identity + validity
#   SystemInfo.SSLCertExists                         (boolean)
#   SystemInfo.ValidFrom                             (ISO date string)
#   SystemInfo.ExpiresOn                             (ISO date string)
#   Intel.SSLCertDaysTillExpiration                  (integer — primary expiration field)
#   SystemInfo.AltNames                              (array of SANs — subject alternative names)
#   SystemInfo.SSLMatchNames                         (boolean — cert CN/SANs match the probed hostname)
#   SystemInfo.SHA256Fingerprint
#   SystemInfo.PublicKeyPin                          (HPKP pin; useful for pinning audits)

# Key + algorithm
#   SystemInfo.PublicKeyAlgorithm                    (RSA | ECDSA | etc.)
#   Extensions[*]                                    (cert extension objects)

# Protocol support — string values, NOT booleans (validated)
#   SystemInfo.Protocols.tls1                        (TLS 1.0 — value: "Supported" or other)
#   SystemInfo.Protocols.tls1_1                      (TLS 1.1 — value: "Supported" or other)
#   SystemInfo.Protocols.tls1_2                      (TLS 1.2 — should be "Supported")
#   SystemInfo.Protocols.tls1_3                      (TLS 1.3 — preferred "Supported")
#   Evaluation: flag tls1 or tls1_1 = "Supported" as a finding (deprecated)

# HTTP→HTTPS redirect posture
#   SystemInfo.Redirects                             (boolean — HTTP endpoint redirects)
#   SystemInfo.RedirectsTo                           (URL — where HTTP redirects; confirm is HTTPS)

# Revocation infrastructure
#   SystemInfo.OCSPUrl                               (OCSP responder URL from cert extension)
#   SystemInfo.AIAUrl                                (Authority Information Access URL)
```

> **Metric availability.** Enumerate what's available with
> `liongard_metric LIST environmentId=<ENV_ID> systemId=<SYS_ID>`.
> File a metric request via the `liongard-metrics` skill for any
> gap that blocks a baseline check. The JMESPath paths above are
> validated from live dataprints; cipher-suite and vulnerability-flag
> fields may be data gaps not yet in the standard set.

### Step 3a — HTTP redirect, name-match, and revocation posture

These fields from the validated dataprint cover checks that are separate from cert expiration:

| Field | Check | Severity if failing |
|---|---|---|
| `SystemInfo.Redirects` | `true` — HTTP endpoint redirects to HTTPS | High if false when `http_to_https_redirect_required = true` |
| `SystemInfo.RedirectsTo` | Confirm target is `https://...` (not HTTP loop or different domain) | High if redirect target is not HTTPS |
| `SystemInfo.SSLMatchNames` | `true` — cert CN/SANs match the probed hostname | Critical if false — browser will show cert mismatch error |
| `SystemInfo.OCSPUrl` | Populated — OCSP responder URL present in cert extension | Low/informational if absent on public-CA cert |
| `SystemInfo.AIAUrl` | Populated — AIA URL present (used for chain building) | Low/informational if absent |

> **Redirect chain integrity:** When `RedirectsTo` is present, trace the full redirect chain.
> A chain that goes `http://` → `http://` → `https://` is still a downgrade-attack window
> for the first hop.

### Step 4 — Expiration evaluation

| Signal | Severity |
|---|---|
| `Intel.SSLCertDaysTillExpiration` ≤ `slas.expiration_critical_days` | Critical |
| `Intel.SSLCertDaysTillExpiration` ≤ `slas.expiration_warn_days` | High |
| `Intel.SSLCertDaysTillExpiration` > `slas.expiration_warn_days` | Informational |
| `SystemInfo.SSLCertExists = false` | Critical — no cert detected |
| Cert already expired (`ExpiresOn` in past) | Critical — service degraded |

### Step 5 — Trust chain + transparency

| Signal | Outcome |
|---|---|
| `chainValid = false` | Critical — cert not trusted by major browsers |
| Issuer is self-signed (production host) | High — should be public CA |
| Issuer not on MSP-approved CA list | Low — consolidation opportunity |
| `transparencyLogged = false` | Medium — modern browsers may distrust |

### Step 6 — Protocol + cipher evaluation

For each protocol version supported by the host, check against
`slas.prohibited_protocols` + `slas.required_protocols`.
`SystemInfo.Protocols.*` values are strings: `"Supported"` indicates the protocol is
active. SSLv2/SSLv3 are not tracked in the `Protocols` object — check cipher suite
acceptance for those:

| Signal | Outcome |
|---|---|
| `Protocols.tls1 = "Supported"` | High — deprecated protocol, compliance-failing |
| `Protocols.tls1_1 = "Supported"` | High — deprecated protocol, compliance-failing |
| `Protocols.tls1_2` not `"Supported"` | Critical — modern client incompatibility |
| `Protocols.tls1_3` not `"Supported"` | Medium — modern best-practice missing |
| Weak ciphers accepted (NULL / EXPORT / RC4 / DES / 3DES / MD5) | High — manual cipher-suite review required; no catalog metric |
| Server-preferred cipher is weak | Medium — manual cipher-suite review required; no catalog metric |

### Step 7 — Key strength evaluation

| Signal | Outcome |
|---|---|
| RSA key < `slas.min_key_size_rsa` (default 2048) | High — re-issue required |
| ECDSA key < `slas.min_key_size_ec` (default 256) | High |
| SHA-1 signature algorithm | High — distrusted by major browsers |

### Step 8 — Known-vulnerability check

For each tracked TLS vulnerability (HEARTBLEED, POODLE, ROBOT, BEAST,
LOGJAM, FREAK, etc.):

| Signal | Outcome |
|---|---|
| Vulnerable flag = true | Critical — patch / reconfigure required |

### Step 9 — HSTS / security headers (HTTPS hosts only)

| Signal | Outcome |
|---|---|
| HSTS header missing | Medium — downgrade-attack exposure |
| HSTS `max-age` < 6 months | Low — short enforcement window |
| `includeSubDomains` directive missing | Low |
| `preload` directive missing on customer's flagship domain | Low |

### Step 10 — QA pass (per `reference/qa-retry-pattern.md`)

This recipe's QA pass especially focuses on:

1. **Retry persistent nulls** on handshake metrics — TLS probes can be
   blocked by WAF rate-limiting, especially at first contact.
2. **Flag stale inspectors** from Step 2.
3. **Cross-reference with the Internet Domain inspector** — when the
   monitored host is the canonical mail / web endpoint for a domain
   covered by the domain inspector, surface the cert posture next to
   the mail-trust posture in a combined finding row.
4. **Proposed-metric gaps** surface in the verification log + file a
   metric request via `liongard-metrics`.
5. **WAF / CDN obfuscation** — when the host is fronted by a WAF or
   CDN (Cloudflare, Akamai), Liongard observes the WAF's TLS posture
   rather than the origin's. Note this in findings so the customer
   knows the evidence reflects the edge layer.

### Step 11 — Render output

| Output mode | Best for |
|---|---|
| `markdown` | Working draft / IT-director audience |
| `word` | Customer-facing letter / compliance evidence appendix |
| `pptx` | Slide-per-host for the pre-sales / QBR deck |
| `xlsx` | Multi-host rollup with filterable findings (cross-system) |

---

## QA & Manual Verification

Per `reference/qa-retry-pattern.md`. Manual checks specific to this
recipe:

- **WAF / CDN identification** — verify whether the observed TLS
  posture reflects an edge layer rather than the origin.
- **Cipher-preference confirmation** — Liongard observes the
  server-preferred cipher; if customer policy requires server-side
  cipher ordering (vs. client-side), confirm via vendor console.
- **Cert deployment confirmation** — when a cert is about to expire,
  confirm the renewal cert has been issued + is awaiting deployment
  vs. not yet ordered.
- **OCSP / CRL status** — partial; full revocation-status verification
  requires CA-side data.

---

## Insights & recommendations — generation patterns

| Pattern | Recommendation template |
|---|---|
| Cert expiring < critical | "URGENT: Renew + deploy <host>'s certificate. Expires in <N> days. Service outage imminent." |
| Cert expiring < warn | "Order renewal certificate for <host> within the next <N> days." |
| Self-signed cert (production) | "Replace self-signed cert on <host> with a public-CA-issued cert." |
| Untrusted chain | "Repair certificate chain on <host>. Browsers will reject as untrusted." |
| TLS 1.0 / 1.1 supported | "Disable TLS 1.0 / 1.1 on <host>. Deprecated; fails most compliance baselines." |
| SSLv2 / SSLv3 supported | "URGENT: Disable SSLv2 / SSLv3 on <host>. Known-broken protocols." |
| TLS 1.3 not supported | "Enable TLS 1.3 on <host> if vendor / appliance supports it." |
| Weak ciphers accepted | "Remove weak ciphers (<list>) from <host>'s allowed cipher list." |
| RSA key < 2048 | "Re-issue <host>'s certificate with a ≥ 2048-bit RSA key (or ECDSA equivalent)." |
| SHA-1 signature | "Re-issue <host>'s certificate with SHA-256 (or stronger) signature." |
| Known vulnerability flagged | "URGENT: Patch <host> for <CVE-name>. Reconfigure cipher/protocol if patching not available." |
| HSTS missing | "Enable HSTS on <host>. Recommend `max-age=15552000; includeSubDomains; preload`." |
| HTTP not redirecting to HTTPS | "Configure <host>'s HTTP endpoint to redirect to HTTPS. Prevents downgrade attacks." |
| Cert name mismatch (`SSLMatchNames = false`) | "Reissue <host>'s certificate to include the correct CN / SAN entries matching the probed hostname." |
| Compliance gap (encryption in transit) | "Provide TLS posture screenshot as encryption-in-transit evidence for <framework> question <Q>." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| OCSP / CRL revocation status | partial — OCSPUrl/AIAUrl present but revocation check requires live CA query | CA-side console |
| HTTP redirect chain integrity | partial — Redirects + RedirectsTo observed; multi-hop chains require tracing | Browser dev tools / curl |
| Server-side cipher-preference enforcement | partial | Vendor console |
| Inside-firewall TLS endpoints | requires endpoint to be probe-reachable | Internal scanning tool (qualys / nessus / etc.) |
| Cert deployment vs. cert ordered | external | MSP cert-management system |
| Origin posture when WAF/CDN-fronted | partial | Direct origin probe (requires customer cooperation) |

---

## Output format

Default `markdown`. Switch to `word` / `pptx` / `xlsx` per audience.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | query=<customer> | array<environment> | ok |
| 1 | liongard_system LIST | envId=<ENV_ID> query="tls" | array<system> | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3 | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath=<path> | varies | ok per path |
| 3a | (redirect / name-match / revocation — derived) | SystemInfo.Redirects/RedirectsTo/SSLMatchNames/OCSPUrl/AIAUrl | findings | ok |
| 4 | (expiration evaluation — derived) | Intel.SSLCertDaysTillExpiration + SystemInfo.ExpiresOn | findings | ok |
| 5 | (chain / transparency — derived) | per slas | findings | ok |
| 6 | (protocol / cipher — derived) | SystemInfo.Protocols.tls1/tls1_1/tls1_2/tls1_3 | findings | ok |
| 7 | (key strength — derived) | SystemInfo.PublicKeyAlgorithm + Extensions[*] | findings | ok |
| 8 | (vulnerability check — derived) | per metric flags | findings | ok |
| 9 | (HSTS — derived) | per slas (HTTPS only) | findings | ok |
| 10 | QA pass | per `reference/qa-retry-pattern.md` | varies | ok |
| 11 | render | per `output.format` | <artifact path> | ok |
```

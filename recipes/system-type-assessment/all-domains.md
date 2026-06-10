---
name: system-type-all-domains
description: >
  Use this skill when the user wants a Domain & DNS inventory across an
  environment — domain expiration roadmap, registrar consolidation, DMARC
  health audit, email-vs-website detection, IP / ASN / hosting footprint.
  Trigger phrases: "domain inventory for <CUSTOMER>", "DNS / domain audit",
  "DMARC posture", "what domains expire soon", "registrar consolidation",
  "domain expiration roadmap". Uses the reconciled `liongard_domain` tool
  exclusively — minimal per-inspector calls required.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_domain"
personas: [vcio-account-manager, soc, technical-alignment-manager, accounting-finance]
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

# System-Type Assessment — All Domains

> Reconciled domain inventory across every domain-aware Liongard inspector.
> The `liongard_domain` tool exposes registrar, expiration, DMARC health,
> email/website detection, IPv4/IPv6, ASN — most queries are direct filters
> with no per-inspector iteration needed.
>
> **Pairs with:** `recipes/external-data/email-security.md` for the gateway
> side of the email-security story (Proofpoint / Mimecast / Vade — outside
> Liongard); `recipes/single-system-analysis/by-inspector/microsoft-365.md`
> for tenant-side verified domains (`Organization[0].verifiedDomains`);
> `recipes/single-system-analysis/by-inspector/internet-domain-dns.md` for
> the single-domain deep dive (deeper than this rollup's per-row summary);
> `recipes/system-type-assessment/all-external-attack-surface.md` for the
> full outside-in view that combines domain posture with TLS, IP
> reputation, and dark-web exposure.
>
> **References:** `reference/asset-fields.md` (`liongard_domain` field map).

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-domain-inventory-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  inventory: "Domain Inventory"
  expiration_roadmap: "Expiration Roadmap"
  dmarc_posture: "DMARC Posture"
  registrar_audit: "Registrar Distribution"
  hosting_footprint: "Hosting Infrastructure"
  unmanaged: "Unmanaged Domains"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  expiration_warn_days: 60
  expiration_critical_days: 14
  dmarc_required: true
  managed_domain_required: true       # MSP should be managing every customer domain

reporting_period: { default: "current_state" }

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

- Quarterly domain audit (vCIO conversation)
- "Are any of <CUSTOMER>'s domains expiring soon?"
- "What's the DMARC health across <CUSTOMER>'s domains?"
- Registrar consolidation candidate analysis ("can we move all the domains
  to one registrar for cost savings?")
- Pre-renewal review for invoice planning (Accounting/Finance)
- Insurance / compliance evidence on email-authentication posture

Personas: vCIO/AM (executive summary, registrar consolidation), SOC (DMARC,
email-auth), TAM (deep dive), Accounting/Finance (renewal cost).

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |

Environment-scoped — no per-system input. The recipe queries `liongard_domain`
directly with structured filters; iteration over per-inspector data is rarely
needed.

---

## Workflow

### Step 1 — Pull a baseline count and DMARC breakdown

```
liongard_domain COUNT environmentId=<ENV_ID>
```

Returns total domain count for the environment.

```
liongard_domain COUNT environmentId=<ENV_ID> dmarcHealth="valid"
liongard_domain COUNT environmentId=<ENV_ID> dmarcHealth="not-valid"
liongard_domain COUNT environmentId=<ENV_ID> dmarcHealth="not-found"
```

Three counts give the DMARC posture summary in three calls — no full record
fetch required for the executive summary.

### Step 2 — Expiration roadmap

```
# Already expired (data-hygiene flag)
liongard_domain LIST environmentId=<ENV_ID> maxDaysTillExpiration=0

# Critical — expiring within SLA's critical window
liongard_domain LIST environmentId=<ENV_ID> maxDaysTillExpiration=<critical>
                     fields=["domainName","registrar","daysTillExpiration","expirationDate"]

# Warn — expiring within SLA's warning window
liongard_domain LIST environmentId=<ENV_ID>
                     minDaysTillExpiration=<critical>
                     maxDaysTillExpiration=<warn>
                     fields=["domainName","registrar","daysTillExpiration","expirationDate"]
```

### Step 3 — DMARC posture detail

```
# Domains misconfigured (DMARC record present but failing)
liongard_domain LIST environmentId=<ENV_ID> dmarcHealth="not-valid"
                     fields=["domainName","emailDetected","ipv4Address"]

# Domains missing DMARC entirely
liongard_domain LIST environmentId=<ENV_ID> dmarcHealth="not-found"
                     emailDetected=true
                     fields=["domainName","registrar"]
# emailDetected=true narrows to domains that actually send mail —
# no-DMARC on a parked domain is lower priority than no-DMARC on a sending domain.
```

### Step 4 — Registrar consolidation analysis

```
# Pull domain + registrar with field projection
liongard_domain LIST environmentId=<ENV_ID> fields=["domainName","registrar","daysTillExpiration"]
  → group_by registrar, count

# Single-domain registrars are the consolidation candidates
candidates = registrars where count == 1
```

### Step 5 — Hosting footprint

```
liongard_domain LIST environmentId=<ENV_ID> websiteDetected=true
                     fields=["domainName","ipv4Address","asn","asName"]
  → group_by asName

# Identifies hosting providers (Cloudflare, AWS, GoDaddy, etc.) and
# flags long-tail single-host domains that may not be on the standard MSP stack.
```

### Step 6 — Managed vs. unmanaged

```
liongard_domain COUNT environmentId=<ENV_ID> managedDomain=true
liongard_domain COUNT environmentId=<ENV_ID> managedDomain=false

# List unmanaged domains for review
liongard_domain LIST environmentId=<ENV_ID> managedDomain=false
                     fields=["domainName","registrar","emailDetected","websiteDetected"]
```

### Step 7 — Email-vs-website detection mismatch

```
# Domains with email but no website (typical: legacy alias domains)
liongard_domain LIST environmentId=<ENV_ID> emailDetected=true websiteDetected=false

# Domains with website but no email (typical: marketing-only)
liongard_domain LIST environmentId=<ENV_ID> emailDetected=false websiteDetected=true

# Both detected = full domain
# Neither detected = parked / inactive
```

---

## Headline KPIs

| KPI | Source | Result shape |
|---|---|---|
| Total domains | `liongard_domain COUNT environmentId=<ENV_ID>` | `<integer>` |
| DMARC valid | `dmarcHealth="valid"` COUNT | `<integer>` |
| DMARC not-valid | `dmarcHealth="not-valid"` COUNT | `<integer>` |
| DMARC not-found | `dmarcHealth="not-found"` COUNT | `<integer>` |
| Expiring ≤ <critical> days | `maxDaysTillExpiration=<critical>` COUNT | `<integer>` |
| Already expired | `maxDaysTillExpiration=0` COUNT | `<integer>` |
| Managed domains | `managedDomain=true` COUNT | `<integer>` |
| Unmanaged domains | `managedDomain=false` COUNT | `<integer>` |
| Domains sending email | `emailDetected=true` COUNT | `<integer>` |

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Domain expiring critical | `daysTillExpiration <= slas.expiration_critical_days` | "**Critical:** <domain> expires in <N> days — renew immediately." |
| Domain expiring soon | `daysTillExpiration <= slas.expiration_warn_days` | "<N> domains expire within <warn> days — schedule renewals." |
| Already expired | `daysTillExpiration < 0` | "<N> domains lapsed — investigate or release." |
| DMARC missing on sending domain | `dmarcHealth=="not-found"` AND `emailDetected==true` | "<N> mail-sending domains have no DMARC record — publish DMARC policy." |
| DMARC misconfigured | `dmarcHealth=="not-valid"` | "<N> domains have malformed DMARC records — review and remediate." |
| Registrar fragmentation | many single-domain registrars | "<N> registrars hold one domain each — consolidate to <preferred> for ops + cost." |
| Unmanaged domains | `managedDomain==false` count > 0 | "<N> domains not flagged as managed — confirm scope or take ownership." |
| Hosting concentration risk | one ASN hosting most websites | "<pct>% of websites on <ASN> — confirm DR posture if hosting goes down." |
| Legacy alias domain | `emailDetected==true AND websiteDetected==false` | "<N> domains are mail-only — confirm still in use; decommission if not." |

---

## QA & Manual Verification

Run the QA pass per `reference/qa-retry-pattern.md` before rendering output:

1. **Retry persistent nulls.** If any `liongard_domain` LIST or COUNT call
   returns null or zero records on a per-status query (e.g.,
   `dmarcHealth="not-valid"` returns 0 when the customer has known DMARC
   issues), retry up to `qa.retry_attempts` times.

2. **Flag stale inspector data.** For every domain in the result set, check
   `lastSeen`. Flag domains where `lastSeen` is older than
   `qa.flag_inspector_lastseen_threshold_days` — the DMARC / expiration
   data may be stale. Recommend a re-inspection.

3. **Cross-tool divergence (when applicable).** If running this recipe
   alongside `microsoft-365.md`, compare M365 `verifiedDomains` against
   `liongard_domain` `domainName` for the same customer. Domains in M365
   but not in `liongard_domain` (or vice versa) are coverage gaps.

4. **Proposed-metric gaps for this recipe** — none. `liongard_domain`
   exposes the full DMARC / expiration / hosting field set this recipe
   needs.

5. **Manual Verification appendix** — render in the deliverable. Typical
   items for this recipe:
   - Domains with persistent-null DMARC after retries (re-run inspector or
     check via dig/MxToolbox).
   - Domains with `daysTillExpiration` mismatching the registrar's portal
     (registrar API lag).
   - Domains in M365 `verifiedDomains` but absent from `liongard_domain`
     (extend domain inspector coverage).

## Forward-looking renewal roadmap

Build a per-quarter renewal calendar grouped by registrar — useful for vCIO
conversations and Accounting/Finance budget planning:

```
# Domains by quarter of expiration
liongard_domain LIST environmentId=<ENV_ID>
                     fields=["domainName","registrar","expirationDate","daysTillExpiration"]
  → group_by quarter(expirationDate)
  → group_by registrar within each quarter

# Output: a calendar grid showing how many domain renewals fall in each quarter,
# per registrar. Lights up cost-spike quarters in advance.
```

---

## Data gaps & coverage notes

| Field / topic | Status | Source if missing |
|---|---|---|
| WHOIS contact data | not in inventory | Manual WHOIS or registrar export |
| SPF / DKIM detail beyond DMARC health | partial — see `internet-domain-dns-inspector` for raw DNS records | Cross-reference via `liongard_metric` if specific record content needed |
| TLS / SSL cert detail | separate inspector | `tls-ssl-inspector` (ID 16) — separate recipe |
| Web content / CMS / vulnerability scan | not in scope | External tools (Detectify, Qualys) |
| DNS change history | not in inventory | `liongard_detection` for DNS-change events |

---

## Output format

Markdown / Word / PowerPoint / Excel per `output.format`. **xlsx** is the
canonical deliverable for renewal calendars and registrar audits (sortable,
filterable). **pptx** for executive overview with the DMARC posture donut
and renewal-by-quarter chart.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_domain COUNT | envId=<ENV_ID> | { Count: <int> } | ok |
| 3 | liongard_domain COUNT | envId=<ENV_ID> dmarcHealth=valid/not-valid/not-found | { Count: <int> } | ok per call |
| 4 | liongard_domain LIST | envId=<ENV_ID> maxDaysTillExpiration=<critical> | array<domain> | ok |
| 5 | liongard_domain LIST | envId=<ENV_ID> dmarcHealth=not-valid emailDetected=true | array<domain> | ok |
| 6 | liongard_domain LIST | envId=<ENV_ID> fields=[...] | array<domain> | ok |
```

> Note how few tool calls this recipe needs vs. the older asset-based
> recipes — `liongard_domain`'s structured filters and COUNT operation push
> the heavy lifting server-side.

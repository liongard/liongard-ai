---
name: single-system-network-ip-address
description: >
  Use this skill when the user wants a single-IP external posture
  analysis — public IP reputation, blocklist (RBL / DNSBL) status,
  hosting / ASN footprint, geolocation, reverse DNS, observed open
  ports, or known-CVE exposure on services detected on that IP.
  Trigger phrases: "IP reputation for <ip>", "is <ip> on a blocklist",
  "external port scan on <ip>", "ASN / hosting for <ip>", "is <ip>
  exposing risky services", "IP reverse DNS check", "RBL status of
  <ip>". Non-credentialed — pulls from public reputation feeds, DNS,
  and observation data; suitable for prospects and pre-sales
  discovery.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric"
personas: [sales, soc, vcio-account-manager, technical-alignment-manager, noc]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  # Reconciled 2026-05-29 vs live dataprint (live production environment, inspected 2026-03-13).
  # SystemInfo exposes only Ip / ReverseLookup / AS / ASInfo / limitedOutput. The inspector
  # does NOT return blocklist/RBL, CVE, reputation-score, open-ports, or threat-intel data —
  # those refs pruned to internal/proposed-metrics-backlog.md. NOTE: the recipe description
  # over-promises external-posture data the inspector doesn't collect; trim it to ASN/DNS facts.
  - metrics:network-ip-inspector:ip-address
  - metrics:network-ip-inspector:reverse-lookup
  - metrics:network-ip-inspector:asn
  - metrics:network-ip-inspector:asn-info
  - metrics:network-ip-inspector:limited-output
---

# Single-System Analysis — Network IP Address

> **Inspector:** `network-ip-inspector` (ID 18). Network category.
> External-attack-surface family. **One system per monitored public
> IP.** Pulls from public reputation feeds, DNS, blocklist lookups,
> and observation data — **no customer credential required**.
>
> **References:** `reference/inspector-aliases.md` (Network IP, IP
> monitor). Pairs with `tls-ssl.md` (when the IP exposes TLS
> endpoints) and `internet-domain-dns.md` (the IP-to-domain mapping
> story).

> ⚠️ **Dataprint reality note.** The live Network IP inspector
> dataprint is lean. Validated fields from `GET_OVERVIEW` are:
> `SystemInfo.{ReverseLookup, Ip, AS, ASInfo, limitedOutput}`.
> When `limitedOutput = true`, the inspector was unable to gather
> full enrichment data for this IP.
>
> The blocklist, port-scan, CVE, and advanced reputation fields
> described in Steps 4–6 below are **data gaps** — they
> represent what the recipe would surface *if* those metrics exist
> in the customer's environment. Always run
> `liongard_metric LIST environmentId=<ENV_ID> systemId=<SYS_ID>`
> to confirm what is actually available before building a report.
> File missing metric requests via the `liongard-metrics` skill.

---

## Pre-Sales Discovery Value

The Network IP inspector is the **exposure-surface side of the
external posture story**. Where the Internet Domain and TLS inspectors
surface *what's reachable*, the Network IP inspector surfaces *whether
the IP is trusted by the internet*.

Common discovery findings:

- **Mail-deliverability blockers.** A prospect's outbound mail IP
  showing up on Spamhaus / Barracuda / SORBS produces measurable
  business pain (bounced customer email, lost deals). MSPs that can
  surface this proactively earn instant credibility.
- **Forgotten exposed services.** Open RDP / SMB / Telnet / FTP
  detected on a public IP is a finding the prospect's IT director
  often doesn't know about — frequently legacy services left running
  after a vendor change.
- **ASN / hosting drift.** When a prospect's "primary office IP" is
  hosted at a residential / co-lo ASN that doesn't match where they
  think their datacenter is, it indicates documentation drift — a
  finding the MSP can productize as "we keep your network topology
  documented."

Accepts a list of IPs via `customization.discovery_input.ips[]` for
pre-sales / trial-environment mode.

> **Sales narrative tip:** Reputation findings (blocklist hits) are
> the highest-impact deliverable — they map directly to revenue impact
> via mail deliverability. Lead with those in the deck.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer-or-prospect>-<ip>-network-ip-review-<date>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  ip_identification: "IP & Network Identification"
  reverse_dns: "Reverse DNS / PTR"
  hosting_asn: "Hosting / ASN"
  geolocation: "Geolocation"
  reputation: "Reputation & Blocklist Status"
  open_ports: "Open Ports & Services Detected"
  cve_exposure: "Known-CVE Exposure"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"                       # technical | balanced | executive

slas:
  prohibited_open_ports:
    - 23          # Telnet — never permitted
    - 21          # FTP — discouraged
    - 3389        # RDP — never permitted directly to internet
    - 445         # SMB — never permitted to internet
    - 1433        # MSSQL — never permitted to internet
    - 5432        # Postgres — never permitted to internet
    - 3306        # MySQL — never permitted to internet
    - 22          # SSH — only with key-based + IP allowlist; flag for review
  acceptable_open_ports:
    - 80
    - 443
    - 25          # mail
    - 465
    - 587
    - 993
    - 995
    - 53          # DNS (only on authoritative NS hosts)
  reputation_must_pass: true             # any blocklist hit = finding
  ptr_required_on_mail_ips: true         # outbound-mail IPs must have valid PTR
  ptr_matches_helo_required: true        # PTR matches HELO/EHLO banner

reporting_period:
  default: "current_state"

discovery_input:
  # Non-credentialed pre-sales mode.
  mode: "credentialed"                   # credentialed | discovery
  ips: []                                # ["203.0.113.10", "203.0.113.11"]

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

- "IP reputation for <ip>"
- "Is <ip> on a blocklist?"
- "External port scan on <ip>"
- "ASN / hosting for <ip>"
- "Is <ip> exposing risky services?"
- "IP reverse DNS check"
- "RBL / DNSBL status of <ip>"
- "Pre-sales external posture for <prospect>"
- "Why is <customer>'s mail bouncing — RBL hit?" (incident-driven)

Cadence: monthly for customer-facing IPs (reputation churn); ad-hoc
for incidents; on-demand during pre-sales.

Personas:
- **Sales** (primary in discovery mode — reputation findings power
  the proposal)
- **SOC** (incident — mail deliverability, post-compromise reputation
  triage)
- **vCIO / Account Manager** (renewal narrative — reputation
  monitoring as part of managed service)
- **TAM** (remediation — closing exposed ports, fixing PTR records)
- **NOC** (operational — mail-flow troubleshooting)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes (credentialed mode) | `liongard_environment LIST` |
| System ID (the specific IP system) | Yes — one per recipe run | `liongard_system LIST query="network-ip"` |
| IP address(es) | Yes (discovery mode) | User-provided; see `discovery_input.ips` |
| Optional: focus area | No | User prompt — e.g., "focus on mail reputation only" |

> **System-per-IP.** The `network-ip-inspector` creates one Liongard
> system per monitored IP. A customer with 4 public IPs has 4 systems
> under this inspector.

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer-or-prospect>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="network-ip"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

IP reputation churns — blocklist additions / removals happen daily.
Stale inspector data is materially more risky here than for the
domain or TLS inspectors. Flag aggressively.

### Step 3 — Identity + hosting (validated JMESPath paths)

Use `liongard_metric GENERATE_AND_EVALUATE` with the paths below.
These paths are **validated** against the live Network IP inspector dataprint.

```
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  jmesPath="<path>"

# Validated fields (confirmed from live GET_OVERVIEW):
#   SystemInfo.Ip                              (the monitored public IP address)
#   SystemInfo.ReverseLookup                   (PTR record — reverse DNS)
#   SystemInfo.AS                              (ASN number, e.g., "AS8075")
#   SystemInfo.ASInfo                          (ASN organization description)
#   SystemInfo.limitedOutput                   (boolean — true = inspector got partial data only)
```

> **`limitedOutput = true`** means the inspector could not fully enrich the IP
> (e.g., rate-limited by reputation APIs, RFC 1918 escape, or probe timeout).
> When this flag is true, supplement with external tools (Shodan, VirusTotal,
> MXToolbox) and document the gap in the Data Gaps section.

### Step 4 — Reputation + blocklist (data gaps / enrichment)

> **These metric names/JMESPath queries are proposed.** Confirm availability with
> `liongard_metric LIST` first. File missing metrics via `liongard-metrics`.

```
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  jmesPath="<path>"

# Proposed / enrichment fields (may not be present):
#   "network-ip.reputation.score"              (composite reputation 0–100)
#   "network-ip.blocklist.spamhaus"            (boolean — listed on Spamhaus)
#   "network-ip.blocklist.spamhausZbl"
#   "network-ip.blocklist.spamhausSbl"
#   "network-ip.blocklist.barracuda"
#   "network-ip.blocklist.sorbs"
#   "network-ip.blocklist.surbl"
#   "network-ip.blocklist.uceprotect"
#   "network-ip.blocklist.cbl"                 (composite blocklist)
#   "network-ip.blocklist.listingCount"        (total lists hit)
#   "network-ip.threatIntel.maliciousIndicator"
```

If reputation metrics are not available in Liongard, use external enrichment
and record the gap in the verification log.

### Step 5 — Open ports + service detection (data gaps)

> **Proposed metrics.** Confirm availability before building a port report.

```
# Proposed fields:
#   "network-ip.scan.openPorts"                (list of open TCP ports)
#   "network-ip.scan.openUdpPorts"
#   "network-ip.scan.serviceBanners"           (banner per port)
#   "network-ip.scan.tlsCapablePorts"
```

If port-scan data is unavailable in Liongard, note it in the Data Gaps section.
Complement with Shodan (`shodan.io/host/<ip>`) or Censys for pre-sales discovery.

For each detected open port, evaluate against
`slas.prohibited_open_ports` and `slas.acceptable_open_ports`.

### Step 6 — CVE exposure (data gaps)

> **Proposed metrics.** Service-banner-driven CVE matching is not confirmed
> in the current Network IP dataprint. Confirm availability first.

```
# Proposed fields:
#   "network-ip.cve.criticalCount"
#   "network-ip.cve.highCount"
#   "network-ip.cve.list"                      (CVE IDs + service banners)
```

Surface as Critical / High findings — vendor patch upgrade required.
If CVE data unavailable, note gap; use Shodan/Censys CVE annotations as
external enrichment.

### Step 7 — PTR + HELO alignment

| Signal | Outcome |
|---|---|
| `reverseDns` empty | High — mail-deliverability gap; configure PTR |
| PTR present but generic (e.g., `<isp>-residential-<ip>.com`) | Medium — appears suspicious to recipient MTAs |
| PTR doesn't match HELO/EHLO banner | High — RFC 5321 mismatch; mail trust impact |
| PTR matches HELO, but HELO doesn't match the sender domain | Medium — narrowing the trust chain |

### Step 8 — QA pass (per `reference/qa-retry-pattern.md`)

This recipe's QA pass especially focuses on:

1. **Retry persistent nulls** on reputation metrics — RBL APIs are
   rate-limited and frequently return transient errors.
2. **Flag stale inspectors** aggressively (Step 2).
3. **Cross-reference with the firewall recipe** when applicable — if
   the customer has the `all-firewalls.md` rollup output, confirm the
   firewall's WAN IP matches one of the monitored IPs in this
   recipe's scope. Mismatch = orphaned IP monitoring.
4. **Proposed-metric gaps** surface in the verification log.
5. **Geolocation false positives** — IP geolocation has known accuracy
   issues; treat country / city findings as informational unless
   confirmed via routing data.

### Step 9 — Render output

| Output mode | Best for |
|---|---|
| `markdown` | Working draft / IT-director audience |
| `word` | Customer-facing letter / incident-response evidence |
| `pptx` | Slide-per-IP for the pre-sales / QBR deck |
| `xlsx` | Multi-IP rollup (cross-system) |

---

## QA & Manual Verification

Per `reference/qa-retry-pattern.md`. Manual checks specific to this
recipe:

- **Multi-feed reputation confirmation** — single blocklist hits can
  be transient or feed-specific. Confirm against 2+ feeds before
  declaring a reputation finding.
- **Cloud-provider IP attribution** — when the IP belongs to a major
  cloud provider (AWS / Azure / GCP), confirm the customer's
  responsibility for that IP (vs. a co-tenant on shared infrastructure).
- **NAT / shared-IP scenarios** — small businesses behind ISP-NAT may
  share IPs with others; reputation findings may belong to a different
  tenant.
- **Port-scan completeness** — Liongard's port scan is targeted, not
  exhaustive. For full external-port discovery, complement with a
  dedicated scanner (nmap from outside, Shodan / Censys).

---

## Insights & recommendations — generation patterns

| Pattern | Recommendation template |
|---|---|
| Critical blocklist hit (Spamhaus / Barracuda) | "URGENT: <ip> is on <blocklist>. Mail deliverability impacted. Investigate possible compromise; submit delisting request after remediation." |
| Multi-list reputation hit | "<ip> is on <N> reputation lists. Investigate root cause (compromised host / poorly-configured mail / shared-IP residue)." |
| Single-list reputation hit | "<ip> appears on <blocklist>. Confirm root cause; submit delisting request if clean." |
| PTR missing on mail IP | "Configure PTR record for <ip> matching the sender domain (e.g., `mail.<domain>`). Coordinate with ISP." |
| PTR doesn't match HELO | "Align <ip>'s PTR with the mail server's HELO/EHLO banner." |
| Prohibited port open (RDP/SMB/Telnet/etc.) | "URGENT: Close port <port> on <ip>. Restrict to VPN-only access if legitimate use case." |
| Database port open (MySQL/Postgres/MSSQL) | "URGENT: Close database port <port> on <ip>. Database servers must not be directly internet-exposed." |
| SSH open without context | "Confirm SSH on <ip> uses key-based auth + IP allowlist. Disable if not required." |
| Critical / High CVE on detected service | "<ip> exposes <service-banner> matching <CVE-ID>. Patch / upgrade required." |
| Country mismatch (geolocation vs. expected) | "<ip> geolocates to <country>; customer expects <country>. Confirm hosting / routing." |
| Hosting provider mismatch | "<ip> hosted at <provider>; customer documentation says <provider>. Confirm topology." |
| Threat-intel indicator | "<ip> appears on threat-intel feed <feed>. Investigate scope and remediate." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Exhaustive port scan | partial — targeted scan only | Shodan / Censys / nmap from outside |
| Full CVE-to-service mapping | partial — banner-derived | Vulnerability scanner (Nessus / Qualys) |
| IPv6-only services | partial | Dedicated IPv6 scanner |
| Internal (RFC 1918) IPs | not in scope — this inspector is public-IP-only | Internal scanning tool |
| Blocklist delisting status | external | Per-blocklist delisting form |
| Outbound-traffic anomaly detection | external | NetFlow / mail-flow analytics |

---

## Output format

Default `markdown`. Switch per audience.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | query=<customer> | array<environment> | ok |
| 1 | liongard_system LIST | envId=<ENV_ID> query="network-ip" | array<system> | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3 | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath="SystemInfo.{Ip,ReverseLookup,AS,ASInfo,limitedOutput}" | object | VALIDATED |
| 4 | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath=<reputation-path> | varies | SCHEMA_CONFIRMED — not found in live dataprint; confirm against production system |
| 5 | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath=<scan-path> | list | SCHEMA_CONFIRMED — not found in live dataprint; confirm against production system |
| 6 | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath=<cve-path> | list | SCHEMA_CONFIRMED — not found in live dataprint; confirm against production system |
| 7 | (PTR / HELO — derived) | per slas | findings | ok |
| 8 | QA pass | per `reference/qa-retry-pattern.md` | varies | ok |
| 9 | render | per `output.format` | <artifact path> | ok |
```

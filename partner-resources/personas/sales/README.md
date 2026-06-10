# Sales — Persona Index

Sales runs **pre-sales discovery** (sizing a prospect's environment for a
proposal) and **renewal discussions** (turning the technical assessment
into a renewal / upsell narrative). The sales role's primary deliverable
is a credibility-building snapshot: "we know your environment; here's
what we'd manage; here's what we recommend".

## Audience framing

- **Tone:** balanced for working sessions with the customer's technical
  buyer; executive for the leadership / decision-maker conversation.
- **Format:** PowerPoint for the proposal / pitch deck; Word for the
  scope-of-work attachment; Excel for the technical-inventory annex.
- **Default cadence:** triggered by sales engagements — discovery,
  proposal, renewal. Not periodic.

## SLA emphasis (Sales defaults)

| SLA | Default | Why Sales cares |
|---|---|---|
| `inspector_lastseen_days_max` | 1 day | Sales presentations on stale data are weak |
| Coverage % thresholds | Highlight gaps | A gap is the upsell hook |
| Vendor count thresholds | Highlight sprawl | Consolidation is a common sales narrative |
| `warranty_warn_days` | 180 days | Refresh roadmap = new hardware revenue |

## Common scenarios → recipes

### Phase 0 — Zero-credential external attack surface (the flagship sales motion)

**Run this BEFORE any credentialed inspector.** These four inspectors
require only public identifiers (domain names, public IPs) from the
prospect — no password, no agent install. The combined rollup is the
single highest-leverage pre-sales deliverable in the library.

| Section | Recipe |
|---|---|
| **Outside-in posture (the complete external story)** | `recipes/system-type-assessment/all-external-attack-surface.md` |
| Domain & mail trust (DMARC / SPF / DKIM / WHOIS / expiration) | `recipes/single-system-analysis/by-inspector/internet-domain-dns.md` |
| Encryption-in-transit (TLS certs, protocols, ciphers, vulnerabilities) | `recipes/single-system-analysis/by-inspector/tls-ssl.md` |
| Public-IP reputation, blocklist hits, exposed services | `recipes/single-system-analysis/by-inspector/network-ip-address.md` |
| Credential exposure (dark-web / breach corpus) | `recipes/single-system-analysis/by-inspector/dark-web-monitoring.md` |

> **Why this leads.** Phase 0 produces real findings the prospect can
> verify themselves before agreeing to credentialed inspection. By
> the time the prospect grants credentialed access, the MSP has
> already established outside-in credibility — turning the proposal
> from cold-pitch to addressing-acknowledged-risks.

### Pre-sales discovery (credentialed phase)
The MSP just got a prospect's environment connected to Liongard. Now
Sales (often with TAM or a sales engineer) builds the "this is what
we're seeing" deck.

| Section | Recipe |
|---|---|
| Master discovery deliverable | `recipes/sales-assessment/pre-sales-discovery.md` |
| Environment composition (servers, workstations, mobile) | `recipes/system-type-assessment/all-endpoints.md` |
| Security tooling inventory + gaps (EDR, firewall) | `all-edrs.md`, `all-firewalls.md` |
| Backup coverage assessment | `all-backups.md` |
| Identity tooling + MFA coverage | `microsoft-365.md` + `active-directory.md` |
| Lifecycle risks (Win10 EOL, EOL servers, expiring licenses) | `all-endpoints.md` (Win11 readiness) + `all-servers.md` (lifecycle) + `all-firewalls.md` (license roadmap) + `all-domains.md` (expirations) |
| Phishing / SAT posture | `knowbe4.md` if deployed |

### Renewal discussions

| Scenario | Recipe |
|---|---|
| "Renewal proposal — what's changed in the customer's environment since last year?" | Same recipes as above, with time-series sections enabled to show growth / improvement |
| "Customer wants to renegotiate price — what's the actual scope?" | `all-endpoints.md` (device count) + `microsoft-365.md` (user count) + per-vendor recipes for any tooling in scope |
| "We want to upsell EDR / backup / cyber-insurance prep" | `all-edrs.md` / `all-backups.md` / `cyber-insurance/cyber-insurance-readiness.md` (use the coverage-gap output as the sales hook) |

### Sales-assessment deliverable

| Section | Recipe |
|---|---|
| Full sales-assessment template | `recipes/sales-assessment/pre-sales-discovery.md` |
| Zero-credential discovery starter | `recipes/system-type-assessment/all-external-attack-surface.md` |

## Read across to other personas

- **vCIO / Account Manager** — Sales hands off won deals to vCIO for
  ongoing relationship; renewal preparation often returns to Sales.
- **TAM** — TAM produces the technical-fidelity assessment; Sales
  translates it into commercial narrative.
- **Executive** — when Sales is presenting to customer leadership, the
  Executive persona's framing applies to the deck.

## Sales narrative templates

Each system-type recipe naturally surfaces a coverage-gap finding that
becomes a sales hook. Common templates:

- **EDR upsell** — "Your current EDR sees <N> of <Total> servers
  (<pct>%). The gap is <list>. We recommend deploying <vendor> on the
  uncovered <N> to close that ransomware-exposure window."
- **Backup upsell** — "Your current backup posture protects <N> of
  <Total> servers (<pct>%). The unprotected <N> are <hostname list>.
  Our recommendation includes <vendor> for cloud-tier protection."
- **Cyber-insurance prep** — "Your environment meets <pct>% of the
  cyber-insurance carrier's questionnaire today. The gap is <N> control
  items (<list>). Our engagement closes the gap by <date>."
- **Vendor consolidation** — "You run <N> firewall vendors / <N> backup
  vendors / <N> EDR vendors today. Each adds operational overhead;
  consolidating to <recommended vendor> reduces complexity and license
  spend."

## What to customize first

1. **MSP brand on the pitch deck** — `output.brand.company_name` and
   `output.brand.primary_color` in each recipe's customization block.
2. **Sales-specific output preferences** — most recipes produce
   markdown / xlsx by default. For Sales, override to `pptx` in the
   customization block for the headline deliverables.
3. **Upsell narratives per practice** — fork the templates above for
   the products your MSP actually sells.
4. **Pre-sales discovery checklist** — assemble a sales-specific
   `recipes/sales-assessment/<your-template>.md` that chains the right
   recipes for your proposal template.

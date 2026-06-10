# vCIO / Account Manager — Persona Index

The vCIO (virtual Chief Information Officer) and the Account Manager
own the **customer relationship**. Their reports translate operational
state and security posture into business conversations — refresh
roadmaps, renewal calendars, vendor consolidation candidates, executive
summaries, and quarterly business reviews (QBR / PBR). They lead with
outcomes, not raw counts.

## Audience framing

- **Tone:** balanced for working sessions; executive for slide decks
  going to customer leadership. Frame in risk + business outcomes
  ("reduce account takeover risk", "consolidate vendor spend by 30%",
  "two firewalls reach EOL in Q3 — refresh roadmap required").
- **Format:** PowerPoint for executive deliverables; Word for written
  reports; Excel for the renewal-calendar / asset-inventory backup
  workbooks; Markdown for working notes.
- **Default cadence:** quarterly business reviews; monthly internal
  reviews; on-demand for renewal cycles, customer escalations, RFPs.

## SLA emphasis (vCIO / AM defaults)

| SLA | Default | Why vCIO cares |
|---|---|---|
| `license_expiration_warn_days` | 60 days | Renewal-calendar lead time; avoid surprises |
| `warranty_warn_days` | 90–180 days | Hardware refresh roadmap planning |
| `inspector_lastseen_days_max` | 7 days | Reports built on stale data lose credibility |
| `unprotected_servers_max` | 0 | A customer with unprotected servers needs a conversation |
| Vendor count thresholds | ≥3 distinct firewall / backup / EDR vendors | Consolidation candidate |

## Common scenarios → recipes

### Quarterly Business Review (QBR / PBR)
Recommended PBR sequence — run in order to build a complete picture:

| Step | Recipe | What it produces |
|---|---|---|
| 1 | `recipes/system-type-assessment/all-endpoints.md` | Fleet composition KPIs |
| 2 | `recipes/system-type-assessment/all-edrs.md` | EDR fleet posture |
| 3 | `recipes/system-type-assessment/all-firewalls.md` | Firewall fleet + license-renewal roadmap |
| 4 | `recipes/system-type-assessment/all-backups.md` | Backup coverage + per-vendor distribution |
| 5 | `recipes/system-type-assessment/all-servers.md` | Server-class deep dive + EOL roadmap |
| 6 | `recipes/system-type-assessment/all-hypervisors.md` | Virtualization stack |
| 7 | `recipes/system-type-assessment/all-domains.md` | Domain renewals + DMARC posture |
| 8 | `recipes/single-system-analysis/by-inspector/microsoft-365.md` | M365 license utilization |
| 9 | `recipes/single-system-analysis/by-inspector/knowbe4.md` | Phishing / SAT progress |

### Other vCIO scenarios

| Scenario | Recipe |
|---|---|
| "License renewal roadmap for the customer (next 90 days)" | `all-firewalls.md` (license expiration roadmap section) + `all-domains.md` + `microsoft-365.md` |
| "Hardware refresh roadmap (Win10 EOL, out-of-warranty servers)" | `all-endpoints.md` (Win11 readiness) + `all-servers.md` (lifecycle section) |
| "Vendor consolidation candidate analysis (firewalls, backups, EDRs)" | The 3 corresponding `all-*.md` rollups |
| "Cyber-insurance evidence pack for the upcoming renewal" | `recipes/compliance/cyber-insurance/cyber-insurance-readiness.md` |
| "Customer wants to standardize on one EDR vendor — which to keep?" | `all-edrs.md` (per-vendor coverage matrix + posture) |
| "Pre-renewal SonicWall / FortiGate license check for the customer" | Corresponding per-vendor recipe |
| "Capacity / refresh recommendation for the hypervisor stack" | `all-hypervisors.md` |
| "Account growth — license-utilization trend across all licensed products" | `microsoft-365.md` (licensing) + `single-system-analysis/by-inspector/<each backup vendor>.md` |
| "Onboarding intake for a new customer (scope engagement + first-90-day plan)" | `recipes/onboarding-assessment/new-customer-onboarding.md` |

## Executive deliverable conventions

- **Lead with the KPI dashboard slide** — coverage %, unprotected count, license-expiration count, top risks.
- **Page 2 / Slide 2 — recommended actions**, prioritized. Customers want a list of decisions to make, not a list of data points.
- **Detail in appendix** — analysts ask for it, executives skip past it.
- **Cost language matters** — frame in renewal dollars + budget cycles
  when possible. The recipes' license-expiration roadmap output is
  meant to land in a fiscal-quarter view.

## Read across to other personas

- **SOC** — when a security finding needs customer-side investment,
  vCIO carries the conversation; SOC provides the supporting detail.
- **NOC** — when operational issues warrant a vCIO-level conversation
  (capacity, vendor switch, refresh).
- **TAM** — when configuration standards need updating across the
  customer base based on a vCIO commitment.
- **Sales** — when a renewal discussion expands to an upsell / refresh
  opportunity.
- **Accounting / Finance** — share the renewal calendar; they own the
  budgeting side.

## What to customize first

1. **Quarterly cadence + slide template** — your MSP brand template
   should be set in the `output.brand` block of every recipe.
2. **Renewal-calendar threshold** — `license_expiration_warn_days`
   should match your typical procurement lead time (often 90+ days for
   enterprise customers).
3. **Vendor consolidation threshold** — `≥3 vendors` is the default
   trigger for the consolidation conversation; tune per customer.
4. **Executive summary tone** — `audience.tone: "executive"` in each
   recipe's customization block drops JMESPath / metric IDs from the
   body to the appendix.

# Accounting / Finance — Persona Index

The Accounting / Finance role at an MSP cares about **renewal cycles,
license-seat utilization, cost recovery, and budget planning**. Recipes
for this persona convert the recipe library's license / warranty /
expiration data into renewal calendars and cost-impact reports.

## Audience framing

- **Tone:** balanced. Finance teams want numbers, dates, and dollar
  context. Avoid technical detail; favor monetary impact framing.
- **Format:** **Excel** is the default — sortable, filterable
  expiration grids that integrate with the MSP's accounting / PSA
  tooling. Word for written budget memos.
- **Default cadence:** monthly during budget cycles; quarterly during
  fiscal-year planning; on-demand for true-up / right-sizing events.

## SLA emphasis (Accounting / Finance defaults)

| SLA | Default | Why Finance cares |
|---|---|---|
| `license_expiration_warn_days` | 60–90 days | Procurement lead time; PO cycles |
| `warranty_warn_days` | 180 days | Capital refresh budget cycles |
| Per-seat utilization thresholds | 80–95% | True-up trigger |
| Unused / orphaned license thresholds | 0 expected | Cost-recovery opportunity |

## Common scenarios → recipes

### Renewal calendars

| Scenario | Recipe |
|---|---|
| "Firewall license renewals by quarter (per-vendor breakdown)" | `recipes/system-type-assessment/all-firewalls.md` (license expiration roadmap section) |
| "Domain renewals (90-day window, by registrar)" | `recipes/system-type-assessment/all-domains.md` (expiration roadmap section) |
| "M365 license renewals + per-SKU utilization" | `recipes/single-system-analysis/by-inspector/microsoft-365.md` (licensing section) |
| "EDR vendor renewals (SentinelOne / Sophos / Bitdefender / etc.)" | Corresponding per-vendor recipe (licensing section) |
| "Backup vendor renewals (Cove / Datto / Acronis / etc.)" | Corresponding per-vendor recipe |
| "TLS / SSL certificate expirations" | `recipes/single-system-analysis/by-inspector/tls-ssl.md` (single-host) or `recipes/system-type-assessment/all-external-attack-surface.md` (whole environment) |
| "PSA contract / agreement renewal calendar" | `recipes/system-type-assessment/all-psa-platforms.md` (contract calendar) or per-PSA single |
| "RMM license renewals + utilization" | `recipes/system-type-assessment/all-rmm-platforms.md` (license rollup) or per-RMM single |
| "Cloud-storage license renewals + utilization (Box/Dropbox/Google/M365)" | `recipes/system-type-assessment/all-cloud-storage.md` (license rollup) |

### Cost-recovery / right-sizing

| Scenario | Recipe |
|---|---|
| "M365 licenses assigned to disabled users (cost leak)" | `microsoft-365.md` (`Identities where Enabled == false AND EmailLicenses != null`) |
| "Orphaned backup-vendor protected devices (decommissioned but still paying)" | `all-backups.md` (orphaned-protection findings) |
| "ESET seat consumption — over-licensed?" | `recipes/single-system-analysis/by-inspector/eset-licensing.md` |
| "EDR vendor sprawl — pay for SentinelOne *and* Sophos *and* Bitdefender?" | `all-edrs.md` (vendor distribution + overlap audit) |
| "Hardware refresh budget — out-of-warranty + Win10-EOL count by quarter" | `all-endpoints.md` + `all-servers.md` (lifecycle sections) |

### Budget planning

| Scenario | Recipe |
|---|---|
| "Annual renewal forecast across all customer products" | Chain `all-firewalls.md` + `all-domains.md` + `microsoft-365.md` + per-vendor recipes; consolidate the renewal-by-quarter outputs |
| "Hardware refresh forecast across all customers" | `all-endpoints.md` + `all-servers.md` |
| "License utilization trend (are we growing into / out of seats?)" | Per-vendor recipes' time-series sections |
| "Per-customer Liongard billing — billable identities + devices" | `liongard_identity COUNT liongardBillable=true environmentId=<ENV_ID>` + `liongard_device COUNT managedDevice=true environmentId=<ENV_ID>` per the `reference/asset-fields.md` patterns |

## Read across to other personas

- **vCIO / Account Manager** — vCIO owns the customer conversation; the
  renewal-calendar output from this persona feeds vCIO's quarterly
  business review.
- **Sales** — Sales uses the same renewal-calendar data to time upsell
  conversations.
- **NOC** — NOC surfaces operational issues that have a cost angle (e.g.,
  failing licenses → renewal urgency).
- **Executive** — Executive deck pulls the renewal-roadmap chart from
  the same data.

## What to customize first

1. **Fiscal-year start month** — set `reporting_period.fiscal_year_start_month`
   in each recipe's customization block to your customer's fiscal
   calendar (default = January).
2. **Procurement lead time** — `license_expiration_warn_days` should
   match your typical PO turnaround. 60 days is the default; enterprise
   customers often need 90+.
3. **Cost-per-seat / cost-per-license** — recipes don't carry vendor
   pricing (intentionally; pricing is MSP-specific). Add a lookup table
   in your local fork that joins per-vendor license counts to your
   contract pricing.
4. **Excel template** — most recipes default to markdown / pptx.
   Override to `xlsx` in the customization block for the finance
   workflow. The renewal-calendar grid is the canonical output.

## A note on the cross-cutting "renewal calendar" deliverable

The library doesn't yet have a single `recipes/finance/renewal-calendar.md`
that consolidates renewals across firewalls + domains + M365 + per-vendor
licenses into one customer-facing calendar. That's a candidate
finance-specific recipe to build when MSP-finance use cases drive it
forward. Today, finance teams chain the per-recipe renewal sections
together; a consolidating recipe would simplify that workflow.

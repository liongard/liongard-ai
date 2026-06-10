# Personas — Liongard Prompt Library

Personas are **lenses** on the recipe library. Each persona is a role within
an MSP — NOC, SOC, vCIO / Account Manager, Technical Alignment Manager,
Sales, Executive, Accounting / Finance — and the index in each persona
folder maps the recipes that role uses with role-specific framing notes
(audience tone, expected cadence, SLA emphasis).

Recipes themselves live in `recipes/` and are organized by purpose
(single-system, system-type, domain, compliance, environment-lookback,
roadmap, sales, onboarding, external-data). The persona indexes do **not**
duplicate recipes — they reference them. A single recipe can serve
multiple personas, with each persona's index framing the recipe through
its own lens.

## The 7 personas

| Persona | Primary focus | Typical cadence |
|---|---|---|
| [NOC](./noc/README.md) | Operational state — agent health, capacity, failed jobs, stale inspectors | Daily / weekly health checks |
| [SOC](./soc/README.md) | Security posture — privileged access, MFA, EDR coverage, threats, exposure | Weekly / monthly + on-demand for incidents |
| [vCIO / Account Manager](./vcio-account-manager/README.md) | Customer relationship — executive summaries, license renewals, refresh roadmaps, vendor consolidation | Quarterly business reviews (QBR / PBR) |
| [Technical Alignment Manager](./technical-alignment-manager/README.md) | Standards alignment — onboarding QA, configuration audits, lifecycle planning | Onboarding + quarterly drift checks |
| [Sales](./sales/README.md) | Pre-sales discovery + opportunity sizing | Pre-sales engagements + renewals |
| [Executive](./executive/README.md) | High-level summary for the customer's leadership | Quarterly + on-demand |
| [Accounting / Finance](./accounting-finance/README.md) | License / warranty expiration, vendor cost, renewal calendars | Monthly + quarterly budget cycles |

## How to use the persona indexes

1. **Identify the persona.** Whose perspective is this report for?
2. **Open the persona's `README.md`.** It lists the recipes that role
   commonly invokes, with a one-line "what this gives me" hook per recipe.
3. **Each persona's README also includes:**
   - **Audience framing** — tone (technical / balanced / executive),
     vocabulary preferences, deliverable format defaults.
   - **SLA emphasis** — which SLA thresholds matter most for this role
     (e.g., NOC cares about `inspector_lastseen_days_max`; Finance cares
     about `license_expiration_warn_days`).
   - **Common scenarios** — typical real-world asks ("we need a
     post-incident summary", "the customer wants a renewal calendar")
     mapped to the right recipe.

## Customizing per-MSP

Persona indexes are deliberately generic. To tune for your MSP:

1. Fork or copy the persona's `README.md`.
2. Re-rank recipes by your team's actual cadence (move the most-used
   recipes to the top).
3. Add MSP-specific recipes — onboarding playbooks, custom roll-ups,
   internal-tool integrations — alongside the library recipes.
4. Adjust the SLA emphasis to match your contracts.

The library's recipes are the building blocks; the persona indexes are
your starting point for assembling them into role-specific workflows.

## A note on role overlap

These personas exist on a spectrum, and any given MSP organization will
have its own mapping. Common consolidations:
- **NOC + SOC** at smaller MSPs run together; the combined role uses
  both indexes.
- **vCIO + Account Manager** are sometimes one role, sometimes two.
- **Technical Alignment Manager** doesn't exist at every MSP — its
  recipes often consolidate under NOC, vCIO, or a dedicated standards
  team.
- **Sales** at smaller MSPs may overlap with vCIO / Account Manager.

Read across the indexes when your role spans multiple buckets.

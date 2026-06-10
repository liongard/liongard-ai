# External Data — Service Desk Tickets (PSA)

> **Status:** Liongard does not inspect ticketing/PSA systems for ticket volume
> data. While Liongard has inspectors for several PSAs as systems
> (`connectwise-manage-inspector`, `autotask-inspector`, `halopsa-inspector`,
> `kaseya-bms-inspector`, `syncro-inspector`), those expose configuration and
> integration metadata — not period-by-period ticket volume.

---

## What the deliverable typically needs

Two slides / sections are common:

### Monthly view
- **Opened vs. closed per month** — bar chart for the reporting period
- **Period totals** — `<integer>` opened, `<integer>` closed, `<integer>` still open
- **Reporting period** — typically the most recent quarter

### Annual view
- **Opened vs. closed per quarter** — bar chart Q1–Q4
- **Annual totals** — same shape as monthly
- **Period** — full calendar/fiscal year

### Key metrics
- Tickets opened vs. closed per period
- Still-open ticket count (backlog)
- **Tickets per user per month** — benchmark for "managed device load"
  (commonly ~1–1.5 tickets/user/month for a healthy engagement)

---


```yaml
customize:
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed
```
## Where to source

| Source | What it provides |
|---|---|
| **ConnectWise Manage API** | `/service/tickets` endpoint with date filters for opened/closed status |
| **Datto/Autotask PSA API** | Ticket query with status + date-range filters |
| **HaloPSA API** | Ticket reporting endpoint |
| **Syncro API** | Tickets endpoint |
| **Kaseya BMS API** | Service tickets endpoint |
| **PSA dashboard export** | CSV export from the reporting view |

---

## Liongard complementary data

While ticket volume isn't in Liongard, related Liongard data strengthens the
analysis:

| Liongard signal | What it adds |
|---|---|
| `microsoft-365-inspector` → `length(Users[?accountEnabled == \`true\`])` | Active user count — denominator for **tickets/user/month** ratio |
| Asset inventory `Identities where Enabled == true` | Same denominator, cross-inspector |
| Asset inventory `Devices where category == "compute"` | Managed device count — alternative denominator for "tickets/device" if user-based isn't right |
| `connectwise-automate-inspector` `Tickets` (when integration is configured) | May contain ticket reference IDs — varies by integration |
| `connectwise-automate-inspector` `Clients` | Client/company list for scoping |
| Identity / device growth time-series | Context for ticket volume trends — was a spike caused by user growth? |

---

## Computed metrics

| Metric | Computation |
|---|---|
| **Tickets per user per month** | `tickets_opened / active_users / months_in_period` |
| **Close rate** | `tickets_closed / tickets_opened * 100` |
| **Backlog** | `tickets_still_open_at_period_end` |
| **Period-over-period delta** | `(this_period − last_period) / last_period * 100` |

---

## Insights to surface (templates)

- "Expected ticket volume for an organization of <N> users is approximately
  <N × 1.0> to <N × 1.5> tickets/month."
- "Q<n> ticket volume of <integer> averages <pct> tickets/user/month — within / below /
  above the typical range."
- "Self-service password reset (e.g., M365 SSPR) could reduce the <pct>% of tickets
  that are password-related — recommend enabling Conditional Access SSPR if not
  already in place."
- "Backlog of <integer> open tickets carries over into next period — review aging
  and prioritize."

---

## How a recipe should consume this file

Recipes (typically quarterly lookbacks or onboarding QA) should:

1. Reference this file in the deliverable's appendix.
2. Prompt the user for the PSA export, API endpoint, or pasted CSV.
3. Pull the user count from M365 (or asset inventory) for the per-user ratio.
4. Surface in **Data Gaps** if no PSA data is provided.

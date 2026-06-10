# External Data — Client Surveys (NPS / CSAT)

> **Status:** Net Promoter Score and CSAT survey data are not inspected by
> Liongard. They are typically collected via PSA integrations (ConnectWise
> Manage CSAT, Autotask survey), dedicated MSP survey tools (SmileBack,
> Simplesat, Crewhu), or post-ticket survey workflows.

---

## What the deliverable typically needs

Two slides / sections are common:

### Quarterly view
- **Responses + average NPS per month** — bar chart for the period
- **Period summary** — `<integer>` total responses, breakdown into:
  - Promoters (score 9–10): `<integer>`
  - Passives (score 7–8): `<integer>`
  - Detractors (score 0–6): `<integer>`
- **Response rate** — `<pct>` (responses / opportunities)

### Annual view
- **Responses + average NPS per quarter** — bar chart Q1–Q4
- **Annual summary** — same shape as quarterly, full year

### Key metrics
- Total responses per period
- Promoter / Passive / Detractor breakdown
- **NPS score** = `(% Promoters) − (% Detractors)`
- Response rate = `responses / tickets_closed * 100`
- Average raw score per period

---


```yaml
customize:
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed
```
## Where to source

| Source | What it provides |
|---|---|
| **PSA built-in surveys** (ConnectWise Manage, Autotask) | Survey results tied to closed tickets — typical baseline |
| **SmileBack API** | Smiley-based CSAT, NPS module |
| **Simplesat API** | NPS, CSAT, CES with per-response detail |
| **Crewhu API** | CSAT + gamification metadata |
| **Manual export** | CSV export from the survey tool dashboard |

---

## Liongard complementary data

NPS data has no direct Liongard signal, but Liongard contributes denominators:

| Liongard signal | What it adds |
|---|---|
| `microsoft-365-inspector` → `length(Users[?accountEnabled == \`true\`])` | Active user count — denominator for "% of users surveyed" |
| Asset inventory `Identities where Enabled == true` | Same denominator, cross-inspector |
| Service-desk ticket count (via `external-data/service-desk-tickets.md`) | Denominator for **response rate** = `responses / tickets_closed` |

---

## Computed metrics

| Metric | Computation |
|---|---|
| **NPS Score** | `(promoters / total * 100) − (detractors / total * 100)` |
| **Response Rate** | `responses / tickets_closed * 100` |
| **Average Score** | mean of all individual scores |
| **Period-over-period delta** | `(this_period_NPS − last_period_NPS)` |

---

## Insights to surface (templates)

- "NPS of <integer> for the period — `<integer>` Promoters, `<integer>` Passives,
  `<integer>` Detractors out of `<integer>` responses."
- "Response rate of `<pct>` — recommend aiming for ≥30% to improve statistical
  signal."
- "<integer> Detractors flagged the same theme: review feedback for action."
- "Encourage users to complete NPS on each ticket close — automate via PSA
  workflow if not already enabled."

---

## How a recipe should consume this file

Recipes (typically the quarterly lookback) should:

1. Reference this file.
2. Prompt the user for the survey-tool export or API endpoint.
3. Pull active user / closed-ticket counts from Liongard (M365 + service-desk
   external file) for response-rate computation.
4. Surface in **Data Gaps** if no survey data is provided.

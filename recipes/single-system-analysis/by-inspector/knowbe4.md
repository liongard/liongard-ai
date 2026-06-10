---
name: single-system-knowbe4
description: >
  Use this skill when the user wants a single-system analysis of a KnowBe4 account
  — Periodic Business Review (PBR), phishing test review, security awareness
  training (SAT) completion audit, organization risk score trend, or top
  phish-prone-user identification. Trigger phrases: "KnowBe4 PBR", "KB4 report",
  "phishing security tests review", "training completion check", "pull KnowBe4
  data for <CUSTOMER>". Produces an artifact in the format set in the customization
  block.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_asset"
personas: [vcio-account-manager, soc, technical-alignment-manager]
output_formats: [markdown, word, pptx]
primitives: []
---

# Single-System Analysis — KnowBe4

> **Inspector:** `knowbe4-inspector` (ID 81). Cloud category. Security Awareness
> Training. **No parent/child** — one system per KnowBe4 account.
>
> **References:** `reference/inspector-aliases.md` (KB4, KnowBe4 SAT).
> `reference/asset-fields.md` for cross-checks against the M365 user roster.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-knowbe4-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  risk_score: "Organization Risk Score"
  phishing: "Phishing Security Tests"
  top_clickers: "Top Phish-Prone Users"
  training: "Security Awareness Training"
  campaigns: "Campaign Status"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"

slas:
  training_completion_pct_min: 95
  phish_prone_pct_max: 10        # flag if higher
  past_due_max: 0
  subscription_warn_days: 60     # subscription_end_date < N days = flag

reporting_period:
  default: "last_quarter"
```

---

## When to use

- "Pull the KnowBe4 / KB4 data for <customer>" (PBR)
- "What's the phishing test result for <customer>?"
- "Who are the top phish-prone users?"
- "What's the training completion rate?"
- "Is the subscription expiring soon?"

Cadence: monthly health check (training & phishing trends), quarterly PBR.
Personas: SOC (clicker risk), vCIO/AM (executive summary), TAM.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| KnowBe4 system ID | Yes | `liongard_system LIST query="knowbe4"` (single system) |
| Reporting period | No | Default per customization |

---

## Locating the right system

```
liongard_system LIST searchMode=keyword query="knowbe4" environmentId=<ENV_ID>
```

Single system per environment. `AccountInfo.name` returns the org name (a
`<string>`).

---

## Liongard data sources

> **Asset Inventory First, Metric Cross-Check.** KnowBe4 is the source of truth
> for *phishing-test results, training enrollment, and the org risk score*. The
> asset inventory (Identity records) is the cross-check for *who should be in
> KnowBe4* — every active user with an M365/M365-Entra license should also appear
> as a KnowBe4 user. Identities marked enabled but missing from KnowBe4 = training
> gap.

### Per-vendor data — KnowBe4 fields

| Key | Description |
|---|---|
| `AccountInfo` | Organization metadata: `name`, `type`, `domains`, `number_of_seats`, `current_risk_score`, `risk_score_history`, `subscription_level`, `subscription_end_date`, `admins` |
| `PhishingTests` | Array of phishing security tests with aggregate results + per-recipient detail |
| `Campaigns` | Array of phishing campaigns with frequency, status, and last phish-prone % |
| `TrainingEnrollments` | Array of training enrollment records (per user per module) |
| `TrainingPolicies` | Training policy definitions |
| `TrainingStorePurchases` | Purchased training content |
| `Users` | Array of KnowBe4 user accounts |
| `Groups` | User group definitions |

#### `AccountInfo` fields

| Field | Description |
|---|---|
| `name` | Organization name |
| `type` | Account type (paid / trial) |
| `domains` | Registered email domains |
| `number_of_seats` | Licensed user seats |
| `current_risk_score` | Current organization risk score (0–100) |
| `risk_score_history` | Daily history: `[{date, risk_score}, ...]` |
| `subscription_level` | Plan tier (Diamond, Platinum, etc.) |
| `subscription_end_date` | Expiration date |
| `admins` | Array of admin users |

#### Phishing test fields

| Field | Description |
|---|---|
| `name`, `pst_id`, `status`, `started_at`, `campaign_id` | Test identification |
| `delivered_count`, `opened_count`, `clicked_count`, `replied_count`, `reported_count` | Aggregate counts |
| `data_entered_count`, `macro_enabled_count`, `attachment_open_count` | Action counts |
| `phish_prone_percentage` | Phish-prone % for this test |
| `RecipientResults` | Per-user results: `user`, `delivered_at`, `opened_at`, `clicked_at`, `replied_at`, `reported_at`, `data_entered_at`, `macro_enabled_at`, `attachment_opened_at`, `template` |

#### `TrainingEnrollment` fields

| Field | Description |
|---|---|
| `user` | User object (id, email, name) |
| `module_name` | Training module name |
| `campaign_name` | Training campaign name |
| `enrollment_date`, `start_date`, `completion_date` | Lifecycle dates |
| `status` | `Completed`, `In Progress`, `Past Due`, `Not Started` |
| `time_spent` | Time spent in seconds |
| `policy_acknowledged` | Whether policy was acknowledged |

### Cross-inspector cross-check — asset inventory

```
liongard_asset LIST environmentId=<ENV_ID> assetType=Identity detail=full pageSize=200
```

```
# Active identities not enrolled in any KnowBe4 training
enabled_users = Identities where Enabled == true
kb4_users = TrainingEnrollments[*].user.email (from KnowBe4)
training_gap = enabled_users where Email not in kb4_users
```

---

## Metrics and queries

### Org risk score (headline)

| Metric | JMESPath | Result shape |
|---|---|---|
| Current risk score | `AccountInfo.current_risk_score` | `<float 0–100>` |
| Licensed seats | `AccountInfo.number_of_seats` | `<integer>` |
| Subscription level | `AccountInfo.subscription_level` | `<string>` |
| Subscription end date | `AccountInfo.subscription_end_date` | `<ISO timestamp>` |

### Risk score trend

```jmespath
AccountInfo.risk_score_history[*].{date: date, score: risk_score}
```

### Phishing test summary (per test)

```jmespath
PhishingTests[*].{
  name: name,
  status: status,
  startedAt: started_at,
  delivered: delivered_count,
  clicks: clicked_count,
  replies: replied_count,
  opened: opened_count,
  reported: reported_count,
  dataEntered: data_entered_count,
  macroEnabled: macro_enabled_count,
  attachmentOpened: attachment_open_count,
  phishProne: phish_prone_percentage
}
```

### Phishing aggregate KPIs

| Metric | JMESPath | Result shape |
|---|---|---|
| Total clicks across all tests | `sum(PhishingTests[*].clicked_count)` | `<integer>` |
| Average phish-prone % | `avg(PhishingTests[*].phish_prone_percentage)` | `<float>` |
| Total tests | `length(PhishingTests)` | `<integer>` |
| Total reported (good) | `sum(PhishingTests[*].reported_count)` | `<integer>` |

### Top phish-prone users

```jmespath
PhishingTests[*].RecipientResults[?clicked_at != null].{
  email: user.email,
  name: join(' ', [user.first_name, user.last_name]),
  clickedAt: clicked_at,
  testName: template
}
```

> **Per-user aggregate phish-prone %** (across multiple tests) requires client-side
> grouping — group `RecipientResults` by `user.email` across all tests, then
> compute `clicks / delivered` per user.

### Campaign status

| Metric | JMESPath | Result shape |
|---|---|---|
| Active campaigns | `length(Campaigns[?status == 'Active'])` | `<integer>` |
| Campaign phish-prone | `Campaigns[*].{name: name, phishProne: last_phish_prone_percentage}` | `<array>` |
| Campaign frequency | `Campaigns[*].{name: name, frequency: frequency}` | `<array>` |

### Training enrollment & completion

| Metric | JMESPath | Result shape |
|---|---|---|
| Total enrollments | `length(TrainingEnrollments)` | `<integer>` |
| Completed | `length(TrainingEnrollments[?status == 'Completed'])` | `<integer>` |
| In progress | `length(TrainingEnrollments[?status == 'In Progress'])` | `<integer>` |
| Past due | `length(TrainingEnrollments[?status == 'Past Due'])` | `<integer>` |
| Not started | `length(TrainingEnrollments[?status == 'Not Started'])` | `<integer>` |
| Completion rate | `completed / total * 100` (compute) | `<percent>` |

### Training detail table

```jmespath
TrainingEnrollments[*].{
  userName: join(' ', [user.first_name, user.last_name]),
  email: user.email,
  module: module_name,
  campaign: campaign_name,
  status: status,
  enrolled: enrollment_date,
  completed: completion_date,
  timeSpent: time_spent
}
```

### Time-series

```
# Risk score trend
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="AccountInfo.current_risk_score"

# Training completion growth
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="length(TrainingEnrollments[?status == 'Completed'])"
```

---

## Insights & recommendations

| Insight | Trigger | Recommended action template |
|---|---|---|
| Risk score elevated | `current_risk_score > X` (per MSP threshold) | "Risk score at <N>; recommend additional phishing simulations and SAT modules." |
| High avg phish-prone % | `avg(phish_prone_percentage) > slas.phish_prone_pct_max` | "<pct>% phish-prone — increase test cadence or assign remedial training." |
| Repeat clickers | users with clicks in ≥2 distinct tests | "<N> users clicked on multiple tests; enroll in advanced phishing training." |
| Past-due training | `length(TrainingEnrollments[?status == 'Past Due']) > slas.past_due_max` | "<N> users have past-due training; escalate to managers." |
| Subscription expiring | `subscription_end_date − today < slas.subscription_warn_days` | "Renew KnowBe4 <subscription_level> subscription within <N> days." |
| Training gap | identities enabled but absent from `Users[]` | "<N> M365 users not enrolled in KnowBe4 — provision and enroll." |
| Improving trend | period-over-period delta on `risk_score` is negative | "Risk score improved by <N> points; campaigns are working." |

---

## Data gaps vs. typical PBR slide

| Data point | In Liongard? | Notes |
|---|---|---|
| Phish-prone % per test | Yes | `PhishingTests[].phish_prone_percentage` |
| Click/reply/open counts per test | Yes | Full breakdown |
| Per-user failure table | Yes | Via `RecipientResults[]` |
| Organization risk score | Yes | `AccountInfo.current_risk_score` |
| Risk score history | Yes | `AccountInfo.risk_score_history[]` |
| Industry benchmark phish-prone % | No | Supplement from KnowBe4 dashboard |
| Campaign last phish-prone | Yes | `Campaigns[].last_phish_prone_percentage` |
| Training user-activity chart | Partial | Completion dates available; chart requires aggregation |

---

## Output format

Markdown / Word / PowerPoint per `output.format`. See `templates/output-block-*.md`.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_system LIST | query="knowbe4" envId=<ENV_ID> | array<system> | ok |
| 3 | liongard_metric EVALUATE | jmesPath sysId=<SYS_ID> envId=<ENV_ID> | <integer>, <array>, <object> | ok |
| 4 | liongard_asset LIST | envId=<ENV_ID> assetType=Identity detail=full | array<identity> | ok |
```

---
name: domain-assessment-identity-mfa-gap-report
description: >
  Use this recipe when you need an MFA gap report for a customer: which enabled
  identities do not have multi-factor authentication, which of them are privileged,
  and which are stale or never used. Trigger phrases: "MFA gap report for <customer>",
  "who doesn't have MFA", "MFA coverage for <customer>", "privileged accounts without
  MFA", "Microsoft 365 MFA report", "MFA readiness for cyber insurance". Produces a
  customer-ready report with coverage percentage, a prioritized remediation list,
  and a data-freshness disclosure, using the reconciled identity inventory via
  liongard_identity. Works across Microsoft 365, Entra ID, Google Workspace, Active
  Directory, Duo, Okta and any other inspector Liongard reconciles into identities.
  Best for vCIO/Account Managers, SOC and Executives, monthly or on demand.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_identity, liongard_launchpoint, liongard_metric"
personas: [vcio-account-manager, soc, executive, technical-alignment-manager]
output_formats: [markdown, html, word]
recipeType: DomainAssessmentRecipe
---

# Identity MFA Gap Report

> **Quick reference.** Counts enabled identities by MFA status from Liongard's
> reconciled identity inventory, lists every enabled identity without full MFA
> (privileged first), flags stale and never-used accounts, and discloses how old the
> inventory is. Read-only. Inventory first, Microsoft 365 as confirmation, and every other MFA enforcement point (Duo, IdPs) located and credited.

---

## Customize for your MSP

```yaml
output:
  format: html                # markdown | html | word
  audience_type: external     # internal | external
  filename: "MFA-Gap-Report-<customer>-<period>.html"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  coverage: "MFA Coverage"
  privileged: "Privileged Accounts Without MFA"
  gaps: "Accounts Without Full MFA"
  hygiene: "Stale and Unused Accounts"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

slas:
  mfa_coverage_pct_min: 95
  privileged_mfa_pct_min: 100
  stale_account_days: 90
  inventory_age_days_warn: 3

qa:
  retry_on_null: true
  retry_attempts: 1
  manual_verification_section_required: true
```

---

## When to use

- "MFA gap report for <customer>"
- "Which users don't have MFA?" / "Are our admins protected with MFA?"
- Pre-renewal cyber-insurance check, QBR security slide, onboarding baseline.

Cadence: monthly, or before insurance renewals. Pairs with
`all-identity-providers` (full cross-IdP posture) and the cyber-insurance identity
domain.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment | Yes | `liongard_environment LIST` and match by name |
| Output format and audience | Yes (preflight) | Ask the user unless the customize block answers it |

---

## Workflow

> **Scope rule.** Always use the reconciled `liongard_identity` tool. Use
> `totalMatching` / `count` from the tool as every denominator. Do not count rows you
> happened to receive on one page.

### Step 1: Resolve the environment

```
liongard_environment LIST   (match by name; confirm the ID with the user if ambiguous)
```

### Step 2: Headline counts

```
liongard_identity COUNT environmentId=<ENV_ID> includeStatusCounts=true
liongard_identity COUNT environmentId=<ENV_ID> enabled=true includeStatusCounts=true
liongard_identity COUNT environmentId=<ENV_ID> enabled=true privileged=true includeStatusCounts=true
```

`mfaStatus` values are `YES`, `PARTIAL`, `NO` (VALIDATED, string). Coverage % =
YES / enabled total. Report PARTIAL separately; never fold it into YES.
Compute the same breakdown for privileged enabled identities.

Denominator gotcha: the enabled total is the `count` of the **second** call
(`enabled=true`), not the first call (all identities, including disabled). Take YES /
PARTIAL / NO from that same call's `statusCounts`. If YES + PARTIAL + NO is lower than
the enabled count, report the difference as "MFA status not reported by any source"
and still compute coverage % = YES / enabled count. Do not declare coverage
"indeterminate" because the all-identities total differs from the enabled total.
(Validated 2026-10-07: all identities 568, enabled 311 with YES 58 / PARTIAL 27 / NO 211,
15 enabled with no MFA status → coverage 18.6%.)

Field gotcha: `PARTIAL` means the identity has MFA on at least one reconciled source
but not all. It is a gap, not a pass.

### Step 3: List the gaps (privileged first)

```
liongard_identity LIST environmentId=<ENV_ID> enabled=true privileged=true mfaStatus="NO"
  fields=["displayName","email","mfaStatus","mfaMethod","privileged","accountActivity","lastLogin","inspectors"]
liongard_identity LIST environmentId=<ENV_ID> enabled=true privileged=true mfaStatus="PARTIAL" (same fields)
liongard_identity LIST environmentId=<ENV_ID> enabled=true privileged=false mfaStatus="NO" (same fields)
liongard_identity LIST environmentId=<ENV_ID> enabled=true privileged=false mfaStatus="PARTIAL" (same fields)
```

Page until `pagination.totalItems` rows are retrieved; if the list is truncated, say
how many rows are shown out of the total. `inspectors[].alias` names each source
system for the identity (VALIDATED: array of `{alias,id,name}`).

### Step 4: Stale and unused accounts

```
liongard_identity COUNT environmentId=<ENV_ID> enabled=true accountActivity="Never Used"
liongard_identity COUNT environmentId=<ENV_ID> enabled=true accountActivity="Stale"
liongard_identity COUNT environmentId=<ENV_ID> enabled=true accountActivity="Dormant"
```

Enabled accounts without MFA that are also Never Used / Stale / Dormant are the
cheapest remediation: disable instead of enroll.

Field gotcha: `accountActivity` can be null for service or device-sourced identities;
`lastLogin` is an ISO string or null. Null means "no sign-in data from the source",
not "never signed in".

### Step 5: Inventory freshness (always disclose)

The `LIST` and `COUNT` results carry an `asOf` value ("As of <date> (N days ago)") and an
`InventoryFreshness` block with per-source `ageDays` and `stale`. Report the oldest
source age. If it exceeds `inventory_age_days_warn`, state in the Executive Summary that
the report reflects the inventory as of that date and that identities enrolled in MFA
since then are not reflected.

### Step 6: Find every system that can enforce MFA

MFA is often enforced outside Microsoft 365 (a Duo layer in front of M365, an IdP such
as Okta, JumpCloud or OneLogin, or Google Workspace 2-Step). A gap in one source may be
covered by another, so locate all of them before calling anything a gap.

```
liongard_launchpoint LIST environmentId=<ENV_ID> pageSize=100
  fields=["id","system","inspector","latestInspectionDate","status"]
```

Keep launchpoints whose `inspector.alias` is an MFA-capable identity source:
Microsoft 365, Azure / Entra ID, Google Workspace, Duo Security, Okta, JumpCloud,
OneLogin, Active Directory (for hybrid), and any other identity inspector present
(see `reference/inspector-aliases.md`). Also read `inspectors[].alias` across the Step 3
rows: any alias not in this list that appears on gap identities is a source to name in
the report. Record each source's `latestInspectionDate`.

Per-source enrollment check (run only for sources that exist):

| Source | Check | Single-system recipe |
|---|---|---|
| Duo Security | `Users[?is_enrolled == \`false\` && status == 'active']` length and list; `length(BypassCodes)`; bypass users via `Users[?status == 'bypass']` | `duo-security` |
| JumpCloud / OneLogin / Okta | Use that recipe's MFA enrollment metric | `jumpcloud`, `onelogin` |
| Google Workspace | Use its 2-Step enrollment metric | `google-workspace` |

For each identity in the Step 3 gap list, classify it by its `inspectors[]`:

- **Covered elsewhere**: also present in a Duo-type source with `is_enrolled == true`
  and the source is known to gate the app in question. State "MFA enforced by <source>".
- **Gap**: no enrolled MFA source found.
- **Unverified**: an MFA source exists but enrollment for this identity cannot be matched.

Never mark an identity covered unless the enrolled record for that identity was observed.
A Duo deployment existing in the environment is not proof it protects Microsoft 365.

### Step 7: Microsoft 365 confirmation

The identity inventory is the primary result. Microsoft 365 is the confirmation.

```
liongard_launchpoint LIST environmentId=<ENV_ID> (Step 6 result: M365 child systems)
liongard_metric EVALUATE systemId=<M365_SYSTEM> environmentId=<ENV_ID>
  jmesPathQuery="subtract(length(Users[?Privileged == `Yes`]), length(Users[?Privileged == `Yes` && mfaDetails.enforced == `true`]))"
liongard_metric EVALUATE ... "subtract(length(Users[?Privileged != `Yes`]), length(Users[?Privileged != `Yes` && mfaDetails.enforced == `true`]))"
liongard_metric EVALUATE ... "Policies.ConditionalAccess[?state == 'enabled'].displayName"
liongard_metric EVALUATE ... "Policies.SecurityDefaults"
```

Run on each Microsoft 365 child system (a parent system holds the tenant roster and does
not carry the user MFA fields). Compare the M365 admin and non-admin no-MFA counts with
the inventory's Microsoft 365-sourced rows (`inspectors[].alias == "Microsoft 365"`).

Field gotchas: `mfaDetails` may be absent on some tenants or inspector versions
(SCHEMA only; null on test systems). Null means "No data", not "0 gaps". Counts of 0
from `length()` on an absent field must not be reported as full coverage: confirm
`length(Users[?mfaDetails != null])` is greater than 0 first.

### Step 8: Reconcile and report

For each of: all enabled, privileged, Microsoft 365-sourced, report inventory count,
M365 confirmation count, and which MFA sources cover the difference. If inventory and
M365 disagree, the inventory wins and the difference is listed as a data-quality note with
both values. State clearly which MFA enforcement points were found (e.g. "Duo Security,
Microsoft 365") and which expected ones were absent.

---

## Insights & recommendations

| Condition | Recommendation |
|---|---|
| Privileged identity with MFA = NO or PARTIAL | Highest priority. Enforce phishing-resistant MFA on every admin account this week. |
| Coverage % below `mfa_coverage_pct_min` | Roll out MFA enrollment by group, with a conditional-access or enforced-policy deadline. |
| Enabled, MFA = NO, accountActivity Never Used / Stale / Dormant | Disable or remove; no enrollment needed. |
| PARTIAL identities | Close the remaining sources (e.g. an IdP-only MFA that does not cover VPN or mail). |
| Inventory older than `inventory_age_days_warn` | Re-run the inspectors before presenting externally. |

Rank the remediation table: privileged NO, privileged PARTIAL, standard NO active,
standard PARTIAL, stale/unused.

---

## Data gaps

- `mfaStatus` reflects what each source reports; a source that does not expose MFA state
  is not counted as a gap or a pass. List sources with no MFA signal under Data Gaps.
- Conditional-access exclusions, per-app MFA, and security-defaults state are not part
  of the reconciled identity record; verify in the Microsoft 365 single-system recipe.
- `type` (user, service, guest) is not consistently populated; do not segment on it.

---

## QA & Manual Verification

Retry a null or failed call once. Confirm `count` from Step 2 equals YES + PARTIAL + NO.
Confirm Step 3 row totals match the corresponding counts. Flag any mismatch instead of
picking one. End with a **Manual Verification Needed** section. See
`reference/qa-retry-pattern.md`.

---

## Output format

Executive Summary (coverage %, privileged coverage %, count of gaps, inventory age),
coverage table (YES / PARTIAL / NO for all enabled and for privileged), privileged gap
table, gap table, stale/unused table, recommendations, data gaps, manual verification.
Internal audience adds the verification log; external omits it and shows
"Data as of: YYYY-MM-DD HH:MM UTC".

---

## Coverage cross-check

| Source | Coverage |
|---|---|
| CIS Controls v8.1 | 5.x (account management), 6.3 / 6.4 / 6.5 (MFA for external, remote, admin access) |
| Cyber-insurance identity domain | MFA for email, remote access, privileged accounts |
| QBR recipe | Security posture: MFA coverage KPI |
| Microsoft 365 single-system recipe | Conditional access and security defaults detail |

---

## Verification log

| Path / Query | System | Result | Status |
|---|---|---|---|
| `liongard_identity COUNT includeStatusCounts=true` | System A (inventory 7 days old) | total 77; NO 24, PARTIAL 16, YES 27 | VALIDATED |
| `liongard_identity LIST enabled=true mfaStatus="NO"` | System A | 24 matching; fields incl. `inspectors[]`, `lastLogin`, `accountActivity` returned | VALIDATED |
| `liongard_identity LIST enabled=true` (page of 100) | System A | `asOf` present; `mfaStatus` YES/NO/PARTIAL strings; `privileged` boolean | VALIDATED |
| `accountActivity` values | System A | "Active", "Never Used", null (null for some device-sourced rows) | VALIDATED |
| `inspectors[].alias == "Microsoft 365"` | System A | present on M365-sourced rows | VALIDATED |
| `liongard_launchpoint LIST` (identity sources) | System A | M365 parent and child, Duo, AD, KnowBe4, NinjaOne etc. with `inspector.alias` | VALIDATED |
| Duo `length(Users)`; `Users[0].{status,is_enrolled}` | System A (Duo) | 36 users; `status` "active", `is_enrolled` boolean true | VALIDATED |
| Duo `length(BypassCodes \|\| [])` | System A (Duo) | 0 (integer) | VALIDATED |
| M365 `length(Users)`; `Privileged == 'Yes'` | System A (M365 child) | 17 users; 2 privileged | VALIDATED |
| M365 `mfaDetails.enforced == true` | Systems A (parent and child) | `mfaDetails` absent (0 of 17 non-null); parent has no MFA fields | SCHEMA_CONFIRMED (field not populated on test tenant; registry primitive lists it VALIDATED on another tenant) |
| M365 `Policies.SecurityDefaults` | System A (M365 child) | null | SCHEMA_CONFIRMED |
| `InventoryFreshness.sources[].ageDays` | System A | per-source numeric age with `stale` flag | VALIDATED |

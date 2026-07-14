---
name: single-system-dark-web-monitoring
description: >
  Use this skill when the user wants a Dark Web Monitoring assessment
  for a single domain — exposed-credentials inventory, breach-corpus
  match counts, breach source identification, identity-exposure risk
  surfacing. Trigger phrases: "dark web report for <domain>", "what
  credentials are exposed for <customer>", "breach monitoring for
  <domain>", "have we found any of <customer>'s users in breach
  dumps", "identity exposure for <prospect>". Non-credentialed — pulls
  from breach corpus matched against a customer-specified domain;
  suitable for prospects and pre-sales discovery before any credentialed
  access.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric"
personas: [sales, soc, vcio-account-manager, technical-alignment-manager, executive]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  # Reconciled 2026-05-29: pruned dangling refs not present in the live dataprint (see internal/proposed-metrics-backlog.md).
  - metrics:dark-web-inspector:breach-details
  - metrics:dark-web-inspector:total-breaches-count
  - metrics:dark-web-inspector:users-breach-list
  - metrics:dark-web-inspector:users-email-list
  - metrics:dark-web-inspector:users-with-data-breach-count
---

# Single-System Analysis — Dark Web Monitoring

> **Inspector:** `dark-web-inspector` (ID 4). Cloud category.
> External-attack-surface family. **One system per monitored domain.**
> Pulls from a breach-corpus index, matching addresses ending in
> `@<domain>` against known breach dumps. **No customer credential
> required** — the input is a domain name; the output is a count and
> list of corpus matches.
>
> **References:** `reference/inspector-aliases.md` (Dark Web, Breach
> Monitor). Pairs with `microsoft-365.md` / `active-directory.md` for
> the identity-side remediation story (resetting compromised passwords,
> mandating MFA on exposed accounts).

---

## Pre-Sales Discovery Value

Dark Web findings are **the single most-effective pre-sales artifact**
in the external-attack-surface family. Reasons:

1. **Visceral business impact.** "Here are 47 of your employees'
   credentials in known breach dumps" lands harder than any
   configuration finding. The IT director immediately wants to fix
   it, and the executive immediately sees the brand risk.
2. **Zero-credential, fast turnaround.** The inspector needs only a
   domain name to operate. An MSP can pull a prospect's dark-web
   findings in minutes during the discovery call.
3. **Quick-win remediation story.** Even if the MSP doesn't sign the
   prospect, the recommendation ("force a password reset on the
   exposed accounts; enforce MFA") is actionable in days, not months.

Important framing nuance: **never name individual exposed users in
the pre-sales deck.** Aggregate counts only. Naming an exposed user
makes them defensive, suggests the prospect's IT staff has failed, and
violates the recipe's "preserve_current_vendor_dignity" stance.
Individual-level data goes to the IT director's eyes-only document
after the prospect signs.

Accepts a domain via `customization.discovery_input.domains[]` for
the trial / no-credentialed-environment mode.

> **Sales narrative tip:** Combine dark-web findings with the Internet
> Domain inspector's mail-trust findings to tell the complete
> credential-protection story: "Your users' passwords are in breach
> dumps (dark web), and your domain is vulnerable to spoofing (no
> DMARC) — attackers have both halves they need."

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer-or-prospect>-<domain>-dark-web-<date>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  exposure_summary: "Exposure Summary"
  breach_sources: "Breach Sources"
  affected_accounts: "Affected Accounts"             # internal-only / IT-director-eyes
  recent_exposures: "Recent Exposures"               # last N days
  trend: "Exposure Trend"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"                       # technical | balanced | executive
                                         # Discovery / sales: use executive (aggregate counts).
                                         # Post-engagement: balanced (named accounts allowed for
                                         # IT director).

slas:
  exposure_pct_max: 5                    # % of total identities found in breach corpus
                                         # above which is flagged as Critical
  recent_exposure_days: 90               # last 90 days of new exposures = "recent"
  privileged_account_exposed_max: 0      # any privileged account in breach corpus = Critical
  shared_account_exposed_max: 0          # any shared account in breach corpus = Critical
  mfa_overrides_severity: true           # accounts with MFA enabled get lower severity since
                                         # password reuse risk is partially mitigated

reporting_period:
  default: "current_state"               # the corpus is cumulative; recipe surfaces both
                                         # total and "last N days" subsets

discovery_input:
  # Non-credentialed pre-sales mode.
  mode: "credentialed"                   # credentialed | discovery
  domains: []                            # ["prospect.com"]

privacy:
  redact_individual_users_in: ["pptx", "executive-tone-output"]
                                         # never name individual users in deck or executive
                                         # narrative outputs. Aggregate counts only.
  redact_passwords_in_output: true       # never include plaintext password hashes / clear-text
                                         # passwords in any output — even technical mode

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

- "Dark web report for <domain>"
- "What credentials are exposed for <customer>?"
- "Breach monitoring for <domain>"
- "Have we found any of <customer>'s users in breach dumps?"
- "Identity exposure for <prospect>"
- "Pre-sales dark-web discovery for <prospect>"
- Post-breach triage — "did this user appear in our dark-web monitor?"

Cadence: monthly per domain; on-demand during pre-sales; ad-hoc when
a third-party breach affects a vendor the customer uses.

Personas:
- **Sales** (primary in discovery mode — exposure counts power the
  proposal anchor)
- **SOC** (incident — post-breach lookup; ongoing credential-rotation
  driver)
- **vCIO / Account Manager** (renewal narrative — managed identity
  protection)
- **TAM** (remediation — drives MFA enforcement + password resets on
  exposed accounts)
- **Executive** (consumes the aggregated risk language during
  cyber-insurance / board-update conversations)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes (credentialed mode) | `liongard_environment LIST` |
| System ID (the specific dark-web-monitored domain system) | Yes — one per recipe run | `liongard_system LIST query="dark-web"` |
| Domain | Yes (discovery mode) | User-provided; see `discovery_input.domains` |
| Optional: focus area | No | User prompt — e.g., "focus on privileged accounts only" |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer-or-prospect>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="dark-web"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

The breach corpus updates frequently — daily on the major aggregators.
A stale dark-web inspector is much worse than a stale TLS / domain
inspector because new exposures could have appeared since the last
inspection. Flag stale inspectors aggressively (≤ 7 days threshold).

### Step 3 — Pull exposure data

Use `liongard_metric GENERATE_AND_EVALUATE` with the paths below.
The **VALIDATED** paths are confirmed against the live Dark Web
Monitoring inspector dataprint. SCHEMA_CONFIRMED paths represent enrichment
fields that may not yet exist — confirm with `liongard_metric LIST`
before building a report section that depends on them.

```
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  jmesPath="<path>"

# ── VALIDATED fields (confirmed from live GET_OVERVIEW) ──────────────

#   NumberOfUsersWithDataBreach
#     (integer — count of unique email addresses found in breach corpus)

#   NumberOfTotalBreaches
#     (integer — total breach records across all monitored users)

#   Users[*].{Email: Email, Breaches: Breaches}
#     (array — one entry per monitored user; Breaches is itself an array)

#   Users[*].Email
#     (string — the monitored email address; PascalCase)

#   Users[*].Breaches[*].{Name: Name, Title: Title, Domain: Domain,
#                          BreachDate: BreachDate, AddedDate: AddedDate,
#                          PwnCount: PwnCount, DataClasses: DataClasses,
#                          IsVerified: IsVerified, IsSpamList: IsSpamList,
#                          IsMalware: IsMalware, IsStealerLog: IsStealerLog,
#                          IsSubscriptionFree: IsSubscriptionFree}
#     (array of breach objects per user)
#     Key sub-fields:
#       Name          — machine-readable breach slug (e.g., "LinkedIn")
#       Title         — display name (e.g., "LinkedIn")
#       Domain        — breach source domain
#       BreachDate    — ISO date of breach occurrence
#       AddedDate     — ISO date added to HIBP corpus
#       PwnCount      — number of accounts compromised in this breach
#       DataClasses   — array of exposed data type strings
#                       (e.g., ["Email addresses","Passwords","Names"])
#       IsVerified    — boolean; unverified = higher false-positive risk
#       IsSpamList    — boolean; spam-list hits ≠ credential breach
#       IsMalware     — boolean; stealer-log malware attribution
#       IsStealerLog  — boolean; infostealer origin (elevated severity)
#       IsSubscriptionFree — boolean; paywalled vs. free corpus

# ── Unvalidated fields (confirm via liongard_metric LIST) ────────────

#   "dark-web.exposures.recentCount"
#     (count of exposures within the slas.recent_exposure_days window)

#   "dark-web.exposures.privilegedAccountMatches"
#     (cross-reference: exposed emails matching privileged identity list)

#   "dark-web.exposures.sharedAccountMatches"
#     (cross-reference: exposed emails matching shared/generic accounts)

#   "dark-web.exposures.passwordPlaintextCount"
#     (count of breaches where DataClasses includes "Passwords" in clear-text)
```

> **Proposed-metric gap risk.** Confirm unvalidated paths with
> `liongard_metric LIST environmentId=<ENV_ID> systemId=<SYS_ID>`.
> File missing metric requests via the `liongard-metrics` skill.

### Step 4 — Cross-reference with identity inventory (if available)

When the customer has the M365 / AD / JumpCloud / OneLogin inspector
deployed, cross-reference the exposed-account list against the
authoritative identity inventory:

```
liongard_identity LIST environmentId=<ENV_ID>
                    fields=["username","type","privileged","mfaStatus","lastLogin","enabled"]
```

> **Tool note:** `liongard_identity` is the reconciled identity inventory —
> one record per email, joined across every identity inspector (M365, AD,
> JumpCloud, OneLogin, Duo, etc.). Use the server-side filters
> (`mfaStatus`, `privileged`, `enabled`) or `COUNT` instead of pulling the
> full list when you only need a coverage figure.

Surface enrichment:

| Cross-reference | Surface as |
|---|---|
| Exposed account → currently enabled identity | Active exposure — Critical |
| Exposed account → privileged identity | Highest priority — Critical |
| Exposed account → identity with MFA enabled | Lower severity (still flag for password reset) |
| Exposed account → identity without MFA | Critical — both halves of the attack chain present |
| Exposed account → disabled / stale identity | Lower severity — confirm fully decommissioned |
| Exposed account → not found in identity inventory | Confirm — may be a personal email used at work, or already cleaned up |

> **The cross-reference is the highest-leverage section.** Raw breach
> counts are interesting; cross-referenced to live, MFA-less,
> privileged accounts they become actionable security findings.

### Step 5 — Exposure trend

For each breach source, surface:

| Signal | Treatment |
|---|---|
| Recent exposure (within `slas.recent_exposure_days`) | Lead the narrative — "new exposures this quarter" |
| Pre-existing exposure with old breach | Maintenance — confirm passwords have been rotated since breach date |
| Clear-text passwords in breach | High — password reuse risk |
| Hashed passwords in breach | Medium-to-High depending on hash strength |
| Email-only exposure (no password) | Low — but useful as a phishing-target list signal |

### Step 6 — QA pass (per `reference/qa-retry-pattern.md`)

This recipe's QA pass especially focuses on:

1. **Retry persistent nulls** — breach-corpus API calls can rate-limit
   during heavy load.
2. **Flag stale inspectors** aggressively (Step 2).
3. **Identity cross-reference completeness** — confirm the identity
   inventory used in Step 4 is itself current (not from a stale
   identity-provider inspector).
4. **Privacy validation** — confirm `privacy.redact_individual_users_in`
   has been honored before any deck output. Plaintext-password redaction
   from output is **non-negotiable**.
5. **Proposed-metric gaps** in the verification log.

### Step 7 — Render output

| Output mode | Best for |
|---|---|
| `markdown` | Working draft (technical — IT director eyes-only) |
| `word` | Customer-facing letter with aggregate counts |
| `pptx` | Aggregated-counts-only slides for pre-sales / QBR deck |
| `xlsx` | Internal IT-director-eyes-only sheet with per-account rows |

---

## QA & Manual Verification

Per `reference/qa-retry-pattern.md`. Manual checks specific to this
recipe:

- **Verify identity-cross-reference logic** — false-positive accounts
  (e.g., personal email used at work) shouldn't be presented as
  "compromised employee" findings.
- **Password rotation history** — when the customer's identity
  provider exposes "lastPasswordChange", confirm whether the
  exposed-password breach predates the last rotation (lower severity)
  or postdates (high severity).
- **Privacy clearance** — every output containing per-account data
  needs sign-off on the audience scope before distribution. Default
  the per-account sheet to internal-only.

---

## Insights & recommendations — generation patterns

| Pattern | Recommendation template |
|---|---|
| Privileged account exposed | "URGENT: <N> privileged accounts found in breach corpus. Force password reset + enforce MFA + audit recent activity immediately." |
| Active account exposed without MFA | "<N> active accounts found in breach corpus and lacking MFA. Force password reset + enroll in MFA within 7 days." |
| Active account exposed with MFA | "<N> active accounts found in breach corpus but protected by MFA. Force password reset as standard hygiene." |
| Shared / generic account exposed | "<N> shared accounts (e.g., `info@`, `support@`) found in breach corpus. Convert to per-user named accounts; rotate the shared credentials in the interim." |
| Recent exposure (within warn window) | "<N> new exposures discovered in the last <N> days. Triage source, force password rotation on affected accounts." |
| Plaintext-password exposure | "<N> exposures included clear-text passwords. Treat any password reuse on those accounts as compromised." |
| High exposure rate (% of users) | "Total exposure rate of <N>% suggests systemic password-reuse risk. Recommend organization-wide rotation + password-manager rollout." |
| Disabled account exposed (lingering) | "<N> disabled accounts found in breach corpus. Confirm full decommission (no inboxes / file shares / VPN profiles still linked)." |
| Repeat breach source | "Multiple exposures from <breach-source> indicate users frequenting a compromised third-party service. Awareness training topic." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Real-time breach detection | partial — corpus updates per provider cadence | Per-provider real-time feed (HaveIBeenPwned API, etc.) |
| Personal-email exposure of employees | external | Employee awareness; partner-provided breach lookup tools |
| Breach attribution detail | partial | Threat-intel feeds |
| Password-rotation enforcement evidence | partial — identity-provider dependent | Identity-provider audit log |
| Cross-tenant credential reuse | external | Password-manager analytics (LastPass / 1Password / etc.) |

---

## Output format

Default `markdown` (internal). Switch to `word` / `pptx` for
customer-facing; always honor `privacy.redact_individual_users_in`.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | query=<customer> | array<environment> | ok |
| 1 | liongard_system LIST | envId=<ENV_ID> query="dark-web" | array<system> | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3 | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath="NumberOfUsersWithDataBreach" | integer | VALIDATED |
| 3 | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath="NumberOfTotalBreaches" | integer | VALIDATED |
| 3 | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath="Users[*].{Email: Email, Breaches: Breaches}" | array | VALIDATED |
| 3 | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath=<proposed-path> | varies | SCHEMA_CONFIRMED — not found in live dataprint; confirm against production system |
| 4 | liongard_identity LIST | envId=<ENV_ID> [fields] | array<identity> | ok |
| 4 | (cross-reference — derived) | exposed accounts ∩ identity inventory | enriched-finding | ok |
| 5 | (trend — derived) | per slas.recent_exposure_days | series | ok |
| 6 | QA pass | per `reference/qa-retry-pattern.md` (privacy check included) | varies | ok |
| 7 | render | per `output.format` (with privacy redaction) | <artifact path> | ok |
```

---
name: system-type-all-identity-providers
description: >
  Use this skill when the user wants a unified identity posture
  assessment across all identity providers in an environment —
  Microsoft 365 (Entra ID), Active Directory, JumpCloud, OneLogin,
  and Duo Security. Trigger phrases: "identity posture for <customer>",
  "all identity providers", "MFA coverage across <customer>",
  "privileged-user audit across <customer>", "stale-account audit",
  "identity inventory rollup", "identity-provider sprawl",
  "hybrid identity report".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_identity, liongard_cyber_risk_dashboard"
personas: [soc, technical-alignment-manager, vcio-account-manager, executive, accounting-finance]
output_formats: [pptx, word, xlsx, markdown]
primitives:
  - metrics:active-directory:dhcp-scopes
  - metrics:active-directory:guest-account-enabled
  - metrics:active-directory:guest-members-count
  - metrics:active-directory:lockout-duration-hours
  - metrics:active-directory:lockout-observation-window-hours
  - metrics:active-directory:lockout-threshold
  - metrics:active-directory:lockout-threshold-string
  - metrics:active-directory:max-password-age-days
  - metrics:active-directory:min-password-length
  - metrics:active-directory:never-used-users-count
  - metrics:active-directory:password-complexity-enabled
  - metrics:active-directory:password-history-length
  - metrics:active-directory:password-reversible-encryption
  - metrics:active-directory:privileged-users-count
  - metrics:active-directory:privileged-users-list
  - metrics:active-directory:stale-users-count
  - metrics:azure:enabled-subscriptions-count
  - metrics:azure:nsg-rdp-exposed-count
  - metrics:azure:nsg-rdp-exposed-list
  - metrics:azure:subnets-list
  - metrics:azure:virtual-machine-count
  - metrics:azure:virtual-machines-list
  - metrics:duo-security:active-bypass-lockedout-user-count
  - metrics:duo-security:active-user-count
  - metrics:duo-security:active-user-list
  - metrics:duo-security:admins-summary
  - metrics:duo-security:bypass-codes-summary
  - metrics:duo-security:count-of-integrations
  - metrics:duo-security:settings-summary
  - metrics:duo-security:user-summary-dashboard
  - metrics:duo-security:users-not-enrolled-mfa-count
  - metrics:duo-security:users-not-enrolled-mfa-list
  - metrics:google-workspace:groups-open-membership-count
  - metrics:google-workspace:less-secure-app-access-enabled
  - metrics:google-workspace:licensing-utilization-pct
  - metrics:google-workspace:super-admin-count
  - metrics:google-workspace:super-admin-list
  - metrics:google-workspace:third-party-apps-unverified-count
  - metrics:google-workspace:twostep-coverage-pct
  - metrics:google-workspace:twostep-enforced-count
  - metrics:google-workspace:users-stale-count
  - metrics:google-workspace:users-total-count
  - metrics:jumpcloud:devices-total-count
  - metrics:jumpcloud:locked-user-accounts-count
  - metrics:jumpcloud:locked-user-accounts-list
  - metrics:jumpcloud:no-password-expiration-count
  - metrics:jumpcloud:password-policy-min-length
  - metrics:jumpcloud:sso-application-count
  - metrics:jumpcloud:sso-apps-no-users-count
  - metrics:jumpcloud:systems-with-failed-commands-count
  - metrics:jumpcloud:systems-with-failed-commands-list
  - metrics:jumpcloud:systems-with-failed-policies-count
  - metrics:jumpcloud:systems-with-failed-policies-list
  - metrics:jumpcloud:users-admin-count
  - metrics:jumpcloud:users-enabled-count
  - metrics:jumpcloud:users-mfa-enabled-count
  - metrics:jumpcloud:users-total-count
  - metrics:microsoft-365:active-users-count
  - metrics:microsoft-365:admin-users-mfa-disabled-count
  - metrics:microsoft-365:associated-domains
  - metrics:microsoft-365:conditional-access-policies-list
  - metrics:microsoft-365:directory-sync-enabled
  - metrics:microsoft-365:directory-sync-stale-hours-count
  - metrics:microsoft-365:disabled-users-count
  - metrics:microsoft-365:disabled-users-with-licenses-count
  - metrics:microsoft-365:enterprise-e3-licenses-consumed
  - metrics:microsoft-365:enterprise-e5-licenses-consumed
  - metrics:microsoft-365:licensed-users-count
  - metrics:microsoft-365:licenses-total-assigned-count
  - metrics:microsoft-365:non-admin-users-mfa-disabled-count
  - metrics:microsoft-365:privileged-users-count
  - metrics:microsoft-365:privileged-users-list
  - metrics:microsoft-365:security-defaults-enabled
  - metrics:microsoft-365:sharepoint-sites-count
  - metrics:microsoft-365:stale-licensed-users-count
  - metrics:microsoft-365:unlicensed-users-count
  - metrics:microsoft-365:users-not-mfa-registered-count
  - metrics:onelogin:active-users-count
  - metrics:onelogin:active-users-list
  - metrics:onelogin:application-summary
  - metrics:onelogin:applications-total-count
  - metrics:onelogin:locked-users-count
  - metrics:onelogin:locked-users-list
  - metrics:onelogin:never-logged-in-users-count
  - metrics:onelogin:never-logged-in-users-list
  - metrics:onelogin:suspended-users-count
  - metrics:onelogin:suspended-users-list
  - metrics:onelogin:unactivated-users-count
  - metrics:onelogin:unactivated-users-list
  - metrics:onelogin:user-summary
  - metrics:onelogin:users-mfa-enrolled-count
  - metrics:onelogin:users-with-expired-password-count
  - metrics:onelogin:users-with-expired-password-list
---

# System-Type Assessment — All Identity Providers

> Unified identity posture across every identity-provider inspector
> in the environment. Joins the per-inspector singles with the
> reconciled `liongard_identity` tool to produce one cross-IdP view:
> MFA coverage, privileged-account audit, stale-account roster, IdP-
> sprawl analysis, hybrid-identity reconciliation.
>
> **Identity sources covered:**
>
> | Inspector | Recipe |
> |---|---|
> | Microsoft 365 (incl. Entra ID) | `recipes/single-system-analysis/by-inspector/microsoft-365.md` |
> | Active Directory | `recipes/single-system-analysis/by-inspector/active-directory.md` |
> | Google Workspace | `recipes/single-system-analysis/by-inspector/google-workspace.md` |
> | JumpCloud | `recipes/single-system-analysis/by-inspector/jumpcloud.md` |
> | OneLogin | `recipes/single-system-analysis/by-inspector/onelogin.md` |
> | Duo Security (MFA layer) | `recipes/single-system-analysis/by-inspector/duo-security.md` |
>
> **Note on Duo:** Duo is technically an MFA layer atop another IdP
> (M365 / AD / etc.) rather than an identity source itself. This rollup
> treats Duo as the **MFA-coverage authoritative** layer when present,
> overriding per-IdP MFA flags where Duo evidence exists.
>
> **References:** `reference/asset-fields.md` (the reconciled identity
> inventory tools); `reference/qa-retry-pattern.md`;
> `reference/inspector-aliases.md`.

---

## Customize for your MSP

```yaml
output:
  format: pptx                           # pptx | word | xlsx | markdown
                                         # Default: executive identity-posture deck.
  filename: "<customer>-identity-posture-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  cover: "Identity Posture Assessment"
  executive_summary: "Executive Summary"
  provider_inventory: "Identity Providers in Use"
  mfa_coverage: "MFA Coverage"
  privileged_audit: "Privileged-User Audit"
  stale_accounts: "Stale Accounts"
  shared_accounts: "Shared / Generic Accounts"
  hybrid_reconciliation: "Hybrid-Identity Reconciliation"
  policy_drift: "Policy Drift vs. Standard"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Manual Verification"
  appendix: "Appendix — Per-Provider Detail"
  verification_log: "Verification Log"

audience:
  tone: "balanced"                       # technical | balanced | executive

slas:
  mfa_coverage_pct_min: 95
  privileged_mfa_required: true          # 100% required on privileged
  stale_user_days_max: 90
  shared_account_max: 0
  prohibited_auth_methods: ["sms"]
  identity_provider_consolidation_target: 2   # MSP standard: ≤ 2 IdPs per customer
                                              # (M365 + Duo is one common pair;
                                              #  JumpCloud-only is another;
                                              #  3+ IdPs = consolidation candidate)

reporting_period:
  default: "current_state"

stack:
  auto_discover: true                    # discover deployed IdPs automatically
  inspectors_in_scope: []
  inspectors_to_skip: []

narrative:
  lead_with_combined_story: true         # surface the hybrid-identity reconciliation findings
                                         # before per-provider detail
  surface_no_issue_categories: true      # "MFA coverage at 98% — meets standard" reads as
                                         # confidence-building
  redact_individual_users: false         # for the IT-director-eyes-only flavor; flip to true
                                         # for executive output

qa:
  retry_on_null: true
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: false
  surface_single_source_visibility: true
  manual_verification_section_required: true
```

---

## When to use

- "Identity posture for <customer>"
- "MFA coverage across <customer>'s environment"
- "Privileged-user audit across all identity providers"
- "Stale-account audit"
- "Hybrid-identity report — who's in M365 but not in AD"
- "Identity-provider consolidation candidate analysis"

Cadence: monthly per customer; quarterly in PBR; required content
in compliance / cyber-insurance evidence packs.

Personas:
- **SOC** (primary — MFA, privileged, stale)
- **TAM** (policy drift; bringing customer to MSP IdP standard)
- **vCIO / Account Manager** (consolidation / renewal narrative)
- **Executive** (consumes the headline coverage tiles)
- **Accounting / Finance** (license utilization — IdP seat counts)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |

---

## Workflow

### Step 1 — Scope + IdP discovery

```
liongard_environment LIST searchMode=keyword query="<customer>"

# Discover which IdP inspectors are deployed
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="microsoft-365"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="active-directory"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="google-workspace"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="jumpcloud"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="onelogin"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="duo"
```

Emit a per-provider deployment table. If more than
`slas.identity_provider_consolidation_target` IdPs are deployed,
surface as a consolidation candidate.

### Step 2 — Inspector freshness across all IdPs

```
liongard_timeline LIST environmentId=<ENV_ID>
```

Stale-inspector findings per IdP — each downstream assertion inherits
the stale flag.

### Step 3 — Reconciled identity inventory (ground truth)

> **The `liongard_identity` record is the primary source of truth for every
> cross-system identity question.** Liongard deduplicates by email address across
> every IdP it observes, then synthesizes the combined signals into a single record:
>
> - **`mfaStatus`** (`YES` / `NO` / `PARTIAL`) — confirmed from **any** connected
>   system. An identity shown as "MFA not registered" in M365 native MFA may still
>   have `mfaStatus = "YES"` if Duo is enrolled, if a Conditional Access policy
>   enforces it, or if another IdP (JumpCloud, OneLogin) has confirmed it. Do not
>   conclude MFA is absent based on a single-inspector metric when this field says YES.
> - **`accountActivity`** (`Active` / `Stale` / `Dormant` / `Never Used` /
>   `No Activity Found`) — cross-system synthesized staleness. A user active in one
>   system but dormant in another yields a reconciled activity state that reflects the
>   full picture. Use this for dormancy analysis rather than per-IdP last-login alone.
> - **`privileged`** (bool) — elevated in **any** connected system.
> - **`inspectors[]`** — which systems contributed to this record. An identity with
>   Duo in `inspectors[]` has a Duo-attested MFA signal factored into `mfaStatus`.
>
> Per-IdP metrics in Step 4 are the **cross-check and configuration detail layer** —
> they confirm the reconciled answer and surface inspector-unique fields
> (CA policy names, AD password policy settings, Duo bypass-code status) that don't
> roll up to the identity record. When the reconciled record and a per-IdP metric
> disagree, the reconciled record wins; record the divergence as a data-quality flag.

```
liongard_identity COUNT environmentId=<ENV_ID>
liongard_identity COUNT environmentId=<ENV_ID> enabled=true
liongard_identity COUNT environmentId=<ENV_ID> privileged=true
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" privileged=true

# Full roster with cross-system fields
liongard_identity LIST environmentId=<ENV_ID>
                       fields=["email","displayName","privileged","mfaStatus","mfaMethod",
                               "accountActivity","enabled","lastLogin","emailLicenses","inspectors"]
```

The COUNT results are the headline KPI inputs. The LIST result is the supporting
roster — group by `mfaStatus`, `accountActivity`, and `privileged` client-side for
the section tables.

### Step 4 — Per-IdP findings (chain singles)

For each deployed IdP, chain the corresponding single-system recipe
with `audience.tone` inherited:

| Deployed | Chained recipe |
|---|---|
| M365 | `recipes/single-system-analysis/by-inspector/microsoft-365.md` |
| AD | `recipes/single-system-analysis/by-inspector/active-directory.md` |
| Google Workspace | `recipes/single-system-analysis/by-inspector/google-workspace.md` |
| JumpCloud | `recipes/single-system-analysis/by-inspector/jumpcloud.md` |
| OneLogin | `recipes/single-system-analysis/by-inspector/onelogin.md` |
| Duo | `recipes/single-system-analysis/by-inspector/duo-security.md` |

Extract the **top findings** from each — not the full output.

### Step 5 — MFA coverage rollup

The **reconciled `mfaStatus` from Step 3 IS the headline KPI** — it already
incorporates every connected system's MFA signal, including:
- Duo enrollment (if Duo inspector is deployed)
- Microsoft Conditional Access policy enforcement (if M365 inspector is deployed)
- Security Defaults enablement (M365)
- Native IdP MFA registration (AD, JumpCloud, OneLogin, Google Workspace)

An identity that M365 reports as "MFA not registered" in its native registry
may have `mfaStatus = "YES"` because Duo is enrolled or Conditional Access
enforces an MFA claim. The reconciled view resolves this without manual
cross-referencing.

Compute at two levels:

| Level | Source | Use |
|---|---|---|
| **Reconciled MFA %** (headline) | `(total_enabled - mfaStatus_NO_count) / total_enabled * 100` | Primary KPI — accounts for all enforcement mechanisms |
| Per-IdP MFA % | Each chained recipe's metric (Step 4) | Supporting detail — explains *where* gaps exist and *which* mechanism covers them |

> **On Duo deployments:** When the Duo inspector is in `inspectors[]` for an
> identity, the reconciled `mfaStatus` already reflects Duo enrollment. You do not
> need a separate Duo-attested figure — the reconciled count IS Duo-attested where
> applicable. The Duo single-system recipe (chained in Step 4) surfaces operational
> detail: bypass codes, unenrolled users by application, lockout-threshold settings.

When per-IdP MFA % is lower than the reconciled %, it means other systems are
enforcing MFA that the per-IdP view doesn't see — this is the expected and correct
outcome when Conditional Access or Duo is the enforcement layer. Surface this gap
explicitly so the customer understands the full picture:

> "Your M365 native MFA registration shows 72% enrolled. However, Liongard's
> reconciled identity view shows 94% with confirmed MFA — the difference is users
> covered by Conditional Access policy enforcement and Duo. Remaining 6% (<N> users)
> have no confirmed MFA from any connected system."

### Step 6 — Privileged-user audit

```
liongard_identity LIST environmentId=<ENV_ID> privileged=true
                       fields=["username","accountType","mfaStatus","lastLogin","enabled","inspectors"]
```

Surface each privileged identity with:
- Privileged in which IdP(s)
- MFA status (Duo + native)
- Last-login currency
- Service-account vs. interactive

Flag any privileged identity without MFA as **Critical**.

### Step 7 — Stale-account roster

> **`accountActivity` is the cross-system synthesized staleness signal.** A user
> active in one system but dormant in another yields a reconciled activity state.
> Use the server-side `accountActivity` filter rather than computing from `lastLogin`
> alone (which reflects only the most recent observation across all systems).

```
# Server-side filter — use accountActivity for cross-system dormancy
liongard_identity LIST environmentId=<ENV_ID> enabled=true accountActivity="Stale"
                       fields=["email","displayName","lastLogin","accountActivity","inspectors","privileged"]
liongard_identity LIST environmentId=<ENV_ID> enabled=true accountActivity="Dormant"
                       fields=["email","displayName","lastLogin","accountActivity","inspectors","privileged"]
liongard_identity LIST environmentId=<ENV_ID> enabled=true accountActivity="Never Used"
                       fields=["email","displayName","lastLogin","accountActivity","inspectors","privileged"]
```

Stale + enabled + privileged is a Critical finding — an account with admin rights
that hasn't been used recently is both an access-creep and a credential-compromise
risk. Surface these separately from the general stale roster.

### Step 8 — Hybrid-identity reconciliation

For environments with multiple IdPs, surface:

| Reconciliation finding | Treatment |
|---|---|
| Identity in M365 but not in AD (hybrid environment) | Confirm intentional cloud-only account or sync gap |
| Identity in AD but not in M365 (hybrid environment) | Confirm intentional non-mailbox account |
| Identity in JumpCloud but not in M365 / AD | Confirm SSO-only access scope |
| Identity in OneLogin but not in source IdP | Confirm SSO-only access scope |
| Duo enrollment without matching IdP identity | Confirm not an orphaned Duo enrollment |
| Differing privileged-role across IdPs (admin in one, not another) | Confirm intentional role-separation |

### Step 9 — Policy drift vs. standard

Compare each deployed IdP's policy posture against MSP-standard:

| Standard | M365 | AD | JumpCloud | OneLogin | Duo |
|---|---|---|---|---|---|
| MFA required for admins | ConditionalAccess policy | (handled by Duo / M365) | Org policy | Policy on Admin Role | Policy + Application |
| Password complexity | M365 password policy / federated | Domain password policy | Org password policy | Org password rules | n/a |
| Session timeout | ConditionalAccess | (handled by Duo / M365) | Org policy | Policy session-timeout | Policy session-timeout |
| New-device requires registration | ConditionalAccess | (handled by Duo / M365) | Policy | Policy | Policy new-device action |

### Step 10 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on:
1. Retry persistent nulls per IdP.
2. Stale-inspector flags propagate per IdP.
3. **Cross-IdP count divergence** is expected (each IdP sees its own
   identities); surface the union vs. intersection sizes for the
   IT-director audience.
4. **Reconciled `mfaStatus` is already the authoritative headline KPI** — it
   incorporates Duo, Conditional Access, and native IdP signals. If per-IdP
   MFA counts are lower than the reconciled figure, narrate the gap explicitly
   (see Step 5 example narrative). Do not override the reconciled count with a
   single-IdP figure.
5. Privacy validation when `narrative.redact_individual_users == true`.

### Step 11 — Render

Recommended slide / page order for pptx:

| # | Slide | Content |
|---|---|---|
| 1 | Cover | Customer, period, MSP name + logo |
| 2 | Executive Summary | 5–8 outcome bullets, headline coverage |
| 3 | Identity Providers in Use | Per-IdP deployment table + consolidation candidate flag |
| 4 | MFA Coverage | Reconciled MFA % (headline) + per-IdP breakdown + narrative on enforcement mechanism |
| 5 | Privileged-User Audit | The Step 6 table |
| 6 | Stale Accounts | The Step 7 roster (counts + top N) |
| 7 | Hybrid-Identity Reconciliation | The Step 8 findings |
| 8 | Policy Drift | The Step 9 comparison |
| 9 | Recommendations | Prioritized actions |
| 10 | Data Gaps | The Step 10 manual-verification appendix |

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | Identity rollup — endpoint-questions matrix doesn't apply. The identity-equivalent questions (MFA % / privileged audit / stale accounts) are covered as the rollup's core sections. |
| CIS Controls (v8.1) | ✅ | Maps to CIS 4.7, 5.1, 5.2, 5.3, 5.4, 6.1, 6.2, 6.3, 6.4, 6.5, 6.7, 6.8 — the full account-management + access-control control family. See `recipes/compliance/cyber-insurance/domains/auth.md`. |
| Cyber-insurance domain files | ✅ | This rollup is the canonical evidence source for `domains/auth.md` Q2–Q4, Q6–Q7 (incl. 6a–6f), Q14–Q17 (admin audit), Q30–Q31 (stale), Q38–Q39 (shared). |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this as the customer's reconciled identity-posture section; surfaces reconciled MFA %, privileged audit, stale-account count, hybrid-identity reconciliation. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| Reconciled MFA below SLA | "Reconciled MFA coverage at <N>%. Enforce MFA on the <N> outstanding users." |
| Privileged user without MFA across any IdP | "URGENT: <N> privileged accounts lack MFA. Enforce immediately on <list-of-IdPs>." |
| 3+ IdPs deployed | "Customer uses <N> identity providers. Consolidation candidate — recommended target stack is <MSP standard>." |
| Duo not deployed, mixed-IdP environment | "Duo (or equivalent) MFA layer not deployed. Consider Duo as the single MFA authority across all IdPs." |
| Stale account count high | "<N> active accounts haven't logged in for > <N> days. Schedule disable + delete-after-N-day flow." |
| Identity in M365 but not in AD (hybrid) | "<N> cloud-only M365 identities not present in AD. Confirm intentional vs. sync issue." |
| Identity in AD but not in M365 (hybrid) | "<N> AD identities not present in M365. Confirm non-mailbox scope." |
| Differing privileged role | "<N> identities have privileged role in one IdP but not others. Reconcile to MSP standard." |
| SMS auth method allowed in any IdP | "Disable SMS auth in <list-of-IdPs>. Migrate users to Push / WebAuthn." |
| Password-policy drift | "Tighten <IdP> password policy to MSP standard: min length <baseline>, max age <baseline>, complexity required." |
| Long session timeout | "Reduce session timeout from <N> to <baseline> in <IdP>." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Conditional-access policy detail (M365 / Duo) | partial | M365 Admin Center / Duo Admin Panel |
| Risk-based / step-up authentication | partial | Per-IdP console |
| Federation health (cross-IdP sync) | partial | Per-IdP console |
| Per-app sign-in volume | partial | Per-IdP console |
| Authentication-event log | partial / external | SIEM |
| Shared / generic-account legitimate-use confirmation | external | Customer documentation |

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST + liongard_system LIST | per-IdP queries | array<system> | ok per IdP |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3 | liongard_identity LIST + COUNT | envId=<ENV_ID> [filters] | varies | ok |
| 4 | (chain per-IdP singles) | per single-system recipe | per-recipe findings | ok per IdP |
| 5 | (MFA rollup — derived) | per slas | KPI tiles | ok |
| 6 | liongard_identity LIST | envId=<ENV_ID> privileged=true | array<identity> | ok |
| 7 | liongard_identity LIST | envId=<ENV_ID> [stale filter] | array<identity> | ok |
| 8 | (hybrid reconciliation — derived) | per-IdP set ops | array<finding> | ok |
| 9 | (policy drift — derived) | per slas | comparison table | ok |
| 10 | QA pass | per `reference/qa-retry-pattern.md` | varies | ok |
| 11 | render | per `output.format` | <artifact path> | ok |
```

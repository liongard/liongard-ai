---
name: single-system-jumpcloud
description: >
  Use this skill when the user wants a single-system analysis of a
  JumpCloud directory — identity inventory, MFA enrollment + posture,
  privileged-admin audit, device-enrollment coverage, SSO application
  inventory, policy posture, user-group / device-group hygiene.
  Trigger phrases: "JumpCloud review", "JC posture for <customer>",
  "who's admin in JumpCloud", "JumpCloud MFA report", "JumpCloud
  device coverage", "JumpCloud SSO app inventory". Treats JumpCloud as
  an integrated directory + MDM + SSO platform (its typical positioning
  at small / mid-market MSPs).
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_identity, liongard_device"
personas: [soc, technical-alignment-manager, vcio-account-manager, noc]
output_formats: [markdown, word, pptx, xlsx]
primitives:
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
---

# Single-System Analysis — JumpCloud

> **Inspector:** `jumpcloud-inspector` (ID 68). Cloud category.
> **One system per JumpCloud organization.** Cloud directory +
> identity / device / SSO / MDM hybrid — frequently the primary
> directory at MSPs serving mid-market customers without a Microsoft
> 365 anchor tenant.
>
> **References:** `reference/inspector-aliases.md` (JC, JumpCloud).
> Pairs with `recipes/single-system-analysis/by-inspector/active-directory.md`
> when JumpCloud is bridging an on-prem AD; cross-reference with the
> reconciled identity / device inventory via
> `reference/asset-fields.md`.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-jumpcloud-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  identity_inventory: "Identity Inventory"
  mfa: "MFA Posture"
  admin_audit: "Admin & Privileged-User Audit"
  device_enrollment: "Device Enrollment Coverage"
  sso_applications: "SSO Application Inventory"
  groups: "Group Hygiene"
  policies: "Policy Posture"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"

slas:
  mfa_coverage_pct_min: 95
  privileged_mfa_required: true
  device_enrollment_pct_min: 90
  stale_user_days_max: 90                # disable enabled users with no login in N days
  shared_account_max: 0
  password_policy_min_length: 14
  password_policy_complexity_required: true
  password_policy_max_age_days: 365      # JumpCloud defaults: very long; MSP standard may shorten
  password_policy_reuse_prohibited_count: 24
  default_user_admin_disabled: true      # newly-created users must NOT be admin by default
  sso_apps_with_no_users_max: 0          # orphaned app integrations

reporting_period:
  default: "current_state"

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

- "JumpCloud posture review for <customer>"
- "Who's admin in JumpCloud at <customer>?"
- "JumpCloud MFA coverage check"
- "JumpCloud device-enrollment audit"
- "Which SSO apps does <customer> have in JumpCloud?"

Cadence: monthly per customer; quarterly in PBR; on-demand for incident.

Personas:
- **SOC** (primary — MFA, admin audit, stale-account hygiene)
- **TAM** (policy posture; bringing customer to MSP standard)
- **vCIO / Account Manager** (license utilization + renewal narrative)
- **NOC** (operational — device enrollment / sync issues)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the JumpCloud **child** org) | Yes | `liongard_launchpoint LIST inspectorId=68 environmentId=<ENV_ID>` — see below |

---

## Locating the right system

> **⚠️ Parent/child structure — validated 2026-05-28.** JumpCloud presents as two launchpoints per organisation.

| Launchpoint type | Top-level keys | Use for |
|---|---|---|
| **Parent** | `Name`, `Discovered[]` (child stubs), `Organizations[]` | Tenant roster only — **no identity or device data** |
| **Child** | `Users[]`, `Systems[]`, `Groups[]`, `Applications`, `Policies`, `SystemInfo` | All identity, device, SSO, and policy data |

Always target the **child** system for metric evaluation. Evaluating any identity or device path against the parent returns null or an empty object.

```
liongard_launchpoint LIST inspectorId=68 environmentId=<ENV_ID>
  fields=["id", "system.id", "system.name", "status", "latestInspectionDate"]
```

Pick the system whose name does **not** contain "-Parent" (or confirm via GET_OVERVIEW that it has a `Users` key). Note the `system.id` as `<SYS_ID>`.

---

## Workflow

### Step 1 — Resolve environment + child system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_launchpoint LIST inspectorId=68 environmentId=<ENV_ID>
  fields=["id", "system.id", "system.name", "status", "latestInspectionDate"]
# Select the child system — NOT the parent. See Locating the right system above.
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Identity inventory

```
# Headline counts
liongard_metric EVALUATE jmesPathQuery="length(Users)" systemId=<SYS_ID> environmentId=<ENV_ID>
liongard_metric EVALUATE jmesPathQuery="length(Users[?activated == `true` && suspended != `true`])" systemId=<SYS_ID> environmentId=<ENV_ID>
liongard_metric EVALUATE jmesPathQuery="length(Users[?suspended == `true`])" systemId=<SYS_ID> environmentId=<ENV_ID>
```

> **Field note — user state:** `activated == true && suspended != true` = active enabled user. `activated == false` = invited/pending (has not completed setup). `suspended == true` = explicitly disabled.

```
# User detail roster
liongard_metric EVALUATE systemId=<SYS_ID> environmentId=<ENV_ID>
  jmesPathQuery="Users[*].{
    username: username,
    email: email,
    name: displayName_r,
    sudo: sudo,
    activated: activated,
    suspended: suspended,
    mfa: enable_user_portal_multifactor,
    locked: account_locked,
    pwNeverExpires: password_never_expires
  }"
```

Cross-reference with the reconciled identity inventory:
```
liongard_identity LIST environmentId=<ENV_ID>
  fields=["username","displayName","privileged","mfaStatus","enabled","lastLogin","inspectors"]
# Filter client-side: inspectors contains 'jumpcloud-inspector'
```

### Step 4 — MFA posture

```
liongard_metric EVALUATE jmesPathQuery="length(Users[?enable_user_portal_multifactor == `true`])" systemId=<SYS_ID> environmentId=<ENV_ID>

# Admins without MFA — Critical finding
liongard_metric EVALUATE systemId=<SYS_ID> environmentId=<ENV_ID>
  jmesPathQuery="Users[?sudo == `true` && enable_user_portal_multifactor != `true`].{username: username, email: email}"
```

> **Field note — MFA flags:** `enable_user_portal_multifactor` = user portal MFA (the primary flag to check). `totp_enabled` = TOTP specifically (subset). An admin with `enable_user_portal_multifactor == false` has no MFA on console access — Critical.

Compute coverage: `mfaCount / totalUsers * 100`. Compare against `slas.mfa_coverage_pct_min`.

### Step 5 — Admin / privileged audit

```
liongard_metric EVALUATE jmesPathQuery="length(Users[?sudo == `true`])" systemId=<SYS_ID> environmentId=<ENV_ID>

liongard_metric EVALUATE systemId=<SYS_ID> environmentId=<ENV_ID>
  jmesPathQuery="Users[?sudo == `true`].{username: username, email: email, mfa: enable_user_portal_multifactor, activated: activated}"
```

Surface:
- Sudo/admin count > operational minimum (typically ≤ 5)
- Admins with `enable_user_portal_multifactor == false` = Critical
- Service-account-style names (svc-*, sa-*) — confirm intentional

### Step 6 — Device enrollment

```
liongard_metric EVALUATE jmesPathQuery="length(Systems)" systemId=<SYS_ID> environmentId=<ENV_ID>
liongard_metric EVALUATE jmesPathQuery="length(Systems[?active == `true`])" systemId=<SYS_ID> environmentId=<ENV_ID>

liongard_metric EVALUATE systemId=<SYS_ID> environmentId=<ENV_ID>
  jmesPathQuery="Systems[*].{hostname: hostname, os: os, active: active, lastContact: lastContact}"
```

> **Field note:** `active` is a boolean. `os` is a string: `"Windows"`, `"Mac OS X"`, `"Ubuntu"`, etc. `lastContact` is an ISO timestamp.

Cross-reference with the device inventory — JumpCloud-managed devices should appear in the EDR / RMM inventory for full coverage:
```
liongard_device LIST environmentId=<ENV_ID>
  fields=["hostname","operatingSystem","inspectors","lastSeen"]
# Filter client-side: inspectors contains 'jumpcloud-inspector'
```

### Step 7 — SSO application inventory

```
liongard_metric EVALUATE jmesPathQuery="length(Applications.Applications)" systemId=<SYS_ID> environmentId=<ENV_ID>
liongard_metric EVALUATE jmesPathQuery="Applications.Applications[*].name" systemId=<SYS_ID> environmentId=<ENV_ID>
```

> **Data gap:** Per-app user assignments and SSO sign-in volume are not exposed in the dataprint. Orphaned app detection (apps with no users) requires the JumpCloud Admin Console.

### Step 8 — Groups + policies + password policy

```
# Groups
liongard_metric EVALUATE jmesPathQuery="length(Groups)" systemId=<SYS_ID> environmentId=<ENV_ID>
liongard_metric EVALUATE jmesPathQuery="Groups[*].{name: name, type: type}" systemId=<SYS_ID> environmentId=<ENV_ID>

# Policies
liongard_metric EVALUATE jmesPathQuery="length(Policies.Policies)" systemId=<SYS_ID> environmentId=<ENV_ID>
liongard_metric EVALUATE jmesPathQuery="Policies.Policies[*].name" systemId=<SYS_ID> environmentId=<ENV_ID>
```

> **Field note — policy type:** `Policies.Policies[*].type` is null on many systems. Use `name` for policy identification.

```
# Policy failures (catalog metrics — validated IDs)
liongard_metric EVALUATE metricId=1213 systemId=<SYS_ID> environmentId=<ENV_ID>  # Systems with Failed Policies Count
liongard_metric EVALUATE metricId=1214 systemId=<SYS_ID> environmentId=<ENV_ID>  # Systems with Failed Commands Count
liongard_metric EVALUATE metricId=1211 systemId=<SYS_ID> environmentId=<ENV_ID>  # Systems with Failed Policies List
liongard_metric EVALUATE metricId=1212 systemId=<SYS_ID> environmentId=<ENV_ID>  # Systems with Failed Commands List
```

> **Field note — PolicyResults:** `Policies.PolicyResults[*].state` is the status field (`"success"` / `"failed"`). NOT `status`. Filter: `Policies.PolicyResults[?state == 'failed']`.

```
# Password policy (validated — SystemInfo.settings.passwordPolicy is a 22-field object)
liongard_metric EVALUATE jmesPathQuery="SystemInfo.settings.passwordPolicy" systemId=<SYS_ID> environmentId=<ENV_ID>
# Key scalars:
#   .minLength               — integer (e.g. 8)
#   .passwordExpirationInDays — integer (e.g. 90); 0 = no expiry
#   .maxLoginAttempts         — integer (e.g. 6); 0 = no lockout
#   .needsNumeric / .needsSymbolic / .needsUppercase / .needsLowercase — booleans
#   .maxHistory               — integer (password reuse prevention)
```

Evaluate against `slas.password_policy_*` baseline.

### Step 9 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on:
1. Retry persistent nulls.
2. Stale inspector flag.
3. Cross-tool divergence (`jumpcloud.users.totalCount` vs.
   `liongard_identity COUNT` filtered to JumpCloud).
4. Proposed-metric gaps.
5. Identity cross-reference (JumpCloud users vs. M365 / AD when
   both inspectors deployed) for hybrid environments.

### Step 10 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | JumpCloud is a directory + IdP, not an endpoint EDR; the six standard endpoint questions don't apply. Identity equivalents (total users / MFA / privileged / stale) are covered above. |
| CIS Controls (v8.1) | ✅ | Maps to CIS 4.7 (default account configuration), 5.1 (account inventory), 5.2 (unique accounts), 5.3 (dormant accounts), 5.4 (admin privilege separation), 6.2 (access-grant process), 6.3 (MFA external), 6.4 (MFA admins), 6.5 (MFA all users). |
| Cyber-insurance domain files | ✅ | Aligns with `domains/auth.md` Q2–Q4 (MFA), Q6–Q7 (MFA scope), Q14–Q17 (admin audit), Q30–Q31 (stale-account hygiene), Q38–Q39 (shared / generic accounts). |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this when JumpCloud is the customer's directory; surfaces user count + MFA % + admin count + device-enrollment % as highlights. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| MFA coverage below SLA | "Enroll <N> remaining users in MFA via JumpCloud's TOTP or WebAuthn." |
| Privileged user without MFA | "URGENT: Enforce MFA on <N> Org Admin / Manager accounts immediately." |
| Excessive Org Admin count | "Reduce Org Admin count from <N> to operational minimum (≤ 5). Move non-admin operators to Manager / Billing roles." |
| Stale enabled users | "Disable <N> users with no login in > <N> days after confirming separation." |
| Unbound device (no user) | "Bind <N> JumpCloud devices to their primary user or decommission." |
| SSO app without users | "<N> SSO integrations have no users assigned. Decommission orphaned apps." |
| Password policy below baseline | "Tighten password policy: min length <baseline>, max age <baseline>, complexity required, reuse history ≥ <N>." |
| Default new-user admin | "Confirm new-user-default-role is set to non-admin. Audit recently-created users for accidental admin grant." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Conditional-access / risk-based policy detail | partial | JumpCloud Admin Console |
| RADIUS server / VPN auth detail | partial | JumpCloud Admin Console |
| Directory-sync (AD-bridge) health | partial | JumpCloud Admin Console |
| Per-app SSO sign-in volume | partial | JumpCloud Admin Console |
| Per-device patch posture | not in scope — pair with RMM / EDR inspectors | RMM / EDR consoles |

---

## Verification log

> Validated 2026-05-28 against child system (system A, inspected 2026-03-13, Setup Issue status — historical dataprint used).

```
| Path / Query | Result | Status |
|---|---|---|
| GET_OVERVIEW parent system | Keys: Name, Discovered[], Organizations[] — no identity/device data | VALIDATED — parent has no useful data |
| GET_OVERVIEW child system | Keys: Users[], Systems[], Groups[], Applications, Policies, SystemInfo | VALIDATED — child has full schema |
| length(Users) | 10 (integer) | VALIDATED |
| length(Users[?activated == `true` && suspended != `true`]) | 1 (integer) | VALIDATED |
| length(Users[?suspended == `true`]) | 0 (integer) | VALIDATED |
| length(Users[?sudo == `true`]) | 0 (integer) | VALIDATED — sudo = boolean |
| length(Users[?enable_user_portal_multifactor == `true`]) | 0 (integer) | VALIDATED — MFA flag is boolean |
| length(Users[?account_locked == `true`]) | 0 (integer) | VALIDATED |
| length(Users[?password_never_expires == `true`]) | 0 (integer) | VALIDATED |
| length(Systems) | 4 (integer) | VALIDATED |
| Systems[*].{hostname, os, active, lastContact} | 4 items — active:false, os: "Windows"/"Mac OS X"/"Ubuntu" | VALIDATED |
| length(Groups) | 7 (integer) | VALIDATED |
| length(Applications.Applications) | 1 (integer) | VALIDATED |
| SystemInfo.settings.passwordPolicy | object (22 fields) — minLength:8, complexity required, expiry:90d | VALIDATED |
| SystemInfo.settings.passwordPolicy.minLength | 8 (integer) | VALIDATED |
| Policies.Policies[*].{name, type} | 6 items — type is null on all; use name only | VALIDATED |
| Policies.PolicyResults[*].{id, state, policyID} | 10 items — state:"success"/"failed" (NOT status) | VALIDATED |
| Metric ID 1215 (Locked User Accounts Count) | 0 | VALIDATED — catalog metric resolves on child |
```

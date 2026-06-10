---
name: single-system-onelogin
description: >
  Use this skill when the user wants a single-system analysis of a
  OneLogin tenant — identity inventory, MFA enrollment + factor mix,
  privileged-admin audit, SSO application coverage, policy posture,
  brute-force / suspicious login posture. Trigger phrases: "OneLogin
  review", "OL posture for <customer>", "OneLogin MFA coverage",
  "OneLogin app inventory", "OneLogin admin audit".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_identity"
personas: [soc, technical-alignment-manager, vcio-account-manager]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  # Reconciled 2026-05-29: pruned dangling refs not present in the live dataprint (see internal/proposed-metrics-backlog.md).
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

# Single-System Analysis — OneLogin

> **Inspector:** `onelogin-inspector` (ID 27). Cloud category.
> **One system per OneLogin tenant.** Identity provider / SSO
> platform — typically the customer's anchor for SaaS-application
> SSO + identity lifecycle.
>
> **References:** `reference/inspector-aliases.md` (OL, OneLogin).
> Pairs with `recipes/single-system-analysis/by-inspector/microsoft-365.md`
> and `active-directory.md` for hybrid-identity environments;
> `recipes/system-type-assessment/all-identity-providers.md` for the
> multi-provider rollup.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-onelogin-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  identity_inventory: "Identity Inventory"
  mfa: "MFA Posture"
  admin_audit: "Admin & Privileged-User Audit"
  applications: "Application Inventory"
  policies: "Policy Posture"
  security_events: "Suspicious-Login Surface"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"

slas:
  mfa_coverage_pct_min: 95
  privileged_mfa_required: true
  stale_user_days_max: 90
  shared_account_max: 0
  prohibited_auth_factors: ["sms-otp"]
  preferred_auth_factors: ["onelogin-protect", "webauthn", "yubikey"]
  apps_without_mfa_required_max: 0       # every protected app should require MFA via policy
  excessive_admin_max: 5                 # operational maximum

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

- "OneLogin posture review for <customer>"
- "OneLogin MFA coverage check"
- "OneLogin admin audit"
- "OneLogin app inventory"

Cadence: monthly per customer; quarterly in PBR.

Personas:
- **SOC** (primary — MFA, admin, suspicious-login posture)
- **TAM** (policy posture; bringing customer to MSP standard)
- **vCIO / Account Manager** (license utilization)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the OneLogin tenant) | Yes | `liongard_system LIST query="onelogin"` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="onelogin"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Identity inventory

```
liongard_identity LIST environmentId=<ENV_ID>
                       fields=["username","accountType","privileged","mfaStatus","enabled","lastLogin","inspectors"]
                       filter="inspectors contains 'onelogin-inspector'"

liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative:
#   "onelogin.users.totalCount"
#   "onelogin.users.activeCount"
#   "onelogin.users.suspendedCount"
#   "onelogin.users.lockedCount"
#   "onelogin.users.staleCount"
#   "onelogin.users.byRole"              (Standard / Admin / Super User / etc.)
```

### Step 4 — MFA + auth-factor posture

```
#   "onelogin.users.mfaEnrolledCount"
#   "onelogin.users.mfaCoveragePct"
#   "onelogin.factors.usedDistribution"  (OneLogin Protect / WebAuthn / SMS / Voice / etc.)
#   "onelogin.factors.smsUseCount"
#   "onelogin.factors.webauthnUseCount"
#   "onelogin.factors.yubikeyUseCount"
```

Flag SMS / Voice usage as a remediation finding.

### Step 5 — Admin / privileged audit

```
#   "onelogin.admins.totalCount"
#   "onelogin.admins.byRole"
#   "onelogin.admins.mfaEnforced"
#   "onelogin.admins.delegated"          (delegated-admin scope)
```

Surface:
- Super Users > operational minimum
- Admins without MFA = Critical
- Inactive admins (no login > 90 days) = High

### Step 6 — Application inventory

```
#   "onelogin.applications.totalCount"
#   "onelogin.applications.byType"       (SAML / OIDC / Form-based / etc.)
#   "onelogin.applications.policyAttached"
#   "onelogin.applications.unprotectedCount"
#   "onelogin.applications.byAssignedUserCount"
```

### Step 7 — Policy posture

```
#   "onelogin.policies.totalCount"
#   "onelogin.policies.defaultPolicy"
#   "onelogin.policies.mfaRequired"
#   "onelogin.policies.passwordRules"
#   "onelogin.policies.sessionTimeoutMinutes"
```

### Step 8 — Suspicious-login surface (where exposed)

```
#   "onelogin.events.bruteForceAttemptsCount"   (last 30 days)
#   "onelogin.events.suspiciousIpCount"
#   "onelogin.events.failedLoginCount"
#   "onelogin.events.lockedAccountCount"
```

### Step 9 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on:
1. Retry persistent nulls.
2. Stale inspector flag.
3. Cross-tool divergence (OneLogin user count vs.
   `liongard_identity COUNT` filtered).
4. Proposed-metric gaps.
5. Identity cross-reference for hybrid environments (M365 / AD users
   should also be in OneLogin for SSO).

### Step 10 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | OneLogin is an IdP, not an endpoint EDR; the six standard endpoint questions don't apply. Identity equivalents (total users / MFA / privileged / stale) are covered above. |
| CIS Controls (v8.1) | ✅ | Maps to CIS 5.1, 5.2, 5.3, 5.4, 6.3, 6.4, 6.5 (account inventory, dormant accounts, admin separation, MFA scope). See `recipes/compliance/cyber-insurance/domains/auth.md`. |
| Cyber-insurance domain files | ✅ | Aligns with `domains/auth.md` Q2–Q4 (MFA), Q6–Q7 (MFA scope incl. VPN), Q14–Q17 (admin audit). |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this when OneLogin is deployed; surfaces user count + MFA % + admin count + SSO app count as highlights. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| MFA coverage below SLA | "Enroll <N> users in MFA via OneLogin Protect / WebAuthn." |
| Privileged user without MFA | "URGENT: Enforce MFA on <N> Super User / Admin accounts immediately." |
| SMS / Voice factor in use | "Migrate <N> users from SMS / Voice to OneLogin Protect / WebAuthn." |
| Excessive Super User count | "Reduce Super User count from <N> to operational minimum (≤ <baseline>)." |
| Application without MFA policy | "Bind MFA-required policy to <N> applications." |
| Application without users | "Decommission <N> applications with no assigned users." |
| Brute-force attempts spike | "<N> brute-force attempts observed in last 30 days. Confirm account-lockout policy is in effect; review suspicious-IP list." |
| Stale enabled users | "Disable <N> stale users after confirming separation." |
| Long session timeout | "Reduce session timeout from <N> minutes to <baseline>." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| OneLogin Sandbox vs Production tenant disambiguation | partial | OneLogin Admin Console |
| Risk-based authentication score detail | partial | OneLogin Admin Console |
| RADIUS / VPN auth detail | partial | OneLogin Admin Console |
| Per-app sign-in volume | partial | OneLogin Admin Console |
| SIEM-style event log | partial / external | SIEM |

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | query=<customer> | array<environment> | ok |
| 1 | liongard_system LIST | envId=<ENV_ID> query="onelogin" | array<system> | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3 | liongard_identity LIST + liongard_metric VALUE | envId=<ENV_ID> [filters / metric names/JMESPath queries] | varies | ok per metric |
| 9 | QA pass | per `reference/qa-retry-pattern.md` | varies | ok |
| 10 | render | per `output.format` | <artifact path> | ok |
```

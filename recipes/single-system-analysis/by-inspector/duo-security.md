---
name: single-system-duo-security
description: >
  Use this skill when the user wants a single-system analysis of a Duo
  Security tenant — MFA enrollment coverage, policy posture (allowed
  authentication methods, device-trust posture), bypass-user audit,
  unenrolled user surfacing, application-by-application enforcement.
  Trigger phrases: "Duo review", "Duo MFA report", "Duo posture for
  <customer>", "who's not enrolled in Duo", "Duo bypass user audit",
  "Duo conditional access".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_identity"
personas: [soc, technical-alignment-manager, vcio-account-manager]
output_formats: [markdown, word, pptx, xlsx]
primitives:
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
---

# Single-System Analysis — Duo Security

> **Inspector:** `duo-security-inspector` (ID 47). Apps & Services
> category. **One system per Duo customer account.** Cisco-owned MFA
> platform — often the customer's primary MFA layer in front of M365,
> AD-integrated apps, VPN, and custom SAML applications.
>
> **References:** `reference/inspector-aliases.md` (Duo, Cisco Duo).
> Pairs with `recipes/single-system-analysis/by-inspector/microsoft-365.md`
> and `active-directory.md` for identity-source cross-reference;
> `recipes/system-type-assessment/all-identity-providers.md` for the
> multi-provider rollup.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-duo-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  enrollment: "Enrollment Coverage"
  policy_posture: "Policy Posture"
  bypass_users: "Bypass Users & Exceptions"
  authentication_methods: "Authentication Methods in Use"
  applications: "Protected Applications"
  device_trust: "Device-Trust Posture"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"

slas:
  enrollment_coverage_pct_min: 95
  privileged_enrollment_pct_min: 100
  bypass_user_max: 0                     # any bypass user is a finding
  unenrolled_user_max: 0                 # zero unenrolled active users expected
  prohibited_auth_methods: ["sms"]       # SMS OTP no longer recommended (NIST 800-63B)
  preferred_auth_methods: ["duo-push", "webauthn", "hardware-token"]
  policy_default_action: "deny"          # MSP standard: default deny
  duo_passwordless_enabled: false        # set true if MSP standard

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

- "Duo MFA posture for <customer>"
- "Who isn't enrolled in Duo at <customer>?"
- "Duo bypass user audit"
- "Duo policy review"
- "Are any privileged accounts not in Duo?"

Cadence: monthly per customer; quarterly in the PBR; ad-hoc post-incident.

Personas:
- **SOC** (primary — MFA gap is the most-asked compliance question)
- **TAM** (policy posture; bringing customers to MSP MFA standard)
- **vCIO / Account Manager** (renewal narrative — Duo seat
  utilization, conditional-access upsell)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the Duo tenant) | Yes | `liongard_launchpoint LIST inspectorId=47` |

---

## Locating the right system

Duo uses a **parent/child inspector pattern** when accessed via a Duo MSP account:

| Launchpoint type | Top-level keys | Use for EVALUATE? |
|---|---|---|
| **Parent** (MSP account) | `Discovered[]` — lists managed customer orgs | ❌ No entity data |
| **Child** (customer tenant) | `Users[]`, `Admins[]`, `Groups[]`, `Phones[]`, `Settings`, `BypassCodes[]`, `SystemInfo` | ✅ All EVALUATE calls go here |

**Detection probe:**
```
liongard_launchpoint GET_OVERVIEW systemId=<CANDIDATE> environmentId=<ENV_ID>
```
- Top-level keys include `Discovered[]` → **parent** — skip, find child instead
- Top-level keys include `Users[]` → **child** — proceed with this `systemId`

For standalone Duo accounts (not accessed via MSP panel), there is no parent — use the single system directly.

Document the GET_OVERVIEW result in the verification log.

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_launchpoint LIST inspectorId=47 environmentId=<ENV_ID>
  fields=["id","system","environment","latestInspectionDate","status"]
```

Pick the system with the most recent `latestInspectionDate`. If it's a parent system, find the child for the same customer.

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

Flag if `latestInspectionDate` > 7 days ago (SLA threshold).

### Step 3 — Tenant summary + enrollment metrics

```
liongard_metric EVALUATE jmesPathQuery="Name" systemId=<X> environmentId=<Y>
liongard_metric EVALUATE jmesPathQuery="SystemInfo" systemId=<X> environmentId=<Y>
```

> **Field note — `SystemInfo`:** returns a 4-key object: `{user_count, admin_count, integration_count, telephony_credits_remaining}`. These are pre-aggregated counts.

Enrollment breakdown (validate via `Users[]`):
```
liongard_metric EVALUATE jmesPathQuery="length(Users[?is_enrolled == `true`])" systemId=<X> environmentId=<Y>
liongard_metric EVALUATE jmesPathQuery="length(Users[?is_enrolled == `false`])" systemId=<X> environmentId=<Y>
liongard_metric EVALUATE jmesPathQuery="length(Users[?status == 'bypass'])" systemId=<X> environmentId=<Y>
liongard_metric EVALUATE jmesPathQuery="length(Users[?status == 'locked out'])" systemId=<X> environmentId=<Y>
liongard_metric EVALUATE jmesPathQuery="length(Users[?status == 'disabled'])" systemId=<X> environmentId=<Y>
```

> **Field gotcha — `is_enrolled` is a boolean; `status` is a string.** Use backtick-quoted booleans for `is_enrolled` (`` `true` ``, `` `false` ``) and single-quoted strings for `status` (`'bypass'`, `'locked out'`, `'disabled'`, `'active'`).

> **Field gotcha — null ghost entry in `Users[]`:** Some Duo tenants include one trailing null entry (`{username: null, email: "", status: null, is_enrolled: null}`). The `is_enrolled` boolean filters correctly exclude it; `length(Users)` may count it. Use `SystemInfo.user_count` as the authoritative total.

Compute enrollment coverage %: `enrolled_count / user_count × 100`. No direct field — derive in output.

Full user detail for stale-enrollment analysis:
```
liongard_metric EVALUATE jmesPathQuery="Users[?status != null].{username: username, email: email, status: status, is_enrolled: is_enrolled, last_login: last_login}" systemId=<X> environmentId=<Y>
```

### Step 4 — Policy posture

```
liongard_metric EVALUATE jmesPathQuery="Settings.{sms_enabled: sms_enabled, push_enabled: push_enabled, voice_enabled: voice_enabled, mobile_otp_enabled: mobile_otp_enabled, lockout_threshold: lockout_threshold, lockout_expire_duration: lockout_expire_duration, helpdesk_bypass: helpdesk_bypass, minimum_password_length: minimum_password_length, password_requires_numeric: password_requires_numeric, password_requires_special: password_requires_special, log_retention_days: log_retention_days, inactive_user_expiration: inactive_user_expiration, inactive_admin_expiration: inactive_admin_expiration}" systemId=<X> environmentId=<Y>
```

> **Field gotcha — `lockout_expire_duration` unit is minutes:** Value `7` = 7 minutes. Not hours.

> **Field gotcha — `helpdesk_bypass` is a string enum:** `"allow"` = help desk can issue bypass codes (FINDING). `"allow_with_enrollment"` = limited bypass. `"deny"` = bypass disabled (ideal).

> **Field gotcha — `inactive_user_expiration` = 0 means disabled:** Users are never auto-purged. Flag as a hygiene gap.

For each prohibited method in `slas.prohibited_auth_methods` (default: `["sms"]`), flag if `Settings.sms_enabled == true`.

Check per-group auth method overrides:
```
liongard_metric EVALUATE jmesPathQuery="Groups[*].{name: name, sms_enabled: sms_enabled, push_enabled: push_enabled, voice_enabled: voice_enabled, mobile_otp_enabled: mobile_otp_enabled}" systemId=<X> environmentId=<Y>
```

> **Note — Duo application-level and global policy objects are NOT in the dataprint.** Per-app policy enforcement (e.g., "require Duo Push for VPN") must be confirmed in the Duo Admin Panel → Applications → Policy.

### Step 5 — Bypass / exception audit

```
liongard_metric EVALUATE jmesPathQuery="BypassCodes[*].{user_email: user.email, user_enrolled: user.is_enrolled, expiration: expiration, admin_email: admin_email, reuse_count: reuse_count}" systemId=<X> environmentId=<Y>
liongard_metric EVALUATE jmesPathQuery="Users[?status == 'bypass'].{username: username, email: email, last_login: last_login}" systemId=<X> environmentId=<Y>
```

> **Field gotcha — `reuse_count` is a string, not an integer.** `"0"` = single-use bypass code. Compare with string `"0"` not integer `` `0` ``.

Cross-reference each bypass user against the M365 / AD identity
inventory:

```
liongard_identity LIST environmentId=<ENV_ID>
                       fields=["username","accountType","privileged","mfaStatus","lastLogin","enabled"]
```

Surface bypass users who are:
- Privileged (Critical)
- Currently active (High)
- Unenrolled (`user.is_enrolled == false` in BypassCodes) — bypass is their only auth path (Critical)

### Step 6 — Applications protected

```
liongard_metric EVALUATE jmesPathQuery="SystemInfo.integration_count" systemId=<X> environmentId=<Y>
```

> **Data gap — Duo application details are NOT in the dataprint.** `integration_count` provides the total number of configured integrations only. Application type breakdown (M365, RDP, VPN, Custom-SAML), per-app policy assignment, and unprotected application identification require the Duo Admin Panel → Applications.

### Step 7 — Authentication methods configured + phone inventory

Report which auth methods are **configured** (not usage statistics — those require Duo logs):

```
liongard_metric EVALUATE jmesPathQuery="Settings.{sms_enabled: sms_enabled, push_enabled: push_enabled, voice_enabled: voice_enabled, mobile_otp_enabled: mobile_otp_enabled}" systemId=<X> environmentId=<Y>
liongard_metric EVALUATE jmesPathQuery="length(Phones[?activated == `true`])" systemId=<X> environmentId=<Y>
liongard_metric EVALUATE jmesPathQuery="Phones[*].{model: model, platform: platform, activated: activated, capabilities: capabilities}" systemId=<X> environmentId=<Y>
```

`Phones[].capabilities` returns the method array per device (e.g., `["auto","push","sms","phone","mobile_otp"]`).

> **Data gap — auth method usage statistics are NOT in the dataprint.** Push count, SMS count, WebAuthn use frequency, etc. are authentication log data (Duo Admin Panel → Reports → Authentication Log). The dataprint reflects what is **allowed**, not how often each method is used.

Surface SMS / voice as a remediation finding if enabled (`Settings.sms_enabled == true` or `voice_enabled == true`), per NIST 800-63B guidance.

### Step 8 — Admin audit

```
liongard_metric EVALUATE jmesPathQuery="Admins[*].{name: name, email: email, role: role, status: status, last_login: last_login}" systemId=<X> environmentId=<Y>
```

Flag admins who:
- Have not logged in > 90 days (stale admin)
- Are not enrolled in Duo themselves (cross-reference against `Users[]`)

### Step 9 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on:
1. Retry persistent nulls.
2. Stale inspector flag (> 7 days).
3. **Identity cross-reference completeness** — Duo's `Users[]` should align with M365 / AD; identities in M365 / AD but absent from Duo are unenrolled-user findings.
4. Confirm `SystemInfo.user_count` matches `length(Users[?status != null])` — a divergence indicates a stale dataprint.

### Step 10 — Render output

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | Duo is an MFA layer, not an endpoint EDR; the six standard endpoint questions don't apply. Equivalent identity-coverage questions (total users / MFA-enrolled / privileged / bypass) are covered above. |
| CIS Controls (v8.1) | ✅ | Maps to CIS 5.2 (unique account per user), 5.3 (disable dormant accounts), 6.3 (require MFA externally-exposed apps), 6.4 (require MFA admins), 6.5 (require MFA all users). See `recipes/compliance/cyber-insurance/domains/auth.md`. |
| Cyber-insurance domain files | ✅ | Aligns with `domains/auth.md` Q2–Q4 (MFA coverage), Q6 (MFA for privileged), Q7 (MFA for VPN / remote access), Q14–Q17 (admin audit). |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this when Duo is deployed; surfaces enrollment % + privileged MFA % + bypass-user count as highlights. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| Enrollment coverage below SLA | "Enroll <N> remaining users in Duo via <enrollment workflow>." |
| Privileged user not enrolled | "URGENT: Enroll <N> privileged users in Duo immediately." |
| Bypass user is privileged | "Remove bypass on <N> privileged accounts. Confirm legitimate use case before re-enabling." |
| SMS auth method allowed | "Disable SMS auth method in Duo policy. Migrate users to Push / WebAuthn." |
| Default policy = Allow | "Switch Duo default policy to Deny. Add explicit Allow rules per application." |
| Application without policy bound | "Bind Duo policy to <N> protected applications." |
| Unenrolled M365 / AD identity | "<N> identities in M365 / AD lack a Duo enrollment. Confirm scope, enroll." |
| Stale enrolled user | "<N> users enrolled but inactive > 90 days. Confirm employment, disable if separated." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Duo Edition (Trial/Standard/Advantage/Business/Beyond) | ❌ Not in dataprint | Duo Admin Panel → Settings → Billing |
| Application / integration detail (type, policy bound, protected status) | ❌ Not in dataprint | Duo Admin Panel → Applications |
| Application-level and global policy objects | ❌ Not in dataprint | Duo Admin Panel → Policies |
| Auth method usage statistics (push count, SMS count, WebAuthn frequency) | ❌ Not in dataprint | Duo Admin Panel → Reports → Authentication Log |
| Device-trust / trusted-endpoint configuration | ❌ Not in dataprint | Duo Admin Panel → Device Trust |
| Location-aware / geo-block policy | ❌ Not in dataprint | Duo Admin Panel → Policies → Location-Aware |
| Per-app sign-in volume | ❌ Not in dataprint | Duo Admin Panel → Reports |
| Hardware-token inventory (U2fTokens, Tokens) | `Tokens` and `U2fTokens` keys present; `Tokens` empty on test system | `Tokens[*]` / `U2fTokens[*]` — SCHEMA_CONFIRMED |
| Authentication-event audit log | ❌ Not in dataprint | Duo Admin Panel + SIEM |

---

## Verification log

Validated against System A (child, env: demo environment, last inspected: 2026-05-18, status: Completed).
Parent/child pattern confirmed via GET_OVERVIEW: System B (parent, same env) has `Discovered[]` at top level and no entity data.

| Path / Query | System | Result | Status |
|---|---|---|---|
| GET_OVERVIEW top-level keys | System A (child) | `Users[]`, `Admins[]`, `Groups[]`, `Phones[]`, `Settings`, `BypassCodes[]`, `SystemInfo`, `Name`, `Tokens`, `U2fTokens`, `Endpoints` | VALIDATED |
| `Name` | System A | `"<string>"` (tenant display name string) | VALIDATED |
| `SystemInfo` | System A | `{user_count: 17, admin_count: 2, integration_count: 16, telephony_credits_remaining: 0}` (4-key object) | VALIDATED |
| `length(Users)` | System A | `17` (integer) — note: includes 1 null ghost entry | VALIDATED |
| `length(Users[?is_enrolled == \`true\`])` | System A | `14` (integer) | VALIDATED |
| `length(Users[?is_enrolled == \`false\`])` | System A | `2` (integer) | VALIDATED |
| `length(Users[?status == 'bypass'])` | System A | `0` (integer) — no bypass users on test system | SCHEMA_CONFIRMED |
| `length(Users[?status == 'locked out'])` | System A | `0` (integer) — no locked-out users on test system | SCHEMA_CONFIRMED |
| `length(Users[?status == 'disabled'])` | System A | `0` (integer) — no disabled users on test system | SCHEMA_CONFIRMED |
| `Users[*].{username, email, status, is_enrolled, last_login}` | System A | 17-item array; 1 null ghost entry (`username: null, email: "", status: null`); status values = `"active"` on all non-null users | VALIDATED |
| `Settings.{sms_enabled, push_enabled, voice_enabled, mobile_otp_enabled, lockout_threshold, lockout_expire_duration, helpdesk_bypass, inactive_user_expiration}` | System A | `{sms_enabled: true, push_enabled: true, voice_enabled: true, mobile_otp_enabled: true, lockout_threshold: 10, lockout_expire_duration: 7, helpdesk_bypass: "allow", inactive_user_expiration: 0}` | VALIDATED |
| `Settings.{minimum_password_length, password_requires_numeric, password_requires_special, log_retention_days}` | System A | `{minimum_password_length: 6, password_requires_numeric: false, password_requires_special: false, log_retention_days: 30}` | VALIDATED |
| `length(BypassCodes)` | System A | `1` (integer) | VALIDATED |
| `BypassCodes[*].{user_email: user.email, user_enrolled: user.is_enrolled, expiration, admin_email, reuse_count}` | System A | 1-item array; `user.email` sub-path works; `reuse_count: "0"` is a **string** not integer; `expiration: "2029-01-19"` date string | VALIDATED |
| `Admins[*].{name, email, role, status, last_login}` | System A | 2 admins, role: "Owner", status: "Active" | VALIDATED |
| `Groups[*].{name, status, push_enabled, sms_enabled, voice_enabled, mobile_otp_enabled}` | System A | 3 groups; per-group auth method flags all boolean | VALIDATED |
| `length(Phones)` | System A | `12` (integer) | VALIDATED |
| `Phones[0].{type, model, platform, activated, capabilities}` | System A | `{type: "Mobile", model: "Apple iPhone 15", platform: "Apple iOS", activated: true, capabilities: ["auto","push","sms","phone","mobile_otp"]}` | VALIDATED |
| `SystemInfo.integration_count` | System A | `16` (integer) — count only; no application detail array in dataprint | VALIDATED |

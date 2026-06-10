---
name: single-system-google-workspace
description: >
  Use this skill when the user wants a single-tenant analysis of a
  Google Workspace (GWS) tenant — identity inventory, 2-Step
  Verification posture, super-admin audit, OU structure, group
  hygiene, app-access settings, third-party-app authorization audit,
  security defaults posture, license utilization. Trigger phrases:
  "Google Workspace review", "GWS posture for <customer>", "Google
  Workspace 2SV audit", "Google admin audit", "G Suite review"
  (legacy), "Workspace license utilization".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_identity"
personas: [soc, technical-alignment-manager, vcio-account-manager, accounting-finance]
output_formats: [markdown, word, pptx, xlsx]
primitives:
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
---

# Single-System Analysis — Google Workspace

> **Inspector:** `google-workspace-inspector` (ID 61). Cloud category.
> **One system per Google Workspace tenant.** Formerly G Suite / Google
> Apps; legacy names accepted.
>
> **Identity primacy:** Google Workspace is the **identity layer** for
> the Google ecosystem — analogous to M365's role for the Microsoft
> ecosystem. This inspector covers identity, OUs, groups, app access,
> third-party apps, and tenant-level security settings. **Google Drive
> file-level data lives in the separate `google-drive-inspector`** —
> see `recipes/single-system-analysis/by-inspector/google-drive.md`.
>
> **References:** `reference/inspector-aliases.md` (GWS, Google
> Workspace, G Suite legacy, Google Apps legacy). Pairs with
> `google-drive.md` for the file-share posture and
> `recipes/system-type-assessment/all-identity-providers.md` for
> the multi-IdP rollup.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-google-workspace-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  tenant_identity: "Tenant Identity & SKU Mix"
  users: "User Inventory"
  twostep: "2-Step Verification Posture"
  super_admin: "Super Admin & Privileged-Role Audit"
  ou_structure: "Organizational Unit Structure"
  groups: "Group Hygiene"
  app_access: "App Access (Internal + Third-Party)"
  security_defaults: "Security Defaults & Advanced Protection"
  context_aware: "Context-Aware Access"
  license_utilization: "License Utilization"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 7
  twostep_coverage_pct_min: 95
  super_admin_twostep_required: true
  super_admin_count_max: 5
  super_admin_advanced_protection_required: false   # APP is opt-in; set true if MSP standard
  stale_user_days_max: 90
  shared_account_max: 0
  guest_external_user_review_days_max: 90
  groups_open_membership_max: 0                      # open-to-anyone groups = critical
  groups_external_member_review_required: true
  third_party_app_review_days_max: 180
  third_party_app_unverified_allowed: false          # unverified apps with broad scope = critical
  password_policy_min_length: 14
  password_policy_strength_required: "strong"        # min | strong
  enforce_session_length_hours_max: 14
  enforce_session_length_browser_required: true

reporting_period: { default: "current_state" }

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

- "GWS posture for <customer>"
- "Google Workspace 2SV coverage check"
- "Super-admin audit"
- "Third-party app authorization review"
- "G Suite review" (legacy)
- "Workspace license utilization"
- Identity-provider rollup (chained from `all-identity-providers.md`)

Cadence: monthly per customer; quarterly in PBR.

Personas:
- **SOC** (primary — 2SV, super-admin, third-party app posture)
- **TAM** (policy / OU standards alignment)
- **vCIO / Account Manager** (license utilization, renewal narrative)
- **Accounting / Finance** (SKU rightsizing)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the Google Workspace tenant) | Yes | `liongard_system LIST query="google-workspace"` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="google-workspace"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Tenant identity + SKU mix

```
liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative:
#   "google-workspace.tenant.domain"                  (primary domain)
#   "google-workspace.tenant.customerId"
#   "google-workspace.tenant.skuMix"                  (e.g. Business Standard + Enterprise Standard)
#   "google-workspace.tenant.totalLicensedUsers"
#   "google-workspace.tenant.creationDate"
```

### Step 4 — User inventory (reconciled-first)

```
liongard_identity LIST environmentId=<ENV_ID>
                       fields=["displayName","username","email","accountType","privileged","mfaStatus","enabled","lastLogin","emailLicenses","inspectors"]
                       filter="inspectors contains 'google-workspace-inspector'"

#   "google-workspace.users.totalCount"
#   "google-workspace.users.activeCount"
#   "google-workspace.users.suspendedCount"
#   "google-workspace.users.archivedCount"
#   "google-workspace.users.staleCount"               (no login > stale_user_days_max)
#   "google-workspace.users.byOu"
#   "google-workspace.users.bySku"
#   "google-workspace.users.externalCount"            (guests / external)
```

> **Asset-inventory primacy:** Identity counts come from
> `liongard_identity` deduplicated across IdPs (M365 + AD + GWS + etc.).
> Per-inspector `liongard_metric` calls are for GWS-specific configuration
> the reconciled view doesn't expose.

### Step 5 — 2-Step Verification posture

```
#   "google-workspace.twostep.enforcedCount"
#   "google-workspace.twostep.enrolledCount"
#   "google-workspace.twostep.coveragePct"
#   "google-workspace.twostep.byMethod"                (SMS / TOTP / security key / prompt)
#   "google-workspace.twostep.smsBackupCount"          (less secure)
#   "google-workspace.twostep.securityKeyCount"
#   "google-workspace.twostep.advancedProtectionEnrollmentCount"
```

### Step 6 — Super admin / privileged-role audit

```
#   "google-workspace.admins.superAdminCount"
#   "google-workspace.admins.superAdminList"          (cross-ref to user list)
#   "google-workspace.admins.delegatedAdminCount"
#   "google-workspace.admins.byRole"
#   "google-workspace.admins.adminAlertEnabled"        (alerts on admin role changes)
#   "google-workspace.admins.privilegedTwostepPct"
#   "google-workspace.admins.advancedProtectionEnrollmentCount"
```

> **Super admin 2SV is non-negotiable.** Flag as Critical any super
> admin without 2SV. Advanced Protection Program (security keys only,
> no recovery options) is the MSP-recommended posture for super admins.

### Step 7 — OU structure

```
#   "google-workspace.ous.totalCount"
#   "google-workspace.ous.depth"                       (max nesting depth)
#   "google-workspace.ous.byUserCount"
#   "google-workspace.ous.policyOverrideCount"         (OUs with non-default policies)
#   "google-workspace.ous.emptyCount"
```

### Step 8 — Group hygiene

```
#   "google-workspace.groups.totalCount"
#   "google-workspace.groups.byAccessLevel"            (Public / Team / Announce-only / Restricted)
#   "google-workspace.groups.openMembershipCount"      (anyone in domain can join)
#   "google-workspace.groups.publicCount"              (visible / postable from outside domain)
#   "google-workspace.groups.externalMembersCount"
#   "google-workspace.groups.orphanedCount"            (no owners)
#   "google-workspace.groups.unusedCount"              (no posts > N days)
```

### Step 9 — App access (internal + third-party)

```
#   "google-workspace.appAccess.coreServicesEnabledCount"
#   "google-workspace.appAccess.byServiceStatus"       (per Google service: on / off per OU)
#   "google-workspace.thirdPartyApps.totalCount"
#   "google-workspace.thirdPartyApps.trustedCount"
#   "google-workspace.thirdPartyApps.limitedCount"
#   "google-workspace.thirdPartyApps.blockedCount"
#   "google-workspace.thirdPartyApps.unverifiedCount"
#   "google-workspace.thirdPartyApps.broadScopeCount"  (Drive / Gmail full-access scopes)
#   "google-workspace.thirdPartyApps.installCountByApp"
#   "google-workspace.thirdPartyApps.lastReviewDays"
#   "google-workspace.lessSecureAppAccess.enabled"     (deprecated; should be off)
```

### Step 10 — Security defaults & Advanced Protection

```
#   "google-workspace.security.passwordPolicyMinLength"
#   "google-workspace.security.passwordPolicyStrength"
#   "google-workspace.security.passwordReuse"
#   "google-workspace.security.passwordExpirationDays"
#   "google-workspace.security.sessionLengthHours"
#   "google-workspace.security.sessionWebReauthRequired"
#   "google-workspace.security.recoveryEmailRequired"
#   "google-workspace.security.recoveryPhoneRequired"
#   "google-workspace.security.app.advancedProtectionProgramOptInsCount"
```

### Step 11 — Context-Aware Access

```
#   "google-workspace.cas.enabled"
#   "google-workspace.cas.accessLevelsCount"
#   "google-workspace.cas.assignmentsCount"
#   "google-workspace.cas.policiesByApp"
```

### Step 12 — License utilization

```
#   "google-workspace.licensing.bySkuAssigned"
#   "google-workspace.licensing.bySkuPurchased"
#   "google-workspace.licensing.utilizationPct"
#   "google-workspace.licensing.unusedSeatsCount"
#   "google-workspace.licensing.renewalDate"
```

### Step 13 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on:
1. Retry persistent nulls.
2. Stale inspector flag.
3. **Cross-tool divergence** — GWS user count vs. reconciled `liongard_identity COUNT`.
4. **Super-admin 2SV verification** — manual sanity check on the super-admin list cross-referenced to 2SV enrollment.
5. **Third-party app posture** — confirm `lessSecureAppAccess.enabled` is false; surface any "trusted" apps with broad scope for explicit review.
6. **Federation check** — if GWS is the customer's only IdP, no further routing; if there's both GWS and M365 / AD, surface the federation / SSO topology (typically one is the primary, the other syncs).
7. Proposed-metric gaps.

### Step 14 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | Identity / SaaS, not endpoint. |
| CIS Controls (v8.1) | ✅ | CIS 4.7 (default account configuration), 5.1 / 5.2 / 5.3 / 5.4 (account inventory, unique accounts, dormant, admin separation), 6.3 / 6.4 / 6.5 (2-Step Verification scope), 8.2 / 8.11 (admin audit log retention), 14.6 (DLP — partial via Workspace DLP / context-aware access). |
| Cyber-insurance domain files | ✅ | Aligns with `domains/auth.md` Q2–Q4 (2SV coverage), Q6–Q7 (privileged 2SV), Q14–Q17 (admin audit), Q30–Q31 (stale accounts), Q38–Q39 (shared accounts). Direct equivalent to the M365 recipe's coverage for Google-anchored customers. |
| QBR / quarterly-business-review | ✅ | Chained when GWS is the customer's identity layer; surfaces 2SV %, super-admin count, third-party app posture, license utilization. |
| All Identity Providers rollup | ✅ | `recipes/system-type-assessment/all-identity-providers.md` chains this — GWS becomes a peer of M365 / AD / JumpCloud / OneLogin in the reconciled identity-posture view. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| 2SV coverage below SLA | "Enroll <N> remaining users in 2-Step Verification via Google Authenticator / security key." |
| Super admin without 2SV | "URGENT: <N> super admins lack 2SV. Enforce immediately; recommend security-key 2SV (Advanced Protection Program)." |
| Excessive super admin count | "Reduce super admin count from <N> to operational minimum (<= <baseline>). Use delegated admin roles for scoped admin work." |
| Super admin without Advanced Protection | "<N> super admins not enrolled in Advanced Protection Program. Consider enrolling for security-key-only + tightened recovery." |
| Stale user | "<N> users with no login > <N> days. Confirm separation; suspend / archive." |
| Shared / generic user | "<N> shared / generic accounts (e.g., `info@`, `support@`). Convert to delegated mailboxes / groups." |
| Open-membership group | "URGENT: <N> open-membership groups. Restrict per group-access standards." |
| Public group | "<N> groups publicly visible / postable from outside domain. Restrict." |
| Orphaned group | "<N> groups without active owners. Reassign or archive." |
| Unverified third-party app authorized | "URGENT: <N> unverified third-party apps with broad scope. Review immediately; restrict app-access settings to trusted/limited." |
| Third-party app review overdue | "Third-party app inventory last reviewed > <N> days. Schedule quarterly review." |
| Less Secure App Access enabled | "URGENT: Less Secure App Access enabled. Disable per Google's recommendation; deprecated." |
| Password policy weak | "Tighten password policy: enforce 'strong' strength, min length 14, expiration / reuse history per MSP standard." |
| Long session length | "Session length <N> hours. Reduce per MSP standard; require web reauth." |
| Recovery email / phone missing | "<N> users without recovery info. Add recovery email / phone for account recovery flow." |
| CAS not deployed | "Context-Aware Access not enabled. Configure access levels per device-trust / IP / geo." |
| Excessive unused licenses | "<N> unused / suspended-user licenses. Reclaim seats; right-size SKU mix." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Per-third-party-app sign-in events | partial | Google Admin Audit Logs |
| Per-OU device policy detail | partial | Google Admin Console |
| Vault retention policies | partial | Google Vault Admin |
| Workspace DLP rules / findings | partial | Google Admin DLP |
| Per-user Drive sharing (file-level) | n/a | Use `google-drive.md` recipe |
| Per-admin action audit (admin audit log) | partial | Google Admin Audit Logs |
| Mobile-device management (MDM) detail | partial | Google Admin Mobile / Endpoints |

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST + liongard_system LIST | per inspector | array | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3-12 | liongard_metric VALUE + liongard_identity LIST | envId=<ENV_ID> sysId=<SYS_ID> | varies | ok per metric |
| 13 | QA pass (incl. 2SV verification + third-party app sanity check) | per `reference/qa-retry-pattern.md` | varies | ok |
| 14 | render | per `output.format` | <artifact path> | ok |
```

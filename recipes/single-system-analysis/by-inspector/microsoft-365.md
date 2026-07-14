---
name: single-system-microsoft-365
description: >
  Use this skill when the user wants a single-system analysis of a Microsoft 365
  tenant — Periodic Business Review (PBR), license utilization audit, user/group
  inventory, SharePoint site review, Entra ID identity report, or backup-coverage
  verification (when paired with a SaaS-backup tool). Trigger phrases: "M365 PBR",
  "O365 report", "pull Microsoft 365 / Entra data for <CUSTOMER>", "verify M365
  backup coverage", "license utilization on M365". Produces an artifact in the
  format set in the customization block.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_identity"
personas: [vcio-account-manager, soc, technical-alignment-manager, accounting-finance]
output_formats: [markdown, word, pptx, xlsx]
primitives:
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
---

# Single-System Analysis — Microsoft 365

> **Inspector:** `microsoft-365-inspector` (ID 8). Cloud category. Cloud
> Productivity / Email. **Includes Entra ID / Azure AD identity data** — when a
> user says "Azure AD", "Entra", "AAD", they almost always mean this inspector,
> not the Microsoft Azure (subscription resources) inspector.
>
> **Paired use case — SaaS backup verification.** This recipe also serves as the
> "denominator" for SaaS-backup coverage reporting (Datto SaaS Backup, Cove M365,
> Acronis Cyber Protect, etc.). The M365 inspector tells you what *should* be
> backed up; the backup vendor's portal tells you what *is*.
>
> **References:** `reference/inspector-aliases.md` (M365, O365, Entra, AAD).
> `reference/asset-fields.md` for Identity asset fields (`EmailLicenses`, etc.).

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-microsoft-365-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  tenant: "Tenant Overview"
  identities: "Identity & Access"
  licensing: "Licensing & Cost"
  collaboration: "SharePoint, Teams, OneDrive"
  backup_coverage: "SaaS Backup Coverage"        # only when paired with backup tool
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"

slas:
  mfa_coverage_pct_min: 100        # carriers expect 100% on remote/admin
  inactive_account_days_max: 90    # signInActivity.daysSinceLastSignIn threshold
  license_utilization_pct_max: 95  # flag tenant approaching license cap
  privileged_no_mfa_max: 0

reporting_period:
  default: "current_state"          # M365 is mostly current-state; trends via time-series
```

---

## When to use

- "Pull M365 / O365 / Entra data for <customer>" (PBR)
- "License utilization on the M365 tenant"
- "Identity hygiene review — privileged users, MFA coverage, stale accounts"
- "Verify backup coverage" — paired with the customer's SaaS backup tool
- "What SharePoint sites exist and which are stale?"

Cadence: monthly health check, quarterly PBR.
Personas: vCIO/AM (executive summary, license trend), SOC (identity hygiene), TAM
(deep-dive), Accounting/Finance (license SKU costs and utilization).

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| M365 system ID | Yes | `liongard_system LIST query="microsoft-365"` |
| Reporting period | No | Default per customization |
| Backup vendor (when paired) | No | User input — Datto SaaS Backup, Cove, Acronis, etc. |

---

## Locating the right system

```
liongard_system LIST searchMode=keyword query="microsoft-365" environmentId=<ENV_ID>
```

Single system per tenant. `Organization[0].displayName` returns the tenant display
name (a `<string>`).

---

## Liongard data sources

> **Asset Inventory First, Metric Cross-Check.** For identity questions —
> MFA coverage, privileged users, stale accounts, EmailLicenses distribution — the
> **asset inventory is primary**. The M365 dataprint is the cross-check: it
> exposes Conditional Access policies, Secure Score, mail rules, and other
> tenant-config evidence the asset record doesn't surface.

### Per-vendor data — M365 inspector fields

| Key | Description |
|---|---|
| `Organization` | Tenant metadata: `displayName`, `verifiedDomains`, `onPremisesSyncEnabled`, `onPremisesLastSyncDateTime` |
| `Users` | Array of all Entra ID / Azure AD users: licenses, activity, sync status, MFA flags, ConditionalAccessPolicies |
| `sites` | Array of SharePoint sites (lowercase key — case-sensitive) |
| `Groups` | Array of M365 groups (includes Teams-enabled groups) |
| `Licensing` | Array of license SKUs with consumed/available counts |
| `Domains` | Verified domains |
| `SecureScores` | Microsoft Secure Score data |
| `Contracts` | Partner contracts |
| `MailRules` | Exchange mail rules |
| `ConditionalAccess` (under `Policies`) | Conditional Access policy definitions |

#### User fields (selected)

| Field | Description |
|---|---|
| `displayName` | User display name |
| `userPrincipalName` | UPN (email identifier) |
| `accountEnabled` | Whether account is active |
| `activeLast30Days` | Activity in last 30 days |
| `assignedLicenses` | License assignment array |
| `Assigned_Products` | Friendly product names (e.g., E3, EMS-E3) |
| `onPremisesSyncEnabled` | Synced from on-prem AD |
| `mailNickname` | Exchange alias |
| `Privileged` | "Yes" / "No" — admin role assignment |
| `signInActivity.daysSinceLastSignIn` | Days since last sign-in |
| `passwordPolicies` | Password policy flags (e.g. DisablePasswordExpiration) |
| `ConditionalAccessPolicies` | CA policies applied to this user |
| `perUserMfaState` | Legacy per-user MFA state |

#### SharePoint Site fields

| Field | Description |
|---|---|
| `displayName` | Site name |
| `webUrl` | Site URL |
| `createdDateTime` | Creation date |
| `lastModifiedDateTime` | Last modified |

### Cross-inspector primary — asset inventory

```
liongard_identity LIST environmentId=<ENV_ID> pageSize=200
```

```
# License footprint
Identities | group_by EmailLicenses | count
Identities where EmailLicenses contains "E3"
Identities where EmailLicenses contains "E5"

# MFA coverage
Identities where MfaStatus == "NO" AND Enabled == true

# Privileged + no MFA (highest-risk)
Identities where Privileged == true AND MfaStatus != "YES"

# Stale identities
Identities where AccountActivity in ["Stale","Dormant","Never Used"] AND Enabled == true
```

---

## Metrics and queries

### Tenant metadata

```jmespath
{
  tenantName: Organization[0].displayName,
  domains: Organization[0].verifiedDomains[*].name,
  onPremSync: Organization[0].onPremisesSyncEnabled,
  lastSyncTime: Organization[0].onPremisesLastSyncDateTime
}
```

### Headline counts

| Metric | JMESPath | Result shape |
|---|---|---|
| Active users | `length(Users[?accountEnabled == \`true\`])` | `<integer>` |
| Disabled users | `length(Users[?accountEnabled == \`false\`])` | `<integer>` |
| Privileged users | `length(Users[?Privileged == 'Yes'])` | `<integer>` |
| SharePoint sites | `length(sites)` | `<integer>` |
| M365 groups (Teams proxy) | `length(Groups.ActiveGroups)` | `<integer>` |
| Synced from on-prem | `length(Users[?onPremisesSyncEnabled == \`true\`])` | `<integer>` |

### Licensing

```jmespath
Licensing[*].{
  product: ProductFriendlyName,
  sku: skuPartNumber,
  enabled: prepaidUnits.enabled,
  consumed: consumedUnits,
  unconsumed: UnconsumedUnits_r,
  status: capabilityStatus
}
```

### User inventory (operational)

```jmespath
Users[?accountEnabled == `true`].{
  displayName: displayName,
  upn: userPrincipalName,
  licenses: Assigned_Products,
  activeLast30Days: activeLast30Days,
  onPremSync: onPremisesSyncEnabled,
  privileged: Privileged
}
```

### SharePoint sites

```jmespath
sites[*].{
  name: displayName,
  url: webUrl,
  lastModified: lastModifiedDateTime
}
```

> **Field gotcha:** SharePoint sites key is lowercase `sites` — JMESPath is case-sensitive. `Sites` (capital S) returns null. VALIDATED: System B (2026-05-22, inspectorID=8) returned 18 sites via `length(sites)`.

> **Field gotcha — Groups structure (VALIDATED 2026-05-27):** `Groups` is an
> object (not a flat array). `length(Groups)` returns the number of top-level
> keys on the object (e.g., 2), NOT the group count. Use
> `length(Groups.ActiveGroups)` to count active M365 groups. VALIDATED:
> `length(Groups)` returned 2 on a live tenant; `length(Groups.ActiveGroups)`
> returned the correct member count.

### Conditional Access policies (cyber-insurance evidence)

```jmespath
Policies.ConditionalAccess[?state == 'enabled'].displayName
```

### Onboarding QA — M365 tenant posture

Partner-validated patterns for new-customer onboarding intake (from a partner
onboarding QA mapping). Most map to existing M365 metrics or to the asset
inventory.

| Question | JMESPath / approach | Coverage |
|---|---|---|
| Active mailbox count | `length(Users[?accountEnabled == \`true\`])` (existing pattern) | ✅ |
| Verified domains | `Organization[0].verifiedDomains[*].name` | ✅ |
| Directory sync enabled? | `Organization[0].onPremisesSyncEnabled` | ✅ |
| Last directory sync time | `Organization[0].onPremisesLastSyncDateTime` | ✅ |
| Global Admins (vs. all privileged roles) | `Users[?Privileged == 'Yes' && contains(AssignedRoles, 'Global Administrator')].userPrincipalName` | ⚠️ partial — `Privileged` covers all privileged roles; `AssignedRoles` is an array of role name strings (e.g., `['Global Administrator']`). Use `contains(AssignedRoles, 'Global Administrator')` to narrow to GA specifically. (`directoryRoles` is null — use `AssignedRoles` instead. VALIDATED: System B, 2026-05-22.) |
| License names + counts | `Licensing[*].{ProductFriendlyName: ProductFriendlyName, consumedUnits: consumedUnits, enabled: prepaidUnits.enabled}` | ✅ |
| License *expiration date* per SKU | **Not directly in current dataprint** — partner flagged as (not in current dataprint). Track via tenant subscription metadata (Graph API) or surface via `liongard_identity` `emailLicenses` field for current SKU assignment | ⚠️ partial |

> **Gap flagged by partner audit.** Specific license expiration dates per SKU
> are not in the M365 inspector dataprint today — the consumed/enabled counts
> are available, but not the renewal date. Note this in the **Data Gaps**
> section if the customer's renewal date is required.

### Time-series — scope and trend

```
# Active user count over time (scope creep, headcount tracking)
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="length(Users[?accountEnabled == `true`])"

# SharePoint site growth
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="length(sites)"
```

---

## Insights & recommendations

| Insight | Trigger | Recommended action template |
|---|---|---|
| MFA gap | asset.no_mfa count > 0 | "<N> users have no MFA enrollment — enroll via Conditional Access." |
| Privileged + no MFA | asset.privileged_no_mfa > 0 | "<N> privileged users without MFA — critical, enable today." |
| Stale active accounts | asset.stale_enabled > 0 | "<N> stale accounts still enabled — review for offboarding." |
| License headroom low | `consumedUnits / prepaidUnits.enabled > 0.95` | "Provision <N> additional <SKU> seats." |
| License waste | `unconsumedUnits > N` | "Reclaim <N> <SKU> seats from disabled users." |
| Disabled users still licensed | identities `Enabled == false` AND `EmailLicenses != null` | "Remove <N> licenses from disabled users — true-up savings." |
| AD sync stale | `onPremisesLastSyncDateTime < (today − 1 day)` | "AD Connect sync is stale — investigate connector." |
| New user growth | active users grew >X over period | "User count up <pct>% — review backup seat allocation." |

### Backup coverage verification (paired use case)

When the customer uses Datto SaaS Backup, Cove M365, Acronis, or similar, this
recipe pulls the M365 *denominators*; the backup vendor's portal/API gives the
*numerators*. Surface coverage gaps:

| Vendor metric | M365 denominator | Insight |
|---|---|---|
| OneDrive users protected | `length(Users[?accountEnabled])` | Gap = active users not in vendor's protected list |
| Exchange users protected | `length(Users[?accountEnabled with Exchange license])` | Gap = licensed Exchange users not protected |
| SharePoint sites protected | `length(sites)` | Gap = sites not in vendor's protected list |
| Teams protected | `length(Groups.ActiveGroups[?...Teams filter...])` | Gap = active Teams not protected (filter syntax varies — use portal for exact count) |

The backup-vendor data is **not in Liongard** — supplement from the vendor portal.
Surface this in the **Data Gaps** section.

---

## Data gaps vs. typical PBR slides

| Data point | In Liongard? | Notes |
|---|---|---|
| Active users / license utilization | Yes | This recipe |
| SharePoint sites | Yes | This recipe |
| Conditional Access policies | Yes | `Policies.ConditionalAccess` |
| Secure Score | Yes | `SecureScores` |
| Mail rules audit | Yes | `MailRules` |
| Teams active count | Partial | `Groups.ActiveGroups[]` contains Teams-enabled groups; subtotal requires filter on group type |
| Datto/Cove/Acronis backup status | No | Backup vendor portal |
| Mailbox storage utilization | No | Microsoft Admin Center / Graph API |
| OneDrive storage utilization | No | Microsoft Admin Center / Graph API |
| Microsoft 365 health/incidents | No | Microsoft 365 Admin Center service health |

---

## Output format

Markdown / Word / PowerPoint / Excel per `output.format`. See
`templates/output-block-*.md`. For a finance-oriented license report, prefer
**xlsx** so the per-SKU rows can be sorted and formulas applied.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_system LIST | query="microsoft-365" envId=<ENV_ID> | array<system> | ok |
| 3 | liongard_metric EVALUATE | jmesPath sysId=<SYS_ID> envId=<ENV_ID> | <integer>, <array>, <object> | ok |
| 3a | liongard_metric EVALUATE | jmesPath "length(Groups)" | 2 (object-key count — WRONG) | VALIDATED BUG 2026-05-27: Groups is an object; use length(Groups.ActiveGroups) |
| 3b | liongard_metric EVALUATE | jmesPath "length(Groups.ActiveGroups)" | <integer> correct group count | VALIDATED 2026-05-27 |
| 3c | liongard_metric EVALUATE | jmesPath "Policies.ConditionalAccess[?state == 'enabled'].displayName" | array<string> | VALIDATED 2026-05-27 — top-level ConditionalAccessPolicies is null; correct path is Policies.ConditionalAccess |
| 4 | liongard_identity LIST | envId=<ENV_ID> | array<identity> | ok |
```

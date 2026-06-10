---
name: single-system-slack
description: >
  Use this skill when the user wants a single-tenant analysis of a Slack
  workspace — user inventory, admin audit, 2FA posture, guest/restricted
  user count, channel hygiene (public/private/archived/externally-shared),
  user group inventory. Trigger phrases: "Slack review for <customer>",
  "Slack workspace audit", "Slack 2FA posture", "Slack admin users",
  "externally shared Slack channels", "Slack channel hygiene", "Slack PBR".
  One system per Slack workspace. Produces security-posture and governance
  findings for SOC/TAM review.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_launchpoint, liongard_metric"
personas: [soc, technical-alignment-manager, vcio-account-manager]
output_formats: [markdown, word, xlsx]
primitives:
  # Reconciled 2026-05-29: pruned dangling refs not present in the live dataprint (see internal/proposed-metrics-backlog.md).
  - metrics:slack:active-admin-count
  - metrics:slack:active-users-count
  - metrics:slack:active-users-without-2fa-count
  - metrics:slack:admin-users-count
  - metrics:slack:admin-users-list
  - metrics:slack:archived-channels-count
  - metrics:slack:archived-channels-list
  - metrics:slack:channels-count
  - metrics:slack:deleted-users-count
  - metrics:slack:externally-shared-channels-count
  - metrics:slack:externally-shared-channels-list
  - metrics:slack:guest-users-count
  - metrics:slack:public-channels-count
  - metrics:slack:single-channel-guest-count
  - metrics:slack:users-with-2fa-count
  - metrics:slack:users-without-2fa-count
  - metrics:slack:users-without-2fa-list
---

# Single-System Analysis — Slack

> **Inspector:** `slack-inspector` (ID 66). Cloud / Apps & Services category.
> **One system per Slack workspace.** Connects via Slack API (OAuth) to
> collect workspace identity, user roster with 2FA state, channel inventory,
> externally-shared channel list, and user groups. Requires a Slack admin-
> level OAuth token — connect via Liongard cloud inspector, no agent needed.
>
> **Identity routing note:** Slack user identities reconcile into
> `liongard_identity` via email address. Use the reconciled identity view
> for cross-platform MFA coverage (Slack + M365 + AD + Duo) — the per-
> workspace Slack metrics are best for Slack-specific governance (admin
> audit, channel hygiene, external sharing).
>
> **2FA gotcha:** `has_2fa` is a BOOLEAN field (use backtick `true`/`false`
> in JMESPath, not string `"true"`). The catalog metric 1148 counts ALL users
> without 2FA including deleted accounts and bots. For accurate posture, add
> `deleted == \`false\` && is_bot == \`false\`\` to the filter.
>
> **References:** `reference/inspector-aliases.md` (Slack). Pairs with
> `microsoft-365.md`, `google-workspace.md`, and `duo-security.md` for
> cross-platform identity posture. Feeds `recipes/system-type-assessment/
> all-identity-providers.md` for the identity rollup.

---

## Customize for your MSP

```yaml
output:
  format: markdown              # markdown | word | xlsx
  filename: "<customer>-slack-workspace-review-<YYYY-MM-DD>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Workspace Summary"
  workspace_identity: "Workspace Identity"
  user_inventory: "User Inventory"
  mfa_posture: "2FA / MFA Posture"
  admin_audit: "Admin & Privileged Users"
  guest_users: "Guest & Restricted Users"
  channels: "Channel Inventory & Hygiene"
  external_sharing: "Externally Shared Channels"
  user_groups: "User Groups"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"              # technical | balanced | executive
  reading_level: "manager"

slas:
  two_fa_coverage_pct_min: 100  # 100% for workspaces with sensitive data
  admin_user_count_max: 3       # flag workspaces with more than N admins
  external_sharing_warn: true   # flag any externally shared channels
  inspector_lastseen_days_max: 7

naming:
  client_term: "Client"
  environment_term: "Environment"

qa:
  retry_on_null: true
  retry_on_empty_array: false
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: false
```

---

## When to use

- **Quarterly security review** — 2FA coverage, admin count, externally
  shared channels.
- **Onboarding assessment** — establish baseline user count, admin list,
  and external sharing posture for a new Slack customer.
- **Cyber-insurance / compliance evidence** — 2FA state and admin audit
  support MFA and access-control controls.
- **Offboarding audit** — check for deleted users who retain channel
  memberships or were admins.

---

## Inputs

| Input | How to obtain |
|---|---|
| `environmentId` | `liongard_environment LIST` — find the customer's env ID |
| `systemId` | `liongard_launchpoint LIST inspectorId=66 environmentId=<ENV>` — pick most recent inspection |

---

## Workflow

### Step 1 — Confirm inspection freshness

```
liongard_launchpoint LIST
  inspectorId=66
  environmentId=<ENV_ID>
  fields=["id", "system", "environment", "latestInspectionDate", "status"]
```

If status is "Setup Issue", the API credentials may have expired or the
OAuth app was removed. Document the inspection date and note it in the
manual-verification appendix. A historical dataprint may still exist and
will return valid results for the queries below — confirm the date of the
dataprint and disclose it in the deliverable.

---

### Step 2 — Workspace identity

```
liongard_metric EVALUATE
  jmesPathQuery="SystemInfo"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

**VALIDATED** — Returns `{Team: "<string>", TeamID: "<string>", Domain:
"<string>", EmailDomain: "<string>"}`. (System A, inspected 2025-08-20.)

Report: workspace display name, team ID, primary domain, and email domain.

---

### Step 3 — User inventory

Total active users (non-bot, non-deleted):

```
liongard_metric EVALUATE
  jmesPathQuery="Users[?deleted == `false` && is_bot == `false`] | length(@)"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

Bot users only:

```
liongard_metric EVALUATE
  jmesPathQuery="Users[?is_bot == `true` && deleted == `false`] | length(@)"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

Deleted / deactivated users:

```
liongard_metric EVALUATE
  jmesPathQuery="Users[?deleted == `true`] | length(@)"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

**VALIDATED** — `deleted` and `is_bot` are BOOLEAN fields. Integer count
returned. (System A, 2025-08-20.)

---

### Step 4 — 2FA posture (metricName=`Slack: Users with 2FA Enabled Count` / `Slack: Users without 2FA Enabled Count`)

Users WITH 2FA enabled (active, non-bot only):

```
liongard_metric EVALUATE
  jmesPathQuery="Users[?has_2fa == `true` && deleted == `false` && is_bot == `false`] | length(@)"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

Users WITHOUT 2FA (active, non-bot only):

```
liongard_metric EVALUATE
  jmesPathQuery="Users[?has_2fa == `false` && deleted == `false` && is_bot == `false`] | length(@)"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

Users without 2FA — name and email list:

```
liongard_metric EVALUATE
  jmesPathQuery="Users[?has_2fa == `false` && deleted == `false` && is_bot == `false`].
    join(`, `, [profile.real_name, profile.email])"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

**Gotcha — `has_2fa` is BOOLEAN:** Use backtick syntax (`\`true\``, `\`false\``)
not string syntax (`'true'`, `'false'`). **VALIDATED** (System A returned
integer count correctly, 2025-08-20.)

**Gotcha — `Slack: Users with 2FA Enabled Count` / `Slack: Users without 2FA Enabled Count` include bots and deleted users:** The
above queries extend the catalog metrics with `deleted == \`false\` && is_bot
== \`false\`\` for an accurate active-user posture count. Use the extended
version for security reporting.

Compute coverage: `(with_2fa / total_active) * 100`. Flag if below
`slas.two_fa_coverage_pct_min`.

---

### Step 5 — Admin audit (metricName=`Slack: Admin Users Count` / `Slack: Slack: Admin Users List`)

Admin user count:

```
liongard_metric EVALUATE
  jmesPathQuery="Users[?is_admin == `true` && deleted == `false`] | length(@)"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

Admin user list (name + email):

```
liongard_metric EVALUATE
  jmesPathQuery="Users[?is_admin == `true` && deleted == `false`].
    join(`, `, [profile.real_name, profile.email])"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

Workspace owners (higher privilege than admin):

```
liongard_metric EVALUATE
  jmesPathQuery="Users[?is_owner == `true` && deleted == `false`].
    join(`, `, [profile.real_name, profile.email])"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

**VALIDATED** — `is_admin`, `is_owner`, `is_primary_owner` are BOOLEAN.
(System A, 2025-08-20.)

Flag if admin count exceeds `slas.admin_user_count_max`. Confirm owner
and primary-owner assignments match expected personnel.

---

### Step 6 — Guest & restricted users

Multi-channel guests (`is_restricted`):

```
liongard_metric EVALUATE
  jmesPathQuery="Users[?is_restricted == `true` && deleted == `false`] | length(@)"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

Single-channel guests (`is_ultra_restricted`):

```
liongard_metric EVALUATE
  jmesPathQuery="Users[?is_ultra_restricted == `true` && deleted == `false`] | length(@)"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

**VALIDATED** — both are BOOLEAN. `is_restricted` = multi-channel guest
(can access specific channels); `is_ultra_restricted` = single-channel guest
(Slack Free/Pro only, limited to one channel). (System A, 2025-08-20.)

Confirm all guest accounts are expected and that external contractors or
vendors who no longer work with the client are deactivated.

---

### Step 7 — Channel inventory & hygiene

Total channels:

```
liongard_metric EVALUATE
  jmesPathQuery="Conversations[?is_channel == `true`] | length(@)"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

Public active channels (metricName=`Slack: Public Channels Count`, extended):

```
liongard_metric EVALUATE
  jmesPathQuery="Conversations[?is_channel == `true` && is_private == `false` && is_archived == `false`] | length(@)"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

Private channels:

```
liongard_metric EVALUATE
  jmesPathQuery="Conversations[?is_channel == `true` && is_private == `true` && is_archived == `false`] | length(@)"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

Archived channels (metricName=`Slack: Archived Channels Count`):

```
liongard_metric EVALUATE
  jmesPathQuery="Conversations[?is_channel == `true` && is_archived == `true`] | length(@)"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

**VALIDATED** — `is_channel`, `is_private`, `is_archived`, `is_ext_shared`
are all BOOLEAN. (System A, 2025-08-20.)

---

### Step 8 — Externally shared channels (metricName=`Slack: Externally Shared Channels Count` / `Slack: Externally Shared Channels List`)

Count (metricName=`Slack: Externally Shared Channels Count`):

```
liongard_metric EVALUATE
  jmesPathQuery="Conversations[?is_channel == `true` && is_ext_shared == `true`] | length(@)"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

List of externally shared channel names (metric 1153):

```
liongard_metric EVALUATE
  jmesPathQuery="Conversations[?is_channel == `true` && is_ext_shared == `true`].name"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

**VALIDATED** — filter works correctly; returns integer count and string array
of names. (System A returned 15 externally shared channels, 2025-08-20.)

Flag all externally shared channels when `slas.external_sharing_warn` is
true. Review with the customer — each externally shared channel gives
external users visibility into the channel's content and membership. Confirm
all are intentional business channels (vendor partner, customer support, etc.)
and that deactivated external users have been removed.

---

### Step 9 — User groups

User groups count:

```
liongard_metric EVALUATE
  jmesPathQuery="Groups[?is_usergroup == `true`] | length(@)"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

User groups list (name + handle + user count):

```
liongard_metric EVALUATE
  jmesPathQuery="Groups[?is_usergroup == `true`].{name: name, handle: handle, users: user_count}"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

**VALIDATED** — `is_usergroup` is BOOLEAN; `user_count` is integer.
(System A returned 13 usergroups, 2025-08-20.)

---

### Step 10 — QA pass & manual-verification appendix

Apply the QA retry pattern (`reference/qa-retry-pattern.md`):

- Retry any EVALUATE that returns `null` up to `qa.retry_attempts` times.
- If `latestInspectionDate` is older than `qa.flag_inspector_lastseen_threshold_days`
  days, flag the workspace data as potentially stale.
- Compare active user count from Slack inspector to `liongard_identity COUNT`
  filtered for Slack inspector — flag divergence > `qa.flag_count_divergence_threshold_pct`%.

Build the **Manual verification** appendix:

| Item | Reason | Action |
|---|---|---|
| Admin count > `slas.admin_user_count_max` | More admins than expected | Confirm all admins are current employees with a business need |
| Any user with `is_owner == true` | Owner has highest privilege | Confirm owner is the account's primary business owner |
| Externally shared channels listed | External users can see content | Review channel list with customer; deactivate any stale external invites |
| 2FA coverage below `slas.two_fa_coverage_pct_min` | Users without 2FA | Enforce via Slack admin settings (Enterprise Grid: mandatory 2FA) |
| Deleted user count is high | May have accumulated over time | Review deactivated user list; confirm no sensitive channels still have deactivated members |

---

## Insights & recommendations

| Condition | Finding | Recommendation |
|---|---|---|
| `has_2fa == false` active users exist | **2FA gap — [N] active users without 2FA** | Enforce 2FA workspace-wide in Slack Admin → Authentication. Provide user list. |
| Admin count > `slas.admin_user_count_max` | **Excess admins — [N] workspace admins** | Review admin list; reduce to minimum required. Follow least-privilege. |
| Any `is_owner` other than expected | Unexpected workspace owner | Confirm owner assignment; transfer ownership if person has left the org |
| `is_ext_shared` channels > 0 | **[N] externally shared channels** | Review channel list; remove stale external invites; document business justification for each |
| Guest users present | **[N] guest users** | Confirm all guests are active contractors/vendors; deactivate leavers |
| `deleted` user count is significant | Deactivated accounts accumulate | Confirm no deactivated users retain admin or owner roles |

---

## Data gaps

| Field | Gap type | Alternative |
|---|---|---|
| Per-user last-active timestamp | Not in Slack API v1 user object; Slack Enterprise Grid has analytics APIs | Enterprise Grid: Analytics API; otherwise manual review in Slack Admin |
| DM / private message content | Out of scope — Liongard does not access message content | Slack eDiscovery or Compliance exports for regulated industries |
| Installed Slack apps / integrations | ⚠️ not in dataprint — `Conversations` includes apps but full inventory requires additional API scope | Slack Admin → Installed Apps |
| SSO/SAML configuration status | ⚠️ not in dataprint — requires additional Slack admin API scope | Slack Admin → Authentication |
| Retention policy configuration | ⚠️ not in dataprint | Slack Admin → Message Retention |

---

## Coverage cross-check

| Source | Coverage notes |
|---|---|
| Partner QA matrix | Slack not in partner audit — recipe covers the logical equivalent of the six standard identity questions: total users, active, inactive/deleted, 2FA coverage, admin/privileged, high-risk (external sharing). |
| CIS Controls v8.1 | CIS 5.3 (disable dormant accounts — deleted user check), CIS 6.3 (MFA for all users — 2FA posture), CIS 6.8 (application user list — admin audit). |
| Cyber-insurance domain files | Feeds `domains/auth.md` (MFA state — `has_2fa` coverage) and `domains/governance.md` (user access review — admin + guest audit). |
| QBR recipe | Chain this recipe in QBR Step 8 for "Collaboration Platform" section. Surface 2FA gaps, admin changes, and externally shared channels as QBR highlights. |

---

## Output format

**Default: Markdown** — suitable for TAM security review notes.
**Word**: use for customer-facing Slack security assessment.
**Excel**: use when managing multiple Slack workspaces; one row per workspace
with 2FA coverage %, admin count, external channel count for fleet comparison.

---

## Verification log

| Path / Query | System | Result shape | Status |
|---|---|---|---|
| `SystemInfo` | System A (inspected 2025-08-20) | `{Team: <string>, TeamID: <string>, Domain: <string>, EmailDomain: <string>}` | **VALIDATED** |
| `Users[?is_admin == \`true\`] \| length(@)` | System A | Integer count | **VALIDATED** |
| `Users[?has_2fa == \`false\` && deleted == \`false\` && is_bot == \`false\`] \| length(@)` | System A | Integer count — boolean comparisons confirmed | **VALIDATED** |
| `Users[?deleted == \`false\` && is_bot == \`false\`] \| length(@)` | System A | Integer count | **VALIDATED** |
| `Users[?is_restricted == \`true\` \|\| is_ultra_restricted == \`true\`] \| length(@)` | System A | Integer count — OR compound filter confirmed | **VALIDATED** |
| `Conversations[?is_channel == \`true\` && is_ext_shared == \`true\`] \| length(@)` | System A | Integer count | **VALIDATED** |
| `Conversations[?is_channel == \`true\` && is_private == \`false\` && is_archived == \`false\`] \| length(@)` | System A | Integer count | **VALIDATED** |
| `Groups[?is_usergroup == \`true\`] \| length(@)` | System A | Integer count | **VALIDATED** |
| Per-user last-active timestamp | System A | Not present in user object | **SCHEMA_CONFIRMED — not in dataprint** |
| SSO/SAML configuration | System A | Not in dataprint | **SCHEMA_CONFIRMED — not in dataprint** |

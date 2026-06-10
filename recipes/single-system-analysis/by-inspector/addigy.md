---
name: single-system-addigy-mdm
description: >
  Use this recipe when the user wants a single-system analysis of an Addigy
  macOS MDM account — policy inventory and structure, user role audit, API
  permissions review, and child-system discovery map. Trigger phrases: "Addigy
  MDM report for <customer>", "Addigy policy inventory", "Addigy user audit",
  "Addigy device management review", "macOS MDM posture via Addigy", "Addigy
  child system discovery". Parent/child pattern: one parent per Addigy
  organisation; one child per managed policy / client.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_launchpoint, liongard_metric, liongard_timeline"
inspector_id: 98
inspector_name: "Addigy"
category: MDM
personas: [noc, technical-alignment-manager, vcio-account-manager, accounting-finance]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  - metrics:addigy:device-count
  - metrics:addigy:device-list
  - metrics:addigy:discovered-child-count
  - metrics:addigy:policy-updates-ignored-list
  - metrics:addigy:privileged-user-list
  - metrics:addigy:splashtop-enabled-list
  - metrics:addigy:ssh-enabled-list
  - metrics:addigy:top-level-policy-list
  - metrics:addigy:unique-application-list
  - metrics:addigy:user-list
  - metrics:addigy:vnc-enabled-list
---

# Single-System Analysis — Addigy macOS MDM

> **Inspector:** `addigy-inspector-v2` (ID 98). Apps & Services category.
> **Parent/child pattern.** The parent system (one per Addigy organisation)
> holds the **policy roster**, **user list**, and **API permissions** for the
> MSP's Addigy account. Each Addigy policy generates a corresponding **child**
> launchpoint (auto-discovered via `Discovered[]`) containing per-policy
> device and application data. Addigy is a cloud-based macOS (and iOS) MDM
> platform targeting MSPs and IT teams managing Apple device fleets.
>
> **References:** `reference/inspector-aliases.md` (Addigy, macOS MDM).
> Pairs with `watchman-monitoring.md` for macOS health monitoring, and
> macOS inspector (`macos-inspector`, ID 96) for deeper OS-level signals.
> Use `all-endpoints.md` rollup for cross-platform endpoint posture.

---

## When to use

- "Addigy MDM policy inventory for \<customer\>"
- "Addigy user role and access review"
- "Addigy child system discovery"
- "How many Addigy policies exist for \<customer\>?"
- "Addigy API permission audit"
- "macOS MDM coverage — is Addigy deployed?"
- Onboarding baseline (policy structure); quarterly MDM alignment;
  MSP-standard policy compliance check

Cadence: quarterly for policy and user audits; monthly when onboarding
new clients into Addigy; ad-hoc during toolstack migrations.

Personas:
- **NOC** (Addigy policy deployment status; child-system discovery)
- **TAM / Technical Alignment Manager** (policy structure vs MSP standard;
  user role hygiene; API permission scope review)
- **vCIO / Account Manager** (MDM coverage for macOS fleet; client policy
  accuracy)
- **Accounting / Finance** (client policy count vs contract; seat utilisation)

---

## Customize for your MSP

```yaml
output:
  format: markdown                          # markdown | word | pptx | xlsx
  filename: "<customer>-addigy-mdm-<date>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary:    "Executive Summary"
  account_overview:     "Account Overview"
  policy_inventory:     "Policy Inventory"
  child_discovery:      "Child System Discovery"
  user_audit:           "User Role Audit"
  api_permissions:      "API Permissions"
  per_policy_devices:   "Per-Policy Device Detail (Child Systems)"
  recommendations:      "Recommended Actions"
  data_gaps:            "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"                          # technical | balanced | executive

slas:
  policy_update_ignore_alert: true         # flag policies with ignore_updates == true
  child_discovery_expected: true           # each policy should have a child launchpoint
  user_role_review_days: 90               # flag users not reviewed within 90 days

qa:
  retry_on_null: true
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  surface_proposed_metrics: false
  manual_verification_section_required: true
```

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System / launchpoint ID (Addigy parent) | Yes | `liongard_launchpoint LIST inspectorId=98` |
| Optional: specific policy / client name | No | User prompt — narrows output scope |

---

## Workflow

### Step 1 — Resolve environment + parent system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_launchpoint LIST environmentIds=[<ENV_ID>] inspectorId=98
```

Addigy uses a **parent/child pattern**. The LIST result includes:
- The **parent** system (one per Addigy org) — contains `Policies[]`,
  `Users[]`, `ApiPermissions[]`, `OrganizationID`, `Discovered[]`
- One or more **child** systems (one per Addigy policy) — contain
  `PolicyDetails`, `Devices[]`, `Applications[]`

Run this recipe against the **parent** system for the policy roster and
org-level audit. For per-policy device and application detail, follow
each child launchpoint from `Discovered[]` (see Step 5).

The parent is identified by `parentID == null` and org-level fields such
as `OrganizationID`, `Policies[]`, `Users[]`, and `ApiPermissions[]`.
Children have `parentID` set and a `PolicyDetails` object instead. Do
not evaluate parent metrics against child dataprints, and do not use a
parent dataprint for per-policy device evidence.

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentIds=[<ENV_ID>]
```

The Addigy parent inspector syncs the policy roster and discovers child
systems. Flag the parent inspector last-seen >
`slas.flag_inspector_lastseen_threshold_days` days — newly added policies
or users will not appear until the parent re-inspects.

### Step 3 — Account overview

Use `liongard_metric EVALUATE` for each path below against the selected
**parent** system. These paths were revalidated against Dev MCP Addigy
parent dataprints.

```
liongard_metric EVALUATE environmentId=<ENV_ID> systemId=<PARENT_SYS_ID>
  jmesPathQuery="<path>"

# ── MCP_VALIDATED AGAINST PARENT DATAPRINTS ──────────────────────────

# Organisation ID (Addigy account identifier)
#   OrganizationID
#     → UUID string (e.g. "48ec89d5-d311-408d-b4af-9a826bb0cea7")

# Total policy count (parent only)
#   length(Policies)
#     → integer

# Top-level policies
#   Policies[?parent == null].name
#     → existing metric 67434

# Total user count
#   length(Users)
#     → integer

# User list
#   Users[].name
#     → existing metric 67432

# Privileged user list
#   Users[?addigy_role == 'power' || addigy_role == 'admin' || addigy_role == 'owner'].join(' - ', [name, addigy_role])
#     → existing metric 67433

# Total API permissions granted
#   length(ApiPermissions)
#     → integer (reflects scope of MSP's Addigy API token)
```

### Step 4 — Policy inventory

```
# ── VALIDATED ────────────────────────────────────────────────────────

# Full policy list with settings
#   Policies[].{policyId: policyId,
#               name: name,
#               parent: parent,
#               agent_version: agent_version,
#               ignore_updates: ignore_updates,
#               last_deployed: last_deployed,
#               parent_name_r: parent_name_r}
#
#   policyId          — string (UUID); Addigy's internal policy ID
#   name              — string; policy display name
#                       (typically a client or group name,
#                        e.g. "Client 1", "Client 2")
#   parent            — string (UUID); parent policy ID
#                       (policies are hierarchical — a "Clients" root
#                        policy may contain per-client child policies)
#   agent_version     — string: empty "" = inherit from parent policy;
#                       explicit version = version override
#   ignore_updates    — boolean: false = macOS updates are managed;
#                       true = updates ignored for this policy
#                       *** FLAG: true = policy opted out of updates ***
#   last_deployed     — ISO 8601 timestamp or null;
#                       null = policy was never deployed or has no items
#   parent_name_r     — string; resolved name of the parent policy
#                       (e.g. "Clients")

# Policies with updates ignored
#   Policies[?ignore_updates == `true`].{policyId: policyId, name: name}
#     → array; each entry is a coverage gap (no update management)

# Remote-access policy flags (parent policy roster)
#   Policies[?vnc_settings.enabled == true].name
#     → existing metric 67437
#   Policies[?splashtop_settings.enabled == true].name
#     → existing metric 67438
#   Policies[?ssh_settings.enabled == true].name
#     → existing metric 67439
```

**Policy analysis:**

| Signal | Threshold | Severity |
|---|---|---|
| `ignore_updates == true` | Any policy | Warning — macOS updates are not managed for devices in this policy |
| `last_deployed == null` | Any policy | Info — policy has no deployed items (may be a container policy) |
| Policy count unexpectedly low vs expected client count | Compare to customer list | Warning — client(s) may not have an Addigy policy |

### Step 5 — Child system discovery

```
# ── VALIDATED ────────────────────────────────────────────────────────

# Child systems auto-discovered by this parent
#   Discovered[].{EnvironmentSearch: EnvironmentSearch,
#                 Alias: Alias,
#                 Inspector: Inspector,
#                 Parent: Parent}
#
#   EnvironmentSearch — string; Liongard environment key for this child
#                       (maps to the policy name)
#   Alias             — string; child launchpoint display name
#                       (e.g. "AddigyV2 - Client 1")
#   Inspector         — string; always "addigy-inspector-v2"
#   Parent            — integer; parent launchpoint ID

# Count of discovered child systems (parent only)
#   length(Discovered)
#     → integer
```

**Child discovery reconciliation:**

1. Compare `length(Discovered)` to the expected child-policy count.
   Do **not** blindly compare it to `length(Policies)` because parent /
   container policies can exist without child launchpoints.
2. If a leaf/customer policy has no matching `Discovered[]` entry, the
   parent inspector may be stale or the policy was just created.
3. For each child in `Discovered[]`, run
   `liongard_launchpoint LIST environmentIds=[<CHILD_ENV_ID>]` scoped to the child
   environment to retrieve per-policy device data (see Step 6).

### Step 6 — Per-policy device detail (child systems)

The child-level Addigy system (one per policy) contains:

```
# ── MCP_VALIDATED AGAINST CHILD DATAPRINTS ───────────────────────────
# Evaluate all paths in this section against child systems only
# (`parentID` set). Parent dataprints return null for PolicyDetails,
# Devices[], and Applications[].

# Policy detail for this child
#   PolicyDetails.{policyId: policyId,
#                  name: name,
#                  agent_version: agent_version,
#                  ignore_updates: ignore_updates,
#                  vnc_settings: vnc_settings,
#                  splashtop_settings: splashtop_settings,
#                  ssh_settings: ssh_settings,
#                  system_updates_settings: system_updates_settings}
#
#   vnc_settings.enabled               — boolean; VNC remote access enabled
#   vnc_settings.require_user_permission — boolean; user must approve VNC session
#   splashtop_settings.enabled         — boolean; Splashtop remote access
#   ssh_settings.enabled               — boolean; SSH remote access
#   system_updates_settings.force_update — boolean; force macOS updates
#   system_updates_settings.restart_hard — boolean; hard restart allowed

# Enrolled devices under this policy
#   Devices[]
#     → array of enrolled macOS/iOS devices for this specific policy
#     existing metric 67431: length(Devices)
#     existing metric 67435: Devices[].device_name
#     Validated fields observed on populated child dataprints:
#       device_name, os_version, serial_number, last_online,
#       enrolled_via_dep
#     Fields such as device_id, name, model, supervised may be null in
#     Dev dataprints; do not rely on them without a customer-specific
#     validation pass.

# Device inventory projection
#   Devices[].{device_name: device_name,
#              os_version: os_version,
#              serial_number: serial_number,
#              last_online: last_online,
#              enrolled_via_dep: enrolled_via_dep}

# Deployed applications under this policy
#   Applications[]
#     → array of software items deployed via this Addigy policy
#     existing metric 67436:
#       unique_list(Applications[].join(' ',[name,version]))
```

**Per-policy analysis (when child data is available):**

1. `length(Devices)` / metricName=`Addigy: Device Count` — confirm enrolled device count
   vs expected.
2. `PolicyDetails.vnc_settings.enabled` + `require_user_permission` —
   flag VNC without user-permission requirement as a security finding.
3. `PolicyDetails.ssh_settings.enabled` — flag SSH enabled at policy
   level as an elevated-access finding (confirm with MSP standard).
4. `PolicyDetails.system_updates_settings.force_update` — confirm update
   policy is enforced if `ignore_updates == false`.

### Step 7 — User role audit

```
# ── VALIDATED ────────────────────────────────────────────────────────

# Full user list with role
#   Users[].{orgid: orgid,
#            email: email,
#            addigy_role: addigy_role,
#            name: name}
#
#   orgid       — string (UUID); always equals OrganizationID
#   email       — string; user email address
#   addigy_role — string; confirmed value: "power" (full access)
#                 Other expected roles per Addigy docs: "standard", "read-only"
#   name        — string; display name
```

**User role analysis:**

1. List all users with role and email.
2. Flag any user whose `addigy_role` is unexpected for their function.
3. Cross-reference against known-good user list if available.
4. Note: Addigy does not expose MFA/2FA status in this inspector.
   Use the Addigy console to confirm 2FA enforcement status for each user.

### Step 8 — API permissions review

```
# ── VALIDATED ────────────────────────────────────────────────────────

#   ApiPermissions
#     → array of strings; each entry is an Addigy API permission scope
#       (e.g. "read:devices", "write:policies", "manage:users")
#     length(ApiPermissions) — integer (e.g. 113)
#     NOTE: The full permission list is large; validate actual values
#     against a customer system to identify overly-broad scopes.
```

A large `length(ApiPermissions)` (100+) indicates the API token has very
broad access. Flag for review — the principle of least privilege applies
to MDM API tokens. Surface as a TAM finding with a recommendation to
scope the token to the minimum required permissions.

### Step 9 — QA pass

1. Retry any null results per `reference/qa-retry-pattern.md`.
2. Confirm each expected leaf/customer policy has a matching
   `Discovered[]` child. Avoid simple `length(Policies) ==
   length(Discovered)` because container policies may not produce child
   systems.
3. For child systems with `Devices: Array(0)` — verify against the Addigy
   console whether the policy genuinely has no enrolled devices or if
   child inspection failed.
4. Note nullable child fields (`device_id`, `name`, `model`,
   `supervised`) as manual-verification items if the report needs them.

### Step 10 — Render

Recommended report structure:

| # | Section | Key Content |
|---|---|---|
| 1 | Executive Summary | Policy count, user count, child-system map, update-ignore flags |
| 2 | Account Overview | OrganizationID, policy count, user count, API permission count |
| 3 | Policy Inventory | Table: policy name, parent_name_r, ignore_updates, last_deployed |
| 4 | Child System Discovery | Map: policy → child launchpoint; gap analysis |
| 5 | User Role Audit | Table: name, email, addigy_role |
| 6 | API Permissions | Count; broad-scope flag |
| 7 | Per-Policy Device Detail | For each child: device count, update settings, VNC/SSH flags |
| 8 | Recommended Actions | Prioritised findings |
| 9 | Data Gaps | Manual-verification appendix |

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | Steps 4–5 answer macOS MDM policy coverage and child-system discovery; Step 7 answers MDM admin-user role questions. Device inventory answers available at child-system level (Step 6). |
| CIS Controls (v8.1) | ✅ | CIS 1.1/1.2 (Steps 4–5 — managed policy/device inventory), 5.3 (Step 7 — user roles; Step 8 — API token scope), 7.3/7.4 (Step 4 — ignore_updates flag; child system_updates_settings), 4.6/4.8 (Step 6 child — VNC/SSH remote-access policy review). |
| Cyber-insurance domain files | ✅ | `domains/endpoint.md` — Steps 4–6 MDM policy coverage and device management; `domains/governance.md` — Step 7 user role audit + API token least-privilege as vendor-management evidence. |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this for macOS MDM policy count, update-management posture, and device enrollment coverage. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| `ignore_updates == true` on any policy | "Policy '\<name\>' has macOS update management disabled. Enable update management per MSP standard." |
| Expected leaf policy missing from `Discovered[]` | "Policy '\<name\>' has no child launchpoint. Re-run Addigy parent inspector to trigger child discovery." |
| VNC enabled without user permission | "Policy '\<name\>' enables VNC without requiring user approval. Enforce `require_user_permission: true` per MSP security standard." |
| SSH enabled at policy level | "SSH access enabled for policy '\<name\>'. Confirm this is intentional; limit to admin-only policies if not required broadly." |
| Large API permission count | "Addigy API token has \<N\> permissions — very broad scope. Review and narrow to minimum required for the Liongard integration." |
| No devices in child policy | "Policy '\<name\>' has zero enrolled devices. Verify client onboarding is complete or remove unused policy." |
| User with unexpected broad role | "User \<name\> (\<email\>) has '\<role\>' access. Confirm this is appropriate and documented." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Per-device detail (device name, OS, serial, last online) | ✅ child-system level; metricName=`Addigy: Device List` for device names | Run against each child launchpoint (`Discovered[].EnvironmentSearch`) |
| Device MDM compliance status | ⚠️ partial / field-dependent | Child `Devices[]` sub-fields — validate against live customer |
| Deployed application inventory per policy | ✅ child-system level; metricName=`Addigy: Unique Application List` for unique app list | Child `Applications[]` |
| User MFA / 2FA status | Not in parent dataprint | Addigy console → User Management |
| iOS / iPadOS device enrollment | At child-system level | Child `Devices[]` — platform field |
| Addigy billing / licence utilisation | Not in dataprint | Addigy console → Billing |
| Alert history | Not in dataprint | Addigy console → Alerts |

---

## Verification log

| Step | Tool | Validated Path | Result Shape | Validation Status |
|---|---|---|---|---|
| 3 | liongard_metric EVALUATE | parent `OrganizationID` | UUID string | MCP_VALIDATED |
| 3 | liongard_metric EVALUATE | parent `length(Policies)`, `length(Users)`, `length(ApiPermissions)` | integer | MCP_VALIDATED |
| 3 | liongard_metric EVALUATE | parent metrics metricName=`Addigy: User List`, metricName=`Addigy: Privileged User List`, metricName=`Addigy: Top-Level Policy List` | arrays / strings | MCP_VALIDATED |
| 4 | liongard_metric EVALUATE | parent `Policies[].{policyId, name, parent, agent_version, ignore_updates, last_deployed, parent_name_r}` | array | MCP_VALIDATED |
| 4 | liongard_metric EVALUATE | parent metrics metricName=`Addigy: VNC Enabled List`, metricName=`Addigy: Splashtop Enabled List`, metricName=`Addigy: SSH Enabled List` | arrays | MCP_VALIDATED |
| 5 | liongard_metric EVALUATE | parent `Discovered[].{EnvironmentSearch, Alias, Inspector, Parent}` | array; `Inspector: "addigy-inspector-v2"`, `Parent`: int | MCP_VALIDATED |
| 6 | liongard_metric EVALUATE | child `PolicyDetails`, `Devices[]`, `Applications[]` | object + arrays | MCP_VALIDATED |
| 6 | liongard_metric EVALUATE | child metrics metricName=`Addigy: Device Count`, metricName=`Addigy: Device List`, metricName=`Addigy: Unique Application List` | integer / arrays | MCP_VALIDATED |
| 7 | liongard_metric EVALUATE | parent `Users[].{orgid, email, addigy_role, name}` | array | MCP_VALIDATED |

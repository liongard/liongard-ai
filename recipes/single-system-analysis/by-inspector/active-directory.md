---
name: single-system-active-directory
description: >
  Use this skill when the user wants a single-domain analysis of an
  on-premises Active Directory — Periodic Business Review, password
  policy + account lockout audit, privileged user inventory + group
  membership, stale / disabled account review, default accounts
  posture, EOL workstation roster, DHCP scope inventory. Trigger
  phrases: "AD PBR", "AD review", "pull AD data", "AD password policy
  audit", "AD privileged users", "stale AD accounts", "AD DHCP scopes",
  "Active Directory review for the customer". Distinct from the
  cyber-insurance auth domain file — that one is question-driven for
  insurance evidence; this is operational AD assessment.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_launchpoint, liongard_metric, liongard_identity, liongard_device"
personas: [noc, soc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, pptx, xlsx]
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
---

# Single-System Analysis — Active Directory

> **Inspector:** `active-directory-inspector` (ID 13). Apps & Services
> category, but the target system type is **Directory Service** — on-prem
> AD specifically. **Entra ID / Azure AD identity data lives in
> `microsoft-365-inspector`, not here.**
>
> **References:** `reference/inspector-aliases.md` (AD, ADDS, DC).
> `reference/asset-fields.md` for the `liongard_identity` field map.
> `reference/qa-retry-pattern.md` for QA pass details.


---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-ad-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  domain_identity: "Domain Identity"
  password_policy: "Password Policy & Account Lockout"
  privileged_users: "Privileged User Inventory"
  default_accounts: "Default Accounts (Administrator, Guest)"
  stale_accounts: "Stale, Disabled & Never-Used Accounts"
  computers_eol: "Computer Inventory & EOL Workstations"
  dhcp: "DHCP Scopes"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 1
  password_min_length: 14            # CIS 5.2
  password_history: 24               # CIS standard
  password_max_age_days: 90
  account_lockout_threshold_max: 10
  account_lockout_duration_min: 15   # minutes
  stale_account_days_max: 45         # CIS 5.3
  default_admin_enabled: false
  default_guest_enabled: false

reporting_period: { default: "current_state" }

qa:
  retry_on_null: true
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 1
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: false
  manual_verification_section_required: true
```

---

## When to use

- "Pull AD data for the customer" (PBR or quarterly review)
- "AD password policy audit — does it meet CIS 5.2?"
- "Who's in Domain Admins?"
- "How many stale AD accounts are still enabled?"
- "Are there any never-used AD accounts?"
- "DHCP scope inventory across all sites"
- "Win10 EOL roadmap — which workstations are flagged?"

Personas: NOC (operational state), SOC (privileged + stale-account
audit), vCIO/AM (executive summary, EOL roadmap), TAM (deep dive,
policy compliance).

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| AD system ID | Yes | `liongard_launchpoint LIST inspectorId=13` |
| Reporting period | No | Default per customization |

---

## Locating the right system

```
liongard_launchpoint LIST inspectorId=13 environmentIds=[<ENV_ID>]
```

`Domain.Name` returns the AD domain name. If the customer has
multiple AD forests / domains, each is a separate Liongard system —
select by domain name.


---

## Liongard data sources

> **Asset Inventory First, Metric Cross-Check.** For identity questions
> (privileged users, stale accounts, MFA status, group membership), the
> cross-inspector `liongard_identity` tool is primary — it reconciles
> AD signals with M365, Duo, NinjaOne, etc. The AD inspector dataprint
> is the cross-check + source for **AD-unique fields**: domain password
> policy, account lockout configuration, DHCP scopes, default account
> states, computer inventory.

### Cross-inspector primary — identity inventory

```
liongard_identity LIST environmentId=<ENV_ID>
                       fields=["email","username","displayName","privileged","enabled","mfaStatus","accountActivity","inspectors","lastLogin"]
```

For AD-specific cross-checks:

```
# Privileged identities AD knows about
ad_privileged = identities where privileged == true AND inspectors contains "active-directory-inspector"

# AD identities also reconciled with M365 (typical hybrid setup)
hybrid_identities = identities where inspectors contains both
  "active-directory-inspector" AND "microsoft-365-inspector"

# AD-only privileged accounts (haven't been federated to M365)
ad_only_privileged = ad_privileged where inspectors does not contain "microsoft-365-inspector"

# Stale-but-enabled — strongest offboarding signal
stale_enabled = identities where accountActivity in ["Stale","Dormant","Never Used"]
                                 AND enabled == true
                                 AND inspectors contains "active-directory-inspector"
```

### Per-vendor data — AD dataprint top-level keys

| Key | Description |
|---|---|
| `Domain` | Domain identity — `Name`, `DomainMode`, `DomainModeStr`, FSMO role holders |
| `SystemInfo` | Domain posture summary — `NumPrivilegedUsers`, `PrivilegedUsersStr`, Recycle Bin fields |
| `AccountPolicy` | Domain password + lockout policy (`MinPasswordLength`, `PasswordComplexity`, etc.) |
| `Users` | Domain user account array — `UserActivity`, `LastLogonDate`, `UserStatus`, `memberOf`, `DefaultSystemUser` |
| `Computers` | Domain-joined computer accounts — `Type` (Workstation / Server), OS, `Activity`, `OperatingSystemVersionNum` |
| `DHCP` | DHCP scope inventory (`Serverv4Scopes` array with usage, range, lease detail) |
| `GuestMembers` | Members of the Guests group (should be empty) |
| `DefaultGuestAccountEnabled` | Top-level flag for default Guest account state |

#### Field gotchas (inline notes — not TODO)

- **`AccountPolicy` reflects the default domain policy.** Custom
  **Fine-Grained Password Policies (FGPP)** applied to specific groups
  are NOT in this object — they would require separate inspection. If
  the customer uses FGPP, surface that as a manual-verification item:
  "Customer uses FGPP — confirm per-group policies in
  Active Directory Users and Computers (`dsa.msc`)".
- **`Users[*].UserActivity` is Liongard-synthesized.** Combines
  `LastLogonDate` + cross-inspector signals (e.g., M365 sign-in
  activity, Duo enrollments). Values: `Active`, `Stale`, `Dormant`,
  `Never Used`, `No Activity Found`, `null`. **Prefer this over raw
  `LastLogonDate`** — it's more accurate across replicated DCs (each
  DC has its own `LastLogonDate`; the synthesized field reconciles).
- **`AccountPolicy.AccountLockoutDuration` is in hours (float), NOT minutes.**
  Validated: `0.1666...` = 10 minutes; `0.5` = 30 minutes. To compare against
  a 15-minute SLA, use `AccountLockoutDuration >= 0.25` (0.25 hours = 15 min).
- **`AccountPolicy.lockoutThreshold == 0` means NO lockout enforced** (string
  representation: `AccountLockoutThreshold: "Infinite Bad Logins Allowed"`).
  A value of `0` must be flagged as non-compliant regardless of the ≤10 SLA —
  it means brute force is unlimited. Check: `lockoutThreshold == 0` → FAIL.
- **`Computers[*].MemberOf` is an array of full DN strings**, e.g.
  `"CN=Remote Desktop Users,CN=Builtin,DC=contoso,DC=com"`. JMESPath
  `contains(MemberOf, 'RoarExclude')` checks for exact array element equality
  and will never match a group name substring. `MemberOfStr` is null on
  Computers. Use OS-string-based filters for EOL detection; do not rely on
  group-name exclusion in the Computers filter.
- **EOL workstation detection must use `OperatingSystem` string, not
  `OperatingSystemVersionNum`.** Windows 10 has `OperatingSystemVersionNum: 10`
  — the same integer as Windows 11. The catalog metric 1133 filter
  `OperatingSystemVersionNum < 6.2` only catches pre-Win8 machines and
  **misses Windows 10 entirely**. Use `OperatingSystem.contains(@, 'Windows 10')`
  to correctly identify Win10 machines.

### Cross-inspector device cross-check (for EOL workstation roster)

```
liongard_device LIST environmentId=<ENV_ID> operatingSystem="Windows"
                     fields=["hostname","operatingSystem","osVersion","winElevenReady","inspectors"]
```

```
# Win10 devices that won't upgrade (hardware refresh required)
win10_incompatible = devices where operatingSystem contains "Windows 10"
                                  AND winElevenReady == "Incompatible"

# Cross-check against AD Computers[?EOL] — both should agree
ad_eol_workstations = (from AD metric 1133)
asset_eol_workstations = win10_incompatible

# Divergence = data-quality flag
divergence = ad_eol_workstations symmetric_difference asset_eol_workstations
```

---

## Metrics and queries

### Domain identity

| Metric | JMESPath | Result shape |
|---|---|---|
| Privileged user count | `SystemInfo.NumPrivilegedUsers` | `<integer>` |
| Privileged user list | `SystemInfo.PrivilegedUsersStr` | `<array>` |

### Password policy

| Metric | JMESPath | Compliant when |
|---|---|---|
| Minimum password length | `AccountPolicy.MinPasswordLength` | ≥ `slas.password_min_length` |
| Password complexity | `AccountPolicy.PasswordComplexity` | `true` |
| Maximum password age | `AccountPolicy.MaxPasswordAge` | ≤ `slas.password_max_age_days` (or rotation-free with high entropy + monitoring) |
| Minimum password age | `AccountPolicy.MinPasswordAge` | (prevents rapid rotation back) |
| Password history length | `AccountPolicy.pwdHistoryLength` (metricName=`AD: Password History Length`) | ≥ `slas.password_history` |
| Account policy snapshot | `AccountPolicy` | Full object for reporting |

### Account lockout

| Metric | JMESPath | Compliant when |
|---|---|---|
| Lockout threshold | `AccountPolicy.lockoutThreshold` | 1–10 (`== 0` = no lockout = **FAIL regardless of SLA**) |
| Lockout observation window | `AccountPolicy.AccountLockoutObservationWindow` | ≥ 0.25 hours (15 min) — **field is in hours (float)** |
| Lockout duration | `AccountPolicy.AccountLockoutDuration` | ≥ 0.25 hours (15 min) — **field is in hours (float)** |

**VALIDATED** — System A: `lockoutThreshold: 0` (no lockout), `AccountLockoutDuration: 0.1666...` (10 min), `AccountLockoutThreshold: "Infinite Bad Logins Allowed"`. System B: `AccountLockoutDuration: 0.5` (30 min). Units confirmed as hours.

> **`lockoutThreshold == 0` is always non-compliant.** It means brute force is unlimited. The
> SLA check `≤ 10` passes on 0 — always special-case this: `lockoutThreshold == 0` → flag as
> "No account lockout enforced."

### Default accounts (must be disabled)

| Metric | JMESPath | Compliant when |
|---|---|---|
| Default Administrator enabled | `Users[?CN==\`Administrator\`].Enabled \| [0]` | `false` |
| Default Guest enabled (top-level flag) | `DefaultGuestAccountEnabled` | `false` |
| Guests group member count | `length(GuestMembers)` | `0` |

### Stale / disabled accounts

| Metric | JMESPath | Compliant when |
|---|---|---|
| Stale enabled users count | `Users[?UserActivity==\`Stale\` && DefaultSystemUser==\`false\` && Enabled == \`true\`] | length(@)` | `0` |
| Stale enabled users list | `Users[?UserActivity==\`Stale\` && DefaultSystemUser==\`false\` && Enabled == \`true\`]...` | empty |
| Never-used enabled user count | `Users[?LastLogonDate == \`null\` && DefaultSystemUser == \`false\` && Enabled == \`true\`] | length(@)` | `0` |
| Never-used enabled user list | `Users[?LastLogonDate == \`null\` && DefaultSystemUser == \`false\` && Enabled == \`true\`]...` | empty |
| Disabled users list | `Users[?UserStatus == \`Disabled\`]` | review — offboarding evidence |

### EOL workstations

> ⚠️ **Catalog metrics 1133 / 790 / 791 use `OperatingSystemVersionNum < 6.2`** which only
> catches pre-Windows 8 machines. **Windows 10 has `OperatingSystemVersionNum: 10`** and is
> missed entirely by those catalog metrics. Use the validated queries below instead.

| Metric | JMESPath | Compliant when |
|---|---|---|
| Win10 workstation count (EOL Oct 2025) | `Computers[?OperatingSystem != null && OperatingSystem.contains(@, 'Windows 10') && Type==\`Workstation\` && Enabled==\`true\` && Activity!=\`Stale\`] \| length(@)` | `0` |
| Win10 workstation list | `Computers[?OperatingSystem != null && OperatingSystem.contains(@, 'Windows 10') && Type==\`Workstation\` && Enabled==\`true\` && Activity!=\`Stale\`].{Name: Name, OS: OperatingSystem, Activity: Activity}` | empty |
| Legacy EOL workstations (pre-Win8) | `Computers[?Type==\`Workstation\` && Enabled==\`true\` && Activity!=\`Stale\` && OperatingSystemVersionNum < \`6.2\` && OperatingSystem != null && OperatingSystem.contains(@, 'Windows')] \| length(@)` | `0` |

**VALIDATED** — System A (dev environment): `Computers[?OperatingSystem.contains(@, 'Windows 10') && Type==\`Workstation\` && Enabled==\`true\`]` returned 1 result (one Windows 10 workstation confirmed, `OperatingSystemVersionNum: 10`). Confirms catalog filter `VersionNum < 6.2` would miss this machine.

> **Group exclusion note:** The catalog metric 1133 also filters `contains(MemberOf, 'RoarExclude')`.
> `MemberOf` on Computers is an array of full DN strings — this filter will never match a simple
> group name. There is no `MemberOfStr` field on Computers. Group-based exclusions cannot be
> reliably applied in-query; handle RoarExclude logic in post-processing if required.

### DHCP scopes

| Metric | JMESPath | Compliant when |
|---|---|---|
| DHCP scopes at ≥80% utilization | `DHCP.Serverv4Scopes[?Statistics.PercentageInUse >= \`80\`].Name` | empty |

### MCP-validated additional metrics and manual gaps

The Dev MCP catalog already contains several fields previously treated
as proposed. Keep the remaining manual gaps focused on data that is not
in the AD dataprint.

| Field | Metric / workaround |
|---|---|
| **Reversible encryption flag (critical)** | `jmesPathQuery="AccountPolicy.PasswordReversible"` — should always be `false` |
| Domain name | `jmesPathQuery="Domain.Name"` |
| Account policy domain name (for FGPP scenarios) | Read `AccountPolicy.CanonicalName` |
| Per-scope DHCP name | Client-side `DHCP.Serverv4Scopes[*].Name` |
| Per-scope DHCP range | Client-side `DHCP.Serverv4Scopes[*].ScopeId`, `StartRange`, `EndRange` if present |
| Per-scope DHCP lease duration | Client-side `DHCP.Serverv4Scopes[*].LeaseDuration` if present |
| Per-scope DHCP DNS servers | Client-side option fields under `DHCP.Serverv4Scopes[*]` if present |
| Per-scope DHCP reservations | Client-side reservation fields under `DHCP.Serverv4Scopes[*]` if present |
| Password policy summary | Existing metricName=`Active Directory: Password Policy Summary`; for tabular evidence, evaluate underlying policy metrics individually |

### Time-series — policy drift / stale-account trend

```
# Password policy drift detection (length, complexity, history change?)
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="AccountPolicy.MinPasswordLength"

# Stale-account growth over time
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="Users[?UserActivity==`Stale` && DefaultSystemUser==`false` && Enabled == `true`] | length(@)"
```

---

## QA & Manual Verification

Run the QA pass per `reference/qa-retry-pattern.md` before rendering output:

1. **Retry persistent nulls.** AD metrics commonly return null when the
   DC inspection cycle is mid-run; retry up to `qa.retry_attempts` times.

2. **Flag stale inspector data.** AD inspectors run via WinRM / WMI from
   a Liongard agent — staleness usually indicates an agent-connectivity
   or DC-replication issue. `qa.flag_inspector_lastseen_threshold_days`
   defaults to **1 day** — production AD should be inspected daily.

3. **Cross-tool divergence checks (high value for AD):**

   - **Privileged users:** AD `NumPrivilegedUsers` (metricName=`AD: Privileged Users Count`) vs.
     `liongard_identity COUNT privileged=true` filtered to identities
     with AD in `inspectors[]`. Divergence = M365-only or AD-only
     privileged accounts that the other view doesn't see.
   - **Stale accounts:** AD stale count (metricName=`AD: Stale User Accounts Count`) vs.
     `liongard_identity COUNT accountActivity="Stale"` filtered to AD.
     Divergence = AD-only activity computation differs from cross-inspector
     synthesized accountActivity (the cross-inspector view is
     authoritative).
   - **EOL workstations:** AD EOL workstation metricName=`Active Directory: End of Life Workstations (Excludes Roar Group)` vs.
     `liongard_device LIST` filtered for Win10 + winElevenReady ==
     "Incompatible". Divergence = some EOL devices are not domain-joined
     (or aren't reported back via AD due to inspection lag).

4. **Manual / partial data gaps for this recipe** — surface in the
   manual-verification appendix:
   - Fine-Grained Password Policies (FGPP), trust relationships, and
     GPO inheritance are outside the AD dataprint.
   - Per-scope DHCP detail can vary by dataprint; parse
     `DHCP.Serverv4Scopes[*]` and manually confirm missing option /
     reservation fields.

5. **Manual Verification appendix** — render in the deliverable. Typical
   items for this recipe:
   - **Reversible encryption flag**: confirm [metric 178 not in global catalog]
     (`AccountPolicy.PasswordReversible`) is `false` (critical security
     gap if true).
   - **Fine-Grained Password Policies (FGPP)** if used: enumerate via
     `Get-ADFineGrainedPasswordPolicy` and confirm per-group rules.
   - **Trust relationships** with other domains: not inspected by
     Liongard; confirm via `Get-ADTrust` if multi-forest.
   - **Group Policy Objects (GPOs)**: not enumerated in the dataprint;
     confirm GPO-level password policies via `gpmc.msc` if a specific
     OU has different policy.

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Reversible encryption enabled | `AccountPolicy.PasswordReversible == true` or [metric 178 not in global catalog] returns `true` | "**CRITICAL:** Reversible password encryption is enabled on the domain — passwords are recoverable in cleartext. Disable immediately." |
| Password length below SLA | `AccountPolicy.MinPasswordLength < slas.password_min_length` | "Domain password length is <N>; CIS 5.2 expects ≥<SLA>. Update default domain policy." |
| Password complexity off | `AccountPolicy.PasswordComplexity == false` | "Domain password complexity is disabled — enable in default domain policy." |
| Default Administrator enabled | [metric 1945 not in global catalog] returns `true` | "Built-in Administrator account is enabled — rename and disable; create a separate per-admin elevated account." |
| Default Guest enabled | metricName=`AD: Default Guest Account Enabled` returns `true` | "Built-in Guest account is enabled — disable." |
| Privileged user count high | `SystemInfo.NumPrivilegedUsers > expected_baseline` | "<N> privileged accounts in the domain — review and reduce per least-privilege principle." |
| Stale-but-enabled accounts | metricName=`AD: Stale User Accounts Count` > 0 | "<N> stale accounts still enabled — disable per offboarding process (CIS 5.3 requires disable within 45 days)." |
| Never-used accounts | metricName=`AD: Never Used User Accounts Count` > 0 | "<N> never-used accounts exist — review and remove if they aren't service accounts." |
| EOL workstations | metricName=`Active Directory: End of Life Workstations (Excludes Roar Group)` returns non-empty | "<N> domain-joined workstations on EOL OS — refresh roadmap needed (Win10 EOL October 2025)." |
| DHCP scope near capacity | metricName=`AD: DHCP % In Use Over 80 List` returns non-empty | "<N> DHCP scopes are >80% utilized — plan capacity expansion before exhaustion." |
| No account lockout enforced | `AccountPolicy.lockoutThreshold == 0` | "**Account lockout is disabled** (Infinite Bad Logins Allowed) — enforce a lockout threshold of 5–10 attempts." |
| Lockout threshold too permissive | `AccountPolicy.lockoutThreshold > slas.account_lockout_threshold_max` (and != 0) | "Account lockout threshold is <N> — set to ≤<SLA>." |
| Lockout duration too short | `AccountPolicy.AccountLockoutDuration < 0.25` (< 15 min) | "Lockout duration is <N×60> minutes — set to ≥15 minutes. **Field is in hours; 0.25 = 15 min.**" |
| Stale inspector | `lastSeen > 1 day` | "AD inspector hasn't reported in <N> days — confirm Liongard agent + DC connectivity." |


---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Fine-Grained Password Policies (FGPP) | ❌ not in dataprint | `Get-ADFineGrainedPasswordPolicy` via PowerShell |
| Trust relationships (multi-forest / multi-domain) | ❌ not in dataprint | `Get-ADTrust` via PowerShell |
| Group Policy Objects (GPO) inventory | ❌ not in dataprint | `gpmc.msc` / `Get-GPO` |
| Per-OU policy inheritance | ❌ not in dataprint | `gpmc.msc` |
| Domain Controllers replication health | ❌ not in dataprint | `repadmin` |
| Domain Controllers list | ✅ metricName=`Active Directory: Domain Controllers Count` (catalog entry 176 for DC list absent from global catalog — use DC count metric above) | `Get-ADDomainController` for dispute resolution |
| SPN (Service Principal Name) inventory | ❌ not in dataprint | `setspn -L` per account / `Get-ADUser -Filter * -Properties ServicePrincipalNames` |
| Reversible encryption flag | ✅ [metric 178 not in global catalog] | `Get-ADDefaultDomainPasswordPolicy` for dispute resolution |
| Per-scope DHCP detail | ⚠️ partial — high-utilization list is metricName=`AD: DHCP % In Use Over 80 List`, detail is client-side `DHCP.Serverv4Scopes[*]` | DHCP console / PowerShell |


---

## Output format

Markdown / Word / PowerPoint / Excel per `output.format`. **xlsx** is the
canonical fit for the password-policy-compliance grid + the per-user
stale-account table. **pptx** for the executive overview with the
privileged-user count, stale-account trend, and EOL workstation
roadmap.

---

## Verification log

Validated against two internal dev/demo systems on 2026-05-21:
- **System A** — Windows Server 2025 DC, inspected 2026-05-07
- **System B** — Active Directory Demo environment, inspected 2025-05-13

```
| Path / Query | System | Result | Status |
|---|---|---|---|
| SystemInfo.{NumPrivilegedUsers, PrivilegedUsersStr} | System A | {1, "Administrator"} | VALIDATED |
| AccountPolicy (full object) | System A | 42 fields incl. all policy keys | VALIDATED |
| AccountPolicy.MinPasswordLength | System A | 7 (integer) | VALIDATED |
| AccountPolicy.PasswordComplexity | System A | true (boolean) | VALIDATED |
| AccountPolicy.MaxPasswordAge | System A | 42 (days, integer) | VALIDATED |
| AccountPolicy.pwdHistoryLength | System A | 24 (integer) | VALIDATED |
| AccountPolicy.PasswordReversible | System A | false (boolean) | VALIDATED |
| AccountPolicy.lockoutThreshold | System A | 0 (integer — no lockout) | VALIDATED |
| AccountPolicy.AccountLockoutThreshold | System A | "Infinite Bad Logins Allowed" (string) | VALIDATED |
| AccountPolicy.AccountLockoutDuration | System A / System B | 0.1666.../0.5 (hours float — NOT minutes) | VALIDATED |
| AccountPolicy.AccountLockoutObservationWindow | System A | 0.1666... (hours float) | VALIDATED |
| DefaultGuestAccountEnabled | System A | false (boolean) | VALIDATED |
| length(GuestMembers) | System A | 1 (Guest account) | VALIDATED |
| GuestMembers[0] | System A | {DistinguishedName, Name, ObjectClass, SamAccountName, ObjectGUID} | VALIDATED |
| Users[0] (full object) | System A | 93 fields — see Field gotchas | VALIDATED |
| Users[?CN=='Administrator'].{Enabled, UserStatus} | System A | [{true, "Active"}] | VALIDATED |
| Users[?UserActivity==`Stale` && DefaultSystemUser==`false` && Enabled==`true`] \| length(@) | System A | 0 (no non-default stale users) | VALIDATED |
| Users[?LastLogonDate==`null` && DefaultSystemUser==`false` && Enabled==`true`] \| length(@) | System A | 0 | VALIDATED |
| Users[?UserStatus==`Disabled`].{UserName, UserStatus} | System A | [{Guest, Disabled}, {krbtgt, Disabled}] | VALIDATED |
| Computers[0] (full object) | System A | 65 fields; MemberOf = array of full DNs; MemberOfStr = null | VALIDATED |
| Computers[?Type==`Workstation`].{Name, OS, VersionNum, MemberOf} | System B | [{<workstation-hostname>, "Windows 10 Pro", 10, [DN...]}] | VALIDATED |
| Computers[?OperatingSystem.contains(@, 'Windows 10') && Type==`Workstation` && Enabled==`true`] | System B | 1 result — confirms Win10 VersionNum=10 (not <6.2) | VALIDATED |
| Computers[?Type==`Workstation` && Enabled==`true` && OperatingSystemVersionNum < `6.2`] \| length(@) | System A | 0 — confirms catalog filter misses Win10 | VALIDATED |
| OperatingSystem.contains(@, 'Windows') syntax | System B | 6 Windows computers — syntax works | VALIDATED |
| DHCP.Serverv4Scopes[0] | System A, B, C, D | null across all test systems (DHCP not on DC in lab) | SCHEMA_CONFIRMED |
```

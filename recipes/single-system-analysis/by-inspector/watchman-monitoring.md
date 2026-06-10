---
name: single-system-watchman-monitoring
description: >
  Use this recipe when the user wants a single-system analysis of a Watchman
  Monitoring account — macOS (and Windows) device inventory, missing/unreporting
  machine audit, agent-version drift, software expiration tracking, user 2FA
  posture, group-based device organisation, and OS-version inventory. Trigger
  phrases: "Watchman Monitoring report for <customer>", "Watchman missing
  machines", "Watchman device inventory", "Watchman 2FA audit", "Watchman
  software expirations", "macOS fleet health via Watchman". One system per
  Watchman Monitoring account; Groups represent logical device groupings.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_launchpoint, liongard_metric, liongard_timeline"
inspector_id: 50
inspector_name: "Watchman Monitoring"
category: RMM
personas: [noc, technical-alignment-manager, vcio-account-manager, accounting-finance]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  - metrics:watchman-monitoring-inspector:computer-count
  - metrics:watchman-monitoring-inspector:expirations-within-30d
  - metrics:watchman-monitoring-inspector:groups-without-contact-email
  - metrics:watchman-monitoring-inspector:issue-machines-count
  - metrics:watchman-monitoring-inspector:missing-machines-count
  - metrics:watchman-monitoring-inspector:systconnfo-account-summary
  - metrics:watchman-monitoring-inspector:users-without-2fa-count
---

# Single-System Analysis — Watchman Monitoring

> **Inspector:** `watchman-monitoring-inspector` (ID 50). Apps & Services
> category. **One system per Watchman Monitoring account.** Watchman
> Monitoring is a macOS-native RMM and health-reporting tool. It monitors
> Mac (and some Windows) devices grouped into client Groups, tracks software
> license expirations (e.g., Backblaze cloud backup, Webroot), and reports
> device health issues via the `has_issue` flag. Notably captures
> **two-factor authentication (TFA) status per Watchman user** — a key
> security posture signal.
>
> **References:** `reference/inspector-aliases.md` (Watchman Monitoring).
> Pairs with macOS inspector (`macos-inspector`, ID 96) and EDR inspector
> recipes for full macOS endpoint posture. Software expirations complement
> the backup and AV posture findings from other recipes.

---

## When to use

- "Watchman Monitoring report for \<customer\>"
- "Which Macs are missing or not reporting in Watchman?"
- "Watchman device inventory audit"
- "Watchman user 2FA posture"
- "Software expiration report from Watchman"
- "Mac OS-version inventory via Watchman"
- "Watchman agent version drift"
- Monthly macOS fleet health review; software-renewal planning; TAM
  macOS alignment assessment; QBR macOS section

Cadence: monthly for operational reviews; quarterly in PBR; ad-hoc for
device-gone-missing triage or software-expiration planning.

Personas:
- **NOC** (primary — missing machines, has_issue flags, agent connectivity)
- **TAM / Technical Alignment Manager** (OS version EOL exposure,
  agent version drift, software expirations, 2FA user posture)
- **vCIO / Account Manager** (QBR macOS section, software renewal cost)
- **Accounting / Finance** (expiring software licenses, seat count vs contract)

---

## Customize for your MSP

```yaml
output:
  format: markdown                          # markdown | word | pptx | xlsx
  filename: "<customer>-watchman-<date>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary:    "Executive Summary"
  device_inventory:     "Device Inventory"
  missing_machines:     "Missing / Not Reporting Machines"
  issue_machines:       "Machines with Active Issues"
  os_inventory:         "OS Version Inventory"
  agent_versions:       "Agent Version Drift"
  user_2fa_posture:     "User 2FA Posture"
  software_expirations: "Software Expirations"
  group_summary:        "Group Summary"
  recommendations:      "Recommended Actions"
  data_gaps:            "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"                          # technical | balanced | executive

slas:
  missing_machines_max: 0                   # any missing == true is a finding
  has_issue_machines_max: 0                 # any has_issue == true is a finding
  tfa_required: true                        # flag users where tfa_status == false
  expiration_warn_days: 30                  # warn for expirations within 30 days
  expiration_critical_days: 7              # critical for expirations within 7 days
  agent_version_max_lag: 1                  # flag agents lagging by > 1 minor version

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
| System / launchpoint ID (Watchman account) | Yes | `liongard_launchpoint LIST inspectorId=50` |
| Optional: specific group name | No | User prompt — narrows output scope |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_launchpoint LIST environmentId=<ENV_ID> inspectorId=50
```

One Watchman account = one system. If multiple accounts exist for the
same environment (unusual), confirm with the user which account to
analyse.

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

Watchman Monitoring data is near-real-time in the Watchman console, but
the Liongard inspector captures a point-in-time snapshot. A stale inspector
(> `slas.flag_inspector_lastseen_threshold_days` days) means missing/issue
status may not reflect the current state. Flag aggressively.

### Step 3 — Account summary

Use `liongard_metric GENERATE_AND_EVALUATE` for each path below.
All paths are **VALIDATED** against System A (dev environment)
(last inspected 2025-06-13; Setup Issue status but dataprint preserved).

```
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  jmesPath="<path>"

# ── VALIDATED ────────────────────────────────────────────────────────

# Account-level summary statistics
#   Systconnfo
#     → object with fields:
#       UserCount              — integer; total Watchman user accounts
#       AdminUserCount         — integer; users with admin or owner role
#       AdminUsersStr          — string; comma-separated list of admin names
#       ComputerCount          — integer; total computers managed (e.g. 35)
#       ExpirationCount        — integer; tracked software expirations
#       ComputersNotReportingStr — string; comma-separated list of
#                                  computer_name values not reporting to
#                                  Watchman
#
#   NOTE: Field is spelled "Systconnfo" (typo in Watchman API) — not
#   "SystemInfo". Use exactly this path.
```

### Step 4 — Device inventory

```
# ── VALIDATED ────────────────────────────────────────────────────────

# Total computer count
#   length(Computers)
#     → integer (e.g. 35)

# Full device list with identity, health, and configuration
#   Computers[].{uid: uid,
#                computer_name: computer_name,
#                platform: platform,
#                os_version: os_version,
#                primary_ip: primary_ip,
#                agent_version: agent_version,
#                missing: missing,
#                has_issue: has_issue,
#                serial_number: serial_number,
#                ram_installed: ram_installed,
#                current_uptime: current_uptime,
#                updates_enabled: updates_enabled,
#                groupName: groupName}
#
#   uid              — string; Watchman's internal computer ID (prefix "c_")
#   computer_name    — string; hostname as reported by Watchman
#   platform         — string: "mac" | "windows"
#                      (Watchman primarily monitors macOS but also supports
#                       Windows agents)
#   os_version       — string; full OS version with build number
#                      (e.g. "OS X 10.14.6 (18G2022)");
#                      parse major version for EOL analysis
#   primary_ip       — string; primary IP address of the machine
#   agent_version    — string; Watchman agent version (e.g. "6.6.8.133")
#   missing          — boolean: true = machine not reporting to Watchman
#                      (agent offline, not checked in);
#                      false = actively reporting
#   has_issue        — boolean: true = Watchman has detected an active issue
#                      on this machine (check Watchman console for issue detail)
#   serial_number    — string; machine serial number (partial — first 6 chars)
#   ram_installed    — string (e.g. "8 GB", "16 GB")
#   current_uptime   — string; human-readable uptime
#                      (e.g. "2 days, 11 hours, 5 minutes")
#   updates_enabled  — boolean: true = macOS Software Update is enabled
#   groupName        — string; the Group this computer belongs to
#                      (maps to Groups[].name)

# Count of missing machines
#   length(Computers[?missing == `true`])
#     → integer; any non-zero is a finding

# Count of machines with active issues
#   length(Computers[?has_issue == `true`])
#     → integer; any non-zero is a finding

# Count of online (reporting) machines
#   length(Computers[?missing == `false`])
```

**Device inventory analysis:**

| Signal | Threshold | Severity |
|---|---|---|
| `missing == true` | Any | Warning — machine not checking in; check Watchman console for last seen time |
| `has_issue == true` | Any | Warning — active issue detected; review issue detail in Watchman console |
| `updates_enabled == false` | Any | Warning — macOS Software Update disabled; patch delivery may be blocked |
| `missing == true AND has_issue == true` | Any | High — machine unreachable with known issue |

### Step 5 — OS version inventory

From `Computers[].os_version`, build an OS version breakdown:

```
# Parse major macOS version from os_version string
# e.g. "OS X 10.14.6 (18G2022)" → "macOS Mojave (10.14)"
#      "OS X 10.11.6 (15G22010)" → "OS X El Capitan (10.11)"
#
# Confirmed OS version patterns in test data:
#   "OS X 10.10.x" → Yosemite (EOL Oct 2017)
#   "OS X 10.11.x" → El Capitan (EOL Sep 2018)
#   "OS X 10.12.x" → Sierra (EOL Oct 2019)
#   "OS X 10.13.x" → High Sierra (EOL Oct 2020)
#   "OS X 10.14.x" → Mojave (EOL Oct 2021)
#   "OS X 10.15.x" → Catalina (EOL Nov 2022)
#   "macOS 11.x"   → Big Sur
#   "macOS 12.x"   → Monterey
#   "macOS 13.x"   → Ventura
#   "macOS 14.x"   → Sonoma
#   "macOS 15.x"   → Sequoia (current as of 2026)
```

Group machines by major OS version. Flag any machine running an EOL
macOS version as a compliance risk — EOL macOS versions no longer receive
security patches from Apple.

### Step 6 — Agent version drift

From `Computers[].agent_version`, identify the most common (current)
agent version and flag any machine running an older version.

```
# Confirmed agent versions in test data:
#   "6.6.8.133" — most current in test (majority of machines)
#   "6.6.7.115" — one version behind
#   "6.6.5.101" — two versions behind
#
# Group by agent_version, count per version.
# Flag machines where version < latest by > slas.agent_version_max_lag minor versions.
```

Agent version drift is a TAM finding — older agents may miss health-check
features or fail to report accurately.

### Step 7 — User 2FA posture

```
# ── VALIDATED ────────────────────────────────────────────────────────

# Full user list with 2FA status
#   Users[].{uid: uid,
#            email: email,
#            role: role,
#            firstname: firstname,
#            lastname: lastname,
#            tfa_status: tfa_status,
#            last_signin: last_signin}
#
#   uid          — string; user ID (prefix "u_")
#   email        — string; user email address
#   role         — string: "owner" | "admin" | "employee"
#   firstname    — string
#   lastname     — string
#   tfa_status   — boolean: true = 2FA enabled; false = 2FA disabled
#                  *** SECURITY FLAG: false = user without 2FA ***
#   last_signin  — Unix timestamp integer; convert to date for display

# Count of users without 2FA
#   length(Users[?tfa_status == `false`])
#     → integer; any non-zero is a Critical finding per slas.tfa_required
```

**2FA posture evaluation:**

| Signal | Threshold | Severity |
|---|---|---|
| `tfa_status == false` (owner role) | Any | Critical — account owner without 2FA |
| `tfa_status == false` (admin role) | Any | Critical — admin without 2FA |
| `tfa_status == false` (employee role) | Any | High — employee without 2FA |
| `last_signin` > 90 days ago | Any | Warning — stale user; review if still active |

Surface all users with `tfa_status == false` by name and role — Watchman
admin accounts are high-value targets (access to all managed Mac devices).

### Step 8 — Software expirations

```
# ── VALIDATED ────────────────────────────────────────────────────────

# Software expiration list
#   Expirations[].{uid: uid,
#                  productName: productName,
#                  manufacturerName: manufacturerName,
#                  computer: computer,
#                  groupName: groupName,
#                  expires_at: expires_at,
#                  daysTillExpiration: daysTillExpiration,
#                  renewable: renewable}
#
#   productName         — string; software product name
#                         (e.g. "Cloud Backup", "webroot")
#   manufacturerName    — string; vendor name
#                         (e.g. "Backblaze", "webroot")
#   computer            — string; uid of the computer this expiration
#                         applies to (correlate with Computers[].uid)
#   groupName           — string; group of the computer
#   expires_at          — Unix timestamp integer; convert to date
#   daysTillExpiration  — integer; days until expiration (0 = expired)
#   renewable           — boolean: true = can be renewed

# Expirations within the warn window
#   Expirations[?daysTillExpiration <= `30`]
#
# Already expired
#   Expirations[?daysTillExpiration == `0`]
```

**Expiration severity tiers:**

| `daysTillExpiration` | Severity |
|---|---|
| 0 | Critical — expired |
| 1–7 (`slas.expiration_critical_days`) | Critical |
| 8–30 (`slas.expiration_warn_days`) | Warning |
| > 30 | Info — note for renewal planning |

Group expirations by `productName` and `manufacturerName` to identify
whether the same product is expiring across multiple machines
(batch renewal opportunity).

### Step 9 — Group summary

```
# ── VALIDATED ────────────────────────────────────────────────────────

# Group list with computer counts
#   Groups[].{uid: uid,
#             name: name,
#             visible_computer_count: visible_computer_count,
#             hidden_computer_count: hidden_computer_count,
#             contact_email: contact_email}
#
#   name                    — string; group name (maps to client / location)
#   visible_computer_count  — integer; computers visible in this group
#   hidden_computer_count   — integer; hidden computers (admin-only view)
#   contact_email           — string or null; group contact email
#                             (null = not configured)
```

The Group summary provides the client/location breakdown of the Watchman
fleet. Groups with `hidden_computer_count > 0` indicate devices marked as
hidden by the MSP; document as a coverage-transparency note.

Groups with `contact_email == null` should be flagged as a configuration
gap — the MSP-standard for Watchman is typically to set a group contact
email for alert routing.

### Step 10 — QA pass

1. Retry any null results per `reference/qa-retry-pattern.md`.
2. Verify `Systconnfo.ComputerCount == length(Computers)` — if they
   differ, the dataprint may be partially stale.
3. Cross-reference `Systconnfo.ComputersNotReportingStr` with
   `Computers[?missing == true][].computer_name` — should match.
4. Correlate `Expirations[].computer` (uid) with `Computers[].uid` to
   get the human-readable `computer_name` for each expiration.
5. Flag any user with `last_signin` > 90 days as a stale-account review
   item.

### Step 11 — Render

Recommended report structure:

| # | Section | Key Content |
|---|---|---|
| 1 | Executive Summary | Computer count, missing count, issue count, 2FA fail count, expiration count |
| 2 | Device Inventory | Table: computer_name, platform, os_version, groupName, missing, has_issue, updates_enabled |
| 3 | Missing / Not Reporting | List: name, group, last known uptime; root-cause triage |
| 4 | Machines with Active Issues | List: name, group; link to Watchman console |
| 5 | OS Version Inventory | Breakdown by macOS version; EOL flags |
| 6 | Agent Version Drift | Version distribution; flag lagging agents |
| 7 | User 2FA Posture | Table: name, email, role, tfa_status; Critical flags |
| 8 | Software Expirations | Table: product, vendor, machine, group, days remaining |
| 9 | Group Summary | Table: group name, visible_count, hidden_count, contact_email |
| 10 | Recommended Actions | Prioritised findings |
| 11 | Data Gaps | Manual-verification appendix |

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | Steps 4–5 answer macOS managed-endpoint inventory and OS-version questions; Step 7 answers admin-account 2FA questions; Step 8 answers software-license / backup-expiration questions. |
| CIS Controls (v8.1) | ✅ | CIS 1.1/1.2 (Steps 3–4 — device inventory), 2.1/2.2 (Step 4 — OS versions; Step 8 — installed software expirations), 5.3/6.5 (Step 7 — user 2FA posture), 7.3/7.4 (Step 5 — OS EOL exposure, update_enabled flag), 10.1 (Step 4 — has_issue as proxy for AV/endpoint health). |
| Cyber-insurance domain files | ✅ | `domains/endpoint.md` — Steps 4–5 device coverage + OS EOL; `domains/auth.md` — Step 7 user 2FA posture; `domains/backup.md` — Step 8 Backblaze/cloud-backup expiration tracking. |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this for macOS device count, missing-machine rate, OS EOL exposure, user 2FA posture, and software-renewal calendar. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| `missing == true` machines | "\<N\> Mac(s) not reporting to Watchman. Last seen in \<ComputersNotReportingStr\>. Investigate Watchman agent service or machine power state." |
| `has_issue == true` machines | "\<N\> Mac(s) have active issues in Watchman. Review issue detail in Watchman console for \<list of names\>." |
| EOL macOS version | "\<N\> Mac(s) running EOL macOS (\<version\>). These no longer receive Apple security patches. Upgrade to current supported macOS." |
| `tfa_status == false` (admin/owner) | "URGENT: Watchman admin \<name\> (\<role\>) has 2FA disabled. Enforce 2FA on all Watchman admin accounts — these have access to all managed devices." |
| `updates_enabled == false` | "\<N\> Mac(s) have macOS Software Update disabled. Remediate update policy in Watchman to ensure patch delivery." |
| Software expiring within warn window | "\<product\> licence expires in \<N\> days on \<N\> machines (\<groups\>). Renew before \<date\>." |
| Software already expired | "EXPIRED: \<product\> on \<machine\> in \<group\> has lapsed. Immediate renewal required." |
| Agent version lag | "Watchman agent \<version\> on \<N\> machines is behind current (\<latest\>). Update agent to ensure accurate health reporting." |
| Groups with `contact_email == null` | "\<N\> groups have no contact email configured. Set group contact for alert routing per MSP standard." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Per-device issue detail (what the issue is) | Not in dataprint | Watchman Monitoring console — Issues dashboard |
| MDM profile / configuration profile status | Not in dataprint | Watchman console or macOS MDM (Addigy, Mosyle, Jamf) |
| Disk space per device | Not in dataprint | Watchman console |
| AV product and status per device | Not in dataprint | EDR inspector (CrowdStrike, SentinelOne, etc.) |
| Patch history per device | Not in dataprint | macOS MDM or Patch Manager |
| Windows device full detail | PARTIAL | Platform "windows" — limited fields; use Windows Server / Workstation inspector for full Windows data |
| Backup job status per device | PARTIAL | Expirations[] tracks backup-licence expiry; actual job status is in backup-vendor inspector |

---

## Verification log

| Step | Tool | Validated Path | Result Shape | Validation Status |
|---|---|---|---|---|
| 3 | liongard_metric EVALUATE | `Systconnfo` | object; `UserCount: 3`, `ComputerCount: 35`, `AdminUserCount: 2`, `ExpirationCount: 9`, `ComputersNotReportingStr`: string | VALIDATED (System A, dev environment, last insp. 2025-06-13) |
| 4 | liongard_metric EVALUATE | `length(Computers)` | integer → 35 | VALIDATED |
| 4 | liongard_metric EVALUATE | `Computers[].{uid, computer_name, platform, os_version, primary_ip, agent_version, missing, has_issue, serial_number, ram_installed, current_uptime, updates_enabled, groupName}` | array(35); `platform: "mac"\|"windows"`, `missing: boolean`, `has_issue: boolean`, `updates_enabled: boolean`, `current_uptime: "2 days, 11 hours, 5 minutes"` | VALIDATED |
| 7 | liongard_metric EVALUATE | `Users[].{uid, email, role, firstname, lastname, tfa_status, last_signin}` | array(5); `role: "admin"\|"owner"\|"employee"`, `tfa_status: boolean`, `last_signin`: Unix timestamp | VALIDATED |
| 8 | liongard_metric EVALUATE | `Expirations[].{uid, productName, manufacturerName, computer, groupName, expires_at, daysTillExpiration, renewable}` | array(9); `productName: "Cloud Backup"\|"webroot"`, `daysTillExpiration: integer` | VALIDATED |
| 9 | liongard_metric EVALUATE | `Groups[].{uid, name, visible_computer_count, hidden_computer_count, contact_email}` | array(11); `contact_email: null` on all test entries | VALIDATED |

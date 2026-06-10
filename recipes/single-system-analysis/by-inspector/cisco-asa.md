---
name: single-system-cisco-asa
description: >
  Use this skill when the user wants a single-firewall analysis of a
  Cisco ASA — Periodic Business Review, ASA software version audit,
  license expiration check, running-vs-startup config drift detection,
  interface inventory, ACL audit, site-to-site VPN review. Trigger
  phrases: "ASA PBR", "Cisco ASA review", "pull ASA data", "ASA license
  check", "ASA config drift", "ASA firewall review". Produces an artifact
  in the format set in the customization block.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, soc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, pptx]
primitives:
  - metrics:cisco-asa:configs-match
  - metrics:cisco-asa:last-config-modified
  - metrics:cisco-asa:licenses-expiring-30d-count
  - metrics:cisco-asa:licenses-expiring-5d-count
  - metrics:cisco-asa:licenses-expiring-5d-list
  - metrics:cisco-asa:model
  - metrics:cisco-asa:running-config
  - metrics:cisco-asa:serial-number
  - metrics:cisco-asa:software-version
---

# Single-System Analysis — Cisco ASA

> **Inspector:** `cisco-asa-inspector` (ID 22). Network category. Firewall.
>
> **References:** `reference/inspector-aliases.md` (ASA, Cisco firewall).
> `reference/asset-fields.md` for asset cross-checks.
> `reference/qa-retry-pattern.md` for QA pass details.


---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-cisco-asa-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  identity: "ASA Identity & Software Version"
  config_drift: "Running vs. Startup Config"
  interfaces: "Interface & Security-Level Inventory"
  acls: "Access Control Lists"
  licensing: "License Status"
  vpn: "Site-to-Site VPN"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 1
  license_expiration_warn_days: 60
  config_drift_allowed: false      # running ≠ startup = drift signal

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

- "Pull Cisco ASA data for the customer"
- "ASA PBR / quarterly review"
- "ASA license check — anything expiring?"
- "ASA config drift — has anything changed since last save?"
- "ASA site-to-site VPN review"

Personas: NOC, SOC, vCIO/AM (lifecycle planning is critical given ASA
EOL), TAM.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Cisco ASA system ID | Yes | `liongard_system LIST query="cisco-asa"` |
| Reporting period | No | Default per customization |

---

## Locating the right system

```
liongard_system LIST searchMode=keyword query="cisco-asa" environmentId=<ENV_ID>
```

`SystemInfo.Hostname` (not in current dataprint — fall back to parsing
`RunningConfig` for the `hostname` line) returns the firewall display
name.

> **Disambiguate from Cisco IOS routers.** That's a separate inspector
> (`cisco-ios-inspector` ID 30). ASA = firewall; IOS = router/switch.


---

## Liongard data sources

> **Asset Inventory First, Metric Cross-Check.** ASA's dataprint is the
> source of truth for the firewall's own configuration. The
> `RunningConfig` is the structural source of truth for many fields the
> partner audit flagged as not in dataprint.

### Per-vendor data — Cisco ASA dataprint top-level keys

| Key | Description |
|---|---|
| `SystemInfo` | ASA identity — model, ASA software version, serial |
| `RunningConfig` | Full running configuration text (CLI-exported) |
| `ConfigMatch` | Boolean — whether running config matches startup config (drift detection) |
| `Licenses` | License feature list with expiration |

#### Field gotchas (inline notes — not TODO)

- **`RunningConfig` is the structural source of truth.** ASA stores its
  full configuration as CLI text. Many fields the partner audit flagged
  as not in dataprint (interfaces, ACLs, local users, SSH config, DHCP) can be
  parsed client-side from this string. The recipe should treat this as
  the structural source of truth until purpose-built metrics ship.
- **`ConfigMatch == false` means a reboot will revert recent changes.**
  ASA configuration changes are not persisted until `write memory` or
  `copy run start` is issued. A drift signal is a strong indicator of
  change-management discipline issues.
- **`RunningConfig` is large (multi-KB CLI text).** Parse selectively —
  don't render in full to the report.

### Cross-inspector cross-check — device inventory

```
liongard_device LIST environmentId=<ENV_ID>
                     fields=["hostname","manufacturer","inspectors","internalIP"]
```

```
managed_devices = devices where category == "compute"
# ASA doesn't enumerate connected devices directly. Cross-check via RMM
# or other inspectors to confirm scope.
```

---

## Metrics and queries

### Identity & version

| Metric | JMESPath | Result shape |
|---|---|---|
| Model | `SystemInfo.Model` | `<string>` |
| ASA software version | `SystemInfo.ASAVersion` | `<string>` |

### Config drift

| Metric | JMESPath | Result shape |
|---|---|---|
| Running config snapshot | `RunningConfig` | `<string>` (multi-KB) |
| Running matches startup | `ConfigMatch` | `<bool>` (compliant when `true`) |

### Licensing

| Metric | JMESPath | Result shape |
|---|---|---|
| Licenses expiring within 30 days | `Licenses[?DaysToExpiry < `30`]` | `<array>` (compliant when empty) |

### Proposed metrics (not yet in Liongard library)

The partner audit identified ASA as a major gap area — most onboarding-QA
fields are not in the current dataprint. Parse from `RunningConfig`:

| Field | Workaround (parse from `RunningConfig`) |
|---|---|
| Hostname | Match `^hostname (.*)$` |
| Per-interface IP / security-level | Parse `interface` blocks |
| Local user accounts | Match `^username` lines |
| SSH management channels | Parse `ssh` config block |
| Active license features | Existing 'Licenses Expiring' is partial — full feature list requires UI |
| Inbound ACL permit rules | Parse `access-list` lines, filter by direction + action |
| DHCP enabled | Parse `dhcpd` block |

### Time-series — drift / license trend

```
# Config drift signal over time (any "false" reading = unsaved changes
# at that inspection point)
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="ConfigMatch"

# License countdown
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="length(Licenses[?DaysToExpiry < `30`])"
```

---

## QA & Manual Verification

Run the QA pass per `reference/qa-retry-pattern.md` before rendering output:

1. **Retry persistent nulls.** Retry up to `qa.retry_attempts` times.

2. **Flag stale inspector data.** ASA inspector lastSeen > 1 day = SSH /
   API access issue.

3. **Cross-tool divergence (when applicable).** Track `ConfigMatch`
   history — repeated drift readings = recurring change-management
   discipline issue.

4. **Proposed-metric gaps for this recipe** — surface these in the
   manual-verification appendix:
   - Hostname (parsed from RunningConfig as a workaround)
   - Per-interface IP / security-level summary
   - Local user accounts
   - SSH management channels
   - Active license feature list (full enumeration)
   - Inbound ACL permit rules
   - DHCP enabled flag

5. **Manual Verification appendix** — render in the deliverable. Typical
   items for this recipe:
   - `ConfigMatch == false` (running config diverged from startup —
     `write memory` not run after a recent change).
   - Local user accounts beyond the expected MSP / customer-admin pair
     (parsed from RunningConfig).
   - Inbound ACL permit-any rules (parsed from RunningConfig).
   - ASA software version older than current ASA train (lifecycle gap).

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Config drift detected | `ConfigMatch == false` | "Running config diverges from startup — issue `write memory` to persist; investigate why drift exists." |
| Licenses expiring | `length(Licenses[?DaysToExpiry < 30]) > 0` | "<N> ASA licenses expiring within 30 days — initiate renewal." |
| ASA EOL planning | per Cisco's published lifecycle | "ASA product line is approaching end-of-engineering-support — plan refresh to Firepower/FTD or alternative vendor." |
| ASA software version old | major version below current Cisco-supported train | "ASA software <version> is old — plan upgrade." |
| WAN management exposed | parsed SSH / HTTPS rules permit WAN | "ASA management exposed on WAN — restrict to admin VLAN or VPN." |
| Stale inspector | `lastSeen > 1 day` | "ASA inspector hasn't reported in <N> days — confirm SSH access." |


---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Traffic / bandwidth analytics | ❌ not in dataprint | Cisco AMP / Firepower analytics |
| AnyConnect VPN session detail | ❌ not in dataprint | ASA UI / `show vpn-sessiondb` |
| FirePower module data (if installed) | ❌ separate inspector | FirePower Management Center |
| Most onboarding-QA fields | ⚠️ not in dataprint metrics | Parse `RunningConfig` client-side |


---

## Output format

Markdown / Word / PowerPoint per `output.format`.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_system LIST | query="cisco-asa" envId=<ENV_ID> | array<system> | ok |
| 3 | liongard_metric EVALUATE | metricName or jmesPathQuery sysId=<SYS_ID> envId=<ENV_ID> | <integer>, <bool>, <array>, <string> | ok per metric |
| 4 | liongard_device LIST | envId=<ENV_ID> fields=[hostname,manufacturer,inspectors,internalIP] | array<device> | ok |
| 5 | (QA pass) retry persistent nulls | per `reference/qa-retry-pattern.md` | varies | ok |
```

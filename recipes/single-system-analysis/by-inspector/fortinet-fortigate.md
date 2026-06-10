---
name: single-system-fortinet-fortigate
description: >
  Use this skill when the user wants a single-firewall analysis of a
  Fortinet FortiGate — Periodic Business Review, firmware audit, license
  / security-services expiration, firewall policy summary, LAN-interface
  inventory, IPSec VPN tunnel review, default-credential audit. Trigger
  phrases: "FortiGate PBR", "pull FortiGate data", "FGT firewall review",
  "FortiGate license check", "Fortinet review", "FortiGate firmware
  audit". Produces an artifact in the format set in the customization
  block.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, soc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, pptx]
primitives:
  - metrics:fortinet-fortigate:access-profiles-summary
  - metrics:fortinet-fortigate:dns-servers
  - metrics:fortinet-fortigate:firewall-policy-structured
  - metrics:fortinet-fortigate:firewall-policy-summary
  - metrics:fortinet-fortigate:firewall-vip-summary
  - metrics:fortinet-fortigate:firmware-version
  - metrics:fortinet-fortigate:fortiem-status
  - metrics:fortinet-fortigate:group-summary
  - metrics:fortinet-fortigate:hostname
  - metrics:fortinet-fortigate:interface-summary
  - metrics:fortinet-fortigate:model
  - metrics:fortinet-fortigate:routing-policy-summary
  - metrics:fortinet-fortigate:user-summary
---

# Single-System Analysis — Fortinet FortiGate

> **Inspector:** `fortinet-fortigate-inspector` (ID 33). Network category.
> Firewall.
>
> **References:** `reference/inspector-aliases.md` (FortiGate, Fortinet,
> FGT, Forti). `reference/asset-fields.md` for asset cross-checks.
> `reference/qa-retry-pattern.md` for QA pass details.


---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-fortigate-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  identity: "Firewall Identity & Firmware"
  interfaces: "LAN / WAN Interface Inventory"
  policies: "Firewall Policy Summary"
  vpn: "IPSec VPN Tunnels"
  licensing: "FortiGuard Service Licensing"
  admins: "Admin User Audit"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 1
  license_expiration_warn_days: 60
  firmware_age_months_max: 12

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

- "Pull FortiGate data for the customer"
- "FGT PBR / quarterly review"
- "FortiGate FortiGuard license check"
- "FortiGate firmware audit"
- "IPSec tunnel status review"

Personas: NOC, SOC, vCIO/AM, TAM.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| FortiGate system ID | Yes | `liongard_system LIST query="fortinet"` |
| Reporting period | No | Default per customization |

---

## Locating the right system

```
liongard_system LIST searchMode=keyword query="fortinet" environmentId=<ENV_ID>
```

`SystemInfo.Hostname` returns the firewall display name. Multi-site
deployments show as separate systems — select by hostname.


---

## Liongard data sources

> **Asset Inventory First, Metric Cross-Check.** The FortiGate dataprint
> reports its own configuration. The cross-inspector device inventory
> tells you what's behind the firewall. FortiGate doesn't directly
> enumerate connected devices.

### Per-vendor data — FortiGate dataprint top-level keys

| Key | Description |
|---|---|
| `SystemInfo` | Firewall identity — hostname, model, firmware, serial |
| `Interfaces` | Physical / VLAN interface inventory with IP, zone, role |
| `FirewallPolicy` | Per-policy rule definition (source/dest, action, services, NAT, profiles) |
| `Users` | Local user accounts (VPN/firewall auth users — NOT admin accounts; System > Administrators are a separate category not captured in current inspector) |
| `IpsecVpnPhase1` | Site-to-site IPSec phase-1 configuration (per-tunnel) |
| `Licenses` | Per-service license status (FortiGuard AV, IPS, Web Filter, etc.) |
| `DhcpServers` | Per-interface DHCP server scopes |

#### Field gotchas (inline notes — not TODO)

- **`FirmwareVersion` major version drives lifecycle.** FortiGate firmware
  uses 4-part versions (e.g. `7.4.1`). **Major 6.x is end-of-engineering-
  support; major 7.x is current.** The recipe flags 6.x firmware as a
  critical lifecycle gap.
- **`Interfaces[*].allowAccess` on WAN interfaces is the management-
  exposure check.** Presence of `HTTPS` / `SSH` / `PING` in a WAN-role
  interface's `allowAccess` = management interface exposed to the
  internet. Strong recommendation: restrict to admin VLAN or remove
  entirely.
- **`FirewallPolicy` can be very large.** Production firewalls commonly
  have 100s of policies. Use `length()` and per-policy filters rather
  than dumping the full array.

### Cross-inspector cross-check — device inventory

```
liongard_device LIST environmentId=<ENV_ID>
                     fields=["hostname","manufacturer","inspectors","internalIP"]
```

```
# Devices behind the FortiGate (compute devices on managed network)
managed_devices = devices where category == "compute"

# Devices the FortiGate sees in user-attribution but Liongard doesn't see
# (FortiGate's user FSSO data isn't reflected in this recipe directly,
# but a divergence between RMM device count and FortiGate session count
# can indicate unmanaged devices on the network)
```

---

## Metrics and queries

### Identity & firmware

| Metric | JMESPath | Result shape |
|---|---|---|
| Hostname | `SystemInfo.Hostname` | `<string>` |
| Model | `SystemInfo.Model` | `<string>` |
| Firmware version | `SystemInfo.FirmwareVersion` | `<string>` |

### Local user audit

> **⚠️ Data gap — FortiGate admin accounts (System > Administrators) are NOT captured in the current inspector dataprint.** `AdminUsers` is not a valid key — it returns null across all validated systems. The `Users` key contains VPN/firewall local auth accounts only (not admin accounts). Admin account audit requires manual review in the FortiGate web GUI. VALIDATED: System A (2026-04-22, inspectorID=33) and System B (2026-05-18) both returned null for `AdminUsers`; `length(Users)` returned 0 and 2 respectively (local VPN users).

| Metric | JMESPath | Result shape |
|---|---|---|
| Local VPN/firewall users | `Users[*]` | `<array>` |
| Local user count | `length(Users)` | `<integer>` |

### Firewall policy

| Metric | JMESPath | Result shape |
|---|---|---|
| Firewall policy summary | `FirewallPolicy[*]` | `<array>` |

### Proposed metrics (not yet in Liongard library)

| Field | Workaround |
|---|---|
| LAN-role interface inventory | Client-side filter `Interfaces[?role == 'lan']` |
| WAN-interface allow-access detail | Client-side filter `Interfaces[?role == 'wan'].allowAccess` |
| Per-service license expiration (FortiGuard AV, IPS, Web Filter) | Manual confirm in FortiGate UI |
| DHCP server scope detail | Manual confirm in FortiGate UI |
| IPSec Phase 1 tunnel inventory + status | Manual confirm in FortiGate UI |

### Time-series — firmware / policy-count trend

```
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="length(FirewallPolicy)"

# Local user account count drift (VPN/firewall auth users only — admin accounts not in dataprint)
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="length(Users)"
```

---

## QA & Manual Verification

Run the QA pass per `reference/qa-retry-pattern.md` before rendering output:

1. **Retry persistent nulls.** Retry up to `qa.retry_attempts` times.

2. **Flag stale inspector data.** FortiGate inspector lastSeen > 1 day =
   API access issue.

3. **Cross-tool divergence (when applicable).** Compare admin-user count
   across snapshots — drift may indicate unauthorized admin creation.

4. **Proposed-metric gaps for this recipe** — surface these in the
   manual-verification appendix:
   - LAN-role interface inventory
   - WAN-interface management exposure detail
   - Per-service license expiration (FortiGuard AV, IPS, Web Filter)
   - DHCP server scope detail
   - IPSec Phase 1 tunnel inventory + status

5. **Manual Verification appendix** — render in the deliverable. Typical
   items for this recipe:
   - Firmware in major version 6.x (lifecycle gap).
   - Admin users beyond the expected MSP / customer-admin pair.
   - WAN-role interfaces with `HTTPS` / `SSH` in allowAccess (management
     exposure).

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| End-of-engineering-support firmware | major version of `FirmwareVersion` is 6.x | "**Critical:** FortiGate on major firmware 6.x — out of engineering support; plan upgrade to 7.x." |
| Firmware behind | firmware release > `slas.firmware_age_months_max` | "FortiGate firmware <version> is <N> months old — schedule maintenance window." |
| WAN management exposed | WAN interface `allowAccess` includes HTTPS or SSH | "Firewall management interface exposed on WAN — restrict to admin VLAN or VPN." |
| Excess local users | unexpected entries in `Users` (VPN/local auth users) | "Review FortiGate local user accounts — <N> warrant audit. Admin accounts require manual review in FortiGate GUI (not in dataprint)." |
| Large policy count | `length(FirewallPolicy)` very high | "<N> firewall policies — consider periodic policy cleanup; many large rule bases contain unused or shadowed rules." |
| Stale inspector | `lastSeen > 1 day` | "FortiGate inspector hasn't reported in <N> days — confirm API access." |


---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Admin accounts (System > Administrators) | ❌ not in dataprint — `AdminUsers` key is null; inspector does not capture FortiGate admin accounts | FortiGate web GUI (System > Administrators) |
| Traffic / bandwidth analytics | ❌ not in dataprint | FortiAnalyzer or syslog → SIEM |
| Threat / IPS detection counts | ❌ not in dataprint | FortiAnalyzer or FortiGate UI |
| Per-service license expiration | ⚠️ not in dataprint | FortiGate UI |
| DHCP scope detail | ⚠️ not in dataprint | FortiGate UI |
| IPSec tunnel status | ⚠️ not in dataprint | FortiGate UI |
| HA-pair config drift | ❌ not in dataprint | Manual compare via UI |


---

## Output format

Markdown / Word / PowerPoint per `output.format`.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_system LIST | query="fortinet" envId=<ENV_ID> | array<system> | ok |
| 3 | liongard_metric EVALUATE | metricName or jmesPathQuery sysId=<SYS_ID> envId=<ENV_ID> | <integer>, <array>, <object> | ok per metric |
| 4 | liongard_device LIST | envId=<ENV_ID> fields=[hostname,manufacturer,inspectors,internalIP] | array<device> | ok |
| 5 | (QA pass) retry persistent nulls | per `reference/qa-retry-pattern.md` | varies | ok |
```

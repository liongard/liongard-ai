---
name: single-system-junos
description: >
  Use this skill when the user wants a single-device analysis of a
  Juniper Junos device (SRX firewall, EX switch, MX router, QFX
  data-center switch) — PBR, configuration audit, Junos version
  audit, interface inventory, VLAN / zone audit, firewall-filter
  audit, routing protocol posture, local-user audit, management
  posture. Trigger phrases: "Junos review", "Juniper PBR", "SRX
  audit", "EX switch audit", "MX router PBR", "pull Junos data for
  <customer>", "Junos firmware audit".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, soc, technical-alignment-manager, vcio-account-manager]
output_formats: [markdown, word, pptx]
primitives:
  - metrics:junos:full-configuration
---

# Single-System Analysis — Junos (Juniper)

> **Inspector:** `junos-inspector` (ID 42). Beta. Network category.
> **One system per Junos device.** Covers SRX firewalls, EX
> switches, MX routers, QFX data-center switches running Junos OS.
> Per device, the recipe surfaces what's applicable (an EX produces
> VLAN / port output; an SRX produces zone / firewall-filter output;
> an MX produces routing output).
>
> **Beta inspector caveat:** Field coverage and metric names/JMESPath queries may shift
> as the inspector progresses out of beta. Verify metric names/JMESPath queries with
> `liongard_metric LIST` before relying on them in production
> deliverables.
>
> **References:** `reference/inspector-aliases.md` (Junos, Juniper).

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-junos-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  identity: "Device Identity & Junos Version"
  interfaces: "Interface Inventory"
  vlans_zones: "VLAN / Security Zone Configuration"
  firewall_filters: "Firewall Filter / Security Policy Audit"
  routing: "Routing Protocol Posture"
  local_users: "Local User & AAA Audit"
  management: "Management Interface Posture"
  lifecycle: "Hardware & Software Lifecycle"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 7
  junos_version_age_months_max: 18
  junos_eol_warn_months: 12
  open_telnet_allowed: false
  http_server_allowed: false
  ssh_v1_allowed: false
  default_root_login_allowed: false        # SSH root login = critical
  password_complexity_required: true
  required_aaa_authentication: ["radius", "tacacs+"]
  syslog_configured_required: true
  ntp_configured_required: true

reporting_period: { default: "current_state" }

qa:
  retry_on_null: true
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: false             # Beta inspector — expect many proposed
  manual_verification_section_required: true
```

---

## When to use

- "Pull Junos data for <customer>"
- "SRX / EX / MX PBR"
- "Junos firmware audit"
- "Junos EOL check"
- "Junos firewall-filter review"
- "Junos local-admin audit"

Cadence: monthly per device; quarterly in PBR; ad-hoc on JSA / CVE
disclosure.

Personas: NOC, SOC (SRX firewall focus), TAM, vCIO/AM.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the Junos device) | Yes | `liongard_system LIST query="junos"` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="junos"
```

Identify the device family (SRX / EX / MX / QFX) from the model
field — workflow steps adapt per family.

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Identity + Junos version

```
liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative (verify with liongard_metric LIST):
#   "junos.system.hostname"
#   "junos.system.model"                     (SRX300, EX4300, MX204, QFX5100 etc.)
#   "junos.system.platformFamily"            (srx / ex / mx / qfx)
#   "junos.system.serialNumber"
#   "junos.system.junosVersion"
#   "junos.system.junosReleaseDate"
#   "junos.system.uptimeDays"
#   "junos.system.haMode"                    (standalone / cluster / VC)
```

### Step 4 — Interface inventory

```
#   "junos.interfaces.totalCount"
#   "junos.interfaces.upCount"
#   "junos.interfaces.downCount"
#   "junos.interfaces.byType"                (ge / xe / et / ae / lo / vlan)
#   "junos.interfaces.descriptionMissing"
#   "junos.interfaces.aggregatedCount"        (ae* — link aggregation)
```

### Step 5 — VLANs (EX/QFX) / Security zones (SRX)

```
#   "junos.vlans.totalCount"                  (EX / QFX)
#   "junos.vlans.byUsage"
#   "junos.zones.totalCount"                  (SRX)
#   "junos.zones.list"
#   "junos.zones.untrustList"                 (WAN-facing zones)
```

### Step 6 — Firewall filters / Security policies

```
#   "junos.firewallFilters.totalCount"        (stateless / EX-family)
#   "junos.securityPolicies.totalCount"       (SRX)
#   "junos.securityPolicies.byAction"
#   "junos.securityPolicies.anyAnyCount"
#   "junos.securityPolicies.untrustToTrustCount"
#   "junos.securityPolicies.disabledCount"
#   "junos.securityPolicies.unusedCount"
```

### Step 7 — Routing protocol posture (MX / SRX / EX)

```
#   "junos.routing.protocolsConfigured"       (ospf / isis / bgp / static)
#   "junos.routing.staticRouteCount"
#   "junos.routing.ospfNeighborsCount"
#   "junos.routing.bgpNeighborsCount"
#   "junos.routing.defaultRouteConfigured"
```

### Step 8 — Local user + AAA audit

```
#   "junos.localUsers.totalCount"
#   "junos.localUsers.byClass"                (super-user / operator / etc.)
#   "junos.aaa.method"                        (local / radius / tacacs+)
#   "junos.aaa.authServers"
#   "junos.localUsers.rootSshLoginAllowed"
#   "junos.localUsers.passwordEncryptionEnabled"
```

### Step 9 — Management interface posture

```
#   "junos.management.telnetEnabled"
#   "junos.management.sshEnabled"
#   "junos.management.sshVersion"
#   "junos.management.httpEnabled"
#   "junos.management.httpsEnabled"
#   "junos.management.netconfEnabled"
#   "junos.management.snmpVersion"
#   "junos.management.snmpCommunityList"
#   "junos.management.syslogServers"
#   "junos.management.ntpServers"
#   "junos.management.firewallAccessFilterApplied"
```

### Step 10 — Lifecycle

```
#   "junos.system.eolDate"
#   "junos.system.eosDate"
#   "junos.system.daysUntilEol"
#   "junos.system.daysUntilEos"
```

### Step 11 — QA pass (per `reference/qa-retry-pattern.md`)

Beta-specific: expect more data gap metrics. File metric requests
for baseline checks the current inspector doesn't cover. Confirm
device family detection — workflow output should adapt accordingly.

### Step 12 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | Network infrastructure. |
| CIS Controls (v8.1) | ✅ | CIS 12.1, 12.5, 12.6, 12.8, 4.4, 13.1. SRX family also touches 12.2 (boundary protection) and 13.6 (IDS). |
| Cyber-insurance domain files | ✅ | `domains/network.md` Q19–Q21, Q35–Q36, Q41–Q43 (SRX VPN). |
| QBR / quarterly-business-review | ✅ | Chained via `all-network-infrastructure.md` (EX / QFX) and `all-firewalls.md` (SRX). |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| Junos version out of date | "Junos <X> is <N> months old. Schedule upgrade to current supported release." |
| Junos / hardware near EOL/EOS | "Device <H> within <N> months of EOL/EOS. Refresh roadmap entry required." |
| Telnet enabled | "URGENT: Telnet enabled. Disable; SSH v2 only." |
| Root SSH login allowed | "URGENT: SSH root login enabled. Disable; use named accounts with class super-user." |
| HTTP mgmt enabled | "URGENT: HTTP mgmt enabled. Force HTTPS." |
| SNMP weak community | "URGENT: SNMP weak community. Replace with v3 or strong v2c per allowlist." |
| Mgmt without firewall filter | "Mgmt interface lacks firewall filter. Configure access ACL." |
| Any-any security policy (SRX) | "URGENT: <N> any-any security policies. Restrict per least-privilege." |
| Untrust-to-trust policy (SRX) | "<N> Untrust-to-Trust policies. Confirm legitimate; restrict." |
| Unused security policy | "<N> policies unused. Remove if obsolete." |
| AAA local-only | "AAA local-only. Configure RADIUS/TACACS+ as primary." |
| Syslog / NTP not configured | "Configure syslog + NTP per MSP baseline." |
| VLAN / zone with no interfaces | "<N> unused VLANs / zones. Remove for hygiene." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Per-policy hit count | partial | Junos CLI / Junos Space / Mist |
| BGP / OSPF neighbor detail | partial | Junos CLI |
| SRX IDP / SkyATP detection history | partial | Junos Space Security Director |
| Junos PSIRT / JSA applicability per release | external | Juniper Security Advisory portal |

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST + liongard_system LIST | per inspector | array | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3-10 | liongard_metric VALUE | envId=<ENV_ID> sysId=<SYS_ID> metric=<id> | varies | ok per metric |
| 11 | QA pass | per `reference/qa-retry-pattern.md` | varies | ok |
| 12 | render | per `output.format` | <artifact path> | ok |
```

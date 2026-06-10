---
name: single-system-cisco-sbs-switch
description: >
  Use this skill when the user wants a single-device analysis of a
  Cisco Small Business Switch (CBS / SG series) — PBR, configuration
  audit, firmware audit, port + VLAN configuration, link aggregation,
  PoE budget, local-user audit, management posture. Trigger phrases:
  "Cisco SBS review", "Cisco SG switch audit", "Cisco CBS switch
  review", "pull Cisco SBS data for <customer>", "CBS firmware audit".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, technical-alignment-manager, vcio-account-manager]
output_formats: [markdown, word, pptx]
primitives:
  # Reconciled 2026-05-29 vs live dataprint (internal dev instance, Cisco SBS, inspected 2025-12-05).
  # Added model / local-users-total-count / ports-disabled-count (validated). hostname →
  # system-name (existing). EOL/firmware-date, PoE, http/telnet-enabled, stacking-mode,
  # uptime-days, ports-down/description-missing, vlans-unused pruned to
  # internal/proposed-metrics-backlog.md (not in dataprint; SystemUpTime is a string —
  # uptime-days derivable later).
  - metrics:cisco-sbs-switch-inspector:system-name
  - metrics:cisco-sbs-switch-inspector:model
  - metrics:cisco-sbs-switch-inspector:serial-number
  - metrics:cisco-sbs-switch-inspector:firmware-version
  - metrics:cisco-sbs-switch-inspector:local-users-total-count
  - metrics:cisco-sbs-switch-inspector:ports-total-count
  - metrics:cisco-sbs-switch-inspector:ports-up-count
  - metrics:cisco-sbs-switch-inspector:ports-disabled-count
  - metrics:cisco-sbs-switch-inspector:vlans-total-count
---

# Single-System Analysis — Cisco Small Business Switch

> **Inspector:** `cisco-sbs-switch-inspector` (ID 78). Network
> category. **One system per Cisco SBS / CBS switch.** Covers the
> Cisco SG and CBS-series small-business switches (SG350, SG500,
> CBS220/250/350). **Distinct from Catalyst** (covered by
> `cisco-ios-inspector`) — different OS, different feature set.
>
> **References:** `reference/inspector-aliases.md` (Cisco SBS, SBS).

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-cisco-sbs-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  identity: "Device Identity & Firmware"
  ports: "Port Inventory & Utilization"
  vlans: "VLAN Configuration"
  link_aggregation: "Link Aggregation (LAG)"
  poe: "PoE Budget"
  local_users: "Local User & Admin Audit"
  management: "Management Interface Posture"
  lifecycle: "Hardware & Firmware Lifecycle"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 7
  firmware_age_months_max: 18
  open_telnet_allowed: false
  http_server_allowed: false
  ssh_v1_allowed: false
  default_admin_allowed: false             # 'cisco/cisco' = critical
  default_local_users_max: 1               # MSP-standard admin only
  poe_utilization_pct_warn: 85
  spanning_tree_required: true
  syslog_configured_required: true

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

- "Pull Cisco SBS data for <customer>"
- "Cisco SG / CBS switch PBR"
- "CBS firmware audit"
- "SBS PoE budget check"
- "SBS local-admin audit"

Cadence: monthly per switch; quarterly in PBR.

Personas: NOC (daily health, PoE), TAM (firmware currency, standards),
vCIO/AM (refresh roadmap when EOL approaches).

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the Cisco SBS switch) | Yes | `liongard_system LIST query="cisco-sbs"` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="cisco-sbs"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Identity + firmware

```
liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative:
#   "cisco-sbs.system.hostname"
#   "cisco-sbs.system.model"                  (SG350, CBS220, etc.)
#   "cisco-sbs.system.firmwareVersion"
#   "cisco-sbs.system.firmwareReleaseDate"
#   "cisco-sbs.system.serialNumber"
#   "cisco-sbs.system.uptimeDays"
#   "cisco-sbs.system.stackingMode"           (Standalone / Native Stacking)
```

### Step 4 — Port inventory

```
#   "cisco-sbs.ports.totalCount"
#   "cisco-sbs.ports.upCount"
#   "cisco-sbs.ports.downCount"
#   "cisco-sbs.ports.disabledCount"
#   "cisco-sbs.ports.descriptionMissingCount"
#   "cisco-sbs.ports.errorRateHighCount"
```

### Step 5 — VLANs

```
#   "cisco-sbs.vlans.totalCount"
#   "cisco-sbs.vlans.activeCount"
#   "cisco-sbs.vlans.unusedCount"             (configured, no ports)
#   "cisco-sbs.vlans.nameDefaultCount"
#   "cisco-sbs.vlans.trunkPortCount"
```

### Step 6 — Link aggregation (LAG)

```
#   "cisco-sbs.lag.totalCount"
#   "cisco-sbs.lag.byMode"                    (static / LACP)
#   "cisco-sbs.lag.degradedCount"             (≥1 member port down)
```

### Step 7 — PoE budget

```
#   "cisco-sbs.poe.budgetWatts"
#   "cisco-sbs.poe.consumedWatts"
#   "cisco-sbs.poe.utilizationPct"
#   "cisco-sbs.poe.byPortDraw"
```

### Step 8 — Local user + admin audit

```
#   "cisco-sbs.localUsers.totalCount"
#   "cisco-sbs.localUsers.adminCount"
#   "cisco-sbs.localUsers.defaultNamedCount"
#   "cisco-sbs.localUsers.passwordEncryptionEnabled"
```

### Step 9 — Management interface posture

```
#   "cisco-sbs.management.telnetEnabled"
#   "cisco-sbs.management.sshEnabled"
#   "cisco-sbs.management.sshVersion"
#   "cisco-sbs.management.httpEnabled"
#   "cisco-sbs.management.httpsEnabled"
#   "cisco-sbs.management.snmpVersion"
#   "cisco-sbs.management.snmpCommunityList"
#   "cisco-sbs.management.syslogServers"
#   "cisco-sbs.management.ntpServers"
#   "cisco-sbs.management.aclEnabled"
```

### Step 10 — Lifecycle

```
#   "cisco-sbs.system.eolDate"
#   "cisco-sbs.system.eosDate"
#   "cisco-sbs.system.daysUntilEol"
```

### Step 11 — QA pass (per `reference/qa-retry-pattern.md`)

Standard pattern. Note: SBS line has shorter support lifecycle than
Catalyst; flag EOL aggressively for refresh roadmap.

### Step 12 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | Network infrastructure. |
| CIS Controls (v8.1) | ✅ | CIS 12.1, 12.5, 12.6, 12.8, 4.4, 13.1. |
| Cyber-insurance domain files | ✅ | `domains/network.md` Q19–Q21, Q35–Q36 — extends to switching. |
| QBR / quarterly-business-review | ✅ | Chained via `all-network-infrastructure.md`. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| Firmware out of date | "Firmware <N> months old. Schedule upgrade." |
| Device near EOL/EOS | "Switch <H> within <N> months of EOL/EOS. Refresh roadmap entry required." |
| Telnet enabled | "URGENT: Telnet enabled. Disable; SSH v2 only." |
| HTTP mgmt enabled | "URGENT: HTTP mgmt enabled. Force HTTPS only." |
| SSH v1 | "URGENT: SSH v1 enabled. Force v2 only." |
| Default admin enabled | "URGENT: Default 'cisco' admin account enabled. Rename + rotate." |
| SNMP public/private | "URGENT: SNMP `public`/`private`. Replace with v3 user or strong community." |
| Mgmt without ACL | "Mgmt interface lacks ACL. Configure source-IP allowlist." |
| PoE utilization > warn | "PoE at <N>%. Plan for capacity (add switch or upgrade)." |
| LAG degraded | "<N> LAGs degraded (member port down). Triage." |
| Port with high error rate | "Port <P> showing errors. Check cabling / SFP." |
| VLAN with no ports | "<N> unused VLANs. Remove for hygiene." |
| BPDUguard not enabled | "BPDUguard / portfast not enabled on access ports. Configure." |
| Syslog / NTP not configured | "Configure syslog + NTP per MSP baseline." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Per-port MAC / LLDP detail | partial | Cisco SBS GUI |
| Per-port traffic counters | partial | Cisco SBS GUI |
| Cisco Smart Licensing for SBS (where applicable) | partial / external | CSSM portal |
| Cisco PSIRT applicability per firmware | external | Cisco Security Advisory portal |

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

---
name: single-system-hp-procurve
description: >
  Use this skill when the user wants a single-device analysis of an
  HP ProCurve / HPE Aruba CX (legacy ProCurve / Aruba-OS Switch)
  switch — PBR, configuration audit, firmware audit, port + VLAN
  configuration, LACP / trunk audit, PoE budget, local-user audit,
  management posture. Trigger phrases: "HP ProCurve review", "ProCurve
  switch audit", "Aruba switch PBR", "pull ProCurve data for
  <customer>", "ProCurve firmware audit".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, technical-alignment-manager, vcio-account-manager]
output_formats: [markdown, word, pptx]
primitives:
  - metrics:hp-procurve-inspector:access-list-summary
  - metrics:hp-procurve-inspector:boot-rom-version
  - metrics:hp-procurve-inspector:configuration-status
  - metrics:hp-procurve-inspector:default-boot
  - metrics:hp-procurve-inspector:default-gateway
  - metrics:hp-procurve-inspector:firmware-version
  - metrics:hp-procurve-inspector:igmp-summary
  - metrics:hp-procurve-inspector:interface-summary
  - metrics:hp-procurve-inspector:ip-configuration-summary
  - metrics:hp-procurve-inspector:lacp-summary
  - metrics:hp-procurve-inspector:loop-detection-count
  - metrics:hp-procurve-inspector:management-ip
  - metrics:hp-procurve-inspector:model-list
  - metrics:hp-procurve-inspector:port-security-violation-count
  - metrics:hp-procurve-inspector:trunk-summary
  - metrics:hp-procurve-inspector:vlan-priority-summary
  - metrics:hp-procurve-inspector:vlan-summary
---

# Single-System Analysis — HP ProCurve / HPE Aruba Switch

> **Inspector:** `hp-procurve-inspector` (ID 63). Network category.
> **One system per HP ProCurve / Aruba switch.** Covers legacy
> ProCurve and current HPE Aruba CX / Aruba-OS Switch products.
>
> **References:** `reference/inspector-aliases.md` (ProCurve, HPE
> Aruba). Distinct from Aruba wireless (different inspector, when
> available).

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-hp-procurve-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  identity: "Switch Identity & Firmware"
  ports: "Port Inventory"
  vlans: "VLAN Configuration"
  trunks: "Trunk / Link Aggregation"
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
  default_admin_allowed: false
  default_local_users_max: 1
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

- "Pull ProCurve data for <customer>"
- "ProCurve / Aruba switch PBR"
- "ProCurve firmware audit"
- "ProCurve PoE check"
- "ProCurve local-admin audit"

Cadence: monthly per switch; quarterly in PBR.

Personas: NOC, TAM, vCIO/AM.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the ProCurve / Aruba switch) | Yes | `liongard_system LIST query="procurve"` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="procurve"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Identity + firmware

```
liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative:
#   "procurve.system.hostname"
#   "procurve.system.model"                    (e.g. 2530-24G, Aruba 6300, etc.)
#   "procurve.system.platformFamily"           (ProCurve / Aruba CX / etc.)
#   "procurve.system.firmwareVersion"
#   "procurve.system.firmwareReleaseDate"
#   "procurve.system.serialNumber"
#   "procurve.system.uptimeDays"
#   "procurve.system.stackingMode"
```

### Step 4 — Port inventory

```
#   "procurve.ports.totalCount"
#   "procurve.ports.upCount"
#   "procurve.ports.downCount"
#   "procurve.ports.disabledCount"
#   "procurve.ports.descriptionMissingCount"
#   "procurve.ports.errorRateHighCount"
```

### Step 5 — VLANs

```
#   "procurve.vlans.totalCount"
#   "procurve.vlans.byUsage"
#   "procurve.vlans.unusedCount"
#   "procurve.vlans.taggedTrunkCount"
```

### Step 6 — Trunks / LACP

```
#   "procurve.trunks.totalCount"
#   "procurve.trunks.byMode"                  (static / LACP)
#   "procurve.trunks.degradedCount"
```

### Step 7 — PoE

```
#   "procurve.poe.budgetWatts"
#   "procurve.poe.consumedWatts"
#   "procurve.poe.utilizationPct"
```

### Step 8 — Local user + admin audit

```
#   "procurve.localUsers.totalCount"
#   "procurve.localUsers.adminCount"
#   "procurve.localUsers.defaultNamedCount"
#   "procurve.aaa.method"                      (local / radius / tacacs+)
```

### Step 9 — Management interface

```
#   "procurve.management.telnetEnabled"
#   "procurve.management.sshEnabled"
#   "procurve.management.sshVersion"
#   "procurve.management.httpEnabled"
#   "procurve.management.httpsEnabled"
#   "procurve.management.snmpVersion"
#   "procurve.management.snmpCommunityList"
#   "procurve.management.syslogServers"
#   "procurve.management.ntpServers"
```

### Step 10 — Lifecycle

```
#   "procurve.system.eolDate"
#   "procurve.system.eosDate"
#   "procurve.system.daysUntilEol"
```

### Step 11 — QA pass (per `reference/qa-retry-pattern.md`)

Standard pattern. ProCurve / Aruba family detection matters — the
ProCurve legacy series has different firmware tracks than current
Aruba CX. Surface platform family clearly in the report header.

### Step 12 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | Network infrastructure. |
| CIS Controls (v8.1) | ✅ | CIS 12.1, 12.5, 12.6, 12.8, 4.4, 13.1. |
| Cyber-insurance domain files | ✅ | `domains/network.md` Q19–Q21, Q35–Q36. |
| QBR / quarterly-business-review | ✅ | Chained via `all-network-infrastructure.md`. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| Firmware out of date | "Firmware <N> months old. Schedule upgrade." |
| Device near EOL/EOS | "Switch <H> within <N> months of EOL/EOS. Refresh roadmap entry required." |
| Telnet enabled | "URGENT: Telnet enabled. Disable; SSH only." |
| HTTP mgmt enabled | "URGENT: HTTP mgmt enabled. Force HTTPS only." |
| Default admin | "URGENT: Default admin name. Rename + rotate." |
| SNMP weak community | "URGENT: SNMP weak / default community. Replace with v3 or strong v2c." |
| Mgmt without ACL | "Mgmt lacks ACL. Configure source-IP allowlist." |
| PoE high utilization | "PoE at <N>%. Plan capacity (add switch / upgrade)." |
| LACP trunk degraded | "<N> trunks degraded. Triage." |
| Port high error rate | "Port <P> showing errors. Check cabling." |
| VLAN with no ports | "<N> unused VLANs. Remove for hygiene." |
| AAA local-only | "AAA local-only. Configure RADIUS/TACACS+ as primary." |
| Syslog / NTP missing | "Configure syslog + NTP." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Per-port MAC / LLDP detail | partial | Aruba CX / ProCurve CLI |
| Aruba Central / NetEdit integration | partial | Aruba Central |
| PSIRT / advisory applicability per firmware | external | HPE Aruba advisory portal |

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

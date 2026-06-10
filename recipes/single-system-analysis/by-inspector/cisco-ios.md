---
name: single-system-cisco-ios
description: >
  Use this skill when the user wants a single-device analysis of a
  Cisco IOS / IOS-XE router or switch — PBR, configuration audit,
  IOS version + EOL audit, interface inventory, VLAN audit, ACL
  audit, routing protocol posture, local-user / AAA audit, management-
  interface exposure. Trigger phrases: "Cisco IOS review", "Cisco
  router PBR", "Cisco switch audit", "pull Cisco IOS data for
  <customer>", "Cisco IOS firmware audit", "VLAN audit for the Cisco
  switch", "Cisco router ACL review".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, soc, technical-alignment-manager, vcio-account-manager]
output_formats: [markdown, word, pptx]
primitives:
  - metrics:cisco-ios:admin-disabled-interfaces-list
  - metrics:cisco-ios:model
  - metrics:cisco-ios:running-configuration
  - metrics:cisco-ios:software-type
  - metrics:cisco-ios:software-version
---

# Single-System Analysis — Cisco IOS

> **Inspector:** `cisco-ios-inspector` (ID 30). Network category.
> **One system per Cisco IOS / IOS-XE device.** Covers Cisco routers
> (ISR / ASR) and Catalyst switches running classic IOS or IOS-XE.
> Per device, the recipe surfaces what's applicable (a Catalyst
> switch produces VLAN / port output; an ISR router produces routing
> / NAT output).
>
> **References:** `reference/inspector-aliases.md` (Cisco IOS, Cisco
> router, Cisco switch). Distinct from `cisco-asa-inspector` (firewall)
> and `cisco-sbs-switch-inspector` (small-business switches running
> different OS).

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-cisco-ios-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  identity: "Device Identity & IOS Version"
  interfaces: "Interface Inventory"
  vlans: "VLAN Configuration"                # applicable to switches
  routing: "Routing Protocol Posture"        # applicable to routers
  acls: "ACL Audit"
  aaa: "AAA / Local-User Audit"
  management: "Management Interface Posture"
  lifecycle: "Hardware & Software Lifecycle"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 7
  ios_version_age_months_max: 18           # IOS / IOS-XE major-version cadence
  ios_eol_warn_months: 12                  # alert if device firmware is within N months of EOL/EOS
  open_telnet_allowed: false               # any Telnet vty/HTTP server = critical
  http_server_allowed: false               # `ip http server` enabled = high
  ssh_v1_allowed: false
  any_acl_to_internet_allowed: false
  default_enable_password_allowed: false
  password_encryption_required: true       # `service password-encryption`
  required_local_admins_max: 2             # any non-MSP local accounts flagged
  required_aaa_authentication: ["radius", "tacacs+"]  # MSP-standard auth method
  spanning_tree_required: true             # bpduguard / portfast / etc.
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

- "Pull Cisco IOS data for <customer>"
- "Cisco router / switch PBR"
- "Cisco IOS firmware audit"
- "Cisco IOS EOL / EOS check"
- "VLAN audit on the Cisco switch"
- "ACL review on the Cisco router"
- "Cisco IOS management-exposure audit"

Cadence: monthly per device; quarterly in PBR; ad-hoc on firmware-CVE disclosure.

Personas: NOC (operational), SOC (security — management exposure, AAA),
TAM (firmware currency, standards alignment), vCIO/AM (refresh
roadmap when EOL/EOS approaches).

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the Cisco IOS device) | Yes | `liongard_system LIST query="cisco-ios"` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="cisco-ios"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Identity + IOS version

```
liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative:
#   "cisco-ios.system.hostname"
#   "cisco-ios.system.model"                 (e.g. ISR4451, Catalyst 9300, etc.)
#   "cisco-ios.system.platformType"          (router | switch | wireless-controller)
#   "cisco-ios.system.serialNumber"
#   "cisco-ios.system.iosVersion"
#   "cisco-ios.system.iosTrain"              (e.g. 17.6.5, classic IOS 15.2)
#   "cisco-ios.system.iosReleaseDate"
#   "cisco-ios.system.uptimeDays"
#   "cisco-ios.system.lastReloadReason"
```

### Step 4 — Interface inventory

```
#   "cisco-ios.interfaces.totalCount"
#   "cisco-ios.interfaces.upCount"
#   "cisco-ios.interfaces.downCount"
#   "cisco-ios.interfaces.byType"           (Gi / Te / Fa / Vlan / Loopback / etc.)
#   "cisco-ios.interfaces.errorRateHigh"    (CRC / input errors)
#   "cisco-ios.interfaces.descriptionMissing" (interfaces without `description`)
```

### Step 5 — VLANs (switches)

```
#   "cisco-ios.vlans.totalCount"
#   "cisco-ios.vlans.byUsageStatus"          (active / suspended / no ports)
#   "cisco-ios.vlans.nameDefaultCount"       (e.g. VLAN0010 — no name)
#   "cisco-ios.vlans.taggedTrunkCount"
#   "cisco-ios.spanningTree.mode"            (pvst / rapid-pvst / mst)
#   "cisco-ios.spanningTree.bpduguardEnabled"
#   "cisco-ios.spanningTree.portfastEnabled"
```

### Step 6 — Routing protocol posture (routers)

```
#   "cisco-ios.routing.protocolsConfigured"  (ospf / eigrp / bgp / static)
#   "cisco-ios.routing.staticRouteCount"
#   "cisco-ios.routing.ospfNeighborsCount"
#   "cisco-ios.routing.bgpNeighborsCount"
#   "cisco-ios.routing.defaultRouteConfigured"
#   "cisco-ios.nat.staticRulesCount"
#   "cisco-ios.nat.dynamicRulesCount"
```

### Step 7 — ACL audit

```
#   "cisco-ios.acls.totalCount"
#   "cisco-ios.acls.byType"                 (standard / extended)
#   "cisco-ios.acls.permitAnyAnyCount"
#   "cisco-ios.acls.appliedToInterfaceCount"
#   "cisco-ios.acls.unusedCount"            (configured but not applied)
```

### Step 8 — AAA / local-user audit

```
#   "cisco-ios.aaa.method"                  (local / radius / tacacs+)
#   "cisco-ios.aaa.authServers"
#   "cisco-ios.localUsers.totalCount"
#   "cisco-ios.localUsers.byPrivilege"
#   "cisco-ios.localUsers.passwordEncryptionEnabled"
#   "cisco-ios.localUsers.enablePasswordType"  (type 5 / type 7 / type 9)
#   "cisco-ios.localUsers.defaultEnabled"     (cisco/cisco etc. — critical)
```

### Step 9 — Management interface posture

```
#   "cisco-ios.management.telnetEnabled"
#   "cisco-ios.management.sshVersion"        (1 | 2 | "1 2")
#   "cisco-ios.management.httpServerEnabled"
#   "cisco-ios.management.httpsServerEnabled"
#   "cisco-ios.management.vtyAclName"
#   "cisco-ios.management.snmpVersion"
#   "cisco-ios.management.snmpCommunityList"   (public/private = critical)
#   "cisco-ios.management.syslogServers"
#   "cisco-ios.management.ntpServers"
#   "cisco-ios.management.loggingBufferSize"
```

### Step 10 — Hardware + software lifecycle

```
#   "cisco-ios.system.eolDate"               (vendor-published EOL)
#   "cisco-ios.system.eosDate"               (end-of-support)
#   "cisco-ios.system.daysUntilEol"
#   "cisco-ios.system.daysUntilEos"
#   "cisco-ios.system.smartLicenseStatus"
```

### Step 11 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on retry, freshness, IOS-platform detection (router vs.
switch), proposed-metric gaps. Many Cisco IOS metrics require
parsing `show running-config` and may be marked (not in current dataprint) in the
current inspector.

### Step 12 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | Network infrastructure, not endpoint. |
| CIS Controls (v8.1) | ✅ | CIS 12.1 (asset inventory), 12.5 (centralize network AAA), 12.6 (secure mgmt protocols), 12.8 (out-of-band mgmt), 4.4 (configuration management), 13.1 (network monitoring), 4.1 (centralized config). |
| Cyber-insurance domain files | ✅ | Aligns with `domains/network.md` Q19–Q21, Q35–Q36 — firewall + network infrastructure questions extend to switches / routers. |
| QBR / quarterly-business-review | ✅ | Chained via the new `all-network-infrastructure.md` rollup; firmware-currency + lifecycle data feeds the refresh roadmap. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| IOS version out of date | "IOS train <X> is <N> months old. Schedule upgrade to current supported train per Cisco recommended releases." |
| IOS / hardware near EOL/EOS | "Device <H> within <N> months of EOL/EOS. Refresh roadmap entry required; quote replacement." |
| Telnet enabled | "URGENT: Telnet vty enabled. Disable; restrict to SSH v2 only." |
| HTTP server enabled | "URGENT: `ip http server` enabled. Disable; use HTTPS or out-of-band only." |
| SSH v1 allowed | "URGENT: SSH v1 allowed. Force `ip ssh version 2`." |
| Default enable password / weak crypto | "URGENT: Type 5 / type 7 enable password detected. Re-key as type 9 (scrypt) and rotate." |
| SNMP public/private | "URGENT: SNMP community `public`/`private` configured. Replace with strong v3 user or strong v2c community per allowlist." |
| Mgmt vty no ACL | "vty lines lack source-IP ACL. Configure vty allowlist + transport input restriction." |
| AAA fallback to local-only | "AAA configured local-only. Configure RADIUS/TACACS+ as primary with local as fallback." |
| Local user with default password | "<N> local accounts with weak / default credentials. Rotate." |
| Unused ACL | "<N> ACLs configured but not applied. Remove or apply." |
| Permit any-any rule | "URGENT: <N> ACLs with permit any-any. Restrict per least-privilege." |
| Interface with high error rate | "Interface <I> showing CRC / input errors. Check cabling / SFP." |
| VLAN with no ports | "<N> VLANs configured but unused. Remove for hygiene." |
| BPDUguard / portfast not enabled | "Spanning-tree edge protection (bpduguard + portfast) not enabled on access ports. Configure." |
| Syslog not configured | "No syslog server configured. Configure to central SIEM / log collector." |
| NTP not configured | "NTP not configured. Configure for accurate timestamps in logs / SNMP." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Per-port MAC table | partial | Cisco device CLI / Prime / DNA Center |
| PoE budget / draw | partial | Device CLI |
| BGP route-table size | partial | Device CLI |
| EIGRP / OSPF neighbor detail | partial | Device CLI |
| Cisco Smart Licensing detail | partial | CSSM portal |
| Cisco PSIRT / CVE applicability per IOS version | external | Cisco Security Advisory portal |

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

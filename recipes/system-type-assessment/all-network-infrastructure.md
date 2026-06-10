---
name: system-type-all-network-infrastructure
description: >
  Use this skill when the user wants a unified network-infrastructure
  posture assessment across switches, routers, and wireless controllers
  in an environment — Cisco IOS / IOS-XE, Cisco SBS, HP ProCurve / Aruba,
  Junos (EX / MX / QFX), Ubiquiti UniFi, and the switch / AP portions
  of Cisco Meraki. Trigger phrases: "network infrastructure posture",
  "switch and router audit for <customer>", "wireless posture review",
  "Layer 2 / Layer 3 audit", "VLAN audit across the environment",
  "all switches firmware audit", "network refresh roadmap".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, soc, technical-alignment-manager, vcio-account-manager, accounting-finance]
output_formats: [pptx, word, xlsx, markdown]
primitives:
  - metrics:cisco-ios:admin-disabled-interfaces-list
  - metrics:cisco-ios:model
  - metrics:cisco-ios:running-configuration
  - metrics:cisco-ios:software-type
  - metrics:cisco-ios:software-version
  - metrics:cisco-meraki:days-until-license-expiry
  - metrics:cisco-meraki:device-firmware-summary
  - metrics:cisco-meraki:device-serial-list
  - metrics:cisco-meraki:hardware-list
  - metrics:cisco-meraki:license-status
  - metrics:cisco-meraki:open-ssid-count
  - metrics:cisco-meraki:open-ssid-list
  - metrics:cisco-meraki:privileged-user-count
  - metrics:cisco-meraki:privileged-user-list
  - metrics:cisco-meraki:ssid-list
  - metrics:cisco-meraki:total-device-count
  - metrics:cisco-meraki:vlan-count
  - metrics:cisco-meraki:vpn-enabled-subnets
  - metrics:cisco-meraki:weak-encryption-ssid-count
  - metrics:cisco-meraki:weak-encryption-ssid-list
  - metrics:cisco-sbs-switch-inspector:firmware-version
  - metrics:cisco-sbs-switch-inspector:ports-total-count
  - metrics:cisco-sbs-switch-inspector:ports-up-count
  - metrics:cisco-sbs-switch-inspector:serial-number
  - metrics:cisco-sbs-switch-inspector:vlans-total-count
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
  - metrics:junos:full-configuration
  - metrics:ubiquiti-unifi:controller-version
  - metrics:ubiquiti-unifi:device-serial-number-list
  - metrics:ubiquiti-unifi:devices-list
  - metrics:ubiquiti-unifi:hardware-type-and-version
  - metrics:ubiquiti-unifi:subnets-list
  - metrics:ubiquiti-unifi:super-admin-users-list
---

# System-Type Assessment — All Network Infrastructure

> Unified network-infrastructure posture across every switch / router /
> wireless-controller inspector deployed at the customer. Covers
> Layer 2 (VLANs, ports, spanning tree, LAG), Layer 3 (routing
> protocols, NAT, ACLs), and wireless (SSIDs, security mode, guest
> network) — the network-stack layer **below** the firewall and
> **above** the endpoint.
>
> **Inspectors covered:**
>
> | Inspector | Recipe | Devices covered |
> |---|---|---|
> | Cisco IOS / IOS-XE | `recipes/single-system-analysis/by-inspector/cisco-ios.md` | Catalyst switches, ISR / ASR routers |
> | Cisco Small Business Switch | `recipes/single-system-analysis/by-inspector/cisco-sbs-switch.md` | SG / CBS series |
> | HP ProCurve / HPE Aruba | `recipes/single-system-analysis/by-inspector/hp-procurve.md` | ProCurve + Aruba CX |
> | Junos (Juniper) | `recipes/single-system-analysis/by-inspector/junos.md` | EX / MX / QFX (SRX firewalls join `all-firewalls.md`) |
> | Ubiquiti UniFi | `recipes/single-system-analysis/by-inspector/ubiquiti-unifi.md` | UniFi APs + switches + UDM gateways |
> | Cisco Meraki (MS / MR portion) | `recipes/single-system-analysis/by-inspector/cisco-meraki.md` | Switch + AP layers (MX firewall portion joins `all-firewalls.md`) |
>
> **Relationship to `all-firewalls.md`:** Firewalls are a separate rollup.
> Devices that combine routing + firewall in one box (UDM, SRX, Meraki MX)
> appear in both rollups — once for the firewall role, once for the
> switch / routing / wireless role.
>
> **References:** `reference/asset-fields.md` (device inventory cross-
> check via `liongard_device`), `reference/qa-retry-pattern.md`,
> `reference/inspector-aliases.md`.

---

## Customize for your MSP

```yaml
output:
  format: pptx
  filename: "<customer>-network-infrastructure-posture-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  cover: "Network Infrastructure Posture"
  executive_summary: "Executive Summary"
  inventory: "Device Inventory (Switches / Routers / APs)"
  firmware_currency: "Firmware Currency"
  vlan_topology: "VLAN Topology"
  wireless_posture: "Wireless Security Posture"
  management_exposure: "Management Interface Exposure"
  aaa_authentication: "AAA / Authentication Posture"
  lifecycle: "Lifecycle & Refresh Roadmap"
  vendor_consolidation: "Vendor Consolidation Opportunities"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Manual Verification"
  appendix: "Appendix — Per-Device Detail"
  verification_log: "Verification Log"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 7
  firmware_age_months_max: 18              # baseline across vendors; per-vendor recipes may tighten
  unifi_firmware_age_months_max: 6         # UniFi releases faster
  open_telnet_allowed: false
  http_mgmt_allowed: false
  ssh_v1_allowed: false
  snmp_weak_community_allowed: false
  mgmt_acl_required: true
  ssid_open_authentication_allowed: false
  ssid_wep_or_wpa1_allowed: false
  guest_isolation_required: true
  required_aaa_authentication: ["radius", "tacacs+"]
  syslog_configured_required: true
  ntp_configured_required: true
  network_vendor_consolidation_target: 2   # MSP standard: ≤ 2 network-infrastructure vendors
                                           # (3+ = consolidation candidate)

reporting_period: { default: "current_state" }

stack:
  auto_discover: true
  inspectors_in_scope: []
  inspectors_to_skip: []

qa:
  retry_on_null: true
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: false
  surface_single_source_visibility: true
  manual_verification_section_required: true
```

---

## When to use

- "Network infrastructure posture for <customer>"
- "Switch + router + AP audit for <customer>"
- "Layer 2 / Layer 3 audit"
- "Wireless posture across the environment"
- "All switches firmware audit"
- "Network refresh roadmap"
- "Cross-vendor network consolidation analysis"

Cadence: monthly per customer (operational); quarterly in PBR; annual
in the roadmap-planning recipe; ad-hoc on firmware-CVE disclosure.

Personas:
- **NOC** (primary — operational health, firmware, AP/switch state)
- **SOC** (mgmt-exposure audit, weak crypto / Telnet / SNMP, wireless
  security)
- **TAM** (firmware standards alignment, refresh roadmap)
- **vCIO / Account Manager** (refresh roadmap, vendor consolidation
  business case)
- **Accounting / Finance** (refresh budget — paired with
  `recipes/roadmap-planning/refresh-and-lifecycle-roadmap.md`)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |

---

## Workflow

### Step 1 — Scope + vendor discovery

```
liongard_environment LIST searchMode=keyword query="<customer>"

# Discover deployed network-infrastructure inspectors
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="cisco-ios"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="cisco-sbs"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="procurve"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="junos"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="unifi"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="meraki"
```

Per-vendor deployment table. If more than
`slas.network_vendor_consolidation_target` (default 2) network
vendors deployed, flag as a **consolidation candidate**. (Common
mixed-vendor pattern: Cisco core + UniFi edge / wireless.)

### Step 2 — Inspector freshness across all vendors

```
liongard_timeline LIST environmentId=<ENV_ID>
```

Stale-inspector findings per vendor. Surface vendors where multiple
devices are stale together — indicates the inspector credential /
agent has broken, not individual devices.

### Step 3 — Reconciled device inventory

> **The reconciled asset inventory is the primary source.** Network
> devices appear in `liongard_device` deduplicated by hostname /
> serial / MAC across the inspectors that observe them. See
> `reference/asset-fields.md` § Deduplication keys.

```
liongard_device LIST environmentId=<ENV_ID>
                     fields=["hostname","operatingSystem","manufacturer","model","serialNumber","macAddress","class","role","inspectors","lastSeen"]
                     filter="class IN ['switch','router','wireless-controller','access-point','gateway']"
```

Cross-check that each device's `inspectors[]` array includes its
network-infrastructure inspector. Devices with no network inspector
but a hardware class of switch / router / AP indicate coverage gaps.

### Step 4 — Per-vendor chained findings

For each deployed vendor, chain the per-vendor single recipe with
`audience.tone` inherited. Extract:

- Device inventory (per vendor)
- Firmware version + age
- Mgmt-interface posture (Telnet / SSH / HTTP / SNMP)
- Local-user / AAA posture
- VLAN / SSID inventory (where applicable)
- Lifecycle (EOL / EOS dates)

### Step 5 — Firmware currency rollup

Compute across vendors:

| Vendor | Devices | Up-to-date | Within 6mo | Within 18mo | Out-of-date |
|---|---|---|---|---|---|
| Cisco IOS | N | N | N | N | N |
| Cisco SBS | N | N | N | N | N |
| ProCurve / Aruba | N | N | N | N | N |
| Junos | N | N | N | N | N |
| UniFi | N | N | N | N | N |
| Meraki (MS / MR) | N | N | N | N | N |

Surface the **worst-currency vendor** as the recipe's headline
finding when one vendor is materially behind the others.

### Step 6 — VLAN topology rollup

When the customer has multiple switches (especially across vendors),
surface:

- Total unique VLANs configured across the environment
- VLANs configured on some switches but not others (consistency check)
- VLAN with no ports active anywhere (cleanup candidate)
- VLANs named with default convention (VLANxxxx — no description)

> **VLAN sprawl is the most-common finding** in mixed-vendor or
> post-acquisition environments. The MSP-standard VLAN baseline
> (corp / VoIP / guest / IoT / mgmt) should be consistent across
> every switch.

### Step 7 — Wireless security posture

When UniFi, Meraki MR, or other wireless-capable devices are deployed:

| Posture check | Threshold | Recipe finding |
|---|---|---|
| SSID auth method | Must be WPA2 / WPA3 | Open / WEP / WPA1 = Critical |
| Guest network isolation | Layer 2 isolation enabled | Disabled = High |
| Guest auth | Captive portal / voucher / RADIUS | None = Medium |
| PSK strength (cross-SSID) | ≥ 16 chars | Shorter = High |
| Band steering / fast-roaming | Enabled | Disabled = Low (operational) |

### Step 8 — Management interface exposure rollup

Aggregate across vendors:

- Devices with Telnet enabled → **Critical**
- Devices with HTTP mgmt enabled → **High**
- Devices with SSH v1 → **Critical**
- Devices with SNMP weak community → **Critical**
- Devices without mgmt ACL → **High**

> **Mgmt exposure is the highest-leverage SOC finding** in network
> rollups. A single Telnet-enabled switch in a customer environment
> exposes the whole network to credential interception.

### Step 9 — AAA / authentication posture

Aggregate across vendors:

- Devices on AAA local-only → Medium (Recommend RADIUS / TACACS+)
- Devices with default admin name / weak credentials → Critical
- AAA-server reachability (where reported) → operational health

### Step 10 — Lifecycle + refresh roadmap

Compute:

- Devices within `slas.firmware_age_months_max` of EOL/EOS → roadmap
- Devices discontinued by vendor → urgent refresh
- Hardware class distribution by manufacturing year (where available)
  → refresh-by-quarter plan

Feed this into `recipes/roadmap-planning/refresh-and-lifecycle-roadmap.md`
when running the cross-cutting roadmap.

### Step 11 — Vendor consolidation analysis

If `slas.network_vendor_consolidation_target` exceeded:

- Per-vendor device count
- Cross-vendor management-tool overlap (different consoles per vendor)
- Refresh-driven consolidation opportunity (when a vendor's hardware
  is nearing EOL, refresh window = consolidation window)
- Estimated migration effort + license consolidation savings

### Step 12 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on:
1. Retry persistent nulls per vendor.
2. Stale-inspector flags propagate per vendor.
3. **Class-based reconciliation** — confirm devices' `class` field
   (switch / router / AP) matches the network-infrastructure category
   when chaining the rollup.
4. **Mgmt-exposure verification** — cross-check between vendors when
   the same management station addresses multiple devices.
5. Proposed-metric gaps per vendor.

### Step 13 — Render

Recommended slide / page order for pptx:

| # | Slide | Content |
|---|---|---|
| 1 | Cover | Customer, period |
| 2 | Executive Summary | Headline mgmt-exposure + consolidation flag |
| 3 | Device Inventory | Per-vendor + reconciled count |
| 4 | Firmware Currency | Step 5 matrix |
| 5 | VLAN Topology | Step 6 — consistency + cleanup |
| 6 | Wireless Security Posture | Step 7 |
| 7 | Management Interface Exposure | Step 8 — leading SOC finding |
| 8 | AAA / Authentication | Step 9 |
| 9 | Lifecycle & Refresh Roadmap | Step 10 |
| 10 | Vendor Consolidation Opportunity | Step 11 |
| 11 | Recommended Actions | Prioritized |
| 12 | Data Gaps | Step 12 manual-verification appendix |

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | Network infrastructure, not endpoint. |
| CIS Controls (v8.1) | ✅ | CIS 12.1 (asset inventory), 12.5 (AAA), 12.6 (mgmt protocols), 12.8 (OOB mgmt), 4.4, 13.1, 15.1 / 15.7 (wireless segregation + auth), 13.6 (IDS for network monitoring). |
| Cyber-insurance domain files | ✅ | `domains/network.md` Q19–Q21, Q35–Q36 — firewall + network infrastructure questions. |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this when network infrastructure is deployed; surfaces firmware-currency rollup + mgmt-exposure + refresh roadmap for the AM conversation. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| Multiple network vendors deployed | "Customer uses <N> network-infrastructure vendors. Consolidation candidate — recommended target is <MSP standard>. Estimated savings: simpler ops + tighter standards." |
| Firmware out of date (vendor-wide) | "Vendor <V> running <N> months behind. Schedule firmware-update window." |
| Devices near EOL/EOS | "<N> devices within <N> months of EOL/EOS. Refresh roadmap entry required." |
| Telnet enabled (any device) | "URGENT: <N> devices have Telnet enabled. Disable across fleet." |
| SSH v1 / HTTP mgmt | "URGENT: <N> devices accept SSH v1 / HTTP mgmt. Force v2 / HTTPS only." |
| SNMP weak community | "URGENT: <N> devices use weak SNMP communities. Replace with v3 or strong v2c per allowlist." |
| Mgmt without ACL | "<N> devices' mgmt accepts any source. Configure mgmt allowlist." |
| Default admin enabled | "URGENT: <N> devices have default admin enabled. Rename + rotate across fleet." |
| AAA local-only | "<N> devices on local-only AAA. Configure RADIUS / TACACS+ as primary." |
| VLAN sprawl | "<N> VLANs configured but unused across multiple switches. Cleanup opportunity." |
| VLAN inconsistency | "VLAN <X> configured on <N> switches but missing from <N> others. Reconcile to MSP-standard baseline." |
| Open / weak SSID | "URGENT: <N> SSIDs use open / WEP / WPA1. Upgrade to WPA2 minimum (WPA3 preferred)." |
| Guest isolation off | "<N> guest networks lack L2 isolation. Enable per MSP baseline." |
| Syslog / NTP missing | "<N> devices not configured for syslog / NTP. Configure central log target + NTP." |

---

## Data gaps & coverage notes

Inherits per-vendor data gaps. Rollup-specific:

| Field | Status | Source if missing |
|---|---|---|
| Cross-vendor port-by-port traffic counters | external | Per-vendor consoles + NMS (Auvik / Domotz) |
| Network topology / LLDP cross-vendor | partial | Per-vendor consoles or dedicated topology tool |
| Wireless heatmap / coverage | external | Wireless-design tool |
| Per-tenant refresh cost figures | external (unless MSP populates) | MSP PSA / accounting |
| Per-vendor PSIRT / advisory applicability | external | Per-vendor advisory portals |

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST + liongard_system LIST | per-vendor queries | array<system> | ok per vendor |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3 | liongard_device LIST | envId=<ENV_ID> [class filter] | array<device> | ok |
| 4 | (chain per-vendor singles) | per single-system recipe | per-recipe findings | ok per vendor |
| 5-11 | (per-area rollups — derived) | per slas | aggregations | ok |
| 12 | QA pass | per `reference/qa-retry-pattern.md` | varies | ok |
| 13 | render | per `output.format` | <artifact path> | ok |
```

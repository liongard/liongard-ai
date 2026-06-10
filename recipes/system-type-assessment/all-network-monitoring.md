---
name: system-type-all-network-monitoring
description: >
  Use this skill when the user wants a unified network-monitoring and
  device-discovery posture across all network monitoring tools deployed
  at the customer — Auvik, Domotz, Datto Networking, and Liongard's
  built-in Network Discovery agent. Trigger phrases: "what's on the
  network", "network device inventory for <customer>", "Auvik and Domotz
  combined view", "network monitoring posture", "ISP and gateway audit",
  "device discovery across all monitors", "network availability review",
  "which network monitoring tools are deployed".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_launchpoint, liongard_metric"
personas: [noc, technical-alignment-manager, vcio-account-manager]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  - metrics:autodiscovery-inspector:alive-host-count
  - metrics:autodiscovery-inspector:alive-hosts-without-hostname-count
  - metrics:autodiscovery-inspector:dhcp-servers
  - metrics:autodiscovery-inspector:dns-servers
  - metrics:autodiscovery-inspector:external-ip
  - metrics:autodiscovery-inspector:gateway-ip
  - metrics:autodiscovery-inspector:host-port-matrix
  - metrics:autodiscovery-inspector:hosts-with-open-ports-count
  - metrics:autodiscovery-inspector:isp
  - metrics:autodiscovery-inspector:network-info
  - metrics:autodiscovery-inspector:subnet-slash-notation
  - metrics:autodiscovery-inspector:total-host-count
  - metrics:auvik-inspector:child-alert-count
  - metrics:auvik-inspector:child-configuration-count
  - metrics:auvik-inspector:child-device-count
  - metrics:auvik-inspector:child-entity-audit-count
  - metrics:auvik-inspector:child-network-count
  - metrics:auvik-inspector:device-ip-summary
  - metrics:auvik-inspector:device-warranty-summary
  - metrics:auvik-inspector:expired-device-service-coverage-status-count
  - metrics:auvik-inspector:expired-device-service-coverage-status-list
  - metrics:auvik-inspector:expired-device-warranty-coverage-status-count
  - metrics:auvik-inspector:expired-device-warranty-coverage-status-list
  - metrics:auvik-inspector:known-interface-summary
  - metrics:auvik-inspector:network-summary
  - metrics:auvik-inspector:parent-tenant-count
  - metrics:auvik-inspector:parent-tenant-roster
  - metrics:auvik-inspector:scan-disabled-network-count
  - metrics:auvik-inspector:unknown-device-count
  - metrics:auvik-inspector:unknown-device-list
  - metrics:auvik-inspector:windows-7-workstation-count
  - metrics:auvik-inspector:windows-7-workstations-list
  - metrics:datto-networking-inspector:api-only-user-count
  - metrics:datto-networking-inspector:legacy-network-count
  - metrics:datto-networking-inspector:network-count
  - metrics:datto-networking-inspector:network-inventory
  - metrics:datto-networking-inspector:networks-with-down-gateway-count
  - metrics:datto-networking-inspector:total-node-count
  - metrics:datto-networking-inspector:user-count
  - metrics:datto-networking-inspector:user-inventory
  - metrics:domotz-inspector:agent-connection-consumption
  - metrics:domotz-inspector:agent-status
  - metrics:domotz-inspector:api-usage
  - metrics:domotz-inspector:device-count
  - metrics:domotz-inspector:device-inventory
  - metrics:domotz-inspector:rtd-stats
---

# System-Type Assessment — All Network Monitoring

> Unified device-discovery and network-availability posture across every
> network monitoring inspector deployed at the customer. Covers
> host/device discovery, availability polling, ISP/gateway identity,
> firmware currency, and open-port exposure — from both agent-based
> scanners and cloud-connected monitoring platforms.
>
> **Inspectors covered:**
>
> | Inspector | ID | Recipe | What it contributes |
> |---|---|---|---|
> | Auvik Network Management | 62 | `recipes/single-system-analysis/by-inspector/auvik.md` | VLAN topology, network devices, interfaces, configurations, alerts (parent/child) |
> | Domotz Network Monitoring | 88 | `recipes/single-system-analysis/by-inspector/domotz.md` | Continuous device availability, RTD/packet-loss stats, WAN IP, agent health |
> | Datto Networking | 79 | `recipes/single-system-analysis/by-inspector/datto-networking.md` | Managed network sites, node firmware, gateway health |
> | Network Discovery | 41 | `recipes/single-system-analysis/by-inspector/network-discovery.md` | Subnet sweep, live host inventory, open ports, ISP, gateway |
>
> **Relationship to other rollups:**
> - `all-network-infrastructure.md` — covers Layer 2/3 switch + router
>   configuration (firmware, VLANs, ACLs). Network monitoring tools
>   surface *what exists*; network infrastructure tools surface *how it's
>   configured*.
> - `all-firewalls.md` — firewall posture (WAN rules, VPN, security
>   services). Datto Networking gateway nodes are noted here as context
>   but not duplicated.
> - `all-external-attack-surface.md` — the external view of the same
>   network boundary (internet-facing IPs, TLS, DNS). Network monitoring
>   tools surface the internal view.
>
> **References:** `reference/inspector-aliases.md`,
> `reference/qa-retry-pattern.md`.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-network-monitoring-posture-<date>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  tool_inventory: "Network Monitoring Tools Deployed"
  device_discovery: "Discovered Device Inventory"
  availability: "Availability & Packet Loss"
  open_ports: "Open Port Exposure (Internal)"
  gateway_isp: "Gateway & ISP Identification"
  firmware: "Firmware Currency (Datto Networking)"
  access_audit: "Monitoring Tool Access Audit"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"   # technical | balanced | executive

inspectors:
  auvik: true        # set false if Auvik not deployed
  domotz: true       # set false if Domotz not deployed
  datto_networking: true
  network_discovery: true

slas:
  # Inherited from config/msp-config.yaml where applicable; overrides here
  prohibited_open_ports: [21, 23, 3389, 445, 1433, 5432, 3306]
  packet_loss_threshold_pct: 5
  agent_offline_is_finding: true        # Domotz agent OFFLINE = active finding
  down_gateway_nodes_max: 0             # Datto Networking
  firmware_drift_flag: true             # flag when networks have different firmware versions
  new_host_flag_days: 7                 # Network Discovery — flag hosts seen < N days
  scan_disabled_flag: true              # Auvik — flag networks with scanStatus = "notAllowed"
```

---

## When to use

- "What devices are on the network at <customer>?"
- "Are any Domotz or Auvik agents offline?"
- "Network monitoring posture for <customer>"
- "ISP, gateway, and DNS audit"
- "Are there any open risky ports inside the network?"
- "Datto Networking site health for <customer>"
- "Which network monitoring tools does <customer> have deployed?"
- "QBR network monitoring section"

Cadence: monthly for availability and device-count delta; ad-hoc for
incident-driven investigation (device gone offline, unauthorized host
detected, ISP change).

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Auvik system IDs (parent + child) | If Auvik deployed | `liongard_launchpoint LIST inspectorId=62` |
| Domotz system ID(s) | If Domotz deployed | `liongard_launchpoint LIST inspectorId=88` |
| Datto Networking system ID | If deployed | `liongard_launchpoint LIST inspectorId=79` |
| Network Discovery system ID(s) | If deployed | `liongard_launchpoint LIST inspectorId=41` |

> **Multiple systems per inspector.** Auvik may have one parent + multiple
> child systems (one per tenant). Domotz has one system per agent/probe.
> Network Discovery has one system per deployment point (one per subnet
> sweep agent). Iterate over all systems of each type.

---

## Workflow

### Step 1 — Resolve environment and discover which tools are deployed

```
liongard_environment LIST searchMode=keyword query="<customer>"
```

Then for each enabled inspector, list deployed systems:

```
liongard_launchpoint LIST environmentId=<ENV_ID> inspectorId=62   # Auvik
liongard_launchpoint LIST environmentId=<ENV_ID> inspectorId=88   # Domotz
liongard_launchpoint LIST environmentId=<ENV_ID> inspectorId=79   # Datto Networking
liongard_launchpoint LIST environmentId=<ENV_ID> inspectorId=41   # Network Discovery
```

Build a deployment table:

| Tool | Systems found | Status |
|---|---|---|
| Auvik | N (1 parent + M children) | Active / Setup Issue |
| Domotz | N agents | Active / Offline |
| Datto Networking | N | Active / Failure |
| Network Discovery | N | Active |

Flag any tool in `inspectors.*: true` (enabled in customization) that
returns 0 systems — **coverage gap**.

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

Flag any network monitoring inspector with data older than
`slas.inspector_lastseen_days_max` (from `config/msp-config.yaml`).
Stale network monitoring data misses new devices and active outages.

### Step 3 — Auvik: tenant roster and topology (if deployed)

**Parent system:**

```
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<AUVIK_PARENT_ID>
  description="Count Auvik tenants and list each tenant's domainPrefix and tenantType"
# Validated path: length(Tenants) → integer
# Validated path: Tenants[].{type: type, id: id,
#                             domainPrefix: attributes.domainPrefix,
#                             tenantType: attributes.tenantType}
#   tenantType: "multiClient" | "client"
```

**For each child system** (one per tenant):

```
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<AUVIK_CHILD_ID>
  description="Show tenant name, ID, and count of networks with their scan status"
# Validated paths:
#   SystemInfo.TenantName → string
#   SystemInfo.TenantID   → string
#   length(Networks)      → integer
#   Networks[].attributes.{networkType: networkType, networkName: networkName,
#                           description: description, scanStatus: scanStatus,
#                           lastModified: lastModified}
#     scanStatus: "notAllowed" (scan disabled) or other values
```

Flag networks where `scanStatus = "notAllowed"` — device discovery is
blocked on those VLANs. Note: `Devices`, `Interfaces`, `Configurations`,
and `Alerts` arrays are schema-confirmed but require active scanning to
populate. If all networks show `scanStatus = "notAllowed"`, Auvik's
topology data will be empty.

### Step 4 — Domotz: agent health and device inventory (if deployed)

For each Domotz system (one per probe/agent):

```
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<DOMOTZ_SYS_ID>
  description="Show agent display_name, status value, WAN IP, version, licence type and expiration"
# Validated path:
#   Agent.{display_name: display_name, status_value: status.value,
#           wan_ip: wan_info.ip, wan_hostname: wan_info.hostname,
#           version_agent: version.agent, version_package: version.package,
#           licence_type: licence.type, licence_expiration_time: licence.expiration_time,
#           timezone: timezone}
#   status.value: "ONLINE" | "OFFLINE" (uppercase string)

liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<DOMOTZ_SYS_ID>
  description="Count total devices and list each device's display_name, type label, status, IP addresses, MAC, and vendor"
# Validated path:
#   length(Devices) → integer
#   Devices[].{display_name: display_name, type_label: type.label,
#              status_value: status.value, ip_addresses: ip_addresses,
#              hw_address: hw_address, vendor: vendor, model: model}
#   type.label: string or null; status.value: string or null

liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<DOMOTZ_SYS_ID>
  description="Show RTD stats per device including device_name, avg_median, latest_lost_packet_count, latest_sent_packet_count"
# Validated path:
#   AgentRTDStats[].{device_name: device_name, avg_median: avg_median,
#                    latest_lost_packet_count: latest_lost_packet_count,
#                    latest_sent_packet_count: latest_sent_packet_count}
#   avg_median: decimal string (can be null); counts: integers
```

Flag:
- Agent `status.value = "OFFLINE"` — agent not reporting (per `slas.agent_offline_is_finding`)
- Device `latest_lost_packet_count / latest_sent_packet_count > slas.packet_loss_threshold_pct / 100`
- Licence `expiration_time` within `slas.licence_expiration_warn_days`
- Devices with `type.label = null` — unidentified device type

### Step 5 — Datto Networking: site and node health (if deployed)

```
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<DATTO_NET_ID>
  description="List all networks with name, networkgroup_name, node_count, new_nodes, down_gateway, down_repeater, latest_firmware_version, latest_firmware_version_full, spare_nodes, is_legacy"
# Validated path:
#   length(Networks) → integer
#   sum(Networks[].node_count) → integer (total nodes)
#   length(Networks[?down_gateway > `0`]) → integer (networks with down gateway)
#   Networks[].{name: name, networkgroup_name: networkgroup_name,
#               is_legacy: is_legacy, node_count: node_count,
#               new_nodes: new_nodes, down_gateway: down_gateway,
#               down_repeater: down_repeater,
#               latest_firmware_version: latest_firmware_version,
#               latest_firmware_version_full: latest_firmware_version_full,
#               spare_nodes: spare_nodes}

liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<DATTO_NET_ID>
  description="List all users with name, email, role_id, verified, and api_only"
# Validated path:
#   length(Users) → integer
#   Users[].{name: name, email: email, role_id: role_id,
#             verified: verified, api_only: api_only}
```

Flag:
- `down_gateway > 0` on any network (per `slas.down_gateway_nodes_max: 0`)
- Firmware version drift across networks (compare `latest_firmware_version_full` integers)
- `is_legacy: true` networks
- `api_only: true` users — confirm legitimate service accounts

### Step 6 — Network Discovery: host inventory and open ports (if deployed)

For each Network Discovery system (one per deployment point):

```
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<ND_SYS_ID>
  description="Show full NetworkInfo including ExternalIP, ISP, GatewayIP, GatewayVendor, DNSServers, LocalMachineIP, subnet mask and slash notation, MAC, ExternalDNS"
# Validated path:
#   NetworkInfo.{ExternalIP: ExternalIP, ISP: ISP, GatewayIP: GatewayIP,
#                GatewayVendor: GatewayVendor, DNSServers: DNSServers,
#                LocalMachineIP: LocalMachineIP,
#                SubnetMask: LocalMachineIPSubnetMask,
#                SlashNotation: LocalMachineIPSubnetMaskSlashNotation,
#                MAC: LocalMachineMac, ExternalDNS: ExternalDNS}

liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<ND_SYS_ID>
  description="Count alive hosts, count hosts with at least one open port, and count total hosts discovered"
# Validated paths:
#   length(Hosts) → integer
#   length(Hosts[?Alive == `true`]) → integer
#   length(Hosts[?Ports[?Status == 'open']]) → integer

liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<ND_SYS_ID>
  description="List all hosts with their IP, hostname, alive status, and all ports with their status"
# Validated path:
#   Hosts[].{Ip: Ip, Hostname: Hostname, Alive: Alive, Ports: Ports}
#   Ports[]: {Port: string ("21"|"22"|"80"|"161"|"443"), Status: "open"|"closed"}
```

For each host with any `Status = 'open'` port, evaluate against
`slas.prohibited_open_ports`. Flag prohibited ports as Critical findings.

Also pull DHCP server detection:
```
# Validated path: DHCPServers → array (empty when no DHCP servers detected on subnet)
```

### Step 7 — Cross-tool synthesis

Produce a consolidated summary table:

| Signal | Source | Finding |
|---|---|---|
| Total devices discovered | ND + Domotz + Auvik | N devices across M subnets |
| Device count vs. expected | ND | New hosts in last 7 days: N |
| Availability issues | Domotz | N devices with packet loss > threshold |
| Offline agents | Domotz | N agents OFFLINE |
| Down nodes | Datto Net | N networks with gateway down |
| Open risky ports | ND | N hosts with prohibited ports open |
| Scan blocked | Auvik | N VLANs with scanStatus = "notAllowed" |
| Firmware drift | Datto Net | N networks behind latest firmware |
| Tool coverage gap | All | Inspectors enabled but 0 systems |

### Step 8 — QA pass (per `reference/qa-retry-pattern.md`)

1. Retry nulls on Agent.status.value (Domotz) — transient API delay
2. Flag stale inspectors aggressively (Step 2)
3. Verify Auvik child count matches Tenants[] from parent
4. Cross-reference Network Discovery host count with Domotz device count —
   large divergence may indicate different subnet scope or stale data
5. Confirm Datto Networking networks with `node_count = 0` are intentional
   (decommissioned vs. misconfigured)

### Step 9 — Render output

| Mode | Best for |
|---|---|
| `markdown` | Working draft / NOC investigation |
| `word` | Customer-facing network health report |
| `pptx` | vCIO QBR network section |
| `xlsx` | Multi-site device count delta tracking |

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | Covers network monitoring tool deployment questions (which tools are active, how many devices monitored, gateway/ISP documentation), and the subnet/device-count baseline used in all future QBR deltas. |
| CIS Controls (v8.1) | ✅ | CIS 1.1 (hardware asset inventory — combined device list from all 4 inspectors), 4.4 (network port/protocol/service management — ND open-port audit), 12.2 (network boundary — gateway + WAN IP from ND, down-node from Datto), 13.1 (intrusion detection — new host detection via ND, device availability via Domotz), 13.6 (network infrastructure management — Auvik topology + Datto firmware). |
| Cyber-insurance domain files | ✅ | `domains/network.md` (gateway health, subnet topology, WAN identification — all 4 inspectors), `domains/endpoint.md` (discovered host count cross-reference for EDR coverage gap detection), `domains/governance.md` (network monitoring tool documentation — which tools are deployed and active). |
| QBR / quarterly-business-review | ✅ | QBR chains this rollup for the network monitoring section. Device count delta (ND + Domotz), availability KPIs (Domotz packet loss), site health (Datto), and topology accuracy (Auvik) are standard QBR network findings. |

---

## Insights & recommendations — generation patterns

| Pattern | Recommendation template |
|---|---|
| Domotz agent OFFLINE | "URGENT: Domotz agent <name> is OFFLINE. Network availability monitoring has a gap since <last-seen>. Investigate agent connectivity." |
| Device packet loss > threshold | "<device_name> shows <N>% packet loss over last polling window. Investigate switch port, cable, or NIC issue." |
| Network Discovery: prohibited port open | "Host <ip> (<hostname>) exposes port <port> internally. Verify legitimate use case; restrict access if not required." |
| Auvik scan blocked on all VLANs | "Auvik has scan permission disabled on all VLANs. Grant scan access in Auvik to enable device topology discovery." |
| Datto Networking gateway node down | "URGENT: Gateway node down at site <name>. Users at this site may have no internet connectivity. Check physical connectivity and power." |
| Firmware drift across Datto sites | "Site <name> is on firmware <old>; other sites are on <latest>. Schedule upgrade to close firmware drift." |
| Legacy network flag | "Network <name> is marked legacy in Datto Networking. Evaluate migration to current platform." |
| New host detected | "New host <ip> detected on subnet within the last 7 days. Confirm authorized device; investigate if unexpected." |
| Licence expiring (Domotz) | "Domotz agent <name> licence expires <date>. Renew before expiry to avoid monitoring gap." |
| No network monitoring tools deployed | "No Auvik, Domotz, Datto Networking, or Network Discovery system found. Network device discovery and availability monitoring is a gap. Recommend deploying at least one monitoring tool." |
| Tool gap (inspector enabled, 0 systems) | "Monitoring tool <name> is expected but no active system found for this environment. Investigate deployment." |

---

## Data gaps & coverage notes

| Gap | Source | Mitigation |
|---|---|---|
| Auvik device/interface topology | Auvik (schema-confirmed, scan required) | Grant scan permission on blocked VLANs; data populates once scanning is active |
| Domotz device open_ports per device | Domotz (schema-confirmed, SNMP config required) | Enable SNMP polling in Domotz agent settings |
| Domotz AgentEyesSNMP / AgentEyesTCP custom monitors | Domotz (schema-confirmed, empty in test) | Configure custom eyes monitors in Domotz if needed |
| Network Discovery UDP scanning | ND (port 161 SNMP only) | Port scan covers TCP 21/22/80/443 + UDP 161 only; full port coverage requires dedicated scanner |
| Network Discovery IPv6 | ND | IPv6 hosts not scanned; complement with dedicated IPv6 discovery if required |
| Datto Networking node-level detail (MAC, IP, serial) | Datto Net (parent inspector) | Node detail visible in Datto Networking portal or potential child inspector |
| DHCP lease table detail | ND | `DHCPServers` array populated only when DHCP server is detected on the same subnet |

---

## Output format

Default `markdown`. Switch per audience.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | query=<customer> | array<environment> | ok |
| 1 | liongard_launchpoint LIST | envId=<ENV_ID> inspectorId=62 | array<launchpoint> | ok |
| 1 | liongard_launchpoint LIST | envId=<ENV_ID> inspectorId=88 | array<launchpoint> | ok |
| 1 | liongard_launchpoint LIST | envId=<ENV_ID> inspectorId=79 | array<launchpoint> | ok |
| 1 | liongard_launchpoint LIST | envId=<ENV_ID> inspectorId=41 | array<launchpoint> | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3 | liongard_metric GENERATE_AND_EVALUATE | Auvik parent: Tenants[].{...} | array(9) | VALIDATED |
| 3 | liongard_metric GENERATE_AND_EVALUATE | Auvik child: SystemInfo.TenantName/TenantID, Networks[].attributes.{...} | object/array | VALIDATED |
| 4 | liongard_metric GENERATE_AND_EVALUATE | Domotz: Agent.{...} | object | VALIDATED |
| 4 | liongard_metric GENERATE_AND_EVALUATE | Domotz: Devices[].{...}, length(Devices) | array/integer | VALIDATED |
| 4 | liongard_metric GENERATE_AND_EVALUATE | Domotz: AgentRTDStats[].{...} | array | VALIDATED |
| 5 | liongard_metric GENERATE_AND_EVALUATE | Datto: Networks[].{...}, length/sum/count | array/integers | VALIDATED |
| 5 | liongard_metric GENERATE_AND_EVALUATE | Datto: Users[].{...} | array | VALIDATED |
| 6 | liongard_metric GENERATE_AND_EVALUATE | ND: NetworkInfo.{...} | object | VALIDATED |
| 6 | liongard_metric GENERATE_AND_EVALUATE | ND: length(Hosts), Alive count, open-port count | integers | VALIDATED |
| 6 | liongard_metric GENERATE_AND_EVALUATE | ND: Hosts[].{Ip,Hostname,Alive,Ports} | array | VALIDATED |
| 7 | (cross-tool synthesis — derived) | all above | summary table | ok |
| 8 | QA pass | per `reference/qa-retry-pattern.md` | varies | ok |
| 9 | render | per `output.format` | <artifact path> | ok |
```

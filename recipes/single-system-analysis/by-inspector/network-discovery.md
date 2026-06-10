---
name: single-system-network-discovery
description: >
  Use this skill when the user wants a Network Discovery assessment for a
  single subnet — internal host inventory, open-port audit, gateway/ISP
  identification, DNS server mapping, DHCP server detection, or new-device
  detection. Trigger phrases: "subnet sweep for <customer>", "what devices
  are on the network at <customer>", "open ports inside the network at
  <customer>", "ISP identification for <customer>", "gateway and DNS
  inventory for <customer>", "new device detection at <customer>",
  "network discovery report for <customer>". Agent-deployed, runs from
  inside the customer network; one system per agent/subnet deployment point.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_launchpoint, liongard_metric, liongard_timeline"
personas: [noc, soc, vcio-account-manager, technical-alignment-manager]
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
---

# Single-System Analysis — Network Discovery

> **Inspector:** `autodiscovery-inspector` (ID 41). Network category.
> **One system per deployment point (per agent/subnet).** Runs a subnet
> sweep from inside the customer network via the Liongard agent. Discovers
> all live hosts, resolves hostnames, probes a fixed set of ports (21 FTP,
> 22 SSH, 80 HTTP, 161 SNMP, 443 HTTPS), and identifies the gateway, ISP,
> external DNS, and local machine details. No credentials used — the agent
> scans from the inside, so findings reflect network-layer exposure only.
>
> **References:** `reference/inspector-aliases.md` (Network Discovery,
> autodiscovery). Pairs with firewall-inspector recipes (SonicWall,
> FortiGate, Meraki) for a complete internal + perimeter picture. Feeds
> the `recipes/domain-assessment/network.md` domain file and the
> `recipes/system-type-assessment/all-network.md` rollup.


---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-network-discovery-<subnet>-<date>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary:   "Executive Summary"
  network_identity:    "Network Identity"
  host_inventory:      "Host Inventory"
  open_port_audit:     "Open Port Audit"
  hostname_gaps:       "Hosts Without Hostnames"
  dhcp_servers:        "DHCP Server Discovery"
  insights:            "Key Insights"
  recommendations:     "Recommended Actions"
  data_gaps:           "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"                  # technical | balanced | executive

slas:
  prohibited_open_ports:
    - 21    # FTP — cleartext file transfer
    - 22    # SSH — acceptable only on known admin/jump hosts; flag all others
    - 23    # Telnet — plaintext, must not be open anywhere
    - 3389  # RDP — must not be open to internal networks without explicit exception
    - 445   # SMB — flag all; never open to non-trusted subnets
    - 1433  # MSSQL — flag all non-server hosts
    - 5432  # Postgres — flag all non-server hosts
    - 3306  # MySQL — flag all non-server hosts
  acceptable_ports:
    - 80    # HTTP — acceptable on known web/app servers
    - 443   # HTTPS — acceptable on known web/app servers
    - 53    # DNS — acceptable only on hosts identified as DNS servers via NetworkInfo.DNSServers
  flag_new_hosts_since_days: 7
  flag_hosts_without_hostname: true
  inspector_lastseen_days_max: 7    # inherits from config/msp-config.yaml

reporting_period:
  default: "current_state"          # snapshot; new-host delta derived from timeline

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

- "Subnet sweep for `<customer>`"
- "What devices are on the network at `<customer>`?"
- "Open ports inside the network"
- "ISP identification / gateway inventory for `<customer>`"
- "DNS server mapping for `<customer>`"
- "New device detection — what joined the network this week?"
- "DHCP server discovery at `<customer>`"
- "Network discovery report for `<customer>`"
- Pre-onboarding network baselining

Cadence: on-demand; weekly delta review for new-host detection; monthly
for open-port audits; ad-hoc after network changes.

Personas:
- **NOC** (primary — host inventory, new-device alerts, open-port triage)
- **TAM** (network baselining during onboarding and QBRs)
- **SOC** (lateral-movement surface assessment, prohibited-port enforcement)
- **vCIO / Account Manager** (network topology summary for QBR decks;
  ISP/gateway health narrative)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` → match by customer name |
| System ID (the specific Network Discovery system for this subnet) | Yes — one per subnet/agent | `liongard_launchpoint LIST inspectorId=41` |
| Optional: subnet label / site name | No | User prompt — for filename and report header |
| Optional: focus area | No | User prompt — e.g., "focus on prohibited ports only" |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_launchpoint LIST inspectorId=41 environmentId=<ENV_ID>
```


Each system represents one agent's subnet sweep. Confirm the target
system ID before proceeding — running against the wrong system produces
findings for the wrong subnet.

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

Check `lastSeen` for the Network Discovery system. A stale scan means
new devices, port changes, and ISP changes are invisible. Flag if older
than `slas.inspector_lastseen_days_max` (default 7 days from
`config/msp-config.yaml`).

### Step 3 — Network identity

Pull all `NetworkInfo` fields in a single call. All paths below are
**VALIDATED** against live system data.

```
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  jmesPath="NetworkInfo.{ExternalIP: ExternalIP, ISP: ISP,
             GatewayIP: GatewayIP, GatewayVendor: GatewayVendor,
             DNSServers: DNSServers, LocalMachineIP: LocalMachineIP,
             SubnetMask: LocalMachineIPSubnetMask,
             SlashNotation: LocalMachineIPSubnetMaskSlashNotation,
             MAC: LocalMachineMac, ExternalDNS: ExternalDNS}"
```

Expected result shape:
- `ExternalIP`: `<string>` — the customer's outbound public IP
- `ISP`: `<string>` — ISP name as identified by the external IP
- `GatewayIP`: `<string>` — internal default gateway address
- `GatewayVendor`: `<string>` — gateway vendor name (may be empty; see Data Gaps)
- `DNSServers`: `<array of IP strings>` — internal DNS servers seen by the agent
- `LocalMachineIP`: `<string>` — IP of the Liongard agent host
- `LocalMachineIPSubnetMask`: `<string>` — subnet mask (dotted-decimal)
- `LocalMachineIPSubnetMaskSlashNotation`: `<integer>` — e.g., 24 for /24
- `LocalMachineMac`: `<string>` — MAC address of the agent host
- `ExternalDNS`: `<array of strings>` — external DNS resolvers

Surface in the **Network Identity** section of the output. Compare
`ISP` against the customer's expected ISP (from onboarding intake or
prior reports) and flag mismatches.

### Step 4 — Host inventory counts

Pull total host count, alive host count, and hosts with at least one
open port. All paths are **VALIDATED**.

```
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  jmesPath="length(Hosts)"

liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  jmesPath="length(Hosts[?Alive == `true`])"

liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  jmesPath="length(Hosts[?Ports[?Status == 'open']])"
```

Expected result shapes: `<integer>` for each call.

Surface as KPI counts in the **Host Inventory** section:
- Total hosts discovered
- Alive hosts (responding to scan)
- Hosts with at least one open port

### Step 5 — Open port analysis

Pull the full host-port matrix for all hosts. Path is **VALIDATED**.

```
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  jmesPath="Hosts[].{Ip: Ip, Hostname: Hostname, Alive: Alive, Ports: Ports}"
```

Expected result shape: `<array>` — each element has:
- `Ip`: `<string>`
- `Hostname`: `<string>` (may be empty — see Step 6)
- `Alive`: `<bool>`
- `Ports`: `<array>` — each element: `{Port: "21"|"22"|"80"|"161"|"443", Status: "open"|"closed"}`

**Port evaluation logic:**

For each host, filter `Ports[?Status == 'open']` client-side and
evaluate each open port against the SLA lists:

| Port | Status | Rule |
|------|--------|------|
| 21 (FTP) | `open` | Prohibited — flag Critical |
| 22 (SSH) | `open` | Prohibited by default — flag unless host is a known admin/jump host (manual exception) |
| 23 (Telnet) | `open` | Prohibited — flag Critical |
| 80 (HTTP) | `open` | Acceptable on known web/app servers — flag on workstation-class hosts |
| 161 (SNMP) | `open` | Review — SNMP v1/v2 cleartext risk; flag unless SNMP v3 confirmed |
| 443 (HTTPS) | `open` | Acceptable on known web/app servers |
| 3389 (RDP) | `open` | Prohibited — flag Critical |
| 445 (SMB) | `open` | Prohibited — flag Critical |
| 1433 (MSSQL) | `open` | Prohibited on non-server hosts — flag |
| 5432 (Postgres) | `open` | Prohibited on non-server hosts — flag |
| 3306 (MySQL) | `open` | Prohibited on non-server hosts — flag |

For port 53 (DNS): acceptable only on hosts whose IP appears in
`NetworkInfo.DNSServers`; flag if open on non-DNS hosts.

Note: The scanner probes ports 21, 22, 80, 161, and 443 only. Ports
23, 3389, 445, 1433, 5432, and 3306 are in the SLA prohibited list for
policy completeness but will not appear in the scanned `Ports` array
(they are outside the fixed probe set — see Data Gaps).

### Step 6 — Hostname gap analysis

Identify hosts with empty or missing hostnames. Path is **VALIDATED**
(derived from the same array pulled in Step 5).

Client-side filter after the Step 5 pull:
```
Hosts[?Alive == `true` && (Hostname == '' || !Hostname)]
```

Or as a standalone call:
```
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  jmesPath="length(Hosts[?Alive == `true` && Hostname == ''])"
```

Flag `flag_hosts_without_hostname: true` per SLA. Hosts without
hostnames are harder to attribute to a known asset — cross-reference
IP against `liongard_device LIST ipAddress=<IP>` to attempt
identification. Unresolvable hosts should be flagged for manual triage
(could be shadow IT, IoT, or unmanaged devices).

### Step 7 — DHCP server discovery

Pull DHCP server array. Path is **VALIDATED** (may return empty array
when no DHCP server is detected on the scanned subnet).

```
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  jmesPath="DHCPServers"
```

Expected result shape: `<array>` — empty array when no DHCP servers
detected; array of DHCP server objects when found.

Evaluation:
- **Empty array**: DHCP server not detected on this subnet. Either DHCP
  is served from a different subnet (relay), or the customer uses static
  assignments only. Note in the output; do not flag as a finding unless
  the context indicates a missing DHCP server.
- **One entry**: expected for most SMB networks — confirm IP matches
  the expected DHCP server (typically the gateway or a domain controller).
- **Multiple entries**: flag for review — rogue DHCP servers are a
  security concern (DHCP starvation, DNS poisoning via malicious DHCP
  response).

### Step 8 — QA pass

Per `reference/qa-retry-pattern.md`:

1. **Retry persistent nulls.** Re-run any metric call that returned
   `null` up to `qa.retry_attempts` times with `qa.retry_delay_seconds`
   between attempts. Persistent nulls go to the Manual Verification
   appendix.

2. **Flag stale inspector.** Check `lastSeen` (Step 2) against
   `qa.flag_inspector_lastseen_threshold_days`. A stale scan may miss
   new hosts added since last run.

3. **No cross-tool divergence check required** for this recipe — the
   Network Discovery inspector is the sole source for subnet-level data.
   Cross-reference host IPs against `liongard_device LIST ipAddress=<IP>`
   is additive enrichment, not a competing count.

4. **Known data gaps.** This recipe has no (not in current dataprint)
   metrics — all JMESPath paths in use are VALIDATED. See Data Gaps for
   inspector-level scope limitations.

5. **Render the Manual Verification appendix** per
   `reference/qa-retry-pattern.md`. If QA produced zero items, state:
   "✅ All evidence verified — no manual checks needed."

### Step 9 — Render output

| Output mode | Best for |
|---|---|
| `markdown` | Working draft — NOC triage, internal documentation |
| `word` | Customer-facing network assessment letter |
| `pptx` | QBR network topology slide + open-port risk summary |
| `xlsx` | Host inventory sheet with per-port status columns; conditional formatting on prohibited ports |

---

## QA & Manual Verification

Before rendering the report, run the QA pass per
`reference/qa-retry-pattern.md`:

1. **Retry persistent nulls.** For every metric query that returned null
   in Steps 3–7, re-run up to `qa.retry_attempts` times with
   `qa.retry_delay_seconds` between attempts. Cache the result.

2. **Flag stale inspectors.** Compare the Network Discovery system's
   `lastSeen` against `qa.flag_inspector_lastseen_threshold_days`. Add
   stale systems to the manual-verification list.

3. **No cross-tool divergence check** required for counts specific to
   this inspector's scan data.

4. **Surface known proposed-metric gaps.** This recipe has none — all
   paths are VALIDATED. No unvalidated paths used.

5. **Render the Manual Verification appendix** in the deliverable
   (mandatory when `qa.manual_verification_section_required == true`).

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | Covers network inventory questions: gateway IP, ISP, DNS servers, subnet scope (`/`notation), and internal host discovery. All six standard network questions answered from VALIDATED paths. |
| CIS Controls v8.1 | ✅ | CIS 1.1 — Establish and Maintain Detailed Asset Inventory (all discovered hosts); CIS 4.4 — Manage Network Ports, Protocols, and Services (open-port audit against prohibited list); CIS 12.2 — Establish and Maintain a Secure Network Architecture (network boundary: gateway, ISP, subnet mask); CIS 13.1 — Centralize Security Event Alerting (new-host detection supports IDS/monitoring objectives). |
| Cyber-insurance domain files | ✅ | `domains/network.md` — gateway, subnet topology, ISP, DNS server mapping; `domains/endpoint.md` — discovered hosts cross-referenced against managed-device inventory to surface coverage gaps (devices Liongard discovered on the network but not locally inspected). |
| QBR | ✅ | QBR Step 8 chains this recipe for the network topology section. New-host delta between QBRs surfaces unauthorized device additions; open-port changes surface firewall / ACL drift over the quarter. |

---

## Insights & recommendations — generation patterns


| Pattern | Trigger | Recommended action template |
|---|---|---|
| Prohibited port open on internal host | Port 21, 22, 23, 3389, 445, 1433, 5432, or 3306 `Status == 'open'` on any host | "CRITICAL: Port `<port>` (`<service>`) is open on `<host-IP>` (`<hostname>`). Disable the service or restrict access via firewall ACL. Validate no unauthorized service is running on this port." |
| SSH open on non-admin host | Port 22 `open` on host that is not a known admin/jump host | "SSH is open on `<host-IP>`. Confirm whether this is an authorized admin host; if not, disable the SSH service and investigate." |
| SNMP open on host | Port 161 `open` on any host | "SNMP is open on `<host-IP>`. Confirm SNMP v3 is enforced; SNMP v1/v2 uses cleartext community strings and is a known lateral-movement vector." |
| Host with no hostname | `Alive == true` and `Hostname == ''` | "Host `<IP>` is alive but has no resolvable hostname. Cross-reference against device inventory; unidentified hosts may be shadow IT or IoT. Investigate and label, or isolate to a dedicated IoT VLAN." |
| New host detected (within `flag_new_hosts_since_days` window) | Host first observed within the last `<N>` days per timeline delta | "New host `<IP>` (`<hostname if available>`) appeared on the network within the last `<N>` days. Confirm authorized addition; if unrecognized, treat as potential unauthorized device." |
| Unexpected DHCP server | `length(DHCPServers) > 1`, or DHCP server IP does not match expected gateway/DC | "Multiple DHCP servers detected: `<IPs>`. Rogue DHCP servers can redirect traffic or assign malicious DNS. Confirm all DHCP sources are authorized and remove unauthorized ones." |
| ISP mismatch | `NetworkInfo.ISP` does not match the ISP recorded at onboarding | "ISP identified as `<ISP>` but `<expected-ISP>` was expected. Confirm whether the circuit has changed; if unexpected, investigate for unauthorized network path (secondary NIC, rogue AP)." |
| High ratio of unnamed hosts | `length(Hosts[?Hostname == '']) / length(Hosts[?Alive == true]) > 0.2` | "More than 20% of live hosts have no hostname. This reduces asset attribution accuracy. Ensure all managed endpoints have DNS entries or DHCP reservations with hostname binding." |
| All probed ports closed across all hosts | `length(Hosts[?Ports[?Status == 'open']]) == 0` | "No open ports detected on any host in the scanned port set (21, 22, 80, 161, 443). Verify the scan ran successfully and the agent has network-layer reach to the target subnet." |

---

## Data gaps & coverage notes

| Gap | Status | Notes / Supplement |
|---|---|---|
| Port scope limited to 5 probed ports | Inspector limitation | The scanner probes ports 21, 22, 80, 161, and 443 only. Prohibited ports 23, 3389, 445, 1433, 5432, and 3306 are in the SLA list for policy completeness but are outside the scan scope. Supplement with a full-range port scan via nmap or firewall rule review for comprehensive coverage. |
| IPv6 scanning | Not in scope | The inspector scans IPv4 addresses only. IPv6-reachable hosts are not detected. Supplement with a dedicated IPv6 scanner if the customer runs dual-stack. |
| UDP scanning (beyond port 161) | Partial | UDP scanning is limited to port 161 (SNMP ping). Other UDP services (DNS 53, TFTP 69, NTP 123, SNMP traps 162) are not probed. |
| SNMP authentication | Not used | Port 161 is probed as a UDP ping only; no SNMP community string or SNMPv3 credentials are used. Device type and OID data are not available from this inspector. |
| DHCP lease table | Conditional | `DHCPServers` is populated only when a DHCP server is detected responding on the same subnet as the agent. DHCP servers on other subnets reached via relay are not visible. |
| GatewayVendor identification | Partial | `GatewayVendor` may be empty for devices that do not expose vendor information via the gateway ARP/probe. Commercial-grade and some consumer-grade gateways commonly return an empty string. |
| Host classification | Not available | The inspector identifies hosts by IP, hostname (via DNS reverse lookup), and open ports — it does not classify hosts as workstation vs. server vs. printer vs. IoT. Classification requires cross-referencing discovered IPs with `liongard_device LIST ipAddress=<IP>`. |


---

## Output format

Default `markdown` (internal triage). Switch to `word` for the
customer-facing network assessment letter; `pptx` for the QBR topology
section; `xlsx` for the host inventory compliance workbook with
conditional formatting on prohibited open ports.

---

## Verification log

Every recipe run appends this log. The agent records **shapes only** —
no concrete values, IPs, or hostnames.

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | query=<customer> | array<environment> | ok |
| 1 | liongard_launchpoint LIST | inspectorId=41 envId=<ENV_ID> | array<launchpoint> | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3 | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath="NetworkInfo.{...}" | object | VALIDATED |
| 4 | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath="length(Hosts)" | integer | VALIDATED |
| 4 | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath="length(Hosts[?Alive == `true`])" | integer | VALIDATED |
| 4 | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath="length(Hosts[?Ports[?Status == 'open']])" | integer | VALIDATED |
| 5 | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath="Hosts[].{Ip: Ip, Hostname: Hostname, Alive: Alive, Ports: Ports}" | array | VALIDATED |
| 6 | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath="length(Hosts[?Alive == `true` && Hostname == ''])" | integer | VALIDATED |
| 7 | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath="DHCPServers" | array | VALIDATED |
| 8 | QA pass | per reference/qa-retry-pattern.md | varies | ok |
| 9 | render | per output.format | <artifact path> | ok |
```

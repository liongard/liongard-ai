---
name: single-system-domotz-network-monitoring
description: >
  Use this recipe when the user wants a Domotz Network Monitoring assessment
  for a single Domotz agent (probe) — device inventory audit, availability
  and packet-loss analysis, agent health check, WAN IP review, and licence
  expiration tracking. Trigger phrases: "Domotz report for <customer>",
  "network device inventory from Domotz", "Domotz agent health for <site>",
  "which devices are offline in Domotz", "packet loss in Domotz", "Domotz
  licence expiring", "network availability report from Domotz". Credentialed
  — requires an active Domotz account. One system per Domotz agent (probe).
compatibility: "Requires Liongard MCP: liongard_environment, liongard_launchpoint, liongard_metric, liongard_timeline"
inspector_id: 88
inspector_name: "Domotz Network Monitoring"
category: Network
personas: [noc, technical-alignment-manager, vcio-account-manager]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  # Reconciled 2026-05-29: pruned dangling refs not present in the live dataprint (see internal/proposed-metrics-backlog.md).
  - metrics:domotz-inspector:agent-connection-consumption
  - metrics:domotz-inspector:agent-status
  - metrics:domotz-inspector:api-usage
  - metrics:domotz-inspector:device-count
  - metrics:domotz-inspector:device-inventory
  - metrics:domotz-inspector:rtd-stats
---

# Single-System Analysis — Domotz Network Monitoring

> **Inspector:** `domotz` (ID 88). Network category.
> **One system per Domotz agent (probe).** Each Domotz agent monitors all
> devices on its local network with continuous availability polling,
> round-trip delay (RTD) statistics, WAN information, and a live device
> inventory. **Credentialed** — requires a Domotz account and an active,
> ONLINE probe.
>
> **References:** `reference/inspector-aliases.md` (Domotz, Network Monitor).
> Pairs well with firewall and switch inspectors for a full network-layer
> picture. RTD + packet-loss findings complement endpoint availability data
> from the RMM inspector.

---

## When to use

- "Domotz report for \<customer\>"
- "Network device inventory from Domotz"
- "Domotz agent health for \<site\>"
- "Which devices are offline according to Domotz?"
- "Packet loss investigation — Domotz"
- "Domotz licence expiring soon"
- "Network availability baseline for QBR"
- "Unidentified devices on the network"
- Device-gone-offline triage; new-site onboarding network audit

Cadence: monthly for QBR baseline; on-demand for incident triage or
device-offline alerts; quarterly licence-renewal review.

Personas:
- **NOC** (primary — device availability alerts, packet-loss triage,
  agent OFFLINE recovery)
- **TAM / Technical Alignment Manager** (onboarding baseline, device
  inventory gap analysis, licence renewal)
- **vCIO / Account Manager** (QBR — network availability score,
  unidentified-device risk narrative, licence renewal action item)

---

## Customize for your MSP

```yaml
output:
  format: markdown                          # markdown | word | pptx | xlsx
  filename: "<customer>-domotz-<site>-<date>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary:    "Executive Summary"
  agent_health:         "Agent Health"
  device_inventory:     "Device Inventory"
  availability_analysis: "Availability & Packet-Loss Analysis"
  licence_status:       "Licence Status"
  api_usage:            "API Usage"
  recommendations:      "Recommended Actions"
  data_gaps:            "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"                          # technical | balanced | executive
                                            # NOC/TAM: technical.
                                            # vCIO/QBR deck: executive.

slas:
  agent_status_alert: "OFFLINE"             # flag when Agent.status.value == "OFFLINE"
  licence_expiration_warn_days: 30          # warn when licence expires within 30 days
  packet_loss_threshold_pct: 5              # flag device when
                                            #   (latest_lost_packet_count /
                                            #    latest_sent_packet_count) * 100 >= 5

flags:
  flag_unidentified_devices: true           # flag Devices[] entries where type.label is null

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
| System / launchpoint ID (Domotz probe) | Yes — one per recipe run | `liongard_launchpoint LIST inspectorId=88` |
| Optional: focus area | No | User prompt — e.g., "focus on unidentified devices only" |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_launchpoint LIST environmentId=<ENV_ID> inspectorId=88
```

If multiple Domotz probes exist for the same environment (multi-site
customer), confirm which probe/site the user wants before proceeding.
Each probe is a separate system; run the recipe once per site if a
multi-site rollup is needed.

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

Domotz data is near-real-time for device availability (continuous
polling) but the Liongard inspector snapshot captures a point-in-time
export. A stale inspector (> `slas.inspector_lastseen_days_max` days)
means device-status data may be outdated. Flag aggressively; an OFFLINE
device may have come back online since the last snapshot.

### Step 3 — Agent health

Use `liongard_metric GENERATE_AND_EVALUATE` for each path below.
All paths in this step are **VALIDATED** against System A,
dev environment.

```
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  jmesPath="<path>"

# ── VALIDATED ────────────────────────────────────────────────────────

# Agent identity and connectivity snapshot
#   Agent.{display_name: display_name,
#          status_value: status.value,
#          wan_ip: wan_info.ip,
#          wan_hostname: wan_info.hostname,
#          version_agent: version.agent,
#          version_package: version.package,
#          licence_type: licence.type,
#          licence_expiration_time: licence.expiration_time,
#          timezone: timezone}
#
#   display_name              — string; human-readable probe name
#   status.value              — "ONLINE" | "OFFLINE" (uppercase string)
#   wan_info.ip               — string; current WAN IP of the probe
#   wan_info.hostname         — string; reverse-DNS hostname for WAN IP
#   version.agent             — string (e.g. "6.6.5-b001")
#   version.package           — string
#   licence.type              — string (e.g. "SUBSCRIPTION")
#   licence.expiration_time   — ISO 8601 timestamp
#   timezone                  — IANA timezone string (e.g. "America/Chicago")
```

**Key evaluations from agent health data:**

| Signal | Threshold | Severity |
|---|---|---|
| `status.value` == `"OFFLINE"` | Any | Critical — agent unreachable; all device-status data frozen |
| `licence.expiration_time` within warn window | `slas.licence_expiration_warn_days` | Warning |
| `licence.expiration_time` in the past | Any | Critical — licence lapsed |
| WAN IP changed unexpectedly | Compare to prior snapshot | Info — note for change-tracking |

### Step 4 — Device inventory

```
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  jmesPath="<path>"

# ── VALIDATED ────────────────────────────────────────────────────────

# Total device count
#   length(Devices)
#     → integer (e.g. 10)

# Full device list with identity and classification
#   Devices[].{display_name: display_name,
#              type_label: type.label,
#              status_value: status.value,
#              ip_addresses: ip_addresses,
#              hw_address: hw_address,
#              vendor: vendor,
#              model: model}
#
#   display_name    — string; device name as reported by Domotz
#   type.label      — string (e.g. "Media Player", "Notebook",
#                     "Network Equipment", "Mobile", "Appliance",
#                     "Desktop") or null when Domotz has not
#                     classified the device
#   status.value    — string or null (null when not actively polled)
#   ip_addresses    — array of strings (current IPs for this device)
#   hw_address      — MAC address string
#   vendor          — string (OUI-derived vendor name)
#   model           — string or null
```

**Device inventory analysis:**

1. **Total count** — record `length(Devices)` as the baseline device
   count. Delta from prior report is a QBR action item if significant.
2. **Type breakdown** — group `Devices[]` by `type.label`; count per
   type. Include a count of `null` type entries.
3. **Unidentified devices** — when `flag_unidentified_devices: true`,
   surface all devices where `type.label` is null. These are devices
   Domotz has seen on the network but has not classified; they warrant
   manual identification (could be IoT, rogue devices, or newly added
   hardware).
4. **Vendor list** — enumerate unique `vendor` values for context.
5. **OFFLINE devices** — filter `Devices[]` where `status.value` is not
   null and not `"ONLINE"`. Null status means the device is not actively
   polled (no RTD probe); non-null non-ONLINE means Domotz detected an
   outage.

### Step 5 — Availability and packet-loss analysis

```
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  jmesPath="<path>"

# ── VALIDATED ────────────────────────────────────────────────────────

# RTD (round-trip delay) stats per actively polled device
#   AgentRTDStats[].{device_name: device_name,
#                    avg_median: avg_median,
#                    latest_lost_packet_count: latest_lost_packet_count,
#                    latest_sent_packet_count: latest_sent_packet_count}
#
#   device_name               — string; matches Devices[].display_name
#   avg_median                — string (decimal) or null when no data collected yet
#   latest_lost_packet_count  — integer; packets lost in last RTD probe cycle
#   latest_sent_packet_count  — integer; packets sent in last RTD probe cycle
```

**Packet-loss calculation:**

For each entry in `AgentRTDStats[]` where `latest_sent_packet_count > 0`:

```
packet_loss_pct = (latest_lost_packet_count / latest_sent_packet_count) * 100
```

Flag any device where `packet_loss_pct >= slas.packet_loss_threshold_pct`.

Devices with `latest_sent_packet_count == 0` have not been polled yet
in this cycle; note as "no RTD data" rather than a loss event.

Devices present in `Devices[]` but absent from `AgentRTDStats[]` are
not actively polled by Domotz (availability monitoring not enabled for
that device); note as "not polled" in the report.

### Step 6 — Licence expiration

Using the `Agent.licence.expiration_time` value from Step 3:

1. Parse the ISO 8601 timestamp.
2. Compute days until expiration from today's date.
3. Apply `slas.licence_expiration_warn_days` threshold.
4. If expired (negative days), flag as Critical.

> Note: `slas.licence_expiration_warn_days: 30` (recipe-level default).
> The library-wide `slas.license_expiration_warn_days: 60` in
> `config/msp-config.yaml` is a broader default; this recipe uses the
> tighter 30-day threshold appropriate for a cloud-agent subscription.
> Override in your customization block if the MSP standard differs.

### Step 7 — API usage

```
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  jmesPath="<path>"

# ── VALIDATED ────────────────────────────────────────────────────────

# Domotz API daily usage vs. limit
#   API.{daily_limit: daily_limit, daily_usage: daily_usage}
#     → daily_limit: integer; daily_usage: integer

# Agent connection consumption (concurrent connections)
#   AgentConnectionConsumption.{limit: limit, current: current}
#     → limit: integer; current: integer
```

Flag when `daily_usage / daily_limit` approaches or exceeds 80%. High
API usage can indicate integrations (PSA, RMM) polling Domotz frequently;
confirm intentional vs. runaway calls.

### Step 8 — QA pass (per `reference/qa-retry-pattern.md`)

QA checks specific to this recipe:

1. **Agent OFFLINE gate** — if `Agent.status.value == "OFFLINE"`,
   all device-status fields are stale (last-known state). Prominently
   warn the reader; do not present device statuses as current until the
   agent is confirmed back ONLINE.
2. **Retry persistent nulls** — `avg_median` in RTD stats can be null
   for newly added devices; retry once before treating as a data gap.
3. **Unidentified device count cross-check** — confirm null-type count
   in the narrative matches the flagged list. Discrepancies indicate a
   query or filtering error.
4. **Inspector freshness** — confirm `liongard_timeline` shows a recent
   inspection. Stale data is especially misleading for availability
   metrics.
5. **Licence expiration arithmetic** — double-check the day-count
   calculation; off-by-one errors in date math produce false urgency or
   missed warnings.
6. **Proposed-metric gaps** — surface any schema-only fields noted in
   the data gaps section.

### Step 9 — Render output

| Output mode | Best for |
|---|---|
| `markdown` | NOC working draft; internal device inventory |
| `word` | Customer-facing site health letter |
| `pptx` | QBR network availability slide (device count, offline list, packet-loss summary) |
| `xlsx` | Full device inventory with availability columns; sortable by type, vendor, status |

---

## QA & Manual Verification

Per `reference/qa-retry-pattern.md`. Manual checks specific to this recipe:

- **Cross-reference device inventory against known-assets list** —
  unidentified devices (`type.label` null) should be manually confirmed
  against any CMDB / IT Glue asset list. Unknown MAC addresses warrant
  investigation.
- **WAN IP change tracking** — compare current `wan_info.ip` to the
  previous report. Unexpected WAN IP changes can indicate ISP failover,
  BGP prefix change, or a circuit-level event worth noting in the QBR.
- **RTD data freshness** — RTD stats reflect the last probe cycle
  captured at inspection time. Confirm the snapshot timestamp is recent
  before drawing availability conclusions.
- **Domotz Eyes (SNMP/TCP) confirmation** — if the customer has SNMP
  or TCP custom monitors configured, verify whether `AgentEyesSNMP` and
  `AgentEyesTCP` arrays are populated (see Data Gaps section). If empty,
  note that custom monitoring may not be configured.

---

## Insights & recommendations — generation patterns

| Pattern | Recommendation template |
|---|---|
| Agent OFFLINE | "CRITICAL: The Domotz agent at \<site\> is OFFLINE. All device-status data is frozen at the last inspection. Investigate probe connectivity immediately — check WAN link, Domotz cloud reachability, and probe hardware." |
| Device packet loss ≥ threshold | "\<N\> device(s) exceeded the \<threshold\>% packet-loss threshold: \<device list\>. Investigate switch port, cable, Wi-Fi signal, or device NIC. Persistent loss indicates an availability risk." |
| Unidentified device (`type.label` null) | "\<N\> device(s) on the network could not be classified by Domotz. Review MAC addresses against the asset register; any unrecognized device should be investigated as a potential rogue or shadow-IT asset." |
| Licence expiring within warn window | "The Domotz licence for \<site\> expires on \<date\> (\<N\> days). Initiate renewal to avoid an agent OFFLINE event and loss of continuous availability monitoring." |
| Licence expired | "CRITICAL: The Domotz licence for \<site\> has expired. The probe may be OFFLINE or operating in a degraded mode. Renew immediately." |
| API usage approaching limit | "Domotz API daily usage is at \<N\>% of the daily limit. Audit integrations (PSA, RMM, scripts) polling the Domotz API to prevent throttling." |
| Devices not polled (absent from RTD stats) | "\<N\> device(s) are in the inventory but not actively polled for availability. Enable RTD monitoring in Domotz for critical devices (servers, network equipment, printers) to receive outage alerts." |
| Device count delta | "Device count changed from \<prior\> to \<current\> since the last report. Review new additions for authorization and classification; confirm removals are intentional decommissions." |

---

## Coverage cross-check

| Domain / control | Coverage | Notes |
|---|---|---|
| **onboarding-qa-coverage.md** | ✅ | Covers network device inventory and availability monitoring baseline — device count, type distribution, and active polling confirm the onboarding network-layer checklist |
| **CIS Controls v8.1 — 1.1** | ✅ | Hardware asset inventory: `Devices[]` (display_name, hw_address, vendor, model, ip_addresses) provides the Layer-2 device register for the network segment monitored by this probe |
| **CIS Controls v8.1 — 4.4** | schema-only | Network port/service management: `open_ports` per device is present in the Domotz schema but was not populated in test data — depends on SNMP polling configuration; see Data Gaps |
| **CIS Controls v8.1 — 12.2** | ✅ | Network boundary monitoring: `wan_info.ip` and `wan_info.hostname` provide WAN-boundary visibility; device availability polling confirms boundary connectivity |
| **CIS Controls v8.1 — 13.1** | ✅ | Network monitoring and defense: `AgentRTDStats[]` (avg_median, latest_lost_packet_count, latest_sent_packet_count) provides continuous availability surveillance and latency baselining |
| **domains/network.md** | ✅ | Network device availability + WAN monitoring: agent health, device availability, RTD/packet-loss stats, and WAN IP all map directly to the network domain file |
| **domains/governance.md** | ✅ | Network monitoring documentation: Domotz deployment status, licence validity, and device inventory serve as evidence of active network monitoring for governance and audit purposes |
| **QBR** | ✅ | QBR chains this recipe for the network availability section. Device count delta and persistent packet-loss findings surface as action items. Licence expiration surfaces as a renewal item in the roadmap section |

---

## Data gaps & coverage notes

| Field | Status | Notes |
|---|---|---|
| `open_ports` per device | schema-only / data-absent in test | Present in Domotz schema; not populated in test dev environment. Data presence depends on SNMP polling configuration. Do not include in report unless confirmed populated for the specific system under analysis. |
| `AgentEyesSNMP[]` (SNMP custom monitors) | schema-confirmed / empty in test | Domotz Eyes SNMP monitors are in the schema but returned empty arrays in test data. If the customer has SNMP Eyes configured, this array will be populated. Include a note in reports that custom SNMP monitoring data is available if configured. |
| `AgentEyesTCP[]` (TCP custom monitors) | schema-confirmed / empty in test | Same as AgentEyesSNMP above. TCP Eyes (e.g., port availability checks on specific services) depend on customer configuration. |
| Historical RTD trend | not available via current path | `AgentRTDStats[]` reflects the snapshot at inspection time. Historical trending requires comparing across multiple timeline snapshots; not available in a single `GENERATE_AND_EVALUATE` call. |
| Per-device service/application detail | not in validated paths | Domotz can detect running services on some device types; this detail was not present in the validated test data. Treat as schema-dependent. |

---

## Output format

Default `markdown` (internal working document). Use `word` for
customer-facing site health letters. Use `pptx` for QBR network
availability slides (device count, OFFLINE summary, packet-loss
findings). Use `xlsx` for full device-inventory exports with
availability columns sortable by type, vendor, and polling status.

---

## Verification log

All paths below were confirmed against System A (dev environment).

```
| Step | Tool                               | Args                                                                                 | Result shape                          | Status    |
|------|------------------------------------|--------------------------------------------------------------------------------------|---------------------------------------|-----------|
| 1    | liongard_environment LIST          | query=<customer>                                                                     | array<environment>                    | ok        |
| 1    | liongard_launchpoint LIST          | envId=<ENV_ID> inspectorId=88                                                        | array<launchpoint>                    | ok        |
| 2    | liongard_timeline LIST             | envId=<ENV_ID>                                                                       | array<timeline-entry>                 | ok        |
| 3    | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath="Agent.{display_name: display_name, status_value: status.value, wan_ip: wan_info.ip, wan_hostname: wan_info.hostname, version_agent: version.agent, version_package: version.package, licence_type: licence.type, licence_expiration_time: licence.expiration_time, timezone: timezone}" | object | VALIDATED |
| 4    | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath="length(Devices)"                           | integer                               | VALIDATED |
| 4    | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath="Devices[].{display_name: display_name, type_label: type.label, status_value: status.value, ip_addresses: ip_addresses, hw_address: hw_address, vendor: vendor, model: model}" | array | VALIDATED |
| 5    | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath="AgentRTDStats[].{device_name: device_name, avg_median: avg_median, latest_lost_packet_count: latest_lost_packet_count, latest_sent_packet_count: latest_sent_packet_count}" | array | VALIDATED |
| 6    | (derived)                          | Agent.licence.expiration_time vs. today + slas.licence_expiration_warn_days          | date-diff integer (days)              | ok        |
| 7    | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath="API.{daily_limit: daily_limit, daily_usage: daily_usage}" | object                  | VALIDATED |
| 7    | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath="AgentConnectionConsumption.{limit: limit, current: current}" | object             | VALIDATED |
| 8    | QA pass                            | per reference/qa-retry-pattern.md                                                    | varies                                | ok        |
| 9    | render                             | per output.format                                                                    | <artifact path>                       | ok        |
```

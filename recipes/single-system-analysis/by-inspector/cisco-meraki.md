---
name: single-system-cisco-meraki
description: >
  Use this skill when the user wants a single-network analysis of a Cisco
  Meraki organization — Periodic Business Review (PBR), firewall config
  review, switch / AP / SSID inventory, license expiration, firmware audit,
  VPN policy review. Trigger phrases: "Meraki PBR", "pull Meraki data
  for the customer", "Meraki firewall review", "Meraki network audit",
  "Meraki license expiration", "what APs are deployed", "Meraki SSID
  audit". Produces an artifact in the format set in the customization
  block.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, soc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, pptx, xlsx]
primitives:
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
---

# Single-System Analysis — Cisco Meraki

> **Inspector:** `cisco-meraki-inspector` (ID 3). Network category. Network
> Controller — covers a Meraki *organization* with all its network devices
> (firewall MX, switches MS, access points MR) reported through one
> dataprint per network.
>
> **References:** `reference/inspector-aliases.md` (Meraki, MX, MS, MR).
> `reference/asset-fields.md` for asset-inventory cross-checks.
> `reference/qa-retry-pattern.md` for QA pass details.


---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-meraki-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  inventory: "Network Device Inventory"
  firewall: "Firewall (MX) Configuration"
  switches: "Managed Switches (MS)"
  aps: "Access Points (MR)"
  ssids: "Wireless SSID Audit"
  vpn: "Site-to-Site VPN"
  licensing: "Licensing & Renewal"
  privileged_users: "Dashboard Admin Audit"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 1     # Meraki is cloud-managed, daily inspection expected
  license_expiration_warn_days: 60   # annual licenses; 60-day lead time
  firmware_age_months_max: 6         # Meraki firmware drops monthly
  unsecured_ssid_max: 0              # any SSID without WPA2/WPA3 = flag

reporting_period: { default: "current_state" }

qa:
  retry_on_null: true
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 1     # tighter than default — Meraki is cloud-API-driven
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: false
  manual_verification_section_required: true
```

---

## When to use

- "Pull Meraki data for the customer"
- "Meraki PBR / quarterly review"
- "Any Meraki licenses expiring soon?"
- "What APs are deployed at the site?"
- "Meraki SSID security audit"
- "Confirm site-to-site VPN topology"

Personas: NOC (operational state), SOC (firewall rules + SSID security),
vCIO/AM (executive summary, license renewal roadmap), TAM (deep dive,
multi-product audit).

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Meraki system ID | Yes | `liongard_system LIST query="meraki"` — confirm via `SystemInfo.OrganizationName` |
| Reporting period | No | Default per customization |

---

## Locating the right system

```
liongard_system LIST searchMode=keyword query="meraki" environmentId=<ENV_ID>
```

`SystemInfo.OrganizationName` returns the Meraki organization name — match against
the customer's organization. `SystemInfo.FriendlyKey` returns the subdomain slug.
There is no `SystemInfo.Name` field (returns null).

> **Field gotcha (VALIDATED 2026-05-28):** `SystemInfo` = `{SystemName: "Cisco Meraki",
> FriendlyKey: "<org-slug>", OrganizationID: "<id>", OrganizationName: "<org-name>"}`.
> Use `SystemInfo.OrganizationName` for the human-readable org name in report headers.


---

## Liongard data sources

> **Asset Inventory First, Metric Cross-Check.** The Meraki per-system
> dataprint is the source of truth for *Meraki-managed configuration* —
> firewall rules, switch ports, AP firmware, SSID security, license state,
> VPN policies. The cross-inspector device inventory is the source of
> truth for *coverage* — which Meraki devices are also visible to other
> inspectors (RMM, network discovery), and which Liongard-known devices
> live on Meraki-managed networks but aren't reflected in the Meraki
> dataprint.

### Per-vendor data — Meraki dataprint top-level keys

| Key | Description |
|---|---|
| `SystemInfo` | Network identifier — name, organization, time zone |
| `Networks[*].Devices[]` | Array of every network device (firewall MX, switches MS, APs MR) — devices are nested per-network, not at top level. Flatten with `Networks[*].Devices[]`. `NetworkDevices` is NOT a valid top-level key (returns null). VALIDATED: System B (2026-05-22, inspectorID=3) — 1 MX68 device returned via `Networks[*].Devices[]`. |
| `Networks[*].VLANs[]` | VLAN configuration array (flattened across all networks) — each with id, name, subnet + DHCP detail. Top-level `VLANs` is a comma-separated name string, NOT an array. VALIDATED 2026-05-28. |
| `Networks[*].SSIDs[]` | Wireless SSID array (flattened) — auth mode, encryption, per-SSID firewall rules. Top-level `Ssids` is null. VALIDATED 2026-05-28. |
| `Networks[*].FirewallRules[]` | WAN-to-LAN access rules (flattened across all networks). Top-level `L3FirewallRules` is null. VALIDATED 2026-05-28. |
| `Networks[*].VPNs` | Site-to-site VPN policy object per network — `mode` ("none"/"hub"/"spoke"), not an array of subnets. Top-level `VpnSubnets` is null. VALIDATED 2026-05-28. |
| `LicenseStatus` | Per-product license state + co-termination expiration |
| `Users` | Dashboard user accounts with privilege flag |

#### Field gotchas (inline notes — not TODO)

- **`Networks[*].Devices[]` — devices are nested under each network, not at top level.** `NetworkDevices` is NOT a valid key and returns null. Use `Networks[*].Devices[]` to get the flattened device list. Each device has `name`, `model`, `serial`, `firmware`, `mac`, `wan1Ip` (MX WAN IP), `tags`, `networkId`, `Clients` (connected client array), and `ManagementInterface`. Note: `ipAddress` is not a valid field — use `wan1Ip` for MX appliances. Device type is not a field; derive it from the `model` prefix: `MX` = security appliance (firewall), `MS` = switch, `MR` = wireless AP, `MV` = camera, `MG` = cellular gateway. Filter by prefix: `Networks[*].Devices[?starts_with(model, 'MS')]` for switches, etc.
- **`LicenseStatus` uses a co-termination model** — Meraki applies one
  expiration date to every license at the org level. Per-device license
  counts are inside the object, but they all share one
  `expirationInDays`. That's why a single warning + renewal calendar
  covers the entire customer's Meraki estate.

### Cross-inspector cross-check — device inventory

```
liongard_device LIST environmentId=<ENV_ID>
                     fields=["hostname","manufacturer","model","inspectors"]
```

```
# Devices Meraki sees
meraki_devices = devices where inspectors contains "cisco-meraki-inspector"

# Meraki-known network devices that should also be in RMM but aren't
# (e.g., switches with no monitoring agent option — common, but worth flagging)
managed_gap = meraki_devices where inspectors only contains "cisco-meraki-inspector"

# Devices Liongard knows from other inspectors but Meraki doesn't see —
# either misconfigured org scope or a rogue device on a Meraki-managed VLAN
discovered_outside_meraki = devices where category == "network"
                                       AND inspectors does not contain "cisco-meraki-inspector"
```

---

## Metrics and queries

### Network identity

| Metric | JMESPath | Result shape |
|---|---|---|
| Network identifier | `SystemInfo` | `<object>` |

### Network device inventory

| Metric | JMESPath | Result shape |
|---|---|---|
| All network devices (make/model/WAN IP/firmware) | `Networks[*].Devices[*].{name: name, model: model, serial: serial, wan1Ip: wan1Ip, firmware: firmware, mac: mac}` | `<array>` |
| Firmware audit | `Networks[*].Devices[*].{name: name, model: model, firmware: firmware}` | `<array>` |
| Switch list | `Networks[*].Devices[?starts_with(model, 'MS')]` | `<array>` |
| Device count | `length(Networks[*].Devices[])` | `<integer>` |

### Firewall (MX) configuration

| Metric | JMESPath | Result shape |
|---|---|---|
| WAN-to-LAN access rules (all networks) | `Networks[*].FirewallRules[]` | `<array>` |
| Site-to-site VPN mode per network | `Networks[*].VPNs` | `<array<object>>` — each has `mode` and `NetworkName` |
| VLAN inventory (all networks) | `Networks[*].VLANs[]` | `<array>` |
| VLAN detail (id, name, subnet, DHCP) | `Networks[*].VLANs[].{id: id, name: name, subnet: subnet, applianceIp: applianceIp, dhcpHandling: dhcpHandling}` | `<array>` |

> **Field gotcha (VALIDATED 2026-05-28):** Top-level `L3FirewallRules`, `VpnSubnets`, and `Ssids` are
> null. All of these are nested under `Networks[*]`. Use `Networks[*].FirewallRules[]`,
> `Networks[*].SSIDs[]`, and `Networks[*].VPNs` respectively. Top-level `VLANs` is a
> comma-separated **string** of VLAN names (e.g. "DATA, VOICE, GUEST") — NOT an array.
> Use `Networks[*].VLANs[]` for structured VLAN objects.

### Wireless SSID audit

| Metric | JMESPath | Result shape |
|---|---|---|
| All SSIDs (auth/encryption posture) | `Networks[*].SSIDs[].{name: name, enabled: enabled, authMode: authMode, encryptionMode: encryptionMode}` | `<array>` |
| SSIDs without pre-shared key (open networks) | `Networks[*].SSIDs[?authMode == 'open' \|\| encryptionMode == null].name` | `<array<string>>` (compliant when empty) |
| Count of active SSIDs | `length(Networks[*].SSIDs[?enabled == \`true\`])` | `<integer>` |

### Licensing

| Metric | JMESPath | Result shape |
|---|---|---|
| Full license status object | `LicenseStatus` | `<object>` |
| Days until expiration (countdown) | `LicenseStatus.expirationInDays` | `<integer>` |

### Dashboard admin audit

| Metric | JMESPath | Result shape |
|---|---|---|
| Privileged user list | `Users[?Privileged == 'Yes'].{name: name, email: email}` | `<array>` |

### Proposed metrics (not yet in Liongard library)

The partner onboarding QA flagged the following as missing. Until they
ship, the recipe runs client-side filters against the existing
`Networks[*].Devices[]` and `Networks[*].VLANs[]` arrays:

| Field | Workaround |
|---|---|
| VLAN DHCP scope detail (range, lease, DNS, reservations) | Client-side parse of `Networks[*].VLANs[]` for `dhcpHandling`, `dhcpLeaseTime`, `dnsNameservers`, `fixedIpAssignments` |
| Per-switch management IP | Client-side filter `Networks[*].Devices[?starts_with(model, 'MS')].lanIp` |
| Per-AP management IP | Client-side filter `Networks[*].Devices[?starts_with(model, 'MR')].lanIp` |

### Time-series — license / firmware / device-count trend

```
# License countdown over time
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="LicenseStatus.expirationInDays"

# Network device count over time (capacity / growth)
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="length(Networks[*].Devices[])"
```

---

## QA & Manual Verification

Run the QA pass per `reference/qa-retry-pattern.md` before rendering output:

1. **Retry persistent nulls.** If `liongard_metric EVALUATE` returns null
   for any of the metrics above, retry up to `qa.retry_attempts` times.
   Persistent nulls go to the manual-verification list.

2. **Flag stale inspector data.** Meraki is cloud-API-driven, so a stale
   inspector usually indicates an API-key or scope problem. The recipe's
   `qa.flag_inspector_lastseen_threshold_days` defaults to **1 day** —
   tighter than the library default. Any system with `lastSeen` older
   than 1 day gets flagged.

3. **Cross-tool divergence.** If running this recipe alongside an RMM
   recipe (NinjaOne, ConnectWise Automate, etc.), compare the
   network-device list — devices in RMM but not in Meraki indicate a
   misconfigured Meraki organization scope or an unmanaged segment.

4. **Proposed-metric gaps for this recipe** — list these in the
   manual-verification appendix:
   - VLAN DHCP scope detail (`(not in dataprint) Cisco Meraki: VLAN DHCP Summary`)
   - Per-switch management IP (`(not in dataprint) Cisco Meraki: Switch IP Addresses`)
   - Per-AP management IP (`(not in dataprint) Cisco Meraki: AP IP Addresses`)

5. **Manual Verification appendix** — render in the deliverable. Typical
   items for this recipe:
   - Persistent-null on `LicenseStatus` (verify in Meraki dashboard).
   - SSIDs flagged as open / unencrypted that the customer says are
     intentional (e.g., a guest network — confirm captive portal).
   - Firmware versions older than `slas.firmware_age_months_max` (Meraki
     dashboard shows release date).

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| License expiring soon | `LicenseStatus.expirationInDays < slas.license_expiration_warn_days` | "Meraki licenses expire in <N> days — initiate renewal with the vendor (co-term applies to every device in the org)." |
| License already expired | `LicenseStatus.expirationInDays <= 0` | "**Critical:** Meraki licenses expired — devices may stop receiving cloud-management updates." |
| Open / unencrypted SSID | `length(Networks[*].SSIDs[?authMode == 'open' \|\| encryptionMode == null]) > slas.unsecured_ssid_max` | "<N> SSIDs broadcast open / unencrypted — confirm intentional (e.g., guest captive portal) or apply WPA2/WPA3." |
| Firmware behind | per-device firmware older than `slas.firmware_age_months_max` | "<N> Meraki devices on firmware older than <months> months — schedule maintenance windows for upgrade." |
| Dashboard admin sprawl | unexpected entries in `Users[?Privileged == 'Yes']` | "Review Meraki dashboard admin accounts — <N> entries warrant audit." |
| Stale inspector | `lastSeen` > 1 day | "Meraki inspector hasn't reported in <N> days — confirm API key + organization scope." |


---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Traffic / bandwidth analytics | ❌ not in dataprint | Meraki dashboard / API |
| Threat / IDS detection counts | ❌ not in dataprint | Meraki dashboard / API |
| Client device list (per-AP / per-SSID) | ❌ not in dataprint | Meraki dashboard / API |
| RF / wireless health metrics | ❌ not in dataprint | Meraki dashboard / API |
| VLAN DHCP scope detail | ⚠️ not in dataprint | Manual export from Meraki dashboard |
| Per-switch / per-AP management IP | ⚠️ not in dataprint | Client-side filter on `Networks[*].Devices[]` |
| Switch port-level configuration | ⚠️ partial | Available via per-switch query, but not in standard dataprint |


---

## Output format

Markdown / Word / PowerPoint / Excel per `output.format`. **xlsx** is the
canonical fit for the multi-product device inventory (sortable across
firewall + switches + APs in one table). **pptx** for the executive
overview with a license-renewal countdown slide and an SSID-security
donut.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_system LIST | query="meraki" envId=<ENV_ID> | array<system> | ok |
| 3 | liongard_metric EVALUATE | jmesPathQuery="SystemInfo.Name" sysId=<SYS_ID> | null — WRONG FIELD | BUG 2026-05-28: No SystemInfo.Name field; use SystemInfo.OrganizationName |
| 3a | liongard_metric EVALUATE | jmesPathQuery="SystemInfo.OrganizationName" sysId=<SYS_ID> | "<org-name>" (string) | VALIDATED 2026-05-28 |
| 3b | liongard_metric EVALUATE | jmesPathQuery="L3FirewallRules[*]" sysId=<SYS_ID> | null — WRONG PATH | BUG 2026-05-28: Top-level L3FirewallRules is null; data nested under Networks[*].FirewallRules[] |
| 3c | liongard_metric EVALUATE | jmesPathQuery="Networks[0].FirewallRules[0]" sysId=<SYS_ID> | {Rule_r, policy, comment, srcCidr, destCidr, protocol, NetworkName, syslogEnabled} | VALIDATED 2026-05-28 |
| 3d | liongard_metric EVALUATE | jmesPathQuery="VpnSubnets[*]" sysId=<SYS_ID> | null — WRONG PATH | BUG 2026-05-28: Top-level VpnSubnets is null; use Networks[*].VPNs (object per network with mode + NetworkName) |
| 3e | liongard_metric EVALUATE | jmesPathQuery="Networks[0].VPNs" sysId=<SYS_ID> | {mode: "none", NetworkName: "<name>"} | VALIDATED 2026-05-28 |
| 3f | liongard_metric EVALUATE | jmesPathQuery="Vlans[*]" sysId=<SYS_ID> | null (or comma-string at top-level VLANs) — WRONG PATH | BUG 2026-05-28: Use Networks[*].VLANs[] for structured array |
| 3g | liongard_metric EVALUATE | jmesPathQuery="Networks[0].VLANs[0]" sysId=<SYS_ID> | {id, name, subnet, applianceIp, dhcpHandling, dhcpLeaseTime, dnsNameservers, ...} | VALIDATED 2026-05-28 |
| 3h | liongard_metric EVALUATE | jmesPathQuery="Ssids[*]" sysId=<SYS_ID> | null — WRONG PATH | BUG 2026-05-28: Use Networks[*].SSIDs[] for structured SSID array |
| 3i | liongard_metric EVALUATE | jmesPathQuery="Networks[0].SSIDs[0]" sysId=<SYS_ID> | {name, enabled, authMode, encryptionMode, FirewallRules[*], ...} | VALIDATED 2026-05-28 |
| 4 | liongard_device LIST | envId=<ENV_ID> fields=[hostname,manufacturer,model,inspectors] | array<device> | ok |
| 5 | (QA pass) retry persistent nulls | per `reference/qa-retry-pattern.md` | varies | ok |
```

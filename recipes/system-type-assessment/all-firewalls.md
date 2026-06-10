---
name: system-type-all-firewalls
description: >
  Use this skill when the user wants a unified firewall posture across
  every firewall vendor deployed in an environment — fleet view of
  firmware status, license expirations, default-credential audits,
  WAN-management exposure, site-to-site VPN topology, and per-vendor
  policy inventory. Trigger phrases: "firewall fleet review", "all-
  firewalls report", "unified firewall posture for the customer",
  "compare firewall coverage across vendors", "firewall license
  expiration roadmap", "WAN management exposure audit". Iterates each
  deployed firewall (SonicWall, FortiGate, Cisco ASA, Sophos XG, Cisco
  Meraki MX, WatchGuard, Palo Alto, Barracuda, pfSense, Sophos SG) and
  rolls up to one fleet-level report.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [vcio-account-manager, soc, technical-alignment-manager, noc]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  - metrics:barracuda-firewall:application-control-enabled
  - metrics:barracuda-firewall:atp-enabled
  - metrics:barracuda-firewall:energize-updates-days-until-expiration
  - metrics:barracuda-firewall:firmware-version
  - metrics:barracuda-firewall:ips-enabled
  - metrics:barracuda-firewall:local-users-total-count
  - metrics:barracuda-firewall:rules-open-any-to-any-count
  - metrics:barracuda-firewall:system-model
  - metrics:barracuda-firewall:wan-management-allowed
  - metrics:cisco-asa:configs-match
  - metrics:cisco-asa:last-config-modified
  - metrics:cisco-asa:licenses-expiring-30d-count
  - metrics:cisco-asa:licenses-expiring-5d-count
  - metrics:cisco-asa:licenses-expiring-5d-list
  - metrics:cisco-asa:model
  - metrics:cisco-asa:running-config
  - metrics:cisco-asa:serial-number
  - metrics:cisco-asa:software-version
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
  - metrics:palo-alto-panos:certificate-expiration
  - metrics:palo-alto-panos:check-device-resources
  - metrics:palo-alto-panos:config-changes-pending
  - metrics:palo-alto-panos:device-admins
  - metrics:palo-alto-panos:dhcp-expiration
  - metrics:palo-alto-panos:dhcp-lease-monitoring
  - metrics:palo-alto-panos:expired-device-certificates
  - metrics:palo-alto-panos:interface-packets-received
  - metrics:palo-alto-panos:interface-packets-transmitted
  - metrics:palo-alto-panos:policy-based-forwarding-ips
  - metrics:palo-alto-panos:software-version
  - metrics:pfsense:alias-summary
  - metrics:pfsense:ca-certificate-summary
  - metrics:pfsense:certificate-revocation-list-summary
  - metrics:pfsense:cron-job-summary
  - metrics:pfsense:firewall-rule-summary
  - metrics:pfsense:groups-summary
  - metrics:pfsense:interface-summary
  - metrics:pfsense:nat-1to1-rule-summary
  - metrics:pfsense:outbound-nat-list
  - metrics:pfsense:port-forwarding-rule-summary
  - metrics:pfsense:software-version
  - metrics:pfsense:switchport-summary
  - metrics:pfsense:time-servers
  - metrics:pfsense:user-list-with-scope
  - metrics:pfsense:user-server-certificate-summary
  - metrics:pfsense:users-added-summary
  - metrics:pfsense:virtual-ip-summary
  - metrics:pfsense:vlan-summary
  - metrics:sonicwall:admin-session-idle-timeout
  - metrics:sonicwall:admin-username
  - metrics:sonicwall:agss-license-expiry
  - metrics:sonicwall:any-to-any-allow-rules-count
  - metrics:sonicwall:audit-logging-enabled
  - metrics:sonicwall:capture-atp-enabled
  - metrics:sonicwall:firmware-version
  - metrics:sonicwall:geo-ip-block-all-enabled
  - metrics:sonicwall:hostname
  - metrics:sonicwall:http-management-enabled
  - metrics:sonicwall:licenses-expiring-30d-count
  - metrics:sonicwall:licenses-expiring-30d-list
  - metrics:sonicwall:local-users-count
  - metrics:sonicwall:min-password-length
  - metrics:sonicwall:model
  - metrics:sonicwall:otp-config-count
  - metrics:sonicwall:restart-required
  - metrics:sonicwall:serial-number
  - metrics:sonicwall:stealth-mode-enabled
  - metrics:sonicwall:syslog-configured
  - metrics:sonicwall:user-lockout-enabled
  - metrics:sonicwall:wan-allow-rules-for-management-count
  - metrics:sonicwall:wan-to-lan-explicit-allow-any-list
  - metrics:sonicwall:zones-without-gav-count
  - metrics:sonicwall:zones-without-ips-count
  - metrics:sonicwall:zones-without-ips-list
  - metrics:sophos-firewall:active-user-list
  - metrics:sophos-firewall:device-dns-summary
  - metrics:sophos-firewall:interfaces-count
  - metrics:sophos-firewall:security-policy-summary
  - metrics:sophos-firewall:user-group-summary
  - metrics:sophos-firewall:user-summary
  - metrics:sophos-firewall:zone-summary
  - metrics:sophos-sg:count-of-active-users
  - metrics:sophos-sg:count-of-groups
  - metrics:sophos-sg:interface-summary
  - metrics:sophos-sg:licenses-expiring-30-days-count
  - metrics:sophos-sg:licenses-expiring-30-days-list
  - metrics:sophos-sg:list-of-active-users
  - metrics:sophos-sg:list-of-groups
  - metrics:sophos-sg:list-of-network-definitions
  - metrics:sophos-sg:nat-rules
  - metrics:sophos-sg:packet-filter-rules-summary
  - metrics:sophos-sg:remote-access-profiles-summary
  - metrics:sophos-sg:remote-gateways-summary
  - metrics:sophos-sg:site-to-site-vpn-summary
  - metrics:sophos-sg:ssh-enabled
  - metrics:sophos-sg:utm-version
  - metrics:watchguard:access-rule-summary
  - metrics:watchguard:account-lockout-disabled-count
  - metrics:watchguard:account-lockout-enabled-list
  - metrics:watchguard:alias-summary
  - metrics:watchguard:down-interfaces-count
  - metrics:watchguard:down-interfaces-list
  - metrics:watchguard:dynamic-nat-summary
  - metrics:watchguard:features-expiring-30d-count
  - metrics:watchguard:features-expiring-30d-list
  - metrics:watchguard:firmware-version
  - metrics:watchguard:group-summary
  - metrics:watchguard:hostname
  - metrics:watchguard:interface-summary
  - metrics:watchguard:licensed-interface-count
  - metrics:watchguard:management-ip
  - metrics:watchguard:mgmt-user-summary
  - metrics:watchguard:mgmt-users-locked-out-count
  - metrics:watchguard:mgmt-users-locked-out-list
  - metrics:watchguard:mobile-ipsec-policies
  - metrics:watchguard:mobile-ssl-vpn-summary
  - metrics:watchguard:model
  - metrics:watchguard:one-to-one-nat-summary
  - metrics:watchguard:physical-interface-count
  - metrics:watchguard:quota-action-summary
  - metrics:watchguard:quota-rule-summary
  - metrics:watchguard:serial-number
  - metrics:watchguard:site-to-site-phase1-summary
  - metrics:watchguard:site-to-site-phase2-summary
  - metrics:watchguard:user-summary
---

# System-Type Assessment — All Firewalls

> Cross-vendor firewall posture. Iterates every firewall inspector
> deployed in the environment and produces a unified fleet-level report.
> Each vendor exposes a different field shape — this recipe normalizes
> them into a common reporting schema (identity, firmware, licensing,
> management exposure, policy count, VPN topology, default-credential
> audit) and surfaces gaps per vendor.
>
> **Inspectors covered:**
> - `sonicwall-inspector` (ID 7) — SonicWall (SonicOS 6 + Gen7)
> - `fortinet-fortigate-inspector` (ID 33) — Fortinet FortiGate
> - `cisco-asa-inspector` (ID 22) — Cisco ASA
> - `sophos-firewall-inspector` (ID 28) — Sophos XG / XGS
> - `sophos-sg-inspector` (ID 43) — Sophos SG (legacy)
> - `cisco-meraki-inspector` (ID 3) — Cisco Meraki MX (firewall portion)
> - `watchguard-inspector` (ID 29) — WatchGuard
> - `palo-alto-panos-inspector` (ID 49) — Palo Alto PAN-OS (Beta)
> - `barracuda-firewall-inspector` (ID 52) — Barracuda
> - `pfsense-inspector` (ID 37) — pfSense
>
> **Pairs with:** `recipes/single-system-analysis/by-inspector/<vendor>.md`
> for per-vendor deep dive, `recipes/compliance/cyber-insurance/domains/network.md`
> for cyber-insurance evidence on the firewall stack.
>
> **References:** `reference/inspector-aliases.md` for vendor lookups.
> `reference/asset-fields.md` for the `liongard_device` field map.
> `reference/qa-retry-pattern.md` for the QA pass.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-firewall-fleet-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  fleet_kpis: "Fleet KPI Dashboard"
  identity_inventory: "Firewall Inventory by Vendor"
  firmware_status: "Firmware Currency by Vendor"
  license_roadmap: "License Expiration Roadmap"
  management_exposure: "WAN Management Exposure"
  default_credential_audit: "Default Credential / Admin User Audit"
  policy_complexity: "Firewall Policy Complexity"
  vpn_topology: "Site-to-Site VPN Topology"
  per_vendor_gaps: "Per-Vendor Coverage Gaps"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 1
  license_expiration_warn_days: 60
  firmware_age_months_max: 12
  wan_management_exposure_allowed: false
  policy_count_warn_threshold: 200       # firewalls with >200 rules warrant cleanup discussion

inspectors_in_scope:
  # Set to which firewalls you actually deploy. Empty = use all that exist
  # in the environment.
  - sonicwall-inspector
  - fortinet-fortigate-inspector
  - cisco-asa-inspector
  - sophos-firewall-inspector         # Sophos XG / XGS
  - cisco-meraki-inspector            # MX = firewall portion of Meraki
  - watchguard-inspector
  - palo-alto-panos-inspector         # Beta — verify metric availability
  - barracuda-firewall-inspector
  - pfsense-inspector
  - sophos-sg-inspector               # Legacy UTM — flag for XGS migration

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

- Quarterly firewall fleet review at the customer level
- Pre-renewal license-expiration roadmap (vCIO / Accounting conversation)
- Multi-site MSP audit — "firmware status across all customer firewalls"
- "Are any firewalls exposing management on the WAN?"
- Vendor consolidation analysis — "we have 4 firewall vendors; could we
  standardize?"
- Cyber-insurance evidence — pairs with `cyber-insurance/domains/network.md`

Personas: vCIO/AM (executive summary, vendor consolidation, license
renewal), SOC (WAN exposure + default-credential audit), TAM (deep dive),
NOC (firmware + operational state).

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Reporting period | No | Default per customization |

Environment-scoped — no per-system input. The recipe iterates the deployed
firewall inspectors internally.

---

## Liongard data sources

> **Asset Inventory First, Metric Cross-Check.** This recipe iterates
> per-vendor firewall systems for vendor-specific configuration (firmware,
> license state, policy detail, VPN tunnels), and uses `liongard_device`
> as the cross-inspector source of truth for **what's actually in the
> environment** — including firewalls Liongard has discovered but doesn't
> have a per-vendor inspector for.

| Source | Used for |
|---|---|
| `liongard_system LIST environmentId=<ENV_ID>` | Discover deployed firewall systems by inspector slug |
| `liongard_device LIST environmentId=<ENV_ID> category="network"` | Cross-inspector device inventory of every network device — confirms inspected firewalls + surfaces uninspected ones |
| `liongard_metric EVALUATE` (per firewall) | Per-vendor headline metrics — see each per-vendor recipe for the metric names/JMESPath queries |
| Per-vendor recipes under `recipes/single-system-analysis/by-inspector/` | The single source of truth for per-vendor field shapes; this rollup normalizes them |

The asset-inventory device list is critical for the **coverage gap** analysis
in Step 4 — a network device that appears in the inventory but has no
firewall-inspector system attached is a deployment gap (Liongard sees the
firewall through some other inspector but isn't actively pulling its config).

---

## Workflow

### Step 1 — Discover deployed firewall systems

```
liongard_system LIST environmentId=<ENV_ID>
```

Filter for systems whose inspector slug is in the firewall list (per the
customization block's `inspectors_in_scope`). Group by inspector slug to
produce a per-vendor system list.

### Step 2 — Pull asset inventory for cross-vendor context

```
liongard_device LIST environmentId=<ENV_ID> category="network"
                     fields=["hostname","manufacturer","model","inspectors","internalIP","externalIP","firmware"]
```

This gives the cross-inspector device-inventory view of every network
device — useful for confirming the firewall list against what's actually
in the environment. A firewall in the device inventory but missing from
the per-inspector system list = a coverage gap (the firewall is known but
not actively inspected).

### Step 3 — For each firewall, normalize into the common schema

For every firewall system, run the per-vendor recipe's headline metrics
and map the results to this normalized shape:

| Field | Per-vendor source |
|---|---|
| `vendor` | inspector slug → Display name |
| `hostname` | per-vendor `SystemInfo.Hostname` (or not in current dataprint for ASA) |
| `model` | per-vendor `SystemInfo.Model` |
| `firmware_version` | per-vendor firmware metric |
| `firmware_release_date` | parse from firmware version (Meraki / Fortinet / SonicWall maintain release-date tables externally — note as a manual-verification item if not available) |
| `license_status` | per-vendor license metric (Meraki LicenseStatus, ASA Licenses, FortiGate Licenses, etc.) |
| `wan_management_exposed` | per-vendor management-interface metric |
| `policy_count` | `length()` of per-vendor rule array |
| `local_admin_count` | `length()` of per-vendor user array |
| `vpn_count` | `length()` of per-vendor VPN array |
| `last_seen` | system / asset `lastSeen` |
| `inspector_slug` | for proposed-metric tracking |

### Step 4 — Roll up to fleet KPIs

| Fleet KPI | Computation |
|---|---|
| Total firewalls in fleet | `length(firewall_systems)` |
| Vendors deployed | distinct `vendor` count |
| Firmware-current count | firewalls where `firmware_release_date > today − slas.firmware_age_months_max months` |
| Licenses expiring < SLA | firewalls where any license `daysToExpiry < slas.license_expiration_warn_days` |
| Already-expired licenses | firewalls where any license `daysToExpiry <= 0` |
| WAN management exposed | firewalls where `wan_management_exposed == true` |
| Default credential / admin audit candidates | firewalls where `local_admin_count > expected_baseline` |
| Stale inspectors | firewalls where `last_seen > slas.inspector_lastseen_days_max` |

### Step 5 — Per-vendor coverage gap surfacing

Each firewall vendor has different per-metric availability (see per-vendor
recipes for detail). Produce a per-vendor gap matrix:

| Vendor | Firmware | License | WAN exposure | Policy count | VPN count | Default-cred audit |
|---|---|---|---|---|---|---|
| SonicWall | ✅ | ⚠️ partial (aggregate only) | ✅ | ✅ | ✅ | ✅ |
| FortiGate | ✅ | ⚠️ not in dataprint | 🔍 client-side parse | ✅ | ⚠️ not in dataprint | ✅ |
| Cisco ASA | ✅ | ✅ (expiring-soon list) | 🔍 parse from running config | 🔍 parse from running config | 🔍 parse from running config | 🔍 parse from running config |
| Sophos XG / XGS | ⚠️ not in dataprint | ⚠️ not in dataprint | ⚠️ not in dataprint | ✅ | ⚠️ not in dataprint | ⚠️ not in dataprint |
| Cisco Meraki (MX) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| WatchGuard | ⚠️ not in dataprint | ⚠️ TSS-expiration proposed | ⚠️ not in dataprint | ⚠️ not in dataprint | ⚠️ not in dataprint | ⚠️ not in dataprint |
| Palo Alto PAN-OS (Beta) | ⚠️ not in dataprint | ⚠️ per-subscription proposed | ⚠️ not in dataprint | ✅ | ⚠️ not in dataprint | ⚠️ not in dataprint |
| Barracuda Firewall | ⚠️ not in dataprint | ⚠️ Energize Updates proposed | ⚠️ not in dataprint | ⚠️ not in dataprint | ⚠️ not in dataprint | ⚠️ not in dataprint |
| pfSense | ⚠️ not in dataprint | n/a (open source) | ⚠️ not in dataprint | ⚠️ not in dataprint | ⚠️ not in dataprint | ⚠️ not in dataprint |
| Sophos SG (legacy) | ⚠️ not in dataprint | ⚠️ not in dataprint | ⚠️ not in dataprint | ⚠️ not in dataprint | ⚠️ not in dataprint | ⚠️ not in dataprint |

> See per-vendor recipes for detail:
> `recipes/single-system-analysis/by-inspector/{sonicwall, fortinet-fortigate, cisco-asa, sophos-firewall, cisco-meraki, watchguard, palo-alto-panos, barracuda-firewall, pfsense, sophos-sg}.md`

For ⚠️ and 🔍 cells, the recipe falls back to client-side parsing or
manual UI confirmation — surface in the **Manual Verification Needed**
appendix.

### Step 6 — Cross-vendor consolidation analysis

```
# Vendor consolidation candidate
single_firewall_vendors = vendors deployed where count == 1
# When the customer runs ≥3 distinct firewall vendors, surface
# "vendor consolidation candidate" as a vCIO conversation prompt.
```

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| End-of-engineering-support firmware | any FortiGate on major 6.x; any ASA past current-train | "**Critical:** <N> firewalls on EOL firmware — plan upgrade or refresh." |
| Firmware behind | firmware release > `slas.firmware_age_months_max` months ago | "<N> firewalls on firmware older than <months> months — schedule maintenance." |
| Licenses expiring soon | any license `daysToExpiry < slas.license_expiration_warn_days` | "<N> firewalls have licenses expiring within <SLA> days — initiate renewals; calendar quarterly cost spike." |
| Already-expired licenses | any license `daysToExpiry <= 0` | "**Critical:** <N> firewalls have lapsed licenses — security services may have stopped updating." |
| WAN management exposed | any firewall where management is reachable from WAN | "**Critical:** <N> firewalls expose management on the WAN — restrict to admin VLAN or VPN today." |
| Vendor sprawl | `length(distinct vendors) >= 3` | "Customer runs <N> firewall vendors — consider consolidation for ops + cost; schedule vCIO conversation." |
| Excess policy count | any firewall with `policy_count > slas.policy_count_warn_threshold` | "<hostname> has <N> firewall policies — schedule cleanup; large rule bases hide shadowed and unused rules." |
| Default-credential audit candidate | any firewall with `local_admin_count > expected_baseline` | "<hostname> has <N> local admin accounts — review and remove unused." |
| Coverage gap (firewall in inventory, not inspected) | network device with firewall classification but no firewall-inspector in `inspectors[]` | "<hostname> appears in the network inventory but has no firewall inspector running — connect Liongard to extend coverage." |
| Stale inspector | any firewall with `last_seen > 1 day` | "<N> firewall inspectors stale — confirm API / SSH access." |

---

## License expiration roadmap

The fleet-level license roadmap is one of this recipe's headline outputs.
Build a per-quarter renewal calendar grouped by vendor:

```
For each firewall system:
  for each license / service:
    quarter = quarter(license.expirationDate)
    accumulate by (quarter, vendor)

Output: a calendar grid showing which quarter has license renewals due,
per vendor — useful for vCIO conversations and Accounting/Finance budget
planning.
```

Surface the cost-spike quarters in the executive summary so the customer
can budget proactively.

---

## QA & Manual Verification

Run the QA pass per `reference/qa-retry-pattern.md` before rendering output:

1. **Retry persistent nulls.** Many firewall metrics are vendor-specific
   and may return null when the customer runs a different vendor. Retry
   only when the metric is expected to apply.

2. **Flag stale inspectors.** Tighter `qa.flag_inspector_lastseen_threshold_days: 1`
   for firewalls — they're API-driven and should report daily.

3. **Cross-tool divergence.** When this recipe sees a firewall in the
   network device inventory (`liongard_device LIST category="network"`)
   but no matching firewall-inspector system — that's a coverage gap;
   surface in the manual-verification appendix.

4. **Proposed-metric gaps for this recipe** — surface the union of all
   per-vendor data gaps (see Step 5 matrix). The full list lives
   in `reference/future-recipes-roadmap.md` under the firewall vendors.

5. **Manual Verification appendix** — render in the deliverable. Typical
   items for this recipe:
   - Firewall-inspector lastSeen > 1 day on any firewall.
   - Per-vendor license expiration where the proposed-metric gap forces
     manual UI confirmation (Sophos XG, partially FortiGate / SonicWall).
   - WAN management exposure where the proposed-metric gap forces manual
     UI confirmation.
   - HA-pair drift for vendors that don't expose HA-state via Liongard.

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Traffic / threat analytics across vendors | ❌ not in dataprint for any vendor | Vendor analytics / SIEM |
| HA-pair config drift | ❌ not in dataprint | Manual UI compare per vendor |
| Per-rule hit counts (used vs unused rules) | ❌ not in dataprint | Vendor UI / log analytics |
| Firmware release-date lookup | ⚠️ external | Maintain a per-vendor release-date table; cross-reference against `firmware_version` |
| Per-vendor license renewal cost | ⚠️ external | MSP's PSA / vendor portal |

---

## Output format

Markdown / Word / PowerPoint / Excel per `output.format`. **xlsx** is the
canonical fleet-evidence pack (one row per firewall with normalized
columns). **pptx** for the executive overview with the
license-expiration-by-quarter chart and the per-vendor firmware-currency
gauge.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_system LIST | envId=<ENV_ID> | array<system> | ok |
| 3 | liongard_device LIST | envId=<ENV_ID> category=network fields=[...] | array<device> | ok |
| 4 | per firewall system: liongard_metric EVALUATE | jmesPath sysId=<SYS_ID> envId=<ENV_ID> | varies | ok per vendor |
| 5 | (QA pass) retry persistent nulls | per `reference/qa-retry-pattern.md` | varies | ok |
```

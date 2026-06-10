---
name: single-system-ubiquiti-unifi
description: >
  Use this skill when the user wants a single-controller analysis of
  a Ubiquiti UniFi deployment — PBR, controller version audit, AP /
  switch / gateway inventory, firmware audit, SSID + wireless
  security posture, guest-network audit, VLAN configuration, local
  user / admin audit. Trigger phrases: "UniFi review", "Ubiquiti PBR",
  "UniFi controller audit", "UDM review", "pull UniFi data for
  <customer>", "UniFi firmware audit", "SSID security audit".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, soc, technical-alignment-manager, vcio-account-manager]
output_formats: [markdown, word, pptx]
primitives:
  - metrics:ubiquiti-unifi:controller-version
  - metrics:ubiquiti-unifi:device-serial-number-list
  - metrics:ubiquiti-unifi:devices-list
  - metrics:ubiquiti-unifi:hardware-type-and-version
  - metrics:ubiquiti-unifi:subnets-list
  - metrics:ubiquiti-unifi:super-admin-users-list
---

# Single-System Analysis — Ubiquiti UniFi

> **Inspector:** `ubiquiti-unifi-inspector` (ID 40). Network
> category. **One system per UniFi controller / site.** Covers UniFi
> APs (UAP / U6 / U7), UniFi switches (USW), UniFi gateways (UDM /
> UDM-Pro / UXG / USG), and the UniFi Network controller itself
> (self-hosted or UniFi Hosting).
>
> **References:** `reference/inspector-aliases.md` (UniFi, Ubiquiti,
> UDM). Distinct from the per-firewall recipes — UniFi devices in
> the gateway role (UDM) are included here, not in `all-firewalls.md`.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-unifi-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  controller: "Controller Identity & Version"
  device_inventory: "Device Inventory (APs / Switches / Gateways)"
  ssids: "SSID & Wireless Security"
  guest_network: "Guest Network Audit"
  vlans: "VLAN / Network Configuration"
  local_users: "Local User & Admin Audit"
  management: "Management & Remote Access"
  lifecycle: "Hardware & Firmware Lifecycle"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 7
  controller_version_age_months_max: 6     # UniFi releases frequent updates
  ap_firmware_age_months_max: 6
  switch_firmware_age_months_max: 6
  gateway_firmware_age_months_max: 6
  ssid_open_authentication_allowed: false  # any "Open" SSID = critical (guest excepted)
  ssid_wep_or_wpa1_allowed: false
  ssid_psk_weak_chars_max: 12              # PSK shorter than N chars = weak
  guest_network_isolation_required: true
  guest_network_password_required: false   # captive-portal flow is acceptable
  default_admin_allowed: false             # 'ubnt' default = critical
  remote_access_required: true             # Ubiquiti SSO / remote console access required for MSP

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

- "Pull UniFi data for <customer>"
- "UniFi PBR / quarterly review"
- "UniFi controller version audit"
- "AP firmware audit"
- "SSID wireless security review"
- "Guest network audit"
- "UniFi local-admin audit"

Cadence: monthly per controller; quarterly in PBR; ad-hoc post-incident
or post-firmware-CVE.

Personas: NOC (operational — AP up/down), SOC (wireless security),
TAM (firmware currency, standards), vCIO/AM (refresh roadmap).

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the UniFi controller / site) | Yes | `liongard_system LIST query="unifi"` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="unifi"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Controller identity + version

```
liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative:
#   "unifi.controller.version"
#   "unifi.controller.versionReleaseDate"
#   "unifi.controller.hostType"                (self-hosted / UniFi Hosting / Cloud Key / UDM-managed)
#   "unifi.controller.siteName"
#   "unifi.controller.siteId"
#   "unifi.controller.uptimeDays"
```

### Step 4 — Device inventory

```
#   "unifi.devices.totalCount"
#   "unifi.devices.byType"                     (AP / switch / gateway)
#   "unifi.devices.onlineCount"
#   "unifi.devices.offlineCount"
#   "unifi.devices.byModel"
#   "unifi.devices.byFirmwareVersion"
#   "unifi.devices.firmwareUpToDateCount"
#   "unifi.devices.firmwareOutOfDateCount"
#   "unifi.devices.byClientCount"              (AP-side: connected clients)
#   "unifi.aps.totalCount"
#   "unifi.switches.totalCount"
#   "unifi.gateways.totalCount"
```

### Step 5 — SSIDs + wireless security

```
#   "unifi.ssids.totalCount"
#   "unifi.ssids.list"                          (name + security mode)
#   "unifi.ssids.byAuthMethod"                 (open / WPA2 / WPA3 / WPA-PSK / WPA-Enterprise)
#   "unifi.ssids.openSsidCount"
#   "unifi.ssids.wepOrWpa1Count"
#   "unifi.ssids.wpa2PskCount"
#   "unifi.ssids.wpa3PskCount"
#   "unifi.ssids.wpaEnterpriseCount"
#   "unifi.ssids.guestEnabledCount"
#   "unifi.ssids.broadcastDisabledCount"       (hidden SSIDs)
#   "unifi.ssids.bandSteeringEnabledCount"
#   "unifi.ssids.pmkCachingEnabledCount"
```

### Step 6 — Guest network audit

```
#   "unifi.guest.enabled"
#   "unifi.guest.isolationEnabled"             (Layer 2 isolation between guests)
#   "unifi.guest.portalEnabled"                (captive portal)
#   "unifi.guest.authenticationType"           (none / simple-password / voucher / RADIUS)
#   "unifi.guest.expirationConfigured"
#   "unifi.guest.preAuthSubnetsList"
```

### Step 7 — VLAN / Network configuration

```
#   "unifi.networks.totalCount"
#   "unifi.networks.byPurpose"                 (corporate / guest / VLAN-only / VPN)
#   "unifi.networks.vlanList"
#   "unifi.networks.dhcpEnabledCount"
#   "unifi.networks.firewallEnabledCount"      (for UDM gateway role)
```

### Step 8 — Local user + admin audit

```
#   "unifi.admins.totalCount"
#   "unifi.admins.byRole"                      (Super Admin / Limited Admin / Read-only)
#   "unifi.admins.defaultUbntCount"            ('ubnt' = critical)
#   "unifi.admins.mfaEnabledCount"             (where Ubiquiti SSO is in use)
#   "unifi.admins.lastLoginDays"
```

### Step 9 — Management + remote access

```
#   "unifi.management.remoteAccessEnabled"     (Ubiquiti SSO / Cloud Access)
#   "unifi.management.localCredentialAuth"
#   "unifi.management.upnpEnabled"
#   "unifi.management.ssh.enabled"
#   "unifi.management.snmpEnabled"
```

### Step 10 — Lifecycle

```
#   "unifi.devices.eolList"                    (UAP-AC-PRO / etc. nearing EOL)
#   "unifi.devices.discontinuedList"           (no longer manufactured)
```

### Step 11 — QA pass (per `reference/qa-retry-pattern.md`)

Standard pattern. UniFi controllers update frequently — flag stale
inspector data aggressively. Firmware tracks differ across device
type (AP / switch / gateway) — surface per-class firmware currency
rather than rolling up.

### Step 12 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | Network infrastructure + wireless. |
| CIS Controls (v8.1) | ✅ | CIS 12.1 (asset inventory), 12.6 (mgmt protocols), 12.8 (OOB mgmt), 4.4, 13.1, 15.1 (wireless network segregation), 15.7 (wireless authentication). |
| Cyber-insurance domain files | ✅ | `domains/network.md` Q19–Q21, Q35–Q36 + wireless segregation extends Q21. |
| QBR / quarterly-business-review | ✅ | Chained via `all-network-infrastructure.md`; AP / switch / gateway split is the headline. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| Controller version out of date | "UniFi controller <N> months old. Update — UniFi releases frequent security fixes." |
| Device firmware out of date | "<N> APs / switches / gateways with outdated firmware. Schedule update window." |
| Device offline | "<N> devices offline > <N> days. Triage — physical / network / PoE." |
| AP/device discontinued | "<N> devices on EOL / discontinued models. Refresh roadmap required." |
| Open SSID (non-guest) | "URGENT: <N> open SSIDs (non-guest). Configure WPA2 / WPA3." |
| WEP or WPA1 in use | "URGENT: <N> SSIDs use WEP / WPA1. Upgrade to WPA2 or WPA3 (preferred)." |
| Weak PSK | "<N> SSIDs use short / weak PSK. Rotate to ≥ 16-char passphrase or move to WPA-Enterprise." |
| Guest isolation off | "Guest network L2 isolation disabled. Enable per MSP baseline." |
| Guest auth none | "Guest network has no authentication. Configure captive portal." |
| Default 'ubnt' admin | "URGENT: 'ubnt' default admin enabled. Rename + rotate." |
| Admin without MFA | "<N> UniFi admins without MFA. Enforce via Ubiquiti SSO." |
| Remote access disabled | "Remote access (Ubiquiti SSO) disabled. Enable so MSP can manage." |
| UPnP enabled | "UPnP enabled. Disable on gateway." |
| SNMP weak | "SNMP weak community. Reconfigure." |
| Hidden SSID broadcast off | "<N> SSIDs hidden. Note: hiding ≠ security; review intent." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Per-client connection history | partial | UniFi Network app |
| RF / channel utilization detail | partial | UniFi Network app |
| Per-AP heatmap / coverage | external | UniFi Design Center |
| Threat Management / IDS detail (UDM gateway) | partial | UniFi Network app |
| Wireless intrusion detection (where licensed) | partial | UniFi Network app |
| UniFi Protect / UniFi Talk / UniFi Access cross-product detail | partial / external | Per-app UniFi console |

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

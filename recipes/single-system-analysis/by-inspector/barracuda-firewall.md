---
name: single-system-barracuda-firewall
description: >
  Use this skill when the user wants a single-firewall analysis of a
  Barracuda CloudGen Firewall appliance — PBR, configuration audit,
  license expiration, firmware audit, security-services posture,
  access-rule audit, VPN posture. Trigger phrases: "Barracuda PBR",
  "Barracuda firewall review", "CloudGen audit", "pull Barracuda data
  for <customer>", "Barracuda firmware audit".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, soc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, pptx]
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
---

# Single-System Analysis — Barracuda Firewall

> **Inspector:** `barracuda-firewall-inspector` (ID 52). Network
> category. Firewall. **One system per Barracuda CloudGen Firewall
> appliance.** Covers the F-series and X-series CloudGen Firewall
> product lines.
>
> **References:** `reference/inspector-aliases.md` (Barracuda).
> `reference/asset-fields.md` for asset cross-checks.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-barracuda-fw-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  identity: "Firewall Identity & Firmware"
  interfaces: "Interface & DNS Configuration"
  security_services: "Security Services Posture"
  access_rules: "Access Rules"
  vpn: "Site-to-Site & Client-to-Site VPN"
  local_users: "Local User & Admin Audit"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 1
  license_expiration_warn_days: 60
  firmware_age_months_max: 12
  open_rdp_to_internet_allowed: false
  wan_management_exposure_allowed: false
  default_local_users_max: 1

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

- "Pull Barracuda firewall data for <customer>"
- "Barracuda PBR"
- "Barracuda firmware audit"
- "Any Barracuda licenses / Energize Updates expiring?"
- "CloudGen Firewall config review"

Cadence: monthly per firewall; quarterly in PBR.

Personas: NOC, SOC, vCIO/AM, TAM.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the Barracuda appliance) | Yes | `liongard_system LIST query="barracuda"` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="barracuda"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Identity + firmware

```
liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative:
#   "barracuda-fw.system.model"
#   "barracuda-fw.system.serialNumber"
#   "barracuda-fw.system.firmwareVersion"
#   "barracuda-fw.system.uptimeDays"
#   "barracuda-fw.system.haMode"
```

### Step 4 — Interfaces + DNS

```
#   "barracuda-fw.interfaces.list"
#   "barracuda-fw.interfaces.wanZone"
#   "barracuda-fw.dns.servers"
#   "barracuda-fw.dhcp.scopes"
```

### Step 5 — Security services + Energize Updates

```
#   "barracuda-fw.energizeUpdates.expirationDate"   (subscription giving signature feeds)
#   "barracuda-fw.energizeUpdates.daysUntilExpiration"
#   "barracuda-fw.services.applicationControl.enabled"
#   "barracuda-fw.services.ips.enabled"
#   "barracuda-fw.services.atp.enabled"             (Advanced Threat Protection)
#   "barracuda-fw.services.virusProtection.enabled"
#   "barracuda-fw.services.urlFilter.enabled"
#   "barracuda-fw.services.sslInspection.enabled"
```

### Step 6 — Access rules

```
#   "barracuda-fw.rules.totalCount"
#   "barracuda-fw.rules.byAction"
#   "barracuda-fw.rules.openAnyToAnyCount"
#   "barracuda-fw.rules.wanToLanCount"
#   "barracuda-fw.rules.rdpAllowedCount"
#   "barracuda-fw.rules.disabledCount"
```

### Step 7 — VPN posture

```
#   "barracuda-fw.siteToSite.tunnelCount"
#   "barracuda-fw.siteToSite.byPhase1Encryption"
#   "barracuda-fw.clientToSite.usersCount"          (Barracuda Network Access Client)
#   "barracuda-fw.clientToSite.byAuthMethod"
#   "barracuda-fw.ssl-vpn.enabled"
```

### Step 8 — Local user + admin audit

```
#   "barracuda-fw.localUsers.totalCount"
#   "barracuda-fw.localUsers.adminCount"
#   "barracuda-fw.management.wanAllowed"
#   "barracuda-fw.management.byProtocol"
```

### Step 9 — QA pass (per `reference/qa-retry-pattern.md`)

Same firewall-tight thresholds as the other firewall recipes.

### Step 10 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | Firewall — different question set; covered by all-firewalls rollup. |
| CIS Controls (v8.1) | ✅ | CIS 12.1, 12.2, 12.6, 13.1, 13.6, 9.3 (URL filter), 4.4. |
| Cyber-insurance domain files | ✅ | `domains/network.md` Q19–Q21, Q35–Q36, Q41–Q43. |
| QBR / quarterly-business-review | ✅ | Chained via `all-firewalls.md`. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| Firmware out of date | "Barracuda firmware <N> months old. Schedule upgrade." |
| Energize Updates expiring | "Energize Updates expire <N> days. Renew — IPS / AV / URL filter signature feeds stop without it." |
| Service disabled | "<service> disabled. Confirm intent; re-enable per MSP baseline." |
| Open any-to-any rule | "URGENT: <N> any-to-any rules. Restrict per least-privilege." |
| WAN management exposed | "URGENT: Mgmt on WAN allowed. Restrict to MSP IP allowlist or VPN-only." |
| RDP allowed inbound | "URGENT: Inbound RDP rule. Remove or restrict to VPN-only." |
| S2S tunnel with weak crypto | "<N> tunnels use deprecated Phase 1 encryption. Upgrade to AES-256 / SHA-256." |
| C2S user without MFA | "<N> Client-to-Site users password-only. Enforce MFA via RADIUS." |
| Default admin enabled | "Default admin account present. Rename + rotate credential." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Per-rule hit count | partial | Barracuda Firewall Admin |
| ATP detection history | partial | Barracuda Cloud Control |
| URL Filter category detail | partial | Barracuda Cloud Control |
| Energize Updates subscription history | external | Barracuda Cloud Control |

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST + liongard_system LIST | per inspector | array | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3-8 | liongard_metric VALUE | envId=<ENV_ID> sysId=<SYS_ID> metric=<id> | varies | ok per metric |
| 9 | QA pass | per `reference/qa-retry-pattern.md` | varies | ok |
| 10 | render | per `output.format` | <artifact path> | ok |
```

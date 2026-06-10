---
name: single-system-palo-alto-panos
description: >
  Use this skill when the user wants a single-firewall analysis of a
  Palo Alto Networks firewall (PAN-OS) or Panorama-managed appliance —
  PBR, configuration audit, license / subscription expiration,
  PAN-OS version audit, security-services posture, security-rule audit,
  GlobalProtect / IPSec VPN posture. Trigger phrases: "Palo Alto PBR",
  "PAN-OS audit", "Palo Alto license review", "pull Palo Alto data
  for <customer>", "GlobalProtect audit", "Panorama review".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, soc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, pptx]
primitives:
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
---

# Single-System Analysis — Palo Alto PAN-OS

> **Inspector:** `palo-alto-panos-inspector` (ID 49). Beta. Network
> category. Firewall. **One system per Palo Alto firewall or per
> Panorama-managed device-group.** Covers PA-series, VM-Series, and
> Panorama deployments.
>
> **Beta inspector caveat:** Field coverage and metric names/JMESPath queries may shift
> as the inspector progresses out of beta. Verify metric names/JMESPath queries with
> `liongard_metric LIST` before relying on them in production
> deliverables.
>
> **References:** `reference/inspector-aliases.md` (PA, Palo Alto,
> PAN-OS, Panorama).

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-palo-alto-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  identity: "Firewall Identity & PAN-OS Version"
  interfaces: "Interface & Zone Configuration"
  subscriptions: "Subscription Services (Threat / URL / WildFire / DNS / SD-WAN)"
  security_rules: "Security Rules"
  vpn: "GlobalProtect & IPSec"
  admin: "Admin & Local-User Audit"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 1
  license_expiration_warn_days: 60
  panos_age_months_max: 12                  # PAN-OS major versions
  open_rdp_to_internet_allowed: false
  wan_management_exposure_allowed: false
  default_admin_present_max: 0              # 'admin' account = critical
  any_any_rule_max: 0

reporting_period: { default: "current_state" }

qa:
  retry_on_null: true
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 1
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: false            # Beta inspector — expect many proposed metrics
  manual_verification_section_required: true
```

---

## When to use

- "Pull Palo Alto data for <customer>"
- "Palo Alto PBR"
- "PAN-OS version audit"
- "Any Palo Alto subscriptions expiring?"
- "GlobalProtect audit"
- "Panorama device-group review"

Cadence: monthly per firewall; quarterly in PBR.

Personas: NOC, SOC, vCIO/AM, TAM. **Note:** Palo Alto deployments
typically have a dedicated security team — SOC engagement is high.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the Palo Alto firewall or Panorama) | Yes | `liongard_system LIST query="palo-alto"` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="palo-alto"
```

Confirm whether the system is a **standalone firewall** or a
**Panorama-managed device** — the metric set differs.

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Identity + PAN-OS version

```
liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative (verify with liongard_metric LIST):
#   "palo-alto.system.hostname"
#   "palo-alto.system.serialNumber"
#   "palo-alto.system.model"
#   "palo-alto.system.panosVersion"
#   "palo-alto.system.panosReleaseDate"
#   "palo-alto.system.uptimeDays"
#   "palo-alto.system.haState"               (active / passive / standalone)
#   "palo-alto.system.managedBy"             (standalone / panorama)
```

### Step 4 — Interfaces + zones

```
#   "palo-alto.interfaces.list"
#   "palo-alto.zones.list"
#   "palo-alto.zones.untrustList"            (WAN-equivalent zones)
#   "palo-alto.dns.servers"
```

### Step 5 — Subscription services

```
#   "palo-alto.subscriptions.threatPreventionExpiration"
#   "palo-alto.subscriptions.urlFilteringExpiration"  (PAN-DB)
#   "palo-alto.subscriptions.wildFireExpiration"
#   "palo-alto.subscriptions.dnsSecurityExpiration"
#   "palo-alto.subscriptions.gpExpiration"            (GlobalProtect Portal/Gateway)
#   "palo-alto.subscriptions.iotSecurityExpiration"
#   "palo-alto.subscriptions.advancedThreatPreventionExpiration"
#   "palo-alto.subscriptions.daysUntilNextExpiration"
```

### Step 6 — Security rules

```
#   "palo-alto.rules.totalCount"
#   "palo-alto.rules.byAction"               (allow / deny / drop / reset-client / reset-server)
#   "palo-alto.rules.anyAnyCount"
#   "palo-alto.rules.untrustToTrustCount"
#   "palo-alto.rules.rdpAllowedCount"
#   "palo-alto.rules.disabledCount"
#   "palo-alto.rules.unusedCount"            (hit-count == 0 since last reset)
#   "palo-alto.rules.appIdEnabledCount"
#   "palo-alto.rules.userIdEnabledCount"
```

### Step 7 — VPN posture

```
#   "palo-alto.globalProtect.portalsCount"
#   "palo-alto.globalProtect.gatewaysCount"
#   "palo-alto.globalProtect.connectedUsersLast30Days"
#   "palo-alto.globalProtect.authProfileList"
#   "palo-alto.globalProtect.mfaEnabledCount"
#   "palo-alto.ipsec.tunnelCount"
#   "palo-alto.ipsec.byPhase1Encryption"
#   "palo-alto.ipsec.byPhase2Encryption"
```

### Step 8 — Admin + local-user audit

```
#   "palo-alto.admins.totalCount"
#   "palo-alto.admins.byRole"                (Superuser / Device admin / Vsys admin / etc.)
#   "palo-alto.admins.byAuthMethod"          (local / TACACS+ / RADIUS / SAML)
#   "palo-alto.admins.defaultNamedCount"     ('admin' present = critical)
#   "palo-alto.admins.mfaEnabledCount"
#   "palo-alto.management.wanAllowed"
#   "palo-alto.management.byProtocol"
```

### Step 9 — QA pass (per `reference/qa-retry-pattern.md`)

Beta-specific: expect more data gap metrics than other firewall
recipes. File metric requests for any baseline check the current
inspector doesn't cover. Cross-check Panorama-managed devices —
config differs from standalone.

### Step 10 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | Firewall — different question set. |
| CIS Controls (v8.1) | ✅ | CIS 12.1, 12.2, 12.6, 13.1, 13.6, 9.3, 9.4 (URL filter, DNS security), 4.4, 10.1 (App-ID / WildFire). |
| Cyber-insurance domain files | ✅ | `domains/network.md` Q19–Q21, Q35–Q36, Q41–Q43. Palo Alto's App-ID / User-ID make Q21 (zero-trust posture) particularly strong. |
| QBR / quarterly-business-review | ✅ | Chained via `all-firewalls.md`. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| PAN-OS major-version out of date | "PAN-OS <version> is <N> months old. Plan upgrade — Palo Alto support policy ages out old majors fast." |
| Threat / URL / WildFire subscription expiring | "<subscription> expires <N> days. Renew — without it, signature feeds halt." |
| Any-any rule present | "URGENT: <N> any-any rules. Palo Alto policy hygiene expects explicit App-ID + User-ID per rule." |
| Untrust-to-trust rule | "URGENT: <N> Untrust-to-Trust rules. Confirm legitimate; restrict per least-privilege." |
| Rule without App-ID | "<N> rules without App-ID. Convert from port-based to App-ID for full coverage." |
| Rule without User-ID | "<N> rules without User-ID. Map to AD / Entra users via User-ID agent." |
| Unused rules | "<N> rules with zero hits since last counter reset. Confirm; remove if obsolete." |
| GlobalProtect without MFA | "GlobalProtect Portal authprofile is single-factor. Configure SAML / RADIUS MFA." |
| Default 'admin' account present | "URGENT: Built-in 'admin' account active. Rename + rotate; consider TACACS+/RADIUS for all admins." |
| Mgmt on WAN | "URGENT: Management interface accepts WAN. Restrict via permitted-IP list or MGT-port isolation." |
| HA misconfigured | "HA shows <state>; expected active/passive pair. Investigate." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Per-rule hit count history | partial | Panorama / Firewall web UI / API |
| Threat-log detail | partial | Panorama logging / Strata Logging Service |
| WildFire submission history | partial | WildFire portal |
| App-ID category breakdown | partial | Panorama |
| URL Filter / PAN-DB category usage | partial | Panorama |
| GP gateway-by-gateway connection history | partial | Panorama |

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

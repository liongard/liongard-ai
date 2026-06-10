---
name: single-system-watchguard
description: >
  Use this skill when the user wants a single-firewall analysis of a
  WatchGuard appliance — Periodic Business Review, configuration audit,
  license / subscription expiration, firmware audit, security-services
  posture, branch-office VPN posture, BOVPN / Mobile VPN review.
  Trigger phrases: "WatchGuard PBR", "WG firewall review", "pull
  WatchGuard data for <customer>", "WatchGuard license audit",
  "WatchGuard firmware review", "Firebox audit", "BOVPN review".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, soc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, pptx]
primitives:
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

# Single-System Analysis — WatchGuard

> **Inspector:** `watchguard-inspector` (ID 29). Network category.
> Firewall. **One system per WatchGuard Firebox appliance.**
> Covers Firebox T, M, and FireboxV / Firebox Cloud product lines.
>
> **References:** `reference/inspector-aliases.md` (WatchGuard, WG,
> Firebox). `reference/asset-fields.md` for asset cross-checks.
> `reference/qa-retry-pattern.md` for QA pass details.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-watchguard-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  identity: "Firewall Identity & Firmware"
  interfaces: "Interface & DNS Configuration"
  subscription_services: "Subscription Services (TSS / GAV / IPS / etc.)"
  policies: "Firewall Policies"
  vpn: "BOVPN & Mobile VPN"
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

- "Pull WatchGuard data for <customer>"
- "WatchGuard PBR / quarterly review"
- "WatchGuard firmware audit"
- "Any WatchGuard subscriptions expiring?"
- "Firebox BOVPN review"
- "WG security-services posture check"

Cadence: monthly per firewall; quarterly in PBR.

Personas: NOC (operational), SOC (security posture), vCIO/AM (renewal),
TAM (standards alignment).

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the WatchGuard appliance) | Yes | `liongard_system LIST query="watchguard"` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="watchguard"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Firewall identity + firmware

```
liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative:
#   "watchguard.system.model"
#   "watchguard.system.serialNumber"
#   "watchguard.system.firmwareVersion"
#   "watchguard.system.firmwareReleaseDate"
#   "watchguard.system.haMode"               (Standalone / Active-Passive / Active-Active)
#   "watchguard.system.uptimeDays"
```

### Step 4 — Interfaces + DNS

```
#   "watchguard.interfaces.list"
#   "watchguard.interfaces.wanZone"
#   "watchguard.dns.servers"
#   "watchguard.dhcp.scopes"
```

### Step 5 — Subscription services posture

```
#   "watchguard.tss.expirationDate"          (Total Security Suite — superset)
#   "watchguard.tss.daysUntilExpiration"
#   "watchguard.services.gateway-av.enabled"
#   "watchguard.services.ips.enabled"
#   "watchguard.services.webblocker.enabled"
#   "watchguard.services.spamblocker.enabled"
#   "watchguard.services.reputationDefense.enabled"
#   "watchguard.services.applicationControl.enabled"
#   "watchguard.services.threatDetection.enabled"
```

### Step 6 — Firewall policies

```
#   "watchguard.policies.totalCount"
#   "watchguard.policies.byAction"           (allow / deny / pbr)
#   "watchguard.policies.openAnyToAnyCount"  (highest risk)
#   "watchguard.policies.wanToLanCount"
#   "watchguard.policies.rdpAllowedCount"
#   "watchguard.policies.disabledCount"
```

### Step 7 — VPN posture

```
#   "watchguard.bovpn.tunnelCount"           (branch-office VPN tunnels)
#   "watchguard.bovpn.byPhase1Encryption"
#   "watchguard.bovpn.byPhase2Encryption"
#   "watchguard.mobileVpn.usersCount"        (SSL VPN / IKEv2 / IPSec users)
#   "watchguard.mobileVpn.byAuthMethod"
```

### Step 8 — Local user + admin audit

```
#   "watchguard.localUsers.totalCount"
#   "watchguard.localUsers.adminCount"
#   "watchguard.localUsers.defaultNamedCount" (admin / status / etc.)
#   "watchguard.management.wanAllowed"
#   "watchguard.management.byProtocol"       (HTTPS / SSH / etc.)
```

### Step 9 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on retry, freshness (firewalls are inspector-lastseen-1-day),
cross-tool divergence (firewall WAN IP vs. Network IP inspector if
deployed), proposed-metric gaps.

### Step 10 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | Firewall, not endpoint — different question set. The all-firewalls.md rollup covers cross-vendor firewall coverage. |
| CIS Controls (v8.1) | ✅ | Maps to CIS 12.1 (network infrastructure), 12.2 (boundary protection), 12.6 (mgmt protocols), 13.1 (network monitoring), 13.6 (IDS), 9.3 (DNS filtering — WebBlocker), 4.4 (configuration management). |
| Cyber-insurance domain files | ✅ | Aligns with `domains/network.md` Q19–Q21 (firewall config), Q35–Q36 (firmware currency), Q41–Q43 (VPN). |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this via `all-firewalls.md`; surfaces TSS expiration, firmware age, open-RDP, WAN mgmt exposure. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| Firmware out of date | "WatchGuard firmware <N> months old. Schedule upgrade to current Fireware OS." |
| TSS / subscription expiring | "Total Security Suite expires <N> days. Initiate renewal — without TSS, security services disable." |
| Specific service disabled | "<service> disabled. Confirm intent; re-enable per MSP baseline." |
| Open any-to-any policy | "URGENT: <N> any-to-any policies in policy list. Restrict per least-privilege." |
| WAN management exposed | "URGENT: Management on WAN allowed. Restrict to MSP IP allowlist or VPN-only." |
| RDP allowed inbound | "URGENT: Inbound RDP policy detected. Remove or restrict to VPN-only access." |
| BOVPN with weak crypto | "<N> BOVPN tunnels use deprecated Phase 1/2 encryption. Upgrade to AES-256 / SHA-256." |
| Mobile VPN with password-only auth | "<N> Mobile VPN users password-only. Enforce MFA via RADIUS + Authpoint or external IdP." |
| Default local admin enabled | "Default admin account present. Rename + rotate credential." |
| HA mismatch (standalone where pair expected) | "Firewall in Standalone mode; MSP standard is HA pair. Confirm intent." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Per-policy rule hit counts | partial | WatchGuard Firebox System Manager (WSM) |
| BOVPN tunnel health (up/down history) | partial | WSM / Dimension |
| Per-service license-tier detail | partial | WatchGuard Portal |
| WebBlocker policy detail | partial | WSM |
| Subscription history | external | WatchGuard Portal |

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

---
name: single-system-sophos-sg
description: >
  Use this skill when the user wants a single-firewall analysis of a
  Sophos SG (legacy UTM) appliance — PBR, configuration audit, license
  / subscription expiration, firmware audit, security-services
  posture, migration-to-XGS planning. Trigger phrases: "Sophos SG
  review", "Sophos UTM audit", "legacy Sophos firewall PBR", "Sophos
  SG to XGS migration".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, soc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, pptx]
primitives:
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
---

# Single-System Analysis — Sophos SG (Legacy UTM)

> **Inspector:** `sophos-sg-inspector` (ID 43). Network category.
> Firewall. **One system per Sophos SG appliance.** **Legacy UTM
> firmware** — Sophos's modern firewall is Sophos Firewall (XG / XGS,
> covered by `sophos-firewall-inspector` / recipe
> `sophos-firewall.md`). Distinct from Sophos Central (`sophos-central-inspector`
> — endpoint EDR, not network).
>
> **Three Sophos inspectors — confirm which:** When a user says
> "Sophos", clarify whether they mean Sophos Central (EDR),
> Sophos Firewall (XG / XGS), or Sophos SG (this legacy line).
>
> **Migration relevance:** Sophos SG firmware has been in extended
> sustaining support since 2022. New deployments use XGS. Most SG
> assessments in 2026 produce a migration-to-XGS recommendation.
>
> **References:** `reference/inspector-aliases.md` (Sophos SG).

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-sophos-sg-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  identity: "Firewall Identity & Firmware"
  interfaces: "Interface & DNS Configuration"
  subscription_services: "Subscription / Web Protection / Email Protection"
  rules: "Firewall Rules"
  vpn: "Site-to-Site & Remote Access VPN"
  local_users: "Local User & Admin Audit"
  migration: "Migration to XGS — Planning Notes"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 1
  license_expiration_warn_days: 60
  firmware_age_months_max: 6                  # legacy — flag aggressively
  open_rdp_to_internet_allowed: false
  wan_management_exposure_allowed: false
  default_local_users_max: 1
  migration_recommendation_required: true     # always include the XGS migration narrative

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

- "Sophos SG legacy firewall review"
- "Sophos UTM audit"
- "Pull Sophos SG data for <customer>"
- "Sophos SG to XGS migration planning"

Cadence: monthly per firewall; quarterly in PBR. **Always pair with a
migration recommendation** — SG is sunset technology.

Personas: NOC (operational), SOC (security — legacy crypto risk),
vCIO/AM (renewal + migration narrative), TAM (XGS migration planning).

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the Sophos SG appliance) | Yes | `liongard_system LIST query="sophos-sg"` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="sophos-sg"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Identity + firmware

```
liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative:
#   "sophos-sg.system.model"                 (SG XX, SG-virtual, etc.)
#   "sophos-sg.system.firmwareVersion"       (SG firmware track is distinct from XG)
#   "sophos-sg.system.firmwareReleaseDate"
#   "sophos-sg.system.serialNumber"
#   "sophos-sg.system.uptimeDays"
#   "sophos-sg.system.haMode"
```

### Step 4 — Interfaces + DNS

```
#   "sophos-sg.interfaces.list"
#   "sophos-sg.interfaces.wanZone"
#   "sophos-sg.dns.servers"
#   "sophos-sg.dhcp.scopes"
```

### Step 5 — Subscription / protection services

```
#   "sophos-sg.subscriptions.expirationDate"
#   "sophos-sg.subscriptions.daysUntilExpiration"
#   "sophos-sg.webProtection.enabled"
#   "sophos-sg.webProtection.categoryFilter"
#   "sophos-sg.emailProtection.enabled"
#   "sophos-sg.networkProtection.enabled"
#   "sophos-sg.wirelessProtection.enabled"
```

### Step 6 — Firewall rules

```
#   "sophos-sg.rules.totalCount"
#   "sophos-sg.rules.byAction"
#   "sophos-sg.rules.openAnyToAnyCount"
#   "sophos-sg.rules.wanToLanCount"
#   "sophos-sg.rules.rdpAllowedCount"
#   "sophos-sg.rules.disabledCount"
```

### Step 7 — VPN posture

```
#   "sophos-sg.ipsec.tunnelCount"
#   "sophos-sg.ipsec.byPhase1Encryption"
#   "sophos-sg.ssl-vpn.userCount"
#   "sophos-sg.ssl-vpn.byAuthMethod"
```

### Step 8 — Local user + admin audit

```
#   "sophos-sg.localUsers.totalCount"
#   "sophos-sg.localUsers.adminCount"
#   "sophos-sg.management.wanAllowed"
```

### Step 9 — Migration-to-XGS planning

The recipe surfaces:
- Current SG model + firmware vs. equivalent XGS model
- Subscription expiration date — common XGS migration trigger
- Estimated rule-conversion effort (SG → XGS rule schema differs)
- Cross-reference: is the customer also a Sophos Central EDR
  customer? (XGS + Central pair tightly via Synchronized Security.)

### Step 10 — QA pass (per `reference/qa-retry-pattern.md`)

Same firewall thresholds. Verify the system was correctly identified
as SG (vs. Sophos Firewall) — they're distinct inspectors.

### Step 11 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | Firewall — different question set. |
| CIS Controls (v8.1) | ✅ | CIS 12.1, 12.2, 12.6, 13.1, 13.6, 9.3, 4.4. |
| Cyber-insurance domain files | ✅ | `domains/network.md` Q19–Q21, Q35–Q36, Q41–Q43. **Important:** SG firmware in extended support may fail Q35 (firmware currency) — surface the migration recommendation prominently. |
| QBR / quarterly-business-review | ✅ | Chained via `all-firewalls.md`. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| **SG platform — sustaining support only** | "Customer is on Sophos SG (legacy UTM). Recommend migration to XGS by <subscription-expiration-date> at latest. Pair migration with Sophos Central for Synchronized Security." |
| Firmware out of date | "SG firmware <N> months old. Patch if XGS migration not in window; new deployments should not use SG." |
| Subscription expiring | "Sophos subscription expires <N> days. Renewal == migration trigger — quote XGS pricing alongside." |
| Open any-to-any rule | "URGENT: <N> any-to-any rules. Restrict per least-privilege." |
| WAN mgmt exposed | "URGENT: Mgmt on WAN allowed. Restrict to MSP IP allowlist." |
| RDP allowed inbound | "URGENT: Inbound RDP rule. Remove or restrict to VPN." |
| IPSec tunnel weak crypto | "<N> tunnels use deprecated Phase 1 encryption. Upgrade." |
| SSL VPN without MFA | "SSL VPN single-factor. Enforce MFA via Sophos Authenticator / RADIUS." |
| Default admin enabled | "Default admin account active. Rename + rotate." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Per-rule hit count | partial | Sophos UTM Console |
| Web Protection category-level usage | partial | UTM Console |
| Email Protection / SMTP proxy detail | partial | UTM Console |
| SG-vs-XGS migration tool support | partial | Sophos Central Migration Wizard |

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST + liongard_system LIST | per inspector | array | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3-8 | liongard_metric VALUE | envId=<ENV_ID> sysId=<SYS_ID> metric=<id> | varies | ok per metric |
| 9 | (migration narrative — derived) | per slas.migration_recommendation_required | narrative block | ok |
| 10 | QA pass | per `reference/qa-retry-pattern.md` | varies | ok |
| 11 | render | per `output.format` | <artifact path> | ok |
```

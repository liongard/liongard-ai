---
name: single-system-sophos-firewall
description: >
  Use this skill when the user wants a single-firewall analysis of a
  Sophos XG / XGS firewall (NOT Sophos Central, NOT Sophos SG legacy)
  — Periodic Business Review, firmware audit, security-services posture
  (IPS, Gateway AV), firewall rule summary, site-to-site VPN review,
  central-management status. Trigger phrases: "Sophos XG review", "XGS
  firewall PBR", "pull Sophos firewall data", "Sophos XG audit", "Sophos
  firewall rules review". Confirm with user that they mean the XG/XGS
  firewall, not Sophos Central (endpoint EDR) or Sophos SG (legacy UTM).
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, soc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, pptx]
primitives:
  - metrics:sophos-firewall:active-user-list
  - metrics:sophos-firewall:device-dns-summary
  - metrics:sophos-firewall:interfaces-count
  - metrics:sophos-firewall:security-policy-summary
  - metrics:sophos-firewall:user-group-summary
  - metrics:sophos-firewall:user-summary
  - metrics:sophos-firewall:zone-summary
---

# Single-System Analysis — Sophos Firewall (XG / XGS)

> **Inspector:** `sophos-firewall-inspector` (ID 28). Network category.
> Firewall (XG / XGS).
>
> **Naming gotcha — three Sophos inspectors exist.** Always confirm with
> the user which they mean before running this recipe:
> - `sophos-firewall-inspector` (this one) — XG / XGS firewall
> - `sophos-central-inspector` — cloud EDR / endpoint protection
> - `sophos-sg-inspector` — legacy SG firewall (different product line)
>
> **References:** `reference/inspector-aliases.md` (Sophos XG, Sophos
> XGS, XG firewall, XGS firewall). `reference/asset-fields.md` for asset
> cross-checks. `reference/qa-retry-pattern.md` for QA pass details.


---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-sophos-firewall-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  identity: "Firewall Identity"
  central_management: "Sophos Central Management Status"
  policies: "Firewall Policy Summary"
  services: "Security Services Posture"
  vpn: "Site-to-Site VPN"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 1
  license_expiration_warn_days: 60
  firmware_age_months_max: 12

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

- "Pull Sophos XG / XGS firewall data for the customer"
- "Sophos firewall rules review"
- "Is the Sophos firewall centrally managed?"
- "Sophos XG firmware audit"

> If the user just says "Sophos", **ask which inspector** before running:
> firewall (this one), Central (EDR), or SG (legacy UTM)? Three distinct
> inspectors with different recipes.

Personas: NOC, SOC, vCIO/AM, TAM.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Sophos Firewall system ID | Yes | `liongard_system LIST query="sophos-firewall"` |
| Reporting period | No | Default per customization |

---

## Locating the right system

```
liongard_system LIST searchMode=keyword query="sophos-firewall" environmentId=<ENV_ID>
```

> **Be explicit with `sophos-firewall`** — bare `sophos` returns matches
> from all three Sophos inspectors. The Liongard inspector slug is the
> disambiguation key.

`SystemInfo.Hostname` (not in current dataprint) returns the firewall display name.


---

## Liongard data sources

> **Asset Inventory First, Metric Cross-Check.** The Sophos firewall
> dataprint is the source of truth for *firewall configuration*. The
> cross-inspector device inventory tells you what's behind the firewall.
> If the firewall is also managed via `sophos-central-inspector`, the
> Central recipe is a sibling that contributes endpoint-side context.

### Per-vendor data — Sophos firewall dataprint top-level keys

| Key | Description |
|---|---|
| `SystemInfo` | Firewall identity — hostname, model, firmware |
| `SecurityPolicies` | Firewall rule list (zone-to-zone) |
| `Zones` | Security zone definitions (LAN, WAN, DMZ) |
| `Services` | Per-service enable/disable flags (IPS, Gateway AV, etc.) |
| `VpnConnections` | Site-to-site VPN tunnel list |
| `DhcpServers` | DHCP server scope detail |

#### Field gotchas (inline notes — not TODO)

- **Three Sophos inspectors share the vendor name.** When in doubt, ask
  the user which they mean. Confirming via the inspector slug
  (`sophos-firewall-inspector` vs. `sophos-central-inspector` vs.
  `sophos-sg-inspector`) is the disambiguation pattern across the
  library.

### Cross-inspector cross-check — device inventory

```
liongard_device LIST environmentId=<ENV_ID>
                     fields=["hostname","manufacturer","inspectors","internalIP"]
```

```
managed_devices = devices where category == "compute"
# Sophos firewall doesn't directly enumerate connected devices.
# Cross-check device count via RMM or other inspectors.
```

---

## Metrics and queries

### Firewall policies

| Metric | JMESPath | Result shape |
|---|---|---|
| Security policy summary | `SecurityPolicies[*]` | `<array>` |

### Proposed metrics (not yet in Liongard library)

The partner audit identified Sophos Firewall as a major gap area — most
The following onboarding-QA fields are not in the current dataprint:

| Field | Workaround |
|---|---|
| Hostname (separate metric) | Read `SystemInfo` directly |
| Central management status | Cross-check both `sophos-firewall-inspector` AND `sophos-central-inspector` — overlap = centrally managed |
| WAN admin access exposure | Manual review of zone configuration in Sophos UI |
| IPS / Gateway AV / VPN service status | Manual review in Sophos UI |
| DNS configuration (primary/secondary/tertiary) | Manual review in Sophos UI |
| DHCP scope detail | Manual review in Sophos UI |

### Time-series — policy / service trend

```
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="length(SecurityPolicies)"
```

---

## QA & Manual Verification

Run the QA pass per `reference/qa-retry-pattern.md` before rendering output:

1. **Retry persistent nulls.** Retry up to `qa.retry_attempts` times.

2. **Flag stale inspector data.** Sophos Firewall lastSeen > 1 day = API
   / SSH access issue.

3. **Cross-tool divergence (when applicable).** If the customer also has
   `sophos-central-inspector` deployed, confirm both inspectors agree on
   the firewall's central-management status.

4. **Proposed-metric gaps for this recipe** — surface these in the
   manual-verification appendix:
   - Hostname (separate metric)
   - Central management status
   - WAN admin access exposure
   - IPS / Gateway AV / VPN service status
   - DNS configuration (primary / secondary / tertiary)
   - DHCP scope detail

5. **Manual Verification appendix** — render in the deliverable. Typical
   items for this recipe:
   - Confirm in Sophos UI: IPS + Gateway AV service status.
   - Confirm in Sophos UI: WAN-side admin access posture.
   - Confirm in Sophos UI: DNS + DHCP configuration.
   - If centrally managed, run the `sophos-central` recipe alongside for
     endpoint-side context.

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Centrally managed (cross-link) | both `sophos-firewall-inspector` and `sophos-central-inspector` see this customer | "Sophos firewall is centrally managed via Sophos Central — run the sophos-central recipe alongside for the endpoint-side picture." |
| Excess firewall policies | `length(SecurityPolicies)` very high | "<N> firewall policies — consider periodic policy cleanup; review for shadowed or unused rules." |
| Stale inspector | `lastSeen > 1 day` | "Sophos firewall inspector hasn't reported in <N> days — confirm API / SSH access." |


---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Traffic / bandwidth analytics | ❌ not in dataprint | Sophos Central reporting / iView |
| Threat / IPS detection counts | ❌ not in dataprint | Sophos Central reporting |
| Most onboarding-QA fields | ⚠️ not in dataprint metrics | Sophos UI |
| Synchronized Security Heartbeat detail | ❌ not in dataprint | Sophos Central |
| Web Application Firewall rule detail | ❌ not in dataprint | Sophos UI |


---

## Output format

Markdown / Word / PowerPoint per `output.format`.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_system LIST | query="sophos-firewall" envId=<ENV_ID> | array<system> | ok |
| 3 | liongard_metric EVALUATE | metricName or jmesPathQuery sysId=<SYS_ID> envId=<ENV_ID> | <integer>, <array> | ok per metric |
| 4 | liongard_device LIST | envId=<ENV_ID> fields=[hostname,manufacturer,inspectors,internalIP] | array<device> | ok |
| 5 | (QA pass) retry persistent nulls | per `reference/qa-retry-pattern.md` | varies | ok |
```

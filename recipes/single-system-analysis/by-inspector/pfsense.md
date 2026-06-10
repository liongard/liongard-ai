---
name: single-system-pfsense
description: >
  Use this skill when the user wants a single-firewall analysis of a
  pfSense / Netgate firewall — PBR, configuration audit, package
  inventory, firmware audit, NAT / outbound-rule audit, VPN posture.
  Trigger phrases: "pfSense PBR", "pfSense firewall review", "Netgate
  audit", "pull pfSense data for <customer>", "pfSense firmware
  audit", "pfSense package review".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, soc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, pptx]
primitives:
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
---

# Single-System Analysis — pfSense

> **Inspector:** `pfsense-inspector` (ID 37). Network category.
> Firewall. **One system per pfSense / Netgate appliance.** Open-source
> firewall with optional commercial packages; common in SMB and
> price-sensitive deployments. Distinct from OPNsense (no Liongard
> inspector for OPNsense today).
>
> **References:** `reference/inspector-aliases.md` (pfSense, Netgate).

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-pfsense-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  identity: "Firewall Identity & Firmware"
  interfaces: "Interface & DNS Configuration"
  packages: "Package Inventory"
  firewall_rules: "Firewall & NAT Rules"
  vpn: "IPSec / OpenVPN / WireGuard"
  local_users: "Local User & Admin Audit"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 1
  firmware_age_months_max: 6                  # pfSense releases more frequent than commercial firewalls
  open_rdp_to_internet_allowed: false
  wan_management_exposure_allowed: false
  default_local_users_max: 1                  # admin only by default
  required_packages: []                       # e.g., ["pfBlockerNG-devel","Suricata"] — MSP baseline
  prohibited_packages: []                     # e.g., ["bandwidthd"] — discouraged packages

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

- "Pull pfSense data for <customer>"
- "pfSense PBR / quarterly review"
- "pfSense firmware audit"
- "pfSense package inventory"
- "pfSense rule audit"

Cadence: monthly per firewall; quarterly in PBR.

Personas: NOC, SOC, vCIO/AM, TAM.

> **Note on pfSense Community vs. pfSense Plus:** Netgate's commercial
> edition (Plus) supersedes the Community Edition as of 2.7+. Recipe
> surfaces which edition is detected so the AM conversation can include
> upgrade-to-Plus discussion if applicable.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the pfSense appliance) | Yes | `liongard_system LIST query="pfsense"` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="pfsense"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Identity + firmware

```
liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative:
#   "pfsense.system.hostname"
#   "pfsense.system.platform"               (Community Edition vs Plus)
#   "pfsense.system.version"                (e.g. 2.7.2 CE, 23.09 Plus)
#   "pfsense.system.versionReleaseDate"
#   "pfsense.system.netgateModel"           (where applicable — SG-1100 / SG-3100 / etc.)
#   "pfsense.system.uptimeDays"
#   "pfsense.system.haRole"                 (CARP master / backup / standalone)
```

### Step 4 — Interfaces + DNS

```
#   "pfsense.interfaces.list"
#   "pfsense.interfaces.wanZone"
#   "pfsense.dns.servers"
#   "pfsense.dns.resolverEnabled"           (Unbound)
#   "pfsense.dhcp.scopes"
```

### Step 5 — Package inventory

```
#   "pfsense.packages.installedList"
#   "pfsense.packages.count"
#   "pfsense.packages.updateAvailableCount"
```

Cross-check installed packages against `slas.required_packages` and
`slas.prohibited_packages` from the customization block.

### Step 6 — Firewall + NAT rules

```
#   "pfsense.fwRules.totalCount"
#   "pfsense.fwRules.byAction"              (pass / block / reject)
#   "pfsense.fwRules.openAnyToAnyCount"
#   "pfsense.fwRules.wanToLanCount"
#   "pfsense.fwRules.disabledCount"
#   "pfsense.natRules.outboundCount"
#   "pfsense.natRules.portForwardCount"
#   "pfsense.natRules.rdpForwardCount"
```

### Step 7 — VPN posture

```
#   "pfsense.ipsec.tunnelCount"
#   "pfsense.ipsec.byPhase1Encryption"
#   "pfsense.openvpn.serverCount"
#   "pfsense.openvpn.clientCount"
#   "pfsense.openvpn.tlsAuthEnabledCount"
#   "pfsense.wireguard.tunnelCount"
#   "pfsense.wireguard.peerCount"
```

### Step 8 — Local user + admin audit

```
#   "pfsense.localUsers.totalCount"
#   "pfsense.localUsers.adminCount"
#   "pfsense.management.wanAllowed"
#   "pfsense.management.byProtocol"          (HTTPS / SSH)
#   "pfsense.management.lockoutEnabled"
```

### Step 9 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on retry, freshness, proposed-metric gaps. Note: pfSense's
field availability depends on which packages are installed; document
gaps with "package not installed" in the finding context.

### Step 10 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | Firewall — different question set. |
| CIS Controls (v8.1) | ✅ | CIS 12.1, 12.2, 12.6, 13.1, 13.6, 4.4. (CIS 9.3 / 9.2 if pfBlockerNG installed for DNS / URL filtering.) |
| Cyber-insurance domain files | ✅ | `domains/network.md` Q19–Q21, Q35–Q36, Q41–Q43. Note: pfSense lacks vendor-licensed signature feeds by default — flag if customer's policy requires commercial IPS / threat-intel feeds. |
| QBR / quarterly-business-review | ✅ | Chained via `all-firewalls.md`. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| Version out of date | "pfSense version <N> months old. Schedule upgrade." |
| Required package missing | "Required package `<pkg>` not installed. Install per MSP baseline." |
| Prohibited package installed | "Discouraged package `<pkg>` installed. Confirm intent; remove if not required." |
| Open any-to-any rule | "URGENT: <N> any-to-any rules in fwRule list. Restrict per least-privilege." |
| WAN management exposed | "URGENT: Webconfigurator on WAN allowed. Restrict via firewall rule + use VPN access." |
| RDP port-forward | "URGENT: <N> port-forward rules to TCP/3389. Remove or restrict to VPN." |
| IPSec tunnel weak crypto | "<N> IPSec tunnels use deprecated Phase 1 encryption. Upgrade to AES-256." |
| OpenVPN without TLS auth | "<N> OpenVPN servers without TLS auth. Enable for additional protection." |
| Default admin name | "Admin account named 'admin'. Rename + rotate credential." |
| Lockout disabled | "Webconfigurator lockout not enabled. Enable per MSP baseline." |
| CE-vs-Plus | "Customer on pfSense Community Edition. Discuss Netgate Plus upgrade for commercial support." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Per-rule hit count | partial | pfSense webconfigurator |
| Snort / Suricata alert history | partial (if installed) | pfSense logs |
| pfBlockerNG block detail | partial (if installed) | pfSense logs |
| VPN tunnel up/down history | partial | pfSense logs + Netgate Cloud (Plus) |
| Netgate support-subscription status (Plus) | partial / external | Netgate Cloud |

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

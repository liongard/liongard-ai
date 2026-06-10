---
name: single-system-sonicwall
description: >
  Use this skill when the user wants a single-firewall analysis of a
  SonicWall (SonicOS 6 or SonicOS 7 / Gen7) — Periodic Business Review,
  firewall configuration audit, license expiration, firmware audit,
  security-services posture, DHCP scope review, site-to-site VPN policy
  review. Trigger phrases: "SonicWall PBR", "pull SonicWall data", "SW
  firewall review", "SonicWall Gen7 review", "SonicOS license audit",
  "SonicWall firmware audit". Produces an artifact in the format set in
  the customization block.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, soc, vcio-account-manager, technical-alignment-manager]
output_formats: [markdown, word, pptx]
primitives:
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
---

# Single-System Analysis — SonicWall

> **Inspector:** `sonicwall-inspector` (ID 7). Network category. Firewall.
> One inspector covers both **SonicOS 6** and **SonicOS 7 (Gen7)** —
> fields available depend on which OS version is detected at runtime.
>
> **References:** `reference/inspector-aliases.md` (SonicWall, SW,
> SonicOS, NSa, TZ). `reference/asset-fields.md` for asset cross-checks.
> `reference/qa-retry-pattern.md` for QA pass details.


---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-sonicwall-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  identity: "Firewall Identity & Firmware"
  interfaces: "Interface & DNS Configuration"
  security_services: "Security Services Posture"
  access_rules: "Firewall Access Rules"
  vpn: "Site-to-Site & SSL VPN"
  dhcp: "DHCP Scopes"
  local_users: "Local User & Admin Audit"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 1
  license_expiration_warn_days: 60
  firmware_age_months_max: 12
  default_local_users_max: 1   # any extra default-named local accounts = flag
  rdp_allowed_inbound: false   # WAN→LAN explicit allow-any rules = critical

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

- "Pull SonicWall data for the customer"
- "SonicWall PBR / quarterly review"
- "SonicWall Gen7 firmware audit"
- "Any SonicWall licenses expiring?"
- "SonicWall site-to-site VPN review"

Personas: NOC (operational state), SOC (firewall rules + SSL-VPN), vCIO/AM
(executive summary, license renewal), TAM (deep dive, version-specific
audit).

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| SonicWall system ID | Yes | `liongard_system LIST query="sonicwall"` — confirm via `SystemInfo.Hostname` |
| Reporting period | No | Default per customization |

---

## Locating the right system

```
liongard_system LIST searchMode=keyword query="sonicwall" environmentId=<ENV_ID>
```

`SystemInfo.Hostname` returns the firewall display name. If the customer has
multiple SonicWalls (multi-site), each shows as a separate Liongard system
— select by hostname or site naming convention.

> **Disambiguate from SonicWall Capture Client.** That's a separate
> inspector (`sonicwall-capture-client-inspector` ID 95) for the SonicWall
> EDR product, NOT the firewall. Confirm via the inspector slug if the
> initial keyword search returns both.


---

## Liongard data sources

> **Asset Inventory First, Metric Cross-Check.** The SonicWall per-system
> dataprint is the source of truth for *firewall configuration* — ports,
> rules, services, VPN, DHCP. The cross-inspector device inventory is the
> source of truth for *what's behind the firewall* — devices Liongard
> knows from RMM / OS inspectors / network discovery on the firewall's
> managed network.

### Per-vendor data — SonicWall dataprint top-level keys

| Key | Description |
|---|---|
| `SystemInfo` | Firewall identity — hostname, model, firmware, serial |
| `Interfaces` | Per-port interface configuration (X0, X1, etc.) with IPs and zones |
| `ManagementInterfaces` | Which interfaces allow management (WAN / HTTPS / SSH) |
| `SecurityServices` | License + status per service (Gateway AV, IPS, Anti-Spyware, Botnet) |
| `AccessRules` | Firewall access rule list (zone-to-zone) |
| `VpnPolicies` | Site-to-site VPN tunnels |
| `SslVpn` | SSL-VPN configuration (server, RADIUS, user portal) |
| `LocalUsers` | Local user accounts with role |
| `Zones` | Security zone definitions (LAN, WAN, DMZ) with per-zone service flags |
| `DhcpScopes` | DHCP scopes per VLAN (Gen7 reports more detail than OS 6) |

#### Field gotchas (inline notes — not TODO)

- **Two distinct dataprint schemas — always probe first.** The SonicWall
  inspector (ID 7) serves both SonicOS 6 and SonicOS 7 (Gen7). The two
  schemas are not compatible — many top-level keys and field names differ.
  Use a structural probe (`SystemInfo.Hostname` null = SonicOS 6 schema;
  non-null = Gen7 schema) before evaluating any path. Do NOT rely on the
  firmware version string alone: "SonicOS Enhanced 7.0.2" carries the
  SonicOS 6 dataprint schema. See the Step 0 divergence table in Metrics.
- **`SystemInfo.FirmwareVersion` exists in both schemas** and is safe to
  read before the structural probe. SonicOS 6 format: `6.5.x.x` or
  `SonicOS Enhanced 7.0.x`; Gen7 format: `SonicOS 7.x.x.x`.
- **`Interfaces.X0` is conventionally LAN, `X1` is WAN (Gen7 only).**
  On Gen7, `Interfaces` is a keyed object (`X0`, `X1`). On SonicOS 6,
  `Interfaces` is a flat array — key-based access returns null. Use
  `IPv4Settings.IpAddress` for LAN IP on SonicOS 6.
- **`Licenses[?DaysUntilExpiration < \`30\`]` null guard.** When
  `DaysUntilExpiration` is null on an individual license (common on SonicOS 6
  or when the API omits expiry data), the comparison throws a TypeError.
  Use `Licenses[?DaysUntilExpiration != null && DaysUntilExpiration < \`30\`]`
  to guard against null. Alternatively, rely on the catalog metric
  `metrics:sonicwall:licenses-expiring-30d-list` which handles this
  internally.

### Cross-inspector cross-check — device inventory

```
liongard_device LIST environmentId=<ENV_ID>
                     fields=["hostname","manufacturer","inspectors","internalIP"]
```

```
# Devices on the firewall's managed network
managed_devices = devices where category == "compute" AND inspectors does not contain "sonicwall-inspector"

# (the firewall itself shouldn't appear in compute devices, but if it
# does as a managed device, that's a misclassification flag)
```

---

## Metrics and queries

### Step 0 — Detect SonicOS schema generation first

The SonicWall inspector serves **both SonicOS 6 and SonicOS 7 (Gen7)** from a single
inspector ID (7). The two OS generations produce fundamentally different dataprint
schemas — many top-level keys and field names differ. Always determine the schema
generation before evaluating any path.

**Use a structural probe, not the version string.** The firmware version string is
unreliable: "SonicOS Enhanced 7.0.2-5065" carries the SonicOS 6 schema despite its
7.x version number. The authoritative indicator is whether `SystemInfo.Hostname`
resolves:

```
# Probe 1 — structural schema check (authoritative)
liongard_metric EVALUATE jmesPathQuery="SystemInfo.Hostname"
  systemId=<SYS_ID> environmentId=<ENV_ID>
```

| Result | Schema generation | Use path set |
|---|---|---|
| Non-null string | **Gen7 / SonicOS 7** — `SystemInfo.Hostname` exists | Gen7 paths (primary column below) |
| null | **SonicOS 6** — hostname is at `Administration.FirewallName` | SonicOS 6 fallback column below |

```
# Probe 2 — confirm firmware version for reporting
liongard_metric EVALUATE jmesPathQuery="SystemInfo.FirmwareVersion"
  systemId=<SYS_ID> environmentId=<ENV_ID>
```

Record the firmware version string for the Firmware Identity section regardless of
schema generation — the field exists in both (`SystemInfo.FirmwareVersion`).

### SonicOS 6 vs. Gen7 path divergence

The following fields **differ by OS schema** (VALIDATED 2026-05-27/28). Gen7 is the
primary path. For SonicOS 6, use the fallback column:

| Metric | Gen7 path (primary) | SonicOS 6 fallback | Notes |
|---|---|---|---|
| Hostname | `SystemInfo.Hostname` | `Administration.FirewallName` | Null on SonicOS 6; `Administration.FirewallName` VALIDATED |
| LAN IP (X0) | `Interfaces.X0.IPAddress` | `IPv4Settings.IpAddress` | Gen7: `Interfaces` is a keyed object (`X0`, `X1`); SonicOS 6: `Interfaces` is a flat array — key lookup returns null |
| Local users | `LocalUsers[*]` | `UsersLocal.users[*]` | SonicOS 6: `UsersLocal` is an object with sub-keys `users`, `groups`, `ApplyPasswordConstraints`, `PruneOnExpiry`; user list is at `.users[*]` |
| Site-to-site VPN | `VpnPolicies[*]` | `Vpn.Policies[*]` | SonicOS 6: `Vpn` is an object with sub-keys `Policies` and `Vpn`; S2S tunnels are at `Vpn.Policies[*]` |
| Security services | `SecurityServices` | `TSRStatus.SecurityServices` | Gen7 exposes top-level key; SonicOS 6 nests under `TSRStatus` |

> **Rule:** If a Gen7 path returns null after 2 retries, re-run the structural probe
> and switch to the SonicOS 6 fallback before labeling the field as a data gap.

### Identity & firmware

| Metric | JMESPath | Result shape |
|---|---|---|
| Hostname | `SystemInfo.Hostname` (Gen7) / `Administration.FirewallName` (SonicOS 6) | `<string>` |
| Model number | `SystemInfo.Model` | `<string>` |
| Firmware version | `SystemInfo.FirmwareVersion` | `<string>` |
| LAN management IP (X0) | `Interfaces.X0.IPAddress` (Gen7) / `IPv4Settings.IpAddress` (SonicOS 6) | `<string>` |
| Primary DNS | `DNSConfig.PrimaryDNS` | `<string>` |

### Local users / admin audit

| Metric | JMESPath | Result shape |
|---|---|---|
| Local users | `LocalUsers[*]` (Gen7) / `UsersLocal.users[*]` (SonicOS 6) | `<array>` |
| Management interfaces | `ManagementInterfaces` | `<array>` |

### VPN

| Metric | JMESPath | Result shape |
|---|---|---|
| Site-to-site VPN policies | `VpnPolicies[*]` (Gen7) / `Vpn.SiteToSite[*]` (SonicOS 6) | `<array>` |
| SSL-VPN RADIUS auth enabled | `SslVpn.SslVpnServer.UseRadius` | `<bool>` (compliant when `true`) |

### License expiration (null-guarded)

```jmespath
# Null-safe filter — DaysUntilExpiration can be null on SonicOS 6 or missing licenses
Licenses[?DaysUntilExpiration != null && DaysUntilExpiration < `30`].{
  service: ServiceName,
  daysLeft: DaysUntilExpiration,
  expiry: ExpirationDate
}
```

> Alternatively use catalog metric `metrics:sonicwall:licenses-expiring-30d-list`
> which handles the null guard internally.

### Time-series — license / firmware / device-count trend

```
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="SystemInfo.FirmwareVersion"

# Site-to-site VPN policy count over time (topology drift signal)
liongard_metric EVALUATE_TIME_SERIES
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
  startDate=<ISO timestamp> endDate=<ISO timestamp>
  jmesPathQuery="length(VpnPolicies)"
```

---

## QA & Manual Verification

Run the QA pass per `reference/qa-retry-pattern.md` before rendering output:

1. **Retry persistent nulls.** SonicWall fields commonly return null when
   the customer is on SonicOS 6 but the metric is Gen7-specific (or vice
   versa). After 2 retries, treat as a confirmed version-availability
   gap and flag in the manual-verification list.

2. **Flag stale inspector data.** SonicWall is API-driven; staleness
   usually indicates an API-key, scope, or HA-failover issue.
   `qa.flag_inspector_lastseen_threshold_days` defaults to **1 day** —
   tighter than library default.

3. **Cross-tool divergence (when applicable).** If running this recipe
   alongside an RMM recipe, compare the network-device list — devices on
   a SonicWall-managed network missing from RMM = unmanaged segment.

4. **Proposed-metric gaps for this recipe** — surface these in the
   manual-verification appendix:
   - Per-service license expiration detail (Gateway AV, IPS, Anti-Spyware, Botnet)
   - Secondary / Tertiary DNS configuration
   - DHCP scope detail (range, lease, DNS, reservations)
   - Per-zone Gateway AV / IPS / Anti-Spyware enablement
   - Gen7 cloud backup enabled flag
   - Wide-open WAN→LAN allow-any access rule list

5. **Manual Verification appendix** — render in the deliverable. Typical
   items for this recipe:
   - Persistent null on `SecurityServices` (verify in mysonicwall.com).
   - Local user accounts beyond the expected MSP / customer-admin pair.
   - Firmware older than `slas.firmware_age_months_max` (check release
     date in mysonicwall.com).

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Firmware behind | firmware release > `slas.firmware_age_months_max` months ago | "SonicWall on firmware <version> released <N> months ago — schedule maintenance for upgrade." |
| License expiring soon | per-service `daysToExpiry < slas.license_expiration_warn_days` | "<service> license expires in <N> days — initiate renewal." |
| Excess local users | `length(LocalUsers) > slas.default_local_users_max + expected_count` | "<N> local user accounts on the firewall — review and remove unused." |
| WAN management exposed | `ManagementInterfaces` contains WAN entries | "Firewall management is reachable from the WAN — confirm intentional or restrict to admin VLAN / VPN." |
| SSL-VPN no MFA | `SslVpn.SslVpnServer.UseRadius == false` AND SSL-VPN enabled | "SSL-VPN auth is single-factor — enforce RADIUS + MFA." |
| Wide-open WAN→LAN | Manual review of `AccessRules` — filter for allow-any source/dest on WAN→LAN rules | "**Critical:** wide-open WAN→LAN access rule detected — review and restrict." |
| Stale inspector | `lastSeen > 1 day` | "SonicWall inspector hasn't reported in <N> days — confirm API access." |


---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Traffic / bandwidth analytics | ❌ not in dataprint | SonicWall analytics or syslog → SIEM |
| Capture ATP / threat counts | ❌ not in dataprint | mysonicwall.com or Capture Security Center |
| Per-zone service enablement | ⚠️ not in dataprint — use aggregate `SecurityServices` + UI confirm | SonicWall UI |
| DHCP scope detail | ⚠️ not in dataprint | SonicWall UI |
| Per-service license expiration | ⚠️ not in dataprint — use aggregate `SecurityServices` | SonicWall UI |
| HA-pair config drift | ❌ not in dataprint | Manual compare via UI |


---

## Output format

Markdown / Word / PowerPoint per `output.format`. **pptx** for the
executive overview with a license-renewal countdown slide and a
firmware-age gauge.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_system LIST | query="sonicwall" envId=<ENV_ID> | array<system> | ok |
| 3 | liongard_metric EVALUATE | metricName or jmesPathQuery sysId=<SYS_ID> envId=<ENV_ID> | <integer>, <array>, <object> | ok per metric |
| 3a | liongard_metric EVALUATE | jmesPath "SystemInfo.Hostname" on SonicOS 6 system | null | VALIDATED BUG 2026-05-27: Use Administration.FirewallName on SonicOS 6 |
| 3b | liongard_metric EVALUATE | jmesPath "Interfaces.X0.IPAddress" on SonicOS 6 | null | VALIDATED BUG 2026-05-27: SonicOS 6 Interfaces is array not object; use IPv4Settings.IpAddress |
| 3c | liongard_metric EVALUATE | jmesPath "LocalUsers[*]" on SonicOS 6 | null | VALIDATED BUG 2026-05-28: Use UsersLocal.users[*] on SonicOS 6; UsersLocal has keys: users, groups, ApplyPasswordConstraints, PruneOnExpiry |
| 3d | liongard_metric EVALUATE | jmesPath "VpnPolicies[*]" on SonicOS 6 | null | VALIDATED BUG 2026-05-28: Use Vpn.Policies[*] on SonicOS 6 (confirmed returns empty array on system with no S2S VPN) |
| 4 | liongard_device LIST | envId=<ENV_ID> fields=[hostname,manufacturer,inspectors,internalIP] | array<device> | ok |
| 5 | (QA pass) retry persistent nulls | per `reference/qa-retry-pattern.md` | varies | ok |
```

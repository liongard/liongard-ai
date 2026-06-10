# NOC — Persona Index

The NOC (Network Operations Center) focuses on **operational state** —
keeping inspectors, agents, and managed devices healthy day-to-day. NOC
recipes surface failures, stale data, capacity issues, and patch / backup
gaps before they become customer-facing incidents.

## Audience framing

- **Tone:** technical. NOC consumers are operators reading dashboards;
  jargon is welcome. Show counts, hostnames, status icons (✅ / ⚠️ / ❌ /
  🔍).
- **Format:** Markdown or Excel for daily / weekly reports; PowerPoint
  rarely used unless escalating to leadership.
- **Default cadence:** daily health checks for production, weekly
  rollups, on-demand for incidents.

## SLA emphasis (NOC defaults)

| SLA | Default | Why NOC cares |
|---|---|---|
| `inspector_lastseen_days_max` | 1–7 days | Stale inspector = stale data; operational reports need fresh signal |
| `patch_age_days_max` | 30 days | Critical patches drive ticket volume + breach risk |
| `agent_uptodate_pct_min` | 95% | EDR / RMM agents drifting = posture gap |
| `failed_backups_max` | 0 | Any failed backup is a same-day escalation |
| `cloud_backup_max_age_hours` | 24 | Daily backup cadence is the contract |

## Common scenarios → recipes

| Scenario | Recipe |
|---|---|
| "Daily health check — anything failing across the customer base?" | `recipes/system-type-assessment/all-edrs.md`, `all-firewalls.md`, `all-backups.md`, `all-windows-patching.md` (run in sequence as a daily dashboard) |
| "Are all servers backed up?" | `recipes/system-type-assessment/all-backups.md` |
| "Pull SonicWall / FortiGate / ASA / Sophos / Meraki firewall state for <customer>" | `recipes/single-system-analysis/by-inspector/{sonicwall,fortinet-fortigate,cisco-asa,sophos-firewall,cisco-meraki}.md` |
| "Pull SentinelOne / Huntress / Sophos Central / Bitdefender / CrowdStrike / Webroot / ESET / SCC EDR data for <customer>" | `recipes/single-system-analysis/by-inspector/{sentinelone,huntress,sophos-central,bitdefender-gravityzone,crowdstrike,webroot,eset-licensing,sonicwall-capture-client}.md` |
| "Windows patching compliance across the fleet" | `recipes/system-type-assessment/all-windows-patching.md` |
| "Hypervisor capacity / VM density / datastore free space" | `recipes/system-type-assessment/all-hypervisors.md` |
| "Per-server deep dive (audit / decom / on-call investigation)" | `recipes/single-system-analysis/by-inspector/{windows-server,linux,macos,windows-workstation}.md` |
| "Cove / Datto BCDR / Acronis / Axcient / Veeam / SPX backup vendor deep dive" | `recipes/single-system-analysis/by-inspector/{cove-data-protection,datto-bcdr,acronis-cyber-protect-cloud,axcient-x360-recover,veeam-availability-console,veeam-service-provider-console,storagecraft-spx}.md` |
| "Cisco Umbrella / DNS-security deployment review" | `recipes/single-system-analysis/by-inspector/cisco-umbrella.md` |
| "M365 tenant operational state" | `recipes/single-system-analysis/by-inspector/microsoft-365.md` |
| "AD operational state — stale accounts, lockout policy, EOL workstations" | `recipes/single-system-analysis/by-inspector/active-directory.md` |
| "Domain expiration & DNS / DMARC health" | `recipes/system-type-assessment/all-domains.md` |
| "RMM agent / patch / alert posture across all RMMs" | `recipes/system-type-assessment/all-rmm-platforms.md` (rollup) + per-vendor `recipes/single-system-analysis/by-inspector/{ninjaone,datto-rmm,kaseya-vsa,n-able-n-central,connectwise-automate}.md` |
| "Per-RMM agent coverage / patch / alert deep dive" | Corresponding per-vendor RMM single |
| "Switch + router + AP posture across the network" | `recipes/system-type-assessment/all-network-infrastructure.md` (rollup) + per-vendor `recipes/single-system-analysis/by-inspector/{cisco-ios,cisco-sbs-switch,hp-procurve,junos,ubiquiti-unifi}.md` |
| "Per-switch / per-router / per-AP-controller deep dive" | Corresponding per-vendor network single |
| "Wireless security posture (SSID auth, guest isolation, AP firmware)" | `all-network-infrastructure.md` (wireless section) or `ubiquiti-unifi.md` / `cisco-meraki.md` per platform |

## Read across to other personas

- **SOC** — when an operational issue surfaces a security implication
  (e.g., default admin enabled, WAN management exposed), hand off to SOC.
- **TAM** — when an operational fix requires changing the customer's
  standard configuration, TAM owns the standard.
- **vCIO** — when a recurring operational issue points to a customer
  conversation (capacity, refresh, license renewal).

## What to customize first

1. **SLA thresholds** — your contracts dictate the actual cadence
   (`inspector_lastseen_days_max`, etc.).
2. **Daily dashboard composition** — pick the 3–4 recipes you'd run
   every morning and create a `daily-health-check.md` per customer that
   chains them.
3. **Escalation paths** — fill in your MSP's on-call / ticketing flow
   in each recipe's customization block.

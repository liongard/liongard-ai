# Future Recipes Roadmap

Inspector-by-inspector list of recipes the library should grow into, sourced from
a partner onboarding QA mapping (980 question→metric rows). Priority is approximate
— driven by the number of mapped fields in the partner audit and persona demand.

> **Read with `reference/onboarding-qa-coverage.md`** for the cross-EDR coverage
> matrix and `reference/inspector-aliases.md` for inspector lookup.

## Already shipped

| Recipe | Path | Status |
|---|---|---|
| SentinelOne single-system | `recipes/single-system-analysis/by-inspector/sentinelone.md` | ✅ |
| Huntress single-system | `recipes/single-system-analysis/by-inspector/huntress.md` | ✅ |
| Cisco Umbrella single-system | `recipes/single-system-analysis/by-inspector/cisco-umbrella.md` | ✅ |
| KnowBe4 single-system | `recipes/single-system-analysis/by-inspector/knowbe4.md` | ✅ |
| Microsoft 365 single-system | `recipes/single-system-analysis/by-inspector/microsoft-365.md` | ✅ |
| All-Windows-Patching system-type | `recipes/system-type-assessment/all-windows-patching.md` | ✅ |
| All-EDRs fleet rollup | `recipes/system-type-assessment/all-edrs.md` | ✅ |
| All-Endpoints fleet view | `recipes/system-type-assessment/all-endpoints.md` | ✅ |
| All-Servers (server-class only) | `recipes/system-type-assessment/all-servers.md` | ✅ |
| All-Hypervisors (ESXi + vCenter + Hyper-V) | `recipes/system-type-assessment/all-hypervisors.md` | ✅ |
| All-Domains (uses `liongard_domain` reconciled inventory) | `recipes/system-type-assessment/all-domains.md` | ✅ |
| EDR / Endpoint OS chunk (12 inspectors) | `recipes/single-system-analysis/by-inspector/{bitdefender-gravityzone, crowdstrike, eset-licensing, sonicwall-capture-client, sophos-central, webroot, windows-server, windows-workstation, linux, macos}.md` | ✅ |
| Networking chunk (Meraki + 4 firewalls + rollup) | `recipes/single-system-analysis/by-inspector/{cisco-meraki, sonicwall, fortinet-fortigate, cisco-asa, sophos-firewall}.md` + `recipes/system-type-assessment/all-firewalls.md` | ✅ |
| Active Directory single-system | `recipes/single-system-analysis/by-inspector/active-directory.md` | ✅ |
| All-Backups cross-inspector (server-OS × backup-vendor join) | `recipes/system-type-assessment/all-backups.md` | ✅ |
| Backup vendor singles (7 recipes) | `recipes/single-system-analysis/by-inspector/{cove-data-protection, axcient-x360-recover, datto-bcdr, acronis-cyber-protect-cloud, veeam-availability-console, veeam-service-provider-console, storagecraft-spx}.md` | ✅ |
| Cross-cutting MCP-signal foundation (skeleton update + cross-cutting-signals reference) | `templates/recipe-skeleton.md` + `reference/cross-cutting-signals.md` | ✅ |
| Environment Quarterly Lookback (flagship PBR / QBR) | `recipes/environment-quarterly-lookback/quarterly-business-review.md` | ✅ |
| Cyber Insurance master + 7 domains + Travelers carrier | `recipes/compliance/cyber-insurance/` | ✅ |
| Cyber Insurance carrier recipes (10 carriers) | `recipes/compliance/cyber-insurance/carriers/{aig,at-bay,beazley,chubb,coalition,corvus,cowbell,hartford,hiscox,tokio-marine-hcc}.md` | ✅ |
| New Customer Onboarding (point-in-time gap analysis) | `recipes/onboarding-assessment/new-customer-onboarding.md` | ✅ |
| Refresh & Lifecycle Roadmap (forward-looking calendar) | `recipes/roadmap-planning/refresh-and-lifecycle-roadmap.md` | ✅ |
| Pre-Sales Discovery (discovery / risk-opportunity framing) | `recipes/sales-assessment/pre-sales-discovery.md` | ✅ |
| CMMC Readiness (L1 / L2 / combined) | `recipes/compliance/cmmc/cmmc-readiness.md` | ✅ |
| External Attack Surface singles (4) + rollup — non-credentialed pre-sales flagship | `recipes/single-system-analysis/by-inspector/{internet-domain-dns, tls-ssl, network-ip-address, dark-web-monitoring}.md` + `recipes/system-type-assessment/all-external-attack-surface.md` | ✅ |
| Identity provider singles (3) + rollup | `recipes/single-system-analysis/by-inspector/{duo-security, jumpcloud, onelogin}.md` + `recipes/system-type-assessment/all-identity-providers.md` | ✅ |
| RMM platform singles (5) + rollup | `recipes/single-system-analysis/by-inspector/{ninjaone, datto-rmm, kaseya-vsa, n-able-n-central, connectwise-automate}.md` + `recipes/system-type-assessment/all-rmm-platforms.md` | ✅ |
| PSA platform singles (5) + rollup | `recipes/single-system-analysis/by-inspector/{connectwise-manage, autotask, halopsa, kaseya-bms, syncro}.md` + `recipes/system-type-assessment/all-psa-platforms.md` | ✅ |
| Documentation (IT Glue single) | `recipes/single-system-analysis/by-inspector/itglue.md` | ✅ |
| Cloud-storage singles (3) + rollup | `recipes/single-system-analysis/by-inspector/{box, dropbox, google-drive}.md` + `recipes/system-type-assessment/all-cloud-storage.md` | ✅ |
| MSP-wide config + sweep migration of 57 recipes | `config/msp-config.yaml` + `config/msp-config.local.yaml.example` + `config/README.md` | ✅ |
| Firewall family completion (5 additional singles + rollup extension) | `recipes/single-system-analysis/by-inspector/{watchguard, palo-alto-panos, barracuda-firewall, pfsense, sophos-sg}.md` + extended `all-firewalls.md` | ✅ |
| Network-infrastructure chunk (5 singles + new rollup) | `recipes/single-system-analysis/by-inspector/{cisco-ios, cisco-sbs-switch, hp-procurve, junos, ubiquiti-unifi}.md` + `recipes/system-type-assessment/all-network-infrastructure.md` | ✅ |
| Cloud-infrastructure + Workspace identity chunk (4 singles + 2 rollup extensions) | `recipes/single-system-analysis/by-inspector/{aws, azure, cloudflare, google-workspace}.md` + extensions to `all-identity-providers.md` (GWS chained) + `all-external-attack-surface.md` (Cloudflare chained) | ✅ |
| macOS MDM / health monitoring (2 singles) | `recipes/single-system-analysis/by-inspector/{addigy, watchman-monitoring}.md` | ✅ |
| Storage / NAS (Synology) | `recipes/single-system-analysis/by-inspector/synology-nas.md` | ✅ |
| Network monitoring singles + rollup (4 singles) | `recipes/single-system-analysis/by-inspector/{network-discovery, auvik, domotz, datto-networking}.md` + `recipes/system-type-assessment/all-network-monitoring.md` | ✅ |
| Miscellaneous singles (Managed Printer, Slack, GoDaddy) | `recipes/single-system-analysis/by-inspector/{managed-printer, slack, godaddy}.md` | ✅ |
| HIPAA Security Rule readiness | `recipes/compliance/hipaa/hipaa-readiness.md` | ✅ |
| FTC Safeguards Rule readiness | `recipes/compliance/ftc-safeguards/ftc-safeguards-readiness.md` | ✅ |

## EDR / Endpoint OS

| Recipe | Inspector | Mapped fields | Notes |
|---|---|---|---|
| Bitdefender GravityZone | `bitdefender-gravityzone-inspector` (57) | 10 | Use existing metrics 133, 134, 135, 137, 1072 |
| CrowdStrike Falcon | `crowdstrike-inspector` (102) | 10 | Beta inspector — partner flagged many [PROPOSED] metrics; surface gaps |
| ESET Licensing | `eset-licensing-inspector` (69) | 10 | License-only — recipe must explicitly disclaim endpoint posture |
| SonicWall Capture Client | `sonicwall-capture-client-inspector` (95) | (in EDR set) | Use existing 2147, 2150, 2154 |
| Sophos Central | `sophos-central-inspector` (65) | 10 | Strong server/workstation split; existing 402 + several |
| Webroot | `webroot-inspector` (15) | 10 | Existing 126, 835, 84… |
| Linux | `linux-inspector` (53) | 22 | Hostname/IP/sudo/AV; existing 188, 250 |
| macOS | `macos-inspector` (96) | 14 | Existing 2102, 2105, 2114, 2120, 2122, 2126, 2129 |
| Windows Server | `windows-server-inspector` (25) | 22 | Most-mapped OS — many existing metrics |
| Windows Workstation | `windows-workstation-inspector` (90) | (cross-referenced in patching recipe) | Many existing metrics |

Cross-system rollups to add alongside:
- `recipes/system-type-assessment/all-edrs.md` — unified EDR posture across all six EDRs
- `recipes/system-type-assessment/all-endpoints.md` — Windows Server + Workstation + macOS + Linux combined endpoint posture

## Firewalls

| Recipe | Inspector | Mapped fields | Notes |
|---|---|---|---|
| Cisco Meraki single-system | `cisco-meraki-inspector` (3) | **40 fields** — largest network mapping | ✅ |
| SonicWall (SonicOS 6 + Gen7) | `sonicwall-inspector` (7) | 18 | ✅ |
| Sophos Firewall (XG/XGS) | `sophos-firewall-inspector` (28) | 17 | ✅ |
| Fortinet FortiGate | `fortinet-fortigate-inspector` (33) | 12 | ✅ |
| Cisco ASA | `cisco-asa-inspector` (22) | 12 | ✅ |
| WatchGuard | `watchguard-inspector` (29) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/watchguard.md` |
| Palo Alto PAN-OS | `palo-alto-panos-inspector` (49, Beta) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/palo-alto-panos.md` |
| Barracuda Firewall | `barracuda-firewall-inspector` (52) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/barracuda-firewall.md` |
| pfSense | `pfsense-inspector` (37) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/pfsense.md` |
| Sophos SG (legacy UTM) | `sophos-sg-inspector` (43) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/sophos-sg.md` |
| **All Firewalls rollup** | (composite — covers all 10 above) | n/a | ✅ — `recipes/system-type-assessment/all-firewalls.md` |

## Hypervisors

| Recipe | Inspector | Mapped fields | Notes |
|---|---|---|---|
| VMware ESXi single-system | `vmware-esxi-inspector` (59) | 24 | Existing 268, 270, 277, 279, 282; datastore/VIB count [PROPOSED] |
| Hyper-V single-system | `hyper-v-inspector` (39) | 6 | All existing metrics: 196, 198, 199, 201… |
| VMware vCenter (Beta) | `vmware-vcenter-inspector` (58) | (not in partner audit — but related) | Build alongside ESXi |

Plus `recipes/system-type-assessment/all-hypervisors.md`.

## Identity / directory recipes

| Recipe | Inspector | Mapped fields | Status |
|---|---|---|---|
| Active Directory single-system | `active-directory-inspector` (13) | 25 | ✅ |
| Microsoft 365 single-system | `microsoft-365-inspector` (8) | (separate; covers Entra ID) | ✅ |
| JumpCloud single-system | `jumpcloud-inspector` (68) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/jumpcloud.md` |
| Duo Security single-system | `duo-security-inspector` (47) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/duo-security.md` |
| OneLogin single-system | `onelogin-inspector` (27) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/onelogin.md` |
| **All Identity Providers rollup** | (composite) | n/a | ✅ — `recipes/system-type-assessment/all-identity-providers.md` |

## Domain / DNS / certificates / external attack surface

| Recipe | Inspector | Mapped fields | Status |
|---|---|---|---|
| Internet Domain / DNS single-system | `internet-domain-dns-inspector` (2) | 23 | ✅ — `recipes/single-system-analysis/by-inspector/internet-domain-dns.md` |
| TLS / SSL Certificates single-system | `tls-ssl-inspector` (16) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/tls-ssl.md` |
| Network IP Address single-system | `network-ip-inspector` (4) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/network-ip-address.md` |
| Dark Web Monitoring single-system | `dark-web-inspector` (4) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/dark-web-monitoring.md` |
| **External Attack Surface rollup** (all 4 above + identity cross-reference) | (composite) | n/a | ✅ — `recipes/system-type-assessment/all-external-attack-surface.md` — **flagship pre-sales recipe** |
| Cloudflare single-system | `cloudflare-inspector` (82) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/cloudflare.md` (chained from `all-external-attack-surface.md` rollup) |
| GoDaddy | `godaddy-inspector` (23, beta) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/godaddy.md` — beta inspector; all arrays SCHEMA_CONFIRMED only (empty in test account) |

## Cloud infrastructure (subscription / IaaS / SaaS-platform)

| Recipe | Inspector | Mapped fields | Status |
|---|---|---|---|
| AWS single-system | `aws-inspector` (1) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/aws.md` |
| Microsoft Azure single-system | `azure-inspector` (11) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/azure.md` |
| Google Workspace single-system | `google-workspace-inspector` (61) | 3 | ✅ — `recipes/single-system-analysis/by-inspector/google-workspace.md` (chained from `all-identity-providers.md`) |
| Cloudflare single-system | `cloudflare-inspector` (82) | (not in partner audit) | ✅ — see Domain / DNS section above |
| **All Cloud Infrastructure rollup** | (composite — AWS + Azure + GWS, cross-account / cross-subscription) | n/a | ✅ — `recipes/system-type-assessment/all-cloud-infrastructure.md` — chains aws.md, azure.md, google-workspace.md. Cloudflare not included (covered in `all-external-attack-surface.md`). |

## Backup / DR

| Recipe | Inspector | Mapped fields | Status |
|---|---|---|---|
| Datto BCDR single-system | `datto-bcdr-inspector` (38) | (in cross-inspector backup mapping) | ✅ — `recipes/single-system-analysis/by-inspector/datto-bcdr.md` |
| Cove Data Protection single-system | `cove-data-protection-inspector` (76) | (cyber-insurance backup.md covers metrics) | ✅ — `recipes/single-system-analysis/by-inspector/cove-data-protection.md` |
| Acronis Cyber Protect Cloud single-system | `acronis-cyber-protect-cloud-inspector` (93) | 22 join fields | ✅ — `recipes/single-system-analysis/by-inspector/acronis-cyber-protect-cloud.md` |
| Axcient x360 Recover | `axcient-x360-recover-inspector` (100) | (in cross-inspector mapping) | ✅ — `recipes/single-system-analysis/by-inspector/axcient-x360-recover.md` |
| Veeam Availability Console | `veeam-availability-console-inspector` (35) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/veeam-availability-console.md` |
| Veeam Service Provider Console | `veeam-service-provider-console-inspector` (75) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/veeam-service-provider-console.md` |
| StorageCraft SPX | `storagecraft-spx-inspector` (46) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/storagecraft-spx.md` |
| **All Backups rollup** | (composite — server × backup vendor join) | n/a | ✅ — `recipes/system-type-assessment/all-backups.md` |

## RMM / PSA

| Recipe | Inspector | Mapped fields | Status |
|---|---|---|---|
| ConnectWise Automate single-system | `connectwise-automate-inspector` (36) | (used in patching recipe) | ✅ — `recipes/single-system-analysis/by-inspector/connectwise-automate.md` |
| NinjaOne single-system | `ninjaone-inspector` (72) | (used in cyber-insurance) | ✅ — `recipes/single-system-analysis/by-inspector/ninjaone.md` |
| N-able N-Central single-system | `n-able-n-central-inspector` (71) | (referenced) | ✅ — `recipes/single-system-analysis/by-inspector/n-able-n-central.md` |
| Kaseya VSA single-system | `kaseya-vsa-inspector` (48) | (referenced) | ✅ — `recipes/single-system-analysis/by-inspector/kaseya-vsa.md` |
| Datto RMM single-system | `datto-rmm-inspector` (73) | (referenced) | ✅ — `recipes/single-system-analysis/by-inspector/datto-rmm.md` |
| **All RMM Platforms rollup** | (composite) | n/a | ✅ — `recipes/system-type-assessment/all-rmm-platforms.md` |
| Syncro single-system (PSA + RMM hybrid) | `syncro-inspector` (86) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/syncro.md` |
| N-able RMM single-system | `nable-rmm-inspector` (87) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/nable-rmm.md` |
| ConnectWise Asio single-system | `connectwise-asio-inspector` (103) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/connectwise-asio.md` |
| Continuum RMM single-system (legacy/EOL) | `continuum-rmm-inspector` (60) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/continuum-rmm.md` |
| ConnectWise Manage single-system (PSA) | `connectwise-manage-inspector` (9) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/connectwise-manage.md` |
| Autotask single-system (PSA) | `autotask-inspector` (45) | (PSA) | ✅ — `recipes/single-system-analysis/by-inspector/autotask.md` |
| HaloPSA single-system | `halopsa-inspector` (94) | (PSA) | ✅ — `recipes/single-system-analysis/by-inspector/halopsa.md` |
| Kaseya BMS single-system (PSA) | `kaseya-bms-inspector` (83) | (PSA) | ✅ — `recipes/single-system-analysis/by-inspector/kaseya-bms.md` |
| **All PSA Platforms rollup** | (composite) | n/a | ✅ — `recipes/system-type-assessment/all-psa-platforms.md` |

## macOS MDM / Health Monitoring

| Recipe | Inspector | Mapped fields | Status |
|---|---|---|---|
| Addigy macOS MDM | `addigy-inspector-v2` (98) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/addigy.md` |
| Watchman Monitoring | `watchman-monitoring-inspector` (50) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/watchman-monitoring.md` |

## Storage / NAS

| Recipe | Inspector | Mapped fields | Notes |
|---|---|---|---|
| Synology NAS | `synology-nas-inspector` (64) | 8 | ✅ — `recipes/single-system-analysis/by-inspector/synology-nas.md` — VALIDATED against System A (inspected 2025-05-01) |

## Network infrastructure (switches / routers / wireless)

| Recipe | Inspector | Mapped fields | Status |
|---|---|---|---|
| Cisco IOS / IOS-XE | `cisco-ios-inspector` (30) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/cisco-ios.md` |
| Cisco SBS Switch | `cisco-sbs-switch-inspector` (78) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/cisco-sbs-switch.md` |
| HP ProCurve / Aruba | `hp-procurve-inspector` (63) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/hp-procurve.md` |
| Junos (Juniper) | `junos-inspector` (42, Beta) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/junos.md` |
| Ubiquiti UniFi | `ubiquiti-unifi-inspector` (40) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/ubiquiti-unifi.md` |
| **All Network Infrastructure rollup** | (composite — chains 5 above + Meraki MS/MR portion) | n/a | ✅ — `recipes/system-type-assessment/all-network-infrastructure.md` |

## Network monitoring / discovery

| Recipe | Inspector | Mapped fields | Status |
|---|---|---|---|
| Network Discovery | `autodiscovery-inspector` (41) | 13 | ✅ — `recipes/single-system-analysis/by-inspector/network-discovery.md` |
| Auvik | `auvik-inspector` (62) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/auvik.md` |
| Domotz | `domotz-inspector` (88) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/domotz.md` |
| Datto Networking | `datto-networking-inspector` (79) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/datto-networking.md` |
| **All Network Monitoring rollup** | (composite — chains 4 above) | n/a | ✅ — `recipes/system-type-assessment/all-network-monitoring.md` |

## Cloud storage

| Recipe | Inspector | Mapped fields | Status |
|---|---|---|---|
| Box single-system | `box-com-inspector` (14) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/box.md` |
| Dropbox single-system | `dropbox-inspector` (34) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/dropbox.md` |
| Google Drive single-system | `google-drive-inspector` (80) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/google-drive.md` |
| **All Cloud Storage rollup** | (composite, includes OneDrive via M365) | n/a | ✅ — `recipes/system-type-assessment/all-cloud-storage.md` |

## Documentation

| Recipe | Inspector | Mapped fields | Status |
|---|---|---|---|
| IT Glue single-system | `itglue-inspector` (26) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/itglue.md` |

## Other (single-mapped or low-priority)

| Recipe | Inspector | Mapped fields | Notes |
|---|---|---|---|
| Managed Printer | `managed-printer-inspector` (89, beta) | 12 | ✅ — `recipes/single-system-analysis/by-inspector/managed-printer.md` — VALIDATED (System A, 2025-05-12). Key gotchas: `SystemInfo.Address` returns loopback; use `ifTable[?ipAdEntAddr != '127.0.0.1']` for real IP; `prtAlertSeverityLevel` is STRING; `prtInputCurrentLevel` may be `"Unknown"` string. |
| Slack | `slack-inspector` (66) | (not in partner audit) | ✅ — `recipes/single-system-analysis/by-inspector/slack.md` — SCHEMA_CONFIRMED (System A, 2025-08-20). Key gotchas: `has_2fa` is BOOLEAN; filter for `deleted == \`false\` && is_bot == \`false\`` for accurate active-user 2FA posture. |

## Compliance / persona-driven recipes

These are not single-inspector recipes — they consume the per-inspector recipes
above plus the asset inventory:

| Recipe | Path | Status |
|---|---|---|
| Cyber insurance readiness | `recipes/compliance/cyber-insurance/cyber-insurance-readiness.md` | ✅ |
| CMMC compliance evidence | `recipes/compliance/cmmc/cmmc-readiness.md` | ✅ |
| HIPAA evidence | `recipes/compliance/hipaa/hipaa-readiness.md` | ✅ — maps HIPAA Security Rule (45 CFR Part 164) technical + administrative safeguards to Liongard data; two output modes (Word narrative + Excel evidence workbook) |
| FTC Safeguards Rule | `recipes/compliance/ftc-safeguards/ftc-safeguards-readiness.md` | ✅ — maps 9 WISP elements under 16 CFR Part 314; TAM technical checklist + vCIO executive summary output modes; small-company-exempt flag |
| Quarterly Business Review (full env) | `recipes/environment-quarterly-lookback/quarterly-business-review.md` | ✅ |
| Roadmap planning (EOL / warranty) | `recipes/roadmap-planning/refresh-and-lifecycle-roadmap.md` | ✅ |
| Sales discovery | `recipes/sales-assessment/pre-sales-discovery.md` | ✅ |
| Onboarding assessment | `recipes/onboarding-assessment/new-customer-onboarding.md` | ✅ |

## "Metric request" backlog

The partner audit identified many **proposed metrics** that don't yet exist in
the Liongard library. These should be filed as metric requests via the
`liongard-metrics` skill:

- AD: DHCP scope details (names, ranges, lease duration, DNS servers, reservations)
- AD: account password policy domain name (separate from policy values)
- M365: license expiration date per SKU
- M365: Global Admin user list (separate from generic privileged)
- M365: directory sync enabled status (boolean)
- M365: directory sync last sync time (timestamp)
- M365: active member user count (vs. all enabled, including guests/service)
- SentinelOne: total agents (vs. count derived from Agents[])
- SentinelOne: server-only agent counts split by activity
- CrowdStrike: total enrolled, active sensor, server breakdown, total detections
- Sophos Central: server/workstation breakdown by activity
- Webroot: site name, deactivated count
- Cisco Meraki: switch IP addresses, AP IP addresses, VLAN DHCP summary
- All firewalls: WAN-to-LAN access rule list, site-to-site VPN policies
- VMware ESXi: low datastore free space, installed VIB count
- Internet Domain/DNS: SPF authorized senders, DKIM record domains, per-record check failures

These represent a meaningful expansion of the metrics library — **track
separately and prioritize based on which recipes are most-used.**

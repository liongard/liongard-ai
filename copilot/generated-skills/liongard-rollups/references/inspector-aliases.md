# Inspector Aliases — Centralized Lookup

Canonical reference for translating user vocabulary into the right Liongard inspector
and the right `liongard_system LIST query=` keyword. The library uses this file as
the single source of truth — recipes link here instead of redefining their own
keyword tables.

> **Authoritative source for the underlying mapping:**
> `reference/inspector-name-system-id-mapping.xlsx`. This file adds the user-facing
> aliases (vendor abbreviations, product-family alternatives, parent-company names)
> that the spreadsheet doesn't capture but agents need to recognize.

## How to use this file

1. **Translate the user's phrasing.** Find what they said in the alphabetical
   index. The matching row gives you the canonical inspector name and the API
   keyword.
2. **Run the system search.** `liongard_system LIST searchMode=keyword query="<API keyword>" environmentId=<ENV_ID>`.
3. **Confirm the system.** For inspectors with parent/child models (SentinelOne,
   Cisco Umbrella, Datto BCDR, Acronis, Veeam, Axcient), confirm you targeted the
   child system before evaluating metrics — see the per-inspector notes below.

---

## Common gotchas to avoid

- **"Azure AD" / "Entra ID" / "AAD" → use the `microsoft-365-inspector`, not the
  `azure-inspector`.** The M365 inspector pulls Entra/Azure AD identity data; the
  Azure inspector covers Azure subscription resources (NSGs, EBS, IAM credential
  reports). When a user says "Azure", clarify whether they mean identity or
  subscription resources.
- **"NinjaRMM" → it's now `ninjaone-inspector`.** NinjaRMM was renamed NinjaOne in
  2022. Older recipes and docs say "NinjaRMM"; the inspector slug uses "ninjaone".
- **"G Suite" / "Google Apps" → it's `google-workspace-inspector`.** G Suite was
  renamed to Google Workspace in 2020.
- **"LabTech" → it's `connectwise-automate-inspector`.** Renamed when ConnectWise
  acquired LabTech.
- **"Centrastage" / "Autotask Endpoint Management" → it's `datto-rmm-inspector`.**
- **"Cove" → formerly SolarWinds Backup, now N-able Cove Data Protection.**
- **Sophos has THREE inspectors:** `sophos-central-inspector` (endpoint EDR),
  `sophos-firewall-inspector` (XG/XGS firewall), `sophos-sg-inspector` (legacy SG
  firewall). When a user says "Sophos", confirm which.
- **Cisco has FOUR network inspectors plus Umbrella + Duo:** `cisco-asa-inspector`
  (firewall), `cisco-ios-inspector` (routers/switches), `cisco-meraki-inspector`
  (Meraki cloud), `cisco-sbs-switch-inspector` (small-business switches),
  `cisco-umbrella-inspector` (DNS security), `duo-security-inspector` (MFA).
- **Veeam has TWO inspectors:** `veeam-availability-console-inspector` (VAC) and
  `veeam-service-provider-console-inspector` (VSPC). Confirm which platform.
- **`active-directory-inspector` is categorized "Apps & Services" in the mapping
  xlsx but its target is "Directory Service".** Don't be confused by the category
  label — it's the on-prem AD inspector.

---

## Alphabetical alias index

Quick lookup. Match the user's phrasing in the **Alias** column; use the **API
keyword** in your `liongard_system LIST query=` call.

| Alias / shorthand | Canonical inspector | API keyword |
|---|---|---|
| 3CX | 3CX | `"3cx"` |
| AAD | Microsoft 365 (Entra ID is part of the M365 inspector) | `"microsoft-365"` |
| Acronis | Acronis Cyber Protect Cloud | `"acronis"` |
| ACP | Acronis Cyber Protect Cloud | `"acronis"` |
| AD | Active Directory | `"active-directory"` |
| AD DS | Active Directory | `"active-directory"` |
| ADDS | Active Directory | `"active-directory"` |
| Addigy | Addigy | `"addigy"` |
| Air (BitLyft Air) | BitLyft Air | `"bitlyft"` |
| Amazon | Amazon Web Services | `"aws"` |
| Asio | ConnectWise Asio | `"connectwise-asio"` |
| ASA | Cisco ASA | `"cisco-asa"` |
| AT | Autotask | `"autotask"` |
| Autodiscovery | Network Discovery | `"autodiscovery"` |
| Autotask | Autotask | `"autotask"` |
| Auvik | Auvik | `"auvik"` |
| AWS | Amazon Web Services | `"aws"` |
| Axcient | Axcient x360 Recover | `"axcient"` |
| Azure | Microsoft Azure (subscription resources) | `"azure"` |
| Azure AD | Microsoft 365 (Entra ID is part of the M365 inspector) | `"microsoft-365"` |
| Barracuda | Barracuda Firewall | `"barracuda"` |
| BCDR | Datto BCDR | `"datto-bcdr"` |
| BD / BDGZ | Bitdefender GravityZone | `"bitdefender"` |
| Bitdefender | Bitdefender GravityZone | `"bitdefender"` |
| BitLyft | BitLyft Air | `"bitlyft"` |
| BMS | Kaseya BMS | `"kaseya-bms"` |
| Box / Box.com | Box | `"box"` |
| Capture Client | SonicWall Capture Client | `"sonicwall-capture-client"` |
| Centrastage (legacy) | Datto RMM | `"datto-rmm"` |
| Cisco ASA | Cisco ASA | `"cisco-asa"` |
| Cisco IOS | Cisco IOS | `"cisco-ios"` |
| Cisco Meraki | Cisco Meraki | `"meraki"` |
| Cisco SBS | Cisco Small Business Switch | `"cisco-sbs"` |
| Cisco Umbrella | Cisco Umbrella | `"umbrella"` |
| Cloudflare | Cloudflare | `"cloudflare"` |
| Continuum | Continuum RMM | `"continuum"` |
| ConnectWise Asio | ConnectWise Asio | `"connectwise-asio"` |
| ConnectWise Automate | ConnectWise Automate | `"connectwise-automate"` |
| ConnectWise Manage | ConnectWise Manage | `"connectwise-manage"` |
| Cove | Cove Data Protection | `"cove"` |
| CrowdStrike | CrowdStrike | `"crowdstrike"` |
| CS / CSF | CrowdStrike | `"crowdstrike"` |
| CW Asio | ConnectWise Asio | `"connectwise-asio"` |
| CW Automate / CWA | ConnectWise Automate | `"connectwise-automate"` |
| CW Manage / CWM | ConnectWise Manage | `"connectwise-manage"` |
| Dark Web | Dark Web Monitoring | `"dark-web"` |
| Datto BCDR | Datto BCDR | `"datto-bcdr"` |
| Datto Networking | Datto Networking | `"datto-network"` |
| Datto RMM | Datto RMM | `"datto-rmm"` |
| DC (domain controller) | Active Directory | `"active-directory"` |
| Domain (DNS/WHOIS) | Internet Domain / DNS | `"internet-domain"` |
| Domotz | Domotz | `"domotz"` |
| Dropbox | Dropbox | `"dropbox"` |
| Duo / Duo Security / Cisco Duo | Duo Security | `"duo"` |
| EnGenius | EnGenius Cloud | `"engenius"` |
| Entra / Entra ID | Microsoft 365 (Entra ID is part of the M365 inspector) | `"microsoft-365"` |
| ESET | ESET Licensing | `"eset"` |
| ESXi | VMware ESXi | `"esxi"` |
| Falcon | CrowdStrike | `"crowdstrike"` |
| FGT | Fortinet FortiGate | `"fortinet"` |
| Fortinet / FortiGate / Forti | Fortinet FortiGate | `"fortinet"` |
| GDrive / Google Drive | Google Drive | `"google-drive"` |
| GoDaddy | GoDaddy | `"godaddy"` |
| Google Apps (legacy) | Google Workspace | `"google-workspace"` |
| Google Workspace / GWS | Google Workspace | `"google-workspace"` |
| GravityZone / GZ | Bitdefender GravityZone | `"bitdefender"` |
| G Suite (legacy) | Google Workspace | `"google-workspace"` |
| Halo / HaloPSA | HaloPSA | `"halo"` |
| HP ProCurve / HPE Aruba | HP ProCurve | `"procurve"` |
| Huntress / Huntress Labs | Huntress | `"huntress"` |
| Hyper-V / HyperV | Hyper-V | `"hyper-v"` |
| Intercept X | Sophos Central | `"sophos-central"` |
| ITG / IT Glue | IT Glue | `"itglue"` |
| JC | JumpCloud | `"jumpcloud"` |
| JumpCloud | JumpCloud | `"jumpcloud"` |
| Junos / Juniper | Junos | `"junos"` |
| Kaseya | Kaseya VSA | `"kaseya-vsa"` |
| Kaseya BMS | Kaseya BMS | `"kaseya-bms"` |
| Kaseya VSA / VSA | Kaseya VSA | `"kaseya-vsa"` |
| KB4 / KnowBe4 | KnowBe4 | `"knowbe4"` |
| LabTech (legacy) | ConnectWise Automate | `"connectwise-automate"` |
| Linux | Linux | `"linux"` |
| M365 / Microsoft 365 | Microsoft 365 | `"microsoft-365"` |
| Mac / macOS / OSX | macOS | `"macos"` |
| Manage (PSA) | ConnectWise Manage | `"connectwise-manage"` |
| Managed Print / Printer | Managed Printer | `"printer"` |
| Meraki / MX / MS / MR | Cisco Meraki | `"meraki"` |
| Microsoft Azure | Microsoft Azure | `"azure"` |
| MSSQL / MS SQL | SQL Server | `"sql-server"` |
| N-able N-Central / N-central / NC | N-able N-Central | `"n-central"` |
| N-able RMM | N-able RMM | `"n-able-rmm"` |
| Netgate | pfSense | `"pfsense"` |
| Network IP | Network IP Address | `"network-ip"` |
| Ninja / NinjaOne / NinjaRMM (legacy) | NinjaOne | `"ninjaone"` |
| O365 / Office 365 | Microsoft 365 | `"microsoft-365"` |
| OL / OneLogin | OneLogin | `"onelogin"` |
| OpenDNS (legacy) | Cisco Umbrella | `"umbrella"` |
| OSX | macOS | `"macos"` |
| PA / Palo Alto / PAN-OS / Panorama | Palo Alto PAN-OS | `"palo-alto"` |
| pfSense | pfSense | `"pfsense"` |
| ProCurve | HP ProCurve | `"procurve"` |
| RepairShopr (legacy) | Syncro | `"syncro"` |
| S1 / SentinelOne / Singularity | SentinelOne | `"sentinelone"` |
| SBS (Cisco) | Cisco Small Business Switch | `"cisco-sbs"` |
| SCC | SonicWall Capture Client | `"sonicwall-capture-client"` |
| Server (Windows) | Windows Server | `"windows-server"` |
| ShadowProtect | StorageCraft SPX | `"storagecraft"` |
| SIRIS | Datto BCDR | `"datto-bcdr"` |
| Slack | Slack | `"slack"` |
| SolarWinds Backup (legacy) | Cove Data Protection | `"cove"` |
| SolarWinds N-central (legacy) | N-able N-Central | `"n-central"` |
| SolarWinds RMM (legacy) | N-able RMM | `"n-able-rmm"` |
| SonicOS | SonicWall | `"sonicwall"` |
| SonicWall / SW | SonicWall | `"sonicwall"` |
| SonicWall Capture Client | SonicWall Capture Client | `"sonicwall-capture-client"` |
| SonicWall NSa / TZ | SonicWall | `"sonicwall"` |
| Sophos Central / Sophos Endpoint | Sophos Central | `"sophos-central"` |
| Sophos Firewall / Sophos XG / XGS | Sophos Firewall | `"sophos-firewall"` |
| Sophos SG (legacy) | Sophos SG | `"sophos-sg"` |
| SPX (StorageCraft) | StorageCraft SPX | `"storagecraft"` |
| SQL Server | SQL Server | `"sql-server"` |
| Synology / DSM | Synology NAS | `"synology"` |
| Syncro / Syncro PSA / Syncro MSP | Syncro | `"syncro"` |
| TLS / SSL / Cert | TLS/SSL Certificates | `"tls"` |
| Ubiquiti / UDM / UniFi | Ubiquiti UniFi | `"unifi"` |
| Umbrella | Cisco Umbrella | `"umbrella"` |
| VAC | Veeam Availability Console | `"veeam"` |
| Vade / Vade Secure | Vade | `"vade"` |
| vCenter / vSphere | VMware vCenter | `"vcenter"` |
| Veeam Availability Console | Veeam Availability Console | `"veeam"` |
| Veeam Service Provider Console / VSPC | Veeam Service Provider Console | `"veeam-spc"` |
| VMware (ESXi) | VMware ESXi | `"esxi"` |
| VMware (vCenter) | VMware vCenter | `"vcenter"` |
| Watchman / Watchman Monitoring | Watchman Monitoring | `"watchman"` |
| WatchGuard / WG | WatchGuard | `"watchguard"` |
| Webroot / WSA / SecureAnywhere | Webroot SecureAnywhere GSM | `"webroot"` |
| WHOIS | Internet Domain / DNS | `"internet-domain"` |
| Windows Server / WinSrv | Windows Server | `"windows-server"` |
| Windows Workstation / WS | Windows Workstation | `"windows-workstation"` |
| x360 / x360 Recover | Axcient x360 Recover | `"axcient"` |
| XG / XGS (Sophos) | Sophos Firewall | `"sophos-firewall"` |

---

## Full inspector reference by category

### Apps & Services

| Inspector | ID | Display name | Common aliases | Notes |
|---|---|---|---|---|
| `active-directory-inspector` | 13 | Active Directory | AD, ADDS, AD DS, DC, on-prem AD | On-prem only — Entra ID is via M365 inspector. |
| `addigy-inspector` | 51 | Addigy | Addigy MDM | macOS MDM. |
| `autotask-inspector` | 45 | Autotask | AT, Datto Autotask, Autotask PSA | Datto-owned PSA. |
| `bitlyft-inspector` | — | BitLyft Air | BitLyft, Air | SOAR platform. |
| `bitdefender-gravityzone-inspector` | 57 | Bitdefender GravityZone | BD, BDGZ, GravityZone, GZ | EDR/AV. |
| `connectwise-asio-inspector` | 103 | ConnectWise Asio | Asio, CW Asio | RMM. |
| `connectwise-automate-inspector` | 36 | ConnectWise Automate | CW Automate, CWA, Automate, **LabTech** (legacy) | RMM. |
| `connectwise-manage-inspector` | 9 | ConnectWise Manage | CW Manage, CWM, Manage | PSA. |
| `continuum-rmm-inspector` | 60 | Continuum RMM | Continuum, ConnectWise Continuum | RMM. |
| `cove-data-protection-inspector` | 76 | Cove Data Protection | Cove, N-able Cove, **SolarWinds Backup** (legacy) | Cloud backup. |
| `datto-bcdr-inspector` | 38 | Datto BCDR | BCDR, SIRIS, ALTO, Datto Backup | Parent/child — confirm child appliance. |
| `datto-rmm-inspector` | 73 | Datto RMM | Datto RMM, **Centrastage** (legacy), **Autotask Endpoint Management** (legacy) | RMM. |
| `duo-security-inspector` | 47 | Duo Security | Duo, Cisco Duo | MFA. |
| `halopsa-inspector` | 94 | HaloPSA | Halo, Halo PSA | PSA. |
| `huntress-inspector` | 97 | Huntress | Huntress Labs | EDR. |
| `hyper-v-inspector` | 39 | Hyper-V | HyperV, Microsoft Hyper-V | Hypervisor. |
| `itglue-inspector` | 26 | IT Glue | ITG | Documentation. |
| `kaseya-bms-inspector` | 83 | Kaseya BMS | BMS | PSA. |
| `kaseya-vsa-inspector` | 48 | Kaseya VSA | VSA, Kaseya | RMM. |
| `n-able-n-central-inspector` | 71 | N-able N-Central | N-central, NC, **SolarWinds N-central** (legacy) | RMM. |
| `nable-rmm-inspector` | 87 | N-able RMM | N-able, **SolarWinds RMM** (legacy) | RMM. |
| `ninjaone-inspector` | 72 | NinjaOne | Ninja, **NinjaRMM** (legacy) | RMM. Renamed 2022. |
| `sql-server-inspector` | 10 | SQL Server | MSSQL, MS SQL | Database. |
| `sonicwall-capture-client-inspector` | 95 | SonicWall Capture Client | SCC, Capture Client, SonicWall EDR | EDR. |
| `sophos-central-inspector` | 65 | Sophos Central | Sophos, Sophos Endpoint, Intercept X | EDR. **Distinct from Sophos Firewall.** |
| `storagecraft-spx-inspector` | 46 | StorageCraft SPX | SPX, StorageCraft, ShadowProtect | Backup. |
| `syncro-inspector` | 86 | Syncro | Syncro PSA, Syncro MSP, **RepairShopr** (legacy) | PSA/RMM. |
| `vmware-esxi-inspector` | 59 | VMware ESXi | ESXi, vSphere | Hypervisor. **Distinct from vCenter inspector.** |
| `vade-inspector` | 91 | Vade | Vade Secure, Vade for M365 | Email security. |
| `veeam-availability-console-inspector` | 35 | Veeam Availability Console | VAC | Backup. **Distinct from VSPC.** |
| `veeam-service-provider-console-inspector` | 75 | Veeam Service Provider Console | VSPC | Backup. **Distinct from VAC.** |
| `watchman-monitoring-inspector` | 50 | Watchman Monitoring | Watchman | macOS monitoring. |
| `webroot-inspector` | 15 | Webroot SecureAnywhere GSM | Webroot, WSA, SecureAnywhere | EDR/AV. |

### Beta

| Inspector | ID | Display name | Common aliases | Notes |
|---|---|---|---|---|
| `axcient-x360-recover-inspector` | 100 | Axcient x360 Recover (Beta) | Axcient, x360, x360 Recover | Backup. Parent/child. |
| `crowdstrike-inspector` | 102 | CrowdStrike (Beta) | CS, CrowdStrike Falcon, Falcon, CSF | EDR. |
| `engenius-cloud-inspector` | 101 | EnGenius Cloud (Beta) | EnGenius | Network controller. |
| `godaddy-inspector` | 23 | GoDaddy (Beta) | GoDaddy | Domain registrar. |
| `junos-inspector` | 42 | Junos (Beta) | Juniper, JunOS | Router/switch. |
| `managed-printer-inspector` | 89 | Managed Printer (Beta) | Printer, Managed Print | Print device. |
| `palo-alto-panos-inspector` | 49 | Palo Alto PAN-OS (Beta) | PA, Palo Alto, PAN-OS, Panorama | Firewall. |
| `vmware-vcenter-inspector` | 58 | VMware vCenter (Beta) | vCenter, vSphere | Hypervisor. **Distinct from ESXi inspector.** |

### Cloud

| Inspector | ID | Display name | Common aliases | Notes |
|---|---|---|---|---|
| `3cx-inspector` | 85 | 3CX | 3CX | VoIP. |
| `acronis-cyber-protect-cloud-inspector` | 93 | Acronis Cyber Protect Cloud | Acronis, ACP, Acronis Backup | Parent/child. |
| `aws-inspector` | 1 | Amazon Web Services | AWS, Amazon | Cloud platform. |
| `box-com-inspector` | 14 | Box | Box, Box.com | Cloud storage. |
| `cisco-umbrella-inspector` | 32 | Cisco Umbrella | Umbrella, **OpenDNS** (legacy), Cisco DNS | Parent/child sub-orgs. |
| `cloudflare-inspector` | 82 | Cloudflare | CF | DNS/CDN. |
| `dark-web-inspector` | 4 | Dark Web Monitoring | Dark Web, Breach Monitor | Email breach monitor. |
| `dropbox-inspector` | 34 | Dropbox | Dropbox | Cloud storage. |
| `eset-licensing-inspector` | 69 | ESET Licensing | ESET | EDR licensing. |
| `google-drive-inspector` | 80 | Google Drive | GDrive | Cloud storage. |
| `google-workspace-inspector` | 61 | Google Workspace | GWS, GW, **G Suite** (legacy), **Google Apps** (legacy) | Cloud productivity. |
| `internet-domain-dns-inspector` | 2 | Internet Domain / DNS | Domain, DNS, WHOIS, MX | Domain monitor. |
| `jumpcloud-inspector` | 68 | JumpCloud | JC | Identity/MDM. |
| `knowbe4-inspector` | 81 | KnowBe4 | KB4, KnowBe4 SAT | Security awareness. |
| `microsoft-365-inspector` | 8 | Microsoft 365 | M365, O365, **Office 365**, MS365 | **Includes Entra ID / Azure AD identity data.** |
| `azure-inspector` | 11 | Microsoft Azure | Azure, MS Azure | Subscription resources (NSGs, EBS, IAM). **Identity is via M365 inspector.** |
| `onelogin-inspector` | 27 | OneLogin | OL | Identity provider. |
| `sentinelone-inspector` | 70 | SentinelOne | S1, Singularity | EDR. Parent/child — confirm child tenant. |
| `slack-inspector` | 66 | Slack | Slack | Collaboration. |
| `tls-ssl-inspector` | 16 | TLS/SSL Certificates | TLS, SSL, Cert | Certificate monitor. |

### Endpoint

| Inspector | ID | Display name | Common aliases | Notes |
|---|---|---|---|---|
| `linux-inspector` | 53 | Linux | Linux server, Linux workstation | OS inspector. |
| `windows-server-inspector` | 25 | Windows Server | Server, WinSrv, Server OS | OS inspector. |
| `windows-workstation-inspector` | 90 | Windows Workstation | Workstation, WS, Windows endpoint | OS inspector. |
| `macos-inspector` | 96 | macOS | Mac, OSX | OS inspector. |

### Network

| Inspector | ID | Display name | Common aliases | Notes |
|---|---|---|---|---|
| `auvik-inspector` | 62 | Auvik | Auvik | Network management. |
| `barracuda-firewall-inspector` | 52 | Barracuda Firewall | Barracuda | Firewall. |
| `cisco-asa-inspector` | 22 | Cisco ASA | ASA, Cisco firewall | Firewall. |
| `cisco-ios-inspector` | 30 | Cisco IOS | Cisco IOS, Cisco router, Cisco switch | Router/switch. |
| `cisco-meraki-inspector` | 3 | Cisco Meraki | Meraki, MX, MS, MR | Network controller. |
| `cisco-sbs-switch-inspector` | 78 | Cisco Small Business Switch | Cisco SBS, SBS | Switch. |
| `datto-networking-inspector` | 79 | Datto Networking | Datto Networking | Network management. |
| `domotz-inspector` | 88 | Domotz | Domotz | Network monitoring. |
| `fortinet-fortigate-inspector` | 33 | Fortinet FortiGate | Fortinet, FortiGate, FGT, Forti | Firewall. |
| `hp-procurve-inspector` | 63 | HP ProCurve | ProCurve, HPE Aruba | Switch. |
| `autodiscovery-inspector` | 41 | Network Discovery | Autodiscovery, Discovery | Network discovery. |
| `network-ip-inspector` | 4 | Network IP Address | Network IP, IP monitor | IP monitor. **Note: same ID 4 as Dark Web Monitoring in some lookups; disambiguate by inspector slug.** |
| `sonicwall-inspector` | 7 | SonicWall | SW, SonicOS, SonicWall NSa, SonicWall TZ | Firewall. |
| `sophos-firewall-inspector` | 28 | Sophos Firewall | Sophos XG, XGS | Firewall (XG/XGS). **Distinct from Sophos Central / Sophos SG.** |
| `sophos-sg-inspector` | 43 | Sophos SG | Sophos SG | Firewall (legacy UTM). **Distinct from Sophos Firewall (XG/XGS).** |
| `synology-nas-inspector` | 64 | Synology NAS | Synology, DSM | NAS/storage. |
| `ubiquiti-unifi-inspector` | 40 | Ubiquiti UniFi | UniFi, Ubiquiti, UDM | Network controller. |
| `watchguard-inspector` | 29 | WatchGuard | WG | Firewall. |
| `pfsense-inspector` | 37 | pfSense | pfSense, Netgate | Firewall. |

---

## Maintenance

When a new inspector ships:

1. Confirm the new row in `reference/inspector-name-system-id-mapping.xlsx`.
2. Add a row to the **Alphabetical alias index** with every common name the user
   might say (vendor abbreviation, product family, parent company, legacy name).
3. Add a row to the matching **Full inspector reference by category** table with
   notes on parent/child models, name distinctions, and legacy product names.
4. If the inspector replaces or renames a previous one (e.g., NinjaRMM → NinjaOne),
   keep the old name as an alias so older recipes and user phrasing still resolve.

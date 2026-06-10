# System-Type Assessment Recipes

Cross-system recipes that span every system of a given type in an environment —
"all firewalls", "all EDRs", "Windows patching across every server and
workstation", etc. These iterate the asset inventory or per-system list and
produce a unified report.

Use these when the deliverable is "for the whole environment, not one system."

## Available recipes

| Recipe | Scope | Common asks |
|---|---|---|
| `all-edrs.md` | All deployed EDRs (SentinelOne, Huntress, Sophos Central, Webroot, Bitdefender, CrowdStrike, ESET, SonicWall Capture Client) | Fleet EDR coverage %, per-vendor health, coverage gap, multi-EDR overlap |
| `all-endpoints.md` | All endpoints across OS — Windows Server, Win Workstation, macOS, Linux | Fleet composition, OS family / vendor distribution, Win11 readiness, lifecycle |
| `all-servers.md` | **Server-class only** — Win Server + Linux + server-tier macOS | Role inventory, blast-radius, server-tier patch cadence, local privileged accounts, lifecycle, backup coverage cross-link |
| `all-hypervisors.md` | Hypervisor stack — VMware ESXi, vCenter (Beta), Hyper-V | VM-to-host topology, datastore free space, VM density, snapshot hygiene, HA / replication, license expiry |
| `all-firewalls.md` | All deployed firewalls (SonicWall, FortiGate, ASA, Sophos XG, Meraki MX, etc.) | Fleet firmware status, license expiration roadmap, WAN management exposure, vendor consolidation |
| `all-backups.md` | Server-OS × backup-vendor cross-inspector join (Datto BCDR, Cove, Acronis, Axcient, Veeam, StorageCraft) | Unprotected-server detection, last-valid-backup per server, failed-backup trends, vendor distribution |
| `all-windows-patching.md` | Windows Server + Workstation + optional RMM | Patch compliance %, top unpatched, Win11 readiness |
| `all-domains.md` | All domains via `liongard_domain` reconciled inventory | Expiration roadmap, DMARC posture, registrar consolidation, hosting footprint |
| `all-identity-providers.md` | Identity providers — AD, M365/Entra, Google Workspace, JumpCloud, Okta, OneLogin | MFA coverage, privileged accounts, stale users, sync status across IDPs |
| `all-rmm-platforms.md` | RMM platforms — CW Automate, Datto RMM, NinjaOne, N-able, Kaseya VSA, Syncro | Agent health, offline devices, patch coverage, multi-RMM overlap |
| `all-cloud-infrastructure.md` | Cloud — AWS, Azure, Google Workspace | IAM posture, encryption, logging, security tooling across all cloud tenants |
| `all-cloud-storage.md` | Cloud file storage — OneDrive, SharePoint, Google Drive, Box, Dropbox | Sharing posture, external links, large-file outliers, backup coverage gaps |
| `all-network-infrastructure.md` | Switches, APs, and network devices — Cisco, Ubiquiti UniFi, HP ProCurve, Datto Networking | Firmware currency, management-VLAN exposure, VLAN inventory |
| `all-network-monitoring.md` | Network monitoring platforms — Auvik, Domotz | Coverage gaps, alert posture, topology visibility |
| `all-psa-platforms.md` | PSA platforms — ConnectWise Manage, Autotask, HaloPSA, Kaseya BMS | Contract and SLA data availability for billing reconciliation |
| `all-external-attack-surface.md` | External attack surface — Cloudflare, internet DNS/domain, TLS/SSL, Cisco Umbrella | Domain expiration, cert expiry, public IP exposure, DNS hygiene |

## How they differ from single-system recipes

- **Single-system** (`recipes/single-system-analysis/by-inspector/<x>.md`) — one
  system, one inspector, deep dive. Driven by a system ID.
- **System-type** (this folder) — every system of a class, cross-vendor. Driven by
  an environment ID; iterates per-system internally.
- **Domain assessment** (`recipes/domain-assessment/`) — cross-cutting *attributes*
  rather than systems (auth across all identity systems; encryption across all
  endpoints).

## Recipe structure

Same canonical structure as single-system recipes (see `templates/recipe-skeleton.md`),
but the **Inputs** section requires only an environment ID — the recipe lists the
relevant systems internally. The **Locating the right system** section is replaced
with a "Locating in-scope systems" pattern that lists every system the recipe will
visit.

## References

- `reference/inspector-aliases.md` — inspector lookups
- `reference/asset-fields.md` — asset inventory schema and PBR pattern library
- `templates/recipe-skeleton.md` — canonical recipe shape

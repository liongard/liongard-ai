# Reconciled Asset Inventory — Field Reference

The authoritative reference for the three reconciled-asset-inventory tools:
`liongard_device`, `liongard_identity`, `liongard_domain`. Recipes link here
instead of redefining their own field tables — when a schema changes (new
field, renamed field, deprecated field), update this file.

> **For cross-cutting recipes** (PBR / quarterly lookback, onboarding,
> roadmap, sales assessment, compliance evidence packs) that need broader
> environment-level signals — change-detection, alerts, inspection
> timeline, pre-aggregated KPIs — see
> [`reference/cross-cutting-signals.md`](./cross-cutting-signals.md). That
> file documents the `liongard_detection` / `liongard_alert` /
> `liongard_timeline` / `liongard_cyber_risk_dashboard` /
> `liongard_events` / `liongard_query` / `liongard_report` tools and the
> 10-step pattern for time-bounded narrative reports.

> **`liongard_asset` has been removed** — do not use it in recipes. The three
> tools below replaced it, and the legacy alias no longer resolves on current
> Liongard MCP servers. Always target the dedicated tools directly.
>
> **For category counts (M365 users, Windows workstations, etc.), prefer
> `liongard_cyber_risk_dashboard`** — it exposes named metrics like
> `m365TotalUsers`, `workstationTotalCount`, `winServerTotalCount`,
> `macOSTotalCount`. Use the per-tool `COUNT` operation for attribute-based
> counts (e.g., "identities with mfaStatus = NO in env X").

---

## Tool overview

Each tool exposes three operations:

| Operation | Purpose | Notes |
|---|---|---|
| `LIST` | Filtered listing with pagination | Use server-side filter parameters whenever possible; client-side JMESPath only as fallback. |
| `GET` | Single record by UUID | Direct fetch when you already know the UUID. |
| `COUNT` | Return count(s) without pagination | For `liongard_identity`, also returns a `StatusCounts[]` breakdown by `InventoryState` + `MfaStatus` — always surface this. |

All three tools share these patterns:
- `environmentId=<int>` — filter to one environment. **Omit** to query across
  all accessible environments (use sparingly; cross-tenant defaults are
  governed by the API).
- `inventoryState="Discovery" | "Inventory" | "Archive"` — workflow state.
- `pageSize=<int up to 200>` and `page=<int>` — pagination.
- `fields=[...]` — projection: list only the fields you need to reduce
  payload size.
- `responseFormat="json" | "toon"` — JSON for code-integrated reads; TOON
  for token-efficient long lists.

## Deduplication keys — these are reconciled views, not raw per-inspector lists

The three tools return **one record per real-world entity**, joined across
every inspector that observed it. The dedup keys:

| Tool | Dedup key(s) | What this means |
|---|---|---|
| `liongard_identity` | **email address** (primary) | A user with the same email in M365, AD, JumpCloud, OneLogin, and Duo returns as **one** identity record with `inspectors[]` listing all five. The `LastLoginUser` / `Username` fields stay per-inspector inside that single record. |
| `liongard_device` | **hostname**, **serial number**, **MAC address** (any of the three) | A workstation seen by Windows OS inspector, EDR, RMM, and AD returns as **one** device record with `inspectors[]` listing all four. Liongard's reconciliation engine joins on whichever key is most reliable for that asset class. |
| `liongard_domain` | **domain name** | A domain referenced by the Internet Domain inspector, M365 accepted-domains, and Google Workspace verified-domains returns as **one** record with `inspectors[]` listing all three. |

**Why this matters for assessment recipes** — onboarding intakes, PBRs,
roadmap planning, sales discovery, compliance evidence packs all need
*who/what/where* counts that don't double-count. The reconciled tools
give the MSP that view directly. Per-inspector `liongard_metric` calls
are for **inspector-specific configuration detail** (e.g., the actual
SPF record published, the actual firewall rule list, the actual policy
the EDR is running). They are **not** the right tool for "how many
users does this customer have" — that's `liongard_identity COUNT`.

Concretely, assessment recipes should:

1. **Start with the reconciled inventory** for identities / devices /
   domains — confirms scope and dedup'd counts.
2. **Cross-check against the cyber-risk-dashboard** for category counts
   (M365 user total, Windows workstation total, etc.) — these are
   independently maintained and provide divergence detection.
3. **Drop into per-inspector metrics only when** the recipe needs
   inspector-specific configuration detail the reconciled view doesn't
   expose.

---

## `liongard_device` — Device Inventory

Reconciled hardware/OS view across every device-aware inspector. Authoritative
source for hostname, IP, serial, OS, EDR, warranty, virtualization topology.

> **Routing reminder:** `liongard_device` returns ALL device types mixed
> together — smartphones, DCs, desktops, laptops. For class-specific counts
> (Windows workstations, Windows servers, macOS) prefer
> `liongard_cyber_risk_dashboard`; for class-specific filters use `category=`
> or filter client-side.

### Server-side filter parameters

| Parameter | Type | Notes |
|---|---|---|
| `hostname` | string | Case-insensitive substring match |
| `operatingSystem` | string | "Windows", "Linux", "macOS", etc. |
| `manufacturer` | string | "Dell", "HP", "Lenovo", etc. |
| `model` | string | Model substring |
| `category` | string | Device category |
| `serialNumber` | string | Hardware serial |
| `macAddress` | string | MAC address |
| `ipAddress` | string | Internal IP filter |
| `managedDevice` | bool | MSP-managed flag |
| `domainRole` | string | AD OU path / domain role substring |
| `physical` | bool | true=physical, false=VM |
| `status` | string | active / inactive / idle / standby |
| `inventoryState` | enum | Discovery / Inventory / Archive |
| `query` | string | Free-text keyword search |

### Field reference (queryable + projectable via `fields=`)

| Field | Type | PBR / assessment use |
|---|---|---|
| `id` | UUID | Use with `GET` |
| `hostname` | string | Primary identifier |
| `alias` | string | Friendly name |
| `operatingSystem` | string | OS family for EOL assessment |
| `osVersion` | string | Exact build for EOL date lookup |
| `manufacturer` | string | Hardware vendor breakdown |
| `model` | string | Refresh roadmap; standardization audit |
| `serialNumber` | string | CMDB reconciliation; warranty matching; insurance asset audit |
| `macAddress` | string | Network topology; rogue device detection |
| `internalIP` | string | Subnet inventory |
| `externalIP` | string | Public-exposure detection |
| `category` | string | "compute", "network", etc. |
| `class` | string | Sub-classification within category |
| `role` | string | DC / file / web / app / etc. |
| `purpose` | string | Free-text purpose tag |
| `domainRole` | string | AD OU path / domain role |
| `antivirus` | set string | Confirmed AV product(s); null = not detected (or not locally inspected) |
| `edr` | set string | Confirmed EDR product(s); same null caveat |
| `firmware` | string | BIOS / UEFI / device firmware version |
| `physical` | bool | Physical vs. VM |
| `hostServer` | string | Parent hypervisor when `physical=false` |
| `clusterName` | string | Hypervisor cluster name |
| `dataCenter` | string | DC identifier |
| `virtualizationSoftware` | string | Hypervisor product |
| `hypervisorVersion` | string | Hypervisor version |
| `purchaseDate` | ISO timestamp | Lifecycle |
| `warrantyExpiration` | ISO timestamp | Refresh roadmap; insurance attestation |
| `eolDate` | ISO timestamp | OS EOL when populated |
| `winElevenReady` | string | "Compatible" / "Incompatible" / "Unknown" |
| `assetTagNumber` | string | MSP-internal tag |
| `availableStorage` | string | Free disk |
| `licenseExpiration` | ISO timestamp | Per-device license expiry |
| `hardwareID` | string | Vendor / SMBIOS HW ID |
| `interfaces` | JSON | Network adapters (array) |
| `lastLogin` | ISO timestamp | Orphaned-device detection |
| `lastLoginUser` | string | Primary user assignment |
| `lastSeen` | ISO timestamp | Stale-inspector signal |
| `inspectors` | JSON array | Coverage gap detection |
| `inventoryState` | string | MSP workflow state |
| `lastReviewDate` | ISO timestamp | Audit currency |
| `location` | string | Site / office / RMM tag |
| `locationManaged` | string | MSP-managed location |
| `environmentId` | int | Tenant scope |

### Common patterns

```
# Lookup by hostname
liongard_device LIST hostname="<hostname>" environmentId=<ENV_ID>

# Lookup by serial (warranty registration / asset reconciliation)
liongard_device LIST serialNumber="<serial>"

# Hardware vendor distribution
liongard_device LIST manufacturer="Lenovo" environmentId=<ENV_ID>

# OS-family + physical filter
liongard_device LIST operatingSystem="Windows Server" physical=true environmentId=<ENV_ID>

# Managed-device count
liongard_device COUNT managedDevice=true environmentId=<ENV_ID>

# Devices likely off the radar (Discovery state, not yet categorized)
liongard_device LIST inventoryState="Discovery" environmentId=<ENV_ID>

# Field projection — pull just hostname + serial + warranty for refresh planning
liongard_device LIST environmentId=<ENV_ID> fields=["hostname","serialNumber","warrantyExpiration","model"]

# Cross-check coverage: VMs without a hypervisor host (data-quality flag)
# physical=false should always have hostServer set
liongard_device LIST physical=false environmentId=<ENV_ID> | filter where hostServer is null
```

---

## `liongard_identity` — Identity Inventory

Reconciled user / account view across every identity-aware inspector
(AD, M365, Duo, JumpCloud, NinjaOne, etc.). Authoritative for MFA, privilege,
account activity, license assignment.

### Server-side filter parameters

| Parameter | Type | Notes |
|---|---|---|
| `email` | string | Case-insensitive substring |
| `username` | string | Substring match |
| `firstName` | string | |
| `lastName` | string | |
| `displayName` | string | |
| `department` | string | Department exact match |
| `membership` | string | Group membership substring (e.g. "Domain Admins") |
| `mfaStatus` | string | "YES", "NO", "PARTIAL" |
| `enabled` | bool | |
| `privileged` | bool | |
| `accountActivity` | string | "Active", "Stale", "Dormant", "Never Used", "No Activity Found" |
| `authorizationStatus` | string | Liongard's authorization flag |
| `status` | string | Per-system status |
| `type` | string | Identity type (user / service / application) |
| `inventoryState` | enum | Discovery / Inventory / Archive |
| `query` | string | Free-text keyword |

### Field reference (queryable + projectable via `fields=`)

| Field | Type | PBR / assessment use |
|---|---|---|
| `id` | UUID | Use with `GET` |
| `email` | string | Primary identifier |
| `username` | string | sAMAccountName / UPN local part |
| `firstName`, `lastName`, `displayName` | string | Reports, rosters |
| `phone` | string | Onboarding contact directory |
| `department` | string | Dept rollups |
| `membership` | JSON set | AD/M365 group memberships |
| `type` | string | "service", "application", regular user |
| `enabled` | bool | Active vs. disabled |
| `privileged` | bool | Admin/elevated flag |
| `accountActivity` | string | Cross-inspector synthesized staleness |
| `mfaStatus` | string | "YES", "NO", "PARTIAL", null |
| `mfaMethod` | string | Aggregated MFA method(s) |
| `relatedEmails` | string | Linked UPN/alias addresses |
| `status` | string | Per-system status |
| `locationManaged` | string | Managed location |
| `emailLicenses` | array/string | M365 SKUs assigned (E3, EMS-E3, etc.) — license rightsizing, finance |
| `liongardBillable` | bool | Liongard licensing/billing flag |
| `supportStatus` | string | Active support eligibility |
| `authorizationStatus` | string | Liongard's access-authorization flag |
| `accountCreated` | ISO timestamp | Earliest account creation |
| `lastLogin` | ISO timestamp | Last sign-in |
| `lastSeen` | ISO timestamp | Most recent inspector observation |
| `inspectors` | JSON array | Which systems report this identity |
| `inventoryState` | string | MSP workflow state |
| `lastReviewDate` | ISO timestamp | Access review currency |
| `location`, `purpose` | string | Site / curated note |
| `environmentId` | int | Tenant scope |

### Common patterns

```
# MFA gap count (the most common cyber-insurance signal)
liongard_identity COUNT environmentId=<ENV_ID> mfaStatus="NO" enabled=true
# → returns Count + StatusCounts[] breakdown by InventoryState/MfaStatus

# Privileged users without MFA — critical
liongard_identity LIST environmentId=<ENV_ID> privileged=true mfaStatus="NO"

# Stale-but-enabled (offboarding cleanup)
liongard_identity LIST environmentId=<ENV_ID> enabled=true accountActivity="Stale"
liongard_identity LIST environmentId=<ENV_ID> enabled=true accountActivity="Dormant"
liongard_identity LIST environmentId=<ENV_ID> enabled=true accountActivity="Never Used"

# Department-scoped MFA roll-up
liongard_identity LIST environmentId=<ENV_ID> department="Finance" enabled=true
  # Then group_by mfaStatus client-side

# Service accounts with admin rights (compound — use server filters then JMESPath)
liongard_identity LIST environmentId=<ENV_ID> privileged=true type="service"

# Field projection — light pull for rosters
liongard_identity LIST environmentId=<ENV_ID> fields=["email","displayName","department","mfaStatus","enabled"]

# License footprint (group_by client-side)
liongard_identity LIST environmentId=<ENV_ID> fields=["email","emailLicenses"]
```

### Identity → Device join

There is no direct `relatedDevices` field. To find devices an identity uses,
join on `lastLoginUser`:

```
# 1. Get identity username
identity = liongard_identity GET id=<UUID>
# 2. Find devices where lastLoginUser matches
liongard_device LIST environmentId=<ENV_ID> lastLoginUser=<identity.username>
```

This answers "what devices does this user log into?" — useful for offboarding
device retrieval, executive refresh planning, multi-device user detection.

---

## `liongard_domain` — Domain Inventory

Reconciled DNS/web domain profile. Authoritative for DMARC health, registrar,
expiration, email/website detection, IPv4/IPv6, ASN.

### Server-side filter parameters

| Parameter | Type | Notes |
|---|---|---|
| `category` | string | Domain category |
| `domainName` | string | Substring match |
| `registrar` | string | Substring match |
| `dmarcHealth` | string | "valid", "not-valid", "not-found" |
| `emailDetected` | bool | |
| `websiteDetected` | bool | |
| `ipAddress` | string | IPv4/IPv6 substring |
| `asn` | string | Autonomous System Number |
| `asName` | string | AS organization name |
| `managedDomain` | bool | MSP-managed flag |
| `inventoryState` | enum | Discovery / Inventory / Archive |
| `inspectorId` | string | Filter by source inspector |
| `expirationDateBefore` / `expirationDateAfter` | ISO date | |
| `minDaysTillExpiration` / `maxDaysTillExpiration` | int | |
| `registrationDateBefore` / `registrationDateAfter` | ISO date | |
| `lastSeenBefore` / `lastSeenAfter` | ISO date | |
| `createdAfter` / `createdBefore` | ISO date | |
| `deletedAfter` / `deletedBefore` | ISO date | |
| `query` | string | Free-text keyword |

### Field reference (queryable + projectable via `fields=`)

| Field | Type | PBR / assessment use |
|---|---|---|
| `id` | UUID | Use with `GET` |
| `domainName` | string | Primary identifier |
| `category` | string | Classification |
| `registrar` | string | Vendor consolidation |
| `registrationDate` | ISO timestamp | When registered |
| `expirationDate` | ISO timestamp | When expires |
| `daysTillExpiration` | int | Pre-computed for roadmap |
| `dmarcHealth` | string | "valid", "not-valid", "not-found" |
| `emailDetected` | bool | MX records present |
| `websiteDetected` | bool | A/AAAA records present |
| `ipv4Address` | string | A record |
| `ipv6Address` | string | AAAA record |
| `asn` | string | Autonomous System Number |
| `asName` | string | Hosting org / ISP |
| `managedDomain` | bool | MSP-managed flag |
| `inspectors` | JSON array | Source inspectors |
| `inventoryState` | string | Workflow state |
| `lastSeen` | ISO timestamp | Most recent inspection |
| `createdOn`, `updatedOn`, `deletedOn` | ISO timestamp | Lifecycle |
| `environmentId` | int | Tenant scope |

### Common patterns

```
# Domain expiration roadmap — next 30 days
liongard_domain LIST maxDaysTillExpiration=30 environmentId=<ENV_ID>

# Already-expired domains (data hygiene)
liongard_domain LIST maxDaysTillExpiration=0 environmentId=<ENV_ID>

# DMARC posture audit
liongard_domain COUNT environmentId=<ENV_ID> dmarcHealth="valid"
liongard_domain COUNT environmentId=<ENV_ID> dmarcHealth="not-valid"
liongard_domain COUNT environmentId=<ENV_ID> dmarcHealth="not-found"

# Registrar consolidation candidate
liongard_domain LIST environmentId=<ENV_ID> fields=["domainName","registrar"]
  # group_by registrar client-side

# Domains with email but no website (or vice versa)
liongard_domain LIST emailDetected=true websiteDetected=false environmentId=<ENV_ID>

# Hosting infrastructure rollup
liongard_domain LIST environmentId=<ENV_ID> fields=["domainName","ipv4Address","asn","asName"]
```

---

## Coverage gap rule (devices)

The `inspectors[]` array on each device asset reveals which Liongard inspectors
are aware of it. This is the most reliable way to detect ungoverned assets and
to distinguish "genuinely missing" from "not yet inspected":

| Inspector presence | Asset state | Action |
|---|---|---|
| Local OS inspector + EDR/AV inspector | Fully covered | ✅ |
| Local OS inspector, `edr` is null | Genuine gap — locally confirmed missing | ❌ remediate |
| Only `active-directory-inspector` | Domain-known, not locally inspected | 🔍 deploy endpoint inspector |
| Only RMM inspector | RMM-known, not locally inspected | 🔍 enable Windows/Mac inspector |
| No inspector at all | Shadow / unauthorized | ❌ investigate |

The same logic applies to identities: an identity reported only by an inspector
without MFA visibility (e.g., a legacy LDAP system) will have `mfaStatus = null`
even if the user genuinely has MFA via M365.

---

## Common PBR / single-system patterns

### Hardware inventory rollup
```
liongard_device LIST environmentId=<ENV_ID> fields=["hostname","manufacturer","model","operatingSystem"]
  → group_by manufacturer / model / operatingSystem
```

### Refresh / EOL roadmap
```
# Win10 EOL hardware-replacement candidates
liongard_device LIST environmentId=<ENV_ID> operatingSystem="Windows 10"
  → filter where winElevenReady == "Incompatible"

# Out-of-warranty devices
liongard_device LIST environmentId=<ENV_ID> fields=["hostname","warrantyExpiration"]
  → filter where warrantyExpiration < today

# Warranty expiring within 90 days
# (no direct param — use fields projection + client-side filter)
```

### License / cost insights
```
# M365 SKU distribution
liongard_identity LIST environmentId=<ENV_ID> fields=["email","emailLicenses","department"]
  → group_by emailLicenses

# Identities billable to Liongard (finance)
# Use COUNT to avoid pagination
# (filter parameter for liongardBillable not currently exposed — use LIST + filter)
```

### Virtualization / cluster topology
```
# VM count per host
liongard_device LIST environmentId=<ENV_ID> physical=false fields=["hostname","hostServer"]
  → group_by hostServer

# Cluster occupancy + datacenter footprint
liongard_device LIST environmentId=<ENV_ID> fields=["hostname","clusterName","dataCenter"]
  → group_by (clusterName, dataCenter)
```

### Identity / device cross-reference
```
# Devices assigned to executives
exec_users = liongard_identity LIST environmentId=<ENV_ID> privileged=true
exec_devices = liongard_device LIST environmentId=<ENV_ID> ...
  → filter where lastLoginUser in exec_users.username

# Multi-device users
liongard_device LIST environmentId=<ENV_ID> fields=["lastLoginUser","hostname"]
  → group_by lastLoginUser, count > 1
```

### Domain expiration roadmap
```
# Pre-built — no client-side computation needed
liongard_domain LIST environmentId=<ENV_ID> minDaysTillExpiration=0 maxDaysTillExpiration=90
  → fields=["domainName","registrar","daysTillExpiration","expirationDate"]
```

### DMARC posture
```
# Three categories pre-built
liongard_domain LIST environmentId=<ENV_ID> dmarcHealth="not-valid"  # mis-configured
liongard_domain LIST environmentId=<ENV_ID> dmarcHealth="not-found"  # missing
liongard_domain LIST environmentId=<ENV_ID> dmarcHealth="valid"      # healthy
```

---

## Maintenance

When the inventory schema changes:

1. The tool description (`mcp__Liongard__liongard_device` etc.) is the
   authoritative source. Read it first.
2. Update the field tables and parameter tables here.
3. Update the **patterns** section if a new field unlocks a new pattern or a
   filter parameter becomes available.
4. Update `templates/recipe-skeleton.md` when broadly-used patterns change.
5. Existing recipes may continue to use older patterns until the migration
   sweep — that's intentional, the deprecated alias still resolves.

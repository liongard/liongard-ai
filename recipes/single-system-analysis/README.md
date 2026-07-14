# Single-System Analysis Recipes

One system, one inspector. Each recipe in `by-inspector/` produces a per-system
artifact — Periodic Business Review (PBR / QBR), monthly health check, license
review, threat posture, etc. — using live Liongard data via the asset inventory
(primary) and per-vendor metrics (cross-check).

The recipes in this folder are **the** building blocks for cross-system rollups in
`recipes/system-type-assessment/` and `recipes/environment-quarterly-lookback/`.

## Available recipes

76 per-inspector recipes live in `by-inspector/`. Selected entries by category:

**EDR / Security:**
`sentinelone.md` · `huntress.md` · `crowdstrike.md` · `bitdefender-gravityzone.md` · `sophos-central.md` · `webroot.md` · `sonicwall-capture-client.md` · `eset-licensing.md`

**Identity & Collaboration:**
`microsoft-365.md` · `google-workspace.md` · `active-directory.md` · `jumpcloud.md` · `onelogin.md` · `duo-security.md` · `knowbe4.md` · `dark-web-monitoring.md`

**Network / Firewall:**
`sonicwall.md` · `fortinet-fortigate.md` · `cisco-meraki.md` · `cisco-asa.md` · `cisco-ios.md` · `palo-alto-panos.md` · `sophos-firewall.md` · `sophos-sg.md` · `barracuda-firewall.md` · `pfsense.md` · `watchguard.md` · `ubiquiti-unifi.md` · `auvik.md` · `domotz.md`

**RMM / PSA:**
`connectwise-automate.md` · `connectwise-manage.md` · `connectwise-asio.md` · `datto-rmm.md` · `ninjaone.md` · `kaseya-vsa.md` · `kaseya-bms.md` · `halopsa.md` · `autotask.md` · `syncro.md` · `nable-rmm.md` · `n-able-n-central.md` · `continuum-rmm.md` · `itglue.md`

**Backup / Storage:**
`datto-bcdr.md` · `cove-data-protection.md` · `acronis-cyber-protect-cloud.md` · `axcient-x360-recover.md` · `veeam-availability-console.md` · `veeam-service-provider-console.md` · `storagecraft-spx.md` · `synology-nas.md`

**Endpoint / OS:**
`windows-server.md` · `windows-workstation.md` · `macos.md` · `linux.md` · `addigy.md` · `watchman-monitoring.md`

**Cloud & SaaS:**
`aws.md` · `azure.md` · `google-drive.md` · `box.md` · `dropbox.md` · `slack.md` · `cisco-umbrella.md` · `cloudflare.md`

**Networking / Infra:**
`network-discovery.md` · `network-ip-address.md` · `internet-domain-dns.md` · `tls-ssl.md` · `datto-networking.md` · `hp-procurve.md` · `cisco-sbs-switch.md` · `junos.md` · `managed-printer.md` · `godaddy.md`

For the complete inspector-to-system mapping with IDs, see `internal/inspector-name-system-id-mapping.xlsx`.

## How to invoke a recipe

In a Cowork or Claude Desktop session with the Liongard MCP connected:

```
Using the recipe at recipes/single-system-analysis/by-inspector/<inspector>.md,
produce a <period> single-system review for <inspector> <CUSTOMER_NAME>.
Output as <markdown|word|pptx>.
```

If you know the system ID and environment ID:

```
Using the recipe at recipes/single-system-analysis/by-inspector/<inspector>.md,
produce a single-system review for system <SYSTEM_ID> in environment <ENV_ID>.
Output as <format>.
```

If you only know the customer name:

```
Using the recipe at recipes/single-system-analysis/by-inspector/<inspector>.md,
find a <inspector> system for "<CUSTOMER_NAME>" and produce a single-system review.
Output as <format>.
```

## Parent/child systems

Many inspectors use a parent/child model. The parent is a sparse discovery stub;
the child is the per-tenant system that holds the real data. Every per-inspector
recipe documents how to identify the right child. Always target the child.

Inspectors with parent/child:
- SentinelOne — confirm via `SystemInfo.accountName`
- Huntress — confirm via `Organization.name` (singular = child; parent has `Organizations[]`)
- Cisco Umbrella — confirm via `SystemInfo.Name`
- Datto BCDR — confirm via `SystemInfo.clientCompanyName`
- Acronis Cyber Protect Cloud — confirm via `Account.name`
- Veeam Availability Console — confirm via `BackupRepositories[0].companyName`
- Veeam Service Provider Console — confirm via `BackupJobs[]` on child vs. `Discovered[]` on parent
- Axcient x360 Recover — confirm via `Clients[*].name` (parent) vs. `Devices[]` (child)
- N-able RMM — confirm via `SiteId` on child systems
- ConnectWise Asio — confirm via `Discovered[]` on parent; child has `activityStatus[]`
- Addigy — confirm via `Discovered[]` on parent; child has device-level data

## Recipe structure

Every recipe in this folder follows the canonical structure (see
`templates/recipe-skeleton.md`):

1. **Frontmatter** — `name`, `description`, `compatibility`, `personas`, `output_formats`.
2. **Customize for your MSP** — the YAML block the MSP edits before first use.
3. **When to use** — trigger phrases, cadence, persona fit.
4. **Inputs** — environment ID, system ID, reporting period.
5. **Locating the right system** — keyword + parent/child confirmation.
6. **Liongard data sources** — Asset Inventory First, then per-vendor data.
7. **Metrics and queries** — JMESPath patterns the agent runs.
8. **Insights & recommendations** — generation patterns + SLA-driven thresholds.
9. **Data gaps & coverage notes** — what Liongard doesn't see.
10. **Output format** — Markdown, Word, PowerPoint, or Excel.
11. **Verification log** — the agent appends every query it ran.

## References

- `reference/inspector-aliases.md` — translate user shorthand (S1, KB4, M365,
  Entra, etc.) to the right inspector and API keyword.
- `reference/asset-fields.md` — the complete field map for the reconciled
  `liongard_device` / `liongard_identity` / `liongard_domain` records, with
  PBR-pattern library.
- `templates/recipe-skeleton.md` — the canonical structure for new recipes.

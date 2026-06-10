---
name: single-system-datto-networking
description: >
  Use this skill when the user wants a Datto Networking assessment for a
  single account — network/site inventory, node health, firmware currency,
  and user access audit. Trigger phrases: "Datto Networking health check",
  "how many nodes are down in Datto Networking", "firmware audit for Datto
  Networking", "Datto Networking user access review", "which Datto networks
  have down gateway nodes", "network node count for <customer>", "Datto
  Networking site inventory". Produces a network health and access report
  using live Liongard data. Best for NOC, TAM, and vCIO/Account Manager.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_launchpoint, liongard_metric, liongard_timeline"
personas: [noc, technical-alignment-manager, vcio-account-manager]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  - metrics:datto-networking-inspector:api-only-user-count
  - metrics:datto-networking-inspector:legacy-network-count
  - metrics:datto-networking-inspector:network-count
  - metrics:datto-networking-inspector:network-inventory
  - metrics:datto-networking-inspector:networks-with-down-gateway-count
  - metrics:datto-networking-inspector:total-node-count
  - metrics:datto-networking-inspector:user-count
  - metrics:datto-networking-inspector:user-inventory
---

# Single-System Analysis — Datto Networking

> **Inspector:** `datto-networking-inspector` (ID 79). Network category.
> **Parent inspector — one system per Datto Networking account.** Surfaces
> all managed networks/sites and users for that account. Node-level device
> details (MAC, IP, serial) are **not** in this parent dataprint; they
> appear in child systems if Datto Networking spawns per-network children.
>
> **References:** `reference/inspector-aliases.md` (Datto Networking,
> Datto SD-WAN). Pairs with `datto-rmm.md` for full Datto infrastructure
> coverage; pairs with domain-assessment `domains/network.md` for the
> network device health narrative.


---

## Customize for your MSP

Edit these knobs before first use. Re-edit when your standards change. The
agent reads this block and adapts every downstream output.

```yaml
output:
  format: markdown
  filename: "<customer>-datto-networking-<date>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  network_inventory: "Network & Site Inventory"
  node_health: "Node Health"
  firmware_currency: "Firmware Currency"
  user_access: "User & Access Audit"
  insights: "Key Insights"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"
  appendix: "Appendix — Methodology"

audience:
  tone: "balanced"           # technical | balanced | executive
  reading_level: "manager"   # engineer | manager | executive

slas:
  firmware_age_check: true             # flag any per-network firmware version older than
                                       # the newest version seen across all networks
  down_nodes_max: 0                    # any network with down_gateway > 0 or
                                       # down_repeater > 0 is flagged Critical
  api_only_users_flagged: true         # any api_only=true user triggers a review flag
  flag_legacy_networks: true           # any network with is_legacy=true triggers a flag
  inspector_lastseen_days_max: 7       # inherits from config/msp-config.yaml default

inspectors_in_scope:
  - datto-networking-inspector

naming:
  client_term: "Client"
  environment_term: "Environment"
  site_term: "Site"

qa:
  # See reference/qa-retry-pattern.md for the full QA + manual-verification spec.
  retry_on_null: true
  retry_on_empty_array: false
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: false
  manual_verification_section_required: true
```

---

## When to use

- "Datto Networking health check for <customer>"
- "How many nodes are down in Datto Networking?"
- "Firmware audit for Datto Networking"
- "Datto Networking user access review"
- "Which Datto networks have down gateway nodes?"
- "Network node count for <customer>"
- "Datto Networking site inventory"
- "Is the firmware up to date on Datto Networking?"
- On-demand when a Datto Networking node down alert fires

Cadence: monthly as part of network health review; on-demand when a node
down alert fires or before a firmware upgrade planning session.

Personas:
- **NOC** (primary — node down triage, firmware currency)
- **TAM** (alignment — firmware drift detection, legacy network remediation)
- **vCIO / Account Manager** (QBR — network infrastructure health summary,
  node count delta, upgrade planning)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` → match by customer name |
| System ID (Datto Networking parent system) | Yes — one per recipe run | `liongard_launchpoint LIST inspectorId=79 environmentId=<ENV_ID>` |
| Optional: focus area | No | User prompt — e.g., "focus on networks with down nodes only" |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_launchpoint LIST inspectorId=79 environmentId=<ENV_ID>
```


### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

Check `lastSeen` for the Datto Networking system. If older than
`slas.inspector_lastseen_days_max` (default 7), flag as stale — node health
and firmware data may be out of date. Node down events can change within
hours; treat stale data more aggressively than a slower-changing inspector
like domain registration.

### Step 3 — Network/site inventory

Pull the full network list using `liongard_metric GENERATE_AND_EVALUATE` with
the VALIDATED paths below.

```
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  jmesPath="<path>"

# ── VALIDATED fields (confirmed from System A (dev environment)) ──────────

#   length(Networks)
#     (integer — total number of managed networks/sites in this account)

#   sum(Networks[].node_count)
#     (integer — total node count across all networks)

#   Networks[].{name: name,
#               networkgroup_name: networkgroup_name,
#               is_legacy: is_legacy,
#               node_count: node_count,
#               new_nodes: new_nodes,
#               down_gateway: down_gateway,
#               down_repeater: down_repeater,
#               latest_firmware_version: latest_firmware_version,
#               latest_firmware_version_full: latest_firmware_version_full,
#               oldest_firmware_version: oldest_firmware_version,
#               spare_nodes: spare_nodes}
#
#   Field shapes:
#     name                      — string (network/site display name)
#     networkgroup_name         — string (site group / customer grouping)
#     is_legacy                 — boolean (true = legacy platform; see Insights)
#     node_count                — integer
#     new_nodes                 — integer (nodes recently added; 0 = none pending)
#     down_gateway              — integer (gateway nodes currently down)
#     down_repeater             — integer (repeater nodes currently down)
#     latest_firmware_version   — string (e.g. "7.0.22-fe4a1a548d80660b0559a548b");
#                                  empty string when network has no nodes
#     latest_firmware_version_full — integer (e.g. 70022000 — numeric for comparison)
#     oldest_firmware_version   — string (lowest firmware version in this network)
#     spare_nodes               — integer
```

> **Scrub note:** Do not write concrete version strings, node counts, or
> network names from live data into this recipe. Use shape annotations
> (`<integer>`, `<string>`, `<boolean>`) only.

### Step 4 — Node health

Using the `Networks[]` array from Step 3, evaluate:

```
# Count networks with any down gateway node
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  jmesPath="length(Networks[?down_gateway > `0`])"
  # → integer (VALIDATED)

# Count networks with any down repeater node
#   Client-side filter: Networks[?down_repeater > `0`]
#   → integer (VALIDATED via Networks[] array)
```

Flag any network where `down_gateway > 0` or `down_repeater > 0`. Per SLA
`down_nodes_max: 0` — any down node is Critical.

Flag any network where `new_nodes > 0` for review: new nodes may be
unapproved hardware added without a change record.

### Step 5 — Firmware currency

Using the `latest_firmware_version_full` integer field (numeric, suitable
for comparison), compute the maximum version across all networks. Any network
whose `latest_firmware_version_full` is less than the maximum is running an
older firmware build.

```
# Maximum firmware version across all networks (client-side derived)
#   max(Networks[].latest_firmware_version_full)
#   → integer (VALIDATED via Networks[] array)

# Networks behind the newest version
#   Networks[?latest_firmware_version_full < <max_version>]
#   → filtered array (VALIDATED via Networks[] array)
```

> **Note on empty firmware fields:** `latest_firmware_version` is an empty
> string when a network has no nodes. Exclude networks with `node_count == 0`
> before computing firmware drift.

Flag any network where `is_legacy == true` — legacy networks run on the
older Datto Networking platform and may not receive current firmware updates.

### Step 6 — User / access audit

```
liongard_metric GENERATE_AND_EVALUATE environmentId=<ENV_ID> systemId=<SYS_ID>
  jmesPath="<path>"

# ── VALIDATED fields (confirmed from System A (dev environment)) ──────────

#   length(Users)
#     (integer — total users with Datto Networking account access)

#   Users[].{name: name, email: email, role_id: role_id,
#             verified: verified, api_only: api_only}
#
#   Field shapes:
#     name      — string (can be null for service/API accounts)
#     email     — string
#     role_id   — integer (1 = admin; confirm other role IDs from Datto portal)
#     verified  — ISO timestamp string (when the user verified their account;
#                  null if never verified)
#     api_only  — boolean (true = this account is a service credential, not a
#                  human user)
```

Evaluate:
- Flag any `api_only == true` user per SLA `api_only_users_flagged: true`.
  Confirm each is a documented, legitimate service account.
- Flag any user with `verified == null` — unverified accounts have never
  completed account setup and should be removed or re-invited.
- Review users with `role_id == 1` (admin) — confirm the admin list matches
  expected privileged users.
- Flag any user with `name == null` — service accounts without a display name
  are difficult to audit; ensure they have documented ownership.

### Step 7 — QA pass + render

Run the QA pass per `reference/qa-retry-pattern.md` before rendering. This
recipe's QA pass focuses on:

1. **Retry persistent nulls** — metric calls for Networks[] or Users[] may
   miss on first call if the inspector is mid-cycle.
2. **Flag stale inspectors** (Step 2) — especially important for node health
   data which can change hourly.
3. **No cross-tool divergence** — this recipe uses only per-inspector metrics
   (no asset-inventory cross-check for network nodes); note this limitation
   in the data gaps section.
4. **Proposed-metric gaps** — none for this recipe; all paths are VALIDATED.

Render per `output.format`.

---

## QA & Manual Verification

Before rendering the report, run the QA pass per
`reference/qa-retry-pattern.md`:

1. **Retry persistent nulls.** For every metric call that returned null in
   Steps 3–6, re-run up to `qa.retry_attempts` times with
   `qa.retry_delay_seconds` between attempts.

2. **Flag stale inspectors.** Compare `lastSeen` against
   `qa.flag_inspector_lastseen_threshold_days`. Add stale systems to the
   manual-verification list with a note that node health data may be
   out of date.

3. **Cross-tool divergence check.** Not applicable for this recipe — Datto
   Networking node data is not currently in the reconciled `liongard_device`
   inventory. Record this as a single-source-visibility note in the data
   gaps section.

4. **Known data gaps.** None — all paths in this recipe are
   VALIDATED. If new paths are added in future, list them here.

5. **Render the Manual Verification appendix** in the deliverable
   (mandatory: `qa.manual_verification_section_required: true`).

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` (partner QA matrix) | ✅ | Covers network hardware inventory (node count, site topology) and firmware currency questions from the onboarding intake matrix |
| CIS Controls v8.1 mapping | ✅ | CIS 1.1 — network asset inventory (all managed nodes via `Networks[].node_count`); CIS 2.2 — software/firmware inventory (`latest_firmware_version_full`); CIS 4.1 — configuration management (firmware drift detection across networks); CIS 12.2 — network boundary defense (gateway node status); CIS 5.1 — account inventory (`Users[]`) |
| Cyber-insurance domain files | ✅ | `domains/network.md` — network device health and firmware currency; `domains/auth.md` — user access audit (who holds Datto Networking account access, admin role audit, service account review) |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this recipe for the network infrastructure section; node-count delta and firmware currency appear as operational findings; legacy network flag feeds the roadmap section |

---

## Insights & recommendations — generation patterns


| Pattern | Trigger | Recommendation template |
|---|---|---|
| Down gateway node | `down_gateway > 0` on any network | "URGENT: Gateway node down at <name>. Check physical connectivity and power. If hardware failure, open Datto support case." |
| Down repeater node | `down_repeater > 0` on any network | "Repeater node down on network <name>. Check power and mesh connectivity. May degrade wireless coverage in that area." |
| Firmware version drift | `latest_firmware_version_full` < max across networks | "Network <name> is running firmware <old-version-string> while the newest version in this account is <new-version-string>. Schedule a maintenance window for the upgrade." |
| Legacy network | `is_legacy == true` | "Network <name> is flagged as a legacy Datto Networking site. Evaluate migration to the current platform before legacy firmware support ends." |
| New nodes pending | `new_nodes > 0` | "Network <name> has <N> new node(s) pending provisioning. Confirm these are authorized additions — reject if unrecognized." |
| API-only user | `api_only == true` | "API-only account <email> (role_id <N>) is present. Confirm this is a documented service credential with a named owner. Rotate credentials if ownership is unclear." |
| Unverified user | `verified == null` | "User <email> has never verified their Datto Networking account. Remove the invitation or re-invite with a fresh link." |
| Admin account count | `role_id == 1` | "Review the <N> admin account(s) in this Datto Networking account. Confirm each maps to a current employee or documented service role." |
| Null-name user | `name == null` | "Account <email> has no display name. Ensure this is a documented service account; add a descriptive name in the Datto Networking portal." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Node-level device details (MAC, IP, serial number) | Not in parent dataprint | Datto Networking portal → per-network device view; or child system if Datto Networking spawns per-network child inspectors |
| Individual device diagnostics (signal strength, connection type) | Not in parent dataprint | Datto Networking portal on-demand; or on-device agent |
| Node-level firmware version (per device, not per network) | Not in parent dataprint — `latest_firmware_version` is per-network | Datto Networking portal |
| Historical node up/down events | Not surfaced in static dataprint | `liongard_timeline` change events; Datto Networking event log |
| Datto Networking nodes in `liongard_device` inventory | Not currently reconciled — Datto Networking nodes do not appear in the cross-inspector device asset record | Single-source; no cross-check available |

> **Coverage gap — no cross-inspector device reconciliation.** Because Datto
> Networking nodes are not currently in the `liongard_device` reconciled
> inventory, this recipe cannot cross-check node count against the asset
> record. Surface this as a single-source-visibility note in the Manual
> Verification appendix and recommend confirming the node list in the Datto
> Networking portal when accuracy is critical.

---

## Output formats

The agent picks the format from `output.format` in the customization block.

| Format | Best for |
|---|---|
| `markdown` | Working draft (NOC triage, TAM alignment review) |
| `word` | Customer-facing network health letter |
| `pptx` | QBR network infrastructure slide (node count, firmware currency, action items) |
| `xlsx` | Internal per-network + per-user audit table |

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | query=<customer> | array<environment> | ok |
| 1 | liongard_launchpoint LIST | inspectorId=79 envId=<ENV_ID> | array<system> | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3 | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath="length(Networks)" | integer | VALIDATED |
| 3 | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath="sum(Networks[].node_count)" | integer | VALIDATED |
| 3 | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath="Networks[].{name: name, networkgroup_name: networkgroup_name, is_legacy: is_legacy, node_count: node_count, new_nodes: new_nodes, down_gateway: down_gateway, down_repeater: down_repeater, latest_firmware_version: latest_firmware_version, latest_firmware_version_full: latest_firmware_version_full, oldest_firmware_version: oldest_firmware_version, spare_nodes: spare_nodes}" | array<network-object> | VALIDATED |
| 4 | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath="length(Networks[?down_gateway > \`0\`])" | integer | VALIDATED |
| 4 | (client-side filter) | Networks[?down_repeater > `0`] | filtered array | VALIDATED |
| 5 | (client-side derived) | max(Networks[].latest_firmware_version_full) | integer | VALIDATED |
| 5 | (client-side filter) | Networks[?is_legacy == `true`] | filtered array | VALIDATED |
| 6 | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath="length(Users)" | integer | VALIDATED |
| 6 | liongard_metric GENERATE_AND_EVALUATE | envId=<ENV_ID> sysId=<SYS_ID> jmesPath="Users[].{name: name, email: email, role_id: role_id, verified: verified, api_only: api_only}" | array<user-object> | VALIDATED |
| 7 | QA pass | per reference/qa-retry-pattern.md | varies | ok |
| 7 | render | per output.format | <artifact path> | ok |
```

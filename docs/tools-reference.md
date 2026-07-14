# Tools reference

This page documents the native `liongard_*` tools exposed by the Liongard MCP
at `POST /api/mcp`. These tools are always available when your token
authenticates successfully; the server also merges in any external MCP tools
your tenant has configured.

For the canonical, live schemas, your MCP client can call `tools/list` after
connecting.

Many native tools support `responseFormat: "json" | "toon"` where advertised in
their live schema. Use `json` by default; use `toon` only when a compact
token-efficient representation is helpful.

---

## `liongard_environment`

Read and search Liongard environments (the "customer" or "tenant" concept in
your MSP hierarchy).

Common operations:

- `LIST` — list all environments your token can see, with optional filter /
  keyword search (use `searchMode: "keyword"` for fuzzy name search).
- `GET` — fetch a single environment by ID.
- `COUNT` — return a count only.

Tips:

- Use this as the **first** tool call when a user references an environment by
  name — resolve the name to an `environmentId` before calling any other tool.

---

## `liongard_agents`

Read Liongard agents installed across a tenant. Agents can be Windows, Linux, or
Mac services and may be customer-owned or Liongard-managed.

Common operations:

- `LIST` — retrieve agents with filters and pagination.
- `GET` — retrieve one agent by ID.
- `COUNT` — answer existence or exact-count questions without loading records.

Useful filters:

- `environmentId`
- `platform` (`windows`, `linux`, `mac`)
- `type` (`managed-hosted`, `managed-ondemand`, `customer-on-prem`,
  `customer-managed`, `customer-endpoint`)
- `suspended`
- `managed: false` to show customer-owned/on-prem agents only.

Tips:

- For "are any agents offline/suspended/outdated?" questions, start with
  `COUNT` when the filter exists, then `LIST` only if the user wants examples.
- Do not use `type: "customer-on-prem"` as a synonym for "my agents"; use
  `managed: false` unless the user explicitly asks for that agent type.

---

## `liongard_alert`

Query actionable alerts across the tenant (or within a scoped environment).

Common operations:

- `LIST` — paginated list of alerts with filters on status, severity, system,
  date range, and more.
- `GET` — single alert by ID.
- `COUNT` — count alerts matching a filter.

Tips:

- For "which alerts are open?" questions, filter by `Status = "Open"` and sort
  by severity / created date.
- Pagination is critical here — alert backlogs can be large. The tool response
  includes a `Pagination` block; if you need exact totals, keep paging.

---

## `liongard_detection`

Query change detections — specific changes the Liongard inspectors have
identified across dataprints.

Common operations:

- `LIST` — recent detections, filterable by environment, system, or time window.
- `GET` — single detection by ID.

Tips:

- Use `liongard_detection` when the user asks "what changed recently" or "what
  detections fired on this system". Use `liongard_timeline` when they want the
  full dataprint history.

---

## `liongard_launchpoint` (also covers systems)

The unified tool for **launchpoints and systems**. Every system in Liongard
has exactly one backing launchpoint, so this tool is the single source of
truth for both.

Common operations:

- `LIST` — list launchpoints / systems, with filters:
  - `systemType` — inspector alias (for example `Microsoft 365`).
  - `systemCategory` — inspector category (for example `Productivity`).
  - `configSearch` — search inside system configuration.
  - `environmentId` — scope to one environment.
- `GET` — by `id` or `systemId`.
- `GET_OVERVIEW` — structured overview of a system's dataprint shape.
- `LIST_TYPES` — enumerate system types and categories in scope, with counts.
- `COUNT` — count launchpoints matching a filter.

Tips:

- Start with `LIST_TYPES` when you want to know **what kinds of systems** are
  present before drilling in.
- For "give me an overview of `<system name>`", call `GET_OVERVIEW` after
  resolving the ID.

---

## `liongard_device` / `liongard_identity` / `liongard_domain`

The reconciled asset inventory. Each tool returns one record per real-world
entity, joined across every inspector that observed it:

- `liongard_device` — devices (hostname, OS, serial, IP/MAC, AV/EDR, warranty,
  EOL, virtualization).
- `liongard_identity` — identities (email, MFA status, privileged, enabled,
  account activity, license SKUs).
- `liongard_domain` — domains (registrar, expiration, DMARC health, IP/ASN).

> The legacy `liongard_asset` tool has been removed from the catalog — always
> call the three dedicated tools directly.

Common operations (all three):

- `LIST` — paginated list with server-side filters (`hostname`, `mfaStatus`,
  `dmarcHealth`, `maxDaysTillExpiration`, etc.). Omit `environmentId` to search
  across all accessible environments.
- `GET` — single record by UUID.
- `COUNT` — exact totals without paging; pass `includeStatusCounts: true` for a
  bucketed breakdown (for example MFA coverage in one call).

Tips:

- MFA summaries: `liongard_identity COUNT mfaStatus="NO" enabled=true
  includeStatusCounts=true`.
- For category counts (M365 users, Windows workstations/servers, macOS) prefer
  `liongard_cyber_risk_dashboard`.

---

## `liongard_metric`

Evaluate metric values against systems.

Common operations:

- `LIST` — metric metadata (definitions, templates).
- `EVALUATE` — run a metric against one or more systems and return the
  resulting values.

Tips:

- Use `liongard_cyber_risk_dashboard` for pre-rolled cyber-risk coverage; use
  `liongard_metric EVALUATE` when you want the raw metric values behind a
  custom question.

---

## `liongard_cyber_risk_dashboard`

Cyber-risk coverage roll-ups across an environment or the whole tenant. Covers
five pillars:

- MFA coverage
- EDR coverage
- Encryption coverage
- Firewall coverage
- TLS/SSL coverage

Common operations:

- Per-pillar summary queries (identified by query identifiers that the tool
  documents in its `inputSchema`).

Tips:

- This tool is the fastest path to "how compliant is customer X?". The
  `compliance-check` prompt wraps it with a ready-made instruction block.

---

## `liongard_timeline`

Walk the dataprint timeline for a system — each inspection run produces a new
timeline entry.

Common operations:

- `LIST` — recent timeline entries for a system.
- `GET` — a specific timeline entry.

Tips:

- Each timeline row carries `systemDetailID`; use that (not the row `id`) when
  you want to pull the underlying dataprint.

---

## `liongard_report`

Retrieve Liongard reports (the same reports available in the UI). Reports are
generated summaries for review and communication — they are not authoritative
sources of current configuration state.

Common operations:

- `LIST` — search reports by keyword, optionally scoped with `environmentIds`.
- `GET` — retrieve one report by `id` or exact `name`. Use
  `detail: "summary"` (the default) first; pass `detail: "full"` only when you
  need the per-system metric output.

Tips:

- Report generation is not exposed over MCP; use the Liongard UI to create or
  schedule reports, then retrieve them here.
- For authoritative current values, drill into `liongard_launchpoint`,
  `liongard_device` / `liongard_identity` / `liongard_domain`, or
  `liongard_metric` instead of quoting report output.

---

## `liongard_events`

Query real-time events — system state changes and notable occurrences captured
during inspection runs. Each event is tied to a launchpoint, system,
environment, and inspection.

Common operations:

- `LIST` — paginated events with filters (`environmentId` / `environmentIds`,
  `launchpointId`, `eventType`, `title`, `createdAfter` / `createdBefore`).
- `GET` — a single event by UUID.
- `COUNT` — total events matching a filter, without record data.

Tips:

- For yes/no or existence questions ("Did anything happen overnight?"), use
  `COUNT` first; only `LIST` when the user wants to see the rows.
- Prefer `liongard_alert` for rule-triggered actionable conditions and
  `liongard_detection` for raw per-inspector change detections; use
  `liongard_events` for the raw "what happened?" stream.
- Date filters must be ISO 8601 strings (for example `2026-01-01T00:00:00Z`);
  always narrow scope on large MSP datasets.

---

## `liongard_query`

High-level grounded question-answering. You describe the question in natural
language and pass any conversation history; the tool uses the other
`liongard_*` tools and relevant Liongard data to produce a grounded answer.

Best for:

- Questions that span multiple tools or entities.
- When you don't want to orchestrate tool calls yourself.
- Follow-up questions that reference prior conversation context.

---

## `liongard_navigate`

A tiny, read-only navigator that helps agents discover the full tool catalog
progressively. This is mainly useful for **gateway clients** that want to
minimize `tools/list` size.

Call it with:

- No arguments — returns a curated `domain-menu` (environments, alerts,
  detections, metrics, timeline, launchpoints, inventory, reports,
  cyber-risk-dashboard, query).
- `{ "domain": "<domain or tool name>" }` — returns a `tool-detail` block with
  the input schema and suggested operations for that tool.

Clients that opt into **compact mode** during `initialize` get only
`liongard_navigate` in `tools/list`; `tools/call` still works for every tool by
canonical name.

---

## `_meta.liongard` on every tool

Every native tool includes additive metadata under `tool._meta.liongard` on
`tools/list`:

- `origin` — `"native"` or `"external"`.
- `stableId` — stable identifier (gateways should key bindings on this, not
  `name`).
- `category` — UI/policy grouping (`tenant-scope`, `configuration`, `inventory`,
  `security`, `change-tracking`, `analytics`, `operational`, `reporting`,
  `reasoning`, `navigation`).
- `domain` — matches the `liongard_navigate` domain menu.
- `tokenCostHint` — `"low" | "medium" | "high" | "variable"`.

Clients that don't understand these fields can safely ignore them.

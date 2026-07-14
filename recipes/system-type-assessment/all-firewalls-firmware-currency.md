---
name: system-type-all-firewalls-firmware-currency
description: >
  Use this skill when the user wants to inventory every firewall in an
  environment, read each device's model and installed firmware/OS version
  from Liongard, compare those against the most current firmware available
  online, and produce a prioritized list of firewalls that are outdated and
  need upgrading or replacing. Trigger phrases: "go look at every firewall
  at <customer>, find the ones running outdated firmware we need to upgrade",
  "firewall firmware currency report", "which firewalls need upgrading",
  "firmware upgrade list for the firewalls", "are any firewalls behind on
  firmware", "network inventory firmware report", "firewall patch / version
  audit". Iterates every deployed firewall (SonicWall, FortiGate, Cisco ASA,
  Sophos XG, Cisco Meraki MX, WatchGuard, Palo Alto, Barracuda, pfSense,
  Sophos SG), reads model + firmware from the validated per-vendor metrics,
  performs a LIVE web lookup of the current GA firmware + end-of-life status
  for each model, and rolls up to one upgrade-target report.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_launchpoint, liongard_metric, liongard_device. Requires live web access (WebSearch / web_fetch) for the firmware-currency comparison."
personas: [noc, technical-alignment-manager, vcio-account-manager, soc, executive]
output_formats: [html, xlsx, word, markdown]
primitives:
  - metrics:sonicwall:model
  - metrics:sonicwall:firmware-version
  - metrics:fortinet-fortigate:model
  - metrics:fortinet-fortigate:firmware-version
  - metrics:cisco-asa:model
  - metrics:cisco-asa:software-version
  - metrics:palo-alto-panos:software-version
  - metrics:watchguard:model
  - metrics:watchguard:firmware-version
  - metrics:cisco-meraki:hardware-list
  - metrics:cisco-meraki:device-firmware-summary
---

# System-Type Assessment — Firewall Firmware Currency & Upgrade Targets

> **What this produces.** A single upgrade-target report: every firewall in
> the environment, its model and installed firmware, the current firmware
> available online for that model, and a verdict — **Current / Behind /
> Firmware-EOL / Hardware-EOL / Unknown** — with a prioritized list of which
> devices to upgrade or replace.
>
> **This recipe reuses, not duplicates, `all-firewalls.md`.** It chains the
> general firewall rollup's Steps 1–3 (discover deployed firewalls + read the
> validated per-vendor model/firmware metrics) and adds the one thing that
> rollup deliberately leaves as an external/manual gap (see
> `all-firewalls.md` Step 3 note and Data Gaps row "Firmware release-date
> lookup ⚠️ external"): a **live web comparison of installed firmware vs. the
> latest GA firmware online**, and the upgrade-target deliverable built from it.
>
> **Inspectors covered** (firewalls only — same set as `all-firewalls.md`):
> - `sonicwall-inspector` (ID 7) — SonicWall (SonicOS 6 + Gen7)
> - `fortinet-fortigate-inspector` (ID 33) — Fortinet FortiGate
> - `cisco-asa-inspector` (ID 22) — Cisco ASA
> - `sophos-firewall-inspector` (ID 28) — Sophos XG / XGS
> - `sophos-sg-inspector` (ID 43) — Sophos SG (legacy UTM)
> - `cisco-meraki-inspector` (ID 3) — Cisco Meraki MX (firewall portion)
> - `watchguard-inspector` (ID 29) — WatchGuard
> - `palo-alto-panos-inspector` (ID 49) — Palo Alto PAN-OS (Beta)
> - `barracuda-firewall-inspector` (ID 52) — Barracuda
> - `pfsense-inspector` (ID 37) — pfSense
>
> **Pairs with:**
> - `recipes/system-type-assessment/all-firewalls.md` — full firewall posture
>   (licensing, WAN exposure, policy count, VPN topology). Run that for the
>   complete fleet review; run **this** when the question is specifically
>   "what firmware are they on and what needs upgrading."
> - `recipes/roadmap-planning/refresh-and-lifecycle-roadmap.md` — feed this
>   recipe's Hardware-EOL findings into the forward-looking refresh calendar.
> - `recipes/single-system-analysis/by-inspector/<vendor>.md` — per-vendor deep dive.
>
> **References:** `reference/inspector-aliases.md` (vendor lookups),
> `reference/asset-fields.md` (`liongard_device` field map),
> `reference/qa-retry-pattern.md` (QA pass).

---

## Customize for your MSP

```yaml
output:
  format: html                 # html | xlsx | word | markdown
                               # html is the default upgrade-target report.
  audience_type: external      # internal | external
                               # external: verification log OMITTED; each vendor row shows
                               #   "Data as of: <inspection date>"; web-lookup date stamped.
  filename: "<customer>-firewall-firmware-currency-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  upgrade_targets: "Upgrade Targets (Action Required)"
  inventory: "Firewall Firmware Inventory"
  eol_hardware: "End-of-Life Hardware"
  methodology: "How Firmware Currency Was Determined"
  data_gaps: "Data Gaps & Coverage Notes"
  manual_verification: "Manual Verification Needed"

audience:
  tone: "balanced"             # technical | balanced | executive
  reading_level: "manager"

slas:
  # Tune to your standards. The agent classifies each firewall against these.
  firmware_behind_minor_ok: true     # a newer patch on the SAME train = 🟡 minor, not 🔴
  firmware_age_months_warn: 12       # installed train older than this → flag Behind
  inspector_lastseen_days_max: 7     # firewall inspector staleness flag
  treat_hardware_eol_as_critical: true

firmware_currency:
  # The "latest firmware" comparison is a LIVE web lookup — it is NOT in the
  # Liongard dataprint. These knobs control how that lookup behaves.
  live_lookup: true                  # web-search/fetch the current GA firmware per model at run time
  require_source_citation: true      # every "latest version" claim must cite the URL it came from
  prefer_vendor_domains: true        # weight results from the vendor's own release-notes/EOL pages
  cache_within_run: true             # look up each unique model once per run, reuse across identical models
  unknown_when_unverifiable: true    # if the latest version can't be confirmed online, verdict = Unknown (never guess)

inspectors_in_scope:
  - sonicwall-inspector
  - fortinet-fortigate-inspector
  - cisco-asa-inspector
  - sophos-firewall-inspector
  - cisco-meraki-inspector
  - watchguard-inspector
  - palo-alto-panos-inspector
  - barracuda-firewall-inspector
  - pfsense-inspector
  - sophos-sg-inspector

reporting_period: { default: "current_state" }

qa:
  retry_on_null: true
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  surface_proposed_metrics: false
  manual_verification_section_required: true
```

---

## When to use

- "Go look at every firewall at <customer>, get the model and firmware of each,
  compare to the current firmware online, and tell me which ones are outdated
  and need upgrading." (the canonical partner request this recipe answers)
- Quarterly firmware hygiene review across a customer's firewall fleet.
- Pre-renewal / budget conversation — pairs Hardware-EOL findings into
  `refresh-and-lifecycle-roadmap.md`.
- Security-driven "are any of our firewalls on a vulnerable / EOL train?" audit.

Cadence: on-demand or quarterly. Persona fit: NOC + TAM (operational upgrade
list), vCIO/AM + Exec (replace-vs-upgrade budget framing), SOC (EOL = risk).

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` → match by name |
| Reporting period | No | Default per customization |

Environment-scoped — no per-system input. The recipe discovers the deployed
firewalls itself.

---

## Liongard data sources

> **Asset Inventory First, Metric Cross-Check.** Use
> `liongard_device LIST category="network"` to confirm *what firewalls exist*
> (including any seen by another inspector but not actively config-inspected —
> a coverage gap), then read model + firmware from the validated per-vendor
> metrics below.

### Step-0 discovery is inherited from `all-firewalls.md`

Run `all-firewalls.md` **Step 1** (`liongard_launchpoint LIST environmentId=<ENV_ID>`,
group by firewall inspector slug) and **Step 2** (`liongard_device LIST
category="network"` cross-check). Do not re-implement them here. This recipe
picks up at firmware extraction.

### Per-vendor model + firmware metrics (the only Liongard fields this recipe needs)

All paths below were confirmed against a live multi-vendor environment
(see Verification Log). Each EVALUATE call needs `systemId` + `environmentId`.

| Vendor | Inspector | Model — JMESPath | Firmware — JMESPath | Status |
|---|---|---|---|---|
| SonicWall | `sonicwall-inspector` (7) | `Version.Model` *(SonicOS 7)* / `System.Model` *(SonicOS 6)* | `Version.FirmwareVersion` *(SonicOS 7)* / `System.FirmwareVersion` *(SonicOS 6)* | VALIDATED |
| FortiGate | `fortinet-fortigate-inspector` (33) | `Firmware.current."platform-id"` | `Firmware.current."version"` | VALIDATED |
| Cisco ASA | `cisco-asa-inspector` (22) | `SystemInfo.Model` | `SystemInfo.CiscoAdaptiveSecurityApplianceSoftwareVersion` | VALIDATED |
| Palo Alto | `palo-alto-panos-inspector` (49) | `SystemInfo.model` | `SystemInfo."sw-version"` | VALIDATED |
| WatchGuard | `watchguard-inspector` (29) | `SystemInfo.Model` | `SystemInfo.Version` | VALIDATED |
| Cisco Meraki (MX) | `cisco-meraki-inspector` (3) | `Networks[].Devices[].model` | `Networks[].Devices[].firmware` | VALIDATED |
| Sophos XG/XGS | `sophos-firewall-inspector` (28) | `SystemInfo.Model` *(if present)* | ⚠️ firmware not reliably in dataprint | SCHEMA_CONFIRMED / gap |
| Sophos SG | `sophos-sg-inspector` (43) | ⚠️ not in dataprint | `utm-version` metric | SCHEMA_CONFIRMED / gap |
| Barracuda | `barracuda-firewall-inspector` (52) | `system-model` metric | `firmware-version` metric | SCHEMA_CONFIRMED |
| pfSense | `pfsense-inspector` (37) | n/a (software firewall) | `SystemInfo.version` *(FLOAT — see gotcha)* | VALIDATED |

> **Field gotchas (confirmed live / from learnings):**
> - **SonicWall path differs by generation.** SonicOS 7 dataprints expose
>   `Version.Model` + `Version.FirmwareVersion` (e.g. `"TZ 400 wireless-AC"`,
>   `"SonicOS Enhanced 6.5.5.1-6n"`); SonicOS 6 uses `System.Model` /
>   `System.FirmwareVersion`. **Try `Version.*` first, fall back to `System.*`.**
>   The catalog primitive (`metrics:sonicwall:firmware-version`) uses the
>   `System.*` path. SonicOS 7 systems also carry
>   `SupportResources.FirmwareLifecycleLink` and `.HardwareLifecycleLink` —
>   use these as authoritative vendor lifecycle URLs when present.
> - **Meraki `model` is lowercase**, and `firmware` is prefixed by product
>   line: `"MX 19.2.4"` (firewall), `"MS 16.8"` (switch), `"MR 31.1.7.1"` (AP).
>   **Filter to the MX device(s)** for the firewall comparison:
>   `Networks[].Devices[?contains(firmware, 'MX')]`. The MS/MR devices belong
>   in `all-network-infrastructure.md`, not here.
> - **pfSense `SystemInfo.version` is a FLOAT**, not a string — don't string-compare.
> - **FortiGate `Firmware.current."version"` is the `vX.Y.Z` build string**;
>   `platform-id` (e.g. `"FG100D"`) is the model used for the EOL lookup.

---

## Workflow

### Step 1 — Discover deployed firewalls
Run `all-firewalls.md` Step 1 + Step 2. Result: a per-vendor list of firewall
systems with `systemId`, `environmentId`, `latestInspectionDate`, `status`,
plus the `liongard_device` network inventory for the coverage-gap cross-check.

### Step 2 — Read model + firmware per firewall
For each firewall system, `liongard_metric EVALUATE` the model + firmware
JMESPath from the table above. Recommended single combined call per system:

```
liongard_metric EVALUATE
  jmesPathQuery="{model: <model-path>, firmware: <firmware-path>}"
  systemId=<SYS_ID> environmentId=<ENV_ID>
```

For SonicWall, request the lifecycle links too:
`{model: Version.Model, firmware: Version.FirmwareVersion, fwLifecycle: SupportResources.FirmwareLifecycleLink}`.

Normalize each firewall to: `{vendor, hostname, model, installed_firmware,
inspection_date, inspector_lastseen, system_id}`.

### Step 3 — LIVE firmware-currency lookup (the new capability)

> ⚠️ **This step uses live web data, not Liongard.** The "latest firmware
> available online" is **not** in the dataprint. The agent must look it up at
> run time and treat the result as point-in-time external intelligence, not a
> Liongard-validated fact.

For each **unique** `(vendor, model)` pair (dedup per `firmware_currency.cache_within_run`):

1. `WebSearch` for the current GA firmware and EOL/lifecycle status, e.g.
   `"<vendor> <model> latest firmware version 2026 release notes end of support"`.
   Weight the vendor's own domain (`firmware_currency.prefer_vendor_domains`).
   For SonicWall, fetch the `FirmwareLifecycleLink` from the dataprint first.
2. If a vendor page is JavaScript-rendered and `web_fetch` returns a shell,
   escalate to the browser tools (see `escalate_unhelpful_web_fetch_to_chrome`).
   **Never** fetch via curl/wget/python — respect the web-content restrictions.
3. Capture three facts with their **source URL**: (a) latest GA firmware for
   that model/train, (b) whether the installed train is still supported, and
   (c) whether the **hardware model** is past end-of-sale / end-of-support.
4. If any of the three can't be confirmed online, set that firewall's verdict
   to **Unknown** and add it to Manual Verification — do **not** guess
   (`firmware_currency.unknown_when_unverifiable: true`).

### Step 4 — Classify each firewall

| Verdict | Condition | Color |
|---|---|---|
| **Current** | Installed firmware == latest GA for the model (or latest on a still-supported LTS train) | 🟢 |
| **Minor behind** | Newer patch exists on the **same** train; train still supported (`firmware_behind_minor_ok`) | 🟡 |
| **Behind** | Installed train is older than the current GA train, hardware still supported | 🟠 |
| **Firmware-EOL** | Installed train is end-of-support but a supported upgrade exists on the same hardware | 🟠 |
| **Hardware-EOL** | Model is past end-of-sale / end-of-support — can't be brought current; replace | 🔴 |
| **Unknown** | Latest version or EOL status could not be confirmed online | ⚪ |

`treat_hardware_eol_as_critical: true` sorts 🔴 to the top of the upgrade list.

### Step 5 — Build the upgrade-target list + QA
Sort: Hardware-EOL → Behind/Firmware-EOL → Minor → Current → Unknown.
For each non-green row, write the recommended action (upgrade to version X, or
replace EOL hardware) with the source URL. Run the QA pass (below).

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| EOL hardware in fleet | any firewall verdict == Hardware-EOL | "**Replace:** <hostname> (<model>) is past vendor end-of-support and cannot run current firmware — plan hardware refresh. Source: <url>." |
| Behind on firmware | verdict == Behind or Firmware-EOL | "**Upgrade:** <hostname> (<model>) runs <installed>; current is <latest>. Schedule a maintenance window. Source: <url>." |
| Known-vulnerable train | latest-version lookup cites a CVE fixed in a newer build | "**Security:** <hostname> is on <installed>, which predates the fix in <latest> (<CVE>). Prioritize. Source: <url>." |
| Minor patch available | verdict == Minor behind | "<hostname> is one patch behind on a supported train — low-risk update at next window." |
| Couldn't verify | verdict == Unknown | "Confirm current firmware for <model> in the vendor portal — automated lookup was inconclusive." |
| Stale inspector | `inspector_lastseen > slas.inspector_lastseen_days_max` | "<hostname> inspector last ran <N> days ago — installed-version reading may be stale; re-run before acting." |

---

## How firmware currency was determined (include in deliverable)

The deliverable must state, in plain language, that installed model + firmware
come from Liongard's last inspection of each device (with the date), and that
the "current firmware" column comes from a **live web lookup at report time**,
with the source link for each claim. This keeps the external data auditable and
sets the right expectation: it is accurate as of the lookup date and should be
re-confirmed in the vendor portal before any change-controlled upgrade.

---

## QA & Manual Verification

Run the QA pass per `reference/qa-retry-pattern.md`:

1. **Retry persistent nulls** on the model/firmware EVALUATE (try the SonicWall
   `System.*` fallback before declaring null).
2. **Flag stale inspectors** (`inspector_lastseen > 7d`) — installed version may
   be out of date relative to reality.
3. **Every "latest version" claim carries a source URL** (`require_source_citation`).
   Uncited claims are not allowed in the deliverable.
4. **Unknown verdicts go to Manual Verification**, never guessed.
5. **Render the Manual Verification appendix.** Typical items: vendors where
   firmware isn't in the dataprint (Sophos XG/SG — confirm in vendor console),
   any Unknown verdict, stale inspectors, HA pairs where only one member is read.
   If empty: "✅ All firewalls verified — no manual checks needed."

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` (partner QA matrix) | ✅ | Addresses the "firewall firmware / version currency" question in the network section |
| CIS Controls (v8.1) mapping | ✅ | 4.1 (secure configuration), 7.x (continuous vuln mgmt — EOL/firmware), 12.1 (network infra current) |
| Cyber-insurance domain files | ✅ | `cyber-insurance/domains/network.md` — EOL/unsupported firewall firmware is a common carrier question |
| QBR / quarterly-business-review | ✅ | QBR Step 8 can chain this recipe for the firewall-firmware slide |

No new Liongard metric is required — this recipe reuses existing validated
model/firmware primitives and sources "latest version" externally by design.

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Latest GA firmware per model | ⚠️ external (by design) | Live web lookup at run time; cite source URL |
| Hardware end-of-sale / end-of-support date | ⚠️ external | Vendor lifecycle page (SonicWall provides `HardwareLifecycleLink` in dataprint) |
| Sophos XG/XGS + SG firmware | ⚠️ not reliably in dataprint | Vendor console — Manual Verification |
| Firmware release date | ❌ not in dataprint | Derived from the web lookup, not Liongard |
| CVE applicability to a build | ⚠️ external | NVD / vendor PSIRT, surfaced during the web lookup |

A gap is a visibility limitation (🔍 REVIEW), not a non-compliance.

---

## Output formats

- **HTML (default)** — upgrade-target report: KPI band (total / current /
  behind / EOL), an "Upgrade Targets" table sorted by severity with source
  links, a full inventory table, and a methodology note. Self-contained, MSP-branded.
- **xlsx** — one row per firewall with normalized columns (vendor, hostname,
  model, installed, latest, verdict, action, source) for evidence packs.
- **word** — executive replace-vs-upgrade memo (good for vCIO/budget conversations).

Deliverables write to `outputs/environments/<customer-slug>/`.

---

## Verification log (internal only — omit for external deliverables)

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_launchpoint LIST | envId=<ENV_ID> systemCategory=network | array<system> | ok |
| 2 | liongard_device LIST | envId=<ENV_ID> category=network | array<device> | ok |
| 3 | liongard_metric EVALUATE | {model,firmware} sysId=<SYS_ID> envId=<ENV_ID> | {model:str, firmware:str} | ok per vendor |
| 4 | WebSearch / web_fetch | "<vendor> <model> latest firmware" | external text + source URL | ok |
| 5 | (QA) retry nulls / stale check | per qa-retry-pattern.md | varies | ok |
```

**Paths confirmed live (anonymized):** validated against System A (multi-vendor
dev environment, inspected ~Q2 2026): SonicWall `Version.Model` +
`Version.FirmwareVersion` (TZ-series, SonicOS 6.5.5 train) — `System.*` returned
null on the SonicOS 7 dataprint; FortiGate `Firmware.current."platform-id"` +
`."version"` (FG-100D); Cisco ASA `SystemInfo.Model` +
`...SoftwareVersion` (ASA5508); Palo Alto `SystemInfo.model` +
`SystemInfo."sw-version"` (PA-440); WatchGuard `SystemInfo.Model` +
`SystemInfo.Version` (Firebox T-series); Meraki `Networks[].Devices[?contains(firmware,'MX')].{model,firmware}` (MX85).

---

## Notes for authors

- **Strip evaluated examples** from the recipe (scrub policy). Concrete device
  values live only in `outputs/` deliverables.
- This recipe intentionally depends on **live external data** for the "latest
  firmware" column. That is a feature, not a gap — but the deliverable must
  always cite sources and stamp the lookup date.
- Inspector slugs / IDs match `reference/inspector-name-system-id-mapping.xlsx`.
- Keep this recipe focused on firmware currency. General firewall posture
  (licensing, WAN exposure, policy, VPN) lives in `all-firewalls.md`.

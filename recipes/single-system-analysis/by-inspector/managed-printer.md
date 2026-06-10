---
name: single-system-managed-printer
description: >
  Use this skill when the user wants a single-device analysis of a managed
  network printer — consumable levels, paper tray status, lifetime page count,
  active alerts, network interface health, and firmware/identity details.
  Trigger phrases: "managed printer review for <customer>", "printer toner
  levels", "printer consumable status", "is the printer online?", "printer
  health check", "print volume report", "printer PBR", "check printer
  consumables". This inspector uses SNMP to poll printers directly — no agent
  required, one system per physical printer. Beta inspector — some fields may
  be SCHEMA_CONFIRMED on printers that do not fully expose SNMP MIB-II / Printer MIB
  data.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_launchpoint, liongard_metric"
personas: [noc, technical-alignment-manager, accounting-finance]
output_formats: [markdown, word, xlsx]
primitives:
  - metrics:managed-printer-inspector:alert-critical-events
  - metrics:managed-printer-inspector:consumables-low
  - metrics:managed-printer-inspector:marker-life-count
  - metrics:managed-printer-inspector:network-interface-ip
  - metrics:managed-printer-inspector:printer-serial-number
  - metrics:managed-printer-inspector:sys-name
  - metrics:managed-printer-inspector:system-uptime
---

# Single-System Analysis — Managed Printer

> **Inspector:** `managed-printer-inspector` (ID 89). Beta inspector. **One
> system per physical network printer.** Uses SNMP (MIB-II + RFC 3805 Printer
> MIB) to collect identity, consumable levels, tray status, lifetime page
> counts, and active alerts. No Liongard agent required — connects directly
> to the printer over the network.
>
> **Beta notice:** Coverage varies by printer model and firmware. Printers that
> implement the Printer MIB fully (HP LaserJet, many Ricoh, Xerox, Lexmark
> models) return rich consumable and alert data. Consumer-grade or minimally-
> configured printers may return null/empty for many fields — label those paths
> SCHEMA_CONFIRMED in your verification log. Always check
> `prtAlertTable` for real-time error state before concluding a tray or
> consumable path is absent.
>
> **IP address gotcha:** `SystemInfo.Address` may return the loopback IP
> (`127.0.0.1`) on some models. Use
> `ifTable[?ipAdEntAddr != '127.0.0.1'].ipAdEntAddr | [0]` for the actual
> network interface IP. Validated live.
>
> **References:** `reference/inspector-aliases.md` (Printer, MFP, HP LaserJet,
> Ricoh, Xerox, Lexmark). Pairs with the RMM single-system recipe if the
> printer is also monitored via SNMP trap in NinjaOne / ConnectWise.

---

## Customize for your MSP

```yaml
output:
  format: markdown              # markdown | word | xlsx
  filename: "<customer>-managed-printer-<printer-name>-<YYYY-MM-DD>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Printer Health Summary"
  identity: "Printer Identity & Network"
  consumables: "Consumable Levels"
  paper_trays: "Paper Tray Status"
  alerts: "Active Alerts"
  page_counts: "Page Count & Usage"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"              # technical | balanced | executive
  reading_level: "manager"

slas:
  consumable_low_pct: 20        # flag consumables below this percentage
  consumable_critical_pct: 10   # escalate consumables at or below this percentage
  inspector_lastseen_days_max: 7

naming:
  client_term: "Client"
  environment_term: "Environment"

qa:
  retry_on_null: true
  retry_on_empty_array: false
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: false
```

---

## When to use

- **NOC daily check** — consumable alerts, paper-empty alerts, device offline.
- **Monthly health report** — page volume trend, toner burn rate estimate,
  projected replacement date.
- **Procurement planning** — per-device consumable levels to drive supply
  orders.
- **Asset register** — confirm printer model, serial, IP, and location are
  correct in the CMDB.

---

## Inputs

The user must supply (or the agent must discover):

| Input | How to obtain |
|---|---|
| `environmentId` | `liongard_environment LIST` — find the customer's env ID |
| `systemId` | `liongard_launchpoint LIST inspectorId=89 environmentId=<ENV>` — pick the system with the most recent `latestInspectionDate` |

---

## Workflow

### Step 1 — Confirm inspection freshness

```
liongard_launchpoint LIST
  inspectorId=89
  environmentId=<ENV_ID>
  fields=["id", "system", "environment", "latestInspectionDate", "status"]
```

If `status` is "Timeout" or "Agent Issue", the dataprint may be stale.
Document `latestInspectionDate` in the verification log. If the last
inspection is older than `slas.inspector_lastseen_days_max` days, flag it
in the **Manual verification** appendix — confirm the printer is still online
and reachable via SNMP before presenting numbers.

---

### Step 2 — Printer identity & network

```
liongard_metric EVALUATE
  jmesPathQuery="SystemInfo.{name: sysName, contact: sysContact,
    location: sysLocation, uptime: sysUpTime, serial: printerSerialNumber,
    vendor: vendor, loopbackIp: Address}"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

Then retrieve the real network interface:

```
liongard_metric EVALUATE
  jmesPathQuery="ifTable[?ipAdEntAddr != '127.0.0.1'].{ip: ipAdEntAddr,
    mask: ipAdEntNetMask, iface: ifDescr, speedMbps: ifSpeedMBps_r,
    adminStatus: ifAdminStatus, operStatus: ifOperStatus}"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

**Gotcha — `SystemInfo.Address`:** Returns the loopback IP (`127.0.0.1`) on
HP LaserJet and other models because the SNMP agent binds to the loopback
adapter. The actual management IP is always in `ifTable` — use the filter
above. **VALIDATED** (string on System A, inspected 2025-05-12).

**Gotcha — `SystemInfo.vendor`:** Returns `"Unknown"` on many printer models
because the OID for vendor identity is not populated consistently across
manufacturers. Use `SystemInfo.sysName` + `SystemInfo.printerSerialNumber`
for device identification instead. **VALIDATED**.

Report:
- Printer name (`sysName`) and serial (`printerSerialNumber` or
  `prtGeneralTable[0].prtGeneralSerialNumber` — both confirmed equivalent)
- IP address and subnet from `ifTable`
- Location / contact (often empty — flag for manual update if blank)
- Uptime string (`sysUpTime`) — note this is a formatted string, not a
  numeric duration

---

### Step 3 — Consumable levels

```
liongard_metric EVALUATE
  jmesPathQuery="Consumables[*].{desc: prtMarkerSuppliesDescription,
    type: prtMarkerSuppliesType, pct: prtMarkerSuppliesPercentageRemaining_r,
    level: prtMarkerSuppliesLevel, max: prtMarkerSuppliesMaxCapacity,
    unit: prtMarkerSuppliesSupplyUnit}"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

Then separately filter for low consumables:

```
liongard_metric EVALUATE
  jmesPathQuery="Consumables[?prtMarkerSuppliesPercentageRemaining_r < `20`].
    {desc: prtMarkerSuppliesDescription,
     pct: prtMarkerSuppliesPercentageRemaining_r}"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

**VALIDATED** — `prtMarkerSuppliesPercentageRemaining_r` is an integer 0–100
(the `_r` suffix indicates a computed/derived field). `prtMarkerSuppliesLevel`
is the raw level reading; `prtMarkerSuppliesMaxCapacity` is the maximum.
Filter threshold uses backtick integer comparison. (System A, 2025-05-12.)

For each consumable:
- Flag `pct <= slas.consumable_critical_pct` as 🔴 CRITICAL
- Flag `pct <= slas.consumable_low_pct` as 🟡 LOW
- Report `pct > slas.consumable_low_pct` as ✅ OK

---

### Step 4 — Paper tray status

```
liongard_metric EVALUATE
  jmesPathQuery="prtInputTable[*].{name: prtInputName,
    level: prtInputCurrentLevel, max: prtInputMaxCapacity,
    unit: prtInputCapacityUnit, media: prtInputMediaName,
    status: prtInputStatus}"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

**Gotcha — `prtInputCurrentLevel`:** May return the string `"Unknown"` rather
than an integer on printers that do not expose tray-level reporting via SNMP.
Do NOT treat `"Unknown"` as zero — it means the printer does not report this
value, not that the tray is empty. When `prtInputCurrentLevel == "Unknown"`,
note the tray in the manual-verification appendix. **VALIDATED** (System A
returned `"Unknown"` on both trays — this is expected on HP LaserJet P-series
models.)

`prtInputCapacityUnit` is a string (e.g., `"Sheets"`). `prtInputMaxCapacity`
is an integer.

---

### Step 5 — Active alerts

```
liongard_metric EVALUATE
  jmesPathQuery="prtAlertTable[*].{severity: prtAlertSeverityLevel,
    code: prtAlertCode, desc: prtAlertDescription, group: prtAlertGroup}"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

Then critical-events summary:

```
liongard_metric EVALUATE
  jmesPathQuery="prtGeneralTable[0].prtAlertCriticalEvents"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

**Gotcha — `prtAlertSeverityLevel`:** This is a STRING (`"Warning"`,
`"Error"`, `"Critical"`) — **not** an integer enum. Filter or compare
against string values. **VALIDATED** (System A returned `"Warning"` for
`prtAlertCode: "InputMediaSupplyEmpty"`.)

`prtAlertCode` is a human-readable string identifying the alert type (e.g.,
`"InputMediaSupplyEmpty"`, `"MarkerSupplyLow"`, `"CoverOpen"`).
`prtAlertCriticalEvents` is an integer count — 0 means no critical alerts
have been logged in the printer's lifetime counter.

For each alert: flag `severity == "Critical"` or `severity == "Error"` as
🔴 action required; `severity == "Warning"` as 🟡 attention needed.

---

### Step 6 — Page count & lifetime usage

```
liongard_metric EVALUATE
  jmesPathQuery="prtMarkerTable[0].{lifeCount: prtMarkerLifeCount,
    powerOnCount: prtMarkerPowerOnCount, status: prtMarkerStatus,
    colorants: prtMarkerProcessColorants}"
  systemId=<SYSTEM_ID> environmentId=<ENV_ID>
```

**VALIDATED** — `prtMarkerLifeCount` is an integer (lifetime impression
count). `prtMarkerPowerOnCount` is an integer (power cycles).
`prtMarkerStatus` is an integer — encoding varies by manufacturer; 0
commonly means idle/ok, 3 means printing/warming. Do not interpret status
numbers without confirming against the printer's MIB documentation; surface
the raw value and let the operator confirm meaning if non-zero. (System A,
2025-05-12.)

---

### Step 7 — QA pass & manual-verification appendix

Apply the QA retry pattern (`reference/qa-retry-pattern.md`):

- Retry any EVALUATE that returns `null` up to `qa.retry_attempts` times.
- If `latestInspectionDate` is older than
  `qa.flag_inspector_lastseen_threshold_days` days, flag the system.

Build the **Manual verification** appendix with:

| Item | Reason | Action |
|---|---|---|
| Tray level = `"Unknown"` | Printer does not report via SNMP | Check physical tray level on-site |
| `SystemInfo.location` is blank | Not configured in printer | Update SNMP sysLocation string on device |
| `prtMarkerStatus` non-zero | Manufacturer-specific encoding | Confirm via printer front panel or web UI |
| Consumable ≤ critical threshold | Below `slas.consumable_critical_pct`% | Order replacement immediately |

---

## Insights & recommendations

| Condition | Finding | Recommendation |
|---|---|---|
| Any consumable `pct ≤ slas.consumable_critical_pct` | **Critical — [desc] at [pct]%** | Order replacement immediately; printer may stop mid-job |
| Any consumable `pct ≤ slas.consumable_low_pct` | **Low — [desc] at [pct]%** | Order replacement within the week |
| Any `prtAlertSeverityLevel == "Critical"` or `== "Error"` | **Printer error — [code]** | Investigate alert; check printer console or embedded web server |
| `prtAlertCriticalEvents > 0` | Lifetime critical events recorded | Review alert history; may indicate recurring hardware issue |
| `prtInputCurrentLevel == "Unknown"` on all trays | Paper level unmonitored via SNMP | Enable SNMP tray reporting in printer settings or confirm manually |
| `ifTable` operStatus != `"Up"` on any interface | Network interface down | Confirm network connectivity; check switch port |
| `prtMarkerLifeCount > 300000` | High page volume printer | Check against manufacturer recommended service interval; may need maintenance kit |

---

## Data gaps

The following fields are not consistently available across all printer models
or are not yet in the Liongard metric catalog. Surface them in the
**Data Gaps** section of the deliverable.

| Field | Gap type | Alternative |
|---|---|---|
| Firmware version / date | not in dataprint — not in MIB-II or Printer MIB standard; vendor-specific OID | Check printer embedded web server or management console |
| Print queue depth (jobs waiting) | Not in SNMP Printer MIB | Check printer console or Windows print server |
| Duplex capability | not in dataprint — `prtMediaPathTable` has capacity/speed but not duplex flag | Check printer spec sheet |
| Color vs. mono page split | not in dataprint — aggregate life count only; per-type split requires vendor OID | Printer embedded web server |
| Network security settings (SNMPv3 / admin password status) | Out of scope for SNMP polling — would require credentialed HTTP | Verify via printer embedded web server |

---

## Coverage cross-check

| Source | Coverage notes |
|---|---|
| Partner QA matrix | Printer: name/IP/location/consumables/serial — 12 mapped fields. Most are VALIDATED in this recipe. Firmware and page-type split are data gaps. |
| CIS Controls v8.1 | CIS 1.1 (asset inventory — device ID/IP/serial confirmed); CIS 12.2 (network infrastructure — interface status confirmed). Printers are often overlooked in asset inventories. |
| Cyber-insurance domain files | Printers are endpoint-class assets; this recipe feeds `domains/endpoint.md` for device count and `domains/network.md` for network interface status. |
| QBR recipe | QBR Step 8 can chain this recipe for the "Managed Printers" section of the hardware inventory. Surface consumable critical alerts and page volume as QBR highlights. |

---

## Output format

**Default: Markdown** — suitable for NOC daily check or ticket attachment.
**Word**: use for monthly managed-printer health report delivered to the
customer.
**Excel**: use when managing a fleet of printers; one row per printer with
consumable levels, page counts, and alert status for bulk review.

---

## Verification log

| Path / Query | System | Result shape | Status |
|---|---|---|---|
| `SystemInfo.sysName` | System A (inspected 2025-05-12) | `<string>` — printer hostname | **VALIDATED** |
| `SystemInfo.vendor` | System A | `"Unknown"` (string — not reliably populated on HP models) | **VALIDATED** |
| `SystemInfo.printerSerialNumber` | System A | `<string>` — serial confirmed | **VALIDATED** |
| `SystemInfo.Address` | System A | `"127.0.0.1"` — loopback; use `ifTable` filter for real IP | **VALIDATED** |
| `SystemInfo.sysLocation` | System A | `""` (empty string — not configured) | **VALIDATED** |
| `SystemInfo.sysUpTime` | System A | `"<N> Days <H> Hours..."` (formatted string, not numeric) | **VALIDATED** |
| `ifTable[?ipAdEntAddr != '127.0.0.1'].ipAdEntAddr \| [0]` | System A | `<IPv4>` — actual network IP confirmed | **VALIDATED** |
| `ifTable[*].{ip, mask, iface, speedMbps, adminStatus, operStatus}` | System A | Array(1): `ifAdminStatus`/`ifOperStatus` are strings `"Up"/"Down"`; `ifSpeedMBps_r` is integer | **VALIDATED** |
| `Consumables[*].{desc, pct, level, max}` | System A | Array(1): `prtMarkerSuppliesPercentageRemaining_r` is integer 0–100; `prtMarkerSuppliesDescription` is string | **VALIDATED** |
| `Consumables[?prtMarkerSuppliesPercentageRemaining_r < \`20\`]` | System A | Array(1) — filter fires correctly on integer comparison | **VALIDATED** |
| `prtMarkerTable[0].{lifeCount, powerOnCount, status}` | System A | `prtMarkerLifeCount` integer (impression count); `prtMarkerStatus` integer | **VALIDATED** |
| `prtGeneralTable[0].{serial, criticalEvents, printerName}` | System A | `prtAlertCriticalEvents` is integer; `prtGeneralSerialNumber` matches `SystemInfo.printerSerialNumber` | **VALIDATED** |
| `prtAlertTable[*].{severity, code, desc}` | System A | `prtAlertSeverityLevel` is STRING `"Warning"` (not integer); `prtAlertCode` is string | **VALIDATED** |
| `prtInputTable[*].{name, level, max, unit, media}` | System A | `prtInputCurrentLevel` returned `"Unknown"` (string) on both trays — not integer; `prtInputCapacityUnit` is `"Sheets"` | **VALIDATED** |
| Firmware version | System A | Not present in dataprint (SNMP MIB-II does not expose firmware) | SCHEMA_CONFIRMED |
| Per-type page split (color vs. mono) | System A | Not in Printer MIB standard fields | SCHEMA_CONFIRMED |

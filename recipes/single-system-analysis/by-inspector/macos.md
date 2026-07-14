---
name: single-system-macos
description: >
  Use this skill when the user wants a single-system analysis of a macOS device
  — onboarding QA, hardware inventory, OS version, FileVault encryption status,
  installed applications, antivirus presence. Trigger phrases: "macOS review
  for <HOSTNAME>", "Mac audit", "audit <MAC>", "FileVault status on
  <HOSTNAME>", "OSX review". Produces an artifact in the format set in the
  customization block.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device"
personas: [noc, technical-alignment-manager, soc]
output_formats: [markdown, word, xlsx]
primitives: []
---

# Single-System Analysis — macOS

> **Inspector:** `macos-inspector` (ID 96). Endpoint category. One system per
> Mac in the environment.
>
> **References:** `reference/inspector-aliases.md` (Mac, OSX).
> `reference/asset-fields.md` for the device asset record.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<hostname>-macos-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  identity: "Device Identity & Hardware"
  network: "Network Configuration"
  os_updates: "OS Version & Updates"
  applications: "Installed Applications"
  security: "Security Posture (FileVault, Firewall, AV)"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  patch_age_days_max: 30
  inspector_lastseen_days_max: 7
  filevault_required: true

reporting_period: { default: "current_state" }
```

---

## When to use

- Onboarding intake of a Mac
- "Audit <MAC-HOSTNAME> — what's on it, FileVault on, OS current?"
- Pre-decom checklist on a Mac

Personas: NOC, TAM, SOC (FileVault / encryption posture).

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| macOS system ID | Yes | `liongard_system LIST query="mac"` or `query="macos"` |
| Hostname (alternative) | If no system ID | Match by hostname |

---

## Locating the right system

```
liongard_system LIST searchMode=keyword query="mac" environmentId=<ENV_ID>
```

The asset inventory provides the join:

```
liongard_device LIST environmentId=<ENV_ID> pageSize=200
device = Data[?hostname == '<mac-hostname>' AND operatingSystem contains "macOS"]
```

---

## Liongard data sources

### Per-vendor data — macOS fields

| Key | Description |
|---|---|
| `Hostname` | Device hostname |
| `MachineModel` | Model identifier |
| `InternalIP` | Internal IP |
| `OperatingSystem` | OS version (e.g., "macOS Sonoma 14.x") |
| `Applications` | List of installed applications |
| `AvailableUpdates` | Available macOS updates |
| `Antivirus` | Installed AV / security product names |
| `EDR` | EDR product detection |
| `Firewall.globalState` | Firewall enabled state |
| `Overview.FileVaultEncryption` | FileVault encryption status |
| `SecurityProducts` | Enumerated security products |

### Cross-inspector cross-check — asset inventory

```
device = Data[?hostname == '<hostname>' AND operatingSystem contains "macOS"]
```

Asset record provides:
- `Manufacturer` ("Apple"), `Model`, `SerialNumber`
- `LastLogin`, `LastLoginUser`
- `Inspectors[]` — coverage map (e.g., is Addigy / Watchman Monitoring also reporting?)

---

## Onboarding QA — macOS intake fields

Partner-validated mapping (14 fields) — all map to existing macOS metrics:

| Question | Source | Coverage |
|---|---|---|
| Hostname | macOS hostname | ✅ |
| Site / location | RMM tag, manual | ⚠️ |
| Type / model | macOS Machine Model | ✅ |
| Under warranty? | Asset `warrantyExpiration` (Apple-reported via JAMF, etc.) | ⚠️ partial |
| IP address | macOS Internal IP | ✅ |
| Operating system | macOS Operating System | ✅ |
| Reviewed installed apps | macOS List of Applications | ✅ |
| Available updates | macOS Available Updates | ✅ |
| Antivirus | macOS Antivirus on System | ✅ |
| EDR | macOS EDR on System | ✅ |
| FileVault encryption | macOS FileVault Encryption Status | ✅ |
| Firewall enabled | macOS Firewall Enabled | ✅ |
| Role / purpose | manual | ❌ |
| RAID health | not applicable to most Macs | ❌ |

---

## Metrics and queries

### Identity

```jmespath
{
  hostname: <Hostname value>,
  model: <MachineModel>,
  os: <OperatingSystem>,
  ip: <InternalIP>
}
```

### Updates

| Metric | JMESPath / metric detail | Result shape |
|---|---|---|
| Available updates count | `length(AvailableUpdates)` | `<integer>` |
| Available updates list | `AvailableUpdates[*].Title` | `<array<string>>` |

### Applications

| Metric | JMESPath / metric detail | Result shape |
|---|---|---|
| App list | `Applications[*].[Name, Version]` | `<array>` |

### Security

| Metric | JMESPath / metric detail | Compliant when |
|---|---|---|
| Antivirus product names | `SecurityProducts[*].Name` | non-empty |
| EDR product names | `EDR[*].Name` | non-empty if SLA requires |
| FileVault | `Overview.FileVaultEncryption` | `enabled` |
| Firewall | `contains(Firewall.globalState, 'Enabled')` | `true` |

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| FileVault disabled | `Overview.FileVaultEncryption != 'enabled'` AND `slas.filevault_required` | "Enable FileVault and escrow recovery key." |
| Firewall off | macOS firewall not enabled | "Enable application firewall." |
| Updates pending | `length(AvailableUpdates) > 0` | "<N> macOS updates pending — apply." |
| No AV detected | `length(SecurityProducts) == 0` AND policy requires | "No AV detected — confirm or deploy." |
| OS version unsupported | `OperatingSystem` < current Apple-supported | "Upgrade macOS — currently 3 major versions or older." |
| Stale inspector | `LastSeen > 7 days` | "Mac inspector hasn't reported in <N> days." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Site / location | ⚠️ partial | RMM tag, MDM (Addigy / Jamf) |
| Warranty | ⚠️ partial | Apple Check Coverage tool, MDM |
| Role / purpose | ❌ | Manual entry |
| RAID / disk health | ❌ | `diskutil` / vendor tools |

---

## Output format

Markdown / Word / Excel per `output.format`.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_device LIST | envId=<ENV_ID> | array<device> | ok |
| 3 | liongard_system LIST | query="mac" envId=<ENV_ID> | array<system> | ok |
| 4 | liongard_metric EVALUATE | metricName="macOS: Operating System" sysId=<SYS_ID> envId=<ENV_ID> | string | ok |
| 4 | liongard_metric EVALUATE | metricName="macOS: Model" sysId=<SYS_ID> envId=<ENV_ID> | string | ok |
| 4 | liongard_metric EVALUATE | metricName="macOS: Hostname" sysId=<SYS_ID> envId=<ENV_ID> | string | ok |
| 4 | liongard_metric EVALUATE | metricName="macOS: File Vault Encryption Status" sysId=<SYS_ID> envId=<ENV_ID> | string | ok |
| 4 | liongard_metric EVALUATE | metricName="macOS: Internal IP" sysId=<SYS_ID> envId=<ENV_ID> | string | ok |
| 4 | liongard_metric EVALUATE | metricName="macOS: Antivirus On System" sysId=<SYS_ID> envId=<ENV_ID> | array | ok |
| 4 | liongard_metric EVALUATE | metricName="macOS: List of Available Updates" sysId=<SYS_ID> envId=<ENV_ID> | array | ok |
| 4 | liongard_metric EVALUATE | metricName="macOS: List of Applications" sysId=<SYS_ID> envId=<ENV_ID> | array | ok |
| 4 | liongard_metric EVALUATE | metricName="macOS: Firewall Enabled Status" sysId=<SYS_ID> envId=<ENV_ID> | string/bool | ok |
```

---
name: single-system-linux
description: >
  Use this skill when the user wants a single-system analysis of a Linux server
  / workstation — onboarding QA, hostname/IP/domain, sudo / privileged users,
  installed software / package version, AV / RMM agent presence. Trigger
  phrases: "Linux server review for <HOSTNAME>", "audit <LINUX-BOX>", "what
  packages are on <HOSTNAME>", "who has sudo on <HOSTNAME>". Produces an
  artifact in the format set in the customization block.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_asset"
personas: [noc, technical-alignment-manager, soc]
output_formats: [markdown, word, xlsx]
primitives: []
---

# Single-System Analysis — Linux

> **Inspector:** `linux-inspector` (ID 53). Endpoint category. One system per
> Linux installation in the environment (server or workstation).
>
> **References:** `reference/asset-fields.md` for the device asset record this
> Linux instance appears on. Per partner-validated mapping, several Linux fields
> are not yet in the dataprint — see Data Gaps.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<hostname>-linux-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  identity: "Server Identity"
  network: "Network Configuration"
  os_packages: "OS & Packages"
  users: "Privileged / Sudo Users"
  security: "Security Posture"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 7

reporting_period: { default: "current_state" }
```

---

## When to use

- Onboarding intake of a Linux server
- "Audit <HOSTNAME> — what's on it, who has sudo, what's the version?"
- Patch / package-update review

Personas: NOC, TAM, SOC (privileged user audit).

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| Linux system ID | Yes | `liongard_system LIST query="linux"` |
| Hostname (alternative) | If no system ID | Match by hostname |

---

## Locating the right system

```
liongard_system LIST searchMode=keyword query="linux" environmentId=<ENV_ID>
```

The asset inventory provides the join key:

```
liongard_asset LIST environmentId=<ENV_ID> assetType=Device detail=full pageSize=200
device = Devices[?Hostname == '<linux-hostname>' AND OperatingSystem contains "Linux"]
```

---

## Liongard data sources

### Per-vendor data — Linux fields

| Key | Description |
|---|---|
| `SystemInfo` | Hostname, distro/release info, kernel, IP, virtualization type |
| `Users` | Local users with sudo / privileged flags |
| `Software` (when populated) | Installed packages |
| `Services` (when populated) | systemd / init services |

### Cross-inspector cross-check — asset inventory

```
device = Devices[?Hostname == '<hostname>' AND OperatingSystem contains "Linux"]
```

Asset record provides:
- `Manufacturer`, `Model`, `SerialNumber` (when reported via SMBIOS)
- `Physical` vs. VM
- `HostServer`, `ClusterName` (for VMs on Hyper-V or vCenter)
- `Inspectors[]` — confirms which inspectors see this Linux box

---

## Onboarding QA — Linux intake fields

Partner-validated mapping (22 fields):

| Question | Source | Coverage |
|---|---|---|
| Hostname | `SystemInfo.Hostname` (existing metric `[VI]`) | ✅ |
| Site / location | RMM tag, manual | ⚠️ partial |
| Type (physical / VM / container) | Asset `Physical`, partner-flagged not in current dataprint `Linux: Virtualization Type [VI]` | ⚠️ not in dataprint |
| Under warranty? | Asset `warrantyExpiration` if SMBIOS-reported | ⚠️ rare |
| IP address | Proposed metric `Linux: IP Address [VI]`; asset `InternalIP` | ⚠️ asset cross-check |
| DNS servers | not in dataprint | ❌ — manual or via OS query |
| Operating system | `SystemInfo.VERSION` | ✅ |
| Connected to the domain? | Proposed metric `Linux: Domain Membership [VI]` | ⚠️ not in dataprint |
| Reviewed installed programs | not in dataprint | ❌ — manual `dpkg -l` / `rpm -qa` |
| Pending updates | not in dataprint | ❌ — manual `apt list --upgradable` / `dnf check-update` |
| Sudo users | `Users[?Privileged]` or equivalent privileged-user list from the Linux dataprint | ✅ |
| RMM / Automate installed | Proposed metric `Linux: RMM Agent Service Status [VI]` | ⚠️ not in dataprint |
| Antivirus / EDR installed | Proposed metric `Linux: Antivirus / EDR Software [VI]` | ⚠️ not in dataprint |
| Role / purpose | manual | ❌ |
| RAID health | not in dataprint | ❌ — `mdadm`, vendor tools |
| VM-specific (if hypervisor host) | use `linux` for KVM/Xen via tooling | partial |

> **Many gaps.** Partner audit flagged Linux as a major gap area — most
> onboarding-QA fields are not yet in the dataprint — see Data Gaps. See Data
> Gaps section for the metric backlog.

---

## Metrics and queries

### Identity / OS

| Metric | JMESPath | Result shape |
|---|---|---|
| Hostname | `SystemInfo.Hostname` | `<string>` |
| Software version (kernel/distro) | `SystemInfo.VERSION` | `<string>` |
| Privileged user list | `Users[?Privileged]` | `<array>` |

### Sudo audit

```jmespath
Users[?Privileged].{ name: Username, uid: UID, sudoGroup: SudoGroupMembership }
```

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Sudo accounts beyond expected | count of Sudo users > expected | "Review sudo grants on <hostname>." |
| Stale inspector | `LastSeen` > 7 days | "Linux inspector last reported <N> days ago — confirm agent." |
| RMM coverage unconfirmed | proposed RMM metric not yet built | "Manual check needed: confirm RMM agent on <hostname>." |
| OS version EOL | `SystemInfo.VERSION` indicates EOL distro | "Distro/release at EOL — plan upgrade." |

---

## Data gaps & coverage notes

The Liongard `linux-inspector` is **less mature** than the Windows OS
inspectors. Partner audit flagged the following as data gaps
(not yet in the library — file as metric requests):

- Linux: System Summary [VI]
- Linux: Virtualization Type [VI]
- Linux: IP Address [VI]
- Linux: Domain Membership [VI]
- Linux: RMM Agent Service Status [VI]
- Linux: Antivirus / EDR Software [VI]

For these, fall back to:
- The asset inventory's cross-inspector synthesis (`InternalIP`, `Physical`,
  `HostServer`, `Inspectors[]` showing RMM presence).
- RMM inspectors (NinjaOne, ConnectWise Automate, etc.) — if the Linux box has
  an RMM agent, the RMM dataprint will list it.
- Manual SSH-based checks via the customer's runbook.

---

## Output format

Markdown / Word / Excel per `output.format`.

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST | filter=<name> | array<environment> | ok |
| 2 | liongard_asset LIST | envId=<ENV_ID> assetType=Device detail=full | array<device> | ok |
| 3 | liongard_system LIST | query="linux" envId=<ENV_ID> | array<system> | ok |
| 4 | liongard_metric EVALUATE | metricName="Linux: Privileged User List" sysId=<SYS_ID> envId=<ENV_ID> | <array> | ok |
| 5 | liongard_metric EVALUATE | metricName="Linux: Software Version" sysId=<SYS_ID> envId=<ENV_ID> | <string> | ok |
```

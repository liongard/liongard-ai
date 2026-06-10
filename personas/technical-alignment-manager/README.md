# Technical Alignment Manager — Persona Index

The Technical Alignment Manager (TAM) owns **standards alignment** —
making sure every customer's configuration matches the MSP's documented
best practices. TAM recipes find drift: missing security baselines,
inconsistent agent versions, unconventional rules, gaps in the
recommended tool stack. The TAM role exists at MSPs that have invested
in a Center of Excellence; at smaller MSPs the function is distributed
across NOC, vCIO, and senior engineers.

## Audience framing

- **Tone:** technical to balanced. TAM consumers are engineers reviewing
  configuration; technical detail matters and is welcome.
- **Format:** Excel for per-customer drift reports (sortable, filterable);
  Markdown for working notes; Word for the customer-facing recommendation
  document.
- **Default cadence:** at onboarding; then quarterly drift checks; ad-hoc
  after a customer environment change.

## SLA emphasis (TAM defaults)

| SLA | Default | Why TAM cares |
|---|---|---|
| `inspector_lastseen_days_max` | 1–7 days | Stale data hides drift |
| Configuration consistency thresholds (e.g., firmware age, agent version drift) | Tight | TAM exists to drive consistency |
| `flag_count_divergence_threshold_pct` | 5% (default) → 1% during onboarding | Onboarding wants every reconciliation issue surfaced |
| Standard build vs. observed | 100% match expected | Drift is the TAM's job |

## Common scenarios → recipes

### Onboarding intake (primary cross-cutting recipe)

The TAM's flagship recipe — a *point-in-time* gap analysis that grades a
new customer's environment against the MSP's documented onboarding
standard and produces the 30 / 60 / 90 day remediation plan.

| Recipe | What it gives the TAM |
|---|---|
| `recipes/onboarding-assessment/new-customer-onboarding.md` | Auto-discovers the customer's inspector stack, chains the per-class deep-dives below, then grades findings against the onboarding standard defined in the customization block. Outputs an Excel intake workbook + Word narrative gap analysis. |

### Onboarding deep-dives (chained by the master onboarding recipe)
Use these standalone when the onboarding intake flags a domain that
needs deeper inspection than the rollup produced.

| Domain | Recipe |
|---|---|
| Server intake (Windows / Linux / macOS / VMs) | `recipes/single-system-analysis/by-inspector/{windows-server,linux,macos,windows-workstation}.md` (one per server) |
| Server-class assessment + role inventory | `recipes/system-type-assessment/all-servers.md` |
| Endpoint fleet inventory + Win11 readiness | `recipes/system-type-assessment/all-endpoints.md` |
| Firewall configuration audit | `recipes/system-type-assessment/all-firewalls.md` + per-vendor recipes |
| EDR coverage + posture | `recipes/system-type-assessment/all-edrs.md` + per-vendor recipes |
| Backup coverage | `recipes/system-type-assessment/all-backups.md` |
| AD configuration audit | `recipes/single-system-analysis/by-inspector/active-directory.md` |
| M365 identity + license intake | `recipes/single-system-analysis/by-inspector/microsoft-365.md` |
| Hypervisor stack audit | `recipes/system-type-assessment/all-hypervisors.md` |
| Domain inventory + DMARC posture | `recipes/system-type-assessment/all-domains.md` |
| Documentation completeness + password-vault audit | `recipes/single-system-analysis/by-inspector/itglue.md` |
| PSA platform standards drift | `recipes/system-type-assessment/all-psa-platforms.md` or per-PSA single |
| Cloud-storage retention + sharing-policy alignment | `recipes/system-type-assessment/all-cloud-storage.md` or per-platform single |
| Network-infrastructure firmware + standards alignment | `recipes/system-type-assessment/all-network-infrastructure.md` (firmware-currency + AAA + VLAN-consistency sections) |
| Switch / router / AP refresh roadmap | `all-network-infrastructure.md` (lifecycle section) feeds `recipes/roadmap-planning/refresh-and-lifecycle-roadmap.md` |

### Quarterly standards drift checks

| Scenario | Recipe |
|---|---|
| "Firmware drift across the customer's firewalls" | `all-firewalls.md` (firmware-currency section) |
| "EDR version drift across the customer's endpoints" | `all-edrs.md` |
| "AD password policy drift from MSP standard" | `active-directory.md` (password-policy section) |
| "Server roles — any role consolidation needing review" | `all-servers.md` (role inventory + blast-radius rollup) |
| "Backup retention drift vs. MSP standard (3-2-1 + N days)" | `all-backups.md` + per-vendor recipes |
| "Hypervisor capacity drift (VM density per host trend)" | `all-hypervisors.md` |

### Deep-dive audits

| Scenario | Recipe |
|---|---|
| "Single-firewall config audit — full WAN-to-LAN rule review" | Per-firewall-vendor recipe |
| "Single-server audit — pre-decom checklist, role inventory, last user" | Per-OS recipe |
| "EDR vendor switch — compare two vendors' coverage on the same fleet" | `all-edrs.md` + per-vendor recipes for both |

## Read across to other personas

- **NOC** — when drift surfaces an operational issue, NOC handles
  short-term remediation; TAM updates the standard so it doesn't recur.
- **vCIO** — when standards drift requires customer budget /
  conversation (e.g., refresh, new vendor), TAM provides the technical
  case; vCIO owns the conversation.
- **SOC** — when configuration drift creates a security gap, SOC
  validates risk; TAM updates the build standard.

## What to customize first

1. **Your build-standard documentation** — link each recipe's
   recommendation thresholds to your written standards. The recipe's
   SLA block (`slas.*`) is where this lives.
2. **Onboarding standard baseline** — the
   `onboarding_standard` block in
   `recipes/onboarding-assessment/new-customer-onboarding.md` is the
   recipe's value proposition. Update the expected-inspectors list, the
   identity / endpoint / network / backup / domain baselines, and the
   remediation-phase day boundaries to match your MSP's documented
   onboarding standard. Every customer's intake report grades against
   this block.
3. **Tighter divergence thresholds during onboarding** — set
   `qa.flag_count_divergence_threshold_pct: 1` (vs. the default 5%) so
   onboarding catches every reconciliation issue.
4. **Per-domain standards docs** — link your AD / firewall / backup /
   identity standards from the corresponding recipe's customization
   block so reports auto-flag deviation.

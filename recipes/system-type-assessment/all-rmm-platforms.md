---
name: system-type-all-rmm-platforms
description: >
  Use this skill when the user wants a unified RMM-platform assessment
  across all RMM tenants in an environment — NinjaOne, Datto RMM,
  Kaseya VSA, N-able N-Central, ConnectWise Automate, N-able RMM,
  ConnectWise Asio, Continuum RMM (legacy). Trigger phrases:
  "RMM posture for <customer>", "all RMM platforms", "RMM agent
  coverage across <customer>", "RMM sprawl audit", "RMM
  consolidation candidate", "patch posture across RMMs", "RMM
  technician audit".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device, liongard_cyber_risk_dashboard"
personas: [noc, technical-alignment-manager, vcio-account-manager, accounting-finance, soc]
output_formats: [pptx, word, xlsx, markdown]
primitives:
  - metrics:connectwise-asio-inspector:active-company-count
  - metrics:connectwise-asio-inspector:company-count
  - metrics:connectwise-asio-inspector:company-roster
  - metrics:connectwise-asio-inspector:discovered-child-count
  - metrics:connectwise-asio-inspector:discovered-children
  - metrics:connectwise-asio-inspector:zero-device-companies
  - metrics:connectwise-automate:computers-total-count
  - metrics:continuum-rmm-inspector:antivirus-summary-desktops
  - metrics:continuum-rmm-inspector:antivirus-summary-servers
  - metrics:continuum-rmm-inspector:device-inventory
  - metrics:continuum-rmm-inspector:failed-or-stale-agents-count
  - metrics:continuum-rmm-inspector:failed-or-stale-agents-list
  - metrics:continuum-rmm-inspector:health-scores
  - metrics:continuum-rmm-inspector:patch-state-servers
  - metrics:continuum-rmm-inspector:summary-site
  - metrics:continuum-rmm-inspector:total-agents-count
  - metrics:continuum-rmm-inspector:total-snmp-devices-count
  - metrics:continuum-rmm-inspector:warranty-summary-servers
  - metrics:datto-rmm:devices-pending-patches-count
  - metrics:datto-rmm:devices-snmp-enabled-count
  - metrics:kaseya-vsa-inspector:agents-offline-count
  - metrics:kaseya-vsa-inspector:agents-online-count
  - metrics:kaseya-vsa-inspector:agents-total-count
  - metrics:kaseya-vsa-inspector:alarms-critical-count
  - metrics:kaseya-vsa-inspector:alarms-open-count
  - metrics:kaseya-vsa-inspector:endpoint-security-coverage-count
  - metrics:kaseya-vsa-inspector:licensing-seat-total
  - metrics:kaseya-vsa-inspector:licensing-seat-used
  - metrics:kaseya-vsa-inspector:licensing-utilization-pct
  - metrics:kaseya-vsa-inspector:monitor-sets-assigned-count
  - metrics:kaseya-vsa-inspector:monitor-sets-disabled-count
  - metrics:kaseya-vsa-inspector:patches-critical-pending-count
  - metrics:kaseya-vsa-inspector:patches-pending-count
  - metrics:kaseya-vsa-inspector:users-mfa-enabled-count
  - metrics:kaseya-vsa-inspector:users-total-count
  - metrics:n-able-n-central:count-of-devices-added-last-30-days
  - metrics:n-able-n-central:count-of-devices-failed-state
  - metrics:n-able-n-central:count-of-devices-stale-state
  - metrics:n-able-n-central:count-of-devices-warning-state
  - metrics:n-able-n-central:count-of-esxi-servers
  - metrics:n-able-n-central:count-of-failed-jobs
  - metrics:n-able-n-central:count-of-printers
  - metrics:n-able-n-central:count-of-storage-devices
  - metrics:n-able-n-central:count-of-switch-router-devices
  - metrics:n-able-n-central:count-of-windows-laptops
  - metrics:n-able-n-central:count-of-windows-servers
  - metrics:n-able-n-central:count-of-workstations
  - metrics:n-able-n-central:device-details-powerbi
  - metrics:n-able-n-central:device-info-with-last-user
  - metrics:n-able-n-central:device-list-powerbi
  - metrics:n-able-n-central:list-of-devices-added-last-30-days
  - metrics:n-able-n-central:list-of-devices-failed-state
  - metrics:n-able-n-central:list-of-devices-stale-state
  - metrics:n-able-n-central:list-of-devices-warning-state
  - metrics:n-able-n-central:list-of-esxi-servers
  - metrics:n-able-n-central:list-of-failed-jobs
  - metrics:n-able-n-central:list-of-printers
  - metrics:n-able-n-central:list-of-storage-devices
  - metrics:n-able-n-central:list-of-switch-router-devices
  - metrics:n-able-n-central:list-of-windows-laptops
  - metrics:n-able-n-central:list-of-windows-servers
  - metrics:n-able-n-central:list-of-workstations
  - metrics:nable-rmm:inactive-mobile-devices
  - metrics:nable-rmm:server-count
  - metrics:nable-rmm:server-list
  - metrics:nable-rmm:server-summary
  - metrics:nable-rmm:sites-count
  - metrics:nable-rmm:sites-list
  - metrics:nable-rmm:workstation-count
  - metrics:nable-rmm:workstation-summary
  - metrics:ninjaone:alerts-critical-count
  - metrics:ninjaone:alerts-open-count
  - metrics:ninjaone:devices-online-count
  - metrics:ninjaone:devices-total-count
  - metrics:ninjaone:licensing-utilization-pct
  - metrics:ninjaone:patches-critical-pending-count
  - metrics:ninjaone:patches-pending-count
  - metrics:ninjaone:users-mfa-enabled-count
  - metrics:ninjaone:users-technician-count
---

# System-Type Assessment — All RMM Platforms

> Unified RMM posture across every RMM inspector deployed at the
> customer. Most healthy MSPs run **one RMM**; this rollup surfaces
> sprawl (a common acquisition or migration artifact) and produces the
> consolidated agent / patch / alert / license view.
>
> **RMM inspectors covered:**
>
> | Inspector | Recipe |
> |---|---|
> | NinjaOne | `recipes/single-system-analysis/by-inspector/ninjaone.md` |
> | Datto RMM | `recipes/single-system-analysis/by-inspector/datto-rmm.md` |
> | Kaseya VSA | `recipes/single-system-analysis/by-inspector/kaseya-vsa.md` |
> | N-able N-central | `recipes/single-system-analysis/by-inspector/n-able-n-central.md` |
> | ConnectWise Automate | `recipes/single-system-analysis/by-inspector/connectwise-automate.md` |
> | N-able RMM (N-sight) | `recipes/single-system-analysis/by-inspector/nable-rmm.md` |
> | ConnectWise Asio | `recipes/single-system-analysis/by-inspector/connectwise-asio.md` |
> | Continuum RMM (legacy/EOL) | `recipes/single-system-analysis/by-inspector/continuum-rmm.md` |
> | (future) Syncro | `syncro-inspector` — not yet recipe'd |
>
> **References:** `reference/asset-fields.md` (the reconciled device
> inventory tool); `reference/qa-retry-pattern.md`;
> `reference/inspector-aliases.md`.

---

## Customize for your MSP

```yaml
output:
  format: pptx
  filename: "<customer>-rmm-posture-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  cover: "RMM Posture Assessment"
  executive_summary: "Executive Summary"
  rmm_inventory: "RMM Platforms in Use"
  agent_coverage_rollup: "Agent Coverage (Reconciled)"
  patch_posture_rollup: "Patch Posture"
  av_coverage_rollup: "AV / EDR Coverage"
  monitor_drift: "Monitor / Standard Drift"
  alert_posture_rollup: "Alert / Ticket Activity"
  technician_audit: "Technician / RMM-User Audit"
  licensing_rollup: "License Utilization"
  consolidation_opportunity: "RMM Consolidation Opportunity"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Manual Verification"
  appendix: "Appendix — Per-RMM Detail"
  verification_log: "Verification Log"

audience: { tone: "balanced" }

slas:
  agent_coverage_pct_min: 95
  agent_lastSeen_days_max: 7
  patch_age_days_max: 30
  critical_patches_pending_max: 0
  unresolved_alerts_max: 0
  antivirus_coverage_pct_min: 95
  technician_mfa_required: true
  rmm_consolidation_target: 1            # MSP standard: exactly one RMM per customer
                                         # > 1 = consolidation candidate

reporting_period: { default: "current_state" }

stack:
  auto_discover: true
  inspectors_in_scope: []
  inspectors_to_skip: []

qa:
  retry_on_null: true
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: false
  surface_single_source_visibility: true
  manual_verification_section_required: true
```

---

## When to use

- "RMM posture for <customer>"
- "All RMM agent coverage check"
- "RMM consolidation candidate analysis"
- "Patch posture across RMM platforms"
- "RMM-user MFA audit"

Cadence: monthly per customer; quarterly in PBR; ad-hoc during
migration / consolidation projects.

Personas:
- **NOC** (primary — daily operational view)
- **TAM** (monitor / standard drift; consolidation prep)
- **vCIO / Account Manager** (consolidation business case)
- **Accounting / Finance** (consolidated license utilization)
- **SOC** (RMM-user MFA audit — RMM accounts are high-value attack
  targets)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |

---

## Workflow

### Step 1 — Scope + RMM discovery

```
liongard_environment LIST searchMode=keyword query="<customer>"

# Discover deployed RMM inspectors
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="ninjaone"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="datto-rmm"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="kaseya-vsa"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="n-central"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="connectwise-automate"
liongard_launchpoint LIST environmentId=<ENV_ID> inspectorId=87   # N-able RMM (N-sight)
liongard_launchpoint LIST environmentId=<ENV_ID> inspectorId=103  # ConnectWise Asio
liongard_launchpoint LIST environmentId=<ENV_ID> inspectorId=60   # Continuum RMM (legacy/EOL)
```

Emit a per-RMM deployment table. If more than
`slas.rmm_consolidation_target` (default 1) RMMs are deployed,
surface as a **consolidation candidate** — this is the rollup's most-
differentiated finding.

### Step 2 — Inspector freshness across all RMMs

```
liongard_timeline LIST environmentId=<ENV_ID>
```

Each chained per-RMM recipe inherits stale-inspector findings.

### Step 3 — Reconciled device inventory

```
liongard_device COUNT environmentId=<ENV_ID>
liongard_device LIST environmentId=<ENV_ID>
                     fields=["hostname","operatingSystem","class","role","inspectors","lastSeen"]
```

The reconciled device inventory is the authoritative target for
RMM-coverage analysis — every managed device should appear in at
least one RMM (and ideally exactly one per MSP standard).

### Step 4 — Per-RMM findings (chain singles)

For each deployed RMM, chain the per-vendor single with
`audience.tone` inherited. Extract the top findings — not the full
output.

### Step 5 — Agent-coverage rollup

Compute coverage at three levels:

| Level | Source | Use |
|---|---|---|
| Reconciled coverage % | Count of devices in any RMM ÷ total managed devices | Headline KPI |
| Per-RMM coverage % | Each chained recipe's metric | Per-platform detail |
| Overlap analysis | Devices in 2+ RMMs simultaneously | **Sprawl signal — consolidation finding** |

A device appearing in 2 RMMs is rarely intentional; it usually
indicates an incomplete migration or post-acquisition leftover.
Surface as a quick-win cleanup opportunity.

### Step 6 — Patch posture rollup

Aggregate patch findings across all RMMs:
- Total critical patches pending (reconciled)
- Per-RMM patch policy posture (any deferred-excessively?)
- Per-OS patch posture (cross-reference with
  `recipes/system-type-assessment/all-windows-patching.md`)

### Step 7 — AV / EDR coverage rollup

| Pattern | Treatment |
|---|---|
| Device in RMM but missing from EDR inventory | High — coverage gap |
| Device with conflicting AV vendor reported across RMMs | Medium — clarify ground truth |
| Device with no AV reported in any RMM | Critical |

### Step 8 — Monitor / standard-drift surface

Each RMM has a monitor / agent-procedure layer; cross-RMM
standardization is rare. Surface:
- Disabled standard monitors per RMM (from per-RMM recipes)
- Coverage-of-standard-monitors percentage per RMM
- TAM remediation list to bring each customer to MSP standard

### Step 9 — Alert / ticket rollup

```
For each RMM: openCount + criticalCount + byAge
Aggregate to: total open alerts, total critical, oldest open
```

### Step 10 — Technician / RMM-user audit

For each deployed RMM:
- Technician count
- MFA-enabled count + percentage
- Flag any RMM-user without MFA as Critical (RMM accounts are
  high-value attack targets)
- Cross-RMM: same technician using multiple RMMs (expected during
  migration; long-term = consolidation finding)

### Step 11 — License utilization rollup

```
For each RMM: seatTotal, seatUsed, utilizationPct, renewalDate
Aggregate to: total spend (where MSP populates cost), upcoming renewals
```

When the customer has multiple RMMs deployed, the consolidation
finding includes the **total license-spend opportunity** (if cost
data populated).

### Step 12 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on:
1. Retry persistent nulls per RMM.
2. Stale-inspector flags propagate per RMM.
3. **Cross-RMM device-count divergence** is expected during migration;
   surface union + intersection sizes.
4. **MFA verification** on RMM-user accounts is elevated (high-value
   target).
5. Single-source visibility on devices.

### Step 13 — Render

Recommended slide / page order:

| # | Slide | Content |
|---|---|---|
| 1 | Cover | Customer, period, MSP name + logo |
| 2 | Executive Summary | Headline coverage + consolidation candidate flag |
| 3 | RMM Platforms in Use | Per-RMM deployment table |
| 4 | Agent Coverage (Reconciled) | Reconciled + per-RMM tiles + overlap detail |
| 5 | Patch Posture | Aggregated patch view |
| 6 | AV / EDR Coverage | Aggregated AV/EDR view + gaps |
| 7 | Monitor / Standard Drift | Per-RMM standard-coverage scorecard |
| 8 | Alert / Ticket Activity | Aggregated alert view |
| 9 | Technician Audit | Per-RMM technician + MFA table |
| 10 | License Utilization | Aggregated license view |
| 11 | Consolidation Opportunity | Recommended target RMM + migration plan + cost case |
| 12 | Recommendations | Prioritized actions |
| 13 | Data Gaps | The Step 12 manual-verification appendix |

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ⚠️ | RMM rollup — endpoint-equivalent questions are aggregated at the rollup level (reconciled agent coverage / per-RMM coverage / overlap detection). Matrix doesn't yet include an RMM row; this rollup's "Coverage rollup" section is the candidate template if the matrix is extended to RMM. |
| CIS Controls (v8.1) | ✅ | Maps to CIS 1.1 (asset inventory across all RMMs — reconciled), 2.1 (software inventory), 7.3 / 7.4 (patch posture rollup), 10.1 / 10.6 (AV coverage rollup), 6.3 / 6.4 (RMM-user MFA — high-value target), 8.2 (audit logs). |
| Cyber-insurance domain files | ✅ | This rollup is the consolidated evidence source for the patching / AV-coverage questions in `domains/endpoint.md` when the customer has any RMM deployed. |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this as the customer's reconciled RMM-posture section; surfaces reconciled agent %, patch posture, AV/EDR coverage, monitor-drift scorecard, RMM-user MFA %, and the consolidation candidate flag. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| Multiple RMMs deployed | "Customer uses <N> RMM platforms. Consolidation candidate — recommended target is <MSP standard>. Estimated effort: <S/M/L>; estimated savings: <license consolidation $>." |
| Reconciled agent coverage below SLA | "Reconciled coverage at <N>%. Deploy any-RMM agent to <N> uncovered managed devices." |
| Devices in 2+ RMMs | "<N> devices appear in multiple RMMs. Clean up post-migration: pick the canonical RMM per device and uninstall the others." |
| Critical patches pending (reconciled) | "Apply <N> critical patches across the fleet. Top exposed RMMs: <list>." |
| Devices without AV in any RMM | "<N> devices report no AV / EDR in any RMM. Confirm coverage from another inspector (EDR vendor); deploy if missing." |
| Disabled standard monitors | "<N> standard monitors disabled across <N> RMMs. Bring each customer to MSP-standard monitor coverage." |
| RMM user without MFA | "URGENT: Enforce MFA on <N> RMM user accounts. RMM accounts are high-value targets (cf. 2021 Kaseya VSA incident)." |
| License utilization > warn | "Plan renewal expansion / consolidation across <list-of-RMMs>." |
| Overlapping technician licenses across RMMs | "Same technician licensed in <N> RMMs. Consolidation reduces redundant licensing." |

---

## Data gaps & coverage notes

Inherits per-RMM data gaps. Rollup-specific:

| Field | Status | Source if missing |
|---|---|---|
| Cross-RMM script / automation parity | external | Per-RMM consoles |
| Migration-effort estimation | external | MSP engineering capacity planning |
| Cost-of-license figures | external (unless MSP populates) | MSP PSA / accounting |
| RMM ↔ PSA integration health (per RMM) | partial | Per-RMM ↔ PSA console |

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST + liongard_system LIST | per-RMM queries | array<system> | ok per RMM |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3 | liongard_device LIST + COUNT | envId=<ENV_ID> [filters] | varies | ok |
| 4 | (chain per-RMM singles) | per single-system recipe | per-recipe findings | ok per RMM |
| 5 | (coverage rollup — derived) | per slas | tiles + overlap | ok |
| 6–11 | (per-area rollups — derived) | per slas | aggregations | ok |
| 12 | QA pass | per `reference/qa-retry-pattern.md` | varies | ok |
| 13 | render | per `output.format` | <artifact path> | ok |
```

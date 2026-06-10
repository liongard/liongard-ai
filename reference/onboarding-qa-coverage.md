# Onboarding QA Coverage Matrix

The standard "endpoint posture" questionnaire most MSPs use during onboarding asks
the same six questions of every EDR / antivirus inspector. The answers are not
uniformly available across inspectors — this file is the partner-validated
coverage matrix so recipes don't promise data that an inspector can't provide.

Source pattern: derived from a partner onboarding QA where every endpoint
inspector was mapped to specific fields. Coverage notes are partner-confirmed.

> **Reference, not a recipe.** Use this file to plan what each EDR recipe should
> claim and what it should mark "not directly available — see
> `liongard_asset` cross-check." See the
> "Onboarding QA — Endpoint Posture" section in each EDR recipe for the live
> implementation.

## The six standard questions

| # | Question | Why it matters |
|---|---|---|
| 1 | **Total endpoints managed** | License headroom, scope confirmation |
| 2 | **Active in last 30 days** | Operational coverage right now |
| 3 | **Inactive 2+ months** | Stale agents — uninstall candidates or unprotected |
| 4 | **Not protected** | Endpoints in scope but missing the EDR — coverage gap |
| 5 | **Servers managed** (vs. workstations) | Server policy and licensing distinction |
| 6 | **High alerts / threats** | Active risk |

## Per-inspector coverage

✅ = directly available • ⚠️ = partial / requires client-side derivation •
❌ = not available from the EDR itself; use asset-inventory cross-check
🔄 = available via combined query of two metrics

| Inspector | Total | Active 30d | Inactive 60d+ | Not protected | Servers split | Alerts |
|---|---|---|---|---|---|---|
| **SentinelOne** (`sentinelone-inspector`) | ✅ | ✅ | ✅ | ❌ | ✅ via `machineType=server` | ✅ |
| **Huntress** (`huntress-inspector`) | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ via dataprint; portal only |
| **Bitdefender GravityZone** (`bitdefender-gravityzone-inspector`) | ✅ | ✅ online | ✅ offline | ❌ | ⚠️ VM-count only | ✅ infected |
| **CrowdStrike Falcon** (`crowdstrike-inspector`) | ✅ | ✅ active sensor | ✅ non-normal | ❌ | ✅ | ✅ detections |
| **Sophos Central** (`sophos-central-inspector`) | ✅ | ✅ | ✅ not seen 30d | ✅ separate metric | ✅ | ✅ threat-health-not-good |
| **ESET Licensing** (`eset-licensing-inspector`) | ✅ active users | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Webroot** (`webroot-inspector`) | ✅ | ✅ | ✅ | ✅ deactivated | ❌ | ✅ infected |
| **SonicWall Capture Client** (`sonicwall-capture-client-inspector`) | ✅ | ✅ | ⚠️ | ⚠️ | ❌ | ✅ infected |

> ESET Licensing is licensing-only — **don't promise endpoint last-seen, type, or
> threat data on ESET; recommend co-deploying with another EDR for posture
> visibility.**

## "Not Protected" — the cross-inspector pattern

No EDR exposes "endpoints in our environment that don't have me installed" — by
definition the EDR only sees what reports back. The cross-inspector device
inventory is the only authoritative answer:

```
# Pull the device inventory once (compute-class only) for the run
liongard_device LIST environmentId=<ENV_ID> category="compute" fields=["hostname","inspectors","edr","antivirus"]

# Devices the EDR sees
covered = devices where inspectors contains "<edr-inspector-slug>"

# Compute devices the EDR does NOT see — coverage gap
gap = devices where inspectors does not contain "<edr-inspector-slug>"

# Distinguish "not yet inspected at all" from "EDR specifically missing"
unmanaged = devices where inspectors only contains "active-directory-inspector"
edr_missing_specifically = gap minus unmanaged
```

Every EDR recipe must surface `gap` and `edr_missing_specifically` as
`🔍 REVIEW` (coverage gap) — not as `❌ NON-COMPLIANT` if the device hasn't been
locally inspected at all (the absence may be because no OS inspector has run, not
because EDR is genuinely missing).

> **Note:** The `inspectors` filter isn't yet a server-side parameter on
> `liongard_device`, so the array intersection happens client-side. When the
> filter eventually ships server-side, swap to it.

## "Servers vs. Workstations" — partner-confirmed availability

Where the EDR exposes a server filter, use it directly. Where it doesn't, fall
back to the device inventory:

```
# Device-inventory fallback for server/workstation split
liongard_device LIST environmentId=<ENV_ID> fields=["hostname","class","role","inspectors","operatingSystem"]
  → filter where class == "server" AND inspectors contains "<edr-slug>"
  → filter where class in ["workstation","laptop"] AND inspectors contains "<edr-slug>"
```

This works for **every** EDR — Huntress, ESET, Webroot, etc. — because the
device's `class` / `role` / `operatingSystem` come from the OS / RMM
inspector, not from the EDR. As long as both inspectors see the device, you
can split it.

## "High alerts / threats" — coverage notes

| Inspector | Where to find threats | Notes |
|---|---|---|
| SentinelOne | metric `1043` "Systems With Active Threats Count" + `Threats[]` | Full lifecycle in dataprint |
| Huntress | `Organization.incident_reports_count` | **Cumulative — no active/resolved split**; supplement from Huntress portal |
| Bitdefender | metric `1072` "Infected Systems Count" | |
| CrowdStrike | "Total Detections Count" (proposed metric) | Use `Detections[]` array length |
| Sophos Central | "Endpoints with Threat Health Not In Good State" metric | |
| ESET | not available | Refer to ESET console |
| Webroot | metric `835` "Infected Device Count" | |

## How recipes use this matrix

Every EDR recipe under `recipes/single-system-analysis/by-inspector/` includes an
**Onboarding QA — Endpoint Posture** section that:

1. Answers the six standard questions using the inspector's available metrics.
2. Flags fields the inspector cannot answer with a coverage note pointing back
   here.
3. Falls back to the asset inventory for "Not protected" and (when needed)
   server-vs-workstation splits.

The future cross-system recipe `recipes/system-type-assessment/all-edrs.md` uses
this matrix as its decision table — for each of the six questions, it iterates
the deployed EDRs and aggregates per-inspector results into one row per EDR plus
a unified "fleet" row.

## Maintenance

When a new EDR inspector ships or an existing one adds capabilities:

1. Run an onboarding QA against a test environment.
2. Confirm or update the row in this matrix.
3. Update the corresponding `recipes/single-system-analysis/by-inspector/<edr>.md`.
4. Update `recipes/system-type-assessment/all-edrs.md` if the cross-system rollup
   needs adjustment.

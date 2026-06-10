# `/config` — MSP-Wide Configuration

This folder centralizes every MSP-static value (brand identity, preferred
vendor stack, SLA baselines, privacy / scrub policy, cost estimates) so
recipes don't have to repeat them. The MSP fills out their values **once
here**, and every recipe in `/recipes/` references this config.

## The two files

| File | Tracked? | Purpose |
|---|---|---|
| `msp-config.yaml` | ✅ tracked | The library's default template. Ships with placeholder values like `<Your MSP Name>`. Never edit this with your real values — the file ships with the library. |
| `msp-config.local.yaml` | ❌ gitignored | The MSP's actual values. Override only what you need; the rest inherits from the tracked defaults. |
| `msp-config.local.yaml.example` | ✅ tracked | A worked example showing what `msp-config.local.yaml` typically looks like. Copy this to start. |

## Adopting the library for your MSP

```bash
cp config/msp-config.local.yaml.example config/msp-config.local.yaml
# edit msp-config.local.yaml with your real values
```

That's it. Every recipe now uses your brand, preferred stack, and SLAs.

## What's in the config

The config is organized into six sections — see `msp-config.yaml` for
the full schema with inline comments:

1. **Brand identity** — company name, colors, logo, letterhead, fonts
2. **Output defaults** — default audience tone, default format, date format
3. **Preferred vendor stack** — your standard EDR / backup / firewall / RMM / PSA / etc.
4. **MSP-standard SLAs** — MFA %, patch cadence, EDR coverage, backup recency, etc.
5. **Privacy + scrub policy** — redaction defaults, scrub-patterns path
6. **Cost estimates (optional)** — populate to surface budget figures in roadmap deliverables

## How recipes consume the config

Recipes that reference MSP-wide values use template syntax:

```yaml
output:
  filename: "<customer>-PBR-<period>.<ext>"
  # brand inherits from config/msp-config.yaml — no per-recipe override needed
```

When an agent renders a recipe, it resolves brand / vendor / SLA values
in this order:

1. **Local override** — `msp-config.local.yaml` (the MSP's actual values)
2. **Tracked default** — `msp-config.yaml` (placeholder library values)
3. **Recipe inline override** — the recipe's own customization block,
   if the recipe specifies a value explicitly (rare — used when one
   deliverable needs a stricter or looser threshold than the MSP standard)

## Why this exists

Without the central config, every recipe duplicated ~8–12 lines of
MSP-static boilerplate. With ~70 recipes shipped or planned, an MSP
adopting the library would have to find-and-replace their brand info
in ~70 files. The central config makes adoption a one-file edit and
prevents drift as the MSP's branding or preferred stack evolves.

## Notes on the scrub policy

The `scrub_patterns_path` value points to a **gitignored** file
containing partner / customer / proprietary names that must never
appear in tracked files. The pre-commit grep check (see `CONTRIBUTING.md`)
uses this file to enforce the scrub policy. The file lives outside
this folder — at the repo root, named `.scrub-patterns` by default.

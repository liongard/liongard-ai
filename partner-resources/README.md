# Partner Resources

Tools, templates, and configuration for MSPs that want to customize or extend
the Liongard Prompt Library beyond the out-of-the-box recipes.

## Contents

| Folder / File | Purpose |
|---|---|
| `config/` | MSP-level configuration (`msp-config.yaml`) — set your company name, branding, and default SLA thresholds here so all recipes inherit them |
| `personas/` | Per-persona guides — how each MSP role (NOC, SOC, vCIO/AM, TAM, Sales, Executive, Finance) typically uses recipes |
| `tools/` | Skills and automation helpers for running recipes inside AI agents |
| `CONTRIBUTING.md` | How to customize recipes, author new ones, and submit them back to the library |

## Quick start

1. Copy `config/msp-config.local.yaml.example` to `config/msp-config.local.yaml`
   and fill in your MSP name, branding colors, and SLA overrides.
2. Run any recipe — it will inherit your config automatically.
3. See `CONTRIBUTING.md` for how to tailor a recipe for a specific customer.

# Repository Architecture

`liongard-ai` serves **two related but distinct purposes** in one repository.
This page is the map. If partners are unsure "what do I actually sync and use?",
send them here.

---

## The two parts

### Part 1 — MCP Connector & Plugin (get connected)

Everything needed to install the Liongard plugin and connect a client to the
hosted Liongard MCP server. You use this **once** to get set up.

| Folder | What it is |
| --- | --- |
| `plugins/liongard/` | **Canonical** Claude Code plugin package: skills, slash commands, agents, plugin manifest. This is what `/plugin install liongard` ships. |
| `.claude-plugin/` | Marketplace manifest (`marketplace.json`) for `/plugin marketplace add`. |
| `.claude/` | **Auto-generated mirror** of `plugins/liongard/{skills,commands}` so Claude Code auto-loads them when launched inside this repo. Never hand-edit — regenerate with `scripts/sync-plugin-to-claude.sh`. |
| `docs/` | MCP overview, authentication, tools/prompts reference, per-client setup, harness matrix, troubleshooting. |
| `scripts/` | Config generator, installers, smoke test, repo validation, the plugin→`.claude` sync script. |
| `examples/` | Example prompts and workflows. |

### Part 2 — Recipe Library (do the work)

The agent-friendly recipe library that turns live Liongard data into consistent
MSP artifacts. You **sync this, customize `config/` once, and reference recipes**
in your prompts — repeatedly, as part of normal delivery work.

| Folder | What it is |
| --- | --- |
| `config/` | MSP-wide settings (brand, vendor stack, SLAs). Copy `msp-config.local.yaml.example` → `msp-config.local.yaml` and edit once. Recipes inherit. |
| `recipes/` | The recipes themselves, grouped by category (single-system, system-type, domain, compliance, QBR, onboarding, sales, roadmap, external-data). |
| `personas/` | Per-role indexes (NOC, SOC, vCIO/AM, TAM, Sales, Executive, Finance) listing the recipes each persona uses. |
| `reference/` | Inspector aliases, asset-field reference, QA coverage matrix, QA retry pattern, persona × recipe matrix, future-recipes roadmap. |
| `primitives/` | Semantic registry (`registry.yaml`) + per-inspector metric primitive YAML. |
| `templates/` | Recipe skeleton + reusable customization/output blocks. |
| `partner-resources/` | Partner-facing tools and skills (recipe picker, recipe scaffold generator). |
| `ontology/` | JSON-LD governance context for cross-cutting signals. |
| `schemas/` | JSON Schema for recipe + primitive validation. |

---

## The two agent guides

Two files guide AI agents, for two different jobs. Don't confuse them:

| File | Audience | Covers |
| --- | --- | --- |
| [`AGENTS.md`](AGENTS.md) | Agents/contributors working **on** this repo | Repo purpose, source-of-truth locations, scrub guardrails, validation steps. |
| [`recipes/AGENTS.md`](recipes/AGENTS.md) | Agents **running recipes** at runtime | Orient → route (recipe picker) → pre-flight format/audience questions → render rules (HTML vs markdown). |

---

## Single source of truth — skills & commands

`plugins/liongard/skills/` and `plugins/liongard/commands/` are **canonical**.
The repo-root `.claude/skills/` and `.claude/commands/` are an auto-generated
mirror kept in sync by `scripts/sync-plugin-to-claude.sh`.

- **Edit** skills/commands only under `plugins/liongard/`.
- **Run** `bash scripts/sync-plugin-to-claude.sh` after editing.
- **CI/pre-commit** can verify with `bash scripts/sync-plugin-to-claude.sh --check`.

Never hand-edit `.claude/skills` or `.claude/commands` — those edits are
overwritten on the next sync.

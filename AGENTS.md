# AGENTS.md

Guidance for AI agents working **on** this repository (contributing, packaging,
validating). For running recipes against a live tenant at runtime, see
[`recipes/AGENTS.md`](recipes/AGENTS.md) instead. Repo map: [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Purpose

`liongard-ai` is the public integration repo for the hosted Liongard MCP server.
It contains customer-facing docs, Claude Code plugin packaging, setup commands,
skills, installers, and validation scripts.

## Public Source Of Truth

- Public docs live in `docs/`.
- Claude Code plugin package lives in `plugins/liongard/` — **canonical** for
  skills and slash commands.
- Root `.claude/` is an **auto-generated mirror** of
  `plugins/liongard/{skills,commands}` (so Claude Code auto-loads them when
  launched from this repo). Never hand-edit it; regenerate with
  `bash scripts/sync-plugin-to-claude.sh`.
- Current MCP behavior should be checked against a live or test Liongard tenant
  using `tools/list`, `prompts/list`, and the smoke-test script. Public docs
  should describe product behavior, not implementation locations.

## Rules

- Do not commit real Liongard tokens, customer names, or tenant data.
- Bearer Access Token auth is the supported setup path:
  `Authorization: Bearer <accessKeyId>:<accessKeySecret>`.
- OAuth is experimental/client-dependent unless verified for a specific harness.
- Use `liongard_launchpoint` for system questions; do not reintroduce a systems
  tool in docs or skills.
- Include `liongard_agents` when documenting native tool coverage.
- Keep harness docs honest: mark guides as verified only after a real install
  and `liongard_environment COUNT` succeeds.

## 🛑 CRITICAL GUARDRAIL — Partner and customer names

**No partner names appear in any tracked asset, ever.** This applies to:

- **Partner names** (MSPs, vendors, integrators who shared materials with
  Liongard) — use "partner", "an MSP", "a partner-provided assessment".
- **Partner-employee names** appearing in shared files.
- **Customer / tenant names** that originated in partner-shared materials.
- **Real environment names, system names, hostnames, IPs, account IDs**,
  or any other specific identifier from a partner-shared file or customer
  environment.
- **Internal Liongard test-environment names** not appropriate for a public
  repo.

This applies to **every** tracked file: recipes, references, templates,
docs, commit messages, PR descriptions.

When context requires referencing the origin, use generic phrasing:
`"the partner onboarding QA audit"`, `"a partner-shared spreadsheet"`,
`"a customer environment"` — never a specific name.

The `/recipes/` and `/reference/` directories in this repo are
customer-facing. Treat them with the same scrub discipline as the plugin
docs.

## Running Recipes

When a user asks to run a Liongard recipe (assessment, QBR, compliance check, etc.),
read `recipes/AGENTS.md` before starting. It covers recipe routing, pre-flight format/audience
questions, HTML vs markdown rendering rules, and the session start checklist.

**Generated reports** are always written to `outputs/environments/<customer-slug>/`
(created if missing) — never to the repo root. `outputs/` is gitignored so customer
data never commits. See `recipes/AGENTS.md` § 6.

## Validation

Run before release:

```bash
node scripts/validate-repo.js
node scripts/liongard-mcp-config.js --client generic --print
```

Run `scripts/liongard-mcp-smoke-test.js` with a real test token before marking a
harness verified.

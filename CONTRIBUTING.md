# Contributing to liongard-ai

Thanks for helping make the Liongard AI experience better. This repo holds
customer-facing documentation, slash commands, and skills for the Liongard
MCP — most improvements fall into one of four buckets:

1. **Docs** — keep the guides under [`docs/`](docs/) current as the MCP
   evolves.
2. **Slash commands** — add, improve, or fix commands under
   [`plugins/liongard/commands/`](plugins/liongard/commands/) (canonical home).
3. **Skills** — add, improve, or fix Claude Code skills under
   [`plugins/liongard/skills/`](plugins/liongard/skills/) (canonical home).

> **Canonical vs. mirror.** `plugins/liongard/{commands,skills}/` is the source
> of truth (what `/plugin install liongard` ships). The repo-root `.claude/`
> directory is an auto-generated mirror — never hand-edit it. After changing a
> command or skill, run `bash scripts/sync-plugin-to-claude.sh` and commit both.
4. **Install scripts** — improve the bash installers under
   [`scripts/`](scripts/).

## Ground rules

- **Audience is external.** Write for MSP operators and their engineers,
  not for Liongard employees. Avoid internal jargon or references to
  internal environments.
- **No secrets.** Never commit a real token, customer name, or PII.
- **Keep it working.** Before opening a PR, run every slash command and
  install script you touched against a live tenant (Liongard employees can
  use any test tenant; external contributors can use a sandbox tenant).
- **Match existing style.** Skills and commands share conventions — read
  neighboring files before writing new ones.

## Adding a slash command

1. Create `plugins/liongard/commands/<name>.md` (canonical home).
2. Start with YAML front matter:

   ```markdown
   ---
   description: One-sentence description Claude Code will show in its slash menu.
   argument-hint: "[optional] <required>"
   ---
   ```

3. Keep the body focused on one job. If the command is going to grow, split
   into multiple commands (see `/liongard-setup` delegating to
   `/liongard-setup-api-key` and `/liongard-setup-oauth`).
4. Never echo or log secrets. Always redact tokens in previews.
5. Link to docs in `docs/` when useful instead of repeating content.

## Adding a skill

1. Create `plugins/liongard/skills/<name>/SKILL.md` (canonical home; each skill
   in its own folder). Run `bash scripts/sync-plugin-to-claude.sh` after.
2. Front matter must include:

   ```markdown
   ---
   name: liongard-<kebab-case>
   description: When to use this skill. Be specific — the description is how Claude decides to load it.
   ---
   ```

3. Follow the [skill authoring conventions](docs/skills.md#skill-authoring-conventions):
   resolve IDs first, prefer server-side prompts when available, honor
   pagination, respect scope.
4. List the skill in [`docs/skills.md`](docs/skills.md).

## Adding a client guide

1. Create `docs/clients/<client>.md`.
2. Mirror the structure of the existing client guides (prerequisites →
   quick install → manual install → verify → troubleshoot).
3. Link it from [`README.md`](README.md#supported-clients) and
   [`docs/quickstart.md`](docs/quickstart.md).

## Opening a pull request

1. Fork the repo and create a topic branch.
2. Commit with a clear message (`docs: fix Cursor install path on Windows`,
   `skill: tighten compliance audit scope handling`, …).
3. Open a PR describing the change and how you verified it.
4. A maintainer will review, request changes if needed, and merge.

## Release checklist

Before tagging or publishing a plugin/doc release:

1. Cross-check public capability docs against a current Liongard test tenant by
   calling `tools/list`, `prompts/list`, and the safe smoke-test flow.
2. Run:

   ```bash
   node scripts/validate-repo.js
   node scripts/liongard-mcp-config.js --client generic --print --non-interactive \
     --instance example.app.liongard.com \
     --token lg_mcp_example:replace-with-access-key-secret
   ```

3. Run `node scripts/liongard-mcp-smoke-test.js` against a real test tenant.
4. Verify every harness marked `verified` in `docs/harnesses.md` by installing
   or reconnecting it and successfully calling `liongard_environment COUNT`.
5. Confirm no token, customer name, or PII is present in commits.

## Questions

Open a GitHub issue or reach out to your Liongard CSM.

---

## Recipe library contributions

The sections below cover authoring, scrubbing, and verifying recipes under
`/recipes/`. If you are only working on the plugin (skills, commands,
scripts), you can skip to the [PR checklist](#opening-a-pull-request) above.

### § 0. MSP-wide config — recipes inherit from `/config/msp-config.yaml`

Before writing a recipe, know where MSP-wide static values live: **not in
the recipe itself.** Brand identity, preferred vendor stack, MSP-standard
SLAs, privacy policy, and cost estimates all live in `/config/msp-config.yaml`.
Recipes inherit by default — they only carry per-recipe overrides when a
specific deliverable needs a different value.

| File | Tracked? | Purpose |
|---|---|---|
| `config/msp-config.yaml` | ✅ | Library defaults with placeholder values |
| `config/msp-config.local.yaml` | ❌ (gitignored) | MSP's actual values |
| `config/msp-config.local.yaml.example` | ✅ | Worked example to copy |

When writing a recipe's customization block:
- **Do NOT include a `brand:` block** unless the recipe specifically needs
  to override brand. Reference inheritance with a comment instead:
  `# brand: inherits from config/msp-config.yaml — override per-recipe only if needed`
- **Do NOT inline default SLA values** that already live in the config's
  `slas:` block. Override per-recipe only when a deliverable needs a
  stricter or looser threshold than the MSP standard.
- **Do NOT inline a `preferred_stack:` / `vendor_replacement_preferences:`
  block** — reference the config inheritance pattern (see the cross-cutting
  recipes for examples).

See `/config/README.md` for the full schema.

### § 1. Recipe anatomy

Start every new recipe by copying [`templates/recipe-skeleton.md`](./templates/recipe-skeleton.md).
The skeleton includes:

- **YAML frontmatter** — `name`, `description`, `compatibility`, optional `personas`,
  optional `output_formats`. Required on entry-point recipes under `/recipes`. The
  `description` field controls when the recipe auto-triggers as a skill.
- **Overview** — what the recipe produces, in two sentences.
- **When to use** — trigger phrases and scenarios.
- **Inputs** — environment ID, system ID, time period, customer name, etc.
- **Customize for your MSP** — the customization block (section names, SLAs, output
  format, areas of expertise, naming conventions).
- **Liongard data sources** — metric IDs (with inspector + JMESPath), asset inventory
  fields, parent/child system rules.
- **Output formats** — Word / PowerPoint / Markdown / Excel patterns.
- **Insights & recommendations** — generation patterns the agent applies after fetch.
- **Data gaps** — what to flag when an inspector is missing or a metric returns null.
- **Verification log** — a tail block where the agent records every query it ran and the
  result shape (no concrete values, just shapes).

### § 2. Scrub policy — applied before every commit

This library is published to a **public** GitHub repo. The scrub policy is strict.

#### 🛑 CRITICAL GUARDRAIL — No partner names. No customer names. Ever.

**No partner names appear in any tracked asset, ever.** The same rule
applies to partner-employee names, customer / tenant names that originated
in partner-shared files, and internal Liongard test-environment names.

This applies to **every** tracked file *and* every external artifact
generated from this project — recipes, references, templates, commit
messages, PR descriptions, support cases.

When context absolutely requires referencing the origin, use generic
phrasing:
- "the partner onboarding QA audit"
- "a partner-shared spreadsheet"
- "a customer environment" (never a specific customer name)

If you find yourself typing a specific partner or customer name into a
tracked file, **stop** — find a generic phrasing or strip the reference.

#### Full scrub table

| What | Rule |
|---|---|
| **Partner names** (MSPs, vendors, integrators who shared materials) | **Strip entirely.** Use "partner" / "a partner" / "the partner onboarding QA audit" |
| **Partner-employee names** | Strip entirely |
| Customer / tenant names from partner-shared materials | Replace with `<TENANT_NAME>`, `<CUSTOMER_NAME>` |
| Environment names (including internal Liongard test envs) | Replace with `<ENVIRONMENT_NAME>` |
| Env / system / account IDs | Replace with `<ENV_ID>`, `<SYSTEM_ID>`, `<ACCOUNT_ID>` |
| Hostnames, FQDNs, IPs, MACs | Replace with shape annotations (e.g. `<hostname>`, `<ipv4>`) |
| Email addresses, UPNs | Replace with `<email>` or `<upn>` |
| Example JMESPath evaluated values | Replace with shape annotations: `<string>`, `<integer>`, `<bool>`, `<ISO timestamp>`, `<UUID>`, `<set<string>>` |
| Partner-specific terminology, scoring, role names | Strip or generalize |
| **Keep**: JMESPath queries, metric IDs, inspector slugs, thresholds | These are recipe value, not data |

#### Pre-commit grep

The scrub check uses a **local-only patterns file** so that partner /
customer names never end up hard-coded into the tracked tree. Create a
`.scrub-patterns` file at the repo root (already in `.gitignore`) with one
regex per line. Example:

```
# .scrub-patterns — gitignored; local-only. One regex per line.
<PartnerNameOne>
<PartnerNameTwo>
<InternalEnvName>
```

Then run before opening a PR:

```bash
# Should return no matches in tracked files
git ls-files | xargs grep -lEf .scrub-patterns 2>/dev/null

# Concrete env/system IDs that may have crept in
git ls-files | xargs grep -nE '\b(envId|systemId)\s*=\s*[0-9]{3,}' 2>/dev/null
```

Add to `.scrub-patterns` whenever a new partner shares materials with you or a
historical leak is discovered. The file is gitignored — never commit it.

### § 3. Where files go

| If your recipe is for… | It goes in… |
|---|---|
| One specific inspector (e.g., SentinelOne) | `recipes/single-system-analysis/by-inspector/<inspector-slug>.md` |
| All systems of a type (e.g., all firewalls) | `recipes/system-type-assessment/all-<type>.md` |
| A cross-cutting domain (e.g., authentication) | `recipes/domain-assessment/<domain>.md` |
| Cyber-insurance evidence | `recipes/compliance/cyber-insurance/{cyber-insurance-readiness.md, domains/, carriers/}` |
| Other compliance frameworks (CMMC, HIPAA) | `recipes/compliance/<framework>/` |
| Whole-environment QBR/PBR | `recipes/environment-quarterly-lookback/` |
| Forward-looking lifecycle / EOL / expiration | `recipes/roadmap-planning/` |
| Pre-sales discovery | `recipes/sales-assessment/` |
| New-client onboarding | `recipes/onboarding-assessment/` |
| Documented data Liongard doesn't inspect | `recipes/external-data/` |

### § 4. Persona index updates

When adding a recipe relevant to a persona, update `personas/<role>/README.md` to link
to it with a one-line "what this gives me" hook.

### § 5. Frontmatter rules

Required on every file under `/recipes`:

```yaml
---
name: <kebab-case-skill-name>
description: >
  <2–3 sentences. Describe trigger phrases, the produced artifact, and the
  inspectors or data sources used. Start with "Use this skill when…".>
compatibility: "Requires Liongard MCP: <tool-list>"
personas: [vcio-account-manager, noc]   # optional
output_formats: [word, pptx, markdown]  # optional
---
```

Plain markdown (no frontmatter) is fine for everything outside `/recipes` — persona
indexes, reference docs, templates.

### § 6. Customization block — non-negotiable

Every recipe must include a customization block near the top so the MSP can edit it
without touching recipe internals. See `templates/customization-block.md` for the
canonical format. Required knobs: output format (with default), section names, SLA
thresholds, areas of expertise / inspector availability, naming conventions, audience
tone.

### § 7. Inspector aliases — link, don't duplicate

When a recipe references an inspector or documents the `liongard_system LIST query=`
keyword, **link to `reference/inspector-aliases.md`** instead of writing your own
keyword table. That file is the single source of truth for:

- The API keyword that goes into `query=`.
- Every common shorthand a user might say (S1, M365, O365, Entra, AAD, FGT, KB4,
  NinjaRMM/NinjaOne, LabTech/CW Automate, etc.).
- Parent/child system patterns (SentinelOne, Datto BCDR, Acronis, Veeam, Axcient,
  Umbrella).
- Common gotchas (Entra/Azure AD lives in the M365 inspector, not the Azure
  inspector; Sophos has three distinct inspectors).

When you add a new inspector recipe, **also add the inspector's row to
`reference/inspector-aliases.md`** so the alias index stays complete.

### § 8. Verification and PR checklist

#### 🚨 CRITICAL — JMESPath must be validated against live dataprints

Every JMESPath path written into a recipe MUST be confirmed against a real
Liongard dataprint via MCP before it is committed.

**Required workflow for every new recipe:**

1. Find a live system: `liongard_launchpoint LIST inspectorId=<N>`
2. Explore the schema: `liongard_launchpoint GET_OVERVIEW systemId=<X> environmentId=<Y>`
3. Confirm each path: `liongard_metric EVALUATE jmesPathQuery="<path>" systemId=<X> environmentId=<Y>`
4. Label every path: **VALIDATED**, **SCHEMA_CONFIRMED**, or **PROPOSED**

**Common catalog traps (real bugs found in production):**

| Trap | Example | Reality |
|---|---|---|
| Version number filter misses modern OS | `OperatingSystemVersionNum < 6.2` for EOL workstations | Windows 10 has VersionNum=10; filter only catches pre-Win8 |
| `contains()` on array of full DNs | `contains(MemberOf, 'RoarExclude')` | MemberOf contains full DN strings; exact-match never fires |
| Duration field unit mismatch | `AccountLockoutDuration >= 15` (expecting minutes) | Field is in hours (float); 15 min = 0.25 |
| String field treated as boolean | `Services[?enable_status == 'true']` | enable_status is `"enabled"` / `"disabled"` string |
| Object field treated as scalar | `remain_life < 20` | remain_life is `{trustable: bool, value: int}` object |
| Catalog backtick syntax for strings | `UserActivity==\`Stale\`` | Works in RoarPath but standard JMESPath uses single quotes |

Before opening a PR for a recipe change:

- [ ] Recipe follows `templates/recipe-skeleton.md`.
- [ ] Frontmatter present (if under `/recipes`).
- [ ] Customization block present.
- [ ] **All JMESPath paths validated against a live dataprint.** Verification
      log at the bottom records system ID, environment ID, inspection date, and
      confirmed result shape for every path.
- [ ] **MSP-wide values inherit from `/config/msp-config.yaml`** — no
      duplicated `brand:`, no inlined `preferred_stack:`, no inlined SLA defaults.
- [ ] **Assessment recipes lead with the reconciled asset inventory**
      (`liongard_identity`, `liongard_device`, `liongard_domain`) as the
      primary source for current-state counts. See `reference/asset-fields.md`.
- [ ] Scrub policy applied — no partner/customer/env names, no evaluated values.
- [ ] Inspector slug + ID match `reference/inspector-aliases.md`.
- [ ] Persona index updated if persona relevance changes.

#### Four-source coverage check (required for every new recipe)

Confirm the recipe covers what the MSP audience expects by cross-referencing:

- [ ] **`reference/onboarding-qa-coverage.md`** — if the recipe touches EDR,
      endpoint OS, firewall, backup, RMM, or identity, the recipe addresses
      the six standard QA questions or explicitly notes which are unavailable.
      Never reference the partner by name; use "the partner onboarding QA audit".
- [ ] **CIS Controls (v8.1)** — SOC / TAM / compliance recipes map findings
      to CIS Controls (use the cyber-insurance domain files as the mapping
      reference).
- [ ] **Cyber-insurance domain files** —
      `recipes/compliance/cyber-insurance/domains/{auth,endpoint,backup,network,governance,regulatory,vendor}.md`.
      Cover the referenced metrics or flag them as gaps.
- [ ] **QBR** — `recipes/environment-quarterly-lookback/quarterly-business-review.md`.
      If the QBR chains this recipe, confirm the recipe exposes what the QBR
      needs.

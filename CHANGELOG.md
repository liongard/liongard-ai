# Changelog

## [Unreleased]

### Fixed

- Quick start accuracy pass:
  - `scripts/liongard-mcp-config.js --print` now emits paste-able configs with
    the real access token (previously always redacted, producing configs that
    failed auth when copied verbatim). A stderr note warns that the output
    contains the token.
  - VS Code configs now use the current format: `mcp.json` (workspace
    `.vscode/mcp.json` or user-level via **MCP: Open User Configuration**)
    with the `servers` key — replacing the removed `chat.mcp.servers`
    settings.json key across the generator, `docs/clients/vscode.md`,
    `docs/harnesses.md`, and `docs/troubleshooting.md`.
  - `docs/tools-reference.md`: `liongard_report` documents the supported
    `LIST` / `GET` operations (removed the unsupported `GENERATE`); added a
    `liongard_events` section; `liongard_asset` is documented as removed (not
    a resolving alias). `README.md` tool catalog now includes
    `liongard_events`.
  - GitHub Actions workflow and pre-commit hooks no longer fail on the public
    repo: internal-only governance validators are skipped when
    `internal/scripts/` is absent, and public checks (`validate-repo.js`,
    `.claude/` mirror sync, YAML/JSON syntax) run for everyone.
  - Scrubbed internal test-tenant references from
    `primitives/metrics/webroot.yaml` and
    `primitives/metrics/managed-printer.yaml`.
  - Removed references to non-distributed `internal/scripts/` tooling from
    `primitives/registry.yaml` and `templates/recipe-skeleton.md`.
  - Fixed `README.md` "Using a recipe" ordered-list rendering and switched
    recipe/metric counts to drift-resistant approximations (exact counts live
    in `primitives/registry.yaml` `stats`).

### Added

- `scripts/sync-plugin-to-claude.sh` now mirrors `plugins/liongard/agents`
  into `.claude/agents` alongside skills and commands.
- `docs/capability-status.md` release checklist covers publishing to the
  public GitHub repo (sync, metadata, README rendering, CI status).

## [0.2.3] - 2026-06-01

### Changed

- Updated 49 metric primitive YAML files across all major inspector categories
  with refined field definitions, additional metrics, and improved validation labels.
- Significantly expanded `primitives/registry.yaml` (semantic index rebuilt from
  latest primitives — recipe, inspector, and metric impact tables all updated).

### Added

- README files for config, partner-resources, and all 7 persona directories
  (previously excluded by rsync; now included in partner-facing distribution):
  - `config/README.md`
  - `partner-resources/README.md`, `partner-resources/config/README.md`,
    `partner-resources/personas/README.md`
  - `personas/README.md` + per-persona indexes for all 7 roles

## [0.2.2] - 2026-06-01

### Changed

- Migrated 4 recipes from deprecated `liongard_asset` to new reconciled tools
  (`liongard_identity`, `liongard_device`, `liongard_domain`):
  - `recipes/compliance/cyber-insurance/cyber-insurance-readiness.md` — updated
    primary data-fetch to use `liongard_identity LIST`, `liongard_device LIST`,
    and `liongard_domain LIST`; expanded field sets and cross-system guidance.
  - `recipes/compliance/cyber-insurance/domains/auth.md` — updated asset-inventory
    primacy section to reflect `liongard_identity` as the authoritative cross-system
    identity record; enriched `mfaStatus`, `accountActivity`, and `privileged` field
    semantics.
  - `recipes/system-type-assessment/all-endpoints.md` — Step 1 now uses
    `liongard_device LIST` as the authoritative device roster; updated cross-system
    intelligence notes for `status`, `edr`, and `antivirus` fields.
  - `recipes/system-type-assessment/all-identity-providers.md` — Step 3 now uses
    `liongard_identity LIST` with enriched field list; expanded reconciled-record
    semantics for `mfaStatus`, `accountActivity`, and `privileged`.

### Added

- README files for recipe subcategories:
  - `recipes/compliance/cyber-insurance/README.md`
  - `recipes/external-data/README.md`
  - `recipes/single-system-analysis/README.md`
  - `recipes/system-type-assessment/README.md`
  - `partner-resources/tools/skills/recipe-generator/README.md`

## [0.2.1] - 2026-05-28

### Changed

- Registry rebuilt: 937 metric primitives across 76 inspectors (updated from
  1009/73 as metric files were refined and 3 new inspectors added).
- Updated 12 single-system recipes (active-directory, bitdefender-gravityzone,
  cisco-meraki, crowdstrike, datto-bcdr, duo-security, jumpcloud, microsoft-365,
  sonicwall, webroot, windows-server, windows-server) with validated JMESPath paths.
- Updated 10 system-type recipes (all-backups, all-cloud-storage, all-edrs,
  all-external-attack-surface, all-identity-providers, all-network-infrastructure,
  all-network-monitoring, all-psa-platforms, all-rmm-platforms,
  all-windows-patching) with coverage cross-checks.
- Updated 47 metric primitive YAML files with refined field definitions.
- `external-attack-surface-deep-dive.md` domain recipe updated.
- `cyber-insurance/domains/endpoint.md` updated.
- `CONTRIBUTING.md`: added §1 (recipe anatomy), §4 (persona index updates),
  §6 (customization block), common JMESPath catalog-trap table in §8, and
  expanded scrub policy with `.scrub-patterns` guidance.
- `README.md`: updated primitives count to reflect current registry.
- `ontology/context.jsonld` updated.

## [0.2.0] - 2026-05-26

### Added

- Recipe library: 121 recipes (73 inspectors, 1009 metric primitives) across
  7 MSP personas. New `/recipes/`, `/primitives/`, `/reference/`, `/personas/`,
  `/templates/`, `/config/` top-level folders.
- Semantic registry (`primitives/registry.yaml`): compiled three-way index
  enabling inspector-based recipe discovery and metric impact analysis.
- 7 persona index pages (NOC, SOC, vCIO / Account Manager, Technical Alignment
  Manager, Sales, Executive, Accounting / Finance).
- Reference library: `inspector-aliases.md`, `asset-fields.md`,
  `onboarding-qa-coverage.md`, `qa-retry-pattern.md`,
  `personas-recipe-matrix.md`, `future-recipes-roadmap.md`,
  `cyber-insurance-forms-reference.md`.
- MSP-wide config inheritance pattern (`config/msp-config.yaml` +
  `config/msp-config.local.yaml.example`).
- Recipe templates: `recipe-skeleton.md`, `customization-block.md`,
  `output-block-word.md`, `output-block-pptx.md`.
- Partner-resources mirror under `partner-resources/` (recipe-generator skill +
  recipe-picker skill for partner-facing distribution).
- `AGENTS.md` guardrail: partner-name / customer-name scrub policy extended.
- `CONTRIBUTING.md`: recipe authoring guide, scrub policy, four-source coverage
  check, JMESPath validation workflow, and MSP config inheritance rules merged.

## Unreleased

- Add Claude Code marketplace and plugin packaging for Liongard MCP.
- Document Bearer Access Token auth as the supported setup path.
- Add cross-harness setup guidance, config generation, validation, and smoke
  testing helpers.

# Recipe Generator (Project Skill)

A project-local skill that scaffolds **per-inspector single-system recipes**
in this Liongard Prompt Library. The skill produces a structurally consistent
draft from a small per-inspector YAML spec, leaving explicit `<!-- TODO -->`
markers for the vendor-specific narrative the author fills in by hand.

> **Scope:** single-inspector, single-vendor recipes only. The skill does
> NOT scaffold cross-inspector rollups (`all-*.md`), compliance recipes
> (cyber-insurance, CMMC, HIPAA), external-data files, or domain-assessment
> cross-cutting recipes. Those are hand-crafted because the synthesis is
> the whole point.

## Files in this skill

| File | Purpose |
|---|---|
| `SKILL.md` | The skill instructions Claude follows when invoked |
| `references/recipe-spec-format.md` | Full spec field documentation |
| `assets/recipe-spec-template.yaml` | Blank template — copy + fill |
| `assets/example-spec-cisco-meraki.yaml` | Worked example |

## Installation (Cowork / Claude Desktop)

The skill is authored here so it's git-tracked with the rest of the
library. To make it auto-trigger in your Cowork or Claude Desktop sessions:

```bash
# macOS — symlink into the user-level skill directory
ln -s "$(pwd)/tools/skills/recipe-generator" ~/.claude/skills/recipe-generator

# Or copy if you prefer no symlinks
cp -r "$(pwd)/tools/skills/recipe-generator" ~/.claude/skills/recipe-generator
```

After installation, restart your Cowork / Claude Desktop session and the
skill should appear in available skills with name `recipe-generator`.

## Manual invocation (no install required)

If you don't install the skill, you can still use it by pointing Claude at
`SKILL.md`:

```
Read tools/skills/recipe-generator/SKILL.md and follow it to scaffold a
recipe for Cisco Meraki using the spec at
tools/skills/recipe-generator/assets/example-spec-cisco-meraki.yaml.
```

This works in any session that has read access to this project.

## Authoring a new spec

1. Copy `assets/recipe-spec-template.yaml` to a working location:
   ```bash
   cp tools/skills/recipe-generator/assets/recipe-spec-template.yaml \
      tools/skills/recipe-generator/specs/<inspector-slug>.yaml
   ```
   (The `specs/` directory is gitignored by default — these are working
   files, not project artifacts. Commit them only if you want the generation
   inputs reproducible.)
2. Fill in the required fields (inspector identity, recipe metadata,
   metric list).
3. Read the recipe-spec-format reference if you're unsure about a field.
4. Look at `assets/example-spec-cisco-meraki.yaml` for shape and detail
   level.
5. Invoke the skill (or paste the spec into a Claude prompt asking for
   scaffolding).

## After generation

The skill writes the recipe to
`recipes/single-system-analysis/by-inspector/<slug-without-inspector-suffix>.md`
and reports:
- The path of the file written.
- A count of `<!-- TODO -->` markers and their section names.
- Any `[PROPOSED]` metrics referenced (these need tracking +
  Jira metric-request tickets to the Core team).

Next steps for the author:
1. Fill the TODO markers using the "Vendor-specific narrative checklist"
   in `SKILL.md`.
2. Add the recipe to `reference/future-recipes-roadmap.md` under the
   "Already shipped" table.
3. If new aliases were introduced, update
   `reference/inspector-aliases.md`.
4. If `[PROPOSED]` metrics were referenced, file Jira tickets via the
   `jira-ticket` skill (Core team, AI Agent product area, Feature
   Enhancement, Medium priority).

# Microsoft Copilot package

Partner-ready Liongard recipe packages for **Microsoft Copilot Studio** and **Microsoft 365 Agent Builder**, compiled from the canonical recipes. Nothing here is hand-maintained recipe content; edit the canonical source and rebuild.

| Path | Purpose |
|---|---|
| `generated-skills/` | Skill edition (recommended): three Copilot Studio skills (`liongard-single-system`, `liongard-rollups`, `liongard-environment`). Setup: `docs/setup-copilot-skill.html`. |
| `generated/copilot-studio/` | Knowledge edition: one compiled recipe per file, grouped for file groups. Setup: `docs/setup-copilot-studio.md`. |
| `generated/agent-builder/` | 20-file Agent Builder edition: consolidated `.txt` bundles. Setup: `docs/setup-agent-builder.md`. |
| `build.config.json` | Scope, skill split, platform limits, path/tool rewrites. |
| `templates/` | Generator templates (skill instructions, agent instructions) and `skill-acceptance-tests.txt`, which is shared per partner and not included in the generic release package. |
| `docs/` | Setup guides and acceptance tests. |

Rebuild (needs PyYAML):

```bash
python3 scripts/copilot/build_skill_package.py     # skill edition + local release package (zips are not committed)
python3 scripts/copilot/build_copilot_package.py   # knowledge editions
```

CI runs both with `--check`. The skill zips and the release package under `generated-skills/release/` are build outputs for distribution and are gitignored.

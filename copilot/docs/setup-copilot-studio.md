# Set up the Liongard agent in Copilot Studio

> DRAFT (proof of concept). Limits verified against Microsoft Learn on 2026-10-05; re-check before release.

You need: a Copilot Studio license, a Liongard access key (Bearer `accessKeyId:accessKeySecret`), and this package (`copilot-studio/`).

1. **Create the agent.** Copilot Studio > Create > New agent. Name it "Liongard MSP Assistant".
2. **Instructions.** Paste the contents of `agent-instructions.txt` into *Instructions* (limit: 8,000 characters; the file is validated to fit).
3. **Connect the Liongard MCP server as the tool layer.** Tools > Add a tool > Model Context Protocol > New. Use the Liongard MCP URL and Bearer authentication from the library's `docs/clients/` setup guides. Enable the `liongard_*` tools. Do not upload data exports as knowledge; live data comes from MCP only.
4. **Fill in the MSP profile.** Edit `msp-profile-template.txt` (brand, preferred stack, SLAs, defaults). Save a copy named `msp-profile.txt`.
5. **Upload knowledge.** Copilot Studio cannot upload folders, so create one *file group* per folder under `file-groups/` and upload that folder's files into it. Upload separately: `recipe-catalog.txt`, `msp-profile.txt`, and the files in `references/`.
6. **Choose the model.** Use a model that follows long multi-step instructions (tested: Claude Opus 5.5). Some models skip steps or detour into built-in skills; if you must use another family (for example for CMMC), run the acceptance tests first.
7. **Publish** to your test channel and run `acceptance-tests.md`.

## One agent, no connected agents

Everything runs in this single agent. Do not add connected agents: connected-agent calls hung unpredictably in testing.

## Large reports run in batches

Copilot limits knowledge searches **per turn**. Rollup recipes (onboarding assessment, system-type rollups, QBR over several systems) therefore run about 4 vendors per turn. The agent ends each turn with "Batch N of M complete. Reply continue for the next batch."; reply `continue` until the final turn, which merges the saved result blocks into one report. Single-system recipes finish in one turn.

Cards with many metrics are split into `<recipe>-part-N.md` files. Upload every file in `file-groups/single-system-assessments/`.

## Updating

Download the newer release package, replace the changed files (compare `manifest.json` checksums), re-upload, and re-run the acceptance tests. Your `msp-profile.txt` is never overwritten by a release.

## Limitations

- Knowledge is retrieved, not executed: retrieval can omit a section. Metric lines are grouped under searchable headings and the agent must search for any missing group; if one still cannot be found it reports "Not evaluated" and lists it under Manual Verification Needed. The acceptance tests exist to catch this.
- The agent must never report a pass without a returned value; check the coverage table of every rollup for "Not evaluated".
- Folder structure is not preserved; groups are by name only.
- Tool-count limits per agent may apply; enable only the `liongard_*` tools your recipes need (see `manifest.json`).

## Skill edition (recommended where Skills are available)

The skill edition ships as a partner release package built by `python3 scripts/copilot/build_skill_package.py`:
`copilot/generated-skills/release/Liongard-Copilot-Studio-<version>.zip` (START-HERE.html, three skill zips, agent-instructions.txt, manifest.json). Acceptance tests (`copilot/templates/skill-acceptance-tests.txt`) are not in the generic package; share them per partner..
Partner setup steps live in `copilot/docs/setup-copilot-skill.html` (shipped as START-HERE.html). Run `--check` in CI; never hand-edit generated output.

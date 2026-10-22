# Set up the Liongard agent in Microsoft 365 Copilot Agent Builder

> DRAFT (proof of concept). Agent Builder accepts at most 20 uploaded files and only doc/docx/ppt/pptx/xls/xlsx/pdf/txt/csv (no `.md`, no `.yaml`), which is why this edition ships `.txt` bundles. Verified 2026-10-05; re-check before release.

1. Open Agent Builder in Microsoft 365 Copilot > Create agent.
2. Paste `agent-instructions.txt` into *Instructions* (8,000-character limit; validated at build time).
3. Fill in `msp-profile-template.txt` and save as `msp-profile.txt`.
4. Upload (all must be `.txt`): `recipe-catalog.txt`, `msp-profile.txt`, the `reference-*.txt` files, and every `bundle-*.txt`. The package manifest reports `uploadFileCount`, which is validated to stay within 20.
5. Connect Liongard live data. Whether Agent Builder in your tenant can attach a custom MCP server depends on your Microsoft 365 / admin configuration (open item). If it cannot, build the agent in Copilot Studio instead (`setup-copilot-studio.md`); without the MCP tool layer this agent can explain recipes but cannot produce data-backed reports.
6. Run `acceptance-tests.md`.

## Limitations

- Bundles concatenate several recipes per file; retrieval may be less precise than the one-recipe-per-file Copilot Studio edition.
- No folders, no YAML: primitives are compiled into reference text, not uploaded.

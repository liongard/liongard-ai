# Output Block — Word (.docx)

How to render a recipe's data as a Microsoft Word document. Recipes that support Word
output should reference this file rather than redefining the layout.

## Document structure

| Element | Style | Notes |
|---|---|---|
| Letterhead | Header section | MSP logo from `output.brand.logo_path` (top-left), company name (top-right). Skip if logo not provided. |
| Title | Title style | `<sections.executive_summary>` becomes the document title when running in executive tone. |
| TOC | Auto-generated | After title page; depth = 2. |
| Section heading | Heading 1 | Pulls from `sections.*` in customization block. |
| Subsection heading | Heading 2 | E.g., per-inspector breakdown. |
| Body | Normal | Default font: Calibri 11. |
| Tables | Light Grid | Header row shaded with `output.brand.primary_color`. |
| Insights & Recommendations | Numbered list | Risk-ordered (highest first). |
| Verification Log | Heading 1 (last page) | Only included if `verification.log_queries == true`. |
| Page numbers | Footer | "Page X of Y" centered. |

## Section order

1. Cover page (title, customer, reporting period, generated date, MSP name)
2. Executive Summary (1–2 paragraphs + KPI table)
3. Data Overview
4. Health & Compliance (with status icons: ✅/⚠️/❌)
5. Detail Tables
6. Key Insights
7. Recommended Actions (numbered, prioritized)
8. Data Gaps & Coverage Notes
9. Appendix — Methodology
10. Verification Log (if enabled)

## Tone-driven adaptations

When `audience.tone == "executive"`:
- Drop JMESPath snippets and metric IDs from the body — move to appendix only.
- Replace numeric counts with risk language ("most users have MFA" rather than "94/100").
- Lead each section with the outcome, not the methodology.

When `audience.tone == "technical"`:
- Include JMESPath queries inline in the Detail Tables section.
- Show metric IDs alongside metric names.
- Include raw counts and percentages.

## Implementation notes for the agent

- Use the `docx` skill (see `anthropic-skills:docx`) to produce the file.
- Always read the SKILL.md for the `docx` skill before generating, so style application
  is consistent.
- File saved to the user's selected folder, name from `output.filename`.
- Tables wider than 6 columns: split into stacked tables with shared headers.

See `anthropic-skills:docx` for the production-quality docx skill the agent should use.

# Output Block — PowerPoint (.pptx)

How to render a recipe's data as a PowerPoint deck. Recipes that support PPT output
should reference this file rather than redefining the layout.

## Slide order

| # | Slide type | Content |
|---|---|---|
| 1 | Cover | Title (from `sections.executive_summary` or recipe name), customer, reporting period, MSP name + logo |
| 2 | KPI dashboard | 4–6 headline numbers in tile layout (e.g., MFA coverage, EDR coverage, patch compliance, license utilization) |
| 3 | Executive summary | 3–5 bullet points; outcome language, no jargon |
| 4–N | One slide per recipe section | Per-section data, charts where appropriate |
| N+1 | Insights | 3–5 bullets, risk-ordered |
| N+2 | Recommended actions | Numbered, prioritized; one slide if ≤6 items, two slides otherwise |
| N+3 | Data gaps & coverage | What we couldn't measure and why |
| Last | Appendix | Methodology, inspector list, verification log (small font) |

## Charts — when to use which

| Data shape | Chart |
|---|---|
| Coverage % (e.g., 94/100 with MFA) | Donut |
| Counts across categories | Bar (horizontal for >5 categories) |
| Trends over time (from `EVALUATE_TIME_SERIES`) | Line |
| Distribution by status | Stacked bar |
| Inventory split (physical vs. virtual, by OS) | Pie or treemap |

Limit one chart per slide for readability. If two views are needed (e.g., this period
vs. last period), use side-by-side donuts.

## Visual conventions

- Cover and section dividers use `output.brand.primary_color`.
- Status icons in tables: ✅ (compliant), ⚠️ (partial), ❌ (non-compliant), 🔍 (review).
- Slide titles in 32–40pt; body text in 18–24pt; never below 14pt except appendix.
- Avoid full-text quotes from recipes — paraphrase.

## Tone-driven adaptations

When `audience.tone == "executive"`:
- KPI dashboard slide is mandatory.
- Drop the per-inspector breakdown slides; consolidate into category-level slides.
- Recommended actions are framed as business outcomes ("Reduce account takeover risk")
  not technical steps ("Enable Conditional Access policy X").

When `audience.tone == "technical"`:
- Include per-inspector slides.
- Show metric IDs as small captions on chart slides.
- Append a slide listing every JMESPath query used (in the appendix section).

## Implementation notes for the agent

- Use the `pptx` skill (see `anthropic-skills:pptx`) to produce the file.
- Always read the SKILL.md for the `pptx` skill before generating.
- File saved to the user's selected folder, name from `output.filename` with `.pptx`
  extension.
- Use a 16:9 layout unless the MSP brand template specifies otherwise.

See `anthropic-skills:pptx` for the production-quality pptx skill the agent should use.

# External-Data Recipes

These recipes document data shapes that **Liongard does not currently inspect**.
They are still part of a complete PBR / QBR / health-check deliverable — they just
require an external data source (vendor portal, API, manual export) to populate.

Each file describes:
- What the report needs (the slide / section that consumes the data)
- Why Liongard doesn't have it (no inspector currently)
- Where to source it (vendor API, dashboard export, PSA integration)
- What Liongard *can* provide as complementary context (e.g., M365 user count
  as a denominator for tickets-per-user)

The agent should use these files in two ways:

1. **PBR planning.** When assembling a full PBR, scan this folder to see which
   sections will need external supplementation. Surface them in the **Data Gaps**
   section of every relevant recipe so the human knows what's missing.
2. **Future inspector roadmap.** As Liongard ships new inspectors that cover one
   of these areas, the corresponding file moves out of `/external-data/` into
   `/single-system-analysis/by-inspector/` (or wherever it fits).

## Available files

| File | Domain | Typical source |
|---|---|---|
| `email-security.md` | Email gateway / phishing / spam | Proofpoint, Mimecast, Avanan, Vade portals/APIs |
| `service-desk-tickets.md` | PSA ticket volume + close rates | ConnectWise Manage, Autotask, HaloPSA APIs |
| `client-surveys-nps.md` | NPS / CSAT survey results | SmileBack, Simplesat, Crewhu, PSA surveys |

## How they differ from regular recipes

External-data files are **reference notes**, not skills. They don't carry
frontmatter (no auto-trigger), they don't have a customization block (the
*recipe* that consumes them does), and the agent doesn't fetch via the Liongard
MCP — it reads the file to understand what to ask the user for.

When a recipe (e.g., a quarterly lookback) needs one of these data points, the
recipe should:

1. Reference the matching `external-data/` file.
2. Ask the user to provide the export, paste, or API endpoint.
3. Combine with Liongard data per the file's "Liongard complementary data" note.
4. Surface the source in the deliverable's appendix.

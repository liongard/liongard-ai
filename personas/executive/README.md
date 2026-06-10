# Executive — Persona Index

The Executive persona represents **the customer's leadership** — the CIO,
CISO, COO, CFO, or business owner who reads (rarely consumes in detail)
the reports the MSP produces. Executive deliverables are short, framed in
business outcomes, and visual-first. The persona index here helps you
shape any recipe's output for executive consumption.

## Audience framing

- **Tone:** **executive.** Drop jargon. No JMESPath, no metric IDs, no
  inspector names. Lead every section with the **outcome** ("most users
  are protected; <N> are not"), not the methodology ("we ran metric
  X against system Y").
- **Format:** **PowerPoint** is the default — one slide per topic with a
  KPI dashboard, a chart, and a recommendations bullet list. Word for
  written executive summaries. Markdown / Excel are appendix-only.
- **Length:** under 10 slides for a quarterly review. The detail belongs
  in the working-session deliverable (vCIO + TAM), not the executive
  deck.
- **Default cadence:** quarterly business review, annual review. Ad-hoc
  for incidents, renewals, or acquisitions.

## SLA emphasis (Executive defaults)

Executives don't tune SLAs — they consume the rolled-up status. SLA
defaults in the recipes apply; what matters here is the **language**
used to express violations:

| Detail level | Executive translation |
|---|---|
| "MFA coverage 87% across 124 users" | "Most users are protected; ~16 are not." |
| "License expires in 47 days" | "Renewal due in less than two months." |
| "12 servers behind on critical patches" | "A dozen servers carry elevated risk until patched." |
| "WAN management exposed on 1 firewall" | "Firewall management is reachable from the internet on one device — critical." |
| "Win10 EOL in <8 months>" | "Windows 10 reaches end-of-life this <quarter / year>. Plan refresh." |

## Common scenarios → recipes

The same recipes other personas use — but with `audience.tone: "executive"`
set in the customization block. This drops jargon, moves JMESPath /
metric IDs to the appendix, and renders charts instead of tables.

| Scenario | Recipe |
|---|---|
| Quarterly Business Review executive summary | `recipes/environment-quarterly-lookback/` (planned; chains the system-type rollups) — or run the vCIO PBR sequence with `audience.tone: "executive"` |
| Annual review executive deck | Same recipes, broader time window |
| Cyber-insurance executive summary | `recipes/compliance/cyber-insurance/cyber-insurance-readiness.md` (executive section is the readiness % + gap count) |
| Refresh roadmap for the leadership | `all-endpoints.md` (Win11 readiness) + `all-servers.md` (lifecycle) — `pptx` output |
| Renewal calendar for the leadership | `all-firewalls.md` + `all-domains.md` + `microsoft-365.md` license sections — `pptx` output |
| Incident response executive briefing | Post-incident summary from the relevant single-system recipes; high-level outcome + remediation timeline |

## Slide composition guidance

A typical executive deck from a recipe with `audience.tone: "executive"`:

| Slide | Content |
|---|---|
| Cover | Customer + period + MSP name |
| KPI dashboard | 4–6 outcome KPIs (coverage %, unprotected count, expirations, top risks) |
| Executive summary | 3–5 bullets — outcomes, not methodology |
| Recommended actions | Prioritized, numbered |
| Risk highlights (1–2 slides) | Top 3 risks with single-line description |
| Lifecycle roadmap (1 slide) | EOL devices / expiring licenses by quarter |
| Q&A / Appendix | Anything technical lives here |

## Read across to other personas

- **vCIO / Account Manager** — vCIO presents the executive deck. The
  vCIO persona's index covers the technical recipes; this index frames
  them for the executive consumer.
- **SOC** — SOC findings frame risk for the executive; lead with the
  business impact, not the control name.
- **Sales** — Sales pitch decks share the executive framing
  conventions; format guidance is the same.

## What to customize first

1. **MSP brand template** — slide master, font, colors. Set
   `output.brand.*` in the customization block of every recipe used for
   executive output.
2. **Executive-language phrase bank** — your MSP's standard ways of
   framing the most common findings. The "Executive translation"
   examples above are a starting point; customize for your tone.
3. **Quarterly slide template** — assemble the canonical 8-slide
   quarterly review template and link from each recipe's customization
   block.
4. **Risk-language scale** — your MSP's risk framework (e.g., Critical
   / High / Medium / Low; or H / M / L) — apply consistently in every
   executive deliverable so customers learn what each level means over
   time.

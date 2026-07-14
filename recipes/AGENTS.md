# Agent Operating Guide — Running Liongard Recipes

> **Scope:** this is the **runtime** guide for agents *running* recipes against a
> live tenant. For working *on* this repo (contributing, packaging, validation)
> see [`AGENTS.md`](../AGENTS.md). Repo map: [`ARCHITECTURE.md`](../ARCHITECTURE.md).

Read this file at the start of every session before running any recipe or calling any
MCP tool. It defines how to orient, route, and render — three things that should happen
in every interaction with this library.

---

## 1. Orient — what this library is

This library is a collection of LLM-agent recipes that turn live Liongard MCP data into
customer-facing artifacts: single-system assessments, fleet rollups, QBRs, compliance
evidence packs, onboarding intakes, sales discovery, and roadmap documents.

Recipes tell you exactly which MCP tools to call, in what order, with what JMESPath
queries, and how to interpret results. They are agent instructions, not prose templates.

MSPs served: 7 personas — NOC, SOC, vCIO/Account Manager, TAM, Sales, Executive,
Accounting/Finance.

---

## 2. Route — use the recipe picker before touching data

Before calling any Liongard MCP tool, identify the right recipe for the user's request.

**If you have the `liongard-recipe-picker` skill available, invoke it.** The skill
routes the request to the correct recipe based on the user's intent — it knows the full
recipe catalog, personas, and trigger phrases.

If the skill is not available, locate the recipe manually:

1. Check `reference/future-recipes-roadmap.md` for the recipe file path.
2. Or navigate `recipes/` by type: `single-system-analysis/by-inspector/`,
   `system-type-assessment/`, `domain-assessment/`, `compliance/`,
   `environment-quarterly-lookback/`, `roadmap-planning/`, `sales-assessment/`,
   `onboarding-assessment/`.
3. Or check `personas/<role>/README.md` for the persona's recipe index.

Do not improvise a recipe from scratch when a validated one exists.

---

## 3. Pre-flight — ask two questions before calling any MCP tool

Once the recipe is identified, ask the user these two questions **together, before
starting data collection**. They take two seconds to answer and determine the entire
render path — asking after data collection wastes tokens on the wrong output.

> "Before I start pulling data — two quick questions:
>
> 1. **Output format:** Markdown (plain text, good for PSA attachments and internal
>    notes) or HTML (styled, good for customer-facing delivery via email or portal)?
>
> 2. **Audience:** Internal (MSP team only) or External (customer-facing)?"

Store the answers as two variables for the rest of the session:

```
output_format = markdown | html
audience_type = internal | external
```

If the user has already set `output.format` and `output.audience_type` in the recipe's
**Customize for your MSP** block, skip the questions and use those values.

---

## 4. Render rules — what each combination produces

| `output_format` | `audience_type` | Verification log | Inspector health timestamp | Format |
|---|---|:-:|:-:|---|
| `markdown` | `internal` | ✅ Include | Optional | Raw markdown |
| `markdown` | `external` | ❌ Omit | ✅ Required | Raw markdown |
| `html` | `internal` | ✅ Include | Optional | Styled HTML (see § 5) |
| `html` | `external` | ❌ Omit | ✅ Required | Styled HTML (see § 5) |

**Verification log** — the query log appended by the agent after every run (defined in
the recipe's "Verification log" section). Internal teams use it for QA and auditing.
External customers do not need it and it adds noise to a customer deliverable.

**Inspector health timestamp** — when rendering the inspector health / data overview
section, external-facing outputs must show the `latestInspectionDate` for each
inspector alongside its health status. This makes the data provenance clear to a
customer who wasn't present when the inspection ran. Format as:
`Data as of: <YYYY-MM-DD HH:MM UTC>`. Internal outputs may omit this if the team
already knows the inspection cadence.

---

## 5. HTML output guidance

When `output_format = html`, generate a single self-contained HTML file. Rules:

- **Self-contained.** No external CDN dependencies. All CSS is inline or in a `<style>`
  block in `<head>`. The file must render correctly when opened as a local file or
  pasted into an email.
- **Minimal styling.** Clean, professional. Use a neutral sans-serif font stack
  (`system-ui, -apple-system, sans-serif`), a white background, subtle section dividers,
  and a muted color palette. Do not use Liongard brand colors unless
  `config/msp-config.local.yaml` specifies them — use the MSP's `primary_color` if set.
- **Tables.** Use `<table>` with `border-collapse: collapse` and alternating row shading
  (`#f9f9f9`). Status indicators: ✅ green (`#2e7d32`), ⚠️ amber (`#e65100`),
  ❌ red (`#c62828`), 🔍 blue (`#1565c0`).
- **Section structure.** Render each recipe section as a `<section>` with an `<h2>`
  heading. Use `<h3>` for subsections. A compact `<nav>` TOC at the top linking to
  section anchors is encouraged for longer reports.
- **Data timestamps (external only).** In the inspector health / data overview section,
  render the timestamp as a `<span class="data-timestamp">Data as of: YYYY-MM-DD</span>`
  styled in muted gray (`#666`) next to the inspector name.
- **No verification log (external only).** The verification log section is omitted
  entirely from external HTML output. Do not include a collapsed or hidden version.
- **File naming.** Use the recipe's `output.filename` pattern with `.html` extension.

---

## 6. Output location — where to save the report

Write every generated deliverable to an environment-scoped folder, **never to the
repository root**. This keeps the cloned library clean and groups each customer's
artifacts together.

**Path:** `outputs/environments/<customer-slug>/`

- **`customer-slug`** = the Liongard environment name, sanitized: title-cased,
  spaces → hyphens (e.g., `Contoso`, `Acme-Corp`). Match it to the environment you
  pulled data from.
- **Create the folder if it doesn't exist** before writing the first file.
- **Naming:** `<customer-slug>-<report-type>-<period>.<ext>` — for example
  `Contoso-QBR-Q1-2026.html` or `Acme-Corp-Firewall-Assessment.docx`.
- `outputs/` is **gitignored** — customer data never commits to the library. Files
  persist locally for delivery.
- Do **not** write deliverables to the repo root or into `recipes/`, `reference/`,
  `templates/`, etc. Only `outputs/environments/<customer-slug>/`.

---

## 7. Session start checklist

Before beginning any recipe run:

- [ ] Recipe identified (via recipe picker or manual navigation).
- [ ] Pre-flight questions answered (or customization block already set).
- [ ] `output_format` and `audience_type` confirmed.
- [ ] Output path resolved: `outputs/environments/<customer-slug>/` (folder created).

Then follow the recipe's numbered workflow steps in order.

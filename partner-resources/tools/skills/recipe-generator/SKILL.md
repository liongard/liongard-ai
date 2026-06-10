---
name: recipe-generator
description: >
  Use this skill when the user wants to scaffold a new per-inspector
  single-system Liongard Prompt Library recipe. Trigger on phrases like
  "scaffold the SentinelOne recipe", "stub the Huntress recipe", "draft
  the Bitdefender single-system recipe", "start a new recipe for KnowBe4",
  or "produce a single-system assessment recipe template". The skill takes
  a per-inspector YAML spec (slug, ID, parent/child status, metric IDs,
  proposed-metric gaps) and produces a structural recipe draft with
  customization block, asset-first data sources, metric tables, QA pass,
  and verification log filled in — leaving explicit TODO markers for the
  vendor-specific narrative the author fills in by hand.
  Do NOT use for cross-inspector rollups (the all-* system-type recipes),
  compliance master or domain files (cyber-insurance, CMMC, HIPAA),
  external-data files, or cross-cutting domain-assessment recipes — those
  need real synthesis and are hand-crafted.
---

# Recipe Generator — Liongard Prompt Library (Partner Edition)

This skill scaffolds **per-inspector single-system recipes** for your MSP's
Liongard Prompt Library. It produces a draft markdown recipe with all structural
sections filled in (frontmatter, customization block, asset-first data sources,
metric tables, QA pass, output format, verification log) plus explicit TODO markers
for vendor-specific narrative the author fills in by hand.

> **Partner edition note:** This version is designed for MSP authors building
> recipes against their own customer environments. It does not assume access to
> Liongard's internal primitives registry, metric backlog, or internal reference
> files. Metric verification is done live against your own systems using
> `liongard_metric EVALUATE`.

## What this skill does NOT do

This skill is **only** for per-inspector single-system recipes that fit the
single-inspector-single-vendor pattern. It does **not** scaffold:

- Cross-inspector rollups: `recipes/system-type-assessment/all-*.md`
- Compliance recipes: `recipes/compliance/cyber-insurance/cyber-insurance-readiness.md`,
  `domains/*.md`, `carriers/*.md`, future CMMC / HIPAA folders
- External-data files: `recipes/external-data/*.md`
- Domain-assessment cross-cutting recipes: `recipes/domain-assessment/*.md`

These need cross-vendor synthesis or question-driven curation that templating
can't produce. They are hand-crafted recipes — the author writes the narrative
directly without a scaffold.

## When this skill triggers

Trigger phrases:
- "scaffold the <inspector> recipe"
- "generate a recipe stub for <inspector>"
- "draft the <inspector> single-system recipe"
- "stub the <inspector> recipe"
- "start a new <inspector> recipe"
- "produce the <inspector> assessment recipe template"

If the user names a cross-inspector recipe (e.g., "build all-firewalls.md"),
explicitly tell them this skill doesn't scaffold cross-inspector recipes and
suggest hand-writing instead. Do not produce a draft for those.

## Inputs

The user provides a **per-inspector YAML spec**. Either:

1. **Inline** in their prompt (typical for one-off scaffolding).
2. **Referenced as a file path** (e.g., `tools/skills/recipe-generator/specs/cisco-meraki.yaml`).
3. **Constructed interactively** — if the user just says "scaffold a recipe
   for SonicWall", ask the missing-spec questions before producing the draft.

See `references/recipe-spec-format.md` for the full spec format.
See `assets/recipe-spec-template.yaml` for a blank template.
See `assets/example-spec-cisco-meraki.yaml` for a worked example.

## Workflow

### Step 1 — Confirm scope

If the user asked for a cross-inspector / compliance / external-data /
domain-assessment recipe, stop and tell them this skill doesn't scaffold
those. Otherwise, confirm the inspector slug + recipe family
(single-system).

### Step 2 — Get the spec

If the user provided a complete spec (inline or file), validate it has the
required fields. If they didn't, ask for the missing fields. Required:

```yaml
inspector:
  slug:                  # required, e.g. "cisco-meraki-inspector"
  id:                    # required, e.g. 3
  display_name:          # required, e.g. "Cisco Meraki"
  category:              # required, one of: "Apps & Services" | "Beta" | "Cloud" | "Endpoint" | "Network"
  target_system_type:    # required, e.g. "Network Controller"
  parent_child:          # required, true | false
  identifier_jmespath:   # if parent_child=true, the JMESPath to identify the right child

recipe:
  family:                # always "single-system-analysis" for this skill
  scope_summary:         # required, 1-2 sentences for the description frontmatter
  trigger_phrases:       # required, list of user phrasings that should trigger this recipe
  personas:              # required, list from {noc, soc, vcio-account-manager, technical-alignment-manager, sales, executive, accounting-finance}
  output_formats:        # required, list from {markdown, word, pptx, xlsx}

aliases:
  user_facing:           # optional but recommended, list of common shorthand
  legacy:                # optional, list of legacy product names

slas:                    # optional but recommended; recipe defaults if omitted

metrics:                 # required if recipe uses any per-metric calls; list of {id, name, jmes_path, purpose}
                         # Only list metrics you have verified live against a real system
                         # using liongard_metric EVALUATE. Unverified paths belong in
                         # proposed_metric_gaps.

proposed_metric_gaps:    # optional; metrics this recipe WANTS but that could not be
                         # confirmed in the dataprint. NOT emitted into frontmatter primitives[] —
                         # they belong in the Data-gaps prose section only.

cross_check:             # optional; describe the asset-inventory cross-check pattern
                         # (which liongard_device / liongard_identity / liongard_domain
                         # filters apply)
```

See `references/recipe-spec-format.md` for the full optional fields.

### Step 2b — Parent/child inspector schema (required when `parent_child: true`)

If `spec.inspector.parent_child == true`, apply this pattern throughout the recipe.

**What the two tiers look like:**

| Launchpoint type | Typical top-level keys | Can EVALUATE metrics? |
|---|---|---|
| **Parent** | `Discovered[]`, `Organizations[]` / `Accounts[]`, `Name`, `UniqueCompositeKey`; `overview: {}` (empty) | ❌ No — entity arrays are absent. All paths return null. |
| **Child** | Inspector-specific entity arrays (`Users[]`, `Agents[]`, `Endpoints[]`, `Servers[]`, `Systems[]`, etc.), `SystemInfo`, policy/settings objects | ✅ Yes — all EVALUATE calls target this system ID. |

**Known inspectors (validated 2026-05-28):**

| Inspector | ID | Parent keys | Child entity keys |
|---|---|---|---|
| JumpCloud | 68 | `Discovered[]`, `Organizations[]` | `Users[]`, `Systems[]`, `Groups[]`, `Applications`, `Policies`, `SystemInfo` |
| Huntress | 97 | `Discovered[]`, `Accounts[]` | `Agents[]`, `Incidents[]`, `Organization` |
| SentinelOne | 70 | `Discovered[]` | `AgentsSummary`, `ThreatsSummary`, `Agents`/`Endpoints` |
| CrowdStrike | 102 | `Discovered[]` | `DevicesDetails[]`, `Users[]`, `UsersOverview`, `CustomerDetails` |
| Sophos Central | 65 | `Discovered[]` | `Endpoints[]`, `Servers[]`, `Account`, `Policies` |

Other multi-tenant inspectors (RMM platforms, backup SaaS, PSA) likely follow the same pattern — probe with GET_OVERVIEW before assuming entity data is at the top level.

**Detection procedure** (always include this in the recipe's "Locating the right system" section):

```
liongard_launchpoint GET_OVERVIEW systemId=<candidate_id> environmentId=<env_id>
```

- Keys include `Discovered[]` → **parent**. Do NOT use this systemId for EVALUATE.
- Keys include entity arrays → **child**. Use this systemId for all EVALUATE calls.

**Scaffolding additions triggered by `parent_child: true`:**

1. A "Locating the right system" section with the schema-comparison table and the GET_OVERVIEW detection probe.
2. A callout box at the top of the recipe: `> ⚠️ Parent/child inspector. All metric evaluations must target the child system — the parent returns null for all entity-level paths.`
3. A `TODO` marker: `<!-- TODO: confirm parent and child system IDs for this inspector via GET_OVERVIEW; document key differences in the verification log -->`
4. In the verification log, two rows: GET_OVERVIEW on the parent (showing only `Discovered[]`) and GET_OVERVIEW on the child (showing entity arrays).

### Step 3 — Determine output path

- For `family: single-system-analysis` → write to
  `recipes/single-system-analysis/by-inspector/<slug-without-inspector-suffix>.md`
  (e.g., `cisco-meraki-inspector` → `cisco-meraki.md`)

If the file already exists, ask the user whether to overwrite or write to
`<slug>-draft.md`.

### Step 4 — Read the canonical references

The skill produces a recipe consistent with the project's canonical patterns.
Before generating, read whatever is available in your recipe library:

- `templates/recipe-skeleton.md` — the structural template
- `templates/customization-block.md` — full customization YAML reference
- `reference/asset-fields.md` — per-tool field map for the asset-first data-sources section

Don't duplicate content from those files — link to them.

### Step 5 — Generate the recipe

Produce a markdown file with these sections in order. Sections marked
**(filled)** are auto-populated from the spec; sections marked
**(TODO marker)** are placeholders the author fills in.

| Section | Status | Source |
|---|---|---|
| YAML frontmatter | filled | spec.recipe.* |
| Top-of-file pull quote (inspector / parent-child / references) | filled | spec.inspector + reference links |
| Customize for your MSP | filled | from `templates/customization-block.md` + spec.slas |
| When to use | filled | spec.recipe.trigger_phrases + spec.recipe.personas |
| Inputs table | filled | standard input set |
| Locating the right system | partially filled | system-search command filled; **TODO** for parent/child disambiguation narrative |
| Liongard data sources — primary (asset inventory) | filled | from `reference/asset-fields.md` patterns + spec.cross_check |
| Liongard data sources — per-vendor metrics | filled | from spec.metrics |
| Metrics and queries | filled | from spec.metrics |
| QA & Manual Verification | filled | standard QA template + spec.proposed_metric_gaps |
| **Coverage cross-check** (REQUIRED) | filled | see Step 5b |
| Insights & recommendations | partially filled | template rows; **TODO** for recipe-specific judgment |
| Data gaps & coverage notes | partially filled | known gaps from spec; **TODO** for vendor-specific limitations |
| Output format | filled | from `templates/output-block-*.md` |
| Verification log | filled | standard template |

### Step 5a — Verify every metric path live (REQUIRED)

Before referencing a metric path in the recipe, validate it against a real
system using `liongard_metric EVALUATE`. This is the only reliable way to
confirm the field exists, the type is correct, and the filter syntax works.

**For each path in `spec.metrics`:**

```
liongard_metric EVALUATE jmesPathQuery="<path>" systemId=<X> environmentId=<Y>
```

Rules:
- Test the exact path that will appear in the recipe, not a simplified version.
- If a result is null or empty, try at least one other system before labeling it as a gap.
- For array fields, sample `Array[0]` to confirm the object structure inside.
- For filter expressions, confirm the filter actually works and returns the expected rows.
- For numeric fields, confirm the unit (hours vs. minutes, bytes vs. MB).
- For string fields used in equality filters, confirm the exact string value (`"enabled"` not `true`).

**Label every path in the verification log:**

| Label | Meaning |
|---|---|
| **VALIDATED** | Confirmed non-null result on a live dataprint; example value observed |
| **SCHEMA_CONFIRMED** | Field exists in GET_OVERVIEW; array was empty on test system |
| **PROPOSED** | Not confirmed on any live system — document in Data gaps only |

Paths that cannot be confirmed go into `proposed_metric_gaps` in the spec and the recipe's "Data gaps" section — not into the metric tables.

**Common field gotchas to always verify:**
- Boolean vs. string: some fields are `"enabled"/"disabled"` strings, not booleans.
- Object vs. scalar: some fields that look like numbers are actually `{value, trustable}` objects.
- Threshold of 0 meaning "disabled": `== 0` may mean "no limit enforced", not "threshold is 0".
- Array filter strings: `contains(Array, 'name')` checks for exact element equality, not substring match.

### Step 5b — Coverage cross-check (REQUIRED)

Before marking the recipe done, run a coverage check and add a "Coverage
cross-check" section to the recipe. This step surfaces blind spots before
the recipe reaches customers.

1. **CIS Controls (v8.1) mapping** — for recipes with SOC / TAM / compliance
   audiences, identify which CIS Controls the recipe's findings map to and
   surface them in the Insights / Compliance evidence sections.

2. **Cyber-insurance relevance** — for EDR, identity, network, and backup
   recipes, check whether the recipe covers the standard underwriting questions
   around MFA, patch posture, backup verification, and privileged access. Flag
   any that are missing as gaps.

3. **QBR alignment** — if this recipe's system type feeds a quarterly business
   review, confirm the recipe exposes the highlights a QBR needs: coverage count,
   alert count, last-seen recency, and version/patch posture.

The "Coverage cross-check" section should be a small table with sources,
coverage status (✅ covered / ⚠️ partial / ❌ gap), and a one-line note per row.

### Step 5c — MSP-wide values inherit from `/config/msp-config.yaml`

**Never emit a `brand:` block, a `preferred_stack:` block, or duplicate
MSP-standard SLA values in a generated recipe.** Those live in
`/config/msp-config.yaml` and recipes inherit by reference. The
customization block emits a comment instead:

```yaml
output:
  format: <recipe-specific default>
  filename: "<recipe-specific pattern>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed
```

For per-recipe SLAs, only emit values that are **recipe-specific**. Common
SLAs that already live in the config should NOT be re-emitted unless the
recipe needs a different value.

### Step 6 — Apply the scrub

The recipe must be shareable. Before writing the file:

- No real tenant, customer, or environment names — use `<TENANT_NAME>`,
  `<CUSTOMER_NAME>`, `<ENVIRONMENT_NAME>`
- No specific system or account IDs — use `<SYSTEM_ID>`, `<ENV_ID>`
- No example evaluated values from real systems — use shape annotations
  (`<integer>`, `<bool>`, `<ISO timestamp>`, `<string>`)
- JMESPath queries, metric IDs, and "compliant when" thresholds stay —
  those are recipe value, not customer data

### Step 7 — Mark vendor-specific TODOs explicitly

Use this format consistently so the author can grep for `<!-- TODO` and
find every placeholder:

```markdown
<!-- TODO: vendor-specific narrative — parent/child gotchas, naming
distinctions, version-specific quirks, special-feature notes. -->
```

A typical recipe will have 3–5 TODO markers:
1. Top-of-file pull quote: vendor caveats / "this inspector is unusual because…"
2. Locating the right system: parent/child disambiguation specifics
3. Data sources: per-vendor field gotchas
4. Insights & recommendations: 2–3 vendor-specific insights beyond the template defaults
5. Data gaps: vendor-specific limitations

### Step 8 — Report

After writing the file:

1. Print the path of the file written.
2. Print a count of TODO markers and their section names.
3. List any paths that could not be validated live — these go into the "Data gaps" section
   and should be tested against a real system when one becomes available.
4. Suggest the next step: "Now fill the TODO markers with vendor-specific
   narrative."

## Vendor-specific narrative checklist

When the author fills in the TODO markers, these are the patterns to cover
(not all apply to every recipe):

**Top-of-file pull quote:**
- Inspector category + role (EDR? firewall? RMM? identity provider?)
- Parent/child? If yes, how the parent and child differ
- Naming gotchas (multiple inspectors share a vendor name)
- Beta status (if `category: Beta`, surface that)
- Special features specific to this product

**Locating the right system:**
- Explicit `query=` keyword (not just slug)
- Per-environment expectations (one system per tenant? multiple?)
- **For parent/child inspectors (required):** schema-comparison table, GET_OVERVIEW detection probe, explicit rule: "All EVALUATE calls target the child system."

**Data sources — per-vendor narrative:**
- Field gotchas (casing, type surprises, nested vs. flat)
- Large-array warnings (use `length()` not full pull for arrays >100 items)

**Insights & recommendations:**
- 2–3 vendor-specific insights with templated wording
- SLA-driven thresholds tuned to this vendor

**Data gaps:**
- Vendor-specific limitations
- Where to supplement (vendor portal / API)

## Examples

See `assets/example-spec-cisco-meraki.yaml` for a worked spec.
See `assets/recipe-spec-template.yaml` for a blank template the author
can copy + fill.

## Installation

To make this skill auto-trigger in Cowork / Claude Desktop sessions,
copy or symlink it to your skill directory:

```bash
# Cowork / Claude Desktop user-level skill dir (macOS)
ln -s "$PWD/partner-resources/tools/skills/recipe-generator" ~/.claude/skills/recipe-generator
```

Or invoke manually by reading this SKILL.md from any session and following
its instructions.

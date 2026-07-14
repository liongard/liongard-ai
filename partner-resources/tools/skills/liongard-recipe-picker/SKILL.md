---
name: liongard-recipe-picker
description: >
  Use this skill whenever an MSP user asks for a Liongard-backed customer
  deliverable — QBR, single-system assessment, system-type rollup, cyber-insurance
  questionnaire, compliance evidence pack, onboarding intake, sales discovery,
  refresh roadmap, or any "report on a vendor/system for a customer" request.
  Trigger phrases: "run a QBR for {customer}", "assess our Synology", "what
  does Liongard say about our firewalls", "fill in the cyber-insurance form",
  "CMMC L1 evidence", "onboard {customer}", "refresh roadmap for {customer}",
  "show me the SOC view of {environment}". This skill routes the request to
  the correct recipe in the Liongard Recipe Library so the agent follows the
  validated playbook instead of improvising.
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_device, liongard_identity, liongard_domain"
personas: [noc, soc, vcio-account-manager, technical-alignment-manager, sales, executive, accounting-finance]
output_formats: [markdown, word, pptx, xlsx]
---

# Liongard Recipe Picker

> **What this skill does.** Given a user's request, it (1) classifies the request
> against the recipe library taxonomy, (2) picks the highest-precision recipe
> file, (3) loads that recipe verbatim into the agent's context, and (4) hands
> control back to the agent to follow the recipe end-to-end against live
> Liongard MCP data.
>
> **Why it exists.** Without this skill an MSP-end agent will improvise — it'll
> hit a few MCP tools, miss the QA pass, miss the data-gaps section, and produce
> an inconsistent artifact. With this skill, every request maps to a recipe that
> has already passed the library's governance gates: schema-validated
> frontmatter, registered metric primitives, cross-source coverage check, and
> verification log. Same input phrasing → same recipe → same deliverable shape
> every time.

---

## Routing logic — read this in order

The agent must walk these steps **before** doing any MCP work.

### Step 1 — Classify the request

Map the user's phrasing to one of the nine recipe types:

| User says... | recipeType |
|---|---|
| "QBR", "quarterly review", "what changed in the last 90 days", "PBR" | `QBRRecipe` |
| "assess <single vendor> for <customer>" (e.g., "assess our Synology") | `SystemAssessmentRecipe` |
| "all our firewalls", "rollup across <category>", "every EDR endpoint" | `SystemTypeAssessmentRecipe` |
| "identity posture", "endpoint posture", "network posture" (broader than one inspector) | `DomainAssessmentRecipe` |
| "fill in the cyber insurance form", "Spectra L1 readiness", "<carrier> application" | `CyberInsuranceQuestion` |
| "CMMC <level>", "HIPAA evidence", "FTC Safeguards mapping" | `ComplianceRecipe` |
| "onboard <customer>", "new client intake", "baseline this environment" | `OnboardingRecipe` |
| "pre-sales", "prospect assessment", "discovery before the close" | `SalesRecipe` |
| "refresh roadmap", "EOL plan", "renewal forecast" | `RoadmapRecipe` |

If the request straddles two types, ask one clarifying question. Don't guess.

### Step 2 — Resolve the inspector (for `SystemAssessmentRecipe` only)

Use `reference/inspector-aliases.md` to translate the user's vendor name into
the canonical inspector slug. Examples:

- "Synology" → `synology-nas-inspector` → `recipes/single-system-analysis/by-inspector/synology-nas.md`
- "SentinelOne" / "S1" → `sentinelone-inspector` → `…/by-inspector/sentinelone.md`
- "M365" / "Office 365" → `microsoft-365-inspector` → `…/by-inspector/microsoft-365.md`

If the user says "Sophos" without qualifying, **ask which one** — Sophos Central
(endpoint), Sophos Firewall (XG/XGS), or Sophos SG (legacy). Same for Veeam
(VAC vs. VSPC) and Cisco network products.

### Step 3 — Confirm the recipe exists; otherwise degrade gracefully

```
ls recipes/<category>/<recipe-file>.md
```

If the recipe file is present, load it and proceed to Step 4.

If it's listed in `reference/future-recipes-roadmap.md` but not yet shipped,
tell the user: *"The <vendor> single-system recipe is on the roadmap but not
yet shipped. The closest available recipe is <fallback> — proceed with that?"*

If the request doesn't map to any recipe at all, tell the user explicitly and
suggest filing it for the library backlog. **Do not improvise a one-off** — that
defeats the purpose of the governance layer.

### Step 4 — Load the recipe and follow it verbatim

Read the entire recipe file into context. Honor every section:

1. **Customize block** — use the values verbatim unless the user has overridden
   them in this session. SLA thresholds, output format, section headings come from here.
2. **Workflow steps** — call MCP tools in the exact order specified, with the
   exact JMESPath / structured filters the recipe specifies. Don't rewrite queries.
3. **QA pass** — run the retry / divergence / stale-inspector checks per
   `reference/qa-retry-pattern.md`. Surface every finding in the deliverable.
4. **Data gaps** — populate from the actual findings, not from prior assumptions.
5. **Verification log** — append every MCP call you made with shape annotations only.
6. **Output** — render in the format from the customize block (or the user's override).

If the recipe references a metric primitive by `metrics:<slug>:<condition>`,
resolve it via `primitives/metrics-registry.yaml` — do not look up the metric
by numeric ID. Numeric IDs aren't stable across Liongard instances; the
registry resolves to UUID (preferred) or stable Global metric name.

### Step 5 — Hand the artifact back with a verification log

Final deliverable always includes:
- The artifact in the requested format.
- The verification log (every MCP call, anonymized shapes only).
- The data-gaps section.
- A pointer to the recipe file that was used (so the MSP can audit what playbook ran).

---

## Recipe library map

For the agent's quick reference. Full roadmap in `reference/future-recipes-roadmap.md`.

| Folder | recipeType | What's in it |
|---|---|---|
| `recipes/single-system-analysis/by-inspector/` | `SystemAssessmentRecipe` | One file per inspector — Microsoft 365, SentinelOne, Synology NAS, Fortinet, etc. |
| `recipes/system-type-assessment/` | `SystemTypeAssessmentRecipe` | `all-firewalls.md`, `all-edr-platforms.md`, `all-backups.md`, `all-endpoints.md`, `all-rmm-platforms.md`, etc. |
| `recipes/domain-assessment/` | `DomainAssessmentRecipe` | Identity, endpoint, network, backup posture across all inspectors. |
| `recipes/environment-quarterly-lookback/` | `QBRRecipe` | `quarterly-business-review.md` — composes the rest into a time-bounded deck. |
| `recipes/compliance/cmmc/` | `ComplianceRecipe` | Per-level CMMC evidence packs. |
| `recipes/compliance/cyber-insurance/` | `ComplianceRecipe` / `CyberInsuranceQuestion` | Per-carrier application recipes plus reusable per-question files. |
| `recipes/compliance/hipaa/` | `ComplianceRecipe` | HIPAA Security Rule evidence mapping. |
| `recipes/compliance/ftc-safeguards/` | `ComplianceRecipe` | FTC Safeguards Rule. |
| `recipes/onboarding-assessment/` | `OnboardingRecipe` | New-customer intake. |
| `recipes/sales-assessment/` | `SalesRecipe` | Pre-sales discovery — built around non-credentialed inspectors. |
| `recipes/roadmap-planning/` | `RoadmapRecipe` | Refresh forecast, license renewal, OS upgrade roadmap. |
| `recipes/external-data/` | varies | External attack surface, dark-web breach data, domain WHOIS, TLS posture. |

---

## When NOT to use this skill

- **Plain Liongard MCP questions** — "how many users in env X" or "is the firewall
  inspector running" doesn't need a recipe. Just call the MCP directly.
- **Custom one-offs the user explicitly opts into** — if the user says "ignore the
  recipe, just give me X," respect that. The recipe is a default, not a cage.
- **Recipe authoring** — if the user is *writing* a new recipe rather than
  *running* one, hand off to the `recipe-generator` / `liongard-metrics` skills
  in the internal authoring plugin instead.

---

## Failure modes to watch for

| Symptom | Cause | Fix |
|---|---|---|
| Agent invents JMESPath instead of using the recipe's | Recipe wasn't loaded into context fully | Re-read the entire recipe; do not paraphrase |
| Numeric metric ID hard-coded in MSP-side automation | Caller pinned to a per-instance ID | Switch to `metrics:<slug>:<condition>` reference; the registry resolves UUID/name |
| Two MSPs get different deliverables from "the same" recipe | Customize block was rewritten in one instance | Customize block is local override only — the recipe body is the contract |
| New vendor recipe ships but old MSPs keep running their fork | No version surfacing in deliverables | Recipe `version` from frontmatter must appear in the verification log |

---

## Maintenance

This skill is intentionally thin — it routes, it doesn't synthesize. When the
recipe library adds a new category, update Step 1's table and the library map.
The actual recipe content lives in `recipes/`, validated by the governance gates
in `.github/workflows/validate.yml`.

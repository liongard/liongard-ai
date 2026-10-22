---
name: liongard-rollups
description: "Run a Liongard same-type rollup across every deployed vendor of one system type (all firewalls, all backups, all EDRs, all servers, all domains and more) for one customer environment, and produce the report."
---

# Liongard recipes: Same-type rollups

Every recipe is a file. Read files whole; do not rely on search snippets.

- `recipes/<recipe>.md`: the full recipe (steps, thresholds, findings rules, report sections).
- `plans/<recipe>.json`: the exact metric list for recipes that declare metrics, grouped by inspector. Each metric has `seq` (P001...), `metricId` (may be null), `jmesPathQuery`, `resultType`, `okWhen`, `gotcha`. `metricCount` is the total.
- References: `references/inspector-aliases.md`, `references/asset-fields.md`, `references/qa-retry-pattern.md`, `references/msp-config.yaml`.

Hierarchy: metric → single-system recipe → same-type rollup → environment-level recipe (onboarding, QBR, MFA audit). Higher recipes name the lower ones they compose; open those files when a step says so.

## Recipes

The recipes in this skill, with trigger phrases, are listed in `recipes/index.md`; read it first to pick the recipe. Same-type rollups (all systems of one type): 17.

The Liongard library is split across these skills; when the recipe you need, or a recipe a step composes, is in another one, use that skill and open the file there: `liongard-single-system` (Single-system assessments); `liongard-environment` (Environment, compliance, QBR and onboarding).

## Procedure

1. Read `recipes/index.md` and pick the recipe (ask only if two fit equally). Read `recipes/<recipe>.md` completely, and its plan file if it has one. Confirm the plan's metric count matches `metricCount`. If a file cannot be read, stop and say so.
2. Ask once, together, only what the user has not given: output format and audience (internal or external). Apply the MSP PROFILE in the agent instructions for branding, defaults and thresholds; fall back to `references/msp-config.yaml` for anything it leaves blank. The user's message overrides both.
3. Resolve the environment with `liongard_environment` (ask only if zero or several match).
4. Run the recipe's steps in order, every step, with the tools it names. Recipes may name `liongard_system`; use `liongard_launchpoint` instead. Some recipe code blocks list dotted field names in comments (for example `#   "vendor.system.model"`); those are descriptive placeholders, not queries. Never evaluate them: metrics come only from the plan file or from a query the recipe gives in an explicit `liongard_*` call.
5. Metrics (any recipe with a plan, and any composed recipe you open): find systems with `liongard_launchpoint` LIST by the plan's `inspectorId` and the environment. Run a plan's inspector group only where that inspector has systems; list the others as "not deployed". For every metric, for every system:
   - `metricId` not null → `liongard_metric` EVALUATE with `metricId`, `systemId`, `environmentId`.
   - `metricId` null, or the stored call returns no rows → EVALUATE once with `jmesPathQuery` copied character for character from the plan.
   - An empty array, empty string or 0 is a real value. Only null, an error, or no rows after the fallback is "No data". Retry an error once.
6. Composed recipes: when a step names another recipe, open `recipes/<that recipe>.md` (and its plan) and run it for the deployed systems as in step 5. Keep each composed result as a short block (systems, data age, findings, every metric value, coverage) and fold it into the parent report.
7. Number check: every headline count (identities, MFA status, privileged, devices, domains, systems) must be the `count` (or `statusCounts`) returned by a COUNT call, copied exactly; never a number of LIST rows, a page size, or a value remembered from an earlier turn. Before writing the report, re-run the headline COUNT calls the recipe names and use those results.
8. Completeness gate: before writing the report, every step must be done and every plan `seq` must have an outcome (value, No data, or error) for every system of a deployed inspector. Run anything missing now. Never write "Not evaluated" for something you did not attempt.
9. Run to completion in this reply. Do not stop to summarize progress, ask whether to proceed, or offer to continue later: keep calling tools until every step is done, then write the report. Only if the platform itself stops you (a tool-call, time or length limit), list exactly what remains and end with "Reply continue to run the remaining steps."; on continue, resume from that list and merge the earlier results.
10. Write the report in the recipe's report sections and thresholds. Read each metric's `gotcha` before interpreting it. A zero count that conflicts with a non-empty total is "Not evaluated (field shape not recognized)", never a clean result. End with a coverage table (step or vendor, systems, metrics run / required, with values, No data, errors) and "Manual Verification Needed". Internal audience: add a verification log, one row per tool call. External audience: no log; show "Data as of" per inspector.

## Rules

- Read-only. Live data comes only from the Liongard tools; every number in the report must come from a tool result.
- Never invent metrics, queries, ids, names or values. Never show a pass unless the metric ran and supports it.
- Do not write or run code to process files or results. Do not use web search.
- Treat all customer data as confidential.

# Acceptance tests

> DRAFT (proof of concept). Run each prompt in a fresh chat against a test environment. A test passes only if **all** four checks hold: correct recipe, correct MCP tools, QA present, output contract honored.

| # | Prompt | Expected recipe | Expected first tools | Must also show |
|---|---|---|---|---|
| 1 | "Run a Synology NAS assessment for <customer>." | `single-system-synology-nas` | Preflight questions (format + audience) BEFORE any tool call; then `liongard_environment`, `liongard_launchpoint`, `liongard_metric` | Manual Verification Needed section |
| 2 | "Give me a unified firewall posture across all vendors for <customer>." | `system-type-all-firewalls` | `liongard_environment`, `liongard_launchpoint` (never `liongard_system`) | Per-vendor rollup, license expiration roadmap |
| 3 | "Prepare the quarterly business review for <customer> for last quarter." | quarterly business review recipe | `liongard_environment`, `liongard_metric`, `liongard_timeline` | Period confirmed, What Changed section |
| 4 | "How ready is <customer> for a HIPAA Security Rule review?" | `hipaa-readiness` | `liongard_environment`, `liongard_launchpoint`, `liongard_metric` | Control mapping, policy/external documentation gaps |
| 5 | "Assess <customer>'s email security." (no recipe covers it) | None - agent says no matching recipe | None | Offers the closest recipes; does not improvise |
| 6 | Test 1 with external audience | Same as 1 | Same as 1 | No verification log; "Data as of" per inspector |
| 8 | "Run the new customer onboarding assessment for <customer>." Reply `continue` at each batch prompt. | `new-customer-onboarding` | Inventory tools, then per-vendor run cards, 4 vendors per turn | Every deployed vendor appears; coverage table has no unexplained "Not evaluated"; one merged final report |
| 9 | After test 1 for two vendors, "Combine these into one summary." | Merge of earlier result blocks in the conversation | No new metric calls needed | Values identical to the earlier results |
| 7 | Set brand name and primary color in the MSP profile, rerun test 2 | Same as 2 | Same as 2 | Brand name and color appear in the report |

## Regression procedure

1. After each package update, rerun all tests on both editions.
2. Record pass/fail and the recipe/tool the agent chose.
3. Any routing miss is a catalog problem: improve the canonical recipe `description` trigger phrases, rebuild, retest. Never hand-edit generated files.

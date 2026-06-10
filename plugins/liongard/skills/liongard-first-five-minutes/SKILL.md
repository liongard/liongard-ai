---
name: liongard-first-five-minutes
description: Use after a user first connects Liongard MCP and asks what to try, how to verify setup, or how to get oriented quickly.
---

# Liongard First Five Minutes

Use this skill to give a newly connected user a small, safe orientation flow.

## Workflow

1. Confirm the MCP is connected by calling `liongard_environment` with
   `{ "operation": "COUNT" }`.
2. List up to 5 visible environments with `liongard_environment LIST`.
3. Explain whether the token appears tenant-wide or narrowly scoped based on
   the visible result set. Do not infer more than the tools show.
4. Run one safe operational check:
   - `liongard_alert COUNT` for open alerts, or
   - `liongard_agents COUNT` for agents, or
   - `health-check` prompt if the user wants a broader operator summary.
5. Offer three next questions:
   - `What alerts are open in <environment>?`
   - `Which agents are offline or suspended?`
   - `Run a compliance check for <environment>.`

## Output

Keep the answer short:

- Connection status.
- Visible environment count.
- One useful operational signal.
- Suggested next prompt.

## Guardrails

- Do not expose raw tokens or config values.
- Do not claim tenant-wide visibility unless the tool output makes that clear.
- If any list is paginated or truncated, state that explicitly.

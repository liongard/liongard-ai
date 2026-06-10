# Example prompts

Copy these into your Liongard-connected agent (Claude Code, Claude Desktop,
Cursor, VS Code) and see what it comes back with.

---

## Environments and customers

- List my Liongard environments.
- How many environments does my tenant have?
- Find environments whose name contains "contoso".
- Give me an overview of the **Acme Corp** environment.

## Alerts

- What alerts are open in the **Acme Corp** environment?
- How many Critical alerts are open across the tenant right now?
- Show me the 10 oldest open alerts.
- Investigate alert 12345.
- What alerts fired on the **WindowsAD** inspector in the last 24 hours?

## Inspections and launchpoints

- Which launchpoints are currently failing?
- Which agents are offline or suspended?
- List customer-owned agents that have not checked in recently.
- What kinds of systems are in the **Acme Corp** environment?
- Show me an overview of system 9876.
- What inspectors are running against Microsoft 365 across my tenant?
- For customer Acme, which systems haven't been inspected in the last 48 hours?

## Inventory

- How many active users does **Acme Corp** have?
- Break down identities by MFA status for **Acme Corp**.
- List admin accounts across all environments.
- Which devices don't have EDR installed in **Acme Corp**?
- Count devices by operating system for **Acme Corp**.

## Cyber risk / compliance

- What's our MFA coverage across all environments?
- Run a compliance check on **Acme Corp**.
- Which environments have the worst EDR coverage?
- Show me encryption coverage for the **finance** environments only.
- Compare compliance posture between **Acme Corp** and **Contoso**.

## Recent change / history

- What changed on system 9876 in the last 7 days?
- Show me the timeline for the **Azure AD** system in **Acme Corp**.
- Any notable detections in the last 24 hours?
- What's been modified in **Acme Corp** this week?

## High-level / natural language

- What are the top 3 things I need to pay attention to today?
- If I only have 15 minutes, what should I look at in Liongard right now?
- Summarize the health of my tenant in one paragraph.
- Write a weekly status report for **Acme Corp**.

---

## Power-user combos

These take advantage of the `liongard_query` tool's multi-step reasoning:

- Using liongard_query, tell me which customers had the most actionable alerts
  this week and rank them by severity-weighted impact.
- Using liongard_query, list environments where MFA coverage dropped below
  80% and summarize the biggest gaps.
- Using liongard_query, draft a morning standup summary covering alerts,
  failing inspections, and compliance deltas for our top 5 customers.

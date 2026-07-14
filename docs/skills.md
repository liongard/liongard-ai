# Skills

Claude Code **Skills** are small, self-contained playbooks an agent can load
when the task matches their description. They let you teach Claude — and any
other agent that understands the Anthropic skill format — how to use the
Liongard MCP for specific workflows without polluting every conversation with
boilerplate.

**Canonical location:** skills live under
[`plugins/liongard/skills/`](../plugins/liongard/skills) — each in its own
folder with a `SKILL.md` file. This is the package `/plugin install liongard`
ships. The repo-root [`.claude/skills/`](../.claude/skills) directory is an
auto-generated mirror (so Claude Code auto-loads skills when launched inside
this repo); never hand-edit it. Regenerate it with
`bash scripts/sync-plugin-to-claude.sh`.

---

## Skills shipped here

| Skill | What it's for |
| --- | --- |
| [`liongard-mcp`](../plugins/liongard/skills/liongard-mcp/SKILL.md) | Baseline "how to use the Liongard MCP" reference. Loaded automatically when a user mentions Liongard, agents, alerts, environments, inspections, etc. |
| [`liongard-first-five-minutes`](../plugins/liongard/skills/liongard-first-five-minutes/SKILL.md) | Safe first-run orientation after connecting the MCP: count environments, sample visible scope, and suggest next prompts. |
| [`liongard-investigate-alert`](../plugins/liongard/skills/liongard-investigate-alert/SKILL.md) | End-to-end alert investigation: gather context on the alert, launchpoint, related detections, and propose remediation. |
| [`liongard-environment-health`](../plugins/liongard/skills/liongard-environment-health/SKILL.md) | Daily environment health check — open alert load, failing inspections, recent changes, cyber-risk posture. |
| [`liongard-compliance-audit`](../plugins/liongard/skills/liongard-compliance-audit/SKILL.md) | Compliance audit across the five cyber-risk pillars (MFA, EDR, encryption, firewall, TLS/SSL). |

---

## How Claude loads skills

When you launch Claude Code (or Claude Desktop) from a directory that contains
`.claude/skills/`, Claude discovers each skill by reading its `SKILL.md`
frontmatter. Skills with a matching `description` get loaded automatically
when the user's question fits the trigger conditions.

You can also reference a skill explicitly:

```text
Use the liongard-investigate-alert skill to triage alert 12345.
```

---

## Skill authoring conventions

Every skill we ship follows a few rules:

1. **Front-matter first.** Each `SKILL.md` starts with YAML front matter that
   declares `name`, `description`, and (optionally) `tools`.
2. **MCP-first.** Skills call `liongard_*` tools directly instead of
   reimplementing logic in prose. When the Liongard prompt catalog already has
   a matching prompt (for example `compliance-check`), the skill tells the
   agent to call it rather than duplicating the prompt body.
3. **Resolve IDs once.** If the user names an environment, system, or alert,
   the skill resolves it to an ID via `liongard_environment` /
   `liongard_launchpoint` / `liongard_alert` **before** the main workflow.
4. **Honor pagination.** Skills treat `Pagination` fields as authoritative and
   keep paging when the user's question demands a full count. When they
   intentionally stop early, they say so in the final answer.
5. **Scope respectfully.** Skills never invent `environmentId` values or try
   to bypass token scope.
6. **Short, reusable output.** The final answer leads with the direct answer
   (number, list, yes/no) and keeps supporting evidence compact.

---

## Writing your own Liongard skill

1. Create a directory under `plugins/liongard/skills/` (the canonical home)
   named for your workflow, for example
   `plugins/liongard/skills/liongard-my-workflow/`.
2. Add a `SKILL.md` file. The minimum template:

   ```markdown
   ---
   name: liongard-my-workflow
   description: Short description that tells Claude when to use this skill.
   ---

   # Liongard My Workflow

   ## When to use
   - …

   ## Inputs
   - …

   ## Steps
   1. …
   2. …

   ## Output shape
   - …
   ```

3. Run `bash scripts/sync-plugin-to-claude.sh` to refresh the `.claude/`
   mirror, then commit both and open a PR. See
   [`../CONTRIBUTING.md`](../CONTRIBUTING.md).

---

## Using Liongard skills from other clients

The canonical plugin package stores skills under
[`plugins/liongard/skills`](../plugins/liongard/skills). The root
`.claude/skills/` directory is an auto-generated mirror of it (kept in sync by
`scripts/sync-plugin-to-claude.sh`) so Claude Code auto-loads skills when
launched from this repository. Other clients are catching up:

- **Claude Desktop** reads the `.claude/skills/` mirror when you open the repo
  as your workspace.
- **Cursor** may use a slightly different convention (`.cursor/skills/`);
  copy or symlink from `plugins/liongard/skills` if your Cursor version
  supports local skills.
- **VS Code / Copilot** doesn't have a first-class skill primitive yet. You
  can still paste the relevant skill body into your chat to get the same
  benefit.

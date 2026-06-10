# Liongard AI

Connect Claude Code, Cursor, VS Code, Codex-style CLIs, and other MCP clients
to your Liongard tenant with the hosted Liongard MCP server.

The stable baseline is simple:

1. Create a Liongard **AI Preferences -> Access Tokens** credential.
2. Configure your agent for `https://<instance>.app.liongard.com/api/mcp`.
3. Send `Authorization: Bearer <accessKeyId>:<accessKeySecret>`.
4. Ask: `List my Liongard environments.`

The MCP server is hosted by your Liongard instance. This repo provides the
public plugin package, setup commands, skills, installers, and client docs.

## Fastest Path

### Claude Code Plugin

```text
/plugin marketplace add liongard/liongard-ai
/plugin install liongard
```

Then run:

```text
/liongard-setup
```

### Any MCP Client

Use the shared config generator:

```bash
node scripts/liongard-mcp-config.js --client cursor --print
node scripts/liongard-mcp-config.js --client claude-desktop --write --backup
node scripts/liongard-mcp-config.js --client generic --print
```

See [`docs/quickstart.md`](docs/quickstart.md) and
[`docs/harnesses.md`](docs/harnesses.md) for client-specific setup.

## Recipe Library

A library of agent-friendly **recipes** that turn live Liongard data into
consistent MSP artifacts — QBRs, single-system assessments, cyber-insurance
evidence, onboarding checklists, roadmap planning, and more.

**First-time setup (once per MSP):** copy
`config/msp-config.local.yaml.example` → `config/msp-config.local.yaml`
and fill in your MSP's brand identity, preferred vendor stack, and SLA
baselines. Every recipe inherits from it — no per-recipe edits needed for
brand or stack.

| Path | What's there |
| --- | --- |
| [`config/`](config) | **MSP-wide settings: brand, vendor stack, SLAs. Edit once — recipes inherit.** |
| [`recipes/`](recipes) | 121 recipes across 9 categories (single-system, system-type, domain, compliance, QBR, onboarding, sales, roadmap, external-data). |
| [`personas/`](personas) | Index pages for 7 MSP personas (NOC, SOC, vCIO, TAM, Sales, Executive, Finance) — each lists the recipes that role uses. |
| [`reference/`](reference) | Inspector aliases, asset-field reference, onboarding-QA coverage matrix, QA retry pattern, persona × recipe matrix, future-recipes roadmap. |
| [`primitives/`](primitives) | Semantic registry (`registry.yaml`) + per-inspector metric primitive YAML files (937 metrics, 76 inspectors). Enables intent routing and metric impact analysis. |
| [`templates/`](templates) | Recipe skeleton + reusable customization / output blocks. |
| [`partner-resources/`](partner-resources) | Partner-facing tools and skills: recipe picker and recipe scaffold generator. |

### Using a recipe

0. **First-time setup (once per MSP):** copy
   `config/msp-config.local.yaml.example` → `config/msp-config.local.yaml`
   and fill in your MSP's brand identity, preferred vendor stack, and SLA
   baselines. Every recipe inherits from it — no per-recipe edits needed for
   brand or stack.
1. Open the recipe in your Claude Code / Claude Desktop session with the
   Liongard MCP connected.
2. (Optional) Edit the recipe's **Customize for your MSP** block — section
   names, recipe-specific SLAs, output format. Most recipes work out of the
   box once `msp-config.local.yaml` is set.
3. Reference the recipe in your prompt:

```
Using the recipe at recipes/single-system-analysis/by-inspector/sentinelone.md,
produce a Q4 single-system assessment for SentinelOne system <SYS_ID> in
environment <ENV_ID>. Output as Word docx.
```

4. The agent fetches data via the Liongard MCP, applies your customization,
   produces the artifact.

### Personas served

| Persona | Index | Primary focus |
| --- | --- | --- |
| NOC | [`personas/noc/`](personas/noc) | Agent health, capacity, failed jobs, stale inspectors |
| SOC | [`personas/soc/`](personas/soc) | Privileged access, MFA, EDR, threats, compliance evidence |
| vCIO / Account Manager | [`personas/vcio-account-manager/`](personas/vcio-account-manager) | QBR / PBR, refresh roadmaps, renewals |
| Technical Alignment Manager | [`personas/technical-alignment-manager/`](personas/technical-alignment-manager) | Standards alignment, onboarding QA, configuration drift |
| Sales | [`personas/sales/`](personas/sales) | Pre-sales discovery + renewal upsell |
| Executive | [`personas/executive/`](personas/executive) | Outcomes, business language |
| Accounting / Finance | [`personas/accounting-finance/`](personas/accounting-finance) | Renewal calendars, license utilization, cost recovery |

### Reference materials

In [`reference/`](reference):

- **`inspector-aliases.md`** — every Liongard inspector with vendor abbreviations,
  product-family aliases, parent-company / legacy names, and the API `query=` keyword.
  Use this to translate user shorthand (S1, M365, KB4, FGT, Entra, etc.) into the
  right inspector.
- **`asset-fields.md`** — complete field reference for `liongard_device`,
  `liongard_identity`, `liongard_domain` (the reconciled asset-inventory tools) with
  server-side filter parameters, projection fields, and PBR pattern library.
- **`onboarding-qa-coverage.md`** — EDR coverage matrix showing which fields each EDR
  exposes directly vs. requires asset-inventory fallback.
- **`qa-retry-pattern.md`** — the canonical Quality Assurance + Manual Verification
  pattern every recipe runs before rendering output.
- **`personas-recipe-matrix.md`** — which recipes serve which personas; read by recipe
  or by persona.
- **`future-recipes-roadmap.md`** — what's shipped, what's planned, and the
  proposed-metric backlog.

---

## What's In This Repo

| Path | What it is |
| --- | --- |
| [`.claude-plugin/`](.claude-plugin) | Claude Code marketplace manifest. |
| [`plugins/liongard/`](plugins/liongard) | Installable Claude Code plugin package. |
| [`.claude/`](.claude) | Compatibility copy for launching Claude Code from this repo. |
| [`docs/`](docs) | MCP overview, auth, tools, prompts, harnesses, troubleshooting. |
| [`scripts/`](scripts) | Config generator, installers, validation, smoke tests. |
| [`examples/`](examples) | Example prompts and workflows. |

## Supported Harnesses

| Harness | Setup status | Notes |
| --- | --- | --- |
| Claude Code | Verified path | Plugin + `claude mcp add` HTTP config. |
| Claude Desktop | Config provided | Uses `claude_desktop_config.json`. |
| Cursor | Config provided | Uses `~/.cursor/mcp.json` or project `.cursor/mcp.json`. |
| VS Code / GitHub Copilot | Config provided | MCP setting names can vary by Copilot version. |
| Codex / generic CLI agents | Config provided | Use streamable HTTP MCP with Bearer auth. |
| Gemini CLI, Continue, OpenCode, Windsurf | Documented pattern | Verify against your installed version. |
| Copilot Studio / stateless clients | Advanced | Authenticated `POST /api/mcp` can work without a prior session. |

Full matrix: [`docs/harnesses.md`](docs/harnesses.md).

## What The Liongard MCP Can Do

The native tool catalog includes:

- `liongard_environment` — list and inspect environments.
- `liongard_agents` — list, get, and count Liongard agents.
- `liongard_alert` — query actionable alerts.
- `liongard_detection` — query change detections.
- `liongard_launchpoint` — unified launchpoint and system tool.
- `liongard_asset` — query inventory identities and devices.
- `liongard_metric` — list and evaluate metrics.
- `liongard_cyber_risk_dashboard` — security posture rollups.
- `liongard_report` — list and retrieve reports.
- `liongard_timeline` — walk per-system inspection history.
- `liongard_query` — grounded natural-language Q&A.
- `liongard_navigate` — compact discovery for gateways.

The live server can also expose tenant-configured external MCP tools. The
canonical schema is always `tools/list` from your tenant. See
[`docs/tools-reference.md`](docs/tools-reference.md) and
[`docs/capability-status.md`](docs/capability-status.md).

## Authentication

Bearer token auth is the supported setup path for every harness:

```http
Authorization: Bearer <accessKeyId>:<accessKeySecret>
```

Create credentials in Liongard under **AI Preferences -> Access Tokens**. OAuth
discovery endpoints exist for compatibility, but OAuth setup is client-dependent
and should be treated as experimental until verified in your harness.

Details: [`docs/authentication.md`](docs/authentication.md).

## Troubleshooting

Run `/liongard-doctor` in Claude Code or use:

```bash
node scripts/liongard-mcp-smoke-test.js \
  --instance acme.app.liongard.com \
  --token "$LIONGARD_MCP_TOKEN"
```

More help: [`docs/troubleshooting.md`](docs/troubleshooting.md).

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Keep docs accurate against the live
MCP server behavior and never commit real tokens.

## License

[Apache 2.0](LICENSE).

# Customization Block — Reference

Every recipe under `/recipes` includes a "Customize for your MSP" block at the top. This
file is the canonical reference for what knobs the block exposes and what each one does.
Authors should embed (not link) the relevant subset of this block into each recipe.

The block is a single fenced YAML code block so an agent can parse it and a human can
edit it without touching recipe internals.

```yaml
output:
  format: markdown            # markdown | word | pptx | xlsx
                              # Recipe-level constraints may narrow this set; check the
                              # recipe's "Output formats" section.
  filename: "<artifact>-<customer>-<period>.md"
                              # The agent substitutes <customer> and <period> from
                              # inputs. <period> uses ISO format (e.g., 2026-Q2).
  # brand: INHERITS from config/msp-config.yaml — the MSP's company name, colors,
  #   logo, letterhead, etc. live there and propagate to every recipe.
  #   Override per-recipe ONLY when a specific deliverable needs a different
  #   brand (e.g., a co-branded report for a white-label engagement). To
  #   override, uncomment + set the values:
  #
  # brand:
  #   company_name: "Override MSP Name"
  #   primary_color: "#1F4E79"
  #   logo_path: ""

sections:
  # Rename headings to match your existing report templates. Set any value to null to
  # suppress that section entirely.
  executive_summary: "Executive Summary"
  data_overview: "Overview"
  health_metrics: "Health & Compliance"
  detail_table: "Detail"
  insights: "Key Insights"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"
  appendix: "Appendix — Methodology"

audience:
  tone: "balanced"           # technical | balanced | executive
                              # technical: full jargon, raw counts, query references.
                              # balanced: jargon explained on first use.
                              # executive: outcomes & risk language only; no JMESPath.
  reading_level: "manager"   # engineer | manager | executive

slas:
  # Override these to match your standards. The agent compares evaluated values against
  # these thresholds when computing health/compliance status.
  patch_age_days_max: 30
  mfa_coverage_pct_min: 95
  edr_coverage_pct_min: 95
  agent_uptodate_pct_min: 95
  license_expiration_warn_days: 30
  inspector_lastseen_days_max: 7
  password_min_length: 14
  account_inactive_days_max: 45    # before flagged as stale
  warranty_expiration_warn_days: 90
  firmware_age_months_max: 24

inspectors_in_scope:
  # List the inspectors you actually deploy. The recipe will gracefully skip any
  # inspector listed in the recipe but absent from this list — and surface the absence
  # in the Data Gaps section.
  - <inspector-slug>

naming:
  client_term: "Client"      # Client | Tenant | Customer | Account
  environment_term: "Environment"
  site_term: "Site"
  endpoint_term: "Endpoint"  # Endpoint | Device | Workstation
  identity_term: "User"      # User | Identity | Account

reporting_period:
  default: "last_quarter"    # last_quarter | last_30_days | last_year | custom
  fiscal_year_start_month: 1 # 1 = Jan; 7 = Jul fiscal year start, etc.
  custom_start: ""           # ISO date — only used when default == "custom"
  custom_end: ""             # ISO date — only used when default == "custom"

verification:
  log_queries: true          # Append the verification log to the artifact.
  redact_values: true        # Always true for library-shared outputs; the agent never
                              # writes concrete tenant/customer values into the
                              # verification log.

qa:
  # See reference/qa-retry-pattern.md for the canonical QA + manual-verification
  # implementation. Every recipe runs the QA pass after data collection and
  # before rendering output.
  retry_on_null: true                            # retry calls that return null
  retry_on_empty_array: false                    # empty array often means "no records"
  retry_attempts: 2                              # extra attempts after the first
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7      # systems / assets older than this = stale-data flag
  flag_count_divergence_threshold_pct: 5         # two tools disagree by more than X% = surface both
  surface_proposed_metrics: true                 # list known [PROPOSED] metric gaps
  surface_single_source_visibility: true         # flag AD-only / one-inspector assets when relevant
  manual_verification_section_required: true    # the appendix is mandatory in the deliverable
```

## Notes

- Recipes that don't need every knob (e.g., a sales recipe with no SLAs) should remove
  the unused subsections rather than carry empty values.
- The `inspectors_in_scope` list is critical — it's how the recipe gracefully handles
  MSPs that haven't deployed every inspector the recipe references. Always include it
  in single-system, system-type, and domain recipes.
- `naming` lets the recipe respect MSP terminology without forking. The agent does a
  string substitution before rendering output.

# Recipe Spec Format — Full Reference

The recipe-generator skill takes a per-inspector YAML spec. This file
documents every field — required, optional, and how each maps to the
generated recipe.

## Required fields

```yaml
inspector:
  slug:                          # string — the canonical Liongard inspector slug
  id:                            # int — the canonical Liongard inspector ID
  display_name:                  # string — vendor-facing name
  category:                      # enum — one of:
                                 #   "Apps & Services" | "Beta" | "Cloud" | "Endpoint" | "Network"
  target_system_type:            # string — e.g. "Endpoint Security (EDR)", "Firewall", "Network Controller"
  parent_child:                  # bool — does this inspector use a parent/child model?
  identifier_jmespath:           # string — JMESPath that resolves to the system's
                                 # display name from its dataprint
                                 # (e.g. "SystemInfo.accountName" for SentinelOne)

recipe:
  family:                        # always "single-system-analysis" for this skill
  scope_summary:                 # 1-2 sentences — used in the description frontmatter
                                 # to tell the agent when to invoke this recipe
  trigger_phrases:               # list of strings — concrete user phrasings the
                                 # recipe should respond to
                                 # e.g. ["pull SentinelOne data for <CUSTOMER>",
                                 #       "S1 PBR", "single system review of S1"]
  personas:                      # list — from {noc, soc, vcio-account-manager,
                                 #               technical-alignment-manager,
                                 #               sales, executive,
                                 #               accounting-finance}
  output_formats:                # list — from {markdown, word, pptx, xlsx}
```

## Recommended fields

```yaml
aliases:
  user_facing:                   # list — common shorthand the user might say
                                 # e.g. ["S1", "Singularity"] for SentinelOne
  legacy:                        # list — old / renamed product names
                                 # e.g. ["NinjaRMM"] for NinjaOne

slas:                            # SLA thresholds the recipe applies. The
                                 # generator embeds them in the customization
                                 # block. If omitted, recipe defaults are used.
  patch_age_days_max:            # int — for OS / patch-related recipes
  warranty_warn_days:            # int — hardware lifecycle
  inspector_lastseen_days_max:   # int — staleness threshold (default 7)
  edr_coverage_pct_min:          # int — for EDR recipes
  license_expiration_warn_days:  # int — license expiration warning
  # Add any vendor-specific SLAs here

metrics:
  - id:                          # int or "[PROPOSED]" — Liongard metric ID
    name:                        # string — metric name as in Liongard
    jmes_path:                   # string — JMESPath query the metric uses
    purpose:                     # string — 1-line description of what this
                                 # metric answers
    result_shape:                # optional — e.g. "<integer>", "<bool>", "<array<string>>"
    compliant_when:              # optional — e.g. "0", "true", "non-empty"
  # ... more metrics

onboarding_qa_coverage:          # for EDR-class recipes — the row from
                                 # reference/onboarding-qa-coverage.md
  total_endpoints:               # ✅ | 🔍 | ⚠️ | ❌
  active_30d:                    # ✅ | 🔍 | ⚠️ | ❌
  inactive_60d:                  # ✅ | 🔍 | ⚠️ | ❌
  not_protected:                 # typically 🔍 (asset cross-check)
  servers_split:                 # ✅ | 🔍 | ⚠️ | ❌
  alerts:                        # ✅ | 🔍 | ⚠️ | ❌
  partner_validated_notes:       # string — notes from the partner onboarding QA
                                 # audit specific to this inspector
                                 # (generic phrasing only — never name the partner)

proposed_metric_gaps:            # list — proposed metrics this recipe
                                 # references that don't yet exist. The
                                 # generator surfaces these in the QA section
                                 # and reports them after generation.
  - field:                       # string — what the field would be called
    fallback:                    # string — how the recipe works around it
    jira_ticket:                 # optional — CORE-XXXX if filed already

cross_check:                     # asset-inventory cross-check spec
  asset_type:                    # "device" | "identity" | "domain"
                                 # which liongard_* tool this recipe uses
                                 # for cross-check
  filter_pattern:                # string — the filter used for cross-check
                                 # e.g. for an EDR: 'inspectors contains "<slug>"'
  coverage_question:             # string — what coverage question this answers
                                 # e.g. "compute devices not in <vendor>'s
                                 # protection set"
```

## Optional fields

```yaml
identifier:
  notes:                         # string — extra prose about how to identify
                                 # the right system, beyond the JMESPath

trigger_keyword:                 # string — the exact `query=` keyword for
                                 # liongard_system LIST. Defaults to the
                                 # inspector slug minus "-inspector" if omitted.

dataprint_keys:                  # list — top-level keys on this inspector's
                                 # dataprint, with descriptions. Helps the
                                 # generator populate the "per-vendor data" table.
  - key:                         # string
    description:                 # string

field_gotchas:                   # list — vendor-specific field caveats the
                                 # generator notes in the data-sources section
                                 # (these become inline notes, not TODOs).
  - field:                       # string
    note:                        # string

large_arrays:                    # list — arrays that can be very large and
                                 # warrant a length()-only pattern note
  - field:                       # string
    typical_size:                # string — e.g. "8000+ entries"

time_series_supported:           # bool — does liongard_metric EVALUATE_TIME_SERIES
                                 # work for trends on this inspector?

vendor_console_url_pattern:      # optional — link template for the vendor
                                 # console (e.g. https://falcon.crowdstrike.com)
                                 # used in "supplement from vendor portal"
                                 # references

related_recipes:                 # list — paths to related recipes in this
                                 # library (e.g. system-type rollup, compliance)
                                 # that the generator links from the top-of-file
                                 # pull quote
  - path:                        # string
    relationship:                # string — "rollup", "compliance", "carrier"
```

## Field reference details

### `inspector.parent_child`

When `true`, the generator includes the **Locating the right system**
section's parent/child distinguishing pattern. The author still fills in
the specific dataprint-shape differences in the TODO marker.

When `false`, the section is shorter — just the system-search command and
how to identify the single per-tenant system.

### `inspector.identifier_jmespath`

For parent/child inspectors, this JMESPath identifies which child to use.
Examples:

| Inspector | identifier_jmespath |
|---|---|
| SentinelOne | `SystemInfo.accountName` |
| Cisco Umbrella | `SystemInfo.Name` |
| Datto BCDR | `SystemInfo.clientCompanyName` |
| Acronis Cyber Cloud | `Account.name` |

For non-parent/child, this can be the most-useful identifying field on the
single per-tenant dataprint (e.g. `Organization[0].displayName` for
Microsoft 365).

### `recipe.scope_summary`

Goes into the YAML frontmatter `description` field, which is what triggers
auto-invocation. Should:
- Start with "Use this skill when…"
- Mention typical persona use cases
- Include the most likely user phrasings

### `metrics[*].id`

Use the actual integer Liongard metric ID. For metrics that don't yet
exist, use the literal string `"[PROPOSED]"` and put the descriptive name
in `name`. The generator surfaces all `[PROPOSED]` metrics in the QA
section's "known proposed-metric gaps" subsection.

### `cross_check`

The generator uses this to populate the asset-inventory cross-check
subsection. Typical patterns:

```yaml
# EDR
cross_check:
  asset_type: device
  filter_pattern: 'inspectors contains "sentinelone-inspector"'
  coverage_question: "compute devices without SentinelOne in their inspectors[]"

# Identity provider
cross_check:
  asset_type: identity
  filter_pattern: 'inspectors contains "knowbe4-inspector"'
  coverage_question: "active identities not enrolled in KnowBe4"

# Domain
cross_check:
  asset_type: domain
  filter_pattern: 'managed=true'
  coverage_question: "domains not flagged as managed"
```

## Validation

The generator checks before producing output:

- All required fields present
- `inspector.slug` exists in `reference/inspector-aliases.md`
- `inspector.id` matches the slug in the inspector mapping xlsx
- `recipe.family == "single-system-analysis"` (or skill scope rejected)
- `metrics[*].id` are integers OR `"[PROPOSED]"`
- `personas` are from the canonical 7
- `output_formats` are from {markdown, word, pptx, xlsx}

If any check fails, the generator stops and asks the user to fix the spec
before proceeding.

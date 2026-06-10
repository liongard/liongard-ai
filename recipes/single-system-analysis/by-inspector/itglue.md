---
name: single-system-itglue
description: >
  Use this skill when the user wants a single-system analysis of an
  IT Glue tenant — documentation completeness audit, stale-document
  detection, password-vault audit, per-customer documentation coverage,
  permissions audit, expiration tracking. Trigger phrases: "IT Glue
  review", "ITG posture for <customer>", "IT Glue documentation
  completeness", "stale documentation in IT Glue", "IT Glue password
  vault audit", "ITG permissions audit", "what's missing from
  <customer>'s documentation".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric"
personas: [technical-alignment-manager, vcio-account-manager, noc, soc, accounting-finance]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  # Reconciled 2026-05-29 vs live dataprint (live production environment, inspected 2026-05-29).
  # The dataprint exposes Organizations/Users/Domains/FlexibleAssetTypes/Contacts metadata —
  # NOT document bodies, password vaults, or expiration records, and Users carry no MFA field.
  # documents-*, passwords-*, expirations-*, users-mfa-enabled, users-stale-enabled pruned to
  # internal/proposed-metrics-backlog.md.
  - metrics:itglue-inspector:organizations-total-count
  - metrics:itglue-inspector:organizations-active-count
  - metrics:itglue-inspector:users-total-count
  - metrics:itglue-inspector:users-with-sign-in-count
  - metrics:itglue-inspector:contacts-count
  - metrics:itglue-inspector:flexible-asset-types-count
  - metrics:itglue-inspector:domains-count
---

# Single-System Analysis — IT Glue

> **Inspector:** `itglue-inspector` (ID 26). Apps & Services category.
> **One system per IT Glue account.** Dominant MSP documentation
> platform — owns customer-specific runbooks, network diagrams,
> passwords, asset documentation, contacts, and SOPs.
>
> **References:** `reference/inspector-aliases.md` (ITG, IT Glue).
> Pairs with every other inspector — IT Glue is the **documentation
> wrapper** that holds the human-readable context Liongard's per-
> inspector dataprints can't.

---

## Why this recipe matters

IT Glue is the system of record for **everything an MSP needs to deliver
service to a customer that isn't directly in Liongard's per-inspector
data** — runbooks, contacts, vendor portals, passwords, network diagrams,
SOPs. When documentation drifts (stale runbooks, missing diagrams,
expired passwords), the MSP can't deliver service efficiently and the
customer's risk profile climbs.

This recipe is the **TAM's primary tool** for the documentation-
completeness side of the technical-alignment standard. It complements
every other recipe by surfacing the documentation gaps that the per-
inspector recipes can't see.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-itglue-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  organization_inventory: "Organization Inventory"
  documentation_completeness: "Documentation Completeness"
  stale_documentation: "Stale Documentation"
  password_audit: "Password Vault Audit"
  permissions_audit: "Permissions Audit"
  expiration_tracking: "Expiration Tracking (certs, warranties, licenses)"
  per_org_scorecard: "Per-Organization Documentation Scorecard"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"

slas:
  organization_documentation_min_assets: 10    # minimum asset count per org
  required_document_types_per_org:             # MSP standard: every org has these
    - "network-diagram"
    - "primary-contact"
    - "after-hours-contact"
    - "credentials-vault"
    - "warranty-list"
    - "vendor-portal-list"
    - "license-list"
    - "backup-runbook"
    - "incident-response-runbook"
  stale_document_age_days_max: 365             # docs not updated in N days = stale
  stale_password_age_days_max: 365             # passwords not rotated in N days = stale
  password_without_2fa_max: 0                  # privileged passwords without 2FA = critical
  asset_without_documentation_max: 5           # acceptable orphan count
  user_inactive_days_max: 90                   # IT Glue users not logged in N days
  permissions_review_cadence_days: 180         # last permissions review > N days = finding

reporting_period:
  default: "current_state"

qa:
  retry_on_null: true
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: false
  manual_verification_section_required: true
```

---

## When to use

- "IT Glue posture for <customer>"
- "Documentation completeness for <customer>"
- "Stale documentation roster"
- "IT Glue password vault audit"
- "Per-organization documentation scorecard"
- "Pre-PBR documentation review"
- "Pre-onboarding documentation check (does this new customer's
  documentation meet our standard yet?)"
- "Post-incident documentation update audit"

Cadence: monthly per MSP (rollup); quarterly per customer in PBR;
ad-hoc post-incident.

Personas:
- **TAM** (primary — documentation completeness is the TAM's job;
  drives the standards-alignment scorecard)
- **vCIO / Account Manager** (per-customer scorecard for PBR)
- **NOC** (operational — runbook + contact accuracy)
- **SOC** (password / permissions / vendor-portal audit)
- **Accounting / Finance** (vendor-portal + license documentation
  for renewal cycles)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the IT Glue account) | Yes | `liongard_system LIST query="itglue"` |
| Optional: focus on a specific customer org | No | User prompt |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="itglue"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Organization inventory

```
liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative:
#   "itglue.organizations.totalCount"
#   "itglue.organizations.activeCount"
#   "itglue.organizations.inactiveCount"
#   "itglue.organizations.byType"             (customer / vendor / internal)
#   "itglue.organizations.byMyGlueStatus"     (sharing enabled vs not)
```

### Step 4 — Documentation completeness

```
#   "itglue.documents.totalCount"
#   "itglue.documents.byOrganization"         (per-org count)
#   "itglue.documents.byCategory"             (runbook / diagram / contact / etc.)
#   "itglue.documents.archivedCount"
#   "itglue.organizations.missingRequiredDocsList"
                                               # per slas.required_document_types_per_org
```

Per-organization scorecard: for each required document type, mark
present / missing / archived.

### Step 5 — Stale-documentation detection

```
#   "itglue.documents.lastUpdatedDays"        (per document)
#   "itglue.documents.staleCount"             (> slas.stale_document_age_days_max)
#   "itglue.documents.staleByCategory"
#   "itglue.documents.staleByOrganization"
```

### Step 6 — Password vault audit

```
#   "itglue.passwords.totalCount"
#   "itglue.passwords.byOrganization"
#   "itglue.passwords.byCategory"             (AD admin / vendor portal / database / etc.)
#   "itglue.passwords.lastRotationDays"
#   "itglue.passwords.staleCount"             (> slas.stale_password_age_days_max)
#   "itglue.passwords.notes2faStatus"         (where IT Glue tracks 2FA status)
#   "itglue.passwords.archivedCount"
#   "itglue.passwords.notesUsedInRunbook"     (passwords linked from runbooks vs orphan)
```

### Step 7 — Permissions audit

```
#   "itglue.users.totalCount"
#   "itglue.users.activeCount"
#   "itglue.users.byRole"                     (Administrator / Manager / Editor / Creator / etc.)
#   "itglue.users.mfaEnabledCount"
#   "itglue.users.lastLoginDays"
#   "itglue.users.staleEnabledCount"          (> slas.user_inactive_days_max)
#   "itglue.permissions.lastReviewDays"
#   "itglue.permissions.byOrganization"       (which orgs have which users)
```

### Step 8 — Expiration tracking (certs / warranties / licenses)

```
#   "itglue.expirations.upcomingCount"        (anything with an expiration date in range)
#   "itglue.expirations.byCategory"
#   "itglue.expirations.byOrganization"
#   "itglue.expirations.expiredOverdueCount"
```

> **IT Glue is the only consolidated expiration tracker** for content
> not directly in a Liongard inspector — vendor-portal contracts, SSL
> certs the MSP manages, software licenses outside the EDR / backup /
> RMM scope. Surface this section prominently.

### Step 9 — Per-organization scorecard

For each customer organization, produce a row:

| Customer | Required docs present | Stale docs | Passwords | Last update | Score |
|---|---|---|---|---|---|

Score = `(required_docs_present / total_required) * 100 - stale_penalty - password_penalty`.

### Step 10 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on:
1. Retry persistent nulls.
2. Stale-inspector flag.
3. **Privacy** — password vault content NEVER appears in any output.
   Only counts + metadata. Plaintext / hash redaction is non-negotiable.
4. Cross-tool divergence — IT Glue's organization list should align
   with the MSP's PSA customer list.
5. Proposed-metric gaps.

### Step 11 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | IT Glue is documentation tooling; endpoint-question matrix doesn't apply. |
| CIS Controls (v8.1) | ✅ | Maps to CIS 5.1 (account inventory — IT Glue users), 5.4 (admin role separation), 6.4 (IT Glue user MFA), 8.2 (audit logs of vault access). Password-vault security is CIS 5.6 (password manager). |
| Cyber-insurance domain files | ⚠️ | Aligns with `domains/governance.md` Q22–Q26 (documentation, vendor management); password vault touches `domains/auth.md` Q14–Q17 (privileged credential management) via the vault audit. |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this when IT Glue is the documentation platform; per-customer scorecard becomes the "documentation health" section. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| Org missing required documents | "<N> organizations missing <document-type>. Backfill per MSP onboarding standard." |
| Stale documents > SLA | "<N> documents not updated > <N> days. Schedule TAM documentation review." |
| Stale passwords > SLA | "<N> passwords not rotated > <N> days. Rotate per password-management standard." |
| Privileged password without 2FA flag | "<N> privileged passwords flagged without 2FA in metadata. Confirm 2FA actually enforced at source system." |
| Orphaned passwords (not linked to runbook) | "<N> passwords not referenced from any runbook. Confirm purpose or archive." |
| IT Glue user without MFA | "Enforce MFA on <N> IT Glue users. Documentation platform is high-value target." |
| Stale enabled IT Glue users | "<N> users inactive > <N> days. Confirm separation, disable." |
| Permissions review overdue | "Permissions last reviewed <N> days ago. Schedule quarterly review." |
| Expirations overdue / upcoming | "<N> tracked expirations overdue or upcoming within <N> days. Triage." |
| Org scorecard below threshold | "Organization <O> scoring <N>/100. Documentation backfill required." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Document content / runbook text | not in dataprint (privacy) | IT Glue Console |
| Password values | not in dataprint (privacy — never) | IT Glue Console (vault access controlled) |
| Per-document edit history | partial | IT Glue Console |
| Network diagram accuracy | external | Manual TAM review |
| Cross-tool sync health (M365 → IT Glue sync, RMM → IT Glue sync) | partial | IT Glue Console |
| MyGlue customer-facing portal usage | partial | IT Glue Console |

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST + liongard_system LIST | per inspector | array | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3-9 | liongard_metric VALUE | envId=<ENV_ID> sysId=<SYS_ID> metric=<id> | varies | ok per metric |
| 10 | QA pass (privacy validation included) | per `reference/qa-retry-pattern.md` | varies | ok |
| 11 | render | per `output.format` | <artifact path> | ok |
```

---
name: system-type-all-cloud-storage
description: >
  Use this skill when the user wants a unified cloud-storage assessment
  across all platforms in an environment — Box, Dropbox, Google Drive,
  and OneDrive (via the Microsoft 365 inspector). Trigger phrases:
  "cloud storage posture for <customer>", "all cloud storage", "data
  exposure audit", "external sharing across cloud storage", "cloud
  storage consolidation candidate", "where is sensitive data shared".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_identity"
personas: [soc, technical-alignment-manager, vcio-account-manager, executive, accounting-finance]
output_formats: [pptx, word, xlsx, markdown]
primitives:
  - metrics:box:content-stale-file-count
  - metrics:box:licensing-seat-total
  - metrics:box:licensing-seat-used
  - metrics:box:licensing-utilization-pct
  - metrics:box:retention-policies-count
  - metrics:box:security-admin-count
  - metrics:box:security-app-auth-count
  - metrics:box:shares-external-count
  - metrics:box:shares-open-upload-link-count
  - metrics:box:shares-public-link-count
  - metrics:box:storage-total-gb
  - metrics:box:storage-used-gb
  - metrics:box:storage-utilization-pct
  - metrics:box:system-info
  - metrics:box:users-active-count
  - metrics:box:users-external-count
  - metrics:box:users-inactive-count
  - metrics:box:users-mfa-enabled-count
  - metrics:box:users-total-count
  - metrics:dropbox:content-stale-file-count
  - metrics:dropbox:licensing-seat-total
  - metrics:dropbox:licensing-seat-used
  - metrics:dropbox:licensing-utilization-pct
  - metrics:dropbox:security-admin-count
  - metrics:dropbox:security-app-authorization-count
  - metrics:dropbox:shares-expiration-configured-count
  - metrics:dropbox:shares-external-count
  - metrics:dropbox:shares-public-link-count
  - metrics:dropbox:storage-total-gb
  - metrics:dropbox:storage-used-gb
  - metrics:dropbox:storage-utilization-pct
  - metrics:dropbox:team-folders-orphaned-count
  - metrics:dropbox:team-folders-total-count
  - metrics:dropbox:users-active-count
  - metrics:dropbox:users-mfa-enabled-count
  - metrics:dropbox:users-suspended-count
  - metrics:dropbox:users-total-count
  - metrics:google-drive:folders-internet-commentable
  - metrics:google-drive:folders-internet-editable
  - metrics:google-drive:folders-internet-readable
  - metrics:google-drive:shared-drives-list
  - metrics:google-drive:shared-drives-summary
  - metrics:google-drive:users-list
  - metrics:google-drive:users-total-count
  - metrics:microsoft-365:active-users-count
  - metrics:microsoft-365:admin-users-mfa-disabled-count
  - metrics:microsoft-365:associated-domains
  - metrics:microsoft-365:conditional-access-policies-list
  - metrics:microsoft-365:directory-sync-enabled
  - metrics:microsoft-365:directory-sync-stale-hours-count
  - metrics:microsoft-365:disabled-users-count
  - metrics:microsoft-365:disabled-users-with-licenses-count
  - metrics:microsoft-365:enterprise-e3-licenses-consumed
  - metrics:microsoft-365:enterprise-e5-licenses-consumed
  - metrics:microsoft-365:licensed-users-count
  - metrics:microsoft-365:licenses-total-assigned-count
  - metrics:microsoft-365:non-admin-users-mfa-disabled-count
  - metrics:microsoft-365:privileged-users-count
  - metrics:microsoft-365:privileged-users-list
  - metrics:microsoft-365:security-defaults-enabled
  - metrics:microsoft-365:sharepoint-sites-count
  - metrics:microsoft-365:stale-licensed-users-count
  - metrics:microsoft-365:unlicensed-users-count
  - metrics:microsoft-365:users-not-mfa-registered-count
---

# System-Type Assessment — All Cloud Storage

> Unified cloud-storage posture across every cloud-file inspector
> deployed at the customer. Surfaces the **whole-environment external-
> sharing surface** — the highest-leverage data-exposure finding most
> customers don't realize they have.
>
> **Cloud-storage inspectors covered:**
>
> | Inspector | Recipe |
> |---|---|
> | Box | `recipes/single-system-analysis/by-inspector/box.md` |
> | Dropbox | `recipes/single-system-analysis/by-inspector/dropbox.md` |
> | Google Drive (Workspace) | `recipes/single-system-analysis/by-inspector/google-drive.md` |
> | OneDrive / SharePoint Online (via M365) | `recipes/single-system-analysis/by-inspector/microsoft-365.md` |
>
> **Why this rollup exists:** The highest data-exposure risk in most
> environments isn't the EDR / firewall configuration — it's the
> "anyone with the link" document accidentally shared in 2019 that
> nobody's reviewed since. Per-platform audits miss the cross-platform
> sprawl story; this rollup surfaces it.
>
> **References:** `reference/qa-retry-pattern.md`;
> `reference/inspector-aliases.md`.

---

## Customize for your MSP

```yaml
output:
  format: pptx
  filename: "<customer>-cloud-storage-posture-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  cover: "Cloud Storage Posture Assessment"
  executive_summary: "Executive Summary"
  platform_inventory: "Cloud Storage Platforms in Use"
  user_rollup: "User & MFA Rollup"
  storage_rollup: "Storage Utilization"
  external_sharing_rollup: "External Sharing Surface (Reconciled)"
  high_risk_shares: "High-Risk Shares"
  stale_content_rollup: "Stale Content"
  license_rollup: "License Utilization"
  consolidation_opportunity: "Consolidation Opportunity"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Manual Verification"
  appendix: "Appendix — Per-Platform Detail"
  verification_log: "Verification Log"

audience: { tone: "balanced" }

slas:
  external_share_count_warn: 0
  public_link_count_max: 0
  anyone_with_link_count_max: 0
  stale_content_days_max: 365
  storage_utilization_pct_warn: 85
  license_utilization_pct_warn: 90
  user_mfa_required: true
  cloud_storage_consolidation_target: 2  # MSP standard: ≤ 2 cloud-storage platforms
                                         # (e.g., M365 OneDrive + 1 specialized like Box for legal)

reporting_period:
  default: "current_state"

stack:
  auto_discover: true
  inspectors_in_scope: []
  inspectors_to_skip: []

narrative:
  lead_with_external_sharing: true       # this is the recipe's most-differentiated content
  surface_no_issue_categories: true
  redact_individual_file_names: true     # never name specific files in executive output

qa:
  retry_on_null: true
  retry_attempts: 2
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: false
  surface_single_source_visibility: true
  manual_verification_section_required: true
```

---

## When to use

- "Cloud storage posture for <customer>"
- "External sharing across cloud storage"
- "Where is sensitive data shared at <customer>?"
- "Cloud storage consolidation candidate"
- "Pre-cyber-insurance data-exposure audit"
- "Post-incident scope — where else was this data shared?"

Cadence: monthly per customer; quarterly in PBR; ad-hoc post-incident.

Personas:
- **SOC** (primary — external-sharing surface is the security finding)
- **TAM** (consolidation candidate, retention-policy alignment)
- **vCIO / Account Manager** (consolidation business case, renewal)
- **Executive** (consumes data-exposure risk summary)
- **Accounting / Finance** (consolidated license utilization)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |

---

## Workflow

### Step 1 — Scope + platform discovery

```
liongard_environment LIST searchMode=keyword query="<customer>"

# Discover deployed cloud-storage inspectors
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="box"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="dropbox"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="google-drive"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="microsoft-365"
```

Per-platform deployment table. If more than
`slas.cloud_storage_consolidation_target` (default 2) platforms
deployed, flag as a consolidation candidate.

### Step 2 — Inspector freshness across all platforms

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Per-platform chained findings

For each deployed cloud-storage inspector, chain the per-vendor single
with `audience.tone` inherited. Extract:
- User + MFA status
- Storage utilization
- External-share counts (by share type)
- Stale-content counts
- License utilization

### Step 4 — User + MFA rollup

Compute:
- Total cloud-storage users (reconciled across platforms — users
  with access to ≥ 1 platform)
- MFA coverage % per platform + reconciled
- Users with access to multiple platforms = candidate for
  consolidation review

### Step 5 — Storage utilization rollup

- Total provisioned storage (sum across platforms)
- Total used (sum)
- Per-platform utilization %
- Top consumers (per-user, cross-platform)

### Step 6 — External sharing surface (reconciled)

The differentiated content:

| Share type | Box | Dropbox | GDrive | OneDrive | Total |
|---|---|---|---|---|---|
| External-user shares | N | N | N | N | N |
| Public / anyone-with-link | N | N | N | N | N |
| Public-indexed | n/a | n/a | N | N | N |
| Open-upload (anyone can upload) | N | N | N | N | N |
| Password-protected | N | N | N | N | N |
| Without expiration | N | N | N | N | N |

> **The reconciled view is the recipe's killer chart.** Per-platform
> external-share counts are interesting; the combined view is
> shocking — "Customer X has 4,847 documents externally shared across
> 4 platforms; 12 of them are publicly indexed."

### Step 7 — High-risk shares enumeration

For each platform, identify the **top-risk** shares (subject to
`narrative.redact_individual_file_names == true`, output aggregates
only):

- Open-upload public links (anyone can write)
- Public-indexed documents (Google "Public on the web")
- External shares to disposable / consumer email domains
- External shares to competitor / former-customer domains
- External shares from accounts that have since separated

### Step 8 — Stale content rollup

- Total files not modified > `slas.stale_content_days_max`
- Total storage tied up in stale content
- Per-platform breakdown
- Top stale-content owners (cross-platform)

### Step 9 — License utilization rollup

- Per-platform seat utilization
- Combined seat utilization (when same user has seats in multiple
  platforms — over-licensing)
- Total subscription spend (when MSP populates cost data)

### Step 10 — Consolidation opportunity

If `slas.cloud_storage_consolidation_target` exceeded:

- Per-platform user count + overlap
- Per-platform storage usage + content overlap (best-effort —
  same file across platforms is hard to detect)
- Consolidation target recommendation per MSP standard
- Estimated migration effort + license consolidation savings

### Step 11 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on:
1. Retry persistent nulls per platform.
2. Stale-inspector flags propagate per platform.
3. **Privacy** — file names redacted per `narrative.redact_individual_file_names`.
4. Cross-tool divergence — user lists across platforms should reconcile
   to the identity inventory.
5. Proposed-metric gaps.

### Step 12 — Render

Recommended slide / page order for pptx:

| # | Slide | Content |
|---|---|---|
| 1 | Cover | Customer, period |
| 2 | Executive Summary | Headline external-share count + consolidation flag |
| 3 | Cloud Storage Platforms in Use | Per-platform deployment table |
| 4 | External Sharing Surface (Reconciled) | The Step 6 matrix — leading slide |
| 5 | High-Risk Shares | Step 7 (aggregated, no file names) |
| 6 | User + MFA Rollup | Step 4 |
| 7 | Storage Utilization | Step 5 |
| 8 | Stale Content | Step 8 |
| 9 | License Utilization | Step 9 |
| 10 | Consolidation Opportunity | Step 10 |
| 11 | Recommendations | Prioritized actions |
| 12 | Data Gaps | Step 11 manual-verification appendix |

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | Cloud storage; endpoint-question matrix doesn't apply. |
| CIS Controls (v8.1) | ✅ | Maps to CIS 3.3 (data access management), 3.6 (sensitive data inventory), 3.7 (data classification), 3.12 (retention), 6.3–6.5 (MFA), 14.6 (DLP). |
| Cyber-insurance domain files | ⚠️ | Aligns with `domains/regulatory.md` (HIPAA / GDPR / PCI questions about data-handling controls). |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this when cloud-storage inspectors are deployed; surfaces external-share surface + license utilization for the AM. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| Multiple cloud-storage platforms deployed | "Customer uses <N> cloud-storage platforms. Consolidation candidate — recommended target is <MSP standard>." |
| High external-share count | "<N> external shares active across platforms. Schedule data-exposure review with customer security lead." |
| Public links present | "URGENT: <N> publicly-accessible links across platforms. Review and restrict per data-handling policy." |
| Open-upload public links | "URGENT: <N> 'anyone can upload' links. Remove or restrict immediately." |
| Stale content high | "<N> files (<N> GB) not modified > <N> days. Archive or delete per retention policy." |
| Cross-platform user overlap | "<N> users have seats on <N> platforms. License consolidation opportunity." |
| Storage utilization high (across platforms) | "Combined storage at <N>%. Plan tier consolidation." |
| MFA coverage gap (any platform) | "Enforce MFA on <N> users across <list-of-platforms>." |
| Stale-share owner separated | "<N> external shares owned by separated users. Triage and revoke." |
| Shares to consumer domains | "<N> shares to consumer-email / disposable domains. Confirm legitimate vs. data exfiltration." |
| Retention policy gap | "<N> platforms without retention policy configured. Implement per customer's regulatory requirements." |

---

## Data gaps & coverage notes

Inherits per-platform data gaps. Rollup-specific:

| Field | Status | Source if missing |
|---|---|---|
| Cross-platform same-file detection | external | Manual data-classification audit |
| DLP detail (sensitive-data identification) | partial (per platform) | Dedicated DLP tool |
| External-recipient identity verification | partial | Per-platform consoles |
| Per-tenant subscription cost figures | external (unless MSP populates) | MSP PSA / accounting |
| Share-history audit (when share was created, by whom, what changed) | partial | Per-platform audit logs |

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST + liongard_system LIST | per-platform queries | array<system> | ok per platform |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3 | (chain per-platform singles) | per single-system recipe | per-recipe findings | ok per platform |
| 4-10 | (per-area rollups — derived) | per slas | aggregations | ok |
| 11 | QA pass (privacy validation included) | per `reference/qa-retry-pattern.md` | varies | ok |
| 12 | render | per `output.format` | <artifact path> | ok |
```

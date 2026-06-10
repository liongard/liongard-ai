---
name: single-system-google-drive
description: >
  Use this skill when the user wants a single-system analysis of a
  Google Drive (Workspace Drive) deployment — storage utilization,
  external-sharing audit (security), stale-content detection, shared-
  drive permissions audit, license utilization. Trigger phrases:
  "Google Drive review", "GDrive posture for <customer>", "Google
  Workspace Drive sharing audit", "GDrive storage utilization",
  "shared drive permissions in Google".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_identity"
personas: [soc, technical-alignment-manager, vcio-account-manager, accounting-finance]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  # Reconciled 2026-05-29 vs live dataprint (live production environment, inspected 2026-03-13).
  # security-admin-count and users-mfa-enabled-count added (validated: Users[?isAdmin] /
  # Users[?isEnrolledIn2Sv]). licensing-*, storage-utilization-pct, shared-drives-orphaned-count,
  # and shares-anyone/public-in-search pruned to internal/proposed-metrics-backlog.md
  # (no licensing/quota data; SharedDrives carry no owner/member fields).
  - metrics:google-drive:users-list
  - metrics:google-drive:users-total-count
  - metrics:google-drive:admin-user-count
  - metrics:google-drive:security-admin-count
  - metrics:google-drive:users-2sv-not-enforced-count
  - metrics:google-drive:users-mfa-enabled-count
  - metrics:google-drive:folders-internet-editable
  - metrics:google-drive:folders-internet-readable
  - metrics:google-drive:folders-internet-commentable
  - metrics:google-drive:shared-drives-summary
  - metrics:google-drive:shared-drives-list
---

# Single-System Analysis — Google Drive

> **Inspector:** `google-drive-inspector` (ID 80). Cloud category.
> **One system per Google Workspace tenant's Drive.** Pairs with the
> Google Workspace identity inspector — typically deployed together.
>
> **References:** `reference/inspector-aliases.md` (GDrive, Google
> Drive). Pairs with `google-workspace.md` (identity / IdP side) and
> `recipes/system-type-assessment/all-cloud-storage.md`.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-google-drive-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  user_inventory: "User Inventory"
  storage_utilization: "Storage Utilization"
  external_sharing: "External Sharing Audit"
  stale_content: "Stale Content"
  shared_drives: "Shared Drives Audit"
  license_utilization: "License Utilization"
  security_posture: "Security Posture"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  external_share_count_warn: 0
  anyone_with_link_count_max: 0          # "Anyone with the link" = public
  public_in_search_count_max: 0          # "Public on the web" = highest exposure
  stale_content_days_max: 365
  storage_utilization_pct_warn: 85
  license_utilization_pct_warn: 90
  user_mfa_required: true                # Google Workspace 2-Step Verification
  user_inactive_days_max: 90
  shared_drive_orphan_max: 0             # shared drives without active manager

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

- "GDrive posture for <customer>"
- "Google Drive external sharing audit"
- "Google Drive storage utilization"
- "Shared drive permissions in Google"
- "Stale content in Google Drive"

Cadence: monthly per customer; quarterly in PBR; ad-hoc post-incident
(DLP event, separation).

Personas: SOC (primary — sharing audit), TAM, vCIO/AM, Accounting/Finance.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the Google Drive deployment) | Yes | `liongard_system LIST query="google-drive"` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="google-drive"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — User inventory

```
liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative:
#   "google-drive.users.totalCount"
#   "google-drive.users.activeCount"
#   "google-drive.users.suspendedCount"
#   "google-drive.users.mfaEnabledCount"     (2-Step Verification)
#   "google-drive.users.lastLoginDays"
#   "google-drive.users.byOrgUnit"
```

Cross-reference with `google-workspace-inspector` if deployed for
authoritative user list.

### Step 4 — Storage utilization

```
#   "google-drive.storage.totalGB"
#   "google-drive.storage.usedGB"
#   "google-drive.storage.utilizationPct"
#   "google-drive.storage.byUser"
#   "google-drive.storage.bySharedDrive"
```

### Step 5 — External sharing audit (security)

```
#   "google-drive.shares.externalCount"           (shares to non-tenant users)
#   "google-drive.shares.anyoneWithLinkCount"     (link-based, no auth)
#   "google-drive.shares.publicInSearchCount"     (indexed publicly)
#   "google-drive.shares.byOwner"
#   "google-drive.shares.byExternalDomain"
#   "google-drive.shares.linkDownloadAllowedCount"
```

> **Google Drive's "Anyone with the link" and "Public on the web"
> are the highest-risk sharing modes.** Flag as Critical.

### Step 6 — Stale content

```
#   "google-drive.content.totalFileCount"
#   "google-drive.content.staleFileCount"
#   "google-drive.content.staleByOwner"
#   "google-drive.content.staleStorageGB"
```

### Step 7 — Shared drives audit

```
#   "google-drive.sharedDrives.totalCount"
#   "google-drive.sharedDrives.byManagerCount"    (each shared drive should have ≥ 1 manager)
#   "google-drive.sharedDrives.orphanedCount"     (no active manager)
#   "google-drive.sharedDrives.externalMemberCount"
#   "google-drive.sharedDrives.byMembershipSize"
```

### Step 8 — License utilization

```
#   "google-drive.licensing.seatTotal"
#   "google-drive.licensing.seatUsed"
#   "google-drive.licensing.utilizationPct"
#   "google-drive.licensing.subscriptionTier"     (Business Starter / Standard / Plus / Enterprise)
#   "google-drive.licensing.renewalDate"
```

### Step 9 — Security posture

```
#   "google-drive.security.adminCount"
#   "google-drive.security.serviceAccountCount"
#   "google-drive.security.thirdPartyAppCount"
#   "google-drive.security.dlpEnabled"
#   "google-drive.security.driveContextAwareAccessEnabled"
```

### Step 10 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on retry, freshness, privacy (file names + share URLs redacted
in executive output), cross-tool divergence (vs. Google Workspace
identity), proposed-metric gaps.

### Step 11 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | Cloud storage. |
| CIS Controls (v8.1) | ✅ | CIS 3.3 (data access), 3.6 (data inventory), 3.12 (retention), 6.3–6.5 (Google 2SV / MFA), 14.6 (DLP — partial). |
| Cyber-insurance domain files | ⚠️ | `domains/regulatory.md` for regulated-data customers. |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this when Google Drive is deployed. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| External shares present | "<N> external shares active. Review per policy." |
| "Anyone with link" shares | "URGENT: <N> link-shared documents. Restrict to specific users." |
| "Public on the web" shares | "URGENT: <N> documents publicly indexed. Confirm intent; restrict if unintentional." |
| Stale content | "<N> files not modified > <N> days." |
| Storage utilization high | "Storage at <N>%. Plan upgrade." |
| License utilization high | "License at <N>%. Plan renewal expansion." |
| User without 2SV | "Enforce 2-Step Verification on <N> Google Workspace users." |
| Inactive enabled user | "<N> active users inactive > <N> days." |
| Shared drive without manager | "<N> shared drives orphaned. Reassign manager or archive." |
| Excessive admin count | "Reduce Super Admin count from <N>." |
| Third-party app authorized | "<N> apps authorized. Quarterly review." |
| DLP not configured | "Enable DLP per regulated-data requirements." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Per-file content / DLP detail | partial (Google Workspace DLP) | Google Admin Console + DLP tool |
| Sharing-event audit log | partial | Google Admin Console Audit Logs |
| External recipient verification | partial | Google Admin Console |
| Per-folder permissions detail | partial | Google Admin Console |
| Drive sync client deployment | not in dataprint | Endpoint inventory + Google Admin |

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST + liongard_system LIST | per inspector | array | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3-9 | liongard_metric VALUE + liongard_identity LIST | envId=<ENV_ID> sysId=<SYS_ID> | varies | ok per metric |
| 10 | QA pass (privacy validation) | per `reference/qa-retry-pattern.md` | varies | ok |
| 11 | render | per `output.format` | <artifact path> | ok |
```

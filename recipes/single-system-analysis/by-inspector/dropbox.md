---
name: single-system-dropbox
description: >
  Use this skill when the user wants a single-system analysis of a
  Dropbox Business tenant — storage utilization, external-sharing
  audit (security), stale-content detection, license utilization,
  user inventory + MFA posture, team-folder permissions. Trigger
  phrases: "Dropbox review", "Dropbox posture for <customer>",
  "Dropbox external sharing audit", "Dropbox storage utilization",
  "Dropbox license utilization", "stale content in Dropbox".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_identity"
personas: [soc, technical-alignment-manager, vcio-account-manager, accounting-finance]
output_formats: [markdown, word, pptx, xlsx]
primitives:
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
---

# Single-System Analysis — Dropbox

> **Inspector:** `dropbox-inspector` (ID 34). Cloud category. **One
> system per Dropbox Business tenant.** Cloud file-sync / share
> platform — common at SMB customers and creative / media verticals.
>
> **References:** `reference/inspector-aliases.md` (Dropbox). Pairs
> with `microsoft-365.md` and `recipes/system-type-assessment/all-cloud-storage.md`.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-dropbox-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  user_inventory: "User Inventory"
  storage_utilization: "Storage Utilization"
  external_sharing: "External Sharing Audit"
  stale_content: "Stale Content"
  team_folders: "Team Folder Audit"
  license_utilization: "License Utilization"
  security_posture: "Security Posture"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  external_share_count_warn: 0
  public_link_count_max: 0
  stale_content_days_max: 365
  storage_utilization_pct_warn: 85
  license_utilization_pct_warn: 90
  user_mfa_required: true
  user_inactive_days_max: 90
  password_only_external_share_max: 0
  link_expiration_required: true             # MSP standard: external links have expiration

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

- "Dropbox posture for <customer>"
- "Dropbox external sharing audit"
- "Dropbox storage utilization"
- "Dropbox license utilization"
- "Stale content in Dropbox"
- "Dropbox team folder review"

Cadence: monthly per customer; quarterly in PBR; ad-hoc post-incident.

Personas: SOC (primary — sharing audit), TAM, vCIO/AM, Accounting/Finance.

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the Dropbox tenant) | Yes | `liongard_system LIST query="dropbox"` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="dropbox"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — User inventory

```
liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative:
#   "dropbox.users.totalCount"
#   "dropbox.users.activeCount"
#   "dropbox.users.suspendedCount"
#   "dropbox.users.byRole"                   (Admin / Member / External / etc.)
#   "dropbox.users.mfaEnabledCount"
#   "dropbox.users.lastLoginDays"
```

### Step 4 — Storage utilization

```
#   "dropbox.storage.totalGB"
#   "dropbox.storage.usedGB"
#   "dropbox.storage.utilizationPct"
#   "dropbox.storage.byUser"
#   "dropbox.storage.byTeamFolder"
```

### Step 5 — External sharing audit

```
#   "dropbox.shares.externalCount"
#   "dropbox.shares.publicLinkCount"
#   "dropbox.shares.openLinkWithUploadCount"
#   "dropbox.shares.passwordProtectedCount"
#   "dropbox.shares.expirationConfiguredCount"
#   "dropbox.shares.expiredCount"
#   "dropbox.shares.byOwner"
#   "dropbox.shares.byExternalDomain"
```

### Step 6 — Stale content

```
#   "dropbox.content.totalFileCount"
#   "dropbox.content.staleFileCount"
#   "dropbox.content.staleByOwner"
#   "dropbox.content.staleStorageGB"
```

### Step 7 — Team folder audit

```
#   "dropbox.teamFolders.totalCount"
#   "dropbox.teamFolders.byOwner"
#   "dropbox.teamFolders.byMemberCount"
#   "dropbox.teamFolders.orphanedCount"      (no active owner)
#   "dropbox.teamFolders.archivedCount"
```

### Step 8 — License utilization

```
#   "dropbox.licensing.seatTotal"
#   "dropbox.licensing.seatUsed"
#   "dropbox.licensing.utilizationPct"
#   "dropbox.licensing.tier"
#   "dropbox.licensing.renewalDate"
```

### Step 9 — Security posture

```
#   "dropbox.security.adminCount"
#   "dropbox.security.appAuthorizationCount"
#   "dropbox.security.suspiciousActivityCount"
```

### Step 10 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on retry, freshness, privacy (file names redacted in executive
output), cross-tool divergence (user list vs. M365 / AD), proposed-
metric gaps.

### Step 11 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | Cloud storage. |
| CIS Controls (v8.1) | ✅ | CIS 3.3 (data access), 3.6 (sensitive data inventory), 3.12 (retention), 6.3–6.5 (Dropbox MFA), 14.6 (DLP — partial). |
| Cyber-insurance domain files | ⚠️ | `domains/regulatory.md` for regulated-data customers. |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this when Dropbox is deployed. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| External shares present | "<N> external shares active. Review; expire / revoke per policy." |
| Public link with upload | "URGENT: <N> 'anyone can upload' links active. Remove or restrict." |
| Public link without expiration | "<N> public links without expiration. Add per MSP standard." |
| Public link without password | "<N> public links without password. Add for sensitive content." |
| Stale content | "<N> files (<N> GB) not modified > <N> days. Archive / delete per retention." |
| Storage utilization high | "Storage at <N>%. Plan tier upgrade." |
| License utilization high | "License at <N>%. Plan renewal expansion." |
| User without MFA | "Enforce MFA on <N> Dropbox users." |
| Inactive enabled user | "<N> active users inactive > <N> days. Disable post-separation." |
| Orphaned team folder | "<N> team folders without active owner. Reassign or archive." |
| Excessive admin count | "Reduce admin count from <N>." |
| Third-party app authorized | "<N> apps authorized. Quarterly review." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| File content / DLP detail | partial | Dropbox Admin Console + DLP tool |
| Sharing-event audit log | partial | Dropbox Admin Console |
| External recipient verification | partial | Dropbox Admin Console |
| Per-folder permissions detail | partial | Dropbox Admin Console |
| Smart Sync / selective-sync deployment | not in dataprint | Dropbox Admin Console |

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

---
name: single-system-box
description: >
  Use this skill when the user wants a single-system analysis of a Box
  tenant — storage utilization, external-sharing audit (security),
  stale-content detection, license utilization, user inventory + MFA
  posture, retention compliance. Trigger phrases: "Box review",
  "Box.com posture for <customer>", "Box external sharing audit",
  "Box storage utilization", "Box license utilization", "stale content
  in Box".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_identity"
personas: [soc, technical-alignment-manager, vcio-account-manager, accounting-finance]
output_formats: [markdown, word, pptx, xlsx]
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
---

# Single-System Analysis — Box

> **Inspector:** `box-com-inspector` (ID 14). Cloud category. **One
> system per Box enterprise tenant.** Cloud-content / file-share
> platform — commonly used at customers with compliance / regulated-
> data workflows (legal, healthcare, finance).
>
> **References:** `reference/inspector-aliases.md` (Box, Box.com).
> Pairs with `microsoft-365.md` for the M365-shared-content story
> (Box-vs-OneDrive content sprawl) and `recipes/system-type-assessment/all-cloud-storage.md`
> for the multi-platform rollup.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-box-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  user_inventory: "User Inventory"
  storage_utilization: "Storage Utilization"
  external_sharing: "External Sharing Audit"
  stale_content: "Stale Content"
  retention_compliance: "Retention Compliance"
  license_utilization: "License Utilization"
  security_posture: "Security Posture"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience:
  tone: "balanced"

slas:
  external_share_count_warn: 0           # MSP standard: external shares require explicit policy
                                         # set to >0 to disable the finding
  public_link_count_max: 0               # public (unauthenticated) links = critical
  stale_content_days_max: 365            # files not modified in N days = stale
  storage_utilization_pct_warn: 85
  license_utilization_pct_warn: 90
  user_mfa_required: true
  user_inactive_days_max: 90
  password_only_external_share_max: 0    # external shares without password protection
  retention_policy_required: true        # MSP standard: every customer has retention policy

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

- "Box posture for <customer>"
- "Box external sharing audit"
- "Box storage utilization"
- "Box license utilization"
- "Stale content in Box"
- "Box retention policy review"

Cadence: monthly per customer; quarterly in PBR; ad-hoc post-incident
(e.g., DLP event, lost device, separation).

Personas:
- **SOC** (primary — external-sharing audit, public-link audit, data
  exposure surface)
- **TAM** (retention policy, MSP standards alignment)
- **vCIO / Account Manager** (license utilization, renewal narrative)
- **Accounting / Finance** (license utilization)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the Box tenant) | Yes | `liongard_system LIST query="box"` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="box"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — User inventory

```
liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative:
#   "box.users.totalCount"
#   "box.users.activeCount"
#   "box.users.inactiveCount"
#   "box.users.byRole"                       (Admin / Co-Admin / Standard / External / etc.)
#   "box.users.externalCount"                (cross-organization invited users)
#   "box.users.mfaEnabledCount"
#   "box.users.lastLoginDays"
```

Cross-reference with identity inventory (M365 / AD) — Box users
should align.

### Step 4 — Storage utilization

```
#   "box.storage.totalGB"
#   "box.storage.usedGB"
#   "box.storage.utilizationPct"
#   "box.storage.byUser"                     (per-user top consumers)
#   "box.storage.byFolder"                   (per-folder top consumers)
```

### Step 5 — External sharing audit (the SOC section)

```
#   "box.shares.externalCount"               (shares with external users)
#   "box.shares.publicLinkCount"             (unauthenticated public links)
#   "box.shares.openLinkWithUploadCount"     (anyone can upload — high risk)
#   "box.shares.passwordProtectedCount"
#   "box.shares.expiredCount"
#   "box.shares.expiringWithinWarnDays"
#   "box.shares.byOwner"
#   "box.shares.byOrganization"              (which external orgs have access)
```

> **The external-sharing audit is the recipe's most-differentiated
> security content.** Box's value is collaboration; the risk is the
> "anyone with link" share that escaped review. Flag public + open-
> upload links as Critical.

### Step 6 — Stale content

```
#   "box.content.totalFileCount"
#   "box.content.staleFileCount"             (> stale_content_days_max)
#   "box.content.staleByOwner"
#   "box.content.staleByFolder"
#   "box.content.staleStorageGB"             (storage tied up in stale files)
```

### Step 7 — Retention + compliance

```
#   "box.retention.policiesCount"
#   "box.retention.foldersUnderPolicy"
#   "box.retention.activeHolds"              (legal holds)
#   "box.classification.labeledFileCount"    (when Box Shield / classification enabled)
```

### Step 8 — License utilization

```
#   "box.licensing.seatTotal"
#   "box.licensing.seatUsed"
#   "box.licensing.utilizationPct"
#   "box.licensing.subscriptionTier"
#   "box.licensing.renewalDate"
```

### Step 9 — Security posture

```
#   "box.security.adminCount"                (admin / co-admin role count)
#   "box.security.serviceAccountCount"
#   "box.security.appAuthCount"              (third-party apps authorized)
#   "box.security.suspiciousActivityCount"   (where Box exposes)
```

### Step 10 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on:
1. Retry persistent nulls.
2. Stale inspector flag.
3. **Privacy** — file names + per-share metadata can be sensitive;
   redact in executive output (`narrative.tone == "executive"`).
4. Cross-tool divergence — Box user list vs. M365 / AD identity list.
5. Proposed-metric gaps.

### Step 11 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | Cloud storage, not endpoint coverage. |
| CIS Controls (v8.1) | ✅ | Maps to CIS 3.3 (data access management), 3.6 (sensitive data inventory), 3.12 (data retention), 6.3–6.5 (Box user MFA), 14.6 (DLP — partial via classification). |
| Cyber-insurance domain files | ⚠️ | Aligns with `domains/regulatory.md` (data-handling questions for regulated customers — HIPAA / GDPR / PCI). |
| QBR / quarterly-business-review | ✅ | QBR Step 8 chains this when Box is deployed; surfaces external-share count + storage utilization + license utilization for the AM's renewal conversation. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| External shares present | "<N> external shares active. Review per data-handling policy; expire / revoke as appropriate." |
| Public link with upload | "URGENT: <N> 'anyone can upload' links active. Remove or restrict." |
| Public link without password | "<N> public links without password protection. Review purpose; add password where appropriate." |
| Stale content | "<N> files (<N> GB) not modified > <N> days. Archive or delete per retention policy." |
| Storage utilization high | "Storage at <N>%. Plan tier upgrade or archive cycle." |
| License utilization high | "License utilization <N>%. Plan renewal expansion." |
| User without MFA | "Enforce MFA on <N> Box users." |
| Inactive enabled user | "<N> active users inactive > <N> days. Confirm separation, disable." |
| Retention policy missing | "No retention policy active. Configure per customer's regulatory requirement." |
| Excessive admin count | "Reduce Admin / Co-Admin count from <N> to operational minimum." |
| Third-party app authorized without review | "<N> third-party apps authorized. Quarterly review recommended." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| File content / DLP detail | partial (Box Shield where licensed) | Box Admin Console + DLP tool |
| Sharing-event audit log | partial | Box Admin Console |
| External recipient identity verification | partial | Box Admin Console |
| Per-folder permissions detail | partial | Box Admin Console |
| Classification accuracy (false positives / negatives) | external | Manual data-classification audit |

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

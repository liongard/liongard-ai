---
name: cyber-insurance-readiness
description: >
  Use this skill when the goal is to answer a cyber insurance questionnaire,
  underwriting assessment, or cyber readiness checklist using live Liongard data.
  Trigger phrases: "fill out the cyber insurance questionnaire", "gather evidence for
  insurance", "answer the underwriting questions", "cyber insurance readiness",
  "CIS Control Assist assessment", "insurance application evidence", "cyber readiness
  assessment for <CUSTOMER_NAME>". This skill fetches metric data from Liongard by
  metric name or verified JMESPath and produces an evidence-backed answer set in the format the MSP
  configures (Word, PowerPoint, Markdown, or Excel evidence workbook).
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_identity, liongard_device, liongard_domain"
personas: [vcio-account-manager, soc, technical-alignment-manager]
output_formats: [xlsx, word, markdown]
primitives: []
composes:
  - recipe:compliance:cyber-insurance-auth
  - recipe:compliance:cyber-insurance-backup
  - recipe:compliance:cyber-insurance-endpoint
  - recipe:compliance:cyber-insurance-governance
  - recipe:compliance:cyber-insurance-network
  - recipe:compliance:cyber-insurance-regulatory
  - recipe:compliance:cyber-insurance-vendor
---

# Cyber Insurance Readiness — Master Recipe

This recipe drives the agent through a CIS Controls v8.1 / underwriting-style cyber
insurance questionnaire by domain. Each domain file contains the metric names and
JMESPath queries the agent evaluates; this master file orchestrates the run, applies
your customization, and produces the deliverable.

For carrier-specific variants (e.g., Travelers CyberRisk), see `carriers/`.

---

## Customize for your MSP

```yaml
output:
  format: xlsx              # xlsx | word | markdown
                             # xlsx is the canonical evidence-pack format; word and
                             # markdown produce summary reports for client conversations.
  filename: "<customer>-cyber-insurance-readiness-<YYYY-MM-DD>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  coverage_summary: "Liongard Coverage Summary"
  authentication: "Authentication, MFA & Access Control"
  endpoint: "Endpoint Protection, Patching & Encryption"
  backup: "Backup & Business Continuity"
  network: "Network & Cloud Infrastructure"
  governance: "Governance, Training & Policy"
  regulatory: "Regulatory & Privacy"
  vendor: "Vendor & Third-Party"
  gaps: "Gaps & Remediation Plan"
  appendix: "Appendix — Methodology"

audience:
  tone: "balanced"           # technical | balanced | executive
  reading_level: "manager"

slas:
  patch_age_days_max: 30
  mfa_coverage_pct_min: 100  # carriers typically expect 100% on remote/admin access
  edr_coverage_pct_min: 95
  account_inactive_days_max: 45
  password_min_length: 14
  license_expiration_warn_days: 30

inspectors_in_scope: []      # leave empty to use all referenced inspectors that exist

naming:
  client_term: "Client"
  environment_term: "Environment"
  endpoint_term: "Endpoint"

reporting_period:
  default: "current_state"   # current_state | last_30_days
  evidence_currency_days: 90 # carriers typically require evidence ≤ 30–90 days old

verification:
  log_queries: true
  redact_values: true
```

---

## Coverage summary

Based on CIS Controls v8.1 Control Assist + carrier-form gap analyses:

| Category | Approx Count | Source |
|---|---|---|
| Questions answerable via Liongard metrics | ~37 of 50 core | `liongard_metric EVALUATE` |
| Questions answerable via asset inventory cross-check | ~15 | `liongard_asset` (Identity + Device) |
| Questions requiring manual attestation | ~13 of 50 core | Policy / governance — no inspectable state |
| Regulatory & Privacy questions | ~12 (REG-1..REG-8) | Mostly manual; KnowBe4 for awareness |
| Vendor & Third-Party questions | ~8 (VND-1..VND-8) | Partial Liongard coverage |

Core out-of-scope questions (policy only): commonly Q22, Q24, Q25, Q26, Q29, Q44–Q50.
The exact gap list depends on the carrier; consult the carrier file in `carriers/` if
filling out a specific form.

---

## Workflow

### Step 0 — Pre-flight: internet footprint sweep

Before pulling internal evidence, run the external attack surface recipes. This step:
- Surfaces TLS, email authentication, open-port, and dark-web findings that appear directly
  on carrier forms and in carrier automated scans (Coalition, Corvus both scan before quoting)
- Gives the MSP time to remediate visible issues before the form is submitted
- Produces evidence the carrier can independently verify — the strongest kind

```
# Run all four — or just the ones the client has inspectors for:
recipes/system-type-assessment/all-external-attack-surface.md
  → TLS certificate health (expired certs, weak ciphers, expiry within 30d)
  → DMARC / SPF / DKIM posture (email authentication)
  → Public-IP / open-port exposure (open RDP port 3389, SMB 445, Telnet 23)
  → Dark-web credential exposure

# If you only have specific inspectors:
recipes/single-system-analysis/by-inspector/tls-ssl.md          # TLS certs
recipes/single-system-analysis/by-inspector/internet-domain-dns.md  # DMARC/SPF/DKIM
recipes/single-system-analysis/by-inspector/network-ip-address.md   # open ports
recipes/single-system-analysis/by-inspector/dark-web-monitoring.md  # credential exposure
```

**What each finding maps to on carrier forms:**

| Finding | Carrier question examples |
|---|---|
| Expired or expiring TLS certificate | Corvus DLP scan; Beazley encryption-in-transit; AIG data-in-transit |
| Missing or misconfigured DMARC/SPF/DKIM | Coalition Q6a (email security); Beazley Q7; Hartford SEG; TMHCC §6f |
| Open RDP (port 3389) to internet | At-Bay §15 hard requirement; TMHCC §6b; AIG Q15a; coalition Q6b |
| Dark-web credential exposure | AIG Q14 (compromised passwords); At-Bay posture signal; Beazley controls assessment |

> **Carrier scan note:** Coalition's automated underwriting scan and Corvus's Dynamic Loss
> Prevention (DLP) report check the same signals this step surfaces. Running this before
> submitting means the MSP sees what the carrier will see — and can fix issues proactively
> rather than discovering them as subjectivities or declines.

---

> **Asset Inventory First.** The asset inventory is Liongard's compiled,
> cross-inspector intelligence — for a single identity it reconciles signals from AD,
> M365, Duo, JumpCloud, NinjaRMM, etc. into one record with one synthesized
> `mfaStatus`, `accountActivity`, `privileged`, etc. A per-inspector metric (e.g., AD
> metric 23 Privileged Users Count) only knows what its single inspector knows.
> **Always start with `liongard_asset` and use per-metric `liongard_metric EVALUATE`
> as a cross-check or for inspector-unique fields.**

### Step 1 — Identify the environment
```
liongard_environment LIST
```
Match the customer environment by name. Note `environmentId` — required for every
subsequent call. For multi-site environments, note each site ID; some metrics
(notably backup) are per-site.

### Step 2 — Pull the asset inventory (primary evidence source)

> **The reconciled asset inventory is the primary evidence source for
> every cross-cutting identity and device question on the carrier's
> form.** Liongard deduplicates across every inspector that observed
> the entity — identities by **email address**, devices by **hostname
> / serial number / MAC address** (any of three), domains by **domain
> name** — so one record per real-world entity rolls up every
> inspector's view of it. Per-inspector `liongard_metric` calls in
> Step 3 are reserved for configuration detail the reconciled view
> doesn't expose (specific firewall rules, specific EDR policy
> settings, the actual SPF record, etc.). See
> `reference/asset-fields.md` § Deduplication keys.

```
# Identities — dedup'd by email across M365, AD, Duo, JumpCloud, OneLogin, etc.
liongard_identity LIST environmentId=<ENV_ID> pageSize=200
  fields=["email","displayName","privileged","mfaStatus","mfaMethod","accountActivity",
          "enabled","lastLogin","lastSeen","accountCreated","type","department",
          "membership","emailLicenses","inspectors","inventoryState","authorizationStatus",
          "lastReviewDate"]

# Devices — dedup'd by hostname / serial / MAC across OS, EDR, RMM, AD, hypervisor
liongard_device LIST environmentId=<ENV_ID> pageSize=200
  fields=["hostname","class","role","operatingSystem","osVersion","manufacturer","model",
          "serialNumber","physical","status","antivirus","edr","firmware","warrantyExpiration",
          "winElevenReady","inspectors","inventoryState","lastLogin","lastLoginUser",
          "lastSeen","internalIP","interfaces","environmentId"]

# Domains — dedup'd by domain name across Internet Domain, M365, Google Workspace
liongard_domain LIST environmentId=<ENV_ID> pageSize=200
  fields=["domainName","dmarcHealth","emailDetected","daysTillExpiration","expirationDate",
          "registrar","inspectors","inventoryState"]
```

Paginate using `page=` until all records are retrieved (pageSize=200 per call).
Cache all three arrays for the entire run — every domain file filters this same
dataset client-side. The security fields (`mfaStatus`, `accountActivity`, `antivirus`,
`edr`, `inspectors[]`) are populated in the standard response for these tools.

The asset inventory directly answers — without further calls — the cross-cutting
identity and device questions:

| Question area | Asset filter | Field used |
|---|---|---|
| MFA coverage (Q3, Q4, Q6a–f, MFA-1..3d) | `mfaStatus == "NO"` | identity.`mfaStatus` |
| Privileged accounts (Q14–Q17) | `privileged == true` | identity.`privileged` |
| Stale / dormant accounts (Q30, Q31) | `accountActivity in ["Stale","Dormant","Never Used"] AND enabled == true` | identity.`accountActivity` + `enabled` |
| Default accounts enabled (Q38) | `username in ["administrator","guest"] AND enabled == true` | identity.`enabled` |
| AV / EDR coverage (Q11, Q12) | `edr == null AND inspectors contains <local-inspector>` | device.`edr` + `inspectors[]` |
| Win10 EOL risk (Q1, Q32) | `operatingSystem contains "Windows 10" AND winElevenReady == "Incompatible"` | device.`winElevenReady` |
| Unauthorized assets (Q21) | `inventoryState == "Discovery"` and inspector-coverage gaps | device.`inventoryState` + `inspectors[]` |

> **Liongard IS the IT asset inventory.** Several carrier forms ask directly whether the
> applicant has conducted an IT asset inventory within the last year (e.g., AIG Q17,
> Chubb §4, Hartford §6 data inventory). The answer is affirmative by definition when
> Liongard is deployed and inspectors ran within the evidence currency window
> (`reporting_period.evidence_currency_days`, default 90). In the deliverable, frame it
> as: "IT asset inventory conducted continuously via Liongard; most recent inspection
> [date]. Identity count: [N]. Device count: [N]. Domain count: [N]." This is stronger
> evidence than a point-in-time manual scan — it demonstrates ongoing automated inventory.

For the **complete, authoritative field list** (every Identity and Device asset
field, value shapes, source inspectors, and PBR-style cross-asset patterns), see
**`reference/asset-fields.md`**. The tables below are the cyber-insurance subset
— what's needed to answer the underwriting questions specifically. Use the
centralized reference for hardware inventory, M365 license distribution,
virtualization topology, identity-device joins, and other PBR-relevant fields not
typically required by carriers.

### Step 3 — Cross-check with per-metric evaluation (`liongard_metric EVALUATE`)

For each question, after computing the asset-inventory answer, run the metrics listed
in the domain file as **cross-checks**:

```
# Resolve the system once per inspector type per environment
liongard_system LIST searchMode=keyword query="<inspector-keyword>" environmentId=<ENV_ID>

# Evaluate the metric
liongard_metric EVALUATE metricName=<METRIC_NAME> systemId=<SYS_ID> environmentId=<ENV_ID>
```

Use the **exact metric name** or the verified `jmesPathQuery` from the domain file.
Do not rely on numeric identifiers for metrics; those are tenant-specific. The JMESPath query
runs server-side when evaluated directly; the table column shows it for transparency.

**Why also run the metrics?**
1. **Inspector-unique fields the asset doesn't expose.** Examples: AD password
   policy fields (`AccountPolicy.MinPasswordLength`), M365 Conditional Access policy
   names, SonicWall firewall rules, and Azure NSG exposed RDP ports. These are
   configuration-level evidence that doesn't roll up
   into a per-identity or per-device record.
2. **Quantitative cross-check.** The asset count for "no MFA" should match the sum
   of the per-inspector metric counts (e.g., M365 admin MFA disabled count + Duo
   not-enrolled count + NinjaRMM users without MFA count). Divergence = data quality
   flag (likely a stale inspector run).
3. **Triangulation for high-stakes questions.** Carriers may decline or surcharge
   on MFA gaps. Reporting both asset-derived counts and per-metric counts (with
   matching numbers) is stronger evidence than either alone.

**When the two disagree, the asset value wins** — and the recipe must surface the
divergence as a data-quality flag (likely a recently-stopped inspector, a recent
inspector reconnect, or a sync lag).

#### Identity asset — confirmed field reference

| Field | Type | Values | Insurance use |
|---|---|---|---|
| `accountActivity` | string | "Active", "Stale", "Dormant", "Never Used", "No Activity Found", null | Termination/staleness signal (Q30, Q31) |
| `mfaStatus` | string | "YES", "NO", "PARTIAL", null | MFA enrollment (Q3, Q4, Q6a–f) |
| `mfaMethod` | string/array | policy/method names | Q7 — which MFA tool/policy applies |
| `enabled` | bool | true / false | Q30, Q38 — account enabled state |
| `privileged` | bool | true / false | Q14–Q17 — privileged account flag |
| `lastLogin` | ISO timestamp | last sign-in or null | Q31 — raw 45-day threshold check |
| `lastSeen` | ISO timestamp | most recent inspector observation | Q30/Q31 — stale inspector or orphaned account |
| `accountCreated` | ISO timestamp | account creation date | Q29 — provisioning date |
| `accountType` | string | "application", "service", null | Q16 — service accounts with admin rights |
| `department` | string | dept name or null | Q9f — role-based access by department |
| `membership/InternalIP` | JSON set | AD group memberships | Q14–Q17 — admin group membership per user |
| `relatedEmails` | string | linked UPN/alias | Q30 — alias accounts that survive primary disable |
| `inspectors` | JSON array | which inspectors see this identity | Q6/Q7 — which systems report this identity |
| `inventoryState` | string | "Discovery", "Inventory", "Archive" | MSP workflow state — NOT offboarding evidence |
| `authorizationStatus` | bool | true / false | Q29, VND-2 — Liongard's access authorization flag (sparsely populated) |
| `authorizationStopDate` | ISO timestamp | planned access expiry | VND-3 — when populated |
| `lastReviewDate` | ISO timestamp | most recent manual access review | Q29, VND-2 — access review currency |

> ⚠️ **`inventoryState` is an MSP workflow field, not an offboarding signal.**
> "Archive" means the MSP moved the asset to archive in Liongard — it does not confirm
> formal termination. Real offboarding evidence converges from: (1) `accountActivity`
> in {Stale, Dormant, Never Used}, (2) `lastSeen` > 45 days, (3) identity absent from
> current AD/M365 results OR present in disabled-users metrics.

#### Device asset — confirmed field reference

| Field | Type | Source inspector(s) | Insurance use |
|---|---|---|---|
| `antivirus` | set string | windows-workstation, windows-server, mac inspectors | Q11, Q12 — confirmed AV product(s) |
| `edr` | set string | windows-workstation, windows-server inspectors | Q11, Q12 — confirmed EDR product |
| `operatingSystem` | string | windows-workstation/server, mac inspectors | Q1, Q32 — OS family for EOL assessment |
| `osVersion` | string | windows-workstation/server inspectors | Q1, Q32 — exact build for EOL date lookup |
| `winElevenReady` | string | windows-workstation inspector | Q1, Q32 — Win10 EOL risk; "Incompatible" = HW replacement |
| `warrantyExpiration` | ISO timestamp | windows-workstation (SMBIOS), RMM inspectors | Q1, asset lifecycle |
| `firmware` | string | windows-workstation, network device inspectors | Q35, Q36 — firmware currency |
| `category` | string | Liongard classification | Filter — scope endpoint Qs to category=="compute" |
| `class` | string | windows-workstation/server, RMM | Q11, Q18 — workstation/laptop/server breakdown |
| `physical` | bool | windows-workstation/server | Q18, VND-7 — physical vs. virtual |
| `inspectors` | JSON array | Liongard | Q11, Q21 — coverage gap detection (see below) |
| `lastLogin` | ISO timestamp | windows-workstation, AD | Q21, Q38 — orphaned/unused device |
| `lastLoginUser` | string | windows-workstation | Q21 — who last used the device |
| `lastSeen` | ISO timestamp | Liongard | Stale inspector signal |
| `interfaces` | JSON array | windows-workstation, network inspectors | Q21 — IP/MAC for unauthorized subnet detection |
| `inventoryState` (devices) | string | Liongard (MSP workflow) | Q21 — see workflow note above |

> ⚠️ **`inspectors` array is the coverage gap key for devices.**
> A device with only `active-directory-inspector` is known from AD but NOT locally
> inspected — `antivirus` and `edr` will be `null` because Liongard cannot confirm,
> not because the products are absent. A device with `windows-workstation-inspector`
> present and `edr == null` IS locally inspected — that null means EDR was genuinely
> not detected.

### Step 4 — Multi-inspector questions

Some questions span many inspector types (e.g., Q11 antimalware pulls from Windows,
macOS, Sophos, SentinelOne, Webroot, Bitdefender). The asset-first rule makes these
much simpler than the per-metric approach implies:

1. **From the cached device asset list**, count `edr != null AND inspectors contains
   <local-inspector>` — that is the authoritative confirmed-EDR count across every
   inspector at once.
2. **Distinguish coverage gaps from actual non-compliance** by checking the
   `inspectors[]` array per device:
   - Device locally inspected (Windows WS / Server / mac inspector present) AND
     `edr == null` → genuine gap, ❌ NON-COMPLIANT.
   - Device with only `active-directory-inspector` → not locally inspected, 🔍 REVIEW.
3. **Run the per-vendor metrics as a cross-check** to confirm each EDR/AV product is
   reporting correctly: SentinelOne `AgentsSummary.total`, Sophos metric 402,
   Webroot metric 126, etc. Sum should match the asset-derived confirmed count.
4. **Status = the worst tier across the device population.** Any non-compliant tier
   wins over a partial tier; any partial wins over compliant.

This yields one number to report and a small list of cross-check confirmations,
rather than one number per inspector with no reconciliation.

### Step 5 — Manual attestation items

For questions with no Liongard metric (typical: Q22, Q24–Q26, Q29, Q44–Q50):
- Record the customer's written policy/process attestation.
- Status = `ℹ️ MANUAL`.
- If the customer cannot produce the attestation, status = `❌ NON-COMPLIANT`.

### Step 6 — Produce the gap summary

After completing every domain, filter for `❌ NON-COMPLIANT` and `ℹ️ MANUAL` status.
Produce a prioritized remediation table:

```
| Q# | Question | Status | Gap | Recommended action |
|----|----------|--------|-----|--------------------|
| Q4 | Admin MFA | ❌ | <N> admins lack MFA | Enable MFA in Conditional Access |
| Q31 | Dormant accounts | ❌ | <N> accounts inactive >45d | Disable per offboarding process |
| Q22 | Data Handling Policy | ℹ️ | No written policy | Draft and execute |
```

---

## Inspector keyword reference

> **Use the centralized lookup:** `reference/inspector-aliases.md`.
> That file maps every common shorthand the user might say (S1, M365, O365, Entra,
> AAD, FGT, KB4, NinjaRMM, LabTech, etc.) to the canonical inspector and the exact
> `query=` keyword to pass to `liongard_system LIST`. It also flags the common
> gotchas — Entra/Azure AD vs. the Azure subscription inspector, the three Sophos
> inspectors, parent/child models for SentinelOne / Datto BCDR / Acronis / Veeam /
> Axcient / Umbrella.
>
> Recipes do **not** keep their own keyword tables — they link here so an alias
> change updates one place.

---

## Key constraints

- **Always use metric names or verified JMESPath queries** — never rely on numeric
  identifiers for metrics at runtime.
- **Liongard surfaces evidence, it does not enforce controls** — frame answers as
  "Liongard confirms visibility of X". Never claim Liongard enforces a policy.
- **Null returns ≠ compliant** — if a metric returns null, the system may not be
  inspected. Mark `🔍 REVIEW` with note "system not inspected or inspector not
  configured" and recommend connecting the inspector.
- **Evidence currency matters** — note the assessment date in the deliverable.
  Carriers typically require evidence within 30–90 days.
- **Do not fabricate** — if a system isn't connected to Liongard, say so explicitly.

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ✅ | Cyber-insurance readiness chains from the onboarding inventory. Hardware, identity, backup, and network posture collected at onboarding are the primary evidence inputs for all 7 domain files. Without a complete onboarding record, domain answers are manual attestations rather than evidence-backed. |
| CIS Controls (v8.1) | ✅ | The 7 domain files collectively map to the full CIS control set: `domains/auth.md` (CIS 5–6), `domains/endpoint.md` (CIS 1–4, 7–10), `domains/backup.md` (CIS 10–11), `domains/network.md` (CIS 12–14), `domains/governance.md` (CIS 3, 17–18), `domains/regulatory.md` (CIS 3.11/3.12), `domains/vendor.md` (CIS 15). This recipe is the canonical CIS evidence pack for carrier submission. |
| Cyber-insurance domain files | ✅ | This recipe IS the master that orchestrates all 7 domain files (auth, backup, endpoint, governance, network, regulatory, vendor). The domain files are this recipe's sub-workflow — run each domain file to populate the carrier application evidence. |
| QBR / quarterly-business-review | ✅ | QBR Step 7 chains this recipe for the annual renewal evidence section. Renewal timing drives QBR cadence — the QBR run closest to renewal is the canonical runtime for producing the carrier evidence pack. |

---

## Verification log

The agent appends every query it ran with shape-only result annotations. See
`templates/recipe-skeleton.md` for the canonical verification log format. The log is
mandatory when `verification.log_queries == true` (default).

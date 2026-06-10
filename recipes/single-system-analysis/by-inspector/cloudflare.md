---
name: single-system-cloudflare
description: >
  Use this skill when the user wants a single-tenant analysis of a
  Cloudflare account — zone / domain inventory, DNS posture, SSL/TLS
  edge configuration, WAF & firewall-rule posture, DDoS / rate-limit
  rules, Zero Trust (Access / Gateway / Tunnel) inventory, page-rule
  audit, user / token MFA, audit log retention. Trigger phrases:
  "Cloudflare review", "CF posture for <customer>", "Cloudflare WAF
  audit", "Cloudflare zone inventory", "Cloudflare SSL settings",
  "Cloudflare Zero Trust review", "pull Cloudflare data for
  <customer>".
compatibility: "Requires Liongard MCP: liongard_environment, liongard_system, liongard_metric, liongard_domain"
personas: [soc, technical-alignment-manager, vcio-account-manager, sales, executive]
output_formats: [markdown, word, pptx, xlsx]
primitives:
  # Reconciled 2026-05-29 against live dataprint (live production environment, inspected 2026-03-13).
  # Only primitives that resolve to a VALIDATED/SCHEMA_CONFIRMED definition are listed here.
  # Gap metrics (DNS/SSL/WAF/page-rules/Zero Trust/API-tokens/Workers/Pages/rate-limit/per-user MFA)
  # are tracked in internal/proposed-metrics-backlog.md pending validation on a richer dataprint.
  - metrics:cloudflare-inspector:account-id
  - metrics:cloudflare-inspector:account-name
  - metrics:cloudflare-inspector:account-type
  - metrics:cloudflare-inspector:account-mfa-enforced
  - metrics:cloudflare-inspector:members-total-count
  - metrics:cloudflare-inspector:members-accepted-count
  - metrics:cloudflare-inspector:members-super-admin-count
  - metrics:cloudflare-inspector:roles-count
  - metrics:cloudflare-inspector:access-rules-count
  - metrics:cloudflare-inspector:subscriptions-count
  - metrics:cloudflare-inspector:api-token-status
  - metrics:cloudflare-inspector:api-token-expiry
  - metrics:cloudflare-inspector:audit-logs-count
  - metrics:cloudflare-inspector:zones-total-count
  - metrics:cloudflare-inspector:zones-active-count
  - metrics:cloudflare-inspector:zones-paused-count
  - metrics:cloudflare-inspector:zones-list
---

# Single-System Analysis — Cloudflare

> **Inspector:** `cloudflare-inspector` (ID 82). Cloud category. **One
> system per Cloudflare account.** Covers zones (domains), DNS, SSL/TLS,
> WAF, page rules, rate limiting, Zero Trust (Access / Gateway /
> Tunnel), audit logging, account-level users + tokens.
>
> **External-attack-surface pairing:** Cloudflare sits in front of
> customer-facing properties — its DNS, SSL/TLS, and WAF settings
> shape what an outside attacker sees. The
> `recipes/system-type-assessment/all-external-attack-surface.md`
> rollup chains this recipe when Cloudflare is deployed; combined with
> Internet Domain / TLS / Network IP, it produces the full perimeter
> story.
>
> **References:** `reference/inspector-aliases.md` (Cloudflare, CF).
> Pairs with `internet-domain-dns.md` for the registrar / WHOIS side
> (Cloudflare may also be the registrar via Cloudflare Registrar) and
> `tls-ssl.md` for the per-host TLS posture.

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-cloudflare-review-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  account_identity: "Account Identity & Plan"
  zones: "Zone & Domain Inventory"
  dns_posture: "DNS Posture (DNSSEC, Email Routing)"
  ssl_tls_edge: "SSL/TLS Edge Configuration"
  waf_firewall: "WAF & Firewall Rules"
  rate_limiting: "Rate Limiting & Bot Management"
  page_rules: "Page Rules / Configuration Rules"
  zero_trust: "Zero Trust (Access / Gateway / Tunnel)"
  cdn_workers: "CDN + Workers Inventory"
  audit_logging: "Audit Log Configuration"
  user_token_audit: "User & API Token Audit"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 7
  dnssec_required: false                          # MSP-customizable; set true if standard
  ssl_mode_min: "Full (strict)"                   # Flexible | Full | Full (strict) — least: Full
  edge_min_tls_version: "TLS1_2"
  always_use_https_required: true
  automatic_https_rewrites_required: true
  hsts_required: true
  waf_managed_rules_required: true
  ddos_protection_required: true                  # paid plans only — surface if free plan
  bot_management_required: false                  # paid plans only
  page_rules_max: 20                              # for free / Pro plan; flag if approaching limit
  super_admin_count_max: 3
  super_admin_mfa_required: true
  api_token_age_days_max: 365
  api_token_unused_days_max: 90
  audit_log_retention_review_required: true       # paid plans expose; otherwise external

reporting_period: { default: "current_state" }

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

- "Cloudflare posture for <customer>"
- "Cloudflare PBR / quarterly review"
- "Cloudflare WAF audit"
- "Cloudflare SSL settings review"
- "Zero Trust deployment review"
- "Cloudflare zone consolidation (multiple zones, same customer)"
- "Customer-facing perimeter review (chained from `all-external-attack-surface.md`)"

Cadence: monthly per account; quarterly in PBR; ad-hoc when
Cloudflare publishes a new managed-rule set or after a WAF incident.

Personas:
- **SOC** (primary — WAF, rate-limit, Zero Trust, audit log)
- **TAM** (DNS / SSL standards alignment)
- **vCIO / Account Manager** (plan / feature gaps for renewal upsell)
- **Sales** (pre-sales — when prospect uses Cloudflare, the external-
  attack-surface story includes Cloudflare's edge posture)
- **Executive** (reads top-line Zero Trust adoption + Bot mgmt findings)

---

## Inputs

| Input | Required | Source |
|---|---|---|
| Environment ID | Yes | `liongard_environment LIST` |
| System ID (the Cloudflare account) | Yes — one per account | `liongard_system LIST query="cloudflare"` |

---

## Workflow

### Step 1 — Resolve environment + system

```
liongard_environment LIST searchMode=keyword query="<customer>"
liongard_system LIST environmentId=<ENV_ID> searchMode=keyword query="cloudflare"
```

### Step 2 — Inspector freshness

```
liongard_timeline LIST environmentId=<ENV_ID>
```

### Step 3 — Account identity + plan

```
liongard_metric VALUE environmentId=<ENV_ID> systemId=<SYS_ID> metric="<metric-id>"
# Representative:
#   "cloudflare.account.id"
#   "cloudflare.account.name"
#   "cloudflare.account.type"                   (standard | enterprise)
#   "cloudflare.account.plan"                   (Free / Pro / Business / Enterprise)
#   "cloudflare.account.billingCurrency"
```

### Step 4 — Zones / domains

```
#   "cloudflare.zones.totalCount"
#   "cloudflare.zones.activeCount"
#   "cloudflare.zones.pausedCount"
#   "cloudflare.zones.byPlan"                   (free / pro / business / enterprise per zone)
#   "cloudflare.zones.byStatus"                 (active / pending / moved)
#   "cloudflare.zones.list"
```

Cross-reference with `liongard_domain` — Cloudflare-managed domains
should appear in the reconciled domain inventory.

### Step 5 — DNS posture per zone

```
#   "cloudflare.dns.recordsCount"               (per zone or aggregate)
#   "cloudflare.dns.recordsByType"              (A / AAAA / CNAME / MX / TXT / etc.)
#   "cloudflare.dns.dnssecEnabledZoneCount"
#   "cloudflare.dns.dnssecDisabledZoneCount"
#   "cloudflare.dns.emailRoutingEnabledZoneCount"
#   "cloudflare.dns.spfRecordsCount"
#   "cloudflare.dns.dmarcRecordsCount"
#   "cloudflare.dns.dkimRecordsCount"
#   "cloudflare.dns.proxiedRecordsCount"        (orange-cloud "Proxied" vs DNS-only)
#   "cloudflare.dns.dnsOnlyRecordsCount"
```

### Step 6 — SSL/TLS edge

```
#   "cloudflare.ssl.modeByZone"                 (Off / Flexible / Full / Full strict)
#   "cloudflare.ssl.modeBelowFullStrictCount"   (Flexible or Full — should be Full strict)
#   "cloudflare.ssl.alwaysUseHttpsEnabledCount"
#   "cloudflare.ssl.automaticHttpsRewritesEnabledCount"
#   "cloudflare.ssl.minTlsVersionByZone"
#   "cloudflare.ssl.minTlsBelowStandardCount"
#   "cloudflare.ssl.opportunisticEncryptionEnabledCount"
#   "cloudflare.ssl.tls13EnabledCount"
#   "cloudflare.ssl.hstsEnabledZoneCount"
#   "cloudflare.ssl.hstsMaxAgeBelowStandardCount"
#   "cloudflare.ssl.universalSslEnabledCount"
#   "cloudflare.ssl.advancedCertCount"          (paid feature)
#   "cloudflare.ssl.edgeCertExpiringSoonCount"
```

### Step 7 — WAF & firewall rules

```
#   "cloudflare.waf.enabledZoneCount"
#   "cloudflare.waf.managedRulesetsEnabledCount"
#   "cloudflare.waf.managedRulesetsByOwasp"
#   "cloudflare.waf.customRulesCount"
#   "cloudflare.waf.customRulesByAction"        (block / challenge / log / allow)
#   "cloudflare.firewall.ipAccessRulesCount"
#   "cloudflare.firewall.userAgentRulesCount"
#   "cloudflare.firewall.countryAccessRulesCount"
#   "cloudflare.firewall.zoneLockdownCount"
```

### Step 8 — Rate limiting & bot management

```
#   "cloudflare.rateLimit.rulesCount"
#   "cloudflare.rateLimit.rulesByAction"
#   "cloudflare.ddos.l7ProtectionEnabled"
#   "cloudflare.botManagement.enabled"           (paid plans only)
#   "cloudflare.botManagement.modeByZone"
#   "cloudflare.turnstile.deployed"              (CAPTCHA replacement)
```

### Step 9 — Page rules / config rules

```
#   "cloudflare.pageRules.countByZone"
#   "cloudflare.pageRules.totalCount"
#   "cloudflare.pageRules.byAction"
#   "cloudflare.configRules.count"               (newer rule engine replacing page rules)
```

### Step 10 — Zero Trust (Access / Gateway / Tunnel)

```
#   "cloudflare.zeroTrust.accessApplicationsCount"
#   "cloudflare.zeroTrust.accessApplicationsByType"  (SaaS / Self-hosted / Private network / Infrastructure)
#   "cloudflare.zeroTrust.accessPoliciesCount"
#   "cloudflare.zeroTrust.gatewayDnsPoliciesCount"
#   "cloudflare.zeroTrust.gatewayHttpPoliciesCount"
#   "cloudflare.zeroTrust.gatewayNetworkPoliciesCount"
#   "cloudflare.zeroTrust.tunnelsCount"              (cloudflared / cf tunnels)
#   "cloudflare.zeroTrust.tunnelsByStatus"
#   "cloudflare.zeroTrust.warpClientsActive"
#   "cloudflare.zeroTrust.identityProvidersCount"
```

### Step 11 — CDN + Workers inventory

```
#   "cloudflare.cdn.cachingByZone"               (off / standard / aggressive)
#   "cloudflare.cdn.argoEnabledCount"            (paid)
#   "cloudflare.cdn.cacheReserveEnabledCount"
#   "cloudflare.workers.scriptsCount"
#   "cloudflare.workers.routesCount"
#   "cloudflare.workers.kvNamespacesCount"
#   "cloudflare.workers.r2BucketsCount"
#   "cloudflare.workers.d1DatabasesCount"
#   "cloudflare.pages.projectsCount"
```

### Step 12 — Audit log + user / token audit

```
#   "cloudflare.audit.logRetentionDays"          (paid; otherwise external)
#   "cloudflare.audit.diagnosticExportEnabled"
#   "cloudflare.users.totalCount"
#   "cloudflare.users.byRole"                    (Super Admin / Admin / Read / etc.)
#   "cloudflare.users.superAdminCount"
#   "cloudflare.users.mfaEnabledCount"
#   "cloudflare.users.mfaDisabledCount"
#   "cloudflare.apiTokens.totalCount"
#   "cloudflare.apiTokens.activeCount"
#   "cloudflare.apiTokens.olderThanWarn"
#   "cloudflare.apiTokens.unusedDaysList"
#   "cloudflare.apiTokens.broadScopeCount"       (global / write-everything tokens)
```

### Step 13 — QA pass (per `reference/qa-retry-pattern.md`)

Focus on:
1. Retry persistent nulls.
2. Stale inspector flag.
3. **Cross-tool divergence** — Cloudflare zone list vs. `liongard_domain` reconciled inventory.
4. **TLS edge cross-check** — for each customer-facing host, compare Cloudflare's SSL Mode + min TLS to what the `tls-ssl-inspector` actually observes from the public internet.
5. **Plan-feature gap surfacing** — features that require Pro / Business / Enterprise but show "not configured" need a plan-aware note (don't flag as failure if the customer is on Free).
6. Proposed-metric gaps.

### Step 14 — Render

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | n/a | DNS / CDN / WAF — not endpoint. |
| CIS Controls (v8.1) | ✅ | CIS 3.10 (encryption in transit — SSL Mode + min TLS), 6.3 / 6.4 (CF user MFA), 8.2 (audit logging), 12.2 (WAF as boundary), 13.6 (WAF as IDS), 9.3 / 9.4 (DNS filtering via Gateway — Zero Trust). |
| Cyber-insurance domain files | ✅ | Aligns with `domains/network.md` (WAF + DDoS as perimeter protection), `domains/auth.md` (CF user MFA + Zero Trust identity providers). |
| QBR / quarterly-business-review | ✅ | Chained when Cloudflare is deployed; surfaces edge-TLS posture, WAF / Zero Trust adoption, plan-feature gaps. |
| External attack surface rollup | ✅ | `recipes/system-type-assessment/all-external-attack-surface.md` chains this for edge DNS + TLS + WAF posture per customer-facing zone. |

---

## Insights & recommendations

| Pattern | Recommendation template |
|---|---|
| SSL Mode below Full (strict) | "<N> zones use Flexible / Full SSL. Upgrade to Full (strict) for end-to-end TLS validation." |
| Edge TLS below 1.2 | "<N> zones allow TLS < 1.2 at edge. Raise minimum to 1.2." |
| Always Use HTTPS off | "<N> zones don't enforce Always-Use-HTTPS. Enable per MSP baseline." |
| HSTS not enabled | "<N> zones without HSTS. Enable; configure max-age, includeSubDomains, preload for customer flagship domains." |
| DNSSEC disabled | "<N> zones without DNSSEC. Enable per MSP standard (if upstream registrar supports)." |
| Records DNS-only (not proxied) on customer-facing hosts | "<N> customer-facing records DNS-only. Confirm intentional; proxied (orange-cloud) gives DDoS / WAF / cache benefits." |
| WAF managed rulesets disabled | "<N> zones with WAF disabled. Enable managed rulesets per MSP baseline." |
| Custom firewall rules without allow / block / challenge action | "Audit <N> custom rules with 'log' or 'allow' action; confirm not bypassing protection." |
| Country / IP access rules drift | "<N> country access rules in place. Review for drift / unintended geo-blocking." |
| Bot management not enabled | "Bot Management not enabled (requires Pro+ plan). Consider for credential-stuffing / scraping protection." |
| Zero Trust Access apps without policy | "<N> Access applications without active policy. Review or remove." |
| WARP clients low | "WARP coverage at <N>. Expand client deployment per MSP Zero-Trust standard." |
| Cloudflare user without MFA | "<N> Cloudflare users without MFA. Enforce account-wide." |
| API token old / unused | "<N> API tokens > <N> days old or unused > <N> days. Rotate or revoke." |
| API token with broad scope | "<N> API tokens have global / write-everything scope. Replace with scoped tokens." |
| Audit log retention low / external | "Audit log retention at <N> days. Pro+ exposes retention controls; Free relies on Cloudflare's default. Confirm meets compliance requirement." |
| Page rules near limit | "<N> page rules — within <N> of plan limit. Consider migrating to Configuration Rules." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Per-rule hit counts / Analytics | partial | Cloudflare Analytics |
| Web analytics / Browser Insights | partial | Cloudflare Analytics |
| Bot Management score distribution | partial (paid) | Cloudflare Dashboard |
| Per-WAF-rule sample requests | partial | Cloudflare Security Events |
| Argo / Smart Routing performance | partial | Cloudflare Argo Analytics |
| Account-level Billing detail | partial | Cloudflare Billing |
| Audit log on Free plan | external | Manual review of Activity feed |

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_environment LIST + liongard_system LIST | per inspector | array | ok |
| 2 | liongard_timeline LIST | envId=<ENV_ID> | array<timeline-entry> | ok |
| 3-12 | liongard_metric VALUE + liongard_domain LIST | envId=<ENV_ID> sysId=<SYS_ID> | varies | ok per metric |
| 13 | QA pass | per `reference/qa-retry-pattern.md` | varies | ok |
| 14 | render | per `output.format` | <artifact path> | ok |
```

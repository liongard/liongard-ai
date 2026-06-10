---
name: single-system-godaddy
description: >
  Use this skill when the user wants a single-system assessment of a GoDaddy
  account. Trigger phrases: "GoDaddy domain audit for <customer>", "GoDaddy
  domain expiration", "domain registrar report", "GoDaddy subscription review",
  "GoDaddy certificate audit". Queries the godaddy-inspector dataprint for
  domain inventory, order history, and subscription status.
compatibility: "Requires Liongard MCP: liongard_launchpoint, liongard_metric"
personas: [technical-alignment-manager, vcio-account-manager, accounting-finance]
output_formats: [markdown, word, xlsx]
primitives:
  - metrics:godaddy-inspector:domain-count
  - metrics:godaddy-inspector:domain-list
  - metrics:godaddy-inspector:domains-auto-renew-disabled
  - metrics:godaddy-inspector:domains-transfer-lock-disabled
  - metrics:godaddy-inspector:order-count
  - metrics:godaddy-inspector:order-list
  - metrics:godaddy-inspector:subscription-count
  - metrics:godaddy-inspector:subscription-list
---

# Single-System Assessment — GoDaddy

> Per-account GoDaddy domain registrar and subscription posture. Covers domain
> inventory (expiration, auto-renew, DNS provider), order history, and active
> subscriptions.
>
> **Inspector:** `godaddy-inspector` (beta)
> **Inspector ID:** 122 (confirm via `liongard_launchpoint LIST`)
>
> ⚠️ **Beta inspector notice:** The GoDaddy inspector is in beta as of the
> last validated inspection (2024-12-12). All data arrays (`Domains`, `Orders`,
> `Subscriptions`) were empty in the System A. This recipe documents the
> confirmed schema; field-level validation against live populated data is
> **SCHEMA_CONFIRMED** only. Treat recommendations as guidance pending
> validation against a GoDaddy account with active domains.
>
> **Pairs with:** `all-domains.md` (cross-registrar domain expiration rollup),
> `all-certificates.md` (SSL/TLS certificate expiration), `all-dns.md`
> (DNS provider posture).

---

## Customize for your MSP

```yaml
output:
  format: markdown
  filename: "<customer>-godaddy-assessment-<period>.<ext>"
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed

sections:
  executive_summary: "Executive Summary"
  account_overview: "Account Overview"
  domain_inventory: "Domain Inventory"
  expiring_domains: "Expiring Domains"
  subscriptions: "Active Subscriptions"
  order_history: "Order History"
  recommendations: "Recommended Actions"
  data_gaps: "Data Gaps & Coverage Notes"

audience: { tone: "balanced" }

slas:
  inspector_lastseen_days_max: 30      # GoDaddy API data is relatively static
  domain_expiry_warn_days: 60
  domain_expiry_critical_days: 14
  autorenew_required: true

reporting_period: { default: "current_state" }
```

---

## When to use

- Domain expiration review during onboarding
- Quarterly domain/subscription hygiene audit
- "Which GoDaddy domains are expiring in the next 60 days?"
- Pre-renewal cost review (Accounting/Finance)
- "Is auto-renew enabled on all GoDaddy domains?"

Personas: TAM (domain/subscription hygiene), vCIO/AM (renewal planning), Accounting/Finance
(subscription cost visibility).

---

## Inputs

| Input | Required | Source |
|---|---|---|
| System ID | Yes | `liongard_launchpoint LIST inspectorId=<GoDaddy inspector ID>` |
| Environment ID | Yes | from launchpoint result |

To find the GoDaddy inspector ID for your Liongard instance:
```
liongard_launchpoint LIST environmentId=<ENV_ID> searchMode=keyword query="godaddy"
```

---

## Workflow

### Step 1 — Locate the system

```
liongard_launchpoint LIST environmentId=<ENV_ID> searchMode=keyword query="godaddy"
```

Note the `systemId` and `environmentId`. Check `LastSeen` — if > 30 days, the domain
data may not reflect recent renewals or new registrations.

### Step 2 — Domain inventory

```jmespath
length(Domains)
```

```jmespath
Domains[].{
  domain: domain,
  status: status,
  expires: expires,
  autoRenew: renewAuto,
  renewable: renewable,
  renewDeadline: renewDeadline,
  privacy: privacy,
  locked: locked,
  nameServers: nameServers
}
```

**SCHEMA_CONFIRMED** — field names confirmed via GET_OVERVIEW on System A
(last inspected 2024-12-12). Array was empty on System A — no live value validation.

Expected field types (from inspector schema):
- `domain`: string (FQDN, e.g., `"example.com"`)
- `status`: string (`"ACTIVE"` | `"CANCELLED"` | `"PENDING_DELETE"`)
- `expires`: ISO 8601 datetime string
- `renewAuto`: boolean (`true` = auto-renew enabled — **FLAG false**)
- `renewable`: boolean
- `renewDeadline`: ISO 8601 datetime string
- `privacy`: boolean (WHOIS privacy enabled)
- `locked`: boolean (transfer lock — **FLAG if false; transfer lock recommended**)
- `nameServers`: array of strings

Filter domains expiring within SLA:
```jmespath
Domains[?expires != null]
```
(Sort/filter by date in post-processing — JMESPath does not support date arithmetic natively)

Flag auto-renew disabled:
```jmespath
Domains[?renewAuto == `false`].{domain: domain, expires: expires, status: status}
```

Flag transfer lock disabled:
```jmespath
Domains[?locked == `false`].{domain: domain, status: status}
```

### Step 3 — Subscriptions

```jmespath
length(Subscriptions)
```

```jmespath
Subscriptions[].{
  label: label,
  productGroupKey: productGroupKey,
  status: status,
  expiresAt: expiresAt,
  renewalPeriod: renewalPeriod,
  renewalPeriodUnit: renewalPeriodUnit,
  price: pricing.commitment.maximum.amount,
  currency: pricing.commitment.maximum.currency
}
```

**SCHEMA_CONFIRMED** — confirmed via GET_OVERVIEW; array empty in System A.

Expected field types:
- `label`: string (human-readable subscription name, e.g., `"Website Builder"`)
- `productGroupKey`: string (e.g., `"websiteBuilder"`, `"ssl"`, `"email"`)
- `status`: string (`"ACTIVE"` | `"PENDING"` | `"CANCELLED"`)
- `expiresAt`: ISO 8601 datetime string (flag within `slas.domain_expiry_warn_days`)
- `renewalPeriod`: integer (renewal interval count)
- `renewalPeriodUnit`: string (`"MONTHLY"` | `"ANNUAL"`)

### Step 4 — Order history

```jmespath
length(Orders)
```

```jmespath
Orders[].{
  orderId: orderId,
  createdAt: createdAt,
  type: type,
  totalPrice: pricing.total.amount,
  currency: pricing.total.currency
}
```

**SCHEMA_CONFIRMED** — confirmed via GET_OVERVIEW; array empty in System A.

Expected field types:
- `orderId`: string
- `createdAt`: ISO 8601 datetime string
- `type`: string (`"PURCHASE"` | `"RENEWAL"` | `"CREDIT"`)
- `pricing.total.amount`: number

---

## Insights & recommendations

| Insight | Trigger | Recommended action |
|---|---|---|
| Domain expiring soon (warn) | `expires` within `slas.domain_expiry_warn_days` | "<domain> expires in <N> days — schedule renewal." |
| Domain expiring critical | `expires` within `slas.domain_expiry_critical_days` | "URGENT: <domain> expires in <N> days — renew immediately." |
| Auto-renew disabled | `renewAuto == false` | "Auto-renew is off for <domain> — enable to prevent accidental expiration." |
| Transfer lock disabled | `locked == false` | "<domain> transfer lock is off — enable to prevent unauthorized domain transfers." |
| WHOIS privacy disabled | `privacy == false` | "<domain> has no WHOIS privacy — registrant contact info is publicly visible." |
| Subscription expiring | `expiresAt` within warn window | "Subscription <label> expires <date> — renew or cancel as needed." |
| SSL subscription via GoDaddy | `productGroupKey == 'ssl'` | "SSL certificate managed via GoDaddy subscription — cross-reference with `all-certificates.md`." |

---

## Data gaps & coverage notes

| Field | Status | Source if missing |
|---|---|---|
| Domain inventory + expiration | ⚠️ SCHEMA_CONFIRMED | GoDaddy account console or DNS provider |
| DNS provider per domain | ⚠️ SCHEMA_CONFIRMED | `nameServers` field (schema confirmed) |
| SSL certificates (non-GoDaddy) | ❌ | `all-certificates.md` (external scanner) |
| Email/hosting services | ⚠️ SCHEMA_CONFIRMED | GoDaddy subscriptions |
| Registrar transfer history | ⚠️ SCHEMA_CONFIRMED | Order history (schema confirmed) |
| GoDaddy account security (MFA, login history) | ❌ | GoDaddy console only |
| Domains at other registrars | ❌ | Must chain additional registrar inspectors |

> **Beta note:** All data arrays (`Domains`, `Orders`, `Subscriptions`) were empty on the
> validation System A (System A (inspected 2024-12-12)). This recipe
> cannot be fully validated until a GoDaddy account with active domains is available.
> File a metric request with Liongard support if the inspector consistently returns empty
> arrays on accounts known to have domains.

---

## Coverage cross-check

| Source | Status | Note |
|---|:-:|---|
| `reference/onboarding-qa-coverage.md` | ⚠️ | Domain expiration + auto-renew are onboarding checklist items. Steps 2–3 address these when the inspector returns data. Beta status limits validation. |
| CIS Controls (v8.1) | ✅ | CIS 1.1 (Step 2 — domain asset inventory), 12.1 (Steps 2–3 — DNS/registrar management, transfer lock, expiration monitoring). |
| Cyber-insurance domain files | ✅ | Domain expiration monitoring supports `domains/network.md` registrar hygiene evidence. |
| QBR / quarterly-business-review | ✅ | Domain expiration summary is a standard QBR checklist item for TAMs and vCIOs. |

---

## Output format

Markdown / Word for narrative. **xlsx** for domain inventory table (one row per domain:
name, status, expiration date, auto-renew, transfer lock, WHOIS privacy).

---

## Verification log

```
| Step | Tool | Args | Result Shape | Status |
|------|------|------|--------------|--------|
| 1 | liongard_launchpoint LIST | searchMode=keyword query="godaddy" envId=<envId> | array<launchpoint> | ok — System A |
| 2 | liongard_launchpoint GET_OVERVIEW | sysId=<sysId> envId=<envId> | schema object | SCHEMA_CONFIRMED |
| 2 | liongard_metric EVALUATE | length(Domains) sysId=<sysId> envId=<envId> | 0 | SCHEMA_CONFIRMED (empty array) |
| 3 | liongard_metric EVALUATE | length(Subscriptions) sysId=<sysId> envId=<envId> | 0 | SCHEMA_CONFIRMED (empty array) |
| 4 | liongard_metric EVALUATE | length(Orders) sysId=<sysId> envId=<envId> | 0 | SCHEMA_CONFIRMED (empty array) |
```

Last inspection: 2024-12-12 (beta inspector — data limited; GoDaddy API integration may require active account with domains)

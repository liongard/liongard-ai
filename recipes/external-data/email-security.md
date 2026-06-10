# External Data — Email Security (Proofpoint / Mimecast / Avanan / Vade)

> **Status:** No Liongard inspector for primary email gateways like Proofpoint,
> Mimecast, or Avanan. The Liongard `vade-inspector` (ID 91) covers Vade Secure
> only — for any other gateway, source data externally.

---

## What the deliverable typically needs

Two slides / sections are common in MSP PBRs:

### Email security summary
- **Spam breakdown** — inbound spam count + subcategory split (Spam, SPF failure)
- **Fraud breakdown** — by type (Imposter, Phishing, DMARC, DKIM, SPF)
- **Malware breakdown** — inbound malware count (Virus)
- **Threats by domain** — breakdown by recipient domain
- **Headline KPI** — `<integer>` emails kept out of inboxes in the period
- **Threat composition** — `<integer>` virus, `<integer>` imposter, `<integer>` phishing

### Top accounts by traffic
- Horizontal bar chart per user — Virus, Fraud, Filtered Block, Filtered Allow,
  Spam, Clean
- Top users by email volume with threat breakdown

### Key metrics
- Detected threats in period
- Threat breakdown by category
- Per-domain threat distribution
- Per-user threat targeting

---


```yaml
customize:
  # brand: inherits from config/msp-config.yaml — override per-recipe only if needed
```
## Where to source

| Source | What it provides |
|---|---|
| **Proofpoint TAP API** (Targeted Attack Protection) | Threat data, message-level details, click events |
| **Proofpoint dashboard export** | Spam / fraud / malware reports for the period |
| **Mimecast API** | Targeted Threat Protection, mail-flow stats |
| **Avanan / Check Point Harmony Email & Collaboration API** | Phishing, malware, suspicious counts |
| **Vade for M365** | Use the Liongard `vade-inspector` (ID 91) directly |
| **SIEM integration** | Aggregated email-security events when Proofpoint/Mimecast/Avanan ship logs into the SIEM |

---

## Liongard complementary data

While the gateway itself isn't in Liongard, the **Microsoft 365 inspector** can
contribute related context:

| Liongard signal | What it adds |
|---|---|
| `Domains` / `Organization[0].verifiedDomains` | Verify which domains are active on the tenant. Useful for the "domain X is contributing significantly to inbound spam — assess retaining it" insight pattern. |
| `MailRules` | Mail-flow rules in Exchange that affect filtering (forwarding, transport rules). |
| `Users[?Privileged == 'Yes']` | Cross-reference top-targeted users against M365 role/privilege — leadership/admins are typical phishing targets. |
| `Users` with `signInActivity` | Detect compromised accounts post-phishing — sign-in anomalies after a phishing detection. |

---

## Insights to surface (templates)

- "<integer> emails were kept out of user inboxes in the period — <pct>% of total
  inbound mail."
- "Domain `<domain>` remains active on the M365 tenant and contributes
  disproportionately to inbound spam. Assess whether the alias is still required."
- "Leadership accounts (privileged users in M365) typically receive the most
  phishing attempts due to visibility and authority — confirm MFA and Conditional
  Access policies are in force on these accounts."
- "Recommend deploying URL defense, attachment defense, attachment sandboxing,
  and anti-spoofing policies if not already enabled on the gateway."

---

## How a recipe should consume this file

Recipes that produce a full PBR (e.g., a quarterly environment lookback) should:

1. Detect that email-security is in scope from the customization block.
2. Reference this file in the deliverable's appendix.
3. Prompt the user for the gateway export or API endpoint.
4. Fall back to a "external supplementation required" note in the **Data Gaps**
   section if no source is provided.
5. Layer in the Liongard `Domains` / `MailRules` / privileged-user context where
   it strengthens an insight.

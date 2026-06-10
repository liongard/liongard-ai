# Cyber Insurance Recipes

Liongard-driven evidence packs for cyber-insurance underwriting and renewal questionnaires.

## Files

| File | Purpose |
|---|---|
| `cyber-insurance-readiness.md` | Entry-point recipe. Customization block, workflow, asset-inventory schema, gap summary. Use this when filling out a generic CIS Controls v8.1 / Control Assist style assessment. |
| `cyber-insurance-application-universal.md` | Universal application recipe — carrier-agnostic question map spanning all major underwriting domains. Use as a standalone deliverable or as a master reference when no carrier-specific file exists. |
| `domains/` | Per-control-area metric references. The master skill walks the agent through these in order. |
| `carriers/` | Carrier-specific question maps. Use when filling out a named carrier's form. |

## Domains

| File | Coverage |
|---|---|
| `domains/auth.md` | Authentication, MFA & access control (Q2–Q4, Q6–Q7 incl. 6a–6f, Q14–Q17, Q30–Q31, Q38–Q39) |
| `domains/endpoint.md` | Endpoint protection, patching & encryption (Q1, Q8–Q12, Q10-sub, Q27, Q32–Q34, Q37, Q40) |
| `domains/backup.md` | Backup & business continuity (Q5, Q5a, Q5b, Q46) |
| `domains/network.md` | Network & cloud infrastructure (Q19–Q21, Q35–Q36, Q41–Q43) |
| `domains/governance.md` | Governance, training & policy (Q13, Q18, Q22–Q26, Q28–Q29, Q44–Q50) |
| `domains/regulatory.md` | Regulatory & privacy (REG-1..REG-8 — HIPAA, GDPR, PCI-DSS) |
| `domains/vendor.md` | Vendor & third-party (VND-1..VND-8) |

## External-attack-surface cross-references

Several questions on every cyber-insurance form ask for evidence that
maps directly to the external-attack-surface inspectors:

| Question category | Evidence source |
|---|---|
| Encryption-in-transit posture | `recipes/system-type-assessment/all-external-attack-surface.md` → Encryption-in-Transit section (or single-host: `recipes/single-system-analysis/by-inspector/tls-ssl.md`) |
| Dark-web / credential-exposure monitoring | `recipes/single-system-analysis/by-inspector/dark-web-monitoring.md` |
| Email authentication (DMARC / SPF / DKIM) | `recipes/single-system-analysis/by-inspector/internet-domain-dns.md` or the rollup |
| Public-IP / boundary-exposure | `recipes/single-system-analysis/by-inspector/network-ip-address.md` |

## Carriers

| File | Forms covered |
|---|---|
| `carriers/aig.md` | AIG CyberEdge Application (149053, Ed. 08/23) — ≤$50M revenue |
| `carriers/at-bay.md` | At-Bay New Business (AB-CYB-APP), Renewal (AB-CYB-RAP), Ransomware Supplemental (AB-CYB-RWS) |
| `carriers/beazley.md` | Beazley Below-$250M (F00863 042023), Short Sub-$20M |
| `carriers/chubb.md` | Chubb Cyber ERM (PF-48163 08/17 and 10/16) |
| `carriers/coalition.md` | Coalition Cyber & Tech E&O (SP 17 717 1120 / Active Cyber Policy) |
| `carriers/corvus.md` | Corvus Smart Cyber® Application v3.2 (Sep 2024) |
| `carriers/cowbell.md` | Cowbell Prime 250 Renewal (PRIME 250 075 06 21) + New Business (PRIME 250 003 07 20) |
| `carriers/hartford.md` | Hartford CyberChoice Premier (CB 00 H027 02 0323) + Underwriting (CB 00 H027 03 0824) |
| `carriers/hiscox.md` | Hiscox PRO® Tech & Cyber Renewal (PLP_A0002) |
| `carriers/tokio-marine-hcc.md` | Tokio Marine HCC NetGuard® Plus (NGP-NBA 10.2020) |
| `carriers/travelers.md` | Travelers CYB-14202 (CyberRisk Renewal Application), CYB-14306 (MFA Attestation) |

Each carrier file maps the carrier's question numbers to coverage status (`LIONGARD` / `PARTIAL` / `MANUAL`)
and the relevant `domains/` file section. Metric tables live in the domain files — carrier files
reference them rather than duplicating. Source forms are in `internal/cyber-insurance-forms/<carrier>/`.

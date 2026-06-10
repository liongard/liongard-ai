# SOC — Persona Index

The SOC (Security Operations Center) focuses on **security posture** —
privileged access, MFA coverage, EDR / firewall posture, threat surface,
public exposure, and compliance evidence. SOC recipes produce the data
that drives security conversations and incident response.

## Audience framing

- **Tone:** balanced — security-fluent but consumed by both security
  analysts and customer-facing executives. Lead with risk language;
  technical detail in appendix.
- **Format:** Markdown for analyst use, Word / PowerPoint for customer
  briefings, Excel for evidence packs (cyber insurance, compliance
  audits).
- **Default cadence:** weekly EDR / coverage posture; monthly MFA + privileged audit;
  on-demand for incidents; quarterly for compliance / cyber insurance.

## SLA emphasis (SOC defaults)

| SLA | Default | Why SOC cares |
|---|---|---|
| `mfa_coverage_pct_min` | 100% (admins + remote access), 95% (all users) | Cyber insurance carriers commonly require this |
| `edr_coverage_pct_min` | 95–100% | EDR gaps are the #1 ransomware vector |
| `privileged_no_mfa_max` | 0 | Privileged + no MFA = critical |
| `account_inactive_days_max` | 45 (CIS 5.3) | Stale enabled accounts are abandoned attack surface |
| `default_admin_enabled` | false | Built-in Administrator / Guest must be disabled |
| `wan_management_exposure_allowed` | false | Firewall management on WAN bypasses the firewall |
| `unresolved_threats_max` | 0 | Any open threat warrants triage |

## Common scenarios → recipes

| Scenario | Recipe |
|---|---|
| "Cyber-insurance evidence pack" | `recipes/compliance/cyber-insurance/cyber-insurance-readiness.md` + the 7 domain files |
| "Travelers cyber-insurance renewal application" | `recipes/compliance/cyber-insurance/carriers/travelers.md` |
| "MFA gap across the customer — who's missing it?" | `recipes/system-type-assessment/all-identity-providers.md` (rollup) + per-IdP `recipes/single-system-analysis/by-inspector/{microsoft-365,active-directory,jumpcloud,onelogin,duo-security}.md` + the cyber-insurance auth domain |
| "Unified identity posture — MFA + privileged + stale across all IdPs" | `recipes/system-type-assessment/all-identity-providers.md` |
| "Per-IdP MFA / admin / SSO deep dive" | Corresponding per-IdP single |
| "RMM-user MFA audit (RMM accounts are high-value targets)" | `recipes/system-type-assessment/all-rmm-platforms.md` (technician audit section) |
| "Cloud-storage external sharing audit — where is data exposed?" | `recipes/system-type-assessment/all-cloud-storage.md` (rollup) + per-platform `recipes/single-system-analysis/by-inspector/{box,dropbox,google-drive,microsoft-365}.md` |
| "Public link / 'anyone with the link' triage" | `recipes/system-type-assessment/all-cloud-storage.md` (high-risk shares section) |
| "Documentation completeness + password-vault audit" | `recipes/single-system-analysis/by-inspector/itglue.md` |
| "PSA-user MFA audit (PSA accounts are high-value targets)" | `recipes/system-type-assessment/all-psa-platforms.md` (PSA-user audit section) |
| "Network management exposure audit (Telnet / HTTP / weak SNMP across switches & routers)" | `recipes/system-type-assessment/all-network-infrastructure.md` (mgmt-exposure section) — the leading SOC finding in network rollups |
| "Wireless security posture review (open SSIDs, WEP/WPA1, guest isolation)" | `all-network-infrastructure.md` (wireless section) |
| "Per-switch / per-router AAA + local-user audit" | Corresponding per-vendor network single |
| "Privileged user audit (AD + M365 reconciled)" | `recipes/single-system-analysis/by-inspector/active-directory.md` + `microsoft-365.md` (cross-reference) |
| "EDR fleet posture — coverage % + active threats" | `recipes/system-type-assessment/all-edrs.md` |
| "Server-tier security posture (privileged, RDP, firewall, AV/EDR)" | `recipes/system-type-assessment/all-servers.md` |
| "Firewall posture — WAN management exposure, wide-open WAN→LAN rules, default credentials" | `recipes/system-type-assessment/all-firewalls.md` |
| "Stale / disabled account roster — offboarding compliance" | `recipes/single-system-analysis/by-inspector/active-directory.md` (stale/disabled section) + `microsoft-365.md` |
| "Email-authentication posture (DMARC, SPF, DKIM)" | `recipes/system-type-assessment/all-domains.md` (DMARC posture section) + `recipes/single-system-analysis/by-inspector/internet-domain-dns.md` (single-domain deep dive) + `recipes/external-data/email-security.md` for gateway side |
| "External attack surface posture (whole environment, outside-in)" | `recipes/system-type-assessment/all-external-attack-surface.md` (combines domain / TLS / IP / dark-web) |
| "Credential exposure / dark-web — are any of our users in breach dumps?" | `recipes/single-system-analysis/by-inspector/dark-web-monitoring.md` (cross-joined with identity inventory) |
| "Encryption-in-transit evidence (TLS protocols / cipher strength) for compliance" | `recipes/single-system-analysis/by-inspector/tls-ssl.md` |
| "Public IP reputation / RBL hit — why is mail bouncing?" | `recipes/single-system-analysis/by-inspector/network-ip-address.md` |
| "Backup posture for ransomware preparedness — offsite + retention" | `recipes/system-type-assessment/all-backups.md` (cloud-sync + retention sections) |
| "Single-firewall / EDR / endpoint deep dive after an incident" | Corresponding `recipes/single-system-analysis/by-inspector/<inspector>.md` |
| "Post-incident scope — who logged into the compromised box" | `recipes/single-system-analysis/by-inspector/windows-workstation.md` + identity ↔ device join from `reference/asset-fields.md` |
| "Phishing posture — KnowBe4 results + top clickers" | `recipes/single-system-analysis/by-inspector/knowbe4.md` |

## Read across to other personas

- **NOC** — when an EDR / firewall issue is operational (agent offline,
  inspector stale), hand off to NOC.
- **vCIO** — when a security finding warrants a customer conversation
  (e.g., $N privileged users without MFA → recommendation to invest in
  conditional access enforcement).
- **TAM** — when a posture gap is a configuration-standard issue (e.g.,
  default admin enabled across customers → TAM updates the build
  standard).

## What to customize first

1. **MFA / EDR coverage SLA percentages** — your contracts may be more
   permissive (95% MFA) or stricter (100% for admins).
2. **Compliance frameworks in scope** — start with cyber insurance
   (already shipped); add CMMC / HIPAA recipes when needed.
3. **Phishing test cadence + acceptable phish-prone %** — calibrate the
   KnowBe4 recipe's SLAs to your customer's industry / risk tolerance.
4. **Incident response playbook integration** — link recipes from your
   IR runbook so analysts can run them in one step.

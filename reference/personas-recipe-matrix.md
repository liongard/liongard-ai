# Persona × Recipe Matrix

Which recipes serve which personas. Read **two ways**:

- **By recipe** (Section 1) — pick a recipe; see which personas use it
  primarily (✅), secondarily (◉), or rarely/not (blank).
- **By persona** (Section 2) — pick a role; see the recipes that role
  uses, grouped by typical scenario.

Legend:

| Symbol | Meaning |
|---|---|
| ✅ | Primary user — the recipe was designed with this persona in mind |
| ◉ | Secondary user — uses the recipe occasionally or in specific scenarios |
| (blank) | Not typically used by this persona |

> **Note:** Every recipe can be tuned for any persona via the
> `audience.tone` knob in the customization block (`technical` /
> `balanced` / `executive`). The matrix below reflects **typical**
> usage, not the limit of what's possible.

---

## Section 1 — By recipe

### Single-system analysis (`recipes/single-system-analysis/by-inspector/`)

| Recipe | NOC | SOC | vCIO/AM | TAM | Sales | Exec | Acct/Fin |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `active-directory.md` | ✅ | ✅ | ✅ | ✅ | ◉ | ◉ | |
| `microsoft-365.md` | ◉ | ✅ | ✅ | ✅ | ◉ | ◉ | ✅ |
| `cisco-umbrella.md` | ✅ | ✅ | ✅ | ✅ | ◉ | | |
| `knowbe4.md` | | ✅ | ✅ | ✅ | ◉ | ◉ | ◉ |
| **EDR / AV** (`sentinelone`, `huntress`, `sophos-central`, `bitdefender-gravityzone`, `crowdstrike`, `webroot`, `eset-licensing`, `sonicwall-capture-client`) | ✅ | ✅ | ✅ | ✅ | ◉ | | ◉ |
| **Endpoint OS** (`windows-server`, `windows-workstation`, `linux`, `macos`) | ✅ | ◉ | ◉ | ✅ | ◉ | | |
| **Firewalls** (`sonicwall`, `fortinet-fortigate`, `cisco-asa`, `sophos-firewall`, `cisco-meraki`, `watchguard`, `palo-alto-panos`, `barracuda-firewall`, `pfsense`, `sophos-sg`) | ✅ | ✅ | ✅ | ✅ | ◉ | ◉ | ◉ |
| **Backup vendors** (`cove-data-protection`, `axcient-x360-recover`, `datto-bcdr`, `acronis-cyber-protect-cloud`, `veeam-availability-console`, `veeam-service-provider-console`, `storagecraft-spx`) | ✅ | ◉ | ✅ | ✅ | ◉ | | ◉ |
| `internet-domain-dns.md` | | ✅ | ✅ | ✅ | ✅ | ◉ | ◉ |
| `tls-ssl.md` | | ✅ | ✅ | ✅ | ✅ | ◉ | ◉ |
| `network-ip-address.md` | ◉ | ✅ | ◉ | ✅ | ✅ | | |
| `dark-web-monitoring.md` | | ✅ | ✅ | ✅ | ✅ | ✅ | |
| `duo-security.md` | | ✅ | | ✅ | | | |
| `jumpcloud.md` | ◉ | ✅ | ◉ | ✅ | | | ◉ |
| `onelogin.md` | | ✅ | ◉ | ✅ | | | ◉ |
| `ninjaone.md` | ✅ | | ◉ | ✅ | | | ✅ |
| `datto-rmm.md` | ✅ | | ◉ | ✅ | | | ✅ |
| `kaseya-vsa.md` | ✅ | ◉ | ◉ | ✅ | | | ✅ |
| `n-able-n-central.md` | ✅ | | ◉ | ✅ | | | ✅ |
| `connectwise-automate.md` | ✅ | | ◉ | ✅ | | | ✅ |
| `connectwise-manage.md` | ◉ | | ✅ | ◉ | | | ✅ |
| `autotask.md` | ◉ | | ✅ | ◉ | | | ✅ |
| `halopsa.md` | ◉ | | ✅ | ◉ | | | ✅ |
| `kaseya-bms.md` | ◉ | ◉ | ✅ | ◉ | | | ✅ |
| `syncro.md` | ✅ | ◉ | ✅ | ✅ | | | ✅ |
| `itglue.md` | ◉ | ◉ | ✅ | ✅ | | | ◉ |
| `box.md` | | ✅ | ✅ | ✅ | | ◉ | ✅ |
| `dropbox.md` | | ✅ | ✅ | ✅ | | ◉ | ✅ |
| `google-drive.md` | | ✅ | ✅ | ✅ | | ◉ | ✅ |
| `aws.md` | ◉ | ✅ | ✅ | ✅ | | ◉ | ✅ |
| `azure.md` | ◉ | ✅ | ✅ | ✅ | | ◉ | ✅ |
| `cloudflare.md` | | ✅ | ✅ | ✅ | ◉ | ◉ | ◉ |
| `google-workspace.md` | | ✅ | ✅ | ✅ | | | ✅ |
| `cisco-ios.md` | ✅ | ✅ | ✅ | ✅ | | | ◉ |
| `cisco-sbs-switch.md` | ✅ | | ✅ | ✅ | | | ◉ |
| `hp-procurve.md` | ✅ | | ✅ | ✅ | | | ◉ |
| `junos.md` | ✅ | ✅ | ✅ | ✅ | | | ◉ |
| `ubiquiti-unifi.md` | ✅ | ✅ | ✅ | ✅ | | | ◉ |
| `managed-printer.md` | ✅ | | ◉ | ✅ | | | ✅ |
| `slack.md` | | ✅ | ✅ | ✅ | | | |

### System-type assessment (`recipes/system-type-assessment/`)

| Recipe | NOC | SOC | vCIO/AM | TAM | Sales | Exec | Acct/Fin |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `all-edrs.md` | ✅ | ✅ | ✅ | ✅ | ✅ | ◉ | ◉ |
| `all-endpoints.md` | ✅ | ◉ | ✅ | ✅ | ✅ | ◉ | ✅ |
| `all-servers.md` | ✅ | ✅ | ✅ | ✅ | ◉ | ◉ | |
| `all-hypervisors.md` | ✅ | ◉ | ✅ | ✅ | ◉ | | ◉ |
| `all-firewalls.md` | ✅ | ✅ | ✅ | ✅ | ✅ | ◉ | ✅ |
| `all-backups.md` | ✅ | ✅ | ✅ | ✅ | ✅ | ◉ | ◉ |
| `all-domains.md` | ◉ | ✅ | ✅ | ✅ | ◉ | ◉ | ✅ |
| `all-windows-patching.md` | ✅ | ◉ | ✅ | ✅ | ◉ | | |
| `all-external-attack-surface.md` | ◉ | ✅ | ✅ | ✅ | ✅ | ✅ | |
| `all-identity-providers.md` | | ✅ | ✅ | ✅ | ◉ | ✅ | ✅ |
| `all-rmm-platforms.md` | ✅ | ◉ | ✅ | ✅ | | | ✅ |
| `all-psa-platforms.md` | ✅ | | ✅ | ◉ | | | ✅ |
| `all-cloud-storage.md` | | ✅ | ✅ | ✅ | | ✅ | ✅ |
| `all-network-infrastructure.md` | ✅ | ✅ | ✅ | ✅ | | ◉ | ✅ |
| `all-cloud-infrastructure.md` | | ✅ | ✅ | ✅ | ◉ | ◉ | ✅ |

### Compliance (`recipes/compliance/cyber-insurance/`)

| Recipe | NOC | SOC | vCIO/AM | TAM | Sales | Exec | Acct/Fin |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `cyber-insurance-readiness.md` | | ✅ | ✅ | ✅ | ✅ | ◉ | ◉ |
| `domains/auth.md` | | ✅ | ◉ | ✅ | | | |
| `domains/endpoint.md` | ◉ | ✅ | ◉ | ✅ | | | |
| `domains/backup.md` | ✅ | ✅ | ◉ | ◉ | | | |
| `domains/network.md` | ◉ | ✅ | ◉ | ✅ | | | |
| `domains/governance.md` | | ✅ | ✅ | ◉ | | ◉ | |
| `domains/regulatory.md` | | ✅ | ✅ | | | ◉ | |
| `domains/vendor.md` | | ✅ | ✅ | ◉ | | | |
| `carriers/travelers.md` | | ✅ | ✅ | ◉ | ✅ | ◉ | ◉ |

### Cross-cutting recipes (whole-environment workflows)

| Recipe | NOC | SOC | vCIO/AM | TAM | Sales | Exec | Acct/Fin |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `environment-quarterly-lookback/quarterly-business-review.md` | ◉ | ◉ | ✅ | ◉ | ◉ | ✅ | ◉ |
| `onboarding-assessment/new-customer-onboarding.md` | ◉ | ◉ | ✅ | ✅ | ◉ | ◉ | ◉ |
| `roadmap-planning/refresh-and-lifecycle-roadmap.md` | ◉ | | ✅ | ◉ | ◉ | ✅ | ✅ |
| `sales-assessment/pre-sales-discovery.md` | | ◉ | ✅ | ◉ | ✅ | ◉ | ◉ |
| `compliance/cmmc/cmmc-readiness.md` | | ✅ | ✅ | ◉ | ◉ | ◉ | |
| `compliance/hipaa/hipaa-readiness.md` | | ✅ | ✅ | ✅ | ◉ | ◉ | |
| `compliance/ftc-safeguards/ftc-safeguards-readiness.md` | | ✅ | ✅ | ✅ | ◉ | ✅ | ◉ |

### External data (`recipes/external-data/`)

| Recipe | NOC | SOC | vCIO/AM | TAM | Sales | Exec | Acct/Fin |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `email-security.md` | ◉ | ✅ | ✅ | ◉ | | ◉ | |
| `service-desk-tickets.md` | ✅ | | ✅ | ◉ | ◉ | ◉ | ✅ |
| `client-surveys-nps.md` | | | ✅ | | ◉ | ✅ | |

---

## Section 2 — By persona

### NOC
**Operational state — daily / weekly health checks.** See [`personas/noc/README.md`](../personas/noc/README.md).

| Scenario | Recipes |
|---|---|
| Daily fleet health dashboard | `all-edrs`, `all-firewalls`, `all-backups`, `all-windows-patching` |
| Single-system deep dive | Per-inspector single-system recipes |
| Hypervisor capacity check | `all-hypervisors` |
| Server-tier operational audit | `all-servers` + per-OS recipes |
| RMM agent / patch / alert posture across all RMMs | `all-rmm-platforms` (rollup) + per-vendor `ninjaone`, `datto-rmm`, `kaseya-vsa`, `n-able-n-central`, `connectwise-automate` |

### SOC
**Security posture — weekly / monthly + incident-driven.** See [`personas/soc/README.md`](../personas/soc/README.md).

| Scenario | Recipes |
|---|---|
| Cyber-insurance evidence | `compliance/cyber-insurance/cyber-insurance-readiness.md` + 7 domain files + carrier files |
| MFA / privileged audit | `all-identity-providers` (rollup) + per-IdP `microsoft-365`, `active-directory`, `jumpcloud`, `onelogin`, `duo-security` + the identity-related cyber-insurance domain files |
| EDR fleet posture | `all-edrs` + per-vendor singles |
| Firewall security posture | `all-firewalls` + per-vendor singles |
| Email-auth posture | `all-domains` + `internet-domain-dns` + `external-data/email-security` |
| External attack surface posture | `all-external-attack-surface` (combines `internet-domain-dns`, `tls-ssl`, `network-ip-address`, `dark-web-monitoring`) |
| Credential exposure / dark-web triage | `dark-web-monitoring` (cross-joined with the identity inventory) |
| Encryption-in-transit evidence | `tls-ssl` (single-host) or `all-external-attack-surface` (whole environment) |
| Ransomware preparedness | `all-backups` |
| Phishing posture | `knowbe4` |
| Post-incident scope | Per-system singles + identity↔device join (see `reference/asset-fields.md`) |

### vCIO / Account Manager
**Customer relationship — quarterly business reviews + renewals.** See [`personas/vcio-account-manager/README.md`](../personas/vcio-account-manager/README.md).

| Scenario | Recipes |
|---|---|
| Quarterly business review (PBR / QBR) | `environment-quarterly-lookback/quarterly-business-review.md` (chains the per-class rollups below) |
| Per-class rollups for PBR detail | `all-endpoints` → `all-edrs` → `all-firewalls` → `all-backups` → `all-servers` → `all-hypervisors` → `all-domains` → `microsoft-365` → `knowbe4` |
| New customer kickoff / engagement scoping | `onboarding-assessment/new-customer-onboarding.md` |
| Refresh roadmap | `all-endpoints` (Win11 readiness) + `all-servers` (lifecycle) |
| Renewal calendar | `all-firewalls` + `all-domains` + `microsoft-365` + per-vendor licensing recipes |
| Vendor consolidation | The 3 corresponding `all-*` rollups (firewalls / backups / EDRs) |
| Cyber-insurance pre-renewal | `compliance/cyber-insurance/cyber-insurance-readiness.md` |

### Technical Alignment Manager (TAM)
**Standards alignment — onboarding + quarterly drift.** See [`personas/technical-alignment-manager/README.md`](../personas/technical-alignment-manager/README.md).

| Scenario | Recipes |
|---|---|
| Onboarding intake (point-in-time gap analysis vs. MSP standard) | `onboarding-assessment/new-customer-onboarding.md` (auto-chains all per-class rollups + per-OS singles below) |
| Onboarding QA — supporting deep-dives | Per-OS singles + `all-servers` + `all-endpoints` + `all-firewalls` + `all-edrs` + `all-backups` + `active-directory` + `microsoft-365` + `all-hypervisors` + `all-domains` |
| Quarterly drift check | `environment-quarterly-lookback/quarterly-business-review.md` with tighter `qa.flag_count_divergence_threshold_pct` |
| Re-grading at the 1-year anniversary | Re-run `onboarding-assessment/new-customer-onboarding.md` to confirm customer has stayed at standard |
| Per-system deep-dive audit | Corresponding per-inspector single-system recipe |

### Sales
**Pre-sales discovery + renewal upsell.** See [`personas/sales/README.md`](../personas/sales/README.md).

| Scenario | Recipes |
|---|---|
| **Zero-credential external discovery (Phase 0 — always lead here)** | `all-external-attack-surface.md` (chains `internet-domain-dns`, `tls-ssl`, `network-ip-address`, `dark-web-monitoring`) |
| Pre-sales discovery deck (credentialed phase) | `all-endpoints`, `all-edrs`, `all-firewalls`, `all-backups`, `microsoft-365`, `active-directory`, `knowbe4`, plus `compliance/cyber-insurance/cyber-insurance-readiness` for prep |
| Renewal proposal | Same recipes with time-series sections to show growth |
| Upsell narrative | The corresponding `all-*` rollup for the practice being pitched |

### Executive
**Customer leadership — quarterly + on-demand.** See [`personas/executive/README.md`](../personas/executive/README.md).

The Executive persona uses the same recipes other personas use, with
`audience.tone: "executive"` set in the customization block. The most
common executive-facing recipes:

- Quarterly Business Review (the vCIO PBR sequence above)
- Cyber-insurance executive summary (`compliance/cyber-insurance/cyber-insurance-readiness`)
- Refresh roadmap (`all-endpoints` + `all-servers`)
- Renewal calendar (chained `all-*` license sections)
- Incident response summary (per-system singles, post-incident)

### Accounting / Finance
**Renewal calendars, license utilization, cost recovery.** See [`personas/accounting-finance/README.md`](../personas/accounting-finance/README.md).

| Scenario | Recipes |
|---|---|
| Firewall license renewals | `all-firewalls` (license expiration roadmap) |
| Domain renewals | `all-domains` (expiration roadmap) |
| M365 license utilization / renewals | `microsoft-365` (licensing) |
| Per-vendor backup / EDR renewals | Per-vendor singles |
| Cost-recovery (orphaned licenses, disabled-user M365) | `microsoft-365`, `all-backups` (orphaned protection), `all-edrs` (vendor sprawl) |
| Hardware refresh budget | `all-endpoints` + `all-servers` (lifecycle) |
| Ticket volume per user (denominator for capacity planning) | `external-data/service-desk-tickets` |

---

## Maintenance

When a new recipe ships:

1. Add the row to **Section 1** with primary / secondary persona markings.
2. Add the recipe to the matching scenario row in **Section 2**.
3. If the recipe introduces a new persona-relevant scenario, add a row
   to the relevant persona's scenarios table.
4. Update the corresponding persona's `README.md` in `personas/<role>/`
   to surface the recipe in that role's index.

When a persona's recipe usage materially shifts:

1. Update Section 1 markings.
2. Update the persona's `README.md` index.
3. Note the change in `learnings.md` if the shift represents a new
   pattern (e.g., a new role emerges that consolidates two existing
   personas).

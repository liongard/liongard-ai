# metrics-system-type-all-firewalls-barracuda-firewall - Metric reference (barracuda-firewall-inspector)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Required metric primitives for the recipe `system-type-all-firewalls` (System-Type Assessment — All Firewalls), inspector `barracuda-firewall-inspector` (ID 52). 9 primitives, sequence ids P001-P009. For every system of this inspector, evaluate EVERY primitive below with `liongard_metric EVALUATE` (`jmesPathQuery`, `systemId`, `environmentId`), retry a null or error once, and log one row per primitive per system. Respect each gotcha.

- **`metrics:barracuda-firewall:application-control-enabled`** [P001] - Barracuda Firewall — Application Control License Status. Whether the Application Control security service is enabled on the appliance.
  - metricId: none (use query) | query: `SecuritySubscriptions[?name EQ_OP 'AppID'].status | [0]` | result: string
  - compliant when: result EQ_OP true
  - gotcha: Licence status, not an on/off flag; application control is applied per firewall rule.
  - status: VALIDATED
- **`metrics:barracuda-firewall:atp-enabled`** [P002] - Barracuda Firewall — ATP License Status. Whether the Advanced Threat Protection (ATP) service is enabled on the appliance.
  - metricId: none (use query) | query: `SecuritySubscriptions[?name EQ_OP 'ATD'].status | [0]` | result: string
  - compliant when: result EQ_OP true
  - gotcha: Licence status (e.g. "Licensed"), not an on/off flag; ATP is applied per firewall rule.
  - status: VALIDATED
- **`metrics:barracuda-firewall:energize-updates-days-until-expiration`** [P003] - Barracuda Firewall — Energize Updates Days Until Expiration. Days remaining until Energize Updates subscription expires. Subscription feeds IPS, AV, and URL filter signatures — expiry stops all signature updates.
  - metricId: none (use query) | query: `Licenses[?module EQ_OP 'Energize-Updates'].daysTillExpiration | [0]` | result: integer
  - compliant when: result > 60
  - status: VALIDATED
- **`metrics:barracuda-firewall:firmware-version`** [P004] - Barracuda Firewall — Firmware Version. Current firmware version installed on the Barracuda CloudGen Firewall appliance.
  - metricId: none (use query) | query: `SystemInfo.release` | result: string
  - status: VALIDATED
- **`metrics:barracuda-firewall:ips-enabled`** [P005] - Barracuda Firewall — IPS Enabled. Whether the Intrusion Prevention System (IPS) security service is enabled on the appliance.
  - metricId: none (use query) | query: `IPS.enable` | result: boolean
  - compliant when: result EQ_OP true
  - gotcha: Also check IPS.reportOnly: true means detect-only (a finding).
  - status: VALIDATED
- **`metrics:barracuda-firewall:local-users-total-count`** [P006] - Barracuda Firewall — Admin Account Count. Total number of local user accounts configured on the appliance.
  - metricId: none (use query) | query: `length(Admins)` | result: integer
  - gotcha: Only administrator accounts are in the dataprint.
  - status: VALIDATED
- **`metrics:barracuda-firewall:rules-open-any-to-any-count`** [P007] - Barracuda Firewall — Open Any-to-Any Access Rules Count. Count of access rules permitting any source to any destination — critical finding requiring immediate restriction.
  - metricId: none (use query) | query: `length(FirewallRules[?source.references EQ_OP 'Any' AND_OP destination.references EQ_OP 'Any' AND_OP action.type!='block' AND_OP action.type!='deny' AND_OP !deactivated])` | result: integer
  - compliant when: result EQ_OP 0
  - gotcha: Action values observed: block, pass. Filter confirmed; no positive case observed yet.
  - status: VALIDATED
- **`metrics:barracuda-firewall:system-model`** [P008] - Barracuda Firewall — System Model. Hardware model of the Barracuda CloudGen Firewall appliance.
  - metricId: none (use query) | query: `SystemInfo.appliance` | result: string
  - gotcha: SystemInfo.model gives the lowercase form.
  - status: VALIDATED
- **`metrics:barracuda-firewall:wan-management-allowed`** [P009] - Barracuda Firewall — Admins With Unrestricted Source IP. Whether management access is permitted from the WAN interface — must be false per MSP baseline.
  - metricId: none (use query) | query: `length(Admins[?contains(peerIpRestriction, '0.0.0.0/0')])` | result: integer
  - compliant when: result EQ_OP false
  - gotcha: No WAN-management flag exists; counts admin accounts allowed to log in from any source IP.
  - status: VALIDATED

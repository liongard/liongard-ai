# metrics-system-type-all-firewalls-sophos-firewall - Metric reference (sophos-firewall-inspector)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Required metric primitives for the recipe `system-type-all-firewalls` (System-Type Assessment — All Firewalls), inspector `sophos-firewall-inspector` (ID 28). 7 primitives, sequence ids P102-P108. For every system of this inspector, evaluate EVERY primitive below with `liongard_metric EVALUATE` (`jmesPathQuery`, `systemId`, `environmentId`), retry a null or error once, and log one row per primitive per system. Respect each gotcha.

- **`metrics:sophos-firewall:active-user-list`** [P102] - Sophos Firewall — Active User List. Returns the names of all currently active users on the Sophos XG/XGS firewall
  - metricId: 220 | query: `` User[?Status EQ_OP `Active`].Name | join(`, `, @) `` | result: string
  - status: VALIDATED
- **`metrics:sophos-firewall:device-dns-summary`** [P103] - Sophos Firewall — Device DNS Summary. Returns the DNS IPv4 summary configuration for the Sophos XG/XGS firewall
  - metricId: 584 | query: `SystemInfo.DNS_IPv4_Summary` | result: string
  - status: VALIDATED
- **`metrics:sophos-firewall:interfaces-count`** [P104] - Sophos Firewall — Interfaces Count. Total number of interfaces configured on the Sophos XG/XGS firewall
  - metricId: 221 | query: `SystemInfo.InterfacesCount` | result: integer
  - status: VALIDATED
- **`metrics:sophos-firewall:security-policy-summary`** [P105] - Sophos Firewall — Security Policy Summary. Returns name and ordering details for all security policies on the Sophos XG/XGS firewall
  - metricId: 583 | query: `` SecurityPolicy[].join( ` ', ' `, [join(`: `, [`Name`,to_string(Name)]), join(`: `, [`After`, to_string(After.Name)])]) `` | result: array
  - status: VALIDATED
- **`metrics:sophos-firewall:user-group-summary`** [P106] - Sophos Firewall — User Group Summary. Returns name and type details for all user groups configured on the Sophos XG/XGS firewall
  - metricId: 585 | query: `` UserGroup.GroupDetail[].join( ` ', ' `, [join(`: `, [`Name`, to_string(Name)]), join(`: `, [`Type`, to_string(GroupType)])]) `` | result: array
  - status: VALIDATED
- **`metrics:sophos-firewall:user-summary`** [P107] - Sophos Firewall — Active User Summary. Returns name, status, and group membership for all active users on the Sophos XG/XGS firewall
  - metricId: 582 | query: `` User[?Status EQ_OP `Active`].join( ` ', ' `, [join(`: `, [`Name`, to_string(Name)]), join(`: `, [`Status`, to_string(Status)])]) `` | result: array
  - status: VALIDATED
- **`metrics:sophos-firewall:zone-summary`** [P108] - Sophos Firewall — Zone Summary. Returns name, type, and SSH/HTTPS management flags for all security zones on the Sophos XG/XGS firewall
  - metricId: 586 | query: `` Zone[].join( `, `, [join(`: `, [`Name`, to_string(Name)]), join(`: `, [`Type`, to_string(Type)]), join(`: `, [`SSH`, to_string(SSH)])]) `` | result: array
  - status: VALIDATED

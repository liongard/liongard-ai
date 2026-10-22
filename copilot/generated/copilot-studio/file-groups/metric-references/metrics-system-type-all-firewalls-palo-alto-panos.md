# metrics-system-type-all-firewalls-palo-alto-panos - Metric reference (palo-alto-panos-inspector)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Required metric primitives for the recipe `system-type-all-firewalls` (System-Type Assessment — All Firewalls), inspector `palo-alto-panos-inspector` (ID 49). 11 primitives, sequence ids P047-P057. For every system of this inspector, evaluate EVERY primitive below with `liongard_metric EVALUATE` (`jmesPathQuery`, `systemId`, `environmentId`), retry a null or error once, and log one row per primitive per system. Respect each gotcha.

- **`metrics:palo-alto-panos:certificate-expiration`** [P047] - Palo Alto PAN-OS — Certificate Expiration Summary. Formatted list of shared certificates with common name and not-valid-after date. Used to flag certificates approaching expiration.
  - metricId: 76072 | query: `` Configuration.shared.certificate[].join(`, `, [join(`: `, ['Name', "common-name"]), join(`: `, ['Expiration Date', "not-valid-after"])]) `` | result: array
  - status: VALIDATED
- **`metrics:palo-alto-panos:check-device-resources`** [P048] - Palo Alto PAN-OS — Device Resource Utilization (CPU & Memory). Formatted summary of CPU and memory utilization percentages from SystemResources. Used for capacity and performance monitoring.
  - metricId: 76075 | query: `` SystemResources.join(`, `, [join(`: `, ['CPU Utilization', to_string(CPU.UsagePercentage)]), join(`: `, ['Memory Utilization', to_string(Memory.UsagePercentage)])]) `` | result: object
  - status: VALIDATED
- **`metrics:palo-alto-panos:config-changes-pending`** [P049] - Palo Alto PAN-OS — Configuration Changes Pending. Whether uncommitted configuration changes exist from Configuration.pending-changes-exist. Pending changes mean the running config does not match the candidate config — critical for audits.
  - metricId: 76069 | query: `Configuration."pending-changes-exist"` | result: boolean
  - compliant when: result EQ_OP false
  - gotcha: Key is hyphenated — JMESPath requires quoting: Configuration."pending-changes-exist".
  - status: VALIDATED
- **`metrics:palo-alto-panos:device-admins`** [P050] - Palo Alto PAN-OS — Device Administrator List. Array of admin usernames from AdminUsers[].admin. Use to audit for the default 'admin' account and excess privileged users.
  - metricId: 76070 | query: `AdminUsers[].admin` | result: array
  - status: VALIDATED
- **`metrics:palo-alto-panos:dhcp-expiration`** [P051] - Palo Alto PAN-OS — DHCP Lease Expiration Summary. Formatted list of DHCP leases with IP and lease-end timestamp from Interfaces[].dhcp.lease.leases[].
  - metricId: 76074 | query: `` Interfaces[].dhcp.lease.leases[?"lease-end"].join(`, `, [join(`: `, ['IP', "ip"]), join(`: `, ['Lease End', "lease-end"])])[] `` | result: array
  - status: VALIDATED
- **`metrics:palo-alto-panos:dhcp-lease-monitoring`** [P052] - Palo Alto PAN-OS — DHCP Active Lease Count. Count of active DHCP leases across all interfaces from length(Interfaces[].dhcp.lease.leases[]). Provides scope for DHCP server load.
  - metricId: 76073 | query: `length(Interfaces[].dhcp.lease.leases[])` | result: integer (count)
  - status: VALIDATED
- **`metrics:palo-alto-panos:expired-device-certificates`** [P053] - Palo Alto PAN-OS — Expired Device Certificates (Boolean). Returns true if any system certificates are past their expiration date. Uses time_until() to check days remaining < 0.
  - metricId: 76071 | query: `SystemInfo.certificates.info[?time_until(expirationDate, 'days') < '0'] | length(@) > '0'` | result: boolean
  - compliant when: result EQ_OP false
  - status: VALIDATED
- **`metrics:palo-alto-panos:interface-packets-received`** [P054] - Palo Alto PAN-OS — Interface Packets Received Summary. Formatted summary of received packet counts per interface. Used for traffic load and capacity review.
  - metricId: 76077 | query: `` Interfaces[].join(`, `, [join(`: `, ['Interface', name]), join(`: `, ['Received Packets', to_string(status."received-packets")])]) `` | result: array
  - status: VALIDATED
- **`metrics:palo-alto-panos:interface-packets-transmitted`** [P055] - Palo Alto PAN-OS — Interface Packets Transmitted Summary. Formatted summary of transmitted packet counts per interface. Used for traffic load and capacity review.
  - metricId: 76078 | query: `` Interfaces[].join(`, `, [join(`: `, ['Interface', name]), join(`: `, ['Transmitted Packets', to_string(status."transmitted-packets")])]) `` | result: array
  - status: VALIDATED
- **`metrics:palo-alto-panos:policy-based-forwarding-ips`** [P056] - Palo Alto PAN-OS — Policy Based Forwarding IP Addresses. Formatted list of policy-based forwarding (PBF) rules with rule name and forwarding nexthop IP across all applicable interfaces.
  - metricId: 76076 | query: `` Interfaces[?pbfRules[].nexthop].pbfRules[].join(`, `, [join(`: `, ['Rule', "name"]), join(`: `, ['Forwarding IP', nexthop])]) `` | result: array
  - status: VALIDATED
- **`metrics:palo-alto-panos:software-version`** [P057] - Palo Alto PAN-OS — Software Version. Running PAN-OS version string from SystemInfo.sw-version. Used for firmware currency checks and CVE cross-reference. Key field for lifecycle review.
  - metricId: 76068 | query: `SystemInfo."sw-version"` | result: string
  - gotcha: The key is hyphenated — JMESPath requires quoting: SystemInfo."sw-version". Without quotes the hyphen is interpreted as subtraction and the query returns null.
  - status: VALIDATED

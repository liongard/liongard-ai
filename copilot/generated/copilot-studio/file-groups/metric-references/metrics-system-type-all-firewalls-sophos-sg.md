# metrics-system-type-all-firewalls-sophos-sg - Metric reference (sophos-sg-inspector)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Required metric primitives for the recipe `system-type-all-firewalls` (System-Type Assessment — All Firewalls), inspector `sophos-sg-inspector` (ID 43). 15 primitives, sequence ids P109-P123. For every system of this inspector, evaluate EVERY primitive below with `liongard_metric EVALUATE` (`jmesPathQuery`, `systemId`, `environmentId`), retry a null or error once, and log one row per primitive per system. Respect each gotcha.

- **`metrics:sophos-sg:count-of-active-users`** [P109] - Sophos SG — Count of Active Users. Total number of enabled (active) users configured on the Sophos SG appliance
  - metricId: 1397 | query: `` Users[?enabled EQ_OP `true`] | length(@) `` | result: integer
  - status: VALIDATED
- **`metrics:sophos-sg:count-of-groups`** [P110] - Sophos SG — Count of Groups. Total number of groups configured on the Sophos SG appliance
  - metricId: 1388 | query: `Groups[] | length(@)` | result: integer
  - status: VALIDATED
- **`metrics:sophos-sg:interface-summary`** [P111] - Sophos SG — Interface Summary. Returns name, type, IP address, link state, and MTU for all interfaces on the Sophos SG appliance
  - metricId: 1162 | query: `` Interfaces[].[`Name:` name , `| Type:` InterfaceType_r ,`| Address:`primary_address `| Link:` link, `| MTU:` mtu] `` | result: array
  - status: VALIDATED
- **`metrics:sophos-sg:licenses-expiring-30-days-count`** [P112] - Sophos SG — Licenses Within 30 Days of Expiration Count. Total number of Sophos SG licenses expiring within the next 30 days
  - metricId: 1387 | query: `` SystemInfo.Licensing[?DaysUntilExpiration_r < `30`] | length(@) `` | result: integer
  - status: VALIDATED
- **`metrics:sophos-sg:licenses-expiring-30-days-list`** [P113] - Sophos SG — Licenses Within 30 Days of Expiration List. Returns the names of Sophos SG licenses expiring within the next 30 days
  - metricId: 1396 | query: `` SystemInfo.Licensing[?DaysUntilExpiration_r < `30`].name `` | result: array
  - status: VALIDATED
- **`metrics:sophos-sg:list-of-active-users`** [P114] - Sophos SG — List of Active Users. Returns the names of all enabled (active) users configured on the Sophos SG appliance
  - metricId: 1159 | query: `` Users[?enabled EQ_OP `true`].name `` | result: array
  - status: VALIDATED
- **`metrics:sophos-sg:list-of-groups`** [P115] - Sophos SG — List of Groups. Returns name, dynamic flag, and network for all groups configured on the Sophos SG appliance
  - metricId: 1161 | query: `` Groups[].[`Name:`,name,`| Dynamic:` dynamic, `| Network:` network] `` | result: array
  - status: VALIDATED
- **`metrics:sophos-sg:list-of-network-definitions`** [P116] - Sophos SG — List of Network Definitions. Returns name and address for all network definition objects on the Sophos SG appliance
  - metricId: 1386 | query: `` NetworkDefinitions[].[`Name:`name, `| Address:`address] `` | result: array
  - status: VALIDATED
- **`metrics:sophos-sg:nat-rules`** [P117] - Sophos SG — NAT Rules. Returns name, source, service, and destination for all active NAT rules on the Sophos SG appliance
  - metricId: 496 | query: `` NAT[?status EQ_OP `true`].[name, `| Src: `, source.name, `| Svc: `, service.name, `| Dest: `, destination.name] `` | result: array
  - status: VALIDATED
- **`metrics:sophos-sg:packet-filter-rules-summary`** [P118] - Sophos SG — Packet Filter Rules Summary. Returns name, action, direction, and status for all packet filter rules on the Sophos SG appliance
  - metricId: 1163 | query: `` PacketFilter[].[`Name:`name,`| Action:`action,`| Direction:`direction, `| Status:` status] `` | result: array
  - status: VALIDATED
- **`metrics:sophos-sg:remote-access-profiles-summary`** [P119] - Sophos SG — Remote Access Profiles Summary. Returns name, status, and assigned networks for all SSL remote access profiles on the Sophos SG appliance
  - metricId: 1167 | query: `` SSLRemoteAccessProfile[].[`Name:`name, `| Status:`status, `| Networks:` to_string(networks_r)] `` | result: array
  - status: VALIDATED
- **`metrics:sophos-sg:remote-gateways-summary`** [P120] - Sophos SG — Remote Gateways Summary. Returns name, authentication method, host, and Xauth flag for all IPsec remote gateways on the Sophos SG appliance
  - metricId: 1165 | query: `` IpsecRemoteGateway[].[`Name:`name, `| Auth:`authentication, `| Host:` host, `| Xauth:`xauth] `` | result: array
  - status: VALIDATED
- **`metrics:sophos-sg:site-to-site-vpn-summary`** [P121] - Sophos SG — Site-to-Site VPN Connections Summary. Returns name, status, interface, and remote gateway for all site-to-site VPN connections on the Sophos SG appliance
  - metricId: 1164 | query: `` SiteToSiteVPN[].[`Name:`name, `| Status:`status, `| Interface:`interface, `| Remote Gateway:`remote_gateway] `` | result: array
  - status: VALIDATED
- **`metrics:sophos-sg:ssh-enabled`** [P122] - Sophos SG — SSH Enabled. Indicates whether SSH access is enabled on the Sophos SG appliance
  - metricId: 1157 | query: `SystemInfo.SSHAccessEnabled` | result: boolean
  - status: VALIDATED
- **`metrics:sophos-sg:utm-version`** [P123] - Sophos SG — UTM Version. Returns the current UTM firmware version of the Sophos SG appliance
  - metricId: 1156 | query: `SystemInfo.UTMVersion` | result: string
  - status: VALIDATED

# Single-System Analysis — Fortinet FortiGate (Run Card part 2)

Recipe `single-system-fortinet-fortigate` run card part 2: continuation of `single-system-fortinet-fortigate run card` with metrics P001-P006. Run each line exactly as step 4 of the main run card says.

### single-system-fortinet-fortigate metrics P001-P006

- **P001** metricId 630 - Access Profiles Summary (array)
  - fallback query: `` UserProfiles[].join( `, `, [join(`: `, [`Name`, to_string(name)]), join(`: `, [`Scope`,to_string(scope)]) , join(`: `, [`Network Config`,to_string(netgrp)]) , join(`: `, [`System Config`,to_string(sysgrp)]) , join(`: `, [`Security Profiles`,to_string(utmgrp)]), join(`: `, [`IPsec,SSL,PPTP,L2TP VPN`,to_string(vpngrp)])]) ``
- **P002** metricId 222 - DNS Servers (string)
  - fallback query: `` DNS.["primary","secondary"] | join(`, `, @) ``
- **P003** metricId 106514 - Firewall Policy Summary (Structured) (array)
  - fallback query: `FirewallPolicy[].[name, srcintf[].name, dstintf[].name, srcaddr[].name, dstaddr[].name, service[].name, comments]`
- **P004** metricId 631 - Firewall Policy Summary (Rich) (array)
  - fallback query: `` FirewallPolicy[].join( `, `, [join(`: `, [`Name`, to_string(name)]) , join(`: `, [`NAT`,to_string(nat)]), join(`: `, [`Action`,to_string(action)]), join(`: `, [`Status`,to_string(status)]), join(`: `, [`Source Address`,to_string(sort(srcaddr[].name))]), join(`: `, [`Source Interface`,to_string(sort(srcintf[].name))]), join(`: `, [`Service`,to_string(sort(service[].name))])]) ``
- **P005** metricId 632 - Firewall VIP Summary (array)
  - fallback query: `` FirewallVIP[].join( `, `, [join(`: `, [`Name`, to_string(name)]), join(`: `, [`Type`, to_string(type)]), join(`: `, [`External IP`, to_string(extip)]), join(`: `, [`External Interface`, to_string(extintf)]), join(`: `, [`External Port`, to_string(extport)]), join(`: `, [`Mapped IP Range`, to_string(sort(mappedip[].range))]) , join(`: `, [`Mapped Port`, to_string(mappedport)])]) | sort(@) ``
- **P006** metricId 224 - Firmware Version (string) - Quoted key required in JMESPath because 'version' is a reserved word in some JMESPath implementations. Use Firmware.current."version" not Firmware.current.versi...
  - fallback query: `Firmware.current."version"`

# Single-System Analysis — Fortinet FortiGate (Run Card part 3)

Recipe `single-system-fortinet-fortigate` run card part 3: continuation of `single-system-fortinet-fortigate run card` with metrics P007-P012. Run each line exactly as step 4 of the main run card says.

### single-system-fortinet-fortigate metrics P007-P012

- **P007** metricId 106544 - FortiEMS Cloud Status (object)
  - fallback query: `{Name: Name, Status: Licensing.fortiems_cloud.status}`
- **P008** metricId 628 - Group Summary (array)
  - fallback query: `` Groups[].join( `, `, [join(`: `, [`Name`,to_string(name)]), join(`: `, [`Email`,to_string(email)]), join(`: `, [`Member`,to_string(sort(member[].name))]), join(`: `, [`Group Type`,to_string("group-type")])]) | sort(@) ``
- **P009** metricId 626 - Hostname (string)
  - fallback query: `SystemGlobal.hostname`
- **P010** metricId 629 - Interface Summary (array)
  - fallback query: `` Interfaces[].join( `, `, [join(`: `, [`Name`, to_string(name)]), join(`: `, [`Vdom`,to_string(vdom)]), join(`: `, [`Type`,to_string(type)]), join(`: `, [`IP & Subnet`,to_string(ip)]), join(`: `, [`Role`,to_string(role)]), join(`: `, [`VLAN ID`,to_string(vlanid)])]) | sort(@) ``
- **P011** metricId 223 - Model Number (string) - Two paths exist for model/version info. id=223 uses Firmware.current."platform-id" (the Fortinet API path). id=521 uses SystemInfo.Firmware.Version for the firm...
  - fallback query: `Firmware.current."platform-id"`
- **P012** metricId 633 - Routing Policy Summary (array)
  - fallback query: `` IPV4Routing[].join( `, `, [join(`: `, [`Type`, to_string(type)]), join(`: `, [`Gateway`, to_string(gateway)]), join(`: `, [`IP Mask`, to_string(ip_mask)]), join(`: `, [`Interface`, to_string(interface)])]) | sort(@) ``

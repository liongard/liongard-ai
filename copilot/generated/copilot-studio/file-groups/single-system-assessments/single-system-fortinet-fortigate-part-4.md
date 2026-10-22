# Single-System Analysis — Fortinet FortiGate (Run Card part 4)

Recipe `single-system-fortinet-fortigate` run card part 4: continuation of `single-system-fortinet-fortigate run card` with metrics P013-P013. Run each line exactly as step 4 of the main run card says.

### single-system-fortinet-fortigate metrics P013-P013

- **P013** metricId 627 - User Summary (array) - Users[] contains local VPN/firewall auth accounts only — NOT admin accounts. FortiGate admin accounts (System > Administrators) are NOT present in the dataprint...
  - fallback query: `` Users[].join( `, `, [join(`: `, [`Name`, to_string(name)]), join(`: `, [`Vdom Name`,to_string(sort(vdom[].name))]), join(`: `, [`Type`,to_string(type_r)]), join(`: `, [`Profile`,to_string(accprofile)])]) | sort(@) ``

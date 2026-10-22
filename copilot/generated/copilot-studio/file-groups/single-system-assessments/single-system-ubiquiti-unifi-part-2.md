# Single-System Analysis — Ubiquiti UniFi (Run Card part 2)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Recipe `single-system-ubiquiti-unifi` run card part 2: continuation of `single-system-ubiquiti-unifi run card` with metrics P001-P006. Run each line exactly as step 4 of the main run card says.

### single-system-ubiquiti-unifi metrics P001-P006

- **P001** metricId 1643 - Controller Version (array)
  - fallback query: `SystemInfo[].version`
- **P002** metricId 524 - Device Serial Number List (array)
  - fallback query: `Devices[].serial | sort(@)`
- **P003** metricId 233 - Devices List (array)
  - fallback query: `` Devices[?name AND_OP model].join(`:` , [name,model]) ``
- **P004** metricId 1644 - Hardware Type and Version (array)
  - fallback query: `` Devices[].join(`: `, [name,type,model,version]) ``
- **P005** metricId 232 - Subnets List (array)
  - fallback query: `` NetworkConf[?ip_subnet AND_OP name].join(`:` , [name, ip_subnet]) ``
- **P006** metricId 234 - Super Admin Users List (string)
  - fallback query: `` Users[?is_super EQ_OP `true`].name | join(`, `, @) ``

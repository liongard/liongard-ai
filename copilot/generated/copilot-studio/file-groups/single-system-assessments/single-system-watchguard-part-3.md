# Single-System Analysis — WatchGuard (Run Card part 3)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Recipe `single-system-watchguard` run card part 3: continuation of `single-system-watchguard run card` with metrics P007-P012. Run each line exactly as step 4 of the main run card says.

### single-system-watchguard metrics P007-P012

- **P007** metricId 596 - Dynamic NAT Summary (array)
  - fallback query: `` NAT.dynamicNAT[].join( `, `, [join(`: `, [`To`, to_string(To)]), join(`: `, [`From`, to_string(From)]), join(`: `, [`Source IP`, to_string(SourceIP)])]) | sort(@) ``
- **P008** metricId 889 - Features Expiring Within 30 Days Count (integer) - OK when result EQ_OP 0 ; DaysUntilExpiration_r is a resolved/computed string field — filter uses string comparison '<= 30' not numeric. Confirm behavior when value is exactly 30.
  - fallback query: `Features[?DaysUntilExpiration_r <= '30'] | length(@)`
- **P009** metricId 888 - Features Expiring Within 30 Days List (array) - OK when result EQ_OP []
  - fallback query: `Features[?DaysUntilExpiration_r <= '30'].[Feature,Expiration]`
- **P010** metricId 318 - Firmware Version (Fireware OS) (string)
  - fallback query: `SystemInfo.Version`
- **P011** metricId 605 - Group Account Summary (array)
  - fallback query: `` Users[?Type EQ_OP 'Group'].join( `, `, [join(`: `, [`Name`, to_string(Name)]), join(`: `, [`AuthServer`, to_string(AuthServer)]), join(`: `, [`Description`, to_string(Description)])]) | sort(@) ``
- **P012** metricId 1999 - Hostname (System Name) (string)
  - fallback query: `SystemInfo.SystemName`

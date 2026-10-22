# Single-System Analysis — WatchGuard (Run Card part 2)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Recipe `single-system-watchguard` run card part 2: continuation of `single-system-watchguard run card` with metrics P001-P006. Run each line exactly as step 4 of the main run card says.

### single-system-watchguard metrics P001-P006

- **P001** metricId 601 - Access Rule Summary (array)
  - fallback query: `` AccessRules[].join( `, `, [join(`: `, [`Name`, to_string(Name)]), join(`: `, [`Enabled`, to_string(Enabled)]), join(`: `, [`Action`, to_string(ConnectionsAre)]), join(`: `, [`Service`, to_string(Service)]), join(`: `, [`From`, to_string(FromAliasList)]), join(`: `, [`To`, to_string(ToAliasList)]), join(`: `, [`Static NAT`, to_string(StaticNat)]), join(`: `, [`Global NAT`, to_string(GlobalDnat)]) , join(`: `, [`Global 1:1 Nat`, to_string(Global_1to1Nat)])]) | sort(@) ``
- **P002** metricId 885 - Account Lockout Disabled Count (integer) - OK when result EQ_OP 0
  - fallback query: `SystemInfo.AccountLockoutSettings[?Status != 'Enabled'] |length(@)`
- **P003** metricId 884 - Account Lockout Enabled Status List (array)
  - fallback query: `SystemInfo.AccountLockoutSettings[?Status EQ_OP 'Enabled'].[Status][]`
- **P004** metricId 603 - Alias Summary (array)
  - fallback query: `` Aliases[].join( `, `, [join(`: `, [`Name`, to_string("Alias Name")]), join(`: `, [`Description`, to_string(Description)]), join(`: `, [`Members`, to_string(AliasMembersList_r)])]) | sort(@) ``
- **P005** metricId 883 - Down Interfaces Count (integer) - OK when result EQ_OP 0
  - fallback query: `Interfaces[?Enabled EQ_OP 'yes' AND_OP Status != 'Up'] | length(@)`
- **P006** metricId 882 - Down Interfaces List (array) - OK when result EQ_OP []
  - fallback query: `Interfaces[?Enabled EQ_OP 'yes' AND_OP Status != 'Up'].[Name, Status]`

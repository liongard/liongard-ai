# Single-System Analysis — WatchGuard (Run Card part 4)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Recipe `single-system-watchguard` run card part 4: continuation of `single-system-watchguard run card` with metrics P013-P018. Run each line exactly as step 4 of the main run card says.

### single-system-watchguard metrics P013-P018

- **P013** metricId 598 - Interface Summary (array)
  - fallback query: `` Interfaces[].join( `, `, [join(`: `, [`Name`, to_string(Name)]), join(`: `, [`Enabled`, to_string(Enabled)]), join(`: `, [`Type`, to_string(Type)]), join(`: `, [`Address`, to_string(Address)]), join(`: `, [`IP Type`, to_string(IPNodeType)]), join(`: `, [`IP Assignment`, to_string(IPAssignment)])]) | sort(@) ``
- **P014** metricId 319 - Licensed Interface Count (integer)
  - fallback query: `SystemInfo.LicensedInterface`
- **P015** metricId 606 - Management IP Address (string)
  - fallback query: `SystemInfo.ManagementIP`
- **P016** metricId 602 - Management User Summary (array)
  - fallback query: `` DeviceMgmtUsers[].join( `, `, [join(`: `, [`Username`, to_string(Username)]), join(`: `, [`Role`, to_string(Role)]), join(`: `, [`AuthServer`, to_string(AuthServer)])]) | sort(@) ``
- **P017** metricId 887 - Management Users Locked Out Count (integer) - OK when result EQ_OP 0
  - fallback query: `DeviceMgmtUsers[?LockedOutStatus !='No lockout'] | length(@)`
- **P018** metricId 886 - Management Users Locked Out List (array) - OK when result EQ_OP []
  - fallback query: `DeviceMgmtUsers[?LockedOutStatus !='No lockout'].[Username]`

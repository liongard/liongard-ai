# Single-System Analysis — Microsoft 365 (Run Card part 2)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Recipe `single-system-microsoft-365` run card part 2: continuation of `single-system-microsoft-365 run card` with metrics P001-P006. Run each line exactly as step 4 of the main run card says.

### single-system-microsoft-365 metrics P001-P006

- **P001** metricId 1786 - Active Users Count (integer)
  - fallback query: `` length(Users[?accountEnabled EQ_OP `true`]) ``
- **P002** metricId 683 - Admin Users with MFA Disabled Count (integer) - OK when result EQ_OP 0
  - fallback query: `` subtract(length(Users[?Privileged EQ_OP `Yes`]), length(Users[?Privileged EQ_OP `Yes` AND_OP mfaDetails.enforced EQ_OP `true`])) ``
- **P003** metricId 6 - Associated Domains (string)
  - fallback query: `` Domains[*].id | join(`, `, @) ``
- **P004** metricId 979 - Conditional Access Policies (Enabled List) (array)
  - fallback query: `` Policies.ConditionalAccess[?state EQ_OP `enabled`].displayName ``
- **P005** metricId 529 - Directory Sync Enabled (boolean) - OK when result EQ_OP true when hybrid environment expected; result EQ_OP false for cloud-only tenants
  - fallback query: `SystemInfo.DirectorySync[].DirectorySyncEnabled | [0]`
- **P006** metricId 1790 - Directory Sync Stale (>=24h) Count (integer) - OK when result EQ_OP 0
  - fallback query: `` SystemInfo.DirectorySync[?DirectorySyncEnabled EQ_OP `true` AND_OP HoursSinceLastSync_r >= `24`] | length(@) ``

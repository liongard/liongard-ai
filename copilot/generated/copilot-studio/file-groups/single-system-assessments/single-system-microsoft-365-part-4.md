# Single-System Analysis — Microsoft 365 (Run Card part 4)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Recipe `single-system-microsoft-365` run card part 4: continuation of `single-system-microsoft-365 run card` with metrics P013-P018. Run each line exactly as step 4 of the main run card says.

### single-system-microsoft-365 metrics P013-P018

- **P013** metricId 763 - Non-Admin Users with MFA Disabled Count (integer) - OK when result EQ_OP 0
  - fallback query: `` subtract(length(Users[?Privileged != `Yes`]), length(Users[?Privileged != `Yes` AND_OP mfaDetails.enforced EQ_OP `true`])) ``
- **P014** metricId 20 - Privileged Users Count (integer)
  - fallback query: `` Users[?Privileged EQ_OP `Yes`] | length(@) ``
- **P015** metricId 450 - Privileged Users List (array)
  - fallback query: `` Users[?Privileged EQ_OP `Yes`] | sort_by(@,&id)[].[displayName OR_OP userPrincipalName] | [] ``
- **P016** metricId 987 - Security Defaults Enabled (boolean) - OK when result EQ_OP true when Conditional Access is not in use (Basic or Business tenants)
  - fallback query: `SystemInfo.Overview.securityDefaults.isEnabled`
- **P017** metricId 1234 - SharePoint Sites Count (integer) - SharePoint sites key is lowercase 'sites' — JMESPath is case-sensitive. 'Sites' (capital S) returns null. VALIDATED: System B (2026-05-22, inspectorID=8) return...
  - fallback query: `sites[] | length(@)`
- **P018** metricId 767 - Stale Licensed Users Count (integer)
  - fallback query: `` length(Users[?activeLast30Days EQ_OP `false` AND_OP accountEnabled EQ_OP `true` ]) ``

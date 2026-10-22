# Single-System Analysis — Microsoft 365 (Run Card part 5)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Recipe `single-system-microsoft-365` run card part 5: continuation of `single-system-microsoft-365 run card` with metrics P019-P020. Run each line exactly as step 4 of the main run card says.

### single-system-microsoft-365 metrics P019-P020

- **P019** metricId 40 - Unlicensed Users Count (integer)
  - fallback query: `` Users[?Assigned_Products EQ_OP ``] | length(@) ``
- **P020** metricId 994 - Users Not Registered for MFA Count (integer) - OK when result EQ_OP 0
  - fallback query: `` Users[?isMfaRegistered_r != `Enabled` AND_OP accountEnabled EQ_OP `true`] | length(@) ``

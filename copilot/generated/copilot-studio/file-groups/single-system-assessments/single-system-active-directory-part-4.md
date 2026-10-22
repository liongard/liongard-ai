# Single-System Analysis — Active Directory (Run Card part 4)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Recipe `single-system-active-directory` run card part 4: continuation of `single-system-active-directory run card` with metrics P013-P016. Run each line exactly as step 4 of the main run card says.

### single-system-active-directory metrics P013-P016

- **P013** metricId none - Store Passwords With Reversible Encryption (boolean)
  - fallback query: `AccountPolicy.PasswordReversible`
- **P014** metricId 23 - Privileged Users Count (integer)
  - fallback query: `SystemInfo.NumPrivilegedUsers`
- **P015** metricId 76 - Privileged Users List (string) (string)
  - fallback query: `SystemInfo.PrivilegedUsersStr`
- **P016** metricId 773 - Stale Active User Accounts Count (integer)
  - fallback query: `` Users[?UserActivity EQ_OP `Stale` AND_OP DefaultSystemUser EQ_OP `false` AND_OP Enabled EQ_OP `true`] | length(@) ``

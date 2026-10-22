# Single-System Analysis — Active Directory (Run Card part 3)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Recipe `single-system-active-directory` run card part 3: continuation of `single-system-active-directory run card` with metrics P007-P012. Run each line exactly as step 4 of the main run card says.

### single-system-active-directory metrics P007-P012

- **P007** metricId none - Lockout Threshold Description (string) - Distinct from AccountPolicy.lockoutThreshold (integer). This is a display string. When lockoutThreshold = 0 this returns 'Infinite Bad Logins Allowed'.
  - fallback query: `AccountPolicy.AccountLockoutThreshold`
- **P008** metricId 748 - Maximum Password Age (integer)
  - fallback query: `AccountPolicy.MaxPasswordAge`
- **P009** metricId 792 - Account Minimum Password Length (integer)
  - fallback query: `AccountPolicy.MinPasswordLength`
- **P010** metricId 775 - Never-Used Active User Accounts Count (integer)
  - fallback query: `` Users[?LastLogonDate EQ_OP `null` AND_OP DefaultSystemUser EQ_OP `false` AND_OP Enabled EQ_OP `true`] | length(@) ``
- **P011** metricId 793 - Password Complexity Enabled (boolean)
  - fallback query: `AccountPolicy.PasswordComplexity`
- **P012** metricId 2022 - Password History Length (integer)
  - fallback query: `AccountPolicy.pwdHistoryLength`

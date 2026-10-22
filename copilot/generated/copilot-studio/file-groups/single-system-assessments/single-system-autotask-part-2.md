# Single-System Analysis — Autotask (Run Card part 2)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Recipe `single-system-autotask` run card part 2: continuation of `single-system-autotask run card` with metrics P001-P006. Run each line exactly as step 4 of the main run card says.

### single-system-autotask metrics P001-P006

- **P001** metricId none - Active Account Count (integer)
  - fallback query: `` length(Accounts[?Active EQ_OP `true`]) ``
- **P002** metricId none - Inactive Account Count (integer)
  - fallback query: `` length(Accounts[?Active EQ_OP `false`]) ``
- **P003** metricId none - Total Account Count (integer)
  - fallback query: `length(Accounts)`
- **P004** metricId none - Active Contact Count (integer)
  - fallback query: `` length(Contacts[?Active EQ_OP `1`]) ``
- **P005** metricId none - Primary Contact Count (integer)
  - fallback query: `` length(Contacts[?PrimaryContact EQ_OP `true`]) ``
- **P006** metricId none - Total Contact Count (integer)
  - fallback query: `length(Contacts)`

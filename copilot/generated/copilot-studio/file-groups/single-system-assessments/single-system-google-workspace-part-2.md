# Single-System Analysis — Google Workspace (Run Card part 2)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Recipe `single-system-google-workspace` run card part 2: continuation of `single-system-google-workspace run card` with metrics P001-P006. Run each line exactly as step 4 of the main run card says.

### single-system-google-workspace metrics P001-P006

- **P001** metricId none - Subscription Seat Summary (array) - Subscriptions present on one of three systems; on flexible plans assigned can exceed purchased, so report the fields rather than a single percentage.
  - fallback query: `Subscriptions[].{sku: skuName, status: status, purchased: seats.numberOfSeats, max: seats.maximumNumberOfSeats, assigned: seats.licensedNumberOfSeats}`
- **P002** metricId none - Super Admin Count (integer)
  - fallback query: `` length(Users[?isAdmin EQ_OP `true`]) ``
- **P003** metricId none - Super Admin List (array)
  - fallback query: `` Users[?isAdmin EQ_OP `true`].primaryEmail ``
- **P004** metricId none - 2-Step Verification Enrollment (enrolled / total) (object) - Returns enrolled and total; compute the percentage as enrolled / total. isEnrolledIn2Sv_m holds strings; do not filter on it.
  - fallback query: `{enrolled: length(Users[?isEnrolledIn2Sv AND_OP !suspended AND_OP !archived]), total: length(Users[?!suspended AND_OP !archived])}`
- **P005** metricId none - 2-Step Verification Enforced Count (integer)
  - fallback query: `` length(Users[?isEnforcedIn2Sv EQ_OP `true`]) ``
- **P006** metricId none - Stale User Count (integer)
  - fallback query: `` length(Users[?DaysSinceLastLogin_r > `90`]) ``

# Single-System Assessment — Synology NAS (Run Card part 2)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Recipe `single-system-synology-nas` run card part 2: continuation of `single-system-synology-nas run card` with metrics P001-P006. Run each line exactly as step 4 of the main run card says.

### single-system-synology-nas metrics P001-P006

- **P001** metricId 399 - Active Users Count (integer) - Users[].expired is a STRING — "normal" means active, "now" means currently expired. Filter with EQ_OP `normal` (backtick literal). Don't compare against true/false...
  - fallback query: `` Users[?expired EQ_OP `normal`] | length(@) ``
- **P002** metricId none - Admin Users Count (integer) - See admin-users-list. Liongard catalog metric 398 still uses the old name-only query (counts every user): do not use it until it is corrected.
  - fallback query: `Users[?GroupMembership[?name EQ_OP 'administrators' AND_OP is_member] OR_OP GroupMembership.groups[?name EQ_OP 'administrators' AND_OP is_member]] | length(@)`
- **P003** metricId none - Admin Users List (array) - OK when result contains only expected admin accounts ; GroupMembership is an array of {name, is_member} on DSM 6 and an object {groups: [...]} on DSM 7. Every user lists the administrators group with is_member true/...
  - fallback query: `Users[?GroupMembership[?name EQ_OP 'administrators' AND_OP is_member] OR_OP GroupMembership.groups[?name EQ_OP 'administrators' AND_OP is_member]].name`
- **P004** metricId none - Disks in Normal State (Count) (integer)
  - fallback query: `length(Disks[?status EQ_OP 'normal'])`
- **P005** metricId none - SSD Disk Count (integer) - Disks[].isSsd is a BOOLEAN (true/false), not a string. Filter with EQ_OP `true` (backtick literal). remain_life is an OBJECT {trustable: bool, value: int}, not a s...
  - fallback query: `` length(Disks[?isSsd EQ_OP `true`]) ``
- **P006** metricId none - Drives Not in Normal State (Count) (integer) - OK when result EQ_OP 0 ; drive_status_category / drive_status_key do not exist in current dataprints (DSM 6.2 and 7.1); filters on them always return 0 (a silent false pass). Use status...
  - fallback query: `Disks[?status != 'normal'] | length(@)`

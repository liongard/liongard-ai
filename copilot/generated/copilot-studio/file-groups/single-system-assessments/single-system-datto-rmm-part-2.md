# Single-System Analysis — Datto RMM (Run Card part 2)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Recipe `single-system-datto-rmm` run card part 2: continuation of `single-system-datto-rmm run card` with metrics P001-P002. Run each line exactly as step 4 of the main run card says.

### single-system-datto-rmm metrics P001-P002

- **P001** metricId 1069 - Devices with Pending Approved Patches Count (integer) - OK when result EQ_OP 0
  - fallback query: `` Devices[?patchManagement.patchesApprovedPending > `0`] | length(@) ``
- **P002** metricId 1070 - Devices with SNMP Enabled Count (integer)
  - fallback query: `` Devices[?snmpEnabled EQ_OP `true`] | length(@) ``

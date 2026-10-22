# Single-System Analysis — Microsoft 365 (Run Card part 3)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Recipe `single-system-microsoft-365` run card part 3: continuation of `single-system-microsoft-365 run card` with metrics P007-P012. Run each line exactly as step 4 of the main run card says.

### single-system-microsoft-365 metrics P007-P012

- **P007** metricId 64 - Disabled Users Count (integer)
  - fallback query: `` Users[?accountEnabled EQ_OP `false`]|length(@) ``
- **P008** metricId 879 - Disabled Users with Licenses Count (integer) - OK when result EQ_OP 0
  - fallback query: `` Users[?accountEnabled EQ_OP `false` AND_OP assignedLicenses.length(@) > `0`] | length(@) ``
- **P009** metricId 37 - Enterprise E3 Licenses Consumed (integer)
  - fallback query: `` Licensing[?skuPartNumber EQ_OP `ENTERPRISEPACK`].consumedUnits | [0] ``
- **P010** metricId 38 - Enterprise E5 Licenses Consumed (integer)
  - fallback query: `` Licensing[?skuPartNumber EQ_OP `ENTERPRISEPREMIUM`].consumedUnits | [0] ``
- **P011** metricId 41 - Licensed Users Count (integer)
  - fallback query: `` Users[?Assigned_Products != ``] | length(@) ``
- **P012** metricId 63 - Total Licenses Assigned Count (integer)
  - fallback query: `Licensing[].consumedUnits | sum(@)`

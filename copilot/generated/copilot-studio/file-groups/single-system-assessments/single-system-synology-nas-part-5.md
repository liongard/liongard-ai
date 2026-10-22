# Single-System Assessment — Synology NAS (Run Card part 5)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Recipe `single-system-synology-nas` run card part 5: continuation of `single-system-synology-nas run card` with metrics P019-P024. Run each line exactly as step 4 of the main run card says.

### single-system-synology-nas metrics P019-P024

- **P019** metricId 920 - Storage Pools Not in Normal State (List) (array) - OK when result EQ_OP []
  - fallback query: `` StoragePools[?status !=`normal`].id ``
- **P020** metricId 396 - System Temperature (Celsius) (integer)
  - fallback query: `SystemInfo.sys_temp`
- **P021** metricId 917 - Volumes Below 20% Free Space (Count) (integer) - OK when result EQ_OP 0
  - fallback query: `` Volumes[?volume_percentage_free_r < `20`] | length(@) ``
- **P022** metricId 916 - Volumes Below 20% Free Space (List) (array) - OK when result EQ_OP []
  - fallback query: `` Volumes[?volume_percentage_free_r < `20`].id ``
- **P023** metricId 923 - Volumes Not in Normal State (Count) (integer) - OK when result EQ_OP 0
  - fallback query: `` Volumes[?!contains(status,`normal`)] | length(@) ``
- **P024** metricId 922 - Volumes Not in Normal State (List) (array) - OK when result EQ_OP []
  - fallback query: `` Volumes[?!contains(status,`normal`)].id ``

# Single-System Assessment — Synology NAS (Run Card part 4)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Recipe `single-system-synology-nas` run card part 4: continuation of `single-system-synology-nas run card` with metrics P013-P018. Run each line exactly as step 4 of the main run card says.

### single-system-synology-nas metrics P013-P018

- **P013** metricId 395 - Serial Number (string)
  - fallback query: `SystemInfo.serial`
- **P014** metricId none - Disabled Services Count (integer) - Service state field varies: DSM 7 enable_status "enabled"/"disabled"/"static"; older DSM 6 enable_status "enable"/"disable"; newer DSM 6 boolean enable. Use the...
  - fallback query: `length(Services[?enable_status EQ_OP 'disabled' OR_OP enable_status EQ_OP 'disable' OR_OP type(enable) EQ_OP 'boolean' AND_OP !enable])`
- **P015** metricId none - Enabled Services Count (integer) - Service state field varies: DSM 7 enable_status "enabled"/"disabled"/"static"; older DSM 6 enable_status "enable"/"disable"; newer DSM 6 boolean enable. Use the...
  - fallback query: `length(Services[?enable_status EQ_OP 'enabled' OR_OP enable_status EQ_OP 'enable' OR_OP type(enable) EQ_OP 'boolean' AND_OP enable])`
- **P016** metricId none - Total Services Count (integer)
  - fallback query: `length(Services)`
- **P017** metricId none - Unencrypted Shares Count (integer) - OK when result EQ_OP 0 ; Shares[].encryption is an INTEGER (0 = not encrypted, 1 = encrypted), NOT a boolean. Don't compare against `false`.
  - fallback query: `` length(Shares[?encryption EQ_OP `0`]) ``
- **P018** metricId 921 - Storage Pools Not in Normal State (Count) (integer) - OK when result EQ_OP 0
  - fallback query: `` StoragePools[?status !=`normal`] | length(@) ``

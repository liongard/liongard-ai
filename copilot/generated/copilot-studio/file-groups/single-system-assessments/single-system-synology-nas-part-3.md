# Single-System Assessment — Synology NAS (Run Card part 3)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Recipe `single-system-synology-nas` run card part 3: continuation of `single-system-synology-nas run card` with metrics P007-P012. Run each line exactly as step 4 of the main run card says.

### single-system-synology-nas metrics P007-P012

- **P007** metricId none - Drives Not in Normal State (List) (array) - OK when result EQ_OP [] ; drive_status_category / drive_status_key do not exist in current dataprints (DSM 6.2 and 7.1); filters on them always return 0 (a silent false pass). Use status...
  - fallback query: `Disks[?status != 'normal'].name`
- **P008** metricId 393 - Firmware Version (string)
  - fallback query: `SystemInfo.firmware_ver`
- **P009** metricId 919 - iSCSI Targets Offline (Count) (integer) - OK when result EQ_OP 0
  - fallback query: `` ISCSITargets[?enabled EQ_OP `true` AND_OP status != `online`] | [?status != `connected`] | length(@) ``
- **P010** metricId 918 - iSCSI Targets Offline (List) (array) - OK when result EQ_OP []
  - fallback query: `` ISCSITargets[?enabled EQ_OP `true` AND_OP status != `online`] | [?status != `connected`].join(`: `, [name, iqn]) ``
- **P011** metricId 394 - Model (string)
  - fallback query: `SystemInfo.model`
- **P012** metricId none - Enabled Services (List) (array) - Service state field varies: DSM 7 enable_status "enabled"/"disabled"/"static"; older DSM 6 enable_status "enable"/"disable"; newer DSM 6 boolean enable. Use the...
  - fallback query: `Services[?enable_status EQ_OP 'enabled' OR_OP enable_status EQ_OP 'enable' OR_OP type(enable) EQ_OP 'boolean' AND_OP enable].display_name`

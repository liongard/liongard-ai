# Single-System Analysis — Datto BCDR (Run Card part 2)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Recipe `single-system-datto-bcdr` run card part 2: continuation of `single-system-datto-bcdr run card` with metrics P001-P006. Run each line exactly as step 4 of the main run card says.

### single-system-datto-bcdr metrics P001-P006

- **P001** metricId 2079 - Agent Backups Without Screenshot Verification (array) - OK when result EQ_OP [] ; !isArchived uses boolean negation here — confirming isArchived is stored as boolean on the Assets[] objects. The older metrics (ids 757, 759, 760) use string or...
  - fallback query: `Assets[?!isArchived AND_OP type EQ_OP 'agent' AND_OP !lastScreenshotAttempt].name[]`
- **P002** metricId 218 - Appliance Model (string)
  - fallback query: `SystemInfo.model`
- **P003** metricId 217 - Appliance Serial Number (string)
  - fallback query: `SystemInfo.serialNumber`
- **P004** metricId 219 - Protected Assets Count (integer)
  - fallback query: `length(Assets)`
- **P005** metricId 216 - Associated Device Names (string)
  - fallback query: `` Assets[].name | join(`, ` @) ``
- **P006** metricId 757 - Recent Backup Failures (Most Recent Job) (array) - OK when result EQ_OP [] ; isArchived is tested as string 'true' in the Global metric (isArchived != `true`), not boolean. backups[0] references the most recent backup job entry. Both ass...
  - fallback query: `` Assets[?isArchived != `true` AND_OP backups[0].backup.status EQ_OP 'failure'].name ``

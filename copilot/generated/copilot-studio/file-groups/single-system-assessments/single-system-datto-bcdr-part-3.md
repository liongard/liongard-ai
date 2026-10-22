# Single-System Analysis — Datto BCDR (Run Card part 3)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Recipe `single-system-datto-bcdr` run card part 3: continuation of `single-system-datto-bcdr run card` with metrics P007-P012. Run each line exactly as step 4 of the main run card says.

### single-system-datto-bcdr metrics P007-P012

- **P007** metricId 2078 - Assets With No Successful Backup in 30+ Days (array) - OK when result EQ_OP []
  - fallback query: `` Assets[?isArchived EQ_OP `false` AND_OP HoursSinceLastSuccessfulBackup_r != `99999` AND_OP HoursSinceLastSuccessfulBackup_r > `720`].name[] ``
- **P008** metricId 760 - Backups Not Completed in Last 24 Hours Count (integer) - OK when result EQ_OP 0 ; HoursSinceLastSuccessfulBackup_r is a Liongard-computed (_r suffix) field, not a native Datto field. A value of 99999 means 'never backed up' or data unavailabl...
  - fallback query: `` Assets[?isArchived EQ_OP `false` AND_OP HoursSinceLastSuccessfulBackup_r != `99999` AND_OP HoursSinceLastSuccessfulBackup_r > `24`] | length(@) ``
- **P009** metricId 759 - Backups Not Completed in Last 24 Hours Summary (string) - OK when result EQ_OP null OR_OP result EQ_OP ''
  - fallback query: `` Assets[?isArchived EQ_OP `false` AND_OP HoursSinceLastSuccessfulBackup_r != `99999` AND_OP HoursSinceLastSuccessfulBackup_r > `24`].[name, join(' ',['Latest Successful Backup:' ,latestSuccessfulBackup_r])][] | join (' | ', @) ``
- **P010** metricId 1000 - Days Until Service Expiration (integer) - OK when result > 30 ; NumDaysTillServiceExpiration_r uses the _r suffix — this is a Liongard-computed derived field, not a raw Datto API field.
  - fallback query: `SystemInfo.NumDaysTillServiceExpiration_r`
- **P011** metricId 976 - Days Until Warranty Expiration (integer) - OK when result > 30
  - fallback query: `SystemInfo.NumDaysTillWarrantyExpiration`
- **P012** metricId 833 - Percent Local Storage Free (integer) - OK when result >= 20
  - fallback query: `SystemInfo.PercentLocalStorageFree`

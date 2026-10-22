# metrics-system-type-all-firewalls-cisco-asa - Metric reference (cisco-asa-inspector)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Required metric primitives for the recipe `system-type-all-firewalls` (System-Type Assessment — All Firewalls), inspector `cisco-asa-inspector` (ID 22). 9 primitives, sequence ids P010-P018. For every system of this inspector, evaluate EVERY primitive below with `liongard_metric EVALUATE` (`jmesPathQuery`, `systemId`, `environmentId`), retry a null or error once, and log one row per primitive per system. Respect each gotcha.

- **`metrics:cisco-asa:configs-match`** [P010] - Cisco ASA — Running and Startup Configs Match. Boolean indicating whether the running config matches the startup config from SystemInfo.MatchingConfigurations. False means unsaved changes will be lost on reboot.
  - metricId: 736 | query: `SystemInfo.MatchingConfigurations` | result: boolean
  - compliant when: result EQ_OP true
  - status: VALIDATED
- **`metrics:cisco-asa:last-config-modified`** [P011] - Cisco ASA — Last Config Modification Date. Timestamp of the last configuration change from SystemInfo.LastModifiedAt. Use for change detection.
  - metricId: 18 | query: `SystemInfo.LastModifiedAt` | result: string
  - status: VALIDATED
- **`metrics:cisco-asa:licenses-expiring-30d-count`** [P012] - Cisco ASA — Active Licenses Expiring Within 30 Days Count. Count of active ASA licenses expiring within 30 days from SystemInfo.Licenses[?DaysTillExpiration<=30 AND_OP Active EQ_OP true].
  - metricId: 732 | query: `` length(SystemInfo.Licenses[?DaysTillExpiration<=`30` AND_OP Active EQ_OP `true`]) `` | result: integer (count)
  - compliant when: result EQ_OP 0
  - status: VALIDATED
- **`metrics:cisco-asa:licenses-expiring-5d-count`** [P013] - Cisco ASA — Active Licenses Expiring Within 5 Days Count. Count of active ASA licenses expiring within 5 days — critical alert threshold.
  - metricId: 731 | query: `` length(SystemInfo.Licenses[?DaysTillExpiration<=`5` AND_OP Active EQ_OP `true`]) `` | result: integer (count)
  - compliant when: result EQ_OP 0
  - status: VALIDATED
- **`metrics:cisco-asa:licenses-expiring-5d-list`** [P014] - Cisco ASA — Active Licenses Expiring Within 5 Days List. List of active ASA license objects expiring within 5 days.
  - metricId: 730 | query: `` to_string(SystemInfo.Licenses[?DaysTillExpiration<=`5` AND_OP Active EQ_OP `true`] OR_OP `-`) `` | result: string
  - compliant when: result EQ_OP '-'
  - status: VALIDATED
- **`metrics:cisco-asa:model`** [P015] - Cisco ASA — Model. Hardware model from SystemInfo.Model.
  - metricId: 257 | query: `SystemInfo.Model` | result: string
  - status: VALIDATED
- **`metrics:cisco-asa:running-config`** [P016] - Cisco ASA — Running Configuration. Full running configuration snapshot from RunningConfig. Use for policy review and change detection.
  - metricId: 522 | query: `RunningConfig` | result: object
  - status: VALIDATED
- **`metrics:cisco-asa:serial-number`** [P017] - Cisco ASA — Serial Number. Hardware serial number from SystemInfo.SerialNumber.
  - metricId: 9 | query: `SystemInfo.SerialNumber` | result: string
  - status: VALIDATED
- **`metrics:cisco-asa:software-version`** [P018] - Cisco ASA — ASA Software Version. ASA software version string from SystemInfo.CiscoAdaptiveSecurityApplianceSoftwareVersion.
  - metricId: 254 | query: `SystemInfo.CiscoAdaptiveSecurityApplianceSoftwareVersion` | result: string
  - status: VALIDATED

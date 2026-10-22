# Single-System Analysis — Huntress (Run Card part 2)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Recipe `single-system-huntress` run card part 2: continuation of `single-system-huntress run card` with metrics P001-P006. Run each line exactly as step 4 of the main run card says.

### single-system-huntress metrics P001-P006

- **P001** metricId none - Incident Reports Count (integer) - OK when result EQ_OP 0 ; Incidents[] and Footholds[] arrays DO NOT exist in the Huntress child dataprint. The only available incident indicator is Organization.incident_reports_count (i...
  - fallback query: `Organization.incident_reports_count`
- **P002** metricId none - Total Agents Count (integer) - Agents[] confirmed fields: id, version, arch, win_build_number, domain_name, created_at, hostname, ipv4_address, external_ip, mac_addresses, updated_at, last_su...
  - fallback query: `length(Agents)`
- **P003** metricId 24301 - Unresponsive Agents Count (21 days) (integer) - OK when result EQ_OP 0
  - fallback query: `` Agents[?DaysSinceLastCheckin >= `21`] | length(@) ``
- **P004** metricId 24303 - Unresponsive Agents Count (30 days) (integer) - OK when result EQ_OP 0
  - fallback query: `` Agents[?DaysSinceLastCheckin >= `30`] | length(@) ``
- **P005** metricId 24307 - Unresponsive Agents Count (60 days) (integer) - OK when result EQ_OP 0
  - fallback query: `` Agents[?DaysSinceLastCheckin >= `60`] | length(@) ``
- **P006** metricId 24300 - Unresponsive Agents List (21 days) (array) - OK when result EQ_OP []
  - fallback query: `` Agents[?DaysSinceLastCheckin >= `21`].hostname ``

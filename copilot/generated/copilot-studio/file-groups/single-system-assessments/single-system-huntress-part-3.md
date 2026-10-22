# Single-System Analysis — Huntress (Run Card part 3)

> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)

Recipe `single-system-huntress` run card part 3: continuation of `single-system-huntress run card` with metrics P007-P008. Run each line exactly as step 4 of the main run card says.

### single-system-huntress metrics P007-P008

- **P007** metricId 24302 - Unresponsive Agents List (30 days) (array) - OK when result EQ_OP []
  - fallback query: `` Agents[?DaysSinceLastCheckin >= `30`].hostname ``
- **P008** metricId 24306 - Unresponsive Agents List (60 days) (array)
  - fallback query: `` Agents[?DaysSinceLastCheckin >= `60`].hostname ``

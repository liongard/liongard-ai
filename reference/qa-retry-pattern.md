# Quality Assurance & Manual Verification — Canonical Pattern

Every recipe runs a QA pass after data collection and before rendering the
report. The QA pass retries transient failures, flags stale inspectors and
divergent counts, surfaces known data gaps, and produces a **Manual
Verification Needed** appendix in the deliverable so the reader knows exactly
what to confirm by hand.

This file is the canonical implementation. Recipes link here instead of
redefining the pattern.

---

## When QA runs

```
Step 1: Identify environment + scope
Step 2: Pull primary evidence (asset inventory tools, metrics)
Step 3: Compute insights / status
Step 4: ▼▼▼ QA & manual-verification pass ▼▼▼
Step 5: Render output
Step 6: Append verification log
```

The QA pass mutates the in-memory dataset (filling retried values) and
**produces a list of manual-check items** that gets included in the rendered
deliverable.

---

## What QA inspects

### Category 1 — Transient nulls (retry)

A metric or asset query that returns `null` may be:
- A genuine absence ("there is no value")
- A transient miss (inspector mid-cycle, API throttle, sync lag)

The retry pattern doesn't try to distinguish these — it retries N times. If
all retries return `null`, **only then** treat as a confirmed absence and
log to the manual-verification appendix.

```
def fetch_with_retry(call, args):
    attempts = 1 + qa.retry_attempts
    for i in range(attempts):
        result = call(**args)
        if result is not None and not is_failed_status(result):
            return result, attempts_used=i+1
        if i < attempts - 1:
            sleep(qa.retry_delay_seconds)
    # Persistent null — log as confirmed absence requiring verification
    return result, attempts_used=attempts, persistent_null=True
```

Apply to:
- `liongard_metric EVALUATE` — every metric call.
- `liongard_device LIST` / `COUNT`, `liongard_identity LIST` / `COUNT`,
  `liongard_domain LIST` / `COUNT` — when result count is 0 AND a non-zero
  result was expected (e.g., the customer has an M365 tenant but
  `liongard_identity COUNT` returns 0 — that's a transient miss, not the
  customer having zero identities).
- `liongard_system LIST` — when no systems return for an inspector keyword
  the customer is known to have deployed.

**Don't retry:**
- `liongard_environment LIST` — the environment list is stable; failures
  are usually auth, not transient.
- Empty arrays when emptiness is the expected outcome (the recipe knows
  the customer has zero of the thing).

### Category 2 — Stale inspector (flag, don't retry)

A system / asset record with `lastSeen` older than
`qa.flag_inspector_lastseen_threshold_days` (default 7) is reporting stale
data. Don't retry — the data won't change without the inspector running.

```
for each system / asset / metric source used:
    if lastSeen < (today - qa.flag_inspector_lastseen_threshold_days):
        manual_verification.append({
            'category': 'stale_inspector',
            'source': <system or asset>,
            'last_seen': lastSeen,
            'days_stale': today - lastSeen,
            'remediation': 'Trigger an inspection from Liongard or confirm via vendor console'
        })
```

For per-host data (e.g., a Windows Server's pending-update count), if the
server's inspector `lastSeen` > threshold, **flag the per-host result as
stale** in the report — the count may be out of date.

### Category 3 — Count divergence (flag, don't pick a winner)

When two tools answer the same question differently — for example,
`liongard_identity COUNT mfaStatus="NO"` returns 12, but the per-inspector
M365 metric `683` (Admin MFA Disabled Count) returns 8 — surface **both
values** and let the user decide. Do not silently pick one.

```
for each pair of tools answering the same question:
    if abs(value_a - value_b) / max(value_a, value_b) > qa.flag_count_divergence_threshold_pct / 100:
        manual_verification.append({
            'category': 'count_divergence',
            'question': <q>,
            'tool_a': {'name': <tool>, 'value': value_a},
            'tool_b': {'name': <tool>, 'value': value_b},
            'remediation': 'Confirm in the vendor console; divergence usually indicates an inspector lag or scope difference'
        })
```

The asset-inventory tools (`liongard_device`, `liongard_identity`,
`liongard_domain`) are authoritative for cross-inspector synthesis — if
they disagree with a single-inspector metric, the **asset value wins**, but
the divergence still gets flagged.

### Category 4 — Known proposed-metric gaps (flag, list)

Recipes that depend on metrics marked `[PROPOSED]` (not yet in the Liongard
library — see `reference/future-recipes-roadmap.md`) should explicitly list
which fields are not directly available, with the workaround the recipe
used and the manual-check action.

```
for each proposed_metric in recipe.proposed_metrics_used:
    manual_verification.append({
        'category': 'proposed_metric_gap',
        'field': <field_name>,
        'workaround': <client_side_filter or 'no fallback'>,
        'remediation': 'Confirm in <vendor> console; track Jira ticket <CORE-XXXX>'
    })
```

### Category 5 — Single-source data quality flag

When data for an asset comes from only one inspector (e.g., a device with
`inspectors[]` containing only `active-directory-inspector`), security
fields like `antivirus`, `edr`, BitLocker status will be `null` — the
inspector that would populate them hasn't run.

```
for each device in primary_evidence:
    if length(device.inspectors) == 1 and device.inspectors[0] == 'active-directory-inspector':
        if recipe.needs_local_inspection_fields:
            manual_verification.append({
                'category': 'single_source_visibility',
                'device': device.hostname,
                'reason': 'Domain-known but not locally inspected',
                'remediation': 'Deploy windows-workstation-inspector or windows-server-inspector for security-posture data'
            })
```

The same applies to identities reported only by one inspector (e.g., a
legacy LDAP system with no MFA visibility).

---

## The "Manual Verification Needed" appendix

Every deliverable must include this appendix. It's the user-facing summary
of everything QA flagged.

### Format

```markdown
## Manual Verification Needed

The following items require confirmation outside Liongard. Each is flagged
because Liongard could not produce a definitive value within this
assessment run.

| # | Category | Item | Why | Recommended check |
|---|---|---|---|---|
| 1 | Stale inspector | SonicWall firewall <hostname> | Inspector last reported 9 days ago | Confirm firmware version + WAN rules in SonicWall portal |
| 2 | Count divergence | Privileged users count | liongard_identity reports 12; AD metric 23 reports 14 | Reconcile in AD; difference may be M365-only privileged accounts |
| 3 | Proposed metric gap | M365 license expiration date per SKU | Not yet in Liongard library | Confirm renewal date in M365 admin portal; track CORE-XXXX |
| 4 | Single-source visibility | <hostname> | Domain-known, no local inspection | Deploy Windows Workstation Inspector |
| 5 | Persistent null | EDR detection on <hostname> | 3 retries returned null | Verify EDR install state in vendor console |
```

### Rendering rules

- The appendix is **not optional**. If the QA pass produced zero items,
  the section says so explicitly: "✅ All evidence verified — no manual
  checks needed."
- Items are ordered by severity: persistent null > count divergence > stale
  inspector > proposed metric gap > single-source visibility.
- Each item has a concrete recommended check — no generic "review the
  console" guidance.

---

## Customization knobs (in the recipe's customization block)

```yaml
qa:
  retry_on_null: true                            # retry metric calls returning null
  retry_on_empty_array: false                    # empty array usually = no records
  retry_attempts: 2                              # extra attempts after the first
  retry_delay_seconds: 5
  flag_inspector_lastseen_threshold_days: 7
  flag_count_divergence_threshold_pct: 5
  surface_proposed_metrics: true                 # list known [PROPOSED] gaps
  surface_single_source_visibility: true         # flag AD-only / one-inspector assets
  manual_verification_section_required: true    # appendix mandatory
```

MSPs can tighten or loosen any threshold. Typical overrides:
- Server-class recipes: `flag_inspector_lastseen_threshold_days: 1` (daily
  inspection expected on production servers).
- Onboarding QA: `flag_count_divergence_threshold_pct: 1` (during
  onboarding the MSP wants to see every divergence to fix data quality).
- Roadmap planning: `surface_proposed_metrics: true` is critical (the
  roadmap recipe's whole purpose is to expose what isn't yet measurable).

---

## Recipe section template

Recipes paste this section after **Insights & recommendations** and before
**Output format**:

```markdown
## QA & Manual Verification

Before rendering the report, run the QA pass per `reference/qa-retry-pattern.md`:

1. **Retry persistent nulls.** For every metric / asset query that returned
   null in Step 2 / 3, re-run up to `qa.retry_attempts` times with
   `qa.retry_delay_seconds` between attempts. Cache the result.

2. **Flag stale inspectors.** For every system / asset used by this recipe,
   compare `lastSeen` against `qa.flag_inspector_lastseen_threshold_days`.
   Add stale ones to the manual-verification list.

3. **Cross-tool divergence check** *(applicable when this recipe queries
   the same question from two tools)*. Compare the answers; flag if
   divergence > `qa.flag_count_divergence_threshold_pct`.

4. **Surface this recipe's known proposed-metric gaps.** Append to the
   manual-verification list: <list of [PROPOSED] metrics this recipe used>.

5. **Render the Manual Verification appendix** in the deliverable
   (mandatory if `qa.manual_verification_section_required == true`).
```

---

## Maintenance

When adding a new recipe:
- Inherit the pattern by copying the section template above.
- List the recipe's known proposed-metric dependencies in the **Known
  proposed-metric gaps** section.
- If the recipe queries the same question from multiple tools, list the
  divergence pairs explicitly.

When the API changes:
- Retry behavior may need adjustment if a tool's null semantics change.
- Update the pattern here and recipes will inherit on next sweep.

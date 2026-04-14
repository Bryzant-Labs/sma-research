# Fleet Health Review — 2026-04-14 15:24 UTC

## 1. Fleet Pulse

- **Vast.ai**: 7 instances (6 running, 1 A100 PCIE + 3x RTX 3090 + 2x Titan RTX + 1x P40), $2.20/hr, no `util` data reported on any instance (null across the board). 3 queue tasks running, 4 queued, 1 new failure vs prev run.
- **Fleet Manager**: alive, cycle 2212 (+1 in 9 min — healthy ~8 min/cycle).
- **NIMs daemon**: systemctl active, 5 outcomes today (was 3), 100% success (5 OK / 0 fail), currently running `nims_molmim_keap1_cddo`. Heartbeat 2 min stale (OK).
- **Modal**: `not_implemented` — as expected.
- **Local GPUs**: not yet reporting — GB10 / RTX 6000 not wired.

## 2. Anomalies

### HIGH — Vast snapshot flapped between runs
- **Signal**: `fleet_health_prev.json` had `vast.status=fail, instances=[]` at 13:15; current run 13:24 is `ok` with 7 instances. 9 min earlier the collector couldn't reach vast API.
- **Hypothesis**: Transient vast API/auth hiccup, or rate limit. The snapshot cron treated a failed API call as a valid state (empty instances) rather than preserving last-known-good.
- **Action**: Have the snapshot collector distinguish "API error" from "0 instances" and carry forward prior state on API failure. One data point is not enough — watch the next 2–3 snapshots.

### HIGH — today_success_rate dropped 0.47 → 0.37 in 9 min
- **Signal**: today_fail 8 → 12 (+4 fails), today_ok still 7. outcomes_total 67 → 71 (all 4 new outcomes were failures).
- **Hypothesis**: A burst of deploy failures is now landing in learner outcomes. Only 1 appears in deploy_alerts.md (`p14_diffdock_erralpha_shard_a`, ssh_unreachable). The other 3 failures are NOT surfaced by deploy_watcher — gap between learner outcome ingestion and watcher's visibility.
- **Action**: Reconcile the 4 new failures against deploy_watcher's stream. If 3 are invisible to watcher, the assertion hook is missing a code path (likely non-deploy failures like verify-fail or task-level reject).

### MEDIUM — Active avoid rule is dormant (pre-fix rule from prior state)
- **Signal**: `diffdock_screen AND gpu_class=RTX 3090 → AVOID ssh_unreachable first-fail` rule at 0.75 confidence, unchanged between runs. Meanwhile `p14_diffdock_erralpha` (a diffdock task) just failed on GPU 34918076 (RTX 3090) with exactly `ssh_unreachable / publickey`. Did the rule gate this? Can't tell from snapshot.
- **Hypothesis**: Either (a) task_type is `diffdock_erralpha` not `diffdock_screen` (canonical-name mismatch repeating the 2-week bug from today's fix), or (b) rule fires but deployer still logs the fail without retry-with-backoff, or (c) rule fires and retry succeeds but isn't reflected here.
- **Action**: Grep fleet_manager log for `p14_diffdock_erralpha` to confirm backoff retry path was taken. If `diffdock_erralpha` is a distinct task_type, the avoid rule needs widening OR task_type needs canonicalizing to `diffdock_screen`.

### MEDIUM — All instances show util=null
- **Signal**: `util: null` for all 7 instances, including ones 60+ min uptime actively running jobs.
- **Hypothesis**: Vast API `gpu_util` field no longer populated, or collector field name drift. Without util, can't detect zombie-burn (the $2/hr problem from this morning).
- **Action**: Verify collector is pulling `gpu_util`/`cur_perf_pct` correctly from `vastai show instances --raw`. Without util, verify-fail detection for "GPU booked but idle" is blind.

### MEDIUM — deploy_watcher has only 1 assertion ever
- **Signal**: `deploy_assertions.jsonl` contains 1 line total (today 13:09). Watcher PID 103012 has been running for hours.
- **Hypothesis**: Either (a) only one task has cleared the 120s post-deploy window so far today, or (b) the watcher attaches to a PID-list that's empty most of the time. If queue has 3 running + 4 queued, assertions should be firing more often.
- **Action**: Check watcher log for how many "assert started" events vs "assert fail" — absence of fails is suspicious given 12 failures today. It may be only observing deploy-stage, not runtime crashes.

### LOW — Learner analyzer threshold (HAVING COUNT >= 3) may be too high for current scale
- **Signal**: 12 failures today but only 1 active avoid rule. ssh_unreachable + publickey is a known-bad signature but hasn't crossed the 3-occurrence gate across matching (task_type, gpu_class) tuples today.
- **Hypothesis**: With failures spread across task_types (diffdock_erralpha, diffdock_screen, etc.), no single tuple accrues 3 instances fast. Rules never form.
- **Action**: Consider widening analyzer's GROUP BY to include (error_signature) alone — ssh_unreachable/publickey is infrastructure-level, not task-specific. Or drop threshold to 2 with human-approval gate for the 3rd.

## 3. Regressions vs Last Run (9-min delta)

| Metric | Prev (13:15) | Now (13:24) | Δ |
|---|---|---|---|
| Vast instances | API fail (0) | 7 | +7 (API recovery) |
| $/hr | unknown | 2.20 | — |
| Queue running | 4 | 3 | -1 |
| Queue failed (cumulative) | 41 | 42 | +1 |
| today_ok | 7 | 7 | 0 |
| today_fail | 8 | 12 | +4 |
| today_success_rate | 0.47 | 0.37 | -0.10 |
| outcomes_total | 67 | 71 | +4 (all fails) |
| NIMs jobs_done | 3 | 5 | +2 |
| active_rules | 2 | 2 | 0 |
| checkpoint timestamp | 12:56 | 13:22 | +26 min (fresh, OK) |

**New failed task IDs (from deploy_alerts)**: `p14_diffdock_erralpha_shard_a` (GPU 34918076 RTX 3090, ssh_unreachable). The other 3 new failures are not itemized in snapshot — visibility gap.

## 4. Suggested Learnings for AgentLearner (human-approve, don't auto-form)

1. **ssh_unreachable / publickey on ssh7.vast.ai = ALWAYS transient** (infra-level, not task-level).
   - Condition: `error_signature CONTAINS 'ssh7.vast.ai: Permission denied (publickey)'`
   - Action: retry SSH 30s/2m/5m with `vastai show instance` health check before failing; do NOT decrement task health on first occurrence.
   - Suggested confidence: 0.90
   - Why human-approved: cross-cuts task_types; auto-analyzer GROUP BY (task_type,gpu_class) won't surface this signature even at 10+ occurrences.

2. **util=null with uptime>20 min = possible zombie** (matches this-morning's $2/hr burn).
   - Condition: `util IS NULL AND uptime_min > 20 AND dph > 1.0`
   - Action: escalate as CRITICAL — capture pstree + gpu-smi from instance; do NOT auto-destroy, alert human.
   - Suggested confidence: 0.80
   - Why human-approved: destroy-on-null risks killing a healthy instance during vast API field drift; today's $2/hr loss justifies a guardrail even if it's slightly noisy.

3. **task_type canonical mismatch detector**.
   - Condition: `new task_type observed that matches PREFIX of an existing canonical task_type` (e.g. `diffdock_erralpha` vs `diffdock_screen`)
   - Action: halt dispatch, alert — this was the exact silent-drop bug from today.
   - Suggested confidence: 0.95
   - Why human-approved: the cost of this bug was 2 weeks of silent failure; a detector is cheap insurance.

4. **outcome arrival without deploy_watcher assertion row = observability hole**.
   - Condition: `learner outcome logged with success=false AND no matching deploy_assertions.jsonl row within ±5 min`
   - Action: tag the failure as `unobserved_by_watcher` and page.
   - Suggested confidence: 0.85
   - Why human-approved: watcher blind-spots are the single scariest failure mode; better to over-alert early while coverage is being validated.

---

STATUS: YELLOW — Fleet functionally running (NIMs 5/5, queue draining, manager healthy) but new instrumentation has visibility gaps: success rate slid to 37%, only 1 of 4+ new failures reached deploy_watcher, and util=null on all vast instances blinds the zombie detector.

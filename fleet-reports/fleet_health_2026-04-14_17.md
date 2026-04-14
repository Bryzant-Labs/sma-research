# Fleet Health Review — 2026-04-14 17:00 UTC

## 1. Fleet Pulse

- **Vast.ai**: 4 instances, $1.60/hr. 3 running (A100 PCIE 94%, Tesla P40 100%, Titan RTX 98%) + 1 RTX 3090 still uptime=0/status=null (now allocated ~3h, never phoned home — will re-check next cycle; if it crosses uptime>15min with util still null, it becomes the first real zombie-suspect test). `n_zombie_suspect=0`.
- **Fleet manager**: alive PID 128593, restarted 16:16 UTC. Cycles progressing cleanly: 2221 (pre-restart) → 2222 (16:16) → 2223 (16:22) → 2224 (16:25) → 2225 (16:30). No startup crash, no errors in recent tail.
- **Deploy watcher**: alive PID 127182, restarted 16:23 UTC with VERIFY_FAIL_RX live. Log shows 2 clean startup lines, no crashes.
- **NIMs daemon**: active, jobs_done=2 in current key cycle, 10 total outcomes, all success. Heartbeat fresh. Tier-1 advancing.
- **Queue**: 271 completed, 42 failed (+0 since prev), 11 queued, 2 running, 1 blocked, 1 planned, 3 superseded. Flow healthy.
- **Reconciliation**: `healthy=true`, `orphan_count=0`, age 155s (fresh, not stale). 16 deploy_failure_outcomes historical, 0 fell inside the post-16:14 reconcile window → clean state since the cutoff. Report ran at 16:27.
- **Checkpoint**: vast lane 119GB synced OK, NIMs two-hop OK, modal still `not_implemented`.

## 2. Reconciliation — Primary Finding

**GREEN.** `reconciliation.healthy == true`, `orphan_count == 0`, `watcher_fails_without_outcome == 0`, `outcomes_in_reconcile_window == 0`. The 16 pre-cutoff failures are correctly excluded. No silent drift detected. This is the structural invariant working as designed — there is currently nothing for it to complain about because no new deploys have failed since the cutoff. That is a thin test: the mechanism is proven to run and write a fresh file on the 15/45 cron, but it has not yet been tested against a live post-16:14 failure event. Will stay GREEN until the next real deploy failure lands; that is the first true validation.

## 3. Prior-Fix Honesty Check

### Fix 1 — Deploy watcher VERIFY_FAIL tail (restarted 16:23, PID 127182)
- **Evidence**: watcher process alive, log shows start line at 14:23 UTC (host clock offset, matches 16:23 real). `deploy_assertions.jsonl` still 1 line (from 13:09), `deploy_alerts.md` still 1 line. **No new entries since 16:23 — but also no new deploy launches the watcher would have seen.** Fleet_manager cycles 2222–2225 show no `LAUNCHED PID=` events in recent tail and no `FAILED verification` patterns; queue is 2 running (both long-lived), only 11 queued waiting on GPU availability.
- **Verdict**: **Fix cannot be disproven by absence of events.** The watcher is armed. No new fails have occurred to feed it. First post-restart deploy will be the validating signal. Note: `recent_1h_fail=2` in the learner — investigate whether those 2 were pre-16:23 (probable given cycle gap) or if they are post-16:23 fails that bypassed the deploy stage and so would not produce a watcher assertion by design. Below.

### Fix 2 — gate_blocked retry (env GATE_BLOCKED_RETRY_S=21600)
- **Evidence (CONFIRMED)**: fleet_manager.log shows exactly 6 retry lines at 16:25:04, one per parked task:
  - `p6_mmpbsa_limk2_genmol119_bbb0`, `p6_mmpbsa_limk2_references`, `p7_md_pfn2_bbb5_50ns`, `p7_md_limk1_bbb5_50ns`, `p8_md_4ap_kv12_50ns`, `holo_mmpbsa_bbb5`
  - All log `age 360m ≥ 360m` — parked at 10:25 UTC, fired at the 6h boundary.
- **Verdict**: **Working exactly as specified.** The 6 parked tasks are now eligible for re-dispatch. Queue still shows `gate_blocked=1` in snapshot (not 6) — consistent with most having moved back to `queued`. Monitor: do they re-deploy successfully, or do they re-enter gate_blocked immediately? If they re-block within one cycle, the retry is pointless thrash — needs a confidence-decay coupling.

### Fix 3 — Windowed metrics (recent_1h / recent_30min)
- **Evidence**: snapshot `learner` block contains all six fields:
  - `recent_1h_ok=0, recent_1h_fail=2, recent_1h_success_rate=0.0`
  - `recent_30min_ok=0, recent_30min_fail=0, recent_30min_success_rate=0.0`
- **Verdict**: **Landed.** Immediately useful: 30-min window is completely quiet, 1h has 2 residual failures. This tells us more than `today_success_rate=0.30` (which is poisoned by morning ghost-rule events).

## 4. New Regressions / Concerns

### HIGH — Previous-run snapshot had `vast: api_fail` ("No such file or directory: 'vastai'")
- **Evidence**: `fleet_health_prev.json` shows `vast.status=api_fail, rc=-1`, full vast block empty, yet current snapshot (16 seconds later) has vast fully populated. Collector ran twice back-to-back; the first run did not have `vastai` on PATH. The `*/15` cron almost certainly runs with a minimal environment — this is likely a **real recurring blind spot: every 15-min cron snapshot may be flying blind on Vast** depending on whether PATH inherits the user shell.
- **Ask**: check crontab PATH for `fleet_health_snapshot.py`. If cron env lacks the Vast CLI path, half the snapshots in the day are lying about Vast state. The current one ran from the supervisor's interactive shell, which is why vast is visible now.

### MEDIUM — 2 unaccounted-for learner failures in last 1h, invisible to watcher
- **Evidence**: `recent_1h_fail=2`, `recent_30min_fail=0` → the 2 failures landed between 15:30 and 16:00 UTC, pre-watcher-restart at 16:23. Reconciliation correctly classifies them outside the window (before cutoff was 15:00 for VERIFY_FAIL, 16:14 for gate-block suppression). They are therefore **knowingly excluded**. This is honest accounting, not drift.
- **Action**: none — but these 2 must not linger as `today_fail=16` forever. The `since_fix_ts` metric (my prior suggestion) would cleanly separate them.

### LOW — Watcher log only shows start lines, no heartbeat
- **Evidence**: `logs/deploy_watcher.log` has 2 lines total, both "deploy_watcher starting — N historical deploys skipped". No periodic "alive" heartbeat. If the watcher wedges on a regex match or a Claude CLI hang, we won't notice until the next supervisor review.
- **Suggestion**: emit a heartbeat line every N minutes, or an "idle, last event at X" line on each scan. Currently distinguishable only by `pgrep`.

### LOW — `today_success_rate=0.30` still poisoned; no `since_fix_ts` yet
- Same finding as last review; not regressed, just not-fixed-yet. Windowed metrics partly compensate. Would still prefer a first-class field.

### LOW — Rule-count history not snapshotted
- Still impossible to verify from the snapshot alone that all 11 purged rules were ghosts. Deactivated-rule list should be in snapshot for auditability.

## 5. Suggested Learnings for AgentLearner

1. **Cron PATH for fleet_health_snapshot.py** — verify `vastai` resolves in the cron environment; add explicit `PATH=...` in crontab or use absolute path. If half our supervisor snapshots are `vast.status=api_fail`, the review cadence is effectively half. (Confidence: 0.95, pure observability.)
2. **Watcher liveness heartbeat** — emit `deploy_watcher heartbeat: alive, last_event=T, queue_seen=N` every 5 min to `deploy_watcher.log`. Makes wedge vs idle distinguishable. (0.90)
3. **gate_blocked retry outcome tracking** — when a retry fires, instrument the next decision on that task: did it re-block? If yes within 2 cycles, mark the blocking rule's confidence *= 0.5 automatically. (0.80 — matches "cure worse than disease" concern, now testable since 6 retries just fired.)
4. **Reconciliation write-age watchdog** — if `reconciliation.age_s > 2400` (cron missed two ticks), flag `reconciliation.stale=true` loudly in snapshot. Currently stale=false computed; codify the threshold. (0.85)
5. **`since_fix_ts` field on today_* counters** — promote from last round's suggestion; still unmet. (0.90)

## 6. Verdict

**YELLOW-green, trending green.** All three prior fixes are honestly in place (gate_blocked retry firing is the strongest positive signal — 6 timed retries at the exact 6h boundary). Reconciliation invariant healthy but untested against a live failure. Vast collector has an intermittent PATH regression that needs one-line crontab fix before I'd call the whole pipeline GREEN. Watcher is armed but unexercised — not yet proven, just plausibly healthy.

Not-yet-green until: (a) Vast-in-cron PATH confirmed, (b) one real post-16:23 deploy failure flows through watcher → reconciliation → supervisor cleanly with orphan_count still 0.

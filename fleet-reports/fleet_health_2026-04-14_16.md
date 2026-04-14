# Fleet Health Review — 2026-04-14 16:18 UTC

## 1. Fleet Pulse

- **Vast.ai**: 4 instances (down from 7 — healthy consolidation after the Titan RTX ghost-rule cleanup). 3 running (A100 PCIE + Tesla P40 + Titan RTX, all util ~94–99 %), 1 RTX 3090 freshly allocated (uptime=0, status=null — not yet up). Total $1.60/hr (was $2.20). `n_zombie_suspect=0`.
- **util field WORKS**: 93.99 / 99.99 / 97.99 on the three running boxes. Null only on the brand-new 3090 which hasn't booted — expected. Previous hypothesis that collector was broken was correct; today's fix landed cleanly.
- **Fleet Manager**: alive, PID 122330 (restarted 16:14 UTC), cycle 2222 at 16:16. Cycle-2221 was 16:13 pre-restart, cycle-2222 is 16:16 post-restart → **restart was clean, no startup crash, took one cycle to re-enter main loop**.
- **Queue**: 2 running, 5 queued, 6 gate_blocked (unchanged vs prev), 1 planned, 42 failed (no new failures in queue table). completed=271.
- **Learner**: 84 decisions / 75 outcomes, today 7 OK / 16 fail (0.30 success). **active_rules collapsed 13 → 2** — exactly the ghost-rule purge we expected. Only the pre-existing diffdock_screen×RTX 3090 avoid + one other rule remain.
- **NIMs daemon**: active, heartbeat fresh (1 min stale), currently running `t1_molmim_pfn1_actin`. **jobs_done: 1 → 2 in last hour, total outcomes file 9 → 10 lines** (CFL1 finished 14:17, 852 s). All 10 recent outcomes = success. Tier-1 backlog IS advancing but slowly (~1 job / 15 min).
- **Modal**: `not_implemented` — unchanged.
- **Local GPUs (GB10 / RTX 6000)**: still not wired — supervisor blind.

## 2. Anomalies

### HIGH — Watcher still not capturing verify-fail events
- **Signal**: `today_fail` is 16 in current snapshot vs 12 in prev 15:24 report (+4 more failures). `deploy_assertions.jsonl` still has exactly **1 line** (from 13:09 UTC). `llm_diagnoses/` still has exactly **1 diagnosis** (same task, 13:09). No new diagnostic artifacts since 15:09 despite 4+ additional learner-recorded failures.
- **Hypothesis (revised)**: Either (a) the watcher patch that "also tails FAILED verification events" is live but none of those 4 failures produced a `FAILED verification` log line (they were gate_blocked rejections / pre-deploy aborts instead), or (b) the 16 vs 12 delta is partly accounting drift from the gate-match fix (old ghost-rule-induced fake outcomes being **replayed** into today's counters when the learner was restarted). Very important to disambiguate.
- **Action**: grep `fleet_manager.log` for the 4 new outcome rows since 15:24, cross-check whether their `outcome_type` is `gate_blocked_synthetic` / `ghost_rule_replay` vs a real deploy event. If they're stale ghosts, `today_fail` counter needs to be re-baselined (otherwise success rate is permanently poisoned). If they're real, watcher patch is incomplete.

### MEDIUM — today_success_rate stuck at 0.30, not recovering
- **Signal**: prev report 0.37 → now 0.30. Three hours of fixes, zero improvement in the rolling metric. today_ok unchanged at 7.
- **Hypothesis**: The today-counter is cumulative across the full 24 h window and cannot visibly recover until tomorrow UTC rollover even if every subsequent deploy succeeds. But if the +4 new failures are real (not ghost replays), then the post-fix regime is still producing failures at the same rate.
- **Action**: add a `today_success_rate_since_fix` metric keyed on `collected_at >= 16:14 UTC` so we can tell whether post-restart behavior is actually better; the current metric is not actionable during the repair window.

### MEDIUM — New RTX 3090 (id 34917766) freshly allocated at $0.10/hr, uptime=0, status=null
- **Signal**: dph=0.10, uptime_min=0, util=null, status=null. This is a **just-rented instance** that hasn't phoned home yet.
- **Why it matters**: exactly the shape of "null util + low uptime" is benign and must NOT trigger the new zombie_suspect rule. Current snapshot says `zombie_suspect=false` → good, the `uptime>15min AND util<=2` gate correctly ignores it. Keep watching: if uptime crosses 15 and util is still null at 16:33+, that is the first real zombie test of the new instrumentation.
- **Action**: no action now; flag for next review.

### LOW — gate_blocked queue depth stable at 6, none advancing
- **Signal**: `gate_blocked=6` both prev and current. With the new "don't overwrite gate_blocked to queued, don't record false outcome" fix, those 6 tasks are now correctly parked. But they are also **not being retried** — the cure must include a retry path, otherwise they sit forever.
- **Hypothesis**: No retry policy for gate_blocked yet. The learner blocks the initial match but there's no exponential-backoff re-evaluation.
- **Action**: wire a per-task `gate_blocked_retry_after` timestamp (e.g. 1 h) and have fleet_manager sweep gate_blocked → queued when the gate conditions no longer match (e.g. GPU class changed, rule deprecated, confidence decayed). Otherwise the cure **is** worse than the disease: 6 tasks silently stuck.

### LOW — Active rule count 13 → 2: confirm no good rules got purged
- **Signal**: 11 rules were deactivated as ghosts. Remaining 2 include the "diffdock_screen × RTX 3090 AVOID ssh_unreachable" rule (pre-dated the ghost episode, legitimate). Other rule not dumped in snapshot — can't fully audit.
- **Action**: dump full rules table (active + deactivated) into the next snapshot so the reviewer can spot-check that deactivations were all synthetic-Titan-RTX artifacts, not a real signal accidentally killed.

## 3. Regressions vs Last Run (54-min delta, 15:24 → 16:18)

| Metric | Prev (15:24) | Now (16:18) | Δ | Note |
|---|---|---|---|---|
| Vast instances | 7 | 4 | -3 | Titan RTX extras destroyed? Consolidated? Confirm intentional |
| $/hr | 2.20 | 1.60 | -0.60 | Good |
| Vast util visible | 0/7 | 3/4 | FIXED | New field live |
| n_zombie_suspect | field missing | 0 | NEW | Field wired |
| Queue running | 3 | 2 | -1 | |
| Queue gate_blocked | — | 6 | NEW | Now exposed (good) |
| Queue failed | 42 | 42 | 0 | No new queue failures |
| today_ok | 7 | 7 | 0 | Stuck |
| today_fail | 12 | 16 | +4 | Investigate (ghost replay vs real) |
| today_success_rate | 0.37 | 0.30 | -0.07 | Metric poisoned during repair window |
| outcomes_total | 71 | 75 | +4 | Matches +4 fails |
| active_rules | 2 | 2 | 0 (*) | But 13 → 2 earlier today; 11 ghosts purged |
| deploy_assertions lines | 1 | 1 | 0 | **Watcher STILL has 1 assertion ever** |
| llm_diagnoses files | 3 (1 incident) | 3 | 0 | No new diagnoses |
| NIMs jobs_done | 5 | 10 | +5 | Tier-1 pack advancing |
| NIMs recent_fail | 0 | 0 | 0 | |
| Fleet mgr cycle | 2212 | 2222 | +10 | Healthy (incl. clean restart) |

(*) snapshot reports 2 both times; the 13→2 purge happened between snapshots. The field itself is not a regression but the count trace is not logged — add a rule-count history.

## 4. Suggested Learnings for AgentLearner (human-approve)

1. **Ghost-rule early warning** — if `active_rules` grows by >3 in any 30-min window AND all new rules share the same `gpu_class`, freeze the learner's rule-formation and alert before the 4th fires. (Prevents the 11-rule cascade from happening again.)
   - Confidence: 0.85 — cheap insurance, would have caught this morning's bug in the first 20 min.

2. **gate_blocked staleness monitor** — any task stuck in `gate_blocked` > 1 h without a retry attempt should be auto-requeued with the blocking rule's confidence temporarily decayed 50 %.
   - Confidence: 0.80 — prevents the "cure worse than disease" failure mode. Needs a soft cap (max 2 requeues) so we don't spin.

3. **`today_success_rate` with a `since_fix_ts`** — splitting the metric into pre/post any fleet_manager restart makes repair-window effectiveness visible in near-real-time.
   - Confidence: 0.90 — pure observability, no risk.

4. **Watcher coverage assertion** — for every learner outcome with `success=false`, the watcher must have emitted a matching `deploy_assertions.jsonl` row OR a `gate_blocked` row within ±5 min. Missing = flag `unobserved_by_watcher` (same as yesterday's suggestion, re-flag because it now has evidence: 4 invisible failures in the last hour).
   - Confidence: 0.90 — promote from yesterday's "suggested" to "urgent".

5. **Ghost-rule unit test** — add a regression test: dispatch a task with `task_type=diffdock_screen_v2` against an instance with `gpu_class=Titan RTX` and assert the "diffdock_screen AND RTX 3090" rule does NOT match. (Codifies today's fix so the learner can't regress.)
   - Confidence: 0.95 — pure test, zero risk.

## 5. What the Supervisor STILL Can't See

- **Modal lane**: `not_implemented`. If a Modal job fails, supervisor has no signal at all.
- **moltbot disk space**: heartbeat says "running" but doesn't expose `df -h /home/bryzant`. If NIMs output dir fills up, we'll learn about it from a job failure, not from a capacity alert.
- **moltbot systemd journal**: only `systemctl_active` is pulled. A unit that restart-loops every 30 s still reports `active` — need `ActiveEnterTimestamp` + restart count.
- **Local GPUs (GB10, RTX 6000)**: not wired. Zero visibility.
- **Rule history**: only current active rules snapshotted. Deactivated rules and rule-formation events are not in `fleet_health.json` — can't audit the 13→2 purge from the snapshot alone.
- **Learner outcome → watcher assertion join**: no join key between the two streams, so we can't automatically detect "outcome arrived but watcher never saw the deploy" (the exact blind spot that hid today's ghost-rule loop for hours).
- **Vast instance ↔ task_id binding**: snapshot lists instances and queue separately; if a task runs on GPU X and that GPU later gets re-rented for a different task, the supervisor can't reconstruct which task "owned" that burn-hour.
- **No `since_last_restart` counter on fleet_manager** — on the 16:14 restart, the cycle counter (2222) is process-lifetime, not since-boot, which is fine but the snapshot doesn't record the restart timestamp. If fleet_manager restart-loops overnight, this review flow wouldn't catch it.

---

STATUS: YELLOW-improving — util visibility fixed, ghost-rule cascade purged cleanly (13→2), fleet_manager restart was clean, NIMs tier-1 advancing (5 new jobs in the hour, all success). BUT deploy_watcher still has only 1 assertion ever despite 4 new learner failures in the last hour — the fix for `FAILED verification` tailing is either not live or those 4 failures bypassed the deploy stage entirely (likely gate_blocked synthetic outcomes replayed as learner fails). today_success_rate stuck at 0.30 and cannot recover today. 6 gate_blocked tasks with no retry path — cure-worse-than-disease risk. Not green until (a) watcher assertions start flowing or we confirm they're not expected to, (b) gate_blocked retry policy lands.

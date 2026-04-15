# Fleet Reconciliation Report — 2026-04-15T16:15:01.712936+00:00

**Window**: ±300s match, 24h lookback.

## Status: 🔴 DRIFT DETECTED

- Deploy failures in learner: **25**
- In reconcile window (after cutoffs): **25**
- Matched by watcher: **16** ✓
- Orphan outcomes (learner failure, no watcher row): **9** ⚠️
- Watcher fails without outcome: **0**

## Orphan outcomes (failures the watcher did NOT see)

- `validator_2026-04-15_diffdock_limk2_10mol` on GPU 34979256 at 2026-04-15 07:20:14 — type=diffdock_screen — `verify_fail: no summary.json produced`
- `validator_2026-04-15_diffdock_limk2_10mol` on GPU 34979254 at 2026-04-15 07:15:18 — type=diffdock_screen — `verify_fail: no summary.json produced`
- `idh1_p3_selectivity_panel` on GPU 34929019 at 2026-04-14 18:57:44 — type=diffdock_screen — `verify_fail: diffdock produced 0 poses (silent failure)`
- `p4a_diffdock_rock2_clean_chemistry` on GPU 34929019 at 2026-04-14 18:50:23 — type=diffdock_screen — `verify_fail: diffdock produced 0 poses (silent failure)`
- `p3_diffdock_ncald_novel` on GPU 34929019 at 2026-04-14 18:42:56 — type=diffdock_screen — `verify_fail: diffdock produced 0 poses (silent failure)`
- `p1a_diffdock_limk2_admet_top100` on GPU 34929019 at 2026-04-14 18:35:24 — type=diffdock_screen — `verify_fail: diffdock produced 0 poses (silent failure)`
- `p3_diffdock_ncald_novel` on GPU 34929019 at 2026-04-14 18:18:58 — type=diffdock_screen — `verify_fail: diffdock produced 0 poses (silent failure)`
- `p1a_diffdock_limk2_admet_top100` on GPU 34929019 at 2026-04-14 18:11:19 — type=diffdock_screen — `verify_fail: diffdock produced 0 poses (silent failure)`
- `p3_diffdock_ncald_novel` on GPU 34929019 at 2026-04-14 16:29:12 — type=diffdock_screen — `verify_fail: diffdock produced 0 poses (silent failure)`
# Fleet Reconciliation Report — 2026-04-15T18:45:01.900520+00:00

**Window**: ±300s match, 24h lookback.

## Status: 🔴 DRIFT DETECTED

- Deploy failures in learner: **18**
- In reconcile window (after cutoffs): **18**
- Matched by watcher: **14** ✓
- Orphan outcomes (learner failure, no watcher row): **4** ⚠️
- Watcher fails without outcome: **0**

## Orphan outcomes (failures the watcher did NOT see)

- `validator_2026-04-15_diffdock_limk2_10mol` on GPU 34979256 at 2026-04-15 07:20:14 — type=diffdock_screen — `verify_fail: no summary.json produced`
- `validator_2026-04-15_diffdock_limk2_10mol` on GPU 34979254 at 2026-04-15 07:15:18 — type=diffdock_screen — `verify_fail: no summary.json produced`
- `idh1_p3_selectivity_panel` on GPU 34929019 at 2026-04-14 18:57:44 — type=diffdock_screen — `verify_fail: diffdock produced 0 poses (silent failure)`
- `p4a_diffdock_rock2_clean_chemistry` on GPU 34929019 at 2026-04-14 18:50:23 — type=diffdock_screen — `verify_fail: diffdock produced 0 poses (silent failure)`
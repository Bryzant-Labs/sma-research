# Fleet Reconciliation Report — 2026-04-16T00:15:01.819579+00:00

**Window**: ±300s match, 24h lookback.

## Status: 🟢 HEALTHY

- Deploy failures in learner: **7**
- In reconcile window (after cutoffs): **7**
- Matched by watcher: **5** ✓
- Orphan outcomes (learner failure, no watcher row): **2** 
- Watcher fails without outcome: **0**

## Orphan outcomes (failures the watcher did NOT see)

- `validator_2026-04-15_diffdock_limk2_10mol` on GPU 34979256 at 2026-04-15 07:20:14 — type=diffdock_screen — `verify_fail: no summary.json produced`
- `validator_2026-04-15_diffdock_limk2_10mol` on GPU 34979254 at 2026-04-15 07:15:18 — type=diffdock_screen — `verify_fail: no summary.json produced`
# bbb5 (`genmol_119_bbb_5`)

**Status**: CHARACTERIZED
**Verdict**: **Dual LIMK2/ROCK1 inhibitor** — NOT LIMK2-selective. Binds ROCK1 stronger than LIMK2.
**Priority**: MEDIUM (backup candidate only)

## Story

`bbb5` was initially a promising LIMK2 hit from GenMol. 100 ns validated MD + MMPBSA re-scoring showed it binds ROCK1 with higher affinity than LIMK2, disqualifying it from the LIMK2-selective track. Useful as a **dual-inhibitor control** for the ROCK–LIMK2–CFL2 axis.

## Data

- `bbb5_selectivity_FINAL.json` — Final selectivity verdict
- `mmpbsa/` — Complete MMPBSA energy tables and selectivity summary
  - `LIMK2_bbb5_100ns_VALIDATED_MMPBSA_*` — Validated 100 ns run
  - `LIMK2_bbb5_POCKET_FIXED_MMPBSA_*` — Pocket-fixed comparison
  - `LIMK2_bbb5_holo_MMPBSA_*` — Standard holo run
  - `ROCK1_bbb5_selectivity_MMPBSA_*` — ROCK1 reference
  - `LIMK1_bbb5_selectivity_MMPBSA_*` — LIMK1 reference
  - `selectivity_summary.json` + `mmpbsa_report.txt`

## Finding

[`../../findings/2026-04-09/FINDING_2026-04-09_bbb5_dual_LIMK2_ROCK1.md`](../../findings/2026-04-09/FINDING_2026-04-09_bbb5_dual_LIMK2_ROCK1.md)

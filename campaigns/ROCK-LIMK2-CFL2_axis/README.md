# ROCK–LIMK2–CFL2 Axis

**Status**: **VALIDATED** across 3 independent datasets
**Priority**: CRITICAL (core therapeutic axis for SMA)
**Started**: 2026-03-24

## Hypothesis

> SMN deficiency → ROCK2 hyperactivation → LIMK phosphorylation → cofilin inactivation → actin-rod formation → axonal-transport block → motor-neuron death

## Evidence

- LIMK2 is **+2.81×** in SMA motor neurons
- CFL2 is **disease-specific**: UP in SMA, DOWN in ALS
- PFN2 is **+1.22 log2FC** MN-enriched
- Zero competitors in the LIMK2-selective drug-space globally

## Compounds characterized

| Compound | Binding | Verdict |
|---|---|---|
| Fasudil | ROCK1/2 inhibitor (approved JP) | Muscle-mediated, not neuroprotective (Bowerman 2012) |
| bbb5 (`genmol_119_bbb_5`) | Dual LIMK2/ROCK1 | See [`../bbb5_dual_LIMK2_ROCK1/`](../bbb5_dual_LIMK2_ROCK1/) |
| 14 PocketXMol hits | LIMK2-selective (margin > 0.3) | See [`../PocketXMol_LIMK2_selective/`](../PocketXMol_LIMK2_selective/) |

## Contents

- `data/md_results_summary.json` — Aggregated MD run summary
- `md-simulations-2026-04-10/` — 2026-04-10 holo/reference simulations for LIMK1, LIMK2, ROCK1, ROCK2 with BMS5, LIMKi3, bbb5, Fasudil, and genmol_119_bbb_0

## Related findings

- [`../../findings/2026-04-09/FINDING_2026-04-09_bbb5_dual_LIMK2_ROCK1.md`](../../findings/2026-04-09/FINDING_2026-04-09_bbb5_dual_LIMK2_ROCK1.md)

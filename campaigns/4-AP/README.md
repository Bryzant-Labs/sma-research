# 4-Aminopyridine (4-AP) Campaign

**Compound**: `Nc1ccncc1` (MW 94, FDA-approved for MS walking difficulty)
**Started**: 2026-04-02
**Status**: **CORRECTED (2026-04-06)** — see `2026-04-06_correction/`
**Current verdict**: Kv-channel compensation for proprioceptive motor-neuron dysfunction (Simon's hypothesis). **NOT** a CORO1C multi-target agent.
**Priority**: HIGH

## Story

1. **April 2** — Original screen: DiffDock flagged CORO1C as rank-1 of 378 pairs (confidence +0.251). 18 GPU analyses, ~500 GPU-hours, MD trajectories on CORO1C, Kv1.2, SMN2 pre-mRNA, FEP, SMD, analog design (73 MolMIM + 500 GenMol), full ADMET (BBB 79%, bioavail 94%). See `2026-04-02_original_screen/`.
2. **April 6** — CORRECTION: GSE287257 scRNA-seq showed CORO1C is NOT motor-neuron-enriched (p=0.52). PFN2 and LIMK1 are the real MN actin genes. At MW 94, 4-AP is flagged by ADMET v2 as a fragment-artifact candidate. See `2026-04-06_correction/correction_notice.md`.
3. **April 10** — Paper reframe: Simon's proprioception hypothesis + connection to the 14 LIMK2-selective hits. See `2026-04-10_updates/`.

## What is still valid

- Kv1.2 100 ns MD binding (positive control)
- ADMET profile (BBB 79%, bioavail 94%, hERG 12%, AMES 55%)
- Pipeline methodology
- 6 publication figures (see `/figures/4AP/`)

## What is retracted

- CORO1C as a therapeutic target
- Multi-target SMA claim
- Direct SMN2 binding (0 stable contacts in 2026-04-10 follow-up MD)

## Pending work

- MMPBSA on existing Kv1.2 100 ns trajectory (raw `.dcd` in Dropbox)
- Contact-map analysis on Kv1.2 trajectory
- CFL2 trajectory analysis (211 MB file, sits in Dropbox)
- Paper reframe with Simon + LIMK2 connection

## Trajectories

Large `.dcd` files live in Dropbox (`Dropbox/SMA/GPU-Results-Trajectories/4AP_*.dcd`) — see [`docs/data_access.md`](../../docs/data_access.md).

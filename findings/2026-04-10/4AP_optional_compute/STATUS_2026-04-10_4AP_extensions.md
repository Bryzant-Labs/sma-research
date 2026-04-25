# 4-AP Extension Experiments — Deployment Status

**Date**: 2026-04-10 (deployment 20:25–21:52 UTC)
**Status**: RUNNING
**Instance**: Vast.ai RTX 3090 `34571669` (ssh1.vast.ai:11668), $0.1127/hr, California

## What was deployed

Three DiffDock v1.1 batches testing 4-AP and its sister-compound 3,4-DAP (Firdapse) against target sets NOT covered by the April 2 campaign:

1. **batch_4ap_regeneration** — 4-AP vs BDNF/TrkB/STAT3/PTEN/mTOR-FRB (Simon's "lässt Nerven wachsen" angle)
2. **batch_4ap_kv1_family** — 4-AP vs Kv1.1/Kv1.3/Kv1.5 (side-effect/selectivity panel; Kv1.2 already has 100ns MD)
3. **batch_34DAP** — 3,4-Diaminopyridine (Firdapse) vs the combined 13-target panel, to answer "is DAP a better candidate than 4-AP?"

## Methodology (matches April 2 campaign)
- DiffDock v1.1 (gcorso/DiffDock), 10 samples per complex, `--no_final_step_noise`, batch 10
- ESM2-t33-650M language-model embeddings
- PDB targets downloaded fresh from RCSB; GAP43 and STMN2 had no AlphaFold model available (intrinsically disordered — excluded from database) and were skipped
- Each docking ~80–100 s on RTX 3090, so full run ≈ 30–35 min compute

## Live preliminary results (batch 1 COMPLETE)

| Target | PDB | DiffDock conf. | Interpretation |
|---|---|---:|---|
| BDNF (growth factor) | 1BND | −2.96 | No binding — 4-AP too small for neurotrophin pocket |
| TrkB kinase domain | 4ASZ | **−0.19** | Moderate — kinase ATP-pocket fit; not strong enough to claim binding |
| STAT3 SH2 | 1BG1 | **−0.16** | Moderate — possible pocket fit |
| PTEN phosphatase | 1D5R | −0.38 | Weak |
| mTOR FRB | 4DRI | **−0.17** | Moderate — FRB pocket fit |

**Scale** (from April 2 campaign): > 0 = strong (CORO1C artefact was +0.25), −1 to 0 = moderate, < −1.5 = no binding.

Two preliminary notes:
1. **4-AP does NOT strongly bind any classical regeneration target.** Confidence values cluster at weak-moderate (−0.15 to −0.4). This is consistent with 4-AP being a selective Kv1 blocker, not a pleiotropic growth-factor mimetic. It partially NEGATIVES the "lässt Nerven wachsen" direct-target angle at the molecular-docking level.
2. **Three targets show non-trivial pocket fit (TrkB, STAT3, mTOR FRB).** These are not selective binding — just "the pocket is big enough to hold this 94-Dalton fragment" — but warrants flagging. The 4-AP fragment artefact noted in the April 6 correction applies here.

Batches 2 and 3 in progress — live data under `/results/diffdock_4ap_ext/` on the instance and will be synced when complete.

## Cost and timing

| Item | Value |
|---|---|
| Hourly rate | $0.1127/hr |
| Setup time (install + SO3 precompute + ESM2 download + test run) | ~2.3 h |
| Compute batch (ETA) | ~35 min |
| Budget used | ~$0.35 of $8 allocated |
| Budget remaining | ~$7.65 |

## What to do when complete

1. Run `bash ~/gpu-fleet/scripts/sync_4ap_extensions_results.sh` — fetches summary.json + rank-1 SDFs to both `gpu-fleet/` and `Dropbox/findings/2026-04-10/4AP_optional_compute/`
2. Review `batch_34DAP/summary.json` — the critical comparison of 3,4-DAP vs 4-AP on identical targets
3. Write `FINDING_2026-04-10_4AP_regeneration_and_selectivity_panel.md` once all three summaries are in
4. Update `PROJECT_CATALOG.md` 4-AP section with new data paths
5. Stop or keep the instance — $0.1127/h so can stay up cheaply if more docking is planned

## Files

| File | Location |
|---|---|
| Driver script | `~/gpu-fleet/scripts/diffdock_4ap_extensions.py` |
| Sync script | `~/gpu-fleet/scripts/sync_4ap_extensions_results.sh` |
| Live results (remote) | `ssh1.vast.ai:11668:/results/diffdock_4ap_ext/` |
| Master log (remote) | `/results/diffdock_4ap_ext/master.log` |
| This status file | `Dropbox/SMA/findings/2026-04-10/4AP_optional_compute/STATUS_2026-04-10_4AP_extensions.md` |

## Notes / Setup pitfalls for next time

- **SO(3) table precomputation on first DiffDock import takes ~11 min on Vast.ai RTX 3090 instances** (not minutes but ~672 s of numpy loops). Subsequent imports load from `.so3_*.npy` cache in under a second. **Cache these files to a Dropbox blob and ship with the install script** — would save 15+ min per new instance.
- **NumPy 2.0 breaks pandas 2.0.3 binary compatibility.** Install torch first, then force `numpy<2.0 pandas==2.0.3`.
- **Thread oversubscription**: Vast.ai host shows 72 CPUs but guest has much fewer. Always set `OMP_NUM_THREADS=8 MKL_NUM_THREADS=8` to prevent spinning.
- **ESM2-650M download is 2.5 GB and can be slow** (~10 min). Also worth caching.
- **AlphaFold has no models for highly disordered proteins** (GAP43, STMN2 returned 404). Use small-fragment approach or skip.

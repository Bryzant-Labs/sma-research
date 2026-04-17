# LIMK2 Arm 1 Redesign — Handoff for Continuation (2026-04-17 17:01 UTC)

## Status summary

PocketXMol generation phase is running on Vast instance 35141611 (A100 SXM 40GB) under tmux session `pxm_arm1`:
- **Strategy A DONE**: 485 / 500 successful (15 bad)
- **Strategy B DONE**: 480 / 500 successful (15 bad, 5 incomplete)
- **Strategy C IN PROGRESS**: started 17:01 UTC, projected complete ~17:20 UTC

When C completes, file `/root/results_limk2_arm1/.complete` will be touched.

## To continue (one command)

```bash
cd /home/bryza/sma-research/qms/limk2_arm1_redesign
python3 orchestrate_redesign.py 2>&1 | tee logs/orchestrate_$(date -u +%Y%m%d_%H%M).log
```

This will:
1. Pull all SDFs from asxm (A/B/C directories) via rsync
2. Run RDKit filter + Lipinski + QED≥0.4 + BBB≥0.5 + strategy-specific (A/C: HBD 2-4; B: Tanimoto_LIMKi3 ≥ 0.3)
3. Build Boltz-2 affinity head YAMLs for all survivors
4. Run Boltz-2 affinity head on sma-h100-two (H100 PCIe self-host, `~10s` per compound)
5. Apply gate: `affinity_probability_binary > 0.3`
6. If ≥ 5 binders: run 15-kinase selectivity panel (`~15×N×3s` batched)
7. Apply gate: `z_LIMK2 > 0 AND sel_z > 0`
8. Write `LIMK2_ARM1_REDESIGN_RESULTS.md` (RESTORED or EXHAUSTED verdict)
9. Triple-LLM verify via `/home/bryza/gpu-fleet/scripts/triple_llm_verify.py`
10. If triple-LLM 3/3 PASS → update `LIMK2_NEW_STORY_FOR_SIMON.md` v3

**Budget estimate for scoring phase:** ~5-8 min total on sma-h100-two (if batch server idle).

## Key files ready

- `/home/bryza/sma-research/qms/limk2_arm1_redesign/orchestrate_redesign.py` — main runner
- `/home/bryza/sma-research/qms/limk2_arm1_redesign/filter_and_score.py` — filter cascade
- `/home/bryza/sma-research/qms/limk2_arm1_redesign/run_kinase_panel.py` — 15-kinase panel
- `/home/bryza/sma-research/qms/limk2_arm1_redesign/pocket_geometry.json` — anchor documentation
- `/home/bryza/sma-research/qms/limk2_arm1_redesign/4tpt_chainA_apo.pdb` — stripped chain A
- `/home/bryza/sma-research/qms/limk2_arm1_redesign/configs/config_{A,B,C}_*.yml` — PXM configs

## LIMK2_NEW_STORY update (when orchestrator finishes)

If RESTORED (≥ 5 final survivors):
- Replace Arm 1 REPLACEMENT section §1 with:
  "Arm 1 — LIMK2-αC ACTIVATOR (redesigned, {N} new leads, DRAFT v3)"
  List top-5 with SMILES + Ki + 95% PI + sel_z

If EXHAUSTED (< 5):
- Strengthen Arm 1 retraction:
  "Arm 1 redesign strategies A/B/C exhausted (2026-04-17 evening)"
  Point to `LIMK2_ARM1_REDESIGN_RESULTS.md` §6 honest verdict

In both cases: triple-LLM 3/3 PASS required before any external comms.

## Strategy A preliminary filter (from 485 mols, already computed)

| Gate | Retained |
|---|---:|
| Raw | 485 |
| RDKit valid unique | 485 |
| Lipinski Ro5 | 438 |
| QED ≥ 0.4 | 413 |
| BBB ≥ 0.5 | 147 |
| HBD ∈ [2, 4] (strategy A) | **27** |

Extrapolation (rough):
- Strategy C (same filter as A): likely ~25-30 survivors
- Strategy B (Tanimoto ≥ 0.3 vs LIMKi3): **high risk of 0-5 survivors** — prior library gen showed max Tanimoto ~0.2; strategy-B pocket shift (to 35H COM, distance 20 Å from prior pocket) may or may not bias toward LIMKi3-similar scaffolds.

**Plausible total pre-Boltz survivors across A+B+C: 50-70.**

Given prior library yielded 4 binders (binary prob > 0.3) from 99 BBB-filtered compounds (4%), a 50-70 new-filter cohort would expect 2-3 binders — **below the 5-threshold**. Honest retraction is the likely outcome unless strategy C or strategy B provide unexpectedly strong cohorts.

## Compute actually spent

- PXM env setup on Vast 35141611: ~10 min (mamba + pip torch 2.4.1 cu124 + pyg)
- PXM checkpoint relay via WSL: ~1 min
- PXM generation: ~60 min (actual, 3 strategies sequential on A100 SXM 40GB @ ~$0.89/hr = $0.89)
- **Total so far: ~$0.90** (well within $5 budget)

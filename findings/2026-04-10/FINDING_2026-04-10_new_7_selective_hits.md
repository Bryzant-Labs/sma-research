# Seven New LIMK2-Selective Hits from Overnight DiffDock Campaign (2026-04-09 → 04-10)

**Date**: 2026-04-10
**Status**: COMPUTATIONAL PRELIMINARY — needs wet-lab validation
**Campaign**: DiffDock v2.2 selectivity screen on PocketXMol DFG-out generation
**Compute**: 4 × Vast.ai GPUs overnight, ~8 h, ~$8 total
**License**: CC-BY-4.0

## TL;DR

Seven molecules from the PocketXMol DFG-out Type II library passed our LIMK2 selectivity filter (LIMK2 confidence − LIMK1/ROCK1 confidence ≥ 0.30, LIMK2 confidence ≥ −0.8). Combined with the previous session's seven hits, **we now hold 14 computational LIMK2-selective candidates** for triage, re-docking with pocket constraints, MD validation, and eventual wet-lab screening.

## Hits

Source: `drug_discovery/diffdock_selectivity/2026-04-09_chunks/gpu_34455192/selective_gpu0_start3261.json`

| # | mol_id | SMILES | LIMK2 conf | LIMK1 conf | ROCK1 conf | Margin |
|---|--------|--------|-----------:|-----------:|-----------:|-------:|
| 1 | 84_0   | `O=C(NCc1cccnc1-c1ccccc1)N1CCN2CC=C=C21` | −0.17 | −0.85 | −1.23 | **0.68** |
| 2 | 851_0  | `O=c1c2nc3cc4c(nc3c=2c2ccnc3cccc1c32)=c1ccccc1=N4` | −0.05 | −0.73 | −4.03 | **0.68** |
| 3 | 293_0  | `Nc1ncc(-c2ccc(-c3ccc4c(Cc5cccnc5)cccc4n3)cc2)cn1` | −0.68 | −1.48 | −1.22 | **0.54** |
| 4 | 987_0  | `CC1=C2C(=Nc3ccccc32)C=C1c1nc2c3c(nn(C)c3n1)C=C2` | −0.21 | −0.73 | −0.67 | **0.46** |
| 5 | 1019_0 | `COC(=O)c1cccc(-c2nccc(-c3ccccc3C(=O)O)n2)c1` | −0.51 | −0.97 | −1.87 | **0.46** |
| 6 | 307_0  | `Oc1cccc(Cn2c(NCCc3ccccc3)nc3c4ncccc4ccc32)c1` | −0.65 | −1.04 | −1.87 | **0.39** |
| 7 | 434_0  | `O=C1CN(c2ccccc2)c2ccccc2CN1CCc1cccc2ncccc12` | −0.86 | −1.19 | −2.05 | **0.33** |

**Selectivity margin** = LIMK2 confidence − max(LIMK1 confidence, ROCK1 confidence). Higher = more selective.

**DiffDock confidence is log-odds of pose correctness**, not binding affinity. A value near 0 means DiffDock is confident in the top-ranked pose; highly negative values mean the top pose is uncertain (either weak pocket binding, or multiple equally plausible modes). Hit ranking here is therefore comparative, not absolute.

## Combined candidate pool (n = 14)

| Campaign | n | Status |
|---|---|---|
| Session 1 (pre-2026-04-09): PocketXMol DFG-out + DiffDock screen | 7 | summarized in `mmpbsa/bbb5_selectivity_FINAL.json` context and earlier session logs |
| Session 2 (overnight 2026-04-09 → 04-10): DiffDock rescreen of new generative batches | 7 | this finding |
| **Total** | **14** | all passing margin ≥ 0.30 |

## Immediate Next Steps

1. **ADMET triage** (ADMET-AI). Drop anything failing two or more of: BBB, DILI, hERG, CYP3A4.
2. **Re-dock top-10 with DiffDock + pocket restraint** (POCKET_FIXED) to kill near-miss poses that drifted out of the ATP site.
3. **Short (10 ns) MD contact persistence** on top 3–5 surviving hits for LIMK2 vs LIMK1 vs ROCK1 — use the same amber14/GAFF2/TIP3P-FB protocol as the reference MDs in `md_sims/`.
4. **MMPBSA ddG** on surviving hits, comparing vs the BMS-5 and LIMKi3 reference runs (`md_sims/LIMK2_BMS5_POCKET_FIXED`, `md_sims/LIMK2_LIMKi3_POCKET_FIXED`).
5. **Novelty check** against ChEMBL / PubChem — discard anything within Tanimoto > 0.85 of a known LIMK2 inhibitor.
6. **Present top 1–3 remaining hits to Simon** with full evidence package (not preliminary scores).

## Caveats

- DiffDock confidence is pose-quality, not binding strength. Several hits carry unusual valence patterns in the SMILES (`c=2`, `=c1`, aromatic nitrogen patterns). These need RDKit sanitization + manual inspection before wet-lab purchase — some may be DiffDock-internal tautomer artifacts.
- Absolute selectivity has only been tested against LIMK1 + ROCK1. JAK2, ROCK2, and kinome-wide panels are still open.
- Pose SDFs live under `drug_discovery/diffdock_selectivity/2026-04-09_chunks/gpu_34455192/docked/` (mirrored to Dropbox for large files).
- This is **not a therapeutic claim**. It is a computational prioritization list pending orthogonal validation.

## Data Provenance

- Source molecules: `drug_discovery/pocketxmol/dfg_out_2026-04-09/` (batches 1, 2, 4; 7,275 molecules total).
- Docking: DiffDock v2.2 via NVIDIA NIM container, 40 samples per input.
- Selectivity panel: LIMK2 (PDB 4TPT, DFG-out), LIMK1 (3S95), ROCK1 (2ESM).
- Filter script: threshold 0.30 margin, LIMK2 confidence ≥ −0.8.
- Raw output: `selective_gpu0_start3261.json` and `all_results_gpu0_start3261.json` in the chunk directory.

## Citation

Open-source SMA drug-discovery platform — `Bryzant-Labs/sma-research`. Published under CC-BY-4.0.

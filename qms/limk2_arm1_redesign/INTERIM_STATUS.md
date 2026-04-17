# LIMK2 Arm 1 Redesign — Interim Status (2026-04-17 16:58 UTC)

## Progress (a): 1,500 molecules generation

- **Strategy A (Asp-activator DFG-oriented)**: COMPLETE — 485 / 500 successful (15 bad reconstructions).
- **Strategy B (LIMKi3 scaffold-seeded)**: IN PROGRESS — 386 / 500 at 16:57.
- **Strategy C (αC-Glu/DFG-Asp H-bond network)**: NOT YET STARTED. Queued after B.

Projected PXM completion: ~17:25 UTC.

Running on Vast instance 35141611 (sma-pxm-batch-20260417-asxm, A100 SXM 40GB).

## 4TPT verification

Title confirmed via RCSB: "Crystal Structure of the Human LIMK2 Kinase Domain In Complex With a Non-ATP Competitive Inhibitor".

Key residue re-mapping (task spec mentioned K383/T407/G408/T409/D460 — these do not match the 4TPT chain A numbering, which is UniProt-native). Actual anchors used:
- Catalytic β3-Lys: K360
- αC-Glu: E376
- HRD-Asp: D451
- DFG-Asp: D469
- Gatekeeper vicinity: T405
- 35H (LIMKi3 analog) ligand COM: [9.384, 7.372, 20.916] Å

## Pocket definitions

- **A** (activator DFG-oriented): [7.629, -8.294, 17.021], radius 10 Å
  (prior αC center [9.556, -12.361, 17.014] shifted 4.5 Å toward D469 Cα)
- **B** (LIMKi3 scaffold-seeded): [9.384, 7.372, 20.916], radius 10 Å
  (35H ligand COM from 4TPT co-crystal; 20 Å from prior αC pocket — totally distinct region)
- **C** (αC-E376 + DFG-D469 carboxylate H-bond network): [3.620, -8.196, 22.835], radius 8 Å
  (midpoint of E376 carboxylate and D469 carboxylate)

## Strategy A preliminary filter (485 mols complete)

| Gate | In | Out | Retained |
|---|---:|---:|---:|
| Raw PocketXMol | — | 485 | 100% |
| RDKit valid + unique canonical SMILES | 485 | 485 | 100% |
| Lipinski Ro5 | 485 | 438 | 90% |
| QED ≥ 0.4 | 438 | 413 | 85% |
| BBB ≥ 0.5 (Egan logistic) | 413 | 147 | 30% |
| HBD ∈ [2, 4] (strategy A requirement for Asp carboxylate H-bond) | 147 | 27 | 6% |

**Strategy A pre-Boltz survivors: 27 compounds** (from 485 = 5.6% yield).

Sample top survivors by QED:
- `31.sdf`: QED=0.51 BBB=0.54 HBD=2 Tanimoto_LIMKi3=0.100
  `O=c1nc(-c2ccc3[nH]c4ccncc4c3c2)cc(-c2ccccc2)[nH]1`
- `166.sdf`: QED=0.77 BBB=0.70 HBD=3 Tanimoto_LIMKi3=0.115
  `Oc1ccccc1CNC1=CNC2=CC=C(Oc3cccc[nH+]3)C=CC2=C1`
- `13.sdf`: QED=0.54 BBB=0.52 HBD=2 Tanimoto_LIMKi3=0.155
  `O=c1[nH]cnc2nc(C#Cc3ccccc3)nc(Nc3ccc(F)cc3)c12`
- `441.sdf`: QED=0.49 BBB=0.51 HBD=2 Tanimoto_LIMKi3=0.167
  `Cc1ccc2c(CNc3ncncc3C(=O)NCCc3ccccc3)ccnc2c1`

## Infrastructure ready

- `filter_and_score.py`: end-to-end filter + Boltz-2 affinity head scorer (tested on A)
- `run_kinase_panel.py`: 15-kinase selectivity Z-scorer
- `orchestrate_redesign.py`: orchestrator + RESULTS.md generator + HONEST RETRACTION path
- Boltz-2 LIMK2 calibration of record loaded: slope=1.249, intercept=3.549, RMSE=0.378, R²=0.690
- LIMK2 kinase domain sequence loaded (278 aa)
- 15-kinase panel sequences loaded
- sma-h100-two Boltz-2 self-host verified idle and ready (~10 s/job per Boltz-2 affinity head)

## Next steps (pending B+C completion at ~17:25)

1. Rsync all 1,500 SDFs back to local
2. Run `filter_and_score.py` → full filter cascade → Boltz-2 affinity head on all survivors
3. If ≥ 5 compounds pass `affinity_probability_binary > 0.3`: run 15-kinase panel
4. If ≥ 5 pass both affinity AND selectivity z-gates: write `LIMK2_ARM1_REDESIGN_RESULTS.md` as DRAFT + triple-LLM verify
5. Else: write HONEST RETRACTION documenting that redesign strategies A/B/C are exhausted
6. Update `LIMK2_NEW_STORY_FOR_SIMON.md` v3 with outcome

## Budget

- PXM on A100 SXM 40GB (Vast 35141611): ~60 min wall-clock, ~$0.85
- Boltz-2 affinity head self-host: $0 marginal
- Boltz-2 panel self-host: $0 marginal
- **Well within $5 task budget.**

## Hard rule compliance

- DRAFT only — external transmission BLOCKED.
- Protected instances 35120547 and 35120548 untouched.
- 4TPT title verified before starting.
- Honest retraction path exists (and will be triggered if < 5 survivors pass both gates).

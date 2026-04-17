# DUSP6 PocketXMol Inhibitor Campaign — RESULTS (DRAFT)

**Status**: VERIFIED — triple_llm_verify 3/3 PASS (OpenAI GPT-4o, Groq Llama-3.3-70B, Gemini 2.0 Flash) — 2026-04-17T08:56Z
**Campaign**: `dusp6_inhibitor`
**Date**: 2026-04-17
**Instance**: A100 SXM4-40GB, Slovenia, ssh2:10542, contract 35120543, $0.69/hr

## PDB Verification (MANDATORY — 3 of 3 PDB briefs today were wrong)

```
TITLE     CRYSTAL STRUCTURE OF PYST1 (MKP3)
HEADER    HYDROLASE                               11-JUL-98   1MKP
COMPND   2 MOLECULE: PYST1;
COMPND   4 FRAGMENT: CATALYTIC DOMAIN;
COMPND   5 SYNONYM: DUAL SPECIFICITY PHOSPHATASE, MAP KINASE PHOSPHATASE 3, MKP-3;
COMPND   7 EC: 3.1.3.48, 3.1.3.16;
SOURCE   2 ORGANISM_SCIENTIFIC: HOMO SAPIENS;
```

**PASS**: 1MKP = human DUSP6 / MKP-3 / PYST1, catalytic domain, chain A residues 204–347.

## Pocket derivation

DSP-fold catalytic pocket around **Cys287** (nucleophile) and **Arg283** (P-loop phosphate-stabilising arginine, spatially adjacent at 5.7 Å CA-CA — not the sequence-downstream Arg299 which sits 27 Å away on a surface loop).

- `pocket_center = [3.11, 65.40, 21.17]`
- `pocket_radius = 10.0 Å` (generator setting; 15.3 Å is the max distance for all 11 core residues)
- **Pocket residues (11)**: Gly232, Ile233, Lys234, Tyr235, Ala282, Arg283, Gly284, Lys285, Asn286, Cys287, Gly288

Script: `/results/pocketxmol/dusp6/derive_pocket.py`
JSON: `/home/bryza/sma-research/qms/dusp6_pocket.json`

## Generation run

| Metric | Value |
|---|---|
| Target n_molecules | 600 |
| batch_size | 50 |
| Generated | 600 |
| Unique SMILES | 423 (70.5 %) |
| RDKit-valid | 423 / 423 (100 %) |
| Smoke test | PASS (5 mols, 3 valid, 14.8 s) |
| Full run wall-time | ~4 min |
| **GPU utilisation** | **94 %** (A100 SXM4, 262 W draw) |
| VRAM used | 1.8 GB / 40 GB |
| tmux session | `pxm_dusp6` |

## Post-filter (BBB + QED ≥ 0.4 + Lipinski)

**92 / 423 (21.7 %) pass** BBB + QED + Lipinski triple-gate.

Filter gates: MW < 500, HBD ≤ 3, HBA ≤ 7, TPSA < 90 Å², logP ∈ [1, 4], QED ≥ 0.4, Lipinski.

## Top 5 by QED

| # | SMILES | MW | logP | TPSA | QED |
|---|---|---|---|---|---|
| 1 | `OC1CCCC[C@@H]2C=C(OCc3cccc4nnccc34)C[C@@H]3C1C32` | 336 | 3.85 | 55 | **0.925** |
| 2 | `C[C@H]1CCC(=O)C2=C3[C@@H](NN3C(OCCc3ccccc3)CC2)C1=O` | 340 | 2.38 | 59 | **0.912** |
| 3 | `Cc1cncc(C=CCN2CC3C(=N)[C@H](C)NCCC3C2=O)c1` | 312 | 1.88 | 69 | **0.895** |
| 4 | `Cc1cccc(Cc2cc(C)nc(NC(=O)N[C@H]3CC(=O)CCO3)c2)c1` | 353 | 3.12 | 80 | **0.885** |
| 5 | `COc1ccc2cc(CNC3=C[C@@H]4CCCC[C@H](C)C4NC3=O)oc2c1` | 354 | 3.74 | 64 | **0.878** |

All five drug-like, MW 312–354, BBB-compatible PSA, logP in neuro-optimal 1.9–3.9 range.

## Next steps (not yet executed)

1. **Top 100 Boltz-2 selectivity panel**: DUSP6 + SSH1 + SSH2 + SSH3 (phosphatase 4-panel → Z-score selectivity per compound per target).
2. **Cross-reference**: lookup hits against known DUSP6 tool compounds (BCI, NSC 95397, RR505) for scaffold novelty.
3. **Within-family selectivity add-on**: extend panel to DUSP1/4/5/7/9 (closer paralogues) once a Z-score hit shortlist is defined.

## Honest caveats

- **Apo crystal**: 1MKP is unliganded and in the inactive conformation (no ERK2 bound). Active-state pocket may differ; no native ligand → no per-target C_rel baseline.
- **Shallow DSP active site**: DSP fold is historically hard to drug with non-covalent compounds. Known DUSP6 inhibitors are allosteric (BCI) rather than active-site. Expect true-binder yield from an active-site generator to be low.
- **Non-covalent warheads**: PocketXMol does not generate covalent Cys-targeting electrophiles. Upper affinity ceiling is modest.
- **Cross-family panel, not within-family**: SSH1/SSH2/SSH3 are slingshot phosphatases (different fold). They test broad phosphatase selectivity but not the clinically critical within-DUSP selectivity (DUSP1/4/5/7/9).
- **Therapeutic direction UNRESOLVED**: DUSP6 up- vs down-regulation in SMA MN is model-system-dependent. This is exploratory compute, not a therapy claim (same hedge policy as CDK5 and LIMK2-ATP).

## Cost

- Wall-time: ~4 min generation + ~1 min filter = ~5 min
- Instance cost: $0.058
- Total campaign cost: ≈ $0.06

## File manifest

- Plan: `/home/bryza/sma-research/qms/dusp6_inhibitor_plan.md`
- Task JSON: `/home/bryza/sma-research/qms/dusp6_inhibitor_task.json`
- Pocket JSON: `/home/bryza/sma-research/qms/dusp6_pocket.json`
- Top filtered CSV: `/home/bryza/sma-research/qms/dusp6_inhibitor_top.csv`
- Summary JSON: `/home/bryza/sma-research/qms/dusp6_inhibitor_summary.json`
- Remote SDFs: `ssh2:10542:/results/pocketxmol/dusp6_inhibitor/SDF/`
- Remote full SMILES: `ssh2:10542:/results/pocketxmol/dusp6_inhibitor/molecules.smi`
- Remote full filtered CSV: `ssh2:10542:/results/pocketxmol/dusp6_inhibitor/filtered.csv`
- Run log: `ssh2:10542:/results/pocketxmol/dusp6_inhibitor_run.log`

# SMA-Score Ranker v1 — 2026-04-16

## Method
GradientBoostingClassifier over:
- RDKit descriptors (MW, logP, HBA, HBD, TPSA, rotatable, aromatic, heavy, fcsp3, aliphatic, ring count)
- Max + mean Tanimoto similarity to 15 literature-strict SMA-rescue / NMJ-beneficial compounds

## Training data
- **Positives (15):** Fasudil, Y-27632, Ripasudil, LIMKi3, BMS-5, bbb5, Belumosudil, Netarsudil, Risdiplam, Riluzole, Edaravone, 4-AP, 3,4-DAP, Pyridostigmine, Neostigmine
- **Negatives (500):** random kinase inhibitors pulled from ChEMBL (22,626 rows ingested across 25 kinases: LIMK1/2, ROCK1/2, JAK1-3, CDK1-6, MAPK1/3/14, SRC, ABL1, FYN, LCK, AKT1/2, GSK3B, MTOR, PAK1/2/4)

## Output
- 518 GenMol scaffold-hop compounds ranked by SMA-phenotype relevance probability
- Top-9 compounds pass both QED >0.69 AND SMA-score ~1.0 (Fasudil/LIMKi3/Ripasudil/BMS-5 family derivatives)

## Caveat (honest)
ROC-AUC 1.000 reflects that LIMK/ROCK scaffolds are well-separated from random kinase inhibitors in Morgan fingerprint space. v1 is a **first-pass filter**, not a nuanced predictor. Binary output (1.0 or ~1e-9) — usable as "gate" not "rank-within-pass" score.

## v2 next steps
- Add Boltz-2 iptm features (LIMK2/LIMK1/ROCK2 scoring currently queued for top 50)
- Add ChEMBL Ki as feature (matched by SMILES)
- Multi-class: phenotype-rescue vs off-target-dominant vs cytotoxic

## Strategic frame
This is Phase 1.1 of the SMA Orchestration Layer plan (plan-sma-orchestration-layer-2026-04-16). Replaces "fine-tune SMA-Boltz" with "light ranker over generic models" — data-feasible today, produces actionable output immediately.

## Files
- `sma_score_ranker.py` — training + scoring script
- `candidates_ranked.csv` — 518 compounds with sma_score + qed + source

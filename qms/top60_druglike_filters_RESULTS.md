# Top-60 Drug-Quality Filter Results

**Status:** INTERNAL — triple_llm_verify 3/3 PASS (2026-04-17). No external comms until human medchem review.
**Date:** 2026-04-17

## Method

### Dataset identity (pinned, verifiable)
- **LIMK2 source:** `/home/bryza/fleet-results/limk2_activator_alphaC/boltz2_kinase_panel.csv` (43 rows; derived from LIMK2-alphaC activator campaign, DFG-out 4TPT template, Boltz-2 15-kinase panel). Ranked by sum of `z_LIMK2` (prefer-target z-score) + `selectivity_z` (cross-kinase margin). Top 20 retained.
- **ROCK2 source:** `/home/bryza/fleet-results/rock2_activator_alphaC/boltz2_rescore_ranked.tsv` (23 rows; ROCK2 kinase-domain target, Boltz-2 rescore). Ranked by `iptm`. Top 20 retained. Note: this file's `bbb_filtered.csv` does not share a `canonical_smiles` column keyed on these SMILES, so BBB-pass conservatively = False for this arm (true status unknown, not a fail).
- **MDM2 source:** `/home/bryza/fleet-results/mdm2_activator_v2_allosteric/top100_by_cfd_pos.csv` (100 rows; MDM2 allosteric activator v2 campaign, cross-field design scoring). Ranked by `cfd_pos`. Top 20 retained. BBB-pass = `bbb_prob >= 0.5` from the source file.
- **Reference library (IP-novelty):** 5021 compounds total = 5000 potent ChEMBL kinase inhibitors (from `/home/bryza/fleet-results/chembl_ki/kinase_ki.parquet`, 22,626 total rows across 25 kinase targets; filtered pchembl_value >= 6 or standard_value_nm <= 10000; deduplicated by canonical_smiles; sorted by potency) + 21 curated literature MDM2/LIMK/ROCK drugs (Nutlin-3a, Idasanutlin, AMG-232, APG-115, Milademetan, RG-7388, SAR405838, MI-77301, SJ-172550, MK-8242, NVP-CGM097, HDM201, LIMKi3, LX-7101, BMS-5, Fasudil, Y-27632, H-1152, Belumosudil, AT13148, GSK269962A, Staurosporine).

### Filters and tools (pinned versions)
- **Software:** RDKit 2026.03.1 (PAINS via `rdkit.Chem.FilterCatalog`; ECFP4 via `AllChem.GetMorganFingerprintAsBitVect(radius=2, nBits=2048)`; Tanimoto via `DataStructs.TanimotoSimilarity`).
- **Filter 1 — PAINS:** RDKit FilterCatalog with PAINS_A, PAINS_B, PAINS_C catalogs separately (Baell & Holloway, *J. Med. Chem.* 2010, 53(7):2719-40). Severity = first match in order A > B > C.
- **Filter 2 — SA-score:** Ertl & Schuffenhauer, *J. Cheminf.* 2009, 1:8. Implementation: `rdkit/Contrib/SA_Score/sascorer.py` (shipped with RDKit; `fpscores.pkl.gz` reference database built from 1M PubChem compounds). Scale 1 (easy) to 10 (hard). Gate: SA <= 5 = commercially tractable.
- **Filter 3 — IP-novelty:** Max Tanimoto ECFP4 (radius=2, 2048 bits) of each query vs reference library. Gate: max Tanimoto < 0.4 = potentially novel chemotype; >= 0.4 = related to known drug, patent risk.
- **Composite wet-lab-ready score (max 9):** PAINS-free (+3) + SA <= 5 (+2) + Tanimoto < 0.4 (+2) + BBB-pass (+1) + QED >= 0.5 (+1).

### Reproducibility
- Script: `/home/bryza/sma-research/qms/top60_druglike_filters.py`
- Per-compound output: `/home/bryza/sma-research/qms/top60_druglike_filters_RESULTS.json` (all 60 rows with PAINS severity, SA, Tanimoto, nearest reference, QED, BBB, composite score).
- All SMILES canonicalized via `Chem.MolToSmiles(Chem.MolFromSmiles(...))` before fingerprinting.

## Summary (per arm)

| Arm | n | PAINS-free | SA<=5 | Tanimoto<0.4 | BBB-pass | QED>=0.5 | Wet-lab-ready (>=7) | Mean score |
|---|---|---|---|---|---|---|---|---|
| LIMK2_activator | 20 | 19 | 20 | 19 | 20 | 19 | 19 | 8.70 |
| ROCK2_activator | 20 | 17 | 17 | 20 | 0 | 15 | 15 | 7.00 |
| MDM2_activator_v2 | 20 | 19 | 20 | 20 | 20 | 14 | 19 | 8.55 |

**Composite wet-lab-ready distribution (all 60):**

| Score | Count |
|---|---|
| 9 | 32 |
| 8 | 18 |
| 7 | 3 |
| 6 | 1 |
| 5 | 4 |
| 4 | 1 |
| 2 | 1 |

## Top 5 wet-lab-ready — LIMK2_activator

| Rank | Score | SMILES | PAINS | SA | max_Tanimoto | nearest_ref | BBB | QED | src_rank |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **9/9** | `CS(=O)(=O)c1ccccc1-c1cccc(Oc2ccc(C(N)=O)cc2)c1` | free | 1.89 | 0.308 | chembl::PAK4::CHEMBL446500 | YES | 0.746 | 15 |
| 2 | **9/9** | `O=C(NCc1ccccc1)c1cnc(Oc2ccccc2)cc1O` | free | 1.95 | 0.351 | chembl::ROCK1::CHEMBL1922125 | YES | 0.754 | 13 |
| 3 | **9/9** | `Cc1cccc(NC(=O)c2cccc(Oc3ccncn3)c2)c1O` | free | 2.12 | 0.355 | chembl::LCK::CHEMBL408849 | YES | 0.718 | 3 |
| 4 | **9/9** | `NC(=O)c1ccnn1CCc1ccc(Oc2cccnc2)cc1` | free | 2.22 | 0.342 | chembl::PAK4::CHEMBL2207743 | YES | 0.758 | 5 |
| 5 | **9/9** | `COc1ccc(CN2CCc3c(ccnc3-c3cccnc3)C2=O)cc1` | free | 2.25 | 0.315 | chembl::GSK3B::CHEMBL361567 | YES | 0.728 | 18 |

### Rationale — LIMK2_activator

- **#1** (src_rank 15): PAINS-free; SA=1.89 (tractable); Tanimoto=0.308 vs chembl::PAK4::CHEMBL446500 (novel chemotype)
- **#2** (src_rank 13): PAINS-free; SA=1.95 (tractable); Tanimoto=0.351 vs chembl::ROCK1::CHEMBL1922125 (novel chemotype)
- **#3** (src_rank 3): PAINS-free; SA=2.12 (tractable); Tanimoto=0.355 vs chembl::LCK::CHEMBL408849 (novel chemotype)
- **#4** (src_rank 5): PAINS-free; SA=2.22 (tractable); Tanimoto=0.342 vs chembl::PAK4::CHEMBL2207743 (novel chemotype)
- **#5** (src_rank 18): PAINS-free; SA=2.25 (tractable); Tanimoto=0.315 vs chembl::GSK3B::CHEMBL361567 (novel chemotype)

## Top 5 wet-lab-ready — ROCK2_activator

| Rank | Score | SMILES | PAINS | SA | max_Tanimoto | nearest_ref | BBB | QED | src_rank |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **8/9** | `O=C1C(O)=N[N+](=Cc2ccccc2)N1c1ccccc1OCC(O)c1ccccc1` | free | 3.37 | 0.290 | chembl::PAK4::CHEMBL477514 | no | 0.621 | 18 |
| 2 | **8/9** | `O=C(O)c1cc([N+]#Cc2cccnc2)c2c(c1)N[N+](=Cc1ccccc1)C2` | free | 3.61 | 0.244 | chembl::JAK3::CHEMBL106944 | no | 0.686 | 15 |
| 3 | **8/9** | `COc1ccc(CCNNC2CCCC3C(=O)CCCC3C2N)cc1` | free | 3.77 | 0.306 | chembl::PAK4::CHEMBL163037 | no | 0.544 | 2 |
| 4 | **8/9** | `CC1CCCC(=CCNN2Cc3nccn4c3c(c3cc(N)ccc34)C2)C1=O` | free | 4.05 | 0.209 | chembl::ROCK1::CHEMBL1080071 | no | 0.543 | 7 |
| 5 | **8/9** | `Clc1ccc2c(n1)NC(NC1CCCc3c(nc4ccncnc3-4)C1)C2` | free | 4.07 | 0.215 | chembl::JAK2::CHEMBL121947 | no | 0.536 | 1 |

### Rationale — ROCK2_activator

- **#1** (src_rank 18): PAINS-free; SA=3.37 (tractable); Tanimoto=0.290 vs chembl::PAK4::CHEMBL477514 (novel chemotype)
- **#2** (src_rank 15): PAINS-free; SA=3.61 (tractable); Tanimoto=0.244 vs chembl::JAK3::CHEMBL106944 (novel chemotype)
- **#3** (src_rank 2): PAINS-free; SA=3.77 (tractable); Tanimoto=0.306 vs chembl::PAK4::CHEMBL163037 (novel chemotype)
- **#4** (src_rank 7): PAINS-free; SA=4.05 (tractable); Tanimoto=0.209 vs chembl::ROCK1::CHEMBL1080071 (novel chemotype)
- **#5** (src_rank 1): PAINS-free; SA=4.07 (tractable); Tanimoto=0.215 vs chembl::JAK2::CHEMBL121947 (novel chemotype)

## Top 5 wet-lab-ready — MDM2_activator_v2

| Rank | Score | SMILES | PAINS | SA | max_Tanimoto | nearest_ref | BBB | QED | src_rank |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **9/9** | `O=C(NCCn1cncn1)c1cccc(OCCc2ccc(F)cc2)c1` | free | 2.06 | 0.329 | chembl::PAK2::CHEMBL3804850 | YES | 0.675 | 19 |
| 2 | **9/9** | `O=C(Nc1ccc(-n2c(CCc3ccccc3)nccc2=O)cc1)c1ccc(O)cc1` | free | 2.11 | 0.329 | chembl::PAK2::CHEMBL3805630 | YES | 0.503 | 15 |
| 3 | **9/9** | `COc1ncc(-c2cccc(C(=O)O)c2)c(-c2ccccc2)c1O` | free | 2.17 | 0.333 | chembl::ROCK1::CHEMBL1982957 | YES | 0.763 | 10 |
| 4 | **9/9** | `N#Cc1ccc(Nc2nc(Oc3ccncc3)ccc2C(=O)O)cc1` | free | 2.28 | 0.271 | chembl::CDK2::CHEMBL359794 | YES | 0.735 | 1 |
| 5 | **9/9** | `O=C(C=Cc1ccc2c(c1)OCO2)Nc1ccc(-c2c[nH]nn2)cc1` | free | 2.59 | 0.263 | chembl::PAK2::CHEMBL3804923 | YES | 0.716 | 9 |

### Rationale — MDM2_activator_v2

- **#1** (src_rank 19): PAINS-free; SA=2.06 (tractable); Tanimoto=0.329 vs chembl::PAK2::CHEMBL3804850 (novel chemotype)
- **#2** (src_rank 15): PAINS-free; SA=2.11 (tractable); Tanimoto=0.329 vs chembl::PAK2::CHEMBL3805630 (novel chemotype)
- **#3** (src_rank 10): PAINS-free; SA=2.17 (tractable); Tanimoto=0.333 vs chembl::ROCK1::CHEMBL1982957 (novel chemotype)
- **#4** (src_rank 1): PAINS-free; SA=2.28 (tractable); Tanimoto=0.271 vs chembl::CDK2::CHEMBL359794 (novel chemotype)
- **#5** (src_rank 9): PAINS-free; SA=2.59 (tractable); Tanimoto=0.263 vs chembl::PAK2::CHEMBL3804923 (novel chemotype)

## Flagged compounds

### PAINS-A severity (2) — remove from consideration

| Arm | src_rank | SMILES | Match |
|---|---|---|---|
| ROCK2_activator | 9 | `OC12C3=CCCC1CC1CC(C=[N+]=Nc4ccccn4)CC(=NN3)C12` | azo_A(324) |
| ROCK2_activator | 10 | `Oc1ccc(CN2N=C(c3ccc(O)cc3)Nc3ccccc32)cc1` | hzone_phenol_B(215) |

### High SA-score (> 5) — synthesis-expert review needed (3)

| Arm | src_rank | SA | SMILES |
|---|---|---|---|
| ROCK2_activator | 8 | 5.63 | `Cc1cccc2c1[nH+]cn2C(O)=NCC1CC=C2C(C=C3C=CNC=N3)CCC21` |
| ROCK2_activator | 9 | 5.46 | `OC12C3=CCCC1CC1CC(C=[N+]=Nc4ccccn4)CC(=NN3)C12` |
| ROCK2_activator | 4 | 5.32 | `O=C1CCC=NC2CC3N[N+](Nc4ccc(=O)[nH]c4)=CCCC3C12` |

### Near-duplicate to known drug (Tanimoto >= 0.4) — patent risk (1)

| Arm | src_rank | Tanimoto | nearest_ref | SMILES |
|---|---|---|---|---|
| LIMK2_activator | 10 | 0.431 | chembl::MAPK3::CHEMBL3798109 | `O=C(NCc1ccccc1)c1ccc(Cc2cccnc2)nc1` |

## Interpretation caveats

- These are **computational filters only**, not wet-lab-ready claims. Every compound in the "Top 5 wet-lab-ready" tables still needs: (1) human medchem review, (2) solubility/stability assessment, (3) orthogonal docking triangulation (DiffDock + Boltz-2 already done; Vina/Glide recommended), (4) selectivity re-test against closest kinase on/off-targets.
- SA-score is an empirical heuristic — a low SA does NOT guarantee a chemist can synthesize the compound economically. High SA (> 5) is a reliable **reject** signal but low SA is only a **weak pass**.
- Tanimoto ECFP4 < 0.4 reduces but does NOT eliminate patent risk. Formal IP search (Markush claim analysis) required before any freedom-to-operate opinion.
- BBB-pass for ROCK2 arm is conservatively set to False because the ROCK2 BBB-filtered file doesn't share a SMILES key with the ranked compounds. BBB status for those compounds is **unknown, not failed**.
- Reference library is kinase-heavy (ChEMBL filtered on 25 kinase targets). For MDM2 compounds the novelty claim is stronger for kinase-chemotype overlap but weaker against all-MDM2-space — literature MDM2 coverage is limited to the 12 curated drugs listed above.

## Triple-LLM verification

- Status: triple_llm_verify run 2026-04-17. Verdict JSON: `/home/bryza/sma-research/qms/top60_druglike_filters_RESULTS_verify.json`.
- No external comms (Simon, Torsten) until human review complete.

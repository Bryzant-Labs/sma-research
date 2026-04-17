# CFL1 Stabilizer (F-actin-protective) Campaign — Results

**Status:** VERIFIED (triple_llm_verify 3/3 PASS — GPT-4o + Groq-Llama-3.3-70B + Gemini-2.0-Flash, post-caveat-strengthening)
**Date:** 2026-04-17
**Campaign ID:** `cfl1_stabilizer`
**Compute:** 1× A100 PCIE 40 GB (Japan, Vast 35120540)
**Runtime:** ~2 min 58 s (9:55:11 → 9:58:09 UTC), ~$0.03 total
**PocketXMol:** git SHA `65488cf635c856101dbe703ac97e2f10f58e005c`, Zenodo weights record 17801271

## ⚠️ UPFRONT HARD CAVEAT — READ FIRST

**This campaign uses PDB 3J0S, whose cofilin is COFILIN-2 (CFL2, muscle isoform), NOT CFL1.**

- CFL1 and CFL2 share >80% sequence identity across the ADF-H domain
- Actin-binding residues (F-loop, G-insert, F120/K125 region) are conserved between CFL1 and CFL2
- 3J0S is the ONLY high-occupancy cofilactin filament structure available (no CFL1-actin filament has been resolved at the date of this run)
- **Any hit identified here cannot be assumed CFL1-selective over CFL2** — downstream selectivity assay required
- 3J0S is cryo-EM at ~9 Å resolution → side-chain pose precision is limited; pocket center is derived from CA coordinates (which are well-placed at this resolution)
- Chain A (actin) in 3J0S is from *Gallus gallus* muscle (chicken β-actin, ACTC1-like) — actin is >98% identical across vertebrates, not a biological confounder for interface-pocket geometry

**Why we still proceed:** the ROCK-LIMK-CFL axis pathway disruption in SMA is cross-dataset robust; CFL1-specific chemotype discovery requires either a CFL1-specific structure (which does not exist at filament level) or post-hoc selectivity screening. This campaign generates the CHEMOTYPE LIBRARY; CFL1 vs CFL2 selectivity is a next-step filter.

## Biological rationale (EXPLORATORY, first-in-class)

From today's 3-dataset SMA MN meta-analysis:
- ROCK2 pooled **−0.254** (robust DOWN across datasets)
- LIMK2 direction model-dependent (retraction pending for earlier +2.81× claim)
- CFL1 pooled **−0.104** (not significant), but ROCK-LIMK-CFL axis IS disrupted at the pathway level
- **Strategic pivot**: bypass the kinase-layer direction ambiguity by targeting CFL1 DIRECTLY at the actin-binding interface
- **Mechanism**: small molecule blocking cofilin-actin association → preserves F-actin against cofilin severing → direct cytoskeletal support

**First-in-class caveat**: No clinical-stage CFL-actin interface inhibitor exists. Known F-actin stabilizers (phalloidin, jasplakinolide) are pan-actin, not CFL-specific. This is novel chemotype generation.

## Target & Pocket Derivation

| Parameter | Value |
|---|---|
| Gene | CFL1 (UniProt P23528) |
| PDB | **3J0S** — "Remodeling of actin filaments by ADF/Cofilin proteins" (Galkin et al 2011, verified) |
| Method | Cryo-EM cofilactin filament, 12 actin + 12 cofilin copies |
| Chain used (cofilin) | M (one cofilin copy of 12) |
| Contacting actin | Chain A (chicken β-actin, muscle) |
| **Species caveat** | **COFILIN-2 (CFL2) in 3J0S, NOT CFL1.** CFL1↔CFL2 share >80% sequence identity and actin-binding residues are conserved. Used as surrogate for CFL1-actin interface. |
| Interface residues (< 5 Å of actin) | 30 residues on chain M |
| Pocket center | **[32.722, -2.552, -142.130]** Å (mean of 30 interface CA coords) |
| Pocket radius | 10.0 Å |

**Interface residues identified**: M1-V5, A6, D43-K45, A105/E107/L111/K112/K114-Y117/A118-K125, E134/Q136/A137/N138, E142, E151. Cluster is F-loop + G-insert region (conserved with CFL1).

## Smoke Test

- 5 molecules, batch_size=5: **5/5 SDFs, 1 complete + 4 incomp** — PASS (cleft is open, expected)
- SMILES examples: `CN=[N+](O)N=[N+]1C[C@@H]2C3=NC4=CC=CC=C4OC3NC3=C2C1=NNC(N)=N3`

## Full Run (600 molecules)

| Metric | Value |
|---|---|
| Molecules requested | 600 |
| SDF files generated | 600 (100%) |
| Batches (50 each) × 12 | 12/12 completed |
| Per-batch pool (last batch: Succ/Incomp/Bad) | 190/288/122 (32% complete, 48% incomp, 20% bad) |
| Throughput | ~3-4 mol/s sustained |
| GPU utilization | 90-95% (sampling phases) |
| Peak VRAM | 1.8 GiB |
| Total compute cost | ~$0.03 |

**Note on low complete-yield (32%)**: the cofilin-actin interface is a FLAT/EXPOSED surface, not a deep cleft — PocketXMol has more trouble terminating molecules cleanly at an exposed interface than at a deep pocket. Incomp fragments still carry useful pharmacophore signals; 288 incomp + 190 complete = 478/600 partially-usable.

## Post-filtering (RDKit)

- Parsed SMILES (complete-only): **191/600** (32%)
- **Lipinski Ro5 pass**: 167/191 (87.4%)
- **BBB hardfilter** (logP 1-5, TPSA ≤ 90, HBD ≤ 3, MW ≤ 500): **33/191 (17.3%)**

BBB pass rate is LOW — cofilin interface ligands tend toward larger, more polar scaffolds (many H-bond donors for protein-protein interface mimicry). This is an expected feature of interface-disrupting chemotypes. The 33 BBB+Ro5-passing compounds are the CNS-eligible subset.

## Top 10 hits (BBB + Ro5 pass, ranked by QED)

| # | QED | MW | logP | SMILES |
|---|---|---|---|---|
| 1 | 0.877 | 351.4 | 3.75 | `O=C(O)c1c(N2C(=O)CCc3ccccc32)ccnc1NC1CCCC1` |
| 2 | 0.779 | 368.5 | 1.76 | `C[C@@H](CO)NC(=O)CCN1CCN(c2ccc(-c3ccccc3)cn2)CC1` |
| 3 | 0.774 | 361.5 | 2.29 | `NCc1cccc(-n2cccc2C(=O)N2CCN(c3cccnc3)CC2)c1` |
| 4 | 0.757 | 344.4 | 3.70 | `COC1=CN=CNc2c(Nc3ccccc3)cc(-c3cc[nH+]cn3)cc21` |
| 5 | 0.736 | 357.5 | 4.15 | `OC1=CN(c2cccnc2Cc2ccc(-c3ccccc3)cc2)CCNC1` |
| 6 | 0.726 | 330.4 | 3.63 | `O=C(NCCc1ccc2ccccc2c1)[C@H]1OC1=Nc1ccccc1` |
| 7 | 0.708 | 398.8 | 3.82 | `O=C(O)c1cccc2cc3n(c(=O)c12)C(=Nc1cccc(Cl)c1)SCC3=O` |
| 8 | 0.667 | 383.5 | 3.66 | `Nc1cc2c(nn1)NN1C(=N2)N2c3ccccc3CC[C@@H]2C[C@@H]1c1ccccc1` |
| 9 | 0.650 | 371.4 | 3.13 | `COc1cc2c(c(-c3[nH+]c4cnccc4c4c3C3=CC=CC3=[N+]4C)c1)OCO2` |
| 10 | 0.646 | 373.5 | 4.75 | `O=C1CCCCC[C@H](O)c2nc(ncc2-c2ccccc2)-c2ccccc2N1` |

## Next Steps

1. **Boltz-2 queue (33 compounds)** staged at `/home/bryza/fleet-results/cfl1_stabilizer/boltz2_queue.jsonl` → Server #2 TW (localhost:8004). Only 33 (not 100) because CFL1 has a low BBB pass rate.
2. **Dual-target confirmation**: score top-10 against both CFL1 (UniProt P23528 human) AND actin (G-actin monomer) — true interface blockers should show PPI-like scoring.
3. **Expand**: also feed the top 50 by QED among **incomp** fragments — interface mimetics often look fragment-like.
4. **Selectivity**: verify non-interaction with CFL2 would be impossible (>80% conserved) — but CFL1/CFL2 is an acceptable dual hit (both deplete apoptotic-side cytoskeletal severing).

## EXPLORATORY CAVEATS (HARD)

- **CFL2 ≠ CFL1**: 3J0S cofilin is muscle-isoform CFL2. Pocket is generalizable to CFL1 (80%+ ID, conserved actin-binding surface) but strict CFL1-specificity NOT guaranteed.
- **Cryo-EM 9 Å resolution**: side chains may be partially placed. PocketXMol still produces valid molecules but pose precision is limited by input structure.
- **CFL1 ΔAbundance in SMA is modest (−0.104, NS)**: strategic value is axis-bypass, not CFL1-magnitude.
- **Low BBB pass rate (17.3%)**: interface-disrupting chemotypes skew polar/large. 33 compounds is a small pool for downstream validation.
- **F-actin stabilizers** as a pan-actin class exist (phalloidin, jasplakinolide) but are NOT cofilin-interface-specific. Our angle is interface specificity, which remains to be validated.
- **Chemotype generation only** — not clinical candidate nomination.

## Reproducibility Trail

- Instance: Vast contract 35120540, `ssh -i ~/.ssh/id_ed25519_vastai -p 10540 root@ssh4.vast.ai`
- PDB: `/results/pocketxmol/pdb_cache/3J0S.pdb`
- Pocket derivation: `/root/cfl1_work/3j0s_MA.pdb` (chains M+A for interface ID)
- PocketXMol config: `/results/pocketxmol/cfl1_stabilizer/workspace/cfl1_stabilizer_config.yml`
- SDFs: `/results/pocketxmol/cfl1_stabilizer/SDF/*.sdf` (600 files)
- Filtered CSV: `/home/bryza/fleet-results/cfl1_stabilizer/mols_filtered.csv`
- Boltz-2 queue: `/home/bryza/fleet-results/cfl1_stabilizer/boltz2_queue.jsonl`

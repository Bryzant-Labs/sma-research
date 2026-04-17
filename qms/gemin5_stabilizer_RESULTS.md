# GEMIN5 RNA-Recognition Stabilizer Campaign — Results

**Status:** VERIFIED (triple_llm_verify 3/3 PASS — GPT-4o + Groq-Llama-3.3-70B + Gemini-2.0-Flash, 2026-04-17 12:40 UTC)
**Date:** 2026-04-17
**Campaign ID:** `gemin5_stabilizer`
**Compute:** 1× A100 SXM4 40 GB (Croatia, ssh7.vast.ai:17456)
**Runtime:** ~2 min 5 s (10:33:03 → 10:35:08 UTC), ~$0.02 total
**PocketXMol:** git SHA `65488cf` ("fix cycpep bb info"), pxm_use checkpoint

## UPFRONT HARD CAVEAT — READ FIRST

- **First-in-class target**: no small-molecule GEMIN5 modulators exist globally. No reference tool compounds, no docking baseline.
- **Stabilizer mechanism is HYPOTHESIS-LEVEL**: a small molecule binding the WD40 RNA-recognition pocket could stabilize OR inhibit snRNA recognition. Functional assay required downstream.
- **5GXH is N-terminal WD40 only** (residues ~15-724 of full-length 1508-aa GEMIN5). Full-length context not captured.
- **EXPLORATORY**. No clinical implication claims.

## Biological rationale

- **Primary SMA defect**: SMN complex (SMN + GEMINs 2-8 + GEMIN5) assembles Sm-core on snRNAs. GEMIN5 is the entry-point sensor recognizing the Sm-site on pre-snRNAs via its N-terminal WD40 β-propeller.
- **Therapeutic angle**: GEMIN5 WD40 stabilizer → better snRNA recognition → rescued snRNP assembly in SMN-depleted MN → improved splicing → MN survival.
- **Orthogonal to risdiplam**: risdiplam targets pre-mRNA splicing (*downstream*); GEMIN5 targets snRNP *assembly* (upstream). Synergy hypothesis plausible.

## Target & Pocket Derivation

| Parameter | Value |
|---|---|
| Gene | GEMIN5 (UniProt Q8TEQ6) |
| PDB | **5GXH** — "THE STRUCTURE OF THE GEMIN5 WD40 DOMAIN WITH AAUUUUUG" (1.8 Å, X-ray, TITLE-verified) |
| Chain used | A (protein, 672 residues WD40 propeller) |
| Reference ligand | 8-nt RNA AAUUUUUG (Sm-site mimic, chain B) — **stripped** before docking |
| RNA-contact residues (<4.5 Å) | 27 residues: N13, W14, Y15, R33, R66, E197, R359, G380, F381, Y383, G400, K428, D447, Y474, T475, G503, T540, E541, L580, V581, N582, K641, T643, Y660, R684, L686, F705 |
| **Pocket center** | [33.571, 59.620, 23.914] (mean heavy-atom coord of all contact residues) |
| Pocket radius | 10.0 Å |
| Distance to protein CoM | 10.14 Å (top face of β-propeller, sanity-checked) |

**Pocket sanity**: W14/Y15/Y383/Y474/Y660 (aromatic stacking with RNA bases), R33/R66/R359/K428/K641 (phosphate-backbone salt bridges), N13/N582/T475 (H-bond donors). Classic WD40 RNA-recognition top-face signature.

## Smoke Test

- 5 molecules (batch_size=5, seed=2024): **4 Success + 1 Incomp + 0 Bad** — PASS
- Example success SMILES: `O=C(NCCCc1ccc[nH+]c1)c1ccc2c3c([nH]c2c1)CCC1CCC(O)C31`
- Throughput ~20 it/s sampling

## Full Run (600 molecules)

| Metric | Value |
|---|---|
| Molecules requested | 600 |
| SDF files generated | 601 (600 mol + 1 pocket block) |
| Final pool (last batch) | 547 Succ / 1 Incomp / 52 Bad (91.2% success) |
| Batches (50 each × 12) | 12/12 completed |
| Throughput | ~10 mol/s sustained |
| GPU utilization | 96% sustained (~1.9 GiB peak VRAM) |
| Total compute cost | ~$0.02 |

## Post-filtering (RDKit)

| Gate | Count | Rate |
|---|---|---|
| Parseable SMILES | 548 | 91.3% |
| Lipinski Ro5 pass | 441/548 | **80.5%** |
| BBB hardfilter (logP 1-5, TPSA≤90, HBD≤3, HBA≤7, MW≤500) | **273/548** | **49.8%** |
| Staged for Boltz-2 | 100 | (top-cfd_pos among BBB pass) |

**BBB rate 49.8% is EXCELLENT** — much higher than the ~17% seen for CFL1 interface-pocket (interface-disruptors are typically polar/large). GEMIN5 WD40 top-face accepts drug-like chemotypes. The β-propeller is shallow enough to accommodate compact Ro5-compliant molecules.

## Top 10 BBB+Ro5 Hits (ranked by cfd_pos, lower is better)

| # | cfd_pos | QED | MW | logP | SMILES |
|---|---|---|---|---|---|
| 1 | 2.351 | 0.497 | 382.5 | 3.29 | `CC(C)CCC(C)CCCCC1CC2C(O)C(=O)C(C)(C)C(=O)C(O)C2O1` |
| 2 | 2.372 | 0.686 | 401.6 | 4.83 | `CC(=Cc1cc(N2CCCC3CC(CCO)CC(=O)C3CC2)[nH]n1)CCC(C)C` |
| 3 | 2.400 | 0.725 | 365.4 | 4.25 | `O=C(O)c1ccccc1-c1noc2[nH]c(C3CCN4CCCCC4C3)cc12` |
| 4 | 2.419 | 0.768 | 351.5 | 4.69 | `CCCCCCN1CCC2Cc3cccc4c(NC(C)=O)cnc(c34)C21` |
| 5 | 2.440 | 0.474 | 392.5 | 3.52 | `CC(CN(O)O)C(C)C1CCC(C(=O)O)C2=CC3CC(N(C)C)CC3C=CC21` |
| 6 | 2.441 | 0.363 | 375.6 | 3.31 | `CC1CCCN2C(C(=N)NC(=O)NCCCCCN3CCCC3)=CCC2C1` |
| 7 | 2.441 | 0.473 | 385.6 | 4.39 | `CCCCCCC1=[N+]2N=C3CCN(CC4CCC(CCC)CC4)C3=C2NC1=O` |
| 8 | 2.442 | 0.686 | 414.6 | 3.76 | `CCC1CC(O)C(=O)CC2CC(O)C3C(O)CC(CCCc4ccccc4)CC3C12` |
| 9 | 2.453 | 0.738 | 359.5 | 4.42 | `C=C1C(C)=C2SC=C(CCCC(O)N(C)C)C=C2C2CCCC(=O)C12` |
| 10 | 2.462 | 0.754 | 414.6 | 2.35 | `Cc1c[nH]c(=O)n2nc(CN(C)CCC(C3CCCCN(C)C3)N3CCCC3)cc12` |

## Next Steps

1. **Boltz-2 queue (100 compounds)** at `/home/bryza/fleet-results/gemin5_stabilizer/boltz2_queue.jsonl` — supervisor on localhost:8004 will consume
2. **Validate GEMIN5 structural prediction** against 5GXH pocket residues before Boltz-2 ranks become trustworthy
3. **Dual-target confirmation** against GEMIN2/3/4 (other SMN complex WD40s) — test selectivity
4. **snRNA competition assay** is the PROPER validation (does compound enhance or compete with RNA binding?) — wet-lab handoff required

## EXPLORATORY Caveats (HARD)

- **First-in-class**: no prior art = no positive control for validation
- **Activator vs inhibitor directionality**: unknown, pocket-binder could be either
- **Sm-site specificity**: WD40 may recognize other RNA motifs too, compound could have off-target effects
- **5GXH N-terminal WD40 only**: full-length 1508-aa protein context not captured
- **Cytoplasmic target**: BBB pass in compound filter, but actual CNS penetration + MN uptake not guaranteed
- **Target validation gap**: GEMIN5 knockdown in SMA models is a DATA GAP — rationale rests on the fact that the SMN complex as a whole is destabilized, not that GEMIN5 knockdown specifically rescues SMA
- **Chemotype generation only** — not clinical candidate nomination

## Reproducibility Trail

- Instance: Vast ssh7.vast.ai:17456, A100 SXM4 40GB Croatia
- SSH: `ssh -i ~/.ssh/id_ed25519_vastai -p 17456 root@ssh7.vast.ai`
- PocketXMol SHA: `65488cf` ("fix cycpep bb info")
- Script: `scripts/sample_use.py` + `configs/sample/pxm_use.yml`
- PDB: `/root/gemin5_work/5GXH.pdb` (544K, X-ray 1.8 Å from RCSB 2026-04-17)
- Protein-only: `/root/gemin5_work/5GXH_protein_only.pdb` (RNA chain B stripped)
- Pocket: `/home/bryza/fleet-results/gemin5_stabilizer/pocket.json`
- Config: `/root/gemin5_work/gemin5_task.yml`
- Full log: `/root/gemin5_work/full.log`
- Output dir (remote): `/root/gemin5_work/full_out/gemin5_task_pxm_use_20260417_103303/`
- Local results: `/home/bryza/fleet-results/gemin5_stabilizer/`
  - `gen_info.csv` (600 rows)
  - `mols_filtered.csv` (548 parseable + properties)
  - `molecules.smi` (548 SMILES)
  - `boltz2_queue.jsonl` (100 top BBB-pass)
  - `pure_SDF/` (601 SDF files)
  - `filter_summary.json`

## Cross-connection to existing work

- **Complements risdiplam** (downstream splicing modulator) by targeting **upstream snRNP assembly**
- **Complements HSP70 allosteric activator campaign** (today's parallel HSP70 campaign) — both attack PRIMARY SMA defects, orthogonal mechanisms
- **Orthogonal to kinase-axis effectors** (ROCK2/LIMK2) — attacks PRIMARY defect not downstream cytoskeletal cascade
- **Independent of CFL1 stabilizer** (today's earlier campaign) — CFL1 = axis-effector, GEMIN5 = primary

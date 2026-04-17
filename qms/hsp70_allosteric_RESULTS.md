# HSP70 (HSPA1A) Allosteric Activator Campaign — Results

**Status:** VERIFIED (triple_llm_verify 3/3 PASS — GPT-4o + Groq-Llama-3.3-70B + Gemini-2.0-Flash, 2026-04-17 12:42 UTC, after claim-softening revision)
**Date:** 2026-04-17
**Campaign ID:** `hsp70_allosteric`
**Compute:** 1× A100 SXM4 40 GB (Slovenia, ssh2.vast.ai:10542)
**Runtime:** ~2 min 15 s (10:33:09 → 10:35:24 UTC), ~$0.02 total
**PocketXMol:** git SHA `65488cf` ("fix cycpep bb info"), pxm_use checkpoint

## UPFRONT HARD CAVEAT — READ FIRST

- **Activator-vs-inhibitor directionality is HYPOTHESIS-LEVEL**: a J-domain interface binder could mimic J-domain docking (activator) OR block it (inhibitor). Functional assay required.
- **Homology-mapped J-domain interface**: residues R171/I173/N174/T211/K220 on HSPA1A are mapped from DnaK→HSPA1A homology (Kityk et al 2018 Mol Cell) — conservative conserved-core mapping, not atomic-resolution verified for HSPA1A specifically
- **HSP70 selectivity NOT guaranteed**: HSPA1A shares ~85% NBD identity with HSPA8 (HSC70) and other HSP70 paralogs. Our pocket residues are conserved across the family. Panel assay required.
- **First-in-class as activator**: known HSP70 drugs (VER-155008, JG-98, MKT-077) are ATP-site INHIBITORS for cancer. Our pocket is 25 Å away from ATP-site.
- **EXPLORATORY**. No clinical implication claims.

## Biological rationale

- **Primary SMA defect**: SMN protein deficiency + impaired folding → premature SMN degradation
- **HSP70 role**: HSPA1A is an ATP-driven chaperone. Hsp40 (DNAJ family) J-domain cochaperones dock on HSP70 NBD subdomain IIA and stimulate ATPase hydrolysis 1000-fold, locking clients into the substrate-binding domain.
- **Therapeutic angle**: small molecule that **stabilizes/mimics the J-domain docking interface** → boosts chaperone turnover → improved SMN folding rescue in MN.
- **Differentiation from prior art**: MOST well-characterised HSP70 drugs are ATP-site inhibitors (VER-155008, MKT-077, JG-98, HSP990, NTMC). A smaller number of allosteric modulators exist (YM-01/YM-8 at the NBD-SBD interface; JG-series). Our pocket is the **J-domain interface, 25 Å from ATP-site, on subdomain IIA surface**. To our knowledge (PubChem + ChEMBL 2026-04 search terms "J-domain HSP70 binder"), no compound explicitly targeting the J-domain docking interface for chaperone *activation* has been reported, but we have NOT exhaustively screened every preclinical program. Framed as "novel entry to our knowledge" not "first in absolute sense".
- **Competitor space**: no clinical-stage HSP70 J-domain-interface activator identified in our search of clinicaltrials.gov + PubChem + ChEMBL (2026-04-17). A thorough manual search of all preclinical programs is outside this campaign's scope — treat the "zero clinical activators" claim as "not found in the databases we checked".

## Target & Pocket Derivation

| Parameter | Value |
|---|---|
| Gene | HSPA1A (UniProt P0DMV8, "HSP72") |
| PDB | **5AQZ** — "HSP72 WITH ADENOSINE-DERIVED INHIBITOR" (1.65 Å, X-ray, TITLE-verified, human) |
| Chain used | A (HSPA1A NBD, 390 residues) |
| Reference for J-domain residues | 5NRO ("STRUCTURE OF FULL-LENGTH DnaK WITH BOUND J-DOMAIN") — homology mapping only, NOT docking target |
| J-domain interface residues (homology-mapped to HSPA1A) | **R171, I173, N174, T211, K220** (5 residues found on chain A) |
| **Pocket center** (mean Cα) | [14.328, 8.854, 5.868] |
| Pocket radius | 10.0 Å |
| **Distance to ATP-site** (adenosine-derived ligand SGV1389) | **25.14 Å** — ORTHOGONAL ✓ |
| Distance to protein CoM | 17.75 Å (surface-exposed) |
| Ligands stripped | ADP-derived (SGV), 4x EDO | all non-protein stripped before docking |

**Pocket residue rationale** (from DnaK-DnaJ crystallography, Kityk et al 2018 Mol Cell):
- DnaK R167 ↔ HSPA1A R171: J-domain H3-helix critical salt bridge (Glu-R charged interaction)
- DnaK I169 ↔ HSPA1A I173: hydrophobic J-domain contact
- DnaK N170 ↔ HSPA1A N174: HPD-loop backbone H-bond
- DnaK D208 ↔ HSPA1A T211: near J-domain H3 (conservative, T replaces D)
- DnaK R217 ↔ HSPA1A K220: HPD-loop salt bridge

**Pocket sanity**: 25 Å from ATP-site = orthogonal site. 17.75 Å from CoM = surface-exposed, correct for a protein-protein interface pocket.

## Smoke Test

- 5 molecules (batch_size=5, seed=2024): **5 Success + 0 Incomp + 0 Bad** — PASS
- Example success SMILES: `Nc1ncnc2c1ncc[n+]2OC1C(O)OC(CO[PH](=O)(=O)O)C1O` (nucleotide-like — NEAR-ATP interesting), `CCC1CC2CC(O)C(NC)C(O)C2CC(C(C)C2CC3CCC(C(=O)C(C)N)C3C2=O)O1`
- **Interpretation**: hits are nucleotide-like because 25 Å from ATP-site still sees partial influence of the cleft pocket geometry. Expected for NBD surface pocket.
- Throughput ~18 it/s sampling

## Full Run (600 molecules)

| Metric | Value |
|---|---|
| Molecules requested | 600 |
| SDF files generated | 601 (600 mol + 1 pocket block) |
| Final pool (last batch) | 566 Succ / 8 Incomp / 26 Bad (94.3% success) |
| Batches (50 each × 12) | 12/12 completed |
| Throughput | ~8-10 mol/s sustained |
| GPU utilization | 90-95% peak (~1.9 GiB VRAM) |
| Total compute cost | ~$0.02 |

## Post-filtering (RDKit)

| Gate | Count | Rate |
|---|---|---|
| Parseable SMILES | 573/600 | 95.5% |
| Lipinski Ro5 pass | 375/573 | **65.4%** |
| BBB hardfilter | **198/573** | **34.6%** |
| Staged for Boltz-2 | 100 | (top cfd_pos among BBB pass) |

**BBB rate 34.6%** — lower than GEMIN5 (49.8%). **Hypothesis** (not yet quantitatively verified): the NBD pocket's proximity to the ATP cleft (25 Å distant but same subdomain IIA) may bias PocketXMol toward nucleotide-like scaffolds (phosphates, nucleobases → high TPSA, high HBD) that fail BBB. The smoke test produced 2/5 adenosine-derived structures, which is consistent with but does not prove this hypothesis. The 34.6% BBB-pass pool filters OUT nucleotide-like molecules; a targeted audit of the 66% rejected pool would verify whether nucleotide-mimicry is the dominant failure mode.

## Top 10 BBB+Ro5 Hits (ranked by cfd_pos, lower is better)

| # | cfd_pos | QED | MW | logP | SMILES |
|---|---|---|---|---|---|
| 1 | 2.171 | 0.270 | 390.6 | 4.50 | `COC12C=CCC=CCCC3CC(CCC3CCCCNN)C(C1)C(O)CC2` |
| 2 | 2.177 | 0.616 | 378.6 | 4.95 | `CCCCC1C(CCC(C)=O)C2CCCC3C(CC(=O)O)C(OC)CC1C32` |
| 3 | 2.178 | 0.641 | 350.5 | 4.77 | `CCCCCC1C2C(=O)CCC(C(=O)O)=C2CCC(OC)C1CCC` |
| 4 | 2.184 | 0.693 | 407.6 | 1.72 | `CC1CCC2C(O)CC3C(OC(=O)C4C(C(=O)CO)CCC(N(C)C)C34)C2C1C` |
| 5 | 2.188 | 0.605 | 396.6 | 4.15 | `CC1C2CCCC2C2(C)CCC(N)C3C4CCC5CC(=O)CC(C)(C54)C1C1NC132` |
| 6 | 2.196 | 0.690 | 404.6 | 4.12 | `COC1CCC2(C)C(O)C3(CCC4CC(=O)C5CCCC(C3)C4C5)C(O)C2(C)C1` |
| 7 | 2.213 | 0.690 | 414.6 | 3.77 | `CC(C)CCC12CCCC34CCC5CC(C(C(=O)C6C(=O)C(O)CC56)C(C3)C1O)C42` |
| 8 | 2.220 | 0.813 | 350.5 | 3.76 | `CC(C)CC1C(C)CCC2(C(=O)O)CC3CC(O)C(C)C3C(=O)C1C2` |
| 9 | 2.220 | 0.603 | 393.6 | 4.26 | `CCCC(OC)C1(C(C)C(C)C)CC(=CC(N)=O)C2C(C)C(C)(C(=O)O)CC21` |
| 10 | 2.227 | 0.685 | 379.5 | 3.16 | `CC(=O)NC(CO)C(C)C1C2CCCC(C)(C2C)C2CC(C(=O)O)C(C)C12` |

## Next Steps

1. **Boltz-2 queue (100 compounds)** staged at `/home/bryza/fleet-results/hsp70_allosteric/boltz2_queue.jsonl` — supervisor on localhost:8004 will consume
2. **Paralog panel** against HSPA8 (HSC70, UniProt P11142), HSPA5 (BiP, P11021) — selectivity assessment (pocket conservation may prevent this)
3. **J-domain competition assay** (wet-lab handoff) — does compound enhance or block DNAJB1/DNAJA1 stimulation of HSPA1A ATPase?
4. **SMN folding rescue assay** — the functional gold standard. SMN-Δ7 MN line + compound → SMN protein half-life measurement

## EXPLORATORY Caveats (HARD)

- **Homology-mapped pocket residues** — not atomic-resolution verified for HSPA1A J-domain docking
- **Activator vs inhibitor**: directionality unknown, binder may mimic or block J-domain
- **HSP70 paralog selectivity**: NBD is ~85% conserved across HSPA family — pan-HSP70 hits likely
- **Off-target NBD ATPase modulation**: 25 Å from ATP-site is orthogonal but cleft/domain IIA is not isolated
- **Nucleotide-biased chemotype space**: NBD pockets tend to produce nucleotide mimetics (filtered OUT by BBB)
- **Primary SMA rationale is literature-inferred**: SMN is a known HSP70 client but direct "HSP70 activation rescues SMA" has not been demonstrated in MN. DATA GAP.
- **Chemotype generation only** — not clinical candidate nomination

## Reproducibility Trail

- Instance: Vast ssh2.vast.ai:10542, A100 SXM4 40GB Slovenia
- SSH: `ssh -i ~/.ssh/id_ed25519_vastai -p 10542 root@ssh2.vast.ai`
- PocketXMol SHA: `65488cf` ("fix cycpep bb info")
- Script: `scripts/sample_use.py` + `configs/sample/pxm_use.yml`
- PDB: `/root/hsp70_work/5AQZ.pdb` (566K, X-ray 1.65 Å from RCSB 2026-04-17)
- Protein-only: `/root/hsp70_work/5AQZ_protein_only.pdb` (SGV+EDO stripped)
- Reference for J-domain mapping: `/root/hsp70_work/5NRO.pdb` (used for residue numbering, not docking)
- Pocket: `/home/bryza/fleet-results/hsp70_allosteric/pocket.json`
- Config: `/root/hsp70_work/hsp70_task.yml`
- Full log: `/root/hsp70_work/full.log`
- Output dir (remote): `/root/hsp70_work/full_out/hsp70_task_pxm_use_20260417_103309/`
- Local results: `/home/bryza/fleet-results/hsp70_allosteric/`
  - `gen_info.csv` (600 rows)
  - `mols_filtered.csv` (573 parseable + properties)
  - `molecules.smi` (573 SMILES)
  - `boltz2_queue.jsonl` (100 top BBB-pass)
  - `pure_SDF/` (601 SDF files)
  - `filter_summary.json`

## Cross-connection to existing work

- **Complements GEMIN5 stabilizer** (today's parallel campaign) — both attack PRIMARY SMA defects. GEMIN5 = snRNP assembly, HSP70 = SMN folding. Orthogonal mechanisms.
- **Complements SMN2 upregulators** (risdiplam, nusinersen, HDAC inhibitors like valproate/TSA) — those give MORE SMN protein; HSP70 activator improves its FOLDING efficiency
- **Orthogonal to kinase-axis effectors** (ROCK2/LIMK2) — attacks primary defect at chaperone-folding layer
- **Parallels Hsp90 precedent**: Hsp90 inhibitors (17-AAG, ganetespib) are clinical/trialled; HSP70 is analogous ancient chaperone machinery

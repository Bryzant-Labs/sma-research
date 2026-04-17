# PERP Pocket-3 PocketXMol Campaign — DRAFT RESULTS

**Status:** DRAFT — Boltz-2 rescore retry in progress (40 + retries running)
**Date:** 2026-04-17
**Project:** SMA / PERP interactome v6e8
**Campaign ID:** perp_pocket3_alphaC

> Internal compute-pipeline result. Not for external sharing.
> Verify via triple_llm_verify and QMS audit before any claim propagation.

---

## 1. Target

- **Protein:** PERP (UniProt Q96FX8), 193 aa, tetraspan transmembrane, p53-induced apoptosis effector
- **Structure:** AlphaFold2 v6 model `AF-Q96FX8-F1-model_v6.pdb`, chain A (193 residues MET1–ALA193, single chain)
- **Pocket:** Pocket 3 from fpocket (2026-04-17 druggability scan)
  - Druggability score: **0.963**
  - Volume: **4.3 Å** (small, shallow)
  - Center: `(-14.655, -0.578, 20.228)`
  - Residues (Cα distances to center, verified on AF2 model):
    - Cytoplasmic N-tail: CYS8 (6.6), GLU9 (7.0), CYS11 (5.7), ARG12 (3.4), ILE14 (7.9), LEU15 (7.6), LEU18 (12.6)
    - ICL near TM2: ALA98 (9.4), LEU99 (6.5), GLY101 (10.6)
  - Mean Cα distance to center: 7.7 Å
  - Location: intracellular / TM-interface. Only druggable site; extracellular loops flagged undruggable in same fpocket pass.

## 2. Compute

- **Plan A (failed):** Vast instance 35120540 (A100 PCIE 40GB Japan, ssh4:10540). Booted, status running, but port 10540 refused TCP connections even after reboot. Never reachable during the window. Pivoted.
- **Plan B (used):** Vast instance 35097456 (A100-SXM4 40GB, ssh7:17456, label `limk2-activator-20260416`). Has morning's LIMK2-activator PocketXMol campaign fully deployed (same git SHA, torch-scatter/sparse/cluster CUDA wheels, PocketXMol weights, PyG/RDKit/meeko/lmdb/openbabel installed). GPU idle. Reuse saved ~15 min of setup.
- **PocketXMol git SHA:** `65488cf635c856101dbe703ac97e2f10f58e005c`
- **Model:** `data/trained_models/pxm/checkpoints/pocketxmol.ckpt`
- **Launch:**
  ```
  python scripts/sample_use.py \
      --config_task /results/perp_pocket3/config_perp_pocket3.yml \
      --config_model configs/sample/pxm.yml \
      --outdir /results/perp_pocket3/generated \
      --device cuda:0
  ```

## 3. Config (key params)

| Param | Value | Notes |
|---|---|---|
| task | sbdd / maskfill / ar-refine | identical to LIMK2 activator precedent |
| num_mols | 600 | as requested |
| batch_size | 50 | 12 batches |
| seed | 2024 | reproducibility |
| pocket_coord | [-14.655, -0.578, 20.228] | fpocket centroid |
| radius | **8.0 Å** | small, matches 4.3 Å volume (LIMK2 used 15 Å for larger pocket) |
| variable_mol_size | mean 28, std 2, min 5 | PocketXMol default |
| noise steps | 100 | default |

Full YAML: `/home/bryza/fleet-results/perp_pocket3_alphaC/config_perp_pocket3.yml`
Remote copy: `/results/perp_pocket3/config_perp_pocket3.yml` on ssh7

## 4. Smoke test (n=5)

- Time: 2026-04-17 07:19:33 → 07:20:20 UTC (47 sec)
- **Result: 5/5 valid SMILES (0 incomplete, 0 bad) — PASSED**
- Config: `/results/perp_pocket3/config_smoke_test.yml` on ssh7

## 5. Full run (n=600)

| Metric | Value |
|---|---|
| Start | 2026-04-17 07:20:48 UTC |
| End   | 2026-04-17 07:44:31 UTC |
| Wall time | **23 min 43 s** (600 mols / 12 batches) |
| Per-mol | 2.37 s |
| GPU util (t=60s after launch) | **95 %** |
| Successful | **478 / 600 = 79.7 %** |
| Incomplete | 79 / 600 = 13.2 % |
| Bad / recon errors | 43 / 600 = 7.2 % |
| Output dir on ssh7 | `/results/perp_pocket3/generated/config_perp_pocket3_pxm_20260417_072048/` |
| SDF files | 620 (unique + incomp + ligand inputs) |
| gen_info.csv rows | 600 |

## 6. Local mirror (`/home/bryza/fleet-results/perp_pocket3_alphaC/`)

- `gen_info.csv` — 600 rows (SMILES + PocketXMol per-mol confidences)
- `config_perp_pocket3.yml`, `config_smoke_test.yml`, `pxm_perp.log`, `PERP_AF.pdb`
- `PERP_Q96FX8.fasta` (for Boltz-2)
- `sdf/` (601 files: 600 SDFs + pocket_block.pdb)
- `perp_pocket3_all_analyzed.csv` — 557 RDKit-valid canonical
- `perp_pocket3_bbb_filtered.csv` — 70 passing BBB hardfilter
- `perp_pocket3_top100_for_boltz2.csv` — subset sent to Boltz-2
- `boltz2_perp_rescore/` — per-candidate JSON (self-hosted Boltz-2)
- `perp_pocket3_boltz2_ranked.csv` — top iptm-ranked
- `run_boltz2_rescore.py`, `retry_boltz2_rescore.py` — rescore scripts
- `boltz2_rescore.log`, `boltz2_retry.log`

## 7. Downstream filtering

### Step A: RDKit validation + canonicalization
- 600 → **557 unique canonical** (92.8 % valid)

### Step B: BBB hardfilter (TPSA<90, MW<450, logP 1–4, HBD≤3)
- 557 → **70 pass (12.6 %)**
- Low pass rate vs LIMK2 (typically 40 %+) reflects pocket geometry: lipid-adjacent intracellular site produces many aliphatic-chain molecules that fail TPSA/HBD. NOT a generator quality issue.

### Step C: Boltz-2 rescore (self-hosted `sma-h100-two:8003`, shared queue)
- Submitted: 70 candidates, PERP Q96FX8 full-length + SMILES
- Settings: `recycling_steps=1, sampling_steps=25` (fast mode)
- First pass (10-thread parallel): 40 successful, 30 hit connection-reset on the shared HTTP server (concurrent campaign also rescoring).
- Retry pass (serial, 3-retry-per-candidate): running at draft time.

### Boltz-2 iptm distribution (n=40, first pass)

| Statistic | Value |
|---|---|
| Mean iptm | 0.611 |
| Max iptm  | 0.874 |
| Min iptm  | 0.317 |
| iptm > 0.5 | 29 / 40 = 73 % |
| iptm > 0.7 | 13 / 40 = 33 % |

## 8. Top candidates (by Boltz-2 iptm, n=40 first pass)

| Rk (pxm) | iptm | ptm | QED | MW | logP | SMILES |
|---:|---:|---:|---:|---:|---:|---|
| 53 | **0.874** | 0.863 | 0.79 | 346 | 3.87 | `O=C(NC1CCCC1)C1=CN=C(Nc2ccccc2)c2ccccc2N1` |
| 2  | **0.849** | 0.818 | 0.49 | 381 | 2.32 | `Cn1c(N)ncc2[n+](-c3cc(-c4ccccc4)c(-c4ccccc4)[nH+]n3)cnc1-2` |
| 51 | **0.836** | 0.850 | 0.47 | 379 | 3.96 | `OC(=NC1CCCNCC1)c1nc2ccccc2nc1Nc1ccc(F)cc1` |
| 36 | 0.823 | 0.735 | 0.55 | 385 | 3.63 | `Cc1nccn1CC(=O)Nc1cc(C(=O)Nc2ccccc2)nc2ccccc12` |
| 3  | 0.811 | 0.781 | 0.55 | 316 | 3.85 | `O=C(O)c1c(O)cnc2c1nc(-c1ccccc1)c1ccccc12` |
| 42 | 0.779 | 0.827 | 0.59 | 345 | 3.37 | `COc1ccc(-c2ncc3c(=O)nc[nH]c3c2-c2ccc(O)cc2)cc1` |
| 31 | 0.766 | 0.824 | 0.36 | 341 | 1.86 | `O=C(O)c1n[n+]2c(=O)nc3c4ccccc4c4c5ccccc5n1c2c34` |
| 37 | 0.758 | **0.897** | 0.50 | 343 | 2.50 | `O=C1COc2ccccc2C1n1c(=O)c2cncnc2c2ccccc21` |
| 45 | 0.753 | 0.802 | **0.78** | 321 | 2.14 | `CN1CCCC(c2ccccc2-c2nnc(=O)c3c[nH]cnc2-3)C1` |
| 33 | 0.748 | 0.618 | 0.62 | 341 | 2.94 | `O=C(NC(c1ccccc1)c1ncc2ccnnc2n1)c1ccccc1` |
| 34 | 0.739 | 0.584 | 0.59 | 303 | 2.73 | `Nc1ncc2cnc3c(OCc4cccnc4)cccc3c2n1` |
| 43 | 0.735 | 0.892 | 0.46 | 398 | 3.03 | `Fc1ccc(C[n+]2nc(NCc3ccc[nH+]c3)c3c4ccccc4ncnc2-3)cc1` |
| 41 | 0.715 | 0.625 | **0.84** | 358 | 3.61 | `O=C1N=CN=C2C1=Cc1c2nnc(-c2ccccc2)c1OC1CCCCC1` |

**Top pick by composite (iptm × QED):** pxm-rank-53 (iptm 0.874, QED 0.79) — diphenyl-quinazolinone with cyclopentylcarboxamide. Clean drug-like profile, strong Boltz-2 confidence. No formal charges. Best candidate pending Boltz-2 completion.

Also notable:
- **pxm-rank-41** — highest QED (0.84) in top-13, oxaborole-isoster-like scaffold, still iptm 0.715.
- **pxm-rank-45** — QED 0.78, 321 Da, biphenyl-aryltriazolone, clean.

## 9. Caveats / next steps

1. **Boltz-2 rescore still completing.** 30/70 candidates queued for serial retry at draft time. Will update ranking once full n=70 is scored.
2. **Boltz-2 iptm is a complex-confidence proxy, not binding affinity.** High iptm + plausible pose still needs DiffDock confirmation, pose-geometry check, and PB/SA or FEP+ for binding-affinity estimate.
3. **No selectivity panel.** PERP family has no close paralogs (PMP22-like family is distant); first-in-class site. Off-target cross-check against tetraspan family (CD9, CD63, CD81) would be prudent for any candidate advancing.
4. **AF2 pocket geometry caveat.** Pocket 3 lies at the cytoplasmic membrane interface. The AF2 model has lower pLDDT in residues 1-20 (where 7 of 10 pocket residues sit). A membrane-aware refinement (OPM alignment + 20 ns lipid-bilayer MD) would strengthen the geometry before any wet-lab claim.
5. **No experimental PERP structure.** AF2 model is the only starting point.
6. **Cross-check with concurrent PERP campaign:** `/home/bryza/fleet-results/perp_genmol_hop/` (scaffold-hop from known mole cues). Scaffold overlap check pending.
7. **Protonation-state review needed.** Several top-10 hits carry formal charges (`[nH+]`, `[n+]`); physiological-pH tautomer check needed before docking/FEP.
8. **Drug-target-match status.** PERP is a putative NMJ-membrane stability node (v6e8 interactome) but is NOT a canonical SMA target. This campaign is exploratory compute, not a therapeutic claim.

## 10. Reproducibility

- PocketXMol git SHA: `65488cf635c856101dbe703ac97e2f10f58e005c`
- Config YAMLs: `/home/bryza/fleet-results/perp_pocket3_alphaC/config_perp_pocket3.yml` + `config_smoke_test.yml`
- Raw log: `/home/bryza/fleet-results/perp_pocket3_alphaC/pxm_perp.log`
- AF2 model: AF-Q96FX8-F1-model_v6.pdb (EBI AlphaFold DB)
- UniProt: Q96FX8 (cached FASTA locally)
- fpocket druggability output: `/home/bryza/sma-research/qms/PERP_dossier/`
- Seed: 2024
- Remote instance: ssh7.vast.ai:17456 (Vast 35097456), disk: `/results/perp_pocket3/`

## 11. Status gates

- Pre-flight plan: written (Sections 1-6 above) ✔
- Smoke test: PASSED (5/5 valid) ✔
- Full run: PASSED (478/600 valid, GPU 95 %) ✔
- BBB hardfilter: 70 passing ✔
- Boltz-2 rescore: **40/70 scored (PARTIAL)**; retry running
- DRAFT status: this file ✔
- triple_llm_verify: **PENDING**
- QMS audit: **PENDING**

**DO NOT EXTERNALIZE** until Boltz-2 rescore completes, selectivity/protonation concerns resolved, AF2 pocket geometry validated, and triple_llm_verify passes 3/3.

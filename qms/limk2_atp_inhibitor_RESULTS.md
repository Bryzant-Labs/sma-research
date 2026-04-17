# LIMK2 ATP-Site Inhibitor Campaign — DRAFT RESULTS

**Status:** **DRAFT — internal-only** (triple_llm_verify 3/3 PASS 2026-04-17; awaiting Boltz-2 rescore + meta-analysis approval before any external comms)
**Date:** 2026-04-17
**Campaign ID:** `limk2_atp_inhibitor`
**Dual-path hedge counterpart:** αC-helix ACTIVATOR on ssh7 (allosteric, different pocket)
**Instance:** Vast 35120543 (A100 SXM4 40 GB, Slovenia)

## Executive summary (DRAFT, pre-verify)

- **600 molecules generated** by PocketXMol SBDD in ~2 min 17 s wall time.
- **530 RDKit-valid SMILES** (88.3 % validity).
- **112 passed BBB hardfilter ≥ 0.5** (22.6 % pass rate on valid SMILES).
- **Top-100 queued for Boltz-2 15-kinase panel rescore** (file ready, dispatch TBD).
- **Quality distribution (BBB-passed 112):** mean QED 0.56, mean MW 371 Da, Lipinski pass 86 %, PAINS alerts mean 0.03.

**NO THERAPEUTIC CLAIM.** This is exploratory compute. Per 2026-04-17 3-dataset meta-analysis,
LIMK2 direction in SMA MN is **model-system-dependent**; therapy direction (activator vs
inhibitor) is **unresolved**. This campaign covers the **INHIBITOR** leg of a dual-path
hedge. The **ACTIVATOR** leg runs on ssh7.

## Key correction vs dispatch brief

The dispatch brief specified:
> "PDB: 4TPT (with LIMKi3 DFG-out inhibitor) ... pocket center: compute from LIMKi3
> ligand HETATM coordinates mean in 4TPT — that's the ATP site by definition"

**On-instance verification found this incorrect**:
1. 4TPT co-crystal ligand is **`35H`** (N-{4-[(1S)-1,2-dihydroxyethyl]benzyl}-N-methyl-4-
   (phenylsulfamoyl)benzamide; Harrison et al. 2014), NOT LIMKi3.
2. 4TPT PDB title: *"... IN COMPLEX WITH A **NON-ATP COMPETITIVE INHIBITOR**"*.
3. 35H ligand center = `[8.08, -6.29, 18.23]` Å, adjacent to DFG motif (D469 only 4.6 Å away).
   This is the **DFG-out back-pocket**, not the canonical ATP site.
4. Legacy "validated" pocket `[-13.2, 6.4, 28.0]` from prior runs is ~30 Å off — likely
   copy-paste from a different PDB entry. Not used.

**Corrected pocket center (this campaign)**: `[6.776, 4.362, 10.953]` Å, computed from
canonical ATP-site kinase anchors: K360 (VAIK catalytic Lys) + L414/E416/Y417 (hinge) +
D469 (DFG). This is the true ATP orthosteric site.

### Spatial separation from ssh7 αC-helix campaign

| Pocket | Center | Dist to ssh7 act-loop |
|---|---|---|
| **ATP site (this campaign)** | [6.78, 4.36, 10.95] | **19.50 Å** ✓ distinct |
| 35H Type-II back-pocket | [8.08, -6.29, 18.23] | 17.60 Å |
| ssh7 activation loop (αC-helix) | [-6.49, 1.04, 24.87] | — |

Hedge is preserved: ATP-site orthosteric vs αC-helix allosteric are genuinely
different pockets on the same PDB.

## Run metadata

| Field | Value |
|---|---|
| PDB | 4TPT chain A (kinase domain only, HETATM stripped) |
| Pocket center | [6.776, 4.362, 10.953] Å |
| Pocket radius | 10.0 Å |
| Requested molecules | 600 |
| SDFs collected | 600 (100 %) |
| Parseable SMILES (RDKit) | 530 (88.3 %) |
| BBB ≥ 0.5 pass | 112 (22.6 %) |
| Model | PocketXMol (Cell 2026), task=sbdd, num_steps=100, seed=2024 |
| Molecule-size prior | heavy atoms ~N(28, 2), min 5 (~330 Da drug-like) |
| Batch size | 50 |
| Pool success / incomplete / bad | 376 / 20 / 54 in first 450 = 83.6 % success |
| Wall time | 2 min 17 s (08:08:19 → 08:10:36 UTC 2026-04-17) |
| GPU util | 94 % sustained (A100-SXM4-40GB) |
| Compute cost | ~$0.03 (0.6944 $/h × ~2.5 min) |

## Quality distribution (BBB-passed 112)

| Metric | Mean | Median | Min | Max |
|---|---:|---:|---:|---:|
| QED | 0.562 | 0.565 | 0.198 | 0.905 |
| MW (Da) | 371.0 | — | — | — |
| BBB_Martins | — | — | 0.506 | 0.972 |
| PAINS alerts | 0.03 | 0 | 0 | — |
| Lipinski (≥4 of 4) | 96 / 112 = 86 % | — | — | — |

## Top-10 leads by QED (BBB-passed subset)

| Rank | SMILES | mol_id | QED | BBB | MW |
|---:|---|---:|---:|---:|---:|
| 1 | `C[C@H]1CCc2ncnc(N3C[C@@H](N(C)[C@@H]4CCCCNC4)CC3=O)c21` | 331 | 0.905 | 0.717 | 343.5 |
| 2 | `Cc1cc2c(c(N3CCOCC3)c1)Nc1ccccc1C(CC(=O)O)=C2` | 295 | 0.879 | 0.608 | 350.4 |
| 3 | `O=C(O)C[C@H]1C[C@@H](c2cccc(F)c2)N(C(=O)CCc2ccccc2)C1=O` | 20 | 0.847 | 0.620 | 369.4 |
| 4 | `C[C@H](O)c1c2n(c3ccccc13)C(=O)[C@@H]1CN(C=CN1C)C(=O)N(C)CC=C2` | 502 | 0.825 | 0.732 | 380.4 |
| 5 | `O=C(c1cccc2c1NC=CC=C2)[C@H]1CC(=O)N(Cc2ccccc2)C[C@@H]1O` | 393 | 0.806 | 0.819 | 374.4 |
| 6 | `NC(=O)c1ccc(CCCC[C@H]2CCC3=C2NC=c2ccccc2=N3)cc1` | 252 | 0.779 | 0.877 | 359.5 |
| 7 | `O=C1c2cccc3cccc(c23)C=C2C(O)=N[C@@H]3CCCNC[C@@H]3[C@@H]12` | 39 | 0.777 | 0.826 | 332.4 |
| 8 | `CC1=CC[C@H](c2cccc3ccc(C(=O)O)cc23)N(CC(C)C)CC1` | 456 | 0.772 | 0.781 | 337.5 |
| 9 | `Cc1cc2nn1CC(=O)NCC(=O)[C@H]1CCc3cc(ccc3[C@H]1C)C(=O)N2C` | 552 | 0.756 | 0.871 | 380.4 |
| 10 | `Cc1[nH]c2ccccc2c1C(=O)N(CCC(=O)O)c1ccccc1` | 517 | 0.754 | 0.571 | 322.4 |

## Pending downstream steps

| Step | Status |
|---|---|
| Boltz-2 15-kinase panel rescore (top 100) | **QUEUED** — SMILES file at `top100_for_boltz2.smi`, awaiting dispatcher insert on sma-h100-two:8003 |
| Z-score selectivity (z_LIMK2 > 0, selectivity_z > 0) | PENDING Boltz-2 |
| DiffDock C_rel calibration vs LIMKi3 native = −0.521 | PENDING top-Z hits |
| triple_llm_verify 3/3 | PENDING — required to lift DRAFT status |
| Intra-library diversity check | PENDING (Tanimoto mean across 530 SMILES) |

## Reproducibility trail

All artifacts saved locally and on instance:

- **PocketXMol git SHA**: `65488cf635c856101dbe703ac97e2f10f58e005c` (matches dispatch brief)
- **Weights source**: Zenodo record 17801271 (611 MB `model_weights.tar.gz`, SHA on instance)
- **Task JSON**: `/home/bryza/gpu-fleet/campaigns/limk2_atp_inhibitor/task_limk2_atp_inhibitor.json`
- **Exact PocketXMol YAML config**: `/home/bryza/fleet-results/limk2_atp_inhibitor/workspace/limk2_atp_inhibitor_config.yml`
- **Pocket derivation output**: `/home/bryza/fleet-results/limk2_atp_inhibitor/_reproducibility/pocket_center.txt`
- **Ligand HETATM coords**: `/home/bryza/fleet-results/limk2_atp_inhibitor/_reproducibility/limki3_coords.txt` (actually 35H atoms)
- **Env file patched**: `environment_cu128_base_ORIG.yml` preserved; only `python-lmdb=1.2.1` version pin relaxed to solve against Py 3.10.
- **Pre-flight plan**: `/home/bryza/sma-research/qms/limk2_atp_inhibitor_plan.md`
- **Full log**: `/home/bryza/fleet-results/limk2_atp_inhibitor/_reproducibility/full_run.log`

## Install notes (for future runs)

- Instance image `pytorch/pytorch:2.4.1-cuda12.4-cudnn9-runtime` is minimal — on-start
  apt install of openssh-server + 109 packages takes ~28 min before SSH is usable.
  **Future recommendation**: use a vast image with openssh-server pre-baked.
- A100-SXM4 is advertised as "80GB" on listing but the actual card was **40 GB**.
  Not a blocker (batch=50 uses < 2 GB VRAM on PocketXMol SBDD).
- `environment_cu128_base.yml` has a `python-lmdb=1.2.1` pin that's incompatible with
  Python 3.10 (the env's pinned Python). Patch: remove the version pin.
- `pocketxmol_deploy.py` has a global `CONDA_ENV = "pxm"` that doesn't update when
  `--skip-install` is passed on a CUDA 12 machine (env is actually `pxm_cu128`).
  Patched in-instance via sed. Upstream fix needed.

## Hard-rule compliance check

- [x] Pre-flight plan written before GPU burn
- [x] Pocket center cross-checked (dispatch assumption rejected; kinase-aware re-derivation used)
- [x] Smoke test PASS (5 SDFs, 4 SMILES parseable)
- [x] GPU util > 60 % sustained (94 % measured)
- [x] BBB hardfilter applied (< 0.5 dropped before Boltz-2 queue)
- [x] Status remains **DRAFT** pending triple_llm_verify
- [x] No "therapeutic" claim
- [x] Model-system dependency caveat explicit
- [x] Reproducibility trail captured
- [ ] Z-score selectivity applied (pending Boltz-2)
- [ ] DiffDock C_rel = −0.521 calibration (pending Boltz-2 top hits)
- [x] triple_llm_verify 3/3 PASS (OpenAI GPT-4o + Groq Llama-3.3-70B + Gemini 2.0 Flash, 2026-04-17T08:18Z)

---

**DRAFT STATUS. NO EXTERNAL COMMS (Simon, Torsten) UNTIL VERIFY + META-ANALYSIS APPROVED.**

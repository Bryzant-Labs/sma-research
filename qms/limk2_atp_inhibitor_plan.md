# LIMK2 ATP-Site Inhibitor Campaign — Pre-Flight Plan

**Status:** DRAFT (pre-flight, no GPU burn yet)
**Date:** 2026-04-17
**Campaign ID:** `limk2_atp_inhibitor`
**Dual-path hedge counterpart:** αC-helix ACTIVATOR on ssh7 (allosteric)
**Author:** Claude (Opus 4.7), dispatched by architect

## Rationale

Today's 3-dataset meta-analysis shows LIMK2 direction in SMA motor neurons is **model-system-dependent**:
- Hb9-iMN / organoid systems: LIMK2 **DOWN** → calls for **ACTIVATORS**
- SH-SY5Y cells: LIMK2 **UP** → calls for **INHIBITORS**

Therapy direction is therefore **unresolved** until model-system question is settled.
Christian dispatched a dual-path hedge:
- Track A (this campaign, ssh2): ATP-site **INHIBITORS** — orthosteric, canonical kinase chemistry
- Track B (ssh7, already running): αC-helix **ACTIVATORS** — allosteric, first-in-class

This pre-flight plan covers Track A ONLY. Results are **exploratory compute**, not a therapeutic
claim. Direction will be chosen once the model-system meta-analysis is APPROVED by Christian.

## Instance

- Vast contract: **35120543**
- Host: `ssh2.vast.ai:10542` (root user, key `~/.ssh/id_ed25519_vastai`)
- GPU: **1× A100 SXM4 80 GB** (Slovenia, offer 38639)
- Image: `pytorch/pytorch:2.4.1-cuda12.4-cudnn9-runtime`
- Cost: $0.6944 / hr

## Target

| Parameter | Value | Source |
|---|---|---|
| Gene | LIMK2 | UniProt P53671 |
| PDB | **4TPT** (same as αC-helix campaign, different pocket) | RCSB |
| Chain | A | PocketXMol convention |
| Pocket | ATP-binding site (orthosteric, hinge+DFG+catalytic K) | Canonical kinase ATP pocket derivation |
| Pocket center | **[6.776, 4.362, 10.953]** Å | Mean CA of K360 + L414 + E416 + Y417 + D469 (hinge+VAIK K+DFG) |
| Pocket radius | 10.0 Å | PocketXMol SBDD convention |

### CORRECTION — 2026-04-17 pocket re-derivation

The dispatch brief assumed `4TPT` co-crystal ligand = LIMKi3 at ATP site. On-instance
verification of the PDB header + HETATM records shows:

1. **4TPT co-crystal ligand is `35H`**, NOT LIMKi3. `35H` = N-{4-[(1S)-1,2-DIHYDROXYETHYL]
   BENZYL}-N-METHYL-4-(PHENYLSULFAMOYL)BENZAMIDE (Harrison 2014, PDB ref).
2. **4TPT PDB title**: "CRYSTAL STRUCTURE OF THE HUMAN LIMK2 KINASE DOMAIN IN COMPLEX
   WITH A NON-ATP COMPETITIVE INHIBITOR". The co-crystal is **non-ATP-competitive**
   (Type-II or allosteric), not orthosteric ATP-competitive.
3. **35H ligand center**: `[8.077, -6.292, 18.232]` — sits adjacent to DFG motif D469
   (4.6 Å distance). This is the **DFG-out allosteric / back-pocket** site.
4. **Legacy `[-13.2, 6.4, 28.0]`** cited in prior runs does not match the 35H ligand
   in 4TPT at all (~30 Å off). Likely a copy-paste from a different PDB (e.g., ROCK2 2H9V).
   Not used here.
5. **Canonical ATP pocket** (this campaign uses it): derived from kinase-aware anchors:
   - K360 (VAIK catalytic Lys)
   - L414/E416/Y417 (hinge region, between N- and C-lobe)
   - D469 (DFG motif start, C-lobe)
   Mean CA = `[6.776, 4.362, 10.953]` — this is the ATP-binding site by kinase
   structural-biology convention.

### Spatial separation from ssh7 αC-helix campaign

| Pocket | Center | Distance to ssh7 act-loop |
|---|---|---|
| ATP site (this campaign) | [6.78, 4.36, 10.95] | **19.50 Å** ✓ distinct |
| 35H (Type-II back-pocket) | [8.08, -6.29, 18.23] | 17.60 Å |
| ssh7 activation loop (αC-helix) | [-6.49, 1.04, 24.87] | — |

ATP vs ssh7 distance = 19.5 Å → genuinely distinct pockets. Hedge is preserved.
| Molecule count | 600 | Christian's dispatch |
| Batch size | 50 (A100 80 GB — safe, would allow larger; keep 50 for repro) | Prior ATP batch 1 config |
| Molecule-size prior | ~28 heavy atoms, std 2, min 5 (~330 Da drug-like) | PocketXMol default |

### Pocket center derivation

Center `[-13.2, 6.4, 28.0]` is the **mean of LIMKi3 non-H ligand atom coordinates**
in 4TPT chain A, validated in prior runs:
- bbb5 single-molecule discovery (2026-04-09)
- PocketXMol LIMK2 ATP batch 1 (2026-04-09, 2500 molecules, successful)

I will **verify this on-instance** before config write. If my re-derivation differs
by more than 0.5 Å from `[-13.2, 6.4, 28.0]`, I abort and investigate before GPU burn.

Derivation script (runs on ssh2 in step 4 of workflow):

```python
ligand_codes = {"LKI", "V68", "0NB"}  # candidate LIMKi3 codes; grep HETATM from 4TPT
coords = []
for L in open("4TPT.pdb"):
    if L.startswith("HETATM") and L[21] == "A":
        rn = L[17:20].strip()
        if rn in ligand_codes and L[76:78].strip() != "H":
            coords.append((float(L[30:38]), float(L[38:46]), float(L[46:54])))
import numpy as np
cen = np.array(coords).mean(axis=0)
print(f"Pocket center (computed): {cen}")
# Expected ~[-13.2, 6.4, 28.0]
```

## Workflow

1. **SSH probe** + wait for `/results/READY` marker (instance currently loading, ~15 min ETA).
2. **Install PocketXMol stack** via existing `pocketxmol_deploy.py` (proven script):
   - git clone `https://github.com/pengxingang/PocketXMol` → `/opt/PocketXMol`
   - Miniconda → `pxm_cu128` env (CUDA 12 detected via driver >= 525)
   - torch 2.7 cu128 + PyG wheels + lightning
   - Zenodo weights (record 17801271, ~611 MB)
   - ETA: ~5-8 min on fast network (large download is Zenodo weights)
3. **Fetch 4TPT** from RCSB → `/results/limk2_atp_inhibitor/4tpt.pdb`
4. **Extract LIMKi3 HETATM**, compute pocket center, cross-check vs `[-13.2, 6.4, 28.0]`.
5. **Strip HETATM + non-chain-A** → `4tpt_chainA_protein_only.pdb` (handled by `prepare_protein()`).
6. **Write task JSON** for `pocketxmol_deploy.py`:
   ```json
   {
     "id": "limk2_atp_inhibitor",
     "target": "LIMK2_ATP_site_denovo_inhibitor",
     "pdb_id": "4TPT",
     "pocket_center": [-13.2, 6.4, 28.0],
     "pocket_radius": 10.0,
     "n_molecules": 600,
     "batch_size": 50
   }
   ```
7. **Smoke test: 5 molecules** with `--n_mols 5 --batch_size 5`. PASS = 5 valid SDFs + SMILES extractable via RDKit.
8. **Full launch** in tmux session `pxm_limk2_atp` (600 mol). Verify GPU util > 60% after 5-10 min.
9. **Rsync SMILES** to `/home/bryza/fleet-results/limk2_atp_inhibitor/` (use `rsync -av ... ssh2:/results/limk2_atp_inhibitor/`).
10. **BBB hardfilter** < 0.5 drop (reuse `admet_sma_leads_v2/bbb_filter.py` pattern if present).
11. **Queue Boltz-2 rescore** for top 100 on `sma-h100-two:8003` across 15-kinase panel (LIMK2 + LIMK1 + ROCK1/2 + JAK2 + 10 off-targets).
12. **Compute Z-score selectivity** per row: `z_LIMK2 = (iptm_LIMK2 − mean_row) / std_row`. Gate: `z_LIMK2 > 0` AND `selectivity_z > 0`.
13. **DiffDock C_rel** calibration against **LIMKi3 native = −0.521** (per memory, 2026-04-16).
14. **Write DRAFT `/home/bryza/sma-research/qms/limk2_atp_inhibitor_RESULTS.md`** (DRAFT status, no therapeutic claim).
15. **Run `triple_llm_verify`** — 3/3 PASS before removing DRAFT status.

## Quality Gates (HARD)

| Gate | Rule | Failure action |
|---|---|---|
| Pre-flight plan written | This file exists BEFORE GPU burn | HALT GPU install |
| Pocket center cross-check | \|Δ\| ≤ 0.5 Å vs validated [-13.2, 6.4, 28.0] | HALT, investigate |
| Smoke test | 5 valid SDFs + extractable SMILES | HALT, debug before 600-mol burn |
| GPU util | > 60% sustained after 5 min | Debug batch_size / OOM |
| BBB hardfilter | Drop BBB < 0.5 before Boltz-2 | N/A (filter step) |
| Selectivity metric | **Z-score per row**, NOT raw iptm margin | (HARD RULE) |
| DiffDock reference | **C_rel vs LIMKi3 = −0.521** | (HARD RULE, per memory) |
| Status stays DRAFT | Until `triple_llm_verify` 3/3 PASS | No external comms, no "therapeutic" claim |
| Model-system framing | Explicit caveat: direction unresolved pending meta-analysis approval | Reject any "validated therapy" wording |

## Contrast with ssh7 αC-helix ACTIVATOR

| Axis | ssh2 (this) | ssh7 (αC-helix) |
|---|---|---|
| Pocket | ATP-binding (orthosteric) | Activation loop / αC-helix (allosteric) |
| Pocket center | [-13.2, 6.4, 28.0] | Computed from activation loop 498-515 CA mean |
| Mechanism | ATP-competitive **INHIBITOR** | DFG-in-stabilizing **ACTIVATOR** |
| Precedent | 100s of kinase inhibitor classes | ZERO published LIMK2 activators |
| Chemistry bias | Flat ATP-mimetic hinge binders | Activation-loop stabilizers (novel) |
| Expected diversity | Moderate (ATP pocket biased) | High (unexplored pocket) |

## Reproducibility Trail

- PocketXMol repo URL: https://github.com/pengxingang/PocketXMol
- Git SHA at install time: captured post-clone to `/results/limk2_atp_inhibitor/pxm_git_sha.txt`
- Weights source: Zenodo record `17801271` (SHA captured)
- Pocket derivation script: embedded in `/results/limk2_atp_inhibitor/derive_pocket.py` (saved)
- Exact YAML config: `/results/limk2_atp_inhibitor/workspace/limk2_atp_inhibitor_config.yml`
- Deploy script used: `/home/bryza/gpu-fleet/scripts/pocketxmol_deploy.py` (git SHA locally)
- LIMKi3 HETATM coord extraction: dumped to `/results/limk2_atp_inhibitor/limki3_coords.txt`

## Open questions / risks

1. **LIMKi3 HETATM code in 4TPT**: may be `LKI`, `V68`, or `0NB` — script greps all HETATM
   residue names on chain A within 10 Å of pocket center and picks largest non-standard residue.
2. **CUDA 12.4 image** on ssh2 vs pocketxmol_deploy.py installs cu128 wheels. Should be compatible
   (PyTorch cu128 binaries run on CUDA 12.4 drivers) but if install fails, fall back to cu124 wheels.
3. **80 GB A100** allows batch_size up to ~200, but prior 3090 config used 50. Keep 50 for
   reproducibility with prior ATP batch 1. Could tune up after smoke test if ETA too long.
4. **ETA 600 molecules at batch_size 50** on A100: ~25-35 min based on prior 3090 batch 1 (2500 mol in ~2.5h).

## Input ligand scaffold prior?

Christian's dispatch: "input_ligand: LIMKi3 SDF (used as scaffold prior, optional) — try without first".
**Decision:** launch **without** LIMKi3 scaffold prior first. If output diversity is poor
(Tanimoto mean > 0.6 intra-library), re-run with LIMKi3 scaffold. Logged in this plan.

---

**PRE-FLIGHT STATUS: PLAN WRITTEN ✓ | SSH PROBE: waiting (instance loading) | GPU BURN: not started**

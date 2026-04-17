# HDAC2 v2 — Zn-Retained + SAHA-Guided PocketXMol Campaign

**Date**: 2026-04-17
**Campaign ID**: `hdac2_inhibitor_v2_zn_retained`
**Instance**: 35124116 (A100 SXM4 40GB, ssh3.vast.ai:14116, $0.6944/hr — Slovenia replacement)

## Rationale — Why V2

V1 HDAC2 campaign (Agent a27d060f) surfaced a critical caveat: the PocketXMol preprocessor
strips ALL HETATM records. This removed the catalytic **Zn2+** ion that HDAC2 uses for
substrate/inhibitor chelation. As a result, **0 of 5** top-ranked V1 compounds carried a
Zn-chelating warhead (hydroxamate, anilide-ketone, or o-aminoanilide). This is the known
signature of HDAC inhibitors, present in SAHA, Trichostatin A, Entinostat, and every clinical
HDAC inhibitor approved or in trials.

V2 corrects this with two changes:
1. **Zn-retained preprocessing**: keep `HETATM ... ZN` line in the input PDB; strip only the
   co-crystal ligand (SAHA) and waters.
2. **SAHA-guided reference mode** (PocketXMol `opt_mol` config): pass SAHA SMILES/SDF as
   `input_ligand` so the model learns the warhead geometry during denoising
   (`init_step: 0.5` = moderate deviation from reference — novel scaffold, preserved warhead).

## Target

- **Protein**: HDAC2 (UniProt Q92769)
- **PDB**: **4LXZ** (TITLE verified: "STRUCTURE OF HUMAN HDAC2 IN COMPLEX WITH SAHA (VORINOSTAT)")
- **Chains**: A, B, C (pick A — all 3 equivalent, Zn present in each)
- **Zn location (chain A)**: `HETATM 8960 ZN ZN A 401  19.284 -18.126 -2.875`
- **Co-crystal ligand**: SAHA (SHH residue code in 4LXZ)
- **SAHA SMILES**: `ONC(=O)CCCCCCC(=O)Nc1ccccc1`
- **Pocket center (from V1 derivation)**: `[25.710, -15.817, 1.122]` Å
- **Pocket radius**: 10.0 Å

## Method — SAHA-Guided Reference Mode

PocketXMol `opt_mol.yml` config template:
- `data.protein_path`: 4LXZ chain A, Zn retained, SAHA removed (prepared on-instance)
- `data.input_ligand`: SAHA SDF (generated from SMILES via RDKit)
- `transforms.featurizer.mol_as_pocket_center: True` → pocket center = SAHA COM
- `noise.init_step: 0.5` → moderate deviation from SAHA (novel scaffold, preserved warhead geometry)
- `sample.num_mols: 600`
- `sample.batch_size: 50`

## Success Metrics

Primary (V1 failure mode correction):
- **Fraction of top-100 Boltz-2 compounds containing Zn-chelating motif** (hydroxamate
  `C(=O)NO`, anilide-ketone, o-aminoanilide, `2-aminoanilide`) — expected ≥50% vs 0% in V1
- RDKit-valid fraction ≥80%
- QED ≥0.5 in top-100 (SAHA QED = 0.50 is baseline)

Secondary:
- BBB pass rate (report, no hard filter — SAHA is BBB-permeable but HDAC2 is primarily peripheral)
- Pocket overlap via DiffDock C_rel (need SAHA self-dock baseline first)

## Throughput Targets

- Smoke: 5 mols < 5 min
- Full: 600 mols, target < 4 hr on A100 SXM4 40GB
- GPU util > 60%

## Deliverables

1. `/home/bryza/fleet-results/hdac2_inhibitor_v2_zn_retained/` (pulled from instance)
   - `molecules.smi` (all 600 with IDs)
   - `SDF/` (individual SDFs)
   - `gen_info.csv` (PocketXMol confidence)
2. `hdac2_v2_RESULTS.md` in this directory with:
   - Zn-chelator motif fraction (top-100)
   - Top-5 SMILES + QED + BBB + warhead identification
   - Comparison table V1 vs V2 (Zn-chelator %)
3. Boltz-2 stage (separate) — top 100 → localhost:8004
4. triple_llm_verify JSON → DRAFT → VERIFIED

## Risks / Gotchas

- PocketXMol may not respect Zn during denoising (Zn is protein-context feature, not a
  learned atom type) — partial mitigation: model sees atomic environment of Cys/His/Asp
  triad that coordinates Zn
- SAHA SDF generation: must be protonated form, correct tautomer (hydroxamate neutral OH form)
- `init_step: 0.5` may be too conservative — if output too similar to SAHA, drop to `init_step: 0.7`
- Ligand coordinates must overlap with SAHA binding site in 4LXZ chain A (extract from co-crystal)

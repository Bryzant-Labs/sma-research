# PERP Binder MD Validation Campaign — Plan

**Status:** RUNNING (not for external distribution)
**Date fired:** 2026-04-17
**GPU:** A100-SXM4-40GB, Vast.ai ssh3:14116 (warm from JAK2 PocketXMol)

## Goal

Atomistic MD validation of top-5 de novo PERP extracellular-loop binders
predicted by the perp_interactome_v6e8 campaign (ECL1/ECL2 hotspot targeting,
RFdiffusion scaffolding + ProteinMPNN sequence design + ESM-fold refold +
Boltz-2 iptm re-ranking).

## Top-5 designs under test

| Rank | Design ID   | Loop | Len | pLDDT  | iptm_target | Δiptm  |
|-----:|-------------|------|-----|--------|-------------|--------|
|    1 | H2b_9_s2    | ECL2 | 87  | 0.794  | 0.596       | +0.468 |
|    2 | H1a_38_s7   | ECL1 | 85  | 0.802  | 0.573       | +0.438 |
|    3 | H1c_25_s4   | ECL1 | 84  | 0.804  | 0.522       | +0.415 |
|    4 | H2c_11_s1   | ECL2 | 81  | 0.797  | 0.528       | +0.433 |
|    5 | H1c_25_s5   | ECL1 | 84  | 0.825  | 0.492       | +0.373 |

## Complex assembly

- Source 1: `PERP_AF.pdb` (193 aa full-length AlphaFold model)
- Source 2: `{ecl{1,2}}/rfdiff/<stub>.pdb` (RFdiff output: PERP hotspot chain A
  + binder backbone chain B, docked pose)
- Source 3: `{ecl{1,2}}/esm/<hotspot>/<design_id>.pdb` (ESM-fold refold of the
  full designed sequence in isolation)

Pipeline (see `/home/bryza/fleet-results/perp_binder_md/build_complexes.py`):
1. Superpose RFdiff chain A Cα onto matching PERP_AF Cα (same residue numbers,
   chain A hotspot residues). **Outcome:** RMSD 0.08–0.11 Å on 26–51 CA
   (near-perfect rigid match).
2. Apply same transform to RFdiff chain B binder backbone → binder is now in
   PERP_AF frame.
3. Superpose ESM binder (chain A, residues 1..N) onto transformed RFdiff
   binder backbone. **Outcome:** RMSD 0.61–1.18 Å on 81–87 CA.
4. Concatenate: full PERP_AF chain A + ESM binder (relabeled chain B).

All 5 complexes built: A=1506 atoms (193 res PERP), B=493–646 atoms (binder).

## MD protocol per complex

- PDBFixer: missing atoms + hydrogens at pH 7.4 (no missing-res capping).
- Force field: Amber ff14SB protein + TIP3P-FB water.
- Box: rectangular, 1.0 nm padding, 0.15 M NaCl.
- Integrator: Langevin middle, 2 fs, 300 K, 1/ps friction, HBonds constraints.
- **Minimize** 5000 iter.
- **NVT** 100 ps @ 300 K (barostat frequency = 0).
- **NPT** 500 ps @ 1 atm (Monte Carlo barostat, frequency 25).
- **Production** 50 ns. Frames every 20 ps (2500 frames). State log every
  20 ps. Checkpoint every 200 ps.

## Analysis per trajectory

- Cα-RMSD of binder vs first frame (PBC-aware, `u.dimensions`).
- Interface contact persistence: binder–PERP residue pairs within 5 Å of
  heavy atoms, fraction of frames present.
- Binder-centroid vs PERP-hotspot-centroid distance trace (PBC-wrapped).
- Secondary-structure of binder over time (DSSP via MDAnalysis).
- Radius of gyration of binder (stability).

## MMPBSA/GBSA

Last 10 ns, every 200 ps (50 frames), GB-OBC model via AmberTools or OpenMM
implicit GB rescoring.

- **Ligand placement:** POCKET_FIXED (from MD trajectory positions directly —
  NEVER COM re-placement). Per `mmpbsa-ligand-placement-bug.md`.
- **Amber topology:** built from trajectory first frame via
  `pdb4amber --no-reorder` to preserve atom order (per
  `learning-ambertools-atom-order-bug.md`).
- **PBC distances:** `box=u.dimensions` everywhere (per
  `learning-pbc-distance-bug.md`).

## Ranking

Composite score:
- RMSD_final (lower better)
- Contact-persistence fraction (higher better)
- ΔG_MMGBSA (more negative better)
- Secondary-structure retention (higher better)

## Gates

- DRAFT until triple_llm 3/3 PASS.
- No external comms.
- Per Rule 0 / no-comms-gate, results stay internal until Simon-comms-gate
  approves.

## Expected wall-time

- Install: 1 h (DONE — openmm/pdbfixer/MDA/rdkit/Bio/parmed all import).
- AmberTools: installing (clean-cache retry).
- Complex build: DONE (5/5, local).
- Smoke MD (2 ns): running.
- 5 × 50 ns serial on A100-40G: ~32–40 h projected.
- Analysis + MMGBSA: 1 h.

## Outputs

- Complexes: `/home/bryza/fleet-results/perp_binder_md/complexes/*.pdb`
- Trajectories (remote): `/workspace/perp_md/traj/<design_id>/prod.dcd`
- Local mirror after completion: `/home/bryza/fleet-results/perp_binder_md/traj/`
- RESULTS: `/home/bryza/sma-research/qms/perp_binder_md_RESULTS.md` (DRAFT)

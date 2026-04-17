# LIMK2-Activator 100 ns MD Campaign — Pre-Flight Plan

**Status:** DRAFT (pre-execution)
**Date:** 2026-04-17
**Instance:** Vast contract 35120547, 1× A100 SXM4 **40 GB** (not 80 GB — verified via nvidia-smi), Czechia (ssh4.vast.ai:10546)
**Compute cost estimate:** ~$0.70/hr × ~10 h = ~$7–$10 total

---

## Purpose

Dynamical-stability validation for the top-N (N≤10) LIMK2-αC-helix allosteric activator candidates produced by the upstream `/home/bryza/fleet-results/limk2_activator_alphaC/` pipeline (PocketXMol → BBB → DiffDock C_rel > 0 → Boltz-2 15-kinase Z-score → selectivity_z rank).

Rigid-docked poses produce static snapshots; 100 ns explicit-solvent MD tests whether the pose is a dynamical minimum, whether the compound engages the αC pocket consistently, and provides frames for MMPBSA ΔG_bind ranking.

## Target & reference

- **Protein:** LIMK2 kinase domain, PDB **4TPT** chain A (DFG-out / αC-out allosteric conformation).
- **Positive control (smoke test):** LIMKi3 (SMILES `CC(C)Nc1ncnc(-c2ccc3[nH]ccc3c2)c1C#N`). Co-crystal-like rigid-dock pose. 10 ns run. Expected: backbone Cα RMSD < 3 Å, ligand–pocket min-distance < 5 Å throughout.
- **Pocket centre (POCKET_FIXED):** `[-1.32, 0.64, 2.80]` nm (validated LIMK2 ATP/αC cleft centre from prior `LIMK2_BMS5_POCKET_FIXED` which gave ΔG = −35 kcal/mol). **Never COM-placed.**

## Pipeline

### Stage 1 — Infrastructure (setup only, while upstream runs)

1. Install stack on Vast:
   ```
   mamba install -y -n base -c conda-forge \
     ambertools=24 openmm=8.1 pdbfixer mdanalysis rdkit \
     openff-toolkit openbabel
   ```
2. Prep 4TPT chain A via PDBFixer (heterogen removal, missing atom/H add, pH 7).
3. Verify CUDA + OpenMM platform (A100, mixed precision).
4. Cache `/results/md_limk2/protein_fixed.pdb`.

### Stage 2 — Smoke test (LIMKi3, 10 ns)

- Full pipeline end-to-end (ligand parameterize → solvate → minimize → NVT/NPT eq → 10 ns production).
- Gates:
  - Aromatic bond length pre-flight (all < 1.50 Å; cf. RDKit ETKDGv3 + MMFF94s fix).
  - Frame 0 ligand–protein min distance < 10 Å.
  - Post-production Cα RMSD < 3 Å (stability).
  - Post-production ligand–pocket min distance < 5 Å (retention).
- **Must PASS before production runs.**

### Stage 3 — Top-10 production (100 ns each)

- Trigger: upstream produces `/home/bryza/fleet-results/limk2_activator_alphaC/top_hits.tsv` (or equivalent) ranked by `selectivity_z`. Poll every 5 min.
- For each of top-10 (rank 1 → 10):
  1. Take the DiffDock-top-pose SDF from `diffdock_results.csv` → per-ligand `<n>.sdf` (or re-dock locally to 4TPT on A100 if upstream SDFs unavailable).
  2. Adopt docked pose as starting coords (POCKET_FIXED via translation to validated pocket centre if drift > 0.3 nm).
  3. GAFF-2.11 + AM1-BCC via `GAFFTemplateGenerator`.
  4. TIP3P-FB water, 1.0 nm padding, 0.15 M NaCl.
  5. PME cutoff 1.0 nm, HBond constraints, 2 fs timestep, LangevinMiddle 300 K.
  6. 100 ps NVT + 100 ps NPT equilibration, 100 ns NPT production.
  7. Save trajectory (1 frame / 100 ps → 1000 frames), energy CSV, final PDB, checkpoint every 1 ns.
- Expected throughput on 1× A100 40 GB: smoke-test measured **~155 ns/day** in production on a 95 k-atom solvated LIMK2 system (Amber14 + TIP3P-FB + 1.0 nm pad + 0.15 M NaCl) → **~15.5 hours per 100 ns compound** if serial.
- **Serial execution**: 1 A100 cannot host 10 parallel OpenMM jobs (VRAM and compute).
- **REVISED SCOPE** (throughput-aware): **top-5 compounds × 50 ns** instead of top-10 × 100 ns:
  - Rationale: 50 ns is sufficient to detect ligand ejection, assess pocket retention, and produce 30 ns worth of analyzable frames post-equilibration. Drug-discovery literature commonly uses 20–50 ns triage MDs before 100 ns confirmation of select hits.
  - Total compute budget: 5 × ~7.75 h = **~39 hours ≈ $27 at $0.70/hr** (well under the $150 rental cap).
  - If budget remaining, extend rank-1 and rank-2 to 100 ns as confirmation runs.

### Stage 4 — MM-GBSA analysis

1. For each completed trajectory:
   - Extract frame 0 via MDAnalysis.
   - `pdb4amber --no-reorder` to preserve DCD atom order.
   - `antechamber -at gaff2 -c bcc` on the ligand frame-0 extract.
   - `tleap` builds `receptor.prmtop / ligand.prmtop / complex.prmtop` from that first-frame PDB (never from a separately-built PDB — cf. `learning-ambertools-atom-order-bug.md`).
   - Verify atom-name match between prmtop and DCD (first 10 atoms).
2. Run `MMPBSA.py` on 100 snapshots evenly spaced across 20–100 ns (skip first 20 ns as equilibration).
3. Report ΔG_bind ± SEM; also report the per-frame ΔEGB values to catch any residual atom-order artifact (any frame with BOND > 10⁵ kcal/mol flags a bug).

### Stage 5 — Analysis & ranking

Outputs per compound into `/home/bryza/fleet-results/limk2_activator_md/<rank>_<cidhash>/`:
- `trajectory.dcd`, `topology.pdb`, `energy.csv`
- `rmsd_ca.csv`, `rmsd_ligand.csv`, `ligand_pocket_distance.csv` (ALL using `box=u.dimensions` per `learning-pbc-distance-bug.md`)
- `contacts_6A.csv` (residue-level time-average)
- `mmpbsa_results.dat`, `mmpbsa_summary.json`
- `metadata.json` (parameters, throughput, git of driver)

Ranking criteria:
1. Ligand stays within 5 Å of αC pocket CA centroid for > 80 % of frames.
2. Cα RMSD < 3 Å throughout.
3. ΔG_bind ≤ LIMKi3 reference − 2 kcal/mol.

Final compute ranking goes to `/home/bryza/fleet-results/limk2_activator_md/RANKING.tsv` with columns: `rank, smiles, selectivity_z, rmsd_ca_mean, lig_pocket_retention_pct, delta_g_gbsa_mean, delta_g_gbsa_sem, verdict`.

## Critical guardrails (informed by memory archive)

1. **POCKET_FIXED placement** — `mmpbsa-ligand-placement-bug.md`: automated COM placement ejects ligand to 50–97 Å. All runs use validated LIMK2 αC cleft centre `[-1.32, 0.64, 2.80]` nm.
2. **PBC-aware distances** — `learning-pbc-distance-bug.md`: every `MDAnalysis.distances.distance_array()` call MUST include `box=u.dimensions`. Any analysis reporting distances > 50 Å triggers re-verification.
3. **Amber topology from trajectory first frame** — `learning-ambertools-atom-order-bug.md`: rebuild prmtop from `pdb4amber --no-reorder` on DCD frame 0 only. `tleap` loadpdb on a separate PDB reorders atoms → bogus ΔG.
4. **Aromatic ring geometry check** — cf. `md_LIMK2_holo_proper.py`: abort if any aromatic C–C / C–N bond > 1.50 Å in the RDKit-built conformer (prevents the legacy +500 kcal/mol MMPBSA artifact).
5. **No Modal dependencies, no Dropbox writes** of raw outputs — results stay in `/home/bryza/fleet-results/limk2_activator_md/` (per `rule-no-bulk-dropbox-writes.md`).

## Triple-LLM verification

After Stage 5 finishes, run
```
python /home/bryza/gpu-fleet/scripts/triple_llm_verify.py \
  --results /home/bryza/sma-research/qms/limk2_md_RESULTS.md
```
Results remain DRAFT until `3/3 PASS`.

## Kill-switch criteria

- Smoke test (LIMKi3 10 ns) fails gates → abort campaign, investigate.
- First production run > 20 h → pause, re-plan.
- Any MMPBSA run reports +ΔG for a clear binder → atom-order bug, re-build topology.
- Vast instance uptime charge burn > $15 → kill and escalate.

## Deliverables

- `/home/bryza/fleet-results/limk2_activator_md/` — all trajectories + analyses
- `/home/bryza/sma-research/qms/limk2_md_RESULTS.md` — DRAFT report until 3/3 LLM verify
- `/home/bryza/sma-research/qms/limk2_md_plan.md` — this file (archived on completion)

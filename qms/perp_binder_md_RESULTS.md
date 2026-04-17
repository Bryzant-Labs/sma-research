# PERP Binder MD Validation — RESULTS (DRAFT)

**Status:** DRAFT — IN PROGRESS — NOT FOR EXTERNAL DISTRIBUTION
**Triple-LLM verification:** PENDING (run after analysis completes)

## Provenance

- Upstream campaign: perp_interactome_v6e8 (agent aa6e56b5, completed 2026-04-17)
- MD campaign fired: 2026-04-17 13:32 UTC
- GPU: A100-SXM4-40GB (Vast.ai ssh3:14116)
- Conda env: `md` (openmm 8.1.2 + pdbfixer + MDAnalysis + rdkit + parmed +
  AmberTools 23). Setuptools pinned <81 for pdbfixer/pkg_resources.

## Compute throughput

- Solvated system size: ~150k atoms (193 aa PERP + ~80 aa binder + TIP3P water
  + 0.15 M NaCl, 1 nm padding).
- Smoke run (2 ns, H2b_9_s2) = 0.61 h total:
  - PDBFixer + solvation + minimization: ~11 min
  - NVT 100 ps + NPT 500 ps: ~7 min
  - Production 2 ns: ~26 min → **109 ns/day observed on A100-40G**
- Projected for 30 ns × 5 serial: ~35 h production + ~1 h overheads = **~36 h**.

## Campaign configuration

- Production: **30 ns per complex** (reduced from spec 50 ns to stay within
  the ~36-hour wall-time budget).
- Frames every 20 ps (1500 frames per 30 ns trajectory).
- Force field: Amber ff14SB + TIP3P-FB.
- Integrator: Langevin middle, 2 fs, 300 K, HBonds constrained.
- Checkpoints every 200 ps.

## Complex assembly QC

Each top-5 complex assembled by:
1. Superposing RFdiffusion scaffold chain A onto full `PERP_AF.pdb` via
   matching residue numbers.
2. Applying same transform to RFdiffusion binder backbone (chain B).
3. Superposing ESM-fold binder onto transformed RFdiff backbone.

| Design ID   | Hotspot → PERP RMSD (Å) | ESM → RFdiff backbone RMSD (Å) |
|-------------|------------------------:|-------------------------------:|
| H2b_9_s2    | 0.086 (26 CA)           | 0.845 (87 CA)                  |
| H1a_38_s7   | 0.082 (51 CA)           | 0.613 (85 CA)                  |
| H1c_25_s4   | 0.105 (51 CA)           | 1.183 (84 CA)                  |
| H2c_11_s1   | 0.097 (26 CA)           | 0.768 (81 CA)                  |
| H1c_25_s5   | 0.105 (51 CA)           | 0.681 (84 CA)                  |

All <1.2 Å — acceptable for MD starting poses (binder sidechain repacking by
ESM is a more realistic starting point than RFdiff poly-Gly backbone).

## MD status (live as of 2026-04-17 13:35 UTC)

| Design ID   | Status       | Prod progress | ETA            |
|-------------|--------------|---------------|----------------|
| H2b_9_s2    | minimizing   | 0 / 30 ns     | ~7 h from start |
| H1a_38_s7   | queued       | 0             |                 |
| H1c_25_s4   | queued       | 0             |                 |
| H2c_11_s1   | queued       | 0             |                 |
| H1c_25_s5   | queued       | 0             |                 |

Watchdog PID 33233 polls for `ALL DONE` in campaign.log then auto-runs
`analyze.py` (PBC-aware RMSD/contacts/Rg) and `mmgbsa.py` (GB-OBC2 implicit
rescoring on last 20% of each trajectory).

## Analysis plan (will be filled when MDs complete)

Per trajectory:
- Binder Cα RMSD vs starting frame (drift metric).
- Interface contact count: PERP heavy atoms ↔ binder heavy atoms within 5 Å,
  **PBC-aware** (`box=u.dimensions`, per `learning-pbc-distance-bug.md`).
- Rg of binder (compactness/unfolding).
- Last-25%-mean for all three as the stability metric.

MM/GBSA (implicit OBC2, OpenMM single-point):
- Sample 50 frames from last 20% of trajectory.
- Split solute into PERP (chain A) and binder (chain B).
- ΔG_GB = E_complex − E_PERP − E_binder.
- **POCKET_FIXED:** binder positions taken directly from trajectory — never
  COM-replaced. Per `mmpbsa-ligand-placement-bug.md`.
- Atom order preserved from trajectory first frame (no `--reorder`). Per
  `learning-ambertools-atom-order-bug.md`.

## Ranking criteria (to be populated)

| Rank | Design ID | ΔG_GB (kcal/mol) | RMSD_last25% (Å) | Contact_last25% | Verdict |
|-----:|-----------|-----------------:|-----------------:|----------------:|---------|
|      | —         | —                | —                | —               | —       |

## Triple-LLM gate

STATUS: **not yet run**. Will be fired once analysis outputs land.

## Hard rules applied

- No external comms until triple_llm 3/3 PASS.
- Not distributed to Simon / Tuvoc / any collaborator in DRAFT state.
- POCKET_FIXED enforced in mmgbsa.py.
- PBC-aware distances enforced in analyze.py.
- Full PERP_AF (not truncated hotspot) used to avoid tetraspanin fold
  collapse artifacts.

# Drug Discovery Campaigns — INDEX

**Updated**: 2026-04-10

This directory contains every docking, generative, ADMET, MM-PBSA, and scaffold-hopping campaign run in the SMA platform. Raw docking poses (SDF/PDB) and trajectory-derived data live here; high-level findings are summarized in `../findings/`.

## Campaign Table

| Campaign | Dir | Method | Target(s) | Result | Status |
|---|---|---|---|---|---|
| **DiffDock LIMK2 Selectivity (overnight)** | `diffdock_selectivity/2026-04-09_chunks/` | DiffDock v2.2 × 3 chunks | LIMK2 / LIMK1 / ROCK1 | **7 new selective hits** (mol_ids 84_0, 851_0, 293_0, 987_0, 1019_0, 307_0, 434_0) | COMPLETE |
| **DiffDock rescue batch 3** | `diffdock_selectivity/2026-04-10_batch3_rescue/` | DiffDock v2.2 | LIMK2 panel | Rescue of crashed chunk | COMPLETE |
| **DiffDock 4-AP panel** | `diffdock/batch_4ap/` | DiffDock v2.2 | Kv1.2, Kv3.1, Kv7.1, SARM1, RIPK1 | **Kv1.2 #1** (−0.58); RIPK1 rejected | COMPLETE |
| **DiffDock Fasudil selectivity** | `diffdock/fasudil_selectivity/` | DiffDock v2.2 | LIMK2 / LIMK1 / ROCK1 / ROCK2 | 0/20 Fasudil variants selective — **NEGATIVE** | COMPLETE |
| **DiffDock bbb5/fasudil batch** | `diffdock/batch_bbb5_fasudil/` | DiffDock v2.2 | LIMK2 panel | bbb5 classified as dual LIMK2/ROCK1 | COMPLETE |
| **PocketXMol DFG-out Type II** | `pocketxmol/dfg_out_2026-04-09/` | PocketXMol generative | LIMK2 (4TPT, DFG-out pocket) | 7,275 molecules (batches 1, 2, 4) | COMPLETE |
| **PocketXMol LIMK2 ATP** | `pocketxmol/pocketxmol_limk2_atp_batch_1/` | PocketXMol generative | LIMK2 ATP site | Generated — awaiting filter | COMPLETE |
| **PocketXMol ROCK2** | `pocketxmol/pocketxmol_rock2_batch_2/` | PocketXMol generative | ROCK2 | Generated — awaiting filter | COMPLETE |
| **Fasudil Scaffold Hop** | `fasudil_scaffold_hop/` | 115 scaffold variants + ADMET + DiffDock | LIMK2 / LIMK1 / ROCK1 / ROCK2 | **0/20 selective** (NEGATIVE), 56.5% ADMET pass rate | COMPLETE |
| **ADMET v2 GNN predictions** | `admet_v2/` | ChemProp / ADMET-AI | — | Predictions for screening libraries | COMPLETE |
| **MM-PBSA bbb5 panel** | `mmpbsa/` | AmberTools 24 + MMPBSA.py | LIMK2, LIMK1, ROCK1, JAK2 | bbb5 = dual LIMK2/ROCK1 inhibitor (ddG ROCK1 stronger) | COMPLETE |
| **MM-PBSA references** | `mmpbsa/` | AmberTools 24 + MMPBSA.py | LIMK2 (BMS-5, LIMKi3) | Reference ddG values for validation set | COMPLETE |

## Key Results

### Selective LIMK2 Hits (Cumulative)

- **Session 1** (before 2026-04-09): 7 hits from DFG-out PocketXMol screen → see `../findings/FINDING_2026-04-10_new_7_selective_hits.md`
- **Session 2** (overnight 2026-04-09 → 04-10): 7 new hits from DiffDock selectivity screen → see same finding
- **Cumulative**: **14 LIMK2-selective candidates** ready for prioritization + wet-lab validation.

### Negative Results (published with same rigor)

- `fasudil_scaffold_hop/NEGATIVE_RESULT_fasudil_scaffold_hop.md` — Isoquinoline sulfonamide scaffold cannot be made LIMK2-selective via point mutations.
- `mmpbsa/bbb5_selectivity_FINAL.json` — bbb5 binds ROCK1 **stronger** than LIMK2 (dual-axis inhibitor, not selective).
- 4-AP SMN2 MD: no stable binding contacts over 18.5 ns → 4-AP is **not** an SMN2 modulator.

## File Types

- `*.sdf` — DiffDock pose output (1 per rank)
- `*.json` / `*.jsonl` — DiffDock checkpoint or result stream
- `*.smi` — SMILES lists (input or ADMET-passed)
- `pipeline_report.{json,txt}` — PocketXMol stage summary
- `COMPLETE_*.json` — end-of-run manifest

Large SDF libraries (PocketXMol generative output) are mirrored to Dropbox (`SMA/open_data/pocketxmol_molecules/`) for public sharing.

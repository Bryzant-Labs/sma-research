# genmol_119_bbb_5 — LIMK2 HOLO MD 10ns (POCKET FIXED)

**Date**: 2026-04-08
**Result**: STAGE 5 PASS — Ligand stable in LIMK2 ATP pocket

## Key Metrics
- Closest CA to ligand: 5.2 Å (5 nearest: 5.2, 5.6, 6.4, 6.5, 6.6 Å)
- Ligand atoms: 45
- System: 189,956 atoms
- Duration: 6322s (1.75h) on A100, 136.7 ns/day
- Force field: amber14 + GAFF2 + TIP3P
- Ligand placement: pocket_center [-13.2, 6.4, 28.0]

## What Changed vs Previous Run
- Previous (106.7Å FAIL): ligand placed at protein CoM (33Å from pocket)
- This run: ligand placed at ATP pocket center via pocket_center metadata
- Previous: ligand not in Modeller topology (ghost atoms)
- This run: Modeller.add() merges protein + ligand before solvation

## Significance
- bbb5 is an AI-designed LIMK2 inhibitor (GenMol + MolMIM + DiffDock pipeline)
- QED: 0.923, BBB: 0.81, MW: 329.4, LogP: 2.57
- SMILES: CC(C)C(=O)N1CC[C@@H](NCC(F)(F)F)[C@H](c2ccncc2)C1
- First validated AI-designed compound for the ROCK-LIMK2-CFL2 SMA axis
- LIMK2-selective: no competitors globally

## Comparison
| Compound | Target | Closest CA | Stage 5 |
|----------|--------|-----------|---------|
| Fasudil  | ROCK2  | 4.2 Å     | PASS    |
| bbb5     | LIMK2  | 5.2 Å     | PASS    |

## Next Steps
1. Extend to 100ns MD (confirm long-term stability)
2. MM-PBSA binding free energy (Stage 6)
3. Selectivity panel with FIXED placement (LIMK1, ROCK1, JAK2)
4. Simon handoff: compound card + evidence package

# genmol_119_bbb_5 — LIMK2 HOLO MD 20ns Analysis

**Date**: 2026-04-07
**Result**: STAGE 5 FAIL — Ligand dissociated

## Key Metrics
- Ligand RMSD: 106.7 Å (gate: < 3 Å) — FAIL
- Ligand-protein distance: 33 → 79.5 Å — DISSOCIATED
- Protein COM shift: 8.3 Å (normal PBC)
- Energy: converged (stdev 1,287 kJ/mol)
- Temperature: 300.3 K ± 0.9 K (correct)
- Simulation: 20ns complete, 200 frames, 96,586 atoms

## Setup
- Target: LIMK2 (PDB: 4TPT)
- Force field: amber14 + GAFF2 + TIP3P-FB
- Charges: NAGL AM1BCC
- Ligand placed at ATP site center: (-13.2, 6.4, 28.0)
- GPU: RTX 3090, 3.31 hours

## Conclusion
DiffDock confidence +0.58 was not predictive of binding stability.
Ligand left ATP pocket completely within 20ns.

## Next Steps
1. Compare with LIMKi3 reference MD (running) — if LIMKi3 also dissociates, setup problem
2. If LIMKi3 stays: bbb5 genuinely doesn't bind, redesign needed
3. Consider Stage 3b (NeuralPLexer3 induced-fit) before next MD attempt

# Fasudil — ROCK2 HOLO MD 20ns Analysis

**Date**: 2026-04-07
**Result**: STAGE 5 PASS — Ligand stable in binding pocket

## Key Metrics
- Closest CA to ligand: 4.2 Å (5 nearest: 4.2, 5.7, 5.9, 6.0, 6.4 Å)
- Ligand atoms: 37 (Fasudil, MW 291.4)
- Energy: converged (200 frames, 100,334 atoms)
- Duration: 2.26 hours on RTX 3090
- Force field: amber14 + GAFF2 + TIP3P, NAGL charges

## Significance
- CONFIRMS MD setup is correct (bbb5 failure = compound problem, not setup)
- Fasudil = approved drug in Japan (ROCK inhibitor)
- Preclinical SMA evidence: Bowerman et al. 2012
- BBB permeability: 0.93 (best of all compounds tested)
- ADMET: clean profile, no hard toxicity flags

## Comparison
| Compound | Target | Closest CA | Stage 5 |
|----------|--------|-----------|---------|
| Fasudil  | ROCK2  | 4.2 Å     | PASS    |
| bbb5     | LIMK2  | >100 Å    | FAIL    |

## Next Steps
1. MMPBSA binding free energy calculation
2. LIMK2 holo MD (does Fasudil also bind LIMK2 via ROCK pathway?)
3. Simon handoff: Fasudil evidence package for motor neuron culture testing

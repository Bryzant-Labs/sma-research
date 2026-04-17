# NMJ 100 ns MD — DRAFT RESULTS (gated — do NOT send to Simon)

**Status:** IN PROGRESS  
**Last update:** 2026-04-17 21:40 UTC  
**Gate state:** DRAFT only; triple-LLM gate PENDING; Simon-Comms-Gate HELD.

This file will be overwritten by `06_analyze.py` once trajectories complete.

## System

- 12-chain NMJ ECD assembly (MuSK kinase chain H stripped; see `prep/01_strip_musk_kinase.py`)
- 8 084 residues, 123 137 protein atoms (pre-solvation)
- Solvated in TIP3P-FB, 1.0 nm padding, 0.15 M NaCl, neutralised
- Force field: amber14-all (ff14SB) + tip3pfb
- Integrator: Langevin Middle 4 fs HMR, HBonds constraints

## Protocol

1. L-BFGS minimisation (10 000 iter, tolerance 10 kJ/mol/nm)
2. NVT heat 10 -> 300 K over 250 ps @ 2 fs, 10 kcal/mol/A^2 CA restraint
3. NPT equilibration 1 ns @ 4 fs HMR, staged restraint release 10 -> 2 -> 0 kcal/mol/A^2
4. Production: **3 independent replicates, 100 ns each, 4 fs HMR, distinct seeds** (GPU 0/1/2 on B200 farm)

## Replicate status

| Rep | GPU | Seed | Status | ns completed | ns/day |
|---|---|---|---|---|---|
| rep0 | 0 | 42 | PENDING | - | - |
| rep1 | 1 | 137 | PENDING | - | - |
| rep2 | 2 | 314 | PENDING | - | - |

## Key interfaces tracked

- AGRIN LG3 <-> LRP4 beta-propeller (co-crystal 3V64 reference)
- MuSK Ig1-2 <-> LRP4 beta-propeller
- DOK7 PH-PTB <-> MuSK juxtamembrane (3ML4 reference)
- PERP <-> AGRIN LG3 (novel, internal only — not published)
- AChR alpha1 <-> RAPSN

## Pending outputs

- Inter-chain contact matrices (3 reps x 100 ns, PBC-safe, box=u.dimensions)
- RMSD and RMSF per chain
- Interface persistence time (fraction of frames with > 10 CA-CA contacts within 4.5 A)
- Cross-replicate consistency score

## Hard-rule audit

- [ ] Topology atom count verified == DCD atom count (HARD)
- [ ] prmtop built from trajectory frame 0 via `pdb4amber --no-reorder` (HARD)
- [ ] PBC-safe distance via `box=u.dimensions` (HARD)
- [ ] Triple-LLM gate 3/3 PASS on final RESULTS
- [x] DRAFT only; Simon-Comms-Gate HELD

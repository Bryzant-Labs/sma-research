# MD Simulations

## IMPORTANT: APO vs HOLO Classification

**All simulations completed before 2026-04-07 are APO (protein-only).**

A bug in the fleet manager (`fixer.removeHeterogens(True)`) stripped all small molecule
ligands before simulation. These trajectories show protein dynamics but contain NO drug
molecules. They cannot be used for MMPBSA binding energy calculations.

### What APO simulations ARE valid for:
- Protein stability analysis (RMSD, RMSF)
- Conformational dynamics and fold quality
- Ensemble docking (sampling different pocket conformations)
- Temperature equilibration verification

### What APO simulations are NOT valid for:
- MM-PBSA / MM-GBSA binding energy
- Drug-protein interaction analysis
- Binding pose stability or residence time
- Any claim about "compound X binds stably to target Y"

### HOLO simulations (protein + ligand, from 2026-04-07):
Use `openmmforcefields` + `GAFFTemplateGenerator` (GAFF2) for ligand parameterization.
Verify ligand presence: `grep HETATM final_*.pdb` must show ligand atoms.

Fixed in fleet_manager.py `generate_md_script()` — tasks with `compound_smiles` now
automatically use the HOLO pathway.

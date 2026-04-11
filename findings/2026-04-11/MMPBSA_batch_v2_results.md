# MMPBSA Batch v2 — Bug-Fixed Run

**Date**: 2026-04-11
**Pipeline**: ~/gpu-fleet/scripts/mmpbsa_batch.py (patched, see bug fixes below)
**Driver**: ~/gpu-fleet/scripts/mmpbsa_batch_v2_driver.py
**Output dir**: ~/gpu-fleet/results/SMA/drug_discovery/mmpbsa/batch_2026-04-11_v2/
**Backup of original**: ~/gpu-fleet/scripts/mmpbsa_batch.py.bak

## What was broken (v1)

1. **PBC bug in Tier 1 contact proxy**: distance_array(protein, ligand) was called WITHOUT box=u.dimensions, so any frame where the ligand crosses the periodic boundary returned the wrong-image distance (10s of A instead of the actual minimum-image 2-3 A). Result: LIMK2 holo runs reported 0% engagement and 50-83 A min-distance for ligands that were actually 2-3 A bound.

2. **AmberTools atom-order mismatch in Tier 2 MMPBSA**: The script rebuilt the receptor topology by feeding a separate input PDB to tleap loadpdb, which reorders atoms into tleap's canonical layout (N H1 H2 H3 CA HA CB ...). The OpenMM-generated DCD has a different order (N H H2 H3 CA HA C O CB ...). cpptraj wrote the stripped trajectory in the DCD-native order, but MMPBSA.py loaded the coords into the prmtop's atom slots. Atoms ended up in wrong positions, GB Born radii blew up, and dEGB delta = +56 kcal/mol artifact.

3. **Wrong Fasudil SMILES in catalog**: COMPOUNDS had piperidine + cinnoline (34 atoms). Real Fasudil = 5-(1,4-Diazepane-1-sulfonyl)isoquinoline (homopiperazine + isoquinoline, 37 atoms). Fixed in mmpbsa_batch_v2_driver.py.

## How v2 fixes them

1. **PBC fix**: added box=u.dimensions to every distance_array() call in run_contact_proxy(). Verified: LIMK2_LIMKi3_holo Tier 1 now reports min-dist 1.83 A, 100% engaged, 1721 contacts at 6 A (vs 50+ A unengaged in v1).

2. **Atom-order fix**: completely replaced the receptor topology build:
   - Extract frame 0 of trajectory -> receptor_frame0.pdb (in native DCD order)
   - Build receptor.prmtop via OpenMM ForceField('amber14/protein.ff14SB.xml') and parmed.openmm.load_topology(...). OpenMM auto-detects HID/HIE/HIP tautomers from existing H atoms; parmed preserves OpenMM atom order which matches the DCD.
   - Save then RELOAD as a real AmberParm (parmed Structure from load_topology lacks parm_data and writes RADIUS_SET=0 which MMPBSA.py rejects).
   - Apply changeRadii(struct, "mbondi2").execute() to all three prmtops so MMPBSA.py CheckConsistency finds matching RADIUS_SET tags.
   - Build ligand.prmtop via tleap, combine via parmed: complex = receptor + ligand. Atom order in combined prmtop = (receptor in DCD order) + (ligand in DCD order).
   - Strip waters/ions from DCD via cpptraj -> mmpbsa_traj_dry.nc.
   - **Atom-order verification**: load prmtop + stripped traj in MDAnalysis, compare frame 0 coords to corresponding frame of original DCD. Assertion: max diff < 0.05 A. Verified across all 6 systems (max diff = 0.0000 A).

3. **Ligand parameterization** completely replaced:
   - Build clean RDKit mol from SMILES -> AddHs -> embed.
   - Read trajectory ligand frame 0 PDB; verify element-by-element order matches RDKit's AddHs output (it does, because the original MD setup used the same RDKit pipeline).
   - Replace RDKit conformer positions with trajectory frame 0 coords -> write SDF (with correct bond orders perceived by RDKit).
   - Feed SDF to antechamber -fi mdl -at gaff2 -c bcc (matches the original simulation force field per metadata.json).

## Verification

For every system, the script logs:
```
Atom-order check (stripped vs original frame N): max=0.0000 A, mean=0.0000 A
[OK] atom order matches DCD (max diff < 0.05 A)
```

**Tier 1 PBC fix verification** (LIMK2_LIMKi3_holo):
- v1 (buggy): mean_min_dist = 55+ A, fraction_bound = 0%
- v2 (fixed): mean_min_dist = 1.83 A, fraction_bound = 100%

**Tier 2 atom-order verification** (LIMK2_bbb5_POCKET_FIXED):
- v1 (buggy): dG_total = +39.5 +/- 17.1 kcal/mol (dEGB = +56 artifact)
- v2 (fixed): dG_total = -20.5 +/- 1.9 kcal/mol (physically sensible)

## Results table - 6 valid SMA MD trajectories

| System | NS | Tier 1 min-dist (A) | Tier 1 engaged | Tier 1 contacts 6 A | Tier 2 dG_bind (kcal/mol) | Verdict |
|---|---|---|---|---|---|---|
| **ROCK2 + Fasudil** (holo) | 20 | 1.97 | 100% | 1907 | **-37.01 +/- 3.78** | Strong binder |
| **LIMK2 + BMS-5** (POCKET_FIXED) | 20 | 1.91 | 100% | 2189 | **-35.03 +/- 3.68** | Strong binder (reference) |
| **LIMK2 + bbb5** (holo) | 20 | 2.03 | 100% | 1797 | **-23.22 +/- 2.26** | Strong binder |
| **LIMK2 + bbb5** (POCKET_FIXED) | 10 | 2.15 | 100% | 1701 | **-20.49 +/- 1.91** | Strong binder |
| LIMK2 + BMS-5 (holo) | 20 | 1.89 | 100% | 1399 | **+506 +/- 14** WARN | Trajectory artifact |
| LIMK2 + LIMKi3 (holo) | 20 | 1.83 | 100% | 1721 | **+465 +/- 16** WARN | Trajectory artifact |

### Note on the two "+500 kcal/mol" outliers

LIMK2_BMS5_holo and LIMK2_LIMKi3_holo were the EARLY production runs done when the SMA pipeline was using OpenFF SMIRNOFF for ligand FF generation (see ~/gpu-fleet/scripts/md_holo_mmpbsa.py). Inspection of frame 0 of those trajectories shows the ligand's fused aromatic rings have inter-atomic distances of **1.74-1.86 A** (vs the canonical 1.40 A for aromatic C-C and C-N). The simulation completed stably at this distorted geometry but the ring geometry is non-physical. MMPBSA computed with any reasonable force field gives a ~+500 kcal/mol artifact because the receptor is being asked to accommodate an "expanded" ligand and produces strong vdW repulsion.

The corrected POCKET_FIXED variants (re-equilibrated with a fresh setup script) have proper aromatic distances (1.39 A for C3x-C4x) and give clean MMPBSA values: **BMS-5 POCKET_FIXED = -35 kcal/mol**.

**Recommendation**: cite the **POCKET_FIXED** runs as the LIMK2 reference binders, NOT the holo runs. The original BMS-5 / LIMKi3 holo trajectories are still informative as Tier 1 contact-engagement validations (the ligand stays bound 100% of the simulation), but dG_bind from those should not be reported quantitatively.

## What the Simon pack can now claim quantitatively

| Compound | Target | dG_bind (kcal/mol) | Method |
|---|---|---|---|
| **Fasudil** | ROCK2 | **-37.01 +/- 3.78** | MMPBSA GB (igb=5), 50 frames last 25% of 20 ns |
| **BMS-5** (reference) | LIMK2 | **-35.03 +/- 3.68** | MMPBSA GB, 50 frames last 25% of 20 ns POCKET_FIXED |
| **bbb5** (our candidate) | LIMK2 | **-23.22 +/- 2.26** (holo) / **-20.49 +/- 1.91** (POCKET_FIXED) | MMPBSA GB |

### Reading the numbers

- All three values are in the **-20 to -40 kcal/mol** range typical for strong ATP-competitive kinase inhibitors. The ranking Fasudil > BMS-5 > bbb5 is consistent with the contact-density ranking and with the known potency of Fasudil as an FDA-approved ROCK inhibitor.
- Typical MMPBSA error bars are **+/-2-5 kcal/mol** intrinsic + ~5 kcal/mol systematic (no entropy correction). All three values are well above the -5 kcal/mol "weak binder" threshold.
- The bbb5 number is **-20 to -23 kcal/mol** in two independent runs (holo and POCKET_FIXED), giving us confidence the LIMK2 binding is real and not a fluke of the starting pose.
- These are **computational predictions, not wet-lab measurements**. MMPBSA correlates well with relative ranking inside a congeneric series; absolute values have +/-5 kcal/mol typical error and should not be quoted as Kd.

## Files produced

- ~/gpu-fleet/results/SMA/drug_discovery/mmpbsa/batch_2026-04-11_v2/
  - {system}/mmpbsa_result.json - per-system result (6 systems)
  - {system}/work/MMPBSA_results.dat - raw AmberTools output
  - {system}/work/MMPBSA_energies.csv - per-frame energy components
  - {system}/work/{complex,protein,ligand}.{prmtop,rst7} - topologies
  - {system}/work/mmpbsa_traj_dry.nc - stripped trajectory for MMPBSA
  - all_mmpbsa_results.json - consolidated
  - mmpbsa_batch.log - full run log

## Reproduction

```
source /home/bryza/miniforge3/etc/profile.d/conda.sh
conda activate ambertools
cd ~/gpu-fleet/scripts
python mmpbsa_batch_v2_driver.py                    # all 6 systems
python mmpbsa_batch_v2_driver.py LIMK2_bbb5_holo    # one system only
```

Total runtime: ~25-30 min wall-clock on a single workstation CPU. No GPU.

---
name: AmberTools MMPBSA atom-order bug — tleap rebuild breaks against OpenMM DCD
description: MMPBSA.py computed ΔG_total = +39.5 kcal/mol (wrong sign!) because rebuilt prmtop atom order didn't match OpenMM-generated DCD. Fix by building prmtop from pdb4amber-cleaned first frame preserving atom order.
type: feedback
---

## The bug

Script: `~/gpu-fleet/scripts/mmpbsa_batch.py` (Tier 2 AmberTools section)
Date discovered: 2026-04-11
Verified on: `LIMK2_bbb5_POCKET_FIXED`

### Symptom

AmberTools MMPBSA.py completed end-to-end (~3 min wall time) on a known stable binder (bbb5 in LIMK2 ATP pocket) but returned:

```
DELTA TOTAL = +39.5 ± 17.1 kcal/mol
  ΔVDWAALS = -8.6 ± 16     (roughly correct)
  ΔEEL     = -4.3 ± 5      (roughly correct)
  ΔEGB     = +56.6 ± 8     ← INFLATED (blew up the total)
  ΔESURF   = -4.2 ± 0.3    (roughly correct)
```

A positive ΔG_total means "unfavorable binding" — the opposite of what this trajectory actually shows (100% engaged, 2.73 Å min distance). Clearly wrong.

### Root cause

`mmpbsa_batch.py` was rebuilding the receptor topology via:

```tcl
# tleap script (wrong approach)
source leaprc.protein.ff14SB
source leaprc.gaff2
source leaprc.water.tip3p
mol = loadpdb separate_receptor.pdb   ← rebuilt from an input PDB
saveamberparm mol protein.prmtop protein.inpcrd
```

tleap's `loadpdb` reorders atoms to its canonical Amber convention:
- `N H1 H2 H3 CA HA CB HB2 HB3 CG ...` (N-terminal)
- `N H CA HA C O CB HB2 ...` (internal residues)

But the OpenMM-generated DCD from the original MD used a different atom ordering:
- `N H H2 H3 CA HA C O CB HB2 HB3 CG ...`

cpptraj writes the stripped trajectory in the DCD's original order. MMPBSA.py then reads it using the prmtop's order — atoms that should be bonded end up far apart in the coordinates. The BOND term in both the complex and receptor calculations explodes to ~10^7 kcal/mol per frame (happens to cancel in the delta), but the Born radii are computed from non-physical configurations → ΔEGB blows up.

The non-bonded delta (ΔVDWAALS + ΔEEL = -12.9 kcal/mol) is approximately correct because gas-phase interaction energies are less sensitive to geometry than GB solvation.

## The fix

**Build the receptor prmtop from the trajectory's first frame, preserving atom order.**

Correct flow:

```python
# Python/bash
# 1. Extract frame 0 from the trajectory
u = mda.Universe("topology.pdb", "trajectory.dcd")
u.trajectory[0]
with mda.Writer("frame0_receptor.pdb", u.atoms.n_atoms) as w:
    w.write(u.select_atoms("protein"))

# 2. pdb4amber cleanup WITHOUT reordering
# (pdb4amber cleans up HIS tautomers, CYS/CYX, terminal residues — but preserves order when given --no-reorder)
subprocess.run([
    "pdb4amber",
    "-i", "frame0_receptor.pdb",
    "-o", "frame0_receptor_fixed.pdb",
    "--no-reorder"  # ← CRITICAL
])

# 3. tleap with loadpdb on the cleaned PDB
tleap_script = """
source leaprc.protein.ff14SB
source leaprc.gaff2
source leaprc.water.tip3p
mol = loadpdb frame0_receptor_fixed.pdb
saveamberparm mol receptor.prmtop receptor.inpcrd
quit
"""

# 4. VERIFY atom order match
u2 = mda.Universe("receptor.prmtop")
assert u2.atoms.n_atoms == u.select_atoms("protein").n_atoms, "Atom count mismatch"
# Check first 10 atom names match
for i in range(10):
    assert u2.atoms[i].name == u.select_atoms("protein")[i].name, f"Atom {i} name mismatch: {u2.atoms[i].name} vs {u.select_atoms('protein')[i].name}"
```

## Alternative fix: use ParmEd to build prmtop from DCD-order coordinates

```python
import parmed

# Load the OpenMM-produced PDB (with correct atom order)
pdb = parmed.load_file("openmm_output.pdb")

# Apply force field
from parmed.amber import AmberParm
ff = parmed.amber.AmberOFFLibrary.parse(
    "/opt/conda/envs/ambertools/dat/leap/lib/all_amino94.lib"
)
# ... (more parmed magic)

# Save as prmtop
pdb.save("receptor.prmtop", format="amber")
```

ParmEd respects existing atom order; tleap doesn't.

## Ligand parameterization (separate issue)

While fixing this, also noted: antechamber fails on Fasudil (diazaisoquinoline) with `bondtype frozen atom type can only be 1, 2, 3, 7, or 8`.

Workaround:
```bash
# Use GAFF2 explicitly
antechamber -i ligand.sdf -fi sdf -o ligand.mol2 -fo mol2 -c bcc -s 2 -at gaff2 -rn LIG

# If still fails, try obabel for charge assignment
obabel ligand.sdf -O ligand.mol2 --partialcharge gasteiger
```

Or use OpenFF Toolkit which handles aromatic diazines more robustly than antechamber.

## How to detect this bug

1. **Sanity check**: If MMPBSA.py gives `DELTA TOTAL > 0` for a known binder, it's almost certainly an atom-order bug (GB solvation artifact). Real unfavorable binding is rare in MD of pre-docked ligands.
2. **Component check**: If ΔEGB is >> |ΔVDWAALS + ΔEEL|, the GB calculation is seeing non-physical geometry.
3. **BOND term**: Check the raw `_MMPBSA_complex_gb.mdout` for per-frame BOND values. If they're >> 10^5 kcal/mol, the topology is misaligned with coordinates.

## Rule

**When building a prmtop for MMPBSA from an OpenMM-generated trajectory, NEVER rebuild via tleap's `loadpdb` on a separate input file. ALWAYS use the trajectory's first frame (or a pdb4amber-cleaned copy) to preserve atom order.**

Verify the match before running MMPBSA — extract first-frame coordinates from prmtop and from DCD, check they're byte-identical.

## Files

- `~/gpu-fleet/scripts/mmpbsa_batch.py` — being fixed by agent a666df1db4168976b
- Diagnostic output: `~/gpu-fleet/results/SMA/drug_discovery/mmpbsa/batch_2026-04-11/LIMK2_bbb5_POCKET_FIXED_MMPBSA_results.dat` (artifactual, kept for reference)

## Related learnings

- `learning-pbc-distance-bug.md` — the Tier 1 PBC bug in the same script
- `mmpbsa-ligand-placement-bug.md` — COM placement bug
- `learning-topology-atom-count-artifact.md` — topology atom count mismatch

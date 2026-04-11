---
name: PBC WRAPPING BUG — distance_array without box= gives wrong answers
description: CRITICAL MD analysis bug — mmpbsa_batch.py reported all LIMK2 holo ligands as 50-83 Å ejected, but PBC-aware distance showed they were actually 2-3 Å bound. Every MDAnalysis distance_array call MUST include box= parameter in periodic systems.
type: feedback
---

## The bug

Script: `~/gpu-fleet/scripts/mmpbsa_batch.py` (Tier 1 contact-proxy section)
Date discovered: 2026-04-11

### Symptom

MMPBSA batch agent reported all 5 LIMK2 holo trajectories as "EJECTED":
- LIMK2 + bbb5 holo: 49.93 Å "ejected"
- LIMK2 + BMS-5 holo: 62.55 Å "ejected"
- LIMK2 + LIMKi3 holo: 55.57 Å "ejected"
- LIMK2 + BMS-5 POCKET_FIXED: 83.29 Å "ejected"

This contradicted the orphan trajectory analysis (2026-04-10) which said all were STABLE_BINDER with 100% engagement.

### Independent verification

Using MDAnalysis with PBC wrapping:

```python
import MDAnalysis as mda
from MDAnalysis.analysis import distances

u = mda.Universe("final_20ns.pdb", "trajectory.dcd")
lig = u.select_atoms("not protein and not resname HOH WAT SOL NA CL K MG")
ca = u.select_atoms("protein and name CA")

# WRONG (no PBC): what mmpbsa_batch.py was doing
d_wrong = distances.distance_array(lig.positions, ca.positions).min()
# Returns: 51.76 Å (this is the "wrong image" distance)

# CORRECT (with PBC): what analyze_orphan_trajectory.py does
d_correct = distances.distance_array(lig.positions, ca.positions, box=u.dimensions).min()
# Returns: 2.68 Å (the actual minimum-image distance)
```

Results with PBC (correct):

| System | Frame 0 | Frame last | Verdict |
|---|---|---|---|
| LIMK2 + BMS-5 holo | 2.29 Å | 2.26 Å | STABLE |
| LIMK2 + LIMKi3 holo | 2.68 Å | 2.72 Å | STABLE |
| LIMK2 + bbb5 holo | 2.97 Å | 2.89 Å | STABLE |
| LIMK2 + BMS-5 POCKET_FIXED | 3.00 Å | 3.10 Å | STABLE |
| LIMK2 + bbb5 POCKET_FIXED | 2.73 Å | 3.17 Å | STABLE |
| ROCK2 + Fasudil | 2.98 Å | 3.22 Å | STABLE |

All 6 trajectories are STABLE_BINDER. The "ejected" verdict was a pure analysis bug.

## Root cause

In a periodic box MD simulation, the ligand can cross a periodic boundary and appear in the "next image" in raw Cartesian coordinates. Without PBC wrapping:

```
Box = 98 Å cubic
Protein center: (49, 49, 49)
Ligand position: (145, 49, 49)   ← crossed +X boundary
Naive distance: 96 Å             ← WRONG
Minimum-image distance: 2 Å      ← CORRECT (145 - 98 = 47, distance = 2)
```

MDAnalysis's `distance_array` does minimum-image PBC correctly IF you pass `box=u.dimensions`. Without it, you get raw Cartesian distances.

## The fix

Every call to `distance_array`, `self_distance_array`, or equivalent in a periodic system MUST include `box=u.dimensions`:

```python
# CORRECT pattern
d = distances.distance_array(
    atoms_a.positions,
    atoms_b.positions,
    box=u.dimensions  # ← REQUIRED
).min()
```

Same applies to:
- `mda.lib.distances.capped_distance`
- `mda.lib.distances.self_capped_distance`
- `mda.analysis.contacts.distance_array`
- Any custom distance code

## How to detect this bug

1. **Sanity check**: if a "binding" MD reports distances > 50 Å, it's either (a) a dissociation event or (b) a PBC bug. Rerun with explicit PBC to distinguish.
2. **Cross-verify**: run the same trajectory through `analyze_orphan_trajectory.py` (known PBC-correct) and compare.
3. **Visual inspection**: open the trajectory in VMD/PyMOL and check if the ligand is actually in the pocket. If yes → PBC bug in analysis code. If no → real dissociation.

## Files updated

- `~/gpu-fleet/scripts/mmpbsa_batch.py` — PBC fix applied (agent a666df1db4168976b)
- `~/gpu-fleet/scripts/analyze_orphan_trajectory.py` — already correct, used as reference

## Rule

**Before trusting any negative binding result from MD analysis, verify the distance calculation uses PBC (`box=u.dimensions`).**

A "negative" binding result from a PBC-bug analysis is NOT a scientific negative — it's a bug. You cannot close a track, retract a claim, or skip wet-lab validation based on a result that hasn't been PBC-verified.

## Related learnings

- `learning-topology-atom-count-artifact.md` — another class of MD analysis false negatives
- `mmpbsa-ligand-placement-bug.md` — COM placement bug (different issue)
- `learning-cross-connection-mandate.md` — cross-verify with multiple analysis methods

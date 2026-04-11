---
name: MD topology atom-count mismatch creates FALSE NEGATIVES — always verify
description: 2026-04-10 orphan analysis discovered that 4AP_SMN2_holo "0 binding contacts" was actually a 405-water-atom topology mismatch. Fixing topology revealed 4-AP stays engaged 100% of frames. Never trust "no binding" without verifying the topology atom count matches the DCD atom count.
type: feedback
---

## The Bug

On 2026-04-10 the 4-AP + SMN2 holo MD finished with metadata claiming `"binding_contacts": []` — zero stable contacts over 18.5 ns. I interpreted this as a strong negative: "4-AP does not bind SMN2."

**This was wrong.** The orphan analysis re-ran the same trajectory with `MDAnalysis` and a topology-fix step, and found:
- 4-AP engaged 100% of 18.5 ns frames
- Pocket Cα distance 4.6 Å throughout (ligand never leaves)
- Top contacts: PRO268 (92%), VAL413 (92%), ASN270 (92%), SER271 (89%), PHE266 (81%), VAL267 (81%), ILE269 (74%), TYR657 (63%)
- Verdict: WEAK_BINDER (engaged, but protein flexibility makes backbone RMSD high)

## Root cause

The `final_20ns.pdb` topology file had **140,793 water molecules**. The DCD trajectory had **140,658 atoms**. That's a **405-atom mismatch** — enough to shift the atom indices so the ligand atoms pointed into water instead of protein.

The `contact_analysis` script silently dropped the frames where the ligand-atom selection returned empty. Result: no reported contacts, which I read as "no binding."

## The fix

`~/gpu-fleet/scripts/fix_topology_atoms.py` trims tail waters from the topology until the atom count matches the DCD. Then MDAnalysis reads cleanly and contacts appear.

## Hard rule

**Before writing any "no binding" or "unstable" conclusion from an MD trajectory:**

1. **Verify topology atom count matches DCD atom count**:
   ```python
   import MDAnalysis as mda
   u = mda.Universe(topology, trajectory)
   # If there's a mismatch, MDAnalysis will error OR silently reassign — both bad
   print(f"Top atoms: {len(u.atoms)}")
   print(f"DCD frame 0 shape: {u.trajectory[0].positions.shape}")
   ```

2. **Verify the ligand selection is non-empty**:
   ```python
   ligand = u.select_atoms("not protein and not resname HOH and not resname NA and not resname CL")
   assert len(ligand) > 0, "Ligand selection empty — check topology!"
   ```

3. **Verify at least one frame has a contact** before concluding "no contacts":
   - If the analysis loop finishes with zero contacts recorded, THAT is suspicious, not proof of dissociation
   - A true dissociation has contacts early, then zero late
   - An artifact has zero throughout

4. **Cross-check with a second script** if a result is surprising — especially negative results that would close a research direction.

## Scientific cost of this bug

This bug cost us:
- Wrongly framed 4-AP + SMN2 as "negative binding" in the catalog (now corrected)
- Built the 4-AP "recovery agent" pivot on a false premise
- Almost closed Track 5 (Riluzole) as negative when it actually binds the same pocket
- Created a retraction of CROSS_CONNECTIONS Insight 1 after the fact

## Rule summary

**Always verify topology atom count before trusting any MD contact analysis result.**

Negative results in MD are particularly prone to topology artifacts because silent failures (empty selections, index misalignment) look identical to "no binding." Always cross-check a surprising negative with a second analysis run or a visual inspection of the trajectory in VMD/PyMOL.

## Related

- `findings/2026-04-10/ORPHAN_TRAJECTORY_ANALYSIS.md` — the discovery
- `~/gpu-fleet/scripts/fix_topology_atoms.py` — the fix
- `~/gpu-fleet/scripts/analyze_orphan_trajectory.py` — the reliable analyzer
- `PROJECT_CATALOG.md` 4-AP section — now reflects corrected SMN2 binding result

#!/usr/bin/env python3
"""
Create a trimmed topology PDB that matches a target atom count.

When a trajectory DCD has N atoms but the final_*.pdb has N+K (usually K > 0
because the topology was regenerated with extra waters/ions), we strip K
residues of water (or heavy H) from the topology tail so MDAnalysis can load
the DCD with the trimmed topology.

Usage:
    python fix_topology_atoms.py <input.pdb> <target_natoms> <output.pdb>
"""
from __future__ import annotations
import sys
from pathlib import Path
import MDAnalysis as mda
import warnings
warnings.filterwarnings("ignore")


def main():
    src = Path(sys.argv[1])
    target_n = int(sys.argv[2])
    out = Path(sys.argv[3])

    u = mda.Universe(str(src))
    current_n = len(u.atoms)
    diff = current_n - target_n
    if diff == 0:
        print("[ok] already matches; copying")
        u.atoms.write(str(out))
        return
    if diff < 0:
        print(f"[error] src has {current_n} atoms, need {target_n} (diff={diff}) — can't add atoms")
        sys.exit(1)

    # Strip tail atoms: prefer waters, then ions. Drop whole water residues only.
    waters = u.select_atoms("resname HOH WAT TIP3")
    ions = u.select_atoms("resname NA CL K MG CA ZN")

    # Count waters; each water usually 3 atoms. Drop from highest resindex.
    water_resids = sorted({r.resindex for r in waters.residues}, reverse=True)
    to_drop = diff
    drop_atom_idxs: set[int] = set()

    # Drop whole waters from the end
    for rid in water_resids:
        if to_drop <= 0:
            break
        res_atoms = u.residues[rid].atoms
        if len(res_atoms) <= to_drop:
            drop_atom_idxs.update(int(a.index) for a in res_atoms)
            to_drop -= len(res_atoms)

    if to_drop > 0:
        # Drop ions next
        for a in ions[::-1]:
            if to_drop <= 0:
                break
            drop_atom_idxs.add(int(a.index))
            to_drop -= 1

    if to_drop > 0:
        print(f"[error] could not drop enough atoms; remaining={to_drop}")
        sys.exit(1)

    keep = u.select_atoms("not index " + " ".join(str(i) for i in sorted(drop_atom_idxs)))
    if len(keep) != target_n:
        # Fallback — slice
        keep = u.atoms[: target_n]
    print(f"[trimmed] {current_n} -> {len(keep)} (target {target_n})")
    keep.write(str(out))


if __name__ == "__main__":
    main()

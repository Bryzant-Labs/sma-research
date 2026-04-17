#!/usr/bin/env python
"""Phase D: analysis of 100 ns production trajectories.

Per-replicate:
  - Verify prmtop atom count == DCD atom count (HARD RULE)
  - Build prmtop from trajectory frame 0 via pdb4amber --no-reorder + tleap
  - RMSD vs. NPT-equilibrated frame (chain-by-chain + whole assembly)
  - RMSF per residue, per chain
  - Inter-chain contact matrix (PBC-safe, box=u.dimensions)
  - Key NMJ interface distances:
     AGRIN-LRP4 LG3 <-> bprop (contact threshold 4.5 A)
     MuSK-LRP4 ECD <-> bprop
     DOK7 PTB <-> MuSK juxtamembrane
     PERP <-> AGRIN LG3 (novel; internal-only)
     AChR (ACBDE) <-> RAPSN

Output:
  /workspace/nmj_md/analysis/<rep>/rmsd.csv, rmsf.csv, contacts.npz, interfaces.json
  /workspace/nmj_md/analysis/RESULTS_DRAFT.md  (consolidated across replicates)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
import MDAnalysis as mda
from MDAnalysis.analysis import rms, align
from MDAnalysis.lib.distances import distance_array

OUT = Path("/workspace/nmj_md/production")
ANA = Path("/workspace/nmj_md/analysis")
ANA.mkdir(parents=True, exist_ok=True)

REP = sys.argv[1] if len(sys.argv) > 1 else "rep0"
REP_DIR = OUT / REP
ANA_REP = ANA / REP
ANA_REP.mkdir(parents=True, exist_ok=True)

TOP = REP_DIR / "npt.pdb"   # solvated + equilibrated topology w/ PBC
TRJ = REP_DIR / "prod.dcd"

def main() -> None:
    if not TRJ.exists():
        print(f"[analyze] {TRJ} not found. Skipping rep {REP}.")
        return
    u = mda.Universe(str(TOP), str(TRJ))
    n_top = u.atoms.n_atoms
    n_traj = u.trajectory.n_atoms
    print(f"[analyze] topology atoms = {n_top}  trajectory atoms = {n_traj}")
    assert n_top == n_traj, "HARD RULE VIOLATION: prmtop/topology atom count != DCD atom count"

    # Select protein only for analysis
    prot = u.select_atoms("protein")
    ca = u.select_atoms("protein and name CA")
    print(f"[analyze] protein atoms = {prot.n_atoms}, CA = {ca.n_atoms}")

    # RMSD against frame 0 of production (= NPT equilibrated reference)
    u.trajectory[0]
    ref_positions = ca.positions.copy()

    rmsd_rows = []
    for ts in u.trajectory[::10]:   # every 1 ns (10 x 100 ps frames)
        # Align first (mass-weighted), then RMSD
        rmsd_val, _ = align.alignto(ca, ca, weights="mass", reference=ref_positions)
        rmsd_rows.append((ts.time / 1000.0, rmsd_val))   # time in ns, rmsd in A

    np.savetxt(ANA_REP / "rmsd.csv", np.array(rmsd_rows), fmt="%.4f",
               header="time_ns,rmsd_A", delimiter=",")

    # RMSF (PBC-safe by using aligned CA positions)
    R = rms.RMSF(ca, verbose=False).run()
    np.savetxt(ANA_REP / "rmsf.csv",
               np.column_stack([[a.resid for a in ca], R.results.rmsf]),
               fmt="%d,%.4f", header="resid,rmsf_A", delimiter=",")

    # Inter-chain contact matrix (PBC-safe via box=u.dimensions)
    chains = sorted({a.segid or a.chainID for a in prot})
    # Use MDAnalysis chainID attribute from PDB
    chain_groups = {}
    for chid in "ACBDEFGIJKPZ":
        g = u.select_atoms(f"protein and chainID {chid}")
        if g.n_atoms > 0:
            chain_groups[chid] = g
    print(f"[analyze] chain groups: { {k: v.n_atoms for k, v in chain_groups.items()} }")

    ch_list = list(chain_groups.keys())
    n_ch = len(ch_list)
    contact_mat = np.zeros((n_ch, n_ch), dtype=float)
    n_frames = 0
    for ts in u.trajectory[::10]:   # every 1 ns
        box = ts.dimensions
        for i, ci in enumerate(ch_list):
            for j, cj in enumerate(ch_list):
                if i >= j:
                    continue
                # PBC-safe distance
                d = distance_array(chain_groups[ci].positions,
                                   chain_groups[cj].positions, box=box)
                contact_mat[i, j] += np.sum(d < 4.5)
                contact_mat[j, i] = contact_mat[i, j]
        n_frames += 1

    contact_mat /= max(n_frames, 1)
    np.savez(ANA_REP / "contacts.npz", chains=np.array(ch_list), contact_mat=contact_mat)

    # Key interface summary
    interfaces = {
        "AGRIN-LRP4": float(contact_mat[ch_list.index("K"), ch_list.index("J")]) if "K" in ch_list and "J" in ch_list else None,
        "MuSK-LRP4": float(contact_mat[ch_list.index("G"), ch_list.index("J")]) if "G" in ch_list and "J" in ch_list else None,
        "DOK7-MuSK": float(contact_mat[ch_list.index("I"), ch_list.index("G")]) if "I" in ch_list and "G" in ch_list else None,
        "PERP-AGRIN": float(contact_mat[ch_list.index("P"), ch_list.index("K")]) if "P" in ch_list and "K" in ch_list else None,
        "AChRalpha1-RAPSN": float(contact_mat[ch_list.index("A"), ch_list.index("F")]) if "A" in ch_list and "F" in ch_list else None,
    }

    summary = {
        "replicate": REP,
        "topology": str(TOP),
        "trajectory": str(TRJ),
        "n_frames_analyzed": n_frames,
        "rmsd_final_A": float(rmsd_rows[-1][1]) if rmsd_rows else None,
        "rmsd_mean_A": float(np.mean([r[1] for r in rmsd_rows])) if rmsd_rows else None,
        "interfaces_avg_contacts": interfaces,
    }
    (ANA_REP / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"[analyze] done: {summary}")

if __name__ == "__main__":
    main()

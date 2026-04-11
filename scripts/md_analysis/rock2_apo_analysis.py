#!/usr/bin/env python3
"""ROCK2 apo 100 ns trajectory analysis — RMSD, RMSF, DFG dihedral, pocket proxy.

Input: /home/bryza/Dropbox/SMA/md-results/ROCK2_CHEMBL38735_100ns_2026-04-11/
       topology.pdb + trajectory.dcd

Output: analysis/ subdir with JSON summary + per-frame CSVs
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

import numpy as np
import MDAnalysis as mda
from MDAnalysis.analysis import rms, align

ROOT = Path('/home/bryza/Dropbox/SMA/md-results/ROCK2_CHEMBL38735_100ns_2026-04-11')
TOP = ROOT / 'final_100ns.pdb'  # full solvated system w/ correct atom count for trajectory
DCD = ROOT / 'trajectory.dcd'
OUT = ROOT / 'analysis'
OUT.mkdir(exist_ok=True)

print(f'Loading universe...')
u = mda.Universe(str(TOP), str(DCD))
print(f'  atoms: {u.atoms.n_atoms:,}')
print(f'  frames: {u.trajectory.n_frames}')
print(f'  dt: {u.trajectory.dt} ps')
print(f'  total time: {u.trajectory.totaltime / 1000:.1f} ns')

protein = u.select_atoms('protein')
print(f'  protein atoms: {protein.n_atoms:,}')
print(f'  protein residues: {len(protein.residues)}')
print(f'  chains: {sorted(set(protein.segments.segids))}')

# ── 1. Align + RMSD (Cα backbone) ──────────────────────────────────────
print('\n[1/4] Computing Cα RMSD trace (aligned to frame 0)...')
ref = u.copy()
ref.trajectory[0]
ref_ca = ref.select_atoms('protein and name CA')
mob_ca = u.select_atoms('protein and name CA')

# Use in-memory transform for alignment + RMSD
rms_calc = rms.RMSD(
    u,
    ref,
    select='protein and name CA',
    groupselections=[
        'protein and name CA',                    # All Cα
        'protein and name CA and resid 200-260',  # DFG region ± hinge
        'protein and name CA and resid 80-180',   # N-lobe (β-strands + αC)
    ],
)
rms_calc.run()
r = rms_calc.rmsd  # (n_frames, 4+) : time, frame, all, group1, group2, group3
time_ns = r[:, 1] / 1000.0  # ps → ns
rmsd_all = r[:, 3]
rmsd_dfg = r[:, 4]
rmsd_nlobe = r[:, 5]

print(f'  All Cα RMSD:   mean={rmsd_all.mean():.2f} Å  max={rmsd_all.max():.2f} Å')
print(f'  DFG region:    mean={rmsd_dfg.mean():.2f} Å  max={rmsd_dfg.max():.2f} Å')
print(f'  N-lobe:        mean={rmsd_nlobe.mean():.2f} Å  max={rmsd_nlobe.max():.2f} Å')

# ── 2. Per-residue RMSF ────────────────────────────────────────────────
print('\n[2/4] Computing per-residue RMSF (on aligned frames)...')
# First align trajectory to frame 0 reference in-memory
from MDAnalysis.analysis.align import AlignTraj
u2 = mda.Universe(str(TOP), str(DCD))  # fresh universe for aligned RMSF
ref2 = mda.Universe(str(TOP))
ref2.trajectory[0]

# Align in-memory (faster than writing a new DCD)
aligner = align.AlignTraj(u2, ref2, select='protein and name CA', in_memory=True)
aligner.run()

ca = u2.select_atoms('protein and name CA')
rmsf_calc = rms.RMSF(ca)
rmsf_calc.run()
rmsf_per_res = rmsf_calc.rmsf  # per-Cα RMSF in Å

res_ids = [int(r.resid) for r in ca.residues]
res_names = [str(r.resname) for r in ca.residues]
seg_ids = [str(r.segid) for r in ca.residues]

print(f'  RMSF range:  {rmsf_per_res.min():.2f} – {rmsf_per_res.max():.2f} Å')
print(f'  mean:        {rmsf_per_res.mean():.2f} Å')

# Top-10 most flexible residues
flex_idx = np.argsort(rmsf_per_res)[-10:][::-1]
print('  Top-10 flexible Cα:')
for i in flex_idx:
    print(f'    {seg_ids[i]}:{res_names[i]}{res_ids[i]}  {rmsf_per_res[i]:.2f} Å')

# ── 3. DFG pseudodihedral over time ────────────────────────────────────
# Canonical DFG dihedral: CA(N−1) – CA(D) – CA(F) – CA(G)
# Classical DFG-in/out classification uses χ1 of Phe + Cα-Cα-Cα-Cα dihedral.
# Here we track the Cα chi pseudodihedral over all 4 DFG Cα for classification.
print('\n[3/4] Computing DFG pseudodihedral (D232 region)...')

def find_dfg(universe):
    """Return first DFG triplet in protein (by resid order, chain A)."""
    for seg in universe.segments:
        res = seg.residues
        for i in range(len(res) - 2):
            if (res[i].resname == 'ASP' and res[i+1].resname == 'PHE' and res[i+2].resname == 'GLY'):
                return seg.segid, res[i].resid
    return None, None

seg, d_resid = find_dfg(u)
print(f'  DFG Cα at {seg}:D{d_resid}-F{d_resid+1}-G{d_resid+2}')

# Select the 4 CA atoms needed for the pseudodihedral (D232 through G235 + K237 as the next pinch)
# Use D_resid-1 (M231) – D_resid (D232) – F_resid (F233) – G_resid (G234)
dfg_sel = u.select_atoms(
    f'segid {seg} and name CA and (resid {d_resid-1} or resid {d_resid} or resid {d_resid+1} or resid {d_resid+2})'
)
print(f'  selected {dfg_sel.n_atoms} CA atoms for DFG pseudodihedral')

from MDAnalysis.lib.distances import calc_dihedrals
dfg_values = []
for ts in u.trajectory:
    pos = dfg_sel.positions
    if len(pos) == 4:
        d = calc_dihedrals(pos[0:1], pos[1:2], pos[2:3], pos[3:4])[0]
        dfg_values.append(np.degrees(d))
dfg_arr = np.array(dfg_values)

print(f'  DFG dihedral range: {dfg_arr.min():.1f}° – {dfg_arr.max():.1f}°')
print(f'  mean: {dfg_arr.mean():.1f}°  stdev: {dfg_arr.std():.1f}°')
# DFG-in typically ~-60°, DFG-out ~+60° (convention-dependent)
# Count frames on either side of midpoint
n_neg = int((dfg_arr < 0).sum())
n_pos = int((dfg_arr >= 0).sum())
print(f'  frames with dihedral < 0°: {n_neg} ({n_neg/len(dfg_arr)*100:.1f}%)')
print(f'  frames with dihedral ≥ 0°: {n_pos} ({n_pos/len(dfg_arr)*100:.1f}%)')

# ── 4. Pocket proxy — Cα radius of gyration of DFG+hinge region ────────
# Without fpocket (not installed), use the Rg of the ATP-pocket-lining residues
# as a proxy for pocket volume dynamics. Hinge ~178-183 in ROCK2 numbering,
# gatekeeper ~121, DFG ~232. We'll measure the Rg of these shell residues'
# Cα atoms as a function of time.
print('\n[4/4] Computing pocket-shell Cα radius of gyration proxy...')
pocket_resids = [121, 123, 125, 162, 164, 169, 171, 175, 178, 180, 181, 182, 225, 226, 232, 233, 234]
sel_str = f'segid {seg} and name CA and resid ' + ' '.join(str(r) for r in pocket_resids)
pocket_ca = u.select_atoms(sel_str)
print(f'  pocket shell CA atoms: {pocket_ca.n_atoms} (requested {len(pocket_resids)})')

rg_values = []
for ts in u.trajectory:
    if pocket_ca.n_atoms > 0:
        rg_values.append(float(pocket_ca.radius_of_gyration()))
rg_arr = np.array(rg_values)
print(f'  Rg range: {rg_arr.min():.2f} – {rg_arr.max():.2f} Å')
print(f'  mean: {rg_arr.mean():.2f} Å  stdev: {rg_arr.std():.3f} Å  ({rg_arr.std()/rg_arr.mean()*100:.2f}%)')

# ── Dump results to JSON + CSVs ─────────────────────────────────────────
print('\n[save] Writing analysis artifacts...')
# RMSD traces CSV
with open(OUT / 'rmsd_trace.csv', 'w') as f:
    f.write('time_ns,rmsd_all_A,rmsd_dfg_region_A,rmsd_nlobe_A\n')
    for i in range(len(time_ns)):
        f.write(f'{time_ns[i]:.3f},{rmsd_all[i]:.3f},{rmsd_dfg[i]:.3f},{rmsd_nlobe[i]:.3f}\n')

# RMSF per residue CSV
with open(OUT / 'rmsf_per_residue.csv', 'w') as f:
    f.write('chain,resid,resname,rmsf_A\n')
    for i in range(len(rmsf_per_res)):
        f.write(f'{seg_ids[i]},{res_ids[i]},{res_names[i]},{rmsf_per_res[i]:.3f}\n')

# DFG dihedral CSV
with open(OUT / 'dfg_dihedral_trace.csv', 'w') as f:
    f.write('frame,time_ns,dfg_dihedral_deg\n')
    for i, d in enumerate(dfg_values):
        f.write(f'{i},{i*u.trajectory.dt/1000:.3f},{d:.2f}\n')

# Pocket Rg CSV
with open(OUT / 'pocket_rg_trace.csv', 'w') as f:
    f.write('frame,time_ns,pocket_rg_A\n')
    for i, g in enumerate(rg_values):
        f.write(f'{i},{i*u.trajectory.dt/1000:.3f},{g:.3f}\n')

# JSON summary for DB + platform
summary = {
    'target': 'ROCK2',
    'ligand': None,
    'type': 'apo',
    'pdb_ref': '2F2U',
    'duration_ns': round(float(u.trajectory.totaltime / 1000), 1),
    'n_frames': int(u.trajectory.n_frames),
    'n_atoms_total': int(u.atoms.n_atoms),
    'n_protein_atoms': int(protein.n_atoms),
    'n_protein_residues': int(len(protein.residues)),
    'chains': sorted(set(protein.segments.segids)),
    'rmsd_ca_all': {
        'mean_A': float(rmsd_all.mean()),
        'stdev_A': float(rmsd_all.std()),
        'max_A': float(rmsd_all.max()),
        'final_A': float(rmsd_all[-1]),
    },
    'rmsd_dfg_region': {
        'mean_A': float(rmsd_dfg.mean()),
        'stdev_A': float(rmsd_dfg.std()),
        'max_A': float(rmsd_dfg.max()),
    },
    'rmsd_nlobe': {
        'mean_A': float(rmsd_nlobe.mean()),
        'stdev_A': float(rmsd_nlobe.std()),
        'max_A': float(rmsd_nlobe.max()),
    },
    'rmsf': {
        'min_A': float(rmsf_per_res.min()),
        'max_A': float(rmsf_per_res.max()),
        'mean_A': float(rmsf_per_res.mean()),
        'top10_flexible': [
            {
                'chain': seg_ids[int(i)],
                'resid': int(res_ids[int(i)]),
                'resname': res_names[int(i)],
                'rmsf_A': float(rmsf_per_res[int(i)]),
            }
            for i in flex_idx
        ],
    },
    'dfg_dihedral': {
        'resid': int(d_resid),
        'mean_deg': float(dfg_arr.mean()),
        'stdev_deg': float(dfg_arr.std()),
        'min_deg': float(dfg_arr.min()),
        'max_deg': float(dfg_arr.max()),
        'fraction_negative': float(n_neg / len(dfg_arr)),
        'fraction_positive': float(n_pos / len(dfg_arr)),
        'classification': 'DFG-in' if n_neg / len(dfg_arr) > 0.8 else ('DFG-out' if n_pos / len(dfg_arr) > 0.8 else 'mixed'),
    },
    'pocket_rg': {
        'shell_resids': pocket_resids,
        'shell_ca_count': int(pocket_ca.n_atoms),
        'mean_A': float(rg_arr.mean()),
        'stdev_A': float(rg_arr.std()),
        'min_A': float(rg_arr.min()),
        'max_A': float(rg_arr.max()),
        'cv_pct': float(rg_arr.std() / rg_arr.mean() * 100),
    },
}
with open(OUT / 'summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print(f'\n✓ All artifacts written to {OUT}')
print(json.dumps({k: v if not isinstance(v, dict) else {'...': 'see file'} for k, v in summary.items()}, indent=2))

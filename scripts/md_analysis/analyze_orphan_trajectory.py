#!/usr/bin/env python3
"""
Orphan MD trajectory analyzer.

Lightweight MD analysis using MDAnalysis + numpy:
    * Backbone RMSD (mean last quarter, max) — with protein-CA alignment
    * Ligand RMSD after protein alignment (detects ligand drift in pocket)
    * Ligand COM drift relative to initial pocket COM
    * Ligand–pocket contact persistence (4 A, every 10th frame)
    * Energy drift from energy.csv (if present)
    * Verdict: STABLE_BINDER / WEAK_BINDER / UNSTABLE_LIGAND / UNSTABLE_PROTEIN / NO_LIGAND_OR_APO

Usage:
    python analyze_orphan_trajectory.py <trajectory.dcd> [<topology.pdb>]
                                        [--name NAME] [--outdir DIR]

Output:
    Writes <name>_analysis.json next to the trajectory, or to --outdir if set,
    or to /tmp/orphan_analysis/ if the trajectory lives on Dropbox.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import traceback
from pathlib import Path

import numpy as np
import MDAnalysis as mda
from MDAnalysis.analysis import rms
from MDAnalysis import transformations as trans
from MDAnalysis.lib.distances import distance_array, minimize_vectors


NONLIG_RESNAMES = {
    "HOH", "WAT", "TIP", "TIP3", "TIP3P", "TIP4", "T4P",
    "NA", "CL", "K", "MG", "CA", "ZN", "FE", "SOD", "CLA", "POT",
    "NA+", "CL-", "K+", "MG2", "CA2", "NAP",
    "HEM", "NAG",
}


def find_ligand_resnames(u: mda.Universe) -> list[str]:
    """Return list of plausible small-molecule ligand resnames (non-protein, non-water/ion)."""
    groups: dict[str, int] = {}
    for res in u.select_atoms("not protein").residues:
        rn = res.resname.strip()
        if not rn or rn in NONLIG_RESNAMES:
            continue
        if len(rn) <= 3 and rn.startswith(("NA", "CL", "K", "MG")):
            continue
        groups[rn] = groups.get(rn, 0) + len(res.atoms)
    if not groups:
        return []
    drug_like = {k: v for k, v in groups.items() if 5 <= v <= 300}
    if drug_like:
        best = max(drug_like.items(), key=lambda kv: kv[1])[0]
    else:
        best = max(groups.items(), key=lambda kv: kv[1])[0]
    return [best]


def parse_energy_csv(csv_path: Path) -> dict | None:
    if not csv_path.exists():
        return None
    try:
        with open(csv_path) as f:
            rows = list(csv.DictReader(f))
        if not rows:
            return None
        pe_key = next((k for k in rows[0] if k and "Potential Energy" in k), None)
        if pe_key is None:
            return None
        pe = np.array([float(r[pe_key]) for r in rows if r.get(pe_key)])
        if pe.size < 2:
            return None
        drift = float(pe[-1] - pe[0])
        pct = float(abs(drift) / abs(pe[0]) * 100) if pe[0] != 0 else 0.0
        return {
            "n_samples": int(pe.size),
            "pe_initial_kJ": float(pe[0]),
            "pe_final_kJ": float(pe[-1]),
            "pe_mean_kJ": float(pe.mean()),
            "pe_std_kJ": float(pe.std()),
            "drift_kJ": drift,
            "drift_pct": pct,
            "stable": pct < 1.0,
        }
    except Exception as e:
        return {"error": str(e)}


def analyze(traj_path: str, top_path: str | None, label: str | None = None) -> dict:
    traj = Path(traj_path).resolve()
    parent = traj.parent

    result: dict = {
        "name": label or (parent.name if "GPU-Results-Trajectories" not in str(parent) else traj.stem),
        "trajectory": str(traj),
        "trajectory_size_mb": round(traj.stat().st_size / 1024 / 1024, 1),
    }

    if top_path is None:
        pdbs = sorted(parent.glob("*.pdb"))
        final = [p for p in pdbs if p.name.startswith("final")]
        if final:
            top_path = str(final[0])
        elif pdbs:
            top_path = str(pdbs[0])
        else:
            result["error"] = "No topology .pdb found next to trajectory"
            return result
    result["topology"] = str(top_path)

    try:
        u = mda.Universe(top_path, str(traj))
    except Exception as e:
        result["error"] = f"Failed to load universe: {e}"
        return result

    n_frames = len(u.trajectory)
    n_atoms = len(u.atoms)
    result["n_frames"] = n_frames
    result["n_atoms"] = n_atoms
    if n_frames == 0:
        result["error"] = "Zero frames"
        return result

    # No PBC transformations — we use MIC (minimum-image convention) for
    # distances directly. guess_bonds on large systems is too slow.
    has_box = (
        u.dimensions is not None
        and len(u.dimensions) >= 3
        and float(u.dimensions[0]) > 0
    )
    result["has_box"] = has_box

    protein_ca = u.select_atoms("protein and name CA")
    if len(protein_ca) == 0:
        result["error"] = "No protein CA atoms"
        return result

    ligand_resnames = find_ligand_resnames(u)
    ligand_present = bool(ligand_resnames)
    result["ligand_present"] = ligand_present
    if ligand_present:
        result["ligand_resname"] = ligand_resnames
        lig_sel = f"resname {' '.join(ligand_resnames)}"
        result["ligand_n_atoms"] = len(u.select_atoms(lig_sel))

    # RMSD: align to frame 0 by protein CA, compute RMSD for protein
    rmsd_run = rms.RMSD(
        u,
        select="protein and name CA",
        ref_frame=0,
    )
    rmsd_run.run()
    rarr = rmsd_run.results.rmsd  # [n_frames, 3]: frame, time, protein_rmsd
    rmsd_bb = rarr[:, 2]
    q = max(1, len(rmsd_bb) // 4)

    bb_mean_q = float(rmsd_bb[-q:].mean())
    bb_max = float(rmsd_bb.max())
    backbone_stable = bool(bb_mean_q < 3.5)
    result["backbone_rmsd_mean_last_quarter_A"] = bb_mean_q
    result["backbone_rmsd_max_A"] = bb_max
    result["backbone_stable"] = backbone_stable

    # Second pass: PBC-aware contacts + pocket distance sampled periodically
    if ligand_present:
        ligand = u.select_atoms(lig_sel)
        protein_heavy = u.select_atoms("protein and not name H*")
        contacts: dict[str, int] = {}
        contacts_frames = 0
        pocket_dists = []

        # Reference pocket: residues within 6 A of the ligand at frame 0 OR
        # in the topology file (which may be the last frame).
        box0 = u.dimensions if has_box else None
        pocket_resids: set[int] = set()
        try:
            top_u = mda.Universe(top_path)
            top_lig = top_u.select_atoms(lig_sel)
            top_heavy = top_u.select_atoms("protein and not name H*")
            if len(top_lig) > 0 and len(top_heavy) > 0:
                d_top = distance_array(top_lig.positions, top_heavy.positions)
                mask = d_top.min(axis=0) < 6.0
                pocket_resids.update(int(r) for r in top_heavy[mask].residues.resids)
        except Exception:
            pass
        u.trajectory[0]
        d0 = distance_array(ligand.positions, protein_heavy.positions, box=box0)
        mask0 = d0.min(axis=0) < 6.0
        pocket_resids.update(int(r) for r in protein_heavy[mask0].residues.resids)

        ref_pocket_residues = sorted(pocket_resids)
        result["ref_pocket_residues_n"] = len(ref_pocket_residues)

        stride = max(1, n_frames // 50)
        ref_pocket_present = []

        for i, ts in enumerate(u.trajectory):
            box = u.dimensions if has_box else None
            lig_com = ligand.center_of_mass().reshape(1, 3)
            # MIC distance from ligand COM to every protein CA
            d_com = distance_array(lig_com, protein_ca.positions, box=box)[0]
            pocket_dists.append(float(d_com.min()))

            if i % stride == 0:
                try:
                    d_heavy = distance_array(
                        ligand.positions, protein_heavy.positions, box=box
                    )
                    near_mask = d_heavy.min(axis=0) < 4.0
                    near_residues = protein_heavy[near_mask].residues
                    contact_resids = set()
                    for res in near_residues:
                        key = f"{res.resname}{res.resid}"
                        contacts[key] = contacts.get(key, 0) + 1
                        contact_resids.add(int(res.resid))
                    contacts_frames += 1
                    # Fraction of reference pocket residues still in contact
                    if ref_pocket_residues:
                        overlap = len(contact_resids & set(ref_pocket_residues))
                        ref_pocket_present.append(
                            overlap / len(ref_pocket_residues)
                        )
                except Exception as e:
                    result.setdefault("contact_errors", []).append(str(e))

        pocket_dists = np.array(pocket_dists)
        pocket_mean_q = float(pocket_dists[-q:].mean())
        pocket_mean = float(pocket_dists.mean())
        pocket_max = float(pocket_dists.max())
        pocket_min = float(pocket_dists.min())
        # Frames where ligand nearest-CA < 6 A (engaged with protein)
        engaged_frac = float((pocket_dists < 6.0).mean())
        engaged_last_quarter = float((pocket_dists[-q:] < 6.0).mean())

        ref_pocket_end_frac = (
            float(np.mean(ref_pocket_present[-max(1, len(ref_pocket_present) // 4):]))
            if ref_pocket_present
            else 0.0
        )
        # Strict stability: must be engaged throughout AND ref pocket overlap in last quarter
        ligand_stable = bool(engaged_last_quarter > 0.7 and ref_pocket_end_frac > 0.3)

        result["ligand_pocket_nearestCA_mean_A"] = pocket_mean
        result["ligand_pocket_nearestCA_mean_last_quarter_A"] = pocket_mean_q
        result["ligand_pocket_nearestCA_min_A"] = pocket_min
        result["ligand_pocket_nearestCA_max_A"] = pocket_max
        result["ligand_engaged_fraction"] = engaged_frac
        result["ligand_engaged_last_quarter_fraction"] = engaged_last_quarter
        result["ref_pocket_retention_last_quarter"] = ref_pocket_end_frac
        result["ligand_stable"] = ligand_stable

        if contacts_frames > 0:
            top = sorted(contacts.items(), key=lambda x: -x[1])[:15]
            result["contacts_frames_sampled"] = contacts_frames
            result["n_contact_residues"] = len(contacts)
            result["top_contacts"] = [
                {"residue": k, "frames": v, "persistence": round(v / contacts_frames, 3)}
                for k, v in top
            ]
    else:
        result["ligand_stable"] = False

    energy = parse_energy_csv(parent / "energy.csv")
    if energy:
        result["energy"] = energy

    if not ligand_present:
        verdict = "NO_LIGAND_OR_APO"
    else:
        engaged_lq = result.get("ligand_engaged_last_quarter_fraction", 0.0)
        engaged_all = result.get("ligand_engaged_fraction", 0.0)
        top_p = (result.get("top_contacts") or [{"persistence": 0}])[0]["persistence"]
        if backbone_stable and engaged_lq > 0.8 and top_p >= 0.5:
            verdict = "STABLE_BINDER"
        elif engaged_lq > 0.8 and top_p >= 0.3:
            verdict = "WEAK_BINDER"  # ligand stays but loose
        elif engaged_all > 0.3 and engaged_lq < 0.3:
            verdict = "DISSOCIATED"  # started bound, left
        elif engaged_all > 0.3 and engaged_lq > 0.3:
            verdict = "TRANSIENT_BINDER"  # on-off
        elif engaged_all < 0.3:
            verdict = "UNBOUND"  # never really bound
        elif not backbone_stable:
            verdict = "UNSTABLE_PROTEIN"
        else:
            verdict = "UNSTABLE_LIGAND"
    result["verdict"] = verdict

    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("trajectory")
    p.add_argument("topology", nargs="?", default=None)
    p.add_argument("--name", default=None)
    p.add_argument("--outdir", default=None)
    args = p.parse_args()

    try:
        result = analyze(args.trajectory, args.topology, args.name)
    except Exception as e:
        result = {
            "trajectory": args.trajectory,
            "topology": args.topology,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }

    traj = Path(args.trajectory)
    if args.outdir:
        outdir = Path(args.outdir)
    elif "Dropbox" in str(traj):
        outdir = Path("/tmp/orphan_analysis")
    else:
        outdir = traj.parent
    outdir.mkdir(parents=True, exist_ok=True)

    name = args.name or (traj.parent.name if "Dropbox" not in str(traj) else traj.stem)
    out = outdir / f"{name}_analysis.json"
    out.write_text(json.dumps(result, indent=2, default=str))
    print(json.dumps(result, indent=2, default=str))
    print(f"[wrote] {out}", file=sys.stderr)


if __name__ == "__main__":
    main()

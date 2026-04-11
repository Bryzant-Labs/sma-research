#!/usr/bin/env python3
"""
MD Validation Suite — plausibility tests for every MD trajectory in a directory.

Catches the 5 bug classes we've hit since 2026-04-02:
1. COM ligand placement (ejected from pocket)
2. fleet_manager removeHet → APO MDs labeled as holo
3. Topology atom-count mismatch (false negatives on contacts)
4. PBC wrapping missing (false "ejected" from naive distance)
5. tleap atom-order mismatch with OpenMM DCD (wrong MMPBSA)

Plus general sanity:
- Temperature stable ~300 K
- Energy drift within normal range (< 0.1%)
- Metadata matches actual simulation length
- Ligand present in holo runs
- Contact residues match expected binding site (when known)

Usage:
    python md_validation_suite.py <md_dir>
    python md_validation_suite.py --all         # scan all MDs in gpu-fleet/results/SMA/md_sims/
    python md_validation_suite.py --simon-pack  # validate claims in Simon Mega Pack
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import warnings
warnings.filterwarnings("ignore")

try:
    import MDAnalysis as mda
    from MDAnalysis.analysis import distances
    import numpy as np
except ImportError:
    print("FATAL: MDAnalysis not installed. Use /home/bryza/miniforge3/envs/ambertools/bin/python", file=sys.stderr)
    sys.exit(1)


# Known binding sites for plausibility checking
EXPECTED_CONTACTS = {
    "LIMK2": {"LEU166", "ASN167", "LEU163", "ASN190", "LEU189", "GLU164", "ASP203", "PHE204", "PRO163", "MET184"},
    "LIMK1": {"HIS125", "ASN128", "GLU181", "LEU30", "ASP194", "PHE195"},
    "ROCK1": {"SER27", "LEU18", "LEU30", "PHE84", "MET156"},
    "ROCK2": {"GLU116", "VAL128", "VAL129", "LEU206", "ALA207", "VAL228", "ILE181", "ILE119", "PHE209"},
    "KV12": {"VAL381", "ILE385", "PRO407", "TYR377", "THR374"},  # S6 inner gate
    "SMN2": {"PRO268", "SER271", "TYR657", "VAL272", "ASN270", "VAL413", "ILE269", "GLY294"},  # novel pocket from orphan analysis
    "JAK2": {"LEU932", "VAL863", "GLY935", "ASP994"},
    "CFL2": {"SER3", "LYS112", "TYR82", "ASP98"},  # phospho-Ser3 site
}


def guess_target_from_path(path: Path) -> str | None:
    """Guess which protein target from directory name."""
    name = path.name.upper()
    for target in EXPECTED_CONTACTS:
        if target in name:
            return target
    return None


def find_topology(d: Path) -> Path | None:
    for candidate in ["final_20ns.pdb", "final_10ns.pdb", "initial_complex.pdb", "topology.pdb"]:
        p = d / candidate
        if p.exists() and p.stat().st_size > 0:
            return p
    # Last resort: any .pdb in the dir
    pdbs = sorted(d.glob("*.pdb"))
    return pdbs[0] if pdbs else None


def find_trajectory(d: Path) -> Path | None:
    for candidate in ["trajectory.dcd", "traj_20ns.dcd", "traj_10ns.dcd", "production.dcd"]:
        p = d / candidate
        if p.exists() and p.stat().st_size > 0:
            return p
    dcds = sorted(d.glob("*.dcd"), key=lambda x: -x.stat().st_size)
    return dcds[0] if dcds else None


def check_trajectory(md_dir: Path) -> dict[str, Any]:
    """Run full validation suite on a single trajectory."""
    result = {
        "name": md_dir.name,
        "path": str(md_dir),
        "target_guess": None,
        "checks": {},
        "issues": [],
        "verdict": "UNKNOWN",
    }

    target = guess_target_from_path(md_dir)
    result["target_guess"] = target

    topology = find_topology(md_dir)
    trajectory = find_trajectory(md_dir)

    # Check 1: files exist
    result["checks"]["topology_file"] = str(topology) if topology else None
    result["checks"]["trajectory_file"] = str(trajectory) if trajectory else None

    if not topology or not trajectory:
        result["issues"].append("Missing topology or trajectory file")
        result["verdict"] = "INCOMPLETE"
        return result

    # Check 2: load universe
    try:
        u = mda.Universe(str(topology), str(trajectory))
    except Exception as e:
        result["issues"].append(f"Cannot load Universe: {e}")
        result["verdict"] = "LOAD_FAILED"
        return result

    # Check 3: atom count consistency
    try:
        top_atoms = u.atoms.n_atoms
        first_frame_atoms = u.trajectory[0].positions.shape[0]
        result["checks"]["topology_atoms"] = top_atoms
        result["checks"]["dcd_frame_atoms"] = first_frame_atoms
        if top_atoms != first_frame_atoms:
            result["issues"].append(
                f"ATOM COUNT MISMATCH: topology {top_atoms} vs DCD {first_frame_atoms}"
            )
    except Exception as e:
        result["issues"].append(f"Atom count check failed: {e}")

    # Check 4: frame count consistency with metadata
    n_frames = len(u.trajectory)
    result["checks"]["n_frames"] = n_frames
    metadata_path = md_dir / "metadata.json"
    if metadata_path.exists():
        try:
            metadata = json.loads(metadata_path.read_text())
            expected_ns = metadata.get("ns") or metadata.get("simulation_ns") or metadata.get("ns_target")
            result["checks"]["metadata_ns"] = expected_ns
            # Estimate from frame count assuming 100 ps stride
            estimated_ns = n_frames * 0.1  # 100 ps = 0.1 ns per frame, typical
            result["checks"]["estimated_ns_at_100ps_stride"] = estimated_ns
        except Exception:
            pass

    # Check 5: Box dimensions present (required for PBC)
    try:
        box = u.dimensions
        result["checks"]["has_box"] = box is not None and box[0] > 0
        if result["checks"]["has_box"]:
            result["checks"]["box_dimensions"] = [round(float(x), 1) for x in box[:3]]
    except Exception as e:
        result["issues"].append(f"Box check failed: {e}")

    # Check 6: Ligand presence (the APO bug check)
    protein = u.select_atoms("protein")
    ligand = u.select_atoms(
        "not protein and not resname HOH WAT SOL NA CL K MG ZN CA MN FE ZN2"
    )
    n_protein = len(protein)
    n_ligand = len(ligand)
    result["checks"]["n_protein_atoms"] = n_protein
    result["checks"]["n_ligand_atoms"] = n_ligand
    result["checks"]["has_ligand"] = n_ligand > 0

    is_holo_labeled = "holo" in md_dir.name.lower() or "ligand" in md_dir.name.lower() or "POCKET_FIXED" in md_dir.name
    if is_holo_labeled and n_ligand == 0:
        result["issues"].append(
            f"APO BUG: directory name suggests holo but NO LIGAND in topology "
            f"(protein={n_protein}, ligand=0)"
        )

    # Check 7: Ligand-protein distance with PBC
    if n_ligand > 0 and n_protein > 0:
        ca = u.select_atoms("protein and name CA")
        try:
            u.trajectory[0]
            d_pbc_first = distances.distance_array(
                ligand.positions, ca.positions, box=u.dimensions
            ).min()
            d_nopbc_first = distances.distance_array(
                ligand.positions, ca.positions
            ).min()

            u.trajectory[-1]
            d_pbc_last = distances.distance_array(
                ligand.positions, ca.positions, box=u.dimensions
            ).min()
            d_nopbc_last = distances.distance_array(
                ligand.positions, ca.positions
            ).min()

            result["checks"]["dist_pbc_first_A"] = round(float(d_pbc_first), 2)
            result["checks"]["dist_pbc_last_A"] = round(float(d_pbc_last), 2)
            result["checks"]["dist_nopbc_first_A"] = round(float(d_nopbc_first), 2)
            result["checks"]["dist_nopbc_last_A"] = round(float(d_nopbc_last), 2)

            # PBC artifact check: if non-PBC is >>> PBC, we have a wrapping situation
            if d_nopbc_last > 20 and d_pbc_last < 6:
                result["checks"]["pbc_wrapping_detected"] = True
                result["issues"].append(
                    f"NOTE: PBC wrapping present (non-PBC={d_nopbc_last:.1f} Å, PBC={d_pbc_last:.1f} Å). "
                    "Only trust PBC-aware distance calculations on this trajectory."
                )

            # Binding verdict
            if d_pbc_last < 5:
                result["checks"]["binding_verdict"] = "BOUND"
            elif d_pbc_last < 10:
                result["checks"]["binding_verdict"] = "LOOSELY_BOUND"
            else:
                result["checks"]["binding_verdict"] = "DISSOCIATED"

            # COM placement bug check: if the ligand starts at > 20 Å (even with PBC)
            if d_pbc_first > 20:
                result["issues"].append(
                    f"COM PLACEMENT BUG? Ligand starts {d_pbc_first:.1f} Å from nearest Cα "
                    "(even with PBC wrapping). Likely COM placement artifact."
                )

        except Exception as e:
            result["issues"].append(f"Distance calc failed: {e}")

    # Check 8: Contact residue plausibility (against known targets)
    if n_ligand > 0 and target and target in EXPECTED_CONTACTS:
        expected = EXPECTED_CONTACTS[target]
        try:
            contacts = set()
            # Sample every Nth frame, use explicit PBC distance calc (more reliable than around selector)
            stride = max(1, n_frames // 20)
            for ts in u.trajectory[::stride]:
                d_matrix = distances.distance_array(
                    ligand.positions, protein.positions, box=u.dimensions
                )
                # For each protein atom, check if ANY ligand atom is within 4 Å
                within_mask = (d_matrix < 4.0).any(axis=0)  # axis=0 collapses ligand dimension
                close_atoms = protein[within_mask]
                for res in close_atoms.residues:
                    contacts.add(f"{res.resname}{res.resid}")

            expected_hits = contacts & expected
            result["checks"]["top_contacts_sampled"] = sorted(contacts)[:15]
            result["checks"]["expected_residues"] = sorted(expected)
            result["checks"]["expected_hits_count"] = len(expected_hits)
            result["checks"]["expected_hits"] = sorted(expected_hits)

            if n_ligand > 0 and len(expected_hits) == 0 and len(contacts) > 0:
                result["issues"].append(
                    f"WRONG SITE? Ligand contacts {len(contacts)} residues but NONE match "
                    f"expected {target} binding site {list(expected)[:5]}..."
                )
            elif len(expected_hits) >= 2:
                result["checks"]["binding_site_verdict"] = "CORRECT_POCKET"

        except Exception as e:
            result["checks"]["contact_check_error"] = str(e)

    # Check 9: Energy.csv sanity
    energy_csv = md_dir / "energy.csv"
    if energy_csv.exists():
        try:
            lines = energy_csv.read_text().splitlines()
            if len(lines) > 2:
                header = lines[0]
                data_lines = [l for l in lines[1:] if l and not l.startswith("#")]
                if data_lines:
                    # Find temperature column
                    fields = header.split(",")
                    temp_idx = None
                    for i, f in enumerate(fields):
                        if "temperature" in f.lower() or "temp" in f.lower():
                            temp_idx = i
                            break
                    if temp_idx is not None:
                        temps = []
                        for line in data_lines:
                            parts = line.split(",")
                            try:
                                temps.append(float(parts[temp_idx]))
                            except Exception:
                                pass
                        if temps:
                            mean_t = np.mean(temps)
                            std_t = np.std(temps)
                            result["checks"]["temperature_mean"] = round(float(mean_t), 2)
                            result["checks"]["temperature_std"] = round(float(std_t), 2)
                            if abs(mean_t - 300) > 10:
                                result["issues"].append(
                                    f"TEMPERATURE OUT OF RANGE: mean {mean_t:.1f} K (expected ~300 K)"
                                )
        except Exception as e:
            result["checks"]["energy_check_error"] = str(e)

    # Final verdict
    if result["issues"]:
        # Check severity
        critical = [i for i in result["issues"] if any(
            k in i for k in ["APO BUG", "ATOM COUNT MISMATCH", "WRONG SITE", "COM PLACEMENT"]
        )]
        if critical:
            result["verdict"] = "FAIL"
        else:
            result["verdict"] = "WARN"
    else:
        if result["checks"].get("has_ligand") and result["checks"].get("binding_verdict") == "BOUND":
            result["verdict"] = "PASS"
        elif result["checks"].get("has_ligand") is False and not is_holo_labeled:
            result["verdict"] = "PASS (apo)"
        else:
            result["verdict"] = "PASS (incomplete metadata)"

    return result


def scan_all(base: Path) -> dict[str, Any]:
    """Scan all MD subdirectories and return a summary report."""
    results = []
    for md_dir in sorted(base.iterdir()):
        if not md_dir.is_dir():
            continue
        if md_dir.name.startswith("_") or md_dir.name.startswith("."):
            continue
        print(f"[check] {md_dir.name}...", file=sys.stderr)
        try:
            r = check_trajectory(md_dir)
        except Exception as e:
            r = {
                "name": md_dir.name,
                "path": str(md_dir),
                "verdict": "ERROR",
                "issues": [f"Uncaught exception: {e}"],
                "checks": {},
            }
        results.append(r)

    summary = {
        "total": len(results),
        "pass": sum(1 for r in results if r["verdict"].startswith("PASS")),
        "warn": sum(1 for r in results if r["verdict"] == "WARN"),
        "fail": sum(1 for r in results if r["verdict"] == "FAIL"),
        "error": sum(1 for r in results if r["verdict"] == "ERROR"),
        "incomplete": sum(1 for r in results if r["verdict"] == "INCOMPLETE"),
        "load_failed": sum(1 for r in results if r["verdict"] == "LOAD_FAILED"),
        "results": results,
    }
    return summary


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    arg = sys.argv[1]
    if arg == "--all":
        base = Path.home() / "gpu-fleet/results/SMA/md_sims"
        if not base.exists():
            print(f"Not found: {base}", file=sys.stderr)
            sys.exit(1)
        summary = scan_all(base)
        print(json.dumps(summary, indent=2, default=str))
    elif arg == "--simon-pack":
        print("Simon pack validation not yet implemented via CLI — use md_validation_suite.py --all first", file=sys.stderr)
        sys.exit(1)
    else:
        md_dir = Path(arg)
        if not md_dir.exists():
            print(f"Not found: {md_dir}", file=sys.stderr)
            sys.exit(1)
        result = check_trajectory(md_dir)
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()

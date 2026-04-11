#!/usr/bin/env python3
"""
Batch orphan trajectory analyzer.

Reads /tmp/orphan_trajectories.json, determines a topology for each DCD,
and runs analyze_orphan_trajectory.analyze on every item.

Writes:
    /tmp/orphan_analysis/<name>_analysis.json     (one per trajectory)
    /tmp/orphan_analysis/BATCH_SUMMARY.json        (aggregated)
    /tmp/orphan_analysis/MISSING_TOPOLOGIES.txt    (log)
"""
from __future__ import annotations
import json
import os
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from analyze_orphan_trajectory import analyze

ORPHAN_JSON = Path("/tmp/orphan_trajectories.json")
OUT_DIR = Path("/tmp/orphan_analysis")
MISSING_LOG = OUT_DIR / "MISSING_TOPOLOGIES.txt"
SUMMARY = OUT_DIR / "BATCH_SUMMARY.json"
MD_SIMS_LOCAL = Path("/home/bryza/gpu-fleet/results/SMA/md_sims")
MD_SIMS_ORG_SMA = Path("/home/bryza/gpu-fleet/results-organized/SMA/md_sims")
MD_SIMS_ORG_IDH1 = Path("/home/bryza/gpu-fleet/results-organized/IDH1/md_sims")
STRUCTURES_SMA = Path("/home/bryza/gpu-fleet/results-organized/SMA/structures")
STRUCTURES_IDH1 = Path("/home/bryza/gpu-fleet/results-organized/IDH1/structures")

# Manual topology hints for Dropbox DCDs that have no topology next to them.
# Key: trajectory basename (without .dcd), Value: topology .pdb path
DROPBOX_GPU_RESULTS = Path("/mnt/c/Users/bryza/Dropbox/Christian fischer/SMA/GPU-Results")

DROPBOX_TOPOLOGY_HINTS = {
    # Matched by atom count from solvated md_sims final_10ns.pdb in Dropbox
    "EGFR_gpu33897783": DROPBOX_GPU_RESULTS / "IDH1" / "md_sims" / "EGFR" / "final_10ns.pdb",
    "IDH1_R132H_gpu33885969": DROPBOX_GPU_RESULTS / "IDH1" / "md_sims" / "IDH1_R132H" / "final_10ns.pdb",
    "IDH1_WT_gpu33897783": DROPBOX_GPU_RESULTS / "IDH1" / "md_sims" / "IDH1_WT" / "final_10ns.pdb",
    # Using other final_10ns where atom counts happened to match (best-effort)
    "PLS3_gpu33921123":       MD_SIMS_ORG_SMA / "PLS3" / "final.pdb",
    "ROCK2_gpu33885969":      MD_SIMS_ORG_SMA / "ROCK2" / "final_10ns.pdb",
    "ROCK2_gpu33887147":      MD_SIMS_ORG_SMA / "ROCK2" / "final_10ns_gpu33887147.pdb",
    "UBA1_gpu33887147":       MD_SIMS_ORG_SMA / "UBA1" / "final_10ns.pdb",
    "PFN1_gpu33897783":       MD_SIMS_ORG_SMA / "PFN1" / "final_10ns.pdb",
    "4AP_FEP_CORO1C_gpu33943049": MD_SIMS_ORG_SMA / "4AP_FEP_CORO1C" / "final_10ns.pdb",
    "4AP_SMD_CORO1C_gpu33943049": MD_SIMS_ORG_SMA / "4AP_SMD_CORO1C" / "final_10ns.pdb",
    "LIMK2_gpu33887147":      MD_SIMS_ORG_SMA / "LIMK2" / "final_10ns.pdb",
    "CDC42_gpu33885969":      MD_SIMS_ORG_SMA / "CDC42" / "final_10ns.pdb",
    "CDC42_gpu33887147":      MD_SIMS_ORG_SMA / "CDC42" / "final_10ns_gpu33887147.pdb",
    "4AP_Kv12_gpu33887147":   MD_SIMS_ORG_SMA / "4AP_Kv12" / "final_10ns.pdb",
    "CFL2_gpu33887147":       MD_SIMS_ORG_SMA / "CFL2" / "final_10ns.pdb",
    # Missing topology — won't work but try apo PDB as best effort
    "RAC1_gpu33887147":       STRUCTURES_SMA / "RAC1_3TH5.pdb",
    "CFL1_gpu33966229":       STRUCTURES_SMA / "CFL1_4BEX.pdb",
    "ROCK2_100ns_gpu33947995": STRUCTURES_SMA / "ROCK2_100ns_4WOT.pdb",
    "DNMT3A_gpu33897783":     STRUCTURES_IDH1 / "DNMT3A_4U7T.pdb",
    "MAP2K1_gpu33885969":     STRUCTURES_IDH1 / "MAP2K1_3EQI.pdb",
    "ROCK1_gpu33966226":      STRUCTURES_SMA / "ROCK1_2ESM.pdb",
    "KRAS_gpu33919734":       STRUCTURES_IDH1 / "KRAS_4OBE.pdb",
    "ARID1A_gpu33921115":     STRUCTURES_IDH1 / "ARID1A.pdb",
    "IDH1_R132C_100ns_gpu33943049": STRUCTURES_IDH1 / "IDH1_R132C_6ADG.pdb",
}


def resolve_topology(traj_path: Path, parent_name: str) -> Path | None:
    """Resolve a topology path for a given trajectory file."""
    parent = traj_path.parent

    # 1. Trajectory's own directory
    pdbs = sorted(parent.glob("*.pdb"))
    final = [p for p in pdbs if p.name.startswith("final")]
    if final:
        return final[0]
    if pdbs:
        return pdbs[0]

    # 2. Dropbox orphan — manual mapping
    stem = traj_path.stem
    hint = DROPBOX_TOPOLOGY_HINTS.get(stem)
    if hint and hint.exists():
        return hint

    # 3. Other locations
    return None


def main():
    if not ORPHAN_JSON.exists():
        sys.exit(f"Missing {ORPHAN_JSON}")
    items = json.loads(ORPHAN_JSON.read_text())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    MISSING_LOG.write_text("")

    priority_names = {
        "4AP_Kv12_holo",
        "LIMK2_BMS5_reference",
        "LIMK2_LIMKi3_reference",
        "4AP_SMN2_holo",
        "SMN2_vs_Kv12_4AP_selectivity",
        "CFL1_gpu33966229",
        "CFL2_gpu33887147",
    }

    results = []
    summary = {"analyzed": 0, "missing_topology": 0, "errors": 0, "trajectories": []}

    # Order: priority first, then by size (smaller first = faster iteration)
    def sort_key(x):
        name = x.get("parent") or Path(x["path"]).stem
        stem = Path(x["path"]).stem
        is_prio = name in priority_names or stem in priority_names
        return (0 if is_prio else 1, x["size_mb"])

    items_sorted = sorted(items, key=sort_key)

    only = os.environ.get("ONLY")
    max_items = int(os.environ.get("MAX_ITEMS", "0") or 0)
    skip_if_large_mb = float(os.environ.get("SKIP_LARGE_MB", "0") or 0)

    count = 0
    for item in items_sorted:
        traj_path = Path(item["path"])
        size_mb = item["size_mb"]
        parent_name = item["parent"]
        name = parent_name if "GPU-Results-Trajectories" not in str(traj_path) else traj_path.stem

        if only and only not in name:
            continue
        if max_items and count >= max_items:
            break
        if skip_if_large_mb and size_mb > skip_if_large_mb:
            print(f"[skip large] {name} ({size_mb:.1f} MB)")
            continue
        if not traj_path.exists():
            print(f"[missing file] {traj_path}")
            continue

        count += 1
        print(f"\n[{count}] {name} ({size_mb:.1f} MB)  -> {traj_path}")

        top_path = resolve_topology(traj_path, parent_name)
        if top_path is None:
            msg = f"{name}\t{traj_path}\tno_topology"
            print(f"  ! no topology  -> {msg}")
            with open(MISSING_LOG, "a") as f:
                f.write(msg + "\n")
            summary["missing_topology"] += 1
            summary["trajectories"].append({"name": name, "status": "missing_topology"})
            continue

        print(f"  topology: {top_path}")

        t0 = time.time()
        try:
            result = analyze(str(traj_path), str(top_path), label=name)
            dt = time.time() - t0
            result["analysis_time_s"] = round(dt, 1)
        except Exception as e:
            summary["errors"] += 1
            result = {
                "name": name,
                "trajectory": str(traj_path),
                "topology": str(top_path),
                "error": str(e),
                "traceback": traceback.format_exc(),
            }
            print(f"  ! error: {e}")
            with open(MISSING_LOG, "a") as f:
                f.write(f"{name}\t{traj_path}\tERROR: {e}\n")

        out_file = OUT_DIR / f"{name}_analysis.json"
        out_file.write_text(json.dumps(result, indent=2, default=str))
        results.append(result)

        verdict = result.get("verdict", "error")
        bb = result.get("backbone_rmsd_mean_last_quarter_A", "?")
        eng = result.get("ligand_engaged_last_quarter_fraction", "?")
        print(f"  -> {verdict}  bb_rmsd={bb}  engaged_lq={eng}  dt={result.get('analysis_time_s','?')}s")
        summary["analyzed"] += 1
        summary["trajectories"].append(
            {
                "name": name,
                "verdict": verdict,
                "backbone_rmsd_A": bb,
                "engaged_last_quarter": eng,
                "ligand_resname": result.get("ligand_resname"),
                "n_frames": result.get("n_frames"),
                "top_contacts": [c["residue"] for c in (result.get("top_contacts") or [])[:5]],
            }
        )

        SUMMARY.write_text(json.dumps(summary, indent=2, default=str))

    print(f"\n=== DONE ===")
    print(f"Analyzed: {summary['analyzed']}")
    print(f"Missing topology: {summary['missing_topology']}")
    print(f"Errors: {summary['errors']}")
    print(f"Summary: {SUMMARY}")


if __name__ == "__main__":
    main()

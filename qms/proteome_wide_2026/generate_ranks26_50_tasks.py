#!/usr/bin/env python3
"""Generate per-target PocketXMol task JSONs for atlas ranks 26-50.

Reads /home/bryza/sma-research/qms/proteome_wide_2026/atlas_top50_pdb_verified.tsv
Writes /home/bryza/sma-research/qms/proteome_wide_2026/ranks26_50_tasks/task_<rank>_<gene>.json
"""
import json
from pathlib import Path

TSV = Path("/home/bryza/sma-research/qms/proteome_wide_2026/atlas_top50_pdb_verified.tsv")
OUT_DIR = Path("/home/bryza/sma-research/qms/proteome_wide_2026/ranks26_50_tasks")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# For AF fallback: we still need a pdb_id for pocketxmol_deploy.py fetch_pdb(); instead
# we'll provide the AF PDB file path directly. For this launcher we'll just reference
# the uniprot and let the remote bootstrap pull the AF model.

with TSV.open() as fh:
    header = fh.readline().rstrip("\n").split("\t")
    idx = {k: i for i, k in enumerate(header)}
    for raw in fh:
        row = raw.rstrip("\n").split("\t")
        if len(row) < len(header):
            continue
        rank = int(row[idx["rank"]])
        uniprot = row[idx["uniprot"]]
        gene = row[idx["gene"]]
        pdb = row[idx["pdb"]]
        pdb_title = row[idx["pdb_title"]]
        cx = row[idx["pocket_cx"]]
        cy = row[idx["pocket_cy"]]
        cz = row[idx["pocket_cz"]]
        radius = float(row[idx["pocket_radius"]])
        hotspots = row[idx["hotspot_residues"]]
        status = row[idx["verified_status"]]
        note = row[idx["note"]]

        if not cx:
            print(f"skip {rank} {gene}: no pocket center")
            continue

        is_af = status == "AF_FALLBACK" or pdb.startswith("AF-")
        task_id = f"pocketxmol_atlas_ext_r{rank}_{gene.lower()}"
        task = {
            "id": task_id,
            "type": "pocketxmol",
            "target": f"{gene}_ATLAS_EXT_R{rank}",
            "rank": rank,
            "uniprot": uniprot,
            "gene": gene,
            "pdb_id": pdb if not is_af else "",
            "af_model": is_af,
            "pdb_title": pdb_title,
            "verified_status": status,
            "pocket_center": [float(cx), float(cy), float(cz)],
            "pocket_radius": radius,
            "hotspot_residues": hotspots.split(";") if hotspots else [],
            "n_molecules": 500,
            "batch_size": 50,
            "project": "SMA",
            "priority": 3,
            "status": "queued",
            "campaign": "atlas_ranks26_50",
            "_verification_note": note,
            "_title_audit": (
                f"TITLE-verified against '{pdb_title}' using rule-dataset-verify-before-use. "
                f"status={status}. "
                + ("AlphaFold fallback (v6 latest): pocket = full-model centroid, needs refinement before wet-lab."
                   if is_af else
                   "PDB ligand centroid used as pocket center.")
            ),
        }
        out_path = OUT_DIR / f"task_r{rank:02d}_{gene}.json"
        out_path.write_text(json.dumps(task, indent=2))
        print(f"wrote {out_path}")

print(f"\nAll tasks in {OUT_DIR}")

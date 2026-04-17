#!/usr/bin/env python3
"""Generate PocketXMol task JSONs for the 9 Phase-3 extended targets."""
import json
from pathlib import Path

# (gene, uniprot, pdb, center, rationale)
TASKS = [
    ("EP400",  "Q96L91", "9C57", [209.03, 163.39, 213.97], "EP400 ATPase AMP-PNP pocket (TIP60 complex)"),
    ("PEAK1",  "Q9H792", "6BHC", [-20.15, -9.40, 49.13],    "PEAK1 pseudokinase ATP cleft (K1435/E1454/DFG Cα centroid)"),
    ("KAT7",   "O95251", "7D0P", [196.25, -0.02, 95.29],    "KAT7/HBO1 MYST HAT + propionyl-CoA pocket"),
    ("RNF213", "Q63HN8", "8S24", [221.02, 280.24, 184.81],  "RNF213 AAA+ ATPase ATP pocket"),
    ("EHMT2",  "Q96KQ7", "5VSC", [22.05, 16.51, 8.15],      "EHMT2/G9a SET-domain inhibitor pocket (9HJ co-crystal)"),
    ("KAT6A",  "Q92794", "9DZN", [13.14, 11.03, 16.47],     "KAT6A MYST HAT bisubstrate pocket (CMC co-crystal)"),
    ("KAT5",   "Q92993", "2OU2", [27.46, 24.07, 10.28],     "KAT5/TIP60 MYST HAT acetyl-CoA pocket"),
    ("KMT5B",  "Q4FZB7", "3S8P", [5.20, 36.29, -5.36],      "KMT5B/SUV420H1 SET domain SAM cofactor site"),
    ("EHMT1",  "Q9H9B1", "3HNA", [14.96, 2.07, 14.52],      "EHMT1/GLP SET domain SAH cofactor site"),
]

out_dir = Path("/home/bryza/sma-research/qms/proteome_wide_2026/extended_tasks")
out_dir.mkdir(parents=True, exist_ok=True)

for gene, uniprot, pdb, center, rationale in TASKS:
    task = {
        "id": f"pocketxmol_{gene.lower()}_sma_atlas_ext",
        "type": "pocketxmol",
        "target": f"{gene}_SMA_ATLAS_EXT",
        "uniprot": uniprot,
        "pdb_id": pdb,
        "pocket_center": center,
        "pocket_radius": 10.0,
        "n_molecules": 600,
        "batch_size": 50,
        "project": "SMA",
        "priority": 2,
        "status": "queued",
        "_notes": f"{rationale}. TITLE-verified 2026-04-17 (see TITLE_AUDIT_extended.md). Atlas extended campaign ranks 6-25 Phase-3."
    }
    p = out_dir / f"task_{gene}.json"
    p.write_text(json.dumps(task, indent=2))
    print(f"Wrote {p}")

# Generate master runner script
runner = """#!/bin/bash
# Atlas Extended (ranks 6-25) PocketXMol Campaign Runner — 2026-04-17
# Runs 9 PocketXMol tasks sequentially on A100-SXM4-40GB (35124116)
# Expected: ~30 min per task (600 mols, batch 50) = ~4.5 h total wall-clock

set -u
cd /workspace
mkdir -p /workspace/atlas_extended_logs

TARGETS=(EP400 PEAK1 KAT7 RNF213 EHMT2 KAT6A KAT5 KMT5B EHMT1)
START_TIME=$(date +%s)
echo "=== Atlas Extended PocketXMol Campaign START $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" \\
    | tee /workspace/atlas_extended_logs/MASTER.log

for target in "${TARGETS[@]}"; do
    task_json="/workspace/extended_tasks/task_${target}.json"
    logfile="/workspace/atlas_extended_logs/${target}.log"
    echo "" | tee -a /workspace/atlas_extended_logs/MASTER.log
    echo ">>> [$(date -u +%H:%M:%S)] FIRING ${target} (task: ${task_json})" \\
        | tee -a /workspace/atlas_extended_logs/MASTER.log
    t0=$(date +%s)
    python3 /workspace/pocketxmol_deploy.py --task ${task_json} --skip-install --device cuda:0 \\
        2>&1 | tee ${logfile}
    rc=${PIPESTATUS[0]}
    t1=$(date +%s)
    dt=$((t1 - t0))
    echo "<<< [$(date -u +%H:%M:%S)] ${target} exit=${rc} elapsed=${dt}s" \\
        | tee -a /workspace/atlas_extended_logs/MASTER.log
    task_id=$(grep -oP '"id"\\s*:\\s*"\\K[^"]+' ${task_json})
    n_sdf=$(ls /results/pocketxmol/${task_id}/SDF/*.sdf 2>/dev/null | wc -l)
    echo "    produced ${n_sdf} SDFs under /results/pocketxmol/${task_id}/" \\
        | tee -a /workspace/atlas_extended_logs/MASTER.log
done

END_TIME=$(date +%s)
TOTAL=$((END_TIME - START_TIME))
echo "" | tee -a /workspace/atlas_extended_logs/MASTER.log
echo "=== Atlas Extended PocketXMol Campaign COMPLETE $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" \\
    | tee -a /workspace/atlas_extended_logs/MASTER.log
echo "Total wall time: ${TOTAL}s ($((TOTAL/60)) min)" \\
    | tee -a /workspace/atlas_extended_logs/MASTER.log
touch /workspace/atlas_extended_logs/CAMPAIGN_COMPLETE
"""

runner_path = out_dir / "run_atlas_extended.sh"
runner_path.write_text(runner)
runner_path.chmod(0o755)
print(f"\nWrote {runner_path}")

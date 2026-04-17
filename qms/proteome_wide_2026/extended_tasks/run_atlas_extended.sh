#!/bin/bash
# Atlas Extended (ranks 6-25) PocketXMol Campaign Runner — 2026-04-17
# Runs 9 PocketXMol tasks sequentially on A100-SXM4-40GB (35124116)
# Expected: ~30 min per task (600 mols, batch 50) = ~4.5 h total wall-clock

set -u
cd /workspace
mkdir -p /workspace/atlas_extended_logs

TARGETS=(EP400 PEAK1 KAT7 RNF213 EHMT2 KAT6A KAT5 KMT5B EHMT1)
START_TIME=$(date +%s)
echo "=== Atlas Extended PocketXMol Campaign START $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" \
    | tee /workspace/atlas_extended_logs/MASTER.log

for target in "${TARGETS[@]}"; do
    task_json="/workspace/extended_tasks/task_${target}.json"
    logfile="/workspace/atlas_extended_logs/${target}.log"
    echo "" | tee -a /workspace/atlas_extended_logs/MASTER.log
    echo ">>> [$(date -u +%H:%M:%S)] FIRING ${target} (task: ${task_json})" \
        | tee -a /workspace/atlas_extended_logs/MASTER.log
    t0=$(date +%s)
    python3 /workspace/pocketxmol_deploy.py --task ${task_json} --skip-install --device cuda:0 \
        2>&1 | tee ${logfile}
    rc=${PIPESTATUS[0]}
    t1=$(date +%s)
    dt=$((t1 - t0))
    echo "<<< [$(date -u +%H:%M:%S)] ${target} exit=${rc} elapsed=${dt}s" \
        | tee -a /workspace/atlas_extended_logs/MASTER.log
    task_id=$(grep -oP '"id"\s*:\s*"\K[^"]+' ${task_json})
    n_sdf=$(ls /results/pocketxmol/${task_id}/SDF/*.sdf 2>/dev/null | wc -l)
    echo "    produced ${n_sdf} SDFs under /results/pocketxmol/${task_id}/" \
        | tee -a /workspace/atlas_extended_logs/MASTER.log
done

END_TIME=$(date +%s)
TOTAL=$((END_TIME - START_TIME))
echo "" | tee -a /workspace/atlas_extended_logs/MASTER.log
echo "=== Atlas Extended PocketXMol Campaign COMPLETE $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" \
    | tee -a /workspace/atlas_extended_logs/MASTER.log
echo "Total wall time: ${TOTAL}s ($((TOTAL/60)) min)" \
    | tee -a /workspace/atlas_extended_logs/MASTER.log
touch /workspace/atlas_extended_logs/CAMPAIGN_COMPLETE

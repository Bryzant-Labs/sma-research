#!/usr/bin/env bash
# LIMK2 Arm 1 redesign — 3 PXM campaigns on asxm A100
set -euo pipefail

export PATH=/opt/miniconda3/envs/pxm_cu128/bin:$PATH
cd /root/PocketXMol

RESDIR=/root/results_limk2_arm1
LOG=$RESDIR/run.log
echo "=== LIMK2 Arm 1 redesign start $(date -u +%FT%TZ) ===" > "$LOG"
nvidia-smi -L >> "$LOG"
python --version >> "$LOG"

for SUB in A B C; do
    case $SUB in
        A) CFG=$RESDIR/configs/config_A_activator_dfg_oriented.yml; OUT=$RESDIR/generated_A ;;
        B) CFG=$RESDIR/configs/config_B_limki3_seeded.yml;          OUT=$RESDIR/generated_B ;;
        C) CFG=$RESDIR/configs/config_C_hbond_network.yml;          OUT=$RESDIR/generated_C ;;
    esac
    mkdir -p "$OUT"
    echo "=== Strategy $SUB start $(date -u +%FT%TZ) ===" >> "$LOG"
    python -m scripts.sample_use \
        --config_task "$CFG" \
        --config_model configs/sample/pxm.yml \
        --outdir "$OUT" \
        --device cuda:0 \
        >> "$LOG" 2>&1
    NSDF=$(ls "$OUT" 2>/dev/null | grep -c '\.sdf$' || echo 0)
    echo "=== Strategy $SUB DONE — $NSDF SDFs — $(date -u +%FT%TZ) ===" >> "$LOG"
done

echo "=== All 3 strategies complete $(date -u +%FT%TZ) ===" >> "$LOG"
echo "DONE" > $RESDIR/.complete

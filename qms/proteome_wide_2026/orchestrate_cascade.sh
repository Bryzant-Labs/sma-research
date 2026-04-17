#!/bin/bash
# Orchestrator: pull PXM results as they complete, run cascade filter,
# then fire Boltz-2 panel, then build final report.
#
# Run from local workstation. Polls GPU every ~2 min.

set -u
GPU_PORT=14116
GPU_HOST=ssh3.vast.ai
CAMPAIGN_DIR=/workspace/atlas_extended_logs
PXM_RESULTS_ROOT=/results/pocketxmol
LOCAL_CASCADE=/home/bryza/sma-research/qms/proteome_wide_2026/cascade_extended_output
QMS=/home/bryza/sma-research/qms
PROT_DIR=/home/bryza/sma-research/qms/proteome_wide_2026

mkdir -p "$LOCAL_CASCADE"
mkdir -p "$LOCAL_CASCADE/raw_pulls"

TARGETS=(EP400 PEAK1 KAT7 RNF213 EHMT2 KAT6A KAT5 KMT5B EHMT1)
DONE_MARKER="$LOCAL_CASCADE/.orchestrator_done"

log() {
    echo "[$(date -u +%H:%M:%S)] $*"
}

# --- Step A: poll until CAMPAIGN_COMPLETE ---
log "Waiting for extended PXM campaign to complete on GPU $GPU_PORT..."
while true; do
    if ssh -i ~/.ssh/id_ed25519_vastai -o StrictHostKeyChecking=no -p $GPU_PORT root@$GPU_HOST \
        "test -f $CAMPAIGN_DIR/CAMPAIGN_COMPLETE" 2>/dev/null; then
        log "Campaign complete."
        break
    fi
    # Print progress
    PROG=$(ssh -i ~/.ssh/id_ed25519_vastai -o StrictHostKeyChecking=no -p $GPU_PORT root@$GPU_HOST \
        "tail -3 $CAMPAIGN_DIR/MASTER.log 2>/dev/null | tr '\\n' ' '" 2>/dev/null)
    log "  progress: $PROG"
    sleep 120
done

# --- Step B: pull all target results ---
log "Pulling PXM results for all 9 targets..."
for tgt in "${TARGETS[@]}"; do
    lower=$(echo "$tgt" | tr '[:upper:]' '[:lower:]')
    task_id="pocketxmol_${lower}_sma_atlas_ext"
    local_out="$LOCAL_CASCADE/raw_pulls/$task_id"
    mkdir -p "$local_out"
    log "  pulling $tgt ($task_id)"
    # Top-level gen_info.csv (the deploy script symlinks/copies it there)
    scp -q -i ~/.ssh/id_ed25519_vastai -o StrictHostKeyChecking=no -P $GPU_PORT \
        root@$GPU_HOST:$PXM_RESULTS_ROOT/$task_id/gen_info.csv \
        "$local_out/gen_info.csv" 2>/dev/null && log "    got $tgt" || {
        # Fallback: find the subdir via remote shell
        REMOTE_CSV=$(ssh -i ~/.ssh/id_ed25519_vastai -o StrictHostKeyChecking=no -p $GPU_PORT root@$GPU_HOST \
            "find $PXM_RESULTS_ROOT/$task_id/raw_output -maxdepth 3 -name gen_info.csv 2>/dev/null | head -1")
        if [ -n "$REMOTE_CSV" ]; then
            scp -q -i ~/.ssh/id_ed25519_vastai -o StrictHostKeyChecking=no -P $GPU_PORT \
                root@$GPU_HOST:"$REMOTE_CSV" "$local_out/gen_info.csv" 2>/dev/null && log "    got $tgt (via find)"
        else
            log "    WARN: no gen_info.csv for $tgt"
        fi
    }
done

# --- Step C: run cascade filter ---
log "Running cascade filter (RDKit/Lipinski/QED/BBB)..."
python3 $PROT_DIR/cascade_filter_extended.py \
    "$LOCAL_CASCADE/raw_pulls" "$LOCAL_CASCADE" 2>&1 | tee "$LOCAL_CASCADE/cascade_filter.log"

# --- Step D: run Boltz-2 panel ---
# Check server first
if curl -s -m 5 http://localhost:8003/health | grep -q ready; then
    log "Boltz-2 server ready; firing panel..."
    python3 $PROT_DIR/boltz2_panel_extended.py "$LOCAL_CASCADE" \
        --top-n 10 --max-workers 6 2>&1 | tee "$LOCAL_CASCADE/boltz2_panel.log"
else
    log "Boltz-2 server NOT healthy; skipping panel (run manually later)."
fi

# --- Step E: build report ---
log "Building final report..."
python3 $PROT_DIR/build_final_report.py 2>&1 | tee "$LOCAL_CASCADE/report_build.log"

log "All done. See $QMS/ATLAS_TOP25_CASCADE_RESULTS.md"
touch "$DONE_MARKER"

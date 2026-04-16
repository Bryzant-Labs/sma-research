#!/usr/bin/env bash
# ColabFold with CORTEX-extracted residue-pair constraints.
# Called on the TPU VM; reads FASTA + constraint CSV, runs colabfold_batch
# with --constraint-path. CORTEX priors bias folding toward SMA-relevant conformation.
set -u
TID="${1:?usage: $0 <task_id> <fasta> <constraint_csv> <out_dir>}"
FASTA="${2}"
CONSTRAINTS="${3}"
OUT="${4}"
mkdir -p "$OUT"
touch "/tmp/fleet_start_${TID}"
echo "[cortex_cf] start $(date -u +%FT%TZ)" > "$OUT/fleet.log"

# ColabFold batch with constraint path. For chains that don't have constraints,
# --constraint-path is ignored gracefully.
~/.local/bin/colabfold_batch "$FASTA" "$OUT" \
    --msa-mode mmseqs2_uniref_env \
    --num-recycle 3 \
    --num-models 3 \
    --num-seeds 10 \
    --constraint-path "$CONSTRAINTS" \
    >> "$OUT/fleet.log" 2>&1

RC=$?
if [ $RC -eq 0 ]; then
    touch "/tmp/COMPLETE_${TID}"
    echo "[cortex_cf] complete $(date -u +%FT%TZ)" >> "$OUT/fleet.log"
else
    echo "FAIL rc=$RC" > "/tmp/FAILED_${TID}"
    echo "[cortex_cf] failed rc=$RC $(date -u +%FT%TZ)" >> "$OUT/fleet.log"
fi

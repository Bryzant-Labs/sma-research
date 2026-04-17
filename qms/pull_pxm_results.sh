#!/bin/bash
# Pull PocketXMol campaign results from Vast.ai GPU instance to fleet-results/
# Usage: ./pull_pxm_results.sh <ssh_port> <remote_outdir> <local_results_dir> <campaign_id>

set -e
PORT=$1
REMOTE_OUTDIR=$2
LOCAL_DIR=$3
CAMPAIGN=$4

if [ -z "$CAMPAIGN" ]; then
    echo "Usage: $0 <ssh_port> <remote_outdir> <local_results_dir> <campaign_id>"
    exit 1
fi

mkdir -p "$LOCAL_DIR"
mkdir -p "$LOCAL_DIR/SDF"

SSH_HOST_BY_PORT() {
    # Map port -> ssh host (from vast.ai)
    case $1 in
        14116) echo ssh3.vast.ai ;;
        10540) echo ssh4.vast.ai ;;
        *) echo "unknown port $1" >&2; exit 1 ;;
    esac
}

HOST=$(SSH_HOST_BY_PORT $PORT)

echo "[PULL] $CAMPAIGN from root@$HOST:$PORT -> $LOCAL_DIR"

# Find latest experiment subdir on remote
EXP=$(ssh -i ~/.ssh/id_ed25519_vastai -o StrictHostKeyChecking=no -p $PORT root@$HOST \
    "ls -td $REMOTE_OUTDIR/*/ 2>/dev/null | head -1")

if [ -z "$EXP" ]; then
    echo "[PULL] ERROR: no experiment subdir found in $REMOTE_OUTDIR"
    exit 1
fi

echo "[PULL] Remote experiment dir: $EXP"

# Copy gen_info.csv
scp -i ~/.ssh/id_ed25519_vastai -o StrictHostKeyChecking=no -P $PORT \
    root@$HOST:${EXP}gen_info.csv "$LOCAL_DIR/gen_info.csv"

# Copy all final SDF files (not the 0_inputs one)
SDF_DIR=$(ssh -i ~/.ssh/id_ed25519_vastai -o StrictHostKeyChecking=no -p $PORT root@$HOST \
    "ls -d ${EXP}*_SDF 2>/dev/null | head -1")
echo "[PULL] Remote SDF dir: $SDF_DIR"

rsync -az --include='*.sdf' --exclude='0_inputs/***' \
    -e "ssh -i ~/.ssh/id_ed25519_vastai -o StrictHostKeyChecking=no -p $PORT" \
    "root@$HOST:${SDF_DIR}/" "$LOCAL_DIR/SDF/"

# Copy task JSON + plan
ssh -i ~/.ssh/id_ed25519_vastai -o StrictHostKeyChecking=no -p $PORT root@$HOST \
    "ls -la ${REMOTE_OUTDIR%/*}/" || true

N_SDF=$(ls "$LOCAL_DIR/SDF/" 2>/dev/null | grep -c "\.sdf" || echo 0)
N_ROWS=$(($(wc -l < "$LOCAL_DIR/gen_info.csv") - 1))
echo "[PULL] DONE: $N_SDF SDF files, $N_ROWS rows in gen_info.csv"

#!/usr/bin/env bash
# Remote run script — executes on sma-h100-two inside tmux
set -euo pipefail

cd /home/shadeform/limk2_affinity_rerun
LOG=/home/shadeform/limk2_affinity_rerun/run.log
echo "=== LIMK2 affinity rerun start $(date -u +%FT%TZ) ===" > "$LOG"
echo "GPU:" >> "$LOG"
nvidia-smi -L >> "$LOG"

/home/shadeform/miniconda3/envs/pxm_cu128/bin/boltz predict \
  /home/shadeform/limk2_affinity_rerun/in \
  --out_dir /home/shadeform/limk2_affinity_rerun/out \
  --cache /home/shadeform/.boltz_cache \
  --model boltz2 \
  --recycling_steps 1 --sampling_steps 25 \
  --sampling_steps_affinity 100 --diffusion_samples_affinity 3 \
  --accelerator gpu --devices 1 --diffusion_samples 1 \
  --output_format pdb --num_workers 0 --override \
  >> "$LOG" 2>&1

echo "=== DONE $(date -u +%FT%TZ) ===" >> "$LOG"

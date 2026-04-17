#!/bin/bash
# PERP Round 2 disulfide-preserved rerun — for future GPU fire (dispatch when h100-work available)
# Seeds: top 3 ECL1 on-ECL binders OR all top 5 ECL1 (if pipeline diagnosis per
#        PERP_binder_interface_analysis.md invalidates off-ECL H2* binders)
#
# RFdiffusion native disulfide preservation:
#   - PDB includes SSBOND record (line added at top of PERP_ECL1core_ssbond.pdb).
#   - contigmap.contigs `[A30-80/0 N-N]` keeps ECL1 scaffold rigid (diffusion only on binder chain).
#   - The fixed ECL1 scaffold retains C51-C65 geometry (empirically verified intact in Round 1
#     outputs; this rerun re-confirms with explicit SSBOND and partial_T=15 for fine-grained
#     disulfide-fidelity test).
#
# Usage: ssh h100-work "bash /workspace/run_rfdiff_disulfide_rerun.sh" (after rsync of inputs/)

set -uo pipefail

cd /workspace/RFdiffusion || { echo "RFdiffusion install missing"; exit 1; }

SEED_DIR=/workspace/perp_round2_ssbond/inputs
OUT=/workspace/perp_round2_ssbond/outputs
LOG=$OUT/logs
mkdir -p "$OUT" "$LOG"

export HYDRA_FULL_ERROR=1

# ECL1 top-3 (partial diffusion from Round 1 winners with SSBOND-annotated ECL1 core)
# T=15 of 50 — local perturbation, ECL1 scaffold + disulfide kept rigid
run_rfdiff_ssbond() {
  local name="$1"     # H1a_38, H1c_25, H1b_10
  local contigs="$2"  # e.g. [A30-80/0 85-85]
  local hotspots="$3" # e.g. ["A40","A52","A62"]
  local T="$4"
  local N="$5"
  local sub="$6"

  local outprefix="$OUT/$sub/${name}"
  mkdir -p "$OUT/$sub"

  echo "[$(date -u +%H:%M:%S)] rfdiff+SSBOND: $name contigs=$contigs hotspots=$hotspots T=$T N=$N"

  python scripts/run_inference.py \
    inference.input_pdb="$SEED_DIR/${name}_ssbond.pdb" \
    inference.output_prefix="$outprefix" \
    inference.num_designs=$N \
    inference.ckpt_override_path=models/Complex_base_ckpt.pt \
    "contigmap.contigs=$contigs" \
    "ppi.hotspot_res=$hotspots" \
    diffuser.partial_T=$T \
    inference.write_trajectory=False \
    > "$LOG/${sub}_${name}.log" 2>&1
  echo "[$(date -u +%H:%M:%S)] rfdiff+SSBOND: $name rc=$?"
}

# Run top 3 on-ECL candidates + 1 control that was off-ECL in Round 1
# Top on-ECL: H1c_25, H1b_10
# Top iptm: H1a_38 (even though Round 1 was off-ECL - can it re-bind ECL with SSBOND?)
run_rfdiff_ssbond H1a_38  "[\"A30-80/0 85-85\"]" "[\"A40\",\"A52\",\"A62\"]" 15 20 rerun_ssbond
run_rfdiff_ssbond H1c_25  "[\"A30-80/0 84-84\"]" "[\"A69\",\"A71\",\"A73\"]" 15 20 rerun_ssbond
run_rfdiff_ssbond H1b_10  "[\"A30-80/0 85-85\"]" "[\"A60\",\"A62\",\"A70\"]" 15 20 rerun_ssbond

# From scratch (not partial): de novo generation against SSBOND-annotated ECL1
python scripts/run_inference.py \
  inference.input_pdb="$SEED_DIR/PERP_ECL1core_ssbond.pdb" \
  inference.output_prefix="$OUT/denovo_ssbond/denovo" \
  inference.num_designs=20 \
  inference.ckpt_override_path=models/Complex_base_ckpt.pt \
  "contigmap.contigs=[\"A30-80/0 70-100\"]" \
  "ppi.hotspot_res=[\"A69\",\"A71\",\"A73\"]" \
  > "$LOG/denovo_ssbond.log" 2>&1

echo "[done] Disulfide rerun complete. Outputs in $OUT"
ls -la "$OUT"/rerun_ssbond/ "$OUT"/denovo_ssbond/ 2>&1 | tail -20

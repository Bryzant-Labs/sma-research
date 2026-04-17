"""Rescore prior LIMK2 and ROCK2 leads via Boltz-2 affinity head.

Reads /home/bryza/sma-research/qms/chembl_ki_calibration/rescored_leads.json,
builds affinity-YAML for each (target, smiles) pair, runs boltz-2, then applies
the per-kinase calibration to emit predicted log10(Ki_nM) + 95 % PI.

Writes: rescored_leads_affinity.json (same folder).
"""
import json
import math
import subprocess
import time
from pathlib import Path

ROOT = Path("/home/bryza/sma-research/qms/chembl_ki_affinity_head")
LEADS_SRC = Path("/home/bryza/sma-research/qms/chembl_ki_calibration/rescored_leads.json")
KINASE_SEQS = json.loads(Path("/home/bryza/sma-research/qms/chembl_ki_calibration/kinase_sequences.json").read_text())
FITS = json.loads((ROOT / "fits.json").read_text())
YAML_DIR = ROOT / "leads_yaml_in"
YAML_DIR.mkdir(exist_ok=True)
REMOTE_IN = "/home/shadeform/affinity_calib/leads_in"
REMOTE_OUT = "/home/shadeform/affinity_calib/leads_out"

leads = json.loads(LEADS_SRC.read_text())

# Build YAMLs
for i, L in enumerate(leads):
    target = L["target"]
    seq = KINASE_SEQS[target]["seq"]
    smi = L["smiles"].replace("\\", "\\\\").replace('"', '\\"')
    jid = f"LEAD_{target}_{L['rank']:02d}"
    L["job_id"] = jid
    yaml_text = (
        "version: 1\n"
        "sequences:\n"
        "  - protein:\n"
        "      id: A\n"
        f"      sequence: {seq}\n"
        "      msa: empty\n"
        "  - ligand:\n"
        "      id: L1\n"
        f'      smiles: "{smi}"\n'
        "properties:\n"
        "  - affinity:\n"
        "      binder: L1\n"
    )
    (YAML_DIR / f"{jid}.yaml").write_text(yaml_text)

print(f"Built {len(leads)} lead YAMLs → {YAML_DIR}")

# Sync to remote
subprocess.run(["ssh", "sma-h100-two", f"mkdir -p {REMOTE_IN} {REMOTE_OUT}"], check=True)
# Clean outputs
subprocess.run([
    "ssh", "sma-h100-two",
    f"find {REMOTE_OUT} -mindepth 1 -delete 2>/dev/null; find {REMOTE_IN} -mindepth 1 -delete 2>/dev/null; true"
])
r = subprocess.run(["rsync", "-az", str(YAML_DIR) + "/", f"sma-h100-two:{REMOTE_IN}/"])
assert r.returncode == 0, "rsync failed"
print("synced to remote")

# Run boltz
run_cmd = (
    f"/home/shadeform/miniconda3/envs/pxm_cu128/bin/boltz predict {REMOTE_IN} "
    f"--out_dir {REMOTE_OUT} --cache /home/shadeform/.boltz_cache --model boltz2 "
    "--recycling_steps 1 --sampling_steps 25 "
    "--sampling_steps_affinity 100 --diffusion_samples_affinity 3 "
    "--accelerator gpu --devices 1 --diffusion_samples 1 "
    "--output_format pdb --num_workers 0 --override"
)
t0 = time.time()
print(f"running: {run_cmd[:200]}...")
r = subprocess.run(
    ["ssh", "sma-h100-two", run_cmd],
    capture_output=True, text=True, timeout=1800,
)
print(f"elapsed={time.time()-t0:.1f}s rc={r.returncode}")
if r.returncode != 0:
    print("STDERR:", r.stderr[-1500:])
    raise SystemExit(1)

# Sync back
r = subprocess.run([
    "rsync", "-az",
    "--include", "*/",
    "--include", "affinity_*.json",
    "--include", "confidence_*.json",
    "--exclude", "*",
    f"sma-h100-two:{REMOTE_OUT}/",
    str(ROOT / "leads_boltz_out") + "/",
])
assert r.returncode == 0

# Parse results
leads_out_dir = ROOT / "leads_boltz_out"

results = []
for L in leads:
    jid = L["job_id"]
    aff_files = list(leads_out_dir.rglob(f"affinity_{jid}.json"))
    conf_files = list(leads_out_dir.rglob(f"confidence_{jid}_*.json"))
    rec = dict(L)
    if aff_files:
        aj = json.loads(aff_files[0].read_text())
        rec["affinity_pred_value"] = aj.get("affinity_pred_value")
        rec["affinity_probability_binary"] = aj.get("affinity_probability_binary")
    else:
        rec["affinity_pred_value"] = None
    if conf_files:
        cj = json.loads(conf_files[0].read_text())
        rec["iptm_new"] = cj.get("iptm", cj.get("complex_iptm"))
    else:
        rec["iptm_new"] = None

    # Apply per-kinase fit
    target = L["target"]
    fit = FITS.get(target)
    if fit and rec["affinity_pred_value"] is not None:
        pred_log10_ki = fit["slope"] * rec["affinity_pred_value"] + fit["intercept"]
        rec["pred_log10_ki_nM"] = float(pred_log10_ki)
        rec["pred_ki_nM"] = float(10 ** pred_log10_ki)
        # 95% PI = 1.96 * rmse on log-Ki scale
        rmse = fit["rmse_log10_ki"]
        rec["ki_95pi_nM"] = [
            float(10 ** (pred_log10_ki - 1.96 * rmse)),
            float(10 ** (pred_log10_ki + 1.96 * rmse)),
        ]
        rec["calib_r2"] = fit["r2"]
    else:
        rec["pred_log10_ki_nM"] = None
        rec["pred_ki_nM"] = None
        rec["ki_95pi_nM"] = None
    results.append(rec)

(ROOT / "rescored_leads_affinity.json").write_text(json.dumps(results, indent=2))

print("\n=== RESCORED LEADS (affinity-head) ===")
print(f"{'target':<6} {'rank':>3} {'affinity':>9} {'prob_bin':>9} {'Ki_est':>11} {'95% PI (nM)':>28}")
for r in results:
    if r["pred_ki_nM"] is not None:
        ki = r["pred_ki_nM"]
        lo, hi = r["ki_95pi_nM"]
        ki_s = f"{ki:.1f} nM" if ki < 1e4 else f"{ki:.2e} nM"
        pi_s = f"{lo:.2g} – {hi:.2g}"
        aff = r.get("affinity_pred_value")
        pb = r.get("affinity_probability_binary")
        print(f"{r['target']:<6} {r['rank']:>3} {aff:>9.3f} {pb:>9.3f} {ki_s:>11}  {pi_s:>28}")
    else:
        print(f"{r['target']:<6} {r['rank']:>3}  NO AFFINITY OUTPUT")

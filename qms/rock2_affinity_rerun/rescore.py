"""Rescore the ROCK2-alphaC library via Boltz-2 affinity head output.

Reads:
  - /home/bryza/sma-research/qms/rock2_affinity_rerun/boltz_out/ (synced from remote)
  - manifest.json (241 compounds)
  - /home/bryza/sma-research/qms/chembl_ki_affinity_head/fits.json (ROCK2 fit)
  - /home/bryza/fleet-results/rock2_activator_alphaC/top10_selectivity.tsv (prior z-score panel, 3 rows)
  - /home/bryza/fleet-results/rock2_activator_alphaC/boltz2_rescore_ranked.tsv (prior iptm rescore)

Output:
  - top_hits_affinity_v2.tsv (ranked by calibrated Ki, gate prob_binary > 0.3)
  - full_affinity_ranked_v2.tsv (all 241, sorted by log10 Ki)
  - rescored_full.json (every compound's affinity + Ki + prior metrics)
"""
import csv
import json
from pathlib import Path

ROOT = Path("/home/bryza/sma-research/qms/rock2_affinity_rerun")
BOLTZ_OUT = ROOT / "boltz_out"
MANIFEST = json.loads((ROOT / "manifest.json").read_text())
FITS = json.loads(Path("/home/bryza/sma-research/qms/chembl_ki_affinity_head/fits.json").read_text())
ROCK2_FIT = FITS["ROCK2"]  # slope=0.880, intercept=2.960, rmse=0.693
print(f"ROCK2 fit: slope={ROCK2_FIT['slope']:.3f} intercept={ROCK2_FIT['intercept']:.3f} "
      f"R2={ROCK2_FIT['r2']:.3f} rmse={ROCK2_FIT['rmse_log10_ki']:.3f}")

def _tf(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


# Load prior z-score panel (top10_selectivity.tsv has top 3 rows with z_ROCK2/selectivity_z)
PRIOR_Z = Path("/home/bryza/fleet-results/rock2_activator_alphaC/top10_selectivity.tsv")
prior_panel = {}
if PRIOR_Z.exists():
    with PRIOR_Z.open() as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            smi = row.get("smiles")
            if not smi:
                continue
            prior_panel[smi] = {
                "prior_iptm_ROCK2": _tf(row.get("iptm_ROCK2")),
                "prior_iptm_LIMK2": _tf(row.get("iptm_LIMK2")) if "iptm_LIMK2" in row else None,
                "prior_z_ROCK2": _tf(row.get("z_ROCK2")),
                "prior_sel_z": _tf(row.get("selectivity_z")),
                "prior_row_mu_iptm": _tf(row.get("row_mu_iptm")),
                "prior_row_sigma_iptm": _tf(row.get("row_sigma_iptm")),
                "prior_n_kinases_in_panel": int(row["n_kinases_in_panel"]) if row.get("n_kinases_in_panel") else None,
            }
print(f"Prior z-score panel: {len(prior_panel)} compounds")

# Load prior iptm rescore (boltz2_rescore_ranked.tsv has 23 rows iptm/ptm/plddt)
PRIOR_IPTM = Path("/home/bryza/fleet-results/rock2_activator_alphaC/boltz2_rescore_ranked.tsv")
prior_iptm = {}
if PRIOR_IPTM.exists():
    with PRIOR_IPTM.open() as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            smi = row.get("smiles")
            if not smi:
                continue
            prior_iptm[smi] = {
                "prior_iptm": _tf(row.get("iptm")),
                "prior_ptm": _tf(row.get("ptm")),
                "prior_plddt": _tf(row.get("plddt")),
            }
print(f"Prior iptm rescore: {len(prior_iptm)} compounds")

# Parse Boltz-2 affinity outputs
results = []
missing = 0
for comp in MANIFEST["compounds"]:
    jid = f"ROCK2_{comp['id']}"
    aff_files = list(BOLTZ_OUT.rglob(f"affinity_{jid}.json"))
    conf_files = list(BOLTZ_OUT.rglob(f"confidence_{jid}_*.json"))

    rec = {
        "compound_id": comp["id"],
        "filename": comp["filename"],
        "smiles": comp["smiles"],
        "qed": comp.get("qed"),
        "mw": comp.get("mw"),
        "logp": comp.get("logp"),
        "tpsa": comp.get("tpsa"),
        "hbd": comp.get("hbd"),
        "bbb_heuristic": comp.get("bbb_heuristic"),
        "ro5_pass": comp.get("ro5_pass"),
    }

    if aff_files:
        aj = json.loads(aff_files[0].read_text())
        rec["affinity_pred_value"] = aj.get("affinity_pred_value")
        rec["affinity_probability_binary"] = aj.get("affinity_probability_binary")
    else:
        rec["affinity_pred_value"] = None
        rec["affinity_probability_binary"] = None
        missing += 1

    if conf_files:
        cj = json.loads(conf_files[0].read_text())
        rec["iptm_new"] = cj.get("iptm", cj.get("complex_iptm"))
        rec["ptm_new"] = cj.get("ptm")
        rec["plddt_new"] = cj.get("plddt", cj.get("complex_plddt"))
    else:
        rec["iptm_new"] = None
        rec["ptm_new"] = None
        rec["plddt_new"] = None

    # Apply ROCK2 calibration fit
    if rec["affinity_pred_value"] is not None:
        slope, intercept = ROCK2_FIT["slope"], ROCK2_FIT["intercept"]
        rmse = ROCK2_FIT["rmse_log10_ki"]
        log_ki = slope * rec["affinity_pred_value"] + intercept
        rec["log10_Ki_nM"] = log_ki
        rec["Ki_nM"] = 10 ** log_ki
        rec["Ki_95PI_nM_lo"] = 10 ** (log_ki - 1.96 * rmse)
        rec["Ki_95PI_nM_hi"] = 10 ** (log_ki + 1.96 * rmse)
    else:
        rec["log10_Ki_nM"] = None
        rec["Ki_nM"] = None
        rec["Ki_95PI_nM_lo"] = None
        rec["Ki_95PI_nM_hi"] = None

    # Merge prior data
    rec.update(prior_panel.get(comp["smiles"], {}))
    rec.update(prior_iptm.get(comp["smiles"], {}))

    results.append(rec)

print(f"Parsed {len(results)} compounds; missing_affinity={missing}")

# Save full JSON
(ROOT / "rescored_full.json").write_text(json.dumps(results, indent=2, default=str))

# Apply binary-binder gate
GATE_PROB = 0.3
survivors = [r for r in results
             if r["affinity_probability_binary"] is not None
             and r["affinity_probability_binary"] > GATE_PROB]
print(f"\n=== Compounds with affinity_probability_binary > {GATE_PROB}: {len(survivors)} of {len(results)} ===")

# Z-score compatibility
z_OK = [r for r in survivors
        if r.get("prior_z_ROCK2") is not None and r["prior_z_ROCK2"] > 0
        and r.get("prior_sel_z") is not None and r["prior_sel_z"] > 0]
print(f"Of survivors, also passing z_ROCK2>0 AND sel_z>0: {len(z_OK)}")
print(f"  (Note: only {len(prior_panel)} compounds have prior panel data; others have None)")

# Rank by calibrated Ki
survivors_ranked = sorted(survivors, key=lambda r: r["log10_Ki_nM"])

OUT_DIR = Path("/home/bryza/fleet-results/rock2_activator_alphaC")
OUT_TSV = OUT_DIR / "top_hits_affinity_v2.tsv"
fields = [
    "rank", "smiles", "filename",
    "Ki_nM", "Ki_95PI_nM_lo", "Ki_95PI_nM_hi",
    "affinity_pred_value", "affinity_probability_binary",
    "iptm_new", "prior_iptm", "prior_iptm_ROCK2",
    "prior_z_ROCK2", "prior_sel_z",
    "qed", "mw", "logp", "tpsa", "hbd", "bbb_heuristic",
]


def _fmt(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, float):
        return f"{v:.3g}"
    return str(v)


with OUT_TSV.open("w") as f:
    f.write("\t".join(fields) + "\n")
    if not survivors_ranked:
        f.write("# NO COMPOUND PASSED affinity_probability_binary > 0.3 GATE\n")
    else:
        for i, r in enumerate(survivors_ranked, start=1):
            row = [str(i)] + [_fmt(r.get(k)) for k in fields[1:]]
            f.write("\t".join(row) + "\n")
print(f"Wrote -> {OUT_TSV}")

# Full ranked audit table
FULL_TSV = OUT_DIR / "full_affinity_ranked_v2.tsv"
full_ranked = sorted(
    [r for r in results if r["log10_Ki_nM"] is not None],
    key=lambda r: r["log10_Ki_nM"],
)
with FULL_TSV.open("w") as f:
    f.write("\t".join(fields) + "\tgate_binary\tgate_z\n")
    for i, r in enumerate(full_ranked, start=1):
        row = [str(i)] + [_fmt(r.get(k)) for k in fields[1:]]
        gate_b = "PASS" if r.get("affinity_probability_binary") and r["affinity_probability_binary"] > GATE_PROB else "fail"
        z_pass = (r.get("prior_z_ROCK2") or -99) > 0 and (r.get("prior_sel_z") or -99) > 0
        gate_z = "PASS" if z_pass else "fail"
        f.write("\t".join(row) + f"\t{gate_b}\t{gate_z}\n")
print(f"Wrote -> {FULL_TSV}")

# Console summary
print("\n=== BINARY-BINDER GATE SURVIVORS (top 20 by Ki) ===")
if not survivors_ranked:
    print("NONE.")
else:
    print(f"{'rank':>4} {'Ki_nM':>12} {'prob_bind':>10} {'aff_pred':>9} {'z_ROCK2':>8} {'sel_z':>8}  SMILES")
    for i, r in enumerate(survivors_ranked[:20], start=1):
        ki = r["Ki_nM"]
        ki_s = f"{ki:.1f} nM" if ki < 1e4 else f"{ki:.2e} nM"
        zr = r.get("prior_z_ROCK2"); zs = r.get("prior_sel_z")
        zr_s = f"{zr:+.2f}" if zr is not None else "   --   "
        zs_s = f"{zs:+.2f}" if zs is not None else "   --   "
        print(f"{i:>4} {ki_s:>12} {r['affinity_probability_binary']:>10.3f} "
              f"{r['affinity_pred_value']:>9.3f} {zr_s:>8} {zs_s:>8}  {r['smiles'][:48]}")

print("\n=== PRIOR PANEL TOP-3 (from top10_selectivity.tsv) RESCORED ===")
prior_top3_smiles = list(prior_panel.keys())
prior_rescored = [r for r in results if r["smiles"] in prior_top3_smiles]
for r in prior_rescored:
    ki_s = (f"{r['Ki_nM']:.1f} nM" if r['Ki_nM'] and r['Ki_nM'] < 1e4
            else f"{r['Ki_nM']:.2e} nM" if r['Ki_nM'] else "N/A")
    pb = r.get('affinity_probability_binary')
    pb_s = f"{pb:.3f}" if pb is not None else "N/A"
    gate_b = "PASS" if pb and pb > 0.3 else "FAIL"
    print(f"  {r['smiles'][:60]:60} -> Ki {ki_s:>12}, prob_bind {pb_s} [{gate_b}]")

# Summary stats
n_total = len(results)
n_valid = len([r for r in results if r["affinity_pred_value"] is not None])
n_pass = len(survivors_ranked)
summary = {
    "n_compounds": n_total,
    "n_with_affinity": n_valid,
    "n_pass_binary_gate": n_pass,
    "n_pass_z_score_gate": len(z_OK),
    "pct_pass_binary": round(100 * n_pass / max(1, n_valid), 2),
    "best_Ki_nM": survivors_ranked[0]["Ki_nM"] if survivors_ranked else None,
    "best_smiles": survivors_ranked[0]["smiles"] if survivors_ranked else None,
    "rock2_fit_r2": ROCK2_FIT["r2"],
    "rock2_fit_rmse_log10_ki": ROCK2_FIT["rmse_log10_ki"],
    "gate_prob_threshold": GATE_PROB,
}
(ROOT / "summary.json").write_text(json.dumps(summary, indent=2))
print(f"\n=== SUMMARY ===\n{json.dumps(summary, indent=2)}")

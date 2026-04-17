"""Rescore the LIMK2 library via Boltz-2 affinity head output.

Reads:
  - /home/bryza/sma-research/qms/limk2_affinity_rerun/boltz_out/ (synced from remote)
  - manifest.json
  - /home/bryza/sma-research/qms/chembl_ki_affinity_head/fits.json (LIMK2 fit)
  - /home/bryza/fleet-results/limk2_activator_alphaC/top_hits.tsv (prior z-score panel)
  - /home/bryza/fleet-results/limk2_activator_alphaC/bbb_filtered.csv (ADMET props)

Output:
  - top_hits_affinity_v2.tsv (ranked by calibrated Ki, affinity_prob_binary > 0.3 gate)
  - rescored_full.json (every compound's aff + Ki + z-score)
  - summary.md (top 10 table)
"""
import csv
import json
import math
from pathlib import Path

ROOT = Path("/home/bryza/sma-research/qms/limk2_affinity_rerun")
BOLTZ_OUT = ROOT / "boltz_out"
MANIFEST = json.loads((ROOT / "manifest.json").read_text())
FITS = json.loads(Path("/home/bryza/sma-research/qms/chembl_ki_affinity_head/fits.json").read_text())
LIMK2_FIT = FITS["LIMK2"]  # slope=1.249, intercept=3.549, rmse=0.378

# Load prior panel z-scores (by canonical SMILES)
TOP_HITS_PRIOR = Path("/home/bryza/fleet-results/limk2_activator_alphaC/top_hits.tsv")
prior_panel = {}
with TOP_HITS_PRIOR.open() as f:
    r = csv.DictReader(f, delimiter="\t")
    for row in r:
        smi = row["smiles"]
        prior_panel[smi] = {
            "prior_iptm_LIMK2": float(row["iptm_LIMK2"]) if row.get("iptm_LIMK2") else None,
            "prior_z_LIMK2": float(row["z_LIMK2"]) if row.get("z_LIMK2") else None,
            "prior_sel_z": float(row["selectivity_z"]) if row.get("selectivity_z") else None,
            "prior_C_rel": float(row["C_rel"]) if row.get("C_rel") else None,
        }

# Load ADMET props from bbb_filtered (has MW/TPSA/logP/HBD)
BBB_CSV = Path("/home/bryza/fleet-results/limk2_activator_alphaC/bbb_filtered.csv")
gen_info = {}
with BBB_CSV.open() as f:
    r = csv.DictReader(f)
    for row in r:
        key = row["canonical_smiles"]
        gen_info[key] = {
            "MW": float(row["MW"]) if row.get("MW") else None,
            "TPSA": float(row["TPSA"]) if row.get("TPSA") else None,
            "logP": float(row["logP"]) if row.get("logP") else None,
            "HBD": int(row["HBD"]) if row.get("HBD") else None,
        }

# Load DiffDock C_rel from diffdock_results (to retain the prior DD signal)
DD_CSV = Path("/home/bryza/fleet-results/limk2_activator_alphaC/diffdock_results.csv")
dd = {}
with DD_CSV.open() as f:
    r = csv.DictReader(f)
    for row in r:
        try:
            dd[row["canonical_smiles"]] = {
                "dd_conf": float(row["best_confidence"]),
                "C_rel": float(row["C_rel"]),
            }
        except (ValueError, KeyError):
            pass

# Parse Boltz-2 affinity outputs
results = []
missing = 0
for comp in MANIFEST["compounds"]:
    jid = f"LIMK2_{comp['id']}"
    aff_files = list(BOLTZ_OUT.rglob(f"affinity_{jid}.json"))
    conf_files = list(BOLTZ_OUT.rglob(f"confidence_{jid}_*.json"))

    rec = {
        "compound_id": comp["id"],
        "filename": comp["filename"],
        "smiles": comp["smiles"],
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
    else:
        rec["iptm_new"] = None

    # Apply LIMK2 calibration fit
    if rec["affinity_pred_value"] is not None:
        slope, intercept = LIMK2_FIT["slope"], LIMK2_FIT["intercept"]
        rmse = LIMK2_FIT["rmse_log10_ki"]
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

    # Merge prior panel + ADMET
    rec.update(prior_panel.get(comp["smiles"], {}))
    rec.update(gen_info.get(comp["smiles"], {}))
    rec.update(dd.get(comp["smiles"], {}))

    results.append(rec)

print(f"Parsed {len(results)} compounds; missing_affinity={missing}")

# Save full table
(ROOT / "rescored_full.json").write_text(json.dumps(results, indent=2))

# Apply the binary-binder gate (primary selection gate per task)
GATE_PROB = 0.3
survivors = [r for r in results
             if r["affinity_probability_binary"] is not None
             and r["affinity_probability_binary"] > GATE_PROB]
print(f"Compounds with affinity_probability_binary > {GATE_PROB}: {len(survivors)}")

# Also check z-score compatibility for survivors
z_OK = [r for r in survivors
        if r.get("prior_z_LIMK2") is not None and r["prior_z_LIMK2"] > 0
        and r.get("prior_sel_z") is not None and r["prior_sel_z"] > 0]
print(f"Of survivors, also passing z_LIMK2>0 AND sel_z>0: {len(z_OK)}")

# Rank survivors by calibrated Ki (ascending = tightest)
survivors_ranked = sorted(survivors, key=lambda r: r["log10_Ki_nM"])

# Write top hits TSV — use all survivors (nM-ordered)
OUT_DIR = Path("/home/bryza/fleet-results/limk2_activator_alphaC")
OUT_TSV = OUT_DIR / "top_hits_affinity_v2.tsv"
fields = [
    "rank", "smiles", "filename",
    "Ki_nM", "Ki_95PI_nM_lo", "Ki_95PI_nM_hi",
    "affinity_pred_value", "affinity_probability_binary",
    "iptm_new", "prior_iptm_LIMK2", "prior_z_LIMK2", "prior_sel_z", "prior_C_rel",
    "MW", "TPSA", "logP", "HBD",
]

with OUT_TSV.open("w") as f:
    f.write("\t".join(fields) + "\n")
    if not survivors_ranked:
        f.write("# NO COMPOUND PASSED affinity_probability_binary > 0.3 GATE\n")
    else:
        for i, r in enumerate(survivors_ranked, start=1):
            row = [str(i)] + [
                f"{r.get(k):.3g}" if isinstance(r.get(k), float) else
                (str(r.get(k)) if r.get(k) is not None else "")
                for k in fields[1:]
            ]
            f.write("\t".join(row) + "\n")

print(f"Wrote → {OUT_TSV}")

# Also write full ranked table (all compounds sorted by log10_Ki) for audit
FULL_TSV = OUT_DIR / "full_affinity_ranked_v2.tsv"
full_ranked = sorted(
    [r for r in results if r["log10_Ki_nM"] is not None],
    key=lambda r: r["log10_Ki_nM"],
)
with FULL_TSV.open("w") as f:
    f.write("\t".join(fields) + "\tgate_binary\tgate_z\n")
    for i, r in enumerate(full_ranked, start=1):
        row = [str(i)] + [
            f"{r.get(k):.3g}" if isinstance(r.get(k), float) else
            (str(r.get(k)) if r.get(k) is not None else "")
            for k in fields[1:]
        ]
        gate_binary = "PASS" if r.get("affinity_probability_binary", 0) and r["affinity_probability_binary"] > GATE_PROB else "fail"
        z_pass = (r.get("prior_z_LIMK2") or -99) > 0 and (r.get("prior_sel_z") or -99) > 0
        gate_z = "PASS" if z_pass else "fail"
        f.write("\t".join(row) + f"\t{gate_binary}\t{gate_z}\n")

print(f"Wrote → {FULL_TSV}")

# Print summary
print("\n=== BINARY-BINDER GATE SURVIVORS ===")
if not survivors_ranked:
    print("NONE.")
else:
    print(f"{'rank':>4} {'Ki_nM':>12} {'prob_bind':>10} {'aff_pred':>10} {'z_L2':>8} {'sel_z':>8}  SMILES")
    for i, r in enumerate(survivors_ranked[:20], start=1):
        ki = r["Ki_nM"]
        ki_s = f"{ki:.1f} nM" if ki < 1e4 else f"{ki:.2e} nM"
        zl = r.get("prior_z_LIMK2"); zs = r.get("prior_sel_z")
        zl_s = f"{zl:+.2f}" if zl is not None else "   —   "
        zs_s = f"{zs:+.2f}" if zs is not None else "   —   "
        print(f"{i:>4} {ki_s:>12} {r['affinity_probability_binary']:>10.3f} "
              f"{r['affinity_pred_value']:>10.3f} {zl_s:>8} {zs_s:>8}  {r['smiles'][:48]}")

print("\n=== PRIOR TOP-4 RESCORED (iptm rank invalid per affinity-head calibration) ===")
prior_top4_smiles = [
    "C[n+]1ccc(O)c2cc(C(=O)c3ccc(Oc4nccc[nH+]4)cc3)ccc21",
    "Cc1cccc(NC(=O)c2cccc(Oc3ccncn3)c2)c1O",
    "O=C(NCc1ccccc1)c1ccc(Cc2cccnc2)nc1",
    "CC1c2ccccc2CN1C(=O)c1ccc(-n2nccc2C(N)=O)cc1",
]
prior_rescored = [r for r in results if r["smiles"] in prior_top4_smiles]
for r in prior_rescored:
    ki_s = f"{r['Ki_nM']:.1f} nM" if r['Ki_nM'] and r['Ki_nM'] < 1e4 else f"{r['Ki_nM']:.2e} nM" if r['Ki_nM'] else "N/A"
    print(f"  {r['smiles'][:60]} → Ki {ki_s}, prob_bind {r.get('affinity_probability_binary')}")

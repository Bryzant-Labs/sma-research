"""Parse Boltz-2 affinity outputs and fit per-kinase linear regression.

Input: /home/bryza/sma-research/qms/chembl_ki_affinity_head/boltz_out/
       Expected layout: boltz_results_in/predictions/<job_id>/affinity_<job_id>.json
       + confidence_<job_id>_model_0.json (for iptm cross-check)

Output:
  - raw/<kinase>_affinity_rows.json — per-compound (smiles, ki_nM, affinity_pred_value, iptm_new)
  - fits.json — per-kinase {slope, intercept, r2, pearson, n, rmse, ci95}
  - fits_comparison.json — old iptm R² vs new affinity R²
"""
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path("/home/bryza/sma-research/qms/chembl_ki_affinity_head")
RAW = ROOT / "raw"
RAW.mkdir(exist_ok=True)
BOLTZ_OUT = ROOT / "boltz_out"

OLD_FITS = json.loads(
    Path("/home/bryza/sma-research/qms/chembl_ki_calibration/fits.json").read_text()
)

manifest = json.loads((RAW / "manifest.json").read_text())


def find_file(pattern):
    hits = list(BOLTZ_OUT.rglob(pattern))
    return hits[0] if hits else None


by_kinase = {}
missing = []
for row in manifest:
    jid = row["job_id"]
    k = row["kinase"]
    aff_path = find_file(f"affinity_{jid}.json")
    conf_path = find_file(f"confidence_{jid}_*.json")
    rec = dict(row)
    if aff_path:
        aff_json = json.loads(aff_path.read_text())
        rec["affinity_pred_value"] = aff_json.get("affinity_pred_value")
        rec["affinity_probability_binary"] = aff_json.get("affinity_probability_binary")
        rec["affinity_pred_value1"] = aff_json.get("affinity_pred_value1")
        rec["affinity_pred_value2"] = aff_json.get("affinity_pred_value2")
    else:
        rec["affinity_pred_value"] = None
        missing.append((jid, "affinity"))
    if conf_path:
        cj = json.loads(conf_path.read_text())
        rec["iptm_new"] = cj.get("iptm", cj.get("complex_iptm"))
        rec["ptm_new"] = cj.get("ptm", cj.get("complex_ptm"))
    else:
        rec["iptm_new"] = None
    by_kinase.setdefault(k, []).append(rec)


def fit_linear(xs, ys):
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)
    n = len(xs)
    if n < 3:
        return None
    slope, intercept = np.polyfit(xs, ys, 1)
    y_pred = slope * xs + intercept
    resid = ys - y_pred
    ss_res = float(np.sum(resid**2))
    ss_tot = float(np.sum((ys - ys.mean()) ** 2))
    r2 = float(1 - ss_res / ss_tot) if ss_tot > 0 else None
    rmse = float(math.sqrt(ss_res / n))
    # Pearson
    if xs.std() > 0 and ys.std() > 0:
        pearson = float(np.cov(xs, ys, ddof=1)[0, 1] / (xs.std(ddof=1) * ys.std(ddof=1)))
    else:
        pearson = None
    # 95% CI on slope (simple t-based)
    if n > 2:
        se_resid = math.sqrt(ss_res / (n - 2))
        x_ss = float(np.sum((xs - xs.mean()) ** 2))
        se_slope = se_resid / math.sqrt(x_ss) if x_ss > 0 else None
        # t_{0.975, n-2} ~ approx via normal (1.96) for quick CI — acceptable for small n
        # Use 2.1 for n=20 (df=18); table value for df=18 is 2.101
        t_val = 2.101 if n <= 25 else 1.96
        slope_ci = (float(slope - t_val * se_slope), float(slope + t_val * se_slope)) if se_slope else None
    else:
        slope_ci = None
    return {
        "slope": float(slope),
        "intercept": float(intercept),
        "r2": r2,
        "pearson": pearson,
        "n": int(n),
        "rmse_log10_ki": rmse,
        "slope_ci_95": slope_ci,
        "x_range": [float(xs.min()), float(xs.max())],
        "y_range": [float(ys.min()), float(ys.max())],
    }


def fit_log1p_prob(xs_prob, ys):
    """Alternative: regress log10_Ki against affinity_probability_binary (0-1)."""
    return fit_linear(xs_prob, ys)


fits = {}
fits_prob = {}
comparison = {}
for k, rows in by_kinase.items():
    ok = [r for r in rows if r.get("affinity_pred_value") is not None]
    xs = [r["affinity_pred_value"] for r in ok]
    ys = [r["log10_ki_nM"] for r in ok]
    fit = fit_linear(xs, ys)
    fits[k] = fit

    # Also regress against probability_binary
    xs_p = [r["affinity_probability_binary"] for r in ok if r.get("affinity_probability_binary") is not None]
    ys_p = [r["log10_ki_nM"] for r in ok if r.get("affinity_probability_binary") is not None]
    fits_prob[k] = fit_log1p_prob(xs_p, ys_p)

    old = OLD_FITS.get(k, {})
    comparison[k] = {
        "iptm_old": {"r2": old.get("r2"), "pearson": old.get("pearson"), "n": old.get("n")},
        "affinity_pred_value": {
            "r2": fit["r2"] if fit else None,
            "pearson": fit["pearson"] if fit else None,
            "rmse_log10_ki": fit["rmse_log10_ki"] if fit else None,
            "n": fit["n"] if fit else None,
        },
        "affinity_probability_binary": {
            "r2": fits_prob[k]["r2"] if fits_prob[k] else None,
            "pearson": fits_prob[k]["pearson"] if fits_prob[k] else None,
            "n": fits_prob[k]["n"] if fits_prob[k] else None,
        },
    }

    (RAW / f"{k}_affinity_rows.json").write_text(json.dumps(rows, indent=2))

(ROOT / "fits.json").write_text(json.dumps(fits, indent=2))
(ROOT / "fits_probability.json").write_text(json.dumps(fits_prob, indent=2))
(ROOT / "fits_comparison.json").write_text(json.dumps(comparison, indent=2))

if missing:
    (ROOT / "missing.log").write_text("\n".join(f"{j},{w}" for j, w in missing))
    print(f"WARNING: {len(missing)} missing outputs (see missing.log)")

print("\n=== FIT RESULTS ===")
print(f"{'kinase':<8} {'n':>3} {'R²(affinity)':>14} {'R²(iptm_old)':>14} {'Δ':>8}  {'Pearson':>8}")
for k in ["LIMK2", "ROCK2", "JAK2", "MAPK14"]:
    f = fits.get(k)
    old = OLD_FITS.get(k, {})
    if not f:
        print(f"  {k}: NO FIT")
        continue
    dr2 = (f["r2"] - old.get("r2", 0)) if f["r2"] and old.get("r2") is not None else None
    print(
        f"{k:<8} {f['n']:>3} "
        f"{f['r2']:>14.3f} "
        f"{old.get('r2', float('nan')):>14.3f} "
        f"{dr2:>8.3f} "
        f"{f['pearson']:>8.3f}"
    )

print("\n=== GATE ===")
for k, f in fits.items():
    if not f:
        continue
    if f["r2"] >= 0.5:
        print(f"  {k}: USABLE (R²={f['r2']:.3f} >= 0.5) → orchestration-layer affinity calibration")
    elif f["r2"] >= 0.3:
        print(f"  {k}: PARTIAL (R²={f['r2']:.3f}, 0.3-0.5) → rank-only, not quantitative")
    else:
        print(f"  {k}: NULL (R²={f['r2']:.3f} < 0.3) → still unusable")

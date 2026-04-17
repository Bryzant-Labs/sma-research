"""Rescore our top LIMK2-alphaC and ROCK2-alphaC lead compounds via calibrated regression.

For each lead, we have an existing iptm (from prior Boltz-2 panels). Apply the per-kinase
fit (slope, intercept) to estimate Ki_nM. Also compute 95% prediction intervals from
residual std.
"""
import json
import math
import numpy as np
from pathlib import Path

OUT = Path("/home/bryza/sma-research/qms/chembl_ki_calibration")
RAW = OUT / "raw"

# Load fits
fits = json.loads((OUT / "fits.json").read_text())

# Load calibration rows to compute residual SD
def residual_sd(gene):
    rows = json.loads((RAW / f"{gene}_calibration_rows.json").read_text())
    rows = [r for r in rows if r["error"] is None and r["iptm"] > 0]
    fit = fits[gene]
    if "slope" not in fit:
        return None
    xs = np.array([r["iptm"] for r in rows])
    ys = np.array([r["log10_ki_nM"] for r in rows])
    yhat = fit["slope"] * xs + fit["intercept"]
    resid = ys - yhat
    return float(resid.std(ddof=1))


# Top LIMK2-alphaC leads (from limk2_activator_alphaC_RESULTS.md table)
# These have existing iptm from the prior 15-kinase panel (column iptm_LIMK2)
LIMK2_LEADS = [
    {"rank": 1, "sdf": "14.sdf", "smiles": "COc1cc(C)ccc1C(C)NCC1=CC=[N+]2C1=Nc1c[n+](Cc3cncc[nH+]3)ccc12", "iptm": 0.924},
    {"rank": 2, "sdf": "43.sdf", "smiles": "CS(=O)(=O)c1ccccc1-c1cccc(Oc2ccc(C(N)=O)cc2)c1", "iptm": 0.942},
    {"rank": 3, "sdf": "176.sdf", "smiles": "CCc1nc2ccc[nH+]c2cc1OCc1ccc2[nH]cc(C(=O)O)c2c1", "iptm": 0.915},
    {"rank": 4, "sdf": "3.sdf", "smiles": "COc1cc(OC)c(OC)c(C(=O)N2CCN(C(=O)c3ccncc3)CC2)c1", "iptm": 0.910},
]

# Top ROCK2-alphaC leads (from rock2_activator_RESULTS.md top-10)
ROCK2_LEADS = [
    {"rank": 1, "smiles": "Clc1ccc2c(n1)NC(NC1CCCc3c(nc4ccncnc3-4)C1)C2", "iptm": 0.976},
    {"rank": 2, "smiles": "COc1ccc(CCNNC2CCCC3C(=O)CCCC3C2N)cc1", "iptm": 0.968},
    {"rank": 3, "smiles": "ClC1CCCC2NC(CNC3CCN(c4cccnc4)C3)NCC12", "iptm": 0.953},
    {"rank": 4, "smiles": "O=C1CCC=NC2CC3N[N+](Nc4ccc(=O)[nH]c4)=CCCC3C12", "iptm": 0.948},
    {"rank": 5, "smiles": "CC1OC2C=C(Nc3cc4c(F)cccc4c4ccc(C(=O)O)nc34)CC2C1=O", "iptm": 0.939},
    {"rank": 6, "smiles": "CC1CCC(O)C2OC2C2(C1)CC1Cc3ccccc3OC1=C2O", "iptm": 0.934},
    {"rank": 7, "smiles": "CC1CCCC(=CCNN2Cc3nccn4c3c(c3cc(N)ccc34)C2)C1=O", "iptm": 0.929},
    {"rank": 8, "smiles": "Cc1cccc2c1[nH+]cn2C(O)=NCC1CC=C2C(C=C3C=CNC=N3)CCC21", "iptm": 0.919},
    {"rank": 9, "smiles": "OC12C3=CCCC1CC1CC(C=[N+]=Nc4ccccn4)CC(=NN3)C12", "iptm": 0.917},
    {"rank": 10, "smiles": "Oc1ccc(CN2N=C(c3ccc(O)cc3)Nc3ccccc32)cc1", "iptm": 0.917},
]


def predict_ki(gene, iptm):
    fit = fits[gene]
    slope = fit["slope"]
    intercept = fit["intercept"]
    logKi = slope * iptm + intercept
    ki = 10 ** logKi
    # 95% PI ~ +/- 1.96 * residual_sd in log10 space
    rsd = residual_sd(gene)
    if rsd is None:
        return ki, None, None, rsd
    lo = 10 ** (logKi - 1.96 * rsd)
    hi = 10 ** (logKi + 1.96 * rsd)
    return ki, lo, hi, rsd


def fmt(x):
    if x is None:
        return "n/a"
    if x > 1e6:
        return f"{x:.2e}"
    if x > 1000:
        return f"{x/1000:.1f} uM"
    return f"{x:.2f} nM"


def main():
    out_rows = []

    print("=== LIMK2-alphaC leads (calibrated against LIMK2 fit, R^2=%.3f) ===" % fits["LIMK2"]["r2"])
    for l in LIMK2_LEADS:
        ki, lo, hi, rsd = predict_ki("LIMK2", l["iptm"])
        row = {"target": "LIMK2", "gene_used": "LIMK2", "rank": l["rank"],
               "smiles": l["smiles"], "iptm": l["iptm"],
               "ki_nM_est": ki, "ki_lo95": lo, "ki_hi95": hi, "resid_sd": rsd}
        out_rows.append(row)
        print(f"  rank{l['rank']} iptm={l['iptm']:.3f} -> Ki~{fmt(ki)}  [95%PI {fmt(lo)} .. {fmt(hi)}]")

    print("\n=== ROCK2-alphaC leads (calibrated against ROCK2 fit, R^2=%.3f) ===" % fits["ROCK2"]["r2"])
    for l in ROCK2_LEADS:
        ki, lo, hi, rsd = predict_ki("ROCK2", l["iptm"])
        row = {"target": "ROCK2", "gene_used": "ROCK2", "rank": l["rank"],
               "smiles": l["smiles"], "iptm": l["iptm"],
               "ki_nM_est": ki, "ki_lo95": lo, "ki_hi95": hi, "resid_sd": rsd}
        out_rows.append(row)
        print(f"  rank{l['rank']} iptm={l['iptm']:.3f} -> Ki~{fmt(ki)}  [95%PI {fmt(lo)} .. {fmt(hi)}]")

    (OUT / "rescored_leads.json").write_text(json.dumps(out_rows, indent=2))
    print(f"\nSaved: {OUT/'rescored_leads.json'}")


if __name__ == "__main__":
    main()

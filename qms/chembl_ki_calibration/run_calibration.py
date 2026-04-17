"""ChEMBL Ki calibration for Boltz-2 iptm.

For each of N kinases:
  1. Query ChEMBL Ki activities (standard_type=Ki, standard_units=nM, pchembl_value defined)
  2. Take a diverse subset of N_PAIRS compounds (log-Ki spread across ranges)
  3. Boltz-2 co-fold each (kinase-domain + compound) -> iptm
  4. Linear regression: log10(Ki_nM) = slope * iptm + intercept
  5. Report slope, intercept, R^2, n

Then rescore our top LIMK2-alphaC + ROCK2-alphaC lead compounds and estimate Ki.

Usage: python3 run_calibration.py [--n-pairs N]
"""
import json
import os
import sys
import time
import math
import urllib.request
import urllib.error
import urllib.parse
import argparse
from pathlib import Path

import numpy as np

# ---------------- CONFIG ----------------
URL = os.environ.get("BOLTZ2_URL", "http://localhost:8004/predict")
RECYCLING_STEPS = 1
SAMPLING_STEPS = 25

OUT_DIR = Path("/home/bryza/sma-research/qms/chembl_ki_calibration")
RAW_DIR = OUT_DIR / "raw"
RAW_DIR.mkdir(exist_ok=True, parents=True)

# Kinase domains (UniProt-based, hand-curated)
# Ranges reflect canonical kinase catalytic domain for docking purposes.
KINASES = {
    # gene -> (chembl_id, uniprot, kd_start, kd_end)
    "LIMK2":  ("CHEMBL5932", "P53671", 330, 610),   # kinase domain 330-610
    "ROCK2":  ("CHEMBL2973", "O75116",  92, 354),   # ROCK2 kinase 92-354
    "JAK2":   ("CHEMBL2971", "O60674", 840, 1132),  # JH1 catalytic
    "MAPK14": ("CHEMBL260",  "Q16539",   4, 353),   # ~full
    "CDK2":   ("CHEMBL301",  "P24941",   1, 298),   # full
    "CDK5":   ("CHEMBL4036", "Q00535",   1, 292),   # full
    "LIMK1":  ("CHEMBL3836", "P53667", 340, 620),   # kinase domain
    "ROCK1":  ("CHEMBL3231", "Q13464",  91, 354),   # ROCK1 kinase
}

# ---------------- HTTP HELPERS ----------------
def get_uniprot_seq(acc):
    url = f"https://rest.uniprot.org/uniprotkb/{acc}.fasta"
    with urllib.request.urlopen(url, timeout=20) as r:
        txt = r.read().decode()
    return "".join(txt.split("\n")[1:]).strip()


def fetch_chembl_ki(target_chembl_id, limit=200):
    """Fetch Ki activities for a target. Returns list of dicts with smiles, ki_nM, pchembl."""
    base = "https://www.ebi.ac.uk/chembl/api/data/activity.json"
    params = {
        "target_chembl_id": target_chembl_id,
        "standard_type": "Ki",
        "standard_units": "nM",
        "standard_relation": "=",
        "pchembl_value__isnull": "false",
        "limit": min(limit, 1000),
    }
    q = urllib.parse.urlencode(params)
    out = []
    url = f"{base}?{q}"
    while url and len(out) < limit:
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.loads(r.read())
        for a in data.get("activities", []):
            smi = a.get("canonical_smiles")
            val = a.get("standard_value")
            pch = a.get("pchembl_value")
            if not (smi and val and pch):
                continue
            try:
                ki_nM = float(val)
                if ki_nM <= 0:
                    continue
            except (ValueError, TypeError):
                continue
            out.append({
                "smiles": smi,
                "ki_nM": ki_nM,
                "pchembl": float(pch),
                "chembl_id": a.get("molecule_chembl_id"),
                "assay_chembl_id": a.get("assay_chembl_id"),
                "assay_type": a.get("assay_type"),
            })
        # paginate
        nxt = data.get("page_meta", {}).get("next")
        url = (f"https://www.ebi.ac.uk{nxt}" if nxt else None)
        if len(out) >= limit:
            break
    return out


def diverse_subset(entries, n=30):
    """Pick n entries diverse across pchembl spread. Deduplicate by SMILES."""
    # Dedup: keep median Ki per SMILES
    by_smi = {}
    for e in entries:
        s = e["smiles"]
        by_smi.setdefault(s, []).append(e["ki_nM"])
    uniq = []
    for s, kis in by_smi.items():
        med = float(np.median(kis))
        uniq.append({"smiles": s, "ki_nM": med, "pchembl": 9.0 - math.log10(med)})
    # Skip multi-fragment (contains ".") and very long (>80 heavy atoms)
    uniq = [e for e in uniq if "." not in e["smiles"] and len(e["smiles"]) < 200]
    # Stratify by log10 Ki decade
    uniq.sort(key=lambda e: e["ki_nM"])
    if len(uniq) <= n:
        return uniq
    # Uniform sampling across log-Ki sorted list
    idxs = np.linspace(0, len(uniq) - 1, n).astype(int)
    picked = [uniq[i] for i in idxs]
    return picked


def call_boltz2(protein_seq, smiles, timeout=900):
    body = {
        "polymers": [{"id": "A", "sequence": protein_seq}],
        "ligands": [{"id": "L1", "smiles": smiles}],
        "recycling_steps": RECYCLING_STEPS,
        "sampling_steps": SAMPLING_STEPS,
    }
    req = urllib.request.Request(
        URL, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
        iptm = data.get("iptm_scores", [0.0])[0]
        ptm = data.get("ptm_scores", [0.0])[0]
        plddt = data.get("complex_plddt_scores", [0.0])[0]
        return iptm, ptm, plddt, None
    except urllib.error.HTTPError as e:
        return 0.0, 0.0, 0.0, f"HTTP {e.code}: {e.read()[:200].decode(errors='ignore')}"
    except Exception as e:
        return 0.0, 0.0, 0.0, f"ERR: {str(e)[:200]}"


def linear_fit(xs, ys):
    """Returns slope, intercept, r2, n (for ys = slope*xs + intercept)."""
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)
    n = len(xs)
    if n < 3:
        return None, None, None, n
    slope, intercept = np.polyfit(xs, ys, 1)
    y_pred = slope * xs + intercept
    ss_res = float(np.sum((ys - y_pred) ** 2))
    ss_tot = float(np.sum((ys - ys.mean()) ** 2))
    r2 = (1 - ss_res / ss_tot) if ss_tot > 0 else None
    return float(slope), float(intercept), r2, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-pairs", type=int, default=25, help="Ki-SMILES pairs per kinase")
    ap.add_argument("--kinases", nargs="+", default=["LIMK2", "ROCK2", "JAK2", "MAPK14"],
                    help="subset of kinases to calibrate")
    args = ap.parse_args()

    print(f"[calib] n_pairs={args.n_pairs} kinases={args.kinases}")

    # Step 1: fetch sequences
    seqs = {}
    for g in args.kinases:
        cid, acc, s, e = KINASES[g]
        full = get_uniprot_seq(acc)
        kd = full[s - 1:e]
        seqs[g] = kd
        print(f"  {g} {acc} KD {s}-{e} len={len(kd)}")

    (OUT_DIR / "kinase_sequences.json").write_text(json.dumps({
        g: {"uniprot": KINASES[g][1], "kd_start": KINASES[g][2],
            "kd_end": KINASES[g][3], "seq": seqs[g]}
        for g in args.kinases}, indent=2))

    # Step 2: for each kinase, fetch ChEMBL Ki, build calibration set, co-fold
    all_fits = {}
    for g in args.kinases:
        print(f"\n=== {g} ===")
        cid = KINASES[g][0]
        try:
            entries = fetch_chembl_ki(cid, limit=400)
        except Exception as e:
            print(f"  [{g}] ChEMBL fetch failed: {e}")
            continue
        print(f"  [{g}] ChEMBL Ki entries: {len(entries)}")
        # Filter: Ki in [0.01 nM, 1e6 nM]
        entries = [e for e in entries if 0.01 <= e["ki_nM"] <= 1e6]
        picked = diverse_subset(entries, n=args.n_pairs)
        print(f"  [{g}] picked {len(picked)} diverse pairs (log-Ki range "
              f"{math.log10(picked[0]['ki_nM']):.2f}..{math.log10(picked[-1]['ki_nM']):.2f})")

        (RAW_DIR / f"{g}_chembl_pairs.json").write_text(json.dumps(picked, indent=2))

        rows = []
        for i, e in enumerate(picked):
            t0 = time.time()
            iptm, ptm, plddt, err = call_boltz2(seqs[g], e["smiles"])
            dt = time.time() - t0
            logKi = math.log10(e["ki_nM"])
            rows.append({
                "smiles": e["smiles"],
                "ki_nM": e["ki_nM"],
                "log10_ki_nM": logKi,
                "iptm": iptm, "ptm": ptm, "plddt": plddt,
                "error": err, "elapsed_s": dt,
            })
            print(f"  [{g} {i+1}/{len(picked)}] iptm={iptm:.3f} log10Ki={logKi:.2f} err={err} t={dt:.1f}s", flush=True)
            # Checkpoint
            (RAW_DIR / f"{g}_calibration_rows.json").write_text(json.dumps(rows, indent=2))

        # Fit
        ok = [r for r in rows if r["error"] is None and r["iptm"] > 0]
        if len(ok) >= 3:
            slope, intercept, r2, n = linear_fit([r["iptm"] for r in ok],
                                                  [r["log10_ki_nM"] for r in ok])
            # Also Pearson
            xs = np.array([r["iptm"] for r in ok])
            ys = np.array([r["log10_ki_nM"] for r in ok])
            cov = float(np.cov(xs, ys, ddof=1)[0, 1])
            pearson = float(cov / (xs.std(ddof=1) * ys.std(ddof=1))) if xs.std() > 0 and ys.std() > 0 else None
            all_fits[g] = {
                "slope": slope, "intercept": intercept, "r2": r2, "n": n,
                "pearson": pearson,
                "iptm_range": [float(xs.min()), float(xs.max())],
                "log10Ki_range": [float(ys.min()), float(ys.max())],
            }
            print(f"  [{g} FIT] log10(Ki_nM) = {slope:.3f} * iptm + {intercept:.3f}  R^2={r2:.3f} pearson={pearson:.3f} n={n}")
        else:
            all_fits[g] = {"error": f"only {len(ok)} ok pairs"}

        (OUT_DIR / "fits.json").write_text(json.dumps(all_fits, indent=2))

    print("\n=== DONE — fits per kinase ===")
    for g, fit in all_fits.items():
        print(f"  {g}: {fit}")


if __name__ == "__main__":
    main()

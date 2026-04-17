#!/usr/bin/env python3
"""Boltz-2 selectivity panel for extended atlas cascade.

For each of 9 atlas targets (primary) + 15-kinase panel (off-target reference):
  - Take top 10 per target from top100_<TARGET>.tsv
  - Dock each compound against 16 proteins total (1 primary + 15 kinases)
  - Compute Z-score selectivity: z_primary - mean(z_kinases)

Gate: z_primary > 0 AND sel_z > 0.

Server: Boltz-2 self-host (localhost:8003 default, 8004 fallback)

Usage:
  python boltz2_panel_extended.py <cascade_output_dir> [--top-n 10] [--max-workers 8]

Writes:
  <out>/boltz2_panel_<target>.jsonl    - raw predictions
  <out>/zscore_matrix_<target>.csv     - compound × protein matrix with Z-scores
  <out>/zscore_combined.csv            - all targets combined
"""
import argparse
import csv
import json
import os
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests


KINASE_PANEL_PATH = Path("/home/bryza/fleet-results/kinase_panel_domains.json")
TARGET_DOMAINS_PATH = Path("/home/bryza/sma-research/qms/proteome_wide_2026/extended_target_domains.json")
BOLTZ_URLS = ["http://localhost:8003/predict", "http://localhost:8004/predict"]


def pick_server():
    for url in BOLTZ_URLS:
        try:
            r = requests.get(url.replace("/predict", "/health"), timeout=5)
            if r.status_code == 200 and r.json().get("status") == "ready":
                return url
        except Exception:
            pass
    return None


def boltz2_call(url, seq, smi, cid, tname, retries=2):
    for attempt in range(retries):
        try:
            r = requests.post(url, json={
                "polymers": [{"id": "A", "molecule_type": "protein", "sequence": seq}],
                "ligands": [{"id": "L1", "smiles": smi}],
                "recycling_steps": 1,
                "sampling_steps": 25,
            }, timeout=1800)
            if r.status_code == 200:
                j = r.json()
                return {
                    "compound_id": cid, "target": tname, "smiles": smi,
                    "iptm": float(j["iptm_scores"][0]),
                    "ptm": float(j["ptm_scores"][0]),
                    "plddt": float(j["complex_plddt_scores"][0]),
                    "conf": float(j["confidence_scores"][0]),
                }
            err = f"http{r.status_code}:{r.text[:200]}"
        except Exception as e:
            err = f"exc:{type(e).__name__}:{e}"
        time.sleep(5 * (attempt + 1))
    return {"compound_id": cid, "target": tname, "smiles": smi, "error": err}


def run_target(url, primary_target, top_compounds, primary_seq, kinase_panel,
               out_dir, max_workers=6):
    """Run 1 primary + 15 kinases × N compounds Boltz-2 panel."""
    all_proteins = {primary_target: primary_seq, **kinase_panel}
    jobs = []
    for c in top_compounds:
        cid = f"{primary_target}_cpd_{c['rank']}"
        smi = c["smiles"]
        for tname, seq in all_proteins.items():
            jobs.append((smi, cid, tname, seq))
    print(f"[{primary_target}] {len(top_compounds)} compounds × {len(all_proteins)} proteins = {len(jobs)} calls")

    results = []
    raw_out = open(out_dir / f"boltz2_panel_{primary_target}.jsonl", "w")
    t0 = time.time()
    errors = 0
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(boltz2_call, url, seq, smi, cid, tname): (cid, tname)
                for smi, cid, tname, seq in jobs}
        done = 0
        for fut in as_completed(futs):
            res = fut.result()
            results.append(res)
            raw_out.write(json.dumps(res) + "\n")
            raw_out.flush()
            done += 1
            if "error" in res:
                errors += 1
            if done % 10 == 0 or done == len(jobs):
                elapsed = time.time() - t0
                rate = done / elapsed if elapsed > 0 else 0
                eta = (len(jobs) - done) / rate if rate > 0 else 0
                print(f"[{primary_target}] {done}/{len(jobs)} | {errors} err | {rate:.2f}/s | ETA {eta/60:.1f}m")
    raw_out.close()

    # Aggregate
    by_cpd = {}
    for r in results:
        if "error" in r:
            continue
        by_cpd.setdefault(r["compound_id"], {})[r["target"]] = r["iptm"]

    # Compute per-target mean/std across compounds
    target_stats = {}
    for t in all_proteins:
        vals = [d[t] for d in by_cpd.values() if t in d]
        if len(vals) >= 2:
            target_stats[t] = (statistics.mean(vals), statistics.stdev(vals))

    # Compound matrix
    zscore_rows = []
    kinases = list(kinase_panel.keys())
    for cid, d in by_cpd.items():
        row = {"compound_id": cid, "primary_target": primary_target,
               "n_scored": len(d)}
        for t in [primary_target] + kinases:
            row[f"iptm_{t}"] = d.get(t)
        zs = {}
        for t in [primary_target] + kinases:
            iptm = d.get(t)
            if iptm is not None and t in target_stats:
                mu, sd = target_stats[t]
                z = (iptm - mu) / sd if sd > 0 else 0.0
                zs[t] = z
                row[f"z_{t}"] = z
            else:
                row[f"z_{t}"] = None
        z_primary = zs.get(primary_target)
        kinase_z = [v for k, v in zs.items() if k in kinases]
        mean_z_kinases = statistics.mean(kinase_z) if kinase_z else 0.0
        row["z_primary"] = z_primary
        row["mean_z_kinases"] = mean_z_kinases
        row["selectivity_z"] = (z_primary - mean_z_kinases) if z_primary is not None else None
        zscore_rows.append(row)

    zscore_rows.sort(key=lambda r: (-(r["selectivity_z"] if r["selectivity_z"] is not None else -99)))

    # Write CSV
    matrix_path = out_dir / f"zscore_matrix_{primary_target}.csv"
    if zscore_rows:
        keys = list(zscore_rows[0].keys())
        with open(matrix_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            for row in zscore_rows:
                w.writerow(row)
    print(f"[{primary_target}] wrote {matrix_path}")
    return zscore_rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("cascade_dir", type=Path, help="Dir with top100_<TARGET>.tsv files")
    p.add_argument("--top-n", type=int, default=10)
    p.add_argument("--max-workers", type=int, default=6)
    p.add_argument("--out-dir", type=Path, default=None)
    p.add_argument("--targets", nargs="+", default=[
        "EP400", "PEAK1", "KAT7", "RNF213", "EHMT2", "KAT6A", "KAT5", "KMT5B", "EHMT1"
    ])
    args = p.parse_args()

    out_dir = args.out_dir or args.cascade_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    url = pick_server()
    if url is None:
        print("ERROR: no Boltz-2 server healthy", file=sys.stderr)
        sys.exit(2)
    print(f"[boltz2] using {url}")

    kinase_panel = json.load(open(KINASE_PANEL_PATH))
    domains = json.load(open(TARGET_DOMAINS_PATH))

    all_rows = []
    for tgt in args.targets:
        if tgt not in domains:
            print(f"[{tgt}] no domain sequence; skipping")
            continue
        top_tsv = args.cascade_dir / f"top100_{tgt}.tsv"
        if not top_tsv.exists():
            print(f"[{tgt}] no {top_tsv}; skipping")
            continue
        # Load top-N
        top_compounds = []
        with open(top_tsv) as f:
            reader = csv.DictReader(f, delimiter="\t")
            for i, row in enumerate(reader, 1):
                if i > args.top_n:
                    break
                top_compounds.append({"rank": i, "smiles": row["smiles"], "cfd_pos": float(row["cfd_pos"])})
        if not top_compounds:
            print(f"[{tgt}] top100 file empty; skipping")
            continue

        rows = run_target(url, tgt, top_compounds, domains[tgt]["seq"],
                          kinase_panel, out_dir, max_workers=args.max_workers)
        all_rows.extend(rows)

    # Combined z-score file
    if all_rows:
        combined = out_dir / "zscore_combined.csv"
        keys = list(all_rows[0].keys())
        with open(combined, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            for row in all_rows:
                w.writerow(row)
        # Cross-target ranking
        selected = [r for r in all_rows
                    if r["z_primary"] is not None and r["z_primary"] > 0
                    and r["selectivity_z"] is not None and r["selectivity_z"] > 0]
        selected.sort(key=lambda r: -r["selectivity_z"])
        print(f"\n[COMBINED] {len(all_rows)} rows total, {len(selected)} pass z_primary > 0 AND sel_z > 0")
        print(f"\n[TOP-10 CROSS-TARGET]")
        for r in selected[:10]:
            print(f"  {r['compound_id']:30s} z_primary={r['z_primary']:.3f} sel_z={r['selectivity_z']:.3f}")
        # Write ranked top
        top_path = out_dir / "cross_target_top_hits.csv"
        with open(top_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            for row in selected[:50]:
                w.writerow(row)
        print(f"[wrote] {top_path}")


if __name__ == "__main__":
    main()

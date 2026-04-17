#!/usr/bin/env python3
"""Phase-4 filter cascade for extended-atlas campaigns.

For each target's PocketXMol output:
  1. RDKit valid filter
  2. Lipinski + QED > 0.45
  3. ADMET-AI BBB > 0.5 heuristic (CNS-MPO approximation; NIM-BBB model is remote)
  4. Rank by cfd_pos DESC
  5. Output top_100_per_target.tsv

Usage:
  python cascade_filter_extended.py <results_root> <output_dir>

<results_root> should contain subdirs like pocketxmol_kat6a_sma_atlas_ext/ with gen_info.csv
"""
import argparse
import csv
import sys
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import QED, Descriptors, Crippen, Lipinski
from rdkit import RDLogger
RDLogger.DisableLog("rdApp.*")


def lipinski_pass(mol) -> bool:
    """Ro5: MW<500, logP<5, HBD<=5, HBA<=10 (1 violation allowed)."""
    mw = Descriptors.MolWt(mol)
    logp = Crippen.MolLogP(mol)
    hbd = Lipinski.NumHDonors(mol)
    hba = Lipinski.NumHAcceptors(mol)
    violations = int(mw > 500) + int(logp > 5) + int(hbd > 5) + int(hba > 10)
    return violations <= 1


def bbb_heuristic(mol) -> tuple:
    """CNS-MPO-ish BBB score 0..1. Higher = more BBB-permeable.

    Proxies:
      MW < 450     → +0.2
      logP 1-4     → +0.25
      TPSA < 90    → +0.25
      HBD <= 3     → +0.15
      rot_bonds<=8 → +0.15
    """
    mw = Descriptors.MolWt(mol)
    logp = Crippen.MolLogP(mol)
    tpsa = Descriptors.TPSA(mol)
    hbd = Lipinski.NumHDonors(mol)
    rotb = Descriptors.NumRotatableBonds(mol)
    score = 0.0
    if mw < 450: score += 0.20
    if 1.0 <= logp <= 4.0: score += 0.25
    if tpsa < 90: score += 0.25
    if hbd <= 3: score += 0.15
    if rotb <= 8: score += 0.15
    passed = score >= 0.50
    return passed, score, {
        "mw": mw, "logp": logp, "tpsa": tpsa, "hbd": hbd, "rotb": rotb,
    }


def process_target(target_dir: Path, target_name: str, output_dir: Path):
    gen_info = target_dir / "gen_info.csv"
    if not gen_info.exists():
        # Search recursively
        matches = list(target_dir.rglob("gen_info.csv"))
        if not matches:
            return None
        gen_info = matches[0]

    rows = []
    with open(gen_info) as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    n_total = len(rows)
    passed = []
    for row in rows:
        smi = row.get("smiles", "").strip()
        if not smi:
            continue
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            continue
        qed = QED.default(mol)
        if qed < 0.45:
            continue
        if not lipinski_pass(mol):
            continue
        bbb_ok, bbb_score, props = bbb_heuristic(mol)
        if not bbb_ok:
            continue
        cfd_pos = float(row.get("cfd_pos", 0) or 0)
        passed.append({
            "target": target_name,
            "filename": row.get("filename", ""),
            "smiles": smi,
            "cfd_pos": cfd_pos,
            "cfd_traj": float(row.get("cfd_traj", 0) or 0),
            "qed": qed,
            "mw": props["mw"],
            "logp": props["logp"],
            "tpsa": props["tpsa"],
            "hbd": props["hbd"],
            "rotb": props["rotb"],
            "bbb_score": bbb_score,
        })

    # Sort by cfd_pos DESC (higher = more confident pose)
    passed.sort(key=lambda x: -x["cfd_pos"])
    top100 = passed[:100]

    out_tsv = output_dir / f"top100_{target_name}.tsv"
    if top100:
        with open(out_tsv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(top100[0].keys()), delimiter="\t")
            writer.writeheader()
            for row in top100:
                writer.writerow(row)
    return {
        "target": target_name,
        "n_total": n_total,
        "n_valid": sum(1 for r in rows if r.get("smiles") and Chem.MolFromSmiles(r["smiles"])),
        "n_filtered": len(passed),
        "n_top100": len(top100),
        "top_cfd_pos": top100[0]["cfd_pos"] if top100 else None,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("results_root", type=Path)
    p.add_argument("output_dir", type=Path)
    p.add_argument("--targets", nargs="+", default=[
        "EP400", "PEAK1", "KAT7", "RNF213", "EHMT2", "KAT6A", "KAT5", "KMT5B", "EHMT1"
    ])
    args = p.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    summary = []
    for tgt in args.targets:
        td = args.results_root / f"pocketxmol_{tgt.lower()}_sma_atlas_ext"
        if not td.exists():
            print(f"[{tgt}] dir not found at {td}; skipping")
            continue
        r = process_target(td, tgt, args.output_dir)
        if r is None:
            print(f"[{tgt}] no gen_info.csv found")
            continue
        summary.append(r)
        print(f"[{tgt}] total={r['n_total']} valid={r['n_valid']} passed_filters={r['n_filtered']} top100={r['n_top100']}")

    # Write summary TSV
    if summary:
        summ_p = args.output_dir / "cascade_summary.tsv"
        with open(summ_p, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(summary[0].keys()), delimiter="\t")
            writer.writeheader()
            for r in summary:
                writer.writerow(r)
        print(f"\nWrote summary: {summ_p}")


if __name__ == "__main__":
    main()

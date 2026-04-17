#!/usr/bin/env python3
"""Analyze PocketXMol campaign output: validity, QED, BBB, Zn-chelator motif detection.

Usage:
  python analyze_pxm_campaign.py <results_dir> [--zn-chelator-check]

<results_dir> should contain gen_info.csv + SDF/ (copied from /results/pocketxmol/<task_id>)
"""
import argparse
import csv
import sys
from pathlib import Path

try:
    from rdkit import Chem
    from rdkit.Chem import QED, Descriptors, AllChem
    from rdkit import RDLogger
    RDLogger.DisableLog("rdApp.*")
except ImportError:
    print("RDKit required. pip install rdkit", file=sys.stderr)
    sys.exit(1)


# Zn-chelator SMARTS patterns (HDAC inhibitor warhead classes)
ZN_CHELATOR_PATTERNS = {
    "hydroxamate": "[CX3](=[OX1])[NX3][OX2H]",          # C(=O)N-OH
    "hydroxamate_ionized": "[CX3](=[OX1])[NX3][OX1-]",    # deprotonated
    "anilide_ketone": "[CX3](=O)[NX3H][c]",               # aryl amide (o-aminoanilide class precursor)
    "o_aminoanilide": "[NX3H2]c1ccccc1[NX3H][CX3](=O)",   # 2-aminoanilide (mocetinostat/entinostat class)
    "carboxylic_acid": "[CX3](=O)[OX2H]",                  # valproate class (weak)
    "thiol": "[SX2H]",                                     # romidepsin-like (SH)
    "benzamide_NH2": "c1ccc(cc1)[NX3H][CX3](=O)",         # benzamide near aniline (entinostat)
    "ketone_alpha_amide": "[CX3](=O)[CX3](=O)[NX3H]",     # alpha-ketoamide
    "trifluoromethylketone": "[CX3](=O)C(F)(F)F",          # TFMK class
}


def classify_zn_chelator(smiles):
    """Return list of Zn-chelator motifs present in molecule."""
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return [], False
        hits = []
        for name, smarts in ZN_CHELATOR_PATTERNS.items():
            patt = Chem.MolFromSmarts(smarts)
            if patt is not None and mol.HasSubstructMatch(patt):
                hits.append(name)
        return hits, bool(hits)
    except Exception:
        return [], False


def bbb_predict(mol):
    """Simple BBB pass heuristic (Ertl + Veber + Lipinski subset).
    Returns (pass_bool, score).
    Reference: CNS MPO heuristic: MW<450, logP 1-5, TPSA<90, HBD<=3.
    """
    try:
        mw = Descriptors.MolWt(mol)
        logp = Descriptors.MolLogP(mol)
        tpsa = Descriptors.TPSA(mol)
        hbd = Descriptors.NumHDonors(mol)
        hba = Descriptors.NumHAcceptors(mol)
        rotb = Descriptors.NumRotatableBonds(mol)
        pass_mw = mw < 500
        pass_logp = 0.5 <= logp <= 5.5
        pass_tpsa = tpsa < 90
        pass_hbd = hbd <= 3
        pass_rotb = rotb <= 10
        passed = all([pass_mw, pass_logp, pass_tpsa, pass_hbd, pass_rotb])
        return passed, {"mw": mw, "logp": logp, "tpsa": tpsa, "hbd": hbd, "hba": hba, "rotb": rotb}
    except Exception:
        return False, {}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("results_dir", type=Path)
    p.add_argument("--zn-chelator-check", action="store_true", help="Report Zn-chelator motif fraction")
    p.add_argument("--top-n", type=int, default=100, help="Top-N to report Zn-chelator stats on (by PocketXMol cfd_pos)")
    p.add_argument("--output", type=Path, default=None, help="Write analysis CSV to this path")
    args = p.parse_args()

    rd = args.results_dir
    info_csv = rd / "gen_info.csv"
    if not info_csv.exists():
        # fallback: try to find in subdirs
        matches = list(rd.rglob("gen_info.csv"))
        if matches:
            info_csv = matches[0]
        else:
            print(f"ERROR: gen_info.csv not found in {rd}", file=sys.stderr)
            sys.exit(1)

    print(f"[ANALYZE] Reading {info_csv}", file=sys.stderr)
    rows = []
    with open(info_csv) as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    print(f"[ANALYZE] Total rows: {len(rows)}")

    # Validate SMILES + compute QED + BBB + Zn-chelator
    analyzed = []
    n_valid = 0
    for row in rows:
        smi = row.get("smiles", "").strip()
        if not smi:
            continue
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            continue
        n_valid += 1
        qed = QED.default(mol)
        bbb_pass, bbb_props = bbb_predict(mol)
        zn_motifs, is_zn_chelator = classify_zn_chelator(smi)
        cfd_pos = float(row.get("cfd_pos", 0) or 0)
        analyzed.append({
            "smiles": smi,
            "filename": row.get("filename", ""),
            "cfd_pos": cfd_pos,
            "cfd_traj": float(row.get("cfd_traj", 0) or 0),
            "cfd_node": float(row.get("cfd_node", 0) or 0),
            "cfd_edge": float(row.get("cfd_edge", 0) or 0),
            "qed": qed,
            "bbb_pass": bbb_pass,
            "mw": bbb_props.get("mw", 0),
            "logp": bbb_props.get("logp", 0),
            "tpsa": bbb_props.get("tpsa", 0),
            "hbd": bbb_props.get("hbd", 0),
            "zn_motifs": ";".join(zn_motifs),
            "is_zn_chelator": is_zn_chelator,
        })

    # Rank by cfd_pos DESC (higher = more confident pose)
    analyzed.sort(key=lambda r: r["cfd_pos"], reverse=True)

    print(f"[ANALYZE] Valid SMILES: {n_valid}/{len(rows)} ({100*n_valid/max(1,len(rows)):.1f}%)")
    n_bbb = sum(1 for r in analyzed if r["bbb_pass"])
    print(f"[ANALYZE] BBB-pass: {n_bbb}/{n_valid} ({100*n_bbb/max(1,n_valid):.1f}%)")

    top_n = analyzed[: args.top_n]
    if args.zn_chelator_check:
        n_zn_top = sum(1 for r in top_n if r["is_zn_chelator"])
        print(f"[ANALYZE] Zn-chelator motif in top-{args.top_n}: {n_zn_top}/{len(top_n)} "
              f"({100*n_zn_top/max(1,len(top_n)):.1f}%)")
        motif_counts = {}
        for r in top_n:
            for m in r["zn_motifs"].split(";"):
                if m:
                    motif_counts[m] = motif_counts.get(m, 0) + 1
        print(f"[ANALYZE] Motif breakdown in top-{args.top_n}:")
        for m, c in sorted(motif_counts.items(), key=lambda x: -x[1]):
            print(f"  {m}: {c}")

    print("\n[ANALYZE] Top-5 by PocketXMol cfd_pos:")
    for i, r in enumerate(analyzed[:5], 1):
        zn_flag = "Zn-CHELATOR" if r["is_zn_chelator"] else "no-zn"
        motifs = r["zn_motifs"] if r["zn_motifs"] else "none"
        print(f"  #{i}  cfd_pos={r['cfd_pos']:.3f}  QED={r['qed']:.3f}  BBB={'Y' if r['bbb_pass'] else 'N'}  "
              f"MW={r['mw']:.0f}  logP={r['logp']:.2f}  [{zn_flag}] motifs={motifs}")
        print(f"       SMILES: {r['smiles']}")

    if args.output:
        with open(args.output, "w", newline="") as f:
            if analyzed:
                writer = csv.DictWriter(f, fieldnames=list(analyzed[0].keys()))
                writer.writeheader()
                for r in analyzed:
                    writer.writerow(r)
        print(f"[ANALYZE] Wrote {len(analyzed)} rows to {args.output}")


if __name__ == "__main__":
    main()

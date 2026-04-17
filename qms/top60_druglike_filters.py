#!/usr/bin/env python3
"""
3 orthogonal drug-quality filters on 60 top leads across 3 therapeutic arms.
  Filter 1: PAINS (RDKit FilterCatalog, PAINS-A/B/C severity)
  Filter 2: SA-score (Ertl 2009 via rdkit.Contrib.SA_Score.sascorer)
  Filter 3: IP-novelty via Tanimoto ECFP4 vs curated drug library

Composite wet_lab_ready score (max 9):
  + 3  PAINS-free
  + 2  SA <= 5
  + 2  max Tanimoto < 0.4
  + 1  BBB-pass (from original data where available)
  + 1  QED >= 0.5
"""
from __future__ import annotations
import os
import sys
import json
from pathlib import Path
from collections import defaultdict

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, DataStructs, QED
from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams

RDLogger.DisableLog("rdApp.*")

# ---------- paths ----------
LIMK2_CSV = "/home/bryza/fleet-results/limk2_activator_alphaC/boltz2_kinase_panel.csv"
ROCK2_TSV = "/home/bryza/fleet-results/rock2_activator_alphaC/boltz2_rescore_ranked.tsv"
ROCK2_BBB = "/home/bryza/fleet-results/rock2_activator_alphaC/bbb_filtered.csv"
MDM2_CSV  = "/home/bryza/fleet-results/mdm2_activator_v2_allosteric/top100_by_cfd_pos.csv"
CHEMBL_PARQUET = "/home/bryza/fleet-results/chembl_ki/kinase_ki.parquet"

OUT_DIR = Path("/home/bryza/sma-research/qms")
OUT_MD = OUT_DIR / "top60_druglike_filters_RESULTS.md"
OUT_JSON = OUT_DIR / "top60_druglike_filters_RESULTS.json"

import rdkit
SASCORER_DIR = os.path.join(os.path.dirname(rdkit.__file__), "Contrib", "SA_Score")
sys.path.insert(0, SASCORER_DIR)
import sascorer  # type: ignore  # noqa: E402


# ---------- known MDM2 inhibitors (literature, curated) ----------
KNOWN_MDM2_INHIBITORS = {
    "Nutlin-3a":    "Cc1ccc(C(=O)N2CCN(C(=O)N3C(c4ccc(Cl)cc4)(c4ccc(Cl)cc4)C(c4cc5cc(OC(C)C)ccc5[nH]4)=N3)CC2)cc1",
    "Idasanutlin":  "COc1cc(C2=NC3(CCC3)C(=O)N2c2ccc(F)cc2)cc(OC)c1OC",
    "AMG-232":      "CC1(COC(=O)C(=CC1=O)c1cc2ccc(Cl)cc2n1C)C",
    "APG-115":      "O=C1N(c2ccc(F)cc2)C2(CCC2)CC12c1ccc(Cl)cc1-c1ccc(Cl)cc12",
    "Milademetan":  "CC1=NC(c2ccccc2Cl)=NN1C1(C(=O)O)CC2(CCC2)C1c1ccc(F)cc1",
    "RG-7388":      "COc1cc(C2=NC3(CCC3)C(=O)N2c2ccc(F)cc2)cc(F)c1OC",
    "SAR405838":    "CC(C)(C)NC(=O)C1C2CC(c3ccc(Cl)cc3)C(c3ccc(Cl)cc3)C2(c2ccc(F)cc2)N1",
    "MI-77301":     "CC(C)(C)OC(=O)N1C(C(=O)NC2CCC2)C2CC(c3ccc(Cl)cc3)C(c3ccc(Cl)cc3)C12",
    "SJ-172550":    "O=C(O)c1ccc(N(c2ccccc2)c2nc(-c3ccc(Cl)cc3)[nH]n2)cc1",
    "MK-8242":      "CC(C)(C)c1cc(C(=O)N2CCN(c3ncccn3)CC2)cc(C(F)(F)F)c1",
    "NVP-CGM097":   "COc1cc2c(cc1OC)C(c1cc(Cl)ccc1OC)(c1cccc(C(=O)N3CCC(C)(C)CC3)c1)N(C)C2=O",
    "HDM201":       "CC1(C)CC(C(=O)O)c2cc(-c3ccc(F)cc3)n(-c3ccc(Cl)cc3)c2C1",
}

# ---------- known LIMK / ROCK inhibitors (supplement to ChEMBL) ----------
KNOWN_LIMK_ROCK = {
    "LIMKi3":      "CC(=O)Nc1ccc(-c2ncccc2-c2ccc(NC(C)=O)cc2)cc1",
    "LX-7101":     "CC1=NN(c2ncnc3[nH]cc(-c4cccc(F)c4)c23)C(=O)C1",
    "BMS-5":       "COc1ccc(-c2cc(C(=O)Nc3ccc(C(F)(F)F)cn3)ccn2)cc1",
    "Fasudil":     "O=S(=O)(N1CCCNCC1)c1cccc2cnccc12",
    "Y-27632":     "CC(N)C1CCC(C(=O)Nc2ccnc(N)c2)CC1",
    "H-1152":      "CC1C(C(=O)N)N1S(=O)(=O)c1cccc2cnccc12",
    "Belumosudil": "CCc1nc(Nc2ccc(C(=O)NC3CCCCC3)cc2)c2ccccc2n1",
    "AT13148":     "CCC(N)c1cnc(-c2ccc(Cl)cc2)c(C(N)=O)c1",
    "GSK269962A":  "CCN(CC)CCOc1ccc2[nH]c(-c3ccnc(Nc4ccc(N5CCN(C)CC5)cc4)n3)nc2c1",
    "Staurosporine":"CN[C@@H]1C[C@@H]2O[C@@](C)([C@@H]1OC)n1c3ccccc3c3c4c(c5c6ccccc6[nH]c5c31)CNC4=O",
}


def canonicalize(smi: str):
    if not smi or not isinstance(smi, str):
        return None
    try:
        m = Chem.MolFromSmiles(smi)
        if m is None:
            return None
        return Chem.MolToSmiles(m)
    except Exception:
        return None


def ecfp4(mol, n_bits: int = 2048):
    return AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=n_bits)


def load_limk2_top20() -> pd.DataFrame:
    df = pd.read_csv(LIMK2_CSV)
    # score: z_LIMK2 (prefer-target) and selectivity_z (off-target margin)
    df["combined"] = df["z_LIMK2"].fillna(-10) + df["selectivity_z"].fillna(-10)
    df = df.sort_values("combined", ascending=False).head(20).reset_index(drop=True)
    df["arm"] = "LIMK2_activator"
    df["src_rank"] = range(1, len(df) + 1)
    # BBB pass? pull from bbb_filtered.csv
    bbb = pd.read_csv("/home/bryza/fleet-results/limk2_activator_alphaC/bbb_filtered.csv")
    bbb_keys = set(bbb["canonical_smiles"].dropna().tolist())
    df["bbb_pass"] = df["canonical_smiles"].isin(bbb_keys)
    # QED — compute here
    df["qed"] = df["canonical_smiles"].apply(
        lambda s: QED.qed(Chem.MolFromSmiles(s)) if canonicalize(s) else float("nan"))
    df["smiles"] = df["canonical_smiles"]
    return df[["arm", "src_rank", "smiles", "filename", "z_LIMK2",
               "selectivity_z", "bbb_pass", "qed"]].copy()


def load_rock2_top20() -> pd.DataFrame:
    df = pd.read_csv(ROCK2_TSV, sep="\t")
    df = df.sort_values("iptm", ascending=False).head(20).reset_index(drop=True)
    df["arm"] = "ROCK2_activator"
    df["src_rank"] = range(1, len(df) + 1)
    # BBB pass from bbb_filtered.csv if present
    bbb_pass_map = {}
    try:
        bbb = pd.read_csv(ROCK2_BBB)
        if "canonical_smiles" in bbb.columns:
            bbb_pass_map = {s: True for s in bbb["canonical_smiles"].dropna()}
    except Exception:
        pass
    df["bbb_pass"] = df["smiles"].apply(lambda s: canonicalize(s) in bbb_pass_map) \
        if bbb_pass_map else False
    # QED — use provided if present, else compute
    if "qed" not in df.columns or df["qed"].isna().all():
        df["qed"] = df["smiles"].apply(
            lambda s: QED.qed(Chem.MolFromSmiles(s)) if canonicalize(s) else float("nan"))
    df["z_LIMK2"] = float("nan")
    df["selectivity_z"] = float("nan")
    return df[["arm", "src_rank", "smiles", "filename", "iptm",
               "bbb_pass", "qed"]].copy()


def load_mdm2_top20() -> pd.DataFrame:
    df = pd.read_csv(MDM2_CSV)
    df = df.sort_values("cfd_pos", ascending=False).head(20).reset_index(drop=True)
    df["arm"] = "MDM2_activator_v2"
    df["src_rank"] = range(1, len(df) + 1)
    # bbb_prob -> bbb_pass at 0.5 threshold
    df["bbb_pass"] = df["bbb_prob"].fillna(0) >= 0.5
    return df[["arm", "src_rank", "smiles", "filename", "cfd_pos",
               "bbb_pass", "qed"]].copy()


# ---------- filters ----------
def pains_classify(mol):
    """Return {'pains_free': bool, 'severity': 'free'|'A'|'B'|'C', 'match_desc': str}"""
    results = {}
    for tag, cat_enum in [
        ("A", FilterCatalogParams.FilterCatalogs.PAINS_A),
        ("B", FilterCatalogParams.FilterCatalogs.PAINS_B),
        ("C", FilterCatalogParams.FilterCatalogs.PAINS_C),
    ]:
        params = FilterCatalogParams()
        params.AddCatalog(cat_enum)
        fc = FilterCatalog(params)
        entry = fc.GetFirstMatch(mol)
        results[tag] = entry.GetDescription() if entry is not None else None
    if results["A"]:
        return {"pains_free": False, "severity": "A", "match_desc": results["A"]}
    if results["B"]:
        return {"pains_free": False, "severity": "B", "match_desc": results["B"]}
    if results["C"]:
        return {"pains_free": False, "severity": "C", "match_desc": results["C"]}
    return {"pains_free": True, "severity": "free", "match_desc": ""}


def sa_score(mol) -> float:
    try:
        return float(sascorer.calculateScore(mol))
    except Exception:
        return float("nan")


# ---------- reference drug library (Tanimoto IP-novelty) ----------
def build_reference_library() -> dict:
    """Returns dict: name -> (smi, fp)."""
    ref = {}
    # Known MDM2 + LIMK/ROCK inhibitors (literature)
    for name, smi in {**KNOWN_MDM2_INHIBITORS, **KNOWN_LIMK_ROCK}.items():
        c = canonicalize(smi)
        if c is None:
            continue
        mol = Chem.MolFromSmiles(c)
        ref[f"lit::{name}"] = (c, ecfp4(mol))

    # ChEMBL kinase Ki library (potent kinase compounds)
    # Filter: pchembl_value >= 6 (IC50 <= 1 uM) OR standard_value_nm <= 10000 (<= 10 uM)
    try:
        df = pd.read_parquet(CHEMBL_PARQUET)
        df["pchembl_value"] = pd.to_numeric(df["pchembl_value"], errors="coerce")
        df["standard_value_nm"] = pd.to_numeric(df["standard_value_nm"], errors="coerce")
        potent = df[(df["pchembl_value"] >= 6) |
                    (df["standard_value_nm"] <= 10000)].copy()
        potent = potent.drop_duplicates("canonical_smiles")
        potent = potent.sort_values("pchembl_value", ascending=False).head(5000)
        count = 0
        for _, row in potent.iterrows():
            c = canonicalize(row["canonical_smiles"])
            if c is None:
                continue
            mol = Chem.MolFromSmiles(c)
            ref[f"chembl::{row['target_name']}::{row['molecule_chembl_id']}"] = (c, ecfp4(mol))
            count += 1
        print(f"  ChEMBL kinase reference loaded: {count} potent compounds")
    except Exception as e:
        print(f"  ChEMBL load failed: {e}")
    return ref


def max_tanimoto_vs_ref(fp, ref_library) -> tuple:
    best = 0.0
    best_name = ""
    for name, (_, ref_fp) in ref_library.items():
        t = DataStructs.TanimotoSimilarity(fp, ref_fp)
        if t > best:
            best = t
            best_name = name
    return best, best_name


# ---------- main ----------
def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("[1/5] Loading 60 compounds across 3 arms...")
    limk2 = load_limk2_top20()
    rock2 = load_rock2_top20()
    mdm2  = load_mdm2_top20()
    print(f"  LIMK2: {len(limk2)}  ROCK2: {len(rock2)}  MDM2: {len(mdm2)}")

    all_rows = []
    for df in (limk2, rock2, mdm2):
        for _, r in df.iterrows():
            smi = r.get("smiles")
            canonical = canonicalize(smi)
            if canonical is None:
                continue
            mol = Chem.MolFromSmiles(canonical)
            if mol is None:
                continue
            all_rows.append({
                "arm": r["arm"],
                "src_rank": int(r["src_rank"]),
                "smiles": canonical,
                "filename": r.get("filename", ""),
                "qed": float(r.get("qed", float("nan")) or float("nan")),
                "bbb_pass": bool(r.get("bbb_pass", False)),
                "z_LIMK2": float(r.get("z_LIMK2", float("nan")) or float("nan"))
                    if "z_LIMK2" in r else float("nan"),
                "selectivity_z": float(r.get("selectivity_z", float("nan")) or float("nan"))
                    if "selectivity_z" in r else float("nan"),
                "iptm": float(r.get("iptm", float("nan")) or float("nan"))
                    if "iptm" in r else float("nan"),
                "cfd_pos": float(r.get("cfd_pos", float("nan")) or float("nan"))
                    if "cfd_pos" in r else float("nan"),
                "mol": mol,
            })

    print(f"  Valid canonicalizable compounds: {len(all_rows)}")

    print("[2/5] Filter 1: PAINS classification...")
    for r in all_rows:
        p = pains_classify(r["mol"])
        r["pains_free"] = p["pains_free"]
        r["pains_severity"] = p["severity"]
        r["pains_match_desc"] = p["match_desc"]

    print("[3/5] Filter 2: Synthetic Accessibility (SA-score)...")
    for r in all_rows:
        r["sa_score"] = sa_score(r["mol"])

    print("[4/5] Filter 3: IP-novelty (Tanimoto ECFP4 vs drug library)...")
    ref_lib = build_reference_library()
    print(f"  Reference library size: {len(ref_lib)}")
    for r in all_rows:
        fp = ecfp4(r["mol"])
        t, name = max_tanimoto_vs_ref(fp, ref_lib)
        r["max_tanimoto"] = t
        r["nearest_ref"] = name

    print("[5/5] Composite wet-lab-ready score...")
    for r in all_rows:
        score = 0
        if r["pains_free"]:
            score += 3
        if r["sa_score"] == r["sa_score"] and r["sa_score"] <= 5:
            score += 2
        if r["max_tanimoto"] < 0.4:
            score += 2
        if r["bbb_pass"]:
            score += 1
        if (r["qed"] == r["qed"]) and r["qed"] >= 0.5:
            score += 1
        r["wet_lab_ready"] = score

    # ---------- output ----------
    rows_clean = []
    for r in all_rows:
        rc = {k: v for k, v in r.items() if k != "mol"}
        rows_clean.append(rc)

    with open(OUT_JSON, "w") as f:
        json.dump({"rows": rows_clean,
                   "reference_library_size": len(ref_lib)}, f, indent=2, default=str)

    md = []
    md.append("# Top-60 Drug-Quality Filter Results")
    md.append("")
    md.append("**Status:** DRAFT — triple_llm_verify pending, no external comms")
    md.append("**Date:** 2026-04-17")
    md.append("")
    md.append("## Method")
    md.append("- **Input:** 60 compounds (20 per arm, 3 small-molecule arms)")
    md.append("  - LIMK2-alphaC activator: top 20 by (z_LIMK2 + selectivity_z) from boltz2_kinase_panel.csv")
    md.append("  - ROCK2-alphaC activator: top 20 by Boltz-2 iptm")
    md.append("  - MDM2 activator v2 allosteric: top 20 by cfd_pos")
    md.append("- **Filter 1:** RDKit PAINS (PAINS-A/B/C severity)")
    md.append("- **Filter 2:** SA-score (Ertl 2009, RDKit Contrib/SA_Score/sascorer.py)")
    md.append("- **Filter 3:** IP-novelty — max Tanimoto ECFP4 (r=2, 2048 bits) vs")
    md.append(f"  {len(ref_lib)}-compound reference library (ChEMBL potent kinase inhibitors pchembl>=6 or <=10uM + curated MDM2/LIMK/ROCK literature drugs)")
    md.append("- **Composite:** PAINS-free (+3) + SA<=5 (+2) + Tanimoto<0.4 (+2) + BBB-pass (+1) + QED>=0.5 (+1); max 9")
    md.append("")

    md.append("## Summary (per arm)")
    md.append("")
    md.append("| Arm | n | PAINS-free | SA<=5 | Tanimoto<0.4 | BBB-pass | QED>=0.5 | Wet-lab-ready (>=7) | Mean score |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    summary = {}
    for arm in ["LIMK2_activator", "ROCK2_activator", "MDM2_activator_v2"]:
        sub = [r for r in all_rows if r["arm"] == arm]
        s = {
            "n": len(sub),
            "pains_free": sum(1 for r in sub if r["pains_free"]),
            "sa_le5":     sum(1 for r in sub if r["sa_score"] == r["sa_score"] and r["sa_score"] <= 5),
            "novel":      sum(1 for r in sub if r["max_tanimoto"] < 0.4),
            "bbb_pass":   sum(1 for r in sub if r["bbb_pass"]),
            "qed_ge05":   sum(1 for r in sub if (r["qed"] == r["qed"]) and r["qed"] >= 0.5),
            "wet_lab_ready_ge7": sum(1 for r in sub if r["wet_lab_ready"] >= 7),
            "mean_score": (sum(r["wet_lab_ready"] for r in sub) / len(sub)) if sub else 0.0,
        }
        summary[arm] = s
        md.append(f"| {arm} | {s['n']} | {s['pains_free']} | {s['sa_le5']} | {s['novel']} | "
                  f"{s['bbb_pass']} | {s['qed_ge05']} | {s['wet_lab_ready_ge7']} | {s['mean_score']:.2f} |")

    md.append("")
    md.append("**Composite wet-lab-ready distribution (all 60):**")
    md.append("")
    dist = defaultdict(int)
    for r in all_rows:
        dist[r["wet_lab_ready"]] += 1
    md.append("| Score | Count |")
    md.append("|---|---|")
    for k in sorted(dist.keys(), reverse=True):
        md.append(f"| {k} | {dist[k]} |")
    md.append("")

    for arm in ["LIMK2_activator", "ROCK2_activator", "MDM2_activator_v2"]:
        sub = [r for r in all_rows if r["arm"] == arm]
        sub_sorted = sorted(sub, key=lambda r: (-r["wet_lab_ready"],
                                                r.get("sa_score", 10) or 10,
                                                r.get("max_tanimoto", 1.0)))
        md.append(f"## Top 5 wet-lab-ready — {arm}")
        md.append("")
        md.append("| Rank | Score | SMILES | PAINS | SA | max_Tanimoto | nearest_ref | BBB | QED | src_rank |")
        md.append("|---|---|---|---|---|---|---|---|---|---|")
        for i, r in enumerate(sub_sorted[:5], start=1):
            md.append(
                f"| {i} | **{r['wet_lab_ready']}/9** | `{r['smiles']}` | "
                f"{r['pains_severity']} | {r['sa_score']:.2f} | "
                f"{r['max_tanimoto']:.3f} | {r['nearest_ref']} | "
                f"{'YES' if r['bbb_pass'] else 'no'} | "
                f"{r['qed']:.3f} | {r['src_rank']} |"
            )
        md.append("")
        md.append(f"### Rationale — {arm}")
        md.append("")
        for i, r in enumerate(sub_sorted[:5], start=1):
            reasons = []
            if r["pains_free"]:
                reasons.append("PAINS-free")
            else:
                reasons.append(f"PAINS-{r['pains_severity']}: {r['pains_match_desc']}")
            reasons.append(f"SA={r['sa_score']:.2f}" +
                           (" (tractable)" if r['sa_score'] <= 5 else " (HARD)"))
            reasons.append(f"Tanimoto={r['max_tanimoto']:.3f} vs {r['nearest_ref']}" +
                           (" (novel chemotype)" if r['max_tanimoto'] < 0.4 else " (related to known drug)"))
            md.append(f"- **#{i}** (src_rank {r['src_rank']}): " + "; ".join(reasons))
        md.append("")

    md.append("## Flagged compounds")
    md.append("")
    pains_A = [r for r in all_rows if r["pains_severity"] == "A"]
    if pains_A:
        md.append(f"### PAINS-A severity ({len(pains_A)}) — remove from consideration")
        md.append("")
        md.append("| Arm | src_rank | SMILES | Match |")
        md.append("|---|---|---|---|")
        for r in pains_A:
            md.append(f"| {r['arm']} | {r['src_rank']} | `{r['smiles']}` | {r['pains_match_desc']} |")
        md.append("")
    else:
        md.append("- No PAINS-A hits.")
        md.append("")

    hard_sa = [r for r in all_rows if r["sa_score"] == r["sa_score"] and r["sa_score"] > 5]
    if hard_sa:
        md.append(f"### High SA-score (> 5) — synthesis-expert review needed ({len(hard_sa)})")
        md.append("")
        md.append("| Arm | src_rank | SA | SMILES |")
        md.append("|---|---|---|---|")
        for r in sorted(hard_sa, key=lambda x: -x["sa_score"]):
            md.append(f"| {r['arm']} | {r['src_rank']} | {r['sa_score']:.2f} | `{r['smiles']}` |")
        md.append("")

    near_dup = [r for r in all_rows if r["max_tanimoto"] >= 0.4]
    if near_dup:
        md.append(f"### Near-duplicate to known drug (Tanimoto >= 0.4) — patent risk ({len(near_dup)})")
        md.append("")
        md.append("| Arm | src_rank | Tanimoto | nearest_ref | SMILES |")
        md.append("|---|---|---|---|---|")
        for r in sorted(near_dup, key=lambda x: -x["max_tanimoto"]):
            md.append(f"| {r['arm']} | {r['src_rank']} | {r['max_tanimoto']:.3f} | "
                      f"{r['nearest_ref']} | `{r['smiles']}` |")
        md.append("")

    md.append("## Triple-LLM verification")
    md.append("")
    md.append("- Status: DRAFT pending triple_llm_verify 3/3")
    md.append("- All compounds canonicalized via RDKit (MolToSmiles). PAINS/SA/Tanimoto math reproducible.")
    md.append("- No external comms (Simon, Torsten) until review complete.")
    md.append("")

    OUT_MD.write_text("\n".join(md))
    print(f"\nWritten: {OUT_MD}")
    print(f"Written: {OUT_JSON}")

    print("\n--- Summary ---")
    for arm, s in summary.items():
        print(f"{arm}: n={s['n']} PAINS-free={s['pains_free']} "
              f"SA<=5={s['sa_le5']} novel={s['novel']} "
              f"wet-lab-ready>=7={s['wet_lab_ready_ge7']} mean={s['mean_score']:.2f}")
    print("Composite distribution:")
    for k in sorted(dist.keys(), reverse=True):
        print(f"  {k}: {dist[k]}")


if __name__ == "__main__":
    main()

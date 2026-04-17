#!/usr/bin/env python3
"""Batch SMA-Score + RAscore + CNS-MPO re-scoring of all active PocketXMol/GenMol libraries.

Created 2026-04-17 in response to LIMK2 αC retraction (pipeline-stack audit).

For each campaign dir under /home/bryza/fleet-results/ matching the known patterns:
  1. Load compounds from pxm_smiles_master.csv / pxm_smiles_raw.csv / gen_info.csv
  2. Train SMA-Score GradientBoosting model (15 POS + ChEMBL NEG from sma_score_ranker)
  3. Compute RAscore (SAScore-normalised), CNS-MPO (Wager 4-param), BBB votes
  4. Write sma_rescore.tsv alongside each library
  5. Compare against prior top-20 iptm (if boltz2 selectivity tsv present)
  6. Flag campaigns where SMA-Score top-20 is DISJOINT from iptm top-20
"""
import csv, json, sys
from pathlib import Path
import numpy as np
import pandas as pd

from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, Crippen, QED, DataStructs, RDConfig
import os as _os
sys.path.append(_os.path.join(RDConfig.RDContribDir, "SA_Score"))
import sascorer  # noqa

from sklearn.ensemble import GradientBoostingClassifier

# ---- copy POSITIVES from sma_score_ranker.py for fidelity ----
POSITIVES = {
    "fasudil":       "COc1ccc2c(c1)sc1cc(O)ccc21",
    "y27632":        "c1cc(ccn1)C(=O)Nc1ccc(C)cc1",
    "ripasudil":     "CN(C)S(=O)(=O)c1ccccc1O",
    "limki3":        "COc1cc(-c2ncc3ccccc3n2)ccc1O",
    "bms5":          "Cc1ccc(-c2cc(NC(=O)c3ccc(F)cc3)nc(N)n2)cc1",
    "bbb5":          "CC(=O)Nc1ccc(-c2ccccc2)cc1",
    "belumosudil":   "CC(C)Nc1ncc(-c2cc(F)ccc2N)s1",
    "netarsudil":    "CCOC(=O)C(c1ccncc1)N(CCc1cccnc1)c1ccccc1",
    "risdiplam":     "CC(C)(C)c1ccc(N2CCC(c3nnc(N4CCOCC4)n3C)CC2)c(OC)c1",
    "riluzole":      "NC1=NC2=CC(OC(F)(F)F)=CC=C2S1",
    "edaravone":     "CC1=NN(C(=O)C1)c1ccccc1",
    "4ap":           "NC1=CC=NC=C1",
    "34_dap":        "Nc1ccncc1N",
    "pyridostigmine":"CN(C)C(=O)Oc1ccc[n+](C)c1",
    "neostigmine":   "CN(C)C(=O)Oc1cccc([N+](C)(C)C)c1",
}
POS_MOLS = {n: Chem.MolFromSmiles(s) for n, s in POSITIVES.items()}
POS_FPS = {n: AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=1024)
           for n, m in POS_MOLS.items() if m is not None}

RES_DIR = Path("/home/bryza/fleet-results")
OUT_BASE = RES_DIR  # sma_rescore.tsv goes next to original

CAMPAIGN_GLOBS = [
    "limk2_*", "rock2_*", "perp_*", "mdm2_*", "cfl1_*",
    "musk_*", "cdk5_*", "hdac2_*", "mtor_*", "jak2_*",
    "dusp*", "nrf2_keap1_*", "bruno_celf_*",
]

def _mol(smi):
    return Chem.MolFromSmiles(smi) if smi else None

def _fp(m, n_bits=1024):
    return AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=n_bits) if m else None

def _desc(m):
    if m is None: return [0.0]*11
    return [
        Descriptors.MolWt(m), Descriptors.MolLogP(m),
        Descriptors.NumHAcceptors(m), Descriptors.NumHDonors(m),
        Descriptors.TPSA(m), Descriptors.NumRotatableBonds(m),
        Descriptors.NumAromaticRings(m), Descriptors.HeavyAtomCount(m),
        Descriptors.FractionCSP3(m), Descriptors.NumAliphaticRings(m),
        Descriptors.RingCount(m),
    ]

DESC_COLS = ["mw","logp","hba","hbd","tpsa","rotb","naro","heavy","fcsp3","naliph","ringc"]

def _tani_features(m):
    if m is None: return [0.0, 0.0]
    fp = _fp(m)
    sims = [DataStructs.TanimotoSimilarity(fp, pfp) for pfp in POS_FPS.values()]
    return [max(sims), sum(sims)/len(sims)]

def featurize(smiles_list):
    rows = []
    for smi in smiles_list:
        m = _mol(smi)
        rows.append(_desc(m) + _tani_features(m))
    return pd.DataFrame(rows, columns=DESC_COLS + ["pos_tani_max","pos_tani_mean"])

def wager_cns_mpo_v2(mw, logp, tpsa, hbd):
    def ramp(x, lg, hb):
        if x <= lg: return 1.0
        if x >= hb: return 0.0
        return 1.0 - (x - lg) / (hb - lg)
    def peak(x, pl, ph, ol, oh):
        if pl <= x <= ph: return 1.0
        if x < ol or x > oh: return 0.0
        if x < pl: return (x - ol) / (pl - ol)
        return (oh - x) / (oh - ph)
    return round(ramp(mw,360,500) + ramp(logp,3,5) + peak(tpsa,40,90,20,120) + ramp(hbd,0.5,3.5), 3)

def ra_score_from_sa(sa):
    # Normalize SAScore (1 easy, 10 hard) -> RAscore (0 hard, 1 easy)
    return round(max(0.0, min(1.0, 1.0 - (sa - 1.0) / 9.0)), 3)

# ---- train model once ----
chembl_file = Path("/home/bryza/fleet-results/chembl_ki/kinase_ki.parquet")
if chembl_file.exists():
    cdf = pd.read_parquet(chembl_file)
    pos_set = set(POSITIVES.values())
    neg_smi = cdf[~cdf["canonical_smiles"].isin(pos_set)]["canonical_smiles"].dropna().unique()
    # Use only 50 negatives so model doesn't degenerate to "exact-match" classifier —
    # 15 POS vs 500 NEG caused sma_score ≈ 2.5e-9 for all novel compounds
    if len(neg_smi) > 50:
        rng = np.random.default_rng(42)
        neg_smi = rng.choice(neg_smi, 50, replace=False).tolist()
    else:
        neg_smi = list(neg_smi)
    print(f"[rescore] ChEMBL negatives: {len(neg_smi)}")
else:
    print("[rescore] ChEMBL not yet ingested — using fallback negatives")
    neg_smi = [
        "CC(=O)Oc1ccccc1C(=O)O","CC(C)NCC(O)COc1ccc(CCOCC2CC2)cc1",
        "CC(=O)NCCc1ccc(O)cc1","CC(C)Cc1ccc(C(C)C(=O)O)cc1",
        "OC(=O)Cc1ccc(Cl)c(Cl)c1","CC(C)(C)NCC(O)c1cc(Cl)c(N)c(Cl)c1",
        "O=C(O)c1ccccc1O","CCOC(=O)c1ccccc1",
        "CN(C)CCCC1(c2ccc(cc2)CC(=O)N)c2ccccc2OC1",
        "Cc1ccc(-c2ccc(NS(=O)(=O)c3ccc(C(F)(F)F)cc3)cc2)nn1",
    ]

pos_smi_list = list(POSITIVES.values())
y = np.array([1]*len(pos_smi_list) + [0]*len(neg_smi))
X_train = featurize(pos_smi_list + neg_smi)
clf = GradientBoostingClassifier(n_estimators=200, max_depth=3, random_state=42)
clf.fit(X_train, y)
print(f"[rescore] model trained on {len(pos_smi_list)} POS + {len(neg_smi)} NEG")

# ---- discover campaigns ----
dirs = []
for glob_pat in CAMPAIGN_GLOBS:
    dirs.extend(RES_DIR.glob(glob_pat))
atlas = RES_DIR / "atlas_top5_pxm"
if atlas.exists():
    for sub in atlas.iterdir():
        if sub.is_dir(): dirs.append(sub)

# Campaigns to skip (not real libraries)
skip = {"perp_panel_throttled.log"}
dirs = [d for d in dirs if d.is_dir() and d.name not in skip]
print(f"[rescore] {len(dirs)} candidate campaign dirs")

def load_smiles(d: Path):
    """Return list of (smiles, qed_or_proxy) tuples from whatever format is present."""
    for fname in ("pxm_smiles_master.csv", "pxm_smiles_raw.csv"):
        f = d / fname
        if f.exists():
            out = []
            try:
                with f.open() as fh:
                    for row in csv.DictReader(fh):
                        smi = row.get("smiles") or row.get("canonical_smiles")
                        if not smi: continue
                        try: qed = float(row.get("qed", 0) or 0)
                        except: qed = 0.0
                        out.append((smi, qed))
                if out: return out, fname
            except Exception as e:
                print(f"  error {f}: {e}")
    f = d / "gen_info.csv"
    if f.exists():
        out = []
        try:
            with f.open() as fh:
                for row in csv.DictReader(fh):
                    smi = row.get("smiles")
                    if not smi or row.get("tag") == "bad": continue
                    try:
                        cfd = float(row.get("cfd_pos", 3.0) or 3.0)
                        qed = max(0.0, min(1.0, 1.0 - (cfd - 2.0)/2.0))
                    except: qed = 0.5
                    out.append((smi, qed))
            if out: return out, "gen_info.csv"
        except Exception as e:
            print(f"  error {f}: {e}")
    # GenMol aggregated libraries — also scan nested libraries/aggregated/
    candidate_files = []
    for fname in ("all_genmol_dedup.csv", "master_top200.csv", "combined_library.smi",
                  "genmol_results.json", "valid_smiles.csv", "top100.csv",
                  "master_library_combined.csv"):
        candidate_files.append(d / fname)
    for nested in ("libraries/aggregated", "library", "scoring"):
        for fname in ("master_library_combined.csv", "all_genmol_dedup.csv",
                      "master_top200.csv", "combined_library.smi"):
            candidate_files.append(d / nested / fname)
    for f in candidate_files:
        fname = f.name
        if f.exists():
            out = []
            try:
                if fname.endswith(".smi"):
                    for line in f.open():
                        smi = line.strip().split()[0] if line.strip() else ""
                        if smi: out.append((smi, 0.5))
                elif fname.endswith(".json"):
                    data = json.loads(f.read_text())
                    chunks = data if isinstance(data, list) else [data]
                    for c in chunks:
                        res = c.get("result", c) or {}
                        mols = res.get("molecules", [])
                        if isinstance(mols, str):
                            try: mols = json.loads(mols)
                            except: mols = []
                        for m in mols:
                            if isinstance(m, dict):
                                smi = m.get("smiles") or m.get("sample")
                                if smi: out.append((smi, m.get("score", 0) or 0))
                else:
                    with f.open() as fh:
                        for row in csv.DictReader(fh):
                            smi = row.get("smiles") or row.get("canonical_smiles")
                            if not smi: continue
                            try: qed = float(row.get("qed", 0) or 0)
                            except: qed = 0.0
                            out.append((smi, qed))
                if out: return out, fname
            except Exception as e:
                print(f"  error {f}: {e}")
    return [], None

def load_iptm_top(d: Path, n=20):
    """Try to find an existing iptm-based top-K to compare against."""
    for fname in ("top_hits.tsv", "top_hits_affinity_v2.tsv", "top10_selectivity.tsv",
                  "boltz2_rescore_ranked.tsv"):
        f = d / fname
        if f.exists():
            try:
                df = pd.read_csv(f, sep="\t")
                if "smiles" in df.columns:
                    return df["smiles"].head(n).tolist(), fname
            except Exception as e:
                pass
    return None, None

# ---- main loop ----
results_summary = []
disjoint_alerts = []
for d in sorted(dirs):
    pairs, src = load_smiles(d)
    if not pairs:
        print(f"[skip] {d.relative_to(RES_DIR)} — no SMILES source found")
        continue

    # dedupe
    seen = set(); uniq = []
    for smi, q in pairs:
        if smi in seen: continue
        seen.add(smi); uniq.append((smi, q))
    if not uniq:
        continue

    smiles_list = [p[0] for p in uniq]
    qed_list = [p[1] for p in uniq]

    # SMA-Score
    X_cand = featurize(smiles_list)
    sma_score = clf.predict_proba(X_cand)[:, 1]

    # RAscore + CNS-MPO + classical descriptors
    rows = []
    for (smi, qed_in), sma_s in zip(uniq, sma_score):
        m = _mol(smi)
        if m is None:
            rows.append({"smiles": smi, "sma_score": float(sma_s), "valid": False,
                         "ra_score": 0.0, "cns_mpo": 0.0, "qed": qed_in,
                         "mw": 0, "logp": 0, "tpsa": 0, "hbd": 0, "hba": 0})
            continue
        try: sa = sascorer.calculateScore(m)
        except: sa = 10.0
        mw = Descriptors.MolWt(m); logp = Crippen.MolLogP(m)
        tpsa = Descriptors.TPSA(m); hbd = Descriptors.NumHDonors(m); hba = Descriptors.NumHAcceptors(m)
        qed_v = QED.qed(m)
        mpo = wager_cns_mpo_v2(mw, logp, tpsa, hbd)
        rows.append({
            "smiles": smi, "sma_score": float(sma_s), "valid": True,
            "ra_score": ra_score_from_sa(sa), "sa_score": round(sa, 3),
            "cns_mpo": mpo, "qed_rdkit": round(qed_v, 3), "qed_source": qed_in,
            "mw": round(mw, 1), "logp": round(logp, 2), "tpsa": round(tpsa, 1),
            "hbd": hbd, "hba": hba,
        })

    df = pd.DataFrame(rows)
    # Composite rank = sma_score * (cns_mpo / 4) * ra_score — gives granular ordering
    # within the GB "pass" bucket since GB is binarized to ~2 values.
    df["composite_rank"] = (
        df["sma_score"].clip(lower=1e-6) * df["cns_mpo"].fillna(0) / 4.0 * df["ra_score"].fillna(0)
    )
    df = df.sort_values(["sma_score", "composite_rank"], ascending=[False, False])
    out = d / "sma_rescore.tsv"
    df.to_csv(out, sep="\t", index=False)

    top20_sma = df.head(20)["smiles"].tolist()
    iptm_top, iptm_src = load_iptm_top(d, 20)
    overlap = None; disjoint = None
    # Count compounds that pass SMA-Score gate (nonzero = above ChEMBL-kinase baseline)
    pass_threshold = max(1e-7, df["sma_score"].quantile(0.5))
    n_pass = int((df["sma_score"] > pass_threshold).sum())
    pass_rate = n_pass / max(1, len(df))

    # Flag when almost no compounds pass the SMA-Score gate (i.e. library is
    # biologically off-mission per the 15 positive anchors)
    if pass_rate < 0.01:
        disjoint_alerts.append({
            "campaign": str(d.relative_to(RES_DIR)),
            "severity": "RETRACTION_WARNING",
            "reason": "ZERO_SMA_SCORE_PASS",
            "pass_rate": round(pass_rate, 4),
            "n_pass": n_pass,
            "n_compounds": len(uniq),
            "source_file": src,
            "note": "No compounds cleared the SMA-Score gate — library is "
                    "not SMA-mission-aligned relative to the 15 POS anchors.",
        })

    if iptm_top:
        ov = set(top20_sma) & set(iptm_top)
        overlap = len(ov)
        disjoint = len(iptm_top) - overlap
        # Disjunction = <=25% overlap (≤5 of top-20) when we have enough iptm data to compare
        if overlap <= 5 and len(iptm_top) >= 10:
            severity = "RETRACTION_WARNING" if overlap <= 2 else "REVIEW_NEEDED"
            disjoint_alerts.append({
                "campaign": str(d.relative_to(RES_DIR)),
                "severity": severity,
                "reason": "DISJOINT_TOP20",
                "iptm_source": iptm_src,
                "overlap_top20": overlap,
                "disjoint_count": disjoint,
                "source_file": src,
                "n_compounds": len(uniq),
            })

    results_summary.append({
        "campaign": str(d.relative_to(RES_DIR)),
        "source_file": src,
        "n_compounds": len(uniq),
        "n_valid": int(df["valid"].sum()),
        "top_sma_score": float(df["sma_score"].max()),
        "median_sma": float(df["sma_score"].median()),
        "iptm_source": iptm_src,
        "overlap_top20": overlap,
    })
    print(f"[done] {d.relative_to(RES_DIR)}: {len(uniq)} cpds, top-SMA={df['sma_score'].max():.3f}, "
          f"overlap(iptm↔sma top20)={overlap}")

# ---- write summary ----
summary_df = pd.DataFrame(results_summary)
summary_path = Path("/home/bryza/sma-research/qms/PIPELINE_RESCORE_SUMMARY_2026-04-17.tsv")
summary_df.to_csv(summary_path, sep="\t", index=False)
print(f"\n[summary] {len(summary_df)} campaigns rescored → {summary_path}")

alerts_path = Path("/home/bryza/sma-research/qms/PIPELINE_RESCORE_DISJOINT_ALERTS_2026-04-17.json")
alerts_path.write_text(json.dumps(disjoint_alerts, indent=2))
print(f"[alerts] {len(disjoint_alerts)} disjoint campaigns → {alerts_path}")

# Print disjoint alerts
for a in disjoint_alerts:
    if a.get("reason") == "DISJOINT_TOP20":
        print(f"  [{a['severity']}] {a['campaign']} — only {a['overlap_top20']} of top-20 overlap with iptm")
    else:
        print(f"  [{a['severity']}] {a['campaign']} — {a.get('reason')}: "
              f"{a.get('n_pass', 0)}/{a.get('n_compounds', '?')} compounds pass SMA-Score gate")

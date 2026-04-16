"""SMA-Score ranker v1 — GradientBoosting binary classifier.
POS = ~20 literature-strict SMA-rescue / NMJ-beneficial compounds.
NEG = random kinase inhibitors from ChEMBL without SMA literature link.

Features: RDKit descriptors + Tanimoto to positives.
Output: rank every candidate compound by SMA-relevance probability.
Trains in-memory per run (fast) — no model persistence needed.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, DataStructs
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import GradientBoostingClassifier

OUT_DIR = Path("/home/bryza/fleet-results/sma_score")
OUT_DIR.mkdir(parents=True, exist_ok=True)

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

def _mol(smi):
    return Chem.MolFromSmiles(smi)

def _fp(m, n_bits=1024):
    if m is None: return None
    return AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=n_bits)

POS_MOLS = {n: _mol(s) for n, s in POSITIVES.items()}
POS_FPS = {n: _fp(m) for n, m in POS_MOLS.items() if m is not None}

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
    this_fp = _fp(m)
    sims = [DataStructs.TanimotoSimilarity(this_fp, pfp) for pfp in POS_FPS.values()]
    return [max(sims), sum(sims)/len(sims)]

def featurize(smiles_list):
    rows = []
    for smi in smiles_list:
        m = _mol(smi)
        rows.append(_desc(m) + _tani_features(m))
    return pd.DataFrame(rows, columns=DESC_COLS + ["pos_tani_max","pos_tani_mean"])

# ----------------------------------------------------------------------
# Negatives: ChEMBL if available, else built-in fallback
# ----------------------------------------------------------------------
chembl_file = Path("/home/bryza/fleet-results/chembl_ki/kinase_ki.parquet")
if chembl_file.exists():
    cdf = pd.read_parquet(chembl_file)
    pos_set = set(POSITIVES.values())
    neg_smi = cdf[~cdf["canonical_smiles"].isin(pos_set)]["canonical_smiles"].dropna().unique()
    if len(neg_smi) > 500:
        rng = np.random.default_rng(42)
        neg_smi = rng.choice(neg_smi, 500, replace=False).tolist()
    else:
        neg_smi = list(neg_smi)
    print(f"[ranker] ChEMBL negatives: {len(neg_smi)}")
else:
    print("[ranker] ChEMBL not yet ingested — using 30 drug-like fallback negatives")
    neg_smi = [
        "CC(=O)Oc1ccccc1C(=O)O","CC(C)NCC(O)COc1ccc(CCOCC2CC2)cc1",
        "CC(=O)NCCc1ccc(O)cc1","CC(C)Cc1ccc(C(C)C(=O)O)cc1",
        "OC(=O)Cc1ccc(Cl)c(Cl)c1","CC(C)(C)NCC(O)c1cc(Cl)c(N)c(Cl)c1",
        "O=C(O)c1ccccc1O","CCOC(=O)c1ccccc1",
        "CN(C)CCCC1(c2ccc(cc2)CC(=O)N)c2ccccc2OC1",
        "O=S(=O)(Nc1ccc(N=Nc2ccc(O)c(C(=O)O)c2)cc1)c1ccccc1",
        "Cc1ccc(-c2ccc(NS(=O)(=O)c3ccc(C(F)(F)F)cc3)cc2)nn1",
        "CCOC(=O)[C@@H](N)Cc1ccccc1","OC(C(F)(F)F)C1CCCCC1",
        "Nc1ncnc2c1ncn2C","CCCN1C(=O)c2cc(I)ccc2N(C)C1=O",
        "CCCCCCCCCCCCCCCC(=O)O","OC1CCCCC1O",
        "CN(CCC1)CCC1c1ccc(Cl)cc1","CC(N)Cc1ccccc1",
        "COc1ccc(-c2cccc(C(=O)O)c2)cc1","c1ccc(Nc2ccccc2)cc1",
        "CC(C)Cn1cncn1","CCN(CC)CCN","Nc1ccc(N)cc1",
        "CC1=CC(=NN1)c1ccc(Cl)cc1","O=C1Nc2ccccc2C1=O",
        "COc1cc(C=O)ccc1O","Cc1ccc2nc(N)sc2c1","NC(=O)c1ccccc1",
        "CCCCc1ccncc1",
    ]

# ----------------------------------------------------------------------
# Train
# ----------------------------------------------------------------------
pos_smi_list = list(POSITIVES.values())
y = np.array([1]*len(pos_smi_list) + [0]*len(neg_smi))
X = featurize(pos_smi_list + neg_smi)

print(f"[ranker] training: {len(pos_smi_list)} POS + {len(neg_smi)} NEG, {X.shape[1]} features")

clf = GradientBoostingClassifier(n_estimators=200, max_depth=3, random_state=42)
try:
    cv_scores = cross_val_score(clf, X, y, cv=min(5, len(pos_smi_list)), scoring="roc_auc")
    print(f"[ranker] 5-fold ROC-AUC: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
except Exception as e:
    print(f"[ranker] CV skipped: {e}")

clf.fit(X, y)

imps = sorted(zip(X.columns, clf.feature_importances_), key=lambda r: -r[1])
print("\n[ranker] top features:")
for f, i in imps[:6]: print(f"  {f:15s} {i:.3f}")

# ----------------------------------------------------------------------
# Score GenMol + PocketXMol candidates
# ----------------------------------------------------------------------
candidates = []
res_dir = Path("/home/bryza/fleet-results")
for d in res_dir.glob("genmol_*"):
    f = d / "genmol_results.json"
    if not f.exists(): continue
    try: data = json.loads(f.read_text())
    except: continue
    for chunk in data:
        res = chunk.get("result") or {}
        for mol_d in res.get("molecules", []):
            candidates.append({
                "source": f"genmol:{d.name.replace('genmol_','')}",
                "smiles": mol_d["smiles"],
                "qed": mol_d.get("score", 0),
            })

print(f"\n[ranker] scoring {len(candidates)} GenMol candidates")
if candidates:
    cand_df = pd.DataFrame(candidates)
    cand_df = cand_df.drop_duplicates(subset=["smiles"])
    cand_X = featurize(cand_df["smiles"].tolist())
    cand_df["sma_score"] = clf.predict_proba(cand_X)[:, 1]
    cand_df = cand_df.sort_values("sma_score", ascending=False)
    out = OUT_DIR / "candidates_ranked.csv"
    cand_df.to_csv(out, index=False)
    print(f"[ranker] saved → {out}")
    print("\n[ranker] TOP 15 by SMA-relevance score:")
    print(cand_df.head(15)[["source","qed","sma_score","smiles"]].to_string(index=False))

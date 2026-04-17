#!/usr/bin/env python3
"""
Tanimoto clustering + scaffold analysis + top-20 wet-lab prioritisation.

Inputs produced by build_master_matrix.py:
  compounds_scored.csv     (per canonical SMILES: descriptors + final_score)
  master_matrix_long.csv   (per canonical SMILES x campaign: score)
  per_compound_aggregates.csv
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, DataStructs
from rdkit.Chem.Scaffolds import MurckoScaffold

RDLogger.DisableLog("rdApp.*")

OUT = Path("/home/bryza/sma-research/qms/cross_campaign_synthesis")

# =============================================================================
# Load
# =============================================================================
comp = pd.read_csv(OUT / "compounds_scored.csv")
mm = pd.read_csv(OUT / "master_matrix_long.csv")
agg = pd.read_csv(OUT / "per_compound_aggregates.csv")

# campaigns_hit / targets_hit columns were saved as python-list-str
def _parse_list(s):
    if pd.isna(s): return []
    s = str(s).strip()
    if s.startswith("[") and s.endswith("]"):
        try:
            return [x.strip(" '\"") for x in s[1:-1].split(",") if x.strip()]
        except Exception:
            return []
    return []

comp["campaigns_hit"] = comp["campaigns_hit"].apply(_parse_list)
comp["targets_hit"] = comp["targets_hit"].apply(_parse_list)

# =============================================================================
# Polypharmacology filter
# =============================================================================
poly = comp[comp["n_campaigns"].fillna(0) >= 2].copy()
poly = poly.sort_values(["tier_A_hits", "n_campaigns", "final_score"],
                         ascending=[False, False, False])
poly.to_csv(OUT / "polypharm_hits.csv", index=False)

# exact duplicates (same SMILES appearing in >1 campaign) -> already captured
# near-duplicates (Tanimoto >= 0.85) across campaigns - use ECFP4

# =============================================================================
# Tanimoto matrix -- compute only for reasonable subsets to control RAM:
# - all compounds that hit any tier-A campaign AND pass Lipinski
# =============================================================================
A_CAMPAIGNS = {"rock2_activator_alphaC", "musk_activator_alphaC",
               "perp_pocket3_alphaC", "perp_genmol_hop",
               "smn2_splice_genmol_hop", "agrin_lg3_modulator",
               "dok7_binder", "mdm2_activator"}

mm_tierA = mm[mm["tier"] == "A"]
tierA_smiles = set(mm_tierA["canonical_smiles"].unique())
print(f"[INFO] tier-A compound pool: {len(tierA_smiles)}")

cand = comp[comp["canonical_smiles"].isin(tierA_smiles)].copy()
cand = cand[(cand["Lipinski_pass"] == 1)
            & (cand["has_reactive_group"] == 0)
            & (cand["PAINS_count"] == 0)].copy()
print(f"[INFO] tier-A Lipinski+no-PAINS+no-reactive pool: {len(cand)}")

# ---------- fingerprints ----------
fp_map = {}
for smi in cand["canonical_smiles"]:
    mol = Chem.MolFromSmiles(smi)
    if mol is None: continue
    fp_map[smi] = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)

# =============================================================================
# Butina clustering on Tanimoto distance (0.4 cutoff => ~0.6 similarity)
# =============================================================================
from rdkit.ML.Cluster import Butina

smiles_list = list(fp_map.keys())
fps = [fp_map[s] for s in smiles_list]

dists = []
n = len(fps)
for i in range(1, n):
    sims = DataStructs.BulkTanimotoSimilarity(fps[i], fps[:i])
    dists.extend([1 - x for x in sims])

clusters = Butina.ClusterData(dists, n, 0.4, isDistData=True)
print(f"[INFO] Butina clusters (cutoff 0.4, sim>=0.60): {len(clusters)}")

smi_to_cluster = {}
for cid, mem in enumerate(clusters):
    for idx in mem:
        smi_to_cluster[smiles_list[idx]] = cid

cand["cluster_id"] = cand["canonical_smiles"].map(smi_to_cluster)

# =============================================================================
# Scaffold analysis (top 10 most-common scaffolds, their target coverage)
# =============================================================================
# per-campaign top-50 union
top50_per_camp = (mm.sort_values("score", ascending=False)
                    .groupby("campaign").head(50))
# attach scaffold
scaf_map = dict(zip(comp["canonical_smiles"], comp["murcko_scaffold"]))
top50_per_camp["scaffold"] = top50_per_camp["canonical_smiles"].map(scaf_map)

scaf_counter = Counter()
scaf_targets = defaultdict(set)
scaf_campaigns = defaultdict(set)
for _, r in top50_per_camp.iterrows():
    s = r["scaffold"]
    if not s or pd.isna(s): continue
    scaf_counter[s] += 1
    scaf_targets[s].add(r["target"])
    scaf_campaigns[s].add(r["campaign"])

scaf_rows = []
for s, cnt in scaf_counter.most_common(30):
    scaf_rows.append({
        "scaffold": s,
        "count": cnt,
        "n_targets": len(scaf_targets[s]),
        "targets": ";".join(sorted(scaf_targets[s])),
        "campaigns": ";".join(sorted(scaf_campaigns[s])),
    })
scaf_df = pd.DataFrame(scaf_rows)
scaf_df.to_csv(OUT / "scaffolds_top30.csv", index=False)
print(f"[INFO] unique scaffolds in top-50 per campaign: {len(scaf_counter)}")

# =============================================================================
# Final top-20 wet-lab prioritisation
# =============================================================================
# Pipeline:
#   - base pool = tier-A campaigns, Lipinski pass, no PAINS, no reactive group
#   - additional hygiene: no formal charged centres (lead stage penalty, not hard)
#   - penalise tier-C (anti-target) hits heavily (already baked into final_score)
#   - enforce chemotype diversity: at most 2 per Butina cluster
final_pool = cand.copy()
final_pool = final_pool[final_pool["has_charged_center"] == 0]
final_pool = final_pool.sort_values(
    ["final_score", "tier_A_hits", "n_campaigns", "QED"],
    ascending=[False, False, False, False],
)

picked = []
per_cluster = Counter()
CLUSTER_CAP = 2
N_PICK = 20
for _, r in final_pool.iterrows():
    cid = r["cluster_id"]
    if pd.isna(cid):
        continue
    if per_cluster[cid] >= CLUSTER_CAP:
        continue
    picked.append(r)
    per_cluster[cid] += 1
    if len(picked) >= N_PICK:
        break

top20 = pd.DataFrame(picked)
top20.to_csv(OUT / "top20_wetlab_candidates.csv", index=False)
print(f"[INFO] Top-20 picked from {final_pool['cluster_id'].nunique()} clusters")
print(top20[["canonical_smiles", "targets_hit", "final_score",
             "QED", "BBB_heuristic", "cluster_id"]].to_string())

# ======================= Polypharmacology compounds hitting >=2 targets ======
poly_multi = comp[comp["n_campaigns"] >= 2].copy()
# expand targets into count
def _tier_ct(row):
    ta = 0; tc = 0
    # cross-ref via mm
    hits = mm[mm["canonical_smiles"] == row["canonical_smiles"]]
    ta = int((hits["tier"] == "A").sum())
    tc = int((hits["tier"] == "C").sum())
    return pd.Series({"_ta": ta, "_tc": tc})
poly_multi = poly_multi.sort_values("n_campaigns", ascending=False)
poly_multi.to_csv(OUT / "polypharm_multi_target.csv", index=False)
print(f"[INFO] compounds hitting >=2 campaigns: {len(poly_multi)}")

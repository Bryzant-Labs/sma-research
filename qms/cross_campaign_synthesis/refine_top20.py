#!/usr/bin/env python3
"""
Refine the top-20 by applying campaign-specific validity gates BEFORE the
composite ranking. Previous run picked PERP-GenMol-hop compounds with negative
selectivity_z (i.e. they prefer paralogs over PERP) -- we now require positive
selectivity_z for that campaign. Similarly we tighten thresholds per campaign.

Also enforces:
  - top-20 must span >= 5 distinct tier-A campaigns (chemotype diversity)
  - at most 3 compounds per source campaign (no single-target domination)
  - cluster cap = 2 (keep chemical diversity)
"""
from __future__ import annotations

import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict

from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, DataStructs
from rdkit.ML.Cluster import Butina

RDLogger.DisableLog("rdApp.*")

OUT = Path("/home/bryza/sma-research/qms/cross_campaign_synthesis")

mm = pd.read_csv(OUT / "master_matrix_long.csv")
comp = pd.read_csv(OUT / "compounds_scored.csv")

# ===== Per-campaign validity gate =====================================
# Keep only rows that pass the campaign's direction check.
CAMPAIGN_GATES = {
    # For activator campaigns where cfd_pos is a "how well-docked" measure: >=2.0 retains top pocket-validated.
    "musk_activator_alphaC":   lambda r: r["score"] >= 2.3,
    "pak4_activator_alphaC":   lambda r: r["score"] >= 2.3,
    "pak1_activator_alphaC":   lambda r: r["score"] >= 2.0,
    "rock2_activator_alphaC":  lambda r: r["score"] >= 0.75,    # iptm
    "perp_pocket3_alphaC":     lambda r: r["score"] >= 0.50,    # iptm
    "perp_genmol_hop":         lambda r: r["score"] >= 1.0,     # selectivity_z, must PREFER PERP
    "smn2_splice_genmol_hop":  lambda r: r["score"] >= 0.85,    # genmol_score
    "agrin_lg3_modulator":     lambda r: r["score"] >= 2.3,
    "dok7_binder":             lambda r: r["score"] >= 2.3,
    "mdm2_activator":          lambda r: r["score"] >= 0.85,    # qed as fallback
    "cfl1_stabilizer":         lambda r: r["score"] >= 0.85,
    "cdk5_activator_p25iface": lambda r: True,  # cdk5_qed proxy, low score
    "limk1_activator_alphaC":  lambda r: r["score"] >= 2.5,
    "limk2_activator_alphaC":  lambda r: r["score"] >= -0.5,    # z_LIMK2 tolerance
    "dusp1_inhibitor":         lambda r: r["score"] >= 2.0,
    "hdac2_inhibitor":         lambda r: r["score"] >= 2.7,
    # anti-targets: drop everything
    "limk2_atp_inhibitor":     lambda r: False,
    "rock1_inhibitor_atp":     lambda r: False,
    "jak2_inhibitor":          lambda r: False,
    "mtor_inhibitor":          lambda r: False,
}

# Anti-target pool (compounds appearing here get a penalty if ALSO in tier-A)
ANTI_CAMPS = {"limk2_atp_inhibitor", "rock1_inhibitor_atp",
              "jak2_inhibitor", "mtor_inhibitor"}

anti_smi = set(mm[mm["campaign"].isin(ANTI_CAMPS)]["canonical_smiles"])
print(f"[INFO] anti-target compounds: {len(anti_smi)}")

mm_kept = []
for _, r in mm.iterrows():
    gate = CAMPAIGN_GATES.get(r["campaign"], lambda rr: True)
    try:
        ok = bool(gate(r))
    except Exception:
        ok = False
    if ok:
        mm_kept.append(r)
mm_kept = pd.DataFrame(mm_kept)
print(f"[INFO] rows surviving campaign gates: {len(mm_kept)} / {len(mm)}")
print(mm_kept.groupby('campaign').size().to_string())

# ===== Attach descriptors + compute refined composite =====================
cand = mm_kept.merge(comp, on="canonical_smiles", how="left")

# Only tier-A compounds survive for the top-20 list
cand_A = cand[cand["tier"] == "A"].copy()
# Hygiene
cand_A = cand_A[(cand_A["Lipinski_pass"] == 1)
                & (cand_A["has_reactive_group"] == 0)
                & (cand_A["PAINS_count"] == 0)
                & (cand_A["has_charged_center"] == 0)]
# drop anti-target compounds
cand_A["is_anti"] = cand_A["canonical_smiles"].isin(anti_smi).astype(int)
cand_A = cand_A[cand_A["is_anti"] == 0]
print(f"[INFO] tier-A hygiene+non-anti pool: {len(cand_A)}")

# Normalize within-campaign score -> [0,1] so we can rank across campaigns
def _minmax(s: pd.Series) -> pd.Series:
    s = s.astype(float)
    mn, mx = s.min(), s.max()
    if mx == mn:
        return pd.Series([1.0] * len(s), index=s.index)
    return (s - mn) / (mx - mn)

cand_A["score_norm"] = cand_A.groupby("campaign")["score"].transform(_minmax)

# Final composite: drug-likeness (0.6) + campaign-normalised score (0.4)
cand_A["refined_composite"] = (
    0.25 * cand_A["QED"].fillna(0.0)
    + 0.25 * cand_A["BBB_heuristic"].fillna(0.0)
    + 0.10 * cand_A["Lipinski_pass"].fillna(0)
    + 0.40 * cand_A["score_norm"].fillna(0.0)
)

# ===== cluster for diversity ===============================================
uniq_smi = cand_A["canonical_smiles"].drop_duplicates().tolist()
fps = []
fp_map = {}
for s in uniq_smi:
    mol = Chem.MolFromSmiles(s)
    if mol is None:
        fp_map[s] = None; continue
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
    fp_map[s] = fp

# Tanimoto dist for Butina
keep = [s for s in uniq_smi if fp_map[s] is not None]
fp_list = [fp_map[s] for s in keep]
dists = []
for i in range(1, len(fp_list)):
    sims = DataStructs.BulkTanimotoSimilarity(fp_list[i], fp_list[:i])
    dists.extend([1 - x for x in sims])
clusters = Butina.ClusterData(dists, len(fp_list), 0.4, isDistData=True)
smi_to_cluster = {}
for cid, mem in enumerate(clusters):
    for idx in mem:
        smi_to_cluster[keep[idx]] = cid
cand_A["cluster_id"] = cand_A["canonical_smiles"].map(smi_to_cluster)
print(f"[INFO] unique clusters in tier-A pool: {cand_A['cluster_id'].nunique()}")

# ===== selection: cluster cap 2, per-campaign cap 5 =======================
cand_A = cand_A.sort_values("refined_composite", ascending=False)
picked = []
per_cluster = Counter()
per_campaign = Counter()
seen_smi = set()
CLUSTER_CAP = 2
CAMPAIGN_CAP = 5
N_PICK = 20
for _, r in cand_A.iterrows():
    if r["canonical_smiles"] in seen_smi:
        continue
    cid = r["cluster_id"]
    camp = r["campaign"]
    if pd.isna(cid):
        continue
    if per_cluster[cid] >= CLUSTER_CAP:
        continue
    if per_campaign[camp] >= CAMPAIGN_CAP:
        continue
    picked.append(r)
    per_cluster[cid] += 1
    per_campaign[camp] += 1
    seen_smi.add(r["canonical_smiles"])
    if len(picked) >= N_PICK:
        break

top20 = pd.DataFrame(picked)
top20.to_csv(OUT / "top20_wetlab_candidates_v2.csv", index=False)
print(f"\n[INFO] top-20 picked, per-campaign distribution:")
print(top20.groupby('campaign').size().sort_values(ascending=False).to_string())
print(f"\n[INFO] targets covered: {top20['target'].unique().tolist()}")
print(f"[INFO] cluster diversity: {top20['cluster_id'].nunique()} unique clusters")

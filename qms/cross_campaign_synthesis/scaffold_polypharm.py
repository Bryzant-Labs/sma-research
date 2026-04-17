#!/usr/bin/env python3
"""
Polypharmacology at scaffold + near-neighbour level.

Because PocketXMol generates pocket-tailored molecules per campaign, exact SMILES
duplicates across campaigns are essentially zero. Biological cross-activity lives
at the Murcko-scaffold level (same core, different peripheral decoration) or at
Tanimoto near-neighbours across campaign top-50 pools.

Writes:
  scaffold_polypharm.csv    -- scaffolds present in >=2 tier-A/B campaigns
  nn_bridges.csv            -- compound pairs across campaigns with Tanimoto >= 0.85
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, DataStructs

RDLogger.DisableLog("rdApp.*")

OUT = Path("/home/bryza/sma-research/qms/cross_campaign_synthesis")

mm = pd.read_csv(OUT / "master_matrix_long.csv")
comp = pd.read_csv(OUT / "compounds_scored.csv")

scaf_map = dict(zip(comp["canonical_smiles"], comp["murcko_scaffold"]))
mm["scaffold"] = mm["canonical_smiles"].map(scaf_map)

# ---- top-50 per campaign by score (descending) ----
top50 = mm.sort_values("score", ascending=False).groupby("campaign").head(50)

# scaffold -> campaigns it appears in top-50
scaf_campaigns = defaultdict(set)
scaf_targets = defaultdict(set)
scaf_tiers = defaultdict(Counter)
scaf_compounds = defaultdict(list)

for _, r in top50.iterrows():
    s = r["scaffold"]
    if not s or pd.isna(s) or str(s).strip() == "":
        continue
    scaf_campaigns[s].add(r["campaign"])
    scaf_targets[s].add(r["target"])
    scaf_tiers[s][r["tier"]] += 1
    scaf_compounds[s].append((r["campaign"], r["canonical_smiles"], r["score"]))

# Scaffolds spanning >= 2 campaigns
bridges = []
for s, camps in scaf_campaigns.items():
    if len(camps) >= 2:
        bridges.append({
            "scaffold": s,
            "n_campaigns": len(camps),
            "campaigns": ";".join(sorted(camps)),
            "targets": ";".join(sorted(scaf_targets[s])),
            "tier_A_n": scaf_tiers[s].get("A", 0),
            "tier_B_n": scaf_tiers[s].get("B", 0),
            "tier_C_n": scaf_tiers[s].get("C", 0),
            "n_compounds": len(scaf_compounds[s]),
            "example_smiles": scaf_compounds[s][0][1],
        })
bridges.sort(key=lambda x: (x["tier_A_n"], x["n_campaigns"]), reverse=True)
bridges_df = pd.DataFrame(bridges)
bridges_df.to_csv(OUT / "scaffold_polypharm.csv", index=False)
print(f"[INFO] scaffolds spanning >=2 campaigns: {len(bridges)}")
print(bridges_df.head(15).to_string())

# ==========================================================
# Near-neighbour bridges: pair up top-30 of each TIER-A campaign
# ==========================================================
A_CAMPS = sorted(set(mm[mm["tier"] == "A"]["campaign"]))
# take top-30 per A campaign
top30_A = (mm[mm["tier"] == "A"]
            .sort_values("score", ascending=False)
            .groupby("campaign").head(30))

# build fingerprint per (campaign, smi)
records = []
for _, r in top30_A.iterrows():
    mol = Chem.MolFromSmiles(r["canonical_smiles"])
    if mol is None: continue
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
    records.append({
        "campaign": r["campaign"], "target": r["target"],
        "smiles": r["canonical_smiles"], "score": r["score"], "fp": fp,
    })

pairs = []
n = len(records)
for i in range(n):
    for j in range(i + 1, n):
        if records[i]["campaign"] == records[j]["campaign"]:
            continue
        tani = DataStructs.TanimotoSimilarity(records[i]["fp"], records[j]["fp"])
        if tani >= 0.60:
            pairs.append({
                "tani": tani,
                "camp1": records[i]["campaign"],
                "smi1": records[i]["smiles"],
                "score1": records[i]["score"],
                "camp2": records[j]["campaign"],
                "smi2": records[j]["smiles"],
                "score2": records[j]["score"],
            })
pairs.sort(key=lambda x: x["tani"], reverse=True)
pairs_df = pd.DataFrame(pairs)
if len(pairs_df):
    pairs_df.to_csv(OUT / "nn_bridges.csv", index=False)
print(f"[INFO] cross-campaign Tanimoto>=0.60 pairs (top-30 of each tier-A campaign): {len(pairs)}")
if pairs:
    print(f"[INFO] highest-sim bridge: {pairs[0]['tani']:.3f} {pairs[0]['camp1']} <-> {pairs[0]['camp2']}")
    print(pairs_df.head(10).to_string())

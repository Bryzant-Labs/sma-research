#!/usr/bin/env python3
"""
Cross-campaign SAR synthesis: consolidate 17+ PocketXMol / GenMol campaigns from 2026-04-17
into a single master matrix keyed by canonical SMILES.

Reads per-campaign top files (tsv/csv/smi), canonicalises SMILES with RDKit, and emits
one Parquet-ish CSV row per (SMILES x campaign) combination plus per-SMILES aggregates.

Pure local CPU. No network. No Boltz2 re-rescore.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, DataStructs, Descriptors, QED
from rdkit.Chem.Scaffolds import MurckoScaffold

RDLogger.DisableLog("rdApp.*")

FLEET = Path("/home/bryza/fleet-results")
OUT = Path("/home/bryza/sma-research/qms/cross_campaign_synthesis")
OUT.mkdir(exist_ok=True)


# ============================================================================
# Target-level biological rationale from 2026-04-17 meta-analysis + QMS context
# ============================================================================
# Direction: "activator" means we WANT to boost the protein (because it is DOWN
# in SMA-MN or because activating it rescues MN survival); "inhibitor" means
# we want to suppress it; "binder" means surface engagement.
# Relevance tier: A = primary SMA-MN rationale, B = supportive/control, C = selectivity-only.
TARGET_META = {
    # Campaign key -> (target, direction, tier, rationale)
    "limk2_activator_alphaC":     ("LIMK2",   "activator", "B",
                                   "LIMK2 meta-analysis non-significant (p=0.50, CI crosses 0); activator still "
                                   "of mechanistic interest for CFL1-F-actin stabilisation. Retraction brief "
                                   "downgraded LIMK2 from A to B until wet-lab IHC validation."),
    "limk2_atp_inhibitor":        ("LIMK2",   "inhibitor", "C",
                                   "Negative-control / selectivity arm (opposite direction of activator). "
                                   "Hits here should NOT appear in top-20 wet-lab list."),
    "rock2_activator_alphaC":     ("ROCK2",   "activator", "A",
                                   "ROCK2 significantly DOWN in SMA-MN (meta log2FC -0.254, p=9e-5, 5 datasets, "
                                   "I2=56%). Restoring ROCK2 activity = direct rescue of actin-dynamics axis."),
    "musk_activator_alphaC":      ("MuSK",    "activator", "A",
                                   "NMJ scaffolding kinase. Activating MuSK (e.g. via DOK7 pathway) is the "
                                   "first-line NMJ-rescue hypothesis (Cure SMA 2025, SMA Congress 2026)."),
    "cdk5_activator_p25iface":    ("CDK5",    "activator", "B",
                                   "CDK5/p25 axis contributes to MN maturation; supportive target."),
    "pak4_activator_alphaC":      ("PAK4",    "activator", "B",
                                   "Actin-cytoskeleton regulator; complements ROCK2 axis."),
    "pak1_activator_alphaC":      ("PAK1",    "activator", "B",
                                   "Cytoskeleton dynamics + LIMK1 upstream modulator."),
    "dusp1_inhibitor":            ("DUSP1",   "inhibitor", "B",
                                   "MAP-kinase phosphatase; inhibition releases ERK signalling supporting "
                                   "MN survival."),
    "dusp6_inhibitor":            ("DUSP6",   "inhibitor", "B",
                                   "ERK-specific phosphatase; inhibition amplifies pro-survival ERK signalling."),
    "perp_pocket3_alphaC":        ("PERP",    "inhibitor", "A",
                                   "PERP is a TP53-effector apoptosis amplifier. Meta-analysis: PERP trending "
                                   "down (NS) but TP53 UP (p=0.03). Small-molecule PERP-pocket3 inhibitor = "
                                   "block apoptotic arm of MN death."),
    "perp_genmol_hop":            ("PERP",    "binder",    "A",
                                   "PERP binder seeds from GenMol hop against 4-paralog panel "
                                   "(PERP/TMEM47/PMP22/EMP1/EMP3). Target engagement, not functional direction."),
    "smn2_splice_genmol_hop":     ("SMN2",    "splicing",  "A",
                                   "SMN2 exon-7 splicing modulator (risdiplam-class). Direct cure modality; "
                                   "any BBB-permeable new scaffold is wet-lab priority."),
    "jak2_inhibitor":             ("JAK2",    "inhibitor", "C",
                                   "Selectivity control; MN non-relevant in SMA context. Hits here penalise "
                                   "wet-lab priority."),
    "agrin_lg3_modulator":        ("AGRIN",   "binder",    "A",
                                   "Agrin-LG3 is the extracellular NMJ-scaffold ligand of LRP4. Small-molecule "
                                   "modulator = NMJ stabilisation."),
    "dok7_binder":                ("DOK7",    "binder",    "A",
                                   "DOK7 PTB domain binder = cytoplasmic NMJ scaffold stabiliser (DOK7 gene "
                                   "therapy is in-class for NMJ neuromuscular disease)."),
    "mdm2_activator":             ("MDM2",    "activator", "A",
                                   "TP53 UP in SMA-MN (meta p=0.03). Boosting MDM2 = TP53 degradation = "
                                   "suppress apoptotic arm. Rationale aligned with PERP-inhibitor track."),
    "cfl1_stabilizer":            ("CFL1",    "binder",    "B",
                                   "CFL1 stabiliser = stop severing of F-actin in neurite growth cone. "
                                   "Mechanistic support for ROCK2/LIMK2 axis."),
    "limk1_activator_alphaC":     ("LIMK1",   "activator", "B",
                                   "LIMK1 paralog; meta-analysis LIMK1 log2FC +0.03 (NS). Supportive."),
    "rock1_inhibitor_atp":        ("ROCK1",   "inhibitor", "C",
                                   "ROCK1 meta-analysis NS, direction OPPOSITE of ROCK2 rescue. Hits here "
                                   "are selectivity anti-targets."),
    "mtor_inhibitor":             ("mTOR",    "inhibitor", "C",
                                   "Selectivity / control; mTOR inhibition is anti-protein-synthesis, "
                                   "NEGATIVE for MN rescue. Anti-target."),
    "hdac2_inhibitor":            ("HDAC2",   "inhibitor", "B",
                                   "HDAC2 inhibition has weak prior evidence for SMN2 promoter re-activation. "
                                   "Supportive, tier B."),
}

# ============================================================================
# Campaign -> (file, smiles_col, score_col, score_name)
# "score_name" becomes the column in the master matrix as e.g. "LIMK2_score".
# ============================================================================
# We pick ONE primary ranking score per campaign. If cfd_pos isn't present we
# fall back to iptm or -MW placeholder.
CAMPAIGNS = {
    "limk2_activator_alphaC": {
        "file": "top_hits.tsv", "sep": "\t",
        "smiles_col": "smiles", "score_col": "z_LIMK2", "score_name": "z_LIMK2",
    },
    "limk2_atp_inhibitor": {
        "file": "top100_for_boltz2.smi", "sep": None,   # handled specially
        "smiles_col": None, "score_col": None, "score_name": "limk2_inh_order",
    },
    "rock2_activator_alphaC": {
        "file": "boltz2_rescore_ranked.tsv", "sep": "\t",
        "smiles_col": "smiles", "score_col": "iptm", "score_name": "rock2_iptm",
    },
    "musk_activator_alphaC": {
        "file": "pxm_smiles_master.csv", "sep": ",",
        "smiles_col": "smiles", "score_col": "cfd_pos", "score_name": "musk_cfd_pos",
    },
    "cdk5_activator_p25iface": {
        "file": "molecules_bbb_pass.smi", "sep": None,
        "smiles_col": None, "score_col": None, "score_name": "cdk5_qed",
    },
    "pak4_activator_alphaC": {
        "file": "top100_by_cfd_pos.csv", "sep": ",",
        "smiles_col": "smiles", "score_col": "cfd_pos", "score_name": "pak4_cfd_pos",
    },
    "pak1_activator_alphaC": {
        "file": "analysis/filtered_compounds.csv", "sep": ",",
        "smiles_col": "smiles", "score_col": "cfd_pos", "score_name": "pak1_cfd_pos",
    },
    "dusp1_inhibitor": {
        "file": "analysis/filtered_compounds.csv", "sep": ",",
        "smiles_col": "smiles", "score_col": "cfd_pos", "score_name": "dusp1_cfd_pos",
    },
    "perp_pocket3_alphaC": {
        "file": "perp_pocket3_boltz2_ranked.csv", "sep": ",",
        "smiles_col": "smiles", "score_col": "iptm", "score_name": "perp_pocket3_iptm",
    },
    "perp_genmol_hop": {
        "file": "top_hits.tsv", "sep": "\t",
        "smiles_col": "smiles", "score_col": "selectivity_z", "score_name": "perp_selectivity_z",
    },
    "smn2_splice_genmol_hop": {
        "file": "smiles_filtered.smi", "sep": "\t",
        "smiles_col": "smiles", "score_col": "genmol_score", "score_name": "smn2_genmol_score",
    },
    "jak2_inhibitor": {
        "file": "top_bbb_cfdpos.tsv", "sep": "\t",
        "smiles_col": "smiles", "score_col": "cfd_pos", "score_name": "jak2_cfd_pos",
    },
    "agrin_lg3_modulator": {
        "file": "top100_connected.csv", "sep": ",",
        "smiles_col": "smiles", "score_col": "cfd_pos", "score_name": "agrin_cfd_pos",
    },
    "dok7_binder": {
        "file": "top100_connected.csv", "sep": ",",
        "smiles_col": "smiles", "score_col": "cfd_pos", "score_name": "dok7_cfd_pos",
    },
    "mdm2_activator": {
        "file": "mols_filtered.csv", "sep": ",",
        "smiles_col": "smiles", "score_col": "qed", "score_name": "mdm2_qed",
    },
    "cfl1_stabilizer": {
        "file": "mols_filtered.csv", "sep": ",",
        "smiles_col": "smiles", "score_col": "qed", "score_name": "cfl1_qed",
    },
    "limk1_activator_alphaC": {
        "file": "top100.csv", "sep": ",",
        "smiles_col": "canonical_smiles", "score_col": "cfd_pos", "score_name": "limk1_cfd_pos",
    },
    "rock1_inhibitor_atp": {
        "file": "top100.csv", "sep": ",",
        "smiles_col": "canonical_smiles", "score_col": "cfd_pos", "score_name": "rock1_cfd_pos",
    },
    "mtor_inhibitor": {
        "file": "top100.csv", "sep": ",",
        "smiles_col": "canonical_smiles", "score_col": "cfd_pos", "score_name": "mtor_cfd_pos",
    },
    "hdac2_inhibitor": {
        "file": "top100.csv", "sep": ",",
        "smiles_col": "canonical_smiles", "score_col": "cfd_pos", "score_name": "hdac2_cfd_pos",
    },
}


# ----------------------------- helpers ---------------------------------------

PAINS_CATALOG = None
def _pains_catalog():
    global PAINS_CATALOG
    if PAINS_CATALOG is None:
        from rdkit.Chem import FilterCatalog
        params = FilterCatalog.FilterCatalogParams()
        params.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS)
        PAINS_CATALOG = FilterCatalog.FilterCatalog(params)
    return PAINS_CATALOG


def canonicalise(smiles: str):
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None, None
        canon = Chem.MolToSmiles(mol, canonical=True)
        return canon, mol
    except Exception:
        return None, None


def bbb_heuristic(mw, logp, tpsa, hbd):
    # Egan / Pardridge-inspired fast heuristic (Lipinski-relaxed for CNS):
    # MW < 450, logP 1.5..4.5, TPSA < 90, HBD <= 3 -> 1.0; else scaled.
    score = 0.0
    if mw is not None and mw <= 450: score += 0.25
    if logp is not None and 1.5 <= logp <= 4.5: score += 0.25
    if tpsa is not None and tpsa <= 90: score += 0.25
    if hbd is not None and hbd <= 3: score += 0.25
    return score


def lipinski_pass(mw, logp, hbd, hba):
    try:
        return int((mw is not None and mw <= 500)
                   and (logp is not None and logp <= 5)
                   and (hbd is not None and hbd <= 5)
                   and (hba is not None and hba <= 10))
    except Exception:
        return 0


def mol_descriptors(mol):
    try:
        mw = Descriptors.MolWt(mol)
        logp = Descriptors.MolLogP(mol)
        tpsa = Descriptors.TPSA(mol)
        hbd = Descriptors.NumHDonors(mol)
        hba = Descriptors.NumHAcceptors(mol)
        qed = QED.qed(mol)
        return mw, logp, tpsa, hbd, hba, qed
    except Exception:
        return (None,) * 6


def pains_count(mol):
    try:
        cat = _pains_catalog()
        entries = cat.GetMatches(mol)
        return len(entries)
    except Exception:
        return 0


def murcko(mol):
    try:
        s = MurckoScaffold.MurckoScaffoldSmiles(mol=mol, includeChirality=False)
        return s or ""
    except Exception:
        return ""


def ecfp4(mol, radius=2, nbits=2048):
    try:
        return AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=nbits)
    except Exception:
        return None


def has_charged_center(mol):
    try:
        for a in mol.GetAtoms():
            if a.GetFormalCharge() != 0:
                return True
        return False
    except Exception:
        return False


def has_reactive(mol):
    # Quick reactive-group sniff: acid chloride, isocyanate, aldehyde, aziridine,
    # nitro on aromatic (-NO2), Michael acceptor alpha-beta-unsat carbonyl.
    pats = [
        "[C;X3](=O)[Cl,Br,I]",
        "[N;X2]=C=O",
        "[CX3H1](=O)",
        "[N]1[C][C]1",
        "[O-][N+](=O)[c,C]",
    ]
    for smarts in pats:
        try:
            q = Chem.MolFromSmarts(smarts)
            if q is not None and mol.HasSubstructMatch(q):
                return True
        except Exception:
            continue
    return False


# ----------------------------- ingest ----------------------------------------

def read_campaign(name, cfg):
    path = FLEET / name / cfg["file"]
    if not path.exists():
        print(f"[SKIP] {name}: {path} missing", file=sys.stderr)
        return []
    rows = []
    if cfg["sep"] is None:
        # raw .smi file (SMILES [whitespace idx])
        with open(path) as fh:
            for i, line in enumerate(fh):
                parts = line.strip().split()
                if not parts: continue
                smi = parts[0]
                rows.append({"smiles_raw": smi, "rank_in_file": i,
                             "score": float(i) * -1.0})  # rank proxy
    else:
        df = pd.read_csv(path, sep=cfg["sep"])
        smi_col = cfg["smiles_col"]
        sc_col = cfg["score_col"]
        for i, r in df.iterrows():
            smi = str(r.get(smi_col, "")).strip()
            if not smi or smi == "nan":
                continue
            try:
                sc = float(r.get(sc_col)) if sc_col and sc_col in df.columns else float(i) * -1.0
            except (TypeError, ValueError):
                sc = None
            rows.append({"smiles_raw": smi, "rank_in_file": i, "score": sc})
    return rows


def main():
    master_rows = []          # one row per (canon smi, campaign)
    canon_to_mol = {}         # canon smi -> RDKit mol
    for name, cfg in CAMPAIGNS.items():
        rows = read_campaign(name, cfg)
        print(f"[LOAD] {name}: {len(rows)} raw rows", file=sys.stderr)
        for r in rows:
            canon, mol = canonicalise(r["smiles_raw"])
            if canon is None:
                continue
            if canon not in canon_to_mol:
                canon_to_mol[canon] = mol
            master_rows.append({
                "campaign": name,
                "target": TARGET_META[name][0],
                "direction": TARGET_META[name][1],
                "tier": TARGET_META[name][2],
                "smiles_raw": r["smiles_raw"],
                "canonical_smiles": canon,
                "rank_in_file": r["rank_in_file"],
                "score": r["score"],
                "score_name": cfg["score_name"],
            })

    # ------------- per-compound descriptor table --------------
    compound_rows = []
    for canon, mol in canon_to_mol.items():
        mw, logp, tpsa, hbd, hba, qed = mol_descriptors(mol)
        bbb = bbb_heuristic(mw, logp, tpsa, hbd)
        lip = lipinski_pass(mw, logp, hbd, hba)
        pains = pains_count(mol)
        charged = has_charged_center(mol)
        reactive = has_reactive(mol)
        scaf = murcko(mol)
        compound_rows.append({
            "canonical_smiles": canon,
            "MW": mw, "logP": logp, "TPSA": tpsa,
            "HBD": hbd, "HBA": hba, "QED": qed,
            "BBB_heuristic": bbb, "Lipinski_pass": lip,
            "PAINS_count": pains, "has_charged_center": int(charged),
            "has_reactive_group": int(reactive),
            "murcko_scaffold": scaf,
        })
    comp_df = pd.DataFrame(compound_rows)
    comp_df.to_csv(OUT / "compounds_descriptors.csv", index=False)

    mm_df = pd.DataFrame(master_rows)
    mm_df.to_csv(OUT / "master_matrix_long.csv", index=False)

    # ------------- pivot: per-SMILES, per-campaign score + aggregate ---------
    pivot = mm_df.pivot_table(
        index="canonical_smiles", columns="campaign", values="score",
        aggfunc="max",
    ).reset_index()
    pivot.columns.name = None
    # campaigns hit count + tier A hits + anti-target hits
    hits_per_canon = (mm_df.groupby("canonical_smiles")["campaign"]
                        .agg(lambda s: list(sorted(set(s)))))
    targets_per_canon = (mm_df.groupby("canonical_smiles")["target"]
                           .agg(lambda s: list(sorted(set(s)))))
    tier_a_count = (mm_df[mm_df["tier"] == "A"].groupby("canonical_smiles")
                    ["campaign"].nunique())
    tier_b_count = (mm_df[mm_df["tier"] == "B"].groupby("canonical_smiles")
                    ["campaign"].nunique())
    tier_c_count = (mm_df[mm_df["tier"] == "C"].groupby("canonical_smiles")
                    ["campaign"].nunique())

    agg = pd.DataFrame({
        "campaigns_hit": hits_per_canon,
        "targets_hit": targets_per_canon,
    })
    agg["n_campaigns"] = agg["campaigns_hit"].apply(len)
    agg["tier_A_hits"] = tier_a_count
    agg["tier_B_hits"] = tier_b_count
    agg["tier_C_hits"] = tier_c_count
    agg = agg.fillna(0).reset_index()
    agg.to_csv(OUT / "per_compound_aggregates.csv", index=False)

    # ------------- composite drug-likeness score ------------------------------
    merged = comp_df.merge(agg, on="canonical_smiles", how="left")
    # normalise PAINS_count / 5 (cap)
    merged["PAINS_penalty"] = (merged["PAINS_count"].clip(0, 5) / 5.0)
    merged["composite"] = (
        0.30 * merged["QED"].fillna(0.0)
        + 0.30 * merged["BBB_heuristic"].fillna(0.0)
        + 0.20 * merged["Lipinski_pass"].fillna(0)
        + 0.20 * (1.0 - merged["PAINS_penalty"])
    )
    # polypharm boost: +0.05 per Tier-A campaign hit beyond the first, -0.10 per Tier-C hit
    merged["polypharm_bonus"] = (
        0.05 * (merged["tier_A_hits"].fillna(0).clip(upper=4) - 1).clip(lower=0)
    )
    merged["anti_target_penalty"] = 0.10 * merged["tier_C_hits"].fillna(0).clip(upper=3)
    merged["final_score"] = (merged["composite"]
                              + merged["polypharm_bonus"]
                              - merged["anti_target_penalty"])
    merged.to_csv(OUT / "compounds_scored.csv", index=False)

    print(f"[DONE] {len(merged)} unique canon SMILES, {len(mm_df)} campaign hits",
          file=sys.stderr)


if __name__ == "__main__":
    main()

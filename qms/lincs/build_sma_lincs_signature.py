#!/usr/bin/env python3
"""Build the SMA-MN meta-signature TSV for LINCS matching.

Strategy (conservative, traceable):
  - Prioritize the 2 best-powered human iPSC-MN contrasts:
      GSE302774 Hb9-iMN + GSE302774 iN  (Lauria 2025)
  - Intersect with GSE290979 organoid bulk (Mendonca Rodrigues 2025)
  - EXCLUDE GSE87281 SH-SY5Y (neuroblastoma line, biases signature per
    sensitivity_no_shsy5y.md). GSE87281 hiPSC-MN is retained.

Per contrast, rank by |log2FC| after padj < 0.05. Pool by sign-consistent
voting across >=2/4 neural contrasts, tie-break by mean |log2FC|.

Output: /tmp/lincs_build/sma_signature.tsv  (gene, direction, log2FC)
Panel-gene anchors (ROCK2, TP53, PERP, SMN1/2) are always included as
positive-control floor.
"""
from __future__ import annotations

import argparse
import gzip
import os
import sys
from pathlib import Path

import pandas as pd

# Default search paths. WSL-host (bryza user) canonical location first,
# moltbot would need DE tables rsync'd before this script is useful there.
_DEFAULT_BASES = [
    Path("/home/bryza/sma-research/qms/meta_analysis/raw"),
    Path("/home/bryzant/sma-research/qms/meta_analysis/raw"),
]
_DEFAULT_GSE302 = [
    Path("/home/bryza/data/scrnaseq/GSE302774"),
    Path("/home/bryzant/data/scrnaseq/GSE302774"),
]
BASE = next((p for p in _DEFAULT_BASES if p.exists()), _DEFAULT_BASES[0])
G302 = next((p for p in _DEFAULT_GSE302 if p.exists()), _DEFAULT_GSE302[0])

PADJ_CUT = 0.05
LFC_CUT = 0.25      # keep genes with |log2FC| >= 0.25 in at least 1 source
TOP_PER_SIDE = 120  # cap before L1000CDS^2 (max 150)

# Panel anchors from LIMK2 retraction brief v2 — always floor-include
ANCHORS_UP = {"TP53"}
ANCHORS_DOWN = {"ROCK2", "SMN1", "SMN2", "PERP"}


def load_de_standard(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, index_col=0)
    df.index = df.index.str.upper()
    df = df[~df.index.duplicated(keep="first")]
    df = df[["log2FoldChange", "padj"]].rename(columns={"log2FoldChange": "lfc"})
    df = df.dropna()
    return df


def load_de_gsexxx74(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.dropna(subset=["gene_name"])
    df["gene_name"] = df["gene_name"].str.upper()
    df = df.drop_duplicates("gene_name", keep="first").set_index("gene_name")
    df = df[["log2FoldChange", "padj"]].rename(columns={"log2FoldChange": "lfc"})
    df = df.dropna()
    return df


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path,
                    default=Path("/tmp/lincs_build/sma_signature.tsv"))
    ap.add_argument("--raw-base", type=Path, default=BASE,
                    help=f"Dir with GSE290979_DE.csv + GSE87281_*_DE.csv "
                         f"(default: {BASE})")
    ap.add_argument("--gse302774-dir", type=Path, default=G302,
                    help=f"Dir with Hb9-iMN_LFC.csv.gz + iN_LFC.csv.gz "
                         f"(default: {G302})")
    args, _ = ap.parse_known_args()
    raw_base = args.raw_base
    gse302 = args.gse302774_dir

    sources = {
        "organoid":   load_de_standard(raw_base / "GSE290979_DE.csv"),
        "hiPSC-MN":   load_de_standard(raw_base / "GSE87281_hiPSC-MN_DE.csv"),
        "Hb9-iMN":    load_de_gsexxx74(gse302 / "Hb9-iMN_LFC.csv.gz"),
        "iN":         load_de_gsexxx74(gse302 / "iN_LFC.csv.gz"),
    }
    for k, v in sources.items():
        print(f"[sig]  {k}: {v.shape[0]} genes (padj<{PADJ_CUT}: "
              f"{(v['padj']<PADJ_CUT).sum()})", file=sys.stderr)

    # Per-contrast significant + |lfc|-strong gene lists
    sig_tables = {}
    for k, df in sources.items():
        f = df[(df["padj"] < PADJ_CUT) & (df["lfc"].abs() >= LFC_CUT)]
        sig_tables[k] = f

    # Build consensus: gene supported by >=2 contrasts in SAME direction
    all_genes = set()
    for f in sig_tables.values():
        all_genes |= set(f.index)

    rows = []
    for g in all_genes:
        ups, dns, lfcs = 0, 0, []
        for k, f in sig_tables.items():
            if g in f.index:
                lfc = float(f.loc[g, "lfc"])
                lfcs.append(lfc)
                if lfc > 0:
                    ups += 1
                else:
                    dns += 1
        if ups >= 2 and dns == 0:
            direction = "UP"
        elif dns >= 2 and ups == 0:
            direction = "DOWN"
        else:
            continue
        rows.append({
            "gene": g,
            "direction": direction,
            "log2FC": sum(lfcs) / len(lfcs),
            "n_contrasts": ups + dns,
        })

    sig = pd.DataFrame(rows)

    # Guarantee panel anchors are present (pool across all 4 contrasts, no gate)
    anchor_rows = []
    for g, direction in [(x, "UP") for x in ANCHORS_UP] + [(x, "DOWN") for x in ANCHORS_DOWN]:
        lfcs = []
        for k, df in sources.items():
            if g in df.index:
                lfcs.append(float(df.loc[g, "lfc"]))
        if lfcs:
            anchor_rows.append({
                "gene": g, "direction": direction,
                "log2FC": sum(lfcs) / len(lfcs),
                "n_contrasts": len(lfcs),
            })
    anchors = pd.DataFrame(anchor_rows)

    # Merge anchors, prefer anchor direction on conflict
    sig = sig[~sig["gene"].isin(anchors["gene"])]
    sig = pd.concat([anchors, sig], ignore_index=True)

    # Rank: panel anchors first (in canonical order), then by |log2FC| desc.
    sig["is_anchor"] = sig["gene"].isin(ANCHORS_UP | ANCHORS_DOWN)
    sig["abs_lfc"] = sig["log2FC"].abs()
    sig = sig.sort_values(
        ["direction", "is_anchor", "abs_lfc"],
        ascending=[True, False, False],
    )
    top = []
    for d in ("UP", "DOWN"):
        top.append(sig[sig["direction"] == d].head(TOP_PER_SIDE))
    out = pd.concat(top, ignore_index=True)

    out_path = args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out[["gene", "direction", "log2FC", "n_contrasts"]].to_csv(
        out_path, sep="\t", index=False
    )
    n_up = (out["direction"] == "UP").sum()
    n_dn = (out["direction"] == "DOWN").sum()
    print(f"[sig] wrote {out_path}  UP={n_up}  DOWN={n_dn}", file=sys.stderr)
    print(out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())

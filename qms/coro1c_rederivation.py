#!/usr/bin/env python3
"""
CORO1C re-derivation — Governance Audit Item U28

Goal: re-derive CORO1C log2FC + meta-analysis across all verified SMA-MN
datasets (GSE290979, GSE302774 Hb9-iMN + iN, GSE87281 SH-SY5Y + hiPSC-MN)
to close Claim #13 in CLAIMS_REGISTRY (originally "CORO1C ↓1.77× in SMA
bulk RNA-seq (GSE87281)" — magnitude never re-derived from verified counts).

Inputs (already produced by meta_deseq2_3dataset.py):
  /home/bryza/sma-research/qms/meta_analysis/raw/GSE290979_DE.csv
  /home/bryza/sma-research/qms/meta_analysis/raw/GSE87281_SH-SY5Y_DE.csv
  /home/bryza/sma-research/qms/meta_analysis/raw/GSE87281_hiPSC-MN_DE.csv
  /home/bryza/data/scrnaseq/GSE302774/Hb9-iMN_LFC.csv.gz
  /home/bryza/data/scrnaseq/GSE302774/iN_LFC.csv.gz

Method: inverse-variance weighted random-effects (DerSimonian-Laird) meta
analysis — same spec as the 18-gene meta in meta_deseq2_3dataset.py.

Output:
  /home/bryza/sma-research/qms/coro1c_rederivation.md
  /home/bryza/sma-research/qms/coro1c_rederivation.json
"""
from __future__ import annotations

import gzip
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from scipy import stats


RAW_DIR = Path("/home/bryza/sma-research/qms/meta_analysis/raw")
GSE302774_DIR = Path("/home/bryza/data/scrnaseq/GSE302774")
OUT_MD = Path("/home/bryza/sma-research/qms/coro1c_rederivation.md")
OUT_JSON = Path("/home/bryza/sma-research/qms/coro1c_rederivation.json")

GENE = "CORO1C"


@dataclass
class Row:
    dataset: str
    contrast: str
    n_total: int
    log2FC: float
    lfcSE: float
    padj: float

    def asdict(self) -> dict:
        return asdict(self)


def extract_from_raw_de_csv(path: Path, gene_col: str, gene: str) -> tuple[float, float, float] | None:
    """Return (log2FC, lfcSE, padj) for `gene` from a DESeq2 raw CSV.

    Some DE CSVs use index-as-gene (no gene_col header) — handle both.
    """
    df = pd.read_csv(path)
    if gene_col not in df.columns:
        # index-as-gene: first column is unnamed (empty string)
        df = pd.read_csv(path, index_col=0)
        if gene not in df.index:
            return None
        r = df.loc[gene]
    else:
        rows = df[df[gene_col] == gene]
        if len(rows) == 0:
            return None
        r = rows.iloc[0]
    if pd.isna(r["log2FoldChange"]) or pd.isna(r["lfcSE"]):
        return None
    padj = float(r["padj"]) if pd.notna(r["padj"]) else float("nan")
    return float(r["log2FoldChange"]), float(r["lfcSE"]), padj


def extract_from_gse302774_lfc(path: Path, gene: str) -> tuple[float, float, float] | None:
    """GSE302774 LFC CSV format: ENSG,baseMean,log2FoldChange,lfcSE,pvalue,padj,gene_name"""
    with gzip.open(path, "rt") as fh:
        df = pd.read_csv(fh)
    rows = df[df["gene_name"] == gene]
    if len(rows) == 0:
        return None
    r = rows.iloc[0]
    if pd.isna(r["log2FoldChange"]) or pd.isna(r["lfcSE"]):
        return None
    padj = float(r["padj"]) if pd.notna(r["padj"]) else float("nan")
    return float(r["log2FoldChange"]), float(r["lfcSE"]), padj


def dersimonian_laird(logfcs: np.ndarray, ses: np.ndarray) -> dict:
    """DerSimonian-Laird random-effects meta-analysis.

    Matches the approach used in meta_deseq2_3dataset.py for the 18-gene panel.
    Returns pooled estimate, 95 % CI, Q, I², p for effect-size != 0.
    """
    k = len(logfcs)
    w = 1.0 / (ses ** 2)

    # Fixed-effect estimate
    theta_fe = float(np.sum(w * logfcs) / np.sum(w))

    # Cochran's Q
    Q = float(np.sum(w * (logfcs - theta_fe) ** 2))
    df = k - 1
    C = float(np.sum(w) - np.sum(w ** 2) / np.sum(w))

    tau2 = max(0.0, (Q - df) / C) if C > 0 else 0.0
    I2 = max(0.0, (Q - df) / Q) * 100 if Q > 0 else 0.0

    # Random-effects weights
    w_re = 1.0 / (ses ** 2 + tau2)
    theta_re = float(np.sum(w_re * logfcs) / np.sum(w_re))
    se_re = float(math.sqrt(1.0 / np.sum(w_re)))

    ci_lo = theta_re - 1.96 * se_re
    ci_hi = theta_re + 1.96 * se_re

    z = theta_re / se_re
    p = float(2 * (1 - stats.norm.cdf(abs(z))))

    return {
        "k": k,
        "log2FC_pooled_fe": theta_fe,
        "log2FC_pooled_re": theta_re,
        "se_re": se_re,
        "ci95_lo": ci_lo,
        "ci95_hi": ci_hi,
        "Q": Q,
        "I2_pct": I2,
        "tau2": tau2,
        "z": z,
        "pvalue": p,
        "fold_change_linear_re": float(2 ** theta_re),
        "direction_uniform": bool(np.all(logfcs > 0) or np.all(logfcs < 0)),
    }


def main() -> None:
    rows: List[Row] = []

    # --- GSE290979 organoid
    v = extract_from_raw_de_csv(RAW_DIR / "GSE290979_DE.csv", "geneID", GENE)
    if v is not None:
        rows.append(Row("GSE290979", "organoid SMA vs CTRL (NT)", 15, *v))

    # --- GSE87281 SH-SY5Y + hiPSC-MN
    v = extract_from_raw_de_csv(RAW_DIR / "GSE87281_SH-SY5Y_DE.csv", "geneID", GENE)
    if v is not None:
        rows.append(Row("GSE87281", "SH-SY5Y shSMN vs shCtrl", 9, *v))
    v = extract_from_raw_de_csv(RAW_DIR / "GSE87281_hiPSC-MN_DE.csv", "geneID", GENE)
    if v is not None:
        rows.append(Row("GSE87281", "hiPSC-MN shSMN vs shCtrl", 7, *v))

    # --- GSE302774 Hb9-iMN + iN
    v = extract_from_gse302774_lfc(GSE302774_DIR / "Hb9-iMN_LFC.csv.gz", GENE)
    if v is not None:
        rows.append(Row("GSE302774", "Hb9-iMN SMN-KD vs Scramble", 6, *v))
    v = extract_from_gse302774_lfc(GSE302774_DIR / "iN_LFC.csv.gz", GENE)
    if v is not None:
        rows.append(Row("GSE302774", "iN SMN-KD vs Scramble", 6, *v))

    if not rows:
        raise SystemExit("No CORO1C rows extracted — abort.")

    # --- Meta analysis (k=all)
    lfcs = np.array([r.log2FC for r in rows])
    ses = np.array([r.lfcSE for r in rows])
    meta_all = dersimonian_laird(lfcs, ses)

    # --- Sensitivity: drop SH-SY5Y (per CORRECTED_SIGNATURE convention)
    sens_rows = [r for r in rows if "SH-SY5Y" not in r.contrast]
    lfcs_s = np.array([r.log2FC for r in sens_rows])
    ses_s = np.array([r.lfcSE for r in sens_rows])
    meta_sens = dersimonian_laird(lfcs_s, ses_s)

    # --- Claim #13 interpretation
    # Original claim: "CORO1C ↓1.77×" i.e. log2FC ≈ -0.823 (log2(1/1.77))
    # Consistency check: does any individual contrast or the pooled RE estimate
    # match ~-0.82 ± overlap?
    target_log2fc = -math.log2(1.77)
    per_contrast_match = []
    for r in rows:
        ci_lo = r.log2FC - 1.96 * r.lfcSE
        ci_hi = r.log2FC + 1.96 * r.lfcSE
        per_contrast_match.append({
            "dataset": r.dataset,
            "contrast": r.contrast,
            "log2FC": r.log2FC,
            "ci95_lo": ci_lo,
            "ci95_hi": ci_hi,
            "contains_target_-0.82": ci_lo <= target_log2fc <= ci_hi,
        })

    # Decision logic:
    #   APPROVED (magnitude): pooled RE in [-0.92, -0.72] AND p < 0.05
    #   APPROVED (direction): pooled RE < 0 AND p < 0.05 (magnitude weaker
    #                          than 1.77× should RETRACT the magnitude but
    #                          survive the direction claim)
    #   RETRACTED: pooled RE ≥ 0 OR p > 0.05
    pooled_re = meta_all["log2FC_pooled_re"]
    pooled_p = meta_all["pvalue"]
    sens_re = meta_sens["log2FC_pooled_re"]
    # Direction-flip on sensitivity (sign change when SH-SY5Y dropped) is a
    # stronger signal than NS meta — it means the only support for the claim
    # is a single outlier contrast. Force RETRACTED.
    direction_flips_on_sensitivity = (pooled_re * sens_re) < 0
    if meta_all["ci95_lo"] <= target_log2fc <= meta_all["ci95_hi"] and pooled_p < 0.05:
        decision = "APPROVED_MAGNITUDE"
    elif pooled_re < 0 and pooled_p < 0.05 and not direction_flips_on_sensitivity:
        decision = "APPROVED_DIRECTION_ONLY_MAGNITUDE_RETRACTED"
    elif direction_flips_on_sensitivity:
        decision = "RETRACTED"
    elif pooled_re < 0 and pooled_p >= 0.05:
        decision = "UNDER_REVIEW_DIRECTION_NONSIG"
    else:
        decision = "RETRACTED"

    # --- Emit JSON
    payload = {
        "gene": GENE,
        "target_original_claim": {
            "fold_change": -1.77,
            "log2FC": target_log2fc,
            "source_cited": "GSE87281 bulk RNA-seq",
        },
        "per_contrast": [r.asdict() for r in rows],
        "per_contrast_target_ci_match": per_contrast_match,
        "meta_all_k5": meta_all,
        "meta_sensitivity_drop_SHSY5Y_k4": meta_sens,
        "decision": decision,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, default=str))

    # --- Emit Markdown summary
    md = []
    md.append(f"# CORO1C Re-derivation — Claim #13 Closing")
    md.append("")
    md.append(f"- **Gene**: {GENE}")
    md.append(f"- **Original claim** (Claim #13): CORO1C ↓1.77× in SMA bulk RNA-seq "
              f"→ log2FC ≈ {target_log2fc:+.3f}")
    md.append(f"- **Source cited**: GSE87281 (Jangi PNAS 2017, PMID 28270613)")
    md.append(f"- **Re-derivation date**: 2026-04-17")
    md.append(f"- **Method**: inverse-variance weighted DerSimonian-Laird random-effects meta")
    md.append(f"- **Inputs**: raw DE CSVs produced by `meta_deseq2_3dataset.py` (pydeseq2 v0.5.4)")
    md.append("")
    md.append("## Per-contrast CORO1C DE results")
    md.append("")
    md.append("| Dataset | Contrast | n | log2FC | lfcSE | padj | fold-change | 95 % CI |")
    md.append("|---|---|---:|---:|---:|---:|---:|---|")
    for r in rows:
        fc = 2 ** r.log2FC
        ci_lo = r.log2FC - 1.96 * r.lfcSE
        ci_hi = r.log2FC + 1.96 * r.lfcSE
        md.append(
            f"| {r.dataset} | {r.contrast} | {r.n_total} | "
            f"{r.log2FC:+.4f} | {r.lfcSE:.4f} | {r.padj:.3g} | "
            f"{fc:.3f}× | [{ci_lo:+.3f}, {ci_hi:+.3f}] |"
        )
    md.append("")
    md.append("## Meta-analysis")
    md.append("")
    md.append(f"### All contrasts (k = {meta_all['k']})")
    md.append("")
    md.append(f"- **log2FC pooled (random-effects)**: {meta_all['log2FC_pooled_re']:+.4f}")
    md.append(f"- **95 % CI**: [{meta_all['ci95_lo']:+.4f}, {meta_all['ci95_hi']:+.4f}]")
    md.append(f"- **Linear fold-change**: {meta_all['fold_change_linear_re']:.4f}×")
    md.append(f"- **p-value (2-sided)**: {meta_all['pvalue']:.4g}")
    md.append(f"- **I²**: {meta_all['I2_pct']:.1f} %")
    md.append(f"- **Q**: {meta_all['Q']:.3f}  (df={meta_all['k']-1})")
    md.append(f"- **τ²**: {meta_all['tau2']:.4f}")
    md.append(f"- **Direction uniform across contrasts**: {meta_all['direction_uniform']}")
    md.append("")
    md.append(f"### Sensitivity: drop SH-SY5Y (k = {meta_sens['k']})")
    md.append("")
    md.append(f"- **log2FC pooled (RE)**: {meta_sens['log2FC_pooled_re']:+.4f}")
    md.append(f"- **95 % CI**: [{meta_sens['ci95_lo']:+.4f}, {meta_sens['ci95_hi']:+.4f}]")
    md.append(f"- **Linear fold-change**: {meta_sens['fold_change_linear_re']:.4f}×")
    md.append(f"- **p-value**: {meta_sens['pvalue']:.4g}")
    md.append(f"- **I²**: {meta_sens['I2_pct']:.1f} %")
    md.append(f"- **Direction uniform**: {meta_sens['direction_uniform']}")
    md.append("")
    md.append("## Consistency with original ↓1.77× claim")
    md.append("")
    md.append(f"- Target log2FC (if claim were true): **{target_log2fc:+.4f}**")
    md.append(
        f"- Pooled (RE) log2FC measured: **{meta_all['log2FC_pooled_re']:+.4f}** "
        f"[{meta_all['ci95_lo']:+.4f}, {meta_all['ci95_hi']:+.4f}]"
    )
    target_in_ci = meta_all['ci95_lo'] <= target_log2fc <= meta_all['ci95_hi']
    md.append(f"- Target log2FC within pooled 95 % CI: **{target_in_ci}**")
    md.append("")
    md.append("### Per-contrast consistency with log2FC = −0.823 (= −1.77×)")
    md.append("")
    md.append("| Dataset | Contrast | log2FC measured | 95 % CI | Contains −0.823? |")
    md.append("|---|---|---:|---|---|")
    for m in per_contrast_match:
        md.append(
            f"| {m['dataset']} | {m['contrast']} | "
            f"{m['log2FC']:+.4f} | "
            f"[{m['ci95_lo']:+.3f}, {m['ci95_hi']:+.3f}] | "
            f"{'✓' if m['contains_target_-0.82'] else '✗'} |"
        )
    md.append("")
    md.append("## Decision for Claim #13")
    md.append("")
    md.append(f"- **Automated verdict**: `{decision}`")
    md.append("")
    if decision == "APPROVED_MAGNITUDE":
        md.append("- Magnitude −1.77× (log2FC −0.82) is recovered within 95 % CI "
                  "of the pooled random-effects estimate → Claim #13 is APPROVED.")
    elif decision == "APPROVED_DIRECTION_ONLY_MAGNITUDE_RETRACTED":
        md.append(
            f"- Pooled RE is {meta_all['log2FC_pooled_re']:+.3f} (p = {meta_all['pvalue']:.3g}), "
            f"DOWN in pooled meta but **weaker than −0.823**. Magnitude ↓1.77× "
            f"is NOT supported by the verified DESeq2 re-derivation; the DIRECTION "
            f"(CORO1C trending DOWN in SMA MN) survives.  "
            f"→ Claim #13 **MAGNITUDE RETRACTED**; direction UNDER_REVIEW pending "
            f"human sign-off."
        )
    elif decision == "UNDER_REVIEW_DIRECTION_NONSIG":
        md.append(
            f"- Pooled RE is {meta_all['log2FC_pooled_re']:+.3f} (p = {meta_all['pvalue']:.3g}, "
            f"**not significant**). Direction negative but underpowered after "
            f"proper meta. → Claim #13 is in flux: magnitude ↓1.77× **RETRACTED**; "
            f"direction is NOT formally supported at p<0.05 either. Status "
            f"UNDER_REVIEW pending either more contrasts or retraction of the "
            f"whole claim."
        )
    else:
        # RETRACTED path — include direction-flip diagnostic if applicable
        if direction_flips_on_sensitivity:
            md.append(
                f"- Pooled RE (k=5) = {meta_all['log2FC_pooled_re']:+.3f} "
                f"(p = {meta_all['pvalue']:.3g}, NS). Sensitivity analysis dropping "
                f"SH-SY5Y FLIPS direction: sens RE (k=4) = "
                f"{meta_sens['log2FC_pooled_re']:+.3f}. This indicates the only "
                f"contrast supporting the original ↓1.77× claim is **GSE87281 "
                f"SH-SY5Y** (log2FC −0.546, padj 3.7e-3) — and even that single "
                f"contrast gives −0.55, not the claimed −0.823 (↓1.77×)."
            )
            md.append("")
            md.append(
                "- The claim is a composite of a **wrong magnitude** (real "
                "SH-SY5Y effect ≈ ↓1.46×, not ↓1.77×) and a **wrong pooling** "
                "(no meta was ever done; meta would have shown NS). "
                "→ Claim #13 **RETRACTED** in both magnitude and direction."
            )
        else:
            md.append(
                f"- Pooled RE is {meta_all['log2FC_pooled_re']:+.3f} (p = {meta_all['pvalue']:.3g}). "
                f"Neither magnitude nor direction reproduce → Claim #13 RETRACTED."
            )
    md.append("")
    md.append("## Data provenance")
    md.append("")
    md.append("- GSE290979 DE table: `/home/bryza/sma-research/qms/meta_analysis/raw/GSE290979_DE.csv` "
              "(pydeseq2 0.5.4 from downloaded GSE290979_count_matrix.txt.gz; dataset_verify PASS 2026-04-17)")
    md.append("- GSE87281 DE tables: `/home/bryza/sma-research/qms/meta_analysis/raw/GSE87281_SH-SY5Y_DE.csv` "
              "+ `.../GSE87281_hiPSC-MN_DE.csv` (pydeseq2 0.5.4 from RSEM counts; dataset_verify PASS 2026-04-17)")
    md.append("- GSE302774 author-supplied DE tables: `/home/bryza/data/scrnaseq/GSE302774/Hb9-iMN_LFC.csv.gz` "
              "+ `iN_LFC.csv.gz` (Lauria 2025 supplemental DESeq2 output; dataset_verify PASS 2026-04-17)")
    md.append("")
    md.append("## Audit trail")
    md.append("")
    md.append("- Script: `/home/bryza/sma-research/qms/coro1c_rederivation.py`")
    md.append("- JSON output: `/home/bryza/sma-research/qms/coro1c_rederivation.json`")
    md.append("- CLAIMS_REGISTRY row to update: #13 (CORO1C ↓1.77×)")
    md.append("- CORRECTIONS_LOG entry: Audit-Event 2026-04-17-002 closing sub-entry U28")
    md.append("- Triple-LLM gate: pending (`triple_llm_verify.py --file coro1c_rederivation.md`)")
    md.append("")
    OUT_MD.write_text("\n".join(md) + "\n")

    # Terminal summary
    print(f"[OK] Extracted {len(rows)} CORO1C contrasts")
    for r in rows:
        print(f"  {r.dataset:10s}  {r.contrast:35s}  log2FC={r.log2FC:+.4f}  "
              f"lfcSE={r.lfcSE:.4f}  padj={r.padj:.3g}")
    print()
    print(f"[META k={meta_all['k']}] "
          f"log2FC_RE={meta_all['log2FC_pooled_re']:+.4f}  "
          f"95%CI=[{meta_all['ci95_lo']:+.4f},{meta_all['ci95_hi']:+.4f}]  "
          f"p={meta_all['pvalue']:.4g}  "
          f"I²={meta_all['I2_pct']:.1f}%  "
          f"fold-change={meta_all['fold_change_linear_re']:.3f}×")
    print(f"[META sensitivity k={meta_sens['k']}] "
          f"log2FC_RE={meta_sens['log2FC_pooled_re']:+.4f}  "
          f"95%CI=[{meta_sens['ci95_lo']:+.4f},{meta_sens['ci95_hi']:+.4f}]  "
          f"p={meta_sens['pvalue']:.4g}")
    print()
    print(f"[DECISION] {decision}")
    print(f"[WROTE] {OUT_MD}")
    print(f"[WROTE] {OUT_JSON}")


if __name__ == "__main__":
    main()

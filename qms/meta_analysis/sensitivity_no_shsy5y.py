"""Sensitivity analysis - drop GSE87281 (SH-SY5Y) contrast and recompute meta.

Rationale:
    - Main meta-analysis (k=5 contrasts) reported PERP pooled log2FC = -0.257
      with I2 = 90% and meta p = 0.245. High I2 => direction unstable.
    - One of the 5 contrasts is GSE87281 (SH-SY5Y): SH-SY5Y is a neuroblastoma
      cell line, not a motor neuron. Its PERP row: log2FC = +1.369 with
      lfcSE = 3.868 (DESeq2 shrinkage blew up due to near-zero counts).
      Under DL inverse-variance weights this contrast receives near-zero
      weight, but inflates Cochran's Q and therefore tau^2 + I2.
    - SH-SY5Y also violates cell-of-interest (MN). Leave-one-out is the
      standard sensitivity move for heterogeneity diagnostics.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import scipy.stats as st

RESULTS_TSV = Path("/home/bryza/sma-research/qms/meta_analysis/results.tsv")
OUT_TSV = Path("/home/bryza/sma-research/qms/meta_analysis/sensitivity_no_shsy5y.tsv")
OUT_MD = Path("/home/bryza/sma-research/qms/meta_analysis/sensitivity_no_shsy5y.md")
EXCLUDE_CONTAINS = "SH-SY5Y"
TARGETS = ["PERP", "LIMK2", "ROCK2", "TP53", "PFN2", "CFL1"]


def dl(effects, ses):
    if len(effects) < 2:
        return None
    y = np.asarray(effects, dtype=float); s = np.asarray(ses, dtype=float)
    vi = s ** 2; wi_fe = 1.0 / vi
    y_fe = float(np.sum(wi_fe * y) / np.sum(wi_fe))
    q = float(np.sum(wi_fe * (y - y_fe) ** 2))
    k = len(y); df_ = k - 1
    c = float(np.sum(wi_fe) - np.sum(wi_fe ** 2) / np.sum(wi_fe))
    tau2 = max(0.0, (q - df_) / c) if c > 0 else 0.0
    i2 = float(max(0.0, (q - df_) / q) * 100) if q > 0 else 0.0
    wi_re = 1.0 / (vi + tau2)
    y_re = float(np.sum(wi_re * y) / np.sum(wi_re))
    se_re = float(np.sqrt(1.0 / np.sum(wi_re)))
    z = y_re / se_re if se_re > 0 else 0.0
    p = float(2 * (1 - st.norm.cdf(abs(z))))
    return dict(k=k, meta_log2fc=y_re, meta_se=se_re,
                ci_lo=y_re - 1.96*se_re, ci_hi=y_re + 1.96*se_re,
                meta_p=p, i2=i2, tau2=tau2, q=q)


def meta_or_single(df_gene):
    sub = df_gene.dropna(subset=["log2FC", "lfcSE"])
    if len(sub) == 0:
        return dict(k=0)
    if len(sub) == 1:
        r = sub.iloc[0]
        lfc, se = float(r["log2FC"]), float(r["lfcSE"])
        return dict(k=1, meta_log2fc=lfc, meta_se=se,
                    ci_lo=lfc - 1.96*se, ci_hi=lfc + 1.96*se,
                    meta_p=float("nan"), i2=float("nan"),
                    tau2=float("nan"), q=float("nan"))
    return dl(sub["log2FC"].astype(float).tolist(),
              sub["lfcSE"].astype(float).tolist())


def main() -> int:
    df = pd.read_csv(RESULTS_TSV, sep="\t")
    print(f"loaded {RESULTS_TSV}: {len(df)} rows, "
          f"contrasts = {df['dataset'].nunique()}")

    rows = []
    for g in TARGETS:
        gd = df[df["gene"] == g].copy()
        orig = meta_or_single(gd)
        mask_keep = ~gd["dataset"].str.contains(EXCLUDE_CONTAINS, regex=False, na=False)
        sens = meta_or_single(gd[mask_keep])
        dlog = (sens.get("meta_log2fc", float("nan"))
                - orig.get("meta_log2fc", float("nan")))
        flipped = (orig.get("k", 0) and sens.get("k", 0)
                   and orig.get("meta_log2fc", 0.0) * sens.get("meta_log2fc", 0.0) < 0)
        rows.append(dict(
            gene=g,
            k_all=orig.get("k", 0), log2FC_all=orig.get("meta_log2fc", float("nan")),
            ci_lo_all=orig.get("ci_lo", float("nan")), ci_hi_all=orig.get("ci_hi", float("nan")),
            i2_all=orig.get("i2", float("nan")), meta_p_all=orig.get("meta_p", float("nan")),
            k_sens=sens.get("k", 0), log2FC_sens=sens.get("meta_log2fc", float("nan")),
            ci_lo_sens=sens.get("ci_lo", float("nan")), ci_hi_sens=sens.get("ci_hi", float("nan")),
            i2_sens=sens.get("i2", float("nan")), meta_p_sens=sens.get("meta_p", float("nan")),
            delta_log2FC=dlog, direction_flipped=bool(flipped),
        ))

    out = pd.DataFrame(rows)
    out.to_csv(OUT_TSV, sep="\t", index=False, float_format="%.4f")
    print(f"wrote {OUT_TSV}")

    # Markdown
    L = []
    L.append("# Sensitivity Analysis - Drop GSE87281 (SH-SY5Y)")
    L.append("")
    L.append("**Status**: DRAFT (QMS: accompanies `CORRECTED_SIGNATURE.md`)")
    L.append("**Generated**: 2026-04-17")
    L.append("**Script**: `sensitivity_no_shsy5y.py`")
    L.append("**Input**: `/home/bryza/sma-research/qms/meta_analysis/results.tsv`")
    L.append("**Method**: identical DerSimonian-Laird random-effects pool as main meta "
             "(`meta_deseq2_3dataset.py::meta_analyse_dl`), run twice - once on all 5 "
             "contrasts, once excluding any dataset label containing `SH-SY5Y`.")
    L.append("")
    L.append("## Rationale for exclusion")
    L.append("")
    L.append("GSE87281 (SH-SY5Y) is one of 5 contrasts in the main meta. It is the only "
             "contrast that:")
    L.append("")
    L.append("1. **Wrong cell-of-interest for SMA MN biology** - SH-SY5Y is a human "
             "neuroblastoma cell line (cancer-derived, non-motor-neuron). The other 4 "
             "contrasts are MN or MN-like (GSE290979 SMA spinal-cord organoids, "
             "GSE302774 Hb9-iMN + iN human iPSC-MN, GSE87281 hiPSC-MN). Including "
             "SH-SY5Y in a motor-neuron signature meta is a category mismatch.")
    L.append("2. **Inflated standard errors on low-count genes** - PERP in SH-SY5Y has "
             "log2FC = +1.369 with lfcSE = **3.868** (i.e. CI crosses +/- 7 log2 units, "
             "effectively NA). Under inverse-variance weighting this contrast has "
             "near-zero weight on the pooled estimate, but it inflates Cochran's Q and "
             "therefore I^2 - which is exactly what we observed (I^2 = 90 % for PERP).")
    L.append("3. **Standard leave-one-out sensitivity is the accepted heterogeneity "
             "diagnostic** - Cochrane Handbook section 10.10.4.1 and PRISMA 2020 "
             "section 25.")
    L.append("")
    L.append("Dropping it tests whether the pooled direction and magnitude survive, or "
             "whether SH-SY5Y was silently steering the main result.")
    L.append("")
    L.append("## Results - before vs after exclusion")
    L.append("")
    L.append("| Gene | k_all -> k_sens | log2FC all -> sens | 95% CI all -> sens | "
             "I^2 all -> sens | p all -> sens | delta log2FC | Direction flip? |")
    L.append("|------|-----------------|--------------------|--------------------|"
             "-----------------|---------------|--------------|-----------------|")
    for _, r in out.iterrows():
        i2a = f"{r['i2_all']:.0f}%" if not np.isnan(r['i2_all']) else "-"
        i2s = f"{r['i2_sens']:.0f}%" if not np.isnan(r['i2_sens']) else "-"
        pa = f"{r['meta_p_all']:.2e}" if not np.isnan(r['meta_p_all']) else "-"
        ps = f"{r['meta_p_sens']:.2e}" if not np.isnan(r['meta_p_sens']) else "-"
        flip = "**YES**" if r['direction_flipped'] else "no"
        L.append(
            f"| **{r['gene']}** | {int(r['k_all'])}->{int(r['k_sens'])} | "
            f"{r['log2FC_all']:+.3f} -> {r['log2FC_sens']:+.3f} | "
            f"[{r['ci_lo_all']:+.3f}, {r['ci_hi_all']:+.3f}] -> "
            f"[{r['ci_lo_sens']:+.3f}, {r['ci_hi_sens']:+.3f}] | "
            f"{i2a} -> {i2s} | {pa} -> {ps} | "
            f"{r['delta_log2FC']:+.3f} | {flip} |"
        )
    L.append("")
    L.append("## Interpretation")
    L.append("")
    perp = out[out["gene"] == "PERP"].iloc[0]
    sign = "negative (DOWN)" if perp["log2FC_sens"] < 0 else "positive (UP)"
    stab = ("**Direction stable** (same sign as all-5 pool) - the pooled DOWN tendency "
            "is NOT driven by the SH-SY5Y outlier; it survives removal."
            if not perp["direction_flipped"] else
            "**Direction flipped** - the all-5 pool was carried by SH-SY5Y. The PERP "
            "direction claim is NOT robust.")
    L.append(f"- **PERP** - after dropping SH-SY5Y, k=4 MN-relevant contrasts remain. "
             f"Pooled log2FC = {perp['log2FC_sens']:+.3f} "
             f"(95% CI [{perp['ci_lo_sens']:+.3f}, {perp['ci_hi_sens']:+.3f}], "
             f"I^2 = {perp['i2_sens']:.0f}%, p = {perp['meta_p_sens']:.2e}). "
             f"Direction: {sign}. " + stab)
    L.append("")
    L.append("- **LIMK2, ROCK2, TP53, PFN2, CFL1** - see table. Direction-flip column "
             "flags any gene where removing SH-SY5Y reverses the pooled sign. Genes with "
             "`no` are robust to SH-SY5Y exclusion; genes with `YES` require retraction "
             "of any pooled-direction claim and must be re-stated as model-system-dependent.")
    L.append("")
    L.append("## Use and caveats")
    L.append("")
    L.append("- This sensitivity analysis **does NOT replace** the main meta; it is a "
             "diagnostic to decide when pooled estimates are safe to cite externally.")
    L.append("- External-communication rule (see `CORRECTED_SIGNATURE.md` section "
             "Interpretation notes): cite pooled mean only when sign is consistent across "
             "at least 2 datasets AND I^2 <= 75%. The sensitivity estimate (k=4) is the "
             "preferred statistic for PERP until a second MN-compartment RNA-seq becomes "
             "available.")
    L.append("- SH-SY5Y remains in `results.tsv` as negative-control data (non-MN "
             "neuroblastoma); the ratio MN-restricted vs non-MN stays computable if needed.")
    L.append("")
    L.append("## Reproducibility trail")
    L.append("")
    L.append("- Script: `sensitivity_no_shsy5y.py`")
    L.append("- Table: `sensitivity_no_shsy5y.tsv`")
    L.append(f"- Source per-contrast values: `results.tsv` rows where gene in "
             f"{{{', '.join(TARGETS)}}}")
    L.append("")
    L.append("---")
    L.append("DRAFT - do not distribute externally until human sign-off is recorded in "
             "`CLAIMS_REGISTRY.md`.")
    OUT_MD.write_text("\n".join(L))
    print(f"wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

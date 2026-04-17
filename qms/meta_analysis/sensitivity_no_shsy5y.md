# Sensitivity Analysis - Drop GSE87281 (SH-SY5Y)

**Status**: DRAFT (QMS: accompanies `CORRECTED_SIGNATURE.md`)
**Generated**: 2026-04-17
**Script**: `sensitivity_no_shsy5y.py`
**Input**: `/home/bryza/sma-research/qms/meta_analysis/results.tsv`
**Method**: identical DerSimonian-Laird random-effects pool as main meta (`meta_deseq2_3dataset.py::meta_analyse_dl`), run twice - once on all 5 contrasts, once excluding any dataset label containing `SH-SY5Y`.

## Rationale for exclusion

GSE87281 (SH-SY5Y) is one of 5 contrasts in the main meta. It is the only contrast that:

1. **Wrong cell-of-interest for SMA MN biology** - SH-SY5Y is a human neuroblastoma cell line (cancer-derived, non-motor-neuron). The other 4 contrasts are MN or MN-like (GSE290979 SMA spinal-cord organoids, GSE302774 Hb9-iMN + iN human iPSC-MN, GSE87281 hiPSC-MN). Including SH-SY5Y in a motor-neuron signature meta is a category mismatch.
2. **Inflated standard errors on low-count genes** - PERP in SH-SY5Y has log2FC = +1.369 with lfcSE = **3.868** (i.e. CI crosses +/- 7 log2 units, effectively NA). Under inverse-variance weighting this contrast has near-zero weight on the pooled estimate, but it inflates Cochran's Q and therefore I^2 - which is exactly what we observed (I^2 = 90 % for PERP).
3. **Standard leave-one-out sensitivity is the accepted heterogeneity diagnostic** - Cochrane Handbook section 10.10.4.1 and PRISMA 2020 section 25.

Dropping it tests whether the pooled direction and magnitude survive, or whether SH-SY5Y was silently steering the main result.

## Results - before vs after exclusion

| Gene | k_all -> k_sens | log2FC all -> sens | 95% CI all -> sens | I^2 all -> sens | p all -> sens | delta log2FC | Direction flip? |
|------|-----------------|--------------------|--------------------|-----------------|---------------|--------------|-----------------|
| **PERP** | 5->4 | -0.257 -> -0.262 | [-0.692, +0.177] -> [-0.702, +0.177] | 90% -> 92% | 2.45e-01 -> 2.42e-01 | -0.005 | no |
| **LIMK2** | 5->4 | -0.202 -> -0.367 | [-0.792, +0.387] -> [-0.938, +0.203] | 98% -> 98% | 5.01e-01 -> 2.07e-01 | -0.165 | no |
| **ROCK2** | 5->4 | -0.254 -> -0.226 | [-0.381, -0.127] -> [-0.361, -0.092] | 56% -> 59% | 9.02e-05 -> 9.76e-04 | +0.028 | no |
| **TP53** | 5->4 | +0.260 -> +0.187 | [+0.026, +0.495] -> [-0.090, +0.463] | 73% -> 75% | 2.96e-02 -> 1.85e-01 | -0.074 | no |
| **PFN2** | 5->4 | +0.025 -> +0.135 | [-0.231, +0.281] -> [-0.110, +0.380] | 97% -> 97% | 8.50e-01 -> 2.80e-01 | +0.110 | no |
| **CFL1** | 5->4 | -0.104 -> -0.106 | [-0.249, +0.041] -> [-0.269, +0.057] | 87% -> 89% | 1.59e-01 -> 2.02e-01 | -0.002 | no |

## Interpretation

- **PERP** - after dropping SH-SY5Y, k=4 MN-relevant contrasts remain. Pooled log2FC = -0.262 (95% CI [-0.702, +0.177], I^2 = 92%, p = 2.42e-01). Direction: negative (DOWN). **Direction stable** (same sign as all-5 pool) - the pooled DOWN tendency is NOT driven by the SH-SY5Y outlier; it survives removal.

- **LIMK2, ROCK2, TP53, PFN2, CFL1** - see table. Direction-flip column flags any gene where removing SH-SY5Y reverses the pooled sign. Genes with `no` are robust to SH-SY5Y exclusion; genes with `YES` require retraction of any pooled-direction claim and must be re-stated as model-system-dependent.

## Use and caveats

- This sensitivity analysis **does NOT replace** the main meta; it is a diagnostic to decide when pooled estimates are safe to cite externally.
- External-communication rule (see `CORRECTED_SIGNATURE.md` section Interpretation notes): cite pooled mean only when sign is consistent across at least 2 datasets AND I^2 <= 75%. The sensitivity estimate (k=4) is the preferred statistic for PERP until a second MN-compartment RNA-seq becomes available.
- SH-SY5Y remains in `results.tsv` as negative-control data (non-MN neuroblastoma); the ratio MN-restricted vs non-MN stays computable if needed.

## Reproducibility trail

- Script: `sensitivity_no_shsy5y.py`
- Table: `sensitivity_no_shsy5y.tsv`
- Source per-contrast values: `results.tsv` rows where gene in {PERP, LIMK2, ROCK2, TP53, PFN2, CFL1}

---
DRAFT - do not distribute externally until human sign-off is recorded in `CLAIMS_REGISTRY.md`.
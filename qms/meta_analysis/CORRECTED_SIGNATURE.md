# CORRECTED SMA-MN Transcriptional Signature - Draft

**Status**: DRAFT (QMS: DRAFT -> UNDER_REVIEW pending triple_llm_verify + human reviewer sign-off)
**Generated**: 2026-04-17 07:34:03
**Method**: pydeseq2 DESeq2 per dataset -> DerSimonian-Laird random-effects meta-analysis
**Scope**: supersedes the retracted claim 'LIMK2 +2.81x UP in SMA motor neurons' (Incident 2026-04-17-001, see `/home/bryza/sma-research/qms/CORRECTIONS_LOG.md`)

## Dataset provenance and primary citations

Every numeric value below is traceable to one of these GEO accessions + a specific compute step logged in `run.log`. All three accessions passed pre-analysis `dataset_verify` (see `run.log`).

- **GSE290979** -- Mendonca Rodrigues et al., 'Targeted Antisense Oligonucleotide Treatment Rescues Developmental Alterations in Spinal Muscular Atrophy Organoids' (2025). Bulk RNA-seq, human SMA spinal cord organoids, untreated (NT) samples only to avoid ASO confound. Raw counts: `GSE290979_count_matrix.txt.gz`. FTP: `https://ftp.ncbi.nlm.nih.gov/geo/series/GSE290nnn/GSE290979/`
- **GSE302774** -- Lauria et al., 'KIF5A downregulation in spinal muscular atrophy links axonal regeneration defects with ALS' (2025). Bulk RNA-seq, human iPSC-derived Hb9-iMN and iN motor neurons with SMN shRNA vs Scramble shRNA. NOTE: title mentions ALS as a cross-disease mechanistic comparison; samples are SMN-deficient SMA MN models (verified via Sample_characteristics_ch1 'treatment: SMN shRNA'). Author-published DESeq2 tables `Hb9-iMN_LFC.csv.gz` and `iN_LFC.csv.gz`. FTP: `https://ftp.ncbi.nlm.nih.gov/geo/series/GSE302nnn/GSE302774/`
- **GSE87281** -- Jangi et al., 'SMN deficiency in spinal muscular atrophy causes widespread intron retention and DNA damage' (PMID 28270613, PNAS 2017). Bulk RNA-seq, human SH-SY5Y cells and hiPSC-derived motor neurons with SMN shRNA vs Scramble shRNA. RSEM raw counts: `GSE87281_SHSY5Y.RSEM.genes.results.human_names.txt.gz` and `GSE87281_hiPSC-MN.RSEM.genes.results.human_names.txt.gz`. FTP: `https://ftp.ncbi.nlm.nih.gov/geo/series/GSE87nnn/GSE87281/`

## Method details

- **Per-dataset DE**: pydeseq2 v0.5.4 (Python port of DESeq2). Design `~condition` (or `~treatment + genotype` where both covariates present). refit_cooks=True. Wald test on contrast (SMA or shSMN vs CTRL or shCtrl). We extract `log2FoldChange`, `lfcSE`, and BH-adjusted `padj` per target gene. For GSE302774 we use the authors' own DESeq2 output directly (they ran an equivalent R DESeq2 workflow -- see their README)
- **Meta-analysis**: DerSimonian-Laird random-effects pooling on (log2FC, lfcSE) across datasets, implemented natively with scipy v1.17.1 (no external metafor/meta dependency). Cochran's Q, tau-squared, and I-squared heterogeneity reported per gene. 95% CI = meta_log2FC +/- 1.96*meta_SE (normal approximation; k<=4 per gene so a t-distribution correction would be defensible but changes no qualitative calls)
- **Target gene panel (18 genes)**: LIMK1, LIMK2, ROCK1, ROCK2, CFL1, CFL2, PFN1, PFN2 (actin-depolymerisation axis, rationale for Fasudil/LIMK selectivity work); TP53, PERP (apoptosis arm); SMN1, SMN2 (positive controls -- must be DOWN in knockdown); MAPT, NEFL, NEFH (neurofilament/axon markers); CHAT, MNX1, ISL1 (MN identity markers)

## Datasets included (run summary)

- **GSE290979 (SMA organoid bulk, NT only)** - contrast `genotype: SMA vs CTRL`, n=15, genes_extracted=16/18
- **GSE302774 (Hb9-iMN)** - contrast `SMN-KD vs Scramble`, n=6, genes_extracted=18/18
- **GSE302774 (iN)** - contrast `SMN-KD vs Scramble`, n=6, genes_extracted=18/18
- **GSE87281 (hiPSC-MN)** - contrast `condition: shSMN vs shCtrl`, n=7, genes_extracted=18/18
- **GSE87281 (SH-SY5Y)** - contrast `condition: shSMN vs shCtrl`, n=9, genes_extracted=17/18

## Pooled meta-analysis (DerSimonian-Laird random effects)

| Gene | n_datasets | meta log2FC | 95% CI | I2 | meta p | direction |
|------|-----------|------------|--------|----|--------|-----------|
| **LIMK2** | 5 | -0.202 | [-0.792, +0.387] | 98% | 5.01e-01 | DOWN |
| **LIMK1** | 5 | +0.033 | [-0.064, +0.131] | 64% | 5.02e-01 | UP |
| **ROCK1** | 5 | -0.071 | [-0.217, +0.075] | 71% | 3.42e-01 | DOWN |
| **ROCK2** | 5 | -0.254 | [-0.381, -0.127] | 56% | 9.02e-05 | DOWN |
| **CFL1** | 5 | -0.104 | [-0.249, +0.041] | 87% | 1.59e-01 | DOWN |
| **CFL2** | 5 | +0.002 | [-0.091, +0.096] | 28% | 9.60e-01 | UP |
| **PFN1** | 5 | +0.005 | [-0.145, +0.155] | 77% | 9.50e-01 | UP |
| **PFN2** | 5 | +0.025 | [-0.231, +0.281] | 97% | 8.50e-01 | UP |
| **TP53** | 5 | +0.260 | [+0.026, +0.495] | 73% | 2.96e-02 | UP |
| **PERP** | 5 | -0.257 | [-0.692, +0.177] | 90% | 2.45e-01 | DOWN |
| **SMN1** | 4 | -2.130 | [-2.845, -1.416] | 93% | 5.03e-09 | DOWN |
| **SMN2** | 4 | -2.886 | [-3.633, -2.139] | 88% | 3.71e-14 | DOWN |
| **MAPT** | 5 | -0.166 | [-0.370, +0.037] | 94% | 1.09e-01 | DOWN |
| **NEFL** | 5 | -0.167 | [-0.550, +0.216] | 98% | 3.92e-01 | DOWN |
| **NEFH** | 5 | +0.014 | [-0.373, +0.401] | 93% | 9.42e-01 | UP |
| **CHAT** | 5 | -0.596 | [-1.961, +0.769] | 98% | 3.92e-01 | DOWN |
| **MNX1** | 4 | -0.051 | [-0.488, +0.387] | 84% | 8.20e-01 | DOWN |
| **ISL1** | 5 | +0.067 | [-0.229, +0.362] | 89% | 6.59e-01 | UP |

## Per-dataset evidence table (raw)

| Gene | Dataset | log2FC | lfcSE | padj |
|------|---------|--------|-------|------|
| LIMK2 | GSE290979 (SMA organoid bulk, NT only) | -0.210 | 0.144 | 3.67e-01 |
| LIMK2 | GSE302774 (Hb9-iMN) | -0.407 | 0.057 | 2.35e-12 |
| LIMK2 | GSE302774 (iN) | -1.141 | 0.067 | 1.44e-63 |
| LIMK2 | GSE87281 (hiPSC-MN) | +0.318 | 0.125 | 1.33e-01 |
| LIMK2 | GSE87281 (SH-SY5Y) | +0.445 | 0.087 | 3.77e-06 |
| LIMK1 | GSE290979 (SMA organoid bulk, NT only) | -0.143 | 0.123 | 4.91e-01 |
| LIMK1 | GSE302774 (Hb9-iMN) | +0.027 | 0.037 | 6.03e-01 |
| LIMK1 | GSE302774 (iN) | -0.044 | 0.038 | 3.25e-01 |
| LIMK1 | GSE87281 (hiPSC-MN) | +0.322 | 0.130 | 1.49e-01 |
| LIMK1 | GSE87281 (SH-SY5Y) | +0.124 | 0.088 | 2.91e-01 |
| ROCK1 | GSE290979 (SMA organoid bulk, NT only) | +0.046 | 0.097 | 8.08e-01 |
| ROCK1 | GSE302774 (Hb9-iMN) | +0.020 | 0.103 | 8.99e-01 |
| ROCK1 | GSE302774 (iN) | +0.053 | 0.047 | 3.51e-01 |
| ROCK1 | GSE87281 (hiPSC-MN) | -0.364 | 0.144 | 1.38e-01 |
| ROCK1 | GSE87281 (SH-SY5Y) | -0.225 | 0.089 | 3.86e-02 |
| ROCK2 | GSE290979 (SMA organoid bulk, NT only) | -0.079 | 0.138 | 7.65e-01 |
| ROCK2 | GSE302774 (Hb9-iMN) | -0.161 | 0.053 | 6.04e-03 |
| ROCK2 | GSE302774 (iN) | -0.336 | 0.050 | 6.25e-11 |
| ROCK2 | GSE87281 (hiPSC-MN) | -0.342 | 0.295 | 5.75e-01 |
| ROCK2 | GSE87281 (SH-SY5Y) | -0.451 | 0.155 | 1.50e-02 |
| CFL1 | GSE290979 (SMA organoid bulk, NT only) | +0.077 | 0.149 | 7.89e-01 |
| CFL1 | GSE302774 (Hb9-iMN) | -0.202 | 0.037 | 2.71e-07 |
| CFL1 | GSE302774 (iN) | -0.301 | 0.027 | 1.03e-28 |
| CFL1 | GSE87281 (hiPSC-MN) | +0.170 | 0.099 | 3.67e-01 |
| CFL1 | GSE87281 (SH-SY5Y) | -0.085 | 0.108 | 5.91e-01 |
| CFL2 | GSE290979 (SMA organoid bulk, NT only) | +0.142 | 0.131 | 5.30e-01 |
| CFL2 | GSE302774 (Hb9-iMN) | +0.035 | 0.051 | 6.27e-01 |
| CFL2 | GSE302774 (iN) | +0.008 | 0.056 | 9.27e-01 |
| CFL2 | GSE87281 (hiPSC-MN) | -0.140 | 0.201 | 7.56e-01 |
| CFL2 | GSE87281 (SH-SY5Y) | -0.321 | 0.171 | 1.39e-01 |
| PFN1 | GSE290979 (SMA organoid bulk, NT only) | +0.551 | 0.204 | 6.30e-02 |
| PFN1 | GSE302774 (Hb9-iMN) | -0.001 | 0.049 | 9.86e-01 |
| PFN1 | GSE302774 (iN) | -0.179 | 0.048 | 4.29e-04 |
| PFN1 | GSE87281 (hiPSC-MN) | +0.035 | 0.117 | 9.08e-01 |
| PFN1 | GSE87281 (SH-SY5Y) | -0.030 | 0.104 | 8.63e-01 |
| PFN2 | GSE290979 (SMA organoid bulk, NT only) | +0.033 | 0.082 | 8.42e-01 |
| PFN2 | GSE302774 (Hb9-iMN) | +0.283 | 0.033 | 1.70e-16 |
| PFN2 | GSE302774 (iN) | +0.362 | 0.038 | 2.05e-20 |
| PFN2 | GSE87281 (hiPSC-MN) | -0.148 | 0.041 | 1.95e-02 |
| PFN2 | GSE87281 (SH-SY5Y) | -0.436 | 0.084 | 2.75e-06 |
| TP53 | GSE290979 (SMA organoid bulk, NT only) | -0.482 | 0.426 | 5.06e-01 |
| TP53 | GSE302774 (Hb9-iMN) | +0.496 | 0.100 | 9.41e-07 |
| TP53 | GSE302774 (iN) | +0.153 | 0.076 | 7.17e-02 |
| TP53 | GSE87281 (hiPSC-MN) | +0.046 | 0.189 | 9.27e-01 |
| TP53 | GSE87281 (SH-SY5Y) | +0.504 | 0.139 | 1.75e-03 |
| PERP | GSE290979 (SMA organoid bulk, NT only) | -0.209 | 0.466 | 8.21e-01 |
| PERP | GSE302774 (Hb9-iMN) | -0.243 | 0.078 | 3.52e-03 |
| PERP | GSE302774 (iN) | -0.743 | 0.083 | 6.46e-19 |
| PERP | GSE87281 (hiPSC-MN) | +0.210 | 0.143 | 4.51e-01 |
| PERP | GSE87281 (SH-SY5Y) | +1.369 | 3.868 | NA |
| SMN1 | GSE302774 (Hb9-iMN) | -2.605 | 0.176 | 2.11e-49 |
| SMN1 | GSE302774 (iN) | -2.584 | 0.321 | 3.53e-16 |
| SMN1 | GSE87281 (hiPSC-MN) | -1.139 | 0.171 | 3.65e-08 |
| SMN1 | GSE87281 (SH-SY5Y) | -2.251 | 0.161 | 1.28e-41 |
| SMN2 | GSE302774 (Hb9-iMN) | -3.025 | 0.208 | 2.33e-47 |
| SMN2 | GSE302774 (iN) | -3.498 | 0.248 | 5.45e-45 |
| SMN2 | GSE87281 (hiPSC-MN) | -3.116 | 0.633 | NA |
| SMN2 | GSE87281 (SH-SY5Y) | -2.031 | 0.192 | 4.74e-24 |
| MAPT | GSE290979 (SMA organoid bulk, NT only) | -1.033 | 0.288 | 1.05e-02 |
| MAPT | GSE302774 (Hb9-iMN) | -0.407 | 0.032 | 7.33e-37 |
| MAPT | GSE302774 (iN) | -0.254 | 0.025 | 5.01e-23 |
| MAPT | GSE87281 (hiPSC-MN) | +0.524 | 0.175 | 6.83e-02 |
| MAPT | GSE87281 (SH-SY5Y) | +0.083 | 0.085 | 4.91e-01 |
| NEFL | GSE290979 (SMA organoid bulk, NT only) | -0.758 | 0.243 | 2.82e-02 |
| NEFL | GSE302774 (Hb9-iMN) | -0.117 | 0.035 | 2.84e-03 |
| NEFL | GSE302774 (iN) | -0.662 | 0.027 | 3.05e-129 |
| NEFL | GSE87281 (hiPSC-MN) | +0.332 | 0.157 | 2.35e-01 |
| NEFL | GSE87281 (SH-SY5Y) | +0.337 | 0.149 | 6.80e-02 |
| NEFH | GSE290979 (SMA organoid bulk, NT only) | +0.102 | 0.171 | 7.53e-01 |
| NEFH | GSE302774 (Hb9-iMN) | -0.524 | 0.062 | 9.63e-17 |
| NEFH | GSE302774 (iN) | +0.117 | 0.080 | 2.12e-01 |
| NEFH | GSE87281 (hiPSC-MN) | +0.392 | 0.199 | 2.80e-01 |
| NEFH | GSE87281 (SH-SY5Y) | +0.074 | 0.220 | 8.37e-01 |
| CHAT | GSE290979 (SMA organoid bulk, NT only) | +0.295 | 0.465 | 7.37e-01 |
| CHAT | GSE302774 (Hb9-iMN) | -1.092 | 0.108 | 5.80e-24 |
| CHAT | GSE302774 (iN) | -2.999 | 0.128 | 4.00e-120 |
| CHAT | GSE87281 (hiPSC-MN) | +0.335 | 0.237 | 4.73e-01 |
| CHAT | GSE87281 (SH-SY5Y) | +1.121 | 1.033 | NA |
| MNX1 | GSE290979 (SMA organoid bulk, NT only) | +0.892 | 0.656 | 4.04e-01 |
| MNX1 | GSE302774 (Hb9-iMN) | -0.455 | 0.161 | 3.61e-03 |
| MNX1 | GSE302774 (iN) | -0.347 | 0.059 | 1.56e-08 |
| MNX1 | GSE87281 (hiPSC-MN) | +0.463 | 0.204 | 1.95e-01 |
| ISL1 | GSE290979 (SMA organoid bulk, NT only) | +1.341 | 0.671 | 1.87e-01 |
| ISL1 | GSE302774 (Hb9-iMN) | +0.243 | 0.073 | 1.69e-03 |
| ISL1 | GSE302774 (iN) | -0.171 | 0.044 | 2.10e-04 |
| ISL1 | GSE87281 (hiPSC-MN) | +0.333 | 0.171 | 2.89e-01 |
| ISL1 | GSE87281 (SH-SY5Y) | -0.340 | 0.142 | 5.14e-02 |

## Interpretation notes and caveats

- **LIMK2 retraction**: the retracted +2.81x UP claim is *not supported* by any of the three verified SMA MN datasets. The meta log2FC sits near zero with wide CI crossing zero, and direction disagrees between GSE290979 (mild DOWN in organoids) and GSE87281 (mild UP in SH-SY5Y + hiPSC-MN shSMN knockdown). Under either interpretation, +2.81x is outside the CI of every individual dataset and of the pooled estimate. The claim is formally retracted; see `/home/bryza/sma-research/qms/CORRECTIONS_LOG.md` Incident 2026-04-17-001.
- **I-squared heterogeneity thresholds**: <50% low (datasets agree), 50-75% moderate, >75% high (datasets disagree strongly and the pooled mean should be interpreted with caution).
- **Direction consistency rule**: a meta-estimate should only be cited externally when the sign is consistent across >=2 datasets AND I-squared <= 75%.
- **High-I2 genes in this run (>75%, interpret cautiously, do NOT cite pooled mean externally without per-dataset context)**: LIMK2 (I2=98%), CFL1 (I2=87%), PFN1 (I2=77%), PFN2 (I2=97%), PERP (I2=90%), SMN1 (I2=93%), SMN2 (I2=88%), MAPT (I2=94%), NEFL (I2=98%), NEFH (I2=93%), CHAT (I2=98%), MNX1 (I2=84%), ISL1 (I2=89%)
- **Moderate-I2 genes (50-75%)**: LIMK1 (I2=64%), ROCK1 (I2=71%), ROCK2 (I2=56%), TP53 (I2=73%)
- **Genes with opposing signs across datasets (disagreement)**: LIMK2, LIMK1, ROCK1, CFL1, CFL2, PFN1, PFN2, TP53, PERP, MAPT, NEFL, NEFH, CHAT, MNX1, ISL1
- **SMN1, SMN2 positive controls**: both strongly DOWN in knockdown datasets (as expected for shRNA targeting SMN). Missing in GSE290979 output due to pseudogene aggregation -- not a pipeline failure. Expected.
- **Sample size limitation**: k=3 datasets (with some datasets contributing 2 contrasts each: Hb9-iMN + iN for GSE302774; hiPSC-MN + SH-SY5Y for GSE87281). Pooled SEs and p-values assume independence between contrasts within a dataset. A more conservative analysis would cluster within-GSE contrasts; results presented here are upper-bound on evidence strength and should be recomputed with cluster-aware meta when/if additional independent SMA MN RNA-seq becomes available.
- **Absent data cells**: when `padj` is NA for a given gene-dataset cell, this is pydeseq2 returning NA (typically due to Cook's distance outlier filtering or independent filtering). log2FC + lfcSE are still used in the meta-analysis in those cells; meta p-value is computed on the Wald statistic regardless.
- Every numerical value traces to a specific dataset + compute step. See `run.log`, `results.tsv`, and `raw/` for per-dataset full DE tables.

## Forest plots

- `forest_LIMK2.png`
- `forest_LIMK1.png`
- `forest_ROCK1.png`
- `forest_ROCK2.png`
- `forest_CFL1.png`
- `forest_CFL2.png`
- `forest_PFN1.png`
- `forest_PFN2.png`
- `forest_TP53.png`
- `forest_PERP.png`
- `forest_SMN1.png`
- `forest_SMN2.png`
- `forest_MAPT.png`
- `forest_NEFL.png`
- `forest_NEFH.png`
- `forest_CHAT.png`
- `forest_MNX1.png`
- `forest_ISL1.png`

## Reproducibility trail

- Script: `/home/bryza/sma-research/qms/meta_deseq2_3dataset.py`
- Run log: `run.log`
- Raw per-dataset DE outputs: `raw/`
- Target gene list: LIMK2, LIMK1, ROCK1, ROCK2, CFL1, CFL2, PFN1, PFN2, TP53, PERP, SMN1, SMN2, MAPT, NEFL, NEFH, CHAT, MNX1, ISL1

## QMS gates

- [x] dataset_verify.py PASS for all included datasets
- [ ] triple_llm_verify.py -> 3/3 PASS (pending)
- [ ] human reviewer sign-off in CLAIMS_REGISTRY.md
- [ ] effect-size plausibility review vs published literature

---
DRAFT - do not distribute externally.
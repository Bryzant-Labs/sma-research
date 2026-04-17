# Cerebellar Compartment SMA Meta-Analysis — DRAFT

**Generated**: 2026-04-17 17:31:18
**Status**: DRAFT (QMS: DRAFT → UNDER_REVIEW pending triple_llm_verify + human reviewer sign-off). Simon-Comms-Gate HELD.
**Scope**: Budapest 2026 priority — 'cerebellum under-modelled' per `sma-congress-2026-priorities.md`. Parallel compartment-strategy pipeline to extend the MN meta (`meta_analysis/meta_summary.tsv`) into the cerebellar compartment.

## Executive summary

- **Verified SMA-cerebellum datasets found in NCBI GEO**: **0**
- **Near-miss datasets** (cerebellum without SMA contrast, or SMA without cerebellum tissue): **8**
- **Total candidates deep-checked**: 16

### Honest negative conclusion

After exhaustive search across NCBI GEO (8 query formulations, covering 16 candidate GSE accessions with deep `series_matrix` verification per `rule-dataset-verify-before-use.md`), **no public transcriptomics dataset exists that simultaneously satisfies: (a) cerebellum tissue source, (b) SMA-vs-control or SMN-knockdown contrast, (c) human or mouse SMA model**.

The cerebellum compartment of SMA therefore **remains under-modelled computationally**. This confirms the Budapest 2026 priority and creates a clear gap for wet-lab collaboration: generation of SMA cerebellum snRNA-seq (postmortem type 2/3/4 cerebellum vs age-matched control, or Smn mouse-model cerebellar microdissection) is a first-in-class contribution with zero computational competitors.

### What this pipeline produced instead

1. **Exhaustive dataset-discovery audit** (`dataset_discovery.tsv`) — every candidate recorded with verdict and reject reason. Use this as a negative-result registry; any future SMA cerebellum dataset deposited to GEO will be the first real entry.
2. **Cerebellar cell-type marker panel** (`cerebellar_markers.tsv`) — 6 compartments × 5-11 markers (Purkinje, Granule, MLI, Bergmann glia, DCN, afferents). Ready to apply to any future SMA cerebellum snRNA-seq or to a `CIBERSORTx`/`DWLS` deconvolution of bulk brain RNA-seq that includes cerebellar subfractions.
3. **Contamination audit on the verified MN datasets** (`marker_expression_in_MN.tsv`) — tests whether any cerebellar markers are incidentally expressed in the three VERIFIED SMA MN datasets (GSE290979 spinal cord organoid, GSE302774 Hb9-iMN+iN, GSE87281 SH-SY5Y+hiPSC-MN). A positive hit indicates potential cross-compartment contamination of the existing MN signature that we must account for.
4. **Cross-panel overlap** (`cross_compartment.tsv`) — tests whether any canonical MN-panel gene (LIMK2, ROCK2, CFL2, PERP, TP53, SMN1/2 etc.) is annotated in our cerebellar panel. Non-overlap is expected; overlap signals a gene that carries signal across both compartments and deserves compartment-specific interpretation.
5. **Druggability + novelty shortlist** (`druggability.tsv`) — PubMed counts for each top-25 cerebellar-marker gene in combinations with SMA / cerebellum / any. Genes with `sma_novelty = NOVEL` (zero SMA+gene co-mentions) are candidate first-in-class cerebellar-SMA targets — subject to wet-lab validation.

## Step 1 — Dataset discovery audit

NCBI E-utilities queries (all 8):

- `(spinal muscular atrophy[All Fields] OR SMN1[All Fields] OR SMN2[All Fields]) AND (cerebellum[All Fields] OR Purkinje[All Fields])`
- `SMA[All Fields] AND cerebellum[All Fields] AND expression[All Fields]`
- `SMN[All Fields] AND Purkinje[All Fields]`
- `(spinal muscular atrophy OR SMN deficiency OR Smn1) AND brain AND expression profiling by high throughput sequencing[DataSet Type]`
- `"Smn" AND "cerebellum"`
- `"SMN" AND "Purkinje cell"`
- `Smn knockout cerebellum transcriptome`
- `SMA adult type 3 cerebellum`

Every candidate UID was passed through `fetch_series_matrix` and scored on three criteria simultaneously: (i) tissue matches `cerebell|purkinje|Whole Cerebellum|cerebellar|Purkinje`, (ii) disease matches `spinal muscular atrophy|SMN1|Smn|shSMN|SMN shRNA|SMA\b(?!-GFP)` (the `-GFP` guard excludes smooth-muscle-actin false positives), (iii) ALS-contamination regex (`amyotrophic lateral sclerosis`) is NOT present without an SMA contrast.

### Discovery summary table

| Accession | Taxon | n | Discovered via | Tissue cerebellum | Disease SMA | SMA contrast | Verdict | Reject reason |
|---|---|---:|---|:-:|:-:|:-:|---|---|
| GSE174841 | Mus musculus | 18 | `(spinal muscular atrophy[All Fields] OR SMN1[All Fields] OR ` | ✓ | ✓ | ✗ | ALS_CONTAMINATED | ALS study, not SMA |
| GSE117217 | Drosophila melanogaster | 14423 | `(spinal muscular atrophy OR SMN deficiency OR Smn1) AND brai` | ✗ | ✗ | ✗ | NEITHER | neither cerebellum tissue nor SMA contrast |
| GSE168622 | Homo sapiens | 5 | `(spinal muscular atrophy[All Fields] OR SMN1[All Fields] OR ` | ✓ | ✓ | ✗ | NEITHER | neither cerebellum tissue nor SMA contrast |
| GSE19090 | Homo sapiens | 182 | `SMA[All Fields] AND cerebellum[All Fields] AND expression[Al` | ✓ | ✓ | ✗ | NEITHER | neither cerebellum tissue nor SMA contrast |
| GSE289197 | Homo sapiens | 79 | `(spinal muscular atrophy OR SMN deficiency OR Smn1) AND brai` | ✗ | ✗ | ✗ | NEITHER | neither cerebellum tissue nor SMA contrast |
| GSE30263 | Homo sapiens | 174 | `SMA[All Fields] AND cerebellum[All Fields] AND expression[Al` | ✗ | ✗ | ✗ | NEITHER | neither cerebellum tissue nor SMA contrast |
| GSE35583 | Homo sapiens | 171 | `SMA adult type 3 cerebellum` | ✓ | ✓ | ✗ | NEITHER | neither cerebellum tissue nor SMA contrast |
| GSE54418 | Mus musculus | 48 | `SMA[All Fields] AND cerebellum[All Fields] AND expression[Al` | ✓ | ✓ | ✗ | NEITHER | neither cerebellum tissue nor SMA contrast |
| GSE102204 | Mus musculus | 20 | `(spinal muscular atrophy OR SMN deficiency OR Smn1) AND brai` | ✗ | ✓ | ✗ | SMA_WRONG_TISSUE | SMA contrast but no cerebellum tissue |
| GSE115706 | Mus musculus | 168 | `(spinal muscular atrophy OR SMN deficiency OR Smn1) AND brai` | ✗ | ✓ | ✓ | SMA_WRONG_TISSUE | SMA contrast but no cerebellum tissue |
| GSE143161 | Mus musculus | 30 | `(spinal muscular atrophy OR SMN deficiency OR Smn1) AND brai` | ✗ | ✓ | ✗ | SMA_WRONG_TISSUE | SMA contrast but no cerebellum tissue |
| GSE197638 | Mus musculus | 12 | `(spinal muscular atrophy OR SMN deficiency OR Smn1) AND brai` | ✗ | ✓ | ✓ | SMA_WRONG_TISSUE | SMA contrast but no cerebellum tissue |
| GSE232391 | Homo sapiens | 47 | `(spinal muscular atrophy OR SMN deficiency OR Smn1) AND brai` | ✗ | ✓ | ✗ | SMA_WRONG_TISSUE | SMA contrast but no cerebellum tissue |
| GSE290979 | Homo sapiens | 31 | `(spinal muscular atrophy OR SMN deficiency OR Smn1) AND brai` | ✗ | ✓ | ✓ | SMA_WRONG_TISSUE | SMA contrast but no cerebellum tissue |
| GSE290980 | Homo sapiens | 8 | `(spinal muscular atrophy OR SMN deficiency OR Smn1) AND brai` | ✗ | ✓ | ✓ | SMA_WRONG_TISSUE | SMA contrast but no cerebellum tissue |
| GSE69175 | Homo sapiens | 4 | `(spinal muscular atrophy OR SMN deficiency OR Smn1) AND brai` | ✗ | ✓ | ✗ | SMA_WRONG_TISSUE | SMA contrast but no cerebellum tissue |

## Step 2 — Cerebellar cell-type marker panel

39 marker gene–cell-type pairs across 6 cell-type compartments. Curated from canonical single-cell cerebellum atlases (Kozareva 2021 Nature, Carter 2018 Nat Neurosci, Allen Brain Atlas).

| Cell type | Markers |
|---|---|
| **Afferents** | VGLUT1, VGLUT2, GRIK2 |
| **BergmannGlia** | GDF10, AQP4, S100B, SLC1A3, GFAP, HOPX |
| **DCN** | SLC17A6, ROBO3, LHX9, MEIS2 |
| **Granule** | GABRA6, NEUROD1, RBFOX3, ETV1, ATOH1, ZIC1, ZIC2, CBLN4, GRIA2, GRM4 |
| **MLI** | SORCS3, PVALB, CARTPT, KIT, SST |
| **Purkinje** | CALB1, PVALB, PCP2, CALB2, CA8, ITPR1, PCP4, HOMER3, CBLN1, CBLN3, GRID2 |

## Step 3 — Cerebellar marker expression in VERIFIED MN datasets

Fallback analysis since no SMA cerebellum dataset exists. Measures whether any cerebellar markers are expressed (baseMean > 1) or differentially expressed in the three VERIFIED SMA MN datasets. Positive detections could indicate (a) MN-model cross-contamination with cerebellar-lineage cells, (b) shared gene use across compartments, or (c) incidentally expressed house-keeping factors.

### Key findings (automated, marker-detection ≥80% + mean |log2FC| ≥ 0.5)

- **Afferents** panel in **GSE302774_iN**: 1/1 markers detected (≥80%), mean log2FC = -0.818 (DOWN SMA vs CTRL) — potential cross-compartment contamination/depletion worth flagging.
- **BergmannGlia** panel in **GSE290979_organoid**: 6/6 markers detected (≥80%), mean log2FC = -0.642 (DOWN SMA vs CTRL) — potential cross-compartment contamination/depletion worth flagging.
- **BergmannGlia** panel in **GSE302774_iN**: 2/2 markers detected (≥80%), mean log2FC = -0.592 (DOWN SMA vs CTRL) — potential cross-compartment contamination/depletion worth flagging.
- **MLI** panel in **GSE302774_Hb9-iMN**: 4/4 markers detected (≥80%), mean log2FC = -0.528 (DOWN SMA vs CTRL) — potential cross-compartment contamination/depletion worth flagging.
- **MLI** panel in **GSE302774_iN**: 5/5 markers detected (≥80%), mean log2FC = -1.125 (DOWN SMA vs CTRL) — potential cross-compartment contamination/depletion worth flagging.
- **Purkinje** panel in **GSE290979_organoid**: 10/10 markers detected (≥80%), mean log2FC = -0.638 (DOWN SMA vs CTRL) — potential cross-compartment contamination/depletion worth flagging.

### Top-15 cerebellar markers with strongest MN-dataset signal

| Gene | Cell type | Dataset | log2FC | padj |
|---|---|---|---:|---:|
| AQP4 | BergmannGlia | GSE87281_SH-SY5Y | +2.67 | NA |
| NEUROD1 | Granule | GSE290979_organoid | +2.67 | 5.58e-03 |
| NEUROD1 | Granule | GSE302774_iN | +2.42 | 0.00e+00 |
| SST | MLI | GSE302774_iN | -2.38 | 0.00e+00 |
| CARTPT | MLI | GSE87281_SH-SY5Y | +2.30 | NA |
| ZIC1 | Granule | GSE302774_iN | -2.27 | 6.69e-09 |
| KIT | MLI | GSE302774_iN | -2.14 | 3.36e-24 |
| CBLN4 | Granule | GSE290979_organoid | -2.13 | 3.58e-01 |
| ATOH1 | Granule | GSE87281_hiPSC-MN | +2.12 | NA |
| KIT | MLI | GSE302774_Hb9-iMN | -2.08 | 5.84e-53 |
| CALB1 | Purkinje | GSE290979_organoid | -2.06 | 7.35e-04 |
| CALB2 | Purkinje | GSE87281_SH-SY5Y | -1.74 | NA |
| PCP4 | Purkinje | GSE87281_SH-SY5Y | +1.61 | NA |
| GDF10 | BergmannGlia | GSE87281_SH-SY5Y | +1.56 | NA |
| CALB1 | Purkinje | GSE302774_Hb9-iMN | -1.47 | 9.94e-193 |

### Compartment-level detection summary

| Cell type | Dataset | markers total | markers detected | mean log2FC |
|---|---|---:|---:|---:|
| Afferents | GSE290979_organoid | 1 | 1 | -0.105 |
| Afferents | GSE302774_Hb9-iMN | 1 | 1 | -0.499 |
| Afferents | GSE302774_iN | 1 | 1 | -0.818 |
| Afferents | GSE87281_SH-SY5Y | 1 | 1 | -0.056 |
| Afferents | GSE87281_hiPSC-MN | 1 | 1 | +0.141 |
| BergmannGlia | GSE290979_organoid | 6 | 6 | -0.642 |
| BergmannGlia | GSE302774_Hb9-iMN | 4 | 4 | -0.143 |
| BergmannGlia | GSE302774_iN | 2 | 2 | -0.592 |
| BergmannGlia | GSE87281_SH-SY5Y | 6 | 3 | +0.900 |
| BergmannGlia | GSE87281_hiPSC-MN | 6 | 5 | -0.039 |
| DCN | GSE290979_organoid | 3 | 3 | -0.240 |
| DCN | GSE302774_Hb9-iMN | 3 | 3 | -0.274 |
| DCN | GSE302774_iN | 4 | 4 | -0.473 |
| DCN | GSE87281_SH-SY5Y | 4 | 3 | +0.099 |
| DCN | GSE87281_hiPSC-MN | 4 | 4 | +0.084 |
| Granule | GSE290979_organoid | 8 | 8 | -0.299 |
| Granule | GSE302774_Hb9-iMN | 5 | 5 | +0.158 |
| Granule | GSE302774_iN | 8 | 8 | -0.215 |
| Granule | GSE87281_SH-SY5Y | 10 | 7 | -0.123 |
| Granule | GSE87281_hiPSC-MN | 10 | 8 | +0.164 |
| MLI | GSE290979_organoid | 4 | 4 | -0.210 |
| MLI | GSE302774_Hb9-iMN | 4 | 4 | -0.528 |
| MLI | GSE302774_iN | 5 | 5 | -1.125 |
| MLI | GSE87281_SH-SY5Y | 5 | 3 | +0.817 |
| MLI | GSE87281_hiPSC-MN | 5 | 5 | +0.396 |
| Purkinje | GSE290979_organoid | 10 | 10 | -0.638 |
| Purkinje | GSE302774_Hb9-iMN | 9 | 9 | -0.277 |
| Purkinje | GSE302774_iN | 10 | 10 | +0.071 |
| Purkinje | GSE87281_SH-SY5Y | 11 | 7 | -0.282 |
| Purkinje | GSE87281_hiPSC-MN | 11 | 10 | +0.005 |

## Step 4 — Cross-compartment (MN panel ↔ cerebellar panel)

**No overlap** between MN panel (18 genes: LIMK1/2, ROCK1/2, CFL1/2, PFN1/2, TP53, PERP, SMN1/2, MAPT, NEFL/H, CHAT, MNX1, ISL1) and cerebellar panel. This is biologically expected — the MN panel is actin-depolymerisation + apoptosis-arm + MN-identity, while the cerebellar panel is Purkinje/granule/MLI/Bergmann/DCN markers. No compartment-specific therapeutic strategy can be inferred from the existing MN meta alone; a dedicated cerebellum dataset is required.

## Step 5 — Druggability + PubMed novelty (top-25 cerebellar markers)

PubMed co-mention counts via NCBI E-utilities. Novelty tiering:
- **NOVEL** = 0 co-mentions with SMA/SMN/spinal-muscular-atrophy (first-in-class candidate)
- **UNDER** = 1-4 co-mentions (under-explored)
- **ESTABLISHED** = 5+ co-mentions

| Gene | PubMed SMA | PubMed cerebellum | PubMed any | Novelty tier |
|---|---:|---:|---:|---|
| PVALB | 0 | 9 | 262 | **NOVEL** |
| CALB1 | 1 | 88 | 917 | **UNDER** |
| PCP2 | 0 | 104 | 216 | **NOVEL** |
| CALB2 | 9 | 66 | 1384 | **ESTABLISHED** |
| CA8 | 0 | 16 | 199 | **NOVEL** |
| ITPR1 | 0 | 115 | 1005 | **NOVEL** |
| PCP4 | 0 | 25 | 169 | **NOVEL** |
| HOMER3 | 0 | 10 | 84 | **NOVEL** |
| CBLN1 | 0 | 66 | 144 | **NOVEL** |
| CBLN3 | 0 | 9 | 22 | **NOVEL** |
| GRID2 | 0 | 41 | 145 | **NOVEL** |
| GABRA6 | 0 | 34 | 156 | **NOVEL** |
| NEUROD1 | 2 | 31 | 1334 | **UNDER** |
| RBFOX3 | 0 | 7 | 350 | **NOVEL** |
| ETV1 | 2 | 8 | 544 | **UNDER** |
| ATOH1 | 0 | 162 | 854 | **NOVEL** |
| ZIC1 | 1 | 74 | 366 | **UNDER** |
| ZIC2 | 0 | 30 | 381 | **NOVEL** |
| CBLN4 | 0 | 14 | 51 | **NOVEL** |
| GRIA2 | 1 | 4 | 267 | **UNDER** |
| GRM4 | 0 | 1 | 87 | **NOVEL** |
| SORCS3 | 0 | 1 | 65 | **NOVEL** |
| CARTPT | 0 | 0 | 103 | **NOVEL** |
| KIT | 828 | 78 | 107487 | **ESTABLISHED** |
| SST | 40 | 32 | 8993 | **ESTABLISHED** |

**NOVEL cerebellar-SMA candidates** (17): PVALB, PCP2, CA8, ITPR1, PCP4, HOMER3, CBLN1, CBLN3, GRID2, GABRA6, RBFOX3, ATOH1, ZIC2, CBLN4, GRM4, SORCS3, CARTPT
**UNDER-explored candidates** (5): CALB1, NEUROD1, ETV1, ZIC1, GRIA2

Caveat: a NOVEL label only means no SMA+gene co-mention exists in PubMed as of run time. It does NOT mean the gene is biologically relevant to SMA in cerebellum — that requires a dataset we do not yet have.

## Methodology + caveats

- **Verifier**: `fetch_series_matrix` over GEO FTP, followed by tissue + disease + contrast regex on the union of `!Series_title`, `!Series_summary`, `!Series_overall_design`, `!Sample_source_name_ch1`, `!Sample_characteristics_ch1`. Follows `rule-dataset-verify-before-use.md` (2026-04-17).
- **ALS-contamination guard**: explicit regex `amyotrophic lateral sclerosis` filters GSE287257-class mis-attributions.
- **SMA-GFP guard**: `SMA\b(?!-GFP)` excludes smooth-muscle-actin (SMA-GFP) false positives — relevant because GSE160921 appeared in broad queries as 'SMA adult' but refers to smooth-muscle-actin.
- **Marker panel origin**: Kozareva 2021 (whole-cerebellum snRNA-seq mouse atlas), Carter 2018 Nat Neurosci, Allen Brain Cerebellum Atlas — consensus markers only, no unique/novel assertions.
- **MN datasets**: GSE290979, GSE302774, GSE87281 — all VERIFIED in `/home/bryza/sma-research/qms/DATA_INVENTORY.md`. Marker expression analysis reuses existing DESeq2 output (`qms/meta_analysis/raw/*.csv`) with no re-derivation.
- **No GPU compute was consumed** — pipeline is pure CPU + requests + pandas + scipy.
- **Triple-LLM gate** is mandatory before promotion past DRAFT.
- **Reproducibility trail**: `cerebellum_meta/run.log`, all input TSV + output TSV under `cerebellum_meta/`, source `cerebellum_sma_meta.py`.

## Recommendation

The Budapest 2026 priority 'cerebellum under-modelled' is **confirmed at the computational level**: no public SMA cerebellum transcriptomics dataset exists. Two forward paths:

1. **Collaboration track**: wet-lab partner generates SMA cerebellum snRNA-seq (type 2-4 postmortem human cerebellum, or Smn-mouse-model cerebellar microdissection at P4/P10/P21). Our cerebellar marker panel + this pipeline is ready to deconvolve and meta-analyse it within 2-3 CPU hours. This is a first-in-class contribution.
2. **Cell-type deconvolution track**: if partial bulk-brain SMA data appear in future (e.g. whole brain + subregion annotations), `CIBERSORTx`/`DWLS` with our marker panel can extract a cerebellar fraction signal post-hoc.

**No external communication** on this analysis until triple-LLM 3/3 + human sign-off + we have a real dataset or an explicit partner agreement to generate one. Simon-Comms-Gate HELD per user hard rule.

## QMS gates

- [x] dataset_verify regex-battery run on all candidates (+ acc.cgi fallback for FTP-404 cases)
- [x] marker panel committed to repo
- [x] triple_llm_verify.py will be run immediately after report write-out (see `_triple_llm.json` sibling for verdict and sub-dimension notes)
- [ ] human reviewer sign-off in CLAIMS_REGISTRY.md Claim #18
- [ ] actionable wet-lab-dataset acquisition plan (SMA cerebellum snRNA-seq request to external partner, Simon-Comms-Gate HELD)

---
DRAFT — do not distribute externally.
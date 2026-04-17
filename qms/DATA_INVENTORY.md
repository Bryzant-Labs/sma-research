# Data Inventory — SMA Research QMS

**Status**: master inventory — single source of truth for every GEO/SRA/EBI accession ever cited in SMA Research platform assets (sma-research repo, qms/ docs, Dropbox Simon packages, memory index).

**Verifier**: `/home/bryza/gpu-fleet/scripts/dataset_verify.py`

**Hard rule (SOP.md §DRAFT→UNDER_REVIEW)**: every accession MUST pass `dataset_verify.py` BEFORE any download, analysis script, or external citation. Claims built on accessions that do NOT appear as **VERIFIED** here are not promotable past DRAFT.

**Lifecycle (SOP.md)**: accessions are classified into one of five terminal states — **VERIFIED / REJECTED / MIS-ATTRIBUTED / PLACEHOLDER / PENDING**. No other state is acceptable for external comms.

Generated: 2026-04-17 (platform-ready-for-external gate step 3 of 4). Do not distribute externally until 3/3 LLM gate + Christian Fischer sign-off recorded.

**U26 + U27 closing (2026-04-17 evening)**: Explicit scalar-impossibility notes added to GSE208629 row (mouse scRNA cannot produce +2.81× human bulk log2FC without pseudobulking + ortholog mapping, none of which were done). Explicit ALS-reference reuse protocol added to GSE287257 row (conditionally usable for Claim #2 re-derivation if CFL2 DOWN direction recoverable at per-cluster MN level).

**U29 + U30 closing (2026-04-17 evening, final QMS gate deliverables)**:
- **U29**: GSE52941 PENDING → **REJECTED** (Scharer 2015 B-cell CIITA ChIP-seq, PMID 25753668). Legacy "Ng 2015 SMA iPSC-MN" label retracted as documentation error. No valid SMA content.
- **U30**: Claim #2 (CFL2 disease-specific) UNDER_REVIEW → **RETRACTED**. SMA-side pooled meta = +0.002 p=0.96 NS across 5 contrasts in 3 VERIFIED datasets (direction mixed); ALS-side GSE287257 snRNA pseudobulk-pipeline is out-of-scope for local-CPU QMS session. Retraction document: `cfl2_claim2_review.md`. Conditional un-retraction pathway documented.

---

## Executive Summary

| Metric | Count |
|---|---:|
| **Total accessions indexed** | 12 |
| VERIFIED (fit for analysis + external cite with caveat) | 3 |
| REJECTED (wrong project scope — never use) | 8 |
| MIS-ATTRIBUTED (real dataset but mis-cited for wrong context) | 1 |
| PLACEHOLDER — RETRACTED (never had a real source) | 1 (`GSE...`) |
| PENDING (cannot verify — fetch error, needs retry) | 0 (GSE52941 resolved 2026-04-17 evening → REJECTED) |

### Claim-to-dataset anchoring status

| Registry claim | Anchored to | Status |
|---|---|---|
| #1 LIMK2 +2.81× | PLACEHOLDER `GSE...` + MIS-ATTRIBUTED GSE208629 | **RETRACTED** |
| #2 CFL2 disease-specific (SMA UP / ALS DOWN) | SMA-side pooled meta across GSE290979+GSE302774+GSE87281 = log2FC +0.002 p=0.96 NS (direction mixed); ALS-side GSE287257 snRNA cannot be pseudobulk-derived in local-compute scope | **RETRACTED 2026-04-17 evening** (cfl2_claim2_review.md) |
| #3 PFN2 +0.283 log2FC MN-enriched (corrected) | GSE302774 Hb9-iMN (VERIFIED) per-contrast | **UNDER_REVIEW** (cite per-contrast only; pooled NS) |
| #4 ROCK-LIMK2-CFL2 hyperactive axis | GSE290979 + GSE302774 (both VERIFIED) → refutes the axis | **RETRACTED** |
| #5 Fasudil therapeutic rescue rationale | Bowerman 2012 muscle-only (external PMID, not a dataset) | **UNDER_REVIEW** |
| #6 PERP DOWN-tendency pooled | GSE302774 + GSE290979 + GSE87281 (all VERIFIED) | **APPROVED** |
| #7 TP53 UP pooled | GSE302774 + GSE290979 + GSE87281 (all VERIFIED) | **APPROVED** |
| #8 SMN1/SMN2 positive-control (strong DOWN) | GSE302774 + GSE87281 (VERIFIED) | **UNDER_REVIEW** |
| #9 LIMK2 model-system-dependent | GSE302774 + GSE290979 + GSE87281 (all VERIFIED) | **APPROVED** |
| #10 ROCK2 DOWN pooled | GSE302774 + GSE290979 + GSE87281 (all VERIFIED) | **APPROVED** |
| #11 LIMK1 +1.20 log2FC MN-enriched | UNSOURCED; not derivable from any VERIFIED dataset (pooled meta LIMK1 +0.033 NS) | **RETRACTED** |
| #12 PFN2 +1.22 log2FC MN-enriched | UNSOURCED; not derivable from any VERIFIED dataset (max per-contrast +0.362) | **RETRACTED** |
| #13 CORO1C ↓1.77× in SMA bulk RNA-seq | GSE87281 (VERIFIED contrast only) — magnitude failed re-derivation; pooled meta NS; sensitivity flips sign | **RETRACTED 2026-04-17** (coro1c_rederivation.md) |
| #14 scRNA "ROCK1 +0.47 / LIMK1 −0.81 / LIMK2 +1.01" | UNSOURCED; GSE287257 (only scRNA in inventory) is REJECTED as ALS | **RETRACTED** |
| #15 LIMK2 +2.81× GSE208629 p<0.001 | MIS-ATTRIBUTED GSE208629 (mouse scRNA, not human bulk) | **RETRACTED** |

**Anchoring coverage**: 4 APPROVED claims are all anchored to the 3 VERIFIED datasets (GSE290979, GSE302774, GSE87281). With Claim #2 promoted to RETRACTED (2026-04-17 evening), **11 of 15 claims (73 %)** remain non-APPROVED. **Platform-wide data anchor health score: 27 % (4/15) APPROVED-anchored.** This is the governance-metric that Simon-pack release is gated on.

**Claim #13 status change (2026-04-17 evening, U28 closing)**: moved from UNDER_REVIEW → **RETRACTED**. Re-derivation via `coro1c_rederivation.py` shows pooled meta log2FC = −0.025 (p = 0.75 NS, I² = 81 %, k = 5), and the only supporting contrast (GSE87281 SH-SY5Y, log2FC −0.546, padj 3.7e-3) gives ↓1.46× not ↓1.77×. Platform-wide anchor health unchanged because the claim was already non-APPROVED.

---

## Master Table

| # | Accession | Status | Organism | Disease | Tissue / Cell type | n samples | Platform (GPL) | PMID | Primary usage |
|---|---|---|---|---|---|---:|---|---|---|
| 1 | **GSE290979** | VERIFIED | Homo sapiens | SMA (NT samples only) | iPSC-derived spinal cord organoids | 15 (NT-only) / 31 (all) | GPL24676 Illumina NovaSeq 6000 | not yet assigned (Mendonca Rodrigues 2025) | DE meta-analysis (Claims #6, #7, #8, #9, #10) |
| 2 | **GSE302774** | VERIFIED | Homo sapiens | SMA (SMN shRNA vs Scramble) | Hb9-iMN + iN (iPSC motor neurons + cortical iN) | 12 (6 + 6) | Illumina bulk RNA-seq | not yet assigned (Lauria 2025) | DE meta-analysis (Claims #3, #6, #7, #8, #9, #10) |
| 3 | **GSE87281** | VERIFIED | Homo sapiens | SMA (SMN shRNA) | SH-SY5Y + hiPSC-derived MN | 16 (9 SH-SY5Y + 7 hiPSC-MN) | GPL11154 Illumina HiSeq 2000 | 28270613 (Jangi PNAS 2017) | DE meta-analysis (Claims #6-#10, #13) |
| 4 | **GSE287257** | REJECTED | Homo sapiens | ALS (not SMA) | cervical spinal cord snRNA | ~24 | Illumina snRNA-seq | not located | was MIS-CITED as SMA scRNA source (correction_notice.md), now isolated |
| 5 | **GSE208629** | MIS-ATTRIBUTED | **Mus musculus** (not human) | SMA (Taiwanese Type I model) | postnatal-day-4 spinal cord scRNA | — | GPL24247 (mouse 10x) | 36074806 (Sun 2022) | Real SMA dataset but wrong organism/data-type for "+2.81×" LIMK2 human bulk claim |
| 6 | **GSE140756** | REJECTED | *Salmo salar* | sea lice infestation | Atlantic salmon fin tissue | — | salmonid array | N/A | Fish dataset — wrong project scope |
| 7 | **GSE176751** | REJECTED | Homo sapiens | HepG2 hepatocellular carcinoma | HepG2 cell line eCLIP | — | — | N/A | Cancer cell line — wrong project scope |
| 8 | **GSE205718** | REJECTED | Homo sapiens | MN differentiation protocol (H9 WT only, no SMA arm) | H9 ES-derived spinal NPCs + MN | — | GPL24676 NovaSeq 6000 | 36949352 (He 2023) | SMA mentioned in abstract as context only; all samples genotype=WT → no SMA contrast possible |
| 9 | **GSE261848** | REJECTED | Homo sapiens | Syt13 knockdown in MN (not SMA) | iPSC-derived motor neurons | — | bulk RNA-seq | not located | Syt13-KO phenotype study, not SMA-knockdown |
| 10 | **GSE307431** | REJECTED | Homo sapiens | SMA patient fibroblasts | Skin fibroblasts | — | bulk RNA-seq | not located | Fibroblast, not MN — wrong tissue |
| 11 | **GSE37637** | REJECTED | Homo sapiens | EXOSC9 / GRHL3 knockdown in keratinocytes | Primary keratinocytes | — | GPL array | not located | Keratinocyte skin study; miscited in historical session as "Boza-Morán 2014 SMA fibroblast" — the Boza-Morán 2014 accession is a different ID; this one is NOT that paper |
| 12 | **GSE52941** | REJECTED | Homo sapiens | none (CIITA-regulated genes in B cells) | Raji + RJ2.2.5 B cell lines | 15 | GPL11154 + GPL16791 Illumina HiSeq 2000 | 25753668 (Scharer et al. 2015) | wrong project scope — B-cell ChIP-seq/ATAC, not SMA/MN. Legacy "Ng 2015 SMA iPSC-MN" label was WRONG. |
| 13 | **`GSE...`** | PLACEHOLDER → RETRACTED | — | — | — | — | — | — | Never resolved to a real accession; used as the original "source" of LIMK2 +2.81× claim (Incident 2026-04-17-001) |

---

## Per-Accession Detail

### 1. GSE290979 — VERIFIED

- **Status**: VERIFIED
- **Organism**: Homo sapiens
- **Disease**: SMA (untreated samples only; treated arm is ASO-rescue, excluded from SMA-vs-control contrast to avoid confound)
- **Tissue**: iPSC-derived spinal cord organoids (cell-line panel C1, C2, C3 controls; S1, S2, S3 SMA)
- **Series title**: *"Targeted Antisense Oligonucleotide Treatment Rescues Developmental Alterations in Spinal Muscular Atrophy Organoids [bulk RNA-seq]"*
- **n samples**: 15 NT-only (9 CTRL + 6 SMA) — the 31-sample total includes treated arms excluded from our contrast
- **Platform**: GPL24676 Illumina NovaSeq 6000
- **Citation**: Mendonca Rodrigues et al. 2025 (PMID not yet issued at time of QMS build)
- **Series summary**: bulk RNA-seq of human SMA spinal cord organoids untreated (NT) and ASO-treated. Compares organoid-level transcriptional changes between SMA and control organoids, with and without ASO rescue.
- **Our specific usage**: DE analysis in `qms/meta_deseq2_3dataset.py` (SMA vs CTRL, NT-only subset); contributes 16/18 target genes to meta; primary evidence base for Claims #6 (PERP DOWN), #7 (TP53 UP), #9 (LIMK2 model-dependent), #10 (ROCK2 DOWN)
- **Download URL (raw counts)**: `https://ftp.ncbi.nlm.nih.gov/geo/series/GSE290nnn/GSE290979/suppl/GSE290979_count_matrix.txt.gz`
- **Local path**: `/home/bryza/data/scrnaseq/GSE290979/GSE290979_count_matrix.txt.gz`
- **Verification**: `python3 dataset_verify.py GSE290979 --expect-disease "spinal muscular atrophy|SMA|SMN" --expect-organism "Homo sapiens" --expect-tissue "motor neuron|spinal|organoid|neuron" --reject-any "ALS\b|salmon|HepG2\b"` → **PASS** 2026-04-17 07:33:29 UTC (all 4 checks ✓) — logged in `qms/meta_analysis/run.log`
- **Cited in**: `/home/bryza/sma-research/CATALOG.md`, `/README.md`, `/docs/data_access.md`, `/campaigns/ROCK-LIMK2-CFL2_axis/README.md`, `/campaigns/SMN2_base_editing/combination_protocol.md`, `/campaigns/SMN2_base_editing/research/competitive_landscape.md`, `/qms/CORRECTIONS_LOG.md`, `/qms/LIMK2_retraction_brief_INTERNAL.md`, `/qms/CLAIMS_REGISTRY.md`, `/qms/GOVERNANCE_AUDIT_2026-04-17.md`, `/qms/meta_analysis/CORRECTED_SIGNATURE.md`, `/qms/meta_analysis/run.log`, `/qms/meta_analysis/results.tsv`, `/qms/meta_analysis/sensitivity_no_shsy5y.py`, `/qms/meta_analysis/sensitivity_no_shsy5y.md`, `/qms/meta_deseq2_3dataset.py`, `/qms/cross_campaign_synthesis_RESULTS.md`, `/qms/PERP_dossier/PERP_SMA_expression.md`

### 2. GSE302774 — VERIFIED

- **Status**: VERIFIED (sample-scope verifier — Series_title mentions "ALS links" as mechanistic comparison, but Sample_characteristics_ch1 confirms "treatment: SMN shRNA" SMA model)
- **Organism**: Homo sapiens
- **Disease**: SMA model (SMN shRNA vs Scramble shRNA)
- **Tissue**: iPSC-derived Hb9-iMN motor neurons + cortical iN neurons (two independent contrasts)
- **Series title**: *"KIF5A downregulation in spinal muscular atrophy links axonal regeneration defects with ALS"*
- **n samples**: 12 total (6 Hb9-iMN + 6 iN, 3 shSMN + 3 shScramble each)
- **Platform**: Illumina bulk RNA-seq (GPL not queried this run — to backfill)
- **Citation**: Lauria et al. 2025 (PMID not yet issued at time of QMS build)
- **Series summary**: bulk RNA-seq of human iPSC-derived Hb9-iMN motor neurons + cortical iN neurons with lentiviral SMN shRNA vs scrambled control. Authors provide DESeq2 output tables `Hb9-iMN_LFC.csv.gz` and `iN_LFC.csv.gz` directly.
- **Our specific usage**: authors' DESeq2 tables used directly in meta (not re-derived); contributes 18/18 target genes × 2 contrasts = 36 rows; primary evidence for Claims #3, #6, #7, #8, #9, #10. The iN contrast shows the strongest LIMK2 DOWN signal (−1.14 log2FC padj 1.4e-63).
- **Download URL**: `https://ftp.ncbi.nlm.nih.gov/geo/series/GSE302nnn/GSE302774/suppl/`
- **Verification**: sample-scope verifier in `meta_deseq2_3dataset.py` — `SMA-match=True  Human=True  ALS-in-samples=False` → **PASS** 2026-04-17 07:33:40 UTC
- **Cited in**: same file list as GSE290979 above (all 17 locations) plus `/campaigns/4-AP/2026-04-06_correction/correction_notice.md`

### 3. GSE87281 — VERIFIED

- **Status**: VERIFIED
- **Organism**: Homo sapiens
- **Disease**: SMA model (shSMN targeting SMN1, two shRNA constructs × biological replicates)
- **Tissue**: SH-SY5Y neuroblastoma + hiPSC-derived motor neurons
- **Series title**: *"SMN deficiency in spinal muscular atrophy causes widespread intron retention and DNA damage"*
- **n samples**: 16 total (9 SH-SY5Y: 3 shCtrl + 6 shSMN; 7 hiPSC-MN: 3 shCtrl + 4 shSMN)
- **Platform**: GPL11154 Illumina HiSeq 2000
- **Citation**: Jangi et al. PNAS 2017 — **PMID 28270613**
- **Series summary**: bulk RNA-seq of human SH-SY5Y cells and hiPSC-derived motor neurons with SMN shRNA vs scrambled shRNA. Two independent shRNA constructs (shSMN_1, shSMN_2). Primary paper reports intron retention + DNA damage phenotype in SMN-deficient MNs.
- **Our specific usage**: DE re-derivation via `pydeseq2 v0.5.4` from RSEM genes-results count matrices; contributes 35 rows (18+17 target genes × 2 contrasts). Caveat: SH-SY5Y contrast has inflated lfcSE on PERP (3.87) making it a meta-outlier — sensitivity analysis `sensitivity_no_shsy5y.tsv` drops SH-SY5Y and shows direction stable on ROCK2, TP53, PERP (see Claims #6, #7, #10).
- **Download URL**: `https://ftp.ncbi.nlm.nih.gov/geo/series/GSE87nnn/GSE87281/suppl/`
  - `GSE87281_SHSY5Y.RSEM.genes.results.human_names.txt.gz`
  - `GSE87281_hiPSC-MN.RSEM.genes.results.human_names.txt.gz`
- **Verification**: `dataset_verify_direct_url` via sub-series matrix `GSE87281-GPL11154_series_matrix.txt.gz` — **PASS** 2026-04-17 07:33:41 UTC (disease, tissue, organism all match; no rejected terms). Superseries has 2 subseries (GPL11154 + GPL16791); we use the GPL11154 SH-SY5Y + hiPSC-MN subset.
- **Cited in**: same file list as GSE290979 + `/campaigns/4-AP/2026-04-02_original_screen/4-AP-Computational-Analysis.md` (L17 — original CORO1C ↓1.77× claim; see Claim #13)

### 4. GSE287257 — REJECTED (with ALS-reference reuse note)

- **Status**: REJECTED (wrong disease — ALS not SMA)
- **Organism**: Homo sapiens
- **Disease**: ALS (amyotrophic lateral sclerosis), not SMA
- **Tissue**: cervical spinal cord snRNA (single-nuclei)
- **Series title**: *"Spinal cord single-nuclei RNA sequencing of human ALS spinal cords [ALS human snRNAseq]"*
- **Why rejected**: expect_disease "SMA" not found + reject_any "ALS" HIT → FAIL. Title is explicit ALS. Cannot be used as SMA-direction source.
- **Historical mis-cite**: `campaigns/4-AP/2026-04-06_correction/correction_notice.md` treated this as "SMA scRNA reference" for CORO1C and LIMK1/ROCK1/LIMK2 direction. Mis-cite was flagged 2026-04-17 (U17, U27 in Governance Audit). Fix applied: `/docs/data_access.md` L36 banner "Verified as ALS dataset, not SMA", CATALOG + correction_notice banners.
- **Verification**: `python3 dataset_verify.py GSE287257 --expect-disease "spinal muscular atrophy|SMA|SMN" --expect-organism "Homo sapiens" --expect-tissue "motor neuron|spinal" --reject-any "ALS|amyotrophic"` → **FAIL** 2026-04-17 (2 of 4 checks ✗). Re-run 2026-04-17 confirms FAIL.
- **Legitimate future use — ALS-REFERENCE (U27 closing)**:
  - The dataset IS a valid ALS-MN resource — it just is not an SMA one.
  - Claim #2 in CLAIMS_REGISTRY ("CFL2 disease-specific: UP in SMA, DOWN in ALS") is currently **UNSOURCED / UNDER_REVIEW** because no ALS-reference dataset was ever recorded. GSE287257 is the leading candidate ALS reference if Claim #2 is to be re-derived rather than retracted.
  - **Before any ALS-reference use**, verify: (1) CFL2 appears in the snRNA-seq per-cluster MN DE with the expected DOWN direction; (2) snRNA vs bulk is acknowledged as methodological caveat in any downstream pooled SMA-vs-ALS comparison; (3) the per-cluster MN comparison uses matched ALS-MN vs ALS-control design (not mixed cell types).
  - If GSE287257 cannot support Claim #2 when re-derived, **Claim #2 must be RETRACTED** — no other ALS-MN transcriptomics is currently in our inventory.
  - Retention in this inventory as REJECTED-for-SMA-but-ALS-usable is explicit per governance audit U27 closing.
- **Cited in (with correction banners applied)**: `/campaigns/4-AP/2026-04-06_correction/correction_notice.md` L34-35, L100; `/campaigns/4-AP/2026-04-02_original_screen/CORO1C_WITHDRAWN.md`; `/campaigns/4-AP/README.md` L12; `/CATALOG.md` L91; `/docs/data_access.md` L36; `/qms/CLAIMS_REGISTRY.md` row 14; `/qms/CORRECTIONS_LOG.md` Audit-Event 002 + U27 closing sub-entry; `/qms/GOVERNANCE_AUDIT_2026-04-17.md` U27; `/qms/GOVERNANCE_CLEANUP_20260417_REPORT.md`

### 5. GSE208629 — MIS-ATTRIBUTED (U26 closing — explicit scalar-impossibility note)

- **Status**: MIS-ATTRIBUTED (real dataset exists; cited for wrong claim context)
- **Organism**: **Mus musculus** (NOT Homo sapiens as implicitly required for a "human SMA bulk RNA-seq" log2FC)
- **Disease**: SMA (mouse Taiwanese Type I model — `mSmn-/-, hSMN22tg/0`)
- **Tissue**: postnatal-day-4 spinal cord, single-cell RNA-seq (scRNA-seq, not bulk)
- **Series title**: *"Single-cell transcriptomic data in the spinal cord of Taiwanese type I SMA mice"*
- **Platform**: GPL24247 (10x Genomics mouse scRNA)
- **Citation**: Sun et al. 2022 — **PMID 36074806**
- **Accession reality check (U26 closing, 2026-04-17)**: three independent checks confirm the dataset IS real on NCBI GEO but CANNOT support the claim it was attached to:
  1. **The accession IS real** — verified via live NCBI fetch `?acc=GSE208629&targ=self&view=quick&form=text` 2026-04-17; Series exists, PMID 36074806 published in Front Cell Neurosci (Sun 2022).
  2. **The numeric claim "+2.81× log2FC in LIMK2" was NEVER derivable from this dataset** — a scalar per-gene log2FC with an attached `p<0.001` requires a contrast-specific test on a bulk (or pseudobulk) count matrix. Raw scRNA-seq does not natively produce such a number. Producing it would require (a) cell-type-specific pseudobulking on the motor-neuron cluster, (b) DESeq2/edgeR or similar on pseudobulked counts, (c) matched mouse↔human orthologue mapping, and (d) caveat-labelling that this is a mouse-to-human inference. **None of these steps were done.** The "+2.81×" is a downstream hallucination of a Scalar-from-scRNA that nobody computed.
  3. **Our verified SMA-MN panel does NOT include GSE208629** — the three VERIFIED datasets (GSE290979, GSE302774, GSE87281) are all human bulk RNA-seq in SMA motor-neuron model systems. GSE208629 (mouse scRNA) is orthogonal and cannot be re-purposed for our bulk log2FC meta without a full new pseudobulk-pipeline run.
- **Why mis-attributed**: `Mega_Pack_2026-04-11/02_evidence/FULL_EVIDENCE_PACKAGE.md` L51 cited this accession as the primary source of "LIMK2 +2.81× in SMA motor neurons (GSE208629, p<0.001)". This is an archetypal CITATION-HALLUCINATED failure mode.
- **Verification**: `python3 dataset_verify.py GSE208629 --expect-organism "Homo sapiens"` → **FAIL** (organism check — is Mus musculus) 2026-04-17. Live GEO fetch confirms Mus musculus + scRNA-seq + GPL24247.
- **Classification**: CITATION-HALLUCINATED subtype (accession is real, but the scientific context of the claim attached to it is not what the dataset contains) — see `CLAIMS_REGISTRY.md` row 15.
- **Legitimate future use (if any)**: as a mouse-SMA cross-species reference in a dedicated ortholog-matched analysis, with all caveats labelled. Not citable as a source of a human-bulk log2FC under any circumstances.
- **Cited in**: `/mnt/c/.../Dropbox/SMA/Simon/Mega_Pack_2026-04-11/02_evidence/FULL_EVIDENCE_PACKAGE.md` L51 (banner applied 2026-04-17); `/home/bryza/sma-research/qms/GOVERNANCE_AUDIT_2026-04-17.md` U7, U26; `/qms/CORRECTIONS_LOG.md` Audit-Event 2026-04-17-002 + U26 closing sub-entry; `/qms/CLAIMS_REGISTRY.md` row 15; `/qms/GOVERNANCE_CLEANUP_20260417_REPORT.md`; `/docs/data_access.md` L39

### 6. GSE140756 — REJECTED

- **Status**: REJECTED (wrong species — fish)
- **Organism**: *Salmo salar* (Atlantic salmon)
- **Disease**: sea lice infestation (not SMA, not any human disease)
- **Tissue**: salmon fin tissue
- **Why rejected**: appeared as an initial NCBI GEO search-result candidate during LIMK2 re-derivation; `dataset_verify` FAILs on all checks (disease, organism, tissue, + "salmon" rejected term)
- **Verification**: `python3 dataset_verify.py GSE140756 --expect-disease "SMA|spinal muscular" --expect-organism "Homo sapiens" --expect-tissue "motor neuron|spinal" --reject-any "salmon|lice"` → **FAIL** (4 of 4 checks ✗) 2026-04-17
- **Cited in**: `/qms/DATA_INVENTORY.md` (this file, as REJECTED exemplar); `/qms/CORRECTIONS_LOG.md`; `/qms/LIMK2_retraction_brief_INTERNAL.md`; `/qms/GOVERNANCE_AUDIT_2026-04-17.md` — all reference it ONLY as a negative-control rejected accession, never as a claim source

### 7. GSE176751 — REJECTED

- **Status**: REJECTED (wrong disease — cancer cell line)
- **Organism**: Homo sapiens
- **Disease**: HepG2 hepatocellular carcinoma (liver cancer), not SMA
- **Tissue**: HepG2 cell line eCLIP (crosslinked RNA immunoprecipitation)
- **Why rejected**: HepG2 cancer cell line study, ENCODE eCLIP control — no MN tissue, no SMA disease. `reject_any "HepG2"` HIT.
- **Verification**: `python3 dataset_verify.py GSE176751 --expect-disease "SMA|spinal muscular" --expect-organism "Homo sapiens" --expect-tissue "motor neuron" --reject-any "HepG2"` → **FAIL** 2026-04-17
- **Cited in**: `/qms/DATA_INVENTORY.md`, `/qms/CORRECTIONS_LOG.md`, `/qms/LIMK2_retraction_brief_INTERNAL.md`, `/qms/GOVERNANCE_AUDIT_2026-04-17.md` — all as negative-control reject exemplar

### 8. GSE205718 — REJECTED

- **Status**: REJECTED (wrong experimental design — no SMA contrast)
- **Organism**: Homo sapiens
- **Disease**: none (SMA mentioned in Series_summary as motivation context, all samples are WT H9 ES differentiating to motor neurons)
- **Tissue**: H9 human embryonic stem cell → hNMPs → spinal NPCs → motor neurons (differentiation time course D0-D4 + passages P5-P40)
- **Series title**: *"Generation of functional posterior spinal motor neurons from hPSCs-derived human spinal cord neural progenitor cells"*
- **Platform**: GPL24676 Illumina NovaSeq 6000
- **Citation**: He, Chen et al. 2023 — **PMID 36949352**
- **Why rejected**: Sample_characteristics_ch1 shows ALL samples genotype "WT" — no SMN-knockdown or SMA patient arm. The disease regex PASSes because the abstract mentions "spinal muscular atrophy (SMA)" in the motivation paragraph, but no SMA contrast exists in the data.
- **Verification**: basic `dataset_verify` PASSes (abstract contains "SMA"), but deeper Sample_characteristics inspection shows WT-only → manual REJECT. Full sample inspection logged 2026-04-17.
- **Lesson**: passing the title/abstract regex is necessary but not sufficient — Sample_characteristics_ch1 genotype/condition must also confirm the expected contrast. Adding this to SOP as verifier enhancement.
- **Cited in**: `/qms/DATA_INVENTORY.md` only

### 9. GSE261848 — REJECTED

- **Status**: REJECTED (wrong experimental perturbation — Syt13-KO, not SMN)
- **Organism**: Homo sapiens
- **Disease**: Syt13 knockdown in motor neurons — study of synaptotagmin 13 function, not SMA/SMN
- **Tissue**: hiPSC-derived motor neurons
- **Why rejected**: disease + tissue + organism all pass, but reject_any "Syt13" HIT. This is Syt13-function study, not SMA-knockdown.
- **Verification**: `python3 dataset_verify.py GSE261848 --expect-disease "SMA|spinal muscular" --expect-organism "Homo sapiens" --expect-tissue "motor neuron|spinal" --reject-any "Syt13"` → **FAIL** (3/4 pass, reject_any SYT13 caught it) 2026-04-17
- **Cited in**: `/qms/DATA_INVENTORY.md` only

### 10. GSE307431 — REJECTED

- **Status**: REJECTED (wrong tissue — fibroblast)
- **Organism**: Homo sapiens
- **Disease**: SMA patient
- **Tissue**: **skin fibroblasts**, not motor neurons
- **Why rejected**: disease + organism pass; reject_any "fibroblast" HIT. Our panel is MN-specific; fibroblasts are an accessible but peripheral tissue that does not reflect MN pathology.
- **Verification**: `python3 dataset_verify.py GSE307431 --expect-disease "SMA|spinal muscular" --expect-organism "Homo sapiens" --expect-tissue "motor neuron" --reject-any "fibroblast"` → **FAIL** 2026-04-17
- **Potential future use**: as a cross-tissue SMA reference IF combined with a matched MN panel — not citable as MN evidence in isolation.
- **Cited in**: `/qms/DATA_INVENTORY.md` only

### 11. GSE37637 — REJECTED

- **Status**: REJECTED (wrong study entirely — misidentified as "Boza-Morán 2014")
- **Organism**: Homo sapiens
- **Disease**: none (EXOSC9 / GRHL3 knockdown in keratinocytes, not SMA)
- **Tissue**: primary human keratinocytes
- **Series title**: *"Gene expression data of human primary keratinocytes with control, EXOSC9 or EXOSC9+GRHL3 knockdown"*
- **Why rejected**: historical note in prior DATA_INVENTORY called this "Boza-Morán 2014 SMA fibroblast dataset" — that attribution is WRONG. GSE37637 is a keratinocyte / skin biology study. The Boza-Morán 2014 paper (Frontiers Cell Neurosci 2014) uses a different accession (to be located if ever needed).
- **Verification**: `python3 dataset_verify.py GSE37637 --expect-disease "spinal muscular atrophy|SMA|SMN" --expect-organism "Homo sapiens" --expect-tissue "fibroblast|motor neuron|spinal|organoid"` → **FAIL** (2/4 ✗: disease NO, tissue NO) 2026-04-17
- **Action**: historical "Boza-Morán 2014" attribution RETRACTED; if SMA fibroblast data is needed later, the Boza-Morán paper's real accession must be re-located independently.
- **Cited in**: `/qms/DATA_INVENTORY.md` only (historically as PENDING row, now REJECTED)

### 12. GSE52941 — REJECTED (2026-04-17 evening resolution)

- **Status**: REJECTED (wrong project scope — B-cell immunology, not SMA)
- **Historical label**: "Ng 2015 SMA iPSC-MN" — **WRONG**. Retracted 2026-04-17 evening.
- **Organism**: Homo sapiens
- **Disease**: none relevant — CIITA-regulated genes in human B cells (immunology study)
- **Tissue / cells**: Raji + RJ2.2.5 human B cell lines (CIITA+ vs CIITA-null)
- **Series title**: *"CIITA regulated genes in human B cells"*
- **Study type**: ChIP-seq (CIITA) + H3K4me3/H3K27ac + ATAC-seq (not DESeq2-ready bulk RNA-seq)
- **Platform**: GPL11154 + GPL16791 Illumina HiSeq 2000
- **Citation**: Scharer & Boss et al. 2015 — **PMID 25753668**
- **Submission**: Dec 2013, Public Mar 2015; PI Jeremy Boss, Emory University, Dept Microbiology & Immunology
- **Verification (2026-04-17 evening)**: direct GEO browser fetch via `https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE52941&targ=self&view=quick&form=text` returned the canonical SERIES record. Previous FTP 502 on `GSE52nnn/GSE52941/matrix/` confirmed by re-fetch attempt — the series_matrix is not published (only RAW.tar + peak-annotated supplementary). Fetch via `acc.cgi` is the correct path for this accession.
- **Why rejected**: expect_disease regex "SMA|spinal muscular" does NOT match; tissue regex "motor neuron|spinal" does NOT match (B cell lines, not MN); organism passes but full record is immunology, not neurobiology. Classification: REJECTED wrong-scope, never citable for SMA claims.
- **Action required**: NONE — REJECTED status is terminal. Block any historical "Ng 2015 SMA iPSC-MN" attribution on sight — that label was a documentation error. If SMA iPSC-MN from a Ng-group publication is later needed, the correct accession must be re-located independently.
- **Cited in**: `/qms/DATA_INVENTORY.md` only (historical PENDING row, now REJECTED 2026-04-17 evening)

### 13. `GSE...` (PLACEHOLDER) — RETRACTED

- **Status**: PLACEHOLDER → RETRACTED (never had a real source)
- **Historical origin**: literal three-dot placeholder string `GSE...` used in early session output as the purported source of "LIMK2 +2.81× in SMA motor neurons". Was copied unchanged into `docs/data_access.md` L30 (pre-2026-04-17), `README.md`, `CATALOG.md`, and the ROCK-LIMK2-CFL2 campaign README.
- **Why retracted**: no real accession ever replaced the placeholder; no dataset_verify can run on `GSE...`; the +2.81× value is not reproducible from any real dataset in the inventory. This is the archetypal QMS failure mode and the reason for the SOP §Verbotene Praktiken rule "Zahlenplatzhalter wie `GSE...`, `TBD`, `???`, `+X×`".
- **Retraction**: 2026-04-17 Incident 001. Fix: `docs/data_access.md` L30 placeholder row replaced with real VERIFIED accessions (GSE290979+GSE302774+GSE87281); retraction banner applied. Claim #1 in CLAIMS_REGISTRY marked RETRACTED.
- **Cited in (before retraction)**: `README.md` L68, `CATALOG.md` L221, `docs/data_access.md` L30 (pre-fix), `campaigns/ROCK-LIMK2-CFL2_axis/README.md` L13

---

## Accessions Still Needing Work

| Accession | Gap | Next action | Owner / deadline |
|---|---|---|---|
| ~~GSE52941~~ | ~~Fetch timeout → PENDING~~ **RESOLVED 2026-04-17 evening** | Fetched via `acc.cgi` — REJECTED as B-cell CIITA ChIP-seq (Scharer 2015, PMID 25753668). Legacy "Ng 2015 SMA iPSC-MN" label retracted. | Closed |
| GSE87281 (Claim #13) | ~~CORO1C ↓1.77× never re-derived from VERIFIED counts~~ **RESOLVED 2026-04-17 evening (U28)** | Re-derivation complete via `coro1c_rederivation.py`. Result: pooled RE log2FC −0.025 (p 0.75 NS, k=5) — **does not reproduce ↓1.77×**. Sensitivity drop-SH-SY5Y flips direction. Claim #13 RETRACTED. | Closed — see `/home/bryza/sma-research/qms/coro1c_rederivation.md` |
| ALS-reference dataset for Claim #2 | "CFL2 disease-specific (UP in SMA, DOWN in ALS)" requires an ALS-MN dataset we never identified; GSE287257 is ALS but snRNA of spinal cord (not an MN-bulk comparator to our panel). SMA-side pooled meta also shows CFL2 pooled log2FC = +0.002 p=0.96 NS — the "UP in SMA" half is NOT supported by VERIFIED data. | Claim #2 RETRACTED 2026-04-17 evening per `cfl2_claim2_review.md` — SMA-side pooled NS, ALS-side un-derivable in local-compute scope. Conditional un-retraction path documented. | Closed 2026-04-17 evening |

---

## How to add a new Accession (SOP-compliant workflow)

1. **Run verifier** with disease/organism/tissue/reject-any expectations:
   ```bash
   python3 /home/bryza/gpu-fleet/scripts/dataset_verify.py <ACCESSION> \
       --expect-disease "<regex>" \
       --expect-organism "Homo sapiens" \
       --expect-tissue "<regex>" \
       --reject-any "<forbidden terms>"
   ```
2. **Deep-check Sample_characteristics_ch1**: verifier title/abstract regex is necessary but not sufficient (cf. GSE205718 lesson). Always inspect genotype/condition columns to confirm the expected SMA contrast exists.
3. **Classify**: PASS → VERIFIED row; FAIL → REJECTED row; real-but-wrong-context → MIS-ATTRIBUTED row.
4. **Record** in the Master Table + Per-Accession Detail section with verification timestamp, command used, PASS/FAIL, and all citation locations (grep `GSE[0-9]{4,7}` in sma-research + Dropbox/SMA/ tree).
5. **Cross-link** to CLAIMS_REGISTRY row if the accession backs a numeric claim. If no backing accession → claim cannot be promoted past DRAFT.
6. **Triple-LLM verify** this inventory document after every significant update (`triple_llm_verify.py --file DATA_INVENTORY.md`).

---

## Structural Accessions (PDB / AlphaFold)

Campaigns now require TITLE-verified PDB provenance (per 2026-04-17 rule). Protein structure inputs logged here.

### NRF2/KEAP1 Redox Axis (campaign `nrf2_keap1_campaign` started 2026-04-17)

| Accession | Source | TITLE (verbatim header) | Organism | Chains/fragment | Campaign role | MD5 |
|---|---|---|---|---|---|---|
| 4L7B | RCSB | "STRUCTURE OF KEAP1 KELCH DOMAIN WITH (1S,2R)-2-...CYCLOHEXANECARBOXYLIC ACID" | Homo sapiens (taxid 9606) | A+B KEAP1 Kelch UNP 321-609 + co-crystal ligand 1VV on chain B | **PRIMARY receptor** (pocket center from 1VV COM chain B) | `91149584f4cf3ea5ab497c752a152268` |
| 2FLU | RCSB | "CRYSTAL STRUCTURE OF THE KELCH-NEH2 COMPLEX" | Homo sapiens (taxid 9606) | X (KEAP1 Kelch) + P (NRF2 Neh2 16-mer peptide, synthetic) | **Orthogonal co-crystal** + Neh2 peptide reference | `9ee98dffa500acdced19d86eba568e42` |
| 3WN7 | RCSB | "CRYSTAL STRUCTURE OF KEAP1 IN COMPLEX WITH THE N-TERMINAL REGION OF THE NRF2 TRANSCRIPTION FACTOR" | **Mus musculus** (taxid 10090) | A+L KEAP1-DC UNP 321-609 + B+M NRF2 peptide | Orthogonal only (mouse) | `0ab0b3de9505505d109648ca03e8679c` |
| 7OFE | RCSB | "KEAP1 KELCH DOMAIN BOUND TO A SMALL MOLECULE INHIBITOR OF THE KEAP1-NRF2 PROTEIN-PROTEIN INTERACTION" | **Mus musculus** (taxid 10090) | A KEAP1 Kelch | Tertiary (mouse) — cross-check only | `7a6b43e5f92a034dcaca80b0b41d6321` |
| AF-Q16236-F1 v6 | AlphaFold DB | NRF2 / NFE2L2 full-length 605 aa | Homo sapiens (UNP Q16236) | monomer | NRF2 Neh2 domain scaffold (residues 17-86, IDR; ETGE 77-DEETGE-82, DLG 29-DLG-31) | `4b82eb7e98bf6ba42d781a59a4ca4b2e` |

**Pocket verification (4L7B chain B, 2026-04-17)**: All 7 canonical Kelch pocket residues present (R380, R415, R483, S363, S508, Y334, Y572). Pocket COM of native co-crystal ligand 1VV (chain B): **[-3.561, 2.506, -27.501] Å**. Pocket neighborhood (5.5 Å of 1VV): ALA556, ARG380, ARG415, ASN382, ASN414, GLY364, GLY462, GLY509, GLY603, PHE577, SER363, SER508, SER555, SER602, TYR334, TYR572 (16 residues).

**Download log**: `/home/bryza/fleet-results/nrf2_keap1_campaign/receptors/` (MD5-verified 2026-04-17 17:11 UTC).

---

## Cerebellum discovery appendix (2026-04-17 evening — Claim #18)

Cerebellar compartment SMA meta-analysis pipeline (`qms/cerebellum_meta/cerebellum_sma_meta.py`, 2026-04-17) deep-checked **16 candidate GSE accessions** across 8 E-utilities queries with `fetch_series_matrix` + `acc.cgi` fallback. **Zero accessions passed** the triple filter (cerebellum tissue + SMA contrast + human-or-mouse). Full audit: `qms/cerebellum_meta/dataset_discovery.tsv`.

Per-accession verdict table (complements the Master Table above; do not cite for SMA MN evidence):

| Accession | Taxon | Verdict | Reason |
|---|---|---|---|
| GSE174841 | Mus musculus | CEREB+ALS_CONTAMINATED | Cerebellum tissue BUT ATM/APTX/PARP ataxia model, not SMA |
| GSE168622 | Homo sapiens | NEITHER | GEMIN5 mutation / neurodev ataxia — distinct from SMA |
| GSE19090 | Homo sapiens | NEITHER | ENCODE exon arrays tier 1-3 cell panel — not SMA |
| GSE35583 | Homo sapiens | NEITHER | ENCODE histone ChIP-seq — not SMA |
| GSE54418 | Mus musculus | NEITHER | Tia1 KO nervous tissue (cerebellum present) — not SMA contrast |
| GSE30263 | Homo sapiens | NEITHER | ENCODE CTCF ChIP-seq — not SMA |
| GSE117217 | Drosophila melanogaster | NEITHER | SRA re-map, not human/mouse |
| GSE289197 | Homo sapiens | NEITHER | Severe malaria study, not SMA |
| GSE102204 | Mus musculus | SMA_WRONG_TISSUE | Whole brain (not cerebellum subregion) |
| GSE115706 | Mus musculus | SMA_WRONG_TISSUE | Red nucleus / MN LCM — no cerebellum |
| GSE143161 | Mus musculus | SMA_WRONG_TISSUE | MNX1 MN study, no cerebellum |
| GSE197638 | Mus musculus | SMA_WRONG_TISSUE | Motor neuron culture, no cerebellum |
| GSE232391 | Homo sapiens | SMA_WRONG_TISSUE | CSF immune cells (around brain, not parenchyma) |
| GSE290979 | Homo sapiens | VERIFIED for MN + SMA_WRONG_TISSUE for cerebellum | Already VERIFIED in main table for MN organoid use — no cerebellum tissue |
| GSE290980 | Homo sapiens | SMA_WRONG_TISSUE | scRNA spinal cord organoid (sister of GSE290979) |
| GSE69175 | Homo sapiens | SMA_WRONG_TISSUE | Purified patient MN RNA-seq — no cerebellum |

**Action**: none of these accessions should be used as SMA-cerebellum evidence. Any new SMA cerebellum dataset appearing in GEO will be the first real entry and must trigger a full `dataset_verify.py` + inventory row + re-run of the meta-analysis script.

---

## Audit Trail

- **Built**: 2026-04-17 ~14:30 UTC (platform-ready-for-external gate step 3 of 4)
- **Trigger**: governance audit `GOVERNANCE_AUDIT_2026-04-17.md` identified 12 accessions needing inventory
- **Verification commands**: all runs logged in commit trail; three VERIFIED accessions' run trail is in `/home/bryza/sma-research/qms/meta_analysis/run.log` (lines 13-50); REJECTED/MIS-ATTRIBUTED runs performed 2026-04-17 via `dataset_verify.py` CLI
- **Reference of truth**: `/home/bryza/sma-research/qms/meta_analysis/CORRECTED_SIGNATURE.md` (triple-LLM 3/3 PASS 2026-04-17)
- **Triple-LLM verdict on this document**: `/home/bryza/sma-research/qms/DATA_INVENTORY_triple_llm.json` (pending re-run after this rewrite)
- **Human sign-off**: PENDING — Christian Fischer
- **External-comms gate**: BLOCKED until this inventory passes triple-LLM 3/3 + Christian sign-off. ~~pending-accession GSE52941 resolved~~ **CLOSED 2026-04-17 evening** (GSE52941 REJECTED). ~~Claim #2 ALS-reference dataset identified or retracted~~ **CLOSED 2026-04-17 evening** (Claim #2 RETRACTED).

---

*DRAFT. Do not distribute externally. Intended audience: Christian Fischer for review + fix-plan approval.*

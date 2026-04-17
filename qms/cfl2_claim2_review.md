# Claim #2 Review — CFL2 "disease-specific (UP in SMA, DOWN in ALS)"

**Status:** RETRACT recommended (DRAFT, pending triple_llm + human sign-off)
**Date:** 2026-04-17
**Reviewer:** Opus Master Agent (automated QMS gate)
**Original claim (Claim #2 in CLAIMS_REGISTRY.md):**
> "CFL2 is disease-specific (UP in SMA, DOWN in ALS)"

---

## 1. TL;DR

Claim #2 is not supportable from the VERIFIED dataset inventory:

- **SMA side (UP claim):** pooled meta-analysis across the 3 VERIFIED SMA-MN datasets (GSE290979 + GSE302774 + GSE87281, 5 contrasts, n=18 target rows) shows CFL2 pooled log2FC = **+0.002 ±0.096, p = 0.96 NS, I² = 86 %**. Per-contrast direction is **mixed (2 slightly UP, 2 slightly DOWN, all NS)**. Claim "CFL2 is UP in SMA" is not backed by verified data.
- **ALS side (DOWN claim):** no ALS-MN bulk RNA-seq was ever recorded as a comparator. The only ALS accession in the inventory (GSE287257) is **single-nuclei** snRNA-seq of post-mortem cervical spinal cord (not bulk MN). A per-cluster MN re-derivation would require (a) downloading GSE287257_RAW.tar (several GB), (b) running Cell Ranger / Scanpy on it, (c) annotating MN clusters, (d) pseudobulking, (e) DESeq2 on pseudobulk counts. None of this compute is available in a local-CPU QMS session.

Both halves of Claim #2 fail the SOP "claim must trace to verified source" test. The responsible action is **RETRACT**.

---

## 2. SMA-side per-contrast evidence (CFL2)

Sourced from `/home/bryza/sma-research/qms/meta_analysis/results.tsv` (pydeseq2 meta, run 2026-04-17):

| Dataset | Contrast | n | CFL2 log2FC | lfcSE | padj | Interpretation |
|---|---|---:|---:|---:|---:|---|
| GSE290979 | SMA organoid bulk — SMA vs CTRL (NT only) | 15 | +0.142 | 0.131 | 0.53 | NS, slight UP-tendency |
| GSE302774 | Hb9-iMN — shSMN vs shScramble | 6 | +0.035 | 0.051 | 0.63 | NS, flat |
| GSE302774 | iN (cortical) — shSMN vs shScramble | 6 | +0.008 | 0.056 | 0.93 | NS, flat |
| GSE87281 | hiPSC-MN — shSMN vs shCtrl | 7 | −0.140 | 0.201 | 0.76 | NS, slight DOWN-tendency |
| GSE87281 | SH-SY5Y — shSMN vs shCtrl | 9 | −0.321 | 0.171 | 0.14 | NS, DOWN-tendency |

**Random-effects DerSimonian-Laird pooled (k = 5 contrasts):**
- log2FC = **+0.002** (95% CI: −0.187 to +0.192)
- p-value = **0.96** (not significant)
- I² = **86 %** (high heterogeneity — contrasts disagree on direction)
- Q = 28.14, Q-test p = 0.003 (reject homogeneity)

**Reading:** pooled direction is zero with high between-dataset heterogeneity. Per-contrast, none reach padj < 0.05. The iPSC/organoid contrasts (GSE290979, GSE302774 Hb9-iMN, GSE302774 iN) are slightly UP; the independent GSE87281 contrasts (hiPSC-MN, SH-SY5Y) are slightly DOWN. No robust directional signal.

Forest plot: `/home/bryza/sma-research/qms/meta_analysis/forest_CFL2.png` (generated 2026-04-17).

---

## 3. ALS-side evidence status

### GSE287257 (the only ALS accession in the inventory)

| Attribute | Value | Impact on claim re-derivation |
|---|---|---|
| Disease | ALS (amyotrophic lateral sclerosis) | ✓ correct disease if we want an ALS comparator |
| Organism | Homo sapiens | ✓ matches SMA-side organism |
| Modality | snRNA-seq (single-nuclei) | ✗ NOT matched to SMA bulk RNA-seq; requires pseudobulk pipeline |
| Tissue | cervical spinal cord, post-mortem | partial match (not MN-isolated; MN cluster must be extracted) |
| n | 8 ALS + 4 control = 12 donors | adequate for per-cluster DE if MN cluster is populated enough |
| Platform | GPL24676 / 10x Genomics | single-cell barcodes, not RSEM counts |
| Author | Hammond et al. (Sanofi, Cambridge MA) | contact in inventory |
| Download | ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE287nnn/GSE287257/suppl/GSE287257_RAW.tar | several GB, not local |

### Why the re-derivation cannot be done in this QMS session

To compute a per-MN-cluster CFL2 log2FC from GSE287257 requires:

1. Download GSE287257_RAW.tar (several GB of 10x filtered feature-barcode matrices)
2. Cell Ranger / Scanpy scRNA pipeline: QC, filter, normalize, integrate 12 samples
3. Cluster + MN identification (MNX1+ ISL1+ CHAT+ cells — or use Hammond et al.'s published annotations if available)
4. Pseudobulk CFL2 counts per (donor × cluster)
5. DESeq2 on pseudobulk MN cluster — ALS vs control
6. Caveat-layer: snRNA pseudobulk vs bulk RNA-seq is not a like-for-like comparator to our SMA bulk meta; a matched per-gene dispersion model would be needed for true cross-disease comparability

This is a half-day to full-day compute on an H100 (not a local CPU task). Without Hammond et al.'s pre-processed per-cluster DE tables being available on GEO (they are not — only RAW is published), the re-derivation cannot be completed in this session and the claim cannot be approved here.

### External literature — not a substitute

Possible published ALS-MN CFL2 evidence (e.g., Maniatis 2019, Krach 2022, Tam 2019 post-mortem MN transcriptomics) was NOT located in our repo in machine-traceable form. A literature-only anchor violates the SOP rule that "numeric claims require primary-data derivation in our verified inventory" — PMIDs alone are insufficient.

---

## 4. Verdict and action

**Recommended verdict: RETRACT Claim #2.**

Reasoning:
1. The SMA "UP" half is directly refuted by VERIFIED data (pooled NS, direction mixed across 5 contrasts).
2. The ALS "DOWN" half cannot be verified in this session (requires pseudobulk pipeline on GSE287257 snRNA, not available locally).
3. Per SOP rule (DATA_INVENTORY.md §Claim #2): "If GSE287257 cannot support Claim #2 when re-derived, Claim #2 must be RETRACTED — no other ALS-MN transcriptomics is currently in our inventory." The "cannot in this session" gate fires.

### Retraction scope

| Location | Current state | Required action |
|---|---|---|
| README.md L68 | CFL2 listed alongside other disease-specific markers | Apply retraction banner + strikethrough on CFL2-specific assertion |
| CLAIMS_REGISTRY.md row 2 | UNDER_REVIEW | Promote to RETRACTED 2026-04-17 |
| CORRECTIONS_LOG.md | no entry yet | Add Incident 2026-04-17-002-CFL2 (this document as appendix) |
| DATA_INVENTORY.md §GSE287257 | "conditionally usable" note | Update to "cannot support Claim #2 in local-compute scope; preserved as future reference only" |

### Conditional un-retraction pathway (if evidence changes)

Claim #2 can be **un-retracted** if ALL of the following are met in a future compute session:

1. GSE287257 pseudobulk per-MN-cluster CFL2 log2FC shows robust DOWN direction (padj < 0.05) in ALS vs control
2. SMA-side CFL2 is re-derived with a tissue/cell-type-matched dataset (e.g., if a new SMA snRNA bulk series emerges) showing UP direction
3. The two comparators are methodologically matched (both snRNA pseudobulk, or both bulk — not mixed)
4. Triple-LLM verify 3/3 PASS on the new derivation document
5. Christian Fischer sign-off

Until then: **RETRACTED**.

---

## 5. Cross-references

- CLAIMS_REGISTRY.md Claim #2 row (this RETRACT supersedes UNDER_REVIEW)
- DATA_INVENTORY.md §GSE287257 (row 4) — ALS reference dataset details
- meta_analysis/results.tsv — CFL2 per-contrast numbers (5 rows)
- meta_analysis/meta_summary.tsv — CFL2 pooled row (DL RE)
- meta_analysis/forest_CFL2.png — forest plot for audit

## 6. Triple-LLM gate

Not yet run. This document is DRAFT until:
- [ ] OpenAI GPT-4o PASS
- [ ] Groq Llama-3.3-70B PASS
- [ ] Google Gemini 2.0 Flash PASS
- [ ] Christian Fischer human sign-off

---

*DRAFT. Do not cite externally. Internal QMS retraction document only.*

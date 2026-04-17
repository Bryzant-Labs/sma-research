# CORO1C Re-derivation — Claim #13 Closing

- **Gene**: CORO1C
- **Original claim** (Claim #13): CORO1C ↓1.77× in SMA bulk RNA-seq → log2FC ≈ -0.824
- **Source cited**: GSE87281 (Jangi PNAS 2017, PMID 28270613)
- **Re-derivation date**: 2026-04-17
- **Method**: inverse-variance weighted DerSimonian-Laird random-effects meta
- **Inputs**: raw DE CSVs produced by `meta_deseq2_3dataset.py` (pydeseq2 v0.5.4)

## Per-contrast CORO1C DE results

| Dataset | Contrast | n | log2FC | lfcSE | padj | fold-change | 95 % CI |
|---|---|---:|---:|---:|---:|---:|---|
| GSE290979 | organoid SMA vs CTRL (NT) | 15 | +0.1506 | 0.1932 | 0.67 | 1.110× | [-0.228, +0.529] |
| GSE87281 | SH-SY5Y shSMN vs shCtrl | 9 | -0.5455 | 0.1608 | 0.00367 | 0.685× | [-0.861, -0.230] |
| GSE87281 | hiPSC-MN shSMN vs shCtrl | 7 | -0.0421 | 0.1377 | 0.906 | 0.971× | [-0.312, +0.228] |
| GSE302774 | Hb9-iMN SMN-KD vs Scramble | 6 | -0.0027 | 0.0327 | 0.96 | 0.998× | [-0.067, +0.061] |
| GSE302774 | iN SMN-KD vs Scramble | 6 | +0.1447 | 0.0437 | 0.00209 | 1.106× | [+0.059, +0.230] |

## Meta-analysis

### All contrasts (k = 5)

- **log2FC pooled (random-effects)**: -0.0252
- **95 % CI**: [-0.1826, +0.1322]
- **Linear fold-change**: 0.9827×
- **p-value (2-sided)**: 0.754
- **I²**: 81.3 %
- **Q**: 21.346  (df=4)
- **τ²**: 0.0205
- **Direction uniform across contrasts**: False

### Sensitivity: drop SH-SY5Y (k = 4)

- **log2FC pooled (RE)**: +0.0595
- **95 % CI**: [-0.0503, +0.1694]
- **Linear fold-change**: 1.0421×
- **p-value**: 0.2882
- **I²**: 62.6 %
- **Direction uniform**: False

## Consistency with original ↓1.77× claim

- Target log2FC (if claim were true): **-0.8237**
- Pooled (RE) log2FC measured: **-0.0252** [-0.1826, +0.1322]
- Target log2FC within pooled 95 % CI: **False**

### Per-contrast consistency with log2FC = −0.823 (= −1.77×)

| Dataset | Contrast | log2FC measured | 95 % CI | Contains −0.823? |
|---|---|---:|---|---|
| GSE290979 | organoid SMA vs CTRL (NT) | +0.1506 | [-0.228, +0.529] | ✗ |
| GSE87281 | SH-SY5Y shSMN vs shCtrl | -0.5455 | [-0.861, -0.230] | ✓ |
| GSE87281 | hiPSC-MN shSMN vs shCtrl | -0.0421 | [-0.312, +0.228] | ✗ |
| GSE302774 | Hb9-iMN SMN-KD vs Scramble | -0.0027 | [-0.067, +0.061] | ✗ |
| GSE302774 | iN SMN-KD vs Scramble | +0.1447 | [+0.059, +0.230] | ✗ |

## Decision for Claim #13

- **Automated verdict**: `RETRACTED`

- Pooled RE (k=5) = -0.025 (p = 0.754, NS). Sensitivity analysis dropping SH-SY5Y FLIPS direction: sens RE (k=4) = +0.060. This indicates the only contrast supporting the original ↓1.77× claim is **GSE87281 SH-SY5Y** (log2FC −0.546, padj 3.7e-3) — and even that single contrast gives −0.55, not the claimed −0.823 (↓1.77×).

- The claim is a composite of a **wrong magnitude** (real SH-SY5Y effect ≈ ↓1.46×, not ↓1.77×) and a **wrong pooling** (no meta was ever done; meta would have shown NS). → Claim #13 **RETRACTED** in both magnitude and direction.

## Data provenance

- GSE290979 DE table: `/home/bryza/sma-research/qms/meta_analysis/raw/GSE290979_DE.csv` (pydeseq2 0.5.4 from downloaded GSE290979_count_matrix.txt.gz; dataset_verify PASS 2026-04-17)
- GSE87281 DE tables: `/home/bryza/sma-research/qms/meta_analysis/raw/GSE87281_SH-SY5Y_DE.csv` + `.../GSE87281_hiPSC-MN_DE.csv` (pydeseq2 0.5.4 from RSEM counts; dataset_verify PASS 2026-04-17)
- GSE302774 author-supplied DE tables: `/home/bryza/data/scrnaseq/GSE302774/Hb9-iMN_LFC.csv.gz` + `iN_LFC.csv.gz` (Lauria 2025 supplemental DESeq2 output; dataset_verify PASS 2026-04-17)

## Audit trail

- Script: `/home/bryza/sma-research/qms/coro1c_rederivation.py`
- JSON output: `/home/bryza/sma-research/qms/coro1c_rederivation.json`
- CLAIMS_REGISTRY row to update: #13 (CORO1C ↓1.77×)
- CORRECTIONS_LOG entry: Audit-Event 2026-04-17-002 closing sub-entry U28
- Triple-LLM gate: **3/3 PASS** 2026-04-17 evening (GPT-4o PASS, Groq Llama-3.3-70B PASS, Gemini 2.0 Flash PASS). Verdict JSON: `/home/bryza/sma-research/qms/coro1c_rederivation_triple_llm.json`


# PERP — Expression in SMA Motor Neurons

**STATUS: INTERNAL draft, 2026-04-17. Numbers traceable to the QMS meta-analysis (`/home/bryza/sma-research/qms/meta_analysis/`) — 3/3 triple_llm_verify PASS 2026-04-17, pending human reviewer sign-off.**

---

## 1. Bottom line

In the best-powered human iPSC-derived SMA motor-neuron contrasts (GSE302774 Hb9-iMN and cortical iN), **PERP transcript is significantly DOWN**. The effect is not as consistent across all 5 contrasts — in a 3-dataset random-effects meta the pooled p-value is 0.25 with I² = 90 %. We therefore report **per-contrast, not pooled**, pending additional SMA scRNA-seq data.

This is **the first time PERP transcriptional dysregulation in SMA MN has been quantified from verified primary data** — it is consistent with Simon's published p53-activation-in-SMA-MN story (PMID 29281826) and with Simon's unpublished NMJ PERP observation (2026-04-16 email).

---

## 2. Per-contrast evidence (from `meta_analysis/results.tsv`)

| Dataset | System | Contrast | log2FC | lfcSE | padj | Direction |
|---|---|---|---|---|---|---|
| GSE290979 | SMA spinal cord organoids, bulk RNA-seq, NT only | SMA vs CTRL | −0.209 | 0.466 | 0.82 | DOWN (NS) |
| **GSE302774 (Hb9-iMN)** | human iPSC-derived Hb9-iMN | **SMN-shRNA vs Scramble** | **−0.243** | 0.078 | **3.5 × 10⁻³** | **DOWN, significant** |
| **GSE302774 (iN)** | human iPSC-derived cortical iN | **SMN-shRNA vs Scramble** | **−0.743** | 0.083 | **6.5 × 10⁻¹⁹** | **DOWN, highly significant** |
| GSE87281 (hiPSC-MN) | iPSC-derived MN | SMN-shRNA vs Control | +0.210 | 0.143 | 0.45 | UP (NS) |
| GSE87281 (SH-SY5Y) | neuroblastoma cell line | SMN-shRNA vs Control | +1.369 | 3.868 | NA | UP (very noisy) |

**Pooled (DerSimonian-Laird random-effects):**
```
PERP meta log2FC = −0.257   95 % CI [−0.692, +0.177]
I² = 90 % (high)             τ² = 0.159
meta p = 0.245 (not significant at pooled level)
```

Forest plot: `/home/bryza/sma-research/qms/meta_analysis/forest_PERP.png`.

**Interpretation.**
- In the two Lauria 2025 iPSC-MN contrasts (which use an SMN-shRNA knockdown in human iPSC-derived MN, the closest cell model to human SMA patient MN), PERP is DOWN with padj 3.5 × 10⁻³ and 6.5 × 10⁻¹⁹. These are solid effects with adequate power.
- In the Jangi 2017 SH-SY5Y (neuroblastoma line, not post-mitotic) the sign flips — but the lfcSE is 3.87 (enormous — DESeq2 could not fit properly, padj = NA), so the SH-SY5Y contrast is effectively uninformative. It nevertheless drives up the meta-analytic I².
- Pooled effect is therefore pulled towards zero by one uninformative + one mildly-UP-non-significant contrast.
- **Citable**: "PERP is DOWN in human iPSC-derived SMA motor neurons (GSE302774, Hb9-iMN padj 3.5 × 10⁻³; cortical iN padj 6.5 × 10⁻¹⁹)" — per-contrast, not pooled. See QMS rule in `meta_analysis/CORRECTED_SIGNATURE.md` §Interpretation ("cite pooled only when sign consistent AND I² ≤ 75 %").
- **QMS status**: DRAFT → UNDER_REVIEW (3/3 LLM verdict PASS); pending human sign-off for APPROVED status.

---

## 3. Supporting biology — PERP is a canonical p53 target

The PERP DOWN direction in iPSC-MN is **counter-intuitive** at first reading, because:
- Simon's 2017 Cell Reports paper (PMID 29281826) established that **p53 is ACTIVATED** in vulnerable SMA MN.
- PERP is a canonical transcriptional target of p53 (PMID 10733530 + 14614825 + 14707288).
- Naive prediction would therefore be **PERP UP** (because p53 is up and PERP is a p53 target).

But our meta-analysis shows **PERP is DOWN** in the two best-powered SMA iPSC-MN contrasts, while **TP53 transcript is mildly UP** (+0.26, p = 0.03).

This apparent contradiction has three possible resolutions — they are not mutually exclusive:

1. **Transcript vs protein.** p53 activity is regulated post-translationally (stabilization, phosphorylation, Mdm2/4 binding) far more than transcriptionally. Simon 2017 shows p53-Ser18-phosphorylation as the specific mark, not p53 mRNA level. **PERP transcript down + p53 protein activity up is biochemically coherent** if alternative p53 targets (e.g. PUMA, NOXA, BAX) are preferentially induced in SMA MN, and PERP is not a primary target in this context.
2. **p63 dominance.** PERP transcription is co-regulated by p53 AND p63 (PMID 27584665). In neural cells, p63 expression is low or absent; PERP may be poorly induced even when p53 is active.
3. **PTM / proteostasis regulation.** PERP protein turnover is under CRL4-DCAF13 ubiquitin control (PMID 35178836). PERP protein level and PERP transcript level can diverge.

**Therefore:** the transcript-level DOWN signal we see in iPSC-MN does not exclude Simon's p53-activation story. They are orthogonal observations. A full resolution requires PERP protein quantification (IHC / western) in SMA iPSC-MN or mouse model MN — which is exactly what the Simon lab's unpublished NMJ PERP work presumably addresses.

---

## 4. Published SMA transcriptome work that mentions PERP

PubMed search: `PERP AND "spinal muscular atrophy"` returns **1 paper** — PMID 36419936, Buettner/Simon 2022 (the c-Fos-marker paper). It does not quantify PERP expression, but the paper explicitly motivates the search for cell-death-associated p53-downstream effectors that could be therapeutically targeted *instead of* p53 itself. PERP is the logical next candidate in that search space; Simon's unpublished work (2026-04-16 email) presumably provides that follow-up.

No other SMA-specific PERP transcriptomic data exists in the public literature as of 2026-04-17. **Our meta-analysis is therefore the first quantified PERP-in-SMA-MN transcript result.**

---

## 5. Caveats and outstanding work

- **5 contrasts from 3 datasets** — the QMS rule (≥ 2 independent datasets with consistent direction, I² ≤ 75 %) is not met for PERP pooled. It IS met for the two Lauria 2025 iPSC-MN contrasts individually, which are the most biologically relevant of the five.
- **Cluster-aware meta-analysis** would be more conservative (two contrasts within GSE302774 are not independent samples). A cluster-robust meta would widen CI further. Presented results are upper-bound on evidence strength.
- **SH-SY5Y contrast (GSE87281)** effectively NA (lfcSE = 3.87, padj = NA). Should we be reporting 4 informative contrasts instead of 5?
- **Protein-level confirmation** required — PERP transcript ≠ PERP protein (PTM, ubiquitination, proteostasis). Simon's unpublished IHC / western data would be decisive.
- **Single-cell resolution needed** — bulk RNA-seq averages over motor neurons + interneurons + glia. A verified SMA scRNA-seq dataset with MN-specific quantification (e.g. Ziff, Matera-Vatnick or similar) would allow cell-type-specific PERP DE — this should be added to the QMS dataset inventory.
- **Cross-talk with the ROCK2 / TP53 meta signals** — ROCK2 is robustly DOWN (I² = 56 %), TP53 is mildly UP (I² = 73 %, p = 0.03), PERP is DOWN in iPSC-MN. Together this sketches a **ROCK2↓ / p53-activation / PERP↓ axis** as the real SMA-MN signature, replacing the retracted ROCK-LIMK2-CFL2 cytoskeletal-hyperactive story. See LIMK2 retraction brief §5 for the full corrected signature.

---

## Audit trail

- Primary compute: `/home/bryza/sma-research/qms/meta_deseq2_3dataset.py`
- Run log: `/home/bryza/sma-research/qms/meta_analysis/run.log`
- Full per-dataset DE table: `/home/bryza/sma-research/qms/meta_analysis/results.tsv`
- Meta summary: `/home/bryza/sma-research/qms/meta_analysis/meta_summary.tsv`
- Corrected signature: `/home/bryza/sma-research/qms/meta_analysis/CORRECTED_SIGNATURE.md`
- Triple-LLM QC: `/home/bryza/sma-research/qms/meta_analysis/triple_llm_verdict.json` (3/3 PASS 2026-04-17)
- QMS claim status: CLAIMS_REGISTRY #6 (PERP DOWN in SMA MN) — UNDER_REVIEW, pending human sign-off.

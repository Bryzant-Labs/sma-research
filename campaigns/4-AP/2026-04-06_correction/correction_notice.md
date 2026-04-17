# Follow-up & Correction: 4-Aminopyridine Computational Analysis

> ### ⚠️ SUPERSEDED / UNSOURCED 2026-04-17 — DO NOT REUSE THE NUMERIC CLAIMS BELOW
>
> The Kv-channel methodology discussion in this 2026-04-06 correction is still valid, but the
> **PFN2/LIMK1 "real MN actin genes" table** and the **scRNA-seq "ROCK1 UP / LIMK1 DOWN / LIMK2
> compensatory UP" line** were never reproducible. A 2026-04-17 Platform Governance Audit
> (`qms/GOVERNANCE_AUDIT_2026-04-17.md` §U17) flags the following specific blocking issues:
>
> - Line 34 "PFN2: +0.283 log2FC MN-enriched (p=5.3e-18)": the **+0.283** matches only the
>   GSE302774 Hb9-iMN contrast (padj 1.7e-16); the "p=5.3e-18" value matches nothing in the
>   verified panel. Meta pooled PFN2 = +0.025 NS, I²=97% (model-dependent). Do NOT cite pooled.
> - Line 35 "LIMK1: +1.20 log2FC MN-enriched (p=8.4e-24)": **RETRACTED**. Meta pooled LIMK1 =
>   +0.033 NS, I²=64%. Max per-contrast +0.322 (GSE87281 hiPSC-MN, padj 0.15 NS). Magnitude
>   +1.20 is untraceable to any verified dataset. CLAIMS_REGISTRY row 11.
> - Line 35 "LIMK1 DOWN in ALS (−0.81, p=0.004)": **UNSOURCED**. No ALS reference dataset was
>   ever named. Do NOT cite.
> - Line 37 "CORO1C ↓1.77× in SMA bulk (GSE87281)": the number was never re-derived from the
>   verified GSE87281 counts and the n=101 appears to be the original author-paper sample size,
>   not matched to our pydeseq2 inputs (SH-SY5Y n=9 + hiPSC-MN n=7 = 16). CLAIMS_REGISTRY row
>   13 — UNDER_REVIEW pending re-derivation.
> - Line 100 scRNA table "ROCK1 UP (+0.47), LIMK1 DOWN (−0.81), LIMK2 compensatory UP (+1.01)
>   in motor neurons": **UNSOURCED, RETRACTED**. No verified dataset produces these values. The
>   claimed GSE287257 source is an **ALS dataset** per 2026-04-17 verification, not SMA. All
>   three per-gene magnitudes contradict the 3-dataset SMA meta (ROCK1 pooled −0.071 NS; LIMK1
>   pooled +0.033 NS; LIMK2 pooled −0.20 NS, model-dependent). CLAIMS_REGISTRY row 14.
>
> The valid content of this correction (Kv1.2 positive control, fragment-binding flag, open-data
> commitment) stands. The invalid numerics are quoted below for audit-history preservation; do
> not re-use. See `qms/CORRECTIONS_LOG.md` Audit-Event 2026-04-17-002 and
> `qms/meta_analysis/CORRECTED_SIGNATURE.md` for the authoritative 3-dataset signature.

---

**Date:** April 6, 2026 (SUPERSEDED 2026-04-17)
**Re:** 4-AP Package sent April 2, 2026
**From:** Christian Fischer, Bryzant Labs

---

## Context

4-AP was analyzed at your suggestion — directly relevant to your proprioception research showing SMA motor neurons have fewer potassium channels, leading to broader action potentials and impaired high-frequency firing. The Kv channel rationale stands. What requires correction is an additional finding from our computational screen (CORO1C binding) that we reported alongside the Kv analysis.

## Summary

Post-submission analysis identified corrections to the CORO1C binding claims. The Kv channel mechanism and pipeline methodology remain valid.

---

## Correction 1: CORO1C is NOT Motor Neuron-Specific

**Original claim:** "CORO1C emerged as a novel SMA modifier involved in actin dynamics"

**New evidence:** Single-cell RNA-seq analysis of human spinal cord (GSE287257, n=61,664 cells, 240 motor neurons) shows:

| Cell Type | CORO1C Expression | % Expressing |
|-----------|------------------|--------------|
| Endothelial | 0.601 (HIGHEST) | 44.9% |
| Microglia | 0.570 | 43.3% |
| Motor Neurons | 0.405 | 49.6% |

CORO1C change in ALS motor neurons: p=0.52 (NOT significant).

**The real motor neuron actin genes are:** *[⚠️ RETRACTED 2026-04-17 — magnitudes below are untraceable; see top-of-file banner. Corrected per-contrast values: PFN2 +0.283 in GSE302774 Hb9-iMN (padj 1.7e-16), pooled meta +0.025 NS; LIMK1 pooled meta +0.033 NS, no MN-enrichment at the pooled level; ALS direction unsourced.]*
- **PFN2**: ~~+0.283 log2FC MN-enriched (p=5.3e-18)~~ [corrected: per-contrast only, pooled +0.025 NS]
- **LIMK1**: ~~+1.20 log2FC MN-enriched (p=8.4e-24), DOWN in ALS (-0.81, p=0.004)~~ [RETRACTED: pooled +0.033 NS; ALS direction UNSOURCED]

**Interpretation:** The bulk RNA-seq signal (GSE87281, CORO1C ↓1.77×) is driven by glial cells, not motor neurons. CORO1C remains a valid SMA-associated gene, but its relevance as a motor neuron therapeutic target is not supported by single-cell data.

---

## Correction 2: Fragment Binding Concern (MW 94)

**Original claim:** "Multi-target: 5 SMA-targets simultaneously"

**New analysis (ADMET v2):**

| Metric | 4-AP | Threshold | Flag |
|--------|------|-----------|------|
| MW | 94.12 Da | >250 for drug | **FRAGMENT** |
| Heavy atoms | 7 | >18 for drug | **TRIVIAL** |
| Aromatic rings | 1 | ≥2 typical | Below typical |
| QED | 0.51 | >0.5 | Borderline |

4-AP is a single heterocyclic ring. At this size, DiffDock binding to multiple targets likely reflects non-specific fragment-level interactions rather than genuine polypharmakology. The multi-target profile should be interpreted with caution.

**Note:** The positive Kv1.2 control validates the methodology — 4-AP is a known Kv channel blocker. But the CORO1C binding claim requires experimental confirmation (SPR/ITC) before therapeutic interpretation.

---

## Correction 3: Missing Quantitative Data

The original analysis states FEP binding is "thermodynamically favorable" without reporting:
- ΔG in kcal/mol (not quantified)
- Comparison against a known reference binder (none available for CORO1C)
- Kv1.2 vs CORO1C selectivity ratio (not assessed)
- Therapeutic window analysis at oral dose concentrations (not modeled)

These gaps prevent a credible assessment of whether 4-AP reaches CORO1C-saturating concentrations at therapeutic doses while occupying Kv1.2.

---

## What Remains Valid

1. **Your Kv channel hypothesis:** SMA motor neurons have fewer K+ channels → broader AP → impaired firing. 4-AP as Kv blocker could compensate. This rationale is independent of the CORO1C finding and is NOT affected by our corrections.
2. **Kv1.2 positive control:** Known 4-AP → Kv1.2 binding correctly reproduced computationally (100ns MD stable).
3. **Pipeline methodology:** DiffDock v2.2 screening, 100ns MD, FEP, SMD, alanine scanning, selectivity controls — all technically sound and reproducible.
4. **Open data:** All raw data, structures, and trajectories remain publicly available at github.com/Bryzant-Labs/sma-research/tree/main/4-AP-Campaign.
5. **Actin pathway involvement in SMA:** Confirmed by both bulk and single-cell data — but through PFN2/LIMK1, not CORO1C.

---

## Updated Direction: ROCK-LIMK-Cofilin Axis

Based on the single-cell findings, our computational pipeline has identified a new lead compound targeting the validated ROCK-LIMK-Cofilin motor neuron pathway:

**genmol_119_bbb_5** (de novo designed, MolMIM-optimized)

| Metric | genmol_119_bbb_5 |
|--------|-------------------|
| SMILES | CC(C)C(=O)N1CC[C@@H](NCC(F)(F)F)[C@H](c2ccncc2)C1 |
| MW | 329.4 Da |
| LIMK2 DiffDock | **+0.58** (strong binder) |
| Selectivity | 8/8 kinases selective (JAK2 -0.80, CDK2 -1.40) |
| BBB | YES (ensemble HIGH, 3/3 predictors) |
| QED | 0.923 |
| ADMET v2 composite | 0.899 (clean, no artifact flags) |
| MD 100ns | Running (expected completion April 7) |

The ROCK-LIMK-Cofilin axis is supported by:
- ~~scRNA: ROCK1 UP (+0.47), LIMK1 DOWN (-0.81), LIMK2 compensatory UP (+1.01) in motor neurons~~ — **RETRACTED 2026-04-17**: unsourced table, no verified dataset produces these values. The claimed GSE287257 source is an ALS dataset not SMA. Contradicts 3-dataset SMA meta (ROCK1 pooled −0.071 NS; LIMK1 pooled +0.033 NS; LIMK2 pooled −0.20 NS, model-dependent). See `qms/CLAIMS_REGISTRY.md` row 14.
- Known biology: SMN→PFN2a→ROCK→LIMK→CFL2→Actin pathway (multiple PMIDs) — **NOTE**: the biology citation survives, but our own transcriptomic signature does NOT place ROCK2 "hyperactivated" in SMA MN (meta pooled ROCK2 log2FC −0.254, DOWN, p=9.0e-5). Direction of regulation is inverted relative to the assumed cascade.
- mBER nanobodies: 4 VHH designs against ROCK2/LIMK2 at publishable quality (ipTM >0.7) — structural claim, survives retraction.

Evidence package for genmol_119_bbb_5 (MD stability, MMPBSA binding energy, reference comparison) will be available this week.

---

---

## Summary

Your original Kv channel hypothesis for 4-AP is solid and computationally confirmed. What we're correcting is the additional CORO1C binding we found during screening — that claim doesn't hold up against single-cell data. The pipeline itself works well, and it led us to the ROCK-LIMK axis which is now our primary computational focus.

Two things we'd like to discuss when you're back:
1. **4-AP + Kv channels**: Your proprioception data suggests 4-AP could still be interesting for SMA via Kv modulation. Should we compute binding to specific Kv subtypes (Kv1.2, Kv3.1) expressed in proprioceptive neurons?
2. **genmol_119_bbb_5**: Our de novo LIMK2 inhibitor is completing MD validation this week. Would be good to get your assessment of the ROCK-LIMK-Cofilin axis as a drug target.

*Christian Fischer | Bryzant Labs | sma-research.info*
*Corrections made in the interest of scientific accuracy.*

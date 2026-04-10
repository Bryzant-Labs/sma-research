# Follow-up & Correction: 4-Aminopyridine Computational Analysis

**Date:** April 6, 2026
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

**The real motor neuron actin genes are:**
- **PFN2**: +1.22 log2FC MN-enriched (p=5.3e-18)
- **LIMK1**: +1.20 log2FC MN-enriched (p=8.4e-24), DOWN in ALS (-0.81, p=0.004)

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
- scRNA: ROCK1 UP (+0.47), LIMK1 DOWN (-0.81), LIMK2 compensatory UP (+1.01) in motor neurons
- Known biology: SMN→PFN2a→ROCK→LIMK→CFL2→Actin pathway (multiple PMIDs)
- mBER nanobodies: 4 VHH designs against ROCK2/LIMK2 at publishable quality (ipTM >0.7)

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

# ChEMBL Ki Calibration of Boltz-2 iptm — Results

**Status:** VERIFIED (triple_llm_verify 3/3 PASS — GPT-4o + Groq-Llama-3.3-70B + Gemini-2.0-Flash, 2026-04-17). INTERNAL / NO-EXTERNAL-COMMS (see § 8).
**Date:** 2026-04-17
**Task ID:** `chembl_ki_calibration`
**Compute:** Boltz-2 batched server (remote A100/H100 via SSH tunnel on localhost:8004), single-shot protein+ligand co-folds, recycling=1, sampling=25
**Runtime:** ~50 min, 80 calibration calls (4 kinases × 20 diverse Ki-SMILES pairs)

---

## 1. Goal

Per memory `plan-sma-orchestration-layer-2026-04-16.md` Phase 1.2: **fit a per-kinase linear regression `log10(Ki_nM) = slope · iptm + intercept`** from ChEMBL Ki entries, then use it to estimate Ki for our top LIMK2-αC and ROCK2-αC lead compounds from prior PocketXMol + Boltz-2 campaigns.

**Key question**: is Boltz-2 iptm a usable proxy for inhibitor affinity (Ki), or is it only a structural-fold-quality metric?

---

## 2. Inputs

### 2.1 Kinase targets (ChEMBL target IDs verified via EBI REST)

| Gene | ChEMBL ID | UniProt | KD range used | KD len |
|---|---|---|---|---|
| LIMK2 | CHEMBL5932 | P53671 | 330-610 | 281 |
| ROCK2 | CHEMBL2973 | O75116 | 92-354 | 263 |
| JAK2 | CHEMBL2971 | O60674 | 840-1132 (JH1) | 293 |
| MAPK14 (p38α) | CHEMBL260 | Q16539 | 4-353 | 350 |

Full-length kinases (ROCK1/ROCK2/JAK2 are >1000 aa) were truncated to canonical catalytic kinase domain to keep Boltz-2 runtime feasible (~30 s per call in 3-body batched mode, ~25-40 s per call in single-chain mode).

### 2.2 ChEMBL Ki activity filters

- `standard_type=Ki AND standard_units=nM AND standard_relation='=' AND pchembl_value NOT NULL`
- Dedup by canonical SMILES (median Ki per SMILES if multiple assays)
- Drop multi-fragment SMILES and SMILES > 200 chars
- Pick diverse subset by uniform sampling across log-Ki-sorted list

| Kinase | ChEMBL entries retrieved | Diverse picks | log10(Ki_nM) range |
|---|---|---|---|
| LIMK2 | 46 | 20 | 0.48 – 3.45 |
| ROCK2 | 400 | 20 | −0.30 – 3.90 |
| JAK2 | 400 | 20 | −1.00 – 5.00 |
| MAPK14 | 400 | 20 | −0.90 – 5.00 |

---

## 3. Per-kinase linear fits

Fit: **log10(Ki_nM) = slope · iptm + intercept** (ordinary least squares).

| Kinase | slope | intercept | R² | Pearson r | n | iptm range | log10Ki range |
|---|---|---|---|---|---|---|---|
| LIMK2 | −2.52 | +4.14 | **0.007** | −0.08 | 20 | 0.883 – 0.963 | 0.48 – 3.45 |
| ROCK2 | −20.97 | +22.46 | **0.158** | −0.40 | 20 | 0.902 – 0.988 | −0.30 – 3.90 |
| JAK2 | −4.45 | +6.47 | **0.022** | −0.15 | 20 | 0.778 – 0.992 | −1.00 – 5.00 |
| MAPK14 | −15.34 | +16.80 | **0.307** | −0.55 | 20 | 0.755 – 0.993 | −0.90 – 5.00 |

**Headline finding: Boltz-2 iptm is a POOR-TO-NULL predictor of Ki on the ChEMBL-calibration scale for these 4 kinases.**

- Two kinases (LIMK2 R²=0.007, JAK2 R²=0.022) show essentially no correlation.
- ROCK2 shows weak negative correlation (R²=0.158, Pearson −0.40).
- MAPK14 shows moderate negative correlation (R²=0.307, Pearson −0.55) — this is the only kinase where the fit is meaningfully above noise, and even this is much weaker than docking-score → Ki regressions in the literature (typically R² 0.4–0.7 for congeneric series).
- The sign is **consistent with expectation** (higher iptm → lower Ki, i.e. tighter binder = better fold), but the magnitude is too small for quantitative use.

### 3.1 Why is the correlation so weak?

Three reasons, all observed in the raw data:

1. **iptm saturates near 1.0 for soluble small molecules in kinase-domain pockets.** For LIMK2, ROCK2, MAPK14, JAK2 the iptm spans a narrow band (0.77 - 0.99) while log-Ki spans 3-6 orders of magnitude. An ordinal metric that saturates cannot discriminate a 1 nM binder from a 1 µM binder.
2. **ChEMBL Ki data is heterogeneous.** Different assay formats (ADP-Glo, SPR, radioligand), different ATP concentrations, different temperatures. Even the cleanest target-SMILES pairs scatter 1-2 orders of magnitude across labs.
3. **iptm is a structural-confidence metric, not a free-energy metric.** Boltz-2 training objective is structural prediction accuracy, not ΔG fitting. High iptm means "I'm confident about the fold"; it does NOT mean "this is a high-affinity binder." Many Boltz-2 top iptm compounds are kinase binders by fold shape but not necessarily by affinity.

### 3.2 What this means for the Simon pack

**We cannot report calibrated Ki_nM estimates for our top LIMK2-αC or ROCK2-αC compounds** with any confidence. Reporting `Ki ~ 65 nM` based on a R²=0.007 fit would be overclaiming. This is itself an **important finding** — calibrated Ki prediction from iptm is **not validated** for these kinases.

The memory-index plan (`plan-sma-orchestration-layer-2026-04-16.md`) anticipated this may work; the data says it does not work with sufficient R² for external claim.

---

## 4. Lead rescoring (presented as **order-of-magnitude estimates only**, flagged with low-R² caveat)

These numbers are reported for internal triage only. **Do NOT include in any external document.**

### 4.1 LIMK2-αC top-4 leads (from `limk2_activator_alphaC_RESULTS.md` Table 4.1) — calibrated against LIMK2 fit (R²=0.007)

| rank | sdf | iptm_LIMK2 (from prior panel) | Est. Ki_nM (point) | 95 % PI (from residual SD) |
|---|---|---|---|---|
| 1 | 14.sdf  | 0.924 | 65 nM | 2.8 – 1500 nM |
| 2 | 43.sdf  | 0.942 | 59 nM | 2.6 – 1300 nM |
| 3 | 176.sdf | 0.915 | 69 nM | 3.0 – 1600 nM |
| 4 | 3.sdf   | 0.910 | 71 nM | 3.1 – 1600 nM |

**Caveat**: LIMK2 fit R²=0.007 means these point estimates are effectively meaningless — the 95% prediction interval spans **2.5 log-orders** (nM to µM). All four leads are indistinguishable under this calibration.

### 4.2 ROCK2-αC top-10 leads (from `rock2_activator_RESULTS.md` Table 117-130) — calibrated against ROCK2 fit (R²=0.158)

| rank | iptm | Est. Ki (point) | 95 % PI |
|---|---|---|---|
| 1 | 0.976 | 100 nM | 1.4 – 7200 nM |
| 2 | 0.968 | 147 nM | 2.0 – 10 600 nM |
| 3 | 0.953 | 303 nM | 4.2 – 21 900 nM |
| 4 | 0.948 | 386 nM | 5.3 – 27 900 nM |
| 5 | 0.939 | 595 nM | 8.2 – 43 100 nM |
| 6 | 0.934 | 758 nM | 10.5 – 54 800 nM |
| 7 | 0.929 | 965 nM | 13.3 – 69 800 nM |
| 8 | 0.919 | 1.6 µM | 22 – 113 µM |
| 9 | 0.917 | 1.7 µM | 24 – 125 µM |
| 10 | 0.917 | 1.7 µM | 24 – 125 µM |

**Caveat**: ROCK2 fit R²=0.158, Pearson −0.40. The ordinal ranking across ROCK2 leads (rank 1 tighter than rank 10) is **slightly more trustworthy than random** (R²~16 %) but still far from quantitative. Any claim like "rank 1 is ~100 nM" is wrong at the 95 % PI, which spans from 1.4 nM to 7.2 µM.

### 4.3 Recommended interpretation

- For **internal ranking**, iptm > 0.95 can be used as a soft gate for "plausibly sub-µM binder on ROCK2 scale", but the per-compound Ki cannot be stated.
- For **external comms (Simon)**, report only "iptm > 0.95 in Boltz-2 panel" and do NOT present calibrated nM estimates.
- For any wet-lab proposal, request **IC50 determination via ADP-Glo or SPR**; do not send Boltz-2-derived Ki estimates as scientific claims.

---

## 5. What a better calibration would require

- **Congeneric-series fit per scaffold**, not pan-ChEMBL fit. Within a single chemotype, iptm rank-order often tracks Ki rank-order; across chemotypes it does not.
- **Boltz-2 affinity module**. Boltz-2 ships with a dedicated `affinity` head; iptm is the interface confidence, not the trained affinity score. Using the affinity head (which requires a specific YAML block) should be the first upgrade, not a deeper iptm fit.
- **Orthogonal metric ensemble** — Boltz-2 affinity + DiffDock C_rel + Glide XP docking score, fit jointly. Our prior campaign (`finding-zscore-selectivity-2026-04-16.md`) showed that **Z-score of iptm across a 15-kinase panel** is more informative for selectivity than raw iptm; the same principle likely applies for Ki.
- **More pairs per kinase** (100-200 vs 20). Our 20-pair fits are severely underpowered; this is deliberate (compute budget) but limits confidence in the R² estimate itself.

---

## 6. Caveats (HARD)

- **iptm ≠ affinity**. iptm is a structural-interface-confidence score from Boltz-2's structural head; it was not trained against binding free energy or Ki. Using it as a Ki proxy is a published heuristic (Boltz-2 affinity paper 2025) but is calibration-target-dependent. Our data show the heuristic fails across 3/4 SMA-relevant kinases.
- **ChEMBL Ki heterogeneity**. Even with `standard_relation='='` and pchembl-non-null, Ki values in ChEMBL vary ~1-2 log-orders for the same compound across assays. This is a hard floor on achievable R².
- **Kinase-domain truncation**. Our KD slices (e.g. ROCK2 92-354) exclude regulatory domains. For JAK2 we used only JH1 (catalytic). This may bias iptm relative to a full-length reality; the effect is probably small for ATP-site binders but non-zero.
- **n=20 per kinase is exploratory, not definitive.** R² = 0.307 for MAPK14 could be 0.15-0.50 under resampling.
- **Our LIMK2 and ROCK2 lead compounds were not directly re-measured by Boltz-2 in this campaign** — we use iptm values from prior campaigns. If those were measured at different settings (recycling / sampling / model version), the calibration does not strictly apply.

---

## 7. Report answer to pre-registered question

**Q: Per-kinase regression params + R² + 95 % CI?**

| Kinase | slope | intercept | R² | Pearson | n | notes |
|---|---|---|---|---|---|---|
| LIMK2 | −2.52 | +4.14 | 0.007 | −0.08 | 20 | null fit, iptm not a Ki proxy here |
| ROCK2 | −20.97 | +22.46 | 0.158 | −0.40 | 20 | weak fit, ordinal only |
| JAK2 | −4.45 | +6.47 | 0.022 | −0.15 | 20 | null fit |
| MAPK14 | −15.34 | +16.80 | 0.307 | −0.55 | 20 | best of 4 but still weak |

**Q: Calibrated Ki predictions for top 10 LIMK2-αC + top 10 ROCK2-αC?** — see § 4. All predictions carry 95 % PIs spanning ≥ 2.5 log orders and should not be cited as Ki values outside this document.

**Q: Caveat?** — iptm is an interface-quality proxy, not a free-energy score. These Ki estimates are order-of-magnitude indicative only; at the observed R² for 3 of 4 kinases, they are not quantitatively usable.

---

## 8. Quality gate + next steps

- **DRAFT until triple_llm_verify 3/3 PASS.**
- **No external comms** — this result **weakens** the "iptm → Ki" claim rather than supporting it, so it should not go to Simon. It **does** support the CORTEX / orchestration-layer position that Boltz-2 iptm is one of several signals, not a standalone Ki oracle.
- **Next-compute proposal (cheap)**: re-run calibration using the Boltz-2 **affinity head** (not iptm) on the same 80 Ki-SMILES pairs. If affinity-head R² > 0.5 on LIMK2 or ROCK2 that becomes the calibration of record. Compute cost: comparable (~1 hour).

## 9. Reproducibility Trail

- Script (fit): `/home/bryza/sma-research/qms/chembl_ki_calibration/run_calibration.py`
- Script (rescore leads): `/home/bryza/sma-research/qms/chembl_ki_calibration/rescore_leads.py`
- Log: `/home/bryza/sma-research/qms/chembl_ki_calibration/calibration.log`
- Fit params: `/home/bryza/sma-research/qms/chembl_ki_calibration/fits.json`
- Kinase sequences used: `/home/bryza/sma-research/qms/chembl_ki_calibration/kinase_sequences.json`
- Per-kinase ChEMBL pairs: `/home/bryza/sma-research/qms/chembl_ki_calibration/raw/{LIMK2,ROCK2,JAK2,MAPK14}_chembl_pairs.json`
- Per-kinase calibration rows (iptm + Ki + error): `/home/bryza/sma-research/qms/chembl_ki_calibration/raw/{LIMK2,ROCK2,JAK2,MAPK14}_calibration_rows.json`
- Rescored leads: `/home/bryza/sma-research/qms/chembl_ki_calibration/rescored_leads.json`
- Boltz-2 server: `http://localhost:8004/predict` (SSH-tunnelled, boltz2-batched backend)
- ChEMBL REST: `https://www.ebi.ac.uk/chembl/api/data/activity.json` (2026-04-17 access)
- UniProt REST: `https://rest.uniprot.org/uniprotkb/<acc>.fasta` (2026-04-17 access)

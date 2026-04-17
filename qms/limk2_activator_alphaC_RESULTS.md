# LIMK2 αC-Helix Allosteric Activator Pipeline — RESULTS (DRAFT v4, post-affinity-head)

**Status:** DRAFT — affinity-head rescoring of the full 109-compound library COMPLETE (2026-04-17 evening). Triple-LLM v4 re-run required after this retraction update. External comms remain **BLOCKED**.
**Date:** 2026-04-17 (v4 revision: evening, after ae345009 affinity-head calibration)
**Author:** Opus Master Agent
**Pre-registration:** /home/bryza/sma-research/qms/limk2_downstream_plan.md

---

## 0. §RETRACTION NOTE (added 2026-04-17 evening, Incident 2026-04-17-005)

**The prior §4.1 "Top Hits" table listing 4 iptm-ranked LIMK2-αC leads (14.sdf sel_z +0.86, 43.sdf sel_z +0.83, 176.sdf sel_z +0.15, 3.sdf sel_z +0.01) is RETRACTED as a ranking.**

### What went wrong

Agent ae345009 established (`chembl_ki_affinity_head_RESULTS.md`) that Boltz-2 `iptm` is an interface-quality metric and is **NOT predictive of Ki** for LIMK2 (R² = 0.007 against 20 ChEMBL Ki pairs — indistinguishable from noise). The prior Gate-4 ranking on `z_LIMK2` + `sel_z` used iptm as its underlying signal, so **rank ordering within the library under iptm is statistically equivalent to random for LIMK2 Ki**. The same ae345009 finding showed the Boltz-2 **affinity head** is usable on LIMK2 (R² = 0.690 calibrated against the same 20 Ki pairs), and delivers calibrated Ki predictions.

### Rescoring of the prior top-4

Each of the 4 prior top iptm-ranked leads rescored through the affinity head. Calibration fit (slope 1.249, intercept 3.549, RMSE 0.378 log10-Ki) applied to compute Ki_nM + 95% PI. Binary-binder gate set at `affinity_probability_binary > 0.3`:

| Prior rank | SMILES (first 40) | File | prior iptm | prior sel_z | **affinity_pred_value** | **prob_binary** | **Ki (calibrated)** | 95% PI | Gate |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `COc1cc(C)ccc1C(C)NCC1=CC=[N+]2C1...` | 14.sdf | 0.924 | +0.86 | −0.186 | 0.060 | **2.1 µM** | 380 nM – 11 µM | **FAIL** |
| 2 | `CS(=O)(=O)c1ccccc1-c1cccc(Oc2...` | 43.sdf | 0.942 | +0.83 | +1.679 | 0.048 | **442 µM** | 80 – 2,400 µM | **FAIL** |
| 3 | `CCc1nc2ccc[nH+]c2cc1OCc1ccc2...` | 176.sdf | 0.915 | +0.15 | +0.747 | 0.076 | **30 µM** | 5.5 – 170 µM | **FAIL** |
| 4 | `COc1cc(OC)c(OC)c(C(=O)N2CCN(...` | 3.sdf | 0.910 | +0.01 | +1.630 | 0.070 | **380 µM** | 70 – 2,100 µM | **FAIL** |

**All 4 prior top-4 FAIL the binary-binder gate (prob < 0.3).** None is a credible nanomolar LIMK2 binder. The Arm-1 Simon-pack recommended lead (43.sdf) is particularly affected — calibrated Ki ~442 µM, 30-10,000× weaker than originally implied by iptm-based ranking. This invalidates the prior "top hit" interpretation.

### Full-library affinity-head rerun (this retraction supersedes the old rank)

All 109 BBB-filtered compounds rescored via Boltz-2 affinity head on sma-h100-two (12m 12s affinity + 4m 29s structural, H100 PCIe, $0 marginal). 99/109 successful (10 PocketXMol-incomplete SMILES rejected by RDKit). Binary-binder gate applied.

**Compounds passing `affinity_probability_binary > 0.3`: 4 of 99 (4.0 %).**

| rank | SMILES | File | prior C_rel | Ki (nM) | 95 % PI | prob_binary | aff_pred | iptm_new | z-gate(prior panel) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `CNc1cc2c(c3ccc[nH+]c13)=CC1=CC(OCCc3cccc[nH+]3)=CNC1=CC=2` | 539.sdf | −0.278 (fail Gate 3) | **1.1 µM** | 198 nM – 6.0 µM | 0.309 | −0.409 | 0.953 | not in prior panel |
| 2 | `Oc1cccc(-c2cc(N3CCc4ncc5ccccc5c4C3)ncn2)c1` | 374.sdf | −0.257 (fail Gate 3) | **1.4 µM** | 251 nM – 7.6 µM | 0.307 | −0.328 | 0.953 | not in prior panel |
| 3 | `COc1ccc(O)c(NC(=O)C=Cc2cccc(-c3cnccn3)c2)c1` | 1.sdf | −0.792 (fail Gate 3) | **4.4 µM** | 800 nM – 24 µM | 0.314 | +0.075 | 0.931 | not in prior panel |
| 4 | `Cn1cccc1C(=O)c1cccc(Oc2ccc(-c3cnccn3)nn2)c1` | 162.sdf | +0.054 (pass Gate 3) | **15 µM** | 2.7 – 83 µM | 0.320 | +0.504 | 0.919 | not in prior panel |

### Honest conclusion

**The LIMK2-αC PocketXMol library contains NO compound that is simultaneously (a) a binary-binder under Boltz-2 affinity head (prob > 0.3), (b) sub-µM in calibrated Ki, and (c) selectivity-positive by prior 15-kinase panel z-scores.**

- The 4 binary-binder survivors are all µM-range (1.1 – 15 µM point estimates; 95 % PIs extend into tens of µM). None is nanomolar.
- **0 of 4 survivors pass the prior z-score selectivity gate** (z_LIMK2 > 0 AND sel_z > 0) — because the 4 survivors were not among the 15 compounds that got a full 15-kinase panel in the prior pipeline (top_hits.tsv had 15 rows; bbb_filtered had 109). z-score on the 4 survivors is unavailable.
- 3 of 4 survivors (ranks 1, 2, 3) FAILED the prior DiffDock C_rel > 0 geometry gate (C_rel −0.28, −0.26, −0.79 respectively). Only rank 4 (15 µM) passed the prior Gate 3.
- The best numerical calibrated-Ki survivor (1.1 µM rank-1, 539.sdf) is a PocketXMol-generated pyridinium/dihydroquinoline polyconjugated cation — **two [nH+] and a conjugated C=C/C=N system**. This is a protonation/tautomer artefact, not a clean drug-like lead. The neutralised form must be redocked + rescored before any interpretation.

### Action

1. **Arm 1 of the Simon pack narrative (LIMK2-αC activator "recommended lead 43.sdf") is retracted** as an actionable lead. Lead-rank change from iptm-based to affinity-head-based has inverted the selection — 43.sdf is the *worst* of the four former top-4 under the affinity head (442 µM).
2. **Library requires redesign**. PocketXMol αC-helix generation with DFG-out 4TPT anchoring did not produce a nanomolar binder. Recommended next pipeline: co-crystal Asp460-oriented scaffolds, PocketXMol seeded from LIMKi3 fragment, or alternative anchoring strategy. Budget for redesign: ~22 min Boltz-2 affinity run per 100-compound batch.
3. **Do NOT advance any compound from this library to wet-lab.** 
4. **Corrections**: this RESULTS file section §4 (old top-4) flagged as RETRACTED. `LIMK2_NEW_STORY_FOR_SIMON.md` Arm 1 narrative updated accordingly. Simon-Comms-Gate remains HELD.

### Files

- Rescoring script: `/home/bryza/sma-research/qms/limk2_affinity_rerun/rescore.py`
- Full rescored table: `/home/bryza/fleet-results/limk2_activator_alphaC/full_affinity_ranked_v2.tsv` (all 99 compounds, sorted by log10 Ki)
- Binary-binder gate survivors: `/home/bryza/fleet-results/limk2_activator_alphaC/top_hits_affinity_v2.tsv` (4 compounds)
- Raw Boltz-2 outputs: `/home/bryza/sma-research/qms/limk2_affinity_rerun/boltz_out/` (99 affinity + 99 confidence JSONs)
- Fits-of-record: `/home/bryza/sma-research/qms/chembl_ki_affinity_head/fits.json` (LIMK2 slope 1.249, intercept 3.549, RMSE 0.378, R² 0.690)
- Remote run log: `sma-h100-two:/home/shadeform/limk2_affinity_rerun/run.log`

### Cross-reference

- Incident 2026-04-17-005 entry in `CORRECTIONS_LOG.md` (SMA QMS corrections ledger)
- Calibration rationale: `chembl_ki_affinity_head_RESULTS.md` § 3.1 (iptm vs affinity head head-to-head, LIMK2 row)

---

## 1. HARD CAVEATS (read first)

1. **§0 RETRACTION supersedes the old §4 top-4 ranking.** iptm-based ranking for LIMK2 Ki selection is invalid (R² = 0.007 vs ChEMBL Ki per ae345009). Use the affinity-head gate in §0 for any LIMK2 lead decision from this library.
2. **LIMK2 direction in SMA MN is model-system-dependent** (today's 3-dataset DESeq2 meta-analysis; see /home/bryza/sma-research/qms/meta_analysis/). iMN/iN → DOWN (favors activator); SH-SY5Y → UP (favors inhibitor). This activator compute is **exploratory**. Inhibitor arm should not be shelved.
3. **Gate 4 (old) Boltz-2 15-kinase panel is now DEPRECATED** as a primary selection gate. It remains a useful *secondary triangulator* for off-target geometry: a compound still needs `z_LIMK2 > 0` to be considered LIMK2-preferring on pose geometry. Under the new design, the primary gate is `affinity_probability_binary > 0.3`, with z-score panel run as triangulation on survivors. Current library produces 4 binary-binder survivors, 0 of which have z-score panel data (they were not in the 15-compound iptm-top subset that got paneled). See §0.
4. **Every numeric value below is DRAFT.** Not for external comms.
5. **Boltz-2 iptm = interface-quality metric, NOT Ki.** High iptm means self-consistent ligand-protein interface geometry. It does **not** quantify affinity. Used ONLY as row-wise panel geometry proxy for off-target distinction. NEVER as LIMK2 affinity ranking signal (see ae345009).
6. **Boltz-2 affinity head (affinity_pred_value + affinity_probability_binary)** is the correct primary Ki metric for LIMK2 under the calibrated R² = 0.690 fit. §0 applies this fit (slope 1.249, intercept 3.549, RMSE 0.378 log10-Ki ≈ ±2.4× multiplicative Ki uncertainty).
7. **DiffDock confidence ≠ docking score.** It is a pose-realism scalar. C_rel > 0 means "better-looking pose than LIMKi3 on 4TPT", it is NOT "better binder than LIMKi3".

---

## 2. Pipeline Funnel (QMS audit)

| Gate | Rule | n_before | n_after | dropped |
|---|---|---|---|---|
| 0 | PocketXMol generation (ssh7 A100, 600 samples) | 600 | 469 valid | 131 (89 incomp + 42 bad) |
| 1 | RDKit validity + unique canonical SMILES | 600 | 558 | 42 invalid, 0 dups |
| 2 | BBB hardfilter (TPSA<90, MW<450, 1≤logP≤4, HBD≤3) | 558 | **109** | 449 |
| 3 | DiffDock C_rel > 0 (4TPT, LIMKi3-calibrated) | 109 | **43** | 66 |
| 4 | Boltz-2 15-kinase z_LIMK2>0 AND selectivity_z>0 (fully-scored compounds only) | 43 | 4/4 (of 4 fully scored) | pending 39 more compound-panels |
| 5 | Sort by selectivity_z desc | 4 | **4** | — |

Audit trail: `/home/bryza/fleet-results/limk2_activator_alphaC/filter_log.jsonl`

---

## 3. LIMKi3 DiffDock Reference (Gate 3 calibration)

| Quantity | Value |
|---|---|
| Canonical SMILES | `Nc1ccc2cc(Nc3ccc(C(=O)Nc4ccccc4)cc3)c(Cl)cc2n1` |
| PubChem CID | 11525740 |
| Target PDB | 4TPT (DFG-out LIMK2) |
| In-run best confidence over 10 poses | **−0.5642** |
| Historical baseline (memory) | −0.521 |
| Delta vs historical | −0.043 (8% low) |

In-run value reproduces historical within tolerance. Used for all C_rel computations.

---

## 4. Top Hits (DRAFT — 4 of 43 compound-panels complete)

> ⚠️ **SECTION 4 IS RETRACTED AS A LEAD RANKING** (2026-04-17 evening, Incident 2026-04-17-005). The iptm-based top-4 in §4.1 below are NOT nanomolar binders. See §0 Retraction Note for the affinity-head rescoring and the new 4-survivor table. Section 4 is kept unmodified below for audit history only.

### 4.1 Currently passing Gate 4 (gate-consistent, NOT independently triangulated) — **RETRACTED**

| Rank | SMILES | File | MW | TPSA | logP | HBD | dd_conf | C_rel | iptm_LIMK2 | z_LIMK2 | sel_z |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `COc1cc(C)ccc1C(C)NCC1=CC=[N+]2C1=Nc1c[n+](Cc3cncc[nH+]3)ccc12` | 14.sdf | 427.5 | 67.5 | 2.60 | 1 | −0.561 | **+0.003** | 0.924 | +0.80 | **+0.86** |
| 2 | `CS(=O)(=O)c1ccccc1-c1cccc(Oc2ccc(C(N)=O)cc2)c1` | 43.sdf | 367.4 | 86.5 | 3.65 | 1 | −0.463 | **+0.101** | 0.942 | +0.78 | **+0.83** |
| 3 | `CCc1nc2ccc[nH+]c2cc1OCc1ccc2[nH]cc(C(=O)O)c2c1` | 176.sdf | 348.4 | 89.4 | 3.37 | 2 | −0.319 | **+0.245** | 0.915 | +0.14 | **+0.15** |
| 4 | `COc1cc(OC)c(OC)c(C(=O)N2CCN(C(=O)c3ccncc3)CC2)c1` | 3.sdf | 385.4 | 81.2 | 1.71 | 0 | −0.363 | **+0.198** | 0.910 | +0.01 | **+0.01** |

### 4.2 Interpretation (DRAFT)

- **#1 (14.sdf), sel_z = +0.86:** Strongest selectivity_z, but pyridinium + imidazolium charges (`[N+]`, `[nH+]`) are **protonation artefacts from PocketXMol's SDF generation**. They may not survive QM/MM neutralization; iptm may be inflated by electrostatic stabilization that does not exist in the neutral species. **Action: QM/MM recheck + neutral-form redock before any downstream compute.**
- **#2 (43.sdf), sel_z = +0.83:** Cleanest drug-like scaffold — diaryl ether + sulfone + primary amide, neutral at physiological pH. **Best candidate for 20 ns MD follow-up.**
- **#3 (176.sdf), sel_z = +0.15:** Indole-2-carboxylic acid tethered to ethyl-quinoline via benzyl ether. `sel_z` is at noise-floor of a 15-kinase panel (null σ ≈ 1.04). **Not above noise; should not be advanced without repeat measurement.**
- **#4 (3.sdf), sel_z = +0.01:** Piperazine-dimethoxy-isonicotinamide. Passes gate by margin; at noise floor. **Discard unless re-measurement moves it up.**

### 4.3 Effect-size reality

Under null distribution (15 iptm values drawn from the same distribution), σ(selectivity_z) ≈ sqrt(1 + 1/14) ≈ 1.04. So:
- sel_z = +0.86 (hit #1) ≈ 0.83 σ from null mean — meaningful but not overwhelming
- sel_z = +0.83 (hit #2) ≈ 0.80 σ — similar
- sel_z = +0.15 (hit #3) ≈ 0.14 σ — **within noise**
- sel_z = +0.01 (hit #4) ≈ 0.01 σ — **noise**

**No hit qualifies as a "strong" selectivity signal by panel Z-score alone.** The two candidates worth further compute are #1 (pending neutralization) and #2 (neutral-already, most recommendable for MD).

### 4.4 Comparison vs prior programme leads

- Previous best LIMK2 sel_z in this programme: +0.75 (session 2026-04-16, GenMol LIMKi3-hop scaffold). Current #1 (+0.86) exceeds this but is protonation-compromised; current #2 (+0.83) is comparable and clean.

---

## 5. Orthogonal validation (TBD — NONE DONE YET)

| Method | Status | Purpose |
|---|---|---|
| 20 ns holo MD in LIMK2 4TPT | NOT DONE | pose-stability, hinge-ratio, protonation check |
| FEP+ ΔΔG | NOT DONE | affinity scoring |
| ChEMBL Ki calibration | NOT DONE | iptm → Ki map |
| Experimental Ki, thermal shift | NOT DONE | gold standard |
| Inhibitor-arm parallel compute | NOT DONE | for direction-of-change disambiguation |

**We do NOT claim validated LIMK2-selective activators.**

---

## 6. Gate 4 Panel Statistics (current JSONL state)

- Total attempts: 399
- Successful (status=ok): 284
- Retries exhausted (status=err/retries_exhausted): 115
- Unique compounds with at least 1 successful measurement: 26
- Unique compounds with full 15-kinase panel: 4

Server instability timeline (for audit):
- 09:18 UTC: panel v1 started via h100-two:8003 self-host
- ~09:40: self-host restarted (lost in-flight), panel v1 reached 360/645 in JSONL (in-memory state lost on kill)
- ~10:14: panel v2 started on hosted NIM with resumable JSONL
- 10:18, 10:21: self-host h100-two:8003 restarted twice more
- 10:44: panel v2 re-launched (resume logic fixed — previously `status != ok` entries were falsely marked done)
- Ongoing: panel v2 (PID 1584206) running, 367 new calls remaining

---

## 7. Next Steps

1. **Let v2 finish** (ETA 40-60 min from re-launch).
2. **Re-run finalizer** `/tmp/build_panel_csv_and_hits_v2.py` after that, which SMILES-matches JSONL to DD results.
3. **Triple-LLM v3** on the finalized report.
4. **MD follow-up on #2 (43.sdf)** — the cleanest drug-like hit. 20 ns LIMK2 4TPT holo.
5. **Neutral-form redock of #1 (14.sdf)** after QM/MM neutralization.
6. **Do NOT send to Simon / Torsten / any external channel** until these steps complete.

---

## 8. File Manifest

- `/home/bryza/fleet-results/limk2_activator_alphaC/gen_info.csv` — raw PocketXMol (600)
- `/home/bryza/fleet-results/limk2_activator_alphaC/bbb_filtered.csv` — Gate 1+2 (109)
- `/home/bryza/fleet-results/limk2_activator_alphaC/diffdock_results.csv` — Gate 3 (109 docks; 43 C_rel>0)
- `/home/bryza/fleet-results/limk2_activator_alphaC/diffdock_reference.json` — LIMKi3 baseline (−0.5642)
- `/home/bryza/fleet-results/limk2_activator_alphaC/boltz2_kinase_panel.csv` — Gate 4 matrix (43 × 15, partial)
- `/home/bryza/fleet-results/limk2_activator_alphaC/boltz2_results.jsonl` — RESUMABLE source-of-truth
- `/home/bryza/fleet-results/limk2_activator_alphaC/top_hits.tsv` — Gate 5 sorted
- `/home/bryza/fleet-results/limk2_activator_alphaC/filter_log.jsonl` — per-gate counts
- `/tmp/boltz2_panel_v2.py` — resumable panel runner (fixed: retries failed calls)
- `/tmp/build_panel_csv_and_hits_v2.py` — finalizer (SMILES-matched)

---

## 9. QMS Sign-off

- Pre-registration: signed 2026-04-17 pre-compute.
- Dataset verify: passed (all SMILES trace to gen_info.csv via filename).
- DRAFT status: YES.
- Triple-LLM gate (v1, v2): **1/3 PASS each**. Persistent BLOCKS are the protonation-artefact and incomplete-panel flags, both of which ARE documented in this file.  External comms BLOCKED.

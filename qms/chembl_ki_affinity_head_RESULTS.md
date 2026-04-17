# ChEMBL Ki Calibration — Boltz-2 Affinity Head (Rescue of the Null iptm Calibration)

**Status:** DRAFT (pending triple_llm_verify). INTERNAL — Simon-Comms-Gate HELD.
**Date:** 2026-04-17
**Task ID:** `chembl_ki_affinity_head`
**Rescue of:** `chembl_ki_calibration_RESULTS.md` (iptm null, agent `a31633bf`)
**Compute:** Boltz-2 affinity head (`properties: - affinity: binder: L1`) on sma-h100-two (H100 PCIe 80 GB). CLI batch-dir mode, recycling=1, sampling=25 (struct) + sampling_steps_affinity=100, diffusion_samples_affinity=3. `boltz2_aff.ckpt` self-hosted.
**Runtime:** 10 min 04 s for 80 inputs (structural + affinity); 4 min 36 s for 14 leads. Total wall ≈ 15 min. $0 marginal (self-host).

---

## 1. Endpoint decision

- Checked the batched server at `localhost:8003/8004` (`boltz2_batch_server.py` on sma-h100-two). It writes YAMLs without the `properties:` block and never invokes the affinity checkpoint — it exposes only iptm / ptm / plddt. **Affinity is not reachable through the current HTTP server.**
- Pivoted to **direct `boltz predict` CLI over SSH in tmux** on sma-h100-two, using affinity-enabled YAML. 80 inputs in a single batch-dir call, 10 min 04 s wall (same machine, same checkpoint that the HTTP server uses).
- Weight file already cached: `/home/shadeform/.boltz_cache/boltz2_aff.ckpt`. No download, no $ burn.

**Endpoint used:** Boltz-2 CLI `boltz predict --model boltz2` with `properties: - affinity: binder: L1` in each input YAML. `affinity_pred_value` (log-molar, IC50/Ki-like scale) parsed from `predictions/<jobid>/affinity_<jobid>.json`.

---

## 2. Inputs

Re-used the **identical 80 (SMILES, Ki_nM) pairs** from `chembl_ki_calibration/raw/<kinase>_calibration_rows.json` — LIMK2, ROCK2, JAK2, MAPK14, 20 diverse ChEMBL Ki pairs each. Same kinase-domain sequences from `kinase_sequences.json`. This is an apples-to-apples replacement of the iptm proxy with the trained affinity head.

---

## 3. Per-kinase linear fits: `log10(Ki_nM) = slope · affinity_pred_value + intercept`

Positive slope is expected because `affinity_pred_value` is reported by Boltz-2 as log(IC50) in molar units (≈ −pKi), so a tighter binder emits a **more negative** affinity value and a **lower** log10(Ki_nM).

| Kinase | slope | intercept | R² | Pearson r | n | RMSE (log₁₀ Ki) | slope 95 % CI |
|---|---|---|---|---|---|---|---|
| LIMK2  | +1.249 | +3.549 | **0.690** | +0.831 | 20 | 0.378 | [+0.834, +1.664] |
| ROCK2  | +0.880 | +2.960 | **0.528** | +0.726 | 20 | 0.693 | [+0.468, +1.293] |
| JAK2   | +0.884 | +2.627 | **0.392** | +0.626 | 20 | 1.108 | [+0.338, +1.429] |
| MAPK14 | +0.961 | +2.695 | **0.544** | +0.737 | 20 | 1.010 | [+0.525, +1.396] |

### 3.1 Head-to-head: iptm proxy vs affinity head

| Kinase | R² iptm (old) | R² affinity_pred_value (new) | Δ | Gate |
|---|---|---|---|---|
| LIMK2  | 0.007 | **0.690** | +0.683 | **USABLE (R² ≥ 0.5)** |
| ROCK2  | 0.158 | **0.528** | +0.370 | **USABLE (R² ≥ 0.5)** |
| JAK2   | 0.022 | 0.392 | +0.370 | PARTIAL (0.3-0.5, rank only) |
| MAPK14 | 0.307 | **0.544** | +0.237 | **USABLE (R² ≥ 0.5)** |

**The affinity head rescues the calibration for 3 of 4 kinases.** LIMK2 — the headline SMA target — went from R²=0.007 (statistical noise) to R²=0.690 (a strong Ki predictor). ROCK2 crossed the R²≥0.5 "usable" gate. JAK2 remains PARTIAL; the wide Ki range (−1 to +5 log10) and likely data heterogeneity limit the fit, but Pearson +0.63 is still well above noise.

### 3.2 Alternative: `affinity_probability_binary` (binary binder/non-binder head)

Tested as a secondary metric. For ROCK2, JAK2, MAPK14 it is competitive with `affinity_pred_value`; for LIMK2 it is much worse (R²=0.16). `affinity_pred_value` is the recommended primary.

| Kinase | R² (affinity_pred_value) | R² (affinity_probability_binary) |
|---|---|---|
| LIMK2  | **0.690** | 0.155 |
| ROCK2  | **0.528** | 0.474 |
| JAK2   | 0.392 | **0.449** |
| MAPK14 | 0.544 | **0.554** |

---

## 4. Lead rescoring against calibrated fits

Re-ran the 14 prior top leads (LIMK2-αC 4 + ROCK2-αC 10) through the affinity head, then applied the per-kinase fit to get calibrated Ki_nM estimates with 95 % prediction intervals.

### 4.1 LIMK2-αC top-4 (prior iptm ranking, R²=0.007 → noise)

| rank | SMILES (first 40 chars) | prior iptm | affinity_pred_value | affinity_prob_bind | **Ki (calibrated)** | 95 % PI |
|---|---|---|---|---|---|---|
| 1 | COc1cc(C)ccc1C(C)NCC1=CC=[N+]2C1... | 0.924 | −0.186 | 0.060 | **2.1 µM**  | 380 nM – 11 µM |
| 2 | CS(=O)(=O)c1ccccc1-c1cccc(Oc2...  | 0.942 | +1.679 | 0.048 | **440 µM** | 80 – 2 400 µM |
| 3 | CCc1nc2ccc[nH+]c2cc1OCc1ccc2...   | 0.915 | +0.747 | 0.076 | **30 µM**  | 5.5 – 170 µM |
| 4 | COc1cc(OC)c(OC)c(C(=O)N2CCN(...   | 0.910 | +1.630 | 0.070 | **380 µM** | 70 – 2 100 µM |

**Finding: the prior iptm-based top-4 LIMK2 leads are NOT nanomolar binders.** Rank-1 is ~2 µM (best), rank-2 and rank-4 are sub-mM at best. The prior report estimated all four at ~65 nM (based on the null R²=0.007 fit); the affinity-head estimate is **30 ×–10 000 × weaker**, consistent with the iptm-ranking being essentially random against LIMK2 Ki.

None of the 4 has `affinity_probability_binary > 0.5` — the Boltz-2 binary head itself agrees these are not confident LIMK2 binders. Under the new calibration, **the LIMK2-αC campaign produces no µM-grade LIMK2 lead** from these 4 compounds.

### 4.2 ROCK2-αC top-10 (prior iptm ranking, R²=0.158 → weak)

| rank | prior iptm | affinity_pred_value | affinity_prob_bind | **Ki (calibrated)** | 95 % PI |
|---|---|---|---|---|---|
| 1  | 0.976 | −1.000 | 0.435 | **120 nM**  | 5.3 – 2 700 nM |
| 2  | 0.968 | +0.876 |  0.056 | **5.4 µM**  | 0.24 – 120 µM |
| 3  | 0.953 | −0.520 |  0.140 | **318 nM**  | 14 – 7 200 nM |
| 4  | 0.948 | +0.918 |  0.044 | **5.9 µM**  | 0.26 – 130 µM |
| 5  | 0.939 | +0.495 |  0.268 | **2.5 µM**  | 0.11 – 57 µM |
| 6  | 0.934 | −0.400 |  0.081 | **405 nM**  | 18 – 9 200 nM |
| 7  | 0.929 | **−1.217** | **0.249** | **77 nM**   | 3.4 – 1 800 nM |
| 8  | 0.919 | **−1.186** | 0.157 | **82 nM**   | 3.6 – 1 900 nM |
| 9  | 0.917 | +0.324 |  0.320 | **1.8 µM**  | 0.077 – 40 µM |
| 10 | 0.917 | +0.549 |  0.289 | **2.8 µM**  | 0.12 – 63 µM |

**Finding: ROCK2 shows rank scrambling under the affinity head.** Prior iptm-rank 7 (ROCK2 #7, SMILES `CC1CCCC(=CCNN2Cc3nccn4c3c(c3cc(N)ccc34)C2)C1=O`) emerges as the tightest calibrated binder (~77 nM, 95 % PI 3.4–1 800 nM), followed by #8 (82 nM), #1 (120 nM), #3 (318 nM), #6 (405 nM). iptm-ranks 2, 4 are weaker than 1/3/6/7/8. The **iptm top-1 does survive as a plausible sub-µM binder** (120 nM, but 95 % PI spans 5 nM – 2.7 µM), and the ROCK2 list contains 5 compounds with calibrated Ki < 500 nM (ranks 1, 3, 6, 7, 8).

The `affinity_probability_binary` signal for ROCK2 #1 is 0.435 — the strongest "binder probability" of the 14 leads, consistent with it being the cleanest ROCK2 lead. Ranks 5, 9, 10 have binary probabilities 0.27–0.32 (borderline). All others are ≤ 0.16.

### 4.3 Rescoring recommendation

- **LIMK2 campaign**: None of the 4 iptm-ranked leads is a credible nM LIMK2 binder under affinity-head calibration. **Do not advance any of these to wet-lab without re-screening**. Either re-filter the PocketXMol library (+ Boltz-2 iptm ≥ 0.95) through the affinity head, or de-prioritise LIMK2-αC in favor of a different target/mechanism.
- **ROCK2 campaign**: rank-1, rank-3, rank-6, rank-7, rank-8 all have calibrated Ki < 500 nM point estimates. Rank-7 and rank-8 are the best on log-Ki (77 / 82 nM) but have lower `affinity_probability_binary` (0.25 / 0.16) — recommend triangulating rank-1 (120 nM Ki, 0.435 prob-binder, top iptm) with rank-7 as a secondary back-up. All need wet-lab IC50 determination.

File: `rescored_leads_affinity.json` in this folder.

---

## 5. Caveats

- `affinity_pred_value` is Boltz-2's regression head trained on published pKi/pIC50 data. It is **not a free-energy score** — it's an ML prediction of an experimental label. For novel chemotypes outside training distribution, residuals may be larger than the RMSE here suggests. RMSE on log10(Ki_nM) is 0.38 (LIMK2), 0.69 (ROCK2), 1.11 (JAK2), 1.01 (MAPK14) — corresponding to a ~2.4× / 4.9× / 13× / 10× multiplicative Ki uncertainty even within the calibrated regime.
- n=20 per kinase is still a small calibration set. R² estimates have non-trivial uncertainty (bootstrap 95 % CI likely ±0.15). Bigger calibration sets (n=100) would tighten this, but at 10 min / 80 samples the marginal cost is low — a 400-sample calibration (100/kinase) is ~50 min on the same H100.
- Same kinase-domain truncation caveats as the iptm report (e.g. ROCK2 92–354 excludes regulatory coiled-coil; JAK2 JH1 only).
- ChEMBL Ki heterogeneity unchanged — a ~0.5–1 log-order floor on achievable RMSE is inherent to ChEMBL itself, independent of the model.
- Lead rescoring uses a single affinity-head inference per lead (3 diffusion samples averaged internally). Variance across seeds not quantified here; consider running 3 independent seeds on the final 5 ROCK2 leads before wet-lab.
- The affinity head was **trained by the Boltz-2 team on a distinct split**; these 80 ChEMBL pairs may overlap the training set. This would bias R² optimistically. The observed R² should be treated as an **upper bound** on out-of-distribution performance. Mitigation: future calibration should use compound-scaffold-out splits or a held-out ChEMBL subset post-training-cutoff.

---

## 6. Gate decision

| Kinase | iptm R² | affinity R² | Verdict |
|---|---|---|---|
| **LIMK2**  | 0.007 | **0.690** | **USABLE** — orchestration-layer calibration switches from iptm-proxy to affinity-head for LIMK2 Ki reporting. |
| **ROCK2**  | 0.158 | **0.528** | **USABLE** — same; ROCK2 affinity-head calibration of record. |
| MAPK14 | 0.307 | **0.544** | USABLE (sanity check, not a primary SMA target). |
| JAK2   | 0.022 | 0.392 | PARTIAL — rank-only. Do not cite Ki nM for JAK2 leads. |

---

## 7. Orchestration-layer recommendation

**Update `plan-sma-orchestration-layer-2026-04-16.md` Phase 1.2 and `plan-sma-orchestration-layer` / SMA-Score ranker v1:**

1. **Replace iptm → Ki linear fit** (null, R²=0.007–0.307) **with the affinity_pred_value → Ki linear fit per kinase**. Store `fits.json` as the calibration-of-record. Boltz-2 affinity head requires the `properties: - affinity: binder: <ligand_id>` YAML block; a self-hosted CLI batch run on sma-h100-two is the current-minimum path.
2. **Expose the affinity head via the HTTP server**: patch `boltz2_batch_server.py` to accept `include_affinity: true` in the request body and inject the `properties` block into the generated YAML, then parse `affinity_<job_id>.json` and return `affinity_pred_value` + `affinity_probability_binary` in the response. Estimated work: ~1 hour. Until then, the SMA-Score ranker should call the CLI in a subprocess or write directly to `/home/shadeform/affinity_calib/in` → trigger run → read `affinity_*.json`. Marginal cost per compound: ~5 s affinity + ~7 s structural on a cold batch of 80.
3. **Dual-metric ranking**: use `affinity_pred_value` as the primary ordinal signal **plus** `affinity_probability_binary > 0.3` as a binary gate (ROCK2 top-1 = 0.435, top-3/6 = 0.14/0.08 — the binary head distinguishes confident binders from weak ones independently). Report both.
4. **Flag the LIMK2-αC finding upstream**: the prior top-4 LIMK2-αC leads (ranked by iptm 0.91–0.94) are NOT sub-µM LIMK2 binders under the affinity head (2 µM – 440 µM range). This invalidates the iptm-based rank for LIMK2 selection. Rerun the PocketXMol library through the affinity head, not iptm. This is a ~20-minute compute on H100 for a 275-compound library.
5. **Retract/correct** the iptm-based Ki estimates in any internal document that used them (`rescored_leads.json` — the 65/59/69/71 nM LIMK2 points are wrong). Update `chembl_ki_calibration_RESULTS.md` § 4.1 with a correction note pointing here. Log in `CORRECTIONS_LOG.md`.
6. **Calibration refresh cadence**: re-run calibration quarterly or whenever Boltz-2 model weights update, n=100 per kinase.

---

## 8. Reproducibility Trail

- YAML builder: `build_yamls.py` (same folder)
- Fit + comparison: `fit_affinity.py` (same folder)
- Lead rescorer: `rescore_leads.py` (same folder)
- 80 raw YAMLs in: `yaml_in/`
- Boltz-2 outputs (affinity + confidence JSONs) in: `boltz_out/` (rsynced from sma-h100-two `/home/shadeform/affinity_calib/out_full`)
- Lead outputs in: `leads_boltz_out/`
- Per-kinase annotated rows: `raw/<kinase>_affinity_rows.json`
- Fit params: `fits.json`
- Fit params (probability_binary): `fits_probability.json`
- Iptm vs affinity comparison: `fits_comparison.json`
- Rescored leads (14 compounds, calibrated Ki + 95 % PI): `rescored_leads_affinity.json`
- Boltz version: self-hosted `/home/shadeform/miniconda3/envs/pxm_cu128/bin/boltz predict` + `boltz2_aff.ckpt` (cached).
- Hardware: sma-h100-two (shadeform brev), single H100 PCIe 80 GB. tmux session `boltz_affinity`.
- Run log: `/home/shadeform/affinity_calib/run.log` (remote), `logs/` (local TBD on next pull).

---

## 9. Quality gate + next steps

- **DRAFT until triple_llm_verify 3/3 PASS.**
- **No external comms** — this result is internal-methodology-update, not a scientific claim to ship. It materially tightens and in some cases inverts prior LIMK2/ROCK2 lead rankings, so it strengthens the Simon-Comms-Gate HOLD.
- **Immediate next compute (cheap)**:
  1. Rerun the **full PocketXMol LIMK2 library** (275 compounds) through the affinity head on the same batch CLI — ~22 min on H100. This gives the first LIMK2-selective lead under a calibrated Ki proxy.
  2. Patch `boltz2_batch_server.py` for `include_affinity: true` so future campaigns don't bypass the HTTP worker.
  3. Expand calibration to n=100/kinase to tighten R² estimates.

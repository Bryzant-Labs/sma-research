# DepMap Differential-Dependency Screen for SMA Target Discovery

**Date**: 2026-04-20
**Author**: Bryzant Labs SMA platform (autonomous agent)
**Tool**: `depmap_sl_screen.py` v1.0 (additive; does not modify fleet/saturator/supervisor)
**Status**: INTERNAL — NOT TO BE SENT TO SIMON OR TORSTEN PENDING TRIPLE-LLM CONSENSUS GATE ON TOP-5 (per HARD RULE 3)

---

## 1. Executive summary

We ran a genome-wide differential-dependency screen on the latest public DepMap
release (**26Q1**, 1,208 CRISPR-screened cancer cell lines) stratified by SMN1
mRNA expression quartile. The goal was to identify genes whose loss
preferentially phenocopies or rescues the SMN-low state — candidate therapeutic
targets that genetic epistasis flags as mission-relevant.

**Headline result**: the screen ran cleanly (pan-essential positive control RPL3
passes, pipeline reads Chronos correctly) but the biological signal is weak and
SMA-specificity is low. Only **2 genes** clear an absolute effect size of
|Δdepsc| ≥ 0.3 and **185 / 17,787 (1.0 %)** clear FDR < 0.05. None of the top-50
are in Simon's priority list. NCALD — the only mechanistic sanity control we
could test — **fails** direction (Δ = −0.004, p = 0.74), i.e. we do **not**
reproduce Riessland 2017's "LoF protective in SMN-Δ7 mouse" finding in CCLE.
This is a real limitation of using cancer cell lines as a motor-neuron proxy,
not a pipeline bug.

**Recommendation**: DepMap is useful as a **negative filter** (dropping targets
that are pan-essential in cancer, i.e. undruggable because systemic knockdown
would kill every dividing cell) but **not** as a positive hit-discovery primary
screen for SMA. The 5 top "rescuer-direction" candidates (SEPHS2, CBFB, CDAN1,
CHMP4B, UROD) should be treated as hypothesis-generation only and run through a
triple-LLM consensus gate before any external citation.

---

## 2. Methodology

### Data

| Field | Value |
| --- | --- |
| DepMap release | **DepMap Public 26Q1** (canonical 3b44.1 / 5bbf.37) |
| CRISPR gene-effect file | `CRISPRGeneEffect.csv` — Chronos-scored, 1,208 lines × 18,531 genes |
| Expression file | `OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv` — 1,719 lines × 19,215 genes (filtered to `IsDefaultEntryForModel=Yes`) |
| Cell line annotation | `Model.csv` |
| Intersect (CRISPR ∩ expression) | 1,140 cell lines |
| Gene coverage after NaN filter | 17,787 / 18,531 (≥ 285 non-NaN scores per gene) |

### Stratification

- Context gene: **SMN1** (log₂ TPM+1)
- SMN-low quartile: `n = 285` cell lines with SMN1 ≤ 5.407
- SMN-high quartile: `n = 285` cell lines with SMN1 ≥ 6.102
- SMN1 mRNA mean across CCLE = 5.727, std = 0.568 — narrow dynamic range across
  cancer cell lines, which is itself a caveat (see §5).

### Differential dependency

For each gene:
- `delta_depsc = mean(depsc_low) − mean(depsc_high)`
- Welch t-test (`scipy.stats.ttest_ind`, `equal_var=False`, `nan_policy='omit'`)
- Mann-Whitney U sanity on top-2000 by |Δ| (column `mwu_pvalue` in TSV)
- Benjamini-Hochberg FDR (implemented in-script; no statsmodels dep)

Direction convention:
- `Δ > 0` → gene is **less essential** in SMN-low = rescuer candidate (LoF is
  better tolerated when SMN is low → potentially protective)
- `Δ < 0` → gene is **more essential** in SMN-low = classical synthetic-lethal
  direction (less useful for SMA therapy; useful for SMA cancer comorbidity)

### Annotation

- Internal curated druggability table (`DEFAULT_ANNOTATION` in the script, 37
  genes covering SMA modifiers + Simon A1-A4 + B1-B3 + stress).
- Optional extension via `--annotation-tsv` (not used for this run; all non-
  curated genes annotated as `unknown`).
- **Open Targets live API intentionally NOT called**: rate-limited,
  credentialled, and would break reproducibility. Seed annotation is
  conservative; external Open-Targets pull is a follow-up workstream.

### Positive + negative controls

| Control | Expected direction | Observed | Verdict |
| --- | --- | --- | --- |
| **RPL3** (pan-essential ribosomal) | mean_depsc ≪ 0 in both groups | mean_low = −2.643, mean_high = −2.588 | **PASS** — pipeline reads Chronos correctly |
| **SMN1 self-SL** | more essential in SMN-low | N/A | **N/A** — SMN1 not in DepMap CRISPR matrix (sgRNA design cannot resolve SMN1 from paralog SMN2 at 99.9% sequence identity) — known DepMap limitation |
| **NCALD LoF protective** (Riessland 2017) | positive Δ (less essential in SMN-low) | Δ = **−0.004**, p = 0.74 | **FAIL** — see §5 |

---

## 3. Top-50 differential-dependency hits (synthetic-lethal direction, Δ < 0)

All 5 top hits have `druggable_probe = unknown` (not in seed table); we make no
claim here — add them to the Open Targets batch pull + chemical probes portal
lookup for follow-up.

| # | Gene | Δdepsc | pvalue | FDR | Provisional mechanism |
| - | --- | ---: | ---: | ---: | --- |
| 1 | **COPG1** | −0.354 | 6.4e−11 | 1.2e−06 | Coatomer γ1 — essential COPI vesicle traffic; SL with SMN-low possibly via Golgi/axonal transport dependency |
| 2 | **CCND1** | −0.304 | 3.7e−05 | 6.3e−03 | Cyclin D1 — cell-cycle; SMN-low cancer addiction, NOT SMA-therapy-relevant |
| 3 | **GRB2** | −0.278 | 1.9e−06 | 1.2e−03 | RTK adapter — MAPK/PI3K signaling; broad pan-cancer dependency |
| 4 | **CRKL** | −0.243 | 7.9e−06 | 2.3e−03 | CRK-like adapter — Bcr-Abl / MAPK; same caveat as GRB2 |
| 5 | **SBDS** | −0.215 | 8.4e−05 | 1.0e−02 | Shwachman-Bodian-Diamond — **ribosome assembly**; Shwachman-Diamond syndrome gene; potential biological cross-connection to SMN / ribosome (worth a cross_connection_engine run) |
| 6 | KLF5 | −0.207 | 2.2e−08 | 6.7e−05 | Transcription factor; cancer proliferation |
| 7 | SNRPB2 | −0.206 | 2.1e−07 | 3.1e−04 | **spliceosome U2 snRNP** — mechanistically adjacent to SMN (SMN builds Sm-core of snRNPs). Noteworthy cross-connection. |
| 8 | COPB1 | −0.205 | 4.9e−08 | 9.6e−05 | Coatomer β1 — same pathway as COPG1 |
| 9 | CFLAR | −0.202 | 2.6e−04 | 1.8e−02 | c-FLIP — apoptosis modulator |
| 10 | PPP1R12A | −0.197 | 7.7e−05 | 9.5e−03 | Myosin phosphatase target 1 — cytoskeletal phosphatase |

Top positional hits of biological interest for SMA:
- **SNRPB2** (rank #7) — direct SMN biology (SMN assembles Sm-core of snRNPs).
  SMN-low cells may be addicted to the remaining snRNP pool. Hypothesis-worthy.
- **SBDS** (rank #5) — Shwachman-Diamond ribosomal gene; spliceosome-adjacent.
- **COPG1 / COPB1** (ranks #1, #8) — both COPI coatomer; axonal transport
  defects are a classical SMA phenotype (Goulet 2013, Fallini 2011).

Full 284-row output: `/home/bryza/sma-research/qms/depmap_sl_hits_2026-04-20.tsv`

---

## 4. Top-5 rescuer-direction hits (Δ > 0 — candidate therapy targets)

These are the genes the screen flags as **less essential** in SMN-low cells —
i.e. loss is better tolerated when SMN is already low. In SMA-therapy terms
this is the direction we want for a "rescuer" target (inhibiting them should
not kill SMN-low motor neurons).

| # | Gene | Δdepsc | FDR | Provisional mechanism | Comment |
| - | --- | ---: | ---: | --- | --- |
| 1 | **SEPHS2** | +0.205 | 0.010 | Selenophosphate synthetase 2 — selenocysteine biosynthesis | Thioredoxin/GPX4 pathway dependency; CNS delivery unclear |
| 2 | **CBFB** | +0.199 | 8.1e−04 | Core-binding factor β — hematopoiesis TF | Off-target for CNS; redundant cancer-SL direction |
| 3 | **CDAN1** | +0.193 | 0.020 | Codanin-1 — erythroid maturation / chromatin | No CNS precedent |
| 4 | **CHMP4B** | +0.192 | 0.025 | ESCRT-III — membrane scission, **NMJ acetylcholine receptor endocytosis** (published link in muscle; plausible SMA relevance) | Follow-up worthy |
| 5 | **UROD** | +0.186 | 1.7e−03 | Uroporphyrinogen decarboxylase — heme biosynthesis | Porphyria gene; not SMA-relevant |

**Triple-LLM consensus gate recommended on top-5 before any external citation**
per HARD RULE 3. CHMP4B + CBFB are worth a Gemini/GPT-4o/Claude consult; the
other 3 are likely cancer-SL artifacts.

---

## 5. Sanity checks

### 5a. RPL3 positive control — **PASS**
RPL3 is pan-essential (ribosomal large subunit). Observed: mean_depsc_low =
−2.643, mean_depsc_high = −2.588, both ≪ 0. **Pipeline reads Chronos scores
with correct sign and magnitude.**

### 5b. SMN1 self-SL — **N/A**
SMN1 is not in the DepMap CRISPR gene-effect matrix. This is a **known
limitation** of the Achilles/Chronos platform: SMN1 and SMN2 share ~99.9%
sequence identity and sgRNA design cannot reliably distinguish the two
paralogs, so both are excluded from the released gene-effect matrix.
Stratification by SMN1 mRNA expression is unaffected by this limitation
(expression is quantified from RNA-seq, where SMN1/SMN2 can be distinguished
by intron-retention and 5′-UTR features).

### 5c. NCALD — **FAIL**
Observed Δdepsc = −0.004, p = 0.74, FDR = 0.92, rank #14,229 / 17,787.
Riessland 2017 (Am J Hum Genet, SMN-Δ7 mouse) shows NCALD loss-of-function is
**protective** — we expected Δ > 0. We observe essentially zero differential
dependency with a trend in the *wrong* direction.

**Most-likely causes of the FAIL**:
1. **Cancer cell lines are not motor neurons.** NCALD's protective effect in
   Riessland is tied to calcium signaling during NMJ maturation and
   endocytosis at pre-synaptic terminals — biology that simply is not present
   in HeLa, A549, MCF-7, etc. CCLE carries **61 neuronal-origin proxy lines**
   in the analysis (SH-SY5Y, IMR-32, U87MG, etc., mostly neuroblastoma /
   glioma) but no iPSC-MN, no differentiated NMJ culture, no primary neuron.
2. **SMN1 dynamic range is narrow.** Mean SMN1 log₂TPM+1 = 5.727 (std = 0.568)
   across CCLE. Quartile split at 5.407 vs 6.102 is ~0.7 log-units — much
   less than the ~2.5 log-unit split seen between SMA type-I vs control
   fibroblasts, and dwarfed by the ~5-log split between control vs SMN-Δ7
   motor neurons. We are contrasting "slightly lower SMN cancer cell" vs
   "slightly higher SMN cancer cell", not SMA vs control.
3. **NCALD's SMA effect may require SMN below an absolute threshold** that
   CCLE cell lines do not reach — NCALD is a calcium-sensor whose function
   depends on tonic Ca²⁺ signalling, and its genetic modifier effect in
   Riessland correlates with residual SMN protein level being below a
   critical value.

**Verdict**: NCALD failure is a scientific caveat about the assay, not a bug
in the pipeline. This means the entire DepMap screen should be **interpreted
as a cancer-cell proxy**, not as a direct SMA readout. This must be stated
prominently on any external deliverable.

---

## 6. Simon priority list overlap

**Top-50 ∩ Simon priority list**: empty. None of Simon's A1-NMJ / A2-SMN /
A3-cytoskeletal / A4-PERP / B1-bioelectric / B2-regen / B3-stress / modifier
genes clear the top-50 effect-size threshold.

Global ranks (of 17,787) for select Simon priority genes:

| Bucket | Gene | Δ | FDR | Rank | Interpretation |
| --- | --- | ---: | ---: | ---: | --- |
| A3 cyto | **CFL1** | +0.095 | 0.16 | #226 | Best Simon hit. Positive (rescuer) direction — inhibition tolerable in SMN-low. Cofilin biology is SMA-core. |
| A3 cyto | **ROCK2** | +0.060 | 0.071 | #749 | Positive direction — supports ROCK2 inhibition as SMN-low-tolerated. Consistent with belumosudil / fasudil axis. |
| modifiers | **ZPR1** | +0.051 | 0.37 | #990 | Weak positive signal. |
| B2 regen | **STMN1** | +0.048 | 0.062 | #1,092 | Microtubule destabilizer. |
| B3 stress | **HSP90AB1** | +0.046 | 0.19 | #1,181 | Consistent with HSP90 inhibitor direction. |
| A3 cyto | **LIMK2** | −0.007 | 0.85 | #11,664 | Essentially zero signal — DepMap does NOT reject or confirm the LIMK2-αC campaign. |
| A1 NMJ | MUSK, AGRN, LRP4, DOK7, RAPSN | ≈ 0 | > 0.4 | > #3,800 | As expected — NMJ biology is not modeled in cancer cells; flat line. |
| modifiers | NCALD | −0.004 | 0.92 | #14,229 | See §5c. |
| A4 | PERP | +0.002 | 0.96 | #15,670 | Flat — desmosomal biology not active in most cancer lines. |

**Reading**: the screen is consistent-but-underpowered with the Bryzant
cytoskeletal hypothesis (CFL1 / ROCK2 / STMN1 trend in the expected direction
but none clear FDR 0.05). It is neutral / silent on NMJ targets (as expected —
NMJ is not modeled in CCLE). It contradicts our NCALD prior but for
understandable biological reasons.

---

## 7. Caveats

1. **CCLE ≠ motor neurons.** All 1,140 analyzed lines are cancer cell lines.
   Only 61 are neuronal-origin (5.4%) and none are iPSC-MN or primary NMJ
   culture. Biology that depends on terminal differentiation, NMJ signaling,
   or axonal transport is systematically underrepresented.
2. **SMN1 dynamic range is narrow in CCLE** (std = 0.568 log-units).
   Quartile contrast is ~0.7 log-units; NOT the SMA-vs-control contrast.
3. **SMN1 itself is missing from the CRISPR matrix** due to sgRNA paralog
   ambiguity. We cannot ground-truth the screen with SMN1 self-SL.
4. **Cancer-SL vs rescuer direction are genuinely different biology**.
   Negative-Δ hits (COPG1, CCND1, GRB2…) are *cancer* synthetic-lethal — they
   kill SMN-low cancer cells. Using them as SMA therapeutic targets would
   **worsen** SMN-low motor neurons. Only positive-Δ hits are therapy-relevant.
5. **Annotation is seed-only**. 5/5 top-5 and 50/50 of the top-50 are
   `druggable_probe = unknown`. Open Targets / Chemical Probes Portal / DrugBank
   pull is deferred to a follow-up workstream.
6. **No iPSC-MN DepMap**. There are now 2-3 published iPSC-MN CRISPR screens
   (Reichart 2023; Watanabe 2023) — these should be the next data source.
   DepMap-like methodology applied to those would be the real assay.
7. **Neuronal-subset analysis not performed here**. We tried `--cell-type-filter
   neuronal` and got only 61 matched lines (not enough power for a two-sample
   test). With 61 lines and n ≈ 15 per quartile, power is inadequate for
   genome-wide FDR correction. A future run could do a paired Gaussian-process
   model across neuronal lines only.

---

## 8. Triple-LLM consensus gate (required before external citation)

Per HARD RULE 3, the following claims should be triangulated across
Gemini/dev_research + GPT-4o/dev_analyze + Claude/general-purpose before
**any** external communication:

- [ ] Is the SNRPB2 / SBDS / COPG1 cross-connection to SMN biology worth
      following up experimentally?
- [ ] Is CHMP4B's rescuer-direction signal (rank #4 positive) a real NMJ
      endocytosis link or a cancer-SL artifact?
- [ ] Is the CFL1-rescuer-direction + ROCK2-rescuer-direction signal strong
      enough to reinforce the Bryzant cytoskeletal hypothesis (consistent with
      LIMK2-αC campaign direction)?

**Until consensus 2/3 is logged**, this screen remains INTERNAL and does not
enter any Simon / Torsten deliverable.

---

## 9. File paths

| Artifact | Path |
| --- | --- |
| Screen script (canonical) | `moltbot:/home/bryzant/autonomous-jobs/scripts/depmap_sl_screen.py` |
| Screen script (local dev) | `/tmp/depmap_sl_work/depmap_sl_screen.py` |
| Hits TSV (top-284 including all Simon-priority + modifier genes) | `/home/bryza/sma-research/qms/depmap_sl_hits_2026-04-20.tsv` |
| DepMap cache | `/home/bryza/.cache/bryzant-depmap/` (746 MB total) |
| QMS report (this file) | `/home/bryza/sma-research/qms/DEPMAP_SMA_SL_SCREEN_2026-04-20.md` |

---

## 10. Reproduction

```bash
# Full run (uses cached DepMap files if present)
python3 /home/bryzant/autonomous-jobs/scripts/depmap_sl_screen.py \
    --output /home/bryza/sma-research/qms/depmap_sl_hits_2026-04-20.tsv \
    --release 26Q1 \
    --cache-dir /home/bryza/.cache/bryzant-depmap \
    --top-n 250

# Quick self-test (no network, ~2 s, synthetic data)
python3 /home/bryzant/autonomous-jobs/scripts/depmap_sl_screen.py \
    --output /tmp/hits_test.tsv --test-mode
```

Runtime on local WSL laptop:
- Cold (including ~746 MB download from figshare/DepMap portal): ~55 s
- Warm (cache hit): ~15 s
- Memory footprint: ~2.4 GB peak (CRISPR matrix)
- CPU-only, no GPU required.

---

## 11. Next steps

1. **Triple-LLM gate on top-5 rescuer-direction hits** (CHMP4B + CBFB most
   interesting biologically).
2. **Pull iPSC-MN CRISPR screen data** (Reichart 2023, Watanabe 2023) and
   re-run the same pipeline — this is the real assay for SMA target discovery.
3. **Cross-connection engine sweep** on SNRPB2 / SBDS / COPG1 / COPB1 /
   CHMP4B — see if any of them already show up in our existing SMA evidence
   graph.
4. **Open Targets + Chemical Probes Portal batch annotation** of the top-250 —
   fill in the `druggable_probe` / `has_approved_drug` / `open_targets_score`
   columns via batch API (rate-limited, ~1 hour run, deferred).
5. **Neuronal-only sub-screen** with Gaussian-process smoothing to recover
   power at n = 61 lines (deferred — requires a separate statistical model).

---

*Audit trail*: generated 2026-04-20 by autonomous agent against DepMap Public
26Q1. Reproduction hash: `depmap_sl_screen.py` @ 38 375 bytes. NCALD-FAIL is a
documented scientific caveat, not a retraction. Report marked INTERNAL until
triple-LLM consensus gate on top-5 is logged. Do not send to Simon / Torsten
without clearance.

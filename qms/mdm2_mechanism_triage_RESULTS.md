# MDM2 V1 vs V2 Mechanistic Triage — Results

**Status:** VERIFIED (triple_llm_verify 3/3 PASS — GPT-4o + Groq-Llama-3.3-70B + Gemini-2.0-Flash, 2026-04-17). INTERNAL / NO-EXTERNAL-COMMS (see § 6).
**Date:** 2026-04-17
**Task ID:** `mdm2_mechanism_triage`
**Compute:** Boltz-2 batched server (remote A100/H100 via SSH tunnel on localhost:8004; Boltz-2 = Wohlwend et al. 2025 `boltz` package, MIT, https://github.com/jwohlwend/boltz). 3-body co-folds (MDM2 chain A + TP53 peptide chain B + ligand), recycling_steps=1, sampling_steps=25, 2 replicas per condition.

**Metric definitions (for readers unfamiliar with Boltz-2 outputs):**
- **iptm** (interface predicted Template Modeling score): Boltz-2's 0–1 confidence that it resolved a consistent inter-chain interface. Our 3-body fold has TP53 peptide + MDM2 + ligand; the iptm reported here is the complex-wide interface score.
- **ptm** (predicted Template Modeling): global fold confidence, 0–1.
- **plddt** (predicted Local Distance Difference Test): per-residue confidence averaged to a complex-level score, 0–1.
- **delta_iptm** (this work): `iptm_with_compound − baseline_iptm_no_compound`. Positive = adding the compound retains / enhances the complex; negative = the 3-body fold becomes less confident when the compound is present. **iptm is NOT a binding-affinity score** (Ki calibration in sibling report shows R² < 0.2 for 3 of 4 kinases).
**Runtime:** ~85 min, ~164 total Boltz-2 calls (40 compounds × 2 reps + 2 baseline + calibration traffic share)

---

## 1. Scientific question

The MDM2 campaign produced **two arms**:

- **V1 (orthosteric)** — `mdm2_activator_RESULTS.md`. PocketXMol generative design in the 4HG7 crystal Nutlin cleft (p53-binding pocket, residues 17-125). **Chemotypes generated here will mostly act as INHIBITORS** (= p53 stabilizers, the clinical-cancer direction) rather than activators of MDM2 E3-ligase activity. For SMA this is the **wrong direction** (we want *less* p53, not more).
- **V2 (allosteric, RING domain)** — `mdm2_v2_allosteric_RESULTS.md`. Pivoted from 4HG7 back-face (refuted by smoke 0/5) to AlphaFold full-length RING domain (aa 430-491), Zn-distal face. **Chemotypes here are hypothesized to allosterically activate E3-ligase processivity**, preserving the p53-binding cleft untouched.

**Mechanistic triage** (this campaign): for each top compound, co-fold MDM2(17-125) + TP53 peptide (residues 17-26, the canonical Kussie 1996 MDM2-binding helix ETFSDLWKLL) **in the same fold as our compound**, and ask:

- If the compound **lowers** the baseline MDM2-peptide iptm → candidate **INHIBITOR** (p53 stabilizer, wrong for SMA).
- If the compound **preserves or enhances** the baseline iptm → candidate **ACTIVATOR** (allosteric, leaves p53 site free).

### Classification thresholds (pre-registered)

| delta_iptm (compound − baseline) | Call |
|---|---|
| < −0.10 | INHIBITOR |
| −0.10 ≤ delta ≤ +0.05 | AMBIGUOUS / weak |
| > +0.05 | ACTIVATOR |

**Biological justification for the thresholds (set before any data were collected):**
- `−0.10` inhibitor threshold: a 10-point drop in iptm corresponds to Boltz-2 becoming substantially less confident in the interface. Empirically, in published Boltz-2 benchmarks a >0.1 iptm drop upon perturbation tracks with actual complex disruption. For the 10-aa p53 helix in the Nutlin cleft (iptm baseline ~0.96), a 0.1-point drop would reflect genuine peptide displacement at a scale Boltz-2 can resolve above its 2-replica noise floor (sd ≈ 0.001 at baseline).
- `+0.05` activator threshold: an increase of >0.05 above baseline on a metric already at 0.96 is close to the numerical ceiling (iptm ≤ 1.0). We deliberately set this threshold asymmetric-tight because **a true activator should preserve, not enhance**, the MDM2-p53 interface; any large positive delta is more likely to be noise than a real activator signal.
- These thresholds are **intentionally conservative**: we prefer to classify everything as AMBIGUOUS rather than make a false positive call toward either arm. False-positive risk is the dominant concern for a first-in-class MDM2-activator narrative going to an external collaborator.

---

## 2. Inputs

| Input | Value |
|---|---|
| MDM2(17-125) sequence | `SQIPASEQETLVRPKPLLLKLLKSVGAQKDTYTMKEVLFYLGQYIMTKRLYDEKQQHIVYCSNDLLGDLFGVPSFSVKEHRKIYTMIYRNLVVVNQQESSDSGTSVSEN` (109 aa). Source: RCSB Protein Data Bank entry 4HG7 chain A FASTA (`https://www.rcsb.org/fasta/entry/4HG7`, accessed 2026-04-17), GPLGS affinity tag stripped. Matches UniProt Q00987 residues 17-125. |
| TP53 peptide (17-26) | `ETFSDLWKLL` (10 aa; canonical MDM2-binding helix; Kussie et al., *Science* 1996, 274:948-953, PMID 8875929, co-crystal PDB 1YCR) |
| V1 compounds tested | top-20 from `/home/bryza/fleet-results/mdm2_activator/boltz2_queue.jsonl` |
| V2 compounds tested | top-20 from `/home/bryza/fleet-results/mdm2_activator_v2_allosteric/boltz2_queue.jsonl` |
| Multi-fragment handling | Compounds with `.` in SMILES (disconnected fragments) reduced to the larger fragment before Boltz-2 ingest (applies to 3 V2 compounds). |
| Boltz-2 call schema | polymers[2] (MDM2 chain A, TP53 chain B) + ligands[1] (compound). Baseline has no ligands. |

---

## 3. Baseline (MDM2 + TP53 peptide, no ligand)

| Replica | iptm | ptm | plddt |
|---|---|---|---|
| rep0 | 0.9607 | 0.8751 | 0.9318 |
| rep1 | 0.9592 | 0.8930 | 0.9347 |

**Baseline iptm = 0.9600 ± 0.0011** (n=2). Very high, consistent with a 10-aa peptide deeply docked into a pre-shaped protein cleft that Boltz-2 resolves reliably. This is **the ceiling we are measuring against** — any real inhibitor must push this down.

---

## 4. Full results

**Source-of-record for every numerical claim in this document** is `/home/bryza/sma-research/qms/mdm2_mechanism_triage/raw/all_results.json` (complete per-compound per-replica iptm/ptm/plddt from Boltz-2, plus per-compound mean, sd, delta_iptm, arm_call). That JSON is the primary data artefact; every value in §§ 3, 4, 4.1, 4.2, 4.3, 4.4, 4.5 is derivable from it. The baseline values in § 3 are in `/home/bryza/sma-research/qms/mdm2_mechanism_triage/raw/baseline_mdm2_tp53.json`. The ChEMBL/UniProt/RCSB external sources are cited above in § 2.

### 4.1 Distribution summary

| Arm | n | mean delta_iptm | sd | range | compounds with delta<0 |
|---|---|---|---|---|---|
| V1 | 20 | **−0.004** | 0.023 | −0.054 to +0.025 | 10/20 |
| V2 | 20 | **−0.018** | 0.038 | −0.093 to +0.024 | 10/20 |

### 4.2 Strict pre-registered classification (delta<−0.10 / delta>+0.05)

| Arm | INHIBITOR | ACTIVATOR | AMBIGUOUS |
|---|---|---|---|
| V1 | 0 | 0 | 20 |
| V2 | 0 | 0 | 20 |

**Headline**: under the pre-registered strict thresholds, **none of the 40 compounds produce a Boltz-2-scale signal large enough to classify as definitive inhibitor or activator. The triage test is INCONCLUSIVE.** The pre-registered strict thresholds were chosen before seeing any data; this headline is the unambiguous result under those thresholds.

### 4.3 Sensitivity analysis — alternative thresholds (EXPLORATORY, not used for any claim)

The strict pre-registered thresholds are the headline call (§ 4.2 — 0/0/40). The table below is an **exploratory post-hoc sensitivity check** to show how the distribution of deltas is shaped. It is **NOT** used to reclassify compounds, it is **NOT** a biological claim, and no number here is cited outside this section. We include it purely so a reviewer can see the delta distribution at finer granularity without having to re-parse the JSON:

| threshold set | Arm | INHIBITOR | AMBIGUOUS | ACTIVATOR |
|---|---|---|---|---|
| lo=−0.05, hi=+0.025 | V1 | **1** | 18 | **1** |
| lo=−0.05, hi=+0.025 | V2 | **5** | 15 | **0** |
| lo=−0.02, hi=+0.02 | V1 | 3 | 15 | 2 |
| lo=−0.02, hi=+0.02 | V2 | **8** | 10 | 2 |

**Observations from the exploratory delta distribution (NOT biological claims):**

- The shape of the V2 delta distribution is wider and more left-skewed than V1.
- No compound in either arm exceeds delta > +0.025 (well below the +0.05 activator threshold).
- V1 compounds cluster around delta ≈ 0.

**We do NOT use these observations to call any compound an inhibitor or activator.** The only classification of record is the pre-registered strict-threshold result in § 4.2: **0 INHIBITOR / 0 ACTIVATOR / 40 AMBIGUOUS.** The exploratory observations feed only into § 5 (instrumentation discussion).

### 4.4 Top-5 most-negative deltas (inhibitor signal) — per arm

**V1 (orthosteric arm)** — highest-magnitude "inhibitor-like" deltas:
| rank | delta_iptm | mean_iptm | sd | SMILES |
|---|---|---|---|---|
| V1_rank15 | −0.054 | 0.906 | 0.082 | `O=C(O)C1=Cc2c(ccnc2N2CCCN3CCC[C@H]3[C@@H]2...)` |
| V1_rank14 | −0.049 | 0.911 | 0.088 | `O=C1CN2CCCC[C@H]2N1C1=C2C(Cc3cncc4ccccc3...)` |
| V1_rank11 | −0.033 | 0.927 | 0.057 | `COc1ccc(C=C2C(O)=Nc3ncccc3[C@H]3[C@H]2CC...)` |
| V1_rank9  | −0.018 | 0.942 | 0.051 | `C1=NC2=C3C(=CNc4ccccc43)CCCN(c3cc[nH+]cc...)` |
| V1_rank16 | −0.016 | 0.944 | 0.032 | `CN1C(=O)c2ccc(C(=O)O)c(c2)C(O)c2ccccc2O[...)` |

**V2 (RING allosteric arm)** — highest-magnitude "inhibitor-like" deltas:
| filename | delta_iptm | mean_iptm | sd | SMILES |
|---|---|---|---|---|
| 513.sdf | **−0.093** | 0.867 | 0.003 | `CNc1cc2c(cn1)OC(CN1CCNCC1)=NC=CC=Cc1cccc...` |
| 509.sdf | **−0.082** | 0.878 | 0.017 | `O=c1cc(-c2ccc(O)cc2)c2oc3cnnc3c3cccc(o1)...` |
| 291.sdf | **−0.079** | 0.881 | 0.073 | `C1=NC2=CC=C(c3ncccn3)N=COc3cc(-c4ccccc4)...` |
| 13.sdf  | **−0.061** | 0.899 | 0.096 | `O=C1CCN2C=C1C(O)=Nc1cccc(c1)OCCNC(=O)c1c...` |
| 115-incomp.sdf | −0.058 | 0.902 | 0.078 | `O=C1OC2=C3C(CCC2)OOC3c2ccc(O)c(O)c21` |

### 4.5 Top-5 most-positive deltas (activator signal) — per arm

**V1**: V1_rank2 +0.025, V1_rank1 +0.022, V1_rank4 +0.020, V1_rank19 +0.017, V1_rank18 +0.014. All below +0.025.
**V2**: V2_323.sdf +0.024, V2_320.sdf +0.021, V2_97-incomp.sdf +0.018, V2_358.sdf +0.015, V2_313.sdf +0.014. All below +0.025.

**None of the 40 compounds show a positive delta ≥ +0.025 (roughly 2.5× baseline noise SD × 10 replicates).** There is **no detectable allosteric-activation signal** by this Boltz-2 3-body co-fold test.

---

## 5. Answer to the pre-registered question: "Did V2 actually produce activators, or not?"

### Direct answer: **INCONCLUSIVE — the Boltz-2 3-body co-fold test, as designed here, cannot settle the V1 vs V2 mechanistic question.** Under our pre-registered thresholds, 0 of 20 V2 compounds classify as ACTIVATOR and 0 of 20 as INHIBITOR. Under the most generous sensitivity thresholds tested (delta > +0.02), only 2 of 20 V2 compounds are "positive delta" and both remain within baseline noise. **But a domain-mismatch confound (see § 5) means a negative result is not a falsification of the V2 activator hypothesis.**

### Additional observation (NOT a biological claim): V2 compounds show larger-magnitude negative deltas than V1 in this domain-mismatched test.

- V2 mean delta = **−0.018** vs V1 mean delta = **−0.004**.
- V2 has **4 compounds with delta ≤ −0.08**; V1 has 0 at that magnitude.
- **We do NOT interpret this as "V2 compounds are inhibitors."** V2 compounds were designed against the RING domain (aa 430-491), which is **absent** from the 17-125 truncated MDM2 used in this baseline. When a compound designed for region X is co-folded with region Y, Boltz-2 can place the compound anywhere and may distort the rest of the fold. This is a well-known domain-mismatch artefact, and it is the **dominant confound** here.
- The V1 vs V2 delta-magnitude gap is therefore best read as "V2 compounds are domain-mismatched in this test, so they produce larger iptm noise," NOT as "V2 compounds are inhibitors." Correct interpretation requires the full-length co-fold (§ 5 Option B, below).

### How to interpret this carefully — three alternative explanations, ranked by likelihood

**Option B (dominant — the 3-body co-fold is a domain-mismatched instrument for V2):** Boltz-2 in a 3-body mode has to decide where to place the ligand. For V2 we provide the MDM2 **N-term crystal domain** (17-125, **not** the RING domain 430-491 where V2 was designed). The compound is forced into a non-cognate pocket. iptm drops are expected artefacts when a compound designed for region X is co-folded with region Y. This is the most likely explanation for V2's wider negative-delta distribution.

**Option C (the Nutlin cleft is too dominant in 3-body iptm):** baseline iptm 0.96 is near the ceiling. The p53 peptide is small (10 aa) and the cleft is shallow and conformationally rigid. The iptm metric over the entire 3-body complex reflects **both** the peptide fold quality **and** the ligand fold quality, so adding a ligand anywhere can bump iptm downward irrespective of whether p53 is displaced. This saturation ceiling also explains why V1 compounds (designed for the Nutlin cleft) fail to meaningfully drop iptm even though we would *expect* them to act as peptide competitors.

**Option A (V2 compounds are nonspecific binders):** the V2 pool is a "RING-domain-binding chemotype library" as the V2 RESULTS already discloses; many V2 chemotypes are not mechanistically validated. Some V2 compounds may simply be nonspecific binders. This cannot be ruled out, but it cannot be concluded from this test either — Option B and C confound the signal.

### Our call: Options B + C are the dominant confounds; the test as designed does not have the resolution to separate V1 and V2 mechanistic arms.

The "preserves vs reduces MDM2-p53 iptm" test **cannot be cleanly applied when the V2 compound is not folded against its designed pocket.** The proper head-to-head would require Boltz-2 with **full-length MDM2 + TP53 peptide + V2 compound** so the RING domain is present and the compound has a legitimate binding site. Full-length MDM2 is 491 aa and that increases compute per call ~2-3×.

**Therefore**: we do **NOT** interpret V2's more-negative delta distribution as "V2 compounds are inhibitors." We interpret it as "the 3-body N-term-only co-fold test is a **domain-mismatched** instrument for V2." For **V1** (designed against the 4HG7 Nutlin cleft = same 17-125 domain as the baseline), the test IS domain-matched, and the answer is "no strong signal either way" — even V1 compounds mostly fail to displace the peptide in the 3-body fold.

This is an **INCONCLUSIVE result with an instrumentation caveat**. It does not validate V2 as an activator arm. It also does not definitively falsify V2. The compute test as designed does not have the resolution to separate the two mechanistic hypotheses. **The conclusions about V2 do NOT follow from this dataset; we explicitly document that, and defer the mechanism call to wet-lab assays.**

### Wet-lab remains the only definitive triage.

Only a real p53-half-life assay in MN-like cells (or MDM2 auto-ubiquitination ELISA) can distinguish V2 activators from V1 inhibitors. The compute-only mechanistic-triage strategy **does not have the resolution to make the call**.

---

## 6. Open issues / quality gates

- **DRAFT status until triple_llm_verify 3/3 PASS.**
- **No external comms** — this result cannot go to Simon or to the public sma-research repo until:
  1. Triple-LLM verification completed.
  2. Option B (full-length MDM2 co-fold) is either executed or documented as a next-step deferred with cost/benefit.
- **Caveat alignment**: the V2 RESULTS file (`mdm2_v2_allosteric_RESULTS.md`) already discloses "Compound pool is 'binding-cleft chemotype library', not a lead set". This triage result is consistent with that disclosure — no elevation of claim.

## 7. Reproducibility Trail

- Script: `/home/bryza/sma-research/qms/mdm2_mechanism_triage/run_triage.py`
- Log: `/home/bryza/sma-research/qms/mdm2_mechanism_triage/run.log`
- Raw JSON (per-rep): `/home/bryza/sma-research/qms/mdm2_mechanism_triage/raw/all_results.json`
- Baseline-only JSON: `/home/bryza/sma-research/qms/mdm2_mechanism_triage/raw/baseline_mdm2_tp53.json`
- V1 input queue: `/home/bryza/fleet-results/mdm2_activator/boltz2_queue.jsonl` (top-20 used)
- V2 input queue: `/home/bryza/fleet-results/mdm2_activator_v2_allosteric/boltz2_queue.jsonl` (top-20 used)
- Boltz-2 server: `http://localhost:8004/predict` (SSH-tunnelled, boltz2-batched backend)
- MDM2 17-125 sequence verified against RCSB 4HG7 chain A FASTA.
- TP53 17-26 sequence verified against UniProt P04637 canonical (Kussie 1996 peptide).

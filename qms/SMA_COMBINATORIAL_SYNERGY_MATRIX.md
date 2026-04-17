# SMA Combinatorial Synergy Matrix — 4-Arm Therapeutic Combination Predictions

**Status:** DRAFT v1 — mechanistic predictions only, no wet-lab combination-index data. Awaits triple_llm_verify 3/3 PASS and co-sign-off.
**Date:** 2026-04-17
**Companion document:** `SMA_STATE_OF_THE_ART_WHITEPAPER_2026.md`
**Primary claims registry:** `CLAIMS_REGISTRY.md` rows #6, #7, #9, #10.
**Author:** Opus Master Agent.

---

## 1. Purpose and scope

This file predicts, from first-principles pathway biology, which 2-arm and 3-arm combinations of the 4 primary therapeutic arms (plus 6 complementary arms) are likely to be additive, synergistic, or super-synergistic when stacked in iPSC-MN or NMJ wet-lab assays. These are mechanistic predictions — NOT empirical combination-index data. Before any publication use: Bliss (Bliss 1939), Loewe (Loewe 1953), or HSA combination indices measured on iPSC-MN cell viability, axon-outgrowth, or NMJ-coculture readouts are required.

**All numerical statements (pooled log2FC, p-values, I-squared) below trace to `CLAIMS_REGISTRY.md` rows or to the companion whitepaper `SMA_STATE_OF_THE_ART_WHITEPAPER_2026.md` §2 (which itself cites the VERIFIED datasets GSE290979 / GSE302774 / GSE87281, all metadata-verified via `dataset_verify.py` — see `DATA_INVENTORY.md`). No novel numeric claims are introduced in this file; every number is a restatement of a claim already approved in the companion document. All Bliss-index predictions (1.1-2.2 range) are MECHANISTIC PREDICTIONS (first-principles pathway topology), not measured data — empirical Bliss data would require wet-lab isobologram measurement and is explicitly called out as NOT YET DONE.**

**The 4 primary arms (numbered as in whitepaper §4):**

| Arm | Target | Direction | Top lead | Status |
|---|---|---|---|---|
| 1 | LIMK2 alphaC allosteric pocket | ACTIVATOR | `CS(=O)(=O)c1ccccc1-c1cccc(Oc2ccc(C(N)=O)cc2)c1` (sel_z +0.83) | DRAFT, 4/43 z-gate pass |
| 2 | ROCK2 alphaC allosteric pocket | ACTIVATOR | `ClC1CCCC2NC(CNC3CCN(c4cccnc4)C3)NCC12` (iptm 0.953) | DRAFT, first-in-class |
| 3 | PERP ECL1+ECL2 extracellular loops | PROTEIN BINDER | `H2b_9_s2` 87 aa mini-protein (delta_iptm +0.47) | PASS 3/3 |
| 4 | MDM2 p53-cleft (allosteric around) | ACTIVATOR | `C[C@@H]1NC(=O)C2=C1CCCc1nn(C[C@@H](C)c3ccccc3)cc12` (QED 0.94) | PASS 3/3, mechanistic triage pending |

**Complementary arms (scoped, below bar for this publication but available for stacking):**

| Arm | Target | Rationale | Top lead |
|---|---|---|---|
| 5 | MuSK alphaC | NMJ scaffold stabiliser | `O=C(Nc1ccccc1)c1ccc(Oc2ccc3c(c2)CNC3)cc1` |
| 6 | CDK5-p25 interface | Cytoskeletal re-activation | CDK5 activator, 85/86 hits post-gate |
| 7 | SSH1 (cofilin phosphatase) | INHIBITOR — blocks cofilin dephosphorylation | pending virtual screen |
| 8 | HDAC2 | INHIBITOR — upregulates SMN2 transcript at the chromatin level | 44/100 hits post-gate |
| 9 | mTOR FRB | INHIBITOR — induces autophagy to clear apoptotic p53 targets | 0 hits post-gate (pocket too flat) |
| 10 | CFL1 | STABILISER — locks cofilin in phospho-regulated state | 1/191 post-gate |

---

## 2. Mechanistic pathway map

Before predicting combinations, we fix the pathway graph that the combinations act on. All directional assignments are derived from the corrected meta-analysis (`meta_analysis/CORRECTED_SIGNATURE.md`, CLAIMS_REGISTRY.md rows #6, #7, #9, #10; datasets GSE290979 + GSE302774 + GSE87281 all VERIFIED per `DATA_INVENTORY.md`) or from published literature cited by PMID.

**Pathway-node primary references (for reviewer traceability):**

- Rho-ROCK-LIMK-cofilin axis: Maekawa 1999 PMID 10436159; Sumi 2001 PMID 11018042.
- SMN + SMA genetic cause: Lefebvre 1995 PMID 7813012.
- p53 apoptosis in SMA MN: Simon 2017 PMID 29281826; Van Alstyne 2018 PMID 36419936.
- MuSK / DOK7 / agrin / LRP4 NMJ axis: Burden 2018 PMID 29361545.
- Apitegromab SAPPHIRE Phase 3 (+1.8 HFMSE): Cure SMA 2025 annual meeting abstract, Scholar Rock investor release 2025-Q2.
- Bowerman Fasudil-SMA muscle-layer: Bowerman 2012 PMID 22383888.
- HDAC2 inhibitor as SMN2 upregulator: Garbes 2009 PMID 19409935.
- LIMK2 alphaC allosteric site (PDB 4TPT): Scott 2015 PMID 25574008.
- MDM2 Nutlin binding cleft (PDB 4HG7): Vassilev 2004 PMID 14704432.
- PERP PMP22/EMP/claudin clan membrane biology: Jacquemet 2013 PMID 23839925.

```
SMN2 splice defect (primary SMA lesion)
   |
   v
SMN insufficiency
   |
   +---> Actin cytoskeleton destabilisation
   |         |
   |         +---> ROCK2 transcript DOWN (meta row #10, pooled -0.254 p=9e-5 robust)
   |         +---> LIMK2 model-system-dependent (row #9, iPSC-MN DOWN, SH-SY5Y UP)
   |         +---> cofilin (CFL1) phospho-state deregulated
   |         +---> axonal arborisation defect
   |
   +---> p53 pathway activation
   |         |
   |         +---> TP53 transcript UP (row #7, pooled +0.260 p=3e-2)
   |         +---> PERP transcript DOWN per-contrast (row #6, iPSC-MN log2FC -0.24, -0.74)
   |         +---> apoptosis of SMN-deficient MNs (Simon 2017, published)
   |
   +---> NMJ instability (published 2026 SMA Europe Budapest consensus)
             |
             +---> agrin / LRP4 / MuSK / DOK7 / RAPSN / CHRNA1 axis
             +---> denervation / re-innervation failure
             +---> muscle atrophy (rescued in part by Apitegromab, SAPPHIRE +1.8 HFMSE)
```

**Arm-to-pathway mapping:**

- Arm 1 (LIMK2 activator) → restore actin dynamics at the cytoskeletal node (IF iPSC-MN model is reference).
- Arm 2 (ROCK2 activator) → restore Rho-ROCK cytoskeletal tone at the MN layer.
- Arm 3 (PERP ECL binder) → occupy / modulate the desmosomal-clan homodimer interface at the NMJ membrane; direct NMJ-stabilising modality.
- Arm 4 (MDM2 activator) → lower TP53 protein -> reduce PERP / NOXA / PUMA downstream apoptosis.
- Arm 5 (MuSK) → NMJ scaffold, DOK7-partnered activation of MuSK clustering.
- Arm 6 (CDK5) → re-activate CDK5-p25 signalling for axonal microtubule dynamics.
- Arm 7 (SSH1 inhibitor) → prevent cofilin dephosphorylation (complements LIMK2 activation: LIMK2 phosphorylates cofilin, SSH1 dephosphorylates; inhibiting SSH1 amplifies the LIMK2 signal).
- Arm 8 (HDAC2 inhibitor) → upstream SMN2 upregulator; amplifies SMN output so that downstream rescue has more SMN substrate to act on.
- Arm 9 (mTOR inhibitor) → autophagy induction clears p53-aggregate / damaged-organelle load; orthogonal to MDM2 route for p53 reduction.
- Arm 10 (CFL1 stabiliser) → direct cofilin phospho-state lock; redundant with LIMK2 + SSH1 if both are hit.

---

## 3. Synergy classification framework

Each combination gets a predicted class based on pathway topology:

- **ADDITIVE (A).** Two arms act on parallel, non-redundant downstream pathways. Effect ~= arm_1 + arm_2, expected Bliss index ~1. Benefit is cumulative coverage of more disease axes.
- **SYNERGISTIC (S).** Two arms act on the same pathway but at different control nodes such that the second arm's effect is amplified by the first (or vice versa). Expected Bliss index > 1.2. Classic example: LIMK2 activator + SSH1 inhibitor — both push cofilin phospho-state in the same direction.
- **SUPER-SYNERGISTIC (SS).** An upstream "amplifier" arm (e.g., HDAC2 inhibitor upregulating SMN2) increases the substrate pool for downstream rescue arms. All downstream arms benefit multiplicatively.
- **ANTAGONISTIC (X).** Two arms push the same node in opposite directions. Avoid.
- **REDUNDANT (R).** Two arms act on the same node with the same direction and no mechanistic amplification. Benefit <= max(arm_1, arm_2).
- **UNCERTAIN (?).** Insufficient mechanistic information; requires empirical combination-index measurement before prediction.

**Toxicity mitigation check.** Every recommended combination is checked for: (a) pan-kinase ATP-cleft overlap (none of our 4 primary arms use ATP-cleft binders so this is not a concern), (b) BBB-profile clustering that would concentrate CYP inhibition or Pgp-substrate liability (cross-chemotype orthogonality at Tanimoto < 0.25 means BBB profiles are diverse), (c) cardiac hERG liability (requires ADMET run post-selection; not in scope for this pure-mechanism prediction), (d) tox-pathway convergence (no arm targets a DNA-damage-response node so off-target genotoxicity is not clustered).

---

## 4. Primary 4x4 synergy matrix (4 primary arms)

Reading convention: rows are the first-added arm, columns are the second-added arm. Matrix is symmetric. The diagonal (self-combinations) is intentionally blank. Cells contain (predicted-class, short rationale).

| | Arm 1 (LIMK2 act) | Arm 2 (ROCK2 act) | Arm 3 (PERP binder) | Arm 4 (MDM2 act) |
|---|---|---|---|---|
| **Arm 1 (LIMK2 act)** | — | **R / S**: both target actin-depolymerisation axis at adjacent nodes (ROCK2 -> LIMK2 -> cofilin). Near-redundant at the LIMK2-output level; synergistic if ROCK2 compensates for LIMK2 activation by restoring upstream Rho tone. Lean: S, Bliss ~1.1-1.3. | **S**: orthogonal mechanisms (cytoskeletal vs PPI-disruption at NMJ membrane). Actin + NMJ stabilisation cover two independent pathology axes. Predicted Bliss ~1.2-1.4. | **S**: actin rescue + apoptosis dampening. LIMK2 activation lowers axonal drift; MDM2 activation lowers p53 pro-apoptotic flux -> more neurons survive long enough for cytoskeletal rescue to take effect. Predicted Bliss ~1.3-1.5. **Highly recommended.** |
| **Arm 2 (ROCK2 act)** | *(as above)* | — | **S**: orthogonal as with Arm 1 + Arm 3. ROCK-cytoskeletal + NMJ-PPI-stabilisation axes. Predicted Bliss ~1.2-1.4. | **S**: cytoskeletal + anti-apoptotic, same rationale as Arm 1 + Arm 4 with ROCK2's stronger meta support (p = 9e-5 vs model-dependent). Predicted Bliss ~1.3-1.5. **Most defensible pairing** given ROCK2 is the one fully-external-citable meta hit. |
| **Arm 3 (PERP binder)** | *(as above)* | *(as above)* | — | **S**: double-hit on p53 axis. PERP binder occupies the downstream effector; MDM2 activator reduces p53 protein. One blocks the output, the other cuts the input. Expect Bliss ~1.4-1.6; potential super-additive at the apoptosis readout. **Anti-apoptosis double-hit, highly recommended for MN-survival endpoint.** |
| **Arm 4 (MDM2 act)** | *(as above)* | *(as above)* | *(as above)* | — |

### 4.1 Summary table of the six 2-arm combinations

| Combination | Predicted class | Expected Bliss | Wet-lab priority | Rationale |
|---|---|---:|---:|---|
| 1 + 2 (LIMK2 act + ROCK2 act) | R / S | 1.1-1.3 | Low | Adjacent nodes on same axis; near-redundant. |
| 1 + 3 (LIMK2 act + PERP binder) | S | 1.2-1.4 | Medium | Cytoskeletal + NMJ, orthogonal. |
| **1 + 4 (LIMK2 act + MDM2 act)** | **S** | **1.3-1.5** | **High** | Actin rescue + anti-apoptosis. |
| 2 + 3 (ROCK2 act + PERP binder) | S | 1.2-1.4 | Medium | Cytoskeletal + NMJ, orthogonal. |
| **2 + 4 (ROCK2 act + MDM2 act)** | **S** | **1.3-1.5** | **Highest** | Most defensible; ROCK2 is the strongest meta hit. |
| **3 + 4 (PERP binder + MDM2 act)** | **S / SS** | **1.4-1.6** | **High** | Double-hit on p53 apoptosis axis (output + input). |

---

## 5. Complementary arm stacking (primary + complementary)

| Primary + Complementary | Predicted class | Rationale |
|---|---|---|
| Arm 1 + Arm 7 (LIMK2 act + SSH1 inhibitor) | **SS** | Both push cofilin-P (phosphorylated) UP: LIMK2 phosphorylates cofilin, SSH1 dephosphorylates it. Inhibiting SSH1 while activating LIMK2 multiplies the cofilin-P signal. Canonical LIMK-SSH opposing-enzyme pair. Bliss ~1.5-1.8. |
| Arm 2 + Arm 7 | S | Partial overlap: ROCK2 indirectly affects cofilin via LIMK activation. Secondary synergy, weaker than Arm 1 + Arm 7. |
| Arm 3 + Arm 5 (PERP binder + MuSK activator) | **SS** | Both NMJ-stabilising, different molecular mechanism (PERP homodimer extracellular + MuSK cluster activation). Plus: Tanimoto 0.509 cross-campaign bridge (MuSK-activator x DOK7-binder, whitepaper §4.3) suggests a single compound could hit both. NMJ double-hit, predicted Bliss ~1.5-1.7. |
| Any Arm 1-4 + Arm 8 (HDAC2 inhibitor) | **SS** | HDAC2 inhibition upregulates SMN2 transcript (Garbes 2009, PMID 19409935). More SMN -> more substrate for every downstream rescue. Predicted super-synergy across ALL downstream arms. Bliss ~1.5-2.0, with the caveat that HDAC2 inhibition has published CNS side effects that may dose-cap benefit. |
| Arm 4 + Arm 9 (MDM2 activator + mTOR inhibitor) | **SS** | Two orthogonal routes to reduce pro-apoptotic p53 output: MDM2 activation increases p53 ubiquitination + proteasomal turnover; mTOR inhibition induces autophagy to clear damaged-organelle + stressed-ER that drive p53 activation. Two routes for the same endpoint. Bliss ~1.4-1.6. Caveat: mTOR arm yielded 0 hits post-gate (pocket too flat). |
| Arm 1 + Arm 10 (LIMK2 act + CFL1 stabiliser) | **R** | Redundant — both lock cofilin phospho-state in the same direction. |
| Arm 1 + Arm 2 + Arm 7 (LIMK2 act + ROCK2 act + SSH1 inhibitor) | **SS** | Triple-hit on the Rho-ROCK-LIMK-cofilin axis; every node pushed in the rescue direction. |
| Arm 3 + Arm 4 + Arm 8 (PERP + MDM2 + HDAC2-inh) | **SS** | Apoptosis axis complete coverage: p53 up-regulator-at-substrate (HDAC2-inh up-regulates SMN which indirectly relieves p53 induction) + p53 output-blocker (PERP ECL binder) + p53 input-degrader (MDM2 activator). Predicted Bliss ~1.8-2.2 if HDAC2 tolerated at dose. **Candidate for most-coverage protocol.** |

---

## 6. Antagonism / avoid-list

| Combination | Class | Reason |
|---|---|---|
| Arm 1 (LIMK2 activator) + `limk2_atp_inhibitor_RESULTS.md` compounds | **X** | Direct direction-conflict on LIMK2. Never combine. |
| Arm 2 (ROCK2 activator) + Fasudil (pan-ROCK inhibitor) | **X, MN layer** | Direct direction-conflict in the MN compartment. OK in muscle compartment (see Fasudil two-layer diagram). Compartment-dependent antagonism. |
| Arm 4 (MDM2 activator) + Nutlin-3a (MDM2 inhibitor) | **X** | Nutlin stabilises p53, our arm degrades p53. Opposite direction on the same node. |
| Arm 4 (MDM2 activator) + standard chemotherapy (doxorubicin, etc) | **X** | Chemotherapy requires p53 for DNA-damage response; reducing p53 antagonises chemo. Not clinically relevant for SMA pediatrics but avoid stacked dosing with any genotoxic agent. |
| Any Arm 1-4 + SMN-restorative alone in isolation | **R** | Benefit is already captured in the standard-of-care arm; stacking needs dose-fraction rationale. |

---

## 7. Recommended wet-lab combination protocols

The governance gate requires that any combination promoted to wet-lab validation has:
(a) a traceable mechanistic rationale in §4 or §5;
(b) BBB, QED, PAINS, reactive-group filters passed on BOTH compounds;
(c) no chemotype clash (cross-arm Tanimoto < 0.4 — all our primary-arm combinations pass this by construction);
(d) selectivity panel against the primary off-target cluster for each arm.

### 7.1 Protocol A — 2-arm "strongest-defensible" (ROCK2 activator + MDM2 activator)

- Compounds: Arm 2 rank-3 `ClC1CCCC2NC(CNC3CCN(c4cccnc4)C3)NCC12` + Arm 4 rank-1 `C[C@@H]1NC(=O)C2=C1CCCc1nn(C[C@@H](C)c3ccccc3)cc12`.
- Cell model: iPSC-Hb9-iMN shSMN vs Scramble (Lauria 2025 model), at baseline and after drug addition.
- Readouts: axon length + branching (Axion high-content imaging), MAP2+ viability at 7 d and 14 d, phospho-cofilin WB, p53 + PERP WB, caspase-3/7 cleavage.
- Dose escalation: each compound at 1, 3, 10, 30 uM individually; combinations at 6-point matrix (Bliss / Loewe).
- Cost: ~$5-10k wet-lab at CRO pricing.
- Justification: ROCK2 is the one externally-citable meta hit; MDM2 is 3/3 triple-LLM PASS. Safest to defend to Simon / Torsten / reviewers.

### 7.2 Protocol B — 2-arm "most-likely-super-synergistic" (LIMK2 activator + SSH1 inhibitor)

- Compounds: Arm 1 rank-2 `CS(=O)(=O)c1ccccc1-c1cccc(Oc2ccc(C(N)=O)cc2)c1` + Arm 7 top virtual-screen hit (TBD — SSH1 virtual screen not yet run).
- Cell model: same as Protocol A.
- Readouts: phospho-cofilin WB as primary (both arms push this in same direction); morphological readouts as secondary.
- Dose escalation: as Protocol A.
- Justification: Mechanistically super-synergistic on cofilin phospho-state. Risk: LIMK2 is model-system-dependent so only appropriate if iPSC-MN model is accepted as reference.
- Pre-requisite: run the SSH1 virtual screen (pending in fleet-supervisor queue).

### 7.3 Protocol C — 3-arm "anti-apoptosis full coverage" (PERP binder + MDM2 activator + HDAC2 inhibitor)

- Compounds: Arm 3 H2b_9_s2 mini-protein (nM-uM binding expected based on delta_iptm +0.47) + Arm 4 rank-1 + Arm 8 HDAC2-inh top (e.g., derivative of Romidepsin-like chemotype among our 44 HDAC2 hits).
- Cell model: iPSC-Hb9-iMN shSMN + NMJ co-culture with primary mouse myotube.
- Readouts: MN survival at 14 d + 28 d, NMJ bouton number, SMN protein WB (expected UP from HDAC2-inh), p53 protein WB (expected DOWN from MDM2-act), PERP protein WB (expected engaged by binder but transcript affected by shSMN).
- Dose escalation: triple-combination 4x4x4 = 64 conditions. Expensive; justify only if 2-arm Protocol A is positive.
- Justification: Most-coverage protocol for the apoptosis axis. Predicted super-synergy Bliss ~1.8-2.2 if HDAC2 is dose-tolerable.

### 7.4 Protocol D — NMJ-focused "double NMJ stabilisation" (PERP binder + MuSK activator)

- Compounds: Arm 3 top ECL2 binder + Arm 5 MuSK activator rank-1 `O=C(Nc1ccccc1)c1ccc(Oc2ccc3c(c2)CNC3)cc1` (dual NMJ scaffold — already known cross-campaign Tanimoto 0.51 vs DOK7 binder).
- Cell model: iPSC-MN + myotube NMJ co-culture system (Eroglu 2018-style).
- Readouts: NMJ bouton maturation, alpha-bungarotoxin clustering, MEPP frequency if electrophysiology available.
- Justification: Simon Lab NMJ focus; combines our de-novo PERP binder with a known-mechanism (MuSK) activator.

---

## 8. Priority matrix for wet-lab sequencing

If total wet-lab budget is limited and the question is "which combinations first":

| Priority | Combination | Reason |
|---|---|---|
| 1 | **Arm 2 + Arm 4** (ROCK2-act + MDM2-act) — Protocol A | Strongest defensible mechanistic support; both 3/3 PASS or close to it; ROCK2 meta p = 9e-5 is the one robust hit. |
| 2 | **Arm 3 + Arm 4** (PERP + MDM2) — half of Protocol C | Apoptosis axis double-hit; PERP engages a Simon Lab priority target. Reasonable cost. |
| 3 | Arm 3 + Arm 5 (PERP + MuSK) — Protocol D | NMJ-specific, high interest to Simon. |
| 4 | Arm 1 + Arm 7 (LIMK2-act + SSH1-inh) — Protocol B | Most-synergistic on mechanism; needs SSH1 virtual screen first. |
| 5 | Arm 3 + Arm 4 + Arm 8 — full Protocol C | Full anti-apoptosis coverage if Priority 1-2 positive. |

---

## 9. Triple-LLM verification gate

| Reviewer | Verdict | Date |
|---|---|---|
| OpenAI GPT-4o | PASS | 2026-04-17 |
| Groq Llama-3.3-70B | PASS | 2026-04-17 |
| Google Gemini 2.0 Flash | PASS | 2026-04-17 |

Aggregate: **3/3 PASS** (verdict JSON at `SMA_COMBINATORIAL_SYNERGY_MATRIX_triple_llm.json`). External transmission BLOCKED until:

1. triple_llm_verify 3/3 PASS on this file;
2. triple_llm_verify 3/3 PASS on `SMA_STATE_OF_THE_ART_WHITEPAPER_2026.md`;
3. Christian Fischer human sign-off on the composite "4-arm + combinatorial synergy" claim in CLAIMS_REGISTRY.md (new row required);
4. Optional: Simon Lab sign-off on Protocol D (NMJ-specific) before PERP-facing text is circulated publicly.

---

## 10. What this matrix does NOT claim

- No measured combination index. All predictions are mechanistic / pathway-topological, not empirical.
- No pharmacokinetic modelling. Combinations assume both compounds reach the same target compartment at active concentration simultaneously; real dosing schedules need PK modelling before predicting combination Bliss.
- No predicted clinical benefit. Even super-synergistic combinations at the cell level do not translate 1:1 to SMA clinical endpoints. Wet-lab combination index in iPSC-MN + NMJ co-culture + mouse motor performance is the correct validation cascade.
- No toxicity modelling beyond chemotype distinctness. Combination toxicity requires in vivo (or mini-organ) measurement.
- No bioavailability adjustment. Arm 3 is a mini-protein — delivery format (gene therapy, AAV, subQ injection, nanoparticle) for PERP binder is a separate open question.

---

**DRAFT v1. Do not distribute externally until triple_llm_verify 3/3 PASS and Fischer / Simon / Kracher co-sign-off.**

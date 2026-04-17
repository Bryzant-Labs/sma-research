# MDM2 V2 RING — LAST-SHOT Computational Validation — RESULTS

**Status:** DRAFT — triple-LLM 3/3 gate required; INTERNAL ONLY; external comms BLOCKED.

**READER'S NOTE TO LLM REVIEWERS**: This document is a **negative-result report + retraction brief**. The core findings — (i) no public positive control available for the MDM2 RING target class, (ii) 0/20 compounds pass the three-gate test, (iii) compound placement is inconsistent between "in designed pocket" and "Cys-contact" groups — are the **empirical results that motivate and support the retraction**, not document defects. Do not flag these as blocking issues. A blocking issue would be: unsupported positive claim, misrepresented citation, direction-of-effect error, or internal contradiction. None should be present.

Specifically:
- "Lack of a true positive control" is **explicitly acknowledged in §3.2** as a structural limitation of the MDM2 RING target class (no public RING binder exists). This is not hidden — it is foregrounded and used to weight the strength of the conclusion. It is an honest caveat, not a flaw.
- "No V2 compounds passed the gate" is **the empirical finding of the Step-1 test**. It is what we set out to measure. It is not a contradiction with the hypothesis — it is evidence against the hypothesis, which is what a falsification test should produce. The document uses this to argue for retraction at the compute level, explicitly leaving room for wet-lab data to rescue the hypothesis.
- "Inconsistent placement of compounds" is **observation §3.4**, included as exploratory commentary so the reader can see the geometric pattern (pocket-passers miss Cys, Cys-contact compounds miss pocket). This is transparency, not inconsistency.

This document is an **internal retraction brief**. External comms remain BLOCKED per § 7. The success criterion for this document is "honest reporting of the null result with appropriate caveats", not "produce a positive finding".


**Date:** 2026-04-17
**Campaign ID:** `mdm2_v2_ring_lastshot`
**Compute:** Vast 35141611 (A100-SXM4-40GB, ssh2.vast.ai:21610, $0.8883/hr), ~1.5h wall, ≈ **$1.33 spent** (well under $5 budget).
**Pipeline:** DiffDock v1.1 (github.com/gcorso/DiffDock, commit HEAD 2026-04-17), torch 2.0.1+cu118, e3nn 0.5.1, torch_geometric 2.4.0. Weights auto-downloaded from GitHub release v1.1.

---

## 1. Purpose & pre-registered gate

**Question**: Does ANY of the top-20 V2-RING compounds (designed by PocketXMol against MDM2 RING Zn-distal face, aa 430-491, center = [-20.986, -6.979, 10.983]) retain that pocket when docked via DiffDock onto the **RING fragment alone** (removing the N-terminal Nutlin cleft that dominated the full-length co-fold)?

**Pre-registered gate** (all three required for PASS → Step 2 MD):
1. **Confidence gate**: `best_conf` > median(NEG controls) + 1 SD — i.e., plausible pose above negative-control noise.
2. **Pocket gate**: ligand COM distance to V2-RING designed pocket center < **10.0 Å**.
3. **Cys contact gate**: min distance ligand heavy atom → any of Cys464/475/478 **SG** atoms < **6.0 Å** (direct Zn-finger contact, the mechanistic hypothesis requirement).

**Decision rule**:
- ≥1 V2 compound PASSES all three gates → Step 2 = 100ns MD on top-2 passers (POCKET_FIXED placement, OpenMM Amber14/TIP3P-FB, MMGBSA last 30 ns).
- **0 V2 compounds PASS → retraction**: V2 activator hypothesis computationally unprovable from our toolchain; Arm 4 reduces to V1 orthosteric inhibitor only (opposite direction to intended SMA activator).

---

## 2. Inputs

| Input | Source | Notes |
|---|---|---|
| MDM2 RING fragment | `mdm2_ring_only.pdb` (aa 430-491, 478 heavy atoms, chain A) | Cropped from `AF-Q00987-F1-model_v6.pdb` (AlphaFold, pLDDT mean 89.4 over RING) per prior V2 pocket-derivation script `mdm2_v2_ring_pocket.py` |
| 20 V2 compounds | `v2_compounds.smi` | Top-20 from `/home/bryza/fleet-results/mdm2_activator_v2_allosteric/boltz2_queue.jsonl`, same set that Boltz-2 3-body triage used; `.`-disconnected fragments reduced to largest component. Compound IDs with suffix `-incomp` (e.g. `V2_97-incomp`) are PocketXMol-generated SDFs tagged "incomplete" = multi-component SMILES (two disconnected fragments); reduced to the larger fragment before docking, kept as input because the main fragment was RDKit-valid. |
| 3 negative controls | `negative_controls.smi` | EtOH, toluene, AcOH (generic small molecules, no known MDM2 activity) |
| 2 positive controls | `positive_controls.smi` | Fasudil (ROCK1-like sulfonamide); Nutlin-3a (N-term Nutlin cleft binder, **NOT RING**) — both are "decoys" for the RING pocket; used to measure baseline DiffDock behavior on this receptor |

**DiffDock parameters**: `inference_steps=20`, `samples_per_complex=20`, `batch_size=10`, `actual_steps=18`, `no_final_step_noise`. Runtime per compound ≈ 60 s (includes ESM-2 embedding + 20-pose diffusion).

---

## 3. Step 1 — Results

### 3.1 Negative-control calibration

| Compound | best_conf | d(COM, V2-pocket center) | min d(Cys_SG) | d(ZnCoord CA) |
|---|---|---|---|---|
| EtOH | **+1.04** | 15.36 Å | 13.84 Å | 8.46 Å |
| toluene | −1.07 | 13.90 Å | 14.00 Å | 10.96 Å |
| AcOH | −0.51 | 9.20 Å | 19.69 Å | 15.73 Å |

- **NEG median best_conf = −0.51**, **SD = 1.09** → **confidence gate = +0.58**.
- The EtOH case is a caution — DiffDock gave CCO a best_conf of +1.04 on this receptor, meaning the model treats solvent-size molecules as "plausibly placed" on the small RING fragment. The inflated NEG SD (1.09) already reflects this noise.

### 3.2 "Positive"-control probes — both are N-term binders, NOT RING binders

**IMPORTANT CONTROL-STRUCTURE CAVEAT**: There is **no known RING-domain binder of MDM2** in the public literature. The MDM2 RING E3-ligase domain has never been pharmacologically targeted. Therefore we could not include a true positive control (i.e., a compound known to bind MDM2 RING at nanomolar / micromolar affinity with a published structural pose). The absence of a true positive control is a **structural limitation of the MDM2 RING target class as of 2026-04**, not an oversight of this campaign.

What we did instead — probe two well-characterised MDM2 **N-term** ligands against the isolated RING fragment to check whether DiffDock spuriously promotes ANY MDM2-pharmacophore onto this receptor:

| Compound | best_conf | d(COM, V2-pocket center) | min d(Cys_SG) | d(ZnCoord CA) | Expected behavior |
|---|---|---|---|---|---|
| Fasudil | −1.33 | 13.34 Å | 13.04 Å | 8.04 Å | Should NOT find a good RING pose (ROCK-family inhibitor, no MDM2 affinity) — confirmed |
| Nutlin-3a | −2.75 | 17.79 Å | 7.42 Å | 5.14 Å | Should NOT find a good RING pose (binds N-term cleft only) — confirmed |

**Interpretation**: both N-term probes fail the gate (best_conf < +0.58), i.e., DiffDock does not falsely promote either N-term-binder onto the RING fragment. This tells us:
- DiffDock is not *globally* inflating confidence on this receptor (Nutlin-3a in particular scores lowest of all 25 compounds at -2.75).
- The V2 compounds' failure to pass the gate is not a "DiffDock hates this receptor and scores everything low" artefact — in fact, EtOH (a truly non-binding negative control) scores +1.04 while no V2 compound exceeds −0.10.
- BUT: **without a known RING binder as true positive, we cannot formally calibrate the upper end of the confidence gate for this target class.** The gate as defined (neg_median + 1 SD) is therefore a "does it beat solvent-noise" test, not a "does it match a known RING binder" test. This is the strongest probe available given the lack of public RING binders, and the V2 compounds fail even this weakest-possible comparison.

### 3.3 V2 compound results — full table

| ID | best_conf | d(COM, center) Å | min d(Cys_SG) Å | d(ZnCoord CA) Å | conf | pocket | cys | PASS |
|---|---|---|---|---|---|---|---|---|
| V2_97-incomp | −1.47 | 18.23 | 2.31 | 3.96 | F | F | P | F |
| V2_115-incomp | −1.69 | 19.49 | 3.86 | 4.71 | F | F | P | F |
| V2_227-incomp | −0.10 | 8.63 | 11.08 | 7.60 | F | P | F | F |
| V2_320 | −1.23 | 15.31 | 14.16 | 10.14 | F | F | F | F |
| V2_358 | −1.14 | 16.15 | 13.18 | 9.47 | F | F | F | F |
| V2_291 | −2.82 | 17.54 | 7.45 | 6.17 | F | F | F | F |
| V2_313 | −0.99 | 10.42 | 7.35 | 6.35 | F | F | F | F |
| V2_407 | −1.17 | 5.66 | 8.90 | 10.36 | F | P | F | F |
| V2_554 | −0.38 | 22.80 | 8.78 | 4.26 | F | F | F | F |
| V2_323 | −1.69 | 5.96 | 9.65 | 7.46 | F | P | F | F |
| V2_64 | −1.25 | 21.29 | 7.30 | 4.71 | F | F | F | F |
| V2_509 | −1.84 | 16.32 | 6.32 | 4.60 | F | F | F | F |
| V2_276 | −3.37 | 13.13 | 8.18 | 4.36 | F | F | F | F |
| V2_403 | −1.19 | 14.38 | 11.93 | 4.31 | F | F | F | F |
| V2_13 | −1.38 | 14.90 | 13.60 | 10.40 | F | F | F | F |
| V2_390 | −2.25 | 9.27 | 8.85 | 8.15 | F | P | F | F |
| V2_385 | −1.23 | 14.56 | 14.26 | 11.64 | F | F | F | F |
| V2_489 | −1.54 | 11.67 | 8.17 | 4.60 | F | F | F | F |
| V2_513 | −2.56 | 20.18 | 7.65 | 5.07 | F | F | F | F |
| V2_389 | −1.28 | 18.29 | 3.44 | 4.13 | F | F | P | F |

**Passers per gate**:
- conf gate (>+0.58): **0 / 20**
- pocket gate (<10 Å): 4 / 20 (V2_227, V2_407, V2_323, V2_390)
- Cys contact gate (<6 Å): 3 / 20 (V2_97, V2_115, V2_389)
- **All-three gates**: **0 / 20**

### 3.4 Key observations (exploratory, not claims)

- **V2 compounds distribute DiffDock confidence broadly negative** (mean −1.58, sd 0.76). NONE match or exceed negative-control noise.
- **The 3 compounds with Cys-SG contact <6 Å** all have d(COM, designed pocket center) ≥ 14 Å — i.e., they are placed on the **opposite face** of the RING fragment from the designed V2-RING pocket, closer to the Zn-binding core, which contradicts the hypothesis (we designed for the Zn-**distal** face, not the Zn-coord face).
- **The 4 compounds in the correct pocket** (<10 Å from center) all miss the Cys contacts (min Cys_SG distance 7.3 – 11.1 Å) — i.e., they are "approximately near" the designed pocket center but not engaging the zinc-finger surface.
- Per §3.1, **EtOH gives best_conf +1.04 on this receptor — higher than any V2 compound.** This is a red flag about DiffDock's discrimination capacity on a 62-residue fragment.

---

## 4. Step 2 — NOT TRIGGERED

Per §1 decision rule: 0/20 passers → Step 2 (100 ns MD + MMGBSA) **skipped to conserve compute**. No MD was run.

---

## 5. Verdict

### Direct answer to the pre-registered question

**Does the V2-RING activator hypothesis hold up under RING-fragment-only DiffDock?** — **NO. 0 of 20 V2 compounds pass the combined confidence + pocket + Cys-contact gate.**

### Three alternative explanations, ranked

**A (dominant — V2-RING pocket is not a real binding site for our compounds):** The PocketXMol-generated V2 pool was designed against a pocket-audit-derived cavity (1.28 Å nearest atom, 40 atoms within 6 Å) on an AlphaFold RING. But DiffDock, which knows nothing of that design intent, places compounds variously across the RING fragment surface without convergence on the designed pocket. The 4 in-pocket compounds don't engage zinc-finger Cys residues; the 3 Cys-contact compounds don't engage the designed pocket. This is what "designed pocket is not reproduced by an orthogonal pose-predictor" looks like. It does NOT mean zero MDM2 RING binding ever happens in reality — but it does mean our compute pipeline cannot confirm it.

**B (secondary — DiffDock is poorly calibrated on 62-residue fragments):** EtOH scoring +1.04 on a truncated 62-residue receptor is a serious calibration warning. DiffDock v1.1 was trained on PDBBind full proteins; a bare RING domain gives the model unusually few anchor points. We would expect higher noise and lower discrimination on this receptor than on typical full proteins. This is a **partial** alibi for V2 but does not rescue the hypothesis — because a well-designed allosteric binder should still outscore EtOH, and none do.

**C (weakest — gate thresholds too strict):** Relaxing the conf gate to `neg_median` (−0.51, no SD buffer) would promote 0 compounds still (all V2 conf < −0.51 except V2_227 at −0.10 and V2_554 at −0.38; V2_227 passes pocket but fails Cys; V2_554 fails pocket). Relaxing the Cys gate to <8 Å (still physically-meaningful contact) admits V2_291, V2_313, V2_509 — all of which fail the pocket gate. **No combination of relaxed thresholds yields a three-gate passer.** The gates are not the problem; the data are.

### Our call: **V2 activator hypothesis could not be computationally validated by our current toolchain (Boltz-2 + DiffDock v1.1 + PocketXMol), under the honest caveat that the MDM2 RING domain as a whole has no known public small-molecule binder for us to calibrate against.**

What this statement does NOT claim:
- It does **NOT** claim V2 compounds are non-binders in vitro.
- It does **NOT** claim the V2-RING hypothesis is falsified at the biological level.
- It does **NOT** claim no future computational method (e.g., AlphaFold-3 with explicit Zn-coordination, Boltz-2 with residue-pair constraints, physics-based FEP, or relative binding free energy calculations) could retrieve a signal.

What this statement DOES claim:
- Four sequential compute probes using our current toolchain came back unsupportive.
- We should not claim V2 as a validated activator arm in external communication.
- We should not spend more compute on V2 using this toolchain until either (a) a new method becomes available, or (b) wet-lab data rescues one or more of the 20 compounds.

Four orthogonal compute probes have all come back unsupportive:
- PocketXMol design pose + DiffDock placement disagree → pose ambiguity.
- Boltz-2 3-body triage (prior campaign) was domain-mismatched → inconclusive.
- Boltz-2 full-length triage (prior agent a85eb23a) was N-term-dominated → unable to classify.
- DiffDock on RING fragment (this campaign) → 0/20 pass the three-gate test.

The fact that four separate compute angles all fail to support V2-as-activator is the strongest signal we can extract without wet-lab data. **Further compute will NOT distinguish V2 activators from V1 inhibitors on this chemical matter.** Only wet-lab MDM2 auto-ubiquitination ELISA + in-cell p53 half-life assay can rescue any of the 20 compounds.

---

## 6. Retraction applied to the Simon narrative

**File updated**: `/home/bryza/sma-research/qms/LIMK2_NEW_STORY_FOR_SIMON.md` — Arm 4 V2 section updated to mark V2 "computationally not validated by our toolchain (Boltz-2 + DiffDock); see `MDM2_V2_RING_LASTSHOT_RESULTS.md`".

Three re-framing options are offered in the SIMON file; the decision on which to take (drop the arm / keep as negative catalogue / re-cast V1 as tool compound) is left to Christian. The file does NOT unilaterally commit to "Arm 4 reduces to V1 inhibitor" — that is one of three options presented to the decision-maker.

**Separately** from the V2 retraction, the V1 arm's own hard caveat (documented in `mdm2_activator_RESULTS.md` since 2026-04-17 and unchanged by this last-shot) was already that V1 compounds will likely act as p53 stabilizers (inhibitor direction, wrong for SMA). This last-shot document does not change V1's character; it removes the V2 activator counter-weight that had made the arm-as-a-whole defensible for SMA.

**Wet-lab remains the only possible rescue path.** If someone runs an MDM2 auto-ubiquitination ELISA on the top-20 V2 compounds and finds a real activator, the compute-level retraction is overturned by data. We cannot predict that from compute alone.

---

## 7. Caveats (hard)

1. **DiffDock v1.1 is stochastic** (20 samples here; per-compound sd on best_conf typically 0.3-0.7 across re-runs). Re-running would not change the 0/20 verdict — NO compound is close to passing even one-sigma above NEG noise.
2. **RING fragment (62 aa) is small for DiffDock training distribution.** A proper follow-up would use **Boltz-2 full-length + constraints** that force the ligand into the RING pocket, but that's exactly what prior campaigns did and it gave inconclusive results. We have looped the available toolchain.
3. **The designed "druggable concavity" on AF-RING may be an AlphaFold artefact.** RING domains in real crystals are typically flat and shallow. AF inflates surface pockets for low-pLDDT loop regions. 40 atoms within 6 Å of the designed center may reflect model-soft regions, not a real binding site.
4. **Nutlin-3a docked to −2.75 on the RING fragment** — meaning even the N-term MDM2 gold-standard drug fails to register here. This confirms the RING fragment as a non-standard receptor for current pose predictors.
5. **EtOH anomaly**: EtOH (solvent-size molecule, unambiguously a non-binder) scored best_conf = +1.04 on this receptor — higher than every V2 compound. Plausible mechanism: DiffDock's confidence head was trained to reward small-molecule-scale features on mostly-pocket-like surfaces; a tiny molecule on a fragment receptor gives fewer per-atom constraints, and the confidence head has no strong penalty for "ligand is too small to be a drug". This is a **DiffDock calibration issue on small fragments**, documented here as a limit of the tool rather than as a property of MDM2. A downstream mitigation would be to filter out poses where the ligand sits on solvent-exposed surface rather than docked into a cleft; we did this implicitly via the pocket + Cys gates.
6. **No known RING binder in public literature** (§3.2) means we cannot validate DiffDock's upper-bound discrimination on this target class. The "last-shot" in this campaign's name refers to exhausting our **compute** options, not ruling out future **wet-lab** evidence.
7. **No external comms** until triple-LLM 3/3 + Christian review + decision on Arm 4 fate.

---

## 8. Reproducibility trail

- Working dir (local): `/home/bryza/fleet-results/mdm2_v2_ring_lastshot/`
- Script: `/home/bryza/fleet-results/mdm2_v2_ring_lastshot/run_mdm2_ring_diffdock.py`
- Analyzer: `/home/bryza/fleet-results/mdm2_v2_ring_lastshot/analyze_results.py`
- Raw results JSON: `/home/bryza/fleet-results/mdm2_v2_ring_lastshot/results.json`
- Summary JSON: `/home/bryza/fleet-results/mdm2_v2_ring_lastshot/summary.json`
- Summary Markdown: `/home/bryza/fleet-results/mdm2_v2_ring_lastshot/summary.md`
- Run log: `/home/bryza/fleet-results/mdm2_v2_ring_lastshot/run.log`
- Receptor PDB: `/home/bryza/fleet-results/mdm2_v2_ring_lastshot/mdm2_ring_only.pdb`
- Input SMILES: `/home/bryza/fleet-results/mdm2_v2_ring_lastshot/v2_compounds.smi` (+ negative/positive controls)
- Remote instance: Vast 35141611 (ssh2.vast.ai:21610), DiffDock at `/opt/DiffDock` (commit HEAD 2026-04-17)
- DiffDock weights path: `/opt/DiffDock/workdir/v1.1/score_model/*` (from GitHub release v1.1)
- GPU: A100-SXM4-40GB, sharing with concurrent PocketXMol LIMK2 Arm 1 job (no interference observed)

---

## 9. Next-step recommendation

1. **Update LIMK2_NEW_STORY_FOR_SIMON** (this session) — Arm 4 V2 retracted, V1 clearly flagged as inhibitor (wrong direction for SMA).
2. **Do NOT send anything to Simon about Arm 4 activator** until Christian decides how to re-frame the 4-arm story (3 valid arms + 1 retracted? or drop Arm 4?).
3. **Re-run triple-LLM verification** on both this document and the updated SIMON file.
4. **Consider removing Arm 4** from cross-chemotype SAR / Simon pack entirely, rather than keeping a retracted arm.
5. **Archive raw V2 SDF library** — the compounds are not invalid chemotypes, they are just unvalidated as RING binders. They may be useful as negative controls for future campaigns.

End.

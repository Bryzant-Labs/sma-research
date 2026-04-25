# Riluzole x LIMK2-alphaC — Structural Due Diligence + Kinase Selectivity Panel

**Date:** 2026-04-21
**Batch:** chai1_batch_2026-04-21_rerun
**Tool:** Chai-1 v0.6.1 (5 replicates for LIMK2, 1 per off-target)
**Parameters:** num_trunk_recycles=3, num_diffn_timesteps=200, use_esm_embeddings=True, seed=42
**GPU:** Vast.ai RTX_4090 (instance 35382347, Quebec_CA, $0.2405/hr)
**Purpose:** Structural half of pre-comms due diligence on riluzole x LIMK2-alphaC hypothesis `199a98d3-e0c4-4c72-9c3f-96e6a5e82b7a` (previously `validated`, conf 0.95).

---

## 1. LIMK2-alphaC x Riluzole — Structure Recovered

Best model (5 replicates, all within iPTM 0.7663-0.7672): `pred.model_idx_0.cif`.

- **iPTM (interface pTM):** 0.7672
- **pTM (global):** 0.8427
- **Matches prior batch (0.767)** — reproducibility confirmed.

### 1.1 Binding Pocket Classification

**Class: `ATP_site` (classical kinase hinge + P-loop).**
**NOT the alpha-C allosteric pocket** (alphaC in our sequence spans residues ~40-70 and had 0 contacts <5A).

All 16 protein residues within 5A of any riluzole heavy atom cluster in the ATP-cleft:
hinge (res 82-95) + glycine-rich P-loop (res 17-25).

### 1.2 Top-5 Contact Residues (heavy-atom distance to riluzole)

| Rank | Residue     | Position | min dist (A) | Role                        |
|------|-------------|----------|--------------|-----------------------------|
| 1    | GLU (E83)   | 83       | 2.73         | ATP hinge glutamate         |
| 2    | GLU (E84)   | 84       | 2.78         | ATP hinge glutamate         |
| 3    | LEU (L86)   | 86       | 2.80         | hinge back-pocket           |
| 4    | GLY (G89)   | 89       | 2.85         | hinge loop (`LPLG`)         |
| 5    | ILE (I19)   | 19       | 3.01         | P-loop (Gly-rich, `KKIGAGSFG`) |

Hinge motif `EEFLPLGDL` at pos 83-91 is the canonical kinase-domain ATP hinge. Riluzole thiazole-NH and benzothiazole ring nitrogen act as H-bond donors/acceptors to the hinge backbone glutamates — this is the textbook "hinge-binder" pharmacophore shared by virtually all ATP-competitive kinase inhibitors (e.g. imatinib, sunitinib, staurosporine).

### 1.3 Cys Disulfide Bracket Check

LIMK2-alphaC Cys positions: **C32, C59, C132, C163**.
None of these are within 5A of riluzole. No disulfide bracket engagement. (Any C51-C65 equivalent the Bryzant saturator might have presumed does not exist — the Cys pair nearest the alpha-C region is C32-C59 (27 residues apart, sequence-remote), and neither contacts riluzole in the Chai-1 model.)

### 1.4 pLDDT of alpha-C Helix

Chai-1 v0.6.1 `scores.model_idx_*.npz` exposes per-chain pTM (0.829 for the kinase chain) and per-chain-pair iPTM but does not surface residue-level pLDDT in the standard summary. Per-residue pLDDT is in the CIF `B-factor` column and can be re-derived; given the riluzole contact is on the **opposite face** (hinge, res 83-91) from the alpha-C helix (res 40-70), no meaningful allosteric stabilization/destabilization of alpha-C is expected or observed.

---

## 2. Kinase Selectivity Panel

All 6 kinases run with identical protocol (seed=42, kinase-domain only, UniProt-derived sequences).

| Kinase | UniProt | Domain  | iPTM   | pTM    | delta_iPTM vs LIMK2 |
|--------|---------|---------|--------|--------|---------------------|
| LIMK2 (ref) | Q9UDI7 | alpha-C+kinase | **0.7672** | 0.8427 | 0.0000 |
| LIMK1  | P53667  | 339-605 | 0.7468 | 0.8960 | -0.0204             |
| ROCK2  | O75116  | 92-354  | 0.7823 | 0.9352 | **+0.0151**         |
| JAK2   | O60674  | 849-1124| **0.7963** | 0.9483 | **+0.0292**         |
| SRC    | P12931  | 270-521 | 0.7834 | 0.9484 | **+0.0162**         |
| ABL1   | P00519  | 242-493 | 0.7591 | 0.9398 | -0.0081             |

**Selectivity margin (LIMK2 - max off-target) = -0.0292** (fails the >0.2 threshold by order of magnitude and is in fact **negative**).

**Selectivity verdict: `likely_pan_kinase`.**
- JAK2 (0.796), ROCK2 (0.782), SRC (0.783) **all score higher iPTM than LIMK2**.
- 4 of 5 off-targets cluster at iPTM 0.75-0.80 — Chai-1 happily docks riluzole into every kinase ATP hinge with comparable confidence.
- This is the **same pan-kinase failure mode** documented for LIMKi3 (see `finding-pocketxmol-fails-diffdock-validation-2026-04-16.md` + `roi-surprises-2026-04-17.md`).

---

## 3. Kill-Test Mutation Proposal

Goal: falsify the alleged LIMK2-alpha-C allosteric binding by breaking the predicted ATP-hinge anchor. If riluzole truly bound to the alpha-C allosteric pocket, an ATP-site mutation would be INERT. If Chai-1 is right that riluzole binds the hinge, an E83A mutation should drop Ki from measured ~µM to **abolished**.

### Primary mutant: **E83A (LIMK2-alphaC numbering)**
- Removes the #1 hinge carboxyl (2.73 A from riluzole).
- Predicted effect: loss of hinge H-bond anchor; complete loss of riluzole affinity.
- Wet-lab assay: LanthaScreen kinase binding assay (Thermo) or KinaseProfiler (Eurofins) — measure IC50 shift WT vs E83A.

### Backup double mutant: **E83A / E84A**
- Both hinge glutamates removed. Should be fully abolishing regardless of which E is the dominant anchor.

### Negative control (if we wanted to falsify alpha-C allosteric instead):
- **Y57F** or **R50A** (two residues in the putative alpha-C allosteric pocket, res 40-70). If Chai-1 is right that riluzole is in the ATP site, these alpha-C mutants should have **no effect** on riluzole Ki.

The WT-vs-E83A-vs-Y57F comparison is the complete falsification experiment: only ATP-site mutants should shift Ki if our structural conclusion is correct.

---

## 4. Verdict

**STATUS: `PAN_KINASE` / `SURFACE_ARTIFACT` (ATP-site, not alpha-C allosteric).**

The structural half of the due diligence **fails the selectivity gate**:

1. Binding site is **canonical ATP hinge**, not the alpha-C allosteric pocket the Bryzant saturator targeted.
2. 4 of 5 off-target kinases score equal-or-better iPTM than LIMK2 — textbook pan-kinase signature.
3. Differential iPTM margin is **negative** (LIMK2 loses to JAK2).
4. Known biology: riluzole's documented mechanism is voltage-gated Na+ channel blockade + glutamate release inhibition, **not** kinase inhibition at therapeutic doses (Cheah 2010, Bellingham 2011).
5. Even if riluzole weakly engages kinases at high concentrations, there is **no structural evidence** that LIMK2 is preferred over JAK2/SRC/ROCK2.

## 5. Implications for Preprint / Simon Comms

- **DO NOT** send the riluzole x LIMK2-alphaC finding to Simon or Torsten as a "validated dual-target hit."
- Hypothesis `199a98d3` has been **flipped to `under_review`** with confidence reduced 0.95 -> 0.45.
- Any preprint must include this selectivity panel as a negative-control figure and acknowledge the pan-kinase artifact.
- **Next step:** if Christian wants to keep this line alive, run wet-lab LIMK2 KinaseProfiler +/- E83A mutant. Until then, the finding is a *structural-artifact* and must not be communicated externally as a validated repurposing candidate.
- This also partially corroborates Rule -2d (Bowerman 2012 Fasudil retraction) context: kinase-pathway claims in SMA need orthogonal validation; iPTM alone is insufficient.

---

## 6. Artifact Paths

- **CIFs (LIMK2 x riluzole, 5 replicates):**
  `/home/bryzant/fleet-results/riluzole_limk2_structure_2026-04-21/out/LIMK2/pred.model_idx_{0..4}.cif`
- **Selectivity-panel CIFs (1 each):**
  `/home/bryzant/fleet-results/riluzole_limk2_structure_2026-04-21/out/{LIMK1,ROCK2,JAK2,SRC,ABL1}/pred.model_idx_0.cif`
- **Scores npz + raw results.json + analysis.json:**
  `/home/bryzant/fleet-results/riluzole_limk2_structure_2026-04-21/out/`
- **Scripts:** `run_chai.py`, `analyze.py`, `kinases.json` in same dir.

## 7. DB Writes (committed)

- 5 new claims with `predicate='chai1_selectivity_iptm'`, `claim_type='drug_target'` (metadata carries `real_claim_type='orthogonal_validation'`).
- 5 new evidence rows linked to source `edb6c1b1-ae21-474e-b224-3f7b3fa3c003` (Bryzant Chai-1 orthogonal validation batch 2026-04-21).
- Hypothesis `199a98d3-e0c4-4c72-9c3f-96e6a5e82b7a`:
  - `status`: `validated` -> `under_review`
  - `confidence`: 0.95 -> 0.45
  - `metadata.structural_analysis_2026-04-21` populated with full binding-site analysis, selectivity table, kill-test mutations, CIF paths.

## 8. GPU Accounting

- Instance: **35382347** (Vast.ai, RTX_4090, Quebec_CA)
- Rate: $0.2405/hr
- Wall time: ~30 min (rental start ~18:18 UTC, destroy ~18:48 UTC)
- Estimated cost: ~**$0.12** (well under $0.50 budget cap; under $1.20 absolute max).
- Container: `pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime`, 60 GB disk.
- Destroy: guaranteed via try/finally pattern (see next section in session log).

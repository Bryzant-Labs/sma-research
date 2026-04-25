# Cross-Chemotype SAR — 4-Arm SMA Attack

**Status:** APPROVED 2026-04-19 (triple_llm_verify 3/3 PASS 2026-04-17; Christian Fischer human sign-off 2026-04-19 per Claim #16 in CLAIMS_REGISTRY.md)
**Author:** Opus Master Agent
**Date:** 2026-04-17
**Pipeline script:** `/home/bryza/sma-research/qms/scripts/cross_chemotype_4arm_sar.py`
**Inputs (frozen):**
  - LIMK2: `/home/bryza/fleet-results/limk2_activator_alphaC/top_hits.tsv` + `diffdock_results.csv` (panel-complete hits n=4 + padding from C_rel>0 BBB pool to reach n=20)
  - ROCK2: `/home/bryza/fleet-results/rock2_activator_alphaC/boltz2_rescore_ranked.tsv` (top-20 by Boltz-2 iptm)
  - MDM2: `/home/bryza/fleet-results/mdm2_activator/mols_filtered.csv` (top-20 by QED among BBB+Ro5 pass)
  - PERP: `/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/top_binders_ecl{1,2}.tsv` (top-10 per ECL by delta_iptm) — see methodological note below

---

## 1. Methodological note — why PERP is treated as a 4th orthogonal modality, not mixed into Tanimoto

PERP leads are **de-novo mini-protein binders (70-95 aa peptides)**, not small molecules — they cannot be represented in ECFP4 fingerprint space. PERP is therefore **chemotypically orthogonal by construction** to the other three arms (it is a different modality entirely: RFdiffusion + ProteinMPNN + ESMfold + Boltz-2 PPI pipeline, vs PocketXMol small-molecule generation for the kinase/E3 arms). The cross-chemotype Tanimoto heat-map below covers the three small-molecule arms (LIMK2, ROCK2, MDM2 — 60 compounds, 3 × 20).

Writing this explicitly because the naive reader's question is *"you ran 4 campaigns, why is the matrix 60×60 not 80×80?"* — because the 4th arm is a different compound class that the matrix can't represent.

---

## 2. Headline result

**All three small-molecule arms are chemotypically fully disjoint** from each other at the top-20 level (max cross-arm Tanimoto = 0.254, **zero** cross-arm pairs ≥ 0.4, **20/20 unique Murcko scaffolds per arm**). Combined with the PERP mini-protein modality as a 4th independent class, the 4-arm attack is **four truly independent vectors**, not four flavours of the same chemistry.

This is the scientifically correct outcome for a pocket-aware generative pipeline targeting four structurally dissimilar binding sites (two kinase αC-helix pockets in LIMK2 + ROCK2, one E3 ligase p53-cleft in MDM2, two membrane-protein extracellular loops in PERP): PocketXMol's geometry-conditioned generation plus RFdiffusion's backbone-design prior converge on distinct chemistries for distinct pockets. No scaffold contamination is a QC-pass, not a weakness.

---

## 3. Tanimoto matrix stats (ECFP4, 2048-bit, radius 2)

Heatmap (60×60, arms grouped LIMK2→ROCK2→MDM2, white lines = arm boundaries):
`/home/bryza/sma-research/qms/scripts/out/tanimoto_heatmap_80x80.png`

Raw numpy matrix: `/home/bryza/sma-research/qms/scripts/out/tanimoto_matrix.npy` with label map in `tanimoto_matrix_labels.csv`.

### Per-arm (intra-arm diversity inside each top-20)

| Arm | n_pairs | mean | median | max | p95 | ≥0.4 | ≥0.6 |
|---|---:|---:|---:|---:|---:|---:|---:|
| LIMK2 vs LIMK2 | 380 | 0.148 | 0.139 | **0.342** | 0.244 | 0.0% | 0.0% |
| ROCK2 vs ROCK2 | 380 | 0.114 | 0.112 | 0.272 | 0.163 | 0.0% | 0.0% |
| MDM2 vs MDM2   | 380 | 0.122 | 0.119 | 0.235 | 0.183 | 0.0% | 0.0% |

**Reading:** each arm's top-20 is itself highly diverse. The *within-arm* maxima (0.34 for LIMK2, 0.27 for ROCK2, 0.24 for MDM2) are well below the conventional "same scaffold" threshold of ~0.6-0.7. This matches PocketXMol's published behaviour (high chemotype diversity, low generator-locking).

### Cross-arm (inter-arm distinctness)

| Arm-pair | n_pairs | mean | median | max | p95 | ≥0.4 | ≥0.6 |
|---|---:|---:|---:|---:|---:|---:|---:|
| LIMK2 × ROCK2 | 400 | 0.103 | 0.099 | 0.221 | 0.162 | **0.0%** | 0.0% |
| LIMK2 × MDM2  | 400 | 0.109 | 0.104 | **0.254** | 0.164 | **0.0%** | 0.0% |
| ROCK2 × MDM2  | 400 | 0.111 | 0.109 | 0.211 | 0.165 | **0.0%** | 0.0% |

**Reading:** zero compound pairs across arm boundaries cross the "likely same chemotype" threshold of Tanimoto ≥ 0.4. The single highest cross-arm pair (LIMK2 × MDM2 at 0.254) is well below background — the matrix contains no "shortcut molecules" that would pass in two campaigns on the same scaffold.

This reproduces and extends the ROCK2-vs-LIMK2 cross-connection result already recorded in the ROCK2 campaign: `/home/bryza/fleet-results/rock2_activator_alphaC/cross_connection_limk2.json` — 0 exact-SMILES overlap, 0 near-similar scaffolds at Tanimoto ≥ 0.4. Here we extend to include MDM2 and reach the same conclusion.

---

## 4. Murcko scaffold clustering

Full per-compound table: `/home/bryza/sma-research/qms/scripts/out/murcko_cluster_per_arm.csv`.

| Arm | Unique Murcko scaffolds | Total compounds | Singletons (scaffold used once) |
|---|---:|---:|---:|
| LIMK2 | **20** | 20 | **20** |
| ROCK2 | **20** | 20 | **20** |
| MDM2  | **20** | 20 | **20** |

Every top-20 compound sits on its own scaffold. No arm is a single-chemotype series being re-sampled. The 60-compound small-molecule space **spans 60 distinct Murcko scaffolds**.

**Implication for downstream compute:** each lead is an independent medchem starting point. Going to ADMET + FEP+ + Rosetta-Relax validation for top-5 per arm is 15 independent series, not 3 flavour-tests of the same series. Cost scales; but so does de-risking.

---

## 5. Arm-by-arm anchor chemotypes (representative)

### 5.1 LIMK2-αC activator (panel-complete top hits; see `limk2_activator_alphaC_RESULTS.md`)

- **Rank 1 — `COc1cc(C)ccc1C(C)NCC1=CC=[N+]2C1=Nc1c[n+](Cc3cncc[nH+]3)ccc12`** (sel_z +0.86, iptm_LIMK2 0.924, C_rel +0.003)
  Carries pyridinium + imidazolium protonation artifacts from PocketXMol SDF generation — flagged for QM/MM neutralisation before any downstream claim. Currently the top selectivity-z hit on paper but compromised by charge state.
- **Rank 2 — `CS(=O)(=O)c1ccccc1-c1cccc(Oc2ccc(C(N)=O)cc2)c1`** (sel_z +0.83, iptm_LIMK2 0.942, C_rel +0.101)
  Sulfone + diaryl ether + primary amide. **Neutral at physiological pH**, no charge artifacts. Cleanest drug-like scaffold in the panel — recommended for 20 ns MD follow-up as the lead compound.

### 5.2 ROCK2-αC activator (see `rock2_activator_RESULTS.md`)

- **Rank 3 — `ClC1CCCC2NC(CNC3CCN(c4cccnc4)C3)NCC12`** (iptm 0.953, QED 0.72)
  Piperidine + pyridine scaffold, kinase-friendly, no obvious reactive groups. The cleanest top-10 lead after medchem triage (ranks 1, 2, 4 contain hydrazine/azo fragments requiring follow-up).

### 5.3 MDM2 activator (see `mdm2_activator_RESULTS.md`)

- **Rank 1 — `C[C@@H]1NC(=O)C2=C1CCCc1nn(C[C@@H](C)c3ccccc3)cc12`** (QED 0.943, MW 321, logP 3.30)
  Pyrazolo-fused bicycle with benzyl substitution. Drug-like cluster — distinct from Nutlin-family inhibitors (the entire clinical-stage MDM2 chemical class). Mechanistic direction (activator vs inhibitor) requires post-hoc Boltz-2 comparison against MDM2-p53-peptide complex.

### 5.4 PERP mini-protein binders (see `PERP_binder_design_RESULTS.md`)

- **Overall top lead — H2b_9_s2** (87 aa, ECL2, delta_iptm +0.468, iptm_target 0.596, pLDDT 0.794): `REKEREALLAAALAEAREVGEAILADPENAEALLAAAEAEVEAARARAEALAAEDPERAADELAAVDVRAAVLRETAILLAEKRAAA`
- **ECL1 top lead — H1a_38_s7** (85 aa, delta_iptm +0.438): `AEAAEAAELEAHIEELARRVLEEVRARYPDYPGAESVARDTRDAMRAAAAEARAAGAPLEEIKAAIEAAARAQLARWLALLDARR`

Mini-protein class, not small molecules. 3-helix bundle geometry, ~70-90 aa, amphipathic helix-1 engages hotspot triplet.

---

## 6. Conclusions for the Simon reply pack

1. **4 independent attack vectors, not 4 flavours of one.** Intra-arm Tanimoto median ≤ 0.15, inter-arm max ≤ 0.25, zero cross-arm pairs ≥ 0.4, zero Murcko scaffold overlap, 4th arm a different modality entirely. These 4 tracks cannot fail together from any single chemotype-specific liability.
2. **Minimum follow-up work for publication-quality support:** top-5 per small-molecule arm × {20 ns holo MD, MM-GBSA, FEP+, ChEMBL-Ki calibration} + top-5 per ECL for PERP × {Rosetta InterfaceAnalyzer, AF3 / Chai-1 co-fold, 50 ns MD MM-GBSA}. Estimated compute: ~€300-500 on Vast A100/H100 rental, 3-5 d wall-clock.
3. **Fasudil rationale is NOT tested here.** The cross-chemotype SAR says nothing about Fasudil direction; that's in `PERP_dossier/fasudil_two_layer_diagram.md`. The SAR is scaffold-novelty evidence: our compounds are **not** fasudil-like (fasudil SMILES = `O=S(=O)(N1CCCN=CC1)c1cccc2cnccc12`, ECFP4 vs our top hits < 0.15 for all 60). No chemotype contamination across the therapy-class boundary.
4. **What this does NOT say.** It does not say any of our 60 small molecules is functionally validated. PocketXMol plus Boltz-2 iptm plus DiffDock C_rel is an interface-quality proxy pipeline. Wet-lab enzymatic assay (LIMK2 / ROCK2 kinase activity panels, MDM2-p53 displacement AlphaLISA) is required before any "activator" language outside internal notes.

---

## 7. Open questions for Simon

1. **Which of the 4 arms does your NMJ biology prioritize?** Our PERP arm is specifically scoped to your unpublished ECL finding. LIMK2 + ROCK2 are MN-intrinsic cytoskeletal; MDM2 is MN-intrinsic apoptosis. Resource allocation for wet-lab validation depends on which arm you want to take into assay first.
2. **Which cell model is reference for LIMK2 direction?** The meta-analysis split (DOWN in Hb9-iMN/iN, UP in SH-SY5Y) means activator vs inhibitor is a patient-model-dependent choice. Your position on Hb9-iMN vs SH-SY5Y as reference model would let us commit to one of the two LIMK2 directions.
3. **Muscle-compartment vs MN-intrinsic pathology — which dominates in your patient cohorts?** This determines whether existing pan-ROCK-inhibitor pharmacology stays on the table as muscle-directed adjunct or is ruled out entirely in favor of MN-intrinsic rescue (our Arm 2 ROCK2-αC activator).
4. **Scaffold-novelty / IP status:** are any of the top Murcko scaffolds (`/home/bryza/sma-research/qms/scripts/out/murcko_cluster_per_arm.csv`) already in your group's patent-watch list? We have not done an IP-novelty screen yet.

---

## 8. Triple-LLM QC gate

| Reviewer | Verdict | Date |
|---|---|---|
| OpenAI GPT-4o | **PASS** | 2026-04-17 evening |
| Groq Llama-3.3-70B | **PASS** | 2026-04-17 evening |
| Google Gemini 2.0 Flash | **PASS** | 2026-04-17 evening |

Aggregate: **3/3 PASS.** Verifier script: `/home/bryza/gpu-fleet/scripts/triple_llm_verify.py`.

Advisory notes (all non-blocking):
- GPT-4o: add detail on PERP mini-protein methodology; clarify LIMK2-Rank-1 protonation-artifact impact on bioactivity.
- Groq-Llama: add PocketXMol SDF generation notes; expand QM/MM neutralisation discussion.
- Gemini: no blocking notes.

External transmission: APPROVED. Christian Fischer human sign-off on Claim #16 (composite 4-arm response) recorded 2026-04-19 in `CLAIMS_REGISTRY.md`.

---

*APPROVED for external transmission 2026-04-19. Numbers in this file are traceable to the frozen input files listed in the header.*

# Wet-Lab Handoff — Top-5 per 4-Arm SMA Attack

**Status:** DRAFT v1 — no external comms until triple_llm 3/3 PASS + Christian Fischer sign-off
**Date:** 2026-04-17
**Author:** Opus Master Agent
**Gate-context:** Task 1 of final QMS deliverables package; Claim #16 promotion pathway (see CLAIMS_REGISTRY.md)
**Source inputs (frozen):**
- LIMK2: `/home/bryza/fleet-results/limk2_activator_alphaC/top_hits.tsv` (4 panel-complete + pending) + LIMKi3 reference (rank 5)
- ROCK2: `/home/bryza/fleet-results/rock2_activator_alphaC/boltz2_rescore_ranked.tsv` (top-5 by Boltz-2 iptm)
- MDM2: `/home/bryza/fleet-results/mdm2_activator_v2_allosteric/top100_by_cfd_pos.csv` (top-5 by cfd_pos)
- PERP: `/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/top_binders_ecl{1,2}.tsv` (top-3 ECL1 + top-2 ECL2 = 5)

---

## 1. Scope and methodology

This document scores 20 lead compounds (5 per therapeutic arm) for wet-lab feasibility. "Feasibility" here means: *given a collaborator with access to CRO-grade medchem and standard kinase / PPI assay equipment, how quickly and cheaply can the compound be tested for its hypothesized activity?*

Four feasibility axes per compound:
1. **Synthesis cost / route** (rough) — commercial availability vs custom synthesis, SA-score for difficulty
2. **Assay readiness** — which wet-lab assay per arm
3. **Readiness score (1-5)** — composite: 1 = low feasibility (expensive, slow, uncertain), 5 = high feasibility (commercial, ready assay, drug-like)
4. **Expected cost range per compound-test** (EUR)

### Scoring conventions

- **SA-score**: RDKit Ertl-Schuffenhauer score (1 = very easy; 10 = very hard). Computed via `rdkit.Contrib.SA_Score.sascorer`. Cut-offs: ≤3 = "commercial or easy custom", 3-4 = "standard custom medchem", >4 = "hard, consider scaffold-hop before assay".
- **Commercial availability (heuristic)**: SMILES pattern inspection for "standard kinase-binder" features (pyridine + sulfone + amide + commonly-traded fragments). Exact-SMILES ChEMBL/PubChem query NOT run in this local session (requires ChEMBL web-service call, out of scope).
- **Expression feasibility (PERP only)**: Cys content, length, N-terminal Met, low-complexity regions, %Ala, %Arg+Lys.
- **Readiness score 1-5**: composite scalar — 5 if commercial AND low SA AND QED > 0.6 AND passes Lipinski 4/4 AND has a 1-assay readout; 1 if custom AND high SA AND has charge-state or reactive-group flags.

---

## 2. Arm 1 — LIMK2-αC activator (top 5)

**Source:** `/home/bryza/fleet-results/limk2_activator_alphaC/top_hits.tsv`

### Suggested wet-lab assay

- **Primary activity:** **Kinase-Glo® LIMK2 activity assay (Promega)** — luminescent ATP-depletion readout. LIMK2 phosphorylates cofilin-derived peptide substrate; ATP depletion measured over time. Compounds that INCREASE ATP depletion rate vs basal LIMK2 = **activators**. Compounds that DECREASE = inhibitors. Approximate kit cost: 300 EUR + plate consumables.
- **Alternative:** **IMAP® Progressive Kinase Assay (Molecular Devices)** — fluorescence polarization, substrate-agnostic, nanomole-scale. ~350 EUR kit.
- **Secondary (orthogonal):** **Cofilin-S3 phospho-ELISA** in LIMK2-transfected HEK293 cells — functional downstream readout. ~200 EUR/compound.
- **Must include:** LIMKi3 (commercial LIMK-inhibitor) as negative control (should show inhibition, not activation). Y-27632 (ROCK-inhibitor) as pathway control.

### Top 5 LIMK2 compounds

| # | Rank | SMILES | MW | logP | QED | SA | sel_z | iptm | C_rel | Synthesis | Readiness | EUR/test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L1 | Top-1 | `COc1cc(C)ccc1C(C)NCC1=CC=[N+]2C1=Nc1c[n+](Cc3cncc[nH+]3)ccc12` | 427.5 | 2.60 | 0.59 | **4.80** | +0.86 | 0.924 | +0.003 | **Hard custom** — pyridinium + imidazolium charges are PocketXMol protonation artifacts; neutral-form chemistry is polyheterocyclic fused system requiring 4-5 synthesis steps. Flag: likely unstable in DMSO stock. | **2/5** | ~600-900 (custom synthesis + QC) |
| L2 | Top-2 | `CS(=O)(=O)c1ccccc1-c1cccc(Oc2ccc(C(N)=O)cc2)c1` | 367.4 | 3.65 | **0.75** | **1.89** | +0.83 | 0.942 | +0.101 | **Easy** — diaryl ether + sulfone + primary amide. Standard Ullmann / Chan-Lam + sulfonylation; 2-3 steps. Likely traceable to a commercial intermediate. **Recommended lead.** | **5/5** | ~80-150 (commercial or simple custom) |
| L3 | Top-3 | `CCc1nc2ccc[nH+]c2cc1OCc1ccc2[nH]cc(C(=O)O)c2c1` | 348.4 | 3.37 | 0.58 | 3.33 | +0.15 | 0.915 | +0.245 | **Medium** — naphthyridine + indole-2-carboxylic acid tethered via benzyl ether. Pyridinium charge is likely a PocketXMol artefact; neutral form achievable with standard medchem. | 3/5 | ~300-500 |
| L4 | Top-4 | `COc1cc(OC)c(OC)c(C(=O)N2CCN(C(=O)c3ccncc3)CC2)c1` | 385.4 | 1.71 | **0.78** | **2.11** | +0.01 | 0.910 | +0.198 | **Easy** — trimethoxybenzamide + isonicotinamide piperazine. 2 amide couplings from commercial acids; scaffold in commercial catalogs (e.g., Enamine REAL). | **5/5** | ~40-100 (likely commercial) |
| L5 | Reference | `Nc1ccc2cc(Nc3ccc(C(=O)Nc4ccccc4)cc3)c(Cl)cc2n1` (LIMKi3) | 388.9 | 5.47 | 0.43 | 2.02 | — | — | −0.521 (native) | **Commercial** — Pfizer Chemical Library, Cayman Chemical, Sigma-Aldrich. Reference LIMK-inhibitor. NOT a lead; assay control only. | 5/5 (as control) | ~50 per 10 mg (commercial) |

### Arm 1 notes

- **L2 (43.sdf, sel_z +0.83)** is the recommended lead for first wet-lab assay — easy synthesis, high QED, low SA-score, neutral at physiological pH.
- **L1 (14.sdf)** carries protonation artifacts; wet-lab requires QM/MM-neutralized synthesis plan OR scaffold-hop before ordering. Currently **NOT RECOMMENDED** to send to synthesis.
- **L4 (3.sdf)** is at noise floor on sel_z (+0.01) — worth a wet-lab assay anyway because synthesis is trivial and panel-z is noisy; quick CRO order + Kinase-Glo run would resolve whether this is a real activator or a random-positive.
- The activator hypothesis (LIMK2 DOWN in Hb9-iMN/iN per Claim #9 → restore cytoskeletal dynamics) is **model-dependent** (SH-SY5Y shows UP). **HARD PREREQUISITE:** Christian + Simon must explicitly commit to a reference cell model (Hb9-iMN, iN, hiPSC-MN, or SH-SY5Y) BEFORE any activator assay is ordered. If the chosen reference shows CFL-axis UP (e.g., SH-SY5Y), the activator-direction compounds in this arm become INHIBITOR candidates (direction-of-intervention flipped). Do not proceed to synthesis until this decision is made.

---

## 3. Arm 2 — ROCK2-αC activator (top 5)

**Source:** `/home/bryza/fleet-results/rock2_activator_alphaC/boltz2_rescore_ranked.tsv`

### Suggested wet-lab assay

- **Primary activity:** **ROCK2 kinase activity assay (Cell Signaling Technology, kit #7788 or #9910)** — substrate: myelin basic protein or MYPT1-derived peptide. Readout: ³²P-ATP incorporation (standard gold) OR ADP-Glo luminescent (EUR-friendly). ~400 EUR/kit.
- **Alternative:** **Myosin Light Chain (MLC) phosphorylation in A7r5 or primary MEF cells** — functional downstream (ROCK → MLCP inhibition → MLC phosphorylation). pMLC2(Ser19) ELISA or Western. ~300 EUR/plate.
- **Pathway validation:** pair with Y-27632 (pan-ROCK inhibitor, negative control — must not show activation) and ATP-site ROCK2 inhibitor benzoxaborole (co-crystal ligand from 4L6Q PDB, should dose-dependently inhibit).
- **Warning:** ROCK2 activator hypothesis is **first-in-class** (no published ROCK2 activator exists globally). Wet-lab validation is genuinely exploratory.

### Top 5 ROCK2 compounds

| # | Rank | SMILES | MW | logP | QED | SA | iptm | Notes | Synthesis | Readiness | EUR/test |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 | Top-1 | `Clc1ccc2c(n1)NC(NC1CCCc3c(nc4ccncnc3-4)C1)C2` | 366.9 | 2.86 | 0.54 | 4.07 | 0.976 | Chloropyridine + pyrido-pyrazine fused scaffold | **Medium-hard** — 3 ring-fused scaffolds require bespoke synthesis, 4-6 steps | 3/5 | ~400-700 |
| R2 | Top-2 | `COc1ccc(CCNNC2CCCC3C(=O)CCCC3C2N)cc1` | 345.5 | 2.20 | 0.54 | 4.40 | 0.968 | **⚠ DO NOT ORDER** — hydrazine N-N linkage is a known metabolic liability (in-vivo oxidation → diazonium). Listed here for completeness of "top 5 by Boltz-2 iptm" reporting. Medchem verdict: **KILL**. Substitute with R5 or R3 as active lead. | **Do not synthesize** — scaffold-hop required before any assay order | **1/5 (dead scaffold)** | N/A (not to be ordered) |
| R3 | Top-3 | `ClC1CCCC2NC(CNC3CCN(c4cccnc4)C3)NCC12` | 349.9 | 1.54 | **0.72** | **4.40** | 0.953 | Piperidine + pyridine scaffold — clean kinase-friendly | **Medium** — piperidine + pyridine with chloro-cyclohexane cap; 3-4 steps. **Recommended lead.** | **4/5** | ~250-400 |
| R4 | Top-6 | `CC1CCC(O)C2OC2C2(C1)CC1Cc3ccccc3OC1=C2O` | 328.4 | 3.35 | **0.72** | **4.99** | 0.934 | Natural-product-like fused ring; epoxide flag | **Hard** — polycyclic natural-product-like, requires stereoselective synthesis; SA 4.99 | 2/5 | ~700-1200 |
| R5 | Top-10 | `Oc1ccc(CN2N=C(c3ccc(O)cc3)Nc3ccccc32)cc1` | 331.4 | 3.89 | 0.68 | **2.43** | 0.917 | Triazoloquinoline bis-phenol — drug-like, Lipinski 4/4 | **Easy** — benzylation of triazolo-quinoline + reductive amination; 2-3 steps. **Recommended lead (cost-optimal).** | **5/5** | ~100-200 |

### Arm 2 notes

- **R5 (599.sdf)** is the cost-optimal lead — easiest synthesis, clean scaffold, QED 0.68, Lipinski 4/4. Likely traceable to a commercial building block.
- **R3 (533.sdf)** is the highest-confidence lead (iptm 0.953, QED 0.72) with acceptable synthesis cost.
- **R2 (170.sdf, hydrazine) must NOT be ordered** — hydrazine N-N bond is a known metabolic liability (oxidation to diazonium in vivo). Listed in the top-5 table only for Boltz-2 iptm ranking transparency; do not treat as a wet-lab candidate. Use R3 or R5 as the active leads. RESULTS doc (`rock2_activator_RESULTS.md`) already flags this.
- **ROCK2 activator hypothesis is genuinely first-in-class.** No precedent. Any wet-lab positive is a novel observation; any negative rules out the activator direction. Either result is scientifically valuable.

---

## 4. Arm 3 — MDM2 V2-RING allosteric activator (top 5)

**Source:** `/home/bryza/fleet-results/mdm2_activator_v2_allosteric/top100_by_cfd_pos.csv`

### Suggested wet-lab assay

- **Primary activity:** **MDM2-p53 time-resolved FRET (TR-FRET)** — e.g., Cisbio "MDM2/p53 binding kit" or BPS Bioscience kit. Measures MDM2 binding to p53-derived peptide. Preserved binding = **activator** (does not compete p53 out; allosteric site); disrupted binding = **inhibitor** (Nutlin-like, ORTHOSTERIC). **Direction discriminator.** ~600 EUR/kit.
- **Mechanism probe:** **MDM2 E3 ligase auto-ubiquitination assay** (e.g., R&D Systems kit #U-110). Readout: ubiquitin ladder on Western. Compounds that INCREASE auto-ubiquitination = activators (enhance E2~Ub handoff). Compounds that don't = either inactive or non-activator binders.
- **Cell-based (downstream):** **p53 half-life in SMN-deficient MN-like cells** — pulse-chase Western. Activator = shorter p53 half-life (faster MDM2-mediated degradation). Christian's MN model (iPSC-Hb9 with SMN-KD or SMA-patient-derived) is the ideal context.
- **Selectivity counter-screens:** MDMX/MDM4 (paralog), BIRC3 and TRIM28 (unrelated E3 RINGs). TR-FRET kits or activity assays — ~300 EUR each.

### Top 5 MDM2 compounds

| # | Rank | SMILES | MW | logP | QED | SA | BBB | cfd_pos | Notes | Synthesis | Readiness | EUR/test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M1 | Top-1 | `CCOC(O)c1cc2[nH+]ccc-2c2c(c1)CC(C)(C)C2.c1ccc2[nH]nnc2c1` | 391.5 | 3.72 | 0.52 | 4.35 | 0.91 | 2.287 | **Multi-component (two disconnected fragments)** — only larger fragment will enter assay | **Problematic** — as-generated is 2-component; single-scaffold extraction needed | 2/5 | ~400-700 |
| M2 | Top-4 | `CN1C(=O)c2[nH]nc(NC(CCc3ccc(C#N)cc3)c3ccccc3)c2C1=O` | 385.4 | 3.29 | 0.63 | **3.10** | 0.80 | 2.320 | Pyrazolo-pyrimidinedione + cyano-phenyl; drug-like; single connected component | **Medium** — 4 steps: pyrazolo-pyrimidinedione assembly + N-alkylation. **Recommended cost-optimal lead.** | **4/5** | ~200-400 |
| M3 | Top-5 | `CNC(O)c1cccc(C2=CC3N4CCN=C4NC(=O)C3(C)CCC2)c1` | 354.5 | 1.64 | **0.72** | 4.44 | 1.00 | 2.360 | Spirobicyclic imidazoline amide — novel scaffold, clean | **Medium-hard** — spirobicyclic + chiral center; 4-5 steps with stereocontrol | 3/5 | ~500-900 |
| M4 | Top-6 | `C1=NC2=CC=C(c3ncccn3)N=COc3cc(-c4ccccc4)nc(c3=C2)=C1` | 377.4 | 2.53 | 0.69 | 4.88 | 1.00 | 2.424 | Extensive ring-fused aromatic — likely RDKit parsing artefact (two `=` in non-aromatic ring); flagged for medchem review | **Problematic** — SMILES valency suggests parsing error; requires structure-verification before synthesis | 2/5 | ~600-1000 |
| M5 | Top-3 (incomp) | `CN1CCCCCN1.O=C1OC2=C3C(CCC2)OOC3c2ccc(O)c(O)c21` | 390.4 | 2.68 | 0.35 | 4.43 | 0.83 | 2.288 | **Multi-component** — piperidine + catechol-chromone peroxide. Peroxide = stability flag | **Problematic** — multi-component + peroxide; NOT RECOMMENDED | 1/5 | ~600-1000 |

### Arm 3 notes

- **M2 (320.sdf)** is the recommended lead — lowest SA, drug-like, clean single-component SMILES, MDM2-RING-plausible heterocycle with amide handle.
- **3 of top 5 are multi-component or SMILES-suspect** — this is a known PocketXMol artefact on the complex RING pocket. The downstream Boltz-2 selectivity panel will filter these naturally; prioritize single-component compounds when ordering synthesis.
- **Direction discriminator (activator vs inhibitor) is MANDATORY** — TR-FRET MDM2-p53 binding assay resolves this in one experiment. If compound disrupts binding → V1-site inhibitor (Nutlin-like, WRONG direction for SMA); if compound preserves binding AND enhances ubiquitination → V2-site activator (CORRECT direction).
- The "V2-RING activator" concept is first-in-class globally — ZERO precedent. Any wet-lab positive is a pharmaceutical first.

---

## 5. Arm 4 — PERP ECL de-novo mini-protein binders (top 5)

**Source:** `/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/top_binders_ecl{1,2}.tsv`

### Suggested wet-lab assay

Protein binders, not small molecules → different assay stack:

- **Expression:** E. coli BL21(DE3) + pET28a(+) N-terminal His6 tag. 50 mL culture + Ni-NTA purification + SEC → ~1 mg pure protein. **Expected cost: ~150-300 EUR per binder (synthetic gene + cloning + expression + purification).** Total ~750-1500 EUR for 5 binders.
- **Primary binding:** **Bio-Layer Interferometry (BLI, Octet)** vs recombinant PERP-ECL1 or ECL2 peptide (purchased from commercial peptide synthesis, ~300 EUR/peptide). Kd measurement. ~800 EUR/binder-target including consumables.
- **Alternative:** **SPR (Biacore)** for higher sensitivity if BLI Kd > 10 μM.
- **Confirmation:** **Pull-down** from PERP-overexpressing HEK293 cell lysate using His-tagged binder as bait.
- **Specificity:** **BLI/SPR counter-screens** vs related PMP22-family proteins, or scrambled-PERP-ECL peptide (confirms sequence-specificity).
- **Warning:** scrambled control in compute (seeded shuffle) was sequence-scrambled but NOT conformation-scrambled. Wet-lab binding to linear peptide may underestimate true PERP-ECL-conformation binding; authentic PERP expression in mammalian cells OR synthetic disulfide-bonded PERP-ECL peptide is ideal.

### Top 5 PERP binders

| # | design_id | ECL | len | pLDDT | iptm | Δiptm | Cys | N-term Met | %Ala | Expression risk | Synthesis | Readiness | EUR/test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | H1a_38_s7 | ECL1 | 85 | 0.802 | 0.573 | +0.438 | 0 | yes | 33% | **Low** — no Cys, N-term Met present, 3 Pro, 1 Trp | Synthetic gene + E. coli | **5/5** | ~700-1200 (gene + expression + BLI) |
| P2 | H1c_25_s4 | ECL1 | 84 | 0.804 | 0.522 | +0.415 | 0 | no | 48% | Medium — no N-term Met (need Met start for E. coli), 48% Ala high | Synthetic gene + add N-Met | 3/5 | ~800-1300 |
| P3 | H1c_25_s5 | ECL1 | 84 | 0.825 | 0.492 | +0.373 | 0 | no | **70%** | **High** — 70% Ala + poly-Ala run of 10 residues; solubility/aggregation risk; likely a degenerate RFdiffusion trap | **NOT RECOMMENDED** for initial order; flag for re-design | **1/5** | ~1000-1500 (high re-work risk) |
| P4 | H2b_9_s2 | ECL2 | 87 | 0.794 | 0.596 | +0.468 | 0 | no | 37% | Medium — no N-term Met; otherwise clean | Synthetic gene + add N-Met | **4/5** | ~700-1200 |
| P5 | H2c_11_s1 | ECL2 | 81 | 0.797 | 0.528 | +0.433 | 0 | yes | 52% | Medium — N-term Met present, 52% Ala high; likely still foldable | Synthetic gene + E. coli | **4/5** | ~700-1200 |

### Arm 4 notes

- **P1 (H1a_38_s7)** is the cleanest candidate — N-term Met, reasonable amino-acid distribution, highest Δiptm vs scrambled in ECL1 (+0.438). **Recommended priority.**
- **P3 (H1c_25_s5)** has 70% alanine + poly-Ala run 10 — likely a degenerate RFdiffusion/ProteinMPNN trap (low-complexity regions tend to aggregate or mis-fold). NOT RECOMMENDED — flag for ProteinMPNN re-design at temperature 0.3-0.5 with alanine penalty.
- **PERP ECL disulfides** (native C19-C21, C45-C47 in ECL1) are NOT preserved in our design because RFdiffusion contigs did not enforce SSbond records. Wet-lab binding to oxidized native-folded PERP may differ from to reduced linear-ECL peptide. First-pass BLI should use SYNTHETIC disulfide-folded peptide to match in-compute model fidelity.
- **Full complement of 43 leads** exists beyond top-5 (`PERP_binder_design_RESULTS.md`). Top-5 is a cost-constrained priority list for first wet-lab round.

---

## 6. Composite wet-lab cost estimate

| Arm | Compounds | Synthesis + assay per compound (EUR) | Arm total (EUR, top-5 minus killed) |
|---|---:|---|---:|
| LIMK2 | 4 (L1 needs neutralization first; L5 is commercial control) | 40-900 | ~1,200-2,000 |
| ROCK2 | 4 (R2 killed, hydrazine) | 100-1200 | ~1,100-2,300 |
| MDM2 | 2-3 viable (M1/M4/M5 problematic) | 200-1000 | ~400-1,500 |
| PERP | 4 (P3 excluded, poly-Ala degenerate) | 700-1500 | ~2,800-4,500 |
| **Grand total (viable subset)** | **~14 orderable of 20** | — | **~5,500-10,500 EUR** |

Recommended first-round minimum (4 priority compounds, 1 per arm):
- L2 (LIMK2-αC, ~150 EUR)
- R5 (ROCK2-αC, ~150 EUR)
- M2 (MDM2-V2, ~300 EUR)
- P1 (PERP-ECL1, ~900 EUR with gene + expression + BLI)

**First-round minimum total: ~1,500 EUR** for proof-of-concept across all 4 arms.

---

## 7. Quality gates

| Gate | Status | Notes |
|---|---|---|
| Source data frozen | PASS | inputs listed in header |
| Small-molecule rdkit + SA scoring | PASS | RDKit `sascorer` via Contrib; MW / logP / TPSA / HBD / HBA / QED from standard RDKit Descriptors |
| PERP expression-risk heuristic | PASS | length + Cys + Met + %Ala + poly-A + %basic run against rule-set |
| Commercial availability — exact-SMILES query against ChEMBL/PubChem | **NOT RUN** (out of scope local-CPU; requires ChEMBL web call). Estimates here are heuristic (SMILES pattern inspection). | Gap: add ChEMBL API call to synthesis-cost module before external use. |
| Triple-LLM verify (v1) | **1/3 PASS (v1, 2026-04-17)** — GPT-4o PASS; Groq-Llama FAIL (generic "lack of citations" BLOCKs — not actionable); Gemini FAIL (v1) on R2-hydrazine contradiction + LIMK2-model-dependent gate. **v2 pending** after R2 language tightened + LIMK2-model-dependent language made a hard prerequisite (done in this revision). | gate-mandatory before external transmission. Results saved at `wet_lab_handoff_20_compounds_verify.json`. |
| Christian Fischer human sign-off | **PENDING** | required for external comms |

### Triple-LLM verification command (to run)

```bash
python3 /home/bryza/gpu-fleet/scripts/triple_llm_verify.py \
    --file /home/bryza/sma-research/qms/wet_lab_handoff_20_compounds.md
```

---

## 8. Cross-references

- Claim #16 (CLAIMS_REGISTRY.md) — this doc is Gate-2 evidence for the composite claim (per-arm wet-lab feasibility confirmed)
- `cross_chemotype_4arm_SAR.md` — Tanimoto matrix / Murcko scaffold uniqueness (20 unique per arm, all 60 small-mols on distinct scaffolds)
- `limk2_activator_alphaC_RESULTS.md` — source of L1-L5 numbers
- `rock2_activator_RESULTS.md` — source of R1-R5 numbers
- `mdm2_v2_allosteric_RESULTS.md` — source of M1-M5 numbers
- `PERP_binder_design_RESULTS.md` — source of P1-P5 numbers

---

## 9. Caveats (do not strip)

1. **ChEMBL/PubChem exact-SMILES query not run.** "Commercial availability" scores here are heuristic (SMILES-pattern inspection), not authoritative. Before ordering from a CRO, run ChEMBL + PubChem + Enamine exact-SMILES matching on each compound.
2. **SA-score is not a definitive cost estimator.** SA = synthetic accessibility ∈ [1,10]; real CRO quotes depend on scale, stereocontrol, and IP restrictions.
3. **LIMK2 activator hypothesis is model-dependent.** Per Claim #9, LIMK2 direction in SMA MN depends on model system (DOWN in Hb9-iMN / iN, UP in SH-SY5Y / hiPSC-MN). Before ordering activators, Christian/Simon must commit to a reference model. Inhibitors are the opposite recommendation and would use the same synthesis cost structure.
4. **ROCK2 activator is first-in-class globally.** No published precedent. Wet-lab result is genuinely exploratory.
5. **MDM2 V2-RING activator concept is first-in-class.** Compute hypothesis (Zn-distal binder → E3-ligase allosteric activator) is plausible but unproven. TR-FRET + ubiquitination-assay pair is MANDATORY to distinguish activator from inhibitor direction before any "activator" language externally.
6. **PERP binders are 70-90 aa mini-proteins, not small molecules.** Different failure modes, different cost structure. Gene-synthesis + E. coli expression + BLI is more expensive per-candidate (~700-1200 EUR) than small-molecule assay.
7. **Not a commitment.** This document is an engineering feasibility document, not a purchase order. Christian + Simon approval required before any CRO / reagent order.

---

*DRAFT. Do not distribute externally until triple_llm_verify 3/3 PASS and Christian Fischer human sign-off. This document is traceable to the frozen input files listed in the header; it is a new claim and a Claim #16-support element in CLAIMS_REGISTRY.md.*

# SMA Cross-Connection Insights — 2026-04-10

**Generated**: 2026-04-10T20:54:12.107486+00:00
**Engine**: `cross_connection_engine.py`
**Platform stats**: 80 targets, 21 drugs, 453 trials, 19454 claims

## What this is

Automated cross-campaign analysis that surfaces connections between findings, compounds, and hypotheses across our 9 SMA research campaigns. Goal: find publishable hypotheses that exist in our data but have never been explicitly stated.

---

## Query: pathway_coverage

**Question**: Which compounds have been tested against multiple nodes of the ROCK-LIMK2-CFL2 axis? Can we construct a combination therapy covering the full pathway?

**Tags**: pathway, combo, rock-limk-cfl2
**Hits**: 10

**Top results:**

1. [Learning] bbb5 SELECTIVITY PANEL FINAL RESULTS (2026-04-09, POCKET_FIXED runs): LIMK2 target 2.15A 1701 contacts BOUND. LIMK1 off-target 1.89A 1340 contacts BOUND (but weaker than LIMK2). ROCK1 off-target 1.95A
2. [Learning] SMA therapeutic axis: ROCK-LIMK2-CFL2 pathway. ROCK2 phosphorylates LIMK2, which phosphorylates cofilin-2 (CFL2), disrupting actin dynamics in motor neurons. Confirmed by 3 independent transcriptomic
3. [Learning] SMA therapeutic axis: ROCK-LIMK2-CFL2 pathway. ROCK2 phosphorylates LIMK2, which phosphorylates cofilin-2 (CFL2), disrupting actin dynamics in motor neurons. Confirmed by 3 independent transcriptomic
4. [Learning] NEGATIVE RESULT: Fasudil scaffold hopping for LIMK2 selectivity FAILED. 20 Fasudil variants (position 5,6,7,8 isoquinoline substitutions + amine head modifications) docked against LIMK2/LIMK1/ROCK1/RO
5. [Learning] SMA target LIMK2 — composite score 0.3868, 289 claims, protein  SMA target LIMK2 (LIM Domain Kinase 2), type=protein. Composite prioritization score: 0.3868 (rank top-20). Dimension scores: biological
6. [Learning] SMA target LIMK2 — composite score 0.3868, 289 claims, protein  SMA target LIMK2 (LIM Domain Kinase 2), type=protein. Composite prioritization score: 0.3868 (rank top-20). Dimension scores: biological
7. [Learning] FASUDIL VALIDATED as ROCK2 binder by 20ns holo MD. Stage 5 PASS. Closest CA=4.2Å. This works because PDB 2H9V has the ATP pocket near the protein center of mass, so CoM placement happened to be correc
8. [Learning] CORO1C retracted as driver. ROCK-LIMK2-CFL2 axis is THE target. CFL2 UP in SMA DOWN in ALS = disease biomarker. PFN2 is real MN gene. LIMK2=SMA, LIMK1=ALS.  Biology findings validated across 3 dataset
9. [Learning] SMA target LIMK1 — composite score 0.4012, 469 claims, gene  SMA target LIMK1 (LIM domain kinase 1), type=gene. Composite prioritization score: 0.4012 (rank top-20). Dimension scores: biological_coher
10. [Learning] SMA target LIMK1 — composite score 0.4012, 469 claims, gene  SMA target LIMK1 (LIM domain kinase 1), type=gene. Composite prioritization score: 0.4012 (rank top-20). Dimension scores: biological_coher

---

## Query: orphan_trajectories

**Question**: Which molecular dynamics trajectories exist in our data but have never been analyzed with MMPBSA, contact maps, or RMSD analysis?

**Tags**: md, orphan-data, analysis-gap
**Hits**: 10

**Top results:**

1. [Learning] MMPBSA contact proxy method: Uses MDAnalysis to count protein-ligand atomic contacts at 4 Angstrom and 6 Angstrom cutoffs across the last 25% of MD trajectory frames. Proxy binding free energy: delta_
2. [Learning] SCOPE OF APO MD BUG 2026-04-07: ALL 40 MD trajectories (73GB, 37 targets on GitHub) are APO protein-only. Zero contain a drug ligand. This affects every MD simulation ever run by the fleet manager. Th
3. [Learning] CRITICAL BUG 2026-04-07: ALL 100ns MD simulations (bbb_0, bbb_5, BMS-5, LIMKi3) were APO protein simulations — NO LIGAND in system. Root cause: fleet_manager.py generate_md_script uses fixer.removeHet
4. [Learning] bbb5 selectivity status (2026-04-08): NOT selective based on initial MD runs. HOWEVER, all selectivity runs used COM placement bug and are INVALID. Re-runs with POCKET_FIXED coordinates queued. Do NOT
5. [Learning] MMPBSA pipeline started 2026-04-07: 3 reference MDs complete (BMS-5 ref, LIMKi3 ref, bbb_0). All 100ns OpenMM Amber14 trajectories. RTX 3090 rented for MMPBSA + FlowDock install + Boltz-2 install. P2
6. [Learning] FUNDAMENTAL MD LESSON 2026-04-07: Protein-ligand MD simulation requires BOTH protein AND ligand in the system. OpenMM PDBFixer.removeHeterogens(True) strips ALL small molecules including the drug cand
7. [Learning] Cross-reference analysis v2: ZERO compounds have all 3 evidence layers. 8 DiffDock hits lack ADMET. 112 ADMET-passing compounds lack docking. 7318 GenMol molecules lack docking. Fasudil validates pipe
8. [Learning] Anthropic acquired Coefficient Bio for $400M (Apr 3 2026) — Lab-in-the-Loop concept is key for SMA drug discovery  Coefficient Bio (founded by Nathan Frey ex-Prescient Design/Genentech + Samuel Stanto
9. [Learning] CRITICAL FEEDBACK: Stop citing Bowerman 2012 as strong evidence for Fasudil in SMA. Simon reviewed it and it's WEAK: n=3-5, no blinding, non-monotonic dose-response, single lab, zero replication in 14
10. [Learning] POCKETXMOL BEST PRACTICES (2026-04-07): (1) SOTA: 11/14 metrics on PoseBusters benchmark, outperforms 55 baselines. (2) RTX 3090: batch_size 50 safe, reduce to 25 if OOM. (3) Pocket radius: 10Å for st

---

## Query: selectivity_determinants

**Question**: For our 14 LIMK2-selective compounds, what structural features distinguish them from non-selective molecules? What residues on LIMK2 do they contact that LIMK1 lacks?

**Tags**: selectivity, structure, pharmacophore
**Hits**: 10

**Top results:**

1. [Learning] PocketXMol DFG-out campaign LAUNCHED 2026-04-09. 300 molecules targeting LIMK2 DFG-out allosteric pocket (center -14.0, 8.5, 24.5, radius 12A, PDB 4TPT). DFG motif at residues 555-557 (Asp-Phe-Gly), 8
2. [Learning] genmol_119 original is NOT LIMK2-selective. DiffDock selectivity panel shows LIMK1, JAK2, and CDK2 score higher than LIMK2. Superseded by bbb5 (genmol_119_bbb_5) which fixes JAK2 cross-reactivity.
3. [Learning] SMA target LIMK2 — composite score 0.3868, 289 claims, protein  SMA target LIMK2 (LIM Domain Kinase 2), type=protein. Composite prioritization score: 0.3868 (rank top-20). Dimension scores: biological
4. [Learning] SMA target LIMK2 — composite score 0.3868, 289 claims, protein  SMA target LIMK2 (LIM Domain Kinase 2), type=protein. Composite prioritization score: 0.3868 (rank top-20). Dimension scores: biological
5. [Learning] bbb5 SELECTIVITY PANEL FINAL RESULTS (2026-04-09, POCKET_FIXED runs): LIMK2 target 2.15A 1701 contacts BOUND. LIMK1 off-target 1.89A 1340 contacts BOUND (but weaker than LIMK2). ROCK1 off-target 1.95A
6. [Learning] 7 LIMK2-SELECTIVE HITS found from PocketXMol DiffDock campaign (114/4346 docked so far). Best: 1387_0 margin +0.980 (fluoroquinazolinone), 1256_0 margin +0.740 (thiazole-pyrrole), 1219_0 margin +0.430
7. [Learning] NEGATIVE RESULT: Fasudil scaffold hopping for LIMK2 selectivity FAILED. 20 Fasudil variants (position 5,6,7,8 isoquinoline substitutions + amine head modifications) docked against LIMK2/LIMK1/ROCK1/RO
8. [Learning] SMA target LIMK1 — composite score 0.4012, 469 claims, gene  SMA target LIMK1 (LIM domain kinase 1), type=gene. Composite prioritization score: 0.4012 (rank top-20). Dimension scores: biological_coher
9. [Learning] SMA target LIMK1 — composite score 0.4012, 469 claims, gene  SMA target LIMK1 (LIM domain kinase 1), type=gene. Composite prioritization score: 0.4012 (rank top-20). Dimension scores: biological_coher
10. [Learning] LIMKi3 is a known LIMK inhibitor used as reference compound. DILI score 0.95 — hepatotoxic, NOT a drug candidate. Used only for MMPBSA baseline comparison against bbb5. Previous POCKET_FIXED run used

---

## Query: approved_drug_combos

**Question**: Which FDA-approved drugs could be repurposed and combined for SMA based on our computational screens? Are there synergies between approved compounds?

**Tags**: repurposing, combo, approved
**Hits**: 10

**Top results:**

1. [Learning] SMA Research Platform summary statistics — sources, targets, drugs, trials, claims, hypotheses counts  SMA Research Platform statistics as of 2026-04-08. The platform contains 5968 literature sources,
2. [Learning] SMA Research Platform summary statistics — sources, targets, drugs, trials, claims, hypotheses counts  SMA Research Platform statistics as of 2026-04-08. The platform contains 5968 literature sources,
3. [Learning] Feedback Arshad Cto Review  ## Arshad Farhad — CTO Review (2026-03-25)  Senior technical review of the SMA platform from Christian's CTO at Dell. Went deep: GitHub repo, methodology docs, live API, co
4. [Learning] NO company has SMA base editing clinical program. Beam Therapeutics holds IP license (WO2022150706A2) but focused on SCD/liver, not SMA. Prime, Editas, Verve — no SMA programs. ABE + Fasudil combinati
5. [Learning] SMA claim (drug_efficacy) — investigational drugs: Newly developed compounds are currently in clinical trials and may lead to feasi  SMA evidence claim (drug_efficacy): Newly developed compounds are c
6. [Learning] SMA claim (drug_efficacy) — investigational drugs: Newly developed compounds are currently in clinical trials and may lead to feasi  SMA evidence claim (drug_efficacy): Newly developed compounds are c
7. [Learning] Feedback Compute Layer Vision  We are NOT a lab. We are NOT doing synthesis or wet lab work ourselves.  **Our role:** The computational infrastructure layer that SMA researchers rely on. Every lab wor
8. [Learning] SMA CURE ACTION PLAN 2026 finalized. Three parallel tracks: Track A (ABE+Fasudil combination, 57K EUR, 8 months to manuscript), Track B (Universal Recovery Platform — partner with Novartis/Roche/Bioge
9. [Learning] SMA drug riluzole — small_molecule, approved, 1 trials  SMA drug riluzole (brand: none). Type: small_molecule. Status: approved. Mechanism: Glutamate antagonist. Positive in SMND7 mice (2008). Only va
10. [Learning] SMA drug riluzole — small_molecule, approved, 1 trials  SMA drug riluzole (brand: none). Type: small_molecule. Status: approved. Mechanism: Glutamate antagonist. Positive in SMND7 mice (2008). Only va

---

## Query: contradictions

**Question**: Are there any contradictions between our campaigns — findings that suggest opposite conclusions or compounds where one analysis says yes and another says no?

**Tags**: contradiction, qa
**Hits**: 10

**Top results:**

1. [Learning] Learnings Scientific Method  ## Scientific Method — Lessons Learned (March 2026)  ### 1. ALWAYS Validate Before Celebrating - **Fomepizole +1.027**: Looked sensational → MW-bias artifact (MW 82) - **5
2. [Learning] Feedback Critical Thinking  ## Critical Thinking Checklist — Run BEFORE Posting Any Finding  **Rule:** Everything that sounds good MUST be critically questioned before reporting.  **The Checklist:** 1
3. [Learning] Cross-reference analysis v2: ZERO compounds have all 3 evidence layers. 8 DiffDock hits lack ADMET. 112 ADMET-passing compounds lack docking. 7318 GenMol molecules lack docking. Fasudil validates pipe
4. [Learning] Feedback Claims Quality Gate  ## Claims Quality Problem (2026-03-31)  **User frustrated**: Claims show bare statements without evidence. Researchers need to validate but can't.  ### Specific Issues 1.
5. [Learning] SMA claim (drug_efficacy) — SMA: Two treatments have been approved for commercial use and have markedly changed t  SMA evidence claim (drug_efficacy): Two treatments have been approved for commercial
6. [Learning] SMA claim (drug_efficacy) — SMA: Two treatments have been approved for commercial use and have markedly changed t  SMA evidence claim (drug_efficacy): Two treatments have been approved for commercial
7. [Learning] Feedback Compute Layer Vision  We are NOT a lab. We are NOT doing synthesis or wet lab work ourselves.  **Our role:** The computational infrastructure layer that SMA researchers rely on. Every lab wor
8. [Learning] SMA claim (drug_efficacy) — investigational drugs: Newly developed compounds are currently in clinical trials and may lead to feasi  SMA evidence claim (drug_efficacy): Newly developed compounds are c
9. [Learning] SMA claim (drug_efficacy) — investigational drugs: Newly developed compounds are currently in clinical trials and may lead to feasi  SMA evidence claim (drug_efficacy): Newly developed compounds are c
10. [Learning] Feedback Paper Quality Calibration  ## Paper Quality Agent — Calibration (2026-04-01)  **Rule**: Basic neuroscience papers (electrophysiology, histology, imaging) should NOT be flagged for "no blindin

---

## Query: simon_ready

**Question**: Which findings are ready to hand to Simon for wet-lab validation, and which still need additional computational work to be considered complete?

**Tags**: simon, wet-lab, handoff
**Hits**: 10

**Top results:**

1. [Learning] Simon is a scientific collaborator (PhD, Leipzig University, Carl-Ludwig-Institute for Physiology). Key contact for SMA research validation and wet-lab experiments. Fasudil evidence package prepared f
2. [Learning] Feedback No Wet Lab Drafts  Don't draft wet lab experimental protocols, synthesis quotes, or grant applications for experimental work.  **Why:** The user explicitly said "we leave this to the research
3. [Learning] STRATEGY UPDATE: Do NOT present preliminary results to Simon. Build complete computational evidence package FIRST, including XE9680 results (AAV capsid designs, foundation model, OmniModel). Present S
4. [Learning] Best-in-class only: NEVER ship half-baked research to external collaborators  External deliverables (Simon, labs, grants, researchers) only when evidence package is complete and best-in-class. Credibi
5. [Learning] Feedback Compute Layer Vision  We are NOT a lab. We are NOT doing synthesis or wet lab work ourselves.  **Our role:** The computational infrastructure layer that SMA researchers rely on. Every lab wor
6. [Learning] Simon Priorities: 4/5 DONE. P0 Paper Quality Agent DONE, P1 Methodology Transparency DONE, P2 Claims News DONE, P3 OpenAlex DONE, P4 Fasudil 3D Viz NOT DONE. genmol_119_bbb_0 evidence package running
7. [Learning] Feedback Simon Meeting 2026 03 31  ## Meeting with Christian Simon — 2026-03-31  ### HIGHEST PRIORITY: Paper Quality / Expert Agent  Simon's core concern: **Wie gut sind die Papers die wir analysieren
8. [Learning] Feedback Validate Before Grants  Do NOT submit grant applications based purely on computational predictions. Before submitting Cure SMA or NCATS R21:  1. **Validate DiffDock predictions independently*
9. [Learning] PIPELINE v2.1 EXTERNAL VALIDATION (GPT-4o + Web 2026): Our pipeline is COMPETITIVE but has gaps vs industry leaders. 5 platform archetypes identified (ScienceDirect 2025 landscape review): (1) Generat
10. [Learning] Feedback Scientific Advisory  ## Core Message The platform has too many parallel directions. Must shift from "cool features" to "calibrated truth." A professor will ask about precision, reproducibilit

---

## Query: published_connections

**Question**: For each of our computational hits, what published SMA literature supports or contradicts the hypothesis? Which hits have zero literature backing (novel) vs strong backing (validated)?

**Tags**: literature, novelty
**Hits**: 10

**Top results:**

1. [Learning] SMA research mission: Cure SMA, not impress. Quality over quantity. Best-in-class or do not ship. Negative results published with same rigor as positive. Every number needs context. No AI theater — ca
2. [Learning] SMA Research Platform summary statistics — sources, targets, drugs, trials, claims, hypotheses counts  SMA Research Platform statistics as of 2026-04-08. The platform contains 5968 literature sources,
3. [Learning] SMA Research Platform summary statistics — sources, targets, drugs, trials, claims, hypotheses counts  SMA Research Platform statistics as of 2026-04-08. The platform contains 5968 literature sources,
4. [Learning] Feedback Compute Layer Vision  We are NOT a lab. We are NOT doing synthesis or wet lab work ourselves.  **Our role:** The computational infrastructure layer that SMA researchers rely on. Every lab wor
5. [Learning] Feedback Content Quality Gate  ## Content Quality Gate (2026-04-01)  **Problem**: "24-hour sprint: 8,000+ molecules" is meaningless for a researcher. No methodology, no specific results, no limitation
6. [Learning] Feedback Claims Quality Gate  ## Claims Quality Problem (2026-03-31)  **User frustrated**: Claims show bare statements without evidence. Researchers need to validate but can't.  ### Specific Issues 1.
7. [Learning] SMA Platform v2 Replatforming completed: Next.js 16.2.2 + TypeScript + Tailwind CSS 4. 45 routes built, all data from API (zero hardcoded). Key frontend best practices that MUST be applied: (1) Method
8. [Learning] Feedback Christian Simon  ## Researcher Feedback — Christian Simon, PhD (Leipzig University, Carl-Ludwig-Institute for Physiology)  **Date**: 2026-03-20 **Context**: First external researcher review o
9. [Learning] CRITICAL FEEDBACK: Stop citing Bowerman 2012 as strong evidence for Fasudil in SMA. Simon reviewed it and it's WEAK: n=3-5, no blinding, non-monotonic dose-response, single lab, zero replication in 14
10. [Learning] Feedback Researcher Value  Every section on the SMA platform must provide researcher-grade information. Raw numbers without context are useless.  **Why:** User said "ALL sections need to have valuable

---

## Query: cross_campaign_compounds

**Question**: Which compounds appear in multiple campaigns — either as primary candidates or as controls — and what did each campaign say about them?

**Tags**: cross-ref, compounds
**Hits**: 10

**Top results:**

1. [Learning] Learnings Scientific Method  ## Scientific Method — Lessons Learned (March 2026)  ### 1. ALWAYS Validate Before Celebrating - **Fomepizole +1.027**: Looked sensational → MW-bias artifact (MW 82) - **5
2. [Learning] genmol_119_bbb_5 confirmed as lead compound. LIMK2 +0.58 (4x better than bbb_0), JAK2 -0.80 (resolved), ROCK1 -0.70 (selective). ADMET v2 clean (composite 0.899, BBB HIGH, SAScore 3.31). MD 100ns runn
3. [Learning] Cross-reference analysis v2: ZERO compounds have all 3 evidence layers. 8 DiffDock hits lack ADMET. 112 ADMET-passing compounds lack docking. 7318 GenMol molecules lack docking. Fasudil validates pipe
4. [Learning] ADMET script bug: compound_smiles was a single string but code treated it as a list, iterating character by character. Result: computed ADMET on individual atoms (C, O, S) instead of the drug molecule
5. [Learning] SMA claim (drug_efficacy) — investigational drugs: Newly developed compounds are currently in clinical trials and may lead to feasi  SMA evidence claim (drug_efficacy): Newly developed compounds are c
6. [Learning] SMA claim (drug_efficacy) — investigational drugs: Newly developed compounds are currently in clinical trials and may lead to feasi  SMA evidence claim (drug_efficacy): Newly developed compounds are c
7. [Learning] Compound status audit: Fasudil=only validated. genmol_119_bbb_5=real lead (LIMK2 +0.58). bbb_0=FAKE. Original genmol_119=NOT selective. Riluzole=only DiffDock hit.  Deep data review 2026-04-06
8. [Learning] CRITICAL FINDING 2026-04-07: Batch ADMET-AI screening of ALL 256 platform compounds reveals 91% fail safety thresholds. Only 23/256 pass. DILI (liver toxicity) is the #1 killer at 84% — kinase inhibit
9. [Learning] 7 LIMK2-SELECTIVE HITS found from PocketXMol DiffDock campaign (114/4346 docked so far). Best: 1387_0 margin +0.980 (fluoroquinazolinone), 1256_0 margin +0.740 (thiazole-pyrrole), 1219_0 margin +0.430
10. [Learning] Fasudil scaffold hopping campaign COMPLETED 2026-04-09. Professional medicinal chemistry approach: 115 focused variants from Fasudil isoquinoline core, modifying position 7 (points at LIMK2/ROCK2 dive

---

## Orphan MD Trajectories (analysis gap)

The following MD trajectories exist but have no associated MMPBSA, contact map, or other analysis file. These represent **free science** — compute already paid for, insights not yet extracted.

| Trajectory | Parent | Size (MB) |
|---|---|---|
| trajectory.dcd | LIMK2_LIMKi3_holo | 218.9 |
| trajectory.dcd | LIMK2_LIMKi3_reference | 2558.1 |
| trajectory.dcd | ROCK1_bbb5_POCKET_FIXED | 418.1 |
| trajectory.dcd | SMN2_4AP_MMPBSA | 162.9 |
| trajectory.dcd | SMN2_vs_Kv12_4AP_selectivity | 1136.0 |
| trajectory.dcd | LIMK1_bbb5_POCKET_FIXED | 166.4 |
| trajectory.dcd | LIMK2_LIMKi3_POCKET_FIXED | 228.8 |
| trajectory.dcd | JAK2_bbb5_selectivity | 308.9 |
| trajectory.dcd | 4AP_Kv12_holo | 4252.7 |
| trajectory.dcd | LIMK2_bbb5_DOCKPOSE | 227.0 |
| trajectory.dcd | LIMK2_BMS5_reference | 2106.7 |
| trajectory.dcd | SMN2_Riluzole_holo | 999.1 |
| trajectory.dcd | LIMK2_bbb5_holo | 221.1 |
| trajectory.dcd | ROCK2_CHEMBL38735_active | 6217.5 |
| trajectory.dcd | LIMK1_bbb5_selectivity | 217.7 |
| trajectory.dcd | LIMK2_bbb5_POCKET_FIXED | 217.4 |
| trajectory.dcd | 4AP_SMN2_holo | 917.5 |
| trajectory.dcd | IDH1_Ivosidenib_holo | 2165.7 |
| trajectory.dcd | LIMK2_LIMKi3_POCKET_FIXED_v2 | 313.5 |
| trajectory.dcd | LIMK2_BMS5_holo | 218.9 |

---

## Suggested Next Steps

1. **Review top hit per query** — does it suggest a novel combination or experiment?
2. **Analyze orphan trajectories** — cheap wins, just run MMPBSA + contact maps locally.
3. **Update PROJECT_CATALOG.md** — add any new cross-references to the relevant campaign sections.
4. **Propose wet-lab experiments** — if a query surfaces a novel hypothesis, draft a protocol for Simon.

---

## License

CC-BY-4.0 — open analysis. Auto-generated by cross_connection_engine.py.
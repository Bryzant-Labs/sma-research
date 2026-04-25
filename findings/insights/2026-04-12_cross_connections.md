# SMA Cross-Connection Insights — 2026-04-12

**Generated**: 2026-04-12T04:00:05.582971+00:00
**Engine**: `cross_connection_engine.py`
**Platform stats**: 94 targets, 32 drugs, 453 trials, 19454 claims

## What this is

Automated cross-campaign analysis that surfaces connections between findings, compounds, and hypotheses across our 9 SMA research campaigns. Goal: find publishable hypotheses that exist in our data but have never been explicitly stated.

---

## Query: pathway_coverage

**Question**: Which compounds have been tested against multiple nodes of the ROCK-LIMK2-CFL2 axis? Can we construct a combination therapy covering the full pathway?

**Tags**: pathway, combo, rock-limk-cfl2
**Hits**: 10

**Top results:**

1. [Learning] SMA news — ROCK-LIMK2-CFL2 Pathway — Two Validated Compounds from Both Entry Points [score 142]  SMA news (announcement, score 142, 2026-04-08): ROCK-LIMK2-CFL2 Pathway — Two Validated Compounds from
2. [Learning] Cross-connection sweep 2026-04-10: 8 queries, 50 orphan trajectories  # SMA Cross-Connection Insights — 2026-04-10  **Generated**: 2026-04-10T20:54:12.107486+00:00 **Engine**: `cross_connection_engine
3. [Learning] Finding 2026-04-09: bbb5 Is a Dual LIMK2 / ROCK1 Inhibitor — NOT LIMK2-Selective  # bbb5 Is a Dual LIMK2 / ROCK1 Inhibitor — NOT LIMK2-Selective  **Date**: 2026-04-09 **Status**: COMPUTATIONAL VALIDAT
4. [Learning] bbb5 SELECTIVITY PANEL FINAL RESULTS (2026-04-09, POCKET_FIXED runs): LIMK2 target 2.15A 1701 contacts BOUND. LIMK1 off-target 1.89A 1340 contacts BOUND (but weaker than LIMK2). ROCK1 off-target 1.95A
5. [Learning] SMA therapeutic axis: ROCK-LIMK2-CFL2 pathway. ROCK2 phosphorylates LIMK2, which phosphorylates cofilin-2 (CFL2), disrupting actin dynamics in motor neurons. Confirmed by 3 independent transcriptomic
6. [Learning] SMA therapeutic axis: ROCK-LIMK2-CFL2 pathway. ROCK2 phosphorylates LIMK2, which phosphorylates cofilin-2 (CFL2), disrupting actin dynamics in motor neurons. Confirmed by 3 independent transcriptomic
7. [Learning] Finding 2026-04-10: NEGATIVE RESULT: Fasudil Scaffold Hopping for LIMK2 Selectivity  # NEGATIVE RESULT: Fasudil Scaffold Hopping for LIMK2 Selectivity  **Date**: 2026-04-09 **Status**: FAILED — No LIM
8. [Learning] SMA news — H-1152 Shows Unexpected LIMK2 Binding — Dual-Target Potential [score 105]  SMA news (discovery, score 105, 2026-03-24): H-1152 Shows Unexpected LIMK2 Binding — Dual-Target Potential. Tags:
9. [Learning] SMA news — ROCK Inhibitor Landscape — 13 Compounds Mapped for SMA Relevance [score 123]  SMA news (discovery, score 123, 2026-03-24): ROCK Inhibitor Landscape — 13 Compounds Mapped for SMA Relevance.
10. [Learning] SMA news — genmol_119 Selectivity Panel — NOT Selective for LIMK2 (Superseded by bbb_5) [score 115]  SMA news (drug_discovery, score 115, 2026-04-05): genmol_119 Selectivity Panel — NOT Selective for

---

## Query: orphan_trajectories

**Question**: Which molecular dynamics trajectories exist in our data but have never been analyzed with MMPBSA, contact maps, or RMSD analysis?

**Tags**: md, orphan-data, analysis-gap
**Hits**: 10

**Top results:**

1. [Learning] MMPBSA contact proxy method: Uses MDAnalysis to count protein-ligand atomic contacts at 4 Angstrom and 6 Angstrom cutoffs across the last 25% of MD trajectory frames. Proxy binding free energy: delta_
2. [Learning] SMA news — 50 Orphan MD Trajectories Analyzed — LIMK2 Pipeline Validated, 4-AP SMN2 Pocket Rediscovered, CFL2 Claim Retracted [score 173]  SMA news (discovery, score 173, 2026-04-11): 50 Orphan MD Tra
3. [Learning] MMPBSA BATCH V2 SUCCESS: All 4 valid binders produced physically sensible dG_bind values  Date: 2026-04-11 Pipeline: ~/gpu-fleet/scripts/mmpbsa_batch.py (patched v2) + mmpbsa_batch_v2_driver.py Result
4. [Learning] CRITICAL MD ANALYSIS BUG: AmberTools MMPBSA prmtop atom-order mismatch with OpenMM DCD  Date: 2026-04-11 Script: ~/gpu-fleet/scripts/mmpbsa_batch.py (Tier 2 AmberTools)  SYMPTOM: MMPBSA.py on known st
5. [Learning] SCOPE OF APO MD BUG 2026-04-07: ALL 40 MD trajectories (73GB, 37 targets on GitHub) are APO protein-only. Zero contain a drug ligand. This affects every MD simulation ever run by the fleet manager. Th
6. [Learning] CRITICAL BUG 2026-04-07: ALL 100ns MD simulations (bbb_0, bbb_5, BMS-5, LIMKi3) were APO protein simulations — NO LIGAND in system. Root cause: fleet_manager.py generate_md_script uses fixer.removeHet
7. [Learning] CRITICAL MD ANALYSIS BUG: PBC wrapping missing from distance_array calls in mmpbsa_batch.py  Date: 2026-04-11 Script: ~/gpu-fleet/scripts/mmpbsa_batch.py (Tier 1 contact-proxy)  SYMPTOM: Reported LIMK
8. [Learning] Cross-connection sweep 2026-04-10: 8 queries, 50 orphan trajectories  # SMA Cross-Connection Insights — 2026-04-10  **Generated**: 2026-04-10T20:54:12.107486+00:00 **Engine**: `cross_connection_engine
9. [Learning] ROCK2 apo 100 ns MD baseline — core pocket is rock-stable, RMSD is misleading  Analyzed 2026-04-12 via MDAnalysis. 100 ns apo-ROCK2 dimer (PDB 2F2U, amber14-all/TIP3P/0.15M NaCl, 23.5 ns/day on RTX 30
10. [Learning] SMA news — genmol_119_bbb_5 Stage 5 FAIL — Ligand Dissociates from LIMK2 in 20ns MD [score 116]  SMA news (announcement, score 116, 2026-04-07): genmol_119_bbb_5 Stage 5 FAIL — Ligand Dissociates from

---

## Query: selectivity_determinants

**Question**: For our 14 LIMK2-selective compounds, what structural features distinguish them from non-selective molecules? What residues on LIMK2 do they contact that LIMK1 lacks?

**Tags**: selectivity, structure, pharmacophore
**Hits**: 10

**Top results:**

1. [Learning] PocketXMol DFG-out campaign LAUNCHED 2026-04-09. 300 molecules targeting LIMK2 DFG-out allosteric pocket (center -14.0, 8.5, 24.5, radius 12A, PDB 4TPT). DFG motif at residues 555-557 (Asp-Phe-Gly), 8
2. [Learning] SMA news — Seven New LIMK2-Selective Hits from Overnight DiffDock Campaign (Total: 14) [score 132]  SMA news (gpu_result, score 132, 2026-04-10): Seven New LIMK2-Selective Hits from Overnight DiffDock
3. [Learning] SMA news — genmol_119 Selectivity Panel — NOT Selective for LIMK2 (Superseded by bbb_5) [score 115]  SMA news (drug_discovery, score 115, 2026-04-05): genmol_119 Selectivity Panel — NOT Selective for
4. [Learning] Finding 2026-04-10: Seven New LIMK2-Selective Hits from Overnight DiffDock Campaign (2026-04-09 → 04-10)  # Seven New LIMK2-Selective Hits from Overnight DiffDock Campaign (2026-04-09 → 04-10)  **Date
5. [Learning] genmol_119 original is NOT LIMK2-selective. DiffDock selectivity panel shows LIMK1, JAK2, and CDK2 score higher than LIMK2. Superseded by bbb5 (genmol_119_bbb_5) which fixes JAK2 cross-reactivity.
6. [Learning] Finding 2026-04-09: bbb5 Is a Dual LIMK2 / ROCK1 Inhibitor — NOT LIMK2-Selective  # bbb5 Is a Dual LIMK2 / ROCK1 Inhibitor — NOT LIMK2-Selective  **Date**: 2026-04-09 **Status**: COMPUTATIONAL VALIDAT
7. [Learning] SMA target LIMK2 — composite score 0.3868, 289 claims, protein  SMA target LIMK2 (LIM Domain Kinase 2), type=protein. Composite prioritization score: 0.3868 (rank top-20). Dimension scores: biological
8. [Learning] SMA target LIMK2 — composite score 0.3868, 289 claims, protein  SMA target LIMK2 (LIM Domain Kinase 2), type=protein. Composite prioritization score: 0.3868 (rank top-20). Dimension scores: biological
9. [Learning] SMA target LIMK2 — composite score 0.3868, 289 claims, protein  SMA target LIMK2 (LIM Domain Kinase 2), type=protein. Composite prioritization score: 0.3868 (rank top-20). Dimension scores: biological
10. [Learning] SMA target LIMK2 — composite score 0.3868, 289 claims, protein  SMA target LIMK2 (LIM Domain Kinase 2), type=protein. Composite prioritization score: 0.3868 (rank top-20). Dimension scores: biological

---

## Query: approved_drug_combos

**Question**: Which FDA-approved drugs could be repurposed and combined for SMA based on our computational screens? Are there synergies between approved compounds?

**Tags**: repurposing, combo, approved
**Hits**: 10

**Top results:**

1. [Learning] SMA Research Platform summary statistics — sources, targets, drugs, trials, claims, hypotheses counts  SMA Research Platform statistics as of 2026-04-08. The platform contains 5968 literature sources,
2. [Learning] SMA Research Platform summary statistics — sources, targets, drugs, trials, claims, hypotheses counts  SMA Research Platform statistics as of 2026-04-08. The platform contains 5968 literature sources,
3. [Learning] SMA Research Platform summary statistics — sources, targets, drugs, trials, claims, hypotheses counts  SMA Research Platform statistics as of 2026-04-08. The platform contains 5968 literature sources,
4. [Learning] SMA Research Platform summary statistics — sources, targets, drugs, trials, claims, hypotheses counts  SMA Research Platform statistics as of 2026-04-08. The platform contains 5968 literature sources,
5. [Learning] Feedback Arshad Cto Review  ## Arshad Farhad — CTO Review (2026-03-25)  Senior technical review of the SMA platform from Christian's CTO at Dell. Went deep: GitHub repo, methodology docs, live API, co
6. [Learning] NO company has SMA base editing clinical program. Beam Therapeutics holds IP license (WO2022150706A2) but focused on SCD/liver, not SMA. Prime, Editas, Verve — no SMA programs. ABE + Fasudil combinati
7. [Learning] SMA claim (drug_efficacy) — investigational drugs: Newly developed compounds are currently in clinical trials and may lead to feasi  SMA evidence claim (drug_efficacy): Newly developed compounds are c
8. [Learning] SMA claim (drug_efficacy) — investigational drugs: Newly developed compounds are currently in clinical trials and may lead to feasi  SMA evidence claim (drug_efficacy): Newly developed compounds are c
9. [Learning] SMA claim (drug_efficacy) — investigational drugs: Newly developed compounds are currently in clinical trials and may lead to feasi  SMA evidence claim (drug_efficacy): Newly developed compounds are c
10. [Learning] SMA claim (drug_efficacy) — investigational drugs: Newly developed compounds are currently in clinical trials and may lead to feasi  SMA evidence claim (drug_efficacy): Newly developed compounds are c

---

## Query: contradictions

**Question**: Are there any contradictions between our campaigns — findings that suggest opposite conclusions or compounds where one analysis says yes and another says no?

**Tags**: contradiction, qa
**Hits**: 10

**Top results:**

1. [Learning] Learnings Scientific Method  ## Scientific Method — Lessons Learned (March 2026)  ### 1. ALWAYS Validate Before Celebrating - **Fomepizole +1.027**: Looked sensational → MW-bias artifact (MW 82) - **5
2. [Learning] Cross-connection sweep 2026-04-10: 8 queries, 50 orphan trajectories  # SMA Cross-Connection Insights — 2026-04-10  **Generated**: 2026-04-10T20:54:12.107486+00:00 **Engine**: `cross_connection_engine
3. [Learning] Feedback Critical Thinking  ## Critical Thinking Checklist — Run BEFORE Posting Any Finding  **Rule:** Everything that sounds good MUST be critically questioned before reporting.  **The Checklist:** 1
4. [Learning] SMA news — SMA Congress 2026: NMJ axis is the #1 unmet need — launching an in-silico rescue campaign [score 122]  SMA news (announcement, score 122, 2026-04-12): SMA Congress 2026: NMJ axis is the #1
5. [Learning] Cross-reference analysis v2: ZERO compounds have all 3 evidence layers. 8 DiffDock hits lack ADMET. 112 ADMET-passing compounds lack docking. 7318 GenMol molecules lack docking. Fasudil validates pipe
6. [Learning] Feedback Claims Quality Gate  ## Claims Quality Problem (2026-03-31)  **User frustrated**: Claims show bare statements without evidence. Researchers need to validate but can't.  ### Specific Issues 1.
7. [Learning] SMA claim (drug_efficacy) — SMA: Two treatments have been approved for commercial use and have markedly changed t  SMA evidence claim (drug_efficacy): Two treatments have been approved for commercial
8. [Learning] SMA claim (drug_efficacy) — SMA: Two treatments have been approved for commercial use and have markedly changed t  SMA evidence claim (drug_efficacy): Two treatments have been approved for commercial
9. [Learning] SMA claim (drug_efficacy) — SMA: Two treatments have been approved for commercial use and have markedly changed t  SMA evidence claim (drug_efficacy): Two treatments have been approved for commercial
10. [Learning] SMA claim (drug_efficacy) — SMA: Two treatments have been approved for commercial use and have markedly changed t  SMA evidence claim (drug_efficacy): Two treatments have been approved for commercial

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
4. [Learning] SMA Research Platform summary statistics — sources, targets, drugs, trials, claims, hypotheses counts  SMA Research Platform statistics as of 2026-04-08. The platform contains 5968 literature sources,
5. [Learning] SMA Research Platform summary statistics — sources, targets, drugs, trials, claims, hypotheses counts  SMA Research Platform statistics as of 2026-04-08. The platform contains 5968 literature sources,
6. [Learning] Feedback Compute Layer Vision  We are NOT a lab. We are NOT doing synthesis or wet lab work ourselves.  **Our role:** The computational infrastructure layer that SMA researchers rely on. Every lab wor
7. [Learning] Feedback Content Quality Gate  ## Content Quality Gate (2026-04-01)  **Problem**: "24-hour sprint: 8,000+ molecules" is meaningless for a researcher. No methodology, no specific results, no limitation
8. [Learning] Feedback Claims Quality Gate  ## Claims Quality Problem (2026-03-31)  **User frustrated**: Claims show bare statements without evidence. Researchers need to validate but can't.  ### Specific Issues 1.
9. [Learning] SMA Platform v2 Replatforming completed: Next.js 16.2.2 + TypeScript + Tailwind CSS 4. 45 routes built, all data from API (zero hardcoded). Key frontend best practices that MUST be applied: (1) Method
10. [Learning] Feedback Christian Simon  ## Researcher Feedback — Christian Simon, PhD (Leipzig University, Carl-Ludwig-Institute for Physiology)  **Date**: 2026-03-20 **Context**: First external researcher review o

---

## Query: cross_campaign_compounds

**Question**: Which compounds appear in multiple campaigns — either as primary candidates or as controls — and what did each campaign say about them?

**Tags**: cross-ref, compounds
**Hits**: 10

**Top results:**

1. [Learning] Cross-connection sweep 2026-04-10: 8 queries, 50 orphan trajectories  # SMA Cross-Connection Insights — 2026-04-10  **Generated**: 2026-04-10T20:54:12.107486+00:00 **Engine**: `cross_connection_engine
2. [Learning] SMA Congress 2026 NMJ compute campaign dispatched — MuSK/LRP4/DOK7/AGRN/RAPSN DiffDock  Launched 2026-04-12 on Vast instance 34668099 (RTX 3090, $0.24/hr). Targets: MuSK intracellular kinase domain (P
3. [Learning] SMA Congress 2026 NRF2/KEAP1 compute campaign dispatched — omaveloxolone, bardoxolone, KI-696, ML-385 control  Launched 2026-04-12 on Vast instance 34668107 (RTX 3090, $0.15/hr). Target: KEAP1 Kelch d
4. [Learning] Learnings Scientific Method  ## Scientific Method — Lessons Learned (March 2026)  ### 1. ALWAYS Validate Before Celebrating - **Fomepizole +1.027**: Looked sensational → MW-bias artifact (MW 82) - **5
5. [Learning] genmol_119_bbb_5 confirmed as lead compound. LIMK2 +0.58 (4x better than bbb_0), JAK2 -0.80 (resolved), ROCK1 -0.70 (selective). ADMET v2 clean (composite 0.899, BBB HIGH, SAScore 3.31). MD 100ns runn
6. [Learning] Cross-reference analysis v2: ZERO compounds have all 3 evidence layers. 8 DiffDock hits lack ADMET. 112 ADMET-passing compounds lack docking. 7318 GenMol molecules lack docking. Fasudil validates pipe
7. [Learning] SMA Congress 2026 follow-up campaign ready — 17 targets + 13 drugs seeded, 4 pathway nodes added, 12 news posts live  2026-04-12 execution pass. Backend seed_congress_2026.py added 17 targets (MUSK, L
8. [Learning] ADMET script bug: compound_smiles was a single string but code treated it as a list, iterating character by character. Result: computed ADMET on individual atoms (C, O, S) instead of the drug molecule
9. [Learning] SMA Congress 2026: NRF2/KEAP1 redox axis is the most druggable missing target — bardoxolone/sulforaphane/DMF/CDDO-Me for repurposing  The congress treated metabolism and redox as a major under-explore
10. [Learning] Cross-connection v3 LLM synthesis 2026-04-10: 27 compounds  # Cross-Connection Insights v3 (LLM-synthesized) — 2026-04-10  **Generated**: 2026-04-10T21:15:31.954425+00:00 **Engine**: `cross_connection

---

## Orphan MD Trajectories (analysis gap)

The following MD trajectories exist but have no associated MMPBSA, contact map, or other analysis file. These represent **free science** — compute already paid for, insights not yet extracted.

| Trajectory | Parent | Size (MB) |
|---|---|---|
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
| trajectory.dcd | ROCK2_CHEMBL38735_active | 8127.5 |
| trajectory.dcd | LIMK1_bbb5_selectivity | 217.7 |
| trajectory.dcd | 4AP_SMN2_holo | 917.5 |
| trajectory.dcd | IDH1_Ivosidenib_holo | 2165.7 |
| trajectory.dcd | LIMK2_LIMKi3_POCKET_FIXED_v2 | 313.5 |
| trajectory.dcd | 4AP_Kv12_holo_proper | 1056.1 |
| trajectory.dcd | ROCK1_bbb5_selectivity | 699.8 |
| trajectory.dcd | LIMK2_BMS5_holo_proper | 218.3 |
| trajectory.dcd | LIMK2_bbb5_100ns_VALIDATED | 250.9 |

---

## Suggested Next Steps

1. **Review top hit per query** — does it suggest a novel combination or experiment?
2. **Analyze orphan trajectories** — cheap wins, just run MMPBSA + contact maps locally.
3. **Update PROJECT_CATALOG.md** — add any new cross-references to the relevant campaign sections.
4. **Propose wet-lab experiments** — if a query surfaces a novel hypothesis, draft a protocol for Simon.

---

## License

CC-BY-4.0 — open analysis. Auto-generated by cross_connection_engine.py.
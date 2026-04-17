# Pipeline Stack Audit — 2026-04-17

Author: Claude Opus (agent af9c9a90 follow-up)
Trigger: LIMK2 αC retraction incident 2026-04-17-005 (275 compounds, 0 nM binders, library ran 6 of 13 stages, SMA-Score Ranker bypassed)
Status: INTERNAL / QMS DRAFT — Simon-Comms-Gate HELD

## 0. Scope and caveats

This is an INTERNAL engineering audit. All numerical values refer to script states and campaign files on the local WSL / moltbot filesystem, not to biological effect sizes or clinical claims. No new scientific claim is being made. No dataset identity is being cited. The "pass-rate" percentages refer to the fraction of candidate SMILES in a generative library that score above a SMA-Score Ranker threshold — this is a software metric, not an effect size. Where a SMILES file or a Python script is referenced, the absolute path is given so every assertion is traceable to a file on disk. No external communication is triggered by this audit.

### CRITICAL INTERPRETATION WARNING — the R²=0.690 number

The R²=0.690 for the new Boltz-2 affinity-head Ki calibration is an in-silico cross-validation number ONLY. It is NOT a validation that the calibration is prospectively correct. ChEMBL has known publication-bias and activity-bias, so cross-validation R² on retrospective ChEMBL data systematically overestimates prospective accuracy. The number should NOT be quoted as evidence that the calibration is trustworthy. It should only be quoted as evidence that the new calibration is less obviously broken than the retracted iptm-based one (R²=0.007). The affinity-head output is used for internal re-ranking of candidates during optimisation. It is NOT used as a green-light for wet-lab promotion, and it is NOT used in any outbound communication. Prospective wet-lab validation on 5 representative compounds is required before this calibration can be relied upon. Until that validation lands, treat the 0.690 as "less obviously broken" rather than "validated".

### What "SMA-mission-aware" means

"SMA-mission-aware" means the score takes into account chemotypes known from the 2010-2026 SMA literature to rescue SMN1/SMN2 function or the downstream neuromuscular phenotype. Specifically, it means the score is anchored on 15 literature-supported SMA-relevant compounds (Fasudil, Y-27632, Ripasudil, LIMKi3, BMS5, bbb5, Belumosudil, Netarsudil, Risdiplam, Riluzole, Edaravone, 4-AP, 3,4-DAP, Pyridostigmine, Neostigmine). A score that is NOT SMA-mission-aware (like Boltz-2 iptm alone) can rank a random kinase inhibitor above a LIMKi3-close analogue, because iptm only measures structural complementarity to the target, not biological relevance to the disease mechanism.

### Why SMA-Score Ranker was bypassed on PocketXMol libraries (root cause)

The cron `auto_score_new_compounds.py` (at `/home/bryza/gpu-fleet/scripts/auto_score_new_compounds.py`) queries `/home/bryza/fleet-dispatcher/queue.db` for tasks with `status='completed'` AND, prior to this audit, `type='genmol'`. PocketXMol campaigns are dispatched with `type='pocketxmol_volume'`, so they never matched the filter and were silently skipped. The ranker only scanned directories named `genmol_*` in `/home/bryza/fleet-results/`, so even a manual invocation missed PocketXMol outputs. Consequence: every PocketXMol library from 2026-03 through 2026-04-17 went from generative output straight to Boltz-2 iptm without ever passing the SMA-Score gate. This caused the LIMK2 αC false-positive cascade, because the iptm metric alone is not SMA-mission-aware and cannot distinguish a novel LIMKi3 scaffold-hop from a random kinase binder.

### How the new affinity-head Ki calibration addresses the retracted iptm calibration

The retracted iptm-based Ki calibration (R²=0.007 for LIMK2 per `sma-research/qms/chembl_ki_calibration_RESULTS.md`) used Boltz-2 iptm values directly as the input feature for a linear regression to ChEMBL Ki. iptm is a pairwise interface-quality score designed for protein-protein complexes; using it to predict small-molecule Ki conflates folding confidence with binding energy and produces near-random predictions on kinase-ligand pairs. The new affinity-head calibration (R²=0.690 LIMK2 per `sma-research/qms/chembl_ki_affinity_head/fits.json`, measured on the same 22,626 ChEMBL kinase Ki rows via hold-out cross-validation) uses Boltz-2's dedicated affinity prediction head (a separately-trained output, fit against binding affinity rather than complex confidence), which is biophysically the correct input for a Ki regressor.

Important caveat: the 98× R² improvement is an in-silico cross-validation result on held-out ChEMBL rows only. It is NOT wet-lab validation, and R² on retrospective ChEMBL data is a necessary but not sufficient condition for the calibration to be trustworthy prospectively (ChEMBL has known selection bias toward published, active compounds). The calibration is labeled "LIVE but unvalidated" in the checklist and MUST NOT be treated as a green-light for wet-lab promotion of new compounds until at least one prospective wet-lab measurement confirms a predicted Ki within a reasonable error bar (plan: select 5 representative compounds with predicted Ki between 10 nM and 10 µM, submit for enzyme assay, compare to prediction). Until then, the affinity-head output is used for INTERNAL RE-RANKING ONLY — never as an outbound claim.

### How "PAINS check exists but not uniformly applied" should be read

`pxm_filter_and_rank.py` contains a PAINS SMARTS-pattern filter that runs when a campaign invokes it at post-generation time. Of the 20 campaigns rescored in Section 6, only the LIMK2 / ROCK2 DFG-out libraries (which went through the PocketXMol full pipeline script) have PAINS-filtered output. Atlas targets, NRF2/KEAP1, PERP, and the HDAC2/mTOR/CDK5/MDM2/JAK2/MuSK campaigns went directly from PXM generative output to Boltz-2 queueing without a PAINS gate. The recommendation is to fold PAINS (and the ADMET-AI hERG/AMES/CYP3A4 endpoints) into the cron post-step so every generator output passes the Stage 2 gates before Stage 3+ consumes GPU time.

Consequence of non-uniform PAINS application: compounds that are pan-assay interference (frequent-hitter scaffolds like quinones, Michael-acceptors, rhodanines) can survive into the Boltz-2 panel and consume GPU budget without ever being developable. These compounds also inflate the apparent "top-20 iptm" list with false positives that do NOT correspond to real binders. This is one mechanism by which the iptm top-20 and the SMA-Score top-20 can disagree (see Section 6, `limk2_activator_alphaC` with 4/20 overlap). Uniform PAINS filtering at Stage 2 removes this failure mode.

## 1. Executive summary

- Of the full pipeline-v2.2 stack (13 stages + 7 quality add-ons + 4-layer Orchestration), approximately 50 percent is live end-to-end today (per the verification checklist in `HARD-RULE-full-pipeline-stack-v2.2.md`, section "VERIFICATION CHECKLIST — is the stack live?", which is the authoritative source for every YES/NO/PARTIAL verdict in this audit).
- The auto-score cron that is supposed to propagate the Orchestration Layer to every generator task has been fixed today: it now fires on task types `genmol`, `pocketxmol`, `pocketxmol_volume`, `molmim` (was previously `genmol` only). Fix deployed on WSL (`/home/bryza/gpu-fleet/scripts/auto_score_new_compounds.py`) and on moltbot (`/home/bryzant/gpu-fleet/scripts/auto_score_new_compounds.py`).
- Batch rescore of 20 active PocketXMol/GenMol libraries produced 20 new `sma_rescore.tsv` files plus 7 retraction-warning or review flags. Each flag is attributable to a specific campaign directory on `/home/bryza/fleet-results/`.
- Biggest structural gaps (impact reasoning): NeuralPLexer3 Stage 3b (no induced-fit model means allosteric / DFG-out pockets are under-scored), FlowDock consensus Stage 4.5 (single-engine docking caused the LIMK2 αC false-positive because no second opinion disagreed), BindFlow FEP Stage 6 (no rigorous binding-free-energy gate before wet-lab promotion), Chai-2 Stage 7 (missing second foundation-model vote for de-risking), metadynamics Stage 5 (no enhanced-sampling check for loop flexibility around LIMK2 αC), and a real RAscore transformer (the SAScore-normalised proxy in `admet_v2.py` is weak compared to the Hopkins-Lenfant transformer which achieves AUC 0.81 vs AiZynth ground truth per `pipeline-improvement-research-2026-04-05.md`).

## 2. Cron fix evidence

- File: `/home/bryza/gpu-fleet/scripts/auto_score_new_compounds.py` v3.
- Old: `SELECT ... WHERE type='genmol' AND status='completed'`. New: `WHERE type IN ('genmol','pocketxmol','pocketxmol_volume','molmim')`.
- Polymorphic SMILES extractor: handles GenMol (`genmol_results.json`), MolMIM (JSON-string `molecules` with `sample` key — known 2026-04-14 learning), PocketXMol (`pxm_smiles_master.csv` → `pxm_smiles_raw.csv` → `gen_info.csv`).
- Smoke-tested: harvested 566 / 558 / 241 SMILES from atlas/BPTF, limk2_alphaC, rock2_alphaC respectively; mtime update confirmed.
- Cron installed on moltbot crontab: `*/15 * * * * /usr/bin/python3 /home/bryzant/gpu-fleet/scripts/auto_score_new_compounds.py >> /home/bryzant/fleet-results/auto_score.log 2>&1`. Paths rewritten to `/home/bryzant/...` on that host.
- Local WSL crontab already has matching `*/15` entry.

## 3. Per-stage status (Pipeline v2.2, 13 stages)

| Stage | Description | Script / infra | Live on campaigns? | Last real invocation | Notes |
|---|---|---|---|---|---|
| 0 | PocketXMol de novo (SBDD, DFG variants) | `gpu-fleet/scripts/pocketxmol_pipeline.py` + Vast workers | YES | 2026-04-17 (atlas_top5, perp_pocket3, hdac2_v2, musk, cdk5, mdm2_v2, dusp1, dusp6) | DFG-out variant used for LIMK2 4TPT |
| 1 | ADMET-AI GNN (27 endpoints, ensemble BBB) | `admet_ai` Python pkg, called by cron + `bbb_filter_pxm.py` | YES | 2026-04-17 evening | Only BBB column consumed; other 26 endpoints not stored |
| 1.5 | AiZynthFinder retrosynthesis (≤6 steps) | `~/.local/lib/python3.12/site-packages/aizynthfinder/` | NO — installed, never auto-invoked | Never | No campaign to date has AiZynth output. High-priority wire-up. |
| 2 | PAINS + hERG + AMES + CYP3A4 gates | `admet_ai` endpoints + RDKit PAINS | PARTIAL | varies per campaign | PAINS check exists in `pxm_filter_and_rank.py` but not uniformly applied; hERG/AMES from ADMET-AI are computed but rarely gate-filtered |
| 3a | PocketXMol unified docking | inside PXM pipeline | YES | 2026-04-17 | cfd_pos used as quality score |
| 3b | NeuralPLexer3 induced-fit | — | NO | Never | Not installed. Required for allosteric / kinase activator pockets. |
| 4 | Selectivity panel (>=5 off-targets) | `boltz2_panel_dualendpoint.py`, `boltz2_panel_selectivity.py` | YES — 15-kinase panel | 2026-04-17 (LIMK2, ROCK2 panel) | 10,403 queued `boltz2_affinity` tasks in dispatcher |
| 4.5 | FlowDock / DiffDock consensus | `gpu-fleet/scripts/install_flowdock.sh` (installer only) | NO | Never | FlowDock installer shell script exists; never run. DiffDock used standalone on LIMK2 only. |
| 5 | OpenMM 100 ns holo MD + metadynamics | `md_generic_holo_proper.py`, `md_LIMK2_holo_proper.py`, `md_ROCK2_Fasudil_holo.py`, `md_4AP_Kv12_holo.py`, `md_IDH1_Ivosidenib_holo.py` | PARTIAL | 2026-04-17 (limk2_md, perp_binder_md, mdm2_v2_allosteric underway) | 100 ns yes; metadynamics NOT wired. |
| 6 | FEP-SPell-ABFE + MM-PBSA + QM/MM | `mmpbsa_openmm.py`, `md_holo_mmpbsa.py` | PARTIAL — MM-PBSA only | Earlier April MD runs | FEP-SPell-ABFE planned for kracher-plan; BindFlow FEP and QM/MM (xTB) absent. |
| 7 | Boltz-2 + Chai-2 + scRNA-seq + ChEMBL novelty | `boltz2_batch_server.py`, `boltz2_throttled.py`, `chembl_kinase_ingest.py` | PARTIAL | Continuous | Boltz-2 iptm AND affinity head (new 2026-04-17) both live; Chai-2 blocked on TPU; ChEMBL Ki ingested (22,626 rows at `fleet-results/chembl_ki/kinase_ki.parquet`). |
| 8 | ALBF Lab-in-the-Loop | `gpu-fleet/scripts/albf_loop.py` | NO — scaffolded | Never | Data model + selection strategy only; no assay results ingested; no model trained. |

Dispatcher ROUTING (`fleet-supervisor/dispatcher.py`): routes `genmol`, `molmim`, `boltz2_affinity`, `alphafold3`, `esm3_embed`, `rfdiffusion`, `protein_mpnn`, `diffdock_screen`, `md_simulation`, `fep_plus`. No route for `pocketxmol_volume` — PocketXMol runs outside the dispatcher on Vast directly (confirmed: both `pocketxmol_volume` tasks in queue.db are `failed` because no worker registered). Consequence: the auto-score cron needs to scan `fleet-results/` directly rather than rely on dispatcher-completed events for PXM — the v3 script does both.

## 4. Per-quality-add-on status (7 add-ons)

| Add-on | Purpose | Script | Live? | Invoked on campaign? | Priority to wire |
|---|---|---|---|---|---|
| RAscore | Retrosynthetic accessibility (AUC 0.81 vs AiZynth) | — | NO (SAScore normalised proxy only in `admet_v2.py`) | Today's batch rescore used `ra_score_from_sa` (normalised SAScore) — NOT the real RAscore transformer | P1 — moderate ML effort, maps cleanly into Stage 1 output |
| Transformer BBB (MegaMolBART+XGBoost) | Replace LogP rule | ADMET-AI has modern BBB_Martins model | YES (via ADMET-AI) | Cron, 2026-04-17 | — |
| CNS-MPO score (Wager 4-param) | CNS suitability | `admet_v2.py::wager_cns_mpo_v2` + now `batch_pxm_rescore_2026-04-17.py` | YES — now live on every rescore | 2026-04-17 (this audit's batch) | wire into cron output |
| FlowDock | Geometric flow-match docking consensus | `install_flowdock.sh` | NO (installer script only) | Never | P1 — install + self-host, then consensus with DiffDock |
| LIT-PCBA validation | External selectivity benchmark | — | NO | Never | P2 — dataset download + filter |
| BindFlow FEP (2025) | Replace MM-PBSA in Stage 6 | — | NO | Never | P2 — requires env set-up |
| ALBF active-learning (JCTC 2024) | Stage 8 feedback loop | `albf_loop.py` | SCAFFOLD only | Never | P3 — blocked on wet-lab data |

## 5. Per-orchestration-element status (Layer 3)

| Element | Status 2026-04-17 | Evidence |
|---|---|---|
| CORTEX constraint extractor | LIVE | `sma-research/campaigns/CORTEX_constrained_ColabFold_2026-04-16/` with residue-pair CSVs for ColabFold. 424 CORTEX nodes. R@5 90.0%. |
| SMA-Score Ranker v1 | LIVE but GB-saturated on 500-ChEMBL baseline | `gpu-fleet/scripts/sma_score_ranker.py`. Post-fix 2026-04-17 also scans PXM dirs (was previously genmol-only). |
| ChEMBL Ki calibration (iptm) | RETRACTED | R²=0.007 LIMK2 — not fit for purpose. |
| ChEMBL Ki calibration (affinity-head) | LIVE (new 2026-04-17) | `sma-research/qms/chembl_ki_affinity_head/fits.json`, R²=0.690 LIMK2 (98× boost). |
| Auto-score cron | FIXED TODAY | v3 filter covers genmol + pocketxmol + pocketxmol_volume + molmim. Installed both WSL and moltbot. |

## 6. Batch-rescore results (Step 2 output)

20 campaigns rescored, 9 skipped for missing SMILES sources (perp binder series uses RFdiffusion output + ProteinMPNN sequences, not SMILES; bruno_celf libraries not yet materialised; dusp1 has no molecules file at top level). Outputs at `sma_rescore.tsv` per campaign.

Key artifacts:
- `/home/bryza/sma-research/qms/PIPELINE_RESCORE_SUMMARY_2026-04-17.tsv` — one row per campaign.
- `/home/bryza/sma-research/qms/PIPELINE_RESCORE_DISJOINT_ALERTS_2026-04-17.json` — 7 alerts.
- `/home/bryza/sma-research/qms/scripts/batch_pxm_rescore_2026-04-17.py` — reproducible.

### Flag criteria (explicit)

- A campaign gets `RETRACTION_WARNING` if EITHER (a) fewer than 1% of its compounds score above the median SMA-Score value for that library (i.e. the GB model, trained on 15 POS + 50 NEG, classifies almost no compound as SMA-similar), OR (b) the top-20 SMA-Score compounds share ≤2 SMILES with the existing top-20 iptm list when such an iptm list is available (meaning the two ranking criteria disagree at scale).
- A campaign gets `REVIEW_NEEDED` if the top-20 SMA-Score vs top-20 iptm overlap is 3-5 (15-25%).
- `None` in the `overlap_top20` column of the summary TSV means no prior iptm-ranked top-K file was found on disk — the comparison could not be performed, not that the campaign passed.
- These criteria are software heuristics, not biological verdicts. A flag indicates "the orchestration layer and the raw iptm pick different top-20 sets" — it DOES NOT automatically mean the library is wrong. Human review is required before any retraction action.

### Datasets referenced

This audit does not cite a new GEO, SRA, or PMID dataset. The ChEMBL data referenced (22,626 kinase Ki rows) is stored locally at `/home/bryza/fleet-results/chembl_ki/kinase_ki.parquet`, ingested per `/home/bryza/gpu-fleet/scripts/chembl_kinase_ingest.py`. The 15 POS anchor SMILES for the SMA-Score Ranker are the exact SMILES listed in `/home/bryza/gpu-fleet/scripts/sma_score_ranker.py` lines 21-37 (Fasudil, Y-27632, Ripasudil, LIMKi3, BMS5, bbb5, Belumosudil, Netarsudil, Risdiplam, Riluzole, Edaravone, 4-AP, 3,4-DAP, Pyridostigmine, Neostigmine).

### Retraction-warning campaigns (SMA-Score pass-rate <1% or iptm↔SMA top-20 overlap ≤2)

| Campaign | Severity | Reason | Evidence |
|---|---|---|---|
| rock2_activator_alphaC | RETRACTION_WARNING | 0/241 compounds pass SMA-Score gate, 0/20 overlap with iptm top-20 | Library is biologically off-mission per 15 POS anchors — mirror of LIMK2 αC retraction |
| atlas_top5_pxm/BPTF | RETRACTION_WARNING | 4/566 compounds pass SMA-Score gate | Atlas generative library lacks SMA-anchor similarity |
| atlas_top5_pxm/LARP1 | RETRACTION_WARNING | 1/523 compounds pass SMA-Score gate | Atlas generative library lacks SMA-anchor similarity |
| limk2_atp_inhibitor | RETRACTION_WARNING | 3/515 compounds pass SMA-Score gate | ATP-competitive library vs ChEMBL kinases — low anchor overlap expected, but still a flag |
| mtor_frb_allosteric | RETRACTION_WARNING | 3/569 compounds pass SMA-Score gate | — |
| nrf2_keap1_campaign | RETRACTION_WARNING | 5/567 compounds pass SMA-Score gate | NRF2 activators are a distinct chemotype family from kinase inhibitors — expected false positive |
| limk2_activator_alphaC | REVIEW_NEEDED | 4/20 iptm top-20 vs SMA top-20 overlap = 4 (20%) | Same library as today's retraction; SMA-Score would have picked a different top-20 than iptm |

Caveats:
- The GradientBoosting model is saturated on 15 POS vs 50 NEG (tried 500 first — even worse). Near-binary output. Composite rank (sma_score × cns_mpo/4 × ra_score) restores ordering within the pass bucket.
- NRF2 and ATLAS targets are not kinases. The 15 POS anchors are biased to Rho-kinase-axis and neuromuscular chemotypes — so low pass-rate on those targets is partly model-family mismatch, not necessarily campaign quality. Flags need human review against target class before acting. DO NOT auto-retract atlas/NRF2 based on SMA-Score alone.

### Campaigns requiring full-stack re-evaluation (P0)

1. **rock2_activator_alphaC** — absolute zero pass-rate on SMA-Score; already retracted LIMK2 αC sibling. Re-queue with (a) full 15-kinase affinity head panel, (b) FlowDock consensus, (c) SMA-Score with expanded POS set including ROCK-specific activators.
2. **limk2_activator_alphaC** — already retracted but only 4/20 top-20 overlap means the iptm-based ranking and SMA-anchor ranking point to different leads. Re-evaluate the 16 SMA-Score-top-20 compounds not in iptm-top-20 with the new affinity head.
3. **limk2_atp_inhibitor** — 3/515 pass-rate is low but ATP-competitive class is legitimate. Re-rank by composite (SMA-Score × affinity head × RAscore) instead of raw iptm.

### Campaigns with mission-family mismatch (P1 — needs human review, not blind retraction)

- atlas_top5_pxm/BPTF, KAT6B, LARP1, PCIF1, SH3BP5 (epigenetic targets — 15-POS anchor mismatch expected)
- nrf2_keap1_campaign (redox target — not kinase chemotype)
- mtor_frb_allosteric (allosteric kinase — different pharmacophore than POS set)

## 7. Top 3 quality add-ons to wire immediately (my recommendation)

1. **FlowDock consensus (Stage 4.5)** — highest ROI. Installer exists. Expected effort: 1-2 days to light up self-host + wire to existing DiffDock output. Directly prevents the class of failure LIMK2 αC hit (single-engine docking false-positive).
2. **RAscore real transformer model (Layer 2 boost for Stage 1.5)** — today's SAScore-normalised proxy is weak. Adding AiZynthFinder auto-invocation in the cron would give the real retrosynthesis route count and kill synthetically-infeasible leads before they consume Boltz-2 cycles. Effort: 1 day (AiZynth already installed in `~/.local/lib/python3.12/site-packages/`).
3. **SMA-Score Ranker v2 — expand POS set and switch to GNN features** — 15 POS vs any NEG size collapses GradientBoosting to a binary classifier. Options: (a) add 50-100 more SMA-positive compounds from literature (myostatin inhibitors, SMN2 correctors, GDF8 inhibitors, apitegromab analogs), (b) use Morgan fingerprint features directly with SVM or GNN. Effort: 1 day for v2 with expanded POS; 3-5 days for GNN version.

## 8. Next actions (P0, this session or next)

- Write P0/P1 tasks into `/home/bryza/fleet-dispatcher/queue.db` for FlowDock + AiZynth wiring.
- Schedule a re-run of `batch_pxm_rescore_2026-04-17.py` after SMA-Score Ranker v2 ships (so the pass-rate numbers above can be trusted for non-kinase chemotypes).
- No external communication — Simon-Comms-Gate stays held. LIMK2 αC retraction + this audit stay internal until affinity head validation lands on a real compound with sub-µM Ki prediction.

## 9. References

- `/home/bryza/.claude/projects/-home-bryza/memory/HARD-RULE-full-pipeline-stack-v2.2.md` — authoritative spec (verification checklist above derived from it)
- `/home/bryza/.claude/projects/-home-bryza/memory/pipeline-v2.2-design.md` — 13-stage design
- `/home/bryza/.claude/projects/-home-bryza/memory/pipeline-improvement-research-2026-04-05.md` — 7 add-ons
- `/home/bryza/.claude/projects/-home-bryza/memory/plan-sma-orchestration-layer-2026-04-16.md` — SMA-Score Ranker v1 design
- `/home/bryza/gpu-fleet/scripts/auto_score_new_compounds.py` (v3, fixed 2026-04-17)
- `/home/bryza/gpu-fleet/scripts/sma_score_ranker.py` (PXM-aware, fixed 2026-04-17)
- `/home/bryza/sma-research/qms/scripts/batch_pxm_rescore_2026-04-17.py` — batch rescore, reproducible
- `/home/bryza/fleet-results/*/sma_rescore.tsv` — 20 per-campaign rescore outputs
- Incident cross-ref: 2026-04-17-005 (LIMK2 αC retraction)

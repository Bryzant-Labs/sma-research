# Bruno / CELF1 / CELF2 Translation-Defect Axis — Campaign Plan

**Status**: DRAFT — Simon-Comms-Gate HELD. Triple-LLM gate REQUIRED before any promotion past DRAFT.
**Date**: 2026-04-17 (evening checkpoint)
**Campaign ID**: `bruno_celf_2026-04-17`
**Author**: Opus (fleet orchestrator)
**Scientific rationale**: Budapest SMA Congress 2026 priority — *"Bruno translation defects orthogonal to splicing — under-modelled."* (`sma-congress-2026-priorities.md`). Zero SMA drug-discovery groups targeting CELF1/CELF2 directly (as of 2026-04-17 literature survey).

## Hypothesis
CELF1 and CELF2 are RNA-binding proteins (RBPs) that govern alternative splicing AND cytoplasmic translation localization in motor neurons. SMA is canonically a splicing disease (SMN2 exon 7 skipping). The Bruno/CELF family controls an **orthogonal regulatory layer**: mRNA localization + translation efficiency at the NMJ. Fallini 2014 (PMID 24934431) showed SMN loss disrupts β-actin mRNA axonal translation — a Bruno/CELF-type mechanism.

**If** selective small-molecule inhibitors or modulators of CELF1/CELF2 RNA-binding can be designed that are orthogonal to MBNL1 and to the HuR/MSI1 paralogs, **then** they become lead candidates for:
1. Restoring axonal mRNA translation at the NMJ in SMA MN.
2. Complementing (not replacing) risdiplam/nusinersen splicing correction.
3. Potentially generalizing to myotonic dystrophy (CELF1 gain-of-function) and Bruno-class translation defects in other neuromuscular disorders.

## Honest failure-mode disclosure
This is a **high-risk / novel** campaign. Risks to name up front:
- **RBP druggability is historically poor**. Reported IC50s for CELF1/CELF2/MBNL1 modulators are typically 5–50 µM (weak). A sub-µM hit is not expected from a 24h compute campaign.
- **Selectivity across the RRM family is hard**. CELF1 RRM1/2, CELF2 RRM1/2, MSI1, ELAVL1 (HuR) share fold topology (β1-α1-β2-β3-α2-β4). Margin of ≥0.1 Boltz-2 iptm over paralogs = already notable.
- **In-silico RNA competition** is a proxy; only a wet-lab fluorescence-polarization (FP) assay against fluorescently-labeled UG-repeat RNA can confirm.
- **CELF1 3NMR ligand** is RNA, not a drug-like fragment. There is no validated small-molecule binding-site definition — we are treating the RNA-binding face as a "druggable pocket" by analogy.
- **Phase-5 AutoDock Vina + RNA competition** is a cartoon of the real thermodynamics. It will produce a rank; it will not produce Kd.

## Phase 1 — Target structures (TITLE-verified 2026-04-17)

All PDBs below have been queried against RCSB `data-api` (`/rest/v1/core/entry/{id}`). Titles match the expected RBP. The original plan (in the kickoff prompt) cited **4 incorrect PDBs** that TITLE-verify rejected — see `pdb_verify/TITLE_VERIFY.txt` for the rejected IDs (4D7R / 5F3B / 5F3T / 3D2S-ZF1ZF2). Corrected inventory below is **authoritative**:

| # | Target | Domain | PDB | Method | Resolution | Residues | RCSB title (verified) | UniProt |
|---|---|---|---|---|---|---|---|---|
| 1 | CELF1 (CUGBP1) | RRM1 + RRM2 + RNA | **3NMR** | X-ray | 1.85 Å | 14–187 | "Crystal Structure of CUGBP1 RRM1/2-RNA Complex" | Q92879 |
| 2 | CELF1 (CUGBP1) | RRM1 + RRM2 (NMR) | **2DHS** | NMR | — | 1–187 | "Solution Structure of Nucleic Acid Binding Protein CUGBP1ab" | Q92879 |
| 3 | CELF1 (CUGBP1) | RRM1+2, apo form | **3NNA** | X-ray | 1.90 Å | 14–187 | "Crystal Structure of CUGBP1 RRM1/2-RNA Complex" (alt conform.) | Q92879 |
| 4 | CELF2 (ETR-3 / BRUNOL3) | RRM1 + RRM2 | **4LMZ** | X-ray | 2.78 Å | 36–211 | "Structural insight into RNA recognition by RRM1+2 domain of human ETR-3 protein" | O95319 |
| 5 | CELF2 (ETR-3) | RRM1+2 (higher-res, DNA) | **9URH** | X-ray | 1.82 Å | 36–211 | "Structural insight into DNA recognition by RRM1+2 domain of human ETR-3 protein" | O95319 |
| 6 | CELF2 | RRM3 C-terminal | **4LJM** | X-ray | 3.0 Å | 416–508 | "Crystal structure of C-terminal RNA recognition motif of human ETR3" | O95319 |
| 7 | MBNL1 | ZF1+ZF2 | **3D2N** | X-ray | 2.7 Å | 9–90 | "Crystal structure of MBNL1 tandem zinc finger 1 and 2 domain" | Q9NR56 |
| 8 | MBNL1 | ZF3+ZF4 + CGCUGU RNA | **3D2S** | X-ray | 1.7 Å | 178–246 | "Crystal structure of MBNL1 tandem zinc finger 3 and 4 domain in complex with CGCUGU RNA" | Q9NR56 |
| 9 | MSI1 (selectivity anti-target) | RRM1/2 (AF-assigned) | UniProt **O43347** | — | AF | 20–189 | — | O43347 |
| 10 | ELAVL1 / HuR (selectivity anti-target) | RRM1/2 (AF-assigned) | UniProt **Q15717** | — | AF | 18–181 | — | Q15717 |

For Boltz-2 PPI/affinity co-fold we use the **sequence slice** (not the PDB coordinates — Boltz-2 folds the slice de novo, so it is identity-checked via UniProt FASTA download, written to `seeds/target_slices_rrm.json`).

## Phase 2 — Library generation (SUBMITTED 2026-04-17 evening)

### What was enqueued (live in `/home/bryzant/fleet-dispatcher/queue.db`)

1. **MolMIM scaffold expansion (hosted NIM, `molmim` task type)** — 5 tasks × 160 molecules each = **800 candidate molecules**, biased toward:
   - `celf_risd_core` (risdiplam RNA-binding core — UG-rich-RNA precedent in SMA)
   - `celf_branap_core` (branaplam core — proven SMA-RNA-binding chemotype)
   - `celf_berglund` (Berglund-lab MBNL1-reactive amide, literature-guided)
   - `celf_furamidine` (DB75 CUG-binder class; diamidine motif)
   - `celf_mitox_scaffold` (mitoxantrone-class intercalator)
   Algorithm: CMA-ES, QED-property, min_similarity=0.3, iterations=10.

2. **Boltz-2 affinity selectivity panel (hosted NIM, `boltz2_affinity` task type)** — 5 tasks × 12 pairs each = **60 co-folds** spanning the 5-RBP panel (CELF1_RRM12, CELF2_RRM12, MBNL1_ZF34, MSI1_RRM12, ELAVL1_RRM12) × 12 literature-grounded seed compounds (pentamidine, furamidine DB75, Hoechst 33258, neomycin B, actinomycin D core, risdiplam core, branaplam core, mitoxantrone, proflavine, spermine, paromomycin core, Berglund MBNL1 cmpd). Settings: recycling=3, sampling=50, mmcif output.

### What was NOT enqueued and why (HARD RULE: no silent-skip task types)

| Originally-planned item | Reason not enqueued | Mitigation |
|---|---|---|
| RFdiffusion ×150 binders on CELF1 RRM1/2 interface | `rfdiffusion` task type is **failing** on the live dispatcher: last 4 attempts on DOK7/AGRN/RAPSN/LRP4 failed with `[Errno 2] No such file or directory: 'brev'` (brev CLI missing on moltbot). Re-firing would silently fail again. | Deferred to next sprint after `brev` CLI is reinstalled on moltbot. |
| PocketXMol ×1500 against CELF1 RNA-binding face | `pocketxmol` is **not in ROUTING**. Per `feedback-canonical-task-types.md`, enqueueing a non-routed type is silently skipped — it would not run. | Defer to direct Vast A100 deploy (manual) once triage-budget permits. Requires either (a) new dispatcher task type + worker, or (b) direct `ssh vast-a100` shell script. |
| GenMol ×800 BBB-enriched scaffolds | GenMol NIM is documented as "broken server-side" in `learnings-gpu-fleet-2026-04-14.md`. | Substituted MolMIM (5 × 160 = 800 mols) as the scaffold generator. Same target molecule count. |
| DiffDock rescoring on 5-protein panel | `diffdock_screen` IS in ROUTING (Vast/Brev), but requires RNA-free apo receptor PDB. For CELF1 the RNA-free apo is 3NMR-chain-only (RNA-stripped) — needs manual prep. | Boltz-2 co-fold already provides structural affinity signal; DiffDock rescore queued as Phase 3b manual step, not auto-enqueued. |

### Phase 2 summary — enqueued vs. original plan

| Metric | Planned | Enqueued | Delta |
|---|---:|---:|---:|
| Scaffolds/molecules generated | 2,450 | 800 | −67% (GenMol down + PocketXMol not routed) |
| Targets in selectivity panel | 5 | 5 | 0 |
| Seed compounds scored | — | 12 | +12 |
| Triple-LLM gate coverage | 100% | queued; pending | — |

## Phase 3 — Scoring cascade (DESIGN; triggered automatically when Phase 2 tasks complete)

1. ADMET-AI (local; `/home/bryza/sma-research/admet/`) on all 800 MolMIM outputs.
   - BBB > 0.5
   - hERG < 0.7
   - CYP3A4 inhibition < 0.8
   - Lipinski + QED standard
2. Re-submit top-200 ADMET-pass molecules as **second-round Boltz-2 affinity panel** over the same 5-RBP targets.
3. Compute per-row **z-score differential**:
   - `z_CELF1 = (iptm_CELF1 − mean(iptm_all_5)) / std(iptm_all_5)`
   - `sel_z = z_CELF1 − max(z_MSI1, z_ELAVL1)` (selectivity over non-CELF paralogs)
   - Gate: **z_CELF1 > 0 AND sel_z > 0**
   (per `rule-zscore-is-the-selectivity-metric.md`)
4. Cross-selectivity-check against MBNL1 (CELF1 functional antagonist) — **demand MBNL1 iptm lower than CELF1** (do not want a promiscuous CUG-binder).

## Phase 4 — Top-5 MD (25 ns each) — DEFERRED to post-Phase-3 triple-LLM gate

- `md_simulation` task type routes to VastWorker/LocalWorker. 5 × 25 ns on A100 40GB ~= 3–4 h GPU.
- Protocol: POCKET_FIXED against CELF1 RRM1/2 3NMR (RNA-stripped apo), CHARMM36m + TIP3P + 0.15 M NaCl, 310 K.
- Post-process: MMGBSA on best 3 leads.

## Phase 5 — RNA-competition proxy (DEFERRED; post-Phase-4)

For top-10 leads:
- Generate apo CELF1 RRM1/2 (3NMR RNA-stripped).
- Generate 15-nt UG-repeat RNA `5'-UGUGUGUGUGUGUGU-3'` via RDKit/openmm-nucleic-acids prep.
- AutoDock Vina dock small molecule to the RNA-binding face.
- Separately, position the RNA in its crystallographic pose.
- Report competitive-proxy = `E_dock(compound) − E_dock(UG-repeat_frag)`.
- **This is a proxy, not a binding competition assay**. Document explicitly.

## Budget
- **Hosted NIM**: free (no per-call fees; rate-limited at 3 req/s)
- **Vast A100 40GB** (if needed for manual PocketXMol / MD): budget cap **$25**, ~$0.4–0.8/hr → 30–60 GPU-h available.
- **Brev sma-h100-two** (for Boltz-2 self-host if hosted NIM is throttled): already online, $0 incremental.

## Outputs (expected locations)
- `/home/bryza/fleet-results/bruno_celf_campaign/` — raw compute outputs, seeds, PDB verify logs.
- `/home/bryza/sma-research/qms/BRUNO_CELF1_TRANSLATION_AXIS_RESULTS.md` — triple-LLM gated results doc (DRAFT until Phase 3 complete).
- `/home/bryza/sma-research/qms/DATA_INVENTORY.md` — addendum with 3NMR / 4LMZ / 3D2N / 3D2S accession verifications.
- Top-10 RBP-directed leads TSV (CELF1-preferred by z-score).

## Hard rules recap
- Simon-Comms-Gate **HELD** — no Simon email, no Dropbox Mega Pack update, no `LIMK2_NEW_STORY` style doc until this campaign passes 3/3 triple-LLM gate AND Christian Fischer SEND-trigger.
- File name **MUST** include `_INTERNAL_DO_NOT_SEND` until gate passes (inherited from `session-2026-04-17-data-integrity-incident.md` practice).
- Every numeric claim must be traceable to a file under `/home/bryza/fleet-results/bruno_celf_campaign/` or to a VERIFIED public dataset (no placeholder numbers; per `rule-dataset-verify-before-use.md`).
- Cross-connection check: see PERP axis — both projects touch **mRNA trafficking at the NMJ**. If a CELF1-selective hit emerges, check whether PERP top-5 binders share chemotype features via ECFP4/Tanimoto before declaring orthogonality.

## Reporting checkpoints
- [x] Phase 1: TITLE-verify PDBs — **DONE 2026-04-17 (4 originally-cited PDBs REJECTED, 5 correct PDBs identified)**.
- [x] Phase 2: enqueue library + selectivity panel — **DONE 2026-04-17 (10 tasks queued)**.
- [ ] Phase 2 → RESULTS: first checkpoint (library size + verified targets).
- [ ] Phase 3: score + selectivity z-gate. Second checkpoint.
- [ ] Phase 4: MD 25 ns on top-5.
- [ ] Phase 5: RNA competition proxy on top-10.
- [ ] Triple-LLM gate (Opus + Groq + Gemini) on final RESULTS doc.
- [ ] Cross-connection check with PERP / NMJ campaigns.

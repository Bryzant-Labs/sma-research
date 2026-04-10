# SMA Research — PROJECT CATALOG (Single Source of Truth)

> **RULE #1 FOR CLAUDE**: BEFORE starting ANY new computational work, search this file for the topic.
> If it's here → read the existing data BEFORE touching the GPU.
> NEVER re-run what's already done. Extend what exists.

**Last updated**: 2026-04-10
**Purpose**: One catalog of every major compute campaign, its status, where data lives, and the CURRENT scientific interpretation (which changes as new data comes in).

---

## Quick Index

| Campaign | Start | Status | Current Verdict | Priority |
|---|---|---|---|---|
| [4-AP Multi-Target](#4-ap-campaign) | 2026-04-02 | CORRECTED | Kv compensation (Simon angle), NOT CORO1C | HIGH |
| [ROCK-LIMK2-CFL2 axis](#rock-limk-axis) | 2026-03-24 | VALIDATED | Core therapeutic axis for SMA | CRITICAL |
| [Fasudil Evidence Package](#fasudil-package) | 2026-03-30 | STAGED | Wait for finished package per Simon rule | HIGH |
| [bbb5 dual-binder](#bbb5) | 2026-04-05 | DONE | Dual LIMK2/ROCK1, NOT selective — backup | MEDIUM |
| [PocketXMol LIMK2-selective](#pocketxmol-limk2) | 2026-04-07 | ACTIVE | 14 selective hits from 20K screen | HIGH |
| [Fasudil scaffold hop](#fasudil-scaffold) | 2026-04-09 | NEGATIVE | 0/20 selective — published as neg result | DONE |
| [SMN2 Base Editing (ABE)](#abe-cure) | 2026-04-09 | RESEARCH | Liu lab 99% done, we EXTEND | HIGH |
| [ESM-2 kinase similarity](#esm2) | 2026-04-10 | DONE | LIMK1/2=0.990, ROCK1/2=0.998 | DONE |
| [Cas-OFFinder gRNA safety](#casoffinder) | 2026-04-10 | DONE | 14 exact-match antisense = safest | DONE |
| [RFdiffusion AAV capsid](#aav-capsid) | 2026-04-10 | RUNNING | 50 designs, ETA 22:00 UTC | HIGH |

---

## Campaigns (detailed)

### <a name="4-ap-campaign"></a>4-AP (4-Aminopyridine / Dalfampridine / Ampyra)

**Compound**: `Nc1ccncc1` (MW 94, FDA-approved for MS walking difficulty)
**Start**: 2026-04-02 (Simon suggested as relevant to his proprioception research)
**Status**: CORRECTED (2026-04-06)

#### What was done (April 2 campaign — 18 GPU analyses, ~500 GPU-hours)

1. **DiffDock v2.2 screening** — 378 compound-target pairs
2. **MD simulations**:
   - 4-AP + CORO1C 100ns (PDB 2B4E) — `GPU-Results-Trajectories/4AP_FEP_CORO1C_gpu33943049.dcd` (820MB)
   - 4-AP + Kv1.2 100ns (PDB 2R9R) — `GPU-Results-Trajectories/4AP_Kv12_gpu33887147.dcd` (389MB)
   - 4-AP + SMN2 pre-mRNA 100ns (GROMACS, PDB 4QK9)
   - FEP CORO1C 10ns
   - SMD CORO1C 10ns — `GPU-Results-Trajectories/4AP_SMD_CORO1C_gpu33943049.dcd` (735MB)
   - CFL2 MD — `GPU-Results-Trajectories/CFL2_gpu33887147.dcd` (211MB) **[4-AP + Cofilin-2, downstream target]**
   - CFL1 MD — `GPU-Results-Trajectories/CFL1_gpu33966229.dcd` (967MB)
   - Alanine scanning mutants
   - Selectivity control (10 random non-SMA proteins)
3. **Analog design**: 73 MolMIM analogs + 500 GenMol de-novo
4. **GenMol CFL2**: 3,634 molecules generated for CFL2
5. **ADMET full profile**: BBB 79%, bioavail 94%, hERG 12%, AMES 55%, DILI 62%, halflife 19h
6. **6 publication figures** in `4-AP-Figures/`

#### Original claim (April 2): CORO1C multi-target
- CORO1C DiffDock confidence +0.251 (rank 1 of 378)
- 5 targets bound: CORO1C, NCALD, SMN2, SMN1, UBA1
- Paper draft: `4-AP-Computational-Analysis.md`

#### CORRECTION (April 6): CORO1C withdrawn
**File**: `4-AP-Correction-Follow-Up.md`
- GSE287257 scRNA-seq (240 MNs): CORO1C NOT motor neuron-enriched (p=0.52 NS)
- CORO1C expression: 0.601 endothelial > 0.570 microglia > 0.405 MNs
- Real MN actin genes: **PFN2** (+1.22 log2FC, p=5.3e-18) and **LIMK1** (+1.20, p=8.4e-24)
- 4-AP at MW 94 triggers fragment-artifact flag in ADMET v2 (too small → nonspecific binding suspected)

#### Simon's ACTUAL hypothesis (from Correction doc)
> "SMA motor neurons have fewer potassium channels, leading to broader action potentials and impaired high-frequency firing. 4-AP as Kv blocker could compensate."

**Key**: NOT regeneration. NOT SMN2 splicing. It's **Kv compensation for proprioceptive MN dysfunction** — a symptomatic/functional improvement angle complementary to any SMN restoration therapy.

#### What's still valid
- ✅ Kv1.2 100ns MD stable binding (positive control reproduced)
- ✅ ADMET profile (BBB 79%, bioavail 94%)
- ✅ Pipeline methodology sound
- ❌ CORO1C claims withdrawn
- ❌ Multi-target claim compromised (fragment artifact)
- ❌ SMN2 binding (confirmed by my 2026-04-10 MD: 0 stable contacts after 18.6ns)

#### Gaps / Pending work
- [ ] **MMPBSA on Kv1.2 100ns trajectory** — we have .dcd but never computed ΔG (gap since April 2!)
- [ ] **Contact map analysis** on Kv1.2 trajectory — which residues touch 4-AP?
- [ ] **CFL2 trajectory analysis** — 211MB file exists, contents unknown to me. CFL2 is downstream of LIMK2 in our core axis!
- [ ] **Paper reframe**: CORO1C out, Simon proprioception angle in, connection to 14 LIMK2-selective hits
- [ ] Kv1.2 SMD unbinding (listed as queued in `4-AP-ANALYSIS-TASKS-2-4.md` — verify if completed)
- [ ] 73 MolMIM analogs were screened vs Kv1.2 (0 hits) but NOT vs current targets (LIMK2, ROCK2)

#### Duplicate work I did today (2026-04-10) — SKIP NEXT TIME
- Started new 20ns Kv1.2 MD (crashed at 62.5%). **Useless — 100ns already exists from April 2.**
- Ran new 4-AP + SMN2 MD showing 0 contacts. **Redundant — already deprecated.**
- Ran 4-AP DiffDock vs 5 targets again. **Already in 378-pair screen from April 2.**

#### Key files
| File | Location |
|---|---|
| Paper draft | `Dropbox/SMA/4-AP-Computational-Analysis.md` |
| Correction | `Dropbox/SMA/4-AP-Correction-Follow-Up.md` |
| Findings summary | `Dropbox/SMA/4-AP-FINDINGS-SUMMARY.md` |
| Pending tasks | `Dropbox/SMA/4-AP-ANALYSIS-TASKS-2-4.md` |
| Figures | `Dropbox/SMA/4-AP-Figures/fig1-6_*.png` |
| Trajectories | `Dropbox/SMA/GPU-Results-Trajectories/4AP_*.dcd` + `CFL2_*.dcd` |
| ADMET | `Dropbox/SMA/GPU-Results/admet-profiling/4AP_all_compounds/` |
| Presentations | `Dropbox/SMA/4AP-Presentation-Prof.pptx` (+ updated) |
| GitHub | `github.com/Bryzant-Labs/sma-research/tree/main/4-AP-Campaign` |

---

### <a name="rock-limk-axis"></a>ROCK-LIMK2-CFL2 Axis

**Hypothesis**: SMN deficiency → ROCK2 hyperactivation → LIMK phosphorylation → cofilin inactivation → actin rod formation → axonal transport block → motor neuron death
**Status**: VALIDATED by 3 independent datasets (see session recaps)
**Key findings**:
- LIMK2 +2.81× in SMA motor neurons
- CFL2 is disease-specific (UP in SMA, DOWN in ALS)
- PFN2 +1.22 log2FC MN-enriched
- Zero competitors in LIMK2-selective drug space globally

**Compounds tested**:
- Fasudil (ROCK inhibitor, approved in Japan) — structure validated, MD 100ns done
- bbb5 (genmol_119_bbb_5) — turned out to be dual LIMK2/ROCK1, not selective
- 14 LIMK2-selective PocketXMol hits (7 previous + 7 overnight 2026-04-10)

**Key files**:
- Memory: `memory/finding-esm2-kinase-selectivity.md`
- MD sims: `Dropbox/SMA/md_results/` + `gpu-fleet/results/SMA/md_sims/LIMK2_*` and `LIMK1_*`
- Session recap: `memory/session-2026-04-09-final-recap.md`

---

### <a name="pocketxmol-limk2"></a>PocketXMol LIMK2-Selective Campaign

**Tool**: PocketXMol (Cell 2026, 82.5% docking success)
**Campaign**: 20,000 molecule screen against LIMK2 ATP site + DFG-out pocket
**Status**: ACTIVE (additional batches generated overnight 2026-04-10)

**Results**:
- 4,346 molecules passed basic filters
- DiffDock selectivity vs LIMK1/ROCK1: **14 selective hits** (threshold margin > 0.3)
  - 7 from 2026-04-09 session (chunks 0-2173)
  - 7 from 2026-04-10 overnight (chunk 2174-3260)
- Top lead: `1219_0` (pyrazolo-pyridine, margin +0.43, BBB+DILI pass)
- 7,275 additional DFG-out Type II molecules generated (batches 1, 2, 4) — DiffDock selectivity pending

**Key files**:
- Selective hits JSON: `gpu-fleet/results/SMA/drug_discovery/diffdock_selectivity/2026-04-10_overnight_chunks/gpu_34455192/selective_gpu0_start3261.json`
- Older 7 hits: `gpu-fleet/results/SMA/pocketxmol/selective_hits_diffdock.json`
- Dropbox backup: `findings/diffdock_selectivity_2026-04-10/`
- Finding: `findings/2026-04-10/FINDING_2026-04-10_new_7_selective_hits.md`

---

### <a name="fasudil-package"></a>Fasudil Evidence Package (for Simon)

**Status**: STAGED — per rule "Simon gets finished work only"
**Folder**: `Dropbox/SMA/Simon_Fasudil_Evidence_Package/`
**Updated**: 2026-04-09 (removed Bowerman 2012 as lead evidence per Simon feedback)

**Contents**:
- Evidence summary
- ROCK-LIMK-CFL2 pathway rationale
- Fasudil MD 100ns results
- Selectivity data
- Combination protocol (ABE + Fasudil, 65 mice, 57K EUR)

---

### <a name="bbb5"></a>bbb5 (genmol_119_bbb_5)

**Status**: CHARACTERIZED — dual LIMK2/ROCK1 inhibitor, NOT LIMK2-selective
**Verdict**: Backup candidate, not primary
**Key**: Binds ROCK1 stronger than LIMK2 — cannot claim selectivity
**Finding**: `findings/2026-04-09/FINDING_2026-04-09_bbb5_dual_LIMK2_ROCK1.md`

---

### <a name="fasudil-scaffold"></a>Fasudil Scaffold Hop

**Status**: NEGATIVE RESULT (published)
**Result**: 0/20 scaffold variants LIMK2-selective
**Reason**: Isoquinoline scaffold is inherently ROCK-preferring
**Finding**: `findings/2026-04-10/FINDING_2026-04-10_Fasudil_scaffold_hop_NEGATIVE.md`

---

### <a name="abe-cure"></a>SMN2 Base Editing (ABE) — Cure Track

**Status**: RESEARCH — Liu lab achieved 99% editing (Science 2023), we EXTEND not replicate
**Key**: Track 2A of the cure pivot. Partner with ABE + Fasudil combo.
**Files**: `Dropbox/SMA/smn2-base-editing/`, `memory/sma-cure-action-plan.md`

---

### <a name="esm2"></a>ESM-2 Foundation Embeddings

**Date**: 2026-04-10
**Finding**: **LIMK1/LIMK2 = 0.990, ROCK1/ROCK2 = 0.998** cosine similarity
**Interpretation**: Empirically validates why kinase selectivity is hard — global sequence embeddings cannot distinguish isoforms. Pocket-level required.
**Files**: `gpu-fleet/results/SMA/esm2_foundation/`, `findings/2026-04-10/FINDING_2026-04-10_ESM2_kinase_similarity.md`

---

### <a name="casoffinder"></a>Cas-OFFinder SMN2 gRNA Safety

**Date**: 2026-04-10
**Method**: 6 candidate gRNAs vs hg38, up to 4 mismatches
**Result**: 2,097 total hits; **`TTTGTCTAAAACCCATATAA`** (antisense) = safest with 14 exact matches; **`GTTTTAGACAAAATCAAAAA`** = unusable (176 matches)
**Key**: Our antisense guide is 39% safer than Liu's published gRNA A8
**Finding**: `findings/2026-04-10/FINDING_2026-04-10_casoffinder_SMN2_guide_safety.md`

---

### <a name="aav-capsid"></a>RFdiffusion AAV9 Capsid Design

**Status**: RUNNING (started 2026-04-10 ~19:30 UTC, ETA ~22:00 UTC)
**Target**: 50 AAV9 VP1 variants with improved motor neuron tropism
**Compute**: A100 PCIe 80GB Sweden (`34565416`)
**Contig**: `A219-489/10-25/A507-580/10-25/A598-736` (VR-V and VR-VIII loops)
**Live sync**: `gpu-fleet/results/SMA/aav_capsid_design/`

---

## Rules (enforce these Claude)

### Before starting ANY new compute work on topic X:

1. **Grep this file** for X — if found, READ the section FULLY
2. **Check the "Key files" paths** — do the data files exist? Check size + mtime
3. **Check "Current Verdict"** — has the hypothesis been superseded?
4. **Check "Gaps / Pending work"** — is what you're about to do already listed as TODO, or is it duplicate work?
5. **Ask Christian if still relevant** — hypotheses change; don't assume old assumption still holds
6. Only THEN start compute

### After completing ANY major work:

1. **Update this file** with the new data paths + verdict
2. **Update MEMORY.md** with one-line pointer
3. **Copy to Dropbox** (findings, data, trajectories)
4. **Commit to GitHub** (if public-safe)

### When Simon (or any collaborator) gives feedback:

1. **Write a CORRECTION section** in the relevant campaign (don't edit history)
2. **Mark old claims as [WITHDRAWN]** — leave them visible for provenance
3. **Update verdict and gaps**

---

## Open Questions That Need Christian / Simon Input

1. **4-AP**: Run MMPBSA on existing Kv1.2 100ns trajectory to finally get ΔG?
2. **4-AP**: Analyze CFL2 trajectory (211 MB, we've never looked at it) — could be direct hit on ROCK-LIMK2-CFL2 axis
3. **4-AP paper reframe**: Who rewrites the paper with Simon's proprioception angle + LIMK2 connection?
4. **PocketXMol DFG-out**: Run DiffDock selectivity on the 7,275 new molecules?
5. **RFdiffusion AAV**: When done, compare to AAV9 baseline + AAV-PHP.eB benchmarks?

---

## License

CC-BY-4.0 — open catalog. Part of `Bryzant-Labs/sma-research`.

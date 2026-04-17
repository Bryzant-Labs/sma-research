# SMA CURE — Action Plan 2026

> ⚠️ **UNDER_REVIEW 2026-04-17** — The "ROCK-LIMK2-CFL2 axis (3 datasets)" framing on line 19
> and the "ABE + Fasudil = cure" premise on line 6 rest on the RETRACTED hyperactive-axis
> rationale (Incident 2026-04-17-001). ROCK2 is pooled DOWN in SMA MN (−0.254, p=9.0e-5),
> LIMK2 model-dependent. Track A (ABE base editing) survives independently; Fasudil side of
> the combination is UNDER_REVIEW at the MN-intrinsic rescue layer but survives at the
> muscle-layer (Bowerman 2012). See `qms/CORRECTIONS_LOG.md` Audit-Event 2026-04-17-002 §U20
> and `qms/meta_analysis/CORRECTED_SIGNATURE.md`.

## From the SMA Omni Model Vision → Concrete Execution

The original SMA Moonshot++ plan (€500K, 1,280 GPUs, 6 weeks) outlined the vision.
Today we have the specific path: **ABE base editing + ROCK-LIMK2-CFL2 recovery = the cure nobody else is building.**

---

## WHAT CHANGED SINCE THE ORIGINAL PLAN

| Original Vision (6 months ago) | What We Now Know (April 2026) |
|-------------------------------|-------------------------------|
| "Generate 10-100M drug candidates" | Done: 20K generated, 7 LIMK2-selective hits found |
| "CRISPR Prime Editing blueprint" | Better: ABE base editing already works at 99% (Liu lab) |
| "AAV 2.0 capsid designs" | Still needed — delivery remains the bottleneck |
| "SMA OmniModel" | Partially built — 5968 sources, 80 targets, 19454 claims in our platform |
| "€500K GPU sprint" | Can start with €300-500 on Vast.ai, scale when XE9680 arrives |
| "Unknown therapeutic targets" | ~~Found: ROCK-LIMK2-CFL2 axis (3 datasets), ZERO competitors in LIMK2-selective~~ **RETRACTED 2026-04-17** — axis framing inverted (ROCK2 DOWN in SMA MN per meta, p=9.0e-5). Re-framed: ZERO competitors in LIMK2-selective chemistry (structural/selectivity claim, survives), but the disease-axis rationale needs re-derivation. See `qms/CORRECTIONS_LOG.md` Audit-Event 002. |

**The biggest shift**: We don't need to find the genetic fix — **Liu lab already found it (99% editing)**. We need to:
1. Optimize delivery (AAV capsid design — WP4 from original plan)
2. Build the recovery arm (Fasudil/LIMK2 — our unique contribution)
3. Validate the combination (ABE + Fasudil in mouse model)

---

## ACTION PLAN — 3 PARALLEL TRACKS

### TRACK A: ABE + Fasudil Combination (THE CURE)
**Timeline: Complete ALL compute → Present to Simon with finished package → Wet lab**

**Phase 1: Computational (NOW — complete before Simon meeting)**

| Step | What | Cost | Status |
|------|------|------|--------|
| A1 | Extract Liu lab guide sequences | €0 | **DONE** — gRNA A8 identified |
| A2 | Novel guide design + scoring | €0 | **DONE** — pos 7, 0 bystanders |
| A3 | Cas-OFFinder genome-wide off-target | €50 | Ready to deploy |
| A4 | SpliceAI verify exon 7 inclusion | €20 | Script ready |
| A5 | Combination protocol design | €0 | **DONE** — 65 mice, 57K EUR |
| A6 | **XE9680: AAV capsid optimization** | €0 (borrowed) | Waiting for hardware |
| A7 | **XE9680: SMA foundation model** | €0 (borrowed) | Waiting for hardware |
| A8 | **XE9680: OmniModel predictions** | €0 (borrowed) | Waiting for hardware |
| A9 | Build COMPLETE evidence package | €0 | After A3-A8 done |

**Phase 2: Simon Handoff (AFTER all compute is finished)**

| Step | What | Cost |
|------|------|------|
| A10 | Present FINISHED package to Simon | €0 |
| A11 | Simon validates and begins wet lab | ~57K EUR |
| A12 | Analyze results | €0 |
| A13 | Publish | €0 |

**KEY RULE: Simon gets finished work only. No preliminary results. No proposals. A complete, lab-ready package that he can execute immediately.**

### TRACK B: Universal Recovery Platform (PARTNERSHIPS)
**Timeline: Continuous — our ongoing contribution**

| Step | What | When | Cost |
|------|------|------|------|
| B1 | Fasudil evidence package for pharma partners | **DONE** | €0 |
| B2 | LIMK2-selective compound optimization (1219_0) | Running | GPU costs |
| B3 | Contact Novartis (Zolgensma + Fasudil combo) | After Simon data | €0 |
| B4 | Contact Roche (risdiplam + Fasudil combo) | After Simon data | €0 |
| B5 | Contact Biogen (nusinersen + Fasudil combo) | After Simon data | €0 |
| B6 | Platform as open resource for all partners | Continuous | Server costs |

### TRACK C: SMA Omni Model (XE9680 WHEN AVAILABLE)
**Timeline: When Dell XE9680 arrives**

From the original plan, UPDATED with current knowledge:

| WP | Original | Updated Priority | Status |
|----|----------|-----------------|--------|
| WP1 | Data aggregation | **DONE** — 5968 sources, 80 targets, 19454 claims | Complete |
| WP2 | SMA OmniModel | **HIGH** — train on our platform data + ROCK pathway | Needs XE9680 |
| WP3 | Drug generation | **PARTIALLY DONE** — 20K PocketXMol, 7 selective hits | Continuing |
| WP4 | AAV 2.0 capsid design | **HIGHEST PRIORITY** — delivery is THE bottleneck | Needs XE9680 |
| WP5 | Open-source release | **CONTINUOUS** — platform already public | Live |

**XE9680 Focus (8× H100, 640GB VRAM):**
1. AAV capsid evolution (RFdiffusion + ProteinMPNN) — design capsids that reach MORE motor neurons
2. SMA foundation model (SMA-GPT) — predict editing outcomes + pathway interactions
3. Microsecond MD simulations — verify capsid-receptor binding
4. Multi-omics integration — patient stratification for combination therapy

---

## BUDGET COMPARISON

| Approach | Cost | What You Get |
|----------|------|-------------|
| **Our plan (Tracks A+B)** | **~€60-80K** | ABE+Fasudil combo validated in mice, partnership-ready |
| XE9680 addition (Track C) | +€0 (borrowed) | Foundation model, AAV designs, OmniModel |
| Original Moonshot++ | €500K | Everything above + 100M molecules + massive scale |
| Pharma equivalent | €50-100M | Same results, 5-10 years slower |

---

## WHAT'S ALREADY DONE (our current assets)

### Computational Platform
- 5,968 literature sources ingested and analyzed
- 80 molecular targets scored and ranked
- 19,454 evidence claims extracted
- 451 clinical trials tracked
- CORTEX knowledge graph: 424 nodes, 90% R@5 retrieval
- 13 MCP tools for programmatic access
- Auto-learn system with Opus validation gate

### Drug Discovery Results
- Fasudil: ROCK2 binder validated (4.2Å, Stage 5 PASS)
- bbb5: dual LIMK2/ROCK1 inhibitor characterized
- 7 LIMK2-selective hits from 20K PocketXMol campaign
- 1219_0 (pyrazolo-pyridine): lead selective hit (BBB+DILI pass)
- 65 Fasudil scaffold variants with clean ADMET (negative selectivity result published)
- 16 MD simulations completed and analyzed
- MMPBSA binding free energy pipeline operational

### Base Editing
- Published guide sequences extracted (gRNA A8: 99% efficiency)
- Novel guide candidate identified (pos 7, 0 bystanders, score 0.755)
- Combination protocol designed (65 mice, 57K EUR)
- Competitive landscape mapped (ZERO companies with SMA base editing program)
- Gene Editing section live on platform (both v1 and v2)

### Infrastructure
- GPU fleet: 12 instances managed autonomously
- AmberTools: installed locally for rigorous MMPBSA
- PocketXMol: 20K molecule campaign complete
- DiffDock: selectivity screening running
- Daily CORTEX harvest: SMA + CMS APIs

---

## THE ONE-SLIDE PITCH

```
NOBODY IN THE WORLD IS DOING THIS:

  Base Editing (fixes the gene) + ROCK Pathway Inhibition (repairs the damage)
  = ABE + Fasudil combination therapy for SMA

  The genetic fix exists (99% editing, Liu lab)
  The recovery drug exists (Fasudil, approved in Japan)
  The combination has never been tested
  
  Cost to validate: €57K in mice
  Cost to identify: €200 in GPU compute
  
  If it works: first combination cure for SMA
  If it doesn't: honest negative result, still valuable data
  
  Zero competitors. Open platform. Mission: cure SMA.
```

---

## REVISED EXECUTION ORDER

```
Phase 1: COMPUTE EVERYTHING (Now → XE9680 arrival)
├── Vast.ai: Cas-OFFinder, SpliceAI, DiffDock selectivity
├── Vast.ai: Complete LIMK2-selective campaign 
├── Local: BE-Hive, guide scoring, MMPBSA
├── XE9680: AAV capsid design (RFdiffusion)
├── XE9680: SMA foundation model (SMA-GPT)
├── XE9680: OmniModel v1
└── XE9680: Microsecond MD validations

Phase 2: BUILD EVIDENCE PACKAGE (After all compute)
├── Validated guide sequences + off-target profiles
├── AAV capsid designs ranked by MN tropism
├── OmniModel predictions for combo therapy
├── Complete ADMET + selectivity data for LIMK2 candidates
├── Combination protocol: ABE + Fasudil, ready to execute
└── Everything in one package, lab-ready

Phase 3: SIMON HANDOFF (One meeting, finished work)
├── Present complete package
├── He decides: go/no-go
└── If go: wet lab starts immediately (57K EUR)
```

## NEXT 7 DAYS

| Day | Action | Owner |
|-----|--------|-------|
| 1 | Cas-OFFinder off-target analysis (rent 1 A100) | Claude/GPU |
| 2 | SpliceAI verification of editing outcome | Claude/local |
| 3 | Collect remaining DiffDock selectivity results | Claude/GPU |
| 4 | Run MMPBSA on new POCKET_FIXED MDs | Claude/local |
| 5 | Update platform with all new data | Claude |
| 6 | AAV capsid literature review (prep for XE9680) | Claude |
| 7 | Prepare XE9680 workload specifications | Claude |

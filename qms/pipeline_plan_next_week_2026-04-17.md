# SMA Compute Pipeline Plan — Week of 2026-04-17 → 2026-04-24

**Status: DRAFT — internal only. Simon-Comms-Gate HELD. No external claims.**

Authored: 2026-04-17 20:30 UTC
Data source: `gpu-fleet/lib/gpu_roi_table.json` (n≥5 rows only), `workload_compatibility.json`, `gpu_picker.py`, `roi-surprises-2026-04-17.md`, `fleet-infrastructure-learnings-2026-04-17.md`.
Budget: **$300 paid-GPU spend cap** Apr 17 → Apr 24. Free NIM uncapped. TPU assumed **not** TRC-confirmed (pre-stage only; flip if approval lands).

---

## Section 1 — Headline targets by Apr 24, 2026

Three measurable deliverables (two stretch). Each has a deliverable, owner track, $-spend envelope, success gate, compute routing.

| # | Deliverable | Owner track | Spend envelope | Success gate | Compute routing |
|---|---|---|---|---|---|
| **1** | **LIMK2 αC activator wet-lab pick-list v1** — 5 SMILES with triple-LLM 3/3 PASS, C_rel > 0 (co-crystal-calibrated), z_LIMK2 > 0, 50 ns MD stability, selectivity vs ROCK1/ROCK2/LIMK1 documented | Kracher Schritt 1 | **$55** | 5 SMILES, each with CLAIMS_REGISTRY entry + wet-lab one-pager | 50 ns replicates on **RTX 3090** pool ($0.037/ns); Boltz-2 rescore on **self-host batched H100 SXM 80G** ($0.00042/cmpd); DiffDock C_rel on **RTX 4090** pool (pending n≥5 confirmation) |
| **2** | **SSH1 phosphatase lead-hypothesis (APPROVED or REJECTED)** — triple-LLM gated decision on whether SSH1 inhibition is a distinct mechanistic hit vs LIMK2-activation proxy | Kracher Schritt 2 | **$25** | hypothesis file `/qms/SSH1_vscreen_RESULTS.md` with APPROVED or REJECTED header; CLAIMS_REGISTRY sign-off | Phase 3 on **Free NIM** (GenMol+MPNN+Boltz-2 iptm proxy); reserved France H100 (35137507) finishes only if NIM insufficient; expected <10 h wall-clock |
| **3** | **NMJ MD Opt-1 3-replicate 100 ns** — 3 converged 100 ns replicates of 12-chain ECD; interface-contact fraction stable ± 20%; triple-LLM verdict on Boltz-2 iptm 0.13–0.18 "weak-as-expected" | Opt 1 | **$70** | 3 × DCD + 3 × metrics.tsv with contact persistence + RMSD plateau <3 Å | Current **B200 #2 (35152540)** runs out ~Apr 18 evening; **reprovision as 3 × RTX 3090** at $0.170/hr = 0.037/ns vs B200 $30/hr (~37× cheaper per-ns) |
| **4 (stretch)** | **Bispecific binder farm — 10 gate-pass candidates** | Opt 2 | **$40** | 10 designs passing: pLDDT≥0.70 AND Boltz-2 iptm≥0.55 AND MPNN seq_recovery≥0.40 | Continue **B200 #1 (35153395)** through its wall-time; post-runoff triage on **Brev H100 attach-mode** for Chai-1 cross-validation at ~$1.49/hr |
| **5 (stretch)** | **ROCK2 robust-DOWN target dossier** — new hypothesis arm since ROCK2 is the strongest meta-analysis hit (β=−0.254, p=9e-5, I²=56%) | New track | **$20** | Hypothesis file + DRAFT claim; NO external send | **Free NIM** GenMol+Boltz-2 scaffold-hop on ROCK2 activator pocket (inverted from ROCK2-inhibition Fasudil logic); ADMET-AI CPU; PocketXMol 1 A100 SXM4 short |

**Total projected paid spend:** ~**$210** (leaves ~$90 contingency headroom for preemption churn, DOA rentals, targeted bursts).

---

## Section 2 — Routing table per workload (real-data-driven)

All cost cells cite the corresponding ROI table row. Silent-zero workloads are blocked (see Section 6).

| Workload | Destination tier | Rationale (ROI cell) | Daily throughput | $/day | Silent-zero pre-flight fix |
|---|---|---|---|---|---|
| `boltz2_rescore_streaming` (interactive) | **Vast A100_SXM4_40G** | $0.02444/useful-cmpd vs H100_NVL $0.04603 (**1.88× cheaper**); memory ceiling 360 residues covers SMA complexes (median 275, max 360) | ~840 cmpd/day on 1 A100 | $20.32 (1 GPU) | no |
| `boltz2_rescore_batched` | **Brev H100 SXM self-host** (sma-h100-two:8003) | $0.00042/cmpd batched vs $0.02444 streaming (**58× cheaper** via 28 s warmup amortization at batch=5) | 86,400/day sustained solo; 28,800 at n3 contention | $35.83 persistent (if full day) but shared across tracks | no; keep n≤2 concurrent to avoid 3× contention penalty |
| `pocketxmol_volume` | **Vast A100_SXM4_40G** | $0.046/useful-molecule (gate-pass 40%). No cheaper tier has n≥5. | ~1104 mol/day (46/hr × 24, gate-adj ~440) | $20.33 (1 GPU) | C_rel calibration required per target |
| `diffdock_screen` | **Vast RTX_4090** (preferred once n≥5) → **Brev H100 SXM** fallback | RTX_4090 ~$0.0001/pose raw at n=3 (PRELIMINARY); H100 SXM confirmed $0.00104/useful-pose. Kick off 2 more RTX runs this week to close n≥5. | RTX: ~60,000 poses/day (24h × 2500); H100: 86,400/day | RTX: $6.00/day; H100: $35.83/day | C_rel calibration MUST precede each target — "absolute 0.5" is a trap |
| `openmm_md_production_85K_atoms` | **Vast RTX_3090** | $0.0370/ns vs A100_PCIE $0.166/ns (**4.5× cheaper**); 4.6 ns/hr × 24 = 110 ns/day — exceeds 100 ns deadline in <1 day | 110 ns/day per GPU | $4.08 (1 GPU) × 3 reps = $12.24 | source-build OpenMM (CUDA_ERROR_UNSUPPORTED_PTX_VERSION with conda/pip) |
| `openmm_md_production_35K_atoms` (FEP / metadynamics) | **Vast RTX_3090** first; **Vast A100_SXM4** only if FEP/metadynamics cross-replica | 35K atoms @ 182 ns/day on RTX_3090; $0.0224/ns | 182 ns/day | $4.08 | same |
| `protein_mpnn` | **Hosted NIM (Free)** | $0/design; gate-pass 46.1% (known silent-zero, still best effective price). Self-host backup for high-stakes designs only. | 500/hr × 24 = 12,000/day, gate-adjusted 5530 | $0 | hold on high-stakes jobs until upstream NIM fix; batch ≥ 50 input PDBs per submission |
| `genmol_generate` | **Hosted NIM (Free)** | $0/mol, 92% gate-pass (strong). | 1200/hr × 24 = 28,800/day, gate-adj 26,500 | $0 | none |
| `boltz2_affinity` (iptm proxy) | **Hosted NIM (Free)** | $0 free tier; 75% gate rate (429 throttling). Use only for coarse screen, not APPROVED-claim numbers | 100/call, multi-call/day up to quota | $0 | none |
| `molmim_generate` | **BLOCKED** (see Section 6) | 0/811 gate-pass since Apr 14. Infinite effective cost. | 0 | $0 | Triton 500 server-side upstream fix |
| `rfdiffusion_binder` | **BLOCKED** until contigs pre-flight lands (Section 6) | 0/4 PDB survival. | 0 | $0 | contigs-vs-PDB-range validation before firing |
| `colabfold_multimer_small` | **TPU v6e-4/8 (if TRC confirmed)** else Vast A100_80G | TPU = $0 with TRC; A100_80G $0.0225/fold; memory ceiling 900 residues on A100 80G, 8463 residues on TPU v6e-4 | TPU: proteome-scale; A100: 40 folds/hr | $0 (TPU) or $21.60/day (A100) | verify JAX-native before TPU alloc |
| `prot_t5_embed` | **TPU v6e (if TRC confirmed)** else NO_GO | Perfect TPU fit; no A100 measurement yet | NO_DATA throughput | $0 or NO_GO | none |
| `esm2_scan` | **TPU v6e (if TRC confirmed)** else Vast A100_SXM4 | JAX port TPU-ready; CUDA fallback functional | NO_DATA | $0 or ~$20/day | none |
| `openfold_multistate` | **TPU v6e (if TRC confirmed)** else Vast H100 | NO_DATA on runs; keep pre-staged | NO_DATA | $0 or ~$36/day | none |
| `chai1` (cross-validation) | **Brev H100 SXM attach-mode** | CUDA-only; never TPU ($9 lesson). Use for bispecific farm cross-check only. | ~200 folds/day estimate | ~$36/day if rented | none |
| `admet_ai_batch` | **CPU (local / moltbot)** | GPU marginal; don't rent | 1000+/hr CPU | $0 | none |
| `mmpbsa` | **CPU (local / moltbot)** | CPU-bound in practice | — | $0 | Amber topology from trajectory first frame; PBC-aware distance |

**Net daily burn plan (paid) under normal operation:** ~$30–40/day average → $210–280 over 7 days. See Section 7 waterfall.

---

## Section 3 — Scientific tracks (weekly schedule)

### Track 1 — LIMK2 αC activator (Kracher Schritt vorwärts 1)

**State at 2026-04-17 20:30 UTC:**
- Agent `a34b3302`: MD LIMK2 top-5 × 50 ns running on A100 SXM4 Czechia (35120547, 90% util, 154 ns/day smoke). Already 5 instances running LIMK2 downstream (35097680 Bulgaria ssh1-vscreen, 35138198 retry, 35141608 H100 NVL PxM batch).
- 469 valid SMILES from PocketXMol αC campaign (a81706c5), triple-LLM 3/3 PASS.
- Boltz-2 15-kinase panel partially complete (~590/645 at last check).

**Next 3 milestones:**

| Milestone | ETA | Routing |
|---|---|---|
| M1: Finish Boltz-2 15-kinase panel for top 100 αC hits | Apr 18 morning | **Self-host batched** on sma-h100-two:8003 ($0.00042/cmpd) — NOT streaming |
| M2: 3-replicate 50 ns MD on top 5 selective hits | Apr 19 evening | **3 × RTX 3090** ($0.170/hr × 36 h × 3 = **$18.36**). **Redeploy** — DO NOT keep A100 SXM4 Czechia at $0.81/hr (that's $29/ns vs $0.037/ns on RTX 3090, **22× overpay**) |
| M3: Wet-lab pick-list v1 with CLAIMS_REGISTRY entries | Apr 22 | CPU ADMET-AI + manual triage |

**Fork decision:** If Boltz-2 rescore finds ≥ 3 compounds with z_LIMK2 > +1.0 AND selectivity_z > 0.5 by **Apr 19 noon**, fire an additional 100 ns metadynamics replicate on **1 × A100_SXM4_40G** ($0.847/hr × 24 h = **$20.33** — justified for free-energy-critical work). Otherwise stay on RTX 3090 plain MD.

---

### Track 2 — SSH1 phosphatase inhibitor (Kracher Schritt vorwärts 2)

**State at 2026-04-17 20:30 UTC:**
- Agent `a5010743`: SSH1 vscreen Phase 3 on Free NIM + reserved France H100 (35137507, currently 0% util — silent).
- `/qms/ssh1_vscreen/` has Phase 1/2 outputs.

**Next 3 milestones:**

| Milestone | ETA | Routing |
|---|---|---|
| M1: Phase 3 GenMol+MPNN+Boltz-2 iptm on 2 SSH1 pockets | Apr 18 evening | **Free NIM** (genmol 92% gate; mpnn 46% gate; boltz2 iptm 75% gate) — $0 |
| M2: Top-20 PocketXMol rescore | Apr 19 | **Vast A100_SXM4_40G** ($0.046/useful-mol). Target burst: ~8 h × $0.70 = **$5.60** |
| M3: Hypothesis-approve-or-reject with triple-LLM + CLAIMS_REGISTRY | Apr 20 | CPU triage |

**Fork decision:** If Free-NIM Phase 3 shows ≥ 5 hits with iptm > 0.55 by **Apr 18 22:00 UTC**, release the France H100 (35137507) **immediately** ($1.49/hr, already idle = pure burn). If no hits, pivot H100 to Chai-1 cross-check at $1.49/hr × 6 h = **$9**.

---

### Track 3 — NMJ 12-chain ECD 100 ns × 3 MD (Opt 1)

**State at 2026-04-17 20:30 UTC:**
- **B200 #2 (35152540)** running 0% util currently — **RED FLAG** for $30/hr burn. Either MD not yet started, or config issue. Triage tonight.
- TPU v6e-8 atomic assembly validated (iPTM 0.13–0.18, triple-LLM 3/3 PASS).

**Next 3 milestones:**

| Milestone | ETA | Routing |
|---|---|---|
| M1: Verify MD actually producing ns on B200 or reprovision | Apr 17 23:59 UTC | **Decision gate** — see fork |
| M2: 3 replicates × 100 ns converged | Apr 20 | **3 × RTX 3090** ($4.08/day × 3 × 3 days = **$36.72**) |
| M3: Metadynamics replicate on most-interesting interface | Apr 22 | **1 × A100_SXM4** ($20.33 for 24 h) |

**Fork decision (CRITICAL — execute tonight):** If B200 #2 is still 0% util at Apr 17 23:59 UTC, **destroy it immediately** — already burning $30/hr on nothing (~$70 wasted if we wait until morning). Redeploy as 3 × RTX 3090 at $0.51/hr total (**59× cheaper**, same 3-replicate output). Backup the MD inputs first (rsync + checksum per `rule-never-autodelete-without-verified-backup.md`).

---

### Track 4 — NMJ bispecific binder farm (Opt 2)

**State at 2026-04-17 20:30 UTC:**
- **B200 #1 (35153395)** running 72.9% util — earning its $30/hr (4+ concurrent users per the 8-way B200 rule).
- 427 backbones generated; gate-pass phase starting.

**Next 3 milestones:**

| Milestone | ETA | Routing |
|---|---|---|
| M1: Gate-pass filtering (MPNN+ESMfold+Boltz-2) on 427 backbones | Apr 18 evening | Continue **B200 #1** through wall-time (24 h); MPNN+ESMfold both free-NIM-eligible for overflow |
| M2: Top-20 Chai-1 cross-validation | Apr 19–20 | **Brev H100 SXM attach-mode** ($1.49/hr × 10 h = **$14.90**). Chai-1 CUDA-only (never TPU) |
| M3: Top-10 pick-list with experimental handoff draft | Apr 22 | CPU |

**Fork decision:** If ≥ 10 gate-passers by **Apr 19 08:00 UTC**, fire Chai-1 cross-check on Brev H100 for **$15**. If ≥ 20 gate-passers, extend Brev H100 session an additional day (+$36) for deeper Chai-1 + Boltz-2 batched validation. If < 5, extend Proteina-Complexa generation another 18 h on B200 #1 ($540 — **STOP if farm is underperforming**, switch to a different NMJ receptor pair instead).

---

## Section 4 — Contingency fills (TPU + Free NIM + RTX pool)

### 4.1 TPU v6e (only if TRC confirmed mid-week)

**Trigger:** TRC approval email lands.
**Pre-staged workloads (executable within 30 min of approval):**

| Workload | Slice | Content | Expected output |
|---|---|---|---|
| ColabFold proteome batch | v6e-8 | 174 remaining SMA proteins × 3 seeds = 522 folds | 522 PDBs with pLDDT ≥ 0.7 gate |
| ProtT5 full embeddings | v6e-4 | 176 SMA proteome entries | 1024-D embedding tensor for ranker |
| OpenFold JAX branch validation | v6e-4 | Top 20 NMJ subcomplex pairs | Multi-state ensemble |
| AF3 (if weights land) | v6e-8 | Full NMJ 11.7k-residue complex | Single-shot assembly |

**Cost if TRC confirmed:** $0.
**Cost worst case (TPU rental without TRC):** $778/day → **DO NOT RENT**. If TRC denied, these stay pre-staged as a backlog until GB10 Spark lands or TPU becomes funded.

### 4.2 Free NIM backlog queue (keep saturated 24/7)

Per-day pre-queued quota to keep free tier full even with no human present:

| Workload | Target/day | Gate-adj output |
|---|---|---|
| Boltz-2 iptm proxy rescore (screens only, not APPROVED claims) | 200 tasks × 20 cmpd = 4000 | 3000 |
| ProteinMPNN sequence designs | 500 tasks × 100 seq = 50,000 (gate 46%) | 23,000 |
| GenMol variations (SAFE, 20 mol/call) | 300 tasks × 20 = 6000 (gate 92%) | 5,520 |
| ESMfold structure checks | 100 tasks | ~90 |

Dispatcher cron `*/5 * * * * queue_refill.py` keeps the queue ≥ 30 tasks. If NIM quota saturates (429 spike), demote overflow to **RTX 4090 pool** or **self-host H100 batched** — never upgrade to paid for NIM-only work.

### 4.3 RTX 3090 / 4090 pool (the per-dollar winner for production)

Based on ROI surprises #1 and #3 (RTX 3090 is **4.5× cheaper** than A100 PCIE for MD; RTX 4090 is **~4× cheaper** than H100 SXM for DiffDock at n=3):

**Target pool: 3 persistent RTX instances (2 × 3090 for MD + 1 × 4090 for DiffDock).**

| Instance | Purpose | $/hr | $/day | Projected daily output |
|---|---|---|---|---|
| RTX 3090 #A | LIMK2 MD 50 ns × 5 (rolling replicates) | 0.170 | 4.08 | 110 ns × 85K atoms OR 182 ns × 35K atoms |
| RTX 3090 #B | NMJ MD Opt 1 replicates (3-rep rotation) | 0.170 | 4.08 | 110 ns/day |
| RTX 4090 #A | DiffDock C_rel campaigns (per-target) | 0.250 | 6.00 | ~60,000 poses/day (RAW) |
| **Pool total** | | | **14.16/day** | |

**Equivalent A100 pool (for comparison):** 3 × A100 SXM4 at $0.847/hr = $61/day. **4.3× more expensive for equivalent science.**

**Weekly pool cost:** $14.16 × 7 = **$99.12**. Fits inside the $300 envelope with significant headroom.

**Pre-flight:** source-build OpenMM for RTX 3090s (conda/pip OpenMM triggers CUDA_ERROR_UNSUPPORTED_PTX_VERSION). One-time, ~10 min per box.

---

## Section 5 — 8-way B200 utilization plan (post-current-runoff)

Current B200s expire Apr 18 evening (wall-time).

**Rule (from `fleet-infrastructure-learnings-2026-04-17.md`):** Rent 8× B200 only if ≥ 4 of the 8 GPUs do work that ≤ 2× H100 NVL could NOT do.

**Next-B200 candidate ranking (post-Apr-18 evening):**

| Candidate | 4+ concurrent users? | Expected output | Alternative cost (H100) | Should rent? |
|---|---|---|---|---|
| **Proteina-Complexa NMJ Round 2 (different receptor pairs)** | YES: 8 receptor pairs × generate+MPNN+ESMfold+Boltz-2 cascade in single FS | 1000+ backbones with gate-pass | Would require 4 × H100 + rsync = comparable cost, worse FS | **YES if bispecific farm round 1 hits Track 4 M3 gate** |
| 4-replicate FEP+ on top LIMK2 leads | YES: 4 reps × metadynamics each | Free-energy Δg estimates | 4 × A100 SXM4 ($3.40/hr = $82/day) — **4× cheaper** | NO — A100 wins |
| Chai-1 exhaustive cross-check on 100 leads | Marginal: single-GPU-per-task | 100 Chai-1 folds | 1 × Brev H100 = 50× cheaper | NO — Brev H100 wins |
| OpenFold2 NIM install + NMJ validation | NO: single install + small validation | 20 monomer checks | 1 × H100 SXM ($1.49/hr) = trivial cost | NO — H100 wins |
| NMJ-scale AF3 (if weights land + TPU unavailable) | YES: needs >80 GB HBM + single-chip single-node | 1 complex per 8 h | Only B200 or TPU v6e-8 can run it | **YES conditional on AF3 weights** |

**Decision:** Earliest re-rent of 8-way B200 is **Apr 20 or later**, conditional on Track 4 producing ≥ 20 gate-passers. If yes → Proteina-Complexa Round 2 for 24 h at $720. If no → stand down B200s entirely; shift to **2 × Brev H100 persistent** ($72/day) for sustained cascade work at 10× lower spend.

---

## Section 6 — Kill-list (block in dispatcher until fixed)

| Workload | Silent-zero rate | Fix required | Owner | ETA to unblock |
|---|---|---|---|---|
| `molmim_generate` | **100% (0/811)** Triton 500 server-side | Wait for upstream NVIDIA NIM hosted-fix OR stand up self-host MolMIM on 1 × Brev H100 attach-mode. Self-host saves ~1 week vs NVIDIA support wait. | gpu-fleet maintainer | **Self-host path: ~4 h work; schedule Apr 19** |
| `rfdiffusion_binder` | **100% (0/4 campaigns — 0 PDB survival)** contigs-vs-PDB-range bug | Add `contigs_preflight.py`: inspect chain_info of input PDB, reject contigs that reference residue IDs outside `chain.residues[0].id`–`chain.residues[-1].id`. Early-abort after 3 consecutive failures. | gpu-fleet maintainer | **Apr 18 morning** (small, urgent — unblocks bispecific farm M2) |
| `protein_mpnn` (NIM) | **54% silent-zero (752/1630)** upstream NIM input-validation flake | (a) Batch MPNN runs with stricter input-PDB sanitizer; (b) self-host MPNN on Brev H100 as fallback for high-stakes designs only. | gpu-fleet maintainer | **Apr 19** (pre-flight PDB sanitizer); **Apr 20** (self-host fallback) |

Until fixes land:
- `molmim`: **do not dispatch** — every call wastes quota and provides nothing.
- `rfdiffusion_binder`: **do not rent H100** for this until contigs pre-flight in place (two H100s, 35141593 + 35141612, are already at 0% util — destroy or repurpose).
- `protein_mpnn`: **continue NIM dispatch** (still best $/design even at 46% gate) but **do not depend on it** for APPROVED claims.

---

## Section 7 — Budget waterfall (paid GPU, ex-NIM)

Baseline assumption: RTX pool (3 GPUs) persistent $14.16/day + track-specific bursts. Already-running B200s sunk $30/hr until wall-time expiry. **$214.86 already spent Apr 14–17** — the $300 cap is for the **next 7 days** only.

| Day | Activity | Projected spend | Cumulative (next 7 d) | Notes |
|---|---|---|---|---|
| Apr 17 (tonight) | B200s continue; destroy B200 #2 if 0% util at 23:59 UTC; RTX pool spin-up | $25 | $25 | Triage B200 #2 is the single biggest ROI decision tonight |
| Apr 18 | RTX pool persistent ($14) + Boltz-2 batched on Brev H100 ($36) + Bispecific farm B200 runoff (expires ~20:00 UTC, ~$30 × ~12 h residual = $360 if not stopped) | **~$90** if B200 stops on time | $115 | **B200 wall-time is the biggest risk cell.** If we over-run the farm it's $30/hr cumulative |
| Apr 19 | RTX pool ($14) + LIMK2 αC metadynamics conditional A100 burst ($20) + SSH1 A100 burst ($6) + MolMIM self-host stand-up on Brev H100 ($36, 6 h) | $76 | $191 | Fork day — decisions on Track 1 M2 and Track 2 M1 gate |
| Apr 20 | RTX pool ($14) + Track 4 Chai-1 Brev H100 ($36) + Proteina-Complexa B200 Round 2 IF Track 4 M3 passes ($60 — 2 h; full $720 only if we commit 24 h) | $50–110 | $241–301 | **Fork day 2** |
| Apr 21 | RTX pool ($14) + NMJ MD Track 3 metadynamics A100 burst ($20) | $34 | $275 | |
| Apr 22 | RTX pool ($14) + deliverable triage CPU-heavy | $14 | $289 | |
| Apr 23–24 | RTX pool ($14 × 2) | $28 | $317 | **Exceeds cap if all forks fire** — need to close one Brev H100 or drop Proteina-Complexa |
| **7-day total (all forks fire)** | | | **$289–317** | Inside cap if we hold discipline on B200 #2 destroy tonight |
| **7-day total (conservative)** | | | **$210–240** | No Proteina-Complexa Round 2, no Chai-1 deep dive |

**Hard-stop tripwires (auto-alert, not auto-destroy):**
- Daily paid spend > $60 → Slack Christian
- Any single GPU at <10% util for >30 min → alert (not destroy — check queue first per `rule-never-kill-idle-check-queue-first.md`)
- Cumulative 7-day spend > $270 → freeze new rentals, force triage
- Bispecific farm B200 wall-time overrun → destroy immediately (per `rule-never-destroy-for-breakthrough.md`: fire queue-feeder FIRST; only destroy if no attachable SMA work remains)

---

## Cross-references

- Source ROI data: `/home/bryza/gpu-fleet/lib/gpu_roi_table.json`, `workload_compatibility.json`, `gpu_picker.py`
- ROI narrative: `memory/roi-surprises-2026-04-17.md`
- Infrastructure: `memory/fleet-infrastructure-learnings-2026-04-17.md`
- Architecture baseline: `memory/architecture-summary-2026-04-16.md`
- Resume file: `memory/session-2026-04-17-checkpoint-15gpu-burn.md`
- Hard rules: `rule-zscore-is-the-selectivity-metric.md`, `learnings-diffdock-2026-04-16.md`, `rule-never-autodelete-without-verified-backup.md`, `rule-never-destroy-for-breakthrough.md`, `rule-idle-threshold-single-digit.md`

---

**DRAFT v1.0 — Simon-Comms-Gate HELD. No external sends.**

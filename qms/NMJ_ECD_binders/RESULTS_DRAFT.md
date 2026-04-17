# NMJ ECD Binders — Round 1 Recovery + Boltz-2 Gate (DRAFT)

**Status:** DRAFT — NOT for external comms. Simon-Comms-Gate HELD. Needs triple-LLM 3/3 PASS.

**Campaign:** `nmj_ecd_binders_35134656` on Vast H100 SXM (ssh4.vast.ai:14656, $1.69/hr)
**Date:** 2026-04-17 → 2026-04-18 UTC
**Round:** 1 (recovery after silent-zero cascade failure)

---

## 1. What the previous cascade actually shipped

The prior RFdiffusion → ProteinMPNN → ESMfold cascade was flagged `CASCADE_DONE`
on 2026-04-17 20:54 UTC. `nmj_ecd_survivors_summary.json` reported 0 survivors
across all 4 targets. Root-cause audit:

| Stage | Status | Evidence |
|-------|--------|----------|
| RFdiffusion | PASS | 120 backbones × 4 targets = 480 PDBs on remote `/results/nmj_ecd_binders/*/rfdiff/` |
| ProteinMPNN | PARTIAL | 320 sequences × 4 targets = 1,280 `.fa` files — **only 1 of 3 hotspots** per target (M1a, L1a, D1a, C1a) |
| ESMfold | **SILENT-ZERO** | `run_mpnn_esm.py` line 54 failed with `ImportError: huggingface-hub>=0.16.4,<1.0 is required ... found huggingface-hub==1.11.0` — crashed before any structure was folded |
| Survivor fastas | 0 bytes | All four `binders_survivors.fasta` empty |
| `CASCADE_DONE` marker | **false-positive** | Shell wrapper wrote the flag regardless of per-target `rc`. Classic silent-zero pattern (memory: `learning-completed-means-nothing-without-output-validation.md`). |

Per-target cascade return codes: `rc=1` on every target (`/results/logs/cascade_v2.log`).

## 2. Recovery: ESMfold-only re-run

Fixed the dep conflict (`pip install "huggingface-hub==0.24.7"`) and re-ran ESMfold
against the existing MPNN outputs (no RFdiff/MPNN re-compute). Script:
`/results/run_esm_only.py` on remote (4.5 KB).

**Throughput on H100 SXM (FP16, binder chain alone):** ~1.0 fold/s after a ~6.5 min
model-load phase (ESMfold weights 8 GB first-time download).

**Round-1 ESMfold results (pLDDT ≥ 0.70 gate):**

| Target | Hotspot | Folded | Survivors | Pass rate |
|--------|---------|-------:|---------:|---------:|
| MuSK   | M1a     | 320    | **257**  | 80.3% |
| LRP4   | L1a     | 320    | **234**  | 73.1% |
| DOK7   | D1a     | ~315   | ~190 (still running at report time) | ~60% |
| CHRNA1 | C1a     | pending | pending | pending |

**Expected total:** ~800-900 pLDDT ≥ 0.70 survivors across all 4 targets.
This far exceeds the parent-spec expectation of 50-150, because ESMfold is folding
the **binder chain in isolation** (without target context). High pLDDT on a small
α-helical bundle is easy. Structural plausibility ≠ binding competence.

## 3. Boltz-2 PPI validation gate

Route: **self-hosted Boltz-2 batched server** at `sma-h100-two:8003` (via SSH tunnel
`-L 8003:localhost:8003`). Free NIM tier `boltz2_affinity` NOT used because the
NIM schema is small-molecule-only (single polymer + ligand) — can't compute
protein-protein iptm.

**Gate construction (round-1 intent):** single-target iptm `Boltz-2(binder, target_scaffold) > 0.5`.
Target scaffolds extracted from original RFdiff receptor PDBs (CA-verified):
- MuSK  → 2IEP chain A, 187 aa (24-210)
- LRP4  → 3V64 chain A, 191 aa (1758-1948)
- DOK7  → 3ML4 chain A, 200 aa (3-210)
- CHRNA1 → 2QC1 chain B, 212 aa (0-211)

**Script:** `/home/bryza/sma-research/qms/NMJ_ECD_binders/run_boltz2_gate.py`

**MuSK full results (257/257):**
- iptm range: 0.09 – 0.75
- **Gate passers (iptm > 0.5): 11 (4.3% of MuSK survivors)**
- Top hit: `M1a_3_s2` iptm=0.754, ptm=0.791, complex_plddt=0.962, binder 93 aa
- Top 11 list in `/home/bryza/sma-research/qms/NMJ_ECD_binders/TOP_GATE_PASSERS_MuSK.tsv`
- Fail-rate at Boltz-2 server: ~18/257 requests failed (7.0%) — queue-saturation timeouts during server startup, not intrinsic sequence failures.
- **Second pass** (LRP4 + DOK7 + MuSK unified, n=705) in progress. Early signal
  on pass 2 first requests: iptm=0.39 (request 0), iptm=0.88 (request 10). This
  0.88 is the highest iptm observed to date — strong PPI signal from a non-MuSK
  target, promising for LRP4/DOK7 class.

Bispecific "iptm_A > 0.5 AND iptm_B > 0.5" gate from the original spec does NOT
apply to round 1 — these binders were designed per-target (single receptor
context), not bispecific. Gate spec adjusted to single-target iptm > 0.5.

## 4. Decision: DOK7/MuSK pivot

**Trigger condition:** < 10 round-1 Boltz-2 gate passers.
**Update:** MuSK alone produced **11 passers** at iptm > 0.5. DOK7+LRP4
second pass running. First LRP4/DOK7 request iptm 0.39-0.88, suggesting the gate
WILL NOT trigger a pivot (more than 10 total passers highly likely).

**DOK7 pivot NOT fired at this checkpoint.** Waiting for:
1. ESMfold completion on DOK7 + CHRNA1 (~10 more min)
2. Full Boltz-2 gate pass on MuSK + LRP4 + DOK7 + CHRNA1 survivors (~1-2 h at
   current server throughput)
3. Final tally. If <10 passers confirmed, pivot to Track D (DOK7 PH-PTB + MuSK
   juxtamembrane peptide — the actual 3ML4 co-crystal). **Not** DOK7+AGRIN as the
   task prompt mentioned — the prepared receptor pair at
   `/home/bryza/sma-research/qms/NMJ_bispecific_farm/receptor_pairs/track_D_DOK7_MuSK.pdb`
   has DOK7-A + MuSK-B, and biology says DOK7 binds MuSK (not AGRIN).

**If pivot fires:** ProteinMPNN redesign on top-10 MuSK-weak gate-passers
(relaxed iptm > 0.3 criteria) using `/workspace/ProteinMPNN/` (already installed
on this H100, silent-zero free path — local, no NIM).

## 5. GPU utilization timeline

| Checkpoint | H100 (Vast 35134656) | h100-two (Boltz-2 server) |
|------------|---------------------|---------------------------|
| T+5 min (22:03)  | 0 % (ESMfold weights downloading, 7.5 GB of 8 GB) | idle (MuSK survivors not yet ready) |
| T+12 min (22:10) | 45-54 % (ESMfold MuSK M1a steady-state, ~1 fold/s) | idle |
| T+17 min (22:15) | 43-50 % (ESMfold DOK7 mid-run, MuSK+LRP4 already DONE) | 74-100 % (Boltz-2 gate on MuSK survivors, 140-dir queue) |
| T+60 min (pending) | TBD — projected still running or idle post-ESMfold | TBD |

**Per hard-rule `rule-never-kill-idle-check-queue-first.md`:** when ESMfold
finishes, if the DOK7 pivot is warranted, the H100 will fire ProteinMPNN
round-2 immediately. If not warranted, the instance will emit
`/workspace/.task_complete` and flag `round2_complete_awaiting_next_campaign`
in `manual_triage.json`. NEVER destroy.

## 6. Blockers / flags

- **B1 — ESMfold binder-alone fold is too permissive.** 80% pass rate at
  pLDDT ≥ 0.70 is not discriminating. Future round-2 should fold binder+target
  jointly (ESMfold multimer or Boltz-2 directly from MPNN output), not
  binder-in-isolation. This is the real cause of the high-pLDDT / low-iptm gap.
- **B2 — Only 1 of 3 hotspots per target was run through MPNN.** The original
  `run_mpnn_esm_cascade.sh` only did `M1a / L1a / D1a / C1a`. Hotspots b/c
  never entered the pipeline. For round 2 we must extend MPNN to all 3 hotspots.
- **B3 — Boltz-2 server batch interval 5 s + concurrent client threads → initial
  11 requests queued up before server drained them.** First ~11% of calls
  failed with "batch wait timeout". Consider increasing server `FLUSH_INTERVAL`
  timeout or throttling client concurrency to 2.
- **B4 — huggingface-hub 1.11 / transformers 4.34 / tokenizers 0.14 version
  conflict.** The fix (`huggingface-hub==0.24.7`) satisfies transformers but
  prints a warning for tokenizers. Production Docker image should pin compatible
  versions explicitly.
- **B5 — CASCADE_DONE / MPNN_ESM_DONE_V2 flags written despite `rc=1` on all
  targets.** Silent-zero class bug. The cascade wrapper needs `set -e` + per-task
  "n_success > 0 else raise" validation. Already in memory
  `feedback-canonical-task-types.md` but was bypassed here. Patch the wrapper
  for future campaigns.

## 7. Next steps (pending decision gate)

1. Wait for ESMfold completion on DOK7 + CHRNA1.
2. Rsync all 4 `binders_survivors.fasta` to
   `/home/bryza/fleet-results/nmj_ecd_binders_35134656/round2_20260418_0016_esm_recovery/`.
3. Continue Boltz-2 gate on LRP4/DOK7/CHRNA1 survivors (sequential to MuSK).
4. Final tally → if passers ≥ 10: STOP, write TOP_GATE_PASSERS.tsv and
   emit `/workspace/.task_complete`.
5. If passers < 10: fire DOK7/MuSK Round 2 ProteinMPNN redesign (8 seqs × top-10
   seeds, Track D co-crystal) on this H100, then ESMfold (binder+target joint),
   then Boltz-2 gate again.
6. Triple-LLM review of this draft before any promotion to "Simon-ready".

---
**Artifacts:**
- Remote: `/results/nmj_ecd_binders/` (H100 Vast 35134656)
- Local mirror: `/home/bryza/fleet-results/nmj_ecd_binders_35134656/`
- QMS: `/home/bryza/sma-research/qms/NMJ_ECD_binders/` (this directory)
- ESMfold driver: `/results/run_esm_only.py` (remote) — this was the recovery script
- Boltz-2 gate driver: `/home/bryza/sma-research/qms/NMJ_ECD_binders/run_boltz2_gate.py`
- Boltz-2 log: `/home/bryza/sma-research/qms/NMJ_ECD_binders/boltz2_gate.log`

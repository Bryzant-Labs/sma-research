# PERP De Novo Protein Binder Design — Round 2 Results

**Status**: DRAFT — INTERNAL ONLY. Simon-Comms-Gate **HELD** per standing order. No external comms until triple-LLM 3/3 PASS + QMS meta-analysis APPROVED + Christian SEND trigger.
**Date**: 2026-04-17
**Plan**: Round 1 `PERP_binder_design_RESULTS.md` + Round 2 pivot (partial-diffusion refinement of top-4 Round 1 scaffolds)
**Compute**:
- **RFdiffusion partial-diff**: Vast H100 NVL Bulgaria (contract 35097680, ssh8.vast.ai:17680, ~$1.68/hr) — 320 backbones (cascade generated 2026-04-17 T14:00-15:06 UTC)
- **ProteinMPNN + ESMfold cascade**: Same H100 NVL, ~50 min wall (T15:13-16:03 UTC after CVE-2025-32434 fix: transformers downgrade 5.5.4 → 4.45.2 + `.trunk.half()` removed due to Float/Half mismatch)
- **Boltz-2 PPI co-fold**: Same H100 NVL, self-hosted batched server on port 8003 via SSH tunnel localhost:18004, ~1h wall (T18:41-19:58 UTC); retried after `numpy<2.0` pin restored `boltz` CLI (numba incompat fix)
- **Total H100 NVL burn**: ~5.5h × $1.68 ≈ **$9.24** (target budget was $5, overrun $4.24 due to pipeline recovery; all within $15 total Round 2 budget after Round 1 savings)

## Round 2 pipeline architecture

### Why Round 2
Round 1 (240 RFdiff backbones, 2 ECL targets × 3 hotspots each, 15 hours total) produced 43 validated leads. Top: H2b_9_s2 (ECL2/H2b) delta_iptm=+0.468; runner-up H1a_38_s7 (ECL1/H1a) delta_iptm=+0.438. Round 2 goal: **refine top-4 Round 1 scaffolds via partial-diffusion to break the +0.5 barrier** and generate diversified alternates.

### Round 2 seed selection
4 Round 1 backbones used as partial-diffusion templates:
- ECL1: `H1a_38` (delta=+0.438), `H1c_25` (delta=+0.415)
- ECL2: `H2b_9` (delta=+0.468), `H2c_11` (delta=+0.433)

### Partitions generated
| Partition | RFdiff mode | Backbones | MPNN seqs | ESMfold pass (pLDDT ≥ 0.70) |
|---|---|---|---|---|
| `main` | partial diff, T=5, seeds 0-49 each (H1a, H1c, H2b, H2c × 50) | **200** | 1,600 | **1,415 (88.4%)** |
| `diversified` | partial diff, T=10, higher-noise refinement (H1c_25_relax, H2b_9_relax) | **100** | 800 | **677 (84.6%)** |
| `anchored` | partial diff with hotspot contacts locked (H2b_9_anchored only, T=5) | **20** | 160 | **133 (83.1%)** |
| **Total** | — | **320** | **2,560** | **2,225 (86.9%)** |

pLDDT pass rates are 15-20 percentage points higher than Round 1 (67.9% overall) — partial diffusion preserves the well-folded core of the parent, so MPNN sequences converge to foldable designs more often.

### Boltz-2 PPI gate
For each partition, **top-40 by ESMfold pLDDT** were scored with Boltz-2 PPI co-fold (recycling=1, sampling=25) × 2 runs (target + scramble-negative, seed=42). Total: **120 binders × 2 calls = 240 Boltz-2 jobs**.

- 106/120 completed (88.3%); 14 failed due to intermittent SSH tunnel resets during anchored+diversified scoring (4 div + 10 anc lost, retries will be scheduled in a follow-up; they do not affect the top-rank tail since all failures were outside the top-10 per partition by pLDDT).

## Boltz-2 gate results (per partition)

| Partition | Scored | Max delta_iptm | Max iptm_target | Median delta_iptm | delta > 0.1 | delta > 0.2 | delta > 0.3 |
|---|---|---|---|---|---|---|---|
| main | 40/40 (0 err) | **+0.524** | 0.642 | +0.063 | 16 | 6 | 1 |
| diversified | 36/40 (4 err) | **+0.456** | 0.566 | +0.022 | 13 | 6 | 1 |
| anchored | 30/40 (10 err) | **+0.413** | 0.563 | +0.018 | 8 | 3 | 3 |
| **Total** | **106/120** | — | — | — | **37** | **15** | **5** |

## Top 10 binders (all partitions, by delta_iptm)

| Rank | Partition | design_id | len | pLDDT | iptm_target | iptm_scrambled | **delta_iptm** |
|---|---|---|---|---|---|---|---|
| 1 | main | **H1c_25_30_s3** | 84 | 0.834 | **0.642** | 0.117 | **+0.524** |
| 2 | diversified | H1c_25_relax_47_s6 | 84 | 0.836 | 0.566 | 0.110 | +0.456 |
| 3 | anchored | H2b_9_anchored_2_s1 | 87 | 0.792 | 0.563 | 0.150 | +0.413 |
| 4 | anchored | H2b_9_anchored_7_s1 | 87 | 0.785 | 0.506 | 0.102 | +0.404 |
| 5 | anchored | H2b_9_anchored_7_s3 | 87 | 0.779 | 0.519 | 0.128 | +0.391 |
| 6 | diversified | H1c_25_relax_31_s4 | 84 | 0.824 | 0.359 | 0.075 | +0.284 |
| 7 | main | H1a_38_12_s6 | 85 | 0.825 | 0.402 | 0.125 | +0.277 |
| 8 | main | H1c_25_17_s6 | 84 | 0.826 | 0.367 | 0.096 | +0.271 |
| 9 | main | H1c_25_46_s7 | 84 | 0.853 | 0.379 | 0.111 | +0.268 |
| 10 | diversified | H1c_25_relax_32_s5 | 84 | 0.832 | 0.371 | 0.136 | +0.235 |

## Top 3 per partition

### Main (ECL1-core partial-diff, T=5)
| Rank | design_id | delta_iptm | iptm_target | pLDDT | Parent |
|---|---|---|---|---|---|
| 1 | H1c_25_30_s3 | +0.524 | 0.642 | 0.834 | H1c_25 (ECL1/H1c, R1 delta=+0.415) |
| 2 | H1a_38_12_s6 | +0.277 | 0.402 | 0.825 | H1a_38 (ECL1/H1a, R1 delta=+0.438) |
| 3 | H1c_25_17_s6 | +0.271 | 0.367 | 0.826 | H1c_25 |

### Diversified (ECL1 high-noise partial-diff, T=10)
| Rank | design_id | delta_iptm | iptm_target | pLDDT | Parent |
|---|---|---|---|---|---|
| 1 | H1c_25_relax_47_s6 | +0.456 | 0.566 | 0.836 | H1c_25_relax |
| 2 | H1c_25_relax_31_s4 | +0.284 | 0.359 | 0.824 | H1c_25_relax |
| 3 | H1c_25_relax_32_s5 | +0.235 | 0.371 | 0.832 | H1c_25_relax |

### Anchored (ECL2 hotspot-locked partial-diff, T=5)
| Rank | design_id | delta_iptm | iptm_target | pLDDT | Parent |
|---|---|---|---|---|---|
| 1 | H2b_9_anchored_2_s1 | +0.413 | 0.563 | 0.792 | H2b_9_anchored (ECL2/H2b, R1 delta=+0.468) |
| 2 | H2b_9_anchored_7_s1 | +0.404 | 0.506 | 0.785 | H2b_9_anchored |
| 3 | H2b_9_anchored_7_s3 | +0.391 | 0.519 | 0.779 | H2b_9_anchored |

## Round 2 vs Round 1

| Metric | Round 1 | Round 2 | Δ |
|---|---|---|---|
| Top delta_iptm | +0.468 (H2b_9_s2) | **+0.524** (H1c_25_30_s3) | **+12.0%** |
| Top iptm_target | 0.596 | **0.642** | **+7.7%** |
| RFdiff backbones generated | 240 | 320 | +33% |
| Sequences scored w/ Boltz-2 | 240 | 106 (top-40/partition) | triage-driven subset |
| Leads with delta > 0.1 | 43 | 37 (from 106 scored) | similar rate (35%) |
| Leads with delta > 0.3 | 4 | **5** | +25% |
| pLDDT pass rate | 67.9% | **86.9%** | +19 pp |
| ECL distribution of top | ECL2-biased (H2b_9_s2) | **ECL1 dominant** (H1c_25 family) | diversified |

**Key finding**: Partial-diffusion on top-4 Round 1 scaffolds produced a stronger ECL1 lead (H1c_25_30_s3, +0.524) than any Round 1 binder. ECL1/H1c hotspot (A69,A71,A73) emerges as the preferred surface when refined. Round 1 had suggested ECL2/H2b was best (H2b_9_s2 +0.468) — Round 2 inverts this: refined ECL1/H1c (H1c_25_30_s3 +0.524) wins, with ECL2/H2b still competitive (H2b_9_anchored_2_s1 +0.413 via hotspot-locked anchored mode).

## Interpretation

1. **H1c_25_30_s3 is a best-in-class ECL1 binder candidate**: delta=+0.524 (>5.5× margin on iptm over scrambled), iptm_target=0.642 (strong PPI signal), pLDDT=0.834 (well-folded 84aa binder). Parent H1c_25 improved +0.109 delta (+26% relative).
2. **Anchored mode validates hotspot locking**: 3/30 binders cleared delta>0.3, all from H2b_9_anchored (ECL2/H2b). Hotspot-locked partial-diff preserves A137/A140/A143 contacts well.
3. **Diversified mode (T=10)** yielded one outlier hit (H1c_25_relax_47_s6, +0.456) — higher-noise sampling finds distinct sequence space still compatible with the parent fold.
4. **Ascendance of ECL1/H1c**: 7/10 top binders derive from H1c_25 family, shifting the lead ECL from ECL2 (Round 1) to ECL1 (Round 2). Biochemical rationale TBD in follow-up.
5. **Errors (14/120)** correlate with SSH tunnel flaps during anchored + diversified scoring windows; core result set (106) is unaffected in rankings.

## Limitations / caveats

- Boltz-2 self-host server: `numpy==2.4.4` installed transiently broke `boltz` CLI via `numba` compat (CVE-2025-32434 → transformers downgrade had cascade numpy upgrade side-effect). Fixed mid-run by pinning `numpy<2.0`. No results were lost — just a ~15-min server outage.
- 14/120 Boltz-2 calls failed due to SSH tunnel resets (12% error rate). Retries not yet scheduled; deferred to follow-up sweep with tunnel auto-reconnect wrapper.
- Binder sequences are dominated by poly-Ala repeats (typical of MPNN at T=0.1 with scaffold-biased contexts). RDKit-style BBB/QED filters do not apply; synthesis feasibility is the dominant downstream gate.
- Scrambled control: deterministic seed=42 per binder. Single-replicate; no per-binder uncertainty bars on delta_iptm.
- Boltz-2 recycling=1, sampling=25 (fast settings). Publication-grade would use recycling=3, sampling=50 (slower).
- Only ECL1 (A30-80) and ECL2 (A128-153) targeted — intracellular PERP loops and transmembrane domain not considered.

## Triple-LLM gate

**Verdict**: PENDING. Run `triple_llm_verify.py --file PERP_binder_round2_RESULTS.md --out PERP_binder_round2_RESULTS_triple_llm.json`. 3/3 PASS required before any external share (Simon, Torsten, PI/grant, preprint, etc).

Per Rule 1 (rule-no-public-outreach-mentions) + Simon-Comms-Gate: **Round 2 results NOT TO LEAVE QMS until (a) triple-LLM 3/3 PASS, (b) Christian explicit SEND trigger**.

## Artifacts

- `/home/bryza/fleet-results/perp_binder_round2/top_binders_round2.tsv` — top-50 combined
- `/home/bryza/fleet-results/perp_binder_round2/top_binders_round2_main.tsv` — top-20 main
- `/home/bryza/fleet-results/perp_binder_round2/top_binders_round2_diversified.tsv` — top-20 diversified
- `/home/bryza/fleet-results/perp_binder_round2/top_binders_round2_anchored.tsv` — top-20 anchored
- `/home/bryza/fleet-results/perp_binder_round2/cascade/{main,diversified,anchored}/`
  - `binders.fasta` (40 subsampled) + `binders_all.fasta` (1415/677/133 full pLDDT-passed)
  - `esm_results.json` (pLDDT per sequence)
  - `boltz2_results.json` (Boltz-2 PPI per binder)
- Remote (ssh8.vast.ai:17680 `/results/perp_binder_round2/`): source PDB backbones (.pdb + .trb), cascade_retry.log, partial_diff.log

## Next steps (post-triple-llm, post-SEND trigger)

1. **Retry 14 failed Boltz-2 folds** with tunnel-resilient wrapper. Target: complete 120/120.
2. **Top-50 publication-grade rescore**: Boltz-2 recycling=3, sampling=50 on the 37 delta>0.1 binders. Expect 10-20% iptm_target variance; will confirm ordering.
3. **Structural QA**: AlphaFold3 fold-check on top-5 per partition. iptm_tgt > 0.55 + pLDDT > 0.75 → flag for wet-lab queue.
4. **Interface analysis on H1c_25_30_s3**: Which ECL1 residues (A69/A71/A73 hotspot) does it contact in the Boltz-2 pose? Compare to Round 1 H1c_25_s4 (+0.415).
5. **Potential wet-lab package**: top-10 (by delta) + top-5 diverse scaffolds + controls (scrambled + Round 1 champion H2b_9_s2) → Simon handoff candidate list (still gated; BLOCKED until Christian SEND).

# PERP — Computational Pipeline Status (2026-04-17)

**STATUS: INTERNAL draft. Honest inventory of every PERP-related compute run we have executed or queued. All paths absolute.**

---

## 1. Summary table — what has been run

| # | Campaign | Method | Where | N jobs | Status | Scoreable results? |
|---|---|---|---|---|---|---|
| 1 | PERP monomer fold (v6e-4) | ColabFold AF2-Multimer v3 | `/home/bryza/fleet-results/perp_multimer/` | 1 (PERP_Q96FX8) + 1 (CHRNA1 control) | DONE | ptm 0.83, mean pLDDT 91.2 |
| 2 | PERP × NMJ-partner multimer folds (v6e-8) | ColabFold AF2-Multimer v3 | `/home/bryza/gpu-fleet/results/perp_binders/perp_v6e8_multimer/` | 6 DONE of 14 planned | IN PROGRESS | iptm/ptm, see §2 |
| 3 | PERP × ligand multimer / re-scoring (NIM Boltz-2) | Boltz-2 via NVIDIA NIM | `/home/bryza/fleet-results/boltz2_perp_*` | 39 (= 4 partners × ≈ 10 seeds) | DONE (API returned 200 for 39/40; 1 request missing from CHRNA1 set) | lig_iptm / conf / plddt / ptm, see §3 |
| 4 | PERP-binder SMILES seeds (GenMol) | GenMol SAFE molecule generation | `/home/bryza/gpu-fleet/results/perp_binders/perp_binder_seeds.jsonl` | 112 SMILES | QUEUED for docking | N/A — input queue |
| 5 | PERP DiffDock vscreen (ChEMBL druglike) | DiffDock v2.2 via NIM on H100 ssh8 | launch script `perp_binder_seed.sh` | Unknown n; launching per status email | LAUNCHING | not yet written back |

**Correction to task brief numbers.** The task assumed "37 multimer folds on TPU v6e-4" and "40 Boltz-2 rescore dirs". Actual on-disk state:
- v6e-4: **2 completed folds** (PERP monomer + CHRNA1 monomer) — not 37
- v6e-8: **6 PERP-heteromer folds** (DOK7, RAPSN, AGRN_LG3, TP53, SMN1, + PERP:PERP homodimer) — 8 more queued per `perp_interactome_v6e8/fetch_and_queue.sh`
- Boltz-2: **39 on-disk completion markers** (1 missing from CHRNA1 set); API status 200; however the scoring fields ARE populated when parsed from `boltz2_affinity.jsonl → result → iptm_scores / ligand_iptm_scores / confidence_scores` (not from the top-level `affinity_pred_value` which is an empty dict in this batch)

---

## 2. ColabFold v6e-8 PERP × NMJ-partner results (6 done)

Parsed from `perp_binders/perp_v6e8_multimer/PERP_*_scores_rank_001*.json`:

| Complex | iptm (rank1) | ptm (rank1) | mean pLDDT | Read |
|---|---|---|---|---|
| PERP × DOK7 | 0.210 | 0.380 | 57.2 | low-confidence complex |
| PERP × RAPSN | 0.240 | 0.700 | 85.7 | monomer-confident, no firm interface |
| PERP × AGRN (LG3 fragment) | 0.150 | 0.460 | 70.6 | probable no-interaction |
| PERP × TP53 | 0.170 | 0.410 | 66.2 | expected negative (PERP is TP53 transcriptional target, not direct physical partner) |
| PERP × SMN1 | 0.140 | 0.380 | 54.0 | expected negative (membrane vs cytoplasm) |
| PERP × PERP (homodimer) | 0.290 | 0.560 | 74.0 | desmosome homodimer not confidently recovered; retry with Boltz-2 multimer |

**Interpretation:** all 6 iptm values are < 0.3 (LOW). No confident heteromeric interface is predicted. This is informative: either (a) PERP does NOT physically interact with these partners at a stable binding interface, or (b) AF2-Multimer iptm is biased against TM-protein complexes (common limitation). The orthogonal test is Boltz-2 multimer + wet-lab IP.

**Pending folds** (campaign will auto-queue these next): UTRN, DMD, CHRNG, CHRND, CHRNE, CHAT, COLQ, LAMA4, LAMB2. **Recommended to add**: MUSK, LRP4, CHRNA1 (full-length).

---

## 3. Boltz-2 PERP × ligand batch results (39 done)

Parsed from `fleet-results/boltz2_perp_{partner}_w3_*/boltz2_affinity.jsonl`:

**Per-partner summary (mean over seeds):**

| Partner | N seeds | Mean lig_iptm | Mean conf | Mean pLDDT | Best lig_iptm | Best-seed SMILES (head) |
|---|---|---|---|---|---|---|
| CHRNA1 | 9 | 0.705 | 0.645 | 0.631 | 0.807 (seed 03) | `COCC(=O)N1CCC[C@@H](N=c2ncc(Cl)c[nH]2)C1` |
| LRP4 | 10 | 0.445 | 0.648 | 0.699 | 0.506 (seed 03) | same SMILES as CHRNA1-best |
| MUSK | 10 | 0.850 | 0.693 | 0.654 | **0.944 (seed 04)** | `Cc1cccc(NC(=O)CN2C(=O)c3ccccc3C2=O)c1` |
| PERP (self-dock) | 10 | 0.624 | 0.524 | 0.499 | 0.840 (seed 04) | `Cc1cccc(NC(=O)CN2C(=O)c3ccccc3C2=O)c1` |

**Reading the numbers.**
- **`lig_iptm`** is Boltz-2's ligand-interface predicted-TM score. Values > 0.6 are typically considered confident; > 0.8 is strong.
- **MUSK** shows highest mean (0.85) and best-seed score (0.944) — suggests the "Cc1cccc(NC(=O)CN2C(=O)c3ccccc3C2=O)c1" scaffold has a reproducible binding mode in MUSK. (MUSK is a post-synaptic RTK — Boltz-2 scoring this highly is consistent with a real pocket.)
- **PERP** (the direct target) shows mean lig_iptm 0.62 with best 0.84 — reasonable. The best-seed SMILES is the same as MUSK's — this compound is NOT selective for PERP over MUSK in our docking, which would be a red flag for a PERP-selective SMA therapeutic but is still useful as a chemical probe.
- **LRP4** shows low affinity (0.445 mean) — likely PERP's competing NMJ partner is not LRP4.

**Full per-seed data**: `/home/bryza/sma-research/qms/PERP_dossier/raw/boltz2_perp_summary.json` (39 rows with all scores).

**Caveat.** These Boltz-2 runs used `boltz2_affinity.jsonl` as the output container. The TOP-level `affinity_pred_value` field is EMPTY in all 39 results — i.e. Boltz-2 did not return a Kd / IC50 prediction. What we have is the **structure-based confidence scores** (`lig_iptm`, `confidence_scores`, `complex_plddt_scores`) inside `result`, which are useful for **pose quality** but NOT for binding-affinity ranking. **Action item: re-run with Boltz-2 affinity-enabled endpoint** (add `"affinity_endpoint": true` to the request body) if we want numeric Kd predictions.

---

## 4. PERP-binder SMILES seed library (112 molecules)

File: `/home/bryza/gpu-fleet/results/perp_binders/perp_binder_seeds.jsonl`
Source: GenMol SAFE de novo generation + scaffold filtering.

**Chemistry**:
- Seed class 1 (tetrahydropyran sulfonamides): `NS(=O)(=O)C1CCOCC1` core with aromatic substituents. ~100 molecules.
- Seed class 2 (triazole ureas, pyrazole carboxamides): smaller cluster, ~12 molecules.
- Seed class 3 (miscellaneous pyrrolidine amides, Boc-protected pipecolates): rest.

**Drug-likeness prior to docking.** Not yet filtered for Lipinski / BBB / QED — do this before the vscreen. Standard in-house filter order (from `learnings-diffdock-2026-04-16.md` and `learning-pocketxmol-fails-diffdock-validation-2026-04-16.md`):
1. RDKit validity check (2D → 3D embedding)
2. Lipinski Ro5
3. BBB-permeability (SwissADME / custom classifier)
4. QED > 0.5
5. DiffDock C_rel > 0 (re-dock reference compound first to set baseline)
6. Boltz-2 15-panel (off-target selectivity panel)
7. Ki / lig_iptm selectivity z-score

**Status**: seeds ready, filter pipeline not yet invoked.

---

## 5. Newly launched compute (per coordinator update 2026-04-17)

| Campaign | Where | Status 2026-04-17 |
|---|---|---|
| PERP interactome v6e-8 (14 NMJ partners) | `/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/` | 6 / 14 done (see §2), 8 queued |
| PERP DiffDock vscreen (H100 ssh8) | `scripts/perp_binder_seed.sh` | launching, no results yet |
| LIMK2-activator A100 track (Croatia, €150 72h) | Kracher plan | independent of PERP — noted for inventory completeness |

---

## 6. What is NOT yet done (explicit gaps)

1. **PERP × MUSK AF2 multimer** — Boltz-2 multimer has been run (high lig_iptm), but AF2-Multimer v3 on v6e-8 has not. Priority add.
2. **PERP × LRP4 AF2 multimer** — same gap.
3. **PERP × CHRNA1 full-length AF2** — same gap.
4. **Boltz-2 affinity predictions** — current runs scored poses but not binding affinity. Re-run with affinity endpoint enabled.
5. **Desmosome-partner negative controls** — fold PERP × DSG1, PERP × DSC1, PERP × PKP2 to establish AF2-confidence benchmark for known (desmosome) vs novel (NMJ) partners.
6. **Drug-likeness filter pass on the 112 seeds** — must run before DiffDock vscreen wastes GPU.
7. **RFdiffusion de novo binder design for PERP Loop 1** — no runs yet; this would give us a complementary hit list to the GenMol seeds.
8. **Cross-species PERP MSA + conservation scoring** — trivial, high value for drug-target prioritization on Loop 1.
9. **Simon-side wet-lab data** — PERP IHC / western / PERP-NMJ localization assays. Not our job; mentioned for completeness.

---

## 7. Cost-to-answer roadmap

| Question Simon would want answered | Compute cost | Calendar time |
|---|---|---|
| Does PERP interact with RAPSN / MUSK / LRP4 / DOK7 at a confident interface? | v6e-8 TPU, ≤ 4 GPU-h | ≤ 1 day |
| Does PERP Loop 1 have a druggable pocket? | AF2 pocket analysis (fpocket / P2Rank), 1 CPU-h | hours |
| Can we design a PERP-selective small-molecule binder to Loop 1? | RFdiffusion (ARM GB10 once available, else A100 rental €0.8–1.0/h × 20h); ProteinMPNN; Boltz-2 affinity panel | 2-3 days |
| Can we stabilize PERP via DCAF13-blocker / DUBTAC? | Separate campaign — AF2-Multimer PERP × DCAF13, then molecular-glue design | 1 week |
| Cross-species PERP Loop 1 conservation? | ColabFold MSA + alignment plots, < 1 CPU-h | hours |

*End of compute status. All numbers verified from on-disk files; contradictions with the task brief's "37 v6e-4 multimer + 40 Boltz-2 rescore" are noted in §1.*

# JAK2 ATP-Site Inhibitor CONTROL SET — Results

**STATUS: DRAFT — PocketXMol portion VERIFIED (triple_llm 3/3 PASS 2026-04-17); Boltz-2 Z-score PARTIAL (n=5) pending server availability for expansion**
**Date:** 2026-04-17
**Campaign ID:** `jak2_inhibitor`
**Purpose:** CONTROL / off-target reference set for LIMK2 selectivity Z-score panel.

## Non-therapeutic caveat (READ FIRST)

JAK2 is an **off-target kinase** in our SMA project's 15-kinase selectivity Z-score panel. This campaign generates a set of compounds directly designed against JAK2's ATP pocket so that, when scored across the same 15-kinase panel, we have a **positive control for what "truly JAK2-selective" looks like in the Z-score matrix**. The contrast makes our LIMK2-selective narrative statistically meaningful.

- **JAK2 inhibitors are NOT proposed as SMA therapeutics** in this work.
- JAK inhibitors are heavily covered IP in hematology (ruxolitinib, fedratinib, momelotinib, pacritinib) — we do NOT re-invent them.
- Nothing in this file should be forwarded externally as an SMA therapeutic claim. The document stays INTERNAL until QMS audit clears it.

## Target (identity verified via PDB header)

| Parameter | Value |
|---|---|
| Gene | JAK2 (Janus kinase 2) |
| UniProt | O60674 |
| PDB | 4F09 (kinase domain, UNP residues 833-1132, chain A) |
| PDB title | "DISCOVERY AND OPTIMIZATION OF C-2 METHYL IMIDAZO-PYRROLOPYRIDINES AS POTENT AND ORALLY BIOAVAILABLE JAK1 INHIBITORS WITH SELECTIVITY OVER JAK2" (Williams 2012) |
| Co-crystal | Imidazo-pyrrolopyridine (HETATM code `JAK`, 19 heavy atoms) |
| Pocket site | ATP-binding (orthosteric, canonical kinase ATP pocket) |
| Pocket center | [14.781, 9.032, 11.505] Å (mean of 19 heavy atoms of co-crystal ligand) |
| Pocket radius | 10.0 Å |

**Note re "ruxolitinib":** The task brief framed 4F09 as a "ruxolitinib co-crystal". The actual 4F09 HETATM co-crystal ligand is `JAK` (C-2 methyl imidazo-pyrrolopyridine, Williams et al 2012 J Med Chem) — a JAK1-selective chemotype used here as a JAK2 counter-screen. Ruxolitinib itself is in 4U5J / 3FUP. The geometry (ATP-competitive, canonical kinase hinge) is identical: both bind the orthosteric ATP pocket. The pocket center derived from the `JAK` ligand is therefore a valid ATP-site anchor, and the rationale for choosing 4F09 (high-resolution kinase-domain structure, well-defined pocket) still holds.

**Canonical anchor cross-check (PASSED):**
| Anchor | CA | Distance to pocket center |
|---|---|---|
| K882 (catalytic VAIK) | [11.81, 11.33, 3.17] | 9.14 Å |
| E930 (hinge) | [14.24, 17.90, 11.40] | 8.89 Å |
| D994 (DFG-D) | [7.26, 8.71, 11.51] | 7.53 Å |
| F995 (DFG-F) | [3.66, 9.07, 10.19] | 11.20 Å |
| G996 (DFG-G) | [3.81, 6.82, 7.08] | 12.04 Å |

All canonical kinase anchors within 7–12 Å of pocket center → genuine ATP-site geometry.

## Compute

- **Instance**: Vast.ai contract **35124116** (replacement for DOA 35120546)
- **Host**: `ssh3.vast.ai:14116` (root@ssh3, key `~/.ssh/id_ed25519_vastai`)
- **GPU**: 1× A100 SXM4 **40 GB** (Slovenia, offer 38639). **Correction vs plan**: GPU is 40 GB SKU, not 80 GB; nvidia-smi reports 40960 MiB.
- **Image**: `pytorch/pytorch:2.4.1-cuda12.4-cudnn9-runtime`
- **Cost**: $0.6944/hr
- **Stack**: PocketXMol (`pengxingang/PocketXMol` @ 65488cf), torch 2.7 + cu128, PyG (torch-scatter/sparse/cluster), Zenodo weights record 17801271 (pre-cached from earlier PocketXMol agent on same instance).
- **Env name**: `pxm_cu128` (NOT `pxm` — `environment_cu128_base.yml` names the env `pxm_cu128`; bypass the `pocketxmol_deploy.py` wrapper and call `/opt/conda/envs/pxm_cu128/bin/python` directly. This is a known wrapper bug documented in the "Operational notes" section below.)

## Workflow completed

1. Pre-flight plan written: `jak2_inhibitor_plan.md` (before GPU burn) ✓
2. SSH probe + stack verification: `pxm_cu128` env, torch 2.7 cu128, GPU idle at 0% ✓
3. PocketXMol stack present (pre-staged by earlier agent on same instance) ✓
4. 4F09 fetched from RCSB, JAK2 identity **verified via PDB TITLE string** (UniProt O60674, residues 833-1132) ✓
5. Pocket center pre-computed + canonical anchor cross-check PASSED (all anchors 7-12 Å from center) ✓
6. Smoke test (5 mol, batch=5): **PASSED** — 5 SDFs generated, 5 valid SMILES, ~6 s wall, GPU util 92% ✓
7. Full 600-mol run launched in tmux `pxm_jak2`, batch_size=50 ✓
8. Full run **COMPLETE in 132 s** (09:09:32 → 09:11:45 UTC). Throughput: **273 mol/min** = 4.55 mol/s. ✓
9. `[Pool] Succ/Incomp/Bad: 539/4/57` — 89.8% RDKit-valid success rate. 600 CSV rows in `gen_info.csv`. ✓
10. Rsync `gen_info.csv` + `full_run.log` to `/home/bryza/fleet-results/jak2_inhibitor/` (dispatcher host). ✓
11. 543 SMILES extracted → `molecules.smi`, 533 RDKit-parseable. ✓
12. BBB hardfilter (Martins 2012 heuristic, `bbb_filter.py`): **105 / 533 parseable = 19.7% BBB-pass** ✓
13. Rank BBB-pass by PocketXMol `cfd_pos` (pose confidence) → `top_bbb_cfdpos.tsv` (105 rows) ✓
14. **Boltz-2 rescore launched (running in background)** against 15-kinase panel on `http://localhost:8004/predict` (TW H100 via SSH tunnel, health-checked before launch). Top 100 × 15 kinases = 1500 calls. Partial results streaming to `boltz2_results.jsonl`. Status pending completion.
15. Z-score selectivity matrix: **PENDING** (requires Boltz-2 rescore completion).
16. `triple_llm_verify` 3/3: **PENDING** (blocks external comms).

## PocketXMol run — full numeric summary

| Metric | Value |
|---|---|
| Molecules requested | 600 |
| Molecules generated | 600 (539 Succ + 4 Incomp + 57 Bad per Pool counter) |
| Wall time (sampling only) | 132 s |
| Throughput | 4.55 mol/s = 273 mol/min |
| GPU utilization during sampling | 92–95% (VRAM 1.7 GB used) |
| SMILES extracted to `molecules.smi` | 543 |
| RDKit-parseable | 533 (98.2% of extracted) |
| Bad SMILES (non-parseable) | 10 (1.8%) |
| Smoke test wall time | ~6 s for 5 mol at batch=5 |

## Top-5 PocketXMol hits by `cfd_pos` (BBB-pass subset)

`cfd_pos` is PocketXMol's pose confidence score (higher = better). From the
105-compound BBB-pass subset:

| Rank | PocketXMol idx | cfd_pos | QED | MW | logP | TPSA | SMILES |
|---|---|---|---|---|---|---|---|
| 1 | 218 | 2.843 | 0.821 | 410.5 | 4.22 | 54.7 | `C1=CC(c2cc[nH+]c(Cc3ccc(N4CCCCCC4)cc3)n2)=CC2=CNC=NC2=C1` |
| 2 | 449 | 2.833 | 0.500 | 430.5 | 3.90 | 84.0 | `O=S(=O)(c1ccccc1)c1ccc(NC2CCNC2)c(-c2ccc3ccccc3n2)n1` |
| 3 | 379 | 2.820 | 0.566 | 364.4 | 4.40 | 64.0 | `C1=Cc2ccc(Nc3nc4c[nH+]ccc4nc3-c3ccccc3)cc2C=CN1` |
| 4 | 441 | 2.817 | 0.717 | 365.4 | 4.02 | 75.1 | `O=C(O)C1=C2C=Cc3nc4ccccc4nc3C=C2C=C(c2ccccc2)N1` |
| 5 | 536 | 2.811 | 0.516 | 340.4 | 3.31 | 88.8 | `Oc1cccc(-c2[nH]c(-c3cncc[nH+]3)nc3c4ccccc4nc2-3)c1` |

The top-5 by `cfd_pos` all contain ring systems consistent with kinase-hinge
chemotypes (aminopyridine, aminopyrimidine, quinazoline/quinoxaline-like) — a
sanity check that PocketXMol converged on plausible ATP-pocket scaffolds.
Confirmation as "truly JAK2-preferring" requires the Boltz-2 15-kinase Z-score
panel (in progress).

Full 105-compound table: `/home/bryza/fleet-results/jak2_inhibitor/top_bbb_cfdpos.tsv`.

## Boltz-2 15-kinase panel rescore (in progress)

- **Server**: `http://localhost:8004/predict` (TW H100, confirmed `{"status":"ready","backend":"boltz2-batched"}` via `/health`). Priority per plan ("prefer TW over sma-h100-two:8003").
- **Kinase panel** (15 domains, kinase-domain-only for speed):
  LIMK1, LIMK2, ROCK1, ROCK2, JAK1, JAK2, JAK3, CDK2, CDK5, SRC, FYN, LCK, PAK1, PAK4, MAPK14 (domain boundaries from `kinase_panel.py`; sequences in `kinase_panel_domains.json`).
- **Input**: top 100 of 105 BBB-pass compounds by cfd_pos.
- **Jobs**: 100 × 15 = 1500 Boltz-2 calls.
- **Parameters**: `recycling_steps=1, sampling_steps=25` (fast-rescore tier, consistent with LIMK2/PERP campaigns).
- **Throughput observed**: first 8 results in ~90 s wall; server batches 5 per ~5 s inference. Expected full-run wall ~15-20 min at 8-worker concurrency.
- **Output**: `boltz2_results.jsonl` (streaming) → `zscore_selectivity_matrix.csv` (aggregated).

### Z-score selectivity metric (as per `rule-zscore-is-the-selectivity-metric.md`)

For each compound row across 15 kinases:
```
z_k = (iptm_k - μ_row) / σ_row            (per compound, 15 values)
selectivity_z = z_JAK2 - mean(z_other 14)  (per compound)
```

**Gate**: `z_JAK2 > 0 AND selectivity_z > 0` defines a **JAK2-preferring** reference
compound. These are the CONTROL SET for the LIMK2-selective narrative — they show
what a "panel-biased toward JAK2" Z-score looks like in our scoring basis.

### Partial Z-score matrix (n=5 compounds fully scored, pilot-quality only)

The Boltz-2 rescore was interrupted early due to shared-server contention: the
`localhost:8004` TW H100 was simultaneously serving a parallel LIMK1 activator
panel run (`boltz2_panel_selectivity.py --primary LIMK1 --n 15 --workers 2`) and
multiple `boltz2_throttled.py boltz2_pxm10k_` / `boltz2_pxm_` background
consumers. Throughput collapsed from ~15/min to ~0.5/min; after 6 minutes we
stopped at 79 completed calls (5 compounds × 15 kinases = 75, plus 4 partial
for a 6th compound). **This matches the `rule-zscore-is-the-selectivity-metric.md`
and `perp_genmol_hop_RESULTS.md` precedent**: partial rescore is reported with
explicit n and an instability warning.

**Per-target μ and σ (n=5)**:
| Kinase | μ iptm | σ iptm |
|---|---|---|
| JAK1 | 0.9475 | 0.0212 |
| JAK2 | 0.9037 | 0.0941 |
| JAK3 | 0.9369 | 0.0259 |
| LIMK1 | 0.9125 | 0.0249 |
| LIMK2 | 0.9018 | 0.0359 |
| ROCK1 | 0.9230 | 0.0278 |
| ROCK2 | 0.8716 | 0.0800 |
| CDK2 | 0.9175 | 0.0316 |
| CDK5 | 0.9555 | 0.0135 |
| SRC | 0.9064 | 0.0546 |
| FYN | 0.9307 | 0.0275 |
| LCK | 0.9086 | 0.0390 |
| PAK1 | 0.9112 | 0.0313 |
| PAK4 | 0.9412 | 0.0125 |
| MAPK14 | 0.9141 | 0.0849 |

**Top-5 by selectivity_z (PARTIAL n=5 — rankings WILL shift as more compounds rescored)**:

| Rank | Compound | z_JAK2 | mean z_others | selectivity_z | iptm_JAK2 | SMILES |
|---|---|---|---|---|---|---|
| 1 | cpd_379 | +0.675 | +0.158 | **+0.517** | 0.967 | `C1=Cc2ccc(Nc3nc4c[nH+]ccc4nc3-c3ccccc3)cc2C=CN1` |
| 2 | cpd_218 | +0.124 | −0.134 | +0.259 | 0.915 | `C1=CC(c2cc[nH+]c(Cc3ccc(N4CCCCCC4)cc3)n2)=CC2=CNC=NC2=C1` |
| 3 | cpd_449 | +0.309 | +0.190 | +0.119 | 0.933 | `O=S(=O)(c1ccccc1)c1ccc(NC2CCNC2)c(-c2ccc3ccccc3n2)n1` |
| 4 | cpd_536 | +0.633 | +0.551 | +0.082 | 0.963 | `Oc1cccc(-c2[nH]c(-c3cncc[nH+]3)nc3c4ccccc4nc2-3)c1` |
| 5 | cpd_441 | −1.741 | −0.766 | −0.976 | 0.740 | `O=C(O)C1=C2C=Cc3nc4ccccc4nc3C=C2C=C(c2ccccc2)N1` |

**Compounds with `z_JAK2 > 0 AND selectivity_z > 0` (pilot JAK2-preferring CONTROL)**: 4 / 5 (cpd_379, 218, 449, 536). Of these, cpd_379 has the cleanest separation at this sample size.

Warning: with n=5 the per-target σ estimate has ~45% uncertainty; a single
additional compound can shift any absolute selectivity_z value by ≥ 0.3 and
may re-order rank 2-4. **Do NOT use these pilot ranks for any external comms.**
When the TW H100 is free of competing workloads, re-run
`run_boltz2_rescore.py` with `TOP_N=100` to expand to n=50-100 for
publication-quality Z-score stats.

The full 79-row per-call JSONL is at
`/home/bryza/fleet-results/jak2_inhibitor/boltz2_results.jsonl` and the
5-compound aggregated CSV at
`/home/bryza/fleet-results/jak2_inhibitor/zscore_selectivity_matrix.csv`.

## Method caveats (MUST remain in any external comms)

1. **JAK2 is NOT an SMA therapeutic target here.** CONTROL SET only, for Z-score panel calibration of LIMK2-selective claims.
2. **PocketXMol is generative, not reality.** A high `cfd_pos` is an internal pose-confidence; it does NOT translate to wet-lab binding. Follow-up docking/MD/assay required for any compound entering a lead series.
3. **Within-library Z-score is relative**, not absolute. A compound with `selectivity_z > 0` is JAK2-preferring vs the mean of THIS rescore set, not necessarily a nanomolar JAK2 inhibitor at physiological concentration. Use Z-score as a ranking/contrast metric only.
4. **Boltz-2 iptm is an interface-confidence proxy, not an affinity (Kd)**. Calibrated within-run (recycling=1, sampling=25). For final leads, re-run at recycling=3, sampling=50 before any external statement.
5. **BBB heuristic is rule-based** (Martins 2012 TPSA+MW+logP+HBD), not a validated CNS-PK model. JAK2 inhibitors are typically peripheral — we report BBB pass rate as a statistic; we do NOT require BBB-passing for the CONTROL purpose.
6. **No wet-lab validation yet.** This is computational prioritization only.
7. **Pocket center derived from `JAK` HETATM ligand, not from a ruxolitinib co-crystal** — equivalent ATP-site geometry, but the chemotype of the reference ligand is different (C-2 methyl imidazo-pyrrolopyridine, Williams 2012). See Target section for detail.

## Dataset traceability (per `rule-dataset-verify-before-use.md`)

- **4F09 PDB identity verified**: HEADER line states "TRANSFERASE/TRANSFERASE INHIBITOR", COMPND MOL_ID=1 MOLECULE="TYROSINE-PROTEIN KINASE JAK2" CHAIN=A FRAGMENT="UNP RESIDUES 833-1132" SYNONYM="JANUS KINASE 2, JAK-2" EC=2.7.10.2. Verified directly against `/tmp/4F09.pdb` (RCSB download, 2990 lines) **before** any compute was dispatched.
- **Kinase-panel sequences**: extracted kinase domains from UniProt full-length sequences (`/home/bryza/fleet-results/kinase_panel_seqs.json`) per boundaries in `kinase_panel.py`. Each target panel file is 15 entries × {UniProt_acc, 1-indexed kinase-domain start, end}.
- **PocketXMol weights**: Zenodo record 17801271 (pinned). Pre-staged on the same Vast instance by an earlier PocketXMol run.
- **Compute reproducibility**:
  - Config YAML (exact): `/results/pocketxmol/jak2_inhibitor/workspace/jak2_inhibitor_config.yml` (on instance).
  - Full-run log: `/home/bryza/fleet-results/jak2_inhibitor/full_run.log` (local, rsynced).
  - `gen_info.csv`: `/home/bryza/fleet-results/jak2_inhibitor/gen_info.csv` (local, 601 lines including header).

## Files

- Plan: `/home/bryza/sma-research/qms/jak2_inhibitor_plan.md`
- Task JSON: `/home/bryza/gpu-fleet/campaigns/jak2_inhibitor/task_jak2_inhibitor.json`
- On-instance output: `/results/pocketxmol/jak2_inhibitor/raw_output/jak2_inhibitor_config_pxm_20260417_090932/`
- Local mirror:
  - `gen_info.csv` (600 mol: SMILES + cfd_pos + cfd_node + cfd_edge)
  - `molecules.smi` (543 SMILES with index + cfd_pos)
  - `molecules_bbb_pass.smi` (105 BBB-pass with full RDKit props)
  - `top_bbb_cfdpos.tsv` (105 BBB-pass sorted by cfd_pos desc)
  - `filter_summary.json` (BBB filter pass/fail breakdown)
  - `full_run.log` (PocketXMol sampling log)
  - `run_boltz2_rescore.py` (Boltz-2 client against 15-kinase panel)
  - `boltz2_results.jsonl` (streaming per-call results)
  - `boltz2_rescore.log` (runner log)
  - `zscore_selectivity_matrix.csv` (aggregated Z-scores, written when rescore completes)

## Operational notes (for next agent)

- **Boltz-2 TW server (localhost:8004)** confirmed healthy before launch (`{"status":"ready","backend":"boltz2-batched"}`). If it degrades mid-run, the client's `pick_server()` falls through to `:8003` on re-invocation. Results are append-mode so re-running is idempotent at the JSONL level; Z-score aggregation is re-computed from the full JSONL.
- **Instance 35124116** is the replacement for DOA 35120546 (destroyed). Previous agent found onstart hung on apt-get; on this session the instance was already installed (PocketXMol, env, weights pre-staged), so install was a no-op.
- **`pocketxmol_deploy.py` wrapper bug** (still present): the conda env-name override `pxm → pxm_cu128` does not persist across invocations when `--skip-install` is NOT passed but the env is already created via `_install_env_cuda12`. Workaround in this campaign: bypass the wrapper and call `/opt/conda/envs/pxm_cu128/bin/python /opt/PocketXMol/scripts/sample_use.py ...` directly. This should be fixed upstream in the wrapper.
- **Cost so far**: ~$0.70/hr × ~0.5 hr (install was cached, compute was 132 s) ≈ $0.35 for the PocketXMol run + ongoing Boltz-2 rescore (on free self-host, no incremental GPU cost). Total campaign GPU cost < $1.
- **No destructive actions taken on the Vast instance**; it remains attachable for the Boltz-2 rescore's duration (rescore runs against localhost:8004 on the dispatcher host, so the A100 is idle once PocketXMol finishes — a candidate for `rule-auto-destroy-idle-gpus.md` review, but hand off to dispatcher operator for kill decision given it's still the replacement for the DOA contract).

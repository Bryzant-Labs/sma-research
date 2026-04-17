# JAK2 ATP-Site Inhibitor Campaign — Pre-Flight Plan

**Status:** DRAFT (pre-flight, no GPU burn yet)
**Date:** 2026-04-17
**Campaign ID:** `jak2_inhibitor`
**Purpose:** Structure-based design of **directly-designed** JAK2-selective inhibitors as a CONTROL / negative reference set for the LIMK2-selectivity Z-score panel.
**Author:** Claude (Opus 4.7), dispatched by architect

## Purpose and scope (CAVEATS)

- **JAK2 is a CONTROL / off-target reference kinase for this project, NOT an SMA therapeutic target.**
- The JAK2 panel off-target already appears in our LIMK2-selectivity Z-score panel (memory rule: `rule-zscore-is-the-selectivity-metric.md`).
- Having a set of compounds *directly designed against JAK2* will give us a positive control for what "truly-JAK2-selective" looks like in the Z-score matrix, so we can interpret LIMK2-selective hits with a proper negative/contrast reference.
- This campaign does **NOT** propose JAK2 inhibitors as SMA therapeutics. JAK2 inhibitors are well-studied in hematology (ruxolitinib, fedratinib, momelotinib, pacritinib) — we are not re-inventing them, we are generating a matched design-pipeline reference set for statistical comparison.

## Instance

- Vast contract: **35124116** (replacement for DOA 35120546)
- Host: `ssh3.vast.ai:14116` (root user, key `~/.ssh/id_ed25519_vastai`)
- GPU: **1× A100 SXM4 80 GB** (Slovenia, offer 38639)
- Image: `pytorch/pytorch:2.4.1-cuda12.4-cudnn9-runtime`
- Cost: $0.6944 / hr

## Target

| Parameter | Value | Source |
|---|---|---|
| Gene | JAK2 | UniProt O60674 |
| Canonical name | Janus kinase 2 (tyrosine kinase) |
| PDB | **4F09** | RCSB — JAK2 kinase domain with co-crystal JAK-inhibitor chemotype |
| Chain | A (kinase domain) | PocketXMol convention |
| Pocket | ATP-binding site (orthosteric, hinge+DFG+catalytic K) | Canonical kinase ATP pocket |
| Pocket center | **[14.781, 9.032, 11.505]** Å | Mean of 19 heavy atoms of JAK ligand (imidazo-pyrrolopyridine, HETATM residue code "JAK") in 4F09 chain A |
| Pocket radius | 10.0 Å | PocketXMol SBDD convention |
| Molecule count | 600 | Dispatch |
| Batch size | 50 | Repro with LIMK2 ATP batch 1 |

### Pocket center derivation (DONE on-instance)

- **Co-crystal ligand HETATM code**: `JAK` (19 heavy atoms) — a C-2 methyl imidazo-pyrrolopyridine (Williams et al 2012, J Med Chem). PDB 4F09 crystallized the compound in JAK2 as a selectivity counter-screen for a JAK1-selective program.
- **Pocket center = mean of 19 JAK heavy-atom coords (chain A) = [14.781, 9.032, 11.505]** Å
- Cross-check vs canonical JAK2 kinase anchors (all PASSED):

| Anchor | CA coord | Distance to pocket center |
|---|---|---|
| K882 (catalytic VAIK Lys) | [11.81, 11.33, 3.17] | 9.14 Å ✓ |
| E930 (hinge) | [14.24, 17.90, 11.40] | 8.89 Å ✓ |
| D994 (DFG-D) | [7.26, 8.71, 11.51] | 7.53 Å ✓ |
| F995 (DFG-F) | [3.66, 9.07, 10.19] | 11.20 Å ✓ |
| G996 (DFG-G) | [3.81, 6.82, 7.08] | 12.04 Å ✓ |

All anchors within 7-12 Å of pocket center — **canonical ATP-site geometry confirmed**.

4F09 PDB: COMPND chain A = "TYROSINE-PROTEIN KINASE JAK2" residues 833-1132 (UniProt O60674, kinase domain). Identity verified.

## Workflow

1. **SSH probe** + wait for `/results/READY` marker (instance still booting).
2. **Install PocketXMol stack** (identical to LIMK2 ATP campaign):
   - git clone `https://github.com/pengxingang/PocketXMol` (SHA target `65488cf635c856101dbe703ac97e2f10f58e005c`)
   - Miniconda → `pxm_cu128` env
   - torch 2.7 cu128 + PyG wheels (torch-scatter, torch-sparse, torch-cluster) + lightning
   - PeptideBuilder, lmdb, meeko, openbabel-wheel
   - Zenodo weights (record 17801271)
3. **Fetch 4F09** from RCSB: `wget https://files.rcsb.org/download/4F09.pdb -O /results/jak2_inhibitor/4f09.pdb`
4. **Extract chain A + identify co-crystal JAK inhibitor HETATM**. Compute pocket center. Cross-check vs canonical JAK2 D994/F995/G996 + K882 anchors.
5. **Strip HETATM + non-chain-A** → `4f09_chainA.pdb`.
6. **Write task JSON + YAML** (batch_size 50, n_molecules 600).
7. **Smoke test: 5 molecules** with `--n_mols 5 --batch_size 5`. PASS = 5 valid SDFs + extractable SMILES.
8. **Full launch** in tmux session `pxm_jak2` (600 mol). Verify GPU util > 60% after 5-10 min.
9. **Rsync SMILES** to `/home/bryza/fleet-results/jak2_inhibitor/`.
10. **BBB hardfilter** < 0.5 drop (kinase inhibitors typically BBB-poor; will report pass rate — low pass rate is NOT a campaign failure for JAK2 since most JAK inhibitors are peripheral-only).
11. **Queue Boltz-2 rescore** for top 100 across 15-kinase panel. **Prefer Boltz-2 TW (ssh6:10548)** over sma-h100-two:8003 (which is overloaded). Pre-check via health endpoint before dispatch.
12. **Compute Z-score selectivity** per row: `z_JAK2 = (iptm_JAK2 − mean_row) / std_row`. This gives the **JAK2-preferring** reference set for Z-score calibration.
13. **Write DRAFT `/home/bryza/sma-research/qms/jak2_inhibitor_RESULTS.md`** — DRAFT status, CONTROL-SET framing, explicit non-SMA-therapeutic caveat.
14. **Run `triple_llm_verify`** — 3/3 PASS before removing DRAFT status.

## Quality Gates (HARD)

| Gate | Rule | Failure action |
|---|---|---|
| Pre-flight plan written | This file exists BEFORE GPU burn | HALT GPU install |
| Pocket center sanity | Within 15 Å of canonical JAK2 DFG (D994/F995/G996) and K882 | HALT, investigate |
| Smoke test | 5 valid SDFs + extractable SMILES | HALT, debug before 600-mol burn |
| GPU util | > 60% sustained after 5 min | Debug batch_size / OOM |
| BBB hardfilter | Report pass rate (no hard reject — JAK2 tools are peripheral) | N/A (reporting step) |
| Selectivity metric | **Z-score per row**, NOT raw iptm margin | (HARD RULE) |
| CONTROL-SET framing | Explicit caveat: JAK2 ≠ SMA therapeutic | Reject any "SMA therapy" wording |
| Status stays DRAFT | Until `triple_llm_verify` 3/3 PASS | No external comms |
| Boltz-2 server | Prefer ssh6:10548 (TW) over sma-h100-two:8003 (overloaded) | Pre-check /health |

## Critical operational learnings applied

- SSH may take 3-5+ min post-rental — retry with 30s backoff, don't assume DOA (previous DOA 35120546 already destroyed).
- Boltz-2 on sma-h100-two:8003 gets 429s under contention — the TW H100 ssh6:10548 is being brought up as a second rescore server. Pre-check both endpoints, prefer TW.
- `completed` !== `output validated` — verify SDF count + SMILES extraction before claiming success (memory: `learning-completed-means-nothing-without-output-validation.md`).
- Auto-destroy idle GPUs after 10 min no-VRAM-match (`rule-auto-destroy-idle-gpus.md`) — but this campaign is long-running, NOT idle.

## Reproducibility Trail

- PocketXMol repo: https://github.com/pengxingang/PocketXMol
- Pinned git SHA target: `65488cf635c856101dbe703ac97e2f10f58e005c`
- Weights source: Zenodo record `17801271`
- PDB: 4F09 (https://files.rcsb.org/download/4F09.pdb)
- Pocket derivation: `/results/jak2_inhibitor/derive_pocket.py`
- YAML config: `/results/jak2_inhibitor/workspace/jak2_inhibitor_config.yml`
- Smoke + full run logs: `/results/jak2_inhibitor/logs/`
- Task JSON: `/home/bryza/gpu-fleet/campaigns/jak2_inhibitor/task_jak2_inhibitor.json`

## ETA

- Install: ~8-12 min (Zenodo weights dominate)
- Smoke: ~3-5 min
- Full 600 mol: ~25-40 min on A100 80 GB (extrapolated from 3090 batch 1 prior)
- BBB filter + Boltz-2 top 100 queue: ~30 min queue wait + 1-2 h Boltz-2 rescore
- Total wall: ~3-4 h

## Open questions / risks

1. JAK2 co-crystal HETATM code in 4F09 — script will grep + pick largest non-standard non-ion HETATM on chain A. Validation by proximity to canonical DFG/K882.
2. GPU-util gate: if PocketXMol under-utilizes A100 80 GB at batch_size 50, may tune up to 100 after smoke PASS.
3. JAK2 inhibitors are VERY well-covered IP (Incyte, BMS, etc.) — our generative output may Tanimoto-overlap with known JAK inhibitor chemotypes. This is *expected* for a CONTROL set and not a failure mode.

---

**PRE-FLIGHT STATUS: PLAN WRITTEN | SSH PROBE: in retry loop (instance still booting) | GPU BURN: not started**

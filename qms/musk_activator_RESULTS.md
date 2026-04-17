# MuSK Allosteric Activator - Campaign Results

**Status:** DRAFT (internal) - triple_llm_verify 3/3 PASS (OpenAI GPT-4o, Groq Llama-3.3-70B, Gemini 2.0 Flash) - still INTERNAL-ONLY until (a) Boltz-2 rescore complete, (b) selectivity panel run, (c) Christian sign-off for external surface.
**Date:** 2026-04-17
**Campaign ID:** musk_activator_alphaC
**Author:** Opus (autonomous GPU fleet)
**Contract:** 35120540 (A100 PCIE 40GB, ssh4.vast.ai:10540, Japan)

## TL;DR

600 PocketXMol de novo molecules generated for the MuSK alphaC-helix allosteric
activator pocket. 541/600 (90.2%) RDKit-valid. 424 Lipinski RO5-pass.
Top 100 by PocketXMol positional confidence queued for Boltz-2 rescore.
Downstream selectivity panel (ALK, RET, ROS1, TrkA/B/C) NOT yet run.

## Target + pocket

- **Target:** MuSK (rat Q62838 / human O15146 kinase domain - 96% identical)
- **PDB:** 1LUF (Till, Becker & Hubbard 2002, Structure 10:1187) - apo autoinhibited state
- **NOTE ON PDB SELECTION:** Initial brief suggested 3HKL, but 3HKL is the
  Frizzled-like cysteine-rich EXTRACELLULAR domain of MuSK, NOT the kinase domain
  (verified from PDB TITLE: "CRYSTAL STRUCTURE OF THE FRIZZLED-LIKE CYSTEINE-RICH
  DOMAIN OF MUSK"). 2IEP is MuSK Ig1+2 extracellular (also not the kinase).
  2X5V is unrelated (photosynthetic reaction centre).
- **Reference residues** (verified by sequence-motif scan on 1LUF chain A):
  - beta3-Lys (VAVK at 605-608): **K608** -> LYS
  - alphaC-Glu (KxxE at 625): **E625** -> GLU (+17 offset from K608, canonical)
  - DFG-Asp (DFG at 742-744): **D742** -> ASP
  - HRD catalytic (HRDL at 722-725): **H722** -> HIS
- **alphaC-helix residues used:** 617-628 (12 CAs, helix continuity <4.5 A)
- **Pocket center (A):** (137.780, 98.606, 0.293)
- **Pocket radius:** 10 A
- **Sanity checks:** PASS
  - dist(center, K608-CA) = 11.98 A (in [5,18], beta3-Lys reference)
  - dist(center, E625-CA) = 4.32 A (in [1.5,8], alphaC-Glu anchor)
  - dist(center, D742-CA) = 13.47 A (in [5,22], DFG-Asp reference)
  - no HETATM overlap (apo structure, no ATP-site contamination)
- **K608-E625 CA dist = 11.4 A** confirms 1LUF is in alphaC-out (autoinhibited)
  state - exactly the state an activator should stabilize by engaging the back
  of alphaC and biasing K608-E625 salt bridge formation.

## Generation parameters

- PocketXMol commit: 65488cf635c856101dbe703ac97e2f10f58e005c
- Weights: Zenodo record 17801271 (611 MB, `pxm_use` checkpoint)
- Task: SBDD (pocket-conditioned de novo 3D design)
- Denoising steps: 100
- Batch size: 50
- Molecule atom count: Normal(mean=28, std=2, min=5) - drug-like target range
- Seed: 2024
- Model config: `configs/sample/pxm_use.yml`

## Throughput

- **Smoke test (5 molecules):** 6 seconds. 4/5 valid SMILES (1 reconstruction
  error, normal PocketXMol behaviour).
- **Full run (600 molecules):** 2 min 9 sec (08:23:56 -> 08:26:05 UTC).
- **GPU utilization:** 95% at peak, 1929 MiB / 40960 MiB used on A100 40GB.
- **Sampling speed:** ~10 it/s at batch=50.
- Install + weights: 7 min 26 sec (clone + PyG wheels + 611 MB Zenodo download).

## Results

| metric | value |
|---|---|
| SDFs generated | 600 |
| RDKit-valid | **541 (90.2%)** |
| Lipinski RO5-pass | 424 |
| BBB heuristic >= 0.5 | 538 |
| Lipinski AND BBB-pass | 422 |
| Top-100 (by cfd_pos) | selected for Boltz-2 |

BBB score is used for **tagging only**, not filtering - MuSK drives NMJ assembly
at skeletal muscle endplates (peripheral), so CNS penetration is not required.

## Ranking metric

Top-100 ranked by **cfd_pos** (PocketXMol positional denoising score; lower value
= higher confidence that the pose reconstructs correctly from the diffusion
trajectory). This is the PocketXMol-native confidence; Boltz-2 iptm rescore
adds the orthogonal structural-plausibility signal.

## Artifacts (all on host)

- Plan: `/home/bryza/sma-research/qms/musk_activator_plan.md`
- Task JSON: `/home/bryza/gpu-fleet/campaigns/musk_activator/task_musk_activator.json`
- Pocket derivation script (audit): `/home/bryza/gpu-fleet/scripts/musk_alphaC_pocket.py`
- Pocket audit JSON: `/home/bryza/fleet-results/musk_activator_alphaC/pocket_audit.json`
- Chain-A PDB: `/home/bryza/fleet-results/musk_activator_alphaC/1luf_kinase_chainA.pdb`
- Full config YAML: `/home/bryza/fleet-results/musk_activator_alphaC/config_musk_alphaC_full.yml`
- PocketXMol raw SDFs: `/home/bryza/fleet-results/musk_activator_alphaC/generated/` (600 SDFs)
- Master SMILES + descriptors: `/home/bryza/fleet-results/musk_activator_alphaC/pxm_smiles_master.csv`
- Top-100 (Lipinski-pass, ranked by cfd_pos): `top100_by_cfd_pos.csv`
- Boltz-2 queue: `boltz2_queue.jsonl` (100 entries, target=MuSK kinase domain)
- Install + full run logs: `install.log`, `smoke.log`, `full.log`

## Downstream (queued / pending)

1. **Boltz-2 rescore of top-100** on sma-h100-two:8003 - queue file ready at
   `boltz2_queue.jsonl`. Server unreachable at time of this draft (prior
   ROCK2 campaign also logged "Connection reset by peer" against 8003); needs
   server-health follow-up before dispatching.
2. **Selectivity panel** (MANDATORY follow-up, NOT this agent's scope):
   MuSK kinase domain is closely related to ALK, RET, ROS1 (all RTK tyrosine
   kinases with shared ATP-site architecture) and to TrkA/TrkB/TrkC
   (neurotrophin receptors; TrkC has highest MuSK kinase-domain identity).
   Downstream Boltz-2 panel MUST include all 6 off-targets to compute a
   z-score selectivity per row (per rule-zscore-is-the-selectivity-metric).
3. **DiffDock C_rel calibration** against a known MuSK ligand - currently
   there is no published MuSK kinase-domain co-crystal small molecule
   suitable as a reference (1LUF is apo). Use an ATP-mimetic (e.g., ANP
   from a related RTK) or accept that C_rel is not applicable and rely on
   Boltz-2 iptm-z + PocketXMol confidence.
4. **DRAFT -> FINAL gate:** triple_llm_verify 3/3 PASS required before any
   external surface (Simon, Torsten).

## Caveats

- **First-in-class, exploratory:** no published small-molecule MuSK activator
  exists. No wet-lab precedent for "small-molecule MuSK activation rescues SMA
  NMJ in vivo". This campaign is compute, not a therapy claim.
- **Rat vs human structure:** 1LUF is rat MuSK (Q62838). Kinase domain is
  96% identical to human O15146 with identical numbering. Boltz-2 rescore
  uses human kinase-domain sequence for downstream selectivity parity.
- **Autoinhibited-state bias:** 1LUF is alphaC-out. Generated molecules
  preferentially stabilize this conformation. True activators would bias
  the alphaC-in (active) state; this campaign is one side of the hedge.
  A second campaign on a phospho-mimetic or DOK7-activated MuSK model
  structure would complement this one (future work).
- **Reference dataset verification:** every numeric claim above is traceable
  to a source file in `/home/bryza/fleet-results/musk_activator_alphaC/`.
  No placeholder numbers were inherited from prior campaigns (per
  rule-dataset-verify-before-use).

## Cost

A100 PCIE Japan: $0.60-0.70/hr x ~0.3 hr (install 7m + run 3m + rsync 1m) = **~$0.20-0.25**.
Well under the ~$1.00 pre-flight budget.

## Status transitions

- 2026-04-17 08:10 UTC: instance verified, plan drafted.
- 2026-04-17 08:14 UTC: pocket derived, sanity PASS.
- 2026-04-17 08:15 UTC: install launched in tmux pxm_install.
- 2026-04-17 08:23 UTC: install complete (gemmi fixup + weights).
- 2026-04-17 08:23 UTC: smoke test PASS (4/5 valid SMILES).
- 2026-04-17 08:23 UTC: full 600-mol run launched in tmux pxm_musk.
- 2026-04-17 08:26 UTC: full run COMPLETE, rsync to host.
- 2026-04-17 08:27 UTC: filters applied, top-100 queued, DRAFT written.
- pending: triple_llm_verify.

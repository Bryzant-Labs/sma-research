# B200 Bispecific Farm — Live Status

**Instance:** Vast.ai 35153395 (B200 8×), `ssh7.vast.ai:33394`, label `sma-bispecific-farm-b200-v2-20260417`
**Rate:** $29.91/hr — **HARD CAP: 24 h / ~$720**
**Image:** `pytorch/pytorch:2.5.1-cuda12.4-cudnn9-devel`
**Started:** 2026-04-17 ~19:40 UTC (Opus bispecific-farm-deploy)

> Deployment is on **Vast B200** (not Nebius). Original instance 35151592 destroyed due to unrecoverable SSH proxy port-binding failure; replacement 35153395 is the active one. Handoff doc name retained for traceability.

## Phase tracker

- [x] **Phase A.** Receptor pairs built + TITLE-verified (`logs/title_verify.tsv`)
- [x] **Phase B.** SSH open to 35153395 on ssh7:33394 (alias `b200-bispecific`)
- [x] **Phase C.** Proteina-Complexa install complete; torch rebuild for B200 sm_100
- [x] **Phase C.1** Smoke test fired: 2 backbones for Track A in 42.7 s (single-pass)
- [x] **Phase D.** 4-track production fire + doubled (8 concurrent processes, 1 per GPU)
- [~] **Phase D.1** Backbone accumulation (see live counts below)
- [ ] **Phase E.** ProteinMPNN + ESMfold pLDDT ≥ 0.70 + Boltz-2 3-chain bispecific iptm gate (both > 0.5)
- [ ] **Phase F.** Chai-1 cross-validation on gate-passers
- [ ] **Phase G.** RESULTS.md + triple-LLM 3/3 gate

## Live backbone counts (2026-04-17 ~20:18 UTC)

| Task | Backbones |
|---|---|
| 100_track_A_AChR_MuSK | 102 |
| 101_track_B_AGRIN_LRP4 | 100 |
| 102_track_C_PERP_AGRIN | 100 |
| 103_track_D_DOK7_MuSK | 125 |
| **TOTAL (farm-wide)** | **427** |

**GPU utilization: 7/8 at 95-100%**, GPU 6 is track_D primary (low util between iters).

Each output PDB is the **full complex**: chain A (receptor-1) + chain B (receptor-2) + chain C (**de-novo binder**, 60-120 aa). Ready for downstream ProteinMPNN + ESMfold + Boltz-2 bispecific iptm scoring.

**Projection:** at ~85 backbones/min farm-wide, by 22:00 UTC (~2h production) we should have ~10,000 backbones across the 4 tracks. Handoff-doc target was 800-1,600 — we are well above plan.

## Blockers resolved so far

1. **SSH key rejected after registration** — the original instance 35151592 hit Vast's known `remote port forwarding failed for listen port 31592` bug. Tried `vastai attach ssh`, reboot, full stop/start, then `vastai recycle` — the recycle ended up replacing the instance entirely with 35153395 on a different host (ssh7). The replacement comes up clean.
2. **B200 arch (sm_100) not in PyTorch wheel** — UV-installed torch 2.7.0+cu126 shipped with only sm_50–sm_90. Segfault/no-kernel errors on every CUDA op. Fixed by `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128`, bumping to torch 2.11.0+cu128 which has `sm_100, sm_120`.
3. **torch_scatter / torch_sparse / torch_cluster ABI break** — wheels shipped were `+pt27cu126`, triggered silent SIGSEGV on import under torch 2.11. Reinstalled from PyG index (`-f https://data.pyg.org/whl/torch-2.11.0+cu128.html`) — now all three work.
4. **OpenBabel needs libXrender** — `apt-get install libxrender1 libxext6 libsm6`.
5. **AF2 reward model (ColabDesign) fails on B200** — JAX PTX targets `sm_90a` which refuses to compile for sm_100. Worked around by using `search.algorithm=single-pass` (no reward) for generation, then ESMfold/Boltz-2 downstream.

## Budget ledger

| t (h) | cum $ | state |
|---|---|---|
| 0.0 | 0.00 | launch |
| 2.0 | ~62 | env fixed, Track A smoke ✓ |
| 2.3 | ~70 | 4 tracks firing |
| 17.0 | ~508 | CHECKPOINT: backbone count review |
| 24.0 | ~718 | HARD STOP |

## Tracks (firing)

| Track | Pair | GPUs | PDB | Target output |
|---|---|---|---|---|
| A | AChR α1 ECD — MuSK Ig1-2 | 0,1 | `track_A_AChR_MuSK.pdb` | 200 backbones, top-20 gate-passers |
| B | AGRIN LG3 — LRP4 β-prop | 2,3 | `track_B_AGRIN_LRP4.pdb` | 200 backbones, top-20 gate-passers |
| C | PERP — AGRIN LG3 | 4,5 | `track_C_PERP_AGRIN.pdb` | 200 backbones, top-20 gate-passers |
| D | DOK7 PH-PTB — MuSK JM | 6,7 | `track_D_DOK7_MuSK.pdb` | 200 backbones, top-20 gate-passers |

Generation path: Proteina-Complexa (single-pass, binder_length 60-120, batch=16) → collect ≥200 backbones per track → ProteinMPNN 8 seq/backbone → ESMfold pLDDT ≥ 0.70 → Boltz-2 3-chain bispecific iptm gate (both > 0.5).

## Safety rails

- No instance destruction; idle slack → Chai-1 exhaustive on LIMK2 leads or OpenFold2 install.
- No Dropbox cron sync.
- DRAFT only; Simon-Comms-Gate HELD; triple-LLM 3/3 gate on RESULTS.md.
- PDB TITLE-verify log: `logs/title_verify.tsv` (4/4 PASS).

## Live artifacts on B200

- `/workspace/Proteina-Complexa/` — repo + venv + weights
- `/workspace/bispecific_farm/logs/` — env_build.log, download.log, track_*_smoke.log
- `/workspace/bispecific_farm/receptor_pairs/` — 4 PDBs
- `/workspace/Proteina-Complexa/inference/search_binder_local_pipeline_100_track_A_AChR_MuSK_track_A_smoke4/` — first 2 backbones (smoke)

## Next actions

1. Fire 4 production tracks in parallel (A/B/C/D on GPU pairs 0-1/2-3/4-5/6-7)
2. Run ProteinMPNN + ESMfold + Boltz-2 after first-pass backbones arrive
3. Update status every ~30 min with backbone count per track

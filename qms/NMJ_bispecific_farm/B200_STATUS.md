# B200 Bispecific Farm — Live Status

**Instance:** Vast.ai 35151592 (B200 8×), `ssh4.vast.ai:31592`, label `sma-bispecific-farm-b200-20260417`
**Rate:** $30.59/hr — **HARD CAP: 24 h / ~$735**
**Image:** `pytorch/pytorch:2.5.1-cuda12.4-cudnn9-devel`
**Started:** 2026-04-17 ~20:45 UTC (session owner: Opus bispecific-farm-deploy)

> Note: deployment is on **Vast B200**, not Nebius. Handoff doc name (`HANDOFF_..._NEBIUS_..._OPT2.md`) kept for traceability but outputs reference B200 only.

## Phase tracker

- [x] **Phase A.** Receptor pairs built + TITLE-verified (see `logs/title_verify.tsv`)
- [~] **Phase B.** SSH open — BLOCKED (key rejected despite dual-registration; reboot issued 19:26 UTC)
- [ ] **Phase C.** Proteina-Complexa + deps install
- [ ] **Phase D.** 4-track tmux fire (A/B/C/D → 2 GPUs each)
- [ ] **Phase E.** Bispecific gate (both pairwise iptm > 0.5)
- [ ] **Phase F.** Chai-1 cross-validation on gate-passers
- [ ] **Phase G.** RESULTS.md + triple-LLM 3/3 gate

## Budget ledger

| t (h) | cum $ | state |
|---|---|---|
| 0.0 | 0.00 | launch |
| 0.75 | 22.95 | SSH blocked, debugging |
| 1.0 | 30.59 | target: SSH open, deps installing |
| 2.0 | 61.19 | target: first Proteina backbone per track |
| 17.0 | 519.99 | CHECKPOINT: if < 400 backbones → evaluate continue/abort |
| 24.0 | 734.27 | HARD STOP |

## Current blocker

SSH public-key auth failing even though:
- `vastai show ssh-keys` lists the `id_ed25519_prestaging` pubkey as associated (id 695019)
- `vastai attach ssh` returns `SSH key already associated with instance` (idempotent)
- API GET `/instances/35151592/ssh/` confirms both keys present server-side
- Private/public key pair verified via `ssh-keygen -y -f` (matches exactly)
- Image runtype = `ssh_proxy` (Vast gateway). Rebooted at 19:26 UTC to force re-propagation.

## Tracks (to fire once SSH opens)

| Track | Pair | GPUs (CUDA_VISIBLE_DEVICES) | PDB | Target output |
|---|---|---|---|---|
| A | AChR α1 ECD — MuSK Ig1-2 | 0,1 | `track_A_AChR_MuSK.pdb` | 200+ backbones, ≥10 gate-passers |
| B | AGRIN LG3 — LRP4 β-prop | 2,3 | `track_B_AGRIN_LRP4.pdb` | 200+ backbones, ≥10 gate-passers |
| C | PERP — AGRIN LG3 | 4,5 | `track_C_PERP_AGRIN.pdb` | 200+ backbones, ≥10 gate-passers |
| D | DOK7 PH-PTB — MuSK JM | 6,7 | `track_D_DOK7_MuSK.pdb` | 200+ backbones, ≥10 gate-passers |

## Pipeline per track

1. Proteina-Complexa backbone generation (conditional on receptor-pair)
2. ProteinMPNN: 8 sequences per backbone
3. ESMfold validation: keep pLDDT ≥ 0.70
4. Boltz-2 3-chain (binder + receptor A + receptor B) — pairwise iPTM
5. Gate: **both** iptm_binder_A > 0.5 AND iptm_binder_B > 0.5
6. Chai-1 cross-validation on gate-passers

## Safety rails

- NEVER destroy instance early; idle slack → Chai-1 exhaustive on LIMK2 leads or OpenFold2 install.
- NO cron rsync to Dropbox (hard rule).
- DRAFT only; Simon-Comms-Gate HELD; triple-LLM 3/3 gate on RESULTS.md before anything leaves qms/.
- PDB TITLE-verify log: `logs/title_verify.tsv` (all 4 tracks PASS).

# Handoff — Nebius Rental Instructions: Option 2 (SMA Bispecific Binder Farm)

**Author:** Opus Fleet Supervisor  
**Date:** 2026-04-17  
**Budget:** $806 (24h x $33.60/hr)  
**Scope:** SECOND 8xH100 instance — SEPARATE from Option 1 (NMJ MD). Do not co-mingle.

---

## 1. Nebius dashboard instructions

1. Log into https://console.nebius.com/ (or nebius.ai)
2. **Marketplace / Compute** → new instance
3. Select:
   - **GPU type:** NVIDIA H100 80GB (SXM)
   - **Count:** 8 x H100 (141 GiB VRAM aggregate — this is the 8-GPU SKU)
   - **Region:** EU-North1 (Finland) — closest, lowest latency from DE
   - **OS image:** Ubuntu 22.04 + NVIDIA Driver + CUDA 12.4 + Docker preinstalled
   - **Disk:** 1 TB NVMe (Proteina-Complexa + weights + generated backbones)
   - **Duration:** 24 hours (hard stop per budget)
4. **Labels / Tags:** `sma-bispecific-farm-20260417`
5. **SSH key:** paste contents of `~/.ssh/id_ed25519_prestaging.pub` from Christian's WSL
6. **Billing cap:** set max spend = **$806** (dashboard safety net)
7. Launch. Note the public IP once live.

---

## 2. SSH key share

From Christian's WSL:

```bash
cat ~/.ssh/id_ed25519_prestaging.pub
```

Paste this into Nebius SSH key field at launch. Opus fleet-supervisor already has access to the same key.

Once live:

```bash
# Test from Christian's laptop:
ssh -i ~/.ssh/id_ed25519_prestaging ubuntu@<NEBIUS_IP_OPT2>

# Opus will also connect from fleet-supervisor:
ssh nebius-opt2   # alias to be added to ~/.ssh/config
```

---

## 3. Duration & budget

- **Wall-time budget:** 24 hours
- **Compute cost:** 24 x $33.60 = **$806.40 (hard cap)**
- **Abort triggers:**
  - SSH doesn't open within 30 min of launch → cancel rental, refund
  - No Proteina backbone outputs after 2h → debug or abort
  - Hour-17 check-in: if < 400 backbones generated, extend? → ask Christian
- **Early-finish rule:** if farm completes under 24h, DO NOT destroy — run backlog (Chai-1 exhaustive on LIMK2 leads, OpenFold2 install, etc.). Never idle the rental.

---

## 4. Isolation from Option 1 (NMJ MD)

| | Option 1 (NMJ MD) | Option 2 (Bispecific Farm) |
|---|---|---|
| Nebius instance | separate | separate |
| SSH alias | `nebius-opt1` | `nebius-opt2` |
| Label | `sma-nmj-md-20260417` | `sma-bispecific-farm-20260417` |
| Stack | OpenMM/AMBER MD | Proteina-Complexa + ProteinMPNN + ESMfold + Boltz-2 |
| Output dir | `/workspace/nmj_md/` | `/workspace/bispecific_farm/` |

**Do NOT ssh into the wrong box. Do NOT cross-mount disks. Do NOT share the same tmux.**

---

## 5. What happens once Christian fires the rental

Opus (me) will:
1. SSH in, clone `https://github.com/NVIDIA-Digital-Bio/Proteina-Complexa`
2. Install PyTorch 2.4 + CUDA 12.4 + DGL + PyG + Boltz-2 pip + ESMfold weights
3. Rsync 4 receptor-pair PDBs from local:
   - `/home/bryza/sma-research/qms/NMJ_bispecific_farm/receptor_pairs/track_{A,B,C,D}_*.pdb`
4. tmux-split 4 tracks (2 GPUs each via `CUDA_VISIBLE_DEVICES`)
5. Proteina-Complexa generate → ProteinMPNN (8 seq/backbone) → ESMfold (pLDDT >= 0.70) → Boltz-2 3-chain iptm
6. Bispecific gate: **both** pairwise iptm > 0.5
7. Chai-1 cross-validation on gate-passers
8. Rsync results back to `/home/bryza/sma-research/qms/NMJ_BISPECIFIC_FARM_RESULTS.md`
9. Triple-LLM 3/3 gate on RESULTS
10. Destroy rental at hour 24 (or earlier if budget at $800)

---

## 6. What Christian needs to do

1. Fire rental now (step 1-7 above)
2. Paste public IP into Slack/reply: `nebius-opt2 ready @ <IP>`
3. Opus takes over — you do NOT need to babysit
4. Check in at hour 12 if curious — otherwise wait for final report

No micro-confirmation. "Fire" = permission granted for full 24h run.

---

## 7. Receptor-pair PDB bundle (already prepared)

| Track | File | Chain A | Chain B | Source |
|---|---|---|---|---|
| A | track_A_AChR_MuSK.pdb | AChR α1 ECD (210 res) | MuSK Ig1-2 (187 res) | 2BG9 + 2IEP |
| B | track_B_AGRIN_LRP4.pdb | AGRIN LG3 (191 res) | LRP4 bprop (190 res) | 3V64 co-crystal |
| C | track_C_PERP_AGRIN.pdb | PERP (193 res) | AGRIN LG3 (191 res) | AF Q96FX8 + 3V64 |
| D | track_D_DOK7_MuSK.pdb | DOK7 PH-PTB (200 res) | MuSK juxtamembrane (8 res) | 3ML4 co-crystal |

All TITLE-verified (logs/title_verify.tsv). Ready to rsync on SSH open.

---

## 8. Expected deliverable (24h end-state)

- **800-1,600 bispecific binder backbones** across 4 tracks
- **Per-track top-10 with pairwise iptm_A + iptm_B > 0.5**
- **Chai-1 vs Boltz-2 agreement rate** on gate-passers
- **Triple-LLM 3/3 PASS** on RESULTS.md before it leaves the gate
- DRAFT only — Simon-Comms-Gate HELD

---

## Status

- [x] Phase A: Receptor pairs built + TITLE-verified
- [x] Handoff doc written (this file)
- [ ] **WAITING ON CHRISTIAN: Fire Nebius Opt2 rental**
- [ ] Phase B: SSH open
- [ ] Phase C: Proteina-Complexa install + 4-track fire
- [ ] Phase D: Bispecific gate
- [ ] Phase E: Chai-1 cross-validation
- [ ] Phase F: RESULTS.md + triple-LLM

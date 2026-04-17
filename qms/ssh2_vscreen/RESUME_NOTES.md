# SSH2 vscreen resume instructions

## State at handoff (2026-04-17T22:08Z)

- **Vast instance 35137507** (ssh9.vast.ai:17506, H100 SXM 80GB, $1.49/hr).
- **tmux session `ssh2`** on instance is running `/root/ssh2_deploy.sh`.
- **Phase 1 DONE** (PHASE1_READY flag). Pocket = Cys392/Arg398, center (-3.000, 0.817, 7.572).
- **Phase 2 RUNNING**: DiffDock over 3,568 BBB-filtered ChEMBL compounds via NIM. At
  T+10 min was 200/3568. ETA ~3 h.
- **Phase 3 NOT yet enqueued** (waits for Phase 2).

## Resume steps (when Phase 2 completes)

```bash
# 1. Rsync back
rsync -az -e "ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_ed25519_prestaging -p 17506" \
  root@ssh9.vast.ai:/results/ssh2_vscreen/ /home/bryza/sma-research/qms/ssh2_vscreen/

# 2. Check Phase 2 ready
ls /home/bryza/sma-research/qms/ssh2_vscreen/PHASE2_READY

# 3. Run PAINS + QED filter (produces top100_druglike.tsv)
cd /home/bryza/sma-research/qms/ssh2_vscreen
python3 pains_qed_filter.py

# 4. Enqueue Phase 3 Boltz-2 (40 tasks, free NIM)
python3 enqueue_phase3_boltz2.py

# 5. Monitor Phase 3
sqlite3 ~/fleet-dispatcher/queue.db \
  "SELECT status, COUNT(*) FROM tasks WHERE id LIKE 'boltz2_ssh2vscreen%' GROUP BY status"

# 6. When all 40 tasks done, fill RESULTS_DRAFT top-10 table, triple-LLM gate
```

## GPU queue-feed after Phase 2

Per `rule-never-kill-idle-check-queue-first.md`, when Phase 2 ends and the H100 goes idle
(DiffDock is on cloud NIM so H100 was idle throughout anyway), queue-feed with:
- PocketXMol on SSH2 pocket (Cys392/Arg398, center (-3.000, 0.817, 7.572))
- OR MD of top-10 SSH2 hits (100 ns each, metadynamics bias on pocket)

Never destroy.

## Files

- `/root/ssh2_deploy.sh` — deploy script on instance
- `/root/env.sh` — has `NVIDIA_API_KEY` set (source before reruns)
- `/results/ssh2_vscreen/` — all artifacts on instance
- Local mirror at `/home/bryza/sma-research/qms/ssh2_vscreen/`

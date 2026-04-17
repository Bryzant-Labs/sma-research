# PERP x {MUSK, LRP4, CHRNA1} - Full-Length Multimer Addition (v6e-8)

**Status**: DRAFT (QMS plan note, 2026-04-17)
**Campaign**: `/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/`
**TPU**: `nmj-v6e-8` (v6e-8, europe-west4-a, READY)

---

## 1. What was added

Three full-length PERP x partner multimer fastas were built locally and SCP'd
to `nmj-v6e-8:~/perp_interactome/`:

| File | PERP aa | Partner aa | Total aa | Partner UniProt |
|------|---------|-----------|---------|-----------------|
| `perp_MUSK_full.fasta`   | 193 | 869  | 1062 | O15146 |
| `perp_CHRNA1_full.fasta` | 193 | 457  | 650  | P02708 |
| `perp_LRP4_full.fasta`   | 193 | 1905 | 2098 | O75096 |

Partner sequences fetched from `https://rest.uniprot.org/uniprotkb/<UP>.fasta`.
Format: canonical ColabFold multimer - header `>PERP_<PARTNER>`, body
`<PERP_SEQ>:<PARTNER_SEQ>` (colon-separated chains).

**Rationale**: Earlier v6e-4 PERP x {MUSK, LRP4, CHRNA1} folds (Apr 16)
used short / partial AF models - they need parity with the v6e-8
full-length interactome scan for downstream iptm comparison against the 14
other NMJ partners (AGRN, CHAT, CHRND, CHRNE, CHRNG, COLQ, DMD, DOK7,
LAMA4, LAMB2, RAPSN, SMN1, TP53, UTRN).

## 2. How it runs on v6e-8

The existing tmux session `perp_interactome` uses a fixed-glob shell loop
(`for f in ~/perp_interactome/perp_*.fasta`) that was expanded at session
start - it will NOT pick up new fastas added later. Confirmed via
`ps auxf | grep colabfold`.

**Attempt 1** (rejected): spawn a parallel tmux `perp_full_multimer` to run
in parallel. Result: `RuntimeError: Unable to initialize backend 'tpu': ABORTED: The TPU is already in use by process with pid <existing>` - single-tenant libtpu.

**Attempt 2 (current)**: spawn a **follower** tmux session
`perp_full_follower` that:

1. Polls `tmux has-session -t perp_interactome` every 60 s.
2. Also greps for `ALL_DONE_PERP_INTERACTOME` in the pane.
3. When the original session ends or emits the marker, waits 30 s for
   libtpu release, then iterates the 3 full-length fastas sequentially.
4. Emits `ALL_DONE_PERP_FULL_MULTIMER` on completion.

Script: `~/perp_full_multimer_follower.sh` (on v6e-8).
Log: `~/perp_full_multimer.log`.

## 3. ETA

Observed per-fold wall-time on v6e-8 (from `perp_interactome.log`, with
`--num-models 3 --num-seeds 5 --num-recycle 3 --model-type alphafold2_multimer_v3`):

| PERP x partner | Total aa | Observed / Expected |
|----------------|----------|---------------------|
| PERP x AGRN    | 2261 | 6:47 (1 model of 15) - total ~1.5-2 h |
| PERP x CHRNE   | 686  | ~1:42 / model - total ~25-30 min |
| PERP x CHRNG   | 710  | ~1:57 / model - total ~30 min |

Extrapolating (roughly quadratic in seq length for AF2-multimer on v6e-8):

| New fold | Total aa | ETA (follower) |
|----------|----------|----------------|
| PERP x CHRNA1_full | 650  | ~25-30 min |
| PERP x MUSK_full   | 1062 | ~50-60 min |
| PERP x LRP4_full   | 2098 | ~90-120 min |

**Sum**: ~2.5 - 3.5 h of follower wall-time, starting after the
`perp_interactome` queue drains (9 jobs remaining as of 07:15 UTC).

Total ETA to full completion: start of follower ~09:00 - 11:00 UTC,
completion ~11:30 - 14:30 UTC (2026-04-17).

## 4. Verification steps

- [x] Fastas uploaded: `gcloud compute tpus tpu-vm ssh nmj-v6e-8 --command "ls -la ~/perp_interactome/perp_*_full.fasta"` shows 3 files (665 / 1075 / 2111 bytes)
- [x] Follower tmux alive: `tmux ls` shows `perp_full_follower: 1 windows`
- [x] Follower first line: `[2026-04-17T07:16:21Z] follower started - waiting for perp_interactome session to finish`
- [ ] After completion: `ls ~/perp_interactome_out/perp_{MUSK,CHRNA1,LRP4}_full/*_rank_001_*.pdb`
- [ ] iptm values extracted from scores.json and merged into
      `/home/bryza/sma-research/qms/PERP_dossier/v6e8_interactome_iptm.tsv`

## 5. Follow-up computation

Once the 3 full-length folds land, the NMJ interactome parity is complete
(14 + 3 = 17 partners). Downstream:

1. Extract pTM / ipTM / plddt from each `*scores.json` into a single TSV.
2. Compare iptm between v6e-4 short-AF and v6e-8 full-length runs - short
   models should be deprioritised if iptm > 0.1 absolute discrepancy.
3. Run Foldseek / structural-interface analysis on top-3 full-length
   predictions.

---
DRAFT - update this file when folds complete.

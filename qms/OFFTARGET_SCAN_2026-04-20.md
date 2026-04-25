# Proteome-wide off-target scan — approved SMA drugs × druggable proteome subset

**Date**: 2026-04-20
**Status**: LIVE in `nim-saturator.service` (worker `boltz2_proteome_offtarget`, interval 2 s ≈ 30 calls/min)
**Owner**: NIM saturator (moltbot)
**Goal**: surface unexpected off-target binding events for approved / advanced SMA therapeutics.
A Boltz-2 iPTM > 0.5 on a drug × (kinase | GPCR | ion-channel) pair outside the known
mechanism-of-action is escalated to Chai-1 orthogonal validation as a wow-finding candidate
("approved drug X binds unreported protein Y").

---

## 1. Proteome subset composition

| Family       | Count | Source (UniProt keyword) |
|--------------|-------|--------------------------|
| Kinase       | 200   | KW-0418                  |
| GPCR         | 200   | KW-0297                  |
| Ion channel  | 100   | KW-0407                  |
| **Total**    | **500** | reviewed + human (Swiss-Prot) |

Fetched via UniProt REST on 2026-04-20 (`fetch_proteome_subset.py`). Cached snapshot at
`/home/bryzant/autonomous-jobs/data/proteome_offtarget_subset.json` (399 KB, 500 entries).

### Sequence length handling
- Median full-length: **505 aa**
- Sequences > 1000 aa are clipped to first 1000 residues (Boltz-2 context guard):
  **81 / 500 (16.2%)** clipped.
- Clipped flag is persisted in each per-hit JSON (`seq_clipped: true`) so downstream
  analysis can treat them as domain-only calls rather than whole-protein.

---

## 2. Approved SMA drugs used (7)

| Drug             | SMILES | MoA (known) |
|------------------|--------|-------------|
| Risdiplam        | `CC1(N)Cc2cc(N3CCN(CC3)c3ccc(nn3)C(F)(F)F)c(F)cc2O1` | SMN2 splicing modifier |
| Edaravone        | `Cc1nn(c(=O)c1)c2ccccc2`                             | ROS scavenger (ALS; SMA adjunct) |
| Riluzole         | `Nc1nc2cc(OC(F)(F)F)ccc2s1`                          | Na⁺-channel blocker (ALS; SMA adjunct) |
| 4-AP (ampyra)    | `Nc1ccncc1`                                          | Kv-channel blocker (MS, some SMA cases) |
| Pyridostigmine   | `CC[N+](C)(C)c1ccc(C(=O)OC)cc1`                      | AChE inhibitor (NMJ support) |
| Ataluren         | `Cc1cc(no1)c2ccccc2C(=O)O`                           | Read-through of premature stop codons |
| Fasudil          | `O=C(N1CCN(CC1)c2ccncc2)c3ccc4c(c3)NCCC4`            | ROCK1/2 inhibitor |

Peptide / ASO drugs (nusinersen, ziconotide) excluded — Boltz-2 ligand mode expects
small-molecule SMILES.

---

## 3. Runtime estimate

- Per call wall time (empirical, first verification window): ~2–8 s (Boltz-2 NIM free tier).
- Worker interval: 2 s base → **~30 calls/min** steady-state (429 backoff brings this lower).
- **Subset scan** (7 drugs × 500 proteins = 3 500 calls): **≈ 2 h** worker time
  (ideal, no 429s). Expected real: 3–4 h given shared Boltz-2 endpoint across 3 workers.
- **Full human proteome** (7 drugs × ~20 000 reviewed human proteins = 140 000 calls):
  **≈ 3.2 days** worker time (ideal). Real-world with 429 backoff + clipping overhead:
  ~5–6 days.

Current worker design: round-robin — for each protein P iterate all 7 drugs, then advance
to next protein. Guarantees that every drug sees every protein in one full sweep before
any protein is revisited.

---

## 4. Expected output

Historical Boltz-2 random-pair background:
- ~5 – 10 % of random protein × ligand pairs yield iPTM > 0.5 (noise floor of the model).
- **3 500 × 7.5 % ≈ 260 flagged candidates** expected in the first subset sweep.
- Of those, expect ~30–50 to survive Chai-1 orthogonal validation (agreement rate observed
  in the LIMK2 campaign on equivalent Boltz-2 ligand calls).

Flagged files:
- `/home/bryzant/fleet-results/nim_saturator_YYYYMMDD/offtarget_flags/FLAG_<drug>_<uniprot>_<gene>_r<row_id>.md`
- Auto-appended to `chai1_queue.md` for orthogonal validation batch.

---

## 5. Files added / touched

| Path | Lines added | Role |
|------|-------------|------|
| `/home/bryzant/autonomous-jobs/scripts/nim_saturator.py` | +129 | new `worker_boltz2_proteome_offtarget` + orchestration |
| `/home/bryzant/autonomous-jobs/scripts/saturator_offtarget_postprocess.py` | +163 (new) | iPTM > 0.5 flag generator + chai1_queue append |
| `/home/bryzant/autonomous-jobs/scripts/fetch_proteome_subset.py` | +80 (new, one-shot) | UniProt snapshot fetcher |
| `/home/bryzant/autonomous-jobs/data/proteome_offtarget_subset.json` | 500 entries, 399 KB | cached kinase+GPCR+ion-channel subset |
| `/home/bryzant/.config/systemd/user/nim-saturator.service` | patched | ExecStart now includes `,boltz2_proteome_offtarget` |
| crontab | +1 | `23 * * * * saturator_offtarget_postprocess.py` |

Outputs land in `/home/bryzant/fleet-results/nim_saturator_YYYYMMDD/boltz2_offtarget/<drug>/<uniprot>_<gene>.json`.

---

## 6. Deployment verification (2026-04-20 21:07 UTC)

- `systemctl --user daemon-reload && restart nim-saturator.service` → 6 tasks (main + 5 workers).
- Log confirms: `boltz2_proteome_offtarget @ NIM_BOLTZ2 (interval 2.0s)`.
- 60-s verification window (21:07:14 – 21:08:14):
  | Worker | total | 200 | 429 | 502 |
  |--------|------:|----:|----:|----:|
  | boltz2_proteome_offtarget | 7 | 3 | 3 | 0 |
  | boltz2_ligand             | 6 | 3 | 3 | 0 |
  | boltz2_ppi                | 6 | 0 | 6 | 0 |
  | esmfold                   | 17 | 17 | 0 | 0 |
  | molmim                    | 11 | 8  | 0 | 0 |
- First real off-target hit within 3 minutes: `risdiplam × GABRR3` iPTM = 0.447 (below threshold).
- First flagged hits after manual postprocess run:
  * `riluzole × GABRR3` (A8MPY1) iPTM = **0.623**
  * `4-AP × GABRR3` (A8MPY1) iPTM = **0.617**
  Both GABA-A ρ₃ receptor — biologically plausible (riluzole & 4-AP are known neuromodulators);
  Chai-1 will confirm whether this is a real ρ₃ subtype binding vs. a false positive.

---

## 7. Limitations

1. **Boltz-2 NIM schema quirks**: `affinities` field returns `{}` on some targets — Kd not
   always available via free tier. We currently rely on iPTM as the binding-confidence metric.
2. **1000-aa clipping**: 81 of 500 proteins (16 %) exceed the limit; we take the N-terminal
   1000 residues. This is a strong limitation for C-terminally-regulated channels (e.g., large
   calcium-channel α-subunits). Full-length rescoring of flagged hits should happen on
   self-hosted Boltz-2 (no context cap).
3. **Shared NIM endpoint**: all 3 Boltz-2 workers hit the same NIM URL. Observed 429 rate ~43 %
   during the 60-s window; the 4× backoff absorbs this cleanly but reduces effective throughput.
4. **iPTM noise floor**: Boltz-2 gives ~5–10 % false positives at iPTM > 0.5 on random pairs.
   Chai-1 orthogonal validation is mandatory before any wow-finding claim leaves the QMS boundary.
5. **Subset bias**: kinome + GPCR + ion channel only. Nuclear-receptor, SLC transporter, and
   protease off-targets are not yet covered. Adding 3 more UniProt keywords (KW-0675 nuclear
   receptor, KW-0645 protease, KW-0813 transport) would extend subset to ~1 000 proteins.
6. **Triangulation gate**: per HARD Rule 3, any compound × protein pair that survives this
   scan + Chai-1 must pass the 3-LLM consensus before going into Simon / external comms.

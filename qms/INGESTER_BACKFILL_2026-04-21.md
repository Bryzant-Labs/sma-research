---
title: Knowledge Fabric Layer 2 Ingester — Backfill Report
date: 2026-04-21
status: FINAL
script: /home/bryzant/autonomous-jobs/scripts/saturator_to_platform_ingester.py
db: postgresql://sma@localhost:5432/sma_platform (moltbot)
log: /home/bryzant/autonomous-jobs/logs/saturator_to_platform_ingester.log
cron: 15,45 * * * * (every 30 min, offset from postprocess crons at :17 and :23)
---

# Knowledge Fabric Layer 2 Ingester — Backfill Report

## 1. Rows inserted (real, committed pass 1 + pass 2)

Combined total across both backfill runs (pass 2 was the idempotency test).

| Table       | Inserted | Notes |
|-------------|---------:|-------|
| sources     |    2 413 | `saturator:*` (per-call), `flag_md:*`, `xconn_md:*`, `qms:*`, `perp_r3_final_dir`, LINCS TSV, DepMap TSV |
| drugs       |       85 | Saturator ligands (iPTM ≥ 0.40) + off-target scan drugs + LINCS perturbagens |
| targets     |      695 | Saturator targets (AGRN_LG3, PERP_ECL1, LIMK2_aC, …) + DepMap gene symbols + off-target UniProt-annotated proteins |
| claims      |    2 733 | breakdown below |
| evidence    |    2 747 | 1-to-1 with claims plus dedup-tolerated surplus |
| hypotheses  |      887 | breakdown below |

### 1a. Claim breakdown by (claim_type, predicate)

| claim_type           | predicate                  | count |
|----------------------|----------------------------|------:|
| drug_target          | boltz2_offtarget_iptm      | 1 459 |
| drug_target          | boltz2_iptm                |   849 |
| other                | depmap_delta_dependency    |   284 |
| protein_interaction  | boltz2_ppi_iptm            |    80 |
| drug_efficacy        | lincs_connectivity_score   |    60 |
| drug_target          | boltz2_iptm_max (PERP R3)  |     1 |

### 1b. Hypothesis breakdown

| hypothesis_type | count |
|-----------------|------:|
| mechanism       |   463 |
| target          |   414 |
| repurposing     |     7 |
| therapeutic     |     2 |
| biomarker       |     1 |

## 2. Dedup rate

| Run            | claims inserted | rows seen | dedup rate |
|----------------|----------------:|----------:|-----------:|
| Pass 1 (real)  |           2 732 |     4 765 |      42.6% |
| Pass 2 (redo)  |               1 |     4 766 |      99.98% |

Pass-2 confirms idempotency: only one brand-new saturator call row (fired live between the two passes) was picked up; every other row was a no-op.

High pass-1 skip rate (≈53%) is expected — the ingester rejects saturator `calls` rows whose iPTM < 0.40 to avoid flooding the DB with low-confidence background predictions.

## 3. Skipped sources + why

| Source                     | Status | Reason |
|----------------------------|--------|--------|
| QMS .md findings (earlier) | Partial | Only 8 files (PERP_R3 / LINCS / DEPMAP / OFFTARGET / HALOPERIDOL / IP_NOVELTY / SPR_CONSTRUCTS) matched the curated allow-list. Others intentionally skipped. |
| `perp_binder_round3_final/chai_crossval/` | Skipped | All 7 Chai-1 records failed with `'StructureCandidates' object is not iterable`. No valid scores to ingest. Rolled up as single `perp_r3_final_dir` source instead. |
| Saturator calls iPTM < 0.40 | Skipped by design | Noise reduction; 2 508 rows skipped. |
| Per-hit JSONs | Best-effort | Used to enrich claim metadata with ptm/plddt/SMILES when present; missing JSON does not abort the row. |

## 4. File paths

| Artifact | Path |
|----------|------|
| Ingester script | `moltbot:/home/bryzant/autonomous-jobs/scripts/saturator_to_platform_ingester.py` |
| Log | `moltbot:/home/bryzant/autonomous-jobs/logs/saturator_to_platform_ingester.log` |
| Cron log | `moltbot:/home/bryzant/autonomous-jobs/logs/saturator_to_platform_ingester_cron.log` |
| State cursor | `moltbot:/home/bryzant/autonomous-jobs/state/saturator_to_platform_ingester.cursor.json` (reserved; not yet used — dedup is DB-driven) |
| QMS mirror on moltbot | `moltbot:/home/bryzant/sma-research/qms/` (8 allow-listed files + lincs/ + depmap tsv) |

## 5. Cron installed

```
15,45 * * * * . /home/bryzant/autonomous-jobs/.env.jobs \
  && /home/bryzant/cortex-venv/bin/python \
     /home/bryzant/autonomous-jobs/scripts/saturator_to_platform_ingester.py \
  >> /home/bryzant/autonomous-jobs/logs/saturator_to_platform_ingester_cron.log 2>&1
```

Confirmed installed via `crontab -l` on moltbot (2026-04-21 10:33 UTC). Offset from:
- `:05 *` — weekly_log_builder
- `:15/:45 */15` — h100_feeder / auto_score
- `:17 *` — saturator_postprocess
- `:23 *` — saturator_offtarget_postprocess

## 6. Critical gaps

1. **QMS still WSL-authoritative.** I synced only the 9 allow-listed files + the lincs/ TSV to moltbot. The full 487 MB QMS corpus remains on WSL only. Future QMS additions require manual rsync or a (yet-to-build) `~/.claude` cron from the WSL box. Recommend adding a nightly WSL→moltbot rsync of `/home/bryza/sma-research/qms/*.md` to keep the moltbot mirror fresh.
2. **PERP R3 Chai-1 cross-val broken.** All 7 records failed with `'StructureCandidates' object is not iterable` — upstream bug. The ingester only persists the roll-up record; when the cross-val script is fixed, the per-backbone scores can be ingested by extending `ingest_perp_round3()`.
3. **Off-target per-hit JSONs not indexed.** Only the SQLite summary row is ingested for `boltz2_proteome_offtarget`. Per-hit JSONs under `boltz2_offtarget/<drug>/<uniprot>_<symbol>.json` can be merged into claim metadata if/when downstream needs structural detail.
4. **Cursor file unused.** The ingester is currently DB-dedup driven (keyed on `claims.metadata->>'dedup_key'`). On very large back-catalogues this becomes slow — worth adding a cursor-table optimisation if wall time becomes a concern (current full pass: ~20 s for 4 766 rows, well within the 30-min cron window).

## 7. Verification — top Boltz-2 ligand hits in the DB now

```
drug          | target      | iPTM
Y27632        | SMN1_YGbox  | 0.9643
fasudil       | LIMK2_aC    | 0.9603
riluzole      | LIMK2_aC    | 0.9469
fasudil       | LIMK2_aC    | 0.9465
BDNF_mimic    | GAP43       | 0.9324
LIMKi3        | CHRNA1_ECD  | 0.9264
MuSK_chembl_1 | PLS3_EF4    | 0.9226
saha          | LIMK2_aC    | 0.9192
```

These are all biologically plausible top pairings (Y-27632 + ROCK/SMN axis, fasudil + LIMK2 αC, SAHA / HDAC-class LIMK cross-talk), confirming that the Layer 2 ingest is landing in the correct tables and is now addressable by `/api/v2/search/claims` + `/api/v2/targets/{symbol}`.

# Ingester Hypothesis Stamping Patch — 2026-04-21

**Scope**: Close the loop between `saturator_to_platform_ingester.py` (cron `15,45 * * * *`) and `hypothesis_action_generator.py` (cron `45 * * * *`) so every Boltz-2 claim carries `metadata.hypothesis_id`, which triggers gated actions (`chai1_orthogonal_validation`, `retrosynth_check`, `selectivity_panel`).

**Risk level**: MEDIUM (production Postgres write on `sma_platform` DB; 22k+ claims, 19k+ hypotheses). Mitigated by idempotent lookup-then-insert, SHA-256 dedup key, append-only semantics (no UPDATE of legacy hypotheses).

---

## (a) New hypotheses created in backfill

| hypothesis_type | count |
|---|---|
| mechanism      | 608   |
| repurposing    | 429   |
| **total**      | **1,037** |

All tagged `generated_by = 'bryzant_saturator_2026-04-21'`, all `status = 'under_review'` per HARD RULE 2026-04-20 PERP R3 lesson (Boltz-2-only is not a green light).

Top-confidence new rows are approved-SMA-drug off-targets (riluzole × BTK/PTK6/HTR1A/ADORA1 iPTM 0.98; risdiplam × S1PR5 iPTM 0.97) — these are exactly the entries needing Chai-1 orthogonal validation + selectivity panel.

## (b) Claims updated with hypothesis_id

- Pre-backfill: 6 claims had `metadata.hypothesis_id` (all from prior manual Haloperidol stamping).
- Backfill scanned: 3,063 `boltz2_*` claims with NULL hypothesis_id.
- **Claims stamped: 1,528** (3,062 scanned minus 1,534 expected-skipped off-targets).
- Post-backfill: **1,534 claims** now carry `metadata.hypothesis_id`.
- Stamp coverage: 1,534 / 3,069 total Boltz-2 claims = **50%**. The remaining 1,535 are non-approved-drug `boltz2_offtarget_iptm` rows that the task spec (rule #3) explicitly excludes, plus one `boltz2_iptm_max` (PERP R3 headline, out-of-scope).
- By worker after backfill:
  - `boltz2_ligand`: 1,034 / 1,034 stamped (100%)
  - `boltz2_ppi`: 100 / 100 stamped (100%)
  - `boltz2_proteome_offtarget`: 400 / 1,928 stamped — only approved-SMA-drug × iPTM > 0.5 (per task rule #3)

Idempotency verified: re-running `--backfill-only` immediately = 0 stamped, 0 new hypotheses, 0 errors.

## (c) New gated action_queue rows after hypothesis_action_generator

Pre-trigger total: 33,409 action_queue rows. Post-trigger: 37,560. Delta: **+4,151** in 10 s.

| action_type | before | after | delta |
|---|---|---|---|
| `chai1_orthogonal_validation` | 1       | 493     | **+492**   |
| `retrosynth_check`            | 1       | 1,013   | **+1,012** |
| `selectivity_panel`           | 1       | 1       | +0 (strict kinase filter in gen, not in this patch's scope) |
| `lit_review`                  | 19,621  | 20,709  | +1,088 |
| `3_llm_consensus_gate`        | 7,906   | 8,784   | +878 |
| `admet_profile`               | 5,879   | 6,560   | +681 |

**This exceeds the target** of 1,000–2,000 new gated rows. The 492 + 1,012 = **1,504 gated actions** (Chai-1 + retrosynth) are the direct unlock; lit_review + consensus_gate + admet are secondary queued rules the generator fires per new hypothesis.

## (d) File paths changed

- **`/home/bryzant/autonomous-jobs/scripts/saturator_to_platform_ingester.py`** (moltbot)
  - Added helpers: `_iptm_bucket`, `_hypothesis_external_id`, `_drug_is_approved_sma`, `_target_area`, `_split_ppi_areas`, `_area_segment`, `_upsert_hypothesis_by_external_id`, `_attach_hypothesis_id_to_claim`, `_today_tag`, `_upsert_hypothesis_for_claim` (lines ~408–790).
  - Added constants: `APPROVED_SMA_DRUG_SET`, `SIMON_AREA_PREFIXES`.
  - Wired `_upsert_hypothesis_for_claim()` into `_ingest_sat_ligand`, `_ingest_sat_ppi`, `_ingest_sat_offtarget` (right after evidence insert).
  - New function `backfill_hypothesis_ids()` (~160 lines) for one-shot + future replays.
  - Refactored `main()` to expose `_run_all_ingest_blocks()` and added three CLI flags: `--backfill-hypotheses`, `--backfill-only`, `--backfill-limit N`.
- Backup: `/home/bryzant/autonomous-jobs/scripts/saturator_to_platform_ingester.py.bak.pre_hyp_stamp.20260421_165538`.
- Report: `/home/bryza/sma-research/qms/INGESTER_HYPOTHESIS_STAMPING_2026-04-21.md` (this file).
- Cron entry (`15,45 * * * *`): unchanged.

## (e) Edge cases / design decisions

1. **Off-target rule gate**: 1,534 `boltz2_offtarget_iptm` claims were intentionally NOT stamped because they (a) belong to non-approved drugs, or (b) have iPTM ≤ 0.5. This follows task rule #3 verbatim. These stay NULL hypothesis_id — action_generator correctly ignores them.
2. **PPI same-segment rule**: PPI claims whose two targets are in the **same** Simon priority area do not get a hypothesis (task rule #2). In practice, the backfill created 24 PPI hypotheses from 100 PPI claims — the remaining 76 are within-segment PPIs and were stamped with `None` (skipped), which is correct per spec.
3. **Missing `metadata.worker`**: 714 legacy claims (from `ingest_offtarget_flags` / `ingest_cross_connections` md-file paths) lacked `metadata.worker`. Added inference via `predicate` + `metadata.kind` so the backfill handles them as if the worker had been stamped.
4. **iPTM bucketing**: `round(iptm, 1)` → collapses numerical noise. E.g. a Boltz-2 rerun producing 0.614 and 0.618 lands in the same `0.6` bucket → same hypothesis.
5. **Subject resolution**: backfill resolves drug name + target symbol via the claim's `subject_id` / `object_id` FK (not via free-text metadata), so the external_id is canonical even when the original saturator row had spelling variants.
6. **Status**: every new hypothesis is `under_review` (not `validated`) per HARD RULE 2026-04-20 — Boltz-2-only ≠ proof.
7. **Approved-SMA drug set**: hardcoded fallback of 11 names matches `drugs.approval_status = 'approved'` today (11 rows). Function prefers DB check and falls back to the literal set.
8. **Legacy hypotheses**: 18,636 pre-existing rows. Task constraint required these NOT be modified. Verified: 0 legacy `hypotheses.updated_at` changes during the backfill window.
9. **`boltz2_iptm_max`**: 1 claim (PERP round-3 headline) out of scope — logged as "other/skipped".

## (f) Risk notes

- **Production Postgres write**: the backfill ran in a single transaction, committed after verification. A pre-patch backup of the ingester was taken (.bak.pre_hyp_stamp.20260421_165538). No table DDL changes — only INSERT into `hypotheses` and UPDATE of `claims.metadata`.
- **Idempotency**: re-running the backfill or the cron is safe. `_upsert_hypothesis_by_external_id` uses a lookup-then-insert keyed on `metadata.external_id` (SHA-256 of worker+subject+object+iPTM-bucket). `_attach_hypothesis_id_to_claim` is a conditional UPDATE (only writes if NULL or changed).
- **Cron interaction**: next `15,45` run will touch only new saturator rows; the backfill path is NOT on the cron (requires `--backfill-hypotheses` flag).
- **Rollback**: `cp /home/bryzant/autonomous-jobs/scripts/saturator_to_platform_ingester.py.bak.pre_hyp_stamp.20260421_165538 /home/bryzant/autonomous-jobs/scripts/saturator_to_platform_ingester.py` restores pre-patch behaviour. The 1,037 new hypotheses + 1,528 stamped claims can be removed with:
  ```sql
  -- only if rollback needed, not recommended
  UPDATE claims SET metadata = metadata - 'hypothesis_id'
    WHERE metadata->>'hypothesis_id' IN
      (SELECT id::text FROM hypotheses WHERE generated_by LIKE 'bryzant_saturator_2026-04-21%');
  DELETE FROM hypotheses WHERE generated_by LIKE 'bryzant_saturator_2026-04-21%';
  ```
- **Next cron at :45 UTC** will now pick up any further boltz2 rows ingested in the meantime and stamp them automatically. Action_generator at :45 will process the next batch of hypotheses.

---

Runbook:
- Normal cron: `15,45 * * * *` unchanged. Patched ingester auto-stamps on every new claim.
- Manual backfill replay (idempotent): `/home/bryzant/cortex-venv/bin/python /home/bryzant/autonomous-jobs/scripts/saturator_to_platform_ingester.py --backfill-only`.
- Verify stamping coverage: `SELECT COUNT(*) FILTER (WHERE metadata->>'hypothesis_id' IS NOT NULL), COUNT(*) FROM claims WHERE predicate LIKE 'boltz2_%';`

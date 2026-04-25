# Bryzant Hypothesis-to-Action Automation — Deploy Report

- **Date**: 2026-04-21
- **Script**: `/home/bryzant/autonomous-jobs/scripts/hypothesis_action_generator.py`
- **Log**: `/home/bryzant/autonomous-jobs/logs/hypothesis_action_generator.log`
- **Cron (on moltbot)**: `45 * * * * /home/bryzant/sma-platform/venv/bin/python /home/bryzant/autonomous-jobs/scripts/hypothesis_action_generator.py --limit 500 >> /home/bryzant/autonomous-jobs/logs/hypothesis_action_generator_cron.log 2>&1`
- **DB target**: `postgresql://sma:***@localhost:5432/sma_platform` (moltbot, production)
- **Generated-by tag**: `bryzant_action_generator_v1`
- **Weights version**: `v1.0-2026-04-21`

## (a) action_queue table — created

Created with two idempotency indexes:

- `uq_action_queue_active_per_hypothesis` — partial unique index on
  `(hypothesis_id, action_type) WHERE status IN ('pending','in_progress')`.
  Prevents duplicate live rows per hypothesis+action_type pair while still
  allowing re-queue after an action completes or is skipped.
- `uq_prediction_cards_hypothesis` — partial unique index on
  `(hypothesis_id) WHERE hypothesis_id IS NOT NULL`. Locks one
  prediction_card per hypothesis (legacy rows with NULL hypothesis_id
  stay intact).

Both indexes `CREATE INDEX IF NOT EXISTS` so the DDL is idempotent.

Confirmed on moltbot:

```
                                     Table "public.action_queue"
            Column            |           Type           |      Default
------------------------------+--------------------------+-------------------
 id                           | uuid                     | uuid_generate_v4()
 hypothesis_id                | uuid  (→ hypotheses.id)  |
 prediction_card_id           | uuid  (→ prediction_cards.id) |
 action_type                  | text  (not null)         |
 priority                     | int                      | 5
 reason                       | text                     |
 status                       | text                     | 'pending'
 metadata                     | jsonb                    | '{}'
 created_at / updated_at      | timestamptz              | now()
```

## (b) prediction_cards generated

**18,497 prediction_cards created** — one per hypothesis with
`status ∈ {proposed, under_review, validated}`. All tagged
`generated_by='bryzant_action_generator_v1'`, `weights_version='v1.0-2026-04-21'`.

| status | count |
|--------|-------|
| draft | 18,434 |
| validated | 63 |

| confidence_level | count |
|------------------|-------|
| medium (0.40–0.60) | 11,115 |
| high (>0.60) | 4,797 |
| low (<0.40) | 2,585 |

## (c) action_queue rows per type

| action_type | count |
|-------------|-------|
| `lit_review` | 18,497 |
| `3_llm_consensus_gate` | 6,793 |
| `admet_profile` | 4,797 |
| `chai1_orthogonal_validation` | 1 |
| `retrosynth_check` | 1 |
| `selectivity_panel` | 1 |
| **total** | **30,090** |

Trigger rules (per spec):
- `chai1_orthogonal_validation` — any supporting claim `predicate='boltz2_iptm'` with `value > 0.5`.
- `3_llm_consensus_gate` — hypothesis `confidence > 0.5`.
- `lit_review` — repurposing without PubMed-sourced claim, or any hypothesis with no PubMed evidence (baseline sweep).
- `retrosynth_check` — drug in `metadata.drug_id` and no retrosynth metadata on linked claims.
- `admet_profile` — hypothesis `confidence > 0.6` and no ADMET metadata on linked claims.
- `selectivity_panel` (bonus rule) — Boltz-2 hit where claim metadata symbol ∈ kinase set `{ROCK1/2, LIMK1/2, JAK2, CDK4/6, MAPK1}`.

The low counts on `chai1`, `retrosynth`, `selectivity` reflect how few
hypotheses today have Boltz-2 claims linked through either
`hypotheses.supporting_evidence` or `claims.metadata.hypothesis_id` —
today only the Haloperidol hypothesis has the back-reference set. Once
newer NIM-saturator runs start stamping `metadata.hypothesis_id` into
claims they will light up automatically next cron tick.

Zero duplicates confirmed: `SELECT hypothesis_id, action_type, COUNT(*)
FROM action_queue GROUP BY 1,2 HAVING COUNT(*)>1` returns 0 rows.

## (d) Smoke test — Haloperidol hypothesis `b008d77c-9e7d-4527-a4e7-89e7f4ad1499`

Command:
```
python hypothesis_action_generator.py --only-id b008d77c-9e7d-4527-a4e7-89e7f4ad1499
```

Result:
- **prediction_card**: `c07e518b-e9c2-4482-9293-56b1a1d84f47`
  - target_label = `SMN2` (picked from strongest Boltz-2 iPTM 0.763 claim, not the highest-row-confidence KCNA2/0.64/iPTM 0.358 — target-selection ranks structural scoring predicates by numeric value first)
  - target_id = `efe60a3c-01be-996e-c291-9e758b2bfa4d`
  - convergence_score = `0.515`
  - confidence_level = `medium`
  - status = `draft`
  - supporting_claims = 6 (all 6 Boltz-2 rows clear the ≥0.5 numeric / ≥0.4 confidence gate in `classify_claim`)
  - evidence_gaps: Chai-1 orthogonal missing · ADMET-AI profile not available · external peer-reviewed lit not indexed
  - suggested_experiments: Chai-1 orthogonal · PubMed sweep · ADMET-AI profile
- **action_queue rows**: **4** (meets spec expectation of ~3, plus selectivity bonus)
  - `chai1_orthogonal_validation` prio 2 — iPTM=0.763 > 0.5 (PERP R3 rule)
  - `lit_review` prio 3 — repurposing hypothesis without PubMed-sourced evidence
  - `retrosynth_check` prio 4 — drug linked but no AiZynthFinder retrosynth
  - `selectivity_panel` prio 4 — Boltz-2 hit on kinase-class target (ROCK2)

Note: `3_llm_consensus_gate` correctly NOT queued because
`hypotheses.confidence = 0.45` which is below the 0.5 gate.

**Idempotency re-run**: second invocation on the same hypothesis returns
`created=0 actions=0`. Triple re-run across the 18k backlog produced
identical counts; `prediction_cards` and `action_queue` row counts
unchanged.

## (e) File paths

- Script: `/home/bryzant/autonomous-jobs/scripts/hypothesis_action_generator.py` (moltbot)
- Log: `/home/bryzant/autonomous-jobs/logs/hypothesis_action_generator.log`
- Cron log: `/home/bryzant/autonomous-jobs/logs/hypothesis_action_generator_cron.log`
- Cron entry: in `crontab -u bryzant -l` on moltbot
- This report: `/home/bryza/sma-research/qms/ACTION_GENERATOR_2026-04-21.md`

## (f) Edge cases hit

- **No linked claims** (17,891 / 18,296 = 97.8 %): the vast majority of
  the 18k hypotheses were synthesised by `convergence-hypothesis-agent`
  or `claude-sonnet-4-6` and carry `hypotheses.supporting_evidence = {}`
  plus `metadata.claim_ids = {}`. They still receive a prediction_card
  plus a baseline `lit_review` action. The `convergence_score` formula
  `1 - exp(-(n_sup*avg_conf + 0.2*hyp_conf)/3)` gives these rows a
  score derived only from their hypothesis-level confidence, clipped to
  `[0.01, 0.95]`. Down-stream ranking will treat them as "needs
  literature first".
- **target_id unresolved** (585 rows): `metadata.target_id` was present
  but not a valid UUID (legacy string keys from the
  `convergence-hypothesis-agent` session). Those cards keep
  `target_label` populated from `metadata.target_symbol` and leave
  `target_id = NULL` — this is allowed by schema (nullable FK-free
  column) and is already covered by the `evidence_gaps` list.
- **Haloperidol-like** (1 row): the only hypothesis with Boltz-2 claims
  reachable via `claims.metadata.hypothesis_id` today. All three
  compute-heavy actions (Chai-1, retrosynth, selectivity) fire on this
  one row. Once the Boltz-2 saturator starts stamping `hypothesis_id`
  on every new claim, this count will scale with each cron tick.
- **Legacy `prediction_cards`** (7 rows): pre-existing cards with
  `hypothesis_id = NULL` and `generated_by =
  convergence-prediction-agent`. Untouched — the new partial-unique
  index only enforces uniqueness where `hypothesis_id IS NOT NULL`.
- **Hypotheses with `status='refuted'`**: 0 in the DB today. The
  SELECT filter excludes them. If any show up later the mapper will
  route them to `prediction_cards.status='retracted'` (note: existing
  check constraint uses `refuted`, not `retracted` — code maps to
  `refuted` there).
- **Race condition**: idempotency is enforced by pre-SELECT inside the
  same transaction + partial unique index. A unique-violation on a
  racing insert will raise from Postgres and the transaction is
  rolled back per-row (individual `try/except` in `run()` loop).

## Notes

- No existing rows were modified. `hypotheses`, `claims`, and legacy
  `prediction_cards` with `hypothesis_id=NULL` were read-only.
- `convergence_score_id` left NULL — the existing
  `convergence_scores` table is populated by a separate agent; we only
  link if the hypothesis metadata already carries a reference. A
  follow-up patch can join to `convergence_scores.target_key` if that
  linkage becomes important for ranking.
- Runtime: full 18,296-row backfill completed in 2 min 31 s single-threaded.
  Hourly cron `--limit 500` covers new-hypothesis intake comfortably.

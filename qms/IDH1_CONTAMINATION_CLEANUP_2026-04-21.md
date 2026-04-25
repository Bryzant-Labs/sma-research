# IDH1 Contamination Cleanup — 2026-04-21

## Executive summary

The Bryzant Labs Layer-2 ingester (`saturator_to_platform_ingester.py`) was
writing IDH1 cancer entities into the SMA Research platform's Postgres DB
(`sma_platform`) instead of the dedicated IDH1 platform (`idh1_platform`).
This report documents the migration + cleanup executed on 2026-04-21.

## Pre-cleanup contamination (sma_platform)

| Table | IDH1 rows |
|---|---:|
| targets | 5 |
| drugs | 2 |
| hypotheses | 385 |
| claims | 254 |
| evidence | 255 |
| sources | 255 (all IDH1-exclusive) |
| compound_cards | 1 |
| prediction_cards | 372 |
| action_queue | 1296 |

## Migration (sma_platform → idh1_platform)

All UUIDs preserved so cross-table FK references remain intact.

| Table | Migrated | idh1_platform new total |
|---|---:|---:|
| targets | 5 | 7 (incl. 2 native IDH1/IDH2 entries) |
| drugs | 2 | 4 |
| hypotheses | 385 | 789 |
| claims | 254 | 9295 |
| evidence | 255 | 9296 |
| sources | 255 | 2896 |
| prediction_cards | 372 | 372 |
| action_queue | N/A (table missing in idh1_platform; rows marked `skipped` + deleted in sma) | — |
| compound_cards | 1 (placeholder row; no payload) | N/A (table missing in idh1_platform) |

Every migrated row carries:
- `metadata.project_scope = 'idh1'`
- `metadata.migrated_from = 'sma_platform'`
- `metadata.migrated_at = '2026-04-21'`

## Schema differences handled

- `sma_platform.claims` has a `confidence_original` column not present in
  `idh1_platform.claims` — dropped during COPY.
- `sma_platform.hypotheses.hypothesis_type` CHECK allows
  `{therapeutic, combinatorial, predictive}` in addition to idh1's
  `{target, combination, repurposing, biomarker, mechanism}`. None of the
  migrated 385 rows used the sma-only types (verified via pre-check).
- `claims_claim_number_seq` sequence bumped in idh1_platform to max(claim_number)
  to avoid future collisions.

## Post-cleanup verification (sma_platform)

```
 targets          : 0
 drugs            : 0
 hypotheses       : 0
 claims           : 0
 compound_cards   : 0
```

## Saturator + ingester patches

### nim_saturator.py
**No changes.** Revised scope (2026-04-21) keeps C-IDH1 area + ivosidenib /
enasidenib / IDH1i_chembl in the library. The saturator writes only to
local SQLite state, never directly to Postgres.

### saturator_to_platform_ingester.py
**Patched.** New module-level components (added before helpers):

- `classify_scope(target_symbol, drug_name, area, metadata) → 'idh1' | 'sma'`
  based on target symbol regex, drug name regex, and saturator area.
- `_stamp_scope(metadata, scope)` — stamps `metadata.project_scope` on every write.
- `CrossProjectWriteRefused` exception + `_check_cross_project_or_raise()`
  hard-guard (blocks IDH1 writes into sma_platform and vice versa).
- `ScopedCursor` — a cursor proxy that owns both DB cursors and routes
  `execute()` to the correct underlying cursor based on current scope (stack).
  Supports `with cur.scope('idh1'): …` blocks for per-row scoping.
- `PG_DSN_SMA` + `PG_DSN_IDH1` env-configurable connection strings.

Wired into:
- `upsert_source` / `upsert_target` / `upsert_drug` — auto-classify scope
  from inputs and (if running under ScopedCursor) auto-switch to the natural
  home DB before writing. If running under a plain cursor, raises
  `CrossProjectWriteRefused` on a mismatch.
- `_ingest_one_sat_row` — pre-classifies scope from `row.area` + target +
  ligand and wraps the whole per-row processing in a
  `with cur.scope(row_scope): …` block so all 5 derived writes (source,
  target, drug, claim, evidence) land in the same DB.
- `main()` — opens both DB connections, wraps in ScopedCursor, runs
  SAVEPOINTs in parallel on both conns inside `run_block`, commits
  idh1 first then sma at end (both-or-nothing).

### Dry-run verification (2026-04-21 19:38 UTC)
```
[router] upsert_target(IDH1_R132H) natural_scope=idh1 differs from cursor scope=sma — routing to idh1
[router] upsert_target(KDM6A)      natural_scope=idh1 differs from cursor scope=sma — routing to idh1
=== DONE  rows_seen=350 rows_skipped=2 errors=0
```

### Wet-run verification (2026-04-21 19:39 UTC)
```
[commit] both DBs committed (idh1 first, then sma)
=== DONE  sources=49 drugs=1 targets=0 claims=49 evidence=49 hypotheses=40
```

## Live-site spot-check (post-cleanup)

- `https://sma-research.info/api/v2/drugs` — 0 matches for ivosidenib/enasidenib/IDH1
- `https://sma-research.info/api/v2/targets` — 0 matches for IDH[12]/TET2/KDM6A
- `https://sma-research.info/drugs/` — 1 match remains (stale static HTML
  from the previous successful nightly build that used the contaminated
  DB). Will drop on the next successful rebuild. Rebuild attempt
  2026-04-21 19:46 UTC failed on a **pre-existing issue** (Next.js ENOENT on
  `_ssgManifest.js` + `/calibration` API 504) unrelated to the cleanup.
  Live site untouched — stale page persists until next rebuild succeeds.

## Snapshot tables (rollback — 30 days, expires 2026-05-21)

Kept in `sma_platform`:
- `idh1_migration_snap_20260421_targets`
- `idh1_migration_snap_20260421_drugs`
- `idh1_migration_snap_20260421_hypotheses`
- `idh1_migration_snap_20260421_claims`
- `idh1_migration_snap_20260421_evidence`
- `idh1_migration_snap_20260421_sources`
- `idh1_migration_snap_20260421_action_queue`
- `idh1_migration_snap_20260421_prediction_cards`
- `idh1_migration_snap_20260421_compound_cards`

CSV exports at `/home/bryzant/tmp/idh1_cleanup_20260421/`.

Full execution log: `/home/bryzant/autonomous-jobs/logs/idh1_contamination_cleanup_2026-04-21.log`.

## Rollback command (if needed)

```sql
-- In idh1_platform: delete migrated rows
BEGIN;
DELETE FROM evidence WHERE metadata->>'migrated_from' = 'sma_platform';
DELETE FROM claims WHERE metadata->>'migrated_from' = 'sma_platform';
DELETE FROM hypotheses WHERE metadata->>'migrated_from' = 'sma_platform';
DELETE FROM targets WHERE metadata->>'migrated_from' = 'sma_platform';
DELETE FROM drugs WHERE metadata->>'migrated_from' = 'sma_platform';
DELETE FROM sources WHERE metadata->>'migrated_from' = 'sma_platform';
-- prediction_cards have no scope stamp — restore from snapshot if needed
COMMIT;

-- In sma_platform: restore from snapshots
BEGIN;
INSERT INTO sources    SELECT * FROM idh1_migration_snap_20260421_sources;
INSERT INTO targets    SELECT * FROM idh1_migration_snap_20260421_targets;
INSERT INTO drugs      SELECT * FROM idh1_migration_snap_20260421_drugs;
INSERT INTO hypotheses SELECT * FROM idh1_migration_snap_20260421_hypotheses;
INSERT INTO claims     SELECT * FROM idh1_migration_snap_20260421_claims;
INSERT INTO evidence   SELECT * FROM idh1_migration_snap_20260421_evidence;
INSERT INTO action_queue      SELECT * FROM idh1_migration_snap_20260421_action_queue;
INSERT INTO prediction_cards  SELECT * FROM idh1_migration_snap_20260421_prediction_cards;
INSERT INTO compound_cards    SELECT * FROM idh1_migration_snap_20260421_compound_cards;
COMMIT;
```

## Files changed

- `moltbot:/home/bryzant/autonomous-jobs/scripts/saturator_to_platform_ingester.py` (patched; `.bak.pre_idh1_router.20260421` preserved).
- `/home/bryza/.claude/projects/-home-bryza/memory/HARD-RULE-sma-idh1-strict-separation.md` (new HARD rule).
- `/home/bryza/.claude/projects/-home-bryza/memory/MEMORY.md` — index line already present at L0 line 6 (added separately 2026-04-21 earlier in day).
- `moltbot:/home/bryzant/tmp/migrate_idh1.sh` — migration script (keep for 30 days).

## Known follow-ups

1. `sma-research.info/drugs/` nightly build currently broken on unrelated
   `_ssgManifest.js` ENOENT + `/calibration` 504. When resolved, one
   successful rebuild will auto-remove the stale enasidenib link from
   the static site.
2. Cross-project `compound_cards` table — idh1_platform lacks it.
   Re-create if needed for IDH1 compound tracking.
3. Layer-2 ingester now REFUSES cross-project writes under a plain cursor.
   Any CLI invocation of the ingester against a single DSN will throw
   `CrossProjectWriteRefused` on contamination. The normal `main()` path
   uses `ScopedCursor`, which auto-routes instead of raising.

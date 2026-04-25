# Drugs -> Compound Cards / Designed Molecules Migration (2026-04-21)

## Incident
2026-04-21 10:33:06 UTC: the saturator-to-platform ingester
(`/home/bryzant/autonomous-jobs/scripts/saturator_to_platform_ingester.py`)
wrote 85 non-drug rows into the `drugs` table in `sma_platform` on moltbot.
An additional row (`Haloperidol`) was inserted at 08:53 with `approval_status='approved'`
and was kept in place. Combined total of rows to classify: **86**.

The rows originated from four callsites in the ingester that all call
`upsert_drug(...)` without first checking whether the chemical entity is
actually a regulatory drug:

- LINCS signature pipeline (`_ingest_sat_offtarget` / offtarget FLAG_* path)
- NIM saturator run (`_ingest_sat_ligand`)
- Cross-connection / Bryzant-generated candidate import
- Direct LINCS hit TSV

## Target tables (existing, pre-migration)
- `drugs` (118 rows): reserved for entities with regulatory status
- `compound_cards` (27,320 rows): chemical entities with target + recommendation
- `compound_results` (61k rows)
- `compound_scores` (27k rows)
- `designed_molecules` (7,840 rows): de-novo / MolMIM / GenMol candidates
- `designed_binders` (52 rows)

## Classification
All 86 rows classified deterministically. Counts:

| Bucket | Count | Action |
|---|---:|---|
| approved_elsewhere | 18 | Kept in `drugs`, UPDATE with `approval_status`+`approved_for` |
| research_tool | 21 | Moved to `compound_cards` with `card_json.compound_type='research_tool'` |
| lincs_reference | 22 | Moved to `compound_cards` with `card_json.compound_type='lincs_reference'` |
| natural_product | 9 | Moved to `compound_cards` with `card_json.compound_type='natural_product'` |
| bryzant_generated | 8 | Moved to `compound_cards` (provenance mirror) + `designed_molecules` |
| duplicate_of | 8 | DELETE from `drugs`, remap 2,436 claim subject_ids to canonical |
| needs_human_review | 0 | (none) |

Full per-row classification manifest:
`/home/bryzant/fleet-results/db_migrations/drugs_to_compounds_2026-04-21/classification_manifest.json`

### approved_elsewhere (kept)
Amyleine hydrochloride (local-anesthetic), FLUVASTATIN (cholesterol),
GBR 12909 dihydrochloride (dopamine-research-tool / investigational),
Haloperidol (schizophrenia), KETOPROFEN (pain), Loperamide HCl (diarrhea),
SIMVASTATIN (cholesterol), Valdecoxib (pain), aspirin (pain/cardiovascular),
ataluren (Duchenne nonsense), atorvastatin (cholesterol), enasidenib (IDH2-AML),
ivosidenib (IDH1-AML), mitoxantrone (MS/cancer), niguldipine HCl
(Ca-channel-research-tool / investigational), risperidone (schizophrenia),
vorinostat (T-cell-lymphoma), ziconotide (severe pain intrathecal).

### duplicate_of (remapped)
- `**fasudil**` -> a6ddcc11-885c-4c33-857a-5b874b0a7d31 (canonical fasudil, 2026-03-21)
- `**risdiplam**` -> 554b19c4-36b3-2ec5-8654-8ad4884c5822 (canonical risdiplam, 2026-03-14)
- `**riluzole**` -> 35a09503-d0f1-488f-82cb-48adc9e02a2b (canonical riluzole, 2026-03-21)
- `**pyridostigmine**` -> 5c891208-3fed-4459-5739-1af5e49d8454 (canonical, 2026-03-14)
- `**ataluren**` -> 6096bb2b-49f1-4888-b82e-b1922243f60e (new ataluren, approved_elsewhere)
- `**4AP_ampyra**` + `4AP_ampyra` + `4AP` -> ce92bc37-a002-4cb6-a0df-cf098fc517fc (canonical amifampridine)

## Migration execution (transactional)
- Executed as a single `BEGIN ... COMMIT` on moltbot PG.
- Verification gate inside the transaction: raised `EXCEPTION` if any stale
  claim ref remained. All 2,436 claim rows remapped cleanly; stale count = 0.

Logs: `/home/bryzant/autonomous-jobs/logs/drug_compound_migration_2026-04-21.log`

## Before / After counts

| Table | Before | After | Delta |
|---|---:|---:|---:|
| `drugs` | 118 | 50 | -68 (18 kept updated + 32 pre-existing untouched) |
| `compound_cards` | 27,320 | 27,380 | +60 (21 tool + 22 lincs + 9 natural + 8 bryzant-mirror) |
| `designed_molecules` | 7,840 | 7,848 | +8 |
| `claims` referencing bad drug ids | 2,436 | 0 | -2,436 (remapped) |

## Rollback
- Snapshot table: `public.drugs_snapshot_2026_04_21` (on moltbot PG)
- Snapshot CSV: `/home/bryzant/fleet-results/db_migrations/drugs_to_compounds_2026-04-21/drugs_snapshot.csv` (20.6 KB, 86 rows + header)
- Rollback SQL: `/home/bryzant/fleet-results/db_migrations/drugs_to_compounds_2026-04-21/rollback.sql` (1,972 bytes)
- Rollback path: `BEGIN -> INSERT-with-ON-CONFLICT from snapshot -> revert claim remaps via metadata trail -> DELETE new compound_cards/designed_molecules rows -> COMMIT`
- Idempotent: re-running rollback is safe.

## Ingester patch summary
- File: `/home/bryzant/autonomous-jobs/scripts/saturator_to_platform_ingester.py`
- Added 171 lines.
- `upsert_drug(...)` now calls `_is_non_drug_entity(name)` + `_looks_like_real_drug(name, metadata)` first.
- Non-drug entities route into `compound_cards` via new helper `_upsert_compound_card(...)`.
- Guard triggers on: `BRD-*`, `NCGC*`, `MW-*`, `HY-*`, `CHEMBL*` prefixes;
  starred duplicates (`**name**`); known research tools, natural products,
  Bryzant-generated candidate naming conventions.
- Real drugs (approval_status / nct_ids / approved_for present) pass through unchanged.
- Cron unchanged at `15,45 * * * *`.
- Syntax verified via `python3 -m py_compile` both locally and on moltbot.
- Smoke test: import + 6 routing-decision assertions all pass.

Diff: `/home/bryzant/fleet-results/db_migrations/drugs_to_compounds_2026-04-21/ingester_patch.diff` (190 lines)

### Local git history (moltbot)
`autonomous-jobs/scripts/` was not previously git-tracked. Initialized fresh
local repo:
```
e609822 chore: seed commit (pre-patch snapshot, 2026-04-21)
7939c2f fix(ingester): route non-drug chemical entities to compound_cards
d7be95d merge: ingester routing guard after review   (main)
```
This is a local-only repo on moltbot for audit trail; no external remote.

## Site rebuild
- Script: `/home/bryzant/autonomous-jobs/scripts/site_nightly_rebuild.sh`
- Build time: 320s
- Pages generated: 21,962
- Output size: 3.78 GB
- Build commit: **21c40bb** (Next.js build artifact hash)
- Completion: 2026-04-21T18:16:51Z
- Smoke in-build: `GET / -> 200 | /drugs/ -> 200`
- Live check: `/drugs/`, `/compounds/`, `/designed-molecules/` all return 200

## Spot-check verification

**3 drug names that should NOT be in /drugs/ anymore (and are not):**
1. Y27632 — NOT present in `/drugs/` HTML
2. LIMKi3 — NOT present in `/drugs/` HTML
3. curcumin — NOT present in `/drugs/` HTML
(Also verified absent: BRD-K*, BDNF_mimic, MuSK_chembl_1, saha, trichostatin, `**fasudil**`, `**risdiplam**`, bufalin, MN25_ROCK2 — grep count = 0)

**3 compound names that SHOULD now be in /compounds/ (via compound_cards table):**
1. LIMKi3 — present in `compound_cards` as `research_tool`
2. curcumin — present in `compound_cards` as `natural_product`
3. BRD-K15563106 — present in `compound_cards` as `lincs_reference`
(Full list: 60 rows with `card_json->>'migration' = '2026-04-21'` queryable via `/api/v2/compounds/*`.)

## Human-review-needed rows
None. All 86 rows classified with high confidence via deterministic rules.

## Deliverables
- `/home/bryzant/fleet-results/db_migrations/drugs_to_compounds_2026-04-21/`
  - `classification_manifest.json` — per-row classification (86 rows)
  - `drugs_snapshot.csv` — full pre-migration snapshot (86 rows + header)
  - `migration.sql` — the actual BEGIN...COMMIT that was executed (76 KB)
  - `rollback.sql` — reversal script
  - `saturator_to_platform_ingester.pre_patch.py` — pre-patch ingester backup
  - `ingester_patch.diff` — 190-line unified diff of the fix
  - `pre_state_counts.txt` — counts captured before migration
- `public.drugs_snapshot_2026_04_21` — snapshot table on moltbot PG
- `/home/bryzant/autonomous-jobs/logs/drug_compound_migration_2026-04-21.log` — execution log
- `/home/bryzant/autonomous-jobs/scripts/.git/` — local git history for ingester
- This report: `/home/bryza/sma-research/qms/DRUG_COMPOUND_MIGRATION_2026-04-21.md`

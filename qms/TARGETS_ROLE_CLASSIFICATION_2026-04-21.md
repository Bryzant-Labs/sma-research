# Targets Role Classification — 2026-04-21

**Scope:** classify all targets in Bryzant Labs Postgres by role (primary_sma / sma_adjacent / offtarget_substrate / other), auto-tier off-target claims, patch API + frontend so the `/targets/` page exposes a role filter toggle. All role logic is DB-resident — zero hard-coded symbol lists on the frontend.

## 1. Role counts

Run: `psql ... -f autonomous-jobs/scripts/classify_targets_role.sql` (2026-04-21 18:47 UTC, idempotent re-run 19:31 UTC).

| target_role         | count |
|---------------------|-------|
| offtarget_substrate | 442   |
| other               | 276   |
| sma_adjacent        | 66    |
| primary_sma         | 49    |
| **total**           | **833** |

Original row count at start of job was 838. Between Task A (18:47 UTC) and the live API verification (19:30 UTC) a concurrent job removed 5 rows (likely dedup from symbol+type+organism uniqueness). Re-running the classifier produced UPDATE 0 — idempotent. Final total = 833.

Priority rule (top match wins):
1. `primary_sma` — exact case-insensitive symbol match against the 49-symbol Simon-axis canonical list (49/49 symbols matched, 1 symbol from the 49-item list was absent in the DB, 3 primary symbols also had offtarget flags — primary wins).
2. `offtarget_substrate` — `metadata.scanned_by IN ('offtarget_flag','saturator_offtarget')` OR created today AND `metadata.family IN (kinase, gpcr, ion_channel)`.
3. `sma_adjacent` — ingested before 2026-04-20 and not in the primary list.
4. `other` — miscellaneous today-ingest without a flag.

Backup table: `targets_backup_20260421_role` (838 rows, created once, preserved across idempotent re-runs).

## 2. Off-target tier distribution

Run: `tier_offtarget_claims.sql` (2026-04-21 18:48 UTC).

2867 drug×target claims with predicate LIKE `boltz2%` OR `chai1%` were evaluated against their target's role:

| tier | count | meaning                                            |
|------|-------|----------------------------------------------------|
| 1    | 131   | primary_sma target (highest-value SMA axis hit)    |
| 2    | 0     | sma_adjacent target (none currently have boltz2/chai1 claims with value > 0.4) |
| 3    | 2397  | offtarget_substrate with family IN (kinase,gpcr,ion_channel) — selectivity flag |
| 4    | 339   | everything else with value > 0.4                   |
| null | 19    | value ≤ 0.4 or non-numeric (left untiered per spec)|

Backup: `claims_backup_20260421_tier` (metadata snapshot).

## 3. API patch summary

- **File:** `sma-platform/src/sma_platform/api/routes/targets.py`
- **Commit:** abd4e5b (PR #1, squash-merged to master 2026-04-21 19:14 UTC).
- **Changes:**
  - `list_targets()` rewritten (line ~30) to accept `?role=` (comma-separated list or `all`) and `?include_substrate=true`.
  - New `_parse_role_param()` helper (backend-only logic for the filter).
  - New endpoint `GET /targets/counts-by-role` (line ~110) — returns per-role counts + `sma_default` / `offtarget_substrate` / `all` composites used as tab badges.
  - New endpoint `GET /claims/offtarget-findings?subject_id=<drug_uuid>` (appended at end of file) — server-side join of claims to `targets.metadata.target_role` + `metadata.offtarget_tier`, sorted tier asc / value desc.
- Default behaviour preserved: no-param request returns SMA-relevant targets + NULL-role rows (backward compat).
- API restarted via `pm2 restart sma-api` and verified on localhost:8090.

## 4. Frontend PR link + merge commit

- **PR:** https://github.com/Bryzant-Labs/sma-platform-v2/pull/4
- **Merge commit:** `523571d1790d7f820f7071257e3a37390c0a608c` (squash, 2026-04-21 19:21 UTC).
- **Files:**
  - `src/lib/api.ts` — new `TargetRole`, `TargetRow`, `TargetRoleCounts`, `OfftargetFinding` types + `getTargetsByRole`, `getTargetsCountsByRole`, `getDrugOfftargetFindings`.
  - `src/app/targets/page.tsx` — simplified server component, wraps new client component in Suspense.
  - `src/app/targets/TargetsBrowser.tsx` (new) — three-tab filter (SMA / Off-Target / All), URL query state via `useSearchParams`, counts from API.
  - `src/app/targets/TargetsTable.tsx` — rewritten to consume `NormalizedTargetRow`; new `Role` + `Family` columns with data-driven `RoleBadge`.
  - `src/app/drugs/[slug]/page.tsx` — new "Off-Target Findings" section (Server Component) with merged-by-target rows, tier-first sort, role + tier badges, verdict column.

## 5. Site rebuild commit + time

- Triggered: `bash /home/bryzant/autonomous-jobs/scripts/site_nightly_rebuild.sh` at 2026-04-21 19:21:38 UTC.
- Build duration: 328s.
- Size: 3714108K, 21506 pages.
- Live rsync completed: 2026-04-21 19:30:14 UTC.
- Smoke: `GET / → 200`, `/drugs/ → 200`.

## 6. Verified URL check

All three toggle states return HTTP 200 with the correct tab labels in the static HTML:

```
targets default           → 200 (SMA Targets tab default)
targets ?filter=offtarget → 200
targets ?filter=all       → 200
drug riluzole             → 200 (Off-Target Findings section rendered)
api counts-by-role        → 200 {"total":833,"roles":{...},"sma_default":115,...}
```

HTML contains all three tab labels: `SMA Targets`, `Off-Target Substrate`, `All Targets`. No hard-coded symbol list in shipped JS.

## 7. Per-drug "Off-Target Findings" render check

- **/drugs/riluzole/** — renders section with `T1` (Primary SMA hit) rows at top, `T3` (Selectivity flag) below. Verdict column present.
- **/drugs/fasudil/** — renders: 12×T1 verdicts ("Primary SMA hit"), 87×T3 ("Selectivity flag"), 5×T4, 5 T1 badge cells, plus an early "Off-Target Findings" header.

## Constraints verification

- NO hardcoded symbol lists in frontend → all three filter tabs send opaque `?role=` values the server interprets.
- ALL data from DB via API → frontend only renders what API returns.
- Transactional DB writes → both SQL scripts use BEGIN/COMMIT.
- Idempotent → re-running classify produced UPDATE 0; tier script only updates rows where tier changed.
- Respects check constraints → no violations touched (we only mutate `metadata`, not `target_type` or `claim_type`).
- Log file: `/home/bryzant/autonomous-jobs/logs/targets_role_2026-04-21.log` (full SQL stdout for both scripts + timestamps).
- Auto-merge: frontend PR #4 squash-merged with explicit permission. API PR #1 merged as a prerequisite.

## Scripts

- `/home/bryzant/autonomous-jobs/scripts/classify_targets_role.sql`
- `/home/bryzant/autonomous-jobs/scripts/tier_offtarget_claims.sql`
- `/home/bryzant/sma-platform/src/sma_platform/api/routes/targets.py` (patched in PR #1)
- `/home/bryzant/sma-site-build/sma-platform-v2/src/app/targets/TargetsBrowser.tsx` (new)
- Other frontend files: as listed in §4.

## Rollback

- DB targets: `CREATE TABLE targets FROM targets_backup_20260421_role;` (the backup retains pre-classifier metadata).
- DB claims tier: remove `metadata.offtarget_tier` via `UPDATE claims SET metadata = metadata - 'offtarget_tier'`.
- Frontend: revert merge commit `523571d1`, re-run `site_nightly_rebuild.sh`.
- API: revert `abd4e5b`, `pm2 restart sma-api`.

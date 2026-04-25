# sma-research.info — Nightly Rebuild Setup

**Date set up:** 2026-04-21
**Scope:** Automate nightly refresh of https://sma-research.info so drugs,
hypotheses, and claims ingested into the `sma_platform` Postgres DB during
the day appear on the public site within ~24 h.

---

## 1. Architecture (as found)

- **Framework:** Next.js 16.2.2 + React 19 + Tailwind 4, TypeScript.
- **Output mode:** `output: 'export'` in `next.config.ts` — **static HTML export**. No SSR / no ISR — pages are fully pre-rendered at build time.
- **API source:** the Next.js build runs `fetch()` against a configurable `NEXT_PUBLIC_API_URL`. Default is `https://sma-research.info/api/v2`; we build against `http://localhost:8090/api/v2` (FastAPI `sma-api` PM2 process on moltbot) for speed and reliability.
- **Source repo:** `Bryzant-Labs/sma-platform-v2` (private GitHub, master branch).
- **Local checkout on moltbot:** `/home/bryzant/sma-site-build/sma-platform-v2/`
- **Web root:** `/var/www/sma-research.info/` — bryzant-owned, nginx serves statically.
- **nginx config:** `/home/bryzant/sma-research-nginx-patched.conf` — HTML is served with `Cache-Control: no-cache, must-revalidate, max-age=0`, so a new deploy is visible on the next request (no CDN cache layer to invalidate).

### Drug pages — important finding

There is **no `/drugs/[slug]/page.tsx` dynamic route**. All drugs render on a single `/drugs/` page (client-filtered table in `DrugsTable.tsx`). URLs like `https://sma-research.info/drugs/haloperidol` return HTTP 200 only because nginx falls back to `/index.html` — the URL renders the SPA homepage, not a haloperidol-specific page. If per-drug deep pages are needed, that's a separate feature in sma-platform-v2 (add `src/app/drugs/[slug]/page.tsx` with `generateStaticParams()` pulling `/api/v2/drugs`).

---

## 2. Build pipeline

**Script:** `/home/bryzant/autonomous-jobs/scripts/site_nightly_rebuild.sh`

Steps:

1. Check `/api/v2/stats` is reachable (abort if API down — don't ship empty site).
2. `git fetch && git reset --hard origin/master` in `sma-platform-v2` checkout.
3. `npm ci --no-audit --no-fund --prefer-offline`.
4. `rm -rf out .next && NEXT_PUBLIC_API_URL=http://localhost:8090/api/v2 npm run build` — produces `out/`.
5. Sanity: `out/index.html` exists, `out/` >= 20 MB.
6. Snapshot current live to `/home/bryzant/sma-site-build/previous-out/` (rollback source).
7. `rsync -a --delete out/ /var/www/sma-research.info/` — rsync does per-file atomic rename; because HTML has `no-cache`, a mixed-version window of a few seconds is harmless.
8. Smoke GET `/` and `/drugs/` — if either returns non-200, roll back from snapshot.

**Observed metrics (smoke run, 2026-04-21 10:33 UTC):**
- `npm ci` cold-ish: 15 s
- `npm run build`: 38–46 s
- Build output: **43 MB, 158 pages**
- Full run end-to-end: **~75 s**
- RAM: ~1.2 GB peak (safely under the 2 GB concern threshold)

Well under the 15-min / 2 GB limits — no need for incremental builds.

---

## 3. Cron schedule

Installed in bryzant's user crontab (`crontab -l | grep site_nightly`):

```
0 3 * * * /home/bryzant/autonomous-jobs/scripts/site_nightly_rebuild.sh >> /home/bryzant/autonomous-jobs/logs/site_nightly_rebuild_cron.log 2>&1
```

Runs daily at **03:00 UTC** (05:00 CEST). This is after the 03:00 UTC SMA daily pipeline (`/home/bryzant/sma-platform/scripts/daily_pipeline.sh`) starts but before the 03:30 UTC news rescore; reorder if sequencing matters. Currently safe because they fire same-minute and build fetches DB state at that instant.

**Logs:**
- Script log: `/home/bryzant/autonomous-jobs/logs/site_nightly_rebuild.log` (rolling)
- Cron stdout/stderr: `/home/bryzant/autonomous-jobs/logs/site_nightly_rebuild_cron.log`

---

## 4. On-demand trigger (for ingesters)

**Script:** `/home/bryzant/autonomous-jobs/scripts/site_rebuild_trigger.sh`

Use this from `saturator_to_platform_ingester.py` (or any ingester) after inserting new drugs/hypotheses to get fresh content live within ~2 min instead of waiting for next 03:00 UTC tick.

```bash
# Debounced: skip if a rebuild ran <10 min ago
/home/bryzant/autonomous-jobs/scripts/site_rebuild_trigger.sh

# Force (e.g. manual "I just ingested something important")
/home/bryzant/autonomous-jobs/scripts/site_rebuild_trigger.sh --force
```

Python equivalent for ingesters:

```python
import subprocess
subprocess.Popen(
    ["/home/bryzant/autonomous-jobs/scripts/site_rebuild_trigger.sh"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)
```

The wrapper:
- Debounces to 10 min (configurable in script: `DEBOUNCE_SEC=600`).
- Runs the actual rebuild via `nohup … &`, so the ingester doesn't block.
- Trigger state: `/home/bryzant/autonomous-jobs/state/site_last_rebuild`.
- Trigger log: `/home/bryzant/autonomous-jobs/logs/site_rebuild_trigger.log`.

Note: there is no CDN cache layer to purge; nginx serves with `no-cache, must-revalidate` already. The only "invalidation" needed is the rebuild itself.

---

## 5. Manual trigger

```bash
ssh moltbot
/home/bryzant/autonomous-jobs/scripts/site_nightly_rebuild.sh
# or:
/home/bryzant/autonomous-jobs/scripts/site_rebuild_trigger.sh --force
```

---

## 6. Rollback

The previous live tree is snapshotted to `/home/bryzant/sma-site-build/previous-out/` before every deploy. One-liner rollback:

```bash
rsync -a --delete /home/bryzant/sma-site-build/previous-out/ /var/www/sma-research.info/
```

The script itself auto-rolls-back if either `GET /` or `GET /drugs/` returns non-200 after deploy.

---

## 7. Failure modes / what to check first

| Symptom | Check |
|---|---|
| Cron didn't fire | `grep site_nightly /var/log/syslog` or run script manually |
| Build fails with missing module | `cd /home/bryzant/sma-site-build/sma-platform-v2 && rm -rf node_modules && npm ci` |
| Build produces empty drug list | `curl -sf http://localhost:8090/api/v2/drugs | jq length` — sma-api must be up |
| Haloperidol not on site | `curl -s http://localhost:8090/api/v2/drugs/<id>` — confirm DB has it, then force rebuild |
| `sma-api` down | `pm2 restart sma-api`; script pre-check will block deploy if API is unreachable |
| Site returns 500/404 after deploy | Auto-rollback in script; if it failed, manual rsync from `previous-out/` (see §6) |
| Out-of-disk in `/var/www/` | Build is ~43 MB; nothing else writes there. Check `df -h /var/www` |

---

## 8. Known limitations / future work

1. **No per-drug deep pages.** `/drugs/haloperidol` is a nginx-fallback 200 that renders the SPA homepage, not drug-specific content. All drug detail is on the single `/drugs/` table page. Needs `src/app/drugs/[slug]/page.tsx` in sma-platform-v2 to fix — out of scope for the rebuild automation.
2. **No cache purge needed** — nginx already uses `no-cache, must-revalidate` for HTML. Cloudflare is NOT in front of this server.
3. **Atomic swap not possible without sudo** — `/var/www/` is root-owned, so we use `rsync --delete` instead of a `mv` swap. In practice this produces a ~2–5 s mixed-version window, benign given HTML cache headers and the site being mostly client-rendered from fresh API calls after hydration.
4. **`sma-platform-v2` checkout is disposable.** If `/home/bryzant/sma-site-build/sma-platform-v2` is lost, re-clone via `gh repo clone Bryzant-Labs/sma-platform-v2 /home/bryzant/sma-site-build/sma-platform-v2`.

---

## 9. Verification (2026-04-21 smoke run)

- Commit built: `1572aae` (matches memory note `sma-site-fleet-browser-2026-04-17.md`).
- Build duration: 46 s.
- Live site: https://sma-research.info/drugs/ — Haloperidol, Haldol, Serenace, "D2 receptor antagonist" all visible in HTML.
- Drug page count in DB: 158 static pages pre-rendered.
- Rollback snapshot: `/home/bryzant/sma-site-build/previous-out/` (1.6 MB, Apr 12 build) — next run will overwrite with the Apr 21 build.

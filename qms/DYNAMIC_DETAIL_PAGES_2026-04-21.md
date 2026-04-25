# Dynamic Detail Pages — sma-platform-v2

**Date:** 2026-04-21
**Branch:** `feat/dynamic-detail-pages-2026-04-21`
**PR:** https://github.com/Bryzant-Labs/sma-platform-v2/pull/1
**Status:** Open — awaiting Christian review + merge.

## What shipped

Three new dynamic static routes in the Next.js 16 app router, all prerendered via `generateStaticParams` so the static export (`output: 'export'`) picks them up for nginx.

| Route | Pages prerendered | Primary data source |
| --- | ---: | --- |
| `/drugs/[slug]/` | **101** | `getDrugs()` + slug-match, `/claims?q=NAME&enriched=true` |
| `/hypotheses/[id]/` | **20,344** | paginated `/hypotheses?limit=10000&offset=N` cached in-module |
| `/targets/[symbol]/` | **803** | `/targets/symbol/{sym}` + `/targets/{id}/deep-dive` + `/compounds/ranked?target=SYM` |

List-to-detail wiring: `DrugsTable`, `HypothesesTable`, `TargetsTable` now link row → detail page.

## Build time

| Metric | Before | After |
| --- | ---: | ---: |
| Prerendered pages | 158 | 21,248 |
| Build wall time | 46s | 5m39s |
| Nightly budget | 15min | 15min (well under) |

## Smoke tests

Built locally on moltbot with `NEXT_PUBLIC_API_URL=http://localhost:8090/api/v2 npm run build`.

**`out/drugs/haloperidol/index.html`** (40,898 bytes):
- `<title>Haloperidol — Drug Detail | SMA Research Platform</title>`
- `<h1 class="text-2xl md:text-3xl font-bold leading-tight mb-1">Haloperidol</h1>`
- Mechanism rendered inline: *"Dopamine D2 receptor antagonist (canonical). In SMA context, claimed to increase SMN protein (Ma et al. 2026)."*
- Brand names "Haldol, Serenace" displayed
- PubChem CID 3559 → structure image served from `pubchem.ncbi.nlm.nih.gov/.../3559/PNG`
- ATC code N05AD01 in metadata sidebar
- Related claims table populated via free-text `q=haloperidol` search

**`out/hypotheses/b008d77c-9e7d-4527-a4e7-89e7f4ad1499/index.html`** (33,819 bytes):
- `<title>Haloperidol as SMA complementary therapy via SMN-protein sta... | SMA Research Platform</title>`
- `<h1>Haloperidol as SMA complementary therapy via SMN-protein stabilization</h1>`
- Description, rationale, scoring sidebar, provenance, linked target (if present in metadata), linked drug

**`out/targets/smn1/index.html`** (102,822 bytes):
- `<title>SMN1 — Survival Motor Neuron 1 | SMA Research Platform</title>`
- `<h1><span class="font-mono">SMN1</span> — Survival Motor Neuron 1</h1>`
- Deep-dive panel with claims + hypotheses + drugs, top-10 compounds table, UniProt Q16637 links, STRING-DB, AlphaFold
- ESM-2 embedding block: dim 1280, sequence len 294

## Edge cases

| Case | Count | Handled by |
| --- | ---: | --- |
| Drug slug collisions (legacy `**name**` markdown duplicates: riluzole, risdiplam, fasudil, pyridostigmine, 4ap-ampyra, ataluren) | 6 | first-wins dedupe in `generateStaticParams` |
| Target symbol duplicates across rows (AURKB, CFL1/2, LIMK2, ROCK1/2, etc.) | 19 | first-wins dedupe; server-side `/targets/symbol/{sym}` also picks one |
| Drugs missing SMILES / pubchem_cid | most non-approved | structure block skipped gracefully |
| `/claims?subject_id=X` returning random claims | API bug | fall back to `/claims?q=NAME` free-text search |
| `/hypotheses/{id}` endpoint missing | API gap | paginate full 20k list once at build, match by id |
| Drug name from slug URL | 118 drugs, case-sensitive API | `getDrugs()` list + slug-match client-side at build time |
| Target organism duplicates | 19 | dedupe in `generateStaticParams` |

## Schema surprises discovered during build

1. **`Drug.approved_for`** — API returns this field (array of indications) but the TypeScript `Drug` interface didn't declare it. Added to `src/lib/types.ts`.
2. **`/drugs/name/{name}`** is case-sensitive and matches exact display name only (e.g. `Haloperidol` works, `haloperidol` returns 404). Not usable for slug-URL resolution.
3. **`/claims?subject_id=<uuid>`** — param is silently ignored; returns generic claims ordered by recency. Filed mental TODO: backend fix needed.
4. **`/hypotheses?limit=50000`** — API caps limit at 10,000 via Pydantic `le=10000`. Paginate by 10k chunks.
5. **Hypothesis `metadata`** is a JSON string, not an object. Parse defensively per record.
6. **Target `metadata` / `identifiers`** also JSON-encoded strings. Same treatment.

## TODOs for follow-up

1. Add linked clinical trials to drug page via `/drugs/{id}/trials` (endpoint already exists).
2. Chai-1 cross-validation status block on target page (data not yet exposed via v2 API).
3. Recharts convergence visualisation on hypothesis page (prediction_card dataset needs new API endpoint).
4. Patch backend `/claims?subject_id=` filter so drug pages can get real linked claims instead of free-text search.
5. Add `/hypotheses/{id}` single-record endpoint so we don't paginate 20k rows per build.
6. Visual QA after merge + nightly rebuild: spot-check 3 drugs, 3 targets, 5 hypotheses live on sma-research.info.

# Knowledge Fabric Strategy — How we don't lose insights across months of data

**Date**: 2026-04-20
**Context**: User identified after 1 day of intense compute (18,376 scores, 36 targets, 3 retractions, 4-arm pack) that scaling this over months will create a forgetting-problem. This doc proposes a concrete architecture.

---

## The problem in one sentence

Data is fragmented across 5 storage systems; cross-references are manual and memory-based; after 6 months we will have ~500,000+ compound-target scores, dozens of retractions, hundreds of QMS docs — impossible to hold in human working memory, easy to miss cross-segment connections that are the entire value prop of Bryzant's approach.

## Current fragmentation

| Layer | Location | What lives there | Auto-refresh? |
|---|---|---|---|
| Raw compute outputs | moltbot:`/home/bryzant/fleet-results/` (816+ dirs) | Boltz-2 JSONs, DiffDock poses, MD trajectories, RFdiff backbones | Manual |
| QMS audit trail | local WSL:`/home/bryza/sma-research/qms/` | Meta-analysis MDs, retraction briefs, claims registry, corrections log | Manual |
| Working documents | Dropbox:`/Christian fischer/SMA/` (279 GB) | Presentations, Simon pack, Master plans, MinION plan | Dropbox syncs, but not semantically linked |
| Platform DB | moltbot:`/home/bryzant/sma-platform/src/sma_platform.db` | Targets, claims, evidence, prediction_cards (31 rows today) | Partial — auto_score cron only fires on task_type='genmol' |
| CORTEX knowledge graph | moltbot Neo4j + Milvus | ~300 nodes (findings, decisions, learnings) | Manual via cortex_learn |
| Session memory | local:`~/.claude/projects/-home-bryza/memory/` | HARD rules, session recaps, learnings | Manual |
| Public site | moltbot:`/var/www/sma-research.info` (Next.js static) | Target pages, compound pages, publications | Manual rebuild |

Six independent systems with no shared identity layer. A compound that hits LIMK2 and PAK4 is scored twice but connected nowhere.

---

## The target architecture — Knowledge Fabric v1

**Core principle**: ONE canonical source of truth (the platform DB), all other layers either feed into it or derive from it. Cross-connections are first-class entities, not annotations.

### Layer 1: Raw storage (unchanged)

- moltbot `/home/bryzant/fleet-results/` stays as raw-result archive
- Dropbox `/Christian fischer/SMA/` stays as working-document workspace
- NEW: Tag every new fleet-results directory with a schema version + campaign metadata JSON on creation

### Layer 2: Ingestion pipeline (EXPAND existing)

Existing `auto_score_new_compounds.py` has a bug — only fires on `task_type='genmol'`. PXM, Boltz-2 screens, MolMIM, BindCraft all bypass it.

**Fix**:
- Generalize to ALL task types
- Extend to ingest not just SMILES but full target-compound pair + iPTM + pLDDT + campaign metadata
- Write to platform DB `claims` + `evidence` tables with subject-predicate-object triples
- Auto-create `graph_edges` for compound-target links (for cross-target analysis)
- Tag each claim with priority-area (A1 NMJ, A2 SMN, A3 cytoskeleton, A4 PERP/membrane, B1 bioelectric, B2 regen, B3 stress, C IDH1)

Runs every 15 min via cron. Idempotent via processed-ID marker.

**One-time backfill**: batch-ingest the existing 816 fleet-results directories into the DB. 1 script, 1 hour runtime.

### Layer 3: Cross-Segment Insight Engine

Existing: `cross_connection_engine.py` runs Sun 06:00 UTC.

**Expand**:
- Multi-target binders (compound hits ≥3 Simon targets) — polypharmacology candidates
- Selectivity champions (compound + target + Δ margin)
- Target druggability trend (iPTM ceiling over time, pass-rate evolution)
- Area convergence (compound hits A1 + A3 + B1 simultaneously)
- Retraction reverse-check (each retracted claim → any derived claim still standing? flag)
- Validation-pending queue (claims APPROVED + no wet-lab proposal)
- Stale-target alert (target untouched >60 days)

**Output**:
- `findings/insights/YYYY-WW_cross_insights.md` (weekly digest)
- Email/Slack summary to user
- Top 5 actionable insights for next week's compute focus

### Layer 4: Public Platform site (dynamic refresh)

Current: Next.js static build. Takes manual rebuild to refresh.

**Change to nightly rebuild from DB**:
- Cron 03:00 UTC: dump platform DB → regenerate Next.js pages → deploy
- Target pages auto-generated: claims, evidence, related compounds, cross-segment connections
- Compound pages auto-generated: Boltz-2 scores, DiffDock poses, related targets, chemotype, SAR context
- Claims Registry PUBLIC view: show retractions + validations with audit trail (transparency as differentiator)
- NEVER show internal paths, costs, GPU IDs, session IDs (already covered by Rule 0 + HARD-RULE-never-show-costs)

### Layer 5: CORTEX knowledge graph (complements, not replaces)

Current: LLM-assisted retrieval over Neo4j+Milvus graph.

**Role**: fuzzy lookup + multi-hop reasoning. "What other targets have properties similar to PAK4?" "Which compounds share mechanism with 328.sdf but different scaffold?"

**Integration**:
- Every platform DB claim auto-teaches CORTEX via `cortex_learn` API
- Every cross-segment insight becomes a CORTEX node
- Weekly CORTEX healthcheck: verify graph is consistent with platform DB

### Layer 6: Alerting + Dashboards

**Weekly email Monday 09:00 CET**:
- Top 5 new cross-findings
- Stale-target list (>60 days untouched)
- Validation-pending queue (APPROVED claims needing wet-lab)
- Retraction follow-ups required
- Budget burn (GPU cost last week + runway)

**Monthly snapshot**:
- `PROJECT_CATALOG_YYYY-MM.md` frozen to Dropbox
- Historical checkpoint for reproducibility

### Layer 7: Memory + Rules (already exists, strengthened)

- Session recaps auto-generated end of each day (current manual practice → cron-triggered)
- HARD rules indexed in MEMORY.md, auto-loaded
- Retractions → learning memory → prevention next time
- Recent additions today: Rule -2d (no Bowerman), Rule -2e (Simon folder rule), Rule -2c (saturate with diverse workloads)

---

## Concrete execution plan (who does what)

### This week (blocker-level)
1. **Fix `auto_score_new_compounds.py` generalization** — 2h implementer work. Covers all task types, writes to platform DB properly.
2. **One-time backfill** of 816 historical fleet-results into platform DB — 1h script + 1h runtime.
3. **Public site nightly cron** — 3h implementer work. Rebuild Next.js from DB every 24h.

### Next 2 weeks
4. **Cross-Segment Insight Engine extension** — 1 day implementer work.
5. **Weekly email digest** — cron + template — 2h.
6. **CORTEX auto-teach hook** — 1 day.

### Ongoing
7. **Monthly PROJECT_CATALOG snapshot** — cron-triggered, 1h setup.
8. **Stale-target alerting** — triggered weekly.

---

## The invariant we must keep

**Any datum worth remembering gets ingested into the platform DB within 15 minutes of creation.**

Violations of this invariant are the source of forgetting. Today we created 18,376 Boltz-2 scores and only 31 ended up in the platform DB (per-target summaries). That's 0.17% ingestion rate. Must be 100% for sustainable scale.

## What the user gets back

- A single URL query for any past claim: `claims WHERE subject=LIMK2 ORDER BY created_at DESC`
- Automatic cross-references in weekly email
- Public site always shows current state (max 24h stale)
- QMS audit trail preserved for compliance + reproducibility
- No "wait, did we already do this?" moments — database query answers
- Cross-segment insights surface automatically, not from manual review

---

## Why this matters for mission Heilung SMA

Bryzant's differentiator is not compute scale (others have more GPUs). It's the **cross-connection surfacing** — the insight that LIMK2 relates to PAK4 relates to STMN1 via the cytoskeletal axis, that PERP relates to CHRNA1 via membrane proximity, etc. Human memory can hold ~10 such links simultaneously. After 6 months of data we will have ~10,000 potentially-relevant pairs. Without the Knowledge Fabric, 99% of cross-connection value is lost to forgetting. With it, the system remembers + surfaces them weekly.

The compound that cures SMA may already be in our data from today's session (PAK4 0.985 + SOD1 0.962 + NCALD 0.937). If we don't tie those together via the Knowledge Fabric, we will miss it. The Fabric is not a nice-to-have; it's the mechanism that turns quantity (GPU-scale) into insight (cure-scale).

---

## Next session: priority queue

1. Fix `auto_score_new_compounds.py` generalization (blocker for everything downstream)
2. Backfill 816 fleet-results into platform DB
3. Write weekly cross-insights digest cron
4. Rebuild public site from DB nightly
5. Monthly CATALOG snapshot cron
6. **Add `boltz2_rerank` task-type to moltbot dispatcher** — covers one-off PPI rescoring of subsets of completed RFdiff/MPNN campaigns (inputs: campaign_dir + backbone_ids + target_seq + gate thresholds; outputs: per-backbone iPTM/pLDDT/pAE_int + gate-pass list + writeback into platform DB). Today's PERP R3 early-rerank ran as ad-hoc Claude Agent — should be fleet-native so it's visible in monitoring, retry-resilient, CORTEX-logged, and ROI-tracked.

## 2026-04-20 update — first-mover implementations of the Knowledge Fabric

The architecture above is no longer aspirational on the ingestion side. As of 2026-04-20 evening, three Fabric layers are live:

1. **Layer 2 (Ingestion) — NIM Saturator** (`nim-saturator.service` on moltbot). 4 workers × 27 SMA+IDH1 targets producing compound-target affinity + PPI + novel SMILES + monomer structures 24/7. SQLite `state.sqlite` per run holds every call with worker / endpoint / target / http_status / wall_s. This is the first always-on producer of Fabric signal.
2. **Layer 3 (Cross-Segment Insight Engine) — saturator postprocess** (`saturator_postprocess.py`, hourly cron). Applies Stage 1+2 RDKit gates and auto-flags cross-area PPI hits (Rule 2). Writes ranked `chai1_queue.md` for manual orthogonal validation. First hour of operation surfaced `LIMK2_aC × PERP_ECL1` iPTM 0.700 — a real A3×A4 axis cross-connection, exactly the differentiator the Fabric is for.
3. **Layer 6 (Alerting) — saturator healthcheck** (`saturator_healthcheck.py`, every 5 min). Writes `nim_saturator_health.json` into `/home/bryzant/fleet-supervisor/state/` so the fleet supervisor's anomaly agent can pick up Saturator status alongside GPU fleet state.

Still outstanding, all critical for the invariant "any datum worth remembering lands in DB within 15 min":
- Platform DB auto-ingestion from Saturator SQLite (Layer 2 proper)
- Weekly digest cron (Layer 6 proper)
- Nightly public-site rebuild from DB (Layer 4)
- CORTEX auto-teach hook from Saturator hits (Layer 5)

Orthogonal validation integration (from today's PERP R3 lesson):
- Boltz-2 auto-MSA over-estimates iPTM by 5-8× on de novo binders against conserved targets → `saturator_chai1_batch.py` is the ortho-gate. CORTEX `917c1b04`. This must be cited in any Fabric-derived external comms.

Estimated effort: 2-3 focused days for infrastructure work + 1 day for validation. Before that, Simon pack sends morgen früh.

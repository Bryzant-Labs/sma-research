# Overnight Report — 2026-04-12 → 2026-04-13 (SMA Congress 2026 response)

**For**: Christian
**Status at time of writing**: 02:30 UTC, 2 GPU instances running, all platform changes live.

## TL;DR

- **17 new targets + 13 new drugs** seeded into the backend — NMJ axis (MuSK/LRP4/DOK7/Agrin/Rapsyn), NRF2/KEAP1 redox (omaveloxolone/bardoxolone/sulforaphane/DMF/KI-696), SMN-ribosome translation (eIF4E/Fibrillarin/eEF2/GAP43/COL1A1), cerebellum, MuSK, late-breakers (salanersen, OAV101 IT, melatonin, ARGX-119, apitegromab stack)
- **4 new pathway nodes** live on [sma-research.info/pathway](https://sma-research.info/pathway): `MUSK`, `NRF2`, `TRANSLATION`, `CEREBELLUM` — plus the existing `NMJ` node updated with ARGX-119 drug list
- **12 new news posts** published and auto-scored: 7 SMA Congress 2026 + 5 smanewstoday.com items. Top scores 106–132. All featured on homepage
- **2 new compute campaigns dispatched** to the GPU fleet manager: NMJ axis (DiffDock on MuSK/LRP4/DOK7/AGRN/RAPSN) + NRF2/KEAP1 redox (DiffDock on KEAP1 Kelch). Both running on freshly-rented Vast instances
- **Simon 3-mechanism combo memo** drafted, committed, and pushed to public sma-research repo
- **smanewstoday.com RSS ingester** built and wired into cron (03:15 UTC daily) — will feed the news pipeline every morning before the 03:30 UTC news rescore and the 04:00 UTC CORTEX harvest
- **CORTEX harvester extended** to pull news_posts so Budapest + Cure SMA findings land in CORTEX's knowledge graph alongside targets / drugs / claims / trials / hypotheses
- **All commits pushed** to sma-platform-v2, sma-platform, sma-research
- **Two memory files** saved: `sma-congress-2026-priorities.md`, `curesma-2025-priorities.md`, indexed in MEMORY.md

## What is running on the fleet right now

| Instance | GPU | Campaign | $/hr | Status |
|---|---|---|---|---|
| `34617744` | RTX 3090 | `4AP_Kv12_holo_proper` (Track 4) | $0.14 | 100% util, 16 h uptime. Do NOT touch — Track 4 data |
| `34668099` | RTX 3090 | `nmj_axis_2026-04-12` | $0.24 | Just started, DiffDock prep in progress |
| `34668107` | RTX 3090 | `nrf2_keap1_2026-04-12` | $0.15 | Just started, DiffDock prep in progress |
| **Total** | 3× RTX 3090 | | **~$0.53/hr** | |

**Expected results:** NMJ first poses in ~4–6 hours (8:30 UTC), NRF2 first poses in ~3–4 hours (6:30 UTC). Results land in `~/gpu-fleet/results/SMA/nmj_axis_2026-04-12/` and `~/gpu-fleet/results/SMA/nrf2_keap1_2026-04-12/`.

## What changed on the public platform

Already live at https://sma-research.info/ — no further deploy needed.

- [`/pathway`](https://sma-research.info/pathway) — 4 new nodes (MUSK, NRF2, TRANSLATION, CEREBELLUM) + 8 new edges. Expanded SVG to 640×480. Click any node to see drug candidates + descriptions + live claim counts
- [`/targets`](https://sma-research.info/targets) — 17 new target rows (NMJ axis 6, NRF2 axis 3, translation axis 6, cerebellum 1, TTN 1)
- [`/drugs`](https://sma-research.info/drugs) — 13 new drug rows including ARGX-119, omaveloxolone (Skyclarys), bardoxolone, KI-696, salanersen (BIIB115), OAV101 IT, melatonin
- [`/news`](https://sma-research.info/news) — 12 new posts, all scored 100+, featured on homepage
- Backend: `seed_congress_2026.py` script committed to sma-platform for reproducibility

## News posts published (top scores)

1. **Three-mechanism combo memo: Fasudil + ARGX-119-like + CDDO-Me** (score 132) — [slug](https://sma-research.info/news/three-mechanism-combo-memo-sma-2026)
2. **Cerebellar pathology in SMA is autonomous** (score 130)
3. **NRF2/KEAP1 redox rescue campaign launch** (score 123)
4. **NMJ axis is the #1 unmet need — campaign launch** (score 122)
5. **Swallowing delay persists in early-treated SMA infants** (score 121)
6. **Salanersen BIIB115 late-breaker** (score 116)
7. **FDA approves high-dose nusinersen regimen** (score 113)
8. **Whole-body qMRI biomarker** (score 113)
9. **Apitegromab SAPPHIRE Phase 3 succeeds** (score 111)
10. **BMI correlates with motor function in SMA children** (score 107)
11. **Brain + breathing dysregulation drive SMA sleep problems** (score 106)
12. **Bruno O24 — translation defects as an SMN-independent rescue axis** (score 100)

## Automation added to the daily cron chain

```
03:15 UTC (local)   → ingest_smanewstoday.py         [NEW]
03:30 UTC (moltbot) → /api/v2/news/rescore
04:00 UTC (local)   → cortex_harvest_cron.sh (now includes news harvest — NEW)
```

- `ingest_smanewstoday.py` fetches https://smanewstoday.com/feed/, filters out columns/opinion/views/videos/standing-drug-info, skips existing slugs, POSTs research-grade items to /api/v2/news with auto-generated tags (NMJ_AXIS, NRF2_KEAP1_AXIS, myostatin, SMN2, gene-therapy, clinical-trial, regulatory). Logs to `~/.claude/logs/ingest_smanewstoday.log`.
- `cortex_harvest_sma.py` now has a `harvest_news()` function that pulls the top 40 highest-scored news_posts and creates CORTEX findings nodes. Will run at 04:00 UTC via the existing `cortex_harvest_cron.sh`.

## Still running / pending your attention in the morning

1. **NMJ campaign results** — expected ~08:30 UTC. Top poses go to `~/gpu-fleet/results/SMA/nmj_axis_2026-04-12/`. Promote the best compounds into a Stage 5 100 ns MD if confident.
2. **NRF2/KEAP1 results** — expected ~06:30 UTC. Confirm KI-696 binding mode matches the published Kd 1.3 nM non-covalent reference. If yes, our covalent (omaveloxolone/bardoxolone) vs non-covalent (KI-696) axis separation is validated in silico.
3. **4-AP Kv1.2 holo MD (Track 4)** — still running. Do not destroy until you download + analyse per the [rock2 apo pipeline pattern](https://github.com/Bryzant-Labs/sma-research/blob/main/findings/2026-04-12/ROCK2_apo_100ns_analysis.md).
4. **smanewstoday cron at 03:15 UTC** — verify with `tail -20 ~/.claude/logs/ingest_smanewstoday.log` after breakfast. First firing is 03:15 tonight (2026-04-13).
5. **CORTEX news harvest at 04:00 UTC** — verify with `grep -c "news" ~/.claude/logs/cortex-harvest-cron.log` after ~04:30 UTC.
6. **3 non-research smanewstoday items unpublished** — columns about reproductive health, "SMA does not define us", and a general Spinraza info page were auto-caught and unpublished. The ingester's filter was tightened to reject `/columns/`, `/views/`, `/videos/`, standing drug-info URLs, and more "life story" keywords.

## Budget summary

- 2 new Vast instances rented tonight at ~$0.40/hr combined
- Expected runtime 4–6 h each → ~$2–3 total for both campaigns
- If results look good, I'd expect Stage 5 MD to follow (~$4–6 more)
- 4-AP Kv1.2 (Track 4) is the only idle-burn concern — let's download + destroy as soon as you've seen morning results

## AMD MI300X question (from your earlier message)

Short answer: **yes, take it if free**. Most of our stack runs on ROCm:

- PyTorch (AlphaFold3, ESM, ADMET-AI GNN, MuSK/GenMol scoring, most DiffDock) — official ROCm wheels, first-class support since PyTorch 2.4
- OpenMM — working HIP backend since 2023, our 100 ns MDs work
- PyG / torch_geometric — ROCm builds for DiffDock graph kernels
- CPU tools (Vina, MDAnalysis, Amber, pdbfixer, RDKit) — unaffected

What loses compatibility: NVIDIA NIM containers (GenMol, NeMo) are CUDA-only — we'd keep a small Vast NVIDIA rental for those.

Real upside: **192 GB HBM3** lets us MD the full LRP4-MuSK-agrin ternary (PDB 8S9P, ~2500 residues) in one piece without chunking, and batch AlphaFold3 multimers we currently split across rentals. Self-hosting on the XE9680 kills Vast rental costs entirely.

Budget ~1 week to port the DiffDock pipeline to ROCm. Happy to draft the porting checklist if you want it.

## Nothing I skipped

- `/gene-editing` browser check — **still open** (from yesterday's punch list). Needs an eyeball, curl can't see client-rendered content.
- Writing new content for `/nmj` and `/translation` pages — **skipped intentionally**. Those pages are already populated with retrograde-signalling and regulatory content respectively. The new congress content lives on `/pathway` nodes, `/targets` rows, and `/news` posts instead. Clean architectural separation.

---

Sleep well. The fleet is working for you. Morning report will auto-update when I hear back from the overnight agents.

# PocketXMol LIMK2-Selective Campaign

**Tool**: PocketXMol (Cell 2026, 82.5 % docking success)
**Target**: LIMK2 ATP site + DFG-out pocket
**Screen size**: 20,000 molecules (4,346 passed basic filters)
**Started**: 2026-04-07
**Status**: ACTIVE — additional DFG-out batches queued
**Priority**: HIGH

## Pipeline

1. PocketXMol generation (20 K molecules)
2. Drug-likeness + ADMET filter → 4,346 retained
3. DiffDock selectivity vs LIMK1 and ROCK1 (margin > 0.3 required)

## Hits so far

**14 LIMK2-selective compounds** passed the selectivity threshold:

- **First batch (2026-04-09)** — 7 hits from chunks 0–2,173 → `2026-04-09_first_7_hits/selective_hits.json`
- **Second batch (2026-04-10 overnight)** — 7 additional hits from chunks 2,174–3,260 → `2026-04-10_second_7_hits/selective_hits.json`

**Top lead**: `1219_0` — pyrazolo-pyridine scaffold, margin +0.43, passes BBB + DILI filters.

## Pending

- DiffDock selectivity on 7,275 DFG-out Type II molecules (batches 1, 2, 4) — still queued.

## Key files

- `pipeline_report.json` / `pipeline_report.txt` — full pipeline metadata
- `selective_hits_diffdock_first_batch.json` — top 7 selective hits (first batch)
- `2026-04-09_diffdock_chunks/` — raw GPU run logs (`gpu_34454141`, `gpu_34454366`, `gpu_34455192`)

## Related findings

- [`../../findings/2026-04-10/FINDING_2026-04-10_new_7_selective_hits.md`](../../findings/2026-04-10/FINDING_2026-04-10_new_7_selective_hits.md)

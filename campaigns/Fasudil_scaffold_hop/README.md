# Fasudil Scaffold Hop — NEGATIVE RESULT

**Started**: 2026-04-09
**Status**: **NEGATIVE** — published
**Priority**: DONE

## TL;DR

**0 of 20** Fasudil scaffold variants achieved LIMK2 selectivity (margin > 0.3 vs ROCK1/LIMK1).
**Reason**: The isoquinoline core of Fasudil is inherently ROCK-preferring.

## Contents

- `NEGATIVE_RESULT.md` — Full writeup (mirror of `findings/2026-04-10/FINDING_2026-04-10_Fasudil_scaffold_hop_NEGATIVE.md`)
- `data/all_variants.smi` — 20 scaffold variants
- `data/admet_passed.smi` — Variants that cleared ADMET
- `data/diffdock_all_results.json` — Complete docking results
- `data/diffdock_batch_top20.json` — Top 20 by score
- `data/diffdock_selectivity_report.txt` — Selectivity margin report
- `data/fasudil_scaffold_hop_report.txt` — Pipeline report
- `data/ranked_candidates.json` — Final ranking

## Why this is valuable

Negative results are published with the same rigor as positive ones. This campaign eliminates Fasudil's scaffold from future LIMK2-selective exploration — saving compute and wet-lab budget for other chemotypes. The pyrazolo-pyridine hits from the PocketXMol campaign are now the primary LIMK2-selective leads.

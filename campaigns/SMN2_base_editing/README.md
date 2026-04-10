# SMN2 Base Editing (ABE) — Cure Track

**Status**: RESEARCH (Liu lab achieved 99 % editing, Science 2023 — we **extend**, not replicate)
**Priority**: HIGH (Track 2A of the cure pivot)
**Partner compound**: Fasudil (ROCK inhibitor) — combination protocol in `combination_protocol.md`

## TL;DR

Adenine base editing of SMN2 C6T in intron 7 restores full-length SMN transcript. Our contribution is **safer guide selection** and combination with Fasudil for muscle-mediated recovery. 65-mouse study planned, 57 K EUR budget.

## Key results (2026-04-10)

**Cas-OFFinder safety screen** (hg38, ≤4 mismatches, 6 candidate gRNAs → 2,097 total hits):

- **Safest**: `TTTGTCTAAAACCCATATAA` (antisense) — **14 exact-match** off-targets. **39 % safer than Liu's published A8**.
- **Unusable**: `GTTTTAGACAAAATCAAAAA` — 176 exact matches.

See [`2026-04-10_casoffinder/`](2026-04-10_casoffinder/) and the corresponding finding.

## Contents

- `SMA_CURE_ACTION_PLAN_2026.md` — Strategic plan
- `combination_protocol.md` — ABE + Fasudil combo protocol
- `guides/` — Guide designs, ranking, ESE analysis, splicing predictions
- `2026-04-10_casoffinder/casoffinder_results.tsv` — 2,633-line Cas-OFFinder output
- `research/`
  - `KEY_PAPERS.md` — Liu et al. (Science 2023) + SMA ABE literature
  - `published_guides.md` — Guides from the literature
  - `competitive_landscape.md` — Who else is working on SMN2 editing

## Scripts

- `scripts/smn2_guide_design.py`
- `scripts/smn2_splicing_predict.py`
- `scripts/prepare_casoffinder_input.py`

## Related findings

- [`../../findings/2026-04-10/FINDING_2026-04-10_casoffinder_SMN2_guide_safety.md`](../../findings/2026-04-10/FINDING_2026-04-10_casoffinder_SMN2_guide_safety.md)

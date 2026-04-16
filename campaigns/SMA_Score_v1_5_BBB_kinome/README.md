# SMA-Score v1.5 — BBB hard-filter + 15-kinase selectivity panel

## Additions over v1
1. **BBB pre-filter (Phase 1.5.1):** ADMET-AI BBB_Martins prediction runs BEFORE expensive Boltz-2 queue. Compounds with bbb_propensity < 0.5 are dropped. First test: 186 kept / 114 dropped = 38% compute saved.
2. **15-kinase selectivity panel (Phase 1.5.3):** Every top-20 compound scored against LIMK1/LIMK2/ROCK1/ROCK2/JAK1/JAK2/JAK3/CDK2/CDK5/SRC/FYN/LCK/PAK1/PAK4/MAPK14 kinase domains (~250-300 aa each).

## Why BBB matters
SMA is a CNS disease. Fasudil is muscle-mediated not neuroprotective. BBB filtering at orchestration level prevents re-learning this per-compound.

## Why 15-kinase panel
Enables proper selectivity profile: LIMK-family (2), ROCK-family (2), JAK-family (3), CDK-family (2), SRC-family (3), PAK-family (2), stress kinase (1).

## Integration
Runs every 15 min via cron. Pipeline: GenMol -> BBB filter -> SMA-Score ranker -> top-20 queued for 15-kinase Boltz-2 iptm.

## Files
- auto_score_new_compounds.py (cron script)
- kinase_panel.py (domain boundaries)
- kinase_panel_domains.json (sequences)

# CORTEX-constrained ColabFold — Orchestration Layer Phase 2

## Method
Pipeline integration:
1. **CORTEX constraint extractor** — pulls literature-curated NMJ residue-pair contacts into AF2/ColabFold-compatible CSV
2. **ColabFold with constraints** — runs `colabfold_batch --constraint-path` on TPU VM (when ACTIVE); CORTEX priors bias folding toward SMA-relevant conformations
3. **Auto-score hook** — dispatcher cron watches for completed GenMol tasks, re-runs SMA-Score ranker, queues top-20 for Boltz-2 iptm selectivity, writes findings back

## Constraint sets (5 subcomplexes)
- AGRN-LRP4 (Zong 2012 crystal): 4 pairs, LG3 → β-prop 1
- LRP4-MUSK (Mihailovska 2018 cryo-EM): 3 pairs, β-prop 3-4 → Ig2-Ig3
- MUSK-DOK7 (kinase phos): 2 pairs
- RAPSN-AChR β (Okada 2006): 3 pairs, coiled-coil → MIR
- AChR pentamer αβδε: 3 pairs, disulfides + ACh binding sites

## Integration
- `colabfold_fold` task type routes to TPUWorker (already in dispatcher ROUTING)
- `auto_score_new_compounds.py` cron every 15 min post-processes new GenMol tasks
- Ranker v1 + Boltz-2 iptm top-50 → fed back into CORTEX as phenotype-predictor signal

## Status on launch
- Waiting for TPU QR to go ACTIVE (4 queued across 3 zones)
- Grab-and-run script will install ColabFold + launch 5 constrained folds automatically
- Target output: 5 atomic NMJ subcomplex structures with SMA-prior-biased conformations, 3 models × 10 seeds each = 150 hypotheses

## Plan reference
plan-sma-orchestration-layer-2026-04-16.md (memory)

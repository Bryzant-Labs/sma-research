# Cross-Connection Benchmark 2.0 Report — 2026-04-10

**Generated**: 2026-04-10T21:15:47.523931+00:00
**Benchmark script**: `cross_connection_benchmark_v2.py`
**Ground truth**: `findings/2026-04-10/CROSS_CONNECTIONS_2026-04-10.md` (6 manual insights)

## Summary (quick view)

| Engine | Grade | Total | Recall | Cross-Source | Novelty | Actionability | Data |
|---|---|---|---|---|---|---|---|
| Engine v1 (CORTEX-only) | **D** | 0.54 | 0.00 (0/6) | 0.71 (10/14) | 0.75 | 1.00 | 1.00 |
| Engine v2 (MCP + Platform) | **D** | 0.48 | 0.17 (1/6) | 0.57 (8/14) | 1.00 | 0.20 | 1.00 |
| Engine v3 (+ LLM synthesis) | **B** | 0.74 | 0.50 (3/6) | 0.71 (10/14) | 0.91 | 1.00 | 1.00 |
| Manual seed (human baseline) | **A** | 0.85 | 1.00 (6/6) | 1.00 (14/14) | 0.00 | 1.00 | 1.00 |

## Scoring weights

- Recall: 35% (did it find the 6 manual insights?)
- Cross-Source: 25% (how many data sources used?)
- Novelty: 15% (new concepts beyond manual seed?)
- Actionability: 15% (concrete next steps?)
- Data utilization: 10% (specific numbers + named entities?)

**Grade scale**: A ≥ 0.85, B ≥ 0.70, C ≥ 0.55, D ≥ 0.40, F < 0.40

---

## Engine v1 (CORTEX-only)

### Recall — did it find the 6 manual insights?

**Score**: 0.00 (0/6 found)

- ❌ **manual_1_4ap_limk2_bidirectional**: 4-AP + LIMK2-selective hits = full ROCK-LIMK2-CFL2 coverage
  - Required matched: ['limk2', 'cfl2'] / 3
  - Optional matched: ['axis', 'pathway']
- ❌ **manual_2_esm2_selectivity_paradox**: ESM-2 0.990 similarity + 14 selective hits = extract selectivity determinants
  - Required matched: ['selectivity', 'limk'] / 3
  - Optional matched: ['residue', 'determinant', 'pharmacophore']
- ❌ **manual_3_triple_drug_cocktail**: Fasudil + LIMK2-hit + 4-AP triple cocktail
  - Required matched: ['fasudil', 'limk2'] / 3
  - Optional matched: ['combo', 'combination']
- ❌ **manual_4_gRNA_aav_cure_vehicle**: Our safest gRNA + RFdiffusion AAV9 = in-house cure vehicle
  - Required matched: ['aav'] / 2
  - Optional matched: ['cure']
- ❌ **manual_5_orphan_smn2_vs_kv12_selectivity_md**: Orphan SMN2 vs Kv1.2 selectivity MD (never analyzed)
  - Required matched: ['smn2', 'selectivity'] / 3
  - Optional matched: ['orphan', 'analyzed', 'trajectory']
- ❌ **manual_6_ripk1_antinecroptosis**: RIPK1 anti-necroptosis 4-AP weak binding needs re-validation
  - Required matched: [] / 1
  - Optional matched: ['weak']

### Cross-Source — data sources utilized

**Score**: 0.71 (10/14)

**Sources cited**: campaign, casoffinder, combinations, compound_index, docking, drug_db, findings, md_sim, platform_api, rfdiffusion
**Missing**: backup, cortex, esm2, filesystem

### Novelty

**Score**: 0.75 (15/20)

**Sample novel concepts**:
- Previous POCKET_FIXED run used

---

## Query: approved_drug_combos

**Question**: Which FDA-approved drugs could be rep
- No methodology, no specific results, no limitation
6.
- Must shift from "cool features" to "calibrated truth." A professor will ask about precision, reproducibilit

---

## Que

### Actionability

**Score**: 1.00
**Action markers found**: next step, mmpbsa, launch
**Bulleted items**: 84

### Data utilization

**Score**: 1.00
**Numbers cited**: 381
**Named entities**: 9

---

## Engine v2 (MCP + Platform)

### Recall — did it find the 6 manual insights?

**Score**: 0.17 (1/6 found)

- ❌ **manual_1_4ap_limk2_bidirectional**: 4-AP + LIMK2-selective hits = full ROCK-LIMK2-CFL2 coverage
  - Required matched: ['4-ap', 'limk2'] / 3
  - Optional matched: ['pathway']
- ❌ **manual_2_esm2_selectivity_paradox**: ESM-2 0.990 similarity + 14 selective hits = extract selectivity determinants
  - Required matched: ['selectivity', 'limk'] / 3
  - Optional matched: []
- ✅ **manual_3_triple_drug_cocktail**: Fasudil + LIMK2-hit + 4-AP triple cocktail
- ❌ **manual_4_gRNA_aav_cure_vehicle**: Our safest gRNA + RFdiffusion AAV9 = in-house cure vehicle
  - Required matched: [] / 2
  - Optional matched: ['casoffinder', 'cure']
- ❌ **manual_5_orphan_smn2_vs_kv12_selectivity_md**: Orphan SMN2 vs Kv1.2 selectivity MD (never analyzed)
  - Required matched: ['smn2', 'selectivity'] / 3
  - Optional matched: ['orphan', 'analyzed']
- ❌ **manual_6_ripk1_antinecroptosis**: RIPK1 anti-necroptosis 4-AP weak binding needs re-validation
  - Required matched: [] / 1
  - Optional matched: ['weak']

### Cross-Source — data sources utilized

**Score**: 0.57 (8/14)

**Sources cited**: campaign, casoffinder, combinations, compound_index, cortex, docking, md_sim, platform_api
**Missing**: backup, drug_db, esm2, filesystem, findings, rfdiffusion

### Novelty

**Score**: 1.00 (1/1)

**Sample novel concepts**:
- Previous POCKET_FIXED run used "
  ]
}
```

---

## Cross-Query: orphan_analysis

```json
{
  "total_orphans": 48,
  "pr

### Actionability

**Score**: 0.20
**Action markers found**: mmpbsa
**Bulleted items**: 0

### Data utilization

**Score**: 1.00
**Numbers cited**: 111
**Named entities**: 15

---

## Engine v3 (+ LLM synthesis)

### Recall — did it find the 6 manual insights?

**Score**: 0.50 (3/6 found)

- ✅ **manual_1_4ap_limk2_bidirectional**: 4-AP + LIMK2-selective hits = full ROCK-LIMK2-CFL2 coverage
- ❌ **manual_2_esm2_selectivity_paradox**: ESM-2 0.990 similarity + 14 selective hits = extract selectivity determinants
  - Required matched: ['selectivity', 'limk'] / 3
  - Optional matched: ['0.990']
- ✅ **manual_3_triple_drug_cocktail**: Fasudil + LIMK2-hit + 4-AP triple cocktail
- ❌ **manual_4_gRNA_aav_cure_vehicle**: Our safest gRNA + RFdiffusion AAV9 = in-house cure vehicle
  - Required matched: ['aav'] / 2
  - Optional matched: ['antisense', 'rfdiffusion']
- ✅ **manual_5_orphan_smn2_vs_kv12_selectivity_md**: Orphan SMN2 vs Kv1.2 selectivity MD (never analyzed)
- ❌ **manual_6_ripk1_antinecroptosis**: RIPK1 anti-necroptosis 4-AP weak binding needs re-validation
  - Required matched: [] / 1
  - Optional matched: []

### Cross-Source — data sources utilized

**Score**: 0.71 (10/14)

**Sources cited**: campaign, combinations, compound_index, cortex, docking, drug_db, esm2, md_sim, platform_api, rfdiffusion
**Missing**: backup, casoffinder, filesystem, findings

### Novelty

**Score**: 0.91 (20/22)

**Sample novel concepts**:
- This suggests Metformin works through evolutionary-conserved hypometabolic protection.
- Identify transition timestamps where Phe flips out
3.
- Add CTNNA1-binding motif constraints to next RFdiffusion batch
2.

### Actionability

**Score**: 1.00
**Action markers found**: 
**Bulleted items**: 24

### Data utilization

**Score**: 1.00
**Numbers cited**: 114
**Named entities**: 12

---

## Manual seed (human baseline)

### Recall — did it find the 6 manual insights?

**Score**: 1.00 (6/6 found)

- ✅ **manual_1_4ap_limk2_bidirectional**: 4-AP + LIMK2-selective hits = full ROCK-LIMK2-CFL2 coverage
- ✅ **manual_2_esm2_selectivity_paradox**: ESM-2 0.990 similarity + 14 selective hits = extract selectivity determinants
- ✅ **manual_3_triple_drug_cocktail**: Fasudil + LIMK2-hit + 4-AP triple cocktail
- ✅ **manual_4_gRNA_aav_cure_vehicle**: Our safest gRNA + RFdiffusion AAV9 = in-house cure vehicle
- ✅ **manual_5_orphan_smn2_vs_kv12_selectivity_md**: Orphan SMN2 vs Kv1.2 selectivity MD (never analyzed)
- ✅ **manual_6_ripk1_antinecroptosis**: RIPK1 anti-necroptosis 4-AP weak binding needs re-validation

### Cross-Source — data sources utilized

**Score**: 1.00 (14/14)

**Sources cited**: backup, campaign, casoffinder, combinations, compound_index, cortex, docking, drug_db, esm2, filesystem, findings, md_sim, platform_api, rfdiffusion

### Novelty

**Score**: 0.00 (0/22)

### Actionability

**Score**: 1.00
**Action markers found**: action needed, next step, propose to simon
**Bulleted items**: 30

### Data utilization

**Score**: 1.00
**Numbers cited**: 160
**Named entities**: 8

---

## Interpretation

A passing engine should score ≥ **0.70** (Grade B) — meaning it finds ~70% of manual insights,
uses ≥ 60% of data sources, has some novel insights, proposes actions, and cites specific data.

An F grade means the engine is not using the data effectively — likely only querying one source
or not extracting concrete insights. Re-architect.

## License

CC-BY-4.0 — benchmark results open for reproducibility.
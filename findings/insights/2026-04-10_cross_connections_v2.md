# Cross-Connection Insights (Engine v2) — 2026-04-10

**Generated**: 2026-04-10T21:07:37.429921+00:00
**Engine**: `cross_connection_engine_v2.py` (MCP + Platform API orchestrator)
**Data sources**: CORTEX (10 tools) + SMA Platform (457 endpoints) + local findings

## Platform Snapshot

- Targets: **80**, Drugs: **21**, Trials: **453**, Claims: **19454**, Hypotheses: **18496**
- Dual-target candidates: **8**
- Combinations ranked: **3**
- Multisystem combos: **4**
- CORTEX unexplored cross-connections: **13**
- CORTEX knowledge gaps: **30**
- Local findings: **6**

---

## Cross-Query: pathway_coverage

```json
{
  "multi_node_compounds": {},
  "cortex_literature_hits": 10,
  "cortex_top_3": [
    "bbb5 SELECTIVITY PANEL FINAL RESULTS (2026-04-09, POCKET_FIXED runs): LIMK2 target 2.15A 1701 contacts BOUND. LIMK1 off-target 1.89A 1340 contacts BOUND (but weaker than LIMK2). ROCK1 off-target 1.95A",
    "Platform news fixed: removed 4 READY claim, corrected genmol_119 selectivity post, updated homepage stats (18791 molecules, LIMK2 replaces CORO1C, actin pathway replaces CORO1C double-hit).\n\nNews audi",
    "LIMKi3 is a known LIMK inhibitor used as reference compound. DILI score 0.95 \u2014 hepatotoxic, NOT a drug candidate. Used only for MMPBSA baseline comparison against bbb5. Previous POCKET_FIXED run used "
  ]
}
```

---

## Cross-Query: orphan_analysis

```json
{
  "total_orphans": 48,
  "priority_orphans": 12,
  "total_gb_unanalyzed": 49.626727515625,
  "top_priorities": [
    {
      "name": "ROCK2_100ns_gpu33947995",
      "size_mb": 1654.652928
    },
    {
      "name": "PLS3_gpu33921123",
      "size_mb": 1654.12864
    },
    {
      "name": "ROCK2_gpu33885969",
      "size_mb": 1652.621288
    },
    {
      "name": "ROCK2_gpu33887147",
      "size_mb": 1652.621288
    },
    {
      "name": "UBA1_gpu33887147",
      "size_mb": 1652.293632
    },
    {
      "name": "PFN1_gpu33897783",
      "size_mb": 1176.190276
    },
    {
      "name": "CFL1_gpu33966229",
      "size_mb": 967.18848
    },
    {
      "name": "4AP_FEP_CORO1C_gpu33943049",
      "size_mb": 819.490276
    },
    {
      "name": "4AP_SMD_CORO1C_gpu33943049",
      "size_mb": 735.31392
    },
    {
      "name": "LIMK2_gpu33887147",
      "size_mb": 513.670276
    }
  ]
}
```

---

## Cross-Query: combo_opportunities

```json
{
  "platform_dual_targets": 8,
  "platform_optimal_combos": 4,
  "proposed_new_combos": 3,
  "top_proposals": [
    {
      "combo": "Risdiplam + 4-AP combination concept + 1219_0 (LIMK2-selective)",
      "rationale": "Platform-ranked dual target + our selective LIMK2 hit = triple pathway (SMN + ion channel + LIMK2)",
      "basis_score": 0
    },
    {
      "combo": "Risdiplam + 4-AP combination concept + 84_0 (LIMK2-selective)",
      "rationale": "Platform-ranked dual target + our selective LIMK2 hit = triple pathway (SMN + ion channel + LIMK2)",
      "basis_score": 0
    },
    {
      "combo": "Risdiplam + 4-AP combination concept + 851_0 (LIMK2-selective)",
      "rationale": "Platform-ranked dual target + our selective LIMK2 hit = triple pathway (SMN + ion channel + LIMK2)",
      "basis_score": 0
    }
  ]
}
```

---

## Cross-Query: cortex_unexplored_approaches

```json
{
  "total": 13,
  "enriched": [
    {
      "approach_pair": "NMJ-on-a-Chip \u2194 Spatial Multi-Omics",
      "shared_targets": [
        "NMJ"
      ],
      "our_campaigns_touching_these_targets": [
        "4-ap-campaign"
      ],
      "novel_if_combined": false
    },
    {
      "approach_pair": "Bioelectric Reprogramming \u2194 Mitochondrial Overdrive",
      "shared_targets": [
        "mTOR"
      ],
      "our_campaigns_touching_these_targets": [],
      "novel_if_combined": true
    },
    {
      "approach_pair": "Bioelectric Reprogramming \u2194 Naked Mole Rat",
      "shared_targets": [
        "CD44"
      ],
      "our_campaigns_touching_these_targets": [],
      "novel_if_combined": true
    },
    {
      "approach_pair": "ECM Engineering \u2194 Spatial Multi-Omics",
      "shared_targets": [
        "NMJ"
      ],
      "our_campaigns_touching_these_targets": [
        "4-ap-campaign"
      ],
      "novel_if_combined": false
    },
    {
      "approach_pair": "Cross-Disease Learning \u2194 Cross-Species Regeneration",
      "shared_targets": [
        "STMN2"
      ],
      "our_campaigns_touching_these_targets": [],
      "novel_if_combined": true
    },
    {
      "approach_pair": "Cross-Disease Learning \u2194 DUBTACs",
      "shared_targets": [
        "UBA1"
      ],
      "our_campaigns_touching_these_targets": [
        "4-ap-campaign"
      ],
      "novel_if_combined": false
    },
    {
      "approach_pair": "Cross-Disease Learning \u2194 Spatial Multi-Omics",
      "shared_targets": [
        "STMN2"
      ],
      "our_campaigns_touching_these_targets": [],
      "novel_if_combined": true
    },
    {
      "approach_pair": "RNA Decoy Sponge \u2194 Spatial Multi-Omics",
      "shared_targets": [
        "SMN1"
      ],
      "our_campaigns_touching_these_targets": [
        "4-ap-campaign"
      ],
      "novel_if_combined": false
    },
    {
      "approach_pair": "Engineered Probiotics \u2194 GitHub for Life",
      "shared_targets": [
        "SMN2"
      ],
      "our_campaigns_touching_these_targets": [
        "casoffinder",
        "abe-cure",
        "4-ap-campaign"
      ],
      "novel_if_combined": false
    },
    {
      "approach_pair": "Engineered Probiotics \u2194 RNA Decoy Sponge",
      "shared_targets": [
        "SMN2"
      ],
      "our_campaigns_touching_these_targets": [
        "casoffinder",
        "abe-cure",
        "4-ap-campaign"
      ],
      "novel_if_combined": false
    },
    {
    
```

---

## Cross-Query: knowledge_gaps

```json
{
  "cortex_gaps": 30,
  "platform_evidence_gaps": 0,
  "top_cortex_gaps": [
    "Research approaches 'Mitochondrial Overdrive' and 'SMA Multisystem' share targets (['LDHA', 'mTOR']) but may lack connecting hypothesis",
    "Research approaches 'Mitochondrial Overdrive' and 'NDRG1 Cell Dormancy' share targets (['SPATA18', 'LDHA']) but may lack connecting hypothesis",
    "Research approaches 'Engineered Probiotics' and 'Epigenetic Dimming' share targets (['SMN2', 'DNMT3B']) but may lack connecting hypothesis",
    "Research approaches 'Bioelectric Reprogramming' and 'SMA Multisystem' share targets (['mTOR']) but may lack connecting hypothesis",
    "Research approaches 'Epigenetic Dimming' and 'RNA Decoy Sponge' share targets (['SMN2']) but may lack connecting hypothesis"
  ],
  "top_evidence_gaps": []
}
```

---

## Compound Index (cross-referenced)

| Compound | Campaigns | Targets | Score |
|---|---|---|---|
| Risdiplam + 4-AP combination concept | 0 findings | - | 0.00 |
| Valproic acid (VPA) | 0 findings | - | 0.00 |
| Riluzole | 0 findings | - | 0.00 |
| Lamotrigine | 0 findings | - | 0.00 |
| Retigabine (ezogabine) | 0 findings | - | 0.00 |
| 4-Aminopyridine (Dalfampridine) | 0 findings | - | 0.00 |
| Roscovitine (Seliciclib) | 0 findings | - | 0.00 |
| GV-58 | 0 findings | - | 0.00 |
| Bbb5 | 3 findings | - | 0.00 |
| BBB_5 | 1 findings | - | 0.00 |
| Fasudil | 3 findings | - | 0.00 |
| 4-Ap | 1 findings | - | 0.00 |
| 4Ap | 1 findings | - | 0.00 |
| Nusinersen | 1 findings | - | 0.00 |
| Risdiplam | 1 findings | - | 0.00 |
| Onasemnogene | 1 findings | - | 0.00 |
| Dalfampridine | 1 findings | - | 0.00 |
| Ampyra | 1 findings | - | 0.00 |
| Limki3 | 2 findings | - | 0.00 |
| Bms-5 | 2 findings | - | 0.00 |

## License

CC-BY-4.0 — auto-generated by cross_connection_engine_v2.py.
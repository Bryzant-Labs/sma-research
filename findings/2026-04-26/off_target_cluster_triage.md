# Off-Target Cluster Triage — 2026-04-26

**Source**: NIM Saturator boltz2_offtarget_iptm worker, 2026-04-21 → 2026-04-25 (5 days, 14-day window queried)
**CEO escalation**: Tier-2 from CORTEX CEO 2026-04-26 11:27 UTC
**Reviewer**: Opus 4.7, internal triage only (NOT external — Quality CQO 3-LLM gate not run)

## Summary

CEO surfaced 7 hits ≥0.86. The actual cluster is **dramatically larger** — **60+ hits at iPTM ≥ 0.97** across 8 named drugs + 7 unresolved compound_card UUIDs. Statistical pattern raises confidence + concern.

## Named-drug cluster (reproduced ≥2 hits, max iPTM ≥ 0.85)

### 🔥 Repurposing leads (mechanistically plausible)

| Drug | Off-target | Hits | Max iPTM | Mean | Why it matters |
|---|---|---|---|---|---|
| **Fasudil** | **GRK2** | 4 | 0.983 | 0.982 | β-adrenergic GRK2 inhibition = HF + COPD therapeutic axis. Fasudil already kinase inhibitor — extends repurposing horizon |
| **Risdiplam** | **S1PR5** | 5 | 0.983 | 0.977 | S1PR5 oligodendrocyte-enriched; could explain CNS effects. Chai-1 ortho was already queued (CEO surfaced 0.97) |
| Risdiplam | GPR42 | 7 | 0.982 | 0.971 | FFA-receptor family pseudogene paralog. Reproducibility 7× = strong signal but biology unclear |
| Ataluren | RIPK2 | 3 | 0.982 | 0.982 | RIPK2 = NLR/inflammasome kinase; could explain anti-inflammatory side effects |

### ⚠️ Safety signals (require validation before clinical comms)

| Drug | Off-target | Hits | Max iPTM | Mean | Concern |
|---|---|---|---|---|---|
| **Pyridostigmine** | **OPRD1** | 4 | 0.985 | 0.980 | δ-opioid receptor. Pyridostigmine peripheral only (no BBB) so risk = peripheral opioid signaling; may explain GI side effects |
| Pyridostigmine | OPRK1 | 2 | 0.984 | 0.984 | κ-opioid receptor |
| **Riluzole** | **HTR5A** | 4 | **0.988** | 0.986 | 5-HT5A serotonin receptor. Riluzole's known psychiatric SE may map here |
| Riluzole | HTR1A | 4 | 0.982 | 0.980 | 5-HT1A — partial overlap with riluzole's known glutamate/serotonin pharmacology |
| Riluzole | ADORA1 | 6 | 0.983 | 0.980 | Adenosine A1 — could explain riluzole sedation |
| Riluzole | BTK + PTK6 + TEC + FGR + CSK | 4×3-4 | ~0.98 | ~0.98 | **Multi-kinase pan-binding pattern — likely Boltz-2 ATP-pocket bias** |
| **Amifampridine (4-AP)** | PTK6 + PRKX + BTK + MAPK10 | 1× each | 0.98-0.987 | ~0.98 | Same kinase-pan pattern. 4-AP is a K+ channel blocker — kinase binding biologically odd |

### Pattern flag (statistical warning)

`riluzole`, `amifampridine`, and several compound_card UUIDs all hit the same kinase set: **BTK, PTK6, PRKX, TEC, FGR, CSK**. Three explanations:

1. **Real**: kinase ATP pockets are highly conserved; small molecules with planar aromatic scaffolds often promiscuously bind multiple kinases (cf. staurosporine, sunitinib known polypharmacology).
2. **Boltz-2 systematic FP**: model may over-score docking into well-characterized kinase folds in its training set.
3. **Predictive cluster**: hits may correctly identify ATP-mimetic ligands by structure but mis-rank specificity.

**Action**: triangulate with Chai-1 + ESMfold orthogonal scoring (already in `chai1_orthogonal_validation` queue, 862 rows pending). Without ortho, **do not assert any of these as validated leads externally**.

## Unresolved compound_card UUIDs (7 IDs)

Not in `drugs` table → likely `compound_cards` or `designed_molecules` per Rule -2g-v2 (drugs table = regulatory-only, 2026-04-21). The query left-join missed them. UUIDs:

```
30db8ef6-cd9d-4db4-b3ff-fc3557235802 → HTR5A, BTK, ADORA1, FGR, CSK, TEC, ...
a0e91870-26b7-4a20-a9a3-5c974bf55fe3 → PRKX, BTK, TGFBR1, ULK3, CDK5, ACVRL1, GRK2, FGR, CHEK1, PTK6
de63e240-b566-4787-8ef4-61069ff03dcf → PRKX, BTK, TGFBR1, ULK3, ACVRL1, CDK5, CHEK1, PTK6, FGR
d62a4c4f-265b-4d34-9987-6bb4502311b8 → GRK2, PRKX
e90ca21c-d0dd-4113-a7d2-6f11ed20eb96 → OPRD1
1bd55a6b-093c-4f32-9c56-e3216f8d10c6 → S1PR5, GPR42
3ada885c-645e-4a57-bdff-6ea670cf85ee → RIPK2
```

Their off-target patterns **mirror named drugs** (riluzole-like multi-kinase, risdiplam-like S1PR5/GPR42). These may be GenMol-generated analogs of approved drugs (intentional design or accidental similarity). Worth resolving via:

```sql
SELECT id, smiles, name, source FROM compound_cards WHERE id IN (...);
SELECT id, smiles, name FROM designed_molecules WHERE id IN (...);
```

## Recommended next actions

1. **Push `chai1_orthogonal_validation` through** — 862 rows pending, current rate ~50/day at NIM Boltz-2 25-50% ok-rate. CEO is right that NIM tier upgrade or rate reduction is the bottleneck. The triage above cannot be promoted to "validated" without ortho.
2. **Resolve the 7 compound_card UUIDs** — query both `compound_cards` and `designed_molecules` to identify what these compounds are; if they're GenMol designs, document parent scaffold.
3. **Literature triangulate top 4 named-drug hits**:
   - Riluzole + HTR5A — pubmed search
   - Pyridostigmine + OPRD1 — known opioid system interactions
   - Fasudil + GRK2 — kinase selectivity literature
   - Risdiplam + S1PR5 — emerging ADMET data
4. **Boltz-2 calibration audit** — sample 10 known-negative drug-target pairs (e.g. `aspirin × LIMK2`), measure iPTM distribution. If known-negatives also score ≥0.95, the cluster is a model artifact, not a finding.

## Gate status (Quality CQO)

❌ **NOT externally publishable**. Internal review only. Required before any external communication:
- 3-LLM consensus PASS per HARD-RULE-3-llm-consensus-gate
- Chai-1 orthogonal ≥0.7 on top 5 hits
- Boltz-2 calibration audit (action 4 above)
- Literature triangulation (action 3 above)

## Cross-refs

- CORTEX CEO escalation: `cortex-ceo/state/events.log` 2026-04-26 11:27 UTC
- Source: NIM Saturator `boltz2_offtarget_iptm` worker
- Postgres `claims` table, predicate=`boltz2_offtarget_iptm`, last 14 days
- HARD-RULE-3-llm-consensus-gate, RULE-0-LLM-CSUITE-ARCHITECTURE

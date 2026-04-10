# Cross-Connection Methodology

## Why

"Don't forget projects" is level 1.0. The real value of a curated research platform is **finding connections nobody else sees** — hypotheses that emerge ONLY when you cross-reference multiple campaigns.

## How

The cross-connection engine combines multiple data sources:

1. **Structured API data** — SMA Platform's 457 endpoints provide targets, drugs, combinations, hypotheses, evidence, scores, digital twin results
2. **Semantic CORTEX queries** — natural-language questions across the knowledge graph
3. **CORTEX cross_connections tool** — pre-computed unexplored approach pairs
4. **Local findings markdown** — campaign-level summaries
5. **PROJECT_CATALOG.md** — master campaign index with verdicts and gaps

## Cross-queries that work

| Query | Sources combined | Output |
|---|---|---|
| Pathway coverage | CORTEX + compound index | Compounds hitting multiple axis nodes |
| Orphan analysis | Filesystem + catalog | MDs paid for but not analyzed |
| Combo opportunities | Platform twin + our hits | New combo proposals |
| CORTEX unexplored | cross_connections tool | Approach pairs with shared targets |
| Knowledge gaps | CORTEX gaps + platform evidence_gaps | What to research next |

## Example finding (2026-04-10 manual seed)

Manual cross-reference of PROJECT_CATALOG produced 6 publishable hypotheses in 30 minutes:

1. 4-AP + LIMK2 hit = bidirectional ROCK-LIMK2-CFL2 coverage
2. ESM-2 0.990 paradox → selectivity-determinant residue extraction
3. Fasudil + LIMK2 + 4-AP triple cocktail
4. Our gRNA + AAV RFdiffusion = full cure vehicle
5. Orphan SMN2 vs Kv1.2 MD (never analyzed)
6. RIPK1 anti-necroptosis track re-validation

See: `findings/2026-04-10/CROSS_CONNECTIONS_2026-04-10.md`

## Automated run (v2)

```bash
python3 scripts/cross_connections/cross_connection_engine_v2.py --publish
```

Outputs to `findings/insights/YYYY-MM-DD_cross_connections_v2.md` and pushes a summary back to CORTEX.

## Schedule

- Weekly: Sunday 06:00 UTC
- On-demand: any time
- On new finding: should be triggered (not yet automated — TODO)

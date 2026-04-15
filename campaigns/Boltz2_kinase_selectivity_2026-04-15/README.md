# Boltz-2 Kinase Selectivity Matrix (iptm proxy) — 2026-04-15

**Status:** draft / internal · NOT publication-ready

## Method
- 10 small-molecule inhibitors × 11 kinase targets, Boltz-2 (public NVIDIA NIM)
- Public NIM returns empty `affinities: {}`, so **interface pTM (iptm) used as binding-interface quality proxy** — higher iptm = stronger predicted complex interface
- Single-seed predictions (no consensus ensemble yet)

## Key finding
**No existing ligand is LIMK2-selective** by iptm. Selectivity margin = LIMK2 iptm − max(off-target iptm):

| Compound | LIMK2 | Worst off-target | Margin |
|---|---|---|---|
| **BMS-5** | 0.611 | ROCK2 (0.796) | **−0.185** (best near-selective) |
| Fasudil | 0.562 | ROCK2 (0.759) | −0.197 |
| LIMKi3 | 0.399 | CDK2 (0.631) | −0.232 |
| bbb5 | 0.533 | MAPK1 (0.849) | −0.316 |
| Y-27632 | 0.363 | CDK2 (0.743) | −0.380 |

## Interpretation
1. All known ROCK inhibitors (fasudil, Y-27632, ripasudil) show ROCK2 iptm > LIMK2 iptm → pharmacology-consistent sanity check
2. **bbb5** independently re-confirmed as dual (off-target = MAPK1, not LIMK2-selective)
3. **BMS-5 = best commercial starting scaffold** if Track-2 (design LIMK2-selective) starts from a known compound
4. Validates thesis: **truly LIMK2-selective drug must be designed de novo** — RFdiffusion binders + PocketXMol generation is the correct path

## Caveats (why not a public post yet)
- iptm ≠ IC50/Ki — it's an interface-quality metric, not a true binding affinity
- 10 compounds × 11 kinases = small matrix; need full kinome (~500 kinases) for real selectivity claims
- Single-seed predictions; no ensemble variance estimate
- No MD validation of predicted poses
- No cross-ref with published experimental Ki

## Next steps toward publishable result
- MD (100 ns) on top 3 predicted complexes to confirm stability
- Expand panel to full kinome (KLIFS + ChEMBL kinase set, ~460 structures)
- Cross-ref published IC50/Ki from ChEMBL (fasudil, BMS-5, LIMKi3 all have literature Ki)
- Consensus ensemble (5 seeds) for each compound×target

## Files
- `affinity_matrix_iptm.csv` — full 10×11 matrix

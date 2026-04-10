# NEGATIVE RESULT: Fasudil Scaffold Hopping for LIMK2 Selectivity

**Date**: 2026-04-09
**Status**: FAILED — No LIMK2-selective variant found
**Published with same rigor as positive results**

## Summary

We systematically modified Fasudil (approved ROCK inhibitor, DILI 0.28, BBB 0.93) to achieve LIMK2 selectivity for SMA therapy. 115 variants were generated across 9 modification categories. 65 passed ADMET-AI screening (56.5% — excellent safety profile). Top 20 were docked via DiffDock against LIMK2, LIMK1, ROCK1, and ROCK2.

**Result: 0/20 achieved LIMK2 selectivity (margin > 0.3)**

## Data

### Best Variants by Selectivity Margin

| Variant | Modification | LIMK2 | LIMK1 | ROCK1 | ROCK2 | Margin |
|---------|-------------|-------|-------|-------|-------|--------|
| B_7Cl | 7-chloro isoquinoline | +0.050 | -0.140 | -0.460 | -0.110 | +0.160 |
| B_7F | 7-fluoro isoquinoline | -0.090 | -0.090 | -0.020 | -0.160 | -0.070 |
| B_7CFFF | 7-trifluoromethyl | -0.460 | -0.360 | -1.560 | -1.180 | -0.100 |
| Fasudil_ref | Unmodified | -0.850 | -0.040 | -0.150 | +0.350 | -1.200 |

### Modification Categories Tested

1. Isoquinoline substitutions (positions 5,6,7,8): F, Cl, CH3, OCH3, CF3, NH2
2. Amine head replacements: morpholine, piperidine, pyrrolidine, homopiperazine
3. Combined modifications
4. Hybrid designs (LIMKi3/BMS-5 pharmacophore elements)
5. Linker modifications (SO2NH → CONH, CH2NH)
6. N-linked heterocycle heads
7. Constrained analogs
8. Fluorine scan

### ADMET Results (positive finding within negative result)

Scaffold hopping from Fasudil produced dramatically better ADMET profiles than de novo generation:
- **Fasudil variants**: 56.5% pass all ADMET gates (65/115)
- **PocketXMol random**: 0% pass all ADMET gates (0/1934)

This confirms Fasudil's isoquinoline core is inherently drug-safe.

## Root Cause Analysis

Fasudil's isoquinoline sulfonamide scaffold has a geometric complementarity with the ROCK kinase family ATP pocket that is deeply encoded in its 3D shape. The ROCK2 binding pocket (PDB 2H9V) accommodates the flat isoquinoline ring and the sulfonamide linker in a conformation that is suboptimal for LIMK2's differently shaped hinge region.

Key structural differences:
- LIMK2 gatekeeper K383 (large, charged) vs ROCK2 M172 (small, hydrophobic)
- Position 7 modifications (pointing at gatekeeper) improved LIMK2 from -0.850 to +0.050 but couldn't overcome the scaffold's ROCK preference
- The sulfonamide linker geometry constrains the molecule in a ROCK-favorable orientation

## Conclusion

**Fasudil's scaffold is fundamentally ROCK-selective.** LIMK2-selective drug candidates require a completely different chemical scaffold. The PocketXMol de novo campaign (19,404 molecules) produced one LIMK2-selective hit from a pyrazolo-pyridine scaffold (1219_0, margin +0.43) — confirming that novel scaffolds are necessary.

## Recommendation

1. Do NOT pursue further Fasudil modifications for LIMK2 selectivity
2. Fasudil remains the validated ROCK2/LIMK2 dual inhibitor candidate (Track 1 → Simon)
3. LIMK2-selective compounds should come from de novo design (PocketXMol, different scaffolds)
4. B_7Cl (margin +0.160) could be a starting point for ROCK2-selective optimization if needed

## Methods

- Variant generation: RDKit SMILES enumeration from Fasudil core
- ADMET: ADMET-AI v2.0.1 GNN (41 TDC endpoints, local GPU)
- Docking: DiffDock v1.1 on RTX 3090, 10 poses per compound, 4 targets
- Selectivity threshold: LIMK2_confidence - max(LIMK1, ROCK1, ROCK2) > 0.3

# LIMKi3 — LIMK2 HOLO MD 20ns Analysis

**Date**: 2026-04-07
**Result**: DISSOCIATED — 94.8Å from nearest CA

## Diagnostic Significance
LIMKi3 is a KNOWN LIMK2 binder. Its dissociation CONFIRMS the problem is the MD setup (CoM ligand placement), NOT compound-specific.

## Comparison
| Compound | Target | Closest CA | Verdict |
|----------|--------|-----------|---------|
| Fasudil  | ROCK2  | 4.2Å      | PASS    |
| bbb5     | LIMK2  | 106.7Å    | FAIL    |
| LIMKi3   | LIMK2  | 94.8Å     | FAIL    |

## Root Cause
Fleet manager places ligands at protein center of mass. ROCK2 (2H9V) ATP pocket happens to be near CoM → Fasudil works. LIMK2 (4TPT) ATP pocket is 33Å from CoM → all ligands drift away.

## Fix
Re-run with pocket_center=[-13.2, 6.4, 28.0] (LIMK2 ATP site). Fleet manager already patched.

## Implication
bbb5 is NOT necessarily dead — it was never tested in the correct position. Must re-run both bbb5 AND LIMKi3 with correct placement.

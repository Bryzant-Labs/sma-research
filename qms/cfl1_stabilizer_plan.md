# CFL1 Stabilizer (F-actin-protective) Campaign — Pre-Flight Plan

**Status:** DRAFT (pre-flight)
**Date:** 2026-04-17
**Campaign ID:** `cfl1_stabilizer`
**Purpose:** Direct CFL1/actin-interface small-molecule stabilizer — compounds that block cofilin-actin association, preserving F-actin against cofilin severing. Bypasses the kinase-layer direction ambiguity (ROCK2-LIMK2) from today's meta-analysis.
**Author:** Claude (Opus 4.7), dispatched by architect

## Biological rationale (from today's 3-dataset SMA MN meta-analysis)

- **Meta-analysis finding (2026-04-17)**: ROCK-LIMK-CFL axis IS disrupted, but directionality is model-dependent:
  - ROCK2: pooled **−0.254** (robust DOWN, cross-dataset)
  - LIMK2: model-dependent (not consistent — retraction from earlier +2.81× claim still pending)
  - CFL1: pooled **−0.104** (not significant)
  - Overall axis: disrupted but kinase-layer direction uncertain
- **Strategic pivot**: rather than target the kinase layer (uncertain direction → could hit either way in different MN), target **CFL1 directly at the actin-binding interface**.
- **Mechanism**: a small molecule that binds the cofilin-actin interface and INHIBITS cofilin-actin association = **preserves F-actin** = direct cytoskeletal support. Bypasses the LIMK2-direction ambiguity entirely.
- **Chemotype space**: cofilin inhibitors are a sparse area globally. A few tool compounds (AC-29, LIM-kinase inhibitors as indirect cofilin modulators) but no clinical-stage cofilin-interface inhibitor. EXPLORATORY.
- **Caveat**: CFL1 disruption is modest in our meta (−0.104, NS). The target rationale is axis-level (ROCK2-LIMK2-CFL disrupted), not CFL1-specific-magnitude.

## Instance

- Vast contract: **35120540** (warm, PocketXMol already installed)
- Host: `ssh4.vast.ai:10540` (root user, key `~/.ssh/id_ed25519_vastai`)
- GPU: **1× A100 PCIE 40 GB** (Japan)
- Image: PyTorch warm
- PocketXMol: `/opt/PocketXMol` AND `/workspace/PocketXMol` (git SHA `65488cf635c856101dbe703ac97e2f10f58e005c`)
- Cost: ~$0.50-0.70/hr

## Target

| Parameter | Value | Source |
|---|---|---|
| Gene | CFL1 | UniProt P23528 |
| Canonical name | Cofilin-1 (non-muscle isoform) |
| PDB | **3J0S** | RCSB: "Remodeling of actin filaments by ADF/Cofilin proteins" (Galkin et al 2011 PNAS) |
| Chain (CFL) | M, N, O, P, Q, R, S, T, U, V, W, X (12 cofilin copies) | COMPND verified |
| Chain (actin) | A, B, C, D, E, F, G, H, I, J, K, L (12 actin copies) | COMPND verified |
| **CFL species caveat** | **Cofilin-2 (CFL2) in 3J0S, NOT CFL1** | CFL1 ↔ CFL2 identity >80%, actin-binding residues conserved — use 3J0S as surrogate for CFL1-actin interface |
| Actin source | Chicken β-actin (muscle) — CFL2 is muscle isoform | Biologically appropriate pairing |
| Strategy | Target the **cofilin-actin interface** on the cofilin side (actin-contact residues ~90-115) OR at the cofilin-cofilin contact between successive cofilin subunits on the filament | |
| Pocket center | TBD (computed on-instance from cofilin-actin contact residues) | Will derive |
| Pocket radius | 10.0 Å | PocketXMol SBDD convention |
| Molecule count | 600 | Per brief |
| Batch size | 50 | Matches earlier campaigns |

### Pocket derivation strategy (HARD — to be confirmed on-instance)

3J0S is a cryo-EM cofilactin filament (resolution ~9 Å, sufficient for pocket localization at 10 Å radius). Strategy:

1. **Extract chain M (one cofilin copy)** + its contacting actin chain (chain A).
2. **Identify cofilin-actin interface residues**: known CFL-actin contact residues are M96, R105, Y82, and the F-loop (residues 95-106 in CFL1/CFL2 numbering). These sit at the **cofilin → actin** interface.
3. **Pocket center** = mean heavy atoms of cofilin interface residues M96/R105/K112 (CFL2 numbering, equivalent to CFL1 numbering in the conserved core).
4. **Target** = a pocket ON THE COFILIN SURFACE that faces actin. Compounds designed here will block cofilin-actin association → preserve F-actin.

Alternative (fallback): cofilin-cofilin longitudinal contact along the filament (between chain M and chain N successive cofilins). This pocket closes the cooperative severing mechanism. Will try pocket #1 first.

**Warning**: cryo-EM resolution (~9 Å) is lower than crystal. PocketXMol may complain about missing side chains. **Mitigation**: use PDBFixer to rebuild side chains before pocket derivation. If 3J0S is unusable after fixup, fallback to 5HVK (LIMK1-D460N + full-length CFL1 crystal, 2.1 Å) — but 5HVK's CFL1 is in LIMK1-bound conformation, not actin-bound.

## Workflow

1. **SSH probe** (already verified, PocketXMol warm).
2. **Fetch 3J0S** from RCSB (already done to /tmp on-instance).
3. **Extract chains M (cofilin) + A (contacting actin)** → `3j0s_MA.pdb` in `/root/cfl1_work/`.
4. **Run PDBFixer** to rebuild missing side chains (cryo-EM at 9 Å often has sparse side-chain placement).
5. **Identify cofilin-actin interface residues** on chain M (CFL2): M96/R105/K112 or equivalent. Compute pocket center as mean heavy atoms of these residues on chain M.
6. **Strip to chain M only** (cofilin surface pocket, protein context is chain M).
7. **Write task JSON + YAML** (batch_size 50, n_molecules 600).
8. **Smoke test: 5 molecules** with `--n_mols 5 --batch_size 5`. PASS = 5 valid SDFs.
9. **Full launch** in tmux session `pxm_cfl1` (600 mol). Verify GPU util > 60% after 5-10 min.
10. **Rsync SMILES** to `/home/bryza/fleet-results/cfl1_stabilizer/`.
11. **BBB hardfilter** < 0.5 drop (MN cytoplasmic target — BBB crucial for spinal cord penetration).
12. **STAGE Boltz-2 queue** (top 100) to `queue.jsonl`. DO NOT launch — supervisor consumes.
13. **Write DRAFT `/home/bryza/sma-research/qms/cfl1_stabilizer_RESULTS.md`** with EXPLORATORY caveats + CFL2-not-CFL1 caveat.
14. **triple_llm_verify 3/3 PASS** → DRAFT → VERIFIED.

## Quality Gates (HARD)

| Gate | Rule | Failure action |
|---|---|---|
| Plan written | This file exists BEFORE GPU burn | HALT |
| PDB title verified | 3J0S = cofilactin filament | ALREADY VERIFIED |
| CFL species caveat | CFL2 in 3J0S, not CFL1 | EXPLICIT in results |
| Interface residue sanity | M96/R105/K112 at cofilin-actin contact | HALT if off |
| PDBFixer side chains | Ran before pocket derivation (cryo-EM 9 Å) | HALT if chains sparse |
| Smoke test | 5 valid SDFs + SMILES | HALT |
| GPU util | > 60% after 5 min | Debug |
| BBB hardfilter | Pass rate reported, > 30% expected | Report |
| EXPLORATORY framing | CFL1-stabilizer is first-in-class, CFL2 surrogate | HARD |
| Status stays DRAFT | Until triple_llm_verify 3/3 | No external comms |

## Critical caveats

- **CFL2 ≠ CFL1** — but actin-contact residues are conserved. Pocket is generalizable but strict CFL1-specificity not guaranteed by this PDB.
- **cryo-EM 9 Å resolution** — may need PDBFixer. Fallback = 5HVK (CFL1 alone, LIMK1 bound — different conformation).
- **CFL1 ΔAbundance in SMA is modest (−0.104, NS)** — the strategic value is bypassing LIMK2-direction-ambiguity, not magnitude of CFL1 perturbation.
- **F-actin stabilizers** are a known class (phalloidin, jasplakinolide) but they are pan-actin stabilizers, not cofilin-interface-specific. Our angle is specificity.
- **EXPLORATORY only**.

## Reproducibility Trail

- PocketXMol git SHA: `65488cf635c856101dbe703ac97e2f10f58e005c`
- Zenodo weights: record 17801271
- PDB: 3J0S, chains M (cofilin-2) + A (actin, muscle chicken)
- Pocket center: `{TBD — computed on-instance}`
- Compute: 1× A100 40GB, ~3-5 min full run expected (slower than 80GB)

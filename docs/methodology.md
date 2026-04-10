# Methodology — Pipeline v2.2

This document describes the computational pipeline used across all SMA campaigns in this repository.

## Overview

Pipeline v2.2 is a **13-stage** evidence-generation pipeline running on a self-managed Vast.ai GPU fleet. Every campaign in `campaigns/` is produced by some subset of these stages.

## Stages

1. **Target selection** — Evidence graph query (scRNA-seq, bulk RNA-seq, proteomics, literature)
2. **Structure retrieval / prediction** — PDB → AlphaFold2 / ESMfold fallback
3. **Pocket detection** — DoGSiteScorer / fpocket
4. **Ligand sourcing** — ChEMBL, DrugBank, de-novo (MolMIM / GenMol / PocketXMol)
5. **Drug-likeness filter** — Lipinski, QED, PAINS, BBB
6. **ADMET prediction** — ADMET-AI (41 endpoints)
7. **Docking** — DiffDock v2.2 (NVIDIA NIM) or AutoDock Vina (CPU fallback)
8. **Selectivity screen** — Docking against paralog panel (LIMK1, ROCK1/2, JAK2 for kinases)
9. **Molecular dynamics** — OpenMM 8.2 CUDA, typically 100 ns production run
10. **Metadynamics** — For binding-free-energy refinement when MD is inconclusive
11. **MMPBSA / MMGBSA** — Post-MD energy rescoring
12. **QM/MM** — For ligands where quantum effects matter (catalytic sites)
13. **Report generation** — JSON + markdown finding → `findings/YYYY-MM-DD/`

## Quality gates

Every finding passes through:

- **Reproducibility check** — all inputs (PDB IDs, SMILES, force-field, seed) logged in metadata
- **Negative-control selectivity** — random off-target panel must not score highly
- **Rigorous negative-result publication** — failed campaigns are published with the same rigor as positives (see `campaigns/Fasudil_scaffold_hop/` for an example)

## Tools and versions

See the Tools table in the top-level [README.md](../README.md).

## Compute infrastructure

- **GPUs**: Vast.ai marketplace — RTX 3090 / A100 / H100 depending on task
- **Orchestration**: Autonomous fleet manager polling instances every 5 min
- **Budget**: ~$1/hour averaged
- **Storage**: GPU results sync to Dropbox → selective copy to this repo

## Related documents

- [`reproducibility.md`](reproducibility.md) — step-by-step reproduction instructions
- [`data_access.md`](data_access.md) — how to access large trajectories

# 4-Aminopyridine (4-AP) Multi-Target SMA Campaign

## Key Finding
4-AP (FDA-approved MS drug) binds **5 SMA targets simultaneously**, with the strongest hit on **CORO1C (+0.251)** — a novel SMA modifier with zero prior drug screening publications.

## Contents

### Documents
- [Findings Summary](4-AP-FINDINGS-SUMMARY.md) — Complete overview of 18 GPU analyses
- [Computational Analysis](4-AP-Computational-Analysis.md) — Draft for academic discussion
- [Analysis Tasks 2-4](4-AP-ANALYSIS-TASKS-2-4.md) — SMD comparison, analog ranking, co-binding

### Figures
| Figure | Description |
|--------|-------------|
| [fig1_diffdock_heatmap.png](figures/fig1_diffdock_heatmap.png) | DiffDock v2.2 confidence scores — 7 compounds × 7 targets |
| [fig2_energy_comparison.png](figures/fig2_energy_comparison.png) | MD energy profiles: SMD vs FEP vs Kv1.2 control |
| [fig3_admet_radar.png](figures/fig3_admet_radar.png) | ADMET safety radar (BBB 79%, bioavailability 94%) |
| [fig4_multitarget_pathway.png](figures/fig4_multitarget_pathway.png) | 4-AP → 5 targets → 3 pathways → motor neuron |
| [fig5_smd_unbinding.png](figures/fig5_smd_unbinding.png) | Steered MD unbinding force analysis |
| [fig6_cost_comparison.png](figures/fig6_cost_comparison.png) | Treatment cost: $2K vs $340K-$2.1M/year |

### Raw Data
| File | Description |
|------|-------------|
| [data/energy/](data/energy/) | MD simulation energy CSVs (SMD, FEP, Kv1.2) |
| [data/structures/](data/structures/) | PDB structures (9 files: CORO1C, Kv1.2, SMN2 complexes) |
| [data/docking/](data/docking/) | DiffDock analog screening scores (73 MolMIM analogs vs Kv1.2) |
| [data/4AP_admet.json](data/4AP_admet.json) | Full ADMET profile (TDC benchmarks) |

### Trajectories (large files)
DCD trajectory files (37 GB total) are available via Dropbox shared folder. Contact christian@bryzant.com for access.

## Computational Campaign (18 GPU tasks)
| Category | Tasks | Tools |
|----------|-------|-------|
| Molecular Docking | 5 | DiffDock v2.2 NIM + Local |
| MD Simulations | 7 | OpenMM 8.2 CUDA |
| Free Energy | 1 | OpenMM FEP |
| Steered MD | 2 | OpenMM SMD |
| Special Analyses | 3 | Electrostatics, Mutants, Selectivity |
| Molecule Design | 2 | GenMol, MolMIM |
| Safety Profiling | 1 | ADMET-AI (TDC) |

## Multi-Target Profile
```
4-AP → CORO1C  (+0.251)  Actin Dynamics     ← NOVEL, #1 hit of 378 pairs
4-AP → NCALD   (pos.)    Calcium Signaling
4-AP → SMN2    (+0.100)  Primary SMA Gene
4-AP → SMN1    (pos.)    SMA Gene
4-AP → UBA1    (pos.)    Protein Homeostasis
```

## Platform
All data queryable at https://sma-research.info

---
*Christian Fischer | Bryzant Labs | April 2026*
*Computational analysis — experimental validation required*

# SMA Research -- Open Computational Drug Discovery

Evidence-first drug discovery for Spinal Muscular Atrophy.
40,000+ compute jobs. 197K evidence claims. 818K screened compounds.

**Platform**: https://sma-research.info |
**GPU Results**: https://sma-research.info/gpu-results/ |
**License**: [CC-BY-4.0](LICENSE)

*All data in this repository are computational predictions. Experimental validation is required before any therapeutic claim.*

---

## Pipeline Overview (v2.5)

The SMA Research Platform runs a 10-stage computational drug discovery pipeline with three knowledge gates that filter biologically implausible hypotheses before expensive GPU/TPU compute.

**Stages:**

0. Target nomination (literature + scRNA-seq)
0.5. BIO-GATE -- LLM-based biological plausibility filter
1. Structure prediction (AlphaFold 3, Boltz-2, Chai-1, OpenFold3)
2. Integrated ADMET screening (BBB, hERG, CYP, hepatotox)
2.5. TARGET-GATE -- druggability and mechanism-of-action check
3. Molecular docking (DiffDock, AutoDock Vina, NeuralPLexer)
3.5. DOCK-GATE -- pose quality and binding mode validation
4. De novo molecule generation (GenMol, MolMIM, ProteinMPNN, RFDiffusion)
4.5. Interface analysis (residue extraction, cross-method Jaccard, alanine scan)
5. Molecular dynamics (100 ns GROMACS on CUDA, MM-PBSA free energy)
6. Multi-method consensus and evidence synthesis

Each compound requires agreement across at least two independent structural methods before advancing. The three knowledge gates (HR-23) reduce wasted compute by 40-50% by applying LLM biological knowledge before GPU allocation.

---

## Current Therapeutic Axes

| Axis | Target(s) | Status | Key Evidence |
|------|-----------|--------|-------------|
| ROCK2 kinase inhibition | ROCK2 (O75116) | Flagship | AF3 iPTM 0.82-0.89, 96 pipeline-complete compounds, scRNA-seq signal (exploratory) |
| p38/MK2 stress signaling | MAPK14, MAPKAPK2 | Active | AF3 iPTM 0.89, motor neuron stress response literature |
| Kv2.1 ion channel | KCNB1 | Discovery | Novel target, computational nomination |
| MCU calcium signaling | MCU | Discovery | Mitochondrial calcium hypothesis |
| SNPH mitochondrial transport | SNPH | Discovery | Axonal transport rescue rationale |
| NRF2-KEAP1 oxidative stress | NFE2L2, KEAP1 | Validated | Budapest Congress 2026 confirmation |
| HDAC6 protein homeostasis | HDAC6 | Active | Proteostasis rescue pathway |
| 4-AP symptomatic | Kv channels | Active | Complementary to SMN-restoration therapies |

---

## Compute Infrastructure

**Free tier (primary):**
- NVIDIA NIM -- 6 API endpoints (Boltz-2, ProteinMPNN, RFDiffusion, GenMol, MolMIM, OpenFold3)
- Dell workstation -- RTX GPU + 12-core CPU (AF3, Boltz-2 native, Vina, AutoDock-GPU)
- Google TPU Research Cloud -- TPU v4-8 (AlphaFold 3 native, JAX/Haiku)
- DGX Spark -- 2x GB10 (Chai-1, Boltz-2 native)

**Paid tier (on-demand):**
- Vast.ai spot instances -- RTX 4090 (100 ns MD + MM-PBSA, pre-baked Docker images)

**Storage:**
- Spark1 (canonical), Backblaze B2 (mirror), Dropbox (deliverables)

Fleet utilization target: 85-95% active capacity. Autonomous C-suite (6 AI roles) manages dispatch, quality, compliance, and storage without manual intervention.

---

## Key Findings

**ROCK2 as SMA therapeutic target:**
- AF3 structural predictions show strong binding (iPTM 0.82-0.89) across ROCK2 compound series
- scRNA-seq reanalysis (GSE290980, pseudobulk DESeq2) shows ROCK2 expression signal in SMA motor neurons -- exploratory, n=2 donors, not statistically significant after correction
- 96 compounds have completed the full 10-stage pipeline through ROCK2
- Fasudil (existing ROCK inhibitor) acts via muscle, not direct neuroprotection (Bowerman 2012)

**Structural validation:**
- AF3 replication of ROCK-LIMK-CFL cascade confirmed (ROCK2 x CFL2 iPTM 0.82, independently replicated)
- ROCK isoform selectivity discovered: ROCK1 x CFL1 = 0.12 vs ROCK2 x CFL2 = 0.82 (delta 0.70)
- NRG1 x ErbB3 ECD = iPTM 0.800 (NMJ signaling, publication-grade)
- First de novo binder above publication threshold: BINDER_ROCK2_414 = 0.68

**Corrections and negative results (published with equal rigor):**
- LIMK2 "+2.81x upregulation" claim RETRACTED -- meta-analysis (GSE290979, GSE302774, GSE87281) shows LIMK2 is mildly DOWN in SMA MN, not UP. See `qms/CORRECTIONS_LOG.md`
- Fasudil scaffold hop: 0/20 variants achieved LIMK2 selectivity. Isoquinoline sulfonamide scaffold is inherently ROCK-preferring
- 4-AP does not bind CORO1C therapeutically -- reclassified as Kv-channel compensator
- AF3 high-confidence kinase pairs may model kinase-substrate encounter complexes, not stable PPIs (3-LLM red-team consensus)

**Honest limitations:**
- 0% of MD simulations show ligand residence time (binding kinetics gap)
- scRNA-seq pseudobulk results are not significant after multiple testing correction
- All preclinical findings are computational and unreplicated in wet lab
- Multi-method consensus reduces false positives but does not replace experimental validation

---

## Campaigns

| Campaign | Start | Status | Summary |
|----------|-------|--------|---------|
| ROCK2 compound series | 2026-03 | Active | 96 pipeline-complete, flagship axis |
| p38/MAPK14 axis | 2026-05 | Active | iPTM 0.89, motor neuron stress signaling |
| NRF2-KEAP1 validation | 2026-05 | Validated | Budapest Congress 2026 confirmed |
| Novel target discovery | 2026-05 | Discovery | Kv2.1, MCU, SNPH -- computational nomination |
| scRNA-seq reanalysis | 2026-05 | Active | GSE290980 pseudobulk correction, exploratory |
| 4-AP multi-target | 2026-04 | Corrected | Kv compensation, not CORO1C |
| Fasudil evidence package | 2026-03 | Staged | Muscle-mediated, not neuroprotective |
| PocketXMol LIMK2-selective | 2026-04 | Active | 14 selective hits from 20K screen |
| Fasudil scaffold hop | 2026-04 | Negative | 0/20 selective -- published as negative result |
| SMN2 base editing (ABE) | 2026-04 | Research | Guide safety analysis complete |
| ESM2 kinase similarity | 2026-04 | Done | LIMK1/2=0.990, ROCK1/2=0.998 |
| Boltz-2 kinase selectivity | 2026-04 | Done | Cross-validation with AF3 |

Full campaign details in individual directories under `campaigns/`.

---

## NVIDIA Technology

This project uses NVIDIA infrastructure extensively:

- **NIM Boltz-2** -- protein-ligand and protein-protein structure prediction
- **NIM ProteinMPNN** -- sequence design for de novo binders
- **NIM RFDiffusion** -- protein backbone generation
- **NIM GenMol** -- generative molecule design
- **NIM MolMIM** -- molecular optimization
- **NIM OpenFold3** -- structure prediction
- **CUDA 12.4** -- GPU-accelerated MD (GROMACS), AutoDock-GPU, DiffDock
- **DGX Spark** -- native Boltz-2 and Chai-1 inference

---

## Repository Structure

```
sma-research/
  campaigns/         Per-campaign data, code, and findings
  findings/          Chronological discovery summaries
  structures/        PDB files for target proteins
  molecules/         Compound libraries and generated molecules
  admet/             ADMET screening results
  docking/           Docking scores (Vina, DiffDock)
  md_simulations/    Molecular dynamics trajectories
  figures/           Publication-ready figures
  scripts/           Analysis and pipeline code
  data/              GPU results and reports
  docs/              Methodology and reproducibility notes
  infrastructure/    GPU benchmark data
  qms/               Quality management and corrections log
```

---

## Citation

```
Fischer, C. (2026). SMA Research -- Open Computational Drug Discovery.
Bryzant Labs. https://github.com/Bryzant-Labs/sma-research
```

Machine-readable: [CITATION.cff](CITATION.cff)

---

## License

[Creative Commons Attribution 4.0 International (CC-BY-4.0)](LICENSE)

## Contact

Christian Fischer -- Bryzant Labs -- christian@bryzant.com -- https://sma-research.info

---

*Computational predictions only. No therapeutic claims are made without experimental validation.*

# Computational identification of 4-Aminopyridine as a multi-target compound for Spinal Muscular Atrophy via actin cytoskeleton modulation

## DRAFT — For discussion with Prof. Schoeneberg / Simon

---

### Abstract

4-Aminopyridine (4-AP, Fampridine), an FDA-approved potassium channel blocker, was identified through systematic computational screening as a multi-target compound binding five SMA-relevant proteins. Virtual screening of 378 compound-target pairs using DiffDock v2.2 revealed 4-AP as the highest-confidence binder to Coronin-1C (CORO1C, confidence +0.251), a novel SMA modifier involved in actin dynamics. 100ns molecular dynamics simulations confirmed stable binding, while free energy perturbation and alanine scanning identified key binding residues. 4-AP simultaneously engages NCALD, SMN2, SMN1, and UBA1, suggesting a multi-pathway mechanism complementary to existing SMN2-targeting therapies. As an oral, BBB-penetrant, approved drug (~$2K/year vs $340K-$2.1M for current SMA therapies), 4-AP represents a compelling repositioning candidate warranting experimental validation.

---

### Introduction

Spinal Muscular Atrophy (SMA) is caused by homozygous loss of SMN1, leading to motor neuron degeneration. Current therapies (nusinersen, risdiplam, onasemnogene) all target SMN2 splicing or SMN1 gene replacement. While transformative, they do not address downstream pathology in the actin cytoskeleton, neuromuscular junction, and protein homeostasis pathways increasingly implicated in SMA severity.

CORO1C (Coronin-1C) emerged from our evidence convergence analysis as a novel SMA modifier: downregulated 1.77-fold in SMA patient samples (GSE87281, n=101, FDR=1.5e-71), linked to PLS3 via STRING-DB (score 0.818), and vulnerable to intron retention due to SMN-dependent splicing (112bp intron + 58bp microexon). No prior drug screening for CORO1C has been published.

4-Aminopyridine (4-AP, Dalfampridine) is a voltage-gated potassium channel blocker approved for multiple sclerosis since 2010. Its established safety profile, oral bioavailability (94%), and BBB penetration (79%) make it an ideal repositioning candidate if new indications are identified.

---

### Methods

**Virtual Screening**: DiffDock v2.2 (NVIDIA NIM) was used to dock 54 compounds against 7 SMA protein targets (378 pairs). 4-AP (SMILES: Nc1ccncc1) was included as a known Kv1.2 channel binder (positive control).

**Molecular Dynamics**: OpenMM 8.2 with Amber14/TIP3P force field, 300K, PME electrostatics:
- 4-AP + CORO1C: 100ns production MD (PDB: 2B4E, 136,575 atoms)
- 4-AP + Kv1.2: 100ns positive control (PDB: 2R9R)
- 4-AP + SMN2 pre-mRNA: 100ns (PDB: 4QK9, GROMACS)
- Free Energy Perturbation (FEP): 10ns, 4-AP in CORO1C pocket
- Steered MD (SMD): 10ns, pulling 4-AP from CORO1C and Kv1.2 binding sites
- Alanine scanning: R→A, K→A mutations in CORO1C binding pocket

**Selectivity Control**: 4-AP docked into 10 randomly selected non-SMA proteins to establish specificity.

**ADMET Profiling**: TDC ADMET benchmarks for BBB, hERG, AMES, DILI, bioavailability, CYP interactions.

**Analog Design**: MolMIM scaffold optimization (73 analogs) and GenMol de-novo generation (500 molecules).

All data openly available: https://github.com/Bryzant-Labs/sma-research

---

### Results

#### 1. 4-AP binds CORO1C with highest confidence across all screened pairs
DiffDock v2.2 confidence: **+0.251** (rank 1 of 378 compound-target pairs). For comparison, the average positive hit has confidence ~+0.05.

#### 2. Multi-target binding profile (5 SMA targets)
4-AP shows positive binding to CORO1C (+0.251), NCALD, SMN2 (+0.100), SMN1, and UBA1 — spanning three distinct SMA pathways (actin dynamics, calcium signaling, protein homeostasis).

#### 3. Stable 100ns MD binding
4-AP remained in the CORO1C binding pocket throughout 100ns production MD. Potential energy remained stable at -2,174 ± 2 MJ/mol. Equilibrium RMSD < 2.5 A.

#### 4. Free energy confirms favorable binding
FEP calculation over 10ns (136,575 atoms, 183 ns/day) showed thermodynamically favorable binding.

#### 5. Alanine scanning identifies critical residues
R→A mutations in the CORO1C binding pocket abolished 4-AP binding, confirming specific protein-ligand interactions rather than nonspecific surface association.

#### 6. Selectivity confirmed
Cross-docking of 4-AP into 10 random non-SMA proteins showed no positive binding, confirming target selectivity.

#### 7. Favorable ADMET profile
BBB penetration 79%, oral bioavailability 94%, low hERG risk (12%), low carcinogenicity (4%). Key concern: borderline AMES mutagenicity (55%) — consistent with known 4-AP literature but requires monitoring.

#### 8. Kv1.2 positive control validates methodology
Known 4-AP → Kv1.2 binding reproduced computationally (100ns MD stable), establishing confidence in the CORO1C discovery.

---

### Discussion

This study identifies a potential new mechanism of action for 4-AP in SMA through CORO1C modulation. The CORO1C double-hit hypothesis — SMN loss leads to intron retention, reducing CORO1C, which disrupts actin dynamics in motor neurons — provides a mechanistic rationale for 4-AP's multi-target activity.

**Strengths**:
- Systematic screening (378 pairs) with appropriate controls
- Multiple orthogonal computational methods (docking, MD, FEP, SMD, mutagenesis)
- Known drug with established safety — rapid repositioning possible
- Open data and reproducible methods

**Limitations**:
- Purely computational — no experimental binding data
- DiffDock confidence scores are not binding affinities
- 4-AP is a very small molecule (MW 94) — prone to nonspecific interactions
- Kv1.2 channel blockade may dominate pharmacology in vivo

**Proposed Experimental Validation**:
1. Surface plasmon resonance (SPR): 4-AP vs recombinant CORO1C — measure KD
2. iPSC-derived SMA motor neurons: 4-AP effect on survival, neurite outgrowth, actin dynamics
3. SMNΔ7 mouse model: 4-AP alone and in combination with risdiplam
4. Proteomics: 4-AP-treated SMA fibroblasts — CORO1C, PLS3, CFL2 levels

---

### Conclusion

Computational evidence supports 4-Aminopyridine as a multi-target SMA compound acting through actin cytoskeleton modulation via CORO1C. As an approved, oral, BBB-penetrant drug available at ~1/100th the cost of current SMA therapies, experimental validation of this repositioning hypothesis is warranted.

---

### Figures (to generate)
1. DiffDock confidence heatmap (54 compounds × 7 targets, 4-AP → CORO1C highlighted)
2. 100ns MD trajectory RMSD plot (4-AP in CORO1C vs Kv1.2)
3. CORO1C binding pocket with 4-AP — electrostatic surface + H-bonds
4. Alanine scanning — binding energy change per mutation
5. Multi-target pathway diagram (CORO1C → PLS3 → actin → motor neuron)
6. ADMET radar chart (BBB, bioavailability, hERG, AMES, ClinTox)

---

*Christian Fischer | Bryzant Labs | sma-research.info*
*Computational analysis — experimental validation required*
*Contact: christian@bryzant.com*

---

### Data Availability (Open Access)

All data, figures, and raw results are publicly available:

**GitHub Repository**: https://github.com/Bryzant-Labs/sma-research/tree/main/4-AP-Campaign

| Resource | Link |
|----------|------|
| **Findings Summary** | [4-AP-FINDINGS-SUMMARY.md](https://github.com/Bryzant-Labs/sma-research/blob/main/4-AP-Campaign/4-AP-FINDINGS-SUMMARY.md) |
| **Paper Draft** | [4-AP-PAPER-DRAFT-FOR-PROFESSOR.md](https://github.com/Bryzant-Labs/sma-research/blob/main/4-AP-Campaign/4-AP-PAPER-DRAFT-FOR-PROFESSOR.md) |
| **Fig 1: DiffDock Heatmap** | [fig1_diffdock_heatmap.png](https://github.com/Bryzant-Labs/sma-research/blob/main/4-AP-Campaign/figures/fig1_diffdock_heatmap.png) |
| **Fig 2: Energy Profiles** | [fig2_energy_comparison.png](https://github.com/Bryzant-Labs/sma-research/blob/main/4-AP-Campaign/figures/fig2_energy_comparison.png) |
| **Fig 3: ADMET Radar** | [fig3_admet_radar.png](https://github.com/Bryzant-Labs/sma-research/blob/main/4-AP-Campaign/figures/fig3_admet_radar.png) |
| **Fig 4: Multi-Target Pathway** | [fig4_multitarget_pathway.png](https://github.com/Bryzant-Labs/sma-research/blob/main/4-AP-Campaign/figures/fig4_multitarget_pathway.png) |
| **Fig 5: SMD Unbinding** | [fig5_smd_unbinding.png](https://github.com/Bryzant-Labs/sma-research/blob/main/4-AP-Campaign/figures/fig5_smd_unbinding.png) |
| **Fig 6: Cost Comparison** | [fig6_cost_comparison.png](https://github.com/Bryzant-Labs/sma-research/blob/main/4-AP-Campaign/figures/fig6_cost_comparison.png) |
| **Energy CSVs** | [data/energy/](https://github.com/Bryzant-Labs/sma-research/tree/main/4-AP-Campaign/data/energy) |
| **PDB Structures** | [data/structures/](https://github.com/Bryzant-Labs/sma-research/tree/main/4-AP-Campaign/data/structures) |
| **DiffDock Scores** | [data/docking/](https://github.com/Bryzant-Labs/sma-research/tree/main/4-AP-Campaign/data/docking) |
| **ADMET Profile** | [data/4AP_admet.json](https://github.com/Bryzant-Labs/sma-research/blob/main/4-AP-Campaign/data/4AP_admet.json) |
| **MD Trajectories (37 GB)** | Dropbox shared folder (contact christian@bryzant.com) |
| **Platform (queryable)** | https://sma-research.info |

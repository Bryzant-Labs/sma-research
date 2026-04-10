# SMA Research — Open Drug Discovery

Evidence-first computational drug discovery for Spinal Muscular Atrophy (SMA).
All data **CC-BY-4.0**. Platform: https://sma-research.info

> **This repository is the open-source catalog for every SMA drug-discovery compute campaign run by Bryzant Labs.**
> The structure mirrors [PROJECT_CATALOG.md](CATALOG.md) — one folder per campaign, chronological finding summaries, publication figures, and reproducibility notes.

---

## Campaigns

| Campaign | Start | Status | Current Verdict | Priority |
|---|---|---|---|---|
| [4-AP Multi-Target](campaigns/4-AP/) | 2026-04-02 | CORRECTED | Kv compensation angle (not CORO1C) | HIGH |
| [ROCK-LIMK2-CFL2 axis](campaigns/ROCK-LIMK2-CFL2_axis/) | 2026-03-24 | VALIDATED | Core therapeutic axis for SMA | CRITICAL |
| [Fasudil Evidence Package](campaigns/Fasudil_evidence_package/) | 2026-03-30 | STAGED | Wait for finished package | HIGH |
| [bbb5 dual-binder](campaigns/bbb5_dual_LIMK2_ROCK1/) | 2026-04-05 | DONE | Dual LIMK2/ROCK1, not selective | MEDIUM |
| [PocketXMol LIMK2-selective](campaigns/PocketXMol_LIMK2_selective/) | 2026-04-07 | ACTIVE | 14 selective hits from 20K screen | HIGH |
| [Fasudil scaffold hop](campaigns/Fasudil_scaffold_hop/) | 2026-04-09 | NEGATIVE | 0/20 selective — published negative | DONE |
| [SMN2 Base Editing (ABE)](campaigns/SMN2_base_editing/) | 2026-04-09 | RESEARCH | Liu lab 99% done, we extend | HIGH |
| [ESM-2 kinase similarity](campaigns/ESM2_kinase_similarity/) | 2026-04-10 | DONE | LIMK1/2=0.990, ROCK1/2=0.998 | DONE |
| [RFdiffusion AAV capsid](campaigns/AAV_capsid_design/) | 2026-04-10 | RUNNING | 50 designs, ETA 22:00 UTC | HIGH |

Full catalog with detailed narrative in [CATALOG.md](CATALOG.md).

---

## Structure

```
sma-research/
├── campaigns/           Per-campaign data, code, findings
│   ├── 4-AP/            4-Aminopyridine multi-target screen
│   ├── ROCK-LIMK2-CFL2_axis/
│   ├── PocketXMol_LIMK2_selective/
│   ├── Fasudil_scaffold_hop/
│   ├── Fasudil_evidence_package/
│   ├── bbb5_dual_LIMK2_ROCK1/
│   ├── SMN2_base_editing/
│   ├── ESM2_kinase_similarity/
│   └── AAV_capsid_design/
├── findings/            Chronological markdown findings
│   ├── 2026-04-09/
│   ├── 2026-04-10/
│   └── INDEX.md
├── figures/             Publication-ready figures
├── docs/                Methodology + reproducibility
├── scripts/             Analysis code
└── data/                Legacy GPU results (pre-reorg)
```

---

## Quick Links

- **Platform**: https://sma-research.info
- **Findings by date**: [findings/INDEX.md](findings/INDEX.md)
- **Full catalog**: [CATALOG.md](CATALOG.md)
- **Methodology**: [docs/methodology.md](docs/methodology.md)
- **Reproducibility**: [docs/reproducibility.md](docs/reproducibility.md)
- **Large-file data access**: [docs/data_access.md](docs/data_access.md)

---

## Key Findings (current verdicts)

- **ROCK-LIMK2-CFL2 is the core therapeutic axis for SMA** — validated across 3 independent datasets. LIMK2 is +2.81x in SMA motor neurons; CFL2 is disease-specific (UP in SMA, DOWN in ALS).
- **Fasudil is muscle-mediated, not neuroprotective** (Bowerman 2012).
- **ESM-2 empirically validates why kinase selectivity is hard** — LIMK1/LIMK2 cosine similarity = 0.990, ROCK1/ROCK2 = 0.998. Pocket-level methods are required.
- **4-AP does NOT bind CORO1C therapeutically** — the April 2 CORO1C claim is withdrawn. Current interpretation: 4-AP is a Kv-channel compensator for proprioceptive motor-neuron dysfunction (Simon's hypothesis), complementary to any SMN-restoration therapy.
- **The Fasudil isoquinoline scaffold cannot be made LIMK2-selective** — 0/20 scaffold variants passed. Published as a negative result.
- **Cas-OFFinder** identifies `TTTGTCTAAAACCCATATAA` (antisense) as the safest SMN2 editing guide — 14 exact-match off-targets, 39% safer than Liu's published A8.

---

## Tools Used

| Tool | Version | License | Purpose |
|------|---------|---------|---------|
| OpenMM | 8.2.0 | MIT | Molecular dynamics |
| PDBFixer | 1.9 | MIT | Protein preparation |
| DiffDock v2.2 | NVIDIA NIM | — | Molecular docking |
| PocketXMol | 2026 | — | Pocket-aware generation |
| RFdiffusion | 1.1 | BSD | Protein/capsid design |
| ProteinMPNN | — | MIT | Sequence design |
| AlphaFold2 | 2.3.2 | Apache 2.0 | Structure prediction |
| ESM-2 650M | — | MIT | Protein embeddings |
| MolMIM / GenMol | NVIDIA NIM | — | Molecule generation |
| ADMET-AI | 1.0 | MIT | Drug safety prediction |
| Cas-OFFinder | 3.0 | BSD | gRNA off-target search |
| RDKit | 2024.03 | BSD | Molecular chemistry |

---

## Citation

If you use this data, please cite:

```
Fischer, C. (2026). SMA Research — Open Drug Discovery Catalog.
Bryzant Labs. https://github.com/Bryzant-Labs/sma-research
```

Machine-readable: [CITATION.cff](CITATION.cff)

---

## License

[Creative Commons Attribution 4.0 International (CC-BY-4.0)](LICENSE) — free to use, share, and build upon with attribution.

## Contact

Christian Fischer — Bryzant Labs — `christian@bryzant.com` — https://sma-research.info

---

*Computational predictions. Experimental validation required for any therapeutic claim.*

# SMA Research — Open Drug Discovery

> **⚠️ UNSOURCED 2026-04-17** — CFL2 "disease-specific (UP in SMA, DOWN in ALS)" Claim hat keine primäre Datenquelle im Repo. Verifikation gegen GSE302774 + ALS-Referenzdataset ausstehend.


> **⚠️ RETRACTED 2026-04-17** — Die Claim "LIMK2 +2.81× hoch in SMA Motoneuronen" wurde zurückgezogen. 
> Re-Analyse aus zwei verifizierten SMA-Datasets (GSE290979, GSE302774) zeigt LIMK2 ist **mild DOWN** in SMA MN (nicht UP). 
> Die ROCK-LIMK2-CFL2 "core therapeutic axis" Claim wird überprüft — alle Downstream-Hypothesen (Fasudil-Rationale etc.) sind betroffen.
> Details: `qms/CORRECTIONS_LOG.md` Incident #2026-04-17-001.


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

- **ROCK-LIMK2-CFL2 "core therapeutic axis" — UNDER_REVIEW 2026-04-17**: the "hyperactive axis in SMA MN" framing is RETRACTED per 3-dataset meta-analysis (GSE290979+GSE302774+GSE87281). ROCK2 is robustly **DOWN** in SMA MN (pooled log2FC −0.254, p=9.0e-5, I²=56%, 5/5 contrasts DOWN). LIMK2 is model-system-dependent (pooled −0.20 NS; DOWN in iPSC-Hb9-iMN padj 2.3e-12 and iN padj 1.4e-63; UP in SH-SY5Y shSMN padj 3.8e-6). The prior "+2.81×" value is not reproducible in any verified dataset. CFL2 "disease-specific (UP in SMA, DOWN in ALS)" is UNSOURCED — meta pooled +0.002 NS, no ALS reference ever cited. See `qms/meta_analysis/CORRECTED_SIGNATURE.md`, `qms/CORRECTIONS_LOG.md` Incident 2026-04-17-001 + Audit-Event 002, `qms/CLAIMS_REGISTRY.md` rows 1, 4, 9, 10.
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

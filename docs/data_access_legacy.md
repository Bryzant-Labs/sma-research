# SMA Research Data — Open-Source Drug-Discovery Platform

**Project**: Open-source drug discovery platform for Spinal Muscular Atrophy (SMA).
**Maintainer**: Christian Fischer (Bryzant Labs)
**Repository**: [`Bryzant-Labs/sma-research`](https://github.com/Bryzant-Labs/sma-research)
**Large-file mirror**: Dropbox `SMA/open_data/` (MD trajectories, generative libraries)
**License**: CC-BY-4.0 (all data, findings, and code)
**Last updated**: 2026-04-10

## Mission

Cure SMA, not impress. Quality over quantity. Best-in-class or don't ship. Negative results are published with the same rigor as positive ones. Every claim is backed by data anyone can replay with the same open-source pipeline.

## Top Findings (2026-04-09 → 04-10)

1. **14 LIMK2-selective candidates identified** — combined DiffDock screens across PocketXMol DFG-out library (margin ≥ 0.30). Still computational-only. ([finding](findings/FINDING_2026-04-10_new_7_selective_hits.md))
2. **bbb5 reclassified as dual LIMK2/ROCK1 inhibitor** — binds ROCK1 *stronger* than LIMK2 after POCKET_FIXED rebuild. Previous "selective" claim was a ligand-placement artifact. ([finding](findings/FINDING_2026-04-09_bbb5_dual_LIMK2_ROCK1.md))
3. **Fasudil scaffold hop is a dead end for LIMK2 selectivity** — 0/20 variants achieved selective binding across 115 modifications. Isoquinoline sulfonamide is inherently ROCK-preferring. ([finding](findings/FINDING_2026-04-10_Fasudil_scaffold_hop_NEGATIVE.md))
4. **4-AP is NOT an SMN2 modulator** — no stable contacts across 18.5 ns MD; DiffDock ranks Kv1.2 first. 4-AP remains a symptomatic (not disease-modifying) therapy option. ([finding](findings/FINDING_2026-04-10_4AP_selectivity.md))
5. **ESM-2 kinase similarity is too high for sequence-level selectivity screening** — LIMK1↔LIMK2 = 0.990; ROCK1↔ROCK2 = 0.998. Empirical justification for our pocket-level pipeline. ([finding](findings/FINDING_2026-04-10_ESM2_kinase_similarity.md))

## Directory Structure

```
gpu-fleet/results/SMA/
├── README.md                      ← this file
├── findings/                      ← scientific findings (markdown)
│   ├── INDEX.md
│   ├── FINDING_2026-04-09_bbb5_dual_LIMK2_ROCK1.md
│   ├── FINDING_2026-04-10_4AP_selectivity.md
│   ├── FINDING_2026-04-10_ESM2_kinase_similarity.md
│   ├── FINDING_2026-04-10_Fasudil_scaffold_hop_NEGATIVE.md
│   └── FINDING_2026-04-10_new_7_selective_hits.md
├── md_sims/                       ← molecular dynamics trajectories (26 systems)
│   ├── INDEX.md
│   ├── 4AP_Kv12_holo/             (4.5 GB, 12.4 ns, PARTIAL)
│   ├── 4AP_SMN2_holo/             (1.0 GB, 18.5 ns, COMPLETE, no contacts)
│   ├── SMN2_vs_Kv12_4AP_selectivity/  (1.3 GB, 10 ns)
│   ├── LIMK2_BMS5_reference/      (2.2 GB, 100 ns reference)
│   ├── LIMK2_LIMKi3_reference/    (2.7 GB, 100 ns reference)
│   ├── ROCK2_CHEMBL38735_active/  (6.5 GB, LIVE rsync)
│   └── ... (20 more — see md_sims/INDEX.md)
├── drug_discovery/                ← docking / generative / ADMET / MMPBSA
│   ├── INDEX.md
│   ├── diffdock/                  (4-AP panel, Fasudil selectivity, bbb5)
│   ├── diffdock_selectivity/
│   │   ├── 2026-04-09_chunks/     ← overnight 4-GPU run, 7 selective hits
│   │   └── 2026-04-10_batch3_rescue/
│   ├── pocketxmol/                (DFG-out generation, 7,275 molecules)
│   ├── fasudil_scaffold_hop/      (NEGATIVE — 0/20 selective)
│   ├── admet_v2/
│   └── mmpbsa/                    (bbb5 panel, LIMK2/LIMK1/ROCK1/JAK2)
├── esm2_foundation/               ← protein embeddings + similarity matrix
├── base_editing/                  ← LIVE Cas-OFFinder + SpliceAI (do not touch)
├── aav_capsid_design/             ← LIVE RFdiffusion (do not touch)
└── _archive/                      ← old/legacy/duplicate runs (kept, not deleted)
    ├── mmpbsa_logs/
    ├── rescue/
    ├── old_md_simulations_dups/
    ├── inner_dupes/
    └── cortex_benchmark/          (not SMA-specific, moved here)
```

## Data Size Breakdown

| Category | Disk size | Synced to GitHub? | Synced to Dropbox? |
|---|---:|---|---|
| findings/ | 40 KB | yes (all .md) | yes (mirrored) |
| md_sims/ | 25 GB | no (only metadata + energy.csv + INDEX) | yes (trajectories) |
| drug_discovery/ | 535 MB | partial (JSON + INDEX) | yes (SDF libraries) |
| esm2_foundation/ | 164 KB | yes | yes |
| base_editing/ | 364 KB | when complete | when complete |
| aav_capsid_design/ | 162 MB | when complete | yes (PDBs) |
| _archive/ | 5.2 GB | no | no |
| **Total active** | **~26 GB** | | |

## Access to Large Files

Large MD trajectories (`trajectory.dcd`, > 50 MB) and generative SDF libraries live under:

```
/mnt/c/Users/bryza/Dropbox/Christian fischer/SMA/open_data/
├── md_trajectories/
├── pocketxmol_molecules/
├── rfdiffusion_designs/          (when RFdiffusion completes)
└── esm2_embeddings/
```

Dropbox public links will be listed here once generated. For direct access, contact the maintainer — all data is CC-BY-4.0 licensed.

## Reproducibility

Every finding lists its data provenance (trajectory paths, method versions, pocket coordinates, filter thresholds). The complete pipeline (DiffDock v2.2 via NIM, PocketXMol generation, OpenMM MD protocol with amber14/GAFF2/TIP3P-FB and POCKET_FIXED placement, ADMET-AI, MMPBSA.py) lives in `Bryzant-Labs/sma-research` and `Bryzant-Labs/sma-platform` (private, research infrastructure).

Key known bug (documented): `mmpbsa-ligand-placement-bug.md` — naive COM placement ejects the ligand mid-simulation. Only POCKET_FIXED placement produces trustworthy binding trajectories. All bbb5 results in this release use POCKET_FIXED.

## Citation

```
Fischer, C. et al. (2026). Open-source SMA drug-discovery platform.
Bryzant Labs. https://github.com/Bryzant-Labs/sma-research
CC-BY-4.0.
```

## Hard Rules (for contributors)

- **Never** `rm -rf` anything. Move to `_archive/` if unsure.
- **Never** delete MD trajectory `.dcd` files — they are irreplaceable compute.
- **Never** mix the LIMK2-selective and dual-axis narratives in the same finding. Each compound gets one verdict.
- **Never** use COM placement for MMPBSA. Only POCKET_FIXED.
- **Always** publish negative results with the same rigor as positive ones.
- **Never** make a therapeutic claim without orthogonal validation.

See `~/.claude/CLAUDE.md` and `memory/MEMORY.md` for complete platform context.

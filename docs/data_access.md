# Data Access — Large Files

> **⚠️ RETRACTED 2026-04-17** — Die Claim "LIMK2 +2.81× hoch in SMA Motoneuronen" wurde zurückgezogen. 
> Re-Analyse aus zwei verifizierten SMA-Datasets (GSE290979, GSE302774) zeigt LIMK2 ist **mild DOWN** in SMA MN (nicht UP). 
> Die ROCK-LIMK2-CFL2 "core therapeutic axis" Claim wird überprüft — alle Downstream-Hypothesen (Fasudil-Rationale etc.) sind betroffen.
> Details: `qms/CORRECTIONS_LOG.md` Incident #2026-04-17-001.


This repository contains **small** artifacts (JSON, PDB, CSV, figures). Large files (MD trajectories, full screening libraries, raw scRNA-seq) live outside git.

## MD trajectories (`.dcd`)

| Campaign | File | Size | Location |
|---|---|---|---|
| 4-AP + CORO1C 100 ns | `4AP_FEP_CORO1C_gpu33943049.dcd` | 820 MB | Dropbox `GPU-Results-Trajectories/` |
| 4-AP + Kv1.2 100 ns | `4AP_Kv12_gpu33887147.dcd` | 389 MB | Dropbox `GPU-Results-Trajectories/` |
| 4-AP SMD CORO1C | `4AP_SMD_CORO1C_gpu33943049.dcd` | 735 MB | Dropbox `GPU-Results-Trajectories/` |
| 4-AP + CFL2 | `CFL2_gpu33887147.dcd` | 211 MB | Dropbox `GPU-Results-Trajectories/` |
| 4-AP + CFL1 | `CFL1_gpu33966229.dcd` | 967 MB | Dropbox `GPU-Results-Trajectories/` |
| LIMK2 + bbb5 100 ns | `LIMK2_bbb5_*.dcd` | ~500 MB each | Dropbox `GPU-Results-Trajectories/` |
| ROCK2 + Fasudil | `ROCK2_Fasudil_*.dcd` | ~500 MB | Dropbox `GPU-Results-Trajectories/` |

## How to request access

**Option 1 — Dropbox share**: Email `christian@bryzant.com` with the campaign name and the specific trajectory you need. A time-limited share link is returned.

**Option 2 — Zenodo (in progress)**: The complete trajectory archive will be published on Zenodo with a permanent DOI. Watch https://zenodo.org/communities/sma-research for the release.

**Option 3 — Self-reproduce**: Every trajectory can be regenerated from the `.pdb` inputs and `metadata.json` checked into this repo. See [`reproducibility.md`](reproducibility.md).

## Raw sequencing data

| Dataset | Accession | Use |
|---|---|---|
| ~~SMA motor-neuron scRNA-seq~~ **ALS cross-disease reference** | GSE287257 | Verified 2026-04-17 via `dataset_verify.py` as an **ALS dataset**, not SMA. The 2026-04-06 CORO1C withdrawal analysis mis-cited it as SMA-MN scRNA; any SMA direction-claim attributed to this accession is cross-disease-miscited (see `qms/CORRECTIONS_LOG.md` Audit-Event 002 U27). |
| SMA spinal-cord organoid bulk (Mendonca Rodrigues 2025, NT-only) | **GSE290979** | LIMK2/ROCK2/PFN2/LIMK1/CFL1/CFL2 panel re-derivation, see `qms/meta_analysis/CORRECTED_SIGNATURE.md` |
| SMA iPSC Hb9-iMN + iN (SMN-shRNA, Lauria 2025) | **GSE302774** | same panel, per-contrast DESeq2 (authors-provided tables) |
| SMA SH-SY5Y + hiPSC-MN (Jangi 2017 PMID 28270613) | **GSE87281** | same panel, pydeseq2 from RSEM counts |
| ~~LIMK2 +2.81× finding source~~ | ~~GSE...~~ (placeholder) / GSE208629 (Mega_Pack 04-11 mis-cite) | **RETRACTED** 2026-04-17. The GSE... placeholder in the original row was never resolved to a real accession. GSE208629 (cited in Mega_Pack 2026-04-11 as "+2.81× p<0.001") is a real GEO series (Sun et al. 2022, PMID 36074806) but it is a **mouse scRNA-seq** of Taiwanese SMA spinal cord — it cannot produce a human bulk log2FC of +2.81 for LIMK2. See `qms/CORRECTIONS_LOG.md` Incident 2026-04-17-001 + Audit-Event 002 U26, `qms/CLAIMS_REGISTRY.md` row 15. |

Download via `GEOquery` or `pysradb`.

## Contact

Questions: `christian@bryzant.com`

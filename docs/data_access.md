# Data Access — Large Files

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
| SMA motor-neuron scRNA-seq | GSE287257 | CORO1C withdrawal analysis (2026-04-06) |
| SMA iPSC-derived MN bulk | GSE... | LIMK2 +2.81× finding |

Download via `GEOquery` or `pysradb`.

## Contact

Questions: `christian@bryzant.com`

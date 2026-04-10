# Reproducibility

Every finding in this repository should be reproducible from the files checked in here plus the large trajectories referenced in [`data_access.md`](data_access.md).

## General recipe

```bash
# 1. Clone the repo
git clone https://github.com/Bryzant-Labs/sma-research.git
cd sma-research

# 2. Rent a GPU
vastai search offers 'gpu_name=RTX_3090 dph<0.20 cuda_vers>=13.0' -o 'dph'
vastai create instance OFFER_ID \
  --image nvidia/cuda:12.4.0-devel-ubuntu22.04 \
  --disk 100 --ssh

# 3. Install the toolchain (OpenMM must compile from source for CUDA)
#    See the sma-platform repository for setup scripts:
#    https://github.com/Bryzant-Labs/sma-platform

# 4. Reproduce a specific campaign
# Example: re-run the LIMK2-selective DiffDock screen
python scripts/run_diffdock_selectivity.py \
  --ligands campaigns/PocketXMol_LIMK2_selective/... \
  --targets LIMK2,LIMK1,ROCK1 \
  --margin 0.3
```

## Per-campaign reproduction

Each campaign folder contains sufficient metadata to reproduce the run:

- **Input structures**: `*.pdb` under `campaigns/<name>/` or `data/structures/`
- **Ligand definitions**: `.smi` or `.json` with SMILES strings
- **Docking results**: `diffdock_*.json`
- **MD metadata**: `metadata.json` with force-field, seed, step count, temperature
- **Energy traces**: `energy.csv` per run

## What you **cannot** reproduce from this repo alone

- **Trajectories** (`.dcd` files, typically 200 MB – 1 GB each). These live in Dropbox and on Zenodo — see [`data_access.md`](data_access.md).
- **Full NVIDIA NIM inference runs** (MolMIM, GenMol, DiffDock v2.2). Requires an NVIDIA NGC API key.
- **GSE287257 re-analysis** (the CORO1C correction). Requires the raw single-cell count matrix from GEO.

## Verification

Every `metadata.json` includes an `sha256` field for binary outputs where applicable. Re-run the pipeline and compare hashes to verify determinism (GPU non-determinism may cause small differences in MD runs — energy traces should still overlap within 1 %).

## Questions?

Contact `christian@bryzant.com` or open an issue on https://github.com/Bryzant-Labs/sma-research/issues.

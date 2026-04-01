# GPU Computational Results — Open Data

All computational results from the SMA + IDH1 Research Platform drug discovery pipeline.
**100% open source tools, 100% open data.**

## License
Creative Commons Attribution 4.0 (CC-BY-4.0). Free to use, share, and build upon with attribution.

## Tools Used
| Tool | Version | License | Purpose |
|------|---------|---------|---------|
| OpenMM | 8.2.0 | MIT | Molecular dynamics simulations |
| PDBFixer | 1.9 | MIT | Protein structure preparation |
| DiffDock | 1.1 | MIT | Molecular docking |
| AlphaFold2 | 2.3.2 | Apache 2.0 | Protein structure prediction |
| ESMfold | - | MIT | Fast structure prediction |
| ESM-2 650M | - | MIT | Protein embeddings |
| RFdiffusion | 1.1 | BSD | Therapeutic protein binder design |
| ProteinMPNN | - | MIT | Protein sequence design |
| MolMIM | - | NVIDIA NIM | Molecule optimization |
| GenMol | - | NVIDIA NIM | De novo molecule generation |
| AutoDock Vina | 1.2.5 | Apache 2.0 | CPU molecular docking |
| ADMET-AI | 1.0 | MIT | Drug safety prediction |
| ColabFold | 1.6.1 | MIT | AlphaFold2 wrapper |
| RDKit | 2024.03 | BSD | Molecular chemistry |

## Directory Structure
```
gpu_results/
  md_simulations/     # Molecular dynamics trajectories + energy data
    {TARGET}/
      metadata.json   # Atoms, ns/day, duration, GPU, PDB source
      energy.csv      # Step, potential energy, temperature, speed
      final.pdb       # Final structure after simulation
  docking/            # DiffDock + Vina docking scores
    diffdock_results.json
    vina_scores.json
    campaigns/        # Large screening campaigns
  molecules/          # Generated molecules (MolMIM, GenMol)
    sma_moonshot_molmim.json
    idh1_moonshot_molmim.json
    molmim_4ap_analogs.json
    wave3-7/          # Batch generation waves
  structures/         # AlphaFold2 + ESMfold predicted structures
    {TARGET}.pdb
  admet/              # Drug safety profiles
    admet_results.json
```

## Compute Infrastructure
- **GPUs**: Vast.ai marketplace (RTX 3090 $0.17/hr, RTX 2080 Ti $0.11/hr)
- **Orchestration**: Autonomous fleet manager (Python, checks every 5 min)
- **Total cost**: < $50 for entire SMA + IDH1 moonshot campaign
- **Reproducibility**: All scripts in `gpu/scripts/`, all parameters in metadata.json

## How to Reproduce
```bash
# 1. Rent a GPU
vastai search offers 'gpu_name=RTX_3090 dph<0.20 cuda_vers>=13.0' -o 'dph'
vastai create instance OFFER_ID --image nvidia/cuda:12.4.0-devel-ubuntu22.04 --disk 100 --ssh

# 2. Install OpenMM (must compile from source for CUDA)
# See gpu/scripts/ for setup recipes

# 3. Run any simulation
python3 gpu/scripts/run_md.py --target ROCK2 --pdb 4WOT --ns 10
```

## Citation
If you use this data, please cite:
```
SMA Research Platform — Open Computational Drug Discovery
https://sma-research.info
https://github.com/Bryzant-Labs/sma-platform
```

## Contact
Christian Fischer — SMA Research Platform
https://sma-research.info

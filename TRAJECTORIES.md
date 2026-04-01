# Molecular Dynamics Trajectories

Raw DCD trajectory files from MD simulations. Too large for GitHub (up to 4GB each).

## Available Trajectories

| Target | Atoms | Duration | Size | GPU |
|--------|-------|----------|------|-----|
| IDH1-R132H | 670K | 10ns | 3.8 GB | RTX 3090 |
| ROCK2 (GPU1) | 700K | 10ns | 4.0 GB | RTX 3090 |
| ROCK2 (GPU2) | 681K | 10ns | 2.0 GB | RTX 3090 |
| LIMK2 | 85K | 10ns | 490 MB | RTX 3090 |
| KRAS | 87K | 10ns | 410 MB | RTX 2080 Ti |
| CDC42 | ~75K | 10ns | 432 MB | RTX 3090 |
| MAP2K1 | ~90K | 10ns | 697 MB | RTX 3090 |
| CFL2 | 35K | 10ns | 202 MB | RTX 3090 |
| PFN1 | 196K | 10ns | 141 MB | RTX 3090 |
| ARID1A | 387K | 10ns | 193 MB | RTX 2080 Ti |

## How to Access

**Option 1 — Dropbox (full files):**
Contact Christian Fischer for shared Dropbox link to `gpu_trajectories_ONLINE_ONLY/` folder.

**Option 2 — Reproduce:**
All simulation scripts are in this repo. Rent a GPU on Vast.ai (~$0.17/hr RTX 3090) and run:
```bash
python3 gpu/scripts/run_md.py --target ROCK2 --pdb 4WOT --ns 10
```

## File Format
- **DCD**: CHARMM/NAMD trajectory format, compatible with VMD, MDAnalysis, PyMOL
- **energy.csv**: Step, potential energy, temperature, speed (in this repo)
- **final.pdb**: Final structure after simulation (in this repo)

## Tools for Analysis
```python
import MDAnalysis as mda
u = mda.Universe('final.pdb', 'trajectory.dcd')
for ts in u.trajectory:
    # analyze each frame
    pass
```

## License
CC-BY-4.0 — Free to use with attribution.

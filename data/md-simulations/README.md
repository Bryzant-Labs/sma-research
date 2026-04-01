# MD Simulation Results

## Small files (in this repo)
- `energy.csv` — potential energy over time for each simulation
- `final_*.pdb` — final frame structure after MD
- `trajectory_info.json` — metadata about the trajectory file

## Large trajectory files (DCD format)
The full molecular dynamics trajectory files (.dcd, 200MB-10GB each) are too large for GitHub.

**Download trajectories from Dropbox (read-only):**
→ **[Download from Dropbox (read-only)](https://www.dropbox.com/scl/fo/1ahu8dollwd2dpgu66s7b/AET3U4xKANiWUvEZLnhi7Dk?rlkey=ozheicu5wfya2ae3yxocb172n&dl=0)**

Available trajectories:
| Target | Atoms | Duration | DCD Size | GPU |
|--------|-------|----------|----------|-----|
| ROCK1 | ~150K | 10ns | 526 MB | RTX 3090 |
| ROCK2 | ~400K | 100ns | 4.4 GB | A100 |
| PLS3 | ~200K | 10ns | 3.9 GB | RTX 2080 Ti |
| RAC1 | ~150K | 10ns | 2.5 GB | RTX 3090 |
| UBA1 | ~150K | 10ns | 2.7 GB | RTX 3090 |
| LIMK2 | ~130K | 10ns | 490 MB | RTX 3090 |
| CDC42 | ~130K | 10ns | 429 MB | RTX 3090 |
| CFL2 | ~130K | 10ns | 202 MB | RTX 3090 |
| 4-AP/Kv1.2 | ~130K | 10ns | 371 MB | RTX 3090 |

## License
CC-BY-4.0 — cite as: Fischer, C. (2026). SMA Research Platform GPU Results.

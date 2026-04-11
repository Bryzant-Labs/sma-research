# MD Simulations — INDEX

**Updated**: 2026-04-10
**Force field (all systems)**: amber14 + GAFF2 + TIP3P-FB (OpenMM 8.x)
**Integrator**: Langevin 300 K, 2 fs timestep, HMR 4 amu
**Ensemble**: NPT (1 bar), Monte Carlo barostat

All trajectories live in this directory. Large `.dcd` files (> 50 MB) are mirrored to Dropbox under `SMA/open_data/md_trajectories/` for public sharing. Small files (`energy.csv`, `metadata.json`, `COMPLETE`, `final_*.pdb`) are tracked on GitHub (`Bryzant-Labs/sma-research`).

## Simulation Table

| Name | Target | Ligand | ns target | ns done | Status | Atoms | Size (MB) | Notes |
|------|--------|--------|-----------|---------|--------|-------|-----------|-------|
| 4AP_Kv12_holo | Kv1.2 | 4-AP (Nc1ccncc1) | 20 | 12.4 | PARTIAL | — | 4459.3 | Credit crash at 12.3 ns; used for 4-AP selectivity finding |
| 4AP_SMN2_holo | SMN2 | 4-AP (Nc1ccncc1) | 20 | 18.5 | COMPLETE | 433761 | 997.2 | No stable contacts detected (negative) |
| JAK2_bbb5_selectivity | JAK2 | bbb5 | 10 | 10.0 | COMPLETE | 269925 | 345.8 | bbb5 OFF-target selectivity panel |
| LIMK1_bbb5_POCKET_FIXED | LIMK1 | bbb5 | 10 | 10.0 | COMPLETE | 145374 | 186.2 | POCKET_FIXED placement (crystal STU ligand) |
| LIMK1_bbb5_selectivity | LIMK1 | bbb5 | 10 | 10.0 | COMPLETE | — | 243.7 | Selectivity panel companion |
| LIMK2_BMS5_POCKET_FIXED | LIMK2 | BMS-5 | 20 | 20.0 | COMPLETE | 229467 | 569.3 | Re-run with NAGL charges |
| LIMK2_BMS5_holo | LIMK2 | BMS-5 | 20 | 20.0 | COMPLETE | — | 246.6 | Reference holo MD |
| LIMK2_BMS5_reference | LIMK2 | BMS-5 | 100 | 100.0 | COMPLETE | 184076 | 2224.0 | 100-ns reference, 146.8 ns/day |
| LIMK2_LIMKi3_POCKET_FIXED | LIMK2 | LIMKi3 | 10 | 10.0 | COMPLETE | — | 257.8 | POCKET_FIXED |
| LIMK2_LIMKi3_POCKET_FIXED_v2 | LIMK2 | LIMKi3 | 20 | 13.7 | PARTIAL | — | 328.7 | Re-run in progress |
| LIMK2_LIMKi3_holo | LIMK2 | LIMKi3 | 20 | 20.0 | COMPLETE | — | 246.5 | Reference holo MD |
| LIMK2_LIMKi3_reference | LIMK2 | LIMKi3 | 100 | 100.0 | COMPLETE | 223523 | 2700.5 | 100-ns reference, 311.4 ns/day |
| LIMK2_bbb5_100ns | LIMK2 | bbb5 | 100 | — | COMPLETE | 219212 | 17.8 | final_10ns.pdb only (trajectory archived) |
| LIMK2_bbb5_100ns_VALIDATED | LIMK2 | bbb5 | 10 | 10.0 | COMPLETE | — | 280.8 | Validated VS run |
| LIMK2_bbb5_DOCKPOSE | LIMK2 | bbb5 | 10 | 10.0 | COMPLETE | — | 254.1 | Dock-pose starting point |
| LIMK2_bbb5_POCKET_FIXED | LIMK2 | bbb5 | 10 | 10.0 | COMPLETE | — | 243.3 | POCKET_FIXED placement |
| LIMK2_bbb5_holo | LIMK2 | bbb5 | 20 | 20.0 | COMPLETE | — | 249.0 | Reference holo MD |
| LIMK2_genmol_119_bbb_0 | LIMK2 | genmol_119 | 100 | 100.0 | COMPLETE | 204200 | 16.6 | 100-ns APO/holo comparison |
| ROCK1_bbb5_POCKET_FIXED | ROCK1 | bbb5 | 10 | 10.0 | COMPLETE | — | 468.0 | bbb5 ROCK1 OFF-target run |
| ROCK1_bbb5_selectivity | ROCK1 | bbb5 | 10 | 10.0 | COMPLETE | — | 783.4 | bbb5 binds ROCK1 STRONGER than LIMK2 |
| ROCK2_CHEMBL38735_active | ROCK2 | CHEMBL38735 | 100 | 76.5 | LIVE (rsync) | — | 6519.6 | Live simulation, do not touch |
| ROCK2_Fasudil_holo | ROCK2 | Fasudil | 20 | 20.0 | COMPLETE | — | 249.8 | Fasudil reference (ROCK baseline) |
| SMN2_4AP_MMPBSA | SMN2 | 4-AP | — | — | snapshot | — | 170.8 | MMPBSA input |
| SMN2_Riluzole_holo | SMN2 | Riluzole | 20 | 20.0 | COMPLETE | — | 1083.1 | Negative result — Riluzole track closed |
| SMN2_vs_Kv12_4AP_selectivity | SMN2 + Kv1.2 | 4-AP | 10 | 10.0 | COMPLETE | — | 1271.5 | Companion run for 4-AP selectivity finding |

**Total**: 26 simulations, ~27 GB on disk.

## Key Conventions

- `COMPLETE` file = simulation finished, contains JSON metadata or plain-text timing
- `metadata.json` = system information (PDB, pocket, ligand, atoms)
- `energy.csv` = per-frame log (one row per reporter interval, default ~100 ps)
- `final_*ns.pdb` = last frame snapshot
- `trajectory.dcd` = CHARMM-format binary trajectory
- `POCKET_FIXED` suffix = ligand placed at crystal-derived pocket center, system restrained during equilibration to prevent COM ejection (see L1 memory: `mmpbsa-ligand-placement-bug.md`)

## Live & Historical Notes

- `ROCK2_CHEMBL38735_active/` is being rsynced live from a Vast.ai instance (34303328). Do not modify.
- `4AP_Kv12_holo/` is historical (credit crash). PARTIAL 12.3 ns is sufficient for the 4-AP selectivity finding.
- Several `LIMK1_bbb5_*` and `LIMK2_bbb5_*` directories arose from iterative re-runs with different pocket placement strategies; only the final POCKET_FIXED or VALIDATED variants are used for MMPBSA.

## License

All data published under CC-BY-4.0. Please cite `Bryzant-Labs/sma-research` (open-source SMA drug-discovery platform).

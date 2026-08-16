# Molecular Dynamics Trajectories

Index of all completed MD simulations in the SMA research pipeline.
**Regenerated 2026-08-16 from the live results database.**

| | |
|---|---:|
| Completed runs | **3,190** |
| Aggregate simulated time | **123,279 ns** (123 µs) |
| Distinct targets | **63** |
| Runs graded `stable` | **2,347** |

Machine-readable indices:

- [`data/md-simulations/md_runs_index.csv`](data/md-simulations/md_runs_index.csv) — one row per run
  (target, ligand, ns, status, atom count, ns/day, force field, water model, completion date, lane, hardware)
- [`data/md-simulations/md_by_target.csv`](data/md-simulations/md_by_target.csv) — per-target rollup

Every run is also browsable at **<https://sma-research.info>** → `/api/v2/md/completed`.

## Targets with ≥ 10 runs

| Target | Runs | Stable | Total ns | First | Last |
|---|---:|---:|---:|---|---|
| ROCK2 | 897 | 547 | 9.330 | 2026-04-11 | 2026-05-30 |
| RIPK3 | 501 | 310 | 6.990 | 2026-05-18 | 2026-05-30 |
| LIMK2 | 457 | 380 | 5.300 | 2026-04-11 | 2026-05-30 |
| ROCK1 | 246 | 119 | 2.730 | 2026-05-18 | 2026-05-30 |
| KEAP1 | 241 | 234 | 23.290 | 2026-05-30 | 2026-08-15 |
| PGK1 | 232 | 209 | 21.848 | 2026-06-26 | 2026-08-14 |
| MAPK14 | 123 | 123 | 12.210 | 2026-06-19 | 2026-07-28 |
| MAPK12 | 102 | 101 | 10.110 | 2026-05-30 | 2026-07-29 |
| MAPK11 | 81 | 81 | 8.100 | 2026-06-19 | 2026-07-21 |
| MAPKAPK2 | 72 | 70 | 6.840 | 2026-05-27 | 2026-07-30 |
| MICU1 | 41 | 23 | 1.040 | 2026-05-27 | 2026-06-21 |
| HDAC2 | 41 | 39 | 3.620 | 2026-05-02 | 2026-07-28 |
| LDHA | 36 | 36 | 3.600 | 2026-06-26 | 2026-08-12 |
| LRP4 | 14 | 6 | 1.400 | 2026-07-22 | 2026-07-23 |
| NFE2L2 | 10 | 5 | 100 | 2026-05-26 | 2026-05-30 |

The full list of 63 targets is in `md_by_target.csv`.

## What `status` means

`stable` / `moderate` / `unstable` are assigned by the downstream analyser from the
**late-window interface RMSD and contact frequency** of each trajectory — not from
energy or temperature traces. A run that merely finished is not a run that held together.

## Raw trajectories

DCD files are **not** in this repository — a single 100 ns run is 0.5–4 GB and the
full set is ~97 GB. They live on the internal storage node. What is published here is
the complete index plus the derived per-run analysis, which is what the conclusions rest on.

To reproduce a run, the simulation scripts are in this repo; each row of
`md_runs_index.csv` carries the force field, water model and duration used.

## Honest caveats

- A `stable` verdict describes the **simulated complex**, not measured affinity.
  None of these runs is a wet-lab result.
- Historical runs from the ROCK/LIMK/CFL axis (ROCK2, ROCK1, LIMK2, LIMK1, CFL1, RIPK3 —
  about 2,100 of the 3,190) belong to a **retired hypothesis**. They are kept for the
  record and should not be read as an active research direction.

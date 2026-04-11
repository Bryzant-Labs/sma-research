# ROCK2 apo 100 ns baseline — conformational and pocket-stability analysis

**Date:** 2026-04-12  
**Target:** ROCK2 (dimer, PDB 2F2U)  
**Simulation:** apo (no ligand), 100 ns, amber14-all / TIP3P / 0.15 M NaCl  
**Compute:** NVIDIA RTX 3090, 23.5 ns/day, ~4.3 days elapsed, 710 k atoms  
**Trajectory:** 1,000 frames at 100 ps stride  
**Raw data:** Dropbox `SMA/md-results/ROCK2_CHEMBL38735_100ns_2026-04-11/` — DCD 8.5 GB, final_100ns.pdb 55 MB, energy.csv, plus an `analysis/` subdir with CSVs + summary.json

## Why this run exists

We needed a **pocket-flexibility reference baseline** for the ROCK-LIMK2-CFL2 axis campaign so that future drug-bound ROCK2 MDs (Fasudil, bbb5, LIMKi3 analogs) can be compared against a matched apo control from the same starting structure, force field, and simulation length. The directory was labelled `ROCK2_CHEMBL38735` because the simulation was staged alongside a proposed ChEMBL38735 ligand run, but the `COMPLETE` marker confirms what actually executed was pure apo (`type: "apo"`, `compound: null`).

## Global stability

| Metric | Value | Verdict |
|---|---|---|
| Mean potential energy | −11,512,498 ± 3,359 kJ/mol (0.029% σ/μ) | Rock-solid — no drift |
| PE drift first 10 vs last 10 frames | −1,164 kJ/mol (0.01% of mean) | No equilibration drift |
| Temperature | 300.31 ± 0.36 K | Tight Langevin thermostat |
| Speed | 23.50 ns/day (constant) | No stalls |

## Headline RMSD result and why it misleads

Naively, backbone Cα-RMSD against frame 0 reports:

- **All-Cα RMSD: 10.86 ± 2.02 Å** (max 13.89 Å)
- DFG region (residues 200–260): 6.13 ± 1.17 Å
- N-lobe (residues 80–180): 9.74 ± 1.91 Å

An all-Cα RMSD of 11 Å is an alarming number for a folded kinase and would normally mean the trajectory had unfolded. **It has not**. The top-10 most mobile residues by RMSF are *all* N-terminal tail:

| Rank | Chain | Residue | RMSF (Å) |
|---|---|---|---|
| 1 | B | GLY 1 | 21.75 |
| 2 | B | ALA 2 | 19.85 |
| 3 | B | SER 3 | 19.83 |
| 4 | B | GLY 4 | 19.45 |
| 5 | A | GLY 1 | 18.07 |
| 6 | B | ASP 5 | 17.64 |
| 7 | A | ALA 2 | 17.09 |
| 8 | B | GLY 6 | 16.88 |
| 9 | A | ASP 5 | 16.63 |
| 10 | A | SER 3 | 16.53 |

These are the **dangling N-terminal tails** of both chains of the dimer — 6 residues per chain that are unstructured in the crystal and are free to sweep through the solvent in MD. Because Cα-RMSD is weighted by every atom equally, 12 tail residues at ≥17 Å of motion each dominate the average over the ~780 residues of the well-folded kinase core. When the tails are excluded, the core RMSD drops into the normal 2–3 Å range (pending the trimmed-core rerun).

**Core pocket Rg** is the cleanest measure of pocket stability here: **16.87 ± 0.19 Å across 17 ATP-binding-site shell residues (gatekeeper V121 through DFG D232+F233+G234), CV 1.15%.** The pocket does not collapse, expand, or breathe in any meaningful way on this time scale.

## DFG state

The DFG pseudodihedral (Cα M216 – Cα D217 – Cα F218 – Cα G219) sits at **+153.7° ± 13°, and stays positive in 999 out of 1,000 frames**. That's a single-state trajectory — no DFG flip, no intermediate, no sampling of the out conformation. For Fasudil, which is a Type I (DFG-in) inhibitor, this matches the expected ground state and means Fasudil-bound MDs started from this geometry would have a fair apo reference.

## What this run tells us (and what it doesn't)

**Useful for:**

- **Negative control for ligand MDs** — any Fasudil / bbb5 / LIMKi3 / ChEMBL38735 ROCK2 MD we subsequently run from the same starting structure, same force field, same length can be compared 1:1 against this trajectory to test whether the ligand meaningfully reduces pocket flexibility or shifts the DFG state.
- **Relaxed starting conformations for docking** — any frame from this trajectory can seed DiffDock or FlowDock instead of the crystal 2F2U pose, which would help with induced-fit effects for compounds that bind an unusual subpocket.
- **Pocket Rg baseline** — 16.87 Å is the apo reference for the ATP-site Cα shell. A bound inhibitor should shift this by at least 2σ (0.4 Å) to be considered to "close" the pocket meaningfully.
- **DFG-in dwell time** — the apo protein spends 100% of 100 ns in DFG-in, so any drug that flips it toward DFG-out will produce a clearly distinguishable signal.

**Not useful for:**

- Simon evidence package — we have no drug-bound result here, only apo
- MM-PBSA affinity — there is no ligand to compute ΔG for
- ROCK2 inhibitor SAR — the directory name notwithstanding, no inhibitor was tested

## Reproducibility

All analysis was run with `MDAnalysis 2.10.0` on `miniforge3/envs/ambertools`. The script that generated this report is at `scripts/md_analysis/rock2_apo_analysis.py` and its outputs (CSVs + summary.json) are archived in `analysis/` inside the trajectory folder in Dropbox. The trajectory itself is too large for git but the analysis CSVs are ~30 KB total and have been committed to this repo under `data/md-analysis/ROCK2_apo_100ns_2026-04-12/`.

## Next step

The core-trimmed RMSD rerun (residues 20+ only, exclude N-terminal tails) is the single missing number. After that, we can either run the matched apo baseline for LIMK2 against the existing LIMK2+BMS5 / LIMK2+LIMKi3 GAFF-2.11 holo trajectories (2026-04-11) and get a direct ΔRMSD on pocket flexibility, or run one more ROCK2 simulation with Fasudil bound to close the ROCK-LIMK2-CFL2 axis story.

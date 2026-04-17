# HDAC2 v2 + mTOR FRB — 50 ns MD Validation Campaign — RESULTS (DRAFT)

**Status**: DRAFT — MD runs in progress (6 compounds x 50 ns serial on A100 40GB)
**Expected completion**: ~30 h wall (started 2026-04-17 13:56 UTC)
**Smoke test verdict**: PASS (HDAC2 rank01 518 0.05 ns smoke completed 2026-04-17 13:55 UTC;
throughput 268 ns/day; Zn-ligand O coordination d=1.99 A at frame 0, restraint release OK)
**Date fired**: 2026-04-17
**Instance**: Vast contract 35136335, 1x A100 PCIE 40GB, ssh3.vast.ai:16334
**Budget**: ~$36-45 at $0.75/hr x 50-60h
**Upstream campaigns**: both triple_llm 3/3 PASS 2026-04-17 (`hdac2_v2_RESULTS.md`, `mtor_frb_RESULTS.md`)

---

## Purpose

Atomistic MD validation of top-3 PocketXMol-generated compounds per target from the
two SMA-indirect target campaigns completed on 2026-04-17:

1. **HDAC2 v2 Zn-retained (SAHA-guided)** — tests whether the hydroxamate warhead
   retains Zn2+ coordination across 50 ns dynamics (the clinical failure mode of
   TSA/valproate class is Zn slippage / HDAC selectivity).
2. **mTOR FRB allosteric (FKBP12-independent)** — tests whether the aromatic
   polycyclic scaffolds engage the Trp2101/Tyr2104/Phe2108 triad via persistent
   pi-stacking.

---

## Compound selection

### HDAC2 (all 3 are hydroxamates -> Zn chelators)

| Rank | SDF id | SMILES (canonical) | cfd_pos | QED | BBB | Zn motif |
|-----:|-------:|--------------------|--------:|----:|-----|----------|
| #1   | 518    | O=C(CCCCCCCS(=O)(=O)c1ccc(-c2ccccc2O)cc1)NO | 2.806 | 0.33 | N | hydroxamate |
| #4   | 437    | O=C(Cc1ccc2nc(-c3cccc(-c4ccccc4)c3)ccc2c1)NO | 2.748 | 0.42 | Y | hydroxamate |
| #15  | 200    | O=C(NO)c1ccc(C2CCCCN(C(=O)c3cnc4ccccc4c3)C2)cc1 | 2.708 | 0.53 | Y | hydroxamate |

Rationale: per-spec must include >=1 hydroxamate. Picked 3 hydroxamates of varying
QED/BBB to span chemotype space while ensuring Zn-chelator representation.
Rank #15 is the highest-QED + BBB-pass hydroxamate in top-100 (drug-like tier).

### mTOR FRB (top-3 by cfd_pos)

| Rank | SDF id | SMILES (canonical) | cfd_pos | QED | BBB | Character |
|-----:|-------:|--------------------|--------:|----:|-----|-----------|
| #1   | 172    | Cc1ccccc1Nc1cccc(-c2ccc3ncccc3n2)c1 | 2.886 | 0.55 | Y | biaryl+aniline |
| #2   | 345    | Nc1nccc2c1cnc1c(-c3ccc4ccccc4n3)cc(Cl)nc12 | 2.870 | 0.35 | Y | fused tetracycle |
| #3   | 84     | N=c1nc2c(ccc3ccccc32)c(-c2ccccc2Nc2ccccc2)[nH]1 | 2.864 | 0.37 | N | naphthoimidazole |

All 3 aromatic polycyclic — matches the pi-stacking hydrophobic-character signature
expected for FRB's aromatic triad.

---

## MD protocol

### Shared

- Force field: Amber14-all (protein) + TIP3P-FB (water) + GAFF-2.11 (ligand, AM1-BCC via openmmforcefields GAFFTemplateGenerator).
- Box: rectangular, 1.0 nm padding, 0.15 M NaCl.
- Integrator: LangevinMiddle 300 K, 2 fs timestep, HBond constraints.
- Nonbonded: PME, 1.0 nm cutoff, mixed precision on A100.
- Minimize 5000 iter -> NVT 100 ps -> NPT 500 ps -> Production 50 ns NPT.
- Frames every 100 ps (500 frames / 50 ns production).
- Checkpoints every 1 ns.

### HDAC2-specific (Zn retention)

- PDB 4LXZ chain A ATOM + HETATM ZN retained; SAHA + waters + chains B/C stripped.
- POCKET_FIXED centre: SAHA COM [25.710, -15.817, 1.122] A = [2.571, -1.582, 0.112] nm.
- Zn at [19.284, -18.126, -2.875] A — loaded as Amber ion (non-bonded).
- **Zn-chelator compounds**: flat-bottom harmonic distance restraint (r_flat = 3.0 A, k = 2 kcal/mol/A^2) between closest ligand O and Zn during minimization + NVT + NPT equilibration only. Released before production (k -> 0) so the 50 ns trajectory measures whether coordination is a dynamical minimum, not a restrained pose.

### mTOR FRB-specific

- PDB 1FAP chain B only (FKBP12 chain A stripped — FKBP12-independent target).
- All HETATM removed (rapamycin, waters).
- POCKET_FIXED centre: aromatic triad COM [-14.907, 28.278, 29.232] A = [-1.491, 2.828, 2.923] nm.
- No unusual parameterization — standard GAFF2.

### Placement strategy

Per-compound SDF from PocketXMol has docked coords; if SDF COM is within 0.5 nm of the validated pocket centroid, keep the pose. Otherwise rigid-translate COM to POCKET_FIXED centre (no COM-to-COM bug — cf. `mmpbsa-ligand-placement-bug.md`).

### Quality-gate guardrails (per `rule-dataset-verify-before-use.md`)

1. Aromatic-bond pre-flight (< 1.50 A required).
2. Frame-0 ligand-protein min distance < 10 A (ensures pose is docked, not ejected).
3. PBC-aware distances via `box=ts.dimensions` in all MDAnalysis calls.
4. MMPBSA topology rebuilt via `pdb4amber --no-reorder` on DCD frame 0 only (prevents atom-order explosion).
5. DRAFT until triple_llm 3/3 PASS.

---

## Analysis outputs (per run)

- `trajectory.dcd`, `topology.pdb`, `final_50ns.pdb`, `equil.csv`, `energy.csv`, `metadata.json`
- `rmsd_ca.csv`, `rmsd_ligand.csv`, `ligand_pocket_distance.csv`, `contacts_6A.csv`
- **HDAC2 only**: `zn_ligand_O_distance.csv` — closest ligand O to Zn per frame
- **mTOR only**: `triad_min_distance.csv` — ligand-to-triad min distance per frame
- `mmpbsa/mmpbsa_results.dat`, `mmpbsa/mmpbsa_summary.json` (100 frames, last 30 ns, GB-OBC igb=5)

---

## Metrics to report

### HDAC2 Zn-chelator persistence

For each hydroxamate compound:
- **Zn-coordinated fraction**: % of frames where min(ligand O, Zn) < 3.0 A (tight coord) and < 4.0 A (loose coord).
- **Cross-campaign**: among 3 hydroxamate compounds, what fraction of 3 *stays* coordinated > 80% of 50 ns?
- Expected: SAHA-class hydroxamates should retain coordination in >90% of frames if the ligand geometry is consistent with Zn-binding.

### mTOR FRB pi-stacking persistence

For each compound:
- **Triad engagement**: % of frames where min(ligand heavy, triad ring atoms) < 5.0 A.
- **Triad residue contact frequencies** (from `contacts_6A.csv`): Trp2101, Tyr2104, Phe2108 contact fraction.
- Expected: aromatic polycyclics should maintain triad contacts > 70% of frames.

### Common

- **Cα RMSD** over 50 ns (< 3 A stability threshold).
- **Ligand-pocket distance retention**: % frames with pocket distance < 10 A (ligand in pocket).
- **MMPBSA ΔG_bind** on last 30 ns, every 300 ps.

---

## Ranking per target (computed after runs complete)

Composite score:
1. Ligand retention > 80% of frames.
2. Cα RMSD < 3 A.
3. MMPBSA ΔG_bind ≤ reference (SAHA for HDAC2 — to be computed separately; no FRB reference, use internal ranking).
4. HDAC2: Zn-coordinated fraction > 80% at 4 A cutoff.
5. mTOR: triad-engaged fraction > 70%.

Primary wet-lab triage candidate per target = top-scoring compound on all 5 criteria.

---

## Kill switches

- Any run's frame-0 placement fails (ligand > 10 A from protein) -> abort and re-dock.
- Smoke: first run >= 12 h wall-clock -> pause, re-plan.
- Any MMPBSA reports +ΔG for a clear binder -> atom-order bug — rebuild topology.
- Budget burn > $50 -> kill and escalate.

---

## Results — to be filled on completion

### HDAC2 runs

| Rank | SDF | Duration (ns) | Cα RMSD mean (A) | Lig retention (%) | Zn coord < 3 A (%) | Zn coord < 4 A (%) | ΔG_bind (kcal/mol) | Verdict |
|-----:|----:|--------------:|-----------------:|------------------:|-------------------:|-------------------:|-------------------:|---------|
| #1 518  | hydroxamate | TBD | TBD | TBD | TBD | TBD | TBD | PENDING |
| #4 437  | hydroxamate | TBD | TBD | TBD | TBD | TBD | TBD | PENDING |
| #15 200 | hydroxamate | TBD | TBD | TBD | TBD | TBD | TBD | PENDING |

### mTOR FRB runs

| Rank | SDF | Duration (ns) | Cα RMSD mean (A) | Lig retention (%) | Triad contact (%) | Triad min-dist mean (A) | ΔG_bind (kcal/mol) | Verdict |
|-----:|----:|--------------:|-----------------:|------------------:|------------------:|------------------------:|-------------------:|---------|
| #1 172 | biaryl     | TBD | TBD | TBD | TBD | TBD | TBD | PENDING |
| #2 345 | tetracycle | TBD | TBD | TBD | TBD | TBD | TBD | PENDING |
| #3 84  | naphthoimi | TBD | TBD | TBD | TBD | TBD | TBD | PENDING |

---

## Framing (for internal log, not external comms)

Per-campaign headers `hdac2_v2_RESULTS.md` and `mtor_frb_RESULTS.md`: both are
methodology / compute exercises, NOT primary SMA therapeutic tracks. Not included
in external outputs to Tuvoc / Simon / Piyush / Dinky (cf. `rule-tuvoc-cms-only.md`
+ `session-2026-04-17-data-integrity-incident.md` — no external comms while QMS audit ongoing).

HDAC2 SMA relevance: HDAC inhibition upregulates SMN2 (early valproate/romidepsin trials). A clean hydroxamate-class lead would be a secondary backup to splice modulators.

mTOR SMA relevance: autophagy balance in motor neurons; FRB-direct binders would be a *novel* mechanism (current rapalogs/rapamycin require FKBP12 adapter).

---

## Deliverables

- `/home/bryza/fleet-results/hdac2_inhibitor_v2_zn_retained/md/runs/` — 3 HDAC2 trajectories
- `/home/bryza/fleet-results/mtor_frb_allosteric/md/runs/` — 3 mTOR trajectories
- `/home/bryza/sma-research/qms/hdac2_mtor_md_RESULTS.md` — this file (DRAFT -> VERIFIED on 3/3)
- `/home/bryza/sma-research/qms/hdac2_mtor_md_plan.md` (identical plan archived)

Triple-LLM verification via `/home/bryza/gpu-fleet/scripts/triple_llm_verify.py` after all 6 runs complete.

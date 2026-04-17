# LIMK2-Activator 100 ns MD Campaign — RESULTS

**Status:** DRAFT (pipeline in progress — awaiting compute)
**Date initiated:** 2026-04-17
**Pipeline plan:** `/home/bryza/sma-research/qms/limk2_md_plan.md`
**Compute host:** Vast A100 SXM4 40 GB, contract 35120547, ssh4.vast.ai:10546 (Czechia)
**Triple-LLM verify:** NOT YET RUN (pending MD + MMPBSA completion)

---

## 1. Context

Dynamical stability validation of top-N LIMK2-αC-helix allosteric activator candidates from the upstream PocketXMol → BBB-hardfilter → DiffDock C_rel → Boltz-2 15-kinase Z-score pipeline (agent `abbbbde9`, outputs in `/home/bryza/fleet-results/limk2_activator_alphaC/`).

**Caveat from meta-analysis (see `/home/bryza/sma-research/qms/LIMK2_retraction_brief_INTERNAL.md`):** LIMK2 direction in SMA MN is model-system-dependent (iMN/iN DOWN, SH-SY5Y UP). This activator compute track is **exploratory**; selectivity against inhibitor ligands is tracked separately. Do not export any conclusions externally until triple-LLM gate passes.

## 2. Method

- **Target:** LIMK2 PDB 4TPT chain A, DFG-out / αC-out allosteric pocket.
- **Pocket placement:** POCKET_FIXED centre `[-1.32, 0.64, 2.80]` nm (empirically validated LIMK2 αC/ATP cleft centroid from prior LIMK2_BMS5_POCKET_FIXED run that gave ΔG = −35 kcal/mol). **Never COM-placed** (per `mmpbsa-ligand-placement-bug.md`).
- **Force field:** Amber14-all (protein) + TIP3P-FB water + GAFF-2.11 (ligand) with AM1-BCC charges via antechamber.
- **Simulation parameters:** PME 1.0 nm cutoff, HBond constraints, 2 fs timestep, LangevinMiddle 300 K, 0.15 M NaCl.
- **Equilibration:** 5 000-iter energy minimisation, 100 ps NVT, 100–500 ps NPT.
- **Production:** 50 ns NPT per compound (rank 1–5), 100 ns for smoke control.
- **Analysis:** MDAnalysis with `box=u.dimensions` on **every** `distance_array` call (per `learning-pbc-distance-bug.md`). MM-GBSA via AmberTools MMPBSA.py with prmtop rebuilt from trajectory first frame via `pdb4amber --no-reorder` (per `learning-ambertools-atom-order-bug.md`).

## 3. Smoke test (positive control)

**Ligand:** LIMKi3 (SMILES `CC(C)Nc1ncnc(-c2ccc3[nH]ccc3c2)c1C#N`, MW 277.3 Da, 36 heavy atoms).
**Production:** 10 ns.

| Metric | Value | Gate | Status |
|---|---|---|---|
| Protein atoms (4TPT, cleaned) | 8 889 | — | OK |
| Solvated system | 95 635 atoms | — | OK |
| Max aromatic bond length | 1.422 Å | <1.50 Å | PASS |
| Frame 0 ligand–protein min distance | 0.51 Å | <10 Å (not <0.05 clash) | PASS (small clash, minimiser resolved) |
| Production speed | 155 ns/day | >50 ns/day | PASS |
| Cα RMSD mean (post-1ns) | TBD | <3 Å | PENDING |
| Ligand-pocket retention (5 Å) | TBD | >80% | PENDING |
| Verdict | TBD | STABLE_BINDER or PARTIAL | PENDING |

(populated after analysis.json lands)

## 4. Top-5 production runs

**Input file:** `/home/bryza/fleet-results/limk2_activator_alphaC/top_hits.tsv` (from downstream agent abbbbde9, columns: `smiles, bbb_score, diffdock_conf, C_rel, iptm_LIMK2, z_LIMK2, iptm_{14 off-targets}, selectivity_z, rank`).

| Rank | SMILES | selectivity_z | Cα RMSD mean (Å) | Lig-pocket retention (%) | ΔG_GBSA (kcal/mol) | Verdict |
|---:|---|---:|---:|---:|---:|:--:|
| 1 | TBD | — | — | — | — | PENDING |
| 2 | TBD | — | — | — | — | PENDING |
| 3 | TBD | — | — | — | — | PENDING |
| 4 | TBD | — | — | — | — | PENDING |
| 5 | TBD | — | — | — | — | PENDING |

(populated after each run.json lands)

## 5. Ranking & interpretation

TO BE WRITTEN after data lands. Criteria:

1. Cα RMSD mean < 3 Å throughout production (stability).
2. Ligand-pocket retention > 80 % at 5 Å (pose dynamical minimum).
3. ΔG_GBSA ≤ LIMKi3 reference − 2 kcal/mol (binding affinity).
4. No ejected frames (> 20 Å) — triggers PBC re-verification.

## 6. Limitations

- 50 ns per compound is a triage scale, not a definitive binding-free-energy calculation. Top hits should go to 100+ ns + FEP on a subsequent compute allocation.
- MM-GBSA (igb=5) is an implicit-solvent approximation; differences of < 2 kcal/mol between ranks are not significant.
- Boltz-2 iptm Z-score panel used by upstream is itself an approximation and has shown occasional rank inversions vs co-crystal references.
- LIMK2-activator mechanistic hypothesis depends on iMN/iN-specific downregulation that is not seen in SH-SY5Y datasets.

## 7. Quality status

- [x] Pre-flight plan archived (`/home/bryza/sma-research/qms/limk2_md_plan.md`)
- [ ] Smoke test (LIMKi3 10 ns) passed
- [ ] Top-5 production runs completed
- [ ] MMPBSA completed for all 5
- [ ] Triple-LLM verify 3/3 PASS
- [ ] DRAFT → APPROVED

**DRAFT — not for external circulation until all gates pass.**

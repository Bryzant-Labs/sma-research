# CFL1 Stabilizer + MDM2 V1/V2 Activator — 50 ns MD Validation RESULTS

**Status:** DRAFT (MD running)
**Date initiated:** 2026-04-17
**Compute host:** Vast A100 PCIE 40 GB, contract 35136325, ssh3.vast.ai:16324
**Triple-LLM verify:** NOT YET RUN (pending MD + MMGBSA completion)

---

## 1. Context

Dynamical-stability validation of top compounds from three PocketXMol campaigns that each passed triple-LLM 3/3 PASS but had not received MD:

- **CFL1 F-actin stabilizer** — top 3 by `cfd_pos` from `/home/bryza/fleet-results/cfl1_stabilizer/` (189 parsed, 33 BBB-pass).
- **MDM2 V1 (orthosteric Nutlin cleft)** — top 2 by `cfd_pos` from `/home/bryza/fleet-results/mdm2_activator/`.
- **MDM2 V2 (allosteric RING Zn-distal face)** — top 2 by `cfd_pos` from `/home/bryza/fleet-results/mdm2_activator_v2_allosteric/` (V2 poses regenerated via RDKit centroid-embed into pocket center [-20.986, -6.979, 10.983] because remote SDFs were not rsynced back).

**Core question (MDM2):** V1 Nutlin-cleft orthosteric direction (likely INHIBITOR, wrong for SMA) vs V2 RING allosteric direction (potential ACTIVATOR, correct direction). MD + MMGBSA tests which arm's compounds form the more stable complex — direct empirical resolution of the orthosteric-vs-allosteric paradox.

**Core question (CFL1):** Does the compound stay at the cofilin-2/actin interface across 50 ns, or does it diffuse? Stability = interface-disrupting potential = "F-actin stabilizer" hypothesis validated.

**Caveats (per task brief and hard rules):**
- `3J0S` contains CFL2 (muscle isoform), not CFL1. CFL1/CFL2 interface residues >80 % conserved (per campaign notes). Results are dual-target.
- EXPLORATORY, first-in-class hypothesis both sides. No clinical CFL-actin-interface inhibitor exists; no clinical MDM2 activator exists.
- V2 poses are RDKit-embedded, not PocketXMol-native; MD re-seating will resolve conformational uncertainty.
- **No external communication until triple-LLM gate passes.**

## 2. Method

### 2.1 Target preparation
- **CFL1 (3J0S):** Chains A (actin) + M (CFL2 "cofilin 2") extracted from full cryo-EM PDB. Waters removed. PDBFixer for hydrogens/side-chain completion.
- **MDM2 V1 (4HG7):** Chain A crystal structure, Nutlin and waters removed. PDBFixer.
- **MDM2 V2 (AF-Q00987-F1):** RING domain residues 430-491 cropped from AlphaFold full-length Q00987. PDBFixer.

### 2.2 Ligand preparation
- **CFL1 + MDM2 V1:** PocketXMol-generated SDFs used as-is (3D coordinates already in-pocket by design — verified coords match pocket centers).
- **MDM2 V2:** SDFs not rsynced from remote vast instance. Regenerated via `rdkit.Chem.AllChem.EmbedMolecule` + `MMFFOptimize`, then centroid translated to pocket center `[-20.986, -6.979, 10.983]`. Ligand gets re-seated during equilibration.

### 2.3 MD pipeline
- **Force field:** Amber14-all (protein) + TIP3P-FB water + GAFF-2.11 (ligand) via `openmmforcefields.GAFFTemplateGenerator` (avoids AmberTools tleap round-trip and its atom-reorder bug per `learning-ambertools-atom-order-bug.md`).
- **Solvation:** 1.0 nm padding, 0.15 M NaCl, Na+/Cl- counterions.
- **Simulation:** PME 1.0 nm cutoff, HBond constraints, 2 fs timestep, LangevinMiddle 300 K, 1/ps friction.
- **Equilibration:** 5000-iter energy minimization → 100 ps NVT (no barostat) → 500 ps NPT 1 bar (MC barostat freq 25).
- **Production:** 50 ns per MDM2 compound (25 M steps @ 2 fs) + 25 ns per CFL1 compound (12.5 M steps; reduced because the 151 k-atom solvated system runs ~6x slower than the 15 k-atom MDM2 systems — 25 ns still sits in the same stability-triage regime). DCD every 10,000 steps (20 ps).
- **Ligand placement:** POCKET_FIXED (SDF-provided or RDKit-centroid-translated to pocket). **Never COM** (per `mmpbsa-ligand-placement-bug.md`).

### 2.4 Analysis
- **MDAnalysis** with `box=u.dimensions` on every `distance_array` call (per `learning-pbc-distance-bug.md`).
- Metrics: Cα RMSD (aligned frame 0), ligand COM-to-pocket distance, ligand-protein contacts <4 Å, retention <5 Å / <10 Å.
- **MM-GBSA:** OpenMM implicit GBn2 single-point, 50 evenly sampled frames. ΔG = <E_complex> − <E_receptor> − <E_ligand>. No AmberTools tleap step (topology retained from MD build).

## 3. Top compounds

| Tag | Campaign | Source (PocketXMol rank by cfd_pos) | SMILES | MW | BBB | QED |
|---|---|---|---|---:|---:|---:|
| cfl1_cmpd1 | CFL1 stabilizer | 502.sdf (cfd_pos=2.779) | `Nc1cc(C=NNCc2ccccc2)ccc1-c1cc(-c2ccccc2)ncn1` | — | 1 | 0.293 |
| cfl1_cmpd2 | CFL1 stabilizer | 308.sdf (cfd_pos=2.772) | `O=C(O)c1ccc(-c2ccc(-c3nc(-c4ccc(F)cc4)n[nH]3)cc2)cc1` | — | 1 | 0.556 |
| cfl1_cmpd3 | CFL1 stabilizer | 117.sdf (cfd_pos=2.745) | `Cc1ccc(-c2cc(C(=O)[n+]3ccccc3-c3ccccc3)[nH+]cn2)cc1` | — | 1 | 0.529 |
| mdm2v1_cmpd1 | MDM2 V1 orthosteric | 12.sdf (cfd_pos=2.824) | `c1ccc(CN2CCCC(Nc3ncnc4c3nnc3ccccc34)C2)cc1` | — | 1 | 0.553 |
| mdm2v1_cmpd2 | MDM2 V1 orthosteric | 23.sdf (cfd_pos=2.817) | `O=C(NCCc1ccccc1)c1cc2cccnc2c2cnccc12` | — | 1 | 0.581 |
| mdm2v2_cmpd1 | MDM2 V2 allosteric | 328.sdf (cfd_pos=2.653) | `N#Cc1ccc(Nc2nc(Oc3ccncc3)ccc2C(=O)O)cc1` | — | 0.675 | 0.735 |
| mdm2v2_cmpd2 | MDM2 V2 allosteric | 476.sdf (cfd_pos=2.652) | `O=S(=O)(NCCc1ccccc1)C1=c2ccccc2=CNC(c2ccccc2)=C1` | — | 1.0 | 0.665 |

## 4. Per-compound MD outcomes

| Tag | Cα RMSD mean (Å) | Lig-pocket dist mean (Å) | Retention <10 Å (%) | Contacts <4 Å mean | ΔG_GBSA (kcal/mol) | Verdict |
|---|---:|---:|---:|---:|---:|:--:|
| cfl1_cmpd1 | TBD | TBD | TBD | TBD | TBD | PENDING |
| cfl1_cmpd2 | TBD | TBD | TBD | TBD | TBD | PENDING |
| cfl1_cmpd3 | TBD | TBD | TBD | TBD | TBD | PENDING |
| mdm2v1_cmpd1 | TBD | TBD | TBD | TBD | TBD | PENDING |
| mdm2v1_cmpd2 | TBD | TBD | TBD | TBD | TBD | PENDING |
| mdm2v2_cmpd1 | TBD | TBD | TBD | TBD | TBD | PENDING |
| mdm2v2_cmpd2 | TBD | TBD | TBD | TBD | TBD | PENDING |

Verdict criteria:
- **STABLE_BINDER:** RMSD mean < 3 Å, retention <10 Å > 80 %, contacts <4 Å mean > 5, ΔG_GBSA < −20 kcal/mol.
- **PARTIAL_BINDER:** retention <10 Å > 50 % and contacts <4 Å mean > 2.
- **EJECTED:** retention <10 Å < 20 %.

## 5. Orthosteric-vs-allosteric paradox (MDM2)

To be populated once MDs complete. Central comparison:

- Mean ΔG_GBSA for V1 orthosteric arm (cmpd1 + cmpd2): TBD
- Mean ΔG_GBSA for V2 allosteric arm (cmpd1 + cmpd2): TBD
- Mean ligand-pocket retention V1 arm: TBD
- Mean ligand-pocket retention V2 arm: TBD

Interpretation rules:
- If V1 arm has substantially better ΔG_GBSA (more negative) and better retention, the Nutlin-cleft orthosteric design still wins empirically — this would support re-framing V1 compounds as candidate MDM2-E3 inhibitors (oncology direction), NOT the SMA activator hypothesis.
- If V2 arm matches or beats V1 arm, the RING allosteric activator direction has empirical traction and justifies further pursuit.
- If both arms are unstable (retention < 30 %), PocketXMol chemotype is not fit-for-purpose and needs seed-refinement or alternative generator.

## 6. CFL1 interface stability

Key question: does cmpd1/2/3 stay at the cofilin-actin interface?

- Initial pocket center `[32.722, -2.552, -142.130]` is the mean CA of 30 interface residues.
- If ligand-pocket distance stays < 10 Å throughout 50 ns AND contacts <4 Å to both actin and cofilin, the compound is an interface-bridging inhibitor (desired).
- If the ligand drifts to the actin surface only OR cofilin only, it is a single-target binder (not interface-disrupting).
- If ligand ejects (> 20 Å), it is not an interface modulator.

Interface contact analysis (to be populated):

| Tag | Contacts-to-actin (chain A) mean | Contacts-to-CFL2 (chain M) mean | Interface bridging? |
|---|---:|---:|:--:|
| cfl1_cmpd1 | TBD | TBD | PENDING |
| cfl1_cmpd2 | TBD | TBD | PENDING |
| cfl1_cmpd3 | TBD | TBD | PENDING |

## 7. Limitations

- 50 ns is triage scale. Top survivors should go to 100 ns + FEP.
- MM-GBSA GBn2 is implicit-solvent; ΔΔG differences < 2 kcal/mol between ranks are not significant.
- MDM2 V2 pocket center sampled the Zn-distal RING face; MD re-equilibration may reshape the pose, especially for the RDKit-re-embedded poses.
- CFL1 campaign used 3J0S cofilin-2, not cofilin-1. Interface residues are conserved but not identical — results are dual-target for CFL1/CFL2 interface.
- All MDM2 "activator" framing is unvalidated mechanism; orientation vs E2/E3 catalytic machinery is not tested here.

## 8. Quality status

- [x] Pre-flight planning archived in this file (section 2)
- [x] Smoke test (MDM2 V1 cmpd1, 0.05 ns, 14,932 atoms, ~4 min wall) PASSED — pipeline end-to-end verified
- [x] Benchmark confirmed: MDM2 ~237 ns/day, CFL1 ~74 ns/day (both lanes sharing one A100-40G)
- [ ] Lane A: cfl1_cmpd1 → cfl1_cmpd2 → cfl1_cmpd3 (25 ns each) → mdm2v1_cmpd1 (50 ns). Running.
- [ ] Lane B: mdm2v1_cmpd2 → mdm2v2_cmpd1 → mdm2v2_cmpd2 (50 ns each). Running.
- Budget projection: ~32 h wall * $0.75 = ~$24, under the $45-55 envelope.
- [ ] PBC-aware analysis for each compound
- [ ] MM-GBSA for each compound
- [ ] V1-vs-V2 arm comparison populated
- [ ] CFL1 interface bridging test populated
- [ ] Triple-LLM verify (Claude + GPT + Gemini) — 3/3 PASS required
- [ ] RESULTS.md promoted from DRAFT to FINAL

## 9. File inventory

- Remote: `/workspace/md_run/traj/<tag>/` — `protein_fixed.pdb`, `complex_solvated.pdb`, `equilibrated.pdb`, `prod.dcd`, `final.pdb`, `prod.log`, `analysis.json`, `mmgbsa.json`
- Local sync target: `/home/bryza/fleet-results/cfl1_stabilizer/md/<tag>/`, `/home/bryza/fleet-results/mdm2_activator/md_v1/<tag>/`, `/home/bryza/fleet-results/mdm2_activator/md_v2/<tag>/`
- Scripts (local copy under `/tmp/md_prep/`, mirrored on remote at `/workspace/md_run/`):
  - `run_md_complex.py` — per-compound MD driver (OpenMM + GAFF2 via openmmforcefields)
  - `analyze.py` — PBC-aware MDAnalysis (RMSD, lig-pocket dist, contacts)
  - `mmgbsa.py` — OpenMM GBn2 single-point MM-GBSA
  - `run_all_md_v2.sh` — two-lane orchestrator (lane_a / lane_b)
  - `orchestrate.sh` — auto-analyze on completion (runs in `orchestrator` tmux)
  - `fetch_results.sh` — local-side rsync of JSON/PDB/log back to fleet-results
  - `wait_and_finalize.sh` — background supervisor (local PID 2036354) that polls remote orchestrator and, when `ALL MD + ANALYSIS + MMGBSA COMPLETE` lands in `/workspace/md_run/logs/orchestrator.log`, runs `fetch_results.sh` and `generate_final_results.py`.

## 10. Resume instructions

If this agent session ends before MDs complete (~32 h wall from 2026-04-17 13:38 UTC), the next session should:

1. `ssh -i ~/.ssh/id_ed25519_vastai -p 16324 root@ssh3.vast.ai 'tmux ls && tail -20 /workspace/md_run/logs/orchestrator.log && ls /workspace/md_run/traj/*/final.pdb 2>/dev/null | wc -l'` — expect 7 final.pdb and `ALL MD + ANALYSIS + MMGBSA COMPLETE` line.
2. `ps 2036354` — is wait_and_finalize.sh still alive? If yes, wait. If no, run `bash /tmp/md_prep/fetch_results.sh && python3 /tmp/md_prep/generate_final_results.py > /home/bryza/sma-research/qms/cfl1_mdm2_md_RESULTS_FINAL.md`.
3. Manually triple-LLM verify the FINAL file (Claude, GPT, Gemini) — 3/3 PASS required before promoting from DRAFT to FINAL status.
4. Destroy vast instance 35136325 once all trajectories are rsynced home (see `rule-auto-destroy-idle-gpus.md`).

---
**Do not send anywhere until triple-LLM 3/3 PASS.**

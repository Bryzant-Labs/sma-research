# CDK5 Allosteric Activator (p25-interface) — Results

**Status:** INTERNAL — `triple_llm_verify` 3/3 PASS (GPT-4o PASS, Llama-3.3-70B PASS, Gemini 2.0 Flash PASS). Still NOT cleared for external comms: the upstream SMA direction question (LIMK2 meta-analysis APPROVED / model-system chosen) must resolve first. Treat as exploratory internal compute only.
**Date:** 2026-04-17
**Campaign ID:** `cdk5_activator_p25iface`
**Exploratory level:** HIGH — no published SMA CDK5 evidence; hypothesis-driven compute.
**Author:** Claude (Opus 4.7)

## TL;DR

- Generated **600 small molecules** (A100 SXM4 40 GB, PocketXMol, 2 min wall clock) targeting
  the **p25-binding interface on CDK5** (1UNH chain A, not ATP site).
- **529 valid RDKit SMILES** (88.2% valid). **85 compounds (16.5%) pass BBB hardfilter**
  (MW ≤ 450, logP 1.0–4.5, TPSA ≤ 90, HBD ≤ 3, QED ≥ 0.40).
- Zero ATP-analog / phosphate contamination in the BBB-pass set.
- 170 Boltz-2 affinity tasks queued for **CDK5 × CDK2** selectivity pair (85 compounds × 2 kinases).

All outputs are **exploratory compute**. No therapeutic claim. Direction ("activator better
than inhibitor in SMA iMN") has **no direct published support** and remains a hypothesis.

## Biological rationale (copy from plan)

- CDK5 phosphorylates **cofilin at S3** — same residue as LIMK2.
- 2026-04-17 SMA meta-analysis: LIMK2 **DOWN** in Hb9-iMN / organoid, UP in SH-SY5Y.
- **If the iMN branch is the disease-relevant one**, enhancing CDK5 activity could compensate
  for LIMK2 LoF via a parallel enzyme on the same substrate.
- CDK5 uniquely requires p35 or p25 for activation (no cyclin). Allosteric activators at
  the p25 interface could mimic the activator-bound state without requiring calpain cleavage.
- **Caveat**: p25 itself is pathological (Alzheimer's tau hyperphosphorylation). Any activator
  must avoid mimicking p25's disease-causing aspects. Primary risk: tauopathy aggravation.
- **Zero published small-molecule CDK5 allosteric activators globally.** First-in-class exploratory.

## Instance + compute

| Parameter | Value |
|---|---|
| Vast contract | 35120543 |
| GPU | A100 SXM4 40 GB (Slovenia) |
| Wall clock (full 600-mol run) | **130 s** (08:27:55 – 08:30:05 UTC, 2026-04-17) |
| GPU utilization | 93% sustained |
| VRAM | 1.8 GB peak |
| Cost | ~$0.025 (130 s × $0.69/h) |

## Pocket derivation

1UNH (CDK5 chain A + p25 chain D cocrystal, 2003, Tarricone et al.). Parsed all ATOM records,
computed 6.0 Å contact pairs between each (CDK5, p25) chain combination:

| CDK5 chain | p25 chain | contact atoms |
|---|---|---|
| **A** | **D** | **232** (selected) |
| A | E | 0 |
| B | D | 0 |
| B | E | 227 |

40 CDK5 residues on chain A within 6 Å of p25 chain D:

```
37, 38, 43, 44, 45, 46, 47, 49, 50, 52, 53, 54, 56, 57, 58,
69, 70, 71, 74, 76,
120, 121, 122, 125,
146, 147, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 161, 162, 177
```

- **45–58**: PSTAIRE-equivalent α-C helix (canonical cyclin/activator binding face in CDKs).
- **69–76**: β3–β4 face, glycine-rich loop region.
- **146–162**: L12 loop + αEF helix — secondary cyclin contact surface.
- **177**: activation loop start.

Pocket center (mean CA of interface residues on CDK5 side):
**[31.093, −0.232, 26.309] Å** (PDB-relative coords).

## Generation parameters

- PocketXMol SBDD simple mode
- Pocket radius: 10.0 Å
- Molecule-size prior: ~28 heavy atoms, σ 2, min 5 (~330 Da drug-like)
- Seed: 2024
- Batch size: 50 × 12 batches = 600 target
- Denoising steps: 100 per batch, 10.0 it/s on A100

Per-batch pool stats (Succ/Incomp/Bad):
- Batch 1: 43/0/7 (86% success)
- Batch 2: 85/1/14 (85% vs cumulative 43)
- ... (pattern steady through all 12 batches, ~85–90% per-batch success)

Final summary: **n_molecules_collected = 600**, **n_smiles = 529** (88.2% RDKit-parseable).

## BBB / drug-likeness filter

Applied Martins-like hardfilter + Lipinski + QED:

```
MW ≤ 450, logP 1.0–4.5, TPSA ≤ 90, HBD ≤ 3, HBA ≤ 8,
RotB ≤ 8, heavy 15–35, QED ≥ 0.40
```

Results:
- Parsed: 516 / 529 (13 unparseable post-SMILES cleanup)
- Pass: **85 / 516 = 16.5%**
- Top failure reasons: TPSA > 90 (302), logP out-of-band (268), QED < 0.40 (210), HBD > 3 (171), HBA > 8 (117)

The low BBB pass-rate vs LIMK2 ATP campaign is expected: **PPI-like allosteric pockets
bias generation toward larger, more polar molecules.** Alternative path (future):
relax TPSA ceiling to 120 for non-CNS-penetrant assessment (CDK5 activation is
arguably also a peripheral neuron target).

## Top 15 BBB-pass candidates (ranked by PocketXMol confidence, ascending = better)

| rank | idx | cfd_sum | MW | logP | TPSA | QED | SMILES |
|---|---|---|---|---|---|---|---|
| 1 | 45 | 28.26 | 353.4 | 3.55 | 86.6 | 0.784 | `CC1=CC=C2C1=Cc1sc3cc(C(=O)NCCC(=O)O)cc(O)c3c12` |
| 2 | 582 | 28.99 | 370.4 | 3.74 | 74.0 | 0.415 | `Cc1ccc2c(c1)-c1oc3cn4c(=O)n5ccc(C)nc5nc4c3c1C=CO2` |
| 3 | 99 | 29.03 | 328.4 | 3.13 | 45.2 | 0.772 | `CC(C)(C)c1c[nH]c(=O)c2c1=NC=2c1ccc(-c2ccccc2)cc1` |
| 4 | 564 | 29.52 | 382.4 | 4.37 | 80.9 | 0.557 | `CC(=O)NC1=CC(c2nc3ccc(C)ccc-3n2)=Cc2c(C)ccc3onc1c23` |
| 5 | 264 | 29.56 | 316.4 | 3.43 | 68.6 | 0.616 | `Cc1cc2c(C)c(C)ccc2[nH+]c1-c1ccc(-c2nnn[nH]2)cc1` |
| 6 | 7 | 29.64 | 317.3 | 2.56 | 72.2 | 0.629 | `Cc1ccc2nc(NCc3ccc4ccccc4c3)nn2c(=O)n1` |
| 7 | 201 | 29.93 | 374.4 | 2.30 | 84.8 | 0.532 | `O=C1C=C(c2ccc(-c3ccc[n+](O)c3)[nH+]c2)C[C@@H]2Oc3ccc(O)cc3[C@H]12` |
| 8 | 187 | 29.98 | 319.4 | 3.43 | 68.0 | 0.803 | `Cc1ncc2c(c1-n1cnc(-c3ccc(C(=O)O)cc3)c1)CCC2` |
| 9 | 511 | 30.03 | 359.3 | 3.27 | 88.0 | 0.685 | `C[C@@H](C(F)F)n1[nH]cc2cc(-c3cccc(C=CC(=O)O)c3)nc-2c1=O` |
| 10 | 539 | 30.25 | 348.3 | 3.61 | 75.6 | 0.561 | `Nc1c(N=Cc2ccco2)c(O)cc[n+]1-c1ccc(C(F)(F)F)cc1` |
| 11 | 176 | 30.39 | 329.4 | 4.13 | 46.5 | 0.678 | `O=C(c1ccc(C2=CN=CCC2)o1)[n+]1ccc(-c2ccccc2)cc1` |
| 12 | 369 | 30.40 | 391.4 | 4.19 | 70.0 | 0.728 | `O=C1C=C2NN=NC2CN1c1nc(-c2ccc(-c3ccc(F)cc3)cc2)cs1` |
| 13 | 488 | 30.41 | 387.4 | 4.10 | 67.1 | 0.452 | `OC(=Cc1cccc2c(C(F)(F)F)c[nH]c12)NCCn1c[nH+]c2ccccc21` |
| 14 | 505 | 30.42 | 371.4 | 3.86 | 83.5 | 0.407 | `Cc1ccc(O)c2c1C(=O)C(=O)[C@H](c1ccc(-c3ccccc3)cc1)C(=O)N2` |
| 15 | 474 | 30.62 | 402.5 | 4.10 | 89.3 | 0.506 | `Cc1ccc2c(c1)cc1c3c(cc(Cc4cccc(S(N)(=O)=O)c4)cc32)C(=O)N1` |

Chemotype tally in top 15: indole (1), fused pyrimidine / benzo-fused N-heterocycle (6),
pyrazole-carboxylate (2), sulfonamide (1), mixed biaryl (5). None are obvious ATP
mimetics (no hinge-binder diaminopyrimidine/purine pattern in the top set), which is
consistent with targeting the p25 interface rather than ATP pocket.

## Boltz-2 selectivity queue (submitted, PENDING)

170 tasks queued to dispatcher DB (task IDs `boltz2_cdk5act_{cdk5|cdk2}_{idx}`):
- 85 BBB-pass compounds × 2 kinases (CDK5 primary + CDK2 paralog selectivity control)
- Priority 2, status `queued`

Pending expansion after initial triage (post-Boltz-2 CDK5/CDK2 analysis):
- Full 15-kinase panel (CDK1, CDK7, CDK9, LIMK1/2, ROCK1/2, JAK1/2/3, SRC, FYN, LCK, PAK1/4, MAPK14)
- DiffDock self-dock validation on a 1UNH re-prepared structure (to compute C_rel baseline)

**Selectivity gate (hard rule)**: `z_CDK5 > 0` AND `z_CDK5 > z_CDK2` per row.
No CDK2-preferring compound will be flagged as a CDK5 activator lead.

## Open risks / caveats

1. **No published SMA CDK5 dysregulation evidence.** This campaign is an exploratory
   hypothesis based on cofilin-S3 parallelism with LIMK2. If the iMN LIMK2-DOWN branch
   is not the therapeutically relevant model system (see `session-2026-04-17-data-integrity-incident.md`),
   the whole CDK5-activator rationale collapses.
2. **Tauopathy risk.** p25-mimetic CDK5 activators risk aggravating tau hyperphosphorylation.
   Any lead must be checked against tau phosphorylation liability (MD on 4TNR tau-bound
   CDK5 structure in a follow-up campaign).
3. **Activator vs occupier.** PocketXMol generates shape-complementary molecules; it
   does NOT distinguish "stabilizes the active p25-bound conformation" from "sits in the
   pocket without functional effect". MD on top 5 binders is required to confirm the
   allosteric-activator mechanism (not in this campaign's scope).
4. **CDK2 paralog selectivity** is the primary pharmacology risk. CDK2 is cell-cycle
   critical; off-target CDK2 activation = uncontrolled proliferation. Selectivity gate
   above is mandatory.
5. **1UNH has a cocrystallized CDK5 inhibitor (roscovitine/aloisine/indirubin)** at the
   ATP site on the opposite face. The p25-interface pocket center [31.093, −0.232, 26.309]
   is ~17–20 Å from the ATP pocket (based on kinase domain geometry). Cross-contamination
   of training signal between the two sites in PocketXMol's SBDD mode is possible but
   unlikely given the spatial separation. Verified: **0% ATP/phosphate content in BBB-pass set.**
6. **Pocket radius 10 Å** captures ~40 interface residues but may over-select surface
   residues vs deep pocket residues. If top leads bind shallow surface and lose in Boltz-2,
   re-run with radius 8 Å for tighter pocket definition.

## Provenance / reproducibility

| Artifact | Path |
|---|---|
| Plan (pre-flight) | `/home/bryza/sma-research/qms/cdk5_activator_plan.md` |
| Results (this file) | `/home/bryza/sma-research/qms/cdk5_activator_RESULTS.md` |
| Raw SMILES | `/home/bryza/fleet-results/cdk5_activator_p25iface/molecules.smi` (529 lines) |
| BBB-pass SMILES | `/home/bryza/fleet-results/cdk5_activator_p25iface/molecules_bbb_pass.smi` (85) |
| PocketXMol gen_info | `/home/bryza/fleet-results/cdk5_activator_p25iface/gen_info.csv` |
| BBB filter script | `/home/bryza/fleet-results/cdk5_activator_p25iface/bbb_filter.py` |
| Pocket derivation | `/home/bryza/fleet-results/cdk5_activator_p25iface/provenance/derive_pocket.py` |
| Filtered CDK5 chain A | `/home/bryza/fleet-results/cdk5_activator_p25iface/provenance/1unh_cdk5_chainA.pdb` |
| Task JSON | `/home/bryza/fleet-results/cdk5_activator_p25iface/provenance/task.json` |
| Run log | `/home/bryza/fleet-results/cdk5_activator_p25iface/provenance/full_run.log` |
| Pocket center file | `/home/bryza/fleet-results/cdk5_activator_p25iface/provenance/pocket_center.txt` |
| Interface residues file | `/home/bryza/fleet-results/cdk5_activator_p25iface/provenance/interface_residues.txt` |
| Instance remote results | `root@ssh2.vast.ai:10542:/results/pocketxmol/cdk5_activator_p25iface/` (including 600 SDFs) |

Deploy script: `/opt/pocketxmol_deploy.py` on ssh2 (same version as LIMK2 campaign).
PocketXMol repo: `https://github.com/pengxingang/PocketXMol` (already cloned to `/opt/PocketXMol`).
Weights: Zenodo record `17801271`.

## Next steps (NOT executed yet)

1. Wait for Boltz-2 CDK5/CDK2 drain (170 tasks, dispatcher + throttled runners).
2. Compute Z-score selectivity per row.
3. Filter by `z_CDK5 > 0 AND z_CDK5 > z_CDK2`.
4. Top 5 leads → MD on 1UNH reconstituted CDK5/p25 complex (separate GPU campaign).
5. `triple_llm_verify` 3/3 PASS → remove DRAFT status.
6. If 3/3 PASS and any lead survives MD, write Simon-strippable brief (NO SMA/IDH1 language; see Rule 0).

---

**DRAFT STATUS PRESERVED. NO EXTERNAL COMMS. NO THERAPEUTIC CLAIM.**

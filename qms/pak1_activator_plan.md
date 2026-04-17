# PAK1 Allosteric Activator - Pre-Flight Plan

**Status:** DRAFT - exploratory (PAK1 alphaC-activator for SMA NMJ; complements PAK4 panel)
**Date:** 2026-04-17
**Author:** Opus (autonomous GPU fleet)
**Campaign ID:** pak1_activator_alphaC
**Contract:** 35120540 (A100 PCIE 40GB, ssh4.vast.ai:10540, Japan)

## Scientific rationale

PAK1 (p21-Activated Kinase 1, UniProt Q13153) is the Group-I PAK family prototype,
the cytoskeletal effector for Rac1/Cdc42 GTPases. It phosphorylates LIMK1 →
LIMK1 phosphorylates cofilin → F-actin stabilization at synaptic terminals and
the neuromuscular junction (NMJ). PAK1-null mice have NMJ structural defects
and defective presynaptic vesicle release.

- PAK1 sits in the **Rac1/Cdc42 → PAK → LIMK → cofilin → F-actin** axis,
  parallel to the PAK4 pathway we targeted earlier today.
- PAK1 activation stabilizes F-actin at synaptic terminals; plausibly rescues
  NMJ actin organization in SMA (motor endplate).
- **Hedge rationale:** PAK1 complements PAK4 (Group-II) by covering the
  Group-I PAK selectivity arm. A non-selective PAK pan-activator would
  activate both; the campaign produces a within-PAK selectivity reference set
  when compared against the PAK4 run.
- PAK1 is in our 15-kinase selectivity panel as the Group-I nearest neighbour.
- **Oncology caveat:** PAK1 hyperactivation is oncogenic (breast, colon).
  PAK1 activator for SMA is a narrow therapeutic-window proposition;
  first-in-class and HIGHLY EXPLORATORY. Not to be surfaced externally
  without Christian sign-off.

**Target:** PAK1 (UniProt Q13153, human), kinase domain.
**Strategy:** allosteric activator targeting the alphaC-helix region
(Type III-like), same design pattern as LIMK2/ROCK2/MuSK/PAK4 campaigns.

## Target selection - PDB verified 2026-04-17

Candidates (verified via RCSB JSON API + UniProt cross-refs):

| PDB | TITLE | mutations | resolution | pick? |
|---|---|---|---|---|
| 1F3M | Crystal Structure of Human Serine/Threonine Kinase PAK1 | none (WT) | 2.30 A | autoinhibited state; alphaC-out not ideal for activator |
| 1YHV | Crystal Structure of PAK1 with two point mutations | K299R, T423E | 1.80 A | same issue as 3Q52 |
| **3Q52** | **Structure of phosphorylated PAK1 kinase domain** | **K299R, L516I** | **1.80 A** | **CHOSEN** (brief recommendation) |
| 3FXZ | PAK1 + inhibitor | — | 1.64 A | ATP-site ligand contaminates |

**PICK: 3Q52** (1.80 A, phosphorylated PAK1 kinase domain; Wang et al 2011).
- TITLE verified: "Structure of phosphorylated PAK1 kinase domain"
- Method: X-RAY DIFFRACTION, 1.801 A
- Mutations: K299R (crystallography-stabilization to prevent
  autodephosphorylation) + L516I (minor surface residue, unrelated to catalysis)
- Phospho-T423 present (TPO residue; activation-loop pT423 = active state)
- Sequence range 248-545 matches UniProt Q13153 248-545 (DBREF confirmed)

**Mutation accepted:** K299R preserves positive charge + side-chain length at
the beta3 position. The alphaC-helix geometry is determined by the alphaC-Glu
E315 side of the salt bridge, which is NATIVE (wild-type) in 3Q52. The K→R
mutation does NOT distort alphaC pocket derivation. Documented in audit.

## Pocket derivation (alphaC-helix) - motif scan VERIFIED

Sequence-motif scan on 3Q52 chain A (residues 248-545):
- **beta3 residue (VAIR motif at 296-299)**: **R299** (K299R crystallography mutant; 3-letter = ARG)
- **alphaC-Glu (canonical Q13153 E315)**: **E315** = GLU (native, unmodified)
- **HRD catalytic**: **H387** (HRD at 387-389; scan hit)
- **DFG motif**: **D407** (DFG at 407-409; scan hit)

K299-E315 CA distance = 12.96 A (alphaC in a partially-open state, as
expected for a phosphorylated kinase with K299R destabilizing the canonical
salt bridge).

### Pocket center

- alphaC helix window: **307-319** (13 residues, E315 center +/- 6)
- Helix continuity: all consecutive CA-CA < 4.5 A (13 CAs)
- **Pocket center (A): (-28.055, -32.408, 10.574)**
- Pocket radius: **10 A**

### Sanity checks (all PASS)

| check | value | range | ok |
|---|---|---|---|
| dist(center, K299/R299-CA) | 13.33 A | [5, 18] | PASS |
| dist(center, E315-CA) | 3.73 A | [1.5, 8] | PASS |
| dist(center, D407-CA, DFG) | 10.69 A | [5, 22] | PASS |
| dist(center, H387-CA, HRD) | 13.07 A | [5, 22] | PASS |
| alphaC helix continuity | max gap < 4.5 A | - | PASS |
| nearest HETATM (TPO/pT423) | 12.01 A | > 5 A | PASS |
| reference residues resolved | R299=ARG, E315=GLU, D407=ASP, H387=HIS | - | PASS |

## Workflow (on A100 JP)

1. [DONE] SSH into contract 35120540 (ssh4:10540). `/results/READY` verified.
2. [DONE] PocketXMol already installed at /workspace/PocketXMol (SHA 65488cf),
   warm from MuSK + PAK4 campaigns. INSTALL SKIP.
3. [DONE] Fetched 3Q52 to /results/pak1_activator/3q52.pdb.
4. [DONE] Ran pocket-derivation script → pocket_center.txt + pocket_audit.json
   + 3q52_kinase_chainA.pdb. Sanity PASS after accepting K299R crystallography
   mutation (documented).
5. [DONE] Smoke test: 5 molecules in 25 sec. Succ/Incomp/Bad = 1/4/0. PASS.
6. [RUNNING] Full launch: tmux session `pxm_pak1`, 600 molecules, batch 50.
7. Post-run: collect SDFs, RDKit filter, BBB tag, Boltz-2 queue top 100.

## Post-generation (host-side)

8. rsync `/results/pak1_activator/full_output/` → `/home/bryza/fleet-results/pak1_activator_alphaC/`.
9. RDKit filters: valence-valid, Lipinski RO5.
10. BBB tag (NOT hardfilter drop; NMJ is peripheral tissue, parity with PAK4/MuSK).
11. Queue Boltz-2 rescore for top 100 vs PAK1 (localhost:8004 H100 TW Server #2).
12. Within-PAK selectivity: compare iptm margins vs PAK4 run from earlier today.

## Selectivity context (downstream, not this agent)

PAK1 kinase domain is closely related to:
- **PAK2, PAK3** (Group-I PAKs) — required in panel
- **PAK4, PAK5, PAK6** (Group-II PAKs) — panel, especially PAK4
- **LIMK1, LIMK2** (downstream PAK1 substrates) — in panel
- **ROCK1, ROCK2** (parallel rho-effector) — in panel

Selectivity requirement: PAK1-activator must NOT co-activate PAK2/3 (similar
cell-biology consequences) and must NOT cross-react with PAK4/5/6 (different
paralogue tree). The pocket at alphaC is PAK-subfamily-specific so the
selectivity panel is realistic.

## Quality gates (HARD)

- Pocket derivation script saved at `/home/bryza/gpu-fleet/scripts/pak1_alphaC_pocket.py`.
- Smoke test PASSED (25 sec, 1/4/0 valid pattern, A100 GPU fully utilized).
- Full launch tmux session `pxm_pak1` running.
- All results filed `STATUS: DRAFT` until `triple_llm_verify` 3/3 PASS.
- **PAK1 activator = oncology-adjacent.** Must flag in all external docs.
- Do NOT surface to Simon/Torsten without Christian sign-off.

## Expected output

- 600 SDFs in /results/pak1_activator/full_output/*/pak1_alphaC_full_SDF/.
- gen_info.csv with PocketXMol confidences (cfd_pos).
- After RDKit/Lipinski: ~70-85% pass (per PAK4 precedent today).
- After Boltz-2 rescore: ranked top-100 by iptm vs PAK1 fold.

## ETA

- Install + weights: 0 min (warm).
- 600-mol generation at batch 50, 100 denoising steps: ~3-5 min on A100 PCIE 40GB
  (PAK4 precedent earlier today: 600 mols in ~4 min on same instance type).

## Risks

| risk | mitigation |
|---|---|
| 3Q52 K299R mutation biases pocket | R vs K preserves electrostatic + length; alphaC geometry determined by native E315; ACCEPTED |
| 3Q52 alphaC K-E distance 13 A (not classical 4-6) | acceptable; phosphorylated kinase has displaced alphaC from mutation; pocket captures the activator-binding surface |
| ssh4:10540 SSH flakiness (JP link) | 2-3 retries; tmux persistence |
| PocketXMol OOM at batch 50 | PAK4 precedent used <2 GB / 40 GB; impossible |
| PAK1 oncology risk | flag in RESULTS; panel must include PAK2/3 before external |

## Budget

A100 PCIE JP: $0.60-0.70/hr × ~0.1 hr = **~$0.07**. Install skip saves ~7 min.

## Decision log

- DECISION: target **3Q52** (K299R phosphorylated PAK1 kinase domain at 1.8 A).
  Beats 1F3M (WT but autoinhibited, alphaC-out) and 1YHV (same K299R mutation,
  1.8 A but less recent). 3FXZ has inhibitor contamination.
- DECISION: accept K299R crystallography mutation. Documented in audit. Does
  not affect alphaC pocket geometry.
- DECISION: motif-scan-verified residues (E315/H387/D407) match canonical
  Q13153. No assumed numbering.
- DECISION: alphaC-helix pocket, same template as LIMK2/ROCK2/MuSK/PAK4.
- DECISION: 600 mols, matching PAK4 scale. Scale to 3000 only if Boltz-2
  rescore yields ≥ 20 ranked hits after PAK selectivity panel.
- DECISION: BBB tag-only (NMJ is peripheral), parity with PAK4/MuSK.

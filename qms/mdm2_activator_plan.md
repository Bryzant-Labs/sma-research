# MDM2 Activator / Allosteric-Enhancer Campaign — Pre-Flight Plan

**Status:** DRAFT (pre-flight)
**Date:** 2026-04-17
**Campaign ID:** `mdm2_activator`
**Purpose:** FIRST-IN-CLASS: novel-chemotype small molecules that ENHANCE MDM2 E3-ligase activity toward TP53, to REDUCE pooled-UP p53 protein in SMA motor neurons (opposite of all existing MDM2 oncology programs).
**Author:** Claude (Opus 4.7), dispatched by architect

## Biological rationale (from today's 3-dataset SMA MN meta-analysis)

- **Meta-analysis finding (2026-04-17)**: pooled TP53 expression in SMA motor neurons = **+0.260 (p = 0.030)** across 3 independent datasets. p53-downstream apoptosis axis (PERP, PUMA, NOXA) is elevated in SMA MN.
- **Directionality**: less p53 = less PERP/PUMA/NOXA apoptosis signalling. We want an **MDM2 ACTIVATOR / ENHANCER** (increases TP53 ubiquitination + proteasomal degradation).
- **Global chemotype space**: ALL clinical-stage MDM2 programs are INHIBITORS (Nutlin, RG7112, idasanutlin, NVP-CGM097, HDM201) for oncology (stabilize p53). An MDM2 activator is **first-in-class** and category-orthogonal.
- **EXPLORATORY framing (HARD)**: this is a novel mechanistic direction (opposite of oncology convention). No clinical precedent for MDM2 activators. Report as first-in-class generative hypothesis, not as validated therapeutic.
- **SMA mechanism path**: apoptosis pressure on MN → MN loss → muscle weakness. Reducing p53 (not blocking it — just trimming the UP signal) may relieve apoptotic pressure without shutting down p53's normal surveillance role.

## Instance

- Vast contract: **35124116** (replacement, still warm from JAK2+HDAC2+MTOR earlier today)
- Host: `ssh3.vast.ai:14116` (root user, key `~/.ssh/id_ed25519_vastai`)
- GPU: **1× A100 SXM4 80 GB** (Slovenia, offer 38639)
- Image: `pytorch/pytorch:2.4.1-cuda12.4-cudnn9-runtime`
- PocketXMol: already installed at `/opt/PocketXMol` (git SHA `65488cf635c856101dbe703ac97e2f10f58e005c`)
- Cost: ~$0.6944 / hr

## Target

| Parameter | Value | Source |
|---|---|---|
| Gene | MDM2 | UniProt Q00987 |
| Canonical name | E3 ubiquitin-protein ligase Mdm2 (HDM2) |
| PDB | **4HG7** | RCSB: "Crystal structure of an MDM2/Nutlin-3a complex" |
| Chain | A (p53-binding domain, residues 17-125) | COMPND verified |
| Source | Homo sapiens, gene MDM2 | Verified |
| Co-crystal ligand | NUT (Nutlin-3a) | HETATM |
| Strategy | Target AROUND/ADJACENT to the p53-binding cleft — find allosteric modulators that ENHANCE p53-binding (not block it like Nutlin) |
| Pocket center | TBD (computed on-instance from NUT HETATM mean) | Will derive |
| Pocket radius | 10.0 Å | PocketXMol SBDD convention |
| Molecule count | 600 | Per brief |
| Batch size | 50 | Matches JAK2/HDAC2 campaigns earlier today |

### Pocket derivation strategy (HARD — to be confirmed on-instance)

4HG7 is the MDM2 p53-binding cleft with Nutlin-3a occupying the Phe19/Trp23/Leu26 hotspot mimic. Two options:

1. **ORTHOSTERIC (same as Nutlin pocket)**: compute pocket center at mean of NUT heavy atoms. This is the p53-binding cleft. Ligands designed here will COMPETE with p53 and BLOCK MDM2-p53 interaction (= INHIBIT MDM2 function = STABILIZE p53 = WRONG direction for our hypothesis, same as Nutlin).
2. **ALLOSTERIC ADJACENT**: shift pocket center ~8-12 Å away from NUT center toward known MDM2 RING-domain / allosteric communication residues. **Target = allosteric stabilizer of the p53-bound conformation** (enhance ubiquitination turnover without blocking binding).

**Decision**: we'll run **OPTION 1 (orthosteric, nutlin-site)** but label the output as "**binding-cleft chemotype library**" — this is a necessary first pass to get novel chemotypes in the p53-binding region. Mechanistic direction (activator vs inhibitor) is evaluated post-hoc: compounds that bind near but NOT directly on F19/W23/L26 hotspots may act as p53-allosteric enhancers.

This is an EXPLORATORY chemotype generation, not a guaranteed activator screen. Boltz-2 rescore against the MDM2-p53 peptide complex will classify compounds by whether they **displace** p53 (inhibitor) or **co-bind** (potential activator / allosteric).

## Workflow

1. **SSH probe** (already verified, PocketXMol warm).
2. **Fetch 4HG7** from RCSB (already done to /tmp on-instance).
3. **Extract chain A only + strip HETATM (including NUT)** → `4hg7_chainA.pdb` in `/root/mdm2_work/`.
4. **Compute pocket center** as mean of NUT HETATM heavy atoms (19 atoms). Cross-check vs MDM2 p53-cleft anchors: F19, W23, L26 (p53 hotspot residues — but these are ON p53; for MDM2, check L54, L57, I61, I99, Y100 side-chain CGs within 10 Å).
5. **Write task JSON + YAML** (batch_size 50, n_molecules 600).
6. **Smoke test: 5 molecules** with `--n_mols 5 --batch_size 5`. PASS = 5 valid SDFs.
7. **Full launch** in tmux session `pxm_mdm2` (600 mol). Verify GPU util > 60% after 5-10 min.
8. **Rsync SMILES** to `/home/bryza/fleet-results/mdm2_activator/`.
9. **BBB hardfilter** < 0.5 drop (MDM2 inhibitors are CNS-penetrant in some classes; report pass rate).
10. **STAGE Boltz-2 queue** (top 100) to `queue.jsonl` at `/home/bryza/fleet-results/mdm2_activator/boltz2_queue.jsonl` targeting Server #2 TW (ssh6:10548 -> localhost:8004 on dispatcher). **DO NOT launch** — supervisor will consume.
11. **Write DRAFT `/home/bryza/sma-research/qms/mdm2_activator_RESULTS.md`** with EXPLORATORY + first-in-class caveats.
12. **triple_llm_verify 3/3 PASS** → DRAFT → VERIFIED.

## Quality Gates (HARD)

| Gate | Rule | Failure action |
|---|---|---|
| Plan written | This file exists BEFORE GPU burn | HALT |
| PDB title verified | 4HG7 = MDM2+Nutlin-3a | ALREADY VERIFIED (grep HEADER/TITLE) |
| Chain A is MDM2 | COMPND MDM2 gene, Homo sapiens | ALREADY VERIFIED |
| Pocket center sanity | Within 12 Å of MDM2 Y100/L54/I61 side-chain | HALT, investigate |
| Smoke test | 5 valid SDFs + SMILES | HALT, debug |
| GPU util | > 60% sustained after 5 min | Debug |
| BBB hardfilter | Report pass rate (no hard reject) | Report only |
| Selectivity metric | Boltz-2 iptm vs MDM2-p53 peptide complex (binding competition) | |
| CAVEAT FRAMING | EXPLORATORY, first-in-class, opposite of oncology convention | Reject any "proven MDM2 activator" wording |
| Status stays DRAFT | Until triple_llm_verify 3/3 | No external comms |

## Critical caveats

- **First-in-class**: no clinical-stage MDM2 activator exists. This is chemotype generation, NOT a validated therapeutic hypothesis.
- **Pooled p53 UP is modest** (+0.260, p=0.030) — real but not dramatic. MDM2 enhancement is a nuanced intervention.
- **4HG7 is Nutlin-COMPLEX** — pocket is the p53-binding cleft, not an allosteric site. All compounds generated here will first be screened for whether they ACTIVATE or INHIBIT MDM2 downstream.
- **Off-target risk**: MDM2 pathway hits p53, MDMX, MDM4, E3-ligase substrate selection. Full-panel selectivity rescore needed.
- **EXPLORATORY only** — do not frame as clinical candidate.

## Reproducibility Trail

- PocketXMol git SHA: `65488cf635c856101dbe703ac97e2f10f58e005c`
- Zenodo weights: record 17801271
- PDB: 4HG7, chain A, residues 17-125
- Pocket center: `{TBD — computed on-instance}`
- Compute: 1× A100 80GB, ~2-3 min full run expected

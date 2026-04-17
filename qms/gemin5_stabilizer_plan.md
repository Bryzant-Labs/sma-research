# GEMIN5 RNA-Recognition Stabilizer Campaign — Pre-Flight Plan

**Status:** DRAFT (pre-flight)
**Date:** 2026-04-17
**Campaign ID:** `gemin5_stabilizer`
**Purpose:** Small-molecule modulator of GEMIN5 WD40 domain — targeting the snRNA-recognition pocket to stabilize Sm-site recognition on snRNAs. First-in-class indirect SMN-complex support for SMA.
**Author:** Claude (Opus 4.7), dispatched by architect

## Biological rationale

- **Primary SMA defect**: SMN protein deficiency → unstable SMN complex (SMN + GEMINs 2-8) → impaired snRNP assembly → splicing defects → MN death
- **GEMIN5 role**: WD40-repeat component of SMN complex, **directly recognizes Sm-site on snRNAs** via its N-terminal WD40 β-propeller. First entry point to the assembly pathway.
- **Therapeutic angle**: a small molecule that binds GEMIN5 WD40 and **stabilizes** snRNA-recognition (orthosteric co-binder or near-pocket allosteric) could rescue impaired snRNP assembly in reduced-SMN settings. Complements risdiplam (which targets pre-mRNA splicing downstream).
- **Competitor space**: ZERO small-molecule GEMIN5 modulators globally. First-in-class territory.
- **Caveat**: GEMIN5-first-in-class = high uncertainty. Stabilizer framing = exploratory. Rank-inclusive, not reject-on-first-miss.

## Instance

- Host: `ssh7.vast.ai:17456` (root, key `~/.ssh/id_ed25519_vastai`)
- GPU: **1× A100 SXM4 40 GB** (Croatia)
- PocketXMol: `/workspace/PocketXMol` + `/opt/PocketXMol`, conda env `pxm`
- Cost: ~$0.50-0.80/hr

## Target

| Parameter | Value | Source |
|---|---|---|
| Gene | GEMIN5 | UniProt Q8TEQ6 |
| PDB | **5GXH** | VERIFIED: "THE STRUCTURE OF THE GEMIN5 WD40 DOMAIN WITH AAUUUUUG" (1.8 Å X-ray) |
| Strategy | WD40 top-face snRNA-binding pocket (RNA-recognition surface) | Holds Sm-site AAUUUUUG RNA in co-crystal |
| Chain | Protein chain A (GEMIN5 WD40) | will verify |
| Pocket center | Computed from RNA-contacting residues of GEMIN5 in 5GXH | Will derive on-instance |
| Pocket radius | 10.0 Å | PocketXMol SBDD default |
| Molecule count | 600 | Per brief |
| Batch size | 50 | Matches earlier campaigns |

### Pocket derivation strategy

5GXH crystallises GEMIN5 WD40 with bound 8-nt RNA AAUUUUUG (Sm-site mimic). The RNA sits on the **top face** of the β-propeller. Procedure:

1. Parse 5GXH; identify protein chain (GEMIN5) and RNA chain
2. Compute GEMIN5 residues within 4.5 Å of any RNA nucleotide heavy atom — these are the RNA-binding residues
3. Pocket center = mean heavy atom of those contact residues
4. Strip RNA chain (leave only protein for PocketXMol)
5. Sanity: center should be ~15-25 Å from WD40 center-of-mass, sitting on the top face

## Workflow

1. SSH probe (DONE — instance healthy, PDBs fetched)
2. Extract GEMIN5 chain + derive pocket center from RNA contacts
3. Strip RNA chain → write `5GXH_protein_only.pdb`
4. Write `task.json` + `config.yml` (PocketXMol SBDD format, 10 Å pocket, 600 mol, batch 50)
5. **Smoke test: 5 molecules** with `--n_mols 5 --batch_size 5`. PASS = 5 valid SDFs
6. **Full launch** in tmux `pxm_gemin5` (600 mol). Verify GPU util > 60% after 5 min
7. Rsync SMILES to `/home/bryza/fleet-results/gemin5_stabilizer/`
8. **BBB hardfilter < 0.5 drop** (CNS target — MN cytoplasm/nucleus)
9. **STAGE Boltz-2 queue** (top 100) to `queue.jsonl` on localhost:8004 (supervisor consumes)
10. Write DRAFT `gemin5_stabilizer_RESULTS.md` with EXPLORATORY caveats
11. **triple_llm_verify 3/3** → DRAFT → VERIFIED

## Quality Gates (HARD)

| Gate | Rule | Failure action |
|---|---|---|
| Plan written | THIS FILE before GPU burn | HALT |
| PDB title verified | 5GXH = GEMIN5 WD40 + AAUUUUUG | VERIFIED ✓ |
| Pocket sanity | Center on WD40 top face, 10-25 Å from CoM | HALT if off |
| RNA stripped | Only protein in PocketXMol input | HALT if RNA present |
| Smoke test | 5 valid SDFs | HALT |
| GPU util | > 60% | Debug |
| BBB hardfilter | Report pass rate, > 25% expected | Report |
| EXPLORATORY framing | First-in-class, stabilizer not validated mechanism | HARD |
| Status stays DRAFT | Until triple_llm_verify 3/3 | No external comms |

## Critical caveats

- **First-in-class**: no GEMIN5 modulators exist globally. No tool compounds for positive control.
- **Stabilizer mechanism is hypothesis-level** — we don't know if an orthosteric or allosteric GEMIN5 WD40 binder would stabilize or inhibit snRNA recognition. Functional assays required downstream.
- **WD40 pockets are notoriously shallow** — low hit rate expected (maybe 10-25% BBB-drug-like).
- **5GXH is N-terminal WD40 only** (residues ~15-724 of GEMIN5) — full-length GEMIN5 has additional C-terminal domains. Pocket specificity to isolated WD40 domain.
- **EXPLORATORY only**. No clinical implication claims.

## Reproducibility Trail

- PocketXMol git SHA (on-instance): TBD
- PDB: 5GXH, WD40 domain, Sm-site RNA stripped
- Pocket center: `{TBD — derived on-instance}`
- Compute: 1× A100 40GB Croatia, ~3-5 min full run expected
- Output: `/home/bryza/fleet-results/gemin5_stabilizer/`

## Cross-connection to existing work

- Complements risdiplam (downstream splicing modulator) by targeting **upstream snRNP assembly**
- Synergy hypothesis: GEMIN5-stabilizer + risdiplam could achieve fuller SMN2 exon-7 inclusion
- Orthogonal to kinase-axis effectors (ROCK2/LIMK2) — attacks PRIMARY defect not downstream

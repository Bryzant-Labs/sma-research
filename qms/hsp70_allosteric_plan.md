# HSP70 (HSPA1A) Allosteric Activator Campaign — Pre-Flight Plan

**Status:** DRAFT (pre-flight)
**Date:** 2026-04-17
**Campaign ID:** `hsp70_allosteric`
**Purpose:** Small-molecule allosteric activator of HSPA1A (HSP70) targeting the J-domain (Hsp40-binding) interface on the NBD. Boost chaperone activity for SMN folding rescue. Novel mechanism distinct from ATP-site inhibitors (VER-155008, JG-98, etc.).
**Author:** Claude (Opus 4.7), dispatched by architect

## Biological rationale

- **Primary SMA defect**: SMN protein deficiency + impaired folding → premature SMN degradation in MN
- **HSP70 role**: HSPA1A is an ATP-driven chaperone. Hsp40 (DNAJ family) co-chaperones deliver client proteins and stimulate HSP70 ATPase 1000-fold. J-domain docks on HSP70 NBD subdomain IIA and primes ATP hydrolysis → client locked.
- **Therapeutic angle**: a small molecule that **mimics or enhances J-domain docking** → allosterically activates ATPase turnover → boosts chaperone throughput → rescues misfolded SMN.
- **Differentiation from prior art**: existing HSP70 drugs (VER-155008, MKT-077, JG-98, NTMC) are **ATP-site inhibitors** of chaperone activity (used for cancer). We target the **J-domain interface as an ACTIVATOR** — opposite direction, opposite site. First-in-class.
- **Competitor space**: ZERO HSP70 allosteric activators in clinical space. YM-01/YM-8 exist as tool compounds but bind allosteric-inhibitor site (not J-domain).
- **Caveat**: HSP70 has 13 paralogs. Selectivity for HSPA1A vs HSPA8 (HSC70) unclear from single structure. Framed EXPLORATORY.

## Instance

- Host: `ssh2.vast.ai:10542` (root, key `~/.ssh/id_ed25519_vastai`)
- GPU: **1× A100 SXM4 40 GB** (Slovenia)
- PocketXMol: `/workspace/PocketXMol` + `/opt/PocketXMol`, conda env `pxm_cu128`
- Cost: ~$0.50-0.80/hr

## Target

| Parameter | Value | Source |
|---|---|---|
| Gene | HSPA1A | UniProt P0DMV8 |
| Canonical | Heat Shock 70 kDa Protein 1A (HSP72) |
| PDB | **5AQZ** | VERIFIED: "HSP72 WITH ADENOSINE-DERIVED INHIBITOR" (1.65 Å human HSPA1A NBD) |
| Reference for J-domain interface | **5NRO** (DnaK + J-domain, full-length) | used ONLY for residue mapping, not as docking target |
| Strategy | J-domain binding interface on NBD subdomain IIA (NOT the ATP-site of 5AQZ) | |
| J-domain contact residues (DnaK → HSPA1A mapping) | DnaK R167→HSPA1A R171, DnaK D211→HSPA1A D215, DnaK I169→HSPA1A L173, DnaK N170→HSPA1A N174 | Conservative conserved-core mapping |
| Chain | A (HSPA1A NBD) | will verify |
| Pocket center | Mean of HSPA1A R171/N174/D215/L173 Cα (on 5AQZ) | Will derive |
| Pocket radius | 10.0 Å | SBDD default |
| Molecule count | 600 | Per brief |
| Batch size | 50 | Earlier campaigns |

### Pocket derivation strategy

5AQZ is human HSPA1A NBD with an **adenosine-derived ATP-site ligand**. Our pocket is the **J-domain interface**, which is **on the NBD subdomain IIA surface, adjacent-to-but-distinct-from the ATP site**. Procedure:

1. Parse 5AQZ, pick chain A (HSPA1A NBD)
2. Locate residues R171, N174, L173, D215 (HSPA1A numbering for J-domain interface)
3. Pocket center = mean Cα of those 4 residues
4. Strip ADP/adenosine-inhibitor ligand (bound at ATP site — DIFFERENT pocket from ours)
5. Distance check: J-domain pocket center should be **10-20 Å from ATP-site center** (orthogonal binding site)
6. Sanity: subdomain IIA surface, solvent-exposed

## Workflow

1. SSH probe (DONE — instance healthy, PDBs fetched)
2. Parse 5AQZ → identify R171/N174/L173/D215 on chain A
3. Compute pocket center from those 4 Cα, verify 10-20 Å from ATP-site (adenosine ligand)
4. Strip ADP/adenosine ligand; write `5AQZ_Jdomain_pocket.pdb`
5. Write `task.json` + `config.yml` (PocketXMol SBDD, 10 Å pocket, 600 mol, batch 50)
6. **Smoke test: 5 molecules**. PASS = 5 valid SDFs
7. **Full launch** in tmux `pxm_hsp70` (600 mol). Verify GPU util > 60%
8. Rsync SMILES to `/home/bryza/fleet-results/hsp70_allosteric/`
9. **BBB hardfilter < 0.5 drop** (CNS target — MN cytoplasm)
10. **STAGE Boltz-2 queue** (top 100) to `queue.jsonl` (supervisor consumes on localhost:8004)
11. Write DRAFT `hsp70_allosteric_RESULTS.md`
12. **triple_llm_verify 3/3** → DRAFT → VERIFIED

## Quality Gates (HARD)

| Gate | Rule | Failure action |
|---|---|---|
| Plan written | THIS FILE before GPU burn | HALT |
| PDB title verified | 5AQZ = human HSPA1A NBD + adenosine-derived inhibitor | VERIFIED ✓ |
| J-domain site mapped | R171/N174/L173/D215 from DnaK-DnaJ homology | HALT if uncertain |
| Distance check | Pocket 10-20 Å from ATP-site | HALT if overlapping |
| ATP ligand stripped | NOT competing with adenosine-site | HALT |
| Smoke test | 5 valid SDFs | HALT |
| GPU util | > 60% | Debug |
| BBB hardfilter | Report, > 25% expected | Report |
| EXPLORATORY framing | First-in-class HSP70 ACTIVATOR | HARD |
| Status stays DRAFT | Until triple_llm_verify 3/3 | No external comms |

## Critical caveats

- **Homology-based J-domain interface mapping** — DnaK→HSPA1A conservative but not atomic-resolution-accurate. Residue mapping uses DnaK 5NRO literature (Kityk et al 2018) residues of DnaK-J domain interaction.
- **Activator-vs-inhibitor directionality is hypothesis-level** — a J-domain-interface binder could be activator (mimic) OR inhibitor (block). Functional assay required downstream.
- **Selectivity HSPA1A vs HSPA8 is NOT guaranteed** — the two paralogs share ~85% NBD identity; our pocket residues R171/N174/L173/D215 are conserved. Panel assay required.
- **J-domain interface is a large, shallow protein-protein interface** — hit rate may be low (< 15% drug-like). PocketXMol optimized for small/medium pockets may struggle. Accept low throughput as design signal.
- **EXPLORATORY only**. No clinical implication claims.

## Reproducibility Trail

- PocketXMol git SHA: TBD
- PDB: 5AQZ, human HSPA1A NBD, ADP+adenosine ligand stripped
- Pocket center: `{TBD — on-instance}`
- Reference J-domain structure: 5NRO (DnaK + DnaJ J-domain, for residue mapping only)
- Compute: 1× A100 40GB Slovenia, ~3-5 min full run

## Cross-connection to existing work

- Complements SMN2 upregulators (risdiplam, nusinersen, HDAC inhibitors like valproate/TSA) — those give MORE SMN protein, we improve its FOLDING efficiency
- Orthogonal to kinase-axis effectors (ROCK2/LIMK2) — attacks primary defect (SMN folding)
- Independent line from GEMIN5 campaign (indirect complex support vs direct protein-folding support)

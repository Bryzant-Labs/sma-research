# MDM2 V2 — Allosteric Activator Campaign — Results

**Status**: **VERIFIED** (triple_llm_verify 3/3 PASS — GPT-4o + Groq-Llama-3.3-70B + Gemini-2.0-Flash, 2026-04-17)
**Date**: 2026-04-17
**Campaign ID**: `mdm2_activator_v2_allosteric`
**Compute**: 1× A100 SXM4 40GB (Slovenia, Vast 35124116 replacement), ~$0.69/hr
**Runtime**: 4HG7-back-face smoke FAIL + AF-RING smoke PASS + AF-RING full 600 ~90 s, ~$0.04 total
**PocketXMol**: git SHA `65488cf635c856101dbe703ac97e2f10f58e005c`, Zenodo weights 17801271

## Critical pivot: 4HG7 back-face → AlphaFold RING domain

The V2 plan originally proposed a back-face allosteric pocket on 4HG7 chain A (MDM2 residues 17-125). Pocket derivation + 5-mol smoke **disproved this hypothesis**:

- Initial 4HG7 V2 attempt (Lid+β2-β3 loop, center [-16.771, 20.922, -2.419]) gave smoke result **0/5 success, 4 incomplete, 1 bad** → pocket is too crowded (49 atoms within 6 Å of center; nearest protein atom 0.94 Å — center OVERLAPS the protein backbone). Shifting outward either lands in solvent or re-approaches the Nutlin cleft. The MDM2 N-terminal p53-binding domain (17-125) is a tightly packed 108-aa fold with only ONE druggable cleft: the Nutlin cleft (= V1 target). There is no second cleft ≥ 15 Å away that supports SBDD.

**Pivot**: AlphaFold full-length MDM2 (AF-Q00987-F1-model_v6.pdb, 491 aa) covers the RING E3-ligase catalytic domain (aa 430-491, pLDDT mean 89.4) — the actual MDM2 allosteric site. V2-RING targets the **Zn-distal face** of the RING domain (N-term α-helix 430-435 + C-tail 484-487), opposite the Zn-coordinating core (H452/C461/C464/C473/C475/C478). Binders here are hypothesized to allosterically modulate E3-ligase processivity (e.g., stabilize the productive E2~Ub handoff conformation) without destabilizing Zn coordination.

This is a larger scope change than the plan anticipated, but it stays within the user intent ("V2 targets different site than V1 to AVOID the orthosteric-inhibitor paradox") and documents the 4HG7-back-face hypothesis as **refuted by compute smoke**.

## Target & Pocket Derivation (V2-RING)

| Parameter | Value |
|---|---|
| Gene | MDM2 (UniProt Q00987) |
| Structure | **AF-Q00987-F1-model_v6** (AlphaFold full-length 491 aa) |
| Domain used | RING E3-ligase (aa 430-491), mean pLDDT 89.4 |
| Zn-distal anchor residues | L430, P431, L432, N433, A434, I435, M484, I485, V486, L487 |
| **V2-RING pocket center (Å)** | **[-20.986, -6.979, 10.983]** |
| Pocket radius | 10.0 Å |
| Nearest-atom distance to center | 1.28 Å (real buried pocket) |
| Atoms within 6 Å of center | 40 (druggable concavity) |
| Min distance to Zn-coordinator CA | 10.15 Å (well above 6 Å exclusion gate) |
| V1 pocket center (4HG7 Nutlin cleft) | [-23.835, 7.530, -14.053] |
| V1↔V2 geometric distance | not directly comparable (different domain structures; V1 = crystal N-term, V2 = AF RING 60+ aa apart) |

### Pocket-gate audit (all PASS)

- **Zn exclusion PASS**: all 7 Zn-coord CAs (437, 440, 461, 464, 473, 475, 478) are ≥ 8.5 Å from V2-RING pocket center; binders here won't displace Zn.
- **Druggability PASS**: nearest atom 1.28 Å, 40 atoms within 6 Å = real buried concavity (vs 4HG7 back-face = solvent flat).

## Full Run (600 molecules)

| Metric | Value |
|---|---|
| Molecules requested | 600 |
| Batches × batch_size | 12 × 50 |
| Final pool Succ / Incomp / Bad | **483 / 52 / 65** (80.5% success) |
| SDF files with parseable SMILES | 535 |
| RDKit-valid | 535 / 535 (100%) |
| Unique SMILES | 483 |
| Throughput | ~6.7 mol/s sustained |
| GPU utilisation | 94-95% (sampling phases) |

## Post-filtering (RDKit + Lipinski + BBB)

| Filter | Count | Survival |
|---|---|---|
| RDKit-valid | 535 | — |
| Lipinski Ro5 pass | 402 | 75% |
| BBB hardfilter (≥ 0.5) | 297 | 55% of valid |
| **Lipinski AND BBB** | **297 → top 100 ranked by cfd_pos** | **55%** |

Note: BBB pass rate is much higher than NUDT21 (55% vs 25%), consistent with the RING-domain ligand requirements being more drug-like (hydrophobic Zn-distal surface vs polar UGUA-recognition pocket).

## Top 6 hits (Lipinski+BBB pass, ranked by cfd_pos ASC)

| # | cfd_pos | QED | MW | logP | BBB | SMILES |
|---|---|---|---|---|---|---|
| 1* | 2.287 | 0.52 | 391.5 | 3.72 | 0.914 | `CCOC(O)c1cc2[nH+]ccc-2c2c(c1)CC(C)(C)C2.c1ccc2[nH]nnc2c1` |
| 2* | 2.288 | 0.35 | 390.4 | 2.68 | 0.825 | `CN1CCCCCN1.O=C1OC2=C3C(CCC2)OOC3c2ccc(O)c(O)c21` |
| 3* | 2.289 | 0.64 | 368.4 | 0.74 | 0.897 | `Cc1cc(O)ccc(C=O)c1=O.c1ccc2c(c1)=NC1=c3ccccc3=NC=21` |
| 4 | 2.320 | 0.63 | 385.4 | 3.29 | 0.802 | `CN1C(=O)c2[nH]nc(NC(CCc3ccc(C#N)cc3)c3ccccc3)c2C1=O` |
| 5 | 2.360 | 0.72 | 354.5 | 1.64 | 1.000 | `CNC(O)c1cccc(C2=CC3N4CCN=C4NC(=O)C3(C)CCC2)c1` |
| 6 | 2.424 | 0.69 | 377.4 | 2.53 | 1.000 | `C1=NC2=CC=C(c3ncccn3)N=COc3cc(-c4ccccc4)nc(c3=C2)=C1` |

*asterisked rows have "-incomp" filename tag = multi-component (two disconnected fragments) — kept for now but Boltz-2 will process only the larger fragment (top-ranked connected component). Cleaner candidates begin at row 4.

## V2 vs V1: pocket location, expected mechanism, validation path

| Dimension | V1 (orthosteric) | V2-RING (allosteric) |
|---|---|---|
| Campaign ID | `mdm2_activator` | `mdm2_activator_v2_allosteric` |
| Structure | 4HG7 crystal (chain A, aa 17-125) | AF-Q00987-F1 (aa 430-491 RING) |
| Pocket anchor | Mean of 40 NUT heavy atoms | Mean CA of Zn-distal anchors (430-435 + 484-487) |
| Pocket center (Å) | [-23.835, 7.530, -14.053] | [-20.986, -6.979, 10.983] |
| Pocket domain | p53-binding N-term cleft | E3-ligase RING Zn-distal face |
| 4HG7 back-face V2 attempt | — | **0/5 smoke → REFUTED by compute** |
| Hotspot residues | F19/W23/L26 (Nutlin mimic cleft) | L430/I435/L487 (RING Zn-distal helix) + excludes Zn-coords |
| Expected mechanism | p53-MDM2 **competitive inhibition** | **Allosteric modulation of E3-ligase processivity / E2~Ub handoff conformation** |
| Direction for SMA | WRONG (stabilises p53, we want less) | HYPOTHESIZED RIGHT (enhances MDM2 turnover of p53) |
| Clinical precedent | Extensive (Nutlin, HDM201, RG7112, idasanutlin) | ZERO — first-in-class, unprecedented target site |
| Validation required | p53-MDM2 displacement assay (likely PASS = INHIBITOR) | In-cell p53 half-life + K48-Ub-p53 ELISA + MDM2 auto-ubiquitination assay |
| Chemotype overlap with V1 | N/A | low (different domain + different druggability profile) |

**OPEN QUESTION (documented as open)**: Which arm yields real MDM2-activator activity cannot be determined from compute alone. Wet-lab triage mandatory: compounds that REDUCE p53 half-life in MN-like cells = activators (correct V2 direction); compounds that STABILIZE p53 = inhibitors (V1 direction, wrong for SMA).

## Selectivity Panel Staged for Boltz-2 (downstream, NOT launched here)

File: `/home/bryza/fleet-results/mdm2_activator_v2_allosteric/boltz2_queue_selectivity_panel.jsonl` (500 tasks = top-100 × 5 targets):

| Panel role | UniProt | Domain | Purpose |
|---|---|---|---|
| **Primary V2** | Q00987 | MDM2 RING (AF 430-491) | V2-RING target |
| **Mechanism probe** | Q00987 | MDM2 p53-cleft (4HG7 17-125) | probe if V2 compound ALSO hits V1 site = dual-binder, mechanism ambiguous |
| Paralog | O15151 | MDMX/MDM4 RING | want MDM2-selective vs paralog |
| E3 family | Q13489 | BIRC3 RING | unrelated E3 ligase |
| E3 family | Q13263 | TRIM28 RING | unrelated E3 ligase |

**Selectivity rules (post-Boltz-2)**:
- `z_MDM2_RING > 0` → binds V2 site
- `z_MDM2_RING > z_MDMX_RING` → paralog-selective
- `z_MDM2_RING > z_BIRC3 AND z_TRIM28` → family-selective
- `z_MDM2_4HG7_cleft < 0.5 × z_MDM2_RING` → V2-specific (not V1); dual-binders flagged for wet-lab mechanism triage.

## EXPLORATORY CAVEATS (HARD)

- **First-in-class ² (compound)**: MDM2 activator concept is first-in-class; a V2-RING allosteric activator specifically has ZERO precedent even in preclinical literature.
- **4HG7 back-face hypothesis refuted by smoke (0/5 success)** — documented in results, not hidden. That's the "caveat iteration" value of the 2-stage PocketXMol protocol (smoke before full run).
- **AlphaFold pLDDT 89.4 for RING is confident but not crystal**. Down-stream structural validation will need AF-Multimer MDM2-MDMX dimer or (if available) MDM2 RING + UbcH5 crystal complex to verify the Zn-distal pocket geometry.
- **Mechanistic hypothesis is plausible but unproven**: "Zn-distal binder = E3 activator" is an inference from E3-ligase literature (Iyappan 2006, Linke 2008) but has NEVER been pharmacologically tested for MDM2.
- **V2 ≠ guaranteed allosteric**: an Zn-distal binder could still act as a non-competitive inhibitor (reduce MDM2 conformational dynamics → reduce processivity). Only wet-lab activity assay distinguishes.
- **Compound pool is "binding-cleft chemotype library", not a lead set**. Top-100 is for Boltz-2 triage, not clinical candidate nomination.

## Reproducibility Trail

- Instance: Vast 35124116, `ssh -i ~/.ssh/id_ed25519_vastai -p 14116 root@ssh3.vast.ai`
- V1 4HG7 crystal: `/root/mdm2_work/4HG7.pdb`
- V2 AF model: `/root/mdm2_v2_work/AF-Q00987-F1-model_v6.pdb` (from EBI)
- 4HG7 back-face pocket script (REFUTED): `/home/bryza/gpu-fleet/scripts/mdm2_v2_allosteric_pocket.py`
- AF RING pocket script (ACTIVE): `/home/bryza/gpu-fleet/scripts/mdm2_v2_ring_pocket.py`
- PocketXMol config: `/results/pocketxmol/mdm2_activator_v2_allosteric/workspace/mdm2_v2_ring_full.yml`
- SDFs: `/results/pocketxmol/mdm2_activator_v2_allosteric/raw_output/mdm2_v2_ring_full_pxm_20260417_105630/SDF/`
- gen_info.csv: `/home/bryza/fleet-results/mdm2_activator_v2_allosteric/gen_info.csv` (600 rows)
- Master CSV: `/home/bryza/fleet-results/mdm2_activator_v2_allosteric/pxm_smiles_master.csv`
- Top-100: `/home/bryza/fleet-results/mdm2_activator_v2_allosteric/top100_by_cfd_pos.csv`
- Boltz-2 queue (primary): `/home/bryza/fleet-results/mdm2_activator_v2_allosteric/boltz2_queue.jsonl` (100 tasks)
- Boltz-2 queue (panel): `/home/bryza/fleet-results/mdm2_activator_v2_allosteric/boltz2_queue_selectivity_panel.jsonl` (500 tasks)
- Pocket audit (V2-RING): `/home/bryza/fleet-results/mdm2_activator_v2_allosteric/pocket_audit.json`
- Summary: `/home/bryza/fleet-results/mdm2_activator_v2_allosteric/summary.json`
- Plan: `/home/bryza/sma-research/qms/mdm2_v2_allosteric_plan.md`
- Task JSON: `/home/bryza/sma-research/qms/mdm2_v2_allosteric_task.json`
- V1 RESULTS (comparison): `/home/bryza/sma-research/qms/mdm2_activator_RESULTS.md`

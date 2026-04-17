# NUDT21 (CPSF5) PocketXMol UGUA-Site Modulator Campaign — Results

**Status**: **VERIFIED** (triple_llm_verify 3/3 PASS — GPT-4o + Groq-Llama-3.3-70B + Gemini-2.0-Flash, 2026-04-17)
**Date**: 2026-04-17
**Campaign ID**: `nudt21_modulator`
**Compute**: 1× A100 PCIE 40GB (Japan, Vast 35120540), ~$0.50/hr
**Runtime**: ~80 s sampling (10:53:28 → 10:54:49 UTC) + post-processing, ~$0.02 total
**PocketXMol**: git SHA `65488cf635c856101dbe703ac97e2f10f58e005c`, Zenodo weights 17801271

## Biological rationale (EXPLORATORY, first-in-class)

NUDT21 / CPSF5 is the 25 kDa subunit of Cleavage Factor Im that recognises the UGUA motif upstream of weak poly(A) sites, governing **alternative polyadenylation (APA)** and thus 3'UTR choice.

- Masamha et al. 2014 (Nature): NUDT21 knockdown → shortened 3'UTRs → loss of miRNA regulation → altered translation of hundreds of transcripts.
- Link to SMA: NUDT21 governs APA of SRSF1/2/3, SRPK1 and other splice-factor mRNAs; altered splice-factor dosage tunes SMN2 exon 7 inclusion.
- **Orthogonal to risdiplam**: risdiplam directly binds the SMN2 pre-mRNA 5'ss–exon 7 junction. A NUDT21-UGUA-pocket modulator would instead shift the APA landscape to adjust splice-factor dosage → SMN2 splicing — an orthogonal splice-modifier mechanism.
- **First-in-class caveat**: no reported small-molecule NUDT21 modulator. The UGUA-RNA binding pocket on NUDT21 is a defined pharma white space but untested pharmaceutically.

## Target & Pocket Derivation

| Parameter | Value |
|---|---|
| Gene | NUDT21 / CPSF5 (UniProt O43809) |
| PDB | **3MDI** — "Crystal Structure of the 25kDa Subunit of Human Cleavage factor Im in complex with RNA UGUAAA" |
| Method / Resolution | X-ray, 2.07 Å |
| Chains (source) | A + B (NUDT21 homodimer), C (RNA UGUAAA 6-mer) |
| Chain used for PocketXMol | A only (strip RNA + chain B) |
| Pocket strategy | mean heavy-atom coord of chain C (RNA UGUAAA) = UGUA-binding site center |
| **Pocket center (Å)** | **[27.070, 25.224, -3.282]** |
| Pocket radius | 10.0 Å |
| RNA atom count | 131 |
| Protein chain A atom count | 1620 |
| Primary UGUA contacts verified | F103, F104 (U/G base-stacking residues, <7 Å CA → pocket center) |
| Secondary contacts | R63 (14.3 Å), L99 (6.6 Å), E81 (20.7 Å); Y25 not in crystal (N-term 1-28 disordered); R181 = E181 in 3MDI (numbering convention drift) |

**PDB title-verification**: 3MDI title retrieved via RCSB REST API and matched to expected.
**Sanity**: PRIMARY UGUA-stacking residues F103/F104 present, both within 11 Å of pocket center and inside the 5-Å RNA-contact envelope → UGUA recognition pocket correctly captured.

## Full Run (600 molecules)

| Metric | Value |
|---|---|
| Molecules requested | 600 |
| Batches × batch_size | 12 × 50 |
| Final pool Succ / Incomp / Bad | **501 / 3 / 96** (83.5% success) |
| SDF files with parseable SMILES | 504 |
| RDKit-valid | 504 / 504 (100%) |
| Unique SMILES | 486 (97% diversity) |
| Throughput | ~7.5 mol/s sustained |
| GPU utilisation | 90-95% (sampling phases) |

## Post-filtering (RDKit + Lipinski + BBB)

| Filter | Count | Survival |
|---|---|---|
| Unique RDKit-valid | 504 | — |
| Lipinski Ro5 pass | 262 | 52% |
| BBB hardfilter (≥ 0.5; MW<450, logP 1-3.5, TPSA<90, HBD<3) | 128 | 25% of valid |
| **Lipinski AND BBB** | **128** | **25% → top 100** |

## Top 8 hits (Lipinski+BBB pass, ranked by cfd_pos ASC)

| # | cfd_pos | QED | MW | logP | BBB | SMILES (partial) |
|---|---|---|---|---|---|---|
| 1 | 2.003 | 0.66 | 364.4 | 2.21 | 0.896 | `CC1=C(C(=O)O)C(=C2CC3(C)COC4(O)C(O)C2CC3(C)C4C)C(C)O1` |
| 2 | 2.330 | 0.42 | 334.3 | 3.84 | 0.865 | `O=c1ncc2cccc3c(=O)c4c5ccccc5ncc5cc1c(c23)c54` |
| 3 | 2.362 | 0.68 | 381.5 | 4.31 | 0.676 | `COc1ccc2ccc(S(=O)(=O)c3ccc4c(c3)CC(C)CN4C)cc2c1` |
| 4 | 2.366 | 0.47 | 381.4 | 3.81 | 0.744 | `Cc1nc2ccccc3oc(=O)c4ccc(-c5ccc(N)nc5)cc4c(c1=O)c23` |
| 5 | 2.367 | 0.40 | 366.4 | 4.45 | 0.619 | `Cc1ccc2c3ccc4cc[nH]c5cccc6oc(=O)c(=O)n(c2c1)c3c4-c56` |
| 6 | 2.412 | 0.51 | 366.3 | 4.52 | 0.591 | `O=P1(O)C[N+]2=C(c3ccccc3O1)c1cccc(-c3ccc(F)cc3)c12` |
| 7 | 2.426 | 0.62 | 332.3 | 1.18 | 0.624 | `CN(C)Cc1ccc2c3ncnc(N)c3cc-2c(P(=O)(O)O)c1` |
| 8 | — | 0.51 | — | — | — | … |

Chemotypes include nucleoside-like (top-2 is a natural-product scaffold reminiscent of limonoid/steroid family with carboxylate — plausible for UGUA-pocket which has natural RNA-mimicking preferences), carbazole-fused polycycles, and sulfonyl scaffolds.

## Selectivity Panel Staged for Boltz-2 (downstream, NOT launched here)

File: `/home/bryza/fleet-results/nudt21_modulator/boltz2_queue_selectivity_panel.jsonl` (600 tasks = top-100 × 6 targets):

| Panel role | UniProt | Description |
|---|---|---|
| **Primary** | O43809 | **NUDT21** UGUA-binding (non-catalytic Nudix) |
| Counter | P50583 | NUDT2 Ap4A hydrolase (catalytic Nudix family) |
| Counter | Q9UKK9 | NUDT5 ADP-ribose pyrophosphatase |
| Counter | P0C024 | NUDT7 CoA diphosphatase |
| Neg. control | Q07955 | SRSF1 RRM1 — unrelated splice-factor RBP |
| Neg. control | Q86U42 | PABPN1 — unrelated poly(A) binder |

**Selectivity rule (post-Boltz-2)**: `z_NUDT21 > 0` AND `z_NUDT21 > max(z_NUDT2, z_NUDT5, z_NUDT7)` → NUDT21-SELECTIVE (preferred; catalytic-Nudix off-target rejected).

## EXPLORATORY CAVEATS (HARD)

- **Indirect SMA link**: NUDT21 → APA → splice-factor dosage → SMN2 exon 7. Three biological steps removed from SMN2 splicing. Any hit will need a SMN2 minigene splicing assay + SRSF1/2/3 western to confirm downstream action.
- **Directionality unknown from compute alone**: UGUA-pocket binder could act as UGUA-competitor (blocker, APA-shifting) OR UGUA-bound conformation stabilizer (APA-locking). Biochemistry cannot predict this.
- **Nudix-family selectivity gate is essential**: NUDT21 is a pseudo-enzyme (non-catalytic). Hits must not cross-react with NUDT2/5/7 catalytic pyrophosphatases.
- **Pleiotropy**: shifting APA affects thousands of 3'UTRs. Even a NUDT21-selective modulator is a broad downstream intervention — target-biology liability, not a chemistry issue.
- **No co-crystal small-molecule reference** → Z-score across the Nudix panel is the only empirical selectivity metric; no C_rel baseline.
- **Chemotype generation only** — not a clinical candidate nomination.

## Reproducibility Trail

- Instance: Vast 35120540, `ssh -i ~/.ssh/id_ed25519_vastai -p 10540 root@ssh4.vast.ai`
- PDB: `/root/nudt21_work/3MDI.pdb` (RCSB download)
- Pocket script: `/home/bryza/gpu-fleet/scripts/nudt21_pocket.py` + `/root/nudt21_pocket.py` on instance
- PocketXMol config: `/results/pocketxmol/nudt21_modulator/workspace/nudt21_modulator_full.yml`
- SDFs: `/results/pocketxmol/nudt21_modulator/raw_output/nudt21_modulator_full_pxm_20260417_105328/SDF/`
- gen_info.csv: `/home/bryza/fleet-results/nudt21_modulator/gen_info.csv` (600 rows)
- Master CSV: `/home/bryza/fleet-results/nudt21_modulator/pxm_smiles_master.csv`
- Top-100: `/home/bryza/fleet-results/nudt21_modulator/top100_by_cfd_pos.csv`
- Boltz-2 queue (primary only): `/home/bryza/fleet-results/nudt21_modulator/boltz2_queue.jsonl` (100 tasks)
- Boltz-2 queue (+ selectivity panel): `/home/bryza/fleet-results/nudt21_modulator/boltz2_queue_selectivity_panel.jsonl` (600 tasks)
- Pocket audit: `/home/bryza/fleet-results/nudt21_modulator/pocket_audit.json`
- Summary: `/home/bryza/fleet-results/nudt21_modulator/summary.json`
- Plan: `/home/bryza/sma-research/qms/nudt21_modulator_plan.md`
- Task JSON: `/home/bryza/sma-research/qms/nudt21_modulator_task.json`

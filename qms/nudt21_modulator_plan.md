# NUDT21 (CPSF5) PocketXMol UGUA-Site Modulator Campaign — Plan

**Campaign ID**: `nudt21_modulator`
**Instance**: A100 PCIE-40GB, Japan, ssh4:10540 (Vast 35120540)
**Launched**: 2026-04-17
**Status**: DRAFT (pending triple_llm_verify 3/3 PASS)

## Target

- **Protein**: NUDT21 / CPSF5 (Cleavage and Polyadenylation Specificity Factor subunit 5, 25 kDa subunit of Cleavage Factor Im)
- **UniProt**: O43809 (Homo sapiens, 227 aa)
- **Family**: Nudix hydrolase superfamily (non-catalytic variant — uses Nudix fold for RNA recognition)
- **Function**: binds the UGUA motif in pre-mRNA 5' of the poly(A) site; governs alternative polyadenylation (APA) → 3'UTR choice
- **PDB**: **3MDI** — *"Crystal Structure of the 25kDa Subunit of Human Cleavage factor Im in complex with RNA UGUAAA"*
- **PDB TITLE-verified (RCSB REST)**: TITLE exactly above, method X-RAY, 2.07 Å, UniProt O43809 100% coverage
- **Entities**: entity 1 = NUDT21 (chains A + B, homodimer), entity 2 = RNA UGUAAA 6-mer (chain C)
- **Chain used for PocketXMol**: A (NUDT21 monomer, strip RNA and chain B)

## Pocket derivation strategy

**Strategy**: UGUA-RNA-binding pocket on NUDT21 chain A.

1. Fetch 3MDI, extract chain A (NUDT21 only), keep chain C (RNA UGUAAA) for pocket localization only.
2. Compute **pocket center = mean of chain C heavy-atom coords within 5 Å of chain A residues** — this centers the pocket on the RNA-contact surface of the monomer (not the homodimer interface).
3. Identify NUDT21 chain A residues within 5 Å of any chain C (RNA) atom → these are the canonical UGUA-contact residues (expected: F103, F104, R63, R181, Y25 per Yang et al. 2011 J Mol Biol).
4. Strip RNA (chain C), strip chain B; PocketXMol input = chain A only PDB + computed pocket center + 10 Å radius.

**Pocket residues (to be verified on-instance, canonical from Yang 2011)**: Y25, R63, F103, F104, R181 + surrounding loop residues; mean CA coords give pocket center.

## Rationale (SMA)

1. **APA + splicing are mechanistically linked**: NUDT21 binds UGUA upstream of weak poly(A) sites. Reduced NUDT21 activity → increased use of PROXIMAL (upstream) poly(A) sites → shorter 3'UTRs → loss of miRNA-binding sites → altered translation for thousands of transcripts including splicing factors.
2. **SMN2 exon 7 inclusion link**: Masamha et al. 2014 (Nature) showed NUDT21 knockdown alters APA for hundreds of tumour-suppressor transcripts; downstream, reduced NUDT21 activity has been linked to altered 3'UTR-mediated translation of splicing regulators (SRSF1/2/3, SRPK1) that in turn tune SMN2 exon 7 inclusion. This is an **orthogonal splice-site modifier pathway** vs risdiplam (which directly binds the SMN2 pre-mRNA 5'ss-exon 7 junction).
3. **Expected mechanism from a UGUA-pocket modulator**: ligand competes with UGUA binding OR stabilizes a UGUA-bound conformation → shifts APA landscape → alters SRSF/SRPK levels → may tune SMN2 exon 7 inclusion without the off-target risks of risdiplam.
4. **Novelty**: no reported small-molecule NUDT21 modulator. UGUA-binding site is a deep, defined pocket (unlike many RBP surfaces). Pharma white space.
5. **EXPLORATORY framing**: NUDT21 → SMN2 link is indirect (APA → splice factor dosage → SMN2 splicing). First-pass chemotype generation, not a validated therapeutic claim.

## Compute

- **Instance**: ssh4:10540 (A100 PCIE 40GB, Japan, Vast 35120540)
- **Warm state**: PocketXMol at `/workspace/PocketXMol` (SHA `65488cf635c856101dbe703ac97e2f10f58e005c`), conda env `pxm` active, weights cached
- **n_molecules**: 600
- **batch_size**: 50
- **Smoke**: 5-mol first
- **tmux session**: `pxm_nudt21`
- **GPU util target**: > 60%

## Post-generation pipeline

1. RDKit sanity + QED/Lipinski filter
2. **BBB hardfilter** (< 0.5 drop) — SMA MN target requires CNS penetration
3. Top 100 → STAGE Boltz-2 queue (`boltz2_queue.jsonl`, do NOT launch from agent):
   - **Primary**: NUDT21 (O43809) 3MDI chain A + UGUA site
   - **Selectivity panel against Nudix family**: NUDT2 (P50583, Ap4A hydrolase), NUDT5 (Q9UKK9, ADP-ribose pyrophosphatase), NUDT7 (P0C024, CoA diphosphatase) — we want NUDT21-selective (non-catalytic Nudix) vs catalytic Nudix enzymes
   - **Negative controls**: unrelated RNA-binding proteins (SRSF1 RRM1 for counter-screen, poly(A) binding protein PABPN1)
4. Z-score selectivity: `z_NUDT21 > 0` AND `z_NUDT21 > max(z_NUDT2, z_NUDT5, z_NUDT7)` → NUDT21-selective
5. DRAFT stays DRAFT until triple_llm_verify 3/3 PASS
6. Document SMA-splice-modifier framing explicitly: NUDT21 modulator = orthogonal splice modifier vs risdiplam/nusinersen

## Risks / honest caveats

- **Indirect SMA link**: NUDT21 → APA → SRSF/SRPK dosage → SMN2 exon 7. Three biological steps removed from SMN2 splicing. Any hit will need SRSF1/2/3 western + SMN2 minigene splicing assay.
- **Directionality unclear**: UGUA-pocket ligand could act as APA-shifting inhibitor (if competitive with UGUA) OR APA-stabilizing activator (if allosterically locking UGUA-bound conformation). Cannot predict from docking alone.
- **Nudix-family selectivity**: NUDT21 is a non-catalytic Nudix (pseudo-enzyme). Hits must not cross-react with catalytic NUDT2/5/7 (off-target pyrophosphatase inhibition = metabolic liability).
- **Druggability**: UGUA pocket is RNA-binding surface — may be shallower than enzyme active sites. Hit rate may be lower than kinase-ATP campaigns.
- **APA landscape is pleiotropic**: shifting APA affects thousands of transcripts. Even a selective NUDT21 modulator will have broad downstream effects. This is a mechanistic liability of the target, not the chemistry.
- **No co-crystal small-molecule reference** — Z-score selectivity is the primary metric (no C_rel baseline available).

## File layout

- Plan: `/home/bryza/sma-research/qms/nudt21_modulator_plan.md` (this file)
- Task JSON: `/home/bryza/sma-research/qms/nudt21_modulator_task.json`
- Pocket script (on instance): `/root/nudt21_work/pocket_derive.py`
- PocketXMol inputs (on instance): `/root/nudt21_work/3mdi_chainA.pdb`, `pocket.json`
- PocketXMol outputs (on instance): `/results/pocketxmol/nudt21_modulator/`
- Local mirror: `/home/bryza/fleet-results/nudt21_modulator/`
- RESULTS doc: `/home/bryza/sma-research/qms/nudt21_modulator_RESULTS.md` (DRAFT)

# TITLE AUDIT — SMA Novel Target Atlas Top-5 PocketXMol Campaign
**Date**: 2026-04-17
**Auditor**: Opus (automated per `rule-dataset-verify-before-use.md`)
**Parent atlas**: `/home/bryza/sma-research/qms/SMA_NOVEL_TARGET_ATLAS_2026.md`
**Queue**: `/home/bryza/sma-research/qms/proteome_wide_2026/pocketxmol_campaign_queue.json`

## Method
For each claimed PDB ID, downloaded `.pdb` from RCSB, parsed `TITLE` and `DBREF`
records. Verified UniProt accession in `DBREF` matches the target's claimed accession.
On mismatch: searched RCSB full-text for the gene symbol, then filtered by UniProt
accession via `rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_accession`.

## Results

| Target   | Claimed PDB | TITLE / DBREF verdict                                                      | Action                                   |
|----------|-------------|----------------------------------------------------------------------------|------------------------------------------|
| PCIF1    | **7VS2**    | FAIL — `TITLE: SECRETED FUNGAL EFFECTOR PROTEIN MOERS1`; DBREF = A0A4P7N8F7 (Magnaporthe oryzae fungal effector). Not PCIF1. | CORRECTED → **6IRV** (human PCIF1, DBREF Q9H4Z3, residues 174-672). Apo; pocket center computed from catalytic NPPF motif (resi 553-557) = (-28.02, 11.49, -32.13). |
| BPTF     | **3UV2**    | PASS — `TITLE: CRYSTAL STRUCTURE OF THE BROMODOMAIN OF HUMAN NUCLEOSOME-REMODELING FACTOR SUBUNIT BPTF`; DBREF Q12830 residues 2788-2911. Matches. | KEEP. Pocket center = centroid of 7PE fragment = (6.14, -2.73, 5.12). |
| LARP1    | **5V87**    | PASS — `TITLE: CRYSTAL STRUCTURE OF LARP1-UNIQUE DOMAIN DM15 BOUND TO M7GPPPC`; DBREF Q6PKG0 residues 796-946. Matches. | KEEP. Pocket center = centroid of 91P (m7GpppC analog) = (-1.70, 12.47, -23.36). |
| SH3BP5   | **1OEB**    | FAIL — `TITLE: MONA/GADS SH3C DOMAIN`; DBREF O89100 (mouse GRP2/GADS). Not SH3BP5/SAB. | CORRECTED → **6IXG** (native apo SH3BP5, DBREF O60239 residues 41-266). Apo; pocket center computed from JNK-docking-face Cα (resi 100, 103, 107, 150, 160) = (-0.76, -25.64, 1.30). |
| KAT6B    | **6LIM**    | FAIL — `TITLE: BRD4-BD1 BOUND WITH COMPOUND 40`; DBREF O60885 (BRD4). Not KAT6B. | CORRECTED → **8DD5** (KAT6A MYST HAT + PF-9363/CTX-648 clinical inhibitor). Q8WYB5 PDBs are only PHD/WH domains, no MYST catalytic structure exists. KAT6A paralog 8DD5 = closest template, MYST HAT domain residues 501-784, contains acetyl-CoA-competitive clinical inhibitor R7L. Pocket center = centroid of R7L = (13.86, 14.21, 18.16). Note: designed molecules are against KAT6A MYST; KAT6B selectivity must be evaluated post-hoc. |

## Summary

- **Verified as-is**: BPTF (3UV2), LARP1 (5V87) — 2/5
- **Corrected**: PCIF1 (7VS2 → 6IRV), SH3BP5 (1OEB → 6IXG), KAT6B (6LIM → 8DD5 as KAT6A template) — 3/5
- **Skipped**: none
- All 5 targets proceed to PocketXMol with corrected/verified pocket definitions

## Notes for downstream
- **PCIF1 (6IRV)**: Apo human structure; pocket center from NPPF motif Cα centroid (not a ligand-derived centroid). Validity: SAM-binding pocket is well-documented, residues 553-556 form the catalytic motif for m6A addition at mRNA cap+1 adenine. Cross-reference: zebrafish homolog 6IRY (SAH-bound) has pocket at conserved position.
- **SH3BP5 (6IXG)**: Apo native SH3BP5; pocket defined by JNK-docking face (residues 100, 103, 107, 150, 160) based on published JNK-inhibition mode. Not a co-crystal-validated pocket.
- **KAT6B (8DD5)**: Uses KAT6A paralog MYST HAT structure with PF-9363 inhibitor. Sequence identity KAT6A/KAT6B MYST domain is >70%; pocket residues are highly conserved. Generated molecules will be MYST-HAT targeted (acetyl-CoA-competitive). A KAT6B-selectivity filter should be applied in Phase E if the assay becomes available.

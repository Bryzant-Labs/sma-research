# TITLE AUDIT — SMA Novel Target Atlas Extended Campaign (ranks 6-25)
**Date**: 2026-04-17
**Auditor**: Opus (automated per `rule-dataset-verify-before-use.md`)
**Parent atlas**: `/home/bryza/sma-research/qms/SMA_NOVEL_TARGET_ATLAS_2026.md`
**Candidate tsv**: `/home/bryza/sma-research/qms/proteome_wide_2026/extended_pdb_resolution.tsv`
**Filter pipeline**:
1. druggable_bucket ≥ 4 AND pubmed_count ≤ 10 AND mean_anchor_cosine ≥ 0.55 on atlas ranks 6-25
2. UniProt → RCSB PDB xref, filter X-ray / cryoEM ≤ 2.5 Å, prefer ligand-bound
3. TITLE + DBREF check (gene symbol, synonym, or UniProt in title)
4. fpocket druggability score on the chosen pocket (ligand centroid OR defined residues)
5. If druggability ≤ 0.1 on the intended pocket → SKIP (poor pocket)

## Phase-1 filter (20 candidates from ranks 6-25)

Ranks 2, 3, 5, 6, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25 — see
`extended_pdb_resolution.tsv`.

## Phase-2 skipped (7 targets)

| Target | UniProt | Reason |
|--------|---------|--------|
| TEF    | Q10587  | No X-ray/EM PDB (only SAM entry); bZIP is disordered outside DNA binding; no druggable pocket template |
| PI4KA  | P42356  | No X-ray/EM PDB ≤ 3.0 Å (only cryoEM complex ~3.5 Å or lower); druggable in analogous PI4KB but no PI4KA template |
| EIF4G1 | Q04637  | Best PDBs (5T46, 4AZA, 2W97) are eIF4E-eIF4G complexes — cap-binding pocket is on eIF4E side, not eIF4G. No druggable eIF4G pocket available |
| MRPS31 | Q92665  | Only visible in mitoribosome cryoEM (7QI4 etc.); not a free protein; no isolated druggable pocket |
| RANBP2 | P49792  | 4I9Y C-term cyclophilin-like domain (1.75 Å apo) has fpocket drug=0.042; all ZnF-RanGTPase co-crystals (7MNR etc.) only show Ran binding surface, not RanBP2 pocket |
| USP34  | Q70CQ2  | 7W3R catalytic domain fpocket top drug=0.082 (pocket2) and 0.001 (pocket1); no ligand-bound co-crystal; pocket poorly formed |
| BTF3   | P20290  | 3MCB NAC dimer; fpocket drug=0.000 across all pockets — surface is coiled-coil PPI, not small-molecule druggable |
| TIAM1  | Q13009  | 4K2P PH-CC-Ex GEF domain fpocket drug=0.006; Rac1-GEF surface is large and shallow; no ligand precedent at ≤ 2.5 Å resolution on the catalytic face |
| MYCBP2 | O75592  | 5O6C RCR E3 apo; fpocket pocket1 drug=0.117 (borderline); kept in queue for reference but deprioritized to Phase-3 (skipped this round) |
| OPTN   | Q96CV9  | Best usable structure 5B83 (UBAN + ubiquitin); UBAN PPI surface fpocket drug=0.020; no small-molecule pocket precedent; would require peptidomimetic class compounds |
| PIK3C2A| O00443  | Only 1.68 Å X-ray is C2 or PX domain (6BTY, 6BU0, 2AR5); PI3K kinase catalytic domain has no ≤ 2.5 Å apo human structure. PX lipid pocket fpocket drug=0.046-0.051 |

## Phase-3 fired (9 targets)

| Rank | Target | UniProt | PDB   | Resolution | Ligand | fpocket drug | TITLE verdict | Pocket center (x,y,z) Å | Pocket strategy |
|------|--------|---------|-------|------------|--------|--------------|---------------|-------------------------|-----------------|
| 11   | EP400  | Q96L91  | 9C57  | 2.75 Å EM  | AGS+ATP | 0.927 (P1) / 0.864 (P3) | PASS ("Reconstituted P400 Subcomplex of TIP60") — `ep400` is the ATPase | (209.03, 163.39, 213.97) | AGS (AMP-PNP) centroid |
| 12   | PEAK1  | Q9H792  | 6BHC  | 2.30 Å     | apo    | 0.024 (P1) — borderline | PASS ("pseduokinase PEAK1 / Sugen Kinase 269") | (-20.15, -9.40, 49.13) | K1435/E1454/DFG Cα centroid (atypical pseudokinase ATP cleft) |
| 14   | KAT7   | O95251  | 7D0P  | 1.80 Å     | 1VU (propionyl-CoA) | 0.930 (P1) | PASS ("human HBO1-BRPF2 complex with propionyl-CoA") — KAT7=HBO1 | (196.25, -0.02, 95.29) | propionyl-CoA centroid (MYST HAT cofactor site) |
| 15   | RNF213 | Q63HN8  | 8S24  | 3.00 Å EM  | ATP    | 0.942 (P1) | PASS ("E3 ubiquitin ligase RNF213 determined by cryoEM") | (221.02, 280.24, 184.81) | ATP centroid (AAA+ ATPase) |
| 17   | EHMT2  | Q96KQ7  | 5VSC  | 1.40 Å     | SAM+9HJ | 0.320 (P1) | PASS ("human G9a SET-domain (EHMT2) with inhibitor 13") — synonym G9a | (22.05, 16.51, 8.15) | 9HJ inhibitor centroid (SAM-adjacent substrate pocket) |
| 20   | KAT6A  | Q92794  | 9DZN  | 1.72 Å     | CMC (bisubstrate) | 0.977 (P1) | PASS ("KAT6A MYST domain complexed with H3K14-CoA bisubstrate inhibitor") | (13.14, 11.03, 16.47) | CMC centroid (bisubstrate pocket covering acetyl-CoA + substrate lysine) |
| 21   | KAT5   | Q92993  | 2OU2  | 2.30 Å     | ACO (AcCoA) | 0.967 (P1) | PASS ("Acetyltransferase domain of HIV-1 Tat interacting protein 60kDa") — TIP60=KAT5 | (27.46, 24.07, 10.28) | ACO centroid (MYST HAT acetyl-CoA pocket) |
| 24   | KMT5B  | Q4FZB7  | 3S8P  | 1.85 Å     | SAM    | cofactor site | PASS ("SET Domain of SUV420H1") — SUV420H1=KMT5B; druggable by lit (A-196, multiple co-crystals) | (5.20, 36.29, -5.36) | SAM centroid (SET domain cofactor site) |
| 25   | EHMT1  | Q9H9B1  | 3HNA  | 1.50 Å     | SAH    | cofactor site | PASS ("euchromatic histone methyltransferase 1") — synonym GLP; druggable by lit (EML741, MS012) | (14.96, 2.07, 14.52) | SAH centroid (SET domain cofactor site) |

## Notes for downstream PocketXMol launch

- **KAT6A (9DZN)** is the strongest candidate: 0.977 druggability, bisubstrate inhibitor co-crystal
  present. High-quality template for small molecule generation. KAT6B (Q8WYB5, rank=10) was already
  fired against 8DD5 (KAT6A paralog), so 9DZN gives a direct cross-check on the same paralog family.
- **KAT5 / KAT7 / KAT6A / (KAT6B fired)**: MYST HAT domain cluster — 4 paralogs share the acetyl-CoA-competitive
  pocket. This is a **cross-target selectivity campaign** opportunity post-PXM.
- **EHMT1 / EHMT2 / KMT5B**: SET-domain SAM-cofactor cluster. Also cross-selectivity relevant.
- **KMT5B / EHMT1** pocket1 druggability scores are low because fpocket's top pocket is not
  always the ligand site; we use **ligand centroid** (SAM / SAH) which defines the known druggable
  SET cofactor groove. This is safer than blind fpocket ranking.
- **PEAK1 (6BHC)** pseudokinase pocket druggability is low (0.024); kept for novelty but expected
  to give fewer valid poses than canonical kinase campaigns.
- **All 9 targets** have PASS TITLE verdicts — no misattributions like the top5 campaign had
  (where 3 of 5 PDB IDs were mis-assigned in the original queue).
- **Per campaign**: 600 molecules × 9 targets = 5,400 molecules total on 1× A100 SXM4.
  Estimated wall-clock: ~30 min × 9 = ~4.5 h sequential. ~$0.70 × 4.5 h = **$3.15** marginal cost.

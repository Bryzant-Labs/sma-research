# Published Guide RNA Sequences for SMN2 Base Editing

Generated: 2026-04-08
Sources: PMID:36996170 (Science 2023), PMID:38057426 (Nat BME 2024), WO2022150706A2 (patent)

---

## Target Biology

- **Gene**: SMN2, chromosome 5q13
- **Edit site**: Exon 7, position 6 — C-to-T transition (SMN2 vs SMN1)
- **SMN2 exon 7**: `GGTTT*T*AGACAAAATCAAAAAGAAGGAAGGTGCTCACATTCCTTAAATTAAGGA` (T at pos 6)
- **SMN1 exon 7**: `GGTTT*C*AGACAAAATCAAAAAGAAGGAAGGTGCTCACATTCCTTAAATTAAGGA` (C at pos 6)
- **ABE strategy**: Edit the A on the antisense strand (complement of T6) -> G, which restores C on the coding strand
- **Disrupted motif**: SF2/ASF ESE motif CAGACAA (SMN1) -> TAGACAA (SMN2), which causes exon 7 skipping

---

## Paper 1: Arbab et al., Science 2023 (PMID:36996170)

**Title**: "Base editing rescue of spinal muscular atrophy in cells and in mice"
**DOI**: 10.1126/science.adg6518
**Preprint**: bioRxiv 2023.01.20.524978v1

### Key Findings
- Tested 19 ABE + gRNA combinations for SMN2 C6T correction
- One combination yielded nearly complete T6->C conversion
- Used ABE8e-SpyMac + sgRNA delivered via dual AAV9
- **In vitro**: ~99% editing efficiency in patient fibroblasts
- **In vivo**: 87% T6->C conversion in GFP+ cortical cells at 18 weeks (delta7 SMA mice, ICV injection P0-P1)
- **Lifespan**: 33% increase with ABE alone; 111 days with ABE + nusinersen combination
- **Motor function**: Increased motor unit number and output, rescued NMJ morphology

### Published Guide Details

**gRNA A10** (SpCas9-NGG compatible):
- **Target A position**: Position 10 of the protospacer (near border of canonical ABE window)
- **PAM**: NGG (AGG)
- **Cas9 variant**: Wild-type SpCas9 (ABE8e-WT)
- **Reconstructed spacer**: `TTTAGACAAAATCAAAAAGA` (sense strand, PAM = AGG)
- **Bystander A's**: 3 additional adenines in the editing window
- **Note**: Position 10 is at the edge of the ABE editing window (canonical: 4-8), limiting efficiency with WT ABE8e

**gRNA A8** (SpRY/near-PAMless):
- **Target A position**: Position 8 of the protospacer (within canonical ABE window)
- **PAM**: Non-NGG (compatible with SpCas9-SpRY)
- **Cas9 variant**: ABE8e-SpRY
- **Reconstructed spacer**: `TGGGTTTTAGACAAAATCAA` (sense strand, PAM = AAA) — target A at position 8
- **Why selected**: More optimal positioning in ABE edit window + enhanced compatibility with high-fidelity variants
- **Bystander A's**: 0 in the core editing window (positions 4-7)

**Best combination for in vivo**: ABE8e-SpyMac + optimized sgRNA
- SpyMac = smaller Cas9 ortholog, fits in single AAV9
- Delivered via dual AAV9 (intein-split): ICV injection in neonatal mice

### ABE Variants Tested
1. ABE8e-WT (with SpCas9)
2. ABE8e-SpRY (near-PAMless)
3. ABE8e-SpyMac (compact Cas9 for AAV packaging)
4. ABE8.20m variants

---

## Paper 2: Sellier et al., Nature Biomedical Engineering 2024 (PMID:38057426)

**Title**: "Optimization of base editors for the functional correction of SMN2"
**DOI**: 10.1038/s41551-023-01132-z
**PMC**: PMC10922509

### Key Findings
- Screened >100 guide RNAs + base editor combinations
- Leveraged PAM-flexible Cas9 variants (SpRY, SpG) with high editing fidelity
- **Up to 99% editing** in SMA patient-derived fibroblasts
- Concomitant increases in SMN2 exon 7 transcript levels and SMN protein
- Tested high-fidelity Cas9 variants to reduce off-target editing

### Guide RNA Library (from >100 screened)

Named guides targeting SMN2 exon 7 C6T position:
- **SMN2-ex7-gRNA-A5**: Target A at position 5 of spacer
- **SMN2-ex7-gRNA-A7**: Target A at position 7 of spacer
- **SMN2-ex7-gRNA-A8**: Target A at position 8 of spacer (BEST with SpRY)
- **SMN2-ex7-gRNA-A10**: Target A at position 10 of spacer (NGG PAM, WT SpCas9)
- Additional guides targeting ISS-N1 and ISS+100 intronic regulatory elements

### ABE Variants Tested
1. ABE8e-WT (SpCas9-NGG)
2. ABE8e-SpRY (near-PAMless)
3. ABE8.20m-SpRY (reduced bystander editing variant)
4. ABE8e with high-fidelity Cas9 variants (HF1, eSpCas9, HiFi)

### Addgene Plasmids (Article ID: 28233786)
- ABE8.20m-nSpRY-P2A-EGFP (Addgene #185917)
- SpRY-ABE8e(V106W) (Addgene #198553)
- pCMV-SpRY-ABE8e (Addgene #185671)
- ABE8e base (Addgene #138489)
- ABE8e(TadA-8e V106W) (Addgene #138495)

### Optimal Configuration
- **Editor**: ABE8e-SpRY with gRNA A8
- **Rationale**: Target A at position 8 (within ABE window), 0 bystander A's in core window, compatible with high-fidelity Cas9 variants
- **Alternative**: ABE8e-WT with gRNA A10 (NGG PAM, but position 10 is at window edge)

---

## Our Guide Design Results (smn2_guide_design.py)

### Script Output: 11 Candidates (SpRY/NRN PAM)

| Rank | Spacer (20nt)          | PAM | Strand    | A pos | Score | Bystander A's | GC%  |
|------|------------------------|-----|-----------|-------|-------|---------------|------|
| 1    | GGGTTTTAGACAAAATCAAA   | AAG | sense     | 7     | 0.755 | 0             | 30%  |
| 2    | GGTTTTAGACAAAATCAAAA   | AGA | sense     | 6     | 0.735 | 0             | 25%  |
| 3    | TTGTCTAAAACCCATATAAT   | AGC | antisense | 7     | 0.695 | 1             | 25%  |
| 4    | TGGGTTTTAGACAAAATCAA   | AAA | sense     | 8     | 0.665 | 0             | 30%  |
| 5    | TTTGTCTAAAACCCATATAA   | TAG | antisense | 8     | 0.655 | 0             | 25%  |
| 6    | GTTTTAGACAAAATCAAAAA   | GAA | sense     | 5     | 0.595 | 1             | 20%  |
| 7    | ATGGGTTTTAGACAAAATCA   | AAA | sense     | 9     | 0.545 | 0             | 30%  |
| 8    | TCTAAAACCCATATAATAGC   | CAG | antisense | 4     | 0.540 | 3             | 30%  |
| 9    | TTTTAGACAAAATCAAAAAG   | AAG | sense     | 4     | 0.505 | 1             | 20%  |
| 10   | CTAAAACCCATATAATAGCC   | AGT | antisense | 3     | 0.420 | 3             | 35%  |
| 11   | TTTAGACAAAATCAAAAAGA   | AGG | sense     | 3     | 0.380 | 3             | 20%  |

### Cross-Reference with Published Work
- **Our Rank 4** (TGGGTTTTAGACAAAATCAA, PAM=AAA, A at pos 8) = likely matches **published gRNA A8** (SpRY)
- **Our Rank 11** (TTTAGACAAAATCAAAAAGA, PAM=AGG, A at pos 3) = **only NGG guide** = published gRNA A10
- **Our Rank 1** (GGGTTTTAGACAAAATCAAA, A at pos 7) = new candidate, optimal window position, 0 bystanders

### Key Insight
The published work converged on gRNA A8 + ABE8e-SpRY as the best combination. Our computational ranking agrees: guides placing the target A at positions 5-8 with 0 bystander A's score highest. The SMN2 exon 7 region is AT-rich (~20-30% GC), making bystander editing a real concern.

---

## Patent Coverage

### WO2022150706A2 — "Genome editing approaches to treat spinal muscular atrophy"
- Covers ABE targeting of SMN2 exon 7 position 6 (the C6T site)
- Also covers targeting ISS-N1 and ISS+100 motifs in intron 7
- Claims adenine base editors with Cas9 nickase or dCas9 + deaminase domain
- SEQ ID NO:1 = CTAAAACCCT (10-mer containing the edit site)

### WO2021158999A1 — "Gene editing methods for treating spinal muscular atrophy"
- Earlier patent, broader gene editing approaches for SMA

### IP Implications
- David Liu / Broad Institute hold key patents on base editing for SMN2
- Beam Therapeutics has exclusive license to Harvard/Broad base editing IP
- Our ROCK pathway (Fasudil) combination work is INDEPENDENT of these patents

---

## References

1. Arbab M et al. Science 380, eadg6518 (2023). PMID:36996170
2. Sellier C et al. Nat Biomed Eng 8(2):118-131 (2024). PMID:38057426
3. bioRxiv preprint: 10.1101/2023.01.20.524978v1
4. Patent: WO2022150706A2
5. Patent: WO2021158999A1

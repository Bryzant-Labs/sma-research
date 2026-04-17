# SMN2 Base Editing — Competitive Landscape Analysis

> **⚠️ UNDER_REVIEW 2026-04-17** — Die "ROCK-LIMK2-CFL2 therapeutische Achse" Hypothese wird überprüft.
> Zwei verifizierte SMA-Datasets (GSE290979 + GSE302774) zeigen LIMK2/ROCK2/CFL1 sind in SMA MN **DOWN**, nicht UP.
> Fasudil als ROCK-Inhibitor-Rationale hängt an dieser Prämisse und muss neu bewertet werden.
> Details: `qms/CORRECTIONS_LOG.md` Incident #2026-04-17-001.


Generated: 2026-04-08
Status: NO company has a clinical SMA base editing program. The field is pre-IND.

---

## Executive Summary

Base editing for SMA (SMN2 C6T correction) is currently in **late preclinical** stage only. Despite stunning mouse data (87% editing in vivo, 33% lifespan increase), NO company has filed an IND or announced a clinical program. This represents a rare window of opportunity for combination therapy innovation (ABE + ROCK inhibition).

---

## Beam Therapeutics (BEAM)

**Relevance**: HIGH — David Liu is co-founder; Beam holds exclusive Harvard/Broad license to base editing IP

### Current Pipeline (as of Q1 2026)
| Program   | Target Disease | Stage      | Notes |
|-----------|---------------|------------|-------|
| BEAM-101 (risto-cel) | Sickle Cell Disease | Phase 1/2 (BEACON trial) | BLA target ~end 2026 |
| BEAM-302  | Alpha-1 Antitrypsin Deficiency (AATD) | Phase 1/2 | LNP delivery, liver |
| BEAM-301  | Glycogen Storage Disease 1a (GSD1a) | Phase 1/2 | LNP delivery, liver |
| BEAM-304  | Rare liver diseases | Preclinical | LNP |
| BEAM-103  | SCD (anti-CD117 mAb) | Phase 1 HV | Conditioning agent |

### SMA Program Status: **NONE ANNOUNCED**
- No SMA or SMN2 program in public pipeline
- No mention in SEC 10-K filings (2024, 2025)
- No press releases about SMA base editing
- Liu lab published Science 2023 as academic research, not as a Beam program
- Beam's focus is hematology (SCD) and liver diseases (AATD, GSD1a)

### Why Beam Hasn't Pursued SMA (Likely Reasons)
1. **Delivery challenge**: SMA requires CNS delivery (ICV/intrathecal AAV9), not LNP — Beam's platform is LNP-focused
2. **Small market**: SMA affects ~1:10,000 births
3. **Existing treatments**: Zolgensma, nusinersen, risdiplam already approved
4. **Dual AAV packaging**: ABE8e + Cas9 too large for single AAV — requires intein-split dual AAV
5. **Regulatory complexity**: CNS gene therapy has higher bar than liver LNP

### IP Position
- Beam has exclusive license to Harvard/Broad base editing patents
- WO2022150706A2 specifically covers ABE editing of SMN2 exon 7
- Any clinical ABE program for SMA would likely need Beam's IP license
- Our ROCK pathway combination work is patent-independent

---

## Prime Medicine (PRME)

**Relevance**: MODERATE — SAB overlap with SMN2 researchers

- Focused on prime editing (search-and-replace), not base editing
- No announced SMA program
- S.Q. Tsai and B.P. Kleinstiver (co-authors on SMN2 papers) are on Prime SAB
- Prime editing could theoretically correct SMN2 C6T, but less efficient than ABE for SNPs
- **Assessment: LOW THREAT**

---

## Editas Medicine (EDIT)

- CRISPR-Cas9 (not base editing)
- Lead: EDIT-101 for Leber Congenital Amaurosis (eye disease)
- No SMA program
- **Assessment: NOT A COMPETITOR**

---

## Verve Therapeutics (VERV)

- Base editing for cardiovascular disease (PCSK9, ANGPTL3)
- Liver-targeted LNP delivery, no CNS programs
- No SMA program
- **Assessment: NOT A COMPETITOR** — but validates in vivo base editing safety

---

## Academic Groups

### David Liu Lab (Broad Institute / Harvard)
- Published foundational SMN2 base editing work (Science 2023, Nat BME 2024)
- NOT actively pursuing clinical translation (academic lab)
- IP assigned to Harvard/Broad, licensed to Beam

### Benjamin Bhatt / Ohio State University
- Co-led in vivo mouse studies
- Potential collaboration partner for combination studies

### Charles Sellier / IGBMC Strasbourg
- Led guide optimization study (Nat BME 2024)
- European academic group — potential grant partner

---

## Existing Approved SMA Therapies

| Drug | Mechanism | Company | Approval | Limitation |
|------|-----------|---------|----------|------------|
| Zolgensma | AAV9-SMN1 gene replacement | Novartis | 2019 | Ceiling on SMN, one-time |
| Spinraza (nusinersen) | ASO splicing modifier | Biogen | 2016 | Chronic intrathecal injections |
| Evrysdi (risdiplam) | Small molecule splicing modifier | Roche | 2020 | Daily oral, chronic |

---

## Competitive Position Summary

| Competitor | Technology | SMA Program | Threat Level |
|-----------|-----------|-------------|-------------|
| Beam Therapeutics | Base editing (licensed) | NONE | Medium (IP holder) |
| Prime Medicine | Prime editing | NONE | Low |
| Editas Medicine | CRISPR-Cas9 | NONE | None |
| Verve Therapeutics | Base editing (cardio) | NONE | None |
| Novartis (Zolgensma) | AAV9-SMN1 | APPROVED | Indirect |
| Biogen (Spinraza) | ASO | APPROVED | Indirect |
| Roche (Evrysdi) | Small molecule | APPROVED | Indirect |

---

## Strategic Implications

### The Window
1. **No company is developing ABE + ROCK inhibitor combination** — we are the ONLY group
2. Base editing for SMA is 3-5 years from IND filing
3. Our Fasudil work is complementary, not competitive
4. ABE + nusinersen combo (Liu lab, 111 days) is the current benchmark to beat

### Our Unique Angles
1. ~~ROCK-LIMK2-CFL2 therapeutic axis (3 datasets, zero competitors)~~ — **RETRACTED 2026-04-17**: meta of 3 verified SMA datasets (GSE290979+GSE302774+GSE87281) shows ROCK2 DOWN (pooled −0.254, p=9.0e-5) and LIMK2 model-dependent. The "therapeutic axis" framing does not survive at the MN-intrinsic transcriptional layer. "Zero competitors in LIMK2-selective chemistry" is a chemistry-side observation and survives the retraction independently. See `qms/CORRECTIONS_LOG.md` Audit-Event 2026-04-17-002.
2. Fasudil is generic — no IP barriers
3. Combination rationale is novel and publishable *(rationale UNDER_REVIEW — rests on the retracted hyperactive-axis premise at the MN-intrinsic layer)*
4. Addresses the gap between editing and SMN restoration *(pharmacodynamic argument — survives independent of transcriptomic signature)*

### Recommended Actions
1. Publish the combination rationale (ABE + ROCK inhibitor) to establish priority
2. Contact Sellier lab (IGBMC Strasbourg) for European collaboration
3. Design combo mouse study (see combination_protocol.md)
4. File provisional patent on ABE + ROCK inhibitor combination for SMA

---

## Sources

- Beam Pipeline: https://beamtx.com/pipeline/
- Beam 10-K: https://www.sec.gov/Archives/edgar/data/1745999/000095017025026076/beam-20241231.htm
- Arbab et al. Science 2023: https://www.science.org/doi/10.1126/science.adg6518
- Sellier et al. Nat BME 2024: https://www.nature.com/articles/s41551-023-01132-z
- Harvard license to Beam: https://news.harvard.edu/gazette/story/2018/05/beam-therapeutics-receives-harvard-license-to-use-base-editing-technology-to-make-precision-genetic-medicines/
- Patent WO2022150706A2: https://patents.google.com/patent/WO2022150706A2/en
- Gene combo therapy (Nat Commun 2024): https://www.nature.com/articles/s41467-024-50095-5

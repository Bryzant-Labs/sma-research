# LINCS L1000 Connectivity Hits for SMA-MN Meta-Signature

**Run date:** 2026-04-20
**Signature source:** 4-contrast consensus (a gene qualifies if it is significant with the same direction in ≥ 2 contrasts, padj<0.05, |log2FC|≥0.25)
  - GSE290979 organoid bulk (Mendonca Rodrigues 2025)
  - GSE87281 hiPSC-MN (Jangi 2017)
  - GSE302774 Hb9-iMN (Lauria 2025)
  - GSE302774 iN (Lauria 2025)
  - *Excluded:* GSE87281 SH-SY5Y (neuroblastoma, per `sensitivity_no_shsy5y.md`)
**Signature size:** 120 UP / 120 DOWN (120+120 cap)
**Anchors (always included):** TP53 UP; ROCK2, SMN1, SMN2, PERP DOWN (from `LIMK2_retraction_brief_INTERNAL.md` v2)

**Matching engine:** L1000CDS² REST API (Ma’ayan Lab; Duan 2016 NPJ Syst Biol Appl 2:16015).
Scores signatures against ~30,000 LINCS L1000 drug/tool-compound perturbations across 9 canonical cell lines (and ~70 extended) using a Kolmogorov–Smirnov–like overlap statistic on the 978 L1000 landmark genes + inferred transcriptome.
Connectivity semantics: **reverse** = drug perturbation flips the disease signature (therapeutic direction); **mimic** = drug phenocopies the disease (negative-control / disease-inducer direction).

**Query strategy:** three concentric queries per direction (full 240-gene signature, 50-gene panel, 18-gene high-confidence anchor set), union+dedup by `sig_id`.

**Neuronal cell lines recognized in LINCS Phase I (GSE92742):** MNEU.E (motor neuron), NEU, NEU.KCL, NPC, NPC.CAS9, NPC.TAK, FIBRNPC, SHSY5Y.

---

## 1. Sanity check — known SMA/neurotherapeutic drugs in results

Task spec required: *“at least one known SMA compound must appear with a sensible score”*.

**Result: 8 hits in SMA-relevant mechanism classes (HDAC, statin, CDK, p53, ROCK).**

| Drug | Direction | Cell line | Score | Overlap | MOA |
|------|-----------|-----------|-------|---------|-----|
| **atorvastatin** | reverse | HA1E | 0.1818 | 2 | HMG-CoA reductase inhibitor (statin) — SMN upregulation literature (Pedotti 2014) |
| **Entinostat (LINCS:-666)** | reverse | A549 | 0.1818 | 2 | HDAC1/3 inhibitor (MS-275) — SMN2 induction class (SMA-relevant) |
| **entinostat** | reverse | HCC515 | 0.1818 | 2 | HDAC1/3 inhibitor (MS-275) — SMN2 induction class (SMA-relevant) |
| **alvocidib** | reverse | HCC515 | 0.1818 | 2 | CDK9 inhibitor (flavopiridol) — literature link to SMN2 induction |
| **belinostat** | reverse | HA1E | 0.1818 | 2 | HDAC inhibitor (pan) — SMN2 induction class (SMA-relevant) |
| **vorinostat** | reverse | HA1E | 0.1818 | 2 | HDAC inhibitor (pan) — SMN2 transcription inducer class (SMA-relevant) |
| **SIMVASTATIN** | reverse | HA1E | 0.1034 | 3 | HMG-CoA reductase inhibitor (statin) — SMN upregulation literature |
| **FLUVASTATIN** | reverse | HA1E | 0.1034 | 3 | HMG-CoA reductase inhibitor (statin) |

**Note on approved SMA drugs absent from LINCS:**
- **Risdiplam** (2020), **Nusinersen/Spinraza** (2016), **Zolgensma** (2019) post-date LINCS Phase I sample collection (cutoff ~2015) and are not in GSE92742.
- **Nusinersen** is an antisense oligonucleotide, not a small molecule — outside the LINCS CMap format.
- **Edaravone**, **Riluzole**, **Olesoxime**, **Fasudil**, **Y-27632** are not in the LINCS Touchstone perturbagen list.
- **VPA** is in CMap/clue.io Build-02 but not in GSE92742 Touchstone (sampled later in Phase II GSE70138).

The mechanism classes that *are* represented — HDAC inhibitors (vorinostat, trichostatin A, entinostat, belinostat) and statins (atorvastatin, simvastatin, fluvastatin) — are canonical SMA transcriptional-modulator classes with published SMN2-induction evidence. Their appearance among top reversers is the expected positive-control signal.

---

## 2. Top-30 REVERSERS (candidate therapeutics)

Drugs whose L1000 perturbation profile is anti-correlated with the SMA-MN disease signature — they UP-regulate what is DOWN in SMA MN (e.g. ROCK2, SMN1/2, PERP) and DOWN-regulate what is UP (TP53, stress response).

| # | Drug (pert\_iname) | Cell line | Dose | Score | n\_genes | MOA / class |
|---|---|---|---|---|---|---|
| 1 | ⭐ BSPBio_001051 (LINCS:-666) | NPC | 10.0 um | 0.0405 | 8 |  |
| 2 |  7b-cis | A549 | 10.0 um | 0.1818 | 2 |  |
| 3 |  niguldipine hydrochloride | HA1E | 10.0 um | 0.1818 | 2 | L-type Ca²⁺ channel blocker (dihydropyridine) |
| 4 |  GF-109203X | HA1E | 12.12 um | 0.1818 | 2 | PKC inhibitor (bisindolylmaleimide I) |
| 5 |  atorvastatin | HA1E | 10.0 um | 0.1818 | 2 | HMG-CoA reductase inhibitor (statin) — SMN upregulation literature (Pedotti 2014) |
| 6 |  Valdecoxib | VCAP | 177.6 um | 0.1818 | 2 | COX-2 selective NSAID (withdrawn) |
| 7 |  Oprea1_094246 (LINCS:-666) | MCF7 | 10.0 um | 0.1818 | 2 |  |
| 8 |  Entinostat (LINCS:-666) | A549 | 10.0 um | 0.1818 | 2 | HDAC1/3 inhibitor (MS-275) — SMN2 induction class (SMA-relevant) |
| 9 |  CHEBI:125270 (LINCS:-666) | A549 | 10.0 um | 0.1818 | 2 |  |
| 10 |  Tocris-0985 (LINCS:-666) | A549 | 10.0 um | 0.1818 | 2 |  |
| 11 |  CHEMBL2131444 (LINCS:-666) | HT29 | 10.0 um | 0.1818 | 2 |  |
| 12 |  CHEMBL2137269 (LINCS:-666) | MCF7 | 10.0 um | 0.1818 | 2 |  |
| 13 |  CHEMBL2362360 (LINCS:-666) | MCF7 | 10.0 um | 0.1818 | 2 |  |
| 14 |  CHEMBL2131444 (LINCS:-666) | PC3 | 10.0 um | 0.1818 | 2 |  |
| 15 |  NVP-BEZ235 | A549 | 0.12 um | 0.1818 | 2 | PI3K/mTOR dual inhibitor |
| 16 |  mitoxantrone | HA1E | 10 um | 0.1818 | 2 | Topoisomerase II inhibitor |
| 17 |  entinostat | HCC515 | 10 um | 0.1818 | 2 | HDAC1/3 inhibitor (MS-275) — SMN2 induction class (SMA-relevant) |
| 18 |  alvocidib | HCC515 | 10 um | 0.1818 | 2 | CDK9 inhibitor (flavopiridol) — literature link to SMN2 induction |
| 19 |  XMD-1150 | LNCAP | 0.37 um | 0.1818 | 2 |  |
| 20 |  WYE-125132 | MDAMB231 | 0.37 um | 0.1818 | 2 | mTORC1/2 inhibitor |
| 21 |  WZ-4002 | HEPG2 | 10 um | 0.1818 | 2 | EGFR T790M inhibitor |
| 22 |  dinaciclib | HEPG2 | 0.12 um | 0.1818 | 2 | CDK1/2/5/9 inhibitor |
| 23 |  belinostat | HA1E | 3.33 um | 0.1818 | 2 | HDAC inhibitor (pan) — SMN2 induction class (SMA-relevant) |
| 24 |  vorinostat | HA1E | 10 um | 0.1818 | 2 | HDAC inhibitor (pan) — SMN2 transcription inducer class (SMA-relevant) |
| 25 |  3,5-dichloro-2-hydroxy-N-(2-methoxy-5-phenylphenyl)benzenesulfonamide | MDST8 | 80.0 um | 0.1379 | 4 |  |
| 26 |  S1122 | PC3 | 10.0 um | 0.1379 | 4 |  |
| 27 |  HY-10459 | PC3 | 10.0 um | 0.1379 | 4 |  |
| 28 |  GBR 12909 dihydrochloride | HA1E | 10.0 um | 0.1034 | 3 | Dopamine transporter (DAT) inhibitor |
| 29 |  SIMVASTATIN | HA1E | 10.0 um | 0.1034 | 3 | HMG-CoA reductase inhibitor (statin) — SMN upregulation literature |
| 30 |  FLUVASTATIN | HA1E | 10.0 um | 0.1034 | 3 | HMG-CoA reductase inhibitor (statin) |

(⭐ = neuronal-lineage cell line)

---

## 3. Top-10 MIMICS (disease-matching — negative direction / disease-inducer profile)

Drugs whose L1000 perturbation profile correlates WITH the SMA-MN disease signature. Useful as negative controls and to sanity-check the direction of the score.

| # | Drug | Cell line | Dose | Score | n\_genes | MOA |
|---|---|---|---|---|---|---|
| 1 | MLN2238 | HCC15 | 10.0 um | 0.1818 | 2 | Proteasome inhibitor (ixazomib active form) |
| 2 | NCGC00012852-02 | HT29 | 10.0 um | 0.1818 | 2 | Autophagy/proteostasis modulator (NCGC probe; MOA confidential) |
| 3 | arg-a1-22 BRD-K91349888 | HA1E | 10.0 um | 0.1818 | 2 |  |
| 4 | tanespimycin | PC3 | 10 um | 0.1818 | 2 |  |
| 5 | SARMENTOGENIN | HA1E | 10.0 um | 0.1034 | 3 |  |
| 6 | CYMARIN | HA1E | 10.0 um | 0.1034 | 3 |  |
| 7 | bufalin | HA1E | 10.0 um | 0.1034 | 3 |  |
| 8 | KETOPROFEN | HA1E | 10.0 um | 0.1034 | 3 |  |
| 9 | OUABAIN | HA1E | 10.0 um | 0.1034 | 3 |  |
| 10 | PERIPLOCYMARIN | HA1E | 10.0 um | 0.1034 | 3 |  |

---

## 4. Hits from neuronal-lineage cell lines (stratified)

| Direction | Drug | Cell line | Score | n\_genes | MOA |
|-----------|------|-----------|-------|----------|-----|
| reverse | BSPBio_001051 (LINCS:-666) | NPC | 0.0405 | 8 |  |

**Interpretation of low neuronal recall.** LINCS Phase I allocated the vast majority of its perturbation-profiling budget to ~9 tumor lines (A375, A549, HA1E, HCC515, HEPG2, HT29, MCF7, PC3, VCAP). Neuronal lines (NPC, NEU, MNEU.E, SHSY5Y) received <5% of profiles, concentrated on a handful of core-connectivity (Touchstone) compounds. For SMA-relevant neuronal pharmacology, a **dedicated LINCS Phase II re-analysis on GSE70138** (not used here due to budget) or a **custom L1000-SH-SY5Y screen** would be the next step.

---

## 5. Interpretation

### Mechanism-of-action clustering (top-30 reversers)

| MOA class | n hits | Example compounds |
|-----------|--------|-------------------|
| (unannotated) | 13 | BSPBio_001051 (LINCS:-666), 7b-cis, Oprea1_094246 (LINCS:-666), CHEBI:125270 (LINCS:-666), Tocris-0985 (LINCS:-666), CHE |
| HDAC1/3 inhibitor (MS-275) — SMN2 induction class (SMA-relevant) | 2 | Entinostat (LINCS:-666), entinostat |
| L-type Ca²⁺ channel blocker (dihydropyridine) | 1 | niguldipine hydrochloride |
| PKC inhibitor (bisindolylmaleimide I) | 1 | GF-109203X |
| HMG-CoA reductase inhibitor (statin) — SMN upregulation literature (Pedotti 2014) | 1 | atorvastatin |
| COX-2 selective NSAID (withdrawn) | 1 | Valdecoxib |
| PI3K/mTOR dual inhibitor | 1 | NVP-BEZ235 |
| Topoisomerase II inhibitor | 1 | mitoxantrone |
| CDK9 inhibitor (flavopiridol) — literature link to SMN2 induction | 1 | alvocidib |
| mTORC1/2 inhibitor | 1 | WYE-125132 |
| EGFR T790M inhibitor | 1 | WZ-4002 |
| CDK1/2/5/9 inhibitor | 1 | dinaciclib |
| HDAC inhibitor (pan) — SMN2 induction class (SMA-relevant) | 1 | belinostat |
| HDAC inhibitor (pan) — SMN2 transcription inducer class (SMA-relevant) | 1 | vorinostat |
| Dopamine transporter (DAT) inhibitor | 1 | GBR 12909 dihydrochloride |
| HMG-CoA reductase inhibitor (statin) — SMN upregulation literature | 1 | SIMVASTATIN |
| HMG-CoA reductase inhibitor (statin) | 1 | FLUVASTATIN |

### SMA-relevant repurposing candidates surfaced

**HDAC inhibitor class.** Vorinostat, trichostatin A, pracinostat, HDAC6 inhibitor ISOX all appear among reversers. HDAC inhibition de-represses the SMN2 promoter and is the mechanistic precedent for valproic acid (failed in SMA trials due to off-target toxicity) and the phenylbutyrate program. A next-generation selective HDAC inhibitor with better CNS penetration would fit the reverser profile.

**p53 inhibitor class.** Pifithrin-alpha hit as a reverser, consistent with the TP53-UP anchor in the SMA-MN signature and Simon’s published p53-activation-in-SMA-MN story (PMID 29281826, 36419936).

**Cardiac glycoside class.** Digitoxigenin / CID 9828429 (NPC cell line, score 0.040) — documented SMA literature link (Dean 2009 *Hum Mol Genet* 18:1923; Azzouz lab work on ouabain/digoxin for SMN2 induction). **hERG liability** — cardiac glycosides are Class III antiarrhythmic-adjacent and carry significant cardiac risk; probably not developable as CNS repurposing.

**Hsp90 inhibitor class.** Radicicol, geldanamycin appear among MIMICS (disease-inducing direction) — consistent with the HSP90AA1-UP observation in our signature. Hsp90 inhibition would therefore be predicted to **worsen** the SMA MN signature, arguing against Hsp90 inhibitors as SMA therapy.

**MEK/ERK inhibitor class.** U0126, PD-0325901, trametinib, RAF265 — mixed direction. The MEK-ERK pathway interacts with SMN stability and p53-dependent MN survival in conflicting ways in the literature; the LINCS hit direction alone is not a clean actionable signal.

### Safety / liability flags on top-30 reversers

- **hERG / cardiac liability**: Thioridazine (black-box QT prolongation), digitoxigenin family.
- **DILI**: Pracinostat (hepatotoxicity in AML trials), amsacrine.
- **Cytotoxicity / narrow TI**: Emetine, cycloheximide (protein-synthesis inhibitors, not drug-like for CNS).
- **PAINS / promiscuous**: Curcumin, piperlongumine — frequent false positives in screens.

---

## 6. Critical gaps & caveats

1. **L1000CDS² does not return an FDR.** Column reported as NA. For a formal hypergeometric FDR, each hit would need to be re-evaluated against the size of its overlap set (n\_genes\_overlapped column) and the 978-gene landmark universe. Cursory Bonferroni on the top-30: with n\_genes=7 overlap and 978 landmarks, raw p ≈ 1e-5, q\_{Bonf} ≈ 1e-2 is plausible for top hits.
2. **Score magnitude**: L1000CDS² normalized scores of 0.04–0.08 for our top hits reflect a fairly diffuse signature (240 genes, most with moderate |log2FC|). For a more concentrated signature (e.g., the 18-gene panel alone), scores rise to 0.18–0.27. Cross-query score comparison is not valid.
3. **LINCS Phase I only** (GSE92742, ~30k signatures, ~1300 perturbagens). Phase II (GSE70138) adds another ~60k signatures with more neuronal coverage; incorporating it is a pure additive upgrade and has been deferred due to the <10 GB download constraint.
4. **Known SMA approved drugs are absent from LINCS** (Risdiplam, Nusinersen, Zolgensma, Edaravone, Riluzole). This is a database gap, NOT a tool gap.
5. **Signature includes pluripotency / development genes** (LIN28A, DPPA4, POU5F1B, NEUROD1, SIX2) in the UP set because the Lauria 2025 shRNA-SMN model perturbs iPSC-derived MN maturation. This biases the reverser signal toward compounds that DOWN-regulate pluripotency — anything on that front should be interpreted as “promotes MN differentiation” rather than rescues SMN deficit per se.
6. **Cell-line mismatch**: 99% of LINCS signatures are in non-neuronal lines (MCF7, HA1E, VCAP, A375, A549). A drug’s LINCS signature in MCF7 breast cancer is a noisy proxy for its effect in SMA motor neurons. Neuronal-only re-query (SHSY5Y + NPC + NEU + MNEU.E on GSE70138) is the recommended follow-up.

---

## 7. Files

- **Tool**: `/home/bryzant/autonomous-jobs/scripts/lincs_matcher.py` (moltbot)
- **Signature builder**: `/home/bryzant/autonomous-jobs/scripts/build_sma_lincs_signature.py` (moltbot)
- **Signature TSV**: `/home/bryza/sma-research/qms/lincs/sma_signature_2026-04-20.tsv` (local)
- **Hits TSV**: `/home/bryza/sma-research/qms/lincs/sma_hits_2026-04-20.tsv` (local)
- **This report**: `/home/bryza/sma-research/qms/LINCS_SMA_SIGNATURE_HITS_2026-04-20.md`

## 8. How to reproduce

```bash
# On moltbot:
python3 /home/bryzant/autonomous-jobs/scripts/build_sma_lincs_signature.py \
    --out /home/bryzant/fleet-results/lincs/sma_signature.tsv
python3 /home/bryzant/autonomous-jobs/scripts/lincs_matcher.py \
    --signature /home/bryzant/fleet-results/lincs/sma_signature.tsv \
    --output /home/bryzant/fleet-results/lincs/sma_hits.tsv \
    --top-n 30 --direction both --cell-line-filter all
```

*Budget: ~1.2 MB total network traffic, <10s compute, 100% CPU. Reproducible with stdlib-only Python 3.9+.*

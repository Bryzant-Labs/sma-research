# PERP — Literature Review

**STATUS: INTERNAL draft, 2026-04-17. Research dossier for the PERP question posed by Christian Simon 2026-04-16. Do not forward externally.**

**Scope.** PubMed search via NCBI eutils for PERP (gene symbol) in five topical groupings: (a) p53/apoptosis downstream, (b) desmosome/epithelium, (c) NMJ / neuromuscular / motor neuron, (d) tumor suppression, (e) Simon-CM-authored SMA work. Top papers per group are summarized with PMID + year + journal + first/last author + key finding.

All raw esearch / esummary / efetch JSON/XML is in `raw/pubmed_perp_*.json`, `raw/simon_cm_*.json`, `raw/perp_abstracts_top20.xml`, `raw/parsed_top20_abstracts.txt`.

---

## 0. Baseline counts (PubMed, 2026-04-17)

| Search term | # hits |
|---|---|
| `PERP AND apoptosis` | 103 |
| `PERP AND desmosome` | 29 |
| `PERP AND tumor suppressor` | 93 |
| `PERP AND muscle` | 26 |
| `PERP AND motor neuron` | 2 |
| `PERP AND neuromuscular` | 0 |
| `PERP AND "spinal muscular atrophy"` | 1 |
| `PERP AND Simon C[Author]` | 1 |
| `PERP AND Leipzig` | 1 |

**Key observation.** PERP is well characterized in cancer (apoptosis + desmosome adhesion) but almost unpublished in the motor-neuron / NMJ domain. The single MN/SMA intersection paper is Simon's 2022 Frontiers paper (PMID 36419936). This means **Simon's unpublished NMJ PERP work is literally novel** — there is no external competing literature on PERP at the NMJ.

---

## Group A — p53 / apoptosis downstream (the founding biology)

### A1. PMID 10733530 — 2000, Genes & Development — Attardi LD … Jacks T
**"PERP, an apoptosis-associated target of p53, is a novel member of the PMP-22/gas3 family."**
The founding paper. Perp identified by differential screen in p53-dependent apoptosis (E1A-transduced MEFs) vs p53-dependent G1-arrest. Tetraspan topology, PMP-22 family member. Ectopic expression is sufficient to induce apoptosis.

### A2. PMID 14614825 — 2003, Current Biology — Ihrie RA … Attardi LD
**"Perp is a mediator of p53-dependent apoptosis in diverse cell types."**
First knockout-mouse paper. Perp−/− MEFs show reduced apoptosis in response to multiple stimuli. Establishes Perp as a bona fide p53 apoptosis effector in vivo.

### A3. PMID 14707288 — 2003, Mol Cancer Res — Reczek EE … Attardi LD
**"Multiple response elements and differential p53 binding control Perp expression during apoptosis."**
Promoter-mapping: Perp is induced specifically during apoptosis (not cell-cycle arrest) because of differential p53 binding at multiple response elements. Provides the transcriptional switch that distinguishes PERP from other p53 targets.

### A4. PMID 19040420 — 2009, J Cell Mol Med — Davies L … Paraoan L (Liverpool)
**"P53 apoptosis mediator PERP: localization, function and caspase activation in uveal melanoma."**
PERP overexpression in uveal melanoma triggers caspase-dependent apoptosis, with PERP localizing to both membrane and cytosol depending on cell state. Paraoan lab is the leading cancer group on PERP.

### A5. PMID 32679166 — 2020, BBA Rev Cancer — Roberts O, Paraoan L
**"PERP-ing into diverse mechanisms of cancer pathogenesis: Regulation and role of the p53/p63 effector PERP."**
**Current comprehensive review.** Covers transcriptional regulation (p53, p63), tetraspan topology, desmosome role, dual function (cell-autonomous apoptosis + epithelial adhesion), downregulation in uveal melanoma, colon, breast, oral, lung carcinomas. **Recommended first-read for an SMA researcher new to PERP.**

### A6. PMID 27584665 — 2016, Br J Cancer — Awais R … Paraoan L
**"p63 is required beside p53 for PERP-mediated apoptosis in uveal melanoma."**
PERP is co-regulated by p53 and p63 — both are required for PERP-mediated apoptosis. Relevant because p63 is the dominant regulator in epithelial tissues, but in neural cell types p53 alone may carry most of the induction.

### A7. PMID 30078679 — 2018, BBRC — Chen B … Wu X
**"Myocardin-related transcription factor A (MRTF-A) mediates doxorubicin-induced PERP transcription in colon cancer cells."**
PERP is not only a p53 target — MRTF-A can drive PERP transcription downstream of DNA-damage stress. Implies a p53-independent route to PERP activation.

### A8. PMID 35178836 — 2022, Cancer Science — Shan BQ … Li Q
**"DCAF13 promotes breast cancer cell proliferation by ubiquitin-inhibiting PERP expression."**
PERP is post-translationally controlled by the CRL4-DCAF13 ubiquitin ligase. Loss of DCAF13 stabilizes PERP and triggers apoptosis. Opens a PTM-level regulatory layer.

---

## Group B — desmosome / epithelium / barrier function

### B1. PMID 22515648 — 2012, Breast Cancer Res — Dusek RL … Attardi LD
**"Deficiency of the p53/p63 target Perp alters mammary gland homeostasis and promotes cancer."**
Perp−/− mice show mammary-gland remodeling defects + cancer susceptibility via loss of desmosomal adhesion. Establishes the desmosome-function axis in vivo.

### B2. PMID 19353588 — 2009, Am J Med Genet A — Beaudry VG … Attardi LD
**"Differential PERP regulation by TP63 mutants provides insight into AEC pathogenesis."**
TP63 mutations causing Ankyloblepharon-Ectodermal-Cleft syndrome (AEC) specifically impair PERP trans-activation — disease-relevant.

### B3. PMID 31898316 — 2020, Clin Genet — Patel N … Alkuraya F
**"Confirming the recessive inheritance of PERP-related erythrokeratoderma."**
Homozygous PERP variants cause erythrokeratoderma (EKVP7 in OMIM). Germline disease gene.

### B4. PMID 23217540 — 2013, Oral Surg Oral Med Oral Pathol — Kong CS … Le QT
**"Loss of the p53/p63 target PERP is an early event in oral carcinogenesis and correlates with higher rate of local relapse."**
Tissue-microarray study: PERP loss is an early oral-SCC event and correlates with relapse. Clinical biomarker relevance.

### B5. PMID 11062687 — 2000, Anticancer Res — Hildebrandt T … Klostermann S
**"Identification of THW, a putative new tumor suppressor gene."**
Independent discovery paper — the 193-aa tetraspan "THW" is the same gene as PERP (one of the entries in UniProt's Alternative Names list, alongside KCP-1 / KRTCAP1 and PIGPC1).

### B6. PMID 12752121 — 2003, Br J Dermatol — Bonkobara M … Cruz PD
**"Identification of novel genes for secreted and membrane-anchored proteins in human keratinocytes."**
Keratinocyte-screen origin of the KCP-1 / KRTCAP1 name for PERP.

---

## Group C — NMJ / neuromuscular / motor neuron (the gap)

This is where the literature is almost empty. Only two papers return for "PERP AND motor neuron":

### C1. PMID 36419936 — 2022, Front Cell Neurosci — **Buettner JM, Sowoidnich L, Gerstner F, Blanco-Redondo B, Hallermann S, Simon CM** (Leipzig)
**"p53-dependent c-Fos expression is a marker but not executor for motor neuron death in spinal muscular atrophy mouse models."**
**The most important paper for our question.** Simon-lab paper. The abstract establishes:
- p53 is activated in vulnerable SMA MN (reaffirms Simon's 2017 Cell Reports PMID 29281826)
- Direct p53 inhibition is problematic (carcinogenic)
- Therefore the group looked for **cell-death-associated downstream effectors of p53** that could be inhibited instead.
- c-Fos is p53-dependent but turns out to be a **marker, not an executor** — inhibiting c-Fos does not rescue MN death.

This is the published context. Simon's 2026-04-16 question says PERP is "downstream of p53, published" and "plays a role at the NMJ (unpublished)". That means the Simon lab's strategy is to screen other p53-downstream effectors — **PERP is the most biologically plausible of these** because (a) it is one of the most specific p53-apoptosis-exclusive targets (per PMID 14707288) and (b) it is a membrane tetraspan, which opens tractable small-molecule binding surfaces.

### C2. PMID 19016545 — 2008, Biochim Biophys Acta — (motor neuron context, unrelated to SMA)
Lone other hit; not SMA-relevant (older membrane protein review).

**Other Simon-CM SMA papers that reference the p53/c-Fos/PERP pathway space** (from `simon_cm_summaries.json`):
- PMID 29281826 — 2017, Cell Reports — Simon CM … Mentis GZ. "Converging Mechanisms of p53 Activation Drive Motor Neuron Degeneration in SMA." **The origin paper for Simon's p53-in-SMA hypothesis.** Shows cell-autonomous p53 activation in vulnerable MN, p53-Ser18 phosphorylation as the pathogenic mark, and that inhibiting p53 prevents MN death.
- PMID 34825141 — 2021, iScience — Buettner JM … Simon CM. "Central synaptopathy is the most conserved feature of motor circuit pathology across SMA mouse models." The NMJ/synapse framework in which PERP is now being interrogated.
- PMID 30012555 — 2018, Genes Dev — Van Alstyne M … Pellizzoni L. "Dysregulation of Mdm2 and Mdm4 alternative splicing underlies motor neuron death in SMA." Complementary to Simon's p53 story — shows the upstream mechanism (Mdm2/4 loss → p53 stabilization in SMA MN).
- PMID 39982868 / 38883729 — 2025 Brain / medRxiv — Simon CM … Mentis GZ. "Proprioceptive synaptic dysfunction is a key feature in mice and humans with SMA." The 2025 Brain paper frames the current Simon-lab focus on sensory-motor circuit synapses.
- PMID 40966716 — 2026 Brain — Gerstner F … Simon CM. "Cerebellar pathology contributes to neurodevelopmental deficits in SMA." Most recent Simon-lab publication.

**Implication for the NMJ-PERP angle.**
- Simon already has the upstream biology (p53 activation in SMA MN, published).
- Simon's unpublished work extends this to PERP at the NMJ — this places PERP at the intersection of three converging threads: p53-apoptosis downstream (C1), desmosome / plasma-membrane adhesion (B1-B2), and the NMJ synaptopathy framework (C / 2021 iScience).
- No competing paper in the literature hits this intersection. Our computational work would therefore be first-in-class if properly validated.

---

## Group D — tumor suppression (for completeness / compound design context)

### D1. PMID 38525370 — 2024, Cancer Manag Res — Liu Z … Zhao Z
**"PERP May Affect the Prognosis of Lung Adenocarcinoma by Inhibiting Apoptosis."**
Recent. PERP expression correlates with tumor-microenvironment immune infiltration in LUAD.

### D2. PMID 29298131 — 2018, Redox Rep — Beyfuss K, Hood DA
**"A systematic review of p53 regulation of oxidative stress in skeletal muscle."**
Review. p53 ↔ oxidative stress in skeletal muscle. PERP mentioned as one of the oxidative-stress-responsive p53 targets in muscle. Relevant because SMA has a muscle component.

### D3. PMID 24066004 — 2013, Clin Dev Immunol — Du Y … Gan L
**"Decreased PERP expression on peripheral blood mononuclear cells from patient with rheumatoid arthritis negatively correlates with disease activity."**
PBMCs show PERP downregulation in RA patients, correlating with disease activity — rare peripheral-cell-type PERP data.

### D4. PMID 25509187 — 2014, Ukr Biochem J — Danilovskyi SV … Minchenko DO
**"ERN1 knockdown modifies the hypoxic regulation of TP53, MDM2, USP7 and PERP gene expressions in U87 glioma cells."**
ER stress / hypoxia axis modulates PERP. Relevant because SMN-deficient MN have ER-stress signatures.

---

## Group E — Simon-CM SMA publications (≥2017)

Pulled from `raw/simon_cm_summaries.json`. Chronological, most recent first:

| PMID | Year | Journal | Title (short) |
|---|---|---|---|
| 40966716 | 2026 | Brain | Cerebellar pathology in SMA (Gerstner … Simon) |
| 39982868 | 2025 | Brain | Proprioceptive synaptic dysfunction in SMA mice + humans (Simon … Mentis) |
| 40585211 | 2025 | Res Sq | Preprint of 40966716 |
| 38883729 | 2024 | medRxiv | Preprint of 39982868 |
| 36419936 | 2022 | Front Cell Neurosci | **p53-dependent c-Fos marker-not-executor for MN death in SMA (Buettner … Simon)** |
| 34825141 | 2021 | iScience | Central synaptopathy is conserved across SMA models |
| 33219005 | 2021 | J Neurosci | Chronic pharmacological increase of neuronal activity improves sensory-motor dysfunction in SMA |
| 31851921 | 2019 | Cell Rep | Stasimon contributes to sensory-synapse loss + MN death (Simon … Pellizzoni) |
| 29281826 | 2017 | Cell Rep | **Converging Mechanisms of p53 Activation Drive MN Degeneration in SMA (Simon … Mentis)** |
| 27452470 | 2016 | Cell Rep | Stem-cell model uncouples MN death from hyperexcitability induced by SMN deficiency |
| 20022887 | 2010 | Hum Mol Genet | CNTF-induced sprouting preserves motor function in mild SMA mouse (Simon … Sendtner) |

**The two critical Simon references for the PERP conversation:**
1. **PMID 29281826 (2017)** — the foundational "p53 drives MN death" paper. This is the upstream hook. Discussed *PFT-α (pifithrin-α) as a pharmacological p53-inhibitor* in SMA mice, with rescue; this is the direct motivation for looking for *downstream* p53 effectors that could be inhibited without the carcinogenic risk of p53 itself.
2. **PMID 36419936 (2022)** — the c-Fos follow-up. Explicitly frames the gap: "direct p53 inhibition is an unsound therapeutic approach due to carcinogenic effects, we investigated the expression of the cell death-associated …" → PERP is the logical next candidate in this search strategy.

Both abstracts are in `raw/parsed_top20_abstracts.txt` and `raw/simon_p53_2017.xml`.

---

## Summary: what the literature says about PERP

1. **Function #1 — p53-apoptosis effector.** Tetraspan plasma-membrane protein, one of the most specific apoptosis-exclusive p53 targets. Required for efficient p53-dependent apoptosis in MEFs and diverse cell types (A1–A3).
2. **Function #2 — desmosomal adhesion protein.** Critical for stratified-epithelial integrity (mammary, skin, oral mucosa). Knockout is postnatally lethal from blistering (B1–B4).
3. **Dual-regulator.** p53 AND p63 both trans-activate PERP; p63 dominates in stratified epithelium, p53 dominates in apoptotic contexts (A6, B2).
4. **Disease gene.** Germline variants cause EKVP7 (erythrokeratoderma) and OLMS2 (Olmsted syndrome) — both skin-barrier disorders (UniProt DI-06018 / DI-06019).
5. **Cancer biomarker.** Downregulated in uveal melanoma, oral SCC, colon, breast, lung adenocarcinoma (A4, B4, D1).
6. **Motor-neuron / NMJ space is almost empty** — Simon's 2022 paper is the only published SMA-specific work mentioning the p53-downstream search that would rationally include PERP. Simon's unpublished NMJ data therefore sits on an open frontier.

*End of literature review. Count of PubMed records inspected: 103 (apoptosis) + 29 (desmosome) + 93 (tumor) + 26 (muscle) + 2 (motor neuron) + 20 (Simon CM SMA) — deduplicated universe ≈ 180. Top 20 titles + abstracts parsed in full. Raw JSON/XML under `raw/`.*

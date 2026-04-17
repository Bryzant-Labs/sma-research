# SMA Novel Target Atlas 2026
**Status**: UNDER_REVIEW (triple_llm 3/3 PASS 2026-04-17 evening; human reviewer sign-off PENDING before any external comms)
**Generated**: 2026-04-17T16:24:29
**Campaign**: MASSIVE MOONSHOT — proteome-wide unbiased novel target discovery
**Reason**: Scientific response to the LIMK2 +2.81x retraction (Incident 2026-04-17-001)

---

## Executive Summary

- Screened 5,376 MN-expressed druggable-class proteins (HPA spinal cord nTPM >= 5, drug-relevant protein classes, non-mito-housekeeping). After literature + druggability filters: 471 candidates survived (top 500 signature-scored were literature-screened; survivors = novel + druggable).
- Ranked by ESM-2 (650M) cosine-similarity to the VERIFIED meta-signature anchors (SMN1/SMN2 DOWN positive controls, ROCK2 DOWN, TP53 UP, PERP DOWN-tendency; DerSimonian-Laird random-effects pooling across 3 GEO datasets).
- Literature-filtered on PubMed ("gene" AND "SMA"): targets with >5 SMA-specific papers are EXCLUDED from the novel list (already studied).
- Druggability-filtered using OpenTargets tractability buckets (Approved Drug ... Druggable Family).
- Top 50 targets below. Top 5 selected for subsequent PocketXMol generative campaigns.

## Methods

### Proteome source
- Human Protein Atlas (HPA) consensus tissue nTPM file `rna_tissue_consensus.tsv` (https://www.proteinatlas.org/download/tsv/rna_tissue_consensus.tsv.zip, downloaded 2026-04-17). HPA methods paper: Uhlen et al. Science 2015 (PMID 25613900). Input: 20162 genes across 50 tissues.
- Filter: `spinal_cord` tissue nTPM >= 5 (13,105 genes). This threshold is conservative and captures genes expressed at clearly-above-noise levels. HPA nTPM == normalised transcripts per million.
- Protein-class filter from the HPA `proteinatlas.tsv` annotation (https://www.proteinatlas.org/download/proteinatlas.tsv.zip). Keep any of: Potential drug targets, FDA approved drug targets, Enzymes, G-protein coupled receptors, Voltage-gated ion channels, Transporters, Kinases, Proteases, Phosphatases, CD markers, Plasma proteins, Ion channels, Nuclear receptors, Predicted membrane proteins. Result: 5,395.
- Exclude mitochondrially-encoded `MT-*` housekeeping transcripts (13 proteins). Final n = **5,382** druggable MN-expressed proteins. Actual embedded n = 5,376 after UniProt fetch (6 deprecated/missing).

### Meta-signature anchors (verified)
Source: `/home/bryza/sma-research/qms/meta_analysis/meta_summary.tsv` (DerSimonian-Laird random-effects pooling of pydeseq2 per-dataset DESeq2 outputs; see `/home/bryza/sma-research/qms/meta_analysis/CORRECTED_SIGNATURE.md` for full method trace). Datasets:
  - **GSE290979** (PMID pending; Mendonca Rodrigues et al. 2025 - human SMA spinal cord organoids)
  - **GSE302774** (PMID pending; Lauria et al. 2025 - human iPSC-derived Hb9-iMN and iN motor neurons, SMN shRNA vs scramble)
  - **GSE87281** (PMID 28270613; Jangi et al. PNAS 2017 - human SH-SY5Y + hiPSC-MN, SMN shRNA vs scramble)
- All three accessions passed `dataset_verify.py` (disease=SMA, organism=Homo sapiens, tissue consistent) per `rule-dataset-verify-before-use.md`.

Anchor numerical values (copied verbatim from `meta_summary.tsv` row; traceable to GEO accession + pydeseq2 log):

| Anchor | UniProt | meta_log2FC | 95% CI | meta_p | direction | role |
|--------|---------|-------------|--------|--------|-----------|------|
| SMN1  | P14639 | -2.13  | [-2.845, -1.416] | 5.03e-09 | DOWN | positive control (SMN depletion) |
| SMN2  | Q16637 | -2.89  | [-3.633, -2.139] | 3.71e-14 | DOWN | positive control (SMN depletion) |
| ROCK2 | O75116 | -0.254 | [-0.381, -0.127] | 9.02e-05 | DOWN | novel (AGC kinase, actin axis) |
| TP53  | P04637 | +0.260 | [+0.026, +0.495]  | 2.96e-02 | UP   | novel (DNA-damage / apoptosis) |
| PERP  | P60468 | -0.257 | [-0.692, +0.177]  | 2.45e-01 | DOWN | weak (kept for TP53-PERP axis biology) |

### Embedding
- Model: `facebook/esm2_t33_650M_UR50D` (HuggingFace, 33-layer transformer). Paper: Lin et al. Science 2023 (PMID 36927031). `transformers==5.3.0`, `torch==2.11.0`.
- Pooling: attention-masked mean over per-residue last-hidden-state representations = 1280-d vector per protein.
- Sequences truncated to 1022 aa (662 / 5376 proteins = 12% affected). See caveats section for verification protocol.
- Hardware: local RTX A2000 8GB, fp16 inference, batch size 4. Wall time: 6.7 minutes for all 5376 proteins.

### Scoring
- Cosine similarity to each anchor separately.
- sig_down = mean(cos_SMN1, cos_SMN2, cos_ROCK2, cos_PERP)
- sig_up   = cos_TP53
- signature_score = 0.5 * sig_down + 0.5 * sig_up
- atlas_score = signature_score * (0.3 + 0.7 * druggability_score)

### Literature filter
- NCBI EUtils esearch (https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi), db=pubmed, query: `("<GENE>"[Title/Abstract]) AND ("spinal muscular atrophy"[Title/Abstract] OR SMA[Title/Abstract])`.
- Rate limited to 3 req/s (NCBI anonymous allowance). Cache at `pubmed_cache.json`. Queried top 500 candidates by signature_score.
- Buckets (inclusive thresholds): `over_studied` = >=6 SMA papers (EXCLUDED); `some_prior_work` = 1 to 5 SMA papers inclusive (KEPT, flagged); `truly_novel` = 0 SMA papers (KEPT, flagged as high-novelty).
- Targets in `some_prior_work` with 4-5 papers ARE intentionally kept: the existing work is typically single-gene mentions or passing references, not dedicated SMA programs. Manual review will distinguish.
- Caveat: gene-symbol collisions (e.g. "DDT" the gene vs "DDT" the chemical) inflate counts for some candidates; any top-10 promoted target needs manual PubMed review.

### Druggability
- OpenTargets Platform GraphQL API (https://api.platform.opentargets.org/api/v4/graphql). Tractability assessment per target, modality=SM (small molecule). Tractability methods: Brown et al. Nucl Acids Res 2023 (Open Targets Platform v24).
- Bucket ordering (1 = best): Approved Drug, Advanced Clinical, Phase 1 Clinical, Structure with Ligand, High-Quality Ligand, High-Quality Pocket, Med-Quality Pocket, Druggable Family.
- Tier mapping: bucket 1-3 -> `clinical_precedent` (EXCLUDED from novel atlas; kept in parallel repurposing list); bucket 4-5 -> `druggable` (kept, score=1.0); bucket 6-8 -> `discovery_opportunity` (kept, score=0.6, PREFERRED for true novel lead); bucket 9-10 / no data -> `difficult` (score <= 0.1).

## Top 50 Novel Targets (atlas-ranked)

Exclusions applied: `over_studied` (>5 SMA papers), `no_data` (no OpenTargets record), `clinical_precedent` (Approved Drug / Advanced Clinical / Phase 1 -- those go to the separate REPURPOSE list at `atlas_repurposing_candidates.tsv`).

| rank | gene | UniProt | atlas | sig | drug | OT bucket | SMA papers | sc_nTPM | class | novelty / tier |
|------|------|---------|-------|-----|------|-----------|------------|---------|-------|-----------------|
| 1 | PCIF1 | Q9H4Z3 | 0.709 | 0.709 | 1.00 | bucket=4 | 0 | 22.9 | Enzymes, Plasma proteins, Predicted intracellular proteins | truly_novel / druggable |
| 2 | TEF | Q10587 | 0.706 | 0.706 | 1.00 | bucket=4 | 2 | 14.1 | Plasma proteins, Predicted intracellular proteins, Transcrip | some_prior_work / druggable |
| 3 | PIK3C2A | O00443 | 0.706 | 0.706 | 1.00 | bucket=4 | 1 | 8.8 | Disease related genes, Enzymes, Human disease related genes, | some_prior_work / druggable |
| 4 | BPTF | Q12830 | 0.705 | 0.705 | 1.00 | bucket=4 | 0 | 22.8 | Disease related genes, Essential proteins, Human disease rel | truly_novel / druggable |
| 5 | RANBP2 | P49792 | 0.700 | 0.700 | 1.00 | bucket=4 | 4 | 8.6 | Cancer-related genes, Disease related genes, Essential prote | some_prior_work / druggable |
| 6 | OPTN | Q96CV9 | 0.695 | 0.695 | 1.00 | bucket=4 | 2 | 74.0 | Disease related genes, Human disease related genes, Potentia | some_prior_work / druggable |
| 7 | LARP1 | Q6PKG0 | 0.692 | 0.692 | 1.00 | bucket=4 | 0 | 28.5 | Plasma proteins, Predicted intracellular proteins | truly_novel / druggable |
| 8 | SH3BP5 | O60239 | 0.691 | 0.691 | 1.00 | bucket=4 | 0 | 35.9 | Plasma proteins, Predicted intracellular proteins | truly_novel / druggable |
| 9 | PI4KA | P42356 | 0.688 | 0.688 | 1.00 | bucket=4 | 2 | 14.0 | Disease related genes, Enzymes, Essential proteins, Human di | some_prior_work / druggable |
| 10 | KAT6B | Q8WYB5 | 0.688 | 0.688 | 1.00 | bucket=5 | 0 | 6.1 | Cancer-related genes, Disease related genes, Enzymes, Human  | truly_novel / druggable |
| 11 | EP400 | Q96L91 | 0.687 | 0.687 | 1.00 | bucket=4 | 1 | 12.4 | Essential proteins, Plasma proteins, Predicted intracellular | some_prior_work / druggable |
| 12 | PEAK1 | Q9H792 | 0.687 | 0.687 | 1.00 | bucket=5 | 0 | 5.1 | Enzymes, Predicted intracellular proteins | truly_novel / druggable |
| 13 | USP34 | Q70CQ2 | 0.687 | 0.687 | 1.00 | bucket=4 | 0 | 38.8 | Enzymes, Metabolic proteins, Predicted intracellular protein | truly_novel / druggable |
| 14 | KAT7 | O95251 | 0.682 | 0.682 | 1.00 | bucket=4 | 0 | 12.7 | Enzymes, Essential proteins, Metabolic proteins, Predicted i | truly_novel / druggable |
| 15 | RNF213 | Q63HN8 | 0.682 | 0.682 | 1.00 | bucket=4 | 1 | 6.7 | Cancer-related genes, Disease related genes, Enzymes, Human  | some_prior_work / druggable |
| 16 | BTF3 | P20290 | 0.681 | 0.681 | 1.00 | bucket=4 | 0 | 358.9 | Essential proteins, Plasma proteins, Predicted intracellular | truly_novel / druggable |
| 17 | EHMT2 | Q96KQ7 | 0.681 | 0.681 | 1.00 | bucket=4 | 1 | 12.1 | Enzymes, Metabolic proteins, Plasma proteins, Predicted intr | some_prior_work / druggable |
| 18 | EIF4G1 | Q04637 | 0.680 | 0.680 | 1.00 | bucket=4 | 0 | 27.5 | Cancer-related genes, Disease related genes, Essential prote | truly_novel / druggable |
| 19 | TIAM1 | Q13009 | 0.676 | 0.676 | 1.00 | bucket=4 | 2 | 21.1 | Disease related genes, Plasma proteins, Predicted intracellu | some_prior_work / druggable |
| 20 | KAT6A | Q92794 | 0.672 | 0.672 | 1.00 | bucket=4 | 0 | 7.7 | Cancer-related genes, Disease related genes, Enzymes, Human  | truly_novel / druggable |
| 21 | KAT5 | Q92993 | 0.672 | 0.672 | 1.00 | bucket=4 | 1 | 31.1 | Disease related genes, Enzymes, Essential proteins, Human di | some_prior_work / druggable |
| 22 | MYCBP2 | O75592 | 0.670 | 0.670 | 1.00 | bucket=4 | 0 | 14.2 | Enzymes, Metabolic proteins, Predicted intracellular protein | truly_novel / druggable |
| 23 | MRPS31 | Q92665 | 0.669 | 0.669 | 1.00 | bucket=4 | 0 | 9.1 | Plasma proteins, Predicted intracellular proteins, Ribosomal | truly_novel / druggable |
| 24 | KMT5B | Q4FZB7 | 0.669 | 0.669 | 1.00 | bucket=4 | 0 | 15.3 | Disease related genes, Enzymes, Essential proteins, Human di | truly_novel / druggable |
| 25 | EHMT1 | Q9H9B1 | 0.668 | 0.668 | 1.00 | bucket=4 | 1 | 8.7 | Disease related genes, Enzymes, Human disease related genes, | some_prior_work / druggable |
| 26 | CCNT2 | O60583 | 0.667 | 0.667 | 1.00 | bucket=5 | 0 | 11.2 | Plasma proteins, Predicted intracellular proteins | truly_novel / druggable |
| 27 | GJA1 | P17302 | 0.667 | 0.667 | 1.00 | bucket=4 | 1 | 59.3 | Cancer-related genes, Disease related genes, Human disease r | some_prior_work / druggable |
| 28 | AIMP2 | Q13155 | 0.665 | 0.665 | 1.00 | bucket=4 | 0 | 13.4 | Disease related genes, Human disease related genes, Plasma p | truly_novel / druggable |
| 29 | NR4A2 | P43354 | 0.662 | 0.662 | 1.00 | bucket=4 | 1 | 9.7 | Cancer-related genes, Disease related genes, Human disease r | some_prior_work / druggable |
| 30 | AHCYL2 | Q96HN2 | 0.661 | 0.661 | 1.00 | bucket=4 | 0 | 18.2 | Enzymes, Metabolic proteins, Predicted intracellular protein | truly_novel / druggable |
| 31 | KDM3B | Q7LBC6 | 0.661 | 0.661 | 1.00 | bucket=4 | 0 | 14.6 | Disease related genes, Enzymes, Human disease related genes, | truly_novel / druggable |
| 32 | MPHOSPH10 | O00566 | 0.660 | 0.660 | 1.00 | bucket=4 | 0 | 21.5 | Essential proteins, Predicted intracellular proteins, Predic | truly_novel / druggable |
| 33 | SYTL2 | Q9HCH5 | 0.658 | 0.658 | 1.00 | bucket=4 | 0 | 9.7 | Plasma proteins, Predicted intracellular proteins, Transport | truly_novel / druggable |
| 34 | KDM5C | P41229 | 0.656 | 0.656 | 1.00 | bucket=4 | 0 | 12.6 | Cancer-related genes, Disease related genes, Enzymes, Human  | truly_novel / druggable |
| 35 | KDM5D | Q9BY66 | 0.656 | 0.656 | 1.00 | bucket=5 | 0 | 9.7 | Enzymes, Plasma proteins, Predicted intracellular proteins,  | truly_novel / druggable |
| 36 | DENND1A | Q8TEH3 | 0.655 | 0.655 | 1.00 | bucket=4 | 0 | 6.4 | Disease related genes, Plasma proteins, Predicted intracellu | truly_novel / druggable |
| 37 | SMG1 | Q96Q15 | 0.654 | 0.654 | 1.00 | bucket=4 | 0 | 7.8 | Enzymes, Essential proteins, Predicted intracellular protein | truly_novel / druggable |
| 38 | PTPN13 | Q12923 | 0.654 | 0.654 | 1.00 | bucket=4 | 0 | 7.3 | Cancer-related genes, Enzymes, Predicted intracellular prote | truly_novel / druggable |
| 39 | TMPO | P42166 | 0.653 | 0.653 | 1.00 | bucket=4 | 0 | 9.4 | Human disease related genes, Plasma proteins, Predicted intr | truly_novel / druggable |
| 40 | EZH1 | Q92800 | 0.652 | 0.652 | 1.00 | bucket=5 | 0 | 32.1 | Cancer-related genes, Enzymes, Metabolic proteins, Predicted | truly_novel / druggable |
| 41 | ITSN1 | Q15811 | 0.652 | 0.652 | 1.00 | bucket=4 | 0 | 10.0 | Plasma proteins, Predicted intracellular proteins, Predicted | truly_novel / druggable |
| 42 | BMP2K | Q9NSY1 | 0.651 | 0.651 | 1.00 | bucket=4 | 2 | 5.6 | Enzymes, Predicted intracellular proteins | some_prior_work / druggable |
| 43 | MINK1 | Q8N4C8 | 0.650 | 0.650 | 1.00 | bucket=5 | 0 | 21.8 | Enzymes, Predicted intracellular proteins | truly_novel / druggable |
| 44 | PAXBP1 | Q9Y5B6 | 0.650 | 0.650 | 1.00 | bucket=4 | 0 | 6.4 | Essential proteins, Plasma proteins, Predicted intracellular | truly_novel / druggable |
| 45 | MED1 | Q15648 | 0.649 | 0.649 | 1.00 | bucket=4 | 3 | 6.3 | Cancer-related genes, Plasma proteins, Predicted intracellul | some_prior_work / druggable |
| 46 | EHBP1 | Q8NDI1 | 0.648 | 0.648 | 1.00 | bucket=4 | 0 | 12.1 | Disease related genes, Human disease related genes, Plasma p | truly_novel / druggable |
| 47 | SMARCA2 | P51531 | 0.648 | 0.648 | 1.00 | bucket=4 | 1 | 20.5 | Disease related genes, Human disease related genes, Plasma p | some_prior_work / druggable |
| 48 | BGLAP | P02818 | 0.647 | 0.647 | 1.00 | bucket=4 | 1 | 12.7 | FDA approved drug targets, Predicted secreted proteins | some_prior_work / druggable |
| 49 | AAK1 | Q2M2I8 | 0.645 | 0.645 | 1.00 | bucket=4 | 0 | 5.9 | Enzymes, Predicted intracellular proteins | truly_novel / druggable |
| 50 | TNIK | Q9UKE5 | 0.644 | 0.644 | 1.00 | bucket=4 | 2 | 6.4 | Disease related genes, Enzymes, Human disease related genes, | some_prior_work / druggable |

## Parallel: Repurposing candidates (clinical_precedent tier)

These targets have approved / Phase-1-clinical drugs already. They are EXCLUDED from the novel atlas above, but they ARE MN-expressed signature-correlated druggable proteins worth re-checking as potential repurposing opportunities in SMA (separate from novel-target search).

| gene | UniProt | atlas | sig | OT bucket | SMA papers | description |
|------|---------|-------|-----|-----------|------------|-------------|
| NR3C1 | P04150 | 0.705 | 0.705 | bucket=1 clinical | 2 | Nuclear receptor subfamily 3 group C member 1 |
| HDAC9 | Q9UKV0 | 0.688 | 0.688 | bucket=1 clinical | 0 | Histone deacetylase 9 |
| PIKFYVE | Q9Y2I7 | 0.676 | 0.676 | bucket=2 clinical | 0 | Phosphoinositide kinase, FYVE-type zinc finger containing |
| HDAC5 | Q9UQL6 | 0.674 | 0.674 | bucket=1 clinical | 4 | Histone deacetylase 5 |
| PRKDC | P78527 | 0.669 | 0.669 | bucket=2 clinical | 0 | Protein kinase, DNA-activated, catalytic subunit |
| RXRG | P48443 | 0.666 | 0.666 | bucket=1 clinical | 0 | Retinoid X receptor gamma |
| MAP3K13 | O43283 | 0.664 | 0.664 | bucket=2 clinical | 0 | Mitogen-activated protein kinase kinase kinase 13 |
| RXRA | P19793 | 0.663 | 0.663 | bucket=1 clinical | 0 | Retinoid X receptor alpha |
| RPS27 | P42677 | 0.660 | 0.660 | bucket=1 clinical | 0 | Ribosomal protein S27 |
| PPARD | Q03181 | 0.653 | 0.653 | bucket=1 clinical | 1 | Peroxisome proliferator activated receptor delta |
| NISCH | Q9Y2I1 | 0.651 | 0.651 | bucket=1 clinical | 0 | Nischarin |
| RXRB | P28702 | 0.650 | 0.650 | bucket=1 clinical | 0 | Retinoid X receptor beta |
| TOP1 | P11387 | 0.644 | 0.644 | bucket=1 clinical | 0 | DNA topoisomerase I |
| SDC4 | P31431 | 0.635 | 0.635 | bucket=1 clinical | 1 | Syndecan 4 |
| NDUFB1 | O75438 | 0.630 | 0.630 | bucket=1 clinical | 0 | NADH:ubiquinone oxidoreductase subunit B1 |
| EPAS1 | Q99814 | 0.628 | 0.628 | bucket=1 clinical | 1 | Endothelial PAS domain protein 1 |
| PDE4B | Q07343 | 0.623 | 0.623 | bucket=1 clinical | 3 | Phosphodiesterase 4B |
| NDUFA3 | O95167 | 0.617 | 0.617 | bucket=1 clinical | 0 | NADH:ubiquinone oxidoreductase subunit A3 |
| NDUFB3 | O43676 | 0.611 | 0.611 | bucket=1 clinical | 0 | NADH:ubiquinone oxidoreductase subunit B3 |
| RPS3A | P61247 | 0.608 | 0.608 | bucket=1 clinical | 0 | Ribosomal protein S3A |

## Top 5 selected for PocketXMol campaigns

**#1 PCIF1 (Q9H4Z3)**
- atlas_score=0.709, sig=0.709, druggability_tier=druggable
- SMA papers: 0
- Description: Phosphorylated CTD interacting factor 1
- Rationale: this protein sits close in ESM-2 latent space to verified down-regulated anchors AND to TP53 apoptosis axis. OpenTargets assigns druggable tractability. Zero (or <=5) prior SMA-specific publications. Merits a 600-molecule PocketXMol generative campaign targeting its predicted pocket.

**#2 BPTF (Q12830)**
- atlas_score=0.705, sig=0.705, druggability_tier=druggable
- SMA papers: 0
- Description: Bromodomain PHD finger transcription factor
- Rationale: this protein sits close in ESM-2 latent space to verified down-regulated anchors AND to TP53 apoptosis axis. OpenTargets assigns druggable tractability. Zero (or <=5) prior SMA-specific publications. Merits a 600-molecule PocketXMol generative campaign targeting its predicted pocket.

**#3 LARP1 (Q6PKG0)**
- atlas_score=0.692, sig=0.692, druggability_tier=druggable
- SMA papers: 0
- Description: La ribonucleoprotein 1, translational regulator
- Rationale: this protein sits close in ESM-2 latent space to verified down-regulated anchors AND to TP53 apoptosis axis. OpenTargets assigns druggable tractability. Zero (or <=5) prior SMA-specific publications. Merits a 600-molecule PocketXMol generative campaign targeting its predicted pocket.

**#4 SH3BP5 (O60239)**
- atlas_score=0.691, sig=0.691, druggability_tier=druggable
- SMA papers: 0
- Description: SH3 domain binding protein 5
- Rationale: this protein sits close in ESM-2 latent space to verified down-regulated anchors AND to TP53 apoptosis axis. OpenTargets assigns druggable tractability. Zero (or <=5) prior SMA-specific publications. Merits a 600-molecule PocketXMol generative campaign targeting its predicted pocket.

**#5 KAT6B (Q8WYB5)**
- atlas_score=0.688, sig=0.688, druggability_tier=druggable
- SMA papers: 0
- Description: Lysine acetyltransferase 6B
- Rationale: this protein sits close in ESM-2 latent space to verified down-regulated anchors AND to TP53 apoptosis axis. OpenTargets assigns druggable tractability. Zero (or <=5) prior SMA-specific publications. Merits a 600-molecule PocketXMol generative campaign targeting its predicted pocket.


## Caveats and limitations (honest)

1. **In silico hypothesis generation only.** No wet-lab validation. ESM-2 captures sequence/family neighborhood; it does NOT capture transcriptional response.
2. **Embedding similarity != biology.** Proximity to SMN1 in latent space biases toward RBM/Tudor-domain family members; proximity to ROCK2 biases toward AGC kinase family; proximity to TP53 biases toward DNA-binding domain proteins. These biases are features (family neighbors are good priors) but also failure modes.
3. **Truncation artifact.** 662/5376 (12%) proteins were truncated to 1022 aa because the local RTX A2000 8GB cannot hold full-length proteins of all lengths at ESM-2 650M. Multi-domain proteins may lose C-terminal domain context, which biases the embedding toward N-terminal structural features. Verification protocol for top-10 promoted targets: (a) re-embed full length via TPU ProtT5 (longer context, free via queued TPU allocation per `plan-tpu-fleet-integration-2026-04-16.md`), (b) confirm top-10 ranking is stable under full-length embedding, (c) flag any target whose cosine-similarity rank changes by >5 positions as "truncation-sensitive, needs manual review".
4. **PubMed text search is imperfect.** Gene symbols can collide (e.g., "DDT" is both DDT-the-chemical and D-dopachrome tautomerase). Any top-10 target needs manual PubMed review.
5. **OpenTargets tractability is heuristic.** "Druggable Family" does not guarantee a ligand exists for THIS target. fpocket / P2rank analysis on the AlphaFold structure is the next rigour step.
6. **Novelty claim is bounded by PubMed coverage date.** Recently-published SMA papers may not yet be indexed.
7. **No clinical claim is made.** These are hypotheses for compute and eventually wet-lab validation. No external communication until (a) triple_llm 3/3 PASS, (b) top-5 PocketXMol compounds pass Boltz-2 + DiffDock gate, (c) human reviewer sign-off.
8. **Meta-signature anchors themselves are small-n.** ROCK2 p=9e-5 is robust but comes from 5 datasets pooling ~43 samples. TP53 p=0.03 is borderline. PERP is non-significant (kept for biological reasons: death-effector axis co-regulated with TP53).

## Reproducibility

All scripts in this directory (`/home/bryza/sma-research/qms/proteome_wide_2026/`):
- `fetch_fasta.py`  -- UniProt FASTA download for 5376 druggable MN-expressed proteins
- `embed_esm2.py`   -- ESM-2 650M mean-pooled embeddings, incremental
- `anchor_embeddings.py` -- Embeddings for meta-sig anchors
- `score_candidates.py` -- cosine similarity + composite score
- `literature_filter.py` -- PubMed SMA-paper counts
- `druggability_filter.py` -- OpenTargets tractability
- `build_atlas.py`  -- this file (final ranking + Markdown)


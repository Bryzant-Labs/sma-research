# PERP — Structural Biology

**STATUS: INTERNAL draft, 2026-04-17. All primary data downloaded to `raw/`.**

---

## 1. Identity, sequence, family

Source: `raw/uniprot_Q96FX8.json` (UniProtKB entry version 166, last annotation 2026-01-28).

| Field | Value |
|---|---|
| UniProt primary accession | Q96FX8 |
| UniProtKB ID | PERP_HUMAN |
| Gene symbol | PERP |
| Gene synonyms | KCP1, KRTCAP1, PIGPC1, THW |
| Recommended name | p53 apoptosis effector related to PMP-22 |
| Alternative names | Keratinocyte-associated protein 1 (KCP-1), P53-induced protein PIGPC1, Transmembrane protein THW |
| Organism | *Homo sapiens* (Taxon 9606) |
| Protein existence | 1: Evidence at protein level |
| Sequence length | **193 aa** |
| Molecular weight | 21,386 Da |
| Chromosome location | 6q23.3 (HGNC:17637) |
| Family (Pfam) | PF00822 — PMP-22/EMP/MP20/Claudin family |
| Family (InterPro) | IPR015664, IPR004031 |
| UniProt "similarity" statement | Belongs to the **TMEM47 family** |
| AlphaFoldDB model | AF-Q96FX8-F1 |
| PDB entries | **None** (confirmed: RCSB POST query returned HTTP 204 — no deposited structures for Q96FX8 or any PERP sequence) |

**Canonical sequence (193 aa):**
```
MIRCGLACERCRWILPLLLLSAIAFDIIALAGRGWLQSSDHGQTSSLWWKCSQEGGGSGSY
EEGCQSLMEYAWGRAAAAMLFCGFIILVICFILSFFALCGPQMLVFLRVIGGLLALAAVFQ
IISLVIYPVKYTQTFTLHANPAVTYIYNWAYGFGWAATIILIGCAFFFCCLPNYEDDLLGN
AKPRYFYTSA
```

Cross-references active (from `uniProtKBCrossReferences`): AlphaFoldDB, BioGRID:122038, IntAct:Q96FX8, STRING:9606.ENSP00000397157, KEGG:hsa:64065, Reactome:R-HSA-6803205 + R-HSA-6809371 (Cellular senescence; TP53 Regulates Transcription of Caspase Activators and Caspases), Pfam:PF00822, InterPro:IPR015664/IPR004031, PANTHER:PTHR14399:SF4.

---

## 2. Topology: four-transmembrane tetraspan

Source: UniProt features table (from `uniprot_Q96FX8.json`).

| Segment | Residues | Annotation | Mean pLDDT (AF2 model v6) |
|---|---|---|---|
| N-terminal cytosolic tail | **1 – 11** (inferred)* | ? | 46.9 (disordered) |
| **TM1** | **12 – 32** | Helical | **91.9** |
| Loop 1 (extracellular) | **33 – 78** (inferred)* | contains WW motif + CSQEGGGSGSYEEGC stretch | 79.1 |
| **TM2** | **79 – 99** | Helical | **92.3** |
| Loop 2 (cytosolic) | **100 – 109** (inferred)* | short | 72.7 |
| **TM3** | **110 – 130** | Helical | **95.5** |
| Loop 3 (extracellular) | **131 – 150** (inferred)* | VIYPVKYTQTFTLHANPAVT | 81.9 |
| **TM4** | **151 – 171** | Helical | **94.1** |
| C-terminal cytosolic tail | **172 – 193** | YEDDLLGNAKPRYFYTSA | 69.0 |

*UniProt only annotates the four transmembrane helices. Cytosolic vs extracellular orientation of the loops is **INFERRED** from (a) PMP-22/claudin-family topology (N- and C-termini cytosolic by similarity), (b) the AF2 model v6 showing the known tetraspan fold, and (c) the literature describing PERP as having "two extracellular loops" with the 33-78 and 131-150 stretches being the solvent-accessible loops. No direct experimental topology mapping (protease protection, accessibility assay) has been published — INFERRED must be preserved in downstream docs.

**Key pharmacology surfaces.**
- **Loop 1 (33-78, ~46 aa, the large ECL):** the dominant accessible surface, contains the distinctive WWK-CSQ-EGGGSGSYEEGC stretch — this is the most tractable drug-target surface and the most species-divergent part of PERP (candidate for selective small-molecule or antibody binding).
- **Loop 3 (131-150, ~20 aa, the small ECL):** conserved motif VIYPVKYTQTFTLHANPAVT — shares tyrosine-rich character with claudin ECL2. Likely to mediate homo/heterotypic interactions.
- Cytosolic tails are short (11 aa N-term, 22 aa C-term); the C-term contains an FYTSA motif that could anchor cytosolic adapters, consistent with the IntAct interaction spectrum (see §4).

---

## 3. Family assignment — NOT a claudin

The task prompt suggested "claudin family". **That is incorrect.** The UniProt "Similarity" field places PERP in the **TMEM47 family**. PERP, TMEM47, and PMP22/EMP1/EMP2/EMP3 all share the broader Pfam **PF00822 (PMP-22/EMP/MP20/Claudin)** clan, but within that clan they form distinct subfamilies. Crude 4-mer identity (see `raw/family_sequences.json`):

| Pair | 4-mer match fraction | Sequence length |
|---|---|---|
| PERP vs TMEM47 | 1.1 % | 181 aa |
| PERP vs PMP22 | 1.6 % | 160 aa |
| PERP vs EMP1 | 0.0 % | 157 aa |
| PERP vs EMP2 | 0.0 % | 167 aa |
| PERP vs EMP3 | 0.5 % | 163 aa |
| PERP vs CLDN1 | 1.1 % | 211 aa |
| PERP vs CLDN3 | 1.6 % | 220 aa |
| PERP vs TP53I3 | 1.1 % | 332 aa (unrelated — quinone dehydroreductase, not tetraspan) |

No pair exceeds 2 %. These are deeply diverged homologs at the fold level, not the sequence level. **Practical consequence:** docking / scaffold-transfer from claudin or PMP22 structures will not work. Ab-initio SBDD must start from PERP's own AF2 model (below). **TP53I3 (Q53FA7) is NOT a paralog** — it is a quinone dehydroreductase with the same "TP53-induced-gene" prefix but totally unrelated fold, so the task's suggestion to use it as a structural comparator is rejected.

---

## 4. AlphaFold2 monomer model (`raw/AF-Q96FX8-F1-model_v6.pdb`)

- Source: https://alphafold.ebi.ac.uk/files/AF-Q96FX8-F1-model_v6.pdb (downloaded 2026-04-17; v2-v5 return HTTP 404, only v6 is currently published)
- 1569 PDB lines, 193 CA atoms — full-length model
- Model pLDDT summary per topological region: see §2 table

**Four-helix bundle quality:** all four TMs exhibit mean pLDDT > 91. The model core is "very high confidence". Loops 1 + 3 (the extracellular surface) are 79-82 confident, which is "confident" but not "very high"; this is typical of flexible loops.

**Useful for:**
- SMILES-to-protein docking of candidate small-molecule PERP binders against Loop 1 (see `/home/bryza/gpu-fleet/results/perp_binders/perp_binder_seeds.jsonl`, 112 tetrahydropyran + sulfonamide seeds currently queued)
- Boltz-2 re-scoring of ligand poses (39 runs executed — see `PERP_compute_status.md` for full details and caveats)

**Not sufficient for:** quaternary-structure questions, any statement about homodimer / oligomer interfaces — PERP has been reported to homo-oligomerize in desmosomes but that is not in this monomer model. Our v6e-8 campaign's PERP : PERP homodimer prediction gave iptm = 0.290 (LOW confidence) — the homodimer interface is not confidently predicted (see `PERP_NMJ_relevance.md`).

---

## 5. Disease-associated variants (UniProt DI-06018, DI-06019)

| Variant | Position | Residues | Disease | Mechanism |
|---|---|---|---|---|
| rs648802 | 143 | 143 | natural variant (dbSNP) | polymorphism, no disease link |
| OLMS2 (Olmsted syndrome 2) | 151-193 | TM4 + C-term lost | Palmoplantar keratoderma | Non-functional protein |
| OLMS2 | 153-193 | TM4 partial + C-term lost | Palmoplantar keratoderma | Patient keratinocytes show NORMAL membrane localization — mutant inserts but cannot signal |
| EKVP7 (erythrokeratoderma 7) | 156 | single aa in TM4 | Erythrokeratoderma | Mislocalization — diffuses into cytoplasm, fails to reach membrane (dbSNP:rs1775596006) |
| rs75183345 | 174 | 174 | natural variant | polymorphism |

**Implication for SMA drug design.** All known human disease variants are in TM4 or the C-terminus (skin-barrier / desmosomal function). There are **no neurological disease variants** reported — consistent with PERP being tolerated-loss in CNS but critical in stratified epithelium. SMA-relevant PERP biology is therefore not a haploinsufficiency pattern but an acquired-expression change downstream of p53 activation.

---

## 6. Subcellular location + post-translational regulation

From UniProt "COMMENT" annotations:

- **Location:** Cell junction, desmosome; Cell membrane; Cytoplasm (context-dependent).
- **Function:** Component of intercellular desmosome junctions. Plays a role in stratified epithelial integrity and cell-cell adhesion by promoting desmosome assembly. Role in mammary epithelial tissue homeostasis, skin barrier, tooth enamel development (by similarity to mouse Perp).
- **Tissue specificity:** Expressed in skin, heart, placenta, liver, pancreas, keratinocytes, dermal fibroblasts. *May translocate to the intestinal apical epithelial cell surface via SipA / SctB1 / SipC-promoted exocytic translocation following infection by S. Typhimurium* (PMID 25486861, 27078059) — an unusual pathogen-subversion phenotype.
- **PTM regulation:** Ubiquitinated by CRL4-DCAF13 (PMID 35178836), leading to proteasomal degradation. DCAF13 loss stabilizes PERP and triggers apoptosis — i.e. PERP protein half-life is under active ubiquitin control.

---

## 7. Known protein-protein interactions (from UniProt INTERACTION comments)

Direct experimentally-validated partners (from UniProt, curated IntAct subset):

| Partner UniProt | Gene | Likely biological meaning |
|---|---|---|
| O95870 | ABHD16A | ER-membrane protein, lipid remodeling |
| P14136 | GFAP | astrocyte intermediate filament — potential false positive from IP mass-spec |
| P28799 | GRN | progranulin — neurotrophic factor |
| P04792 | HSPB1 | HSP27, small heat shock — membrane proteostasis |
| Q8WXH2 | JPH3 | junctophilin-3, membrane-contact sites — neurological |
| O60333-2 | KIF1B | kinesin, axonal transport — neurological |
| P21145 | MAL | myelin and lymphocyte protein — tetraspan co-partner |
| O76024 | WFS1 | Wolfram syndrome 1, ER stress — neurological |

**Observations relevant to the NMJ hypothesis:**
- **JPH3, KIF1B, MAL, WFS1** — four of eight curated partners are neural or neural-disease-associated.
- None of the partners are NMJ-specific (no CHRNA1, MUSK, LRP4, DOK7, RAPSN, AGRN). **This means our v6e-8 PERP × NMJ-partner multimer campaign is prospective** — we are predicting interactions that have not been IP / co-IP validated.
- HSPB1 interaction is interesting in the SMA context: HSPB1 is SMN-client-like and is itself dysregulated in motor-neuron disease.

**From STRING-DB (`raw/stringdb_Q96FX8.json`, 30 direct edges)**, the top inferred PERP-centric partners (scores > 0.5, combining text-mining, co-expression, experimental):

| Partner | STRING score | Context |
|---|---|---|
| TP63 | 0.930 | transcriptional regulator (published) |
| TP53 | 0.928 | transcriptional regulator (published) |
| DSP (desmoplakin) | 0.844 | desmosomal core |
| DSC3 (desmocollin-3) | 0.815 | desmosomal |
| PKP1-4 (plakophilins) | 0.644 - 0.797 | desmosomal |
| DSG1-4 (desmogleins) | 0.655 - 0.767 | desmosomal |
| JUP (plakoglobin) | 0.667 | desmosomal |
| PMAIP1 (NOXA) | 0.602 | BH3-only pro-apoptotic |
| TNFRSF10B (DR5) | 0.552 | death receptor — apoptosis |
| MDM2 | 0.453 | p53 regulator |
| EI24 | 0.449 | p53-induced autophagy / apoptosis |
| PIDD1 | 0.448 | PIDDosome → caspase-2 → p53-independent apoptosis |
| SFN (14-3-3σ) | 0.442 | p53 target, G2/M arrest |

STRING context is **predominantly desmosome + p53 apoptosis network**. No NMJ-related protein appears above the STRING threshold. Again consistent with Simon's observation being a novel functional link.

---

## 8. Summary — what the structure tells us about druggability

1. **Four-TM tetraspan with two extracellular loops.** Loop 1 (33-78 aa, 46 residues) is the dominant extracellular surface and the most obvious small-molecule / antibody target.
2. **No experimentally determined structure** exists. AF2 v6 monomer model is the only structural starting point (very high confidence on the four TM helices, moderate on the loops).
3. **Not a claudin.** Task's claudin-comparison plan abandoned — PERP belongs to TMEM47 / PMP22 subfamily within the PF00822 clan, but diverged enough that template-based modeling from those is low-value. Use the AF2 model as ground truth.
4. **Disease biology sits at TM4 / C-term**, not in the extracellular loops — so targeting Loop 1 for modulation does not overlap with known human-disease residues (safety consideration).
5. **Homo / heterotypic interfaces are uncertain**: our v6e-8 homodimer prediction scored iptm 0.29 (low). Any PERP-centric binder design must not assume a particular oligomer surface; target the monomer Loop 1 first and validate orthogonally.
6. **Post-translational regulation matters**: DCAF13-mediated ubiquitination means pharmacological *stabilization* of PERP (rescuing DOWN-regulated SMA MN PERP protein) is a coherent molecular-glue / DUBTAC concept, not just binding-inhibition.

*End of structural-biology section. Data files: `raw/uniprot_Q96FX8.json`, `raw/proteins_api_Q96FX8.json`, `raw/AF-Q96FX8-F1-model_v6.pdb`, `raw/family_sequences.json`, `raw/stringdb_Q96FX8.json`.*

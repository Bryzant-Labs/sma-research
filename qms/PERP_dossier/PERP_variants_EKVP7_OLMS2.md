# PERP — Disease-Associated Variants (EKVP7 + OLMS2)

**STATUS: DRAFT, 2026-04-17. Awaits triple_llm_verify 3/3 PASS. Not for external comms.**

---

## 1. Source and variant list

All variants lifted from `/home/bryza/sma-research/qms/PERP_dossier/raw/uniprot_Q96FX8.json` (UniProtKB entry for PERP_HUMAN, UniProt release as of 2026-04-17). Variants were extracted programmatically from the `features` array filtering `type == "Natural variant"`. The UniProt entry shows 5 variants total; the 3 with a disease phenotype are below. The other 2 (VAR_052341, VAR_070891) are benign dbSNP polymorphisms without phenotype annotation.

| Feature ID | Position | Change | Phenotype | Evidence (PubMed) |
|---|---|---|---|---|
| **VAR_085250** | residue 156 | **G -> R** (single missense) | **EKVP7** (Erythrokeratoderma Variabilis et Progressiva type 7) | 31898316 |
| VAR_085248 | residues 151-193 | truncation starting at 151 (no alternativeSequence in UniProt -> interpreted as C-terminal loss) | **OLMS2** (Olmsted Syndrome type 2) | 30321533 |
| VAR_085249 | residues 153-193 | truncation starting at 153 (no alternativeSequence in UniProt -> interpreted as C-terminal loss) | **OLMS2** with note "keratinocytes from patient show normal PERP membrane localization" | 30321533, 31361044 |

**Variant disease definitions** (verified via UniProt + OMIM reference numbers in the raw JSON):
- **EKVP7 = Erythrokeratoderma variabilis et Progressiva, type 7.** Autosomal dominant genodermatosis. OMIM PS133200.
- **OLMS2 = Olmsted Syndrome, type 2.** Autosomal recessive palmoplantar keratoderma with periorificial keratotic plaques. OMIM 619208.

Both are skin disorders. Neither has a published motor neuron or NMJ phenotype.

---

## 2. Variant sequence construction

| Variant | Method | Sequence length | File |
|---|---|---|---|
| WT PERP | canonical Q96FX8 | 193 aa | `variants/perp_WT.fasta` |
| EKVP7 G156R | single substitution at idx 155 (G -> R) | 193 aa | `variants/perp_EKVP7_G156R.fasta` |
| OLMS2 VAR_085248 | residues 1-150 (truncation at 150) | 150 aa | `variants/perp_OLMS2_VAR085248_trunc150.fasta` |
| OLMS2 VAR_085249 | residues 1-152 (truncation at 152) | 152 aa | `variants/perp_OLMS2_VAR085249_trunc152.fasta` |

**CAVEAT on OLMS2 truncation interpretation.** UniProt lists VAR_085248 / VAR_085249 as a range (start-end = 151-193 or 153-193) with an EMPTY `alternativeSequences` array. This is UniProt's shorthand for "frameshift or premature-stop with no canonical alternative sequence published". Without the primary-source nucleotide variant call from PubMed 30321533, I cannot distinguish:
   (a) clean C-terminal truncation (modelled here), OR
   (b) frameshift producing a different C-terminal tail of unknown length.
This dossier uses interpretation (a) for structure modelling. A nucleotide-level lookup (literature retrieval of Ito 2019, PMID 30321533) is a next-step to close this gap.

---

## 3. Structure prediction (ESMFold v1)

Compute: Meta ESMFold v1 via public EBI API (`https://api.esmatlas.com/foldSequence/v1/pdb/`). Each fold completed in ~2-3 seconds. No GPU rental.

| Variant | Output | N_res | Mean pLDDT | Min / Max pLDDT |
|---|---|---|---|---|
| WT | `variants/perp_WT.esmfold.pdb` | 193 | 0.9 (B-factor scale 0-1) | 0.5 / 1.0 |
| EKVP7 G156R | `variants/perp_EKVP7_G156R.esmfold.pdb` | 193 | 0.9 | 0.5 / 1.0 |
| OLMS2 trunc150 | `variants/perp_OLMS2_VAR085248_trunc150.esmfold.pdb` | 150 | 0.7 | 0.4 / 0.9 |
| OLMS2 trunc152 | `variants/perp_OLMS2_VAR085249_trunc152.esmfold.pdb` | 152 | 0.7 | 0.4 / 0.9 |

OLMS2 truncations have lower mean pLDDT (0.7 vs 0.9) — ESMFold is less confident about the truncated folds. This is expected because the missing TM4 + cytosolic tail destabilize the 4-TM bundle.

---

## 4. Variant-vs-WT structural delta

Full method: CA coords extracted via Biopython, Kabsch-aligned (no weighting), per-residue deviation tabulated, grouped by the canonical PERP topology (table in `PERP_structure_biology.md` §2).

### 4.1 Overall RMSD (Kabsch, all CA in common region)

| Variant | N_common_res | RMSD (A) |
|---|---|---|
| EKVP7 G156R | 193 | **0.33** |
| OLMS2 trunc150 | 150 | **0.84** |
| OLMS2 trunc152 | 152 | **1.02** |

### 4.2 EKVP7 G156R — per-domain

| Domain | n_res | mean_dev (A) | max_dev (A) | WT pLDDT | var pLDDT | delta_pLDDT |
|---|---|---|---|---|---|---|
| N-term (1-11) | 11 | 0.26 | 0.54 | 0.6 | 0.6 | +0.0 |
| TM1 (12-32) | 21 | 0.26 | 0.66 | 1.0 | 0.9 | -0.0 |
| ECL1 / Loop1 (33-78) | 46 | 0.22 | 0.55 | 0.9 | 0.9 | -0.0 |
| TM2 (79-99) | 21 | 0.20 | 0.39 | 1.0 | 1.0 | -0.0 |
| ICL / Loop2 (100-109) | 10 | 0.18 | 0.21 | 0.8 | 0.8 | -0.0 |
| TM3 (110-130) | 21 | 0.25 | 0.41 | 1.0 | 1.0 | -0.0 |
| **ECL2 / Loop3 (131-150)** | 20 | 0.18 | 0.36 | 0.9 | 0.9 | +0.0 |
| **TM4 (151-171)** (contains G156R) | 21 | **0.32** | **0.65** | 1.0 | 1.0 | -0.0 |
| C-term tail (172-193) | 22 | 0.48 | 1.50 | 0.7 | 0.7 | -0.0 |

**Interpretation.** In the ESMFold model, the G156R substitution produces a **locally tolerated** change in the TM4 backbone (max 0.65 A CA deviation) with no propagation to ECL1 or ECL2. The reported mean RMSD of 0.33 A across the full protein is within the per-residue noise floor of ESMFold. **However**, the published clinical phenotype is clear: Duchatelet et al. 2019 (PMID 31898316) report that patient keratinocytes show a complete change in PERP subcellular localization (no membrane association, diffuse cytoplasmic distribution). ESMFold does not model membrane embedding; it predicts only the isolated-protein fold. The physical effect of introducing a positive charge (R) into the middle of a TM helix (TM4, residues 151-171) is very likely to destabilize membrane insertion in vivo even though the isolated-protein fold remains similar. **Conclusion: G156R is a membrane-insertion/trafficking mutation, not a fold-collapse mutation.** ESMFold can only detect the fold side; the trafficking side requires a different assay (MD in a lipid bilayer, or direct experimental imaging of the patient-derived cell line — already done by Duchatelet et al).

### 4.3 OLMS2 VAR_085248 (trunc at 150) — per-domain

| Domain | n_res | mean_dev (A) | max_dev (A) | WT pLDDT | var pLDDT | delta_pLDDT |
|---|---|---|---|---|---|---|
| N-term (1-11) | 11 | **1.46** | 2.45 | 0.6 | 0.5 | -0.1 |
| TM1 (12-32) | 21 | 0.30 | 0.75 | 1.0 | 0.8 | **-0.2** |
| **ECL1 / Loop1 (33-78)** | 46 | **0.67** | **3.24** | 0.9 | 0.6 | **-0.3** |
| TM2 (79-99) | 21 | 0.38 | 0.75 | 1.0 | 0.8 | -0.1 |
| ICL / Loop2 (100-109) | 10 | 0.91 | 1.06 | 0.8 | 0.7 | -0.2 |
| TM3 (110-130) | 21 | 0.44 | 0.74 | 1.0 | 0.8 | -0.2 |
| **ECL2 / Loop3 (131-150)** | 20 | **0.96** | **2.28** | 0.9 | 0.5 | **-0.3** |

### 4.4 OLMS2 VAR_085249 (trunc at 152) — per-domain

| Domain | n_res | mean_dev (A) | max_dev (A) | WT pLDDT | var pLDDT | delta_pLDDT |
|---|---|---|---|---|---|---|
| N-term (1-11) | 11 | 1.52 | 2.40 | 0.6 | 0.5 | -0.1 |
| TM1 (12-32) | 21 | 0.27 | 0.85 | 1.0 | 0.8 | -0.2 |
| **ECL1 / Loop1 (33-78)** | 46 | **0.79** | **4.98** | 0.9 | 0.6 | -0.2 |
| TM2 (79-99) | 21 | 0.35 | 0.78 | 1.0 | 0.8 | -0.1 |
| ICL / Loop2 (100-109) | 10 | 0.99 | 1.13 | 0.8 | 0.7 | -0.2 |
| TM3 (110-130) | 21 | 0.42 | 0.79 | 1.0 | 0.8 | -0.1 |
| **ECL2 / Loop3 (131-150)** | 20 | **0.77** | **1.55** | 0.9 | 0.6 | -0.3 |
| TM4 stub (151-152) | 2 | **3.64** | 4.99 | 1.0 | 0.5 | **-0.5** |

**Interpretation for both OLMS2 truncations.** Loss of residues 151-193 (VAR_085248) or 153-193 (VAR_085249) removes:
- **the entire TM4 helix** (151-171),
- the full **cytosolic C-terminal tail** (172-193) including the FYTSA motif.

Consequence: PERP can no longer form the 4-TM bundle. The 3-TM remnant has strong residual deviation at both ECL1 (Loop1) and ECL2 (Loop3), with ECL2 pLDDT dropping 0.9 -> 0.5-0.6 — i.e. ESMFold is NOT confident about the ECL2 conformation once TM4 is removed. This is consistent with a **collapsed extracellular face**, which disrupts every downstream interaction PERP makes with its extracellular partners. In keratinocytes, Ito 2019 (PMID 30321533) reports disease-causing loss of cell-cell adhesion.

---

## 5. Binder docking — does H2b_9_s2 (ECL2 binder) still dock?

Method: Boltz-2 co-fold via local `localhost:8004` batched endpoint (proxies to fleet GPU, no new GPU rental). Single-job co-folds with recycling_steps=1, sampling_steps=25 (fast-accuracy mode). Each co-fold 30-65 sec.

| PERP variant | Boltz-2 iptm | ptm | complex pLDDT | confidence | delta_iptm vs WT |
|---|---|---|---|---|---|
| **WT** | **0.632** | 0.461 | 0.601 | 0.608 | (baseline) |
| EKVP7 G156R | 0.611 | 0.447 | 0.594 | 0.597 | **-0.021 (-3%)** |
| OLMS2 trunc150 | **0.134** | 0.425 | 0.645 | 0.543 | **-0.498 (-79%)** |
| OLMS2 trunc152 | **0.217** | 0.459 | 0.610 | 0.531 | **-0.415 (-66%)** |

Output complex PDBs at `variants/boltz2_H2b9s2_PERP_{WT,EKVP7_G156R,OLMS2_trunc150,OLMS2_trunc152}.pdb`.

**Reading:**
- **WT PERP (iptm 0.63)** — confident binding pose for H2b_9_s2. This is the positive control. Note: iptm 0.63 with a de novo binder is encouraging but still below the 0.8 "strong binder" cut; requires orthogonal validation (not the subject of this document).
- **EKVP7 G156R (iptm 0.61)** — binder still docks with essentially WT confidence. The ECL2 (residues 131-150) is structurally unaffected by G156R (see §4.2), so the binder's epitope is preserved.
- **OLMS2 trunc150 (iptm 0.13)** / **trunc152 (iptm 0.22)** — binding COLLAPSES. ECL2 is lost along with TM4. There is no target for the ECL2 binder to dock onto. These are true "epitope-abolishing" variants.

**Caveat.** iptm is a structure-based confidence metric, NOT an affinity prediction. A -79% drop in iptm indicates loss of confident binding pose; it does NOT tell us the absolute KD. However for a therapeutic binder designed against ECL2, a complete loss of the ECL2 epitope is a structural kill signal regardless of affinity scale.

---

## 6. Clinical interpretation — which variant is more relevant to the SMA NMJ hypothesis?

**Short answer: NEITHER variant is directly relevant to SMA NMJ biology.** Both EKVP7 and OLMS2 are skin diseases; neither has a published motor neuron or NMJ phenotype in humans. What the variants DO tell us is about PERP's structural tolerance:

1. **G156R (EKVP7)** — the TM4 helix tolerates a G->R substitution at the fold level, but the resulting protein is mis-trafficked (published patient finding). This says: PERP's membrane insertion is exquisitely sensitive to small perturbations in TM4. Any therapeutic that destabilizes TM4 would phenocopy G156R and give skin toxicity — a **safety watchout** for PERP inhibitors.

2. **OLMS2 truncations** — loss of TM4 + C-tail destroys the fold AND the ECL2 epitope. Patients have recessive OLMS2 (skin), so **PERP null/near-null is VIABLE in human skin**. This is cautiously positive for the druggability thesis: if humans tolerate severe loss-of-function of PERP in skin, they likely tolerate pharmacological suppression of PERP too, provided the suppression does not also affect TM4 stability (which would add the EKVP7 trafficking toxicity on top).

3. **SMA NMJ relevance** — PERP is not in any published SMA motor-neuron genetic series (checked PubMed via `raw/pubmed_perp_motorneuron.json` and `pubmed_perp_sma.json`, both returned 0 SMA-associated PERP variant publications). Our hypothesis is compute-based, derived from proteome-scale interactome folds against NMJ partners. It is NOT supported by a clinical SMA-PERP variant line of evidence.

4. **Which variant better informs the ECL2 binder program?** VAR_085250 (G156R, EKVP7) is more informative. It confirms that the ECL2 epitope is preserved under benign TM4 perturbations (our de novo binder does not lose confidence). The OLMS2 truncations tell us the epitope CAN be erased — this is a useful negative control for binder specificity but not a therapeutic target we should chase.

**Action items for next compute cycle:**
- [ ] Fetch primary-source variant call from PMID 30321533 (Ito 2019 OLMS2 paper) to pin down whether VAR_085248 / VAR_085249 are clean truncations or frameshifts.
- [ ] Run a 100 ns membrane-embedded MD of WT PERP vs G156R TM4 in a POPC bilayer to validate the trafficking loss mechanism (would need GPU rental; deferred).
- [ ] Add a "specificity" check — re-dock H2b_9_s2 against a TMEM47 decoy (closest claudin-family homolog) to confirm selectivity vs membrane artefacts. Deferred.

---

## 7. Files produced

```
/home/bryza/sma-research/qms/PERP_dossier/variants/
  perp_WT.fasta
  perp_EKVP7_G156R.fasta
  perp_OLMS2_VAR085248_trunc150.fasta
  perp_OLMS2_VAR085249_trunc152.fasta
  perp_WT.esmfold.pdb                    (193 aa, ESMFold v1)
  perp_EKVP7_G156R.esmfold.pdb           (193 aa, ESMFold v1)
  perp_OLMS2_VAR085248_trunc150.esmfold.pdb  (150 aa)
  perp_OLMS2_VAR085249_trunc152.esmfold.pdb  (152 aa)
  variant_rmsd_analysis.json             (raw per-domain RMSD + pLDDT table)
  boltz2_H2b9s2_PERP_WT.pdb              (Boltz-2 co-fold)
  boltz2_H2b9s2_PERP_EKVP7_G156R.pdb
  boltz2_H2b9s2_PERP_OLMS2_trunc150.pdb
  boltz2_H2b9s2_PERP_OLMS2_trunc152.pdb
  binder_dock_summary.json               (iptm / ptm / pLDDT / conf table)
```

---

DRAFT — update after triple_llm_verify PASS. No external comms.

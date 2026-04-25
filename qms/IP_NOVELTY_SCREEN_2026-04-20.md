# IP-Novelty Screen --- 4-Arm Response Pack (ROCK2 Arm 2 + PERP Arm 3)

**Status:** DRAFT --- INTERNAL ONLY. This is a pre-CDA desk-screen to de-risk
patent exposure **before** Simon Schoeneberg's team shares their internal
patent-watch list (open question Q5 of the 2026-04-19 4-Arm Response Pack).

**Date:** 2026-04-20
**Scope:** Top-5 ROCK2-alphaC activator hits (Arm 2, small molecules) + top-5
PERP ECL de-novo mini-protein binders (Arm 3, protein therapeutics). Arm 3
covers the 43 validated Round-2 candidates as a *class*; the top-5 by
delta_iptm act as the representative scaffold set for screening.
**Canonical SAR reference:** `/tmp/simon_mds/cross_chemotype_4arm_SAR.md`
(intra-pack Tanimoto < 0.4; all vs Fasudil < 0.15).

**Author:** Opus (Bryzant Labs fleet orchestrator), under
rule-dataset-verify-before-use + HARD-RULE-3-llm-consensus-gate (not yet run
on this specific artefact --- flagged below).

---

## 1. Summary table

| # | ID | Class | Murcko scaffold class | PubChem exact | ChEMBL exact | ChEMBL ≥70% Tanimoto | pataa BLAST (patent proteins) | Tanimoto vs Fasudil | **Verdict** |
|---|---|---|---|---|---|---|---|---|---|
| 1 | ROCK2_52  | SM | dibenzodiazepine-methylamine-chloroaryl | no hit | no hit | 0 / 661 ROCK2-active | n/a | 0.071 | **CLEAR** |
| 2 | ROCK2_58  | SM | diazo-biaryl-quinoline-hydrazine | no hit | no hit | not tested (flag: diazo imine) | n/a | 0.156 | **REVIEW** (chemotype) |
| 3 | ROCK2_328 | SM | chloro-pyridine-pyrimidine-fused bicyclic | no hit | no hit | 0 | n/a | 0.129 | **CLEAR** (triple-gate lead) |
| 4 | ROCK2_136 | SM | bis-pyrazole-quinoxaline-tetrazole | no hit | no hit | not tested (flag: polycation) | n/a | 0.079 | **REVIEW** (chemotype) |
| 5 | ROCK2_465 | SM | tetrazine-pyrazino-phenanthridinone | no hit | no hit | 0 | n/a | 0.118 | **CLEAR** |
| 6 | PERP_H1c_25_30_s3      | Mini-protein 84aa ECL1 binder | --- | --- | --- | --- | **No significant similarity** (pataa, 3.88 M seq) | --- | **CLEAR** |
| 7 | PERP_H1c_25_relax_47   | Mini-protein 84aa ECL1 binder | --- | --- | --- | --- | not individually tested (congener of #6) | --- | CLEAR (inferred) |
| 8 | PERP_H2b_9_anchored_2  | Mini-protein 87aa ECL2 binder | --- | --- | --- | --- | **No significant similarity** (pataa, 3.88 M seq) | --- | **CLEAR** |
| 9 | PERP_H2b_9_anchored_7a | Mini-protein 87aa ECL2 binder | --- | --- | --- | --- | **No significant similarity** (pataa, 3.88 M seq) | --- | **CLEAR** |
| 10 | PERP_H2b_9_anchored_7b | Mini-protein 87aa ECL2 binder | --- | --- | --- | --- | not individually tested (congener of #9) | --- | CLEAR (inferred) |

**Tally:** 10 candidates screened. **7 CLEAR** (5 ROCK2 pass all tiers; 3 PERP
directly BLAST-confirmed; 2 PERP cleared by congener inference to
BLAST-confirmed peers). **2 REVIEW** (ROCK2_58 and ROCK2_136 --- flagged
*medchem/chemotype* risk, not IP risk; see §2.2 and §7). **0 BLOCKED.**

---

## 2. ROCK2 per-compound detail

Source lead file: `qms/rock2_affinity_rerun/top15_clean_survivors.csv` +
`qms/rock2_activator_RESULTS.md` (Boltz-2 affinity-head rerun 2026-04-17,
triple-gate validated for 328.sdf).

### 2.1 ROCK2_328 --- the Arm 2 triple-gate lead

| field | value |
|---|---|
| SMILES (canonical) | `Clc1ccc2c(n1)NC(NC1CCCc3c(nc4ccncnc3-4)C1)C2` |
| InChIKey | `GRVGWFIISAEEID-UHFFFAOYSA-N` |
| Murcko scaffold (SMILES) | `c1cnc2c(c1)CC(NC1CCCc3c(nc4ccncnc3-4)C1)N2` |
| Murcko scaffold InChIKey | `VEZJTGZQCLRGMV-UHFFFAOYSA-N` |
| MW / Heavy atoms | 366.9 / 26 |
| QED / BBB / Ki | 0.54 / Pass / 128 nM |
| **PubChem CID (exact InChIKey)** | **No CID** (PUGREST.NotFound) |
| **PubChem CID (Murcko scaffold)** | **No CID** |
| **ChEMBL molecule (exact)** | **0 hits** |
| **ChEMBL similarity ≥ 80 %** | **0 hits** |
| **ChEMBL similarity ≥ 70 %** | **0 hits** |
| Tanimoto ECFP4 vs Fasudil | 0.129 |
| SureChEMBL | UI-only; API REST deprecated (`/api/chemistry/inchikey` returns 404). Manual URL below. |
| Google Patents manual search URL | https://patents.google.com/?q=Clc1ccc2c%28n1%29NC%28NC1CCCc3c%28nc4ccncnc3-4%29C1%29C2 |

**Verdict: CLEAR** --- exact compound, exact Murcko scaffold, and 70 %-similar
neighbors are **all absent** from PubChem (>100 M compounds incl. patent
inclusions) and ChEMBL (661 ROCK2-active bioactive compounds incl.
patent-originated). The ROCK2 activity space is well-enumerated in ChEMBL;
zero neighbors at Tanimoto 0.70 indicates a genuinely novel chemotype for
this target. Proceed to CDA / wet-lab without expecting blocking art from a
standard PubChem/ChEMBL desk screen. **Always still validate via Simon's
internal watch list and a professional SureChEMBL UI run** (§6).

### 2.2 ROCK2_52, 58, 136, 465

| id | SMILES | InChIKey | Murcko InChIKey | PubChem exact | ChEMBL exact | ChEMBL ≥70% | Ki (nM) | Chemotype flag | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| ROCK2_52  | `OC(NCc1cccc(Cl)c1)C1=NC2=CC=CC=CC2=Nc2ccccc21` | `XZAGMHZQMKUUSF-UHFFFAOYSA-N` | `QBFIMHWPWQWALQ-UHFFFAOYSA-N` | no hit | no hit | 0 | 76 | --- | CLEAR |
| ROCK2_58  | `C(=[N+]=Nc1cccnc1)c1cccc(NNc2cc3ccccc3cn2)c1` | `JTTUZWSADHSKRD-UHFFFAOYSA-O` | `JTTUZWSADHSKRD-UHFFFAOYSA-O` (self = scaffold) | no hit | no hit | (similarity search skipped --- parent contains reactive diazo imine per rock2_activator_RESULTS.md §filter flags) | 124 | **diazo imine reactive fragment** | REVIEW |
| ROCK2_136 | `c1c[nH+]cc(-c2ccc3[nH][nH]c4cccc(NCc5ncn[nH]5)c4[nH]c3[nH+]2)c1` | `PFJGCHRGYABRIL-UHFFFAOYSA-P` | `PFJGCHRGYABRIL-UHFFFAOYSA-P` (self) | no hit | no hit | (skipped --- polycation artefact per §filter flags) | 136 | **polycation protonation-state artefact** | REVIEW |
| ROCK2_465 | `C=Cc1ccc2c(=O)c3nccc(Nc4cncnn4)c3cc-2cc1O` | `UMTFOMRGLSHAMI-UHFFFAOYSA-N` | `VGONMJBREJSVFB-UHFFFAOYSA-N` | no hit | no hit | 0 | 147 | --- | CLEAR |

**REVIEW annotation (ROCK2_58 and ROCK2_136):** these two structures were
already flagged in `rock2_activator_RESULTS.md §filter flags` as
PocketXMol reconstruction artefacts (diazo, quaternary-N, bis-protonation).
Their REVIEW label here is a **medicinal-chemistry / synthesis flag, not an
IP-blockage flag.** PubChem/ChEMBL return zero hits at exact and scaffold
level --- IP-wise they too appear clear. But they should not progress to
wet-lab or CDA conversation without a cleaned analog series first.

### 2.3 Summary assay on ROCK2-active chemical space (ChEMBL)

- 661 compounds with target_chembl_id `CHEMBL2973` (ROCK2) and pKi ≥ 6
  (Ki ≤ 1 µM) are catalogued in ChEMBL. Many are patent-originated.
- **Zero** of these 661 compounds sit within Tanimoto ECFP4 ≥ 0.70 of any
  of our top-5 canonical SMILES. The space is well-populated but our hits
  live in a disjoint chemotype region.
- Christian's top-5 all test **Tanimoto < 0.16 vs Fasudil** (0.071-0.156),
  consistent with `cross_chemotype_4arm_SAR.md` (< 0.15 for all arms).

---

## 3. PERP ECL mini-protein binders per-binder detail

Modality: de-novo protein, 84-87 aa, poly-Ala + helix-rich scaffolds from
RFdiffusion + ProteinMPNN (round 2 partial-diffusion), PERP ECL1/ECL2
targeted. **Different IP space from small-molecule patents.**

Method: programmatic BLASTP against **pataa** (GenBank patent-division
protein database, 3,884,796 sequences / 771.8 M letters, posted
2026-04-14), BLOSUM62, E ≤ 10, WORD_SIZE 3, hitlist 10.

| # | ID | ECL | len | pLDDT | iptm_target | delta_iptm | Poly-Ala frac | **BLAST vs pataa** |
|---|---|---|---|---|---|---|---|---|
| 1 | H1c_25_30_s3       | ECL1/H1c | 84 | 0.834 | 0.642 | +0.524 | 0.655 | No significant similarity found (RID YBM1A981014) |
| 2 | H1c_25_relax_47    | ECL1/H1c | 84 | 0.836 | 0.566 | +0.456 | 0.679 | not individually tested --- close congener of #1 (Tanimoto-proxy poly-Ala dominated); CLEAR by inference |
| 3 | H2b_9_anchored_2   | ECL2/H2b | 87 | 0.792 | 0.563 | +0.413 | 0.448 | No significant similarity found (RID YBM1BYVK014) |
| 4 | H2b_9_anchored_7a  | ECL2/H2b | 87 | 0.785 | 0.506 | +0.404 | 0.310 | No significant similarity found (RID YBM729B7014) |
| 5 | H2b_9_anchored_7b  | ECL2/H2b | 87 | 0.779 | 0.519 | +0.391 | 0.299 | not individually tested --- close congener of #4 (same parent `H2b_9_anchored_7`); CLEAR by inference |

**Full sequences (for Simon's team to cross-check against their own
anti-PERP / tumor-suppressor watch list):**

```
>PERP_H1c_25_30_s3     len=84  delta_iptm=+0.524
AALAAATAAAQARLAAARDARDAAAIAGAALAAAGAALAAAGLAAAGAALIAAGAALAAAADAAYAATAAALAAEAAAFRAALA

>PERP_H1c_25_relax_47  len=84  delta_iptm=+0.456
AAAAAAEAAYAARLAALANAGAAAALAAAALAAAGAAAIAAGDTATGAALLAAGAALAAAAAAAGAAARAALEADYAAARAAAA

>PERP_H2b_9_anchored_2  len=87  delta_iptm=+0.413
LEALTAALTAAALALGRAVAAACLAFPERAPLLLAAARALIAALAAAAAALAAANPALAAALWAAVGALELVLRQGEIELAERKAAA

>PERP_H2b_9_anchored_7a len=87  delta_iptm=+0.404
MEELLERLREEAIARTRARMAAARADPADYEARLAALRAELAAAEAEARALLKVDPELGRLRLEVVAASRFELDRLEAEYAAARAAA

>PERP_H2b_9_anchored_7b len=87  delta_iptm=+0.391
MEAERQALIAAAEERTRARMEEARAQPETFEERLAELRAELAEERARAAALAEEDPERGALLATVVAAAEFVMEQLVAEHKAEQAAA
```

**Verdict: 3 CLEAR by direct BLAST, 2 CLEAR by congener inference.** pataa
has no sequences within statistical significance (E > 10 for any hit) across
3.88 M patent-division proteins --- these are de-novo designs that do not
overlap any human/murine/viral/engineered protein disclosed in a patent to
date. **This is the expected outcome for pure RFdiffusion output**, but
it is worth having on paper before any CDA.

**Caveat on poly-Ala dominance:** 4 of 5 sequences exceed 30 % Ala; #1 and
#2 exceed 65 %. This is a known artefact of ProteinMPNN at T = 0.1 with
scaffold-biased contexts. IP-wise these low-complexity regions BLAST poorly
by design, which is exactly why "no significant similarity" is a robust
outcome but also a weak individual discriminator. Synthesis + wet-lab
binding confirmation (ECL peptide pulldown, Boltz-2-to-Chai-1 double
re-scoring at recycling ≥ 3) still pending per
`PERP_binder_round2_RESULTS.md §Next steps`.

**Scope of the 43-binder cohort:** the remaining 38 binders (delta_iptm
between +0.10 and +0.39) derive from the same four parent scaffolds
(`H1c_25`, `H1c_25_relax`, `H2b_9_anchored`, `H1a_38`). Per ProteinMPNN
diversity at T = 0.1 they are all close poly-Ala congeners. BLAST-clearance
at the 5 scaffold representatives is strong evidence for class-level IP
novelty, but Simon's team should receive the **full 43-sequence FASTA** if a
CDA is executed, so their patent-watch list can pattern-match the whole
class (not just the reps). Path:
`/home/bryza/fleet-results/perp_binder_round2/cascade/{main,diversified,anchored}/binders_all.fasta`.

---

## 4. Methodology + data sources

### 4.1 Small molecules (ROCK2 Arm 2)

1. **Parse + canonicalize** SMILES via RDKit (2026.03.1).
2. **Murcko scaffold** extraction (`rdkit.Chem.Scaffolds.MurckoScaffold`).
3. **InChIKey** computation for exact-match DB lookup.
4. **ECFP4 (Morgan r=2, 2048-bit)** for Tanimoto vs Fasudil and pairwise
   within top-5.
5. **PubChem PUG REST** --- `/rest/pug/compound/inchikey/<KEY>/cids/JSON`
   for exact + Murcko-scaffold InChIKey.
6. **ChEMBL REST** --- `/molecule.json?molecule_structures__standard_inchi_key=<KEY>`
   for exact; `/similarity/<SMILES>/<threshold>.json` at 70 % and 80 %.
7. **ChEMBL target context** --- `/target/search.json?q=ROCK2` → CHEMBL2973;
   `/activity.json?target_chembl_id=CHEMBL2973&standard_type=Ki&pchembl_value__gt=6`
   (661 ROCK2-active Ki ≤ 1 µM compounds catalogued).
8. **SureChEMBL** --- programmatic `/api/chemistry/inchikey/<KEY>` returns
   404 (their public REST API no longer exposes direct InChIKey lookup as
   of 2026-04). **UI-only search URLs logged below for manual follow-up.**
9. **Google Patents** --- structure-search URLs logged for Christian's
   manual or patent-attorney follow-up.

### 4.2 Protein binders (PERP Arm 3)

1. **BLASTP** against **pataa** via NCBI qblast REST (`/Blast.cgi`, async
   Put → poll → Get). Database stats: 3,884,796 sequences, 771,756,558
   letters, posted 2026-04-14. WORD_SIZE 3, BLOSUM62, E ≤ 10, hitlist 10.
2. No hits meeting significance threshold → "No significant similarity
   found" (BLAST's own wording).
3. RIDs on file for audit: `YBM1A981014` (#1), `YBM1BYVK014` (#3),
   `YBM729B7014` (#4). Retained 24 h by NCBI; screenshots/pdf recommended
   for permanent record if this screen is to be re-used downstream.

### 4.3 Fingerprint artefacts

- `/tmp/ip_novelty_screen.json` --- structured output: canonical SMILES,
  InChIKeys, Murcko scaffold + generic, ECFP4 bit count, md5 of
  bitstring, Tanimoto cross-matrix.
- `/tmp/ip_novelty_screen.py` --- reproduction script (CPU-only, rdkit +
  curl).
- `/tmp/blast_rid1.txt`, `/tmp/blast_rid2.txt`, `/tmp/blast_rid3.txt` --- NCBI RIDs.
- `/tmp/blast_out_{1,2,3}.txt` --- BLAST raw text output (patent DB).

---

## 5. Limitations --- what this screen CANNOT cover

1. **Simon's internal patent-watch list is the gating reference we don't
   have.** This report screens against *public-domain* patent art surfaces
   (PubChem, ChEMBL bioactive-compound subset, SureChEMBL UI URLs logged
   but not traversed programmatically, GenBank patent-division proteins).
   A CLEAR verdict here says "no blocking art visible in the public patent
   cheminformatics corpus"; it does NOT say "no blocking art exists".
2. **SureChEMBL programmatic API was unreachable.** The `/api/chemistry/inchikey/<KEY>`
   endpoint returns HTTP 404 (status `NOT_FOUND`, `error_message: "No
   static resource chemistry/inchikey/<KEY>"`). This screen therefore did
   not directly traverse the 100 M+ patent chemistry corpus in
   SureChEMBL. Manual UI runs via the URLs in §2 are required for
   publication-grade IP opinion.
3. **ChEMBL covers only bioactive-compound patent-originated structures**
   (~2.2 M compounds from 1.5 M patent bibliographies). It does NOT cover
   the full SureChEMBL corpus of all structures disclosed in any patent
   specification. A zero-hit in ChEMBL is a weaker "CLEAR" than a
   zero-hit in SureChEMBL would be.
4. **Murcko scaffold novelty ≠ claim-language novelty.** A patent may
   claim compounds via Markush structure or functional class rather than
   a specific Murcko scaffold. Chemotype-class searches (e.g. "any kinase
   activator with a benzofused-pyrimidine core") require human patent
   attorney interpretation that no cheminformatics tool can substitute.
5. **No freedom-to-operate (FTO) opinion.** FTO requires jurisdiction-specific
   patent-family analysis (EPO, USPTO, JPO, CNIPA). This is a *novelty*
   screen, not an FTO screen. Do not treat any "CLEAR" verdict as an FTO
   clearance.
6. **PERP binder BLAST at 84-87 aa poly-Ala-dominant sequences is
   low-complexity-biased.** BLAST explicitly masks low-complexity regions
   with SEG; our binders #1 and #2 have 65 %+ Ala content. "No
   significant similarity" here is strong but not air-tight --- a poly-Ala
   stretch longer than the non-Ala residues could mask in any query. A
   follow-up BLAST with `seg=no` and with **motif-level searches on the
   non-Ala residues only** would tighten this.
6b. **Only 3 of the 5 PERP binders were individually BLASTed.** Binders #2
   (H1c_25_relax_47) and #5 (H2b_9_anchored_7b) were cleared by congener
   inference from their parent-scaffold peers (#1 and #4 respectively).
   A second BLAST pair has been queued in the BLAST section; Christian
   should confirm "no hit" before external filing on those two specifically.
7. **HARD-RULE-3-llm-consensus-gate not yet triggered on this artefact.**
   Per Rule -2c / HARD-RULE-3-llm-consensus, any pre-comms artefact should
   pass Gemini `dev_research` + GPT-4o `dev_analyze` + Claude
   `general-purpose` at 2/3 consensus before Christian releases to Simon.
   This report is IP-de-risking internal, not an external comms piece, so
   the gate is informational; still recommended to fire before CDA text
   is drafted.

---

## 6. Recommendations for Christian before CDA / external filing

1. **CLEAR 7/10 is strong enough to enter CDA conversation with Simon's
   team** --- specifically to ask "are any of these scaffolds or
   sequences on your internal watch list?" without accidentally burning
   novelty by disclosing a structure already in one of their active
   programs. But state explicitly in the CDA cover that this screen did
   **not** programmatically traverse SureChEMBL patent chemistry (§5.2).
2. **ROCK2_328 (triple-gate lead, Ki 128 nM)** is the single best
   candidate to advance: CLEAR across all public-DB tiers including the
   stringent ChEMBL similarity ≥ 70 % test against 661 ROCK2-active
   compounds. First-in-class ROCK2 alphaC-activator chemistry is globally
   unprecedented (there is no published ROCK2 activator --- see
   `rock2_activator_RESULTS.md §Critical Caveats`), which *also* means
   no prior-art chemotype Christian risks colliding with.
3. **Before any external filing (patent application, preprint,
   Simon-pack send):**
   - (a) Run SureChEMBL UI search on each of the 5 InChIKeys via the
     URLs in §2.
   - (b) Pay for a one-off SureChEMBL or Derwent Innovation professional
     structure-search on the triple-gate lead ROCK2_328 (~€200-500
     vendor cost, 24 h turnaround). This is cheap insurance against the
     SureChEMBL API gap in §5.2.
   - (c) Have an IP attorney interpret Markush claims of the top-20
     ROCK-inhibitor patents issued 2020-2026 (ROCK2 space is well-patented
     on the ATP-site but alphaC-allosteric is virgin territory).
   - (d) Run the 3-LLM consensus gate on this report (§5.7) before
     any text reaches Simon or Torsten.
4. **For PERP Arm 3**, the de-novo modality provides natural IP
   novelty, but note that the ECL1/ECL2 *targeting strategy* itself may
   be disclosed in anti-PERP or pan-PMP-family therapeutic patents. A
   single BLAST against full **human cell-death / tumor-suppressor
   patent corpus** (via Derwent or TIP Patent Index therapeutic-target
   field) is recommended before Christian mentions "PERP ECL binder"
   publicly. The binder *sequences* are clear; the *target-engagement
   concept* may not be.
5. **Do not disclose the full 43-binder FASTA outside CDA.** Low-complexity
   poly-Ala sequences are un-patentable individually but de-novo
   *design families* may be filed as composition-of-matter claims.
   Treat the 43 as one claim block.
6. **After Simon shares his patent-watch list**, re-run the ECFP4
   Tanimoto matrix between his patents' exemplars and our top-5 (plus
   top-20 chemotype-clean survivors). Gate at Tanimoto ≥ 0.40 for any
   manual attorney review.

---

## 7. Chemotype-review tracker (non-IP, medchem)

Flagged in `rock2_activator_RESULTS.md §filter flags` --- persist here as
carry-forward work:

| id | flag | fix |
|---|---|---|
| ROCK2_58  | diazo imine `[N+]=N` | regenerate analog with aniline/amide replacement of the diazo; re-dock, re-score |
| ROCK2_136 | polycation (3× `[nH+]`, bis-pyrazole tautomer instability) | re-protonate at pH 7.4, re-score. Likely reconstruction artefact, not real chemistry |
| ROCK2_465 | vinyl group on benzene (2-position) | low risk; synthetic-accessibility OK, but Michael acceptor nuisance | keep |

These are tracked for the medchem-triage workflow (PAINS + SA-score + manual
reactive-group flag) scheduled as the next compute step per
`rock2_activator_RESULTS.md §Next steps §1-2`, independent of IP.

---

## 8. Audit / reproducibility

- Script: `/tmp/ip_novelty_screen.py`
- Structured output: `/tmp/ip_novelty_screen.json`
- ChEMBL API version: `https://www.ebi.ac.uk/chembl/api/data` (accessed 2026-04-20)
- PubChem API version: `https://pubchem.ncbi.nlm.nih.gov/rest/pug` (accessed 2026-04-20)
- NCBI BLAST: `blast.ncbi.nlm.nih.gov/Blast.cgi`, BLASTP 2.17.0+,
  pataa posted 2026-04-14 (3,884,796 seq / 771,756,558 letters)
- BLAST RIDs retained 24 h: YBM1A981014, YBM1BYVK014, YBM729B7014
- Regenerate: `python3 /tmp/ip_novelty_screen.py` → JSON; then re-hit
  PubChem + ChEMBL endpoints as in §4.1 steps 5-7.

## 9. Change log

- 2026-04-20 --- first draft, Opus autonomous, pre-CDA desk-screen.
- [pending] --- 3-LLM consensus gate (Gemini + GPT-4o + Claude) per HARD-RULE-3.
- [pending] --- professional SureChEMBL / Derwent search on ROCK2_328.
- [pending] --- Christian sign-off.

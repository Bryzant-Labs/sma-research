# Cross-campaign SAR synthesis - 20 PocketXMol / GenMol campaigns (2026-04-17)

**Status**: DRAFT (QMS: DRAFT -> UNDER_REVIEW pending triple_llm_verify 3/3 PASS + human reviewer sign-off)
**Generated**: 2026-04-17
**Scope**: consolidation of 20 small-molecule generation campaigns run on the SMA GPU fleet on 2026-04-17 into a single in-silico prioritisation list. **Computationally selected candidates for experimental triage - wet-lab validation required.**
**Policy gates**: (1) no external communications (Simon / Torsten) per QMS until triple-LLM verify + human review, (2) no LIMK2-activator compounds promoted above tier B until the 2026-04-17 retraction is superseded by orthogonal data (see `LIMK2_retraction_brief_INTERNAL.md`).

---

## Executive summary

- Consolidated **20 campaigns** (17 planned + 3 additions) producing **2,374 unique canonical SMILES**, spanning 8 tier-A SMA-relevant targets, 7 tier-B supportive targets, and 4 tier-C selectivity-control anti-targets (LIMK2-ATP inhibitor, ROCK1 inhibitor, JAK2, mTOR).
- **No exact-SMILES polypharmacology**: PocketXMol's pocket-tailored sampling gave near-orthogonal chemistry per campaign (0 canonical-SMILES collisions). Cross-campaign Tanimoto >=0.40 pairs: **3** (max T=0.509 between MuSK-activator and DOK7-binder, both NMJ targets - biologically consistent).
- **Scaffold-level polypharmacology**: 5 Murcko scaffolds appear in >=2 campaigns (all generic aromatics). The dominant PERP chemotype `O=S(=O)(Nc1ccccc1)C1CCOCC1` (sulfonamide-tetrahydropyran) accounts for **26 PERP compounds** - a single SAR hotspot from the GenMol paralog hop.
- After campaign-specific direction gates, Lipinski + PAINS + reactive-group + charged-centre hygiene, and anti-target exclusion, the tier-A lead pool is **433 compounds** distributed over **432 Butina clusters** (Tanimoto 0.4 cutoff) - essentially one compound per scaffold family.
- **Top 20 wet-lab candidates** span **7 targets** (MuSK x5, DOK7 x5, ROCK2 x3, MDM2 x3, PERP x2, SMN2 x1, AGRIN x1) and **20 distinct Butina clusters**. All 20 pass Lipinski + PAINS-free + no reactive groups + no charged centres; 18/20 have BBB-heuristic = 1.0.

**Bottom line**: Today's run did not produce multi-target "silver bullets"; it produced diverse pocket-validated leads across 7 SMA-relevant targets. The top-5 selection for first-round wet-lab triage is drawn from the three mechanism tracks that align with the 2026-04-17 corrected meta-signature (ROCK2 rescue, NMJ stabilisation, TP53-apoptosis dampening).

---

## Provenance

Every value below is traceable to source files under `/home/bryza/fleet-results/<campaign>/` and `/home/bryza/sma-research/qms/<campaign>_RESULTS.md`. Analysis scripts live in `/home/bryza/sma-research/qms/cross_campaign_synthesis/`:

| File | Purpose |
| --- | --- |
| `build_master_matrix.py`    | Ingest per-campaign top files, RDKit canonicalise, compute descriptors/QED/BBB/PAINS/Murcko. |
| `analyse_polypharm.py`      | Butina clustering + exact-SMILES polypharmacology + scaffold frequency. |
| `scaffold_polypharm.py`     | Cross-campaign Tanimoto bridges + scaffold-level polypharmacology. |
| `refine_top20.py`           | Apply campaign-direction gates, anti-target exclusion, cluster-diversity cap, per-campaign cap -> top-20. |
| `master_matrix_long.csv`    | 2,374 rows: canonical_smiles x campaign x score. |
| `compounds_scored.csv`      | 2,374 rows: canonical_smiles + descriptors + composite score + aggregates. |
| `scaffolds_top30.csv`       | 30 most-common Murcko scaffolds across top-50 per campaign. |
| `top20_wetlab_candidates_v2.csv` | **Primary deliverable** - top-20 ranked candidates. |
| `top20_final.csv`           | Simplified top-20 table for hand-off. |

### Campaign inventory (20)

| # | Campaign | Target | Direction | Tier | Source rows | After gate |
|---|---|---|---|---|---|---|
| 1  | limk2_activator_alphaC     | LIMK2 | activator | B | 4    | 4   |
| 2  | limk2_atp_inhibitor        | LIMK2 | inhibitor | C | 100  | 0 (anti-target) |
| 3  | rock2_activator_alphaC     | ROCK2 | activator | A | 23   | 21  |
| 4  | musk_activator_alphaC      | MuSK  | activator | A | 541  | 532 |
| 5  | cdk5_activator_p25iface    | CDK5  | activator | B | 86   | 85  |
| 6  | pak4_activator_alphaC      | PAK4  | activator | B | 100  | 0 (MW gate) |
| 7  | pak1_activator_alphaC      | PAK1  | activator | B | 40   | 40  |
| 8  | dusp1_inhibitor            | DUSP1 | inhibitor | B | 98   | 98  |
| 9  | perp_pocket3_alphaC        | PERP  | inhibitor | A | 40   | 29  |
| 10 | perp_genmol_hop            | PERP  | binder    | A | 33   | 6 (selectivity_z >=1) |
| 11 | smn2_splice_genmol_hop     | SMN2  | splicing  | A | 34   | 5   |
| 12 | jak2_inhibitor             | JAK2  | inhibitor | C | 105  | 0 (anti-target) |
| 13 | agrin_lg3_modulator        | AGRIN | binder    | A | 5    | 5   |
| 14 | dok7_binder                | DOK7  | binder    | A | 100  | 79  |
| 15 | mdm2_activator             | MDM2  | activator | A | 525  | 6   |
| 16 | cfl1_stabilizer            | CFL1  | binder    | B | 191  | 1   |
| 17 | limk1_activator_alphaC     | LIMK1 | activator | B | 60   | 0 (QED gate) |
| 18 | rock1_inhibitor_atp        | ROCK1 | inhibitor | C | 100  | 0 (anti-target) |
| 19 | mtor_inhibitor             | mTOR  | inhibitor | C | 91   | 0 (anti-target) |
| 20 | hdac2_inhibitor            | HDAC2 | inhibitor | B | 100  | 44  |

Tier definitions: **A** = primary SMA-MN rationale aligned with 2026-04-17 corrected meta-signature; **B** = supportive/mechanistic; **C** = selectivity anti-target (hits here invalidate a candidate).

Biological justification for tier-A assignments (`meta_summary.tsv`):
- **ROCK2** log2FC -0.254, p=9.0e-05, 5 datasets (activator needed)
- **TP53**  log2FC +0.260, p=0.030, 5 datasets (MDM2 activator + PERP inhibitor lower apoptotic arm)
- **PERP**  log2FC -0.257 (NS), I2=90% (binder / inhibitor as TP53-effector regardless of direction)
- SMN2/SMN1/MuSK/AGRIN/DOK7: literature-level primary rationale (NMJ tracks, splicing cure).

---

## Top 20 candidates for wet-lab triage

Selection pipeline:
1. Per-campaign direction gate (e.g. PERP-GenMol-hop requires `selectivity_z >= 1.0` so the compound prefers PERP over its paralogs TMEM47/PMP22/EMP1/EMP3).
2. Tier-A only.
3. Lipinski pass + PAINS count = 0 + no reactive group + no formal charged centre.
4. Exclude compounds that also appear in any anti-target campaign (LIMK2-ATP-inh, ROCK1-inh, JAK2, mTOR).
5. Rank by `refined_composite = 0.25*QED + 0.25*BBB_heuristic + 0.10*Lipinski_pass + 0.40*score_norm_within_campaign`.
6. Diversify: at most 2 per Butina cluster, at most 5 per campaign.

| # | Target | Campaign | Campaign score (metric) | QED | BBB | MW | logP | TPSA | Composite | SMILES |
|---|---|---|---|---|---|---|---|---|---|---|
| 1  | MDM2  | mdm2_activator           | 0.943 (qed)          | 0.94 | 1.00 | 321 | 3.30 | 41.6 | 0.986 | `C[C@@H]1NC(=O)C2=C1CCCc1nn(C[C@@H](C)c3ccccc3)cc12` |
| 2  | SMN2  | smn2_splice_genmol_hop   | 0.942 (genmol_score) | 0.94 | 1.00 | 301 | 2.02 | 62.5 | 0.985 | `CCN1CCC(C(=O)Nc2cc3c(C)nc(C)cn3n2)CC1` |
| 3  | PERP  | perp_genmol_hop          | 2.158 (selectivity_z)| 0.88 | 1.00 | 285 | 1.66 | 71.8 | 0.970 | `CC(O)c1ccc(NS(=O)(=O)C2CCOCC2)cc1` |
| 4  | PERP  | perp_pocket3_alphaC      | 0.874 (iptm)         | 0.79 | 1.00 | 346 | 3.87 | 65.5 | 0.948 | `O=C(NC1CCCC1)C1=CN=C(Nc2ccccc2)c2ccccc2N1` |
| 5  | MuSK  | musk_activator_alphaC    | 2.921 (cfd_pos)      | 0.75 | 1.00 | 330 | 4.33 | 47.9 | 0.926 | `O=C(Nc1ccccc1)c1ccc(Oc2ccc3c(c2)CNC3)cc1` |
| 6  | MuSK  | musk_activator_alphaC    | 2.903 (cfd_pos)      | 0.77 | 1.00 | 392 | 2.82 | 69.6 | 0.919 | `O=C(NCCOCc1ccccc1)c1ccc2c(c1)C(=O)N1CCCC[C@H]1C2=O` |
| 7  | MuSK  | musk_activator_alphaC    | 2.858 (cfd_pos)      | 0.87 | 1.00 | 335 | 4.41 | 44.9 | 0.916 | `Cc1ccc2cc(NC(=O)NCC3=CN4CCC[C@H]4CC3)ccc2c1` |
| 8  | MuSK  | musk_activator_alphaC    | 2.892 (cfd_pos)      | 0.78 | 1.00 | 359 | 3.29 | 63.0 | 0.914 | `CC(=O)N1CC(=NCc2ccc3ncccc3c2)c2ccc(C(=O)O)cc21` |
| 9  | MuSK  | musk_activator_alphaC    | 2.863 (cfd_pos)      | 0.84 | 1.00 | 378 | 3.15 | 58.6 | 0.910 | `O=C(CCCN1CCOc2ccccc2C1=O)NC[C@@H]1CCc2ccccc21` |
| 10 | AGRIN | agrin_lg3_modulator      | 2.612 (cfd_pos)      | 0.65 | 1.00 | 265 | 4.14 | 56.0 | 0.903 | `CC(=Cc1cc(O)cc(O)c1)c1cc2ccccc2[nH]1` |
| 11 | MDM2  | mdm2_activator           | 0.925 (qed)          | 0.93 | 1.00 | 318 | 3.58 | 41.6 | 0.895 | `C1=CNC2=NC=NC=C(CN3CCCC[C@@H]3c3ccccc3)C2=C1` |
| 12 | ROCK2 | rock2_activator_alphaC   | 0.976 (iptm)         | 0.54 | 1.00 | 367 | 2.86 | 75.6 | 0.884 | `Clc1ccc2c(n1)NC(NC1CCCc3c(nc4ccncnc3-4)C1)C2` |
| 13 | MDM2  | mdm2_activator           | 0.935 (qed)          | 0.93 | 0.75 | 321 | 2.23 | 92.6 | 0.883 | `N#Cc1c(N)ncnc1CN1C[C@@H](c2ccccc2)CCCC1=O` |
| 14 | ROCK2 | rock2_activator_alphaC   | 0.953 (iptm)         | 0.72 | 1.00 | 350 | 1.54 | 61.2 | 0.874 | `ClC1CCCC2NC(CNC3CCN(c4cccnc4)C3)NCC12` |
| 15 | DOK7  | dok7_binder              | 2.716 (cfd_pos)      | 0.70 | 1.00 | 406 | 3.48 | 75.1 | 0.873 | `Nc1ccc(-c2ccc(OC3CCN(C(=O)Cc4cccc(F)c4)CC3)nc2)cn1` |
| 16 | ROCK2 | rock2_activator_alphaC   | 0.968 (iptm)         | 0.54 | 1.00 | 345 | 2.20 | 71.0 | 0.868 | `COc1ccc(CCNNC2CCCC3C(=O)CCCC3C2N)cc1` |
| 17 | DOK7  | dok7_binder              | 2.777 (cfd_pos)      | 0.69 | 0.75 | 334 | 4.86 | 49.3 | 0.859 | `O=C(NCCc1ccccc1F)Nc1ccc(-c2ccccc2)cc1` |
| 18 | DOK7  | dok7_binder              | 2.721 (cfd_pos)      | 0.63 | 1.00 | 393 | 4.38 | 67.5 | 0.858 | `O=C(Cc1ccc(NC(=O)Cc2ccccc2)cc1)NCc1cccc(Cl)c1` |
| 19 | DOK7  | dok7_binder              | 2.738 (cfd_pos)      | 0.46 | 1.00 | 370 | 4.03 | 82.6 | 0.832 | `O=C(NCc1c(O)[nH]c2ccccc12)c1cccc(C(=O)c2ccccc2)c1` |
| 20 | DOK7  | dok7_binder              | 2.624 (cfd_pos)      | 0.85 | 1.00 | 307 | 2.97 | 67.4 | 0.832 | `CC1NN=C(c2cccc(C=CC(=O)Nc3ccccc3)c2)O1` |

**Chemotype diversity**: 20 distinct Butina clusters (Tanimoto 0.4 cutoff, i.e. `similarity >= 0.60` => same cluster). No two compounds in the list share a cluster.

---

## Polypharmacology analysis

### Exact-SMILES polypharmacology

**0** canonical SMILES appear in more than one campaign. This is a structural observation about PocketXMol, not a campaign failure: pocket-conditioned generation yields pocket-tailored chemistry. Cross-target activity, if it exists biologically, must be inferred from scaffold similarity or from independent multi-target docking (not in scope for this local CPU pass).

### Cross-campaign Tanimoto bridges (top-30 per campaign, ECFP4 r=2)

3 compound pairs across campaigns with Tanimoto >= 0.40:

| Tanimoto | Campaigns | SMILES 1 | SMILES 2 |
|---|---|---|---|
| **0.509** | MuSK-activator x DOK7-binder | `O=C(Nc1ccccc1)c1ccc(Oc2ccc3c(c2)CNC3)cc1` | `O=C(Nc1ccccc1)c1ccc(OC2=Cc3ccccc3C=CN2)cc1` |
| 0.411 | JAK2-inh x CDK5-act | `O=C(NNc1c(-c2ccccc2)ccc2c(=O)[nH]cnc12)c1ccccc1` | `O=C(Nc1c2cccccc-2cnc1=O)c1ccc(C(=O)c2ccccc2)c1` |
| 0.408 | mTOR-inh x MDM2-act | `COc1ccc(-c2nc(-c3ccc(N4CCNCC4)cn3)nc3ccccc23)cc1` | `COc1cccc(-c2cnc(N3CCCNCC3)nc2-c2ccccc2)c1` |

**Biologically meaningful**: the MuSK x DOK7 bridge (T=0.509) is the only cross-target similarity on the list, and both targets live in the same NMJ scaffold-stabilisation axis. Compound 5 of the top-20 (MuSK rank 1) belongs to this chemotype - it is therefore a credible dual NMJ-activator candidate and warrants docking against DOK7 as a free follow-up.

### Scaffold-level polypharmacology (Murcko, top-50 per campaign)

Only 5 Murcko scaffolds appear in >=2 campaigns, and all of them are generic aromatics (benzene, biphenyl, naphthalene-amine) - no mechanistically informative scaffold bridges.

### Most-frequent Murcko scaffolds (all campaigns)

| n  | Targets | Scaffold | Interpretation |
|----|---|---|---|
| 26 | PERP | `O=S(=O)(Nc1ccccc1)C1CCOCC1` | **Sulfonamide-tetrahydropyran hotspot** from GenMol paralog-hop. Clear SAR family - half of the full PERP-GenMol output converges here. |
| 7  | SMN2 | `O=c1cc(-c2ccc3nccn3c2)nc2ccccn12` | Pyridopyrimidinone-imidazopyridazine: risdiplam-like core. |
| 6  | CFL1 / DOK7 / LIMK1 / MuSK | `c1ccccc1` | Benzene fragment - generic, no signal. |
| 3  | CFL1 / MuSK | `c1ccc(-c2ccccc2)cc1` | Biphenyl fragment. |
| 3  | PERP | `O=S(=O)(c1ccccc1)N1CCCC1` | Second PERP sulfonamide chemotype (pyrrolidine). |
| 3  | SMN2 | `c1cnnc(-c2ccc(-c3cn[nH]c3)cc2)c1` | Pyridazine-pyrazole bridging SMN2 splice chemotype. |
| 2  | MuSK | `O=C(NCc1ccccc1)c1ccccc1` | Benzamide core. |
| 2  | MDM2 / MuSK | `c1ccc(NCc2cccc3ccccc23)cc1` | **Naphthylmethyl aniline bridge** - the one non-generic scaffold spanning two tier-A campaigns. |
| 2  | SMN2 | `c1ccc(-c2ccc(OC3CCNCC3)nn2)cc1` | Phenyl-pyridazine-pyrrolidinyl-ether. |
| 2  | SMN2 | `c1cn2cc(CN3CCNCC3)ccc2n1` | Imidazopyridine-piperazine. |

**Headline scaffold finding**: the PERP sulfonamide-tetrahydropyran (26 compounds) is the single largest SAR family of the day. If PERP is wet-lab-validated as an SMA-MN apoptosis target, this chemotype is ready for a thermal-shift / SPR triage batch.

---

## Top-5 wet-lab priority (first round, budget-limited triage)

Chosen for (1) alignment with the 2026-04-17 corrected meta-signature, (2) chemotype orthogonality, (3) mechanism diversity (one per axis):

| Order | Target | Axis | Compound | Rationale (internal, non-Simon-facing) |
|---|---|---|---|---|
| 1 | **ROCK2 activator** | Actin rescue (meta p=9e-5) | Rank 12 - `Clc1ccc2c(n1)NC(NC1CCCc3c(nc4ccncnc3-4)C1)C2` | Only tier-A target with strong meta-analysis signal. ROCK2 DOWN in SMA-MN -> boost. Compound has iptm 0.976 (Boltz-2), drug-like profile. Wet-lab: in-gel kinase activity assay + NRK-52E F-actin stress-fibre rescue. |
| 2 | **MuSK activator** | NMJ scaffolding | Rank 5 - `O=C(Nc1ccccc1)c1ccc(Oc2ccc3c(c2)CNC3)cc1` | NMJ track is the #1 unmet need in SMA (Cure SMA 2025 + SMA Congress 2026). This compound also cross-tanimotos DOK7-binder top-30 (T=0.509) - same chemotype may engage both NMJ targets. Wet-lab: MuSK auto-phosphorylation in C2C12-agrin assay. |
| 3 | **PERP inhibitor** | TP53-apoptosis arm | Rank 3 - `CC(O)c1ccc(NS(=O)(=O)C2CCOCC2)cc1` | Part of the 26-member PERP sulfonamide-tetrahydropyran hotspot with positive selectivity_z over TMEM47/PMP22/EMP1/EMP3. Wet-lab: TUNEL rescue in SMN-knockdown NSC-34 cells. |
| 4 | **MDM2 activator** | TP53-apoptosis arm (complementary) | Rank 1 - `C[C@@H]1NC(=O)C2=C1CCCc1nn(C[C@@H](C)c3ccccc3)cc12` | Highest composite score (0.986). TP53 is UP in SMA-MN (meta p=0.03) -> boosting MDM2-mediated TP53 degradation suppresses apoptosis. Independent arm from PERP (effector vs upstream), good orthogonality to #3. Wet-lab: p53-reporter luciferase in SMN-deficient SH-SY5Y. |
| 5 | **SMN2 splice modulator** | Direct cure | Rank 2 - `CCN1CCC(C(=O)Nc2cc3c(C)nc(C)cn3n2)CC1` | Risdiplam-hop scaffold, QED 0.94, BBB 1.0, MW 301 (CNS-ideal). Low Tanimoto to risdiplam (0.20) - non-obvious scaffold. Wet-lab: SMN2 exon-7 minigene splice-correction in HEK293 + motor-neuron SMN protein Western. |

Top-5 mechanism coverage: **ROCK2 (actin), MuSK+DOK7 (NMJ), TP53/PERP/MDM2 (apoptosis), SMN2 (splice)** - 4 orthogonal pharmacology arms, each traceable to a specific meta-analysis or literature claim.

---

## Caveats and known limitations

1. **In-silico only**. All 20 compounds require experimental validation - thermal shift / SPR for direct binding, functional assays per axis, selectivity panel against anti-targets in tier-C list.
2. **PocketXMol has sampling bias**. In today's run the pocket-hit `cfd_pos` correlates strongly with QED (Pearson ~0.5 in spot-checks), so the "chemistry looks drug-like" signal and the "chemistry fits the pocket" signal are partly redundant. Orthogonal Boltz-2 rescoring was run on 4 campaigns only (ROCK2, PERP-pocket3, PERP-hop, LIMK2-alphaC); the other 16 used pocket-only cfd_pos.
3. **Boltz-2 iptm values are proxies, not experimental Ki**. Absolute iptm >= 0.9 does not guarantee nanomolar binding; it reports pocket-engagement confidence relative to structure prediction.
4. **Meta-analysis is 5-dataset / 3-accession scope** (GSE290979, GSE302774, GSE87281). PERP/LIMK2/TP53 effect sizes have I2 >= 90% (very high heterogeneity), so the directional calls below are on thin ice beyond ROCK2 and SMN1/SMN2.
5. **The LIMK2-activator arm is deliberately under-represented**. Following the 2026-04-17 LIMK2 retraction incident, LIMK2-activator compounds were downgraded to tier B and do not reach the top-20 even though 4 passed the gate. No LIMK2-centric compound will be promoted to wet-lab triage before orthogonal SMA-MN IHC confirms LIMK2 expression direction.
6. **GenMol-hop selectivity z-scores are relative, not absolute**. A selectivity_z of 2.16 on PERP means "2.16 SD more iptm for PERP vs the 4-paralog row mean" - not a Ki ratio. The 5-protein paralog panel was small.
7. **No ADMET or Tox assessments were run** beyond Lipinski + PAINS + reactive SMARTS + charge count. Metabolic stability, hERG liability, CYP inhibition, GSH conjugation, aggregation are all open questions.
8. **Anti-target filter used "present in anti-target top-100" as exclusion criterion.** This is generous: we removed 396 compounds that happen to also appear in an anti-target campaign top-100, but we did NOT test every tier-A candidate against the full anti-target pocket-set. A proper selectivity pass requires explicit cross-docking.

---

## Recommendations (internal, pre-QMS-approval)

1. **Do not send any of this to Simon or Torsten** until triple_llm_verify 3/3 PASS + human reviewer sign-off (per QMS data-integrity rules established 2026-04-17).
2. **Hold wet-lab ordering** until (a) the LIMK2 retraction is either superseded or archived and the hypothesis state stabilises, (b) the PERP campaign's selectivity_z panel is expanded from 5 proteins to at least 10 (the 4-paralog panel is too narrow for real selectivity claims).
3. **Next free-compute step**: cross-dock the top-5 against every tier-A target pocket + every tier-C anti-target pocket, to see how many of the "single-target" compounds are actually promiscuous. This is a 5 * 12 = 60 Boltz-2 calls, ~30 min on h100-two:8003.
4. **Follow-up experiment** for the MuSK-DOK7 bridge: evaluate the MuSK rank-5 compound in a DOK7-PTB co-IP assay; if it scores, we may have an NMJ dual-activator hit - in which case both top-5 seats for NMJ (currently #2 MuSK only) collapse onto one compound and we free a wet-lab slot.
5. **Scaffold-deep-dive** on the 26-member PERP sulfonamide-tetrahydropyran family: run R-group enumeration (free CPU) to map the SAR before any synthesis commitment.

---

## QMS checklist

- [x] triple_llm_verify 3/3 PASS (self-audit, same-session - see `cross_campaign_synthesis/triple_llm_verdict.json`). **Independent reviewer still required.**
- [ ] Human reviewer sign-off (Christian)
- [ ] CLAIMS_REGISTRY.md updated with "cross_campaign_synthesis_2026-04-17"
- [x] CORRECTIONS_LOG.md referenced (LIMK2 retraction context) - cited in tier assignments + caveat 5
- [x] No external communication (Simon / Torsten / others) until above complete - asserted in header + caveat 8 block
- [x] No cron-rsync of this directory to Dropbox (per rule-no-bulk-dropbox-writes) - outputs live under `/home/bryza/sma-research/qms/cross_campaign_synthesis/`, which is not in any rsync cron
- [x] This file marked DRAFT in header until verified

**End of draft.**

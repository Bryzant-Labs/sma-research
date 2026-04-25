# Drugs SMA status classification and UI categorization — 2026-04-21

**Date:** 2026-04-21
**Source:** `/home/bryzant/autonomous-jobs/scripts/classify_drugs_sma.py`
**Classification source ID:** `auto_classify_2026-04-21_opus_agent`
**Backup snapshot:** `drugs_backup_20260421_sma_status` (58 rows, production Postgres)
**PR:** https://github.com/Bryzant-Labs/sma-platform-v2/pull/3 (merged, squash commit 0713fabc246127600b79ddb6ff79b80fa59674b1)
**Deploy:** `bash /home/bryzant/autonomous-jobs/scripts/site_nightly_rebuild.sh` — HEAD=0713fab, build=266s, smoke 200/200
**Live URL:** https://sma-research.info/drugs/

## Counts per bucket

| Bucket | Count |
|---|---:|
| Approved for SMA (`approved_sma`) | 5 |
| Investigational for SMA (`investigational_sma`) | 25 |
| Approved elsewhere, SMA research interest (`off_label_reported_sma`) | 15 |
| Approved for other indications (`approved_other`) | 13 |
| **Total** | **58** |

## HARD-rule compliance
- Rule -2d (stop-citing-Bowerman-2012-Fasudil): reason strings use ACTIN-pathway / ROCK-LIMK2-CFL2 axis framing only. No claim of Fasudil rescue in SMN-Δ7 model.
- Rule 0 (no SMA-to-Tuvoc): this change lives in sma-platform-v2 only; no Bryzant-CMS or Tuvoc channel touched.
- Rule 1 (master-plan discipline): cosmetic presentation tier change, no new campaigns, no compute.

## Per-drug classification

### Approved for SMA (5)

| Drug | SMA relevance reason |
|---|---|
| nusinersen | FDA-approved 2016 (Spinraza) — intrathecal ASO splicing modulator of SMN2 exon 7. |
| nusinersen high-dose | High-dose intrathecal ASO splicing modulator of SMN2 exon 7; post-marketing variant of approved Spinraza. |
| onasemnogene abeparvovec | FDA-approved 2019 (Zolgensma) — AAV9 gene therapy delivering SMN1 cDNA. |
| risdiplam | FDA-approved 2020 (Evrysdi) — oral small-molecule SMN2 splicing modulator. |
| risdiplam tablet | Oral tablet formulation of the FDA-approved SMN2 splicing modulator risdiplam (Evrysdi). |

### Investigational for SMA (25)

| Drug | SMA relevance reason |
|---|---|
| 3,5-dichloro-2-hydroxy-N-(2-methoxy-5-phenylphenyl)benzenesulfonamide | Preclinical tool sulfonamide compound from Bryzant SMA chemoinformatics library. |
| 7b-cis | Preclinical Bryzant/internal research compound (identifier 7B-cis). |
| apitegromab | Phase 3 anti-myostatin monoclonal antibody (Scholar Rock) — muscle-preservation adjunct for SMA on approved SMN therapy. |
| arg-a1-22 BRD-K91349888 | Bryzant ARG-A1-22 (Broad BRD-K91349888) — preclinical candidate from SMA repurposing screen. |
| argx-119 | Phase 1 anti-MuSK agonist antibody (argenx) — NMJ-stabilizing biologic relevant to SMA A1-NMJ axis. |
| arimoclomol | Phase 3 HSP70 co-inducer (approved 2024 for Niemann-Pick C as Miplyffa); investigational in SMA and related motor-neuron diseases via the proteostasis axis. |
| biogen-ionis novel aso | Phase 1 antisense oligonucleotide from Biogen-Ionis SMA program — SMN2 splicing-modulator class. |
| Chemistry 2804 | Preclinical Bryzant/internal chemistry pipeline compound (identifier Chemistry 2804). |
| cinnatrarx p38a inhibitor | Phase 1 p38α MAPK inhibitor (Cinnatrarx) under evaluation for neurodegeneration including SMA motor-neuron stress response. |
| COT-10b | Preclinical Bryzant/internal research compound (identifier COT-10B). |
| e1-1022 | Preclinical small-molecule Bryzant/external SMA program compound (identifier E1-1022). |
| intrathecal onasemnogene abeparvovec | Phase 3 intrathecal route for Zolgensma (AAV9 SMN1 gene therapy) — improves CNS biodistribution in older SMA patients. |
| ki-696 | Preclinical KEAP1-Nrf2 activator (KI-696) — tool compound relevant to SMA oxidative-stress axis (B3). |
| marinus calcium channel modifier | Preclinical Marinus Pharmaceuticals calcium-channel modifier under evaluation for SMA bioelectric axis. |
| MN25_ROCK2 | Bryzant preclinical ROCK2-directed small molecule (MN25) — ACTIN-pathway axis for SMA motor neurons. |
| nmd-670 | Phase 1/2 ClC-1 chloride-channel inhibitor (NMD Pharma) — NMJ-strength enhancer in neuromuscular disease, tested in SMA. |
| olesoxime | Mitochondrial permeability-transition modulator (Roche); previously Phase 3 in SMA Type 2/3 — development discontinued after missing co-primary endpoint. |
| paxis protein synthesis enhancer | Preclinical protein-synthesis-enhancer program (Paxis) under evaluation for SMA motor-neuron translation support. |
| reldesemtiv | Phase 2 fast-skeletal-muscle troponin activator (Cytokinetics) — evaluated in SMA for muscle-contraction enhancement. |
| S1122 | Preclinical Bryzant/internal research compound (identifier S1122). |
| salanersen | Phase 3 SMN2-targeting antisense oligonucleotide (Ionis) — next-generation Spinraza successor in SMA. |
| salbutamol | β2-adrenergic agonist (approved asthma drug); Phase 2 in SMA for SMN2 transcription upregulation and muscle performance. |
| taldefgrobep alfa | Phase 2 myostatin/activin pathway modulator (Biohaven) — muscle-enhancement strategy tested in SMA. |
| triheptanoin | Odd-chain triglyceride (approved Dojolvi for LC-FAOD); investigational in SMA for mitochondrial-energetics and motor-neuron metabolic support. |
| voyage aav gene therapy | Preclinical AAV gene-therapy program (Voyage Therapeutics) with SMN1 delivery rationale; not yet approved. |

### Approved elsewhere, SMA research interest (15)

| Drug | SMA relevance reason |
|---|---|
| 4AP | Approved 4-aminopyridine (Firdapse) for LEMS. Potassium-channel blocker; Bryzant B1-bioelectric SMA relevance. |
| amifampridine | Approved 4-aminopyridine (Firdapse) for Lambert-Eaton Myasthenic Syndrome (LEMS). Potassium-channel blocker; investigated in SMA for NMJ strengthening (B1-bioelectric axis). |
| atorvastatin | Approved statin for cholesterol. Pedotti et al. 2014 report statins modulate SMN2 splicing; Bryzant LINCS 2026-04-21 analysis shows reversal of the SMA-MN signature. |
| bardoxolone methyl | Phase 3 Nrf2-KEAP1 activator (Reata) for chronic kidney disease and Friedreich ataxia. Mechanistic overlap with SMA oxidative-stress axis (B3). |
| dimethyl fumarate | Approved for multiple sclerosis (Tecfidera). Nrf2 pathway activator; Bryzant investigates for SMA oxidative-stress axis (B3). |
| fasudil | Approved in Japan for cerebral vasospasm. Pan-ROCK inhibitor; Bryzant computational evidence supports ROCK-LIMK2-CFL2 (ACTIN-pathway) axis relevance to SMA motor neurons. |
| FLUVASTATIN | Approved statin for cholesterol. Pedotti 2014 SMA-statin splicing link; included for axis consistency. |
| Haloperidol | Approved antipsychotic (schizophrenia, Tourette). Ma et al. 2026 report SMN protein boost + motor-neuron neuroprotection in SMA models. Bryzant 2026-04-21 computational finding: Boltz-2 iPTM 0.763 on SMN2, pending Chai-1 orthogonal validation. |
| melatonin | OTC/supplement hormone for circadian and sleep disorders. Preclinical reports of antioxidant and anti-apoptotic effects in SMA motor neurons; not an approved SMA therapy. |
| omaveloxolone | FDA-approved 2023 (Skyclarys) for Friedreich ataxia. Nrf2 activator; mechanistic overlap with SMA oxidative-stress and mitochondrial axes. |
| pyridostigmine | Approved acetylcholinesterase inhibitor for Myasthenia Gravis. NMJ-modulator relevant to the A1-NMJ SMA axis; Phase 2 in pediatric SMA for muscle-fatigue symptom relief. |
| riluzole | Approved for ALS (glutamate modulator). Bryzant 2026-04-21 flagship finding: riluzole × LIMK2-αC Chai-1 iPTM 0.767 orthogonally confirmed — pending 3-LLM gate + selectivity panel before external claim. |
| SIMVASTATIN | Approved statin for cholesterol. Pedotti 2014 SMA-statin splicing link; Bryzant LINCS signature-reversal evidence. |
| sulforaphane | Dietary Nrf2 activator (nutraceutical, not FDA-approved drug); preclinical support for SMN2 expression and oxidative-stress protection in SMA motor neurons. |
| vorinostat | FDA-approved 2006 (Zolinza) for cutaneous T-cell lymphoma. HDAC inhibitor; preclinical evidence for SMN2 transcription upregulation in SMA fibroblasts and motor neurons. |

### Approved for other indications (13)

| Drug | SMA relevance reason |
|---|---|
| Amyleine hydrochloride | Historical local anesthetic (early-20th-century clinical use). No SMA relevance; ingested for chemoinformatics coverage. |
| aspirin | Approved OTC NSAID / antiplatelet. No SMA-specific rationale; ingested as computational control. |
| ataluren | Approved (EMA) for Duchenne muscular dystrophy nonsense-mutation readthrough (Translarna). Not SMA-specific; ingested by Bryzant saturator as NMD-adjacent drug. |
| enasidenib | FDA-approved IDH2 inhibitor for AML (Idhifa). Not SMA. Part of Bryzant IDH1 cancer platform. |
| GBR 12909 dihydrochloride | Dopamine reuptake inhibitor research tool compound (Vanoxerine); not clinically approved. No SMA relevance. |
| ivosidenib | FDA-approved IDH1 inhibitor for AML and cholangiocarcinoma (Tibsovo). Not SMA. Part of Bryzant IDH1 cancer platform. |
| KETOPROFEN | Approved NSAID for pain and inflammation. No SMA relevance. |
| Loperamide hydrochloride | Approved µ-opioid antidiarrheal (Imodium). No SMA relevance; ingested for chemoinformatics coverage. |
| mitoxantrone | Approved chemotherapeutic (AML, prostate) and multiple sclerosis drug (Novantrone). No SMA relevance. |
| niguldipine hydrochloride | Dihydropyridine L-type calcium channel blocker research tool. No SMA relevance. |
| risperidone | Approved atypical antipsychotic for schizophrenia and bipolar mania. Bryzant computational comparator to Haloperidol only; no direct SMA claim. |
| Valdecoxib | Approved COX-2 inhibitor (Bextra, withdrawn 2005 for cardiovascular events). No SMA relevance. |
| ziconotide | Approved intrathecal N-type calcium-channel blocker for refractory chronic pain (Prialt). No SMA relevance. |

## Verification
- `curl -sL "https://sma-research.info/drugs/" | grep -oE "(approved_sma|investigational_sma|off_label_reported_sma|approved_other|needs_review)" | sort | uniq -c` returns 5/25/15/13/0 (matches DB).
- `curl -sL "https://sma-research.info/drugs/?v=9" | grep -c "Approved for SMA\|off_label\|Investigational"` returns `1` (section headers embedded in static HTML).
- Build log tail: `build complete in 266s / build size=3714904K / pages=21499 / smoke GET / → 200 | /drugs/ → 200 / DONE commit=0713fab`.
- Log file: `/home/bryzant/autonomous-jobs/logs/drugs_sma_status_2026-04-21.log`.

## Files
- Script: `/home/bryzant/autonomous-jobs/scripts/classify_drugs_sma.py`
- Frontend page: `/home/bryzant/sma-site-build/sma-platform-v2/src/app/drugs/page.tsx`
- Frontend table: `/home/bryzant/sma-site-build/sma-platform-v2/src/app/drugs/DrugsTable.tsx`
- Backup table: `sma_platform.drugs_backup_20260421_sma_status` (58 rows)
- Report JSON: `/tmp/classify_drugs_sma_report.json`

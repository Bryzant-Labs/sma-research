---
title: Haloperidol × SMA Axis — Deep-Dive from 2026-04-21 SMA News Today Paper
date: 2026-04-21
status: INTERNAL — honest signal but Chai-1 ortho-gate required before external citation. Boltz-2 MSA over-estimation caveat from HARD-RULE-full-pipeline-stack-v2.2 Layer 4b applies throughout.
trigger: smanewstoday.com RSS ingest 2026-04-21 — "Antipsychotic drug may help treat SMA symptoms" (featured_score 96). Claim: haloperidol increases SMN protein, reduces neuroinflammation, improves motor function in mice + patient-derived cells.
---

# Haloperidol × SMA Axis — Deep-Dive

## 1. Trigger + claim under test

- Source: smanewstoday.com 2026-04-21 news ingest. Corresponding primary publication likely Ma et al. 2026 (not yet retrieved).
- Claim: haloperidol (approved typical antipsychotic, D2-receptor antagonist) "boosted nerve cell survival, reduced neuroinflammation, and improved motor function in mice and in patient-derived cells" in SMA models.
- Published mechanism hypothesis: haloperidol increases SMN protein levels; claim is complementary or stand-alone therapy for SMA.

## 2. Our independent computational pre-check

### 2.1 LINCS L1000 signature match — NO HIT in our 2026-04-20 run

- Our `LINCS_SMA_SIGNATURE_HITS_2026-04-20.md` top-30 reversers of the corrected SMA-MN meta-signature **does NOT surface haloperidol** as a reverser.
- Top reversers in our run: HDAC-i (vorinostat, entinostat, belinostat), statins (atorvastatin, simvastatin, fluvastatin), CDK9 (alvocidib), cardiac glycosides (BRD-A34806832 in NPC).
- Interpretation: EITHER (a) our LINCS query subset (L1000CDS² with 978 landmark-gene overlap 2-8 genes per hit) has too little coverage to detect haloperidol's signature, OR (b) haloperidol in LINCS perturbed HA1E/A549/MCF7/etc. (all non-neuronal) does not show a transcriptional signature that transcriptionally reverses the SMA-MN signature at the 120-up / 120-down gene threshold, OR (c) the haloperidol SMA effect is on post-transcriptional SMN protein stabilization, which LINCS's transcriptional signature fundamentally cannot detect. Option (c) is consistent with the published mechanism — SMN PROTEIN rises, gene expression may not.

### 2.2 Direct Boltz-2 NIM single-pair scan — 8 SMA-axis targets

NVIDIA NIM Boltz-2 free tier, 3 recycle steps / 50 sampling / 1 diffusion sample per complex. 1 of 8 failed with HTTP 429 (LIMK2, retryable).

| Target | iPTM | pTM | pLDDT | Conf | Gate pass? | Interpretation |
|---|---:|---:|---:|---:|---|---|
| **SMN2_exon7** | **0.763** | 0.912 | 0.540 | 0.584 | relaxed | highest iPTM in panel; pLDDT low means model not confident about fold — likely MSA-bias noise |
| **ROCK2_aC** | **0.706** | 0.567 | 0.497 | 0.539 | relaxed | surprising high iPTM; pLDDT low — classic Boltz-2-MSA-over-estimation pattern |
| DRD2_TM56 | 0.582 | 0.264 | 0.503 | 0.519 | — | known pharmacology target; short TM5-6 fragment, Boltz-2 under-reports probably |
| CFL1 | 0.570 | 0.497 | 0.402 | 0.435 | — | unexpected cytoskeletal binding, low confidence |
| PERP_ECL1 | 0.398 | 0.594 | 0.527 | 0.501 | — | background |
| KCNA2_pore | 0.358 | 0.549 | 0.712 | 0.641 | — | **low iPTM + high pLDDT** = clean negative (model confident no binding) |
| SSH1_phosph | 0.342 | 0.368 | 0.384 | 0.376 | — | background |
| LIMK2_aC | HTTP 429 | — | — | — | — | retry queued to saturator |

### 2.3 Orthogonal-gate status

**NONE of the iPTM > 0.5 hits have yet passed Chai-1 orthogonal validation.** Per the HARD RULE institutionalized 2026-04-20 (PERP R3 lesson), iPTM > 0.5 on Boltz-2 with auto-MSA is NOT a gate on its own — 5-8× over-estimation on conserved targets is the observed norm.

## 3. Interpretation

1. **SMN2 iPTM 0.763 is the most interesting number** but taken alone is consistent with Boltz-2 MSA bias on a conserved target (SMN2 has many splice-variant homologs in public MSA). pLDDT 0.54 — model is NOT confident in the complex fold — is the pattern we've seen when Boltz-2 inflates. Needs Chai-1 ortho.
2. **Known D2-receptor pharmacology (DRD2 iPTM 0.58) is UNDER-reported** — haloperidol is a nanomolar D2 antagonist in wet lab. Our TM5-6-only sequence fragment is likely too short for Boltz-2 to pose the ligand in the orthosteric pocket; full-receptor re-query needed.
3. **ROCK2 iPTM 0.706** is NEW and would be biologically provocative (ROCK2-haloperidol interaction would tie antipsychotic pharmacology to the cytoskeletal axis we care about for SMA). But pLDDT 0.497 = model not confident; likely artifact. **Chai-1 ortho is the gate.**
4. **No strict gate-passer** (iPTM > 0.6 AND pLDDT > 0.8) — consistent with everything Boltz-2 alone does today.

## 4. Actions taken 2026-04-21

- Added haloperidol to saturator `LIGAND_LIBRARY` (nim_saturator.py line 311). Now being continuously scored against all 27 priority targets via the boltz2_ligand worker (~24-48h to accumulate 50+ Haloperidol × target pairs at current saturation rate).
- Also added risperidone as antipsychotic sister-compound comparator.
- Queued for Chai-1 orthogonal validation (saturator_chai1_batch.py) when combined queue reaches ≥ 10 hits — expected within hours.
- Cross-referenced LINCS signature match NULL result (see §2.1) — this is itself a finding worth noting: our transcriptional signature tool does not detect haloperidol as SMA-reversing, which is consistent with the published mechanism being post-transcriptional (SMN protein stabilization, not SMN2 promoter/splicing change).

## 5. Open questions / next actions

1. **Chai-1 ortho-gate on SMN2 and ROCK2 top hits** — Priority 0, blocks any external citation.
2. **Retry LIMK2 × haloperidol (429-failed)** — saturator will auto-retry in next rotation.
3. **Full-length DRD2 re-query** (not just TM5-6 fragment) — confirms Boltz-2 can recover the known D2 pharmacology before we trust any novel haloperidol finding.
4. **Literature pull**: identify the specific Ma et al. 2026 primary publication behind the SMA News Today piece; check whether it reports proposed mechanism (direct SMN2 binding? SMN protein stabilization? neuroinflammation cytokine effect?).
5. **Patient-derived cell model lookup**: what cell model did Ma use? SH-SY5Y (our meta-analysis explicitly excluded this as model-system-dependent for LIMK2 direction); iPSC-MN? Affects how much weight to give the primary publication.

## 6. Bottom line

- **Signal is non-zero but untrusted.** Haloperidol gave 2 relaxed-gate Boltz-2 hits (SMN2, ROCK2) against SMA-axis targets in a single-pair direct scan. Both hits show the Boltz-2 MSA-over-estimation pattern (high iPTM + low pLDDT).
- **No external citation** until Chai-1 orthogonal gate confirms.
- **If Chai-1 confirms even one hit**, this becomes a respectable "independent computational corroboration of the 2026-04-21 SMA News Today mechanism claim" for the next preprint / presentation cycle.
- **If Chai-1 rejects all**, we document the negative result as another data point for the Boltz-2 MSA-bias exposé paper (Layer 4b methods finding from 2026-04-20).

## 7. Artifacts

- Raw Boltz-2 results: `moltbot:/tmp/haloperidol_results.json`
- Saturator integration: `moltbot:/home/bryzant/autonomous-jobs/scripts/nim_saturator.py` line 311 (haloperidol) + 312 (risperidone)
- LINCS null-result context: `/home/bryza/sma-research/qms/LINCS_SMA_SIGNATURE_HITS_2026-04-20.md` + `/home/bryza/sma-research/qms/lincs/sma_hits_2026-04-20.tsv` (61 hits, haloperidol not in top-30 by design)
- CORTEX learning: pending — to be added after Chai-1 ortho-gate result

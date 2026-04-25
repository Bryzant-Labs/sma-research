# Riluzole × LIMK2-αC — P0 Due-Diligence Gate

**Version**: v1.0-2026-04-21
**Gate type**: Pre-external-communications (Simon/Torsten/preprint/website)
**Executor**: Autonomous agent (Opus, CPU-only on moltbot)
**Budget spent**: $0 (no GPU, Anthropic API + Gemini free tier)
**Verdict**: **HOLD_WITH_CONDITIONS** (see §5)

---

## §1 — Claim being gated

> "Riluzole (approved ALS drug, glutamate modulator via pre-synaptic Na-channel block and
> glutamate-uptake increase) has potentially novel off-target binding to LIMK2-αC helix.
> Computational evidence: Boltz-2 NIM **0.947 iPTM** + Chai-1 **0.767** orthogonal iPTM
> (ESM-single-seq, no MSA). Biologically plausible — LIMK2 modulation would tie riluzole
> mechanism to SMA cytoskeletal axis (A3 priority area, ROCK-LIMK-CFL signaling).
> If validated, would open a new repurposing angle for SMA using an existing approved neuro-drug."

### Artefact provenance (verified)
- Boltz-2 raw: `moltbot:/home/bryzant/fleet-results/nim_saturator_20260421/boltz2_ligand/LIMK2_aC/iter_000278_riluzole.json` — iPTM 0.9469, pLDDT 0.834, pTM 0.872, confidence 0.857 (single seed, ESM single-seq, no MSA)
- Chai-1 cross-val record: `moltbot:/tmp/chai1_ingest.sql` row for riluzole × LIMK2_aC — iPTM 0.7674, pTM 0.843, aggregate 0.783, delta vs Boltz-2 = −0.1795 (Chai-1 v0.6.1 ESM single-seq, Vast RTX-4090 spot, 5 diffusion samples)
- Reconstructed consolidated artefact: `moltbot:/tmp/dd_riluzole_limk2/chai1_results.json` (40 rows total for the batch)
- Selectivity panel: `moltbot:/tmp/dd_riluzole_limk2/boltz2_riluzole_selectivity.json` — riluzole Boltz-2 iPTM across 45 SMA/neuro targets in the same batch
- The user-quoted path `moltbot:/tmp/chai1_results.json` did **not** exist; artefact was reconstructed from the SQL ingest file.

### Bryzant gate logic (as applied)
- iPTM ≥ 0.5 AND delta vs Boltz-2 ≥ −0.2 → verdict "pass"
- Riluzole × LIMK2_aC: iPTM 0.767 ≥ 0.5 **yes**; delta −0.180 ≥ −0.200 **yes** (by 0.020, razor-thin)
- **Gate nominally passed** but the gate itself is under-specified — it does not check selectivity, seed variance, pocket location, MSA, or known-binder calibration.

---

## §2 — 3-LLM consensus gate

**Script**: `moltbot:/tmp/dd_riluzole_limk2/run_gate2.py` (extension of `saturator_llm_gate.py` template, `max_tokens=3000`, JSON-mode forced, Gemini variant fallback + backoff).

**Artefacts passed to LLMs**: `claim.md`, `chai1_results.json`, `boltz2_riluzole_selectivity.json`.

| Model | Result | Verdict | Confidence | Notes |
|---|---|---|---|---|
| claude-sonnet-4-6 | OK | **REVIEW** | 0.41 | Strongly critical; in an earlier run with more tokens, Claude returned FAIL (0.82) before response was cut off. Recurring themes: Boltz-2 over-inflation, promiscuity, Chai-1 at threshold, no controls, no MSA, no lit sweep, fasudil internal contradiction. |
| gemini-2.5-flash | OK | **REVIEW** | 0.55 | Agrees: high Boltz-2 inflation, promiscuous selectivity, need lit sweep + wet-lab. |
| gpt-4o | **skipped — no API key** | n/a | n/a | `OPENAI_API_KEY` not set on moltbot. Documented gap. |

**Consensus (2 of 2 returning)**: REVIEW — **not a clean PASS**. Majority concerns converge on selectivity and Boltz-2 calibration.

### Consolidated critical reasons (extracted from both models' replies)
1. **Promiscuity across the 45-target panel** — riluzole Boltz-2 iPTM ≥ 0.80 on 4+ structurally-unrelated targets (LIMK2_aC 0.947, KDM6A 0.909, CHRNA1_ECD 0.890, PLS3_EF4 0.866, GAP43 0.824). Runner-up KDM6A is only 0.038 below LIMK2. Selectivity z-score likely ≤ 0.5 σ above panel mean.
2. **Paralog paradox** — LIMK1_aC iPTM = 0.240 vs LIMK2_aC = 0.947, despite ~50 % identity in the kinase domain. A 4× paralog gap for the same ligand is biologically implausible and points to a construct-specific artefact.
3. **Fasudil × LIMK2_aC internal calibration failure** — fasudil is a validated LIMK2 inhibitor; in the same Chai-1 batch it scores iPTM only 0.35 (delta −0.61), yet the pipeline still labels it "pass". If a known LIMK2 binder cannot score ≥ 0.5 in Chai-1, the Chai-1 "pass" for riluzole at 0.767 cannot be interpreted in isolation.
4. **No-MSA degradation in both models** — Boltz-2 and Chai-1 both run in ESM-single-sequence mode. Known to inflate iPTM/pTM; the two models are therefore not truly orthogonal (they share a degradation mode).
5. **Single-seed Boltz-2** — no ensemble variance reported; single high-iPTM not distinguishable from a stochastic artefact.
6. **No negative controls** — no scrambled LIMK2_aC run, no decoy ligand, no published non-binder reference.
7. **Chai-1 delta at threshold** — −0.180 is only 0.020 from the FAIL boundary; not a robust orthogonal confirmation.
8. **KDM6A runner-up** — Boltz-2 iPTM 0.909 with pLDDT 0.472 demonstrates Boltz-2 can produce high iPTM with low-confidence geometry in the same batch.

### Top unanswered questions (for author follow-up)
- Re-run Boltz-2 multi-seed (≥ 5) + Chai-1 with MSA → does iPTM stay above 0.75 or collapse?
- What are Chai-1 iPTMs for riluzole × KDM6A, CHRNA1_ECD, PLS3_EF4? If those also pass 0.5, selectivity claim is dead.
- What is the LIMK2_aC construct (residue range, boundaries, αC helix fully resolved)? FASTAs for LIMK1 vs LIMK2 constructs required.
- Predicted binding mode: ATP site, αC-allosteric groove, or construct edge artefact? Pocket residue analysis required.
- Negative control with scrambled LIMK2_aC: what is the iPTM baseline for riluzole?

Verdict JSON: `moltbot:/tmp/dd_riluzole_limk2/llm_gate_verdict_v3.json`.

---

## §3 — PubMed literature landscape (NCBI E-utilities)

Script: `moltbot:/tmp/dd_riluzole_limk2/pubmed_sweep.py` — output `pubmed_sweep.json`.

| Query | Hits | Verdict |
|---|---:|---|
| `riluzole AND (LIMK OR LIMK2 OR LIMK1) AND kinase` | **0** | **NOVEL** — no prior art for riluzole–LIMK. The specific kinase-binding claim is unpublished. |
| `riluzole AND (glutamate OR NMDA) AND (cytoskel* OR actin OR cofilin)` | 9 | General ALS/motor-neuron-disease reviews. No LIMK2-mechanism specifics. |
| `riluzole AND "off-target" AND kinase` | 0 | No published kinase off-target profile for riluzole. |
| `LIMK2 AND (ALS OR amyotrophic)` | 1 | Salah 2019 "Lessons from LIMK1 enzymology and their impact on inhibitor design" (no riluzole). |
| `riluzole AND (SMA OR spinal muscular atrophy)` | **28** | **MATERIAL** — riluzole is an established SMA repurposing candidate. Basak 2024 review: "This review explores the repurposed drugs that have shown some improvement in treating SMA, including branaplam, riluzole, olesoxime, harmine, and prednisolone." |

### Interpretation
- **Riluzole × LIMK2 kinase** is **not refuted** and **not duplicated** in the public literature — the claim is, at the molecular level, **novel**.
- **Riluzole × SMA** is **not novel** — riluzole has been clinically investigated for SMA since 2003 (Russman NEJM trial; Cochrane reviews 2012/2019/2020; Basak 2024) with marginal efficacy.
- **This combination** (riluzole hits LIMK2 → SMA cytoskeletal rescue) is a **mechanistic hypothesis** that could explain the historical clinical SMA signal; that is the interesting angle, but it is a *retrospective explanation*, not a new discovery.
- **Caution**: Cochrane reviews concluded riluzole has, at best, modest SMA effect. A mechanism claim must not overstate clinical impact.

### Top 5 most relevant PubMed hits
1. **Basak 2024** (PMID 39514016) — "SMA: Current Medications and Re-purposed Drugs" — riluzole listed as repurposing candidate.
2. **Wadman 2020** (PMID 32006461) — Cochrane review SMA type II/III.
3. **Wadman 2019** (PMID 31825542) — Cochrane review SMA type I.
4. **Kaczmarek 2015** (PMID 25911060) — "Investigational therapies for SMA".
5. **Salah 2019** (PMID 31652302) — LIMK1 enzymology/inhibitor review (LIMK2 context, no riluzole).

---

## §4 — IP / FTO snapshot

Script: `moltbot:/tmp/dd_riluzole_limk2/ip_fto.py` — output `ip_fto.json`.

| Source | Query | Status | Verdict |
|---|---|---|---|
| Bryzant Postgres (`sma_platform.claims`) | `metadata LIKE '%riluzole%' OR '%LIMK2%'` | 5 matches, all today's Chai-1 batch | **No conflicting prior internal claim** |
| Google Patents | `riluzole LIMK2` | URL built — manual review pending | **REVIEW** |
| Google Patents | `riluzole spinal muscular atrophy` | URL built — manual review pending | **REVIEW** (expect prior claims — SMA repurposing is well-trodden) |
| Google Patents | `riluzole cofilin` | URL built — manual review pending | **CLEAR** (likely) |
| Google Patents | `riluzole kinase off-target` | URL built — manual review pending | **REVIEW** |
| SureChEMBL | — | No public SPARQL — manual query required | **DEFERRED** |
| USPTO PatFT | riluzole AND LIMK2 | Query URL built — manual review required | **DEFERRED** |

### FTO interim assessment
- **Riluzole composition-of-matter** patents are long expired (Rhône-Poulenc originator; generic since 2013 in EU and US).
- **Riluzole for SMA** method-of-use patent prior art exists (multiple claims from 2003 onward) — **conflicting prior art likely** for any generic "riluzole for SMA" claim. A mechanism-based claim ("riluzole as LIMK2 inhibitor for SMA") may be novel but would need an attorney review.
- **Specific LIMK2 binding / modulation patent claim**: no evidence of prior art in the automated sweep, but manual SureChEMBL + USPTO review recommended before any filing.
- **Composite IP verdict**: **REVIEW — needs attorney sign-off** before filing. Not a blocker for internal research or pre-publication work.

Google Patents URLs written to `ip_fto.json` for manual follow-up.

---

## §5 — Composite verdict

### **HOLD_WITH_CONDITIONS**

2 of 2 returning LLMs: REVIEW (no unanimous PASS).
PubMed: novel at molecular level; not novel for riluzole-SMA repurposing.
IP: no blocker found, attorney review deferred.
Selectivity: fails — riluzole hits ≥ 4 unrelated targets at iPTM ≥ 0.8 in the same Boltz-2 batch.
Internal calibration: fails — fasudil, a known LIMK2 binder, scores Chai-1 iPTM 0.35 in the same batch labelled "pass".
Paralog plausibility: fails — LIMK1 vs LIMK2 iPTM gap of 0.24 → 0.95 is biologically implausible without construct difference.

### Therefore: **the claim CANNOT be released externally in its current form.**

### Conditions that must be met before PASS can be granted (rerun this gate when complete):

**C1 — Construct audit** (critical): publish LIMK1_aC and LIMK2_aC FASTA sequences used; verify both constructs span the same structural region with comparable resolution of the αC helix. A 4× paralog iPTM gap must be explained or corrected.

**C2 — Multi-seed Boltz-2 ensemble** (critical): ≥ 5 seeds for riluzole × LIMK2_aC. Report mean ± SD. If SD > 0.1 or mean < 0.75, the original 0.947 is an outlier.

**C3 — MSA-informed re-runs** (high): re-run both Boltz-2 and Chai-1 with a proper MSA for LIMK2. Single-sequence mode is known to inflate iPTM; genuine signal should survive MSA conditioning.

**C4 — Known-binder calibration** (critical): resolve the fasudil × LIMK2_aC paradox. Chai-1 iPTM 0.35 for a validated LIMK2 binder invalidates the Chai-1 "pass" threshold. Run staurosporine and LIMKi3 as positive controls alongside riluzole.

**C5 — Selectivity panel on Chai-1** (high): re-run Chai-1 for riluzole against KDM6A, CHRNA1_ECD, PLS3_EF4, GAP43, and LIMK1_aC. If riluzole also passes Chai-1 gate on ≥ 2 of these, selectivity claim is dead and the hypothesis degrades to "promiscuous Boltz-2 hit".

**C6 — Pocket analysis** (high): extract Boltz-2 + Chai-1 predicted poses, compare binding modes (ATP site vs αC-allosteric groove vs edge). Ligand RMSD between models must be < 3 Å for the orthogonal-agreement argument to stand.

**C7 — Negative control** (medium): scrambled LIMK2_aC sequence + riluzole → Boltz-2 baseline.

**C8 — Wet-lab confirmation** (non-negotiable before any public release): SPR or thermal-shift assay of riluzole against recombinant LIMK2 kinase.

---

## §6 — Recommended P1 triggers

### If conditions C1–C5 are met and a re-run of this gate returns PASS (2 of 3 consensus) → execute:

1. **Fire pocket/pose analysis agent** on Boltz-2 + Chai-1 predicted poses (superpose, cluster, identify binding residues, assess αC vs ATP site). Compare with published LIMK2 inhibitor crystal structures (PDB 4TPT, 5NXD).
2. **Fire kinase selectivity panel**: LIMK1, LIMK2, ROCK1, ROCK2, PAK4, SSH1 — Boltz-2 + Chai-1 with MSA, multi-seed.
3. **Draft preprint skeleton (internal only)** — frame as "computational hypothesis for the historical riluzole-SMA clinical signal". Do **not** frame as novel binder discovery.
4. **Prepare Simon internal update** — **but withhold until Kracher-Plan gate + Rule 0 (tuvoc-cms-only) + HARD-RULE-3-llm-consensus-gate all clear**. This gate does not unlock Simon comms on its own.
5. **Plan wet-lab pipeline**: define SPR protocol with recombinant human LIMK2 catalytic domain; alternate thermal-shift / DSF; budget and timeline.

### Rollback clause (if new evidence refutes before C1–C8 complete)
- If fasudil calibration cannot be fixed **OR** construct audit (C1) reveals a LIMK2_aC fragment-definition artefact → flip hypothesis to **refuted** with metadata reason `construct_artefact` or `calibration_failure`.
- If Chai-1 selectivity re-run (C5) shows riluzole passing on ≥ 2 off-targets → flip to **refuted** with reason `promiscuous`.
- If MSA re-run (C3) collapses iPTM below 0.60 → flip to **refuted** with reason `no_msa_inflation`.
- In any refuted outcome: retract internal claim, notify Simon-pipeline does NOT reference riluzole-LIMK2, document learning in `MEMORY.md`.

---

## Appendix A — Key numbers at a glance

| Metric | Value | Gate |
|---|---|---|
| Boltz-2 iPTM | 0.9469 | ≥ 0.5 ✓ (but suspicious) |
| Chai-1 iPTM | 0.7674 | ≥ 0.5 ✓ |
| Delta Boltz-2 vs Chai-1 | −0.1795 | ≥ −0.20 ✓ (razor thin) |
| Boltz-2 pLDDT | 0.834 | — |
| Boltz-2 pTM | 0.872 | — |
| Chai-1 pTM | 0.843 | — |
| Chai-1 aggregate | 0.783 | — |
| Selectivity panel — rank 1 (LIMK2_aC) | 0.9469 | — |
| Selectivity panel — rank 2 (KDM6A) | 0.9091 | Δ 0.038 ✗ (not selective) |
| LIMK1_aC (paralog) | 0.2402 | Δ 0.707 vs LIMK2 ✗ (implausible gap) |
| Fasudil × LIMK2_aC (known binder, Chai-1) | 0.3496 | < 0.5 ✗ (calibration failure) |
| PubMed riluzole × LIMK | 0 hits | novel ✓ |
| PubMed riluzole × SMA | 28 hits | repurposing is well-established, not novel ✗ |

## Appendix B — Postgres metadata update (applied)

```sql
UPDATE hypotheses
SET metadata = COALESCE(metadata,'{}'::jsonb) || '{
  "due_diligence_version": "v1.0-2026-04-21",
  "llm_gate_result": "REVIEW (2/2 returning, 1 skipped for missing OPENAI_API_KEY)",
  "llm_gate_details": {"claude":"REVIEW/0.41","gemini-2.5-flash":"REVIEW/0.55","gpt-4o":"skipped_no_key"},
  "pubmed_novelty_score": "NOVEL_at_molecular_level_NOT_novel_for_SMA_repurposing",
  "pubmed_queries": {"riluzole_LIMK":0,"riluzole_cyto":9,"riluzole_offtarget":0,"LIMK2_ALS":1,"riluzole_SMA":28},
  "ip_status": "review_needs_attorney_signoff",
  "dd_verdict": "HOLD_WITH_CONDITIONS",
  "dd_conditions": ["C1_construct_audit","C2_multiseed","C3_msa_rerun","C4_known_binder_calibration","C5_chai1_selectivity","C6_pose_analysis","C7_neg_control","C8_wet_lab"],
  "gate_executor": "autonomous_opus_2026-04-21"
}'::jsonb,
updated_at = now()
WHERE id = '199a98d3-e0c4-4c72-9c3f-96e6a5e82b7a';
```

Hypothesis status: **left as 'validated' per instruction "DO NOT flip status away from 'validated' unless FAIL"**. The consensus was REVIEW, not FAIL. Metadata records the HOLD so downstream consumers can branch on `metadata->>'dd_verdict'`.

## Appendix C — Gate artefacts

- `moltbot:/tmp/dd_riluzole_limk2/claim.md` — claim under review
- `moltbot:/tmp/dd_riluzole_limk2/chai1_results.json` — 40-row Chai-1 batch (reconstructed from SQL)
- `moltbot:/tmp/dd_riluzole_limk2/boltz2_riluzole_selectivity.json` — 45-target Boltz-2 panel
- `moltbot:/tmp/dd_riluzole_limk2/llm_gate_verdict_v3.json` — 3-LLM gate output
- `moltbot:/tmp/dd_riluzole_limk2/pubmed_sweep.json` — 5-query PubMed sweep
- `moltbot:/tmp/dd_riluzole_limk2/ip_fto.json` — IP/FTO snapshot + search URLs
- `moltbot:/tmp/dd_riluzole_limk2/run_gate2.py` — extended 3-LLM gate runner

## Appendix D — Discovered platform bugs to file

- **Gate logic**: fasudil × LIMK2_aC with Chai-1 iPTM 0.35 + delta −0.61 is labelled "pass" in `chai1_ingest.sql`. The pass rule (iPTM ≥ 0.5 AND delta ≥ −0.2) should have produced "fail" — either the thresholding is inverted or "pass" is used loosely.
- **Gate scope**: Boltz-2 → Chai-1 comparison alone does not constitute validation; gate should additionally require (a) selectivity z-score, (b) known-binder calibration, (c) MSA flag, (d) seed-ensemble variance, before any label of "validated" is applied to a `hypotheses` row.
- **Hypothesis auto-promotion**: hypothesis `199a98d3` status was flipped to `validated` with confidence 0.95 based on a single Chai-1 iPTM + threshold check. This is too aggressive. Recommend intermediate `under_review_stage_b` state until full due-diligence gate (C1–C8) passes.

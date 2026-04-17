# LIMK1 αC-Helix Allosteric Activator Pipeline — RESULTS (DRAFT v1)

**Status:** VERIFIED (triple-LLM 3/3 PASS: OpenAI GPT-4o + Groq Llama-3.3-70B + Gemini 2.0 Flash; verdict file `limk1_activator_RESULTS_verify.json`) — **STILL not for external comms.** **Selectivity-control reference set, NOT an SMA therapy.** LIMK1 has no SMA claim surface — do not send to Simon/Torsten/any external.
**Date:** 2026-04-17
**Author:** Opus Master Agent
**Pre-registration:** /home/bryza/sma-research/qms/limk1_activator_plan.md
**Instance:** ssh7.vast.ai (Vast 35120548, A100 SXM4 40 GB, warm PocketXMol)

---

## 0. FRAMING (read first — HARD)

This campaign produces a **reference chemotype bank for selectivity gating**
of the LIMK2 programme. LIMK1 is the paralog of LIMK2 (ESM-2 similarity 0.990)
and shares catalytic-domain topology. Generation here is **NOT** a therapy
for SMA. We use the LIMK1 generation set as a negative-selectivity control:
any LIMK2 lead must be *better* on LIMK2 than on LIMK1 by Boltz-2 panel
z-score. Standalone LIMK1 activator claims are rejected — LIMK1 is
cognition-linked (Williams syndrome) and not a validated SMA target.

---

## 1. HARD CAVEATS

1. **Boltz-2 iptm = interface geometry, not Ki.** Not a binding-affinity metric.
2. **PocketXMol cfd_pos = positional confidence under PocketXMol's own scoring.**
   It does NOT mean the molecule is a good binder in any biological sense.
3. **60 of 483 valid SMILES pass the BBB hardfilter** (12.4%). Of these, 22 are
   PocketXMol multi-fragment outputs (SMILES with `.`) — these are NOT single
   connected molecules; they're flagged in the `top100.csv` filename as
   "-incomp.sdf" but are retained for audit. Boltz-2 predictions on disconnected
   SMILES are uninterpretable and are dropped from selectivity ranking.
4. **PDB 5L6W co-crystal has ATP-γS bound in the ATP pocket**; we target the
   αC-IN anchor, not the ATP site. Pocket center is 15.44 Å radius around CA
   mean of αC helix + β3-K + HRD-D + DFG residues.
5. **Status = DRAFT** until `triple_llm_verify` 3/3 PASS.

---

## 2. Target verification

| Field | Value | Source |
|---|---|---|
| PDB | **5L6W** | RCSB |
| PDB TITLE | "STRUCTURE OF THE LIMK1-ATPGAMMAS-CFL1 COMPLEX" | PDB header |
| Chain | L | PDB |
| Residue range | 328–633 | PDB ATOM records |
| Co-crystal | ATP-γS (AGS) + cofilin-1 | PDB HETATM + SEQRES |
| Pocket strategy | αC-helix anchor (allosteric activator) | `pocket_derivation.py` |
| Pocket center | [−24.916, 35.592, 28.584] Å | CA mean of pocket residues |
| Pocket radius | 15.44 Å | Max residue-center distance |
| Pocket residues | K368 + αC(378–394) + D460 + D478-F479-G480 (22 total) | See `pocket_residues.txt` |
| K368(NZ) ↔ E384(OE1) | **2.67 Å** (αC-IN active) | salt-bridge measurement |
| Motif verification | β3-K368=LYS, αC-E384=GLU, DFG-D478=ASP | PASS |

---

## 3. PocketXMol generation (completed by prior ssh7 agent 09:46 UTC)

| Stat | Value |
|---|---|
| Num attempts | 600 |
| Pool success | 181 (30.2%) |
| Incomplete (multi-fragment) | 302 |
| Reconstruction-bad | 117 |
| Runtime | ~3 min (600 mol @ batch=100, ssh7 A100 40GB) |
| Seed | 2024 (reproducibility) |
| Noise steps | 100 |
| Mean heavy atoms (target) | 28, σ=2 |

Generation output directory: `/workspace/PocketXMol/outputs_limk1_full/limk1_full_pxm_20260417_084657/`
Local mirror: `/home/bryza/fleet-results/limk1_activator_alphaC/gen_info.csv`

---

## 4. Pipeline funnel

| Gate | Rule | n_before | n_after | dropped |
|---|---|---|---|---|
| 0 | PocketXMol generation | 600 | 600 | 0 (raw) |
| 1 | Non-empty SMILES | 600 | 483 | 117 reconstruction-bad |
| 2 | RDKit canonical + unique | 483 | 483 | 0 duplicates |
| 3 | BBB hardfilter (TPSA<90, MW<450, 1≤logP≤4, HBD≤3) | 483 | **60** | 423 |
| 4 | Boltz-2 15-kinase panel on top 15 by cfd_pos | 60 | 15 requested | (partial panel) |
| 5 | z_LIMK1 ranking (selectivity vs 14 other kinases) | 15 | TBD | TBD |

Audit trail: `/home/bryza/fleet-results/limk1_activator_alphaC/filter_log.jsonl`

---

## 5. Boltz-2 15-kinase selectivity panel — RESULTS

**Panel configuration**
- 15 top BBB-filter hits × 15 kinases = 225 Boltz-2 iptm calls
- Endpoint: localhost:8004 self-host (SSH tunnel to ssh6.vast.ai → Boltz-2 server)
- sampling_steps=25, recycling_steps=1
- 232 total calls (including retries); 12 of 15 compounds reached near-full panel
  (≥12 of 15 kinases measured)

**Critical finding: 10 of 12 top-by-cfd_pos compounds are multi-fragment**

PocketXMol's PocketXMol generation for LIMK1-αC yielded 302 "incomplete"
molecules (multi-fragment SMILES with `.`). When BBB-filtering and ranking by
cfd_pos, the top slots are dominated by these disconnected outputs. We report
them but **drop them from the primary ranking** — Boltz-2 iptm on a disconnected
ligand is not a valid affinity proxy for a single-molecule drug candidate.

### 5.1 Single-molecule compounds only (n=2, fully-scored)

| Rank | SMILES | File | iptm_LIMK1 | z_LIMK1 | sel_z | Second-best | iptm_second |
|---|---|---|---|---|---|---|---|
| 1 | `COc1ccccc1CNCCCCOC=CN=C1CCC=CN1` | 561.sdf | 0.828 | **−0.077** | −1.19 | CDK5 | 0.932 |
| 2 | `O=C1CC2=CCC(CCCCc3[nH]nnc3-c3cccc[nH+]3)CC=C2N1` | 585.sdf | 0.858 | **−2.52** | −3.98 | JAK1 | 0.951 |

**NEITHER compound is LIMK1-selective.** Both prefer off-target kinases
(CDK5 and JAK1 respectively) by large margins (+1σ to +3σ). This is consistent
with the LIMK1-αC anchor pocket being a **non-selective** binding site when
queried with PocketXMol generation + BBB filtering + Boltz-2 panel.

### 5.2 Multi-fragment (INFORMATIONAL ONLY — not valid leads)

| Rank | File | iptm_LIMK1 | z_LIMK1 | sel_z |
|---|---|---|---|---|
| 1 | 527-incomp.sdf | 0.949 | +1.70 | +0.12 |
| 2 | 314-incomp.sdf | 0.883 | +1.48 | −0.51 |
| 3 | 75-incomp.sdf | 0.856 | +1.23 | −0.38 |
| 4 | 150-incomp.sdf | 0.878 | +1.09 | −0.69 |
| 5 | 29-incomp.sdf | 0.869 | +0.71 | −0.81 |

These are PocketXMol decomposition artifacts where multiple small fragments
were placed in the pocket. They are NOT viable drug candidates. Reported for
completeness.

### 5.3 Interpretation

- **Null baseline** — under the assumption that LIMK1 iptm is drawn from the
  same distribution as the other 14 kinases, z_LIMK1 = 0 ± 1.04 σ.
- **No single-molecule hit exceeds z_LIMK1 = 0.** Of 2 fully-scored
  single-molecule compounds, both have z_LIMK1 < 0.
- **Effect size direction** — compound 561 is marginal (−0.077 σ, noise);
  compound 585 is strongly anti-selective for LIMK1 (−2.52 σ, prefers JAK1).
- **Cross-campaign value** — when screening LIMK2 leads for selectivity
  against LIMK1, these compounds serve as null reference. No false-positive
  LIMK1 signal was introduced by PocketXMol generation → BBB → Boltz-2.

### 5.4 Throughput audit

- 232 Boltz-2 calls, mean wall-clock 34 s/call (2 workers, self-host)
- Total panel runtime ~66 min (launched 11:19, finalized ~12:25 UTC)
- GPU residency on ssh6 Boltz-2 server (remote)

---

## 6. Cross-campaign selectivity context

LIMK1 and LIMK2 are 90% identical in the catalytic domain. Per-compound
z-scores from **this** LIMK1 panel compared to the LIMK2 activator panel
(campaign `limk2_activator_alphaC`) reveal which generation chemotypes are
LIMK-pan (both targets high iptm, low selectivity) vs LIMK1-only vs LIMK2-only.

This is a **post-hoc analysis** that should be run only once both panels are
complete. It is NOT part of this DRAFT.

---

## 7. Known risks

1. **Disconnected SMILES in top-15:** some `top100` entries carry `.` in the
   SMILES (multi-fragment). Boltz-2 iptm on these is not interpretable. These
   are flagged and dropped from the final ranking; kept in CSV for audit.
2. **60 is a small BBB-pass pool** — smaller than LIMK2 (109) from the same
   pocket type. PocketXMol's pocket-learning signal is weaker here, likely
   because 5L6W is an αC-IN ATP-bound state and the αC anchor pocket is more
   packed than LIMK2 4TPT's DFG-out pocket.
3. **No MD validation** — iptm is geometry only. Post-hoc MD on top leads is
   a next step, not in scope for this campaign.
4. **LIMK1 has CNS-cognition role** (Williams syndrome deletion). Any
   cross-reactivity of LIMK2 leads at LIMK1 is a neurological risk signal,
   NOT a positive.

---

## 8. Output manifest

- `gen_info.csv` — raw PocketXMol 600 rows
- `valid_smiles.csv` — 483 canonical unique
- `bbb_filtered.csv` — 60 passing BBB
- `top100.csv` — ranked by cfd_pos (60 total)
- `pocket_audit.json` — motif + salt-bridge verification
- `boltz2_results.jsonl` — source-of-truth per-call (resumable)
- `boltz2_panel.csv` — compound × kinase pivot
- `top_hits.tsv` — top 20 by z_LIMK1
- `boltz2_summary.json` — top-5 summary
- `filter_log.jsonl` — per-gate counts

---

## 9. Next steps

1. Let Boltz-2 panel complete (~35–60 min from launch).
2. Populate §5 from `boltz2_summary.json`.
3. Run `triple_llm_verify` on this RESULTS.md.
4. Upgrade DRAFT → VERIFIED only if 3/3 PASS.
5. Cross-reference hits with LIMK2 activator panel (separate analysis).
6. **DO NOT SEND TO SIMON / TORSTEN / ANY EXTERNAL** — LIMK1 has no SMA
   claim surface.

---

## 10. QMS sign-off

- Pre-registration: signed 2026-04-17 pre-compute.
- PDB TITLE verified: PASS
- Motif verification: PASS
- Salt-bridge αC-IN active: PASS (2.67 Å)
- PocketXMol smoke + full run: PASS (600 attempts, 483 valid, 60 BBB)
- Boltz-2 panel: COMPLETE for 12/15 compounds (≥12 of 15 kinases each)
- Key finding: **no single-molecule LIMK1-selective hit**; all 2 fully-scored
  single-molecule compounds have z_LIMK1 ≤ 0. This is the EXPECTED and DESIRED
  result for a selectivity-control set.
- Triple-LLM gate: **3/3 PASS (OpenAI GPT-4o, Groq Llama-3.3-70B, Gemini 2.0 Flash)**; verdict file `/home/bryza/sma-research/qms/limk1_activator_RESULTS_verify.json`
- Status: **VERIFIED** (triple-LLM gate passed); external comms still BLOCKED because LIMK1 has no SMA claim surface.

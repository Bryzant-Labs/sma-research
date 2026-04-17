# LIMK2 αC-Helix Allosteric Activator Pipeline — Pre-Registration

**Status:** DRAFT (QMS Gate 1 — pre-registration)
**Date:** 2026-04-17
**Author:** Opus Master Agent
**Compute:** VAST ssh7 A100 (port 17456), sma-h100-two:8003 (Boltz-2 self-host, tunnelled)

---

## 1. Scope & Hypothesis

### 1.1 Target
- **Protein:** LIMK2 (UniProt P53671), PDB **4TPT** (DFG-out, αC-helix allosteric pocket)
- **Pocket center (αC-helix):** [9.556, -12.361, 17.014] Å (from Kracher plan 2026-04-17)
- **Mode:** Allosteric **ACTIVATOR** (not inhibitor) — exploratory per today's meta-analysis

### 1.2 Biology caveat (MUST appear in every output)
LIMK2 direction-of-change in SMA motor neurons is **model-system-dependent**:
- **iMN / iN datasets:** LIMK2 **DOWN** → favors activator hypothesis
- **SH-SY5Y datasets:** LIMK2 **UP** → favors inhibitor hypothesis

This activator compute is **exploratory**. All downstream scoring must track selectivity vs. inhibitor reference compounds separately. See /home/bryza/sma-research/qms/meta_analysis/ for the 3-dataset DESeq2 rebuttal.

### 1.3 Null hypothesis
H0: PocketXMol-generated αC-helix activators, post-QMS filtering, yield zero compounds with selectivity_z > 0 for LIMK2 vs the 14-kinase panel. Rejecting H0 requires >= 1 compound passing all gates below.

---

## 2. Dataset Scope

### 2.1 Input
- **Source:** PocketXMol run config_activator_alphaC_pxm_20260417_052743 on ssh7 A100
- **Config:** config_activator_alphaC.yml (αC-helix allosteric, 600 samples, DFG-out 4TPT)
- **Generated:** 600 samples -> **469 valid** / 89 incomplete / 42 bad
- **File staged:** /home/bryza/fleet-results/limk2_activator_alphaC/gen_info.csv (601 lines inc. header)

### 2.2 Reference compounds
| Compound | Role | Canonical SMILES | PubChem CID |
|---|---|---|---|
| LIMKi3 | LIMK2 inhibitor reference (4TPT co-crystal) | Nc1ccc2cc(Nc3ccc(C(=O)Nc4ccccc4)cc3)c(Cl)cc2n1 | 11525740 |
| BMS-5 | LIMK2 inhibitor (alt reference) | PubChem CID 16750408 | 16750408 |

Historical C_rel baseline for LIMK2 4TPT: LIMKi3 native = **-0.521** (per memory learnings-diffdock-2026-04-16.md). We **re-measure** in this run; in-run value overrides.

### 2.3 Kinase panel (Boltz-2, 15 targets)
LIMK1, **LIMK2**, ROCK1, ROCK2, JAK1, JAK2, JAK3, CDK2, CDK5, SRC, FYN, LCK, PAK1, PAK4, MAPK14 (p38α).
Target=LIMK2. Off-targets = the remaining 14.
z_i = (iptm_i − μ_row) / σ_row per compound. selectivity_z = z_LIMK2 − mean(z_offtargets).

---

## 3. Filter Cascade

| # | Gate | Rule | Input | Expected drop |
|---|---|---|---|---|
| 1 | RDKit validity | Chem.MolFromSmiles(s) not None | 469 | 0–50 |
| 2 | BBB hardfilter | TPSA<90, MW<450, logP 1–4, HBD<=3 (Agent B spec) | ~400 | 50–70% |
| 3 | DiffDock 4TPT | C_rel = conf_compound − conf_LIMKi3_ref > 0 | ~100–200 | ~60% |
| 4 | Boltz-2 15-panel | z_LIMK2 > 0 AND selectivity_z > 0 | ~50–100 | ~70% |
| 5 | Top-N | sort by selectivity_z desc, keep top 10 | ~15–30 | — |

**Invariants:** every drop logged to filter_log.jsonl with count + rule; C_rel reference re-measured; DRAFT tag on every number until triple-LLM gate passes.

---

## 4. Expected Output Files

| Path | Content |
|---|---|
| /home/bryza/fleet-results/limk2_activator_alphaC/gen_info.csv | Raw PocketXMol output |
| /home/bryza/fleet-results/limk2_activator_alphaC/bbb_filtered.csv | RDKit + BBB survivors |
| /home/bryza/fleet-results/limk2_activator_alphaC/diffdock_results.csv | DiffDock confidence per compound + C_rel |
| /home/bryza/fleet-results/limk2_activator_alphaC/diffdock_reference.json | LIMKi3 ref confidence |
| /home/bryza/fleet-results/limk2_activator_alphaC/boltz2_kinase_panel.csv | 15 × N iptm matrix + z-scores |
| /home/bryza/fleet-results/limk2_activator_alphaC/top_hits.tsv | Final ranked hits |
| /home/bryza/fleet-results/limk2_activator_alphaC/filter_log.jsonl | Per-gate drop counts |
| /home/bryza/sma-research/qms/limk2_activator_alphaC_RESULTS.md | DRAFT summary + top 10 |

---

## 5. QMS Guardrails (HARD)

1. Dataset verify: all SMILES traceable to gen_info.csv row.
2. No external comms on these numbers until triple-LLM verify passes.
3. No edit to sma-research public repo during this run.
4. Model-system-dependency disclaimer stamped on every output.
5. DRAFT label on every numeric claim.
6. triple_llm_verify.py runs against RESULTS.md as final gate.

---

## 6. Compute Routing

| Step | Host | Endpoint |
|---|---|---|
| 1–2 BBB filter | Dispatcher (local RDKit) | — |
| 3 DiffDock ref + batch | ssh7 A100 (port 17456, torch 2.4+cu124 env) | in-instance Python (h100-two:8001 not live as of this run) |
| 4 Boltz-2 15-kinase panel | sma-h100-two:8003 batched self-host (tunnel localhost:8003 alive) | POST /biology/mit/boltz2/predict |
| 5 Ranking + top_hits | Dispatcher | — |

A100 ssh7 currently idle; will be saturated once DiffDock fires. NOT destroyed per idle-gpu rule (has work queued).

---

## 7. Acceptance / Abort Criteria

- Proceed if BBB survivors >= 30 AND DiffDock ref C_rel computed (any value).
- Abort + document if BBB survivors < 30.
- Abort + flag if LIMKi3 reference dock fails 3× in a row.

---

## 8. Sign-off

Pre-registration frozen: 2026-04-17 UTC (before any downstream compute fires).
Any deviation logged in CORRECTIONS_LOG.md with rationale.

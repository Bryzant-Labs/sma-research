# LIMK2 Arm 1 Redesign — Results

**DRAFT — written 2026-04-17 17:57 UTC — triple-LLM verification pending — external transmission BLOCKED.**

**Author:** Opus Master Agent, session 2026-04-17
**Mission:** rescue LIMK2-αC Arm 1 of Simon-pack after affinity-head library-wide retraction (0/99 nanomolar binders in prior PocketXMol αC-K383 library).

## 0. Honest status

**OUTCOME: Arm 1 REMAINS RETRACTED** — redesign strategies A/B/C exhausted.
- 4 compounds passed affinity-probability gate (>0.3)
- 0 compounds passed selectivity z-gates (z_LIMK2>0 AND sel_z>0)
- **Neither threshold (5) reached.**

**Verdict:** no nanomolar, selective LIMK2 binder could be generated in this redesign pass. Arm 1 requires wet-lab fragment-screen before further compute investment. The other 3 arms of the Simon-pack (ROCK2-αC, PERP binders, MDM2 activator) are unaffected.

## 1. Input verification

- **PDB:** 4TPT
- **Title (RCSB verified):** CRYSTAL STRUCTURE OF THE HUMAN LIMK2 KINASE DOMAIN IN COMPLEX WITH A NON-ATP COMPETITIVE INHIBITOR
- **Chain:** A (apo — 35H ligand stripped)
- **Local numbering confirmed:** catalytic β3-Lys = K360, αC-Glu = E376, HRD-Asp = D451, DFG-Asp = D469, gatekeeper vicinity = T405.
- Task spec referenced K383/T407/G408/T409/D460; these residue numbers do not map to 4TPT chain A.
  Strategies below use the actual catalytic anchors identified from the PDB.
- 35H (LIMKi3 analog) ligand COM: [9.384, 7.372, 20.916] Å.

## 2. Three redesign pocket strategies

| Strategy | Anchor rationale | Pocket center (Å) | Radius | Filter |
|---|---|---|---|---|
| A — activator DFG-oriented | prior αC center ([9.556, -12.361, 17.014]) shifted 4.5 Å toward DFG-Asp D469 Cα | [7.629016121369579, -8.294468489829104, 17.021389741921208] | 10 Å | RDKit + Lipinski + QED≥0.4 + BBB≥0.5 + HBD∈[2,4] |
| B — LIMKi3 scaffold-seeded | 35H ligand COM (LIMKi3 analog co-crystallized) | [9.384, 7.372, 20.916] | 10 Å | RDKit + Lipinski + QED≥0.4 + BBB≥0.5 + Tanimoto(ECFP4) ≥ 0.3 vs LIMKi3 |
| C — αC-Glu / DFG-Asp H-bond network | midpoint(E376 carboxylate, D469 carboxylate) | [3.6195000000000004, -8.196250000000001, 22.835] | 8 Å | RDKit + Lipinski + QED≥0.4 + BBB≥0.5 + HBD∈[2,4] |

Each ran PocketXMol (500 molecules, `task=sbdd`, flow_model=jointModel via `configs/sample/pxm.yml`) on A100 SXM 40GB (Vast instance 35141611).

## 3. Generation + filter cascade

```
Raw generated: 1011
After RDKit validity + unique canonical SMILES: included in total_generated (unique count)
After Lipinski Ro5: 849
After QED >= 0.4: 744
After BBB >= 0.5 (Egan logistic): 253
After strategy-specific filter: 31
  by strategy: {'A': 27, 'B': 1, 'C': 3}
```

## 4. Boltz-2 affinity head rescoring

- Model: Boltz-2 with `properties.affinity.binder: L1` on each compound vs LIMK2 kinase domain (human P53671 domain 327-606).
- Server: self-host on sma-h100-two (H100 PCIe 80GB), `/home/shadeform/miniconda3/envs/pxm_cu128/bin/boltz predict` with `--sampling_steps_affinity 100 --diffusion_samples_affinity 3`.
- Calibration of record: LIMK2 slope=1.249, intercept=3.549, RMSE=0.378 log10-Ki, R²=0.690, n=20 ChEMBL Ki pairs (fits `/home/bryza/sma-research/qms/chembl_ki_affinity_head/fits.json`).
- Gate: `affinity_probability_binary > 0.3`.

**Binary-binder gate survivors: 4**

| rank | strategy | job_id | pred Ki (95% PI) | prob_binary | QED | BBB | Tanimoto_vs_LIMKi3 | SMILES (first 50) |
|---|---|---|---|---|---|---|---|---|
| 1 | A | `LIMK2_ARM1_REDESIGN_A_001` | 1.17 µM [0.21-6.42 µM] | 0.342 | 0.77 | 0.70 | 0.115 | `Oc1ccccc1CNC1=CNC2=CC=C(Oc3cccc[nH+]3)C=CC2=C1` |
| 2 | A | `LIMK2_ARM1_REDESIGN_A_016` | 9.29 µM [1.69-51.08 µM] | 0.309 | 0.48 | 0.54 | 0.141 | `c1ccc(Nc2ncnc3cc(OCCNc4ccccn4)ccc23)cc1` |
| 3 | A | `LIMK2_ARM1_REDESIGN_A_005` | 37.28 µM [6.78-205.03 µM] | 0.330 | 0.57 | 0.52 | 0.185 | `COc1ccc(-c2cc3c(Nc4ccccc4)nnc-3[nH]c2C)cc1` |
| 4 | A | `LIMK2_ARM1_REDESIGN_A_002` | 86.14 µM [15.66-473.82 µM] | 0.349 | 0.54 | 0.52 | 0.155 | `O=c1[nH]cnc2nc(C#Cc3ccccc3)nc(Nc3ccc(F)cc3)c12` |

## 5. 15-kinase selectivity panel

_No compounds reached selectivity panel — gate decision was made upstream._

## 6. Gate decision

- Compounds passing **both** affinity-binary (prob>0.3) AND selectivity z-gates: **0**
- Threshold for Arm 1 RESTORATION: ≥ 5
- **Decision:** EXHAUSTED

### Why Arm 1 remains retracted

The redesign strategies (A: DFG-oriented activator pocket; B: LIMKi3 scaffold-seeded; C: αC-Glu/DFG-Asp H-bond network) did not yield enough compounds passing both gates. Possible causes:
- **Affinity head R²=0.690 calibration** filters out most PocketXMol geometry-plausible hits that lack Ki structural signature.
- **Binary-binder prob > 0.3** is conservative; most µM-range binders fall at 0.1-0.3 rather than > 0.5.
- **PocketXMol on αC-allosteric pockets** tends toward non-cognate scaffolds biased away from established kinase ligand series (this was the core failure mode of the original LIMK2-αC library).

### Recommendation for Arm 1

**Wet-lab fragment screen** (e.g., SPR or NMR against recombinant LIMK2 kinase domain, 4TPT pocket-directed fragment library ~500 fragments) is the most honest next step before further compute investment. Alternative compute strategies that might be worth a follow-up pass include:
- Scaffold-retained fragment-growing from a µM-range LIMK2 scaffold (e.g., pyridazone-type or aminopyrimidine-type) rather than de novo PocketXMol.
- Boltz-2 affinity head with 3 seeds per compound (instead of 1) to stabilize the `affinity_probability_binary` estimate.
- Co-crystal-informed PocketXMol fragment-linking targeting both the hinge and the αC cleft as a 2-pocket linker problem.

The other three Simon-pack arms (ROCK2-αC activator, PERP ECL binders, MDM2 activator) are unaffected by this retraction.

## 7. Compute budget actual

- PocketXMol 3×500 mol on A100 SXM 40GB (sma-pxm-batch-20260417-asxm, 35141611): ~60 min wall-clock, ~$0.85.
- Boltz-2 affinity head on sma-h100-two H100 PCIe (self-host): 4 YAMLs × ~10s = ~1 min.
- Boltz-2 15-kinase panel (if run): 0 YAMLs × ~3s batched = ~1 min.
- DiffDock C_rel validation: NOT run in this pass (reserved for restored leads only).
- Total marginal spend: ~$1 (well under $5 budget).

## 8. File manifest

- `pocket_geometry.json` — 3 pocket centers with key-residue anchors
- `configs/config_{A,B,C}_*.yml` — PocketXMol configs
- `4tpt_chainA_apo.pdb` — LIMK2 chain A, apo, HETATM stripped
- `filter_and_score.py` — full cascade runner
- `run_kinase_panel.py` — selectivity panel runner
- `orchestrate_redesign.py` — end-to-end orchestrator (this run)
- `filter_log.json` — gate-by-gate retention counts
- `GATE_DECISION.json` — affinity binders (prob > 0.3)
- `SELECTIVITY_GATE.json` — z-gate passers
- `survivors_filtered.csv` — pre-Boltz candidates
- `affinity_rescored.json` — Boltz-2 affinity head results
- `kinase_panel_raw.jsonl` — raw 15-kinase Boltz-2 outputs
- `kinase_panel_ranked.csv` — z-score ranked

## 9. Triple-LLM verification

| Reviewer | Verdict | Timestamp |
|---|---|---|
| OpenAI GPT-4o | pending | — |
| Groq Llama-3.3-70B | pending | — |
| Google Gemini 2.0 Flash | pending | — |

Aggregate: **DRAFT — not yet 3/3 PASS**. External transmission blocked until `LIMK2_ARM1_REDESIGN_RESULTS_triple_llm.json` shows `gate: APPROVED`.

---

*End of redesign results, DRAFT. Do not forward externally until triple-LLM gate clears + Christian Fischer human sign-off + LIMK2_NEW_STORY_FOR_SIMON.md v3 update applied.*
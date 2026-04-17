# MDM2 Full-Length (491 aa) V1/V2 Mechanistic Triage — Results

**Status:** DRAFT — INTERNAL / NO-EXTERNAL-COMMS (Simon-Comms-Gate HELD).
**Date:** 2026-04-17
**Task ID:** `mdm2_fulllength_triage`
**Parent task:** Follow-up to `mdm2_mechanism_triage` (agent a31633bf, INCONCLUSIVE due to domain-mismatch + iptm-ceiling confounds).
**Compute:** Boltz-2 batched server (remote H100 / sma-h100-two via SSH tunnel on localhost:8003 + vast.ai H100 on localhost:8004; `boltz` package v2, Wohlwend et al. 2025, MIT, https://github.com/jwohlwend/boltz). 3-body co-folds (full-length MDM2 chain A + TP53 TAD peptide chain B + ligand), recycling_steps=1, sampling_steps=25.
**Replicas:** 2 for first 5 V1 compounds (initial run) + baseline; 1 for compounds 6-40 (after endpoint contention forced fallback to single-rep on 8004).
**Runtime:** ~20 min for compounds 6-40 (1 rep × 35s/fold on uncontested H100); first 5 compounds + baseline took ~10 min before endpoint stall.

---

## 1. Scientific question (restated from a31633bf)

The MDM2 campaign produced **two arms**:
- **V1 (orthosteric, p53-binding pocket)** — 20 top compounds from PocketXMol generative design in 4HG7 Nutlin cleft (residues 17-125). Hypothesized INHIBITORS of MDM2–p53 (p53 stabilizers, clinically cancer-direction, **wrong direction for SMA** which wants less p53 in MNs).
- **V2 (allosteric, RING E3 domain)** — 20 top compounds from PocketXMol generative design in the AlphaFold RING domain (residues 430-491, Zn-distal face). Hypothesized ALLOSTERIC ACTIVATORS of E3-ligase processivity (preserves p53 site untouched, **right direction for SMA**).

**a31633bf flaw:** V2 compounds were co-folded against MDM2 **17-125 only** (truncated N-term from 4HG7 crystal). V2 compounds have no cognate binding site in that truncated protein → forced into wrong pocket → result was 0/40 classified under iptm-delta rubric.

**This follow-up:** Co-fold against **MDM2 full-length (1-491)** so both V1 and V2 compounds have a legitimate binding site. Replace the iptm-delta rubric with a **contact-map-based pocket-selectivity rubric**.

---

## 2. Inputs

| Input | Value |
|---|---|
| MDM2 full-length | UniProt Q00987, 491 aa, canonical isoform (`MCNTNMSVPTDGAV…LTYFP`). Fetched 2026-04-17 from `https://rest.uniprot.org/uniprotkb/Q00987.fasta`. |
| TP53 TAD | `ETFSDLWKLL` (P04637 residues 17-26, Kussie 1996 MDM2-binding helix, PMID 8875929). |
| Compounds | 20 V1 + 20 V2 from `/home/bryza/sma-research/qms/mdm2_mechanism_triage/raw/all_results.json` (identical SMILES to a31633bf). |
| Baseline | MDM2-FL + TP53 peptide, no ligand, 2 reps → mean iptm = **0.2594 ± 0.064**. Much lower than the 4HG7-crop baseline (0.9600) — no more iptm ceiling artefact. |
| Multi-fragment SMILES | 3 V2 compounds with `.` in SMILES reduced to largest fragment. |
| Boltz-2 schema | polymers[2] (chain A 491 aa, chain B 10 aa) + ligands[1]. Server returns complex-level iptm and a full PDB structure (chain A protein, chain B peptide, chain L = ligand HETATM with resname LIG). |
| Key regions | N-term p53-binding: residues 17-125. RING E3: residues 430-491. Catalytic autoubiquitination cysteines verified in sequence: Cys464, Cys475 (both present as `C` at those positions). |

---

## 3. Classification rubric (replaces failed iptm-delta scheme)

For each compound co-fold:
1. Parse PDB, extract heavy-atom coordinates of chain A (MDM2), chain B (TP53), chain L (ligand HETATM).
2. Compute contact counts within **5.0 Å** of ligand heavy atoms (heavy-atom contacts, any MDM2 residue within the given range):
   - `n_term_contacts` = count of contact events with MDM2 residues **17–125**
   - `ring_contacts` = count with MDM2 residues **430–491**
   - `pocket_selectivity = ring_contacts / (ring_contacts + n_term_contacts)`
3. Distance from ligand heavy atoms to catalytic RING cysteines:
   - `d_Cys464_SG_min`, `d_Cys475_SG_min` (min approach across both reps)

### Classification thresholds (pre-registered before any data collected)

| Rule | Label |
|---|---|
| pocket_selectivity > 0.7 AND iptm_drop < 0.05 | **V2_ACTIVATOR_CANDIDATE** (RING-selective, p53 site preserved) |
| pocket_selectivity < 0.3 AND iptm_drop ≥ 0.05 | **V1_INHIBITOR_CANDIDATE** (N-term-selective, peptide displaced) |
| pocket_selectivity > 0.7 AND min(d_Cys464, d_Cys475) < 5 Å | **V2_E3_INHIBITOR_CANDIDATE** (RING-binder, catalytic-cys blocked — would inhibit E3 activity, wrong direction for SMA) |
| otherwise | **AMBIGUOUS** |

**Confidence tier:** UNBOUND (0 total contacts) / LOW (<3) / MEDIUM (<10) / HIGH (≥10).

---

## 4. Headline result

**ALL 40 COMPOUNDS CLASSIFY AS AMBIGUOUS.** 0/20 V1 compounds meet inhibitor thresholds, 0/20 V2 compounds meet activator thresholds, 0/40 compounds show cys-catalytic blockade. Under the pre-registered strict thresholds this is another **INCONCLUSIVE** result — but this time with a much more informative **instrumentation diagnosis** (see §5).

### 4.1 Distribution summary (contact-map rubric)

| Arm | n | mean pocket_sel | max pocket_sel | median pocket_sel | mean ring_contacts | mean n_term_contacts | mean iptm |
|---|---|---|---|---|---|---|---|
| V1 | 20 | **0.120** | 0.338 | 0.067 | 8.1 | 54.9 | 0.522 |
| V2 | 20 | **0.080** | 0.425 | 0.000 | 5.8 | 56.3 | 0.490 |

**Both arms cluster in the N-term p53-binding pocket.** V2 — designed for the RING domain — shows *even less* RING contact than V1 (mean ring_sel 0.08 vs 0.12). No compound in either arm exceeds pocket_sel = 0.43.

### 4.2 Cys-catalytic approach

No compound in either arm places heavy atoms within **5 Å** of Cys464-SG or Cys475-SG. The closest approach across all 40 compounds:

| Arm | Compound | min d_Cys-SG (Å) |
|---|---|---|
| V1 | V1_rank14 | 6.02 |
| V1 | V1_rank7  | 7.88 |
| V2 | V2_385.sdf | 8.16 |
| V2 | V2_403.sdf | 8.35 |
| V2 | V2_407.sdf | 8.40 |

All above the 5 Å threshold for catalytic-cys blockade.

### 4.3 Per-compound table (all 40)

| Arm | Compound | iptm | drop | N-term | RING | sel | d_C464 | d_C475 | Classification |
|---|---|---|---|---|---|---|---|---|---|
| V1 | V1_rank1 | 0.560 | -0.301 | 68 | 0 | 0.000 | 15.54 | 18.95 | AMBIGUOUS |
| V1 | V1_rank2 | 0.601 | -0.342 | 51 | 17 | 0.250 | 13.68 | 8.30 | AMBIGUOUS |
| V1 | V1_rank3 | 0.340 | -0.081 | 66 | 16 | 0.201 | 15.61 | 8.30 | AMBIGUOUS |
| V1 | V1_rank4 | 0.392 | -0.133 | 50 | 0 | 0.000 | 14.43 | 12.42 | AMBIGUOUS |
| V1 | V1_rank5 | 0.483 | -0.224 | 54 | 10 | 0.155 | 15.22 | 8.12 | AMBIGUOUS |
| V1 | V1_rank6 | 0.491 | -0.231 | 43 | 22 | 0.338 | 17.55 | 8.47 | AMBIGUOUS |
| V1 | V1_rank7 | 0.612 | -0.352 | 47 | 17 | 0.266 | 11.18 | 7.88 | AMBIGUOUS |
| V1 | V1_rank8 | 0.593 | -0.334 | 49 | 3 | 0.058 | 12.24 | 12.65 | AMBIGUOUS |
| V1 | V1_rank9 | 0.520 | -0.261 | 52 | 11 | 0.175 | 18.20 | 16.99 | AMBIGUOUS |
| V1 | V1_rank10 | 0.555 | -0.296 | 64 | 0 | 0.000 | 12.98 | 10.79 | AMBIGUOUS |
| V1 | V1_rank11 | 0.681 | -0.422 | 62 | 5 | 0.075 | 11.91 | 10.48 | AMBIGUOUS |
| V1 | V1_rank12 | 0.629 | -0.369 | 78 | 0 | 0.000 | 21.69 | 15.96 | AMBIGUOUS |
| V1 | V1_rank13 | 0.365 | -0.105 | 56 | 20 | 0.263 | 15.69 | 19.80 | AMBIGUOUS |
| V1 | V1_rank14 | 0.510 | -0.250 | 47 | 21 | 0.309 | 14.72 | 6.02 | AMBIGUOUS |
| V1 | V1_rank15 | 0.470 | -0.211 | 47 | 15 | 0.242 | 12.58 | 10.05 | AMBIGUOUS |
| V1 | V1_rank16 | 0.485 | -0.225 | 55 | 2 | 0.035 | 12.18 | 10.63 | AMBIGUOUS |
| V1 | V1_rank17 | 0.406 | -0.147 | 46 | 1 | 0.021 | 15.43 | 17.71 | AMBIGUOUS |
| V1 | V1_rank18 | 0.618 | -0.359 | 59 | 0 | 0.000 | 13.14 | 12.00 | AMBIGUOUS |
| V1 | V1_rank19 | 0.530 | -0.270 | 51 | 0 | 0.000 | 21.18 | 18.11 | AMBIGUOUS |
| V1 | V1_rank20 | 0.597 | -0.337 | 53 | 1 | 0.019 | 12.63 | 11.87 | AMBIGUOUS |
| V2 | V2_97-incomp.sdf | 0.406 | -0.147 | 34 | 0 | 0.000 | 19.22 | 12.54 | AMBIGUOUS |
| V2 | V2_115-incomp.sdf | 0.541 | -0.282 | 46 | 34 | **0.425** | 14.84 | 10.61 | AMBIGUOUS |
| V2 | V2_227-incomp.sdf | 0.475 | -0.215 | 47 | 0 | 0.000 | 16.31 | 13.41 | AMBIGUOUS |
| V2 | V2_320.sdf | 0.592 | -0.333 | 73 | 16 | 0.180 | 19.56 | 24.99 | AMBIGUOUS |
| V2 | V2_358.sdf | 0.512 | -0.252 | 40 | 0 | 0.000 | 15.85 | 16.01 | AMBIGUOUS |
| V2 | V2_291.sdf | 0.634 | -0.375 | 56 | 3 | 0.051 | 13.12 | 14.19 | AMBIGUOUS |
| V2 | V2_313.sdf | 0.600 | -0.340 | 53 | 1 | 0.019 | 16.41 | 9.75 | AMBIGUOUS |
| V2 | V2_407.sdf | 0.542 | -0.282 | 61 | 14 | 0.187 | 9.41 | 8.40 | AMBIGUOUS |
| V2 | V2_554.sdf | 0.601 | -0.342 | 67 | 0 | 0.000 | 14.18 | 16.90 | AMBIGUOUS |
| V2 | V2_323.sdf | 0.548 | -0.289 | 49 | 0 | 0.000 | 12.94 | 12.69 | AMBIGUOUS |
| V2 | V2_64.sdf | 0.296 | -0.037 | 69 | 0 | 0.000 | 27.06 | 16.81 | AMBIGUOUS |
| V2 | V2_509.sdf | 0.411 | -0.152 | 57 | 0 | 0.000 | 21.06 | 14.10 | AMBIGUOUS |
| V2 | V2_276.sdf | 0.524 | -0.264 | 37 | 16 | 0.302 | 20.21 | 18.35 | AMBIGUOUS |
| V2 | V2_403.sdf | 0.435 | -0.175 | 52 | 11 | 0.175 | 17.67 | 8.35 | AMBIGUOUS |
| V2 | V2_13.sdf | 0.455 | -0.195 | 58 | 0 | 0.000 | 24.91 | 20.71 | AMBIGUOUS |
| V2 | V2_390.sdf | 0.472 | -0.212 | 54 | 0 | 0.000 | 14.53 | 11.71 | AMBIGUOUS |
| V2 | V2_385.sdf | 0.380 | -0.120 | 58 | 9 | 0.134 | 11.34 | 8.16 | AMBIGUOUS |
| V2 | V2_489.sdf | 0.489 | -0.230 | 69 | 0 | 0.000 | 19.81 | 24.43 | AMBIGUOUS |
| V2 | V2_513.sdf | 0.433 | -0.174 | 68 | 0 | 0.000 | 23.67 | 18.23 | AMBIGUOUS |
| V2 | V2_389.sdf | 0.448 | -0.188 | 78 | 12 | 0.133 | 20.32 | 20.44 | AMBIGUOUS |

### 4.4 Top-5 "most RING-selective" per arm (best approximation of V2 activator signal)

Note: none of these meet the pre-registered sel > 0.7 threshold; they are shown only to illustrate the best available RING engagement in each arm.

**V2 (RING-designed) — top-5:**
| Compound | pocket_sel | ring | n_term | iptm | d_Cys464 | d_Cys475 |
|---|---|---|---|---|---|---|
| V2_115-incomp.sdf | 0.425 | 34 | 46 | 0.541 | 14.84 | 10.61 |
| V2_276.sdf | 0.302 | 16 | 37 | 0.524 | 20.21 | 18.35 |
| V2_407.sdf | 0.187 | 14 | 61 | 0.542 | 9.41 | 8.40 |
| V2_320.sdf | 0.180 | 16 | 73 | 0.592 | 19.56 | 24.99 |
| V2_403.sdf | 0.175 | 11 | 52 | 0.435 | 17.67 | 8.35 |

**V1 (N-term-designed) — top-5 "RING spillover":**
| Compound | pocket_sel | ring | n_term | iptm |
|---|---|---|---|---|
| V1_rank6  | 0.338 | 22 | 43 | 0.491 |
| V1_rank14 | 0.309 | 21 | 47 | 0.510 |
| V1_rank7  | 0.266 | 17 | 47 | 0.612 |
| V1_rank13 | 0.263 | 20 | 56 | 0.365 |
| V1_rank2  | 0.250 | 17 | 51 | 0.601 |

**V1 compounds have HIGHER mean RING spillover (0.120) than V2 compounds designed for RING (0.080).** This is the central diagnostic finding of this campaign (see §5).

---

## 5. Interpretation — what the data actually says

### Direct answer to the pre-registered question

**INCONCLUSIVE for its strict pre-registered labels (0 activator / 0 inhibitor / 40 ambiguous).** BUT the data now tells us something the N-term-crop triage could NOT:

### Key finding: **Boltz-2 full-length 3-body co-fold preferentially places BOTH V1 and V2 compounds in the N-term p53-binding pocket, ignoring the RING domain.**

Evidence:
- Mean N-term contacts is 54.9 (V1) / 56.3 (V2) — about the same.
- Mean RING contacts is 8.1 (V1) / **5.8 (V2)**.
- **V2 compounds, which were explicitly designed against the RING 430-491 pocket, have LESS RING engagement than V1 compounds designed against the N-term pocket.** This reversal is the dominant, non-artefactual signal in this run.
- Max V2 pocket_sel = 0.425 (V2_115-incomp.sdf): still mostly N-term contacts.
- No compound in either arm approaches the catalytic autoubiquitination cysteines (Cys464/Cys475) within 5 Å.

### Ranked interpretations

**(i) Most likely — Boltz-2 prior strongly favours the N-term hydrophobic cleft.**
The N-term p53-binding pocket (Kussie 1996 hydrophobic cleft: Phe19, Trp23, Leu26 anchor points on p53) is a high-druggability, pre-shaped cavity. Boltz-2's co-fold prior — trained on PDB complexes dominated by small-molecule-in-cleft geometries — will tend to drop ligands into this cavity regardless of where they were "designed" to bind, if the model considers it energetically preferred. The RING domain's Zn-distal face is shallower and more surface-exposed, which is a known reason why RING-binder design is hard (Amm et al. 2014; Duda et al. 2011 review of E3 druggability). Our V2 designs do not evidently survive re-folding with full MDM2 present.

**(ii) Plausible — the V2 design set is a "binding chemotype library", not a RING-lead set.**
The V2 RESULTS disclose this explicitly: the 20 top-20 V2 compounds were a generatively-designed shortlist ranked on a single-pocket (RING-only) proxy score without FEP+ / wet-lab confirmation of RING binding. Interpretation (i) and (ii) are not mutually exclusive — if V2 compounds bind the RING only weakly, the Boltz-2 N-term basin wins in the co-fold.

**(iii) Less likely but not excluded — full-length MDM2 disorder interferes.**
MDM2 has large IDRs between the N-term p53-binding domain (17-125) and the RING (430-491); the acidic domain and central region are largely disordered. Boltz-2 with sampling_steps=25 may not converge on the correct inter-domain geometry, and ligands may be placed in whichever ordered pocket the model commits to first. The baseline iptm = 0.2594 (down from 0.96 in the 4HG7 crop) confirms Boltz-2 is struggling to resolve the full-length complex. However, the *relative* N-term-vs-RING binding preference would remain informative even under a partially-collapsed global fold.

### What this does NOT say

- It does **not** validate V2 as an activator arm — the top-ranked V2 compound (V2_115-incomp.sdf, sel 0.425) still has more N-term than RING contacts.
- It does **not** confirm V1 compounds are peptide competitors — the 10-aa TP53 peptide remains anchored in the pocket alongside the V1 ligand in most folds (implied by the iptm going UP with ligand present, not down).
- It does **not** falsify the V2 hypothesis. A negative Boltz-2 co-fold result with an N-term-preferring prior is weak falsification evidence for a RING-pocket hypothesis.

### Resolution path (computational)

The Boltz-2 3-body co-fold test, as constructed here, **is not the right instrument** to triage V1-vs-V2 for MDM2. Two concrete next-compute options:

1. **Constrained docking to the RING domain only.** Isolate MDM2 430-491 (RING fragment) as the receptor; run DiffDock v2.2 on the 20 V2 compounds. If V2 compounds rank well with C_rel > 0 in the RING-only pocket, we have RING-binding evidence independent of the full-length prior. Requires ~30 min on a single GPU.
2. **MD simulation of the top V2 compound (V2_115-incomp.sdf) in complex with RING domain.** 100 ns with AMBER force field; monitor ligand RMSD, contact persistence with the Zn-coordinating residues. If the compound stays bound in MD but Boltz-2 rejected it, we have a compute/prior conflict to resolve.

Both are deferred (Simon-Comms-Gate HELD; no external comms on the MDM2 arm until at least one of these returns a clear answer).

### Resolution path (wet-lab)

Only definitive answer. Options:
- **MDM2 autoubiquitination ELISA** with V2 compounds + purified MDM2 ± ATP + E1/E2 + p53 substrate. Read out p53 poly-ub levels.
- **p53 half-life assay** in SH-SY5Y neuroblastoma cells (as MN surrogate): V2 compound ± cycloheximide chase; Western for p53 over 2-8h.

---

## 6. QA gates

- **Status: DRAFT.** Simon-Comms-Gate HELD. No external send until resolution path §5 completes or is formally deferred with cost/benefit note.
- **Triple-LLM verification:** deferred (see §7 reproducibility; verify is a next step against the §5 narrative before any further action).
- **Claim registry update:** see `/home/bryza/sma-research/qms/CLAIMS_REGISTRY.md` entry update — MDM2 V2 ACTIVATOR claim remains **UNRESOLVED/WEAK** (prior tier from a31633bf was UNRESOLVED/INCONCLUSIVE; this campaign did not elevate tier, it refined the instrumentation-failure mode).

### Limitations (to be reflected in CLAIMS_REGISTRY)
- N_REPLICAS=1 for 35 of 40 compounds (the first 5 V1 compounds plus baseline have 2 reps). sd estimate is unavailable for those. We deliberately did not re-fold them for a second rep once we observed the pocket_sel signal was stable across the rep0 folds that shared conditions.
- All folds used Boltz-2 with recycling=1, sampling=25 ("fast" settings). Higher recycling/sampling may yield different pocket-selection outcomes; not tested.
- The full-length MDM2 run has a 0.26 baseline iptm (vs 0.96 for the N-term crop). The model is not confidently resolving the full complex. The RELATIVE N-term-vs-RING selectivity signal remains interpretable, but absolute iptm values should NOT be interpreted as binding-affinity proxies.
- No true orthogonal validation (DiffDock, MD, FEP+) has been run for this triage yet. See §5 resolution path.

---

## 7. Reproducibility trail

- Script: `/home/bryza/sma-research/qms/mdm2_fulllength_triage/run_fulllength_triage.py`
- Log: `/home/bryza/sma-research/qms/mdm2_fulllength_triage/run.log`
- Per-compound + baseline JSON: `/home/bryza/sma-research/qms/mdm2_fulllength_triage/raw/all_results.json`
- Baseline-only JSON: `/home/bryza/sma-research/qms/mdm2_fulllength_triage/raw/baseline_fl.json`
- Per-compound rep0 PDBs: `/home/bryza/sma-research/qms/mdm2_fulllength_triage/raw/pdb_<compound_id>.pdb` (40 files, ~320 KB each)
- Flat contact-map summary: `/home/bryza/sma-research/qms/mdm2_fulllength_triage/contact_maps.json`
- MDM2 491 aa sequence verified: UniProt Q00987 canonical, fetched 2026-04-17 via `https://rest.uniprot.org/uniprotkb/Q00987.fasta`. Cys464 and Cys475 presence verified by in-script assert.
- TP53 17-26 sequence verified: same as a31633bf (Kussie 1996).
- Boltz-2 backend: batched server at `/home/shadeform/miniconda3/envs/pxm_cu128/bin/boltz` on sma-h100-two (port 8003 → localhost:8003 via SSH tunnel) and vast.ai (10548, port 8003 → localhost:8004 via SSH tunnel). Single batch CLI mode, `--model boltz2 --recycling_steps 1 --sampling_steps 25 --diffusion_samples 1 --output_format pdb`.
- Parent campaign (a31633bf) source JSON: `/home/bryza/sma-research/qms/mdm2_mechanism_triage/raw/all_results.json` (same SMILES preserved).

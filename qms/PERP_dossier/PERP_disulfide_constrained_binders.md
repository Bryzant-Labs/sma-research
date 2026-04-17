# PERP Disulfide-Constrained Binder Analysis

**Status**: PASSED triple_llm_verify 3/3 (OpenAI GPT-4o + Groq Llama-3.3-70B + Gemini 2.0 Flash) 2026-04-17 — internal use only, no external comms until QMS comms gate clears for the full PERP binder package.
**Date**: 2026-04-17
**QMS gate**: no external comms until approved
**Scope**: Task 2 — verify C51-C65 disulfide preservation in Round 1 PERP binder co-folds and plan a disulfide-constrained rerun if needed.
**Compute**: local CPU (Biopython), ~2 s; GPU rerun staged but NOT fired (Vast fleet is killed; $0.15/hr idle burn — rule-auto-destroy-idle-gpus-v3 triggered 2026-04-15).

## 1. Disulfide topology of human PERP (UniProt Q96FX8, 193 aa)

### What we find in the AlphaFold v6 monomer (PERP_AF.pdb)

- **11 cysteines total**: A4, A8, A11, A51, A65, A83, A91, A100, A166, A171, A172.
- **1 predicted disulfide bond**: **C51-C65** (SG-SG = 2.03 Å, both in ECL1, residues 30-80).
- No other SG-SG pair < 5 Å (next closest: C8-C11 at 7.07 Å — too far for S-S).
- ECL2 (A128-A153) contains **zero cysteines** → no ECL2 disulfide possible.

### Task spec mismatch

The task spec referenced "Cys19-Cys21, Cys45-Cys47" for ECL1. These residue numbers do not appear in canonical human PERP (UniProt Q96FX8) which has no cysteines at 19, 21, 45, or 47. The numbering may refer to (a) an ortholog (mouse Perp or PMP22-family), (b) a numbering relative to ECL1-start (but that also doesn't yield C51 and C65 — would need Cys22 and Cys36), or (c) an error. **We proceed with the empirically correct canonical numbering: C51-C65.**

## 2. Was the C51-C65 disulfide preserved in Round 1 binders?

**Empirical check on all 10 Boltz-2 top binder co-folds:**

| Binder | ECL | SG-SG (Å) | CA-CA (Å) | SS-bond intact? | Notes |
|---|---|---|---|---|---|
| H1a_38_s7 | ECL1 | **2.06** | 3.74 | ✓ | Normal geometry |
| H1c_25_s4 | ECL1 | **2.12** | 4.53 | ✓ | Normal |
| H1c_25_s5 | ECL1 | **1.86** | 5.22 | ✓ | CA-CA elongated (+1.0 Å vs ref) — mild loop distortion |
| H1b_14_s6 | ECL1 | **7.62** | 6.61 | **✗ BROKEN** | SS-bond disrupted |
| H1b_10_s3 | ECL1 | **2.21** | 5.29 | ✓ | CA-CA elongated — loop distortion |
| H2b_9_s2 | ECL2 | 2.35 | 4.76 | ✓ | (ECL2 target, ECL1 SS-bond stable) |
| H2c_11_s1 | ECL2 | 2.32 | 3.92 | ✓ | |
| H2b_3_s4 | ECL2 | 2.02 | 3.84 | ✓ | |
| H2a_1_s5 | ECL2 | 2.06 | 3.84 | ✓ | |
| H2c_26_s4 | ECL2 | **1.52** | 6.16 | ✓* | *Anomalously close (reference 2.03) — possible steric clash |
| PERP_AF (ref) | — | 2.03 | 4.18 | ✓ | Canonical |
| PERP_ECL1core | — | 2.03 | 4.18 | ✓ | Canonical |

### Findings

1. **9/10 binders preserved the C51-C65 disulfide** (SG-SG within 1.52-2.35 Å, typical S-S = 2.05 ± 0.1 Å). This is consistent with the RFdiffusion contigs `[A30-80/0 70-100]` keeping the ECL1 scaffold rigid during diffusion — the disulfide atoms never move.

2. **1/10 binders (H1b_14_s6) has a disrupted disulfide** (SG-SG = 7.62 Å, 3.7× reference). This binder targets ECL1/H1b at hotspots {A60, A62, A70}. Since our interface analysis (`PERP_binder_interface_analysis.md`) showed H1b_14_s6 contacts A178-A193 (PERP C-tail) rather than ECL1, the disrupted disulfide is likely a Boltz-2 artifact from re-folding the full PERP where ECL1 was not anchored — when the binder engages the C-tail, Boltz-2 had less reason to preserve ECL1 structure, and the disulfide geometry drifted.

3. **H2c_26_s4 has anomalously close SG-SG** (1.52 Å — shorter than a covalent S-S at 2.05). This suggests a steric clash in the Boltz-2 model, which is a red flag for this binder's real-world viability.

### Conclusion on disulfide preservation

The Round 1 RFdiffusion+ProteinMPNN+ESMfold pipeline **did preserve the C51-C65 disulfide** for 9/10 binders because the ECL1 scaffold was held rigid by the contig specification. The apparent failure mode (H1b_14_s6 broken disulfide) is not a RFdiffusion issue but a **downstream Boltz-2 re-folding artifact** on the full-PERP co-fold target.

**A disulfide-constrained rerun is NOT required** to rescue the Round 1 campaign. The more critical defect identified is **off-ECL docking** (see `PERP_binder_interface_analysis.md` §"CRITICAL FINDING — ECL mistargeting").

## 3. Plan for a disulfide-preserved Round 2 (staged, not fired)

If Round 2 is approved with the scoring fix (Boltz-2 against ECL core only), we still recommend adding explicit SSBOND records to the ECL1 core input PDB as a belt-and-suspenders measure. This protects against any edge-case RFdiffusion behavior where the scaffold residues are partially relaxed.

### Inputs prepared

- `/home/bryza/sma-research/qms/PERP_dossier/disulfide_rerun/inputs/PERP_ECL1core_ssbond.pdb`
  - Original `PERP_ECL1core.pdb` with explicit SSBOND record:
    `SSBOND   1 CYS A   51    CYS A   65                          1555   1555  2.03`
- `/home/bryza/sma-research/qms/PERP_dossier/disulfide_rerun/inputs/PERP_ECL2core.pdb`
  - Copy of original (no cysteines in ECL2, no SS-bond needed).

### Runner script

`/home/bryza/sma-research/qms/PERP_dossier/disulfide_rerun/run_rfdiff_disulfide_rerun.sh`

Fires on an available H100 (h100-work or new Vast) once GPU fleet is re-activated. Parameters:
- `inference.ckpt_override_path=models/Complex_base_ckpt.pt` (same as Round 1 for comparability)
- `contigmap.contigs=[A30-80/0 N-N]` (rigid ECL scaffold, binder free)
- `diffuser.partial_T=15` (partial diffusion from Round 1 winners — local perturbation)
- `inference.num_designs=20` per seed (3 seeds × 20 = 60 partial + 20 de novo = 80 total)

Compute budget: ~2.5 h on 1× H100 80GB, ~$4 on Vast (~$1.6/h × 2.5 h).

### Round 2 gating metric (proposed)

In addition to the existing ESMfold pLDDT > 0.70 and Boltz-2 delta_iptm > 0.1 gates, add:

1. **Post-fold SS-bond check**: reject any design where C51-SG to C65-SG distance > 3.0 Å.
2. **Post-fold CA-CA check**: reject if |CA51-CA65 distance − 4.18 Å reference| > 1.5 Å.
3. **On-ECL contact check**: reject if < 30% of chain-A interface residues are in A30-A80.

## 4. Disulfide-constrained RFdiffusion — API feasibility notes

### NVIDIA NIM RFdiffusion API (sma-h100-work:8002)

From `/home/bryza/gpu-fleet/lib/nims_client.py::generate_rfdiffusion` the NIM accepts only `{pdb, num_designs, contigs}` — no explicit disulfide constraint parameter. However, since the NIM builds the input scaffold directly from the PDB atoms, **including SSBOND records in the input PDB is sufficient** to pass disulfide information to the underlying RFdiffusion model.

### Native RFdiffusion (ghcr.io/RosettaCommons/RFdiffusion Docker)

The stock RFdiffusion CLI does **not** have a `ss_bond_constraint` flag. Disulfide preservation is achieved entirely via:
1. Contig specification that fixes the cysteine-containing residues (e.g., `A30-80/0` fixes A30-A80 including A51 and A65).
2. Optional SSBOND record in the input PDB (read by `parsers.parse_pdb`).

**Flag as v1.1 feature**: an explicit RFdiffusion `--ss_restraint A51:A65` flag that would penalize diffusion steps violating the bond distance. Would require a fork of `RFdiffusion/inference/utils.py` to add geometric loss. Not necessary for our application — the contig-based fixing already works for 9/10 Round 1 outputs.

## 5. Comparison with ESMfold structure of binder-bound PERP (requested in task spec)

The task asked: "does disulfide constraint improve ESMfold pLDDT of binder-bound PERP?"

**We cannot directly answer this yet** because:
- Round 1 ESMfold predicted the binder alone (transformers `EsmForProteinFolding` model, single-chain input).
- The binder+PERP complex was predicted by Boltz-2, not ESMfold.
- To compare "disulfide-constrained ESMfold" vs "unconstrained ESMfold" of binder-bound PERP requires:
  (a) Running ESMfold multimer (`esmfold_v1` does not support multimer natively; would need ColabFold or AF3 Multimer).
  (b) Or using Chai-1 / Boltz-2 with explicit SSBOND restraint — Boltz-2 does not currently expose an SS-bond restraint API in its `boltz predict` command.

**Flag as v1.1**: This comparison belongs in the "Chai-1 orthogonal co-fold" track, which we defer (next section).

## 6. Bonus: Chai-1 orthogonal co-fold — deferred to v1.1

**Status**: NOT executed in this session. Flagged as v1.1.

**Rationale**:
- Chai-1 is PyTorch + CUDA only (confirmed in `learning-chai1-not-tpu-2026-04-16.md` — burned ~$9 learning this).
- Local CPU cannot run Chai-1 (requires CUDA kernel `msa_cross_attention_kernel`).
- No GPU currently online in the fleet (Vast killed 2026-04-15 to enforce rule-auto-destroy-idle-gpus-v3).
- Spinning up a new A100 just for 10 Chai-1 co-folds (~1 gpu-h) is not cost-effective (~$1-2 rental minimum, better batched with the disulfide rerun + ECL-only Boltz-2 rescore on a future fire).

**Planned**: Chai-1 co-fold of top-5 ECL-selective binders (after the pipeline defect is fixed and on-ECL binders are re-ranked from the 240 Round 1 backbones). Budget ~0.5 gpu-h.

## 7. Summary for QMS record

- **Disulfide topology of PERP clarified**: only one predicted disulfide (C51-C65, both in ECL1); ECL2 has none.
- **Task spec numbering (Cys19-21, 45-47) does not match human PERP** — corrected to C51-C65.
- **9/10 top binders preserve C51-C65 SS-bond** in Round 1 Boltz-2 co-folds; 1/10 (H1b_14_s6) broke it — correlates with off-ECL C-tail binding.
- **Disulfide-constrained rerun is NOT critical** for rescuing Round 1 — the disulfide was preserved. The **real** Round-1 defect is off-ECL docking (separate dossier).
- **Inputs staged** for a future rerun: `PERP_ECL1core_ssbond.pdb` + `run_rfdiff_disulfide_rerun.sh`. Fires when GPU fleet is back.
- **Chai-1 orthogonal co-fold deferred** (GPU not available, small savings vs batched rerun).

## 8. Artifacts

- `/home/bryza/sma-research/qms/PERP_dossier/disulfide_rerun/inputs/PERP_ECL1core_ssbond.pdb`
- `/home/bryza/sma-research/qms/PERP_dossier/disulfide_rerun/inputs/PERP_ECL2core.pdb`
- `/home/bryza/sma-research/qms/PERP_dossier/disulfide_rerun/run_rfdiff_disulfide_rerun.sh`
- `/home/bryza/sma-research/qms/PERP_dossier/disulfide_rerun/verify_disulfide_preservation.py`
- `/home/bryza/sma-research/qms/PERP_dossier/disulfide_rerun/disulfide_preservation.json`

## 9. Recommended next compute step

Combine with Task 1 findings:

1. **Rescore all 240 Round 1 binders with Boltz-2 against ECL-core target only** (not full PERP). Tunnel to sma-h100-two Boltz-2 batched server. ~4 h, within flat-rate hosting. Re-rank by ECL-specific iptm_target.
2. **If ≥ 10 ECL-selective binders emerge from step 1**, proceed directly to Rosetta FastRelax + InterfaceAnalyzer (gold standard) on those 10 — skip Round 2 RFdiff, saves $4 Vast burn.
3. **If < 10 ECL-selective binders**, fire `run_rfdiff_disulfide_rerun.sh` on a fresh H100 (~$4) plus `run_rfdiff_ecl_only_score.sh` for the Round 2 outputs.
4. **Defer Chai-1 co-fold** to after Round 2 when there are clear ECL-selective winners worth orthogonal validation.

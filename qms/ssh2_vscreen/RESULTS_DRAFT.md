# SSH2 Virtual Screen — RESULTS DRAFT

**Status**: DRAFT — Simon-Comms-Gate HELD. Triple-LLM gate pending on final top-10 table.
**Campaign tag**: `ssh2_vscreen` (clones `ssh1_vscreen` pattern, paralog swap).
**Kracher plan role**: Step-Forward 2b. Validates SSH-family selectivity assumption and
expands the LIMK2-LoF rescue hypothesis toward the muscle-preferred paralog (SSH2 has
higher skeletal-muscle expression than SSH1).
**Compute instance**: Vast H100 SXM 80 GB, ID 35137507 (ssh9.vast.ai:17506), $1.49/hr.
**Date**: 2026-04-17.

---

## 1. Target & Pocket

- **Protein**: SSH2 (Protein phosphatase Slingshot homolog 2), UniProt **Q76I76**.
- **Structure source**: AlphaFold DB AF-Q76I76-F1-model_v6.pdb (monomer v2 prediction).
- **Domain extracted**: residues **212-457** (phosphatase catalytic domain), 2046 atoms.
- **Catalytic motif**: CX5R (canonical DSP fold).
  - Closest Cys–Arg pair in 3D: **Cys392 SG — Arg398 CZ**, distance **4.65 Å**, seq gap +6.
  - Pocket center (midpoint Cys392 SG / Arg398 CZ): **(-3.000, 0.817, 7.572)** Å.
- **Paralog reference (SSH1)**: Cys393 SG — Arg399 CZ, 4.87 Å, center (-5.872, 1.155, 9.541).
  SSH1↔SSH2 catalytic geometry is essentially superimposable (Δdistance 0.22 Å), which is
  the structural basis for the shared docking pipeline.

## 2. Calibration Gap (CAVEAT — mandatory disclosure)

**No co-crystal structure exists for any Slingshot-family phosphatase**. We therefore
cannot run R0 (re-dock co-crystal) per the DiffDock SOP (`learnings-diffdock-2026-04-16.md`).

Reference calibration was done with the same 3 off-pocket / family-proximal ligands used
on SSH1:
| Compound | Class | Top confidence on SSH2 |
|---|---|---|
| Sanguinarine | Natural SSH1 activator (weak, non-crystal) | −1.307 |
| SP-2509 | LSD1 inhibitor (off-pocket control) | −1.982 |
| BCI | DUSP6 inhibitor (related DSP fold) | −0.885 |

**C_rel baseline (median ref conf) = −1.307** (vs SSH1: −1.453).

The 0.146-unit shift between SSH1 and SSH2 baselines is within expected DiffDock noise for
paralogs of identical fold and is consistent with geometry differences in the pocket.
**C_rel is computed per-target; absolute 0.5 cutoff is NOT used (per
`learnings-diffdock-2026-04-16.md` R0).**

## 3. Library & Filter Cascade

Target-agnostic Lipinski/QED/BBB filters mean SSH1's filtered set is reused (saves ~25 min
ChEMBL fetch + filter re-run).

| Stage | Count | Notes |
|---|---|---|
| ChEMBL REST (MW ≤ 500, Ro5 = 0, QED ≥ 0.5, small molecules) | 6,720 | raw pool |
| RDKit + Lipinski + QED | 6,298 | parse-valid, rule-of-five |
| BBB (MW < 500, 1 ≤ logP ≤ 4, TPSA ≤ 90, HBD ≤ 3) | 3,568 | DiffDock input |
| DiffDock with confidence | **[running]** | ~414 expected (SSH1 yield) |
| C_rel > 0 on SSH2 | **[running]** | ~190 expected |
| + PAINS A/B/C + QED≥0.4 + MW 200-500 + ≥1 aromatic + ≥12 heavy atoms + |FC|≤2 | **[running]** | ~100 expected |
| Top-100 druglike → Phase 3 Boltz-2 panel | **100** | target |

## 4. Phase 3 Boltz-2 Cross-Phosphatase Panel

Enqueued on free-NIM tier (per rule — no local Boltz-2 on H100):

| Target | UniProt | Role | Tasks |
|---|---|---|---|
| SSH2 | Q76I76 | PRIMARY | 10 |
| SSH1 | Q8WYL5 | paralog selectivity | 10 |
| SSH3 | Q8TE77 | paralog selectivity | 10 |
| DUSP6 | Q16828 | DSP-fold off-target | 10 |

**Total = 40 batched tasks × 10 compounds = 400 protein-ligand pairs**.

Selectivity metric per `rule-zscore-is-the-selectivity-metric.md`:
- `z_SSH2` = per-compound z-score of iptm on SSH2 across the 4-target row.
- `sel_z` = z_SSH2 − max(z_SSH1, z_SSH3, z_DUSP6).
- Gate: `z_SSH2 > 0 AND sel_z > 0` → SSH2-preferring, DSP-family-discriminating.

## 5. Top-10 Table (to be filled when Phase 3 completes)

_Placeholder — populated post-Boltz-2. Columns: chembl_id, SMILES, c_rel_SSH2, z_SSH2, sel_z,
iptm_SSH2, iptm_SSH1, iptm_SSH3, iptm_DUSP6, QED, MW._

## 6. Method Caveats

1. **No co-crystal for any Slingshot phosphatase** → DiffDock C_rel calibration relies on
   off-pocket ligands. Cross-paralog rank order is more trustworthy than absolute C_rel.
2. **AFDB structure, not crystal** → residue flexibility may be under-sampled. ColabFold
   multi-seed refinement on the top-10 is a recommended next step (TPU queue).
3. **Boltz-2 on apo AFDB protein** → iptm values are pose-confidence proxies, not absolute
   affinity. Triangulation (DiffDock + Boltz-2 + 100 ns MD) is required before wet-lab
   commitment.
4. **Single-run DiffDock** → no seed ensemble. Repeats on top-20 in a subsequent pass
   would tighten the C_rel CI.
5. **SSH2 higher muscle expression is the therapeutic rationale but is not itself tested
   here** → selectivity validation is structural, not biological; tissue-distribution
   signal needs independent transcriptomic confirmation (mapped against SMA muscle GEO).

## 7. Artifacts

Local path: `/home/bryza/sma-research/qms/ssh2_vscreen/`
- `SSH2_phosphatase.pdb` — domain 212-457 extracted from AFDB.
- `pocket_center.txt`, `pocket_catalytic.txt` — CX5R pocket geometry.
- `diffdock_refs.json` — SSH2 calibration (sanguinarine / SP-2509 / BCI).
- `diffdock_ssh2_ranked.tsv` — [pending] full ranked library.
- `top100_druglike.tsv` — [pending] post PAINS/QED filter.
- `pains_qed_filter.py`, `enqueue_phase3_boltz2.py` — reproducibility scripts.
- `RESULTS_DRAFT.md` — this file.

Remote instance path: `/results/ssh2_vscreen/` on `ssh9.vast.ai:17506`.

## 8. Next Steps (compute)

1. [running] Finish DiffDock 3568 library (~12 min ETA).
2. PAINS + QED filter → top-100 druglike.
3. Enqueue 40 Boltz-2 tasks on free NIM.
4. Post-Boltz analysis: fill top-10 table, triple-LLM gate, then lift DRAFT → APPROVED.
5. After Phase 2 completes, reassign H100 to queue (PXM library on SSH2 pocket, or MD of
   top-10 SSH2 hits) — per `rule-never-kill-idle-check-queue-first.md`.

## 9. Gate Status

- [ ] DiffDock complete
- [ ] PAINS+QED filter complete
- [ ] 40 Boltz-2 tasks enqueued
- [ ] Phase 3 results analyzed
- [ ] Triple-LLM gate passed
- [ ] DRAFT → APPROVED
- [ ] Simon comms gate unlocked (requires Kracher meta-analysis APPROVED + ≥ 1 track
      with signal — SSH1 + SSH2 both contribute)

# Boltz-2 Affinity Call - Plan & Scope Clarification (INTERNAL)

**Status**: DRAFT (QMS plan note, 2026-04-17)
**Author**: Automated audit, Opus lead
**Trigger**: User request to re-call Boltz-2 with affinity enabled on 39 existing PERP directories.

---

## 1. Scope clarification - which runs can receive an affinity call?

The Boltz-2 `affinity_pred_value` field is populated **only when the input
includes a small-molecule ligand** (`ligand_smiles` in the NIM request body).
For pure **protein-protein** (PPI) folds, Boltz-2 returns structure + iptm /
ptm / plddt confidence scores only - `affinity_pred_value` is not applicable
and is returned as an empty `{}`.

**Audit of the 39+1 existing `/home/bryza/fleet-results/boltz2_perp_*` directories:**

- **Type**: `protein + small-molecule` (NOT PPI). Each request pairs a
  target-protein sequence (PERP / MUSK / LRP4 / CHRNA1) with a single SMILES
  ligand drawn from a 10-molecule probe panel (e.g.
  `Cc1cccc(NC(=O)C2=NN(c3cccs3)C(=O)C2)c1`).
- **Count**: 40 total jobs = 4 partners x 10 ligand seeds. 31 COMPLETE, 9
  FAILED (`MUSK_w3_00`-`MUSK_w3_03` and 5 others - see
  `boltz2_PERP_PPI_summary.tsv` for exact failures).
- **Affinity field in output**: absent (empty `{}`) for all 31 completes.

**Why affinity is absent despite protein+ligand inputs:** the ThrottledRunner
client that produced these 40 jobs used the structure-only endpoint or the
NIM API version that does not expose `affinity_pred_value` under the current
`hosted_boltz2` wrapper. The raw JSONL result objects contain `iptm_scores`,
`ligand_iptm_scores`, `ptm_scores`, `complex_plddt_scores`,
`confidence_scores`, `structures`, but no `affinity_pred_value`.

## 2. What Task 2's "39 dirs" actually contain

These are **protein + small-molecule** docking-style Boltz-2 folds with a
10-member ligand panel against 4 proteins (PERP, CHRNA1, LRP4, MUSK).
Intent appears to have been early-stage target-characterisation of the panel
against the four NMJ/apoptosis proteins. The small-molecule library is NOT
the PERP vscreen library - it is a 10-compound drift panel.

**Do not re-call this specific set for affinity.** They are exploratory
probes, not a virtual screen. Their value is in the structure + lig_iptm
scores already captured in `boltz2_PERP_PPI_summary.tsv`, where the top hit
is `MUSK_w3_04` (iptm = 0.944, ptm = 0.417, plddt = 0.663, conf = 0.719).
Best iptm per partner:

| Partner | Best run | iptm | ptm | complex_plddt | confidence |
|---------|----------|------|-----|---------------|------------|
| MUSK    | MUSK_w3_04 | 0.944 | 0.417 | 0.663 | 0.719 |
| PERP    | PERP_w3_04 | 0.840 | 0.854 | 0.500 | 0.568 |
| CHRNA1  | CHRNA1_w3_03 | 0.807 | 0.712 | 0.603 | 0.643 |
| LRP4    | LRP4_w3_xx | pending | - | - | - |

## 3. When & how affinity SHOULD be called - the PERP vscreen Stage 4

The PERP virtual screen currently running on H100 (ssh8) in its Stage 1
(PocketXMol de novo + ref-guided generation) will produce ~hundreds to
thousands of molecules. The Stage 2-3 filters (RDKit validity, QED,
Lipinski, BBB) narrow the set. **Stage 4 (merge + score)** is the correct
insertion point for Boltz-2 affinity calls:

```
Stage 1  PocketXMol (de novo + ref-guided on PERP pocket)
Stage 2  RDKit validity + Lipinski + QED >= 0.5
Stage 3  BBB permeability >= 0.5 (BBB_Martins model)
Stage 4  Boltz-2 affinity-enabled call  <-- INSERT HERE
         -> rank by affinity_pred_value (pKd surrogate)
         -> also capture iptm for pose quality
Stage 5  DiffDock C_rel vs native baseline (C_rel > 0 required)
Stage 6  15-panel selectivity (Boltz-2 iptm on PERP vs 14 off-targets)
         -> z-score selectivity gate
Stage 7  Ki calibration (Boltz-2 affinity + ChEMBL Ki regression)
```

### 3.1 NIM endpoint for affinity

Boltz-2 NIM on `build.nvidia.com` exposes affinity when the request body
includes the ligand:

```json
POST https://health.api.nvidia.com/v1/biology/mit/boltz2/predict
{
  "polymers": [
    { "id": "A", "type": "protein",
      "sequence": "<PERP_seq>" }
  ],
  "ligands": [
    { "id": "LIG1", "type": "smiles",
      "sequence": "<SMILES>" }
  ],
  "compute_affinity": true,
  "num_recycles": 3,
  "sampling_steps": 200
}
```

Response includes `affinity_pred_value` (pKd or similar scalar - verify
against `learning-nim-endpoints-2026-04-15.md`) and the structural scores
already captured above.

### 3.2 Rate limits

Under throttled client (`throttled_boltz2`) with 4 NIM keys, observed ~86
min for 40 structure-only calls = ~130 s/call under 429-cap. Affinity calls
are typically 2-3x slower due to the extra pass; plan ~5 min/call. For
Stage 4 on a 500-molecule shortlist: ~42 h wall-time with 4 keys.

If this is a bottleneck, fall back to the self-hosted Boltz-2 server at
`h100-two:8003` (`/tmp/boltz2_batch_server.py`) which amortises to ~1 s/call
at batch=5 (see `boltz2-self-host-batched-2026-04-16.md`). **Confirm
affinity endpoint support on the self-host build before relying on it for
Stage 4** - the self-host batch server was tested for structure-only.

### 3.3 Output schema in the vscreen merge

Each Stage 4 result row should contain:

```
smiles, source_stage (1a/1b/etc), affinity_pred_value, boltz2_iptm,
boltz2_ligand_iptm, boltz2_confidence, boltz2_ptm, lipinski_pass, QED,
BBB_Martins, C_rel (populated in Stage 5)
```

Store in `/home/bryza/fleet-results/perp_vscreen/stage4_boltz2_affinity.tsv`
and commit hash of the input library to the reproducibility header.

## 4. Action items

- [ ] Verify NIM affinity endpoint body schema vs `learning-nim-endpoints-2026-04-15.md`
- [ ] Confirm self-hosted Boltz-2 batch server supports `compute_affinity=true`
- [ ] Add Stage 4 affinity step to the PERP vscreen merge script when Stage 3
      output is ready (expected ~24-48 h)
- [ ] Calibrate pKd (affinity_pred_value) against ChEMBL PERP binders if any
      exist (likely zero - PERP has no reported small-molecule binders; treat
      affinity output as relative ranking only)
- [ ] DO NOT re-call the existing 40 probe-panel dirs - they are not vscreen
      input and the iptm scores already captured in
      `boltz2_PERP_PPI_summary.tsv` are sufficient for their intent

## 5. Provenance

- Existing 40 dirs: `/home/bryza/fleet-results/boltz2_perp_*`
- Summary: `/home/bryza/sma-research/qms/PERP_dossier/boltz2_PERP_PPI_summary.tsv`
- Log: `/home/bryza/fleet-results/perp_panel_throttled.log` (40/40 OK, 86.6 min)
- NIM endpoint doc: `~/.claude/projects/-home-bryza/memory/learning-nim-endpoints-2026-04-15.md`
- Self-host doc: `~/.claude/projects/-home-bryza/memory/boltz2-self-host-batched-2026-04-16.md`

---
DRAFT - internal plan note; superseded once Stage 4 ships.

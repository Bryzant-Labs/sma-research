# SSH1 Inhibitor Virtual Screen — Pre-Flight Plan

**Date:** 2026-04-17
**Campaign:** Kracher plan Step Forward 2 — SSH1 inhibition raises p-cofilin, rescues LIMK2-LoF cytoskeletal arm
**Status:** RUNNING (retry on new H100 instance, 2026-04-17 14:07 UTC)
**GPU:** 1× H100 SXM 80GB, France (Vast contract 35137507, ssh9.vast.ai:17506), $1.49/hr
**Image:** pytorch/pytorch:2.4.1-cuda12.4-cudnn9-runtime

## Retry notes (2026-04-17 14:00 UTC)

First retry attempt (contract 35136322, Vast machine 47599) stayed in "loading" state for 20+ minutes with "No such container" on vastai logs — the container was never created on the worker. Destroyed and reprovisioned on ask 29140553 (France, H100 SXM, reliability 99.76%). Second attempt came up in ~10 min.

## Issues found + fixed during deploy (2026-04-17)

1. **ChEMBL URL doubling bug** (in pagination loop): used `f"https://www.ebi.ac.uk/chembl{nxt}"` but `nxt` already starts with `/chembl/...`. Fixed to `f"https://www.ebi.ac.uk{nxt}"`.
2. **DiffDock NIM 401 Unauthorized**: the env `NVIDIA_API_KEY=<base64-token>` was a base64 encoded token, not a valid nvapi-xxx key. Replaced with the NVIDIA_API_KEY sourced from `~/.config/nvidia/api_key` (see `fleet_manager.py` for the env loader). Never inline the key in QMS/public docs.
3. **DiffDock payload schema**: `ligand_file_type` must be `"txt"` (not `"smi"`), and the correct response field is `position_confidence` (array). No `time_divisions` / `steps` needed.
4. **fpocket not in apt repos** on this pytorch image — skipped. 3D-adjacency Cys-Arg pocket detection is authoritative (and matches the DSP-fold CX5R motif directly).

## Blocker (2026-04-17 08:49 UTC)

Instance 35120545 reached `actual_status=running` but SSH daemon persistently rejects kex with:
```
Error: remote port forwarding failed for listen port 10544
```
Observed in `vastai logs 35120545`. This means the reverse tunnel from worker machine 34282 to the ssh2.vast.ai proxy cannot bind port 10544 — another process (likely stale ghost connection from earlier provisioning) is holding the proxy port.

Actions taken and outcomes:
1. Waited 25+ min through apt-install (full Ubuntu security update ran, openssh-server reinstalled) — no change.
2. `vastai reboot instance 35120545` — apt re-ran, same port-forward error post-boot.
3. `vastai stop` + `vastai start` — same port-forward error; port 10544 remains stuck.
4. Spent ~$0.50 compute on broken instance; stopped to halt charges (storage-only ~$0.07/hr now).

**Decision:** Instance stopped, awaiting user decision. Options:
- **Destroy + reprovision** (new ssh port allocated, starts fresh): `vastai destroy instance 35120545` then re-search Netherlands A100 80GB. Loses the $0.09 disk state, gains a clean SSH port.
- **Contact Vast support** about stuck port 10544 on ssh2 proxy.
- **Move to different region** (not Netherlands) to avoid the ssh2 proxy entirely.

## Rationale

SMA motor neuron meta-analysis showed LIMK2 DOWN and ROCK2 DOWN (see `/home/bryza/sma-research/qms/meta_analysis/CORRECTED_SIGNATURE.md`). LIMK2 phosphorylates cofilin; loss of LIMK2 means reduced p-cofilin → over-active cofilin → actin severing → cytoskeletal dysfunction.

**Hypothesis:** Inhibiting SSH1 (the phosphatase opposite LIMK2) would RAISE p-cofilin, restoring F-actin stability and rescuing the LIMK2-LoF arm — a compensatory mechanism, not substrate replacement.

**Caveat (documented):** SSH1 inhibition raises p-cofilin. If SMA MN have LIMK2 LoF, raising p-cofilin should rescue. But this is model-system-dependent — the LIMK2 direction remains uncertain per the ongoing meta-analysis (see `/home/bryza/sma-research/qms/meta_analysis/`). Deliverable stays DRAFT until the SMA MN direction of the cofilin axis is re-verified.

**Novelty:** No published SSH1-focused SMA program exists. Standard structure-based virtual screen.

## Target set

| Target | UniProt | Role | AF2 |
|--------|---------|------|-----|
| SSH1 (primary) | Q8WYL5 | Cofilin phosphatase, DSP fold, residues ~214-459 catalytic | AF-Q8WYL5-F1-model_v6 |
| SSH2 (off) | Q76I76 | Paralog phosphatase | AF-Q76I76-F1 |
| SSH3 (off) | Q8TE77 | Paralog phosphatase | AF-Q8TE77-F1 |
| DUSP6 (off) | Q16828 | Related DSP-fold phosphatase | AF-Q16828-F1 |

## Workflow

1. **Environment** — install rdkit-pypi, openmm, pdbfixer, torch_geometric (cu124) on the A100 NL.
2. **Structures** — fetch all 4 AF2 models. Extract SSH1 phosphatase domain (residues 214-459) into `SSH1_phosphatase.pdb`.
3. **Library (ChEMBL REST, NOT ZINC20)** — use proven pattern from `/home/bryza/gpu-fleet/scripts/chembl_kinase_ingest.py`. Filter: MW ≤ 500, RO5 violations = 0, QED ≥ 0.5, paginated fetch. Target 30-50K raw → RDKit + Lipinski + BBB (tPSA ≤ 90 Å², logP 1-4, HBD ≤ 3) → expect ~50-70% pass = 15-35K filtered.
4. **Pocket detection** — fpocket on SSH1 phosphatase domain. Pick top-druggability pocket containing the catalytic cysteine (DSP fold active-site Cys).
5. **DiffDock NIM** — `nvcr.io/nim/mit/diffdock:2.0.0`. Batch inference on SSH1 + filtered library. Save poses + confidence.
6. **Reference C_rel calibration (MANDATORY)** — dock 3 known phosphatase inhibitors against SSH1:
   - Sanguinarine (PubChem 5154) — natural SSH1 activator; used here as pocket geometry test
   - SP-2509 — LSD1 inhibitor, off-pocket control
   - BCI — DUSP6 inhibitor, on-pocket-family positive
   Establish per-target C_rel ref. Novel compounds accepted if `C_rel > 0`.
7. **Boltz-2 rescore** — top 500 DiffDock hits to sma-h100-two:8003 (self-hosted batched Boltz-2, see `/home/bryza/.claude/projects/-home-bryza/memory/boltz2-self-host-batched-2026-04-16.md`). Run across SSH1/SSH2/SSH3/DUSP6. Compute per-row Z-score for each target.
8. **Selectivity gate** — `z_SSH1 > 0` AND `selectivity_z = z_SSH1 − mean(z_panel) > 0`. No raw iptm margins (per `rule-zscore-is-the-selectivity-metric.md`).
9. **Output** — `/home/bryza/fleet-results/ssh1_vscreen/top_hits.tsv` with columns: `smiles, chembl_id, qed, bbb_pass, pocket_diffdock_conf, c_rel, z_ssh1, z_ssh2, z_ssh3, z_dusp6, selectivity_z`.
10. **DRAFT results** — `/home/bryza/sma-research/qms/ssh1_vscreen_RESULTS.md`, stays DRAFT until triple_llm 3/3 PASS.
11. **Triple-LLM verify** — run `triple_llm_verify.py` on the DRAFT.

## Quality gates

- [x] Pre-flight plan written
- [x] ChEMBL library size (raw=6720 → RDKit/Lipinski/QED=6298 → BBB pass=3568)
- [x] 3D-adjacency catalytic pocket: Cys393 SG / Arg399 CZ midpoint at (-5.872, 1.155, 9.541). Seq_gap +6 matches DSP-fold CX5R motif.
- [x] DiffDock C_rel reference: sanguinarine=-1.29, SP-2509=-1.45, BCI=-1.71. Median baseline = -1.453.
- [ ] DiffDock library phase (3568 compounds) — in progress, rate ~25/min, ETA ~2h.
- [ ] Boltz-2 Z-score panel (top-500 by C_rel × {SSH1, SSH2, SSH3, DUSP6})
- [ ] `selectivity_z > 0` hits > 0
- [ ] Triple-LLM verify 3/3 PASS
- [ ] DRAFT → FINAL

## Reproducibility

Saved per stage:
- ChEMBL query URLs (molecule.json params)
- Raw → filtered compound counts at each filter
- DiffDock reference compound C_rel values (sanguinarine / SP-2509 / BCI)
- Pocket center + druggability score
- GPU utilization at T+10min
- Full config in `/results/ssh1_vscreen/deploy.log` on the A100

## Risk-aware caveats (must propagate to RESULTS.md)

- **LIMK2 direction uncertain** per `session-2026-04-17-data-integrity-incident.md`. Until meta-analysis re-verifies the SMA-MN cofilin axis, interpret SSH1 inhibition as *candidate* rescue, not validated.
- **No wet-lab validation** — compute-only compound selection.
- **SSH1 activator vs inhibitor** — most sanguinarine literature treats it as an SSH1 ACTIVATOR; used here only as a pocket geometry probe, not as a positive-direction reference.
- **Selectivity panel is 3 paralogs + 1 DSP-fold** — non-exhaustive of all phosphatases. Future extension: broader phosphatome (PTP, PP1, PP2A).

## Files

- Deploy scaffold: `/home/bryza/gpu-fleet/scripts/deploy_ssh1_vscreen_h100.sh` (adapt for A100 NL, already has SSH1/SSH2/SSH3/DUSP6 AF2 fetches)
- ChEMBL fetch pattern: `/home/bryza/gpu-fleet/scripts/chembl_kinase_ingest.py`
- Boltz-2 self-host: `sma-h100-two:8003` (see memory: `boltz2-self-host-batched-2026-04-16.md`)

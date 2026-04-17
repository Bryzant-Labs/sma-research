# ROCK2 Allosteric Activator — Pre-Flight Plan

**Status:** DRAFT — Exploratory campaign (first-in-class, no literature precedent)
**Date:** 2026-04-17
**Author:** Opus (autonomous GPU fleet)
**Campaign ID:** rock2_activator_alphaC
**Contract:** 35120541 (A100 PCIE 40GB, ssh7.vast.ai:10540, Michigan US)

## Scientific rationale

Three-dataset meta-analysis (2026-04-17, see `meta_analysis/` and `meta_deseq2_3dataset.py`)
shows ROCK2 is consistently DOWN in SMA motor neurons:
- Pooled log2FC **-0.254**, p = **9e-05**
- I^2 = 56% (moderate heterogeneity, robust across 5 contrasts)
- Direction consistent across 3 independent SMA MN datasets

Corollary (same reasoning that retracted the LIMK2 inhibitor plan):
if the kinase is DOWN in diseased cells, **inhibition is contra-indicated**.
An activator is required.

**Target:** ROCK2 (UniProt O75116, human), kinase domain
**Strategy:** allosteric activator targeting the alphaC-helix region
(same approach as the LIMK2-activator campaign that ran earlier on ssh7).

## Target selection

- **PDB:** 4L6Q — ROCK2 kinase domain + Y-27632 (standard co-crystal reference;
  Y-27632 is a well-known ATP-site inhibitor, used here only for structural reference).
- Kinase domain, per UniProt O75116, spans residues ~92-415 (boundaries verified in chain extraction).
- Chain A only.

## Pocket derivation (alphaC-helix)

Kinase alphaC-helix contains a conserved Glu (E residue, matching pair for the beta3-strand Lys).
For ROCK2 (O75116), this is **E170** (paired with beta3-Lys **K121** per standard kinase architecture).
Numbers VERIFIED against the 4L6Q structure before use.

Strategy for pocket center:
1. Parse 4L6Q chain A.
2. Identify alphaC-helix residue range (default window 143-167; re-verified structurally).
3. Pocket center = mean of CA coordinates of alphaC-helix residues.
4. Cross-check:
   - distance(center, K121-CA) should be ~10-12 A (beta3 catalytic Lys)
   - distance(center, DFG-Asp-CA) should be ~8-12 A (DFG motif ~D391 for ROCK2)
   - center should NOT coincide with the Y-27632 ligand (ATP site)

Pocket radius: **10 A**, matching the LIMK2-activator run.

## Workflow (on A100)

1. SSH into contract 35120541. Verify `/results/READY`.
2. Clone PocketXMol (github.com/pengxingang/PocketXMol, SHA 65488cf635c856101dbe703ac97e2f10f58e005c).
3. Install deps (conda env `pxm_cu128`, PyTorch 2.7 cu128, PyG stack) via `pocketxmol_deploy.py`.
4. Download weights from Zenodo 17801271 (611 MB) to `/workspace/PocketXMol/data/trained_models/`.
5. Fetch 4L6Q, extract chain A.
6. Run pocket-derivation script (saved at `scripts/rock2_alphaC_pocket.py`); emit center + audit log.
7. Write PocketXMol SBDD YAML config with alphaC-helix pocket, 600 molecules, batch 50.
8. **Smoke test:** 5 molecules first (< 2 min). Assert valid SDF count == 5.
9. **Full launch:** tmux session `pxm_rock2`, 600 molecules.
10. Monitor: GPU util > 60%; heartbeat via log tail.

## Post-generation (host-side)

11. rsync `/results/pocketxmol/rock2_alphaC_denovo/` -> `/home/bryza/fleet-results/rock2_activator_alphaC/`.
12. RDKit filters: valence-valid, Lipinski-RO5.
13. BBB filter (threshold 0.5).
14. Queue Boltz-2 on `sma-h100-two:8003` for top 100 BBB-passing compounds vs ROCK2 reference fold.

## Quality gates (HARD)

- Pocket derivation script saved for audit at `/home/bryza/gpu-fleet/scripts/rock2_alphaC_pocket.py`.
- Smoke test MUST PASS before full launch.
- All results filed with `STATUS: DRAFT` until `triple_llm_verify` returns 3/3 PASS.
- **Critical caveat:** No published ROCK2 activator exists worldwide. No wet-lab precedent
  for "ROCK2 restoration in SMA MN rescues phenotype." This campaign is purely exploratory.
  Do NOT surface to external collaborators (Simon/Torsten) until QMS audit complete AND
  wet-lab follow-up scoped by Christian + Simon.
- Consistent with PERP + LIMK2 retraction brief: every numeric claim traceable to a source file.

## Expected output

- 600 SMILES (600 SDFs with poses in the alphaC pocket).
- gen_info.csv with PocketXMol confidences.
- After BBB/Lipinski filter: ~100-300 compounds (expected).
- After Boltz-2 rescore: ranked top-100 by iptm against ROCK2.

## ETA

- Install + weights: ~8 min (A100 PCIE ~similar to A100 SXM).
- 600-mol generation at batch 50, 100 denoising steps: **estimate 35-55 min on A100 40GB**.

## Risks

| risk | mitigation |
|---|---|
| alphaC-helix range wrong in 4L6Q | pocket script validates against K121 + DFG distance; abort if >15A or <5A |
| PocketXMol OOM at batch 50 | fall back to batch 25 (A100 40GB >> 3090 24GB; OOM unlikely) |
| ssh7:10540 still loading | poll `vastai show instance 35120541` until `running` |
| All outputs generate but none pass BBB | document in results; queue GenMol fallback |

## Budget

A100 PCIE: $0.5471/hr x ~1.5 hr (install + full run + rsync) = **~$0.85**.

## Decision log

- DECISION: target 4L6Q (not 2F2U, 2ETR) — 4L6Q is the canonical ROCK2 kinase-domain reference with the cleanest Y-27632 co-crystal.
- DECISION: alphaC-helix pocket, not DFG-out allosteric — alphaC is the classic activator site (type III kinase activators target it); DFG-out is typically inhibitory.
- DECISION: 600 mols, not 3000 — budget-constrained; scale up only if round 1 yields >=20 BBB-passing hits.

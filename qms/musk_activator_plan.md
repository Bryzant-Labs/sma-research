# MuSK Allosteric Activator - Pre-Flight Plan

**Status:** DRAFT - Exploratory campaign (first-in-class, no published MuSK activator globally)
**Date:** 2026-04-17
**Author:** Opus (autonomous GPU fleet)
**Campaign ID:** musk_activator_alphaC
**Contract:** 35120540 (A100 PCIE 40GB, ssh4.vast.ai:10540, Japan)

## Scientific rationale

MuSK (Muscle-Specific Kinase, UniProt O15146) is the master tyrosine kinase
that clusters AChR at the neuromuscular junction (NMJ). The agrin - LRP4 - MuSK - DOK7
signaling axis is the single most important NMJ-forming and NMJ-maintaining pathway.

- SMA patients exhibit NMJ dysfunction as one of the earliest and most severe
  phenotypes (Simon Lab line; Kong 2009; Kariya 2008; Martinez-Hernandez 2013).
- Direct MuSK activation drives AChR clustering - a mechanism-consistent rescue
  path for SMA NMJ dysfunction that is independent of SMN restoration.
- Agrin-like biologics (e.g., agrin-MuSK agonist antibodies in ALS/Cachexia, Burden
  lab) validate the target pharmacologically.
- No published small-molecule MuSK activator exists worldwide. First-in-class.

**Target:** MuSK (UniProt O15146, human), kinase domain.
**Strategy:** allosteric activator targeting the alphaC-helix region, same design
pattern as the LIMK2 and ROCK2 alphaC-activator campaigns.

## Target selection

- **PDB:** **1LUF** (Till 2002, rat MuSK kinase domain, apo autoinhibited state).
  Pre-flight catch: 3HKL is the Frizzled-like cysteine-rich EXTRACELLULAR domain
  of MuSK, NOT the kinase domain. 2IEP is the MuSK Ig1+2 extracellular domain.
  2X5V is unrelated (photosynthetic reaction centre). 1LUF is the canonical
  MuSK kinase-domain structure (Till, Becker & Hubbard 2002, Structure 10:1187).
- 1LUF is rat MuSK (UniProt Q62838); kinase domain 96% identical to human O15146;
  residue numbering is the same between the two orthologs.
- Chain A residues 560-860 (kinase domain, apo).
- No bound ligand - no ATP-site contamination in pocket derivation.

## Pocket derivation (alphaC-helix) - canonical motifs VERIFIED by sequence scan

VAVK motif scan on 1LUF chain A confirmed:
- **beta3-Lys (VAVK)**: **K608** (LYS at 608, VAVK at 605-608)
- **alphaC-Glu (KxxE)**: **E625** (+17 from K608, canonical offset; GLU confirmed)
- **HRD catalytic**: H722 (HRDL at 722-725)
- **DFG motif**: **D742** (DFG at 742-744, ASP confirmed)

Note: 1LUF is the autoinhibited state, so K608-E625 CA distance = 11.4 A
(alphaC-out conformation). This is EXACTLY the state we target for an activator:
binding the back of alphaC to stabilize the alphaC-in rotation.

Strategy for pocket center:
1. Parse 1LUF chain A.
2. alphaC helix window **617-628** (12 residues, helix continuity < 4.5 A
   consecutive CA verified).
3. Pocket center = mean CA of alphaC residues 617-628.
4. Sanity checks:
   - distance(center, K608-CA) in [5, 18] A
   - distance(center, E625-CA) in [1.5, 8] A (center must sit ON alphaC)
   - distance(center, D742-CA) in [5, 22] A (DFG reference)
   - helix continuity: all consecutive CA-CA < 4.5 A
5. Abort run if any sanity check fails.

Pocket radius: **10 A**, matching LIMK2 and ROCK2 alphaC runs.

## Workflow (on A100)

1. SSH into contract 35120540 (ssh4:10540). Verify `/results/READY`.
2. Clone PocketXMol at SHA 65488cf635c856101dbe703ac97e2f10f58e005c.
3. Install deps:
   - torch 2.4.0 + cu124 (already matches image)
   - torch-scatter, torch-sparse, torch-cluster, torch-spline-conv,
     pyg-lib (wheels from https://data.pyg.org/whl/torch-2.4.0+cu124.html)
   - torch_geometric, lightning
   - PeptideBuilder, lmdb, meeko, openbabel-wheel
   - rdkit, biopython, easydict, omegaconf, numpy, pandas.
4. Download PocketXMol weights from Zenodo 17801271 (611 MB) to
   `/workspace/PocketXMol/data/trained_models/`.
5. Fetch 1LUF: `wget https://files.rcsb.org/download/1LUF.pdb -O /results/musk_activator/1luf.pdb`.
6. Run pocket-derivation script (`/results/musk_activator/musk_alphaC_pocket.py`);
   emit `pocket_center.txt` + `pocket_audit.json` + `3hkl_kinase_chainA.pdb`.
7. Write PocketXMol Hydra YAML config with alphaC pocket, 600 molecules, batch 50.
8. **Smoke test:** 5 molecules first (< 2 min). Assert 5 valid SDFs.
9. **Full launch:** tmux session `pxm_musk`, 600 molecules.
10. Monitor: GPU util > 60%; heartbeat via log tail.

## Post-generation (host-side)

11. rsync `/results/musk_activator/generated/` -> `/home/bryza/fleet-results/musk_activator_alphaC/`.
12. RDKit filters: valence-valid, Lipinski RO5.
13. BBB filter (hardfilter threshold 0.5) - NMJ is peripheral so BBB is NOT required,
    but we still keep the filter to drop CNS-toxic leads and keep parity with
    downstream Boltz-2 queue schema. We will NOT drop non-BBB compounds; just tag.
14. Queue Boltz-2 rescore on `sma-h100-two:8003` for top 100 by PocketXMol confidence.

## Selectivity context (downstream follow-up, not this agent)

MuSK kinase domain is closely related to ALK, RET, ROS1, and TrkA/TrkB/TrkC
(neurotrophin receptors). Downstream selectivity panel MUST include those six
off-targets. NOT this campaign's scope - document in RESULTS.md.

## Quality gates (HARD)

- Pocket derivation script saved for audit at
  `/home/bryza/gpu-fleet/scripts/musk_alphaC_pocket.py`.
- Smoke test MUST PASS before full launch.
- All results filed with `STATUS: DRAFT` until `triple_llm_verify` returns 3/3 PASS.
- **Critical caveat:** No published MuSK small-molecule activator exists. No wet-lab
  precedent for "MuSK restoration in SMA NMJ rescues phenotype in vivo" via small
  molecule. This campaign is exploratory compute only.
- Do NOT surface to external collaborators (Simon, Torsten) until QMS audit complete
  AND the PERP + LIMK2 retraction-brief traceability standard is met.
- Every numeric claim must be traceable to a source file.

## Expected output

- 600 SDFs (poses in the alphaC pocket).
- `gen_info.csv` with PocketXMol confidences.
- After RDKit/Lipinski filter: ~300-550 compounds.
- After Boltz-2 rescore: ranked top-100 by iptm against MuSK fold.

## ETA

- Install + weights: ~8-10 min on A100 PCIE (Japan - possibly slower Zenodo).
- 600-mol generation at batch 50, 100 denoising steps: ~40-60 min on A100 40GB.

## Risks

| risk | mitigation |
|---|---|
| 3HKL numbering offset from UniProt | pocket script cross-checks via conserved E730-K608 distance; aborts on mismatch |
| alphaC range wrong in 3HKL | sequence scan for E730 in the structure + helix continuity verification |
| ssh4:10540 SSH flakiness (Japan link) | 2-3 retries with 30s sleep; tmux persistence |
| PocketXMol OOM at batch 50 | fall back to batch 25 (40GB A100 unlikely to OOM) |
| Zenodo rate-limit from Japan | wget -c resume; 3 retries |

## Budget

A100 PCIE: ~$0.60-0.70/hr x ~1.5 hr (install + full run + rsync) = **~$1.00**.

## Decision log

- DECISION: target **1LUF** (rat MuSK kinase domain, Till 2002), NOT 3HKL.
  PRE-FLIGHT CATCH: 3HKL header confirms "Frizzled-like cysteine-rich domain of
  MuSK" - this is the EXTRACELLULAR Fz-CRD domain, NOT the kinase domain.
  2IEP is MuSK Ig1+2 extracellular (also not the kinase). 2X5V is unrelated
  (photosynthetic reaction center). 1LUF (rat Q62838, 96% identical to human
  O15146 kinase domain) is the canonical MuSK kinase-domain structure.
- DECISION: apo 1LUF (no ligand) is actually BETTER than a liganded holo
  structure for alphaC-activator design - no ATP-site occupancy to confuse
  the pocket extractor.
- DECISION: motif-scan-verified residues (K608/E625/D742), not assumed
  numbering. This is the mandated dataset-verify-before-use SOP.
- DECISION: alphaC-helix pocket, not DFG-out or JM-autoinhibitory - alphaC is
  the classic activator site (type III kinase activators target it). MuSK is
  also activated through JM (juxtamembrane) disinhibition biologically, but
  the JM region is absent from 3HKL construct.
- DECISION: 600 mols, not 3000 - budget-constrained; scale to 3000 only if
  round 1 yields >= 20 Boltz-2-ranked hits after selectivity panel.

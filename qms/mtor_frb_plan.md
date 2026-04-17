# mTOR FRB-Domain Allosteric Modulator — PocketXMol Campaign

**Date**: 2026-04-17
**Campaign ID**: `mtor_frb_allosteric`
**Instance**: 35120540 (A100 PCIE 40GB, ssh4.vast.ai:10540, $0.5867/hr — Japan)

## Rationale — Why FRB (not ATP site)

V1 mTOR campaign (Agent a27d060f) targeted the ATP-competitive site (standard mTOR kinase
inhibitor pocket, overlaps sirolimus/rapalogs/everolimus/AZD8055/Torin target). That is
well-covered territory with ~20+ clinical candidates.

V2 pivots to the **FRB (FKBP12-Rapamycin-Binding) domain** — a distinct allosteric site
only ~100 aa (residues 2015-2114). Rapamycin binds FRB via the **FKBP12 adapter protein**.
Small molecules targeting FRB **directly** (bypassing FKBP12) represent a **novel allosteric
class**:
- FKBP12-independent → different tissue distribution (FKBP12 expression-independent)
- Different selectivity profile vs rapamycin (rapamycin-analogues require FKBP12)
- Potentially different substrate selectivity (TORC1 substrates with FKBP12-gated access)

This is relevant to SMA because mTOR axis modulation is a secondary supportive target for
neuron survival (autophagy balance) — an FRB-direct binder would be a new chemotype.

## Target

- **Protein**: mTOR / FRAP (UniProt P42345)
- **PDB**: **1FAP** (TITLE verified: "THE STRUCTURE OF THE IMMUNOPHILIN-IMMUNOSUPPRESSANT
  FKBP12-RAPAMYCIN COMPLEX INTERACTING WITH HUMAN FRAP")
- **Chain B** = FRAP/mTOR FRB fragment, residues **2018-2112** (covers the canonical FRB 2015-2114)
- **Chain A** = FKBP12 (remove for direct-FRB design — we do NOT want FKBP12 adapter in pocket)
- **Key aromatic triad** (rapamycin-binding) — all confirmed present on chain B:
  - **Trp2101** (TRP)
  - **Tyr2104** (TYR)
  - **Phe2108** (PHE)
  - Also: Phe2039, Lys2095, Thr2098 (binding-site residues)

## Method — De Novo SBDD on FRB Pocket

PocketXMol `sbdd_simple.yml` config:
- Preprocessing: keep only chain B (mTOR FRB); remove chain A (FKBP12) + rapamycin HETATM
- Pocket center: COM of **Trp2101, Tyr2104, Phe2108** side-chain centroids
  (computed on-instance from 1FAP chain B)
- Pocket radius: 8.0 Å (FRB pocket is SMALLER than ATP site — tight hydrophobic triad)
- `sample.num_mols: 600`
- `sample.batch_size: 50`
- Molecule size: Normal(mean=28, std=2) atoms, min=5 — drug-like MW 300-500 Da
  (FRB pocket is small; avoid >40-atom ATP-class compounds)

## Success Metrics

Primary:
- RDKit-valid fraction ≥80%
- Top-5 with QED ≥0.5 and hydrophobic character (FRB is HYDROPHOBIC pocket — aromatic triad)
- Docking overlap with aromatic triad residues (DiffDock C_rel vs rapamycin FRB-part baseline)

Secondary:
- BBB pass rate (mTOR CNS-relevant → aim BBB pass ≥40%)
- Selectivity warning: ATP-site overlap check (z-panel vs kinases) — FRB binders SHOULD NOT
  hit the kinase panel

## Throughput Targets

- Smoke: 5 mols < 5 min
- Full: 600 mols, target < 4 hr on A100 PCIE 40GB
- GPU util > 60%

## Deliverables

1. `/home/bryza/fleet-results/mtor_frb_allosteric/` (pulled from instance)
   - `molecules.smi`, `SDF/`, `gen_info.csv`
2. `mtor_frb_RESULTS.md`:
   - Pocket derivation (Trp2101/Tyr2104/Phe2108 COM)
   - Top-5 SMILES + QED + BBB + aromatic/hydrophobic character
   - Contrast vs V1 ATP-site mTOR
3. Boltz-2 stage (separate) — top 100 → localhost:8004
4. triple_llm_verify JSON → DRAFT → VERIFIED

## Risks / Gotchas

- FRB pocket is SHALLOW and hydrophobic — dominated by aromatic triad; may produce
  aromatic-heavy compounds (manage logP drift, Lipinski compliance)
- No FKBP12 in input → model cannot use FKBP12-adapter contacts (this is BY DESIGN for
  direct binders, but expect lower binding affinity than rapamycin's FKBP12-gated mode)
- 1FAP is relatively old (1996, 2.7 Å) — pocket sidechain rotamers may be rapamycin-induced;
  apo/closed-state rotamers could differ. Acceptable for design, flag for Boltz-2 validation.
- FRB pocket "LTOR motif" hydrophobic triad means generated compounds may have poor PK
  (logP > 5) — check in post-filter

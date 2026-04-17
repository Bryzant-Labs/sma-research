# NRF2/KEAP1 Redox Axis Drug-Discovery Campaign — Plan

**Campaign ID**: `nrf2_keap1_campaign`
**Output root**: `/home/bryza/fleet-results/nrf2_keap1_campaign/`
**Launched**: 2026-04-17 (Budapest SMA Congress 2026 priority #2 "wide-open NRF2/KEAP1" per `sma-congress-2026-priorities.md`)
**Status**: DRAFT (pending triple_llm_verify 3/3 PASS, Simon-Comms-Gate HELD)

## Hypothesis

SMA motor neurons show elevated oxidative stress (Singh 2020 PMID 32891838, Miller 2016 PMID 26658556). NRF2 (Q16236) is the master antioxidant response transcription factor. Under homeostasis, KEAP1 (Q14145) Kelch domain grips NRF2 Neh2 domain via the ETGE (residues 77-82) and DLG (29-31) motifs, ubiquitinating NRF2 for proteasomal degradation. Small-molecule disruption of the KEAP1-Kelch × NRF2-Neh2 PPI (primary PMID 17127771) releases NRF2 to translocate into the nucleus and induce ARE-driven antioxidant genes (NQO1, HMOX1, GCLC, etc.).

**Clinical precedent**: DMF/Tecfidera (MS), Bardoxolone-methyl (CKD, withdrawn on safety), Omaveloxolone/Skyclarys (FRDA, approved 2023), Sulforaphane (natural). **Zero direct SMA trials** = wide-open real estate.

**Our angle**: discover BBB-permeant, **non-covalent** KEAP1 Kelch PPI inhibitors (safer than triterpenoid electrophiles for chronic SMA dosing) using generative + physics-based pipeline. Non-covalent binders avoid the off-target cysteine reactivity that made bardoxolone cardiotoxic.

## Targets — TITLE-verified 2026-04-17 (per `rule-dataset-verify-before-use.md`)

| PDB / AF | Source | TITLE | Organism | Role | MD5 |
|---|---|---|---|---|---|
| **4L7B** | RCSB | "STRUCTURE OF KEAP1 KELCH DOMAIN WITH (1S,2R)-2-{[(1S)-1-[(1,3-DIOXO-1,2,3-DIHYDRO-2H-ISOINDOL-2-YL)METHYL]-3,4-DIHYDROISOQUINOLIN-2(1H)-YL]CARBONYL}CYCLOHEXANECARBOXYLIC ACID" | Human (taxid 9606) | **PRIMARY** — PocketXMol input, co-crystal ligand 1VV defines pocket | `91149584f4cf3ea5ab497c752a152268` |
| **2FLU** | RCSB | "CRYSTAL STRUCTURE OF THE KELCH-NEH2 COMPLEX" | Human (taxid 9606) | Orthogonal co-crystal: KEAP1-Kelch (chain X) + NRF2 Neh2 16-mer peptide (chain P) | `9ee98dffa500acdced19d86eba568e42` |
| 3WN7 | RCSB | "CRYSTAL STRUCTURE OF KEAP1 IN COMPLEX WITH THE N-TERMINAL REGION OF THE NRF2 TRANSCRIPTION FACTOR" | **Mouse** (taxid 10090) | Orthogonal (not used for compute) | `0ab0b3de9505505d109648ca03e8679c` |
| 7OFE | RCSB | "KEAP1 KELCH DOMAIN BOUND TO A SMALL MOLECULE INHIBITOR OF THE KEAP1-NRF2 PROTEIN-PROTEIN INTERACTION" | **Mouse** (taxid 10090) | Tertiary (not used for compute) | `7a6b43e5f92a034dcaca80b0b41d6321` |
| AF-Q16236-F1 v6 | AlphaFold DB | NRF2 (NFE2L2) full-length 605 aa | Human | Neh2 domain scaffold (residues 17-86 IDR; ETGE 77-82, DLG 29-31) | `4b82eb7e98bf6ba42d781a59a4ca4b2e` |

**Pocket definition (4L7B chain B)** — verified all 7 canonical Kelch PPI hotspot residues present: R380, R415, R483, S363, S508, Y334, Y572. Pocket center (COM of native 1VV ligand, chain B): **[-3.561, 2.506, -27.501] Å**. Pocket radius: 10 Å. Pocket neighborhood (5.5 Å of 1VV): 16 residues — ALA556, ARG380, ARG415, ASN382, ASN414, GLY364, GLY462, GLY509, GLY603, PHE577, SER363, SER508, SER555, SER602, TYR334, TYR572.

## Pipeline (full v2.1)

### Phase 1: Target structures [DONE]
- PDBs downloaded + MD5-verified 2026-04-17 17:10 UTC, logged in `DATA_INVENTORY.md` Structural Accessions.

### Phase 2: Library generation [DONE]
- **GenMol hosted NIM** — 5 scaffolds × 400 mol = 2000 requested, 1385 unique SMILES harvested (inline `[*{N-N}]` SAFE markers, T=1.7-1.9):
  - `genmol_nrf2_v2_ml334core` — ML334 tetrahydroisoquinoline-aryl, 308 unique
  - `genmol_nrf2_v2_ki696core` — benzoic acid Arg-triad anchor, 259 unique
  - `genmol_nrf2_v2_naphthyl` — naphthalene hydrophobe (KI-696 inspired), 261 unique
  - `genmol_nrf2_v2_bicarbox` — aliphatic carboxylate Neh2-ETGE backbone mimic, 246 unique
  - `genmol_nrf2_v2_sulfonamide` — arylsulfonamide (KI-696 H-bond donor), 311 unique
- **PocketXMol** — 2000 molecules requested against KEAP1 Kelch 4L7B pocket, **running now** on ssh4.vast.ai:10546 (A100 SXM4 40GB, attached idle, $0.81/hr). Config: 100 diffusion steps, bs=40, mol-size mean=32 heavy atoms, pocket_coord=[-3.561, 2.506, -27.501], radius=10 Å.
- **RFdiffusion binders** — *skipped for this campaign* (Brev+VastWorker saturated). Optional follow-up track if first Boltz-2 pass yields insufficient selective hits.

### Phase 3: Scoring cascade [FIRING]
- **ADMET heuristic filter** (RDKit Descriptors + QED + Lipinski + BBB-heuristic Clark-1999): 1395 combined (1385 GenMol + 10 reference) → **354 survivors** (25.4% pass) with Lipinski_viol ≤ 1, QED ≥ 0.4, 300 ≤ MW ≤ 550, BBB_heuristic ≥ 0.70.
- **Boltz-2 15-target selectivity panel**: 25 tasks queued (top-100 × 5 Kelch-repeat targets). Panel = KEAP1_Kelch (primary, UNP Q14145:321-609) + KLHL20 / KLHL22 / KBTBD11 / KLHDC2 Kelch fragments as off-targets. Z-score per row = z_KEAP1 > 0 AND selectivity_z > 0 defines true KEAP1-selective binder.
- **DiffDock co-dock** against KEAP1 Kelch — deferred to Phase 4 (used only on top-20 Boltz-2 survivors), uses self-host if NIM 401s.

### Phase 4: Top-5 MD (planned, not yet fired)
- 50ns POCKET_FIXED MD on top-3 Boltz-2 z>1.5 candidates (per `learnings-gpu-fleet-2026-04-14.md` MMPBSA POCKET_FIXED hotkey).
- 25ns on remaining 2 (budget-aware, ~$10 GPU rental).
- Cys151 proximity tracking (retain 2026-04-12 mechanism: covalent vs non-covalent classifier).

## GPU allocation (scale-up authorized)
Budget cap: $30 total for full campaign (24-36h wall time).
- **Actually spent**: $0 external rent as of Phase 2 completion (reused idle ssh4:10546 A100 for PocketXMol, HostedNIM free tier for GenMol + Boltz-2).
- Phase 4 MD: budget reserved $8-12 for 1× A100 rental × 24h if no idle instance available.

## Hard gates (SOP-compliant)
- DRAFT only. Simon-Comms-Gate HELD until:
  - Triple-LLM 3/3 PASS on RESULTS doc.
  - Christian Fischer SEND trigger.
- TITLE-verified every PDB (2026-04-17 data-integrity incident rule).
- No idle GPUs — ssh4 will be re-queued or destroyed after Phase 2 completes.
- Every dataset/PDB logged in `DATA_INVENTORY.md` with MD5.

## Outputs
- `/home/bryza/fleet-results/nrf2_keap1_campaign/` — all SDFs, TSVs, logs
- `libraries/aggregated/genmol_v2_dedup.csv` — 1385 unique GenMol mols with QED scores
- `libraries/aggregated/admet_full.csv` — ADMET heuristics on 1393 parsed compounds
- `libraries/aggregated/admet_filtered_lipinski_qed_mw_bbb.csv` — 354 survivors
- `libraries/aggregated/combined_library.smi` — GenMol + 10 references
- `receptors/selectivity_panel_kelch.json` — 5-Kelch Boltz-2 panel sequences
- `/home/bryza/sma-research/qms/NRF2_KEAP1_REDOX_CAMPAIGN_RESULTS.md` — full RESULTS (will be written after Phase 4)

## CLAIMS_REGISTRY plan
Will add new claim UNDER_REVIEW after Phase 3 Boltz-2 completes:
> "Computational discovery of X BBB-permeant non-covalent KEAP1-Kelch PPI inhibitors with Y-fold selectivity over related Kelch-repeat proteins (KLHL20/22, KBTBD11, KLHDC2), as SMA redox-axis leads."

## Cross-connections (per `rule-cross-connection-mandate`)
- NRF2 activation → HMOX1/GCLC upregulation → reduced oxidative stress in MN → complements ROCK2/LIMK2 cytoskeleton work (different axis, synergy potential).
- NRF2 → NQO1 induction → detoxification, potentially reducing the cellular stress from `4-AP` + `Fasudil` chronic exposure (supportive care synergy).
- KEAP1 intersects with autophagy (p62/SQSTM1 binding) — possible second mechanism for SMA proteostasis (SMN complex turnover).
- Simon Congress priorities: NMJ (#1), NRF2/KEAP1 (#2, THIS), Bruno translation (#3), cerebellum (#6).

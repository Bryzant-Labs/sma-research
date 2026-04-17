# PAK4 Allosteric Activator - Pre-Flight Plan

**Status:** DRAFT - Exploratory campaign (PAK4 activator for SMA NMJ actin dynamics; HIGHLY EXPLORATORY)
**Date:** 2026-04-17
**Author:** Opus (autonomous GPU fleet)
**Campaign ID:** pak4_activator_alphaC
**Contract:** 35120540 (A100 PCIE 40GB, ssh4.vast.ai:10540, Japan)

## Scientific rationale

PAK4 (p21-Activated Kinase 4, UniProt O96013) is a Group-II Cdc42/Rac1-effector
serine/threonine kinase in the rho-family. Phosphorylates LIMK1 to phosphorylate
cofilin (actin-severing), phosphorylates GEF-H1, and remodels the actin
cytoskeleton at the neuromuscular junction (NMJ). PAK4-knockout mice are
embryonic-lethal with NMJ defects.

- PAK4 sits in the **rho/cdc42/rac1 -> PAK -> LIMK -> cofilin -> F-actin** axis
  that our campaigns target via LIMK2-selective inhibitors.
- PAK4 activation stabilizes F-actin at synaptic terminals and at the motor
  endplate, plausibly rescuing NMJ actin organization in SMA.
- PAK4 appears in our 15-kinase selectivity panel as a near-neighbour of LIMK2
  (shared Cdc42/Rac1 effector module).
- **Caveat:** PAK4 is ALSO overexpressed in several cancers (colon, prostate)
  so an activator is oncology-adjacent. Downstream selectivity against PAK1/2/3
  and oncology risk must be evaluated before any external surface.
- No published small-molecule PAK4 ACTIVATOR. Most PAK4 drug programs have
  pursued INHIBITORS for cancer (PF-03758309, KPT-9274). Activator design
  is first-in-class and exploratory for SMA.

**Target:** PAK4 (UniProt O96013, human), kinase domain.
**Strategy:** allosteric activator targeting the alphaC-helix region, same
design pattern as the LIMK2, ROCK2, and MuSK alphaC-activator campaigns.

## Target selection - PDB verified 2026-04-17

Candidates considered (all verified via PDB TITLE + DBREF to O96013):

| PDB | TITLE | ligand | pick? |
|---|---|---|---|
| 2X4Z | PAK4 + PF-03758309 ATP-site inhibitor | 7KC (PF-3758309), GOL, SEP | NO - alphaC locked-out by ATP-site inhibitor |
| 4FIE | Full-length human PAK4 | ANP (ATP analog), SEP | NO - ATP site occupied |
| 4FII | Catalytic domain + RPKPLVDP peptide | SEP | ~ smaller construct |
| **4JDH** | **Catalytic domain + PAKtide substrate** | SEP only | **YES - clean ATP site** |
| 4APP | PAK4 + tetrahydropyrrolopyrazole inhibitor | ATP-site inhibitor | NO |

**PICK: 4JDH** (Ha, Davis, Boggon 2013). Human PAK4 kinase domain, residues
300-589 chain A, phospho-S474 (activation-loop autophosphorylation, active-like
state), PAKtide peptide substrate in chain B (removed during preprocessing).
No ATP-site ligand. Clean pocket geometry for alphaC-back extraction.

DBREF verified: 4JDH chain A residues 300-589 map UniProt O96013 300-589 (1:1).
No numbering offset.

## Pocket derivation (alphaC-helix) - motif scan VERIFIED

Sequence-motif scan on 4JDH chain A (290 residues, 300-589):
- **beta3-Lys (VAVK motif at 347-350)**: **K350** -> LYS (confirmed via scan;
  PAK4 uses VAVK, not the more common VAIK/VAAK)
- **alphaC-Glu (KxxE pair)**: **E366** (+16 from K350; canonical offset for
  PAK-family kinases)
- **HRD catalytic**: **H438** (HRD at 438-440)
- **DFG motif**: **D458** -> ASP (DFG at 458-460)

K350-E366 CA distance = 10.23 A. This is LARGER than the canonical 4-6 A
alphaC-in salt-bridge distance. Together with phospho-S474 (active-like), this
indicates 4JDH sits in a partially alphaC-displaced state. An activator can
engage the back-of-alphaC surface to stabilize the fully-closed alphaC-in
geometry (K-E salt bridge formation).

### Pocket center

- alphaC helix window: **358-370** (13 residues, E366 center +/- 5)
- Helix continuity: all consecutive CA-CA < 4.5 A verified (13 CAs)
- **Pocket center (A): (-19.137, 13.183, -16.462)**
- Pocket radius: **10 A**

### Sanity checks (all PASS)

| check | value | range | ok |
|---|---|---|---|
| dist(center, K350-CA) | 12.56 A | [5, 18] | PASS |
| dist(center, E366-CA) | 4.58 A | [1.5, 8] | PASS |
| dist(center, D458-CA, DFG) | 10.53 A | [5, 22] | PASS |
| dist(center, H438-CA, HRD) | 12.08 A | [5, 22] | PASS |
| alphaC helix continuity | max gap < 4.5 A | - | PASS |
| nearest HETATM (SEP/pS474) | 10.72 A | > 5 A | PASS |
| reference residues resolved | K350=LYS, E366=GLU, D458=ASP, H438=HIS | - | PASS |

## Workflow (on A100)

1. [DONE] SSH into contract 35120540 (ssh4:10540). `/results/READY` verified.
2. [DONE] PocketXMol already installed at /workspace/PocketXMol (SHA 65488cf).
   INSTALL SKIP - warm from MuSK campaign.
3. [DONE] Fetched 4JDH to /results/pak4_activator/4jdh.pdb.
4. [DONE] Ran pocket-derivation script -> pocket_center.txt + pocket_audit.json
   + 4jdh_kinase_chainA.pdb. Sanity PASS.
5. Write PocketXMol Hydra YAML config: alphaC pocket, 600 mols, batch 50.
6. **Smoke test:** 5 molecules (< 2 min). Assert >= 3 valid SDFs.
7. **Full launch:** tmux session `pxm_pak4`, 600 molecules.
8. Monitor: GPU util > 60%; heartbeat via log tail.

## Post-generation (host-side)

9. rsync `/results/pak4_activator/generated/` -> `/home/bryza/fleet-results/pak4_activator_alphaC/`.
10. RDKit filters: valence-valid, Lipinski RO5.
11. BBB filter hardfilter threshold 0.5 - PAK4 NMJ rescue is peripheral
    (NMJ at motor endplate, skeletal muscle); BBB NOT required; filter tags,
    does not drop (parity with MuSK pipeline).
12. Queue Boltz-2 rescore for top 100.

## Boltz-2 target

Prefer H100 TW #2 (`ssh6.vast.ai:10548`) if Agent a88a7d70 has it ready.
Fallback: stage at `/home/bryza/fleet-results/pak4_activator_alphaC/boltz2_queue.jsonl`
for later rescore on `sma-h100-two:8003`.

## Selectivity context (downstream follow-up, not this agent)

PAK4 kinase domain is closely related to:
- **PAK1, PAK2, PAK3** (Group-I PAKs) - high homology, must be in panel
- **PAK5, PAK6** (Group-II PAKs) - sister kinases
- **LIMK1, LIMK2** (downstream PAK4 substrates) - also in our panel
- **ROCK1, ROCK2** (parallel rho-effector) - also in our panel

Our 15-kinase panel already includes LIMK2/ROCK2. Adding PAK1 at a minimum
is REQUIRED for PAK4 selectivity. Document as MUST-DO in RESULTS.md.

## Quality gates (HARD)

- Pocket derivation script saved for audit at
  `/home/bryza/gpu-fleet/scripts/pak4_alphaC_pocket.py`.
- Smoke test MUST PASS before full launch.
- All results filed with `STATUS: DRAFT` until `triple_llm_verify` 3/3 PASS.
- **Critical caveat:** PAK4 activator = oncology-adjacent; must flag in all
  external-facing docs. PAK4 is oncogenic when hyperactive (colon, pancreatic).
  Activator design for SMA NMJ is a narrow therapeutic-window proposition.
  First-in-class and HIGHLY EXPLORATORY for SMA.
- Do NOT surface to external collaborators (Simon, Torsten) without explicit
  Christian sign-off.
- Every numeric claim must be traceable to a source file.

## Expected output

- 600 SDFs (poses in the alphaC pocket).
- `gen_info.csv` with PocketXMol confidences.
- After RDKit/Lipinski filter: ~300-550 compounds.
- After Boltz-2 rescore: ranked top-100 by iptm against PAK4 fold.

## ETA

- Install + weights: 0 min (warm from MuSK run).
- 600-mol generation at batch 50, 100 denoising steps: ~3-5 min on A100 40GB
  (MuSK precedent: 2 min 9 sec).

## Risks

| risk | mitigation |
|---|---|
| 4JDH numbering offset from UniProt | DBREF confirmed 1:1, motif scan double-checks |
| alphaC range wrong in 4JDH | 13-CA helix continuity verified < 4.5 A |
| PAK4 alphaC K-E distance 10 A (not classic 4-6 A) | acceptable; active-like partially-open state; ideal for activator that closes K-E |
| ssh4:10540 SSH flakiness (Japan link) | 2-3 retries with 30s sleep; tmux persistence |
| PocketXMol OOM at batch 50 | MuSK precedent used 1929 MiB / 40960 MiB; OOM impossible |
| PAK4 oncology risk | flag in RESULTS, require PAK1/2/3 selectivity panel |

## Budget

A100 PCIE Japan: $0.60-0.70/hr x ~0.3 hr (smoke + full run + rsync) = **~$0.20**.
Install skip saves ~7 min vs cold start.

## Decision log

- DECISION: target **4JDH** (human PAK4 300-589 + pS474, PAKtide-bound, no
  ATP-site ligand). Beats 2X4Z/4FIE/4APP for pocket cleanliness - those have
  ATP-site inhibitors or ANP.
- DECISION: motif-scan-verified residues, not assumed numbering. PAK4 uses
  VAVK motif (K350), NOT VAIK as assumed in many generic kinase templates.
- DECISION: alphaC-helix pocket, same pattern as LIMK2/ROCK2/MuSK campaigns.
- DECISION: 600 mols, matching MuSK/ROCK2 scale. Scale to 3000 only if Boltz-2
  rescore yields >= 20 ranked hits after PAK1/2/3/5/6 selectivity panel.
- DECISION: BBB tag-only (not drop) - NMJ is peripheral.
- DECISION: keep 4JDH's SEP at pS474 ALIVE in the geometry but STRIP from
  the PocketXMol input PDB (pocket center 10.7 A away - doesn't affect
  pocket extraction). Clean ATOM-only chain A.

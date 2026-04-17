# DOK7 PTB PocketXMol MuSK-Dimer-Stabilizer Campaign — Plan

**Campaign ID**: `dok7_binder`
**Instance**: A100 SXM4-40GB, Slovenia, contract 35120543 (ssh2:10542)
**Launched**: 2026-04-17
**Status**: DRAFT (pending triple_llm_verify 3/3 PASS)

## Target

- **Protein**: DOK7 — Docking protein 7 (Dok-family adaptor)
- **UniProt**: Q18PE1 (human, 504 aa)
- **Domain**: PH-PTB tandem (residues 1-220, PH domain 1-110 + PTB domain 111-220)
- **PDB**: **3ML4** — *Crystal structure of a complex between Dok7 PH-PTB and the MuSK juxtamembrane region* (Bergamin et al. 2010, Mol. Cell 39:100)
- **PDB TITLE-verified**: `TITLE     CRYSTAL STRUCTURE OF A COMPLEX BETWEEN DOK7 PH-PTB AND THE MUSK JUXTAMEMBRANE REGION`
- **Method**: X-ray, 2.6 Å, R_free 0.30
- **Chains**: A,B,C,D (four DOK7 PH-PTB copies, 1:1 dimer-of-dimers) + E,F,G,H (MuSK JMR 13-aa peptide, residues 544-556)
- **Chain used**: A (DOK7 PTB) + E (MuSK JMR) for interface derivation.

3ML4 is the **only** DOK7 crystal structure in PDB.

## Pocket derivation

**Strategy**: canonical PTB phospho-tyrosine recognition groove that reads MuSK Y553.

From `/opt/dok7_pocket.py`:

DOK7 chain A has 15 residues within 5Å of MuSK JMR (chain E). Focal PTB core:
- L154, S155, D156, L157, **R158**, **R159**, **Y160**, G161, V163 (9 residues)
- Plus secondary: I168, R174, S193, D197, V200, R201

The **R158/R159/Y160 triad** is the canonical PTB pY-recognition motif:
- R158/R159 arg-arg dyad → coordinates the phosphate of pY553
- Y160 → stacks against the tyrosine ring

Verified geometry: R158-R159 CA-CA = 3.79Å, R159-Y160 CA-CA = 3.79Å (perfect trans-peptide spacing, confirming sequential placement in same secondary structure element).

**Pocket center** (mean CA of 9 core residues):
```
pocket_center = [-80.758, -17.716, -27.745]
pocket_radius = 10.0 Å
core_extents = [7.80, 18.55, 12.76] Å
```

## Rationale (SMA)

1. **DOK7 binds phospho-MuSK Y553** via its PTB domain → induces MuSK dimerization → sustains trans-autophosphorylation → drives AChR clustering.
2. **Human DOK7 loss-of-function mutations cause Congenital Myasthenic Syndrome (CMS)** — a phenotypic mimic of SMA NMJ failure. DOK7 knock-in mouse therapy is in trials.
3. **In SMA**, NMJ fails to mature even when SMN is restored. A DOK7 potentiator (small molecule that stabilizes DOK7-MuSK complex or DOK7 dimer) could rescue NMJ independent of SMN status.
4. **CMS + SMA overlap**: DOK7 enhancer useful for both indications. Simon-lab NMJ relevance.

## Compute

- **Instance**: ssh2:10542 (A100 SXM4 40GB, Slovenia)
- **Warm state**: PocketXMol at `/opt/PocketXMol` (SHA `65488cf635c856101dbe703ac97e2f10f58e005c`), conda env `pxm_cu128`, weights cached, deploy script `/opt/pocketxmol_deploy.py`
- **n_molecules**: 600 (match CDK5/DUSP6/LIMK2-ATP campaigns)
- **batch_size**: 50
- **Smoke**: 5-mol first
- **tmux**: `pxm_dok7`
- **GPU util target**: > 60%

## Post-generation pipeline

1. RDKit sanity + QED/Lipinski filter
2. BBB tag-only (NMJ peripheral; don't hardfilter)
3. Top 100 → Boltz-2 panel (localhost:8004):
   - Primary: DOK7 PTB (Q18PE1)
   - Counter: MuSK (O15146) — we want DOK7 binder not MuSK binder
   - Counter: IRS1 PTB, SHC1 PTB (related PTB domains, cross-family selectivity)
4. Z-score selectivity: `z_DOK7 > 0` gate
5. DRAFT stays DRAFT until triple_llm_verify 3/3 PASS

## Risks / honest caveats

- **PTB groove is narrow** — canonical PTB pY-pocket is defined by 3 residues (R158/R159/Y160); generating a non-phosphopeptide small molecule mimic of pY is notoriously hard. Prior PTB-directed drug discovery has struggled.
- **Direction ambiguity**: a generator might yield a pY-mimetic that BLOCKS DOK7-MuSK rather than enhances it. Downstream assay will differentiate. Allosteric stabilizer mode preferred but hard to target computationally.
- **No native small-molecule ligand in 3ML4** — C_rel baseline unavailable; z-score across PTB family is the primary selectivity metric.
- **Single PDB** — no conformational ensemble; hits may not generalize across DOK7 conformations.
- **Dimer interface not targeted here** — 3ML4 dimer contact is separate from the PTB pY-pocket. A separate dimer-interface campaign would be complementary (not run today; single-target focus).

## File layout

- Plan: `/home/bryza/sma-research/qms/dok7_binder_plan.md` (this file)
- Pocket script: `/home/bryza/gpu-fleet/scripts/dok7_pocket.py` (also at `/opt/dok7_pocket.py` on instance)
- Pocket JSON (on A100): `/results/pocketxmol/dok7_binder/pocket_audit.json`
- Task JSON: `/home/bryza/sma-research/qms/dok7_binder_task.json`
- Results (on A100): `/results/pocketxmol/dok7_binder/`
- Local results: `/home/bryza/fleet-results/dok7_binder/`
- RESULTS doc: `/home/bryza/sma-research/qms/dok7_binder_RESULTS.md` (DRAFT)

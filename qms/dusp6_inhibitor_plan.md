# DUSP6 PocketXMol Inhibitor Campaign — Plan

**Campaign ID**: `dusp6_inhibitor`
**Instance**: A100 SXM4-40GB, Slovenia, contract 35120543 (ssh2:10542)
**Launched**: 2026-04-17
**Status**: DRAFT (pending triple_llm_verify 3/3 PASS)

## Target

- **Protein**: DUSP6 / MKP-3 / PYST1 — dual-specificity MAP kinase phosphatase 3
- **UniProt**: Q16828 (human)
- **PDB**: 1MKP — *Crystal structure of PYST1 (MKP3), catalytic domain* (Farooq et al. 2001, Mol. Cell 7:387)
- **PDB TITLE-verified**: `TITLE     CRYSTAL STRUCTURE OF PYST1 (MKP3)`
- **COMPND-verified**: `MOLECULE: PYST1; FRAGMENT: CATALYTIC DOMAIN; SYNONYM: DUAL SPECIFICITY PHOSPHATASE, MAP KINASE PHOSPHATASE 3, MKP-3; EC: 3.1.3.48, 3.1.3.16`
- **Organism**: *Homo sapiens* (taxid 9606)
- **Chain**: A, residues 204–347 (catalytic domain only, 144 residues)

## Catalytic pocket derivation

DUSP6 uses the dual-specificity phosphatase (DSP) fold. Signature motif is `CX5R` (catalytic cysteine + P-loop arginine 5 residues downstream, wrapping back in 3D).

**Residue-level inspection of 1MKP chain A (residues 280–305):**
```
280 ASP  281 GLU  282 ALA  283 ARG  284 GLY  285 LYS  286 ASN
287 CYS  288 GLY  289 VAL  290 LEU  291 VAL  292 HIS  293 SER
294 LEU  295 ALA  296 GLY  297 ILE  298 SER  299 ARG
```

- **Catalytic Cys** = Cys287 (SG coordinates `[-0.332, 75.826, 24.502]`)
- **P-loop Arg (charge stabiliser)** = Arg283 (guanidinium within ~7 Å CA-CA of Cys287). Note: the linear sequence reads C287-G-V-L-V-H292 then arcs, not the typical C-X5-R; however, **Arg283 sits spatially adjacent to Cys287 SG (5.7 Å CA-CA)** forming the classical DSP phosphate-binding pocket. Arg299 further downstream is on a surface loop (27 Å from Cys287), not in the active-site cleft.
- **1MKP is the apo/inactive conformation** (Farooq 2001 — inactive without ERK2 binding). Pocket is well-defined for generator but more extended than the bound state.

**Pocket center** (mean CA of 11 residues within 8 Å of Cys287.SG):
```
pocket_center = [3.11, 65.40, 21.17]
pocket_radius = 15.3 Å (tight core residues)
```

Effective generator radius: **10 Å** (standard for SBDD; broader than 15 Å raw because inactive pocket is shallow — 10 Å focuses generation near Cys287 while allowing Arg283 + surrounding hydrophobic residues).

**Pocket residues** (11): Gly232, Ile233, Lys234, Tyr235, Ala282, Arg283, Gly284, Lys285, Asn286, Cys287, Gly288.

## Rationale (SMA)

1. **DUSP6 inactivates ERK1/2** (MAPK). In SMA motor neurons, ERK/MAPK survival signalling is dysregulated (several datasets).
2. Inhibiting DUSP6 sustains ERK-pT202/pY204 → prolongs pro-survival signalling / extends ERK-dependent neurotrophic responses.
3. DUSP6 is already used as selectivity counter-screen on ssh1 vscreen (SSH1/SSH2/SSH3/DUSP6 panel). Direct DUSP6-inhibitor campaign produces a **positive reference set** for Z-score selectivity validation.
4. **Hedge status**: Like CDK5 / LIMK2-ATP, DUSP6 therapeutic direction (inhibition vs activation) is model-dependent — exploratory compute only; no therapy claim until meta-analysis APPROVED.

## Compute

- **Instance**: ssh2:10542 (A100 40GB SXM4), Slovenia, $0.69/hr
- **Warm state**: PocketXMol at `/opt/PocketXMol`, conda env `pxm_cu128`, weights cached, deploy script at `/opt/pocketxmol_deploy.py`
- **n_molecules**: 600 (match CDK5 + LIMK2-ATP batch size for cross-campaign comparability)
- **batch_size**: 50 (A100 SXM4 headroom allows, keeping at 50 for reproducibility with prior runs)
- **Smoke test**: 5 molecules first
- **tmux**: `pxm_dusp6`
- **GPU util target**: > 60 %

## Post-generation pipeline

1. BBB hardfilter (MW < 500, HBD ≤ 3, HBA ≤ 7, PSA < 90 Å², logP 1–4)
2. QED/Lipinski filter
3. Top 100 → Boltz-2 panel vs DUSP6 + SSH1 + SSH2 + SSH3 (4-phosphatase selectivity)
4. Z-score selectivity: `z_DUSP6 > 0` gate
5. DRAFT stays DRAFT until triple_llm_verify 3/3 PASS

## Risks / honest caveats

- **Apo-crystal generator** — 1MKP is uncomplexed; no native ligand to set C_rel baseline. Z-score across SSH1/SSH2/SSH3/DUSP6 is the primary selectivity signal.
- **DSP fold is flat** — shallow active sites notoriously hard to drug. Historic DUSP6 inhibitors (BCI, (E)-2-benzylidene-3-cyclohexylmethyl-2,3-dihydro-1H-inden-1-one) are allosteric, not active-site. Expect low hit rate on direct active-site generation.
- **No covalent warhead in vanilla PocketXMol** — Cys287 is normally targeted covalently; our molecules will be non-covalent, limiting affinity ceiling vs tool compounds.
- **Selectivity panel limited** — SSH1/SSH2/SSH3 are slingshot (CFL) phosphatases, structurally unrelated to DSPs. Panel tests cross-family selectivity but not within-DUSP selectivity (DUSP1/4/5/7/9 are closer paralogues).

## File layout

- Plan: `/home/bryza/sma-research/qms/dusp6_inhibitor_plan.md` (this file)
- Task JSON: `/home/bryza/sma-research/qms/dusp6_inhibitor_task.json`
- Pocket derivation script (on A100): `/results/pocketxmol/dusp6/derive_pocket.py`
- Pocket JSON (on A100): `/results/pocketxmol/dusp6/pocket.json`
- Results (on A100): `/results/pocketxmol/dusp6_inhibitor/`
- RESULTS doc: `/home/bryza/sma-research/qms/dusp6_inhibitor_RESULTS.md` (DRAFT)

# AGRIN LG3 PocketXMol LRP4-Interface Modulator Campaign — Plan

**Campaign ID**: `agrin_lg3_modulator`
**Instance**: A100 PCIE-40GB, Japan, ssh4:10540
**Launched**: 2026-04-17
**Status**: DRAFT (pending triple_llm_verify 3/3 PASS)

## Target

- **Protein**: AGRIN — LG3 (C-terminal Laminin-G3 globular domain)
- **UniProt (human)**: O00468 (2068 aa)
- **UniProt (PDB source)**: P25304 (rat, 95%+ identical in LG3), Q9QYP1 (rat LRP4)
- **PDB**: **3V64** — *Crystal Structure of agrin and LRP4* (Zong et al. 2012, Genes Dev 26:247)
- **PDB TITLE-verified**: `TITLE     CRYSTAL STRUCTURE OF AGRIN AND LRP4`
- **Method**: X-ray, 2.85 Å, R_free 0.2725
- **Chains used**: A (rat AGRIN LG3, residues 1759-1948, 191 aa) + D (rat LRP4 beta1-propeller, residues 396-737, 342 aa) — PocketXMol uses AGRIN chain A only; the LRP4 chain defines the interface target.

### Important: 3V64 COMPND mis-assignment (self-verified 2026-04-17)
The COMPND block labels FRAGMENT incorrectly relative to MOL_ID. RCSB API entity alignment verifies:
- Chain A/B = AGRIN P25304 1759-1948 (LG3)
- Chain C/D = LRP4 Q9QYP1 396-737 (β1-propeller)

## Pocket derivation

**Strategy**: interface-residues-of-AGRIN-contacting-LRP4 approach.

From `/opt/agrin_lg3_pocket.py` (script preserved in repo):

AGRIN chain A has 18 residues within 5Å of LRP4 atoms, clustering into two interfaces:
1. **Primary SEA/Z-exon face loop (residues 1779-1788)** — 10 consecutive residues, 15.8×6.7×6.1 Å tight cluster, contacting LRP4 chain D (primary LRP4-binding interface on AGRIN LG3).
2. Secondary loop (1844-1883) — 8 residues contacting LRP4 chain C (likely crystal packing artifact / 2:2 assembly).

We use the **SEA-face loop 1779-1788** as the pocket because it is the canonical LRP4-binding interface (Zong 2012 Fig 3).

**Pocket residues (10, all verified by sequence-identity motif check)**:
- S1779, E1780, L1781, T1782, N1783, E1784, I1785, P1786, A1787, E1788

**Contact partners on LRP4**: R447, R557, N469, W573, W599, H642, T488.

**Pocket center** (mean CA of 10 SEA-face residues):
```
pocket_center = [-27.992, 10.692, -38.546]
pocket_radius = 12.0 Å
loop_extents = [15.77, 6.70, 6.05] Å
```

Ca²⁺ ion (canonical LG3 structural calcium) at [-11.461, 7.636, -28.691], 19.5Å away from pocket — well clear of generator zone.

## Rationale (SMA)

1. **AGRIN-LRP4-MuSK axis** is the master switch of NMJ post-synapse development. AGRIN-LG3 from terminal Schwann cells + motor neuron termini → binds LRP4 → activates MuSK → clusters AChR.
2. **In SMA, NMJ fails to mature**. Agrin-mimetic or AGRIN-potentiator small molecules could rescue NMJ assembly — a mechanism orthogonal to SMN1 restoration (risdiplam, nusinersen, Zolgensma all restore SMN but do not fully restore NMJ).
3. **Simon-lab relevance**: Christian Simon (Prof. Schöneberg lab) works on NMJ failure in SMA. LG3 modulator = direct collaboration-relevant payload.
4. **First-in-class**: no reported small-molecule AGRIN-LRP4-interface drug. Major pharma white space.

## Compute

- **Instance**: ssh4:10540 (A100 PCIE 40GB, Japan)
- **Warm state**: PocketXMol at `/workspace/PocketXMol` (SHA `65488cf635c856101dbe703ac97e2f10f58e005c`), weights cached, base conda env with torch 2.4.1+cu124, torch_geometric 2.7.0, rdkit ready.
- **n_molecules**: 600 (match PocketXMol campaign batch size)
- **batch_size**: 50
- **Smoke**: 5-mol first
- **tmux**: `pxm_agrin_lg3`
- **GPU util target**: > 60%

## Post-generation pipeline

1. RDKit sanity + QED/Lipinski filter
2. BBB tag-only (peripheral NMJ; no hardfilter — skeletal muscle synapse is peripheral)
3. Top 100 → Boltz-2 panel (localhost:8004):
   - Primary: AGRIN LG3 (O00468)
   - Counter-screens: LRP4 (O75096) — we want AGRIN-binder not LRP4-binder
   - Negative controls: irrelevant LG domains (LAMA2, LAMB1)
4. Z-score selectivity: `z_AGRIN > 0` gate
5. DRAFT stays DRAFT until triple_llm_verify 3/3 PASS
6. Cross-reference vs Simon lab data once available

## Risks / honest caveats

- **Interface is flat (15.8×6.7×6.1Å)** — canonical protein-protein interface, hard to drug small-molecule. Expected hit rate lower than kinase-ATP-pocket campaigns.
- **Loop-surface pocket** — not a deep cleft; generator must find buried sub-pockets. PocketXMol reference generation may help.
- **Rat AGRIN crystal** — 95% identical to human in LG3 but NOT 100%. Any lead will need human AGRIN re-dock.
- **No native ligand to set C_rel baseline** — Z-score across AGRIN vs LRP4 is the primary selectivity metric.
- **Direction ambiguity**: AGRIN-potentiator is the goal but generative chemistry could yield AGRIN-blocker (competitive AGRIN-mimetic). Downstream assay will differentiate.
- **Allosteric vs competitive** — cannot predict from structure alone which mode a given hit operates by. Molecular-level insight from Boltz-2 pose + SMA lab validation required.

## File layout

- Plan: `/home/bryza/sma-research/qms/agrin_lg3_modulator_plan.md` (this file)
- Pocket script: `/home/bryza/gpu-fleet/scripts/agrin_lg3_pocket.py` (also at `/opt/agrin_lg3_pocket.py` on instance)
- Pocket JSON (on A100): `/results/pocketxmol/agrin_lg3_modulator/pocket_audit.json`
- Task JSON: `/home/bryza/sma-research/qms/agrin_lg3_modulator_task.json`
- Results (on A100): `/results/pocketxmol/agrin_lg3_modulator/`
- Local results: `/home/bryza/fleet-results/agrin_lg3_modulator/`
- RESULTS doc: `/home/bryza/sma-research/qms/agrin_lg3_modulator_RESULTS.md` (DRAFT)

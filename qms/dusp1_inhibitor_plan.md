# DUSP1 PocketXMol Inhibitor Campaign — Plan

**Campaign ID**: `dusp1_inhibitor`
**Instance**: A100 SXM4-40GB, Slovenia, contract 35120543 (ssh2:10542)
**Launched**: 2026-04-17
**Status**: DRAFT (pending triple_llm_verify 3/3 PASS)

## Target

- **Protein**: DUSP1 / MKP-1 — dual-specificity MAP kinase phosphatase 1
- **UniProt**: P28562 (human)
- **Structure source**: **AlphaFold2 monomer v6** (`AF-P28562-F1-model_v6`, 2025-08-01 release).
  No crystal structure of full-length human DUSP1 exists (UniProt/RCSB verified
  via API — closest is DUSP6/MKP-3 (1MKP), used today for sister campaign).
- **Source TITLE (verified)**: `ALPHAFOLD MONOMER V2.0 PREDICTION FOR DUAL SPECIFICITY PROTEIN PHOSPHATASE 1 (P28562)`
- **Global pLDDT**: 79.2 (high-confidence overall)
- **Catalytic pocket pLDDT**: 97.3 (Cys258) / 98.6 (Arg264) — both very-high confidence
- **Organism**: *Homo sapiens* (taxid 9606)
- **Construct**: full-length 367 residues (AF2 single-chain)

## Catalytic pocket derivation

DUSP1 uses the dual-specificity phosphatase (DSP) fold. Signature motif is
`CX5R` (catalytic cysteine + P-loop arginine 5 residues downstream, wrapping
back in 3D).

**Critical learning from DUSP6 agent earlier today** (see
`dusp6_inhibitor_plan.md`): DSP motif is identified by **3D adjacency, NOT
sequence scan**. For DUSP6 the canonical Cys287-Arg293 pair was disrupted by
a loop — actual catalytic pair was Cys287-Arg283 (3D-adjacent, reversed
direction). Our script uses CA-CA < 8 A + +5..+10 downstream preference to
identify the true pair.

**DUSP1 catalytic pair (identified by 3D adjacency):**
```
Cys258 (CA) — Arg264 (CA) = 6.11 A   [within 8 A threshold]
DSP motif window 256-267: "FVHCQAGISRSA"
- C at 258 → catalytic Cys (nucleophile)
- R at 264 → P-loop Arg (+6, 3D adjacent)
- Classical CX5R: 258-263 = "CQAGIS" (5 residues between C and R, then R at 264) ✓
```

Both residues have pLDDT > 97 (very-high AF2 confidence). Unlike DUSP6 this
IS a clean sequence-motif match as well as 3D match.

**Pocket center** (mean CA of 16 residues within 8 A of Cys258.SG):
```
pocket_center = [5.203, 0.802, -17.015]
pocket_residues (16): GLY184, SER185, ALA186, VAL206, SER207, ASP227, HIS257,
                      CYS258, GLN259, ALA260, GLY261, ILE262, SER263, ARG264,
                      SER265, ALA266
```

Effective generator radius: **10 A** (standard for SBDD, same as DUSP6).

## Rationale (SMA)

1. **DUSP1 inactivates multiple MAPK substrates** (ERK, JNK, p38).
   In SMA motor neurons, MAPK stress/survival signalling is dysregulated
   (multiple datasets).
2. **Sister rationale to DUSP6** (our campaign earlier today): both are
   MAPK-dephosphorylating phosphatases, but DUSP1 acts on JNK + p38 in
   addition to ERK, while DUSP6 is ERK-selective. Inhibiting DUSP1 prolongs
   **all three** MAPK pro-survival arms, including JNK (axonal stress
   response) and p38 (inflammation/regeneration).
3. **Panel extension**: DUSP1 + DUSP6 hits allow within-DSP selectivity
   mapping. DUSP1-selective vs DUSP6-selective vs pan-DSP hits characterize
   substrate-channel preferences.
4. **Direction UNRESOLVED**: Like DUSP6, the direction of DUSP1 activity
   (inhibit vs activate) for SMA MN rescue requires meta-analysis. This
   campaign is **exploratory compute**, not a therapy claim.

## Compute

- **Instance**: ssh2:10542 (A100 SXM4 40GB), Slovenia, $0.69/hr
- **Warm state**: PocketXMol at `/opt/PocketXMol`, conda env `pxm_cu128`,
  weights cached, deploy script at `/opt/pocketxmol_deploy.py`
- **n_molecules**: 600 (match DUSP6 + CDK5 + LIMK2-ATP batch size)
- **batch_size**: 50 (A100 SXM4 headroom)
- **Smoke test**: 5 molecules in 14 sec. Succ/Incomp/Bad = 1/4/0. **PASS**.
- **tmux**: `pxm_dusp1`
- **GPU util target**: > 60 %

## Post-generation pipeline

1. BBB hardfilter drop (MW < 500, HBD ≤ 3, HBA ≤ 7, PSA < 90 Å², logP 1–4)
2. QED/Lipinski filter
3. Top 100 → Boltz-2 panel vs DUSP1 + DUSP6 + SSH1 + SSH2 + SSH3 (5-phosphatase selectivity)
4. Z-score selectivity: `z_DUSP1 > 0` AND `z_DUSP1 > z_DUSP6` for DUSP1-selective
5. DRAFT stays DRAFT until triple_llm_verify 3/3 PASS

## Risks / honest caveats

- **AF2 model, not crystal** — no experimental structure of full-length DUSP1.
  Catalytic pocket region has pLDDT > 97 so AF2 local geometry is reliable,
  but substrate-bound conformation may differ. Historic DUSP1 inhibitors are
  few; activity-based screens use substrate analogues.
- **DSP fold is flat** — shallow active sites notoriously hard to drug.
  Expect low hit rate at direct active-site generation.
- **No covalent warhead** — Cys258 is normally targeted covalently; our
  molecules will be non-covalent. Affinity ceiling limited vs tool compounds.
- **Close DUSP paralogues not in panel** — DUSP4/5/6/7 are ≥40% identical to
  DUSP1 in the catalytic domain. Within-DUSP selectivity requires adding
  DUSP4/5/7 to the Boltz-2 panel in a downstream campaign.
- **Direction unresolved for SMA** — inhibit vs activate is meta-analysis
  blocker. Not to be surfaced until approved.

## File layout

- Plan: `/home/bryza/sma-research/qms/dusp1_inhibitor_plan.md` (this file)
- Task JSON: `/home/bryza/sma-research/qms/dusp1_inhibitor_task.json`
- Pocket derivation script (on A100): `/results/dusp1_inhibitor/dusp1_pocket.py`
- Pocket audit JSON (on A100): `/results/dusp1_inhibitor/pocket_audit.json`
- Results (on A100): `/results/dusp1_inhibitor/full_output/`
- RESULTS doc: `/home/bryza/sma-research/qms/dusp1_inhibitor_RESULTS.md` (DRAFT)

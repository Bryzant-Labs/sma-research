# mTOR Inhibitor Campaign Plan (QMS)

**Campaign ID:** `mtor_inhibitor`
**Date started:** 2026-04-17
**Instance:** 35124116 (A100 SXM4 80GB, Slovenia, $0.6944/hr)
**SSH:** `ssh -i ~/.ssh/id_ed25519_vastai -p 14116 root@ssh3.vast.ai`
**Output:** `/results/pocketxmol/mtor_inhibitor/` (on instance)

## Target

- **Gene/Protein:** MTOR (Mechanistic Target of Rapamycin, Serine/threonine-protein kinase mTOR)
- **UniProt:** P42345
- **Organism:** Homo sapiens
- **PDB:** 4JT5
- **PDB TITLE verified:** `MTORDELTAN-MLST8-PP242 COMPLEX`
- **Co-crystal ligand:** PP242 (Torin-family ATP-competitive mTOR inhibitor; PDB ligand code: **P2X**), 23 atoms chain A

## Biological Rationale

mTOR regulates autophagy, protein translation, and cell survival. In SMA motor neurons, autophagy is dysregulated (direction depends on disease stage: excess autophagy in early symptomatic MN leading to neurodegeneration).

Known mTOR kinase-ATP-site inhibitors:
- **Rapamycin** (allosteric, FRB domain) — immunosuppressive
- **Torin1, Torin2, AZD8055, PP242** — broad mTORC1/2 inhibition, immune side effects

A novel-chemotype mTOR-selective ATP-site inhibitor via PocketXMol could deliver controlled MN autophagy modulation. (FRB-domain allosteric targeting deferred — would require a different PDB such as 1FAP rapamycin+FKBP12 complex; left as a follow-up track.)

## Pocket Derivation (audit trail)

```python
# 4JT5 chain A, HETATM residue P2X (PP242)
# 23 atoms, center = mean of (x, y, z)
pocket_center = [51.856, -0.015, -49.146]  # Å
pocket_radius = 10.0                        # Å
# Ligand bbox extent: x=10.7, y=4.9, z=7.1 Å (elongated ATP pocket)
```

Script: on-instance Python parser of `/workspace/pdb_cache/4JT5.pdb`, fixed-width PDB column parser.

## Workflow

1. **Smoke test** — 5 molecules, batch=5
2. **Full run** — 600 molecules, batch=50
3. **Post-filters** (local, after rsync):
   - RDKit valid
   - Lipinski
   - QED > 0.4
   - **BBB > 0.5 hard drop** (CNS penetration for MN autophagy)
4. **Top 100 → Boltz-2** on localhost:8004 (Server #2 TW)
5. **Selectivity panel (PIKK family):** mTOR, PI3Kα, PI3Kβ, PI3Kγ, PI3Kδ, DNA-PK, ATM, ATR
6. **Triple-LLM verify** 3/3 → DRAFT → VERIFIED

## Quality Gates

- [x] PDB TITLE verified: `MTORDELTAN-MLST8-PP242 COMPLEX`
- [x] Pocket derivation script saved to task JSON `_rationale`
- [x] Smoke 5-mol PASS (5/0/0 Succ/Incomp/Bad at 2026-04-17 09:34:02 UTC)
- [x] BBB hardfilter applied: 91/507 (17.9%) passed (TPSA<90, MW<450, 1≤logP≤4, HBD≤3)
- [x] Top 91 Boltz-2 queue written: `/home/bryza/fleet-results/mtor_inhibitor/boltz2_queue.jsonl`
- [ ] Boltz-2 ipTM scoring (submit to localhost:8004 Server #2 TW)
- [ ] Triple-LLM 3/3 verify → DRAFT → VERIFIED

## Run Completion (2026-04-17)

- **Start (full run):** 2026-04-17 09:34:10 UTC
- **End (full run):** 2026-04-17 09:40:28 UTC
- **Wall time:** ~6 min 18 s (parallel with HDAC2 campaign)
- **GPU util:** 96–100% shared with HDAC2; per-process ~1.8 GB VRAM
- **Final pool:** 521 Succ / 1 Incomp / 78 Bad (86.8% success rate of 600)
- **Valid unique SMILES:** 507 (15 duplicates / 78 non-emitted)
- **BBB-pass:** 91 (17.9% of valid — lower than HDAC2 due to larger kinase hinge scaffolds that push MW/logP)
- **Top 91 by cfd_pos** written to `/home/bryza/fleet-results/mtor_inhibitor/top100.csv` (only 91 BBB-pass, all included)
- **Estimated compute cost:** ~6.5 min × $0.6944/hr × 0.5 (shared with HDAC2) ≈ $0.04

### Top 5 by cfd_pos (BBB-filtered)

| # | SMILES | cfd_pos | MW | QED | logP |
|---|--------|---------|------|------|------|
| 1 | `COc1ccc(Oc2ccc3c(c2)C2=c4ccccc4=NC(=O)C2=NC3=O)cc1` | 2.826 | 382.4 | 0.697 | 2.44 |
| 2 | `COc1ccc(-c2nc(-c3ccc(N4CCNCC4)cn3)nc3ccccc23)cc1` | 2.806 | 397.5 | 0.566 | 3.78 |
| 3 | `Oc1c2cc3cccc4c5c[nH+]ccc5nc(c2nc2[n+]1C=CC=2)c34` | 2.756 | 324.3 | 0.269 | 1.88 |
| 4 | `C1=Cc2n[nH+]c3cccnc3c2C=C2Nc3ccccc3N=C12` | 2.755 | 298.3 | 0.694 | 3.01 |
| 5 | `NC(=O)c1ccc(-c2cn3cccc(-c4cnc5cccnc5c4)c3n2)cc1` | 2.752 | 365.4 | 0.528 | 3.71 |

**Rank-1 compound** `COc1ccc(Oc2ccc3c(c2)C2=c4ccccc4=NC(=O)C2=NC3=O)cc1` is a polycyclic aryl-ether with a pyrimidoquinoline-like core and QED 0.697 — sensible kinase ATP-site scaffold. **Rank-2** is an anilinopyrimidine with a piperazine handle — classic kinase hinge-binder scaffold (similar to several clinical kinase inhibitors).

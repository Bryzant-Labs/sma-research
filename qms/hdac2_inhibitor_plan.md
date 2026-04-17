# HDAC2 Inhibitor Campaign Plan (QMS)

**Campaign ID:** `hdac2_inhibitor`
**Date started:** 2026-04-17
**Instance:** 35124116 (A100 SXM4 80GB, Slovenia, $0.6944/hr)
**SSH:** `ssh -i ~/.ssh/id_ed25519_vastai -p 14116 root@ssh3.vast.ai`
**Output:** `/results/pocketxmol/hdac2_inhibitor/` (on instance)

## Target

- **Gene/Protein:** HDAC2 (Histone Deacetylase 2)
- **UniProt:** Q92769
- **Organism:** Homo sapiens
- **PDB:** 4LXZ
- **PDB TITLE verified:** `STRUCTURE OF HUMAN HDAC2 IN COMPLEX WITH SAHA (VORINOSTAT)`
- **Co-crystal ligand:** SAHA / vorinostat (PDB ligand code: **SHH**), 19 atoms chain A
- **Catalytic cofactor:** Zn2+ at [19.284, -18.126, -2.875] (chain A), 7.5 Å from pocket center → within 10 Å sphere

## Biological Rationale

HDAC inhibition relaxes SMN2 promoter chromatin → increases SMN2 expression in SMA motor neurons.
Proof-of-concept: **Trichostatin A (TSA)** + **sodium valproate** demonstrated the SMN2-upregulation axis in vitro and in mouse models, but failed in clinical trials due to off-target toxicity (pan-HDAC activity, hepatotoxicity, neurotoxicity).

A novel-chemotype **HDAC2-selective** inhibitor (vs HDAC1 / HDAC3 / HDAC8 / HDAC6) via PocketXMol pocket-aware generation could deliver SMN2 upregulation with a cleaner safety profile.

## Pocket Derivation (audit trail)

```python
# 4LXZ chain A, HETATM residue SHH (SAHA)
# 19 atoms, center = mean of (x, y, z)
pocket_center = [25.710, -15.817, 1.122]   # Å
pocket_radius = 10.0                        # Å
# Catalytic Zn2+ included within sphere (7.5 Å from center)
# Ligand bbox extent: x=8.9, y=8.2, z=7.6 Å (compact pocket)
```

Script: on-instance Python parser of `/workspace/pdb_cache/4LXZ.pdb`, fixed-width PDB column parser (cols 17–20 = resname, 21 = chain, 30–54 = x/y/z).

## Workflow

1. **Smoke test** — 5 molecules, batch=5, expect ~30 s wall time.
2. **Full run** — 600 molecules, batch=50, expect ~12 × 30 s batches ≈ 6–8 min on A100.
3. **Post-filters** (local, after rsync):
   - RDKit valid
   - Lipinski (MW, HBD, HBA, LogP)
   - QED > 0.4
   - **BBB > 0.5 hard drop** (CNS penetration required for motor neurons)
4. **Top 100 → Boltz-2** on localhost:8004 (Server #2 TW) for ipTM binding
5. **Selectivity panel:** HDAC1, HDAC2, HDAC3, HDAC8 (class I) + HDAC6 (class II off-target for zinc-hydroxamate)
6. **Triple-LLM verify** 3/3 → DRAFT → VERIFIED

## Quality Gates

- [x] PDB TITLE verified: `STRUCTURE OF HUMAN HDAC2 IN COMPLEX WITH SAHA (VORINOSTAT)`
- [x] Pocket derivation script saved to task JSON `_rationale`
- [x] Smoke 5-mol PASS (5/0/0 Succ/Incomp/Bad at 2026-04-17 09:34:02 UTC)
- [x] BBB hardfilter applied: 148/577 (25.6%) passed (TPSA<90, MW<450, 1≤logP≤4, HBD≤3)
- [x] Top 100 Boltz-2 queue written: `/home/bryza/fleet-results/hdac2_inhibitor/boltz2_queue.jsonl`
- [ ] Boltz-2 ipTM scoring (submit to localhost:8004 Server #2 TW)
- [ ] Triple-LLM 3/3 verify → DRAFT → VERIFIED

## Run Completion (2026-04-17)

- **Start (full run):** 2026-04-17 09:34:10 UTC
- **End (full run):** 2026-04-17 09:40:31 UTC
- **Wall time:** ~6 min 21 s (parallel with mTOR campaign)
- **GPU util:** 96–100% shared with mTOR; per-process ~1.8 GB VRAM
- **Final pool:** 565 Succ / 13 Incomp / 22 Bad (94.2% success rate of 600)
- **Valid unique SMILES:** 577 (1 duplicate / 22 non-emitted)
- **BBB-pass:** 148 (25.6% of valid)
- **Top 100 by cfd_pos** written to `/home/bryza/fleet-results/hdac2_inhibitor/top100.csv`
- **Estimated compute cost:** ~6.5 min × $0.6944/hr × 0.5 (shared with mTOR) ≈ $0.04

### Top 5 by cfd_pos (BBB-filtered)

| # | SMILES | cfd_pos | MW | QED | logP |
|---|--------|---------|------|------|------|
| 1 | `c1ccc(C2=Nc3ccccc3N=C(c3ccc4ncc[nH+]c4c3)N2)cc1` | 2.890 | 350.4 | 0.597 | 3.81 |
| 2 | `Cc1ccccc1CCNC1=Nc2ccccc2N=C(c2ccc[nH+]c2)N1` | 2.875 | 356.5 | 0.753 | 3.31 |
| 3 | `O=C(c1ccc(-c2ccccc2)nc1)N1CCN(c2cnc3ccccc3n2)CC1` | 2.854 | 395.5 | 0.530 | 3.65 |
| 4 | `CCCN(Cc1ccccc1)C(C(=O)NCc1ccccc1)c1cnccn1` | 2.853 | 374.5 | 0.620 | 3.75 |
| 5 | `c1ccc(-n2c(NCc3cccnc3)nc3nc4ccccc4nc32)cc1` | 2.850 | 352.4 | 0.530 | 3.98 |

**Caveat**: None of the top-5 contain a hydroxamic acid or ortho-aminoanilide zinc-chelating headgroup (the classical HDAC pharmacophore). PocketXMol produced aromatic/heteroaromatic scaffolds without the specific Zn2+-coordinating warhead. This is a known limitation of pure geometric pocket-aware generation when the catalytic Zn is stripped from the input PDB (HETATM removal). Next iteration should: (a) keep ZN in the protein PDB, or (b) use LIMKi3-style ligand-guided PocketXMol with SAHA as reference.

# PERP De Novo Protein Binder Design — Pre-Flight Plan

**Status**: DRAFT (pre-compute)
**Date**: 2026-04-17
**Target**: PERP (UniProt Q96FX8), 193 aa tetraspan TM protein, TMEM47 family
**Instance**: Vast H100 SXM Japan, contract 35120552, SSH `ssh -i ~/.ssh/id_ed25519_vastai -p 10552 root@ssh8.vast.ai`
**Motivation**: ECL pockets on PERP show fpocket druggability < 0.05 (today's finding from H100-ssh8 vscreen) — small molecules cannot access extracellular surfaces. De-novo protein binder design is the tractable path for Simon's NMJ-role research line.

## Target topology (from UniProt Q96FX8)
- TM1: residues 12-32
- TM2: residues 79-99
- TM3: residues 110-130
- TM4: residues 151-171
- **ECL1 (target A)**: residues 33-78 (46-residue loop, between TM1-TM2)
- **ECL2 (target B)**: residues 131-150 (20-residue loop, between TM3-TM4)
- AF2 v6 source: https://alphafold.ebi.ac.uk/files/AF-Q96FX8-F1-model_v6.pdb

## Campaigns

### Campaign A — ECL1 binder design (long extracellular loop)
- Hotspot triplets (preliminary; refine with SASA check on AF2 model):
  - H1a: 40, 44, 48 (N-terminal third of ECL1)
  - H1b: 50, 54, 58 (center, highest solvent accessibility expected)
  - H1c: 60, 64, 68 (C-terminal third)
  - H1d: 45, 52, 59 (wide-spaced flat epitope)
  - H1e: 48, 55, 62 (symmetric around center)
- Binder length range: 70-100 aa
- Contigs template: `[A1-193/0 70-100]`, `hotspot_res=["A<h>", "A<h+4>", "A<h+8>"]` per triplet
- Backbones: 50 per hotspot triplet × 5 triplets = **250 designs**

### Campaign B — ECL2 binder design (short extracellular loop)
- Hotspot triplets:
  - H2a: 135, 139, 143
  - H2b: 138, 142, 146
  - H2c: 136, 141, 146
- Binder length range: 60-90 aa
- Backbones: 50 × 3 = **150 designs**

Combined: ~400 RFdiffusion backbones.

## Validation cascade

| Stage | Tool | Pass gate |
|---|---|---|
| 1 | RFdiffusion | No explicit filter (all backbones pass to stage 2) |
| 2 | ProteinMPNN (hosted NIM) | 8 seq/backbone, temperature 0.1; drop if >2 non-disulfide Cys or >40% hydrophobic |
| 3 | ESMfold monomer | pLDDT > 70 |
| 4 | Boltz-2 PPI co-fold (sma-h100-two:8003 batched) | delta_iptm = iptm_target − iptm_scrambled > 0.1 |

Scrambled control: same amino acid composition, random.shuffle with fixed seed per design (reproducible).

## Abort triggers
- 3 consecutive RFdiffusion job failures → stop and diagnose (contigs / chain / residue range)
- First 50 backbones across hotspots all yield ESMfold pLDDT < 70 → bad topology; surface before burning remaining 350
- Boltz-2 server health check fails → pause; send diagnostic before restart

## Output artifacts
- `/results/perp_binder_design/PERP_AF.pdb`
- `/results/perp_binder_design/ecl1/rfdiff/*.pdb`
- `/results/perp_binder_design/ecl2/rfdiff/*.pdb`
- `/results/perp_binder_design/top_binders_ecl1.tsv`
- `/results/perp_binder_design/top_binders_ecl2.tsv` — columns: design_id, sequence, length, pLDDT, iptm_target, iptm_scrambled, delta_iptm, rank
- `/home/bryza/sma-research/qms/PERP_binder_design_RESULTS.md` (DRAFT)

## Quality gates (HARD)
- Chain/residue verification BEFORE writing contigs
- Each numeric claim DRAFT until triple_llm_verify.py 3/3 PASS
- No push to public repo
- No external comms (QMS comms gate holds)

## Budget
- 6 h wall-clock max combined
- ETA per stage: RFdiff 1-2 h, MPNN minutes (hosted NIM), ESMfold ~30 min, Boltz-2 ~1 h
- Burn: $1.73/hr × 6 = ~$10.40

## Git SHA at plan draft
Pending — commit with `git log -1 --format=%H` on /home/bryza/sma-research/qms/ after write.

## Success criteria
- GPU utilization > 60% sustained during RFdiff + Boltz-2 phases
- ≥ 20 backbones per ECL with ESMfold pLDDT > 70
- ≥ 3 binders per ECL with delta_iptm > 0.1
- Triple-LLM verify 3/3 PASS on RESULTS.md

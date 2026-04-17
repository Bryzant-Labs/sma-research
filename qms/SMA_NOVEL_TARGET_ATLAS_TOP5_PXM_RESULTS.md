# SMA Novel Target Atlas — Top-5 PocketXMol Campaign Results

**Date**: 2026-04-17
**Campaign ID**: sma_novel_targets_2026
**Parent atlas**: `/home/bryza/sma-research/qms/SMA_NOVEL_TARGET_ATLAS_2026.md`
**Queue**: `/home/bryza/sma-research/qms/proteome_wide_2026/pocketxmol_campaign_queue.json`
**TITLE audit**: `/home/bryza/sma-research/qms/proteome_wide_2026/TITLE_AUDIT.md`
**GPU**: Vast instance 35124116 (A100 SXM4 40GB @ $0.69/hr, label `sma-replacement-jak2-20260417`, attach-mode reuse)
**Wall-clock**: 30 min end-to-end for 3,000 molecules × 5 targets
**Marginal cost**: ~$0.35 (30 min × $0.69/hr; instance was already rented for prior JAK2 campaign)
**Status**: DRAFT — INTERNAL ONLY. Simon-Comms-Gate HELD.

## TITLE Audit Findings

Of 5 originally claimed PDB IDs in the queue, **3 were mis-assigned** and required correction:

| Target | Queue PDB | Audit verdict | Corrected PDB |
|--------|-----------|---------------|---------------|
| PCIF1 | 7VS2 | FAIL (fungal effector MoERS1) | 6IRV (human PCIF1, Q9H4Z3) |
| BPTF | 3UV2 | PASS (BPTF bromodomain, Q12830) | 3UV2 kept |
| LARP1 | 5V87 | PASS (LARP1 DM15 + m7GpppC, Q6PKG0) | 5V87 kept |
| SH3BP5 | 1OEB | FAIL (mouse MONA/GADS) | 6IXG (native apo SH3BP5, O60239) |
| KAT6B | 6LIM | FAIL (BRD4-BD1 bromodomain) | 8DD5 (KAT6A paralog MYST HAT + PF-9363; no Q8WYB5 MYST PDB exists) |

All 5 targets proceeded after correction. No target skipped.

## Per-target Generation Statistics

| Target | PDB | n_generated | RDKit valid | Lipinski pass | BBB pass (≥0.5) | both pass |
|--------|-----|-------------|-------------|---------------|-----------------|-----------|
| PCIF1 | 6IRV | 482/600 | 480 (99.6%) | 408 | 190 | 190 |
| BPTF | 3UV2 | 566/600 | 566 (100.0%) | 391 | 333 | 333 |
| LARP1 | 5V87 | 535/600 | 514 (96.1%) | 249 | 116 | 116 |
| SH3BP5 | 6IXG | 510/600 | 510 (100.0%) | 407 | 305 | 305 |
| KAT6B | 8DD5 | 476/600 | 469 (98.5%) | 357 | 194 | 194 |

**Aggregate**: 5/5 campaigns completed. Average RDKit validity ~99%, average Lipinski-pass ~67%, average BBB-pass ~38%. Much higher quality than prior NIM GenMol runs (drift of 40-70% invalid), consistent with PocketXMol's pocket-aware 3D generation.

## Top-10 Hits per Target (ranked by PocketXMol cfd_pos ASC = lower = higher positional denoising confidence)

All rows are Lipinski-valid. Columns: rank, SMILES, cfd_pos, QED, MW, logP, TPSA, BBB-prob.

### PCIF1 — PCIF1 (human Q9H4Z3) cap-specific m6A methyltransferase SAM-binding pocket

| # | SMILES | cfd_pos | QED | MW | logP | TPSA | BBB |
|---|--------|---------|-----|-----|------|------|-----|
| 1 | `O=C1CCC2CC(C3CCC(c4ccncn4)=CC3O)C2NC(=O)C1O` | 1.4633876085281372 | 0.664 | 357.41 | 0.48 | 112.41 | 0.495 |
| 2 | `Cc1cc2c(cn1)C(COC(=O)C1CNC(c3ccnnc3)=NC1=O)NC2=O` | 1.6366409063339231 | 0.545 | 380.36 | -0.3 | 135.53 | 0.116 |
| 3 | `CCC(=O)Nc1ccc2nnnc(ON=C3OCC4=C3OCC4CO)c2c1` | 1.686466097831726 | 0.745 | 371.35 | 0.99 | 128.05 | 0.364 |
| 4 | `O=c1[nH]c2c3c(ccc(O)cc1-3)CN2C(O)C(O)=NN=Cc1cncnc1` | 1.6940864324569702 | 0.3 | 366.34 | 0.6 | 147.29 | 0.025 |
| 5 | `O=C1OC(C(O)O)C(O)N2c3ncccc3-c3ccc(O)cc3C12` | 1.7176954 | 0.421 | 330.3 | -0.13 | 123.35 | 0.162 |
| 6 | `O=C1C(=Nc2ccccc2)C2CCCC(O)C3NC(=O)C(C1NO)C23` | 1.731744647026062 | 0.587 | 343.38 | 0.58 | 111.02 | 0.361 |
| 7 | `Cc1ccc2c(c1)C=C(O)C(O)=CC(Nc1ccc(C(=O)O)cc1)=C2` | 1.7664493322372437 | 0.663 | 335.36 | 4.5 | 89.79 | 0.4 |
| 8 | `O=C(C1NNC2=C3NON=C3C=CC=C2N1)[n+]1c[n+]2cncnc2cc1O` | 1.77666175365448 | 0.344 | 367.33 | -2.57 | 140.77 | 0.0 |
| 9 | `CC(=O)NC1=CC2=NC=CNC2=CC=C1C(O)=[N+]1CCNC2C(C)OC2C1` | 1.7791391611099243 | 0.408 | 370.43 | 0.07 | 97.99 | 0.364 |
| 10 | `Nc1nccc(Oc2cccc(ON=C3CCC(=O)N=C(O)C3O)c2)n1` | 1.7963378429412842 | 0.691 | 357.33 | 1.22 | 152.51 | 0.0 |

### BPTF — BPTF (human Q12830) bromodomain acetyl-lysine pocket

| # | SMILES | cfd_pos | QED | MW | logP | TPSA | BBB |
|---|--------|---------|-----|-----|------|------|-----|
| 1 | `c1ccc2[nH]c3cccc4ccc5[n+](c6c(nc(c1)-c26)-c1cc[nH]c1CN5)c43` | 2.2176029682159424 | 0.349 | 362.42 | 4.48 | 60.6 | 0.608 |
| 2 | `CC1CN2Cc3cc4c(cccc4cc3O)C(=O)c3cc(cs3)C(O)=NCCC1C2` | 2.340275526046753 | 0.557 | 420.53 | 4.61 | 73.13 | 0.554 |
| 3 | `O=C1c2cncc(c2)NC(c2cccs2)Cc2[nH]ncc2Cc2ccccc21` | 2.345348834991455 | 0.509 | 386.48 | 4.4 | 70.67 | 0.641 |
| 4 | `CC1=CC2=CC(=C(O)N1)C(=O)N(C)c1nnc3[nH]nc(n13)-c1cccc(c1)C...` | 2.3556087017059326 | 0.533 | 401.43 | 2.4 | 111.44 | 0.643 |
| 5 | `Cc1cc2c3c4cccccc4n4cc5c(N(C)C)ccccc5c(c(=O)n2n1)c34` | 2.3636393547058105 | 0.404 | 392.46 | 4.78 | 42.02 | 0.488 |
| 6 | `CN1CC2=CC=C(N)N=C(N2)c2cccc(c2)OCC2CCCC2C1` | 2.366896152496338 | 0.763 | 338.46 | 2.46 | 62.88 | 1.0 |
| 7 | `C=C(c1ccco1)C(C)Nc1cc2ccc3c(c2nc1C)OC(C)CN(C)C3=O` | 2.368975 | 0.709 | 391.47 | 4.5 | 67.6 | 0.599 |
| 8 | `Cn1nc2c(cc3oc4c(O)cccc4c4cc5c(O)ccc2c5c34)c1=O` | 2.40710186958313 | 0.43 | 356.34 | 3.99 | 88.49 | 0.805 |
| 9 | `O=C1N=C2C3=CC=CC=C2NC2CCCN(C2)C(O)c2cccc(c2)CCN1C=N3` | 2.4144625663757324 | 0.698 | 403.49 | 2.53 | 80.53 | 1.0 |
| 10 | `O=c1c2ccccc2c2ccc3c(=O)cc[nH]c3c2c2ccc(O)cc12` | 2.4182794094085693 | 0.447 | 339.35 | 4.05 | 70.16 | 0.779 |

### LARP1 — LARP1 (human Q6PKG0) DM15 cap-binding pocket

| # | SMILES | cfd_pos | QED | MW | logP | TPSA | BBB |
|---|--------|---------|-----|-----|------|------|-----|
| 1 | `CC1C=CC(C(=O)O)CC2=CNC(=O)C2=C2C=C3C(CCCC(O)C3C2)C1` | 1.939261794090271 | 0.62 | 369.46 | 3.09 | 86.63 | 1.0 |
| 2 | `Cc1cccc2c(=O)n3[nH]c4c(F)cccc4c(=O)c4nc5ncc(c12)c5c43` | 2.1956474781036377 | 0.445 | 370.34 | 3.28 | 80.12 | 1.0 |
| 3 | `CC(C)(O)CC1=CC(=O)C2=C(N)C=[N+]3C2=C1CCC31C2CNC3CN1CC3C2` | 2.228907823562622 | 0.612 | 381.5 | 0.63 | 81.6 | 0.854 |
| 4 | `c1ccc2nc3cnc4c5cnc6c7ccccc7nc(ncc(nc2c1)c34)nc56` | 2.237030506134033 | 0.383 | 385.39 | 4.37 | 90.23 | 0.649 |
| 5 | `CC(O)(COP(=O)(O)O)C1OOC1Cn1ccnc2c(=O)nc(N)nc1-2` | 2.277905464172364 | 0.323 | 389.26 | -1.72 | 192.14 | 0.0 |
| 6 | `Cc1ccc2c(Cc3cc(=O)n4c5ccoc5c5cccc3c54)c(=O)n(CCO)c-2cc1` | 2.2841053009033203 | 0.467 | 424.46 | 3.79 | 76.85 | 0.882 |
| 7 | `C=C1CC(C)(C)Nc2ccc(C(NC(=O)C3C(=O)NC(O)C3C)C(=O)O)cc21` | 2.289513349533081 | 0.495 | 387.44 | 1.24 | 127.76 | 0.124 |
| 8 | `CC1=CC=C(C)C2=CN=c3c(c(=O)[nH]c(=O)n3CC(C)COP(=O)(O)O)=[N...` | 2.296257734298706 | 0.416 | 421.37 | -1.71 | 147.95 | 0.0 |
| 9 | `NC1=NC(=O)C2=CN(C3OC(COP(=O)(O)OP(=O)(O)O)C3O)C2=N1` | 2.2988202571868896 | 0.3 | 398.16 | -2.25 | 213.8 | 0.0 |
| 10 | `C=C1CN(CO)Cc2cc(ccc2O)C(O)N2C=C(CC(OC)=CC2)NC1=O` | 2.305076360702514 | 0.559 | 387.44 | 0.9 | 105.5 | 0.474 |

### SH3BP5 — SH3BP5/SAB (human O60239) JNK-docking face pocket

| # | SMILES | cfd_pos | QED | MW | logP | TPSA | BBB |
|---|--------|---------|-----|-----|------|------|-----|
| 1 | `CC1=CC=C(C)C2C(=CCCCCCCC(N)C(=O)O)CC=C2C1O` | 1.9654247 | 0.46 | 345.48 | 3.88 | 83.55 | 0.849 |
| 2 | `OCCCCC1OC(O)COC(Oc2ccc3ccccc3c2)C1O` | 2.0330543518066406 | 0.69 | 348.4 | 1.8 | 88.38 | 1.0 |
| 3 | `O=C1C2=NC=CC3=C(NCNC4CCCC34)C2C(=O)c2ccccc21` | 2.0700765 | 0.764 | 333.39 | 2.22 | 70.56 | 1.0 |
| 4 | `COC1CC(C2=CC=c3c2cn2cncc32)CC1=C(O)c1ccc(N)cc1` | 2.121042966842652 | 0.556 | 359.43 | 3.21 | 72.78 | 1.0 |
| 5 | `COC1CCCC(CC(C)N(C(C)=O)c2cc(C)c3c(c2)=[N+]2C=CC=C2N=3)C1` | 2.1347811222076416 | 0.738 | 380.51 | 2.82 | 44.91 | 1.0 |
| 6 | `O=c1c2c(Oc3ccccc3)ccc(O)cc-2c2cc(O)cc(O)c(O)c1-2` | 2.1616244316101074 | 0.431 | 362.34 | 3.87 | 107.22 | 0.405 |
| 7 | `O=C(NCC1CCNCC1)c1cc(-c2cccs2)n(CCC2CCCO2)n1` | 2.1677406 | 0.765 | 388.54 | 2.91 | 68.18 | 1.0 |
| 8 | `CN1C(=O)C(C)(NC(=CN2C=CC3=C(O)C=CC=CC32)C(=O)O)c2cccnc21` | 2.1745190620422363 | 0.672 | 392.42 | 1.92 | 106.0 | 0.733 |
| 9 | `COc1cc(O)cc(O)c1CC(C)NCC(CCC(=O)O)c1cccc(O)c1` | 2.195650815963745 | 0.424 | 389.45 | 2.98 | 119.25 | 0.171 |
| 10 | `CC(O)NC(C)(CCC(N)=O)CNC1CCCN(c2ccccc2)C1` | 2.1970925331115723 | 0.504 | 348.49 | 1.2 | 90.62 | 0.66 |

### KAT6B — KAT6B MYST HAT pocket (via KAT6A paralog Q92794 template)

| # | SMILES | cfd_pos | QED | MW | logP | TPSA | BBB |
|---|--------|---------|-----|-----|------|------|-----|
| 1 | `CC1C=C2CC=C(C3C=CCC(O)C3=O)C3NC(=O)OC3=C2CC=C1C(=O)O` | 2.034276247024536 | 0.63 | 383.4 | 2.16 | 112.93 | 0.618 |
| 2 | `O=C1CCC2N=NNC(=O)C(=Cc3ccccc3)CC(=O)OCCCCC2C1` | 2.204868793487549 | 0.593 | 383.45 | 3.41 | 97.19 | 0.88 |
| 3 | `Cc1ccc(C2CC(c3cccc4ccccc34)C2C(=O)O)c(C(=O)O)c1C(=O)O` | 2.204910516738892 | 0.577 | 404.42 | 4.52 | 111.9 | 0.377 |
| 4 | `CC1=C2C(C=Nc3ccccc3)C(=O)N=C3NOC(c4ccccc4C=C1)C32` | 2.2088215351104736 | 0.808 | 369.42 | 4.18 | 63.05 | 0.728 |
| 5 | `O=C(O)CC=C(CC=C(O)c1ccc(C(=O)O)o1)c1ccccc1O` | 2.2112908363342285 | 0.566 | 344.32 | 3.53 | 128.2 | 0.239 |
| 6 | `O=C1Nc2nonc2-c2c[nH]cc2CP(=O)(O)C=C1c1c[nH]c2ccccc12` | 2.217891931533813 | 0.365 | 395.32 | 3.31 | 136.9 | 0.146 |
| 7 | `O=C1OC(O)C2=CC=CC=C3N=NC=C(C(=O)C4=NCc5ccccc54)C1=C32` | 2.2285563945770264 | 0.807 | 371.35 | 2.46 | 100.68 | 0.822 |
| 8 | `Cc1c(N)ncnc1CCc1ccc(C(=O)O)c2c1OP(=O)(O)O[PH](O)(O)O2` | 2.250718832015991 | 0.432 | 433.25 | 1.13 | 194.55 | 0.0 |
| 9 | `O=C1COCCC2CC=C(O)C=C2c2c[nH]c(c2)C(c2cccc[nH+]2)CO1` | 2.2539632 | 0.759 | 367.43 | 2.77 | 85.69 | 1.0 |
| 10 | `Nc1nc[nH+]c2c1ncn2C(OP1(=O)OP(=O)(O)O1)C(O)C[n+]1ccccc1` | 2.255798578262329 | 0.355 | 430.25 | -0.05 | 177.04 | 0.0 |

## Pocket Centers & Rationale (verified)

| Target | PDB | Pocket center (x,y,z Å) | Radius (Å) | Source |
|--------|-----|--------------------------|------------|--------|
| PCIF1 | 6IRV | (-28.02, 11.49, -32.13) | 12.0 | NPPF catalytic motif Cα centroid (resi 553-557). Apo human structure; SAM pocket residues conserved with zebrafish SAH-bound 6IRY. |
| BPTF | 3UV2 | (6.14, -2.73, 5.12) | 10.0 | Centroid of 7PE fragment bound in bromodomain acetyl-lysine pocket. |
| LARP1 | 5V87 | (-1.70, 12.47, -23.36) | 10.0 | Centroid of 91P (m7GpppC cap analog) in DM15 cap-binding pocket. |
| SH3BP5 | 6IXG | (-0.76, -25.64, 1.30) | 12.0 | JNK-docking face Cα centroid (resi 100, 103, 107, 150, 160). Native apo. |
| KAT6B | 8DD5 | (13.86, 14.21, 18.16) | 12.0 | Centroid of R7L (PF-9363/CTX-648 clinical inhibitor) in KAT6A MYST HAT pocket. KAT6A used as paralog template (no KAT6B MYST PDB exists; >70% sequence identity in MYST domain). |

## Cost

- **GPU**: Vast 35124116 (A100 SXM4 40GB)
- **Rate**: $0.69/hr
- **Wall-clock**: 30 min (14:33:55 UTC → 15:04:04 UTC)
- **Attach-mode**: reused instance rented for prior JAK2 campaign, no new provisioning
- **Marginal incremental cost**: ~$0.35
- **Within budget** ($0-20 cap): YES

## Caveats & Gates

1. **Not yet Boltz-2/DiffDock validated**. cfd_pos is PocketXMol's internal denoising confidence, not a binding affinity. Next step: route `boltz2_queue.jsonl` per target into Boltz-2 15-kinase/15-offtarget selectivity panel (where applicable) or into DiffDock for non-kinase targets.
2. **BBB threshold is a heuristic** (Mahato 2005-simplified), not a trained model. Targets PCIF1/BPTF/LARP1/KAT6B are intracellular proteins in spinal motor neurons — BBB permeability is required. SH3BP5 also intracellular but mitochondrial-associated.
3. **KAT6B is modeled on KAT6A paralog template**. Generated molecules are against MYST HAT acetyl-CoA-competitive pocket of KAT6A; KAT6B-selective activity must be evaluated post-hoc with AlphaFold2 KAT6B MYST homology modeling + Boltz-2 on KAT6B (once a structural model is available).
4. **Apo-based pocket definitions (PCIF1, SH3BP5)** may have slightly different pocket geometry than holo forms. Top-hit binders should be re-scored against AlphaFold relaxed + ligand-induced-fit models before wet-lab handoff.
5. **Simon-Comms-Gate HELD**. These are in silico hypothesis-generation outputs. No external comms until at least one target reaches Boltz-2 consensus + orthogonal docking validation.

## Downstream Pipeline (Phase F, not yet executed)

For each target, `boltz2_queue.jsonl` contains the top-100 Lipinski-valid compounds ranked by cfd_pos. Next:

1. **Boltz-2 affinity + iptm** per target (100 × 5 = 500 tasks; ~$4-8 on batched self-hosted Boltz-2 server per learnings-diffdock SOP R6).
2. **Selectivity panel** for intracellular kinase/methyltransferase overlap:
   - PCIF1: vs METTL3/METTL14/METTL16 (m6A writers)
   - BPTF: vs BRD4/BRD2/BRD3/TRIM24 (bromodomains)
   - LARP1: vs LARP4/LARP6/LARP7 (La-family)
   - SH3BP5: vs SH3BP5L, JNK1/2/3 (since docking-face)
   - KAT6B: vs KAT6A/MOZ/KAT7/MORF (MYST family)
3. **z-score selectivity gate** (per `rule-zscore-is-the-selectivity-metric.md`)
4. **ADMET filter** (ADMET-AI if available)
5. **MD refinement** for top-5 per target if Boltz-2 passes

## Artifacts

- `/home/bryza/fleet-results/atlas_top5_pxm/PCIF1/SDF/` — 600 raw .sdf files
- `/home/bryza/fleet-results/atlas_top5_pxm/PCIF1/molecules.smi` — SMILES + IDs
- `/home/bryza/fleet-results/atlas_top5_pxm/PCIF1/gen_info.csv` — PocketXMol metadata (cfd scores)
- `/home/bryza/fleet-results/atlas_top5_pxm/PCIF1/pxm_smiles_master.csv` — all + RDKit/Lipinski/BBB
- `/home/bryza/fleet-results/atlas_top5_pxm/PCIF1/top100_by_cfd_pos.csv` — top-100 Lipinski-valid
- `/home/bryza/fleet-results/atlas_top5_pxm/PCIF1/boltz2_queue.jsonl` — top-100 ready for Boltz-2
- `/home/bryza/fleet-results/atlas_top5_pxm/PCIF1/filter_summary.json` — stats
- `/home/bryza/fleet-results/atlas_top5_pxm/PCIF1/summary.json` — PocketXMol run metadata
- `/home/bryza/fleet-results/atlas_top5_pxm/BPTF/SDF/` — 600 raw .sdf files
- `/home/bryza/fleet-results/atlas_top5_pxm/BPTF/molecules.smi` — SMILES + IDs
- `/home/bryza/fleet-results/atlas_top5_pxm/BPTF/gen_info.csv` — PocketXMol metadata (cfd scores)
- `/home/bryza/fleet-results/atlas_top5_pxm/BPTF/pxm_smiles_master.csv` — all + RDKit/Lipinski/BBB
- `/home/bryza/fleet-results/atlas_top5_pxm/BPTF/top100_by_cfd_pos.csv` — top-100 Lipinski-valid
- `/home/bryza/fleet-results/atlas_top5_pxm/BPTF/boltz2_queue.jsonl` — top-100 ready for Boltz-2
- `/home/bryza/fleet-results/atlas_top5_pxm/BPTF/filter_summary.json` — stats
- `/home/bryza/fleet-results/atlas_top5_pxm/BPTF/summary.json` — PocketXMol run metadata
- `/home/bryza/fleet-results/atlas_top5_pxm/LARP1/SDF/` — 600 raw .sdf files
- `/home/bryza/fleet-results/atlas_top5_pxm/LARP1/molecules.smi` — SMILES + IDs
- `/home/bryza/fleet-results/atlas_top5_pxm/LARP1/gen_info.csv` — PocketXMol metadata (cfd scores)
- `/home/bryza/fleet-results/atlas_top5_pxm/LARP1/pxm_smiles_master.csv` — all + RDKit/Lipinski/BBB
- `/home/bryza/fleet-results/atlas_top5_pxm/LARP1/top100_by_cfd_pos.csv` — top-100 Lipinski-valid
- `/home/bryza/fleet-results/atlas_top5_pxm/LARP1/boltz2_queue.jsonl` — top-100 ready for Boltz-2
- `/home/bryza/fleet-results/atlas_top5_pxm/LARP1/filter_summary.json` — stats
- `/home/bryza/fleet-results/atlas_top5_pxm/LARP1/summary.json` — PocketXMol run metadata
- `/home/bryza/fleet-results/atlas_top5_pxm/SH3BP5/SDF/` — 600 raw .sdf files
- `/home/bryza/fleet-results/atlas_top5_pxm/SH3BP5/molecules.smi` — SMILES + IDs
- `/home/bryza/fleet-results/atlas_top5_pxm/SH3BP5/gen_info.csv` — PocketXMol metadata (cfd scores)
- `/home/bryza/fleet-results/atlas_top5_pxm/SH3BP5/pxm_smiles_master.csv` — all + RDKit/Lipinski/BBB
- `/home/bryza/fleet-results/atlas_top5_pxm/SH3BP5/top100_by_cfd_pos.csv` — top-100 Lipinski-valid
- `/home/bryza/fleet-results/atlas_top5_pxm/SH3BP5/boltz2_queue.jsonl` — top-100 ready for Boltz-2
- `/home/bryza/fleet-results/atlas_top5_pxm/SH3BP5/filter_summary.json` — stats
- `/home/bryza/fleet-results/atlas_top5_pxm/SH3BP5/summary.json` — PocketXMol run metadata
- `/home/bryza/fleet-results/atlas_top5_pxm/KAT6B/SDF/` — 600 raw .sdf files
- `/home/bryza/fleet-results/atlas_top5_pxm/KAT6B/molecules.smi` — SMILES + IDs
- `/home/bryza/fleet-results/atlas_top5_pxm/KAT6B/gen_info.csv` — PocketXMol metadata (cfd scores)
- `/home/bryza/fleet-results/atlas_top5_pxm/KAT6B/pxm_smiles_master.csv` — all + RDKit/Lipinski/BBB
- `/home/bryza/fleet-results/atlas_top5_pxm/KAT6B/top100_by_cfd_pos.csv` — top-100 Lipinski-valid
- `/home/bryza/fleet-results/atlas_top5_pxm/KAT6B/boltz2_queue.jsonl` — top-100 ready for Boltz-2
- `/home/bryza/fleet-results/atlas_top5_pxm/KAT6B/filter_summary.json` — stats
- `/home/bryza/fleet-results/atlas_top5_pxm/KAT6B/summary.json` — PocketXMol run metadata

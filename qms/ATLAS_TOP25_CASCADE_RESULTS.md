# SMA Novel Target Atlas — Extended (ranks 6-25) Cascade Results

**Date**: 2026-04-17T16:33:26Z
**Parent atlas**: `/home/bryza/sma-research/qms/SMA_NOVEL_TARGET_ATLAS_2026.md`
**TITLE audit**: `/home/bryza/sma-research/qms/proteome_wide_2026/TITLE_AUDIT_extended.md`
**Top-5 sibling campaign**: `/home/bryza/sma-research/qms/SMA_NOVEL_TARGET_ATLAS_TOP5_PXM_RESULTS.md`
**Cross-connections**: `/home/bryza/sma-research/qms/ATLAS_TOP25_cross_connections.md`
**Top-3 per target**: `/home/bryza/sma-research/qms/ATLAS_TOP25_top3_per_target.tsv`

**Status**: DRAFT — INTERNAL ONLY. Simon-Comms-Gate HELD.

## Target selection (20 → 9 fired)

Atlas ranks 6-25 (skipping top5 = PCIF1, BPTF, LARP1, SH3BP5, KAT6B already fired)
→ 20 candidates passing druggable_bucket ≥ 4, pubmed ≤ 10, mean_cosine ≥ 0.55
→ 11 skipped (no suitable PDB ≤ 2.5 Å OR fpocket druggability < 0.1):
  TEF, PI4KA, EIF4G1, MRPS31, RANBP2, USP34, BTF3, TIAM1, MYCBP2, OPTN, PIK3C2A
→ **9 targets fired**: EP400, PEAK1, KAT7, RNF213, EHMT2, KAT6A, KAT5, KMT5B, EHMT1

See TITLE_AUDIT_extended.md for per-target rationale.

## Per-target cascade statistics

| Target | PDB | total gen | valid | passed filters | top100 | top cfd_pos |
|--------|-----|-----------|-------|----------------|--------|-------------|
| EP400 | 9C57 | 600 | 530 | 326 | 100 | 2.922396659851074 |
| PEAK1 | 6BHC | 600 | 492 | 76 | 76 | 2.902360916137696 |
| KAT7 | 7D0P | 600 | 533 | 278 | 100 | 2.8940141201019287 |
| RNF213 | 8S24 | 600 | 535 | 90 | 90 | 2.871288537979126 |
| EHMT2 | 5VSC | 600 | 575 | 158 | 100 | 2.9483091831207275 |
| KAT6A | 9DZN | 600 | 514 | 108 | 100 | 2.863621473312378 |
| KAT5 | 2OU2 | 600 | 521 | 212 | 100 | 2.8836476802825928 |
| KMT5B | 3S8P | 600 | 559 | 339 | 100 | 2.910175085067749 |
| EHMT1 | 3HNA | 600 | 549 | 244 | 100 | 2.959302425384521 |

## Top-3 per target (Z-scored Boltz-2 selectivity)

Columns: target, rank, SMILES (truncated), QED, BBB, z_primary, selectivity_z

### EP400

| # | SMILES | QED | BBB | iptm_primary | z_primary | sel_z |
|---|--------|-----|-----|--------------|-----------|-------|
| 1 | `c1ccc(-c2cc(Nc3c4ccccc4nc4nccnc34)ccn2)cc1` | 0.465 | 0.750 | — | — | — |
| 2 | `Oc1ccc(-c2cnc(-c3ccccc3)nc2-c2cccnc2)cc1` | 0.599 | 0.750 | — | — | — |
| 3 | `O=C(c1ccc(-c2ccccc2)cc1)c1cc2ccccc2nc1O` | 0.548 | 0.750 | — | — | — |

### PEAK1

| # | SMILES | QED | BBB | iptm_primary | z_primary | sel_z |
|---|--------|-----|-----|--------------|-----------|-------|
| 1 | `Cc1ccc(C)c2c1=NC1=C(Nc3ccc(F)cc3)C(=O)N=NC=21` | 0.924 | 1.000 | — | — | — |
| 2 | `O=C(O)c1ccc(-c2[nH]c3nc(=O)[nH+]cc-3c3cc(O)ccc23)cc1` | 0.484 | 0.750 | — | — | — |
| 3 | `O=C(CNNC(Cc1ccc(Cl)cc1)C(=O)O)Nc1ccc(F)cc1` | 0.538 | 0.600 | — | — | — |

### KAT7

| # | SMILES | QED | BBB | iptm_primary | z_primary | sel_z |
|---|--------|-----|-----|--------------|-----------|-------|
| 1 | `c1ccc(CCNc2nc3ccccc3c3ccccc23)cc1` | 0.534 | 0.750 | — | — | — |
| 2 | `O=P(O)(O)Cc1cccc(-c2cnc3ccccc3c2Cc2ccccc2)c1` | 0.462 | 0.750 | — | — | — |
| 3 | `O=c1[nH]c(OCc2ccccc2)c(Cc2ccc(O)cc2)c2ccccc12` | 0.556 | 0.750 | — | — | — |

### RNF213

| # | SMILES | QED | BBB | iptm_primary | z_primary | sel_z |
|---|--------|-----|-----|--------------|-----------|-------|
| 1 | `O=C(O)c1cc(-c2ccccc2)[n+](Cc2ccccc2)c2ccccc12` | 0.554 | 0.750 | — | — | — |
| 2 | `Cc1cccc2nc3c(N(C)c4ccccn4)ccc(C(=O)O)c3nc12` | 0.567 | 1.000 | — | — | — |
| 3 | `Cc1cccc(-c2ncnc3c2NC2=CC=CC=CC2=C3CO[SH](=O)(O)O)c1` | 0.585 | 0.600 | — | — | — |

### EHMT2

| # | SMILES | QED | BBB | iptm_primary | z_primary | sel_z |
|---|--------|-----|-----|--------------|-----------|-------|
| 1 | `O=C(CNC(=O)c1ccc(-c2ccccc2)cc1)NCCOCc1ccccc1` | 0.552 | 0.850 | — | — | — |
| 2 | `Cc1ccc(-n2ncc(NC(=O)c3cccc(-c4cccnc4)c3)n2)cc1C` | 0.585 | 0.750 | — | — | — |
| 3 | `Cc1ccc(Cc2ccc3ccc(C(=O)CP(=O)(O)O)cc3c2)cc1` | 0.534 | 0.750 | — | — | — |

### KAT6A

| # | SMILES | QED | BBB | iptm_primary | z_primary | sel_z |
|---|--------|-----|-----|--------------|-----------|-------|
| 1 | `O=P(O)(O)c1nc(-c2cccc(F)c2)nc(-c2ccnc3ccccc23)n1` | 0.524 | 0.750 | — | — | — |
| 2 | `O=C(O)C1Cc2cc(-c3ccc(F)cc3)ccc2[NH+]1Cc1ccc2[nH]cnc2c1` | 0.503 | 1.000 | — | — | — |
| 3 | `O=P(O)(O)CN(CCc1ccccc1)CCc1cccc2ncccc12` | 0.594 | 1.000 | — | — | — |

### KAT5

| # | SMILES | QED | BBB | iptm_primary | z_primary | sel_z |
|---|--------|-----|-----|--------------|-----------|-------|
| 1 | `O=c1[nH]c(-c2c[nH+]c3ccccc3c2)nc2cc3ccccc3cc12` | 0.478 | 1.000 | — | — | — |
| 2 | `COc1ccc(-c2nc(Cc3ccccc3)nn3c2nc2ccccc23)cc1` | 0.468 | 0.750 | — | — | — |
| 3 | `CS(=O)(=O)c1ccc2c(c1)c(-c1ccccc1)cn2-c1ccccc1` | 0.539 | 0.750 | — | — | — |

### KMT5B

| # | SMILES | QED | BBB | iptm_primary | z_primary | sel_z |
|---|--------|-----|-----|--------------|-----------|-------|
| 1 | `Cc1ccc(Oc2ccccc2-c2ccc(CP(=O)(O)O)cc2)cc1` | 0.623 | 0.750 | — | — | — |
| 2 | `CNc1cc(C)c(O)cc1CNC(=O)Nc1ccccc1-c1ccccc1` | 0.496 | 0.600 | — | — | — |
| 3 | `c1ccc(CNCc2ccc(-c3cnc4ccccc4n3)cc2)cc1` | 0.583 | 0.750 | — | — | — |

### EHMT1

| # | SMILES | QED | BBB | iptm_primary | z_primary | sel_z |
|---|--------|-----|-----|--------------|-----------|-------|
| 1 | `Cc1ccc(-c2nc(-c3ccc(-c4ccccc4)cc3)[nH]c(=N)n2)cc1` | 0.573 | 0.750 | — | — | — |
| 2 | `c1ccc(Nc2nc(-c3ccccc3)c3cnn(-c4ccccc4)c3n2)cc1` | 0.475 | 0.750 | — | — | — |
| 3 | `NC(=O)c1ccc(-n2nc(-c3ccccc3)c3nc4ccccc4cc32)cc1` | 0.517 | 0.750 | — | — | — |

## Cross-target top hits (passing z_primary > 0 AND sel_z > 0)

_Pending Boltz-2 panel completion._


## Triple-LLM gate

This report MUST be triple-LLM-verified before any non-internal use.
Verification file: `ATLAS_TOP25_CASCADE_RESULTS_triple_llm.json` (pending).

## Next compute steps

1. **MD (25 ns)** for top-3 overall cross-target hits → stage on any idle A100.
2. **Cross-paralog selectivity** (KAT5/6A/7 vs KAT6B; EHMT1 vs EHMT2; KMT5B vs KMT5A/C).
3. **Chai-1 or OpenFold2 multi-seed rescore** for the top-3 to remove Boltz-2 single-pose bias.
4. **Known-inhibitor comparison**: for each target where a reference inhibitor exists (UNC0642/G9a, A-196/SUV420, PF-9363/KAT6, NU9056/KAT5), re-dock via Boltz-2 as sanity check.
5. **Fleet cross-connection cron**: after merge, `cross_connection_engine.py` should auto-detect triangles (KAT5+TP53+PERP, TIP60-EP400, EHMT1+EHMT2).

## Rules of use

- DRAFT. Simon-Comms-Gate HELD until triple-LLM 3/3 PASS + Christian SEND trigger.
- No external (Simon, Torsten) communication.
- Internal worktree review only.

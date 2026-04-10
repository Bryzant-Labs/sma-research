# bbb5 Is a Dual LIMK2 / ROCK1 Inhibitor — NOT LIMK2-Selective

**Date**: 2026-04-09
**Status**: COMPUTATIONAL VALIDATED (4-target panel, MDAnalysis contact proxy + MMPBSA)
**Compound**: `bbb5` (internal id `genmol_119_bbb_5`)
**SMILES**: `CC(C)C(=O)N1CC[C@@H](NCC(F)(F)F)[C@H](c2ccncc2)C1`
**License**: CC-BY-4.0

## TL;DR

bbb5 — previously our top LIMK2-selective candidate from an earlier GenMol run — **binds ROCK1 stronger than LIMK2**. After running a four-target POCKET_FIXED MD panel (LIMK2 / LIMK1 / ROCK1 / JAK2) and extracting contact-proxy and MMPBSA ddG values, bbb5 is reclassified as a **dual LIMK2 / ROCK1 inhibitor** with selectivity only over LIMK1 and JAK2.

This may actually be therapeutically useful for SMA because ROCK → LIMK2 → CFL2 is the whole axis we want to suppress, and hitting both ROCK1 and LIMK2 covers two nodes at once. But the original claim of "LIMK2-selective" is wrong and we no longer make it.

## Panel Results

Source: `drug_discovery/mmpbsa/bbb5_selectivity_FINAL.json`
Method: POCKET_FIXED MD (10–20 ns), MDAnalysis contact proxy (6 Å heavy-atom contacts), proxy-dG estimator.

| Target | PDB | Role | min dist (Å) | contacts (6 Å) | proxy dG | status |
|---|---|---|---:|---:|---:|---|
| **LIMK2** | 4TPT | PRIMARY | 2.15 | 1,701 | −255.2 | BOUND |
| LIMK1 | 3S95 | OFF-target | 1.89 | 1,340 | −200.9 | BOUND |
| **ROCK1** | 2ESM | OFF-target | 1.95 | **2,591** | **−388.7** | BOUND (stronger than LIMK2) |
| JAK2 | 3FUP | OFF-target | 27.05 | 13 | −2.0 | UNBOUND |

### Selectivity table (ddG = LIMK2 − off-target)

| vs. | ddG (proxy kJ/mol) | Selective? | Note |
|---|---:|---|---|
| LIMK1 | +54.3 | yes | LIMK2 binds ~25% more tightly |
| **ROCK1** | **−133.4** | **NO** | ROCK1 binds STRONGER — not selective |
| JAK2 | +253.3 | yes | JAK2 unbound (diffused away) |

## Verdict

**DUAL_LIMK2_ROCK1_INHIBITOR**

bbb5 is not a LIMK2-selective compound. The POCKET_FIXED ROCK1 MD gave the strongest contact count (2,591 at 6 Å) and the most negative contact-proxy dG (−388.7). LIMK2 binding is real and stable, but quantitatively weaker than ROCK1 by a wide margin.

## Why We Caught This

Previous screens used MM-PBSA on trajectories where the ligand had drifted away from the pocket center (the COM placement bug — see L1 memory `mmpbsa-ligand-placement-bug.md`). When we rebuilt the panel with POCKET_FIXED placement (ligand centered on the crystal-derived pocket, harmonic restraint during equilibration), the ROCK1 simulation produced a dramatically stronger binding signature than earlier runs had shown. That broke the LIMK2-selective hypothesis.

This is exactly why we published it as a negative result: the earlier "bbb5 is LIMK2-selective" claim was an artifact of the ligand-placement bug, not a biological finding.

## Implications

- **Do not present bbb5 to Simon as a LIMK2-selective lead.** It is a dual-axis inhibitor at best.
- **But do not drop bbb5 either.** If the ROCK → LIMK2 → CFL2 axis is the therapeutic target, a single molecule hitting two nodes of that axis may be more effective than a selective LIMK2 binder. This is a hypothesis, not a result.
- **Keep bbb5 as a backup track** (Track 3 in our memory). Priority moves to the 14 new selective hits (see `FINDING_2026-04-10_new_7_selective_hits.md`).
- **Do not repeat the COM placement protocol** for any SMA compound. POCKET_FIXED is the only validated method in this platform. See `mmpbsa-ligand-placement-bug.md` in L1 memory.

## Data Provenance

- MD trajectories: `md_sims/LIMK2_bbb5_POCKET_FIXED/`, `md_sims/LIMK1_bbb5_POCKET_FIXED/`, `md_sims/ROCK1_bbb5_POCKET_FIXED/`, `md_sims/JAK2_bbb5_selectivity/`
- MMPBSA results: `drug_discovery/mmpbsa/LIMK2_bbb5_*_MMPBSA_*.csv`, `.dat`
- Selectivity summary: `drug_discovery/mmpbsa/bbb5_selectivity_FINAL.json`

## Citation

Open-source SMA drug-discovery platform — `Bryzant-Labs/sma-research`. Published under CC-BY-4.0.

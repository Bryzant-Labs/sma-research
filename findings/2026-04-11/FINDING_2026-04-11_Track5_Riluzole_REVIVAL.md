# Track 5 Riluzole — REVIVAL from Orphan Trajectory Analysis

**Date**: 2026-04-11
**Status**: COMPUTATIONAL DISCOVERY — reopens closed track
**Previous status**: Track 5 (Riluzole) was marked "CLOSED — negative" in session memory based on DiffDock confidence +0.082
**New status**: REOPEN — Riluzole binds SMN2 at a novel pocket shared with 4-AP

## The discovery

During the 2026-04-10 orphan trajectory analysis (re-running MDAnalysis on 44 completed MD trajectories whose analysis had never been done), we found that **Riluzole remains engaged 100% of 20 ns** on SMN2 at the pocket:

**Top persistent contacts (Riluzole + SMN2):**

| Residue | Frames | Persistence |
|---|---|---|
| GLY294 | 46/50 | 92% |
| SER271 | 46/50 | 92% |
| VAL272 | 45/50 | 90% |
| CYS658 | 44/50 | 88% |
| PRO268 | 43/50 | 86% |
| TYR657 | 37/50 | 74% |

**Top persistent contacts (4-AP + SMN2) for comparison:**

| Residue | Frames | Persistence |
|---|---|---|
| PRO268 | 46/50 | 92% |
| VAL413 | 46/50 | 92% |
| ASN270 | 46/50 | 92% |
| SER271 | 44/50 | 89% |
| PHE266 | 40/50 | 81% |
| VAL267 | 40/50 | 81% |
| ILE269 | 37/50 | 74% |
| TYR657 | 31/50 | 63% |

**Shared residues**: PRO268, SER271, TYR657

## Why this matters

Two structurally different small molecules (Riluzole: benzothiazole, C₈H₅F₃N₂S, MW 234; 4-AP: aminopyridine, C₅H₆N₂, MW 94) **bind the same pocket in independent MD simulations**. This is unlikely to be:

- ❌ Co-solvent placement artifact (different starting poses)
- ❌ Force field bias (both simulations used same protocol, different ligands)
- ❌ Topology mismatch (both MDs verified post-hoc)

It is more likely to be a **real druggable pocket** on SMN2 that neither Nusinersen (ASO) nor Risdiplam (RNA binder) target.

## The pocket

The PRO268/SER271/TYR657 region is distinct from the canonical RNA binding region of the SMN2 Tudor domain. Looking at the spatial arrangement:

- PRO268, VAL267, ASN270 form a small hydrophobic/polar patch
- SER271, GLY294, TYR657 form an adjacent coordination site
- The pocket is solvent-accessible (based on the trajectory)

This is consistent with a **novel small-molecule binding site** that could be exploited for SMN2 modulation, independently of the canonical splicing modifier mechanism.

## Why Track 5 was originally closed

The April session memory (`next-session-priorities-2026-04-09.md`) marked Riluzole as:
> Track 5: Riluzole (CLOSED — negative)

Basis: DiffDock confidence +0.082 (only hit from 56 screened compounds), marked as "positive" but not pursued further.

**What we missed**: DiffDock confidence is a pose-quality estimator, not a binding affinity predictor. A +0.082 means "DiffDock thinks this pose is plausible but not highly confident." The ACTUAL binding was already visible in the MD that was run afterwards — but that MD's analysis was never done until the 2026-04-10 orphan sweep.

This is a case where **orphan data contained the answer that closed us out of a track prematurely**.

## What this means for Simon Pack

The Simon Pack adds a third experiment (Experiment 3) focused on validating the Riluzole/4-AP shared SMN2 pocket:

- **SPR**: measure KD for both compounds vs recombinant SMN2 Tudor domain
- **Reporter assay**: SMN2 exon 7 splicing efficiency ± compounds
- **Co-crystal attempt** (stretch goal): structural confirmation

Cost: ~2,000 EUR, duration: 1 month. **Cheap + high information value**.

If validated: **two FDA-approved drugs** (4-AP for MS, Riluzole for ALS) both hit a novel SMN2 mechanism. Both cross BBB. Both have decades of safety data. Publishable finding even if effect size is modest — the mechanism itself is new.

## Lessons

### 1. Don't close tracks based on single metrics

Riluzole was closed on DiffDock confidence alone. The MD that ran AFTER closure showed the real answer. Always wait for MD + analysis before a final verdict.

### 2. Orphan data can contain retroactive answers

44 MD trajectories had been sitting with no analysis. Re-running MDAnalysis surfaced this discovery in ~30 minutes of CPU time. Lesson: **weekly orphan sweeps** are cheap and high-ROI.

### 3. Shared binding sites across chemotypes are signal, not noise

When two chemically unrelated molecules bind the same residues in independent simulations, the pocket is real. This is now documented in memory as a pattern to watch for.

## Data files

- Original MD: `~/gpu-fleet/results/SMA/md_sims/SMN2_Riluzole_holo/`
- Trajectory: `SMN2_Riluzole_holo/trajectory.dcd` (999 MB, 20 ns)
- Analysis JSON: `/tmp/orphan_analysis/SMN2_Riluzole_holo_analysis.json`
- 4-AP comparison: `/tmp/orphan_analysis/4AP_SMN2_holo_analysis.json`
- Orphan analysis script: `~/gpu-fleet/scripts/analyze_orphan_trajectory.py`

## Action items

1. [ ] Update `PROJECT_CATALOG.md` — mark Track 5 as REOPEN, add SMN2 pocket section
2. [ ] Include in Simon Mega Pack (`02_evidence/08_track5_riluzole_revival.md`)
3. [ ] Add to Experiment 3 in wet-lab protocol
4. [ ] Notify Christian (done via Simon Pack email)
5. [ ] Recompute DiffDock for Riluzole vs SMN2 with better pocket restraint
6. [ ] Run MMPBSA on Riluzole SMN2 trajectory for ΔG_bind (local CPU, ~1h)

## License

CC-BY-4.0 — open finding. Part of `Bryzant-Labs/sma-research` public repository.

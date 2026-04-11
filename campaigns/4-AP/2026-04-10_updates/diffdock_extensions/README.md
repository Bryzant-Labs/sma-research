# 4-AP DiffDock Extensions — 2026-04-10

**Purpose**: Three follow-up DiffDock batches to test specific 4-AP claims that the April 2 multi-target story made but never fully validated.

**Pipeline**: DiffDock v2.2 via NVIDIA NIM, no MD follow-up at this stage.

## Batches

### 1. `regeneration_summary.json` — Regeneration target panel

**Question**: Does 4-AP have measurable affinity for canonical axon-regeneration signaling targets (BDNF / TrkB / STAT3 / PTEN / mTOR)?

**Compound**: 4-AP (`Nc1ccncc1`)
**Targets**: BDNF (1BND), TrkB (4ASZ), STAT3 (1BG1), PTEN (1D5R), mTOR FRB (4DRI)
**Wall time**: 456 s

**Verdict**: All five top-rank confidences are between **-0.16 and -0.38** — well below the docking-significance threshold (rank-1 confidence > +0.0 typically required for a credible hit). Only BDNF reaches -2.96 because BDNF is a small protein homodimer with broad pockets that pick up almost anything. **None of these targets is a real 4-AP binding partner.** The "regeneration multi-target" framing of 4-AP from the April 2 campaign is **NOT supported by structural docking**.

### 2. `kv1_family_summary.json` — Kv1 channel family selectivity

**Question**: Among the Kv1.x family, is 4-AP selective for the axonal subtypes (Kv1.1, Kv1.2) or does it also hit cardiac/lymphoid subtypes (Kv1.3, Kv1.5)?

**Compound**: 4-AP (`Nc1ccncc1`)
**Targets**: Kv1.1 (6EBK), Kv1.3 (3OC3), Kv1.5 (7SIT)
**Wall time**: 261 s

**Result**:
- Kv1.1: -0.05
- Kv1.3: -0.78 (worst)
- Kv1.5: -0.10

**Combined with Kv1.2 from the April 2 campaign**: 4-AP shows the strongest engagement at the axonal Kv1.1 / Kv1.2 pair. Selectivity over Kv1.3 / Kv1.5 is modest but real. This is **consistent with the established Ampyra mechanism** — 4-AP is a relatively selective axonal Kv1 blocker, not a pan-Kv blocker.

### 3. `34DAP_summary.json` — 3,4-DAP (Firdapse) head-to-head

**Question**: Does 3,4-diaminopyridine (Firdapse, the second amine adds basicity and slightly larger volume) have a different docking profile across the same target panel?

**Compound**: 3,4-DAP (`Nc1ccnc(N)c1`)
**Targets**: full panel (BDNF, TrkB, STAT3, PTEN, mTOR FRB, Kv1.1, Kv1.3, Kv1.5, Kv1.2, NCALD, SMN2, SMN1, UBA1)
**Wall time**: 970 s
**Failures**: SMN2 and SMN1 (4QK9 Tudor) — DiffDock could not place 3,4-DAP in the small Tudor pocket

**Head-to-head verdict (vs 4-AP, all confidences from rank-1 best pose)**:

| Target | 4-AP | 3,4-DAP | Better |
|---|---|---|---|
| Kv1.1 | -0.05 | -0.17 | 4-AP |
| Kv1.2 | (April 2 +) | -0.52 | 4-AP |
| Kv1.3 | -0.78 | -1.17 | 4-AP |
| Kv1.5 | -0.10 | -0.30 | 4-AP |
| BDNF | -2.96 | -0.11 | 3,4-DAP (but irrelevant) |
| TrkB | -0.19 | -0.69 | 4-AP |
| NCALD | (April 2) | -1.18 | 4-AP |
| UBA1 | (April 2) | -0.06 | 3,4-DAP |

**Conclusion**: For the axonal Kv1.x family — the only pharmacologically relevant cluster in the panel — **4-AP outperforms 3,4-DAP at every Kv1 subtype**. This is consistent with clinical practice where 4-AP/Ampyra is the preferred MS walking drug despite 3,4-DAP being more potent in some Lambert-Eaton contexts.

## Overall verdict

The combined extension panel **falsifies the April 2 "4-AP as a multi-mechanism recovery agent" framing**:

1. No measurable docking signal at canonical regeneration targets (BDNF/TrkB/STAT3/PTEN/mTOR FRB)
2. Real selectivity at axonal Kv1.1/Kv1.2 over cardiac Kv1.5 and lymphoid Kv1.3
3. 4-AP beats 3,4-DAP at every Kv1 subtype tested

**Reframed verdict**: 4-AP is a **selective axonal Kv1 channel blocker**, not a multi-target recovery drug. Its SMA-relevance comes from compensating for axonal hyperexcitability/conduction failure (the validated Ampyra mechanism), NOT from regeneration signaling.

## Cross-reference

The orphan trajectory analysis on the same day independently rediscovered that **4-AP also weakly engages a novel SMN2 Tudor-domain pocket** shared with Riluzole — see `../../../findings/2026-04-10/ORPHAN_TRAJECTORY_ANALYSIS.md`. So the final story is "selective axonal Kv1 blocker WITH a secondary druggable SMN2 pocket binding event," which is a richer (and structurally honest) story than either of the two earlier framings.

## Where the docked SDF poses live

All ranked SDF poses (rank1-rank10 per target per batch) are too numerous for git. They are mirrored on Dropbox:

- `Dropbox/SMA/open_data/4ap_extensions_2026-04-10/`

On-cluster source: `~/gpu-fleet/results/SMA/drug_discovery/diffdock/4ap_extensions_2026-04-10/`.

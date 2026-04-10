# SMA Research — Findings INDEX

**Updated**: 2026-04-10
**License**: all findings published under CC-BY-4.0

Every entry in this index is a computational result from the open-source SMA drug-discovery platform. "Preliminary" = computational only; "validated" = replicated across independent methods; "published" = Simon / collaborator / external audience has reviewed. Negative results are published with the same rigor as positive ones.

## Findings Table

| Date | Title | One-line summary | Status | File |
|---|---|---|---|---|
| 2026-04-09 | **bbb5 is a dual LIMK2/ROCK1 inhibitor** | bbb5 binds ROCK1 **stronger** than LIMK2 (contacts 2,591 vs 1,701). Reclassified from "LIMK2-selective" to "dual-axis" after POCKET_FIXED rebuild killed the earlier selectivity artifact. | validated (computational, 4-target panel) | [2026-04-09/FINDING_2026-04-09_bbb5_dual_LIMK2_ROCK1.md](2026-04-09/FINDING_2026-04-09_bbb5_dual_LIMK2_ROCK1.md) |
| 2026-04-09 | **Fasudil scaffold hop — NEGATIVE** (initial) | Early negative-result writeup for the Fasudil scaffold hop. | validated negative | [2026-04-09/NEGATIVE_RESULT_fasudil_scaffold_hop.md](2026-04-09/NEGATIVE_RESULT_fasudil_scaffold_hop.md) |
| 2026-04-10 | **4-AP as complementary recovery agent** | 4-AP does not bind SMN2 but stable Kv1.2 binding → complementary to SMN-restoration therapies (nusinersen, risdiplam, ABE). Track B — Universal Recovery Platform. | computational + literature | [2026-04-10/FINDING_2026-04-10_4AP_complementary_recovery.md](2026-04-10/FINDING_2026-04-10_4AP_complementary_recovery.md) |
| 2026-04-10 | **4-AP selectivity analysis (DEPRECATED)** | Older framing — kept for reference. See "complementary recovery" version above. | deprecated | [2026-04-10/DEPRECATED_FINDING_2026-04-10_4AP_selectivity.md](2026-04-10/DEPRECATED_FINDING_2026-04-10_4AP_selectivity.md) |
| 2026-04-10 | **ESM-2 kinase similarity is too high for sequence-level selectivity** | LIMK1↔LIMK2 = 0.990; ROCK1↔ROCK2 = 0.998. Pocket-level screening is the only workable approach. | validated (foundation model) | [2026-04-10/FINDING_2026-04-10_ESM2_kinase_similarity.md](2026-04-10/FINDING_2026-04-10_ESM2_kinase_similarity.md) |
| 2026-04-10 | **Fasudil scaffold hop — NEGATIVE** (final) | 0/20 Fasudil variants achieved LIMK2 selectivity (margin > 0.3) across 115 scaffold modifications. Isoquinoline sulfonamide is inherently ROCK-preferring. | validated negative | [2026-04-10/FINDING_2026-04-10_Fasudil_scaffold_hop_NEGATIVE.md](2026-04-10/FINDING_2026-04-10_Fasudil_scaffold_hop_NEGATIVE.md) |
| 2026-04-10 | **Cas-OFFinder SMN2 guide safety** | Of 6 candidate gRNAs for SMN2 base editing, 3 are safe (≤23 exact off-targets), 1 is the clear winner (antisense `TTTGTCTAAAACCCATATAA`, 14 exacts), 1 unusable (176 off-targets). | computational, ready for wet-lab review | [2026-04-10/FINDING_2026-04-10_casoffinder_SMN2_guide_safety.md](2026-04-10/FINDING_2026-04-10_casoffinder_SMN2_guide_safety.md) |
| 2026-04-10 | **Seven new LIMK2-selective hits (overnight run)** | DiffDock selectivity screen on PocketXMol DFG-out library yielded 7 new hits (margin 0.33–0.68). Combined with prior session = **14 selective candidates** total. | preliminary (DiffDock only) | [2026-04-10/FINDING_2026-04-10_new_7_selective_hits.md](2026-04-10/FINDING_2026-04-10_new_7_selective_hits.md) |

## Tracks Referenced

- **Track 1** — Fasudil → Simon (WAIT for finished compute package)
- **Track 2A** — SMN2 base editing (research ongoing)
- **Track 2B** — Universal recovery platform (Fasudil/LIMK2 complement)
- **Track 2C** — LIMK2-selective (14 candidates, prioritization in progress)
- **Track 3** — bbb5 dual LIMK2/ROCK1 (backup)
- **Track 4** — 4-AP symptomatic therapy (running)
- **Track 5** — Riluzole (CLOSED, negative)

## How to Add a New Finding

1. Create `YYYY-MM-DD/FINDING_YYYY-MM-DD_<slug>.md` in this directory.
2. Include: date, status, method, TL;DR, data, interpretation, caveats, provenance, citation block.
3. Add a row to the table above.
4. Add a pointer from the relevant campaign README in `../campaigns/<name>/`.
5. Commit to `Bryzant-Labs/sma-research`.

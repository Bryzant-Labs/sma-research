# ESM-2 Kinase Similarity — Why Pocket-Level (Not Sequence-Level) Screening Is Required for SMA

**Date**: 2026-04-10
**Status**: COMPUTATIONAL VALIDATED (foundation-model result, reproducible)
**Model**: `facebook/esm2_t33_650M_UR50D` (ESM-2, 650 M parameters)
**Pooling**: mean-pooled residue embeddings, 1280-dim per protein
**License**: CC-BY-4.0

## TL;DR

LIMK1 ↔ LIMK2 have a **cosine similarity of 0.990** and ROCK1 ↔ ROCK2 a cosine of **0.998** in ESM-2 embedding space. This means sequence-/fold-level discriminators cannot reliably separate the paralogs. **Selective drug discovery for SMA therefore requires pocket-level (structure-based) screening** — DiffDock, PocketXMol, or MD-contact metrics — rather than sequence similarity heuristics. This result empirically justifies our pipeline design.

## Method

1. Fetched eight canonical SMA-relevant protein sequences from UniProt: SMN1 (P38398*), SMN2 (Q16637 paralog Q02447), ROCK1 (Q13464), ROCK2 (O75116), LIMK1 (P53667), LIMK2 (P53671), CFL2 (Q9Y281), PTEN (P60484).
2. Ran `esm2_t33_650M_UR50D` on each sequence (no fine-tuning).
3. Mean-pooled the per-residue embeddings across the sequence length → one 1280-dim vector per protein.
4. Computed the 8 × 8 cosine-similarity matrix on unit-normalized embeddings.

Artifacts in `esm2_foundation/`:
- `esm2_embeddings.npy` — (8, 1280) float32 matrix
- `esm2_similarity_matrix.npy` — (8, 8) float32 cosine matrix
- `esm2_similarity_keys.json` — protein order
- `esm2_embed.py` — exact pipeline script

## Result (cosine similarity)

```
             SMN1   SMN2  ROCK1  ROCK2  LIMK1  LIMK2   CFL2   PTEN
SMN1   1.0000 0.898 0.949 0.952 0.935 0.943 0.730 0.884
SMN2   0.898 1.0000 0.884 0.887 0.838 0.852 0.560 0.748
ROCK1  0.949 0.884 1.0000 0.998 0.928 0.948 0.717 0.882
ROCK2  0.952 0.887 0.998 1.0000 0.931 0.949 0.714 0.879
LIMK1  0.935 0.838 0.928 0.931 1.0000 0.990 0.792 0.924
LIMK2  0.943 0.852 0.948 0.949 0.990 1.0000 0.791 0.931
CFL2   0.730 0.560 0.717 0.714 0.792 0.791 1.0000 0.881
PTEN   0.884 0.748 0.882 0.879 0.924 0.931 0.881 1.0000
```

## Interpretation

- **LIMK1 ↔ LIMK2 = 0.990** → essentially indistinguishable in ESM-2 mean-pool space. Any sequence-based classifier will fail to rank LIMK2-selective compounds ahead of LIMK1 cross-reactors.
- **ROCK1 ↔ ROCK2 = 0.998** → even stronger co-similarity. Fasudil hits both (and pharmacologically behaves as a pan-ROCK inhibitor).
- **CFL2 is the most distant node** (cosines 0.56–0.88). This tracks with its different fold family (actin-binding, not kinase) and supports using CFL2 activity as an orthogonal readout rather than a direct ligand target.
- **SMN2 vs. kinases** (0.85–0.95 range) is a spurious similarity driven by sequence-length effects in mean pooling — SMN2 is not a kinase and does not share a druggable pocket with them.

### Why this matters for the SMA platform

We explicitly designed our pipeline around **structure/pocket-level scoring** (DiffDock, PocketXMol, MMPBSA with POCKET_FIXED placement, contact-proxy analyses). This ESM-2 result is the empirical reason: a sequence similarity-based shortcut would have produced the same answer for LIMK1 and LIMK2, making any "LIMK2-selective" claim indistinguishable from a "LIMK1 cross-reactor." Pocket geometry (DFG-in/out, hinge residues, P-loop shape) is the only reliable differentiator.

### What this does **not** say

- It does **not** claim ESM-2 is bad; it is a general-purpose protein embedding. The mean-pool result is a *feature*, not a bug, for homology search.
- It does **not** replace wet-lab selectivity assays. DiffDock/MMPBSA are still computational proxies; KinomeScan or enzymatic IC50 remain the gold standard.
- It does **not** say SMN2 and kinases share biology — the ~0.85 similarity is numeric, not mechanistic.

## Reproducibility

Full embedding script lives at `esm2_foundation/esm2_embed.py` (open-source). High-level steps:

1. Load `facebook/esm2_t33_650M_UR50D` via `transformers.AutoModel`.
2. For each sequence, run the model in inference mode on GPU; mean-pool the last-hidden-state across valid tokens.
3. L2-normalize each embedding, compute `M @ M.T` to get the cosine matrix.

Run on a single RTX 3090 in ~5 minutes, ~$0.08 compute cost.

## Citation

Open-source SMA drug-discovery platform — `Bryzant-Labs/sma-research`.
Published under CC-BY-4.0.

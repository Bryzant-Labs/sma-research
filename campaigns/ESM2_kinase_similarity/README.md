# ESM-2 Foundation Embeddings — Kinase Similarity

**Date**: 2026-04-10
**Status**: DONE
**Priority**: DONE

## TL;DR

**LIMK1 / LIMK2** cosine similarity = **0.990**
**ROCK1 / ROCK2** cosine similarity = **0.998**

Empirically demonstrates why sequence-level foundation embeddings cannot distinguish kinase isoforms — **pocket-level methods are required** for selective drug design. This result supports the PocketXMol campaign's methodology choice.

## Contents

- `similarity_matrix.npy` — Full NxN cosine similarity matrix
- `similarity_keys.json` — Index → kinase name mapping
- `metadata.json` — ESM-2 model config, sequences used, computation date
- `foundation_model_schema.json` — Embedding schema
- `gsea_hallmarks_hg38.json` — GSEA hallmark sets used for downstream analysis

## Script

- `scripts/esm2_embed.py` — Embedding + cosine-similarity computation

## Related finding

- [`../../findings/2026-04-10/FINDING_2026-04-10_ESM2_kinase_similarity.md`](../../findings/2026-04-10/FINDING_2026-04-10_ESM2_kinase_similarity.md)

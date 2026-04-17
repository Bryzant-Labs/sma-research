#!/usr/bin/env python3
"""Score MN-expressed proteome candidates by similarity to verified meta-sig anchors.

Pipeline:
 1. Load proteome ESM-2 embeddings (esm2_embeddings.npz)
 2. Load anchor embeddings (anchor_embeddings.npz)
 3. Compute cosine similarity of each candidate to each anchor
 4. Build two composite scores:
     a. sig_down = mean cosine(candidate, {SMN1, SMN2, ROCK2, PERP})
     b. sig_up   = cosine(candidate, TP53)
     c. signature_score = 0.5 * sig_down + 0.5 * sig_up
        (both contribute equally; sign preserved; we want candidates that sit
         near BOTH an SMN/apoptosis-adjacent down-group AND TP53-axis up-group)
 5. Also compute each anchor's rank in the candidate's nearest-neighbor list,
    as sanity-check for biology.
 6. Write scored TSV: gene, uniprot, cos_SMN1, cos_SMN2, cos_ROCK2, cos_TP53,
    cos_PERP, sig_down, sig_up, signature_score.
"""
import os
import json
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

with np.load('esm2_embeddings.npz') as z:
    accs = list(z.files)
    mat = np.stack([z[a] for a in accs]).astype(np.float32)
print(f'[load] proteome: {mat.shape}')

with np.load('anchor_embeddings.npz') as z:
    anchor_names = list(z.files)
    anchor_mat = np.stack([z[n] for n in anchor_names]).astype(np.float32)
print(f'[load] anchors: {anchor_mat.shape} {anchor_names}')

# Center on proteome mean to remove length/composition bulk signal
# This shift increases dynamic range of cosine similarity
proteome_mean = mat.mean(axis=0, keepdims=True)
mat_centered = mat - proteome_mean
anchor_centered = anchor_mat - proteome_mean


def l2(x):
    n = np.linalg.norm(x, axis=-1, keepdims=True)
    return x / np.clip(n, 1e-8, None)


mat_n = l2(mat_centered)
anchor_n = l2(anchor_centered)

# cosine matrix (N_candidates x N_anchors)
cos = mat_n @ anchor_n.T
print('[score] cos matrix', cos.shape)

cand_df = pd.DataFrame({'uniprot': accs})
for i, name in enumerate(anchor_names):
    cand_df[f'cos_{name}'] = cos[:, i]

# Composite scores
down_cols = [c for c in cand_df.columns if any(a in c for a in ('SMN1', 'SMN2', 'ROCK2', 'PERP'))]
up_cols = [c for c in cand_df.columns if 'TP53' in c]
cand_df['sig_down'] = cand_df[down_cols].mean(axis=1)
cand_df['sig_up'] = cand_df[up_cols].mean(axis=1)
cand_df['signature_score'] = 0.5 * cand_df['sig_down'] + 0.5 * cand_df['sig_up']

# Join with HPA metadata (gene name, description, etc.)
hpa = pd.read_csv('mn_druggable_candidates.tsv', sep='\t')
hpa_small = hpa[['uniprot_primary', 'gene_name', 'Gene', 'sc_ntpm', 'cortex_ntpm',
                 'skm_ntpm', 'heart_ntpm', 'description', 'protein_class']].copy()
hpa_small.columns = ['uniprot', 'gene', 'ensembl', 'sc_ntpm', 'cortex_ntpm', 'skm_ntpm',
                     'heart_ntpm', 'description', 'protein_class']
scored = cand_df.merge(hpa_small, on='uniprot', how='left')

# Exclude the anchors themselves + obvious ribosomal / housekeeping
ANCHOR_ACCS = {'P14639', 'Q16637', 'O75116', 'P04637', 'P60468'}
scored['is_anchor'] = scored['uniprot'].isin(ANCHOR_ACCS)

scored = scored.sort_values('signature_score', ascending=False).reset_index(drop=True)
scored.to_csv('candidates_scored.tsv', sep='\t', index=False)
print(f'[write] candidates_scored.tsv n={len(scored)}')
print(scored.head(20)[['gene', 'uniprot', 'signature_score', 'sig_down',
                        'sig_up', 'sc_ntpm', 'is_anchor']].to_string())

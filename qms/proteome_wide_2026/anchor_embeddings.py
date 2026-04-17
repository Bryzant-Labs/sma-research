#!/usr/bin/env python3
"""Embed the verified meta-signature anchor proteins with the same ESM-2 model.

Anchors come from the VERIFIED meta-analysis in qms/meta_analysis/meta_summary.tsv
(3-dataset DerSimonian-Laird random-effects pooling, dataset_verify PASS).

Verified hits:
  - SMN1   (P14639)  meta_log2FC = -2.13, p = 5.0e-9   => DOWN (positive control)
  - SMN2   (Q16637)  meta_log2FC = -2.89, p = 3.7e-14  => DOWN (positive control)
  - ROCK2  (O75116)  meta_log2FC = -0.25, p = 9.0e-5   => DOWN (novel signal)
  - TP53   (P04637)  meta_log2FC = +0.26, p = 3.0e-2   => UP   (novel signal)

Borderline (informative but p>0.05):
  - PERP   (P60468)  meta_log2FC = -0.26, p = 0.25     => DOWN tendency (weak)

These anchor embeddings define the "SMA-MN transcriptional-response prototype" in
ESM-2 latent space. Our proteome-wide candidates are scored by cosine similarity
to this prototype.

Caveat: ESM-2 captures sequence/family signal, NOT transcriptional-response
biology. "Similarity to SMN1" reflects RBM/Tudor-domain neighbors; similarity to
ROCK2 reflects AGC-kinase neighbors; etc. The approach therefore identifies
family / pathway neighbors of verified hits, and works as hypothesis generator —
NOT as direct proof of transcriptional change in SMA.
"""
import os
import sys
import numpy as np
import torch

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

ANCHORS = {
    'SMN1_P14639': ('P14639', 'DOWN_positive_control'),
    'SMN2_Q16637': ('Q16637', 'DOWN_positive_control'),
    'ROCK2_O75116': ('O75116', 'DOWN_novel'),
    'TP53_P04637': ('P04637', 'UP_novel'),
    'PERP_P60468': ('P60468', 'DOWN_weak'),
}

# Fetch FASTA for anchors (they should already be in mn_proteome.fasta for most)
import requests

def fetch_fasta(acc):
    r = requests.get(f'https://rest.uniprot.org/uniprotkb/{acc}.fasta', timeout=30)
    return r.text if r.status_code == 200 else None

anchor_seqs = {}
for name, (acc, _) in ANCHORS.items():
    txt = fetch_fasta(acc)
    if not txt or not txt.startswith('>'):
        print(f'[WARN] could not fetch {acc}')
        continue
    lines = txt.strip().split('\n')
    seq = ''.join(lines[1:])
    anchor_seqs[name] = (acc, seq)
    print(f'[fetch] {name} {acc} len={len(seq)}')

# Embed
from transformers import AutoTokenizer, AutoModel
tok = AutoTokenizer.from_pretrained('facebook/esm2_t33_650M_UR50D')
model = AutoModel.from_pretrained('facebook/esm2_t33_650M_UR50D')
dev = 'cuda' if torch.cuda.is_available() else 'cpu'
model = (model.to(dev).half()) if dev == 'cuda' else model.to(dev)
model.requires_grad_(False)
model.train(False)
print(f'[device] {dev}')

MAX_LEN = 1022
results = {}
metadata = {}
for name, (acc, seq) in anchor_seqs.items():
    s = seq[:MAX_LEN]
    enc = tok([s], return_tensors='pt', padding=True, truncation=True, max_length=MAX_LEN + 2)
    enc = {k: v.to(dev) for k, v in enc.items()}
    with torch.no_grad():
        out = model(**enc)
    hs = out.last_hidden_state
    mask = enc['attention_mask'].unsqueeze(-1).float()
    pooled = ((hs * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)).float().cpu().numpy()[0]
    results[name] = pooled.astype(np.float32)
    metadata[name] = {'acc': acc, 'seq_len': len(s), 'truncated': len(seq) > MAX_LEN}
    print(f'[embed] {name} shape {pooled.shape}')

np.savez_compressed('anchor_embeddings.npz', **results)
import json
with open('anchor_metadata.json', 'w') as f:
    json.dump({
        'anchors': {k: {'acc': v[0], 'role': v[1]} for k, v in ANCHORS.items()},
        'metadata': metadata,
        'model': 'facebook/esm2_t33_650M_UR50D',
        'pooling': 'attention-masked mean',
        'max_len': MAX_LEN,
    }, f, indent=2)
print('[saved] anchor_embeddings.npz + anchor_metadata.json')

#!/usr/bin/env python3
"""ESM-2 650M embeddings for MN-expressed proteome.

- Reads FASTA at mn_proteome.fasta
- Mean-pools per-residue embeddings to a fixed 1280-d vector per protein
- Skips records > MAX_LEN by truncating to MAX_LEN (RTX A2000 8 GB memory-friendly)
- Saves to esm2_embeddings.npz (one array per accession, no pickle)
- Runs incrementally: if esm2_embeddings.npz exists, skip already-embedded accessions
"""
import os, sys, time
import numpy as np
import torch

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

FASTA = 'mn_proteome.fasta'
OUT = 'esm2_embeddings.npz'
META_OUT = 'esm2_embed_meta.tsv'
MAX_LEN = 1022
MODEL_NAME = 'facebook/esm2_t33_650M_UR50D'


def parse_fasta(p):
    cur_h, cur_s = None, []
    with open(p) as f:
        for line in f:
            line = line.rstrip()
            if not line:
                continue
            if line.startswith('>'):
                if cur_h:
                    yield cur_h, ''.join(cur_s)
                cur_h = line[1:]
                cur_s = []
            else:
                cur_s.append(line)
        if cur_h:
            yield cur_h, ''.join(cur_s)


existing = {}
if os.path.exists(OUT):
    with np.load(OUT) as z:
        for k in z.files:
            existing[k] = z[k]
    print(f'[resume] cached embeddings: {len(existing)}')

recs = []
for h, s in parse_fasta(FASTA):
    parts = h.split('|')
    if len(parts) >= 2:
        acc = parts[1]
    else:
        acc = h.split()[0]
    if acc in existing:
        continue
    seq = s[:MAX_LEN]
    recs.append((acc, seq, h))
print(f'[todo] {len(recs)} proteins to embed')

if not recs:
    print('[done] nothing to do')
    sys.exit(0)

from transformers import AutoTokenizer, AutoModel
print(f'[load] {MODEL_NAME}')
tok = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)
dev = 'cuda' if torch.cuda.is_available() else 'cpu'
if dev == 'cuda':
    model = model.to(dev).half()
else:
    model = model.to(dev)
model.requires_grad_(False)
model.train(False)
print(f'[device] {dev}')

meta_f = open(META_OUT, 'a')
if os.stat(META_OUT).st_size == 0:
    meta_f.write('accession\theader\tseq_len\n')

BATCH = 4
t0 = time.time()
written_since_flush = 0
FLUSH_EVERY = 100
recs.sort(key=lambda r: len(r[1]))


def flush():
    np.savez_compressed(OUT, **existing)


for i in range(0, len(recs), BATCH):
    batch = recs[i:i+BATCH]
    seqs = [r[1] for r in batch]
    accs = [r[0] for r in batch]
    headers = [r[2] for r in batch]
    enc = tok(seqs, return_tensors='pt', padding=True, truncation=True, max_length=MAX_LEN + 2)
    enc = {k: v.to(dev) for k, v in enc.items()}
    with torch.no_grad():
        out = model(**enc)
    hs = out.last_hidden_state
    mask = enc['attention_mask'].unsqueeze(-1).float()
    pooled = (hs * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)
    pooled = pooled.float().cpu().numpy()
    for acc, h, s, v in zip(accs, headers, seqs, pooled):
        existing[acc] = v.astype(np.float32)
        meta_f.write(f'{acc}\t{h}\t{len(s)}\n')
    written_since_flush += len(batch)
    if written_since_flush >= FLUSH_EVERY:
        flush()
        meta_f.flush()
        dt = time.time() - t0
        done_now = len(existing)
        rate = (i + BATCH) / max(1, dt)
        remain = (len(recs) - (i + BATCH)) / max(1, rate)
        print(f'[{i+BATCH}/{len(recs)}] cached={done_now} rate={rate:.2f}/s eta={remain/60:.1f}min', flush=True)
        written_since_flush = 0

flush()
meta_f.close()
print(f'[done] total cached: {len(existing)}, elapsed: {(time.time()-t0)/60:.1f}min')

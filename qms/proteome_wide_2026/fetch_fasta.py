#!/usr/bin/env python3
"""Fetch UniProt FASTA sequences for a list of accessions in chunks."""
import requests, time, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

with open('uniprot_ids.txt') as f:
    ids = [l.strip() for l in f if l.strip()]
print('total:', len(ids), flush=True)

fasta_path = 'mn_proteome.fasta'
done = set()
if os.path.exists(fasta_path):
    with open(fasta_path) as f:
        for line in f:
            if line.startswith('>'):
                parts = line.split('|')
                if len(parts) >= 2:
                    done.add(parts[1])
print('cached:', len(done), flush=True)

todo = [i for i in ids if i not in done]
print('todo:', len(todo), flush=True)

CHUNK = 50
out = open(fasta_path, 'a')
ok = 0
fail = 0
failed_accs = []

for i in range(0, len(todo), CHUNK):
    chunk = todo[i:i+CHUNK]
    q = ' OR '.join(f'accession:{a}' for a in chunk)
    try:
        r = requests.get(
            'https://rest.uniprot.org/uniprotkb/search',
            params={'query': q, 'format': 'fasta', 'size': 500},
            timeout=60,
        )
        if r.status_code == 200 and r.text.startswith('>'):
            out.write(r.text)
            out.flush()
            n = r.text.count('\n>') + 1
            ok += n
            if (i // CHUNK) % 20 == 0:
                print(f'chunk {i//CHUNK+1}/{(len(todo)+CHUNK-1)//CHUNK} +{n} (ok={ok} fail={fail})', flush=True)
        else:
            fail += len(chunk)
            failed_accs.extend(chunk)
            if fail < 200:
                print(f'chunk FAIL status={r.status_code} first_body={r.text[:120]!r}', flush=True)
    except Exception as e:
        fail += len(chunk)
        failed_accs.extend(chunk)
        print(f'err {e}', flush=True)
    time.sleep(0.2)

out.close()
with open('failed_accs.txt', 'w') as f:
    for a in failed_accs:
        f.write(a + '\n')
print(f'DONE ok={ok} fail={fail}', flush=True)

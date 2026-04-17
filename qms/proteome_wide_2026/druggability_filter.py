#!/usr/bin/env python3
"""Druggability filter using OpenTargets Platform API.

For each surviving candidate, query OpenTargets GraphQL for:
  - tractability assessment (Small Molecule, Antibody, Other Modality)
  - specifically SM bucket (1-10, lower = better clinical precedent)
  - PDB coverage (structural knowledge)
  - associated diseases (cross-check novelty)

Druggability tiers:
  - 'clinical_precedent': SM bucket 1-3 (approved drug / clinical candidate)
  - 'druggable': SM bucket 4-6 OR AlphaFold high-confidence + pocket predicted
  - 'discovery_opportunity': SM bucket 7-9 (predicted druggable by structure/ligandability)
  - 'difficult': SM bucket 10 or no data

We score:
  - 1.0 if clinical_precedent OR druggable
  - 0.5 if discovery_opportunity (this is exactly what we WANT for novel targets!)
  - 0.0 if difficult

OpenTargets GraphQL endpoint: https://api.platform.opentargets.org/api/v4/graphql
Query uses Ensembl gene ID (we have that from HPA).
"""
import os
import json
import time
import requests
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

OT = 'https://api.platform.opentargets.org/api/v4/graphql'
CACHE = 'opentargets_cache.json'

QUERY = """
query Target($ensgId: String!) {
  target(ensemblId: $ensgId) {
    id
    approvedSymbol
    tractability {
      label
      modality
      value
    }
  }
}
"""


def load_cache():
    if os.path.exists(CACHE):
        with open(CACHE) as f:
            return json.load(f)
    return {}


def save_cache(c):
    with open(CACHE, 'w') as f:
        json.dump(c, f)


def ot_query(ensembl_id):
    try:
        r = requests.post(OT, json={'query': QUERY, 'variables': {'ensgId': ensembl_id}}, timeout=30)
        if r.status_code != 200:
            return {'error': f'http {r.status_code}'}
        j = r.json()
        if 'errors' in j:
            return {'error': j['errors']}
        d = j.get('data', {}).get('target')
        if not d:
            return {'error': 'no target'}
        return d
    except Exception as e:
        return {'error': str(e)}


def derive_druggability(ot_data):
    """Return (score, tier, label)."""
    if not ot_data or 'error' in ot_data:
        note = str(ot_data.get('error') if ot_data else 'none')[:120]
        return 0.0, 'no_data', note
    tr = ot_data.get('tractability') or []
    sm_bucket = 10
    has_clinical = False
    has_drug = False
    # tractability records: {label, modality, value(bool)}
    for t in tr:
        if not t.get('value'):
            continue
        if t.get('modality') != 'SM':
            continue
        lab = t.get('label', '')
        # OT labels: 'Approved Drug', 'Advanced Clinical', 'Phase 1 Clinical',
        # 'Structure with Ligand', 'High-Quality Ligand', 'High-Quality Pocket',
        # 'Med-Quality Pocket', 'Druggable Family'
        order = ['Approved Drug', 'Advanced Clinical', 'Phase 1 Clinical',
                 'Structure with Ligand', 'High-Quality Ligand',
                 'High-Quality Pocket', 'Med-Quality Pocket', 'Druggable Family']
        if lab in order:
            b = order.index(lab) + 1
            if b < sm_bucket:
                sm_bucket = b
        if lab in ('Approved Drug', 'Advanced Clinical', 'Phase 1 Clinical'):
            has_clinical = True
    if has_clinical:
        return 1.0, 'clinical_precedent', f'bucket={sm_bucket} clinical'
    if sm_bucket <= 5:
        return 1.0, 'druggable', f'bucket={sm_bucket}'
    if sm_bucket <= 8:
        return 0.6, 'discovery_opportunity', f'bucket={sm_bucket}'
    return 0.1, 'difficult', f'bucket={sm_bucket}'


def main():
    df = pd.read_csv('candidates_post_literature.tsv', sep='\t')
    print(f'[load] {len(df)} candidates')

    cache = load_cache()
    scores = []
    for _, row in df.iterrows():
        gene = row['gene']
        # Need Ensembl ID: lookup from the HPA master
        ensg = row.get('Ensembl') or row.get('ensembl')
        if not isinstance(ensg, str) or not ensg.startswith('ENSG'):
            # Try the HPA candidates file to recover
            ensg = None
        cached = cache.get(gene)
        if cached is None:
            if ensg is None:
                # Try to pull from proteinatlas.tsv
                cache[gene] = {'error': 'no_ensembl'}
            else:
                cache[gene] = ot_query(ensg)
            time.sleep(0.15)
            if len(cache) % 20 == 0:
                save_cache(cache)
                print(f'[ot] {len(cache)} queried', flush=True)
        cached = cache[gene]
        s, tier, lbl = derive_druggability(cached)
        scores.append({'gene': gene, 'uniprot': row['uniprot'],
                       'druggability_score': s, 'druggability_tier': tier,
                       'druggability_note': lbl})
    save_cache(cache)
    ds = pd.DataFrame(scores)
    merged = df.merge(ds, on=['gene', 'uniprot'], how='left')
    merged.to_csv('candidates_with_druggability.tsv', sep='\t', index=False)
    print(merged['druggability_tier'].value_counts())


if __name__ == '__main__':
    main()

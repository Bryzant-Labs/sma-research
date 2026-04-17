#!/usr/bin/env python3
"""Count SMA-specific PubMed hits per gene, flag over-studied targets.

For each top-N candidate, query NCBI EUtils esearch with:
  ("<GENE>"[tw] OR "<OFFICIAL_SYMBOL>"[tw]) AND ("spinal muscular atrophy"[tw] OR "SMA"[tw])

Cache results to pubmed_cache.json to avoid re-querying.
Rate-limited to NCBI's 3 rps (no API key) or 10 rps (with NCBI_API_KEY env var).

Flag filter:
  - n_papers >  5  => OVER-STUDIED, mark 'excluded_overstudied=True'
  - n_papers >= 1  => 'some_prior_work'
  - n_papers == 0  => 'truly_novel'
"""
import os
import json
import time
import requests
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

CACHE = 'pubmed_cache.json'
TOP_N = 500

NCBI_API = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
API_KEY = os.environ.get('NCBI_API_KEY')


def count_pubmed(gene):
    q = f'("{gene}"[Title/Abstract]) AND ("spinal muscular atrophy"[Title/Abstract] OR SMA[Title/Abstract])'
    params = {'db': 'pubmed', 'term': q, 'retmode': 'json', 'retmax': 0}
    if API_KEY:
        params['api_key'] = API_KEY
    r = requests.get(NCBI_API, params=params, timeout=20)
    if r.status_code != 200:
        return None
    j = r.json()
    try:
        return int(j['esearchresult']['count'])
    except Exception:
        return None


def load_cache():
    if os.path.exists(CACHE):
        with open(CACHE) as f:
            return json.load(f)
    return {}


def save_cache(c):
    with open(CACHE, 'w') as f:
        json.dump(c, f)


def main():
    df = pd.read_csv('candidates_scored.tsv', sep='\t')
    # Exclude anchors themselves (they have infinite SMA papers by definition) and protein-names that are too generic
    df = df[~df['is_anchor']].copy()
    df = df[df['gene'].notna()].copy()
    # Skip very short symbols that would produce false-positive hits
    df = df[df['gene'].str.len() >= 3].copy()
    cand = df.head(TOP_N)
    print(f'[filter] running PubMed on top {len(cand)}')

    cache = load_cache()
    rate = 0.34 if not API_KEY else 0.11
    new_count = 0
    for gene in cand['gene']:
        if gene in cache:
            continue
        n = count_pubmed(gene)
        cache[gene] = n if n is not None else -1
        new_count += 1
        if new_count % 25 == 0:
            save_cache(cache)
            print(f'[pubmed] {new_count} / {len(cand)} queried (last: {gene} -> {n})', flush=True)
        time.sleep(rate)
    save_cache(cache)
    print(f'[pubmed] total cached: {len(cache)}')

    df['sma_papers'] = df['gene'].map(cache).fillna(-1).astype(int)
    # classify
    def bucket(n):
        if n < 0:
            return 'query_failed'
        if n == 0:
            return 'truly_novel'
        if n <= 5:
            return 'some_prior_work'
        return 'over_studied'
    df['novelty_bucket'] = df['sma_papers'].apply(bucket)
    df.to_csv('candidates_with_literature.tsv', sep='\t', index=False)
    print('[write] candidates_with_literature.tsv')
    print(df['novelty_bucket'].value_counts())

    # Top 50 novel + signature-scored
    surv = df[df['novelty_bucket'].isin(['truly_novel', 'some_prior_work'])].head(500)
    surv.to_csv('candidates_post_literature.tsv', sep='\t', index=False)
    print(f'[survivors] post-literature filter: {len(surv)}')


if __name__ == '__main__':
    main()

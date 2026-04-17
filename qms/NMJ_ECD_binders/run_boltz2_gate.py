#!/usr/bin/env python3
"""Boltz-2 self-hosted gate pipeline for NMJ ECD binder survivors.

For each pLDDT>=0.70 survivor from round 1, compute Boltz-2 iptm of:
  binder + target_scaffold  (single target — round-1 intent)

Uses self-hosted Boltz-2 batched server at sma-h100-two:8003 (NIM-compat schema).
Falls back to free NIM if self-host unavailable.

Gate: complex_iptm > 0.5 (Boltz-2 iptm for 2-chain complex)
Output: /home/bryza/sma-research/qms/NMJ_ECD_binders/TOP_GATE_PASSERS.tsv
"""
import json, sys, time, urllib.request, urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

RESULTS_ROOT = Path("/home/bryza/fleet-results/nmj_ecd_binders_35134656/nmj_ecd_binders")
OUT = Path("/home/bryza/sma-research/qms/NMJ_ECD_binders")
OUT.mkdir(parents=True, exist_ok=True)

SELF_HOSTED = "http://sma-h100-two:8003/predict"

# Target scaffold sequences — extracted from receptor PDBs (chain A/B as used in rfdiff)
def load_target_seqs():
    """Return {target: (chain_id, sequence)} from the receptor PDBs."""
    import string
    three_to_one = {
        'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLU':'E','GLN':'Q','GLY':'G',
        'HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P','SER':'S',
        'THR':'T','TRP':'W','TYR':'Y','VAL':'V','SEC':'U','PYL':'O','MSE':'M',
    }
    config = {
        'MuSK':   ('2IEP', 'A'),
        'LRP4':   ('3V64', 'A'),
        'DOK7':   ('3ML4', 'A'),
        'CHRNA1': ('2QC1', 'B'),
    }
    seqs = {}
    for t, (pdb, chain) in config.items():
        p = Path('/home/bryza/fleet-results/nmj_ecd_binders_35134656/') / f'{pdb}.pdb'
        rs = {}  # residue_num -> aa
        for line in p.read_text().splitlines():
            if line.startswith('ATOM') and line[13:15]=='CA' and line[21]==chain:
                r = int(line[22:26].strip())
                aa3 = line[17:20]
                rs[r] = three_to_one.get(aa3, 'X')
        # return as contiguous by residue number (with gaps left out — Boltz handles)
        if rs:
            nums = sorted(rs)
            seq = ''.join(rs[n] for n in nums)
            seqs[t] = (chain, seq)
            print(f"[{t}] chain {chain}: {len(seq)} aa ({nums[0]}-{nums[-1]})", flush=True)
    return seqs

def load_survivors(target):
    fa = RESULTS_ROOT / target / 'binders_survivors.fasta'
    if not fa.exists() or fa.stat().st_size == 0:
        return []
    items = []
    lines = fa.read_text().splitlines()
    for i in range(0, len(lines)-1, 2):
        hdr = lines[i].lstrip('>')
        seq = lines[i+1]
        # parse plddt from header
        plddt = 0.0
        for tok in hdr.split('|'):
            if tok.startswith('plddt='):
                try: plddt = float(tok.split('=')[1])
                except: pass
        items.append({'id': hdr.split('|')[0], 'seq': seq, 'plddt': plddt, 'target': target})
    return items

def boltz2_predict(binder_seq, target_seq, timeout=600):
    body = {
        "polymers": [
            {"id": "B", "molecule_type": "protein", "sequence": binder_seq},
            {"id": "A", "molecule_type": "protein", "sequence": target_seq},
        ],
        "ligands": [],
        "recycling_steps": 1,
        "sampling_steps": 25,
    }
    data = json.dumps(body).encode()
    req = urllib.request.Request(SELF_HOSTED, data=data, headers={"Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read())
        elapsed = time.time() - t0
        iptm = payload.get("iptm_scores", [0.0])[0]
        ptm = payload.get("ptm_scores", [0.0])[0]
        plddt = payload.get("complex_plddt_scores", [0.0])[0]
        return {"iptm": iptm, "ptm": ptm, "plddt": plddt, "elapsed": elapsed, "ok": True}
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": f"HTTP {e.code}: {e.read()[:200]}"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}

def main():
    target_seqs = load_target_seqs()
    all_items = []
    for t in ['MuSK','LRP4','DOK7','CHRNA1']:
        items = load_survivors(t)
        print(f"[{t}] {len(items)} survivors to gate", flush=True)
        all_items.extend(items)

    if not all_items:
        print("NO SURVIVORS — nothing to gate", flush=True)
        return

    # health check
    try:
        with urllib.request.urlopen(SELF_HOSTED.replace('/predict','/health'), timeout=10) as r:
            hc = r.read()[:200]
            print(f"self-host health: {hc}", flush=True)
    except Exception as e:
        print(f"self-host DOWN: {e} — ABORT (NIM fallback needs different schema)", flush=True)
        return

    results = []
    passers = []
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {}
        for it in all_items:
            tgt_chain, tgt_seq = target_seqs[it['target']]
            fut = ex.submit(boltz2_predict, it['seq'], tgt_seq)
            futs[fut] = it
        for i, fut in enumerate(as_completed(futs)):
            it = futs[fut]
            try:
                res = fut.result()
            except Exception as e:
                res = {'ok': False, 'error': str(e)[:200]}
            rec = {**it, 'boltz2': res}
            results.append(rec)
            if res.get('ok') and res.get('iptm', 0) > 0.5:
                passers.append(rec)
            if i % 10 == 0:
                print(f"  [{i}/{len(futs)}] iptm={res.get('iptm','?')} ok={res.get('ok')}", flush=True)

    (OUT / 'boltz2_all_results.json').write_text(json.dumps(results, indent=2))
    with (OUT / 'TOP_GATE_PASSERS.tsv').open('w') as f:
        f.write("design_id\ttarget\tplddt_esm\tiptm_boltz2\tptm_boltz2\tplddt_boltz2\tbinder_seq\n")
        for r in sorted(passers, key=lambda x: -x['boltz2']['iptm']):
            b = r['boltz2']
            f.write(f"{r['id']}\t{r['target']}\t{r['plddt']:.3f}\t{b['iptm']:.3f}\t{b['ptm']:.3f}\t{b['plddt']:.3f}\t{r['seq']}\n")
    print(f"\n=== GATE SUMMARY ===", flush=True)
    print(f"Total survivors evaluated: {len(results)}", flush=True)
    print(f"Passed iptm>0.5 gate:      {len(passers)}", flush=True)
    for t in ['MuSK','LRP4','DOK7','CHRNA1']:
        n_t = sum(1 for r in results if r['target']==t)
        n_p = sum(1 for r in passers if r['target']==t)
        print(f"  {t}: {n_p}/{n_t}", flush=True)

if __name__ == '__main__':
    main()

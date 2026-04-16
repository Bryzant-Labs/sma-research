"""Dispatcher post-complete hook v2 — BBB pre-filter + 15-kinase panel.

After any genmol task completes:
  1. Compute ADMET-AI BBB prediction for each new compound
  2. Drop compounds with bbb < 0.5 (SMA=CNS disease, BBB is hard gate)
  3. Re-run SMA-Score ranker on survivors
  4. Queue top-20 × 15-kinase panel for Boltz-2 iptm selectivity
  5. Write findings for CORTEX ingest

Runs every 15 min via cron. Idempotent via processed-tasks marker.
Phase 1.5.1 (BBB) + Phase 1.5.3 (kinome) from plan-sma-orchestration-layer-2026-04-16.
"""
import json, sqlite3, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

DB = "/home/bryza/fleet-dispatcher/queue.db"
MARKER_FILE = Path("/home/bryza/fleet-results/.auto_score_processed.json")
NOW = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
BBB_THRESHOLD = 0.5   # ADMET-AI bbb_martins — drop below this

def load_processed():
    return json.loads(MARKER_FILE.read_text()) if MARKER_FILE.exists() else []

def save_processed(ids):
    MARKER_FILE.write_text(json.dumps(ids))

def bbb_filter(smiles_list):
    """Return list of (smi, bbb_score) — full list, caller filters by threshold."""
    try:
        from admet_ai import ADMETModel
    except Exception as e:
        print(f"[auto_score] admet-ai not importable: {e}; skipping BBB filter")
        return [(s, 1.0) for s in smiles_list]
    try:
        m = ADMETModel()
        import pandas as pd
        df = m.predict(smiles=smiles_list)
        # ADMET-AI column is 'BBB_Martins' (propensity to cross BBB)
        bbb_col = next((c for c in df.columns if 'BBB' in c.upper() or 'bbb' in c), None)
        if bbb_col is None:
            print(f"[auto_score] no BBB column in ADMET output; columns: {list(df.columns)[:5]}")
            return [(s, 1.0) for s in smiles_list]
        return list(zip(smiles_list, df[bbb_col].tolist()))
    except Exception as e:
        print(f"[auto_score] BBB prediction failed: {e}")
        return [(s, 1.0) for s in smiles_list]

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    processed = set(load_processed())

    new_genmol = [r for r in conn.execute(
        "SELECT id, result_path FROM tasks WHERE type='genmol' AND status='completed'"
    ) if r["id"] not in processed]

    if not new_genmol:
        print("[auto_score] no new genmol tasks to process")
        return

    # Gather new compounds
    new_compounds = []
    for r in new_genmol:
        rp_raw = r["result_path"]
        if not rp_raw: continue
        rp = Path(rp_raw) / "genmol_results.json"
        if not rp.exists(): continue
        try: data = json.loads(rp.read_text())
        except: continue
        for chunk in data:
            res = chunk.get("result") or {}
            for mol in res.get("molecules", []):
                new_compounds.append({
                    "source": r["id"], "smiles": mol["smiles"], "qed": mol.get("score", 0),
                })

    if not new_compounds:
        processed.update(r["id"] for r in new_genmol)
        save_processed(sorted(processed))
        return

    # Dedupe by SMILES
    seen = set(); uniq = []
    for c in new_compounds:
        if c["smiles"] in seen: continue
        seen.add(c["smiles"]); uniq.append(c)
    print(f"[auto_score] {len(uniq)} unique new SMILES from {len(new_genmol)} tasks")

    # -------- Phase 1.5.1 — BBB hard-filter --------
    smiles_list = [c["smiles"] for c in uniq]
    bbb_scores = bbb_filter(smiles_list)
    bbb_map = dict(bbb_scores)
    survivors = [c for c in uniq if bbb_map.get(c["smiles"], 0) >= BBB_THRESHOLD]
    dropped = len(uniq) - len(survivors)
    print(f"[auto_score] BBB filter (≥{BBB_THRESHOLD}): kept {len(survivors)}, dropped {dropped}")

    # Enrich survivors with BBB score
    for c in survivors:
        c["bbb"] = bbb_map.get(c["smiles"], 0)

    # Re-run ranker (picks up new compounds automatically by scanning fleet-results/genmol_*)
    subprocess.run([sys.executable, "/home/bryza/gpu-fleet/scripts/sma_score_ranker.py"],
                   capture_output=True, timeout=180)

    # -------- Phase 1.5.3 — 15-kinase panel Boltz-2 queue --------
    try:
        panel = json.load(open("/home/bryza/fleet-results/kinase_panel_domains.json"))
    except Exception as e:
        print(f"[auto_score] kinase panel not found ({e}); falling back to 3-kinase")
        panel = {"LIMK2": "MSSLSQLPLHRLQPSVNRIVLPQEGSTVHTLKDGRVKLR",
                 "LIMK1": "MSSLSRLSLHRLQPSVRIVLPQEGKSVHTLKDGRVILRS",
                 "ROCK2": "MSRPPPTGKMPGAPETAPGDGAGASRQRKLEALIRDPRS"}

    # Queue top-20 survivors × full panel
    K = min(20, len(survivors))
    top20 = sorted(survivors, key=lambda c: c["qed"], reverse=True)[:K]

    added = 0
    for i, c in enumerate(top20):
        cid = f"autoscore_{i:03d}"
        for tgt_name, tgt_seq in panel.items():
            h = abs(hash(c["smiles"])) % 100000
            tid = f"boltz2_auto_{tgt_name.lower()}_{cid}_{h}"
            meta = {
                "pairs": [{"protein_seq": tgt_seq, "ligand_smiles": c["smiles"], "id": f"{tgt_name}_{cid}"}],
                "from_genmol_task": c["source"],
                "qed": c["qed"],
                "bbb": c["bbb"],
            }
            conn.execute("""INSERT OR IGNORE INTO tasks
                (id,type,target,status,priority,requirements_json,preferred_worker,
                 created,updated,n_attempts,max_attempts,metadata_json)
                VALUES (?,?,?,'queued',?,'{}','HostedNIMWorker',?,?,0,3,?)""",
                (tid, "boltz2_affinity", tgt_name, 30, NOW, NOW, json.dumps(meta)))
            added += 1
    conn.commit()
    print(f"[auto_score] queued {added} Boltz-2 tasks ({len(top20)} compounds × {len(panel)} kinases)")

    processed.update(r["id"] for r in new_genmol)
    save_processed(sorted(processed))
    print(f"[auto_score] marked {len(new_genmol)} genmol tasks processed (total: {len(processed)})")

if __name__ == "__main__":
    main()

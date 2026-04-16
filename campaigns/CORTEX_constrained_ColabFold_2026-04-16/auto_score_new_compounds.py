"""Dispatcher post-complete hook: after any genmol task completes, auto-queue
Boltz-2 + SMA-Score for its new compounds. Writes findings back to CORTEX.

Runs every 5 min via cron. Idempotent via a processed-tasks marker.
"""
import json, sqlite3, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

DB = "/home/bryza/fleet-dispatcher/queue.db"
MARKER_FILE = Path("/home/bryza/fleet-results/.auto_score_processed.json")
RANKER_OUT = Path("/home/bryza/fleet-results/sma_score/candidates_ranked.csv")
NOW = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")

# Truncated ref seqs (same as used elsewhere — short enough for quick Boltz-2 probe)
LIMK2 = "MSSLSQLPLHRLQPSVNRIVLPQEGSTVHTLKDGRVKLR"
LIMK1 = "MSSLSRLSLHRLQPSVRIVLPQEGKSVHTLKDGRVILRS"
ROCK2 = "MSRPPPTGKMPGAPETAPGDGAGASRQRKLEALIRDPRS"

def load_processed():
    return json.loads(MARKER_FILE.read_text()) if MARKER_FILE.exists() else []

def save_processed(ids):
    MARKER_FILE.write_text(json.dumps(ids))

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    processed = set(load_processed())

    # Find genmol tasks completed but not yet auto-scored
    new_genmol = [r for r in conn.execute(
        "SELECT id, result_path FROM tasks WHERE type='genmol' AND status='completed'"
    ) if r["id"] not in processed]

    if not new_genmol:
        print("[auto_score] no new genmol to process")
        return

    # Collect new compounds from those tasks
    new_compounds = []
    for r in new_genmol:
        rp = Path(r["result_path"]) / "genmol_results.json"
        if not rp.exists(): continue
        try: data = json.loads(rp.read_text())
        except: continue
        for chunk in data:
            res = chunk.get("result") or {}
            for mol in res.get("molecules", []):
                new_compounds.append({
                    "source": r["id"],
                    "smiles": mol["smiles"],
                    "qed": mol.get("score", 0),
                })
    if not new_compounds:
        print(f"[auto_score] found {len(new_genmol)} tasks but no new SMILES")
        return

    # Re-run ranker (includes the new compounds) — cheap, seconds
    print(f"[auto_score] rerunning ranker on {len(new_compounds)} new + existing compounds")
    subprocess.run([sys.executable, "/home/bryza/gpu-fleet/scripts/sma_score_ranker.py"],
                   capture_output=True, timeout=120)

    # Queue Boltz-2 iptm for top-K new compounds against LIMK2/LIMK1/ROCK2
    K = min(20, len(new_compounds))
    # Dedupe by SMILES
    seen = set(); uniq = []
    for c in new_compounds:
        if c["smiles"] in seen: continue
        seen.add(c["smiles"]); uniq.append(c)
    uniq = sorted(uniq, key=lambda c: c["qed"], reverse=True)[:K]

    added = 0
    for i, c in enumerate(uniq):
        cid = f"autoscore_{i:03d}"
        for tgt_name, tgt_seq in [("LIMK2", LIMK2), ("LIMK1", LIMK1), ("ROCK2", ROCK2)]:
            tid = f"boltz2_auto_{tgt_name.lower()}_{cid}_{abs(hash(c['smiles']))%10000}"
            meta = {
                "pairs": [{"protein_seq": tgt_seq, "ligand_smiles": c["smiles"], "id": f"{tgt_name}_{cid}"}],
                "from_genmol_task": c["source"], "qed": c["qed"],
            }
            conn.execute("""INSERT OR IGNORE INTO tasks
                (id,type,target,status,priority,requirements_json,preferred_worker,
                 created,updated,n_attempts,max_attempts,metadata_json)
                VALUES (?,?,?,'queued',?,'{}','HostedNIMWorker',?,?,0,3,?)""",
                (tid, "boltz2_affinity", tgt_name, 30, NOW, NOW, json.dumps(meta)))
            added += 1
    conn.commit()
    print(f"[auto_score] queued {added} Boltz-2 tasks from {len(uniq)} new compounds")

    # Mark genmol tasks as processed
    processed.update(r["id"] for r in new_genmol)
    save_processed(sorted(processed))
    print(f"[auto_score] marked {len(new_genmol)} genmol tasks as processed")

    # Writeback summary to CORTEX would happen here via MCP — deferred to separate cron
    # (CORTEX MCP only available in interactive Claude sessions, not cron)

if __name__ == "__main__":
    main()

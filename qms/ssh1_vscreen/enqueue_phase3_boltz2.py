#!/usr/bin/env python3
"""
Enqueue Phase 3 Boltz-2 cross-phosphatase rescore for SSH1 vscreen.

Enqueues 100 compounds × 4 targets = 400 tasks (or batched) to the fleet queue
(`~/fleet-dispatcher/queue.db`). Each task is a boltz2_affinity task with
metadata_json holding `{"pairs": [...]}` matching the worker schema.

We batch 10 compounds per task (same target) to reduce NIM overhead. → 40 tasks total.
"""
import csv
import json
import sqlite3
import uuid
from pathlib import Path
from datetime import datetime, timezone

DB = Path.home() / "fleet-dispatcher" / "queue.db"
ROOT = Path("/home/bryza/sma-research/qms/ssh1_vscreen")
SEQS = json.load(open(ROOT / "target_sequences.json"))
# SEQS dict: {'SSH1': seq, 'SSH2': seq, 'SSH3': seq, 'DUSP6': seq}

compounds = list(csv.DictReader(open(ROOT / "top100_druglike.tsv"), delimiter="\t"))
print(f"compounds loaded: {len(compounds)}")

BATCH = 10  # compounds per task
PRIO = 40   # higher than autoscore (50), lower than manual (30)

def iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

targets = ["SSH1", "SSH2", "SSH3", "DUSP6"]
rows_to_insert = []
run_tag = "ssh1vscreen_phase3_" + uuid.uuid4().hex[:6]

for tgt in targets:
    prot_seq = SEQS[tgt]
    for i in range(0, len(compounds), BATCH):
        batch = compounds[i : i + BATCH]
        pairs = []
        for c in batch:
            pairs.append({
                "protein_seq": prot_seq,
                "ligand_smiles": c["smiles"],
                "id": f"{tgt}_{c['chembl_id']}",
            })
        task_id = f"boltz2_{run_tag}_{tgt}_b{i//BATCH:02d}"
        meta = {
            "pairs": pairs,
            "campaign": "ssh1_vscreen",
            "phase": 3,
            "target_set": "SSH1+SSH2+SSH3+DUSP6",
            "run_tag": run_tag,
            "source": "diffdock_top100_druglike",
        }
        rows_to_insert.append((
            task_id, "boltz2_affinity", tgt, "queued", PRIO,
            json.dumps({}), None, None, None, iso(), iso(),
            None, None, 0, 3, None, None, json.dumps(meta),
        ))

print(f"tasks to enqueue: {len(rows_to_insert)}")
print(f"  {len(targets)} targets × {len(compounds)//BATCH + (1 if len(compounds)%BATCH else 0)} batches of {BATCH}")

# INSERT
c = sqlite3.connect(str(DB))
cur = c.cursor()
cur.executemany("""
INSERT INTO tasks
 (id, type, target, status, priority,
  requirements_json, preferred_worker, assigned_worker, assigned_gpu,
  created, updated,
  deployed_at, completed_at, n_attempts, max_attempts,
  result_path, error, metadata_json)
VALUES (?, ?, ?, ?, ?,  ?, ?, ?, ?,  ?, ?,  ?, ?, ?, ?,  ?, ?, ?)
""", rows_to_insert)
c.commit()
c.close()
print(f"enqueued run_tag={run_tag}")
print(f"monitor: sqlite3 {DB} \"SELECT status, COUNT(*) FROM tasks WHERE id LIKE '%{run_tag}%' GROUP BY status\"")

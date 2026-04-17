#!/usr/bin/env python3
"""
Enqueue Phase 3 Boltz-2 cross-phosphatase rescore for SSH2 vscreen.

Priority target is SSH2 (primary). Panel = SSH1/SSH2/SSH3/DUSP6 for selectivity
z-scoring. 100 compounds × 4 targets = 400 pairs, batched 10/task = 40 tasks.

Free NIM tier (per rule — no local Boltz-2 on this H100).
"""
import csv
import json
import sqlite3
import uuid
from pathlib import Path
from datetime import datetime, timezone

DB = Path.home() / "fleet-dispatcher" / "queue.db"
ROOT = Path("/home/bryza/sma-research/qms/ssh2_vscreen")
# Target sequences are reused from SSH1 vscreen
SEQS = json.load(open(Path.home() / "sma-research/qms/ssh1_vscreen/target_sequences.json"))

compounds = list(csv.DictReader(open(ROOT / "top100_druglike.tsv"), delimiter="\t"))
print(f"compounds loaded: {len(compounds)}")

BATCH = 10
PRIO = 40

def iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

targets = ["SSH2", "SSH1", "SSH3", "DUSP6"]  # SSH2 first = primary
rows_to_insert = []
run_tag = "ssh2vscreen_phase3_" + uuid.uuid4().hex[:6]

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
            "campaign": "ssh2_vscreen",
            "phase": 3,
            "target_set": "SSH2+SSH1+SSH3+DUSP6",
            "run_tag": run_tag,
            "source": "diffdock_top100_druglike",
            "primary_target": "SSH2",
        }
        rows_to_insert.append((
            task_id, "boltz2_affinity", tgt, "queued", PRIO,
            json.dumps({}), None, None, None, iso(), iso(),
            None, None, 0, 3, None, None, json.dumps(meta),
        ))

print(f"tasks to enqueue: {len(rows_to_insert)}")
print(f"  {len(targets)} targets × {len(compounds)//BATCH + (1 if len(compounds)%BATCH else 0)} batches of {BATCH}")

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

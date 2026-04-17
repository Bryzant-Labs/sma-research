#!/usr/bin/env python3
"""Pick top-3 candidates for 25 ns MD simulation.

Criteria (weighted):
  1. If Boltz-2 panel complete → use z_primary + sel_z
  2. Else → use cfd_pos × QED × BBB_score (from Phase-4 filter output)

Writes md_candidates.tsv ready to feed into MD task generator.
"""
import csv
from pathlib import Path

CASCADE = Path("/home/bryza/sma-research/qms/proteome_wide_2026/cascade_extended_output")
OUT = Path("/home/bryza/sma-research/qms/proteome_wide_2026/md_candidates.tsv")
TARGETS = ["EP400", "PEAK1", "KAT7", "RNF213", "EHMT2", "KAT6A", "KAT5", "KMT5B", "EHMT1"]


def main():
    # Try to read Boltz-2 combined first
    combined = CASCADE / "cross_target_top_hits.csv"
    candidates = []
    use_boltz = combined.exists() and combined.stat().st_size > 100
    if use_boltz:
        with open(combined) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        # Rank by selectivity_z
        scored = [(r, float(r["selectivity_z"]) if r.get("selectivity_z") and r["selectivity_z"] != "" else -99) for r in rows]
        scored.sort(key=lambda x: -x[1])
        for r, s in scored[:3]:
            candidates.append({
                "target": r["primary_target"],
                "compound_id": r["compound_id"],
                "smiles": "<fill>",  # SMILES is in top100 tsv; join below
                "selectivity_z": s,
                "z_primary": r.get("z_primary", ""),
                "method": "boltz2_sel_z",
            })
    else:
        # Fall back to PXM cfd_pos × QED × BBB composite
        per_target_top = []
        for tgt in TARGETS:
            tsv = CASCADE / f"top100_{tgt}.tsv"
            if not tsv.exists():
                continue
            with open(tsv) as f:
                reader = csv.DictReader(f, delimiter="\t")
                for row in reader:
                    try:
                        score = (float(row["cfd_pos"]) * float(row["qed"]) *
                                 (float(row["bbb_score"]) if row["bbb_score"] else 0.5))
                    except Exception:
                        continue
                    per_target_top.append({
                        "target": tgt,
                        "compound_id": f"{tgt}_r{row.get('rank','?')}",
                        "filename": row["filename"],
                        "smiles": row["smiles"],
                        "cfd_pos": row["cfd_pos"],
                        "qed": row["qed"],
                        "bbb_score": row["bbb_score"],
                        "composite": score,
                        "method": "pxm_composite",
                    })
                    break  # just take #1 per target for diversity
        per_target_top.sort(key=lambda x: -x["composite"])
        candidates = per_target_top[:3]

    if not candidates:
        print("No candidates")
        return

    # Write
    keys = sorted({k for c in candidates for k in c.keys()})
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, delimiter="\t")
        w.writeheader()
        for c in candidates:
            w.writerow(c)
    print(f"Wrote {OUT}")
    for c in candidates:
        print(f"  {c.get('target','?'):8s} {c.get('compound_id','?'):20s} method={c.get('method')}")
        print(f"     SMILES: {c.get('smiles', '')[:80]}")


if __name__ == "__main__":
    main()

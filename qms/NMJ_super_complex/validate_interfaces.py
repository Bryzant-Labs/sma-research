#!/usr/bin/env python3
"""
Validate the NMJ super-complex assembly:
  - Count inter-chain CA contacts (5 A cutoff) between every chain pair
  - Summarize pLDDT distribution per chain
  - Detect clashes (< 2.5 A non-bonded heavy-atom contacts across chains)
"""
from __future__ import annotations
import json
from pathlib import Path
from collections import defaultdict
import numpy as np
from Bio.PDB import PDBParser

ROOT = Path("/home/bryza/sma-research/qms/NMJ_super_complex")
PDB = ROOT / "assembly" / "nmj_super_complex.pdb"

parser = PDBParser(QUIET=True)
s = parser.get_structure("nmj", str(PDB))

# Collect CAs and all heavy atoms per chain
ca_by_chain: dict[str, list[tuple[int, np.ndarray, float]]] = defaultdict(list)
heavy_by_chain: dict[str, list[np.ndarray]] = defaultdict(list)

for model in s:
    for chain in model:
        cid = chain.id
        for res in chain:
            if res.id[0] != " ":
                continue
            for atom in res:
                if atom.element == "H":
                    continue
                heavy_by_chain[cid].append(atom.coord)
                if atom.name == "CA":
                    ca_by_chain[cid].append((res.id[1], atom.coord, atom.bfactor))

# Per-chain pLDDT summary (B-factor in ColabFold PDBs is pLDDT 0-100)
plddt_summary = {}
for cid, cas in ca_by_chain.items():
    if not cas:
        continue
    bs = [b for _, _, b in cas]
    plddt_summary[cid] = {
        "n_residues": len(cas),
        "mean_bfactor": float(np.mean(bs)),
        "median_bfactor": float(np.median(bs)),
        "min": float(np.min(bs)),
        "max": float(np.max(bs)),
    }

# Inter-chain CA contacts within 8 A
chains = sorted(ca_by_chain.keys())
ca_contacts = {}
for i, c1 in enumerate(chains):
    for c2 in chains[i + 1:]:
        ca1 = np.array([coord for _, coord, _ in ca_by_chain[c1]])
        ca2 = np.array([coord for _, coord, _ in ca_by_chain[c2]])
        if ca1.size == 0 or ca2.size == 0:
            continue
        d = np.linalg.norm(ca1[:, None, :] - ca2[None, :, :], axis=-1)
        n_8 = int(np.sum(d < 8.0))
        n_5 = int(np.sum(d < 5.0))
        min_d = float(np.min(d))
        if n_8 > 0:
            ca_contacts[f"{c1}-{c2}"] = {
                "ca_pairs_within_5A": n_5,
                "ca_pairs_within_8A": n_8,
                "min_ca_distance_A": min_d,
            }

# Heavy-atom clashes (< 2.0 A between different chains)
# Sample: check only pairs with CA contacts
clashes = {}
for pair, info in ca_contacts.items():
    c1, c2 = pair.split("-")
    h1 = np.array(heavy_by_chain[c1])
    h2 = np.array(heavy_by_chain[c2])
    if h1.size == 0 or h2.size == 0:
        continue
    # Block-wise to avoid huge memory
    n_clashes = 0
    block = 2000
    for i in range(0, len(h1), block):
        sub = h1[i:i + block]
        d = np.linalg.norm(sub[:, None, :] - h2[None, :, :], axis=-1)
        n_clashes += int(np.sum(d < 2.0))
    clashes[pair] = {"heavy_atom_clashes_under_2A": n_clashes}

out = {
    "source_pdb": str(PDB),
    "n_chains": len(chains),
    "plddt_summary_per_chain": plddt_summary,
    "interchain_ca_contacts": ca_contacts,
    "interchain_clashes": clashes,
}

out_path = ROOT / "validation" / "interface_metrics.json"
out_path.write_text(json.dumps(out, indent=2))
print(f"Wrote {out_path}")
print("\nContact summary (chain-chain pairs with any CA within 8 A):")
for pair, info in sorted(ca_contacts.items(), key=lambda x: -x[1]["ca_pairs_within_8A"]):
    clash_info = clashes.get(pair, {}).get("heavy_atom_clashes_under_2A", 0)
    print(f"  {pair}: CA_5A={info['ca_pairs_within_5A']:5d}  "
          f"CA_8A={info['ca_pairs_within_8A']:5d}  "
          f"min_d={info['min_ca_distance_A']:.2f}A  clashes<2A={clash_info}")

print("\npLDDT / B-factor summary per chain:")
for cid, s in plddt_summary.items():
    print(f"  {cid}: n={s['n_residues']:4d}  "
          f"mean={s['mean_bfactor']:.1f}  "
          f"min={s['min']:.1f}  max={s['max']:.1f}")

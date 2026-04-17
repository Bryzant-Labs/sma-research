#!/usr/bin/env python3
"""For EP400 and RNF213, parse PDB ATOM records to find the actual resolved
residue range (the DBREF record claims full length but only a subset is in the
crystal structure).
"""
import json, re, urllib.request
from pathlib import Path

def load_fasta(path):
    out = {}
    cur_id, cur = None, []
    for line in open(path):
        line = line.rstrip("\n")
        if line.startswith(">"):
            if cur_id:
                out[cur_id] = "".join(cur)
            m = re.search(r"\|([A-Z0-9]+)\|", line)
            cur_id = m.group(1) if m else None
            cur = []
        else:
            cur.append(line)
    if cur_id:
        out[cur_id] = "".join(cur)
    return out


def fetch_pdb(pdb_id):
    url = f"https://files.rcsb.org/download/{pdb_id.upper()}.pdb"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def resolved_range_per_uniprot(pdb_text, target_upid):
    """Find which chain corresponds to target UniProt via DBREF, then get ATOM range for that chain."""
    # Find chain(s) for target UniProt
    chains_for_upid = set()
    dbref_range = None
    for line in pdb_text.splitlines():
        if line.startswith("DBREF"):
            parts = line.split()
            if "UNP" not in parts:
                continue
            try:
                upid_idx = parts.index("UNP") + 1
                upid = parts[upid_idx]
                if upid != target_upid:
                    continue
                # chain is parts[2]
                chain = parts[2]
                chains_for_upid.add(chain)
                db_begin = int(parts[-2])
                db_end = int(parts[-1])
                if dbref_range is None:
                    dbref_range = (db_begin, db_end)
                else:
                    dbref_range = (min(dbref_range[0], db_begin), max(dbref_range[1], db_end))
            except (ValueError, IndexError):
                continue
    if not chains_for_upid:
        return None, None, None

    # Find ATOM resnum range for that chain
    atom_resnums = set()
    for line in pdb_text.splitlines():
        if line.startswith("ATOM"):
            if len(line) < 26:
                continue
            ch = line[21]
            if ch in chains_for_upid:
                try:
                    rn = int(line[22:26])
                    atom_resnums.add(rn)
                except ValueError:
                    continue
    if atom_resnums:
        return min(atom_resnums), max(atom_resnums), dbref_range
    return None, None, dbref_range


def main():
    fasta = load_fasta("/home/bryza/sma-research/qms/proteome_wide_2026/mn_proteome.fasta")
    data = json.load(open("/home/bryza/sma-research/qms/proteome_wide_2026/extended_target_domains.json"))

    # Fix EP400 (9C57) and RNF213 (8S24) — both too long
    for gene in ["EP400", "RNF213"]:
        rec = data[gene]
        upid = rec["uniprot"]
        pdb = rec["pdb"]
        print(f"\n[{gene}] re-parsing {pdb} for UniProt {upid}")
        try:
            text = fetch_pdb(pdb)
        except Exception as e:
            print(f"  fetch failed: {e}")
            continue
        atom_min, atom_max, dbref = resolved_range_per_uniprot(text, upid)
        print(f"  DBREF range: {dbref}")
        print(f"  ATOM resolved range: {atom_min}-{atom_max}")

        if atom_min and atom_max and atom_max - atom_min + 1 <= 1500:
            # Use resolved range
            full = fasta[upid]
            seq = full[atom_min-1:atom_max]
            rec["dbref_start"] = atom_min
            rec["dbref_end"] = atom_max
            rec["seq_len"] = len(seq)
            rec["seq"] = seq
            print(f"  Updated: range={atom_min}-{atom_max} len={len(seq)}")
        else:
            print(f"  WARN: resolved range too long or missing")

    outp = Path("/home/bryza/sma-research/qms/proteome_wide_2026/extended_target_domains.json")
    outp.write_text(json.dumps(data, indent=2))
    print(f"\nRewrote {outp}")
    print(f"\nSummary:")
    for g, rec in data.items():
        print(f"  {g:8s} {rec['dbref_start']}-{rec['dbref_end']} len={rec['seq_len']}")


if __name__ == "__main__":
    main()

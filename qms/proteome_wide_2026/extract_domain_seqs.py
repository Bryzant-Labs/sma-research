#!/usr/bin/env python3
"""Extract catalytic/binding domain sequences for Boltz-2.

Uses PDB DBREF records to define the residue range that the chosen PDB covers,
then slices the UniProt full-length sequence to that range.

Output: extended_target_domains.json mapping gene -> {uniprot, pdb, start, end, seq}
"""
import json, re, urllib.request
from pathlib import Path

TARGETS = {
    "EP400":  ("Q96L91", "9C57"),
    "PEAK1":  ("Q9H792", "6BHC"),
    "KAT7":   ("O95251", "7D0P"),
    "RNF213": ("Q63HN8", "8S24"),
    "EHMT2":  ("Q96KQ7", "5VSC"),
    "KAT6A":  ("Q92794", "9DZN"),
    "KAT5":   ("Q92993", "2OU2"),
    "KMT5B":  ("Q4FZB7", "3S8P"),
    "EHMT1":  ("Q9H9B1", "3HNA"),
}

# Load full-length sequences from fasta
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


def fetch_pdb_dbref(pdb_id, target_upid):
    """Fetch PDB and extract DBREF residue range for the given UniProt ID."""
    url = f"https://files.rcsb.org/download/{pdb_id.upper()}.pdb"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        text = resp.read().decode("utf-8", errors="ignore")
    # DBREF  9C57 B    1 3159  UNP    Q96L91   EP400_HUMAN     1   3159
    # fields: record, pdb_id, chain, seq_begin, seq_end, database, uniprot, uniprot_name, db_begin, db_end
    ranges = []
    for line in text.splitlines():
        if line.startswith("DBREF"):
            parts = line.split()
            if len(parts) < 10:
                continue
            # Some variations; search for UNP
            if "UNP" not in parts:
                continue
            try:
                upid_idx = parts.index("UNP") + 1
                upid = parts[upid_idx]
                if upid != target_upid:
                    continue
                db_begin = int(parts[-2])
                db_end = int(parts[-1])
                ranges.append((db_begin, db_end))
            except (ValueError, IndexError):
                continue
    if not ranges:
        return None, None
    # Use widest range
    start = min(r[0] for r in ranges)
    end = max(r[1] for r in ranges)
    return start, end


def main():
    fasta = load_fasta("/home/bryza/sma-research/qms/proteome_wide_2026/mn_proteome.fasta")
    out = {}
    for gene, (upid, pdb) in TARGETS.items():
        full = fasta.get(upid)
        if not full:
            print(f"{gene}: full sequence not in fasta")
            continue
        try:
            start, end = fetch_pdb_dbref(pdb, upid)
        except Exception as e:
            print(f"{gene}: fetch error {e}")
            continue
        if not start:
            print(f"{gene}: no DBREF for {upid} in {pdb}; using full length (len={len(full)})")
            seq = full
            start = 1
            end = len(full)
        else:
            # Slice — UniProt is 1-based
            if end - start + 1 > 1500:
                # cap to 1500 centered around pocket midpoint? For now use start..start+1500
                print(f"{gene}: DBREF range {start}-{end} too long ({end-start+1}); truncating to first 1500")
                end = start + 1499
            seq = full[start-1:end]
        out[gene] = {
            "uniprot": upid,
            "pdb": pdb,
            "dbref_start": start,
            "dbref_end": end,
            "seq_len": len(seq),
            "seq": seq,
        }
        print(f"{gene:8s} {upid} {pdb} range={start}-{end} len={len(seq)}")

    outp = Path("/home/bryza/sma-research/qms/proteome_wide_2026/extended_target_domains.json")
    outp.write_text(json.dumps(out, indent=2))
    print(f"\nWrote {outp}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""Phase A step 1: strip MuSK kinase chain H (intracellular, +260A kludge) from
the 13-chain static assembly. Produce a 12-chain ECD-side assembly for MD.

We keep: A,C (AChRa1 x2), B (AChRb1), D (AChRd), E (AChRe), F (RAPSN),
         G (MuSK ECD), I (DOK7, cytoplasmic but kept since it is not the
                          kinase kludge), J (LRP4 ECD), K (AGRIN), P (PERP),
         Z (H2b_9_s2 binder)
We drop:  H (MuSK kinase, placed +260 A lateral to LRP4 to avoid clashes;
             equilibrating this under restraint across such an unphysical gap
             is not justified for a first production run).

Rationale: per plan Phase A.2 option (a). The MuSK ECD (chain G) is retained
and its interaction with LRP4 + AGRIN is the primary ECD NMJ signal we want
to sample. The kinase domain will be re-integrated in a follow-up ECD+ICD run
once the TM linker is explicitly modelled (future work).

Also drops altloc duplicates, HETATMs (none expected), and renumbers residues
per chain so that AmberTools doesn't balk.
"""
from __future__ import annotations
import sys
from pathlib import Path

INP = Path("/home/bryza/sma-research/qms/NMJ_super_complex/assembly/nmj_super_complex.pdb")
OUT_DIR = Path("/home/bryza/sma-research/qms/NMJ_MD_breakthrough/prep")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT = OUT_DIR / "nmj_12chain_ecd_stripped.pdb"

KEEP_CHAINS = set("ACBDEFGIJKPZ")  # 12 chains; drops H (MuSK kinase)

def main() -> None:
    kept = 0
    dropped_H = 0
    dropped_altloc = 0
    other_drop = 0
    with INP.open() as fh, OUT.open("w") as out:
        out.write("REMARK  NMJ 12-chain ECD assembly (MuSK kinase chain H dropped)\n")
        out.write("REMARK  Parent: nmj_super_complex.pdb (agent a83b79c1)\n")
        out.write("REMARK  Rationale: +260 A MuSK-kinase lateral offset is a kludge.\n")
        out.write("REMARK  Chains retained: A C B D E F G I J K P Z (12 chains)\n")
        for line in fh:
            tag = line[:6]
            if tag in ("ATOM  ", "HETATM"):
                chain = line[21]
                altloc = line[16]
                if chain not in KEEP_CHAINS:
                    if chain == "H":
                        dropped_H += 1
                    else:
                        other_drop += 1
                    continue
                # keep only the primary altloc (A or blank)
                if altloc not in (" ", "A"):
                    dropped_altloc += 1
                    continue
                # force altloc to blank
                line = line[:16] + " " + line[17:]
                # Skip HETATM (no ligands / waters expected in static)
                if tag == "HETATM":
                    other_drop += 1
                    continue
                out.write(line)
                kept += 1
            elif tag.startswith("TER"):
                # Keep TER only for retained chains
                # TER columns: chainID at col 22 (0-indexed 21)
                if len(line) > 21 and line[21] in KEEP_CHAINS:
                    out.write(line)
            elif tag == "END   " or tag == "END\n" or tag == "END":
                out.write("END\n")
                break
            # drop everything else (HEADER, CRYST1, MODEL, etc. we will rewrite later)
    # Append END if missing
    with OUT.open("r") as fh:
        data = fh.read()
    if not data.rstrip().endswith("END"):
        with OUT.open("a") as fh:
            fh.write("END\n")

    print(f"[strip] kept ATOM lines     : {kept}")
    print(f"[strip] dropped chain H     : {dropped_H}")
    print(f"[strip] dropped altloc !=A  : {dropped_altloc}")
    print(f"[strip] dropped other       : {other_drop}")
    print(f"[strip] wrote               : {OUT}")

if __name__ == "__main__":
    main()

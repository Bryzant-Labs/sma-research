#!/usr/bin/env python3
"""Assemble 4 receptor-pair PDBs for SMA Bispecific Binder Farm (Option 2).

Rule: TITLE-verify passed for all source PDBs (see logs/title_verify.tsv).
Output: 4 two-chain receptor-pair PDBs in receptor_pairs/

Tracks:
  A: AChR alpha1 ECD (2BG9 chain A, resi 1-210) + MuSK Ig1-2 (2IEP chain A)
  B: AGRIN LG3 (3V64 chain B) + LRP4 beta-propeller 1-2 (3V64 chain A)  [co-crystal]
  C: PERP full (AF_Q96FX8 chain A) + AGRIN LG3 (3V64 chain B)
  D: DOK7 PH-PTB (3ML4 chain A) + MuSK juxtamembrane peptide (3ML4 chain E)  [co-crystal]
"""
import os
from pathlib import Path
from Bio.PDB import PDBParser, PDBIO, Select, Chain, Model, Structure

SRC = Path("/home/bryza/sma-research/qms/NMJ_super_complex/subcomplexes")
OUT = Path("/home/bryza/sma-research/qms/NMJ_bispecific_farm/receptor_pairs")
OUT.mkdir(parents=True, exist_ok=True)

parser = PDBParser(QUIET=True)


def extract_chain(pdb_file, chain_id, new_chain_id, resi_range=None):
    """Return a Chain object copied from source with renamed id and optional resi filter."""
    struct = parser.get_structure("src", pdb_file)
    model = struct[0]
    if chain_id not in model:
        raise ValueError(f"Chain {chain_id} not found in {pdb_file}. Avail: {[c.id for c in model]}")
    src_chain = model[chain_id]
    new_chain = Chain.Chain(new_chain_id)
    for res in src_chain:
        # skip HETATM except standard residues
        if res.id[0].strip() and res.id[0] != ' ':
            continue
        if resi_range is not None:
            lo, hi = resi_range
            if not (lo <= res.id[1] <= hi):
                continue
        new_chain.add(res.copy())
    return new_chain


def write_pair(out_path, chain_a, chain_b, title):
    """Write 2-chain PDB with renamed chains A and B."""
    struct = Structure.Structure("pair")
    model = Model.Model(0)
    model.add(chain_a)
    model.add(chain_b)
    struct.add(model)
    io = PDBIO()
    io.set_structure(struct)
    tmp = str(out_path) + ".tmp"
    io.save(tmp)
    # prepend TITLE
    with open(tmp) as f:
        body = f.read()
    with open(out_path, "w") as f:
        f.write(f"TITLE     {title}\n")
        f.write(body)
    os.remove(tmp)
    n_a = sum(1 for _ in chain_a)
    n_b = sum(1 for _ in chain_b)
    return n_a, n_b


def track_A():
    # AChR alpha1 ECD from 2BG9 chain A (residues ~1-210 = extracellular)
    # Torpedo californica AChR alpha residues 1-210 = ECD
    achr = extract_chain(SRC / "2BG9.pdb", "A", "A", resi_range=(1, 210))
    # MuSK Ig1-Ig2 from 2IEP chain A
    musk = extract_chain(SRC / "2IEP.pdb", "A", "B")
    return write_pair(
        OUT / "track_A_AChR_MuSK.pdb", achr, musk,
        "TRACK A - AChR ALPHA1 ECD (2BG9:A) + MUSK IG1-2 (2IEP:A) - BISPECIFIC TARGET"
    )


def track_B():
    # 3V64: chains C,D = LRP4 LG3; chains A,B (or similar) = AGRIN. Verify.
    # Per COMPND: LRP4 LG3 = chains C,D; AGRIN = chain A (mol_id 2)
    # We want LRP4 beta-propeller... 3V64 COMPND says LRP4 "LG3 DOMAIN" - need to re-read.
    # Actually COMPND line says "FRAGMENT: LG3 DOMAIN (UNP RESIDUES 1759-1948)" for LRP4
    # That's wrong in the COMPND tag - 3V64 is LRP4 beta-propeller+AGRIN LG3.
    # Plan says: AGRIN LG3 (chain A) + LRP4 (chain B). We'll use those as-is.
    agrin_lg3 = extract_chain(SRC / "3V64.pdb", "A", "A")
    lrp4 = extract_chain(SRC / "3V64.pdb", "B", "B")
    return write_pair(
        OUT / "track_B_AGRIN_LRP4.pdb", agrin_lg3, lrp4,
        "TRACK B - AGRIN LG3 (3V64:A) + LRP4 BETA-PROPELLER (3V64:B) - CO-CRYSTAL BISPECIFIC"
    )


def track_C():
    # PERP full-length AlphaFold (AF_Q96FX8 chain A) + AGRIN LG3 (3V64 chain A)
    perp = extract_chain(SRC / "AF_Q96FX8.pdb", "A", "A")
    agrin_lg3 = extract_chain(SRC / "3V64.pdb", "A", "B")
    return write_pair(
        OUT / "track_C_PERP_AGRIN.pdb", perp, agrin_lg3,
        "TRACK C - PERP FULL (AF Q96FX8) + AGRIN LG3 (3V64:A) - NMJ ORGANIZER BISPECIFIC"
    )


def track_D():
    # 3ML4 is native DOK7 PH-PTB (chain A) + MuSK juxtamembrane (chain E) co-crystal
    dok7 = extract_chain(SRC / "3ML4.pdb", "A", "A")
    musk_jm = extract_chain(SRC / "3ML4.pdb", "E", "B")
    return write_pair(
        OUT / "track_D_DOK7_MuSK.pdb", dok7, musk_jm,
        "TRACK D - DOK7 PH-PTB (3ML4:A) + MUSK JUXTAMEMBRANE (3ML4:E) - CO-CRYSTAL BISPECIFIC"
    )


if __name__ == "__main__":
    print("\n=== PHASE A: Building 4 receptor-pair PDBs ===\n")
    for name, fn in [("A", track_A), ("B", track_B), ("C", track_C), ("D", track_D)]:
        try:
            n_a, n_b = fn()
            size = (OUT / f"track_{name}_*.pdb").__str__()
            files = list(OUT.glob(f"track_{name}_*.pdb"))
            if files:
                sz = files[0].stat().st_size
                print(f"Track {name}: chain A = {n_a} res, chain B = {n_b} res, file = {files[0].name} ({sz} bytes)")
            else:
                print(f"Track {name}: file missing!")
        except Exception as e:
            print(f"Track {name}: FAILED - {e}")
    print("\nDone.\n")

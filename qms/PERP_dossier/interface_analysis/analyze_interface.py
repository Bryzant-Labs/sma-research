#!/usr/bin/env python3
"""
PERP binder interface analysis — lightweight Rosetta InterfaceAnalyzer alternative.

Uses Biopython PDB + Shrake-Rupley SASA. For each PERP+binder complex:
  1. ΔSASA (buried interface surface area)
  2. Interface residue contacts (<4.5 Å heavy-atom)
  3. Electrostatic pairs (charged + charged within 5 Å, opposite-sign)
  4. Hydrogen bond proxy count (donor-acceptor <3.5 Å, with geometric filter)

Inputs: list of _target.pdb (Boltz-2 co-folds; Chain A = PERP, Chain B = binder).
Output: JSON + Markdown table ranking binders by composite interface score.
"""

import json
import math
import sys
from pathlib import Path

from Bio.PDB import PDBParser
from Bio.PDB.SASA import ShrakeRupley

# --- Top 10 PERP binders (from PERP_binder_design_RESULTS.md) ---
BINDERS = [
    # ECL1 top 5
    {"rank": 1, "ecl": "ECL1", "design_id": "H1a_38_s7", "hotspot": "H1a", "length": 85, "plddt": 0.802, "iptm_target": 0.573, "delta_iptm": 0.438,
     "pdb": "/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/ecl1/H1a/H1a_38_s7_target.pdb"},
    {"rank": 2, "ecl": "ECL1", "design_id": "H1c_25_s4", "hotspot": "H1c", "length": 84, "plddt": 0.804, "iptm_target": 0.522, "delta_iptm": 0.415,
     "pdb": "/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/ecl1/H1c/H1c_25_s4_target.pdb"},
    {"rank": 3, "ecl": "ECL1", "design_id": "H1c_25_s5", "hotspot": "H1c", "length": 84, "plddt": 0.825, "iptm_target": 0.492, "delta_iptm": 0.373,
     "pdb": "/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/ecl1/H1c/H1c_25_s5_target.pdb"},
    {"rank": 4, "ecl": "ECL1", "design_id": "H1b_14_s6", "hotspot": "H1b", "length": 72, "plddt": 0.796, "iptm_target": 0.448, "delta_iptm": 0.360,
     "pdb": "/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/ecl1/H1b/H1b_14_s6_target.pdb"},
    {"rank": 5, "ecl": "ECL1", "design_id": "H1b_10_s3", "hotspot": "H1b", "length": 85, "plddt": 0.798, "iptm_target": 0.351, "delta_iptm": 0.260,
     "pdb": "/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/ecl1/H1b/H1b_10_s3_target.pdb"},
    # ECL2 top 5
    {"rank": 1, "ecl": "ECL2", "design_id": "H2b_9_s2", "hotspot": "H2b", "length": 87, "plddt": 0.794, "iptm_target": 0.596, "delta_iptm": 0.468,
     "pdb": "/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/ecl2/H2b/H2b_9_s2_target.pdb"},
    {"rank": 2, "ecl": "ECL2", "design_id": "H2c_11_s1", "hotspot": "H2c", "length": 81, "plddt": 0.797, "iptm_target": 0.528, "delta_iptm": 0.433,
     "pdb": "/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/ecl2/H2c/H2c_11_s1_target.pdb"},
    {"rank": 3, "ecl": "ECL2", "design_id": "H2b_3_s4", "hotspot": "H2b", "length": 75, "plddt": 0.799, "iptm_target": 0.561, "delta_iptm": 0.366,
     "pdb": "/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/ecl2/H2b/H2b_3_s4_target.pdb"},
    {"rank": 4, "ecl": "ECL2", "design_id": "H2a_1_s5", "hotspot": "H2a", "length": 83, "plddt": 0.796, "iptm_target": 0.415, "delta_iptm": 0.328,
     "pdb": "/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/ecl2/H2a/H2a_1_s5_target.pdb"},
    {"rank": 5, "ecl": "ECL2", "design_id": "H2c_26_s4", "hotspot": "H2c", "length": 68, "plddt": 0.799, "iptm_target": 0.385, "delta_iptm": 0.291,
     "pdb": "/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/ecl2/H2c/H2c_26_s4_target.pdb"},
]

# Charged residues
POS_RES = {"LYS", "ARG", "HIS"}
NEG_RES = {"ASP", "GLU"}
# Side-chain "charge-bearing" atom (approximation for salt-bridge proxy)
POS_ATOMS = {"LYS": ["NZ"], "ARG": ["NH1", "NH2", "NE"], "HIS": ["ND1", "NE2"]}
NEG_ATOMS = {"ASP": ["OD1", "OD2"], "GLU": ["OE1", "OE2"]}
# Hydrogen-bond donor/acceptor atoms (simplified, backbone + key sidechain)
HBOND_DONORS = {"N"}  # backbone N (all aa except Pro)
HBOND_DONOR_SC = {
    "SER": ["OG"], "THR": ["OG1"], "TYR": ["OH"], "ASN": ["ND2"], "GLN": ["NE2"],
    "TRP": ["NE1"], "HIS": ["ND1", "NE2"], "LYS": ["NZ"], "ARG": ["NH1", "NH2", "NE"],
}
HBOND_ACCEPTORS = {"O"}  # backbone O
HBOND_ACCEPTOR_SC = {
    "SER": ["OG"], "THR": ["OG1"], "TYR": ["OH"], "ASN": ["OD1"], "GLN": ["OE1"],
    "ASP": ["OD1", "OD2"], "GLU": ["OE1", "OE2"], "HIS": ["ND1", "NE2"],
}

def dist(a, b):
    d = a.coord - b.coord
    return math.sqrt((d[0])**2 + (d[1])**2 + (d[2])**2)

def compute_sasa_dsasa(structure):
    """Compute SASA of complex and of each chain in isolation. Return ΔSASA (per-atom, summed)."""
    # Complex SASA
    sr = ShrakeRupley(probe_radius=1.4, n_points=100)
    sr.compute(structure, level="R")  # per-residue
    complex_sasa_A = sum(r.sasa for r in structure[0]["A"])
    complex_sasa_B = sum(r.sasa for r in structure[0]["B"])

    # Each chain alone
    # Re-compute after extracting chains — use a fresh parser to avoid mutation
    parser = PDBParser(QUIET=True)
    path = structure.header.get("_src_path")  # stuffed below
    # Trick: write just chain A / chain B to tempfiles and recompute
    from Bio.PDB import PDBIO, Select
    class OnlyChain(Select):
        def __init__(self, cid): self.cid = cid
        def accept_chain(self, chain): return chain.id == self.cid
    io = PDBIO()
    io.set_structure(structure)
    tmpA = f"/tmp/_chainA_{id(structure)}.pdb"
    tmpB = f"/tmp/_chainB_{id(structure)}.pdb"
    io.save(tmpA, OnlyChain("A"))
    io.save(tmpB, OnlyChain("B"))

    sA = parser.get_structure("A", tmpA)
    sB = parser.get_structure("B", tmpB)
    sr.compute(sA, level="R")
    sr.compute(sB, level="R")
    alone_A = sum(r.sasa for r in sA[0]["A"])
    alone_B = sum(r.sasa for r in sB[0]["B"])

    # ΔSASA = buried area (summed both sides) / 2 is the interface area
    buried_A = alone_A - complex_sasa_A
    buried_B = alone_B - complex_sasa_B
    interface_area = (buried_A + buried_B) / 2.0
    return {
        "complex_sasa_A": complex_sasa_A,
        "complex_sasa_B": complex_sasa_B,
        "alone_sasa_A": alone_A,
        "alone_sasa_B": alone_B,
        "buried_A": buried_A,
        "buried_B": buried_B,
        "interface_area_A2": interface_area,
    }

def compute_interface_contacts(structure, cutoff=4.5):
    """Count interface residues (any heavy-atom pair A-B within cutoff) and atom-pair contacts."""
    model = structure[0]
    chainA = model["A"]
    chainB = model["B"]
    atomsA = [a for r in chainA for a in r if a.element != "H"]
    atomsB = [a for r in chainB for a in r if a.element != "H"]
    contacts = 0
    iface_res_A = set()
    iface_res_B = set()
    for aA in atomsA:
        for aB in atomsB:
            if dist(aA, aB) <= cutoff:
                contacts += 1
                iface_res_A.add(aA.get_parent().id[1])
                iface_res_B.add(aB.get_parent().id[1])
    return {
        "heavy_atom_contacts": contacts,
        "interface_residues_A": len(iface_res_A),
        "interface_residues_B": len(iface_res_B),
        "iface_res_A_list": sorted(iface_res_A),
        "iface_res_B_list": sorted(iface_res_B),
    }

def compute_salt_bridges(structure, cutoff=5.0):
    """Salt bridge proxy: charge-bearing atom on A vs opposite charge on B within cutoff."""
    model = structure[0]
    chainA = model["A"]
    chainB = model["B"]
    # Build lists of charged atoms per chain
    def charged_atoms(chain):
        pos = []
        neg = []
        for res in chain:
            rn = res.resname
            if rn in POS_RES:
                for an in POS_ATOMS.get(rn, []):
                    if an in res:
                        pos.append((rn, res.id[1], res[an]))
            if rn in NEG_RES:
                for an in NEG_ATOMS.get(rn, []):
                    if an in res:
                        neg.append((rn, res.id[1], res[an]))
        return pos, neg
    posA, negA = charged_atoms(chainA)
    posB, negB = charged_atoms(chainB)
    sb = 0
    details = []
    # + on A, - on B
    for rnA, riA, aA in posA:
        for rnB, riB, aB in negB:
            if dist(aA, aB) <= cutoff:
                sb += 1
                details.append(f"A:{rnA}{riA}-B:{rnB}{riB}({dist(aA,aB):.2f}A)")
    # - on A, + on B
    for rnA, riA, aA in negA:
        for rnB, riB, aB in posB:
            if dist(aA, aB) <= cutoff:
                sb += 1
                details.append(f"A:{rnA}{riA}-B:{rnB}{riB}({dist(aA,aB):.2f}A)")
    return {"salt_bridges": sb, "details": details[:20]}

def compute_hbonds(structure, cutoff=3.5):
    """H-bond proxy: donor heavy atom - acceptor heavy atom within cutoff, across chains.
       No angle filter (no H atoms in PDB) — conservative distance-only count.
       For backbone-N donor, exclude when residue is PRO.
    """
    model = structure[0]
    chainA = model["A"]
    chainB = model["B"]
    def donors(chain):
        d = []
        for res in chain:
            rn = res.resname
            # backbone N (not Pro)
            if "N" in res and rn != "PRO":
                d.append((rn, res.id[1], res["N"]))
            for an in HBOND_DONOR_SC.get(rn, []):
                if an in res:
                    d.append((rn, res.id[1], res[an]))
        return d
    def acceptors(chain):
        a = []
        for res in chain:
            rn = res.resname
            if "O" in res:
                a.append((rn, res.id[1], res["O"]))
            for an in HBOND_ACCEPTOR_SC.get(rn, []):
                if an in res:
                    a.append((rn, res.id[1], res[an]))
        return a
    dA, aA = donors(chainA), acceptors(chainA)
    dB, aB = donors(chainB), acceptors(chainB)
    hb = 0
    # donors A -> acceptors B
    for rnA, riA, atA in dA:
        for rnB, riB, atB in aB:
            if dist(atA, atB) <= cutoff:
                hb += 1
    # donors B -> acceptors A
    for rnB, riB, atB in dB:
        for rnA, riA, atA in aA:
            if dist(atB, atA) <= cutoff:
                hb += 1
    return {"hbonds": hb}

def analyze_one(binder):
    parser = PDBParser(QUIET=True)
    s = parser.get_structure(binder["design_id"], binder["pdb"])
    # Store path for SASA recompute
    s.header["_src_path"] = binder["pdb"]
    out = {**binder}
    print(f"  [{binder['design_id']}] SASA...", file=sys.stderr, flush=True)
    out["sasa"] = compute_sasa_dsasa(s)
    print(f"  [{binder['design_id']}] contacts...", file=sys.stderr, flush=True)
    out["contacts"] = compute_interface_contacts(s, cutoff=4.5)
    print(f"  [{binder['design_id']}] salt bridges...", file=sys.stderr, flush=True)
    out["salt_bridges"] = compute_salt_bridges(s, cutoff=5.0)
    print(f"  [{binder['design_id']}] hbonds...", file=sys.stderr, flush=True)
    out["hbonds"] = compute_hbonds(s, cutoff=3.5)
    return out

def main():
    out_dir = Path("/home/bryza/sma-research/qms/PERP_dossier/interface_analysis")
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for i, b in enumerate(BINDERS, 1):
        print(f"[{i}/{len(BINDERS)}] {b['design_id']} ({b['ecl']})", file=sys.stderr, flush=True)
        try:
            r = analyze_one(b)
            results.append(r)
        except Exception as e:
            print(f"  FAILED: {e}", file=sys.stderr, flush=True)
            results.append({**b, "error": str(e)})
    # Save JSON
    (out_dir / "interface_metrics.json").write_text(json.dumps(results, indent=2, default=str))
    print(f"\nSaved {out_dir/'interface_metrics.json'}", file=sys.stderr)
    # Print table
    print("\n{:20s} {:5s} {:5s} {:6s} {:5s} {:8s} {:4s} {:3s} {:3s}".format(
        "design_id", "ECL", "hotspt", "iptmT", "dIptm", "iface_A2", "cnt", "sb", "hb"))
    for r in results:
        if "error" in r:
            print(f"{r['design_id']:20s} ERROR: {r['error']}")
            continue
        print("{:20s} {:5s} {:5s} {:6.3f} {:+5.3f} {:8.1f} {:4d} {:3d} {:3d}".format(
            r["design_id"], r["ecl"], r["hotspot"],
            r["iptm_target"], r["delta_iptm"],
            r["sasa"]["interface_area_A2"],
            r["contacts"]["heavy_atom_contacts"],
            r["salt_bridges"]["salt_bridges"],
            r["hbonds"]["hbonds"],
        ))

if __name__ == "__main__":
    main()

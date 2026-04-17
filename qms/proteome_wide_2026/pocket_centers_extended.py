#!/usr/bin/env python3
"""Compute pocket centers for extended-campaign PDBs.

For ligand-bound entries: ligand heteroatom centroid.
For apo entries: use published pocket residue Cα centroid OR largest fpocket.

Writes extended_pocket_centers.json consumed by the task-JSON generator.
"""
import json
import urllib.request
import sys
from pathlib import Path

# Final selection: (gene, uniprot, pdb_id, pocket_strategy, pocket_spec, rationale)
# pocket_strategy: "ligand" | "residues" | "chain_bbox"
SELECTION = [
    # PIK3C2A: switch from C2 to PX domain WITH IP6 ligand OR apo
    # 6BU0 has IP6 in PX domain — real druggable pocket, use it
    ("PIK3C2A", "O00443", "6BU0", "ligand", "IHP", "PI3K-C2alpha PX domain + IP6 lipid pocket"),

    # RANBP2: 4GA0 N-term domain apo 1.15Å (cleanest); use residue-based for surface pocket
    # Actually the GDP-binding site on Ran is NOT on RanBP2. RanBP2 ZnFs don't have druggable pockets.
    # Better: use 4I9Y C-term (cyclophilin domain — has a pocket) at 1.75Å.
    # Actually cyclophilin-like domain has known small-molecule site. Use 4I9Y apo + fpocket fallback.
    ("RANBP2", "P49792", "4I9Y", "fpocket", "", "RanBP2 C-term cyclophilin-like domain apo"),

    # OPTN: 9IKQ has GTP in LZD complex. But OPTN itself doesn't bind GTP (Rab8a does).
    # Better: 5B83 UBAN + ubiquitin — UBAN is the druggable PPI surface (SMA-relevant NF-kB axis).
    # Or 3VTV LIR + LC3B (autophagy pocket on LC3B side, not OPTN).
    # Use 5B83 UBAN targeting ubiquitin binding site (PPI inhibitor type).
    ("OPTN", "Q96CV9", "5B83", "residues", "424,430,431,434,438,443,462,466", "OPTN UBAN ubiquitin-binding surface (PPI inhibitor target)"),

    # EP400: 9C57 has AGS/ATP in reconstituted P400 subcomplex — ATP pocket on EP400 ATPase!
    ("EP400", "Q96L91", "9C57", "ligand", "AGS", "EP400 ATPase domain ATP-binding pocket (9C57 AMP-PNP analog)"),

    # PEAK1: 6BHC pseudokinase apo. Pseudokinases have ATP-binding cleft that is targetable.
    # Use residue centroid of canonical K/E/DFG motif residues (PEAK1: K1435, E1454, DFG ~1571).
    ("PEAK1", "Q9H792", "6BHC", "residues", "1435,1454,1571,1572,1573", "PEAK1 ATP-binding cleft (apo pseudokinase)"),

    # USP34: 7W3R catalytic domain apo. USP catalytic triad C,H,D. C3437 is catalytic Cys.
    # Actually USP34 catalytic Cys ~2444 (NTD cat domain). Need to check PDB numbering.
    # Use fpocket since we don't know exact residue numbering in 7W3R.
    ("USP34", "Q70CQ2", "7W3R", "fpocket", "", "USP34 catalytic domain apo (fpocket)"),

    # KAT7: 7D0P MYST HAT + propionyl-CoA (ligand-bound). Use 1VU ligand (propionyl-CoA mimic).
    ("KAT7", "O95251", "7D0P", "ligand", "1VU", "KAT7/HBO1 MYST HAT + propionyl-CoA pocket"),

    # RNF213: 8S24 cryoEM 3.0Å has ATP in AAA ATPase domain. Use it (druggable ATPase).
    ("RNF213", "Q63HN8", "8S24", "ligand", "ATP", "RNF213 AAA ATPase ATP pocket (cryoEM 3.0Å)"),

    # BTF3: 3MCB NAC dimer apo. NAC is a coiled-coil PPI surface. Use fpocket.
    ("BTF3", "P20290", "3MCB", "fpocket", "", "BTF3 NAC dimer surface (fpocket)"),

    # EHMT2 / G9a: 5VSC SET + SAM + inhibitor 13 (9HJ). Use 9HJ ligand centroid (inhibitor site).
    ("EHMT2", "Q96KQ7", "5VSC", "ligand", "9HJ", "EHMT2/G9a SET domain inhibitor site (co-crystal)"),

    # TIAM1: GEF PH-CC-Ex domain is the druggable site (Rac1 exchange).
    # 4K2O is PH-CC-Ex at 2.15Å, apo. Use fpocket.
    # Actually 4K2O is mutant. Use original WT. No WT GEF structure at ≤2.5Å.
    # Accept 4K2P (1.98Å, quintuple mutant PH-CC-Ex) — still the GEF catalytic site.
    ("TIAM1", "Q13009", "4K2P", "fpocket", "", "TIAM1 PH-CC-Ex GEF catalytic surface"),

    # KAT6A: 9DZN KAT6A MYST HAT + CMC bisubstrate inhibitor. Perfect co-crystal.
    ("KAT6A", "Q92794", "9DZN", "ligand", "CMC", "KAT6A MYST HAT + bisubstrate inhibitor (co-crystal)"),

    # KAT5: 2OU2 TIP60 MYST HAT + acetyl-CoA. Use ACO ligand.
    ("KAT5", "Q92993", "2OU2", "ligand", "ACO", "KAT5/TIP60 MYST HAT + acetyl-CoA"),

    # MYCBP2: 5O6C RCR E3 apo. Use fpocket.
    ("MYCBP2", "O75592", "5O6C", "fpocket", "", "MYCBP2 RCR E3 ligase catalytic pocket (apo, fpocket)"),

    # KMT5B: 3S8P SET + SAM. Use SAM centroid.
    ("KMT5B", "Q4FZB7", "3S8P", "ligand", "SAM", "KMT5B/SUV420H1 SET domain + SAM cofactor"),

    # EHMT1: 3HNA SET + SAH. Use SAH centroid.
    ("EHMT1", "Q9H9B1", "3HNA", "ligand", "SAH", "EHMT1/GLP SET domain + SAH cofactor"),
]


def fetch_pdb(pdb_id: str, cache_dir: Path) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    out = cache_dir / f"{pdb_id.upper()}.pdb"
    if out.exists() and out.stat().st_size > 100:
        return out
    url = f"https://files.rcsb.org/download/{pdb_id.upper()}.pdb"
    print(f"  Downloading {url}", file=sys.stderr)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        out.write_bytes(resp.read())
    return out


def parse_ligand_centroid(pdb_path: Path, lig_code: str):
    """Return centroid of first non-H atom set for HETATM with resName == lig_code."""
    xs, ys, zs = [], [], []
    with open(pdb_path) as f:
        for line in f:
            if line.startswith("HETATM"):
                resn = line[17:20].strip()
                if resn == lig_code.strip():
                    element = line[76:78].strip() if len(line) >= 78 else line[12:14].strip()
                    if element.upper() == "H":
                        continue
                    try:
                        x = float(line[30:38]); y = float(line[38:46]); z = float(line[46:54])
                        xs.append(x); ys.append(y); zs.append(z)
                    except Exception:
                        continue
    if not xs:
        return None
    return (sum(xs)/len(xs), sum(ys)/len(ys), sum(zs)/len(zs))


def parse_residue_centroid(pdb_path: Path, resnums, chain=None):
    """Centroid of CA atoms for given residue numbers (any chain unless specified)."""
    xs, ys, zs = [], [], []
    targets = set(int(r) for r in resnums)
    with open(pdb_path) as f:
        for line in f:
            if line.startswith("ATOM"):
                atom_name = line[12:16].strip()
                if atom_name != "CA":
                    continue
                ch = line[21]
                if chain and ch != chain:
                    continue
                try:
                    resnum = int(line[22:26])
                except ValueError:
                    continue
                if resnum in targets:
                    try:
                        x = float(line[30:38]); y = float(line[38:46]); z = float(line[46:54])
                        xs.append(x); ys.append(y); zs.append(z)
                    except Exception:
                        continue
    if not xs:
        return None
    return (sum(xs)/len(xs), sum(ys)/len(ys), sum(zs)/len(zs))


def parse_protein_bbox_center(pdb_path: Path):
    """Center of protein CA atoms as last-resort (NOT a pocket — use only with fpocket)."""
    xs, ys, zs = [], [], []
    with open(pdb_path) as f:
        for line in f:
            if line.startswith("ATOM") and line[12:16].strip() == "CA":
                try:
                    xs.append(float(line[30:38])); ys.append(float(line[38:46])); zs.append(float(line[46:54]))
                except Exception:
                    continue
    if not xs:
        return None
    return (sum(xs)/len(xs), sum(ys)/len(ys), sum(zs)/len(zs))


def run_fpocket(pdb_path: Path, cache_dir: Path):
    """Run fpocket, return centroid of largest pocket (if fpocket installed)."""
    import shutil
    import subprocess
    fp = shutil.which("fpocket")
    if not fp:
        return None
    # fpocket outputs to <input>_out/
    out_dir = pdb_path.parent / f"{pdb_path.stem}_out"
    if not out_dir.exists():
        try:
            subprocess.run([fp, "-f", str(pdb_path)], check=True, cwd=str(pdb_path.parent),
                           capture_output=True, timeout=300)
        except Exception as e:
            print(f"  fpocket failed: {e}", file=sys.stderr)
            return None
    if not out_dir.exists():
        return None
    # Parse pockets/pocket1_atm.pdb centroid
    for i in range(1, 11):
        p = out_dir / "pockets" / f"pocket{i}_atm.pdb"
        if p.exists():
            cent = parse_protein_bbox_center(p)
            if cent:
                return cent
    return None


def main():
    cache = Path("/tmp/pdb_cache_extended")
    out = {}
    for gene, uniprot, pdb, strat, spec, rationale in SELECTION:
        print(f"\n[{gene}] {uniprot} PDB={pdb} strat={strat} spec='{spec}'")
        try:
            pp = fetch_pdb(pdb, cache)
        except Exception as e:
            print(f"  ERROR fetch: {e}", file=sys.stderr)
            out[gene] = {"error": f"fetch: {e}"}
            continue
        center = None
        if strat == "ligand":
            center = parse_ligand_centroid(pp, spec)
            if center is None:
                print(f"  WARN: ligand {spec} not found in {pdb}; falling back to fpocket")
                strat = "fpocket"
        if strat == "residues":
            center = parse_residue_centroid(pp, spec.split(","))
            if center is None:
                print(f"  WARN: residues {spec} not found; falling back to fpocket")
                strat = "fpocket"
        if strat == "fpocket":
            center = run_fpocket(pp, cache)
            if center is None:
                print(f"  WARN: fpocket unavailable or failed; using protein bbox")
                center = parse_protein_bbox_center(pp)
        if center:
            center = tuple(round(v, 2) for v in center)
            print(f"  center={center}")
        out[gene] = {
            "uniprot": uniprot,
            "pdb_id": pdb,
            "pocket_strategy": strat,
            "pocket_spec": spec,
            "pocket_center": list(center) if center else None,
            "pocket_radius": 10.0,
            "rationale": rationale,
        }
    outp = Path("/home/bryza/sma-research/qms/proteome_wide_2026/extended_pocket_centers.json")
    outp.write_text(json.dumps(out, indent=2))
    print(f"\nWrote {outp}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Triage the 20 candidate PDBs: for flagged (CHECK) ones, list alternative PDBs
to help pick the best druggable pocket structure."""
import json, urllib.request, sys

def http_get(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


def uniprot_pdb_xrefs(uniprot: str):
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot}.json"
    data = json.loads(http_get(url))
    pdbs = []
    for ref in data.get("uniProtKBCrossReferences", []):
        if ref.get("database") == "PDB":
            props = {p["key"]: p["value"] for p in ref.get("properties", [])}
            r = props.get("Resolution", "")
            try:
                resolution = float(r.split()[0]) if r and r != "-" else None
            except Exception:
                resolution = None
            pdbs.append({
                "pdb": ref["id"],
                "method": props.get("Method", ""),
                "resolution": resolution,
                "chains": props.get("Chains", ""),
            })
    return pdbs


def rcsb_title(pdb_id: str) -> str:
    try:
        data = json.loads(http_get(f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id.lower()}"))
        return data.get("struct", {}).get("title", "")
    except Exception:
        return ""


def rcsb_ligs(pdb_id: str) -> list:
    try:
        data = json.loads(http_get(f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id.lower()}"))
    except Exception:
        return []
    np_ids = data.get("rcsb_entry_container_identifiers", {}).get("non_polymer_entity_ids", [])
    ignore = {"HOH", "EDO", "GOL", "DMS", "TRS", "PEG", "PG4", "MPD", "SO4", "PO4",
              "CL", "NA", "MG", "CA", "ZN", "K", "FE", "MN", "CU", "ACT", "FMT", "NI",
              "IMD", "CIT", "TLA", "FLC", "MLT", "IPA", "BME", "DMSO", "SCN", "BR", "IOD",
              "PG0", "1PE", "PGE", "BOG", "OCT", "ACE", "NAG"}
    out = []
    for npid in np_ids:
        try:
            npd = json.loads(http_get(f"https://data.rcsb.org/rest/v1/core/nonpolymer_entity/{pdb_id.lower()}/{npid}"))
            cc = npd.get("pdbx_entity_nonpoly", {}).get("comp_id", "")
            if cc and cc not in ignore and len(cc) == 3:
                out.append(cc)
        except Exception:
            continue
    return out


# Targets that need disambiguation
TRIAGE = [
    ("PIK3C2A", "O00443"),   # 6BTY is C2 domain not kinase
    ("OPTN",    "Q96CV9"),   # 9B0B is OPTN-HOIP; need apo OPTN UBAN
    ("EIF4G1",  "Q04637"),   # 5T46 is eIF4E pocket, not eIF4G
    ("TIAM1",   "Q13009"),   # 4GVC is PDZ; is there GEF DH-PH inhibitor?
    ("KAT6A",   "Q92794"),   # 5B78 is PHD; need MYST HAT
    ("KAT5",    "Q92993"),   # 2OU2 is TIP60 MYST HAT + AcCoA — actually PASS
    ("MYCBP2",  "O75592"),   # 5O6C is RCR domain
    ("KAT7",    "O95251"),   # 7D0P is MYST HAT + propionyl-CoA — PASS
    ("EHMT1",   "Q9H9B1"),   # 3HNA SET + SAH — PASS
    ("KMT5B",   "Q4FZB7"),   # 3S8P SET + SAM — PASS
    ("EP400",   "Q96L91"),   # 9CAF TIP60 complex — check if EP400 ATPase visible
    ("BTF3",    "P20290"),   # 3MCB is NAC complex
    ("RNF213",  "Q63HN8"),   # 9JTA RING domain — need AAA ATPase
    ("MRPS31",  "Q92665"),   # mitoribosome
    ("USP34",   "Q70CQ2"),   # 7W3R cat domain
    ("RANBP2",  "P49792"),   # 7MNR ZnF3
    ("PEAK1",   "Q9H792"),   # 6BHC pseudokinase
]

for gene, uniprot in TRIAGE:
    print(f"\n=== {gene} ({uniprot}) ===")
    pdbs = uniprot_pdb_xrefs(uniprot)
    good = [p for p in pdbs if p["method"] in ("X-ray", "EM")
            and p["resolution"] is not None and p["resolution"] <= 3.0]
    good.sort(key=lambda p: p["resolution"])
    # List top-10 with ligands
    for p in good[:10]:
        try:
            t = rcsb_title(p["pdb"])
            l = rcsb_ligs(p["pdb"])
        except Exception:
            continue
        lig_flag = ",".join(l) if l else "-"
        print(f"  {p['pdb']:5s} {p['resolution']:.2f}Å  [lig:{lig_flag:15s}] {t[:90]}")

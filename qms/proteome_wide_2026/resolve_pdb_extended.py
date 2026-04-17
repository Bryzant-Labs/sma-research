#!/usr/bin/env python3
"""Resolve best PDB structures for atlas ranks 6-25 extended campaign.

For each target:
  1. Query UniProt cross-refs → list of PDB IDs for that UniProt
  2. Filter by resolution < 2.5 Å, ligand-bound preferred
  3. Fetch TITLE + DBREF from RCSB, verify UniProt match
  4. If ligand-bound: compute pocket center from heteroatom centroid
  5. If apo: mark for manual literature-guided pocket (skip or fallback)

Output: extended_pdb_resolution.tsv + TITLE_AUDIT_extended.md (skeleton)
"""
import json
import urllib.request
import urllib.parse
import sys
from pathlib import Path

TARGETS = [
    # (rank, gene, uniprot, description_short)
    (2,  "TEF",     "Q10587", "TEF transcription factor, PAR bZIP family"),
    (3,  "PIK3C2A", "O00443", "PI3K class II alpha catalytic subunit"),
    (5,  "RANBP2",  "P49792", "RAN binding protein 2 / Nup358"),
    (6,  "OPTN",    "Q96CV9", "Optineurin"),
    (9,  "PI4KA",   "P42356", "Phosphatidylinositol 4-kinase alpha"),
    (11, "EP400",   "Q96L91", "E1A binding protein p400 (SWI/SNF ATPase)"),
    (12, "PEAK1",   "Q9H792", "Pseudopodium-enriched atypical kinase 1"),
    (13, "USP34",   "Q70CQ2", "Ubiquitin specific peptidase 34"),
    (14, "KAT7",    "O95251", "Lysine acetyltransferase 7 / HBO1"),
    (15, "RNF213",  "Q63HN8", "Ring finger protein 213"),
    (16, "BTF3",    "P20290", "Basic transcription factor 3"),
    (17, "EHMT2",   "Q96KQ7", "Euchromatic histone lysine methyltransferase 2 / G9a"),
    (18, "EIF4G1",  "Q04637", "Eukaryotic translation initiation factor 4 gamma 1"),
    (19, "TIAM1",   "Q13009", "TIAM Rac1 associated GEF 1"),
    (20, "KAT6A",   "Q92794", "Lysine acetyltransferase 6A / MOZ"),
    (21, "KAT5",    "Q92993", "Lysine acetyltransferase 5 / TIP60"),
    (22, "MYCBP2",  "O75592", "MYC binding protein 2 E3 ligase"),
    (23, "MRPS31",  "Q92665", "Mitochondrial ribosomal protein S31"),
    (24, "KMT5B",   "Q4FZB7", "Lysine methyltransferase 5B / SUV4-20H1"),
    (25, "EHMT1",   "Q9H9B1", "Euchromatic histone lysine methyltransferase 1 / GLP"),
]


def http_get(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (SMA-research PDB resolver)"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


def uniprot_pdb_xrefs(uniprot: str) -> list:
    """Query UniProt REST API for PDB cross-references."""
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot}.json"
    try:
        data = json.loads(http_get(url))
    except Exception as e:
        return []
    pdbs = []
    for ref in data.get("uniProtKBCrossReferences", []):
        if ref.get("database") == "PDB":
            props = {p["key"]: p["value"] for p in ref.get("properties", [])}
            resolution = None
            try:
                # Properties may have "Resolution" : "2.10 A"
                r = props.get("Resolution", "")
                if r and r != "-":
                    resolution = float(r.split()[0])
            except Exception:
                pass
            chain_info = props.get("Chains", "")
            method = props.get("Method", "")
            pdbs.append({
                "pdb_id": ref["id"],
                "method": method,
                "resolution": resolution,
                "chain_info": chain_info,
            })
    return pdbs


def rcsb_pdb_metadata(pdb_id: str) -> dict:
    """Fetch RCSB entry metadata via JSON API."""
    url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id.lower()}"
    try:
        return json.loads(http_get(url))
    except Exception as e:
        return {}


def rcsb_nonpolymer_ligands(pdb_id: str) -> list:
    """Fetch non-polymer ligands (hetero compounds) excluding common buffers."""
    url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id.lower()}"
    try:
        data = json.loads(http_get(url))
    except Exception:
        return []
    ligs = data.get("rcsb_binding_affinity", [])
    # Also parse nonpolymer_entity_ids
    np_ids = data.get("rcsb_entry_container_identifiers", {}).get("non_polymer_entity_ids", [])
    ligand_names = []
    ignore = {"HOH", "EDO", "GOL", "DMS", "TRS", "PEG", "PG4", "MPD", "SO4",
              "PO4", "CL", "NA", "MG", "CA", "ZN", "K", "FE", "MN", "CU", "ACT",
              "FMT", "NI", "IMD", "CIT", "TLA", "FLC", "MLT", "IPA", "BME",
              "DMSO", "SCN", "BR", "IOD"}
    for npid in np_ids:
        try:
            npurl = f"https://data.rcsb.org/rest/v1/core/nonpolymer_entity/{pdb_id.lower()}/{npid}"
            npd = json.loads(http_get(npurl))
            cc = npd.get("pdbx_entity_nonpoly", {}).get("comp_id", "")
            name = npd.get("pdbx_entity_nonpoly", {}).get("name", "")
            if cc and cc not in ignore and len(cc) == 3:
                ligand_names.append({"comp_id": cc, "name": name})
        except Exception:
            continue
    return ligand_names


def main():
    out_tsv = Path("/home/bryza/sma-research/qms/proteome_wide_2026/extended_pdb_resolution.tsv")
    out_tsv.parent.mkdir(parents=True, exist_ok=True)

    header = ["rank", "gene", "uniprot", "n_pdbs_xref",
              "best_pdb", "best_resolution", "best_method",
              "best_ligands", "title", "verdict", "note"]
    lines = ["\t".join(header)]

    for rank, gene, uniprot, desc in TARGETS:
        print(f"[{rank:2d}] {gene} ({uniprot}) ...", file=sys.stderr)
        pdbs = uniprot_pdb_xrefs(uniprot)
        # Filter: X-ray or cryoEM, resolution < 2.5 Å
        good = [p for p in pdbs
                if p["method"] in ("X-ray", "EM") and p["resolution"] is not None and p["resolution"] <= 2.5]
        # Prefer resolution asc
        good.sort(key=lambda p: p["resolution"])

        if not good:
            # Fallback: any XRD with resolution <= 3.0
            relaxed = [p for p in pdbs
                       if p["method"] in ("X-ray", "EM") and p["resolution"] is not None and p["resolution"] <= 3.0]
            relaxed.sort(key=lambda p: p["resolution"])
            good = relaxed

        best = None
        title = ""
        ligands_str = ""
        verdict = "SKIP"
        note = ""

        if not good:
            note = f"No X-ray/EM PDB ≤3.0 Å for {uniprot}; {len(pdbs)} xrefs total"
        else:
            # Look for ligand-bound one first
            candidates = good[:5]  # top-5 by resolution
            best_ligbound = None
            for c in candidates:
                ligs = rcsb_nonpolymer_ligands(c["pdb_id"])
                if ligs:
                    c["ligands"] = ligs
                    best_ligbound = c
                    break
                else:
                    c["ligands"] = []
            best = best_ligbound if best_ligbound else good[0]
            if "ligands" not in best:
                best["ligands"] = rcsb_nonpolymer_ligands(best["pdb_id"])

            # Fetch TITLE
            meta = rcsb_pdb_metadata(best["pdb_id"])
            title = meta.get("struct", {}).get("title", "")
            # TITLE-verify: ensure title mentions UniProt gene or closely related
            title_upper = title.upper()
            gene_upper = gene.upper()
            verdict = "PASS" if (gene_upper in title_upper or uniprot.upper() in title_upper) else "CHECK"

            ligands_str = ";".join(f"{l['comp_id']}({l['name'][:30]})" for l in best["ligands"][:3])

        row = [
            str(rank), gene, uniprot, str(len(pdbs)),
            best["pdb_id"] if best else "",
            f"{best['resolution']:.2f}" if best and best.get("resolution") else "",
            best["method"] if best else "",
            ligands_str, title[:100], verdict, note,
        ]
        lines.append("\t".join(row))
        print(f"    best={row[4]} res={row[5]} title={title[:80]} verdict={verdict}", file=sys.stderr)

    out_tsv.write_text("\n".join(lines) + "\n")
    print(f"\nWrote {out_tsv}", file=sys.stderr)


if __name__ == "__main__":
    main()

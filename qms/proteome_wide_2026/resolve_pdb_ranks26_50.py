#!/usr/bin/env python3
"""Resolve best PDB + define pocket for atlas ranks 26-50 (Path D expansion).

For each of the 25 UniProts:
  1. Fetch UniProt entry (rest.uniprot.org) → collect all PDB xrefs
  2. Pick best: prefer X-ray < 2.5 A (relax to 3.0 A), ligand-bound preferred
  3. TITLE-verify via RCSB REST struct.title — reject on mismatch
  4. Fallback: AlphaFold DB (AF-<uniprot>-F1 v4 model) → AF_FALLBACK verdict
  5. Define pocket center from HETATM centroid (co-crystal ligand) if available;
     else literature/residue-based heuristic from RCSB polymer entity annotations;
     else AlphaFold centroid of full model.

Output: atlas_top50_pdb_verified.tsv with columns:
  rank, uniprot, gene, pdb, pdb_title, resolution, pocket_cx, pocket_cy, pocket_cz,
  pocket_radius, hotspot_residues, verified_status (PASS / SKIPPED / AF_FALLBACK)

Designed to be re-runnable; network retries are conservative.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from pathlib import Path
from typing import Optional

TARGETS = [
    # (rank, uniprot, gene, description)
    (26, "O60583", "CCNT2", "Cyclin T2 (P-TEFb complex)"),
    (27, "P17302", "GJA1", "Gap junction alpha 1 / Connexin-43 (N-term or CT domain)"),
    (28, "Q13155", "AIMP2", "Aminoacyl tRNA synthetase complex interacting multifunctional protein 2"),
    (29, "P43354", "NR4A2", "Nuclear receptor subfamily 4 group A member 2 / NURR1 LBD"),
    (30, "Q96HN2", "AHCYL2", "Adenosylhomocysteinase-like 2 (SAHH-like, IRBIT2)"),
    (31, "Q7LBC6", "KDM3B", "Lysine demethylase 3B (JHDM2B, JmjC Fe/2OG)"),
    (32, "O00566", "MPHOSPH10", "M-phase phosphoprotein 10 (U3 snoRNP component)"),
    (33, "Q9HCH5", "SYTL2", "Synaptotagmin-like 2 (SLP2, Rab27 effector)"),
    (34, "P41229", "KDM5C", "Lysine demethylase 5C / JARID1C (JmjC Fe/2OG)"),
    (35, "Q9BY66", "KDM5D", "Lysine demethylase 5D / JARID1D (JmjC Fe/2OG)"),
    (36, "Q8TEH3", "DENND1A", "DENN domain containing 1A (Rab35 GEF)"),
    (37, "Q96Q15", "SMG1", "SMG1 PI3K-related kinase (NMD pathway)"),
    (38, "Q12923", "PTPN13", "Protein tyrosine phosphatase non-receptor 13 (PTP-BL)"),
    (39, "P42166", "TMPO", "Thymopoietin / LAP2 (nuclear envelope, LEM domain)"),
    (40, "Q92800", "EZH1", "Enhancer of zeste 1 PRC2 SET-domain methyltransferase"),
    (41, "Q15811", "ITSN1", "Intersectin 1 (SH3 + EH domains, endocytic scaffold)"),
    (42, "Q9NSY1", "BMP2K", "BMP2 inducible kinase (BIKE, AAK1/GAK family)"),
    (43, "Q8N4C8", "MINK1", "Misshapen-like kinase 1 (STE20/Ste20-like)"),
    (44, "Q9Y5B6", "PAXBP1", "PAX3/PAX7 binding protein 1"),
    (45, "Q15648", "MED1", "Mediator complex subunit 1 / TRAP220"),
    (46, "Q8NDI1", "EHBP1", "EH domain binding protein 1"),
    (47, "P51531", "SMARCA2", "SWI/SNF BRM ATPase (bromo / ATPase domain)"),
    (48, "P02818", "BGLAP", "Bone gamma-carboxyglutamate protein / Osteocalcin"),
    (49, "Q2M2I8", "AAK1", "AP2-associated kinase 1 (Numb endocytic sorting)"),
    (50, "Q9UKE5", "TNIK", "TRAF2/NCK interacting kinase (STE20/Ste20-like)"),
]

UA = "Mozilla/5.0 (SMA-research atlas-ranks26-50)"
OUT_TSV = Path("/home/bryza/sma-research/qms/proteome_wide_2026/atlas_top50_pdb_verified.tsv")
AF_DIR = Path("/home/bryza/sma-research/qms/proteome_wide_2026/af_ranks26_50")
AF_DIR.mkdir(parents=True, exist_ok=True)

# Common non-drug / solvent / cofactor-only HET codes to ignore when picking "ligand-bound"
IGNORE_HETS = {
    "HOH", "DOD", "EDO", "GOL", "DMS", "TRS", "PEG", "PG4", "MPD", "SO4",
    "PO4", "CL", "NA", "MG", "CA", "ZN", "K", "FE", "MN", "CU", "ACT",
    "FMT", "NI", "IMD", "CIT", "TLA", "FLC", "MLT", "IPA", "BME", "DTT",
    "BOG", "BTB", "CO3", "NH4", "OH", "OHD", "OHH", "SCN", "BR", "IOD",
    "PO3", "ACE", "NAG", "MAN", "BMA", "FUC", "GLC", "GAL", "XYL", "NDG",
    # Cofactor but not "drug-bound" — keep as cofactor hint but score lower
}


def http_get(url: str, timeout: int = 40, retries: int = 2) -> str:
    last_err = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:
            last_err = e
            time.sleep(1.0 * (attempt + 1))
    raise RuntimeError(f"http_get failed after retries: {url} -> {last_err}")


def uniprot_pdb_xrefs(uniprot: str) -> list[dict]:
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot}.json"
    data = json.loads(http_get(url))
    pdbs = []
    for ref in data.get("uniProtKBCrossReferences", []):
        if ref.get("database") != "PDB":
            continue
        props = {p["key"]: p["value"] for p in ref.get("properties", [])}
        resolution: Optional[float] = None
        try:
            r = props.get("Resolution", "")
            if r and r not in ("-", "N/A"):
                resolution = float(r.split()[0])
        except Exception:
            pass
        pdbs.append({
            "pdb_id": ref["id"],
            "method": props.get("Method", ""),
            "resolution": resolution,
            "chains": props.get("Chains", ""),
        })
    return pdbs


def rcsb_entry(pdb_id: str) -> dict:
    url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id.lower()}"
    try:
        return json.loads(http_get(url))
    except Exception:
        return {}


def rcsb_nonpolymer_ligands(pdb_id: str) -> list[dict]:
    entry = rcsb_entry(pdb_id)
    np_ids = entry.get("rcsb_entry_container_identifiers", {}).get("non_polymer_entity_ids", [])
    ligs = []
    for npid in np_ids:
        try:
            url = f"https://data.rcsb.org/rest/v1/core/nonpolymer_entity/{pdb_id.lower()}/{npid}"
            npd = json.loads(http_get(url))
            cc = npd.get("pdbx_entity_nonpoly", {}).get("comp_id", "")
            name = npd.get("pdbx_entity_nonpoly", {}).get("name", "")
            if cc and cc not in IGNORE_HETS:
                ligs.append({"comp_id": cc, "name": name})
        except Exception:
            continue
    return ligs


def download_pdb(pdb_id: str, dest: Path) -> Path:
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    try:
        urllib.request.urlretrieve(url, str(dest))
    except Exception:
        # Try alternative (lower-case)
        try:
            urllib.request.urlretrieve(f"https://files.rcsb.org/download/{pdb_id.lower()}.pdb", str(dest))
        except Exception:
            return dest  # return empty path on failure
    return dest


def download_af(uniprot: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 0:
        return True
    url = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot}-F1-model_v4.pdb"
    try:
        urllib.request.urlretrieve(url, str(dest))
        return dest.stat().st_size > 0
    except Exception:
        return False


def parse_atoms_het(pdb_path: Path, target_hets: set[str] | None = None):
    atoms = []
    hets: dict[str, list] = {}
    if not pdb_path.exists() or pdb_path.stat().st_size == 0:
        return atoms, hets
    try:
        with open(pdb_path) as fh:
            for line in fh:
                if line.startswith("ATOM  "):
                    try:
                        x = float(line[30:38]); y = float(line[38:46]); z = float(line[46:54])
                        chain = line[21]
                        resn = line[17:20].strip()
                        resi = int(line[22:26])
                        atoms.append((chain, resn, resi, x, y, z))
                    except Exception:
                        continue
                elif line.startswith("HETATM"):
                    resn = line[17:20].strip()
                    if resn in IGNORE_HETS:
                        continue
                    if target_hets is not None and resn not in target_hets:
                        continue
                    try:
                        x = float(line[30:38]); y = float(line[38:46]); z = float(line[46:54])
                        hets.setdefault(resn, []).append((x, y, z))
                    except Exception:
                        continue
    except Exception:
        pass
    return atoms, hets


def centroid(points):
    if not points:
        return None
    n = len(points)
    return [round(sum(p[i] for p in points) / n, 2) for i in (0, 1, 2)]


def closest_residues(atoms, center, radius=8.0, limit=8):
    if not atoms or not center:
        return []
    cx, cy, cz = center
    best = []
    for (chain, resn, resi, x, y, z) in atoms:
        d2 = (x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2
        best.append((d2, chain, resn, resi))
    best.sort()
    seen = set()
    result = []
    for d2, chain, resn, resi in best:
        key = (chain, resi)
        if key in seen:
            continue
        seen.add(key)
        if d2 ** 0.5 <= radius * 1.5:  # slightly expanded for hotspot list
            result.append(f"{resn}{resi}{chain}")
        if len(result) >= limit:
            break
    return result


# Hints for picking a meaningful PDB + pocket when ligand-bound unavailable.
# Keys: gene. Values: list of regex fragments we want to see in RCSB title to PASS.
GENE_TITLE_HINTS = {
    "CCNT2": [r"CYCLIN\s*T", r"P-?TEFB", r"CDK9"],
    "GJA1": [r"CONNEXIN", r"GJA1", r"CX43"],
    "AIMP2": [r"AIMP2", r"P38", r"P38\s*JTV1", r"GST\s*DOMAIN"],
    "NR4A2": [r"NURR", r"NR4A2"],
    "AHCYL2": [r"AHCYL", r"S-?ADENOSYL", r"IRBIT"],
    "KDM3B": [r"KDM3B", r"JMJD1B", r"JHDM2B"],
    "MPHOSPH10": [r"MPHOSPH10", r"U3 SNORNP", r"MPP10"],
    "SYTL2": [r"SYTL", r"SLP2", r"RAB27", r"SHD"],
    "KDM5C": [r"KDM5C", r"JARID1C"],
    "KDM5D": [r"KDM5D", r"JARID1D"],
    "DENND1A": [r"DENND1A", r"DENN"],
    "SMG1": [r"SMG1", r"NONSENSE", r"NMD"],
    "PTPN13": [r"PTPN13", r"PTP-?BL", r"FAP-?1"],
    "TMPO": [r"LAP2", r"TMPO", r"THYMOPOIETIN", r"LEM"],
    "EZH1": [r"EZH1", r"PRC2"],
    "ITSN1": [r"INTERSECTIN", r"ITSN", r"DH\s*PH", r"EH\s*DOMAIN", r"SH3"],
    "BMP2K": [r"BMP2K", r"BIKE"],
    "MINK1": [r"MINK", r"MISSHAPEN"],
    "PAXBP1": [r"PAXBP", r"PAX3", r"PAX7"],
    "MED1": [r"MED1", r"MEDIATOR", r"TRAP220"],
    "EHBP1": [r"EHBP", r"EH\s*DOMAIN"],
    "SMARCA2": [r"SMARCA2", r"BRM", r"BAF\s*COMPLEX", r"BROMODOMAIN"],
    "BGLAP": [r"OSTEOCALCIN", r"BGLAP", r"BONE\s*GLA"],
    "AAK1": [r"AAK1", r"ADAPTER-?ASSOCIATED\s*KINASE"],
    "TNIK": [r"TNIK", r"TRAF2\s*AND\s*NCK"],
}


def title_verify(gene: str, title: str, uniprot: str) -> bool:
    """Rule-dataset-verify-before-use: confirm title plausibly matches expected gene."""
    if not title:
        return False
    t = title.upper()
    if gene.upper() in t:
        return True
    if uniprot.upper() in t:
        return True
    patterns = GENE_TITLE_HINTS.get(gene.upper(), [])
    for p in patterns:
        if re.search(p, t):
            return True
    return False


def pick_best_pdb(gene: str, uniprot: str, pdbs: list[dict]) -> tuple[Optional[dict], str]:
    """Return (chosen_pdb_dict_with_title_ligands_or_None, reason)."""
    # Filter to experimental structures with reasonable resolution
    xrd = [p for p in pdbs
           if p.get("method") in ("X-ray", "EM") and p.get("resolution") is not None]
    good = [p for p in xrd if p["resolution"] <= 2.5]
    if not good:
        good = [p for p in xrd if p["resolution"] <= 3.0]
    if not good:
        good = xrd  # last resort: any with known res
    if not good:
        return None, "no_experimental_pdb"

    good.sort(key=lambda p: p["resolution"])
    # Walk top-8 by resolution, prefer first one that TITLE-verifies AND is ligand-bound
    tv_pass = []
    candidates = good[:8]
    for c in candidates:
        entry = rcsb_entry(c["pdb_id"])
        title = entry.get("struct", {}).get("title", "")
        c["title"] = title
        if not title_verify(gene, title, uniprot):
            continue
        ligs = rcsb_nonpolymer_ligands(c["pdb_id"])
        c["ligands"] = ligs
        tv_pass.append(c)
    if not tv_pass:
        # None title-verified among top-8. Widen to 20.
        for c in good[8:20]:
            entry = rcsb_entry(c["pdb_id"])
            title = entry.get("struct", {}).get("title", "")
            c["title"] = title
            if not title_verify(gene, title, uniprot):
                continue
            ligs = rcsb_nonpolymer_ligands(c["pdb_id"])
            c["ligands"] = ligs
            tv_pass.append(c)
    if not tv_pass:
        return None, f"no_title_match_in_top20_of_{len(good)}"

    # Prefer ligand-bound (drug-like HET) at reasonable resolution
    lig_bound = [p for p in tv_pass if p.get("ligands")]
    if lig_bound:
        lig_bound.sort(key=lambda p: p["resolution"])
        return lig_bound[0], "title_verified_ligand_bound"
    # else best resolution title-verified
    tv_pass.sort(key=lambda p: p["resolution"])
    return tv_pass[0], "title_verified_apo"


def define_pocket(pdb_id: str, chosen: dict, gene: str, uniprot: str, work_dir: Path):
    """Return (center_xyz, radius, hotspot_residues, strategy)."""
    pdb_path = work_dir / f"{pdb_id}.pdb"
    download_pdb(pdb_id, pdb_path)

    target_hets = {l["comp_id"] for l in chosen.get("ligands", []) if l.get("comp_id")}
    atoms, hets = parse_atoms_het(pdb_path, target_hets=target_hets if target_hets else None)

    if hets:
        # pick largest HET cluster by atom count
        best_het = max(hets.items(), key=lambda kv: len(kv[1]))
        center = centroid(best_het[1])
        if center:
            hotspots = closest_residues(atoms, center, radius=6.0, limit=8)
            return center, 10.0, hotspots, f"ligand_{best_het[0]}_centroid"

    # No usable HET: use backbone CA centroid of first polymer chain
    if atoms:
        # use first chain's midpoint as a weak fallback
        first_chain = atoms[0][0]
        first_chain_atoms = [a for a in atoms if a[0] == first_chain]
        center = centroid([(a[3], a[4], a[5]) for a in first_chain_atoms])
        if center:
            hotspots = closest_residues(atoms, center, radius=8.0, limit=8)
            return center, 10.0, hotspots, f"apo_chain{first_chain}_centroid_LITERATURE_REFINE_NEEDED"

    return None, 10.0, [], "no_atoms"


def af_pocket(uniprot: str, work_dir: Path):
    """AlphaFold fallback: use whole-model centroid + flag for refinement."""
    af_path = work_dir / f"AF-{uniprot}-F1-model_v4.pdb"
    if not download_af(uniprot, af_path):
        return None, 10.0, [], "af_download_failed"
    atoms, _ = parse_atoms_het(af_path)
    if not atoms:
        return None, 10.0, [], "af_no_atoms"
    center = centroid([(a[3], a[4], a[5]) for a in atoms])
    hotspots = closest_residues(atoms, center, radius=10.0, limit=8)
    return center, 10.0, hotspots, "af_fullmodel_centroid_REFINE_NEEDED"


def main():
    header = [
        "rank", "uniprot", "gene", "pdb", "pdb_title", "resolution",
        "pocket_cx", "pocket_cy", "pocket_cz", "pocket_radius",
        "hotspot_residues", "verified_status", "note",
    ]
    lines = ["\t".join(header)]

    for rank, uniprot, gene, desc in TARGETS:
        print(f"[rank {rank:2d}] {gene} ({uniprot}) — {desc}", file=sys.stderr)
        note_parts = []
        try:
            pdbs = uniprot_pdb_xrefs(uniprot)
        except Exception as e:
            pdbs = []
            note_parts.append(f"uniprot_err={e}")
        chosen, reason = (None, "no_pdbs")
        if pdbs:
            try:
                chosen, reason = pick_best_pdb(gene, uniprot, pdbs)
            except Exception as e:
                reason = f"pick_err:{e}"
                chosen = None

        status = "SKIPPED"
        pdb_id = ""
        title = ""
        resolution = ""
        pocket = (None, 10.0, [], "")
        if chosen is not None:
            pdb_id = chosen["pdb_id"]
            title = chosen.get("title", "")[:120]
            resolution = f"{chosen['resolution']:.2f}" if chosen.get("resolution") is not None else ""
            status = "PASS"
            try:
                pocket = define_pocket(pdb_id, chosen, gene, uniprot, AF_DIR)
            except Exception as e:
                note_parts.append(f"pocket_err:{e}")
        else:
            note_parts.append(reason)

        # AlphaFold fallback if no PDB or pocket failed badly
        if chosen is None:
            try:
                af_center, af_r, af_hot, af_strategy = af_pocket(uniprot, AF_DIR)
                if af_center:
                    pdb_id = f"AF-{uniprot}"
                    title = f"AlphaFold-DB v4 model for {uniprot}"
                    resolution = "AF"
                    pocket = (af_center, af_r, af_hot, af_strategy)
                    status = "AF_FALLBACK"
                    note_parts.append("used_alphafold_model")
            except Exception as e:
                note_parts.append(f"af_err:{e}")

        center, radius, hotspots, strategy = pocket
        cx = cy = cz = ""
        if center:
            cx, cy, cz = [str(v) for v in center]
        note_parts.append(f"strategy={strategy}")
        row = [
            str(rank), uniprot, gene, pdb_id, title, resolution,
            cx, cy, cz, f"{radius:.1f}",
            ";".join(hotspots),
            status, "|".join(note_parts),
        ]
        lines.append("\t".join(row))
        print(f"    -> {status} pdb={pdb_id} res={resolution} strategy={strategy}",
              file=sys.stderr)
        # be gentle to APIs
        time.sleep(0.3)

    OUT_TSV.write_text("\n".join(lines) + "\n")
    print(f"\nWrote {OUT_TSV}", file=sys.stderr)


if __name__ == "__main__":
    main()

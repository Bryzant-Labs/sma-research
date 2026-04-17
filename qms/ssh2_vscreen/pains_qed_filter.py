#!/usr/bin/env python3
"""
SSH2 vscreen post-DiffDock PAINS + drug-likeness filter.

Input:  diffdock_ssh2_ranked.tsv  (c_rel sorted)
Output: top100_druglike.tsv        (for Phase 3 Boltz-2 cross-phosphatase rescore)

Target-agnostic filters (same as SSH1 Phase 2 filter):
  - RDKit PAINS A+B+C catalog
  - QED >= 0.40
  - MW 200-500
  - aromatic rings >= 1
  - heavy atoms >= 12
  - formal charge in [-2, +2]

Rationale: DiffDock C_rel baseline on SSH2 was calibrated against sanguinarine,
SP-2509, BCI — NO SSH-family co-crystal exists (CAVEAT documented in
RESULTS_DRAFT). Same reference trio as SSH1 ensures cross-paralog C_rel
comparability.
"""
import csv
import sys
from rdkit import Chem
from rdkit.Chem import QED, Descriptors, FilterCatalog, rdMolDescriptors
from rdkit import RDLogger
RDLogger.DisableLog("rdApp.*")

IN = "diffdock_ssh2_ranked.tsv"
OUT_ALL = "diffdock_ssh2_filtered.tsv"
OUT_TOP = "top100_druglike.tsv"

params = FilterCatalog.FilterCatalogParams()
params.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS_A)
params.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS_B)
params.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS_C)
pains = FilterCatalog.FilterCatalog(params)

rows = list(csv.DictReader(open(IN), delimiter="\t"))
print(f"input: {len(rows)} rows")

pos = [r for r in rows if float(r["c_rel"]) > 0]
print(f"  c_rel > 0: {len(pos)}")

kept = []
rejected = {"parse": 0, "pains": 0, "qed": 0, "mw": 0, "aromatic": 0,
            "heavy": 0, "charge": 0}
for r in pos:
    smi = r["smiles"]
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        rejected["parse"] += 1
        continue
    hit = pains.GetFirstMatch(mol)
    if hit is not None:
        rejected["pains"] += 1
        r["reject"] = f"PAINS:{hit.GetDescription()}"
        continue
    q = QED.qed(mol)
    if q < 0.40:
        rejected["qed"] += 1
        continue
    mw = Descriptors.MolWt(mol)
    if mw < 200 or mw > 500:
        rejected["mw"] += 1
        continue
    arom = rdMolDescriptors.CalcNumAromaticRings(mol)
    if arom < 1:
        rejected["aromatic"] += 1
        continue
    ha = mol.GetNumHeavyAtoms()
    if ha < 12:
        rejected["heavy"] += 1
        continue
    fc = Chem.GetFormalCharge(mol)
    if abs(fc) > 2:
        rejected["charge"] += 1
        continue
    r["qed"] = f"{q:.3f}"
    r["mw"] = f"{mw:.1f}"
    r["aromatic_rings"] = str(arom)
    r["heavy_atoms"] = str(ha)
    r["formal_charge"] = str(fc)
    kept.append(r)

print(f"  rejected: {rejected}")
print(f"  kept: {len(kept)}")

kept.sort(key=lambda r: float(r["c_rel"]), reverse=True)

fields = ["chembl_id", "smiles", "top_conf", "c_rel",
          "qed", "mw", "aromatic_rings", "heavy_atoms", "formal_charge"]
with open(OUT_ALL, "w") as f:
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t",
                       extrasaction="ignore")
    w.writeheader()
    w.writerows(kept)
with open(OUT_TOP, "w") as f:
    w = csv.DictWriter(f, fieldnames=fields, delimiter="\t",
                       extrasaction="ignore")
    w.writeheader()
    w.writerows(kept[:100])

print(f"wrote {OUT_ALL} ({len(kept)}) and {OUT_TOP} ({min(100,len(kept))})")
print()
print("top 10 after filter:")
for r in kept[:10]:
    print(f"  {r['chembl_id']:<14} c_rel={float(r['c_rel']):+.3f}  QED={r['qed']}  MW={r['mw']}  {r['smiles']}")

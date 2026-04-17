#!/usr/bin/env python3
"""
SSH1 vscreen post-DiffDock PAINS + drug-likeness filter.

Input:  diffdock_ssh1_ranked.tsv  (414 rows, c_rel sorted)
Output: top100_druglike.tsv        (for Phase 3 Boltz-2 rescore)

Filters applied to compounds with c_rel > 0:
  - RDKit PAINS A+B+C catalog (rejects quinones, rhodanines, Michael acceptors,
    charged hydrazones, etc.)
  - QED >= 0.40
  - Mw 200-500
  - aromatic rings >= 1  (rejects pure aliphatic fragments like adamantane amine,
    tetraethylammonium)
  - heavy atoms >= 12    (rejects fragment-level hits below lead-like size)
  - formal charge in [-2, +2]  (rejects quaternary ammonium like CHEMBL9324)

Rationale: DiffDock C_rel baseline on SSH1 was calibrated against sanguinarine
(natural SSH1 activator, weak binder), SP-2509 (LSD1 inhibitor, off-pocket
control), and BCI (DUSP6 inhibitor, related fold). Median top_conf = -1.45 is
permissive; as a result the top-414 includes non-pocket-binders.  These filters
clean the pool before the Boltz-2 + cross-phosphatase z-panel step.
"""
import csv
import sys
from rdkit import Chem
from rdkit.Chem import QED, Descriptors, FilterCatalog, rdMolDescriptors
from rdkit import RDLogger
RDLogger.DisableLog("rdApp.*")

IN = "diffdock_ssh1_ranked.tsv"
OUT_ALL = "diffdock_ssh1_filtered.tsv"
OUT_TOP = "top100_druglike.tsv"

# PAINS A+B+C
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

# sort by c_rel desc (already sorted, but be explicit)
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

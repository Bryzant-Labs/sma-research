#!/usr/bin/env python3
"""Verify C51-C65 disulfide preservation across ALL Round 1 ECL1 binders."""
import json
import math
from pathlib import Path
from Bio.PDB import PDBParser

# All ECL1 top 5 Boltz-2 co-fold targets
TARGETS = [
    ("H1a_38_s7", "/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/ecl1/H1a/H1a_38_s7_target.pdb"),
    ("H1c_25_s4", "/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/ecl1/H1c/H1c_25_s4_target.pdb"),
    ("H1c_25_s5", "/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/ecl1/H1c/H1c_25_s5_target.pdb"),
    ("H1b_14_s6", "/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/ecl1/H1b/H1b_14_s6_target.pdb"),
    ("H1b_10_s3", "/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/ecl1/H1b/H1b_10_s3_target.pdb"),
    ("H2b_9_s2",  "/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/ecl2/H2b/H2b_9_s2_target.pdb"),
    ("H2c_11_s1", "/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/ecl2/H2c/H2c_11_s1_target.pdb"),
    ("H2b_3_s4",  "/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/ecl2/H2b/H2b_3_s4_target.pdb"),
    ("H2a_1_s5",  "/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/ecl2/H2a/H2a_1_s5_target.pdb"),
    ("H2c_26_s4", "/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/ecl2/H2c/H2c_26_s4_target.pdb"),
    ("PERP_AF_reference", "/home/bryza/fleet-results/perp_binder_design_FINAL/PERP_AF.pdb"),
    ("PERP_ECL1core_reference", "/home/bryza/fleet-results/perp_binder_design_FINAL/PERP_ECL1core.pdb"),
]

parser = PDBParser(QUIET=True)
rows = []
for name, path in TARGETS:
    try:
        s = parser.get_structure("x", path)
        c51 = s[0]["A"][51]["SG"]
        c65 = s[0]["A"][65]["SG"]
        d = math.sqrt(sum((c51.coord[k]-c65.coord[k])**2 for k in range(3)))
        # Also ChiSS angle proxy: CA-CB-SG-SG-CB-CA torsion not measured here (dist sufficient for SS call)
        # Record Cα-Cα distance to track overall loop conformation
        ca51 = s[0]["A"][51]["CA"]
        ca65 = s[0]["A"][65]["CA"]
        ca_d = math.sqrt(sum((ca51.coord[k]-ca65.coord[k])**2 for k in range(3)))
        ss_intact = d < 3.0
        rows.append({
            "name": name,
            "SG_SG_dist_A": round(d, 2),
            "CA_CA_dist_A": round(ca_d, 2),
            "SS_bond_intact": ss_intact,
        })
    except Exception as e:
        rows.append({"name": name, "error": str(e)})

print(f"{'name':27s} {'SG-SG':>7s} {'CA-CA':>7s} {'SS?':>5s}")
for r in rows:
    if "error" in r:
        print(f"{r['name']:27s} ERROR: {r['error']}")
    else:
        print(f"{r['name']:27s} {r['SG_SG_dist_A']:>7.2f} {r['CA_CA_dist_A']:>7.2f} {'YES' if r['SS_bond_intact'] else 'NO':>5s}")

Path("/home/bryza/sma-research/qms/PERP_dossier/disulfide_rerun/disulfide_preservation.json").write_text(
    json.dumps(rows, indent=2)
)

#!/usr/bin/env python
"""Phase A step 3: solvate with TIP3P-FB in a rectangular box (1.0 nm padding)
and neutralise + 0.15 M NaCl.

We use OpenMM's Modeller.addSolvent because it plays nicely with the
protein.ff14SB + tip3pfb.xml force fields we will use for both the OpenMM
path (if GROMACS is unavailable on Nebius) AND as a reference topology.

Rationale for AMBER14SB (== ff14SB):
- matches prior MD campaigns on this fleet (see learnings-gpu-fleet-2026-04-14)
- well-calibrated for rigid membrane-adjacent protein assemblies
- compatible with TIP3P-FB water (Wang et al. 2014) via the tip3pfb.xml
  bundled with OpenMM 8.x

Outputs:
  nmj_12chain_solvated.pdb
  nmj_12chain_system.xml         (OpenMM serialized System w/ 4 fs HMR)
  nmj_12chain_topology.pdb       (for MDAnalysis / AmberTools)
  solvation_stats.json
"""
from __future__ import annotations
import json
import time
from pathlib import Path
from openmm import (
    LangevinMiddleIntegrator,
    Platform,
    XmlSerializer,
    MonteCarloBarostat,
    unit,
)
from openmm.app import (
    PDBFile,
    Modeller,
    ForceField,
    PME,
    HBonds,
    Simulation,
)

PREP = Path("/home/bryza/sma-research/qms/NMJ_MD_breakthrough/prep")
INP = PREP / "nmj_12chain_fixed_pH74.pdb"
OUT_PDB = PREP / "nmj_12chain_solvated.pdb"
OUT_SYS = PREP / "nmj_12chain_system.xml"
OUT_STATS = PREP / "solvation_stats.json"

def main() -> None:
    t0 = time.time()
    print(f"[solv] loading {INP}")
    pdb = PDBFile(str(INP))

    ff = ForceField("amber14-all.xml", "amber14/tip3pfb.xml")
    # Note: OpenMM's amber14-all.xml corresponds to AMBER ff14SB for proteins.

    modeller = Modeller(pdb.topology, pdb.positions)

    # Re-add hydrogens according to the force-field's definitions so we get
    # a topology that is guaranteed consistent with amber14.
    modeller.addHydrogens(ff, pH=7.4)

    n_protein_atoms = sum(1 for _ in modeller.topology.atoms())
    print(f"[solv] protein atoms (after FF-consistent H): {n_protein_atoms}")

    # Solvate with TIP3P-FB, 1.0 nm padding, rectangular box, 0.15 M NaCl
    modeller.addSolvent(
        ff,
        model="tip3p",   # tip3pfb shares the 3-point geometry
        padding=1.0 * unit.nanometer,
        ionicStrength=0.15 * unit.molar,
        positiveIon="Na+",
        negativeIon="Cl-",
        neutralize=True,
    )

    n_total = sum(1 for _ in modeller.topology.atoms())
    n_water = 0
    n_na = 0
    n_cl = 0
    for res in modeller.topology.residues():
        if res.name in ("HOH", "WAT"):
            n_water += 1
        elif res.name == "NA":
            n_na += 1
        elif res.name == "CL":
            n_cl += 1

    # Build the System with HMR for 4 fs timesteps
    system = ff.createSystem(
        modeller.topology,
        nonbondedMethod=PME,
        nonbondedCutoff=1.0 * unit.nanometer,
        constraints=HBonds,
        hydrogenMass=4.0 * unit.amu,   # HMR
        rigidWater=True,
    )
    # Add a Monte-Carlo barostat for later NPT; we'll activate/deactivate
    # by force index in the run script.
    system.addForce(MonteCarloBarostat(1.0 * unit.bar, 300 * unit.kelvin, 25))

    with OUT_SYS.open("w") as fh:
        fh.write(XmlSerializer.serialize(system))

    with OUT_PDB.open("w") as fh:
        PDBFile.writeFile(modeller.topology, modeller.positions, fh, keepIds=True)

    box = modeller.topology.getPeriodicBoxVectors()
    box_nm = [[v.value_in_unit(unit.nanometer) for v in row] for row in box]

    stats = {
        "protein_atoms": n_protein_atoms,
        "total_atoms": n_total,
        "n_waters": n_water,
        "n_Na": n_na,
        "n_Cl": n_cl,
        "ionic_strength_M": 0.15,
        "water_model": "TIP3P-FB (geometry via tip3p)",
        "forcefield": "amber14-all.xml (ff14SB) + amber14/tip3pfb.xml",
        "padding_nm": 1.0,
        "box_vectors_nm": box_nm,
        "pH_used_for_H": 7.4,
        "hydrogen_mass_repartitioning_amu": 4.0,
        "timestep_compatible_fs": 4,
        "pdb": str(OUT_PDB),
        "system_xml": str(OUT_SYS),
        "elapsed_s": round(time.time() - t0, 1),
    }
    OUT_STATS.write_text(json.dumps(stats, indent=2))
    for k, v in stats.items():
        print(f"[solv] {k} = {v}")

if __name__ == "__main__":
    main()

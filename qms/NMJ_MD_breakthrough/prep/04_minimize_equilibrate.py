#!/usr/bin/env python
"""Phase B: minimise + NVT + NPT equilibrate the solvated NMJ 12-chain system.

Loads the serialized System.xml from Phase A step 3 and the solvated PDB,
runs:
  1. L-BFGS minimisation (tolerance 10 kJ/mol/nm, maxIterations=10000)
  2. NVT heat 10 -> 300 K over 250 ps with 10 kcal/mol/A^2 positional restraint
     on all protein CA atoms
  3. NPT at 300 K / 1 bar for 1 ns with gradual restraint release
     (50 -> 10 -> 2 -> 0 kcal/mol/A^2 CA restraint)

Writes checkpoints and state PDBs after each stage for provenance.
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

from openmm import (
    LangevinMiddleIntegrator,
    MonteCarloBarostat,
    Platform,
    XmlSerializer,
    CustomExternalForce,
    unit,
)
from openmm.app import PDBFile, Simulation, StateDataReporter, DCDReporter, CheckpointReporter

PREP = Path("/workspace/nmj_md/prep")
OUT = Path("/workspace/nmj_md/production")
LOGS = Path("/workspace/nmj_md/logs")
OUT.mkdir(parents=True, exist_ok=True)
LOGS.mkdir(parents=True, exist_ok=True)

SOLV_PDB = PREP / "nmj_12chain_solvated.pdb"
SYS_XML = PREP / "nmj_12chain_system.xml"
REP = sys.argv[1] if len(sys.argv) > 1 else "rep0"
GPU = sys.argv[2] if len(sys.argv) > 2 else "0"
REP_DIR = OUT / REP
REP_DIR.mkdir(parents=True, exist_ok=True)

MIN_PDB = REP_DIR / "min.pdb"
NVT_PDB = REP_DIR / "nvt.pdb"
NPT_PDB = REP_DIR / "npt.pdb"
NPT_CPT = REP_DIR / "npt.chk"
STATS = REP_DIR / "equilibration_stats.json"
LOG = LOGS / f"equilibrate_{REP}.log"

def add_ca_restraint(system, positions, k_kcal_per_A2: float):
    """Add a CustomExternalForce CA positional restraint. Returns force index."""
    k_openmm = k_kcal_per_A2 * 4.184 * 100.0   # kcal/(mol*A^2) -> kJ/(mol*nm^2)
    force = CustomExternalForce("0.5*k*periodicdistance(x,y,z,x0,y0,z0)^2")
    force.addGlobalParameter("k", k_openmm * unit.kilojoule_per_mole / unit.nanometer**2)
    force.addPerParticleParameter("x0")
    force.addPerParticleParameter("y0")
    force.addPerParticleParameter("z0")
    return force

def main() -> None:
    t0 = time.time()
    print(f"[equil] replicate={REP} GPU={GPU}")
    pdb = PDBFile(str(SOLV_PDB))
    with SYS_XML.open() as fh:
        system = XmlSerializer.deserialize(fh.read())

    # Build CA restraint force
    ca_indices = []
    for atom in pdb.topology.atoms():
        if atom.name == "CA" and atom.residue.chain.id in "ACBDEFGIJKPZ":
            ca_indices.append(atom.index)
    print(f"[equil] CA atoms restrained: {len(ca_indices)}")

    restraint = add_ca_restraint(system, pdb.positions, 10.0)  # 10 kcal/mol/A^2
    for idx in ca_indices:
        pos = pdb.positions[idx].value_in_unit(unit.nanometer)
        restraint.addParticle(idx, [pos[0], pos[1], pos[2]])
    r_idx = system.addForce(restraint)

    # Disable barostat during minimisation + NVT
    for i, f in enumerate(system.getForces()):
        if isinstance(f, MonteCarloBarostat):
            barostat_idx = i
            f.setFrequency(0)   # disabled
            break

    integrator = LangevinMiddleIntegrator(10 * unit.kelvin, 1.0 / unit.picosecond, 0.002 * unit.picosecond)
    platform = Platform.getPlatformByName("CUDA")
    props = {"DeviceIndex": GPU, "Precision": "mixed"}
    simulation = Simulation(pdb.topology, system, integrator, platform, props)
    simulation.context.setPositions(pdb.positions)

    # Stage 1: minimise
    print(f"[equil] stage 1: minimise")
    simulation.minimizeEnergy(tolerance=10.0 * unit.kilojoule_per_mole / unit.nanometer, maxIterations=10000)
    st = simulation.context.getState(getPositions=True, enforcePeriodicBox=True)
    with MIN_PDB.open("w") as fh:
        PDBFile.writeFile(simulation.topology, st.getPositions(), fh, keepIds=True)

    # Stage 2: NVT heat 10 -> 300 K over 250 ps (2 fs timestep) w/ 10 kcal/mol/A^2 CA restraint
    print(f"[equil] stage 2: NVT heat 10 -> 300 K, 250 ps, 2 fs, 10 kcal/mol/A^2")
    simulation.reporters.append(StateDataReporter(str(LOG.with_suffix(".nvt.log")), 5000,
        step=True, temperature=True, potentialEnergy=True, kineticEnergy=True, volume=True, density=True, speed=True, separator="\t"))
    simulation.reporters.append(DCDReporter(str(REP_DIR / "nvt.dcd"), 5000))

    n_steps_nvt = 125000   # 250 ps @ 2 fs
    temperatures = [10 + i * (290.0 / 50) for i in range(51)]
    chunk = n_steps_nvt // 50
    for T in temperatures[:-1]:
        integrator.setTemperature(T * unit.kelvin)
        simulation.step(chunk)
    integrator.setTemperature(300.0 * unit.kelvin)
    simulation.step(n_steps_nvt - chunk * 50)

    st = simulation.context.getState(getPositions=True, enforcePeriodicBox=True)
    with NVT_PDB.open("w") as fh:
        PDBFile.writeFile(simulation.topology, st.getPositions(), fh, keepIds=True)

    # Stage 3: NPT equilibrate 1 ns w/ staged restraint release
    #   switch to 4 fs HMR now; activate barostat
    print(f"[equil] stage 3: NPT 1 ns, 4 fs HMR, restraint 10 -> 2 -> 0 kcal/mol/A^2")
    # Re-create integrator at 4 fs
    new_integrator = LangevinMiddleIntegrator(300 * unit.kelvin, 1.0 / unit.picosecond, 0.004 * unit.picosecond)
    # We must rebuild the simulation to swap integrator. Persist state first.
    state = simulation.context.getState(getPositions=True, getVelocities=True, enforcePeriodicBox=True)
    # Activate barostat
    for f in system.getForces():
        if isinstance(f, MonteCarloBarostat):
            f.setFrequency(25)
    simulation = Simulation(pdb.topology, system, new_integrator, platform, props)
    simulation.context.setState(state)

    simulation.reporters.clear()
    simulation.reporters.append(StateDataReporter(str(LOG.with_suffix(".npt.log")), 2500,
        step=True, temperature=True, potentialEnergy=True, volume=True, density=True, speed=True, separator="\t"))
    simulation.reporters.append(DCDReporter(str(REP_DIR / "npt.dcd"), 2500))

    # Schedule: 250 ps at k=10, 250 ps at k=2, 500 ps at k=0
    schedules = [(10.0, 62500), (2.0, 62500), (0.0, 125000)]
    for k_kcal, n_steps in schedules:
        k_openmm = k_kcal * 4.184 * 100.0
        simulation.context.setParameter("k", k_openmm)
        simulation.step(n_steps)

    st = simulation.context.getState(getPositions=True, enforcePeriodicBox=True)
    with NPT_PDB.open("w") as fh:
        PDBFile.writeFile(simulation.topology, st.getPositions(), fh, keepIds=True)
    simulation.saveCheckpoint(str(NPT_CPT))

    stats = {
        "replicate": REP,
        "gpu": GPU,
        "min_pdb": str(MIN_PDB),
        "nvt_pdb": str(NVT_PDB),
        "npt_pdb": str(NPT_PDB),
        "npt_checkpoint": str(NPT_CPT),
        "n_CA_restrained": len(ca_indices),
        "nvt_ps": 250.0,
        "npt_ns": 1.0,
        "elapsed_s": round(time.time() - t0, 1),
    }
    STATS.write_text(json.dumps(stats, indent=2))
    print(f"[equil] done: {stats}")

if __name__ == "__main__":
    main()

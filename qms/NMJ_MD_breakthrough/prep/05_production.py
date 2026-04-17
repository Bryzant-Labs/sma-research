#!/usr/bin/env python
"""Phase C: 100 ns production MD with 4 fs HMR. Starts from Phase B NPT checkpoint.

Writes:
  prod.dcd    (frames every 100 ps = 25 000 steps @ 4 fs)
  prod.log    (tab-separated state data every 10 ps)
  prod.chk    (every 5 ns checkpoint)

Args: <rep_name> <gpu_index>
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

from openmm import LangevinMiddleIntegrator, MonteCarloBarostat, Platform, XmlSerializer, unit
from openmm.app import PDBFile, Simulation, StateDataReporter, DCDReporter, CheckpointReporter

PREP = Path("/workspace/nmj_md/prep")
OUT = Path("/workspace/nmj_md/production")
LOGS = Path("/workspace/nmj_md/logs")

SOLV_PDB = PREP / "nmj_12chain_solvated.pdb"
SYS_XML = PREP / "nmj_12chain_system.xml"
REP = sys.argv[1] if len(sys.argv) > 1 else "rep0"
GPU = sys.argv[2] if len(sys.argv) > 2 else "0"
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 42
REP_DIR = OUT / REP

NPT_CPT = REP_DIR / "npt.chk"
PROD_DCD = REP_DIR / "prod.dcd"
PROD_LOG = REP_DIR / "prod.log"
PROD_CPT = REP_DIR / "prod.chk"
STATS = REP_DIR / "production_stats.json"

STEPS_PER_NS = 250000   # @ 4 fs
TARGET_NS = 100.0
TOTAL_STEPS = int(TARGET_NS * STEPS_PER_NS)
FRAME_INTERVAL = 25000   # 100 ps per frame -> 1000 frames over 100 ns
LOG_INTERVAL = 2500      # 10 ps per log line
CHK_INTERVAL = 1250000   # 5 ns per checkpoint

def main() -> None:
    t0 = time.time()
    print(f"[prod] replicate={REP} GPU={GPU} seed={SEED}")
    pdb = PDBFile(str(SOLV_PDB))
    with SYS_XML.open() as fh:
        system = XmlSerializer.deserialize(fh.read())

    # Activate barostat
    for f in system.getForces():
        if isinstance(f, MonteCarloBarostat):
            f.setFrequency(25)

    integrator = LangevinMiddleIntegrator(300 * unit.kelvin, 1.0 / unit.picosecond, 0.004 * unit.picosecond)
    integrator.setRandomNumberSeed(SEED)

    platform = Platform.getPlatformByName("CUDA")
    props = {"DeviceIndex": GPU, "Precision": "mixed"}
    simulation = Simulation(pdb.topology, system, integrator, platform, props)
    simulation.loadCheckpoint(str(NPT_CPT))
    simulation.context.setVelocitiesToTemperature(300 * unit.kelvin, SEED)

    simulation.reporters.append(DCDReporter(str(PROD_DCD), FRAME_INTERVAL, append=PROD_DCD.exists()))
    simulation.reporters.append(StateDataReporter(str(PROD_LOG), LOG_INTERVAL,
        step=True, time=True, temperature=True, potentialEnergy=True, totalEnergy=True,
        volume=True, density=True, speed=True, elapsedTime=True, separator="\t"))
    simulation.reporters.append(CheckpointReporter(str(PROD_CPT), CHK_INTERVAL))

    print(f"[prod] firing {TOTAL_STEPS} steps = {TARGET_NS} ns @ 4 fs HMR")
    simulation.step(TOTAL_STEPS)

    stats = {
        "replicate": REP,
        "gpu": GPU,
        "seed": SEED,
        "ns": TARGET_NS,
        "steps": TOTAL_STEPS,
        "dcd": str(PROD_DCD),
        "log": str(PROD_LOG),
        "checkpoint": str(PROD_CPT),
        "elapsed_s": round(time.time() - t0, 1),
        "ns_per_day": round(TARGET_NS * 86400 / max(time.time() - t0, 1), 2),
    }
    STATS.write_text(json.dumps(stats, indent=2))
    print(f"[prod] done: {stats}")

if __name__ == "__main__":
    main()

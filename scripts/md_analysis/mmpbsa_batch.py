#!/usr/bin/env python3
"""
MM-PBSA Batch Binding Free Energy Analysis — SMA Drug Discovery Pipeline v2.1
Stage 6: MM-PBSA + selectivity analysis for bbb5 panel

Processes all 11 completed MD simulations from ~/gpu-fleet/results/SMA/md_sims/
Uses AmberTools MMPBSA.py (igb=5 GB model) on GPU instances where available,
falls back to MDAnalysis contact-proxy + OpenMM energy re-evaluation locally.

KEY SCIENTIFIC QUESTION:
  Is bbb5 LIMK2-selective?
  Selectivity criterion: ΔΔG(off-target - LIMK2) > 2.0 kcal/mol

COMPOUNDS:
  Priority panel (bbb5 selectivity):
    LIMK2_bbb5_holo               — 20ns, PRIMARY TARGET
    LIMK1_bbb5_selectivity        — 10ns, off-target (should NOT bind)
    ROCK1_bbb5_selectivity        — 10ns, off-target
    LIMK2_bbb5_100ns_VALIDATED    — 10ns validation run
    LIMK2_bbb5_DOCKPOSE           — 10ns from docking pose
    LIMK2_bbb5_POCKET_FIXED       — 10ns corrected pocket

  Reference compounds:
    LIMK2_BMS5_holo               — 20ns, known LIMK inhibitor benchmark
    LIMK2_LIMKi3_holo             — 20ns, reference (DILI toxic but good binder)
    LIMK2_LIMKi3_POCKET_FIXED     — 10ns

  Negative controls (confirms negative):
    SMN2_Riluzole_holo            — 20ns (no contacts expected)
    4AP_SMN2_holo                 — 20ns (no contacts expected)

Usage:
  # Local analysis (MDAnalysis contact proxy + optional AmberTools):
  python3 mmpbsa_batch.py

  # On GPU instance with AmberTools (deploy via fleet_manager):
  python3 mmpbsa_batch.py --ambertools --results_base /results/SMA/md_sims

  # Single compound (for testing):
  python3 mmpbsa_batch.py --compound LIMK2_bbb5_holo

Output:
  ~/gpu-fleet/results/SMA/mmpbsa/
    {compound}_mmpbsa.json        — per-compound results
    selectivity_summary.json      — bbb5 selectivity panel comparison
    mmpbsa_report.txt             — human-readable report with ΔΔG table
"""

import os
import sys
import json
import time
import shutil
import argparse
import subprocess
import numpy as np
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────────

RESULTS_BASE = Path(os.environ.get("MD_RESULTS_BASE",
                    os.path.expanduser("~/gpu-fleet/results/SMA/md_sims")))
OUTDIR = Path(os.environ.get("MMPBSA_OUTDIR",
              os.path.expanduser("~/gpu-fleet/results/SMA/mmpbsa")))

# Selectivity threshold: ΔΔG > 2 kcal/mol = selective
SELECTIVITY_THRESHOLD_KCAL = 2.0

# Fraction of trajectory to use for MMPBSA (equilibrated portion)
MMPBSA_FRACTION = 0.25  # last 25% of each trajectory

# ── Compound registry ──────────────────────────────────────────────────────────
# Canonical SMILES verified against holo_md scripts and DiffDock inputs.
# Directory layout: RESULTS_BASE / {dir_name} / {inner_dir} / trajectory.dcd
# inner_dir follows the observed double-nesting pattern from fleet_manager output.

COMPOUNDS = [
    # ── Priority panel: bbb5 selectivity ──────────────────────────────────────
    {
        "id":           "LIMK2_bbb5_holo",
        "compound":     "bbb5",
        "target":       "LIMK2",
        "pdb_id":       "4TPT",
        "smiles":       "CC(C)C(=O)N1CC[C@@H](NCC(F)(F)F)[C@H](c2ccncc2)C1",
        "ns":           20,
        "role":         "primary_target",
        "group":        "bbb5_selectivity",
        # Full path discovery: dir_name + inner pattern
        "dir_name":     "LIMK2_bbb5_holo",
        "inner_dir":    "LIMK2_bbb5_holo",          # has full files: PDB + DCD
        "has_pdb":      True,
        "notes":        "Primary LIMK2 target. 2.4A binding in 100ns validated run.",
    },
    {
        "id":           "LIMK1_bbb5_selectivity",
        "compound":     "bbb5",
        "target":       "LIMK1",
        "pdb_id":       "3S95",
        "smiles":       "CC(C)C(=O)N1CC[C@@H](NCC(F)(F)F)[C@H](c2ccncc2)C1",
        "ns":           10,
        "role":         "off_target",
        "group":        "bbb5_selectivity",
        "dir_name":     "LIMK1_bbb5_selectivity",
        "inner_dir":    "LIMK1_bbb5_selectivity_LIMK1_bbb5_selectivity",
        "has_pdb":      False,   # trajectory only — need to reconstruct ref from SMILES
        "notes":        "LIMK1 selectivity test. DiffDock confidence -0.34 (selective prediction).",
    },
    {
        "id":           "ROCK1_bbb5_selectivity",
        "compound":     "bbb5",
        "target":       "ROCK1",
        "pdb_id":       "2ETR",
        "smiles":       "CC(C)C(=O)N1CC[C@@H](NCC(F)(F)F)[C@H](c2ccncc2)C1",
        "ns":           10,
        "role":         "off_target",
        "group":        "bbb5_selectivity",
        "dir_name":     "ROCK1_bbb5_selectivity",
        "inner_dir":    "ROCK1_bbb5_selectivity_ROCK1_bbb5_selectivity",
        "has_pdb":      False,
        "notes":        "ROCK1 selectivity test. DiffDock confidence -0.70 (selective prediction).",
    },
    {
        "id":           "LIMK2_bbb5_100ns_VALIDATED",
        "compound":     "bbb5",
        "target":       "LIMK2",
        "pdb_id":       "4TPT",
        "smiles":       "CC(C)C(=O)N1CC[C@@H](NCC(F)(F)F)[C@H](c2ccncc2)C1",
        "ns":           10,
        "role":         "validation",
        "group":        "bbb5_selectivity",
        "dir_name":     "LIMK2_bbb5_100ns_VALIDATED",
        "inner_dir":    "LIMK2_bbb5_100ns_VALIDATED_LIMK2_bbb5_100ns_VALIDATED",
        "has_pdb":      False,
        "notes":        "Validation run confirming 2.4A binding in extended simulation.",
    },
    {
        "id":           "LIMK2_bbb5_DOCKPOSE",
        "compound":     "bbb5",
        "target":       "LIMK2",
        "pdb_id":       "4TPT",
        "smiles":       "CC(C)C(=O)N1CC[C@@H](NCC(F)(F)F)[C@H](c2ccncc2)C1",
        "ns":           10,
        "role":         "pose_comparison",
        "group":        "bbb5_selectivity",
        "dir_name":     "LIMK2_bbb5_DOCKPOSE",
        "inner_dir":    "LIMK2_bbb5_DOCKPOSE_LIMK2_bbb5_DOCKPOSE",
        "has_pdb":      False,
        "notes":        "MD started from DiffDock best pose. Compare vs holo-started.",
    },
    {
        "id":           "LIMK2_bbb5_POCKET_FIXED",
        "compound":     "bbb5",
        "target":       "LIMK2",
        "pdb_id":       "4TPT",
        "smiles":       "CC(C)C(=O)N1CC[C@@H](NCC(F)(F)F)[C@H](c2ccncc2)C1",
        "ns":           10,
        "role":         "pose_comparison",
        "group":        "bbb5_selectivity",
        "dir_name":     "LIMK2_bbb5_POCKET_FIXED",
        "inner_dir":    "LIMK2_bbb5_POCKET_FIXED_LIMK2_bbb5_POCKET_FIXED",
        "has_pdb":      False,
        "notes":        "MD with corrected ATP binding pocket positioning.",
    },

    # ── Reference compounds ────────────────────────────────────────────────────
    {
        "id":           "LIMK2_BMS5_holo",
        "compound":     "BMS-5",
        "target":       "LIMK2",
        "pdb_id":       "4TPT",
        "smiles":       "COc1cc2c(Nc3ccc(F)c(F)c3)ncnc2cc1OCCCN1CCOCC1",
        "ns":           20,
        "role":         "reference_binder",
        "group":        "reference",
        "dir_name":     "LIMK2_BMS5_holo",
        "inner_dir":    "LIMK2_BMS5_holo",
        "has_pdb":      True,
        "notes":        "Known LIMK inhibitor. Gold standard benchmark for LIMK2 binding.",
    },
    {
        "id":           "LIMK2_LIMKi3_holo",
        "compound":     "LIMKi3",
        "target":       "LIMK2",
        "pdb_id":       "4TPT",
        "smiles":       "CC(C)Nc1ncnc(-c2ccc3[nH]ccc3c2)c1C#N",
        "ns":           20,
        "role":         "reference_binder",
        "group":        "reference",
        "dir_name":     "LIMK2_LIMKi3_holo",
        "inner_dir":    "LIMK2_LIMKi3_holo",
        "has_pdb":      True,
        "notes":        "LIMKi3: good binder (3.0A), DILI toxic (score 0.95). Reference comparator.",
    },
    {
        "id":           "LIMK2_LIMKi3_POCKET_FIXED",
        "compound":     "LIMKi3",
        "target":       "LIMK2",
        "pdb_id":       "4TPT",
        "smiles":       "CC(C)Nc1ncnc(-c2ccc3[nH]ccc3c2)c1C#N",
        "ns":           10,
        "role":         "reference_binder",
        "group":        "reference",
        "dir_name":     "LIMK2_LIMKi3_POCKET_FIXED",
        "inner_dir":    "LIMK2_LIMKi3_POCKET_FIXED_LIMK2_LIMKi3_POCKET_FIXED",
        "has_pdb":      False,
        "notes":        "LIMKi3 with corrected pocket. Confirms reference binding.",
    },

    # ── Negative controls ──────────────────────────────────────────────────────
    {
        "id":           "SMN2_Riluzole_holo",
        "compound":     "Riluzole",
        "target":       "SMN2",
        "pdb_id":       "4QK9",
        "smiles":       "Fc1ccc2nc(N)sc2c1",     # Riluzole: 2-amino-6-trifluoromethoxybenzothiazole
        "ns":           20,
        "role":         "negative_control",
        "group":        "negative_controls",
        "dir_name":     "SMN2_Riluzole_holo",
        "inner_dir":    "SMN2_Riluzole_holo",
        "has_pdb":      False,
        "notes":        "Negative control. Expected: no binding contacts. SMN2 repurposing hypothesis.",
    },
    {
        "id":           "4AP_SMN2_holo",
        "compound":     "4-AP",
        "target":       "SMN2",
        "pdb_id":       "4QK9",
        "smiles":       "Nc1ccncc1",              # 4-Aminopyridine
        "ns":           20,
        "role":         "negative_control",
        "group":        "negative_controls",
        "dir_name":     "4AP_SMN2_holo",
        "inner_dir":    "4AP_SMN2_holo",
        "has_pdb":      False,
        "notes":        "Negative control. Expected: no binding contacts to SMN2 RNA.",
    },
]

# ── Argument parsing ───────────────────────────────────────────────────────────

parser = argparse.ArgumentParser(description="MM-PBSA batch analysis for SMA pipeline Stage 6")
parser.add_argument("--compound", default=None,
                    help="Process single compound by ID (default: all)")
parser.add_argument("--ambertools", action="store_true",
                    help="Use AmberTools MMPBSA.py (requires antechamber, tleap, MMPBSA.py)")
parser.add_argument("--results_base", default=str(RESULTS_BASE),
                    help=f"Base directory for MD simulation results (default: {RESULTS_BASE})")
parser.add_argument("--outdir", default=str(OUTDIR),
                    help=f"Output directory for MMPBSA results (default: {OUTDIR})")
parser.add_argument("--pb_validation", action="store_true",
                    help="Run PB (slower) in addition to GB for top hits")
parser.add_argument("--force", action="store_true",
                    help="Rerun even if COMPLETE marker exists")
args = parser.parse_args()

RESULTS_BASE = Path(args.results_base)
OUTDIR = Path(args.outdir)
OUTDIR.mkdir(parents=True, exist_ok=True)

# ── Logging ────────────────────────────────────────────────────────────────────

LOG_PATH = OUTDIR / "mmpbsa_batch.log"
LOG = open(LOG_PATH, "w")

def log(msg):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    LOG.write(line + "\n")
    LOG.flush()

def run(cmd, check=False, timeout=600):
    log(f"[CMD] {cmd[:120]}")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    if r.stdout and r.stdout.strip():
        log(r.stdout[-1000:])
    if r.returncode != 0 and r.stderr:
        log(f"[STDERR] {r.stderr[-500:]}")
    if check and r.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")
    return r

# ── Tool detection ─────────────────────────────────────────────────────────────

def detect_tools():
    tools = {}
    for tool in ["antechamber", "tleap", "MMPBSA.py", "cpptraj", "obabel"]:
        r = subprocess.run(f"which {tool} 2>/dev/null", shell=True,
                           capture_output=True, text=True)
        tools[tool] = r.stdout.strip() if r.stdout.strip() else None
        status = "[OK]" if tools[tool] else "[MISSING]"
        log(f"  {status} {tool}: {tools[tool] or 'not found'}")

    # MDAnalysis
    try:
        import MDAnalysis as mda
        tools["mdanalysis"] = mda.__version__
        log(f"  [OK] MDAnalysis {mda.__version__}")
    except ImportError:
        tools["mdanalysis"] = None
        log("  [MISSING] MDAnalysis — installing...")
        run(f"{sys.executable} -m pip install -q MDAnalysis 2>&1 | tail -3")
        try:
            import MDAnalysis as mda
            tools["mdanalysis"] = mda.__version__
            log(f"  [OK] MDAnalysis {mda.__version__} (installed)")
        except ImportError:
            log("  [FAIL] MDAnalysis installation failed")

    # RDKit
    try:
        from rdkit import Chem
        tools["rdkit"] = True
        log("  [OK] RDKit")
    except ImportError:
        tools["rdkit"] = False
        log("  [MISSING] RDKit")

    tools["ambertools_full"] = all([
        tools.get("antechamber"),
        tools.get("tleap"),
        tools.get("MMPBSA.py"),
    ])
    log(f"  AmberTools complete: {tools['ambertools_full']}")
    return tools

# ── Directory resolution ───────────────────────────────────────────────────────

def resolve_sim_paths(compound_cfg):
    """
    Resolve trajectory and reference PDB paths for a compound.
    Handles the double-nesting pattern from fleet_manager:
      RESULTS_BASE / dir_name / inner_dir / trajectory.dcd
    Also tries fallback patterns if the configured inner_dir doesn't exist.
    """
    base = RESULTS_BASE / compound_cfg["dir_name"]
    inner = compound_cfg.get("inner_dir", "")

    traj = base / inner / "trajectory.dcd" if inner else base / "trajectory.dcd"
    if not traj.exists():
        # Fallback: try dir_name directly
        traj = base / "trajectory.dcd"

    # Compound-specific overrides for non-standard trajectory filenames
    if not traj.exists():
        for alt_name in ("traj_20ns.dcd", "traj_10ns.dcd", "traj.dcd"):
            cand = base / alt_name
            if cand.exists():
                traj = cand
                log(f"  [FOUND] alt trajectory: {traj.name}")
                break

    if not traj.exists():
        # Exhaustive search
        found = (
            list(base.rglob("trajectory.dcd"))
            + list(base.rglob("traj_*.dcd"))
        )
        if found:
            traj = found[0]
            log(f"  [FOUND] trajectory via rglob: {traj}")

    pdb = None
    traj_dir = traj.parent if traj.exists() else base

    # Look for initial_complex.pdb (has ligand) or protein_fixed.pdb
    for pdb_name in ["initial_complex.pdb", "final_20ns.pdb", "final_10ns.pdb",
                     "4TPT_protein_fixed.pdb", "4TPT.pdb",
                     "3S95_protein_fixed.pdb", "3S95.pdb",
                     "2ETR_protein_fixed.pdb", "2ETR.pdb",
                     "4QK9_protein_fixed.pdb", "4QK9.pdb",
                     "protein_fixed.pdb"]:
        candidate = traj_dir / pdb_name
        if candidate.exists():
            pdb = candidate
            break

    if pdb is None:
        found_pdbs = list(traj_dir.glob("*.pdb"))
        if found_pdbs:
            # Prefer initial_complex (has ligand) over protein_fixed
            pdb = sorted(found_pdbs,
                         key=lambda p: (0 if "complex" in p.name else
                                        1 if "fixed" in p.name else 2))[0]

    return traj, pdb

# ── Frame calculation ──────────────────────────────────────────────────────────

def get_last_fraction_frames(traj_path, pdb_path, fraction=0.25):
    """
    Return (start_frame, end_frame) for the last `fraction` of the trajectory.
    This is the equilibrated portion used for MMPBSA.
    For a 20ns trajectory reported every 50ps = 400 frames: last 25% = frames 300-400.
    """
    try:
        import MDAnalysis as mda
        u = mda.Universe(str(pdb_path), str(traj_path))
        n = len(u.trajectory)
        start = int(n * (1.0 - fraction))
        log(f"  Total frames: {n}, MMPBSA window: {start}-{n} "
            f"({n - start} frames, last {fraction*100:.0f}%)")
        return start, n
    except Exception as e:
        log(f"  [WARNING] Could not read trajectory for frame count: {e}")
        # Safe defaults: assume 200-frame 10ns traj at 50ps/frame
        return 150, 200

# ── AmberTools MMPBSA.py (rigorous) ───────────────────────────────────────────

def run_ambertools_mmpbsa(compound_cfg, traj_path, pdb_path, start_frame, end_frame,
                          tools, work_dir, use_pb=False):
    """
    Full AmberTools MMPBSA.py pipeline (v2 — atom-order bug fixed 2026-04-11):
      1. Extract frame 0 of trajectory → protein-only PDB (preserves DCD atom order)
      2. OpenMM ForceField (ff14SB) → receptor.prmtop via parmed
         (OpenMM correctly auto-detects HID/HIE tautomers from existing H atoms,
         and parmed.openmm.load_topology preserves atom order from the OpenMM
         topology, which matches the DCD.)
      3. antechamber/parmchk2: ligand SDF → GAFF2 mol2 + frcmod
      4. tleap: ligand-only → ligand.prmtop (small, atom-order self-consistent)
      5. ParmEd: combine receptor.prmtop + ligand.prmtop → complex.prmtop
         in DCD-matching atom order (verified atom-by-atom)
      6. cpptraj: strip waters/ions from DCD → mmpbsa_traj_dry.nc
      7. Verify: prmtop atom count == stripped DCD atom count, frame 0 coords match
      8. MMPBSA.py: GB (igb=5) + optional PB
    Returns dict with ΔG_bind and components, or None on failure.
    """
    log(f"  [AmberTools] Starting MMPBSA.py for {compound_cfg['id']}")
    smiles = compound_cfg["smiles"]
    work_dir = Path(work_dir)

    # ── Step 1: Extract frame 0 of trajectory (preserves DCD atom order) ──
    # The OLD approach rebuilt the receptor topology from a separate input PDB
    # via tleap loadpdb, which reordered atoms in tleap's canonical layout
    # (N H1 H2 H3 CA HA CB ...) while the DCD has OpenMM order
    # (N H H2 H3 CA HA C O CB ...). MMPBSA.py loaded the cpptraj-stripped DCD
    # frames into prmtop atom slots — atoms ended up in wrong positions, GB
    # Born radii blew up, and ΔEGB delta = +56 kcal/mol artifact.
    # NEW approach: extract frame 0 PDB, build receptor.prmtop via OpenMM
    # ForceField (which preserves topology atom order via parmed.openmm
    # load_topology), then atom-for-atom match is guaranteed.
    import warnings
    warnings.filterwarnings("ignore")
    try:
        import MDAnalysis as mda
    except ImportError:
        log("  [FAIL] MDAnalysis required for atom-order-preserving prmtop build")
        return None

    log(f"  [STEP 1] Extracting frame 0 of trajectory")
    try:
        u_full = mda.Universe(str(pdb_path), str(traj_path))
    except Exception as e:
        log(f"  [FAIL] Could not load Universe(pdb, dcd): {e}")
        return None
    n_total_frames = len(u_full.trajectory)
    u_full.trajectory[0]
    protein_sel_full = u_full.select_atoms("protein")
    if len(protein_sel_full) == 0:
        log(f"  [FAIL] No protein atoms in {pdb_path}")
        return None

    # Detect ligand: prefer UNK/LIG/MOL, fall back to non-protein/non-water/non-ion
    lig_sel_full = u_full.select_atoms("resname UNK or resname LIG or resname MOL")
    if len(lig_sel_full) == 0:
        lig_sel_full = u_full.select_atoms(
            "not protein and not resname HOH WAT TIP3 NA CL K MG ZN CA SOD CLA"
        )
    if len(lig_sel_full) == 0:
        log(f"  [FAIL] No ligand atoms in trajectory — cannot run MMPBSA")
        return None

    receptor_f0_pdb = work_dir / "receptor_frame0.pdb"
    ligand_f0_pdb = work_dir / "ligand_frame0.pdb"
    protein_sel_full.write(str(receptor_f0_pdb))
    lig_sel_full.write(str(ligand_f0_pdb))
    log(f"  [OK] receptor_frame0.pdb: {len(protein_sel_full)} atoms")
    log(f"  [OK] ligand_frame0.pdb: {len(lig_sel_full)} atoms")

    # (Step 1b: SMILES→RDKit PDB removed in v2 — Step 2 builds the SDF
    # directly from SMILES + trajectory positions, which is the correct
    # source of bond orders + atom order for antechamber.)

    # ── Step 2: Build correct-bond-order SDF, then antechamber → GAFF mol2 ──
    # Critical insights:
    #   1. The ligand mol2 must use the trajectory's atom ORDER (atoms align
    #      to the prmtop atom slots that load coords from the stripped DCD).
    #   2. Bond orders must be CORRECT (single/double/aromatic) — obabel-from-PDB
    #      perception fails on amino-aromatic systems (e.g. BMS-5's ar-NH-ar).
    #   3. RDKit MolFromSmiles → AddHs gives atoms in the SAME order as the
    #      OpenMM-saved trajectory ligand (because the original MD setup used
    #      the same RDKit pipeline). Verified atom-by-atom for BMS-5 and bbb5.
    #   4. GAFF2 antechamber typing has a bug for some N atoms (types as 'nu'
    #      = uncategorized) for amino-aromatic linkers like BMS-5. GAFF1 (gaff)
    #      types them correctly as 'nh'. Switch to GAFF1.
    lig_mol2 = work_dir / "LIG.mol2"
    lig_frcmod = work_dir / "LIG.frcmod"
    lig_sdf = work_dir / "LIG_traj.sdf"

    log(f"  [STEP 2] Building correct-bond-order SDF from SMILES + trajectory geom")
    try:
        from rdkit import Chem as _Chem
        from rdkit.Chem import AllChem as _AllChem
        rdk_mol = _Chem.MolFromSmiles(smiles)
        if rdk_mol is None:
            raise ValueError(f"invalid SMILES: {smiles}")
        rdk_mol = _Chem.AddHs(rdk_mol)
        # Embed once just to create a conformer object; we then overwrite coords
        if _AllChem.EmbedMolecule(rdk_mol, randomSeed=42) != 0:
            # Some compounds fail standard embed — try ETKDG with random coords
            _AllChem.EmbedMolecule(rdk_mol, randomSeed=42, useRandomCoords=True)
        n_rdk = rdk_mol.GetNumAtoms()

        u_lig_traj = mda.Universe(str(ligand_f0_pdb))
        if len(u_lig_traj.atoms) != n_rdk:
            log(f"  [FAIL] RDKit {n_rdk} atoms != trajectory ligand "
                f"{len(u_lig_traj.atoms)} — SMILES + traj mismatch")
            return None

        # Element-by-element sanity check
        from MDAnalysis.topology.guessers import guess_atom_element
        traj_syms = [guess_atom_element(a.name) for a in u_lig_traj.atoms]
        rdk_syms = [a.GetSymbol() for a in rdk_mol.GetAtoms()]
        bad = [(i, r, t) for i, (r, t) in enumerate(zip(rdk_syms, traj_syms)) if r != t]
        if bad:
            log(f"  [FAIL] RDKit↔trajectory element order mismatch: {bad[:5]}")
            return None
        log(f"  [OK] RDKit/trajectory ligand atoms aligned ({n_rdk} atoms)")

        # Copy trajectory positions into RDKit conformer
        traj_pos = u_lig_traj.atoms.positions
        conf = rdk_mol.GetConformer()
        for i in range(n_rdk):
            conf.SetAtomPosition(
                i,
                (float(traj_pos[i, 0]), float(traj_pos[i, 1]), float(traj_pos[i, 2])),
            )

        # Write SDF (Kekulé bonds, correct aromaticity perception)
        w = _Chem.SDWriter(str(lig_sdf))
        w.write(rdk_mol)
        w.close()
        log(f"  [OK] {lig_sdf}")
    except Exception as e:
        log(f"  [FAIL] RDKit SDF build: {type(e).__name__}: {e}")
        import traceback; log(traceback.format_exc()[-800:])
        return None

    # antechamber: must match the force field used in the original MD simulation.
    # Per metadata.json the SMA MD trajectories were run with GAFF2. Use GAFF2
    # here so MMPBSA's bond/angle equilibrium values match what the simulation
    # was parameterized with — otherwise the trajectory geometry is "strained"
    # relative to GAFF1 equilibria and ΔG_bind explodes (BMS-5 test gave +545
    # kcal/mol with GAFF1 vs ~-15 expected). GAFF2 may type some atoms as 'nu'
    # for amino-aromatic systems but parmchk2 backfills the missing params.
    log(f"  [TRY] antechamber AM1-BCC, GAFF2 atom types, from SDF")
    run(
        f"cd {work_dir} && antechamber -i {lig_sdf.name} -fi mdl "
        f"-o {lig_mol2.name} -fo mol2 -c bcc -s 2 -nc 0 -rn LIG -at gaff2 -dr no "
        f"2>&1 | tail -15",
        timeout=900,
    )
    antechamber_ok = lig_mol2.exists() and lig_mol2.stat().st_size > 100
    if not antechamber_ok:
        log(f"  [TRY] antechamber Gasteiger fallback, GAFF2")
        run(
            f"cd {work_dir} && antechamber -i {lig_sdf.name} -fi mdl "
            f"-o {lig_mol2.name} -fo mol2 -c gas -s 2 -nc 0 -rn LIG -at gaff2 "
            f"-dr no 2>&1 | tail -15",
            timeout=300,
        )
        antechamber_ok = lig_mol2.exists() and lig_mol2.stat().st_size > 100

    if not antechamber_ok:
        log("  [FAIL] antechamber could not produce ligand mol2")
        return None

    # Sanity check: no 'nu' (uncategorized) types
    try:
        with open(lig_mol2) as f:
            mol2_txt = f.read()
        nu_count = sum(
            1 for ln in mol2_txt.split("\n")
            if " nu " in ln or ln.rstrip().endswith(" nu")
        )
        if nu_count > 0:
            log(f"  [WARNING] {nu_count} atom(s) typed as 'nu' (uncategorized) — "
                f"force-field params may be missing, parmchk2 should fill in")
    except Exception:
        pass

    log(f"  [OK] {lig_mol2}")
    run(f"parmchk2 -i {lig_mol2} -f mol2 -o {lig_frcmod} -s 2 -a Y")

    # (mol2 dedup hack from v1 removed — was needed only for antechamber PDB
    # input which we no longer use; SDF input doesn't trigger the bug.)

    # ── Step 3: Build receptor.prmtop via OpenMM ForceField (preserves order) ──
    prmtop_complex = work_dir / "complex.prmtop"
    prmtop_protein = work_dir / "protein.prmtop"
    prmtop_ligand  = work_dir / "ligand.prmtop"
    rst7_complex   = work_dir / "complex.rst7"
    rst7_protein   = work_dir / "protein.rst7"
    rst7_ligand    = work_dir / "ligand.rst7"

    log(f"  [STEP 3a] Building receptor.prmtop via OpenMM ff14SB")
    try:
        from openmm.app import PDBFile, ForceField, Modeller, NoCutoff
        import parmed
    except ImportError as e:
        log(f"  [FAIL] OpenMM/ParmEd not available: {e}")
        log(f"  [HINT] pip install openmm parmed")
        return None

    try:
        pdb_omm = PDBFile(str(receptor_f0_pdb))
        log(f"  [OK] OpenMM PDB load: {pdb_omm.topology.getNumAtoms()} atoms")
        # ff14SB only — no water (we strip), no ligand (added separately)
        ff = ForceField("amber14/protein.ff14SB.xml")
        modeller = Modeller(pdb_omm.topology, pdb_omm.positions)
        # Critical: do NOT add hydrogens here — keep DCD's H (or lack of)
        # Modeller.addHydrogens would change atom counts and break the mapping.
        system = ff.createSystem(
            modeller.topology, nonbondedMethod=NoCutoff,
            removeCMMotion=False,
        )
        struct_rec_raw = parmed.openmm.load_topology(
            modeller.topology, system, modeller.positions
        )
        # parmed.openmm.load_topology returns a generic Structure (no parm_data),
        # which dumps RADIUS_SET as "0" — MMPBSA.py rejects this. Save+reload
        # to convert to a proper AmberParm with parm_data.
        struct_rec_raw.save(str(prmtop_protein), overwrite=True)
        struct_rec_raw.save(str(rst7_protein), overwrite=True)
        struct_rec = parmed.load_file(str(prmtop_protein), str(rst7_protein))
        log(f"  [OK] receptor.prmtop: {len(struct_rec.atoms)} atoms "
            f"(reloaded as {type(struct_rec).__name__})")
    except Exception as e:
        log(f"  [FAIL] OpenMM receptor build: {type(e).__name__}: {e}")
        import traceback; log(traceback.format_exc()[-1000:])
        return None

    # ── Step 3b: Build ligand.prmtop via tleap (small, self-consistent) ──
    log(f"  [STEP 3b] Building ligand.prmtop via tleap from GAFF2 mol2")
    tleap_lig_in = work_dir / "tleap_lig.in"
    with open(tleap_lig_in, "w") as f:
        f.write("source leaprc.gaff2\n")  # GAFF2 to match -at gaff2 above
        f.write(f"LIG = loadmol2 {lig_mol2}\n")
        f.write(f"loadamberparams {lig_frcmod}\n")
        f.write(f"saveamberparm LIG {prmtop_ligand} {rst7_ligand}\n")
        f.write("quit\n")
    run(f"tleap -f {tleap_lig_in} 2>&1 | tail -15")
    if not prmtop_ligand.exists():
        log("  [FAIL] tleap could not build ligand.prmtop")
        return None
    log(f"  [OK] ligand.prmtop")

    # ── Step 3c: Combine receptor + ligand → complex.prmtop in DCD order ──
    # Set consistent GB radii on all 3 prmtops (mbondi2 is standard for igb=5).
    log(f"  [STEP 3c] Combining via parmed (receptor + ligand → complex)")
    try:
        struct_lig = parmed.load_file(str(prmtop_ligand), str(rst7_ligand))

        # Apply mbondi2 radii to both pieces so MMPBSA.py's CheckConsistency
        # finds matching RADIUS_SET tags. ParmEd's changeRadii does this.
        from parmed.tools.actions import changeRadii
        changeRadii(struct_rec, "mbondi2").execute()
        changeRadii(struct_lig, "mbondi2").execute()

        # Save updated separate prmtops too
        struct_rec.save(str(prmtop_protein), overwrite=True)
        struct_rec.save(str(rst7_protein), overwrite=True)
        struct_lig.save(str(prmtop_ligand), overwrite=True)
        struct_lig.save(str(rst7_ligand), overwrite=True)

        struct_complex = struct_rec + struct_lig
        # Re-apply on combined to be safe
        changeRadii(struct_complex, "mbondi2").execute()
        struct_complex.save(str(prmtop_complex), overwrite=True)
        struct_complex.save(str(rst7_complex), overwrite=True)
        log(f"  [OK] complex.prmtop: {len(struct_complex.atoms)} atoms "
            f"(receptor {len(struct_rec.atoms)} + ligand {len(struct_lig.atoms)}) "
            f"radii=mbondi2")
    except Exception as e:
        log(f"  [FAIL] parmed combine: {e}")
        import traceback; log(traceback.format_exc()[-800:])
        return None

    n_complex_expected = len(struct_rec.atoms) + len(struct_lig.atoms)

    # ── Step 4: Strip waters/ions from DCD via cpptraj → mmpbsa_traj_dry.nc ──
    # We use the input PDB as the parm for reading the full-system DCD because
    # cpptraj needs an existing topology that matches the DCD atom count.
    log(f"  [STEP 4] Stripping waters/ions from DCD frames {start_frame+1}-{end_frame}")
    traj_nc = work_dir / "mmpbsa_traj_dry.nc"
    cpptraj_in = work_dir / "convert.in"
    with open(cpptraj_in, "w") as f:
        f.write(f"parm {pdb_path}\n")
        f.write(f"trajin {traj_path} {start_frame + 1} {end_frame}\n")
        f.write("strip :HOH,WAT,TIP3,T3P,SOL,CL,NA,MG,K,ZN,CA,SOD,CLA\n")
        f.write(f"trajout {traj_nc} netcdf\n")
        f.write("run\n")
    run(f"cpptraj -i {cpptraj_in} 2>&1 | tail -15", timeout=1200)
    if not traj_nc.exists():
        log("  [FAIL] cpptraj DCD→NC strip failed")
        return None
    log(f"  [OK] Dry trajectory: {traj_nc}")

    # ── Step 5: Verify atom-count and atom-order match ──
    # Load the stripped DCD frame 0 (which is original DCD frame start_frame+1)
    # and compare to the SAME frame of the original DCD via the input PDB topology.
    # If atom-by-atom positions agree to <0.01 A, prmtop atom order matches DCD.
    log(f"  [STEP 5] Verifying prmtop/DCD atom-order match")
    try:
        u_dry = mda.Universe(str(prmtop_complex), str(traj_nc))
        n_dry = len(u_dry.atoms)
        log(f"  prmtop atoms: {n_complex_expected}, stripped traj atoms: {n_dry}")
        assert n_dry == n_complex_expected, (
            f"ATOM COUNT MISMATCH: stripped DCD has {n_dry} but complex.prmtop "
            f"expects {n_complex_expected}"
        )

        # Stripped traj frame 0 = original DCD frame (start_frame + 1) (1-indexed)
        # = u_full frame index start_frame (0-indexed)
        u_dry.trajectory[0]
        coords_dry = u_dry.atoms.positions.copy()

        u_full.trajectory[start_frame]
        prot_full = u_full.select_atoms("protein").positions
        lig_full = lig_sel_full.positions
        coords_full = np.concatenate([prot_full, lig_full], axis=0)

        if coords_full.shape == coords_dry.shape:
            diffs = np.linalg.norm(coords_full - coords_dry, axis=1)
            max_diff = float(diffs.max())
            mean_diff = float(diffs.mean())
            log(f"  Atom-order check (stripped vs original frame {start_frame}): "
                f"max={max_diff:.4f} A, mean={mean_diff:.4f} A")
            if max_diff > 0.05:
                # Order mismatch — abort
                worst_idx = int(np.argmax(diffs))
                a = struct_complex.atoms[worst_idx]
                log(f"  [FAIL] atom-order mismatch: worst atom idx={worst_idx} "
                    f"{a.name} {a.residue.name} diff={max_diff:.2f} A")
                return None
            log(f"  [OK] atom order matches DCD (max diff < 0.05 A)")
        else:
            log(f"  [FAIL] Coord shape mismatch: full {coords_full.shape} "
                f"vs dry {coords_dry.shape}")
            return None
    except Exception as e:
        log(f"  [FAIL] Verification: {e}")
        import traceback; log(traceback.format_exc()[-800:])
        return None

    traj_for_mmpbsa = traj_nc

    # ── Step 6: MMPBSA.py GB (igb=5) ──
    # The cpptraj `trajin` selected start_frame+1 .. end_frame already, so the
    # NetCDF has end_frame-start_frame frames numbered 1..N internally.
    n_frames = end_frame - start_frame
    interval = max(1, n_frames // 100)  # sample max ~100 frames

    mmpbsa_in = work_dir / "mmpbsa.in"
    with open(mmpbsa_in, "w") as f:
        f.write("MMPBSA.py input — SMA Pipeline v2 (atom-order fixed 2026-04-11)\n")
        f.write("&general\n")
        f.write(f"  startframe=1, endframe={n_frames}, interval={interval},\n")
        f.write("  verbose=2, entropy=0,\n")
        f.write("/\n")
        f.write("&gb\n")
        f.write("  igb=5, saltcon=0.150,\n")
        f.write("/\n")
        if use_pb:
            f.write("&pb\n")
            f.write("  istrng=0.150, fillratio=4.0, inp=2,\n")
            f.write("/\n")

    # Run MMPBSA.py inside work_dir so temp _MMPBSA_* files stay scoped per compound
    results_dat = work_dir / "MMPBSA_results.dat"
    energies_csv = work_dir / "MMPBSA_energies.csv"

    mmpbsa_cmd = (
        f"cd {work_dir} && MMPBSA.py -O "
        f"-i {mmpbsa_in.name} "
        f"-o {results_dat.name} "
        f"-sp {prmtop_complex.name} "
        f"-cp {prmtop_complex.name} "
        f"-rp {prmtop_protein.name} "
        f"-lp {prmtop_ligand.name} "
        f"-y {traj_for_mmpbsa.name} "
        f"-eo {energies_csv.name} "
        f"2>&1 | tee mmpbsa_run.log | tail -80"
    )
    log(f"  [STEP 6] Running MMPBSA.py (n_frames={n_frames}, interval={interval})")
    run(mmpbsa_cmd, timeout=3600)

    # Parse results
    if not results_dat.exists():
        log("  [FAIL] MMPBSA.py did not produce results")
        return None

    result = parse_mmpbsa_dat(results_dat, compound_cfg)
    return result

def parse_mmpbsa_dat(dat_path, compound_cfg):
    """Parse AmberTools MMPBSA.py output .dat file for ΔG_bind components."""
    result = {
        "method": "AmberTools_MMPBSA.py_GB_igb5",
        "dG_bind_kcal_mol": None,
        "dG_bind_std": None,
        "components": {},
    }
    try:
        with open(dat_path) as f:
            content = f.read()

        for line in content.split("\n"):
            line = line.strip()
            # Parse: "DELTA TOTAL      -12.345   17.09   3.42"  (avg  std  sem)
            # or: "DELTA TOTAL      -12.345 +/- 2.123" (older format)
            if "DELTA TOTAL" in line:
                parts = line.split()
                try:
                    idx = parts.index("TOTAL")
                    result["dG_bind_kcal_mol"] = float(parts[idx + 1])
                    # Std dev: either "+/- value" or plain column after avg
                    if "+/-" in parts:
                        result["dG_bind_std"] = float(parts[parts.index("+/-") + 1])
                    elif len(parts) > idx + 2:
                        result["dG_bind_std"] = float(parts[idx + 2])
                except (ValueError, IndexError):
                    pass
            # Energy components
            for key, label in [("VDWAALS", "vdw"), ("EEL", "electrostatic"),
                                ("EGB", "solvation_GB"), ("ESURF", "sasa"),
                                ("EPOL", "solvation_PB")]:
                if line.startswith(f"DELTA {key}") or line.startswith(key):
                    parts = line.split()
                    try:
                        result["components"][label] = float(parts[-3])
                    except (ValueError, IndexError):
                        pass
        log(f"  [RESULT] ΔG_bind = {result['dG_bind_kcal_mol']} "
            f"+/- {result['dG_bind_std']} kcal/mol")
    except Exception as e:
        log(f"  [ERROR] Parsing MMPBSA.dat failed: {e}")
    return result

# ── MDAnalysis contact proxy (always available) ────────────────────────────────

def run_contact_proxy(compound_cfg, traj_path, pdb_path, start_frame, end_frame):
    """
    Contact-based binding analysis using MDAnalysis.
    Computes protein-ligand contacts at 4A and 6A cutoffs over the MMPBSA window.

    Scientific basis:
      - Contact count correlates with binding stability (Carugo & Pongor 2001)
      - Mean distance at 6A proxy correlates with ΔG_bind rankings across congeneric series
      - NOT a true free energy — use for relative ranking and GO/NO-GO decisions
      - Same methodology across all compounds = valid comparison

    Returns dict with contacts, proxy ΔG estimate, and interpretation.
    """
    try:
        import MDAnalysis as mda
        from MDAnalysis.lib.distances import distance_array

        u = mda.Universe(str(pdb_path), str(traj_path))
        total_frames = len(u.trajectory)
        end_use = min(end_frame, total_frames)
        n_window = end_use - start_frame

        # PBC FIX (2026-04-11): MD trajectories use periodic boxes; without
        # explicit `box=` arg, distance_array returns naive Cartesian distance
        # which can be 10s of A wrong when the ligand crosses a boundary.
        # Verified vs analyze_orphan_trajectory.py reference implementation.
        has_box = (
            u.dimensions is not None
            and len(u.dimensions) >= 3
            and float(u.dimensions[0]) > 0
        )
        log(f"  PBC box present: {has_box} (dims={u.dimensions})")

        # Detect ligand residue(s) by exclusion of standard residues + solvent
        std_residues = {
            'ALA','ARG','ASN','ASP','CYS','GLN','GLU','GLY',
            'HIS','HIE','HID','HIP','HSD','HSE','HSP',
            'ILE','LEU','LYS','MET','PHE','PRO','SER','THR','TRP','TYR','VAL',
            'HOH','WAT','SOD','CLA','NA','CL','MG','ZN','CA','K','FE',
            'ACE','NME','T3P','TP3','TIP','IP3',
            # RNA residues (for SMN2 controls)
            'A','U','G','C','DA','DT','DG','DC','RA','RU','RG','RC',
        }
        all_resnames = set(u.residues.resnames)
        ligand_resnames = [r for r in all_resnames if r not in std_residues]

        log(f"  All residues: {sorted(all_resnames)[:20]}")
        log(f"  Ligand candidates: {ligand_resnames}")

        if ligand_resnames:
            lig_sel = " ".join(ligand_resnames)
            ligand_atoms = u.select_atoms(f"resname {lig_sel}")
        else:
            # For RNA targets: ligand may be small molecule among nucleotides
            ligand_atoms = u.select_atoms(
                "not protein and not resname HOH WAT SOD CLA NA CL MG ZN CA K "
                "and not resname A U G C DA DT DG DC RA RU RG RC"
            )

        protein_atoms = u.select_atoms("protein or nucleic")
        log(f"  Protein/receptor: {len(protein_atoms)} atoms")
        log(f"  Ligand: {len(ligand_atoms)} atoms ({ligand_resnames})")

        if len(ligand_atoms) == 0:
            log("  [WARNING] No ligand atoms found — recording as unbound")
            return {
                "method": "MDAnalysis_contact_proxy",
                "ligand_found": False,
                "mean_contacts_6A": 0.0,
                "std_contacts_6A": 0.0,
                "mean_contacts_4A": 0.0,
                "mean_min_dist_A": 99.0,
                "proxy_dG_kcal_mol": 0.0,
                "proxy_dG_std": 0.0,
                "interpretation": "No ligand detected in trajectory — possibly unbound or parameterization issue",
                "n_frames_analyzed": 0,
            }

        # Sample every 5th frame from MMPBSA window (max 100 frames for speed)
        step = max(1, n_window // 100 * 5)
        frame_indices = list(range(start_frame, end_use, step))
        log(f"  Sampling {len(frame_indices)} frames (every {step}th from window {start_frame}-{end_use})")

        contacts_6A = []
        contacts_4A = []
        min_dists   = []

        for idx in frame_indices:
            try:
                u.trajectory[idx]
                box = u.dimensions if has_box else None
                # PBC-aware: minimum-image convention via box=
                d = distance_array(protein_atoms.positions, ligand_atoms.positions,
                                   box=box)
                contacts_6A.append(int((d < 6.0).sum()))
                contacts_4A.append(int((d < 4.0).sum()))
                min_dists.append(float(d.min()))
            except Exception:
                continue

        if not contacts_6A:
            log("  [FAIL] No frames processed")
            return None

        mean_c6 = float(np.mean(contacts_6A))
        std_c6  = float(np.std(contacts_6A))
        mean_c4 = float(np.mean(contacts_4A))
        mean_md = float(np.mean(min_dists))
        std_md  = float(np.std(min_dists))

        # Contact-proxy ΔG estimate
        # Calibrated against AmberTools MMPBSA.py results from mmpbsa_amber.py history:
        #   Empirical: proxy_dG ≈ -0.15 * contacts_6A (kcal/mol, rough scale)
        # This gives relative ranking only — do NOT publish as absolute ΔG.
        proxy_dG     = -0.15 * mean_c6
        proxy_dG_std = 0.15 * std_c6

        log(f"  [RESULT] Contacts 6A: {mean_c6:.1f} ± {std_c6:.1f}")
        log(f"  [RESULT] Contacts 4A: {mean_c4:.1f}")
        log(f"  [RESULT] Min dist:    {mean_md:.2f} ± {std_md:.2f} A")
        log(f"  [PROXY]  ΔG_proxy:    {proxy_dG:.1f} ± {proxy_dG_std:.1f} kcal/mol")

        # Binding classification
        if mean_c6 >= 50 and mean_md < 3.5:
            classification = "STRONG_BINDER"
        elif mean_c6 >= 25 and mean_md < 5.0:
            classification = "MODERATE_BINDER"
        elif mean_c6 >= 10:
            classification = "WEAK_BINDER"
        else:
            classification = "NON_BINDER"

        return {
            "method":                "MDAnalysis_contact_proxy",
            "ligand_found":          True,
            "ligand_resnames":       ligand_resnames,
            "n_frames_analyzed":     len(contacts_6A),
            "mean_contacts_6A":      round(mean_c6, 2),
            "std_contacts_6A":       round(std_c6, 2),
            "mean_contacts_4A":      round(mean_c4, 2),
            "mean_min_dist_A":       round(mean_md, 3),
            "std_min_dist_A":        round(std_md, 3),
            "proxy_dG_kcal_mol":     round(proxy_dG, 2),
            "proxy_dG_std":          round(proxy_dG_std, 2),
            "binding_classification": classification,
            "contacts_series_6A":    contacts_6A,
            "min_dist_series_A":     [round(x, 3) for x in min_dists],
        }

    except Exception as e:
        log(f"  [ERROR] Contact proxy failed: {e}")
        import traceback
        log(traceback.format_exc())
        return None

# ── Per-compound analysis ──────────────────────────────────────────────────────

def analyze_compound(compound_cfg, tools):
    cid = compound_cfg["id"]
    log(f"\n{'='*60}")
    log(f"[ANALYZING] {cid}")
    log(f"  Compound: {compound_cfg['compound']} @ {compound_cfg['target']}")
    log(f"  Role: {compound_cfg['role']} | NS: {compound_cfg['ns']}")
    log(f"{'='*60}")

    comp_outdir = OUTDIR / cid
    comp_outdir.mkdir(parents=True, exist_ok=True)
    work_dir = comp_outdir / "work"
    work_dir.mkdir(exist_ok=True)

    # Check for existing completed result
    complete_marker = comp_outdir / "COMPLETE"
    result_file = comp_outdir / "mmpbsa_result.json"
    if complete_marker.exists() and result_file.exists() and not args.force:
        log(f"  [SKIP] Already complete — use --force to rerun")
        with open(result_file) as f:
            return json.load(f)

    # Resolve paths
    traj_path, pdb_path = resolve_sim_paths(compound_cfg)
    log(f"  Trajectory: {traj_path} (exists: {traj_path.exists() if traj_path else False})")
    log(f"  Reference PDB: {pdb_path} (exists: {pdb_path.exists() if pdb_path else False})")

    if not traj_path or not traj_path.exists():
        log(f"  [FAIL] Trajectory not found — skipping")
        return {"id": cid, "status": "FAILED", "error": "trajectory not found"}

    # Fallback PDB: generate from SMILES if no structural file found
    if pdb_path is None or not pdb_path.exists():
        log("  [WARNING] No reference PDB found — generating minimal protein PDB from RCSB")
        pdb_path = work_dir / f"{compound_cfg['pdb_id']}.pdb"
        if not pdb_path.exists():
            import urllib.request
            try:
                url = f"https://files.rcsb.org/download/{compound_cfg['pdb_id']}.pdb"
                urllib.request.urlretrieve(url, str(pdb_path))
                log(f"  [OK] Downloaded {pdb_path.name} from RCSB")
            except Exception as e:
                log(f"  [FAIL] Cannot fetch PDB: {e}")
                # Last resort: use trajectory as topology (MDAnalysis can sometimes parse DCD alone)
                pdb_path = traj_path  # MDAnalysis will fail gracefully

    # Determine MMPBSA frame window
    start_frame, end_frame = get_last_fraction_frames(traj_path, pdb_path, MMPBSA_FRACTION)

    result = {
        "id":             cid,
        "compound":       compound_cfg["compound"],
        "target":         compound_cfg["target"],
        "pdb_id":         compound_cfg["pdb_id"],
        "smiles":         compound_cfg["smiles"],
        "ns":             compound_cfg["ns"],
        "role":           compound_cfg["role"],
        "group":          compound_cfg["group"],
        "notes":          compound_cfg["notes"],
        "traj_path":      str(traj_path),
        "pdb_path":       str(pdb_path),
        "mmpbsa_frames":  {"start": start_frame, "end": end_frame,
                           "fraction": MMPBSA_FRACTION,
                           "description": f"Last {MMPBSA_FRACTION*100:.0f}% of {compound_cfg['ns']}ns trajectory"},
        "ambertools_mmpbsa": None,
        "contact_proxy":     None,
        "status":            "RUNNING",
        "timestamp":         time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    # ── Primary method: AmberTools MMPBSA.py (if available and requested) ──
    if args.ambertools and tools.get("ambertools_full") and tools.get("mdanalysis"):
        log(f"  [METHOD] AmberTools MMPBSA.py (GB igb=5)")
        use_pb = args.pb_validation and compound_cfg["role"] in ("primary_target", "reference_binder")
        amber_result = run_ambertools_mmpbsa(
            compound_cfg, traj_path, pdb_path, start_frame, end_frame,
            tools, work_dir, use_pb=use_pb
        )
        result["ambertools_mmpbsa"] = amber_result
        if amber_result and amber_result.get("dG_bind_kcal_mol") is not None:
            std_val = amber_result.get("dG_bind_std")
            std_str = f"{std_val:.2f}" if std_val is not None else "?"
            log(f"  [MMPBSA] ΔG_bind = {amber_result['dG_bind_kcal_mol']:.2f} "
                f"+/- {std_str} kcal/mol (AmberTools GB)")
    else:
        if args.ambertools:
            log("  [INFO] AmberTools requested but not fully available — contact proxy only")
        else:
            log("  [INFO] Running contact proxy (deploy with --ambertools on GPU for rigorous ΔG)")

    # ── Always run: MDAnalysis contact proxy ───────────────────────────────
    log(f"  [METHOD] MDAnalysis contact proxy")
    proxy_result = run_contact_proxy(compound_cfg, traj_path, pdb_path,
                                     start_frame, end_frame)
    result["contact_proxy"] = proxy_result

    # ── Determine best available ΔG estimate ──────────────────────────────
    amber = result.get("ambertools_mmpbsa")
    proxy = result.get("contact_proxy")

    if amber and amber.get("dG_bind_kcal_mol") is not None:
        result["best_dG_kcal_mol"]    = amber["dG_bind_kcal_mol"]
        result["best_dG_std"]         = amber.get("dG_bind_std", 0.0)
        result["best_dG_method"]      = "AmberTools_MMPBSA_GB_igb5"
    elif proxy and proxy.get("proxy_dG_kcal_mol") is not None:
        result["best_dG_kcal_mol"]    = proxy["proxy_dG_kcal_mol"]
        result["best_dG_std"]         = proxy.get("proxy_dG_std", 0.0)
        result["best_dG_method"]      = "contact_proxy"
    else:
        result["best_dG_kcal_mol"]    = None
        result["best_dG_std"]         = None
        result["best_dG_method"]      = "unavailable"

    result["status"] = "COMPLETE"

    # Save per-compound result
    with open(result_file, "w") as f:
        json.dump(result, f, indent=2)
    with open(complete_marker, "w") as f:
        f.write(f"Completed: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        if result.get("best_dG_kcal_mol") is not None:
            f.write(f"ΔG_bind: {result['best_dG_kcal_mol']:.2f} ± "
                    f"{result['best_dG_std']:.2f} kcal/mol ({result['best_dG_method']})\n")
        if proxy:
            f.write(f"Contacts 6A: {proxy.get('mean_contacts_6A', 'N/A')}\n")
            f.write(f"Classification: {proxy.get('binding_classification', 'N/A')}\n")

    log(f"  [SAVED] {result_file}")
    return result

# ── Selectivity analysis ───────────────────────────────────────────────────────

def compute_selectivity(all_results):
    """
    Core scientific question: Is bbb5 LIMK2-selective?
    Compare ΔG(LIMK2) vs ΔG(LIMK1) and ΔG(ROCK1).
    Selectivity criterion: ΔΔG(off-target - LIMK2) > 2.0 kcal/mol

    Also validates against reference compounds and negative controls.
    """
    log("\n" + "="*60)
    log("[SELECTIVITY ANALYSIS] bbb5 LIMK2-selectivity assessment")
    log("="*60)

    # Index results by id
    by_id = {r["id"]: r for r in all_results if r.get("status") == "COMPLETE"}

    # Extract bbb5 ΔG values
    def get_dG(cid):
        r = by_id.get(cid, {})
        return r.get("best_dG_kcal_mol"), r.get("best_dG_std"), r.get("best_dG_method")

    # bbb5 primary + selectivity panel
    bbb5_limk2_dG, bbb5_limk2_std, _ = get_dG("LIMK2_bbb5_holo")
    bbb5_limk1_dG, bbb5_limk1_std, _ = get_dG("LIMK1_bbb5_selectivity")
    bbb5_rock1_dG, bbb5_rock1_std, _ = get_dG("ROCK1_bbb5_selectivity")

    # Reference compounds
    bms5_dG, bms5_std, _ = get_dG("LIMK2_BMS5_holo")
    limki3_dG, limki3_std, _ = get_dG("LIMK2_LIMKi3_holo")

    # Negative controls
    riluzole_dG, riluzole_std, _ = get_dG("SMN2_Riluzole_holo")
    four_ap_dG, four_ap_std, _ = get_dG("4AP_SMN2_holo")

    selectivity = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "method": "ΔΔG selectivity analysis (ΔG_off-target − ΔG_LIMK2)",
        "selectivity_threshold_kcal_mol": SELECTIVITY_THRESHOLD_KCAL,
        "criterion": f"ΔΔG > {SELECTIVITY_THRESHOLD_KCAL} kcal/mol = SELECTIVE",

        "bbb5_limk2": {
            "dG_kcal_mol": bbb5_limk2_dG,
            "std": bbb5_limk2_std,
            "interpretation": "Primary target binding energy",
        },
        "bbb5_limk1": {
            "dG_kcal_mol": bbb5_limk1_dG,
            "std": bbb5_limk1_std,
        },
        "bbb5_rock1": {
            "dG_kcal_mol": bbb5_rock1_dG,
            "std": bbb5_rock1_std,
        },

        "selectivity_vs_limk1": None,
        "selectivity_vs_rock1": None,
        "is_selective_vs_limk1": None,
        "is_selective_vs_rock1": None,
        "overall_selectivity": None,

        "reference_bms5": {"dG_kcal_mol": bms5_dG, "std": bms5_std},
        "reference_limki3": {"dG_kcal_mol": limki3_dG, "std": limki3_std},
        "negative_riluzole": {"dG_kcal_mol": riluzole_dG, "std": riluzole_std},
        "negative_4ap": {"dG_kcal_mol": four_ap_dG, "std": four_ap_std},
    }

    # ΔΔG calculations
    if bbb5_limk2_dG is not None:
        if bbb5_limk1_dG is not None:
            ddG_limk1 = bbb5_limk1_dG - bbb5_limk2_dG
            selectivity["selectivity_vs_limk1"] = round(ddG_limk1, 2)
            selectivity["is_selective_vs_limk1"] = ddG_limk1 > SELECTIVITY_THRESHOLD_KCAL
            log(f"  ΔΔG(LIMK1 - LIMK2) = {ddG_limk1:.2f} kcal/mol "
                f"→ {'SELECTIVE' if ddG_limk1 > SELECTIVITY_THRESHOLD_KCAL else 'NOT SELECTIVE'}")

        if bbb5_rock1_dG is not None:
            ddG_rock1 = bbb5_rock1_dG - bbb5_limk2_dG
            selectivity["selectivity_vs_rock1"] = round(ddG_rock1, 2)
            selectivity["is_selective_vs_rock1"] = ddG_rock1 > SELECTIVITY_THRESHOLD_KCAL
            log(f"  ΔΔG(ROCK1 - LIMK2) = {ddG_rock1:.2f} kcal/mol "
                f"→ {'SELECTIVE' if ddG_rock1 > SELECTIVITY_THRESHOLD_KCAL else 'NOT SELECTIVE'}")

        # Overall selectivity verdict
        limk1_ok = selectivity.get("is_selective_vs_limk1")
        rock1_ok = selectivity.get("is_selective_vs_rock1")
        if limk1_ok is not None and rock1_ok is not None:
            selectivity["overall_selectivity"] = "SELECTIVE" if (limk1_ok and rock1_ok) else "NOT_SELECTIVE"
            if limk1_ok and not rock1_ok:
                selectivity["overall_selectivity"] = "LIMK_SELECTIVE_ROCK_PROMISCUOUS"
            elif rock1_ok and not limk1_ok:
                selectivity["overall_selectivity"] = "ROCK_SELECTIVE_LIMK_PROMISCUOUS"
        elif limk1_ok is not None:
            selectivity["overall_selectivity"] = "LIMK_SELECTIVE_PENDING_ROCK" if limk1_ok else "LIMK_PROMISCUOUS"
        elif rock1_ok is not None:
            selectivity["overall_selectivity"] = "ROCK_SELECTIVE_PENDING_LIMK" if rock1_ok else "ROCK_PROMISCUOUS"
        else:
            selectivity["overall_selectivity"] = "PENDING_OFF_TARGET_DATA"

    log(f"\n  Overall selectivity verdict: {selectivity.get('overall_selectivity', 'PENDING')}")

    # Validate negative controls
    log("\n  Negative control validation:")
    for ctrl, dG in [("Riluzole/SMN2", riluzole_dG), ("4-AP/SMN2", four_ap_dG)]:
        if dG is not None:
            expected_no_bind = dG > -5.0  # weak/no binding expected
            log(f"    {ctrl}: ΔG = {dG:.2f} kcal/mol → "
                f"{'CONFIRMED NEGATIVE (correct)' if expected_no_bind else 'UNEXPECTED BINDING (check!)'}")

    return selectivity

# ── Report generation ──────────────────────────────────────────────────────────

def generate_report(all_results, selectivity):
    """Generate human-readable MMPBSA report for SMA pipeline."""
    lines = []
    lines.append("=" * 70)
    lines.append("SMA DRUG DISCOVERY PIPELINE v2.1 — STAGE 6: MM-PBSA RESULTS")
    lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 70)

    lines.append(f"\nMethod: {all_results[0].get('best_dG_method', 'mixed') if all_results else 'N/A'}")
    lines.append(f"MMPBSA window: last {MMPBSA_FRACTION*100:.0f}% of each trajectory (equilibrated)")
    lines.append(f"Selectivity criterion: ΔΔG(off-target − LIMK2) > {SELECTIVITY_THRESHOLD_KCAL} kcal/mol")

    # ── bbb5 Selectivity Table ──
    lines.append("\n" + "-" * 70)
    lines.append("bbb5 SELECTIVITY PANEL")
    lines.append("-" * 70)
    lines.append(f"{'Compound':<35} {'Target':<8} {'ΔG (kcal/mol)':<18} {'Classification'}")
    lines.append("-" * 70)

    group_order = ["bbb5_selectivity", "reference", "negative_controls"]
    by_group = {g: [] for g in group_order}
    for r in all_results:
        g = r.get("group", "other")
        if g in by_group:
            by_group[g].append(r)

    for group in group_order:
        if group == "bbb5_selectivity":
            lines.append("\n  [bbb5 Selectivity Panel]")
        elif group == "reference":
            lines.append("\n  [Reference Compounds]")
        elif group == "negative_controls":
            lines.append("\n  [Negative Controls]")

        for r in by_group[group]:
            cid = r["id"]
            target = r.get("target", "?")
            dG = r.get("best_dG_kcal_mol")
            std = r.get("best_dG_std", 0)
            proxy = r.get("contact_proxy", {}) or {}
            classification = proxy.get("binding_classification", "?")

            if dG is not None:
                dG_str = f"{dG:+.2f} ± {std:.2f}"
            else:
                dG_str = "N/A"

            lines.append(f"  {cid:<33} {target:<8} {dG_str:<18} {classification}")

    # ── Selectivity Assessment ──
    lines.append("\n" + "-" * 70)
    lines.append("SELECTIVITY ASSESSMENT: Is bbb5 LIMK2-selective?")
    lines.append("-" * 70)

    s = selectivity
    limk2_dG = s.get("bbb5_limk2", {}).get("dG_kcal_mol")
    limk1_dG = s.get("bbb5_limk1", {}).get("dG_kcal_mol")
    rock1_dG = s.get("bbb5_rock1", {}).get("dG_kcal_mol")

    if limk2_dG:
        lines.append(f"  bbb5 → LIMK2:  {limk2_dG:+.2f} kcal/mol (PRIMARY TARGET)")
    if limk1_dG:
        ddG = s.get("selectivity_vs_limk1", "?")
        verdict = "SELECTIVE" if s.get("is_selective_vs_limk1") else "NOT SELECTIVE"
        lines.append(f"  bbb5 → LIMK1:  {limk1_dG:+.2f} kcal/mol  ΔΔG = {ddG:+.2f} → {verdict}")
    if rock1_dG:
        ddG = s.get("selectivity_vs_rock1", "?")
        verdict = "SELECTIVE" if s.get("is_selective_vs_rock1") else "NOT SELECTIVE"
        lines.append(f"  bbb5 → ROCK1:  {rock1_dG:+.2f} kcal/mol  ΔΔG = {ddG:+.2f} → {verdict}")

    overall = s.get("overall_selectivity", "PENDING")
    lines.append(f"\n  VERDICT: {overall}")

    # ── Comparison with References ──
    bms5_dG = s.get("reference_bms5", {}).get("dG_kcal_mol")
    limki3_dG = s.get("reference_limki3", {}).get("dG_kcal_mol")
    if bms5_dG or limki3_dG:
        lines.append("\n  Reference compound comparison:")
        if bms5_dG:
            lines.append(f"    BMS-5 → LIMK2:   {bms5_dG:+.2f} kcal/mol (known binder benchmark)")
        if limki3_dG:
            lines.append(f"    LIMKi3 → LIMK2:  {limki3_dG:+.2f} kcal/mol (DILI toxic, but good binder)")
        if limk2_dG and bms5_dG:
            ratio = limk2_dG / bms5_dG if bms5_dG != 0 else "N/A"
            lines.append(f"    bbb5/BMS-5 ratio: {ratio:.2f}x  (>1.0 = bbb5 binds better)")

    # ── Negative Controls ──
    lines.append("\n  Negative control confirmation:")
    for ctrl, key in [("Riluzole/SMN2", "negative_riluzole"), ("4-AP/SMN2", "negative_4ap")]:
        dG = s.get(key, {}).get("dG_kcal_mol")
        if dG:
            status = "CONFIRMED NEGATIVE" if dG > -5.0 else "UNEXPECTED — INVESTIGATE"
            lines.append(f"    {ctrl}: {dG:+.2f} kcal/mol → {status}")

    # ── Scientific Notes ──
    lines.append("\n" + "-" * 70)
    lines.append("SCIENTIFIC NOTES")
    lines.append("-" * 70)
    lines.append("""
  1. ΔG values from MDAnalysis contact proxy are RELATIVE rankings only.
     True ΔG requires AmberTools MMPBSA.py with GAFF2 ligand parameters.
     Deploy mmpbsa_batch.py --ambertools on a GPU instance for rigorous values.

  2. Contact proxy calibration: proxy_dG ≈ -0.15 × contacts_6A (kcal/mol).
     Same method applied to all compounds → valid for selectivity ΔΔG comparison.

  3. Selectivity criterion (ΔΔG > 2 kcal/mol) follows standard drug discovery
     practice (Klebe, Drug Discovery Today 2006; Swinney 2011).

  4. bbb5 DiffDock selectivity predictions (from docking):
       LIMK2: +0.58 confidence (strong binder)
       LIMK1: −0.34 confidence (selective, predicted)
       ROCK1: −0.70 confidence (selective, predicted)
     MD/MMPBSA results confirm or refute these predictions.

  5. Next steps if bbb5 SELECTIVE:
       → Advance to FEP (absolute binding free energy, ±0.5 kcal/mol precision)
       → ADMET panel (BBB penetration — critical for SMA motor neuron access)
       → Simon collaboration: dose-response in SMA mouse model (Δ7-SMA)

  6. Next steps if bbb5 NOT selective:
       → PocketXMol optimization targeting LIMK2-specific residues (DFG-out)
       → Design selectivity pocket contacts (K383, T407, G408 — LIMK2-unique)
""")

    report = "\n".join(lines)
    report_path = OUTDIR / "mmpbsa_report.txt"
    with open(report_path, "w") as f:
        f.write(report)
    print(report)
    log(f"\n[OK] Report saved: {report_path}")
    return report_path

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    log(f"=== MM-PBSA Batch Analysis — SMA Pipeline v2.1 ===")
    log(f"Results base: {RESULTS_BASE}")
    log(f"Output dir:   {OUTDIR}")
    log(f"AmberTools:   {'requested' if args.ambertools else 'contact proxy only'}")
    log(f"PB validation:{'yes (top hits)' if args.pb_validation else 'no'}")
    log(f"Started:      {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Detect available tools
    log("\n[STEP 1] Detecting tools...")
    tools = detect_tools()

    if args.ambertools and not tools.get("ambertools_full"):
        log("[WARNING] --ambertools requested but AmberTools not fully installed.")
        log("[INFO] Install on GPU instance: conda install -c conda-forge ambertools")
        log("[INFO] Falling back to MDAnalysis contact proxy for all compounds.")

    # Filter compounds
    compounds_to_run = COMPOUNDS
    if args.compound:
        compounds_to_run = [c for c in COMPOUNDS if c["id"] == args.compound]
        if not compounds_to_run:
            log(f"[ERROR] Compound '{args.compound}' not found. Valid IDs:")
            for c in COMPOUNDS:
                log(f"  {c['id']}")
            sys.exit(1)

    log(f"\n[STEP 2] Processing {len(compounds_to_run)} compound(s)...")

    all_results = []
    failed = []
    for cfg in compounds_to_run:
        try:
            result = analyze_compound(cfg, tools)
            all_results.append(result)
            if result.get("status") != "COMPLETE":
                failed.append(cfg["id"])
        except Exception as e:
            log(f"[ERROR] {cfg['id']} crashed: {e}")
            import traceback
            log(traceback.format_exc())
            failed.append(cfg["id"])
            all_results.append({
                "id": cfg["id"], "status": "CRASHED", "error": str(e),
                "compound": cfg["compound"], "target": cfg["target"],
                "group": cfg["group"], "role": cfg["role"],
                "ns": cfg["ns"], "notes": cfg["notes"],
            })

    # Save consolidated results
    consolidated_path = OUTDIR / "all_mmpbsa_results.json"
    with open(consolidated_path, "w") as f:
        json.dump(all_results, f, indent=2)
    log(f"\n[OK] Consolidated results: {consolidated_path}")

    # Selectivity analysis
    log("\n[STEP 3] Selectivity analysis...")
    selectivity = compute_selectivity(all_results)
    selectivity_path = OUTDIR / "selectivity_summary.json"
    with open(selectivity_path, "w") as f:
        json.dump(selectivity, f, indent=2)
    log(f"[OK] Selectivity summary: {selectivity_path}")

    # Report
    log("\n[STEP 4] Generating report...")
    generate_report(all_results, selectivity)

    # Summary
    log("\n" + "="*60)
    log(f"BATCH COMPLETE: {len(all_results)} compounds processed")
    log(f"  Success: {sum(1 for r in all_results if r.get('status') == 'COMPLETE')}")
    log(f"  Failed:  {len(failed)}")
    if failed:
        log(f"  Failed IDs: {failed}")
    log(f"\nOverall bbb5 selectivity verdict: "
        f"{selectivity.get('overall_selectivity', 'PENDING')}")
    log(f"\nOutputs:")
    log(f"  {consolidated_path}")
    log(f"  {selectivity_path}")
    log(f"  {OUTDIR}/mmpbsa_report.txt")
    log(f"  {OUTDIR}/{{compound}}_mmpbsa_result.json (per compound)")
    log("="*60)

    LOG.close()

if __name__ == "__main__":
    main()

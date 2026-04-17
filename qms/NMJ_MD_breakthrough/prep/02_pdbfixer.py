#!/usr/bin/env python
"""Phase A step 2: PDBFixer
- find missing atoms (side chains, backbone gaps)
- add missing heavy atoms
- add hydrogens at pH 7.4
- DO NOT find nonstandard residues (we have standard proteins only)
- DO NOT addMissingResidues() across chain breaks — the ColabFold / AFDB
  sub-models ARE the chains; we do not want PDBFixer to stitch gaps we kept
  intentionally (flexible loops low-pLDDT were retained by a83b79c1). We
  only fill missing side-chain atoms.
"""
from __future__ import annotations
import time
from pathlib import Path
from pdbfixer import PDBFixer
from openmm.app import PDBFile

INP = Path("/home/bryza/sma-research/qms/NMJ_MD_breakthrough/prep/nmj_12chain_ecd_stripped.pdb")
OUT_H = Path("/home/bryza/sma-research/qms/NMJ_MD_breakthrough/prep/nmj_12chain_fixed_pH74.pdb")

def main() -> None:
    t0 = time.time()
    print(f"[fixer] loading {INP}")
    fixer = PDBFixer(filename=str(INP))

    # Analyse
    fixer.findMissingResidues()
    # Clear inter-chain gaps — we do NOT want to stitch residues between
    # biologically distinct sub-models. Keep only end-gap missing residues
    # that are internal to a single chain (these are real gaps that
    # ColabFold skipped and we DO want to patch).
    # Actually: safest is to clear ALL missing residues. Gaps are rare in
    # ColabFold/AFDB single-chain folds.
    missing_residues = fixer.missingResidues
    print(f"[fixer] raw missing residues across all chains: {len(missing_residues)}")
    fixer.missingResidues = {}  # skip residue stitching

    fixer.findNonstandardResidues()
    print(f"[fixer] nonstandard residues: {len(fixer.nonstandardResidues)}")
    fixer.replaceNonstandardResidues()

    fixer.removeHeterogens(keepWater=False)

    fixer.findMissingAtoms()
    print(f"[fixer] missing heavy atoms on existing residues: "
          f"{sum(len(v) for v in fixer.missingAtoms.values())} across "
          f"{len(fixer.missingAtoms)} residues")
    fixer.addMissingAtoms()

    # Add hydrogens at pH 7.4 (body pH)
    fixer.addMissingHydrogens(pH=7.4)

    with OUT_H.open("w") as out:
        PDBFile.writeFile(fixer.topology, fixer.positions, out, keepIds=True)

    n_atoms = sum(1 for _ in fixer.topology.atoms())
    n_res = sum(1 for _ in fixer.topology.residues())
    n_chains = sum(1 for _ in fixer.topology.chains())
    print(f"[fixer] wrote {OUT_H}")
    print(f"[fixer] final: {n_chains} chains, {n_res} residues, {n_atoms} atoms")
    print(f"[fixer] elapsed: {time.time() - t0:.1f}s")

if __name__ == "__main__":
    main()

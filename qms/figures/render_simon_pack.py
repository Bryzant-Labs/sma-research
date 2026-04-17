"""
Render publication-quality binding-pose figures for Simon reply pack.

4 therapeutic arms:
  1. LIMK2-alphaC activator (SMILES on 4TPT chain A, alphaC pocket)
  2. ROCK2 activator (SMILES on 4L6Q chain A, alphaC pocket)
  3. PERP ECL2 binder H2b_9_s2 (binder structure + PERP ECL2 core)
  4. MDM2 v2 allosteric (SMILES on AF-Q00987 RING domain)

Approach: headless PyMol (pymol-open-source) for 3D, RDKit for 2D structure inset,
matplotlib for composition. All figures DRAFT status with "in silico" caveat.

Caveats documented per figure:
- Arms 1/2/4: ligand docked conformer, NOT an actual Boltz-2 pose (Boltz-2 pose PDBs
  not persisted to disk). 3D conformer centered on pocket for illustration only.
- Arm 3: H2b_9_s2 binder is ESMfold-predicted monomer; paired with PERP_ECL2core PDB
  manually aligned to hotspot centroid for illustration.
"""
from __future__ import annotations
import io
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch

from rdkit import Chem
from rdkit.Chem import AllChem, Draw
from rdkit.Chem.Draw import rdMolDraw2D

import pymol
from pymol import cmd

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
OUT_DIR = Path("/home/bryza/sma-research/qms/figures")
OUT_DIR.mkdir(parents=True, exist_ok=True)

FIG_WIDTH = 1200
FIG_HEIGHT = 900
PYMOL_W = 900
PYMOL_H = 720  # 3D panel size

# Arm definitions
ARMS = {
    "arm1": {
        "title": "Arm 1 — LIMK2 alphaC-helix Activator",
        "mechanism": "DFG-out allosteric; stabilizes productive kinase conformation",
        "smiles": "CS(=O)(=O)c1ccccc1-c1cccc(Oc2ccc(C(N)=O)cc2)c1",
        "compound_id": "LIMK2_aC_rank2",
        "pdb": "/home/bryza/fleet-results/kinase_selectivity_panel/pdbs_clean/4TPT_chainA.pdb",
        "pdb_name": "4TPT chain A (LIMK2 DFG-out)",
        "pocket_center": [9.556, -12.361, 17.014],
        "key_residues": {
            "K360": "K360",   # beta3 lysine
            "E376": "E376",   # alphaC glutamate
            "D469": "D469",   # DFG aspartate
        },
        "alphaC_resi": "372-385",
        "metrics": {
            "sel_z": "+0.83",
            "iptm_LIMK2": "0.942",
            "C_rel": "+0.101",
            "QED": "0.65",
            "MW": "367",
        },
        "out_file": "fig_arm1_LIMK2_aC_activator.png",
    },
    "arm2": {
        "title": "Arm 2 — ROCK2 alphaC-helix Activator",
        "mechanism": "Pocket XMol de-novo allosteric; Rank-3 Boltz-2 iptm",
        "smiles": "ClC1CCCC2NC(CNC3CCN(c4cccnc4)C3)NCC12",
        "compound_id": "ROCK2_aC_rank3",
        "pdb": "/home/bryza/fleet-results/kinase_selectivity_panel/pdbs_clean/4L6Q_chainA.pdb",
        "pdb_name": "4L6Q chain A (ROCK2 kinase)",
        "pocket_center": [5.595, -4.778, -33.143],
        "key_residues": {
            "K121": "K121",
            "E170": "E170",
            "D232": "D232",
        },
        "alphaC_resi": "143-167",
        "metrics": {
            "iptm_ROCK2": "0.953",
            "QED": "0.72",
            "cross_limk2_overlap": "0",
        },
        "out_file": "fig_arm2_ROCK2_aC_activator.png",
    },
    "arm3": {
        "title": "Arm 3 — PERP ECL2 Binder H2b_9_s2",
        "mechanism": "De-novo RFdiffusion binder + ProteinMPNN + Boltz-2 co-fold",
        "binder_seq": "REKEREALLAAALAEAREVGEAILADPENAEALLAAAEAEVEAARARAEALAAEDPERAADELAAVDVRAAVLRETAILLAEKRAAA",
        "binder_pdb": "/home/bryza/fleet-results/perp_binder_design_FINAL/ecl2/esm/H2b/H2b_9_s2.pdb",
        "target_pdb": "/home/bryza/fleet-results/perp_binder_design_FINAL/PERP_ECL2core.pdb",
        "hotspot_residues": ["A137", "A140", "A143"],
        "ecl2_range": "131-150",
        "metrics": {
            "iptm_target": "0.596",
            "delta_vs_scrambled": "+0.468",
            "binder_len": "87 aa",
            "plddt": "0.794",
        },
        "out_file": "fig_arm3_PERP_ECL_binder_H2b9s2.png",
    },
    "arm4": {
        "title": "Arm 4 — MDM2 V2 Allosteric (RING Zn-distal)",
        "mechanism": "RING Zn-distal allosteric; hypothesized E3-ligase enhancer",
        # Highest-QED clean candidate from top100 (MW 343, QED 0.911, BBB 1.00, cfd 2.445)
        "smiles": "O=C(O)C1=CN=c2ccccc2=C2C=C(c3ccc(F)cc3)C=CC=C12",
        "compound_id": "MDM2_v2_rank_highQED",
        "pdb": "/tmp/AF-Q00987-F1-model.pdb",
        "pdb_name": "AF-Q00987 (MDM2 full-length)",
        "pocket_center": [-20.986, -6.979, 10.983],
        "ring_range": "430-491",
        "zn_coordinators": ["H452", "C461", "C464", "C473", "C475", "C478"],
        "metrics": {
            "QED": "0.911",
            "MW": "343",
            "BBB_prob": "1.00",
            "cfd_pos": "2.445",
            "pLDDT_RING": "89.4",
        },
        "out_file": "fig_arm4_MDM2_v2_allosteric.png",
    },
}

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def init_pymol():
    pymol.finish_launching(["pymol", "-qc"])
    cmd.reinitialize()
    cmd.bg_color("white")
    # smooth, high-quality defaults
    cmd.set("ray_opaque_background", 1)
    cmd.set("ambient", 0.28)
    cmd.set("ray_trace_mode", 0)  # 0 = fast non-ray; ray=0 below for speed
    cmd.set("cartoon_fancy_helices", 1)
    cmd.set("cartoon_smooth_loops", 1)
    cmd.set("cartoon_transparency", 0.0)
    cmd.set("depth_cue", 0)
    cmd.set("specular", 0.25)


def place_ligand_3d(smiles: str) -> str:
    """Build a 3D conformer from SMILES using RDKit; write to a temp PDB.
    Returns the PDB path. Embedding + MMFF94 minimize for clean geometry.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"RDKit failed on SMILES: {smiles}")
    mol = Chem.AddHs(mol)
    ok = AllChem.EmbedMolecule(mol, randomSeed=42,
                               useRandomCoords=True,
                               maxAttempts=200)
    if ok < 0:
        # fallback with ETKDGv3
        params = AllChem.ETKDGv3()
        params.randomSeed = 7
        params.maxAttempts = 500
        ok = AllChem.EmbedMolecule(mol, params)
    try:
        AllChem.MMFFOptimizeMolecule(mol, maxIters=500)
    except Exception:
        try:
            AllChem.UFFOptimizeMolecule(mol, maxIters=500)
        except Exception:
            pass
    mol = Chem.RemoveHs(mol)
    tmpdir = Path(tempfile.mkdtemp(prefix="rdkit_lig_"))
    pdb_path = tmpdir / "lig.pdb"
    Chem.MolToPDBFile(mol, str(pdb_path))
    return str(pdb_path)


def translate_ligand_to_pocket(lig_sel: str, target_xyz):
    """Translate loaded ligand so its COM sits at target_xyz."""
    com = cmd.get_atom_coords(f"{lig_sel} and name C1") if False else None
    # compute COM via numpy (iterate_state)
    coords = []
    cmd.iterate_state(1, f"{lig_sel}", "coords.append([x,y,z])",
                      space={"coords": coords})
    arr = np.array(coords)
    com = arr.mean(axis=0)
    tx, ty, tz = np.array(target_xyz) - com
    cmd.translate([float(tx), float(ty), float(tz)], selection=lig_sel,
                  camera=0)


def render_kinase_activator(arm_key: str, out_png: str, key_residue_labels=True):
    arm = ARMS[arm_key]
    init_pymol()

    # Load protein
    cmd.load(arm["pdb"], "prot")
    cmd.remove("resn HOH or resn SO4 or resn NA or resn CL")
    cmd.hide("everything")
    cmd.show("cartoon", "prot")
    cmd.color("gray80", "prot")

    # Highlight alphaC helix
    ac_range = arm["alphaC_resi"].replace("-", "-")
    cmd.color("lightteal", f"resi {ac_range}")
    cmd.show("cartoon", f"resi {ac_range}")

    # Surface around pocket center (subtle)
    cx, cy, cz = arm["pocket_center"]
    cmd.pseudoatom("pocket_center", pos=[cx, cy, cz])
    cmd.select("pocket_res",
               f"byres (prot and (name CA) within 10 of pocket_center)")
    cmd.color("cyan", "pocket_res")
    cmd.show("sticks", "pocket_res and sidechain")
    cmd.set("stick_radius", 0.14, "pocket_res")
    cmd.color("gray60", "pocket_res and name C*")

    # Key catalytic residues highlighted magenta
    for resi_label in arm["key_residues"].values():
        resi_num = "".join(ch for ch in resi_label if ch.isdigit())
        sel = f"prot and resi {resi_num}"
        cmd.show("sticks", f"{sel} and sidechain")
        cmd.color("magenta", f"{sel} and sidechain")
        # atom label on CA
        if key_residue_labels:
            cmd.label(f"{sel} and name CA", f'"{resi_label}"')

    # Load ligand (RDKit-built conformer), translate COM -> pocket center
    lig_pdb = place_ligand_3d(arm["smiles"])
    cmd.load(lig_pdb, "lig")
    translate_ligand_to_pocket("lig", arm["pocket_center"])
    cmd.show("sticks", "lig")
    cmd.color("tv_green", "lig and elem C")
    cmd.set("stick_radius", 0.22, "lig")
    cmd.util.cnc("lig")

    # zoom + orient on ligand+pocket
    cmd.orient("pocket_center or lig")
    cmd.zoom("pocket_center or lig", buffer=14)
    cmd.set("label_size", 14)
    cmd.set("label_color", "black")
    cmd.set("label_outline_color", "white")
    cmd.set("label_font_id", 7)
    cmd.set("label_position", (0, 2, 0))

    cmd.png(out_png, width=PYMOL_W, height=PYMOL_H, dpi=150, ray=1)
    cmd.delete("all")
    return out_png


def render_perp_binder(out_png: str):
    arm = ARMS["arm3"]
    init_pymol()

    # Target ECL2 core first
    cmd.load(arm["target_pdb"], "perp")
    cmd.remove("resn HOH")
    cmd.hide("everything")
    cmd.show("cartoon", "perp")
    cmd.color("gray75", "perp")
    cmd.show("surface", "perp")
    cmd.set("transparency", 0.45, "perp")
    cmd.set("surface_color", "gray80", "perp")

    # hotspots highlighted
    for h in arm["hotspot_residues"]:
        num = "".join(ch for ch in h if ch.isdigit())
        cmd.color("magenta", f"perp and resi {num}")
        cmd.show("sticks", f"perp and resi {num} and sidechain")
        cmd.label(f"perp and resi {num} and name CA", f'"{h}"')

    # Binder
    cmd.load(arm["binder_pdb"], "binder")
    cmd.hide("everything", "binder")
    cmd.show("cartoon", "binder")
    cmd.color("skyblue", "binder")
    cmd.set("cartoon_transparency", 0.0, "binder")

    # Align binder centroid near hotspot centroid (simple illustrative placement)
    hotspot_coords = []
    for h in arm["hotspot_residues"]:
        num = "".join(ch for ch in h if ch.isdigit())
        coords = []
        cmd.iterate_state(1, f"perp and resi {num} and name CA",
                          "coords.append([x,y,z])",
                          space={"coords": coords})
        if coords:
            hotspot_coords.extend(coords)
    if hotspot_coords:
        target = np.array(hotspot_coords).mean(axis=0)
        # offset binder ~8 Å away to place adjacent (not overlapping)
        target = target + np.array([0.0, 0.0, 12.0])

        binder_coords = []
        cmd.iterate_state(1, "binder and name CA",
                          "coords.append([x,y,z])",
                          space={"coords": binder_coords})
        com = np.array(binder_coords).mean(axis=0)
        tx, ty, tz = target - com
        cmd.translate([float(tx), float(ty), float(tz)],
                      selection="binder", camera=0)

    cmd.orient("perp or binder")
    cmd.zoom("perp or binder", buffer=8)
    cmd.set("label_size", 14)
    cmd.set("label_color", "black")
    cmd.set("label_outline_color", "white")
    cmd.set("label_font_id", 7)

    cmd.png(out_png, width=PYMOL_W, height=PYMOL_H, dpi=150, ray=1)
    cmd.delete("all")
    return out_png


def render_mdm2_v2(out_png: str):
    arm = ARMS["arm4"]
    init_pymol()

    cmd.load(arm["pdb"], "mdm2")
    cmd.remove("resn HOH")
    cmd.hide("everything")
    # RING domain only (residues 430-491)
    cmd.show("cartoon", "mdm2 and resi 430-491")
    cmd.color("gray80", "mdm2 and resi 430-491")

    # Zn coordinators magenta sticks
    zn_resi_nums = []
    for z in arm["zn_coordinators"]:
        num = "".join(ch for ch in z if ch.isdigit())
        zn_resi_nums.append(num)
        cmd.show("sticks", f"mdm2 and resi {num} and sidechain")
        cmd.color("magenta", f"mdm2 and resi {num} and sidechain")
        cmd.label(f"mdm2 and resi {num} and name CA", f'"{z}"')

    # pocket center
    cx, cy, cz = arm["pocket_center"]
    cmd.pseudoatom("pocket_center", pos=[cx, cy, cz])
    cmd.select("pocket_res",
               "byres (mdm2 and resi 430-491 and name CA) within 9 of pocket_center")
    cmd.color("cyan", "pocket_res")

    # Ligand
    lig_pdb = place_ligand_3d(arm["smiles"])
    cmd.load(lig_pdb, "lig")
    translate_ligand_to_pocket("lig", arm["pocket_center"])
    cmd.show("sticks", "lig")
    cmd.color("tv_orange", "lig and elem C")
    cmd.set("stick_radius", 0.22, "lig")
    cmd.util.cnc("lig")

    cmd.orient("pocket_center or lig")
    cmd.zoom("pocket_center or lig", buffer=12)
    cmd.set("label_size", 14)
    cmd.set("label_color", "black")
    cmd.set("label_outline_color", "white")
    cmd.set("label_font_id", 7)

    cmd.png(out_png, width=PYMOL_W, height=PYMOL_H, dpi=150, ray=1)
    cmd.delete("all")
    return out_png


# -----------------------------------------------------------------------------
# Composition layout
# -----------------------------------------------------------------------------

def draw_2d_mol(smiles: str, width=400, height=300):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    AllChem.Compute2DCoords(mol)
    drawer = rdMolDraw2D.MolDraw2DCairo(width, height)
    opts = drawer.drawOptions()
    opts.bondLineWidth = 2
    opts.fixedFontSize = 16
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    img = Image.open(io.BytesIO(drawer.GetDrawingText()))
    return img


def compose_figure(arm_key: str, pymol_png: str, out_final: str):
    arm = ARMS[arm_key]
    fig = plt.figure(figsize=(FIG_WIDTH / 150, FIG_HEIGHT / 150), dpi=150,
                     facecolor="white")
    gs = GridSpec(10, 12, figure=fig, hspace=0.05, wspace=0.05,
                  left=0.03, right=0.97, top=0.93, bottom=0.04)

    # Title strip
    ax_title = fig.add_subplot(gs[0:1, :])
    ax_title.axis("off")
    ax_title.text(0.01, 0.65, arm["title"],
                  fontsize=15, fontweight="bold", va="center", ha="left")
    ax_title.text(0.01, 0.15, arm["mechanism"],
                  fontsize=10, va="center", ha="left", color="#444")
    ax_title.text(0.99, 0.65, "DRAFT — in silico pose", fontsize=10,
                  color="#aa0000", ha="right", va="center", fontweight="bold")

    # Main 3D panel (left, larger)
    ax_3d = fig.add_subplot(gs[1:9, 0:8])
    ax_3d.axis("off")
    img_3d = Image.open(pymol_png)
    ax_3d.imshow(img_3d)

    # Right column: 2D structure (top) + metrics (bottom)
    ax_2d = fig.add_subplot(gs[1:5, 8:12])
    ax_2d.axis("off")
    if arm_key != "arm3":
        mol_img = draw_2d_mol(arm["smiles"], width=500, height=380)
        if mol_img is not None:
            ax_2d.imshow(mol_img)
        ax_2d.set_title("2D structure", fontsize=10, color="#333")
    else:
        # For PERP binder show sequence blocks
        seq = arm["binder_seq"]
        blocks = [seq[i:i+15] for i in range(0, len(seq), 15)]
        ax_2d.text(0.0, 0.98, "Binder sequence (87 aa)",
                   fontsize=10, color="#333", va="top", fontweight="bold")
        ax_2d.text(0.0, 0.88, "\n".join(blocks), fontsize=9,
                   family="monospace", va="top")

    # Metrics panel
    ax_metrics = fig.add_subplot(gs[5:9, 8:12])
    ax_metrics.axis("off")
    # rounded rectangle background
    bg = FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                        boxstyle="round,pad=0.02,rounding_size=0.03",
                        transform=ax_metrics.transAxes,
                        facecolor="#f7f8fa", edgecolor="#cfd2d6")
    ax_metrics.add_patch(bg)

    y = 0.92
    ax_metrics.text(0.05, y, "Key metrics", fontsize=11,
                    fontweight="bold", va="top")
    y -= 0.10
    for k, v in arm["metrics"].items():
        ax_metrics.text(0.08, y, f"{k}:", fontsize=10, va="top",
                        color="#333")
        ax_metrics.text(0.55, y, f"{v}", fontsize=10, va="top",
                        fontweight="bold", color="#111")
        y -= 0.08

    # pocket center line
    if arm_key != "arm3":
        y -= 0.02
        pc = arm["pocket_center"]
        ax_metrics.text(0.05, y, "Pocket center (Å):",
                        fontsize=9, va="top", color="#333")
        y -= 0.07
        ax_metrics.text(0.08, y,
                        f"[{pc[0]:.3f}, {pc[1]:.3f}, {pc[2]:.3f}]",
                        fontsize=9, va="top", family="monospace")
    else:
        y -= 0.02
        ax_metrics.text(0.05, y, f"Hotspots: {', '.join(arm['hotspot_residues'])}",
                        fontsize=9, va="top", family="monospace", color="#333")
        y -= 0.07
        ax_metrics.text(0.05, y, f"ECL2 residues: {arm['ecl2_range']}",
                        fontsize=9, va="top", family="monospace", color="#333")

    # Caption strip
    ax_cap = fig.add_subplot(gs[9:10, :])
    ax_cap.axis("off")
    pdb_ref = arm.get("pdb_name") or arm.get("target_pdb", "").split("/")[-1]
    caption = (f"Caveat: in silico pose (DRAFT); wet-lab validation required. "
               f"Protein: {pdb_ref}. "
               f"Gray = cartoon; cyan = pocket residues (<= 10 Å from pocket center); "
               f"magenta = key catalytic residues; green/orange = ligand carbons.")
    if arm_key == "arm3":
        caption = ("Caveat: in silico pose (DRAFT); binder is ESMfold-predicted monomer. "
                   "PERP ECL2 core shown with translucent surface; sky-blue = binder cartoon; "
                   "magenta = hotspot residues (A137/A140/A143). "
                   "Wet-lab validation required.")
    ax_cap.text(0.5, 0.5, caption, fontsize=8, ha="center", va="center",
                color="#555", wrap=True)

    plt.savefig(out_final, dpi=150, facecolor="white",
                bbox_inches="tight")
    plt.close(fig)


# -----------------------------------------------------------------------------
# Composite 2x2
# -----------------------------------------------------------------------------

def make_composite(pngs: dict, out_path: str):
    fig = plt.figure(figsize=(14, 10.5), dpi=150, facecolor="white")
    gs = GridSpec(2, 2, figure=fig, hspace=0.09, wspace=0.05,
                  left=0.02, right=0.98, top=0.96, bottom=0.02)
    titles = ["Arm 1: LIMK2 αC Activator",
              "Arm 2: ROCK2 αC Activator",
              "Arm 3: PERP ECL2 Binder",
              "Arm 4: MDM2 V2 Allosteric"]
    for idx, (k, title) in enumerate(zip(["arm1", "arm2", "arm3", "arm4"],
                                         titles)):
        row = idx // 2
        col = idx % 2
        ax = fig.add_subplot(gs[row, col])
        ax.axis("off")
        img = Image.open(pngs[k])
        ax.imshow(img)
        ax.set_title(title, fontsize=12, fontweight="bold", pad=4)

    fig.suptitle("SMA 4-Arm Therapeutic Attack — DRAFT in silico leads",
                 fontsize=15, fontweight="bold", y=0.995)
    plt.savefig(out_path, dpi=150, facecolor="white", bbox_inches="tight")
    plt.close(fig)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    work = Path(tempfile.mkdtemp(prefix="simon_pack_"))
    pymol_pngs = {}

    # Arm 1
    print("[arm1] rendering LIMK2 alphaC activator...")
    p = str(work / "arm1_3d.png")
    render_kinase_activator("arm1", p)
    pymol_pngs["arm1"] = p

    # Arm 2
    print("[arm2] rendering ROCK2 alphaC activator...")
    p = str(work / "arm2_3d.png")
    render_kinase_activator("arm2", p)
    pymol_pngs["arm2"] = p

    # Arm 3
    print("[arm3] rendering PERP H2b_9_s2 binder...")
    p = str(work / "arm3_3d.png")
    render_perp_binder(p)
    pymol_pngs["arm3"] = p

    # Arm 4
    print("[arm4] rendering MDM2 V2 allosteric...")
    p = str(work / "arm4_3d.png")
    render_mdm2_v2(p)
    pymol_pngs["arm4"] = p

    # Compose final figures
    finals = {}
    for k in ["arm1", "arm2", "arm3", "arm4"]:
        out = OUT_DIR / ARMS[k]["out_file"]
        print(f"[{k}] composing -> {out}")
        compose_figure(k, pymol_pngs[k], str(out))
        finals[k] = str(out)

    # Composite
    composite = OUT_DIR / "fig_4arm_attack_composite.png"
    print(f"[composite] building -> {composite}")
    make_composite(finals, str(composite))

    print("\nDONE. Outputs:")
    for k, v in finals.items():
        print(f"  {k}: {v}")
    print(f"  composite: {composite}")


if __name__ == "__main__":
    main()

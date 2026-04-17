#!/usr/bin/env python3
"""Render Fasudil two-layer decision figure as a PNG."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

OUT = "/home/bryza/sma-research/qms/PERP_dossier"
os.makedirs(OUT, exist_ok=True)

fig, ax = plt.subplots(figsize=(13, 9))
ax.set_xlim(0, 13)
ax.set_ylim(0, 9)
ax.axis("off")

def box(x, y, w, h, text, fc="#e8f0ff", ec="#1f4e79", fs=10, bold=False):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle="round,pad=0.08",
                       linewidth=1.5, facecolor=fc, edgecolor=ec)
    ax.add_patch(p)
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fs,
            fontweight=("bold" if bold else "normal"), wrap=True)

def arrow(x1, y1, x2, y2, color="#1f4e79", lw=1.4, style="-|>"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
                                 arrowstyle=style, color=color,
                                 mutation_scale=14, linewidth=lw))

# Title
ax.text(6.5, 8.55, "Fasudil in SMA — two-compartment decision",
        ha="center", fontsize=14, fontweight="bold")
ax.text(6.5, 8.15, "Same drug, opposite direction-of-change effect depending on which tissue dominates pathology",
        ha="center", fontsize=10, style="italic", color="#444")

# Top: shared fact
box(3.5, 7.15, 6, 0.7,
    "Fasudil = pan-ROCK1/2 inhibitor  (Hoffmann-La Roche HA-1077, clinical vasospasm drug in Japan)",
    fc="#fff6e6", ec="#a66b00", fs=10, bold=True)

# --- Left column: MOTOR NEURON layer ---
box(0.3, 6.0, 5.8, 0.7, "MOTOR-NEURON LAYER  (iPSC Hb9-iMN, iN, hiPSC-MN)",
    fc="#fde4e4", ec="#8b1a1a", fs=11, bold=True)

box(0.3, 4.85, 5.8, 1.0,
    "Meta-analysis (3 datasets, 5 contrasts):\n"
    "ROCK2 pooled log2FC = -0.254\n"
    "95% CI [-0.381, -0.127], I² = 56%, p = 9.0e-5\n"
    "DOWN in all 5 contrasts",
    fc="#ffeaea", ec="#8b1a1a", fs=9)

box(0.3, 3.7, 5.8, 0.9,
    "+ Fasudil (pan-ROCK inhibitor)  further suppresses an already DOWN pathway",
    fc="#ffd6d6", ec="#8b1a1a", fs=9)

box(0.3, 2.55, 5.8, 0.9,
    "Result: WORSENS ROCK2 loss-of-function in MN compartment.\n"
    "MN-intrinsic rationale is not supported by transcriptomic evidence.",
    fc="#f5b3b3", ec="#8b1a1a", fs=9, bold=True)

box(0.3, 1.05, 5.8, 1.25,
    "RESCUE INDICATION (MN layer):\n"
    "ROCK2-αC ACTIVATOR  (first-in-class globally)\n"
    "Campaign: rock2_activator_alphaC  (PocketXMol, 4L6Q αC)\n"
    "Top hit: iptm 0.953, QED 0.72\n"
    "SMILES: ClC1CCCC2NC(CNC3CCN(c4cccnc4)C3)NCC12",
    fc="#d4e5ff", ec="#0b3d91", fs=9, bold=True)

# --- Right column: MUSCLE layer ---
box(6.9, 6.0, 5.8, 0.7, "MUSCLE LAYER  (Bowerman 2012, Smn2B/- mouse limb + diaphragm)",
    fc="#e1f5e1", ec="#1a6b1a", fs=11, bold=True)

box(6.9, 4.85, 5.8, 1.0,
    "Bowerman et al. 2012 (PMID 22383888):\n"
    "ROCK activity ELEVATED in Smn2B/- skeletal muscle.\n"
    "MN-intrinsic ROCK unchanged in their model.",
    fc="#ddf2dd", ec="#1a6b1a", fs=9)

box(6.9, 3.7, 5.8, 0.9,
    "+ Fasudil (pan-ROCK inhibitor)  normalises over-active ROCK in muscle",
    fc="#c8ebc8", ec="#1a6b1a", fs=9)

box(6.9, 2.55, 5.8, 0.9,
    "Result: EXTENDS LIFESPAN in Smn2B/- mouse (muscle-mediated rescue).\n"
    "Preclinical SMA survival data exists and is consistent.",
    fc="#a8dea8", ec="#1a6b1a", fs=9, bold=True)

box(6.9, 1.05, 5.8, 1.25,
    "VIABLE INDICATION (muscle layer):\n"
    "Fasudil REPURPOSING stays on the table\n"
    "(as muscle-directed adjunct, not MN-rescue)\n"
    "Pair with Apitegromab (SAPPHIRE +1.8 HFMSE,\n"
    "SMA 2025 congress, muscle-first modality).",
    fc="#fff0b3", ec="#a66b00", fs=9, bold=True)

# Arrows down each column
arrow(3.2, 7.14, 3.2, 5.87)   # shared-fact -> MN row
arrow(9.8, 7.14, 9.8, 5.87)   # shared-fact -> muscle row
arrow(3.2, 4.83, 3.2, 4.62)
arrow(3.2, 3.68, 3.2, 3.48)
arrow(3.2, 2.53, 3.2, 2.32)
arrow(9.8, 4.83, 9.8, 4.62)
arrow(9.8, 3.68, 9.8, 3.48)
arrow(9.8, 2.53, 9.8, 2.32)

# Decision footer
box(1.5, 0.1, 10, 0.75,
    "DECISION RULE:  whichever compartment dominates a given patient's SMA phenotype determines therapy direction.\n"
    "Current meta-analysis evidence at MN-transcript level does NOT support a pan-ROCK inhibitor as MN-intrinsic rescue.",
    fc="#f4f4f4", ec="#333", fs=9, bold=True)

plt.savefig(os.path.join(OUT, "fasudil_two_layer_diagram.png"),
            dpi=150, bbox_inches="tight")
print("Wrote", os.path.join(OUT, "fasudil_two_layer_diagram.png"))

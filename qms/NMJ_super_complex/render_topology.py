#!/usr/bin/env python3
"""
Render simple topology diagram + interaction heatmap for the NMJ
super-complex (in lieu of ChimeraX rendering, since CX is not on this
host).
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib import colormaps

ROOT = Path("/home/bryza/sma-research/qms/NMJ_super_complex")
METRICS = json.loads((ROOT / "validation" / "interface_metrics.json").read_text())
CHAIN_MAP = json.loads((ROOT / "assembly" / "chain_map.json").read_text())

CHAIN_COLOR = {
    "A": "#daa520", "C": "#daa520",      # α1 x 2 (goldenrod)
    "B": "#ff6347",                      # β1 (tomato)
    "D": "#40e0d0",                      # δ (turquoise)
    "E": "#ee82ee",                      # ε (violet)
    "F": "#fa8072",                      # RAPSN (salmon)
    "G": "#2e8b57",                      # MuSK ECD (seagreen)
    "H": "#228b22",                      # MuSK IC (forest)
    "I": "#90ee90",                      # DOK7 (lightgreen)
    "J": "#4682b4",                      # LRP4 (steelblue)
    "K": "#00bfff",                      # AGRIN (deepskyblue)
    "P": "#da70d6",                      # PERP (orchid)
    "Z": "#ff00ff",                      # binder (magenta)
}

# -------- Figure 1: topology schematic --------
fig, ax = plt.subplots(figsize=(14, 9))

# Positions (x, y) for each protein label
positions = {
    "K": (-6, 8, "AGRIN (LG3)"),
    "J": (-3, 7, "LRP4 (ECD)"),
    "G": (4, 6, "MuSK ECD"),
    "H": (4, 3, "MuSK kinase"),
    "I": (6, 2.5, "DOK7"),
    "A": (0, 4, "AChR α1"),
    "B": (1, 4, "AChR β1"),
    "C": (0, 3, "AChR α1"),
    "D": (-1, 4, "AChR δ"),
    "E": (1, 3, "AChR ε"),
    "F": (0, 0, "RAPSN"),
    "P": (-4, 3, "PERP"),
    "Z": (-5, 3.3, "H2b_9_s2"),
}

# Draw membrane as a horizontal band
ax.axhspan(2.0, 4.0, color="#eee2c6", alpha=0.5, zorder=0, label="Membrane")
ax.text(8.5, 3.0, "muscle\nmembrane", fontsize=8, color="#886633",
        ha="left", va="center")

# Draw chain nodes
for cid, (x, y, label) in positions.items():
    c = CHAIN_COLOR.get(cid, "#888")
    box = FancyBboxPatch(
        (x - 0.6, y - 0.3), 1.2, 0.6,
        boxstyle="round,pad=0.1", linewidth=1.2,
        facecolor=c, edgecolor="black", alpha=0.9, zorder=2,
    )
    ax.add_patch(box)
    ax.text(x, y, label, ha="center", va="center", fontsize=8,
            fontweight="bold", zorder=3)

# Arrows for significant interactions (from interface metrics)
ca_pairs = METRICS["interchain_ca_contacts"]
for pair, info in ca_pairs.items():
    c1, c2 = pair.split("-")
    if c1 not in positions or c2 not in positions:
        continue
    n = info["ca_pairs_within_8A"]
    if n < 20:
        continue
    x1, y1, _ = positions[c1]
    x2, y2, _ = positions[c2]
    lw = min(6, 0.5 + n / 100)
    alpha = min(0.9, 0.3 + n / 1000)
    ax.plot([x1, x2], [y1, y2], "-", color="black", alpha=alpha, lw=lw, zorder=1)

# Label significant signalling arrow
ax.annotate("", xy=(4, 5.5), xytext=(-2, 7), zorder=4,
            arrowprops=dict(arrowstyle="-|>", color="red", lw=2, linestyle="dashed"))
ax.text(1, 7.2, "activation\nAGRIN→LRP4→MuSK", color="red", fontsize=9, ha="center")

ax.annotate("", xy=(0.5, 2.0), xytext=(4, 3.0), zorder=4,
            arrowprops=dict(arrowstyle="-|>", color="blue", lw=2, linestyle="dashed"))
ax.text(2, 1.6, "clustering\nMuSK→rapsyn→AChR", color="blue", fontsize=9, ha="center")

ax.set_xlim(-7, 9)
ax.set_ylim(-2, 10)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title(
    "NMJ Post-synaptic Signalling Super-Complex\n"
    "13 chains, 8463 residues, 65228 atoms – assembled from ColabFold + AlphaFold DB\n"
    "+ 3V64/7SMQ/2IEP crystal templates",
    fontsize=11
)

plt.tight_layout()
out_fig1 = ROOT / "figures" / "nmj_topology.png"
out_fig1.parent.mkdir(exist_ok=True)
plt.savefig(out_fig1, dpi=150, bbox_inches="tight")
plt.close()
print(f"Wrote {out_fig1}")

# -------- Figure 2: interface contact heatmap --------
chain_order = ["K", "J", "G", "H", "I", "A", "B", "C", "D", "E", "F", "P", "Z"]
chain_labels = {
    "K": "AGRIN",
    "J": "LRP4",
    "G": "MuSK-ECD",
    "H": "MuSK-IC",
    "I": "DOK7",
    "A": "AChRα1(1)",
    "B": "AChRβ1",
    "C": "AChRα1(2)",
    "D": "AChRδ",
    "E": "AChRε",
    "F": "RAPSN",
    "P": "PERP",
    "Z": "binder",
}
n = len(chain_order)
mat = np.zeros((n, n))
for pair, info in ca_pairs.items():
    c1, c2 = pair.split("-")
    if c1 in chain_order and c2 in chain_order:
        i, j = chain_order.index(c1), chain_order.index(c2)
        mat[i, j] = info["ca_pairs_within_8A"]
        mat[j, i] = info["ca_pairs_within_8A"]

fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(mat, cmap="YlOrRd", aspect="auto")
ax.set_xticks(range(n))
ax.set_yticks(range(n))
ax.set_xticklabels([chain_labels[c] for c in chain_order], rotation=45, ha="right")
ax.set_yticklabels([chain_labels[c] for c in chain_order])
for i in range(n):
    for j in range(n):
        if mat[i, j] > 0:
            ax.text(j, i, f"{int(mat[i, j])}", ha="center", va="center",
                    fontsize=7, color="black" if mat[i, j] < 500 else "white")
ax.set_title("Inter-chain CA atom pairs within 8 Å (super-complex)")
plt.colorbar(im, ax=ax, label="# CA pairs < 8 Å")
plt.tight_layout()
out_fig2 = ROOT / "figures" / "nmj_contact_heatmap.png"
plt.savefig(out_fig2, dpi=150, bbox_inches="tight")
plt.close()
print(f"Wrote {out_fig2}")

# -------- Figure 3: per-chain pLDDT bar chart --------
plddt = METRICS["plddt_summary_per_chain"]
chains_x = chain_order
means = [plddt.get(c, {}).get("mean_bfactor", 0) for c in chains_x]
colors = [CHAIN_COLOR.get(c, "#888") for c in chains_x]
fig, ax = plt.subplots(figsize=(11, 5))
bars = ax.bar(range(len(chains_x)), means, color=colors, edgecolor="black")
for i, (m, c) in enumerate(zip(means, chains_x)):
    ax.text(i, m + 1, f"{m:.1f}", ha="center", fontsize=8)
ax.axhline(70, color="orange", linestyle="--", lw=1, label="Confident (70)")
ax.axhline(90, color="green", linestyle="--", lw=1, label="Very high (90)")
ax.set_xticks(range(len(chains_x)))
ax.set_xticklabels([f"{c}\n{chain_labels[c]}" for c in chains_x], fontsize=9)
ax.set_ylabel("mean pLDDT (per chain)")
ax.set_title("Per-chain pLDDT (AF-DB B-factor field)")
ax.set_ylim(0, 100)
ax.legend(loc="upper right")
plt.tight_layout()
out_fig3 = ROOT / "figures" / "nmj_plddt_per_chain.png"
plt.savefig(out_fig3, dpi=150, bbox_inches="tight")
plt.close()
print(f"Wrote {out_fig3}")

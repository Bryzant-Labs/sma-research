#!/usr/bin/env python3
"""Plot Bliss matrix heatmap + dose-response-like bar chart for 15 pairs.

Dose-response-style plots are intentionally degenerate (MCP gives only 1 dose point);
we therefore plot single-drug effects and the observed vs expected combination
effect as a single-point bar plot per pair, so the "no dose axis" constraint
is visually obvious.

Author: Opus Master Agent
Date:   2026-04-17
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path("/home/bryza/sma-research/qms/synergy_bliss")
DATA = json.loads((OUT / "bliss_data.json").read_text())

DRUGS = list(DATA["single_drug_effects"].keys())
N = len(DRUGS)


def heatmap():
    M = np.full((N, N), np.nan)
    for r in DATA["pairs"]:
        i = DRUGS.index(r["drug_A"])
        j = DRUGS.index(r["drug_B"])
        M[i, j] = r["bliss_index"]
        M[j, i] = r["bliss_index"]
    # Diagonal: single-drug fractional rescue (not a Bliss index)
    for i, d in enumerate(DRUGS):
        M[i, i] = np.nan

    fig, ax = plt.subplots(figsize=(9, 7))
    vmax = max(0.2, abs(np.nanmax(M)), abs(np.nanmin(M)))
    im = ax.imshow(M, cmap="RdBu_r", vmin=-vmax, vmax=+vmax)
    ax.set_xticks(range(N))
    ax.set_yticks(range(N))
    ax.set_xticklabels(DRUGS, rotation=45, ha="right")
    ax.set_yticklabels(DRUGS)

    # Cell annotations
    for i in range(N):
        for j in range(N):
            if np.isnan(M[i, j]):
                ax.text(j, i, "-", ha="center", va="center", color="gray")
            else:
                ax.text(j, i, f"{M[i, j]:+.3f}", ha="center", va="center",
                        color="white" if abs(M[i, j]) > vmax * 0.5 else "black", fontsize=9)

    # Annotate classification zones in colorbar label
    ax.set_title("Bliss Independence Index — SMA Digital Twin\n"
                 "(Observed − Expected fractional rescue; >+0.1 syn., <−0.1 antag., else additive)",
                 fontsize=11)
    cbar = plt.colorbar(im, ax=ax, label="Bliss index (Δ rescue)")
    cbar.ax.axhline(+0.1, color="green", linewidth=1)
    cbar.ax.axhline(-0.1, color="red", linewidth=1)

    # Footer note
    plt.figtext(0.5, 0.01,
                "Single implicit dose (MCP has no dose axis). All 15 pairs classify as ADDITIVE (|Bliss| ≤ 0.1).",
                ha="center", fontsize=9, style="italic", color="dimgray")
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    out_path = OUT / "bliss_matrix.png"
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Wrote {out_path}")


def dose_response():
    """Bar-plot: per-pair E_A, E_B, E_expected (Bliss), E_observed.

    Since the MCP has NO dose axis, this is NOT a classical dose-response curve.
    We instead plot the 4 canonical points per pair as grouped bars, clearly
    labelled 'single dose'.
    """
    rows = DATA["pairs"]
    n = len(rows)
    fig, ax = plt.subplots(figsize=(13, 8))
    x = np.arange(n)
    w = 0.2

    E_A   = [r["E_A"] for r in rows]
    E_B   = [r["E_B"] for r in rows]
    E_exp = [r["E_expected_bliss"] for r in rows]
    E_obs = [r["E_observed"] for r in rows]

    ax.bar(x - 1.5*w, E_A,   width=w, label="E(A) single",    color="#4C72B0")
    ax.bar(x - 0.5*w, E_B,   width=w, label="E(B) single",    color="#55A868")
    ax.bar(x + 0.5*w, E_exp, width=w, label="E_expected (Bliss)", color="#8172B2", hatch="//")
    ax.bar(x + 1.5*w, E_obs, width=w, label="E_observed (combo)", color="#C44E52")

    labels = [f"{r['drug_A']}\n+\n{r['drug_B']}" for r in rows]
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=0, ha="center", fontsize=7)
    ax.set_ylabel("Fractional rescue E = (fs − baseline) / (1 − baseline)")
    ax.set_title("Per-pair single vs combined effect — SMA Digital Twin\n"
                 "(MCP has no dose axis: single 'efficacious' dose only)",
                 fontsize=11)
    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_ylim(0, max(max(E_obs), max(E_exp)) * 1.2 + 0.05)
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    # Annotate Bliss index on top of each observed bar
    for xi, r in zip(x, rows):
        ax.text(xi + 1.5*w, r["E_observed"] + 0.01,
                f"Bliss\n{r['bliss_index']:+.3f}\n({r['class'][:4]})",
                ha="center", va="bottom", fontsize=6,
                color="green" if r["class"] == "SYNERGISTIC"
                else "red"   if r["class"] == "ANTAGONISTIC"
                else "gray")

    plt.figtext(0.5, 0.005,
                "Dose-response curves not achievable — MCP digital twin accepts only drug names, no concentration axis. "
                "All values are at the MCP's implicit single-dose setpoint.",
                ha="center", fontsize=8, style="italic", color="dimgray")
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    out_path = OUT / "dose_response_curves.png"
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    heatmap()
    dose_response()

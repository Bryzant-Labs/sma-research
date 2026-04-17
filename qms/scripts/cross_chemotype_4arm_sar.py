#!/usr/bin/env python3
"""Cross-chemotype SAR for the 4-arm SMA attack:
   LIMK2-aC activator  x  ROCK2-aC activator  x  PERP ECL binder  x  MDM2 activator.

Output:
  /home/bryza/sma-research/qms/scripts/out/cross_chemotype_top20.csv
  /home/bryza/sma-research/qms/scripts/out/tanimoto_heatmap_80x80.png
  /home/bryza/sma-research/qms/scripts/out/murcko_cluster_per_arm.csv
  /home/bryza/sma-research/qms/scripts/out/cross_arm_off_diagonal_stats.txt

Note: PERP binders are PEPTIDES/mini-proteins, not small molecules. For completeness we
include their sequences but exclude them from the small-molecule Tanimoto comparison.
Cross-arm distinctness is therefore assessed among the 3 small-molecule arms (LIMK2 / ROCK2 / MDM2),
and PERP is treated as a structurally orthogonal modality by construction.
"""
import csv, sys, os
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from rdkit import Chem
from rdkit.Chem import AllChem, DataStructs
from rdkit.Chem.Scaffolds import MurckoScaffold

OUT = "/home/bryza/sma-research/qms/scripts/out"
os.makedirs(OUT, exist_ok=True)

# ---------- 1. Load top-20 per arm ----------

def load_limk2_top20():
    path = "/home/bryza/fleet-results/limk2_activator_alphaC/top_hits.tsv"
    # Only 4 panel-complete hits exist; we extend with the highest-C_rel DiffDock BBB hits
    # to reach n=20 so SAR has signal. Documented as "panel-complete + C_rel>0 pool".
    rows = []
    with open(path) as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            rows.append({
                "arm": "LIMK2",
                "smiles": row["smiles"],
                "rank_primary": int(row["rank"]),
                "primary_metric": row["selectivity_z"],
                "primary_label": "sel_z",
            })
    # Pad with DiffDock C_rel>0 BBB compounds if panel-complete < 20
    if len(rows) < 20:
        dd_path = "/home/bryza/fleet-results/limk2_activator_alphaC/diffdock_results.csv"
        with open(dd_path) as f:
            dd = list(csv.DictReader(f))
        # we'll filter to BBB pass + C_rel>0, sort by C_rel
        bbb_path = "/home/bryza/fleet-results/limk2_activator_alphaC/bbb_filtered.csv"
        bbb_set = set()
        with open(bbb_path) as f:
            for row in csv.DictReader(f):
                bbb_set.add(row["smiles"])
        extras = []
        for row in dd:
            try:
                cr = float(row.get("C_rel", "nan"))
            except Exception:
                continue
            smi_val = row.get("canonical_smiles") or row.get("smiles")
            if smi_val and smi_val in bbb_set and cr > 0:
                extras.append((cr, smi_val))
        extras.sort(reverse=True)
        have = {r["smiles"] for r in rows}
        for cr, smi in extras:
            if smi in have:
                continue
            rows.append({
                "arm": "LIMK2",
                "smiles": smi,
                "rank_primary": len(rows) + 1,
                "primary_metric": f"{cr:.3f}",
                "primary_label": "C_rel",
            })
            if len(rows) >= 20:
                break
    return rows[:20]

def load_rock2_top20():
    path = "/home/bryza/fleet-results/rock2_activator_alphaC/boltz2_rescore_ranked.tsv"
    out = []
    with open(path) as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            out.append({
                "arm": "ROCK2",
                "smiles": row["smiles"],
                "rank_primary": int(row["final_rank"]),
                "primary_metric": row["iptm"],
                "primary_label": "iptm",
            })
            if len(out) >= 20:
                break
    return out

def load_mdm2_top20():
    path = "/home/bryza/fleet-results/mdm2_activator/mols_filtered.csv"
    rows = []
    with open(path) as f:
        for row in csv.DictReader(f):
            if row.get("bbb") == "1" and row.get("ro5") == "1":
                rows.append(row)
    rows.sort(key=lambda r: float(r.get("qed", 0) or 0), reverse=True)
    out = []
    for i, row in enumerate(rows[:20]):
        out.append({
            "arm": "MDM2",
            "smiles": row["smiles"],
            "rank_primary": i + 1,
            "primary_metric": row["qed"],
            "primary_label": "QED",
        })
    return out

def load_perp_top20():
    """PERP binders are mini-protein SEQUENCES, not small molecules.
       Included for completeness / manifest only.
    """
    out = []
    for path, ecl in [
        ("/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/top_binders_ecl1.tsv", "ECL1"),
        ("/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders/top_binders_ecl2.tsv", "ECL2"),
    ]:
        with open(path) as f:
            r = csv.DictReader(f, delimiter="\t")
            for i, row in enumerate(r):
                if i >= 10:
                    break
                out.append({
                    "arm": "PERP",
                    "smiles": f"PEPTIDE::{ecl}::{row['design_id']}",  # placeholder token
                    "sequence": row["sequence"],
                    "rank_primary": int(row["rank"]),
                    "primary_metric": row["delta_iptm"],
                    "primary_label": "delta_iptm",
                    "ecl": ecl,
                })
    return out

# ---------- 2. Build master table ----------

limk2 = load_limk2_top20()
rock2 = load_rock2_top20()
mdm2  = load_mdm2_top20()
perp  = load_perp_top20()

all_rows = limk2 + rock2 + mdm2 + perp

with open(os.path.join(OUT, "cross_chemotype_top20.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["arm", "rank_primary", "primary_label", "primary_metric", "smiles_or_seq"])
    for r in all_rows:
        w.writerow([r["arm"], r["rank_primary"], r["primary_label"], r["primary_metric"],
                    r.get("sequence") or r["smiles"]])

# ---------- 3. Small-molecule ECFP4 Tanimoto matrix (LIMK2 + ROCK2 + MDM2 = 60 rows) ----------

sm = limk2 + rock2 + mdm2
mols = []
labels = []
arms = []
for r in sm:
    m = Chem.MolFromSmiles(r["smiles"])
    if m is None:
        # Try neutralizing charges
        m = Chem.MolFromSmiles(r["smiles"], sanitize=False)
        try:
            Chem.SanitizeMol(m, sanitizeOps=Chem.SanitizeFlags.SANITIZE_ALL ^ Chem.SanitizeFlags.SANITIZE_KEKULIZE)
        except Exception:
            m = None
    if m is None:
        print(f"[WARN] failed to parse {r['arm']} r{r['rank_primary']}: {r['smiles'][:60]}", file=sys.stderr)
        continue
    mols.append(m)
    labels.append(f"{r['arm']}#{r['rank_primary']}")
    arms.append(r["arm"])

fps = [AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=2048) for m in mols]
N = len(fps)
T = np.zeros((N, N), dtype=float)
for i in range(N):
    T[i, i] = 1.0
    for j in range(i + 1, N):
        s = DataStructs.TanimotoSimilarity(fps[i], fps[j])
        T[i, j] = s
        T[j, i] = s

# ---------- 4. Murcko scaffold clustering per arm ----------

scaffolds = defaultdict(lambda: defaultdict(int))  # arm -> scaffold_smiles -> count
arm_scaffold_rows = []
for r, m in zip([row for row in sm if Chem.MolFromSmiles(row["smiles"]) is not None], mols):
    # r iteration above is brittle; rebuild carefully
    pass

# Rebuild cleanly:
scaffolds = defaultdict(lambda: defaultdict(int))
scaffold_rows = []
for r in sm:
    m = Chem.MolFromSmiles(r["smiles"])
    if m is None:
        continue
    try:
        scaf = MurckoScaffold.GetScaffoldForMol(m)
        scaf_smi = Chem.MolToSmiles(scaf) if scaf is not None else "<none>"
    except Exception:
        scaf_smi = "<error>"
    if not scaf_smi:
        scaf_smi = "<acyclic>"
    scaffolds[r["arm"]][scaf_smi] += 1
    scaffold_rows.append((r["arm"], r["rank_primary"], r["smiles"], scaf_smi))

with open(os.path.join(OUT, "murcko_cluster_per_arm.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["arm", "rank", "smiles", "murcko_scaffold"])
    for row in scaffold_rows:
        w.writerow(row)

# ---------- 5. Off-diagonal stats ----------

def block_stats(T, arms, a, b):
    ia = [i for i, x in enumerate(arms) if x == a]
    ib = [i for i, x in enumerate(arms) if x == b]
    vals = []
    for i in ia:
        for j in ib:
            if i == j:
                continue
            vals.append(T[i, j])
    vals = np.array(vals)
    return {
        "n_pairs": len(vals),
        "mean": float(vals.mean()),
        "median": float(np.median(vals)),
        "max": float(vals.max()),
        "p95": float(np.percentile(vals, 95)),
        "frac_ge_0.4": float((vals >= 0.4).mean()),
        "frac_ge_0.6": float((vals >= 0.6).mean()),
    }

pairs = [("LIMK2", "LIMK2"), ("ROCK2", "ROCK2"), ("MDM2", "MDM2"),
         ("LIMK2", "ROCK2"), ("LIMK2", "MDM2"), ("ROCK2", "MDM2")]

stats_lines = []
stats_lines.append(f"# Small-molecule Tanimoto (ECFP4 2048) stats across top-20 per arm")
stats_lines.append(f"# Rows parsed: LIMK2={sum(1 for a in arms if a=='LIMK2')}, "
                   f"ROCK2={sum(1 for a in arms if a=='ROCK2')}, "
                   f"MDM2={sum(1 for a in arms if a=='MDM2')}")
stats_lines.append("")
stats_lines.append(f"{'pair':<14} {'n_pairs':>8} {'mean':>8} {'median':>8} {'max':>8} {'p95':>8} {'>=0.4':>8} {'>=0.6':>8}")
for a, b in pairs:
    s = block_stats(T, arms, a, b)
    stats_lines.append(f"{a+'-'+b:<14} {s['n_pairs']:>8d} {s['mean']:>8.3f} {s['median']:>8.3f} "
                       f"{s['max']:>8.3f} {s['p95']:>8.3f} {s['frac_ge_0.4']:>8.1%} {s['frac_ge_0.6']:>8.1%}")

stats_lines.append("")
stats_lines.append("# Unique Murcko scaffolds per arm")
for arm in ["LIMK2", "ROCK2", "MDM2"]:
    n_unique = len(scaffolds[arm])
    n_total  = sum(scaffolds[arm].values())
    singletons = sum(1 for v in scaffolds[arm].values() if v == 1)
    stats_lines.append(f"  {arm}: {n_unique} unique / {n_total} compounds ({singletons} singletons)")

with open(os.path.join(OUT, "cross_arm_off_diagonal_stats.txt"), "w") as f:
    f.write("\n".join(stats_lines))

print("\n".join(stats_lines))

# ---------- 6. Heatmap ----------

fig, ax = plt.subplots(figsize=(11, 10))
# Reorder so arms are grouped and we can see block structure
order = sorted(range(N), key=lambda i: (arms[i], labels[i]))
T_ord = T[np.ix_(order, order)]
labels_ord = [labels[i] for i in order]
arms_ord = [arms[i] for i in order]

im = ax.imshow(T_ord, cmap="viridis", vmin=0, vmax=1, aspect="auto")
ax.set_xticks(range(N))
ax.set_yticks(range(N))
ax.set_xticklabels(labels_ord, rotation=90, fontsize=6)
ax.set_yticklabels(labels_ord, fontsize=6)
plt.colorbar(im, ax=ax, label="Tanimoto similarity (ECFP4 2048-bit)")

# Block boundaries
counts = {a: sum(1 for x in arms_ord if x == a) for a in ["LIMK2", "ROCK2", "MDM2"]}
c = 0
for a in ["LIMK2", "ROCK2", "MDM2"]:
    c += counts[a]
    if c < N:
        ax.axhline(c - 0.5, color="white", lw=0.8)
        ax.axvline(c - 0.5, color="white", lw=0.8)

ax.set_title("Cross-chemotype Tanimoto matrix — LIMK2 / ROCK2 / MDM2 top-20\n"
             "(PERP binders are mini-proteins → excluded from ECFP4 space)")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "tanimoto_heatmap_80x80.png"), dpi=140)
print(f"\nHeatmap written to {os.path.join(OUT, 'tanimoto_heatmap_80x80.png')}")

# Dump matrix too
np.save(os.path.join(OUT, "tanimoto_matrix.npy"), T_ord)
with open(os.path.join(OUT, "tanimoto_matrix_labels.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["idx", "arm", "label"])
    for i, (a, l) in enumerate(zip(arms_ord, labels_ord)):
        w.writerow([i, a, l])

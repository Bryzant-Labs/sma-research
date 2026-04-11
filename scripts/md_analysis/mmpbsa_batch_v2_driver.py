#!/usr/bin/env python3
"""
mmpbsa_batch_v2_driver.py — Drives the patched mmpbsa_batch.py over the 6
valid SMA MD trajectories for the Simon hand-off package (2026-04-11).

Wraps the patched run_contact_proxy + run_ambertools_mmpbsa with a small
COMPOUNDS list that points to the actual filesystem layout (no double-nesting,
ROCK2 has traj_20ns.dcd not trajectory.dcd, POCKET_FIXED dirs lack initial_complex).

Output: ~/gpu-fleet/results/SMA/drug_discovery/mmpbsa/batch_2026-04-11_v2/
        {system}/mmpbsa_result.json + work/

Both Tier 1 (PBC-correct contact proxy) and Tier 2 (atom-order-fixed
AmberTools MMPBSA.py with GAFF2 ligand + OpenMM-built receptor prmtop) are run
on every system.
"""
from __future__ import annotations

import json
import os
import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

# Capture the original CLI args BEFORE we replace sys.argv for mmpbsa_batch
_orig_argv = list(sys.argv)
_only_id_arg = None
for a in _orig_argv[1:]:
    if not a.startswith("-"):
        _only_id_arg = a
        break

# Inject CLI args BEFORE importing mmpbsa_batch (which parses argv at import)
RESULTS_BASE = Path(os.path.expanduser("~/gpu-fleet/results/SMA/md_sims"))
OUT_V2 = Path(os.path.expanduser(
    "~/gpu-fleet/results/SMA/drug_discovery/mmpbsa/batch_2026-04-11_v2"
))
OUT_V2.mkdir(parents=True, exist_ok=True)

sys.argv = [
    "mmpbsa_batch_v2_driver.py",
    "--ambertools",
    "--results_base", str(RESULTS_BASE),
    "--outdir", str(OUT_V2),
    "--force",
]

# Now import the module — it'll parse args, set up logging in OUT_V2
sys.path.insert(0, str(Path(__file__).parent))
import mmpbsa_batch  # noqa: E402

# Override RESULTS_BASE in the imported module (in case it captured an old one)
mmpbsa_batch.RESULTS_BASE = RESULTS_BASE
mmpbsa_batch.OUTDIR = OUT_V2

# ── 6 Valid trajectories ─────────────────────────────────────────────────────

COMPOUNDS_V2 = [
    {
        "id":         "LIMK2_BMS5_holo",
        "compound":   "BMS-5",
        "target":     "LIMK2",
        "pdb_id":     "4TPT",
        "smiles":     "COc1cc2c(Nc3ccc(F)c(F)c3)ncnc2cc1OCCCN1CCOCC1",
        "ns":         20,
        "role":       "reference_binder",
        "group":      "reference",
        "dir_name":   "LIMK2_BMS5_holo",
        "inner_dir":  "",
        "has_pdb":    True,
        "notes":      "Known LIMK inhibitor benchmark, 20 ns holo MD.",
    },
    {
        "id":         "LIMK2_LIMKi3_holo",
        "compound":   "LIMKi3",
        "target":     "LIMK2",
        "pdb_id":     "4TPT",
        "smiles":     "CC(C)Nc1ncnc(-c2ccc3[nH]ccc3c2)c1C#N",
        "ns":         20,
        "role":       "reference_binder",
        "group":      "reference",
        "dir_name":   "LIMK2_LIMKi3_holo",
        "inner_dir":  "",
        "has_pdb":    True,
        "notes":      "LIMKi3 reference (DILI 0.95 — comparator only).",
    },
    {
        "id":         "LIMK2_bbb5_holo",
        "compound":   "bbb5",
        "target":     "LIMK2",
        "pdb_id":     "4TPT",
        "smiles":     "CC(C)C(=O)N1CC[C@@H](NCC(F)(F)F)[C@H](c2ccncc2)C1",
        "ns":         20,
        "role":       "primary_target",
        "group":      "bbb5_selectivity",
        "dir_name":   "LIMK2_bbb5_holo",
        "inner_dir":  "",
        "has_pdb":    True,
        "notes":      "Primary LIMK2 target, 20 ns holo MD.",
    },
    {
        "id":         "LIMK2_BMS5_POCKET_FIXED",
        "compound":   "BMS-5",
        "target":     "LIMK2",
        "pdb_id":     "4TPT",
        "smiles":     "COc1cc2c(Nc3ccc(F)c(F)c3)ncnc2cc1OCCCN1CCOCC1",
        "ns":         20,
        "role":       "reference_binder",
        "group":      "reference",
        "dir_name":   "LIMK2_BMS5_POCKET_FIXED",
        "inner_dir":  "",
        "has_pdb":    False,
        "notes":      "BMS-5 with corrected pocket positioning, 20 ns.",
    },
    {
        "id":         "LIMK2_bbb5_POCKET_FIXED",
        "compound":   "bbb5",
        "target":     "LIMK2",
        "pdb_id":     "4TPT",
        "smiles":     "CC(C)C(=O)N1CC[C@@H](NCC(F)(F)F)[C@H](c2ccncc2)C1",
        "ns":         10,
        "role":       "primary_target",
        "group":      "bbb5_selectivity",
        "dir_name":   "LIMK2_bbb5_POCKET_FIXED",
        "inner_dir":  "",
        "has_pdb":    False,
        "notes":      "bbb5 with corrected ATP-pocket positioning, 10 ns.",
    },
    {
        "id":         "ROCK2_Fasudil_holo",
        "compound":   "Fasudil",
        "target":     "ROCK2",
        "pdb_id":     "2H9V",
        # Real Fasudil = 5-(1,4-Diazepane-1-sulfonyl)isoquinoline (homopiperazine
        # + isoquinoline). Earlier catalog entry had piperidine + cinnoline (wrong).
        "smiles":     "O=S(=O)(c1cccc2cnccc12)N1CCCNCC1",
        "ns":         20,
        "role":       "fasudil_baseline",
        "group":      "fasudil",
        "dir_name":   "ROCK2_Fasudil_holo",
        "inner_dir":  "",
        "has_pdb":    True,
        "notes":      "Fasudil + ROCK2, 20 ns. Track 1 baseline for Simon pack.",
    },
]


def main() -> None:
    log = mmpbsa_batch.log
    log("=" * 70)
    log(f"MMPBSA BATCH v2 DRIVER — 6 valid SMA trajectories")
    log(f"Output: {OUT_V2}")
    log("=" * 70)

    log("\n[STEP 1] Detecting tools...")
    tools = mmpbsa_batch.detect_tools()
    if not tools.get("ambertools_full"):
        log("[FAIL] AmberTools not fully present in active env")
        sys.exit(1)

    only_id = _only_id_arg
    valid_ids = {c["id"] for c in COMPOUNDS_V2}
    if only_id and only_id not in valid_ids:
        log(f"[WARNING] Unknown compound id: {only_id}. Valid: {sorted(valid_ids)}")
        only_id = None
    if only_id:
        compounds = [c for c in COMPOUNDS_V2 if c["id"] == only_id]
        log(f"  Single-compound mode: {only_id}")
    else:
        compounds = COMPOUNDS_V2

    log(f"\n[STEP 2] Processing {len(compounds)} compound(s)...")
    all_results = []
    for cfg in compounds:
        try:
            r = mmpbsa_batch.analyze_compound(cfg, tools)
            all_results.append(r)
        except Exception as e:
            import traceback
            log(f"[CRASH] {cfg['id']}: {e}")
            log(traceback.format_exc()[-2000:])
            all_results.append({
                "id": cfg["id"],
                "status": "CRASHED",
                "error": str(e),
                "compound": cfg["compound"],
                "target": cfg["target"],
                "group": cfg["group"],
                "role": cfg["role"],
                "ns": cfg["ns"],
                "notes": cfg["notes"],
            })

    consolidated = OUT_V2 / "all_mmpbsa_results.json"
    with open(consolidated, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    log(f"\n[OK] Consolidated: {consolidated}")

    # Summary table to log
    log("\n" + "=" * 70)
    log("BATCH v2 SUMMARY")
    log("=" * 70)
    for r in all_results:
        cid = r.get("id", "?")
        status = r.get("status", "?")
        amber = (r.get("ambertools_mmpbsa") or {}) if isinstance(r, dict) else {}
        proxy = (r.get("contact_proxy") or {}) if isinstance(r, dict) else {}
        amber_dG = amber.get("dG_bind_kcal_mol")
        amber_std = amber.get("dG_bind_std")
        proxy_dG = proxy.get("proxy_dG_kcal_mol")
        min_d = proxy.get("mean_min_dist_A")
        engaged = None
        if proxy.get("contacts_series_6A"):
            n_engaged = sum(1 for c in proxy["contacts_series_6A"] if c > 0)
            engaged = round(100 * n_engaged / len(proxy["contacts_series_6A"]))
        amber_str = (
            f"{amber_dG:+.2f}±{amber_std:.2f}"
            if amber_dG is not None and amber_std is not None
            else "N/A"
        )
        log(f"  {cid:35s} | status={status:8s} "
            f"| MMPBSA ΔG={amber_str:18s} "
            f"| min_d={min_d if min_d is not None else 'N/A'!s:7s} "
            f"| engaged={engaged}%")
    log("=" * 70)
    log(f"Done at {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()

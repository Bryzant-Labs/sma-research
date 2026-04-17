#!/usr/bin/env python3
"""Compute Bliss independence index for all 15 drug pairs against SMA digital twin.

Bliss Independence Model:
    E_A, E_B = effect of drug A or B alone (fraction, 0..1)
    E_AB_expected = E_A + E_B - (E_A * E_B)
    E_AB_observed = measured combination effect
    Bliss_index = E_AB_observed - E_AB_expected

Classification (per user spec):
    > +0.1  -> synergistic
    -0.1 to +0.1 -> additive
    < -0.1  -> antagonistic

Effect metric: "improvement_vs_baseline" from digital-twin JSON
(= functional_score - baseline_functional_score). Normalized to [0, 1]
by dividing by (1 - baseline_fs) so E in [0, 1] is the fraction of
maximal-possible rescue achieved.

Dose-response note: MCP digital twin accepts only drug NAMES (no dose axis).
We therefore cannot vary IC50 multiples. The "1x IC50" point is the only
point available. This is documented as a hard MCP constraint in the report.

Author: Opus Master Agent
Date:   2026-04-17
"""
import json
import math
from itertools import combinations
from pathlib import Path

RAW = Path("/home/bryza/sma-research/qms/synergy_bliss/raw")
OUT = Path("/home/bryza/sma-research/qms/synergy_bliss")

DRUGS = ["Nusinersen", "Risdiplam", "4-Aminopyridine", "Apitegromab", "NMN", "GV-58"]

# Map each MCP drug to its mechanism + nearest 4-arm counterpart (for synergy-matrix context)
DRUG_ARM_MAP = {
    "Nusinersen":      {"mechanism": "SMN2 splicing modulator (ASO)",      "arm_analog": "Arm 8 HDAC2-inh proxy (SMN2 upregulator)"},
    "Risdiplam":       {"mechanism": "SMN2 splicing modulator (small-mol)","arm_analog": "Arm 8 HDAC2-inh proxy (SMN2 upregulator)"},
    "4-Aminopyridine": {"mechanism": "Kv channel blocker (presyn NMJ)",    "arm_analog": "Arm 5 MuSK-adjacent (NMJ scaffold)"},
    "Apitegromab":     {"mechanism": "anti-myostatin (muscle-layer)",      "arm_analog": "Complementary (muscle, not MN)"},
    "NMN":             {"mechanism": "NAD+ precursor (mito bioenergetics)","arm_analog": "Complementary (mito, not 4-arm)"},
    "GV-58":           {"mechanism": "Cav2.1 agonist (presyn NMJ)",        "arm_analog": "Arm 5 MuSK-adjacent (NMJ)"},
}


def load(fn):
    return json.loads((RAW / fn).read_text())


def safe(drug):
    return drug.replace(" ", "_").replace("/", "_")


def effect_from_json(js, baseline_fs):
    """Fractional rescue in [0,1]: (fs - baseline) / (1 - baseline)."""
    fs = js.get("functional_score")
    if fs is None:
        return None
    denom = 1.0 - baseline_fs
    if denom <= 0:
        return 0.0
    return max(0.0, (fs - baseline_fs) / denom)


def main():
    # ---- Load singles ----
    singles = {}
    for d in DRUGS:
        fn = f"single_{safe(d)}.json"
        singles[d] = load(fn)

    baseline_fs = singles[DRUGS[0]]["baseline"]["functional_score"]
    print(f"Baseline functional_score: {baseline_fs}")

    single_effect = {d: effect_from_json(singles[d], baseline_fs) for d in DRUGS}
    print("\nSingle-drug fractional rescue (improvement / (1 - baseline)):")
    for d, e in single_effect.items():
        raw_fs = singles[d]["functional_score"]
        print(f"  {d:20s}  fs={raw_fs:.2f}  E={e:.3f}  ({DRUG_ARM_MAP[d]['mechanism']})")

    # ---- Load pairs + compute Bliss ----
    rows = []
    for a, b in combinations(DRUGS, 2):
        fn = f"pair_{safe(a)}_vs_{safe(b)}.json"
        js = load(fn)
        e_a = single_effect[a]
        e_b = single_effect[b]
        e_obs = effect_from_json(js, baseline_fs)
        e_exp = e_a + e_b - (e_a * e_b)
        bliss = e_obs - e_exp
        if bliss > 0.1:
            cls = "SYNERGISTIC"
        elif bliss < -0.1:
            cls = "ANTAGONISTIC"
        else:
            cls = "ADDITIVE"
        rows.append({
            "drug_A": a,
            "drug_B": b,
            "E_A": round(e_a, 4),
            "E_B": round(e_b, 4),
            "E_expected_bliss": round(e_exp, 4),
            "E_observed": round(e_obs, 4),
            "bliss_index": round(bliss, 4),
            "class": cls,
            "fs_A": singles[a]["functional_score"],
            "fs_B": singles[b]["functional_score"],
            "fs_AB": js["functional_score"],
            "mcp_synergy_type": js.get("synergy_type"),
            "mcp_synergy_score": js.get("synergy_score"),
            "arm_A": DRUG_ARM_MAP[a]["arm_analog"],
            "arm_B": DRUG_ARM_MAP[b]["arm_analog"],
            "mechanism_A": DRUG_ARM_MAP[a]["mechanism"],
            "mechanism_B": DRUG_ARM_MAP[b]["mechanism"],
        })

    # ---- Sort descending ----
    rows.sort(key=lambda r: r["bliss_index"], reverse=True)

    # ---- Print table ----
    print("\n\nBliss-index ranking (15 pairs):")
    print(f"{'Pair':<45} {'E_A':>6} {'E_B':>6} {'E_exp':>6} {'E_obs':>6} {'Bliss':>7} {'Class':<14}")
    print("-" * 105)
    for r in rows:
        pair = f"{r['drug_A']} + {r['drug_B']}"
        print(f"{pair:<45} {r['E_A']:>6.3f} {r['E_B']:>6.3f} {r['E_expected_bliss']:>6.3f} "
              f"{r['E_observed']:>6.3f} {r['bliss_index']:>+7.3f} {r['class']:<14}")

    # ---- Write bliss_data.json ----
    payload = {
        "method": "Bliss Independence (Bliss 1939); E = fractional rescue vs baseline",
        "baseline_functional_score": baseline_fs,
        "effect_metric": "improvement_vs_baseline / (1 - baseline)",
        "classification_thresholds": {
            "synergistic": "bliss > +0.1",
            "additive":    "-0.1 <= bliss <= +0.1",
            "antagonistic":"bliss < -0.1",
        },
        "dose_constraint": (
            "MCP digital twin accepts drug names only; no dose axis. "
            "All effects reported at single implicit 'efficacious' dose level "
            "as modelled by sma-research platform (/api/v2/twin/simulate). "
            "Multi-dose isobologram not achievable with current MCP schema."
        ),
        "single_drug_effects": {d: {"fs": singles[d]["functional_score"], "E": round(single_effect[d], 4)} for d in DRUGS},
        "pairs": rows,
        "note": "This is SIMULATION, not wet-lab. Digital twin is a phenomenological model calibrated to published SMA signatures; it is NOT a validated preclinical model. Do not interpret Bliss values as wet-lab-ready predictions.",
    }
    (OUT / "bliss_data.json").write_text(json.dumps(payload, indent=2))
    print(f"\nWrote {OUT / 'bliss_data.json'}")


if __name__ == "__main__":
    main()

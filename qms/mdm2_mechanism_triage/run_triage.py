"""MDM2 V1 vs V2 mechanistic triage via Boltz-2 co-folding.

For each top-20 V1 + top-20 V2 compound:
  co-fold MDM2(17-125) + TP53 peptide (17-26: ETFSDLWKLL) + compound
  delta_iptm = iptm_with_compound - baseline_iptm_no_compound

Classification:
  delta < -0.1  -> INHIBITOR arm (blocks p53 binding; WRONG direction for SMA)
  delta > +0.05 -> ACTIVATOR arm (allosteric; preserves site, candidate activator; RIGHT direction)
  in-between    -> AMBIGUOUS / weak effect

Uses Boltz-2 batched server at localhost:8004 (tunneled to remote GPU host).
Runs N_REPLICAS per condition to estimate noise.
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from statistics import mean, stdev

# ---------------- CONFIG ----------------
URL = os.environ.get("BOLTZ2_URL", "http://localhost:8004/predict")
N_REPLICAS = int(os.environ.get("N_REPLICAS", "3"))  # replicas per condition for noise
RECYCLING_STEPS = 1
SAMPLING_STEPS = 25
TIMEOUT_S = 900

OUT_DIR = Path("/home/bryza/sma-research/qms/mdm2_mechanism_triage")
RAW_DIR = OUT_DIR / "raw"
RAW_DIR.mkdir(exist_ok=True, parents=True)

# MDM2 p53-binding domain — UniProt Q00987 residues 17-125 (canonical MDM2 N-term)
# Verified from RCSB 4HG7 chain A FASTA (tag GPLGS stripped, starts at SQIPAS residue 17)
MDM2_17_125 = (
    "SQIPASEQETLVRPKPLLLKLLKSVGAQKDTYTMKEVLFYLGQYIMTKRLYDEKQQHIVYCSNDLLGDLFGVPSFSVKEHRKIYTMIYRNLVVVNQQESSDSGTSVSEN"
)
# TP53 canonical MDM2-binding peptide: residues 17-26 of UniProt P04637 = ETFSDLWKLL
# Minimum transactivation-domain helix that binds MDM2 cleft (Kussie et al., 1996 Science)
TP53_17_26 = "ETFSDLWKLL"

V1_QUEUE = Path("/home/bryza/fleet-results/mdm2_activator/boltz2_queue.jsonl")
V2_QUEUE = Path("/home/bryza/fleet-results/mdm2_activator_v2_allosteric/boltz2_queue.jsonl")

# ---------------- HTTP HELPER ----------------
def call_boltz2(polymers, ligands, timeout=TIMEOUT_S):
    """POST to Boltz-2 batched server. Returns (iptm, ptm, plddt, confidence, error_or_none)."""
    body = {
        "polymers": polymers,
        "ligands": ligands,
        "recycling_steps": RECYCLING_STEPS,
        "sampling_steps": SAMPLING_STEPS,
    }
    req = urllib.request.Request(
        URL,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
        iptm = data.get("iptm_scores", [0.0])[0]
        ptm = data.get("ptm_scores", [0.0])[0]
        plddt = data.get("complex_plddt_scores", [0.0])[0]
        conf = data.get("confidence_scores", [0.0])[0]
        return iptm, ptm, plddt, conf, None
    except urllib.error.HTTPError as e:
        return 0.0, 0.0, 0.0, 0.0, f"HTTP {e.code}: {e.read()[:200].decode(errors='ignore')}"
    except Exception as e:
        return 0.0, 0.0, 0.0, 0.0, f"ERR: {str(e)[:200]}"


def fold_baseline_mdm2_tp53():
    """Baseline: MDM2(17-125) + TP53 peptide (17-26), no ligand. Multiple replicas."""
    polymers = [
        {"id": "A", "sequence": MDM2_17_125},
        {"id": "B", "sequence": TP53_17_26},
    ]
    ligands = []  # no ligand
    reps = []
    for i in range(N_REPLICAS):
        t0 = time.time()
        iptm, ptm, plddt, conf, err = call_boltz2(polymers, ligands)
        dt = time.time() - t0
        reps.append({
            "rep": i,
            "iptm": iptm, "ptm": ptm, "plddt": plddt, "confidence": conf,
            "error": err, "elapsed_s": dt,
        })
        print(f"[baseline rep{i}] iptm={iptm:.4f} ptm={ptm:.4f} plddt={plddt:.4f} err={err} t={dt:.1f}s", flush=True)
    (RAW_DIR / "baseline_mdm2_tp53.json").write_text(json.dumps(reps, indent=2))
    oks = [r["iptm"] for r in reps if r["error"] is None and r["iptm"] > 0]
    return mean(oks) if oks else 0.0, stdev(oks) if len(oks) > 1 else 0.0, reps


def fold_ternary(smiles, compound_id, n_reps=None):
    """Ternary: MDM2 + TP53 peptide + compound. Returns iptm mean/sd + raw reps."""
    if n_reps is None:
        n_reps = N_REPLICAS
    polymers = [
        {"id": "A", "sequence": MDM2_17_125},
        {"id": "B", "sequence": TP53_17_26},
    ]
    ligands = [{"id": "L1", "smiles": smiles}]
    reps = []
    for i in range(n_reps):
        t0 = time.time()
        iptm, ptm, plddt, conf, err = call_boltz2(polymers, ligands)
        dt = time.time() - t0
        reps.append({
            "rep": i,
            "iptm": iptm, "ptm": ptm, "plddt": plddt, "confidence": conf,
            "error": err, "elapsed_s": dt,
        })
        print(f"  [{compound_id} rep{i}] iptm={iptm:.4f} err={err} t={dt:.1f}s", flush=True)
    oks = [r["iptm"] for r in reps if r["error"] is None and r["iptm"] > 0]
    return mean(oks) if oks else 0.0, stdev(oks) if len(oks) > 1 else 0.0, reps


def load_top_n(jsonl_path, n=20):
    """Load top N entries from a Boltz-2 queue JSONL."""
    out = []
    with open(jsonl_path) as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            out.append(json.loads(line))
    return out


def main():
    print(f"[triage] output dir: {OUT_DIR}")
    print(f"[triage] N_REPLICAS={N_REPLICAS} recycling={RECYCLING_STEPS} sampling={SAMPLING_STEPS}")

    # Step 1: baseline
    print("\n=== STEP 1: baseline MDM2+TP53-peptide (no ligand) ===")
    baseline_iptm, baseline_sd, baseline_reps = fold_baseline_mdm2_tp53()
    print(f"[baseline] mean_iptm={baseline_iptm:.4f} sd={baseline_sd:.4f} n_ok={sum(1 for r in baseline_reps if r['error'] is None)}")

    if baseline_iptm <= 0:
        print("[FATAL] baseline failed — cannot proceed. Check server.")
        sys.exit(2)

    # Step 2: load top 20 V1 + top 20 V2
    v1_top = load_top_n(V1_QUEUE, 20)
    v2_top = load_top_n(V2_QUEUE, 20)
    print(f"\n=== STEP 2: loaded {len(v1_top)} V1 + {len(v2_top)} V2 compounds ===")

    # Step 3: fold each compound, compute delta
    all_results = []
    for arm_tag, pool in [("V1", v1_top), ("V2", v2_top)]:
        print(f"\n=== STEP 3: {arm_tag} compounds ({len(pool)}) ===")
        for entry in pool:
            # V1 queue uses "ligand_smiles", V2 queue uses "smiles" — normalize
            smiles = entry.get("ligand_smiles") or entry.get("smiles")
            rank = entry.get("rank", entry.get("filename", "?"))
            cid = f"{arm_tag}_rank{rank}" if isinstance(rank, int) else f"{arm_tag}_{rank}"

            if not smiles:
                print(f"  [{cid}] SKIP: no smiles")
                continue

            # Multi-fragment SMILES (V2 top-3 contain "." = 2 disconnected parts)
            # Boltz-2 accepts multi-fragment ligand but some fail — pick the larger fragment.
            if "." in smiles:
                frags = smiles.split(".")
                frags.sort(key=len, reverse=True)
                orig = smiles
                smiles = frags[0]
                print(f"  [{cid}] multi-frag detected; using larger fragment: {smiles} (orig: {orig})")

            mean_iptm, sd_iptm, reps = fold_ternary(smiles, cid)
            delta = mean_iptm - baseline_iptm

            # Classification
            if delta < -0.1:
                arm_call = "INHIBITOR"
            elif delta > 0.05:
                arm_call = "ACTIVATOR"
            else:
                arm_call = "AMBIGUOUS"

            row = {
                "arm": arm_tag,
                "compound_id": cid,
                "rank": rank,
                "smiles": smiles,
                "mean_iptm": mean_iptm,
                "sd_iptm": sd_iptm,
                "n_ok": sum(1 for r in reps if r["error"] is None),
                "delta_iptm": delta,
                "arm_call": arm_call,
                "qed": entry.get("qed"),
                "mw": entry.get("mw"),
                "logp": entry.get("logp"),
                "bbb_prob": entry.get("bbb_prob"),
                "reps": reps,
            }
            all_results.append(row)
            print(f"  [{cid}] mean_iptm={mean_iptm:.4f} sd={sd_iptm:.4f} delta={delta:+.4f} => {arm_call}")

            # Checkpoint after each compound
            (RAW_DIR / "all_results.json").write_text(json.dumps({
                "baseline_iptm": baseline_iptm,
                "baseline_sd": baseline_sd,
                "baseline_reps": baseline_reps,
                "results": all_results,
            }, indent=2))

    # Final summary
    print("\n=== DONE ===")
    print(f"Baseline iptm: {baseline_iptm:.4f} +/- {baseline_sd:.4f}")
    v1_results = [r for r in all_results if r["arm"] == "V1"]
    v2_results = [r for r in all_results if r["arm"] == "V2"]
    print(f"V1 ({len(v1_results)}): INHIBITOR={sum(1 for r in v1_results if r['arm_call']=='INHIBITOR')} "
          f"ACTIVATOR={sum(1 for r in v1_results if r['arm_call']=='ACTIVATOR')} "
          f"AMBIGUOUS={sum(1 for r in v1_results if r['arm_call']=='AMBIGUOUS')}")
    print(f"V2 ({len(v2_results)}): INHIBITOR={sum(1 for r in v2_results if r['arm_call']=='INHIBITOR')} "
          f"ACTIVATOR={sum(1 for r in v2_results if r['arm_call']=='ACTIVATOR')} "
          f"AMBIGUOUS={sum(1 for r in v2_results if r['arm_call']=='AMBIGUOUS')}")


if __name__ == "__main__":
    main()

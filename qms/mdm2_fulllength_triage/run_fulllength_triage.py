"""MDM2 full-length (491 aa) V1/V2 mechanistic triage — contact-map classification.

Replaces the iptm-delta scheme from a31633bf (which failed due to domain mismatch +
iptm ceiling). Here we:

  1. Co-fold MDM2 (full-length 1-491) + TP53 TAD (17-26) + compound via Boltz-2
     (3-body co-fold).
  2. Parse the returned PDB structure.
  3. For each compound, compute:
       - N_term_contacts: heavy-atom contacts within 5 A of residues 17-125
       - RING_contacts: heavy-atom contacts within 5 A of residues 430-491
       - pocket_selectivity = RING_contacts / (N_term_contacts + RING_contacts)
       - d_Cys464_SG, d_Cys475_SG: min heavy-atom distance from compound to Cys464/Cys475 S-gamma
       - A-B iptm change (preservation vs drop) — we use complex iptm as proxy for AB interface
         since the batched server currently does not export per-chain-pair iptm.
  4. Classify:
       - pocket_selectivity > 0.7 AND iptm drop < 0.05  -> V2_ACTIVATOR_CANDIDATE
       - pocket_selectivity < 0.3 AND iptm drop >= 0.05  -> V1_INHIBITOR_CANDIDATE
       - pocket_selectivity 0.3-0.7 OR mixed signal      -> AMBIGUOUS

Uses Boltz-2 batched server at localhost:8004 AND localhost:8003 (round-robin) to
share traffic with other concurrent campaigns.
"""
import json
import os
import sys
import time
import threading
import urllib.request
import urllib.error
import io
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from statistics import mean, stdev

# ---------------- CONFIG ----------------
# Default: round-robin across 8003 (sma-h100-two) + 8004 (vast.ai H100).
# Override BOLTZ2_URL_A / BOLTZ2_URL_B to force a single endpoint.
URLS = [
    os.environ.get("BOLTZ2_URL_A", "http://localhost:8004/predict"),
    os.environ.get("BOLTZ2_URL_B", "http://localhost:8004/predict"),
]
N_REPLICAS = int(os.environ.get("N_REPLICAS", "2"))
RECYCLING_STEPS = 1
SAMPLING_STEPS = 25
TIMEOUT_S = 600  # hard cap per call; on stall, fail fast and continue
CONTACT_CUTOFF_A = 5.0
N_TERM_RANGE = (17, 125)
RING_RANGE = (430, 491)
# Key autoubiquitination cysteines in RING (UniProt Q00987)
RING_CATALYTIC_CYSTEINES = [464, 475]

OUT_DIR = Path("/home/bryza/sma-research/qms/mdm2_fulllength_triage")
RAW_DIR = OUT_DIR / "raw"
RAW_DIR.mkdir(exist_ok=True, parents=True)

# MDM2 full-length — UniProt Q00987, 491 aa (canonical)
MDM2_FL = (
    "MCNTNMSVPTDGAVTTSQIPASEQETLVRPKPLLLKLLKSVGAQKDTYTMKEVLFYLGQY"
    "IMTKRLYDEKQQHIVYCSNDLLGDLFGVPSFSVKEHRKIYTMIYRNLVVVNQQESSDSGT"
    "SVSENRCHLEGGSDQKDLVQELQEEKPSSSHLVSRPSTSSRRRAISETEENSDELSGERQ"
    "RKRHKSDSISLSFDESLALCVIREICCERSSSSESTGTPSNPDLDAGVSEHSGDWLDQDS"
    "VSDQFSVEFEVESLDSEDYSLSEEGQELSDEDDEVYQVTVYQAGESDTDSFEEDPEISLA"
    "DYWKCTSCNEMNPPLPSHCNRCWALRENWLPEDKGKDKGEISEKAKLENSTQAEEGFDVP"
    "DCKKTIVNDSRESCVEENDDKITQASQSQESEDYSQPSTSSSIIYSSQEDVKEFEREETQ"
    "DKEESVESSLPLNAIEPCVICQGRPKNGCIVHGKTGHLMACFTCAKKLKKRNKPCPVCRQ"
    "PIQMIVLTYFP"
)
assert len(MDM2_FL) == 491, f"MDM2_FL length != 491, got {len(MDM2_FL)}"
# Verify Cys at positions 464, 475 in the 1-indexed sequence
for c in RING_CATALYTIC_CYSTEINES:
    assert MDM2_FL[c - 1] == "C", f"expected Cys at pos {c}, got {MDM2_FL[c-1]}"

TP53_17_26 = "ETFSDLWKLL"

# ---------------- HTTP HELPER ----------------
_url_idx_lock = threading.Lock()
_url_idx = {"i": 0}


def pick_url():
    with _url_idx_lock:
        u = URLS[_url_idx["i"] % len(URLS)]
        _url_idx["i"] += 1
    return u


def call_boltz2(polymers, ligands, timeout=TIMEOUT_S, tries=2):
    """POST to Boltz-2 batched server. Returns (iptm, ptm, plddt, structure_pdb, error_or_none)."""
    body = {
        "polymers": polymers,
        "ligands": ligands,
        "recycling_steps": RECYCLING_STEPS,
        "sampling_steps": SAMPLING_STEPS,
    }
    last_err = None
    for attempt in range(tries):
        url = pick_url()
        req = urllib.request.Request(
            url,
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
            structs = data.get("structures", [{}])
            pdb = structs[0].get("structure", "") if structs else ""
            return iptm, ptm, plddt, pdb, None
        except urllib.error.HTTPError as e:
            last_err = f"HTTP {e.code}: {e.read()[:200].decode(errors='ignore')}"
        except Exception as e:
            last_err = f"ERR({url}): {str(e)[:200]}"
    return 0.0, 0.0, 0.0, "", last_err


# ---------------- PDB parsing + contacts ----------------
def parse_pdb(pdb_text):
    """Return list of (chain_id, resnum, resname, atomname, element, x, y, z, is_hetatm).
    Boltz-2 output: chain A = MDM2, chain B = TP53, chain L = ligand (HETATM, resname LIG).
    Boltz-2 PDB has non-standard column widths; we parse by whitespace-split after
    the record marker + serial."""
    atoms = []
    for line in pdb_text.splitlines():
        is_het = line.startswith("HETATM")
        if not (line.startswith("ATOM") or is_het):
            continue
        try:
            # Whitespace-robust: split tokens after the record name + serial.
            # Format: RECORD serial atomname [altloc]resname chain resnum[icode] x y z occ bfac [segid] element [chg]
            # Boltz-2 emits: "HETATM 3949  C9  LIG L1   1      -6.986  -0.614 -10.230  1.00 42.81           C  "
            # tokens: ['HETATM','3949','C9','LIG','L1','1','-6.986','-0.614','-10.230','1.00','42.81','C']
            parts = line.split()
            if len(parts) < 10:
                continue
            atomname = parts[2]
            resname = parts[3]
            chain_res = parts[4]   # "L1" or "A" (chain) - depends on boltz output
            # Detect chain/resnum ambiguity: if chain_res is just letters, next token is resnum.
            # If chain_res is letter+digits (e.g. 'L1'), split.
            if len(chain_res) == 1 and chain_res.isalpha():
                chain = chain_res
                resnum = int(parts[5])
                coord_idx = 6
            else:
                # mix like 'L1' or 'A42' — split at the first digit
                # But we need to be careful: for proteins Boltz writes chain + resnum separately.
                # Check char by char
                for k, ch in enumerate(chain_res):
                    if ch.isdigit():
                        chain = chain_res[:k]
                        resnum_prefix = chain_res[k:]
                        break
                else:
                    chain = chain_res
                    resnum_prefix = ""
                # Then parts[5] might be the resnum OR a continuation
                if resnum_prefix:
                    # Boltz sometimes writes "L1" as chain+segment id, and the actual resnum is parts[5]
                    try:
                        resnum = int(parts[5])
                        coord_idx = 6
                    except Exception:
                        resnum = int(resnum_prefix)
                        coord_idx = 5
                else:
                    resnum = int(parts[5])
                    coord_idx = 6
            x = float(parts[coord_idx])
            y = float(parts[coord_idx + 1])
            z = float(parts[coord_idx + 2])
            # Element is the last non-numeric token; check last col
            element = parts[-1]
            if len(element) > 2 or not element.isalpha():
                element = atomname[0]
            atoms.append((chain, resnum, resname, atomname, element, x, y, z, is_het))
        except Exception:
            continue
    return atoms


def _dist2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2


def classify_contacts(pdb_text, ligand_chain_hint="C"):
    """Parse pdb and compute contact metrics.
    Uses HETATM records as the ligand. Heavy atoms only (element != H)."""
    atoms = parse_pdb(pdb_text)
    if not atoms:
        return {"error": "empty pdb"}

    # ligand = HETATM records with non-H element
    ligand = [(a[5], a[6], a[7]) for a in atoms if a[8] and a[4] != "H"]
    if not ligand:
        # fall back: take any chain that is NOT chain A or chain B in Boltz-2 convention
        ligand = [(a[5], a[6], a[7]) for a in atoms if a[0] not in ("A", "B") and a[4] != "H"]
    if not ligand:
        return {"error": "no ligand atoms"}

    # MDM2 = chain A (heavy atoms, exclude H)
    mdm2 = [(a[1], a[5], a[6], a[7], a[3]) for a in atoms if a[0] == "A" and a[4] != "H" and not a[8]]
    if not mdm2:
        return {"error": "no MDM2 chain A atoms"}

    cutoff2 = CONTACT_CUTOFF_A ** 2

    n_term_contacts = 0
    ring_contacts = 0
    n_term_resids = set()
    ring_resids = set()

    for resnum, px, py, pz, atomname in mdm2:
        in_nterm = N_TERM_RANGE[0] <= resnum <= N_TERM_RANGE[1]
        in_ring = RING_RANGE[0] <= resnum <= RING_RANGE[1]
        if not (in_nterm or in_ring):
            continue
        hit = False
        for lx, ly, lz in ligand:
            if _dist2((px, py, pz), (lx, ly, lz)) <= cutoff2:
                hit = True
                break
        if hit:
            if in_nterm:
                n_term_contacts += 1
                n_term_resids.add(resnum)
            if in_ring:
                ring_contacts += 1
                ring_resids.add(resnum)

    total = n_term_contacts + ring_contacts
    pocket_sel = ring_contacts / total if total > 0 else 0.0

    # Distance from ligand to Cys-SG of catalytic RING cysteines
    cys_dists = {}
    for cys_n in RING_CATALYTIC_CYSTEINES:
        sg = [(px, py, pz) for rn, px, py, pz, atom in mdm2 if rn == cys_n and atom == "SG"]
        if not sg:
            cys_dists[f"d_Cys{cys_n}_SG"] = None
            continue
        sgx, sgy, sgz = sg[0]
        dmin = min(
            ((lx - sgx) ** 2 + (ly - sgy) ** 2 + (lz - sgz) ** 2) ** 0.5
            for lx, ly, lz in ligand
        )
        cys_dists[f"d_Cys{cys_n}_SG"] = round(dmin, 2)

    return {
        "n_term_contacts": n_term_contacts,
        "ring_contacts": ring_contacts,
        "pocket_selectivity": round(pocket_sel, 3),
        "n_term_residues": sorted(n_term_resids),
        "ring_residues": sorted(ring_resids),
        "n_ligand_atoms": len(ligand),
        "n_mdm2_atoms": len(mdm2),
        **cys_dists,
    }


# ---------------- Folding pipelines ----------------
def fold_baseline():
    """Baseline: MDM2-FL + TP53 peptide, no ligand. Reps in parallel across 2 endpoints."""
    polymers = [
        {"id": "A", "sequence": MDM2_FL},
        {"id": "B", "sequence": TP53_17_26},
    ]
    reps = [None] * N_REPLICAS

    def _one(i):
        t0 = time.time()
        iptm, ptm, plddt, pdb, err = call_boltz2(polymers, [])
        dt = time.time() - t0
        return i, {"rep": i, "iptm": iptm, "ptm": ptm, "plddt": plddt, "error": err, "elapsed_s": dt}

    with ThreadPoolExecutor(max_workers=min(N_REPLICAS, 2)) as ex:
        futs = [ex.submit(_one, i) for i in range(N_REPLICAS)]
        for f in as_completed(futs):
            i, row = f.result()
            reps[i] = row
            print(f"[baseline rep{i}] iptm={row['iptm']:.4f} err={row['error']} t={row['elapsed_s']:.1f}s", flush=True)
    (RAW_DIR / "baseline_fl.json").write_text(json.dumps(reps, indent=2))
    oks = [r["iptm"] for r in reps if r["error"] is None and r["iptm"] > 0]
    return (mean(oks) if oks else 0.0), (stdev(oks) if len(oks) > 1 else 0.0), reps


def fold_ternary(smiles, cid):
    """3-body fold + contact analysis. Reps parallel across 2 endpoints."""
    polymers = [
        {"id": "A", "sequence": MDM2_FL},
        {"id": "B", "sequence": TP53_17_26},
    ]
    ligands = [{"id": "L1", "smiles": smiles}]
    reps = [None] * N_REPLICAS

    def _one(i):
        t0 = time.time()
        iptm, ptm, plddt, pdb, err = call_boltz2(polymers, ligands)
        dt = time.time() - t0
        rep = {"rep": i, "iptm": iptm, "ptm": ptm, "plddt": plddt, "error": err, "elapsed_s": dt}
        if err is None and pdb:
            rep["contacts"] = classify_contacts(pdb)
            if i == 0:
                try:
                    (RAW_DIR / f"pdb_{cid}.pdb").write_text(pdb)
                except Exception:
                    pass
        return i, rep

    with ThreadPoolExecutor(max_workers=min(N_REPLICAS, 2)) as ex:
        futs = [ex.submit(_one, i) for i in range(N_REPLICAS)]
        for f in as_completed(futs):
            i, rep = f.result()
            reps[i] = rep
            c = rep.get("contacts", {}) or {}
            print(
                f"  [{cid} rep{i}] iptm={rep['iptm']:.4f} "
                f"n_term={c.get('n_term_contacts','-')} "
                f"ring={c.get('ring_contacts','-')} "
                f"sel={c.get('pocket_selectivity','-')} err={rep['error']} t={rep['elapsed_s']:.1f}s",
                flush=True,
            )
    contacts = [r["contacts"] for r in reps if r and r.get("contacts") and "error" not in r.get("contacts", {})]
    return reps, contacts


def aggregate(reps, contacts):
    """Collapse replicas into a row."""
    oks = [r for r in reps if r["error"] is None and r["iptm"] > 0]
    mean_iptm = mean([r["iptm"] for r in oks]) if oks else 0.0
    sd_iptm = stdev([r["iptm"] for r in oks]) if len(oks) > 1 else 0.0

    # Aggregate contacts: mean of available reps
    if contacts:
        mean_nterm = mean([c.get("n_term_contacts", 0) for c in contacts])
        mean_ring = mean([c.get("ring_contacts", 0) for c in contacts])
        total = mean_nterm + mean_ring
        pocket_sel = mean_ring / total if total > 0 else 0.0
        # Merge Cys distances (min across reps — closest approach)
        def _min_or_none(key):
            vals = [c.get(key) for c in contacts if c.get(key) is not None]
            return round(min(vals), 2) if vals else None
        d464 = _min_or_none("d_Cys464_SG")
        d475 = _min_or_none("d_Cys475_SG")
        nterm_res = sorted(set().union(*[set(c.get("n_term_residues", [])) for c in contacts]))
        ring_res = sorted(set().union(*[set(c.get("ring_residues", [])) for c in contacts]))
    else:
        mean_nterm = mean_ring = pocket_sel = 0.0
        d464 = d475 = None
        nterm_res = ring_res = []
    return {
        "mean_iptm": round(mean_iptm, 4),
        "sd_iptm": round(sd_iptm, 4),
        "n_ok": len(oks),
        "mean_n_term_contacts": round(mean_nterm, 1),
        "mean_ring_contacts": round(mean_ring, 1),
        "pocket_selectivity": round(pocket_sel, 3),
        "d_Cys464_SG_min": d464,
        "d_Cys475_SG_min": d475,
        "n_term_residues_union": nterm_res,
        "ring_residues_union": ring_res,
    }


def classify(row, baseline_iptm):
    """Apply the new rubric."""
    sel = row["pocket_selectivity"]
    iptm_drop = baseline_iptm - row["mean_iptm"]  # positive = iptm dropped

    # Catalytic-cys block: heavy atom < 5 A from either Cys464-SG or Cys475-SG counts as "block"
    cys_block = False
    for k in ("d_Cys464_SG_min", "d_Cys475_SG_min"):
        d = row.get(k)
        if d is not None and d < 5.0:
            cys_block = True
            break

    if sel > 0.7 and iptm_drop < 0.05:
        call_ = "V2_ACTIVATOR_CANDIDATE"
    elif sel < 0.3 and iptm_drop >= 0.05:
        call_ = "V1_INHIBITOR_CANDIDATE"
    elif sel > 0.7 and cys_block:
        call_ = "V2_E3_INHIBITOR_CANDIDATE"  # RING-binder but catalytic-cys blocked
    else:
        call_ = "AMBIGUOUS"

    # Confidence tier
    n_contacts_total = row["mean_n_term_contacts"] + row["mean_ring_contacts"]
    if n_contacts_total == 0:
        tier = "UNBOUND"
    elif n_contacts_total < 3:
        tier = "LOW"
    elif n_contacts_total < 10:
        tier = "MEDIUM"
    else:
        tier = "HIGH"

    row["iptm_drop_vs_baseline"] = round(iptm_drop, 4)
    row["cys_block"] = cys_block
    row["classification"] = call_
    row["confidence_tier"] = tier
    return row


def main():
    print(f"[triage-FL] output dir: {OUT_DIR}")
    print(f"[triage-FL] N_REPLICAS={N_REPLICAS} endpoints={URLS}")
    print(f"[triage-FL] MDM2 length={len(MDM2_FL)} (expect 491) — N-term {N_TERM_RANGE} RING {RING_RANGE}")

    # Load existing compound set from a31633bf
    src = Path("/home/bryza/sma-research/qms/mdm2_mechanism_triage/raw/all_results.json")
    prev = json.loads(src.read_text())
    compounds = [
        {"arm": r["arm"], "compound_id": r["compound_id"], "smiles": r["smiles"],
         "rank": r.get("rank"), "qed": r.get("qed"), "bbb_prob": r.get("bbb_prob")}
        for r in prev["results"]
    ]
    print(f"[triage-FL] loaded {len(compounds)} compounds from a31633bf")

    # Resume from checkpoint if available
    results = []
    base_mean = base_sd = None
    base_reps = []
    ckpt = RAW_DIR / "all_results.json"
    if ckpt.exists():
        try:
            prev_ckpt = json.loads(ckpt.read_text())
            results = prev_ckpt.get("results", [])
            base_mean = prev_ckpt.get("baseline_iptm")
            base_sd = prev_ckpt.get("baseline_sd", 0)
            base_reps = prev_ckpt.get("baseline_reps", [])
            if results:
                print(f"[triage-FL] RESUME from checkpoint: {len(results)} compounds already done, baseline_iptm={base_mean}")
        except Exception as e:
            print(f"[triage-FL] checkpoint load failed: {e}")
            results = []

    # Step 1: baseline (skip if resumed)
    if base_mean is None or base_mean <= 0:
        print("\n=== STEP 1: baseline MDM2-FL + TP53 (no ligand) ===")
        base_mean, base_sd, base_reps = fold_baseline()
        print(f"[baseline] mean_iptm={base_mean:.4f} sd={base_sd:.4f}")
        if base_mean <= 0:
            print("[FATAL] baseline failed")
            sys.exit(2)

    # Skip compounds already done
    done_ids = {r["compound_id"] for r in results}

    # Step 2: 40 compounds
    for ci, comp in enumerate(compounds, 1):
        if comp["compound_id"] in done_ids:
            print(f"\n--- {ci}/{len(compounds)} {comp['compound_id']} (SKIP — already in checkpoint) ---")
            continue
        cid = comp["compound_id"]
        smi = comp["smiles"]
        if "." in smi:
            frags = sorted(smi.split("."), key=len, reverse=True)
            smi = frags[0]
            print(f"  [{cid}] multi-frag; using largest: {smi}")
        print(f"\n--- {ci}/{len(compounds)} {cid} ({comp['arm']}) ---")
        reps, contacts = fold_ternary(smi, cid)
        agg = aggregate(reps, contacts)
        row = {
            "arm": comp["arm"],
            "compound_id": cid,
            "rank": comp["rank"],
            "smiles": smi,
            "qed": comp.get("qed"),
            "bbb_prob": comp.get("bbb_prob"),
            **agg,
            "reps": reps,
        }
        row = classify(row, base_mean)
        results.append(row)
        print(
            f"  [{cid}] iptm={row['mean_iptm']:.4f} drop={row['iptm_drop_vs_baseline']:+.4f} "
            f"sel={row['pocket_selectivity']} cys_block={row['cys_block']} "
            f"=> {row['classification']} [{row['confidence_tier']}]"
        )
        # Checkpoint
        (RAW_DIR / "all_results.json").write_text(json.dumps({
            "baseline_iptm": base_mean,
            "baseline_sd": base_sd,
            "baseline_reps": base_reps,
            "results": results,
            "n_replicas": N_REPLICAS,
            "recycling_steps": RECYCLING_STEPS,
            "sampling_steps": SAMPLING_STEPS,
        }, indent=2))

    # Emit a flat contact_maps.json for the report
    cm = {
        "baseline_iptm_fulllength": base_mean,
        "n_term_range": list(N_TERM_RANGE),
        "ring_range": list(RING_RANGE),
        "catalytic_cysteines": RING_CATALYTIC_CYSTEINES,
        "per_compound": [
            {k: r[k] for k in (
                "arm", "compound_id", "rank", "smiles",
                "mean_iptm", "iptm_drop_vs_baseline",
                "mean_n_term_contacts", "mean_ring_contacts", "pocket_selectivity",
                "d_Cys464_SG_min", "d_Cys475_SG_min", "n_term_residues_union",
                "ring_residues_union", "cys_block", "classification", "confidence_tier"
            )}
            for r in results
        ],
    }
    (RAW_DIR.parent / "contact_maps.json").write_text(json.dumps(cm, indent=2))

    # Summary
    v1 = [r for r in results if r["arm"] == "V1"]
    v2 = [r for r in results if r["arm"] == "V2"]
    print("\n=== SUMMARY ===")
    def ccounts(pool, label):
        classes = [r["classification"] for r in pool]
        u = set(classes)
        for c in sorted(u):
            print(f"  {label} {c}: {classes.count(c)}")
    ccounts(v1, "V1")
    ccounts(v2, "V2")


if __name__ == "__main__":
    main()

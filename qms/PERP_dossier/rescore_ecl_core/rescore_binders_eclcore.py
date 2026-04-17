#!/usr/bin/env python3
"""
ECL-core-only Boltz-2 rescore of all 240 Round-1 PERP binders.

Context:
  Round-1 co-folded binders vs full 193-aa PERP. Interface analyzer (Biopython)
  on top-10 showed 8/10 binders contact PERP C-terminal tail (A170-A193), NOT
  the intended ECL loop. Only H1c_25_s5 (45%) and H1b_10_s3 (27%) were ECL-selective.

Fix:
  Rescore every Round-1 binder against its INTENDED ECL core only:
    * ECL1 core = PERP[30-80] (51 aa), used for H1a/H1b/H1c
    * ECL2 core = PERP[128-153] (26 aa), used for H2a/H2b/H2c
  Remove tail → binder cannot cheat → iptm now reflects true on-ECL affinity.

Pipeline:
  1. Load 240 binder seqs from Round-1 boltz2_results.json per hotspot.
  2. Round-robin dispatch to localhost:8003 + localhost:8004.
  3. For each binder:
       a. fold(ECL_core, binder)    → iptm_target_core
       b. fold(ECL_core, scramble(binder, seed=42))  → iptm_scrambled_core
       c. delta_iptm_core = target - scrambled
  4. Parse returned target structure, compute contact residues on chain A.
     Because chain A = ECL core, iface_res_A represent the ECL residues touched.
  5. Persist per-binder JSONL (resumable).
  6. Rank by delta_iptm_core (desc), tiebreak iptm_target_core then plddt.
  7. Apply filter: iptm_target_core >= 0.35 AND delta_iptm_core > 0.08
     AND at least 3 contact residues on chain A.
  8. Emit per-ECL top-10 TSV + merged master TSV.

Outputs:
  /home/bryza/fleet-results/perp_binder_design_FINAL/rescore_ECLcore_v2.tsv
  /home/bryza/sma-research/qms/PERP_dossier/rescore_ecl_core/rescore_results.jsonl
"""
import json, os, sys, time, random, math, io
import urllib.request, urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from itertools import cycle

# ---- PERP + ECL core sequences ----
PERP_SEQ = (
    "MIRCGLACERCRWILPLLLLSAIAFDIIALAGRGWLQSSDHGQTSSLWWKCSQEGGGSGSYE"
    "EGCQSLMEYAWGRAAAAMLFCGFIILVICFILSFFALCGPQMLVFLRVIGGLLALAAVFQII"
    "SLVIYPVKYTQTFTLHANPAVTYIYNWAYGFGWAATIILIGCAFFFCCLPNYEDDLLGNAKP"
    "RYFYTSA"
)
# ECL1 core: PERP residues 30-80 inclusive (1-indexed). Derived from existing
# PERP_ECL1core.pdb in binders/ which Round-1 used as the ECL1 target definition.
ECL1_CORE = PERP_SEQ[29:80]   # 51 aa
# ECL2 core: PERP residues 128-153 (from PERP_ECL2core.pdb).
ECL2_CORE = PERP_SEQ[127:153]  # 26 aa
assert len(ECL1_CORE) == 51 and ECL1_CORE.startswith("L")
assert len(ECL2_CORE) == 26 and ECL2_CORE.startswith("I")

ECL_CORES = {"ecl1": ECL1_CORE, "ecl2": ECL2_CORE}
HOTSPOTS = {"ecl1": ["H1a", "H1b", "H1c"], "ecl2": ["H2a", "H2b", "H2c"]}

ROUND1_BASE = Path("/home/bryza/gpu-fleet/campaigns/perp_interactome_v6e8/binders")
OUT_DIR = Path("/home/bryza/sma-research/qms/PERP_dossier/rescore_ecl_core")
OUT_DIR.mkdir(parents=True, exist_ok=True)
JSONL = OUT_DIR / "rescore_results.jsonl"

ENDPOINTS = [
    "http://localhost:8003/biology/mit/boltz2/predict",
    "http://localhost:8004/biology/mit/boltz2/predict",
]
ep_cycle = cycle(ENDPOINTS)
ep_lock = Lock()
write_lock = Lock()
def next_ep():
    with ep_lock:
        return next(ep_cycle)


def scramble(seq: str, seed: int = 42) -> str:
    r = random.Random(seed)
    lst = list(seq)
    r.shuffle(lst)
    return ''.join(lst)


def boltz2_ppi(url, target_seq, binder_seq, attempts=3, timeout=900):
    body = {
        "polymers": [
            {"id": "A", "molecule_type": "protein", "sequence": target_seq},
            {"id": "B", "molecule_type": "protein", "sequence": binder_seq},
        ],
        "ligands": [],
        "recycling_steps": 1,
        "sampling_steps": 25,
    }
    for i in range(attempts):
        try:
            req = urllib.request.Request(
                url, data=json.dumps(body).encode(),
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                method="POST")
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = json.loads(r.read())
            return {
                "iptm":  (data.get("iptm_scores") or [None])[0],
                "ptm":   (data.get("ptm_scores")  or [None])[0],
                "plddt": (data.get("complex_plddt_scores") or [None])[0],
                "conf":  (data.get("confidence_scores") or [None])[0],
                "structure": (data.get("structures") or [{}])[0].get("structure", ""),
                "status": "ok",
            }
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504) and i < attempts - 1:
                time.sleep(5 * (2 ** i))
                continue
            return {"iptm": None, "ptm": None, "plddt": None, "structure": "",
                    "status": f"http_{e.code}"}
        except Exception as e:
            if i == attempts - 1:
                return {"iptm": None, "ptm": None, "plddt": None, "structure": "",
                        "status": f"err:{type(e).__name__}:{str(e)[:80]}"}
            time.sleep(5 * (2 ** i))
    return {"iptm": None, "ptm": None, "plddt": None, "structure": "",
            "status": "retries_exhausted"}


def parse_contacts(pdb_text, cutoff=4.5):
    """Parse ATOM records; compute interface residues between chain A and chain B.

    Returns: {iface_res_A: sorted list of resSeq (ints),
              iface_res_B: sorted list,
              heavy_atom_contacts: int,
              n_iface_A: int, n_iface_B: int}
    """
    if not pdb_text:
        return {"iface_res_A": [], "iface_res_B": [],
                "heavy_atom_contacts": 0, "n_iface_A": 0, "n_iface_B": 0}
    # Parse ATOM records into (chain, resSeq, x,y,z)
    atomsA, atomsB = [], []
    for line in pdb_text.split("\n"):
        if not line.startswith("ATOM"):
            continue
        # PDB column-based parsing (safer than split)
        try:
            elem = line[76:78].strip()
            if elem == "H":
                continue
            atname = line[12:16].strip()
            if atname.startswith("H"):  # hydrogen fallback
                continue
            chain = line[21]
            resSeq = int(line[22:26])
            x = float(line[30:38]); y = float(line[38:46]); z = float(line[46:54])
        except (ValueError, IndexError):
            continue
        if chain == "A":
            atomsA.append((resSeq, x, y, z))
        elif chain == "B":
            atomsB.append((resSeq, x, y, z))
    contacts = 0
    iface_A, iface_B = set(), set()
    cut2 = cutoff * cutoff
    for (ra, xa, ya, za) in atomsA:
        for (rb, xb, yb, zb) in atomsB:
            dx = xa - xb; dy = ya - yb; dz = za - zb
            d2 = dx*dx + dy*dy + dz*dz
            if d2 <= cut2:
                contacts += 1
                iface_A.add(ra); iface_B.add(rb)
    return {"iface_res_A": sorted(iface_A), "iface_res_B": sorted(iface_B),
            "heavy_atom_contacts": contacts,
            "n_iface_A": len(iface_A), "n_iface_B": len(iface_B)}


def load_all_binders():
    """Return list of dicts {ecl, hotspot, id, seq, len, plddt_mean, ptm, iptm_target_full, delta_iptm_full, mpnn_score}."""
    out = []
    for ecl, hot_list in HOTSPOTS.items():
        for hot in hot_list:
            f = ROUND1_BASE / ecl / hot / "boltz2_results.json"
            if not f.exists():
                print(f"[warn] missing {f}", file=sys.stderr)
                continue
            rows = json.load(open(f))
            for r in rows:
                if "delta_iptm" not in r:
                    continue
                out.append({
                    "ecl": ecl, "hotspot": hot,
                    "id": r["id"], "seq": r["seq"], "len": r.get("len", len(r["seq"])),
                    "plddt_mean": r.get("plddt_mean", 0.0),
                    "ptm": r.get("ptm", 0.0),
                    "iptm_target_full": r.get("iptm_target", 0.0),
                    "iptm_scrambled_full": r.get("iptm_scrambled", 0.0),
                    "delta_iptm_full": r.get("delta_iptm", 0.0),
                    "mpnn_score": r.get("mpnn_score", 0.0),
                })
    return out


def load_done():
    done = {}
    if JSONL.exists():
        for line in JSONL.read_text().splitlines():
            try:
                r = json.loads(line)
                if r.get("status_target") == "ok" and r.get("status_scrambled") == "ok":
                    done[r["id"]] = r
            except Exception:
                continue
    return done


def job_fn(binder):
    core = ECL_CORES[binder["ecl"]]
    url1 = next_ep()
    tgt = boltz2_ppi(url1, core, binder["seq"])
    url2 = next_ep()
    scr = boltz2_ppi(url2, core, scramble(binder["seq"], seed=42))
    contacts = parse_contacts(tgt.get("structure", ""), cutoff=4.5)
    rec = {
        **{k: binder[k] for k in ("id", "ecl", "hotspot", "seq", "len",
                                   "plddt_mean", "ptm",
                                   "iptm_target_full", "iptm_scrambled_full",
                                   "delta_iptm_full", "mpnn_score")},
        "iptm_target_core":    tgt.get("iptm"),
        "ptm_target_core":     tgt.get("ptm"),
        "plddt_target_core":   tgt.get("plddt"),
        "iptm_scrambled_core": scr.get("iptm"),
        "ptm_scrambled_core":  scr.get("ptm"),
        "plddt_scrambled_core":scr.get("plddt"),
        "status_target":       tgt.get("status"),
        "status_scrambled":    scr.get("status"),
        "endpoints": [url1.split("/")[2], url2.split("/")[2]],
        "iface_res_A_list": contacts["iface_res_A"],
        "iface_res_B_list": contacts["iface_res_B"],
        "heavy_atom_contacts": contacts["heavy_atom_contacts"],
        "n_iface_A": contacts["n_iface_A"],
        "n_iface_B": contacts["n_iface_B"],
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if tgt.get("iptm") is not None and scr.get("iptm") is not None:
        rec["delta_iptm_core"] = tgt["iptm"] - scr["iptm"]
    else:
        rec["delta_iptm_core"] = None
    # Persist structure to disk (target pose only, scrambled discarded to save space)
    if tgt.get("structure"):
        pdb_path = OUT_DIR / "poses" / f"{binder['id']}_core.pdb"
        pdb_path.parent.mkdir(exist_ok=True)
        pdb_path.write_text(tgt["structure"])
    with write_lock:
        with open(JSONL, "a") as f:
            f.write(json.dumps(rec) + "\n")
            f.flush()
    return rec


def main():
    all_binders = load_all_binders()
    print(f"[rescore] loaded {len(all_binders)} Round-1 binders "
          f"(ECL1={sum(1 for b in all_binders if b['ecl']=='ecl1')}, "
          f"ECL2={sum(1 for b in all_binders if b['ecl']=='ecl2')})",
          file=sys.stderr, flush=True)
    done = load_done()
    print(f"[rescore] resume: {len(done)} binders already rescored", file=sys.stderr)
    pending = [b for b in all_binders if b["id"] not in done]
    print(f"[rescore] {len(pending)} pending", file=sys.stderr)
    if not pending:
        print("[rescore] all done", file=sys.stderr)
        return

    t0 = time.time()
    n_ok, n_err = 0, 0
    workers = int(os.environ.get("RESCORE_WORKERS", "6"))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(job_fn, b): b for b in pending}
        for i, fut in enumerate(as_completed(futs), 1):
            b = futs[fut]
            try:
                r = fut.result()
                if r.get("delta_iptm_core") is not None:
                    n_ok += 1
                    print(f"[{i}/{len(pending)}] {r['id']} ({r['ecl']}) "
                          f"iptmT={r['iptm_target_core']:.3f} iptmS={r['iptm_scrambled_core']:.3f} "
                          f"dIptm={r['delta_iptm_core']:+.3f} ifaceA={r['n_iface_A']}",
                          flush=True)
                else:
                    n_err += 1
                    print(f"[{i}/{len(pending)}] {r['id']} ERR "
                          f"t={r['status_target']} s={r['status_scrambled']}", flush=True)
            except Exception as e:
                n_err += 1
                print(f"[{i}/{len(pending)}] {b['id']} WORKER-ERR {type(e).__name__}: {e}",
                      flush=True)
            if i % 5 == 0:
                elapsed = time.time() - t0
                rate = i / max(elapsed, 1)
                eta = (len(pending) - i) / max(rate, 1e-6)
                print(f"  [progress] {i}/{len(pending)} ok={n_ok} err={n_err} "
                      f"elapsed={elapsed:.0f}s eta={eta:.0f}s", flush=True)

    print(f"[rescore] DONE n_ok={n_ok} n_err={n_err}", file=sys.stderr)


if __name__ == "__main__":
    main()

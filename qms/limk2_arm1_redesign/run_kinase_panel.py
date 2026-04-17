"""15-kinase selectivity panel for Arm 1 redesign survivors.

Takes the affinity_probability_binary > 0.3 gate survivors from GATE_DECISION.json,
runs Boltz-2 against each of 15 kinases (including LIMK2) via the
batched localhost:8003 server on sma-h100-two.

Computes:
  - z_LIMK2: (iptm_LIMK2 - mean(all)) / sd(all)
  - sel_z: (iptm_LIMK2 - mean(off-targets)) / sd(off-targets)
  - gate: z_LIMK2 > 0 AND sel_z > 0

Writes:
  - kinase_panel_raw.jsonl
  - kinase_panel_ranked.csv
  - SELECTIVITY_GATE.json
"""
import csv
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/home/bryza/sma-research/qms/limk2_arm1_redesign")
KINASE_SEQS = json.loads(Path("/home/bryza/fleet-results/kinase_panel_domains.json").read_text())
BOLTZ_HOST = "sma-h100-two"
REMOTE_IN = "/home/shadeform/limk2_arm1_panel/in"
REMOTE_OUT = "/home/shadeform/limk2_arm1_panel/out"

# Panel order (keep LIMK2 first)
PANEL = ["LIMK2", "LIMK1", "ROCK1", "ROCK2", "JAK1", "JAK2", "JAK3",
         "CDK2", "CDK5", "SRC", "FYN", "LCK", "PAK1", "PAK4", "MAPK14"]


def load_binders():
    gd = json.loads((ROOT / "GATE_DECISION.json").read_text())
    return gd.get("binders", [])


def build_panel_yamls(binders, yaml_dir):
    yaml_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for i, b in enumerate(binders):
        smi_yaml = b["smiles"].replace("\\", "\\\\").replace('"', '\\"')
        for kinase in PANEL:
            seq = KINASE_SEQS[kinase]
            jid = f"PANEL_{b['strategy']}_{i:03d}_{kinase}"
            yaml_text = (
                "version: 1\n"
                "sequences:\n"
                "  - protein:\n"
                "      id: A\n"
                f"      sequence: {seq}\n"
                "      msa: empty\n"
                "  - ligand:\n"
                "      id: L1\n"
                f'      smiles: "{smi_yaml}"\n'
            )
            (yaml_dir / f"{jid}.yaml").write_text(yaml_text)
            manifest.append({
                "job_id": jid,
                "binder_idx": i,
                "binder_smiles": b["smiles"],
                "binder_strategy": b["strategy"],
                "binder_job_id": b["job_id"],
                "kinase": kinase,
            })
    return manifest


def run_boltz_panel(yaml_dir):
    subprocess.run(
        ["ssh", BOLTZ_HOST, f"mkdir -p {REMOTE_IN} {REMOTE_OUT}; find {REMOTE_IN} -mindepth 1 -delete 2>/dev/null; find {REMOTE_OUT} -mindepth 1 -delete 2>/dev/null; true"],
        check=False,
    )
    r = subprocess.run(
        ["rsync", "-az", str(yaml_dir) + "/", f"{BOLTZ_HOST}:{REMOTE_IN}/"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"rsync panel yamls: {r.stderr}"
    # Use the plain boltz CLI (no affinity head — we just need iptm)
    cmd = (
        f"/home/shadeform/miniconda3/envs/pxm_cu128/bin/boltz predict {REMOTE_IN} "
        f"--out_dir {REMOTE_OUT} --cache /home/shadeform/.boltz_cache --model boltz2 "
        "--recycling_steps 1 --sampling_steps 25 "
        "--accelerator gpu --devices 1 --diffusion_samples 1 "
        "--output_format pdb --num_workers 0 --override"
    )
    t0 = time.time()
    print(f"running boltz panel ({time.strftime('%FT%TZ', time.gmtime())}) ...")
    r = subprocess.run(
        ["ssh", BOLTZ_HOST, cmd],
        capture_output=True, text=True, timeout=14400,
    )
    print(f"elapsed={time.time()-t0:.1f}s rc={r.returncode}")
    if r.returncode != 0:
        print("STDERR tail:", r.stderr[-1500:])
    return r.returncode == 0


def fetch_and_parse(manifest, local_out):
    local_out.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "rsync", "-az",
        "--include", "*/",
        "--include", "confidence_*.json",
        "--exclude", "*",
        f"{BOLTZ_HOST}:{REMOTE_OUT}/",
        str(local_out) + "/",
    ])
    raw = []
    for r in manifest:
        jid = r["job_id"]
        conf_files = list(Path(local_out).rglob(f"confidence_{jid}_*.json"))
        rec = dict(r)
        if conf_files:
            cj = json.loads(conf_files[0].read_text())
            rec["iptm"] = cj.get("iptm", cj.get("complex_iptm"))
            rec["ptm"] = cj.get("ptm")
            rec["plddt"] = cj.get("complex_plddt")
        else:
            rec["iptm"] = None
        raw.append(rec)
    return raw


def compute_zscore_gates(raw):
    """Group by binder, compute z-scores across kinases."""
    by_binder = {}
    for r in raw:
        bi = r["binder_idx"]
        by_binder.setdefault(bi, {"smiles": r["binder_smiles"], "strategy": r["binder_strategy"],
                                   "binder_job_id": r["binder_job_id"], "iptm": {}})
        if r["iptm"] is not None:
            by_binder[bi]["iptm"][r["kinase"]] = r["iptm"]

    out = []
    for bi, b in sorted(by_binder.items()):
        iptm = b["iptm"]
        if "LIMK2" not in iptm:
            continue
        all_vals = list(iptm.values())
        if len(all_vals) < 8:  # need enough for stats
            continue
        mean_all = sum(all_vals) / len(all_vals)
        sd_all = (sum((v - mean_all) ** 2 for v in all_vals) / len(all_vals)) ** 0.5
        off_vals = [iptm[k] for k in iptm if k != "LIMK2"]
        mean_off = sum(off_vals) / len(off_vals)
        sd_off = (sum((v - mean_off) ** 2 for v in off_vals) / len(off_vals)) ** 0.5
        z_limk2 = (iptm["LIMK2"] - mean_all) / sd_all if sd_all > 1e-6 else 0.0
        sel_z = (iptm["LIMK2"] - mean_off) / sd_off if sd_off > 1e-6 else 0.0
        out.append({
            "binder_idx": bi,
            "binder_job_id": b["binder_job_id"],
            "strategy": b["strategy"],
            "smiles": b["smiles"],
            "iptm_LIMK2": iptm["LIMK2"],
            "mean_iptm_all": mean_all,
            "sd_iptm_all": sd_all,
            "mean_iptm_off": mean_off,
            "sd_iptm_off": sd_off,
            "z_LIMK2": z_limk2,
            "sel_z": sel_z,
            "n_kinases_ok": len(all_vals),
            **{f"iptm_{k}": iptm.get(k) for k in PANEL},
        })
    return out


def main():
    print("=== LIMK2 Arm 1 — 15-kinase selectivity panel ===")
    binders = load_binders()
    print(f"Input binders (affinity prob > 0.3): {len(binders)}")
    if not binders:
        print("No binders to panel. Exit.")
        return 0

    yaml_dir = ROOT / "panel_yaml"
    manifest = build_panel_yamls(binders, yaml_dir)
    (ROOT / "panel_manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"Wrote {len(manifest)} panel YAMLs ({len(binders)} compounds × {len(PANEL)} kinases)")

    ok = run_boltz_panel(yaml_dir)
    if not ok:
        print("Boltz panel run FAILED")
        return 1

    raw = fetch_and_parse(manifest, ROOT / "panel_boltz_out")
    with open(ROOT / "kinase_panel_raw.jsonl", "w") as f:
        for r in raw:
            f.write(json.dumps(r) + "\n")

    z_records = compute_zscore_gates(raw)
    z_records.sort(key=lambda r: (-r["sel_z"], -r["z_LIMK2"]))

    csv_path = ROOT / "kinase_panel_ranked.csv"
    if z_records:
        keys = list(z_records[0].keys())
        with open(csv_path, "w") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(z_records)

    passing = [r for r in z_records if r["z_LIMK2"] > 0 and r["sel_z"] > 0]
    print(f"\n=== Z-gate results ===")
    print(f"Total compounds panelled: {len(z_records)}")
    print(f"Pass z_LIMK2 > 0 AND sel_z > 0: {len(passing)}")
    for r in passing[:20]:
        print(f"  {r['binder_job_id']}: z_LIMK2={r['z_LIMK2']:.2f}, sel_z={r['sel_z']:.2f}, iptm_LIMK2={r['iptm_LIMK2']:.3f}")

    (ROOT / "SELECTIVITY_GATE.json").write_text(json.dumps({
        "gate": "z_LIMK2 > 0 AND sel_z > 0",
        "n_panelled": len(z_records),
        "n_passing": len(passing),
        "passing": passing,
        "all_ranked": z_records,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

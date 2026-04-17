"""LIMK2 Arm 1 Redesign — Filter + affinity scoring cascade.

Steps per task spec:
1. Collect SDFs from all 3 campaigns (A/B/C)
2. RDKit validity + uniqueness (canonical SMILES)
3. Lipinski Ro5 + QED >= 0.4 + BBB >= 0.5 + (A/C only: HBD 2-4)
4. Strategy B tag: Tanimoto vs LIMKi3 (PDB ligand 35H) >= 0.3
5. Build Boltz-2 affinity YAMLs (all survivors)
6. Run Boltz-2 affinity head on sma-h100-two
7. Parse affinity_pred_value → calibrated Ki_nM (slope/intercept from fits.json)
8. Apply gate: affinity_probability_binary > 0.3
9. Report survivors

Written into: /home/bryza/sma-research/qms/limk2_arm1_redesign/
Outputs:
  - survivors_filtered.csv (pre-Boltz)
  - affinity_rescored.json (post-Boltz)
  - GATE_DECISION.json
"""
import csv
import json
import math
import subprocess
import sys
import time
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, QED, rdMolDescriptors
from rdkit import DataStructs

ROOT = Path("/home/bryza/sma-research/qms/limk2_arm1_redesign")
REMOTE_HOST = "root@ssh2.vast.ai"
REMOTE_PORT = "21610"
REMOTE_KEY = str(Path.home() / ".ssh/id_ed25519_vastai")
BOLTZ_HOST = "sma-h100-two"
FITS = json.loads(Path("/home/bryza/sma-research/qms/chembl_ki_affinity_head/fits.json").read_text())
LIMK2_SEQ = json.loads(Path("/home/bryza/sma-research/qms/chembl_ki_calibration/kinase_sequences.json").read_text())["LIMK2"]["seq"]

# LIMKi3 (35H from PDB 4TPT) canonical SMILES — from PDB chemical dictionary
LIMKI3_SMILES = "C[C@@H](c1ccc(NC(=O)c2ccccc2)cc1)[C@H](O)CO"  # 35H in RCSB
LIMKI3_SCAFFOLD = "c1ccc2c(c1)ncn2"  # imidazopyridine (user-supplied fragment seed)


def fetch_sdfs_from_asxm():
    """Rsync SDFs from asxm (after PXM runs) back to WSL."""
    local_gen = ROOT / "generated"
    local_gen.mkdir(exist_ok=True)
    for sub in ("A", "B", "C"):
        (local_gen / f"strategy_{sub}").mkdir(exist_ok=True)
        remote_path = f"/root/results_limk2_arm1/generated_{sub}/"
        cmd = [
            "rsync", "-az",
            "-e", f"ssh -i {REMOTE_KEY} -p {REMOTE_PORT}",
            f"{REMOTE_HOST}:{remote_path}",
            str(local_gen / f"strategy_{sub}") + "/",
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"WARN: rsync strategy {sub}: {r.stderr[:200]}")
    return local_gen


def read_sdf_mols(sdf_dir, strategy_tag):
    """Walk an SDF directory; return list of (filename, mol, strategy_tag).
    PXM sample_use output layout:
      <outdir>/<runname>/<runname>_SDF/N.sdf                  = final generated molecule
      <outdir>/<runname>/<runname>_SDF/N-bad.sdf             = failed reconstruction (skip)
      <outdir>/<runname>/<runname>_SDF/N-all.sdf             = trajectory frames (skip)
      <outdir>/<runname>/<runname>_SDF/N-out.sdf             = intermediate (skip)
      <outdir>/<runname>/<runname>_SDF/N-in.sdf              = input state (skip)
      <outdir>/<runname>/<runname>_SDF/N-raw.sdf             = raw pre-refinement (skip)
      <outdir>/<runname>/<runname>_SDF/N_inputs/             = input ref subdir (skip)
    Only accept filenames that are pure integers + .sdf
    """
    import re
    keep_pattern = re.compile(r"^\d+\.sdf$")
    mols = []
    for sdf in Path(sdf_dir).rglob("*.sdf"):
        if not keep_pattern.match(sdf.name):
            continue
        # Skip if under an _inputs subdir
        if "_inputs" in sdf.parts:
            continue
        try:
            supplier = Chem.SDMolSupplier(str(sdf), sanitize=True, removeHs=False)
            for m in supplier:
                if m is None:
                    continue
                mols.append((sdf.name, m, strategy_tag))
        except Exception:
            continue
    return mols


def rdkit_filter(mols):
    """Canonicalize, dedup, return list of dicts."""
    seen = set()
    out = []
    for fn, m, tag in mols:
        try:
            smi = Chem.MolToSmiles(m, canonical=True)
            if not smi or smi in seen:
                continue
            seen.add(smi)
            mw = Descriptors.MolWt(m)
            logp = Descriptors.MolLogP(m)
            tpsa = Descriptors.TPSA(m)
            hbd = rdMolDescriptors.CalcNumHBD(m)
            hba = rdMolDescriptors.CalcNumHBA(m)
            qed = QED.qed(m)
            out.append({
                "filename": fn, "strategy": tag, "smiles": smi,
                "MW": mw, "logP": logp, "TPSA": tpsa, "HBD": hbd, "HBA": hba, "QED": qed,
            })
        except Exception:
            continue
    return out


def bbb_score(smi):
    """BOILED-Egg-style BBB probability proxy: TPSA + logP logistic.
    Reference: SwissADME BBB prediction from TPSA<79 AND WLogP<5.88.
    We use a sigmoid around TPSA 90 / logP [0, 5].
    """
    m = Chem.MolFromSmiles(smi)
    if m is None:
        return 0.0
    logp = Descriptors.MolLogP(m)
    tpsa = Descriptors.TPSA(m)
    # Egan BBB ellipse-inspired logistic
    # BBB+ if TPSA<90 and 0<logP<5
    if tpsa > 140 or logp < -2 or logp > 7:
        return 0.0
    # Simple logistic
    p = 1 / (1 + math.exp((tpsa - 90) / 15)) * 1 / (1 + math.exp(-(logp - 0.5) / 1.0)) * 1 / (1 + math.exp((logp - 5) / 0.8))
    return max(0.0, min(1.0, p))


def lipinski_ro5(rec):
    return (rec["MW"] <= 500 and rec["logP"] <= 5 and rec["HBD"] <= 5 and rec["HBA"] <= 10)


def tanimoto_vs_limki3(smi):
    m = Chem.MolFromSmiles(smi)
    ref = Chem.MolFromSmiles(LIMKI3_SMILES)
    if m is None or ref is None:
        return None
    fp_m = AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=2048)
    fp_r = AllChem.GetMorganFingerprintAsBitVect(ref, 2, nBits=2048)
    return DataStructs.TanimotoSimilarity(fp_m, fp_r)


def apply_filters(records):
    """Apply filter cascade. Returns (passed, filter_log)."""
    total = len(records)
    lipinski = [r for r in records if lipinski_ro5(r)]
    qed_pass = [r for r in lipinski if r["QED"] >= 0.4]
    for r in qed_pass:
        r["BBB"] = bbb_score(r["smiles"])
        r["tanimoto_limki3"] = tanimoto_vs_limki3(r["smiles"])
    bbb_pass = [r for r in qed_pass if r["BBB"] >= 0.5]
    # Strategy-specific:
    # A & C: HBD within 2-4 (activator H-bond with Asp carboxylate)
    # B: Tanimoto vs LIMKi3 >= 0.3
    survivors = []
    for r in bbb_pass:
        s = r["strategy"]
        if s in ("A", "C"):
            if 2 <= r["HBD"] <= 4:
                survivors.append(r)
        elif s == "B":
            if r["tanimoto_limki3"] is not None and r["tanimoto_limki3"] >= 0.3:
                survivors.append(r)
    log = {
        "total_generated": total,
        "after_lipinski": len(lipinski),
        "after_QED_0.4": len(qed_pass),
        "after_BBB_0.5": len(bbb_pass),
        "after_strategy_specific": len(survivors),
        "by_strategy": {
            "A": sum(1 for r in survivors if r["strategy"] == "A"),
            "B": sum(1 for r in survivors if r["strategy"] == "B"),
            "C": sum(1 for r in survivors if r["strategy"] == "C"),
        },
    }
    return survivors, log


def build_boltz_yamls(survivors, out_dir):
    """Write one YAML per survivor for Boltz-2 affinity head run."""
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for i, r in enumerate(survivors):
        smi = r["smiles"].replace("\\", "\\\\").replace('"', '\\"')
        jid = f"LIMK2_ARM1_REDESIGN_{r['strategy']}_{i:03d}"
        yaml_text = (
            "version: 1\n"
            "sequences:\n"
            "  - protein:\n"
            "      id: A\n"
            f"      sequence: {LIMK2_SEQ}\n"
            "      msa: empty\n"
            "  - ligand:\n"
            "      id: L1\n"
            f'      smiles: "{smi}"\n'
            "properties:\n"
            "  - affinity:\n"
            "      binder: L1\n"
        )
        (out_dir / f"{jid}.yaml").write_text(yaml_text)
        r["job_id"] = jid
        manifest.append({"job_id": jid, **{k: v for k, v in r.items() if k != "filename"}})
    return manifest


def run_boltz_affinity(yaml_dir, remote_in, remote_out):
    """Sync YAMLs to boltz host, run boltz predict, sync results back."""
    subprocess.run(
        ["ssh", BOLTZ_HOST, f"mkdir -p {remote_in} {remote_out}; find {remote_in} -mindepth 1 -delete 2>/dev/null; find {remote_out} -mindepth 1 -delete 2>/dev/null; true"],
        check=False,
    )
    r = subprocess.run(
        ["rsync", "-az", str(yaml_dir) + "/", f"{BOLTZ_HOST}:{remote_in}/"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"rsync YAMLs: {r.stderr}"
    cmd = (
        f"/home/shadeform/miniconda3/envs/pxm_cu128/bin/boltz predict {remote_in} "
        f"--out_dir {remote_out} --cache /home/shadeform/.boltz_cache --model boltz2 "
        "--recycling_steps 1 --sampling_steps 25 "
        "--sampling_steps_affinity 100 --diffusion_samples_affinity 3 "
        "--accelerator gpu --devices 1 --diffusion_samples 1 "
        "--output_format pdb --num_workers 0 --override"
    )
    t0 = time.time()
    print(f"running boltz...")
    r = subprocess.run(
        ["ssh", BOLTZ_HOST, cmd],
        capture_output=True, text=True, timeout=7200,
    )
    print(f"elapsed={time.time()-t0:.1f}s rc={r.returncode}")
    if r.returncode != 0:
        print("STDERR tail:", r.stderr[-1500:])
    return r.returncode == 0


def fetch_boltz_results(remote_out, local_out):
    local_out.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([
        "rsync", "-az",
        "--include", "*/",
        "--include", "affinity_*.json",
        "--include", "confidence_*.json",
        "--exclude", "*",
        f"{BOLTZ_HOST}:{remote_out}/",
        str(local_out) + "/",
    ])
    return r.returncode == 0


def parse_affinity_results(manifest, local_out):
    fit = FITS["LIMK2"]
    rmse = fit["rmse_log10_ki"]
    results = []
    for r in manifest:
        jid = r["job_id"]
        aff_files = list(Path(local_out).rglob(f"affinity_{jid}.json"))
        conf_files = list(Path(local_out).rglob(f"confidence_{jid}_*.json"))
        rec = dict(r)
        if aff_files:
            aj = json.loads(aff_files[0].read_text())
            rec["affinity_pred_value"] = aj.get("affinity_pred_value")
            rec["affinity_probability_binary"] = aj.get("affinity_probability_binary")
            if rec["affinity_pred_value"] is not None:
                pred_log10_ki = fit["slope"] * rec["affinity_pred_value"] + fit["intercept"]
                rec["pred_log10_ki_nM"] = float(pred_log10_ki)
                rec["pred_ki_nM"] = float(10 ** pred_log10_ki)
                rec["ki_95pi_nM"] = [
                    float(10 ** (pred_log10_ki - 1.96 * rmse)),
                    float(10 ** (pred_log10_ki + 1.96 * rmse)),
                ]
            else:
                rec["pred_log10_ki_nM"] = None
                rec["pred_ki_nM"] = None
                rec["ki_95pi_nM"] = None
        else:
            rec["affinity_pred_value"] = None
            rec["affinity_probability_binary"] = None
            rec["pred_log10_ki_nM"] = None
            rec["pred_ki_nM"] = None
            rec["ki_95pi_nM"] = None
        if conf_files:
            cj = json.loads(conf_files[0].read_text())
            rec["iptm"] = cj.get("iptm", cj.get("complex_iptm"))
        else:
            rec["iptm"] = None
        results.append(rec)
    return results


def gate_decision(results):
    """Apply gates:
    - affinity_probability_binary > 0.3 (binary binder)
    Returns survivors + decision summary.
    """
    binders = [r for r in results if (r.get("affinity_probability_binary") or 0) > 0.3]
    binders.sort(key=lambda r: r.get("pred_ki_nM") or 9e9)
    return binders


def main():
    print("=== LIMK2 Arm 1 Redesign — filter + score cascade ===")
    print("Step 1: fetch SDFs from asxm")
    gen_dir = fetch_sdfs_from_asxm()

    print("Step 2: read SDFs")
    mols = []
    for sub in ("A", "B", "C"):
        sub_dir = gen_dir / f"strategy_{sub}"
        sub_mols = read_sdf_mols(sub_dir, sub)
        print(f"  Strategy {sub}: {len(sub_mols)} mols")
        mols.extend(sub_mols)
    print(f"Total raw: {len(mols)}")

    print("Step 3: RDKit filter (uniqueness, descriptors)")
    records = rdkit_filter(mols)
    print(f"Unique RDKit-valid: {len(records)}")

    print("Step 4: apply filter cascade")
    survivors, flog = apply_filters(records)
    print(f"Survivors by strategy: {flog['by_strategy']}")
    print(f"Total survivors for Boltz-2 affinity: {len(survivors)}")

    # Write pre-boltz CSV
    pre_csv = ROOT / "survivors_filtered.csv"
    if survivors:
        keys = list(survivors[0].keys())
        with open(pre_csv, "w") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(survivors)
    (ROOT / "filter_log.json").write_text(json.dumps(flog, indent=2))

    if not survivors:
        print("NO SURVIVORS AFTER FILTER CASCADE. GATE: FAIL.")
        (ROOT / "GATE_DECISION.json").write_text(json.dumps({
            "gate": "pre_boltz_filter",
            "decision": "FAIL",
            "n_survivors": 0,
            "filter_log": flog,
        }, indent=2))
        return 1

    print("Step 5: build Boltz-2 affinity YAMLs")
    yaml_dir = ROOT / "affinity_yaml"
    manifest = build_boltz_yamls(survivors, yaml_dir)
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2))

    print(f"Step 6: run Boltz-2 on {BOLTZ_HOST} ({len(manifest)} YAMLs)")
    remote_in = "/home/shadeform/limk2_arm1_redesign/in"
    remote_out = "/home/shadeform/limk2_arm1_redesign/out"
    ok = run_boltz_affinity(yaml_dir, remote_in, remote_out)
    if not ok:
        print("Boltz run FAILED")
        return 1

    print("Step 7: fetch + parse results")
    local_out = ROOT / "boltz_out"
    fetch_boltz_results(remote_out, local_out)
    results = parse_affinity_results(manifest, local_out)
    (ROOT / "affinity_rescored.json").write_text(json.dumps(results, indent=2))

    print("Step 8: gate decision")
    binders = gate_decision(results)
    print(f"Binary-binder gate (prob>0.3) survivors: {len(binders)}")
    for b in binders[:20]:
        ki = b.get("pred_ki_nM")
        pb = b.get("affinity_probability_binary")
        ki_s = f"{ki:.1f}nM" if ki is not None else "NA"
        print(f"  {b['strategy']} {b['job_id']}: Ki={ki_s} prob_bin={pb:.3f} QED={b['QED']:.2f} BBB={b['BBB']:.2f}")

    (ROOT / "GATE_DECISION.json").write_text(json.dumps({
        "gate": "affinity_binary_prob_gt_0.3",
        "n_boltz_scored": len(results),
        "n_binders": len(binders),
        "binders": binders,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

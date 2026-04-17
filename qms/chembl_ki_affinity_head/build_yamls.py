"""Build 80 affinity-enabled Boltz-2 YAML inputs from existing calibration rows.

Uses kinase_sequences.json for the KD sequence (same sequences as the iptm calibration,
so the comparison is apples-to-apples) and the 20 SMILES per kinase from
raw/<kinase>_calibration_rows.json.

Output: /home/bryza/sma-research/qms/chembl_ki_affinity_head/yaml_in/<kinase>_<idx>.yaml
Each YAML contains `properties: - affinity: binder: L1` to trigger the affinity head.
"""
import json
from pathlib import Path

CALIB_DIR = Path("/home/bryza/sma-research/qms/chembl_ki_calibration")
OUT_DIR = Path("/home/bryza/sma-research/qms/chembl_ki_affinity_head/yaml_in")
RAW_DIR = Path("/home/bryza/sma-research/qms/chembl_ki_affinity_head/raw")

seqs = json.loads((CALIB_DIR / "kinase_sequences.json").read_text())

manifest = []
for kinase in ["LIMK2", "ROCK2", "JAK2", "MAPK14"]:
    rows = json.loads((CALIB_DIR / "raw" / f"{kinase}_calibration_rows.json").read_text())
    kd_seq = seqs[kinase]["seq"]
    for idx, r in enumerate(rows):
        smi = r["smiles"]
        ki_nM = r["ki_nM"]
        log10_ki = r["log10_ki_nM"]
        prior_iptm = r["iptm"]
        # Escape the SMILES for YAML — use double quotes, backslash-escape embedded quotes
        smi_yaml = smi.replace("\\", "\\\\").replace('"', '\\"')
        job_id = f"{kinase}_{idx:02d}"
        yaml_text = (
            "version: 1\n"
            "sequences:\n"
            "  - protein:\n"
            "      id: A\n"
            f"      sequence: {kd_seq}\n"
            "      msa: empty\n"
            "  - ligand:\n"
            "      id: L1\n"
            f'      smiles: "{smi_yaml}"\n'
            "properties:\n"
            "  - affinity:\n"
            "      binder: L1\n"
        )
        (OUT_DIR / f"{job_id}.yaml").write_text(yaml_text)
        manifest.append({
            "job_id": job_id,
            "kinase": kinase,
            "idx": idx,
            "smiles": smi,
            "ki_nM": ki_nM,
            "log10_ki_nM": log10_ki,
            "prior_iptm": prior_iptm,
        })

(RAW_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2))
print(f"Built {len(manifest)} YAMLs in {OUT_DIR}")
print(f"Manifest: {RAW_DIR / 'manifest.json'}")

"""Build Boltz-2 affinity YAMLs for the FULL ROCK2-alphaC PocketXMol library (241 compounds).

Input: /home/bryza/fleet-results/rock2_activator_alphaC/pxm_smiles_raw.csv (241 unique SMILES)
Output: /home/bryza/sma-research/qms/rock2_affinity_rerun/yaml_in/ROCK2_<id>.yaml

ROCK2 sequence (UniProt O75116 kinase domain) — SAME sequence used by the ae345009
chembl_ki_affinity_head calibration campaign. Calibration fit:
  slope=0.880, intercept=2.960, r2=0.528, rmse=0.693 log10(Ki_nM).

Scientific rationale: prior rescore_leads.py ran only 10 top compounds. The 241-library
pipeline audit (af9c9a90) flagged SMA-Score 0/241 pass, but that anchor set is biased to
ATP-site kinase inhibitors. The honest retraction criterion is the Boltz-2 affinity head
(R² 0.53 vs Ki for ROCK2) calibrated to nM Ki, gate `affinity_probability_binary > 0.3`.

Parallel to LIMK2 retraction (Incident 2026-04-17-005) pattern.
"""
import csv
import json
from pathlib import Path

ROOT = Path("/home/bryza/sma-research/qms/rock2_affinity_rerun")
YAML_DIR = ROOT / "yaml_in"
YAML_DIR.mkdir(parents=True, exist_ok=True)

# ROCK2 sequence — same calibration target from chembl_ki_affinity_head
KSEQ_PATH = Path("/home/bryza/sma-research/qms/chembl_ki_calibration/kinase_sequences.json")
seqs = json.loads(KSEQ_PATH.read_text())
ROCK2_SEQ = seqs["ROCK2"]["seq"]
print(f"ROCK2 sequence length: {len(ROCK2_SEQ)}")

# Load ALL 241 compounds from pxm_smiles_raw (full library, not BBB-filtered)
SRC = Path("/home/bryza/fleet-results/rock2_activator_alphaC/pxm_smiles_raw.csv")
compounds = []
with SRC.open() as f:
    r = csv.DictReader(f)
    for row in r:
        smi = row["smiles"].strip()
        fname = row["filename"].strip()
        if not smi or not fname:
            continue
        compounds.append({
            "id": Path(fname).stem,  # e.g. "0" from "0.sdf"
            "smiles": smi,
            "filename": fname,
            "qed": float(row.get("qed") or 0) or None,
            "mw": float(row.get("mw") or 0) or None,
            "logp": float(row.get("logp") or 0) or None,
            "tpsa": float(row.get("tpsa") or 0) or None,
            "hbd": int(row.get("hbd") or 0) or None,
            "bbb_heuristic": row.get("bbb_heuristic") == "True",
            "ro5_pass": row.get("ro5_pass") == "True",
        })

print(f"Loaded {len(compounds)} compounds from pxm_smiles_raw.csv")

# Deduplicate by canonical SMILES (keep first filename)
seen = {}
for c in compounds:
    if c["smiles"] not in seen:
        seen[c["smiles"]] = c
compounds = list(seen.values())
print(f"After dedup: {len(compounds)} unique SMILES")

# Build YAMLs
for c in compounds:
    jid = f"ROCK2_{c['id']}"
    smi_esc = c["smiles"].replace("\\", "\\\\").replace('"', '\\"')
    yaml_text = (
        "version: 1\n"
        "sequences:\n"
        "  - protein:\n"
        "      id: A\n"
        f"      sequence: {ROCK2_SEQ}\n"
        "      msa: empty\n"
        "  - ligand:\n"
        "      id: L1\n"
        f'      smiles: "{smi_esc}"\n'
        "properties:\n"
        "  - affinity:\n"
        "      binder: L1\n"
    )
    (YAML_DIR / f"{jid}.yaml").write_text(yaml_text)

print(f"Wrote {len(compounds)} YAMLs -> {YAML_DIR}")

# Save manifest
manifest = {"compounds": compounds, "rock2_seq_len": len(ROCK2_SEQ), "n_compounds": len(compounds)}
(ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2))
print("manifest.json written")

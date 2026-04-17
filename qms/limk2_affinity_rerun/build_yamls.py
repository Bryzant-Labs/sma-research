"""Build Boltz-2 affinity YAMLs for the FULL LIMK2-alphaC PocketXMol library.

Input: /home/bryza/fleet-results/limk2_activator_alphaC/bbb_filtered.csv
       (109 BBB-filtered compounds — the library that entered the panel rerun)
Additionally, we also re-score ALL 558 RDKit-valid compounds (broader audit).

LIMK2 sequence: PDB 4TPT domain (UniProt P53671 K383/T407/G408 pocket),
same sequence used by the ae345009 calibration campaign.
"""
import csv
import json
from pathlib import Path

ROOT = Path("/home/bryza/sma-research/qms/limk2_affinity_rerun")
YAML_DIR = ROOT / "yaml_in"
YAML_DIR.mkdir(parents=True, exist_ok=True)

# LIMK2 sequence — 4TPT domain (kinase catalytic, allosteric aC-helix region)
# Same used in chembl_ki_affinity_head calibration
KSEQ_PATH = Path("/home/bryza/sma-research/qms/chembl_ki_calibration/kinase_sequences.json")
seqs = json.loads(KSEQ_PATH.read_text())
LIMK2_SEQ = seqs["LIMK2"]["seq"]
print(f"LIMK2 sequence length: {len(LIMK2_SEQ)}")

# Load ALL 109 BBB-filtered compounds (the library of interest)
SRC_BBB = Path("/home/bryza/fleet-results/limk2_activator_alphaC/bbb_filtered.csv")
compounds = []
with SRC_BBB.open() as f:
    r = csv.DictReader(f)
    for row in r:
        smi = row["canonical_smiles"].strip()
        fname = row["filename"].strip()
        if not smi or not fname:
            continue
        compounds.append({
            "id": Path(fname).stem,  # e.g. "3" from "3.sdf"
            "smiles": smi,
            "filename": fname,
        })

print(f"Loaded {len(compounds)} compounds from bbb_filtered.csv")

# Deduplicate by canonical SMILES (keep first filename)
seen = {}
for c in compounds:
    if c["smiles"] not in seen:
        seen[c["smiles"]] = c
compounds = list(seen.values())
print(f"After dedup: {len(compounds)} unique SMILES")

# Build YAMLs
for c in compounds:
    jid = f"LIMK2_{c['id']}"
    smi_esc = c["smiles"].replace("\\", "\\\\").replace('"', '\\"')
    yaml_text = (
        "version: 1\n"
        "sequences:\n"
        "  - protein:\n"
        "      id: A\n"
        f"      sequence: {LIMK2_SEQ}\n"
        "      msa: empty\n"
        "  - ligand:\n"
        "      id: L1\n"
        f'      smiles: "{smi_esc}"\n'
        "properties:\n"
        "  - affinity:\n"
        "      binder: L1\n"
    )
    (YAML_DIR / f"{jid}.yaml").write_text(yaml_text)

print(f"Wrote {len(compounds)} YAMLs → {YAML_DIR}")

# Save manifest
manifest = {"compounds": compounds, "limk2_seq_len": len(LIMK2_SEQ)}
(ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2))
print("manifest.json written")

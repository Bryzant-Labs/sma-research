"""15-kinase selectivity panel — kinase-domain subsets for Boltz-2 speed.
Boundaries from UniProt / InterPro / ProSite kinase domain annotations."""
import json
from pathlib import Path

# (name, uniprot_acc, kinase_domain_start, kinase_domain_end)
# 1-indexed inclusive. ~250-310 aa each, fast Boltz-2 inference.
PANEL = {
    "LIMK1":  ("P53667", 330, 604),   # LIM-K1 kinase
    "LIMK2":  ("P53671", 330, 603),   # LIM-K2 kinase
    "ROCK1":  ("Q13464", 76,  354),   # Rho-associated protein kinase 1
    "ROCK2":  ("O75116", 92,  354),   # Rho-associated protein kinase 2
    "JAK1":   ("P23458", 875, 1155),  # JH1 catalytic
    "JAK2":   ("O60674", 849, 1132),  # JH1 catalytic
    "JAK3":   ("P52333", 822, 1124),  # JH1 catalytic
    "CDK2":   ("P24941", 1,   298),   # CDK2 full (mostly kinase)
    "CDK5":   ("Q00535", 1,   292),   # CDK5 full
    "SRC":    ("P12931", 270, 523),   # SRC catalytic
    "FYN":    ("P06241", 275, 530),   # FYN catalytic
    "LCK":    ("P06239", 248, 500),   # LCK catalytic
    "PAK1":   ("Q13153", 270, 524),   # PAK1 catalytic
    "PAK4":   ("O96013", 320, 590),   # PAK4 catalytic
    "MAPK14": ("Q16539", 1,   360),   # p38α full
}

def get_panel():
    """Return {kinase_name: sequence_of_kinase_domain}"""
    full = json.load(open("/home/bryza/fleet-results/kinase_panel_seqs.json"))
    out = {}
    for name, (acc, start, end) in PANEL.items():
        if name not in full: continue
        seq = full[name]
        # 1-indexed → 0-indexed slice
        kd = seq[start-1:end]
        out[name] = kd
    return out

if __name__ == "__main__":
    panel = get_panel()
    Path("/home/bryza/fleet-results/kinase_panel_domains.json").write_text(json.dumps(panel, indent=2))
    for n, s in panel.items():
        print(f"  {n}: {len(s)} aa (kinase domain)")
    print(f"saved {len(panel)} kinase-domain sequences")

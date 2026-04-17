# CDK5 Allosteric Activator Campaign — Pre-Flight Plan

**Status:** DRAFT (pre-flight)
**Date:** 2026-04-17
**Campaign ID:** `cdk5_activator_p25iface`
**Author:** Claude (Opus 4.7), dispatched by architect
**Exploratory level:** HIGH — no published small-molecule CDK5 allosteric activator exists.
Treat all results as exploratory compute; do not overclaim therapeutic value.

## Biological Rationale

CDK5 (UniProt Q00535, 292 aa) is unique among CDKs: it has **no cyclin dependency**.
Instead, CDK5 catalytic activity requires binding to an activator protein:
- **p35** (physiological, CDK5R1 gene product)
- **p25** (pathological, calpain-cleaved p35 fragment, implicated in Alzheimer's)

CDK5 regulates the neuronal cytoskeleton. Key for SMA:
- CDK5 phosphorylates **cofilin at S3** — same residue as LIMK2. This is the actin-severing
  switch point in the ROCK/LIMK/cofilin axis.
- CDK5 also phosphorylates tau, MAP1B, neurofilaments, and regulates actin dynamics
  via Rac1/Pak.

### SMA-relevance and the direction question

Today's 3-dataset LIMK2 meta-analysis showed LIMK2 **DOWN** in Hb9-iMN / organoid SMA
systems. If the cytoskeletal axis is under-active in SMA motor neurons, **enhancing**
cofilin-S3 phosphorylation could compensate for the LIMK2 LoF. CDK5 activation is one
way to hit the same target residue through a parallel enzyme.

**Caveat — this is a hypothesis with no direct published evidence.**
- No published SMA dataset shows CDK5 dysregulation as a driver.
- No CDK5 allosteric activator exists as a clinical tool.
- p25 itself is pathological (Alzheimer's), so the activator must **not** mimic p25 in its
  disease-causing aspects (sustained activation, translocation).

### Why activator, not inhibitor

Canonical pharmacology develops CDK5 **inhibitors** for Alzheimer's (roscovitine, dinaciclib,
seliciclib) — the p25-bound state is hyperactive and drives tau hyperphosphorylation.
Our SMA hypothesis is the opposite direction. Therefore:
- We target the **p25-binding interface on CDK5** to find small molecules that stabilize
  the activator-bound state (or mimic its conformational effect).
- We do NOT target the ATP pocket (would yield inhibitors).
- This is first-in-class exploratory chemistry. Zero global competitors.

## Instance

| Parameter | Value |
|---|---|
| Vast contract | **35120543** |
| Host | `ssh2.vast.ai:10542` (root, key `~/.ssh/id_ed25519_vastai`) |
| GPU | 1× A100 SXM4 40 GB (Slovenia) |
| Image | `pytorch/pytorch:2.4.1-cuda12.4-cudnn9-runtime` |
| PocketXMol status | **Already installed** (ran LIMK2 ATP campaign in 2 min, completed 2026-04-17) |
| Cost | $0.6944 / hr |

## Target

| Parameter | Value | Source |
|---|---|---|
| Gene | CDK5 | UniProt Q00535 |
| PDB | **1UNH** (human CDK5/p25 kinase domain complex) | RCSB |
| CDK5 chain | A (to be verified on-instance) | 1UNH header inspection |
| p25 chain | B / D / E (to be verified on-instance) | 1UNH header inspection |
| Pocket | **p25-binding interface on CDK5** (allosteric, NOT ATP site) | CDK5/p25 contact derivation |
| Pocket center | **computed on-instance** (see derivation below) | Mean CA of CDK5 residues within 6 Å of p25 chain |
| Pocket radius | 10.0 Å | PocketXMol SBDD convention |
| Molecule count | 600 | Christian's dispatch |
| Batch size | 50 | A100 40 GB safe default (reproducible vs LIMK2 campaign) |
| Molecule-size prior | ~28 heavy atoms, σ 2, min 5 (~330 Da drug-like) | PocketXMol default |

### Pocket center derivation (on-instance Python)

Primary: structural CDK5/p25 contact residues.

```python
import numpy as np
from collections import defaultdict

# Parse all ATOM records, grouped by (chain, resi)
chains = defaultdict(list)            # (chain, resi) -> [(x,y,z,atom), ...]
chain_info = defaultdict(int)         # chain -> residue count
for L in open("1unh.pdb"):
    if L.startswith("ATOM"):
        ch = L[21]
        resi = int(L[22:26])
        atom = L[12:16].strip()
        x, y, z = float(L[30:38]), float(L[38:46]), float(L[46:54])
        chains[(ch, resi)].append((x, y, z, atom))
        chain_info[ch] += 1

# CDK5 = longer chain (~292 aa); p25 = shorter (~208 aa p35 C-terminal)
# List chain sizes to identify CDK5 vs p25
print("Chain residue counts:", dict(chain_info))

# Heuristic: largest chain by unique residues = CDK5
unique_res_per_chain = defaultdict(set)
for (ch, resi) in chains.keys():
    unique_res_per_chain[ch].add(resi)
chain_sizes = {ch: len(rs) for ch, rs in unique_res_per_chain.items()}
cdk5_ch = max(chain_sizes, key=chain_sizes.get)
p25_candidates = [ch for ch in chain_sizes if ch != cdk5_ch]
# Pick the p25 chain that is spatially closest to CDK5 if multiple
# Compute contacts: CDK5 residues with any heavy atom within 6.0 A of any p25 heavy atom
def all_atoms_of_chain(ch):
    out = []
    for (c, r), atoms in chains.items():
        if c == ch:
            for (x, y, z, a) in atoms:
                out.append((r, a, x, y, z))
    return out

cdk5_atoms = all_atoms_of_chain(cdk5_ch)
# find best p25 chain by contact count
best_p25_ch = None
best_contacts = 0
for p25_ch in p25_candidates:
    p25_atoms = all_atoms_of_chain(p25_ch)
    p_arr = np.array([[a[2], a[3], a[4]] for a in p25_atoms])
    n_cont = 0
    for (r, a, x, y, z) in cdk5_atoms:
        d = np.linalg.norm(p_arr - np.array([x, y, z]), axis=1)
        if (d < 6.0).any():
            n_cont += 1
    if n_cont > best_contacts:
        best_contacts = n_cont
        best_p25_ch = p25_ch

# Collect CDK5 residues with CA atoms that are within 6 A of any p25 heavy atom
p25_arr = np.array([[a[2], a[3], a[4]] for a in all_atoms_of_chain(best_p25_ch)])
iface_resi = set()
iface_ca_coords = []
for (c, r), atoms in chains.items():
    if c != cdk5_ch:
        continue
    has_iface_atom = False
    ca = None
    for (x, y, z, atom) in atoms:
        if atom == "CA":
            ca = (x, y, z)
        d = np.linalg.norm(p25_arr - np.array([x, y, z]), axis=1)
        if (d < 6.0).any():
            has_iface_atom = True
    if has_iface_atom and ca is not None:
        iface_resi.add(r)
        iface_ca_coords.append(ca)

if len(iface_ca_coords) == 0:
    raise SystemExit("No CDK5/p25 interface residues found — check PDB chain assignment")

center = np.array(iface_ca_coords).mean(axis=0)
print(f"CDK5 chain: {cdk5_ch} | p25 chain: {best_p25_ch}")
print(f"Interface residues (CDK5): {sorted(iface_resi)}")
print(f"Pocket center (CDK5-side mean CA): {center.tolist()}")
```

Script will be saved to `/results/cdk5_activator_p25iface/derive_pocket.py`.

### Fallback if interface residues < 8 or parse fails

Use the **PSTAIRE-like helix region of CDK5** — in canonical CDKs, cyclin binds at the
PSTAIRE helix (αC-helix of N-lobe, residues ~45–58). CDK5 has an analogous αC-helix.
I'll compute the mean CA of CDK5 residues 45–58 as the fallback anchor. This covers
the cyclin-equivalent activator-binding face of the N-lobe even if the 1UNH cocrystal
deviates from the structural expectation.

## Workflow

1. **SSH probe** — instance is warm (LIMK2 campaign just finished).
2. **Prepare campaign dir** `/results/cdk5_activator_p25iface/`.
3. **Fetch 1UNH** from RCSB.
4. **Run derivation script**, dump:
   - `chains.txt` (chain sizes)
   - `interface_residues.txt` (CDK5 iface residues)
   - `pocket_center.txt` (3 floats)
   - `derive_pocket.py` (reproducibility)
5. **Extract CDK5 chain only** (strip p25 + HETATM) → `1unh_cdk5_chainA.pdb`.
   `pocketxmol_deploy.prepare_protein()` already does HETATM strip; we must also
   pre-filter the chain to CDK5-only to prevent PocketXMol using p25 atoms as
   pocket neighbors.
6. **Write task JSON** `/results/cdk5_activator_p25iface/task.json`:
   ```json
   {
     "id": "cdk5_activator_p25iface",
     "type": "pocketxmol",
     "target": "CDK5_p25_interface_allosteric_activator",
     "pdb_id": "1UNH",
     "pocket_center": [..., ..., ...],
     "pocket_radius": 10.0,
     "n_molecules": 600,
     "batch_size": 50,
     "project": "SMA",
     "priority": 2
   }
   ```
   Also write `task_smoke.json` with `n_molecules=5, batch_size=5`.
7. **Smoke test** (5 molecules) using `pocketxmol_deploy.py --task task_smoke.json --skip-install`.
   Expected: ≤ 90 s, 5 valid SDFs, RDKit-parseable SMILES.
8. **Full launch** in tmux session `pxm_cdk5` (600 mol).
   Verify GPU util > 60% within 5 min.
9. **Rsync SMILES** to `/home/bryza/fleet-results/cdk5_activator_p25iface/`.
10. **BBB hardfilter** (drop BBB_Martins < 0.5).
11. **Queue Boltz-2 rescore** for top 100 on `sma-h100-two:8003` across panel:
    - CDK5 (primary) + **CDK2** (selectivity control — closest paralog) + CDK1, CDK7, CDK9
    - plus LIMK2, ROCK1/2, JAK2 to test cross-axis selectivity
12. **Compute Z-score selectivity per row**: `z_CDK5 = (iptm_CDK5 − row_mean) / row_std`.
    Gate: `z_CDK5 > 0` AND `selectivity_z > 0`.
13. **Write DRAFT `/home/bryza/sma-research/qms/cdk5_activator_RESULTS.md`**.
14. **`triple_llm_verify`** — 3/3 PASS before removing DRAFT status.

## Quality Gates (HARD)

| Gate | Rule | Failure action |
|---|---|---|
| Pre-flight plan written | This file exists BEFORE GPU burn | HALT GPU burn |
| Interface residue sanity | ≥ 8 CDK5 residues within 6 Å of p25 | Fallback to PSTAIRE helix residues 45–58 |
| Pocket center finite | No NaN / inf | HALT |
| Smoke test | 5 valid SDFs + extractable SMILES | HALT, debug before 600-mol burn |
| GPU util | > 60% sustained after 5 min | Debug batch_size / OOM |
| BBB hardfilter | Drop BBB < 0.5 before Boltz-2 | (filter step) |
| Selectivity metric | **Z-score per row**, NOT raw iptm margin | (HARD RULE) |
| CDK2 selectivity gate | z_CDK5 > z_CDK2 for flagged leads | Demote to secondary |
| Status stays DRAFT | Until `triple_llm_verify` 3/3 PASS | No external comms, no "therapeutic" claim |
| Exploratory framing | Explicit caveat in RESULTS.md: "no published SMA CDK5 evidence" | Reject any "validated therapy" wording |

## Contrast with LIMK2 ATP-site (same instance, prior run)

| Axis | LIMK2 ATP (ssh2 prior) | CDK5 activator (this campaign) |
|---|---|---|
| Pocket | Orthosteric ATP site | Allosteric p25-binding interface |
| Effect | INHIBITOR | ACTIVATOR |
| Pocket derivation | K360+hinge+D469 CA mean | CDK5 residues < 6 Å of p25 chain |
| Cofilin-S3 effect (desired) | Reduce (SH-SY5Y branch) | Increase (iMN branch via parallel enzyme) |
| Precedent | 100s of kinase inhibitor classes | **ZERO** published small-molecule CDK5 allosteric activators |
| Exploratory level | Moderate | **HIGH** |

## Reproducibility trail

- PocketXMol repo: `/opt/PocketXMol` (git SHA captured at `/results/limk2_atp_inhibitor/pxm_git_sha.txt`, same install)
- Weights: Zenodo record `17801271` (already resident)
- Pocket derivation: `/results/cdk5_activator_p25iface/derive_pocket.py`
- Exact YAML config: `/results/pocketxmol/cdk5_activator_p25iface/workspace/...`
- PDB source: `https://files.rcsb.org/download/1UNH.pdb`
- Deploy script: `/opt/pocketxmol_deploy.py`

## Open questions / risks

1. **Is CDK5 activation even desirable in SMA MNs?** No direct published evidence. This
   campaign is exploratory compute, not a therapeutic claim. Activation could aggravate
   tauopathy risk — document in RESULTS.md as an open risk.
2. **p25 vs p35 binding pocket difference**: 1UNH uses the calpain-cleaved p25. The p25
   binding site on CDK5 is largely identical to p35's core, but surface context differs
   at the cleavage-revealed face. Acceptable for v1 exploratory generation.
3. **CDK2 paralog selectivity** is the main pharmacological risk. Document z_CDK5 vs
   z_CDK2 and discard any hits where CDK2 > CDK5.
4. **Activator mechanism**: PocketXMol cannot distinguish "stabilizes active state" from
   "simply occupies the pocket". Follow-up MD on top 5 needed (not in this campaign's scope).
5. **ETA for 600 mol at batch 50 on A100 40 GB**: ~15–25 min expected (LIMK2 ATP-site
   run took **2 min** — likely batched larger or SBDD simple-mode is fast).
6. **Note on the LIMK2 "2 min" result**: the task brief states LIMK2 ATP campaign finished
   in 2 min which is unusually fast. Verify output counts (should be 600 SDFs). If this
   turns out to be a silent-zero failure (per `learning-completed-means-nothing-without-output-validation.md`),
   we will re-audit before trusting CDK5 output. Post-run validation: `ls /results/pocketxmol/limk2_atp_inhibitor/SDF/ | wc -l` must equal 600.

---

**PRE-FLIGHT STATUS: PLAN WRITTEN | SSH PROBE: OK (GPU idle 0%) | GPU BURN: not started**

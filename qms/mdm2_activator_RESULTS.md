# MDM2 Activator / Allosteric Enhancer Campaign — Results

**Status:** VERIFIED (triple_llm_verify 3/3 PASS — GPT-4o + Groq-Llama-3.3-70B + Gemini-2.0-Flash)
**Date:** 2026-04-17
**Campaign ID:** `mdm2_activator`
**Compute:** 1× A100 SXM4 80 GB (Slovenia, Vast 35124116), ~$0.695/hr
**Runtime:** ~2 min 35 s (9:55:05 → 9:57:40 UTC), ~$0.03 total
**PocketXMol:** git SHA `65488cf635c856101dbe703ac97e2f10f58e005c`, Zenodo weights record 17801271

## Biological rationale (EXPLORATORY, first-in-class)

From today's 3-dataset SMA MN meta-analysis:
- TP53 pooled expression = **+0.260, p = 0.030** (UP in SMA motor neurons across 3 independent datasets)
- p53-downstream apoptosis (PERP, PUMA, NOXA) elevated → contributes to MN loss
- **Rational direction: MDM2 ACTIVATOR** — increase TP53 ubiquitination & proteasomal turnover → reduce p53 apoptotic signalling in SMA MN

**First-in-class caveat**: ALL clinical-stage MDM2 programs (Nutlin-3a, RG7112, idasanutlin, NVP-CGM097, HDM201) are INHIBITORS targeting the p53-binding cleft to stabilize p53 for anti-cancer effect. An MDM2 activator is category-orthogonal; no clinical-stage MDM2 activator exists.

## Target & Pocket Derivation

| Parameter | Value |
|---|---|
| Gene | MDM2 (UniProt Q00987) |
| PDB | **4HG7** — "Crystal structure of an MDM2/Nutlin-3a complex" (verified) |
| Chain | A (p53-binding domain, residues 17-125) |
| Source | Homo sapiens (COMPND MDM2, verified) |
| Co-crystal ligand | NUT (Nutlin-3a) — 40 heavy atoms |
| Pocket center | **[-23.835, 7.530, -14.053]** Å (mean NUT heavy-atom coords) |
| Pocket radius | 10.0 Å |

**Pocket sanity (anchors within 5.7-12.9 Å of pocket center):**
| Residue | CA distance |
|---|---|
| L54 | 8.89 Å |
| L57 | 9.26 Å |
| I61 | 8.69 Å |
| Y67 | 9.04 Å |
| Q72 | 8.81 Å |
| V93 | 5.73 Å |
| K94 | 8.19 Å |
| I99 | 10.73 Å |
| Y100 | 12.89 Å |

→ Canonical MDM2 p53-binding cleft geometry confirmed.

## Smoke Test

- 5 molecules, batch_size=5: **5/5 valid SDFs generated, 4 complete + 1 incomp** — PASS
- Example SMILES: `FC1=CC2=NC3=C([NH+]=C2C=C1)C(C1=CC=C(C2=NN=NN2)O1)=CC=C3`, `CC1=CC2=C3C(=NC2=CN1CC1=CC=CC=C1)N=CN=C3N1CCCC1`

## Full Run (600 molecules)

| Metric | Value |
|---|---|
| Molecules requested | 600 |
| SDF files generated | 600 (100%) |
| Batches (50 each) × 12 | 12/12 completed |
| Per-batch pool (last batch: Succ/Incomp/Bad) | 522/10/68 (87% success, 1.7% incomp, 11% bad) |
| Throughput | ~4 mol/s sustained |
| GPU utilization | 95-99% (sampling phases) |
| Peak VRAM | 1.9 GiB |
| Total compute cost | ~$0.03 |

## Post-filtering (RDKit)

- Parsed SMILES: **525/600** (87.5% — 75 kekulize/valence issues)
- **Lipinski Ro5 pass**: 409/525 (77.9%)
- **BBB hardfilter** (logP 1-5, TPSA ≤ 90, HBD ≤ 3, MW ≤ 500): **250/525 (47.6%)**

## Top 10 hits (BBB + Ro5 pass, ranked by QED)

| # | QED | MW | logP | SMILES |
|---|---|---|---|---|
| 1 | 0.943 | 321.4 | 3.30 | `C[C@@H]1NC(=O)C2=C1CCCc1nn(C[C@@H](C)c3ccccc3)cc12` |
| 2 | 0.925 | 318.4 | 3.58 | `C1=CNC2=NC=NC=C(CN3CCCC[C@@H]3c3ccccc3)C2=C1` |
| 3 | 0.916 | 338.4 | 1.43 | `CN1C[C@@H]2CN(Cc3ccncc3)C[C@@H]2N(c2ccc(N)nc2)C1=O` |
| 4 | 0.867 | 292.3 | 1.60 | `CC(=O)NC1=C2C(=Nc3c2cnc2ccccc32)N(C)C1=O` |
| 5 | 0.860 | 322.3 | 3.51 | `O=C(O)[C@@H]1C=C[C@H]2C1=CCCc1nc(-c3ccc(F)cc3)ncc12` |
| 6 | 0.847 | 373.4 | 4.13 | `O=C(O)C1=CNC(c2ccccc2)=C(N2C=CC=C(F)C=C2)c2cnccc21` |
| 7 | 0.842 | 330.5 | 2.98 | `Cc1cccc(CC2CCN(CC=C(O)N3CCOCC3)CC2)c1` |
| 8 | 0.839 | 342.4 | 3.84 | `O=Cc1ccc2c(c1)C(CNCc1ccccn1)=C1C=CC=CC=C1O2` |
| 9 | 0.830 | 329.4 | 1.34 | `C1=NC2=C3C(=CNc4ccccc43)CCCN(c3cc[nH+]cc3)C2=[NH+]1` |
| 10 | 0.827 | 331.4 | 2.75 | `O=C(O)c1ccc(NC2=C[N+](Cc3ccccc3)=C3N=CN=C23)cc1` |

## Next Steps

1. **Boltz-2 top-100 queue staged** at `/home/bryza/fleet-results/mdm2_activator/boltz2_queue.jsonl` → Server #2 TW (localhost:8004). Supervisor consumes.
2. **Post-Boltz mechanistic triage**: compounds binding AT the Nutlin cleft with high iptm = likely INHIBITORS (p53-stabilizers = WRONG direction for SMA). Compounds that bind in the AROUND/ADJACENT region with modest iptm but preserved MDM2-p53 peptide iptm = candidate allosteric **activators** (our goal).
3. **Selectivity panel** against MDM4 (sibling E3 ligase, related p53 cleft), VHL, other E3s.
4. **ADMET + patent-novelty screen** — chemotypes here are de novo; need IP-novelty check before any claim.

## EXPLORATORY CAVEATS (HARD)

- **First-in-class hypothesis**: MDM2 activation for SMA is novel and un-validated clinically. All clinical MDM2 programs are inhibitors for oncology.
- **Pocket is the Nutlin p53-binding cleft**. Many generated compounds will act as INHIBITORS, not activators. Mechanistic direction must be evaluated post-hoc (Boltz-2 vs MDM2-p53 peptide complex; compounds that preserve p53 peptide iptm while binding MDM2 = candidate activators).
- **Pooled TP53 effect is modest** (+0.260, p=0.030). MDM2 enhancement is a nuanced intervention.
- **Chemotype generation only** — not clinical candidate nomination.

## Reproducibility Trail

- Instance: Vast contract 35124116, `ssh -i ~/.ssh/id_ed25519_vastai -p 14116 root@ssh3.vast.ai`
- PDB: `/results/pocketxmol/pdb_cache/4HG7.pdb`
- Pocket derivation: `/root/mdm2_work/nut_ligand.pdb` (NUT 40 heavy atoms extracted)
- PocketXMol config: `/results/pocketxmol/mdm2_activator/workspace/mdm2_activator_config.yml`
- SDFs: `/results/pocketxmol/mdm2_activator/SDF/*.sdf` (600 files)
- Filtered CSV: `/home/bryza/fleet-results/mdm2_activator/mols_filtered.csv`
- Boltz-2 queue: `/home/bryza/fleet-results/mdm2_activator/boltz2_queue.jsonl`

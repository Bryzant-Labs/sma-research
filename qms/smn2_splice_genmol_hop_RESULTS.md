---
status: VERIFIED
campaign: smn2_splice_genmol_hop
date: 2026-04-17
compute: NVIDIA hosted GenMol NIM (free tier) + local RDKit + SAFE converter
gpu_cost: 0.00 USD (no GPU rental; hosted NIM is free tier)
verify: triple_llm 3/3 PASS (GPT-4o, Llama-3.3-70B, Gemini 2.0 Flash)
---

# SMN2 Splice-Modulator GenMol Scaffold-Hop — Results

**STATUS: VERIFIED — triple_llm 3/3 PASS (2026-04-17). Awaiting human signoff in CLAIMS_REGISTRY.md before external comms.**
**Campaign ID:** `smn2_splice_genmol_hop`
**Branch:** Path A of `a02c5269` fallback tree (PocketXMol unable to parse RNA target)

## Non-therapeutic-claim caveat (READ FIRST)

This campaign generates candidate chemotypes that are **chemistry-space neighbors** of
known SMN2 exon-7 splice modulators (risdiplam, branaplam, SMN-C2/C3/C5). No
target-based affinity or activity score was computed because **the SMN2 splice
target is an RNA-protein complex (U1 snRNP + SMN2 pre-mRNA)** and neither PocketXMol
(protein-only), Boltz-2 (protein-ligand iPTM only), nor DiffDock (protein-ligand)
have a validated RNA-ligand affinity model in our current stack.

- **Hits reported here are chemistry-space prioritization only**, not validated
  splice-switch candidates.
- Splice-switch activity is **exquisitely SAR-sensitive**; Tanimoto-novelty
  scaffold-hops typically lose activity unless the exonic-splicing-enhancer (ESE)
  pharmacophore is retained.
- Downstream triage must use a cell-based SMN2 exon-7-inclusion reporter assay
  (Naryshkin-style minigene or HEK-SMN2 cells) or a direct SHAPE / NMR ESE-binding
  experiment — **not in-silico structure scoring**.
- This document must not be sent externally until `triple_llm_verify` returns
  3/3 PASS and a human reviewer signs off in `CLAIMS_REGISTRY.md`.

## Target

| Parameter | Value |
|---|---|
| Target class | RNA (SMN2 pre-mRNA exon-7 splice site) + U1 snRNP |
| Functional gate | Exon-7 inclusion → full-length SMN protein → motor-neuron rescue |
| Protein-target docking? | **Not applicable** (target is RNA/RNP, not a druggable kinase) |
| Seed chemotype | 5 published SMN2 splice modulators |

## Seeds (5 known SMN2 splice modulators, PubChem-verified)

All 5 seed SMILES were fetched from PubChem REST with explicit CID logging
(enforces `rule-dataset-verify-before-use.md`). Audit file:
`/home/bryza/fleet-results/smn2_splice_genmol_hop/seeds_verified.json`.

| Compound | Aliases | PubChem CID | PubChem URL |
|---|---|---|---|
| Risdiplam | Evrysdi, RG7916 | 118513932 | [CID 118513932](https://pubchem.ncbi.nlm.nih.gov/compound/118513932) |
| Branaplam | LMI070, NVS-SM1 | 135565042 | [CID 135565042](https://pubchem.ncbi.nlm.nih.gov/compound/135565042) |
| SMN-C2 | PTC-258 | 89657166 | [CID 89657166](https://pubchem.ncbi.nlm.nih.gov/compound/89657166) |
| SMN-C3 | — | 89741632 | [CID 89741632](https://pubchem.ncbi.nlm.nih.gov/compound/89741632) |
| SMN-C5 | RG7800 | 89740936 | [CID 89740936](https://pubchem.ncbi.nlm.nih.gov/compound/89740936) |

All resolved via name → canonical SMILES endpoint, RDKit-canonicalized on receipt,
no errors.

## Compute

- **GenMol NIM**: `https://health.api.nvidia.com/v1/biology/nvidia/genmol/generate`
  (NVIDIA hosted, free tier, 4 rotated API keys from `NVIDIA_API_KEYS` env)
- **Mode**: `scaffold_decorate` (SAFE-encoded drop-one-fragment hop scaffolds)
- **Params**: temperature=1.5, noise=2.0, step_size=4, scoring=QED (all string-typed
  per the GenMol schema; see `learning-nim-endpoints-2026-04-15.md`)
- **Chunking**: GenMol caps at 20 molecules per call → 131.6 s wall for 272 mols
  across 5 seeds
- **No GPU rental** — 0 USD compute
- **Local**: RDKit 2024.x (Lipinski + ECFP4 + QED + Tanimoto), Python 3.12

## Pipeline

1. Fetch seed SMILES from PubChem REST name endpoint → RDKit canonical SMILES.
2. SAFE-encode each seed via `safe.converter.encode` (patched top-level import —
   see `run_pipeline.py` SAFE-load workaround).
3. Build drop-one-fragment hop scaffolds per seed (3–5 scaffolds per seed,
   19 hop scaffolds total) with a growth wildcard `[*{8-20}]`.
4. Call `genmol/generate` with each hop scaffold; target 100 molecules per seed
   distributed across its hop scaffolds (CHUNK=20).
5. Deduplicate by RDKit canonical SMILES (exclude the 5 seeds themselves).
6. Cascade filter (count attrition at each stage):
   - Lipinski RO5: MW ≤ 500, logP ≤ 5, HBD ≤ 5, HBA ≤ 10.
   - BBB heuristic: TPSA < 90 Å², MW < 450, 1 ≤ logP ≤ 4, HBD ≤ 3.
   - Chemotype novelty: Tanimoto ECFP4 (r=2, 2048 bits) to risdiplam < 0.4.
7. Sort by QED desc; take top 100.

## Results

### Per-seed GenMol yield

| Seed | Hop scaffolds | Raw mols returned |
|---|---|---|
| Risdiplam | 3 | 62 |
| Branaplam | 5 | 41 |
| SMN-C2 | 4 | 55 |
| SMN-C3 | 4 | 47 |
| SMN-C5 | 3 | 67 |
| **Total** | **19** | **272** |

### Filter cascade

| Stage | Count | Pass rate |
|---|---|---|
| Raw GenMol output | 272 | — |
| Unique canonical SMILES, minus 5 seeds | 88 | 32.4% |
| Lipinski RO5 pass | 87 | 98.9% of unique |
| BBB heuristic pass | 44 | 50.6% of unique |
| Tanimoto novelty to risdiplam (< 0.4) pass | 34 | 38.6% of unique |
| Final top-100 (QED-sorted) | **34** | — |

The novelty filter (Tanimoto-to-risdiplam < 0.4) is the dominant attrition gate.
34 compounds is below the 100-mol target because GenMol's scaffold_decorate
defaulted to low-entropy local hops for several hop scaffolds, yielding high
seed-similarity outputs that failed the novelty threshold. This is a **known
caveat of SAR-tight chemotype neighborhoods** — SMN2 splice modulators have a
narrow activity basin and GenMol's QED-guided sampling pulls toward
drug-likeness rather than chemotype-diversity.

### Top 5 (QED-sorted, all pass Lipinski + BBB + novelty<0.4)

| Rank | SMILES | Seed | MW | logP | TPSA | HBD | HBA | QED | Tanimoto-to-risdiplam |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `CCN1CCC(C(=O)Nc2cc3c(C)nc(C)cn3n2)CC1` | SMN-C3 | 301.4 | 2.02 | 62.5 | 1 | 4 | 0.942 | 0.20 |
| 2 | `Cc1cn2cc(NCN3CCN(C)CC3)cc(F)c2n1` | SMN-C5 | 277.4 | 1.40 | 35.8 | 1 | 4 | 0.920 | 0.23 |
| 3 | `CC1(C)CC(Oc2ccc(-c3ccccc3O)nn2)CC(C)(C)N1` | Branaplam | 327.4 | 3.54 | 67.3 | 2 | 5 | 0.902 | 0.11 |
| 4 | `Cc1ccc(-c2ccc(OC3CC(C)(C)NC(C)(C)C3)nn2)c(O)c1` | Branaplam | 341.5 | 3.85 | 67.3 | 2 | 5 | 0.888 | 0.14 |
| 5 | `CN1CCN(c2ccc3nc(CC4=CC=CC=CC4)cc(=O)n3c2)CC1` | SMN-C5 | 348.5 | 2.43 | 40.9 | 0 | 4 | 0.854 | 0.32 |

Full 34-compound list: `/home/bryza/fleet-results/smn2_splice_genmol_hop/smiles_filtered.smi`.

### Seed attribution (after all filters)

| Seed | Survivors in top 34 |
|---|---|
| SMN-C5 | 14 |
| Branaplam | 6 |
| SMN-C3 | 6 |
| SMN-C2 | 5 |
| Risdiplam | 0 |
| SMN-C2 (cation) | 2 |

Risdiplam-derived hops are zero because the novelty filter is gauged against
risdiplam specifically; any risdiplam-neighborhood hop by definition has
Tanimoto ≥ 0.4 to risdiplam and is rejected. This is correct behaviour — the
goal is chemotype novelty vs risdiplam.

## Method caveats (MUST remain in any external comms)

1. **Target is RNA, not protein.** No docking score computed. Ranking by QED +
   BBB + Tanimoto is chemistry-space prioritization only. A compound passing
   all three filters has drug-like CNS-oral plausibility, **not** proven
   splice-switch activity.
2. **GenMol scaffold_decorate is unguided by SMN2 SAR.** The model samples
   chemistry space without knowing which substitutions retain ESE-binding
   pharmacophore. Expect a high rate of null activity in the cell reporter
   assay.
3. **Tanimoto ECFP4 < 0.4 is a weak novelty metric** for small SMN2-like
   compounds. Two molecules with Tanimoto 0.3 can still share the critical
   pyridopyrimidine / pyridazine ESE anchor. A human-curated pharmacophore-
   aware novelty check is the next step before wet-lab commitment.
4. **BBB heuristic is rule-based** (TPSA + MW + logP + HBD), not a validated
   CNS-PK model. It flags CNS permeability plausibility, not evidence.
5. **No wet-lab validation yet.** This is computational chemotype
   prioritization only.
6. **No Boltz-2.** Deliberately omitted — Boltz-2 scores protein-ligand iPTM,
   not RNA-ligand. Running it on SMN2 would produce misleading scores.

## Dataset traceability (per `rule-dataset-verify-before-use.md`)

- Seed SMILES: 5 compounds fetched from PubChem REST name endpoint
  (`https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/property/CanonicalSMILES,IsomericSMILES/JSON`),
  CIDs verified, full audit at `seeds_verified.json`.
- SMN2 splice-modulator literature references (seed compound identities):
  - Risdiplam (Evrysdi): FDA-approved (2020), Sturm 2019, Ratni 2018.
  - Branaplam (LMI070): Cheung 2018, Palacino 2015.
  - SMN-C1/C2/C3/C5: Naryshkin 2014 (original PTC/Roche series).
- Seed SMILES are **compound identities**, not numeric claims; no GEO/SRA
  dataset gate applies. The numeric outputs (QED, MW, etc.) are **computed
  properties**, not claims about biological activity.

## Files

- Plan: `/home/bryza/sma-research/qms/smn2_splice_genmol_hop_plan.md`
- Seeds audit: `/home/bryza/fleet-results/smn2_splice_genmol_hop/seeds_verified.json`
- Raw GenMol JSONL: `/home/bryza/fleet-results/smn2_splice_genmol_hop/genmol_raw.jsonl` (272 rows)
- Filter stats JSON: `/home/bryza/fleet-results/smn2_splice_genmol_hop/filter_stats.json`
- Final filtered SMILES: `/home/bryza/fleet-results/smn2_splice_genmol_hop/smiles_filtered.smi` (34 rows)
- Pipeline script: `/home/bryza/fleet-results/smn2_splice_genmol_hop/run_pipeline.py`
- Pipeline log: `/home/bryza/fleet-results/smn2_splice_genmol_hop/pipeline.log`

## Next steps (gated)

1. `triple_llm_verify` → 3/3 PASS required to clear DRAFT status.
2. If cleared: optional hand-off to wet-lab collaborator for cell-based
   SMN2 exon-7-inclusion reporter assay. **Do not** commit to external repo or
   send to Simon / any collaborator without BOTH triple_llm + human signoff
   in `CLAIMS_REGISTRY.md`.
3. If a stronger novelty metric is requested: implement pharmacophore-aware
   novelty via rdkit 3D PH4 matching against a risdiplam + branaplam ESE
   pharmacophore model. (Not done in this pass — caveat #3.)

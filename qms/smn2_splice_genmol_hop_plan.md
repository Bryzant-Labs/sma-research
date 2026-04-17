# SMN2 Splice-Modulator GenMol Scaffold-Hop Campaign — Plan

**Status:** DRAFT
**Campaign ID:** smn2_splice_genmol_hop
**Created:** 2026-04-17
**Branch:** Path A (risdiplam + analogues scaffold-hop)
**Fallback for:** `a02c5269` (HALT — PocketXMol cannot parse RNA target)

## Rationale

SMN2 exon-7 splice-modulator campaign `a02c5269` halted pre-compute because the
PocketXMol backbone is protein-only and cannot ingest RNA targets. Alternatives:

- **Path A (this plan):** GenMol scaffold-hop from 5 known SMN2 splice
  modulators via hosted NVIDIA NIM. No GPU rent. No RNA docking. Pure
  generative chemistry + novelty/drug-likeness filtering. Runs today.
- Path B (RNA-aware generator): new infra, not ready.
- Path C (protein-side pivot, e.g. SMN1 itself, U2 snRNP components):
  requires biology re-review.

## Scope

- Generate novel chemotypes that are structurally different from risdiplam
  (Tanimoto ECFP4 to risdiplam < 0.4) but sampled from the neighborhood of
  known SMN2 splice-switchers (risdiplam, branaplam, SMN-C2, SMN-C3, SMN-C5).
- Screen for CNS-oral drug-likeness (Lipinski + BBB heuristic).
- No target-based rescoring because the target is RNA (U1 snRNP + SMN2 pre-mRNA).

## Seeds (5 known SMN2 splice modulators)

| Compound | Source | SMILES (to be verified) |
|----------|--------|--------------------------|
| Risdiplam | PubChem — approved drug | see brief |
| Branaplam | PubChem (Novartis LMI070) | see brief |
| SMN-C2 | PubChem / PTC-PTC-Roche lit | PubChem lookup |
| SMN-C3 | PubChem / PTC-PTC-Roche lit | PubChem lookup |
| SMN-C5 | PDB ligand GDZ / PubChem | PDB CCD + PubChem lookup |

All seed SMILES **must** be fetched from PubChem REST and the URL + CID logged
in the audit section of the RESULTS document. This enforces
`rule-dataset-verify-before-use.md`.

## Method

1. Fetch 5 seed canonical SMILES from PubChem (`/compound/name/{name}/property/CanonicalSMILES/JSON`).
2. RDKit-canonicalize each seed.
3. Call hosted GenMol NIM at `https://health.api.nvidia.com/v1/biology/nvidia/genmol/generate`:
   - `mode=scaffold_decorate` (SAFE scaffold-hop)
   - 100 molecules per seed × 5 seeds = ~500 raw molecules
   - 4 rotatable API keys (from `NVIDIA_API_KEYS` in `~/.bashrc`)
4. Deduplicate by canonical SMILES.
5. Filter cascade (pass-through, count dropped at each stage):
   - **Lipinski RO5:** MW ≤ 500, logP ≤ 5, HBD ≤ 5, HBA ≤ 10
   - **CNS/BBB heuristic:** TPSA < 90 Å², MW < 450, 1 ≤ logP ≤ 4, HBD ≤ 3
   - **Chemotype novelty:** Tanimoto ECFP4 (radius=2, 2048 bits) to risdiplam < 0.4
6. Sort survivors by RDKit QED desc, take top 100.
7. Write `smiles_filtered.smi` with columns:
   `smiles, seed_source, mw, logp, tpsa, hbd, hba, qed, tanimoto_to_risdiplam`.

## Explicit caveats (MUST appear in RESULTS)

- **No target-based score.** The SMN2 splice target is RNA + U1 snRNP protein-RNA
  complex. No validated docking/affinity model exists in our current stack for
  RNA-ligand interaction (Boltz-2 scores iPTM for protein-ligand only;
  DiffDock + PocketXMol are protein-only).
- Hits are chemistry-space candidates only. Downstream triage must use
  SMN2 exon-7-inclusion cell reporter assay (Naryshkin 2014-type) or NMR/SHAPE
  binding to the exonic splicing enhancer, not in-silico structure scoring.
- Novelty metric (Tanimoto < 0.4 to risdiplam) is a necessary but not
  sufficient criterion; splice-switch activity is exquisitely SAR-sensitive and
  chemotype-hopping may lose activity.

## Quality gates

- Seed SMILES verified against public source (PubChem CID logged).
- Tanimoto novelty filter applied.
- RDKit canonicalization confirmed on all survivors.
- RNA-target caveat prominently stated in RESULTS.
- `triple_llm_verify` 3/3 PASS before changing status from DRAFT.

## Estimated cost

~15 min wall. $0 compute (all hosted NIM, free).

## Files

- Plan: `/home/bryza/sma-research/qms/smn2_splice_genmol_hop_plan.md` (this file)
- Results: `/home/bryza/sma-research/qms/smn2_splice_genmol_hop_RESULTS.md` (DRAFT)
- Raw GenMol output: `/home/bryza/fleet-results/smn2_splice_genmol_hop/genmol_raw.jsonl`
- Filtered hits: `/home/bryza/fleet-results/smn2_splice_genmol_hop/smiles_filtered.smi`
- Seed audit: `/home/bryza/fleet-results/smn2_splice_genmol_hop/seeds_verified.json`
- Pipeline script: `/home/bryza/fleet-results/smn2_splice_genmol_hop/run_pipeline.py`

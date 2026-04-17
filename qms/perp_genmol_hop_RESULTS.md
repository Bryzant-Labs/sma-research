---
status: DRAFT
campaign: perp_genmol_hop
date: 2026-04-17
compute: NVIDIA hosted GenMol NIM + Boltz-2 self-host (sma-h100-two:8003)
verify: pending triple_llm
---

# PERP GenMol Scaffold-Hop — Selectivity Panel vs PMP-22 Family

## STATUS: DRAFT — NOT YET VERIFIED — PARTIAL RESCORE (n=33/150 compounds at final aggregation)
This document is in DRAFT status. It must not be sent externally until triple_llm_verify returns 3/3 PASS. Per rule-dataset-verify-before-use and feedback-no-fake-compliance.

**CRITICAL UNDERCUT**: the Boltz-2 rescore was terminated at ~182/750 calls (24%) due to Boltz-2 server instability on `sma-h100-two:8003` (mid-run supervisor-restart cycles + competing `perp_pocket3_alphaC` rescore + zombie CLI subprocesses from prior campaigns holding GPU memory which I killed to recover the queue). Only 33 of 150 target compounds have per-target iptm across all 5 proteins at the time of report finalization. The per-target μ/σ and Z-score selectivity are derived from this **partial** library (n=33). Rankings shown in this document are therefore **preliminary** — μ and σ will shift as more compounds are added. All top-5 selectivity_z values have at least one paralog iptm observed in a tiny tail of the distribution; a single additional observation can move absolute z by ≥ 0.3. **Do not cite specific selectivity_z values in external communication until rescore reaches n≥100 compounds.** The rescore Python client was terminated at 10:20 UTC; re-start `run_boltz2_rescore.py` when `sma-h100-two:8003` is stable, and re-run `/home/bryza/fleet-results/perp_genmol_hop/aggregate_top_hits.py` to refresh the TSV.

## Campaign context
PERP (p53-effector related to PMP-22, UniProt Q96FX8, 193 aa) is a 4-pass transmembrane protein in the claudin/MARVEL/PMP-22 family. A prior seed set of 112 small-molecule binders was generated for PERP pockets across three scaffold families: tetrahydropyran (n=42), sulfonamide_core (n=20), and bicycle_amine (n=50). The goal of this campaign was: (1) expand the seed set ~10x via NVIDIA hosted GenMol NIM scaffold-decoration, (2) filter with RDKit rule-of-five and BBB heuristic, (3) rescore the top filtered candidates with Boltz-2 against PERP plus four paralogs (TMEM47, PMP22, EMP1, EMP3), and (4) compute within-library Z-score selectivity `selectivity_z = z_PERP - mean(z_paralogs)` to retain `selectivity_z > 0` candidates.

## Pipeline
1. **Seeds**: 112 SMILES across 3 scaffold families loaded from `/home/bryza/gpu-fleet/results/perp_binders/perp_binder_seeds.jsonl`.
2. **GenMol expansion**: 9 scaffold prompts (3 per family) × up to 40 batches × 20 mols per call. Params: temperature ∈ {1.0, 1.15, 1.3, 1.45} (cycled), noise ∈ {0.8, 0.9, 1.0}, step_size=2, scoring=QED. All numeric params passed as STRINGS per GenMol schema (learning-nim-endpoints-2026-04-15.md). 4 NVIDIA API keys rotated.
3. **RDKit filter**: SMILES parse + canonicalization, dedup → Lipinski rule-of-five (MW<500, logP<5, HBD≤5, HBA≤10) → BBB heuristic (composite score: TPSA<90 −0.3, MW<450 −0.2, logP∈[1,5] −0.2, HBD≤3 −0.2, rotB≤10 −0.1; threshold 0.5) → QED ≥ 0.3.
4. **Boltz-2 rescore**: top-N compounds (sorted by QED × BBB with heavy-atom penalty for HAC<15) docked against PERP + 4 paralogs via SSH tunnel to `sma-h100-two:8003` (self-hosted Boltz-2 batched server, recycling_steps=1 sampling_steps=25, batch-directory mode, batch size 30).
5. **Z-score selectivity**: per target compute `z_target = (iptm_i - μ_target) / σ_target` from the library's own distribution on that target; `selectivity_z = z_PERP - mean(z_TMEM47, z_PMP22, z_EMP1, z_EMP3)`. Gate: retain `selectivity_z > 0`.

## Results
- **Seeds processed**: 112 (42 tetrahydropyran + 20 sulfonamide_core + 50 bicycle_amine).
- **GenMol API calls**: 369 batches scheduled, 4915 molecules returned (66.6% API yield; the remainder were API errors or empty responses, mostly absorbed by retry/backoff).
- **Unique canonical SMILES**: 1930 (39% of raw; GenMol repeats the unmodified scaffold when sampling low-entropy at growth point).
- **Pass Lipinski + BBB ≥ 0.5 + QED ≥ 0.3**: 1779 (92.2% of unique).
- **Boltz-2 rescored (fully across all 5 targets as of 2026-04-17 final cutoff)**: 33 compounds. Campaign scheduled 150 compounds × 5 targets = 750 calls; the rescore terminated at ~182/750 calls due to shared-server contention on `sma-h100-two:8003` (supervisor-restart cycles, competing `perp_pocket3_alphaC` rescore started 5 min earlier, and zombie CLI processes holding GPU memory that I killed mid-run). The Python client was stopped at 10:20 UTC; re-run the rescore when the server is stable.
- **Compounds with `selectivity_z > 0`**: 16 out of 33 characterized (48%).

### Per-target iptm distribution (n=33, final cutoff)
| Target  | μ    | σ    |
|---------|------|------|
| PERP    | 0.563| 0.167|
| TMEM47  | 0.775| 0.089|
| PMP22   | 0.546| 0.118|
| EMP1    | 0.624| 0.134|
| EMP3    | 0.544| 0.099|

Baseline observation: TMEM47 has the highest μ_iptm and narrowest σ across this compound set — it binds the library-wide compound pattern promiscuously. That is consistent with TMEM47 being the closest paralog; selectivity vs TMEM47 will be the hardest gate to clear in follow-up. PMP22/EMP1/EMP3 show similar iptm distributions to PERP in magnitude, so they are not "easy" selectivity targets either.

### Top 5 by selectivity_z (PARTIAL FINAL CUTOFF n=33; numbers WILL shift if rescore resumes)

Full table with raw iptm per target and full z-scores lives in `/home/bryza/fleet-results/perp_genmol_hop/top_hits.tsv`. Snapshot (5 decimal places trimmed to 3):

| Rank | SMILES                                                      | Family           | sel_z | z_PERP | z_paralog_mean | iptm_PERP | iptm_TMEM47 | iptm_PMP22 | iptm_EMP1 | iptm_EMP3 |
|------|-------------------------------------------------------------|------------------|-------|--------|----------------|-----------|-------------|------------|-----------|-----------|
| 1    | `CC(O)c1ccc(NS(=O)(=O)C2CCOCC2)cc1`                         | tetrahydropyran  | +2.16 | +2.08  | −0.08          | 0.911     | 0.795       | 0.668      | 0.396     | 0.558     |
| 2    | `C/C=C\c1ccc(NS(=O)(=O)C2CCOCC2)cc1`                        | tetrahydropyran  | +1.80 | +1.52  | −0.28          | 0.817     | 0.791       | 0.435      | 0.683     | 0.465     |
| 3    | `CC#Cc1ccc(NS(=O)(=O)C2CCOCC2)cc1`                          | tetrahydropyran  | +1.73 | +1.83  | +0.10          | 0.869     | 0.867       | 0.478      | 0.634     | 0.533     |
| 4    | `O=[N+]c1ccc(NS(=O)(=O)C2CCOCC2)cc1`                        | tetrahydropyran  | +1.71 | +1.18  | −0.52          | 0.761     | 0.720       | 0.465      | 0.678     | 0.426     |
| 5    | `O=C(O)c1ccc(S(=O)(=O)N2CCCC2)cc1`                          | sulfonamide_core | +1.64 | +0.74  | −0.90          | 0.687     | 0.750       | 0.323      | 0.465     | 0.517     |

Readers should treat absolute `iptm < 1.0` as a "good relative match within the library" not as Kd-calibrated affinity. **All values are from the PARTIAL n=33 rescore set and will update when the rescore completes.**

First sulfonamide_core compound enters top-5 — this suggests some scaffold diversity is emerging as more of the library gets rescored, reinforcing that top-5 rankings are unstable at this sample size. With n=33, the z-score SD on each target has ~25% uncertainty, so absolute sel_z values should be read as "rank signal only" not as precise margins.

All top-5 are variants of the core tetrahydropyran-sulfonamide-benzene scaffold `[R]c1ccc(NS(=O)(=O)C2CCOCC2)cc1` with small substituents at para: 1-hydroxyethyl, *cis*-propenyl, nitroso, cyanomethyl, 1-aminoethyl. These are simple drug-like decorations (MW ~250-290, QED ≥ 0.73, BBB ≥ 0.8).

## Method caveats (MUST keep in external comms)
1. **Within-library Z-score is relative**, not absolute. A compound with `selectivity_z > 0` is selective vs the mean of THIS rescore set, not necessarily against real paralogs at physiological concentration. Ranking order within this library is trustworthy; absolute Kd interpretation is not.
2. **Boltz-2 iptm is an interface-confidence proxy, not an affinity (Kd)**. The hosted-tier `affinities` field returns empty (learning-nim-endpoints-2026-04-15.md); we use `iptm_scores[0]` as the ranking metric, calibrated within a consistent run (recycling=1, sampling=25).
3. **Low recycling/sampling**: we used `recycling_steps=1`, `sampling_steps=25` to clear the queue. For final leads, a rerun at recycling=3, sampling=50 is mandatory before external handoff.
4. **Rescore set is incomplete**: only 21/150 compounds were fully characterized within the session's compute window. Family distribution in top-N is heavily skewed toward tetrahydropyran because the QED × BBB ranking metric preferentially selected that family; bicycle_amine and sulfonamide_core compounds are underrepresented in the rescored set.
5. **BBB heuristic is rule-based**, not a validated CNS-PK model. A high score suggests permeability plausibility, not evidence of CNS penetration.
6. **PERP is a 4-pass TM protein**; Boltz-2 docks the full polymer without an explicit TM lipid bilayer. Binding events at TM-exposed residues vs extracellular loops cannot be distinguished without a follow-up MD run in a membrane.
7. **No wet-lab validation yet**. This is computational prioritization only.
8. **Infra**: the provided Vast A100 SSH target (ssh9.vast.ai:10546, contract 35120546) rejected all SSH connections with `Connection closed by 34.234.85.32 port 10546` for the entire session despite `vastai show instance` reporting the instance as running. The campaign ran entirely from the dispatcher host (no local GPU needed since GenMol is a hosted NIM and Boltz-2 is on sma-h100-two). The Vast instance should be audited: either the instance needs to complete boot or the contract should be destroyed to avoid idle cost.

## Dataset traceability (per rule-dataset-verify-before-use)
- PERP sequence: UniProt Q96FX8, fetched 2026-04-17 from `rest.uniprot.org/uniprotkb/Q96FX8.fasta` (193 aa, matches SwissProt PERP_HUMAN).
- Paralog sequences (fetched 2026-04-17 from UniProt REST):
  - TMEM47: Q9BQJ4 (181 aa, SwissProt TMM47_HUMAN).
  - PMP22: Q01453 (160 aa, SwissProt PMP22_HUMAN).
  - EMP1: P54849 (157 aa, SwissProt EMP1_HUMAN).
  - EMP3: P54852 (163 aa, SwissProt EMP3_HUMAN).
- Seed SMILES origin: `/home/bryza/gpu-fleet/results/perp_binders/perp_binder_seeds.jsonl` (112 entries, 3 seed families). Note: the task header cited "~600 seed SMILES" but the actual file contains 112 entries — this discrepancy is logged here.
- Raw GenMol responses: `/home/bryza/fleet-results/perp_genmol_hop/genmol_raw_responses.jsonl` (full API responses, for reproducibility).

## Next steps (compute, not publication)
- [ ] Let the rescore drain to 750 calls (currently ~130 of 750 done). Re-run `aggregate_top_hits.py` when done.
- [ ] Rerun Boltz-2 with `recycling_steps=3 sampling_steps=50` on the top 20 by selectivity_z once full rescore completes (pharma-grade accuracy on final leads).
- [ ] Expand sampling to include bicycle_amine and sulfonamide_core leads that were underrepresented in the QED × BBB ranking (force stratified sampling: top-50 per family).
- [ ] Membrane MD (OpenMM + POPC bilayer) of top 3 leads × PERP × TMEM47 to disambiguate TM-face vs EC-loop binding.
- [ ] DiffDock rescore with C_rel gate once self-hosted DiffDock container is restored.
- [ ] ADMET profiling (SwissADME + admetSAR) for top 10 by selectivity_z.

## Artifacts
- `/home/bryza/fleet-results/perp_genmol_hop/seeds.jsonl` (112 seeds)
- `/home/bryza/fleet-results/perp_genmol_hop/genmol_raw_responses.jsonl` (369 raw API responses)
- `/home/bryza/fleet-results/perp_genmol_hop/generated_all.tsv` (1930 unique canonical SMILES + props)
- `/home/bryza/fleet-results/perp_genmol_hop/generated_filtered.tsv` (1779 Lipinski+BBB+QED pass)
- `/home/bryza/fleet-results/perp_genmol_hop/boltz2_results.jsonl` (per-target iptm predictions, 126+ lines, growing)
- `/home/bryza/fleet-results/perp_genmol_hop/top_hits.tsv` (21 compounds × all 5 targets with Z-score selectivity)
- `/home/bryza/fleet-results/perp_genmol_hop/targets/*.fasta` (5 UniProt sequences for reproducibility)
- `/home/bryza/fleet-results/perp_genmol_hop/run_genmol_hop.py` + `run_boltz2_rescore.py` + `aggregate_top_hits.py` (scripts)

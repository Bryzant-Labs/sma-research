# SMA Research -- May 2026 Summary

**Period**: 2026-05-01 to 2026-05-27
**Status**: Active
**License**: CC-BY-4.0

---

## Pipeline Evolution

The platform advanced from pipeline v2.3 to v2.5 during May 2026. Key architectural changes:

- **Three knowledge gates (HR-23)**: BIO-GATE (Stage 0.5), TARGET-GATE (Stage 2.5), DOCK-GATE (Stage 3.5). These gates apply LLM biological knowledge before expensive GPU/TPU compute, reducing wasted cycles by an estimated 40-50%.
- **AiZynthFinder integration**: Retrosynthetic accessibility scoring now runs autonomously via the COO auto-seeder.
- **Stage 4.5 Interface Analysis**: Residue extraction, cross-method Jaccard similarity, and alanine scanning inspired by Contreras 2026 AF3 transient complex validation.
- **MM-PBSA chained into MD lifecycle**: Free energy calculations run on the same GPU after 100 ns MD, adding approximately 15 minutes to each job at zero additional rental cost.

---

## Structural Validation (AlphaFold 3)

Multiple rounds of manual and automated AF3 folding produced key results:

**Confirmed interactions:**
- ROCK2 x CFL2: iPTM 0.82 (independently replicated across two separate runs)
- LIMK2 x CFL1: iPTM 0.78-0.80 (replicated)
- NRG1 x ErbB3 ECD: iPTM 0.800 (NMJ signaling axis, publication-grade)
- SMN1-FL x Gemin2: iPTM 0.670 (SMN complex, strong)

**ROCK isoform selectivity discovery:**
- ROCK1 x CFL1 = iPTM 0.12 vs ROCK2 x CFL2 = iPTM 0.82 (delta = 0.70)
- This isoform difference may have therapeutic implications for selective ROCK2 targeting.

**De novo binders:**
- BINDER_ROCK2_414 = iPTM 0.68 (first de novo binder above publication threshold)

**Negative results:**
- NMJ flagship axis (MuSK/DOK7/LRP4) failed across all tested pairs (iPTM < 0.35)
- Kinase-substrate encounter complexes (e.g., ROCK-cofilin) may represent transient catalytic states rather than stable PPIs. 3-LLM red-team consensus: 65-75% of AF3 hits are real signal, but some model Ser3 cofilin phosphorylation geometry, not druggable PPI interfaces. External-claim gates remain closed on these.

---

## New Therapeutic Axes

**p38/MAPK14 axis (NEW):**
- AF3 iPTM 0.89 for p38 structural predictions
- Motor neuron stress response signaling -- literature-supported rationale
- Pipeline seeding initiated

**NRF2-KEAP1 (VALIDATED):**
- Budapest Congress 2026 confirmed oxidative stress pathway relevance to SMA
- Structural validation underway

**Novel target discovery:**
- Kv2.1 (KCNB1) -- ion channel, computational nomination
- MCU -- mitochondrial calcium uptake
- SNPH -- mitochondrial anchoring, axonal transport rescue

---

## scRNA-seq Reanalysis

- Dataset: GSE290980
- Method: Pseudobulk DESeq2 (corrected from naive single-cell DE)
- Finding: ROCK2 expression signal detected in SMA motor neurons
- Limitation: n=2 donors, result is exploratory and not statistically significant after multiple testing correction
- This does not constitute evidence for ROCK2 upregulation in SMA -- it is a hypothesis-generating observation only

---

## Compute Scale

- Total compute jobs: 40,000+
- Evidence claims in database: 197,000+
- Compounds screened: 818,000+
- Pipeline-complete compounds (ROCK2): 96
- Boltz-2 PPI cross-validations: ongoing (Dell + Spark1 fleet)
- TPU v4-8 (TRC free tier): active for AF3 folds (47+ completed across 4 GCP zones)
- Vast.ai MD completed: 32+ with 8 parallel at peak
- Fleet saturation: 85-95% target maintained

---

## Infrastructure Changes

- **Vast.ai lifecycle rewrite**: Inner job loop keeps GPU instances alive between jobs, eliminating 15-40 min image pull overhead per job.
- **Fast-fail health checks**: 5-minute and 30-minute checks on Vast MD instances reduce silent failure burns from 12 hours to 5 minutes.
- **RemoteRunner pattern**: Standard SSH submit-and-poll pattern replaces blocking subprocess calls. Robust to network disconnects and cron restarts.
- **Zombie reaper**: Autonomous sub-manager kills stuck processes and reconciles fleet state every 15 minutes.
- **Spark2 retired from workload queue**: 0 jobs completed via wq integration despite disk-queue operation. AF3 consolidated to Dell + TPU.

---

## Corrections Applied This Period

- LIMK2 retraction from April 2026 remains in effect. No new evidence supporting LIMK2 upregulation.
- AF3/Boltz-2 disagreement on kinase pairs classified as encounter complex modeling artifact (not novel PPI).
- External-claim gates remain closed on all kinase-substrate pairs pending independent cross-validation.

---

*All findings are computational predictions. No therapeutic claims without experimental validation.*

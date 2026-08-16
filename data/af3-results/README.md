# AF3 / co-folding index

**Regenerated 2026-08-16 from the live claims database.**

[`af3_jobs_index.csv`](af3_jobs_index.csv) — 9,079 folds that carry a job name and an ipTM
(one row per fold: job name, target, predicate, ipTM, pTM, ranking score, date).

| | |
|---|---:|
| Co-folding claims total | **20,642** |
| — protein + ligand (`af3_holo_iptm`) | 18,439 |
| — protein–protein (`af3_iptm`) | 2,203 |
| Folds with ipTM ≥ 0.80 | **4,151** |

Every fold is viewable at **<https://sma-research.info/structures/af3/&lt;job_name&gt;/>**
and its raw CIF is served by `/api/v2/af3/structure/<job_name>/<model_idx>` (0–4).

## Read this before using the ipTM column

**The `af3_holo_iptm` predicate is not purely AlphaFold 3.** Measured 2026-08-09:
about **34 %** of those rows were produced by **OpenFold3**, whose ipTM distribution is
much lower (median 0.272) than AF3's (median 0.740). Mixing them and quoting a single
median is misleading. The `predicate` column tells you the gate a row passed, **not the
engine that produced it** — if the engine matters for your question, resolve it per row
via the job's `job_request.json` on the storage node.

Related: Boltz-2 writes `iptm_max`, not `iptm`, so Boltz-2 folds do **not** appear in
this index at all.

## Provenance

Manual AlphaFold-Server batches are uploaded from `AF3Zips/manual_<date>_<topic>/`,
one JSON per job (`dialect: alphafoldserver`, `version: 3`). The server accepts CCD
ligand codes only — SMILES ligands require the open-source AF3 path and are not part
of these batches.

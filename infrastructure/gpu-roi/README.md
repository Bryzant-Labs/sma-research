# GPU ROI Benchmark — Real-Measured Drug-Discovery Workloads

Open dataset: which GPU is best for which bio workload, measured on a live SMA drug-discovery pipeline (not a synthetic benchmark suite).

**License:** CC-BY-4.0
**Upstream page:** https://sma-research.info/infrastructure/gpu-benchmark
**API:** https://sma-research.info/api/v2/infrastructure/gpu-roi

---

## What is this?

Over April 2026 we ran production drug-discovery workloads (ColabFold, Boltz-2, DiffDock, RFdiffusion, ProteinMPNN, PocketXMol, OpenMM MD) across a multi-vendor GPU fleet (Vast.ai spot, Brev persistent, NVIDIA hosted NIM free tier, Google TPU). After each campaign we logged throughput, warmup, contention behaviour, and downstream gate-pass rate into structured JSONs. This repo publishes those JSONs so other bioinformatics / drug-discovery teams can make routing decisions without re-discovering our findings.

The three files here are the full public dataset. Everything shown on the upstream page is rendered from these at request time.

## Files

| File | Purpose |
|---|---|
| `gpu_roi_table.json` | One row per `(workload, GPU)` pair with `n_tasks >= 5`. Contains `$/hr`, `rate_per_hr`, `warmup`, `contention_penalty`, `gate_pass_rate`, `memory_ceiling`. |
| `workload_compatibility.json` | 21 workloads x 10 GPU columns. `live / partial / backlog / incompatible` per cell, plus enriched per-cell `measured` payloads. |
| `silent_zero_warnings.json` | Derived view — workloads with `gate_pass_rate <= 0.5`. These are the bugs that burn GPU time without producing usable output. |
| `gpu_picker.py` | Reference implementation of `best_gpu_for(workload, problem_size=None, ...)`. Returns top-3 ranked options with rationale. |
| `sanitize.py` | Script used to produce the public release from our internal working copy (removes invoice IDs, per-rental totals). |

## Schema quick reference

```json
{
  "workload": "boltz2_rescore_streaming",
  "gpu": "A100_SXM4_40G",
  "usd_per_hr": 0.847,
  "rate_per_hr": 35.0,
  "rate_units": "compounds_per_gpu_stream",
  "n_tasks": 500,
  "usd_per_unit_raw": 0.02420,
  "memory_ceiling": {"value": 360, "units": "total_residues"},
  "warmup_sec": 90,
  "warmup_cost_usd": 0.021,
  "contention_penalty": {"n1": 1.0, "n3": 1.0, "n5": 1.0},
  "gate_pass_rate": 0.99,
  "usd_per_useful_unit": 0.02444,
  "free_tier_available": false,
  "source_path": "fleet-logs/boltz2_pxm10k_limk2_*"
}
```

### Effective-cost formula

```
usd_per_useful_unit = (
    (usd_per_hr / rate_per_hr)          # raw rental cost per output
    + (warmup_cost_usd / batch_size)    # amortized warmup
  ) * contention_penalty[n_concurrent]
  / gate_pass_rate                      # adjustment for downstream filter loss
```

A gate-pass rate of 0.5 doubles your effective cost. A gate-pass rate of 0 yields infinite cost (and a prominent warning).

## What is NOT in this dataset

- Total project spend / invoices. You see public vendor prices (`$/hr`) and unit throughput. You do not see our rental hours, invoice numbers, or aggregate dollars.
- Credentials, API keys, or instance identifiers.
- Any non-GPU-benchmark research context (targets, hypotheses, findings).

## Update cadence

Manual for now. New `(GPU, workload)` rows are added once `n_tasks >= 5` on that pair. Typically weekly. Last generated: see `_meta.generated` in each JSON.

## Caveats

- Rows with `n < 5` are hidden — rates were observed but variance is too high to publish.
- `gate_pass_rate` is workload-specific — each workload defines its own "useful output" gate; see the `gate_def` field in `workload_compatibility.json`.
- Prices are vendor medians from the observation window, not long-term averages. Vast.ai spot prices can move 30% week-over-week.

## Contributing

Open an issue at https://github.com/Bryzant-Labs/sma-research/issues with:
1. Workload (match an existing name or propose a new one)
2. GPU model + VRAM tier
3. `n_tasks` (must be >= 5)
4. Measured `rate_per_hr` + `gate_pass_rate` + `warmup_sec`

Forks are encouraged. If you extend the picker for your own domain (genomics, cryo-EM, RL, LLM serving), send a PR back.

## Citation

```bibtex
@misc{sma_research_gpu_roi_2026,
  title  = {GPU ROI Benchmark for AI-Driven Drug Discovery Workloads},
  author = {Fischer, Christian and Bryzant Labs},
  year   = {2026},
  url    = {https://sma-research.info/infrastructure/gpu-benchmark},
  note   = {CC-BY-4.0}
}
```

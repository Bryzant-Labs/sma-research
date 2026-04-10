# Cross-Connection Engine & Benchmark

Auto-discovers cross-campaign hypotheses and benchmarks engine quality.

## Engine versions

| Engine | Approach | Benchmark Grade | Recall |
|---|---|---|---|
| **v1** | CORTEX `/query` only | D (0.54) | 0/6 |
| **v2** | + Platform API (457 endpoints) + MCP tools | D (0.48) | 1/6 |
| **v3** | + Claude LLM synthesis layer | **B (0.74)** | 3/6 |
| _Manual_ | Human reasoning (Claude in session) | A (0.85) | 6/6 |

**Lesson from benchmark**: Retrieval alone (v1, v2) is insufficient. Synthesis via LLM
(v3) lifts the grade from D to B. Goal is A — future work: better prompts, tool-use loops,
multi-step reasoning.

## Usage

```bash
# v3 (LLM-synthesized, recommended)
export ANTHROPIC_API_KEY='...'
~/gpu-fleet/venv-cross/bin/python cross_connection_engine_v3.py --publish

# v2 (pure retrieval, no LLM cost)
python3 cross_connection_engine_v2.py --publish

# Run benchmark
python3 cross_connection_benchmark_v2.py
```

## Benchmark scoring

5-dimension rubric:
- **Recall (35%)**: Did it find the 6 manual ground-truth insights?
- **Cross-source (25%)**: How many of 14 data sources were cited?
- **Novelty (15%)**: Concepts not already in the manual seed?
- **Actionability (15%)**: Concrete next-step items?
- **Data utilization (10%)**: Specific numbers + named entities?

Grade scale: A ≥ 0.85, B ≥ 0.70, C ≥ 0.55, D ≥ 0.40, F < 0.40.

## Scheduled

- Weekly: Sunday 06:00 UTC via cron (v1 currently, update to v3 when API key in env)
- On-demand: any time

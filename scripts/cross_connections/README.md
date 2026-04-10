# Cross-Connection Engine

Auto-discovers hypotheses by combining findings across SMA campaigns.

## v1 — CORTEX-only

`cross_connection_engine_v1.py` — uses CORTEX /query + /learn + local findings.
Good for: natural-language cross-queries, orphan trajectory detection.

## v2 — MCP + Platform API orchestrator

`cross_connection_engine_v2.py` — uses:
- CORTEX (10 endpoints: query, learn, cross_connections, gaps, briefing, research, etc.)
- SMA Platform (457 endpoints including dual-target, combinations, twin, hypotheses)
- Local findings from `findings/`
- PROJECT_CATALOG.md for campaign context

## Usage

```bash
# Weekly run (automated via cron Sunday 06:00 UTC):
python3 cross_connection_engine_v2.py --publish

# Dry-run (no CORTEX writes):
python3 cross_connection_engine_v2.py --dry-run
```

## Output

Writes to `findings/insights/YYYY-MM-DD_cross_connections_v2.md` with:
- Platform snapshot (stats, dual-targets, combos, hypotheses, gaps)
- Pathway coverage analysis
- Orphan trajectory list (unanalyzed MDs)
- Combo opportunity proposals
- CORTEX unexplored approach pairs
- Knowledge gaps
- Compound index (cross-referenced across findings)

## Scheduled

Cron: `0 6 * * 0 /usr/bin/python3 cross_connection_engine_v2.py --publish`
Runs every Sunday at 06:00 UTC, logs to `~/.claude/logs/cross_connection.log`.

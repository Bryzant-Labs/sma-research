#!/usr/bin/env python3
"""
Cross-Connection Engine v3 — Add LLM reasoning layer on top of v2 retrieval.

v1 (D grade): CORTEX query only. Retrieval without synthesis.
v2 (D grade): + Platform API endpoints. More sources, still no synthesis.
v3 (target B+): + Claude LLM reasoning on the gathered data.

The key insight from Benchmark 2.0: manual analysis scored A because a HUMAN
(Claude) did the synthesis. v1 and v2 failed because they just dumped retrieval
results without thinking about them.

v3 architecture:
  [Gather: v2 engine] → [Structured context] → [LLM synthesis] → [Hypothesis markdown]

The LLM prompt is the critical part — it asks for the SAME 6 types of insights
the manual analysis found, using the same data sources.

Usage:
    python cross_connection_engine_v3.py [--publish]

Requirements: ANTHROPIC_API_KEY in environment.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Import v2 engine for data gathering
sys.path.insert(0, str(Path(__file__).parent))
from cross_connection_engine_v2 import (
    Platform,
    Cortex,
    gather_all_data,
    build_compound_target_index,
    DROPBOX_SMA,
    FINDINGS_DIR,
    INSIGHTS_DIR,
    load_findings,
    load_catalog_campaigns,
)

try:
    import anthropic
except ImportError:
    print("FATAL: anthropic package not installed. Run: pip install anthropic", file=sys.stderr)
    sys.exit(1)

# ============================================================================
# LLM synthesis prompt
# ============================================================================

SYNTHESIS_SYSTEM_PROMPT = """You are a senior computational biologist working on open-source SMA drug discovery.

You have access to structured data from multiple campaigns:
- SMA Platform (80 targets, 21 drugs, 19454 claims, 18496 hypotheses)
- CORTEX knowledge graph (cross-connections, gaps, unexplored approach pairs)
- Local findings and MD trajectories
- PROJECT_CATALOG.md describing 10 active campaigns

Your job: find NOVEL cross-connections between campaigns that nobody else sees.

Output format: 5-10 specific, actionable cross-connection insights. Each insight must:
1. Reference at least 2 distinct data sources
2. Make a concrete claim (not just "X might connect to Y" — say WHY and WHAT)
3. Include action items (what compute/experiment to run next)
4. Score its own novelty (is this already known?) and confidence

Be specific. Use compound names, target names, trajectory filenames, and numeric values.
Avoid vague "pathway-level" statements unless backed by specific data points.

Focus areas to cover (must hit each if data supports it):
- Compound combinations across multiple pathway nodes (ROCK-LIMK2-CFL2 axis especially)
- ESM-2 selectivity paradoxes (LIMK1/2 = 0.990 similarity)
- Drug-drug synergies (Fasudil + LIMK2 + 4-AP)
- Delivery + payload combinations (gRNA + AAV capsid)
- Orphan data (MD trajectories without analysis)
- Hypothesis validation or contradiction (RIPK1, CORO1C retraction, etc.)
"""

SYNTHESIS_USER_TEMPLATE = """# SMA Cross-Connection Analysis Request

## Data gathered from all sources

### Platform Snapshot
{platform_stats}

### Dual-target drug candidates (platform scoring)
{dual_targets}

### Ranked combinations
{combinations_rank}

### Multi-system combinations
{multisystem_combos}

### CORTEX unexplored approach pairs (13 total)
{cortex_cross}

### CORTEX knowledge gaps (top 15)
{cortex_gaps}

### Our local findings (this week)
{local_findings}

### Campaign catalog (10 campaigns)
{campaigns_summary}

### Compound index (27 compounds, cross-referenced)
{compound_index}

### Orphan MD trajectories (unanalyzed compute)
{orphans_summary}

---

## Your task

Generate 5-10 cross-connection insights. For each:

**Format:**
```
## Insight N: [title]
**Type**: [synergy/gap/contradiction/validation/orphan-analysis]
**Sources used**: [list]
**Novelty**: [new/known/contested]
**Confidence**: [high/medium/low]

**Claim**: [specific hypothesis with compound names + targets + data]

**Evidence**:
- [specific data point from source 1]
- [specific data point from source 2]
- [...]

**Action**:
1. [concrete compute/experiment step]
2. [next step]

**Expected outcome**: [what would success look like?]
```

Follow the format exactly. Be specific. Reference concrete numbers and names.
"""


# ============================================================================
# LLM synthesis
# ============================================================================

def format_platform_stats(data: dict) -> str:
    s = data.get("stats", {})
    return (
        f"- Targets: {s.get('targets', '?')}\n"
        f"- Drugs: {s.get('drugs', '?')}\n"
        f"- Trials: {s.get('trials', '?')}\n"
        f"- Claims: {s.get('claims', '?')}\n"
        f"- Hypotheses: {s.get('hypotheses', '?')}\n"
    )


def format_list(items, key_fields: list[str] = None, limit: int = 10) -> str:
    # Normalize dict-shaped items (some API endpoints return {"items": [...]})
    if isinstance(items, dict):
        items = items.get("items") or items.get("results") or items.get("combinations") or list(items.values())
    if not isinstance(items, list):
        items = []
    if not items:
        return "(empty)"
    lines = []
    for item in items[:limit]:
        if isinstance(item, dict):
            if key_fields:
                parts = [f"{k}={item.get(k, '?')}" for k in key_fields if k in item]
                lines.append(f"- {', '.join(parts) if parts else json.dumps(item, default=str)[:200]}")
            else:
                lines.append(f"- {json.dumps(item, default=str)[:200]}")
        else:
            lines.append(f"- {str(item)[:200]}")
    return "\n".join(lines)


def format_cortex_cross(cross: list) -> str:
    if not cross:
        return "(empty)"
    lines = []
    for c in cross[:15]:
        shared = ", ".join(c.get("shared_targets", []))
        lines.append(f"- {c.get('approach1')} ↔ {c.get('approach2')}: shared=[{shared}]")
    return "\n".join(lines)


def format_compound_index(index: dict) -> str:
    if not index:
        return "(empty)"
    lines = []
    sorted_items = sorted(index.items(), key=lambda x: -x[1].get("score", 0))
    for name, info in sorted_items[:25]:
        targets = ", ".join(sorted(info["targets"])) if info.get("targets") else "-"
        n_find = len(info.get("findings", []))
        score = info.get("score", 0)
        lines.append(f"- {name}: score={score:.2f}, {n_find} findings, targets=[{targets}]")
    return "\n".join(lines)


def format_findings(findings: list) -> str:
    if not findings:
        return "(empty)"
    lines = []
    for f in findings:
        # Extract TL;DR or first paragraph
        content = f.get("content", "")
        lines.append(f"- **{f.get('title', '?')[:80]}**")
        # Grab first non-header paragraph
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and not stripped.startswith("**"):
                lines.append(f"  {stripped[:200]}")
                break
    return "\n".join(lines)


def format_campaigns(campaigns: dict) -> str:
    if not campaigns:
        return "(empty)"
    lines = []
    for key, text in campaigns.items():
        # Extract first line (campaign name) and status line
        first_lines = text.split("\n")[:5]
        lines.append(f"- **{key}**: " + " | ".join(l.strip() for l in first_lines if l.strip())[:250])
    return "\n".join(lines)


def find_orphan_trajectories() -> list[dict]:
    roots = [
        Path.home() / "gpu-fleet/results/SMA/md_sims",
        DROPBOX_SMA / "GPU-Results-Trajectories",
    ]
    orphans = []
    for root in roots:
        if not root.exists():
            continue
        for dcd in root.rglob("*.dcd"):
            parent = dcd.parent
            if not any(parent.glob("*mmpbsa*.json")) and not any(parent.glob("analysis*.json")):
                orphans.append({
                    "name": dcd.stem,
                    "size_mb": dcd.stat().st_size / 1e6,
                    "parent": parent.name,
                })
    return sorted(orphans, key=lambda x: -x["size_mb"])


def format_orphans(orphans: list) -> str:
    if not orphans:
        return "(empty)"
    lines = [f"Total: {len(orphans)} trajectories, {sum(o['size_mb'] for o in orphans)/1024:.1f} GB"]
    lines.append("Top 15 by size:")
    for o in orphans[:15]:
        lines.append(f"- {o['name']} ({o['size_mb']:.0f} MB) in {o['parent']}")
    return "\n".join(lines)


def build_synthesis_prompt(data: dict, index: dict) -> str:
    orphans = find_orphan_trajectories()
    return SYNTHESIS_USER_TEMPLATE.format(
        platform_stats=format_platform_stats(data),
        dual_targets=format_list(
            data.get("dual_targets") or [],
            key_fields=["name", "score", "channel", "target", "BBB"],
            limit=10,
        ),
        combinations_rank=format_list(data.get("combinations_rank") or [], limit=10),
        multisystem_combos=format_list(data.get("multisystem_combos") or [], limit=10),
        cortex_cross=format_cortex_cross(data.get("cortex_cross") or []),
        cortex_gaps=format_list(
            data.get("cortex_gaps") or [],
            key_fields=["description", "approaches"],
            limit=15,
        ),
        local_findings=format_findings(data.get("findings") or []),
        campaigns_summary=format_campaigns(data.get("campaigns") or {}),
        compound_index=format_compound_index(index),
        orphans_summary=format_orphans(orphans),
    )


def call_claude(prompt: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=8000,
        system=SYNTHESIS_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


# ============================================================================
# Main
# ============================================================================

def main() -> int:
    publish = "--publish" in sys.argv

    print("=" * 70)
    print("Cross-Connection Engine v3 — with LLM synthesis layer")
    print(f"publish={publish}")
    print("=" * 70)

    print("\n[1/4] Gathering data (via v2 engine)...")
    data = gather_all_data()

    print("\n[2/4] Building compound index...")
    index = build_compound_target_index(data)
    print(f"  Indexed {len(index)} compounds")

    print("\n[3/4] Building LLM prompt and calling Claude...")
    prompt = build_synthesis_prompt(data, index)
    print(f"  Prompt size: {len(prompt)} chars")

    try:
        synthesis = call_claude(prompt)
        print(f"  Synthesis: {len(synthesis)} chars")
    except Exception as e:
        print(f"  LLM synthesis FAILED: {e}", file=sys.stderr)
        synthesis = f"[LLM synthesis failed: {e}]\n\nFallback: manual review required."

    print("\n[4/4] Writing output...")

    now = datetime.now(timezone.utc).isoformat()
    date_str = now[:10]
    output_path = INSIGHTS_DIR / f"{date_str}_cross_connections_v3.md"

    lines = [
        f"# Cross-Connection Insights v3 (LLM-synthesized) — {date_str}",
        "",
        f"**Generated**: {now}",
        f"**Engine**: `cross_connection_engine_v3.py` (retrieval + LLM synthesis)",
        f"**Model**: claude-opus-4-20250514",
        f"**Data sources**: {len([k for k in data if data[k]])} (CORTEX + Platform API + local)",
        f"**Compounds indexed**: {len(index)}",
        "",
        "## Platform Snapshot",
        "",
        format_platform_stats(data),
        "",
        "---",
        "",
        "## LLM-synthesized cross-connection insights",
        "",
        synthesis,
        "",
        "---",
        "",
        "## License",
        "",
        "CC-BY-4.0 — auto-generated by cross_connection_engine_v3.py",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Output: {output_path}")

    if publish:
        print("\n[publish] Pushing to CORTEX...")
        Cortex.learn(
            context="\n".join(lines)[:4000],
            description=f"Cross-connection v3 LLM synthesis {date_str}: {len(index)} compounds",
            category="insight",
        )

    print("\n" + "=" * 70)
    print("DONE")
    print(f"Output: {output_path}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
